# ISO 20022 camt.027 - Claim Non Receipt Mapping

## Message Overview

**Message Type:** camt.027.001.07 - ClaimNonReceiptV07
**Category:** CAMT - Cash Management
**Purpose:** Sent by the account owner (creditor) or the previous party in the payment chain to claim that an expected payment has not been received
**Direction:** Account Owner / Creditor → Account Servicer / Previous Party
**Scope:** Investigation for payments that should have been received but were not

**Key Use Cases:**
- Creditor claims payment not received as expected
- Expected payment missing from account
- Duplicate payment claim (payment received multiple times)
- Payment received but for wrong amount
- Payment tracing and investigation
- SWIFT gpi payment tracking queries
- Cross-border payment status inquiries

**Relationship to Other Messages:**
- **pacs.008**: Credit transfer that should have been received
- **pacs.003**: Direct debit that should have been received
- **pain.001**: Original customer credit transfer instruction
- **camt.026**: Unable to Apply (complementary investigation)
- **camt.029**: Resolution of Investigation (response to claim)
- **camt.056**: FI Payment Cancellation Request (may trigger claim)
- **camt.060**: Account Reporting (to verify non-receipt)

**Comparison with Related Messages:**
- **camt.027**: Claim Non-Receipt - payment expected but not received
- **camt.026**: Unable to Apply - payment received but cannot be posted
- **camt.029**: Resolution - response/resolution to investigation cases
- **camt.056**: Cancellation Request - proactive cancellation
- **camt.087**: Request to Modify Payment - modification request

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in camt.027** | 72 |
| **Fields Mapped to CDM** | 72 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- PaymentInstruction.extensions (caseId, investigationStatus, claimType, claimReason)
- Party (assignor, assignee, case creator, claimant)
- Account (missing payment account details)
- FinancialInstitution (account servicer, instructing agent)
- ComplianceCase (investigation case management, priority)

---

## Complete Field Mapping

### 1. Assignment (Assgnmt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Assgnmt/Id | Assignment Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique assignment identifier |
| Assgnmt/Assgnr/Agt/FinInstnId/BICFI | Assignor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Claimant bank BIC |
| Assgnmt/Assgnr/Agt/FinInstnId/ClrSysMmbId/MmbId | Assignor Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| Assgnmt/Assgnr/Agt/FinInstnId/Nm | Assignor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Claimant bank name |
| Assgnmt/Assgnr/Agt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Assignor country |
| Assgnmt/Assgnr/Pty/Nm | Assignor Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Assignor party |
| Assgnmt/Assgnr/Pty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Assignor country |
| Assgnmt/Assgnr/Pty/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| Assgnmt/Assgnr/Pty/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID/org number |
| Assgnmt/Assgne/Agt/FinInstnId/BICFI | Assignee Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Respondent bank BIC |
| Assgnmt/Assgne/Agt/FinInstnId/ClrSysMmbId/MmbId | Assignee Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| Assgnmt/Assgne/Agt/FinInstnId/Nm | Assignee Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Respondent bank name |
| Assgnmt/Assgne/Agt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Assignee country |
| Assgnmt/Assgne/Pty/Nm | Assignee Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Assignee party |
| Assgnmt/Assgne/Pty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Assignee country |
| Assgnmt/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | createdDateTime | Claim message timestamp |

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

