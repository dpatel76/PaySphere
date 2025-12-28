"""
GPS CDM - Batch Promotion Celery Tasks
======================================

High-throughput Celery tasks for promoting batches through medallion layers.
Uses bulk database operations for maximum performance.

Key Features:
- Batch-based processing (10K-50K records per batch)
- Bulk reads and writes using COPY
- Checkpoint-based restartability
- Real-time progress tracking

Layer Flow:
Bronze (raw) → Silver (structured) → Gold (CDM entities)

Usage:
    # Triggered automatically by MicroBatchAccumulator after Bronze write
    # Or manually for reprocessing:

    from gps_cdm.orchestration.batch_promotion_tasks import (
        promote_bronze_to_silver_batch,
        promote_silver_to_gold_batch,
    )

    result = promote_bronze_to_silver_batch.delay(
        batch_id="abc-123",
        message_type="pain.001",
        bronze_record_ids=["id1", "id2", ...]
    )
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from celery import Celery, chain, chord, group

logger = logging.getLogger(__name__)

# =============================================================================
# CELERY APP CONFIGURATION
# =============================================================================

# Import the main Celery app
try:
    from gps_cdm.orchestration.celery_tasks import app
except ImportError:
    # Fallback for standalone testing
    app = Celery('gps_cdm.orchestration.batch_promotion_tasks')
    app.config_from_object({
        'broker_url': os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        'result_backend': os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
    })


# =============================================================================
# DATABASE CONNECTION
# =============================================================================

def get_db_connection():
    """Get PostgreSQL connection."""
    import psycopg2

    return psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=int(os.environ.get('POSTGRES_PORT', 5433)),
        database=os.environ.get('POSTGRES_DB', 'gps_cdm'),
        user=os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
        password=os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password'),
    )


def get_bulk_writer():
    """Get appropriate bulk writer based on data source."""
    from gps_cdm.streaming.bulk_writer import BulkWriter

    data_source = os.environ.get('GPS_CDM_DATA_SOURCE', 'postgresql')

    if data_source == 'databricks':
        return BulkWriter.create('databricks', {
            'server_hostname': os.environ.get('DATABRICKS_SERVER_HOSTNAME'),
            'http_path': os.environ.get('DATABRICKS_HTTP_PATH'),
            'token': os.environ.get('DATABRICKS_TOKEN'),
            'staging_bucket': os.environ.get('DATABRICKS_STAGING_BUCKET', 's3://gps-cdm-staging'),
        })
    else:
        return BulkWriter.create('postgresql', {
            'host': os.environ.get('POSTGRES_HOST', 'localhost'),
            'port': int(os.environ.get('POSTGRES_PORT', 5433)),
            'database': os.environ.get('POSTGRES_DB', 'gps_cdm'),
            'user': os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
            'password': os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password'),
        })


# =============================================================================
# BATCH PROMOTION TASKS
# =============================================================================

@app.task(
    bind=True,
    name='gps_cdm.orchestration.batch_promotion_tasks.promote_bronze_to_silver_batch',
    queue='silver',
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def promote_bronze_to_silver_batch(
    self,
    batch_id: str,
    message_type: str,
    bronze_record_ids: Optional[List[str]] = None,
    limit: int = 10000,
) -> Dict[str, Any]:
    """
    Promote a batch of Bronze records to Silver.

    Optimizations:
    1. Bulk read Bronze records using IN clause
    2. Apply transformations in memory (vectorized where possible)
    3. Bulk write to Silver using COPY
    4. Bulk update Bronze status

    Args:
        batch_id: Batch identifier for tracking
        message_type: Payment message type (e.g., pain.001, MT103)
        bronze_record_ids: Specific record IDs to process (optional)
        limit: Maximum records to process if bronze_record_ids not specified

    Returns:
        Dict with processing results
    """
    start_time = time.time()
    logger.info(f"Starting Bronze→Silver promotion for batch {batch_id}, type={message_type}")

    try:
        # Get extractor for this message type
        from gps_cdm.message_formats.base import ExtractorRegistry
        extractor = ExtractorRegistry.get(message_type)

        if extractor is None:
            raise ValueError(f"No extractor registered for message type: {message_type}")

        conn = get_db_connection()
        bulk_writer = get_bulk_writer()

        # 1. BULK READ: Get Bronze records
        bronze_records = _bulk_read_bronze(
            conn, message_type, bronze_record_ids, limit
        )

        if not bronze_records:
            logger.info(f"No Bronze records to process for batch {batch_id}")
            return {
                'status': 'SUCCESS',
                'batch_id': batch_id,
                'bronze_records': 0,
                'silver_records': 0,
                'errors': 0,
                'duration_seconds': time.time() - start_time,
            }

        logger.info(f"Read {len(bronze_records)} Bronze records")

        # 2. TRANSFORM: Apply extractor to each record
        silver_records = []
        errors = []
        processed_raw_ids = []

        for bronze in bronze_records:
            try:
                # Parse raw content
                raw_content = bronze['raw_content']

                # Extract Silver data
                silver_data = extractor.extract_silver(raw_content)

                # Add required metadata
                silver_data['stg_id'] = f"stg_{uuid.uuid4().hex[:12]}"
                silver_data['source_raw_id'] = bronze['raw_id']
                silver_data['_batch_id'] = batch_id
                silver_data['processing_status'] = 'PENDING'

                silver_records.append(silver_data)
                processed_raw_ids.append(bronze['raw_id'])

            except Exception as e:
                errors.append({
                    'raw_id': bronze['raw_id'],
                    'error': str(e),
                    'error_type': type(e).__name__,
                })
                logger.warning(f"Transform error for {bronze['raw_id']}: {e}")

        logger.info(f"Transformed {len(silver_records)} records, {len(errors)} errors")

        # 3. BULK WRITE: Insert Silver records
        silver_table = _get_silver_table(message_type)

        if silver_records:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                write_result = loop.run_until_complete(
                    bulk_writer.bulk_insert_silver(
                        batch_id=batch_id,
                        message_type=message_type,
                        table=silver_table,
                        records=silver_records,
                    )
                )
            finally:
                loop.close()

            if not write_result.success:
                raise Exception(f"Silver write failed: {write_result.error}")

            logger.info(
                f"Wrote {write_result.records_written} Silver records "
                f"at {write_result.rows_per_second:.0f} rows/sec"
            )

        # 4. BULK UPDATE: Mark Bronze records as processed
        if processed_raw_ids:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(
                    bulk_writer.bulk_update_status(
                        table='bronze.raw_payment_messages',
                        record_ids=processed_raw_ids,
                        status='PROCESSED_TO_SILVER',
                        timestamp_column='processed_to_silver_at',
                    )
                )
            finally:
                loop.close()

        # 5. Record errors to observability
        if errors:
            _record_processing_errors(conn, batch_id, 'silver', silver_table, errors)

        # 6. Trigger Gold promotion
        silver_record_ids = [r['stg_id'] for r in silver_records]

        if silver_record_ids:
            promote_silver_to_gold_batch.delay(
                batch_id=batch_id,
                message_type=message_type,
                silver_record_ids=silver_record_ids,
            )

        conn.close()
        bulk_writer.close()

        duration = time.time() - start_time

        return {
            'status': 'SUCCESS' if not errors else 'PARTIAL',
            'batch_id': batch_id,
            'message_type': message_type,
            'bronze_records': len(bronze_records),
            'silver_records': len(silver_records),
            'errors': len(errors),
            'duration_seconds': duration,
            'rows_per_second': len(silver_records) / duration if duration > 0 else 0,
        }

    except Exception as e:
        logger.exception(f"Bronze→Silver promotion failed for batch {batch_id}: {e}")

        # Retry with exponential backoff
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            return {
                'status': 'FAILED',
                'batch_id': batch_id,
                'message_type': message_type,
                'error': str(e),
                'duration_seconds': time.time() - start_time,
            }


@app.task(
    bind=True,
    name='gps_cdm.orchestration.batch_promotion_tasks.promote_silver_to_gold_batch',
    queue='gold',
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def promote_silver_to_gold_batch(
    self,
    batch_id: str,
    message_type: str,
    silver_record_ids: Optional[List[str]] = None,
    limit: int = 10000,
) -> Dict[str, Any]:
    """
    Promote a batch of Silver records to Gold CDM entities.

    Extracts and upserts:
    - PaymentInstruction
    - Party (Debtor, Creditor, Ultimate*)
    - Account (Debtor, Creditor accounts)
    - FinancialInstitution (Debtor Agent, Creditor Agent)

    Args:
        batch_id: Batch identifier
        message_type: Payment message type
        silver_record_ids: Specific Silver record IDs to process
        limit: Maximum records if silver_record_ids not specified

    Returns:
        Dict with processing results
    """
    start_time = time.time()
    logger.info(f"Starting Silver→Gold promotion for batch {batch_id}, type={message_type}")

    try:
        from gps_cdm.message_formats.base import ExtractorRegistry
        extractor = ExtractorRegistry.get(message_type)

        if extractor is None:
            raise ValueError(f"No extractor registered for message type: {message_type}")

        conn = get_db_connection()
        bulk_writer = get_bulk_writer()

        # 1. BULK READ: Get Silver records
        silver_table = _get_silver_table(message_type)
        silver_records = _bulk_read_silver(
            conn, silver_table, silver_record_ids, limit
        )

        if not silver_records:
            logger.info(f"No Silver records to process for batch {batch_id}")
            return {
                'status': 'SUCCESS',
                'batch_id': batch_id,
                'silver_records': 0,
                'gold_entities': {},
                'duration_seconds': time.time() - start_time,
            }

        logger.info(f"Read {len(silver_records)} Silver records")

        # 2. EXTRACT: Get Gold entities from each Silver record
        payment_instructions = []
        parties = []
        accounts = []
        financial_institutions = []
        errors = []
        processed_stg_ids = []

        for silver in silver_records:
            try:
                # Extract Gold entities
                gold_entities = extractor.extract_gold_entities(silver)

                # Process PaymentInstruction
                if gold_entities.payment_instruction:
                    pi = gold_entities.payment_instruction
                    pi_dict = _to_dict(pi)
                    pi_dict['instruction_id'] = f"instr_{uuid.uuid4().hex[:12]}"
                    pi_dict['source_stg_id'] = silver['stg_id']
                    pi_dict['source_raw_id'] = silver.get('source_raw_id')
                    pi_dict['_batch_id'] = batch_id
                    payment_instructions.append(pi_dict)

                # Process Parties
                for party in gold_entities.parties:
                    party_dict = _to_dict(party)
                    party_dict['party_id'] = f"party_{uuid.uuid4().hex[:12]}"
                    party_dict['_batch_id'] = batch_id
                    parties.append(party_dict)

                # Process Accounts
                for account in gold_entities.accounts:
                    acct_dict = _to_dict(account)
                    acct_dict['account_id'] = f"acct_{uuid.uuid4().hex[:12]}"
                    acct_dict['_batch_id'] = batch_id
                    accounts.append(acct_dict)

                # Process Financial Institutions
                for fi in gold_entities.financial_institutions:
                    fi_dict = _to_dict(fi)
                    fi_dict['fi_id'] = f"fi_{uuid.uuid4().hex[:12]}"
                    fi_dict['_batch_id'] = batch_id
                    financial_institutions.append(fi_dict)

                processed_stg_ids.append(silver['stg_id'])

            except Exception as e:
                errors.append({
                    'stg_id': silver['stg_id'],
                    'error': str(e),
                    'error_type': type(e).__name__,
                })
                logger.warning(f"Gold extraction error for {silver['stg_id']}: {e}")

        logger.info(
            f"Extracted Gold entities: {len(payment_instructions)} instructions, "
            f"{len(parties)} parties, {len(accounts)} accounts, "
            f"{len(financial_institutions)} FIs"
        )

        # 3. BULK WRITE: Upsert to Gold tables
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            gold_counts = {}

            if payment_instructions:
                result = loop.run_until_complete(
                    bulk_writer.bulk_insert_gold(
                        batch_id=batch_id,
                        table='gold.cdm_payment_instruction',
                        records=payment_instructions,
                        merge_keys=['instruction_id'],
                    )
                )
                gold_counts['payment_instruction'] = result.records_written

            if parties:
                result = loop.run_until_complete(
                    bulk_writer.bulk_insert_gold(
                        batch_id=batch_id,
                        table='gold.cdm_party',
                        records=parties,
                        merge_keys=['party_id'],
                    )
                )
                gold_counts['party'] = result.records_written

            if accounts:
                result = loop.run_until_complete(
                    bulk_writer.bulk_insert_gold(
                        batch_id=batch_id,
                        table='gold.cdm_account',
                        records=accounts,
                        merge_keys=['account_id'],
                    )
                )
                gold_counts['account'] = result.records_written

            if financial_institutions:
                result = loop.run_until_complete(
                    bulk_writer.bulk_insert_gold(
                        batch_id=batch_id,
                        table='gold.cdm_financial_institution',
                        records=financial_institutions,
                        merge_keys=['fi_id'],
                    )
                )
                gold_counts['financial_institution'] = result.records_written

            # 4. Update Silver status
            if processed_stg_ids:
                loop.run_until_complete(
                    bulk_writer.bulk_update_status(
                        table=silver_table,
                        record_ids=processed_stg_ids,
                        status='PROCESSED_TO_GOLD',
                        timestamp_column='processed_to_gold_at',
                    )
                )

        finally:
            loop.close()

        # 5. Record errors
        if errors:
            _record_processing_errors(conn, batch_id, 'gold', 'cdm_entities', errors)

        # 6. Update batch tracking
        _update_batch_tracking(conn, batch_id, 'gold', gold_counts)

        conn.close()
        bulk_writer.close()

        duration = time.time() - start_time

        return {
            'status': 'SUCCESS' if not errors else 'PARTIAL',
            'batch_id': batch_id,
            'message_type': message_type,
            'silver_records': len(silver_records),
            'gold_entities': gold_counts,
            'errors': len(errors),
            'duration_seconds': duration,
        }

    except Exception as e:
        logger.exception(f"Silver→Gold promotion failed for batch {batch_id}: {e}")

        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            return {
                'status': 'FAILED',
                'batch_id': batch_id,
                'message_type': message_type,
                'error': str(e),
                'duration_seconds': time.time() - start_time,
            }


@app.task(
    bind=True,
    name='gps_cdm.orchestration.batch_promotion_tasks.poll_pending_bronze_batches',
    queue='celery',
)
def poll_pending_bronze_batches(self, limit: int = 1000) -> Dict[str, Any]:
    """
    Celery Beat task to poll for pending Bronze records and trigger promotion.

    This is the "pull" mechanism for when records are written directly to Bronze
    (e.g., via NiFi PutDatabaseRecord) without going through Kafka.

    Runs every 10 seconds via Celery Beat.
    """
    start_time = time.time()

    try:
        conn = get_db_connection()

        # Find message types with pending Bronze records
        with conn.cursor() as cur:
            cur.execute("""
                SELECT message_type, COUNT(*) as pending_count
                FROM bronze.raw_payment_messages
                WHERE processing_status = 'PENDING'
                GROUP BY message_type
                HAVING COUNT(*) > 0
                ORDER BY pending_count DESC
                LIMIT 10
            """)
            pending_types = cur.fetchall()

        if not pending_types:
            return {
                'status': 'NO_WORK',
                'duration_seconds': time.time() - start_time,
            }

        # Dispatch promotion tasks for each message type
        dispatched = []
        for message_type, count in pending_types:
            batch_id = f"poll_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{message_type}"

            # Get pending record IDs (limit per type)
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT raw_id
                    FROM bronze.raw_payment_messages
                    WHERE processing_status = 'PENDING'
                      AND message_type = %s
                    ORDER BY ingestion_timestamp
                    LIMIT %s
                """, (message_type, min(count, limit // len(pending_types))))
                raw_ids = [row[0] for row in cur.fetchall()]

            if raw_ids:
                # Dispatch promotion task
                promote_bronze_to_silver_batch.delay(
                    batch_id=batch_id,
                    message_type=message_type,
                    bronze_record_ids=raw_ids,
                )
                dispatched.append({
                    'message_type': message_type,
                    'batch_id': batch_id,
                    'record_count': len(raw_ids),
                })

        conn.close()

        return {
            'status': 'DISPATCHED',
            'batches': dispatched,
            'duration_seconds': time.time() - start_time,
        }

    except Exception as e:
        logger.exception(f"Poll pending Bronze failed: {e}")
        return {
            'status': 'ERROR',
            'error': str(e),
            'duration_seconds': time.time() - start_time,
        }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _bulk_read_bronze(
    conn,
    message_type: str,
    record_ids: Optional[List[str]],
    limit: int
) -> List[Dict]:
    """Bulk read Bronze records."""
    with conn.cursor() as cur:
        if record_ids:
            cur.execute("""
                SELECT raw_id, message_type, message_format, raw_content,
                       source_system, source_batch_id, _batch_id
                FROM bronze.raw_payment_messages
                WHERE raw_id = ANY(%s)
            """, (record_ids,))
        else:
            cur.execute("""
                SELECT raw_id, message_type, message_format, raw_content,
                       source_system, source_batch_id, _batch_id
                FROM bronze.raw_payment_messages
                WHERE processing_status = 'PENDING'
                  AND message_type = %s
                ORDER BY ingestion_timestamp
                LIMIT %s
            """, (message_type, limit))

        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]


def _bulk_read_silver(
    conn,
    table: str,
    record_ids: Optional[List[str]],
    limit: int
) -> List[Dict]:
    """Bulk read Silver records."""
    with conn.cursor() as cur:
        if record_ids:
            cur.execute(f"""
                SELECT *
                FROM {table}
                WHERE stg_id = ANY(%s)
            """, (record_ids,))
        else:
            cur.execute(f"""
                SELECT *
                FROM {table}
                WHERE processing_status = 'PENDING'
                ORDER BY _processed_at
                LIMIT %s
            """, (limit,))

        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]


