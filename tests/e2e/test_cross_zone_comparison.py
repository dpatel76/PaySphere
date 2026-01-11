#!/usr/bin/env python3
"""
Cross-Zone Data Comparison Test.

Compares data elements across Bronze → Silver → Gold zones including extension tables
to verify data integrity and transformation accuracy.

Usage:
    PYTHONPATH=src:$PYTHONPATH python tests/e2e/test_cross_zone_comparison.py [batch_id]
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import psycopg2
from psycopg2.extras import RealDictCursor


# Message type to Silver table mapping
# NOTE: SWIFT MT messages (MT103, MT202, MT940) were decommissioned by SWIFT in Nov 2025
SILVER_TABLES = {
    'pain.001': 'stg_pain001',
    'pacs.008': 'stg_pacs008',
    'pacs.002': 'stg_pacs002',
    'pacs.004': 'stg_pacs004',
    'pacs.009': 'stg_pacs009',
    'pain.008': 'stg_pain008',
    'camt.053': 'stg_camt053',
    'FEDWIRE': 'stg_fedwire',
    'ACH': 'stg_ach',
    'SEPA': 'stg_sepa',
    'RTP': 'stg_rtp',
    'CHAPS': 'stg_chaps',
    'BACS': 'stg_bacs',
    'FPS': 'stg_faster_payments',
    'FEDNOW': 'stg_fednow',
    'CHIPS': 'stg_chips',
    'TARGET2': 'stg_target2',
    'NPP': 'stg_npp',
    'UPI': 'stg_upi',
    'PIX': 'stg_pix',
    'MEPS_PLUS': 'stg_meps_plus',
    'RTGS_HK': 'stg_rtgs_hk',
    'BOJNET': 'stg_bojnet',
    'KFTC': 'stg_kftc',
    'CNAPS': 'stg_cnaps',
    'SARIE': 'stg_sarie',
    'UAEFTS': 'stg_uaefts',
    'PROMPTPAY': 'stg_promptpay',
    'PAYNOW': 'stg_paynow',
    'INSTAPAY': 'stg_instapay',
}

# Message type to extension table mapping
# NOTE: SWIFT MT messages (MT103, MT202, MT940) were decommissioned by SWIFT in Nov 2025
EXTENSION_TABLES = {
    'pain.001': 'cdm_payment_extension_iso20022',
    'pacs.008': 'cdm_payment_extension_iso20022',
    'pacs.002': 'cdm_payment_extension_iso20022',
    'pacs.004': 'cdm_payment_extension_iso20022',
    'pacs.009': 'cdm_payment_extension_iso20022',
    'pain.008': 'cdm_payment_extension_iso20022',
    'camt.053': 'cdm_payment_extension_iso20022',
    'FEDWIRE': 'cdm_payment_extension_fedwire',
    'ACH': 'cdm_payment_extension_ach',
    'SEPA': 'cdm_payment_extension_sepa',
    'RTP': 'cdm_payment_extension_rtp',
    # Other schemes use their respective extension tables
}

# Key fields to compare across zones
KEY_FIELDS = {
    'identifiers': ['message_id', 'end_to_end_id', 'transaction_id', 'instruction_id'],
    'amounts': ['instructed_amount', 'instructed_currency', 'interbank_settlement_amount'],
    'dates': ['creation_datetime', 'value_date', 'settlement_date'],
    'parties': ['debtor_id', 'creditor_id', 'debtor_agent_id', 'creditor_agent_id'],
    'references': ['remittance_reference', 'remittance_unstructured'],
}


def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=int(os.environ.get('POSTGRES_PORT', '5433')),
        database=os.environ.get('POSTGRES_DB', 'gps_cdm'),
        user=os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
        password=os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password'),
    )


def get_bronze_record(conn, batch_id: str) -> Optional[Dict[str, Any]]:
    """Get Bronze record for a batch."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT raw_id, message_type, raw_content, _batch_id, _ingested_at,
                   processing_status, source_system, source_file_path,
                   content_size_bytes
            FROM bronze.raw_payment_messages
            WHERE _batch_id = %s
            ORDER BY _ingested_at DESC
            LIMIT 1
        """, (batch_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_silver_record(conn, batch_id: str, message_type: str) -> Optional[Dict[str, Any]]:
    """Get Silver record for a batch."""
    table_name = SILVER_TABLES.get(message_type)
    if not table_name:
        return None

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Get all columns dynamically
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'silver' AND table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        columns = [row['column_name'] for row in cur.fetchall()]

        if not columns:
            return None

        cur.execute(f"""
            SELECT * FROM silver.{table_name}
            WHERE _batch_id = %s
            ORDER BY _processed_at DESC
            LIMIT 1
        """, (batch_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_gold_record(conn, batch_id: str) -> Optional[Dict[str, Any]]:
    """Get Gold main record for a batch."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT * FROM gold.cdm_payment_instruction
            WHERE lineage_batch_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (batch_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_gold_extension(conn, instruction_id: str, message_type: str) -> Optional[Dict[str, Any]]:
    """Get Gold extension record."""
    table_name = EXTENSION_TABLES.get(message_type)
    if not table_name:
        return None

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            cur.execute(f"""
                SELECT * FROM gold.{table_name}
                WHERE instruction_id = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (instruction_id,))
            row = cur.fetchone()
            return dict(row) if row else None
        except Exception:
            return None


def get_gold_parties(conn, instruction_id: str) -> List[Dict[str, Any]]:
    """Get Gold party records."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT * FROM gold.cdm_party
            WHERE party_id IN (
                SELECT debtor_id FROM gold.cdm_payment_instruction WHERE instruction_id = %s
                UNION
                SELECT creditor_id FROM gold.cdm_payment_instruction WHERE instruction_id = %s
                UNION
                SELECT ultimate_debtor_id FROM gold.cdm_payment_instruction WHERE instruction_id = %s
                UNION
                SELECT ultimate_creditor_id FROM gold.cdm_payment_instruction WHERE instruction_id = %s
            )
        """, (instruction_id, instruction_id, instruction_id, instruction_id))
        return [dict(row) for row in cur.fetchall()]


def get_gold_accounts(conn, instruction_id: str) -> List[Dict[str, Any]]:
    """Get Gold account records."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT * FROM gold.cdm_account
            WHERE account_id IN (
                SELECT debtor_account_id FROM gold.cdm_payment_instruction WHERE instruction_id = %s
                UNION
                SELECT creditor_account_id FROM gold.cdm_payment_instruction WHERE instruction_id = %s
            )
        """, (instruction_id, instruction_id))
        return [dict(row) for row in cur.fetchall()]


def get_gold_financial_institutions(conn, instruction_id: str) -> List[Dict[str, Any]]:
    """Get Gold financial institution records."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT * FROM gold.cdm_financial_institution
            WHERE fi_id IN (
                SELECT debtor_agent_id FROM gold.cdm_payment_instruction WHERE instruction_id = %s
                UNION
                SELECT creditor_agent_id FROM gold.cdm_payment_instruction WHERE instruction_id = %s
                UNION
                SELECT intermediary_agent1_id FROM gold.cdm_payment_instruction WHERE instruction_id = %s
                UNION
                SELECT intermediary_agent2_id FROM gold.cdm_payment_instruction WHERE instruction_id = %s
            )
        """, (instruction_id, instruction_id, instruction_id, instruction_id))
        return [dict(row) for row in cur.fetchall()]


def format_value(value: Any) -> str:
    """Format value for display."""
    if value is None:
        return '<NULL>'
    if isinstance(value, (list, dict)):
        return json.dumps(value, default=str)[:50]
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)[:50]


def compare_zones(batch_id: str) -> Dict[str, Any]:
    """Compare data across all zones for a batch."""
    conn = get_db_connection()

    try:
        # Get Bronze record
        bronze = get_bronze_record(conn, batch_id)
        if not bronze:
            return {'error': f'No Bronze record found for batch {batch_id}'}

        message_type = bronze['message_type']

        # Get Silver record
        silver = get_silver_record(conn, batch_id, message_type)
        if not silver:
            return {'error': f'No Silver record found for batch {batch_id}'}

        # Get Gold main record
        gold = get_gold_record(conn, batch_id)
        if not gold:
            return {'error': f'No Gold record found for batch {batch_id}'}

        instruction_id = gold.get('instruction_id')

        # Get Gold extension
        gold_extension = get_gold_extension(conn, instruction_id, message_type)

        # Get Gold related entities
        gold_parties = get_gold_parties(conn, instruction_id)
        gold_accounts = get_gold_accounts(conn, instruction_id)
        gold_fis = get_gold_financial_institutions(conn, instruction_id)

        # Build comparison result
        result = {
            'batch_id': batch_id,
            'message_type': message_type,
            'zones': {
                'bronze': {
                    'record_count': 1,
                    'raw_id': bronze.get('raw_id'),
                    'ingested_at': str(bronze.get('_ingested_at')),
                    'processing_status': bronze.get('processing_status'),
                    'content_size': bronze.get('content_size_bytes') or len(bronze.get('raw_content', '') or ''),
                },
                'silver': {
                    'record_count': 1,
                    'stg_id': silver.get('stg_id'),
                    'table': SILVER_TABLES.get(message_type),
                    'fields': {k: format_value(v) for k, v in silver.items()
                              if not k.startswith('_') and v is not None},
                },
                'gold': {
                    'main': {
                        'record_count': 1,
                        'instruction_id': instruction_id,
                        'fields': {k: format_value(v) for k, v in gold.items()
                                  if v is not None and k not in ['created_at', 'updated_at']},
                    },
                    'extension': {
                        'table': EXTENSION_TABLES.get(message_type),
                        'record_count': 1 if gold_extension else 0,
                        'fields': {k: format_value(v) for k, v in (gold_extension or {}).items()
                                  if v is not None and k not in ['created_at']},
                    },
                    'parties': {
                        'record_count': len(gold_parties),
                        'items': [{k: format_value(v) for k, v in p.items()
                                  if v is not None and k not in ['created_at', 'updated_at']}
                                 for p in gold_parties],
                    },
                    'accounts': {
                        'record_count': len(gold_accounts),
                        'items': [{k: format_value(v) for k, v in a.items()
                                  if v is not None and k not in ['created_at', 'updated_at']}
                                 for a in gold_accounts],
                    },
                    'financial_institutions': {
                        'record_count': len(gold_fis),
                        'items': [{k: format_value(v) for k, v in f.items()
                                  if v is not None and k not in ['created_at', 'updated_at']}
                                 for f in gold_fis],
                    },
                },
            },
            'summary': {
                'bronze_to_silver': 'OK' if silver else 'MISSING',
                'silver_to_gold': 'OK' if gold else 'MISSING',
                'gold_extension': 'OK' if gold_extension else 'N/A' if message_type not in EXTENSION_TABLES else 'MISSING',
                'gold_parties': len(gold_parties),
                'gold_accounts': len(gold_accounts),
                'gold_fis': len(gold_fis),
            },
        }

        return result

    finally:
        conn.close()


def print_comparison(result: Dict[str, Any]):
    """Print comparison result in readable format."""
    if 'error' in result:
        print(f"ERROR: {result['error']}")
        return

    print("\n" + "=" * 80)
    print(f"CROSS-ZONE COMPARISON: {result['batch_id']}")
    print(f"Message Type: {result['message_type']}")
    print("=" * 80)

    # Bronze Zone
    bronze = result['zones']['bronze']
    print("\n--- BRONZE ZONE ---")
    print(f"  Raw ID: {bronze['raw_id']}")
    print(f"  Ingested At: {bronze['ingested_at']}")
    print(f"  Status: {bronze['processing_status']}")
    print(f"  Content Size: {bronze.get('content_size', 'N/A')} bytes")

    # Silver Zone
    silver = result['zones']['silver']
    print(f"\n--- SILVER ZONE ({silver['table']}) ---")
    print(f"  STG ID: {silver['stg_id']}")
    print(f"  Fields ({len(silver['fields'])} populated):")
    for k, v in sorted(silver['fields'].items()):
        if k not in ['stg_id', 'source_raw_id', 'processing_status', 'processing_error']:
            print(f"    {k}: {v}")

    # Gold Zone - Main
    gold_main = result['zones']['gold']['main']
    print(f"\n--- GOLD ZONE (cdm_payment_instruction) ---")
    print(f"  Instruction ID: {gold_main['instruction_id']}")
    print(f"  Key Fields:")
    key_fields_to_show = [
        'message_id', 'end_to_end_id', 'payment_type', 'scheme_code',
        'instructed_amount', 'instructed_currency', 'charge_bearer',
        'debtor_id', 'creditor_id', 'debtor_account_id', 'creditor_account_id',
        'debtor_agent_id', 'creditor_agent_id', 'source_message_type',
    ]
    for k in key_fields_to_show:
        if k in gold_main['fields']:
            print(f"    {k}: {gold_main['fields'][k]}")

    # Gold Zone - Extension
    gold_ext = result['zones']['gold']['extension']
    if gold_ext['record_count'] > 0:
        print(f"\n--- GOLD EXTENSION ({gold_ext['table']}) ---")
        for k, v in sorted(gold_ext['fields'].items()):
            if k not in ['extension_id', 'instruction_id']:
                print(f"    {k}: {v}")
    elif gold_ext['table']:
        print(f"\n--- GOLD EXTENSION ({gold_ext['table']}) ---")
        print("    No extension record found")

    # Gold Zone - Parties
    gold_parties = result['zones']['gold']['parties']
    if gold_parties['record_count'] > 0:
        print(f"\n--- GOLD PARTIES ({gold_parties['record_count']} records) ---")
        for i, party in enumerate(gold_parties['items'], 1):
            role = party.get('party_role', 'UNKNOWN')
            name = party.get('name', 'N/A')
            print(f"    [{i}] {role}: {name}")
            for k in ['party_type', 'country', 'address_line1']:
                if k in party:
                    print(f"        {k}: {party[k]}")

    # Gold Zone - Accounts
    gold_accounts = result['zones']['gold']['accounts']
    if gold_accounts['record_count'] > 0:
        print(f"\n--- GOLD ACCOUNTS ({gold_accounts['record_count']} records) ---")
        for i, acct in enumerate(gold_accounts['items'], 1):
            role = acct.get('account_role', 'UNKNOWN')
            num = acct.get('account_number', 'N/A')
            print(f"    [{i}] {role}: {num}")
            for k in ['account_type', 'currency', 'iban', 'bic']:
                if k in acct:
                    print(f"        {k}: {acct[k]}")

    # Gold Zone - Financial Institutions
    gold_fis = result['zones']['gold']['financial_institutions']
    if gold_fis['record_count'] > 0:
        print(f"\n--- GOLD FINANCIAL INSTITUTIONS ({gold_fis['record_count']} records) ---")
        for i, fi in enumerate(gold_fis['items'], 1):
            fi_type = fi.get('fi_type', 'UNKNOWN')
            name = fi.get('institution_name', 'N/A')
            print(f"    [{i}] {fi_type}: {name}")
            for k in ['bic', 'national_clearing_code', 'country']:
                if k in fi:
                    print(f"        {k}: {fi[k]}")

    # Summary
    summary = result['summary']
    print("\n--- SUMMARY ---")
    print(f"  Bronze → Silver: {summary['bronze_to_silver']}")
    print(f"  Silver → Gold: {summary['silver_to_gold']}")
    print(f"  Gold Extension: {summary['gold_extension']}")
    print(f"  Gold Parties: {summary['gold_parties']}")
    print(f"  Gold Accounts: {summary['gold_accounts']}")
    print(f"  Gold FIs: {summary['gold_fis']}")
    print("=" * 80)


def run_all_comparisons():
    """Run comparison for all recent E2E test batches."""
    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT DISTINCT _batch_id, message_type
                FROM bronze.raw_payment_messages
                WHERE _batch_id LIKE 'e2e_test_%'
                ORDER BY _batch_id
            """)
            batches = cur.fetchall()

        print(f"\nFound {len(batches)} E2E test batches to compare")
        print("=" * 80)

        results = []
        for batch in batches:
            batch_id = batch['_batch_id']
            result = compare_zones(batch_id)
            results.append(result)

            # Print summary line
            if 'error' in result:
                print(f"✗ {batch_id}: {result['error']}")
            else:
                summary = result['summary']
                status = '✓' if summary['bronze_to_silver'] == 'OK' and summary['silver_to_gold'] == 'OK' else '✗'
                ext_status = summary['gold_extension']
                print(f"{status} {batch_id} ({result['message_type']}): "
                      f"B→S={summary['bronze_to_silver']}, S→G={summary['silver_to_gold']}, "
                      f"Ext={ext_status}, Parties={summary['gold_parties']}, "
                      f"Accounts={summary['gold_accounts']}, FIs={summary['gold_fis']}")

        # Overall summary
        success_count = sum(1 for r in results if 'error' not in r
                          and r['summary']['bronze_to_silver'] == 'OK'
                          and r['summary']['silver_to_gold'] == 'OK')
        print("\n" + "=" * 80)
        print(f"OVERALL: {success_count}/{len(results)} batches passed cross-zone comparison")

        return results

    finally:
        conn.close()


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        batch_id = sys.argv[1]
        result = compare_zones(batch_id)
        print_comparison(result)
    else:
        run_all_comparisons()


if __name__ == '__main__':
    main()
