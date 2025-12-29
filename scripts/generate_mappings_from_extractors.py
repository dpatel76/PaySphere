#!/usr/bin/env python3
"""
Generate Silver/Gold field mappings from existing extractors.

This script introspects the existing extractor modules and generates
mapping.silver_field_mappings and mapping.gold_field_mappings entries
for all message types that don't have mappings yet.
"""

import os
import sys
import json
import uuid
import psycopg2
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gps_cdm.message_formats.base import ExtractorRegistry

# Import ALL extractor modules to trigger registration
from gps_cdm.message_formats import pain001
from gps_cdm.message_formats import pacs008
from gps_cdm.message_formats import mt103
from gps_cdm.message_formats import mt202
from gps_cdm.message_formats import mt940
from gps_cdm.message_formats import fedwire
from gps_cdm.message_formats import ach
from gps_cdm.message_formats import rtp
from gps_cdm.message_formats import sepa
from gps_cdm.message_formats import bacs
from gps_cdm.message_formats import chaps
from gps_cdm.message_formats import fps
from gps_cdm.message_formats import chips
from gps_cdm.message_formats import fednow
from gps_cdm.message_formats import npp
from gps_cdm.message_formats import pix
from gps_cdm.message_formats import upi
from gps_cdm.message_formats import instapay
from gps_cdm.message_formats import paynow
from gps_cdm.message_formats import promptpay
from gps_cdm.message_formats import target2
from gps_cdm.message_formats import sarie
from gps_cdm.message_formats import uaefts
from gps_cdm.message_formats import rtgs_hk
from gps_cdm.message_formats import meps_plus
from gps_cdm.message_formats import cnaps
from gps_cdm.message_formats import bojnet
from gps_cdm.message_formats import kftc
from gps_cdm.message_formats import camt053


def get_db_connection():
    """Get PostgreSQL connection."""
    return psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=int(os.environ.get('POSTGRES_PORT', 5433)),
        database=os.environ.get('POSTGRES_DB', 'gps_cdm'),
        user=os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
        password=os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password')
    )


def infer_data_type(column_name: str, value_sample=None) -> str:
    """Infer PostgreSQL data type from column name."""
    col = column_name.lower()

    if col in ('stg_id', 'raw_id', '_batch_id', 'batch_id'):
        return 'VARCHAR'
    if 'amount' in col or 'sum' in col or col == 'amount':
        return 'DECIMAL'
    if 'count' in col or 'number' in col:
        return 'INTEGER'
    if 'date' in col or 'time' in col or col.endswith('_at'):
        return 'TIMESTAMP'
    if col.startswith('is_') or col.startswith('has_'):
        return 'BOOLEAN'
    return 'VARCHAR'


def infer_max_length(column_name: str, extract_args: str = None) -> int:
    """Infer max length from column name or extractor truncation."""
    col = column_name.lower()

    # Common patterns from extractors
    if 'id' in col or 'code' in col:
        return 35
    if 'name' in col:
        return 140
    if 'address' in col or 'details' in col:
        return 500
    if 'iban' in col or 'account' in col:
        return 34
    if 'bic' in col:
        return 11
    if 'currency' in col:
        return 3
    if 'country' in col:
        return 2
    return 255


def infer_source_path(column_name: str, format_id: str) -> str:
    """Infer JSON source path from column name (camelCase convention)."""
    # Map common silver columns to source paths
    mappings = {
        'stg_id': '_GENERATED_UUID',
        'raw_id': '_RAW_ID',
        '_batch_id': '_BATCH_ID',
        'message_type': 'messageType',
        'msg_id': 'messageId',
        'creation_date_time': 'creationDateTime',
        'number_of_transactions': 'numberOfTransactions',
        'control_sum': 'controlSum',
        'debtor_name': 'debtor.name',
        'debtor_iban': 'debtorAccount.iban',
        'debtor_account': 'debtorAccount.iban',
        'debtor_bic': 'debtorAgent.bic',
        'debtor_country': 'debtor.country',
        'debtor_address': 'debtor.address',
        'creditor_name': 'creditor.name',
        'creditor_iban': 'creditorAccount.iban',
        'creditor_account': 'creditorAccount.iban',
        'creditor_bic': 'creditorAgent.bic',
        'creditor_country': 'creditor.country',
        'creditor_address': 'creditor.address',
        'instructed_amount': 'instructedAmount',
        'instructed_currency': 'instructedCurrency',
        'amount': 'amount',
        'currency': 'currency',
        'charge_bearer': 'chargeBearer',
        'end_to_end_id': 'endToEndId',
        'payment_method': 'paymentMethod',
        'remittance_info': 'remittanceInfo',
        'sender_reference': 'senderReference',
        'value_date': 'valueDate',
        'originator_name': 'originatorName',
        'originator_account': 'originatorAccount',
        'originator_address': 'originatorAddress',
        'beneficiary_name': 'beneficiaryName',
        'beneficiary_account': 'beneficiaryAccount',
        'beneficiary_address': 'beneficiaryAddress',
        'originator_bank': 'originatorBank',
        'beneficiary_bank': 'beneficiaryBank',
        'intermediary_bank': 'intermediaryBank',
    }

    if column_name in mappings:
        return mappings[column_name]

    # Convert snake_case to camelCase
    parts = column_name.split('_')
    if len(parts) == 1:
        return column_name
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])


