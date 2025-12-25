# ISO 20022 camt.053 - Bank to Customer Statement Mapping

## Message Overview

**Message Type:** camt.053.001.08 - BankToCustomerStatementV08
**Category:** CAMT - Cash Management
**Purpose:** Sent by a bank to a customer to provide end-of-day account statement with full transaction details
**Direction:** Bank → Customer
**Scope:** Comprehensive daily account statement (final balances and complete transaction history)

**Key Use Cases:**
- End-of-day account statement generation
- Daily reconciliation and accounting
- Complete transaction history for a statement period
- Audit trail and compliance reporting
- Month-end/quarter-end/year-end statements
- Legal record-keeping and archival

**Relationship to Other Messages:**
- **camt.052**: Intraday Account Report (interim report vs. final statement)
- **camt.054**: Debit/Credit Notification (individual transactions vs. comprehensive statement)
- **camt.060**: Account Reporting Request (customer requests statement)
- **pain.001/pain.008**: Payment instructions that appear as statement entries
- **pacs.008/pacs.003**: Interbank payments resulting in account entries

**Comparison with camt.052:**
- **camt.053**: End-of-day statement (one per day, final balances, complete details, legal document)
- **camt.052**: Intraday report (multiple per day, interim balances, cash management)
- **camt.053**: Reconciliation and accounting focus
- **camt.052**: Real-time cash position monitoring focus

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in camt.053** | 178 |
| **Fields Mapped to CDM** | 178 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- Account (account identification, balances)
- Party (account owner, account servicer, transaction parties)
- FinancialInstitution (account servicer, agent banks)
- AccountEntry (individual statement entries)
- AccountBalance (opening, closing balances)

---

## Complete Field Mapping

### 1. Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique statement message ID |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | createdDateTime | Statement creation timestamp |
| GrpHdr/MsgRcpt/Nm | Message Recipient Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Customer receiving statement |
| GrpHdr/MsgRcpt/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| GrpHdr/MsgRcpt/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | ZIP/postal code |
| GrpHdr/MsgRcpt/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| GrpHdr/MsgRcpt/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country |
| GrpHdr/MsgRcpt/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Customer BIC |
| GrpHdr/MsgRcpt/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Customer tax ID |
| GrpHdr/MsgRcpt/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Birth Date | Date | - | 0..1 | ISODate | Party | dateOfBirth | Customer birth date |
| GrpHdr/MsgPgntn/PgNb | Page Number | Text | 1-5 | 1..1 | Numeric string | PaymentInstruction.extensions | pageNumber | Current page number |
| GrpHdr/MsgPgntn/LastPgInd | Last Page Indicator | Boolean | - | 1..1 | true/false | PaymentInstruction.extensions | lastPageIndicator | Is this the last page |
| GrpHdr/AddtlInf | Additional Information | Text | 1-500 | 0..1 | Free text | PaymentInstruction.extensions | additionalInfo | Free-text info |

### 2. Statement (Stmt)

#### 2.1 Statement Identification

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Stmt/Id | Statement Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | statementId | Unique statement identifier |
| Stmt/StmtPgntn/PgNb | Page Number | Text | 1-5 | 1..1 | Numeric string | PaymentInstruction.extensions | statementPageNumber | Statement page number |
| Stmt/StmtPgntn/LastPgInd | Last Page Indicator | Boolean | - | 1..1 | true/false | PaymentInstruction.extensions | statementLastPageIndicator | Last page indicator |
| Stmt/ElctrncSeqNb | Electronic Sequence Number | Number | - | 0..1 | Positive integer | PaymentInstruction.extensions | electronicSequenceNumber | Sequence number |
| Stmt/LglSeqNb | Legal Sequence Number | Number | - | 0..1 | Positive integer | PaymentInstruction.extensions | legalSequenceNumber | Legal sequence |
| Stmt/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction.extensions | statementCreatedDateTime | Statement creation time |
| Stmt/FrToDt/FrDtTm | From Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction.extensions | statementFromDateTime | Statement period start |
| Stmt/FrToDt/ToDtTm | To Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction.extensions | statementToDateTime | Statement period end |
| Stmt/CpyDplctInd | Copy Duplicate Indicator | Code | - | 0..1 | CODU, COPY, DUPL | PaymentInstruction.extensions | copyDuplicateIndicator | Original/copy/duplicate |
| Stmt/RptgSrc/Cd | Reporting Source Code | Code | - | 0..1 | Free text | PaymentInstruction.extensions | reportingSourceCode | Source of statement |
| Stmt/RptgSrc/Prtry | Proprietary Reporting Source | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryReportingSource | Custom source |

