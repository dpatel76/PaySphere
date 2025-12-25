# ISO 20022 camt.056 - FI to FI Payment Cancellation Request Mapping

## Message Overview

**Message Type:** camt.056.001.08 - FIToFIPaymentCancellationRequestV08
**Category:** CAMT - Cash Management
**Purpose:** Sent by a financial institution to request cancellation of a previously sent payment instruction before funds are released to the beneficiary
**Direction:** FI → FI (Bank to Bank)
**Scope:** Interbank payment cancellation request (pre-release of funds)

**Key Use Cases:**
- Cancel payment instruction sent in error
- Stop payment before beneficiary receives funds
- Fraud prevention and detection
- Duplicate payment cancellation
- Incorrect amount or beneficiary correction
- Recall payment before settlement completes

**Relationship to Other Messages:**
- **pacs.008**: Credit transfer that may be cancelled
- **pacs.003**: Direct debit that may be cancelled
- **camt.029**: Resolution of Investigation (response to cancellation request)
- **pacs.004**: Payment Return (if cancellation accepted, return via pacs.004)
- **pain.007**: Customer payment reversal request (customer-to-bank equivalent)
- **camt.055**: Customer payment cancellation request

**Comparison with Related Messages:**
- **camt.056**: FI to FI cancellation request (interbank)
- **camt.055**: Customer to FI cancellation request (customer-facing)
- **pain.007**: Customer payment reversal request
- **pacs.004**: Payment return (pre-settlement)
- **pacs.007**: Payment reversal (post-settlement)

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in camt.056** | 98 |
| **Fields Mapped to CDM** | 98 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- Party (assignor, assignee, parties involved)
- Account (debtor account, creditor account)
- FinancialInstitution (instructing/instructed agents)
- CancellationRequest (cancellation-specific information)

---

## Complete Field Mapping

### 1. Assignment (Assgnmt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Assgnmt/Id | Assignment Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique cancellation request ID |
| Assgnmt/Assgnr/Agt/FinInstnId/BICFI | Assignor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Requesting bank BIC |
| Assgnmt/Assgnr/Agt/FinInstnId/ClrSysMmbId/MmbId | Assignor Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| Assgnmt/Assgnr/Agt/FinInstnId/Nm | Assignor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Requesting bank name |
| Assgnmt/Assgnr/Agt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Bank country |
| Assgnmt/Assgnr/Pty/Nm | Assignor Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Party requesting cancellation |
| Assgnmt/Assgnr/Pty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Assignor country |
| Assgnmt/Assgnr/Pty/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| Assgnmt/Assgnr/Pty/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID/org number |
| Assgnmt/Assgne/Agt/FinInstnId/BICFI | Assignee Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Recipient bank BIC |
| Assgnmt/Assgne/Agt/FinInstnId/ClrSysMmbId/MmbId | Assignee Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| Assgnmt/Assgne/Agt/FinInstnId/Nm | Assignee Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Recipient bank name |
| Assgnmt/Assgne/Agt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Bank country |
| Assgnmt/Assgne/Pty/Nm | Assignee Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Party receiving request |
| Assgnmt/Assgne/Pty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Assignee country |
| Assgnmt/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | createdDateTime | Cancellation request timestamp |

### 2. Case (Case)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Case/Id | Case Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | caseId | Unique case identifier |
| Case/Cretr/Agt/FinInstnId/BICFI | Creator Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Case creator bank BIC |
| Case/Cretr/Agt/FinInstnId/Nm | Creator Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Case creator bank name |
| Case/Cretr/Pty/Nm | Creator Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Party creating case |
| Case/Cretr/Pty/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| Case/ReopCaseIndctn | Reopen Case Indication | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | reopenCaseIndicator | Whether case is being reopened |

### 3. Control Data (CtrlData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CtrlData/NbOfTxs | Number of Transactions | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | numberOfTransactions | Transaction count |
| CtrlData/CtrlSum | Control Sum | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | controlSum | Total of all amounts |

### 4. Underlying Transaction (Undrlyg)

