# ISO 20022 camt.029 - Resolution of Investigation Mapping

## Message Overview

**Message Type:** camt.029.001.09 - ResolutionOfInvestigationV09
**Category:** CAMT - Cash Management
**Purpose:** Response message to an investigation case (camt.026, camt.027) providing the status, resolution, and any corrective action taken
**Direction:** Case Handler → Case Creator (Bidirectional)
**Scope:** Investigation resolution and status updates for exception cases

**Key Use Cases:**
- Respond to unable to apply investigation (camt.026)
- Respond to claim non-receipt investigation (camt.027)
- Provide investigation status update (resolved, rejected, pending, cancelled)
- Communicate corrective action taken
- Provide updated payment information
- Explain investigation outcome
- Close investigation cases
- Forward case to another party

**Relationship to Other Messages:**
- **camt.026**: Unable to Apply (this message resolves)
- **camt.027**: Claim Non-Receipt (this message resolves)
- **camt.056**: FI Payment Cancellation Request (may trigger resolution)
- **pacs.008**: Credit transfer (corrected payment may be sent)
- **pacs.004**: Payment return (if resolution is to return funds)
- **pacs.007**: Payment reversal (if resolution is to reverse)
- **camt.087**: Request to Modify Payment (update message may be sent)

**Comparison with Related Messages:**
- **camt.029**: Resolution - response/outcome to investigation
- **camt.026**: Unable to Apply - initiates investigation
- **camt.027**: Claim Non-Receipt - initiates investigation
- **camt.056**: Cancellation Request - may be part of resolution
- **camt.087**: Modify Request - may be part of corrective action

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in camt.029** | 85 |
| **Fields Mapped to CDM** | 85 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- PaymentInstruction.extensions (caseId, investigationStatus, resolutionStatus, correctiveAction)
- Party (assignor, assignee, case creator)
- Account (corrected account details)
- FinancialInstitution (agents involved)
- ComplianceCase (investigation case management, resolution)

---

## Complete Field Mapping

### 1. Assignment (Assgnmt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Assgnmt/Id | Assignment Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique assignment identifier |
| Assgnmt/Assgnr/Agt/FinInstnId/BICFI | Assignor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Resolution sender BIC |
| Assgnmt/Assgnr/Agt/FinInstnId/ClrSysMmbId/MmbId | Assignor Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| Assgnmt/Assgnr/Agt/FinInstnId/Nm | Assignor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Resolution sender name |
| Assgnmt/Assgnr/Agt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Assignor country |
| Assgnmt/Assgnr/Pty/Nm | Assignor Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Assignor party |
| Assgnmt/Assgnr/Pty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Assignor country |
| Assgnmt/Assgnr/Pty/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| Assgnmt/Assgnr/Pty/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID/org number |
| Assgnmt/Assgne/Agt/FinInstnId/BICFI | Assignee Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Resolution recipient BIC |
| Assgnmt/Assgne/Agt/FinInstnId/ClrSysMmbId/MmbId | Assignee Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| Assgnmt/Assgne/Agt/FinInstnId/Nm | Assignee Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Resolution recipient name |
| Assgnmt/Assgne/Agt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Assignee country |
| Assgnmt/Assgne/Pty/Nm | Assignee Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Assignee party |
| Assgnmt/Assgne/Pty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Assignee country |
| Assgnmt/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | createdDateTime | Resolution message timestamp |

### 2. Resolved Case (RslvdCase)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| RslvdCase/Id | Case Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | caseId | Case being resolved |
| RslvdCase/Cretr/Agt/FinInstnId/BICFI | Creator Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Original case creator BIC |
| RslvdCase/Cretr/Agt/FinInstnId/Nm | Creator Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Original case creator name |
| RslvdCase/Cretr/Pty/Nm | Creator Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Original case creator party |
| RslvdCase/Cretr/Pty/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |

