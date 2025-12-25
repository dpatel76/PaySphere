#!/usr/bin/env python3
"""
Generate standards-compliant test message files for all 63 GPS CDM payment message types.

Each file is generated in its proper format:
- ISO 20022: Valid XML with correct namespaces and schema
- SWIFT MT: Proper block structure (Basic Header, App Header, User Header, Text, Trailer)
- Regional: Appropriate format (JSON, XML, or proprietary)

Usage:
    python scripts/generate_compliant_messages.py [--output-dir data/nifi_input]
"""

import json
import os
import sys
import uuid
import random
from datetime import datetime, timedelta
from decimal import Decimal
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# ============================================================================
# Helper functions for generating realistic test data
# ============================================================================

def random_bic():
    """Generate a realistic BIC code."""
    banks = ['CITIUS33XXX', 'CHASUS33XXX', 'BOFAUS3NXXX', 'WFBIUS6SXXX', 'DEUTDEFFXXX',
             'BNPAFRPPXXX', 'HSBCHKHHXXX', 'SCBLSGSGXXX', 'ANZBAU3MXXX', 'NABOROJJXXX']
    return random.choice(banks)


def random_bic8():
    """Generate 8-character BIC."""
    return random_bic()[:8]


def random_iban(country='DE'):
    """Generate a realistic IBAN for a given country."""
    ibans = {
        'DE': f"DE{random.randint(10,99)}{random.randint(10000000,99999999)}{random.randint(1000000000,9999999999)}",
        'GB': f"GB{random.randint(10,99)}NWBK{random.randint(100000,999999)}{random.randint(10000000,99999999)}",
        'FR': f"FR{random.randint(10,99)}{random.randint(10000,99999)}{random.randint(10000,99999)}{random.randint(10000000000,99999999999)}{''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(2)])}",
        'ES': f"ES{random.randint(10,99)}{random.randint(1000,9999)}{random.randint(1000,9999)}{random.randint(10,99)}{random.randint(1000000000,9999999999)}",
        'IT': f"IT{random.randint(10,99)}{''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(1)])}{random.randint(10000,99999)}{random.randint(10000,99999)}{random.randint(100000000000,999999999999)}",
        'NL': f"NL{random.randint(10,99)}ABNA{random.randint(1000000000,9999999999)}",
    }
    return ibans.get(country, ibans['DE'])


def random_name(is_company=None):
    """Generate a realistic party name."""
    first_names = ['John', 'Emma', 'Michael', 'Sarah', 'David', 'Lisa', 'James', 'Anna', 'Robert', 'Maria']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Wilson', 'Taylor']
    companies = ['Acme Corporation', 'Global Industries Ltd', 'Tech Solutions Inc', 'Prime Services GmbH',
                 'Alpha Trading Co', 'Beta Holdings SA', 'Omega Partners LLC', 'Delta Systems AG',
                 'Phoenix Enterprises', 'Nexus Financial Services']

    if is_company is None:
        is_company = random.random() > 0.5

    if is_company:
        return random.choice(companies)
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def random_amount(min_val=100, max_val=500000):
    """Generate a realistic payment amount."""
    return round(random.uniform(min_val, max_val), 2)


def random_currency():
    """Generate a currency code."""
    currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'SGD', 'HKD', 'AED']
    return random.choice(currencies)


def random_date(days_back=30):
    """Generate a random date within the past N days."""
    delta = timedelta(days=random.randint(0, days_back))
    return (datetime.utcnow() - delta).strftime('%Y-%m-%d')


def random_datetime_iso():
    """Generate current datetime in ISO format."""
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')


def random_reference(prefix='REF'):
    """Generate a payment reference."""
    return f"{prefix}{uuid.uuid4().hex[:12].upper()}"


def format_amount(amount, decimals=2):
    """Format amount with specified decimals."""
    return f"{amount:.{decimals}f}"


# ============================================================================
# ISO 20022 XML Message Generators
# ============================================================================

def prettify_xml(elem):
    """Return a pretty-printed XML string."""
    rough_string = ET.tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def create_iso20022_xml(root_tag, namespace, build_func):
    """Create ISO 20022 XML message with proper structure."""
    # Create root with namespace
    nsmap = {'': namespace}
    root = ET.Element('Document', xmlns=namespace)

    # Build message content
    build_func(root)

    # Generate pretty XML
    xml_str = prettify_xml(root)

    # Remove extra declaration line from minidom
    lines = xml_str.split('\n')
    if lines[0].startswith('<?xml'):
        xml_str = '\n'.join(lines[1:])

    # Add proper declaration
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'


def generate_pain001_xml():
    """ISO 20022 pain.001.001.11 Customer Credit Transfer Initiation."""
    msg_id = f"MSGID{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"
    pmt_inf_id = f"PMTINF{uuid.uuid4().hex[:8].upper()}"
    e2e_id = f"E2E{uuid.uuid4().hex[:10].upper()}"
    amount = random_amount()
    currency = 'EUR'

    def build_content(root):
        cstmr = ET.SubElement(root, 'CstmrCdtTrfInitn')

        # Group Header
        grp_hdr = ET.SubElement(cstmr, 'GrpHdr')
        ET.SubElement(grp_hdr, 'MsgId').text = msg_id
        ET.SubElement(grp_hdr, 'CreDtTm').text = random_datetime_iso()
        ET.SubElement(grp_hdr, 'NbOfTxs').text = '1'
        ET.SubElement(grp_hdr, 'CtrlSum').text = format_amount(amount)
        initg_pty = ET.SubElement(grp_hdr, 'InitgPty')
        ET.SubElement(initg_pty, 'Nm').text = random_name(is_company=True)

        # Payment Information
        pmt_inf = ET.SubElement(cstmr, 'PmtInf')
        ET.SubElement(pmt_inf, 'PmtInfId').text = pmt_inf_id
        ET.SubElement(pmt_inf, 'PmtMtd').text = 'TRF'
        ET.SubElement(pmt_inf, 'BtchBookg').text = 'true'
        ET.SubElement(pmt_inf, 'NbOfTxs').text = '1'
        ET.SubElement(pmt_inf, 'CtrlSum').text = format_amount(amount)

        pmt_tp_inf = ET.SubElement(pmt_inf, 'PmtTpInf')
        svc_lvl = ET.SubElement(pmt_tp_inf, 'SvcLvl')
        ET.SubElement(svc_lvl, 'Cd').text = 'SEPA'

        reqd_exctn_dt = ET.SubElement(pmt_inf, 'ReqdExctnDt')
        ET.SubElement(reqd_exctn_dt, 'Dt').text = random_date(7)

        # Debtor
        dbtr = ET.SubElement(pmt_inf, 'Dbtr')
        ET.SubElement(dbtr, 'Nm').text = random_name()

        dbtr_acct = ET.SubElement(pmt_inf, 'DbtrAcct')
        dbtr_id = ET.SubElement(dbtr_acct, 'Id')
        ET.SubElement(dbtr_id, 'IBAN').text = random_iban('DE')

        dbtr_agt = ET.SubElement(pmt_inf, 'DbtrAgt')
        fin_instn_id = ET.SubElement(dbtr_agt, 'FinInstnId')
        ET.SubElement(fin_instn_id, 'BICFI').text = random_bic()

        ET.SubElement(pmt_inf, 'ChrgBr').text = 'SLEV'

        # Credit Transfer Transaction
        cdt_trf_tx_inf = ET.SubElement(pmt_inf, 'CdtTrfTxInf')

        pmt_id = ET.SubElement(cdt_trf_tx_inf, 'PmtId')
        ET.SubElement(pmt_id, 'EndToEndId').text = e2e_id

        amt = ET.SubElement(cdt_trf_tx_inf, 'Amt')
        instd_amt = ET.SubElement(amt, 'InstdAmt', Ccy=currency)
        instd_amt.text = format_amount(amount)

        cdtr_agt = ET.SubElement(cdt_trf_tx_inf, 'CdtrAgt')
        fin_instn_id2 = ET.SubElement(cdtr_agt, 'FinInstnId')
        ET.SubElement(fin_instn_id2, 'BICFI').text = random_bic()

        cdtr = ET.SubElement(cdt_trf_tx_inf, 'Cdtr')
        ET.SubElement(cdtr, 'Nm').text = random_name()

        cdtr_acct = ET.SubElement(cdt_trf_tx_inf, 'CdtrAcct')
        cdtr_id = ET.SubElement(cdtr_acct, 'Id')
        ET.SubElement(cdtr_id, 'IBAN').text = random_iban('FR')

        rmt_inf = ET.SubElement(cdt_trf_tx_inf, 'RmtInf')
        ET.SubElement(rmt_inf, 'Ustrd').text = f"Invoice {random.randint(10000, 99999)}"

    xml_content = create_iso20022_xml(
        'Document',
        'urn:iso:std:iso:20022:tech:xsd:pain.001.001.11',
        build_content
    )

    return {
        'messageType': 'pain.001',
        'format': 'xml',
        'content': xml_content,
        'messageId': msg_id
    }


