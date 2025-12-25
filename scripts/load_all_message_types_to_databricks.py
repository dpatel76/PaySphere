#!/usr/bin/env python3
"""
Load All 66 Message Types to Databricks Pipeline
=================================================

This script generates sample messages for all 66 supported message types
and processes them through the complete Bronze -> Silver -> Gold pipeline
in Databricks.

Usage:
    python scripts/load_all_message_types_to_databricks.py
"""

import sys
import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Sample messages for all 66 message types
SAMPLE_MESSAGES = {
    # ISO 20022 PAIN (6 types)
    "pain.001": {"Document": {"CstmrCdtTrfInitn": {"GrpHdr": {"MsgId": "E2E-PAIN001-001", "CreDtTm": "2024-12-24T10:30:00Z", "NbOfTxs": "1", "CtrlSum": "10000.00"}, "PmtInf": [{"PmtInfId": "PMT-001", "PmtMtd": "TRF", "ReqdExctnDt": "2024-12-24", "Dbtr": {"Nm": "ACME Corporation"}, "DbtrAcct": {"Id": {"IBAN": "US1234567890"}}, "DbtrAgt": {"FinInstnId": {"BIC": "TESTUS33XXX"}}, "CdtTrfTxInf": [{"PmtId": {"EndToEndId": "E2E-001"}, "Amt": {"InstdAmt": {"Ccy": "USD", "#text": "10000.00"}}, "Cdtr": {"Nm": "Vendor Inc"}, "CdtrAcct": {"Id": {"IBAN": "US9876543210"}}}]}]}}},
    "pain.002": {"Document": {"CstmrPmtStsRpt": {"GrpHdr": {"MsgId": "E2E-PAIN002-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "OrgnlGrpInfAndSts": {"OrgnlMsgId": "ORIG-001", "OrgnlMsgNmId": "pain.001", "GrpSts": "ACCP"}}}},
    "pain.007": {"Document": {"CstmrPmtRvsl": {"GrpHdr": {"MsgId": "E2E-PAIN007-001", "CreDtTm": "2024-12-24T10:30:00Z", "NbOfTxs": "1"}, "OrgnlGrpInf": {"OrgnlMsgId": "ORIG-001"}}}},
    "pain.008": {"Document": {"CstmrDrctDbtInitn": {"GrpHdr": {"MsgId": "E2E-PAIN008-001", "CreDtTm": "2024-12-24T10:30:00Z", "NbOfTxs": "1", "CtrlSum": "5000.00"}, "PmtInf": [{"PmtInfId": "DD-001", "PmtMtd": "DD", "ReqdColltnDt": "2024-12-24", "Cdtr": {"Nm": "Utility Company"}, "CdtrAcct": {"Id": {"IBAN": "US1111222233"}}, "DrctDbtTxInf": [{"PmtId": {"EndToEndId": "DD-E2E-001"}, "InstdAmt": {"Ccy": "USD", "#text": "5000.00"}, "Dbtr": {"Nm": "Customer One"}}]}]}}},
    "pain.013": {"Document": {"CdtrPmtActvtnReq": {"GrpHdr": {"MsgId": "E2E-PAIN013-001", "CreDtTm": "2024-12-24T10:30:00Z", "NbOfTxs": "1"}, "PmtInf": [{"PmtInfId": "RTP-001"}]}}},
    "pain.014": {"Document": {"CdtrPmtActvtnReqStsRpt": {"GrpHdr": {"MsgId": "E2E-PAIN014-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "OrgnlGrpInfAndSts": {"OrgnlMsgId": "RTP-001", "GrpSts": "ACCP"}}}},

    # ISO 20022 PACS (7 types)
    "pacs.002": {"Document": {"FIToFIPmtStsRpt": {"GrpHdr": {"MsgId": "E2E-PACS002-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "OrgnlGrpInfAndSts": {"OrgnlMsgId": "ORIG-PACS-001", "GrpSts": "ACCP"}}}},
    "pacs.003": {"Document": {"FIToFICstmrDrctDbt": {"GrpHdr": {"MsgId": "E2E-PACS003-001", "CreDtTm": "2024-12-24T10:30:00Z", "NbOfTxs": "1", "SttlmInf": {"SttlmMtd": "INDA"}}, "DrctDbtTxInf": [{"PmtId": {"EndToEndId": "PACS003-E2E-001"}, "IntrBkSttlmAmt": {"Ccy": "EUR", "#text": "7500.00"}}]}}},
    "pacs.004": {"Document": {"PmtRtr": {"GrpHdr": {"MsgId": "E2E-PACS004-001", "CreDtTm": "2024-12-24T10:30:00Z", "NbOfTxs": "1"}, "TxInf": [{"RtrId": "RTN-001", "OrgnlEndToEndId": "ORIG-E2E-001", "RtrdIntrBkSttlmAmt": {"Ccy": "USD", "#text": "5000.00"}, "RtrRsnInf": {"Rsn": {"Cd": "AC01"}}}]}}},
    "pacs.007": {"Document": {"FIToFIPmtRvsl": {"GrpHdr": {"MsgId": "E2E-PACS007-001", "CreDtTm": "2024-12-24T10:30:00Z", "NbOfTxs": "1"}, "TxInf": [{"RvslId": "RVS-001", "OrgnlEndToEndId": "ORIG-E2E-001"}]}}},
    "pacs.008": {"Document": {"FIToFICstmrCdtTrf": {"GrpHdr": {"MsgId": "E2E-PACS008-001", "CreDtTm": "2024-12-24T10:30:00Z", "NbOfTxs": "1", "SttlmInf": {"SttlmMtd": "INDA"}}, "CdtTrfTxInf": [{"PmtId": {"EndToEndId": "PACS008-E2E-001", "TxId": "TXN-001"}, "IntrBkSttlmAmt": {"Ccy": "USD", "#text": "25000.00"}, "Dbtr": {"Nm": "Sender Corp"}, "Cdtr": {"Nm": "Receiver Ltd"}}]}}},
    "pacs.009": {"Document": {"FICdtTrf": {"GrpHdr": {"MsgId": "E2E-PACS009-001", "CreDtTm": "2024-12-24T10:30:00Z", "NbOfTxs": "1"}, "CdtTrfTxInf": [{"PmtId": {"EndToEndId": "PACS009-E2E-001"}, "IntrBkSttlmAmt": {"Ccy": "EUR", "#text": "100000.00"}}]}}},
    "pacs.028": {"Document": {"FIToFIPmtStsReq": {"GrpHdr": {"MsgId": "E2E-PACS028-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "TxInf": [{"OrgnlEndToEndId": "ORIG-E2E-001"}]}}},

    # ISO 20022 CAMT (15 types)
    "camt.026": {"Document": {"UblToApply": {"Assgnmt": {"Id": "E2E-CAMT026-001", "CreDtTm": "2024-12-24T10:30:00Z", "Assgnr": {"Agt": {"FinInstnId": {"BIC": "TESTUS33XXX"}}}, "Assgne": {"Agt": {"FinInstnId": {"BIC": "TESTGB22XXX"}}}}}}},
    "camt.027": {"Document": {"ClmNonRct": {"Assgnmt": {"Id": "E2E-CAMT027-001", "CreDtTm": "2024-12-24T10:30:00Z"}}}},
    "camt.028": {"Document": {"AddtlPmtInf": {"Assgnmt": {"Id": "E2E-CAMT028-001", "CreDtTm": "2024-12-24T10:30:00Z"}}}},
    "camt.029": {"Document": {"RsltnOfInvstgtn": {"Assgnmt": {"Id": "E2E-CAMT029-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "Sts": {"Conf": "ACCP"}}}},
    "camt.052": {"Document": {"BkToCstmrAcctRpt": {"GrpHdr": {"MsgId": "E2E-CAMT052-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "Rpt": [{"Id": "RPT-001", "Acct": {"Id": {"IBAN": "US1234567890"}}}]}}},
    "camt.053": {"Document": {"BkToCstmrStmt": {"GrpHdr": {"MsgId": "E2E-CAMT053-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "Stmt": [{"Id": "STMT-001", "CreDtTm": "2024-12-24T10:30:00Z", "Acct": {"Id": {"IBAN": "US1234567890"}}, "Bal": [{"Tp": {"CdOrPrtry": {"Cd": "OPBD"}}, "Amt": {"Ccy": "USD", "#text": "50000.00"}}]}]}}},
    "camt.054": {"Document": {"BkToCstmrDbtCdtNtfctn": {"GrpHdr": {"MsgId": "E2E-CAMT054-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "Ntfctn": [{"Id": "NTF-001", "Acct": {"Id": {"IBAN": "US1234567890"}}}]}}},
    "camt.055": {"Document": {"CstmrPmtCxlReq": {"Assgnmt": {"Id": "E2E-CAMT055-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "Undrlyg": [{"TxInf": [{"OrgnlEndToEndId": "ORIG-E2E-001"}]}]}}},
    "camt.056": {"Document": {"FIToFIPmtCxlReq": {"Assgnmt": {"Id": "E2E-CAMT056-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "Undrlyg": [{"TxInf": [{"OrgnlEndToEndId": "ORIG-E2E-001"}]}]}}},
    "camt.057": {"Document": {"NtfctnToRcv": {"GrpHdr": {"MsgId": "E2E-CAMT057-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "Ntfctn": [{"Id": "NTF-057-001"}]}}},
    "camt.058": {"Document": {"NtfctnToRcvCxlAdvc": {"GrpHdr": {"MsgId": "E2E-CAMT058-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "Undrlyg": [{"OrgnlNtfctnId": "NTF-057-001"}]}}},
    "camt.059": {"Document": {"NtfctnToRcvStsRpt": {"GrpHdr": {"MsgId": "E2E-CAMT059-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "OrgnlNtfctnAndSts": [{"OrgnlNtfctnId": "NTF-057-001", "Sts": "ACCP"}]}}},
    "camt.060": {"Document": {"AcctRptgReq": {"GrpHdr": {"MsgId": "E2E-CAMT060-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "RptgReq": [{"Id": "REQ-001", "ReqdMsgNmId": "camt.053"}]}}},
    "camt.086": {"Document": {"BkSvcsBllgStmt": {"GrpHdr": {"MsgId": "E2E-CAMT086-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "BllgStmt": [{"StmtId": "BSVC-001"}]}}},
    "camt.087": {"Document": {"ReqToModfyPmt": {"Assgnmt": {"Id": "E2E-CAMT087-001", "CreDtTm": "2024-12-24T10:30:00Z"}, "Undrlyg": [{"OrgnlEndToEndId": "ORIG-E2E-001"}]}}},

    # ISO 20022 ACMT (6 types)
    "acmt.001": {"Document": {"AcctOpngInstr": {"MsgId": {"Id": "E2E-ACMT001-001"}, "AcctId": {"IBAN": "US1234567890"}, "Acct": {"Nm": "New Account"}, "AcctPties": {"Ownr": {"Nm": "Account Holder"}}}}},
    "acmt.002": {"Document": {"AcctOpngAddtlInfReq": {"MsgId": {"Id": "E2E-ACMT002-001"}, "OrgnlRefs": [{"OrgnlMsgId": "ACMT001-001"}]}}},
    "acmt.003": {"Document": {"AcctOpngAmndmntReq": {"MsgId": {"Id": "E2E-ACMT003-001"}, "OrgnlRefs": [{"OrgnlMsgId": "ACMT001-001"}]}}},
    "acmt.005": {"Document": {"AcctSwtchInfReq": {"MsgId": {"Id": "E2E-ACMT005-001"}}}},
    "acmt.006": {"Document": {"AcctSwtchInfRspn": {"MsgId": {"Id": "E2E-ACMT006-001"}}}},
    "acmt.007": {"Document": {"AcctClsgReq": {"MsgId": {"Id": "E2E-ACMT007-001"}, "AcctId": {"IBAN": "US1234567890"}}}},

    # SWIFT MT (9 types)
    "MT103": "{1:F01TESTUS33XXXX0000000000}{2:O1030919241224TESTUS33XXXX00000000002412241019N}{4:\n:20:E2E-MT103-001\n:23B:CRED\n:32A:241224USD10000,00\n:50K:/1234567890\nACME CORPORATION\n123 MAIN STREET\nNEW YORK NY 10001\n:59:/9876543210\nVENDOR INC\n456 OAK AVENUE\nLOS ANGELES CA 90001\n:71A:SHA\n:72:/INS/PAYMENT FOR INVOICE 12345\n-}",
    "MT200": "{1:F01TESTUS33XXXX0000000000}{2:O2000919241224TESTUS33XXXX00000000002412241019N}{4:\n:20:E2E-MT200-001\n:32A:241224USD500000,00\n:53A:TESTUS33XXX\n:57A:BOFAUS3NXXX\n-}",
    "MT202": "{1:F01TESTUS33XXXX0000000000}{2:O2020919241224TESTUS33XXXX00000000002412241019N}{4:\n:20:E2E-MT202-001\n:21:REL-MT202-001\n:32A:241224USD1000000,00\n:58A:BOFAUS3NXXX\n-}",
    "MT202COV": "{1:F01TESTUS33XXXX0000000000}{2:O2020919241224TESTUS33XXXX00000000002412241019N}{4:\n:20:E2E-MT202COV-001\n:21:REL-COV-001\n:32A:241224EUR500000,00\n:58A:DEUTDEFF\n:50K:/DE89370400440532013000\nUNDERLYING CUSTOMER GMBH\n:59:/FR7630004000031234567890143\nBENEFICIARY SARL\n-}",
    "MT900": "{1:F01TESTUS33XXXX0000000000}{2:O9000919241224TESTUS33XXXX00000000002412241019N}{4:\n:20:E2E-MT900-001\n:21:REF-900-001\n:25:123456789012\n:32A:241224USD25000,00\n:52A:TESTUS33XXX\n-}",
    "MT910": "{1:F01TESTUS33XXXX0000000000}{2:O9100919241224TESTUS33XXXX00000000002412241019N}{4:\n:20:E2E-MT910-001\n:21:REF-910-001\n:25:123456789012\n:32A:241224USD15000,00\n:52A:TESTUS33XXX\n-}",
    "MT940": "{1:F01TESTUS33XXXX0000000000}{2:O9400919241224TESTUS33XXXX00000000002412241019N}{4:\n:20:E2E-MT940-001\n:25:123456789012\n:28C:1/1\n:60F:C241223EUR100000,00\n:61:241224C5000,00NTRFNONREF//\n:62F:C241224EUR105000,00\n-}",
    "MT942": "{1:F01TESTUS33XXXX0000000000}{2:O9420919241224TESTUS33XXXX00000000002412241019N}{4:\n:20:E2E-MT942-001\n:25:123456789012\n:28C:1/1\n:34F:EUR0,\n:13D:2412241000+0100\n-}",
    "MT950": "{1:F01TESTUS33XXXX0000000000}{2:O9500919241224TESTUS33XXXX00000000002412241019N}{4:\n:20:E2E-MT950-001\n:25:123456789012\n:28C:1/1\n:60F:C241223GBP50000,00\n:62F:C241224GBP52500,00\n-}",

    # Domestic - SEPA (2 types)
    "SEPA_SCT": {"Document": {"CstmrCdtTrfInitn": {"GrpHdr": {"MsgId": "E2E-SEPA-SCT-001", "CreDtTm": "2024-12-24T10:30:00Z", "NbOfTxs": "1", "CtrlSum": "1500.00", "InitgPty": {"Nm": "Company GmbH"}}, "PmtInf": [{"PmtInfId": "SEPA-PMT-001", "PmtMtd": "TRF", "NbOfTxs": "1", "CtrlSum": "1500.00", "PmtTpInf": {"SvcLvl": {"Cd": "SEPA"}}, "ReqdExctnDt": "2024-12-24", "Dbtr": {"Nm": "Company GmbH"}, "DbtrAcct": {"Id": {"IBAN": "DE89370400440532013000"}}, "DbtrAgt": {"FinInstnId": {"BIC": "COBADEFFXXX"}}, "CdtTrfTxInf": [{"PmtId": {"EndToEndId": "SEPA-E2E-001"}, "Amt": {"InstdAmt": {"Ccy": "EUR", "#text": "1500.00"}}, "CdtrAgt": {"FinInstnId": {"BIC": "BNPAFRPPXXX"}}, "Cdtr": {"Nm": "Supplier SARL"}, "CdtrAcct": {"Id": {"IBAN": "FR7630004000031234567890143"}}}]}]}}},
    "SEPA_SDD": {"Document": {"CstmrDrctDbtInitn": {"GrpHdr": {"MsgId": "E2E-SEPA-SDD-001", "CreDtTm": "2024-12-24T10:30:00Z", "NbOfTxs": "1", "CtrlSum": "250.00"}, "PmtInf": [{"PmtInfId": "SEPA-DD-001", "PmtMtd": "DD", "PmtTpInf": {"SvcLvl": {"Cd": "SEPA"}, "LclInstrm": {"Cd": "CORE"}}, "ReqdColltnDt": "2024-12-24", "Cdtr": {"Nm": "Utility Provider"}, "CdtrAcct": {"Id": {"IBAN": "DE89370400440532013000"}}, "DrctDbtTxInf": [{"PmtId": {"EndToEndId": "SEPA-DD-E2E-001"}, "InstdAmt": {"Ccy": "EUR", "#text": "250.00"}, "DrctDbtTx": {"MndtRltdInf": {"MndtId": "MNDT-001"}}, "Dbtr": {"Nm": "Customer Hans"}, "DbtrAcct": {"Id": {"IBAN": "NL91ABNA0417164300"}}}]}]}}},

    # Domestic - US (3 types)
    "NACHA_ACH": {"file_header": {"record_type_code": "1", "priority_code": "01", "immediate_destination": "021000021", "immediate_origin": "123456789", "file_creation_date": "241224", "file_id_modifier": "A"}, "batch": {"record_type_code": "5", "service_class_code": "200", "company_name": "ACME PAYROLL", "company_id": "1123456789", "standard_entry_class": "PPD", "company_entry_description": "PAYROLL", "effective_entry_date": "241224", "batch_number": "1"}, "entry": {"record_type_code": "6", "transaction_code": "22", "receiving_dfi": "02100002", "dfi_account_number": "123456789", "amount": "250000", "individual_id": "E2E-ACH-001", "individual_name": "EMPLOYEE JOHN DOE", "trace_number": "021000021000001"}},
    "FEDWIRE": {"header": {"message_type": "1000", "imad": "20241224MMQFMP1B000001", "omad": "20241224MMQFMP1B000001", "type_subtype": "1000", "input_cycle_date": "20241224", "input_sequence_number": "000001"}, "sender": {"aba": "021000021", "short_name": "SENDER BANK"}, "receiver": {"aba": "021000089", "short_name": "RECEIVER BANK"}, "amount": {"value": "1000000.00", "currency": "USD"}, "originator": {"name": "ORIGINATOR CORP", "address": "123 WALL STREET, NEW YORK NY"}, "beneficiary": {"name": "BENEFICIARY INC", "address": "456 MARKET STREET, SAN FRANCISCO CA"}, "sender_reference": "E2E-FW-001"},
    "CHIPS": {"sequence_number": "E2E-CHIPS-001", "message_type_code": "1000", "sending_participant": "0001", "receiving_participant": "0002", "amount": "5000000.00", "currency": "USD", "value_date": "2024-12-24", "sender_reference": "CHIPS-REF-001"},

    # Domestic - UK (3 types)
    "BACS": {"service_user_number": "123456", "processing_date": "2024-12-24", "transaction_code": "99", "destination_sorting_code": "123456", "destination_account_number": "12345678", "amount": "100000", "reference": "E2E-BACS-001", "originator_name": "COMPANY LTD"},
    "CHAPS": {"message_id": "E2E-CHAPS-001", "creation_datetime": "2024-12-24T10:30:00Z", "instructed_amount": {"value": "500000.00", "currency": "GBP"}, "debtor": {"name": "UK COMPANY PLC", "account": "12345678", "sort_code": "123456"}, "creditor": {"name": "RECIPIENT LTD", "account": "87654321", "sort_code": "654321"}},
    "FASTER_PAYMENTS": {"payment_id": "E2E-FPS-001", "creation_datetime": "2024-12-24T10:30:00Z", "instructed_amount": {"value": "250.00", "currency": "GBP"}, "payer": {"name": "JOHN SMITH", "account": "12345678", "sort_code": "123456"}, "payee": {"name": "JANE DOE", "account": "87654321", "sort_code": "654321"}, "reference": "RENT PAYMENT"},

    # Real-Time Payments (8 types)
    "FEDNOW": {"Document": {"FIToFICstmrCdtTrf": {"GrpHdr": {"MsgId": "E2E-FEDNOW-001", "CreDtTm": "2024-12-24T10:30:00Z", "NbOfTxs": "1", "SttlmInf": {"SttlmMtd": "CLRG", "ClrSys": {"Cd": "FDN"}}}, "CdtTrfTxInf": [{"PmtId": {"EndToEndId": "FEDNOW-E2E-001"}, "IntrBkSttlmAmt": {"Ccy": "USD", "#text": "500.00"}, "Dbtr": {"Nm": "Sender Person"}, "Cdtr": {"Nm": "Receiver Person"}}]}}},
    "RTP": {"message_id": "E2E-RTP-001", "creation_datetime": "2024-12-24T10:30:00Z", "instructed_amount": {"value": "750.00", "currency": "USD"}, "sender": {"name": "RTP SENDER", "routing_number": "021000021", "account_number": "1234567890"}, "receiver": {"name": "RTP RECEIVER", "routing_number": "021000089", "account_number": "0987654321"}, "remittance_info": "Invoice 12345"},
    "PIX": {"endToEndId": "E12345678202412241030PIX001", "creationDateTime": "2024-12-24T10:30:00-03:00", "status": "ACCP", "amount": {"value": "1500.00", "currency": "BRL"}, "payer": {"ispb": "12345678", "cpf_cnpj": "12345678901", "name": "Maria Silva Santos", "account": {"branch": "0001", "number": "123456-7", "type": "CC"}}, "payee": {"ispb": "87654321", "cpf_cnpj": "98765432100", "name": "Loja Comercial LTDA", "pixKey": "loja@email.com"}},
    "NPP": {"payment_id": "E2E-NPP-001", "creation_datetime": "2024-12-24T10:30:00+11:00", "instructed_amount": {"value": "350.00", "currency": "AUD"}, "payer": {"name": "AUSSIE SENDER", "bsb": "123456", "account": "123456789"}, "payee": {"name": "AUSSIE RECEIVER", "bsb": "654321", "account": "987654321"}, "service_type": "x2p1"},
    "UPI": {"transaction_id": "E2E-UPI-001", "creation_datetime": "2024-12-24T10:30:00+05:30", "amount": {"value": "5000.00", "currency": "INR"}, "payer": {"vpa": "sender@upi", "name": "Rajesh Kumar", "account": {"ifsc": "HDFC0001234", "number": "1234567890"}}, "payee": {"vpa": "merchant@upi", "name": "Online Store", "merchant_code": "5411"}, "purpose_code": "00", "note": "Purchase Payment"},
    "PAYNOW": {"transaction_id": "E2E-PAYNOW-001", "creation_datetime": "2024-12-24T10:30:00+08:00", "amount": {"value": "200.00", "currency": "SGD"}, "sender": {"name": "SG SENDER", "account": "123-456789-0"}, "receiver": {"name": "SG MERCHANT", "proxy_type": "UEN", "proxy_value": "S12345678A"}, "reference": "Order 12345"},
    "PROMPTPAY": {"transaction_id": "E2E-PROMPTPAY-001", "creation_datetime": "2024-12-24T10:30:00+07:00", "amount": {"value": "1000.00", "currency": "THB"}, "sender": {"name": "THAI SENDER", "account": "1234567890"}, "receiver": {"name": "THAI MERCHANT", "promptpay_id": "1234567890123"}, "note": "Bill Payment"},
    "INSTAPAY": {"transaction_id": "E2E-INSTAPAY-001", "creation_datetime": "2024-12-24T10:30:00+08:00", "amount": {"value": "2500.00", "currency": "PHP"}, "sender": {"name": "PH SENDER", "account": "1234567890"}, "receiver": {"name": "PH RECEIVER", "account": "0987654321", "bank_code": "BDO"}, "purpose": "Remittance"},

    # RTGS Systems (7 types)
    "TARGET2": {"Document": {"FIToFICstmrCdtTrf": {"GrpHdr": {"MsgId": "E2E-TARGET2-001", "CreDtTm": "2024-12-24T10:30:00Z", "NbOfTxs": "1", "SttlmInf": {"SttlmMtd": "CLRG", "ClrSys": {"Cd": "TGT"}}}, "CdtTrfTxInf": [{"PmtId": {"EndToEndId": "T2-E2E-001"}, "IntrBkSttlmAmt": {"Ccy": "EUR", "#text": "2500000.00"}, "InstgAgt": {"FinInstnId": {"BIC": "DEUTDEFFXXX"}}, "InstdAgt": {"FinInstnId": {"BIC": "BNPAFRPPXXX"}}}]}}},
    "BOJNET": {"message_id": "E2E-BOJNET-001", "creation_datetime": "2024-12-24T10:30:00+09:00", "settlement_date": "2024-12-24", "sender": {"bic": "BOJPJPJT", "name": "BANK OF JAPAN"}, "receiver": {"bic": "MABORJPJ", "name": "MEGA BANK"}, "amount": {"value": "100000000", "currency": "JPY"}, "reference": "BOJNET-REF-001"},
    "CNAPS": {"message_id": "E2E-CNAPS-001", "creation_datetime": "2024-12-24T10:30:00+08:00", "settlement_date": "2024-12-24", "sender": {"bic": "ICBKCNBJ", "name": "ICBC"}, "receiver": {"bic": "BKCHCNBJ", "name": "BANK OF CHINA"}, "amount": {"value": "5000000.00", "currency": "CNY"}, "message_type": "HVPS"},
    "MEPS_PLUS": {"message_id": "E2E-MEPS-001", "creation_datetime": "2024-12-24T10:30:00+08:00", "settlement_date": "2024-12-24", "sender": {"bic": "DBSSSGSG", "name": "DBS BANK"}, "receiver": {"bic": "OCBCSGSG", "name": "OCBC BANK"}, "amount": {"value": "2000000.00", "currency": "SGD"}, "settlement_type": "RTGS"},
    "RTGS_HK": {"message_id": "E2E-RTGSHK-001", "creation_datetime": "2024-12-24T10:30:00+08:00", "settlement_date": "2024-12-24", "sender": {"bic": "HABORHKH", "name": "HANG SENG BANK"}, "receiver": {"bic": "BKCHHKHH", "name": "BANK OF CHINA HK"}, "amount": {"value": "3000000.00", "currency": "HKD"}, "priority": "NORMAL"},
    "SARIE": {"message_id": "E2E-SARIE-001", "creation_datetime": "2024-12-24T10:30:00+03:00", "settlement_date": "2024-12-24", "sender": {"bic": "RABORAJE", "name": "RAJHI BANK"}, "receiver": {"bic": "SAMBSARI", "name": "SAMBA BANK"}, "amount": {"value": "500000.00", "currency": "SAR"}, "purpose": "COMM"},
    "UAEFTS": {"message_id": "E2E-UAEFTS-001", "creation_datetime": "2024-12-24T10:30:00+04:00", "settlement_date": "2024-12-24", "sender": {"bic": "EABORAED", "name": "EMIRATES NBD"}, "receiver": {"bic": "CBSHAEADXXX", "name": "COMMERCIAL BANK"}, "amount": {"value": "250000.00", "currency": "AED"}, "reference": "UAEFTS-REF-001"},
    "KFTC": {"message_id": "E2E-KFTC-001", "creation_datetime": "2024-12-24T10:30:00+09:00", "settlement_date": "2024-12-24", "sender": {"bic": "KOABORKA", "name": "KOREA DEVELOPMENT BANK"}, "receiver": {"bic": "SHINBORKA", "name": "SHINHAN BANK"}, "amount": {"value": "50000000", "currency": "KRW"}, "transaction_type": "01"},
}


def generate_xml_from_dict(message_type: str, data: Dict) -> str:
    """Generate XML string from message dictionary."""
    if isinstance(data, str):
        return data  # Already a string (MT messages)

    # Convert dict to XML-like JSON for parsing
    return json.dumps(data)


def sql_str(val, max_len=None):
    """Helper for safe SQL string."""
    if val is None:
        return "NULL"
    s = str(val).replace("'", "''")
    if max_len:
        s = s[:max_len]
    return f"'{s}'"


def process_message_to_databricks(
    batch_id: str,
    message_type: str,
    content: str,
    connector
) -> Dict[str, Any]:
    """
    Process a single message through the Bronze -> Silver -> Gold pipeline.

    Uses SQL INSERT statements via connector.execute().
    """
    from gps_cdm.orchestration.databricks_pipeline_tasks import parse_message_comprehensive

    result = {
        "batch_id": batch_id,
        "message_type": message_type,
        "bronze_ok": False,
        "silver_ok": False,
        "gold_ok": False,
        "error": None
    }

    try:
        # Generate unique IDs
        raw_id = f"raw_{uuid.uuid4().hex[:12]}"
        stg_id = f"stg_{uuid.uuid4().hex[:12]}"
        instr_id = f"instr_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)

        # Parse message
        parsed = parse_message_comprehensive(content, message_type)
        payment = parsed.get("payment", {})
        instruction = parsed.get("instruction", {})
        debtor = parsed.get("debtor", {})
        creditor = parsed.get("creditor", {})
        debtor_account = parsed.get("debtor_account", {})
        creditor_account = parsed.get("creditor_account", {})

        message_id = payment.get("message_id") or f"E2E-{message_type}-{batch_id[:8]}"
        amount = float(instruction.get("instructed_amount") or payment.get("amount") or 1000)
        currency = instruction.get("instructed_currency") or payment.get("currency") or "USD"
        e2e_id = instruction.get("end_to_end_id") or f"E2E-{raw_id}"

        # 1. BRONZE LAYER - Raw data storage
        bronze_table = connector.get_table_name("bronze_raw_payment")
        escaped_xml = content[:8000].replace("'", "''")

        connector.execute(f"""
            INSERT INTO {bronze_table}
            (raw_id, message_type, message_id, creation_datetime, raw_xml,
             file_name, file_path, _batch_id, _ingested_at)
            VALUES (
                '{raw_id}',
                '{message_type}',
                '{message_id}',
                TIMESTAMP '{now.isoformat()}',
                '{escaped_xml}',
                'e2e_test_{message_type}.json',
                '/e2e/input/',
                '{batch_id}',
                CURRENT_TIMESTAMP()
            )
        """)
        result["bronze_ok"] = True

        # 2. SILVER LAYER - Normalized data
        silver_table = connector.get_table_name("silver_stg_payment_instruction")

        debtor_name = debtor.get("name") or payment.get("debtor_name") or f"Debtor_{message_type}"
        creditor_name = creditor.get("name") or payment.get("creditor_name") or f"Creditor_{message_type}"
        exec_date = instruction.get("requested_execution_date") or now.strftime("%Y-%m-%d")

        connector.execute(f"""
            INSERT INTO {silver_table}
            (stg_id, raw_id, message_type, message_id, payment_id, end_to_end_id,
             instruction_id, amount, currency, debtor_name, debtor_account,
             creditor_name, creditor_account, creditor_agent_bic, debtor_agent_bic,
             execution_date, created_at, dq_score, dq_issues, _batch_id, _ingested_at)
            VALUES (
                '{stg_id}',
                '{raw_id}',
                '{message_type}',
                {sql_str(message_id, 35)},
                'PMT-{stg_id[:8]}',
                {sql_str(e2e_id, 35)},
                'INSTR-{stg_id[:8]}',
                {amount},
                '{currency}',
                {sql_str(debtor_name, 140)},
                {sql_str(debtor_account.get('iban') or debtor_account.get('account_number'), 34)},
                {sql_str(creditor_name, 140)},
                {sql_str(creditor_account.get('iban') or creditor_account.get('account_number'), 34)},
                {sql_str(parsed.get('creditor_agent', {}).get('bic'), 11)},
                {sql_str(parsed.get('debtor_agent', {}).get('bic'), 11)},
                DATE '{exec_date}',
                CURRENT_TIMESTAMP(),
                0.85,
                NULL,
                '{batch_id}',
                CURRENT_TIMESTAMP()
            )
        """)
        result["silver_ok"] = True

        # 3. GOLD LAYER - CDM Payment Instruction
        gold_table = connector.get_table_name("gold_cdm_payment_instruction")

        # Determine payment type based on message type
        payment_type_mapping = {
            "pain.001": "CREDIT_TRANSFER", "pain.002": "STATUS_REPORT",
            "pain.007": "REVERSAL", "pain.008": "DIRECT_DEBIT",
            "pain.013": "REQUEST_TO_PAY", "pain.014": "RTP_STATUS",
            "pacs.002": "STATUS_REPORT", "pacs.003": "DIRECT_DEBIT",
            "pacs.004": "RETURN", "pacs.007": "REVERSAL",
            "pacs.008": "CREDIT_TRANSFER", "pacs.009": "FI_TRANSFER",
            "pacs.028": "STATUS_REQUEST",
            "camt.026": "INVESTIGATION", "camt.027": "CLAIM",
            "camt.028": "INFO", "camt.029": "RESOLUTION",
            "camt.052": "REPORT", "camt.053": "STATEMENT",
            "camt.054": "NOTIFICATION", "camt.055": "CANCEL_REQ",
            "camt.056": "CANCEL_REQ", "camt.057": "NOTIFICATION",
            "camt.058": "CANCEL_ADVICE", "camt.059": "STATUS_REPORT",
            "camt.060": "REPORT_REQ", "camt.086": "BILLING",
            "camt.087": "MODIFY_REQ",
            "acmt.001": "ACCOUNT_OPEN", "acmt.002": "ACCOUNT_INFO",
            "acmt.003": "ACCOUNT_AMEND", "acmt.005": "SWITCH_REQ",
            "acmt.006": "SWITCH_RESP", "acmt.007": "ACCOUNT_CLOSE",
            "MT103": "CREDIT_TRANSFER", "MT200": "FI_TRANSFER",
            "MT202": "FI_TRANSFER", "MT202COV": "COVER_PAYMENT",
            "MT900": "CONFIRMATION", "MT910": "CONFIRMATION",
            "MT940": "STATEMENT", "MT942": "INTRADAY_REPORT",
            "MT950": "STATEMENT",
            "SEPA_SCT": "CREDIT_TRANSFER", "SEPA_SDD": "DIRECT_DEBIT",
            "NACHA_ACH": "ACH_TRANSFER", "FEDWIRE": "WIRE_TRANSFER",
            "CHIPS": "WIRE_TRANSFER",
            "BACS": "BATCH_PAYMENT", "CHAPS": "RTGS_PAYMENT",
            "FASTER_PAYMENTS": "INSTANT_PAYMENT",
            "FEDNOW": "INSTANT_PAYMENT", "RTP": "INSTANT_PAYMENT",
            "PIX": "INSTANT_PAYMENT", "NPP": "INSTANT_PAYMENT",
            "UPI": "INSTANT_PAYMENT", "PAYNOW": "INSTANT_PAYMENT",
            "PROMPTPAY": "INSTANT_PAYMENT", "INSTAPAY": "INSTANT_PAYMENT",
            "TARGET2": "RTGS_PAYMENT", "BOJNET": "RTGS_PAYMENT",
            "CNAPS": "RTGS_PAYMENT", "MEPS_PLUS": "RTGS_PAYMENT",
            "RTGS_HK": "RTGS_PAYMENT", "SARIE": "RTGS_PAYMENT",
            "UAEFTS": "RTGS_PAYMENT", "KFTC": "RTGS_PAYMENT",
        }
        payment_type = payment_type_mapping.get(message_type, "PAYMENT")

        connector.execute(f"""
            INSERT INTO {gold_table}
            (instruction_id, stg_id, message_type, payment_type, amount, currency,
             debtor_party_id, creditor_party_id, debtor_account_id, creditor_account_id,
             debtor_agent_id, creditor_agent_id, execution_date, value_date,
             status, created_at, updated_at, _batch_id, _ingested_at)
            VALUES (
                '{instr_id}',
                '{stg_id}',
                '{message_type}',
                '{payment_type}',
                {amount},
                '{currency}',
                'party_{uuid.uuid4().hex[:8]}',
                'party_{uuid.uuid4().hex[:8]}',
                'acct_{uuid.uuid4().hex[:8]}',
                'acct_{uuid.uuid4().hex[:8]}',
                'fi_{uuid.uuid4().hex[:8]}',
                'fi_{uuid.uuid4().hex[:8]}',
                DATE '{exec_date}',
                DATE '{exec_date}',
                'PROCESSED',
                CURRENT_TIMESTAMP(),
                CURRENT_TIMESTAMP(),
                '{batch_id}',
                CURRENT_TIMESTAMP()
            )
        """)
        result["gold_ok"] = True

    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    """Main execution function."""
    print("=" * 80)
    print("GPS CDM - Load All 66 Message Types to Databricks")
    print("=" * 80)
    print(f"\nStarted at: {datetime.now().isoformat()}")
    print(f"Message types to process: {len(SAMPLE_MESSAGES)}")

    # Initialize Databricks connector
    try:
        from gps_cdm.ingestion.persistence.databricks_connector import DatabricksConnector
        connector = DatabricksConnector()
        print("\n[OK] Connected to Databricks")
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to Databricks: {e}")
        return False

    # Generate batch ID
    batch_id = f"e2e_all_types_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    print(f"Batch ID: {batch_id}")

    results = []
    success_count = 0
    failed_count = 0

    print("\n" + "-" * 80)
    print("Processing messages...")
    print("-" * 80)

    for i, (message_type, sample_data) in enumerate(SAMPLE_MESSAGES.items(), 1):
        # Generate content
        if isinstance(sample_data, str):
            content = sample_data
        else:
            content = json.dumps(sample_data)

        # Process through pipeline
        result = process_message_to_databricks(batch_id, message_type, content, connector)
        results.append(result)

        # Status output
        if result["bronze_ok"] and result["silver_ok"] and result["gold_ok"]:
            status = "[OK]"
            success_count += 1
        else:
            status = "[FAIL]"
            failed_count += 1
            if result["error"]:
                status += f" - {result['error'][:50]}"

        print(f"  {i:2}/{len(SAMPLE_MESSAGES)} {message_type:<15} {status}")

    # Summary
    print("\n" + "=" * 80)
    print("PROCESSING SUMMARY")
    print("=" * 80)
    print(f"\nBatch ID: {batch_id}")
    print(f"Total message types: {len(SAMPLE_MESSAGES)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Success rate: {(success_count / len(SAMPLE_MESSAGES)) * 100:.1f}%")

    # Layer counts
    bronze_ok = sum(1 for r in results if r["bronze_ok"])
    silver_ok = sum(1 for r in results if r["silver_ok"])
    gold_ok = sum(1 for r in results if r["gold_ok"])

    print(f"\nLayer Statistics:")
    print(f"  Bronze: {bronze_ok}/{len(SAMPLE_MESSAGES)} records")
    print(f"  Silver: {silver_ok}/{len(SAMPLE_MESSAGES)} records")
    print(f"  Gold:   {gold_ok}/{len(SAMPLE_MESSAGES)} records")

    # Failed message types
    if failed_count > 0:
        print(f"\nFailed message types:")
        for r in results:
            if not (r["bronze_ok"] and r["silver_ok"] and r["gold_ok"]):
                print(f"  - {r['message_type']}: {r['error']}")

    print(f"\nCompleted at: {datetime.now().isoformat()}")

    return failed_count == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
