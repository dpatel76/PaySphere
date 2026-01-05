#!/usr/bin/env python3
"""
Generate comprehensive field-level mapping report for all payment standards.
Outputs a pipe-delimited file with Bronze → Silver → Gold field mappings.

Usage:
    python scripts/reporting/generate_field_mapping_report.py

Output:
    docs/field_mapping_report.psv
"""

import psycopg2
import os
from datetime import datetime

# Database connection
DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'port': int(os.environ.get('POSTGRES_PORT', 5433)),
    'dbname': os.environ.get('POSTGRES_DB', 'gps_cdm'),
    'user': os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password')
}

# Standard metadata
STANDARD_METADATA = {
    'pain.001': {'country': 'Global', 'format_type': 'ISO20022', 'desc': 'Customer Credit Transfer Initiation'},
    'pacs.008': {'country': 'Global', 'format_type': 'ISO20022', 'desc': 'Financial Institution Credit Transfer'},
    'camt.053': {'country': 'Global', 'format_type': 'ISO20022', 'desc': 'Bank-to-Customer Statement'},
    'MT103': {'country': 'Global', 'format_type': 'SWIFT_MT', 'desc': 'Single Customer Credit Transfer'},
    'MT202': {'country': 'Global', 'format_type': 'SWIFT_MT', 'desc': 'General Financial Institution Transfer'},
    'MT940': {'country': 'Global', 'format_type': 'SWIFT_MT', 'desc': 'Customer Statement Message'},
    'FEDWIRE': {'country': 'United States', 'format_type': 'US_Regional', 'desc': 'Federal Reserve Wire Transfer'},
    'FEDNOW': {'country': 'United States', 'format_type': 'US_Regional', 'desc': 'FedNow Instant Payment'},
    'ACH': {'country': 'United States', 'format_type': 'US_Regional', 'desc': 'Automated Clearing House Payment'},
    'CHIPS': {'country': 'United States', 'format_type': 'US_Regional', 'desc': 'Clearing House Interbank Payments'},
    'RTP': {'country': 'United States', 'format_type': 'US_Regional', 'desc': 'Real-Time Payments'},
    'SEPA': {'country': 'European Union', 'format_type': 'EU_Regional', 'desc': 'Single Euro Payments Area Transfer'},
    'TARGET2': {'country': 'European Union', 'format_type': 'EU_Regional', 'desc': 'Trans-European Real-Time Settlement'},
    'CHAPS': {'country': 'United Kingdom', 'format_type': 'UK_Regional', 'desc': 'Clearing House Automated Payment'},
    'BACS': {'country': 'United Kingdom', 'format_type': 'UK_Regional', 'desc': 'UK Bulk Payment System'},
    'FPS': {'country': 'United Kingdom', 'format_type': 'UK_Regional', 'desc': 'UK Faster Payments Service'},
    'BOJNET': {'country': 'Japan', 'format_type': 'APAC_Regional', 'desc': 'Bank of Japan Financial Network'},
    'CNAPS': {'country': 'China', 'format_type': 'APAC_Regional', 'desc': 'China National Advanced Payment System'},
    'KFTC': {'country': 'South Korea', 'format_type': 'APAC_Regional', 'desc': 'Korea Financial Telecommunications'},
    'MEPS_PLUS': {'country': 'Singapore', 'format_type': 'APAC_Regional', 'desc': 'MAS Electronic Payment System'},
    'RTGS_HK': {'country': 'Hong Kong', 'format_type': 'APAC_Regional', 'desc': 'Hong Kong Real-Time Gross Settlement'},
    'NPP': {'country': 'Australia', 'format_type': 'APAC_Regional', 'desc': 'New Payments Platform'},
    'UPI': {'country': 'India', 'format_type': 'South_Asia', 'desc': 'Unified Payments Interface'},
    'INSTAPAY': {'country': 'Philippines', 'format_type': 'SE_Asia', 'desc': 'Philippine Instant Payment'},
    'PROMPTPAY': {'country': 'Thailand', 'format_type': 'SE_Asia', 'desc': 'Thailand PromptPay System'},
    'PAYNOW': {'country': 'Singapore', 'format_type': 'APAC_Regional', 'desc': 'Singapore PayNow'},
    'SARIE': {'country': 'Saudi Arabia', 'format_type': 'Middle_East', 'desc': 'Saudi Arabian Riyal Interbank Express'},
    'UAEFTS': {'country': 'United Arab Emirates', 'format_type': 'Middle_East', 'desc': 'UAE Funds Transfer System'},
    'PIX': {'country': 'Brazil', 'format_type': 'LATAM', 'desc': 'Brazilian Instant Payment System'},
}