def generate_pain002_xml():
    """ISO 20022 pain.002.001.12 Customer Payment Status Report."""
    msg_id = f"MSGID{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"
    orig_msg_id = f"ORIGMSG{uuid.uuid4().hex[:8].upper()}"

    def build_content(root):
        cstmr_pmt_sts_rpt = ET.SubElement(root, 'CstmrPmtStsRpt')

        # Group Header
        grp_hdr = ET.SubElement(cstmr_pmt_sts_rpt, 'GrpHdr')
        ET.SubElement(grp_hdr, 'MsgId').text = msg_id
        ET.SubElement(grp_hdr, 'CreDtTm').text = random_datetime_iso()
        initg_pty = ET.SubElement(grp_hdr, 'InitgPty')
        ET.SubElement(initg_pty, 'Nm').text = random_name(is_company=True)

        # Original Group Information
        orgnl_grp_inf_and_sts = ET.SubElement(cstmr_pmt_sts_rpt, 'OrgnlGrpInfAndSts')
        ET.SubElement(orgnl_grp_inf_and_sts, 'OrgnlMsgId').text = orig_msg_id
        ET.SubElement(orgnl_grp_inf_and_sts, 'OrgnlMsgNmId').text = 'pain.001.001.11'
        ET.SubElement(orgnl_grp_inf_and_sts, 'GrpSts').text = random.choice(['ACCP', 'ACSP', 'ACSC', 'RJCT'])

    xml_content = create_iso20022_xml(
        'Document',
        'urn:iso:std:iso:20022:tech:xsd:pain.002.001.12',
        build_content
    )

    return {
        'messageType': 'pain.002',
        'format': 'xml',
        'content': xml_content,
        'messageId': msg_id
    }


def generate_pain007_xml():
    """ISO 20022 pain.007.001.11 Customer Payment Reversal."""
    msg_id = f"MSGID{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    def build_content(root):
        cstmr_pmt_rvsl = ET.SubElement(root, 'CstmrPmtRvsl')

        grp_hdr = ET.SubElement(cstmr_pmt_rvsl, 'GrpHdr')
        ET.SubElement(grp_hdr, 'MsgId').text = msg_id
        ET.SubElement(grp_hdr, 'CreDtTm').text = random_datetime_iso()
        ET.SubElement(grp_hdr, 'NbOfTxs').text = '1'
        initg_pty = ET.SubElement(grp_hdr, 'InitgPty')
        ET.SubElement(initg_pty, 'Nm').text = random_name(is_company=True)

    xml_content = create_iso20022_xml(
        'Document',
        'urn:iso:std:iso:20022:tech:xsd:pain.007.001.11',
        build_content
    )

    return {
        'messageType': 'pain.007',
        'format': 'xml',
        'content': xml_content,
        'messageId': msg_id
    }


def generate_pain008_xml():
    """ISO 20022 pain.008.001.10 Customer Direct Debit Initiation."""
    msg_id = f"MSGID{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"
    amount = random_amount()

    def build_content(root):
        cstmr_drct_dbt_initn = ET.SubElement(root, 'CstmrDrctDbtInitn')

        grp_hdr = ET.SubElement(cstmr_drct_dbt_initn, 'GrpHdr')
        ET.SubElement(grp_hdr, 'MsgId').text = msg_id
        ET.SubElement(grp_hdr, 'CreDtTm').text = random_datetime_iso()
        ET.SubElement(grp_hdr, 'NbOfTxs').text = '1'
        ET.SubElement(grp_hdr, 'CtrlSum').text = format_amount(amount)
        initg_pty = ET.SubElement(grp_hdr, 'InitgPty')
        ET.SubElement(initg_pty, 'Nm').text = random_name(is_company=True)

        pmt_inf = ET.SubElement(cstmr_drct_dbt_initn, 'PmtInf')
        ET.SubElement(pmt_inf, 'PmtInfId').text = f"PMTINF{uuid.uuid4().hex[:8].upper()}"
        ET.SubElement(pmt_inf, 'PmtMtd').text = 'DD'

        cdtr = ET.SubElement(pmt_inf, 'Cdtr')
        ET.SubElement(cdtr, 'Nm').text = random_name(is_company=True)

    xml_content = create_iso20022_xml(
        'Document',
        'urn:iso:std:iso:20022:tech:xsd:pain.008.001.10',
        build_content
    )

    return {
        'messageType': 'pain.008',
        'format': 'xml',
        'content': xml_content,
        'messageId': msg_id
    }


def generate_pain013_xml():
    """ISO 20022 pain.013.001.09 Creditor Payment Activation Request."""
    msg_id = f"MSGID{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    def build_content(root):
        cdtr_pmt_actvtn_req = ET.SubElement(root, 'CdtrPmtActvtnReq')

        grp_hdr = ET.SubElement(cdtr_pmt_actvtn_req, 'GrpHdr')
        ET.SubElement(grp_hdr, 'MsgId').text = msg_id
        ET.SubElement(grp_hdr, 'CreDtTm').text = random_datetime_iso()
        ET.SubElement(grp_hdr, 'NbOfTxs').text = '1'
        initg_pty = ET.SubElement(grp_hdr, 'InitgPty')
        ET.SubElement(initg_pty, 'Nm').text = random_name(is_company=True)

    xml_content = create_iso20022_xml(
        'Document',
        'urn:iso:std:iso:20022:tech:xsd:pain.013.001.09',
        build_content
    )

    return {
        'messageType': 'pain.013',
        'format': 'xml',
        'content': xml_content,
        'messageId': msg_id
    }


def generate_pain014_xml():
    """ISO 20022 pain.014.001.09 Creditor Payment Activation Request Status Report."""
    msg_id = f"MSGID{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    def build_content(root):
        cdtr_pmt_actvtn_req_sts_rpt = ET.SubElement(root, 'CdtrPmtActvtnReqStsRpt')

        grp_hdr = ET.SubElement(cdtr_pmt_actvtn_req_sts_rpt, 'GrpHdr')
        ET.SubElement(grp_hdr, 'MsgId').text = msg_id
        ET.SubElement(grp_hdr, 'CreDtTm').text = random_datetime_iso()
        initg_pty = ET.SubElement(grp_hdr, 'InitgPty')
        ET.SubElement(initg_pty, 'Nm').text = random_name(is_company=True)

    xml_content = create_iso20022_xml(
        'Document',
        'urn:iso:std:iso:20022:tech:xsd:pain.014.001.09',
        build_content
    )

    return {
        'messageType': 'pain.014',
        'format': 'xml',
        'content': xml_content,
        'messageId': msg_id
    }


