"""
GPS CDM - Zone-Separated Celery Tasks
=====================================

Clean implementation of zone-separated processing tasks.
Each zone (Bronze, Silver, Gold) has its own dedicated task.

NiFi orchestrates the flow:
  Bronze Task → returns raw_ids → Silver Task → returns stg_ids → Gold Task

Failed records are published to the error queue for reprocessing.
"""

from celery import shared_task
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import uuid
import hashlib
import logging
import os

logger = logging.getLogger(__name__)

# Import extractors and common persistence
from gps_cdm.message_formats.base import ExtractorRegistry, GoldEntityPersister

# Import extractor modules to trigger registration
# Each module registers its extractor when imported
from gps_cdm.message_formats import pain001  # noqa: F401
from gps_cdm.message_formats import mt103    # noqa: F401
from gps_cdm.message_formats import pacs008  # noqa: F401
from gps_cdm.message_formats import fedwire  # noqa: F401


def get_db_connection():
    """Get PostgreSQL connection using environment variables."""
    import psycopg2
    return psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=int(os.environ.get('POSTGRES_PORT', 5433)),
        database=os.environ.get('POSTGRES_DB', 'gps_cdm'),
        user=os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
        password=os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password')
    )


def publish_error(
    cursor,
    batch_id: str,
    zone: str,
    message_type: str,
    error_message: str,
    error_code: str = 'UNKNOWN_ERROR',
    raw_id: Optional[str] = None,
    stg_id: Optional[str] = None,
    original_content: Optional[str] = None,
    error_stack_trace: Optional[str] = None,
    message_id: Optional[str] = None,
    content_hash: Optional[str] = None,
):
    """
    Publish a processing error to the error queue table.

    Args:
        cursor: Database cursor
        batch_id: Batch identifier
        zone: Processing zone (BRONZE, SILVER, GOLD)
        message_type: Type of message being processed
        error_message: Human-readable error description
        error_code: Categorized error code
        raw_id: Bronze record ID (if available)
        stg_id: Silver record ID (if available)
        original_content: Original message content for retry
        error_stack_trace: Full stack trace for debugging
        message_id: Original message ID from source
        content_hash: SHA-256 of content for deduplication
    """
    error_id = f"err_{uuid.uuid4().hex[:12]}"

    cursor.execute("""
        INSERT INTO bronze.processing_errors (
            error_id, batch_id, zone, raw_id, stg_id, content_hash,
            message_type, message_id, error_code, error_message,
            error_stack_trace, original_content, status, retry_count,
            max_retries, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            'PENDING', 0, 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        )
    """, (
        error_id, batch_id, zone, raw_id, stg_id, content_hash,
        message_type, message_id, error_code, error_message,
        error_stack_trace, original_content
    ))

    return error_id


def get_message_format(message_type: str) -> str:
    """Determine message format from message type."""
    msg_type_lower = message_type.lower()
    if msg_type_lower.startswith('pain') or msg_type_lower.startswith('pacs') or msg_type_lower.startswith('camt'):
        return 'ISO20022'
    elif msg_type_lower.startswith('mt'):
        return 'SWIFT_MT'
    elif msg_type_lower == 'fedwire':
        return 'FEDWIRE'
    elif msg_type_lower == 'ach':
        return 'ACH'
    return 'UNKNOWN'


# =============================================================================
# BRONZE ZONE TASK
# =============================================================================

@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True,
             queue='bronze', name='gps_cdm.zone_tasks.process_bronze_records')
