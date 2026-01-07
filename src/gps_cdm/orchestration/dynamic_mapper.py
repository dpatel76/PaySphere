"""
GPS CDM - Dynamic Field Mapper
==============================

Generates dynamic INSERT statements based on database-driven field mappings.
Supports batch inserts for high-throughput processing.

Usage:
    mapper = DynamicMapper(conn)
    records = mapper.prepare_silver_batch('pain.001', raw_records, batch_id)
    mapper.batch_insert_silver(records)
"""

import json
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from functools import lru_cache

logger = logging.getLogger(__name__)


class DynamicMapper:
    """Generates dynamic SQL statements from database-driven mappings."""

    def __init__(self, connection):
        """Initialize with a database connection."""
        self.conn = connection
        self._mapping_cache: Dict[str, List[Dict]] = {}
        self._format_cache: Dict[str, Dict] = {}

    def _get_format_info(self, format_id: str) -> Dict[str, Any]:
        """Get message format metadata from database (case-insensitive lookup)."""
        # Normalize to uppercase for cache key and database lookup
        format_id_upper = format_id.upper()
        if format_id_upper not in self._format_cache:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT format_id, format_name, format_category, silver_table, is_active
                FROM mapping.message_formats
                WHERE UPPER(format_id) = %s AND is_active = TRUE
            """, (format_id_upper,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Unknown or inactive format_id: {format_id}")
            self._format_cache[format_id_upper] = {
                'format_id': row[0],
                'format_name': row[1],
                'format_category': row[2],
                'silver_table': row[3],
                'is_active': row[4]
            }
        return self._format_cache[format_id_upper]

    def _get_silver_mappings(self, format_id: str) -> List[Dict[str, Any]]:
        """Get Silver field mappings from database (case-insensitive lookup).

        Returns mappings with both source_path (XPath for documentation) and
        parser_path (dot-notation for extraction). If parser_path is not set,
        falls back to source_path.
        """
        format_id_upper = format_id.upper()
        if format_id_upper not in self._mapping_cache:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT target_column, source_path, data_type, max_length,
                       is_required, default_value, transform_function, ordinal_position,
                       parser_path
                FROM mapping.silver_field_mappings
                WHERE UPPER(format_id) = %s AND is_active = TRUE
                ORDER BY ordinal_position
            """, (format_id_upper,))
            rows = cursor.fetchall()
            self._mapping_cache[format_id_upper] = [
                {
                    'target_column': row[0],
                    'source_path': row[1],  # XPath for documentation/lineage
                    'data_type': row[2],
                    'max_length': row[3],
                    'is_required': row[4],
                    'default_value': row[5],
                    'transform_function': row[6],
                    'ordinal_position': row[7],
                    'parser_path': row[8]  # Dot-notation for extraction
                }
                for row in rows
            ]
        return self._mapping_cache[format_id_upper]

    def _resolve_path(self, data: Dict[str, Any], path: str) -> Any:
        """
        Resolve a path to a value, trying multiple path formats.

        Supports:
        - Nested paths: debtor.name -> data['debtor']['name']
        - Flat camelCase: debtorName -> data['debtorName']
        - Flat snake_case: debtor_name -> data['debtor_name']
        - Direct key: name -> data['name']

        Examples:
            'debtor.name' -> tries data['debtor']['name'], data['debtorName'],
                            data['debtor_name'], data['name']
        """
        if not path or not data:
            return None

        # Handle special paths
        if path.startswith('_'):
            return None  # Will be handled separately

        # 1. Try original nested path
        value = self._get_nested(data, path)
        if value is not None:
            return value

        # 2. Try flattened camelCase version
        # debtor.name -> debtorName
        parts = path.split('.')
        if len(parts) > 1:
            camel = parts[0] + ''.join(p.capitalize() for p in parts[1:])
            if camel in data:
                return data[camel]

        # 3. Try flattened snake_case version
        # debtor.name -> debtor_name
        snake = path.replace('.', '_')
        if snake in data:
            return data[snake]

        # 4. Try direct key (last part of path)
        if '.' in path:
            last_part = path.split('.')[-1]
            if last_part in data:
                return data[last_part]

        # 5. Try original path as direct key (for paths without dots)
        if path in data:
            return data[path]

        return None

    def _get_nested(self, data: Dict[str, Any], path: str) -> Any:
        """Get value from nested dict using dot notation."""
        if not path or not data:
            return None
        keys = path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
            if value is None:
                return None
        return value

    def _truncate(self, value: Any, max_length: Optional[int]) -> Any:
        """Truncate string value to max length if specified."""
        if value is None or max_length is None:
            return value
        if isinstance(value, str) and len(value) > max_length:
            return value[:max_length]
        return value

    def _transform_value(
        self,
        value: Any,
        data_type: str,
        max_length: Optional[int],
        transform_function: Optional[str]
    ) -> Any:
        """Apply type conversion and transformation to a value."""
        if value is None:
            return None

        # Apply transform function if specified
        if transform_function:
            if transform_function == 'TO_UPPER':
                value = str(value).upper() if value else None
            elif transform_function == 'TO_LOWER':
                value = str(value).lower() if value else None
            elif transform_function == 'TRIM':
                value = str(value).strip() if value else None
            elif transform_function == 'JSON_DUMPS':
                value = json.dumps(value) if value else None

        # Type conversions
        if data_type == 'JSONB':
            if isinstance(value, (dict, list)):
                return json.dumps(value)
            return value
        elif data_type == 'INTEGER':
            try:
                return int(value) if value is not None else None
            except (ValueError, TypeError):
                return None
        elif data_type == 'DECIMAL':
            try:
                return float(value) if value is not None else None
            except (ValueError, TypeError):
                return None
        elif data_type == 'BOOLEAN':
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes')
            return bool(value)
        elif data_type == 'TIMESTAMP':
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                # Try common formats
                for fmt in ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
            return value
        elif data_type == 'DATE':
            if isinstance(value, str):
                try:
                    return datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    pass
            return value
        elif data_type == 'ARRAY':
            # Convert Python list to PostgreSQL array literal {val1,val2}
            if isinstance(value, list):
                # Escape any commas or braces in values
                escaped = []
                for v in value:
                    s = str(v) if v is not None else ''
                    # Quote if contains comma, brace, or whitespace
                    if ',' in s or '{' in s or '}' in s or ' ' in s or '"' in s:
                        s = '"' + s.replace('"', '\\"') + '"'
                    escaped.append(s)
                return '{' + ','.join(escaped) + '}'
            elif value is not None:
                # Single value - wrap in array
                return '{' + str(value) + '}'
            return None
        else:  # VARCHAR
            return self._truncate(str(value), max_length) if value is not None else None

    def extract_silver_record(
        self,
        format_id: str,
        raw_content: Dict[str, Any],
        raw_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        """
        Extract a Silver record from raw content using database mappings.

        Args:
            format_id: Message format identifier (e.g., 'pain.001')
            raw_content: Raw JSON content from Bronze
            raw_id: Reference to Bronze record
            batch_id: Current batch identifier

        Returns:
            Dictionary of column -> value mappings for Silver table
        """
        mappings = self._get_silver_mappings(format_id)
        record = {}

        for mapping in mappings:
            col = mapping['target_column']
            # Use parser_path if available, otherwise fall back to source_path
            # parser_path: dot-notation matching parser output (e.g., debtor.name)
            # source_path: XPath for documentation (e.g., CstmrCdtTrfInitn/PmtInf/Dbtr/Nm)
            path = mapping.get('parser_path') or mapping['source_path']
            data_type = mapping['data_type']
            max_length = mapping['max_length']
            transform = mapping['transform_function']
            default = mapping['default_value']

            # Handle special paths
            if path == '_GENERATED_UUID':
                value = str(uuid.uuid4())
            elif path == '_RAW_ID':
                value = raw_id
            elif path == '_BATCH_ID':
                value = batch_id
            elif path == '_TIMESTAMP':
                value = datetime.utcnow()
            else:
                # Resolve from raw content using parser_path (dot-notation)
                value = self._resolve_path(raw_content, path)

            # Apply default if value is None
            if value is None and default is not None:
                value = default

            # Transform and type-convert
            value = self._transform_value(value, data_type, max_length, transform)

            record[col] = value

        return record

    def prepare_silver_batch(
        self,
        format_id: str,
        bronze_records: List[Tuple[str, Dict[str, Any]]],
        batch_id: str
    ) -> List[Dict[str, Any]]:
        """
        Prepare a batch of Silver records from Bronze records.

        Args:
            format_id: Message format identifier
            bronze_records: List of (raw_id, raw_content) tuples
            batch_id: Current batch identifier

        Returns:
            List of Silver record dictionaries
        """
        return [
            self.extract_silver_record(format_id, content, raw_id, batch_id)
            for raw_id, content in bronze_records
        ]

    def batch_insert_silver(
        self,
        format_id: str,
        records: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> List[str]:
        """
        Batch insert Silver records using executemany for efficiency.

        Args:
            format_id: Message format identifier
            records: List of Silver record dictionaries
            batch_size: Number of records per batch

        Returns:
            List of inserted stg_ids
        """
        if not records:
            return []

        format_info = self._get_format_info(format_id)
        mappings = self._get_silver_mappings(format_id)
        silver_table = format_info['silver_table']

        # Build column list from mappings
        columns = [m['target_column'] for m in mappings]
        col_names = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))

        insert_sql = f"""
            INSERT INTO silver.{silver_table} ({col_names})
            VALUES ({placeholders})
            ON CONFLICT (stg_id) DO NOTHING
            RETURNING stg_id
        """

        cursor = self.conn.cursor()
        inserted_ids = []

        # Process in batches
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]

            for record in batch:
                values = tuple(record.get(col) for col in columns)
                cursor.execute(insert_sql, values)
                result = cursor.fetchone()
                if result:
                    inserted_ids.append(result[0])

        return inserted_ids

    def get_silver_columns(self, format_id: str) -> List[str]:
        """Get ordered list of Silver column names for a format.

        Always includes essential tracking columns (stg_id, raw_id)
        that are not part of the field mappings but are required for
        Gold processing and lineage tracking.

        Note: batch_id is stored as _batch_id in Silver tables but is typically
        not needed for Gold mapping (source_stg_id is used instead).
        """
        # Essential columns that should always be included
        # Note: _batch_id has underscore prefix in Silver tables
        essential_columns = ['stg_id', 'raw_id']

        mappings = self._get_silver_mappings(format_id)
        mapped_columns = [m['target_column'] for m in mappings]

        # Add essential columns at the start if not already present
        result = []
        for col in essential_columns:
            if col not in mapped_columns:
                result.append(col)

        # Add all mapped columns
        result.extend(mapped_columns)

        return result

    def get_silver_values(self, format_id: str, record: Dict[str, Any]) -> Tuple:
        """Get ordered tuple of values for Silver INSERT.

        Must return values in the same order as get_silver_columns().
        Essential columns (stg_id, raw_id) are prepended if not in mappings.
        """
        # Essential columns that should always be included (must match get_silver_columns)
        essential_columns = ['stg_id', 'raw_id']

        mappings = self._get_silver_mappings(format_id)
        mapped_columns = [m['target_column'] for m in mappings]

        # Build values in same order as get_silver_columns
        values = []
        for col in essential_columns:
            if col not in mapped_columns:
                values.append(record.get(col))

        # Add values for all mapped columns
        for m in mappings:
            values.append(record.get(m['target_column']))

        return tuple(values)

    def clear_cache(self):
        """Clear all cached mappings."""
        self._mapping_cache.clear()
        self._format_cache.clear()