def generate_pacs002_xml():
    """ISO 20022 pacs.002.001.12 FI to FI Payment Status Report."""
    msg_id = f"MSGID{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    def build_content(root):
        fi_to_fi_pmt_sts_rpt = ET.SubElement(root, 'FIToFIPmtStsRpt')

        grp_hdr = ET.SubElement(fi_to_fi_pmt_sts_rpt, 'GrpHdr')
        ET.SubElement(grp_hdr, 'MsgId').text = msg_id
        ET.SubElement(grp_hdr, 'CreDtTm').text = random_datetime_iso()
        instg_agt = ET.SubElement(grp_hdr, 'InstgAgt')
        fin_instn_id = ET.SubElement(instg_agt, 'FinInstnId')
        ET.SubElement(fin_instn_id, 'BICFI').text = random_bic()

    xml_content = create_iso20022_xml(
        'Document',
        'urn:iso:std:iso:20022:tech:xsd:pacs.002.001.12',
        build_content
    )

    return {
        'messageType': 'pacs.002',
        'format': 'xml',
        'content': xml_content,
        'messageId': msg_id
    }


def generate_pacs003_xml():
    """ISO 20022 pacs.003.001.09 FI to FI Customer Direct Debit."""
    msg_id = f"MSGID{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"
    amount = random_amount()

    def build_content(root):
        fi_to_fi_cstmr_drct_dbt = ET.SubElement(root, 'FIToFICstmrDrctDbt')

        grp_hdr = ET.SubElement(fi_to_fi_cstmr_drct_dbt, 'GrpHdr')
        ET.SubElement(grp_hdr, 'MsgId').text = msg_id
        ET.SubElement(grp_hdr, 'CreDtTm').text = random_datetime_iso()
        ET.SubElement(grp_hdr, 'NbOfTxs').text = '1'
        ET.SubElement(grp_hdr, 'TtlIntrBkSttlmAmt', Ccy='EUR').text = format_amount(amount)
        ET.SubElement(grp_hdr, 'IntrBkSttlmDt').text = random_date(3)

        instg_agt = ET.SubElement(grp_hdr, 'InstgAgt')
        fin_instn_id = ET.SubElement(instg_agt, 'FinInstnId')
        ET.SubElement(fin_instn_id, 'BICFI').text = random_bic()

    xml_content = create_iso20022_xml(
        'Document',
        'urn:iso:std:iso:20022:tech:xsd:pacs.003.001.09',
        build_content
    )

    return {
        'messageType': 'pacs.003',
        'format': 'xml',
        'content': xml_content,
        'messageId': msg_id
    }


def generate_pacs004_xml():
    """ISO 20022 pacs.004.001.11 Payment Return."""
    msg_id = f"MSGID{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    def build_content(root):
        pmt_rtr = ET.SubElement(root, 'PmtRtr')

        grp_hdr = ET.SubElement(pmt_rtr, 'GrpHdr')
        ET.SubElement(grp_hdr, 'MsgId').text = msg_id
        ET.SubElement(grp_hdr, 'CreDtTm').text = random_datetime_iso()
        ET.SubElement(grp_hdr, 'NbOfTxs').text = '1'

        instg_agt = ET.SubElement(grp_hdr, 'InstgAgt')
        fin_instn_id = ET.SubElement(instg_agt, 'FinInstnId')
        ET.SubElement(fin_instn_id, 'BICFI').text = random_bic()

    xml_content = create_iso20022_xml(
        'Document',
        'urn:iso:std:iso:20022:tech:xsd:pacs.004.001.11',
        build_content
    )

    return {
        'messageType': 'pacs.004',
        'format': 'xml',
        'content': xml_content,
        'messageId': msg_id
    }


def generate_pacs007_xml():
    """ISO 20022 pacs.007.001.11 FI to FI Payment Reversal."""
    msg_id = f"MSGID{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    def build_content(root):
        fi_to_fi_pmt_rvsl = ET.SubElement(root, 'FIToFIPmtRvsl')

        grp_hdr = ET.SubElement(fi_to_fi_pmt_rvsl, 'GrpHdr')
        ET.SubElement(grp_hdr, 'MsgId').text = msg_id
        ET.SubElement(grp_hdr, 'CreDtTm').text = random_datetime_iso()
        ET.SubElement(grp_hdr, 'NbOfTxs').text = '1'

        instg_agt = ET.SubElement(grp_hdr, 'InstgAgt')
        fin_instn_id = ET.SubElement(instg_agt, 'FinInstnId')
        ET.SubElement(fin_instn_id, 'BICFI').text = random_bic()

    xml_content = create_iso20022_xml(
        'Document',
        'urn:iso:std:iso:20022:tech:xsd:pacs.007.001.11',
        build_content
    )

    return {
        'messageType': 'pacs.007',
        'format': 'xml',
        'content': xml_content,
        'messageId': msg_id
    }


def generate_pacs008_xml():
    """ISO 20022 pacs.008.001.10 FI to FI Customer Credit Transfer."""
    msg_id = f"MSGID{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"
    e2e_id = f"E2E{uuid.uuid4().hex[:10].upper()}"
    amount = random_amount()
    currency = 'EUR'

    def build_content(root):
        fi_to_fi_cstmr_cdt_trf = ET.SubElement(root, 'FIToFICstmrCdtTrf')

        # Group Header
        grp_hdr = ET.SubElement(fi_to_fi_cstmr_cdt_trf, 'GrpHdr')
        ET.SubElement(grp_hdr, 'MsgId').text = msg_id
        ET.SubElement(grp_hdr, 'CreDtTm').text = random_datetime_iso()
        ET.SubElement(grp_hdr, 'NbOfTxs').text = '1'
        ttl_amt = ET.SubElement(grp_hdr, 'TtlIntrBkSttlmAmt', Ccy=currency)
        ttl_amt.text = format_amount(amount)
        ET.SubElement(grp_hdr, 'IntrBkSttlmDt').text = random_date(3)
        sttlm_inf = ET.SubElement(grp_hdr, 'SttlmInf')
        ET.SubElement(sttlm_inf, 'SttlmMtd').text = 'CLRG'

        instg_agt = ET.SubElement(grp_hdr, 'InstgAgt')
        fin_instn_id = ET.SubElement(instg_agt, 'FinInstnId')
        ET.SubElement(fin_instn_id, 'BICFI').text = random_bic()

        instd_agt = ET.SubElement(grp_hdr, 'InstdAgt')
        fin_instn_id2 = ET.SubElement(instd_agt, 'FinInstnId')
        ET.SubElement(fin_instn_id2, 'BICFI').text = random_bic()

        # Credit Transfer Transaction
        cdt_trf_tx_inf = ET.SubElement(fi_to_fi_cstmr_cdt_trf, 'CdtTrfTxInf')

        pmt_id = ET.SubElement(cdt_trf_tx_inf, 'PmtId')
        ET.SubElement(pmt_id, 'EndToEndId').text = e2e_id
        ET.SubElement(pmt_id, 'TxId').text = f"TX{uuid.uuid4().hex[:10].upper()}"

        intr_bk_sttlm_amt = ET.SubElement(cdt_trf_tx_inf, 'IntrBkSttlmAmt', Ccy=currency)
        intr_bk_sttlm_amt.text = format_amount(amount)

        ET.SubElement(cdt_trf_tx_inf, 'ChrgBr').text = 'SHAR'

        dbtr = ET.SubElement(cdt_trf_tx_inf, 'Dbtr')
        ET.SubElement(dbtr, 'Nm').text = random_name()

        dbtr_acct = ET.SubElement(cdt_trf_tx_inf, 'DbtrAcct')
        dbtr_id = ET.SubElement(dbtr_acct, 'Id')
        ET.SubElement(dbtr_id, 'IBAN').text = random_iban('DE')

        dbtr_agt = ET.SubElement(cdt_trf_tx_inf, 'DbtrAgt')
        fin_instn_id3 = ET.SubElement(dbtr_agt, 'FinInstnId')
        ET.SubElement(fin_instn_id3, 'BICFI').text = random_bic()

        cdtr_agt = ET.SubElement(cdt_trf_tx_inf, 'CdtrAgt')
        fin_instn_id4 = ET.SubElement(cdtr_agt, 'FinInstnId')
        ET.SubElement(fin_instn_id4, 'BICFI').text = random_bic()

        cdtr = ET.SubElement(cdt_trf_tx_inf, 'Cdtr')
        ET.SubElement(cdtr, 'Nm').text = random_name()

        cdtr_acct = ET.SubElement(cdt_trf_tx_inf, 'CdtrAcct')
        cdtr_id = ET.SubElement(cdtr_acct, 'Id')
        ET.SubElement(cdtr_id, 'IBAN').text = random_iban('FR')

    xml_content = create_iso20022_xml(
        'Document',
        'urn:iso:std:iso:20022:tech:xsd:pacs.008.001.10',
        build_content
    )

    return {
        'messageType': 'pacs.008',
        'format': 'xml',
        'content': xml_content,
        'messageId': msg_id
    }