def _get_silver_table(message_type: str) -> str:
    """Get Silver table name for message type."""
    # Normalize message type to table name
    table_suffix = message_type.lower().replace('.', '_').replace('-', '_')
    return f"silver.stg_{table_suffix}"


def _to_dict(obj: Any) -> Dict[str, Any]:
    """Convert dataclass or object to dict."""
    if hasattr(obj, '__dict__'):
        result = {}
        for key, value in obj.__dict__.items():
            if value is not None:
                if hasattr(value, '__dict__'):
                    result[key] = _to_dict(value)
                elif isinstance(value, (list, tuple)):
                    result[key] = [_to_dict(v) if hasattr(v, '__dict__') else v for v in value]
                else:
                    result[key] = value
        return result
    return obj


def _record_processing_errors(
    conn,
    batch_id: str,
    layer: str,
    table: str,
    errors: List[Dict]
) -> None:
    """Record processing errors to observability table."""
    try:
        with conn.cursor() as cur:
            for error in errors:
                cur.execute("""
                    INSERT INTO observability.obs_processing_errors (
                        error_id, batch_id, layer, table_name,
                        record_id, error_type, error_message, severity
                    ) VALUES (
                        uuid_generate_v4()::text, %s, %s, %s,
                        %s, %s, %s, 'ERROR'
                    )
                """, (
                    batch_id, layer, table,
                    error.get('raw_id') or error.get('stg_id'),
                    error.get('error_type', 'UNKNOWN'),
                    error.get('error', '')[:4000],
                ))
        conn.commit()
    except Exception as e:
        logger.warning(f"Failed to record errors: {e}")


