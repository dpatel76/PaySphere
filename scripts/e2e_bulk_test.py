#!/usr/bin/env python3
"""
GPS CDM - Optimized E2E Bulk Testing Script
============================================

Publishes all test messages simultaneously, tracks IDs through each zone,
and performs bulk validation using dynamic mappings.

Usage:
    python scripts/e2e_bulk_test.py [--formats FORMAT1,FORMAT2,...] [--timeout 60]
"""

import os
import sys
import json
import uuid
import time
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import psycopg2
from psycopg2.extras import RealDictCursor

# Format list will be loaded from database
ALL_FORMATS = []  # Populated from database

def get_all_formats_from_db() -> List[str]:
    """Get all active format IDs from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT format_id FROM mapping.message_formats
        WHERE is_active = true
        ORDER BY format_category, format_id
    """)
    formats = [row[0] for row in cursor.fetchall()]
    conn.close()
    return formats

@dataclass
class TestResult:
    """Result for a single format test."""
    format_id: str
    batch_id: str
    raw_id: str = None
    stg_id: str = None
    instruction_id: str = None
    bronze_status: str = 'PENDING'
    silver_status: str = 'PENDING'
    gold_status: str = 'PENDING'
    bronze_fields: int = 0
    silver_fields: int = 0
    gold_fields: int = 0
    silver_non_null: int = 0
    gold_non_null: int = 0
    error: str = None
    duration_ms: float = 0

@dataclass
class TestSummary:
    """Summary of all test results."""
    total: int = 0
    bronze_pass: int = 0
    silver_pass: int = 0
    gold_pass: int = 0
    failed: List[str] = field(default_factory=list)
    by_category: Dict[str, Dict] = field(default_factory=dict)


def get_db_connection():
    """Get PostgreSQL connection."""
    return psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=int(os.environ.get('POSTGRES_PORT', 5433)),
        database=os.environ.get('POSTGRES_DB', 'gps_cdm'),
        user=os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
        password=os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password')
    )


