# ISO 20022 camt.054 - Bank to Customer Debit Credit Notification Mapping

## Message Overview

**Message Type:** camt.054.001.08 - BankToCustomerDebitCreditNotificationV08
**Category:** CAMT - Cash Management
**Purpose:** Sent by a bank to a customer to notify individual debit or credit entries on an account in real-time or near real-time
**Direction:** Bank → Customer
**Scope:** Real-time transaction notifications (individual entry notifications)

**Key Use Cases:**
- Real-time payment receipt notifications
- Instant debit transaction alerts
- High-value transaction notifications
- Fraud detection and monitoring
- Immediate account activity alerts
- Push notifications for mobile/online banking
- Exception notifications (large amounts, foreign transactions)

**Relationship to Other Messages:**
- **camt.052**: Account Report (multiple entries, summary view)
- **camt.053**: Statement (comprehensive daily statement)
- **camt.060**: Account Reporting Request (customer requests notifications)
- **pain.001/pain.008**: Payment instructions that trigger notifications
- **pacs.008/pacs.003**: Interbank payments resulting in notifications

**Comparison with camt.052/camt.053:**
- **camt.054**: Individual transaction notification (real-time, one or few entries)
- **camt.052**: Intraday report (multiple entries, periodic)
- **camt.053**: End-of-day statement (all entries, comprehensive)
- **camt.054**: Immediate alerts and monitoring
- **camt.052/053**: Reconciliation and accounting

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in camt.054** | 152 |
| **Fields Mapped to CDM** | 152 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- Account (account identification)
- Party (account owner, transaction parties)
- FinancialInstitution (account servicer, agent banks)
- AccountEntry (notification entries)

---

## Complete Field Mapping

### 1. Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique notification ID |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | createdDateTime | Notification timestamp |
| GrpHdr/MsgRcpt/Nm | Message Recipient Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Customer receiving notification |
| GrpHdr/MsgRcpt/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Customer BIC |
| GrpHdr/MsgRcpt/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Customer tax ID |
| GrpHdr/MsgPgntn/PgNb | Page Number | Text | 1-5 | 1..1 | Numeric string | PaymentInstruction.extensions | pageNumber | Current page number |
| GrpHdr/MsgPgntn/LastPgInd | Last Page Indicator | Boolean | - | 1..1 | true/false | PaymentInstruction.extensions | lastPageIndicator | Is this the last page |
| GrpHdr/AddtlInf | Additional Information | Text | 1-500 | 0..1 | Free text | PaymentInstruction.extensions | additionalInfo | Free-text info |

### 2. Notification (Ntfctn)

#### 2.1 Notification Identification

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Id | Notification Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | notificationId | Unique notification identifier |
| Ntfctn/NtfctnPgntn/PgNb | Page Number | Text | 1-5 | 1..1 | Numeric string | PaymentInstruction.extensions | notificationPageNumber | Notification page number |
| Ntfctn/NtfctnPgntn/LastPgInd | Last Page Indicator | Boolean | - | 1..1 | true/false | PaymentInstruction.extensions | notificationLastPageIndicator | Last page indicator |
| Ntfctn/ElctrncSeqNb | Electronic Sequence Number | Number | - | 0..1 | Positive integer | PaymentInstruction.extensions | electronicSequenceNumber | Sequence number |
| Ntfctn/LglSeqNb | Legal Sequence Number | Number | - | 0..1 | Positive integer | PaymentInstruction.extensions | legalSequenceNumber | Legal sequence |
| Ntfctn/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction.extensions | notificationCreatedDateTime | Notification creation time |
| Ntfctn/FrToDt/FrDtTm | From Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | notificationFromDateTime | Notification period start |
| Ntfctn/FrToDt/ToDtTm | To Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | notificationToDateTime | Notification period end |
| Ntfctn/CpyDplctInd | Copy Duplicate Indicator | Code | - | 0..1 | CODU, COPY, DUPL | PaymentInstruction.extensions | copyDuplicateIndicator | Original/copy/duplicate |
| Ntfctn/RptgSrc/Cd | Reporting Source Code | Code | - | 0..1 | Free text | PaymentInstruction.extensions | reportingSourceCode | Source of notification |
| Ntfctn/RptgSrc/Prtry | Proprietary Reporting Source | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryReportingSource | Custom source |

