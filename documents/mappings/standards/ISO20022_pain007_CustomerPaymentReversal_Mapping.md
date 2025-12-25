# ISO 20022 pain.007 - Customer Payment Reversal Request Mapping

## Message Overview

**Message Type:** pain.007.001.09 - CustomerPaymentReversalV09
**Category:** PAIN - Payment Initiation
**Purpose:** Sent by a customer to a bank to request reversal of a previously initiated payment
**Direction:** Customer → Bank
**Scope:** Customer-initiated reversal requests

**Key Use Cases:**
- Customer requests reversal of previously sent credit transfer (pain.001)
- Customer requests cancellation of direct debit initiation (pain.008)
- Error correction for duplicate payments
- Fraud detection and prevention
- Erroneous payment amount correction
- Wrong beneficiary correction

**Relationship to Other Messages:**
- **pain.001**: Customer credit transfer (can be reversed by pain.007)
- **pain.008**: Customer direct debit (can be reversed by pain.007)
- **pain.002**: Bank responds with status of reversal request
- **pacs.007**: Interbank payment reversal (FI-to-FI equivalent)
- **camt.056**: FI to FI payment cancellation request

**Comparison with Other Reversal/Cancellation Messages:**
- **pain.007**: Customer to bank reversal request
- **pacs.007**: FI to FI payment reversal (post-settlement)
- **pacs.004**: FI to FI payment return (pre-settlement)
- **camt.055**: Customer payment cancellation request
- **camt.056**: FI to FI payment cancellation request

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in pain.007** | 88 |
| **Fields Mapped to CDM** | 88 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- Party (debtor, creditor, assignee, assignor)
- Account (debtor account, creditor account)
- FinancialInstitution (instructing/instructed agents)
- ReversalRequest (reversal-specific information)

---

## Complete Field Mapping

### 1. Assignment (Assgnmt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Assgnmt/Id | Assignment Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique reversal request identifier |
| Assgnmt/Assgnr/Agt/FinInstnId/BICFI | Assignor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Customer's bank BIC |
| Assgnmt/Assgnr/Agt/FinInstnId/ClrSysMmbId/MmbId | Assignor Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| Assgnmt/Assgnr/Agt/FinInstnId/Nm | Assignor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Bank name |
| Assgnmt/Assgnr/Pty/Nm | Assignor Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Customer requesting reversal |
| Assgnmt/Assgnr/Pty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Assignor country |
| Assgnmt/Assgnr/Pty/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| Assgnmt/Assgnr/Pty/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID/org number |
| Assgnmt/Assgnr/Pty/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Birth Date | Date | - | 0..1 | ISODate | Party | dateOfBirth | Date of birth |
| Assgnmt/Assgnr/Pty/Id/PrvtId/Othr/Id | Private Other ID | Text | 1-35 | 0..1 | Free text | Party | nationalId | National ID |
| Assgnmt/Assgne/Agt/FinInstnId/BICFI | Assignee Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Recipient bank BIC |
| Assgnmt/Assgne/Agt/FinInstnId/ClrSysMmbId/MmbId | Assignee Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| Assgnmt/Assgne/Agt/FinInstnId/Nm | Assignee Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Recipient bank name |
| Assgnmt/Assgne/Pty/Nm | Assignee Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Party receiving reversal request |
| Assgnmt/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | createdDateTime | Reversal request timestamp |

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
| CtrlData/NbOfTxs | Number of Transactions | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | numberOfTransactions | Transaction count in reversal |
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
| Undrlyg/TxInf/RvslId | Reversal Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | reversalId | Unique reversal identifier |
| Undrlyg/TxInf/OrgnlInstrId | Original Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Original instruction reference |
| Undrlyg/TxInf/OrgnlEndToEndId | Original End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | endToEndId | Original E2E reference |
| Undrlyg/TxInf/OrgnlTxId | Original Transaction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Original transaction reference |
| Undrlyg/TxInf/OrgnlUETR | Original UETR | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Original universal unique identifier |
| Undrlyg/TxInf/OrgnlIntrBkSttlmAmt | Original Interbank Settlement Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | amount | Original settlement amount |
| Undrlyg/TxInf/OrgnlIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | currency | Settlement currency |
| Undrlyg/TxInf/OrgnlIntrBkSttlmDt | Original Interbank Settlement Date | Date | - | 0..1 | ISODate | PaymentInstruction | settlementDate | Original settlement date |
| Undrlyg/TxInf/RvsdIntrBkSttlmAmt | Reversed Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | reversedAmount | Amount to reverse |
| Undrlyg/TxInf/RvsdIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | reversedCurrency | Reversed amount currency |
| Undrlyg/TxInf/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | reversalSettlementDate | Reversal settlement date |
| Undrlyg/TxInf/RvsdInstdAmt | Reversed Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | reversedInstructedAmount | Reversed instructed amount |
| Undrlyg/TxInf/RvsdInstdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | reversedInstructedCurrency | Instructed amount currency |
| Undrlyg/TxInf/XchgRate | Exchange Rate | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | exchangeRate | FX rate applied |
| Undrlyg/TxInf/ChrgBr | Charge Bearer | Code | 4 | 0..1 | DEBT, CRED, SHAR, SLEV | PaymentInstruction.extensions | chargeBearer | Who pays charges |
| Undrlyg/TxInf/ChrgsInf/Amt | Charges Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction.extensions | chargesAmount | Charge amount |
| Undrlyg/TxInf/ChrgsInf/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | chargesCurrency | Charges currency |
| Undrlyg/TxInf/ChrgsInf/Agt/FinInstnId/BICFI | Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Charging agent BIC |

