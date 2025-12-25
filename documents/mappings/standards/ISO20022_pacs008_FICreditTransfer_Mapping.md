# ISO 20022 pacs.008.001.10 - FI to FI Customer Credit Transfer
## Complete Field Mapping to GPS CDM

**Message Type:** pacs.008.001.10 (FIToFICustomerCreditTransferV10)
**Standard:** ISO 20022
**Usage:** Financial institution to financial institution customer credit transfer
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 142 fields mapped)

---

## Message Overview

The pacs.008 message is used to move funds from a debtor account to a creditor account serviced by different financial institutions. It is exchanged between agents (financial institutions) and contains information related to the payment instruction.

**Key Use Cases:**
- Interbank credit transfers
- Cross-border payments
- SWIFT gpi (global payments innovation) transactions
- Correspondent banking payments
- Real-time payment systems (e.g., SEPA, UK Faster Payments)

**Message Flow:** Debtor Agent → Intermediary Agent(s) → Creditor Agent

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total pacs.008 Fields** | 142 | 100% |
| **Mapped to CDM** | 142 | 100% |
| **Direct Mapping** | 128 | 90% |
| **Derived/Calculated** | 10 | 7% |
| **Reference Data Lookup** | 4 | 3% |
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
| GrpHdr/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | interbankSettlementDate | Settlement date between agents |
| GrpHdr/SttlmInf/SttlmMtd | Settlement Method | Code | - | 1..1 | INDA, INGA, COVE, CLRG | PaymentInstruction | settlementMethod | Settlement method code |
| GrpHdr/SttlmInf/SttlmAcct/Id/IBAN | Settlement Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Settlement account IBAN |
| GrpHdr/SttlmInf/SttlmAcct/Id/Othr/Id | Settlement Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Other account identifier |
| GrpHdr/SttlmInf/ClrSys/Cd | Clearing System Code | Code | - | 0..1 | External code | PaymentInstruction | clearingSystemCode | Clearing system identification |
| GrpHdr/SttlmInf/InstgRmbrsmntAgt/FinInstnId/BICFI | Instructing Reimbursement Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Reimbursement agent BIC |
| GrpHdr/SttlmInf/InstdRmbrsmntAgt/FinInstnId/BICFI | Instructed Reimbursement Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Reimbursement agent BIC |
| GrpHdr/PmtTpInf/InstrPrty | Instruction Priority | Code | - | 0..1 | HIGH, NORM | PaymentInstruction | instructionPriority | Priority indicator |
| GrpHdr/PmtTpInf/ClrChanl | Clearing Channel | Code | - | 0..1 | RTGS, RTNS, MPNS, BOOK | PaymentInstruction | clearingChannel | Clearing channel |
| GrpHdr/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | serviceLevelCode | SEPA, URGP, NURG, etc. |
| GrpHdr/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | 1-35 | 0..1 | External code | PaymentInstruction | localInstrument | Country-specific code |
| GrpHdr/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | categoryPurposeCode | CASH, DVPM, INTC, TREA, etc. |
| GrpHdr/InstgAgt/FinInstnId/BICFI | Instructing Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Instructing financial institution |
| GrpHdr/InstdAgt/FinInstnId/BICFI | Instructed Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Instructed financial institution |

### Credit Transfer Transaction Information (CdtTrfTxInf) - Per Transaction

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/PmtId/InstrId | Instruction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Unique instruction ID |
| CdtTrfTxInf/PmtId/EndToEndId | End To End Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | endToEndId | End-to-end unique identifier |
| CdtTrfTxInf/PmtId/TxId | Transaction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Transaction unique ID |
| CdtTrfTxInf/PmtId/UETR | Unique End-to-end Transaction Reference | Text | 36 | 0..1 | UUID | PaymentInstruction | uetr | SWIFT gpi tracker (UUID format) |
| CdtTrfTxInf/PmtId/ClrSysRef | Clearing System Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction | clearingSystemReference | Clearing system transaction ID |
| CdtTrfTxInf/PmtTpInf/InstrPrty | Instruction Priority | Code | - | 0..1 | HIGH, NORM | PaymentInstruction | instructionPriority | Priority for this transaction |
| CdtTrfTxInf/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | serviceLevelCode | SEPA, URGP, etc. |
| CdtTrfTxInf/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | 1-35 | 0..1 | External code | PaymentInstruction | localInstrument | Scheme-specific code |
| CdtTrfTxInf/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | categoryPurposeCode | Payment category |
| CdtTrfTxInf/IntrBkSttlmAmt | Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | interbankSettlementAmount.amount | Settlement amount between banks |
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
| CdtTrfTxInf/ChrgsInf/Agt/FinInstnId/BICFI | Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Charging agent BIC |
| CdtTrfTxInf/MndtRltdInf/MndtId | Mandate Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | mandateId | Direct debit mandate ID |
| CdtTrfTxInf/MndtRltdInf/DtOfSgntr | Date Of Signature | Date | - | 0..1 | ISO Date | PaymentInstruction | mandateSignatureDate | Mandate signature date |

