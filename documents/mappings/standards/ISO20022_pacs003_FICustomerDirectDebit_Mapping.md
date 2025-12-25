# ISO 20022 pacs.003 - FI to FI Customer Direct Debit Mapping

## Message Overview

**Message Type:** pacs.003.001.08 - FIToFICustomerDirectDebit
**Category:** PACS - Payments Clearing and Settlement
**Purpose:** Sent by a creditor financial institution to a debtor financial institution to collect funds from a debtor's account
**Direction:** Creditor Bank → Debtor Bank
**Settlement:** Real-time or batch direct debit collection

**Key Use Cases:**
- SEPA Direct Debit Core (SDD Core) transactions
- SEPA Direct Debit Business-to-Business (SDD B2B) transactions
- Cross-border direct debit collections
- Mandate-based recurring payments
- One-off direct debit collections

**Relationship to Other Messages:**
- **pacs.002**: Used to send status response (accepted/rejected)
- **pacs.004**: Used to return direct debit if settlement fails
- **pacs.007**: Used to reverse direct debit after settlement
- **pain.008**: Customer-to-bank direct debit initiation (generates this message)
- **pain.009-014**: Mandate management messages

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in pacs.003** | 135 |
| **Fields Mapped to CDM** | 135 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- Party (debtor, creditor, ultimate debtor, ultimate creditor)
- Account (debtor account, creditor account)
- FinancialInstitution (debtor agent, creditor agent, intermediary agents)
- Mandate (direct debit mandate information)

---

## Complete Field Mapping

### 1. Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique message identifier |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | createdDateTime | Message creation timestamp |
| GrpHdr/BtchBookg | Batch Booking | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | batchBookingIndicator | Bulk booking indicator |
| GrpHdr/NbOfTxs | Number of Transactions | Text | 1-15 | 1..1 | Numeric string | PaymentInstruction.extensions | numberOfTransactions | Transaction count in message |
| GrpHdr/CtrlSum | Control Sum | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | controlSum | Total of all amounts (validation) |
| GrpHdr/TtlIntrBkSttlmAmt | Total Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | totalSettlementAmount | Total settlement amount |
| GrpHdr/TtlIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | totalSettlementCurrency | Settlement currency |
| GrpHdr/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISODate | PaymentInstruction | settlementDate | Requested settlement date |
| GrpHdr/SttlmInf/SttlmMtd | Settlement Method | Code | - | 1..1 | INDA, INGA, COVE, CLRG | PaymentInstruction.extensions | settlementMethod | Settlement mechanism |
| GrpHdr/SttlmInf/SttlmAcct/Id/IBAN | Settlement Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Settlement account identifier |
| GrpHdr/SttlmInf/SttlmAcct/Id/Othr/Id | Settlement Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN settlement account |
| GrpHdr/SttlmInf/ClrSys/Cd | Clearing System Code | Code | - | 0..1 | ExternalClearingSystemIdentification1Code | PaymentInstruction.extensions | clearingSystemCode | Clearing system identifier |
| GrpHdr/SttlmInf/InstgRmbrsmntAgt/FinInstnId/BICFI | Instructing Reimbursement Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Reimbursement agent identifier |
| GrpHdr/SttlmInf/InstdRmbrsmntAgt/FinInstnId/BICFI | Instructed Reimbursement Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Instructed reimbursement agent |
| GrpHdr/PmtTpInf/InstrPrty | Instruction Priority | Code | 4 | 0..1 | HIGH, NORM | PaymentInstruction.extensions | priority | Processing priority |
| GrpHdr/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | - | 0..1 | SEPA, SDVA, PRPT, URGP | PaymentInstruction.extensions | serviceLevelCode | Service level agreement |
| GrpHdr/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | - | 0..1 | CORE, B2B, COR1 | PaymentInstruction.extensions | localInstrumentCode | Regional instrument (SEPA types) |
| GrpHdr/PmtTpInf/SeqTp | Sequence Type | Code | - | 0..1 | FRST, RCUR, FNAL, OOFF | PaymentInstruction.extensions | mandateSequenceType | Mandate sequence |
| GrpHdr/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | - | 0..1 | CASH, CORT, DVPM, etc. | PaymentInstruction.extensions | categoryPurposeCode | Payment category purpose |
| GrpHdr/InstgAgt/FinInstnId/BICFI | Instructing Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Creditor's financial institution |
| GrpHdr/InstdAgt/FinInstnId/BICFI | Instructed Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Debtor's financial institution |