def get_test_data(format_id: str, batch_id: str) -> Dict[str, Any]:
    """Generate test data for a specific format.

    Handles ISO 20022 composite formats (e.g., FEDWIRE_pacs008) by
    generating data appropriate for the underlying ISO message type.
    """
    unique_id = uuid.uuid4().hex[:8]
    base_time = datetime.now(timezone.utc).isoformat()

    # Common fields for all formats
    common = {
        'creationDateTime': base_time,
        'amount': 1000.00 + abs(hash(format_id)) % 9000,
    }

    # Determine the base format and ISO type for composite formats
    # e.g., FEDWIRE_pacs008 -> base=FEDWIRE, iso=pacs.008
    base_format = format_id
    iso_type = None

    if '_pacs' in format_id.lower() or '_pain' in format_id.lower() or '_camt' in format_id.lower():
        parts = format_id.split('_')
        base_format = parts[0]
        iso_part = '_'.join(parts[1:])
        # Convert pacs008 -> pacs.008
        if iso_part.startswith('pacs') or iso_part.startswith('pain') or iso_part.startswith('camt'):
            iso_type = iso_part[:4] + '.' + iso_part[4:]

    # Format-specific test data
    test_data = {
        # ISO 20022 Core - XML-like structure
        'pain.001': {
            **common,
            'messageId': f'PAIN001-{unique_id}',
            'numberOfTransactions': '1',
            'controlSum': common['amount'],
            'currency': 'EUR',
            'debtorName': f'Debtor {format_id}',
            'debtorIban': 'DE89370400440532013000',
            'creditorName': f'Creditor {format_id}',
            'creditorIban': 'FR7630006000011234567890189',
            'endToEndId': f'E2E-{unique_id}',
            'remittanceInfo': f'E2E Test {format_id}',
        },
        'pacs.008': {
            **common,
            'messageId': f'PACS008-{unique_id}',
            'currency': 'EUR',
            'interbankSettlementAmount': common['amount'],
            'interbankSettlementCurrency': 'EUR',
            'debtorName': f'Debtor {format_id}',
            'debtorIban': 'DE89370400440532013000',
            'debtorAgentBic': 'COBADEFFXXX',
            'creditorName': f'Creditor {format_id}',
            'creditorIban': 'FR7630006000011234567890189',
            'creditorAgentBic': 'BNPAFRPPXXX',
            'endToEndId': f'E2E-{unique_id}',
            'transactionId': f'TXN-{unique_id}',
        },
        'camt.053': {
            **common,
            'messageId': f'CAMT053-{unique_id}',
            'currency': 'EUR',
            'statementId': f'STMT-{unique_id}',
            'accountIban': 'DE89370400440532013000',
            'accountOwnerName': f'Account Owner {format_id}',
            'openingBalance': 50000.00,
            'closingBalance': 51000.00,
            'entryAmount': common['amount'],
            'entryReference': f'REF-{unique_id}',
        },
        # SWIFT MT
        'MT103': {
            **common,
            'sendersReference': f'MT103-{unique_id}',
            'currency': 'USD',
            'valueDate': '250109',
            'orderingCustomerName': f'Ordering {format_id}',
            'orderingCustomerAccount': '123456789',
            'beneficiaryName': f'Beneficiary {format_id}',
            'beneficiaryAccount': '987654321',
            'sendersCorrespondentBic': 'CHASUS33XXX',
            'receiversCorrespondentBic': 'DEUTDEFFXXX',
        },
        'MT202': {
            **common,
            'transactionReferenceNumber': f'MT202-{unique_id}',
            'currency': 'USD',
            'valueDate': '250109',
            'orderingInstitutionBic': 'CHASUS33XXX',
            'beneficiaryInstitutionBic': 'DEUTDEFFXXX',
            'senderToReceiverInfo': f'E2E Test {format_id}',
        },
        'MT940': {
            **common,
            'transactionReferenceNumber': f'MT940-{unique_id}',
            'accountNumber': '123456789',
            'statementNumber': '001',
            'sequenceNumber': '001',
            'openingBalance': 50000.00,
            'closingBalance': 51000.00,
            'currency': 'USD',
        },
        # US Payment Systems
        'ACH': {
            **common,
            'traceNumber': f'{unique_id[:15].ljust(15, "0")}',
            'currency': 'USD',
            'standardEntryClass': 'PPD',
            'companyName': f'Company {format_id}',
            'companyId': '1234567890',
            'receiverName': f'Receiver {format_id}',
            'receiverAccount': '987654321',
            'receivingDfiId': '091000019',
            'originatingDfiId': '081000032',
        },
        'FEDWIRE': {
            **common,
            'imad': f'{unique_id[:22].ljust(22, "0")}',
            'currency': 'USD',
            'typeCode': '10',
            'subtypeCode': '00',
            'senderAba': '021000089',
            'senderName': f'Sender {format_id}',
            'receiverAba': '021000021',
            'receiverName': f'Receiver {format_id}',
            'beneficiaryName': f'Beneficiary {format_id}',
            'beneficiaryAccount': '123456789',
            'originatorName': f'Originator {format_id}',
        },
        'CHIPS': {
            **common,
            'sequenceNumber': f'CHIPS-{unique_id}',
            'currency': 'USD',
            'senderParticipant': '0001',
            'receiverParticipant': '0002',
            'senderReference': f'REF-{unique_id}',
            'beneficiaryName': f'Beneficiary {format_id}',
            'originatorName': f'Originator {format_id}',
        },
        'RTP': {
            **common,
            'messageId': f'RTP-{unique_id}',
            'currency': 'USD',
            'endToEndId': f'E2E-{unique_id}',
            'debtorName': f'Debtor {format_id}',
            'debtorAccount': '123456789',
            'creditorName': f'Creditor {format_id}',
            'creditorAccount': '987654321',
        },
        'FEDNOW': {
            **common,
            'messageId': f'FEDNOW-{unique_id}',
            'currency': 'USD',
            'endToEndId': f'E2E-{unique_id}',
            'debtorName': f'Debtor {format_id}',
            'debtorAccount': '123456789',
            'debtorAgentRoutingNumber': '021000089',
            'creditorName': f'Creditor {format_id}',
            'creditorAccount': '987654321',
            'creditorAgentRoutingNumber': '021000021',
        },
        # UK Payment Systems
        'CHAPS': {
            **common,
            'messageId': f'CHAPS-{unique_id}',
            'currency': 'GBP',
            'endToEndId': f'E2E-{unique_id}',
            'debtorName': f'Debtor {format_id}',
            'debtorIban': 'GB82WEST12345698765432',
            'debtorAgentBic': 'WESTGB2LXXX',
            'creditorName': f'Creditor {format_id}',
            'creditorIban': 'GB29NWBK60161331926819',
            'creditorAgentBic': 'NWBKGB2LXXX',
        },
        'FPS': {
            **common,
            'messageId': f'FPS-{unique_id}',
            'currency': 'GBP',
            'endToEndId': f'E2E-{unique_id}',
            'debtorName': f'Debtor {format_id}',
            'debtorSortCode': '123456',
            'debtorAccount': '12345678',
            'creditorName': f'Creditor {format_id}',
            'creditorSortCode': '654321',
            'creditorAccount': '87654321',
        },
        'BACS': {
            **common,
            'messageId': f'BACS-{unique_id}',
            'currency': 'GBP',
            'processingDate': '250109',
            'serviceUserNumber': '123456',
            'originatingSortCode': '123456',
            'originatingAccount': '12345678',
            'destinationSortCode': '654321',
            'destinationAccount': '87654321',
            'transactionCode': '99',
        },
        # European
        'SEPA': {
            **common,
            'messageId': f'SEPA-{unique_id}',
            'currency': 'EUR',
            'endToEndId': f'E2E-{unique_id}',
            'debtorName': f'Debtor {format_id}',
            'debtorIban': 'DE89370400440532013000',
            'debtorBic': 'COBADEFFXXX',
            'creditorName': f'Creditor {format_id}',
            'creditorIban': 'FR7630006000011234567890189',
            'creditorBic': 'BNPAFRPPXXX',
            'remittanceInfo': f'SEPA E2E Test',
        },
        'TARGET2': {
            **common,
            'messageId': f'TARGET2-{unique_id}',
            'currency': 'EUR',
            'endToEndId': f'E2E-{unique_id}',
            'debtorName': f'Debtor {format_id}',
            'debtorBic': 'COBADEFFXXX',
            'creditorName': f'Creditor {format_id}',
            'creditorBic': 'BNPAFRPPXXX',
            'settlementPriority': 'NORM',
        },
        # Asia-Pacific
        'NPP': {
            **common,
            'messageId': f'NPP-{unique_id}',
            'currency': 'AUD',
            'endToEndId': f'E2E-{unique_id}',
            'debtorName': f'Debtor {format_id}',
            'debtorBsb': '012345',
            'debtorAccount': '123456789',
            'creditorName': f'Creditor {format_id}',
            'creditorBsb': '654321',
            'creditorAccount': '987654321',
            'payIdType': 'EMAL',
            'payIdValue': 'test@example.com',
        },
        'CNAPS': {
            **common,
            'messageId': f'CNAPS-{unique_id}',
            'currency': 'CNY',
            'transactionId': f'TXN-{unique_id}',
            'payerName': f'Payer {format_id}',
            'payerAccount': '6222021234567890123',
            'payerBankCode': '102100099996',
            'payeeName': f'Payee {format_id}',
            'payeeAccount': '6222029876543210987',
            'payeeBankCode': '103100000998',
        },
        'BOJNET': {
            **common,
            'messageId': f'BOJNET-{unique_id}',
            'currency': 'JPY',
            'transactionId': f'TXN-{unique_id}',
            'senderName': f'Sender {format_id}',
            'senderBic': 'BOJPJPJTXXX',
            'receiverName': f'Receiver {format_id}',
            'receiverBic': 'MABORJPJTXX',
            'valueDate': '20250109',
        },
        'KFTC': {
            **common,
            'messageId': f'KFTC-{unique_id}',
            'currency': 'KRW',
            'transactionId': f'TXN-{unique_id}',
            'transactionReference': f'REF-{unique_id}',
            'settlementDate': '2026-01-09',
            'payerName': f'Payer {format_id}',
            'payerAccount': '110-123-456789',
            'payeeName': f'Payee {format_id}',
            'payeeAccount': '333-654-321098',
            'sendingBankCode': '004',
            'receivingBankCode': '011',
            'purpose': 'SUPP',
        },
        'MEPS_PLUS': {
            **common,
            'messageId': f'MEPS-{unique_id}',
            'currency': 'SGD',
            'endToEndId': f'E2E-{unique_id}',
            'debtorName': f'Debtor {format_id}',
            'debtorAccount': 'SG123456789012',
            'debtorAgentBic': 'DBABORSG',
            'creditorName': f'Creditor {format_id}',
            'creditorAccount': 'SG987654321098',
            'creditorAgentBic': 'OCBCSGSG',
        },
        'RTGS_HK': {
            **common,
            'messageId': f'RTGSHK-{unique_id}',
            'currency': 'HKD',
            'endToEndId': f'E2E-{unique_id}',
            'debtorName': f'Debtor {format_id}',
            'debtorAccount': 'HK123456789012',
            'debtorAgentBic': 'HABORHKHHKH',
            'creditorName': f'Creditor {format_id}',
            'creditorAccount': 'HK987654321098',
            'creditorAgentBic': 'SCBLHKHHXXX',
        },
        # Middle East
        'SARIE': {
            **common,
            'messageId': f'SARIE-{unique_id}',
            'currency': 'SAR',
            'endToEndId': f'E2E-{unique_id}',
            'debtorName': f'Debtor {format_id}',
            'debtorIban': 'SA0380000000608010167519',
            'debtorAgentBic': 'NCABORAJ',
            'creditorName': f'Creditor {format_id}',
            'creditorIban': 'SA4420000001234567891234',
            'creditorAgentBic': 'RIABORAJ',
        },
        'UAEFTS': {
            **common,
            'messageId': f'UAEFTS-{unique_id}',
            'currency': 'AED',
            'endToEndId': f'E2E-{unique_id}',
            'debtorName': f'Debtor {format_id}',
            'debtorIban': 'AE070331234567890123456',
            'debtorAgentBic': 'ABORAEADXXX',
            'creditorName': f'Creditor {format_id}',
            'creditorIban': 'AE460261001234567890123',
            'creditorAgentBic': 'ABORAEADXXX',
        },
        # Latin America & Others
        'PIX': {
            **common,
            'transactionId': f'PIX-{unique_id}',
            'currency': 'BRL',
            'endToEndId': f'E2E-{unique_id}',
            'payerName': f'Payer {format_id}',
            'payerAccount': '123456789',
            'payerIspb': '12345678',
            'payeeName': f'Payee {format_id}',
            'payeeAccount': '987654321',
            'payeeIspb': '87654321',
            'remittanceInfo': f'PIX E2E Test',
        },
        'UPI': {
            **common,
            'transactionId': f'UPI-{unique_id}',
            'currency': 'INR',
            'payerVpa': 'payer@upi',
            'payerName': f'Payer {format_id}',
            'payeeVpa': 'payee@upi',
            'payeeName': f'Payee {format_id}',
            'note': f'UPI E2E Test',
        },
        'PROMPTPAY': {
            **common,
            'transactionId': f'PP-{unique_id}',
            'currency': 'THB',
            'endToEndId': f'E2E-{unique_id}',
            'payerName': f'Payer {format_id}',
            'payerAccount': 'TH123456789',
            'payerBankCode': 'KBANK',
            'payerProxyType': 'MSISDN',
            'payerProxyValue': '+66812345678',
            'payeeName': f'Payee {format_id}',
            'payeeAccount': 'TH987654321',
            'payeeBankCode': 'BBL',
            'payeeProxyType': 'TAXID',
            'payeeProxyValue': '1234567890123',
            'remittanceInfo': f'PromptPay E2E Test',
        },
        'PAYNOW': {
            **common,
            'transactionId': f'PN-{unique_id}',
            'currency': 'SGD',
            'endToEndId': f'E2E-{unique_id}',
            'payerName': f'Payer {format_id}',
            'payerAccount': 'SG123456',
            'payerBankCode': 'DBS',
            'payerProxyType': 'MSISDN',
            'payerProxyValue': '+6591234567',
            'payeeName': f'Payee {format_id}',
            'payeeAccount': 'SG987654',
            'payeeBankCode': 'OCBC',
            'payeeProxyType': 'UEN',
            'payeeProxyValue': '202012345A',
            'remittanceInfo': f'PayNow E2E Test',
        },
        'INSTAPAY': {
            **common,
            'messageId': f'INSTAPAY-{unique_id}',
            'currency': 'PHP',
            'endToEndId': f'E2E-{unique_id}',
            'debtorName': f'Debtor {format_id}',
            'debtorAccount': 'PH1234567890',
            'debtorAgentBic': 'BABORPHMM',
            'creditorName': f'Creditor {format_id}',
            'creditorAccount': 'PH0987654321',
            'creditorAgentBic': 'METROCPHM',
        },
    }

    # Handle composite formats (e.g., FEDWIRE_pacs008, CHAPS_pacs002)
    # Use the base format data as template, adding ISO 20022 common fields
    if format_id not in test_data:
        # Check for base format match
        if base_format in test_data:
            data = test_data[base_format].copy()
        elif base_format.upper() in test_data:
            data = test_data[base_format.upper()].copy()
        else:
            # Generate generic ISO 20022 data for unknown formats
            data = {
                **common,
                'messageId': f'{format_id}-{unique_id}',
                'currency': 'USD',
                'endToEndId': f'E2E-{unique_id}',
                'transactionId': f'TXN-{unique_id}',
                'debtorName': f'Debtor {format_id}',
                'debtorAccount': '123456789',
                'debtorAgentBic': 'TESTUS33XXX',
                'creditorName': f'Creditor {format_id}',
                'creditorAccount': '987654321',
                'creditorAgentBic': 'TESTGB2LXXX',
                'remittanceInfo': f'E2E Test {format_id}',
            }

        # Add ISO type-specific fields if detected
        if iso_type:
            data['_isoType'] = iso_type
            if 'pacs.002' in iso_type:
                data['originalMessageId'] = f'ORIG-{unique_id}'
                data['statusCode'] = 'ACCP'
                data['statusReason'] = 'Accepted'
            elif 'pacs.004' in iso_type:
                data['originalMessageId'] = f'ORIG-{unique_id}'
                data['returnReasonCode'] = 'AC04'
                data['returnReasonDescription'] = 'Closed account'
            elif 'pacs.009' in iso_type:
                data['settlementMethod'] = 'INDA'
            elif 'pain.008' in iso_type:
                data['directDebitType'] = 'CORE'
                data['mandateId'] = f'MNDT-{unique_id}'

        return data

    return test_data.get(format_id, {**common, 'messageId': f'{format_id}-{unique_id}'})