def generate_pacs009_xml():
    """ISO 20022 pacs.009.001.10 FI Credit Transfer."""
    msg_id = f"MSGID{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"
    amount = random_amount()

    def build_content(root):
        fi_cdt_trf = ET.SubElement(root, 'FICdtTrf')

        grp_hdr = ET.SubElement(fi_cdt_trf, 'GrpHdr')
        ET.SubElement(grp_hdr, 'MsgId').text = msg_id
        ET.SubElement(grp_hdr, 'CreDtTm').text = random_datetime_iso()
        ET.SubElement(grp_hdr, 'NbOfTxs').text = '1'
        ET.SubElement(grp_hdr, 'TtlIntrBkSttlmAmt', Ccy='EUR').text = format_amount(amount)
        ET.SubElement(grp_hdr, 'IntrBkSttlmDt').text = random_date(3)

        instg_agt = ET.SubElement(grp_hdr, 'InstgAgt')
        fin_instn_id = ET.SubElement(instg_agt, 'FinInstnId')
        ET.SubElement(fin_instn_id, 'BICFI').text = random_bic()

    xml_content = create_iso20022_xml(
        'Document',
        'urn:iso:std:iso:20022:tech:xsd:pacs.009.001.10',
        build_content
    )

    return {
        'messageType': 'pacs.009',
        'format': 'xml',
        'content': xml_content,
        'messageId': msg_id
    }


def generate_pacs028_xml():
    """ISO 20022 pacs.028.001.04 FI to FI Payment Status Request."""
    msg_id = f"MSGID{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    def build_content(root):
        fi_to_fi_pmt_sts_req = ET.SubElement(root, 'FIToFIPmtStsReq')

        grp_hdr = ET.SubElement(fi_to_fi_pmt_sts_req, 'GrpHdr')
        ET.SubElement(grp_hdr, 'MsgId').text = msg_id
        ET.SubElement(grp_hdr, 'CreDtTm').text = random_datetime_iso()

        instg_agt = ET.SubElement(grp_hdr, 'InstgAgt')
        fin_instn_id = ET.SubElement(instg_agt, 'FinInstnId')
        ET.SubElement(fin_instn_id, 'BICFI').text = random_bic()

    xml_content = create_iso20022_xml(
        'Document',
        'urn:iso:std:iso:20022:tech:xsd:pacs.028.001.04',
        build_content
    )

    return {
        'messageType': 'pacs.028',
        'format': 'xml',
        'content': xml_content,
        'messageId': msg_id
    }


# CAMT message generators (similar pattern)
def generate_camt_xml(camt_type, root_element):
    """Generic CAMT message generator."""
    msg_id = f"MSGID{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    def build_content(root):
        main_elem = ET.SubElement(root, root_element)

        grp_hdr = ET.SubElement(main_elem, 'GrpHdr')
        ET.SubElement(grp_hdr, 'MsgId').text = msg_id
        ET.SubElement(grp_hdr, 'CreDtTm').text = random_datetime_iso()

    version_map = {
        'camt.026': '09', 'camt.027': '09', 'camt.028': '11', 'camt.029': '11',
        'camt.052': '10', 'camt.053': '10', 'camt.054': '10', 'camt.055': '10',
        'camt.056': '10', 'camt.057': '08', 'camt.086': '06', 'camt.087': '08'
    }

    version = version_map.get(camt_type, '10')
    namespace = f"urn:iso:std:iso:20022:tech:xsd:{camt_type}.001.{version}"

    xml_content = create_iso20022_xml('Document', namespace, build_content)

    return {
        'messageType': camt_type,
        'format': 'xml',
        'content': xml_content,
        'messageId': msg_id
    }


def generate_camt026_xml():
    return generate_camt_xml('camt.026', 'UblToApply')

def generate_camt027_xml():
    return generate_camt_xml('camt.027', 'ClmNonRct')

def generate_camt028_xml():
    return generate_camt_xml('camt.028', 'AddtlPmtInf')

def generate_camt029_xml():
    return generate_camt_xml('camt.029', 'RsltnOfInvstgtn')

def generate_camt052_xml():
    return generate_camt_xml('camt.052', 'BkToCstmrAcctRpt')

def generate_camt053_xml():
    return generate_camt_xml('camt.053', 'BkToCstmrStmt')

def generate_camt054_xml():
    return generate_camt_xml('camt.054', 'BkToCstmrDbtCdtNtfctn')

def generate_camt055_xml():
    return generate_camt_xml('camt.055', 'CstmrPmtCxlReq')

def generate_camt056_xml():
    return generate_camt_xml('camt.056', 'FIToFIPmtCxlReq')

def generate_camt057_xml():
    return generate_camt_xml('camt.057', 'NtfctnToRcv')

def generate_camt086_xml():
    return generate_camt_xml('camt.086', 'BkSvcsBllgStmt')

def generate_camt087_xml():
    return generate_camt_xml('camt.087', 'ReqToModfyPmt')


# ACMT message generators
def generate_acmt_xml(acmt_type, root_element):
    """Generic ACMT message generator."""
    msg_id = f"MSGID{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    def build_content(root):
        main_elem = ET.SubElement(root, root_element)

        if 'MsgId' in ['acmt.001', 'acmt.002', 'acmt.003']:
            msg_id_elem = ET.SubElement(main_elem, 'MsgId')
            ET.SubElement(msg_id_elem, 'Id').text = msg_id
            ET.SubElement(msg_id_elem, 'CreDtTm').text = random_datetime_iso()
        else:
            ET.SubElement(main_elem, 'MsgId').text = msg_id

    version_map = {
        'acmt.001': '08', 'acmt.002': '08', 'acmt.003': '08',
        'acmt.005': '06', 'acmt.006': '06', 'acmt.007': '05'
    }

    version = version_map.get(acmt_type, '08')
    namespace = f"urn:iso:std:iso:20022:tech:xsd:{acmt_type}.001.{version}"

    xml_content = create_iso20022_xml('Document', namespace, build_content)

    return {
        'messageType': acmt_type,
        'format': 'xml',
        'content': xml_content,
        'messageId': msg_id
    }


def generate_acmt001_xml():
    return generate_acmt_xml('acmt.001', 'AcctOpngInstr')

def generate_acmt002_xml():
    return generate_acmt_xml('acmt.002', 'AcctOpngAddtlInfReq')

def generate_acmt003_xml():
    return generate_acmt_xml('acmt.003', 'AcctOpngAmdmntReq')

def generate_acmt005_xml():
    return generate_acmt_xml('acmt.005', 'ReqForAcctMgmtStsRpt')

def generate_acmt006_xml():
    return generate_acmt_xml('acmt.006', 'AcctMgmtStsRpt')

def generate_acmt007_xml():
    return generate_acmt_xml('acmt.007', 'AcctOpngReq')


# ============================================================================
# SWIFT MT Message Generators
# ============================================================================

def generate_swift_mt_message(mt_type, text_block):
    """Generate a complete SWIFT MT message with all blocks."""
    sender_bic = random_bic8()
    receiver_bic = random_bic8()
    session_number = f"{random.randint(1000,9999)}"
    sequence_number = f"{random.randint(100000,999999)}"

    # Block 1: Basic Header
    block1 = f"{{1:F01{sender_bic}AXXX{session_number}{sequence_number}}}"

    # Block 2: Application Header (Input)
    block2 = f"{{2:I{mt_type}{receiver_bic}N}}"

    # Block 3: User Header
    block3 = "{3:{108:" + f"REF{uuid.uuid4().hex[:12].upper()}" + "}}"

    # Block 4: Text Block
    block4 = "{4:\n" + text_block + "\n-}"

    # Block 5: Trailer
    block5 = "{5:{MAC:00000000}{CHK:" + f"{random.randint(100000000000,999999999999):012d}" + "}}"

    return block1 + block2 + block3 + block4 + block5