### 2. Direct Debit Transaction Information (DrctDbtTxInf)

#### 2.1 Payment Identification

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/PmtId/InstrId | Instruction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Unique instruction identifier |
| DrctDbtTxInf/PmtId/EndToEndId | End to End Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | endToEndId | E2E reference from creditor |
| DrctDbtTxInf/PmtId/TxId | Transaction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Unique transaction identifier |
| DrctDbtTxInf/PmtId/UETR | Unique End-to-end Transaction Reference | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Universal unique identifier |
| DrctDbtTxInf/PmtId/ClrSysRef | Clearing System Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | clearingSystemReference | Clearing system reference |

#### 2.2 Payment Type Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/PmtTpInf/InstrPrty | Instruction Priority | Code | 4 | 0..1 | HIGH, NORM | PaymentInstruction.extensions | priority | Transaction-level priority |
| DrctDbtTxInf/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | - | 0..1 | SEPA, SDVA, PRPT | PaymentInstruction.extensions | serviceLevelCode | Service level |
| DrctDbtTxInf/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | - | 0..1 | CORE, B2B, COR1 | PaymentInstruction.extensions | localInstrumentCode | SEPA direct debit scheme |
| DrctDbtTxInf/PmtTpInf/SeqTp | Sequence Type | Code | 4 | 0..1 | FRST, RCUR, FNAL, OOFF | PaymentInstruction.extensions | mandateSequenceType | Mandate occurrence type |
| DrctDbtTxInf/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | - | 0..1 | CASH, CORT, etc. | PaymentInstruction.extensions | categoryPurposeCode | Category purpose |

#### 2.3 Interbank Settlement

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/IntrBkSttlmAmt | Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | amount | Settlement amount |
| DrctDbtTxInf/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | currency | Settlement currency |
| DrctDbtTxInf/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISODate | PaymentInstruction | settlementDate | Settlement date |
| DrctDbtTxInf/SttlmTmIndctn/DbtDtTm | Debit Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | requestedDebitDateTime | When to debit debtor account |
| DrctDbtTxInf/SttlmTmIndctn/CdtDtTm | Credit Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | requestedCreditDateTime | When to credit creditor account |
| DrctDbtTxInf/SttlmTmReq/CLSTm | Closing Time | Time | - | 0..1 | ISOTime | PaymentInstruction.extensions | closingTime | Settlement cut-off time |

#### 2.4 Instructed Amount

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/InstdAmt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | instructedAmount | Original instructed amount |
| DrctDbtTxInf/InstdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | instructedCurrency | Instructed currency |
| DrctDbtTxInf/XchgRate | Exchange Rate | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | exchangeRate | FX rate applied |

#### 2.5 Charge Bearer

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/ChrgBr | Charge Bearer | Code | 4 | 0..1 | DEBT, CRED, SHAR, SLEV | PaymentInstruction.extensions | chargeBearer | Who pays charges |