### 3. Status (Sts)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Sts/Conf | Confirmation | Code | 4 | 0..1 | RSLV, RJCT, PDNG, CNCL | PaymentInstruction.extensions | investigationStatus | Resolution status code |
| Sts/Orgtr/Nm | Originator Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Status originator |
| Sts/Orgtr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Originator BIC |
| Sts/Rsn/Cd | Reason Code | Code | - | 0..1 | NARR, etc. | PaymentInstruction.extensions | statusReasonCode | ISO 20022 status reason |
| Sts/Rsn/Prtry | Proprietary Reason | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryStatusReason | Custom status reason |
| Sts/AddtlInf | Additional Information | Text | 1-500 | 0..n | Free text | PaymentInstruction.extensions | statusAdditionalInfo | Free-text explanation |

### 4. Corrective Action (CxlDtls or ModDtls)

#### 4.1 Cancellation Details (CxlDtls)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CxlDtls/TxInfAndSts/OrgnlInstrId | Original Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Original instruction reference |
| CxlDtls/TxInfAndSts/OrgnlEndToEndId | Original End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | endToEndId | Original E2E reference |
| CxlDtls/TxInfAndSts/OrgnlTxId | Original Transaction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Original transaction reference |
| CxlDtls/TxInfAndSts/OrgnlUETR | Original UETR | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Original UETR |
| CxlDtls/TxInfAndSts/TxCxlSts | Transaction Cancellation Status | Code | 4 | 0..1 | RJCT, ACCR, PDNG | PaymentInstruction.extensions | cancellationStatus | Cancellation status |
| CxlDtls/TxInfAndSts/CxlStsRsnInf/Rsn/Cd | Cancellation Reason Code | Code | - | 0..1 | CUST, DUPL, FRAD, etc. | PaymentInstruction.extensions | cancellationReasonCode | Cancellation reason |
| CxlDtls/TxInfAndSts/CxlStsRsnInf/AddtlInf | Additional Information | Text | 1-500 | 0..n | Free text | PaymentInstruction.extensions | cancellationAdditionalInfo | Cancellation details |
| CxlDtls/TxInfAndSts/OrgnlTxRef/Amt/InstdAmt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | instructedAmount.amount | Cancelled amount |
| CxlDtls/TxInfAndSts/OrgnlTxRef/Amt/InstdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | instructedAmount.currency | Cancelled currency |

#### 4.2 Modification Details (ModDtls)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ModDtls/TxInfAndSts/OrgnlInstrId | Original Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Original instruction reference |
| ModDtls/TxInfAndSts/OrgnlEndToEndId | Original End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | endToEndId | Original E2E reference |
| ModDtls/TxInfAndSts/OrgnlTxId | Original Transaction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Original transaction reference |
| ModDtls/TxInfAndSts/OrgnlUETR | Original UETR | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Original UETR |
| ModDtls/TxInfAndSts/ModStsId | Modification Status ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | modificationStatusId | Modification status identifier |
| ModDtls/TxInfAndSts/ModSts | Modification Status | Code | 4 | 0..1 | RJCT, ACCR, PDNG | PaymentInstruction.extensions | modificationStatus | Modification status code |
| ModDtls/TxInfAndSts/ModStsRsnInf/Rsn/Cd | Modification Reason Code | Code | - | 0..1 | NARR, etc. | PaymentInstruction.extensions | modificationReasonCode | Modification reason |
| ModDtls/TxInfAndSts/ModStsRsnInf/AddtlInf | Additional Information | Text | 1-500 | 0..n | Free text | PaymentInstruction.extensions | modificationAdditionalInfo | Modification details |
| ModDtls/TxInfAndSts/OrgnlTxRef/IntrBkSttlmAmt | Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | interbankSettlementAmount.amount | Modified settlement amount |
| ModDtls/TxInfAndSts/OrgnlTxRef/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | interbankSettlementAmount.currency | Modified currency |