#### 4.3 Reversal Reason Information (RvslRsnInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/TxInf/RvslRsnInf/Orgtr/Nm | Originator Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Reversal reason originator |
| Undrlyg/TxInf/RvslRsnInf/Orgtr/Id/OrgId/AnyBIC | Originator BIC | Text | - | 0..1 | BIC format | Party | bic | Originator BIC |
| Undrlyg/TxInf/RvslRsnInf/Rsn/Cd | Reason Code | Code | - | 0..1 | FRAD, DUPL, TECH, CUST, etc. | PaymentInstruction.extensions | reversalReasonCode | ISO 20022 reversal reason |
| Undrlyg/TxInf/RvslRsnInf/Rsn/Prtry | Proprietary Reason | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryReversalReason | Custom reversal reason |
| Undrlyg/TxInf/RvslRsnInf/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | reversalAdditionalInfo | Free-text explanation |

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
| Undrlyg/TxInf/OrgnlTxRef/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Original creditor bank |
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

### Reversal Reason Code (RvslRsnInf/Rsn/Cd)

**Common Reversal Reasons:**
- **FRAD** - Fraudulent Payment (fraud detected)
- **DUPL** - Duplicate Payment (payment processed twice)
- **TECH** - Technical Problems (system/technical error)
- **CUST** - Requested by Customer (customer request)
- **AM09** - Wrong Amount (incorrect amount sent)
- **AC03** - Invalid Creditor Account Number (wrong beneficiary account)
- **AC06** - Blocked Account (account is blocked)
- **BE05** - Unrecognised Initiating Party (wrong initiator)
- **FF01** - Invalid File Format (file format issue)
- **MD01** - No Mandate (missing direct debit mandate)
- **MD06** - Refund Request by End Customer (customer refund request)
- **MS03** - Not Specified Reason Agent Generated (unspecified)

### Payment Method (PmtMtd)
- **CHK** - Cheque
- **TRF** - Credit Transfer
- **TRA** - Credit Transfer to Account

### Charge Bearer (ChrgBr)
- **DEBT** - Debtor bears all charges
- **CRED** - Creditor bears all charges
- **SHAR** - Charges shared
- **SLEV** - As per service level agreement

### Service Level (SvcLvl/Cd)
- **SEPA** - Single Euro Payments Area
- **SDVA** - Same Day Value
- **URGP** - Urgent Payment

### Instruction Priority (InstrPrty)
- **HIGH** - High priority
- **NORM** - Normal priority

---

## Message Examples

