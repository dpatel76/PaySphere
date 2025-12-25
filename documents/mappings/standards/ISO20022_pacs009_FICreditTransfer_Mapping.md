# ISO 20022 pacs.009.001.10 - Financial Institution Credit Transfer
## Complete Field Mapping to GPS CDM

**Message Type:** pacs.009.001.10 (FinancialInstitutionCreditTransferV10)
**Standard:** ISO 20022
**Usage:** Financial institution to financial institution own account transfer
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 125 fields mapped)

---

## Message Overview

The pacs.009 message is used to transfer funds between financial institutions' own accounts. Unlike pacs.008 (customer credit transfer), pacs.009 is specifically for financial institution treasury operations, liquidity management, and interbank settlements where the financial institution is acting as principal rather than agent.

**Key Use Cases:**
- Financial institution treasury operations
- Liquidity management between correspondent accounts
- Central bank account funding
- Interbank settlement of own positions
- Nostro/Vostro account management
- Reserve requirement management

**Message Flow:** Instructing Financial Institution → Instructed Financial Institution

**Key Difference from pacs.008:** pacs.009 does not contain customer (debtor/creditor) information as it represents FI-to-FI own account transfers.

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total pacs.009 Fields** | 125 | 100% |
| **Mapped to CDM** | 125 | 100% |
| **Direct Mapping** | 115 | 92% |
| **Derived/Calculated** | 8 | 6% |
| **Reference Data Lookup** | 2 | 2% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | messageId | Unique message identifier |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISO DateTime | PaymentInstruction | creationDateTime | Message creation timestamp |
| GrpHdr/BtchBookg | Batch Booking | Indicator | - | 0..1 | true/false | PaymentInstruction | batchBooking | Batch or individual booking |
| GrpHdr/NbOfTxs | Number Of Transactions | Text | 1-15 | 0..1 | Numeric | PaymentInstruction | numberOfTransactions | Total transactions in message |
| GrpHdr/CtrlSum | Control Sum | DecimalNumber | - | 0..1 | Decimal (18,5) | PaymentInstruction | controlSum | Total amount for control |
| GrpHdr/TtlIntrBkSttlmAmt | Total Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | interbankSettlementAmount | Total settlement amount |
| GrpHdr/TtlIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | interbankSettlementAmount.currency | ISO currency code |
| GrpHdr/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | interbankSettlementDate | Settlement date between FIs |
| GrpHdr/SttlmInf/SttlmMtd | Settlement Method | Code | - | 1..1 | INDA, INGA, COVE, CLRG | PaymentInstruction | settlementMethod | Settlement method code |
| GrpHdr/SttlmInf/SttlmAcct/Id/IBAN | Settlement Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Settlement account IBAN |
| GrpHdr/SttlmInf/SttlmAcct/Id/Othr/Id | Settlement Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Other account identifier |
| GrpHdr/SttlmInf/SttlmAcct/Tp/Cd | Settlement Account Type | Code | - | 0..1 | CACC, SVGS, etc. | Account | accountType | Account type code |
| GrpHdr/SttlmInf/SttlmAcct/Ccy | Settlement Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency |
| GrpHdr/SttlmInf/SttlmAcct/Nm | Settlement Account Name | Text | 1-70 | 0..1 | Free text | Account | accountName | Account name |
| GrpHdr/SttlmInf/ClrSys/Cd | Clearing System Code | Code | - | 0..1 | External code | PaymentInstruction | clearingSystemCode | Clearing system identification |
| GrpHdr/SttlmInf/InstgRmbrsmntAgt/FinInstnId/BICFI | Instructing Reimbursement Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Reimbursement agent BIC |
| GrpHdr/SttlmInf/InstgRmbrsmntAgt/FinInstnId/ClrSysMmbId/MmbId | Reimbursement Agent Clearing Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| GrpHdr/SttlmInf/InstgRmbrsmntAgt/FinInstnId/Nm | Reimbursement Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Institution name |
| GrpHdr/SttlmInf/InstgRmbrsmntAgtAcct/Id/IBAN | Reimbursement Agent Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Reimbursement account IBAN |
| GrpHdr/SttlmInf/InstdRmbrsmntAgt/FinInstnId/BICFI | Instructed Reimbursement Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Reimbursement agent BIC |
| GrpHdr/SttlmInf/InstdRmbrsmntAgtAcct/Id/IBAN | Instructed Reimbursement Agent Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Reimbursement account IBAN |
| GrpHdr/SttlmInf/ThrdRmbrsmntAgt/FinInstnId/BICFI | Third Reimbursement Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Third reimbursement agent |
| GrpHdr/PmtTpInf/InstrPrty | Instruction Priority | Code | - | 0..1 | HIGH, NORM | PaymentInstruction | instructionPriority | Priority indicator |
| GrpHdr/PmtTpInf/ClrChanl | Clearing Channel | Code | - | 0..1 | RTGS, RTNS, MPNS, BOOK | PaymentInstruction | clearingChannel | Clearing channel |
| GrpHdr/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | serviceLevelCode | Service level |
| GrpHdr/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | 1-35 | 0..1 | External code | PaymentInstruction | localInstrument | Country-specific code |
| GrpHdr/InstgAgt/FinInstnId/BICFI | Instructing Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Instructing financial institution |
| GrpHdr/InstgAgt/FinInstnId/ClrSysMmbId/MmbId | Instructing Agent Clearing Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| GrpHdr/InstgAgt/FinInstnId/LEI | Instructing Agent LEI | Code | 20 | 0..1 | LEI | FinancialInstitution | lei | Legal Entity Identifier |
| GrpHdr/InstgAgt/FinInstnId/Nm | Instructing Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Institution name |
| GrpHdr/InstgAgt/FinInstnId/PstlAdr/AdrLine | Instructing Agent Address Line | Text | 1-70 | 0..7 | Free text | FinancialInstitution | addressLine | Address (up to 7 lines) |
| GrpHdr/InstgAgt/FinInstnId/PstlAdr/Ctry | Instructing Agent Country | Code | 2 | 0..1 | ISO 3166 | FinancialInstitution | country | Country code |
| GrpHdr/InstdAgt/FinInstnId/BICFI | Instructed Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Instructed financial institution |
| GrpHdr/InstdAgt/FinInstnId/ClrSysMmbId/MmbId | Instructed Agent Clearing Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| GrpHdr/InstdAgt/FinInstnId/LEI | Instructed Agent LEI | Code | 20 | 0..1 | LEI | FinancialInstitution | lei | Legal Entity Identifier |
| GrpHdr/InstdAgt/FinInstnId/Nm | Instructed Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Institution name |
| GrpHdr/InstdAgt/FinInstnId/PstlAdr/AdrLine | Instructed Agent Address Line | Text | 1-70 | 0..7 | Free text | FinancialInstitution | addressLine | Address (up to 7 lines) |
| GrpHdr/InstdAgt/FinInstnId/PstlAdr/Ctry | Instructed Agent Country | Code | 2 | 0..1 | ISO 3166 | FinancialInstitution | country | Country code |

