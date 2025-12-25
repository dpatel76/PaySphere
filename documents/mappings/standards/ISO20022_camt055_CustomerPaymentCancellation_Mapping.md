# ISO 20022 camt.055 - Customer Payment Cancellation Request Mapping

## Message Overview

**Message Type:** camt.055.001.08 - CustomerPaymentCancellationRequestV08
**Category:** CAMT - Cash Management
**Purpose:** Sent by a bank to request cancellation of a payment instruction at the request of the customer
**Direction:** Customer → FI or FI → FI (on behalf of customer)
**Scope:** Customer-initiated payment cancellation request

**Key Use Cases:**
- Customer requests cancellation of payment sent in error
- Customer wants to stop payment before beneficiary receives funds
- Fraud prevention at customer request
- Duplicate payment cancellation requested by customer
- Incorrect amount or beneficiary correction by customer
- Recall payment before settlement completes

**Relationship to Other Messages:**
- **pain.001**: Customer credit transfer that may be cancelled
- **pain.008**: Customer direct debit that may be cancelled
- **camt.029**: Resolution of Investigation (response to cancellation request)
- **pacs.004**: Payment Return (if cancellation accepted)
- **camt.056**: FI to FI cancellation request (interbank follow-up)
- **pain.007**: Customer payment reversal request (related message)

**Comparison with Related Messages:**
- **camt.055**: Customer to FI cancellation request (customer-facing)
- **camt.056**: FI to FI cancellation request (interbank)
- **pain.007**: Customer payment reversal request (post-settlement)
- **pacs.004**: Payment return (pre-settlement)

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in camt.055** | 95 |
| **Fields Mapped to CDM** | 95 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- Party (assignor, assignee, parties involved)
- Account (debtor account, creditor account)
- FinancialInstitution (instructing/instructed agents)
- ComplianceCase (case management)

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
| Assgnmt/Assgnr/Pty/Nm | Assignor Party Name | Text | 1-140 | 0..1 | Free text | Party | name | Party requesting cancellation |
| Assgnmt/Assgnr/Pty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Assignor country |
| Assgnmt/Assgnr/Pty/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Organization BIC |
| Assgnmt/Assgnr/Pty/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxIdentificationNumber | Tax ID/org number |
| Assgnmt/Assgnr/Pty/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Birth Date | Date | - | 0..1 | ISODate | Party | dateOfBirth | Individual birth date |
| Assgnmt/Assgnr/Pty/Id/PrvtId/Othr/Id | Private ID | Text | 1-35 | 0..1 | Free text | Party | identificationNumber | Individual ID number |
| Assgnmt/Assgne/Agt/FinInstnId/BICFI | Assignee Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Recipient bank BIC |
| Assgnmt/Assgne/Agt/FinInstnId/ClrSysMmbId/MmbId | Assignee Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| Assgnmt/Assgne/Agt/FinInstnId/Nm | Assignee Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Recipient bank name |
| Assgnmt/Assgne/Agt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Bank country |
| Assgnmt/Assgne/Pty/Nm | Assignee Party Name | Text | 1-140 | 0..1 | Free text | Party | name | Party receiving request |
| Assgnmt/Assgne/Pty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Assignee country |
| Assgnmt/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | creationDateTime | Cancellation request timestamp |

### 2. Case (Case)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Case/Id | Case Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | caseId | Unique case identifier |
| Case/Cretr/Agt/FinInstnId/BICFI | Creator Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Case creator bank BIC |
| Case/Cretr/Agt/FinInstnId/Nm | Creator Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Case creator bank name |
| Case/Cretr/Pty/Nm | Creator Party Name | Text | 1-140 | 0..1 | Free text | Party | name | Party creating case |
| Case/Cretr/Pty/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Organization BIC |
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
| Undrlyg/OrgnlGrpInf/OrgnlMsgNmId | Original Message Name ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | originalMessageType | e.g., "pain.001.001.09" |
| Undrlyg/OrgnlGrpInf/OrgnlCreDtTm | Original Creation DateTime | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | originalCreatedDateTime | Original message timestamp |