def _update_batch_tracking(
    conn,
    batch_id: str,
    layer: str,
    counts: Dict[str, int]
) -> None:
    """Update batch tracking with layer completion."""
    try:
        with conn.cursor() as cur:
            if layer == 'silver':
                cur.execute("""
                    UPDATE observability.obs_batch_tracking
                    SET silver_records = %s,
                        silver_completed_at = CURRENT_TIMESTAMP,
                        current_layer = 'silver',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE batch_id = %s
                """, (sum(counts.values()), batch_id))
            elif layer == 'gold':
                cur.execute("""
                    UPDATE observability.obs_batch_tracking
                    SET gold_records = %s,
                        gold_completed_at = CURRENT_TIMESTAMP,
                        current_layer = 'gold',
                        status = 'COMPLETED',
                        completed_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE batch_id = %s
                """, (sum(counts.values()), batch_id))
        conn.commit()
    except Exception as e:
        logger.warning(f"Failed to update batch tracking: {e}")


# =============================================================================
# CELERY BEAT SCHEDULE
# =============================================================================

# Add to Celery Beat schedule for periodic polling
app.conf.beat_schedule = app.conf.beat_schedule or {}
app.conf.beat_schedule.update({
    'poll-pending-bronze-every-10s': {
        'task': 'gps_cdm.orchestration.batch_promotion_tasks.poll_pending_bronze_batches',
        'schedule': 10.0,  # Every 10 seconds
        'options': {'queue': 'celery'},
    },
})