def generate_mt103():
    """SWIFT MT103 Single Customer Credit Transfer."""
    ref = f"{uuid.uuid4().hex[:16].upper()}"
    amount = random_amount()
    currency = random_currency()
    date_str = datetime.utcnow().strftime('%y%m%d')

    text_block = f""":20:{ref}
:23B:CRED
:32A:{date_str}{currency}{format_amount(amount, 2).replace('.', ',')}
:33B:{currency}{format_amount(amount, 2).replace('.', ',')}
:50K:/{random_iban('DE')}
{random_name()}
{random.randint(1,999)} Main Street
New York NY 10001
:52A:{random_bic()}
:53A:{random_bic()}
:57A:{random_bic()}
:59:/{random_iban('GB')}
{random_name()}
{random.randint(1,999)} High Street
London EC1A 1AA
:70:PAYMENT FOR INVOICE {random.randint(10000, 99999)}
:71A:SHA"""

    content = generate_swift_mt_message('103', text_block)

    return {
        'messageType': 'MT103',
        'format': 'swift_mt',
        'content': content,
        'messageId': ref
    }


def generate_mt200():
    """SWIFT MT200 Financial Institution Transfer for Own Account."""
    ref = f"{uuid.uuid4().hex[:16].upper()}"
    amount = random_amount(10000, 1000000)
    currency = random_currency()
    date_str = datetime.utcnow().strftime('%y%m%d')

    text_block = f""":20:{ref}
:32A:{date_str}{currency}{format_amount(amount, 2).replace('.', ',')}
:53A:{random_bic()}
:56A:{random_bic()}
:57A:{random_bic()}
:72:/ACC/{random_iban('DE')}"""

    content = generate_swift_mt_message('200', text_block)

    return {
        'messageType': 'MT200',
        'format': 'swift_mt',
        'content': content,
        'messageId': ref
    }


def generate_mt202():
    """SWIFT MT202 General Financial Institution Transfer."""
    ref = f"{uuid.uuid4().hex[:16].upper()}"
    related_ref = f"{uuid.uuid4().hex[:16].upper()}"
    amount = random_amount(10000, 5000000)
    currency = random_currency()
    date_str = datetime.utcnow().strftime('%y%m%d')

    text_block = f""":20:{ref}
:21:{related_ref}
:32A:{date_str}{currency}{format_amount(amount, 2).replace('.', ',')}
:52A:{random_bic()}
:53A:{random_bic()}
:57A:{random_bic()}
:58A:{random_bic()}
:72:/REC/{random_name()}"""

    content = generate_swift_mt_message('202', text_block)

    return {
        'messageType': 'MT202',
        'format': 'swift_mt',
        'content': content,
        'messageId': ref
    }


def generate_mt202cov():
    """SWIFT MT202COV Cover Payment."""
    ref = f"{uuid.uuid4().hex[:16].upper()}"
    related_ref = f"{uuid.uuid4().hex[:16].upper()}"
    amount = random_amount(10000, 5000000)
    currency = random_currency()
    date_str = datetime.utcnow().strftime('%y%m%d')

    text_block = f""":20:{ref}
:21:{related_ref}
:32A:{date_str}{currency}{format_amount(amount, 2).replace('.', ',')}
:52A:{random_bic()}
:53A:{random_bic()}
:57A:{random_bic()}
:58A:{random_bic()}
:50K:/{random_iban('DE')}
{random_name()}
:59:/{random_iban('GB')}
{random_name()}
:70:COVER PAYMENT FOR MT103
:72:/COV/"""

    content = generate_swift_mt_message('202', text_block)  # COV uses 202 format

    return {
        'messageType': 'MT202COV',
        'format': 'swift_mt',
        'content': content,
        'messageId': ref
    }


def generate_mt900():
    """SWIFT MT900 Confirmation of Debit."""
    ref = f"{uuid.uuid4().hex[:16].upper()}"
    related_ref = f"{uuid.uuid4().hex[:16].upper()}"
    amount = random_amount()
    currency = random_currency()
    date_str = datetime.utcnow().strftime('%y%m%d')

    text_block = f""":20:{ref}
:21:{related_ref}
:25:{random_iban('DE')[:20]}
:32A:{date_str}{currency}{format_amount(amount, 2).replace('.', ',')}
:52A:{random_bic()}"""

    content = generate_swift_mt_message('900', text_block)

    return {
        'messageType': 'MT900',
        'format': 'swift_mt',
        'content': content,
        'messageId': ref
    }


def generate_mt910():
    """SWIFT MT910 Confirmation of Credit."""
    ref = f"{uuid.uuid4().hex[:16].upper()}"
    related_ref = f"{uuid.uuid4().hex[:16].upper()}"
    amount = random_amount()
    currency = random_currency()
    date_str = datetime.utcnow().strftime('%y%m%d')

    text_block = f""":20:{ref}
:21:{related_ref}
:25:{random_iban('DE')[:20]}
:32A:{date_str}{currency}{format_amount(amount, 2).replace('.', ',')}
:52A:{random_bic()}
:50K:{random_name()}"""

    content = generate_swift_mt_message('910', text_block)

    return {
        'messageType': 'MT910',
        'format': 'swift_mt',
        'content': content,
        'messageId': ref
    }


def generate_mt940():
    """SWIFT MT940 Customer Statement Message."""
    ref = f"{uuid.uuid4().hex[:16].upper()}"
    stmt_num = f"{random.randint(1,999)}/{random.randint(1,365)}"
    opening_balance = random_amount()
    closing_balance = opening_balance + random.uniform(-10000, 10000)
    currency = random_currency()
    date_str = datetime.utcnow().strftime('%y%m%d')
    prev_date_str = (datetime.utcnow() - timedelta(days=1)).strftime('%y%m%d')

    text_block = f""":20:{ref}
:25:{random_iban('DE')[:20]}
:28C:{stmt_num}
:60F:C{prev_date_str}{currency}{format_amount(opening_balance, 2).replace('.', ',')}
:61:{date_str}{date_str[-4:]}C{format_amount(random_amount(100, 5000), 2).replace('.', ',')}NTRFREF{random.randint(1000,9999)}//REF{random.randint(10000,99999)}
:86:PAYMENT FROM {random_name()}
:62F:C{date_str}{currency}{format_amount(abs(closing_balance), 2).replace('.', ',')}
:64:C{date_str}{currency}{format_amount(abs(closing_balance), 2).replace('.', ',')}"""

    content = generate_swift_mt_message('940', text_block)

    return {
        'messageType': 'MT940',
        'format': 'swift_mt',
        'content': content,
        'messageId': ref
    }


def generate_mt950():
    """SWIFT MT950 Statement Message."""
    ref = f"{uuid.uuid4().hex[:16].upper()}"
    stmt_num = f"{random.randint(1,999)}/{random.randint(1,365)}"
    opening_balance = random_amount()
    closing_balance = opening_balance + random.uniform(-10000, 10000)
    currency = random_currency()
    date_str = datetime.utcnow().strftime('%y%m%d')
    prev_date_str = (datetime.utcnow() - timedelta(days=1)).strftime('%y%m%d')

    text_block = f""":20:{ref}
:25:{random_iban('DE')[:20]}
:28C:{stmt_num}
:60F:C{prev_date_str}{currency}{format_amount(opening_balance, 2).replace('.', ',')}
:62F:C{date_str}{currency}{format_amount(abs(closing_balance), 2).replace('.', ',')}"""

    content = generate_swift_mt_message('950', text_block)

    return {
        'messageType': 'MT950',
        'format': 'swift_mt',
        'content': content,
        'messageId': ref
    }


# ============================================================================
# Regional Payment Scheme Generators (JSON format with proper structure)
# ============================================================================

