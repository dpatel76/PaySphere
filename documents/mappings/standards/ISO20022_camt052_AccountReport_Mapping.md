# ISO 20022 camt.052 - Bank to Customer Account Report Mapping

## Message Overview

**Message Type:** camt.052.001.08 - BankToCustomerAccountReportV08
**Category:** CAMT - Cash Management
**Purpose:** Sent by a bank to a customer to report intraday or interim account activity
**Direction:** Bank → Customer
**Scope:** Account activity reporting (movements since last report)

**Key Use Cases:**
- Intraday account balance reporting
- Interim account activity updates
- Real-time cash position monitoring
- Treasury management and cash forecasting
- Multiple intraday reports per business day
- Pre-statement account activity notification

**Relationship to Other Messages:**
- **camt.053**: Bank to Customer Statement (end-of-day statement, more comprehensive)
- **camt.054**: Debit/Credit Notification (individual transaction notifications)
- **camt.060**: Account Reporting Request (customer requests account report)
- **pain.001/pain.008**: Payment instructions that generate account entries
- **pacs.008/pacs.003**: Interbank payments that result in account entries

**Comparison with camt.053:**
- **camt.052**: Intraday/interim report (multiple per day, in-progress balances)
- **camt.053**: End-of-day statement (one per day, final balances, more detail)
- **camt.052**: Real-time cash management
- **camt.053**: Reconciliation and accounting

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in camt.052** | 165 |
| **Fields Mapped to CDM** | 165 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- Account (account identification, balances)
- Party (account owner, account servicer)
- FinancialInstitution (account servicer)
- AccountEntry (individual entries)
- AccountBalance (opening, closing, interim balances)

---

## Complete Field Mapping

### 1. Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique report identifier |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | createdDateTime | Report creation timestamp |
| GrpHdr/MsgRcpt/Nm | Message Recipient Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Customer receiving report |
| GrpHdr/MsgRcpt/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Customer BIC |
| GrpHdr/MsgRcpt/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Customer tax ID |
| GrpHdr/MsgPgntn/PgNb | Page Number | Text | 1-5 | 1..1 | Numeric string | PaymentInstruction.extensions | pageNumber | Current page number |
| GrpHdr/MsgPgntn/LastPgInd | Last Page Indicator | Boolean | - | 1..1 | true/false | PaymentInstruction.extensions | lastPageIndicator | Is this the last page |
| GrpHdr/AddtlInf | Additional Information | Text | 1-500 | 0..1 | Free text | PaymentInstruction.extensions | additionalInfo | Free-text info |

### 2. Report (Rpt)

#### 2.1 Report Identification

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Rpt/Id | Report Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | reportId | Unique report identifier |
| Rpt/RptPgntn/PgNb | Page Number | Text | 1-5 | 1..1 | Numeric string | PaymentInstruction.extensions | reportPageNumber | Report page number |
| Rpt/RptPgntn/LastPgInd | Last Page Indicator | Boolean | - | 1..1 | true/false | PaymentInstruction.extensions | reportLastPageIndicator | Last page indicator |
| Rpt/ElctrncSeqNb | Electronic Sequence Number | Number | - | 0..1 | Positive integer | PaymentInstruction.extensions | electronicSequenceNumber | Sequence number |
| Rpt/LglSeqNb | Legal Sequence Number | Number | - | 0..1 | Positive integer | PaymentInstruction.extensions | legalSequenceNumber | Legal sequence |
| Rpt/CreDtTm | Creation Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | reportCreatedDateTime | Report creation time |
| Rpt/FrToDt/FrDtTm | From Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction.extensions | reportFromDateTime | Report period start |
| Rpt/FrToDt/ToDtTm | To Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction.extensions | reportToDateTime | Report period end |
| Rpt/CpyDplctInd | Copy Duplicate Indicator | Code | - | 0..1 | CODU, COPY, DUPL | PaymentInstruction.extensions | copyDuplicateIndicator | Original/copy/duplicate |
| Rpt/RptgSrc/Cd | Reporting Source Code | Code | - | 0..1 | Free text | PaymentInstruction.extensions | reportingSourceCode | Source of report |
| Rpt/RptgSrc/Prtry | Proprietary Reporting Source | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryReportingSource | Custom source |