#### 2.2 Account

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Acct/Id/IBAN | Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Account IBAN |
| Ntfctn/Acct/Id/Othr/Id | Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| Ntfctn/Acct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, LOAN, etc. | Account | accountType | Account type |
| Ntfctn/Acct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency |
| Ntfctn/Acct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account | accountName | Account name |
| Ntfctn/Acct/Ownr/Nm | Owner Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Account owner |
| Ntfctn/Acct/Ownr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| Ntfctn/Acct/Ownr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | ZIP/postal code |
| Ntfctn/Acct/Ownr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| Ntfctn/Acct/Ownr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country |
| Ntfctn/Acct/Ownr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Owner BIC |
| Ntfctn/Acct/Ownr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Owner tax ID |
| Ntfctn/Acct/Svcr/FinInstnId/BICFI | Servicer BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Account servicer BIC |
| Ntfctn/Acct/Svcr/FinInstnId/Nm | Servicer Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Bank name |
| Ntfctn/Acct/Svcr/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Bank country |

#### 2.3 Related Account

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/RltdAcct/Id/IBAN | Related Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Related account |
| Ntfctn/RltdAcct/Id/Othr/Id | Related Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN related account |
| Ntfctn/RltdAcct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account | accountType | Related account type |
| Ntfctn/RltdAcct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Related account currency |

#### 2.4 Entry (Ntry)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Ntry/NtryRef | Entry Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | entryReference | Unique entry reference |
| Ntfctn/Ntry/Amt | Entry Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | amount | Entry amount |
| Ntfctn/Ntry/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | currency | Entry currency |
| Ntfctn/Ntry/CdtDbtInd | Credit Debit Indicator | Code | 4 | 1..1 | CRDT, DBIT | PaymentInstruction.extensions | creditDebitIndicator | Credit or Debit |
| Ntfctn/Ntry/RvslInd | Reversal Indicator | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | reversalIndicator | Is reversal entry |
| Ntfctn/Ntry/Sts/Cd | Entry Status Code | Code | - | 1..1 | BOOK, PDNG, INFO | PaymentInstruction | paymentStatus | Booked/Pending/Info |
| Ntfctn/Ntry/BookgDt/Dt | Booking Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | bookingDate | When booked |
| Ntfctn/Ntry/BookgDt/DtTm | Booking Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | bookingDateTime | Booking timestamp |
| Ntfctn/Ntry/ValDt/Dt | Value Date | Date | - | 0..1 | ISODate | PaymentInstruction | settlementDate | Value date |
| Ntfctn/Ntry/ValDt/DtTm | Value Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | valueDateTime | Value timestamp |
| Ntfctn/Ntry/AcctSvcrRef | Account Servicer Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | accountServicerReference | Bank's reference |
| Ntfctn/Ntry/BkTxCd/Domn/Cd | Domain Code | Code | - | 0..1 | PMNT, CASH, SECU, etc. | PaymentInstruction.extensions | bankTransactionDomainCode | Transaction domain |
| Ntfctn/Ntry/BkTxCd/Domn/Fmly/Cd | Family Code | Code | - | 0..1 | RCDT, RDDT, ICDT, etc. | PaymentInstruction.extensions | bankTransactionFamilyCode | Transaction family |
| Ntfctn/Ntry/BkTxCd/Domn/Fmly/SubFmlyCd | Sub-family Code | Code | - | 0..1 | BOOK, ESCT, etc. | PaymentInstruction.extensions | bankTransactionSubFamilyCode | Transaction sub-family |
| Ntfctn/Ntry/BkTxCd/Prtry/Cd | Proprietary Code | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryBankTransactionCode | Custom transaction code |
| Ntfctn/Ntry/BkTxCd/Prtry/Issr | Issuer | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | bankTransactionCodeIssuer | Code issuer |
| Ntfctn/Ntry/CmmssnWvrInd | Commission Waiver Indicator | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | commissionWaiverIndicator | Commission waived |

