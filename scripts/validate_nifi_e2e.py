#!/usr/bin/env python3
"""
GPS CDM - NiFi-Based E2E Validation
====================================

Validates the complete NiFi → Kafka → Celery/Zone-Consumers → DB pipeline.

This script does NOT publish directly to Kafka. Instead it:
1. Creates test files with proper naming (message_type_batch_id.extension)
2. Copies files to NiFi input directory via docker cp + tar
3. Waits for NiFi to pick up files and publish to Kafka
4. Waits for Celery/zone consumers to process through all zones
5. Validates data in Bronze, Silver, Gold tables

Usage:
    python scripts/validate_nifi_e2e.py --types pain.001,MT103 --verbose
    python scripts/validate_nifi_e2e.py --types pain.001,MT103,pacs.008,FEDWIRE,ACH,SEPA,RTP -v

Requirements:
    - Docker containers running (gps-cdm-nifi, gps-cdm-postgres, gps-cdm-kafka)
    - Celery worker running with zone queues
    - Zone consumers running (bronze, silver, gold)
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import psycopg2

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

    # NiFi
    nifi_container: str = "gps-cdm-nifi"
    nifi_input_dir: str = "/opt/nifi/nifi-current/input/"

    # PostgreSQL
    pg_host: str = "localhost"
    pg_port: int = 5433
    pg_db: str = "gps_cdm"
    pg_user: str = "gps_cdm_svc"
    pg_password: str = "gps_cdm_password"

    # Timing (seconds)
    nifi_poll_interval: int = 30  # NiFi GetFile polls every 30s
    processing_wait: int = 10     # Wait for Celery/consumers
    total_timeout: int = 120      # Max wait time


# =============================================================================
# TEST DATA GENERATOR
# =============================================================================

class TestDataGenerator:
    """Generates compliant test data files for each message type."""

    @staticmethod
    def get_file_extension(message_type: str) -> str:
        """Get proper file extension for message type."""
        xml_types = ['pain.001', 'pain.002', 'pacs.008', 'camt.053', 'SEPA', 'RTP',
                     'FPS', 'NPP', 'INSTAPAY', 'PAYNOW', 'PROMPTPAY', 'CHAPS']
        json_types = ['UPI', 'PIX']

        if message_type in xml_types:
            return 'xml'
        elif message_type in json_types:
            return 'json'
        elif message_type.startswith('MT') or message_type in ['BACS']:
            return 'txt'
        elif message_type == 'ACH':
            return 'txt'
        elif message_type == 'FEDWIRE':
            return 'txt'
        else:
            return 'txt'

    @staticmethod
    def generate(message_type: str, batch_id: str, num_records: int = 3) -> str:
        """Generate test data with multiple records where applicable."""
        generators = {
            'pain.001': TestDataGenerator._pain001_multi,
            'pacs.008': TestDataGenerator._pacs008_multi,
            'MT103': TestDataGenerator._mt103_multi,
            'FEDWIRE': TestDataGenerator._fedwire_multi,
            'ACH': TestDataGenerator._ach_multi,
            'SEPA': TestDataGenerator._sepa_multi,
            'RTP': TestDataGenerator._rtp_multi,
        }

        generator = generators.get(message_type, TestDataGenerator._generic)
        return generator(batch_id, num_records)

    @staticmethod
    def _pain001_multi(batch_id: str, num_records: int) -> str:
        """Generate pain.001 with multiple payment instructions."""
        payments = ""
        for i in range(num_records):
            payments += f"""
    <PmtInf>
      <PmtInfId>PMT-{batch_id}-{i+1}</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>{1000 * (i+1)}.00</CtrlSum>
      <Dbtr>
        <Nm>Test Debtor {i+1}</Nm>
        <PstlAdr><Ctry>US</Ctry></PstlAdr>
      </Dbtr>
      <DbtrAcct><Id><IBAN>US1234567890123456789{i}</IBAN></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BICFI>TESTUS33XXX</BICFI></FinInstnId></DbtrAgt>
      <CdtTrfTxInf>
        <PmtId><EndToEndId>E2E-{batch_id}-{i+1}</EndToEndId></PmtId>
        <Amt><InstdAmt Ccy="USD">{1000 * (i+1)}.00</InstdAmt></Amt>
        <Cdtr><Nm>Test Creditor {i+1}</Nm></Cdtr>
        <CdtrAcct><Id><IBAN>GB8765432109876543210{i}</IBAN></Id></CdtrAcct>
      </CdtTrfTxInf>
    </PmtInf>"""

        total = sum(1000 * (i+1) for i in range(num_records))
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>PAIN001-{batch_id}</MsgId>
      <CreDtTm>{datetime.now().isoformat()}</CreDtTm>
      <NbOfTxs>{num_records}</NbOfTxs>
      <CtrlSum>{total}.00</CtrlSum>
      <InitgPty><Nm>Test Initiator</Nm></InitgPty>
    </GrpHdr>{payments}
  </CstmrCdtTrfInitn>
</Document>'''

    @staticmethod
    def _pacs008_multi(batch_id: str, num_records: int) -> str:
        """Generate pacs.008 with multiple credit transfers."""
        transfers = ""
        for i in range(num_records):
            transfers += f"""
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>INSTR-{batch_id}-{i+1}</InstrId>
        <EndToEndId>E2E-{batch_id}-{i+1}</EndToEndId>
        <TxId>TXN-{batch_id}-{i+1}</TxId>
      </PmtId>
      <IntrBkSttlmAmt Ccy="EUR">{2500 * (i+1)}.00</IntrBkSttlmAmt>
      <Dbtr><Nm>Debtor {i+1} Corp</Nm></Dbtr>
      <DbtrAcct><Id><IBAN>DE8937040044053201300{i}</IBAN></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BICFI>COBADEFFXXX</BICFI></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><BICFI>BNPAFRPPXXX</BICFI></FinInstnId></CdtrAgt>
      <Cdtr><Nm>Creditor {i+1} Ltd</Nm></Cdtr>
      <CdtrAcct><Id><IBAN>FR763000600001123456789018{i}</IBAN></Id></CdtrAcct>
    </CdtTrfTxInf>"""

        total = sum(2500 * (i+1) for i in range(num_records))
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>PACS008-{batch_id}</MsgId>
      <CreDtTm>{datetime.now().isoformat()}</CreDtTm>
      <NbOfTxs>{num_records}</NbOfTxs>
      <TtlIntrBkSttlmAmt Ccy="EUR">{total}.00</TtlIntrBkSttlmAmt>
      <SttlmInf><SttlmMtd>CLRG</SttlmMtd></SttlmInf>
    </GrpHdr>{transfers}
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _mt103_multi(batch_id: str, num_records: int) -> str:
        """Generate multiple MT103 messages (concatenated)."""
        messages = []
        for i in range(num_records):
            msg = f'''{{1:F01TESTUS33XXXX000000000{i+1}}}{{2:O1031200{datetime.now().strftime('%y%m%d')}TESTGB2LXXXX0000000000{i+1}{datetime.now().strftime('%y%m%d')}1200N}}{{3:{{108:MT103{batch_id[:8]}{i+1}}}}}{{4:
:20:TXN-{batch_id[:8]}-{i+1}
:23B:CRED
:32A:{datetime.now().strftime('%y%m%d')}USD{1500 * (i+1)},00
:50K:/US123456789{i}
DEBTOR {i+1} COMPANY
{100 + i} TEST STREET
NEW YORK NY 10001
USA
:52A:TESTUS33XXX
:57A:TESTGB2LXXX
:59:/GB987654321{i}
CREDITOR {i+1} LIMITED
{200 + i} MAIN ROAD
LONDON EC1A 1BB
UK
:70:PAYMENT {batch_id[:8]}-{i+1}
:71A:SHA
-}}{{5:{{CHK:TEST{i+1}}}}}'''
            messages.append(msg)

        return '\n'.join(messages)

    @staticmethod
    def _fedwire_multi(batch_id: str, num_records: int) -> str:
        """Generate multiple FEDWIRE messages."""
        messages = []
        for i in range(num_records):
            amount = str(10000 * (i + 1)).zfill(12)
            msg = f'''{{1500}}00
{{1510}}1000
{{1520}}FED{batch_id[:8]}{i+1}
{{2000}}{amount}
{{3100}}021000089
{{3320}}ORIG BANK {i+1}
{{3400}}021000021
{{3420}}BENE BANK {i+1}
{{4000}}ORIG{batch_id[:6]}{i+1}
{{4100}}/US123456789{i}
ORIGINATOR {i+1} CORP
123 ORIG STREET
NEW YORK NY 10001
{{4200}}/US987654321{i}
BENEFICIARY {i+1} INC
456 BENE AVENUE
CHICAGO IL 60601
{{5000}}FEDWIRE PAYMENT {batch_id[:8]}-{i+1}
{{6000}}REF{batch_id[:8]}{i+1}'''
            messages.append(msg)

        return '\n---\n'.join(messages)

    @staticmethod
    def _ach_multi(batch_id: str, num_records: int) -> str:
        """Generate NACHA ACH file with multiple entries."""
        date = datetime.now().strftime('%y%m%d')
        time_str = datetime.now().strftime('%H%M')

        # File header (94 chars)
        file_header = f"101 021000089 123456789{date}{time_str}A094101GPS CDM TEST       ORIGINATOR         ".ljust(94)

        lines = [file_header]
        entry_count = 0
        total_debit = 0
        total_credit = 0

        for batch_num in range(num_records):
            # Batch header
            company_name = f"COMPANY {batch_num+1}".ljust(16)
            batch_header = f"5200{company_name}1234567890PPDPAYROLL   {date}{date}   1021000890{str(batch_num+1).zfill(7)}".ljust(94)
            lines.append(batch_header)

            # Entry detail (2 entries per batch)
            for entry in range(2):
                amount = 100000 * (batch_num + 1) + entry * 10000  # Amount in cents
                trace = f"0210000890{str(entry_count + 1).zfill(7)}"
                entry_detail = f"6220210000891234567890{str(batch_num)}{str(amount).zfill(10)}{batch_id[:15].ljust(15)}PAYEE {batch_num+1}-{entry+1}         0{trace}".ljust(94)
                lines.append(entry_detail)
                entry_count += 1
                total_credit += amount

            # Batch control
            entry_hash = 21000089 * 2  # Sum of routing numbers
            batch_control = f"8200{str(2).zfill(6)}{str(entry_hash).zfill(10)}{str(0).zfill(12)}{str(total_credit).zfill(12)}1234567890                         021000890{str(batch_num+1).zfill(7)}".ljust(94)
            lines.append(batch_control)

        # File control
        block_count = (len(lines) + 1 + 9) // 10  # Round up to next 10
        file_control = f"9{str(num_records).zfill(6)}{str(block_count).zfill(6)}{str(entry_count).zfill(8)}{str(21000089 * entry_count).zfill(10)}{str(total_debit).zfill(12)}{str(total_credit).zfill(12)}".ljust(94)
        lines.append(file_control)

        # Pad to block of 10
        while len(lines) % 10 != 0:
            lines.append('9' * 94)

        return '\n'.join(lines)

    @staticmethod
    def _sepa_multi(batch_id: str, num_records: int) -> str:
        """Generate SEPA pain.001 with multiple payments."""
        payments = ""
        for i in range(num_records):
            payments += f"""
    <PmtInf>
      <PmtInfId>SEPA-{batch_id}-{i+1}</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <BtchBookg>true</BtchBookg>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>{150 * (i+1)}.00</CtrlSum>
      <PmtTpInf><SvcLvl><Cd>SEPA</Cd></SvcLvl></PmtTpInf>
      <ReqdExctnDt>{datetime.now().strftime('%Y-%m-%d')}</ReqdExctnDt>
      <Dbtr><Nm>SEPA Debtor {i+1}</Nm></Dbtr>
      <DbtrAcct><Id><IBAN>DE8937040044053201300{i}</IBAN></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BIC>COBADEFFXXX</BIC></FinInstnId></DbtrAgt>
      <ChrgBr>SLEV</ChrgBr>
      <CdtTrfTxInf>
        <PmtId><EndToEndId>SEPA-E2E-{batch_id}-{i+1}</EndToEndId></PmtId>
        <Amt><InstdAmt Ccy="EUR">{150 * (i+1)}.00</InstdAmt></Amt>
        <CdtrAgt><FinInstnId><BIC>BNPAFRPPXXX</BIC></FinInstnId></CdtrAgt>
        <Cdtr><Nm>SEPA Creditor {i+1}</Nm></Cdtr>
        <CdtrAcct><Id><IBAN>FR763000600001123456789018{i}</IBAN></Id></CdtrAcct>
        <RmtInf><Ustrd>SEPA Payment {batch_id}-{i+1}</Ustrd></RmtInf>
      </CdtTrfTxInf>
    </PmtInf>"""

        total = sum(150 * (i+1) for i in range(num_records))
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>SEPA-{batch_id}</MsgId>
      <CreDtTm>{datetime.now().isoformat()}</CreDtTm>
      <NbOfTxs>{num_records}</NbOfTxs>
      <CtrlSum>{total}.00</CtrlSum>
      <InitgPty><Nm>SEPA Initiator</Nm></InitgPty>
    </GrpHdr>{payments}
  </CstmrCdtTrfInitn>
</Document>'''

    @staticmethod
    def _rtp_multi(batch_id: str, num_records: int) -> str:
        """Generate RTP pacs.008 with multiple instant payments."""
        transfers = ""
        for i in range(num_records):
            transfers += f"""
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>RTP-{batch_id}-{i+1}</InstrId>
        <EndToEndId>RTP-E2E-{batch_id}-{i+1}</EndToEndId>
        <TxId>RTPTXN-{batch_id}-{i+1}</TxId>
      </PmtId>
      <IntrBkSttlmAmt Ccy="USD">{500 * (i+1)}.00</IntrBkSttlmAmt>
      <AccptncDtTm>{datetime.now().isoformat()}</AccptncDtTm>
      <ChrgBr>SLEV</ChrgBr>
      <Dbtr><Nm>RTP Debtor {i+1}</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>123456789{i}</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>021000089</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>021000021</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>RTP Creditor {i+1}</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>987654321{i}</Id></Othr></Id></CdtrAcct>
      <RmtInf><Ustrd>RTP Payment {batch_id}-{i+1}</Ustrd></RmtInf>
    </CdtTrfTxInf>"""

        total = sum(500 * (i+1) for i in range(num_records))
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>RTP-{batch_id}</MsgId>
      <CreDtTm>{datetime.now().isoformat()}</CreDtTm>
      <NbOfTxs>{num_records}</NbOfTxs>
      <TtlIntrBkSttlmAmt Ccy="USD">{total}.00</TtlIntrBkSttlmAmt>
      <SttlmInf><SttlmMtd>CLRG</SttlmMtd></SttlmInf>
    </GrpHdr>{transfers}
  </FIToFICstmrCdtTrf>
</Document>'''

    @staticmethod
    def _generic(batch_id: str, num_records: int) -> str:
        """Generic JSON message."""
        return json.dumps({
            "messageId": f"GENERIC-{batch_id}",
            "records": [
                {"id": f"REC-{batch_id}-{i}", "amount": 100 * i}
                for i in range(num_records)
            ]
        }, indent=2)


# =============================================================================
# NIFI FILE COPIER
# =============================================================================

class NiFiFileCopier:
    """Copies files to NiFi input directory using tar method."""

    def __init__(self, config: Config):
        self.config = config

    def copy_to_nifi(self, local_path: str, remote_name: str) -> bool:
        """
        Copy file to NiFi input directory using tar method.
        This ensures proper permissions for NiFi to read the file.
        """
        try:
            # Create temp directory with the file
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, remote_name)

            # Copy with readable permissions
            with open(local_path, 'r') as src:
                content = src.read()
            with open(temp_file, 'w') as dst:
                dst.write(content)
            os.chmod(temp_file, 0o644)

            # Use tar to copy to container (preserves permissions, sets nifi as owner)
            cmd = f"cd {temp_dir} && tar cf - . | docker exec -i {self.config.nifi_container} tar xf - -C {self.config.nifi_input_dir}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            # Clean up macOS metadata files
            cleanup_cmd = f"docker exec {self.config.nifi_container} bash -c 'rm -f {self.config.nifi_input_dir}/._*' 2>/dev/null || true"
            subprocess.run(cleanup_cmd, shell=True, capture_output=True)

            # Clean up temp directory
            os.remove(temp_file)
            os.rmdir(temp_dir)

            if result.returncode != 0 and "Cannot utime" not in result.stderr and "Cannot change mode" not in result.stderr:
                logger.error(f"Failed to copy to NiFi: {result.stderr}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error copying to NiFi: {e}")
            return False

    def verify_file_exists(self, filename: str) -> bool:
        """Check if file exists in NiFi input directory."""
        cmd = f"docker exec {self.config.nifi_container} test -f {self.config.nifi_input_dir}/{filename}"
        result = subprocess.run(cmd, shell=True, capture_output=True)
        return result.returncode == 0

    def list_files(self) -> List[str]:
        """List files in NiFi input directory."""
        cmd = f"docker exec {self.config.nifi_container} ls -la {self.config.nifi_input_dir}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')
        return []


# =============================================================================
# VALIDATOR
# =============================================================================

@dataclass
class ValidationResult:
    """Result of validating one message type."""
    message_type: str
    batch_id: str
    num_records: int
    success: bool = False

    # Pipeline stages
    file_created: bool = False
    file_copied_to_nifi: bool = False
    nifi_picked_up: bool = False

    # Zone validation
    bronze_count: int = 0
    silver_count: int = 0
    gold_instruction_count: int = 0
    gold_party_count: int = 0
    gold_account_count: int = 0
    gold_fi_count: int = 0

    # Errors
    error: Optional[str] = None

    @property
    def bronze_ok(self) -> bool:
        return self.bronze_count > 0

    @property
    def silver_ok(self) -> bool:
        return self.silver_count > 0

    @property
    def gold_ok(self) -> bool:
        return self.gold_instruction_count > 0


class NiFiE2EValidator:
    """Validates NiFi-based E2E pipeline."""

    def __init__(self, config: Config):
        self.config = config
        self.copier = NiFiFileCopier(config)
        self._conn = None

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

    def validate_message_type(self, message_type: str, num_records: int = 3,
                             verbose: bool = False) -> ValidationResult:
        """Validate complete NiFi E2E flow for one message type."""
        batch_id = uuid.uuid4().hex[:12]

        result = ValidationResult(
            message_type=message_type,
            batch_id=batch_id,
            num_records=num_records,
        )

        try:
            # Step 1: Generate test data
            test_content = TestDataGenerator.generate(message_type, batch_id, num_records)
            extension = TestDataGenerator.get_file_extension(message_type)
            filename = f"{message_type}_{batch_id}.{extension}"

            if verbose:
                logger.info(f"[{message_type}] Generated {len(test_content)} bytes, {num_records} records")

            # Step 2: Write to temp file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=f'.{extension}', delete=False)
            temp_file.write(test_content)
            temp_file.close()
            result.file_created = True

            if verbose:
                logger.info(f"[{message_type}] Created temp file: {temp_file.name}")

            # Step 3: Copy to NiFi input directory
            if self.copier.copy_to_nifi(temp_file.name, filename):
                result.file_copied_to_nifi = True
                if verbose:
                    logger.info(f"[{message_type}] Copied to NiFi: {filename}")
            else:
                result.error = "Failed to copy file to NiFi"
                return result

            # Clean up temp file
            os.unlink(temp_file.name)

            # Step 4: Wait for NiFi to pick up file
            logger.info(f"[{message_type}] Waiting for NiFi to process (up to {self.config.nifi_poll_interval + 5}s)...")

            start_wait = time.time()
            while time.time() - start_wait < self.config.nifi_poll_interval + 5:
                if not self.copier.verify_file_exists(filename):
                    result.nifi_picked_up = True
                    if verbose:
                        logger.info(f"[{message_type}] NiFi picked up file after {time.time() - start_wait:.1f}s")
                    break
                time.sleep(2)

            if not result.nifi_picked_up:
                # Check file permissions if still there
                files = self.copier.list_files()
                if verbose:
                    logger.warning(f"[{message_type}] File still in input dir. Contents:")
                    for f in files:
                        logger.warning(f"  {f}")
                result.error = "NiFi did not pick up file within timeout"
                return result

            # Step 5: Wait for Celery/zone consumers to process
            logger.info(f"[{message_type}] Waiting for zone processing ({self.config.processing_wait}s)...")
            time.sleep(self.config.processing_wait)

            # Step 6: Validate Bronze
            conn = self._get_db_conn()
            cursor = conn.cursor()

            # Find records by message content pattern (batch_id should be in raw_content)
            cursor.execute("""
                SELECT COUNT(*)
                FROM bronze.raw_payment_messages
                WHERE message_type ILIKE %s
                  AND raw_content LIKE %s
            """, (message_type, f"%{batch_id}%"))
            result.bronze_count = cursor.fetchone()[0]

            if verbose:
                logger.info(f"[{message_type}] Bronze records: {result.bronze_count}")

            # Step 7: Validate Silver
            # Determine Silver table name
            silver_table = f"stg_{message_type.lower().replace('.', '').replace('-', '_')}"

            try:
                # First check if table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'silver' AND table_name = %s
                    )
                """, (silver_table,))

                if cursor.fetchone()[0]:
                    # Find silver records by looking for batch_id pattern in linked bronze records
                    cursor.execute(f"""
                        SELECT COUNT(*)
                        FROM silver.{silver_table} s
                        JOIN bronze.raw_payment_messages b ON s.raw_id = b.raw_id
                        WHERE b.raw_content LIKE %s
                    """, (f"%{batch_id}%",))
                    result.silver_count = cursor.fetchone()[0]

                    if verbose:
                        logger.info(f"[{message_type}] Silver records ({silver_table}): {result.silver_count}")
                else:
                    if verbose:
                        logger.warning(f"[{message_type}] Silver table {silver_table} does not exist")

            except Exception as e:
                if verbose:
                    logger.warning(f"[{message_type}] Silver query error: {e}")
                conn.rollback()

            # Step 8: Validate Gold
            try:
                # Find gold instructions linked to our silver records
                if result.silver_count > 0:
                    cursor.execute(f"""
                        SELECT i.instruction_id
                        FROM gold.cdm_payment_instruction i
                        JOIN silver.{silver_table} s ON i.source_stg_id = s.stg_id
                        JOIN bronze.raw_payment_messages b ON s.raw_id = b.raw_id
                        WHERE b.raw_content LIKE %s
                    """, (f"%{batch_id}%",))

                    instruction_ids = [row[0] for row in cursor.fetchall()]
                    result.gold_instruction_count = len(instruction_ids)

                    if instruction_ids:
                        # Count parties
                        cursor.execute("""
                            SELECT COUNT(*) FROM gold.cdm_party
                            WHERE instruction_id = ANY(%s)
                        """, (instruction_ids,))
                        result.gold_party_count = cursor.fetchone()[0]

                        # Count accounts
                        cursor.execute("""
                            SELECT COUNT(*) FROM gold.cdm_account
                            WHERE instruction_id = ANY(%s)
                        """, (instruction_ids,))
                        result.gold_account_count = cursor.fetchone()[0]

                        # Count FIs
                        cursor.execute("""
                            SELECT COUNT(*) FROM gold.cdm_financial_institution
                            WHERE instruction_id = ANY(%s)
                        """, (instruction_ids,))
                        result.gold_fi_count = cursor.fetchone()[0]

                if verbose:
                    logger.info(f"[{message_type}] Gold: {result.gold_instruction_count} instructions, "
                              f"{result.gold_party_count} parties, {result.gold_account_count} accounts, "
                              f"{result.gold_fi_count} FIs")

            except Exception as e:
                if verbose:
                    logger.warning(f"[{message_type}] Gold query error: {e}")
                conn.rollback()

            # Determine success
            result.success = result.bronze_ok and result.silver_ok and result.gold_ok

        except Exception as e:
            result.error = str(e)
            logger.error(f"[{message_type}] Validation error: {e}")

        return result

    def validate_all(self, message_types: List[str], num_records: int = 3,
                    verbose: bool = False) -> List[ValidationResult]:
        """Validate all message types."""
        results = []

        for msg_type in message_types:
            logger.info(f"\n{'='*60}")
            logger.info(f"Validating {msg_type}...")
            logger.info(f"{'='*60}")

            result = self.validate_message_type(msg_type, num_records, verbose)
            results.append(result)

            status = "PASS" if result.success else "FAIL"
            logger.info(f"  {status}: Bronze={result.bronze_count}, Silver={result.silver_count}, "
                       f"Gold={result.gold_instruction_count} instructions")

        return results

    def print_summary(self, results: List[ValidationResult]) -> None:
        """Print validation summary."""
        print("\n" + "=" * 100)
        print("GPS CDM NiFi-Based E2E Validation Summary")
        print("=" * 100)

        passed = sum(1 for r in results if r.success)
        failed = len(results) - passed

        print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")
        print("-" * 100)
        print(f"{'Type':<12} {'Status':<8} {'NiFi':<6} {'Bronze':<8} {'Silver':<8} {'Gold':<8} {'Parties':<8} {'Accounts':<8} {'FIs':<6}")
        print("-" * 100)

        for r in results:
            status = "PASS" if r.success else "FAIL"
            nifi = "+" if r.nifi_picked_up else "-"
            print(
                f"{r.message_type:<12} {status:<8} {nifi:<6} "
                f"{r.bronze_count:<8} {r.silver_count:<8} {r.gold_instruction_count:<8} "
                f"{r.gold_party_count:<8} {r.gold_account_count:<8} {r.gold_fi_count:<6}"
            )

            if r.error:
                print(f"  ERROR: {r.error}")

        print("=" * 100)

        # Print data element coverage per message type
        print("\nData Element Coverage:")
        print("-" * 60)
        for r in results:
            if r.success:
                coverage = []
                if r.gold_party_count > 0:
                    coverage.append(f"parties({r.gold_party_count})")
                if r.gold_account_count > 0:
                    coverage.append(f"accounts({r.gold_account_count})")
                if r.gold_fi_count > 0:
                    coverage.append(f"FIs({r.gold_fi_count})")
                print(f"  {r.message_type}: {', '.join(coverage) if coverage else 'no entities'}")

    def cleanup(self):
        """Cleanup resources."""
        if self._conn:
            self._conn.close()


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='GPS CDM NiFi-Based E2E Validation')
    parser.add_argument('--types', required=True, help='Comma-separated list of message types')
    parser.add_argument('--records', type=int, default=3, help='Number of records per test file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--pg-host', default='localhost', help='PostgreSQL host')
    parser.add_argument('--pg-port', type=int, default=5433, help='PostgreSQL port')
    parser.add_argument('--nifi-wait', type=int, default=35, help='NiFi poll wait time (seconds)')
    parser.add_argument('--process-wait', type=int, default=15, help='Processing wait time (seconds)')

    args = parser.parse_args()

    message_types = [t.strip() for t in args.types.split(',')]

    config = Config(
        pg_host=args.pg_host,
        pg_port=args.pg_port,
        nifi_poll_interval=args.nifi_wait,
        processing_wait=args.process_wait,
    )

    validator = NiFiE2EValidator(config)

    try:
        results = validator.validate_all(message_types, args.records, args.verbose)
        validator.print_summary(results)

        # Exit with error if any failed
        if any(not r.success for r in results):
            sys.exit(1)

    finally:
        validator.cleanup()


if __name__ == '__main__':
    main()
