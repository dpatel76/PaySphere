#!/usr/bin/env python3
"""
E2E Multi-Record Test Script
=============================

Creates multi-record test files for all 29 message formats and validates
end-to-end processing through NiFi → Kafka → Celery → Bronze → Silver → Gold.

Each test file contains 3 records to verify batch processing works correctly.

Usage:
    # Set environment variables
    export GPS_CDM_DATA_SOURCE=postgresql
    export POSTGRES_HOST=localhost
    export POSTGRES_PORT=5433
    export POSTGRES_DB=gps_cdm
    export POSTGRES_USER=gps_cdm_svc
    export POSTGRES_PASSWORD=gps_cdm_password

    # Run the test
    python scripts/e2e_multi_record_test.py
"""

import os
import sys
import json
import uuid
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# =============================================================================
# TEST FILE GENERATORS - Multi-record files for each format
# =============================================================================

def generate_pain001_multi() -> str:
    """Generate pain.001 XML with 3 transactions."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>PAIN001-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-05T10:00:00</CreDtTm>
      <NbOfTxs>3</NbOfTxs>
      <CtrlSum>3000.00</CtrlSum>
      <InitgPty><Nm>ACME Corporation</Nm></InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>PMT-001</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <ReqdExctnDt><Dt>2025-01-06</Dt></ReqdExctnDt>
      <Dbtr><Nm>ACME Corporation</Nm><PstlAdr><Ctry>US</Ctry></PstlAdr></Dbtr>
      <DbtrAcct><Id><IBAN>US33BANK12345678901234</IBAN></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BICFI>BANKUS33XXX</BICFI></FinInstnId></DbtrAgt>
      <CdtTrfTxInf>
        <PmtId><InstrId>INSTR-001</InstrId><EndToEndId>E2E-001</EndToEndId></PmtId>
        <Amt><InstdAmt Ccy="USD">1000.00</InstdAmt></Amt>
        <CdtrAgt><FinInstnId><BICFI>CREDUS33XXX</BICFI></FinInstnId></CdtrAgt>
        <Cdtr><Nm>Vendor Alpha</Nm></Cdtr>
        <CdtrAcct><Id><IBAN>US44CRED98765432109876</IBAN></Id></CdtrAcct>
        <RmtInf><Ustrd>Invoice INV-001 payment</Ustrd></RmtInf>
      </CdtTrfTxInf>
      <CdtTrfTxInf>
        <PmtId><InstrId>INSTR-002</InstrId><EndToEndId>E2E-002</EndToEndId></PmtId>
        <Amt><InstdAmt Ccy="USD">1000.00</InstdAmt></Amt>
        <CdtrAgt><FinInstnId><BICFI>CREDUS44XXX</BICFI></FinInstnId></CdtrAgt>
        <Cdtr><Nm>Vendor Beta</Nm></Cdtr>
        <CdtrAcct><Id><IBAN>US55CRED11111111111111</IBAN></Id></CdtrAcct>
        <RmtInf><Ustrd>Invoice INV-002 payment</Ustrd></RmtInf>
      </CdtTrfTxInf>
      <CdtTrfTxInf>
        <PmtId><InstrId>INSTR-003</InstrId><EndToEndId>E2E-003</EndToEndId></PmtId>
        <Amt><InstdAmt Ccy="USD">1000.00</InstdAmt></Amt>
        <CdtrAgt><FinInstnId><BICFI>CREDUS55XXX</BICFI></FinInstnId></CdtrAgt>
        <Cdtr><Nm>Vendor Gamma</Nm></Cdtr>
        <CdtrAcct><Id><IBAN>US66CRED22222222222222</IBAN></Id></CdtrAcct>
        <RmtInf><Ustrd>Invoice INV-003 payment</Ustrd></RmtInf>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


def generate_pacs008_multi() -> str:
    """Generate pacs.008 XML with 3 transactions."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>PACS008-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-05T11:00:00</CreDtTm>
      <NbOfTxs>3</NbOfTxs>
      <SttlmInf><SttlmMtd>INDA</SttlmMtd></SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>PACS-001</InstrId><EndToEndId>PACS-E2E-001</EndToEndId><UETR>a1b2c3d4-e5f6-7890-abcd-ef1234567890</UETR></PmtId>
      <IntrBkSttlmAmt Ccy="EUR">5000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2025-01-06</IntrBkSttlmDt>
      <ChrgBr>SLEV</ChrgBr>
      <InstgAgt><FinInstnId><BICFI>INSTEU2LXXX</BICFI></FinInstnId></InstgAgt>
      <InstdAgt><FinInstnId><BICFI>INSTDEU2XXX</BICFI></FinInstnId></InstdAgt>
      <Dbtr><Nm>European Debtor 1</Nm></Dbtr>
      <DbtrAcct><Id><IBAN>DE89370400440532013000</IBAN></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BICFI>DEUTDEFFXXX</BICFI></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><BICFI>ABORFRPPXXX</BICFI></FinInstnId></CdtrAgt>
      <Cdtr><Nm>French Creditor 1</Nm></Cdtr>
      <CdtrAcct><Id><IBAN>FR7630006000011234567890189</IBAN></Id></CdtrAcct>
      <RmtInf><Ustrd>PACS Payment 1</Ustrd></RmtInf>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>PACS-002</InstrId><EndToEndId>PACS-E2E-002</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="EUR">7500.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2025-01-06</IntrBkSttlmDt>
      <Dbtr><Nm>European Debtor 2</Nm></Dbtr>
      <DbtrAcct><Id><IBAN>DE89370400440532013001</IBAN></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BICFI>DEUTDEFFXXX</BICFI></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><BICFI>ABORFRPPXXX</BICFI></FinInstnId></CdtrAgt>
      <Cdtr><Nm>French Creditor 2</Nm></Cdtr>
      <CdtrAcct><Id><IBAN>FR7630006000011234567890190</IBAN></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>PACS-003</InstrId><EndToEndId>PACS-E2E-003</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="EUR">2500.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2025-01-06</IntrBkSttlmDt>
      <Dbtr><Nm>European Debtor 3</Nm></Dbtr>
      <DbtrAcct><Id><IBAN>DE89370400440532013002</IBAN></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BICFI>DEUTDEFFXXX</BICFI></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><BICFI>ABORFRPPXXX</BICFI></FinInstnId></CdtrAgt>
      <Cdtr><Nm>French Creditor 3</Nm></Cdtr>
      <CdtrAcct><Id><IBAN>FR7630006000011234567890191</IBAN></Id></CdtrAcct>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