#### 3.3 Claim Non-Receipt Details (ClmNonRct)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/TxInf/ClmNonRct/DtPrcd | Date Proceeded | Date | - | 1..1 | ISODate | PaymentInstruction.extensions | claimProceedDate | Date claim is being processed |
| Undrlyg/TxInf/ClmNonRct/OrgnlIntrmyAgt1/FinInstnId/BICFI | Original Intermediary Agent 1 BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Intermediary 1 in chain |
| Undrlyg/TxInf/ClmNonRct/OrgnlIntrmyAgt1/FinInstnId/Nm | Original Intermediary Agent 1 Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Intermediary 1 name |
| Undrlyg/TxInf/ClmNonRct/OrgnlIntrmyAgt2/FinInstnId/BICFI | Original Intermediary Agent 2 BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Intermediary 2 in chain |
| Undrlyg/TxInf/ClmNonRct/OrgnlIntrmyAgt2/FinInstnId/Nm | Original Intermediary Agent 2 Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Intermediary 2 name |
| Undrlyg/TxInf/ClmNonRct/OrgnlIntrmyAgt3/FinInstnId/BICFI | Original Intermediary Agent 3 BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Intermediary 3 in chain |
| Undrlyg/TxInf/ClmNonRct/OrgnlIntrmyAgt3/FinInstnId/Nm | Original Intermediary Agent 3 Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Intermediary 3 name |
| Undrlyg/TxInf/ClmNonRct/ClmNonRctDtls/ClmdAmt | Claimed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | claimedAmount | Amount being claimed |
| Undrlyg/TxInf/ClmNonRct/ClmNonRctDtls/ClmdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | claimedCurrency | Claimed currency |
| Undrlyg/TxInf/ClmNonRct/ClmNonRctDtls/ClmNonRctJstfn/MssngOrIncrrctInf/MssngCdtr | Missing Creditor | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | missingCreditorClaim | Creditor missing indicator |
| Undrlyg/TxInf/ClmNonRct/ClmNonRctDtls/ClmNonRctJstfn/MssngOrIncrrctInf/IncrrctCdtr | Incorrect Creditor | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | incorrectCreditorClaim | Creditor incorrect indicator |
| Undrlyg/TxInf/ClmNonRct/ClmNonRctDtls/ClmNonRctJstfn/MssngOrIncrrctInf/MssngDbtr | Missing Debtor | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | missingDebtorClaim | Debtor missing indicator |
| Undrlyg/TxInf/ClmNonRct/ClmNonRctDtls/ClmNonRctJstfn/MssngOrIncrrctInf/IncrrctDbtr | Incorrect Debtor | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | incorrectDebtorClaim | Debtor incorrect indicator |
| Undrlyg/TxInf/ClmNonRct/ClmNonRctDtls/ClmNonRctJstfn/MssngOrIncrrctInf/IncrrctAmt | Incorrect Amount | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | incorrectAmountClaim | Amount incorrect indicator |
| Undrlyg/TxInf/ClmNonRct/ClmNonRctDtls/ClmNonRctJstfn/CdtrRefInf | Creditor Reference Information | Text | 1-500 | 0..1 | Free text | PaymentInstruction.extensions | creditorReferenceInfo | Creditor's reference details |
| Undrlyg/TxInf/ClmNonRct/ClmNonRctDtls/ClmNonRctRsn/Cd | Claim Non-Receipt Reason Code | Code | - | 0..1 | NRCV, DUPL, etc. | PaymentInstruction.extensions | claimNonReceiptReasonCode | ISO 20022 claim reason |
| Undrlyg/TxInf/ClmNonRct/ClmNonRctDtls/ClmNonRctRsn/Prtry | Proprietary Reason | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryClaimReason | Custom claim reason |
| Undrlyg/TxInf/ClmNonRct/ClmNonRctDtls/AddtlClmNonRctInf | Additional Claim Non-Receipt Info | Text | 1-500 | 0..1 | Free text | PaymentInstruction.extensions | claimAdditionalInfo | Free-text explanation |

