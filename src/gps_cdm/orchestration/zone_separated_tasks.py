"""
GPS CDM - Zone-Separated Celery Tasks (New Architecture)
=========================================================

Implements the target architecture where:
1. Bronze stores raw content AS-IS (no JSON wrapping)
2. Silver retrieves by raw_id, parses format-appropriate, extracts fields
3. Gold retrieves by stg_id, transforms to CDM entities

Each task:
- Processes messages for its zone only
- Updates lineage tracking
- Returns IDs for next zone to consume via Kafka
"""

from celery import shared_task
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import uuid
import hashlib
import logging
import os
import re
import traceback

# Import the Celery app from the main celery_tasks module
from gps_cdm.orchestration.celery_tasks import celery_app

logger = logging.getLogger(__name__)


# =============================================================================
# DATABASE CONNECTION
# =============================================================================

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


# =============================================================================
# MAPPING-BASED DYNAMIC SQL
# =============================================================================

class MappingCache:
    """Cache for database mappings to avoid repeated lookups."""
    _silver_mappings: Dict[str, List[Dict]] = {}
    _gold_mappings: Dict[str, Dict[str, List[Dict]]] = {}  # format -> table -> mappings
    _message_formats: Dict[str, Dict] = {}

    @classmethod
    def clear(cls, format_id: str = None) -> None:
        """Clear cached mappings. If format_id is provided, only clear that format."""
        if format_id:
            cls._silver_mappings.pop(format_id, None)
            cls._gold_mappings.pop(format_id, None)
            cls._message_formats.pop(format_id, None)
        else:
            cls._silver_mappings.clear()
            cls._gold_mappings.clear()
            cls._message_formats.clear()

    @classmethod
    def get_silver_mappings(cls, cursor, format_id: str) -> List[Dict]:
        """Get silver field mappings for a format from database."""
        # Check if caching is disabled via environment variable
        disable_cache = os.environ.get('GPS_CDM_DISABLE_MAPPING_CACHE', 'false').lower() == 'true'
        if disable_cache or format_id not in cls._silver_mappings:
            # Use case-insensitive match for format_id (some are lowercase like pain.001)
            cursor.execute("""
                SELECT target_column, source_path, data_type, is_required,
                       default_value, transform_function, transform_expression, max_length
                FROM mapping.silver_field_mappings
                WHERE UPPER(format_id) = UPPER(%s) AND is_active = true
                ORDER BY ordinal_position
            """, (format_id,))

            cls._silver_mappings[format_id] = [
                {
                    'target_column': row[0],
                    'source_path': row[1],
                    'data_type': row[2],
                    'is_required': row[3],
                    'default_value': row[4],
                    'transform_function': row[5],
                    'transform_expression': row[6],
                    'max_length': row[7],
                }
                for row in cursor.fetchall()
            ]
        return cls._silver_mappings[format_id]

    @classmethod
    def get_gold_mappings(cls, cursor, format_id: str, gold_table: str) -> List[Dict]:
        """Get gold field mappings for a format and table from database."""
        cache_key = f"{format_id}:{gold_table}"

        if format_id not in cls._gold_mappings:
            cls._gold_mappings[format_id] = {}

        if gold_table not in cls._gold_mappings[format_id]:
            # Use case-insensitive match for format_id
            cursor.execute("""
                SELECT gold_column, source_expression, entity_role, data_type,
                       is_required, default_value, transform_expression
                FROM mapping.gold_field_mappings
                WHERE UPPER(format_id) = UPPER(%s) AND gold_table = %s AND is_active = true
                ORDER BY ordinal_position
            """, (format_id, gold_table))

            cls._gold_mappings[format_id][gold_table] = [
                {
                    'gold_column': row[0],
                    'source_expression': row[1],
                    'entity_role': row[2],
                    'data_type': row[3],
                    'is_required': row[4],
                    'default_value': row[5],
                    'transform_expression': row[6],
                }
                for row in cursor.fetchall()
            ]
        return cls._gold_mappings[format_id].get(gold_table, [])

    @classmethod
    def get_message_format(cls, cursor, format_id: str) -> Optional[Dict]:
        """Get message format configuration from database."""
        if format_id not in cls._message_formats:
            # Use case-insensitive match for format_id
            cursor.execute("""
                SELECT format_id, format_name, format_category, silver_table
                FROM mapping.message_formats
                WHERE UPPER(format_id) = UPPER(%s) AND is_active = true
            """, (format_id,))

            row = cursor.fetchone()
            if row:
                cls._message_formats[format_id] = {
                    'format_id': row[0],
                    'format_name': row[1],
                    'format_category': row[2],
                    'silver_table': row[3],
                }
            else:
                cls._message_formats[format_id] = None
        return cls._message_formats.get(format_id)

    @classmethod
    def clear_cache(cls):
        """Clear all cached mappings."""
        cls._silver_mappings.clear()
        cls._gold_mappings.clear()
        cls._message_formats.clear()