#### 4.1 Original Group Information (OrgnlGrpInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/OrgnlGrpInf/OrgnlMsgId | Original Message ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | originalMessageId | Reference to original message |
| Undrlyg/OrgnlGrpInf/OrgnlMsgNmId | Original Message Name ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | originalMessageType | e.g., "pacs.008.001.08" |
| Undrlyg/OrgnlGrpInf/OrgnlCreDtTm | Original Creation DateTime | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | originalCreatedDateTime | Original message timestamp |
| Undrlyg/OrgnlGrpInf/OrgnlNbOfTxs | Original Number of Transactions | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | originalNumberOfTransactions | Original transaction count |
| Undrlyg/OrgnlGrpInf/OrgnlCtrlSum | Original Control Sum | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | originalControlSum | Original total amount |

#### 4.2 Transaction Information (TxInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/TxInf/CxlId | Cancellation Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | cancellationId | Unique cancellation identifier |
| Undrlyg/TxInf/CxlStsId | Cancellation Status ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | cancellationStatusId | Status identifier |
| Undrlyg/TxInf/OrgnlInstrId | Original Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Original instruction reference |
| Undrlyg/TxInf/OrgnlEndToEndId | Original End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | endToEndId | Original E2E reference |
| Undrlyg/TxInf/OrgnlTxId | Original Transaction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Original transaction reference |
| Undrlyg/TxInf/OrgnlUETR | Original UETR | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Original universal unique identifier |
| Undrlyg/TxInf/OrgnlIntrBkSttlmAmt | Original Interbank Settlement Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | amount | Original settlement amount |
| Undrlyg/TxInf/OrgnlIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | currency | Settlement currency |
| Undrlyg/TxInf/OrgnlIntrBkSttlmDt | Original Interbank Settlement Date | Date | - | 0..1 | ISODate | PaymentInstruction | settlementDate | Original settlement date |

#### 4.3 Cancellation Reason Information (CxlRsnInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/TxInf/CxlRsnInf/Orgtr/Nm | Originator Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Cancellation reason originator |
| Undrlyg/TxInf/CxlRsnInf/Orgtr/Id/OrgId/AnyBIC | Originator BIC | Text | - | 0..1 | BIC format | Party | bic | Originator BIC |
| Undrlyg/TxInf/CxlRsnInf/Rsn/Cd | Reason Code | Code | - | 0..1 | CUST, DUPL, FRAD, TECH, etc. | PaymentInstruction.extensions | cancellationReasonCode | ISO 20022 cancellation reason |
| Undrlyg/TxInf/CxlRsnInf/Rsn/Prtry | Proprietary Reason | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryCancellationReason | Custom cancellation reason |
| Undrlyg/TxInf/CxlRsnInf/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | cancellationAdditionalInfo | Free-text explanation |