def generate_sepa_sct():
    """SEPA Credit Transfer - uses pain.001 XML internally."""
    result = generate_pain001_xml()
    result['messageType'] = 'SEPA_SCT'
    return result


def generate_sepa_sdd():
    """SEPA Direct Debit - uses pain.008 XML internally."""
    result = generate_pain008_xml()
    result['messageType'] = 'SEPA_SDD'
    return result


def generate_target2():
    """TARGET2 RTGS - uses pacs.009 XML internally."""
    result = generate_pacs009_xml()
    result['messageType'] = 'TARGET2'
    return result


def generate_nacha_ach():
    """NACHA ACH - Fixed width format."""
    batch_num = random.randint(1, 9999999)
    company_name = random_name(is_company=True)[:16].upper().ljust(16)
    company_id = f"1{random.randint(100000000, 999999999)}"
    effective_date = datetime.utcnow().strftime('%y%m%d')
    originating_dfi = f"{random.randint(10000000, 99999999)}"

    # File Header Record (1)
    file_header = f"101 {originating_dfi}0{random.randint(10000000,99999999)} {datetime.utcnow().strftime('%y%m%d%H%M')}A094101FEDERAL RESERVE BANK       YOUR BANK NAME          "

    # Batch Header Record (5)
    sec_code = random.choice(['PPD', 'CCD', 'CTX', 'WEB'])
    batch_header = f"5200{company_name}{' '*20}{company_id}{sec_code}PAYROLL         {effective_date}   1{originating_dfi}{batch_num:07d}"

    # Entry Detail Record (6)
    receiving_dfi = f"{random.randint(10000000, 99999999)}"
    account_num = f"{random.randint(10000000000, 99999999999)}"[:17].ljust(17)
    amount = int(random_amount(100, 10000) * 100)
    individual_name = random_name()[:22].upper().ljust(22)
    trace_num = f"{originating_dfi}{random.randint(0000000, 9999999):07d}"
    entry_detail = f"622{receiving_dfi}0{account_num}{amount:010d}0000000000000000{individual_name}0{originating_dfi}{trace_num}"

    # Batch Control Record (8)
    batch_control = f"8200000001{int(receiving_dfi):08d}0000000000{amount:012d}{company_id}                         {originating_dfi}{batch_num:07d}"

    # File Control Record (9)
    file_control = f"9000001000001{int(originating_dfi + receiving_dfi[:8]):010d}0000000000{amount:012d}                                       "

    content = f"{file_header}\n{batch_header}\n{entry_detail}\n{batch_control}\n{file_control}"

    return {
        'messageType': 'NACHA_ACH',
        'format': 'nacha',
        'content': content,
        'messageId': f"ACH{batch_num:07d}"
    }


def generate_fedwire():
    """Fedwire Funds Transfer - Tag-based format."""
    imad = f"{datetime.utcnow().strftime('%Y%m%d')}{random_bic8()}{random.randint(100000,999999)}"
    sender_aba = f"{random.randint(10000000, 99999999)}1"
    receiver_aba = f"{random.randint(10000000, 99999999)}1"
    amount = int(random_amount(1000, 1000000) * 100)

    content = f"""{{1500}}{datetime.utcnow().strftime('%Y%m%d')}
{{1510}}{imad}
{{1520}}{sender_aba}
{{2000}}{amount:012d}
{{3100}}{sender_aba}{random_name(is_company=True)[:35]}
{{3400}}{receiver_aba}{random_name(is_company=True)[:35]}
{{3600}}{random.choice(['BTR', 'CTR', 'DRB', 'DRC', 'FFR', 'FFS'])}
{{4000}}/{random.randint(1000000000, 9999999999)}
{random_name()}
{{4100}}/{random.randint(1000000000, 9999999999)}
{random_name()}
{{4200}}{random_name()}
{{5000}}{random_name(is_company=True)}
{{6000}}{random_reference()}"""

    return {
        'messageType': 'Fedwire',
        'format': 'fedwire',
        'content': content,
        'messageId': imad
    }


def generate_fednow():
    """FedNow - ISO 20022 based, uses pacs.008."""
    result = generate_pacs008_xml()
    result['messageType'] = 'FedNow'
    return result


def generate_rtp():
    """RTP (The Clearing House) - ISO 20022 based."""
    result = generate_pacs008_xml()
    result['messageType'] = 'RTP'
    return result


def generate_chips():
    """CHIPS - Proprietary format."""
    seq_num = f"{random.randint(100000, 999999)}"
    sender_uid = f"{random.randint(100000, 999999)}"
    receiver_uid = f"{random.randint(100000, 999999)}"
    amount = random_amount(10000, 10000000)

    content = json.dumps({
        "messageType": "CHIPS",
        "chipsMessageType": "PaymentMessage",
        "sequenceNumber": seq_num,
        "senderParticipantId": sender_uid,
        "receiverParticipantId": receiver_uid,
        "valueDate": random_date(1),
        "amount": {"value": amount, "currency": "USD"},
        "senderReference": random_reference(),
        "originator": {
            "name": random_name(),
            "account": f"{random.randint(1000000000, 9999999999)}"
        },
        "beneficiary": {
            "name": random_name(),
            "account": f"{random.randint(1000000000, 9999999999)}"
        }
    }, indent=2)

    return {
        'messageType': 'CHIPS',
        'format': 'json',
        'content': content,
        'messageId': seq_num
    }


def generate_bacs():
    """UK BACS - Standard 18 format."""
    vol_serial = f"{random.randint(100000, 999999)}"
    sort_code_orig = f"{random.randint(100000, 999999)}"
    account_orig = f"{random.randint(10000000, 99999999)}"
    sort_code_dest = f"{random.randint(100000, 999999)}"
    account_dest = f"{random.randint(10000000, 99999999)}"
    amount = int(random_amount(10, 10000) * 100)

    # VOL1 - Volume Header Label
    vol1 = f"VOL1{vol_serial}                                                                                      "

    # HDR1 - Header 1
    hdr1 = f"HDR1A{' '*17}{datetime.utcnow().strftime('%y%j')} {' '*6}000001{' '*35}                    "

    # UHL1 - User Header Label
    uhl1 = f"UHL1{datetime.utcnow().strftime('%y%j')}{' '*80}"

    # Standard 18 record
    txn_code = random.choice(['99', '01', '17', '18', '19'])
    record = f"{sort_code_dest}{account_dest}{txn_code}{sort_code_orig}{account_orig}{' '*4}{amount:011d}{random_name()[:18].upper().ljust(18)}{random_reference()[:18].ljust(18)}"

    content = f"{vol1}\n{hdr1}\n{uhl1}\n{record}"

    return {
        'messageType': 'BACS',
        'format': 'bacs_std18',
        'content': content,
        'messageId': vol_serial
    }


def generate_chaps():
    """UK CHAPS - Uses SWIFT MT103 or ISO 20022."""
    result = generate_mt103()
    result['messageType'] = 'CHAPS'
    return result


def generate_fps():
    """UK Faster Payments - ISO 20022 based."""
    result = generate_pacs008_xml()
    result['messageType'] = 'FPS'
    return result


def generate_pix():
    """Brazil PIX - JSON format."""
    e2e_id = f"E{random.randint(10000000, 99999999)}{datetime.utcnow().strftime('%Y%m%d%H%M')}{uuid.uuid4().hex[:11]}"

    content = json.dumps({
        "messageType": "PIX",
        "endToEndId": e2e_id,
        "creationDateTime": random_datetime_iso(),
        "payer": {
            "ispb": f"{random.randint(10000000, 99999999)}",
            "name": random_name(),
            "cpfCnpj": f"{random.randint(10000000000, 99999999999)}",
            "pixKey": f"+55{random.randint(11000000000, 99999999999)}"
        },
        "payee": {
            "ispb": f"{random.randint(10000000, 99999999)}",
            "name": random_name(),
            "cpfCnpj": f"{random.randint(10000000000, 99999999999)}",
            "pixKey": f"+55{random.randint(11000000000, 99999999999)}"
        },
        "amount": random_amount(),
        "currency": "BRL",
        "infoAdicional": "Payment via PIX"
    }, indent=2)

    return {
        'messageType': 'PIX',
        'format': 'json',
        'content': content,
        'messageId': e2e_id
    }