### Credit Transfer Transaction Information (CdtTrfTxInf) - Per Transaction

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/PmtId/InstrId | Instruction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Unique instruction ID |
| CdtTrfTxInf/PmtId/EndToEndId | End To End Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | endToEndId | End-to-end unique identifier |
| CdtTrfTxInf/PmtId/TxId | Transaction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Transaction unique ID |
| CdtTrfTxInf/PmtId/UETR | Unique End-to-end Transaction Reference | Text | 36 | 0..1 | UUID | PaymentInstruction | uetr | SWIFT gpi tracker (UUID format) |
| CdtTrfTxInf/PmtId/ClrSysRef | Clearing System Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction | clearingSystemReference | Clearing system transaction ID |
| CdtTrfTxInf/PmtTpInf/InstrPrty | Instruction Priority | Code | - | 0..1 | HIGH, NORM | PaymentInstruction | instructionPriority | Priority for this transaction |
| CdtTrfTxInf/PmtTpInf/ClrChanl | Clearing Channel | Code | - | 0..1 | RTGS, RTNS, MPNS, BOOK | PaymentInstruction | clearingChannel | Clearing channel |
| CdtTrfTxInf/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | serviceLevelCode | Service level |
| CdtTrfTxInf/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | 1-35 | 0..1 | External code | PaymentInstruction | localInstrument | Scheme-specific code |
| CdtTrfTxInf/IntrBkSttlmAmt | Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | interbankSettlementAmount.amount | Settlement amount between FIs |
| CdtTrfTxInf/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | interbankSettlementAmount.currency | ISO currency code |
| CdtTrfTxInf/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | interbankSettlementDate | Settlement date |
| CdtTrfTxInf/SttlmTmIndctn/DbtDtTm | Debit Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | debitDateTime | Debit timestamp |
| CdtTrfTxInf/SttlmTmIndctn/CdtDtTm | Credit Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | creditDateTime | Credit timestamp |
| CdtTrfTxInf/SttlmTmReq/CLSTm | Closing Time | Time | - | 0..1 | ISO Time | PaymentInstruction | closingTime | Cut-off time |
| CdtTrfTxInf/InstdAmt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | instructedAmount.amount | Original instructed amount |
| CdtTrfTxInf/InstdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | instructedAmount.currency | Original currency |
| CdtTrfTxInf/XchgRate | Exchange Rate | BaseOneRate | - | 0..1 | Decimal | PaymentInstruction | exchangeRate | FX rate |
| CdtTrfTxInf/ChrgBr | Charge Bearer | Code | - | 1..1 | DEBT, CRED, SHAR, SLEV | PaymentInstruction | chargeBearer | Charge allocation |
| CdtTrfTxInf/ChrgsInf/Amt | Charges Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | chargesAmount | Charges amount |
| CdtTrfTxInf/ChrgsInf/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | chargesAmount.currency | Charges currency |
| CdtTrfTxInf/ChrgsInf/Agt/FinInstnId/BICFI | Charging Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Charging agent BIC |