class DynamicSqlBuilder:
    """Build SQL statements dynamically from database mappings."""

    @staticmethod
    def extract_value_from_path(data: Dict, path: str, default: Any = None) -> Any:
        """
        Extract value from nested dict using dot-notation or slash-notation path.

        Examples:
            data = {'debtor': {'name': 'John', 'address': {'city': 'NYC'}}}
            extract_value_from_path(data, 'debtor.name') -> 'John'
            extract_value_from_path(data, 'debtor/address/city') -> 'NYC'
        """
        if not path or path.startswith('_'):
            return default

        # Support both dot and slash notation
        if '/' in path:
            keys = path.split('/')
        else:
            keys = path.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default

            if value is None:
                return default

        return value if value is not None else default

    @staticmethod
    def build_silver_insert(
        cursor,
        format_id: str,
        silver_table: str,
        parsed_data: Dict,
        raw_id: str,
        batch_id: str,
    ) -> tuple:
        """
        Build Silver INSERT statement dynamically from mappings.

        Returns: (sql, values) tuple for cursor.execute()
        """
        mappings = MappingCache.get_silver_mappings(cursor, format_id)

        if not mappings:
            logger.warning(f"No silver mappings found for {format_id}, using minimal insert")
            return (
                f"""
                INSERT INTO silver.{silver_table} (stg_id, raw_id, _batch_id, processing_status)
                VALUES (%s, %s, %s, 'PENDING')
                RETURNING stg_id
                """,
                (str(uuid.uuid4()), raw_id, batch_id)
            )

        columns = []
        values = []
        placeholders = []

        for mapping in mappings:
            col = mapping['target_column']
            source_path = mapping['source_path']
            default = mapping['default_value']
            max_length = mapping.get('max_length')

            # Handle special generated values
            if source_path == '_GENERATED_UUID':
                value = str(uuid.uuid4())
            elif source_path == '_RAW_ID':
                value = raw_id
            elif source_path == '_BATCH_ID':
                value = batch_id
            else:
                value = DynamicSqlBuilder.extract_value_from_path(parsed_data, source_path, default)

            # Truncate string values to max_length if specified
            if isinstance(value, str) and max_length:
                # Clean up value (remove newlines for single-line fields)
                if max_length <= 35:
                    value = value.replace('\n', ' ').replace('\r', '').strip()
                value = value[:max_length]

            # Handle data type conversions - convert empty strings to NULL for non-string types
            data_type = mapping.get('data_type', '').lower()
            if data_type in ('integer', 'int', 'numeric', 'decimal', 'date', 'timestamp', 'boolean'):
                if value is None or (isinstance(value, str) and not value.strip()):
                    value = None
                elif data_type in ('integer', 'int') and isinstance(value, str):
                    try:
                        value = int(value.strip())
                    except ValueError:
                        value = None
                elif data_type in ('numeric', 'decimal') and isinstance(value, str):
                    try:
                        value = float(value.strip().replace(',', '.'))
                    except ValueError:
                        value = None

            columns.append(col)
            values.append(value)
            placeholders.append('%s')

        # Add processing status column
        if 'processing_status' not in columns:
            columns.append('processing_status')
            values.append('PENDING')
            placeholders.append('%s')

        sql = f"""
            INSERT INTO silver.{silver_table} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING stg_id
        """

        return (sql, tuple(values))

    @staticmethod
    def build_gold_insert(
        cursor,
        format_id: str,
        gold_table: str,
        silver_data: Dict,
        entity_ids: Dict,
        stg_id: str,
        batch_id: str,
        raw_id: str = None,
    ) -> tuple:
        """
        Build Gold INSERT statement dynamically from mappings.

        Returns: (sql, values) tuple for cursor.execute()
        """
        mappings = MappingCache.get_gold_mappings(cursor, format_id, gold_table)

        # Get silver table name for source_stg_table
        format_config = MappingCache.get_message_format(cursor, format_id)
        silver_table = format_config.get('silver_table', f'stg_{format_id.lower()}') if format_config else f'stg_{format_id.lower()}'

        # Start with required NOT NULL columns
        instruction_id = f"instr_{uuid.uuid4().hex[:12]}"
        now_year = datetime.utcnow().year
        now_month = datetime.utcnow().month

        columns = []
        values = []
        placeholders = []

        # Required NOT NULL columns with defaults
        required_columns = {
            'instruction_id': instruction_id,
            'payment_id': silver_data.get('message_id') or instruction_id,  # fallback to instruction_id
            'source_message_type': format_id.upper(),
            'source_stg_table': silver_table,
            'source_stg_id': stg_id,
            'source_raw_id': raw_id or silver_data.get('raw_id'),  # Track lineage back to Bronze
            'payment_type': 'CREDIT_TRANSFER',
            'scheme_code': format_id.upper(),
            'direction': 'OUTBOUND',
            'instructed_currency': silver_data.get('instructed_currency') or silver_data.get('currency') or 'XXX',
            'source_system': 'GPS_CDM',
            'valid_from': None,  # Will use CURRENT_TIMESTAMP
            'is_current': True,
            'partition_year': now_year,
            'partition_month': now_month,
            'region': 'UK',
            'lineage_batch_id': batch_id,
        }

        for col, val in required_columns.items():
            columns.append(col)
            if col == 'valid_from':
                placeholders.append('CURRENT_TIMESTAMP')
            else:
                values.append(val)
                placeholders.append('%s')

        # Add created_at and updated_at
        columns.extend(['created_at', 'updated_at'])
        placeholders.extend(['CURRENT_TIMESTAMP', 'CURRENT_TIMESTAMP'])

        # Add entity reference columns
        entity_columns = [
            ('debtor_id', 'debtor_id'),
            ('debtor_account_id', 'debtor_account_id'),
            ('debtor_agent_id', 'debtor_agent_id'),
            ('creditor_id', 'creditor_id'),
            ('creditor_account_id', 'creditor_account_id'),
            ('creditor_agent_id', 'creditor_agent_id'),
            ('intermediary_agent1_id', 'intermediary_agent1_id'),
            ('intermediary_agent2_id', 'intermediary_agent2_id'),
            ('ultimate_debtor_id', 'ultimate_debtor_id'),
            ('ultimate_creditor_id', 'ultimate_creditor_id'),
        ]

        for col, entity_key in entity_columns:
            if col not in columns:
                columns.append(col)
                values.append(entity_ids.get(entity_key))
                placeholders.append('%s')

        # Add mapped columns from database
        for mapping in mappings:
            col = mapping['gold_column']
            source_expr = mapping['source_expression']
            default = mapping['default_value']
            transform = mapping.get('transform_expression')

            if col in columns:
                continue  # Skip if already added

            # Get value from silver data
            value = silver_data.get(source_expr) or default

            # Apply transformation if specified
            if transform and value:
                if transform == 'ARRAY[value]':
                    # Wrap value in array for array columns
                    value = [value] if value else None
                # Additional transforms can be added here

            # Convert boolean string to actual boolean
            data_type = mapping.get('data_type', '').lower()
            if data_type == 'boolean' and isinstance(value, str):
                value = value.lower() in ('true', '1', 'yes', 't')

            columns.append(col)
            values.append(value)
            placeholders.append('%s')

        # Ensure current_status is set
        if 'current_status' not in columns:
            columns.append('current_status')
            values.append('PENDING')
            placeholders.append('%s')

        sql = f"""
            INSERT INTO gold.{gold_table} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            ON CONFLICT (instruction_id) DO NOTHING
            RETURNING instruction_id
        """

        return (sql, tuple(values), instruction_id)


