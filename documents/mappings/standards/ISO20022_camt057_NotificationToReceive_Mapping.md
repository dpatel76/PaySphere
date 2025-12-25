# ISO 20022 camt.057 - Notification to Receive Mapping

## Message Overview

**Message Type:** camt.057.001.06 - NotificationToReceiveV06
**Category:** CAMT - Cash Management
**Purpose:** Sent by an account owner or party authorized by the account owner to the account servicing institution to notify the receipt of funds
**Direction:** Customer → FI (Account Owner to Bank)
**Scope:** Pre-notification of incoming payment to prepare for receipt

**Key Use Cases:**
- Notify bank of expected incoming payment
- Pre-advise large value receipts for liquidity planning
- Prepare account for incoming funds
- Support reconciliation of expected vs. actual receipts
- Enable bank to prepare for incoming SWIFT/wire transfers
- Facilitate straight-through processing of incoming payments
- Support trade finance and supply chain finance pre-notifications

**Relationship to Other Messages:**
- **pacs.008**: Actual credit transfer that follows notification
- **camt.054**: Debit/credit notification confirming receipt
- **camt.058**: Cancellation of notification to receive
- **MT 210**: SWIFT equivalent for notice to receive
- **pain.001**: Related outbound payment from counterparty
- **camt.052/053**: Account statement showing received funds

**Comparison with Related Messages:**
- **camt.057**: Pre-notification of expected receipt (before funds arrive)
- **camt.054**: Actual notification of received funds (after funds arrive)
- **camt.058**: Cancellation of camt.057 notification
- **MT 210**: SWIFT MT equivalent

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in camt.057** | 88 |
| **Fields Mapped to CDM** | 88 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- Party (account owner, creditor, debtor, ultimate parties)
- Account (creditor account receiving funds)
- FinancialInstitution (account servicing institution, agents)
- Settlement (settlement information)

---

## Complete Field Mapping

### 1. Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique message ID |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | creationDateTime | Message creation timestamp |
| GrpHdr/MsgSndr/Nm | Message Sender Name | Text | 1-140 | 0..1 | Free text | Party | name | Sender name |
| GrpHdr/MsgSndr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Sender country |
| GrpHdr/MsgSndr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Sender BIC |
| GrpHdr/MsgRcpt/Nm | Message Recipient Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Recipient bank name |
| GrpHdr/MsgRcpt/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Recipient bank BIC |

### 2. Account (Acct)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Acct/Id/IBAN | Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Receiving account IBAN |
| Acct/Id/Othr/Id | Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| Acct/Id/Othr/SchmeNm/Cd | Scheme Name Code | Code | - | 0..1 | BBAN, UPIC, etc. | Account.extensions | accountScheme | Account ID scheme |
| Acct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account.extensions | accountTypeCode | Account type |
| Acct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account.extensions | accountCurrency | Account currency |
| Acct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account.extensions | accountName | Account name |
| Acct/Ownr/Nm | Owner Name | Text | 1-140 | 0..1 | Free text | Party | name | Account owner name |
| Acct/Ownr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | postalAddress.streetName | Owner street |
| Acct/Ownr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalAddress.postCode | Owner postal code |
| Acct/Ownr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | postalAddress.townName | Owner city |
| Acct/Ownr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Owner country |
| Acct/Ownr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Owner BIC |
| Acct/Ownr/Id/PrvtId/Othr/Id | Private ID | Text | 1-35 | 0..1 | Free text | Party | identificationNumber | Owner ID |
| Acct/Svcr/FinInstnId/BICFI | Servicer BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Account servicing bank |
| Acct/Svcr/FinInstnId/Nm | Servicer Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Servicing bank name |

### 3. Notification (Ntfctn)

#### 3.1 Notification Identification

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Id | Notification ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | notificationId | Unique notification ID |
| Ntfctn/CreDtTm | Creation Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | notificationCreatedDateTime | Notification timestamp |
| Ntfctn/FrToDt/FrDtTm | From Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | expectedReceiptFromDateTime | Expected receipt window start |
| Ntfctn/FrToDt/ToDtTm | To Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | expectedReceiptToDateTime | Expected receipt window end |

#### 3.2 Entry Information (Ntry)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Ntry/Amt | Entry Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | instructedAmount | Expected amount |
| Ntfctn/Ntry/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | instructedAmount.currency | Amount currency |
| Ntfctn/Ntry/CdtDbtInd | Credit Debit Indicator | Code | 4 | 1..1 | CRDT, DBIT | PaymentInstruction.extensions | creditDebitIndicator | Always CRDT for receipt |
| Ntfctn/Ntry/Sts/Cd | Status Code | Code | - | 0..1 | BOOK, PDNG, INFO | PaymentInstruction | currentStatus | Entry status |
| Ntfctn/Ntry/BookgDt/Dt | Booking Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | bookingDate | Expected booking date |
| Ntfctn/Ntry/BookgDt/DtTm | Booking Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | bookingDateTime | Expected booking timestamp |
| Ntfctn/Ntry/ValDt/Dt | Value Date | Date | - | 0..1 | ISODate | PaymentInstruction | valueDate | Expected value date |
| Ntfctn/Ntry/ValDt/DtTm | Value Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | valueDateTime | Value timestamp |
| Ntfctn/Ntry/AcctSvcrRef | Account Servicer Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | accountServicerReference | Bank reference |

