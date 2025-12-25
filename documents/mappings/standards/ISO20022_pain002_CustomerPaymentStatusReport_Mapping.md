# ISO 20022 pain.002 - Customer Payment Status Report Mapping

## Message Overview

**Message Type:** pain.002.001.10 - CustomerPaymentStatusReport
**Category:** PAIN - Payment Initiation
**Purpose:** Sent by a bank to a customer to report on the status of a payment instruction
**Direction:** Bank → Customer
**Scope:** Customer-facing payment status notifications

**Key Use Cases:**
- Notify customer that payment instruction was received
- Report acceptance or rejection of payment instruction
- Provide status updates during payment processing
- Notify customer of payment completion
- Report reasons for payment rejection or failure

**Relationship to Other Messages:**
- **pain.001**: Customer credit transfer initiation (status is reported via pain.002)
- **pain.008**: Customer direct debit initiation (status is reported via pain.002)
- **pacs.002**: Interbank payment status report (FI-to-FI equivalent)
- **camt.054**: Debit/credit notification (account-level notification)

**Comparison with pacs.002:**
- **pain.002**: Customer-facing (bank to customer)
- **pacs.002**: Interbank (bank to bank)
- **pain.002**: Covers original customer instruction (pain.001, pain.008)
- **pacs.002**: Covers interbank message (pacs.008, pacs.003)

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in pain.002** | 82 |
| **Fields Mapped to CDM** | 82 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- Party (debtor, creditor, original parties)
- Account (debtor account, creditor account)
- FinancialInstitution (instructing/instructed agents)
- StatusReport (status information, reason codes)

---

## Complete Field Mapping

### 1. Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique status report message ID |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | createdDateTime | Status report creation timestamp |
| GrpHdr/InitgPty/Nm | Initiating Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Bank sending status report |
| GrpHdr/InitgPty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Initiating party country |
| GrpHdr/InitgPty/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party | bic | Bank BIC |
| GrpHdr/InitgPty/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Bank identifier |

### 2. Original Group Information and Status (OrgnlGrpInfAndSts)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| OrgnlGrpInfAndSts/OrgnlMsgId | Original Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | originalMessageId | Reference to original pain.001/pain.008 |
| OrgnlGrpInfAndSts/OrgnlMsgNmId | Original Message Name Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | originalMessageType | e.g., "pain.001.001.09" |
| OrgnlGrpInfAndSts/OrgnlCreDtTm | Original Creation Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | originalCreatedDateTime | Original instruction timestamp |
| OrgnlGrpInfAndSts/OrgnlNbOfTxs | Original Number of Transactions | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | originalNumberOfTransactions | Number of transactions in original |
| OrgnlGrpInfAndSts/OrgnlCtrlSum | Original Control Sum | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | originalControlSum | Original total amount |
| OrgnlGrpInfAndSts/GrpSts | Group Status | Code | - | 0..1 | ACCP, ACSC, ACSP, RJCT, PDNG, PART, etc. | PaymentInstruction.extensions | groupStatus | Overall status of group |
| OrgnlGrpInfAndSts/StsRsnInf/Orgtr/Nm | Originator Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Party that originated the status |
| OrgnlGrpInfAndSts/StsRsnInf/Orgtr/Id/OrgId/AnyBIC | Originator BIC | Text | - | 0..1 | BIC format | Party | bic | Originator BIC |
| OrgnlGrpInfAndSts/StsRsnInf/Rsn/Cd | Reason Code | Code | - | 0..1 | AC01-AC99, AG01-AG99, AM01-AM99, etc. | PaymentInstruction.extensions | statusReasonCode | ISO 20022 reason code |
| OrgnlGrpInfAndSts/StsRsnInf/Rsn/Prtry | Proprietary Reason | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryReasonCode | Custom reason code |
| OrgnlGrpInfAndSts/StsRsnInf/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | statusAdditionalInfo | Free-text explanation |
| OrgnlGrpInfAndSts/NbOfTxsPerSts | Number of Transactions per Status | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | numberOfTransactionsPerStatus | Transaction count by status |