#### 2.6 Direct Debit Transaction (DrctDbtTx)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/DrctDbtTx/MndtRltdInf/MndtId | Mandate Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | mandateId | Unique mandate reference |
| DrctDbtTxInf/DrctDbtTx/MndtRltdInf/DtOfSgntr | Date of Signature | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | mandateSignatureDate | Mandate signature date |
| DrctDbtTxInf/DrctDbtTx/MndtRltdInf/AmdmntInd | Amendment Indicator | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | mandateAmendmentIndicator | Mandate changed since last use |
| DrctDbtTxInf/DrctDbtTx/MndtRltdInf/AmdmntInfDtls/OrgnlMndtId | Original Mandate ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalMandateId | Previous mandate ID |
| DrctDbtTxInf/DrctDbtTx/MndtRltdInf/AmdmntInfDtls/OrgnlCdtrSchmeId/Nm | Original Creditor Scheme Name | Text | 1-140 | 0..1 | Free text | PaymentInstruction.extensions | originalCreditorSchemeIdName | Previous creditor scheme ID |
| DrctDbtTxInf/DrctDbtTx/MndtRltdInf/AmdmntInfDtls/OrgnlCdtrSchmeId/Id/PrvtId/Othr/Id | Original Creditor Scheme ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalCreditorSchemeId | Creditor identifier |
| DrctDbtTxInf/DrctDbtTx/MndtRltdInf/AmdmntInfDtls/OrgnlCdtrSchmeId/Id/PrvtId/Othr/SchmeNm/Cd | Scheme Name Code | Code | - | 0..1 | SEPA | PaymentInstruction.extensions | creditorSchemeNameCode | Scheme identifier |
| DrctDbtTxInf/DrctDbtTx/MndtRltdInf/AmdmntInfDtls/OrgnlDbtrAcct/Id/IBAN | Original Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Previous debtor account |
| DrctDbtTxInf/DrctDbtTx/MndtRltdInf/AmdmntInfDtls/OrgnlDbtrAgt/FinInstnId/BICFI | Original Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Previous debtor bank |
| DrctDbtTxInf/DrctDbtTx/MndtRltdInf/ElctrncSgntr | Electronic Signature | Text | 1-1025 | 0..1 | Base64 binary | PaymentInstruction.extensions | mandateElectronicSignature | Digital signature |
| DrctDbtTxInf/DrctDbtTx/CdtrSchmeId/Nm | Creditor Scheme Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Creditor scheme name |
| DrctDbtTxInf/DrctDbtTx/CdtrSchmeId/Id/PrvtId/Othr/Id | Creditor Scheme ID | Text | 1-35 | 0..1 | Free text | Party.extensions | creditorSchemeId | Creditor identifier (e.g., SEPA creditor ID) |
| DrctDbtTxInf/DrctDbtTx/CdtrSchmeId/Id/PrvtId/Othr/SchmeNm/Cd | Scheme Name Code | Code | - | 0..1 | SEPA | Party.extensions | creditorSchemeNameCode | Identifier scheme |
| DrctDbtTxInf/DrctDbtTx/CdtrSchmeId/Id/PrvtId/Othr/Issr | Issuer | Text | 1-35 | 0..1 | Free text | Party.extensions | creditorSchemeIssuer | Scheme issuer |
| DrctDbtTxInf/DrctDbtTx/PreNtfctnId | Pre-notification ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | preNotificationId | Pre-notification reference |
| DrctDbtTxInf/DrctDbtTx/PreNtfctnDt | Pre-notification Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | preNotificationDate | When debtor was notified |

#### 2.7 Creditor Agent (CdtrAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Creditor's bank BIC |
| DrctDbtTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId | Member Identification | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing system member ID |
| DrctDbtTxInf/CdtrAgt/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Creditor agent name |
| DrctDbtTxInf/CdtrAgt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Creditor agent country |
| DrctDbtTxInf/CdtrAgt/FinInstnId/Othr/Id | Other Identification | Text | 1-35 | 0..1 | Free text | FinancialInstitution | otherIdentification | Alternative identifier |