#### 3.3 Entry Details (NtryDtls)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/MsgId | Message ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | relatedMessageId | Related payment message ID |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/AcctSvcrRef | Account Servicer Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | accountServicerReference | Bank reference |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/PmtInfId | Payment Information ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | paymentInformationId | Payment info ID |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/InstrId | Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Instruction reference |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/EndToEndId | End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | endToEndId | E2E reference |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/TxId | Transaction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Transaction reference |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/UETR | UETR | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Unique end-to-end transaction reference |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/MndtId | Mandate ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | mandateId | Direct debit mandate |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/ChqNb | Cheque Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | chequeNumber | Cheque number |
| Ntfctn/Ntry/NtryDtls/TxDtls/Refs/ClrSysRef | Clearing System Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | clearingSystemReference | Clearing system ref |

#### 3.4 Amount Details (AmtDtls)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Ntry/NtryDtls/TxDtls/AmtDtls/InstdAmt/Amt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | instructedAmount | Original instructed amount |
| Ntfctn/Ntry/NtryDtls/TxDtls/AmtDtls/InstdAmt/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | instructedAmount.currency | Instructed currency |
| Ntfctn/Ntry/NtryDtls/TxDtls/AmtDtls/TxAmt/Amt | Transaction Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | transactionAmount | Transaction amount |
| Ntfctn/Ntry/NtryDtls/TxDtls/AmtDtls/TxAmt/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | transactionCurrency | Transaction currency |

#### 3.5 Related Parties

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Free text | Party | name | Ultimate debtor |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/UltmtDbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Ultimate debtor country |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/UltmtDbtr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Ultimate debtor BIC |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | name | Debtor/payer |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | postalAddress.streetName | Debtor street |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalAddress.postCode | Debtor postal code |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | postalAddress.townName | Debtor city |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Debtor country |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Debtor BIC |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Id/PrvtId/Othr/Id | Private ID | Text | 1-35 | 0..1 | Free text | Party | identificationNumber | Debtor private ID |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Debtor account |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/DbtrAcct/Id/Othr/Id | Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN debtor account |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Free text | Party | name | Ultimate creditor |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/UltmtCdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Ultimate creditor country |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/UltmtCdtr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Ultimate creditor BIC |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | name | Creditor/receiver |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | postalAddress.streetName | Creditor street |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalAddress.postCode | Creditor postal code |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | postalAddress.townName | Creditor city |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Creditor country |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Creditor BIC |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Id/PrvtId/Othr/Id | Private ID | Text | 1-35 | 0..1 | Free text | Party | identificationNumber | Creditor private ID |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Creditor account (same as Acct) |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdPties/CdtrAcct/Id/Othr/Id | Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN creditor account |

#### 3.6 Related Agents

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Debtor's bank |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/Nm | Debtor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Debtor bank name |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Creditor's bank |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/Nm | Creditor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Creditor bank name |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdAgts/IntrmyAgt1/FinInstnId/BICFI | Intermediary Agent 1 BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | First intermediary |
| Ntfctn/Ntry/NtryDtls/TxDtls/RltdAgts/IntrmyAgt1/FinInstnId/Nm | Intermediary Agent 1 Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | First intermediary name |

#### 3.7 Purpose and Remittance

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Ntry/NtryDtls/TxDtls/Purp/Cd | Purpose Code | Code | 4 | 0..1 | ISO 20022 codes | PaymentInstruction | purpose | Purpose code |
| Ntfctn/Ntry/NtryDtls/TxDtls/Purp/Prtry | Proprietary Purpose | Text | 1-35 | 0..1 | Free text | PaymentInstruction | purposeDescription | Proprietary purpose |
| Ntfctn/Ntry/NtryDtls/TxDtls/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction | remittanceInformation | Remittance information |
| Ntfctn/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd | Document Type Code | Code | - | 0..1 | MSIN, CINV, etc. | PaymentInstruction.extensions | documentTypeCode | Document type |
| Ntfctn/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | invoiceNumber | Invoice/document number |
| Ntfctn/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocInf/RltdDt | Related Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | invoiceDate | Document date |