#### 3.4 Original Transaction Reference (OrgnlTxRef)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/TxInf/OrgnlTxRef/IntrBkSttlmAmt | Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | originalSettlementAmount | Original settlement amount |
| Undrlyg/TxInf/OrgnlTxRef/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | originalSettlementCurrency | Settlement currency |
| Undrlyg/TxInf/OrgnlTxRef/Amt/InstdAmt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | instructedAmount.amount | Original instructed amount |
| Undrlyg/TxInf/OrgnlTxRef/Amt/InstdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | instructedAmount.currency | Instructed currency |
| Undrlyg/TxInf/OrgnlTxRef/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISODate | PaymentInstruction | settlementDate | Original settlement date |
| Undrlyg/TxInf/OrgnlTxRef/ReqdExctnDt/Dt | Requested Execution Date | Date | - | 0..1 | ISODate | PaymentInstruction | requestedExecutionDate | Original execution date |
| Undrlyg/TxInf/OrgnlTxRef/ReqdExctnDt/DtTm | Requested Execution DateTime | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | requestedExecutionDateTime | Original execution timestamp |
| Undrlyg/TxInf/OrgnlTxRef/PmtTpInf/InstrPrty | Instruction Priority | Code | 4 | 0..1 | HIGH, NORM | ComplianceCase | priority | Original priority (map to case) |
| Undrlyg/TxInf/OrgnlTxRef/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | - | 0..1 | SEPA, SDVA, URGP | PaymentInstruction | serviceLevel | Original service level |
| Undrlyg/TxInf/OrgnlTxRef/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | - | 0..1 | CORE, B2B, etc. | PaymentInstruction | localInstrument | Regional instrument |
| Undrlyg/TxInf/OrgnlTxRef/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | - | 0..1 | CASH, CORT, etc. | PaymentInstruction | categoryPurpose | Payment category |
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
| Undrlyg/TxInf/OrgnlTxRef/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | invoiceNumber | Original invoice number |

### 4. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Claim Non-Receipt Reason Code (ClmNonRctRsn/Cd)

**Common Claim Non-Receipt Reasons:**
- **NRCV** - Payment Not Received (expected payment not arrived)
- **DUPL** - Duplicate Payment (payment received multiple times)
- **FRAD** - Fraudulent Payment (suspected fraud)
- **TECH** - Technical Problem (system/technical issue)
- **AM09** - Wrong Amount (incorrect payment amount received)
- **AC03** - Invalid Creditor Account (wrong beneficiary account)
- **NOOR** - No Original Transaction Reference Found (cannot trace)
- **LATE** - Late Payment (payment received after expected date)
- **NARR** - Narrative Reason (detailed explanation in text)

### Instruction Priority (InstrPrty)
- **HIGH** - High priority claim
- **NORM** - Normal priority claim
- **URGP** - Urgent priority

### Service Level (SvcLvl/Cd)
- **SEPA** - Single Euro Payments Area
- **SDVA** - Same Day Value
- **URGP** - Urgent Payment

### Missing or Incorrect Information Justification

**Boolean Indicators (true/false):**
- **MssngCdtr** - Missing creditor details
- **IncrrctCdtr** - Incorrect creditor details
- **MssngDbtr** - Missing debtor details
- **IncrrctDbtr** - Incorrect debtor details
- **IncrrctAmt** - Incorrect amount

---

## Message Examples

