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

# Flag to control whether to use database-driven mappings or hardcoded extractors
USE_DYNAMIC_MAPPINGS = os.environ.get('GPS_CDM_USE_DYNAMIC_MAPPINGS', 'true').lower() == 'true'


# =============================================================================
# LINEAGE AND OBSERVABILITY HELPERS
# =============================================================================

def ensure_batch_tracking(cursor, batch_id: str, message_type: str, source_system: str = 'KAFKA') -> None:
    """
    Ensure a batch tracking record exists in obs_batch_tracking.
    This is required before inserting lineage records due to FK constraint.

    Args:
        cursor: Database cursor
        batch_id: Batch identifier
        message_type: Message type being processed
        source_system: Source system name
    """
    cursor.execute("""
        INSERT INTO observability.obs_batch_tracking (
            batch_id, message_type, source_system, status, current_layer,
            started_at, created_at, updated_at
        ) VALUES (%s, %s, %s, 'PROCESSING', 'bronze', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (batch_id) DO UPDATE SET
            updated_at = CURRENT_TIMESTAMP
    """, (batch_id, message_type, source_system))


def update_batch_tracking_layer(
    cursor,
    batch_id: str,
    layer: str,
    record_count: int,
    status: str = 'PROCESSING'
) -> None:
    """
    Update batch tracking with layer completion info.

    Args:
        cursor: Database cursor
        batch_id: Batch identifier
        layer: Current layer (bronze, silver, gold)
        record_count: Number of records processed
        status: Processing status
    """
    layer_column = f"{layer}_records"
    completed_column = f"{layer}_completed_at"

    cursor.execute(f"""
        UPDATE observability.obs_batch_tracking
        SET current_layer = %s,
            {layer_column} = %s,
            {completed_column} = CURRENT_TIMESTAMP,
            status = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE batch_id = %s
    """, (layer, record_count, status, batch_id))


# NOTE: PostgreSQL lineage tracking removed - all lineage is now in Neo4j only
# See update_neo4j_lineage() for lineage tracking implementation
#
# BATCH STATISTICS TRACKING:
# -------------------------
# Batch statistics are tracked in TWO places for redundancy:
#
# 1. PostgreSQL (observability.obs_batch_tracking):
#    - Minimal operational tracking for database queries
#    - Columns: batch_id, message_type, status, bronze_records, silver_records, gold_records
#    - Updated via ensure_batch_tracking() and update_batch_tracking_layer()
#
# 2. Neo4j (primary lineage store):
#    - Batch nodes with BatchLayer child nodes
#    - Contains: processed_count, failed_count, input_count, duration_ms
#    - Relationships: PROMOTED_TO between layers with success_rate
#    - Updated via update_neo4j_lineage()
#
# Neo4j is the source of truth for lineage; PostgreSQL is for operational queries


def update_neo4j_lineage(
    batch_id: str,
    message_type: str,
    bronze_count: int,
    silver_count: int,
    gold_count: int,
    duration_ms: int,
    status: str,
) -> bool:
    """
    Update Neo4j knowledge graph with batch lineage information.

    Args:
        batch_id: Batch identifier
        message_type: Message type processed
        bronze_count: Number of Bronze records
        silver_count: Number of Silver records
        gold_count: Number of Gold records
        duration_ms: Total processing duration in milliseconds
        status: Final batch status

    Returns:
        True if successful, False otherwise
    """
    try:
        from gps_cdm.orchestration.neo4j_service import get_neo4j_service
        neo4j = get_neo4j_service()

        if not neo4j.is_available():
            logger.warning("Neo4j not available for lineage update")
            return False

        now = datetime.utcnow()

        # Create/update batch node
        neo4j.upsert_batch({
            'batch_id': batch_id,
            'message_type': message_type,
            'source_system': 'GPS_CDM',
            'status': status,
            'created_at': now.isoformat(),
            'completed_at': now.isoformat() if status in ('SUCCESS', 'PARTIAL', 'FAILED') else None,
            'total_records': bronze_count,
            'duration_ms': duration_ms,
        })

        # Create/update Bronze layer stats
        if bronze_count > 0:
            neo4j.upsert_batch_layer(batch_id, 'bronze', {
                'input_count': bronze_count,
                'processed_count': bronze_count,
                'failed_count': 0,
                'pending_count': 0,
                'started_at': now.isoformat(),
                'completed_at': now.isoformat(),
            })

        # Create/update Silver layer stats and promotion
        if silver_count > 0:
            neo4j.upsert_batch_layer(batch_id, 'silver', {
                'input_count': bronze_count,
                'processed_count': silver_count,
                'failed_count': bronze_count - silver_count,
                'pending_count': 0,
                'started_at': now.isoformat(),
                'completed_at': now.isoformat(),
            })

            # Create Bronze -> Silver promotion relationship
            success_rate = silver_count / bronze_count if bronze_count > 0 else 0
            neo4j.create_layer_promotion(
                batch_id=batch_id,
                source_layer='bronze',
                target_layer='silver',
                record_count=silver_count,
                success_rate=success_rate,
            )

        # Create/update Gold layer stats and promotion
        if gold_count > 0:
            neo4j.upsert_batch_layer(batch_id, 'gold', {
                'input_count': silver_count,
                'processed_count': gold_count,
                'failed_count': silver_count - gold_count if silver_count > gold_count else 0,
                'pending_count': 0,
                'started_at': now.isoformat(),
                'completed_at': now.isoformat(),
            })

            # Create Silver -> Gold promotion relationship
            success_rate = gold_count / silver_count if silver_count > 0 else 0
            neo4j.create_layer_promotion(
                batch_id=batch_id,
                source_layer='silver',
                target_layer='gold',
                record_count=gold_count,
                success_rate=success_rate,
            )

        logger.info(f"[{batch_id}] Neo4j lineage updated: Bronze={bronze_count}, Silver={silver_count}, Gold={gold_count}")
        return True

    except ImportError:
        logger.warning("Neo4j service not available (neo4j package not installed)")
        return False
    except Exception as e:
        logger.error(f"[{batch_id}] Failed to update Neo4j lineage: {e}")
        return False

# Import extractors and common persistence
from gps_cdm.message_formats.base import ExtractorRegistry, GoldEntityPersister
from gps_cdm.orchestration.dynamic_gold_mapper import DynamicGoldMapper