def generate_mt103_multi() -> str:
    """Generate 3 MT103 SWIFT messages concatenated."""
    template = '''{1:F01BANKUS33AXXX0000000001}{2:O1030815250105BANKGB2LXXXX00000000012501051615N}{3:{108:REF%d}{121:%s}}{4:
:20:TXN%d-REF-123456
:23B:CRED
:32A:250105USD%d0000,00
:50K:/12345678901234
ORDERING CUSTOMER %d
123 MAIN STREET
NEW YORK NY 10001
:52A:ORDGUS33XXX
:57A:BNFCGB2LXXX
:59:/GB33BANK60161331926819
BENEFICIARY %d
456 HIGH STREET
LONDON EC1A 1BB
:70:INVOICE %d PAYMENT
:71A:SHA
-}'''
    messages = []
    for i in range(1, 4):
        uetr = f"{uuid.uuid4()}"
        messages.append(template % (i, uetr, i, i, i, i, i))
    return '\n'.join(messages)


def generate_mt202_multi() -> str:
    """Generate 3 MT202 SWIFT messages concatenated."""
    template = '''{1:F01BANKUS33AXXX0000000001}{2:O2020815250105BANKGB2LXXXX00000000012501051615N}{4:
:20:202TXN%d-REF-12
:21:RELATED-REF%d
:32A:250105USD%d00000,00
:52A:ORDGUS33XXX
:53A:SNDRUSCORR
:57A:RCVRGB2LXXX
:58A:/GB33BANK60161331926819
ACCOUNT WITH INST %d
:72:/INS/Additional Info %d
-}'''
    messages = []
    for i in range(1, 4):
        messages.append(template % (i, i, i, i, i))
    return '\n'.join(messages)


def generate_mt940_multi() -> str:
    """Generate MT940 with 3 statement entries."""
    return '''{1:F01BANKUS33AXXX0000000001}{2:O9400815250105BANKGB2LXXXX00000000012501051615N}{4:
:20:940STMT-123456
:25:12345678901234
:28C:1/1
:60F:C250104USD100000,00
:61:250105C10000,00NTRFREF1//ACCTSVCRREF1
:86:CREDIT ENTRY 1 - SALARY PAYMENT
:61:250105D5000,00NTRFREF2//ACCTSVCRREF2
:86:DEBIT ENTRY 2 - UTILITY PAYMENT
:61:250105C7500,00NTRFREF3//ACCTSVCRREF3
:86:CREDIT ENTRY 3 - TRANSFER RECEIVED
:62F:C250105USD112500,00
-}'''


def generate_camt053_multi() -> str:
    """Generate camt.053 XML with 3 statement entries."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.08">
  <BkToCstmrStmt>
    <GrpHdr>
      <MsgId>CAMT053-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-05T12:00:00</CreDtTm>
    </GrpHdr>
    <Stmt>
      <Id>STMT-001</Id>
      <CreDtTm>2025-01-05T12:00:00</CreDtTm>
      <Acct><Id><IBAN>DE89370400440532013000</IBAN></Id></Acct>
      <Bal>
        <Tp><CdOrPrtry><Cd>OPBD</Cd></CdOrPrtry></Tp>
        <Amt Ccy="EUR">50000.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Dt><Dt>2025-01-04</Dt></Dt>
      </Bal>
      <Ntry>
        <Amt Ccy="EUR">1000.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Sts><Cd>BOOK</Cd></Sts>
        <BookgDt><Dt>2025-01-05</Dt></BookgDt>
        <ValDt><Dt>2025-01-05</Dt></ValDt>
        <AcctSvcrRef>ENTRY-001</AcctSvcrRef>
        <NtryDtls><TxDtls><Refs><EndToEndId>E2E-CAMT-001</EndToEndId></Refs></TxDtls></NtryDtls>
      </Ntry>
      <Ntry>
        <Amt Ccy="EUR">2500.00</Amt>
        <CdtDbtInd>DBIT</CdtDbtInd>
        <Sts><Cd>BOOK</Cd></Sts>
        <BookgDt><Dt>2025-01-05</Dt></BookgDt>
        <ValDt><Dt>2025-01-05</Dt></ValDt>
        <AcctSvcrRef>ENTRY-002</AcctSvcrRef>
      </Ntry>
      <Ntry>
        <Amt Ccy="EUR">5000.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Sts><Cd>BOOK</Cd></Sts>
        <BookgDt><Dt>2025-01-05</Dt></BookgDt>
        <ValDt><Dt>2025-01-05</Dt></ValDt>
        <AcctSvcrRef>ENTRY-003</AcctSvcrRef>
      </Ntry>
    </Stmt>
  </BkToCstmrStmt>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


def generate_ach_multi() -> str:
    """Generate ACH/NACHA file with 3 entry detail records."""
    # File header (94 chars)
    file_header = '101 091000019 1234567892501051234A094101FIRST NATIONAL BANK    ACME CORPORATION       TESTREF1'
    # Batch header (94 chars)
    batch_header = '5200ACME CORP       PAYROLL MULTI       1234567890PPDPAYROLL   250103250105   1091000010000001'
    # Entry details (94 chars each) - 3 entries
    entry1 = '62209100001923456789012345   0000100000EMPID00001     JOHN DOE EMPLOYEE 1     0091000010000001'
    entry2 = '62209100001987654321098765   0000150000EMPID00002     JANE SMITH EMPLOYEE 2   0091000010000002'
    entry3 = '62209100001911223344556677   0000200000EMPID00003     BOB JONES EMPLOYEE 3    0091000010000003'
    # Batch control (94 chars)
    batch_control = '820000000300273000030000000000000000004500001234567890                         091000010000001'
    # File control (94 chars)
    file_control = '9000001000001000000030027300003000000000000000000450000                                       '

    return '\n'.join([file_header, batch_header, entry1, entry2, entry3, batch_control, file_control])


def generate_fedwire_multi() -> str:
    """Generate FEDWIRE file with 3 messages separated by ###."""
    template = '''{{1500}}00
{{1510}}1000
{{1520}}{amount}
{{2000}}FEDWIRE-TXN-{idx}
{{3100}}021000089SENDER BANK {idx}
{{3400}}021000021RECEIVER BANK {idx}
{{4000}}ORIGINATOR {idx}
{{4100}}123456789{idx}
{{4200}}BENEFICIARY {idx}
{{4320}}987654321{idx}
{{6000}}PAYMENT FOR INVOICE {idx}'''

    messages = []
    for i in range(1, 4):
        messages.append(template.format(idx=i, amount=i * 50000))
    return '\n###\n'.join(messages)