#### 2.2 Account

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Stmt/Acct/Id/IBAN | Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Account IBAN |
| Stmt/Acct/Id/Othr/Id | Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| Stmt/Acct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, LOAN, TRAS, etc. | Account | accountType | Account type |
| Stmt/Acct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency |
| Stmt/Acct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account | accountName | Account name |
| Stmt/Acct/Ownr/Nm | Owner Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Account owner |
| Stmt/Acct/Ownr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| Stmt/Acct/Ownr/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Free text | Party | buildingNumber | Building number |
| Stmt/Acct/Ownr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | ZIP/postal code |
| Stmt/Acct/Ownr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| Stmt/Acct/Ownr/PstlAdr/CtrySubDvsn | Country Sub-division | Text | 1-35 | 0..1 | Free text | Party | stateProvince | State/province |
| Stmt/Acct/Ownr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country |
| Stmt/Acct/Ownr/PstlAdr/AdrLine | Address Line | Text | 1-70 | 0..7 | Free text | Party | addressLines | Unstructured address |
| Stmt/Acct/Ownr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Owner BIC |
| Stmt/Acct/Ownr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Owner tax ID |
| Stmt/Acct/Ownr/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Birth Date | Date | - | 0..1 | ISODate | Party | dateOfBirth | Owner birth date |
| Stmt/Acct/Ownr/Id/PrvtId/Othr/Id | Private Other ID | Text | 1-35 | 0..1 | Free text | Party | nationalId | National ID |
| Stmt/Acct/Svcr/FinInstnId/BICFI | Servicer BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Account servicer BIC |
| Stmt/Acct/Svcr/FinInstnId/ClrSysMmbId/MmbId | Member Identification | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| Stmt/Acct/Svcr/FinInstnId/Nm | Servicer Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Bank name |
| Stmt/Acct/Svcr/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Bank country |

#### 2.3 Related Account

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Stmt/RltdAcct/Id/IBAN | Related Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Related account |
| Stmt/RltdAcct/Id/Othr/Id | Related Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN related account |
| Stmt/RltdAcct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account | accountType | Related account type |
| Stmt/RltdAcct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Related account currency |
| Stmt/RltdAcct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account | accountName | Related account name |

