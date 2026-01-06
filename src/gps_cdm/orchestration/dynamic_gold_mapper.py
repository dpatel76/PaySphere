"""
Dynamic Gold Mapper - Uses database mappings to populate ALL Gold tables.

This module reads from mapping.gold_field_mappings to determine which Silver
columns should be written to which Gold tables (CDM core + extensions).

Gold Tables:
- cdm_payment_instruction: Main payment record (for payment messages)
- cdm_account_statement: Statement record (for camt.053, MT940, etc.)
- cdm_party: Debtor, Creditor, Ultimate parties
- cdm_account: Debtor/Creditor accounts
- cdm_financial_institution: Agent banks
- cdm_payment_extension_*: Format-specific extensions
- cdm_statement_extension: Statement-specific extensions
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
    - cdm_payment_instruction: For payment messages (pain.001, MT103, etc.)
    - cdm_account_statement: For statement messages (camt.053, MT940, etc.)
    - cdm_party (with entity_role: DEBTOR, CREDITOR, ULTIMATE_DEBTOR, ULTIMATE_CREDITOR)
    - cdm_account (with entity_role: DEBTOR, CREDITOR)
    - cdm_financial_institution (with entity_role: DEBTOR_AGENT, CREDITOR_AGENT, etc.)
    - cdm_payment_extension_*: Format-specific payment extensions
    - cdm_statement_extension: Statement-specific extensions
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
        - COALESCE function: e.g., 'COALESCE(col1, col2, 'default')' -> first non-null value
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

        # SUBSTRING function: SUBSTRING(col, start, length) or SUBSTRING(expr, start, length)
        # Extracts substring from position start with given length (1-indexed)
        if expr.upper().startswith('SUBSTRING(') and expr.endswith(')'):
            return self._evaluate_substring(expr, silver_data, context)

        # COALESCE function: COALESCE(col1, col2, 'literal', ...)
        # Returns first non-null value from the list
        if expr.upper().startswith('COALESCE(') and expr.endswith(')'):
            return self._evaluate_coalesce(expr, silver_data, context)

        # CASE WHEN expression: CASE WHEN condition THEN value ELSE other END
        if expr.upper().startswith('CASE WHEN') and expr.upper().endswith('END'):
            return self._evaluate_case_when(expr, silver_data, context)

        # Silver column reference
        value = silver_data.get(expr)

        # Apply default if value is None and mapping has default
        # (handled separately in build_gold_records)

        return value

    def _evaluate_coalesce(self, expr: str, silver_data: Dict[str, Any],
                           context: Dict[str, Any] = None) -> Any:
        """Evaluate COALESCE(arg1, arg2, ...) expression."""
        args_str = expr[9:-1]  # Remove 'COALESCE(' and ')'
        args = self._parse_coalesce_args(args_str)

        for arg in args:
            arg = arg.strip()
            if not arg:
                continue
            # Check if arg is a literal string
            if arg.startswith("'") and arg.endswith("'"):
                return arg[1:-1]
            # Check if arg references silver.column (remove prefix)
            if arg.startswith('silver.'):
                arg = arg[7:]
            # Recursively evaluate if it's a function call
            if '(' in arg:
                value = self._evaluate_expression(arg, silver_data, context)
            else:
                # Try to get value from silver_data
                value = silver_data.get(arg)
            if value is not None and value != '':
                return value
        return None

    def _evaluate_substring(self, expr: str, silver_data: Dict[str, Any],
                            context: Dict[str, Any] = None) -> Any:
        """
        Evaluate SUBSTRING(source, start, length) expression.

        Handles nested COALESCE and column references.
        Note: PostgreSQL SUBSTRING is 1-indexed, Python is 0-indexed.
        """
        args_str = expr[10:-1]  # Remove 'SUBSTRING(' and ')'
        args = self._parse_coalesce_args(args_str)

        if len(args) < 2:
            return None

        # First arg is the source string (column or expression)
        source_expr = args[0].strip()
        if '(' in source_expr:
            # Nested function call (e.g., COALESCE)
            source_value = self._evaluate_expression(source_expr, silver_data, context)
        else:
            source_value = silver_data.get(source_expr)

        if not source_value:
            return None

        source_value = str(source_value)

        # Parse start position (1-indexed in SQL)
        try:
            start = int(args[1].strip()) - 1  # Convert to 0-indexed
        except (ValueError, IndexError):
            return None

        # Parse optional length
        length = None
        if len(args) >= 3:
            try:
                length = int(args[2].strip())
            except ValueError:
                pass

        if length is not None:
            return source_value[start:start + length]
        else:
            return source_value[start:]

    def _evaluate_case_when(self, expr: str, silver_data: Dict[str, Any],
                            context: Dict[str, Any] = None) -> Any:
        """
        Evaluate simple CASE WHEN expressions.

        Supports:
        - CASE WHEN col IN ('a','b') THEN 'X' ELSE 'Y' END
        - CASE WHEN col = 'value' THEN 'X' ELSE 'Y' END
        - CASE WHEN col != 'value' THEN 'X' ELSE 'Y' END
        - CASE WHEN expr1 != expr2 THEN true ELSE false END
        """
        import re

        # Extract WHEN...THEN...ELSE parts
        case_match = re.match(
            r"CASE\s+WHEN\s+(.+?)\s+THEN\s+(.+?)\s+ELSE\s+(.+?)\s+END",
            expr,
            re.IGNORECASE
        )
        if not case_match:
            return None

        condition = case_match.group(1).strip()
        then_value = case_match.group(2).strip()
        else_value = case_match.group(3).strip()

        # Evaluate condition
        condition_result = self._evaluate_condition(condition, silver_data, context)

        # Return appropriate value
        result_expr = then_value if condition_result else else_value

        # Parse result (could be literal, boolean, or column)
        if result_expr.lower() == 'true':
            return True
        elif result_expr.lower() == 'false':
            return False
        elif result_expr.startswith("'") and result_expr.endswith("'"):
            return result_expr[1:-1]
        else:
            return self._evaluate_expression(result_expr, silver_data, context)

    def _evaluate_condition(self, condition: str, silver_data: Dict[str, Any],
                            context: Dict[str, Any] = None) -> bool:
        """Evaluate a simple condition expression."""
        import re

        # Handle IN clause: col IN ('a', 'b', 'c')
        in_match = re.match(r"(.+?)\s+IN\s*\((.+?)\)", condition, re.IGNORECASE)
        if in_match:
            col_expr = in_match.group(1).strip()
            values_str = in_match.group(2).strip()

            col_value = self._evaluate_expression(col_expr, silver_data, context)
            if col_value is None:
                return False

            # Parse IN values
            values = [v.strip().strip("'\"") for v in values_str.split(',')]
            return str(col_value) in values

        # Handle != comparison
        if '!=' in condition:
            parts = condition.split('!=')
            if len(parts) == 2:
                left = self._evaluate_expression(parts[0].strip(), silver_data, context)
                right = self._evaluate_expression(parts[1].strip(), silver_data, context)
                return left != right

        # Handle = comparison
        if '=' in condition:
            parts = condition.split('=')
            if len(parts) == 2:
                left = self._evaluate_expression(parts[0].strip(), silver_data, context)
                right = self._evaluate_expression(parts[1].strip(), silver_data, context)
                return left == right

        return False

    def _parse_coalesce_args(self, args_str: str) -> List[str]:
        """
        Parse COALESCE arguments, handling quoted strings and nested functions.

        Example: "col1, col2, 'default'" -> ['col1', 'col2', "'default'"]
        """
        args = []
        current_arg = ""
        in_quotes = False
        paren_depth = 0

        for char in args_str:
            if char == "'" and paren_depth == 0:
                in_quotes = not in_quotes
                current_arg += char
            elif char == '(' and not in_quotes:
                paren_depth += 1
                current_arg += char
            elif char == ')' and not in_quotes:
                paren_depth -= 1
                current_arg += char
            elif char == ',' and not in_quotes and paren_depth == 0:
                args.append(current_arg.strip())
                current_arg = ""
            else:
                current_arg += char

        if current_arg.strip():
            args.append(current_arg.strip())

        return args

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
        elif transform == 'COALESCE_UUID':
            # COALESCE_UUID - returns value if not NULL, otherwise generates a UUID
            if value:
                return value
            return str(uuid.uuid4())
        elif transform.startswith('COALESCE:'):
            # COALESCE:default_value - returns literal default if value is NULL
            return value if value else transform[9:]
        elif transform.startswith('COALESCE_FIELD:'):
            # COALESCE_FIELD:other_field - looks up other_field from silver_data if value is NULL
            if value:
                return value
            fallback_field = transform[15:]  # Remove 'COALESCE_FIELD:' prefix
            if silver_data and fallback_field:
                return silver_data.get(fallback_field)
            return None
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
            # Try to derive from BIC - support multiple naming conventions
            if silver_data and entity_role:
                # Map entity roles to possible BIC field names across formats
                role_to_bic_fields = {
                    'DEBTOR_AGENT': ['debtor_agent_bic', 'ordering_institution_bic', 'sender_bic'],
                    'CREDITOR_AGENT': ['creditor_agent_bic', 'account_with_institution_bic', 'receiver_bic'],
                    'INTERMEDIARY': ['intermediary_bic', 'intermediary_institution_bic'],
                    'INTERMEDIARY_AGENT1': ['intermediary_agent1_bic', 'intermediary_bic'],
                    'INTERMEDIARY_AGENT2': ['intermediary_agent2_bic'],
                    'SENDERS_CORRESPONDENT': ['senders_correspondent_bic'],
                    'RECEIVERS_CORRESPONDENT': ['receivers_correspondent_bic'],
                    'ACCOUNT_SERVICER': ['sender_bic', 'account_servicer_bic'],  # MT940 sender
                    'MESSAGE_RECIPIENT': ['receiver_bic', 'message_recipient_bic'],  # MT940 receiver
                }
                bic_fields = role_to_bic_fields.get(entity_role, [])
                for bic_field in bic_fields:
                    bic = silver_data.get(bic_field)
                    if bic:
                        return f"Institution ({bic})"
            # Return None to trigger default_value if set
            return None
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
        elif transform == 'TIME_TO_HHMM':
            # Convert TIME value to HHMM format string (4 chars)
            # Input can be: TIME object, datetime object, or string like "12:34:00"
            if value is None:
                return None
            try:
                if hasattr(value, 'strftime'):
                    # datetime or time object
                    return value.strftime('%H%M')
                elif isinstance(value, str):
                    # String like "12:34:00" or "12:34"
                    parts = value.replace(':', '')[:4]  # Remove colons, take first 4 chars
                    return parts if len(parts) >= 4 else parts.ljust(4, '0')
            except (ValueError, AttributeError):
                return str(value)[:4] if value else None
            return str(value)[:4] if value else None
        elif transform == 'COUNTRY_FROM_BIC':
            # Extract country code (chars 5-6) from BIC
            # BIC format: AAAABBCC where BB is country code (positions 5-6, 1-indexed)
            # First, try to extract from the value directly if it looks like a BIC
            if value and isinstance(value, str) and len(value) >= 6:
                # BIC country code is at positions 5-6 (0-indexed: 4-5)
                return value[4:6].upper()
            # Next, try to look up BIC field based on entity_role
            if silver_data and entity_role:
                # Map entity roles to possible BIC field names across formats
                role_to_bic_fields = {
                    'DEBTOR_AGENT': ['debtor_agent_bic', 'ordering_institution_bic', 'sender_bic'],
                    'CREDITOR_AGENT': ['creditor_agent_bic', 'account_with_institution_bic', 'receiver_bic'],
                    'INTERMEDIARY': ['intermediary_bic', 'intermediary_institution_bic'],
                    'INTERMEDIARY_AGENT1': ['intermediary_agent1_bic', 'intermediary_bic'],
                    'INTERMEDIARY_AGENT2': ['intermediary_agent2_bic'],
                    'SENDERS_CORRESPONDENT': ['senders_correspondent_bic'],
                    'RECEIVERS_CORRESPONDENT': ['receivers_correspondent_bic'],
                    'ACCOUNT_SERVICER': ['sender_bic', 'account_servicer_bic'],  # MT940 sender
                    'MESSAGE_RECIPIENT': ['receiver_bic', 'message_recipient_bic'],  # MT940 receiver
                }
                bic_fields = role_to_bic_fields.get(entity_role, [])
                for bic_field in bic_fields:
                    bic = silver_data.get(bic_field)
                    if bic and len(bic) >= 6:
                        # BIC country code is at positions 5-6 (0-indexed: 4-5)
                        return bic[4:6].upper()
            return None

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
        now = datetime.utcnow()
        context = {
            'stg_id': stg_id,
            'batch_id': batch_id,
            'format_id': format_id,
            'now': now,
            'year': now.year,
            'month': now.month,
            'today': now.date(),
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
            'cdm_account_statement': ['statement_id'],
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
            'statement_id': None,
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
            'account_servicer_id': None,
        }

        # Persist in order: entities first, then instruction/statement (which references them)
        entity_order = [
            'cdm_party',
            'cdm_account',
            'cdm_financial_institution',
            'cdm_payment_instruction',
            'cdm_account_statement',
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
            elif table == 'cdm_statement_extension':
                for record in table_records:
                    # Add statement_id to extension record
                    if result['statement_id']:
                        record.columns['statement_id'] = result['statement_id']
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

        # Add foreign key references for account statement
        elif table == 'cdm_account_statement':
            # Add account servicer FK
            columns['account_servicer_id'] = entity_ids.get('account_servicer_id')
            # Add account FK if available
            columns['account_id'] = entity_ids.get('debtor_account_id')

            # Add audit fields
            columns['current_status'] = columns.get('current_status') or 'PROCESSED'
            columns['created_at'] = datetime.utcnow()
            columns['updated_at'] = datetime.utcnow()

            # Partition fields (with defaults in case context didn't set them)
            now = datetime.utcnow()
            columns['partition_year'] = columns.get('partition_year') or now.year
            columns['partition_month'] = columns.get('partition_month') or now.month

            # Default region if not set
            columns['region'] = columns.get('region') or 'GLOBAL'

            # Default valid_from if not set
            columns['valid_from'] = columns.get('valid_from') or now.date()

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
            'cdm_account_statement': 'statement_id',
            'cdm_party': 'party_id',
            'cdm_account': 'account_id',
            'cdm_financial_institution': 'fi_id',
        }
        # Extension tables use 'extension_id'
        if table.startswith('cdm_payment_extension_') or table == 'cdm_statement_extension':
            return 'extension_id'
        return id_columns.get(table, 'id')

    def _generate_id(self, table: str) -> str:
        """Generate a prefixed ID for a table."""
        prefixes = {
            'cdm_payment_instruction': 'instr_',
            'cdm_account_statement': 'stmt_',
            'cdm_party': 'party_',
            'cdm_account': 'acct_',
            'cdm_financial_institution': 'fi_',
            'cdm_statement_extension': 'stext_',
        }
        prefix = prefixes.get(table, 'ext_')
        return f"{prefix}{uuid.uuid4().hex[:12]}"

    def _track_entity_id(self, result: Dict, table: str, role: Optional[str],
                        entity_id: str) -> None:
        """Track entity ID in result dict based on table and role."""
        if table == 'cdm_payment_instruction':
            result['instruction_id'] = entity_id
        elif table == 'cdm_account_statement':
            result['statement_id'] = entity_id
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
                'ACCOUNT_SERVICER': 'account_servicer_id',
            }
            if role and role in role_map:
                result[role_map[role]] = entity_id

    @classmethod
    def clear_cache(cls) -> None:
        """Clear mappings cache."""
        cls._mappings_cache = {}

    @staticmethod
    def persist_extension_data(cursor, silver_data: Dict[str, Any],
                               format_id: str, instruction_id: str) -> Optional[str]:
        """
        Persist extension data to format-specific Gold extension table.

        Uses database mappings from mapping.gold_field_mappings to determine
        which Silver columns map to which extension table columns.

        Args:
            cursor: Database cursor
            silver_data: Dict of Silver column -> value
            format_id: Message format (e.g., 'MT103', 'pain.001')
            instruction_id: The instruction_id to link extension to

        Returns:
            extension_id if created, None otherwise
        """
        # Determine extension table based on format
        format_lower = format_id.lower().replace('.', '').replace('-', '_')

        # Map format to extension table
        format_to_extension = {
            'pain001': 'cdm_payment_extension_iso20022',
            'pacs008': 'cdm_payment_extension_iso20022',
            'camt053': 'cdm_payment_extension_iso20022',
            'mt103': 'cdm_payment_extension_swift',
            'mt202': 'cdm_payment_extension_swift',
            'mt940': 'cdm_payment_extension_swift',
            'fedwire': 'cdm_payment_extension_fedwire',
            'ach': 'cdm_payment_extension_ach',
            'sepa': 'cdm_payment_extension_sepa',
            'rtp': 'cdm_payment_extension_rtp',
            'bacs': 'cdm_payment_extension_bacs',
            'chaps': 'cdm_payment_extension_chaps',
            'fps': 'cdm_payment_extension_fps',
            'target2': 'cdm_payment_extension_target2',
            'fednow': 'cdm_payment_extension_fednow',
            'npp': 'cdm_payment_extension_npp',
            'chips': 'cdm_payment_extension_chips',
            'pix': 'cdm_payment_extension_pix',
            'upi': 'cdm_payment_extension_upi',
            'cnaps': 'cdm_payment_extension_cnaps',
            'bojnet': 'cdm_payment_extension_bojnet',
            'kftc': 'cdm_payment_extension_kftc',
            'meps_plus': 'cdm_payment_extension_meps_plus',
            'rtgs_hk': 'cdm_payment_extension_rtgs_hk',
            'sarie': 'cdm_payment_extension_sarie',
            'uaefts': 'cdm_payment_extension_uaefts',
            'promptpay': 'cdm_payment_extension_promptpay',
            'paynow': 'cdm_payment_extension_paynow',
            'instapay': 'cdm_payment_extension_instapay',
        }

        extension_table = format_to_extension.get(format_lower)
        if not extension_table:
            # No extension table for this format
            return None

        # Load extension mappings from database
        cursor.execute("""
            SELECT gold_column, source_expression, transform_expression
            FROM mapping.gold_field_mappings
            WHERE format_id = %s
              AND gold_table = %s
              AND is_active = TRUE
            ORDER BY ordinal_position
        """, (format_id, extension_table))

        mappings = cursor.fetchall()
        if not mappings:
            # No mappings defined for this extension table
            return None

        # Build extension record from mappings
        extension_id = f"ext_{uuid.uuid4().hex[:12]}"
        columns = {
            'extension_id': extension_id,
            'instruction_id': instruction_id,
            'created_at': datetime.utcnow(),
        }

        for gold_column, source_expr, transform_expr in mappings:
            if gold_column in ('extension_id', 'instruction_id', 'created_at'):
                continue  # Skip system columns

            # Get value from silver data
            value = None
            if source_expr and source_expr not in ('NULL', '', '_GENERATED_UUID'):
                if source_expr.startswith("'") and source_expr.endswith("'"):
                    # Literal value
                    value = source_expr[1:-1]
                else:
                    # Column reference
                    value = silver_data.get(source_expr)

            # Apply transforms if any
            if transform_expr and value is not None:
                if transform_expr == 'UPPER':
                    value = str(value).upper() if value else None
                elif transform_expr == 'LOWER':
                    value = str(value).lower() if value else None
                elif transform_expr == 'TRIM':
                    value = str(value).strip() if value else None
                elif transform_expr == 'TO_ARRAY':
                    value = [value] if value else None
                elif transform_expr.startswith('COALESCE:'):
                    if value is None:
                        value = transform_expr[9:]

            if value is not None:
                columns[gold_column] = value

        # Only insert if we have data beyond system columns
        if len(columns) <= 3:  # extension_id, instruction_id, created_at
            return None

        # Build INSERT statement
        col_names = list(columns.keys())
        placeholders = ', '.join(['%s'] * len(col_names))
        col_list = ', '.join(col_names)
        values = [columns[c] for c in col_names]

        try:
            cursor.execute(f"""
                INSERT INTO gold.{extension_table} ({col_list})
                VALUES ({placeholders})
                ON CONFLICT (extension_id) DO NOTHING
                RETURNING extension_id
            """, values)

            row = cursor.fetchone()
            if row:
                return row[0]
        except Exception as e:
            logger.warning(f"Failed to insert extension data into {extension_table}: {e}")

        return None


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