def generate_sepa_multi() -> str:
    """Generate SEPA XML with 3 transactions."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>SEPA-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-05T13:00:00</CreDtTm>
      <NbOfTxs>3</NbOfTxs>
      <CtrlSum>4500.00</CtrlSum>
      <InitgPty><Nm>SEPA Initiator</Nm></InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>SEPA-PMT-001</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <BtchBookg>true</BtchBookg>
      <PmtTpInf><SvcLvl><Cd>SEPA</Cd></SvcLvl></PmtTpInf>
      <ReqdExctnDt>2025-01-06</ReqdExctnDt>
      <Dbtr><Nm>German Debtor GmbH</Nm><PstlAdr><Ctry>DE</Ctry></PstlAdr></Dbtr>
      <DbtrAcct><Id><IBAN>DE89370400440532013000</IBAN></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BIC>DEUTDEFFXXX</BIC></FinInstnId></DbtrAgt>
      <ChrgBr>SLEV</ChrgBr>
      <CdtTrfTxInf>
        <PmtId><EndToEndId>SEPA-E2E-001</EndToEndId></PmtId>
        <Amt><InstdAmt Ccy="EUR">1500.00</InstdAmt></Amt>
        <CdtrAgt><FinInstnId><BIC>ABORFRPPXXX</BIC></FinInstnId></CdtrAgt>
        <Cdtr><Nm>French Supplier 1</Nm></Cdtr>
        <CdtrAcct><Id><IBAN>FR7630006000011234567890189</IBAN></Id></CdtrAcct>
        <RmtInf><Ustrd>SEPA Payment 1</Ustrd></RmtInf>
      </CdtTrfTxInf>
      <CdtTrfTxInf>
        <PmtId><EndToEndId>SEPA-E2E-002</EndToEndId></PmtId>
        <Amt><InstdAmt Ccy="EUR">2000.00</InstdAmt></Amt>
        <CdtrAgt><FinInstnId><BIC>INGBNL2AXXX</BIC></FinInstnId></CdtrAgt>
        <Cdtr><Nm>Dutch Supplier 2</Nm></Cdtr>
        <CdtrAcct><Id><IBAN>NL91ABNA0417164300</IBAN></Id></CdtrAcct>
        <RmtInf><Ustrd>SEPA Payment 2</Ustrd></RmtInf>
      </CdtTrfTxInf>
      <CdtTrfTxInf>
        <PmtId><EndToEndId>SEPA-E2E-003</EndToEndId></PmtId>
        <Amt><InstdAmt Ccy="EUR">1000.00</InstdAmt></Amt>
        <CdtrAgt><FinInstnId><BIC>BABORBE2XXX</BIC></FinInstnId></CdtrAgt>
        <Cdtr><Nm>Belgian Supplier 3</Nm></Cdtr>
        <CdtrAcct><Id><IBAN>BE68539007547034</IBAN></Id></CdtrAcct>
        <RmtInf><Ustrd>SEPA Payment 3</Ustrd></RmtInf>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


def generate_rtp_multi() -> str:
    """Generate RTP XML with 3 transactions."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>RTP-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-05T14:00:00</CreDtTm>
      <NbOfTxs>3</NbOfTxs>
      <SttlmInf><SttlmMtd>CLRG</SttlmMtd><ClrSys><Cd>RTP</Cd></ClrSys></SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>RTP-001</InstrId><EndToEndId>RTP-E2E-001</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="USD">500.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2025-01-05</IntrBkSttlmDt>
      <Dbtr><Nm>RTP Payer 1</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>123456789</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>021000089</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>021000021</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>RTP Payee 1</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>987654321</Id></Othr></Id></CdtrAcct>
      <RmtInf><Ustrd>RTP Payment 1</Ustrd></RmtInf>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>RTP-002</InstrId><EndToEndId>RTP-E2E-002</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="USD">750.00</IntrBkSttlmAmt>
      <Dbtr><Nm>RTP Payer 2</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>111222333</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>021000089</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>021000021</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>RTP Payee 2</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>444555666</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>RTP-003</InstrId><EndToEndId>RTP-E2E-003</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="USD">1000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>RTP Payer 3</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>777888999</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>021000089</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>021000021</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>RTP Payee 3</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>000111222</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