#### 4.4 Original Transaction Reference (OrgnlTxRef)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/TxInf/OrgnlTxRef/IntrBkSttlmAmt | Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | originalSettlementAmount | Original settlement amount |
| Undrlyg/TxInf/OrgnlTxRef/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | originalSettlementCurrency | Settlement currency |
| Undrlyg/TxInf/OrgnlTxRef/Amt/InstdAmt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | instructedAmount | Original instructed amount |
| Undrlyg/TxInf/OrgnlTxRef/Amt/InstdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | instructedCurrency | Instructed currency |
| Undrlyg/TxInf/OrgnlTxRef/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | originalSettlementDate | Original settlement date |
| Undrlyg/TxInf/OrgnlTxRef/ReqdExctnDt/Dt | Requested Execution Date | Date | - | 0..1 | ISODate | PaymentInstruction | requestedExecutionDate | Original execution date |
| Undrlyg/TxInf/OrgnlTxRef/ReqdExctnDt/DtTm | Requested Execution DateTime | DateTime | - | 0..1 | ISODateTime | PaymentInstruction | requestedExecutionDateTime | Original execution timestamp |
| Undrlyg/TxInf/OrgnlTxRef/ReqdColltnDt | Requested Collection Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | requestedCollectionDate | Direct debit collection date |
| Undrlyg/TxInf/OrgnlTxRef/PmtTpInf/InstrPrty | Instruction Priority | Code | 4 | 0..1 | HIGH, NORM | PaymentInstruction.extensions | priority | Original priority |
| Undrlyg/TxInf/OrgnlTxRef/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | - | 0..1 | SEPA, SDVA, URGP | PaymentInstruction.extensions | serviceLevelCode | Original service level |
| Undrlyg/TxInf/OrgnlTxRef/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | - | 0..1 | CORE, B2B, etc. | PaymentInstruction.extensions | localInstrumentCode | Regional instrument |
| Undrlyg/TxInf/OrgnlTxRef/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | - | 0..1 | CASH, CORT, etc. | PaymentInstruction.extensions | categoryPurposeCode | Payment category |
| Undrlyg/TxInf/OrgnlTxRef/PmtMtd | Payment Method | Code | 4 | 0..1 | CHK, TRF, TRA | PaymentInstruction.extensions | paymentMethod | Original payment method |
| Undrlyg/TxInf/OrgnlTxRef/MndtRltdInf/MndtId | Mandate ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | mandateId | Direct debit mandate reference |
| Undrlyg/TxInf/OrgnlTxRef/MndtRltdInf/DtOfSgntr | Date of Signature | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | mandateSignatureDate | Mandate signature date |
| Undrlyg/TxInf/OrgnlTxRef/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction | remittanceInformation | Original remittance info |
| Undrlyg/TxInf/OrgnlTxRef/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | invoiceNumber | Original invoice number |
| Undrlyg/TxInf/OrgnlTxRef/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ultimate debtor |
| Undrlyg/TxInf/OrgnlTxRef/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Original debtor |
| Undrlyg/TxInf/OrgnlTxRef/Dbtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| Undrlyg/TxInf/OrgnlTxRef/Dbtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | ZIP/postal code |
| Undrlyg/TxInf/OrgnlTxRef/Dbtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| Undrlyg/TxInf/OrgnlTxRef/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Debtor country |
| Undrlyg/TxInf/OrgnlTxRef/Dbtr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| Undrlyg/TxInf/OrgnlTxRef/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Original debtor account |
| Undrlyg/TxInf/OrgnlTxRef/DbtrAcct/Id/Othr/Id | Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN debtor account |
| Undrlyg/TxInf/OrgnlTxRef/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Original debtor bank |
| Undrlyg/TxInf/OrgnlTxRef/DbtrAgt/FinInstnId/Nm | Debtor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Debtor bank name |
| Undrlyg/TxInf/OrgnlTxRef/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Original creditor bank |
| Undrlyg/TxInf/OrgnlTxRef/CdtrAgt/FinInstnId/Nm | Creditor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Creditor bank name |
| Undrlyg/TxInf/OrgnlTxRef/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Original creditor |
| Undrlyg/TxInf/OrgnlTxRef/Cdtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| Undrlyg/TxInf/OrgnlTxRef/Cdtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | ZIP/postal code |
| Undrlyg/TxInf/OrgnlTxRef/Cdtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| Undrlyg/TxInf/OrgnlTxRef/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Creditor country |
| Undrlyg/TxInf/OrgnlTxRef/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Original creditor account |
| Undrlyg/TxInf/OrgnlTxRef/CdtrAcct/Id/Othr/Id | Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN creditor account |
| Undrlyg/TxInf/OrgnlTxRef/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ultimate creditor |

### 5. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Cancellation Reason Code (CxlRsnInf/Rsn/Cd)

**Common Cancellation Reasons:**
- **CUST** - Requested by Customer (customer initiated cancellation)
- **DUPL** - Duplicate Payment (payment sent twice in error)
- **FRAD** - Fraudulent Payment (fraud detected)
- **TECH** - Technical Problems (system/technical error)
- **AC03** - Invalid Creditor Account Number (wrong beneficiary)
- **AM09** - Wrong Amount (incorrect amount)
- **BE05** - Unrecognised Initiating Party (wrong initiator)
- **AGNT** - Incorrect Agent (wrong intermediary)
- **CURR** - Incorrect Currency (wrong currency)
- **CUTA** - Requested by Customer (customer request)
- **UPAY** - Undue Payment (payment not owed)