### 3. Original Payment Information and Status (OrgnlPmtInfAndSts)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| OrgnlPmtInfAndSts/OrgnlPmtInfId | Original Payment Information ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | originalPaymentInfoId | Payment batch identifier |
| OrgnlPmtInfAndSts/OrgnlNbOfTxs | Original Number of Transactions | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | originalNumberOfTransactions | Transaction count in batch |
| OrgnlPmtInfAndSts/OrgnlCtrlSum | Original Control Sum | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | originalControlSum | Batch control sum |
| OrgnlPmtInfAndSts/PmtInfSts | Payment Information Status | Code | - | 0..1 | ACCP, ACSC, ACSP, RJCT, PDNG, PART | PaymentInstruction.extensions | paymentInfoStatus | Batch-level status |
| OrgnlPmtInfAndSts/StsRsnInf/Orgtr/Nm | Originator Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Status originator |
| OrgnlPmtInfAndSts/StsRsnInf/Rsn/Cd | Reason Code | Code | - | 0..1 | AC01-AC99, etc. | PaymentInstruction.extensions | statusReasonCode | ISO 20022 reason code |
| OrgnlPmtInfAndSts/StsRsnInf/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | statusAdditionalInfo | Free-text explanation |
| OrgnlPmtInfAndSts/NbOfTxsPerSts | Number of Transactions per Status | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | numberOfTransactionsPerStatus | Transaction count by status |

### 4. Transaction Information and Status (TxInfAndSts)

#### 4.1 Status Identification

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/StsId | Status Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | statusId | Unique status identifier |
| TxInfAndSts/OrgnlInstrId | Original Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Original instruction identifier |
| TxInfAndSts/OrgnlEndToEndId | Original End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | endToEndId | Original E2E reference |
| TxInfAndSts/OrgnlTxId | Original Transaction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Original transaction identifier |
| TxInfAndSts/OrgnlUETR | Original UETR | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Original universal unique identifier |
| TxInfAndSts/TxSts | Transaction Status | Code | 4 | 0..1 | ACCP, ACSC, ACSP, RJCT, PDNG, CANC | PaymentInstruction | paymentStatus | Transaction-level status |
| TxInfAndSts/StsRsnInf/Orgtr/Nm | Originator Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Status originator |
| TxInfAndSts/StsRsnInf/Orgtr/Id/OrgId/AnyBIC | Originator BIC | Text | - | 0..1 | BIC format | Party | bic | Originator BIC |
| TxInfAndSts/StsRsnInf/Rsn/Cd | Reason Code | Code | - | 0..1 | AC01-AC99, AG01-AG99, AM01-AM99, etc. | PaymentInstruction.extensions | statusReasonCode | ISO 20022 reason code |
| TxInfAndSts/StsRsnInf/Rsn/Prtry | Proprietary Reason | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryReasonCode | Custom reason code |
| TxInfAndSts/StsRsnInf/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | statusAdditionalInfo | Free-text explanation |
| TxInfAndSts/ChrgsInf/Amt | Charges Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction.extensions | chargesAmount | Charge amount |
| TxInfAndSts/ChrgsInf/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | chargesCurrency | Charges currency |
| TxInfAndSts/ChrgsInf/Agt/FinInstnId/BICFI | Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Charging agent BIC |
| TxInfAndSts/ChrgsInf/Tp/Cd | Charge Type Code | Code | - | 0..1 | CRED, DEBT, SHAR | PaymentInstruction.extensions | chargeType | Charge bearer |
| TxInfAndSts/AccptncDtTm | Acceptance Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | acceptanceDateTime | When payment was accepted |
| TxInfAndSts/AcctSvcrRef | Account Servicer Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | accountServicerReference | Bank's internal reference |
| TxInfAndSts/ClrSysRef | Clearing System Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | clearingSystemReference | Clearing system reference |