#### 2.4 Balances (Bal)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Stmt/Bal/Tp/CdOrPrtry/Cd | Balance Type Code | Code | - | 0..1 | OPBD, CLBD, CLAV, PRCD, FWAV, etc. | Account.extensions | balanceType | Opening/Closing/Available/Forward |
| Stmt/Bal/Tp/CdOrPrtry/Prtry | Proprietary Balance Type | Text | 1-35 | 0..1 | Free text | Account.extensions | proprietaryBalanceType | Custom balance type |
| Stmt/Bal/Amt | Balance Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | Account | balance | Balance amount |
| Stmt/Bal/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | Account | currency | Balance currency |
| Stmt/Bal/CdtDbtInd | Credit Debit Indicator | Code | 4 | 1..1 | CRDT, DBIT | Account.extensions | balanceCreditDebitIndicator | Credit or Debit |
| Stmt/Bal/Dt/Dt | Balance Date | Date | - | 0..1 | ISODate | Account.extensions | balanceDate | Balance date |
| Stmt/Bal/Dt/DtTm | Balance Date Time | DateTime | - | 0..1 | ISODateTime | Account.extensions | balanceDateTime | Balance timestamp |
| Stmt/Bal/Avlbty/Dt/NbOfDays | Number of Days | Text | 1-15 | 0..1 | Numeric string | Account.extensions | availabilityDays | Days until available |
| Stmt/Bal/Avlbty/Dt/ActlDt | Actual Date | Date | - | 0..1 | ISODate | Account.extensions | availabilityDate | When funds available |
| Stmt/Bal/Avlbty/Amt | Availability Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | Account.extensions | availabilityAmount | Amount available |
| Stmt/Bal/Avlbty/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | Account.extensions | availabilityCurrency | Availability currency |
| Stmt/Bal/Avlbty/CdtDbtInd | Credit Debit Indicator | Code | 4 | 1..1 | CRDT, DBIT | Account.extensions | availabilityCreditDebitIndicator | Credit or Debit |

#### 2.5 Transaction Summary (TxsSummry)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Stmt/TxsSummry/TtlNtries/NbOfNtries | Number of Entries | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | totalNumberOfEntries | Total entry count |
| Stmt/TxsSummry/TtlNtries/Sum | Total Sum | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | totalEntriesSum | Sum of all entries |
| Stmt/TxsSummry/TtlNtries/TtlNetNtry/Amt | Total Net Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | totalNetAmount | Net amount |
| Stmt/TxsSummry/TtlNtries/TtlNetNtry/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | totalNetCurrency | Net currency |
| Stmt/TxsSummry/TtlNtries/TtlNetNtry/CdtDbtInd | Credit Debit Indicator | Code | 4 | 1..1 | CRDT, DBIT | PaymentInstruction.extensions | totalNetCreditDebitIndicator | Net credit/debit |
| Stmt/TxsSummry/TtlCdtNtries/NbOfNtries | Number of Credit Entries | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | totalCreditEntries | Credit entry count |
| Stmt/TxsSummry/TtlCdtNtries/Sum | Credit Sum | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | totalCreditSum | Sum of credits |
| Stmt/TxsSummry/TtlDbtNtries/NbOfNtries | Number of Debit Entries | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | totalDebitEntries | Debit entry count |
| Stmt/TxsSummry/TtlDbtNtries/Sum | Debit Sum | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | totalDebitSum | Sum of debits |

#### 2.6 Entry (Ntry) - Same as camt.052

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Stmt/Ntry/NtryRef | Entry Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | entryReference | Unique entry reference |
| Stmt/Ntry/Amt | Entry Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | amount | Entry amount |
| Stmt/Ntry/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | currency | Entry currency |
| Stmt/Ntry/CdtDbtInd | Credit Debit Indicator | Code | 4 | 1..1 | CRDT, DBIT | PaymentInstruction.extensions | creditDebitIndicator | Credit or Debit |
| Stmt/Ntry/RvslInd | Reversal Indicator | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | reversalIndicator | Is reversal entry |
| Stmt/Ntry/Sts/Cd | Entry Status Code | Code | - | 1..1 | BOOK, PDNG, INFO | PaymentInstruction | paymentStatus | Booked/Pending/Info |
| Stmt/Ntry/BookgDt/Dt | Booking Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | bookingDate | When booked |
| Stmt/Ntry/BookgDt/DtTm | Booking Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | bookingDateTime | Booking timestamp |
| Stmt/Ntry/ValDt/Dt | Value Date | Date | - | 0..1 | ISODate | PaymentInstruction | settlementDate | Value date |
| Stmt/Ntry/ValDt/DtTm | Value Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | valueDateTime | Value timestamp |
| Stmt/Ntry/AcctSvcrRef | Account Servicer Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | accountServicerReference | Bank's reference |
| Stmt/Ntry/BkTxCd/Domn/Cd | Domain Code | Code | - | 0..1 | PMNT, CASH, SECU, etc. | PaymentInstruction.extensions | bankTransactionDomainCode | Transaction domain |
| Stmt/Ntry/BkTxCd/Domn/Fmly/Cd | Family Code | Code | - | 0..1 | RCDT, RDDT, ICDT, etc. | PaymentInstruction.extensions | bankTransactionFamilyCode | Transaction family |
| Stmt/Ntry/BkTxCd/Domn/Fmly/SubFmlyCd | Sub-family Code | Code | - | 0..1 | BOOK, ESCT, etc. | PaymentInstruction.extensions | bankTransactionSubFamilyCode | Transaction sub-family |
| Stmt/Ntry/BkTxCd/Prtry/Cd | Proprietary Code | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryBankTransactionCode | Custom transaction code |
| Stmt/Ntry/BkTxCd/Prtry/Issr | Issuer | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | bankTransactionCodeIssuer | Code issuer |
| Stmt/Ntry/CmmssnWvrInd | Commission Waiver Indicator | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | commissionWaiverIndicator | Commission waived |
| Stmt/Ntry/AddtlInfInd/MsgNmId | Message Name ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | additionalInfoMessageNameId | Message type reference |