def generate_chaps_multi() -> str:
    """Generate CHAPS XML with 3 transactions."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>CHAPS-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-05T15:00:00</CreDtTm>
      <NbOfTxs>3</NbOfTxs>
      <SttlmInf><SttlmMtd>CLRG</SttlmMtd><ClrSys><Cd>CHAPS</Cd></ClrSys></SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>CHAPS-001</InstrId><EndToEndId>CHAPS-E2E-001</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="GBP">25000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2025-01-05</IntrBkSttlmDt>
      <Dbtr><Nm>UK Corporate Payer 1</Nm><PstlAdr><Ctry>GB</Ctry></PstlAdr></Dbtr>
      <DbtrAcct><Id><Othr><Id>12345678</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>123456</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>654321</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>UK Supplier 1</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>87654321</Id></Othr></Id></CdtrAcct>
      <RmtInf><Ustrd>CHAPS Payment 1</Ustrd></RmtInf>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>CHAPS-002</InstrId><EndToEndId>CHAPS-E2E-002</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="GBP">50000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>UK Corporate Payer 2</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>11112222</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>123456</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>654321</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>UK Supplier 2</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>33334444</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>CHAPS-003</InstrId><EndToEndId>CHAPS-E2E-003</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="GBP">100000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>UK Corporate Payer 3</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>55556666</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>123456</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>654321</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>UK Supplier 3</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>77778888</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


def generate_fps_multi() -> str:
    """Generate FPS XML with 3 transactions."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>FPS-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-05T16:00:00</CreDtTm>
      <NbOfTxs>3</NbOfTxs>
      <SttlmInf><SttlmMtd>CLRG</SttlmMtd><ClrSys><Cd>FPS</Cd></ClrSys></SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>FPS-001</InstrId><EndToEndId>FPS-E2E-001</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="GBP">250.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2025-01-05</IntrBkSttlmDt>
      <Dbtr><Nm>FPS Payer 1</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>12345678</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>123456</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>654321</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>FPS Payee 1</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>87654321</Id></Othr></Id></CdtrAcct>
      <RmtInf><Ustrd>FPS Payment 1</Ustrd></RmtInf>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>FPS-002</InstrId><EndToEndId>FPS-E2E-002</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="GBP">500.00</IntrBkSttlmAmt>
      <Dbtr><Nm>FPS Payer 2</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>11112222</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>123456</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>654321</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>FPS Payee 2</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>33334444</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>FPS-003</InstrId><EndToEndId>FPS-E2E-003</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="GBP">750.00</IntrBkSttlmAmt>
      <Dbtr><Nm>FPS Payer 3</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>55556666</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>123456</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>654321</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>FPS Payee 3</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>77778888</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


def generate_bacs_multi() -> str:
    """Generate BACS file with 3 payment records."""
    # BACS uses Standard 18 format - 100 char records
    lines = []
    # UHL1 header: VOL1 + Processing date (YYMMDD) + SU Number + SU Name
    lines.append('UHL1 250105123456TEST SERVICE USER     ')
    # Payment records (type 01 = direct debit, 17 = direct credit)
    # Format: TTDSC6SCCCCSACCOUNT#AMOUNT0000REFCCC#####PAYEENAME....
    lines.append('01301234560161012345678000000100000001234PAYMENT 1                                   ')
    lines.append('01301234560161087654321000000200000001235PAYMENT 2                                   ')
    lines.append('01301234560161055556666000000300000001236PAYMENT 3                                   ')
    # UTL1 trailer
    lines.append('UTL10000030000000600000000000000000000000                                            ')
    return '\n'.join(lines)


def generate_chips_multi() -> str:
    """Generate CHIPS file with 3 messages."""
    template = '''{{MSG}}
{{1500}}00
{{2000}}CHIPS-{idx}-REF
{{3100}}0002SENDER BANK {idx}
{{3400}}0003RECEIVER BANK {idx}
{{4000}}ORIGINATOR {idx}
{{4100}}12345678{idx}
{{4200}}BENEFICIARY {idx}
{{4320}}8765432{idx}
{{5000}}{amount}
{{6000}}CHIPS PAYMENT {idx}'''

    messages = []
    for i in range(1, 4):
        messages.append(template.format(idx=i, amount=i * 100000))
    return '\n\n'.join(messages)


def generate_fednow_multi() -> str:
    """Generate FedNow XML with 3 transactions (pacs.008 variant)."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>FEDNOW-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-05T17:00:00</CreDtTm>
      <NbOfTxs>3</NbOfTxs>
      <SttlmInf><SttlmMtd>CLRG</SttlmMtd><ClrSys><Cd>FEDNOW</Cd></ClrSys></SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>FEDNOW-001</InstrId><EndToEndId>FEDNOW-E2E-001</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="USD">100.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2025-01-05</IntrBkSttlmDt>
      <Dbtr><Nm>FedNow Payer 1</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>123456789</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>021000089</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>021000021</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>FedNow Payee 1</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>987654321</Id></Othr></Id></CdtrAcct>
      <RmtInf><Ustrd>FedNow Payment 1</Ustrd></RmtInf>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>FEDNOW-002</InstrId><EndToEndId>FEDNOW-E2E-002</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="USD">200.00</IntrBkSttlmAmt>
      <Dbtr><Nm>FedNow Payer 2</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>111222333</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>021000089</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>021000021</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>FedNow Payee 2</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>444555666</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>FEDNOW-003</InstrId><EndToEndId>FEDNOW-E2E-003</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="USD">300.00</IntrBkSttlmAmt>
      <Dbtr><Nm>FedNow Payer 3</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>777888999</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>021000089</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>021000021</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>FedNow Payee 3</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>000111222</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


def generate_target2_multi() -> str:
    """Generate TARGET2 XML with 3 transactions."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.009.001.08">
  <FICdtTrf>
    <GrpHdr>
      <MsgId>TARGET2-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-05T18:00:00</CreDtTm>
      <NbOfTxs>3</NbOfTxs>
      <SttlmInf><SttlmMtd>CLRG</SttlmMtd><ClrSys><Cd>TGT</Cd></ClrSys></SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>T2-001</InstrId><EndToEndId>T2-E2E-001</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="EUR">1000000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2025-01-05</IntrBkSttlmDt>
      <InstgAgt><FinInstnId><BICFI>DEUTDEFFXXX</BICFI></FinInstnId></InstgAgt>
      <InstdAgt><FinInstnId><BICFI>ABORFRPPXXX</BICFI></FinInstnId></InstdAgt>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>T2-002</InstrId><EndToEndId>T2-E2E-002</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="EUR">2000000.00</IntrBkSttlmAmt>
      <InstgAgt><FinInstnId><BICFI>DEUTDEFFXXX</BICFI></FinInstnId></InstgAgt>
      <InstdAgt><FinInstnId><BICFI>INGBNL2AXXX</BICFI></FinInstnId></InstdAgt>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>T2-003</InstrId><EndToEndId>T2-E2E-003</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="EUR">3000000.00</IntrBkSttlmAmt>
      <InstgAgt><FinInstnId><BICFI>DEUTDEFFXXX</BICFI></FinInstnId></InstgAgt>
      <InstdAgt><FinInstnId><BICFI>BABORBE2XXX</BICFI></FinInstnId></InstdAgt>
    </CdtTrfTxInf>
  </FICdtTrf>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