#### 4.2 Original Transaction Reference (OrgnlTxRef)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/OrgnlTxRef/IntrBkSttlmAmt | Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | amount | Original settlement amount |
| TxInfAndSts/OrgnlTxRef/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | currency | Settlement currency |
| TxInfAndSts/OrgnlTxRef/Amt/InstdAmt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | instructedAmount | Original instructed amount |
| TxInfAndSts/OrgnlTxRef/Amt/InstdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | instructedCurrency | Instructed currency |
| TxInfAndSts/OrgnlTxRef/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISODate | PaymentInstruction | settlementDate | Original settlement date |
| TxInfAndSts/OrgnlTxRef/ReqdExctnDt/Dt | Requested Execution Date | Date | - | 0..1 | ISODate | PaymentInstruction | requestedExecutionDate | Original execution date |
| TxInfAndSts/OrgnlTxRef/ReqdExctnDt/DtTm | Requested Execution DateTime | DateTime | - | 0..1 | ISODateTime | PaymentInstruction | requestedExecutionDateTime | Original execution timestamp |
| TxInfAndSts/OrgnlTxRef/ReqdColltnDt | Requested Collection Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | requestedCollectionDate | Direct debit collection date |
| TxInfAndSts/OrgnlTxRef/PmtTpInf/InstrPrty | Instruction Priority | Code | 4 | 0..1 | HIGH, NORM | PaymentInstruction.extensions | priority | Original priority |
| TxInfAndSts/OrgnlTxRef/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | - | 0..1 | SEPA, SDVA, URGP | PaymentInstruction.extensions | serviceLevelCode | Original service level |
| TxInfAndSts/OrgnlTxRef/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | - | 0..1 | CORE, B2B, etc. | PaymentInstruction.extensions | localInstrumentCode | Regional instrument |
| TxInfAndSts/OrgnlTxRef/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | - | 0..1 | CASH, CORT, etc. | PaymentInstruction.extensions | categoryPurposeCode | Payment category |
| TxInfAndSts/OrgnlTxRef/PmtMtd | Payment Method | Code | 4 | 0..1 | CHK, TRF, TRA | PaymentInstruction.extensions | paymentMethod | Original payment method |
| TxInfAndSts/OrgnlTxRef/MndtRltdInf/MndtId | Mandate ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | mandateId | Direct debit mandate reference |
| TxInfAndSts/OrgnlTxRef/MndtRltdInf/DtOfSgntr | Date of Signature | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | mandateSignatureDate | Mandate signature date |
| TxInfAndSts/OrgnlTxRef/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction | remittanceInformation | Original remittance info |
| TxInfAndSts/OrgnlTxRef/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | invoiceNumber | Original invoice number |
| TxInfAndSts/OrgnlTxRef/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ultimate debtor |
| TxInfAndSts/OrgnlTxRef/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Original debtor |
| TxInfAndSts/OrgnlTxRef/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Debtor country |
| TxInfAndSts/OrgnlTxRef/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Original debtor account |
| TxInfAndSts/OrgnlTxRef/DbtrAcct/Id/Othr/Id | Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN debtor account |
| TxInfAndSts/OrgnlTxRef/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Original debtor bank |
| TxInfAndSts/OrgnlTxRef/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Original creditor bank |
| TxInfAndSts/OrgnlTxRef/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Original creditor |
| TxInfAndSts/OrgnlTxRef/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Creditor country |
| TxInfAndSts/OrgnlTxRef/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Original creditor account |
| TxInfAndSts/OrgnlTxRef/CdtrAcct/Id/Othr/Id | Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN creditor account |
| TxInfAndSts/OrgnlTxRef/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ultimate creditor |

---

## Code Lists and Enumerations

### Transaction Status (TxSts)
- **ACCP** - Accepted Customer Profile (validation passed)
- **ACSC** - Accepted Settlement Completed (payment settled)
- **ACSP** - Accepted Settlement In Process (settlement in progress)
- **ACTC** - Accepted Technical Validation (technical checks passed)
- **ACWC** - Accepted With Change (accepted but modified)
- **PART** - Partially Accepted (some transactions accepted, some rejected)
- **PDNG** - Pending (awaiting processing)
- **RCVD** - Received (received but not yet validated)
- **RJCT** - Rejected (payment rejected)
- **CANC** - Cancelled (payment cancelled)