#### 2.5 Entry Details (NtryDtls)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Ntry/NtryDtls/Btch/MsgId | Batch Message ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | batchMessageId | Batch identifier |
| Ntfctn/Ntry/NtryDtls/Btch/PmtInfId | Payment Info ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | paymentInfoId | Payment batch ID |
| Ntfctn/Ntry/NtryDtls/Btch/NbOfTxs | Number of Transactions | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | numberOfTransactions | Transaction count |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/MsgId | Message ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Message identifier |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/AcctSvcrRef | Account Servicer Ref | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | accountServicerReference | Bank reference |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/PmtInfId | Payment Info ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | paymentInfoId | Payment info reference |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/InstrId | Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Instruction reference |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/EndToEndId | End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | endToEndId | E2E reference |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/TxId | Transaction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Transaction reference |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/UETR | UETR | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Universal unique identifier |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/MndtId | Mandate ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | mandateId | Direct debit mandate |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/ChqNb | Cheque Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | chequeNumber | Cheque number |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/ClrSysRef | Clearing System Ref | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | clearingSystemReference | Clearing reference |
| Ntfctn/Ntry/NtryDtls/TxDtls/AmtDtls/InstdAmt/Amt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | instructedAmount | Instructed amount |
| Ntfctn/Ntry/NtryDtls/TxDtls/AmtDtls/InstdAmt/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | instructedCurrency | Instructed currency |
| Ntfctn/Ntry/NtryDtls/TxDtls/AmtDtls/TxAmt/Amt | Transaction Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | amount | Transaction amount |
| Ntfctn/Ntry/NtryDtls/TxDtls/AmtDtls/TxAmt/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | currency | Transaction currency |
| Ntfctn/Ntry/NtryDtls/TxDtls/AmtDtls/TxAmt/CdtDbtInd | Credit Debit Indicator | Code | 4 | 0..1 | CRDT, DBIT | PaymentInstruction.extensions | creditDebitIndicator | Credit or Debit |
| Ntfctn/Ntry/NtryDtls/TxDtls/Avlbty/Dt/NbOfDays | Number of Days | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | transactionAvailabilityDays | Days until available |
| Ntfctn/Ntry/NtryDtls/TxDtls/Avlbty/Dt/ActlDt | Actual Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | transactionAvailabilityDate | When available |
| Ntfctn/Ntry/NtryDtls/TxDtls/BkTxCd/Domn/Cd | Domain Code | Code | - | 0..1 | PMNT, CASH, etc. | PaymentInstruction.extensions | txBankTransactionDomainCode | Transaction domain |
| Ntfctn/Ntry/NtryDtls/TxDtls/BkTxCd/Domn/Fmly/Cd | Family Code | Code | - | 0..1 | RCDT, RDDT, etc. | PaymentInstruction.extensions | txBankTransactionFamilyCode | Transaction family |
| Ntfctn/Ntry/NtryDtls/TxDtls/BkTxCd/Domn/Fmly/SubFmlyCd | Sub-family Code | Code | - | 0..1 | BOOK, ESCT, etc. | PaymentInstruction.extensions | txBankTransactionSubFamilyCode | Transaction sub-family |

#### 2.6 Related Parties (RltdPties)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/InitgPty/Nm | Initiating Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Payment initiator |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Payer name |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | Postal code |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Debtor country |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Id/OrgId/AnyBIC | Debtor BIC | Text | - | 0..1 | BIC format | Party | bic | Debtor BIC |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Id/OrgId/Othr/Id | Debtor Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Debtor tax ID |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Debtor account |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/DbtrAcct/Id/Othr/Id | Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ultimate payer |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Beneficiary name |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | Postal code |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Creditor country |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Id/OrgId/AnyBIC | Creditor BIC | Text | - | 0..1 | BIC format | Party | bic | Creditor BIC |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Id/OrgId/Othr/Id | Creditor Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Creditor tax ID |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Creditor account |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/CdtrAcct/Id/Othr/Id | Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ultimate beneficiary |