### Example 1: Claim Non-Receipt - Payment Not Received

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.027.001.07">
  <ClmNonRcpt>
    <Assgnmt>
      <Id>CNR-20241220-NOT-RECEIVED-001</Id>
      <Assgnr>
        <Agt>
          <FinInstnId>
            <BICFI>CREDGB2LXXX</BICFI>
            <Nm>Creditor Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>DEBTGB2LXXX</BICFI>
            <Nm>Debtor Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T11:00:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-CNR-2024-11111</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>CREDGB2LXXX</BICFI>
            <Nm>Creditor Bank - Investigation Team</Nm>
          </FinInstnId>
        </Agt>
      </Cretr>
    </Case>
    <Undrlyg>
      <OrgnlGrpInf>
        <OrgnlMsgId>PMT-20241215-ORIG-567</OrgnlMsgId>
        <OrgnlMsgNmId>pacs.008.001.08</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-15T09:00:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <TxInf>
        <OrgnlInstrId>INSTR-EXPECTED-PAYMENT</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-INVOICE-12345</OrgnlEndToEndId>
        <OrgnlTxId>TXN-NOT-RECEIVED</OrgnlTxId>
        <OrgnlUETR>987e6543-e21b-45d3-a987-654321098765</OrgnlUETR>
        <OrgnlIntrBkSttlmAmt Ccy="GBP">50000.00</OrgnlIntrBkSttlmAmt>
        <OrgnlIntrBkSttlmDt>2024-12-16</OrgnlIntrBkSttlmDt>
        <ClmNonRct>
          <DtPrcd>2024-12-20</DtPrcd>
          <ClmNonRctDtls>
            <ClmdAmt Ccy="GBP">50000.00</ClmdAmt>
            <ClmNonRctRsn>
              <Cd>NRCV</Cd>
            </ClmNonRctRsn>
            <AddtlClmNonRctInf>Creditor claims that expected payment of GBP 50,000.00 for Invoice #12345 has not been received. Payment was expected to settle on 2024-12-16 but has not appeared in creditor account GB98CRED12345678901234. Please investigate and provide status update. Payment was confirmed sent by debtor on 2024-12-15. UETR: 987e6543-e21b-45d3-a987-654321098765</AddtlClmNonRctInf>
          </ClmNonRctDtls>
        </ClmNonRct>
        <OrgnlTxRef>
          <IntrBkSttlmAmt Ccy="GBP">50000.00</IntrBkSttlmAmt>
          <IntrBkSttlmDt>2024-12-16</IntrBkSttlmDt>
          <PmtTpInf>
            <InstrPrty>HIGH</InstrPrty>
          </PmtTpInf>
          <Dbtr>
            <Nm>Corporate Debtor Ltd</Nm>
            <PstlAdr>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <IBAN>GB45DEBT30405067890123</IBAN>
            </Id>
          </DbtrAcct>
          <DbtrAgt>
            <FinInstnId>
              <BICFI>DEBTGB2LXXX</BICFI>
            </FinInstnId>
          </DbtrAgt>
          <CdtrAgt>
            <FinInstnId>
              <BICFI>CREDGB2LXXX</BICFI>
            </FinInstnId>
          </CdtrAgt>
          <Cdtr>
            <Nm>Supplier Services Ltd</Nm>
            <PstlAdr>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <IBAN>GB98CRED12345678901234</IBAN>
            </Id>
          </CdtrAcct>
          <RmtInf>
            <Ustrd>Invoice INV-12345 - PAYMENT NOT RECEIVED</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInf>
    </Undrlyg>
  </ClmNonRcpt>