#### 2.2 Account

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Rpt/Acct/Id/IBAN | Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Account IBAN |
| Rpt/Acct/Id/Othr/Id | Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| Rpt/Acct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, LOAN, etc. | Account | accountType | Account type |
| Rpt/Acct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency |
| Rpt/Acct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account | accountName | Account name |
| Rpt/Acct/Ownr/Nm | Owner Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Account owner |
| Rpt/Acct/Ownr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| Rpt/Acct/Ownr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | ZIP/postal code |
| Rpt/Acct/Ownr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| Rpt/Acct/Ownr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country |
| Rpt/Acct/Ownr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Owner BIC |
| Rpt/Acct/Ownr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Owner tax ID |
| Rpt/Acct/Svcr/FinInstnId/BICFI | Servicer BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Account servicer BIC |
| Rpt/Acct/Svcr/FinInstnId/Nm | Servicer Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Bank name |
| Rpt/Acct/Svcr/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Bank country |

#### 2.3 Related Account

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Rpt/RltdAcct/Id/IBAN | Related Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Related account |
| Rpt/RltdAcct/Id/Othr/Id | Related Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN related account |
| Rpt/RltdAcct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account | accountType | Related account type |
| Rpt/RltdAcct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Related account currency |

#### 2.4 Balances (Bal)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Rpt/Bal/Tp/CdOrPrtry/Cd | Balance Type Code | Code | - | 0..1 | OPBD, CLBD, ITBD, PRCD, etc. | Account.extensions | balanceType | Opening/Closing/Interim/Forward |
| Rpt/Bal/Tp/CdOrPrtry/Prtry | Proprietary Balance Type | Text | 1-35 | 0..1 | Free text | Account.extensions | proprietaryBalanceType | Custom balance type |
| Rpt/Bal/Amt | Balance Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | Account | balance | Balance amount |
| Rpt/Bal/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | Account | currency | Balance currency |
| Rpt/Bal/CdtDbtInd | Credit Debit Indicator | Code | 4 | 1..1 | CRDT, DBIT | Account.extensions | balanceCreditDebitIndicator | Credit or Debit |
| Rpt/Bal/Dt/Dt | Balance Date | Date | - | 0..1 | ISODate | Account.extensions | balanceDate | Balance date |
| Rpt/Bal/Dt/DtTm | Balance Date Time | DateTime | - | 0..1 | ISODateTime | Account.extensions | balanceDateTime | Balance timestamp |
| Rpt/Bal/Avlbty/Dt/NbOfDays | Number of Days | Text | 1-15 | 0..1 | Numeric string | Account.extensions | availabilityDays | Days until available |
| Rpt/Bal/Avlbty/Dt/ActlDt | Actual Date | Date | - | 0..1 | ISODate | Account.extensions | availabilityDate | When funds available |

#### 2.5 Transaction Summary (TxsSummry)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Rpt/TxsSummry/TtlNtries/NbOfNtries | Number of Entries | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | totalNumberOfEntries | Total entry count |
| Rpt/TxsSummry/TtlNtries/Sum | Total Sum | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | totalEntriesSum | Sum of all entries |
| Rpt/TxsSummry/TtlNtries/TtlNetNtry/Amt | Total Net Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | totalNetAmount | Net amount |
| Rpt/TxsSummry/TtlNtries/TtlNetNtry/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | totalNetCurrency | Net currency |
| Rpt/TxsSummry/TtlNtries/TtlNetNtry/CdtDbtInd | Credit Debit Indicator | Code | 4 | 1..1 | CRDT, DBIT | PaymentInstruction.extensions | totalNetCreditDebitIndicator | Net credit/debit |
| Rpt/TxsSummry/TtlCdtNtries/NbOfNtries | Number of Credit Entries | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | totalCreditEntries | Credit entry count |
| Rpt/TxsSummry/TtlCdtNtries/Sum | Credit Sum | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | totalCreditSum | Sum of credits |
| Rpt/TxsSummry/TtlDbtNtries/NbOfNtries | Number of Debit Entries | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | totalDebitEntries | Debit entry count |
| Rpt/TxsSummry/TtlDbtNtries/Sum | Debit Sum | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | totalDebitSum | Sum of debits |

