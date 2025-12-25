# ISO 20022 camt.026 - Unable to Apply Mapping

## Message Overview

**Message Type:** camt.026.001.07 - UnableToApplyV07
**Category:** CAMT - Cash Management
**Purpose:** Sent by an account servicer to the account owner or previous party in the payment chain when a payment is received but cannot be applied to an account due to missing or incorrect information
**Direction:** Account Servicer → Account Owner / Previous Party
**Scope:** Exception handling for payments that cannot be processed/credited

**Key Use Cases:**
- Payment received with missing creditor/debtor information
- Incorrect or invalid account number provided
- Missing remittance information required for posting
- Payment amount discrepancy with expected amount
- Duplicate payment identification
- Technical errors preventing posting
- Investigations for unmatched payments

**Relationship to Other Messages:**
- **pacs.008**: Credit transfer that could not be applied
- **pacs.003**: Direct debit that could not be applied
- **camt.027**: Claim non-receipt (complementary investigation)
- **camt.029**: Resolution of Investigation (response to unable to apply)
- **camt.087**: Request to Modify Payment (may trigger unable to apply)
- **pain.001**: Customer credit transfer instruction (original instruction)

**Comparison with Related Messages:**
- **camt.026**: Unable to Apply - account servicer cannot post payment to account
- **camt.027**: Claim Non-Receipt - account owner claims payment not received
- **camt.029**: Resolution - response/resolution to investigation cases
- **camt.056**: Cancellation Request - proactive cancellation before receipt
- **pacs.004**: Payment Return - return of funds with reason code

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in camt.026** | 68 |
| **Fields Mapped to CDM** | 68 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- PaymentInstruction.extensions (caseId, investigationStatus, unableToApplyReason)
- Party (assignor, assignee, case creator, claimant)
- Account (missing/incorrect account details)
- FinancialInstitution (account servicer, instructing agent)
- ComplianceCase (investigation case management)

---

## Complete Field Mapping

### 1. Assignment (Assgnmt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Assgnmt/Id | Assignment Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique assignment identifier |
| Assgnmt/Assgnr/Agt/FinInstnId/BICFI | Assignor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Account servicer BIC |
| Assgnmt/Assgnr/Agt/FinInstnId/ClrSysMmbId/MmbId | Assignor Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| Assgnmt/Assgnr/Agt/FinInstnId/Nm | Assignor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Account servicer name |
| Assgnmt/Assgnr/Agt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Servicer country |
| Assgnmt/Assgnr/Pty/Nm | Assignor Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Assignor party |
| Assgnmt/Assgnr/Pty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Assignor country |
| Assgnmt/Assgnr/Pty/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| Assgnmt/Assgnr/Pty/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID/org number |
| Assgnmt/Assgne/Agt/FinInstnId/BICFI | Assignee Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Previous party BIC |
| Assgnmt/Assgne/Agt/FinInstnId/ClrSysMmbId/MmbId | Assignee Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| Assgnmt/Assgne/Agt/FinInstnId/Nm | Assignee Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Previous party name |
| Assgnmt/Assgne/Agt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Assignee country |
| Assgnmt/Assgne/Pty/Nm | Assignee Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Assignee party |
| Assgnmt/Assgne/Pty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Assignee country |
| Assgnmt/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | createdDateTime | Unable to apply message timestamp |

### 2. Case (Case)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Case/Id | Case Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | caseId | Unique case identifier |
| Case/Cretr/Agt/FinInstnId/BICFI | Creator Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Case creator bank BIC |
| Case/Cretr/Agt/FinInstnId/Nm | Creator Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Case creator bank name |
| Case/Cretr/Pty/Nm | Creator Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Party creating case |
| Case/Cretr/Pty/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| Case/ReopCaseIndctn | Reopen Case Indication | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | reopenCaseIndicator | Whether case is being reopened |

### 3. Underlying Transaction (Undrlyg)

#### 3.1 Original Group Information (OrgnlGrpInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/OrgnlGrpInf/OrgnlMsgId | Original Message ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | originalMessageId | Reference to original message |
| Undrlyg/OrgnlGrpInf/OrgnlMsgNmId | Original Message Name ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | originalMessageType | e.g., "pacs.008.001.08" |
| Undrlyg/OrgnlGrpInf/OrgnlCreDtTm | Original Creation DateTime | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | originalCreatedDateTime | Original message timestamp |