def generate_silver_mappings(cursor, format_id: str, extractor) -> int:
    """Generate silver field mappings for an extractor."""
    try:
        columns = extractor.get_silver_columns()
    except Exception as e:
        print(f"  Error getting columns for {format_id}: {e}")
        return 0

    inserted = 0
    for ordinal, column in enumerate(columns, 1):
        data_type = infer_data_type(column)
        max_length = infer_max_length(column) if data_type == 'VARCHAR' else None
        source_path = infer_source_path(column, format_id)
        is_required = column in ('stg_id', 'raw_id', '_batch_id')

        try:
            # mapping_id is auto-generated SERIAL, don't include it
            cursor.execute("""
                INSERT INTO mapping.silver_field_mappings (
                    format_id, target_column, source_path,
                    data_type, max_length, is_required, ordinal_position,
                    is_active, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, NOW(), NOW())
                ON CONFLICT (format_id, target_column)
                DO NOTHING
            """, (
                format_id, column, source_path,
                data_type, max_length, is_required, ordinal
            ))
            if cursor.rowcount > 0:
                inserted += 1
        except Exception as e:
            print(f"    Error inserting {column}: {e}")
            cursor.connection.rollback()

    return inserted


# Gold entity to table/column mappings
GOLD_ENTITY_MAPPINGS = {
    'payment_instruction': {
        'table': 'cdm_payment_instruction',
        'columns': [
            ('payment_id', 'end_to_end_id', 'end_to_end_id'),
            ('message_type', 'message_type', 'message_type'),
            ('instructed_amount', 'amount', 'amount'),
            ('instructed_currency', 'currency', 'currency'),
            ('charge_bearer', 'charge_bearer', 'charge_bearer'),
            ('payment_method', 'payment_method', 'payment_method'),
            ('remittance_info', 'remittance_info', 'remittance_info'),
            ('creation_datetime', 'creation_date_time', 'creation_date_time'),
            ('value_date', 'value_date', 'value_date'),
        ]
    },
    'party_debtor': {
        'table': 'cdm_party',
        'entity_role': 'DEBTOR',
        'columns': [
            ('name', 'debtor_name', 'debtor_name'),
            ('country', 'debtor_country', 'debtor_country'),
        ]
    },
    'party_creditor': {
        'table': 'cdm_party',
        'entity_role': 'CREDITOR',
        'columns': [
            ('name', 'creditor_name', 'creditor_name'),
            ('country', 'creditor_country', 'creditor_country'),
        ]
    },
    'account_debtor': {
        'table': 'cdm_account',
        'entity_role': 'DEBTOR',
        'columns': [
            ('account_number', 'debtor_iban', 'debtor_account'),
            ('account_type', None, None),
            ('currency', 'currency', 'currency'),
        ]
    },
    'account_creditor': {
        'table': 'cdm_account',
        'entity_role': 'CREDITOR',
        'columns': [
            ('account_number', 'creditor_iban', 'creditor_account'),
            ('account_type', None, None),
            ('currency', 'currency', 'currency'),
        ]
    },
    'fi_debtor_agent': {
        'table': 'cdm_financial_institution',
        'entity_role': 'DEBTOR_AGENT',
        'columns': [
            ('bic', 'debtor_bic', 'debtor_agent_bic'),
            ('name', 'debtor_agent_name', 'debtor_agent_name'),
            ('country', 'debtor_agent_country', 'debtor_agent_country'),
        ]
    },
    'fi_creditor_agent': {
        'table': 'cdm_financial_institution',
        'entity_role': 'CREDITOR_AGENT',
        'columns': [
            ('bic', 'creditor_bic', 'creditor_agent_bic'),
            ('name', 'creditor_agent_name', 'creditor_agent_name'),
            ('country', 'creditor_agent_country', 'creditor_agent_country'),
        ]
    },
}