def generate_npp_multi() -> str:
    """Generate NPP (Australia) XML with 3 transactions."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>NPP-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-05T19:00:00</CreDtTm>
      <NbOfTxs>3</NbOfTxs>
      <SttlmInf><SttlmMtd>CLRG</SttlmMtd><ClrSys><Cd>NPP</Cd></ClrSys></SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>NPP-001</InstrId><EndToEndId>NPP-E2E-001</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="AUD">100.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2025-01-05</IntrBkSttlmDt>
      <Dbtr><Nm>Aussie Payer 1</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>123456789</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>062000</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>063000</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>Aussie Payee 1</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>987654321</Id></Othr></Id></CdtrAcct>
      <RmtInf><Ustrd>NPP Payment 1</Ustrd></RmtInf>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>NPP-002</InstrId><EndToEndId>NPP-E2E-002</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="AUD">200.00</IntrBkSttlmAmt>
      <Dbtr><Nm>Aussie Payer 2</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>111222333</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>062000</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>063000</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>Aussie Payee 2</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>444555666</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>NPP-003</InstrId><EndToEndId>NPP-E2E-003</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="AUD">300.00</IntrBkSttlmAmt>
      <Dbtr><Nm>Aussie Payer 3</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>777888999</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>062000</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>063000</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>Aussie Payee 3</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>000111222</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


def generate_pix_multi() -> str:
    """Generate PIX (Brazil) JSON with 3 transactions."""
    return json.dumps({
        "messageId": f"PIX-MULTI-{uuid.uuid4().hex[:8]}",
        "creationDateTime": "2025-01-05T20:00:00",
        "transactions": [
            {
                "transactionId": "PIX-001",
                "endToEndId": "PIX-E2E-001",
                "amount": 100.00,
                "currency": "BRL",
                "payerName": "PIX Payer 1",
                "payerCpfCnpj": "12345678901",
                "payerAccount": "12345-6",
                "payerBankCode": "001",
                "payeeName": "PIX Payee 1",
                "payeeCpfCnpj": "98765432109",
                "payeeAccount": "98765-4",
                "payeeBankCode": "237",
                "description": "PIX Payment 1"
            },
            {
                "transactionId": "PIX-002",
                "endToEndId": "PIX-E2E-002",
                "amount": 200.00,
                "currency": "BRL",
                "payerName": "PIX Payer 2",
                "payerCpfCnpj": "11111111111",
                "payerAccount": "11111-1",
                "payerBankCode": "001",
                "payeeName": "PIX Payee 2",
                "payeeCpfCnpj": "22222222222",
                "payeeAccount": "22222-2",
                "payeeBankCode": "237",
                "description": "PIX Payment 2"
            },
            {
                "transactionId": "PIX-003",
                "endToEndId": "PIX-E2E-003",
                "amount": 300.00,
                "currency": "BRL",
                "payerName": "PIX Payer 3",
                "payerCpfCnpj": "33333333333",
                "payerAccount": "33333-3",
                "payerBankCode": "001",
                "payeeName": "PIX Payee 3",
                "payeeCpfCnpj": "44444444444",
                "payeeAccount": "44444-4",
                "payeeBankCode": "237",
                "description": "PIX Payment 3"
            }
        ]
    }, indent=2)


def generate_upi_multi() -> str:
    """Generate UPI (India) JSON with 3 transactions."""
    return json.dumps({
        "messageId": f"UPI-MULTI-{uuid.uuid4().hex[:8]}",
        "creationDateTime": "2025-01-05T21:00:00",
        "transactions": [
            {
                "transactionId": "UPI-001",
                "upiReference": "UPI-REF-001",
                "amount": 1000.00,
                "currency": "INR",
                "payerVpa": "payer1@upi",
                "payerName": "UPI Payer 1",
                "payerAccount": "123456789012",
                "payerIfsc": "SBIN0001234",
                "payeeVpa": "payee1@upi",
                "payeeName": "UPI Payee 1",
                "payeeAccount": "987654321098",
                "payeeIfsc": "HDFC0001234",
                "note": "UPI Payment 1"
            },
            {
                "transactionId": "UPI-002",
                "upiReference": "UPI-REF-002",
                "amount": 2000.00,
                "currency": "INR",
                "payerVpa": "payer2@upi",
                "payerName": "UPI Payer 2",
                "payerAccount": "111222333444",
                "payerIfsc": "SBIN0005678",
                "payeeVpa": "payee2@upi",
                "payeeName": "UPI Payee 2",
                "payeeAccount": "555666777888",
                "payeeIfsc": "HDFC0005678",
                "note": "UPI Payment 2"
            },
            {
                "transactionId": "UPI-003",
                "upiReference": "UPI-REF-003",
                "amount": 3000.00,
                "currency": "INR",
                "payerVpa": "payer3@upi",
                "payerName": "UPI Payer 3",
                "payerAccount": "999888777666",
                "payerIfsc": "SBIN0009012",
                "payeeVpa": "payee3@upi",
                "payeeName": "UPI Payee 3",
                "payeeAccount": "333222111000",
                "payeeIfsc": "HDFC0009012",
                "note": "UPI Payment 3"
            }
        ]
    }, indent=2)


def generate_cnaps_multi() -> str:
    """Generate CNAPS (China) fixed-width with 3 records."""
    lines = []
    lines.append('HDR2025010512345678CNAPS SENDER BANK                               ')
    for i in range(1, 4):
        # Transaction record format
        txn = f'TXN{i:03d}10230456789{i:010d}00000{i}0000002025010512345678901234PAYER {i}              87654321{i:04d}PAYEE {i}              PAYMENT {i}     '
        lines.append(txn.ljust(200))
    lines.append('TRL000300000060000                                                ')
    return '\n'.join(lines)


def generate_bojnet_multi() -> str:
    """Generate BOJ-NET (Japan) fixed-width with 3 records."""
    lines = []
    lines.append('HD20250105123456BOJNET SENDER                                     ')
    for i in range(1, 4):
        txn = f'TX{i:04d}12345678901234{i}0000000{i}000000JPY20250105PAYER{i}              87654321{i:04d}00PAYEE{i}              PAYMENT{i}     '
        lines.append(txn.ljust(200))
    lines.append('TR0003000000060000000                                            ')
    return '\n'.join(lines)


def generate_kftc_multi() -> str:
    """Generate KFTC (Korea) fixed-width with 3 records."""
    lines = []
    lines.append('0120250105123456KFTC SENDER BANK                                  ')
    for i in range(1, 4):
        txn = f'02{i:06d}110123456789{i:010d}00000{i}000000KRW20250105PAYER {i}           8765432{i:05d}00PAYEE {i}           PAYMENT {i}      '
        lines.append(txn.ljust(250))
    lines.append('9900030000006000000                                               ')
    return '\n'.join(lines)


def generate_meps_plus_multi() -> str:
    """Generate MEPS+ (Singapore) XML with 3 transactions."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>MEPS-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-05T22:00:00</CreDtTm>
      <NbOfTxs>3</NbOfTxs>
      <SttlmInf><SttlmMtd>CLRG</SttlmMtd><ClrSys><Cd>MEPS</Cd></ClrSys></SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>MEPS-001</InstrId><EndToEndId>MEPS-E2E-001</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="SGD">10000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2025-01-05</IntrBkSttlmDt>
      <Dbtr><Nm>Singapore Payer 1</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>123456789</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>7171</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>7339</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>Singapore Payee 1</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>987654321</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>MEPS-002</InstrId><EndToEndId>MEPS-E2E-002</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="SGD">20000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>Singapore Payer 2</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>111222333</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>7171</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>7339</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>Singapore Payee 2</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>444555666</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>MEPS-003</InstrId><EndToEndId>MEPS-E2E-003</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="SGD">30000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>Singapore Payer 3</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>777888999</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>7171</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>7339</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>Singapore Payee 3</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>000111222</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


