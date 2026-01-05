"""
Dynamic Gold Mapper - Uses database mappings to populate ALL Gold tables.

This module reads from mapping.gold_field_mappings to determine which Silver
columns should be written to which Gold tables (CDM core + extensions).

Gold Tables:
- cdm_payment_instruction: Main payment record
- cdm_party: Debtor, Creditor, Ultimate parties
- cdm_account: Debtor/Creditor accounts
- cdm_financial_institution: Agent banks
- cdm_payment_extension_*: Format-specific extensions
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class GoldMapping:
    """A single Gold field mapping."""
    gold_table: str
    gold_column: str
    source_expression: str
    entity_role: Optional[str] = None
    data_type: Optional[str] = None
    is_required: bool = False
    default_value: Optional[str] = None
    transform_expression: Optional[str] = None
    ordinal_position: int = 0


@dataclass
class GoldRecord:
    """A record to be inserted into a Gold table."""
    table_name: str
    columns: Dict[str, Any] = field(default_factory=dict)
    entity_role: Optional[str] = None


class DynamicGoldMapper:
    """
    Maps Silver records to Gold tables using database-driven mappings.

    Supports all Gold CDM tables:
    - cdm_payment_instruction
    - cdm_party (with entity_role: DEBTOR, CREDITOR, ULTIMATE_DEBTOR, ULTIMATE_CREDITOR)
    - cdm_account (with entity_role: DEBTOR, CREDITOR)
    - cdm_financial_institution (with entity_role: DEBTOR_AGENT, CREDITOR_AGENT, etc.)
    - cdm_payment_extension_* (format-specific)
    """

    # Cache for mappings by format
    _mappings_cache: Dict[str, List[GoldMapping]] = {}

    def __init__(self, conn):
        """Initialize with database connection."""
        self.conn = conn

    def _load_mappings(self, format_id: str) -> List[GoldMapping]:
        """Load Gold mappings from database for a format."""
        if format_id in self._mappings_cache:
            return self._mappings_cache[format_id]

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT gold_table, gold_column, source_expression, entity_role,
                   data_type, is_required, default_value, transform_expression,
                   ordinal_position
            FROM mapping.gold_field_mappings
            WHERE format_id = %s AND is_active = TRUE
            ORDER BY gold_table, entity_role NULLS FIRST, ordinal_position
        """, (format_id,))

        mappings = []
        for row in cursor.fetchall():
            mappings.append(GoldMapping(
                gold_table=row[0],
                gold_column=row[1],
                source_expression=row[2],
                entity_role=row[3],
                data_type=row[4],
                is_required=row[5] or False,
                default_value=row[6],
                transform_expression=row[7],
                ordinal_position=row[8] or 0
            ))

        cursor.close()
        self._mappings_cache[format_id] = mappings
        logger.debug(f"Loaded {len(mappings)} Gold mappings for {format_id}")
        return mappings

    def _evaluate_expression(self, expr: str, silver_data: Dict[str, Any],
                            context: Dict[str, Any] = None) -> Any:
        """
        Evaluate a source_expression to get a value.

        Expressions can be:
        - Silver column name: e.g., 'debtor_name' -> silver_data['debtor_name']
        - Literal string: e.g., "'pain.001'" -> 'pain.001'
        - Generated UUID: '_GENERATED_UUID' -> new UUID
        - Context variable: '_CONTEXT.stg_id' -> context['stg_id']
        - NULL: 'NULL' or empty -> None
        """
        if not expr or expr.upper() == 'NULL':
            return None

        # Literal string (quoted)
        if expr.startswith("'") and expr.endswith("'"):
            return expr[1:-1]

        # Generated UUID
        if expr == '_GENERATED_UUID':
            return str(uuid.uuid4())

        # Context variable
        if expr.startswith('_CONTEXT.') and context:
            key = expr[9:]  # Remove '_CONTEXT.' prefix
            return context.get(key)

        # Silver column reference
        value = silver_data.get(expr)

        # Apply default if value is None and mapping has default
        # (handled separately in build_gold_records)

        return value

    def _apply_transform(self, value: Any, transform: Optional[str],
                         silver_data: Dict[str, Any] = None,
                         entity_role: Optional[str] = None) -> Any:
        """Apply transform expression if defined."""
        if not transform:
            return value

        # Common transforms
        if transform == 'UPPER':
            return str(value).upper() if value else value
        elif transform == 'LOWER':
            return str(value).lower() if value else value
        elif transform == 'TRIM':
            return str(value).strip() if value else value
        elif transform.startswith('COALESCE:'):
            # COALESCE:default_value
            return value if value else transform[9:]
        elif transform == 'COALESCE_IBAN':
            # For account_number, fall back to IBAN if account_number is NULL
            if value:
                return value
            if silver_data and entity_role:
                iban_field = f"{entity_role.lower()}_account_iban"
                return silver_data.get(iban_field) or silver_data.get('debtor_account_iban') or silver_data.get('creditor_account_iban')
            return value
        elif transform == 'COALESCE_BIC':
            # For institution_name, derive from BIC if name is NULL
            if value:
                return value
            # Try to derive from BIC
            if silver_data and entity_role:
                role_to_bic = {
                    'DEBTOR_AGENT': 'debtor_agent_bic',
                    'CREDITOR_AGENT': 'creditor_agent_bic',
                    'INTERMEDIARY_AGENT1': 'intermediary_agent1_bic',
                    'INTERMEDIARY_AGENT2': 'intermediary_agent2_bic',
                }
                bic_field = role_to_bic.get(entity_role)
                bic = silver_data.get(bic_field) if bic_field else None
                if bic:
                    return f"Institution ({bic})"
            # Return a non-None value so default doesn't override
            return None  # This will trigger default_value application
        elif transform == 'TO_ARRAY':
            # Wrap a single value in an array for PostgreSQL array columns
            if value is None:
                return None
            if isinstance(value, list):
                return value
            return [value]
        elif transform == 'TO_DECIMAL':
            try:
                return float(value) if value else None
            except (ValueError, TypeError):
                return None
        elif transform == 'TO_DATE':
            # Parse ISO date string
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    return value
            return value

        return value

    def build_gold_records(self, format_id: str, silver_data: Dict[str, Any],
                          stg_id: str, batch_id: str) -> Dict[str, List[GoldRecord]]:
        """
        Build Gold records from Silver data using database mappings.

        Returns dict of table_name -> list of GoldRecords to insert.
        For entity tables (party, account, fi), multiple records may be created
        based on entity_role.
        """
        mappings = self._load_mappings(format_id)

        # Context for expression evaluation
        context = {
            'stg_id': stg_id,
            'batch_id': batch_id,
            'format_id': format_id,
            'now': datetime.utcnow()
        }

        # Group mappings by (table, entity_role)
        grouped: Dict[Tuple[str, Optional[str]], List[GoldMapping]] = {}
        for m in mappings:
            key = (m.gold_table, m.entity_role)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(m)

        # Build records
        records: Dict[str, List[GoldRecord]] = {}

        for (table, role), table_mappings in grouped.items():
            if table not in records:
                records[table] = []

            record = GoldRecord(table_name=table, entity_role=role)

            for mapping in table_mappings:
                # Evaluate source expression
                value = self._evaluate_expression(
                    mapping.source_expression, silver_data, context
                )

                # Apply transform BEFORE default (transforms may derive value from other fields)
                if mapping.transform_expression:
                    value = self._apply_transform(
                        value, mapping.transform_expression, silver_data, role
                    )

                # Apply default if value is STILL None after transform
                if value is None and mapping.default_value:
                    value = mapping.default_value

                # Skip if required field is still None
                if mapping.is_required and value is None:
                    logger.warning(
                        f"Required field {mapping.gold_column} is NULL for {format_id}"
                    )

                record.columns[mapping.gold_column] = value

            # Only add record if it has meaningful data
            # For entities, check if key identifier is present
            if self._record_has_data(table, record.columns):
                records[table].append(record)

        return records

    def _record_has_data(self, table: str, columns: Dict[str, Any]) -> bool:
        """Check if a record has meaningful data to insert."""
        # Key fields that indicate the record has data
        key_fields = {
            'cdm_party': ['name'],
            'cdm_account': ['account_number', 'iban'],
            'cdm_financial_institution': ['bic', 'lei', 'institution_name'],
            'cdm_payment_instruction': ['instruction_id'],
        }

        fields = key_fields.get(table)
        if not fields:
            # Extension tables - check if any non-id field has data
            return any(
                v is not None and k not in ('instruction_id', 'extension_id')
                for k, v in columns.items()
            )

        return any(columns.get(f) for f in fields)

    def persist_gold_records(self, cursor, records: Dict[str, List[GoldRecord]],
                            format_id: str) -> Dict[str, Any]:
        """
        Persist Gold records to database.

        Returns dict with created IDs for cross-referencing:
        {
            'instruction_id': '...',
            'debtor_id': '...',
            'creditor_id': '...',
            'debtor_account_id': '...',
            ...
        }
        """
        result = {
            'instruction_id': None,
            'payment_id': None,
            'debtor_id': None,
            'creditor_id': None,
            'ultimate_debtor_id': None,
            'ultimate_creditor_id': None,
            'debtor_account_id': None,
            'creditor_account_id': None,
            'debtor_agent_id': None,
            'creditor_agent_id': None,
            'intermediary_agent1_id': None,
            'intermediary_agent2_id': None,
        }

        # Persist in order: entities first, then instruction (which references them)
        entity_order = [
            'cdm_party',
            'cdm_account',
            'cdm_financial_institution',
            'cdm_payment_instruction',
        ]

        for table in entity_order:
            if table not in records:
                continue

            for record in records[table]:
                entity_id = self._persist_single_record(cursor, record, result)

                # Track IDs for cross-referencing
                if entity_id:
                    self._track_entity_id(result, table, record.entity_role, entity_id)

        # Persist extension tables last
        for table, table_records in records.items():
            if table.startswith('cdm_payment_extension_'):
                for record in table_records:
                    # Add instruction_id to extension record
                    if result['instruction_id']:
                        record.columns['instruction_id'] = result['instruction_id']
                    self._persist_single_record(cursor, record, result)

        return result

    def _persist_single_record(self, cursor, record: GoldRecord,
                               entity_ids: Dict[str, Any]) -> Optional[str]:
        """Persist a single Gold record and return its ID."""
        table = record.table_name
        columns = record.columns.copy()

        # Add foreign key references for instruction
        if table == 'cdm_payment_instruction':
            # Add entity FKs
            columns['debtor_id'] = entity_ids.get('debtor_id')
            columns['creditor_id'] = entity_ids.get('creditor_id')
            columns['ultimate_debtor_id'] = entity_ids.get('ultimate_debtor_id')
            columns['ultimate_creditor_id'] = entity_ids.get('ultimate_creditor_id')
            columns['debtor_account_id'] = entity_ids.get('debtor_account_id')
            columns['creditor_account_id'] = entity_ids.get('creditor_account_id')
            columns['debtor_agent_id'] = entity_ids.get('debtor_agent_id')
            columns['creditor_agent_id'] = entity_ids.get('creditor_agent_id')
            columns['intermediary_agent1_id'] = entity_ids.get('intermediary_agent1_id')
            columns['intermediary_agent2_id'] = entity_ids.get('intermediary_agent2_id')

            # Add audit fields
            columns['current_status'] = columns.get('current_status') or 'PROCESSED'
            columns['created_at'] = datetime.utcnow()
            columns['updated_at'] = datetime.utcnow()

            # Partition fields
            now = datetime.utcnow()
            columns['partition_year'] = now.year
            columns['partition_month'] = now.month

        # Get ID column name
        id_column = self._get_id_column(table)

        # Generate ID if not present
        if id_column and not columns.get(id_column):
            columns[id_column] = self._generate_id(table)

        # Filter out None values for optional columns, keep for nullable ones
        insert_columns = {k: v for k, v in columns.items() if v is not None}

        if not insert_columns:
            return None

        # Build INSERT statement
        col_names = list(insert_columns.keys())
        col_str = ', '.join(col_names)
        placeholders = ', '.join(['%s'] * len(col_names))
        values = [insert_columns[c] for c in col_names]

        try:
            cursor.execute(f"""
                INSERT INTO gold.{table} ({col_str})
                VALUES ({placeholders})
                ON CONFLICT ({id_column}) DO NOTHING
                RETURNING {id_column}
            """, values)

            row = cursor.fetchone()
            return row[0] if row else columns.get(id_column)

        except Exception as e:
            logger.error(f"Failed to insert into {table}: {e}")
            logger.debug(f"Columns: {col_names}, Values: {values}")
            raise

    def _get_id_column(self, table: str) -> str:
        """Get the primary key column name for a table."""
        id_columns = {
            'cdm_payment_instruction': 'instruction_id',
            'cdm_party': 'party_id',
            'cdm_account': 'account_id',
            'cdm_financial_institution': 'fi_id',
        }
        # Extension tables use 'extension_id'
        if table.startswith('cdm_payment_extension_'):
            return 'extension_id'
        return id_columns.get(table, 'id')

    def _generate_id(self, table: str) -> str:
        """Generate a prefixed ID for a table."""
        prefixes = {
            'cdm_payment_instruction': 'instr_',
            'cdm_party': 'party_',
            'cdm_account': 'acct_',
            'cdm_financial_institution': 'fi_',
        }
        prefix = prefixes.get(table, 'ext_')
        return f"{prefix}{uuid.uuid4().hex[:12]}"

    def _track_entity_id(self, result: Dict, table: str, role: Optional[str],
                        entity_id: str) -> None:
        """Track entity ID in result dict based on table and role."""
        if table == 'cdm_payment_instruction':
            result['instruction_id'] = entity_id
            # Also track payment_id if present
        elif table == 'cdm_party':
            role_map = {
                'DEBTOR': 'debtor_id',
                'CREDITOR': 'creditor_id',
                'ULTIMATE_DEBTOR': 'ultimate_debtor_id',
                'ULTIMATE_CREDITOR': 'ultimate_creditor_id',
            }
            if role and role in role_map:
                result[role_map[role]] = entity_id
        elif table == 'cdm_account':
            role_map = {
                'DEBTOR': 'debtor_account_id',
                'CREDITOR': 'creditor_account_id',
            }
            if role and role in role_map:
                result[role_map[role]] = entity_id
        elif table == 'cdm_financial_institution':
            role_map = {
                'DEBTOR_AGENT': 'debtor_agent_id',
                'CREDITOR_AGENT': 'creditor_agent_id',
                'INTERMEDIARY_AGENT1': 'intermediary_agent1_id',
                'INTERMEDIARY_AGENT2': 'intermediary_agent2_id',
            }
            if role and role in role_map:
                result[role_map[role]] = entity_id

    @classmethod
    def clear_cache(cls) -> None:
        """Clear mappings cache."""
        cls._mappings_cache = {}


def process_silver_to_gold(cursor, silver_data: Dict[str, Any], format_id: str,
                          stg_id: str, batch_id: str, conn) -> Dict[str, Any]:
    """
    High-level function to process a Silver record to Gold using dynamic mappings.

    Args:
        cursor: Database cursor
        silver_data: Dict of Silver column -> value
        format_id: Message format (e.g., 'pain.001')
        stg_id: Silver staging ID
        batch_id: Processing batch ID
        conn: Database connection

    Returns:
        Dict with created entity IDs
    """
    mapper = DynamicGoldMapper(conn)

    # Build Gold records from Silver data
    gold_records = mapper.build_gold_records(format_id, silver_data, stg_id, batch_id)

    # Persist to database
    entity_ids = mapper.persist_gold_records(cursor, gold_records, format_id)

    logger.info(f"Processed {format_id} to Gold: instruction={entity_ids.get('instruction_id')}")

    return entity_ids