def publish_all_messages(formats: List[str]) -> Dict[str, TestResult]:
    """Publish all test messages in parallel via Celery."""
    from gps_cdm.orchestration.celery_tasks import process_bronze_partition

    results = {}
    tasks = []

    # Submit all tasks at once
    batch_prefix = f'e2e_bulk_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}'

    print(f"\n{'='*60}")
    print(f"Publishing {len(formats)} test messages...")
    print(f"{'='*60}")

    for fmt in formats:
        batch_id = f'{batch_prefix}_{fmt}'
        test_data = get_test_data(fmt, batch_id)

        result = TestResult(format_id=fmt, batch_id=batch_id)
        results[fmt] = result

        # Submit async task
        task = process_bronze_partition.delay(
            partition_id=f'e2e_{fmt}_{uuid.uuid4().hex[:8]}',
            file_paths=[],
            message_type=fmt,
            batch_id=batch_id,
            config={'message_content': test_data}
        )
        tasks.append((fmt, task))

    # Wait for all tasks to complete
    print(f"Waiting for {len(tasks)} tasks to complete...")
    for fmt, task in tasks:
        try:
            output = task.get(timeout=60)
            results[fmt].bronze_status = output.get('status', 'UNKNOWN')
            if output.get('status') == 'SUCCESS':
                results[fmt].raw_id = output.get('raw_ids', [None])[0] if output.get('raw_ids') else None
        except Exception as e:
            results[fmt].bronze_status = 'ERROR'
            results[fmt].error = str(e)[:100]

    return results