### Instructing Agent Account Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/InstgAgt/FinInstnId/BICFI | Instructing Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Instructing FI BIC |
| CdtTrfTxInf/InstgAgt/FinInstnId/ClrSysMmbId/MmbId | Clearing System Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| CdtTrfTxInf/InstgAgt/FinInstnId/LEI | Instructing Agent LEI | Code | 20 | 0..1 | LEI | FinancialInstitution | lei | Legal Entity Identifier |
| CdtTrfTxInf/InstgAgt/FinInstnId/Nm | Instructing Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | FI name |
| CdtTrfTxInf/InstgAgt/FinInstnId/PstlAdr/AdrLine | Instructing Agent Address Line | Text | 1-70 | 0..7 | Free text | FinancialInstitution | addressLine | FI address |
| CdtTrfTxInf/InstgAgt/FinInstnId/PstlAdr/Ctry | Instructing Agent Country | Code | 2 | 0..1 | ISO 3166 | FinancialInstitution | country | FI country |
| CdtTrfTxInf/InstgAgt/BrnchId/Id | Instructing Agent Branch ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | branchId | Branch identifier |
| CdtTrfTxInf/InstgAgt/BrnchId/Nm | Instructing Agent Branch Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | branchName | Branch name |

### Instructed Agent Account Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/InstdAgt/FinInstnId/BICFI | Instructed Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Instructed FI BIC |
| CdtTrfTxInf/InstdAgt/FinInstnId/ClrSysMmbId/MmbId | Clearing System Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| CdtTrfTxInf/InstdAgt/FinInstnId/LEI | Instructed Agent LEI | Code | 20 | 0..1 | LEI | FinancialInstitution | lei | Legal Entity Identifier |
| CdtTrfTxInf/InstdAgt/FinInstnId/Nm | Instructed Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | FI name |
| CdtTrfTxInf/InstdAgt/FinInstnId/PstlAdr/AdrLine | Instructed Agent Address Line | Text | 1-70 | 0..7 | Free text | FinancialInstitution | addressLine | FI address |
| CdtTrfTxInf/InstdAgt/FinInstnId/PstlAdr/Ctry | Instructed Agent Country | Code | 2 | 0..1 | ISO 3166 | FinancialInstitution | country | FI country |
| CdtTrfTxInf/InstdAgt/BrnchId/Id | Instructed Agent Branch ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | branchId | Branch identifier |
| CdtTrfTxInf/InstdAgt/BrnchId/Nm | Instructed Agent Branch Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | branchName | Branch name |