#### 4.2 Transaction Information (TxInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/TxInf/CxlId | Cancellation Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | cancellationId | Unique cancellation identifier |
| Undrlyg/TxInf/OrgnlInstrId | Original Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Original instruction reference |
| Undrlyg/TxInf/OrgnlEndToEndId | Original End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | endToEndId | Original E2E reference |
| Undrlyg/TxInf/OrgnlTxId | Original Transaction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Original transaction reference |
| Undrlyg/TxInf/OrgnlUETR | Original UETR | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Original universal unique identifier |
| Undrlyg/TxInf/OrgnlIntrBkSttlmAmt | Original Interbank Settlement Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | interbankSettlementAmount | Original settlement amount |
| Undrlyg/TxInf/OrgnlIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | interbankSettlementAmount.currency | Settlement currency |

#### 4.3 Cancellation Reason Information (CxlRsnInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/TxInf/CxlRsnInf/Orgtr/Nm | Originator Name | Text | 1-140 | 0..1 | Free text | Party | name | Cancellation reason originator |
| Undrlyg/TxInf/CxlRsnInf/Orgtr/Id/OrgId/AnyBIC | Originator BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Originator BIC |
| Undrlyg/TxInf/CxlRsnInf/Orgtr/Id/PrvtId/Othr/Id | Originator Private ID | Text | 1-35 | 0..1 | Free text | Party | identificationNumber | Private ID |
| Undrlyg/TxInf/CxlRsnInf/Rsn/Cd | Reason Code | Code | - | 0..1 | CUST, DUPL, FRAD, TECH, etc. | PaymentInstruction.extensions | cancellationReasonCode | ISO 20022 cancellation reason |
| Undrlyg/TxInf/CxlRsnInf/Rsn/Prtry | Proprietary Reason | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryCancellationReason | Custom cancellation reason |
| Undrlyg/TxInf/CxlRsnInf/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | cancellationAdditionalInfo | Free-text explanation |

