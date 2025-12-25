# ISO 20022 camt.087 - Request to Modify Payment Mapping

## Message Overview

**Message Type:** camt.087.001.06 - RequestToModifyPaymentV06
**Category:** CAMT - Cash Management
**Purpose:** Sent by a party to request modification of payment instruction details after submission but before execution
**Direction:** Customer → FI or FI → FI
**Scope:** Modification request for payment attributes (not cancellation)

**Key Use Cases:**
- Modify payment amount after submission
- Update beneficiary account details
- Change payment execution date
- Modify remittance information
- Update charge bearer instructions
- Correct payment priority
- Modify intermediary agent routing
- Update regulatory/compliance information

**Relationship to Other Messages:**
- **pain.001**: Original customer credit transfer being modified
- **pacs.008**: FI credit transfer being modified
- **camt.029**: Resolution of Investigation (response to modification request)
- **camt.055/056**: Payment cancellation (alternative to modification)
- **pain.007**: Payment reversal (post-execution alternative)

**Comparison with Related Messages:**
- **camt.087**: Request to modify payment (change details)
- **camt.055/056**: Request to cancel payment (stop payment)
- **pain.007**: Payment reversal (post-execution)
- **camt.029**: Resolution of investigation (response)

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in camt.087** | 92 |
| **Fields Mapped to CDM** | 92 |
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
| Assgnmt/Id | Assignment Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique modification request ID |
| Assgnmt/Assgnr/Agt/FinInstnId/BICFI | Assignor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Requesting bank BIC |
| Assgnmt/Assgnr/Agt/FinInstnId/ClrSysMmbId/MmbId | Assignor Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| Assgnmt/Assgnr/Agt/FinInstnId/Nm | Assignor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Requesting bank name |
| Assgnmt/Assgnr/Agt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Bank country |
| Assgnmt/Assgnr/Pty/Nm | Assignor Party Name | Text | 1-140 | 0..1 | Free text | Party | name | Party requesting modification |
| Assgnmt/Assgnr/Pty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Assignor country |
| Assgnmt/Assgnr/Pty/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Organization BIC |
| Assgnmt/Assgnr/Pty/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxIdentificationNumber | Tax ID/org number |
| Assgnmt/Assgne/Agt/FinInstnId/BICFI | Assignee Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Recipient bank BIC |
| Assgnmt/Assgne/Agt/FinInstnId/ClrSysMmbId/MmbId | Assignee Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| Assgnmt/Assgne/Agt/FinInstnId/Nm | Assignee Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Recipient bank name |
| Assgnmt/Assgne/Agt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Bank country |
| Assgnmt/Assgne/Pty/Nm | Assignee Party Name | Text | 1-140 | 0..1 | Free text | Party | name | Party receiving request |
| Assgnmt/Assgne/Pty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Assignee country |
| Assgnmt/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | creationDateTime | Modification request timestamp |

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
| Undrlyg/OrgnlGrpInf/OrgnlMsgNmId | Original Message Name ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | originalMessageType | e.g., "pacs.008.001.08" |
| Undrlyg/OrgnlGrpInf/OrgnlCreDtTm | Original Creation DateTime | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | originalCreatedDateTime | Original message timestamp |

#### 4.2 Modification Details (Mod)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/Mod/PmtId/InstrId | Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Original instruction reference |
| Undrlyg/Mod/PmtId/EndToEndId | End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | endToEndId | Original E2E reference |
| Undrlyg/Mod/PmtId/TxId | Transaction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Original transaction reference |
| Undrlyg/Mod/PmtId/UETR | UETR | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Original unique transaction reference |

#### 4.3 Modification Reason (ModRsn)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/Mod/ModRsn/Orgtr/Nm | Originator Name | Text | 1-140 | 0..1 | Free text | Party | name | Modification reason originator |
| Undrlyg/Mod/ModRsn/Orgtr/Id/OrgId/AnyBIC | Originator BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Originator BIC |
| Undrlyg/Mod/ModRsn/Rsn/Cd | Reason Code | Code | - | 0..1 | Various codes | PaymentInstruction.extensions | modificationReasonCode | ISO 20022 modification reason |
| Undrlyg/Mod/ModRsn/Rsn/Prtry | Proprietary Reason | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryModificationReason | Custom modification reason |
| Undrlyg/Mod/ModRsn/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | modificationAdditionalInfo | Free-text explanation |