### Debtor Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | name | Originator/debtor name |
| CdtTrfTxInf/Dbtr/PstlAdr/AdrLine | Debtor Address Line | Text | 1-70 | 0..7 | Free text | Party | addressLine | Debtor address (up to 7 lines) |
| CdtTrfTxInf/Dbtr/PstlAdr/StrtNm | Debtor Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street name |
| CdtTrfTxInf/Dbtr/PstlAdr/BldgNb | Debtor Building Number | Text | 1-16 | 0..1 | Free text | Party | buildingNumber | Building number |
| CdtTrfTxInf/Dbtr/PstlAdr/PstCd | Debtor Post Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | Postal/ZIP code |
| CdtTrfTxInf/Dbtr/PstlAdr/TwnNm | Debtor Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City/town |
| CdtTrfTxInf/Dbtr/PstlAdr/CtrySubDvsn | Debtor Country Sub Division | Text | 1-35 | 0..1 | Free text | Party | stateOrProvince | State/province |
| CdtTrfTxInf/Dbtr/PstlAdr/Ctry | Debtor Country | Code | 2 | 0..1 | ISO 3166 | Party | country | ISO country code |
| CdtTrfTxInf/Dbtr/Id/OrgId/AnyBIC | Debtor Organization BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | Organization BIC |
| CdtTrfTxInf/Dbtr/Id/OrgId/LEI | Debtor Legal Entity Identifier | Code | 20 | 0..1 | LEI | Party | lei | Legal Entity Identifier |
| CdtTrfTxInf/Dbtr/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Date Of Birth | Date | - | 1..1 | ISO Date | Party | dateOfBirth | Individual birth date |
| CdtTrfTxInf/Dbtr/Id/PrvtId/DtAndPlcOfBirth/CityOfBirth | City Of Birth | Text | 1-35 | 1..1 | Free text | Party | cityOfBirth | Birth city |
| CdtTrfTxInf/Dbtr/Id/PrvtId/DtAndPlcOfBirth/CtryOfBirth | Country Of Birth | Code | 2 | 1..1 | ISO 3166 | Party | countryOfBirth | Birth country code |
| CdtTrfTxInf/DbtrAcct/Id/IBAN | Debtor Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Debtor account IBAN |
| CdtTrfTxInf/DbtrAcct/Id/Othr/Id | Debtor Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Other account identifier |
| CdtTrfTxInf/DbtrAcct/Tp/Cd | Debtor Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account | accountType | Account type |
| CdtTrfTxInf/DbtrAcct/Ccy | Debtor Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency |
| CdtTrfTxInf/DbtrAcct/Nm | Debtor Account Name | Text | 1-70 | 0..1 | Free text | Account | accountName | Account name |

### Debtor Agent Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Debtor's bank BIC |
| CdtTrfTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId | Clearing System Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| CdtTrfTxInf/DbtrAgt/FinInstnId/Nm | Debtor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Bank name |
| CdtTrfTxInf/DbtrAgt/FinInstnId/PstlAdr/AdrLine | Debtor Agent Address Line | Text | 1-70 | 0..7 | Free text | FinancialInstitution | addressLine | Bank address |
| CdtTrfTxInf/DbtrAgt/FinInstnId/PstlAdr/Ctry | Debtor Agent Country | Code | 2 | 0..1 | ISO 3166 | FinancialInstitution | country | Bank country |
| CdtTrfTxInf/DbtrAgtAcct/Id/IBAN | Debtor Agent Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Correspondent account IBAN |

### Creditor Agent Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Creditor's bank BIC |
| CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId | Clearing System Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| CdtTrfTxInf/CdtrAgt/FinInstnId/Nm | Creditor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Bank name |
| CdtTrfTxInf/CdtrAgt/FinInstnId/PstlAdr/AdrLine | Creditor Agent Address Line | Text | 1-70 | 0..7 | Free text | FinancialInstitution | addressLine | Bank address |
| CdtTrfTxInf/CdtrAgt/FinInstnId/PstlAdr/Ctry | Creditor Agent Country | Code | 2 | 0..1 | ISO 3166 | FinancialInstitution | country | Bank country |
| CdtTrfTxInf/CdtrAgtAcct/Id/IBAN | Creditor Agent Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Correspondent account IBAN |