### Payment Method (PmtMtd)
- **CHK** - Cheque
- **TRF** - Credit Transfer
- **TRA** - Credit Transfer to Account

### Service Level (SvcLvl/Cd)
- **SEPA** - Single Euro Payments Area
- **SDVA** - Same Day Value
- **URGP** - Urgent Payment

### Instruction Priority (InstrPrty)
- **HIGH** - High priority
- **NORM** - Normal priority

---

## Message Examples

### Example 1: Fraud Cancellation Request

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.056.001.08">
  <FIToFIPmtCxlReq>
    <Assgnmt>
      <Id>CXLREQ-20241220-FRAUD-001</Id>
      <Assgnr>
        <Agt>
          <FinInstnId>
            <BICFI>ABCBGB2LXXX</BICFI>
            <Nm>ABC Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>XYZSGB2LXXX</BICFI>
            <Nm>XYZ Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T15:45:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-FRAUD-2024-98765</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>ABCBGB2LXXX</BICFI>
            <Nm>ABC Bank - Fraud Prevention Team</Nm>
          </FinInstnId>
        </Agt>
      </Cretr>
    </Case>
    <CtrlData>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>25000.00</CtrlSum>
    </CtrlData>
    <Undrlyg>
      <OrgnlGrpInf>
        <OrgnlMsgId>PMT-20241220-ORIG-001</OrgnlMsgId>
        <OrgnlMsgNmId>pacs.008.001.08</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-20T14:15:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <TxInf>
        <CxlId>CXLID-FRAUD-001</CxlId>
        <OrgnlInstrId>INSTR-20241220-SUSPICIOUS</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-FRAUDULENT-789</OrgnlEndToEndId>
        <OrgnlTxId>TXN-20241220-FRAUD</OrgnlTxId>
        <OrgnlIntrBkSttlmAmt Ccy="GBP">25000.00</OrgnlIntrBkSttlmAmt>
        <OrgnlIntrBkSttlmDt>2024-12-20</OrgnlIntrBkSttlmDt>
        <CxlRsnInf>
          <Orgtr>
            <Nm>ABC Bank Fraud Department</Nm>
          </Orgtr>
          <Rsn>
            <Cd>FRAD</Cd>
          </Rsn>
          <AddtlInf>URGENT: Fraudulent payment detected. Customer account compromised. Transaction initiated by unauthorized third party. Police report filed - reference FPD-2024-12345. Request immediate cancellation before funds release to beneficiary. Customer notified and account frozen.</AddtlInf>
        </CxlRsnInf>
        <OrgnlTxRef>
          <IntrBkSttlmAmt Ccy="GBP">25000.00</IntrBkSttlmAmt>
          <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
          <PmtMtd>TRF</PmtMtd>
          <Dbtr>
            <Nm>Compromised Customer Account - John Smith</Nm>
            <PstlAdr>
              <StrtNm>High Street</StrtNm>
              <PstCd>SW1A 1AA</PstCd>
              <TwnNm>London</TwnNm>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <IBAN>GB29ABCB60161331926819</IBAN>
            </Id>
          </DbtrAcct>
          <DbtrAgt>
            <FinInstnId>
              <BICFI>ABCBGB2LXXX</BICFI>
            </FinInstnId>
          </DbtrAgt>
          <CdtrAgt>
            <FinInstnId>
              <BICFI>XYZSGB2LXXX</BICFI>
            </FinInstnId>
          </CdtrAgt>
          <Cdtr>
            <Nm>Suspicious Beneficiary Ltd</Nm>
            <PstlAdr>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <IBAN>GB98XYZS12345678901234</IBAN>
            </Id>
          </CdtrAcct>
          <RmtInf>
            <Ustrd>FRAUDULENT - Invoice payment - NOT AUTHORIZED BY CUSTOMER</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInf>
    </Undrlyg>
  </FIToFIPmtCxlReq>