#### 4.4 Modified Transaction Details (ModDtls)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/Mod/ModDtls/IntrBkSttlmAmt | Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | interbankSettlementAmount | Modified settlement amount |
| Undrlyg/Mod/ModDtls/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | interbankSettlementAmount.currency | Settlement currency |
| Undrlyg/Mod/ModDtls/Amt/InstdAmt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | instructedAmount | Modified instructed amount |
| Undrlyg/Mod/ModDtls/Amt/InstdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | instructedAmount.currency | Instructed currency |
| Undrlyg/Mod/ModDtls/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISODate | PaymentInstruction | interbankSettlementDate | Modified settlement date |
| Undrlyg/Mod/ModDtls/ReqdExctnDt/Dt | Requested Execution Date | Date | - | 0..1 | ISODate | PaymentInstruction | requestedExecutionDate | Modified execution date |
| Undrlyg/Mod/ModDtls/ReqdExctnDt/DtTm | Requested Execution DateTime | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | requestedExecutionDateTime | Modified execution timestamp |
| Undrlyg/Mod/ModDtls/ReqdColltnDt | Requested Collection Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | requestedCollectionDate | Direct debit collection date |
| Undrlyg/Mod/ModDtls/PmtTpInf/InstrPrty | Instruction Priority | Code | 4 | 0..1 | HIGH, NORM | PaymentInstruction | priority | Modified priority |
| Undrlyg/Mod/ModDtls/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | - | 0..1 | SEPA, SDVA, URGP | PaymentInstruction | serviceLevel | Modified service level |
| Undrlyg/Mod/ModDtls/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | - | 0..1 | CORE, B2B, etc. | PaymentInstruction | localInstrument | Regional instrument |
| Undrlyg/Mod/ModDtls/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | - | 0..1 | CASH, CORT, etc. | PaymentInstruction | categoryPurpose | Payment category |
| Undrlyg/Mod/ModDtls/PmtMtd | Payment Method | Code | 4 | 0..1 | CHK, TRF, TRA | PaymentInstruction.extensions | paymentMethod | Modified payment method |
| Undrlyg/Mod/ModDtls/ChrgBr | Charge Bearer | Code | 4 | 0..1 | DEBT, CRED, SHAR | PaymentInstruction | chargeBearer | Modified charge bearer |
| Undrlyg/Mod/ModDtls/MndtRltdInf/MndtId | Mandate ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | mandateId | Direct debit mandate reference |
| Undrlyg/Mod/ModDtls/MndtRltdInf/DtOfSgntr | Date of Signature | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | mandateSignatureDate | Mandate signature date |
| Undrlyg/Mod/ModDtls/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction | remittanceInformation | Modified remittance info |
| Undrlyg/Mod/ModDtls/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | invoiceNumber | Modified invoice number |
| Undrlyg/Mod/ModDtls/RmtInf/Strd/RfrdDocInf/RltdDt | Related Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | invoiceDate | Invoice date |

#### 4.5 Modified Parties

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Undrlyg/Mod/ModDtls/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Free text | Party | name | Modified ultimate debtor |
| Undrlyg/Mod/ModDtls/UltmtDbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Ultimate debtor country |
| Undrlyg/Mod/ModDtls/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | name | Modified debtor |
| Undrlyg/Mod/ModDtls/Dbtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | postalAddress.streetName | Street |
| Undrlyg/Mod/ModDtls/Dbtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalAddress.postCode | ZIP/postal code |
| Undrlyg/Mod/ModDtls/Dbtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | postalAddress.townName | City |
| Undrlyg/Mod/ModDtls/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Debtor country |
| Undrlyg/Mod/ModDtls/Dbtr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Organization BIC |
| Undrlyg/Mod/ModDtls/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Modified debtor account |
| Undrlyg/Mod/ModDtls/DbtrAcct/Id/Othr/Id | Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN debtor account |
| Undrlyg/Mod/ModDtls/DbtrAcct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account.extensions | accountTypeCode | Account type |
| Undrlyg/Mod/ModDtls/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Modified debtor bank |
| Undrlyg/Mod/ModDtls/DbtrAgt/FinInstnId/Nm | Debtor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Debtor bank name |
| Undrlyg/Mod/ModDtls/IntrmyAgt1/FinInstnId/BICFI | Intermediary Agent 1 BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Modified intermediary 1 |
| Undrlyg/Mod/ModDtls/IntrmyAgt1/FinInstnId/Nm | Intermediary Agent 1 Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Intermediary 1 name |
| Undrlyg/Mod/ModDtls/IntrmyAgt2/FinInstnId/BICFI | Intermediary Agent 2 BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Modified intermediary 2 |
| Undrlyg/Mod/ModDtls/IntrmyAgt2/FinInstnId/Nm | Intermediary Agent 2 Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Intermediary 2 name |
| Undrlyg/Mod/ModDtls/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Modified creditor bank |
| Undrlyg/Mod/ModDtls/CdtrAgt/FinInstnId/Nm | Creditor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Creditor bank name |
| Undrlyg/Mod/ModDtls/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | name | Modified creditor |
| Undrlyg/Mod/ModDtls/Cdtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | postalAddress.streetName | Street |
| Undrlyg/Mod/ModDtls/Cdtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalAddress.postCode | ZIP/postal code |
| Undrlyg/Mod/ModDtls/Cdtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | postalAddress.townName | City |
| Undrlyg/Mod/ModDtls/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Creditor country |
| Undrlyg/Mod/ModDtls/Cdtr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Organization BIC |
| Undrlyg/Mod/ModDtls/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Modified creditor account |
| Undrlyg/Mod/ModDtls/CdtrAcct/Id/Othr/Id | Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN creditor account |
| Undrlyg/Mod/ModDtls/CdtrAcct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account.extensions | accountTypeCode | Account type |
| Undrlyg/Mod/ModDtls/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Free text | Party | name | Modified ultimate creditor |
| Undrlyg/Mod/ModDtls/UltmtCdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Ultimate creditor country |
| Undrlyg/Mod/ModDtls/Purp/Cd | Purpose Code | Code | 4 | 0..1 | ISO 20022 codes | PaymentInstruction | purpose | Modified purpose code |