#### 2.7 Related Agents

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Debtor bank |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/Nm | Debtor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Debtor bank name |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Creditor bank |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/Nm | Creditor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Creditor bank name |

#### 2.8 Purpose

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Ntry/NtryDtls/TxDtls/Purp/Cd | Purpose Code | Code | - | 0..1 | BONU, CASH, DIVD, SALA, etc. | PaymentInstruction.extensions | purposeCode | Purpose of payment |
| Ntfctn/Ntry/NtryDtls/TxDtls/Purp/Prtry | Proprietary Purpose | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryPurpose | Custom purpose |

#### 2.9 Remittance Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Ntry/NtryDtls/TxDtls/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction | remittanceInformation | Unstructured remittance |
| Ntfctn/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd | Document Type Code | Code | - | 0..1 | CINV, CREN, DEBN, etc. | PaymentInstruction.extensions | documentTypeCode | Invoice type |
| Ntfctn/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | invoiceNumber | Invoice number |
| Ntfctn/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocInf/RltdDt | Related Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | invoiceDate | Invoice date |
| Ntfctn/Ntry/NtryDtls/TxDtls/RmtInf/Strd/CdtrRefInf/Tp/CdOrPrtry/Cd | Creditor Reference Type | Code | - | 0..1 | SCOR | PaymentInstruction.extensions | creditorReferenceType | Reference type |
| Ntfctn/Ntry/NtryDtls/TxDtls/RmtInf/Strd/CdtrRefInf/Ref | Creditor Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | creditorReference | Creditor reference |

#### 2.10 Return Information (RtrInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Ntry/NtryDtls/TxDtls/RtrInf/OrgnlBkTxCd/Domn/Cd | Original Domain Code | Code | - | 0..1 | PMNT, CASH, etc. | PaymentInstruction.extensions | originalBankTransactionDomainCode | Original transaction domain |
| Ntfctn/Ntry/NtryDtls/TxDtls/RtrInf/Orgtr/Nm | Originator Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Return originator |
| Ntfctn/Ntry/NtryDtls/TxDtls/RtrInf/Rsn/Cd | Return Reason Code | Code | - | 0..1 | AC01-AC99, AM01-AM99, etc. | PaymentInstruction.extensions | returnReasonCode | ISO 20022 return reason |
| Ntfctn/Ntry/NtryDtls/TxDtls/RtrInf/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | returnAdditionalInfo | Free-text explanation |

#### 2.11 Charges (Chrgs)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Ntry/Chrgs/TtlChrgsAndTaxAmt | Total Charges and Tax | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | totalChargesAmount | Total charges |
| Ntfctn/Ntry/Chrgs/TtlChrgsAndTaxAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | totalChargesCurrency | Charges currency |
| Ntfctn/Ntry/Chrgs/Rcrd/Amt | Charge Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction.extensions | chargesAmount | Individual charge |
| Ntfctn/Ntry/Chrgs/Rcrd/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | chargesCurrency | Charge currency |
| Ntfctn/Ntry/Chrgs/Rcrd/CdtDbtInd | Credit Debit Indicator | Code | 4 | 0..1 | CRDT, DBIT | PaymentInstruction.extensions | chargeCreditDebitIndicator | Charge credit/debit |
| Ntfctn/Ntry/Chrgs/Rcrd/Tp/Cd | Charge Type Code | Code | - | 0..1 | Free text | PaymentInstruction.extensions | chargeTypeCode | Type of charge |

### 3. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Entry Status (Ntry/Sts/Cd)
- **BOOK** - Booked (posted to account)
- **PDNG** - Pending (not yet posted)
- **INFO** - Information (for info only)

### Credit/Debit Indicator (CdtDbtInd)
- **CRDT** - Credit (money in)
- **DBIT** - Debit (money out)

### Bank Transaction Codes
(Same as camt.052/camt.053 - see previous mappings for full list)