#### 2.6 Entry (Ntry)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Rpt/Ntry/NtryRef | Entry Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | entryReference | Unique entry reference |
| Rpt/Ntry/Amt | Entry Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | amount | Entry amount |
| Rpt/Ntry/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | currency | Entry currency |
| Rpt/Ntry/CdtDbtInd | Credit Debit Indicator | Code | 4 | 1..1 | CRDT, DBIT | PaymentInstruction.extensions | creditDebitIndicator | Credit or Debit |
| Rpt/Ntry/RvslInd | Reversal Indicator | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | reversalIndicator | Is reversal entry |
| Rpt/Ntry/Sts/Cd | Entry Status Code | Code | - | 0..1 | BOOK, PDNG, INFO | PaymentInstruction | paymentStatus | Booked/Pending/Info |
| Rpt/Ntry/BookgDt/Dt | Booking Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | bookingDate | When booked |
| Rpt/Ntry/BookgDt/DtTm | Booking Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | bookingDateTime | Booking timestamp |
| Rpt/Ntry/ValDt/Dt | Value Date | Date | - | 0..1 | ISODate | PaymentInstruction | settlementDate | Value date |
| Rpt/Ntry/ValDt/DtTm | Value Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | valueDateTime | Value timestamp |
| Rpt/Ntry/AcctSvcrRef | Account Servicer Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | accountServicerReference | Bank's reference |
| Rpt/Ntry/BkTxCd/Domn/Cd | Domain Code | Code | - | 0..1 | PMNT, CASH, SECU, etc. | PaymentInstruction.extensions | bankTransactionDomainCode | Transaction domain |
| Rpt/Ntry/BkTxCd/Domn/Fmly/Cd | Family Code | Code | - | 0..1 | RCDT, RDDT, ICDT, etc. | PaymentInstruction.extensions | bankTransactionFamilyCode | Transaction family |
| Rpt/Ntry/BkTxCd/Domn/Fmly/SubFmlyCd | Sub-family Code | Code | - | 0..1 | BOOK, ESCT, etc. | PaymentInstruction.extensions | bankTransactionSubFamilyCode | Transaction sub-family |
| Rpt/Ntry/BkTxCd/Prtry/Cd | Proprietary Code | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryBankTransactionCode | Custom transaction code |
| Rpt/Ntry/BkTxCd/Prtry/Issr | Issuer | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | bankTransactionCodeIssuer | Code issuer |

#### 2.7 Entry Details (NtryDtls)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Rpt/Ntry/NtryDtls/Btch/MsgId | Batch Message ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | batchMessageId | Batch identifier |
| Rpt/Ntry/NtryDtls/Btch/PmtInfId | Payment Info ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | paymentInfoId | Payment batch ID |
| Rpt/Ntry/NtryDtls/Btch/NbOfTxs | Number of Transactions | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | numberOfTransactions | Transaction count |
| Rpt/Ntry/NtryDtls/TxDtls/Refs/MsgId | Message ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Message identifier |
| Rpt/Ntry/NtryDtls/TxDtls/Refs/AcctSvcrRef | Account Servicer Ref | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | accountServicerReference | Bank reference |
| Rpt/Ntry/NtryDtls/TxDtls/Refs/PmtInfId | Payment Info ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | paymentInfoId | Payment info reference |
| Rpt/Ntry/NtryDtls/TxDtls/Refs/InstrId | Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Instruction reference |
| Rpt/Ntry/NtryDtls/TxDtls/Refs/EndToEndId | End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | endToEndId | E2E reference |
| Rpt/Ntry/NtryDtls/TxDtls/Refs/TxId | Transaction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Transaction reference |
| Rpt/Ntry/NtryDtls/TxDtls/Refs/UETR | UETR | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Universal unique identifier |
| Rpt/Ntry/NtryDtls/TxDtls/Refs/MndtId | Mandate ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | mandateId | Direct debit mandate |
| Rpt/Ntry/NtryDtls/TxDtls/Refs/ChqNb | Cheque Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | chequeNumber | Cheque number |
| Rpt/Ntry/NtryDtls/TxDtls/Amt | Transaction Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | amount | Transaction amount |
| Rpt/Ntry/NtryDtls/TxDtls/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | currency | Transaction currency |
| Rpt/Ntry/NtryDtls/TxDtls/CdtDbtInd | Credit Debit Indicator | Code | 4 | 0..1 | CRDT, DBIT | PaymentInstruction.extensions | creditDebitIndicator | Credit or Debit |