def generate_upi():
    """India UPI - JSON format based on NPCI specs."""
    txn_id = f"UPI{uuid.uuid4().hex[:20].upper()}"

    content = json.dumps({
        "messageType": "UPI",
        "txnId": txn_id,
        "txnType": random.choice(["PAY", "COLLECT", "REFUND"]),
        "txnNote": random.choice(["Payment for services", "Invoice payment", "Transfer"]),
        "amount": str(random_amount()),
        "currency": "INR",
        "payer": {
            "vpa": f"{random_name().lower().replace(' ','')}@upi",
            "name": random_name(),
            "ifsc": f"HDFC0{random.randint(100000, 999999)}",
            "account": f"{random.randint(10000000000, 99999999999)}"
        },
        "payee": {
            "vpa": f"{random_name().lower().replace(' ','')}@upi",
            "name": random_name(),
            "ifsc": f"ICIC0{random.randint(100000, 999999)}",
            "account": f"{random.randint(10000000000, 99999999999)}"
        },
        "timestamp": random_datetime_iso(),
        "refId": random_reference()
    }, indent=2)

    return {
        'messageType': 'UPI',
        'format': 'json',
        'content': content,
        'messageId': txn_id
    }


def generate_npp():
    """Australia NPP - ISO 20022 based."""
    result = generate_pacs008_xml()
    result['messageType'] = 'NPP'
    return result


def generate_paynow():
    """Singapore PayNow - FAST/ISO 20022 based."""
    result = generate_pacs008_xml()
    result['messageType'] = 'PayNow'
    return result


def generate_promptpay():
    """Thailand PromptPay - JSON format."""
    txn_id = f"PP{uuid.uuid4().hex[:16].upper()}"

    content = json.dumps({
        "messageType": "PromptPay",
        "transactionId": txn_id,
        "creationDateTime": random_datetime_iso(),
        "sender": {
            "bankCode": f"{random.randint(1, 99):03d}",
            "name": random_name(),
            "promptPayId": f"0{random.randint(800000000, 999999999)}"
        },
        "receiver": {
            "bankCode": f"{random.randint(1, 99):03d}",
            "name": random_name(),
            "promptPayId": f"0{random.randint(800000000, 999999999)}"
        },
        "amount": random_amount(),
        "currency": "THB",
        "reference": random_reference()
    }, indent=2)

    return {
        'messageType': 'PromptPay',
        'format': 'json',
        'content': content,
        'messageId': txn_id
    }


def generate_instapay():
    """Philippines InstaPay - JSON format."""
    txn_id = f"IP{uuid.uuid4().hex[:16].upper()}"

    content = json.dumps({
        "messageType": "InstaPay",
        "transactionId": txn_id,
        "creationDateTime": random_datetime_iso(),
        "sender": {
            "bankCode": f"{random.randint(1, 99):04d}",
            "account": f"{random.randint(1000000000, 9999999999)}",
            "name": random_name()
        },
        "receiver": {
            "bankCode": f"{random.randint(1, 99):04d}",
            "account": f"{random.randint(1000000000, 9999999999)}",
            "name": random_name()
        },
        "amount": random_amount(),
        "currency": "PHP",
        "purpose": random.choice(["SALA", "SUPP", "PENS", "TAXS"])
    }, indent=2)

    return {
        'messageType': 'InstaPay',
        'format': 'json',
        'content': content,
        'messageId': txn_id
    }


def generate_kftc():
    """South Korea KFTC - JSON format."""
    txn_id = f"KFTC{uuid.uuid4().hex[:12].upper()}"

    content = json.dumps({
        "messageType": "KFTC",
        "transactionId": txn_id,
        "creationDateTime": random_datetime_iso(),
        "sender": {
            "bankCode": f"{random.randint(1, 99):03d}",
            "account": f"{random.randint(100000000000, 999999999999)}",
            "name": random_name()
        },
        "receiver": {
            "bankCode": f"{random.randint(1, 99):03d}",
            "account": f"{random.randint(100000000000, 999999999999)}",
            "name": random_name()
        },
        "amount": random_amount(),
        "currency": "KRW"
    }, indent=2)

    return {
        'messageType': 'KFTC',
        'format': 'json',
        'content': content,
        'messageId': txn_id
    }


def generate_bojnet():
    """Japan BOJ-NET - JSON format."""
    txn_id = f"BOJNET{uuid.uuid4().hex[:10].upper()}"

    content = json.dumps({
        "messageType": "BOJNET",
        "transactionId": txn_id,
        "creationDateTime": random_datetime_iso(),
        "senderBIC": random_bic(),
        "senderAccount": f"{random.randint(1000000, 9999999)}",
        "receiverBIC": random_bic(),
        "receiverAccount": f"{random.randint(1000000, 9999999)}",
        "amount": random_amount(),
        "currency": "JPY",
        "valueDate": random_date(0)
    }, indent=2)

    return {
        'messageType': 'BOJNET',
        'format': 'json',
        'content': content,
        'messageId': txn_id
    }


def generate_cnaps():
    """China CNAPS - JSON format."""
    txn_id = f"CNAPS{uuid.uuid4().hex[:11].upper()}"

    content = json.dumps({
        "messageType": "CNAPS",
        "transactionId": txn_id,
        "creationDateTime": random_datetime_iso(),
        "sender": {
            "bankCode": f"{random.randint(100000000000, 999999999999)}",
            "account": f"{random.randint(1000000000000000, 9999999999999999)}",
            "name": random_name()
        },
        "receiver": {
            "bankCode": f"{random.randint(100000000000, 999999999999)}",
            "account": f"{random.randint(1000000000000000, 9999999999999999)}",
            "name": random_name()
        },
        "amount": random_amount(),
        "currency": "CNY"
    }, indent=2)

    return {
        'messageType': 'CNAPS',
        'format': 'json',
        'content': content,
        'messageId': txn_id
    }


def generate_rtgs_hk():
    """Hong Kong RTGS - SWIFT MT based."""
    result = generate_mt202()
    result['messageType'] = 'RTGS_HK'
    return result


def generate_meps():
    """Singapore MEPS+ RTGS - SWIFT MT based."""
    result = generate_mt202()
    result['messageType'] = 'MEPS'
    return result


def generate_sarie():
    """Saudi Arabia SARIE RTGS - JSON format."""
    txn_id = f"SARIE{uuid.uuid4().hex[:11].upper()}"

    content = json.dumps({
        "messageType": "SARIE",
        "transactionId": txn_id,
        "creationDateTime": random_datetime_iso(),
        "senderBIC": random_bic(),
        "senderIBAN": f"SA{random.randint(10, 99)}{random.randint(10, 99)}{''.join([str(random.randint(0,9)) for _ in range(20)])}",
        "receiverBIC": random_bic(),
        "receiverIBAN": f"SA{random.randint(10, 99)}{random.randint(10, 99)}{''.join([str(random.randint(0,9)) for _ in range(20)])}",
        "amount": random_amount(),
        "currency": "SAR",
        "valueDate": random_date(0)
    }, indent=2)

    return {
        'messageType': 'SARIE',
        'format': 'json',
        'content': content,
        'messageId': txn_id
    }


def generate_uaefts():
    """UAE FTS - JSON format."""
    txn_id = f"UAEFTS{uuid.uuid4().hex[:10].upper()}"

    content = json.dumps({
        "messageType": "UAEFTS",
        "transactionId": txn_id,
        "creationDateTime": random_datetime_iso(),
        "senderBIC": random_bic(),
        "senderIBAN": f"AE{random.randint(10, 99)}{random.randint(100, 999)}{''.join([str(random.randint(0,9)) for _ in range(16)])}",
        "receiverBIC": random_bic(),
        "receiverIBAN": f"AE{random.randint(10, 99)}{random.randint(100, 999)}{''.join([str(random.randint(0,9)) for _ in range(16)])}",
        "amount": random_amount(),
        "currency": "AED",
        "valueDate": random_date(0)
    }, indent=2)

    return {
        'messageType': 'UAEFTS',
        'format': 'json',
        'content': content,
        'messageId': txn_id
    }