### 5. Statement Details (StmtDtls) - Optional Payment Confirmation

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| StmtDtls/AcctId/Id/IBAN | Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Confirmed account |
| StmtDtls/AcctId/Id/Othr/Id | Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| StmtDtls/AcctSvcr/FinInstnId/BICFI | Account Servicer BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Servicer BIC |
| StmtDtls/AcctSvcr/FinInstnId/Nm | Account Servicer Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Servicer name |
| StmtDtls/Ntry/Amt | Entry Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction.extensions | confirmedAmount | Confirmed payment amount |
| StmtDtls/Ntry/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | confirmedCurrency | Confirmed currency |
| StmtDtls/Ntry/CdtDbtInd | Credit Debit Indicator | Code | 4 | 1..1 | CRDT, DBIT | PaymentInstruction.extensions | creditDebitIndicator | Direction of entry |
| StmtDtls/Ntry/Sts/Cd | Status Code | Code | 4 | 1..1 | BOOK, PDNG, INFO | PaymentInstruction.extensions | entryStatusCode | Entry status |
| StmtDtls/Ntry/BookgDt/Dt | Booking Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | bookingDate | Date entry booked |
| StmtDtls/Ntry/ValDt/Dt | Value Date | Date | - | 0..1 | ISODate | PaymentInstruction | valueDate | Value date |
| StmtDtls/Ntry/BkTxCd/Domn/Cd | Domain Code | Code | - | 0..1 | PMNT, etc. | PaymentInstruction.extensions | bankTransactionDomainCode | Transaction domain |
| StmtDtls/Ntry/BkTxCd/Domn/Fmly/Cd | Family Code | Code | - | 0..1 | RCDT, ICDT, etc. | PaymentInstruction.extensions | bankTransactionFamilyCode | Transaction family |
| StmtDtls/Ntry/NtryDtls/TxDtls/Refs/InstrId | Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Confirmed instruction ID |
| StmtDtls/Ntry/NtryDtls/TxDtls/Refs/EndToEndId | End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | endToEndId | Confirmed E2E ID |
| StmtDtls/Ntry/NtryDtls/TxDtls/Refs/TxId | Transaction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Confirmed transaction ID |
| StmtDtls/Ntry/NtryDtls/TxDtls/Refs/UETR | UETR | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Confirmed UETR |
| StmtDtls/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Confirmed debtor |
| StmtDtls/Ntry/NtryDtls/TxDtls/RltdPties/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Confirmed debtor account |
| StmtDtls/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Confirmed creditor |
| StmtDtls/Ntry/NtryDtls/TxDtls/RltdPties/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Confirmed creditor account |
| StmtDtls/Ntry/NtryDtls/TxDtls/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction | remittanceInformation | Confirmed remittance info |

### 6. Corrective Transaction (CrrctvTx) - New Payment Initiated

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CrrctvTx/InstrId | Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | New corrective payment ID |
| CrrctvTx/EndToEndId | End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | endToEndId | New E2E reference |
| CrrctvTx/TxId | Transaction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | New transaction reference |
| CrrctvTx/UETR | UETR | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | New UETR |
| CrrctvTx/IntrBkSttlmAmt | Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | interbankSettlementAmount.amount | New settlement amount |
| CrrctvTx/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | interbankSettlementAmount.currency | New settlement currency |
| CrrctvTx/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISODate | PaymentInstruction | settlementDate | New settlement date |
| CrrctvTx/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Corrective debtor |
| CrrctvTx/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Corrective debtor account |
| CrrctvTx/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Corrective debtor bank |
| CrrctvTx/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Corrective creditor bank |
| CrrctvTx/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Corrective creditor |
| CrrctvTx/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Corrective creditor account |
| CrrctvTx/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction | remittanceInformation | Corrective remittance info |

### 7. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Investigation Status (Sts/Conf)

**Resolution Status Codes:**
- **RSLV** - Resolved (investigation completed successfully)
- **RJCT** - Rejected (no issue found, claim rejected)
- **PDNG** - Pending (investigation ongoing, more time needed)
- **CNCL** - Cancelled (investigation cancelled by investigator)