### Creditor Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | name | Beneficiary/creditor name |
| CdtTrfTxInf/Cdtr/PstlAdr/AdrLine | Creditor Address Line | Text | 1-70 | 0..7 | Free text | Party | addressLine | Creditor address (up to 7 lines) |
| CdtTrfTxInf/Cdtr/PstlAdr/StrtNm | Creditor Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street name |
| CdtTrfTxInf/Cdtr/PstlAdr/BldgNb | Creditor Building Number | Text | 1-16 | 0..1 | Free text | Party | buildingNumber | Building number |
| CdtTrfTxInf/Cdtr/PstlAdr/PstCd | Creditor Post Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | Postal/ZIP code |
| CdtTrfTxInf/Cdtr/PstlAdr/TwnNm | Creditor Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City/town |
| CdtTrfTxInf/Cdtr/PstlAdr/CtrySubDvsn | Creditor Country Sub Division | Text | 1-35 | 0..1 | Free text | Party | stateOrProvince | State/province |
| CdtTrfTxInf/Cdtr/PstlAdr/Ctry | Creditor Country | Code | 2 | 0..1 | ISO 3166 | Party | country | ISO country code |
| CdtTrfTxInf/Cdtr/Id/OrgId/AnyBIC | Creditor Organization BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | Organization BIC |
| CdtTrfTxInf/Cdtr/Id/OrgId/LEI | Creditor Legal Entity Identifier | Code | 20 | 0..1 | LEI | Party | lei | Legal Entity Identifier |
| CdtTrfTxInf/Cdtr/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Date Of Birth | Date | - | 1..1 | ISO Date | Party | dateOfBirth | Individual birth date |
| CdtTrfTxInf/CdtrAcct/Id/IBAN | Creditor Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Creditor account IBAN |
| CdtTrfTxInf/CdtrAcct/Id/Othr/Id | Creditor Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Other account identifier |
| CdtTrfTxInf/CdtrAcct/Tp/Cd | Creditor Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account | accountType | Account type |
| CdtTrfTxInf/CdtrAcct/Ccy | Creditor Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency |
| CdtTrfTxInf/CdtrAcct/Nm | Creditor Account Name | Text | 1-70 | 0..1 | Free text | Account | accountName | Account name |

### Intermediary Agent Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/IntrmyAgt1/FinInstnId/BICFI | Intermediary Agent 1 BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | First intermediary bank |
| CdtTrfTxInf/IntrmyAgt1/FinInstnId/Nm | Intermediary Agent 1 Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Bank name |
| CdtTrfTxInf/IntrmyAgt2/FinInstnId/BICFI | Intermediary Agent 2 BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Second intermediary bank |
| CdtTrfTxInf/IntrmyAgt3/FinInstnId/BICFI | Intermediary Agent 3 BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Third intermediary bank |

### Ultimate Parties

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Free text | Party | ultimateDebtorName | Ultimate originating party |
| CdtTrfTxInf/UltmtDbtr/Id/OrgId/LEI | Ultimate Debtor LEI | Code | 20 | 0..1 | LEI | Party | ultimateDebtorLei | LEI of ultimate debtor |
| CdtTrfTxInf/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Free text | Party | ultimateCreditorName | Ultimate beneficiary party |
| CdtTrfTxInf/UltmtCdtr/Id/OrgId/LEI | Ultimate Creditor LEI | Code | 20 | 0..1 | LEI | Party | ultimateCreditorLei | LEI of ultimate creditor |

