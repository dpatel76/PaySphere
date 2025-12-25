#!/usr/bin/env python3
"""
Generate test message files for all 63 GPS CDM payment message types.

Each file contains realistic payment data that matches the expected schema
for that message type.

Usage:
    python scripts/generate_test_messages.py [--output-dir data/nifi_input]
"""

import json
import os
import sys
import uuid
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# Realistic test data generators
def random_bic():
    """Generate a realistic BIC code."""
    banks = ['CITIUS33', 'CHASUS33', 'BOFAUS3N', 'WFBIUS6S', 'DEUTDEFF',
             'BNPAFRPP', 'HSBCHKHH', 'SCBLSGSG', 'ANZBAU3M', 'NABOROJJ']
    return random.choice(banks)


def random_iban():
    """Generate a realistic IBAN."""
    countries = [
        ('DE', '89370400440532013000'),
        ('GB', '29NWBK60161331926819'),
        ('FR', '1420041010050500013M02606'),
        ('ES', '9121000418450200051332'),
        ('IT', '60X0542811101000000123456'),
        ('NL', '91ABNA0417164300'),
    ]
    country, base = random.choice(countries)
    return f"{country}{random.randint(10,99)}{base[:18]}"


def random_name(prefix=""):
    """Generate a realistic party name."""
    first_names = ['John', 'Emma', 'Michael', 'Sarah', 'David', 'Lisa', 'James', 'Anna']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
    companies = ['Acme Corp', 'Global Industries', 'Tech Solutions', 'Prime Services',
                 'Alpha Trading', 'Beta Holdings', 'Omega Partners', 'Delta Systems']

    if random.random() > 0.5:
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    return random.choice(companies)


def random_amount():
    """Generate a realistic payment amount."""
    return round(random.uniform(100, 500000), 2)


def random_currency():
    """Generate a currency code."""
    currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'SGD', 'HKD', 'AED']
    return random.choice(currencies)


def random_date(days_back=30):
    """Generate a random date within the past N days."""
    delta = timedelta(days=random.randint(0, days_back))
    return (datetime.utcnow() - delta).strftime('%Y-%m-%d')


def random_datetime():
    """Generate current datetime in ISO format."""
    return datetime.utcnow().isoformat() + 'Z'


def random_reference():
    """Generate a payment reference."""
    return f"REF-{uuid.uuid4().hex[:12].upper()}"


# Message type specific generators
def generate_pain001():
    """ISO 20022 Customer Credit Transfer Initiation."""
    msg_id = f"PAIN001-{uuid.uuid4().hex[:8].upper()}"
    return {
        "messageType": "pain.001",
        "messageId": msg_id,
        "Document": {
            "CstmrCdtTrfInitn": {
                "GrpHdr": {
                    "MsgId": msg_id,
                    "CreDtTm": random_datetime(),
                    "NbOfTxs": "1",
                    "CtrlSum": str(random_amount()),
                    "InitgPty": {"Nm": random_name()}
                },
                "PmtInf": [{
                    "PmtInfId": f"PMT-{uuid.uuid4().hex[:8]}",
                    "PmtMtd": "TRF",
                    "ReqdExctnDt": {"Dt": random_date(7)},
                    "Dbtr": {"Nm": random_name("Debtor")},
                    "DbtrAcct": {"Id": {"IBAN": random_iban()}},
                    "DbtrAgt": {"FinInstnId": {"BICFI": random_bic()}},
                    "CdtTrfTxInf": [{
                        "PmtId": {"EndToEndId": random_reference()},
                        "Amt": {"InstdAmt": {"Ccy": random_currency(), "value": random_amount()}},
                        "Cdtr": {"Nm": random_name("Creditor")},
                        "CdtrAcct": {"Id": {"IBAN": random_iban()}},
                        "CdtrAgt": {"FinInstnId": {"BICFI": random_bic()}}
                    }]
                }]
            }
        }
    }


def generate_pain002():
    """ISO 20022 Customer Payment Status Report."""
    return {
        "messageType": "pain.002",
        "messageId": f"PAIN002-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalMessageId": f"PAIN001-{uuid.uuid4().hex[:8].upper()}",
        "originalMessageType": "pain.001",
        "groupStatus": random.choice(["ACCP", "ACSP", "ACSC", "ACWC", "RJCT", "PDNG"]),
        "statusReasonCode": random.choice(["AC01", "AC04", "AM04", "FF01", "RC01"]),
        "debtorName": random_name(),
        "creditorName": random_name(),
        "amount": random_amount(),
        "currency": random_currency()
    }


def generate_pain007():
    """ISO 20022 Customer Payment Reversal."""
    return {
        "messageType": "pain.007",
        "messageId": f"PAIN007-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalMessageId": f"PACS008-{uuid.uuid4().hex[:8].upper()}",
        "reversalReason": random.choice(["DUPL", "FRAD", "TECH", "CUST"]),
        "debtorName": random_name(),
        "creditorName": random_name(),
        "amount": random_amount(),
        "currency": random_currency()
    }