class MappingExtractor:
    """
    Extractor that uses database-driven mappings.

    This can replace the hard-coded extractors with a database-driven approach.
    """

    def __init__(self, connection, format_id: str):
        """Initialize with database connection and format ID."""
        self.conn = connection
        self.format_id = format_id
        self.mapper = DynamicMapper(connection)
        self._format_info = self.mapper._get_format_info(format_id)

    @property
    def MESSAGE_TYPE(self) -> str:
        return self.format_id

    @property
    def SILVER_TABLE(self) -> str:
        return self._format_info['silver_table']

    def generate_raw_id(self, msg_id: str = '') -> str:
        """Generate a unique raw_id for Bronze records."""
        import hashlib
        unique = f"{msg_id}_{uuid.uuid4().hex[:8]}"
        hash_part = hashlib.sha256(unique.encode()).hexdigest()[:12]
        return f"raw_{hash_part}"

    def generate_stg_id(self) -> str:
        """Generate a unique stg_id for Silver records."""
        return str(uuid.uuid4())

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw content."""
        msg_id = raw_content.get('messageId', '') or raw_content.get('msg_id', '')
        return {
            'raw_id': self.generate_raw_id(msg_id),
            'message_type': self.format_id,
            'raw_content': json.dumps(raw_content) if isinstance(raw_content, dict) else raw_content,
            'batch_id': batch_id,
        }

    def extract_silver(
        self,
        msg_content: Dict[str, Any],
        raw_id: str,
        stg_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        """Extract Silver record using database mappings."""
        record = self.mapper.extract_silver_record(
            self.format_id, msg_content, raw_id, batch_id
        )
        # Override the generated stg_id with the provided one
        record['stg_id'] = stg_id
        return record

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns."""
        return self.mapper.get_silver_columns(self.format_id)

    def get_silver_values(self, silver_record: Dict[str, Any]) -> Tuple:
        """Return ordered tuple of values for Silver INSERT."""
        return self.mapper.get_silver_values(self.format_id, silver_record)