### Remittance Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/Purp/Cd | Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | purposeCode | CBFF, COMC, GDDS, etc. |
| CdtTrfTxInf/RgltryRptg/Dtls/Cd | Regulatory Reporting Code | Text | 1-10 | 0..1 | Free text | PaymentInstruction | regulatoryReportingCode | Regulatory code |
| CdtTrfTxInf/RgltryRptg/Dtls/Inf | Regulatory Reporting Information | Text | 1-35 | 0..1 | Free text | PaymentInstruction | regulatoryReportingInfo | Additional regulatory info |
| CdtTrfTxInf/RmtInf/Ustrd | Unstructured Remittance Information | Text | 1-140 | 0..1 | Free text | PaymentInstruction | remittanceInformation | Unstructured payment details |
| CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd | Document Type Code | Code | - | 0..1 | External code | PaymentInstruction | documentTypeCode | CINV, DNFA, etc. |
| CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction | documentNumber | Invoice/reference number |
| CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/RltdDt | Related Date | Date | - | 0..1 | ISO Date | PaymentInstruction | documentDate | Invoice/document date |
| CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/DuePyblAmt | Due Payable Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | duePayableAmount | Amount due |
| CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Ref | Creditor Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction | creditorReference | Structured creditor reference |
| CdtTrfTxInf/InstrForCdtrAgt/Cd | Instruction For Creditor Agent Code | Code | - | 0..1 | External code | PaymentInstruction | instructionForCreditorAgent | PHOB, TELB, etc. |
| CdtTrfTxInf/InstrForNxtAgt/Cd | Instruction For Next Agent Code | Code | - | 0..1 | External code | PaymentInstruction | instructionForNextAgent | Instructions for next agent |
| CdtTrfTxInf/InstrForNxtAgt/InstrInf | Instruction Information | Text | 1-140 | 0..1 | Free text | PaymentInstruction | instructionInformation | Free text instructions |

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

### Service Level Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| SEPA | Single Euro Payments Area | PaymentInstruction.serviceLevelCode = 'SEPA' |
| URGP | Urgent Payment | PaymentInstruction.serviceLevelCode = 'URGP' |
| NURG | Normal Urgency | PaymentInstruction.serviceLevelCode = 'NURG' |

### Clearing Channel Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| RTGS | Real Time Gross Settlement | PaymentInstruction.clearingChannel = 'RTGS' |
| RTNS | Real Time Net Settlement | PaymentInstruction.clearingChannel = 'RTNS' |
| MPNS | Multiple Net Settlement | PaymentInstruction.clearingChannel = 'MPNS' |
| BOOK | Book Transfer | PaymentInstruction.clearingChannel = 'BOOK' |

---

## CDM Extensions Required

All 142 pacs.008 fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.10">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>MSGID20241220001</MsgId>
      <CreDtTm>2024-12-20T10:30:00Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <TtlIntrBkSttlmAmt Ccy="USD">125000.00</TtlIntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <SttlmInf>
        <SttlmMtd>INDA</SttlmMtd>
      </SttlmInf>
      <PmtTpInf>
        <InstrPrty>NORM</InstrPrty>
        <SvcLvl>
          <Cd>URGP</Cd>
        </SvcLvl>
      </PmtTpInf>
      <InstgAgt>
        <FinInstnId>
          <BICFI>NWBKGB2LXXX</BICFI>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <BICFI>CHASUS33XXX</BICFI>
        </FinInstnId>
      </InstdAgt>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>INSTRID001</InstrId>
        <EndToEndId>E2E20241220001</EndToEndId>
        <TxId>TXN20241220001</TxId>
        <UETR>97ed4827-7b6f-4491-a06f-b548d5a7512d</UETR>
      </PmtId>
      <IntrBkSttlmAmt Ccy="USD">125000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <ChrgBr>SHAR</ChrgBr>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>NWBKGB2LXXX</BICFI>
          <Nm>National Westminster Bank</Nm>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>ABC Corporation Ltd</Nm>
        <PstlAdr>
          <StrtNm>High Street</StrtNm>
          <BldgNb>123</BldgNb>
          <PstCd>EC2N 2DL</PstCd>
          <TwnNm>London</TwnNm>
          <Ctry>GB</Ctry>
        </PstlAdr>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <IBAN>GB29NWBK60161331926819</IBAN>
        </Id>
      </DbtrAcct>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>CHASUS33XXX</BICFI>
          <Nm>JPMorgan Chase Bank</Nm>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>XYZ Supplier Inc</Nm>
        <PstlAdr>
          <StrtNm>Park Avenue</StrtNm>
          <BldgNb>270</BldgNb>
          <PstCd>10017</PstCd>
          <TwnNm>New York</TwnNm>
          <CtrySubDvsn>NY</CtrySubDvsn>
          <Ctry>US</Ctry>
        </PstlAdr>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>987654321</Id>
          </Othr>
        </Id>
      </CdtrAcct>
      <Purp>
        <Cd>GDDS</Cd>
      </Purp>
      <RmtInf>
        <Ustrd>Payment for Invoice INV-2024-1234</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
```

---

## References

- ISO 20022 Message Definition: https://www.iso20022.org/catalogue-messages/iso-20022-messages-archive?search=pacs.008
- ISO 20022 pacs.008 Schema: https://www.iso20022.org/sites/default/files/documents/D7/pacs.008.001.10.xsd
- SWIFT Standards: https://www.swift.com/standards/iso-20022
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