def process_bronze_records(
    self,
    batch_id: str,
    records: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Process raw records into Bronze layer.

    BRONZE ONLY - does NOT process Silver or Gold.
    Returns raw_ids for NiFi to pass to Silver task.

    Args:
        batch_id: Unique batch identifier
        records: List of {content: str/dict, message_type: str}
        config: Optional configuration

    Returns:
        {
            status: 'SUCCESS' | 'PARTIAL' | 'FAILED',
            batch_id: str,
            raw_ids: [str],  # Successfully created raw_ids
            failed: [{index: int, message_type: str, error: str}],
            records_processed: int,
            duration_seconds: float
        }
    """
    start_time = datetime.utcnow()
    raw_ids = []
    failed = []

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for idx, record in enumerate(records):
            try:
                # Extract content and message_type
                content = record.get('content', record)
                message_type = record.get('message_type', 'UNKNOWN')

                # Parse content if string
                if isinstance(content, str):
                    try:
                        msg_content = json.loads(content)
                    except json.JSONDecodeError:
                        msg_content = {'raw': content}
                else:
                    msg_content = content

                # Generate raw_id
                raw_id = f"raw_{uuid.uuid4().hex[:12]}"

                # Compute content hash for deduplication
                content_str = json.dumps(msg_content, sort_keys=True)
                content_hash = hashlib.sha256(content_str.encode()).hexdigest()[:64]

                # Get message format
                message_format = get_message_format(message_type)

                # Insert into Bronze
                cursor.execute("""
                    INSERT INTO bronze.raw_payment_messages (
                        raw_id, message_type, message_format, raw_content,
                        raw_content_hash, source_system, source_file_path,
                        processing_status, _batch_id, _ingested_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (raw_id) DO NOTHING
                    RETURNING raw_id
                """, (
                    raw_id, message_type, message_format, content_str,
                    content_hash, 'NIFI', f'nifi://batch/{batch_id}',
                    'PENDING', batch_id, datetime.utcnow()
                ))

                result = cursor.fetchone()
                if result:
                    raw_ids.append(raw_id)
                else:
                    # Conflict - record already exists
                    failed.append({
                        'index': idx,
                        'message_type': message_type,
                        'error': 'Duplicate record (content hash conflict)',
                        'error_code': 'DUPLICATE_MESSAGE'
                    })

            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()

                # Publish to error queue
                try:
                    publish_error(
                        cursor=cursor,
                        batch_id=batch_id,
                        zone='BRONZE',
                        message_type=record.get('message_type', 'UNKNOWN'),
                        error_message=str(e),
                        error_code='PARSE_ERROR' if 'JSON' in str(e) else 'UNKNOWN_ERROR',
                        original_content=json.dumps(record) if isinstance(record, dict) else str(record),
                        error_stack_trace=error_trace,
                    )
                except Exception as pub_err:
                    logger.error(f"Failed to publish error: {pub_err}")

                failed.append({
                    'index': idx,
                    'message_type': record.get('message_type', 'UNKNOWN'),
                    'error': str(e),
                    'error_code': 'PARSE_ERROR' if 'JSON' in str(e) else 'UNKNOWN_ERROR'
                })

        conn.commit()

    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    duration = (datetime.utcnow() - start_time).total_seconds()

    # Determine status
    if not failed:
        status = 'SUCCESS'
    elif not raw_ids:
        status = 'FAILED'
    else:
        status = 'PARTIAL'

    return {
        'status': status,
        'batch_id': batch_id,
        'raw_ids': raw_ids,
        'failed': failed,
        'records_processed': len(raw_ids),
        'duration_seconds': duration,
    }


# =============================================================================
# SILVER ZONE TASK
# =============================================================================

@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True,
             queue='silver', name='gps_cdm.zone_tasks.process_silver_records')
def process_silver_records(
    self,
    batch_id: str,
    raw_ids: List[str],
    message_type: str,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Process Bronze records into Silver layer.

    Reads from bronze.raw_payment_messages, transforms using extractors,
    and writes to appropriate silver.stg_* table.

    Args:
        batch_id: Batch identifier
        raw_ids: List of raw_ids from Bronze
        message_type: Message type for extractor lookup
        config: Optional configuration

    Returns:
        {
            status: 'SUCCESS' | 'PARTIAL' | 'FAILED',
            batch_id: str,
            stg_ids: [str],  # Successfully created stg_ids
            failed: [{raw_id: str, error: str}],
            records_processed: int,
            duration_seconds: float
        }
    """
    start_time = datetime.utcnow()
    stg_ids = []
    failed = []

    # Get the extractor for this message type
    extractor = ExtractorRegistry.get(message_type)
    if not extractor:
        logger.error(f"No extractor registered for message type: {message_type}")
        return {
            'status': 'FAILED',
            'batch_id': batch_id,
            'stg_ids': [],
            'failed': [{'raw_id': rid, 'error': f'No extractor for {message_type}'} for rid in raw_ids],
            'records_processed': 0,
            'duration_seconds': 0,
            'error': f'No extractor registered for message type: {message_type}'
        }

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Read Bronze records
        placeholders = ','.join(['%s'] * len(raw_ids))
        cursor.execute(f"""
            SELECT raw_id, message_type, raw_content
            FROM bronze.raw_payment_messages
            WHERE raw_id IN ({placeholders})
              AND processing_status = 'PENDING'
        """, tuple(raw_ids))

        bronze_records = cursor.fetchall()

        for raw_id, msg_type, raw_content in bronze_records:
            try:
                # Parse content
                msg_content = json.loads(raw_content) if isinstance(raw_content, str) else raw_content

                # Generate stg_id
                stg_id = extractor.generate_stg_id()

                # Extract Silver record
                silver_record = extractor.extract_silver(msg_content, raw_id, stg_id, batch_id)

                # Get table and columns
                silver_table = extractor.SILVER_TABLE
                columns = extractor.get_silver_columns()
                values = extractor.get_silver_values(silver_record)

                # Build INSERT statement
                col_names = ', '.join(columns)
                placeholders_sql = ', '.join(['%s'] * len(columns))

                cursor.execute(f"""
                    INSERT INTO silver.{silver_table} ({col_names})
                    VALUES ({placeholders_sql})
                    ON CONFLICT (stg_id) DO NOTHING
                    RETURNING stg_id
                """, values)

                result = cursor.fetchone()
                if result:
                    stg_ids.append(stg_id)

                    # Update Bronze status
                    cursor.execute("""
                        UPDATE bronze.raw_payment_messages
                        SET processing_status = 'PROMOTED_TO_SILVER',
                            processed_to_silver_at = CURRENT_TIMESTAMP
                        WHERE raw_id = %s
                    """, (raw_id,))
                else:
                    failed.append({
                        'raw_id': raw_id,
                        'error': 'Duplicate stg_id (conflict)',
                        'error_code': 'DUPLICATE_MESSAGE'
                    })

            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()

                # Publish to error queue
                try:
                    publish_error(
                        cursor=cursor,
                        batch_id=batch_id,
                        zone='SILVER',
                        message_type=message_type,
                        error_message=str(e),
                        error_code='VALIDATION_ERROR' if 'validation' in str(e).lower() else 'UNKNOWN_ERROR',
                        raw_id=raw_id,
                        error_stack_trace=error_trace,
                    )
                except Exception as pub_err:
                    logger.error(f"Failed to publish error: {pub_err}")

                failed.append({
                    'raw_id': raw_id,
                    'error': str(e),
                    'error_code': 'VALIDATION_ERROR' if 'validation' in str(e).lower() else 'UNKNOWN_ERROR'
                })

        conn.commit()

    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    duration = (datetime.utcnow() - start_time).total_seconds()

    # Determine status
    if not failed:
        status = 'SUCCESS'
    elif not stg_ids:
        status = 'FAILED'
    else:
        status = 'PARTIAL'

    return {
        'status': status,
        'batch_id': batch_id,
        'stg_ids': stg_ids,
        'failed': failed,
        'records_processed': len(stg_ids),
        'duration_seconds': duration,
    }


# =============================================================================
# GOLD ZONE TASK
# =============================================================================

@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True,
             queue='gold', name='gps_cdm.zone_tasks.process_gold_records')
def process_gold_records(
    self,
    batch_id: str,
    stg_ids: List[str],
    message_type: str,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Process Silver records into Gold layer.

    Reads from silver.stg_* table, extracts entities using extractors,
    and writes to gold.cdm_* tables.

    Args:
        batch_id: Batch identifier
        stg_ids: List of stg_ids from Silver
        message_type: Message type for extractor lookup
        config: Optional configuration

    Returns:
        {
            status: 'SUCCESS' | 'PARTIAL' | 'FAILED',
            batch_id: str,
            instruction_ids: [str],  # Successfully created instruction_ids
            failed: [{stg_id: str, error: str}],
            records_processed: int,
            entities_created: {parties: int, accounts: int, financial_institutions: int},
            duration_seconds: float
        }
    """
    start_time = datetime.utcnow()
    instruction_ids = []
    failed = []
    entities_created = {'parties': 0, 'accounts': 0, 'financial_institutions': 0}

    # Get the extractor for this message type
    extractor = ExtractorRegistry.get(message_type)
    if not extractor:
        logger.error(f"No extractor registered for message type: {message_type}")
        return {
            'status': 'FAILED',
            'batch_id': batch_id,
            'instruction_ids': [],
            'failed': [{'stg_id': sid, 'error': f'No extractor for {message_type}'} for sid in stg_ids],
            'records_processed': 0,
            'entities_created': entities_created,
            'duration_seconds': 0,
            'error': f'No extractor registered for message type: {message_type}'
        }

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        silver_table = extractor.SILVER_TABLE

        # Read Silver records
        placeholders = ','.join(['%s'] * len(stg_ids))
        cursor.execute(f"""
            SELECT stg_id, raw_id
            FROM silver.{silver_table}
            WHERE stg_id IN ({placeholders})
        """, tuple(stg_ids))

        silver_records = cursor.fetchall()

        for stg_id, raw_id in silver_records:
            try:
                # Read the original content from Bronze for entity extraction
                cursor.execute("""
                    SELECT raw_content FROM bronze.raw_payment_messages
                    WHERE raw_id = %s
                """, (raw_id,))

                bronze_row = cursor.fetchone()
                if not bronze_row:
                    failed.append({
                        'stg_id': stg_id,
                        'error': f'Bronze record not found: {raw_id}',
                        'error_code': 'MISSING_REQUIRED_FIELD'
                    })
                    continue

                msg_content = json.loads(bronze_row[0])

                # Extract Gold entities
                gold_entities = extractor.extract_gold_entities(msg_content, stg_id, batch_id)

                # Persist entities using common persister
                entity_ids = GoldEntityPersister.persist_all_entities(
                    cursor, gold_entities, message_type, stg_id, 'GPS_CDM'
                )

                # Count created entities
                if entity_ids.get('debtor_id'):
                    entities_created['parties'] += 1
                if entity_ids.get('creditor_id'):
                    entities_created['parties'] += 1
                if entity_ids.get('ultimate_debtor_id'):
                    entities_created['parties'] += 1
                if entity_ids.get('ultimate_creditor_id'):
                    entities_created['parties'] += 1
                if entity_ids.get('debtor_account_id'):
                    entities_created['accounts'] += 1
                if entity_ids.get('creditor_account_id'):
                    entities_created['accounts'] += 1
                if entity_ids.get('debtor_agent_id'):
                    entities_created['financial_institutions'] += 1
                if entity_ids.get('creditor_agent_id'):
                    entities_created['financial_institutions'] += 1
                if entity_ids.get('intermediary_agent1_id'):
                    entities_created['financial_institutions'] += 1

                # Create payment instruction
                instruction_id = f"instr_{uuid.uuid4().hex[:12]}"

                # Extract amounts and identifiers from msg_content
                amount = msg_content.get('instructedAmount') or msg_content.get('amount') or 0
                currency = msg_content.get('instructedCurrency') or msg_content.get('currency') or 'XXX'
                end_to_end_id = msg_content.get('endToEndId') or msg_content.get('end_to_end_id')
                uetr = msg_content.get('uetr')

                # Determine payment type from message type
                payment_type_map = {
                    'pain.001': 'CREDIT_TRANSFER',
                    'pain001': 'CREDIT_TRANSFER',
                    'pacs.008': 'CREDIT_TRANSFER',
                    'pacs008': 'CREDIT_TRANSFER',
                    'mt103': 'CREDIT_TRANSFER',
                    'fedwire': 'WIRE_TRANSFER',
                }
                payment_type = payment_type_map.get(message_type.lower().replace('.', '_').replace('-', '_'), 'TRANSFER')

                # Generate payment_id (transaction group identifier)
                payment_id = f"pmt_{uuid.uuid4().hex[:12]}"

                # Determine scheme from message type
                scheme_map = {
                    'pain.001': 'ISO20022',
                    'pain001': 'ISO20022',
                    'pacs.008': 'ISO20022',
                    'pacs008': 'ISO20022',
                    'mt103': 'SWIFT_MT',
                    'mt103_': 'SWIFT_MT',
                    'fedwire': 'FEDWIRE',
                }
                scheme_code = scheme_map.get(message_type.lower().replace('.', '_').replace('-', '_'), 'OTHER')

                # Get current date parts for partitioning
                now = datetime.utcnow()
                partition_year = now.year
                partition_month = now.month

                cursor.execute("""
                    INSERT INTO gold.cdm_payment_instruction (
                        instruction_id, payment_id, source_stg_id, source_stg_table, source_message_type,
                        payment_type, scheme_code, direction, source_system,
                        instructed_amount, instructed_currency, end_to_end_id, uetr,
                        debtor_id, debtor_account_id, debtor_agent_id,
                        creditor_id, creditor_account_id, creditor_agent_id,
                        intermediary_agent1_id, ultimate_debtor_id, ultimate_creditor_id,
                        current_status, lineage_batch_id, partition_year, partition_month,
                        created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        'PROCESSED', %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (instruction_id) DO NOTHING
                    RETURNING instruction_id
                """, (
                    instruction_id, payment_id, stg_id, silver_table, message_type,
                    payment_type, scheme_code, 'OUTGOING', 'GPS_CDM',
                    amount, currency, end_to_end_id, uetr,
                    entity_ids.get('debtor_id'),
                    entity_ids.get('debtor_account_id'),
                    entity_ids.get('debtor_agent_id'),
                    entity_ids.get('creditor_id'),
                    entity_ids.get('creditor_account_id'),
                    entity_ids.get('creditor_agent_id'),
                    entity_ids.get('intermediary_agent1_id'),
                    entity_ids.get('ultimate_debtor_id'),
                    entity_ids.get('ultimate_creditor_id'),
                    batch_id, partition_year, partition_month
                ))

                result = cursor.fetchone()
                if result:
                    instruction_ids.append(instruction_id)

                    # Update Silver status
                    cursor.execute(f"""
                        UPDATE silver.{silver_table}
                        SET processing_status = 'PROMOTED_TO_GOLD',
                            processed_to_gold_at = CURRENT_TIMESTAMP
                        WHERE stg_id = %s
                    """, (stg_id,))
                else:
                    failed.append({
                        'stg_id': stg_id,
                        'error': 'Duplicate instruction_id (conflict)',
                        'error_code': 'DUPLICATE_MESSAGE'
                    })

            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()

                # Publish to error queue
                try:
                    publish_error(
                        cursor=cursor,
                        batch_id=batch_id,
                        zone='GOLD',
                        message_type=message_type,
                        error_message=str(e),
                        error_code='DB_CONSTRAINT_VIOLATION' if 'constraint' in str(e).lower() else 'UNKNOWN_ERROR',
                        stg_id=stg_id,
                        error_stack_trace=error_trace,
                    )
                except Exception as pub_err:
                    logger.error(f"Failed to publish error: {pub_err}")

                failed.append({
                    'stg_id': stg_id,
                    'error': str(e),
                    'error_code': 'DB_CONSTRAINT_VIOLATION' if 'constraint' in str(e).lower() else 'UNKNOWN_ERROR'
                })

        conn.commit()

    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    duration = (datetime.utcnow() - start_time).total_seconds()

    # Determine status
    if not failed:
        status = 'SUCCESS'
    elif not instruction_ids:
        status = 'FAILED'
    else:
        status = 'PARTIAL'

    return {
        'status': status,
        'batch_id': batch_id,
        'instruction_ids': instruction_ids,
        'failed': failed,
        'records_processed': len(instruction_ids),
        'entities_created': entities_created,
        'duration_seconds': duration,
    }


# =============================================================================
# REPROCESSING TASKS
# =============================================================================

@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True,
             name='gps_cdm.zone_tasks.retry_error')
def retry_error(
    self,
    error_id: str,
    user: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retry a specific error from the error queue.

    Determines which zone failed and re-runs the appropriate task.

    Args:
        error_id: The error_id from bronze.processing_errors
        user: User initiating the retry (for audit)

    Returns:
        {status: str, error_id: str, zone: str, result: dict}
    """
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get error details
        cursor.execute("""
            SELECT error_id, batch_id, zone, raw_id, stg_id, message_type,
                   original_content, retry_count, max_retries
            FROM bronze.processing_errors
            WHERE error_id = %s
        """, (error_id,))

        row = cursor.fetchone()
        if not row:
            return {'status': 'FAILED', 'error': f'Error not found: {error_id}'}

        (err_id, batch_id, zone, raw_id, stg_id, message_type,
         original_content, retry_count, max_retries) = row

        if retry_count >= max_retries:
            return {
                'status': 'FAILED',
                'error_id': error_id,
                'error': 'Max retries exceeded',
                'retry_count': retry_count,
                'max_retries': max_retries
            }

        # Update error status to RETRYING
        cursor.execute("""
            UPDATE bronze.processing_errors
            SET status = 'RETRYING',
                retry_count = retry_count + 1,
                last_retry_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE error_id = %s
        """, (error_id,))

        # Log to history
        cursor.execute("""
            INSERT INTO bronze.processing_error_history (
                error_id, action, action_by, previous_status, new_status
            ) VALUES (%s, 'RETRY_ATTEMPTED', %s, 'PENDING', 'RETRYING')
        """, (error_id, user))

        conn.commit()

        # Dispatch appropriate task based on zone
        if zone == 'BRONZE':
            # Re-process from original content
            content = json.loads(original_content) if original_content else {}
            result = process_bronze_records.delay(
                batch_id=f"retry_{batch_id}",
                records=[{'content': content, 'message_type': message_type}],
            )
        elif zone == 'SILVER':
            # Re-process from raw_id
            if not raw_id:
                return {'status': 'FAILED', 'error': 'No raw_id for SILVER retry'}
            result = process_silver_records.delay(
                batch_id=f"retry_{batch_id}",
                raw_ids=[raw_id],
                message_type=message_type,
            )
        elif zone == 'GOLD':
            # Re-process from stg_id
            if not stg_id:
                return {'status': 'FAILED', 'error': 'No stg_id for GOLD retry'}
            result = process_gold_records.delay(
                batch_id=f"retry_{batch_id}",
                stg_ids=[stg_id],
                message_type=message_type,
            )
        else:
            return {'status': 'FAILED', 'error': f'Unknown zone: {zone}'}

        return {
            'status': 'DISPATCHED',
            'error_id': error_id,
            'zone': zone,
            'task_id': result.id,
        }

    except Exception as e:
        if conn:
            conn.rollback()
        return {'status': 'FAILED', 'error': str(e)}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@shared_task(bind=True, name='gps_cdm.zone_tasks.bulk_retry_errors')
def bulk_retry_errors(
    self,
    error_ids: List[str],
    user: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retry multiple errors from the error queue.

    Args:
        error_ids: List of error_ids to retry
        user: User initiating the retry

    Returns:
        {status: str, total: int, dispatched: int, failed: int, results: [...]}
    """
    results = []
    dispatched = 0
    failed_count = 0

    for error_id in error_ids:
        try:
            result = retry_error.delay(error_id, user)
            results.append({'error_id': error_id, 'task_id': result.id, 'status': 'DISPATCHED'})
            dispatched += 1
        except Exception as e:
            results.append({'error_id': error_id, 'status': 'FAILED', 'error': str(e)})
            failed_count += 1

    return {
        'status': 'SUCCESS' if failed_count == 0 else 'PARTIAL',
        'total': len(error_ids),
        'dispatched': dispatched,
        'failed': failed_count,
        'results': results,
    }