def check_zone_status(results: Dict[str, TestResult], conn) -> None:
    """Check status in each zone for all results."""
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    batch_ids = [r.batch_id for r in results.values()]
    placeholders = ','.join(['%s'] * len(batch_ids))

    # Check Bronze
    cursor.execute(f"""
        SELECT raw_id, message_type, _batch_id, processing_status
        FROM bronze.raw_payment_messages
        WHERE _batch_id IN ({placeholders})
    """, tuple(batch_ids))

    for row in cursor.fetchall():
        fmt = row['message_type']
        if fmt in results:
            results[fmt].raw_id = row['raw_id']
            results[fmt].bronze_status = 'SUCCESS' if row['processing_status'] in ('PROCESSED', 'PENDING') else row['processing_status']


def get_silver_table_for_format(format_id: str, cursor) -> str:
    """Get Silver table name for a format from database."""
    cursor.execute("""
        SELECT silver_table FROM mapping.message_formats
        WHERE UPPER(format_id) = %s AND is_active = true
    """, (format_id.upper(),))
    row = cursor.fetchone()
    return row['silver_table'] if row else f'stg_{format_id.lower().replace(".", "")}'


def validate_silver_layer(results: Dict[str, TestResult], conn) -> None:
    """Validate Silver layer records."""
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    for fmt, result in results.items():
        if not result.raw_id:
            continue

        try:
            silver_table = get_silver_table_for_format(fmt, cursor)

            # Get Silver record
            cursor.execute(f"""
                SELECT * FROM silver.{silver_table}
                WHERE raw_id = %s
                LIMIT 1
            """, (result.raw_id,))

            row = cursor.fetchone()
            if row:
                result.stg_id = row.get('stg_id')
                result.silver_status = 'SUCCESS'
                result.silver_fields = len(row)
                result.silver_non_null = sum(1 for v in row.values() if v is not None)
            else:
                result.silver_status = 'NOT_FOUND'
        except Exception as e:
            result.silver_status = 'ERROR'
            result.error = str(e)[:100]