def generate_pain008():
    """ISO 20022 Customer Direct Debit Initiation."""
    return {
        "messageType": "pain.008",
        "messageId": f"PAIN008-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "numberOfTransactions": random.randint(1, 10),
        "controlSum": random_amount(),
        "creditorName": random_name(),
        "creditorIBAN": random_iban(),
        "creditorBIC": random_bic(),
        "debtorName": random_name(),
        "debtorIBAN": random_iban(),
        "debtorBIC": random_bic(),
        "amount": random_amount(),
        "currency": random_currency(),
        "mandateId": f"MNDT-{uuid.uuid4().hex[:8].upper()}"
    }


def generate_pain013():
    """ISO 20022 Creditor Payment Activation Request."""
    return {
        "messageType": "pain.013",
        "messageId": f"PAIN013-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "creditorName": random_name(),
        "creditorIBAN": random_iban(),
        "amount": random_amount(),
        "currency": random_currency(),
        "paymentPurpose": random.choice(["SALA", "SUPP", "TAXS", "TREA"])
    }


def generate_pain014():
    """ISO 20022 Creditor Payment Activation Request Status Report."""
    return {
        "messageType": "pain.014",
        "messageId": f"PAIN014-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalRequestId": f"PAIN013-{uuid.uuid4().hex[:8].upper()}",
        "status": random.choice(["ACCP", "RJCT", "PDNG"]),
        "creditorName": random_name()
    }


def generate_pacs002():
    """ISO 20022 FI to FI Payment Status Report."""
    return {
        "messageType": "pacs.002",
        "messageId": f"PACS002-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalMessageId": f"PACS008-{uuid.uuid4().hex[:8].upper()}",
        "transactionStatus": random.choice(["ACSP", "ACSC", "RJCT", "PDNG"]),
        "statusReasonCode": random.choice(["AC01", "AC04", "AM04", "FF01"]),
        "instructingAgent": random_bic(),
        "instructedAgent": random_bic()
    }


def generate_pacs003():
    """ISO 20022 FI to FI Customer Direct Debit."""
    return {
        "messageType": "pacs.003",
        "messageId": f"PACS003-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "settlementDate": random_date(3),
        "creditorName": random_name(),
        "creditorBIC": random_bic(),
        "debtorName": random_name(),
        "debtorBIC": random_bic(),
        "amount": random_amount(),
        "currency": random_currency()
    }


def generate_pacs004():
    """ISO 20022 Payment Return."""
    return {
        "messageType": "pacs.004",
        "messageId": f"PACS004-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalMessageId": f"PACS008-{uuid.uuid4().hex[:8].upper()}",
        "returnReason": random.choice(["AC01", "AC04", "AM04", "BE04", "MD01"]),
        "returnedAmount": random_amount(),
        "currency": random_currency(),
        "originalDebtorName": random_name(),
        "originalCreditorName": random_name()
    }


def generate_pacs007():
    """ISO 20022 FI to FI Payment Reversal."""
    return {
        "messageType": "pacs.007",
        "messageId": f"PACS007-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalMessageId": f"PACS008-{uuid.uuid4().hex[:8].upper()}",
        "reversalReason": random.choice(["DUPL", "FRAD", "TECH", "CUST"]),
        "amount": random_amount(),
        "currency": random_currency()
    }


def generate_pacs008():
    """ISO 20022 FI to FI Customer Credit Transfer."""
    msg_id = f"PACS008-{uuid.uuid4().hex[:8].upper()}"
    return {
        "messageType": "pacs.008",
        "messageId": msg_id,
        "creationDateTime": random_datetime(),
        "settlementDate": random_date(3),
        "instructingAgent": random_bic(),
        "instructedAgent": random_bic(),
        "debtorName": random_name(),
        "debtorIBAN": random_iban(),
        "debtorBIC": random_bic(),
        "creditorName": random_name(),
        "creditorIBAN": random_iban(),
        "creditorBIC": random_bic(),
        "amount": random_amount(),
        "currency": random_currency(),
        "endToEndId": random_reference(),
        "chargeBearer": random.choice(["DEBT", "CRED", "SHAR", "SLEV"])
    }


def generate_pacs009():
    """ISO 20022 FI Credit Transfer."""
    return {
        "messageType": "pacs.009",
        "messageId": f"PACS009-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "settlementDate": random_date(3),
        "instructingAgent": random_bic(),
        "instructedAgent": random_bic(),
        "amount": random_amount(),
        "currency": random_currency()
    }


def generate_pacs028():
    """ISO 20022 FI to FI Payment Status Request."""
    return {
        "messageType": "pacs.028",
        "messageId": f"PACS028-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalMessageId": f"PACS008-{uuid.uuid4().hex[:8].upper()}",
        "requestingAgent": random_bic(),
        "respondingAgent": random_bic()
    }