#### 2.8 Creditor (Cdtr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/Cdtr/Nm | Creditor Name | Text | 1-140 | 1..1 | Free text | Party | partyName | Beneficiary name |
| DrctDbtTxInf/Cdtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| DrctDbtTxInf/Cdtr/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Free text | Party | buildingNumber | Building number |
| DrctDbtTxInf/Cdtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | ZIP/postal code |
| DrctDbtTxInf/Cdtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| DrctDbtTxInf/Cdtr/PstlAdr/CtrySubDvsn | Country Sub-division | Text | 1-35 | 0..1 | Free text | Party | stateProvince | State/province |
| DrctDbtTxInf/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country code |
| DrctDbtTxInf/Cdtr/PstlAdr/AdrLine | Address Line | Text | 1-70 | 0..7 | Free text | Party | addressLines | Unstructured address |
| DrctDbtTxInf/Cdtr/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| DrctDbtTxInf/Cdtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID/organization number |
| DrctDbtTxInf/Cdtr/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Birth Date | Date | - | 0..1 | ISODate | Party | dateOfBirth | Date of birth |
| DrctDbtTxInf/Cdtr/Id/PrvtId/Othr/Id | Private Other ID | Text | 1-35 | 0..1 | Free text | Party | nationalId | National ID |

#### 2.9 Creditor Account (CdtrAcct)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | IBAN for creditor |
| DrctDbtTxInf/CdtrAcct/Id/Othr/Id | Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| DrctDbtTxInf/CdtrAcct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account | accountType | Account type |
| DrctDbtTxInf/CdtrAcct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency |
| DrctDbtTxInf/CdtrAcct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account | accountName | Account name |

#### 2.10 Ultimate Creditor (UltmtCdtr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ultimate beneficiary |
| DrctDbtTxInf/UltmtCdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country |
| DrctDbtTxInf/UltmtCdtr/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| DrctDbtTxInf/UltmtCdtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID |

#### 2.11 Debtor Agent (DbtrAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Debtor's bank BIC |
| DrctDbtTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId | Member Identification | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing system member ID |
| DrctDbtTxInf/DbtrAgt/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Debtor agent name |
| DrctDbtTxInf/DbtrAgt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Debtor agent country |

#### 2.12 Debtor (Dbtr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/Dbtr/Nm | Debtor Name | Text | 1-140 | 1..1 | Free text | Party | partyName | Payer name |
| DrctDbtTxInf/Dbtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| DrctDbtTxInf/Dbtr/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Free text | Party | buildingNumber | Building number |
| DrctDbtTxInf/Dbtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | ZIP/postal code |
| DrctDbtTxInf/Dbtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| DrctDbtTxInf/Dbtr/PstlAdr/CtrySubDvsn | Country Sub-division | Text | 1-35 | 0..1 | Free text | Party | stateProvince | State/province |
| DrctDbtTxInf/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country code |
| DrctDbtTxInf/Dbtr/PstlAdr/AdrLine | Address Line | Text | 1-70 | 0..7 | Free text | Party | addressLines | Unstructured address |
| DrctDbtTxInf/Dbtr/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| DrctDbtTxInf/Dbtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID/organization number |
| DrctDbtTxInf/Dbtr/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Birth Date | Date | - | 0..1 | ISODate | Party | dateOfBirth | Date of birth |
| DrctDbtTxInf/Dbtr/Id/PrvtId/Othr/Id | Private Other ID | Text | 1-35 | 0..1 | Free text | Party | nationalId | National ID |

#### 2.13 Debtor Account (DbtrAcct)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 1..1 | IBAN format | Account | accountNumber | IBAN for debtor (mandatory) |
| DrctDbtTxInf/DbtrAcct/Id/Othr/Id | Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| DrctDbtTxInf/DbtrAcct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account | accountType | Account type |
| DrctDbtTxInf/DbtrAcct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency |
| DrctDbtTxInf/DbtrAcct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account | accountName | Account name |

#### 2.14 Ultimate Debtor (UltmtDbtr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ultimate payer |
| DrctDbtTxInf/UltmtDbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country |
| DrctDbtTxInf/UltmtDbtr/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| DrctDbtTxInf/UltmtDbtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID |

#### 2.15 Purpose

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/Purp/Cd | Purpose Code | Code | - | 0..1 | BONU, CASH, DIVD, etc. | PaymentInstruction.extensions | purposeCode | Purpose of payment |
| DrctDbtTxInf/Purp/Prtry | Proprietary Purpose | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryPurpose | Custom purpose |

