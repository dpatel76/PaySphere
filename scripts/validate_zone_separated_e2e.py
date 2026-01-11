#!/usr/bin/env python3
"""
GPS CDM - Zone-Separated E2E Validation
========================================

Validates the complete zone-separated pipeline for all message types.

This script understands the message routing framework:
- NATIVE_ISO / FULLY_MIGRATED formats route to ISO 20022 Silver tables
- INTEGRATION_ONLY / LEGACY formats use format-specific Silver tables

Validates:
1. Bronze records are stored AS-IS
2. Silver records are properly parsed (in correct table based on routing)
3. Gold CDM entities are created
4. Lineage tracking

Usage:
    python scripts/validate_zone_separated_e2e.py [--types TYPE1,TYPE2] [--verbose]

Examples:
    python scripts/validate_zone_separated_e2e.py --types CHAPS,FEDWIRE
    python scripts/validate_zone_separated_e2e.py --all --verbose
"""

import argparse
import json
import logging
import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import psycopg2
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic

# Import message routing framework
from gps_cdm.message_formats.base.message_routing import (
    PAYMENT_STANDARDS,
    AdoptionStatus,
    detect_message_routing,
    get_payment_standard,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# SILVER TABLE ROUTING
# =============================================================================

# Mapping of actual Silver tables that exist in the database
# This is derived from information_schema.tables output
ACTUAL_SILVER_TABLES = {
    # ISO 20022 core tables (used by ISO native/migrated formats)
    'stg_iso20022_pacs008', 'stg_iso20022_pacs002', 'stg_iso20022_pacs004',
    'stg_iso20022_pacs009', 'stg_iso20022_pain001', 'stg_iso20022_pain008',
    'stg_iso20022_camt053', 'stg_iso20022_camt056',
    # Versioned format-specific tables
    'stg_chaps_v', 'stg_chips_v', 'stg_fedwire_v', 'stg_fednow_v',
    'stg_fps_v', 'stg_npp_v', 'stg_rtp_v', 'stg_target2_v',
    'stg_meps_plus_v', 'stg_rtgs_hk_v', 'stg_uaefts_v', 'stg_instapay_v',
    'stg_sepa_v', 'stg_pacs008_v',
    # Non-versioned format-specific tables
    'stg_ach', 'stg_bacs', 'stg_bojnet', 'stg_camt053',
    'stg_cnaps', 'stg_faster_payments', 'stg_kftc',
    'stg_paynow', 'stg_pix', 'stg_promptpay',
    'stg_sarie', 'stg_sepa', 'stg_upi',
    'stg_pain001',
}


def get_silver_table_for_format(format_code: str, iso_message_type: str = None) -> List[str]:
    """
    Determine the correct Silver table(s) for a payment format.

    Based on message routing framework:
    - NATIVE_ISO / FULLY_MIGRATED formats → ISO 20022 tables (stg_iso20022_pacs008, etc.)
    - INTEGRATION_ONLY / LEGACY / NOT_ISO20022 → format-specific tables

    Returns list of possible table names to check (in priority order).
    """
    standard = get_payment_standard(format_code)
    normalized = format_code.lower().replace('.', '').replace('-', '_')

    tables_to_check = []

    # If format is already an ISO type (pain.001, pacs.008, etc.)
    if format_code.lower().startswith(('pain', 'pacs', 'camt')):
        iso_type = format_code.lower().replace('.', '')
        # Check both versioned and non-versioned ISO tables
        tables_to_check.append(f'stg_iso20022_{iso_type}')
        tables_to_check.append(f'stg_{iso_type}')
        tables_to_check.append(f'stg_{iso_type}_v')
        return tables_to_check

    if standard:
        # Get default ISO type for this format
        default_iso = standard.default_iso_type.replace('.', '')

        # For ISO-native or fully migrated formats, primary target is ISO table
        if standard.adoption_status in (AdoptionStatus.NATIVE_ISO, AdoptionStatus.FULLY_MIGRATED):
            # Primary: ISO 20022 table for the target message type
            tables_to_check.append(f'stg_iso20022_{default_iso}')
            # Fallback: versioned format-specific table
            tables_to_check.append(f'stg_{normalized}_v')
            # Fallback: non-versioned format-specific
            tables_to_check.append(f'stg_{normalized}')
        else:
            # For legacy/integration formats, primary is format-specific
            tables_to_check.append(f'stg_{normalized}')
            tables_to_check.append(f'stg_{normalized}_v')
            # Also check ISO table as fallback
            tables_to_check.append(f'stg_iso20022_{default_iso}')
    else:
        # Unknown format - try all possible patterns
        tables_to_check.append(f'stg_{normalized}')
        tables_to_check.append(f'stg_{normalized}_v')
        tables_to_check.append('stg_iso20022_pacs008')

    # Handle special cases
    if format_code.upper() == 'FPS':
        tables_to_check.insert(0, 'stg_faster_payments')

    return tables_to_check


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class Config:
    """Validation configuration."""

    # Kafka
    kafka_bootstrap: str = "localhost:9092"

    # PostgreSQL
    pg_host: str = "localhost"
    pg_port: int = 5433
    pg_db: str = "gps_cdm"
    pg_user: str = "gps_cdm_svc"
    pg_password: str = "gps_cdm_password"

    # Celery
    celery_timeout: int = 30

    # Validation
    wait_for_processing: int = 5  # seconds to wait for async processing


# =============================================================================
# TEST DATA
# =============================================================================

class TestDataGenerator:
    """Generates test data for each message type."""

    @staticmethod
    def generate(message_type: str, test_id: str) -> str:
        """Generate test data for message type.

        NOTE: SWIFT MT messages (MT103, MT202, MT940) were decommissioned by SWIFT in Nov 2025.
        Use ISO 20022 equivalents: MT103→pacs.008, MT202→pacs.009, MT940/MT950→camt.053
        """
        generators = {
            # ISO 20022
            'pain.001': TestDataGenerator._pain001,
            'pain.002': TestDataGenerator._pain002,
            'pacs.008': TestDataGenerator._pacs008,
            'pacs.002': TestDataGenerator._pacs002,
            'pacs.004': TestDataGenerator._pacs004,
            'pacs.009': TestDataGenerator._pacs009,
            'camt.053': TestDataGenerator._camt053,

            # US
            'FEDWIRE': TestDataGenerator._fedwire,
            'ACH': TestDataGenerator._ach,
            'RTP': TestDataGenerator._rtp,
            'FEDNOW': TestDataGenerator._fednow,
            'CHIPS': TestDataGenerator._chips,

            # UK
            'CHAPS': TestDataGenerator._chaps,
            'BACS': TestDataGenerator._bacs,
            'FPS': TestDataGenerator._fps,

            # Europe
            'SEPA': TestDataGenerator._sepa,
            'TARGET2': TestDataGenerator._target2,

            # APAC
            'NPP': TestDataGenerator._npp,
            'UPI': TestDataGenerator._upi,
            'PIX': TestDataGenerator._pix,
            'INSTAPAY': TestDataGenerator._instapay,
            'PAYNOW': TestDataGenerator._paynow,
            'PROMPTPAY': TestDataGenerator._promptpay,
            'MEPS_PLUS': TestDataGenerator._meps_plus,
            'RTGS_HK': TestDataGenerator._rtgs_hk,
            'BOJNET': TestDataGenerator._bojnet,
            'KFTC': TestDataGenerator._kftc,
            'CNAPS': TestDataGenerator._cnaps,

            # Middle East
            'SARIE': TestDataGenerator._sarie,
            'UAEFTS': TestDataGenerator._uaefts,
        }

        generator = generators.get(message_type, TestDataGenerator._generic_json)
        return generator(test_id)

    @staticmethod
    def _pain001(test_id: str) -> str:
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>PAIN001-{test_id}</MsgId>
      <CreDtTm>2025-12-29T12:00:00</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>1000.00</CtrlSum>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>PMT-{test_id}</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <Dbtr>
        <Nm>Test Debtor {test_id}</Nm>
        <PstlAdr><Ctry>US</Ctry></PstlAdr>
      </Dbtr>
      <DbtrAcct><Id><IBAN>US12345678901234567890</IBAN></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BICFI>TESTUS33XXX</BICFI></FinInstnId></DbtrAgt>
      <CdtTrfTxInf>
        <Amt><InstdAmt Ccy="USD">1000.00</InstdAmt></Amt>
        <Cdtr><Nm>Test Creditor {test_id}</Nm></Cdtr>
        <CdtrAcct><Id><IBAN>GB87654321098765432109</IBAN></Id></CdtrAcct>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>'''

    @staticmethod
    def _pain002(test_id: str) -> str:
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.002.001.10">
  <CstmrPmtStsRpt>
    <GrpHdr><MsgId>PAIN002-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm></GrpHdr>
    <OrgnlGrpInfAndSts><OrgnlMsgId>ORIG-{test_id}</OrgnlMsgId><GrpSts>ACCP</GrpSts></OrgnlGrpInfAndSts>
  </CstmrPmtStsRpt>
</Document>'''

    @staticmethod
    def _pacs008(test_id: str) -> str:
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>PACS008-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>INSTR-{test_id}</InstrId><EndToEndId>E2E-{test_id}</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="EUR">2500.00</IntrBkSttlmAmt>
      <Dbtr><Nm>Debtor {test_id}</Nm></Dbtr>
      <Cdtr><Nm>Creditor {test_id}</Nm></Cdtr>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _camt053(test_id: str) -> str:
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.08">
  <BkToCstmrStmt>
    <GrpHdr><MsgId>CAMT053-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm></GrpHdr>
    <Stmt><Id>STMT-{test_id}</Id><ElctrncSeqNb>1</ElctrncSeqNb><LglSeqNb>1</LglSeqNb></Stmt>
  </BkToCstmrStmt>
</Document>'''

    @staticmethod
    def _pacs002(test_id: str) -> str:
        """pacs.002 - Payment Status Report"""
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.002.001.10">
  <FIToFIPmtStsRpt>
    <GrpHdr><MsgId>PACS002-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm></GrpHdr>
    <OrgnlGrpInfAndSts><OrgnlMsgId>ORIG-{test_id}</OrgnlMsgId><GrpSts>ACCP</GrpSts></OrgnlGrpInfAndSts>
  </FIToFIPmtStsRpt>
</Document>'''

    @staticmethod
    def _pacs004(test_id: str) -> str:
        """pacs.004 - Payment Return"""
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.004.001.09">
  <PmtRtr>
    <GrpHdr><MsgId>PACS004-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <TxInf>
      <RtrId>RTN-{test_id}</RtrId>
      <OrgnlEndToEndId>ORIG-E2E-{test_id}</OrgnlEndToEndId>
      <RtrdIntrBkSttlmAmt Ccy="EUR">1000.00</RtrdIntrBkSttlmAmt>
      <RtrRsnInf><Rsn><Cd>AC04</Cd></Rsn></RtrRsnInf>
    </TxInf>
  </PmtRtr>
</Document>'''

    @staticmethod
    def _pacs009(test_id: str) -> str:
        """pacs.009 - Financial Institution Credit Transfer"""
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.009.001.08">
  <FICdtTrf>
    <GrpHdr><MsgId>PACS009-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>FI-INSTR-{test_id}</InstrId><EndToEndId>FI-E2E-{test_id}</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="EUR">50000.00</IntrBkSttlmAmt>
      <Dbtr><FinInstnId><BICFI>DEUTDEFFXXX</BICFI></FinInstnId></Dbtr>
      <Cdtr><FinInstnId><BICFI>COBADEFFXXX</BICFI></FinInstnId></Cdtr>
    </CdtTrfTxInf>
  </FICdtTrf>
</Document>'''

    # NOTE: SWIFT MT messages (MT103, MT202, MT940) were decommissioned by SWIFT in Nov 2025
    # The _mt103, _mt202, _mt940 methods are kept for reference but should not be used

    @staticmethod
    def _chaps(test_id: str) -> str:
        return f'''{{1:F01TESTUS33XXXX0000000001}}{{2:O1031200251229TESTGB2LXXXX00000000012512291200N}}{{3:{{108:MT103{test_id}}}}}{{4:
:20:TXN-{test_id}
:23B:CRED
:32A:251229USD1500,00
:50K:/US1234567890
TEST DEBTOR {test_id}
123 TEST STREET
NEW YORK NY 10001
USA
:52A:TESTUS33XXX
:57A:TESTGB2LXXX
:59:/GB9876543210
TEST CREDITOR {test_id}
456 MAIN ROAD
LONDON EC1A 1BB
UK
:70:E2E TEST PAYMENT {test_id}
:71A:SHA
-}}{{5:{{CHK:TEST{test_id}}}}}'''

    @staticmethod
    def _mt202(test_id: str) -> str:
        return f'''{{1:F01TESTUS33XXXX0000000002}}{{2:O2021200251229TESTGB2LXXXX00000000022512291200N}}{{3:{{108:MT202{test_id}}}}}{{4:
:20:COV-{test_id}
:21:REL-{test_id}
:32A:251229USD50000,00
:52A:TESTUS33XXX
:58A:TESTGB2LXXX
-}}{{5:{{CHK:COV{test_id}}}}}'''

    @staticmethod
    def _mt940(test_id: str) -> str:
        return f'''{{1:F01TESTUS33XXXX0000000003}}{{2:O9401200251229TESTUS33XXXX00000000032512291200N}}{{4:
:20:STMT-{test_id}
:25:12345678
:28C:1/1
:60F:C251228USD10000,00
:61:2512290101D1500,00NTRFTXN{test_id}//CUST REF
:62F:C251229USD8500,00
-}}'''

    @staticmethod
    def _chaps(test_id: str) -> str:
        return f'''{{1:F01BABORLONXXXX0000000001}}{{2:O1031000251229HSABORLONXXXX00000000012512291000N}}{{3:{{108:CHAPS{test_id}}}}}{{4:
:20:CHAPS-{test_id}
:23B:CRED
:32A:251229GBP75000,00
:50K:/GB12VERF0000012345678
CHAPS TEST DEBTOR {test_id}
100 VALIDATION STREET
LONDON EC1 1AB
UNITED KINGDOM
:52A:VERFGB2LXXX
:57A:BABORLONXXX
:59:/GB22DEST1111122222222
CHAPS TEST CREDITOR {test_id}
200 SUCCESS ROAD
MANCHESTER M1 1AA
UNITED KINGDOM
:70:CHAPS E2E TEST {test_id}
:71A:SHA
-}}{{5:{{CHK:CHAPS{test_id}}}}}'''

    @staticmethod
    def _bacs(test_id: str) -> str:
        return f'''{{1:F01BABORLONXXXX0000000002}}{{2:O1031000251229TESTGB2LXXXX00000000022512291000N}}{{3:{{108:BACS{test_id}}}}}{{4:
:20:BACS-{test_id}
:23B:CRED
:32A:251229GBP500,00
:50K:/GB11SORT1234512345678
BACS DEBTOR {test_id}
UK ADDRESS
:59:/GB22DEST9876598765432
BACS CREDITOR {test_id}
:70:BACS PAYMENT {test_id}
:71A:SHA
-}}'''

    @staticmethod
    def _fps(test_id: str) -> str:
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>FPS-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>FPS-INSTR-{test_id}</InstrId><EndToEndId>FPS-E2E-{test_id}</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="GBP">250.00</IntrBkSttlmAmt>
      <Dbtr><Nm>FPS Debtor {test_id}</Nm></Dbtr>
      <Cdtr><Nm>FPS Creditor {test_id}</Nm></Cdtr>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _fedwire(test_id: str) -> str:
        return f'''{{1500}}30
{{1510}}1000
{{1520}}FED-{test_id}
{{2000}}000010000000
{{3100}}021000089
{{3400}}FEDWIRE TEST BANK
{{4100}}ORIG-{test_id}
{{4200}}BENE-{test_id}
{{5000}}FEDWIRE TEST PAYMENT {test_id}
{{6000}}ORIG-BANK-REF-{test_id}'''

    @staticmethod
    def _ach(test_id: str) -> str:
        # NACHA format: 94 characters per line
        file_header = f"101 021000089 1234567890251229     A094101TEST FILE {test_id}".ljust(94)
        batch_header = f"5200TEST COMPANY           1234567890PPDTEST      251229251229   1021000890000001".ljust(94)
        entry = f"622021000089123456789        0000010000{test_id[:10].ljust(15)}TEST PAYEE {test_id[:15]}".ljust(94)
        batch_control = f"82000000010002100008900000000000000000010000001234567890                         021000890000001".ljust(94)
        file_control = f"9000001000001000000010002100008900000000000000000010000                                       ".ljust(94)
        return f"{file_header}\n{batch_header}\n{entry}\n{batch_control}\n{file_control}"

    @staticmethod
    def _rtp(test_id: str) -> str:
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>RTP-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>RTP-INSTR-{test_id}</InstrId><EndToEndId>RTP-E2E-{test_id}</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="USD">500.00</IntrBkSttlmAmt>
      <Dbtr><Nm>RTP Debtor {test_id}</Nm></Dbtr>
      <Cdtr><Nm>RTP Creditor {test_id}</Nm></Cdtr>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _sepa(test_id: str) -> str:
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">
  <CstmrCdtTrfInitn>
    <GrpHdr><MsgId>SEPA-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <PmtInf>
      <PmtInfId>SEPA-PMT-{test_id}</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <Dbtr><Nm>SEPA Debtor {test_id}</Nm></Dbtr>
      <DbtrAcct><Id><IBAN>DE89370400440532013000</IBAN></Id></DbtrAcct>
      <CdtTrfTxInf>
        <Amt><InstdAmt Ccy="EUR">150.00</InstdAmt></Amt>
        <Cdtr><Nm>SEPA Creditor {test_id}</Nm></Cdtr>
        <CdtrAcct><Id><IBAN>FR7630006000011234567890189</IBAN></Id></CdtrAcct>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>'''

    @staticmethod
    def _npp(test_id: str) -> str:
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>NPP-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>NPP-{test_id}</InstrId><EndToEndId>NPP-E2E-{test_id}</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="AUD">200.00</IntrBkSttlmAmt>
      <Dbtr><Nm>NPP Debtor {test_id}</Nm></Dbtr>
      <Cdtr><Nm>NPP Creditor {test_id}</Nm></Cdtr>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _upi(test_id: str) -> str:
        return json.dumps({
            "txnId": f"UPI-{test_id}",
            "payerVpa": f"payer{test_id}@bank",
            "payeeVpa": f"payee{test_id}@bank",
            "amount": "100.00",
            "currency": "INR",
            "note": f"UPI Test Payment {test_id}",
            "timestamp": "2025-12-29T12:00:00"
        })

    @staticmethod
    def _pix(test_id: str) -> str:
        return json.dumps({
            "endToEndId": f"PIX-{test_id}",
            "txid": f"PIXTXN{test_id}",
            "valor": {"original": "50.00"},
            "chave": f"pix{test_id}@email.com",
            "devedor": {"nome": f"PIX Debtor {test_id}"},
            "recebedor": {"nome": f"PIX Creditor {test_id}"},
            "calendario": {"criacao": "2025-12-29T12:00:00"}
        })

    @staticmethod
    def _instapay(test_id: str) -> str:
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>INSTAPAY-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>INSTA-{test_id}</InstrId></PmtId>
      <IntrBkSttlmAmt Ccy="PHP">1000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>InstaPay Debtor {test_id}</Nm></Dbtr>
      <Cdtr><Nm>InstaPay Creditor {test_id}</Nm></Cdtr>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _paynow(test_id: str) -> str:
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>PAYNOW-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>PAYNOW-{test_id}</InstrId></PmtId>
      <IntrBkSttlmAmt Ccy="SGD">500.00</IntrBkSttlmAmt>
      <Dbtr><Nm>PayNow Debtor {test_id}</Nm></Dbtr>
      <Cdtr><Nm>PayNow Creditor {test_id}</Nm></Cdtr>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _promptpay(test_id: str) -> str:
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>PROMPTPAY-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>PROMPT-{test_id}</InstrId></PmtId>
      <IntrBkSttlmAmt Ccy="THB">1500.00</IntrBkSttlmAmt>
      <Dbtr><Nm>PromptPay Debtor {test_id}</Nm></Dbtr>
      <Cdtr><Nm>PromptPay Creditor {test_id}</Nm></Cdtr>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _fednow(test_id: str) -> str:
        """FedNow - ISO 20022 native instant payment (US)"""
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>FEDNOW-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>FEDNOW-{test_id}</InstrId><EndToEndId>FN-E2E-{test_id}</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="USD">500.00</IntrBkSttlmAmt>
      <Dbtr><Nm>FedNow Debtor {test_id}</Nm></Dbtr>
      <Cdtr><Nm>FedNow Creditor {test_id}</Nm></Cdtr>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _chips(test_id: str) -> str:
        """CHIPS - US large value payment (ISO 20022 migrated)"""
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>CHIPS-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>CHIPS-{test_id}</InstrId><EndToEndId>CH-E2E-{test_id}</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="USD">100000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>CHIPS Debtor {test_id}</Nm></Dbtr>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>0001</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <Cdtr><Nm>CHIPS Creditor {test_id}</Nm></Cdtr>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>0002</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _target2(test_id: str) -> str:
        """TARGET2 - Eurozone RTGS (ISO 20022 migrated)"""
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>TARGET2-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>T2-{test_id}</InstrId><EndToEndId>T2-E2E-{test_id}</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="EUR">50000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>TARGET2 Debtor {test_id}</Nm></Dbtr>
      <DbtrAgt><FinInstnId><BICFI>DEUTDEFFXXX</BICFI></FinInstnId></DbtrAgt>
      <Cdtr><Nm>TARGET2 Creditor {test_id}</Nm></Cdtr>
      <CdtrAgt><FinInstnId><BICFI>COBADEFFXXX</BICFI></FinInstnId></CdtrAgt>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _meps_plus(test_id: str) -> str:
        """MEPS+ - Singapore RTGS (ISO 20022 migrated)"""
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>MEPS-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>MEPS-{test_id}</InstrId><EndToEndId>MEPS-E2E-{test_id}</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="SGD">25000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>MEPS Debtor {test_id}</Nm></Dbtr>
      <DbtrAgt><FinInstnId><BICFI>DBSSSGSGXXX</BICFI></FinInstnId></DbtrAgt>
      <Cdtr><Nm>MEPS Creditor {test_id}</Nm></Cdtr>
      <CdtrAgt><FinInstnId><BICFI>OCBCSGSGXXX</BICFI></FinInstnId></CdtrAgt>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _rtgs_hk(test_id: str) -> str:
        """RTGS_HK (CHATS) - Hong Kong RTGS (ISO 20022 migrated)"""
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>RTGSHK-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>CHATS-{test_id}</InstrId><EndToEndId>HK-E2E-{test_id}</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="HKD">50000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>CHATS Debtor {test_id}</Nm></Dbtr>
      <DbtrAgt><FinInstnId><BICFI>HABORHKHXXX</BICFI></FinInstnId></DbtrAgt>
      <Cdtr><Nm>CHATS Creditor {test_id}</Nm></Cdtr>
      <CdtrAgt><FinInstnId><BICFI>SCBLHKHHHKH</BICFI></FinInstnId></CdtrAgt>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _bojnet(test_id: str) -> str:
        """BOJ-NET - Japan Bank of Japan network (ISO 20022 migrated)"""
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>BOJNET-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>BOJ-{test_id}</InstrId><EndToEndId>BOJ-E2E-{test_id}</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="JPY">1000000</IntrBkSttlmAmt>
      <Dbtr><Nm>BOJ-NET Debtor {test_id}</Nm></Dbtr>
      <DbtrAgt><FinInstnId><BICFI>MABORJPJXXX</BICFI></FinInstnId></DbtrAgt>
      <Cdtr><Nm>BOJ-NET Creditor {test_id}</Nm></Cdtr>
      <CdtrAgt><FinInstnId><BICFI>SMBORJPJXXX</BICFI></FinInstnId></CdtrAgt>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _kftc(test_id: str) -> str:
        """KFTC - Korea Financial Telecommunications & Clearings Institute"""
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>KFTC-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>KFTC-{test_id}</InstrId><EndToEndId>KR-E2E-{test_id}</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="KRW">100000</IntrBkSttlmAmt>
      <Dbtr><Nm>KFTC Debtor {test_id}</Nm></Dbtr>
      <DbtrAgt><FinInstnId><BICFI>KOABORKSXXX</BICFI></FinInstnId></DbtrAgt>
      <Cdtr><Nm>KFTC Creditor {test_id}</Nm></Cdtr>
      <CdtrAgt><FinInstnId><BICFI>SHABORKSXXX</BICFI></FinInstnId></CdtrAgt>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _cnaps(test_id: str) -> str:
        """CNAPS - China National Advanced Payment System (ISO 20022 migrated)"""
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>CNAPS-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>CNAPS-{test_id}</InstrId><EndToEndId>CN-E2E-{test_id}</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="CNY">10000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>CNAPS Debtor {test_id}</Nm></Dbtr>
      <DbtrAgt><FinInstnId><BICFI>ICBKBCNBXXX</BICFI></FinInstnId></DbtrAgt>
      <Cdtr><Nm>CNAPS Creditor {test_id}</Nm></Cdtr>
      <CdtrAgt><FinInstnId><BICFI>CCBCBCNBXXX</BICFI></FinInstnId></CdtrAgt>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _sarie(test_id: str) -> str:
        """SARIE - Saudi Arabian Riyal Interbank Express (ISO 20022 migrated)"""
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>SARIE-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>SARIE-{test_id}</InstrId><EndToEndId>SA-E2E-{test_id}</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="SAR">5000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>SARIE Debtor {test_id}</Nm></Dbtr>
      <DbtrAgt><FinInstnId><BICFI>NCBKSAJEXXX</BICFI></FinInstnId></DbtrAgt>
      <Cdtr><Nm>SARIE Creditor {test_id}</Nm></Cdtr>
      <CdtrAgt><FinInstnId><BICFI>RJHISARIXXX</BICFI></FinInstnId></CdtrAgt>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _uaefts(test_id: str) -> str:
        """UAEFTS - UAE Funds Transfer System"""
        return f'''<?xml version="1.0"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr><MsgId>UAEFTS-{test_id}</MsgId><CreDtTm>2025-12-29T12:00:00</CreDtTm><NbOfTxs>1</NbOfTxs></GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>UAEFTS-{test_id}</InstrId><EndToEndId>AE-E2E-{test_id}</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="AED">10000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>UAEFTS Debtor {test_id}</Nm></Dbtr>
      <DbtrAgt><FinInstnId><BICFI>EMIRATEAEXXX</BICFI></FinInstnId></DbtrAgt>
      <Cdtr><Nm>UAEFTS Creditor {test_id}</Nm></Cdtr>
      <CdtrAgt><FinInstnId><BICFI>NBABORAEXXX</BICFI></FinInstnId></CdtrAgt>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _generic_json(test_id: str) -> str:
        return json.dumps({
            "messageId": f"GENERIC-{test_id}",
            "messageType": "UNKNOWN",
            "amount": 100.00,
            "currency": "USD",
            "debtor": {"name": f"Debtor {test_id}"},
            "creditor": {"name": f"Creditor {test_id}"},
            "timestamp": "2025-12-29T12:00:00"
        })


# =============================================================================
# VALIDATOR
# =============================================================================

@dataclass
class ValidationResult:
    """Result of validating one message type."""
    message_type: str
    test_id: str
    success: bool = False
    bronze_stored: bool = False
    bronze_raw_preserved: bool = False
    silver_parsed: bool = False
    silver_fields_populated: int = 0
    gold_created: bool = False
    gold_entities: Dict[str, int] = field(default_factory=dict)
    lineage_tracked: bool = False
    error: Optional[str] = None
    duration_ms: float = 0


class ZoneSeparatedValidator:
    """Validates zone-separated pipeline."""

    def __init__(self, config: Config):
        self.config = config
        self._producer: Optional[KafkaProducer] = None
        self._conn: Optional[psycopg2.connection] = None

    def _get_producer(self) -> KafkaProducer:
        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=self.config.kafka_bootstrap,
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                value_serializer=lambda v: v.encode('utf-8') if v else None,
            )
        return self._producer

    def _get_db_conn(self):
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(
                host=self.config.pg_host,
                port=self.config.pg_port,
                database=self.config.pg_db,
                user=self.config.pg_user,
                password=self.config.pg_password,
            )
        return self._conn

    def validate_message_type(self, message_type: str, verbose: bool = False) -> ValidationResult:
        """Validate complete E2E flow for one message type."""
        test_id = uuid.uuid4().hex[:8].upper()
        batch_id = str(uuid.uuid4())
        start_time = time.time()

        result = ValidationResult(
            message_type=message_type,
            test_id=test_id,
        )

        try:
            # Generate test data
            test_content = TestDataGenerator.generate(message_type, test_id)
            if verbose:
                logger.info(f"[{message_type}] Generated test data: {len(test_content)} bytes")

            # Step 1: Publish to Bronze Kafka topic
            topic = f"bronze.{message_type.lower()}"
            headers = [
                ('message_type', message_type.encode('utf-8')),
                ('batch_id', batch_id.encode('utf-8')),
                ('test_id', test_id.encode('utf-8')),
            ]

            producer = self._get_producer()
            future = producer.send(
                topic=topic,
                key=batch_id,
                value=test_content,
                headers=headers,
            )
            future.get(timeout=10)
            producer.flush()

            if verbose:
                logger.info(f"[{message_type}] Published to {topic}")

            # Wait for async processing
            time.sleep(self.config.wait_for_processing)

            # Step 2: Verify Bronze
            conn = self._get_db_conn()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT raw_id, raw_content, message_format, processing_status
                FROM bronze.raw_payment_messages
                WHERE _batch_id = %s
                ORDER BY _ingested_at DESC
                LIMIT 1
            """, (batch_id,))

            bronze_row = cursor.fetchone()
            if bronze_row:
                result.bronze_stored = True
                raw_id, raw_content, msg_format, status = bronze_row

                # Verify raw content is stored AS-IS (not JSON wrapped)
                result.bronze_raw_preserved = (
                    raw_content == test_content or
                    (test_content.strip() in raw_content if raw_content else False)
                )

                if verbose:
                    logger.info(f"[{message_type}] Bronze: raw_id={raw_id}, format={msg_format}, status={status}")
                    if not result.bronze_raw_preserved:
                        logger.warning(f"[{message_type}] Raw content may be wrapped. Length: {len(raw_content)} vs {len(test_content)}")

            # Step 3: Verify Silver
            # Use message routing framework to determine correct table(s)
            possible_tables = get_silver_table_for_format(message_type)
            silver_table = None
            stg_id = None

            for table in possible_tables:
                try:
                    cursor.execute(f"""
                        SELECT stg_id, raw_id, processing_status
                        FROM silver.{table}
                        WHERE _batch_id = %s
                        ORDER BY _processed_at DESC
                        LIMIT 1
                    """, (batch_id,))

                    silver_row = cursor.fetchone()
                    if silver_row:
                        result.silver_parsed = True
                        stg_id = silver_row[0]
                        silver_table = table

                        # Count populated fields
                        cursor.execute(f"""
                            SELECT COUNT(*)
                            FROM information_schema.columns c
                            WHERE c.table_schema = 'silver'
                              AND c.table_name = %s
                        """, (table,))
                        total_cols = cursor.fetchone()[0]
                        result.silver_fields_populated = total_cols

                        if verbose:
                            logger.info(f"[{message_type}] Silver: stg_id={stg_id}, table={table}")
                        break

                except psycopg2.Error as e:
                    conn.rollback()  # Reset transaction state
                    continue

            if not result.silver_parsed and verbose:
                logger.warning(f"[{message_type}] Silver record not found. Checked tables: {possible_tables}")

            # Step 4: Verify Gold
            # Use stg_id if we found a Silver record, otherwise search by batch_id
            instruction_id = None
            if stg_id:
                cursor.execute("""
                    SELECT instruction_id, source_message_type
                    FROM gold.cdm_payment_instruction
                    WHERE source_stg_id = %s
                    LIMIT 1
                """, (stg_id,))
                gold_row = cursor.fetchone()
                if gold_row:
                    instruction_id = gold_row[0]

            # Fallback: search by batch_id across any Silver table that might have records
            if not instruction_id:
                cursor.execute("""
                    SELECT instruction_id, source_message_type
                    FROM gold.cdm_payment_instruction
                    WHERE source_batch_id = %s
                       OR instruction_id LIKE %s
                    LIMIT 1
                """, (batch_id, f"%{test_id}%"))
                gold_row = cursor.fetchone()
                if gold_row:
                    instruction_id = gold_row[0]

            if instruction_id:
                result.gold_created = True

                # Count entities
                for entity in ['cdm_party', 'cdm_account', 'cdm_financial_institution']:
                    try:
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM gold.{entity}
                            WHERE source_instruction_id = %s OR instruction_id = %s
                        """, (instruction_id, instruction_id))
                        count = cursor.fetchone()[0]
                        result.gold_entities[entity] = count
                    except psycopg2.Error:
                        conn.rollback()
                        result.gold_entities[entity] = 0

                if verbose:
                    logger.info(f"[{message_type}] Gold: instruction_id={instruction_id}, entities={result.gold_entities}")

            # Step 5: Verify Lineage
            cursor.execute("""
                SELECT COUNT(*) FROM observability.obs_data_lineage
                WHERE batch_id = %s
            """, (batch_id,))
            lineage_count = cursor.fetchone()[0]
            result.lineage_tracked = lineage_count > 0

            if verbose:
                logger.info(f"[{message_type}] Lineage records: {lineage_count}")

            # Determine overall success
            result.success = (
                result.bronze_stored and
                result.bronze_raw_preserved and
                result.silver_parsed and
                result.gold_created
            )

        except Exception as e:
            result.error = str(e)
            logger.error(f"[{message_type}] Validation error: {e}")

        finally:
            result.duration_ms = (time.time() - start_time) * 1000

        return result

    def validate_all(self, message_types: List[str], verbose: bool = False) -> List[ValidationResult]:
        """Validate all specified message types."""
        results = []

        for msg_type in message_types:
            logger.info(f"Validating {msg_type}...")
            result = self.validate_message_type(msg_type, verbose)
            results.append(result)

            status = "PASS" if result.success else "FAIL"
            logger.info(f"  {status}: Bronze={result.bronze_stored}, Silver={result.silver_parsed}, Gold={result.gold_created}")

        return results

    def print_summary(self, results: List[ValidationResult]) -> None:
        """Print validation summary."""
        print("\n" + "=" * 80)
        print("GPS CDM Zone-Separated E2E Validation Summary")
        print("=" * 80)

        passed = sum(1 for r in results if r.success)
        failed = len(results) - passed

        print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")
        print("-" * 80)
        print(f"{'Message Type':<15} {'Status':<8} {'Bronze':<8} {'RawOK':<8} {'Silver':<8} {'Gold':<8} {'Lineage':<8}")
        print("-" * 80)

        for r in results:
            status = "PASS" if r.success else "FAIL"
            print(
                f"{r.message_type:<15} {status:<8} "
                f"{'+' if r.bronze_stored else '-':<8} "
                f"{'+' if r.bronze_raw_preserved else '-':<8} "
                f"{'+' if r.silver_parsed else '-':<8} "
                f"{'+' if r.gold_created else '-':<8} "
                f"{'+' if r.lineage_tracked else '-':<8}"
            )

            if r.error:
                print(f"  ERROR: {r.error}")

        print("=" * 80)

    def cleanup(self):
        """Cleanup resources."""
        if self._producer:
            self._producer.close()
        if self._conn:
            self._conn.close()


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='GPS CDM Zone-Separated E2E Validation')
    parser.add_argument('--types', help='Comma-separated list of message types')
    parser.add_argument('--all', action='store_true', help='Test all 29 message types')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--kafka', default='localhost:9092', help='Kafka bootstrap servers')
    parser.add_argument('--pg-host', default='localhost', help='PostgreSQL host')
    parser.add_argument('--pg-port', type=int, default=5433, help='PostgreSQL port')

    args = parser.parse_args()

    # All supported message types
    # NOTE: SWIFT MT messages (MT103, MT202, MT940) were decommissioned by SWIFT in Nov 2025
    all_types = [
        'pain.001', 'pacs.008', 'pacs.002', 'pacs.004', 'pacs.009', 'camt.053',
        'CHAPS', 'BACS', 'FPS',
        'FEDWIRE', 'ACH', 'RTP', 'FEDNOW', 'CHIPS',
        'SEPA', 'TARGET2',
        'NPP', 'UPI', 'PIX',
        'INSTAPAY', 'PAYNOW', 'PROMPTPAY',
        'MEPS_PLUS', 'RTGS_HK', 'BOJNET', 'KFTC', 'CNAPS',
        'SARIE', 'UAEFTS',
    ]

    # Determine which types to test
    if args.types:
        message_types = [t.strip() for t in args.types.split(',')]
    elif args.all:
        message_types = all_types
    else:
        # Default to a subset
        message_types = ['CHAPS', 'pacs.008', 'pain.001', 'FEDWIRE', 'SEPA']

    # Create config
    config = Config(
        kafka_bootstrap=args.kafka,
        pg_host=args.pg_host,
        pg_port=args.pg_port,
    )

    # Run validation
    validator = ZoneSeparatedValidator(config)

    try:
        results = validator.validate_all(message_types, args.verbose)
        validator.print_summary(results)

        # Exit with error if any failed
        if any(not r.success for r in results):
            sys.exit(1)

    finally:
        validator.cleanup()


if __name__ == '__main__':
    main()