def generate_camt026():
    """ISO 20022 Unable to Apply."""
    return {
        "messageType": "camt.026",
        "messageId": f"CAMT026-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalMessageId": f"PACS008-{uuid.uuid4().hex[:8].upper()}",
        "unableToApplyReason": random.choice(["AC01", "AC04", "AM04"]),
        "amount": random_amount(),
        "currency": random_currency()
    }


def generate_camt027():
    """ISO 20022 Claim Non Receipt."""
    return {
        "messageType": "camt.027",
        "messageId": f"CAMT027-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalMessageId": f"PACS008-{uuid.uuid4().hex[:8].upper()}",
        "claimReason": "NRCH",
        "creditorName": random_name(),
        "expectedAmount": random_amount(),
        "currency": random_currency()
    }


def generate_camt028():
    """ISO 20022 Additional Payment Information."""
    return {
        "messageType": "camt.028",
        "messageId": f"CAMT028-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalMessageId": f"PACS008-{uuid.uuid4().hex[:8].upper()}",
        "additionalInfo": "Payment details as requested",
        "debtorName": random_name(),
        "amount": random_amount()
    }


def generate_camt029():
    """ISO 20022 Resolution of Investigation."""
    return {
        "messageType": "camt.029",
        "messageId": f"CAMT029-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "caseId": f"CASE-{uuid.uuid4().hex[:8].upper()}",
        "status": random.choice(["CONF", "RJCT", "PDNG"]),
        "resolution": random.choice(["MODI", "CANC", "ACPT"])
    }


def generate_camt052():
    """ISO 20022 Bank to Customer Account Report."""
    return {
        "messageType": "camt.052",
        "messageId": f"CAMT052-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "accountIBAN": random_iban(),
        "accountOwner": random_name(),
        "reportingPeriod": {"fromDate": random_date(30), "toDate": random_date(0)},
        "openingBalance": random_amount(),
        "closingBalance": random_amount(),
        "currency": random_currency()
    }


def generate_camt053():
    """ISO 20022 Bank to Customer Statement."""
    return {
        "messageType": "camt.053",
        "messageId": f"CAMT053-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "accountIBAN": random_iban(),
        "accountOwner": random_name(),
        "statementDate": random_date(0),
        "openingBalance": random_amount(),
        "closingBalance": random_amount(),
        "currency": random_currency(),
        "numberOfEntries": random.randint(1, 100)
    }


def generate_camt054():
    """ISO 20022 Bank to Customer Debit Credit Notification."""
    return {
        "messageType": "camt.054",
        "messageId": f"CAMT054-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "accountIBAN": random_iban(),
        "notificationType": random.choice(["CRDT", "DBIT"]),
        "amount": random_amount(),
        "currency": random_currency(),
        "valueDate": random_date(0),
        "remittanceInfo": random_reference()
    }


def generate_camt055():
    """ISO 20022 Customer Payment Cancellation Request."""
    return {
        "messageType": "camt.055",
        "messageId": f"CAMT055-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalMessageId": f"PAIN001-{uuid.uuid4().hex[:8].upper()}",
        "cancellationReason": random.choice(["DUPL", "FRAD", "TECH", "CUST"]),
        "requestorName": random_name()
    }


def generate_camt056():
    """ISO 20022 FI to FI Payment Cancellation Request."""
    return {
        "messageType": "camt.056",
        "messageId": f"CAMT056-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalMessageId": f"PACS008-{uuid.uuid4().hex[:8].upper()}",
        "cancellationReason": random.choice(["DUPL", "FRAD", "TECH", "CUST"]),
        "instructingAgent": random_bic(),
        "instructedAgent": random_bic()
    }


def generate_camt057():
    """ISO 20022 Notification to Receive."""
    return {
        "messageType": "camt.057",
        "messageId": f"CAMT057-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "expectedPaymentDate": random_date(7),
        "creditorName": random_name(),
        "creditorIBAN": random_iban(),
        "expectedAmount": random_amount(),
        "currency": random_currency()
    }


def generate_camt086():
    """ISO 20022 Bank Services Billing Statement."""
    return {
        "messageType": "camt.086",
        "messageId": f"CAMT086-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "billingPeriod": {"fromDate": random_date(30), "toDate": random_date(0)},
        "accountIBAN": random_iban(),
        "totalCharges": random_amount(),
        "currency": random_currency()
    }


def generate_camt087():
    """ISO 20022 Request to Modify Payment."""
    return {
        "messageType": "camt.087",
        "messageId": f"CAMT087-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalMessageId": f"PACS008-{uuid.uuid4().hex[:8].upper()}",
        "modificationReason": random.choice(["CRRB", "CRRP", "CRRA"]),
        "requestorName": random_name()
    }