def test_dynamic_mapper():
    """Test the dynamic mapper with sample data."""
    import psycopg2
    import os

    conn = psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=int(os.environ.get('POSTGRES_PORT', 5433)),
        database=os.environ.get('POSTGRES_DB', 'gps_cdm'),
        user=os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
        password=os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password')
    )

    mapper = DynamicMapper(conn)

    # Test data
    test_record = {
        'messageId': 'TEST-DYNAMIC-001',
        'creationDateTime': '2024-01-15T10:30:00Z',
        'numberOfTransactions': 1,
        'controlSum': 1000.00,
        'initiatingParty': {
            'name': 'ACME Corp',
            'id': 'ACME123',
            'idType': 'CUST',
            'country': 'US'
        },
        'debtor': {
            'name': 'John Doe',
            'streetName': '123 Main St',
            'townName': 'New York',
            'country': 'US'
        },
        'debtorAccount': {
            'iban': 'US12345678901234567890',
            'currency': 'USD'
        },
        'debtorAgent': {
            'bic': 'CITIUS33XXX',
            'name': 'Citibank',
            'country': 'US'
        },
        'instructedAmount': 1000.00,
        'instructedCurrency': 'USD',
        'creditor': {
            'name': 'Jane Smith',
            'townName': 'Paris',
            'country': 'FR'
        },
        'creditorAccount': {
            'iban': 'FR7630004000310001234567890',
            'currency': 'EUR'
        },
        'creditorAgent': {
            'bic': 'BNPAFRPP',
            'name': 'BNP Paribas',
            'country': 'FR'
        },
        'chargeBearer': 'SHAR'
    }

    # Extract Silver record
    silver_record = mapper.extract_silver_record(
        'pain.001',
        test_record,
        'raw_test123',
        'batch_test001'
    )

    print("="*60)
    print("Silver Record Extraction Test")
    print("="*60)
    print(f"Total columns: {len(silver_record)}")
    print(f"stg_id: {silver_record.get('stg_id')}")
    print(f"raw_id: {silver_record.get('raw_id')}")
    print(f"msg_id: {silver_record.get('msg_id')}")
    print(f"debtor_name: {silver_record.get('debtor_name')}")
    print(f"debtor_country: {silver_record.get('debtor_country')}")
    print(f"creditor_name: {silver_record.get('creditor_name')}")
    print(f"instructed_amount: {silver_record.get('instructed_amount')}")
    print(f"_batch_id: {silver_record.get('_batch_id')}")
    print("="*60)

    conn.close()
    return silver_record


if __name__ == '__main__':
    test_dynamic_mapper()