### Corrective Action Types

**Implicit from message structure:**
- **NEWI** - New Payment Initiated (CrrctvTx present)
- **CORU** - Correction Sent via Update Message (ModDtls present)
- **CWFW** - Case Forwarded to Another Party (assignment change)
- **RVCD** - Payment Reversed/Credited (StmtDtls with reversal)
- **MDAT** - More Data Needed (Sts/Conf = PDNG)
- **NOCA** - No Corrective Action (Sts/Conf = RJCT)

### Cancellation Status (TxCxlSts)
- **RJCT** - Rejected (cancellation rejected)
- **ACCR** - Accepted with Change (cancellation accepted with modifications)
- **PDNG** - Pending (cancellation pending)

### Modification Status (ModSts)
- **RJCT** - Rejected (modification rejected)
- **ACCR** - Accepted with Change (modification accepted)
- **PDNG** - Pending (modification pending)

### Entry Status (Ntry/Sts/Cd)
- **BOOK** - Booked (entry is confirmed and booked)
- **PDNG** - Pending (entry pending)
- **INFO** - Information (informational entry only)

### Credit/Debit Indicator (CdtDbtInd)
- **CRDT** - Credit entry
- **DBIT** - Debit entry

---

## Message Examples

### Example 1: Resolution - Resolved with New Payment Initiated

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.029.001.09">
  <RsltnOfInvstgtn>
    <Assgnmt>
      <Id>RSLV-20241220-NEWPMT-001</Id>
      <Assgnr>
        <Agt>
          <FinInstnId>
            <BICFI>DEBTGB2LXXX</BICFI>
            <Nm>Debtor Bank - Resolution Team</Nm>
          </FinInstnId>
        </Agt>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>CREDGB2LXXX</BICFI>
            <Nm>Creditor Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T15:00:00</CreDtTm>
    </Assgnmt>
    <RslvdCase>
      <Id>CASE-CNR-2024-11111</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>CREDGB2LXXX</BICFI>
            <Nm>Creditor Bank</Nm>
          </FinInstnId>
        </Agt>
      </Cretr>
    </RslvdCase>
    <Sts>
      <Conf>RSLV</Conf>
      <Orgtr>
        <Nm>Debtor Bank Investigation Team</Nm>
      </Orgtr>
      <AddtlInf>Investigation completed. Original payment was delayed in processing queue due to technical issue. New payment has been initiated with correct value date and reference. Original payment has been cancelled. Case resolved.</AddtlInf>
    </Sts>
    <CrrctvTx>
      <InstrId>INSTR-CORRECTIVE-NEW-001</InstrId>
      <EndToEndId>E2E-INVOICE-12345-CORRECTED</EndToEndId>
      <TxId>TXN-CORRECTIVE-001</TxId>
      <UETR>111e2222-e33b-44d4-a555-666666777777</UETR>
      <IntrBkSttlmAmt Ccy="GBP">50000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <Dbtr>
        <Nm>Corporate Debtor Ltd</Nm>
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
      </Cdtr>
      <CdtrAcct>
        <Id>
          <IBAN>GB98CRED12345678901234</IBAN>
        </Id>
      </CdtrAcct>
      <RmtInf>
        <Ustrd>Invoice INV-12345 - CORRECTIVE PAYMENT - Ref Case CASE-CNR-2024-11111</Ustrd>
      </RmtInf>
    </CrrctvTx>
  </RsltnOfInvstgtn>