</Document>
```

### Example 2: Claim Non-Receipt - Duplicate Payment

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.027.001.07">
  <ClmNonRcpt>
    <Assgnmt>
      <Id>CNR-20241220-DUPLICATE-002</Id>
      <Assgnr>
        <Agt>
          <FinInstnId>
            <BICFI>PAYGB2LXXX</BICFI>
            <Nm>Payee Bank</Nm>
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
      <CreDtTm>2024-12-20T14:30:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-CNR-DUPL-2024-22222</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>PAYGB2LXXX</BICFI>
            <Nm>Payee Bank - Exceptions</Nm>
          </FinInstnId>
        </Agt>
      </Cretr>
    </Case>
    <Undrlyg>
      <OrgnlGrpInf>
        <OrgnlMsgId>PMT-20241220-DUPL-999</OrgnlMsgId>
        <OrgnlMsgNmId>pacs.008.001.08</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-20T10:00:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <TxInf>
        <OrgnlInstrId>INSTR-DUPLICATE-SECOND</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-SALARY-DUPL</OrgnlEndToEndId>
        <OrgnlTxId>TXN-DUPLICATE-999</OrgnlTxId>
        <OrgnlIntrBkSttlmAmt Ccy="GBP">2500.00</OrgnlIntrBkSttlmAmt>
        <OrgnlIntrBkSttlmDt>2024-12-20</OrgnlIntrBkSttlmDt>
        <ClmNonRct>
          <DtPrcd>2024-12-20</DtPrcd>
          <ClmNonRctDtls>
            <ClmdAmt Ccy="GBP">2500.00</ClmdAmt>
            <ClmNonRctRsn>
              <Cd>DUPL</Cd>
            </ClmNonRctRsn>
            <AddtlClmNonRctInf>Duplicate payment claim: Same salary payment of GBP 2,500.00 received twice on 2024-12-20. First payment (E2E-SALARY-ORIGINAL) correctly received at 09:00. Second payment (E2E-SALARY-DUPL) received at 11:00 appears to be duplicate. Employee has confirmed only one salary payment was expected. Please investigate and advise on return of duplicate amount.</AddtlClmNonRctInf>
          </ClmNonRctDtls>
        </ClmNonRct>
        <OrgnlTxRef>
          <IntrBkSttlmAmt Ccy="GBP">2500.00</IntrBkSttlmAmt>
          <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
          <PmtTpInf>
            <InstrPrty>NORM</InstrPrty>
          </PmtTpInf>
          <Dbtr>
            <Nm>Employer Corporation</Nm>
            <PstlAdr>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <IBAN>GB56PAYR20304055667788</IBAN>
            </Id>
          </DbtrAcct>
          <DbtrAgt>
            <FinInstnId>
              <BICFI>PAYRGB2LXXX</BICFI>
            </FinInstnId>
          </DbtrAgt>
          <CdtrAgt>
            <FinInstnId>
              <BICFI>PAYGB2LXXX</BICFI>
            </FinInstnId>
          </CdtrAgt>
          <Cdtr>
            <Nm>Employee John Doe</Nm>
            <PstlAdr>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <IBAN>GB78PAYG12345678901234</IBAN>
            </Id>
          </CdtrAcct>
          <RmtInf>
            <Ustrd>Salary December 2024 - DUPLICATE PAYMENT</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInf>
    </Undrlyg>
  </ClmNonRcpt>
</Document>
```