def generate_acmt001():
    """ISO 20022 Account Opening Instruction."""
    return {
        "messageType": "acmt.001",
        "messageId": f"ACMT001-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "accountOwnerName": random_name(),
        "accountType": random.choice(["CACC", "SVGS", "LOAN"]),
        "currency": random_currency(),
        "servicingAgent": random_bic()
    }


def generate_acmt002():
    """ISO 20022 Account Opening Instruction Amendment."""
    return {
        "messageType": "acmt.002",
        "messageId": f"ACMT002-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalInstructionId": f"ACMT001-{uuid.uuid4().hex[:8].upper()}",
        "amendmentReason": "Address update",
        "accountOwnerName": random_name()
    }


def generate_acmt003():
    """ISO 20022 Account Opening Confirmation."""
    return {
        "messageType": "acmt.003",
        "messageId": f"ACMT003-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalInstructionId": f"ACMT001-{uuid.uuid4().hex[:8].upper()}",
        "accountNumber": random_iban(),
        "accountOwnerName": random_name(),
        "accountStatus": "OPEN"
    }


def generate_acmt005():
    """ISO 20022 Account Request for Acknowledgement."""
    return {
        "messageType": "acmt.005",
        "messageId": f"ACMT005-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "accountNumber": random_iban(),
        "requestType": "STAT"
    }


def generate_acmt006():
    """ISO 20022 Account Request Acknowledgement."""
    return {
        "messageType": "acmt.006",
        "messageId": f"ACMT006-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "originalRequestId": f"ACMT005-{uuid.uuid4().hex[:8].upper()}",
        "acknowledgementStatus": random.choice(["ACCP", "RJCT"])
    }


def generate_acmt007():
    """ISO 20022 Account Closing Request."""
    return {
        "messageType": "acmt.007",
        "messageId": f"ACMT007-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "accountNumber": random_iban(),
        "accountOwnerName": random_name(),
        "closingReason": random.choice(["DEAD", "DORM", "CUST"])
    }


def generate_mt103():
    """SWIFT MT103 Single Customer Credit Transfer."""
    return {
        "messageType": "MT103",
        "messageId": f"MT103-{uuid.uuid4().hex[:8].upper()}",
        "senderBIC": random_bic(),
        "receiverBIC": random_bic(),
        "transactionReference": random_reference(),
        "valueDate": random_date(3),
        "currency": random_currency(),
        "amount": random_amount(),
        "orderingCustomerName": random_name(),
        "orderingCustomerAccount": random_iban(),
        "beneficiaryName": random_name(),
        "beneficiaryAccount": random_iban(),
        "detailsOfCharges": random.choice(["OUR", "BEN", "SHA"])
    }


def generate_mt200():
    """SWIFT MT200 Financial Institution Transfer."""
    return {
        "messageType": "MT200",
        "messageId": f"MT200-{uuid.uuid4().hex[:8].upper()}",
        "senderBIC": random_bic(),
        "receiverBIC": random_bic(),
        "transactionReference": random_reference(),
        "valueDate": random_date(3),
        "currency": random_currency(),
        "amount": random_amount()
    }


def generate_mt202():
    """SWIFT MT202 General Financial Institution Transfer."""
    return {
        "messageType": "MT202",
        "messageId": f"MT202-{uuid.uuid4().hex[:8].upper()}",
        "senderBIC": random_bic(),
        "receiverBIC": random_bic(),
        "transactionReference": random_reference(),
        "relatedReference": random_reference(),
        "valueDate": random_date(3),
        "currency": random_currency(),
        "amount": random_amount(),
        "orderingInstitution": random_bic(),
        "beneficiaryInstitution": random_bic()
    }


def generate_mt202cov():
    """SWIFT MT202COV Cover Payment."""
    return {
        "messageType": "MT202COV",
        "messageId": f"MT202COV-{uuid.uuid4().hex[:8].upper()}",
        "senderBIC": random_bic(),
        "receiverBIC": random_bic(),
        "transactionReference": random_reference(),
        "valueDate": random_date(3),
        "currency": random_currency(),
        "amount": random_amount(),
        "underlyingMT103Ref": f"MT103-{uuid.uuid4().hex[:8].upper()}",
        "orderingCustomerName": random_name(),
        "beneficiaryName": random_name()
    }


def generate_mt900():
    """SWIFT MT900 Confirmation of Debit."""
    return {
        "messageType": "MT900",
        "messageId": f"MT900-{uuid.uuid4().hex[:8].upper()}",
        "senderBIC": random_bic(),
        "receiverBIC": random_bic(),
        "transactionReference": random_reference(),
        "relatedReference": random_reference(),
        "valueDate": random_date(0),
        "currency": random_currency(),
        "amount": random_amount(),
        "accountNumber": random_iban()
    }