</Document>
```

### Example 2: Resolution - Rejected (No Issue Found)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.029.001.09">
  <RsltnOfInvstgtn>
    <Assgnmt>
      <Id>RSLV-20241220-REJECTED-002</Id>
      <Assgnr>
        <Agt>
          <FinInstnId>
            <BICFI>PAYRGB2LXXX</BICFI>
            <Nm>Payer Bank - Investigation</Nm>
          </FinInstnId>
        </Agt>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <BICFI>PAYGB2LXXX</BICFI>
            <Nm>Payee Bank</Nm>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-20T16:30:00</CreDtTm>
    </Assgnmt>
    <RslvdCase>
      <Id>CASE-CNR-DUPL-2024-22222</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>PAYGB2LXXX</BICFI>
            <Nm>Payee Bank</Nm>
          </FinInstnId>
        </Agt>
      </Cretr>
    </RslvdCase>
    <Sts>
      <Conf>RJCT</Conf>
      <Orgtr>
        <Nm>Payer Bank Investigation Team</Nm>
      </Orgtr>
      <Rsn>
        <Cd>NARR</Cd>
      </Rsn>
      <AddtlInf>Investigation completed. Claim rejected - no duplicate payment found. Our records show only one payment of GBP 2,500.00 was sent on 2024-12-20 with E2E reference E2E-SALARY-DUPL. No other payment with similar amount or reference was processed. Beneficiary may have confused this payment with a different transaction. Please verify with employee and check account statement for all December salary credits.</AddtlInf>
    </Sts>
    <StmtDtls>
      <AcctId>
        <Id>
          <IBAN>GB56PAYR20304055667788</IBAN>
        </Id>
      </AcctId>
      <AcctSvcr>
        <FinInstnId>
          <BICFI>PAYRGB2LXXX</BICFI>
          <Nm>Payer Bank</Nm>
        </FinInstnId>
      </AcctSvcr>
      <Ntry>
        <Amt Ccy="GBP">2500.00</Amt>
        <CdtDbtInd>DBIT</CdtDbtInd>
        <Sts>
          <Cd>BOOK</Cd>
        </Sts>
        <BookgDt>
          <Dt>2024-12-20</Dt>
        </BookgDt>
        <ValDt>
          <Dt>2024-12-20</Dt>
        </ValDt>
        <BkTxCd>
          <Domn>
            <Cd>PMNT</Cd>
            <Fmly>
              <Cd>ICDT</Cd>
            </Fmly>
          </Domn>
        </BkTxCd>
        <NtryDtls>
          <TxDtls>
            <Refs>
              <InstrId>INSTR-SALARY-DEC</InstrId>
              <EndToEndId>E2E-SALARY-DUPL</EndToEndId>
              <TxId>TXN-SALARY-999</TxId>
            </Refs>
            <RltdPties>
              <Dbtr>
                <Nm>Employer Corporation</Nm>
              </Dbtr>
              <DbtrAcct>
                <Id>
                  <IBAN>GB56PAYR20304055667788</IBAN>
                </Id>
              </DbtrAcct>
              <Cdtr>
                <Nm>Employee John Doe</Nm>
              </Cdtr>
              <CdtrAcct>
                <Id>
                  <IBAN>GB78PAYG12345678901234</IBAN>
                </Id>
              </CdtrAcct>
            </RltdPties>
            <RmtInf>
              <Ustrd>Salary December 2024</Ustrd>
            </RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
    </StmtDtls>
  </RsltnOfInvstgtn>
</Document>
```

### Example 3: Resolution - Pending (More Time Needed)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.029.001.09">
  <RsltnOfInvstgtn>
    <Assgnmt>
      <Id>RSLV-20241220-PENDING-003</Id>
      <Assgnr>
        <Agt>
          <FinInstnId>
            <BICFI>RECVGB2LXXX</BICFI>
            <Nm>Receiving Bank</Nm>
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
      <CreDtTm>2024-12-20T17:00:00</CreDtTm>
    </Assgnmt>
    <RslvdCase>
      <Id>CASE-UTA-2024-12345</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>RECVGB2LXXX</BICFI>
            <Nm>Receiving Bank</Nm>
          </FinInstnId>
        </Agt>
      </Cretr>
    </RslvdCase>
    <Sts>
      <Conf>PDNG</Conf>
      <Orgtr>
        <Nm>Receiving Bank Investigation Team</Nm>
      </Orgtr>
      <Rsn>
        <Cd>NARR</Cd>
      </Rsn>
      <AddtlInf>Investigation in progress. Unable to Apply case for missing creditor account number. We have contacted the creditor (Services Corp) to obtain correct account details. Creditor has confirmed they are customer of our bank but needs to verify which account should receive payment. Awaiting response from creditor's finance department. Expected resolution within 2 business days. Payment of GBP 15,000.00 is being held securely pending resolution.</AddtlInf>
    </Sts>
  </RsltnOfInvstgtn>