#### 3.2 Transaction Information (TxInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/TxInf/OrgnlInstrId | Original Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Original instruction reference |
| Undrlyg/TxInf/OrgnlEndToEndId | Original End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | endToEndId | Original E2E reference |
| Undrlyg/TxInf/OrgnlTxId | Original Transaction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Original transaction reference |
| Undrlyg/TxInf/OrgnlUETR | Original UETR | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Original universal unique identifier |
| Undrlyg/TxInf/OrgnlIntrBkSttlmAmt | Original Interbank Settlement Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | interbankSettlementAmount.amount | Original settlement amount |
| Undrlyg/TxInf/OrgnlIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | interbankSettlementAmount.currency | Settlement currency |
| Undrlyg/TxInf/OrgnlIntrBkSttlmDt | Original Interbank Settlement Date | Date | - | 0..1 | ISODate | PaymentInstruction | settlementDate | Original settlement date |

#### 3.3 Unable to Apply Reason (UblToApply)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/TxInf/UblToApply/MssngOrIncrrctInf/AMLReq | AML Requirement Indicator | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | amlRequirementIndicator | AML info missing |
| Undrlyg/TxInf/UblToApply/MssngOrIncrrctInf/MssngCdtrAcct | Missing Creditor Account | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | missingCreditorAccount | Creditor account missing |
| Undrlyg/TxInf/UblToApply/MssngOrIncrrctInf/MssngCdtr | Missing Creditor | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | missingCreditor | Creditor details missing |
| Undrlyg/TxInf/UblToApply/MssngOrIncrrctInf/MssngDbtr | Missing Debtor | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | missingDebtor | Debtor details missing |
| Undrlyg/TxInf/UblToApply/MssngOrIncrrctInf/MssngDbtrAcct | Missing Debtor Account | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | missingDebtorAccount | Debtor account missing |
| Undrlyg/TxInf/UblToApply/MssngOrIncrrctInf/MssngRmtInf | Missing Remittance Info | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | missingRemittanceInfo | Remittance info missing |
| Undrlyg/TxInf/UblToApply/MssngOrIncrrctInf/IncrrctCdtrAcct | Incorrect Creditor Account | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | incorrectCreditorAccount | Creditor account incorrect |
| Undrlyg/TxInf/UblToApply/MssngOrIncrrctInf/IncrrctCdtr | Incorrect Creditor | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | incorrectCreditor | Creditor details incorrect |
| Undrlyg/TxInf/UblToApply/MssngOrIncrrctInf/IncrrctDbtr | Incorrect Debtor | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | incorrectDebtor | Debtor details incorrect |
| Undrlyg/TxInf/UblToApply/MssngOrIncrrctInf/IncrrctDbtrAcct | Incorrect Debtor Account | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | incorrectDebtorAccount | Debtor account incorrect |
| Undrlyg/TxInf/UblToApply/MssngOrIncrrctInf/IncrrctAmt | Incorrect Amount | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | incorrectAmount | Amount incorrect |
| Undrlyg/TxInf/UblToApply/PssblDplctInstdAmt | Possible Duplicate Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | possibleDuplicateAmount | Suspected duplicate amount |
| Undrlyg/TxInf/UblToApply/PssblDplctInstdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | possibleDuplicateCurrency | Duplicate currency |
| Undrlyg/TxInf/UblToApply/Rsn/Cd | Reason Code | Code | - | 0..1 | NARR, AC01, AM09, etc. | PaymentInstruction.extensions | unableToApplyReasonCode | ISO 20022 unable to apply reason |
| Undrlyg/TxInf/UblToApply/Rsn/Prtry | Proprietary Reason | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryUnableToApplyReason | Custom reason |
| Undrlyg/TxInf/UblToApply/AddtlUblToApplyInf | Additional Unable to Apply Info | Text | 1-500 | 0..1 | Free text | PaymentInstruction.extensions | unableToApplyAdditionalInfo | Free-text explanation |