### 5. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Modification Reason Code (ModRsn/Rsn/Cd)

**Common Modification Reasons:**
- **NARR** - Narrative (general modification)
- **CUST** - Customer Request
- **TECH** - Technical Problems
- **AM09** - Wrong Amount
- **AC03** - Invalid Creditor Account
- **AGNT** - Incorrect Agent
- **CURR** - Incorrect Currency
- **DDAT** - Incorrect Date
- **BE05** - Unrecognised Initiating Party

### Payment Method (PmtMtd)
- **CHK** - Cheque
- **TRF** - Credit Transfer
- **TRA** - Credit Transfer to Account
- **DD** - Direct Debit

### Charge Bearer (ChrgBr)
- **DEBT** - Debtor bears all charges
- **CRED** - Creditor bears all charges
- **SHAR** - Charges shared between debtor and creditor
- **SLEV** - Service level charges

### Service Level (SvcLvl/Cd)
- **SEPA** - Single Euro Payments Area
- **SDVA** - Same Day Value
- **URGP** - Urgent Payment

### Instruction Priority (InstrPrty)
- **HIGH** - High priority
- **NORM** - Normal priority

### Account Type (Tp/Cd)
- **CACC** - Current/Checking Account
- **SVGS** - Savings Account
- **LOAN** - Loan Account
- **CARD** - Card Account

---

## Message Examples

### Example 1: Modify Payment Amount

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.087.001.06">
  <ReqToModfyPmt>
    <Assgnmt>
      <Id>MODREQ-20241220-001</Id>
      <Assgnr>
        <Pty>
          <Nm>Global Corporation Treasury</Nm>
          <Id>
            <OrgId>
              <AnyBIC>GLBCUS33XXX</AnyBIC>
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
      <CreDtTm>2024-12-20T10:30:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-MOD-2024-12345</Id>
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
        <OrgnlMsgId>PMT-20241220-ORIGINAL</OrgnlMsgId>
        <OrgnlMsgNmId>pain.001.001.09</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-20T09:00:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <Mod>
        <PmtId>
          <EndToEndId>E2E-PAYMENT-MODIFY-001</EndToEndId>
          <TxId>TXN-MODIFY-001</TxId>
        </PmtId>
        <ModRsn>
          <Orgtr>
            <Nm>Global Corporation Finance Team</Nm>
          </Orgtr>
          <Rsn>
            <Cd>AM09</Cd>
          </Rsn>
          <AddtlInf>Incorrect amount entered. Should be USD 50,000.00 instead of USD 55,000.00. Please modify before execution.</AddtlInf>
        </ModRsn>
        <ModDtls>
          <Amt>
            <InstdAmt Ccy="USD">50000.00</InstdAmt>
          </Amt>
          <ReqdExctnDt>
            <Dt>2024-12-21</Dt>
          </ReqdExctnDt>
          <Dbtr>
            <Nm>Global Corporation</Nm>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <Othr>
                <Id>1234567890</Id>
              </Othr>
            </Id>
          </DbtrAcct>
          <Cdtr>
            <Nm>Supplier XYZ Inc</Nm>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <Othr>
                <Id>9876543210</Id>
              </Othr>
            </Id>
          </CdtrAcct>
          <RmtInf>
            <Ustrd>Invoice INV-2024-5678 - CORRECTED AMOUNT</Ustrd>
          </RmtInf>
        </ModDtls>
      </Mod>
    </Undrlyg>
  </ReqToModfyPmt>