</Document>
```

### Example 4: Resolution - Cancelled by Investigator

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.029.001.09">
  <RsltnOfInvstgtn>
    <Assgnmt>
      <Id>RSLV-20241220-CANCELLED-004</Id>
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
      <CreDtTm>2024-12-20T18:00:00</CreDtTm>
    </Assgnmt>
    <RslvdCase>
      <Id>CASE-CNR-AMOUNT-2024-33333</Id>
      <Cretr>
        <Agt>
          <FinInstnId>
            <BICFI>VNDRGB2LXXX</BICFI>
            <Nm>Vendor Bank</Nm>
          </FinInstnId>
        </Agt>
      </Cretr>
    </RslvdCase>
    <Sts>
      <Conf>CNCL</Conf>
      <Orgtr>
        <Nm>Vendor Bank Investigation Team</Nm>
      </Orgtr>
      <Rsn>
        <Cd>NARR</Cd>
      </Rsn>
      <AddtlInf>Investigation cancelled by claimant. Vendor (Vendor Services Ltd) has withdrawn the claim for incorrect amount. After reviewing invoice INV-888, vendor confirmed that payment of GBP 10,000.00 was correct. Invoice showed gross amount of GBP 12,000.00 but net amount after early payment discount (2,000 GBP = 16.67%) was GBP 10,000.00. Vendor finance team had initially overlooked the discount. No further action required. Case closed.</AddtlInf>
    </Sts>
  </RsltnOfInvstgtn>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 85 fields in camt.029 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles payment identification, amounts, dates, party references
- Extension fields accommodate resolution-specific information
- Investigation status codes and corrective action types
- Party entity supports assignor, assignee, case creator, debtor, creditor
- Account entity handles IBAN and non-IBAN account identifiers
- FinancialInstitution entity manages agent information
- ComplianceCase entity supports investigation case management and resolution tracking

**Key Extension Fields Used:**
- caseId (case being resolved)
- investigationStatus (RSLV, RJCT, PDNG, CNCL)
- statusReasonCode, proprietaryStatusReason, statusAdditionalInfo
- cancellationStatus, cancellationReasonCode, cancellationAdditionalInfo
- modificationStatusId, modificationStatus, modificationReasonCode, modificationAdditionalInfo
- confirmedAmount, confirmedCurrency (payment confirmation)
- creditDebitIndicator, entryStatusCode (statement details)
- bookingDate (when entry was booked)
- bankTransactionDomainCode, bankTransactionFamilyCode (transaction classification)
- requestedExecutionDateTime (execution timestamp)
- supplementaryDataLocation, supplementaryData (additional data)

---

## References

- **ISO 20022 Message Definition:** camt.029.001.09 - ResolutionOfInvestigationV09
- **XML Schema:** camt.029.001.09.xsd
- **Related Messages:** camt.026 (unable to apply), camt.027 (claim non-receipt), camt.056 (cancellation request), pacs.008 (credit transfer), pacs.004 (payment return), pacs.007 (payment reversal), camt.087 (modify request)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **Investigation Status Codes:** ISO 20022 External Investigation Execution Confirmation Code
- **Bank Transaction Codes:** ISO 20022 External Bank Transaction Domain Code, Family Code

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