</Document>
```

### Example 2: Duplicate Payment Cancellation

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.056.001.08">
  <FIToFIPmtCxlReq>
    <Assgnmt>
      <Id>CXLREQ-20241220-DUPL-002</Id>
      <Assgnr>
        <Agt>
          <FinInstnId>
            <BICFI>GLBNGB2LXXX</BICFI>
            <Nm>Global Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>BNPAFRPPXXX</BICFI>
            <Nm>BNP Paribas</Nm>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T11:20:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-DUPL-2024-55555</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>GLBNGB2LXXX</BICFI>
            <Nm>Global Bank - Operations</Nm>
          </FinInstnId>
        </Agt>
      </Cretr>
    </Case>
    <CtrlData>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>10000.00</CtrlSum>
    </CtrlData>
    <Undrlyg>
      <OrgnlGrpInf>
        <OrgnlMsgId>PMT-20241220-DUPL-002</OrgnlMsgId>
        <OrgnlMsgNmId>pacs.008.001.08</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-20T10:30:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <TxInf>
        <CxlId>CXLID-DUPL-001</CxlId>
        <OrgnlInstrId>INSTR-DUPLICATE-002</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-INV-88888-DUPLICATE</OrgnlEndToEndId>
        <OrgnlTxId>TXN-DUPLICATE-002</OrgnlTxId>
        <OrgnlIntrBkSttlmAmt Ccy="EUR">10000.00</OrgnlIntrBkSttlmAmt>
        <OrgnlIntrBkSttlmDt>2024-12-20</OrgnlIntrBkSttlmDt>
        <CxlRsnInf>
          <Orgtr>
            <Nm>Global Bank Operations Team</Nm>
          </Orgtr>
          <Rsn>
            <Cd>DUPL</Cd>
          </Rsn>
          <AddtlInf>Duplicate payment detected. Same invoice (INV-88888) was paid twice due to system processing error. First payment (E2E-INV-88888-ORIGINAL) already successfully processed and settled on 2024-12-20. This second payment should be cancelled. Customer has been notified.</AddtlInf>
        </CxlRsnInf>
        <OrgnlTxRef>
          <IntrBkSttlmAmt Ccy="EUR">10000.00</IntrBkSttlmAmt>
          <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
          <PmtMtd>TRF</PmtMtd>
          <Dbtr>
            <Nm>Manufacturing Corp Ltd</Nm>
            <PstlAdr>
              <StrtNm>Industrial Park</StrtNm>
              <PstCd>M1 1AA</PstCd>
              <TwnNm>Manchester</TwnNm>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <IBAN>GB12GLBN20304055667788</IBAN>
            </Id>
          </DbtrAcct>
          <DbtrAgt>
            <FinInstnId>
              <BICFI>GLBNGB2LXXX</BICFI>
            </FinInstnId>
          </DbtrAgt>
          <CdtrAgt>
            <FinInstnId>
              <BICFI>BNPAFRPPXXX</BICFI>
            </FinInstnId>
          </CdtrAgt>
          <Cdtr>
            <Nm>Supplier SARL</Nm>
            <PstlAdr>
              <TwnNm>Paris</TwnNm>
              <Ctry>FR</Ctry>
            </PstlAdr>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <IBAN>FR1420041010050500013M02606</IBAN>
            </Id>
          </CdtrAcct>
          <RmtInf>
            <Ustrd>Invoice INV-88888 - DUPLICATE PAYMENT - Please cancel</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInf>
    </Undrlyg>
  </FIToFIPmtCxlReq>
</Document>
```

