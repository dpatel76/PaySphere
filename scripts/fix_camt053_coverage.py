#!/usr/bin/env python3
"""
Script to fix Standard->Silver field coverage for camt.053 to 100%.

This script:
1. Queries all 211 data elements from mapping.standard_fields
2. Generates ALTER TABLE statements for missing columns
3. Generates INSERT statements for missing silver_field_mappings
"""

import re
import subprocess
import sys


def run_psql(query):
    """Run a psql query and return the result."""
    cmd = [
        'docker', 'exec', 'gps-cdm-postgres',
        'psql', '-U', 'gps_cdm_svc', '-d', 'gps_cdm',
        '-t', '-A', '-F', '|', '-c', query
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return []
    return [line for line in result.stdout.strip().split('\n') if line]


def field_name_to_column(field_name):
    """Convert field_name like 'TxDtls_RltdPties_Cdtr_Nm' to snake_case column name."""
    # First convert CamelCase parts to lowercase with underscores
    # Handle special cases like 'IBAN', 'BIC', 'LEI', 'BICFI'
    s = field_name

    # Preserve underscore-separated parts but convert each part
    parts = s.split('_')
    result_parts = []

    for part in parts:
        # Handle acronyms and convert to lowercase
        # Insert underscore before uppercase letters (for CamelCase)
        converted = re.sub(r'([a-z])([A-Z])', r'\1_\2', part)
        # Handle sequences of uppercase (like 'BICFI' -> 'bicfi')
        converted = converted.lower()
        result_parts.append(converted)

    return '_'.join(result_parts)


def data_type_to_pg_type(data_type):
    """Convert standard field data type to PostgreSQL type."""
    type_map = {
        'string': 'VARCHAR(500)',
        'decimal': 'NUMERIC(18,4)',
        'integer': 'INTEGER',
        'boolean': 'BOOLEAN',
        'date': 'DATE',
        'datetime': 'TIMESTAMP',
    }
    return type_map.get(data_type, 'VARCHAR(500)')


def get_standard_fields():
    """Get all data elements from standard_fields for camt.053."""
    query = """
    SELECT field_path, field_name, data_type, is_mandatory
    FROM mapping.standard_fields
    WHERE format_id = 'camt.053' AND data_type <> 'complex'
    ORDER BY field_path
    """
    rows = run_psql(query)
    fields = []
    for row in rows:
        parts = row.split('|')
        if len(parts) >= 4:
            fields.append({
                'field_path': parts[0],
                'field_name': parts[1],
                'data_type': parts[2],
                'is_mandatory': parts[3] == 't'
            })
    return fields


def get_existing_columns():
    """Get existing columns in silver.stg_camt053."""
    query = """
    SELECT column_name FROM information_schema.columns
    WHERE table_schema = 'silver' AND table_name = 'stg_camt053'
    """
    return set(run_psql(query))


def get_existing_mappings():
    """Get existing source_path values in silver_field_mappings for camt.053."""
    query = """
    SELECT source_path FROM mapping.silver_field_mappings
    WHERE format_id = 'camt.053'
    """
    return set(run_psql(query))


def generate_parser_path(field_path, field_name):
    """Generate the parser_path based on field_path.

    The parser uses camelCase keys extracted from XML.
    Examples:
    - BkToCstmrStmt/GrpHdr/MsgId -> msgId
    - BkToCstmrStmt/Stmt/Acct/Id/IBAN -> accountIdIban
    - BkToCstmrStmt/Stmt/Bal/Amt -> balanceAmount
    """
    # Extract the meaningful parts of the path
    parts = field_path.split('/')

    # Skip the root element (BkToCstmrStmt)
    if parts[0] == 'BkToCstmrStmt':
        parts = parts[1:]

    # Handle @Ccy attribute specially - it's on the parent amount
    if parts[-1] == '@Ccy':
        parts = parts[:-1]
        parts[-1] = parts[-1] + 'Currency'

    # Convert path parts to camelCase
    if len(parts) == 0:
        return field_name

    # Build camelCase path
    result = []
    for i, part in enumerate(parts):
        # Skip GrpHdr and Stmt as they're container elements
        if part in ('GrpHdr', 'Stmt'):
            continue

        # Convert part to camelCase
        # Handle abbreviations like IBAN, BICFI, etc.
        if part.isupper():
            if i == 0 or len(result) == 0:
                result.append(part.lower())
            else:
                result.append(part.capitalize() if len(part) > 2 else part.upper())
        else:
            if len(result) == 0:
                # First part is lowercase
                result.append(part[0].lower() + part[1:])
            else:
                # Subsequent parts have first letter capitalized
                result.append(part[0].upper() + part[1:])

    # Join without separator for camelCase
    if len(result) == 0:
        return field_name

    # For nested paths, join with dots for hierarchical access
    if len(result) > 3:
        # Deep paths use dot notation
        return '.'.join(result)
    else:
        # Simple paths use camelCase concatenation
        return ''.join(result)


def main():
    print("=" * 80)
    print("Fixing camt.053 Standard->Silver Field Coverage")
    print("=" * 80)

    # Get all standard fields
    standard_fields = get_standard_fields()
    print(f"\nTotal standard data elements: {len(standard_fields)}")

    # Get existing columns
    existing_columns = get_existing_columns()
    print(f"Existing Silver columns: {len(existing_columns)}")

    # Get existing mappings
    existing_mappings = get_existing_mappings()
    print(f"Existing Silver mappings: {len(existing_mappings)}")

    # Process each standard field
    alter_statements = []
    insert_statements = []

    # System columns that should not be added from standard fields
    system_columns = {
        'stg_id', 'raw_id', 'message_type', '_batch_id', '_processed_at',
        'processing_status', 'processed_to_gold_at'
    }

    for field in standard_fields:
        field_path = field['field_path']
        field_name = field['field_name']
        data_type = field['data_type']
        is_mandatory = field['is_mandatory']

        # Generate target column name (snake_case)
        target_column = field_name_to_column(field_name)

        # Skip system columns
        if target_column in system_columns:
            continue

        # Generate parser path
        parser_path = generate_parser_path(field_path, field_name)

        # Check if column needs to be added
        if target_column not in existing_columns:
            pg_type = data_type_to_pg_type(data_type)
            alter_statements.append(
                f"ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS {target_column} {pg_type};"
            )

        # Check if mapping needs to be added
        # Source path must match field_path exactly
        if field_path not in existing_mappings:
            # Map data_type to PostgreSQL type string
            pg_type_str = {
                'string': 'VARCHAR',
                'decimal': 'DECIMAL',
                'integer': 'INTEGER',
                'boolean': 'BOOLEAN',
                'date': 'DATE',
                'datetime': 'TIMESTAMP'
            }.get(data_type, 'VARCHAR')

            insert_statements.append(
                f"""INSERT INTO mapping.silver_field_mappings
                (format_id, target_column, source_path, parser_path, data_type, is_required, is_active)
                VALUES ('camt.053', '{target_column}', '{field_path}', '{parser_path}', '{pg_type_str}', {str(is_mandatory).lower()}, true)
                ON CONFLICT (format_id, target_column) DO UPDATE SET
                    source_path = EXCLUDED.source_path,
                    parser_path = EXCLUDED.parser_path,
                    is_required = EXCLUDED.is_required;"""
            )

    print(f"\nColumns to add: {len(alter_statements)}")
    print(f"Mappings to add: {len(insert_statements)}")

    # Write ALTER TABLE statements
    alter_file = '/tmp/camt053_alter_table.sql'
    with open(alter_file, 'w') as f:
        f.write("-- ALTER TABLE statements for silver.stg_camt053\n")
        f.write("-- Generated by fix_camt053_coverage.py\n\n")
        for stmt in alter_statements:
            f.write(stmt + "\n")
    print(f"\nALTER TABLE statements written to: {alter_file}")

    # Write INSERT statements
    insert_file = '/tmp/camt053_insert_mappings.sql'
    with open(insert_file, 'w') as f:
        f.write("-- INSERT statements for mapping.silver_field_mappings\n")
        f.write("-- Generated by fix_camt053_coverage.py\n\n")
        f.write("-- First, check if there's a unique constraint\n")
        f.write("-- If not, we'll use a different approach\n\n")
        for stmt in insert_statements:
            f.write(stmt + "\n\n")
    print(f"INSERT statements written to: {insert_file}")

    # Print sample of what will be done
    print("\n" + "=" * 80)
    print("Sample ALTER TABLE statements (first 10):")
    print("=" * 80)
    for stmt in alter_statements[:10]:
        print(stmt)

    print("\n" + "=" * 80)
    print("Sample INSERT statements (first 5):")
    print("=" * 80)
    for stmt in insert_statements[:5]:
        print(stmt[:200] + "..." if len(stmt) > 200 else stmt)

    return alter_statements, insert_statements


if __name__ == '__main__':
    main()