# Format to Silver table mapping
FORMAT_TO_TABLE = {
    'pain.001': 'stg_pain001', 'pacs.008': 'stg_pacs008', 'camt.053': 'stg_camt053',
    'MT103': 'stg_mt103', 'MT202': 'stg_mt202', 'MT940': 'stg_mt940',
    'FEDWIRE': 'stg_fedwire', 'FEDNOW': 'stg_fednow', 'ACH': 'stg_ach',
    'CHIPS': 'stg_chips', 'RTP': 'stg_rtp', 'SEPA': 'stg_sepa',
    'TARGET2': 'stg_target2', 'CHAPS': 'stg_chaps', 'BACS': 'stg_bacs',
    'FPS': 'stg_fps', 'BOJNET': 'stg_bojnet', 'CNAPS': 'stg_cnaps',
    'KFTC': 'stg_kftc', 'MEPS_PLUS': 'stg_meps_plus', 'RTGS_HK': 'stg_rtgs_hk',
    'NPP': 'stg_npp', 'UPI': 'stg_upi', 'INSTAPAY': 'stg_instapay',
    'PROMPTPAY': 'stg_promptpay', 'PAYNOW': 'stg_paynow', 'SARIE': 'stg_sarie',
    'UAEFTS': 'stg_uaefts', 'PIX': 'stg_pix'
}

# Silver to Gold column mapping
SILVER_TO_GOLD = {
    'msg_id': ('cdm_payment_instruction', 'message_id'),
    'message_id': ('cdm_payment_instruction', 'message_id'),
    'creation_date': ('cdm_payment_instruction', 'creation_datetime'),
    'creation_datetime': ('cdm_payment_instruction', 'creation_datetime'),
    'amount': ('cdm_payment_instruction', 'amount'),
    'currency': ('cdm_payment_instruction', 'currency'),
    'debtor_name': ('cdm_party', 'name'),
    'creditor_name': ('cdm_party', 'name'),
    'debtor_account': ('cdm_account', 'account_number'),
    'creditor_account': ('cdm_account', 'account_number'),
    'debtor_agent_bic': ('cdm_financial_institution', 'bic'),
    'creditor_agent_bic': ('cdm_financial_institution', 'bic'),
    'remittance_info': ('cdm_payment_instruction', 'remittance_info'),
    'end_to_end_id': ('cdm_payment_instruction', 'end_to_end_id'),
    'instruction_id': ('cdm_payment_instruction', 'instruction_id'),
    'purpose_code': ('cdm_payment_instruction', 'purpose_code'),
    'charge_bearer': ('cdm_payment_instruction', 'charge_bearer'),
}

# Gold purpose codes
GOLD_PURPOSE_CODES = {
    'message_id': 'MESSAGE_IDENTIFIER',
    'creation_datetime': 'CREATION_TIMESTAMP',
    'amount': 'PAYMENT_AMOUNT',
    'currency': 'PAYMENT_CURRENCY',
    'name': 'PARTY_IDENTIFICATION',
    'account_number': 'ACCOUNT_IDENTIFIER',
    'bic': 'FINANCIAL_INSTITUTION_ID',
    'remittance_info': 'PAYMENT_REFERENCE',
    'end_to_end_id': 'END_TO_END_TRACKING',
    'instruction_id': 'INSTRUCTION_IDENTIFIER',
    'purpose_code': 'PAYMENT_PURPOSE',
    'charge_bearer': 'CHARGE_ALLOCATION',
}

# System columns
SYSTEM_COLUMNS = {'stg_id', '_raw_id', '_ingested_at', '_batch_id', '_source_file',
                  '_processed_at', 'processed_to_gold_at', 'processing_status',
                  'processing_error', 'source_raw_id'}

SYSTEM_COLUMN_DESCRIPTIONS = {
    '_processed_at': 'Pipeline processing timestamp (System)',
    'processed_to_gold_at': 'Gold promotion timestamp (System)',
    'processing_status': 'Processing status flag (System)',
    'processing_error': 'Error message if processing failed (System)',
    'source_raw_id': 'Reference to source Bronze record (System)',
    'stg_id': 'Silver table primary key (System)',
    '_raw_id': 'Bronze record reference (System)',
    '_ingested_at': 'Ingestion timestamp (System)',
    '_batch_id': 'Batch identifier (System)',
    '_source_file': 'Source filename (System)',
}