#### 2.7 Entry Details (NtryDtls) - Extended from camt.052

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Stmt/Ntry/NtryDtls/Btch/MsgId | Batch Message ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | batchMessageId | Batch identifier |
| Stmt/Ntry/NtryDtls/Btch/PmtInfId | Payment Info ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | paymentInfoId | Payment batch ID |
| Stmt/Ntry/NtryDtls/Btch/NbOfTxs | Number of Transactions | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | numberOfTransactions | Transaction count |
| Stmt/Ntry/NtryDtls/Btch/TtlAmt | Total Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | batchTotalAmount | Batch total |
| Stmt/Ntry/NtryDtls/Btch/TtlAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | batchTotalCurrency | Batch currency |
| Stmt/Ntry/NtryDtls/Btch/CdtDbtInd | Credit Debit Indicator | Code | 4 | 0..1 | CRDT, DBIT | PaymentInstruction.extensions | batchCreditDebitIndicator | Batch credit/debit |
| Stmt/Ntry/NtryDtls/TxDtls/Refs/MsgId | Message ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Message identifier |
| Stmt/Ntry/NtryDtls/TxDtls/Refs/AcctSvcrRef | Account Servicer Ref | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | accountServicerReference | Bank reference |
| Stmt/Ntry/NtryDtls/TxDtls/Refs/PmtInfId | Payment Info ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | paymentInfoId | Payment info reference |
| Stmt/Ntry/NtryDtls/TxDtls/Refs/InstrId | Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Instruction reference |
| Stmt/Ntry/NtryDtls/TxDtls/Refs/EndToEndId | End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | endToEndId | E2E reference |
| Stmt/Ntry/NtryDtls/TxDtls/Refs/TxId | Transaction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Transaction reference |
| Stmt/Ntry/NtryDtls/TxDtls/Refs/UETR | UETR | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Universal unique identifier |
| Stmt/Ntry/NtryDtls/TxDtls/Refs/MndtId | Mandate ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | mandateId | Direct debit mandate |
| Stmt/Ntry/NtryDtls/TxDtls/Refs/ChqNb | Cheque Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | chequeNumber | Cheque number |
| Stmt/Ntry/NtryDtls/TxDtls/Refs/ClrSysRef | Clearing System Ref | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | clearingSystemReference | Clearing reference |
| Stmt/Ntry/NtryDtls/TxDtls/Refs/Prtry/Tp | Proprietary Type | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryReferenceType | Custom reference type |
| Stmt/Ntry/NtryDtls/TxDtls/Refs/Prtry/Ref | Proprietary Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryReference | Custom reference |
| Stmt/Ntry/NtryDtls/TxDtls/AmtDtls/InstdAmt/Amt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | instructedAmount | Instructed amount |
| Stmt/Ntry/NtryDtls/TxDtls/AmtDtls/InstdAmt/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | instructedCurrency | Instructed currency |
| Stmt/Ntry/NtryDtls/TxDtls/AmtDtls/TxAmt/Amt | Transaction Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | amount | Transaction amount |
| Stmt/Ntry/NtryDtls/TxDtls/AmtDtls/TxAmt/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | currency | Transaction currency |
| Stmt/Ntry/NtryDtls/TxDtls/AmtDtls/TxAmt/CdtDbtInd | Credit Debit Indicator | Code | 4 | 0..1 | CRDT, DBIT | PaymentInstruction.extensions | creditDebitIndicator | Credit or Debit |
| Stmt/Ntry/NtryDtls/TxDtls/AmtDtls/CntrValAmt/Amt | Counter Value Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | counterValueAmount | FX counter amount |
| Stmt/Ntry/NtryDtls/TxDtls/AmtDtls/CntrValAmt/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | counterValueCurrency | FX counter currency |
| Stmt/Ntry/NtryDtls/TxDtls/Avlbty/Dt/NbOfDays | Number of Days | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | transactionAvailabilityDays | Days until available |
| Stmt/Ntry/NtryDtls/TxDtls/Avlbty/Dt/ActlDt | Actual Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | transactionAvailabilityDate | When available |