def generate_mt910():
    """SWIFT MT910 Confirmation of Credit."""
    return {
        "messageType": "MT910",
        "messageId": f"MT910-{uuid.uuid4().hex[:8].upper()}",
        "senderBIC": random_bic(),
        "receiverBIC": random_bic(),
        "transactionReference": random_reference(),
        "relatedReference": random_reference(),
        "valueDate": random_date(0),
        "currency": random_currency(),
        "amount": random_amount(),
        "accountNumber": random_iban(),
        "orderingCustomerName": random_name()
    }


def generate_mt940():
    """SWIFT MT940 Customer Statement Message."""
    return {
        "messageType": "MT940",
        "messageId": f"MT940-{uuid.uuid4().hex[:8].upper()}",
        "senderBIC": random_bic(),
        "receiverBIC": random_bic(),
        "transactionReference": random_reference(),
        "accountNumber": random_iban(),
        "statementNumber": f"{random.randint(1,999)}/{random.randint(1,365)}",
        "openingBalance": {"date": random_date(1), "currency": random_currency(), "amount": random_amount()},
        "closingBalance": {"date": random_date(0), "currency": random_currency(), "amount": random_amount()},
        "numberOfEntries": random.randint(1, 50)
    }


def generate_mt950():
    """SWIFT MT950 Statement Message."""
    return {
        "messageType": "MT950",
        "messageId": f"MT950-{uuid.uuid4().hex[:8].upper()}",
        "senderBIC": random_bic(),
        "receiverBIC": random_bic(),
        "transactionReference": random_reference(),
        "accountNumber": random_iban(),
        "statementNumber": f"{random.randint(1,999)}/{random.randint(1,365)}",
        "openingBalance": {"date": random_date(1), "currency": random_currency(), "amount": random_amount()},
        "closingBalance": {"date": random_date(0), "currency": random_currency(), "amount": random_amount()}
    }


def generate_sepa_sct():
    """SEPA Credit Transfer."""
    return {
        "messageType": "SEPA_SCT",
        "messageId": f"SEPA-SCT-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "paymentInformationId": f"PMT-{uuid.uuid4().hex[:8]}",
        "debtorName": random_name(),
        "debtorIBAN": random_iban(),
        "debtorBIC": random_bic(),
        "creditorName": random_name(),
        "creditorIBAN": random_iban(),
        "creditorBIC": random_bic(),
        "amount": random_amount(),
        "currency": "EUR",
        "endToEndId": random_reference(),
        "remittanceInfo": f"Invoice {random.randint(1000, 9999)}"
    }


def generate_sepa_sdd():
    """SEPA Direct Debit."""
    return {
        "messageType": "SEPA_SDD",
        "messageId": f"SEPA-SDD-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "creditorId": f"DE98ZZZ09999999999",
        "creditorName": random_name(),
        "creditorIBAN": random_iban(),
        "debtorName": random_name(),
        "debtorIBAN": random_iban(),
        "amount": random_amount(),
        "currency": "EUR",
        "mandateId": f"MNDT-{uuid.uuid4().hex[:8].upper()}",
        "mandateSignDate": random_date(365),
        "sequenceType": random.choice(["FRST", "RCUR", "FNAL", "OOFF"])
    }


def generate_nacha_ach():
    """NACHA ACH Payment."""
    return {
        "messageType": "NACHA_ACH",
        "messageId": f"ACH-{uuid.uuid4().hex[:8].upper()}",
        "batchNumber": random.randint(1, 9999),
        "companyName": random_name(),
        "companyId": f"{random.randint(100000000, 999999999)}",
        "standardEntryClass": random.choice(["PPD", "CCD", "CTX", "WEB", "TEL"]),
        "effectiveEntryDate": random_date(3),
        "originatingDFI": f"{random.randint(10000000, 99999999)}",
        "receivingDFI": f"{random.randint(10000000, 99999999)}",
        "receiverName": random_name(),
        "receiverAccount": f"{random.randint(100000000, 9999999999)}",
        "amount": random_amount(),
        "transactionCode": random.choice(["22", "27", "32", "37"])
    }


def generate_fedwire():
    """Fedwire Funds Transfer."""
    return {
        "messageType": "Fedwire",
        "messageId": f"FW-{uuid.uuid4().hex[:8].upper()}",
        "imad": f"{random_date(0).replace('-','')}{random_bic()[:8]}{random.randint(100000,999999)}",
        "omad": f"{random_date(0).replace('-','')}{random_bic()[:8]}{random.randint(100000,999999)}",
        "senderABA": f"{random.randint(10000000, 99999999)}1",
        "senderName": random_name(),
        "receiverABA": f"{random.randint(10000000, 99999999)}1",
        "receiverName": random_name(),
        "amount": random_amount(),
        "currency": "USD",
        "businessFunctionCode": random.choice(["BTR", "CTR", "DRB", "DRC", "FFR", "FFS"]),
        "beneficiaryName": random_name(),
        "beneficiaryAccount": f"{random.randint(100000000, 9999999999)}",
        "originatorName": random_name(),
        "originatorAccount": f"{random.randint(100000000, 9999999999)}"
    }