def generate_report():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Get Silver table column types
    cur.execute("""
        SELECT table_name, column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = 'silver'
        ORDER BY table_name, ordinal_position
    """)
    silver_schema = {}
    for row in cur.fetchall():
        table_name, col_name, data_type, max_len = row
        type_str = f"{data_type}({max_len})" if max_len else data_type
        if table_name not in silver_schema:
            silver_schema[table_name] = {}
        silver_schema[table_name][col_name] = type_str

    # Get Gold table column types
    cur.execute("""
        SELECT table_name, column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = 'gold'
        ORDER BY table_name, ordinal_position
    """)
    gold_schema = {}
    for row in cur.fetchall():
        table_name, col_name, data_type, max_len = row
        type_str = f"{data_type}({max_len})" if max_len else data_type
        if table_name not in gold_schema:
            gold_schema[table_name] = {}
        gold_schema[table_name][col_name] = type_str

    # Get Gold field mappings from database
    cur.execute("""
        SELECT format_id, silver_column, gold_table, gold_column, mapping_type
        FROM mapping.gold_field_mappings
        WHERE is_active = true
    """)
    gold_mappings_db = {}
    for row in cur.fetchall():
        format_id, silver_col, gold_table, gold_col, mapping_type = row
        gold_mappings_db[(format_id, silver_col)] = {
            'gold_table': gold_table,
            'gold_column': gold_col,
            'mapping_type': mapping_type
        }

    # Get all field mappings from database
    cur.execute("""
        SELECT DISTINCT
            mf.format_id,
            mf.format_name,
            mf.description as format_desc,
            sfm.target_column,
            sfm.source_path,
            sfm.data_type,
            sfm.max_length,
            sfm.is_required,
            sfm.default_value
        FROM mapping.message_formats mf
        JOIN mapping.silver_field_mappings sfm ON mf.format_id = sfm.format_id
        WHERE mf.is_active = true AND sfm.is_active = true
        ORDER BY mf.format_id, sfm.target_column
    """)
    mappings = cur.fetchall()

    # Build report rows
    report_rows = []
    existing_columns = set()

    for row in mappings:
        format_id, format_name, format_desc, target_column, source_path, data_type, max_length, is_required, default_value = row

        meta = STANDARD_METADATA.get(format_id, {'country': 'Unknown', 'format_type': 'Unknown', 'desc': format_desc or ''})
        silver_table = FORMAT_TO_TABLE.get(format_id, f'stg_{format_id.lower().replace(".", "")}')
        silver_table_full = f"silver.{silver_table}"
        silver_type = silver_schema.get(silver_table, {}).get(target_column, f"{data_type}({max_length})" if max_length else data_type)

        # Get Gold mapping from database
        gold_map = gold_mappings_db.get((format_id, target_column), {})
        gold_table = gold_map.get('gold_table', '')
        gold_column = gold_map.get('gold_column', '')
        mapping_type = gold_map.get('mapping_type', '')

        # Get Gold column type
        gold_table_name = gold_table.replace('gold.', '') if gold_table else ''
        gold_type = gold_schema.get(gold_table_name, {}).get(gold_column, '')

        # Determine purpose code
        if mapping_type == 'CDM_CORE':
            gold_purpose = GOLD_PURPOSE_CODES.get(gold_column, 'CDM_CORE')
        elif mapping_type == 'EXTENSION':
            gold_purpose = 'FORMAT_EXTENSION'
        else:
            gold_purpose = ''

        field_desc = f"{target_column.replace('_', ' ').title()} field"
        if is_required:
            field_desc += " (Required)"

        allowed_values = f"Default: {default_value}" if default_value else ''

        report_rows.append({
            'standard_name': format_id,
            'country': meta['country'],
            'message_format': meta['format_type'],
            'message_format_desc': meta['desc'],
            'std_field_name': target_column,
            'std_field_desc': field_desc,
            'std_field_type': f"{data_type}({max_length})" if max_length else (data_type or 'varchar'),
            'std_field_allowed': allowed_values,
            'std_field_path': source_path or target_column,
            'bronze_table': 'bronze.raw_payment_messages',
            'bronze_column': 'raw_content',
            'silver_table': silver_table_full,
            'silver_column': target_column,
            'silver_type': silver_type,
            'gold_table': gold_table,
            'gold_column': gold_column,
            'gold_type': gold_type,
            'gold_purpose_code': gold_purpose
        })
        existing_columns.add((format_id, target_column))

    # Add any columns in Silver tables not in mappings
    for format_id, table_name in FORMAT_TO_TABLE.items():
        meta = STANDARD_METADATA.get(format_id, {'country': 'Unknown', 'format_type': 'Unknown', 'desc': ''})

        if table_name not in silver_schema:
            continue

        for col_name, col_type in silver_schema[table_name].items():
            if (format_id, col_name) not in existing_columns:
                is_system = col_name.startswith('_') or col_name in SYSTEM_COLUMNS
                field_desc = SYSTEM_COLUMN_DESCRIPTIONS.get(col_name, f"{col_name.replace('_', ' ').title()} field")

                # Get Gold mapping from database
                gold_map = gold_mappings_db.get((format_id, col_name), {})
                gold_table = gold_map.get('gold_table', '')
                gold_column = gold_map.get('gold_column', '')
                mapping_type = gold_map.get('mapping_type', '')

                gold_table_name = gold_table.replace('gold.', '') if gold_table else ''
                gold_type_val = gold_schema.get(gold_table_name, {}).get(gold_column, '')

                if is_system:
                    gold_purpose = 'SYSTEM_METADATA'
                elif mapping_type == 'CDM_CORE':
                    gold_purpose = 'CDM_CORE'
                elif mapping_type == 'EXTENSION':
                    gold_purpose = 'FORMAT_EXTENSION'
                else:
                    gold_purpose = ''

                report_rows.append({
                    'standard_name': format_id,
                    'country': meta['country'],
                    'message_format': meta['format_type'],
                    'message_format_desc': meta['desc'],
                    'std_field_name': col_name,
                    'std_field_desc': field_desc,
                    'std_field_type': col_type,
                    'std_field_allowed': '',
                    'std_field_path': col_name if is_system else '(derived from raw)',
                    'bronze_table': 'bronze.raw_payment_messages' if not is_system else '(system)',
                    'bronze_column': 'raw_content' if not is_system else '(system)',
                    'silver_table': f'silver.{table_name}',
                    'silver_column': col_name,
                    'silver_type': col_type,
                    'gold_table': gold_table,
                    'gold_column': gold_column,
                    'gold_type': gold_type_val,
                    'gold_purpose_code': gold_purpose
                })
                existing_columns.add((format_id, col_name))

    conn.close()

    # Sort by format and column
    report_rows.sort(key=lambda r: (r['standard_name'], r['silver_column']))

    return report_rows