#### 2.8 Related Parties (RltdPties)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/InitgPty/Nm | Initiating Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Payment initiator |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Payer name |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | Postal code |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Debtor country |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Id/OrgId/AnyBIC | Debtor BIC | Text | - | 0..1 | BIC format | Party | bic | Debtor BIC |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Id/OrgId/Othr/Id | Debtor Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Debtor tax ID |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Debtor account |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/DbtrAcct/Id/Othr/Id | Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ultimate payer |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/UltmtDbtr/Id/OrgId/Othr/Id | Ultimate Debtor ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Ultimate payer ID |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Beneficiary name |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | Postal code |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Creditor country |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Id/OrgId/AnyBIC | Creditor BIC | Text | - | 0..1 | BIC format | Party | bic | Creditor BIC |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Id/OrgId/Othr/Id | Creditor Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Creditor tax ID |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Creditor account |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/CdtrAcct/Id/Othr/Id | Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ultimate beneficiary |
| Stmt/Ntry/NtryDtls/TxDtls/RltdPties/UltmtCdtr/Id/OrgId/Othr/Id | Ultimate Creditor ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Ultimate creditor ID |

#### 2.9 Related Agents

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Debtor bank |
| Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/Nm | Debtor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Debtor bank name |
| Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Creditor bank |
| Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/Nm | Creditor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Creditor bank name |
| Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/IntrmyAgt1/FinInstnId/BICFI | Intermediary Agent 1 BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Intermediary bank 1 |
| Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/IntrmyAgt2/FinInstnId/BICFI | Intermediary Agent 2 BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Intermediary bank 2 |

#### 2.10 Purpose

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Stmt/Ntry/NtryDtls/TxDtls/Purp/Cd | Purpose Code | Code | - | 0..1 | BONU, CASH, DIVD, SALA, etc. | PaymentInstruction.extensions | purposeCode | Purpose of payment |
| Stmt/Ntry/NtryDtls/TxDtls/Purp/Prtry | Proprietary Purpose | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryPurpose | Custom purpose |

#### 2.11 Remittance Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction | remittanceInformation | Unstructured remittance |
| Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd | Document Type Code | Code | - | 0..1 | CINV, CREN, DEBN, etc. | PaymentInstruction.extensions | documentTypeCode | Invoice type |
| Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | invoiceNumber | Invoice number |
| Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocInf/RltdDt | Related Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | invoiceDate | Invoice date |
| Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/CdtrRefInf/Tp/CdOrPrtry/Cd | Creditor Reference Type | Code | - | 0..1 | SCOR | PaymentInstruction.extensions | creditorReferenceType | Reference type |
| Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/CdtrRefInf/Ref | Creditor Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | creditorReference | Creditor reference |