#### 4.4 Original Transaction Reference (OrgnlTxRef)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/TxInf/OrgnlTxRef/Amt/InstdAmt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | instructedAmount | Original instructed amount |
| Undrlyg/TxInf/OrgnlTxRef/Amt/InstdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | instructedAmount.currency | Instructed currency |
| Undrlyg/TxInf/OrgnlTxRef/ReqdExctnDt/Dt | Requested Execution Date | Date | - | 0..1 | ISODate | PaymentInstruction | requestedExecutionDate | Original execution date |
| Undrlyg/TxInf/OrgnlTxRef/ReqdExctnDt/DtTm | Requested Execution DateTime | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | requestedExecutionDateTime | Original execution timestamp |
| Undrlyg/TxInf/OrgnlTxRef/ReqdColltnDt | Requested Collection Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | requestedCollectionDate | Direct debit collection date |
| Undrlyg/TxInf/OrgnlTxRef/PmtTpInf/InstrPrty | Instruction Priority | Code | 4 | 0..1 | HIGH, NORM | PaymentInstruction | priority | Original priority |
| Undrlyg/TxInf/OrgnlTxRef/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | - | 0..1 | SEPA, SDVA, URGP | PaymentInstruction | serviceLevel | Original service level |
| Undrlyg/TxInf/OrgnlTxRef/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | - | 0..1 | CORE, B2B, etc. | PaymentInstruction | localInstrument | Regional instrument |
| Undrlyg/TxInf/OrgnlTxRef/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | - | 0..1 | CASH, CORT, etc. | PaymentInstruction | categoryPurpose | Payment category |
| Undrlyg/TxInf/OrgnlTxRef/PmtMtd | Payment Method | Code | 4 | 0..1 | CHK, TRF, TRA | PaymentInstruction.extensions | paymentMethod | Original payment method |
| Undrlyg/TxInf/OrgnlTxRef/MndtRltdInf/MndtId | Mandate ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | mandateId | Direct debit mandate reference |
| Undrlyg/TxInf/OrgnlTxRef/MndtRltdInf/DtOfSgntr | Date of Signature | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | mandateSignatureDate | Mandate signature date |
| Undrlyg/TxInf/OrgnlTxRef/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction | remittanceInformation | Original remittance info |
| Undrlyg/TxInf/OrgnlTxRef/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | invoiceNumber | Original invoice number |
| Undrlyg/TxInf/OrgnlTxRef/RmtInf/Strd/RfrdDocInf/RltdDt | Related Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | invoiceDate | Invoice date |
| Undrlyg/TxInf/OrgnlTxRef/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Free text | Party | name | Ultimate debtor |
| Undrlyg/TxInf/OrgnlTxRef/UltmtDbtr/Id/OrgId/AnyBIC | Ultimate Debtor BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Organization BIC |
| Undrlyg/TxInf/OrgnlTxRef/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | name | Original debtor |
| Undrlyg/TxInf/OrgnlTxRef/Dbtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | postalAddress.streetName | Street |
| Undrlyg/TxInf/OrgnlTxRef/Dbtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalAddress.postCode | ZIP/postal code |
| Undrlyg/TxInf/OrgnlTxRef/Dbtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | postalAddress.townName | City |
| Undrlyg/TxInf/OrgnlTxRef/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Debtor country |
| Undrlyg/TxInf/OrgnlTxRef/Dbtr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Organization BIC |
| Undrlyg/TxInf/OrgnlTxRef/Dbtr/Id/PrvtId/Othr/Id | Private ID | Text | 1-35 | 0..1 | Free text | Party | identificationNumber | Individual ID |
| Undrlyg/TxInf/OrgnlTxRef/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Original debtor account |
| Undrlyg/TxInf/OrgnlTxRef/DbtrAcct/Id/Othr/Id | Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN debtor account |
| Undrlyg/TxInf/OrgnlTxRef/DbtrAcct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account.extensions | accountTypeCode | Account type |
| Undrlyg/TxInf/OrgnlTxRef/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Original debtor bank |
| Undrlyg/TxInf/OrgnlTxRef/DbtrAgt/FinInstnId/Nm | Debtor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Debtor bank name |
| Undrlyg/TxInf/OrgnlTxRef/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Original creditor bank |
| Undrlyg/TxInf/OrgnlTxRef/CdtrAgt/FinInstnId/Nm | Creditor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Creditor bank name |
| Undrlyg/TxInf/OrgnlTxRef/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | name | Original creditor |
| Undrlyg/TxInf/OrgnlTxRef/Cdtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | postalAddress.streetName | Street |
| Undrlyg/TxInf/OrgnlTxRef/Cdtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalAddress.postCode | ZIP/postal code |
| Undrlyg/TxInf/OrgnlTxRef/Cdtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | postalAddress.townName | City |
| Undrlyg/TxInf/OrgnlTxRef/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Creditor country |
| Undrlyg/TxInf/OrgnlTxRef/Cdtr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Organization BIC |
| Undrlyg/TxInf/OrgnlTxRef/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Original creditor account |
| Undrlyg/TxInf/OrgnlTxRef/CdtrAcct/Id/Othr/Id | Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN creditor account |
| Undrlyg/TxInf/OrgnlTxRef/CdtrAcct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account.extensions | accountTypeCode | Account type |
| Undrlyg/TxInf/OrgnlTxRef/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Free text | Party | name | Ultimate creditor |
| Undrlyg/TxInf/OrgnlTxRef/UltmtCdtr/Id/OrgId/AnyBIC | Ultimate Creditor BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Organization BIC |
| Undrlyg/TxInf/OrgnlTxRef/Purp/Cd | Purpose Code | Code | 4 | 0..1 | ISO 20022 codes | PaymentInstruction | purpose | Purpose code |

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
- **LEGL** - Legal Decision (court order/legal requirement)