#### 3.4 Original Transaction Reference (OrgnlTxRef)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/TxInf/OrgnlTxRef/IntrBkSttlmAmt | Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | originalSettlementAmount | Original settlement amount |
| Undrlyg/TxInf/OrgnlTxRef/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | originalSettlementCurrency | Settlement currency |
| Undrlyg/TxInf/OrgnlTxRef/Amt/InstdAmt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | instructedAmount.amount | Original instructed amount |
| Undrlyg/TxInf/OrgnlTxRef/Amt/InstdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | instructedAmount.currency | Instructed currency |
| Undrlyg/TxInf/OrgnlTxRef/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISODate | PaymentInstruction | settlementDate | Original settlement date |
| Undrlyg/TxInf/OrgnlTxRef/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Original debtor |
| Undrlyg/TxInf/OrgnlTxRef/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Debtor country |
| Undrlyg/TxInf/OrgnlTxRef/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Original debtor account |
| Undrlyg/TxInf/OrgnlTxRef/DbtrAcct/Id/Othr/Id | Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN debtor account |
| Undrlyg/TxInf/OrgnlTxRef/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Original debtor bank |
| Undrlyg/TxInf/OrgnlTxRef/DbtrAgt/FinInstnId/Nm | Debtor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Debtor bank name |
| Undrlyg/TxInf/OrgnlTxRef/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Original creditor bank |
| Undrlyg/TxInf/OrgnlTxRef/CdtrAgt/FinInstnId/Nm | Creditor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Creditor bank name |
| Undrlyg/TxInf/OrgnlTxRef/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Original creditor |
| Undrlyg/TxInf/OrgnlTxRef/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Creditor country |
| Undrlyg/TxInf/OrgnlTxRef/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Original creditor account |
| Undrlyg/TxInf/OrgnlTxRef/CdtrAcct/Id/Othr/Id | Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN creditor account |
| Undrlyg/TxInf/OrgnlTxRef/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction | remittanceInformation | Original remittance info |

### 4. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Unable to Apply Reason Code (UblToApply/Rsn/Cd)

**Common Unable to Apply Reasons:**
- **NARR** - Narrative (free-text reason provided)
- **AC01** - Incorrect Account Number (wrong account)
- **AC04** - Closed Account (account has been closed)
- **AC06** - Blocked Account (account is blocked)
- **AM09** - Wrong Amount (incorrect payment amount)
- **BE05** - Unrecognised Initiating Party (unknown debtor)
- **BE07** - Missing Creditor Address (address required but not provided)
- **CUST** - Customer Decision (customer requested unable to apply)
- **NARR** - Narrative Reason (detailed explanation in text)
- **TECH** - Technical Problem (system/technical issue)
- **NOAS** - No Answer from Customer (customer did not respond)
- **RQDA** - Requested Additional Information (more data needed)

### Missing or Incorrect Information Indicators

**Boolean Indicators (true/false):**
- **AMLReq** - AML/CTF information missing
- **MssngCdtrAcct** - Missing creditor account
- **MssngCdtr** - Missing creditor details
- **MssngDbtr** - Missing debtor details
- **MssngDbtrAcct** - Missing debtor account
- **MssngRmtInf** - Missing remittance information
- **IncrrctCdtrAcct** - Incorrect creditor account
- **IncrrctCdtr** - Incorrect creditor details
- **IncrrctDbtr** - Incorrect debtor details
- **IncrrctDbtrAcct** - Incorrect debtor account
- **IncrrctAmt** - Incorrect amount

---

## Message Examples

### Example 1: Unable to Apply - Missing Creditor Account

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.026.001.07">
  <UblToApply>
    <Assgnmt>
      <Id>UTA-20241220-MISSING-ACCT-001</Id>
      <Assgnr>
        <Agt>
          <FinInstnId>
            <BICFI>RECVGB2LXXX</BICFI>
            <Nm>Receiving Bank - Account Servicer</Nm>
          </FinInstnId>
        </Agt>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>SENDGB2LXXX</BICFI>
            <Nm>Sending Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T10:30:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-UTA-2024-12345</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>RECVGB2LXXX</BICFI>
            <Nm>Receiving Bank - Operations</Nm>
          </FinInstnId>
        </Agt>
      </Cretr>
    </Case>
    <Undrlyg>
      <OrgnlGrpInf>
        <OrgnlMsgId>PMT-20241220-ORIG-789</OrgnlMsgId>
        <OrgnlMsgNmId>pacs.008.001.08</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-20T09:00:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <TxInf>
        <OrgnlInstrId>INSTR-MISSING-ACCT</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-PAYMENT-NO-ACCOUNT</OrgnlEndToEndId>
        <OrgnlTxId>TXN-MISSING-ACCT-001</OrgnlTxId>
        <OrgnlUETR>123e4567-e89b-12d3-a456-426614174000</OrgnlUETR>
        <OrgnlIntrBkSttlmAmt Ccy="GBP">15000.00</OrgnlIntrBkSttlmAmt>
        <OrgnlIntrBkSttlmDt>2024-12-20</OrgnlIntrBkSttlmDt>
        <UblToApply>
          <MssngOrIncrrctInf>
            <MssngCdtrAcct>true</MssngCdtrAcct>
          </MssngOrIncrrctInf>
          <Rsn>
            <Cd>AC01</Cd>
          </Rsn>
          <AddtlUblToApplyInf>Payment received but creditor account number is missing from the payment instruction. Unable to identify beneficiary account for posting. Please provide valid account number (IBAN or domestic account number) to process payment. Payment amount GBP 15,000.00 is being held pending resolution.</AddtlUblToApplyInf>
        </UblToApply>
        <OrgnlTxRef>
          <IntrBkSttlmAmt Ccy="GBP">15000.00</IntrBkSttlmAmt>
          <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
          <Dbtr>
            <Nm>Manufacturing Ltd</Nm>
            <PstlAdr>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <IBAN>GB29SEND60161331926819</IBAN>
            </Id>
          </DbtrAcct>
          <DbtrAgt>
            <FinInstnId>
              <BICFI>SENDGB2LXXX</BICFI>
            </FinInstnId>
          </DbtrAgt>
          <CdtrAgt>
            <FinInstnId>
              <BICFI>RECVGB2LXXX</BICFI>
            </FinInstnId>
          </CdtrAgt>
          <Cdtr>
            <Nm>Services Corp</Nm>
            <PstlAdr>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Cdtr>
          <RmtInf>
            <Ustrd>Invoice INV-2024-5678 payment - ACCOUNT NUMBER MISSING</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInf>
    </Undrlyg>
  </UblToApply>