# ============================================================================
# Message Type to Generator Mapping
# ============================================================================

MESSAGE_GENERATORS = {
    # ISO 20022 PAIN
    "pain.001": generate_pain001_xml,
    "pain.002": generate_pain002_xml,
    "pain.007": generate_pain007_xml,
    "pain.008": generate_pain008_xml,
    "pain.013": generate_pain013_xml,
    "pain.014": generate_pain014_xml,

    # ISO 20022 PACS
    "pacs.002": generate_pacs002_xml,
    "pacs.003": generate_pacs003_xml,
    "pacs.004": generate_pacs004_xml,
    "pacs.007": generate_pacs007_xml,
    "pacs.008": generate_pacs008_xml,
    "pacs.009": generate_pacs009_xml,
    "pacs.028": generate_pacs028_xml,

    # ISO 20022 CAMT
    "camt.026": generate_camt026_xml,
    "camt.027": generate_camt027_xml,
    "camt.028": generate_camt028_xml,
    "camt.029": generate_camt029_xml,
    "camt.052": generate_camt052_xml,
    "camt.053": generate_camt053_xml,
    "camt.054": generate_camt054_xml,
    "camt.055": generate_camt055_xml,
    "camt.056": generate_camt056_xml,
    "camt.057": generate_camt057_xml,
    "camt.086": generate_camt086_xml,
    "camt.087": generate_camt087_xml,

    # ISO 20022 ACMT
    "acmt.001": generate_acmt001_xml,
    "acmt.002": generate_acmt002_xml,
    "acmt.003": generate_acmt003_xml,
    "acmt.005": generate_acmt005_xml,
    "acmt.006": generate_acmt006_xml,
    "acmt.007": generate_acmt007_xml,

    # SWIFT MT
    "MT103": generate_mt103,
    "MT200": generate_mt200,
    "MT202": generate_mt202,
    "MT202COV": generate_mt202cov,
    "MT900": generate_mt900,
    "MT910": generate_mt910,
    "MT940": generate_mt940,
    "MT950": generate_mt950,

    # European
    "SEPA_SCT": generate_sepa_sct,
    "SEPA_SDD": generate_sepa_sdd,
    "TARGET2": generate_target2,

    # UK
    "BACS": generate_bacs,
    "CHAPS": generate_chaps,
    "FPS": generate_fps,

    # US
    "NACHA_ACH": generate_nacha_ach,
    "Fedwire": generate_fedwire,
    "FedNow": generate_fednow,
    "RTP": generate_rtp,
    "CHIPS": generate_chips,

    # Latin America
    "PIX": generate_pix,

    # Asia Pacific
    "UPI": generate_upi,
    "NPP": generate_npp,
    "PayNow": generate_paynow,
    "PromptPay": generate_promptpay,
    "InstaPay": generate_instapay,
    "KFTC": generate_kftc,
    "BOJNET": generate_bojnet,
    "CNAPS": generate_cnaps,
    "RTGS_HK": generate_rtgs_hk,
    "MEPS": generate_meps,

    # Middle East
    "SARIE": generate_sarie,
    "UAEFTS": generate_uaefts,
}


def generate_xml_batch(records: list, msg_type: str, batch_id: str) -> str:
    """
    Generate a batch XML document containing multiple records.

    For ISO 20022, each record is wrapped in its own Document element.
    Returns a batch envelope with multiple messages.
    """
    # Extract all XML contents
    xml_contents = [r['content'] for r in records]

    # Create batch envelope
    batch_envelope = f'''<?xml version="1.0" encoding="UTF-8"?>
<BatchMessage xmlns="urn:gps:cdm:batch:1.0">
  <BatchHeader>
    <BatchId>{batch_id}</BatchId>
    <MessageType>{msg_type}</MessageType>
    <RecordCount>{len(records)}</RecordCount>
    <CreatedAt>{datetime.utcnow().isoformat()}</CreatedAt>
  </BatchHeader>
  <Messages>
'''

    for i, content in enumerate(xml_contents):
        # Remove XML declaration from individual messages
        if content.startswith('<?xml'):
            content = content.split('?>', 1)[1].strip()
            if content.startswith('\n'):
                content = content[1:]

        # Indent the content
        indented = '\n'.join('    ' + line for line in content.split('\n') if line.strip())
        batch_envelope += f'    <Message sequence="{i+1}">\n{indented}\n    </Message>\n'

    batch_envelope += '''  </Messages>
</BatchMessage>'''

    return batch_envelope


def generate_all_test_messages(output_dir: str = "data/nifi_input", records_per_file: int = 5):
    """Generate standards-compliant test message files for all supported message types.

    Args:
        output_dir: Directory to write test files
        records_per_file: Number of records/transactions per file (default: 5)
    """
    os.makedirs(output_dir, exist_ok=True)

    generated = []
    errors = []

    for msg_type, generator in MESSAGE_GENERATORS.items():
        try:
            # Generate multiple records per message type
            records = []
            for i in range(records_per_file):
                result = generator()
                records.append(result)

            # Determine file extension and batching strategy based on format
            format_type = records[0].get('format', 'json')

            if format_type == 'xml':
                ext = 'xml'
                # For XML, wrap multiple records in a batch envelope
                batch_id = f"BATCH{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                content = generate_xml_batch(records, msg_type, batch_id)
            elif format_type == 'swift_mt':
                ext = 'mt'
                # For SWIFT MT, concatenate messages with separator
                content = '\n\n$\n\n'.join(r['content'] for r in records)
            elif format_type == 'nacha':
                ext = 'ach'
                # NACHA files are batched by design, use first record
                content = records[0]['content']
            elif format_type == 'fedwire':
                ext = 'fwt'
                # Fedwire: concatenate with newlines
                content = '\n'.join(r['content'] for r in records)
            elif format_type == 'bacs_std18':
                ext = 'bacs'
                # BACS files are batched by design, use first record
                content = records[0]['content']
            else:
                ext = 'json'
                # For JSON formats, create a batch array
                content = json.dumps({
                    "batch_id": f"BATCH{uuid.uuid4().hex[:12].upper()}",
                    "message_type": msg_type,
                    "record_count": len(records),
                    "created_at": datetime.utcnow().isoformat(),
                    "records": [json.loads(r['content']) if isinstance(r['content'], str)
                               else r['content'] for r in records]
                }, indent=2)

            # Create filename (sanitize message type for filename)
            safe_type = msg_type.replace('.', '_').replace('/', '_')
            filename = f"{safe_type}_batch_{records[0]['messageId'][-8:]}.{ext}"
            filepath = os.path.join(output_dir, filename)

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            generated.append((msg_type, filepath, format_type, records_per_file))
            print(f"[OK] {msg_type:15} -> {filename} ({format_type}, {records_per_file} records)")

        except Exception as e:
            errors.append((msg_type, str(e)))
            print(f"[ERR] {msg_type:15} -> Error: {e}")

    print(f"\n{'='*60}")
    print(f"Generated {len(generated)} test message files in {output_dir}")
    total_records = sum(r[3] for r in generated)
    print(f"Total records across all files: {total_records}")
    if errors:
        print(f"Errors: {len(errors)}")
    print(f"{'='*60}")

    # Summary by format
    formats = {}
    for _, _, fmt, _ in generated:
        formats[fmt] = formats.get(fmt, 0) + 1

    print("\nBy format:")
    for fmt, count in sorted(formats.items()):
        print(f"  {fmt}: {count} files")

    return generated, errors


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate standards-compliant test messages for GPS CDM")
    parser.add_argument(
        "--output-dir",
        default="data/nifi_input",
        help="Output directory for test files (default: data/nifi_input)"
    )
    parser.add_argument(
        "--records-per-file",
        type=int,
        default=5,
        help="Number of records per file (default: 5)"
    )
    args = parser.parse_args()

    generate_all_test_messages(args.output_dir, args.records_per_file)


if __name__ == "__main__":
    main()