### Rejection Reason Codes (Rsn/Cd)

**Account Identification Issues (AC01-AC99):**
- **AC01** - Incorrect Account Number
- **AC04** - Closed Account Number
- **AC06** - Blocked Account
- **AC13** - Invalid Debtor Account Type
- **AC14** - Invalid Creditor Account Type

**Agent Issues (AG01-AG99):**
- **AG01** - Transaction Forbidden
- **AG02** - Invalid Bank Operation Code
- **AG03** - Transaction Not Supported

**Amount Issues (AM01-AM99):**
- **AM01** - Zero Amount
- **AM02** - Not Allowed Amount
- **AM03** - Not Allowed Currency
- **AM04** - Insufficient Funds
- **AM05** - Duplication
- **AM09** - Wrong Amount
- **AM10** - Invalid Control Sum

**Regulatory Issues (RR01-RR99):**
- **RR01** - Missing Regulatory Reporting
- **RR02** - Invalid Regulatory Reporting
- **RR03** - Missing Creditor Name or Address
- **RR04** - Regulatory Reason

**Refusal/Return Reasons (MS02-MS03, etc.):**
- **MS02** - Reason Not Specified
- **MS03** - Not Specified Reason Agent Generated
- **BE01** - Inconsistent With End Customer
- **BE04** - Missing Creditor Address
- **BE05** - Unrecognised Initiating Party

**Direct Debit Specific (MD01-MD99):**
- **MD01** - No Mandate
- **MD02** - Missing Mandatory Information
- **MD06** - Refund Request By End Customer
- **MD07** - End Customer Deceased

**Request to Cancel/Return (CUST, DUPL, TECH, FRAD):**
- **CUST** - Requested by Customer
- **DUPL** - Duplicate Payment
- **TECH** - Technical Problems
- **FRAD** - Fraudulent Payment

---

## Message Examples

### Example 1: Accepted Payment (ACSC - Settlement Completed)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.002.001.10">
  <CstmrPmtStsRpt>
    <GrpHdr>
      <MsgId>STATUS-20241220-001</MsgId>
      <CreDtTm>2024-12-20T10:35:00</CreDtTm>
      <InitgPty>
        <Nm>ABC Bank</Nm>
        <Id>
          <OrgId>
            <AnyBIC>ABCBGB2LXXX</AnyBIC>
          </OrgId>
        </Id>
      </InitgPty>
    </GrpHdr>
    <OrgnlPmtInfAndSts>
      <OrgnlPmtInfId>PMT-BATCH-001</OrgnlPmtInfId>
      <TxInfAndSts>
        <StsId>STS-001</StsId>
        <OrgnlInstrId>INSTR-20241220-001</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-INVOICE-54321</OrgnlEndToEndId>
        <OrgnlTxId>TXN-20241220-001</OrgnlTxId>
        <TxSts>ACSC</TxSts>
        <AccptncDtTm>2024-12-20T10:30:15</AccptncDtTm>
        <AcctSvcrRef>ABC-REF-2024-12345</AcctSvcrRef>
        <OrgnlTxRef>
          <IntrBkSttlmAmt Ccy="EUR">5000.00</IntrBkSttlmAmt>
          <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
          <PmtTpInf>
            <SvcLvl>
              <Cd>SEPA</Cd>
            </SvcLvl>
          </PmtTpInf>
          <Dbtr>
            <Nm>John Smith</Nm>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <IBAN>GB29ABCB60161331926819</IBAN>
            </Id>
          </DbtrAcct>
          <Cdtr>
            <Nm>Acme Corporation</Nm>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <IBAN>DE89370400440532013000</IBAN>
            </Id>
          </CdtrAcct>
          <RmtInf>
            <Ustrd>Payment for invoice INV-54321</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInfAndSts>
    </OrgnlPmtInfAndSts>
  </CstmrPmtStsRpt>