def validate_gold_layer(results: Dict[str, TestResult], conn) -> None:
    """Validate Gold layer records."""
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    for fmt, result in results.items():
        if not result.stg_id:
            continue

        try:
            # Check main payment instruction table
            cursor.execute("""
                SELECT instruction_id, source_message_type, instructed_amount, current_status
                FROM gold.cdm_payment_instruction
                WHERE source_stg_id = %s
                LIMIT 1
            """, (result.stg_id,))

            row = cursor.fetchone()
            if row:
                result.instruction_id = row.get('instruction_id')
                result.gold_status = 'SUCCESS'
                result.gold_fields = len(row)
                result.gold_non_null = sum(1 for v in row.values() if v is not None)
            else:
                # Check ISO 20022 aligned table
                cursor.execute("""
                    SELECT instruction_id, source_message_type
                    FROM gold.cdm_pacs_fi_customer_credit_transfer
                    WHERE source_stg_id = %s
                    LIMIT 1
                """, (result.stg_id,))
                row = cursor.fetchone()
                if row:
                    result.instruction_id = row.get('instruction_id')
                    result.gold_status = 'SUCCESS'
                    result.gold_fields = len(row)
                    result.gold_non_null = sum(1 for v in row.values() if v is not None)
                else:
                    result.gold_status = 'NOT_FOUND'
        except Exception as e:
            result.gold_status = 'ERROR'
            result.error = str(e)[:100]