### Example 1: Fraud Reversal Request

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.007.001.09">
  <CstmrPmtRvsl>
    <Assgnmt>
      <Id>REVERSAL-REQ-20241220-001</Id>
      <Assgnr>
        <Pty>
          <Nm>John Smith</Nm>
          <PstlAdr>
            <Ctry>GB</Ctry>
          </PstlAdr>
        </Pty>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>ABCBGB2LXXX</BICFI>
            <Nm>ABC Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T15:30:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-FRAUD-2024-12345</Id>
      <Cretr>
        <Pty>
          <Nm>John Smith</Nm>
        </Pty>
      </Cretr>
    </Case>
    <CtrlData>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>15000.00</CtrlSum>
    </CtrlData>
    <Undrlyg>
      <OrgnlGrpInf>
        <OrgnlMsgId>PMT-20241218-5678</OrgnlMsgId>
        <OrgnlMsgNmId>pain.001.001.09</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-18T10:15:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <TxInf>
        <RvslId>REV-20241220-001</RvslId>
        <OrgnlInstrId>INSTR-20241218-001</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-PAYMENT-5678</OrgnlEndToEndId>
        <OrgnlTxId>TXN-20241218-001</OrgnlTxId>
        <RvsdIntrBkSttlmAmt Ccy="GBP">15000.00</RvsdIntrBkSttlmAmt>
        <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
        <RvslRsnInf>
          <Orgtr>
            <Nm>John Smith</Nm>
          </Orgtr>
          <Rsn>
            <Cd>FRAD</Cd>
          </Rsn>
          <AddtlInf>Fraudulent payment detected. My account was compromised. I did not authorize this payment to the beneficiary. Police report filed - reference: POL-2024-98765. Requesting immediate reversal.</AddtlInf>
        </RvslRsnInf>
        <OrgnlTxRef>
          <IntrBkSttlmAmt Ccy="GBP">15000.00</IntrBkSttlmAmt>
          <IntrBkSttlmDt>2024-12-18</IntrBkSttlmDt>
          <ReqdExctnDt>
            <Dt>2024-12-18</Dt>
          </ReqdExctnDt>
          <PmtTpInf>
            <InstrPrty>NORM</InstrPrty>
          </PmtTpInf>
          <PmtMtd>TRF</PmtMtd>
          <Dbtr>
            <Nm>John Smith</Nm>
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
            <Ustrd>Invoice payment - NOT AUTHORIZED</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInf>
    </Undrlyg>
  </CstmrPmtRvsl>
</Document>
```

### Example 2: Duplicate Payment Reversal

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.007.001.09">
  <CstmrPmtRvsl>
    <Assgnmt>
      <Id>REVERSAL-REQ-20241220-002</Id>
      <Assgnr>
        <Pty>
          <Nm>Global Manufacturing Inc</Nm>
          <Id>
            <OrgId>
              <Othr>
                <Id>GB123456789</Id>
              </Othr>
            </OrgId>
          </Id>
        </Pty>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>GLBNGB2LXXX</BICFI>
            <Nm>Global Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T11:45:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-DUPL-2024-67890</Id>
      <Cretr>
        <Pty>
          <Nm>Global Manufacturing Inc - Finance Dept</Nm>
        </Pty>
      </Cretr>
    </Case>
    <CtrlData>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>25000.00</CtrlSum>
    </CtrlData>
    <Undrlyg>
      <OrgnlGrpInf>
        <OrgnlMsgId>PMT-20241219-9999</OrgnlMsgId>
        <OrgnlMsgNmId>pain.001.001.09</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-19T16:30:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <TxInf>
        <RvslId>REV-DUPL-001</RvslId>
        <OrgnlInstrId>INSTR-20241219-DUPL</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-INV-88888-DUPLICATE</OrgnlEndToEndId>
        <OrgnlTxId>TXN-20241219-DUPL</OrgnlTxId>
        <RvsdIntrBkSttlmAmt Ccy="EUR">25000.00</RvsdIntrBkSttlmAmt>
        <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
        <RvslRsnInf>
          <Orgtr>
            <Nm>Global Manufacturing Inc</Nm>
          </Orgtr>
          <Rsn>
            <Cd>DUPL</Cd>
          </Rsn>
          <AddtlInf>Duplicate payment submitted in error. Same invoice (INV-88888) was paid twice on 2024-12-19 due to system error. First payment (E2E-INV-88888-ORIGINAL) already settled successfully. This second payment should be reversed.</AddtlInf>
        </RvslRsnInf>
        <OrgnlTxRef>
          <IntrBkSttlmAmt Ccy="EUR">25000.00</IntrBkSttlmAmt>
          <IntrBkSttlmDt>2024-12-19</IntrBkSttlmDt>
          <PmtMtd>TRF</PmtMtd>
          <Dbtr>
            <Nm>Global Manufacturing Inc</Nm>
            <PstlAdr>
              <StrtNm>Industrial Avenue</StrtNm>
              <PstCd>M1 1AA</PstCd>
              <TwnNm>Manchester</TwnNm>
              <Ctry>GB</Ctry>
            </PstlAdr>
            <Id>
              <OrgId>
                <Othr>
                  <Id>GB123456789</Id>
                </Othr>
              </OrgId>
            </Id>
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
            <Nm>Parts Supplier SARL</Nm>
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
            <Ustrd>Invoice INV-88888 - Parts delivery December 2024 - DUPLICATE</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInf>
    </Undrlyg>
  </CstmrPmtRvsl>
</Document>
```