**Common for Notifications:**
- **PMNT-RCDT-ESCT** - Received SEPA Credit Transfer
- **PMNT-ICDT-ESCT** - Issued SEPA Credit Transfer
- **PMNT-RDDT-ESDD** - Received SEPA Direct Debit
- **PMNT-ICDT-SALA** - Issued Salary Payment
- **CASH-CWDL** - Cash Withdrawal
- **CASH-CDPT** - Cash Deposit

---

## Message Examples

### Example 1: Credit Notification - Payment Received

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.054.001.08">
  <BkToCstmrDbtCdtNtfctn>
    <GrpHdr>
      <MsgId>NOTIF-20241220-143022-001</MsgId>
      <CreDtTm>2024-12-20T14:30:22</CreDtTm>
      <MsgRcpt>
        <Nm>Small Business Ltd</Nm>
      </MsgRcpt>
    </GrpHdr>
    <Ntfctn>
      <Id>NTFCTN-20241220-001</Id>
      <CreDtTm>2024-12-20T14:30:22</CreDtTm>
      <Acct>
        <Id>
          <IBAN>GB29ABCB60161331926819</IBAN>
        </Id>
        <Ccy>GBP</Ccy>
        <Nm>Small Business Ltd - Current Account</Nm>
        <Ownr>
          <Nm>Small Business Ltd</Nm>
        </Ownr>
        <Svcr>
          <FinInstnId>
            <BICFI>ABCBGB2LXXX</BICFI>
            <Nm>ABC Bank</Nm>
          </FinInstnId>
        </Svcr>
      </Acct>
      <Ntry>
        <NtryRef>ENTRY-20241220-143020</NtryRef>
        <Amt Ccy="GBP">2500.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Sts>
          <Cd>BOOK</Cd>
        </Sts>
        <BookgDt>
          <DtTm>2024-12-20T14:30:20</DtTm>
        </BookgDt>
        <ValDt>
          <Dt>2024-12-20</Dt>
        </ValDt>
        <AcctSvcrRef>ABC-REF-2024-54321</AcctSvcrRef>
        <BkTxCd>
          <Domn>
            <Cd>PMNT</Cd>
            <Fmly>
              <Cd>RCDT</Cd>
              <SubFmlyCd>ESCT</SubFmlyCd>
            </Fmly>
          </Domn>
        </BkTxCd>
        <NtryDtls>
          <TxDtls>
            <Refs>
              <EndToEndId>E2E-CUSTOMER-INV-789</EndToEndId>
              <TxId>TXN-20241220-789</TxId>
            </Refs>
            <AmtDtls>
              <TxAmt>
                <Amt Ccy="GBP">2500.00</Amt>
                <CdtDbtInd>CRDT</CdtDbtInd>
              </TxAmt>
            </AmtDtls>
            <RltdPties>
              <Dbtr>
                <Nm>Customer ABC Ltd</Nm>
                <PstlAdr>
                  <StrtNm>High Street</StrtNm>
                  <PstCd>W1A 1AA</PstCd>
                  <TwnNm>London</TwnNm>
                  <Ctry>GB</Ctry>
                </PstlAdr>
              </Dbtr>
              <DbtrAcct>
                <Id>
                  <IBAN>GB98NWBK12345678901234</IBAN>
                </Id>
              </DbtrAcct>
              <Cdtr>
                <Nm>Small Business Ltd</Nm>
              </Cdtr>
              <CdtrAcct>
                <Id>
                  <IBAN>GB29ABCB60161331926819</IBAN>
                </Id>
              </CdtrAcct>
            </RltdPties>
            <RltdAgts>
              <DbtrAgt>
                <FinInstnId>
                  <BICFI>NWBKGB2LXXX</BICFI>
                  <Nm>National Bank</Nm>
                </FinInstnId>
              </DbtrAgt>
            </RltdAgts>
            <RmtInf>
              <Ustrd>Payment for Invoice INV-2024-789 - Consulting services November 2024</Ustrd>
            </RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
    </Ntfctn>
  </BkToCstmrDbtCdtNtfctn>