# =============================================================================
# FORMAT DETECTION AND PARSING
# =============================================================================

class FormatDetector:
    """Detect message format from content."""

    @staticmethod
    def detect(content: str) -> str:
        """
        Detect format from content (not filename).

        Returns: SWIFT_MT, XML, JSON, FIXED, TAG_VALUE, RAW
        """
        content = content.strip()

        # SWIFT MT block format
        if content.startswith('{1:') or content.startswith('{2:'):
            return 'SWIFT_MT'

        # XML
        if content.startswith('<?xml') or content.startswith('<Document') or content.startswith('<'):
            return 'XML'

        # JSON
        if (content.startswith('{') or content.startswith('[')) and not re.match(r'\{\d:', content):
            try:
                json.loads(content)
                return 'JSON'
            except json.JSONDecodeError:
                pass

        # NACHA/ACH fixed-width (check for file header starting with '1' and batch headers starting with '5')
        lines = content.split('\n')
        if lines and len(lines) > 0:
            first_line = lines[0].strip()
            # ACH File Header starts with record type '1' and priority code '01'
            if first_line.startswith('101') or first_line.startswith('1 0'):
                # Check if there's also a batch header (record type '5')
                has_batch_header = any(line.strip().startswith('5') for line in lines[:10])
                if has_batch_header:
                    return 'FIXED'
            # Also check for all 94-char lines
            if all(len(line.rstrip()) == 94 or len(line.rstrip()) == 0 for line in lines[:5] if line.strip()):
                return 'FIXED'

        # FEDWIRE tag-value
        if re.search(r'\{\d{4}\}', content):
            return 'TAG_VALUE'

        return 'RAW'