def generate_gold_mappings(cursor, format_id: str, extractor) -> int:
    """Generate gold field mappings for an extractor."""
    try:
        columns = extractor.get_silver_columns()
    except Exception as e:
        print(f"  Error getting columns for {format_id}: {e}")
        return 0

    inserted = 0

    # Generate gold mappings based on available silver columns
    for entity_name, entity_def in GOLD_ENTITY_MAPPINGS.items():
        gold_table = entity_def['table']
        entity_role = entity_def.get('entity_role')

        for ordinal, (gold_col, silver_col, alt_silver_col) in enumerate(entity_def['columns'], 1):
            # Check if silver column exists
            source_col = silver_col if silver_col in columns else (alt_silver_col if alt_silver_col in columns else None)

            if not source_col and silver_col is None:
                continue  # Optional mapping

            if source_col:
                try:
                    # mapping_id is auto-generated SERIAL
                    # Unique constraint is on (format_id, gold_table, gold_column, entity_role)
                    cursor.execute("""
                        INSERT INTO mapping.gold_field_mappings (
                            format_id, gold_table, gold_column,
                            source_expression, entity_role, data_type,
                            ordinal_position, is_active, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, NOW(), NOW())
                        ON CONFLICT (format_id, gold_table, gold_column, entity_role)
                        DO NOTHING
                    """, (
                        format_id, gold_table, gold_col,
                        source_col, entity_role, infer_data_type(gold_col),
                        ordinal
                    ))
                    if cursor.rowcount > 0:
                        inserted += 1
                except Exception as e:
                    print(f"    Error inserting gold {gold_col}: {e}")
                    cursor.connection.rollback()

    return inserted


def ensure_message_format(cursor, format_id: str, extractor) -> bool:
    """Ensure message format exists in mapping.message_formats."""
    silver_table = getattr(extractor, 'SILVER_TABLE', f"stg_{format_id.lower().replace('.', '_')}")

    cursor.execute("""
        INSERT INTO mapping.message_formats (
            format_id, format_name, format_category, silver_table,
            bronze_table, is_active, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, TRUE, NOW(), NOW())
        ON CONFLICT (format_id) DO UPDATE SET
            silver_table = EXCLUDED.silver_table,
            updated_at = NOW()
    """, (
        format_id, format_id, 'PAYMENT', silver_table, 'raw_payment_messages'
    ))
    return True


def main():
    """Generate mappings for all registered extractors."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all registered extractors
    extractors = ExtractorRegistry._extractors

    # Find unique extractors (some are registered with multiple aliases)
    seen_types = set()
    unique_extractors = []

    for format_id, extractor in extractors.items():
        msg_type = getattr(extractor, 'MESSAGE_TYPE', format_id)
        if msg_type not in seen_types:
            seen_types.add(msg_type)
            unique_extractors.append((format_id, extractor))

    print(f"Found {len(unique_extractors)} unique extractors")
    print("=" * 60)

    # Check which formats already have mappings
    cursor.execute("""
        SELECT format_id,
               (SELECT COUNT(*) FROM mapping.silver_field_mappings s WHERE s.format_id = m.format_id AND s.is_active) as silver_count
        FROM mapping.message_formats m
        WHERE m.is_active = TRUE
    """)
    existing = {row[0]: row[1] for row in cursor.fetchall()}

    total_silver = 0
    total_gold = 0

    for format_id, extractor in unique_extractors:
        # Use MESSAGE_TYPE if available (canonical name)
        canonical_id = getattr(extractor, 'MESSAGE_TYPE', format_id)

        if existing.get(canonical_id, 0) > 0:
            print(f"[SKIP] {canonical_id}: already has {existing[canonical_id]} silver mappings")
            continue

        print(f"[GEN] {canonical_id}:")

        # Ensure format exists
        ensure_message_format(cursor, canonical_id, extractor)

        # Generate silver mappings
        silver_count = generate_silver_mappings(cursor, canonical_id, extractor)
        print(f"  - Silver mappings: {silver_count}")
        total_silver += silver_count

        # Generate gold mappings
        gold_count = generate_gold_mappings(cursor, canonical_id, extractor)
        print(f"  - Gold mappings: {gold_count}")
        total_gold += gold_count

    conn.commit()

    print("=" * 60)
    print(f"Total new silver mappings: {total_silver}")
    print(f"Total new gold mappings: {total_gold}")

    # Show final summary
    cursor.execute("""
        SELECT mf.format_id,
               (SELECT COUNT(DISTINCT target_column) FROM mapping.silver_field_mappings sfm WHERE sfm.format_id = mf.format_id AND sfm.is_active) as silver_mappings,
               (SELECT COUNT(DISTINCT gold_column) FROM mapping.gold_field_mappings gfm WHERE gfm.format_id = mf.format_id AND gfm.is_active) as gold_mappings
        FROM mapping.message_formats mf
        WHERE mf.is_active = true
        ORDER BY silver_mappings DESC, format_id
    """)

    print("\nFinal mapping counts:")
    print("-" * 50)
    print(f"{'Format':<15} {'Silver':<10} {'Gold':<10}")
    print("-" * 50)
    for row in cursor.fetchall():
        print(f"{row[0]:<15} {row[1]:<10} {row[2]:<10}")

    conn.close()


if __name__ == '__main__':
    main()