def generate_rtgs_hk_multi() -> str:
    """Generate RTGS_HK (Hong Kong) XML with 3 transactions."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>RTGSHK-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-05T23:00:00</CreDtTm>
      <NbOfTxs>3</NbOfTxs>
      <SttlmInf><SttlmMtd>CLRG</SttlmMtd><ClrSys><Cd>CHATS</Cd></ClrSys></SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>RTGSHK-001</InstrId><EndToEndId>RTGSHK-E2E-001</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="HKD">100000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2025-01-05</IntrBkSttlmDt>
      <Dbtr><Nm>HK Payer 1</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>123456789</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BICFI>HABORHKHXXX</BICFI></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><BICFI>BABORHKHXXX</BICFI></FinInstnId></CdtrAgt>
      <Cdtr><Nm>HK Payee 1</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>987654321</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>RTGSHK-002</InstrId><EndToEndId>RTGSHK-E2E-002</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="HKD">200000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>HK Payer 2</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>111222333</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BICFI>HABORHKHXXX</BICFI></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><BICFI>BABORHKHXXX</BICFI></FinInstnId></CdtrAgt>
      <Cdtr><Nm>HK Payee 2</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>444555666</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>RTGSHK-003</InstrId><EndToEndId>RTGSHK-E2E-003</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="HKD">300000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>HK Payer 3</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>777888999</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BICFI>HABORHKHXXX</BICFI></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><BICFI>BABORHKHXXX</BICFI></FinInstnId></CdtrAgt>
      <Cdtr><Nm>HK Payee 3</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>000111222</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


def generate_sarie_multi() -> str:
    """Generate SARIE (Saudi Arabia) tag-value with 3 messages."""
    template = '''{{1100}}SARIE-{idx}
{{1500}}00
{{2000}}SARIE-TXN-{idx}
{{3100}}RIABORIYXXX
{{3400}}SABBSARIXXX
{{4000}}SAUDI PAYER {idx}
{{4100}}SA12345678901234567890{idx}
{{4200}}SAUDI PAYEE {idx}
{{4320}}SA98765432109876543210{idx}
{{5000}}{amount}
{{5010}}SAR
{{6000}}SARIE PAYMENT {idx}'''

    messages = []
    for i in range(1, 4):
        messages.append(template.format(idx=i, amount=i * 10000))
    return '\n###\n'.join(messages)


def generate_uaefts_multi() -> str:
    """Generate UAEFTS (UAE) XML with 3 transactions."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>UAEFTS-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-06T00:00:00</CreDtTm>
      <NbOfTxs>3</NbOfTxs>
      <SttlmInf><SttlmMtd>CLRG</SttlmMtd><ClrSys><Cd>UAEFTS</Cd></ClrSys></SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>UAEFTS-001</InstrId><EndToEndId>UAEFTS-E2E-001</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="AED">50000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2025-01-06</IntrBkSttlmDt>
      <Dbtr><Nm>UAE Payer 1</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>AE123456789012345</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BICFI>ADABORAEAXXX</BICFI></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><BICFI>MASHQAQAXXX</BICFI></FinInstnId></CdtrAgt>
      <Cdtr><Nm>UAE Payee 1</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>AE987654321098765</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>UAEFTS-002</InstrId><EndToEndId>UAEFTS-E2E-002</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="AED">100000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>UAE Payer 2</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>AE111222333444555</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BICFI>ADABORAEAXXX</BICFI></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><BICFI>MASHQAQAXXX</BICFI></FinInstnId></CdtrAgt>
      <Cdtr><Nm>UAE Payee 2</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>AE666777888999000</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>UAEFTS-003</InstrId><EndToEndId>UAEFTS-E2E-003</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="AED">150000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>UAE Payer 3</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>AE555444333222111</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BICFI>ADABORAEAXXX</BICFI></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><BICFI>MASHQAQAXXX</BICFI></FinInstnId></CdtrAgt>
      <Cdtr><Nm>UAE Payee 3</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>AE000999888777666</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