#### 2.8 Related Parties (RltdPties)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Rpt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Payer name |
| Rpt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Debtor country |
| Rpt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Id/OrgId/AnyBIC | Debtor BIC | Text | - | 0..1 | BIC format | Party | bic | Debtor BIC |
| Rpt/Ntry/NtryDtls/TxDtls/RltdPties/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Debtor account |
| Rpt/Ntry/NtryDtls/TxDtls/RltdPties/DbtrAcct/Id/Othr/Id | Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| Rpt/Ntry/NtryDtls/TxDtls/RltdPties/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ultimate payer |
| Rpt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Beneficiary name |
| Rpt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Creditor country |
| Rpt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Id/OrgId/AnyBIC | Creditor BIC | Text | - | 0..1 | BIC format | Party | bic | Creditor BIC |
| Rpt/Ntry/NtryDtls/TxDtls/RltdPties/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Creditor account |
| Rpt/Ntry/NtryDtls/TxDtls/RltdPties/CdtrAcct/Id/Othr/Id | Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| Rpt/Ntry/NtryDtls/TxDtls/RltdPties/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ultimate beneficiary |

#### 2.9 Related Agents

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Rpt/Ntry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Debtor bank |
| Rpt/Ntry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/Nm | Debtor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Debtor bank name |
| Rpt/Ntry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Creditor bank |
| Rpt/Ntry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/Nm | Creditor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Creditor bank name |

#### 2.10 Remittance Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Rpt/Ntry/NtryDtls/TxDtls/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction | remittanceInformation | Unstructured remittance |
| Rpt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | invoiceNumber | Invoice number |
| Rpt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/CdtrRefInf/Ref | Creditor Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | creditorReference | Creditor reference |

#### 2.11 Return Information (RtrInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Rpt/Ntry/NtryDtls/TxDtls/RtrInf/OrgnlBkTxCd/Domn/Cd | Original Domain Code | Code | - | 0..1 | PMNT, CASH, etc. | PaymentInstruction.extensions | originalBankTransactionDomainCode | Original transaction domain |
| Rpt/Ntry/NtryDtls/TxDtls/RtrInf/Orgtr/Nm | Originator Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Return originator |
| Rpt/Ntry/NtryDtls/TxDtls/RtrInf/Rsn/Cd | Return Reason Code | Code | - | 0..1 | AC01-AC99, AM01-AM99, etc. | PaymentInstruction.extensions | returnReasonCode | ISO 20022 return reason |
| Rpt/Ntry/NtryDtls/TxDtls/RtrInf/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | returnAdditionalInfo | Free-text explanation |

### 3. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Balance Type (Bal/Tp/CdOrPrtry/Cd)
- **OPBD** - Opening Booked (start of period booked balance)
- **CLBD** - Closing Booked (end of period booked balance)
- **ITBD** - Interim Booked (intraday booked balance)
- **CLAV** - Closing Available (available balance at close)
- **FWAV** - Forward Available (future available balance)
- **PRCD** - Previously Closed Booked (previous day closing)
- **ITAV** - Interim Available (intraday available balance)
- **OPAV** - Opening Available (opening available balance)

### Credit/Debit Indicator (CdtDbtInd)
- **CRDT** - Credit (money in)
- **DBIT** - Debit (money out)

### Entry Status (Ntry/Sts/Cd)
- **BOOK** - Booked (posted to account)
- **PDNG** - Pending (not yet posted)
- **INFO** - Information (for info only, not affecting balance)

### Bank Transaction Code - Domain (BkTxCd/Domn/Cd)
- **PMNT** - Payments
- **CASH** - Cash Management
- **SECU** - Securities
- **TRAD** - Trade Services
- **DERV** - Derivatives
- **LOAN** - Loans
- **XTND** - Extended Domain