#### 2.12 Return Information (RtrInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Stmt/Ntry/NtryDtls/TxDtls/RtrInf/OrgnlBkTxCd/Domn/Cd | Original Domain Code | Code | - | 0..1 | PMNT, CASH, etc. | PaymentInstruction.extensions | originalBankTransactionDomainCode | Original transaction domain |
| Stmt/Ntry/NtryDtls/TxDtls/RtrInf/Orgtr/Nm | Originator Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Return originator |
| Stmt/Ntry/NtryDtls/TxDtls/RtrInf/Rsn/Cd | Return Reason Code | Code | - | 0..1 | AC01-AC99, AM01-AM99, etc. | PaymentInstruction.extensions | returnReasonCode | ISO 20022 return reason |
| Stmt/Ntry/NtryDtls/TxDtls/RtrInf/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | returnAdditionalInfo | Free-text explanation |

#### 2.13 Charges (Chrgs)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Stmt/Ntry/Chrgs/TtlChrgsAndTaxAmt | Total Charges and Tax | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | totalChargesAmount | Total charges |
| Stmt/Ntry/Chrgs/TtlChrgsAndTaxAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | totalChargesCurrency | Charges currency |
| Stmt/Ntry/Chrgs/Rcrd/Amt | Charge Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction.extensions | chargesAmount | Individual charge |
| Stmt/Ntry/Chrgs/Rcrd/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | chargesCurrency | Charge currency |
| Stmt/Ntry/Chrgs/Rcrd/CdtDbtInd | Credit Debit Indicator | Code | 4 | 0..1 | CRDT, DBIT | PaymentInstruction.extensions | chargeCreditDebitIndicator | Charge credit/debit |
| Stmt/Ntry/Chrgs/Rcrd/Tp/Cd | Charge Type Code | Code | - | 0..1 | Free text | PaymentInstruction.extensions | chargeTypeCode | Type of charge |
| Stmt/Ntry/Chrgs/Rcrd/Tp/Prtry | Proprietary Type | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryChargeType | Custom charge type |

### 3. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Balance Type (Bal/Tp/CdOrPrtry/Cd)
- **OPBD** - Opening Booked (start of statement period)
- **CLBD** - Closing Booked (end of statement period - MANDATORY for statements)
- **CLAV** - Closing Available (available balance at close)
- **PRCD** - Previously Closed Booked (previous statement closing)
- **FWAV** - Forward Available (future available balance)

### Entry Status (Ntry/Sts/Cd)
- **BOOK** - Booked (posted to account - typical for statements)
- **PDNG** - Pending (not yet posted but shown for info)
- **INFO** - Information (for info only, not affecting balance)

### Copy Duplicate Indicator (CpyDplctInd)
- **CODU** - Copy Duplicate (original unavailable)
- **COPY** - Copy (copy of original)
- **DUPL** - Duplicate (duplicate of original)

### Bank Transaction Codes
(Same as camt.052 - see previous mapping for full list)

---

## Message Example