</Document>
```

### Example 2: Unable to Apply - Missing Remittance Information

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.026.001.07">
  <UblToApply>
    <Assgnmt>
      <Id>UTA-20241220-MISSING-REMIT-002</Id>
      <Assgnr>
        <Agt>
          <FinInstnId>
            <BICFI>UTILGB2LXXX</BICFI>
            <Nm>Utility Company Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>CUSTGB2LXXX</BICFI>
            <Nm>Customer Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T14:15:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-UTA-REMIT-2024-99999</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>UTILGB2LXXX</BICFI>
            <Nm>Utility Company - Payment Processing</Nm>
          </FinInstnId>
        </Agt>
      </Cretr>
    </Case>
    <Undrlyg>
      <OrgnlGrpInf>
        <OrgnlMsgId>PMT-20241220-UTILITY-456</OrgnlMsgId>
        <OrgnlMsgNmId>pacs.008.001.08</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-20T13:00:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <TxInf>
        <OrgnlInstrId>INSTR-NO-REMIT</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-UTILITY-PAYMENT</OrgnlEndToEndId>
        <OrgnlTxId>TXN-NO-REMIT-456</OrgnlTxId>
        <OrgnlIntrBkSttlmAmt Ccy="GBP">250.00</OrgnlIntrBkSttlmAmt>
        <OrgnlIntrBkSttlmDt>2024-12-20</OrgnlIntrBkSttlmDt>
        <UblToApply>
          <MssngOrIncrrctInf>
            <MssngRmtInf>true</MssngRmtInf>
          </MssngOrIncrrctInf>
          <Rsn>
            <Cd>NARR</Cd>
          </Rsn>
          <AddtlUblToApplyInf>Payment received for GBP 250.00 but remittance information (customer account number or reference number) is missing. Unable to match payment to customer account without reference. Please provide customer account number or invoice/bill reference in remittance field to allocate payment correctly.</AddtlUblToApplyInf>
        </UblToApply>
        <OrgnlTxRef>
          <IntrBkSttlmAmt Ccy="GBP">250.00</IntrBkSttlmAmt>
          <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
          <Dbtr>
            <Nm>John Smith</Nm>
            <PstlAdr>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <IBAN>GB67CUST40306112345678</IBAN>
            </Id>
          </DbtrAcct>
          <DbtrAgt>
            <FinInstnId>
              <BICFI>CUSTGB2LXXX</BICFI>
            </FinInstnId>
          </DbtrAgt>
          <CdtrAgt>
            <FinInstnId>
              <BICFI>UTILGB2LXXX</BICFI>
            </FinInstnId>
          </CdtrAgt>
          <Cdtr>
            <Nm>Utility Company Ltd</Nm>
            <PstlAdr>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <IBAN>GB98UTIL12345678901234</IBAN>
            </Id>
          </CdtrAcct>
        </OrgnlTxRef>
      </TxInf>
    </Undrlyg>
  </UblToApply>
</Document>
```