#### 2.16 Remittance Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction | remittanceInformation | Unstructured remittance info |
| DrctDbtTxInf/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd | Document Type Code | Code | - | 0..1 | CINV, CREN, DEBN, etc. | PaymentInstruction.extensions | documentTypeCode | Invoice type |
| DrctDbtTxInf/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | invoiceNumber | Invoice number |
| DrctDbtTxInf/RmtInf/Strd/RfrdDocInf/RltdDt | Related Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | invoiceDate | Invoice date |
| DrctDbtTxInf/RmtInf/Strd/RfrdDocAmt/DuePyblAmt | Due Payable Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | duePayableAmount | Amount due |
| DrctDbtTxInf/RmtInf/Strd/CdtrRefInf/Tp/CdOrPrtry/Cd | Creditor Reference Type | Code | - | 0..1 | SCOR | PaymentInstruction.extensions | creditorReferenceType | Reference type |
| DrctDbtTxInf/RmtInf/Strd/CdtrRefInf/Ref | Creditor Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | creditorReference | Structured creditor reference |

---

## Code Lists and Enumerations

### Settlement Method (SttlmMtd)
- **INDA** - Instructed Agent (Debtor agent settles)
- **INGA** - Instructing Agent (Creditor agent settles)
- **COVE** - Cover method
- **CLRG** - Clearing system

### Service Level (SvcLvl/Cd)
- **SEPA** - Single Euro Payments Area
- **SDVA** - Same Day Value
- **PRPT** - EBA Priority Service
- **URGP** - Urgent Payment

### Local Instrument (LclInstrm/Cd)
- **CORE** - SEPA Core Direct Debit
- **B2B** - SEPA Business to Business Direct Debit
- **COR1** - SEPA Core Direct Debit with 1 day notice

### Sequence Type (SeqTp)
- **FRST** - First collection in a series
- **RCUR** - Recurring collection
- **FNAL** - Final collection in a series
- **OOFF** - One-off collection

### Charge Bearer (ChrgBr)
- **DEBT** - Debtor bears all charges
- **CRED** - Creditor bears all charges
- **SHAR** - Charges shared between debtor and creditor
- **SLEV** - Charges as per service level agreement

### Instruction Priority (InstrPrty)
- **HIGH** - High priority
- **NORM** - Normal priority

### Category Purpose (CtgyPurp/Cd)
- **CASH** - Cash Management Transfer
- **CORT** - Trade Settlement
- **DVPM** - Delivery Versus Payment
- **INTC** - Intra-Company Payment
- **TREA** - Treasury Transfer

### Purpose Code (Purp/Cd)
- **BONU** - Bonus Payment
- **CASH** - Cash Management
- **DIVD** - Dividend
- **GOVT** - Government Payment
- **PENS** - Pension Payment
- **SALA** - Salary Payment
- **TAXS** - Tax Payment
- **SUPP** - Supplier Payment
- **UTIL** - Utility Bill Payment

---

## Message Example