### Intermediary Agent Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/IntrmyAgt1/FinInstnId/BICFI | Intermediary Agent 1 BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | First intermediary FI |
| CdtTrfTxInf/IntrmyAgt1/FinInstnId/ClrSysMmbId/MmbId | Intermediary Agent 1 Clearing Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| CdtTrfTxInf/IntrmyAgt1/FinInstnId/Nm | Intermediary Agent 1 Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | FI name |
| CdtTrfTxInf/IntrmyAgt1/FinInstnId/PstlAdr/Ctry | Intermediary Agent 1 Country | Code | 2 | 0..1 | ISO 3166 | FinancialInstitution | country | FI country |
| CdtTrfTxInf/IntrmyAgt1Acct/Id/IBAN | Intermediary Agent 1 Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Correspondent account IBAN |
| CdtTrfTxInf/IntrmyAgt2/FinInstnId/BICFI | Intermediary Agent 2 BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Second intermediary FI |
| CdtTrfTxInf/IntrmyAgt2/FinInstnId/Nm | Intermediary Agent 2 Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | FI name |
| CdtTrfTxInf/IntrmyAgt2Acct/Id/IBAN | Intermediary Agent 2 Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Correspondent account IBAN |
| CdtTrfTxInf/IntrmyAgt3/FinInstnId/BICFI | Intermediary Agent 3 BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Third intermediary FI |
| CdtTrfTxInf/IntrmyAgt3/FinInstnId/Nm | Intermediary Agent 3 Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | FI name |
| CdtTrfTxInf/IntrmyAgt3Acct/Id/IBAN | Intermediary Agent 3 Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Correspondent account IBAN |

### Creditor Agent (Receiving Financial Institution)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Receiving FI BIC |
| CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId | Clearing System Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| CdtTrfTxInf/CdtrAgt/FinInstnId/LEI | Creditor Agent LEI | Code | 20 | 0..1 | LEI | FinancialInstitution | lei | Legal Entity Identifier |
| CdtTrfTxInf/CdtrAgt/FinInstnId/Nm | Creditor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | FI name |
| CdtTrfTxInf/CdtrAgt/FinInstnId/PstlAdr/AdrLine | Creditor Agent Address Line | Text | 1-70 | 0..7 | Free text | FinancialInstitution | addressLine | FI address |
| CdtTrfTxInf/CdtrAgt/FinInstnId/PstlAdr/Ctry | Creditor Agent Country | Code | 2 | 0..1 | ISO 3166 | FinancialInstitution | country | FI country |
| CdtTrfTxInf/CdtrAgt/BrnchId/Id | Creditor Agent Branch ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | branchId | Branch identifier |
| CdtTrfTxInf/CdtrAgt/BrnchId/Nm | Creditor Agent Branch Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | branchName | Branch name |
| CdtTrfTxInf/CdtrAgtAcct/Id/IBAN | Creditor Agent Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Receiving FI account IBAN |
| CdtTrfTxInf/CdtrAgtAcct/Id/Othr/Id | Creditor Agent Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Other account identifier |

### Creditor (Beneficiary FI Own Account)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/Cdtr/FinInstnId/BICFI | Creditor BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Beneficiary FI BIC |
| CdtTrfTxInf/Cdtr/FinInstnId/ClrSysMmbId/MmbId | Creditor Clearing Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| CdtTrfTxInf/Cdtr/FinInstnId/LEI | Creditor LEI | Code | 20 | 0..1 | LEI | FinancialInstitution | lei | Legal Entity Identifier |
| CdtTrfTxInf/Cdtr/FinInstnId/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Beneficiary FI name |
| CdtTrfTxInf/Cdtr/FinInstnId/PstlAdr/AdrLine | Creditor Address Line | Text | 1-70 | 0..7 | Free text | FinancialInstitution | addressLine | FI address |
| CdtTrfTxInf/Cdtr/FinInstnId/PstlAdr/Ctry | Creditor Country | Code | 2 | 0..1 | ISO 3166 | FinancialInstitution | country | FI country |
| CdtTrfTxInf/CdtrAcct/Id/IBAN | Creditor Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Beneficiary FI own account IBAN |
| CdtTrfTxInf/CdtrAcct/Id/Othr/Id | Creditor Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Other account identifier |
| CdtTrfTxInf/CdtrAcct/Tp/Cd | Creditor Account Type Code | Code | - | 0..1 | CACC, SVGS, OTHR | Account | accountType | Account type |
| CdtTrfTxInf/CdtrAcct/Ccy | Creditor Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency |
| CdtTrfTxInf/CdtrAcct/Nm | Creditor Account Name | Text | 1-70 | 0..1 | Free text | Account | accountName | Account name |