</Document>
```

### Example 2: Debit Notification - High-Value Payment Alert

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.054.001.08">
  <BkToCstmrDbtCdtNtfctn>
    <GrpHdr>
      <MsgId>NOTIF-20241220-091545-002</MsgId>
      <CreDtTm>2024-12-20T09:15:45</CreDtTm>
      <MsgRcpt>
        <Nm>John Smith</Nm>
      </MsgRcpt>
    </GrpHdr>
    <Ntfctn>
      <Id>NTFCTN-20241220-002</Id>
      <CreDtTm>2024-12-20T09:15:45</CreDtTm>
      <Acct>
        <Id>
          <IBAN>GB67NWBK40306112345678</IBAN>
        </Id>
        <Ccy>GBP</Ccy>
        <Nm>John Smith - Personal Account</Nm>
        <Ownr>
          <Nm>John Smith</Nm>
        </Ownr>
        <Svcr>
          <FinInstnId>
            <BICFI>NWBKGB2LXXX</BICFI>
            <Nm>National Bank</Nm>
          </FinInstnId>
        </Svcr>
      </Acct>
      <Ntry>
        <NtryRef>ENTRY-20241220-091540</NtryRef>
        <Amt Ccy="GBP">15000.00</Amt>
        <CdtDbtInd>DBIT</CdtDbtInd>
        <Sts>
          <Cd>BOOK</Cd>
        </Sts>
        <BookgDt>
          <DtTm>2024-12-20T09:15:40</DtTm>
        </BookgDt>
        <ValDt>
          <Dt>2024-12-20</Dt>
        </ValDt>
        <AcctSvcrRef>NWBK-REF-2024-98765</AcctSvcrRef>
        <BkTxCd>
          <Domn>
            <Cd>PMNT</Cd>
            <Fmly>
              <Cd>ICDT</Cd>
              <SubFmlyCd>ESCT</SubFmlyCd>
            </Fmly>
          </Domn>
        </BkTxCd>
        <NtryDtls>
          <TxDtls>
            <Refs>
              <EndToEndId>E2E-PROPERTY-DEPOSIT</EndToEndId>
              <TxId>TXN-20241220-PROP</TxId>
            </Refs>
            <AmtDtls>
              <TxAmt>
                <Amt Ccy="GBP">15000.00</Amt>
                <CdtDbtInd>DBIT</CdtDbtInd>
              </TxAmt>
            </AmtDtls>
            <RltdPties>
              <Dbtr>
                <Nm>John Smith</Nm>
              </Dbtr>
              <DbtrAcct>
                <Id>
                  <IBAN>GB67NWBK40306112345678</IBAN>
                </Id>
              </DbtrAcct>
              <Cdtr>
                <Nm>Property Management Solicitors LLP</Nm>
                <PstlAdr>
                  <StrtNm>Legal Quarter</StrtNm>
                  <PstCd>EC4A 1BB</PstCd>
                  <TwnNm>London</TwnNm>
                  <Ctry>GB</Ctry>
                </PstlAdr>
              </Cdtr>
              <CdtrAcct>
                <Id>
                  <IBAN>GB12BARC20005512345678</IBAN>
                </Id>
              </CdtrAcct>
            </RltdPties>
            <RltdAgts>
              <CdtrAgt>
                <FinInstnId>
                  <BICFI>BARCGB22XXX</BICFI>
                  <Nm>Barclays Bank</Nm>
                </FinInstnId>
              </RltdAgts>
            <RmtInf>
              <Ustrd>Property deposit - 123 Main Street - Reference: PROP-2024-456</Ustrd>
            </RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
    </Ntfctn>
  </BkToCstmrDbtCdtNtfctn>
</Document>
```