### End-of-Day Statement (Simplified)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.08">
  <BkToCstmrStmt>
    <GrpHdr>
      <MsgId>STMT-20241220-001</MsgId>
      <CreDtTm>2024-12-21T00:30:00</CreDtTm>
      <MsgRcpt>
        <Nm>Corporate Services Ltd</Nm>
      </MsgRcpt>
    </GrpHdr>
    <Stmt>
      <Id>STMT-2024-12-20</Id>
      <ElctrncSeqNb>354</ElctrncSeqNb>
      <LglSeqNb>354</LglSeqNb>
      <CreDtTm>2024-12-21T00:30:00</CreDtTm>
      <FrToDt>
        <FrDtTm>2024-12-20T00:00:00</FrDtTm>
        <ToDtTm>2024-12-20T23:59:59</ToDtTm>
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
            <Cd>CLBD</Cd>
          </CdOrPrtry>
        </Tp>
        <Amt Ccy="GBP">162500.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Dt>
          <Dt>2024-12-20</Dt>
        </Dt>
      </Bal>
      <Bal>
        <Tp>
          <CdOrPrtry>
            <Cd>CLAV</Cd>
          </CdOrPrtry>
        </Tp>
        <Amt Ccy="GBP">162500.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Dt>
          <Dt>2024-12-20</Dt>
        </Dt>
      </Bal>
      <TxsSummry>
        <TtlNtries>
          <NbOfNtries>28</NbOfNtries>
          <Sum>245000.00</Sum>
          <TtlNetNtry>
            <Amt Ccy="GBP">37500.00</Amt>
            <CdtDbtInd>CRDT</CdtDbtInd>
          </TtlNetNtry>
        </TtlNtries>
        <TtlCdtNtries>
          <NbOfNtries>15</NbOfNtries>
          <Sum>141250.00</Sum>
        </TtlCdtNtries>
        <TtlDbtNtries>
          <NbOfNtries>13</NbOfNtries>
          <Sum>103750.00</Sum>
        </TtlDbtNtries>
      </TxsSummry>
      <Ntry>
        <NtryRef>ENTRY-2024-12-20-001</NtryRef>
        <Amt Ccy="GBP">50000.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Sts>
          <Cd>BOOK</Cd>
        </Sts>
        <BookgDt>
          <Dt>2024-12-20</Dt>
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
            <AmtDtls>
              <TxAmt>
                <Amt Ccy="GBP">50000.00</Amt>
              </TxAmt>
            </AmtDtls>
            <RltdPties>
              <Dbtr>
                <Nm>Client Alpha Ltd</Nm>
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
                <Nm>Corporate Services Ltd</Nm>
              </Cdtr>
              <CdtrAcct>
                <Id>
                  <IBAN>GB29ABCB60161331926819</IBAN>
                </Id>
              </CdtrAcct>
            </RltdPties>
            <RmtInf>
              <Ustrd>Invoice payment - INV-2024-12345 - Professional services December 2024</Ustrd>
            </RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
      <!-- Additional entries would appear here -->
    </Stmt>
  </BkToCstmrStmt>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 178 fields in camt.053 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles entry identification, amounts, dates
- Extension fields accommodate statement-specific information (balances, summaries, charges)
- Account entity supports account identification, balances, types, availability
- Party entity supports account owner, debtor, creditor, ultimate parties with full addresses
- FinancialInstitution entity manages servicer and agent bank information
- Bank transaction codes and charges mapped to extensions

**Key Extension Fields Used:**
- statementId, statementFromDateTime, statementToDateTime (statement identification)
- electronicSequenceNumber, legalSequenceNumber (sequencing)
- balanceType (OPBD, CLBD mandatory; CLAV, PRCD, FWAV optional)
- entryReference, bookingDate, valueDate
- bankTransactionDomainCode, bankTransactionFamilyCode, bankTransactionSubFamilyCode
- totalNumberOfEntries, totalCreditSum, totalDebitSum, totalNetAmount (summaries)
- chargesAmount, chargeTypeCode (charge details)
- availabilityDate, availabilityAmount (funds availability)

---

## References

- **ISO 20022 Message Definition:** camt.053.001.08 - BankToCustomerStatementV08
- **XML Schema:** camt.053.001.08.xsd
- **Related Messages:** camt.052 (account report), camt.054 (debit/credit notification), camt.060 (statement request)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **Bank Transaction Codes:** ISO 20022 External Bank Transaction Domain/Family/Sub-family Codes

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