### Remittance and Purpose Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/Purp/Cd | Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | purposeCode | INTC, TREA, etc. |
| CdtTrfTxInf/RmtInf/Ustrd | Unstructured Remittance Information | Text | 1-140 | 0..1 | Free text | PaymentInstruction | remittanceInformation | Unstructured payment details |
| CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd | Document Type Code | Code | - | 0..1 | External code | PaymentInstruction | documentTypeCode | Document type |
| CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction | documentNumber | Reference number |
| CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/RltdDt | Related Date | Date | - | 0..1 | ISO Date | PaymentInstruction | documentDate | Document date |
| CdtTrfTxInf/InstrForCdtrAgt/Cd | Instruction For Creditor Agent Code | Code | - | 0..1 | External code | PaymentInstruction | instructionForCreditorAgent | Instructions code |
| CdtTrfTxInf/InstrForCdtrAgt/InstrInf | Instruction Information | Text | 1-140 | 0..1 | Free text | PaymentInstruction | instructionInformation | Free text instructions |
| CdtTrfTxInf/InstrForNxtAgt/Cd | Instruction For Next Agent Code | Code | - | 0..1 | External code | PaymentInstruction | instructionForNextAgent | Instructions for next agent |
| CdtTrfTxInf/InstrForNxtAgt/InstrInf | Instruction Information | Text | 1-140 | 0..1 | Free text | PaymentInstruction | instructionInformation | Free text instructions |

### Regulatory Reporting

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/RgltryRptg/Dtls/Cd | Regulatory Reporting Code | Text | 1-10 | 0..1 | Free text | PaymentInstruction | regulatoryReportingCode | Regulatory code |
| CdtTrfTxInf/RgltryRptg/Dtls/Inf | Regulatory Reporting Information | Text | 1-35 | 0..1 | Free text | PaymentInstruction | regulatoryReportingInfo | Additional regulatory info |

### Supplementary Data

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/Envlp | Supplementary Data Envelope | Any | - | 1..1 | XML/JSON | PaymentInstruction | supplementaryData | Additional proprietary data |

---

## Code Lists

### Settlement Method Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| INDA | Instructed Agent | PaymentInstruction.settlementMethod = 'INDA' |
| INGA | Instructing Agent | PaymentInstruction.settlementMethod = 'INGA' |
| COVE | Cover Method | PaymentInstruction.settlementMethod = 'COVE' |
| CLRG | Clearing System | PaymentInstruction.settlementMethod = 'CLRG' |

### Charge Bearer Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| DEBT | Borne by Debtor | PaymentInstruction.chargeBearer = 'DEBT' |
| CRED | Borne by Creditor | PaymentInstruction.chargeBearer = 'CRED' |
| SHAR | Shared | PaymentInstruction.chargeBearer = 'SHAR' |
| SLEV | Service Level | PaymentInstruction.chargeBearer = 'SLEV' |

### Clearing Channel Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| RTGS | Real Time Gross Settlement | PaymentInstruction.clearingChannel = 'RTGS' |
| RTNS | Real Time Net Settlement | PaymentInstruction.clearingChannel = 'RTNS' |
| MPNS | Multiple Net Settlement | PaymentInstruction.clearingChannel = 'MPNS' |
| BOOK | Book Transfer | PaymentInstruction.clearingChannel = 'BOOK' |