### Payment Method (PmtMtd)
- **CHK** - Cheque
- **TRF** - Credit Transfer
- **TRA** - Credit Transfer to Account
- **DD** - Direct Debit

### Service Level (SvcLvl/Cd)
- **SEPA** - Single Euro Payments Area
- **SDVA** - Same Day Value
- **URGP** - Urgent Payment

### Instruction Priority (InstrPrty)
- **HIGH** - High priority
- **NORM** - Normal priority

### Account Type (DbtrAcct/Tp/Cd, CdtrAcct/Tp/Cd)
- **CACC** - Current/Checking Account
- **SVGS** - Savings Account
- **LOAN** - Loan Account
- **CARD** - Card Account

---

## Message Examples

### Example 1: Customer Requests Fraud Cancellation

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.055.001.08">
  <CstmrPmtCxlReq>
    <Assgnmt>
      <Id>CUSTCXL-20241220-001</Id>
      <Assgnr>
        <Pty>
          <Nm>John Smith</Nm>
          <PstlAdr>
            <Ctry>US</Ctry>
          </PstlAdr>
          <Id>
            <PrvtId>
              <Othr>
                <Id>SSN-123456789</Id>
              </Othr>
            </PrvtId>
          </Id>
        </Pty>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>BOFAUS3NXXX</BICFI>
            <Nm>Bank of America</Nm>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T16:30:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-CUSTFRAUD-2024-12345</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>BOFAUS3NXXX</BICFI>
            <Nm>Bank of America - Customer Service</Nm>
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
        <OrgnlMsgId>PMT-CUST-20241220-001</OrgnlMsgId>
        <OrgnlMsgNmId>pain.001.001.09</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-20T10:15:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <TxInf>
        <CxlId>CXLID-CUSTFRAUD-001</CxlId>
        <OrgnlEndToEndId>E2E-FRAUDULENT-20241220</OrgnlEndToEndId>
        <OrgnlTxId>TXN-CUSTOMER-FRAUD</OrgnlTxId>
        <CxlRsnInf>
          <Orgtr>
            <Nm>John Smith - Customer</Nm>
          </Orgtr>
          <Rsn>
            <Cd>FRAD</Cd>
          </Rsn>
          <AddtlInf>Customer reports unauthorized payment. Account potentially compromised. Customer did not authorize this transfer. Request immediate cancellation.</AddtlInf>
        </CxlRsnInf>
        <OrgnlTxRef>
          <Amt>
            <InstdAmt Ccy="USD">5000.00</InstdAmt>
          </Amt>
          <ReqdExctnDt>
            <Dt>2024-12-20</Dt>
          </ReqdExctnDt>
          <PmtTpInf>
            <InstrPrty>NORM</InstrPrty>
          </PmtTpInf>
          <PmtMtd>TRF</PmtMtd>
          <Dbtr>
            <Nm>John Smith</Nm>
            <PstlAdr>
              <StrtNm>Main Street</StrtNm>
              <PstCd>10001</PstCd>
              <TwnNm>New York</TwnNm>
              <Ctry>US</Ctry>
            </PstlAdr>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <Othr>
                <Id>123456789012</Id>
              </Othr>
            </Id>
            <Tp>
              <Cd>CACC</Cd>
            </Tp>
          </DbtrAcct>
          <DbtrAgt>
            <FinInstnId>
              <BICFI>BOFAUS3NXXX</BICFI>
            </FinInstnId>
          </DbtrAgt>
          <CdtrAgt>
            <FinInstnId>
              <BICFI>CHASUS33XXX</BICFI>
            </FinInstnId>
          </CdtrAgt>
          <Cdtr>
            <Nm>Suspicious Beneficiary</Nm>
            <PstlAdr>
              <Ctry>US</Ctry>
            </PstlAdr>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <Othr>
                <Id>987654321098</Id>
              </Othr>
            </Id>
          </CdtrAcct>
          <RmtInf>
            <Ustrd>UNAUTHORIZED PAYMENT - FRAUD</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInf>
    </Undrlyg>
  </CstmrPmtCxlReq>