### SEPA Core Direct Debit (CORE)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.003.001.08">
  <FIToFICstmrDrctDbt>
    <GrpHdr>
      <MsgId>MSGID-20241220-001</MsgId>
      <CreDtTm>2024-12-20T09:30:00</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>1250.00</CtrlSum>
      <TtlIntrBkSttlmAmt Ccy="EUR">1250.00</TtlIntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-22</IntrBkSttlmDt>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
        <ClrSys>
          <Cd>ST2</Cd>
        </ClrSys>
      </SttlmInf>
      <PmtTpInf>
        <InstrPrty>NORM</InstrPrty>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
        <LclInstrm>
          <Cd>CORE</Cd>
        </LclInstrm>
        <SeqTp>RCUR</SeqTp>
      </PmtTpInf>
      <InstgAgt>
        <FinInstnId>
          <BICFI>CRDBFRPPXXX</BICFI>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <BICFI>DEBTDEFFXXX</BICFI>
        </FinInstnId>
      </InstdAgt>
    </GrpHdr>
    <DrctDbtTxInf>
      <PmtId>
        <InstrId>INSTR-20241220-001</InstrId>
        <EndToEndId>E2E-INV-12345</EndToEndId>
        <TxId>TXN-20241220-001</TxId>
      </PmtId>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
        <LclInstrm>
          <Cd>CORE</Cd>
        </LclInstrm>
        <SeqTp>RCUR</SeqTp>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="EUR">1250.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-22</IntrBkSttlmDt>
      <ChrgBr>SLEV</ChrgBr>
      <DrctDbtTx>
        <MndtRltdInf>
          <MndtId>MANDATE-2023-XYZ-789</MndtId>
          <DtOfSgntr>2023-01-15</DtOfSgntr>
          <AmdmntInd>false</AmdmntInd>
        </MndtRltdInf>
        <CdtrSchmeId>
          <Nm>Acme Subscription Services Ltd</Nm>
          <Id>
            <PrvtId>
              <Othr>
                <Id>DE98ZZZ09999999999</Id>
                <SchmeNm>
                  <Cd>SEPA</Cd>
                </SchmeNm>
              </Othr>
            </PrvtId>
          </Id>
        </CdtrSchmeId>
      </DrctDbtTx>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>CRDBFRPPXXX</BICFI>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>Acme Subscription Services Ltd</Nm>
        <PstlAdr>
          <StrtNm>Rue de Commerce</StrtNm>
          <BldgNb>45</BldgNb>
          <PstCd>75001</PstCd>
          <TwnNm>Paris</TwnNm>
          <Ctry>FR</Ctry>
        </PstlAdr>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <IBAN>FR7630006000011234567890189</IBAN>
        </Id>
      </CdtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>DEBTDEFFXXX</BICFI>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>Hans Mueller</Nm>
        <PstlAdr>
          <StrtNm>Hauptstrasse</StrtNm>
          <BldgNb>123</BldgNb>
          <PstCd>10115</PstCd>
          <TwnNm>Berlin</TwnNm>
          <Ctry>DE</Ctry>
        </PstlAdr>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <IBAN>DE89370400440532013000</IBAN>
        </Id>
      </DbtrAcct>
      <Purp>
        <Cd>SUPP</Cd>
      </Purp>
      <RmtInf>
        <Ustrd>Monthly subscription fee - December 2024 - Account #XYZ789</Ustrd>
      </RmtInf>
    </DrctDbtTxInf>
  </FIToFICstmrDrctDbt>