### Example 3: Wrong Amount Reversal

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.007.001.09">
  <CstmrPmtRvsl>
    <Assgnmt>
      <Id>REVERSAL-REQ-20241220-003</Id>
      <Assgnr>
        <Pty>
          <Nm>Jane Doe</Nm>
        </Pty>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>NWBKGB2LXXX</BICFI>
            <Nm>National Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T09:15:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-WRONGAMT-2024-111</Id>
      <Cretr>
        <Pty>
          <Nm>Jane Doe</Nm>
        </Pty>
      </Cretr>
    </Case>
    <CtrlData>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>5000.00</CtrlSum>
    </CtrlData>
    <Undrlyg>
      <OrgnlGrpInf>
        <OrgnlMsgId>PMT-20241220-WRONG</OrgnlMsgId>
        <OrgnlMsgNmId>pain.001.001.09</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-20T08:30:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <TxInf>
        <RvslId>REV-WRONGAMT-001</RvslId>
        <OrgnlInstrId>INSTR-WRONG-AMT</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-RENT-DEC-2024</OrgnlEndToEndId>
        <OrgnlTxId>TXN-WRONG-AMT</OrgnlTxId>
        <RvsdIntrBkSttlmAmt Ccy="GBP">5000.00</RvsdIntrBkSttlmAmt>
        <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
        <RvslRsnInf>
          <Orgtr>
            <Nm>Jane Doe</Nm>
          </Orgtr>
          <Rsn>
            <Cd>AM09</Cd>
          </Rsn>
          <AddtlInf>Incorrect payment amount sent. Intended to pay £500.00 for monthly rent but accidentally entered £5,000.00. Requesting reversal of entire amount. Will resubmit with correct amount of £500.00.</AddtlInf>
        </RvslRsnInf>
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
            <Nm>Property Management Ltd</Nm>
            <PstlAdr>
              <TwnNm>London</TwnNm>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <IBAN>GB12BARC20005512345678</IBAN>
            </Id>
          </CdtrAcct>
          <RmtInf>
            <Ustrd>December 2024 rent payment - WRONG AMOUNT</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInf>
    </Undrlyg>
  </CstmrPmtRvsl>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 88 fields in pain.007 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles reversal identification, amounts, dates
- Extension fields accommodate reversal-specific information (reason codes, case ID)
- Party entity supports assignor, assignee, creditor, debtor, ultimate parties
- Account entity handles IBAN and non-IBAN account identifiers
- FinancialInstitution entity manages agent information

**Key Extension Fields Used:**
- caseId, reopenCaseIndicator (case management)
- reversalId, reversalReasonCode (FRAD, DUPL, TECH, CUST, AM09, etc.)
- reversalAdditionalInfo (free-text explanation)
- reversedAmount, reversedInstructedAmount (amounts being reversed)
- originalMessageId, originalMessageType, originalCreatedDateTime (references to original payment)

---

## References

- **ISO 20022 Message Definition:** pain.007.001.09 - CustomerPaymentReversalV09
- **XML Schema:** pain.007.001.09.xsd
- **Related Messages:** pain.001 (credit transfer), pain.008 (direct debit), pain.002 (status report), pacs.007 (FI reversal)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **Reversal Reason Codes:** ISO 20022 External Payment Reversal Reason Code

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