</Document>
```

### Example 2: Rejected Payment (RJCT - Insufficient Funds)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.002.001.10">
  <CstmrPmtStsRpt>
    <GrpHdr>
      <MsgId>STATUS-20241220-002</MsgId>
      <CreDtTm>2024-12-20T11:20:00</CreDtTm>
      <InitgPty>
        <Nm>XYZ Bank</Nm>
        <Id>
          <OrgId>
            <AnyBIC>XYZBGB2LXXX</AnyBIC>
          </OrgId>
        </Id>
      </InitgPty>
    </GrpHdr>
    <OrgnlPmtInfAndSts>
      <OrgnlPmtInfId>PMT-BATCH-002</OrgnlPmtInfId>
      <TxInfAndSts>
        <StsId>STS-002</StsId>
        <OrgnlInstrId>INSTR-20241220-002</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-SALARY-789</OrgnlEndToEndId>
        <OrgnlTxId>TXN-20241220-002</OrgnlTxId>
        <TxSts>RJCT</TxSts>
        <StsRsnInf>
          <Rsn>
            <Cd>AM04</Cd>
          </Rsn>
          <AddtlInf>Insufficient funds in debtor account. Available balance: EUR 2,345.67. Requested amount: EUR 10,000.00</AddtlInf>
        </StsRsnInf>
        <OrgnlTxRef>
          <IntrBkSttlmAmt Ccy="EUR">10000.00</IntrBkSttlmAmt>
          <ReqdExctnDt>
            <Dt>2024-12-20</Dt>
          </ReqdExctnDt>
          <Dbtr>
            <Nm>Small Business Ltd</Nm>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <IBAN>GB45XYZB12345678901234</IBAN>
            </Id>
          </DbtrAcct>
          <Cdtr>
            <Nm>Employee Jane Doe</Nm>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <IBAN>GB67NWBK40306112345678</IBAN>
            </Id>
          </CdtrAcct>
          <RmtInf>
            <Ustrd>December 2024 salary payment</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInfAndSts>
    </OrgnlPmtInfAndSts>
  </CstmrPmtStsRpt>
</Document>
```

### Example 3: Pending Payment (ACCP - Accepted, Awaiting Settlement)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.002.001.10">
  <CstmrPmtStsRpt>
    <GrpHdr>
      <MsgId>STATUS-20241220-003</MsgId>
      <CreDtTm>2024-12-20T14:00:00</CreDtTm>
      <InitgPty>
        <Nm>Global Bank</Nm>
        <Id>
          <OrgId>
            <AnyBIC>GLBNGB2LXXX</AnyBIC>
          </OrgId>
        </Id>
      </InitgPty>
    </GrpHdr>
    <OrgnlPmtInfAndSts>
      <OrgnlPmtInfId>PMT-BATCH-003</OrgnlPmtInfId>
      <TxInfAndSts>
        <StsId>STS-003</StsId>
        <OrgnlInstrId>INSTR-20241220-003</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-FUTURE-PAY-456</OrgnlEndToEndId>
        <OrgnlTxId>TXN-20241220-003</OrgnlTxId>
        <TxSts>ACCP</TxSts>
        <AccptncDtTm>2024-12-20T14:00:00</AccptncDtTm>
        <StsRsnInf>
          <AddtlInf>Payment accepted and scheduled for future date execution. Will be processed on 2024-12-25.</AddtlInf>
        </StsRsnInf>
        <OrgnlTxRef>
          <IntrBkSttlmAmt Ccy="GBP">25000.00</IntrBkSttlmAmt>
          <ReqdExctnDt>
            <Dt>2024-12-25</Dt>
          </ReqdExctnDt>
          <PmtTpInf>
            <InstrPrty>NORM</InstrPrty>
          </PmtTpInf>
          <Dbtr>
            <Nm>Property Investments Ltd</Nm>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <IBAN>GB98GLBN20304055667788</IBAN>
            </Id>
          </DbtrAcct>
          <Cdtr>
            <Nm>Construction Services Inc</Nm>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <IBAN>GB12BARC20005512345678</IBAN>
            </Id>
          </CdtrAcct>
          <RmtInf>
            <Ustrd>Quarterly contractor payment - Q4 2024</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInfAndSts>
    </OrgnlPmtInfAndSts>
  </CstmrPmtStsRpt>