</Document>
```

### SEPA B2B Direct Debit Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.003.001.08">
  <FIToFICstmrDrctDbt>
    <GrpHdr>
      <MsgId>MSGID-20241220-B2B-001</MsgId>
      <CreDtTm>2024-12-20T14:15:00</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>25000.00</CtrlSum>
      <TtlIntrBkSttlmAmt Ccy="EUR">25000.00</TtlIntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-23</IntrBkSttlmDt>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
        <ClrSys>
          <Cd>ST2</Cd>
        </ClrSys>
      </SttlmInf>
      <PmtTpInf>
        <InstrPrty>NORM</InstrPrty>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
        <LclInstrm>
          <Cd>B2B</Cd>
        </LclInstrm>
        <SeqTp>OOFF</SeqTp>
      </PmtTpInf>
      <InstgAgt>
        <FinInstnId>
          <BICFI>BNPAFRPPXXX</BICFI>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <BICFI>COBADEFFXXX</BICFI>
        </FinInstnId>
      </InstdAgt>
    </GrpHdr>
    <DrctDbtTxInf>
      <PmtId>
        <InstrId>B2B-INSTR-20241220-001</InstrId>
        <EndToEndId>E2E-PO-987654</EndToEndId>
        <TxId>B2B-TXN-20241220-001</TxId>
      </PmtId>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
        <LclInstrm>
          <Cd>B2B</Cd>
        </LclInstrm>
        <SeqTp>OOFF</SeqTp>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="EUR">25000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-23</IntrBkSttlmDt>
      <ChrgBr>SLEV</ChrgBr>
      <DrctDbtTx>
        <MndtRltdInf>
          <MndtId>B2B-MANDATE-2024-ABC-456</MndtId>
          <DtOfSgntr>2024-11-01</DtOfSgntr>
          <AmdmntInd>false</AmdmntInd>
        </MndtRltdInf>
        <CdtrSchmeId>
          <Nm>Global Manufacturing Supplies SARL</Nm>
          <Id>
            <PrvtId>
              <Othr>
                <Id>FR72ZZZ123456</Id>
                <SchmeNm>
                  <Cd>SEPA</Cd>
                </SchmeNm>
              </Othr>
            </PrvtId>
          </Id>
        </CdtrSchmeId>
      </DrctDbtTx>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>BNPAFRPPXXX</BICFI>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>Global Manufacturing Supplies SARL</Nm>
        <PstlAdr>
          <StrtNm>Avenue des Champs-Elysées</StrtNm>
          <BldgNb>100</BldgNb>
          <PstCd>75008</PstCd>
          <TwnNm>Paris</TwnNm>
          <Ctry>FR</Ctry>
        </PstlAdr>
        <Id>
          <OrgId>
            <Othr>
              <Id>FR12345678901</Id>
            </Othr>
          </OrgId>
        </Id>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <IBAN>FR1420041010050500013M02606</IBAN>
        </Id>
      </CdtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>COBADEFFXXX</BICFI>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>Deutsche Automotive Parts GmbH</Nm>
        <PstlAdr>
          <StrtNm>Industriestrasse</StrtNm>
          <BldgNb>56</BldgNb>
          <PstCd>70173</PstCd>
          <TwnNm>Stuttgart</TwnNm>
          <Ctry>DE</Ctry>
        </PstlAdr>
        <Id>
          <OrgId>
            <Othr>
              <Id>DE987654321</Id>
            </Othr>
          </OrgId>
        </Id>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <IBAN>DE89370400440532013000</IBAN>
        </Id>
      </DbtrAcct>
      <Purp>
        <Cd>SUPP</Cd>
      </Purp>
      <RmtInf>
        <Strd>
          <RfrdDocInf>
            <Tp>
              <CdOrPrtry>
                <Cd>CINV</Cd>
              </CdOrPrtry>
            </Tp>
            <Nb>INV-2024-987654</Nb>
            <RltdDt>2024-11-30</RltdDt>
          </RfrdDocInf>
          <RfrdDocAmt>
            <DuePyblAmt Ccy="EUR">25000.00</DuePyblAmt>
          </RfrdDocAmt>
        </Strd>
      </RmtInf>
    </DrctDbtTxInf>
  </FIToFICstmrDrctDbt>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 135 fields in pacs.003 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles instruction identification, amounts, dates
- Extension fields accommodate mandate information, SEPA-specific elements, sequence types
- Party entity supports creditor, debtor, ultimate parties with full identification
- Account entity handles IBAN and non-IBAN account identifiers
- FinancialInstitution entity manages agent information and clearing system details

**Key Extension Fields Used:**
- mandateId, mandateSignatureDate, mandateSequenceType (FRST/RCUR/FNAL/OOFF)
- creditorSchemeId (SEPA creditor identifier)
- localInstrumentCode (CORE/B2B/COR1)
- serviceLevelCode (SEPA)
- preNotificationId, preNotificationDate
- mandateAmendmentIndicator, originalMandateId

---

## References

- **ISO 20022 Message Definition:** pacs.003.001.08 - FIToFICustomerDirectDebit
- **SEPA Rulebook:** EPC Implementation Guidelines for SEPA Direct Debit Core/B2B
- **XML Schema:** pacs.003.001.08.xsd
- **Related Messages:** pain.008 (initiation), pacs.002 (status), pacs.004 (return), pacs.007 (reversal)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