class ContentParser:
    """Parse content based on format."""

    @staticmethod
    def parse(content: str, message_format: str, message_type: str) -> Dict[str, Any]:
        """
        Parse content to structured dict based on format.

        Args:
            content: Raw content string
            message_format: Detected format (SWIFT_MT, XML, JSON, etc.)
            message_type: Message type for parser selection

        Returns:
            Parsed content as dict with extracted fields
        """
        if message_format == 'SWIFT_MT':
            return ContentParser._parse_swift_mt(content, message_type)

        elif message_format == 'XML':
            return ContentParser._parse_xml(content, message_type)

        elif message_format == 'JSON':
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {'_raw_text': content, '_format': 'json_invalid'}

        elif message_format == 'FIXED':
            return ContentParser._parse_fixed_width(content, message_type)

        elif message_format == 'TAG_VALUE':
            return ContentParser._parse_tag_value(content)

        else:
            return {'_raw_text': content, '_format': 'raw'}

    @staticmethod
    def _parse_swift_mt(content: str, message_type: str = None) -> Dict[str, Any]:
        """Parse SWIFT MT block format using message-type-specific parser if available."""
        # Try to use message-type-specific parser first
        if message_type:
            from gps_cdm.message_formats.base import ExtractorRegistry
            extractor = ExtractorRegistry.get(message_type)
            if extractor and hasattr(extractor, 'parser') and hasattr(extractor.parser, 'parse'):
                try:
                    return extractor.parser.parse(content)
                except Exception as e:
                    logger.warning(f"SWIFT MT parser failed for {message_type}: {e}")

        # Fallback to ChapsSwiftParser (generic SWIFT MT parser)
        from gps_cdm.message_formats.chaps import ChapsSwiftParser
        parser = ChapsSwiftParser()
        return parser.parse(content)

    @staticmethod
    def _parse_xml(content: str, message_type: str) -> Dict[str, Any]:
        """Parse XML format using appropriate parser."""
        # Get extractor for message type
        from gps_cdm.message_formats.base import ExtractorRegistry
        extractor = ExtractorRegistry.get(message_type)

        if extractor and hasattr(extractor, 'parser') and hasattr(extractor.parser, 'parse'):
            try:
                return extractor.parser.parse(content)
            except Exception as e:
                logger.warning(f"XML parser failed for {message_type}: {e}")

        # Fallback: basic XML parsing
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(content)
            return ContentParser._xml_to_dict(root)
        except Exception as e:
            logger.warning(f"Fallback XML parsing failed: {e}")
            return {'_raw_text': content, '_format': 'xml'}

    @staticmethod
    def _xml_to_dict(element) -> Dict[str, Any]:
        """Convert XML element to dict (basic)."""
        result = {}
        for child in element:
            tag = child.tag.split('}')[-1]  # Remove namespace
            if len(child):
                result[tag] = ContentParser._xml_to_dict(child)
            else:
                result[tag] = child.text
        return result

    @staticmethod
    def _parse_fixed_width(content: str, message_type: str) -> Dict[str, Any]:
        """Parse fixed-width format (ACH/NACHA)."""
        from gps_cdm.message_formats.base import ExtractorRegistry
        extractor = ExtractorRegistry.get(message_type)

        if extractor and hasattr(extractor, 'parser') and hasattr(extractor.parser, 'parse'):
            try:
                return extractor.parser.parse(content)
            except Exception as e:
                logger.warning(f"Fixed-width parser failed: {e}")

        return {'_raw_text': content, '_format': 'fixed'}

    @staticmethod
    def _parse_tag_value(content: str) -> Dict[str, Any]:
        """Parse FEDWIRE tag-value format."""
        from gps_cdm.message_formats.base import ExtractorRegistry
        extractor = ExtractorRegistry.get('FEDWIRE')

        if extractor and hasattr(extractor, 'parser') and hasattr(extractor.parser, 'parse'):
            try:
                return extractor.parser.parse(content)
            except Exception as e:
                logger.warning(f"Tag-value parser failed: {e}")

        return {'_raw_text': content, '_format': 'tag_value'}


# =============================================================================
# OBSERVABILITY HELPERS
# =============================================================================

def ensure_batch_tracking(cursor, batch_id: str, message_type: str) -> None:
    """Ensure batch tracking record exists."""
    cursor.execute("""
        INSERT INTO observability.obs_batch_tracking (
            batch_id, message_type, source_system, status, current_layer,
            started_at, created_at, updated_at
        ) VALUES (%s, %s, 'KAFKA', 'PROCESSING', 'bronze',
                  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (batch_id) DO UPDATE SET
            updated_at = CURRENT_TIMESTAMP
    """, (batch_id, message_type))