### Example 3: Claim Non-Receipt - Wrong Amount

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.027.001.07">
  <ClmNonRcpt>
    <Assgnmt>
      <Id>CNR-20241220-WRONG-AMT-003</Id>
      <Assgnr>
        <Agt>
          <FinInstnId>
            <BICFI>VNDRGB2LXXX</BICFI>
            <Nm>Vendor Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>BUYRGB2LXXX</BICFI>
            <Nm>Buyer Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T16:00:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-CNR-AMOUNT-2024-33333</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>VNDRGB2LXXX</BICFI>
            <Nm>Vendor Bank</Nm>
          </FinInstnId>
        </Agt>
      </Cretr>
    </Case>
    <Undrlyg>
      <OrgnlGrpInf>
        <OrgnlMsgId>PMT-20241219-INV-888</OrgnlMsgId>
        <OrgnlMsgNmId>pacs.008.001.08</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-19T10:00:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <TxInf>
        <OrgnlInstrId>INSTR-INVOICE-888</OrgnlInstrId>
        <OrgnlEndToEndId>E2E-INV-888-WRONG-AMOUNT</OrgnlEndToEndId>
        <OrgnlTxId>TXN-WRONG-AMT-888</OrgnlTxId>
        <OrgnlIntrBkSttlmAmt Ccy="GBP">10000.00</OrgnlIntrBkSttlmAmt>
        <OrgnlIntrBkSttlmDt>2024-12-19</OrgnlIntrBkSttlmDt>
        <ClmNonRct>
          <DtPrcd>2024-12-20</DtPrcd>
          <ClmNonRctDtls>
            <ClmdAmt Ccy="GBP">2000.00</ClmdAmt>
            <ClmNonRctJstfn>
              <MssngOrIncrrctInf>
                <IncrrctAmt>true</IncrrctAmt>
              </MssngOrIncrrctInf>
            </ClmNonRctJstfn>
            <ClmNonRctRsn>
              <Cd>AM09</Cd>
            </ClmNonRctRsn>
            <AddtlClmNonRctInf>Incorrect amount received. Expected payment: GBP 12,000.00 per Invoice INV-888. Actual payment received: GBP 10,000.00. Shortfall: GBP 2,000.00. Invoice INV-888 dated 2024-12-10 clearly shows amount due of GBP 12,000.00. Vendor claims outstanding balance of GBP 2,000.00. Please investigate discrepancy and arrange payment of shortfall amount.</AddtlClmNonRctInf>
          </ClmNonRctDtls>
        </ClmNonRct>
        <OrgnlTxRef>
          <IntrBkSttlmAmt Ccy="GBP">10000.00</IntrBkSttlmAmt>
          <Amt>
            <InstdAmt Ccy="GBP">10000.00</InstdAmt>
          </Amt>
          <IntrBkSttlmDt>2024-12-19</IntrBkSttlmDt>
          <PmtTpInf>
            <InstrPrty>NORM</InstrPrty>
          </PmtTpInf>
          <Dbtr>
            <Nm>Buyer Company Ltd</Nm>
            <PstlAdr>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <IBAN>GB34BUYR40506078901234</IBAN>
            </Id>
          </DbtrAcct>
          <DbtrAgt>
            <FinInstnId>
              <BICFI>BUYRGB2LXXX</BICFI>
            </FinInstnId>
          </DbtrAgt>
          <CdtrAgt>
            <FinInstnId>
              <BICFI>VNDRGB2LXXX</BICFI>
            </FinInstnId>
          </CdtrAgt>
          <Cdtr>
            <Nm>Vendor Services Ltd</Nm>
            <PstlAdr>
              <Ctry>GB</Ctry>
            </PstlAdr>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <IBAN>GB89VNDR56789012345678</IBAN>
            </Id>
          </CdtrAcct>
          <RmtInf>
            <Ustrd>Invoice INV-888 - WRONG AMOUNT - Expected 12000.00 Received 10000.00</Ustrd>
          </RmtInf>
        </OrgnlTxRef>
      </TxInf>
    </Undrlyg>
  </ClmNonRcpt>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 72 fields in camt.027 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles payment identification, amounts, dates, party references
- Extension fields accommodate claim-non-receipt-specific information
- Boolean flags for claim justification (missing/incorrect information)
- Party entity supports assignor, assignee, case creator, claimant, debtor, creditor
- Account entity handles IBAN and non-IBAN account identifiers
- FinancialInstitution entity manages agent information including intermediaries
- ComplianceCase entity supports investigation case management and priority

**Key Extension Fields Used:**
- caseId, reopenCaseIndicator (case management)
- claimNonReceiptReasonCode, proprietaryClaimReason
- claimAdditionalInfo (free-text explanation)
- claimProceedDate (date claim processed)
- claimedAmount, claimedCurrency (amount being claimed)
- originalMessageId, originalMessageType, originalCreatedDateTime
- Missing/incorrect claim justification flags: missingCreditorClaim, incorrectCreditorClaim, missingDebtorClaim, incorrectDebtorClaim, incorrectAmountClaim
- creditorReferenceInfo (creditor's reference details)
- requestedExecutionDateTime (execution timestamp)

---

## References

- **ISO 20022 Message Definition:** camt.027.001.07 - ClaimNonReceiptV07
- **XML Schema:** camt.027.001.07.xsd
- **Related Messages:** pacs.008 (credit transfer), pacs.003 (direct debit), camt.026 (unable to apply), camt.029 (resolution), camt.056 (cancellation request), pain.001 (customer instruction)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **Claim Non-Receipt Reason Codes:** ISO 20022 External Payment Claim Non-Receipt Reason Code
- **SWIFT gpi Tracker:** Used for UETR-based payment tracking

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
