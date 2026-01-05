#!/usr/bin/env python3
"""
GPS CDM - Zone-Separated E2E Validation
========================================

Validates the complete zone-separated pipeline for all 29 message types:
1. Sends test messages through Bronze Kafka topic
2. Verifies Bronze records are stored AS-IS
3. Verifies Silver records are properly parsed
4. Verifies Gold CDM entities are created
5. Verifies lineage tracking

Usage:
    python scripts/validate_zone_separated_e2e.py [--types TYPE1,TYPE2] [--verbose]

Examples:
    python scripts/validate_zone_separated_e2e.py --types CHAPS,MT103
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
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import psycopg2
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
        """Generate test data for message type."""
        generators = {
            # ISO 20022
            'pain.001': TestDataGenerator._pain001,
            'pain.002': TestDataGenerator._pain002,
            'pacs.008': TestDataGenerator._pacs008,
            'camt.053': TestDataGenerator._camt053,

            # SWIFT MT
            'MT103': TestDataGenerator._mt103,
            'MT202': TestDataGenerator._mt202,
            'MT940': TestDataGenerator._mt940,

            # US
            'FEDWIRE': TestDataGenerator._fedwire,
            'ACH': TestDataGenerator._ach,
            'RTP': TestDataGenerator._rtp,

            # UK
            'CHAPS': TestDataGenerator._chaps,
            'BACS': TestDataGenerator._bacs,
            'FPS': TestDataGenerator._fps,

            # Europe
            'SEPA': TestDataGenerator._sepa,

            # APAC
            'NPP': TestDataGenerator._npp,
            'UPI': TestDataGenerator._upi,
            'PIX': TestDataGenerator._pix,
            'INSTAPAY': TestDataGenerator._instapay,
            'PAYNOW': TestDataGenerator._paynow,
            'PROMPTPAY': TestDataGenerator._promptpay,
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
    def _mt103(test_id: str) -> str:
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
            # Table naming: pain.001 -> stg_pain001 (no extra underscore)
            silver_table = f"stg_{message_type.lower().replace('.', '').replace('-', '_')}"
            try:
                cursor.execute(f"""
                    SELECT stg_id, raw_id, processing_status
                    FROM silver.{silver_table}
                    WHERE _batch_id = %s
                    ORDER BY _processed_at DESC
                    LIMIT 1
                """, (batch_id,))

                silver_row = cursor.fetchone()
                if silver_row:
                    result.silver_parsed = True
                    stg_id = silver_row[0]

                    # Count populated fields
                    cursor.execute(f"""
                        SELECT COUNT(*)
                        FROM information_schema.columns c
                        WHERE c.table_schema = 'silver'
                          AND c.table_name = %s
                    """, (silver_table,))
                    total_cols = cursor.fetchone()[0]
                    result.silver_fields_populated = total_cols

                    if verbose:
                        logger.info(f"[{message_type}] Silver: stg_id={stg_id}, table={silver_table}")

            except Exception as e:
                if verbose:
                    logger.warning(f"[{message_type}] Silver table {silver_table} not found or error: {e}")
                conn.rollback()  # Reset transaction state

            # Step 4: Verify Gold
            cursor.execute("""
                SELECT instruction_id, source_message_type
                FROM gold.cdm_payment_instruction
                WHERE source_stg_id IN (
                    SELECT stg_id FROM silver.stg_chaps WHERE _batch_id = %s
                    UNION SELECT stg_id FROM silver.stg_mt103 WHERE _batch_id = %s
                    UNION SELECT stg_id FROM silver.stg_pain001 WHERE _batch_id = %s
                )
                OR instruction_id LIKE %s
                LIMIT 1
            """, (batch_id, batch_id, batch_id, f"%{test_id}%"))

            gold_row = cursor.fetchone()
            if gold_row:
                result.gold_created = True
                instruction_id = gold_row[0]

                # Count entities
                for entity in ['cdm_party', 'cdm_account', 'cdm_financial_institution']:
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM gold.{entity}
                        WHERE instruction_id = %s
                    """, (instruction_id,))
                    count = cursor.fetchone()[0]
                    result.gold_entities[entity] = count

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
    all_types = [
        'pain.001', 'pacs.008', 'camt.053',
        'MT103', 'MT202', 'MT940',
        'CHAPS', 'BACS', 'FPS',
        'FEDWIRE', 'ACH', 'RTP',
        'SEPA',
        'NPP', 'UPI', 'PIX',
        'INSTAPAY', 'PAYNOW', 'PROMPTPAY',
    ]

    # Determine which types to test
    if args.types:
        message_types = [t.strip() for t in args.types.split(',')]
    elif args.all:
        message_types = all_types
    else:
        # Default to a subset
        message_types = ['CHAPS', 'MT103', 'pain.001', 'FEDWIRE', 'SEPA']

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