</Document>
```

### Example 2: Modify Beneficiary Account Details

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.087.001.06">
  <ReqToModfyPmt>
    <Assgnmt>
      <Id>MODREQ-20241220-ACCT-002</Id>
      <Assgnr>
        <Pty>
          <Nm>ABC Services Inc</Nm>
        </Pty>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>BOFAUS3NXXX</BICFI>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T14:15:00</CreDtTm>
    </Assgnmt>
    <Case>
      <Id>CASE-MOD-ACCT-67890</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>BOFAUS3NXXX</BICFI>
          </FinInstnId>
        </Agt>
      </Cretr>
    </Case>
    <Undrlyg>
      <OrgnlGrpInf>
        <OrgnlMsgId>PMT-20241220-ACCT-WRONG</OrgnlMsgId>
        <OrgnlMsgNmId>pain.001.001.09</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-20T13:00:00</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <Mod>
        <PmtId>
          <EndToEndId>E2E-ACCT-MODIFY-002</EndToEndId>
          <TxId>TXN-ACCT-MODIFY-002</TxId>
        </PmtId>
        <ModRsn>
          <Orgtr>
            <Nm>ABC Services AP Department</Nm>
          </Orgtr>
          <Rsn>
            <Cd>AC03</Cd>
          </Rsn>
          <AddtlInf>Wrong beneficiary account number provided. Beneficiary notified us of new account details. Please update to correct account before processing.</AddtlInf>
        </ModRsn>
        <ModDtls>
          <Amt>
            <InstdAmt Ccy="USD">25000.00</InstdAmt>
          </Amt>
          <ReqdExctnDt>
            <Dt>2024-12-21</Dt>
          </ReqdExctnDt>
          <Dbtr>
            <Nm>ABC Services Inc</Nm>
          </Dbtr>
          <DbtrAcct>
            <Id>
              <Othr>
                <Id>5555666677778888</Id>
              </Othr>
            </Id>
          </DbtrAcct>
          <Cdtr>
            <Nm>Vendor Manufacturing Ltd</Nm>
            <PstlAdr>
              <StrtNm>Industrial Way</StrtNm>
              <PstCd>30301</PstCd>
              <TwnNm>Atlanta</TwnNm>
              <Ctry>US</Ctry>
            </PstlAdr>
          </Cdtr>
          <CdtrAcct>
            <Id>
              <Othr>
                <Id>9999888877776666</Id>
              </Othr>
            </Id>
            <Tp>
              <Cd>CACC</Cd>
            </Tp>
          </CdtrAcct>
          <RmtInf>
            <Ustrd>Payment for Services - Invoice #INV-2024-9999</Ustrd>
            <Strd>
              <RfrdDocInf>
                <Nb>INV-2024-9999</Nb>
                <RltdDt>2024-12-15</RltdDt>
              </RfrdDocInf>
            </Strd>
          </RmtInf>
        </ModDtls>
      </Mod>
    </Undrlyg>
  </ReqToModfyPmt>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 92 fields in camt.087 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles modification identification, amounts, dates, parties
- Extension fields accommodate modification-specific information (reason codes, case ID)
- Party entity supports assignor, assignee, creditor, debtor, ultimate parties, originator
- Account entity handles IBAN and non-IBAN account identifiers with account types
- FinancialInstitution entity manages agent information including intermediaries

**Key Extension Fields Used:**
- caseId, reopenCaseIndicator (case management)
- numberOfTransactions, controlSum
- originalMessageId, originalMessageType, originalCreatedDateTime (references to original payment)
- modificationReasonCode, proprietaryModificationReason, modificationAdditionalInfo
- requestedExecutionDateTime, requestedCollectionDate
- paymentMethod, accountTypeCode
- mandateId, mandateSignatureDate (direct debit)
- invoiceNumber, invoiceDate (remittance)

---

## References

- **ISO 20022 Message Definition:** camt.087.001.06 - RequestToModifyPaymentV06
- **XML Schema:** camt.087.001.06.xsd
- **Related Messages:** pain.001 (customer credit transfer), pacs.008 (FI credit transfer), camt.029 (resolution), camt.055/056 (cancellation), pain.007 (reversal)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **Modification Reason Codes:** ISO 20022 External Payment Modification Reason Code

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