def write_report(report_rows, output_file):
    headers = [
        'Standard Name', 'Country', 'Message Format', 'Message Format Description',
        'Standard Field Name', 'Standard Field Description', 'Standard Field Data Type',
        'Standard Field Allowed Values', 'Standard Field Path',
        'Bronze Table', 'Bronze Column',
        'Silver Table', 'Silver Column', 'Silver Data Type',
        'Gold Table', 'Gold Column', 'Gold Data Type', 'Gold Purpose Code'
    ]

    field_keys = [
        'standard_name', 'country', 'message_format', 'message_format_desc',
        'std_field_name', 'std_field_desc', 'std_field_type',
        'std_field_allowed', 'std_field_path',
        'bronze_table', 'bronze_column',
        'silver_table', 'silver_column', 'silver_type',
        'gold_table', 'gold_column', 'gold_type', 'gold_purpose_code'
    ]

    output_lines = ['|'.join(headers)]
    for row in report_rows:
        values = [str(row.get(k, '') or '') for k in field_keys]
        output_lines.append('|'.join(values))

    with open(output_file, 'w') as f:
        f.write('\n'.join(output_lines))

    return len(output_lines)


def main():
    print("=" * 80)
    print("Generating Field Mapping Report")
    print("=" * 80)

    report_rows = generate_report()

    output_file = os.path.join(os.path.dirname(__file__), '../../docs/field_mapping_report.psv')
    output_file = os.path.abspath(output_file)

    line_count = write_report(report_rows, output_file)

    print(f"\nReport saved to: {output_file}")
    print(f"Total rows: {line_count} (1 header + {len(report_rows)} data)")

    # Print summary
    format_counts = {}
    for row in report_rows:
        fmt = row['standard_name']
        format_counts[fmt] = format_counts.get(fmt, 0) + 1

    print(f"\n--- Summary by Format ---")
    for fmt in sorted(format_counts.keys()):
        print(f"  {fmt}: {format_counts[fmt]} fields")

    print(f"\n  TOTAL: {len(report_rows)} fields across {len(format_counts)} formats")
    print(f"\nGenerated at: {datetime.now().isoformat()}")


if __name__ == '__main__':
    main()