### Example 3: Unable to Apply - Incorrect Account Number

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.026.001.07">
  <UblToApply>
    <Assgnmt>
      <Id>UTA-20241220-WRONG-ACCT-003</Id>
      <Assgnr>
        <Agt>
          <FinInstnId>
            <BICFI>PAYEGB2LXXX</BICFI>
            <Nm>Payee Bank - Account Servicer</Nm>
          </FinInstnId>
        </Agt>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>PAYRGB2LXXX</BICFI>
            <Nm>Payer Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T16:45:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-UTA-WRONGACCT-2024-77777</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>PAYEGB2LXXX</BICFI>
            <Nm>Payee Bank - Exception Handling Team</Nm>
          </FinInstnId>
        </Agt>
      </Cretr>
    </Case>
    <Undrlyg>
      <OrgnlGrpInf>
        <OrgnlMsgId>PMT-20241220-SALARY-888</OrgnlMsgId>
        <OrgnlMsgNmId>pacs.008.001.08</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-20T15:30:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <TxInf>
        <OrgnlInstrId>INSTR-WRONGACCT-888</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-SALARY-DECEMBER</OrgnlEndToEndId>
        <OrgnlTxId>TXN-WRONGACCT-888</OrgnlTxId>
        <OrgnlIntrBkSttlmAmt Ccy="GBP">3500.00</OrgnlIntrBkSttlmAmt>
        <OrgnlIntrBkSttlmDt>2024-12-20</OrgnlIntrBkSttlmDt>
        <UblToApply>
          <MssngOrIncrrctInf>
            <IncrrctCdtrAcct>true</IncrrctCdtrAcct>
          </MssngOrIncrrctInf>
          <Rsn>
            <Cd>AC01</Cd>
          </Rsn>
          <AddtlUblToApplyInf>Payment for GBP 3,500.00 received but creditor account number GB12PAYE20005512345678 does not exist in our system. Account may have been closed or number is incorrect. Check digit validation failed. Please verify correct beneficiary account number and resubmit payment instruction.</AddtlUblToApplyInf>
        </UblToApply>
        <OrgnlTxRef>
          <IntrBkSttlmAmt Ccy="GBP">3500.00</IntrBkSttlmAmt>
          <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
          <Dbtr>
            <Nm>Corporate Employer Ltd</Nm>
            <PstlAdr>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <IBAN>GB45PAYR30405067890123</IBAN>
            </Id>
          </DbtrAcct>
          <DbtrAgt>
            <FinInstnId>
              <BICFI>PAYRGB2LXXX</BICFI>
            </FinInstnId>
          </DbtrAgt>
          <CdtrAgt>
            <FinInstnId>
              <BICFI>PAYEGB2LXXX</BICFI>
            </FinInstnId>
          </CdtrAgt>
          <Cdtr>
            <Nm>Employee Jane Doe</Nm>
            <PstlAdr>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <IBAN>GB12PAYE20005512345678</IBAN>
            </Id>
          </CdtrAcct>
          <RmtInf>
            <Ustrd>Salary December 2024 - INCORRECT ACCOUNT</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInf>
    </Undrlyg>
  </UblToApply>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 68 fields in camt.026 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles payment identification, amounts, dates, party references
- Extension fields accommodate unable-to-apply-specific information
- Boolean flags for missing/incorrect information indicators
- Party entity supports assignor, assignee, case creator, debtor, creditor
- Account entity handles IBAN and non-IBAN account identifiers
- FinancialInstitution entity manages agent information
- ComplianceCase entity supports investigation case management

**Key Extension Fields Used:**
- caseId, reopenCaseIndicator (case management)
- unableToApplyReasonCode, proprietaryUnableToApplyReason
- unableToApplyAdditionalInfo (free-text explanation)
- originalMessageId, originalMessageType, originalCreatedDateTime
- Missing info flags: missingCreditorAccount, missingCreditor, missingDebtor, missingDebtorAccount, missingRemittanceInfo, amlRequirementIndicator
- Incorrect info flags: incorrectCreditorAccount, incorrectCreditor, incorrectDebtor, incorrectDebtorAccount, incorrectAmount
- possibleDuplicateAmount, possibleDuplicateCurrency (duplicate detection)

---

## References

- **ISO 20022 Message Definition:** camt.026.001.07 - UnableToApplyV07
- **XML Schema:** camt.026.001.07.xsd
- **Related Messages:** pacs.008 (credit transfer), pacs.003 (direct debit), camt.027 (claim non-receipt), camt.029 (resolution), camt.087 (request to modify)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **Unable to Apply Reason Codes:** ISO 20022 External Payment Unable to Apply Reason Code

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