def generate_fednow():
    """FedNow Instant Payment."""
    return {
        "messageType": "FedNow",
        "messageId": f"FEDNOW-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderABA": f"{random.randint(10000000, 99999999)}1",
        "senderName": random_name(),
        "receiverABA": f"{random.randint(10000000, 99999999)}1",
        "receiverName": random_name(),
        "amount": random_amount(),
        "currency": "USD",
        "settlementMethod": "CLRG",
        "endToEndId": random_reference(),
        "creditorName": random_name(),
        "creditorAccount": f"{random.randint(100000000, 9999999999)}",
        "debtorName": random_name(),
        "debtorAccount": f"{random.randint(100000000, 9999999999)}"
    }


def generate_rtp():
    """RTP (The Clearing House Real-Time Payments)."""
    return {
        "messageType": "RTP",
        "messageId": f"RTP-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderRTN": f"{random.randint(10000000, 99999999)}1",
        "receiverRTN": f"{random.randint(10000000, 99999999)}1",
        "amount": random_amount(),
        "currency": "USD",
        "creditorName": random_name(),
        "creditorAccount": f"{random.randint(100000000, 9999999999)}",
        "debtorName": random_name(),
        "debtorAccount": f"{random.randint(100000000, 9999999999)}",
        "paymentPurpose": random.choice(["SALA", "SUPP", "PENS", "TAXS"])
    }


def generate_chips():
    """CHIPS (Clearing House Interbank Payments System)."""
    return {
        "messageType": "CHIPS",
        "messageId": f"CHIPS-{uuid.uuid4().hex[:8].upper()}",
        "chipsSequenceNumber": f"{random.randint(100000, 999999)}",
        "senderChipsUID": f"{random.randint(100000, 999999)}",
        "receiverChipsUID": f"{random.randint(100000, 999999)}",
        "amount": random_amount(),
        "currency": "USD",
        "valueDate": random_date(1),
        "senderReference": random_reference(),
        "beneficiaryName": random_name(),
        "originatorName": random_name()
    }


def generate_target2():
    """TARGET2 RTGS Payment."""
    return {
        "messageType": "TARGET2",
        "messageId": f"T2-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderBIC": random_bic(),
        "receiverBIC": random_bic(),
        "amount": random_amount(),
        "currency": "EUR",
        "settlementDate": random_date(0),
        "priority": random.choice(["HIGH", "NORM"]),
        "endToEndId": random_reference()
    }


def generate_bacs():
    """UK BACS Payment."""
    return {
        "messageType": "BACS",
        "messageId": f"BACS-{uuid.uuid4().hex[:8].upper()}",
        "originatingSortCode": f"{random.randint(100000, 999999)}",
        "originatingAccount": f"{random.randint(10000000, 99999999)}",
        "destinationSortCode": f"{random.randint(100000, 999999)}",
        "destinationAccount": f"{random.randint(10000000, 99999999)}",
        "amount": random_amount(),
        "currency": "GBP",
        "processingDate": random_date(3),
        "transactionCode": random.choice(["99", "01", "17", "18"]),
        "reference": random_reference()[:18]
    }


def generate_chaps():
    """UK CHAPS Payment."""
    return {
        "messageType": "CHAPS",
        "messageId": f"CHAPS-{uuid.uuid4().hex[:8].upper()}",
        "senderBIC": random_bic(),
        "receiverBIC": random_bic(),
        "amount": random_amount(),
        "currency": "GBP",
        "valueDate": random_date(0),
        "senderAccount": f"GB{random.randint(10, 99)}XXXX{random.randint(10000000, 99999999)}{random.randint(10000000, 99999999)}",
        "beneficiaryAccount": f"GB{random.randint(10, 99)}XXXX{random.randint(10000000, 99999999)}{random.randint(10000000, 99999999)}",
        "beneficiaryName": random_name(),
        "remittanceInfo": random_reference()
    }


def generate_fps():
    """UK Faster Payments."""
    return {
        "messageType": "FPS",
        "messageId": f"FPS-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderSortCode": f"{random.randint(100000, 999999)}",
        "senderAccount": f"{random.randint(10000000, 99999999)}",
        "receiverSortCode": f"{random.randint(100000, 999999)}",
        "receiverAccount": f"{random.randint(10000000, 99999999)}",
        "amount": random_amount(),
        "currency": "GBP",
        "reference": random_reference()[:18],
        "paymentType": random.choice(["SIP", "SOP", "FDP", "FOP"])
    }


def generate_pix():
    """Brazil PIX Instant Payment."""
    return {
        "messageType": "PIX",
        "messageId": f"PIX-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderISPB": f"{random.randint(10000000, 99999999)}",
        "senderName": random_name(),
        "senderPixKey": f"+55{random.randint(11000000000, 99999999999)}",
        "receiverISPB": f"{random.randint(10000000, 99999999)}",
        "receiverName": random_name(),
        "receiverPixKey": f"+55{random.randint(11000000000, 99999999999)}",
        "amount": random_amount(),
        "currency": "BRL",
        "endToEndId": f"E{random.randint(10000000, 99999999)}{random_datetime()[:10].replace('-','')}{uuid.uuid4().hex[:11]}"
    }