def update_batch_layer(cursor, batch_id: str, layer: str, count: int, status: str = 'PROCESSING') -> None:
    """Update batch tracking for layer completion."""
    cursor.execute(f"""
        UPDATE observability.obs_batch_tracking
        SET current_layer = %s,
            {layer}_records = %s,
            {layer}_completed_at = CURRENT_TIMESTAMP,
            status = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE batch_id = %s
    """, (layer, count, status, batch_id))


def track_message(
    cursor,
    batch_id: str,
    message_id: str,
    message_type: str,
    zone: str,
    status: str,
    bronze_raw_id: Optional[str] = None,
    silver_stg_id: Optional[str] = None,
    gold_instr_id: Optional[str] = None,
    error_message: Optional[str] = None,
) -> None:
    """Track individual message progress through zones."""
    cursor.execute("""
        INSERT INTO observability.obs_message_tracking (
            tracking_id, batch_id, message_id, message_type, current_zone,
            bronze_raw_id, silver_stg_id, gold_instr_id, status, error_message,
            created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (tracking_id) DO UPDATE SET
            current_zone = EXCLUDED.current_zone,
            bronze_raw_id = COALESCE(EXCLUDED.bronze_raw_id, observability.obs_message_tracking.bronze_raw_id),
            silver_stg_id = COALESCE(EXCLUDED.silver_stg_id, observability.obs_message_tracking.silver_stg_id),
            gold_instr_id = COALESCE(EXCLUDED.gold_instr_id, observability.obs_message_tracking.gold_instr_id),
            status = EXCLUDED.status,
            error_message = EXCLUDED.error_message,
            updated_at = CURRENT_TIMESTAMP
    """, (
        f"trk_{uuid.uuid4().hex[:12]}",
        batch_id, message_id, message_type, zone,
        bronze_raw_id, silver_stg_id, gold_instr_id,
        status, error_message
    ))