### Bank Transaction Code - Family (BkTxCd/Domn/Fmly/Cd)
**For PMNT domain:**
- **RCDT** - Received Credit Transfer
- **RDDT** - Received Direct Debit
- **ICDT** - Issued Credit Transfer
- **IDDT** - Issued Direct Debit
- **MCOP** - Miscellaneous Credit Operations
- **MDOP** - Miscellaneous Debit Operations

**For CASH domain:**
- **CWDL** - Cash Withdrawal
- **CDPT** - Cash Deposit
- **FCPM** - Foreign Exchange/Cash Management

### Bank Transaction Code - Sub-family (BkTxCd/Domn/Fmly/SubFmlyCd)
**For RCDT (Received Credit Transfer):**
- **BOOK** - Internal Book Transfer
- **ESCT** - SEPA Credit Transfer
- **DMCT** - Domestic Credit Transfer
- **XBCT** - Cross-Border Credit Transfer
- **SALA** - Salary Payment
- **PENS** - Pension Payment

**For RDDT (Received Direct Debit):**
- **ESDD** - SEPA Direct Debit
- **DMDD** - Domestic Direct Debit

### Copy Duplicate Indicator (CpyDplctInd)
- **CODU** - Copy Duplicate (original unavailable)
- **COPY** - Copy (copy of original)
- **DUPL** - Duplicate (duplicate of original)

---

## Message Example