def generate_promptpay_multi() -> str:
    """Generate PromptPay (Thailand) XML with 3 transactions."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>PROMPTPAY-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-06T01:00:00</CreDtTm>
      <NbOfTxs>3</NbOfTxs>
      <SttlmInf><SttlmMtd>CLRG</SttlmMtd><ClrSys><Cd>PPAY</Cd></ClrSys></SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>PPAY-001</InstrId><EndToEndId>PPAY-E2E-001</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="THB">1000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2025-01-06</IntrBkSttlmDt>
      <Dbtr><Nm>Thai Payer 1</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>1234567890</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>002</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>004</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>Thai Payee 1</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>0987654321</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>PPAY-002</InstrId><EndToEndId>PPAY-E2E-002</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="THB">2000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>Thai Payer 2</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>1112223334</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>002</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>004</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>Thai Payee 2</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>4445556667</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>PPAY-003</InstrId><EndToEndId>PPAY-E2E-003</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="THB">3000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>Thai Payer 3</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>7778889990</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>002</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>004</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>Thai Payee 3</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>0001112223</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


def generate_paynow_multi() -> str:
    """Generate PayNow (Singapore) XML with 3 transactions."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>PAYNOW-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-06T02:00:00</CreDtTm>
      <NbOfTxs>3</NbOfTxs>
      <SttlmInf><SttlmMtd>CLRG</SttlmMtd><ClrSys><Cd>FAST</Cd></ClrSys></SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>PNOW-001</InstrId><EndToEndId>PNOW-E2E-001</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="SGD">500.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2025-01-06</IntrBkSttlmDt>
      <Dbtr><Nm>SG Payer 1</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>123456789</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>7171</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>7339</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>SG Payee 1</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>987654321</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>PNOW-002</InstrId><EndToEndId>PNOW-E2E-002</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="SGD">1000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>SG Payer 2</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>111222333</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>7171</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>7339</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>SG Payee 2</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>444555666</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>PNOW-003</InstrId><EndToEndId>PNOW-E2E-003</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="SGD">1500.00</IntrBkSttlmAmt>
      <Dbtr><Nm>SG Payer 3</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>777888999</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>7171</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>7339</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>SG Payee 3</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>000111222</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