def count_gold_entities(results: Dict[str, TestResult], conn) -> Dict[str, Dict[str, int]]:
    """Count Gold entities created for each format."""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    entity_counts = {}

    stg_ids = [r.stg_id for r in results.values() if r.stg_id]
    if not stg_ids:
        return entity_counts

    placeholders = ','.join(['%s'] * len(stg_ids))

    # Check which column exists in each table
    def safe_count(table: str, stg_ids: List[str]) -> Dict[str, int]:
        try:
            # Try source_stg_id first
            cursor.execute(f"""
                SELECT source_stg_id, COUNT(*) as cnt
                FROM gold.{table}
                WHERE source_stg_id IN ({placeholders})
                GROUP BY source_stg_id
            """, tuple(stg_ids))
            return {row['source_stg_id']: row['cnt'] for row in cursor.fetchall()}
        except Exception:
            conn.rollback()
            try:
                # Try stg_id as fallback
                cursor.execute(f"""
                    SELECT stg_id, COUNT(*) as cnt
                    FROM gold.{table}
                    WHERE stg_id IN ({placeholders})
                    GROUP BY stg_id
                """, tuple(stg_ids))
                return {row['stg_id']: row['cnt'] for row in cursor.fetchall()}
            except Exception:
                conn.rollback()
                return {}

    party_counts = safe_count('cdm_party', stg_ids)
    account_counts = safe_count('cdm_account', stg_ids)
    fi_counts = safe_count('cdm_financial_institution', stg_ids)

    for fmt, result in results.items():
        if result.stg_id:
            entity_counts[fmt] = {
                'parties': party_counts.get(result.stg_id, 0),
                'accounts': account_counts.get(result.stg_id, 0),
                'financial_institutions': fi_counts.get(result.stg_id, 0),
            }

    return entity_counts