#### 3.8 Return Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Ntfctn/Ntry/NtryDtls/TxDtls/RtrInf/OrgnlBkTxCd/Prtry/Cd | Original Bank Transaction Code | Code | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalBankTransactionCode | Original transaction code |
| Ntfctn/Ntry/NtryDtls/TxDtls/RtrInf/Rsn/Cd | Return Reason Code | Code | - | 0..1 | ISO 20022 codes | PaymentInstruction.extensions | returnReasonCode | Reason for return |
| Ntfctn/Ntry/NtryDtls/TxDtls/RtrInf/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | returnAdditionalInfo | Return details |

### 4. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Credit Debit Indicator (CdtDbtInd)
- **CRDT** - Credit (receipt of funds - standard for camt.057)
- **DBIT** - Debit (not typical for notification to receive)

### Entry Status (Sts/Cd)
- **BOOK** - Booked
- **PDNG** - Pending
- **INFO** - Information

### Account Type (Tp/Cd)
- **CACC** - Current/Checking Account
- **SVGS** - Savings Account
- **LOAN** - Loan Account
- **CARD** - Card Account

### Purpose Codes (Purp/Cd)
- **CBFF** - Capital Building
- **CDCD** - Credit Card Payment
- **COMM** - Commission
- **GDDS** - Purchase/Sale of Goods
- **INTC** - Intra-Company Payment
- **SALA** - Salary Payment
- **SECU** - Securities
- **SUPP** - Supplier Payment
- **TRAD** - Trade Services

### Document Type Code (RfrdDocInf/Tp/CdOrPrtry/Cd)
- **MSIN** - Metered Service Invoice
- **CINV** - Commercial Invoice
- **DNFA** - Debit Note Related to Financial Adjustment
- **CMCN** - Commercial Contract
- **SBIN** - Self Billed Invoice
- **RADM** - Remittance Advice Message

---

## Message Examples

### Example 1: Pre-notification of Large Wire Receipt

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.057.001.06">
  <NtfctnToRcv>
    <GrpHdr>
      <MsgId>NTR-20241220-001</MsgId>
      <CreDtTm>2024-12-20T09:00:00</CreDtTm>
      <MsgSndr>
        <Nm>Global Corporation Treasury</Nm>
        <Id>
          <OrgId>
            <AnyBIC>GLBCUS33XXX</AnyBIC>
          </OrgId>
        </Id>
      </MsgSndr>
      <MsgRcpt>
        <Nm>Bank of America</Nm>
        <Id>
          <OrgId>
            <AnyBIC>BOFAUS3NXXX</AnyBIC>
          </OrgId>
        </Id>
      </MsgRcpt>
    </GrpHdr>
    <Acct>
      <Id>
        <Othr>
          <Id>1234567890</Id>
        </Othr>
      </Id>
      <Tp>
        <Cd>CACC</Cd>
      </Tp>
      <Ccy>USD</Ccy>
      <Nm>Operating Account</Nm>
      <Ownr>
        <Nm>Global Corporation</Nm>
        <PstlAdr>
          <StrtNm>Corporate Plaza</StrtNm>
          <PstCd>10001</PstCd>
          <TwnNm>New York</TwnNm>
          <Ctry>US</Ctry>
        </PstlAdr>
      </Ownr>
      <Svcr>
        <FinInstnId>
          <BICFI>BOFAUS3NXXX</BICFI>
          <Nm>Bank of America</Nm>
        </FinInstnId>
      </Svcr>
    </Acct>
    <Ntfctn>
      <Id>NTR-WIRE-20241220-001</Id>
      <CreDtTm>2024-12-20T09:00:00</CreDtTm>
      <FrToDt>
        <FrDtTm>2024-12-20T14:00:00</FrDtTm>
        <ToDtTm>2024-12-20T16:00:00</ToDtTm>
      </FrToDt>
      <Ntry>
        <Amt Ccy="USD">5000000.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Sts>
          <Cd>INFO</Cd>
        </Sts>
        <ValDt>
          <Dt>2024-12-20</Dt>
        </ValDt>
        <NtryDtls>
          <TxDtls>
            <Refs>
              <EndToEndId>E2E-WIRE-RECEIPT-20241220</EndToEndId>
              <TxId>TXN-INCOMING-WIRE-001</TxId>
            </Refs>
            <RltdPties>
              <Dbtr>
                <Nm>European Supplier Ltd</Nm>
                <PstlAdr>
                  <TwnNm>London</TwnNm>
                  <Ctry>GB</Ctry>
                </PstlAdr>
              </Dbtr>
              <DbtrAcct>
                <Id>
                  <IBAN>GB29NWBK60161331926819</IBAN>
                </Id>
              </DbtrAcct>
              <Cdtr>
                <Nm>Global Corporation</Nm>
              </Cdtr>
              <CdtrAcct>
                <Id>
                  <Othr>
                    <Id>1234567890</Id>
                  </Othr>
                </Id>
              </CdtrAcct>
            </RltdPties>
            <RltdAgts>
              <DbtrAgt>
                <FinInstnId>
                  <BICFI>NWBKGB2LXXX</BICFI>
                  <Nm>NatWest Bank</Nm>
                </FinInstnId>
              </DbtrAgt>
              <CdtrAgt>
                <FinInstnId>
                  <BICFI>BOFAUS3NXXX</BICFI>
                  <Nm>Bank of America</Nm>
                </FinInstnId>
              </CdtrAgt>
            </RltdAgts>
            <Purp>
              <Cd>TRAD</Cd>
            </Purp>
            <RmtInf>
              <Ustrd>Trade Settlement for Contract TR-2024-5678</Ustrd>
            </RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
    </Ntfctn>
  </NtfctnToRcv>