def generate_instapay_multi() -> str:
    """Generate InstaPay (Philippines) XML with 3 transactions."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>INSTAPAY-MULTI-{batch_id}</MsgId>
      <CreDtTm>2025-01-06T03:00:00</CreDtTm>
      <NbOfTxs>3</NbOfTxs>
      <SttlmInf><SttlmMtd>CLRG</SttlmMtd><ClrSys><Cd>INSTAPAY</Cd></ClrSys></SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId><InstrId>IPAY-001</InstrId><EndToEndId>IPAY-E2E-001</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="PHP">5000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2025-01-06</IntrBkSttlmDt>
      <Dbtr><Nm>PH Payer 1</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>123456789012</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>010530667</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>010160018</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>PH Payee 1</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>987654321098</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>IPAY-002</InstrId><EndToEndId>IPAY-E2E-002</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="PHP">10000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>PH Payer 2</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>111222333444</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>010530667</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>010160018</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>PH Payee 2</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>555666777888</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
    <CdtTrfTxInf>
      <PmtId><InstrId>IPAY-003</InstrId><EndToEndId>IPAY-E2E-003</EndToEndId></PmtId>
      <IntrBkSttlmAmt Ccy="PHP">15000.00</IntrBkSttlmAmt>
      <Dbtr><Nm>PH Payer 3</Nm></Dbtr>
      <DbtrAcct><Id><Othr><Id>999888777666</Id></Othr></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><ClrSysMmbId><MmbId>010530667</MmbId></ClrSysMmbId></FinInstnId></DbtrAgt>
      <CdtrAgt><FinInstnId><ClrSysMmbId><MmbId>010160018</MmbId></ClrSysMmbId></FinInstnId></CdtrAgt>
      <Cdtr><Nm>PH Payee 3</Nm></Cdtr>
      <CdtrAcct><Id><Othr><Id>333222111000</Id></Othr></Id></CdtrAcct>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>'''.format(batch_id=uuid.uuid4().hex[:8])


# =============================================================================
# TEST FILE GENERATORS MAPPING
# =============================================================================

TEST_GENERATORS = {
    'pain.001': ('xml', generate_pain001_multi, 3),
    'pacs.008': ('xml', generate_pacs008_multi, 3),
    'MT103': ('txt', generate_mt103_multi, 3),
    'MT202': ('txt', generate_mt202_multi, 3),
    'MT940': ('txt', generate_mt940_multi, 3),  # Statement with 3 entries
    'camt.053': ('xml', generate_camt053_multi, 3),
    'ACH': ('ach', generate_ach_multi, 3),
    'FEDWIRE': ('txt', generate_fedwire_multi, 3),
    'SEPA': ('xml', generate_sepa_multi, 3),
    'RTP': ('xml', generate_rtp_multi, 3),
    'CHAPS': ('xml', generate_chaps_multi, 3),
    'FPS': ('xml', generate_fps_multi, 3),
    'BACS': ('txt', generate_bacs_multi, 3),
    'CHIPS': ('txt', generate_chips_multi, 3),
    'FEDNOW': ('xml', generate_fednow_multi, 3),
    'TARGET2': ('xml', generate_target2_multi, 3),
    'NPP': ('xml', generate_npp_multi, 3),
    'PIX': ('json', generate_pix_multi, 3),
    'UPI': ('json', generate_upi_multi, 3),
    'CNAPS': ('txt', generate_cnaps_multi, 3),
    'BOJNET': ('txt', generate_bojnet_multi, 3),
    'KFTC': ('txt', generate_kftc_multi, 3),
    'MEPS_PLUS': ('xml', generate_meps_plus_multi, 3),
    'RTGS_HK': ('xml', generate_rtgs_hk_multi, 3),
    'SARIE': ('txt', generate_sarie_multi, 3),
    'UAEFTS': ('xml', generate_uaefts_multi, 3),
    'PROMPTPAY': ('xml', generate_promptpay_multi, 3),
    'PAYNOW': ('xml', generate_paynow_multi, 3),
    'INSTAPAY': ('xml', generate_instapay_multi, 3),
}


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def get_db_connection():
    """Get PostgreSQL connection."""
    return psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=int(os.environ.get('POSTGRES_PORT', 5433)),
        database=os.environ.get('POSTGRES_DB', 'gps_cdm'),
        user=os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
        password=os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password')
    )


def copy_file_to_nifi(local_path: str, nifi_path: str) -> bool:
    """Copy file to NiFi input directory using tar method."""
    try:
        # Use tar to copy with correct permissions
        cmd = f'cd {os.path.dirname(local_path)} && tar cf - {os.path.basename(local_path)} | docker exec -i gps-cdm-nifi tar xf - -C /opt/nifi/nifi-current/input/'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  Warning: tar copy returned {result.returncode}")

        # Clean up macOS metadata files
        subprocess.run(
            'docker exec gps-cdm-nifi bash -c "rm -f /opt/nifi/nifi-current/input/._*" 2>/dev/null',
            shell=True, capture_output=True
        )
        return True
    except Exception as e:
        print(f"  Error copying file: {e}")
        return False


def run_e2e_test(message_type: str, extension: str, generator, expected_records: int) -> Dict[str, Any]:
    """Run E2E test for a single message format."""
    result = {
        'message_type': message_type,
        'expected_records': expected_records,
        'bronze_count': 0,
        'silver_count': 0,
        'gold_count': 0,
        'status': 'PENDING',
        'errors': [],
    }

    batch_id = f"e2e_test_{uuid.uuid4().hex[:8]}"
    filename = f"{message_type}_MULTI_{batch_id}.{extension}"
    local_path = f"/tmp/nifi_input_test/{filename}"

    try:
        # Generate test file
        os.makedirs('/tmp/nifi_input_test', exist_ok=True)
        content = generator()
        with open(local_path, 'w') as f:
            f.write(content)

        # Copy to NiFi
        if not copy_file_to_nifi(local_path, filename):
            result['status'] = 'FAILED'
            result['errors'].append('Failed to copy file to NiFi')
            return result

        # Wait for processing (NiFi polls every 30 seconds, plus processing time)
        time.sleep(45)

        # Check results in database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check Bronze
        cursor.execute("""
            SELECT COUNT(*) FROM bronze.raw_payment_messages
            WHERE message_type = %s AND _batch_id LIKE %s
        """, (message_type, f'%{batch_id}%'))
        result['bronze_count'] = cursor.fetchone()[0]

        # Check Silver - determine table name
        silver_table = f"stg_{message_type.lower().replace('.', '').replace('-', '_')}"
        try:
            cursor.execute(f"""
                SELECT COUNT(*) FROM silver.{silver_table}
                WHERE _batch_id LIKE %s
            """, (f'%{batch_id}%',))
            result['silver_count'] = cursor.fetchone()[0]
        except Exception as e:
            result['errors'].append(f'Silver query failed: {e}')

        # Check Gold
        cursor.execute("""
            SELECT COUNT(*) FROM gold.cdm_payment_instruction
            WHERE source_message_type = %s AND lineage_batch_id LIKE %s
        """, (message_type, f'%{batch_id}%'))
        result['gold_count'] = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        # Determine status
        if result['bronze_count'] >= expected_records and result['silver_count'] >= expected_records and result['gold_count'] >= expected_records:
            result['status'] = 'SUCCESS'
        elif result['bronze_count'] > 0:
            result['status'] = 'PARTIAL'
        else:
            result['status'] = 'FAILED'

    except Exception as e:
        result['status'] = 'ERROR'
        result['errors'].append(str(e))

    return result


def main():
    """Run E2E tests for all 29 message formats."""
    print("=" * 80)
    print("GPS CDM E2E Multi-Record Test Suite")
    print("=" * 80)
    print(f"Testing {len(TEST_GENERATORS)} message formats with multi-record files")
    print()

    results = []

    for message_type, (extension, generator, expected_records) in TEST_GENERATORS.items():
        print(f"Testing {message_type}...", end=" ", flush=True)
        result = run_e2e_test(message_type, extension, generator, expected_records)
        results.append(result)

        status_symbol = "✓" if result['status'] == 'SUCCESS' else ("⚠" if result['status'] == 'PARTIAL' else "✗")
        print(f"{status_symbol} Bronze={result['bronze_count']}/{expected_records}, "
              f"Silver={result['silver_count']}/{expected_records}, "
              f"Gold={result['gold_count']}/{expected_records}")

        if result['errors']:
            for error in result['errors']:
                print(f"    Error: {error}")

    # Print summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    partial_count = sum(1 for r in results if r['status'] == 'PARTIAL')
    failed_count = sum(1 for r in results if r['status'] in ('FAILED', 'ERROR'))

    print(f"Total formats tested: {len(results)}")
    print(f"  SUCCESS: {success_count}")
    print(f"  PARTIAL: {partial_count}")
    print(f"  FAILED:  {failed_count}")

    # List failures
    if failed_count > 0:
        print()
        print("Failed formats:")
        for r in results:
            if r['status'] in ('FAILED', 'ERROR'):
                print(f"  - {r['message_type']}: {r['errors']}")

    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