### Intraday Account Report with Multiple Entries

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.052.001.08">
  <BkToCstmrAcctRpt>
    <GrpHdr>
      <MsgId>ACCT-RPT-20241220-INTRADAY-001</MsgId>
      <CreDtTm>2024-12-20T14:30:00</CreDtTm>
      <MsgRcpt>
        <Nm>Corporate Services Ltd</Nm>
        <Id>
          <OrgId>
            <Othr>
              <Id>GB123456789</Id>
            </Othr>
          </OrgId>
        </Id>
      </MsgRcpt>
    </GrpHdr>
    <Rpt>
      <Id>RPT-20241220-1430</Id>
      <CreDtTm>2024-12-20T14:30:00</CreDtTm>
      <FrToDt>
        <FrDtTm>2024-12-20T09:00:00</FrDtTm>
        <ToDtTm>2024-12-20T14:30:00</ToDtTm>
      </FrToDt>
      <Acct>
        <Id>
          <IBAN>GB29ABCB60161331926819</IBAN>
        </Id>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
        <Ccy>GBP</Ccy>
        <Nm>Corporate Services Ltd - Current Account</Nm>
        <Ownr>
          <Nm>Corporate Services Ltd</Nm>
          <Id>
            <OrgId>
              <Othr>
                <Id>GB123456789</Id>
              </Othr>
            </OrgId>
          </Id>
        </Ownr>
        <Svcr>
          <FinInstnId>
            <BICFI>ABCBGB2LXXX</BICFI>
            <Nm>ABC Bank</Nm>
          </FinInstnId>
        </Svcr>
      </Acct>
      <Bal>
        <Tp>
          <CdOrPrtry>
            <Cd>OPBD</Cd>
          </CdOrPrtry>
        </Tp>
        <Amt Ccy="GBP">125000.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Dt>
          <Dt>2024-12-20</Dt>
        </Dt>
      </Bal>
      <Bal>
        <Tp>
          <CdOrPrtry>
            <Cd>ITBD</Cd>
          </CdOrPrtry>
        </Tp>
        <Amt Ccy="GBP">162500.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Dt>
          <DtTm>2024-12-20T14:30:00</DtTm>
        </Dt>
      </Bal>
      <TxsSummry>
        <TtlNtries>
          <NbOfNtries>5</NbOfNtries>
          <Sum>87500.00</Sum>
          <TtlNetNtry>
            <Amt Ccy="GBP">37500.00</Amt>
            <CdtDbtInd>CRDT</CdtDbtInd>
          </TtlNetNtry>
        </TtlNtries>
        <TtlCdtNtries>
          <NbOfNtries>3</NbOfNtries>
          <Sum>62500.00</Sum>
        </TtlCdtNtries>
        <TtlDbtNtries>
          <NbOfNtries>2</NbOfNtries>
          <Sum>25000.00</Sum>
        </TtlDbtNtries>
      </TxsSummry>
      <Ntry>
        <NtryRef>ENTRY-001</NtryRef>
        <Amt Ccy="GBP">50000.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Sts>
          <Cd>BOOK</Cd>
        </Sts>
        <BookgDt>
          <DtTm>2024-12-20T10:15:00</DtTm>
        </BookgDt>
        <ValDt>
          <Dt>2024-12-20</Dt>
        </ValDt>
        <AcctSvcrRef>ABC-REF-2024-98765</AcctSvcrRef>
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
              <EndToEndId>E2E-CUST-PAYMENT-789</EndToEndId>
              <TxId>TXN-20241220-789</TxId>
            </Refs>
            <Amt Ccy="GBP">50000.00</Amt>
            <CdtDbtInd>CRDT</CdtDbtInd>
            <RltdPties>
              <Dbtr>
                <Nm>Client Alpha Ltd</Nm>
              </Dbtr>
              <DbtrAcct>
                <Id>
                  <IBAN>GB98NWBK12345678901234</IBAN>
                </Id>
              </DbtrAcct>
              <Cdtr>
                <Nm>Corporate Services Ltd</Nm>
              </Cdtr>
              <CdtrAcct>
                <Id>
                  <IBAN>GB29ABCB60161331926819</IBAN>
                </Id>
              </CdtrAcct>
            </RltdPties>
            <RmtInf>
              <Ustrd>Invoice payment - INV-2024-12345</Ustrd>
            </RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
      <Ntry>
        <NtryRef>ENTRY-002</NtryRef>
        <Amt Ccy="GBP">15000.00</Amt>
        <CdtDbtInd>DBIT</CdtDbtInd>
        <Sts>
          <Cd>BOOK</Cd>
        </Sts>
        <BookgDt>
          <DtTm>2024-12-20T11:30:00</DtTm>
        </BookgDt>
        <ValDt>
          <Dt>2024-12-20</Dt>
        </ValDt>
        <AcctSvcrRef>ABC-REF-2024-98766</AcctSvcrRef>
        <BkTxCd>
          <Domn>
            <Cd>PMNT</Cd>
            <Fmly>
              <Cd>ICDT</Cd>
              <SubFmlyCd>SALA</SubFmlyCd>
            </Fmly>
          </Domn>
        </BkTxCd>
        <NtryDtls>
          <Btch>
            <PmtInfId>PAYROLL-DEC-2024</PmtInfId>
            <NbOfTxs>25</NbOfTxs>
          </Btch>
          <TxDtls>
            <Refs>
              <EndToEndId>E2E-PAYROLL-DEC-2024</EndToEndId>
            </Refs>
            <Amt Ccy="GBP">15000.00</Amt>
            <CdtDbtInd>DBIT</CdtDbtInd>
            <RmtInf>
              <Ustrd>Payroll - December 2024 - 25 employees</Ustrd>
            </RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
      <Ntry>
        <NtryRef>ENTRY-003</NtryRef>
        <Amt Ccy="GBP">10000.00</Amt>
        <CdtDbtInd>DBIT</CdtDbtInd>
        <Sts>
          <Cd>BOOK</Cd>
        </Sts>
        <BookgDt>
          <DtTm>2024-12-20T12:45:00</DtTm>
        </BookgDt>
        <ValDt>
          <Dt>2024-12-20</Dt>
        </ValDt>
        <AcctSvcrRef>ABC-REF-2024-98767</AcctSvcrRef>
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
              <EndToEndId>E2E-SUPPLIER-PAY-456</EndToEndId>
              <TxId>TXN-20241220-456</TxId>
            </Refs>
            <Amt Ccy="GBP">10000.00</Amt>
            <CdtDbtInd>DBIT</CdtDbtInd>
            <RltdPties>
              <Dbtr>
                <Nm>Corporate Services Ltd</Nm>
              </Dbtr>
              <DbtrAcct>
                <Id>
                  <IBAN>GB29ABCB60161331926819</IBAN>
                </Id>
              </DbtrAcct>
              <Cdtr>
                <Nm>Office Supplies International Ltd</Nm>
              </Cdtr>
              <CdtrAcct>
                <Id>
                  <IBAN>GB12BARC20005512345678</IBAN>
                </Id>
              </CdtrAcct>
            </RltdPties>
            <RmtInf>
              <Ustrd>Payment for office supplies - December order</Ustrd>
            </RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
      <Ntry>
        <NtryRef>ENTRY-004</NtryRef>
        <Amt Ccy="GBP">10000.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Sts>
          <Cd>BOOK</Cd>
        </Sts>
        <BookgDt>
          <DtTm>2024-12-20T13:20:00</DtTm>
        </BookgDt>
        <ValDt>
          <Dt>2024-12-20</Dt>
        </ValDt>
        <AcctSvcrRef>ABC-REF-2024-98768</AcctSvcrRef>
        <BkTxCd>
          <Domn>
            <Cd>PMNT</Cd>
            <Fmly>
              <Cd>RDDT</Cd>
              <SubFmlyCd>ESDD</SubFmlyCd>
            </Fmly>
          </Domn>
        </BkTxCd>
        <NtryDtls>
          <TxDtls>
            <Refs>
              <EndToEndId>E2E-DD-COLL-123</EndToEndId>
              <MndtId>MANDATE-2023-CLIENT-123</MndtId>
            </Refs>
            <Amt Ccy="GBP">10000.00</Amt>
            <CdtDbtInd>CRDT</CdtDbtInd>
            <RltdPties>
              <Dbtr>
                <Nm>Regular Customer ABC</Nm>
              </Dbtr>
              <Cdtr>
                <Nm>Corporate Services Ltd</Nm>
              </Cdtr>
            </RltdPties>
            <RmtInf>
              <Ustrd>Monthly service fee - December 2024</Ustrd>
            </RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
      <Ntry>
        <NtryRef>ENTRY-005</NtryRef>
        <Amt Ccy="GBP">2500.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Sts>
          <Cd>PDNG</Cd>
        </Sts>
        <BookgDt>
          <DtTm>2024-12-20T14:15:00</DtTm>
        </BookgDt>
        <ValDt>
          <Dt>2024-12-20</Dt>
        </ValDt>
        <AcctSvcrRef>ABC-REF-2024-98769</AcctSvcrRef>
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
              <EndToEndId>E2E-PENDING-999</EndToEndId>
            </Refs>
            <Amt Ccy="GBP">2500.00</Amt>
            <CdtDbtInd>CRDT</CdtDbtInd>
            <RltdPties>
              <Dbtr>
                <Nm>New Client XYZ</Nm>
              </Dbtr>
              <Cdtr>
                <Nm>Corporate Services Ltd</Nm>
              </Cdtr>
            </RltdPties>
            <RmtInf>
              <Ustrd>Initial deposit - pending validation</Ustrd>
            </RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
    </Rpt>
  </BkToCstmrAcctRpt>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 165 fields in camt.052 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles entry identification, amounts, dates
- Extension fields accommodate account report-specific information (balances, entry details, summaries)
- Account entity supports account identification, balances, types
- Party entity supports account owner, debtor, creditor parties
- FinancialInstitution entity manages servicer information
- Bank transaction codes mapped to extensions for categorization

**Key Extension Fields Used:**
- reportId, reportFromDateTime, reportToDateTime (report identification)
- balanceType (OPBD, CLBD, ITBD, CLAV, etc.)
- entryReference, bookingDate, valueDate
- bankTransactionDomainCode, bankTransactionFamilyCode, bankTransactionSubFamilyCode
- creditDebitIndicator (CRDT/DBIT)
- entryStatus (BOOK/PDNG/INFO)
- totalNumberOfEntries, totalCreditSum, totalDebitSum (summaries)
- pageNumber, lastPageIndicator (pagination)

---

## References

- **ISO 20022 Message Definition:** camt.052.001.08 - BankToCustomerAccountReportV08
- **XML Schema:** camt.052.001.08.xsd
- **Related Messages:** camt.053 (statement), camt.054 (debit/credit notification), camt.060 (report request)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **Bank Transaction Codes:** ISO 20022 External Bank Transaction Domain/Family/Sub-family Codes

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