def generate_upi():
    """India UPI Payment."""
    return {
        "messageType": "UPI",
        "messageId": f"UPI-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "payerVPA": f"{random_name().lower().replace(' ','')}@upi",
        "payerName": random_name(),
        "payerIFSC": f"HDFC0{random.randint(100000, 999999)}",
        "payeeVPA": f"{random_name().lower().replace(' ','')}@upi",
        "payeeName": random_name(),
        "payeeIFSC": f"ICIC0{random.randint(100000, 999999)}",
        "amount": random_amount(),
        "currency": "INR",
        "transactionNote": random.choice(["Payment for services", "Invoice payment", "Transfer", "Bill payment"])
    }


def generate_npp():
    """Australia NPP Payment."""
    return {
        "messageType": "NPP",
        "messageId": f"NPP-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderBSB": f"{random.randint(100, 999)}-{random.randint(100, 999)}",
        "senderAccount": f"{random.randint(100000000, 999999999)}",
        "senderName": random_name(),
        "receiverBSB": f"{random.randint(100, 999)}-{random.randint(100, 999)}",
        "receiverAccount": f"{random.randint(100000000, 999999999)}",
        "receiverName": random_name(),
        "payId": f"{random_name().lower().replace(' ','')}@payid",
        "amount": random_amount(),
        "currency": "AUD"
    }


def generate_paynow():
    """Singapore PayNow."""
    return {
        "messageType": "PayNow",
        "messageId": f"PAYNOW-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderBIC": random_bic(),
        "senderName": random_name(),
        "senderProxy": f"+65{random.randint(80000000, 99999999)}",
        "receiverBIC": random_bic(),
        "receiverName": random_name(),
        "receiverProxy": f"+65{random.randint(80000000, 99999999)}",
        "amount": random_amount(),
        "currency": "SGD"
    }


def generate_promptpay():
    """Thailand PromptPay."""
    return {
        "messageType": "PromptPay",
        "messageId": f"PROMPTPAY-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderBankCode": f"{random.randint(1, 99):03d}",
        "senderName": random_name(),
        "senderPromptPayId": f"0{random.randint(800000000, 999999999)}",
        "receiverBankCode": f"{random.randint(1, 99):03d}",
        "receiverName": random_name(),
        "receiverPromptPayId": f"0{random.randint(800000000, 999999999)}",
        "amount": random_amount(),
        "currency": "THB"
    }


def generate_instapay():
    """Philippines InstaPay."""
    return {
        "messageType": "InstaPay",
        "messageId": f"INSTAPAY-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderBankCode": f"{random.randint(1, 99):04d}",
        "senderAccount": f"{random.randint(1000000000, 9999999999)}",
        "senderName": random_name(),
        "receiverBankCode": f"{random.randint(1, 99):04d}",
        "receiverAccount": f"{random.randint(1000000000, 9999999999)}",
        "receiverName": random_name(),
        "amount": random_amount(),
        "currency": "PHP"
    }


def generate_kftc():
    """South Korea KFTC Payment."""
    return {
        "messageType": "KFTC",
        "messageId": f"KFTC-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderBankCode": f"{random.randint(1, 99):03d}",
        "senderAccount": f"{random.randint(100000000000, 999999999999)}",
        "senderName": random_name(),
        "receiverBankCode": f"{random.randint(1, 99):03d}",
        "receiverAccount": f"{random.randint(100000000000, 999999999999)}",
        "receiverName": random_name(),
        "amount": random_amount(),
        "currency": "KRW"
    }


def generate_bojnet():
    """Japan BOJ-NET Payment."""
    return {
        "messageType": "BOJNET",
        "messageId": f"BOJNET-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderBIC": random_bic(),
        "senderAccount": f"{random.randint(1000000, 9999999)}",
        "receiverBIC": random_bic(),
        "receiverAccount": f"{random.randint(1000000, 9999999)}",
        "amount": random_amount(),
        "currency": "JPY",
        "valueDate": random_date(0)
    }


def generate_cnaps():
    """China CNAPS Payment."""
    return {
        "messageType": "CNAPS",
        "messageId": f"CNAPS-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderBankCode": f"{random.randint(100000000000, 999999999999)}",
        "senderAccount": f"{random.randint(1000000000000000, 9999999999999999)}",
        "senderName": random_name(),
        "receiverBankCode": f"{random.randint(100000000000, 999999999999)}",
        "receiverAccount": f"{random.randint(1000000000000000, 9999999999999999)}",
        "receiverName": random_name(),
        "amount": random_amount(),
        "currency": "CNY"
    }


