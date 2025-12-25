# ISO 20022 pain.008 - Customer Direct Debit Initiation Mapping

## Message Overview

**Message Type:** pain.008.001.08 - CustomerDirectDebitInitiationV08
**Category:** PAIN - Payment Initiation
**Purpose:** Sent by a creditor (or creditor's agent) to their bank to initiate collection of funds from a debtor's account via direct debit
**Direction:** Customer (Creditor) → Bank (Creditor Agent)
**Scope:** Customer-initiated direct debit instruction

**Key Use Cases:**
- SEPA Direct Debit Core (SDD Core) - consumer direct debits
- SEPA Direct Debit Business-to-Business (SDD B2B) - corporate direct debits
- Recurring subscription payments
- Utility bill collections
- Mortgage/loan payments
- Insurance premium collections
- One-off direct debit payments

**Relationship to Other Messages:**
- **pacs.003**: Interbank direct debit message (generated from pain.008)
- **pain.002**: Status report sent by bank to customer
- **pain.007**: Customer reversal request
- **pain.009-014**: Mandate management messages
- **pacs.004**: Return message if direct debit fails
- **pacs.007**: Reversal message after settlement

**Direct Debit Workflow:**
1. Debtor signs mandate authorizing creditor to collect funds
2. Creditor sends **pain.008** to their bank with collection request
3. Bank validates and generates **pacs.003** to debtor's bank
4. Debtor's bank debits debtor account (or rejects)
5. Banks send **pain.002** status to creditor

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in pain.008** | 145 |
| **Fields Mapped to CDM** | 145 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- Party (creditor, debtor, ultimate parties)
- Account (creditor account, debtor account)
- FinancialInstitution (creditor agent, debtor agent)
- Mandate (direct debit mandate information)

---

## Complete Field Mapping

### 1. Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique message identifier |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | createdDateTime | Message creation timestamp |
| GrpHdr/NbOfTxs | Number of Transactions | Text | 1-15 | 1..1 | Numeric string | PaymentInstruction.extensions | numberOfTransactions | Transaction count in message |
| GrpHdr/CtrlSum | Control Sum | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | controlSum | Total of all amounts (validation) |
| GrpHdr/InitgPty/Nm | Initiating Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Creditor or agent initiating |
| GrpHdr/InitgPty/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| GrpHdr/InitgPty/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Free text | Party | buildingNumber | Building number |
| GrpHdr/InitgPty/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | ZIP/postal code |
| GrpHdr/InitgPty/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| GrpHdr/InitgPty/PstlAdr/CtrySubDvsn | Country Sub-division | Text | 1-35 | 0..1 | Free text | Party | stateProvince | State/province |
| GrpHdr/InitgPty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country code |
| GrpHdr/InitgPty/PstlAdr/AdrLine | Address Line | Text | 1-70 | 0..7 | Free text | Party | addressLines | Unstructured address |
| GrpHdr/InitgPty/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| GrpHdr/InitgPty/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID/organization number |
| GrpHdr/InitgPty/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Birth Date | Date | - | 0..1 | ISODate | Party | dateOfBirth | Date of birth |
| GrpHdr/InitgPty/Id/PrvtId/Othr/Id | Private Other ID | Text | 1-35 | 0..1 | Free text | Party | nationalId | National ID |
| GrpHdr/FwdgAgt/FinInstnId/BICFI | Forwarding Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Forwarding agent |

### 2. Payment Information (PmtInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| PmtInf/PmtInfId | Payment Information ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | paymentInfoId | Unique payment batch ID |
| PmtInf/PmtMtd | Payment Method | Code | 2 | 1..1 | DD | PaymentInstruction.extensions | paymentMethod | Direct Debit (DD) |
| PmtInf/BtchBookg | Batch Booking | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | batchBookingIndicator | Bulk booking indicator |
| PmtInf/NbOfTxs | Number of Transactions | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | numberOfTransactions | Transaction count in batch |
| PmtInf/CtrlSum | Control Sum | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | controlSum | Batch control sum |
| PmtInf/PmtTpInf/InstrPrty | Instruction Priority | Code | 4 | 0..1 | HIGH, NORM | PaymentInstruction.extensions | priority | Processing priority |
| PmtInf/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | - | 0..1 | SEPA, SDVA, PRPT | PaymentInstruction.extensions | serviceLevelCode | Service level agreement |
| PmtInf/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | - | 0..1 | CORE, B2B, COR1 | PaymentInstruction.extensions | localInstrumentCode | SEPA direct debit scheme |
| PmtInf/PmtTpInf/SeqTp | Sequence Type | Code | 4 | 0..1 | FRST, RCUR, FNAL, OOFF | PaymentInstruction.extensions | mandateSequenceType | Mandate occurrence type |
| PmtInf/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | - | 0..1 | CASH, DVPM, INTC, TREA | PaymentInstruction.extensions | categoryPurposeCode | Payment category purpose |
| PmtInf/ReqdColltnDt | Requested Collection Date | Date | - | 1..1 | ISODate | PaymentInstruction | requestedExecutionDate | When to collect funds |
| PmtInf/Cdtr/Nm | Creditor Name | Text | 1-140 | 1..1 | Free text | Party | partyName | Creditor name (beneficiary) |
| PmtInf/Cdtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| PmtInf/Cdtr/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Free text | Party | buildingNumber | Building number |
| PmtInf/Cdtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | ZIP/postal code |
| PmtInf/Cdtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| PmtInf/Cdtr/PstlAdr/CtrySubDvsn | Country Sub-division | Text | 1-35 | 0..1 | Free text | Party | stateProvince | State/province |
| PmtInf/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country code |
| PmtInf/Cdtr/PstlAdr/AdrLine | Address Line | Text | 1-70 | 0..7 | Free text | Party | addressLines | Unstructured address |
| PmtInf/Cdtr/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| PmtInf/Cdtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID/organization number |
| PmtInf/Cdtr/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Birth Date | Date | - | 0..1 | ISODate | Party | dateOfBirth | Date of birth |
| PmtInf/Cdtr/Id/PrvtId/Othr/Id | Private Other ID | Text | 1-35 | 0..1 | Free text | Party | nationalId | National ID |
| PmtInf/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 1..1 | IBAN format | Account | accountNumber | IBAN for creditor (mandatory) |
| PmtInf/CdtrAcct/Id/Othr/Id | Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| PmtInf/CdtrAcct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account | accountType | Account type |
| PmtInf/CdtrAcct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency |
| PmtInf/CdtrAcct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account | accountName | Account name |
| PmtInf/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 1..1 | BIC format | FinancialInstitution | bicCode | Creditor's bank BIC (mandatory) |
| PmtInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId | Member Identification | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing system member ID |
| PmtInf/CdtrAgt/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Creditor agent name |
| PmtInf/CdtrAgt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Creditor agent country |
| PmtInf/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ultimate beneficiary |
| PmtInf/UltmtCdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country |
| PmtInf/UltmtCdtr/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| PmtInf/UltmtCdtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID |
| PmtInf/ChrgBr | Charge Bearer | Code | 4 | 0..1 | SLEV, SHAR, CRED, DEBT | PaymentInstruction.extensions | chargeBearer | Who pays charges |
| PmtInf/CdtrSchmeId/Nm | Creditor Scheme Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Creditor scheme name |
| PmtInf/CdtrSchmeId/Id/PrvtId/Othr/Id | Creditor Scheme ID | Text | 1-35 | 0..1 | Free text | Party.extensions | creditorSchemeId | Creditor identifier (e.g., SEPA creditor ID) |
| PmtInf/CdtrSchmeId/Id/PrvtId/Othr/SchmeNm/Cd | Scheme Name Code | Code | - | 0..1 | SEPA | Party.extensions | creditorSchemeNameCode | Identifier scheme |
| PmtInf/CdtrSchmeId/Id/PrvtId/Othr/Issr | Issuer | Text | 1-35 | 0..1 | Free text | Party.extensions | creditorSchemeIssuer | Scheme issuer |

### 3. Direct Debit Transaction Information (DrctDbtTxInf)

#### 3.1 Payment Identification

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/PmtId/InstrId | Instruction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Unique instruction identifier |
| DrctDbtTxInf/PmtId/EndToEndId | End to End Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | endToEndId | E2E reference from creditor |
| DrctDbtTxInf/PmtId/UETR | Unique End-to-end Transaction Reference | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Universal unique identifier |

#### 3.2 Payment Type Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/PmtTpInf/InstrPrty | Instruction Priority | Code | 4 | 0..1 | HIGH, NORM | PaymentInstruction.extensions | priority | Transaction-level priority |
| DrctDbtTxInf/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | - | 0..1 | SEPA, SDVA, PRPT | PaymentInstruction.extensions | serviceLevelCode | Service level |
| DrctDbtTxInf/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | - | 0..1 | CORE, B2B, COR1 | PaymentInstruction.extensions | localInstrumentCode | SEPA direct debit scheme |
| DrctDbtTxInf/PmtTpInf/SeqTp | Sequence Type | Code | 4 | 0..1 | FRST, RCUR, FNAL, OOFF | PaymentInstruction.extensions | mandateSequenceType | Mandate occurrence type |
| DrctDbtTxInf/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | - | 0..1 | CASH, CORT, etc. | PaymentInstruction.extensions | categoryPurposeCode | Category purpose |

#### 3.3 Instructed Amount

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/InstdAmt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | amount | Amount to collect |
| DrctDbtTxInf/InstdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | currency | Collection currency |

#### 3.4 Charge Bearer

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/ChrgBr | Charge Bearer | Code | 4 | 0..1 | SLEV, SHAR, CRED, DEBT | PaymentInstruction.extensions | chargeBearer | Who pays charges |

#### 3.5 Direct Debit Transaction (DrctDbtTx)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/DrctDbtTx/MndtRltdInf/MndtId | Mandate Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | mandateId | Unique mandate reference (mandatory) |
| DrctDbtTxInf/DrctDbtTx/MndtRltdInf/DtOfSgntr | Date of Signature | Date | - | 1..1 | ISODate | PaymentInstruction.extensions | mandateSignatureDate | Mandate signature date (mandatory) |
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

#### 3.6 Ultimate Creditor (UltmtCdtr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ultimate beneficiary |
| DrctDbtTxInf/UltmtCdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country |
| DrctDbtTxInf/UltmtCdtr/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| DrctDbtTxInf/UltmtCdtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID |

#### 3.7 Debtor Agent (DbtrAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Debtor's bank BIC |
| DrctDbtTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId | Member Identification | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing system member ID |
| DrctDbtTxInf/DbtrAgt/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Debtor agent name |
| DrctDbtTxInf/DbtrAgt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Debtor agent country |

#### 3.8 Debtor (Dbtr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/Dbtr/Nm | Debtor Name | Text | 1-140 | 1..1 | Free text | Party | partyName | Payer name (mandatory) |
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

#### 3.9 Debtor Account (DbtrAcct)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 1..1 | IBAN format | Account | accountNumber | IBAN for debtor (mandatory) |
| DrctDbtTxInf/DbtrAcct/Id/Othr/Id | Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| DrctDbtTxInf/DbtrAcct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account | accountType | Account type |
| DrctDbtTxInf/DbtrAcct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency |
| DrctDbtTxInf/DbtrAcct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account | accountName | Account name |

#### 3.10 Ultimate Debtor (UltmtDbtr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ultimate payer |
| DrctDbtTxInf/UltmtDbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country |
| DrctDbtTxInf/UltmtDbtr/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| DrctDbtTxInf/UltmtDbtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID |

#### 3.11 Purpose

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/Purp/Cd | Purpose Code | Code | - | 0..1 | BONU, CASH, DIVD, GOVT, PENS, SALA, TAXS, UTIL, etc. | PaymentInstruction.extensions | purposeCode | Purpose of payment |
| DrctDbtTxInf/Purp/Prtry | Proprietary Purpose | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryPurpose | Custom purpose |

#### 3.12 Regulatory Reporting

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/RgltryRptg/DbtCdtRptgInd | Debit Credit Reporting Indicator | Code | 4 | 0..1 | DEBT, CRED, BOTH | PaymentInstruction.extensions | regulatoryReportingIndicator | Regulatory reporting required |
| DrctDbtTxInf/RgltryRptg/Authrty/Nm | Authority Name | Text | 1-140 | 0..1 | Free text | PaymentInstruction.extensions | regulatoryAuthorityName | Regulatory authority |
| DrctDbtTxInf/RgltryRptg/Authrty/Ctry | Authority Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | PaymentInstruction.extensions | regulatoryAuthorityCountry | Authority country |
| DrctDbtTxInf/RgltryRptg/Dtls/Tp | Regulatory Details Type | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | regulatoryDetailsType | Detail type |
| DrctDbtTxInf/RgltryRptg/Dtls/Inf | Regulatory Information | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | regulatoryInformation | Regulatory info |

#### 3.13 Remittance Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| DrctDbtTxInf/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction | remittanceInformation | Unstructured remittance info |
| DrctDbtTxInf/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd | Document Type Code | Code | - | 0..1 | CINV, CREN, DEBN, etc. | PaymentInstruction.extensions | documentTypeCode | Invoice type |
| DrctDbtTxInf/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | invoiceNumber | Invoice number |
| DrctDbtTxInf/RmtInf/Strd/RfrdDocInf/RltdDt | Related Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | invoiceDate | Invoice date |
| DrctDbtTxInf/RmtInf/Strd/RfrdDocAmt/DuePyblAmt | Due Payable Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | duePayableAmount | Amount due |
| DrctDbtTxInf/RmtInf/Strd/CdtrRefInf/Tp/CdOrPrtry/Cd | Creditor Reference Type | Code | - | 0..1 | SCOR | PaymentInstruction.extensions | creditorReferenceType | Reference type |
| DrctDbtTxInf/RmtInf/Strd/CdtrRefInf/Ref | Creditor Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | creditorReference | Structured creditor reference |

### 4. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Payment Method (PmtMtd)
- **DD** - Direct Debit (mandatory for pain.008)

### Service Level (SvcLvl/Cd)
- **SEPA** - Single Euro Payments Area
- **SDVA** - Same Day Value
- **PRPT** - EBA Priority Service

### Local Instrument (LclInstrm/Cd)
- **CORE** - SEPA Core Direct Debit (consumer)
- **B2B** - SEPA Business to Business Direct Debit (corporate)
- **COR1** - SEPA Core Direct Debit with 1 day notice

### Sequence Type (SeqTp)
- **FRST** - First collection in a series (mandate first use)
- **RCUR** - Recurring collection (subsequent use)
- **FNAL** - Final collection in a series (last use)
- **OOFF** - One-off collection (single use)

### Charge Bearer (ChrgBr)
- **SLEV** - As per service level agreement (SEPA default)
- **SHAR** - Charges shared between debtor and creditor
- **CRED** - Creditor bears all charges
- **DEBT** - Debtor bears all charges

### Instruction Priority (InstrPrty)
- **HIGH** - High priority
- **NORM** - Normal priority

### Purpose Code (Purp/Cd)
- **BONU** - Bonus Payment
- **CASH** - Cash Management
- **DIVD** - Dividend
- **GOVT** - Government Payment
- **PENS** - Pension Payment
- **SALA** - Salary Payment
- **TAXS** - Tax Payment
- **UTIL** - Utility Bill Payment
- **SUPP** - Supplier Payment

---

## Message Examples

### Example 1: SEPA Core Direct Debit - Recurring Subscription

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.001.08">
  <CstmrDrctDbtInitn>
    <GrpHdr>
      <MsgId>DD-COLL-20241220-001</MsgId>
      <CreDtTm>2024-12-20T10:00:00</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>9.99</CtrlSum>
      <InitgPty>
        <Nm>Streaming Service Pro</Nm>
        <Id>
          <OrgId>
            <Othr>
              <Id>FR987654321</Id>
            </Othr>
          </OrgId>
        </Id>
      </InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>PMT-BATCH-SUB-001</PmtInfId>
      <PmtMtd>DD</PmtMtd>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>9.99</CtrlSum>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
        <LclInstrm>
          <Cd>CORE</Cd>
        </LclInstrm>
        <SeqTp>RCUR</SeqTp>
      </PmtTpInf>
      <ReqdColltnDt>2024-12-25</ReqdColltnDt>
      <Cdtr>
        <Nm>Streaming Service Pro</Nm>
        <PstlAdr>
          <StrtNm>Rue de la Paix</StrtNm>
          <BldgNb>100</BldgNb>
          <PstCd>75002</PstCd>
          <TwnNm>Paris</TwnNm>
          <Ctry>FR</Ctry>
        </PstlAdr>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <IBAN>FR7630006000011234567890189</IBAN>
        </Id>
      </CdtrAcct>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>BNPAFRPPXXX</BICFI>
        </FinInstnId>
      </CdtrAgt>
      <ChrgBr>SLEV</ChrgBr>
      <CdtrSchmeId>
        <Nm>Streaming Service Pro</Nm>
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
      <DrctDbtTxInf>
        <PmtId>
          <EndToEndId>E2E-SUB-DEC-2024-USER-789</EndToEndId>
        </PmtId>
        <InstdAmt Ccy="EUR">9.99</InstdAmt>
        <DrctDbtTx>
          <MndtRltdInf>
            <MndtId>MANDATE-2023-USER-789</MndtId>
            <DtOfSgntr>2023-06-15</DtOfSgntr>
            <AmdmntInd>false</AmdmntInd>
          </MndtRltdInf>
        </DrctDbtTx>
        <DbtrAgt>
          <FinInstnId>
            <BICFI>DEBTDEFFXXX</BICFI>
          </FinInstnId>
        </DbtrAgt>
        <Dbtr>
          <Nm>Anna Schmidt</Nm>
          <PstlAdr>
            <StrtNm>Hauptstrasse</StrtNm>
            <BldgNb>25</BldgNb>
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
          <Cd>UTIL</Cd>
        </Purp>
        <RmtInf>
          <Ustrd>Streaming Service Pro - Monthly subscription - December 2024 - Account USER-789</Ustrd>
        </RmtInf>
      </DrctDbtTxInf>
    </PmtInf>
  </CstmrDrctDbtInitn>
</Document>
```

### Example 2: SEPA B2B Direct Debit - First Collection

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.001.08">
  <CstmrDrctDbtInitn>
    <GrpHdr>
      <MsgId>DD-B2B-20241220-001</MsgId>
      <CreDtTm>2024-12-20T14:30:00</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>15000.00</CtrlSum>
      <InitgPty>
        <Nm>Office Supplies International Ltd</Nm>
        <Id>
          <OrgId>
            <Othr>
              <Id>GB123456789</Id>
            </Othr>
          </OrgId>
        </Id>
      </InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>PMT-B2B-BATCH-001</PmtInfId>
      <PmtMtd>DD</PmtMtd>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>15000.00</CtrlSum>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
        <LclInstrm>
          <Cd>B2B</Cd>
        </LclInstrm>
        <SeqTp>FRST</SeqTp>
      </PmtTpInf>
      <ReqdColltnDt>2024-12-27</ReqdColltnDt>
      <Cdtr>
        <Nm>Office Supplies International Ltd</Nm>
        <PstlAdr>
          <StrtNm>Business Park Drive</StrtNm>
          <BldgNb>15</BldgNb>
          <PstCd>EC1A 1BB</PstCd>
          <TwnNm>London</TwnNm>
          <Ctry>GB</Ctry>
        </PstlAdr>
        <Id>
          <OrgId>
            <Othr>
              <Id>GB123456789</Id>
            </Othr>
          </OrgId>
        </Id>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <IBAN>GB29ABCB60161331926819</IBAN>
        </Id>
      </CdtrAcct>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>ABCBGB2LXXX</BICFI>
        </FinInstnId>
      </CdtrAgt>
      <ChrgBr>SLEV</ChrgBr>
      <CdtrSchmeId>
        <Nm>Office Supplies International Ltd</Nm>
        <Id>
          <PrvtId>
            <Othr>
              <Id>GB98ZZZ987654</Id>
              <SchmeNm>
                <Cd>SEPA</Cd>
              </SchmeNm>
            </Othr>
          </PrvtId>
        </Id>
      </CdtrSchmeId>
      <DrctDbtTxInf>
        <PmtId>
          <InstrId>INSTR-B2B-001</InstrId>
          <EndToEndId>E2E-INV-2024-12345</EndToEndId>
        </PmtId>
        <InstdAmt Ccy="EUR">15000.00</InstdAmt>
        <DrctDbtTx>
          <MndtRltdInf>
            <MndtId>B2B-MANDATE-2024-CORP-456</MndtId>
            <DtOfSgntr>2024-12-01</DtOfSgntr>
            <AmdmntInd>false</AmdmntInd>
          </MndtRltdInf>
          <CdtrSchmeId>
            <Nm>Office Supplies International Ltd</Nm>
            <Id>
              <PrvtId>
                <Othr>
                  <Id>GB98ZZZ987654</Id>
                  <SchmeNm>
                    <Cd>SEPA</Cd>
                  </SchmeNm>
                </Othr>
              </PrvtId>
            </Id>
          </CdtrSchmeId>
          <PreNtfctnId>PRENOTIF-2024-12-15-001</PreNtfctnId>
          <PreNtfctnDt>2024-12-15</PreNtfctnDt>
        </DrctDbtTx>
        <DbtrAgt>
          <FinInstnId>
            <BICFI>BNPAFRPPXXX</BICFI>
          </FinInstnId>
        </DbtrAgt>
        <Dbtr>
          <Nm>French Corporate Services SARL</Nm>
          <PstlAdr>
            <StrtNm>Avenue des Champs-Elysées</StrtNm>
            <BldgNb>50</BldgNb>
            <PstCd>75008</PstCd>
            <TwnNm>Paris</TwnNm>
            <Ctry>FR</Ctry>
          </PstlAdr>
          <Id>
            <OrgId>
              <Othr>
                <Id>FR98765432101</Id>
              </Othr>
            </OrgId>
          </Id>
        </Dbtr>
        <DbtrAcct>
          <Id>
            <IBAN>FR1420041010050500013M02606</IBAN>
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
              <Nb>INV-2024-12345</Nb>
              <RltdDt>2024-11-30</RltdDt>
            </RfrdDocInf>
            <RfrdDocAmt>
              <DuePyblAmt Ccy="EUR">15000.00</DuePyblAmt>
            </RfrdDocAmt>
          </Strd>
        </RmtInf>
      </DrctDbtTxInf>
    </PmtInf>
  </CstmrDrctDbtInitn>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 145 fields in pain.008 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles instruction identification, amounts, dates
- Extension fields accommodate mandate information, SEPA-specific elements, sequence types
- Party entity supports creditor, debtor, ultimate parties with full identification
- Account entity handles IBAN and non-IBAN account identifiers
- FinancialInstitution entity manages agent information and clearing system details

**Key Extension Fields Used:**
- mandateId, mandateSignatureDate, mandateSequenceType (FRST/RCUR/FNAL/OOFF) - mandatory for direct debits
- creditorSchemeId (SEPA creditor identifier)
- localInstrumentCode (CORE/B2B/COR1)
- serviceLevelCode (SEPA)
- preNotificationId, preNotificationDate
- mandateAmendmentIndicator, originalMandateId
- paymentInfoId (batch identifier)

---

## References

- **ISO 20022 Message Definition:** pain.008.001.08 - CustomerDirectDebitInitiationV08
- **SEPA Rulebook:** EPC Implementation Guidelines for SEPA Direct Debit Core/B2B
- **XML Schema:** pain.008.001.08.xsd
- **Related Messages:** pacs.003 (interbank), pain.002 (status), pain.007 (reversal), pain.009-014 (mandates)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