def categorize_format(format_id: str) -> str:
    """Categorize format into groups."""
    categories = {
        'ISO 20022 Core': ['pain.001', 'pacs.008', 'camt.053'],
        'SWIFT MT': ['MT103', 'MT202', 'MT940'],
        'US Payments': ['ACH', 'FEDWIRE', 'CHIPS', 'RTP', 'FEDNOW'],
        'UK Payments': ['CHAPS', 'FPS', 'BACS'],
        'European': ['SEPA', 'TARGET2'],
        'Asia-Pacific': ['NPP', 'CNAPS', 'BOJNET', 'KFTC', 'MEPS_PLUS', 'RTGS_HK'],
        'Middle East': ['SARIE', 'UAEFTS'],
        'Regional JSON': ['PIX', 'UPI', 'PROMPTPAY', 'PAYNOW', 'INSTAPAY'],
    }

    for category, formats in categories.items():
        if format_id in formats:
            return category
    return 'Other'


def generate_summary(results: Dict[str, TestResult], entity_counts: Dict[str, Dict]) -> TestSummary:
    """Generate test summary with categorization."""
    summary = TestSummary(total=len(results))

    for fmt, result in results.items():
        category = categorize_format(fmt)

        if category not in summary.by_category:
            summary.by_category[category] = {
                'total': 0, 'bronze_pass': 0, 'silver_pass': 0, 'gold_pass': 0, 'failed': []
            }

        cat = summary.by_category[category]
        cat['total'] += 1

        if result.bronze_status == 'SUCCESS':
            summary.bronze_pass += 1
            cat['bronze_pass'] += 1

        if result.silver_status == 'SUCCESS':
            summary.silver_pass += 1
            cat['silver_pass'] += 1

        if result.gold_status == 'SUCCESS':
            summary.gold_pass += 1
            cat['gold_pass'] += 1
        else:
            summary.failed.append(fmt)
            cat['failed'].append(fmt)

    return summary