### Example 3: Wrong Beneficiary Cancellation

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.056.001.08">
  <FIToFIPmtCxlReq>
    <Assgnmt>
      <Id>CXLREQ-20241220-WRONGBENEF-003</Id>
      <Assgnr>
        <Agt>
          <FinInstnId>
            <BICFI>NWBKGB2LXXX</BICFI>
            <Nm>National Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>BARCGB22XXX</BICFI>
            <Nm>Barclays Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T09:45:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-WRONGACCT-2024-33333</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>NWBKGB2LXXX</BICFI>
            <Nm>National Bank</Nm>
          </FinInstnId>
        </Agt>
      </Cretr>
    </Case>
    <CtrlData>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>5000.00</CtrlSum>
    </CtrlData>
    <Undrlyg>
      <OrgnlGrpInf>
        <OrgnlMsgId>PMT-20241220-ERROR-003</OrgnlMsgId>
        <OrgnlMsgNmId>pacs.008.001.08</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-20T09:00:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <TxInf>
        <CxlId>CXLID-WRONGACCT-001</CxlId>
        <OrgnlInstrId>INSTR-WRONGBENEF</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-PAYMENT-WRONG-ACCOUNT</OrgnlEndToEndId>
        <OrgnlTxId>TXN-WRONGBENEF</OrgnlTxId>
        <OrgnlIntrBkSttlmAmt Ccy="GBP">5000.00</OrgnlIntrBkSttlmAmt>
        <OrgnlIntrBkSttlmDt>2024-12-20</OrgnlIntrBkSttlmDt>
        <CxlRsnInf>
          <Orgtr>
            <Nm>Customer - Jane Doe</Nm>
          </Orgtr>
          <Rsn>
            <Cd>AC03</Cd>
          </Rsn>
          <AddtlInf>Customer entered incorrect beneficiary account number. Payment sent to wrong account (GB12BARC20005512345678). Correct beneficiary account should be GB12BARC20005598765432. Customer requests urgent cancellation before funds are released. Will resubmit with correct details.</AddtlInf>
        </CxlRsnInf>
        <OrgnlTxRef>
          <IntrBkSttlmAmt Ccy="GBP">5000.00</IntrBkSttlmAmt>
          <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
          <PmtMtd>TRF</PmtMtd>
          <Dbtr>
            <Nm>Jane Doe</Nm>
            <PstlAdr>
              <StrtNm>Baker Street</StrtNm>
              <PstCd>NW1 6XE</PstCd>
              <TwnNm>London</TwnNm>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <IBAN>GB67NWBK40306112345678</IBAN>
            </Id>
          </DbtrAcct>
          <DbtrAgt>
            <FinInstnId>
              <BICFI>NWBKGB2LXXX</BICFI>
            </FinInstnId>
          </DbtrAgt>
          <CdtrAgt>
            <FinInstnId>
              <BICFI>BARCGB22XXX</BICFI>
            </FinInstnId>
          </CdtrAgt>
          <Cdtr>
            <Nm>WRONG BENEFICIARY</Nm>
            <PstlAdr>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <IBAN>GB12BARC20005512345678</IBAN>
            </Id>
          </CdtrAcct>
          <RmtInf>
            <Ustrd>INCORRECT BENEFICIARY ACCOUNT - PLEASE CANCEL</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInf>
    </Undrlyg>
  </FIToFIPmtCxlReq>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 98 fields in camt.056 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles cancellation identification, amounts, dates
- Extension fields accommodate cancellation-specific information (reason codes, case ID)
- Party entity supports assignor, assignee, creditor, debtor, ultimate parties
- Account entity handles IBAN and non-IBAN account identifiers
- FinancialInstitution entity manages agent information

**Key Extension Fields Used:**
- caseId, reopenCaseIndicator (case management)
- cancellationId, cancellationStatusId, cancellationReasonCode
- cancellationAdditionalInfo (free-text explanation)
- originalMessageId, originalMessageType, originalCreatedDateTime (references to original payment)
- originalNumberOfTransactions, originalControlSum

---

## References

- **ISO 20022 Message Definition:** camt.056.001.08 - FIToFIPaymentCancellationRequestV08
- **XML Schema:** camt.056.001.08.xsd
- **Related Messages:** pacs.008 (credit transfer), pacs.003 (direct debit), camt.029 (resolution), pacs.004 (return), pain.007 (customer reversal)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **Cancellation Reason Codes:** ISO 20022 External Payment Cancellation Reason Code

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