# Import ALL extractor modules to trigger registration
# Each module registers its extractor when imported
from gps_cdm.message_formats import pain001  # noqa: F401
from gps_cdm.message_formats import pacs008  # noqa: F401
# NOTE: All SWIFT MT imports removed - decommissioned Nov 2025
from gps_cdm.message_formats import fedwire  # noqa: F401
from gps_cdm.message_formats import ach      # noqa: F401
from gps_cdm.message_formats import rtp      # noqa: F401
from gps_cdm.message_formats import sepa     # noqa: F401
from gps_cdm.message_formats import bacs     # noqa: F401
from gps_cdm.message_formats import chaps    # noqa: F401
from gps_cdm.message_formats import fps      # noqa: F401
from gps_cdm.message_formats import chips    # noqa: F401
from gps_cdm.message_formats import fednow   # noqa: F401
from gps_cdm.message_formats import npp      # noqa: F401
from gps_cdm.message_formats import pix      # noqa: F401
from gps_cdm.message_formats import upi      # noqa: F401
from gps_cdm.message_formats import instapay # noqa: F401
from gps_cdm.message_formats import paynow   # noqa: F401
from gps_cdm.message_formats import promptpay # noqa: F401
from gps_cdm.message_formats import target2  # noqa: F401
from gps_cdm.message_formats import sarie    # noqa: F401
from gps_cdm.message_formats import uaefts   # noqa: F401
from gps_cdm.message_formats import rtgs_hk  # noqa: F401
from gps_cdm.message_formats import meps_plus # noqa: F401
from gps_cdm.message_formats import cnaps    # noqa: F401
from gps_cdm.message_formats import bojnet   # noqa: F401
from gps_cdm.message_formats import kftc     # noqa: F401
from gps_cdm.message_formats import camt053  # noqa: F401
# Import ISO 20022 composite format registry (registers pacs.002, pacs.004, pain.008 and composite formats)
from gps_cdm.message_formats import iso20022_registry  # noqa: F401


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
    msg_type_lower = message_type.lower().replace('.', '').replace('-', '').replace('_', '')

    # ISO 20022 XML formats
    iso20022_types = {
        'pain001', 'pain002', 'pain008',
        'pacs002', 'pacs003', 'pacs004', 'pacs008', 'pacs009',
        'camt052', 'camt053', 'camt054',
        'acmt', 'sepa', 'sepasct', 'sepasdd', 'sepainst',
        'rtp', 'fednow', 'npp',
        'chaps', 'fps', 'fasterpaymentsuk',
        'target2', 'rtgshk', 'rtgs',
        'mepsplus', 'meps',
        'uaefts',
        'promptpay', 'paynow', 'instapay',
    }
    if msg_type_lower in iso20022_types:
        return 'ISO20022'

    # SWIFT MT formats (start with 'mt' and have 3 digits)
    if msg_type_lower.startswith('mt'):
        return 'SWIFT_MT'

    # US formats
    if msg_type_lower == 'fedwire':
        return 'FEDWIRE'
    if msg_type_lower == 'ach' or msg_type_lower == 'nacha':
        return 'ACH'
    if msg_type_lower == 'chips':
        return 'CHIPS'

    # UK formats
    if msg_type_lower == 'bacs':
        return 'BACS'

    # Asian formats
    if msg_type_lower in ('cnaps', 'cnaps2'):
        return 'CNAPS'
    if msg_type_lower == 'bojnet':
        return 'BOJNET'
    if msg_type_lower == 'kftc':
        return 'KFTC'

    # Middle East formats
    if msg_type_lower == 'sarie':
        return 'SARIE'

    # JSON formats
    if msg_type_lower in ('pix', 'upi'):
        return 'JSON'

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

                # Run extractor to parse content and store output as JSON
                # This enables Bronze-to-Silver mapping to use JSON keys
                extractor_output_json = None
                try:
                    extractor = ExtractorRegistry.get(message_type)
                    if extractor:
                        # Get raw text from content
                        raw_text = None
                        if isinstance(msg_content, dict):
                            # Extract raw text for parsing - check 'raw' key first (even if multiple keys)
                            # This handles pre-split ACH/BACS messages that have {raw, file_header, batch_header}
                            if 'raw' in msg_content:
                                raw_text = msg_content['raw']
                            elif '_raw_text' in msg_content:
                                raw_text = msg_content['_raw_text']

                        # Parse based on format
                        parsed_content = None
                        if raw_text:
                            # Try extractor's parser - prefer parse_iso_paths() for ISO 20022 dot-notation keys
                            if hasattr(extractor, 'parser'):
                                parser = extractor.parser
                                try:
                                    # Use parse_iso_paths() for ISO 20022 formats to get dot-notation keys
                                    if hasattr(parser, 'parse_iso_paths'):
                                        parsed_content = parser.parse_iso_paths(raw_text)
                                    elif hasattr(parser, 'parse'):
                                        parsed_content = parser.parse(raw_text)
                                except Exception as parse_err:
                                    logger.debug(f"Extractor parser failed for {raw_id}: {parse_err}")

                            # Try generic parsing if extractor parser failed
                            if parsed_content is None:
                                try:
                                    # Try JSON
                                    parsed_content = json.loads(raw_text)
                                except (json.JSONDecodeError, TypeError):
                                    # Try XML via extractor's extract methods
                                    if raw_text.strip().startswith('<'):
                                        try:
                                            # Call extract_silver which handles XML parsing
                                            temp_record = extractor.extract_silver(
                                                {'_raw_text': raw_text}, raw_id, 'temp_stg', batch_id
                                            )
                                            parsed_content = temp_record
                                        except Exception:
                                            parsed_content = {'_raw_text': raw_text}
                                    else:
                                        parsed_content = {'_raw_text': raw_text}
                        else:
                            # Content is already a dict (pre-parsed JSON)
                            parsed_content = msg_content

                        extractor_output_json = json.dumps(parsed_content) if parsed_content else None
                except Exception as ext_err:
                    logger.warning(f"Failed to compute extractor output for {raw_id}: {ext_err}")
                    extractor_output_json = None

                # Insert into Bronze
                cursor.execute("""
                    INSERT INTO bronze.raw_payment_messages (
                        raw_id, message_type, message_format, raw_content,
                        raw_content_hash, source_system, source_file_path,
                        processing_status, _batch_id, _ingested_at, extractor_output
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (raw_id) DO NOTHING
                    RETURNING raw_id
                """, (
                    raw_id, message_type, message_format, content_str,
                    content_hash, 'NIFI', f'nifi://batch/{batch_id}',
                    'PENDING', batch_id, datetime.utcnow(), extractor_output_json
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

        # Read Bronze records (include extractor_output for pre-parsed content)
        placeholders = ','.join(['%s'] * len(raw_ids))
        cursor.execute(f"""
            SELECT raw_id, message_type, raw_content, extractor_output
            FROM bronze.raw_payment_messages
            WHERE raw_id IN ({placeholders})
              AND processing_status = 'PENDING'
        """, tuple(raw_ids))

        bronze_records = cursor.fetchall()

        for raw_id, msg_type, raw_content, extractor_output in bronze_records:
            try:
                # Use extractor_output if available (pre-parsed in Bronze processing)
                raw_text = None  # Initialize for legacy fallback
                if extractor_output:
                    if isinstance(extractor_output, str):
                        msg_content = json.loads(extractor_output)
                    else:
                        msg_content = extractor_output
                    logger.info(f"[SILVER] Using pre-parsed extractor_output for {raw_id}")
                else:
                    # Fall back to parsing raw_content (legacy records without extractor_output)
                    # Parse content
                    msg_content = json.loads(raw_content) if isinstance(raw_content, str) else raw_content

                    # Unwrap raw content if it was stored with {"raw": "..."} or {"_raw_text": "..."}
                    # Note: 'raw' key may exist with other keys (e.g., {raw, file_header, batch_header})
                    if isinstance(msg_content, dict):
                        if 'raw' in msg_content:
                            raw_text = msg_content['raw']
                        elif '_raw_text' in msg_content:
                            raw_text = msg_content['_raw_text']

                if not extractor_output and raw_text:
                    # Try to parse the raw text as JSON first
                    try:
                        msg_content = json.loads(raw_text)
                    except (json.JSONDecodeError, TypeError):
                        # Check if it's SWIFT MT format (starts with {1: or {2:)
                        if raw_text.strip().startswith('{1:') or raw_text.strip().startswith('{2:'):
                            # SWIFT MT block format - use format-specific parser if available
                            # Each format has its own parser that extracts fields correctly
                            parsed_successfully = False

                            # Try extractor's native parser first (e.g., MT103SwiftParser for MT103)
                            if hasattr(extractor, 'parser') and hasattr(extractor.parser, 'parse'):
                                try:
                                    msg_content = extractor.parser.parse(raw_text)
                                    parsed_successfully = True
                                    logger.info(f"Parsed SWIFT MT using {type(extractor.parser).__name__} for {raw_id}")
                                except Exception as parse_err:
                                    logger.warning(f"Format-specific parser failed for {raw_id}: {parse_err}")

                            # Fall back to ChapsSwiftParser (generic SWIFT parser)
                            if not parsed_successfully:
                                try:
                                    from gps_cdm.message_formats.chaps import ChapsSwiftParser
                                    swift_parser = ChapsSwiftParser()
                                    msg_content = swift_parser.parse(raw_text)
                                    logger.info(f"Parsed SWIFT MT using ChapsSwiftParser for {raw_id}: {list(msg_content.keys())}")
                                except Exception as swift_err:
                                    logger.warning(f"Failed to parse SWIFT MT for {raw_id}: {swift_err}")
                                    msg_content = {'_raw_text': raw_text, '_format': 'swift_mt'}
                        elif raw_text.strip().startswith('<'):
                            # XML format - use extractor's parser if available
                            # Prefer parse_iso_paths() for ISO 20022 dot-notation keys
                            if hasattr(extractor, 'parser'):
                                parser = extractor.parser
                                try:
                                    if hasattr(parser, 'parse_iso_paths'):
                                        msg_content = parser.parse_iso_paths(raw_text)
                                    elif hasattr(parser, 'parse'):
                                        msg_content = parser.parse(raw_text)
                                    else:
                                        msg_content = {'_raw_text': raw_text, '_format': 'xml'}
                                except Exception:
                                    msg_content = {'_raw_text': raw_text, '_format': 'xml'}
                            else:
                                msg_content = {'_raw_text': raw_text, '_format': 'xml'}
                        elif raw_text.strip().startswith('UHL1') or message_type.upper() == 'BACS':
                            # BACS Standard 18 fixed-width format
                            # Preserve header context fields before parsing
                            header_context = {k: v for k, v in msg_content.items()
                                             if k in ('processingDate', 'serviceUserNumber', 'serviceUserName')}
                            if hasattr(extractor, 'parser') and hasattr(extractor.parser, 'parse'):
                                try:
                                    parsed = extractor.parser.parse(raw_text)
                                    # Merge header context back into parsed output
                                    msg_content = parsed
                                    for k, v in header_context.items():
                                        if k not in msg_content or msg_content.get(k) is None:
                                            msg_content[k] = v
                                    logger.info(f"Parsed BACS for {raw_id}: keys={list(msg_content.keys())[:5]}")
                                except Exception as parse_err:
                                    logger.warning(f"Failed to parse BACS for {raw_id}: {parse_err}")
                                    msg_content = {'_raw_text': raw_text, '_format': 'bacs'}
                                    msg_content.update(header_context)
                            else:
                                msg_content = {'_raw_text': raw_text, '_format': 'bacs'}
                                msg_content.update(header_context)
                        elif raw_text.strip().startswith('{1') and len(raw_text.strip()) > 2 and raw_text.strip()[2:3].isdigit():
                            # FEDWIRE tag-value format (e.g., {1500}00, {1510}1000)
                            if hasattr(extractor, 'parser') and hasattr(extractor.parser, 'parse'):
                                try:
                                    msg_content = extractor.parser.parse(raw_text)
                                    logger.info(f"Parsed FEDWIRE for {raw_id}: keys={list(msg_content.keys())[:5]}")
                                except Exception as parse_err:
                                    logger.warning(f"Failed to parse FEDWIRE for {raw_id}: {parse_err}")
                                    msg_content = {'_raw_text': raw_text, '_format': 'fedwire'}
                            else:
                                msg_content = {'_raw_text': raw_text, '_format': 'fedwire'}
                        elif raw_text.strip()[:3] == '101' or msg_type.upper() in ('ACH', 'NACHA'):
                            # ACH/NACHA fixed-width format (starts with 101 for file header)
                            if hasattr(extractor, 'parser') and hasattr(extractor.parser, 'parse'):
                                try:
                                    msg_content = extractor.parser.parse(raw_text)
                                    logger.info(f"Parsed ACH for {raw_id}: keys={list(msg_content.keys())[:5]}")
                                except Exception as parse_err:
                                    logger.warning(f"Failed to parse ACH for {raw_id}: {parse_err}")
                                    msg_content = {'_raw_text': raw_text, '_format': 'ach'}
                            else:
                                msg_content = {'_raw_text': raw_text, '_format': 'ach'}
                        else:
                            msg_content = {'_raw_text': raw_text, '_format': 'raw'}

                # Generate stg_id
                stg_id = extractor.generate_stg_id()

                # Determine if content is JSON (proprietary format) vs XML (ISO 20022)
                # Regional systems like PIX, PayNow, KFTC, PROMPTPAY support both formats:
                # - JSON: domestic/proprietary format -> use extractor's extract_silver()
                # - XML: ISO 20022 format -> use DynamicMapper with ISO 20022 mappings
                is_json_content = False
                is_xml_content = False

                # Check raw content format (raw_content is from Bronze DB, may be JSON-wrapped)
                raw_str = raw_content if isinstance(raw_content, str) else str(raw_content)
                # Check if it was wrapped in {"raw": "..."} format
                if raw_text:
                    raw_str = raw_text  # Use unwrapped content

                if isinstance(raw_str, str):
                    stripped = raw_str.strip()
                    if stripped.startswith('{') and not stripped.startswith('{1:'):  # JSON but not SWIFT MT
                        is_json_content = True
                    elif stripped.startswith('<?xml') or stripped.startswith('<Document') or stripped.startswith('<'):
                        is_xml_content = True

                # Also check parsed content for format indicators
                if isinstance(msg_content, dict):
                    # Check if parsed content indicates format
                    content_format = msg_content.get('_format', '')
                    if content_format in ('json', 'JSON'):
                        is_json_content = True
                    elif content_format in ('xml', 'iso20022'):
                        is_xml_content = True
                    # Check for ISO 20022 indicators
                    elif msg_content.get('isISO20022') or msg_content.get('Document'):
                        is_xml_content = True
                    # Check for JSON-only fields (no ISO 20022 equivalent path)
                    elif any(k in msg_content for k in ['payerName', 'payeeName', 'payerAccount', 'payeeAccount',
                                                        'payerProxyType', 'payeeProxyType', 'payerIspb', 'payeeIspb']):
                        is_json_content = True

                # NOTE: We use DynamicMapper for ALL formats (both XML and JSON)
                # The DynamicMapper's _resolve_path() handles multiple path formats:
                # - Nested paths: debtor.name -> data['debtor']['name']
                # - Flat camelCase: debtorName -> data['debtorName']
                # - Direct key: messageId -> data['messageId']
                # This approach is consistent with the user's preference for database-driven mappings
                use_extractor_for_silver = False  # Always use dynamic mappings

                # ENHANCED LOGGING: Log source data before extraction
                logger.info(f"[SILVER][{batch_id}] raw_id={raw_id}, message_type={message_type}")
                logger.info(f"[SILVER][{batch_id}] Format detection: is_json={is_json_content}, is_xml={is_xml_content}, use_extractor={use_extractor_for_silver}")
                if isinstance(msg_content, dict):
                    sample_keys = list(msg_content.keys())[:10]
                    logger.info(f"[SILVER][{batch_id}] Source data keys: {sample_keys}")

                # Extract Silver record using appropriate method
                if USE_DYNAMIC_MAPPINGS and not use_extractor_for_silver:
                    # Use database-driven field mappings (for XML/ISO 20022 content)
                    from gps_cdm.orchestration.dynamic_mapper import DynamicMapper
                    mapper = DynamicMapper(conn)

                    silver_record = mapper.extract_silver_record(message_type, msg_content, raw_id, batch_id)
                    silver_record['stg_id'] = stg_id  # Override generated stg_id
                    silver_record['raw_id'] = raw_id  # Ensure raw_id is set for lineage

                    # Get table from format registry
                    format_info = mapper._get_format_info(message_type)
                    silver_table = format_info['silver_table']
                    columns = mapper.get_silver_columns(message_type)
                    values = mapper.get_silver_values(message_type, silver_record)

                    # ENHANCED LOGGING: Log format resolution and record details
                    logger.info(f"[SILVER][{batch_id}] Format resolved: format_id={format_info.get('format_id')}, "
                               f"base_format={format_info.get('base_format_id')}, table={silver_table}")
                    logger.info(f"[SILVER][{batch_id}] Columns: {len(columns)}, Values: {len(values)}")

                    # Log first few non-null values for debugging
                    non_null_cols = [(c, v) for c, v in zip(columns, values) if v is not None and str(v).strip()]
                    if non_null_cols:
                        sample = non_null_cols[:5]
                        logger.info(f"[SILVER][{batch_id}] Sample values: {sample}")
                else:
                    # Use extractor's extract_silver() for JSON/proprietary content
                    # The extractor handles JSON field mapping internally
                    logger.info(f"[SILVER][{batch_id}] Using extractor.extract_silver() for {message_type}")
                    silver_record = extractor.extract_silver(msg_content, raw_id, stg_id, batch_id)
                    silver_table = extractor.SILVER_TABLE
                    columns = extractor.get_silver_columns()
                    values = extractor.get_silver_values(silver_record)

                    # Log extractor results
                    non_null_count = sum(1 for v in values if v is not None and str(v).strip())
                    logger.info(f"[SILVER][{batch_id}] Extractor result: table={silver_table}, columns={len(columns)}, non_null_values={non_null_count}")

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
                    logger.info(f"[SILVER][{batch_id}] SUCCESS: stg_id={stg_id}, raw_id={raw_id}, table={silver_table}")

                    # Update Bronze status
                    cursor.execute("""
                        UPDATE bronze.raw_payment_messages
                        SET processing_status = 'PROMOTED_TO_SILVER',
                            processed_to_silver_at = CURRENT_TIMESTAMP
                        WHERE raw_id = %s
                    """, (raw_id,))
                else:
                    logger.warning(f"[SILVER][{batch_id}] DUPLICATE: stg_id={stg_id} already exists")
                    failed.append({
                        'raw_id': raw_id,
                        'error': 'Duplicate stg_id (conflict)',
                        'error_code': 'DUPLICATE_MESSAGE'
                    })

            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()

                # ENHANCED LOGGING: Log full error details for troubleshooting
                logger.error(f"[SILVER][{batch_id}] FAILED: raw_id={raw_id}, message_type={message_type}")
                logger.error(f"[SILVER][{batch_id}] Error: {str(e)[:500]}")
                logger.error(f"[SILVER][{batch_id}] Stack trace:\n{error_trace}")

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

        # Read Silver records - get ALL columns for complete data
        # Use DynamicMapper for table/columns when enabled, otherwise use extractor
        if USE_DYNAMIC_MAPPINGS:
            from gps_cdm.orchestration.dynamic_mapper import DynamicMapper
            mapper = DynamicMapper(conn)
            format_info = mapper._get_format_info(message_type)
            silver_table = format_info['silver_table']
            silver_columns = mapper.get_silver_columns(message_type)
        else:
            silver_table = extractor.SILVER_TABLE
            silver_columns = extractor.get_silver_columns()
        col_list = ', '.join(silver_columns)

        placeholders = ','.join(['%s'] * len(stg_ids))
        cursor.execute(f"""
            SELECT {col_list}
            FROM silver.{silver_table}
            WHERE stg_id IN ({placeholders})
        """, tuple(stg_ids))

        silver_records = cursor.fetchall()

        logger.info(f"[GOLD][{batch_id}] message_type={message_type}, stg_ids={stg_ids}, found {len(silver_records)} silver records")

        for silver_row in silver_records:
            # Convert to dict using column names
            silver_data = dict(zip(silver_columns, silver_row))
            stg_id = silver_data.get('stg_id')
            raw_id = silver_data.get('raw_id')

            # ENHANCED LOGGING: Log Silver data being processed for Gold
            logger.info(f"[GOLD][{batch_id}] Processing stg_id={stg_id}, raw_id={raw_id}")
            non_null_silver = {k: v for k, v in silver_data.items() if v is not None}
            sample_keys = list(non_null_silver.keys())[:10]
            logger.info(f"[GOLD][{batch_id}] Silver data keys (non-null): {sample_keys}")

            try:
                # Use DynamicGoldMapper for database-driven Gold processing
                # This reads from mapping.gold_field_mappings to determine how to
                # map Silver columns to all Gold tables (cdm_party, cdm_account,
                # cdm_financial_institution, cdm_payment_instruction, extensions)
                from gps_cdm.orchestration.dynamic_gold_mapper import DynamicGoldMapper
                from gps_cdm.message_formats.base import detect_message_routing

                gold_mapper = DynamicGoldMapper(conn)

                # Detect message routing for formats that require subtype detection
                # This determines which ISO 20022 message type to route to based on
                # the actual content (e.g., ACH credit vs debit → pacs.008 vs pain.008)
                raw_content = silver_data.get('_raw_content', '')
                subtype, target_iso, routing_key = detect_message_routing(
                    message_type, raw_content, silver_data
                )
                logger.info(
                    f"[GOLD][{batch_id}] Routing: subtype={subtype.name}, "
                    f"target_iso={target_iso}, routing_key={routing_key}"
                )

                # Build Gold records from Silver data using database mappings
                # Pass routing info for conditional mapping selection
                logger.info(f"[GOLD][{batch_id}] Building Gold records for {message_type}")
                gold_records = gold_mapper.build_gold_records(
                    message_type, silver_data, stg_id, batch_id,
                    routing_key=routing_key, target_iso_type=target_iso
                )

                # ENHANCED LOGGING: Log what Gold records are being built
                for table_key, records in gold_records.items():
                    if records:
                        logger.info(f"[GOLD][{batch_id}] Table {table_key}: {len(records)} records")
                        if records and isinstance(records[0], dict):
                            sample_cols = list(records[0].keys())[:8]
                            logger.info(f"[GOLD][{batch_id}] {table_key} columns: {sample_cols}")

                # Persist all Gold records (entities first, then instruction, then extensions)
                entity_ids = gold_mapper.persist_gold_records(cursor, gold_records, message_type)
                logger.info(f"[GOLD][{batch_id}] Entity IDs created: {entity_ids}")

                # Persist normalized entity identifiers (IBAN, BIC, LEI, etc.)
                from gps_cdm.orchestration.dynamic_gold_mapper import persist_identifiers
                persist_identifiers(cursor, silver_data, entity_ids, message_type, stg_id)
                logger.debug(f"[GOLD][{batch_id}] Entity identifiers persisted")

                # Count created entities for response
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
                if entity_ids.get('account_servicer_id'):
                    entities_created['financial_institutions'] += 1

                # Check for either instruction_id (payment messages) or statement_id (statement messages like camt.053, MT940)
                instruction_id = entity_ids.get('instruction_id')
                statement_id = entity_ids.get('statement_id')
                gold_id = instruction_id or statement_id

                if gold_id:
                    instruction_ids.append(gold_id)
                    logger.info(f"[GOLD][{batch_id}] SUCCESS: instruction_id={gold_id}, stg_id={stg_id}")

                    # Update Silver status
                    cursor.execute(f"""
                        UPDATE silver.{silver_table}
                        SET processing_status = 'PROMOTED_TO_GOLD',
                            processed_to_gold_at = CURRENT_TIMESTAMP
                        WHERE stg_id = %s
                    """, (stg_id,))
                else:
                    logger.warning(f"[GOLD][{batch_id}] NO_INSTRUCTION: stg_id={stg_id}, entity_ids={entity_ids}")
                    failed.append({
                        'stg_id': stg_id,
                        'error': 'No instruction or statement created (possible duplicate or missing data)',
                        'error_code': 'DUPLICATE_MESSAGE'
                    })

            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()

                # ENHANCED LOGGING: Log full error details for Gold failures
                logger.error(f"[GOLD][{batch_id}] FAILED: stg_id={stg_id}, message_type={message_type}")
                logger.error(f"[GOLD][{batch_id}] Error: {str(e)[:500]}")
                logger.error(f"[GOLD][{batch_id}] Stack trace:\n{error_trace}")

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


# =============================================================================
# MEDALLION ORCHESTRATOR TASK
# =============================================================================

@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True,
             name='gps_cdm.zone_tasks.process_medallion_pipeline')
def process_medallion_pipeline(
    self,
    batch_id: str,
    records: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Orchestrate the complete medallion pipeline: Bronze → Silver → Gold.

    This task ensures:
    1. Transactional integrity per zone (ACID)
    2. No Gold records without Silver records
    3. No Silver records without Bronze records
    4. Proper ID passing between zones
    5. Complete lineage tracking

    The flow is:
    1. Process all records to Bronze (returns raw_ids)
    2. Group raw_ids by message_type
    3. For each message_type, process Silver (returns stg_ids)
    4. For each message_type, process Gold (returns instruction_ids)
    5. Track lineage for all successful records

    Args:
        batch_id: Unique batch identifier
        records: List of {content: str/dict, message_type: str}
        config: Optional configuration

    Returns:
        {
            status: 'SUCCESS' | 'PARTIAL' | 'FAILED',
            batch_id: str,
            bronze: {raw_ids: [...], failed: [...]},
            silver: {stg_ids: [...], failed: [...]},
            gold: {instruction_ids: [...], failed: [...]},
            lineage: {...},
            duration_seconds: float
        }
    """
    start_time = datetime.utcnow()

    result = {
        'status': 'PENDING',
        'batch_id': batch_id,
        'bronze': {'raw_ids': [], 'failed': []},
        'silver': {'stg_ids': [], 'failed': []},
        'gold': {'instruction_ids': [], 'failed': []},
        'lineage': {},
        'duration_seconds': 0,
    }

    conn = None
    cursor = None

    try:
        # =====================================================================
        # STEP 1: BRONZE - Ingest all records
        # =====================================================================
        logger.info(f"[{batch_id}] Starting Bronze processing for {len(records)} records")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Determine primary message type for batch tracking
        primary_message_type = records[0].get('message_type', 'UNKNOWN') if records else 'UNKNOWN'

        # Create batch tracking record (for PostgreSQL operational tracking)
        ensure_batch_tracking(cursor, batch_id, primary_message_type, 'KAFKA')
        conn.commit()

        # Group records by message_type for tracking
        raw_ids_by_type = {}

        # Import message splitter for multi-record files
        from gps_cdm.orchestration.message_splitter import split_message

        # Expand records: split multi-record files into individual transactions
        expanded_records = []
        for record in records:
            content = record.get('content', record)
            message_type = record.get('message_type', 'UNKNOWN')
            kafka_metadata = record.get('kafka_metadata', {})

            # Get raw content string for splitting
            if isinstance(content, str):
                raw_content = content
            elif isinstance(content, dict):
                # Check if it contains raw text (from file)
                raw_content = content.get('_raw_text', content.get('raw', ''))
                if not raw_content:
                    raw_content = json.dumps(content)
            else:
                raw_content = str(content)

            # Split into individual records
            split_records = split_message(raw_content, message_type)

            for split_rec in split_records:
                expanded_records.append({
                    'content': split_rec['content'],
                    'message_type': message_type,
                    'kafka_metadata': kafka_metadata,
                    'parent_context': split_rec.get('parent_context', {}),
                    'record_index': split_rec.get('index', 0),
                })

        logger.info(f"[{batch_id}] Expanded {len(records)} input records to {len(expanded_records)} individual transactions")

        for idx, record in enumerate(expanded_records):
            try:
                content = record.get('content', record)
                message_type = record.get('message_type', 'UNKNOWN')

                # Parse content if string
                if isinstance(content, str):
                    try:
                        msg_content = json.loads(content)
                    except json.JSONDecodeError:
                        msg_content = {'_raw_text': content}
                else:
                    msg_content = content

                # Merge parent context if available
                parent_context = record.get('parent_context', {})
                if parent_context and isinstance(msg_content, dict):
                    # Parent context provides shared fields (e.g., debtor info)
                    for key, value in parent_context.items():
                        if key not in msg_content or msg_content[key] is None:
                            msg_content[key] = value

                # Generate raw_id
                raw_id = f"raw_{uuid.uuid4().hex[:12]}"

                # Compute content hash
                content_str = json.dumps(msg_content, sort_keys=True) if isinstance(msg_content, dict) else str(msg_content)
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
                    content_hash, 'KAFKA', f'kafka://batch/{batch_id}',
                    'PENDING', batch_id, datetime.utcnow()
                ))

                row = cursor.fetchone()
                if row:
                    result['bronze']['raw_ids'].append(raw_id)

                    # Group by message_type for Silver processing
                    if message_type not in raw_ids_by_type:
                        raw_ids_by_type[message_type] = []
                    raw_ids_by_type[message_type].append(raw_id)
                else:
                    result['bronze']['failed'].append({
                        'index': idx,
                        'message_type': message_type,
                        'error': 'Duplicate record',
                        'error_code': 'DUPLICATE_MESSAGE'
                    })

            except Exception as e:
                import traceback
                result['bronze']['failed'].append({
                    'index': idx,
                    'message_type': record.get('message_type', 'UNKNOWN'),
                    'error': str(e),
                    'error_code': 'PARSE_ERROR'
                })

        # COMMIT Bronze transaction - ensures ACID for Bronze zone
        conn.commit()
        logger.info(f"[{batch_id}] Bronze complete: {len(result['bronze']['raw_ids'])} succeeded, {len(result['bronze']['failed'])} failed")

        # If Bronze completely failed, stop here
        if not result['bronze']['raw_ids']:
            result['status'] = 'FAILED'
            result['duration_seconds'] = (datetime.utcnow() - start_time).total_seconds()
            return result

        # =====================================================================
        # STEP 2: SILVER - Transform records by message_type
        # =====================================================================
        logger.info(f"[{batch_id}] Starting Silver processing for {len(raw_ids_by_type)} message types")

        stg_ids_by_type = {}

        for message_type, raw_ids in raw_ids_by_type.items():
            # Get extractor for this message type
            extractor = ExtractorRegistry.get(message_type)

            if not extractor:
                logger.warning(f"[{batch_id}] No extractor for message type: {message_type}, skipping Silver")
                for raw_id in raw_ids:
                    result['silver']['failed'].append({
                        'raw_id': raw_id,
                        'message_type': message_type,
                        'error': f'No extractor for {message_type}',
                        'error_code': 'NO_EXTRACTOR'
                    })
                continue

            silver_table = extractor.SILVER_TABLE

            # Read Bronze records for this message type
            placeholders = ','.join(['%s'] * len(raw_ids))
            cursor.execute(f"""
                SELECT raw_id, raw_content
                FROM bronze.raw_payment_messages
                WHERE raw_id IN ({placeholders})
                  AND processing_status = 'PENDING'
            """, tuple(raw_ids))

            bronze_records = cursor.fetchall()

            stg_ids_for_type = []

            for raw_id, raw_content in bronze_records:
                # Use savepoint to isolate each record's transaction
                # This prevents a single failure from aborting the entire batch
                savepoint_name = f"sp_silver_{raw_id.replace('-', '_')}"
                try:
                    cursor.execute(f"SAVEPOINT {savepoint_name}")

                    # Parse raw_content - Bronze stores data in original format (XML, SWIFT MT, etc.)
                    raw_text = None
                    if isinstance(raw_content, str):
                        try:
                            msg_content = json.loads(raw_content)
                            # Check if JSON-wrapped raw content
                            # Note: 'raw' key may exist with other keys (e.g., {raw, file_header, batch_header})
                            if isinstance(msg_content, dict):
                                if 'raw' in msg_content:
                                    raw_text = msg_content['raw']
                                elif '_raw_text' in msg_content:
                                    raw_text = msg_content['_raw_text']
                        except json.JSONDecodeError:
                            # Not JSON - this is raw format content (XML, SWIFT MT, NACHA, etc.)
                            raw_text = raw_content
                            msg_content = {}
                    else:
                        msg_content = raw_content

                    if raw_text:
                        # Try to parse the raw text as JSON first
                        try:
                            msg_content = json.loads(raw_text)
                        except (json.JSONDecodeError, TypeError):
                            # Check if it's SWIFT MT format (starts with {1: or {2:)
                            if raw_text.strip().startswith('{1:') or raw_text.strip().startswith('{2:'):
                                # SWIFT MT block format - use format-specific parser if available
                                parsed_successfully = False

                                # Try extractor's native parser first (e.g., MT103SwiftParser for MT103)
                                if hasattr(extractor, 'parser') and hasattr(extractor.parser, 'parse'):
                                    try:
                                        msg_content = extractor.parser.parse(raw_text)
                                        parsed_successfully = True
                                        logger.info(f"[{batch_id}] Parsed SWIFT MT using {type(extractor.parser).__name__} for {raw_id}")
                                    except Exception as parse_err:
                                        logger.warning(f"[{batch_id}] Format-specific parser failed for {raw_id}: {parse_err}")

                                # Fall back to ChapsSwiftParser (generic SWIFT parser)
                                if not parsed_successfully:
                                    try:
                                        from gps_cdm.message_formats.chaps import ChapsSwiftParser
                                        swift_parser = ChapsSwiftParser()
                                        msg_content = swift_parser.parse(raw_text)
                                        logger.info(f"[{batch_id}] Parsed SWIFT MT using ChapsSwiftParser for {raw_id}: keys={list(msg_content.keys())[:5]}")
                                    except Exception as parse_err:
                                        logger.warning(f"[{batch_id}] Failed to parse SWIFT MT for {raw_id}: {parse_err}")
                                        msg_content = {'_raw_text': raw_text, '_format': 'swift_mt'}
                            elif raw_text.strip().startswith('<'):
                                # XML format - use extractor's parser if available
                                if hasattr(extractor, 'parser') and hasattr(extractor.parser, 'parse'):
                                    try:
                                        msg_content = extractor.parser.parse(raw_text)
                                        logger.info(f"[{batch_id}] Parsed XML for {raw_id}: keys={list(msg_content.keys())[:5]}")
                                    except Exception as parse_err:
                                        logger.warning(f"[{batch_id}] Failed to parse XML for {raw_id}: {parse_err}")
                                        msg_content = {'_raw_text': raw_text, '_format': 'xml'}
                                else:
                                    msg_content = {'_raw_text': raw_text, '_format': 'xml'}
                            elif raw_text.strip().startswith('{1') and raw_text.strip()[2:3].isdigit():
                                # FEDWIRE tag-value format (e.g., {1500}00, {1510}1000)
                                if hasattr(extractor, 'parser') and hasattr(extractor.parser, 'parse'):
                                    try:
                                        msg_content = extractor.parser.parse(raw_text)
                                        logger.info(f"[{batch_id}] Parsed FEDWIRE for {raw_id}: keys={list(msg_content.keys())[:5]}")
                                    except Exception as parse_err:
                                        logger.warning(f"[{batch_id}] Failed to parse FEDWIRE for {raw_id}: {parse_err}")
                                        msg_content = {'_raw_text': raw_text, '_format': 'fedwire'}
                                else:
                                    msg_content = {'_raw_text': raw_text, '_format': 'fedwire'}
                            elif raw_text.strip()[:3] == '101' or message_type.upper() in ('ACH', 'NACHA'):
                                # ACH/NACHA fixed-width format (starts with 101 for file header)
                                if hasattr(extractor, 'parser') and hasattr(extractor.parser, 'parse'):
                                    try:
                                        msg_content = extractor.parser.parse(raw_text)
                                        logger.info(f"[{batch_id}] Parsed ACH for {raw_id}: keys={list(msg_content.keys())[:5]}")
                                    except Exception as parse_err:
                                        logger.warning(f"[{batch_id}] Failed to parse ACH for {raw_id}: {parse_err}")
                                        msg_content = {'_raw_text': raw_text, '_format': 'ach'}
                                else:
                                    msg_content = {'_raw_text': raw_text, '_format': 'ach'}
                            elif raw_text.strip().startswith('UHL1') or message_type.upper() == 'BACS':
                                # BACS Standard 18 fixed-width format (starts with UHL1 header)
                                # Preserve header context fields before parsing
                                header_context = {k: v for k, v in msg_content.items()
                                                 if k in ('processingDate', 'serviceUserNumber', 'serviceUserName')}
                                if hasattr(extractor, 'parser') and hasattr(extractor.parser, 'parse'):
                                    try:
                                        parsed = extractor.parser.parse(raw_text)
                                        # Merge header context back into parsed output
                                        msg_content = parsed
                                        for k, v in header_context.items():
                                            if k not in msg_content or msg_content.get(k) is None:
                                                msg_content[k] = v
                                        logger.info(f"[{batch_id}] Parsed BACS for {raw_id}: keys={list(msg_content.keys())[:5]}")
                                    except Exception as parse_err:
                                        logger.warning(f"[{batch_id}] Failed to parse BACS for {raw_id}: {parse_err}")
                                        msg_content = {'_raw_text': raw_text, '_format': 'bacs'}
                                        msg_content.update(header_context)
                                else:
                                    msg_content = {'_raw_text': raw_text, '_format': 'bacs'}
                                    msg_content.update(header_context)
                            else:
                                # Unknown format - pass raw text to extractor
                                msg_content = {'_raw_text': raw_text, '_format': 'raw'}

                    # Generate stg_id
                    stg_id = extractor.generate_stg_id()

                    # Extract Silver record using either DynamicMapper (database-driven) or hardcoded extractor
                    if USE_DYNAMIC_MAPPINGS:
                        # Use database-driven field mappings
                        from gps_cdm.orchestration.dynamic_mapper import DynamicMapper
                        mapper = DynamicMapper(conn)
                        silver_record = mapper.extract_silver_record(message_type, msg_content, raw_id, batch_id)
                        silver_record['stg_id'] = stg_id  # Override generated stg_id

                        # Get table from format registry
                        format_info = mapper._get_format_info(message_type)
                        silver_table = format_info['silver_table']
                        columns = mapper.get_silver_columns(message_type)
                        values = mapper.get_silver_values(message_type, silver_record)

                        logger.debug(f"[{batch_id}] Using DynamicMapper for {message_type}: {len(columns)} columns")
                    else:
                        # Use hardcoded extractor (legacy)
                        silver_record = extractor.extract_silver(msg_content, raw_id, stg_id, batch_id)
                        columns = extractor.get_silver_columns()
                        values = extractor.get_silver_values(silver_record)

                    # Build INSERT
                    col_names = ', '.join(columns)
                    placeholders_sql = ', '.join(['%s'] * len(columns))

                    cursor.execute(f"""
                        INSERT INTO silver.{silver_table} ({col_names})
                        VALUES ({placeholders_sql})
                        ON CONFLICT (stg_id) DO NOTHING
                        RETURNING stg_id
                    """, values)

                    row = cursor.fetchone()
                    if row:
                        result['silver']['stg_ids'].append(stg_id)
                        stg_ids_for_type.append(stg_id)

                        # Update Bronze status
                        cursor.execute("""
                            UPDATE bronze.raw_payment_messages
                            SET processing_status = 'PROMOTED_TO_SILVER',
                                processed_to_silver_at = CURRENT_TIMESTAMP
                            WHERE raw_id = %s
                        """, (raw_id,))

                        # Release the savepoint on success
                        cursor.execute(f"RELEASE SAVEPOINT {savepoint_name}")
                    else:
                        cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                        result['silver']['failed'].append({
                            'raw_id': raw_id,
                            'message_type': message_type,
                            'error': 'Duplicate stg_id',
                            'error_code': 'DUPLICATE_MESSAGE'
                        })

                except Exception as e:
                    # Rollback to savepoint to allow subsequent records to continue
                    try:
                        cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                    except Exception:
                        pass  # Savepoint might not exist if error was during SAVEPOINT creation
                    result['silver']['failed'].append({
                        'raw_id': raw_id,
                        'message_type': message_type,
                        'error': str(e),
                        'error_code': 'TRANSFORM_ERROR'
                    })

            stg_ids_by_type[message_type] = stg_ids_for_type

        # COMMIT Silver transaction - ensures ACID for Silver zone
        conn.commit()
        logger.info(f"[{batch_id}] Silver complete: {len(result['silver']['stg_ids'])} succeeded, {len(result['silver']['failed'])} failed")

        # Update batch tracking with Bronze and Silver completion
        update_batch_tracking_layer(cursor, batch_id, 'bronze', len(result['bronze']['raw_ids']), 'PROCESSING')
        update_batch_tracking_layer(cursor, batch_id, 'silver', len(result['silver']['stg_ids']), 'PROCESSING')
        conn.commit()

        # If Silver completely failed, stop here (Bronze is committed)
        if not result['silver']['stg_ids']:
            result['status'] = 'PARTIAL'  # Bronze succeeded but Silver failed
            result['duration_seconds'] = (datetime.utcnow() - start_time).total_seconds()
            return result

        # =====================================================================
        # STEP 3: GOLD - Normalize and map to CDM
        # =====================================================================
        logger.info(f"[{batch_id}] Starting Gold processing")

        for message_type, stg_ids in stg_ids_by_type.items():
            if not stg_ids:
                continue

            extractor = ExtractorRegistry.get(message_type)
            if not extractor:
                continue

            silver_table = extractor.SILVER_TABLE

            # Read Silver records - Gold reads from Silver (already parsed data), NOT Bronze
            placeholders = ','.join(['%s'] * len(stg_ids))

            # Get all columns from Silver table for Gold entity extraction
            # When USE_DYNAMIC_MAPPINGS is enabled, we need to query using the same columns
            # that DynamicMapper used to insert the data (database-driven mappings)
            if USE_DYNAMIC_MAPPINGS:
                from gps_cdm.orchestration.dynamic_mapper import DynamicMapper
                mapper = DynamicMapper(conn)
                silver_columns = mapper.get_silver_columns(message_type)
            else:
                silver_columns = extractor.get_silver_columns()
            col_list = ', '.join(silver_columns)

            cursor.execute(f"""
                SELECT {col_list}
                FROM silver.{silver_table}
                WHERE stg_id IN ({placeholders})
            """, tuple(stg_ids))

            silver_records = cursor.fetchall()

            # Convert to dict for easier access
            for silver_row in silver_records:
                silver_data = dict(zip(silver_columns, silver_row))
                stg_id = silver_data.get('stg_id')
                raw_id = silver_data.get('raw_id')

                # Use savepoint to isolate each record's transaction
                savepoint_name = f"sp_gold_{stg_id.replace('-', '_')}"
                try:
                    cursor.execute(f"SAVEPOINT {savepoint_name}")

                    # Gold reads from Silver (already parsed/validated data)
                    # No need to re-parse Bronze - Silver has the structured data

                    # Extract Gold entities from Silver data
                    gold_entities = extractor.extract_gold_entities(silver_data, stg_id, batch_id)

                    # Persist entities
                    entity_ids = GoldEntityPersister.persist_all_entities(
                        cursor, gold_entities, message_type, stg_id, 'GPS_CDM'
                    )

                    # Create payment instruction
                    instruction_id = f"instr_{uuid.uuid4().hex[:12]}"
                    payment_id = f"pmt_{uuid.uuid4().hex[:12]}"

                    # Extract amount/currency from Silver data (already parsed)
                    # Silver tables use standardized column names
                    amount = silver_data.get('amount') or silver_data.get('instructed_amount') or 0
                    currency = silver_data.get('currency') or silver_data.get('instructed_currency')
                    # Default currencies by scheme (BACS/CHAPS/FPS are GBP, SEPA is EUR)
                    if not currency or currency == 'XXX':
                        scheme_currencies = {'bacs': 'GBP', 'chaps': 'GBP', 'fps': 'GBP', 'sepa': 'EUR'}
                        currency = scheme_currencies.get(message_type.lower(), 'XXX')
                    end_to_end_id = silver_data.get('end_to_end_id') or silver_data.get('message_id')
                    uetr = silver_data.get('uetr')

                    payment_type_map = {
                        'pain.001': 'CREDIT_TRANSFER', 'pain001': 'CREDIT_TRANSFER',
                        'pacs.008': 'CREDIT_TRANSFER', 'pacs008': 'CREDIT_TRANSFER',
                        'mt103': 'CREDIT_TRANSFER', 'fedwire': 'WIRE_TRANSFER',
                        'ach': 'ACH_TRANSFER', 'rtp': 'REAL_TIME', 'sepa': 'CREDIT_TRANSFER',
                        'bacs': 'BATCH_PAYMENT', 'chaps': 'CREDIT_TRANSFER', 'fps': 'INSTANT_PAYMENT',
                    }
                    payment_type = payment_type_map.get(message_type.lower().replace('.', '').replace('-', ''), 'TRANSFER')

                    scheme_map = {
                        'pain.001': 'ISO20022', 'pain001': 'ISO20022',
                        'pacs.008': 'ISO20022', 'pacs008': 'ISO20022',
                        'mt103': 'SWIFT_MT', 'fedwire': 'FEDWIRE',
                        'ach': 'ACH', 'rtp': 'RTP', 'sepa': 'SEPA',
                        'bacs': 'BACS', 'chaps': 'CHAPS', 'fps': 'FPS',
                    }
                    scheme_code = scheme_map.get(message_type.lower().replace('.', '').replace('-', ''), 'OTHER')

                    now = datetime.utcnow()

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
                        batch_id, now.year, now.month
                    ))

                    row = cursor.fetchone()
                    if row:
                        result['gold']['instruction_ids'].append(instruction_id)

                        # Persist extension data to format-specific Gold extension table
                        try:
                            extension_id = DynamicGoldMapper.persist_extension_data(
                                cursor, silver_data, message_type, instruction_id
                            )
                            if extension_id:
                                logger.debug(f"[{batch_id}] Persisted extension data: {extension_id}")
                        except Exception as ext_err:
                            # Log but don't fail - extension data is supplementary
                            logger.warning(f"[{batch_id}] Failed to persist extension data for {stg_id}: {ext_err}")

                        # Update Silver status
                        cursor.execute(f"""
                            UPDATE silver.{silver_table}
                            SET processing_status = 'PROMOTED_TO_GOLD',
                                processed_to_gold_at = CURRENT_TIMESTAMP
                            WHERE stg_id = %s
                        """, (stg_id,))

                        # Track record-level lineage in result (for debugging/response)
                        result['lineage'][stg_id] = {
                            'source_table': f'silver.{silver_table}',
                            'target_table': 'gold.cdm_payment_instruction',
                            'source_id': stg_id,
                            'target_id': instruction_id,
                            'transformation': 'NORMALIZE'
                        }

                        # Release the savepoint on success
                        cursor.execute(f"RELEASE SAVEPOINT {savepoint_name}")
                    else:
                        cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                        result['gold']['failed'].append({
                            'stg_id': stg_id,
                            'message_type': message_type,
                            'error': 'Duplicate instruction_id',
                            'error_code': 'DUPLICATE_MESSAGE'
                        })

                except Exception as e:
                    # Rollback to savepoint to allow subsequent records to continue
                    try:
                        cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                    except Exception:
                        pass
                    result['gold']['failed'].append({
                        'stg_id': stg_id,
                        'message_type': message_type,
                        'error': str(e),
                        'error_code': 'GOLD_ERROR'
                    })

        # COMMIT Gold transaction - ensures ACID for Gold zone
        conn.commit()
        gold_end_time = datetime.utcnow()
        logger.info(f"[{batch_id}] Gold complete: {len(result['gold']['instruction_ids'])} succeeded, {len(result['gold']['failed'])} failed")

        # NOTE: PostgreSQL Gold lineage removed - lineage tracked in Neo4j only via update_neo4j_lineage()

        # Update batch tracking with Gold completion
        final_status = 'SUCCESS' if not result['bronze']['failed'] and not result['silver']['failed'] and not result['gold']['failed'] else 'PARTIAL'
        update_batch_tracking_layer(cursor, batch_id, 'gold', len(result['gold']['instruction_ids']), final_status)

        # Finalize batch tracking
        total_duration_ms = int((gold_end_time - start_time).total_seconds() * 1000)
        total_duration_seconds = (gold_end_time - start_time).total_seconds()
        cursor.execute("""
            UPDATE observability.obs_batch_tracking
            SET status = %s,
                completed_at = CURRENT_TIMESTAMP,
                duration_seconds = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE batch_id = %s
        """, (final_status, total_duration_seconds, batch_id))
        conn.commit()

        # Update Neo4j knowledge graph with lineage
        update_neo4j_lineage(
            batch_id=batch_id,
            message_type=primary_message_type,
            bronze_count=len(result['bronze']['raw_ids']),
            silver_count=len(result['silver']['stg_ids']),
            gold_count=len(result['gold']['instruction_ids']),
            duration_ms=total_duration_ms,
            status=final_status,
        )

        # Determine final status
        if not result['bronze']['failed'] and not result['silver']['failed'] and not result['gold']['failed']:
            result['status'] = 'SUCCESS'
        elif result['gold']['instruction_ids']:
            result['status'] = 'PARTIAL'
        else:
            result['status'] = 'FAILED'

        result['duration_seconds'] = (datetime.utcnow() - start_time).total_seconds()

        logger.info(f"[{batch_id}] Medallion pipeline complete: status={result['status']}, "
                   f"Bronze={len(result['bronze']['raw_ids'])}, "
                   f"Silver={len(result['silver']['stg_ids'])}, "
                   f"Gold={len(result['gold']['instruction_ids'])}")

        return result

    except Exception as e:
        import traceback
        logger.exception(f"[{batch_id}] Medallion pipeline failed: {e}")
        if conn:
            conn.rollback()
        result['status'] = 'FAILED'
        result['error'] = str(e)
        result['error_trace'] = traceback.format_exc()
        result['duration_seconds'] = (datetime.utcnow() - start_time).total_seconds()
        return result

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