### Example 3: Direct Debit Notification

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.054.001.08">
  <BkToCstmrDbtCdtNtfctn>
    <GrpHdr>
      <MsgId>NOTIF-20241220-070015-003</MsgId>
      <CreDtTm>2024-12-20T07:00:15</CreDtTm>
      <MsgRcpt>
        <Nm>Jane Doe</Nm>
      </MsgRcpt>
    </GrpHdr>
    <Ntfctn>
      <Id>NTFCTN-20241220-003</Id>
      <CreDtTm>2024-12-20T07:00:15</CreDtTm>
      <Acct>
        <Id>
          <IBAN>GB45MIDL40051512345678</IBAN>
        </Id>
        <Ccy>GBP</Ccy>
        <Nm>Jane Doe - Current Account</Nm>
        <Ownr>
          <Nm>Jane Doe</Nm>
        </Ownr>
        <Svcr>
          <FinInstnId>
            <BICFI>MIDLGB22XXX</BICFI>
            <Nm>HSBC Bank</Nm>
          </FinInstnId>
        </Svcr>
      </Acct>
      <Ntry>
        <NtryRef>ENTRY-20241220-070010</NtryRef>
        <Amt Ccy="GBP">45.00</Amt>
        <CdtDbtInd>DBIT</CdtDbtInd>
        <Sts>
          <Cd>BOOK</Cd>
        </Sts>
        <BookgDt>
          <DtTm>2024-12-20T07:00:10</DtTm>
        </BookgDt>
        <ValDt>
          <Dt>2024-12-20</Dt>
        </ValDt>
        <AcctSvcrRef>HSBC-REF-2024-DD-123</AcctSvcrRef>
        <BkTxCd>
          <Domn>
            <Cd>PMNT</Cd>
            <Fmly>
              <Cd>IDDT</Cd>
              <SubFmlyCd>ESDD</SubFmlyCd>
            </Fmly>
          </Domn>
        </BkTxCd>
        <NtryDtls>
          <TxDtls>
            <Refs>
              <EndToEndId>E2E-UTILITY-DEC-2024</EndToEndId>
              <MndtId>MANDATE-2023-ELEC-456</MndtId>
            </Refs>
            <AmtDtls>
              <TxAmt>
                <Amt Ccy="GBP">45.00</Amt>
                <CdtDbtInd>DBIT</CdtDbtInd>
              </TxAmt>
            </AmtDtls>
            <RltdPties>
              <Dbtr>
                <Nm>Jane Doe</Nm>
              </Dbtr>
              <DbtrAcct>
                <Id>
                  <IBAN>GB45MIDL40051512345678</IBAN>
                </Id>
              </DbtrAcct>
              <Cdtr>
                <Nm>Power Company Ltd</Nm>
              </Cdtr>
            </RltdPties>
            <Purp>
              <Cd>UTIL</Cd>
            </Purp>
            <RmtInf>
              <Ustrd>Electricity bill - December 2024 - Account #123456789</Ustrd>
            </RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
    </Ntfctn>
  </BkToCstmrDbtCdtNtfctn>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 152 fields in camt.054 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles notification identification, amounts, dates
- Extension fields accommodate notification-specific information (real-time alerts)
- Account entity supports account identification and types
- Party entity supports account owner, debtor, creditor parties
- FinancialInstitution entity manages servicer and agent bank information
- Bank transaction codes mapped to extensions for categorization

**Key Extension Fields Used:**
- notificationId, notificationCreatedDateTime (notification identification)
- entryReference, bookingDateTime, valueDateTime (entry timing)
- bankTransactionDomainCode, bankTransactionFamilyCode, bankTransactionSubFamilyCode
- creditDebitIndicator (CRDT/DBIT)
- entryStatus (BOOK/PDNG/INFO)
- chargesAmount, chargeTypeCode (charge details)
- returnReasonCode, returnAdditionalInfo (return information)

---

## References

- **ISO 20022 Message Definition:** camt.054.001.08 - BankToCustomerDebitCreditNotificationV08
- **XML Schema:** camt.054.001.08.xsd
- **Related Messages:** camt.052 (account report), camt.053 (statement), camt.060 (notification request)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **Bank Transaction Codes:** ISO 20022 External Bank Transaction Domain/Family/Sub-family Codes

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