def print_results(results: Dict[str, TestResult], entity_counts: Dict[str, Dict], summary: TestSummary):
    """Print detailed results and summary."""

    print(f"\n{'='*80}")
    print("E2E BULK TEST RESULTS")
    print(f"{'='*80}")

    # Detailed results table
    print(f"\n{'Format':<12} {'Bronze':<10} {'Silver':<10} {'Gold':<10} {'Entities':<20} {'Error':<30}")
    print("-" * 92)

    for fmt in sorted(results.keys()):
        r = results[fmt]
        entities = entity_counts.get(fmt, {})
        entity_str = f"P:{entities.get('parties',0)} A:{entities.get('accounts',0)} F:{entities.get('financial_institutions',0)}"

        bronze_icon = '✅' if r.bronze_status == 'SUCCESS' else '❌'
        silver_icon = '✅' if r.silver_status == 'SUCCESS' else '❌'
        gold_icon = '✅' if r.gold_status == 'SUCCESS' else '❌'

        error = (r.error or '')[:30] if r.gold_status != 'SUCCESS' else ''

        print(f"{fmt:<12} {bronze_icon} {r.bronze_status:<8} {silver_icon} {r.silver_status:<8} {gold_icon} {r.gold_status:<8} {entity_str:<20} {error}")

    # Category summary
    print(f"\n{'='*80}")
    print("SUMMARY BY CATEGORY")
    print(f"{'='*80}")

    print(f"\n{'Category':<20} {'Total':<8} {'Bronze':<10} {'Silver':<10} {'Gold':<10} {'Failed':<20}")
    print("-" * 78)

    for category, cat_data in sorted(summary.by_category.items()):
        failed_str = ','.join(cat_data['failed'][:3]) + ('...' if len(cat_data['failed']) > 3 else '')
        print(f"{category:<20} {cat_data['total']:<8} {cat_data['bronze_pass']:<10} {cat_data['silver_pass']:<10} {cat_data['gold_pass']:<10} {failed_str:<20}")

    # Overall summary
    print(f"\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}")

    print(f"\nTotal Formats Tested: {summary.total}")
    print(f"Bronze Pass: {summary.bronze_pass}/{summary.total} ({100*summary.bronze_pass/summary.total:.1f}%)")
    print(f"Silver Pass: {summary.silver_pass}/{summary.total} ({100*summary.silver_pass/summary.total:.1f}%)")
    print(f"Gold Pass:   {summary.gold_pass}/{summary.total} ({100*summary.gold_pass/summary.total:.1f}%)")

    if summary.failed:
        print(f"\nFailed Formats ({len(summary.failed)}): {', '.join(summary.failed)}")
    else:
        print(f"\n✅ ALL {summary.total} FORMATS PASSED E2E VALIDATION!")


def main():
    parser = argparse.ArgumentParser(description='GPS CDM E2E Bulk Testing')
    parser.add_argument('--formats', type=str, help='Comma-separated list of formats to test')
    parser.add_argument('--timeout', type=int, default=60, help='Timeout in seconds for zone processing')
    parser.add_argument('--poll-interval', type=int, default=5, help='Polling interval in seconds')
    args = parser.parse_args()

    formats = args.formats.split(',') if args.formats else ALL_FORMATS

    print(f"\n{'#'*80}")
    print(f"# GPS CDM E2E BULK TEST")
    print(f"# Testing {len(formats)} formats")
    print(f"# Started: {datetime.utcnow().isoformat()}")
    print(f"{'#'*80}")

    start_time = time.time()

    # Phase 1: Publish all messages
    results = publish_all_messages(formats)

    # Phase 2: Wait for zone processing
    conn = get_db_connection()

    print(f"\nPolling for zone completion (timeout: {args.timeout}s)...")
    elapsed = 0
    while elapsed < args.timeout:
        check_zone_status(results, conn)
        validate_silver_layer(results, conn)
        validate_gold_layer(results, conn)

        # Check if all done
        all_done = all(r.gold_status in ('SUCCESS', 'ERROR', 'NOT_FOUND') for r in results.values())
        gold_success = sum(1 for r in results.values() if r.gold_status == 'SUCCESS')

        print(f"  [{elapsed}s] Bronze: {sum(1 for r in results.values() if r.bronze_status == 'SUCCESS')}/{len(formats)}, "
              f"Silver: {sum(1 for r in results.values() if r.silver_status == 'SUCCESS')}/{len(formats)}, "
              f"Gold: {gold_success}/{len(formats)}")

        if all_done or gold_success == len(formats):
            break

        time.sleep(args.poll_interval)
        elapsed += args.poll_interval

    # Phase 3: Count entities and generate summary
    entity_counts = count_gold_entities(results, conn)
    summary = generate_summary(results, entity_counts)

    conn.close()

    # Print results
    print_results(results, entity_counts, summary)

    total_time = time.time() - start_time
    print(f"\nTotal execution time: {total_time:.1f}s")

    # Return exit code based on success
    return 0 if summary.gold_pass == summary.total else 1


if __name__ == '__main__':
    sys.exit(main())