def generate_rtgs_hk():
    """Hong Kong RTGS Payment."""
    return {
        "messageType": "RTGS_HK",
        "messageId": f"RTGS-HK-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderBIC": random_bic(),
        "receiverBIC": random_bic(),
        "amount": random_amount(),
        "currency": random.choice(["HKD", "USD", "EUR", "CNY"]),
        "valueDate": random_date(0),
        "priority": random.choice(["01", "02"])
    }


def generate_meps():
    """Singapore MEPS+ RTGS."""
    return {
        "messageType": "MEPS",
        "messageId": f"MEPS-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderBIC": random_bic(),
        "receiverBIC": random_bic(),
        "amount": random_amount(),
        "currency": "SGD",
        "valueDate": random_date(0),
        "endToEndId": random_reference()
    }


def generate_sarie():
    """Saudi Arabia SARIE RTGS."""
    return {
        "messageType": "SARIE",
        "messageId": f"SARIE-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderBIC": random_bic(),
        "senderAccount": f"SA{random.randint(10, 99)}{random.randint(1000000000000000, 9999999999999999)}{random.randint(1000, 9999)}",
        "receiverBIC": random_bic(),
        "receiverAccount": f"SA{random.randint(10, 99)}{random.randint(1000000000000000, 9999999999999999)}{random.randint(1000, 9999)}",
        "amount": random_amount(),
        "currency": "SAR",
        "valueDate": random_date(0)
    }


def generate_uaefts():
    """UAE UAEFTS Payment."""
    return {
        "messageType": "UAEFTS",
        "messageId": f"UAEFTS-{uuid.uuid4().hex[:8].upper()}",
        "creationDateTime": random_datetime(),
        "senderBIC": random_bic(),
        "senderIBAN": f"AE{random.randint(10, 99)}{random.randint(100, 999)}{random.randint(1000000000000000, 9999999999999999)}",
        "receiverBIC": random_bic(),
        "receiverIBAN": f"AE{random.randint(10, 99)}{random.randint(100, 999)}{random.randint(1000000000000000, 9999999999999999)}",
        "amount": random_amount(),
        "currency": "AED",
        "valueDate": random_date(0)
    }


# Message type to generator mapping
MESSAGE_GENERATORS = {
    # ISO 20022 PAIN
    "pain.001": generate_pain001,
    "pain.002": generate_pain002,
    "pain.007": generate_pain007,
    "pain.008": generate_pain008,
    "pain.013": generate_pain013,
    "pain.014": generate_pain014,

    # ISO 20022 PACS
    "pacs.002": generate_pacs002,
    "pacs.003": generate_pacs003,
    "pacs.004": generate_pacs004,
    "pacs.007": generate_pacs007,
    "pacs.008": generate_pacs008,
    "pacs.009": generate_pacs009,
    "pacs.028": generate_pacs028,

    # ISO 20022 CAMT
    "camt.026": generate_camt026,
    "camt.027": generate_camt027,
    "camt.028": generate_camt028,
    "camt.029": generate_camt029,
    "camt.052": generate_camt052,
    "camt.053": generate_camt053,
    "camt.054": generate_camt054,
    "camt.055": generate_camt055,
    "camt.056": generate_camt056,
    "camt.057": generate_camt057,
    "camt.086": generate_camt086,
    "camt.087": generate_camt087,

    # ISO 20022 ACMT
    "acmt.001": generate_acmt001,
    "acmt.002": generate_acmt002,
    "acmt.003": generate_acmt003,
    "acmt.005": generate_acmt005,
    "acmt.006": generate_acmt006,
    "acmt.007": generate_acmt007,

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


def generate_all_test_messages(output_dir: str = "data/nifi_input"):
    """Generate test message files for all supported message types."""
    os.makedirs(output_dir, exist_ok=True)

    generated = []

    for msg_type, generator in MESSAGE_GENERATORS.items():
        try:
            # Generate the message
            message = generator()

            # Create filename (sanitize message type for filename)
            safe_type = msg_type.replace('.', '_').replace('/', '_')
            filename = f"{safe_type}_{uuid.uuid4().hex[:8]}.json"
            filepath = os.path.join(output_dir, filename)

            # Write to file
            with open(filepath, 'w') as f:
                json.dump(message, f, indent=2, default=str)

            generated.append((msg_type, filepath))
            print(f"✓ Generated: {filename}")

        except Exception as e:
            print(f"✗ Error generating {msg_type}: {e}")

    print(f"\n{'='*60}")
    print(f"Generated {len(generated)} test message files in {output_dir}")
    print(f"{'='*60}")

    return generated


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate test message files for GPS CDM")
    parser.add_argument(
        "--output-dir",
        default="data/nifi_input",
        help="Output directory for test files (default: data/nifi_input)"
    )
    args = parser.parse_args()

    generate_all_test_messages(args.output_dir)


if __name__ == "__main__":
    main()