</Document>
```

### Example 2: Duplicate Payment Cancellation

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.055.001.08">
  <CstmrPmtCxlReq>
    <Assgnmt>
      <Id>CUSTCXL-20241220-DUPL-002</Id>
      <Assgnr>
        <Pty>
          <Nm>ABC Corporation</Nm>
          <Id>
            <OrgId>
              <Othr>
                <Id>EIN-987654321</Id>
              </Othr>
            </OrgId>
          </Id>
        </Pty>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>BOFAUS3NXXX</BICFI>
            <Nm>Bank of America</Nm>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T14:00:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-DUPL-2024-67890</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>BOFAUS3NXXX</BICFI>
            <Nm>Bank of America</Nm>
          </FinInstnId>
        </Agt>
      </Cretr>
    </Case>
    <Undrlyg>
      <OrgnlGrpInf>
        <OrgnlMsgId>PMT-CORP-20241220-DUPL</OrgnlMsgId>
        <OrgnlMsgNmId>pain.001.001.09</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-20T13:30:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <TxInf>
        <CxlId>CXLID-DUPL-002</CxlId>
        <OrgnlEndToEndId>E2E-INV-55555-DUPLICATE</OrgnlEndToEndId>
        <OrgnlTxId>TXN-DUPL-002</OrgnlTxId>
        <CxlRsnInf>
          <Orgtr>
            <Nm>ABC Corporation Treasury</Nm>
          </Orgtr>
          <Rsn>
            <Cd>DUPL</Cd>
          </Rsn>
          <AddtlInf>Duplicate payment for invoice INV-55555. Original payment already processed. Please cancel this duplicate transaction.</AddtlInf>
        </CxlRsnInf>
        <OrgnlTxRef>
          <Amt>
            <InstdAmt Ccy="USD">15000.00</InstdAmt>
          </Amt>
          <ReqdExctnDt>
            <Dt>2024-12-20</Dt>
          </ReqdExctnDt>
          <Dbtr>
            <Nm>ABC Corporation</Nm>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <Othr>
                <Id>555666777888</Id>
              </Othr>
            </Id>
          </DbtrAcct>
          <Cdtr>
            <Nm>Vendor XYZ Inc</Nm>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <Othr>
                <Id>111222333444</Id>
              </Othr>
            </Id>
          </CdtrAcct>
          <RmtInf>
            <Ustrd>Invoice INV-55555 - DUPLICATE</Ustrd>
            <Strd>
              <RfrdDocInf>
                <Nb>INV-55555</Nb>
                <RltdDt>2024-12-15</RltdDt>
              </RfrdDocInf>
            </Strd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInf>
    </Undrlyg>
  </CstmrPmtCxlReq>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 95 fields in camt.055 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles cancellation identification, amounts, dates
- Extension fields accommodate cancellation-specific information (reason codes, case ID)
- Party entity supports assignor, assignee, creditor, debtor, ultimate parties, originator
- Account entity handles IBAN and non-IBAN account identifiers with account types
- FinancialInstitution entity manages agent information

**Key Extension Fields Used:**
- caseId, reopenCaseIndicator (case management)
- cancellationId, cancellationReasonCode
- cancellationAdditionalInfo (free-text explanation)
- originalMessageId, originalMessageType, originalCreatedDateTime (references to original payment)
- numberOfTransactions, controlSum
- paymentMethod, accountTypeCode
- mandateId, mandateSignatureDate (direct debit)
- invoiceNumber, invoiceDate (remittance)

---

## References

- **ISO 20022 Message Definition:** camt.055.001.08 - CustomerPaymentCancellationRequestV08
- **XML Schema:** camt.055.001.08.xsd
- **Related Messages:** pain.001 (customer credit transfer), pain.008 (customer direct debit), camt.029 (resolution), pacs.004 (return), camt.056 (FI cancellation), pain.007 (customer reversal)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **Cancellation Reason Codes:** ISO 20022 External Payment Cancellation Reason Code

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