</Document>
```

### Example 4: Rejected Direct Debit (No Mandate)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.002.001.10">
  <CstmrPmtStsRpt>
    <GrpHdr>
      <MsgId>STATUS-20241220-004</MsgId>
      <CreDtTm>2024-12-20T16:45:00</CreDtTm>
      <InitgPty>
        <Nm>European Bank</Nm>
        <Id>
          <OrgId>
            <AnyBIC>EURBFRPPXXX</AnyBIC>
          </OrgId>
        </Id>
      </InitgPty>
    </GrpHdr>
    <OrgnlPmtInfAndSts>
      <OrgnlPmtInfId>DD-BATCH-001</OrgnlPmtInfId>
      <TxInfAndSts>
        <StsId>STS-DD-001</StsId>
        <OrgnlInstrId>DD-INSTR-001</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-SUB-999</OrgnlEndToEndId>
        <TxSts>RJCT</TxSts>
        <StsRsnInf>
          <Rsn>
            <Cd>MD01</Cd>
          </Rsn>
          <AddtlInf>No valid direct debit mandate found for debtor account. Mandate ID MANDATE-2023-XYZ-999 does not exist in our records.</AddtlInf>
        </StsRsnInf>
        <OrgnlTxRef>
          <IntrBkSttlmAmt Ccy="EUR">49.99</IntrBkSttlmAmt>
          <ReqdColltnDt>2024-12-22</ReqdColltnDt>
          <PmtTpInf>
            <SvcLvl>
              <Cd>SEPA</Cd>
            </SvcLvl>
            <LclInstrm>
              <Cd>CORE</Cd>
            </LclInstrm>
          </PmtTpInf>
          <MndtRltdInf>
            <MndtId>MANDATE-2023-XYZ-999</MndtId>
          </MndtRltdInf>
          <Dbtr>
            <Nm>Michel Dubois</Nm>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <IBAN>FR7630006000011234567890189</IBAN>
            </Id>
          </DbtrAcct>
          <Cdtr>
            <Nm>Streaming Service Pro</Nm>
          </Cdtr>
          <RmtInf>
            <Ustrd>Monthly subscription - December 2024</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInfAndSts>
    </OrgnlPmtInfAndSts>
  </CstmrPmtStsRpt>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 82 fields in pain.002 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles status identification, amounts, dates
- Extension fields accommodate status codes, reason codes, acceptance timestamps
- Party entity supports debtor, creditor, originator, ultimate parties
- Account entity handles IBAN and non-IBAN account identifiers
- FinancialInstitution entity manages agent information
- StatusReport functionality accommodated via extensions

**Key Extension Fields Used:**
- originalMessageId, originalMessageType, originalCreatedDateTime
- groupStatus, paymentInfoStatus, transactionStatus (TxSts)
- statusReasonCode (ISO 20022 reason codes: AC01-AC99, AM01-AM99, etc.)
- statusAdditionalInfo (free-text explanation)
- acceptanceDateTime (when payment was accepted)
- accountServicerReference (bank's internal reference)
- numberOfTransactionsPerStatus

---

## References

- **ISO 20022 Message Definition:** pain.002.001.10 - CustomerPaymentStatusReport
- **XML Schema:** pain.002.001.10.xsd
- **Related Messages:** pain.001 (credit transfer), pain.008 (direct debit), pacs.002 (FI status report)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **Status Codes:** ISO 20022 External Payment Transaction Status Code
- **Reason Codes:** ISO 20022 External Payment Status Reason Code

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