</Document>
```

### Example 2: Pre-notification of Customer Payment

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.057.001.06">
  <NtfctnToRcv>
    <GrpHdr>
      <MsgId>NTR-20241220-CUST-002</MsgId>
      <CreDtTm>2024-12-20T10:30:00</CreDtTm>
    </GrpHdr>
    <Acct>
      <Id>
        <Othr>
          <Id>9876543210</Id>
        </Othr>
      </Id>
      <Tp>
        <Cd>CACC</Cd>
      </Tp>
      <Ccy>USD</Ccy>
      <Ownr>
        <Nm>ABC Services Inc</Nm>
      </Ownr>
      <Svcr>
        <FinInstnId>
          <BICFI>BOFAUS3NXXX</BICFI>
        </FinInstnId>
      </Svcr>
    </Acct>
    <Ntfctn>
      <Id>NTR-PAYMENT-20241220-002</Id>
      <CreDtTm>2024-12-20T10:30:00</CreDtTm>
      <Ntry>
        <Amt Ccy="USD">25000.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Sts>
          <Cd>INFO</Cd>
        </Sts>
        <ValDt>
          <Dt>2024-12-21</Dt>
        </ValDt>
        <NtryDtls>
          <TxDtls>
            <Refs>
              <EndToEndId>E2E-CUSTOMER-PMT-20241220</EndToEndId>
            </Refs>
            <AmtDtls>
              <InstdAmt>
                <Amt Ccy="USD">25000.00</Amt>
              </InstdAmt>
            </AmtDtls>
            <RltdPties>
              <Dbtr>
                <Nm>XYZ Manufacturing Co</Nm>
                <PstlAdr>
                  <StrtNm>Industrial Drive</StrtNm>
                  <PstCd>30301</PstCd>
                  <TwnNm>Atlanta</TwnNm>
                  <Ctry>US</Ctry>
                </PstlAdr>
              </Dbtr>
              <Cdtr>
                <Nm>ABC Services Inc</Nm>
              </Cdtr>
              <CdtrAcct>
                <Id>
                  <Othr>
                    <Id>9876543210</Id>
                  </Othr>
                </Id>
              </CdtrAcct>
            </RltdPties>
            <RmtInf>
              <Ustrd>Payment for Services - Invoice #INV-2024-1234</Ustrd>
              <Strd>
                <RfrdDocInf>
                  <Tp>
                    <CdOrPrtry>
                      <Cd>CINV</Cd>
                    </CdOrPrtry>
                  </Tp>
                  <Nb>INV-2024-1234</Nb>
                  <RltdDt>2024-12-15</RltdDt>
                </RfrdDocInf>
              </Strd>
            </RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
    </Ntfctn>
  </NtfctnToRcv>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 88 fields in camt.057 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles notification identification, amounts, dates, references
- Extension fields accommodate notification-specific information (notification ID, expected receipt windows)
- Party entity supports account owner, message sender/recipient, debtor, creditor, ultimate parties
- Account entity handles IBAN and non-IBAN account identifiers with account types and currency
- FinancialInstitution entity manages servicing institution and agent information
- Settlement information supported through existing fields

**Key Extension Fields Used:**
- notificationId, notificationCreatedDateTime
- expectedReceiptFromDateTime, expectedReceiptToDateTime
- creditDebitIndicator, bookingDate, bookingDateTime
- accountServicerReference, relatedMessageId
- paymentInformationId, clearingSystemReference
- chequeNumber, documentTypeCode
- returnReasonCode, returnAdditionalInfo
- accountScheme, accountTypeCode, accountCurrency, accountName

---

## References

- **ISO 20022 Message Definition:** camt.057.001.06 - NotificationToReceiveV06
- **XML Schema:** camt.057.001.06.xsd
- **Related Messages:** pacs.008 (credit transfer), camt.054 (debit/credit notification), camt.058 (notification cancellation), MT 210 (notice to receive)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **Purpose Codes:** ISO 20022 External Purpose Code

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