def record_lineage(
    cursor,
    batch_id: str,
    source_zone: str,
    source_table: str,
    source_id: str,
    target_zone: str,
    target_table: str,
    target_id: str,
    transformation: str = 'NORMALIZE',
    field_mappings: Optional[Dict] = None,
) -> None:
    """Record data lineage between zones."""
    cursor.execute("""
        INSERT INTO observability.obs_data_lineage (
            lineage_id, batch_id,
            source_layer, source_table, source_zone, source_id,
            target_layer, target_table, target_zone, target_id,
            transformation, field_mappings, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
    """, (
        f"lin_{uuid.uuid4().hex[:12]}",
        batch_id,
        source_zone, source_table, source_zone, source_id,  # source_layer = source_zone
        target_zone, target_table, target_zone, target_id,  # target_layer = target_zone
        transformation,
        json.dumps(field_mappings) if field_mappings else None
    ))


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
) -> str:
    """Publish error to processing_errors table."""
    error_id = f"err_{uuid.uuid4().hex[:12]}"

    cursor.execute("""
        INSERT INTO bronze.processing_errors (
            error_id, batch_id, zone, raw_id, stg_id,
            message_type, error_code, error_message,
            original_content, status, retry_count,
            max_retries, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,
                  'PENDING', 0, 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (
        error_id, batch_id, zone, raw_id, stg_id,
        message_type, error_code, error_message, original_content
    ))

    return error_id


# =============================================================================
# BRONZE ZONE TASK
# =============================================================================

@shared_task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    queue='bronze',
    name='gps_cdm.zone_tasks.process_bronze_message'
)
def process_bronze_message(
    self,
    batch_id: str,
    records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Store raw messages in Bronze layer AS-IS.

    This task:
    1. Stores raw content exactly as received (NO JSON wrapping)
    2. Computes content hash for deduplication
    3. Returns raw_ids for Silver consumer to process

    Args:
        batch_id: Batch identifier
        records: List of {content: str, message_type: str, message_format: str, metadata: dict}

    Returns:
        {
            status: 'SUCCESS' | 'PARTIAL' | 'FAILED',
            batch_id: str,
            raw_ids: [str],
            failed: [{index: int, error: str}],
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

        # Ensure batch tracking
        message_type = records[0].get('message_type', 'UNKNOWN') if records else 'UNKNOWN'
        ensure_batch_tracking(cursor, batch_id, message_type)

        for idx, record in enumerate(records):
            try:
                content = record['content']  # Raw content AS-IS
                msg_type = record.get('message_type', 'UNKNOWN')
                msg_format = record.get('message_format') or FormatDetector.detect(content)
                metadata = record.get('metadata', {})

                # Generate raw_id
                raw_id = f"raw_{uuid.uuid4().hex[:12]}"

                # Compute content hash
                content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:64]

                # Insert into Bronze - store content AS-IS
                cursor.execute("""
                    INSERT INTO bronze.raw_payment_messages (
                        raw_id, message_type, message_format, raw_content,
                        raw_content_hash, source_system, source_channel,
                        source_batch_id, processing_status, _batch_id, _ingested_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (raw_id) DO NOTHING
                    RETURNING raw_id
                """, (
                    raw_id, msg_type, msg_format, content,  # content AS-IS
                    content_hash, 'KAFKA', 'NIFI',
                    batch_id, 'PENDING', batch_id
                ))

                result = cursor.fetchone()
                if result:
                    raw_ids.append(raw_id)

                    # Track message
                    track_message(
                        cursor, batch_id, raw_id, msg_type, 'BRONZE',
                        'SUCCESS', bronze_raw_id=raw_id
                    )

                else:
                    failed.append({
                        'index': idx,
                        'message_type': msg_type,
                        'error': 'Duplicate content hash',
                        'error_code': 'DUPLICATE_MESSAGE'
                    })

            except Exception as e:
                error_trace = traceback.format_exc()
                logger.error(f"Bronze processing error: {e}\n{error_trace}")

                publish_error(
                    cursor, batch_id, 'BRONZE',
                    record.get('message_type', 'UNKNOWN'),
                    str(e), 'PROCESSING_ERROR',
                    original_content=record.get('content', '')[:10000]
                )

                failed.append({
                    'index': idx,
                    'message_type': record.get('message_type', 'UNKNOWN'),
                    'error': str(e),
                    'error_code': 'PROCESSING_ERROR'
                })

        # Update batch tracking
        update_batch_layer(cursor, batch_id, 'bronze', len(raw_ids))

        conn.commit()

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Bronze batch error: {e}")
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    duration = (datetime.utcnow() - start_time).total_seconds()

    status = 'SUCCESS' if not failed else ('PARTIAL' if raw_ids else 'FAILED')

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

@shared_task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    queue='silver',
    name='gps_cdm.zone_tasks.process_silver_message'
)
def process_silver_message(
    self,
    batch_id: str,
    raw_ids: List[str],
    message_type: str,
) -> Dict[str, Any]:
    """
    Process Bronze records into Silver layer.

    This task:
    1. Retrieves raw content from Bronze by raw_id
    2. Parses content using format-appropriate parser
    3. Extracts fields using database mappings
    4. Stores in Silver staging table
    5. Returns stg_ids for Gold consumer to process

    Args:
        batch_id: Batch identifier
        raw_ids: List of raw_ids from Bronze
        message_type: Message type for parser/extractor selection

    Returns:
        {
            status: 'SUCCESS' | 'PARTIAL' | 'FAILED',
            batch_id: str,
            stg_ids: [str],
            failed: [{raw_id: str, error: str}],
            duration_seconds: float
        }
    """
    start_time = datetime.utcnow()
    stg_ids = []
    failed = []

    # Get extractor
    from gps_cdm.message_formats.base import ExtractorRegistry
    extractor = ExtractorRegistry.get(message_type)

    if not extractor:
        logger.error(f"No extractor for message type: {message_type}")
        return {
            'status': 'FAILED',
            'batch_id': batch_id,
            'stg_ids': [],
            'failed': [{'raw_id': rid, 'error': f'No extractor for {message_type}'} for rid in raw_ids],
            'duration_seconds': 0,
        }

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Read Bronze records - use extractor_output which is already parsed
        placeholders = ','.join(['%s'] * len(raw_ids))
        cursor.execute(f"""
            SELECT raw_id, message_type, message_format, raw_content, extractor_output
            FROM bronze.raw_payment_messages
            WHERE raw_id IN ({placeholders})
              AND processing_status = 'PENDING'
        """, tuple(raw_ids))

        bronze_records = cursor.fetchall()

        for raw_id, msg_type, msg_format, raw_content, extractor_output in bronze_records:
            try:
                # Use extractor_output from Bronze if available (already parsed by extractor)
                # Fall back to ContentParser if extractor_output is None
                if extractor_output:
                    parsed_content = extractor_output
                else:
                    # Fallback: parse raw_content if extractor_output is missing
                    parsed_content = ContentParser.parse(raw_content, msg_format, msg_type)

                logger.info(f"Parsed {msg_format} for {raw_id}: keys={list(parsed_content.keys())[:5]}")

                # Get silver table from message_formats mapping or fallback to extractor
                format_config = MappingCache.get_message_format(cursor, msg_type)
                if format_config and format_config.get('silver_table'):
                    silver_table = format_config['silver_table']
                else:
                    silver_table = extractor.SILVER_TABLE

                # Build Silver INSERT using database mappings
                sql, values = DynamicSqlBuilder.build_silver_insert(
                    cursor=cursor,
                    format_id=msg_type,
                    silver_table=silver_table,
                    parsed_data=parsed_content,
                    raw_id=raw_id,
                    batch_id=batch_id,
                )

                cursor.execute(sql, values)

                result = cursor.fetchone()
                if result:
                    stg_id = result[0]  # Get stg_id from RETURNING clause
                    stg_ids.append(stg_id)

                    # Update Bronze status
                    cursor.execute("""
                        UPDATE bronze.raw_payment_messages
                        SET processing_status = 'PROMOTED_TO_SILVER',
                            processed_to_silver_at = CURRENT_TIMESTAMP
                        WHERE raw_id = %s
                    """, (raw_id,))

                    # Record lineage
                    record_lineage(
                        cursor, batch_id,
                        'bronze', 'raw_payment_messages', raw_id,
                        'silver', silver_table, stg_id,
                        'PARSE_AND_EXTRACT'
                    )

                    # Track message
                    track_message(
                        cursor, batch_id, raw_id, msg_type, 'SILVER',
                        'SUCCESS', bronze_raw_id=raw_id, silver_stg_id=stg_id
                    )

                else:
                    failed.append({
                        'raw_id': raw_id,
                        'error': 'Duplicate stg_id',
                        'error_code': 'DUPLICATE_MESSAGE'
                    })

            except Exception as e:
                error_trace = traceback.format_exc()
                logger.error(f"Silver processing error for {raw_id}: {e}")

                publish_error(
                    cursor, batch_id, 'SILVER', message_type,
                    str(e), 'EXTRACTION_ERROR', raw_id=raw_id
                )

                failed.append({
                    'raw_id': raw_id,
                    'error': str(e),
                    'error_code': 'EXTRACTION_ERROR'
                })

        # Update batch tracking
        update_batch_layer(cursor, batch_id, 'silver', len(stg_ids))

        conn.commit()

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Silver batch error: {e}")
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    duration = (datetime.utcnow() - start_time).total_seconds()

    status = 'SUCCESS' if not failed else ('PARTIAL' if stg_ids else 'FAILED')

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

@shared_task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    queue='gold',
    name='gps_cdm.zone_tasks.process_gold_message'
)
def process_gold_message(
    self,
    batch_id: str,
    stg_ids: List[str],
    message_type: str,
) -> Dict[str, Any]:
    """
    Process Silver records into Gold CDM layer.

    This task:
    1. Retrieves parsed data from Silver by stg_id
    2. Transforms to CDM specifications using gold mappings
    3. Extracts entities: Party, Account, FinancialInstitution
    4. Stores in Gold tables
    5. Updates Neo4j lineage graph

    Args:
        batch_id: Batch identifier
        stg_ids: List of stg_ids from Silver
        message_type: Message type for entity extraction

    Returns:
        {
            status: 'SUCCESS' | 'PARTIAL' | 'FAILED',
            batch_id: str,
            instruction_ids: [str],
            entities: {parties: [], accounts: [], fis: []},
            failed: [{stg_id: str, error: str}],
            duration_seconds: float
        }
    """
    start_time = datetime.utcnow()
    instruction_ids = []
    all_parties = []
    all_accounts = []
    all_fis = []
    failed = []

    # Get extractor
    from gps_cdm.message_formats.base import ExtractorRegistry, GoldEntityPersister
    extractor = ExtractorRegistry.get(message_type)

    if not extractor:
        logger.error(f"No extractor for message type: {message_type}")
        return {
            'status': 'FAILED',
            'batch_id': batch_id,
            'instruction_ids': [],
            'entities': {'parties': [], 'accounts': [], 'fis': []},
            'failed': [{'stg_id': sid, 'error': f'No extractor for {message_type}'} for sid in stg_ids],
            'duration_seconds': 0,
        }

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get Silver table name from message_formats mapping or fallback to extractor
        format_config = MappingCache.get_message_format(cursor, message_type)
        if format_config and format_config.get('silver_table'):
            silver_table = format_config['silver_table']
        else:
            silver_table = extractor.SILVER_TABLE

        # Read Silver records - get all columns dynamically
        cursor.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'silver' AND table_name = %s
            ORDER BY ordinal_position
        """, (silver_table,))
        columns = [row[0] for row in cursor.fetchall()]
        col_str = ', '.join(columns)

        placeholders = ','.join(['%s'] * len(stg_ids))
        cursor.execute(f"""
            SELECT {col_str}
            FROM silver.{silver_table}
            WHERE stg_id IN ({placeholders})
              AND processing_status = 'PENDING'
        """, tuple(stg_ids))

        silver_records = cursor.fetchall()

        for row in silver_records:
            # Convert row to dict
            silver_data = dict(zip(columns, row))
            stg_id = silver_data['stg_id']
            raw_id = silver_data.get('raw_id')

            try:
                # Extract Gold entities using extractor
                gold_entities = extractor.extract_gold_entities(silver_data, stg_id, batch_id)

                # Persist entities (parties, accounts, FIs) using classmethod
                entity_ids = GoldEntityPersister.persist_all_entities(
                    cursor=cursor,
                    entities=gold_entities,
                    message_type=message_type,
                    stg_id=stg_id,
                )

                # Build Gold INSERT dynamically using database mappings
                sql, values, instruction_id = DynamicSqlBuilder.build_gold_insert(
                    cursor=cursor,
                    format_id=message_type,
                    gold_table='cdm_payment_instruction',
                    silver_data=silver_data,
                    entity_ids=entity_ids,
                    stg_id=stg_id,
                    batch_id=batch_id,
                    raw_id=raw_id,
                )

                cursor.execute(sql, values)

                result = cursor.fetchone()
                if result:
                    instruction_ids.append(instruction_id)

                    # Persist extension data if applicable
                    GoldEntityPersister.persist_extension(
                        cursor=cursor,
                        instruction_id=instruction_id,
                        message_type=message_type,
                        staging_record=silver_data,
                    )

                    # Collect entity IDs for response
                    all_parties.extend([v for k, v in entity_ids.items() if 'id' in k and v and 'party' not in k and 'account' not in k and 'agent' not in k])
                    if entity_ids.get('debtor_id'):
                        all_parties.append(entity_ids['debtor_id'])
                    if entity_ids.get('creditor_id'):
                        all_parties.append(entity_ids['creditor_id'])
                    if entity_ids.get('debtor_account_id'):
                        all_accounts.append(entity_ids['debtor_account_id'])
                    if entity_ids.get('creditor_account_id'):
                        all_accounts.append(entity_ids['creditor_account_id'])
                    if entity_ids.get('debtor_agent_id'):
                        all_fis.append(entity_ids['debtor_agent_id'])
                    if entity_ids.get('creditor_agent_id'):
                        all_fis.append(entity_ids['creditor_agent_id'])

                    # Update Silver status
                    cursor.execute(f"""
                        UPDATE silver.{silver_table}
                        SET processing_status = 'PROMOTED_TO_GOLD',
                            processed_to_gold_at = CURRENT_TIMESTAMP
                        WHERE stg_id = %s
                    """, (stg_id,))

                    # Record lineage
                    record_lineage(
                        cursor, batch_id,
                        'silver', silver_table, stg_id,
                        'gold', 'cdm_payment_instruction', instruction_id,
                        'NORMALIZE_TO_CDM'
                    )

                    # Track message
                    track_message(
                        cursor, batch_id, stg_id, message_type, 'GOLD',
                        'SUCCESS', bronze_raw_id=raw_id, silver_stg_id=stg_id,
                        gold_instr_id=instruction_id
                    )

                else:
                    failed.append({
                        'stg_id': stg_id,
                        'error': 'Failed to persist Gold entities',
                        'error_code': 'PERSIST_ERROR'
                    })

            except Exception as e:
                error_trace = traceback.format_exc()
                logger.error(f"Gold processing error for {stg_id}: {e}")

                publish_error(
                    cursor, batch_id, 'GOLD', message_type,
                    str(e), 'GOLD_ERROR', stg_id=stg_id
                )

                failed.append({
                    'stg_id': stg_id,
                    'error': str(e),
                    'error_code': 'GOLD_ERROR'
                })

        # Update batch tracking
        update_batch_layer(cursor, batch_id, 'gold', len(instruction_ids),
                          'COMPLETED' if not failed else 'PARTIAL')

        conn.commit()

        # Update Neo4j lineage
        try:
            from gps_cdm.orchestration.neo4j_service import get_neo4j_service
            neo4j = get_neo4j_service()

            if neo4j.is_available():
                now = datetime.utcnow()
                duration_ms = int((now - start_time).total_seconds() * 1000)

                neo4j.upsert_batch({
                    'batch_id': batch_id,
                    'message_type': message_type,
                    'status': 'SUCCESS' if not failed else 'PARTIAL',
                    'total_records': len(stg_ids),
                    'duration_ms': duration_ms,
                })

                # Update layer stats
                neo4j.upsert_batch_layer(batch_id, 'gold', {
                    'input_count': len(stg_ids),
                    'processed_count': len(instruction_ids),
                    'failed_count': len(failed),
                })

        except Exception as e:
            logger.warning(f"Neo4j lineage update failed: {e}")

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Gold batch error: {e}")
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    duration = (datetime.utcnow() - start_time).total_seconds()

    status = 'SUCCESS' if not failed else ('PARTIAL' if instruction_ids else 'FAILED')

    return {
        'status': status,
        'batch_id': batch_id,
        'instruction_ids': instruction_ids,
        'entities': {
            'parties': all_parties,
            'accounts': all_accounts,
            'fis': all_fis,
        },
        'failed': failed,
        'records_processed': len(instruction_ids),
        'duration_seconds': duration,
    }