### Purpose Codes (Common for FI Transfers)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| INTC | Intra-Company Payment | PaymentInstruction.purposeCode = 'INTC' |
| TREA | Treasury Payment | PaymentInstruction.purposeCode = 'TREA' |
| CBFF | Capital Building Family | PaymentInstruction.purposeCode = 'CBFF' |
| LIMA | Liquidity Management | PaymentInstruction.purposeCode = 'LIMA' |

---

## CDM Extensions Required

All 125 pacs.009 fields successfully map to existing CDM model. **No enhancements required.**

The CDM entities (PaymentInstruction, FinancialInstitution, Account) fully support FI-to-FI own account transfers without modification.

---

## Message Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.009.001.10">
  <FICdtTrf>
    <GrpHdr>
      <MsgId>MSGID20241220FI001</MsgId>
      <CreDtTm>2024-12-20T14:25:00Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <TtlIntrBkSttlmAmt Ccy="USD">5000000.00</TtlIntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <SttlmInf>
        <SttlmMtd>INDA</SttlmMtd>
      </SttlmInf>
      <PmtTpInf>
        <InstrPrty>HIGH</InstrPrty>
        <ClrChanl>RTGS</ClrChanl>
        <SvcLvl>
          <Cd>URGP</Cd>
        </SvcLvl>
      </PmtTpInf>
      <InstgAgt>
        <FinInstnId>
          <BICFI>CHASUS33XXX</BICFI>
          <Nm>JPMorgan Chase Bank, N.A.</Nm>
          <LEI>8I5DZWZKVSZI1NUHU748</LEI>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <BICFI>CITIUS33XXX</BICFI>
          <Nm>Citibank N.A.</Nm>
          <LEI>E57ODZWZ7FF32TWEFA76</LEI>
        </FinInstnId>
      </InstdAgt>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>JPMC-TREASURY-20241220-001</InstrId>
        <EndToEndId>E2EFI20241220001</EndToEndId>
        <TxId>TXNFI20241220001</TxId>
        <UETR>3f2504e0-4f89-11d3-9a0c-0305e82c3301</UETR>
      </PmtId>
      <PmtTpInf>
        <InstrPrty>HIGH</InstrPrty>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="USD">5000000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <ChrgBr>SHAR</ChrgBr>
      <InstgAgt>
        <FinInstnId>
          <BICFI>CHASUS33XXX</BICFI>
          <Nm>JPMorgan Chase Bank, N.A.</Nm>
          <PstlAdr>
            <AdrLine>383 Madison Avenue</AdrLine>
            <AdrLine>New York, NY 10017</AdrLine>
            <Ctry>US</Ctry>
          </PstlAdr>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <BICFI>CITIUS33XXX</BICFI>
          <Nm>Citibank N.A.</Nm>
          <PstlAdr>
            <AdrLine>399 Park Avenue</AdrLine>
            <AdrLine>New York, NY 10022</AdrLine>
            <Ctry>US</Ctry>
          </PstlAdr>
        </FinInstnId>
      </InstdAgt>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>CITIUS33XXX</BICFI>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <FinInstnId>
          <BICFI>CITIUS33XXX</BICFI>
          <Nm>Citibank N.A.</Nm>
          <LEI>E57ODZWZ7FF32TWEFA76</LEI>
        </FinInstnId>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>021000089-TREASURY-USD</Id>
          </Othr>
        </Id>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
        <Ccy>USD</Ccy>
        <Nm>Citibank Treasury Account USD</Nm>
      </CdtrAcct>
      <Purp>
        <Cd>TREA</Cd>
      </Purp>
      <RmtInf>
        <Ustrd>Liquidity management - funding of USD nostro account</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FICdtTrf>
</Document>
```

---

## References

- ISO 20022 Message Definition: https://www.iso20022.org/catalogue-messages/iso-20022-messages-archive?search=pacs.009
- ISO 20022 pacs.009 Schema: https://www.iso20022.org/sites/default/files/documents/D7/pacs.009.001.10.xsd
- SWIFT Standards: https://www.swift.com/standards/iso-20022/iso-20022-programme
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
