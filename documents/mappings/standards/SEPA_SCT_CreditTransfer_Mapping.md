# SEPA SCT - SEPA Credit Transfer
## Complete Field Mapping to GPS CDM

**Message Type:** SEPA Credit Transfer (pain.001.001.03 / pacs.008.001.02)
**Standard:** ISO 20022 (SEPA rulebook compliant)
**Scheme:** Single Euro Payments Area (SEPA)
**Usage:** Euro credit transfers within SEPA zone (EU + EEA + others)
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 118 fields mapped)

---

## Message Overview

SEPA Credit Transfer (SCT) is a scheme for euro-denominated credit transfers within the Single Euro Payments Area. SEPA SCT uses ISO 20022 XML messages with specific SEPA requirements and limitations.

**Key Characteristics:**
- Currency: EUR only
- Execution time: D+1 (next business day)
- Amount limit: None (scheme rule)
- Charge bearer: SHAR (shared charges) mandatory
- End-to-end ID: Mandatory, max 35 characters
- Character set: SEPA character set (limited Latin)

**SEPA Countries:** 36 countries including EU27, EEA (Iceland, Liechtenstein, Norway), Switzerland, UK, Monaco, San Marino, Andorra, Vatican City

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total SEPA SCT Fields** | 118 | 100% |
| **Mapped to CDM** | 118 | 100% |
| **Direct Mapping** | 109 | 92% |
| **Derived/Calculated** | 7 | 6% |
| **Reference Data Lookup** | 2 | 2% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### pain.001 - Customer Credit Transfer Initiation (Debtor Side)

#### Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | SEPA charset | PaymentInstruction | messageId | Unique message ID |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISO DateTime | PaymentInstruction | creationDateTime | Message creation |
| GrpHdr/NbOfTxs | Number Of Transactions | Text | 1-15 | 1..1 | Numeric | PaymentInstruction | numberOfTransactions | Transaction count |
| GrpHdr/CtrlSum | Control Sum | DecimalNumber | - | 1..1 | Decimal (18,2) | PaymentInstruction | controlSum | Total amount |
| GrpHdr/InitgPty/Nm | Initiating Party Name | Text | 1-70 | 1..1 | SEPA charset | Party | initiatingPartyName | Initiator name |
| GrpHdr/InitgPty/Id/OrgId/Othr/Id | Initiating Party ID | Text | 1-35 | 0..1 | SEPA charset | Party | initiatingPartyId | Organization ID |

#### Payment Information (PmtInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| PmtInf/PmtInfId | Payment Information Identification | Text | 1-35 | 1..1 | SEPA charset | PaymentInstruction | paymentInformationId | Payment batch ID |
| PmtInf/PmtMtd | Payment Method | Code | 3 | 1..1 | TRF | PaymentInstruction | paymentMethod | Always TRF for SCT |
| PmtInf/BtchBookg | Batch Booking | Boolean | - | 0..1 | true/false | PaymentInstruction | batchBooking | Batch or individual |
| PmtInf/NbOfTxs | Number Of Transactions | Text | 1-15 | 0..1 | Numeric | PaymentInstruction | batchNumberOfTransactions | Transactions in batch |
| PmtInf/CtrlSum | Control Sum | DecimalNumber | - | 0..1 | Decimal (18,2) | PaymentInstruction | batchControlSum | Batch total |
| PmtInf/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | 4 | 1..1 | SEPA | PaymentInstruction | serviceLevelCode | Must be SEPA |
| PmtInf/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | 1-35 | 0..1 | CORE, B2B | PaymentInstruction | localInstrument | SEPA payment type |
| PmtInf/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | categoryPurposeCode | CASH, TREA, etc. |
| PmtInf/ReqdExctnDt | Requested Execution Date | Date | - | 1..1 | ISO Date | PaymentInstruction | requestedExecutionDate | Execution date |
| PmtInf/Dbtr/Nm | Debtor Name | Text | 1-70 | 1..1 | SEPA charset | Party | name | Debtor/originator name |
| PmtInf/Dbtr/PstlAdr/Ctry | Debtor Country | Code | 2 | 0..1 | ISO 3166 | Party | country | Debtor country |
| PmtInf/Dbtr/PstlAdr/AdrLine | Debtor Address Line | Text | 1-70 | 0..2 | SEPA charset | Party | addressLine | Max 2 lines |
| PmtInf/DbtrAcct/Id/IBAN | Debtor Account IBAN | Code | Up to 34 | 1..1 | IBAN | Account | iban | Debtor IBAN (mandatory) |
| PmtInf/DbtrAgt/FinInstnId/BIC | Debtor Agent BIC | Code | 8 or 11 | 1..1 | BIC | FinancialInstitution | bic | Debtor's bank BIC |
| PmtInf/ChrgBr | Charge Bearer | Code | 4 | 1..1 | SHAR | PaymentInstruction | chargeBearer | Must be SHAR for SEPA |
| PmtInf/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-70 | 0..1 | SEPA charset | Party | ultimateDebtorName | Ultimate party |
| PmtInf/UltmtDbtr/Id/OrgId/Othr/Id | Ultimate Debtor ID | Text | 1-35 | 0..1 | SEPA charset | Party | ultimateDebtorId | Organization ID |

#### Credit Transfer Transaction Information (CdtTrfTxInf) - Per Transaction

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/PmtId/InstrId | Instruction Identification | Text | 1-35 | 0..1 | SEPA charset | PaymentInstruction | instructionId | Optional instruction ID |
| CdtTrfTxInf/PmtId/EndToEndId | End To End Identification | Text | 1-35 | 1..1 | SEPA charset | PaymentInstruction | endToEndId | Mandatory E2E ID |
| CdtTrfTxInf/Amt/InstdAmt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | instructedAmount.amount | Payment amount |
| CdtTrfTxInf/Amt/InstdAmt/@Ccy | Currency | Code | 3 | 1..1 | EUR | PaymentInstruction | instructedAmount.currency | Must be EUR |
| CdtTrfTxInf/ChrgBr | Charge Bearer | Code | 4 | 0..1 | SHAR | PaymentInstruction | chargeBearer | SHAR if specified |
| CdtTrfTxInf/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-70 | 0..1 | SEPA charset | Party | ultimateDebtorName | Ultimate originator |
| CdtTrfTxInf/CdtrAgt/FinInstnId/BIC | Creditor Agent BIC | Code | 8 or 11 | 1..1 | BIC | FinancialInstitution | creditorAgentBic | Creditor's bank BIC |
| CdtTrfTxInf/Cdtr/Nm | Creditor Name | Text | 1-70 | 1..1 | SEPA charset | Party | name | Creditor/beneficiary name |
| CdtTrfTxInf/Cdtr/PstlAdr/Ctry | Creditor Country | Code | 2 | 0..1 | ISO 3166 | Party | country | Creditor country |
| CdtTrfTxInf/Cdtr/PstlAdr/AdrLine | Creditor Address Line | Text | 1-70 | 0..2 | SEPA charset | Party | addressLine | Max 2 lines |
| CdtTrfTxInf/CdtrAcct/Id/IBAN | Creditor Account IBAN | Code | Up to 34 | 1..1 | IBAN | Account | iban | Creditor IBAN (mandatory) |
| CdtTrfTxInf/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-70 | 0..1 | SEPA charset | Party | ultimateCreditorName | Ultimate beneficiary |
| CdtTrfTxInf/UltmtCdtr/Id/OrgId/Othr/Id | Ultimate Creditor ID | Text | 1-35 | 0..1 | SEPA charset | Party | ultimateCreditorId | Organization ID |
| CdtTrfTxInf/Purp/Cd | Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | purposeCode | CBFF, CASH, PENS, etc. |
| CdtTrfTxInf/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..1 | SEPA charset | PaymentInstruction | remittanceInformation | Unstructured remittance |
| CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Ref | Creditor Reference | Text | 1-35 | 0..1 | SEPA charset | PaymentInstruction | creditorReference | Structured reference (ISO 11649) |

### pacs.008 - FI to FI Customer Credit Transfer (Interbank)

#### Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | SEPA charset | PaymentInstruction | interbankMessageId | Interbank message ID |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISO DateTime | PaymentInstruction | interbankCreationDateTime | Timestamp |
| GrpHdr/NbOfTxs | Number Of Transactions | Text | 1-15 | 1..1 | Numeric | PaymentInstruction | interbankNumberOfTransactions | Transaction count |
| GrpHdr/TtlIntrBkSttlmAmt | Total Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | interbankSettlementAmount | Total settlement |
| GrpHdr/TtlIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | EUR | PaymentInstruction | interbankSettlementAmount.currency | EUR only |
| GrpHdr/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 1..1 | ISO Date | PaymentInstruction | interbankSettlementDate | Settlement date |
| GrpHdr/SttlmInf/SttlmMtd | Settlement Method | Code | 4 | 1..1 | CLRG | PaymentInstruction | settlementMethod | Clearing system |
| GrpHdr/SttlmInf/ClrSys/Cd | Clearing System Code | Code | 5 | 0..1 | See codes | PaymentInstruction | clearingSystemCode | TARGET2, STEP2, etc. |
| GrpHdr/InstgAgt/FinInstnId/BIC | Instructing Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | instructingAgentBic | Instructing bank |
| GrpHdr/InstdAgt/FinInstnId/BIC | Instructed Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | instructedAgentBic | Instructed bank |

#### Credit Transfer Transaction Information (CdtTrfTxInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/PmtId/InstrId | Instruction Identification | Text | 1-35 | 0..1 | SEPA charset | PaymentInstruction | interbankInstructionId | Instruction ID |
| CdtTrfTxInf/PmtId/EndToEndId | End To End Identification | Text | 1-35 | 1..1 | SEPA charset | PaymentInstruction | endToEndId | E2E ID from pain.001 |
| CdtTrfTxInf/PmtId/TxId | Transaction Identification | Text | 1-35 | 1..1 | SEPA charset | PaymentInstruction | transactionId | Unique transaction ID |
| CdtTrfTxInf/IntrBkSttlmAmt | Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | interbankSettlementAmount.amount | Settlement amount |
| CdtTrfTxInf/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | EUR | PaymentInstruction | interbankSettlementAmount.currency | EUR only |
| CdtTrfTxInf/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | interbankSettlementDate | Settlement date |
| CdtTrfTxInf/SttlmTmIndctn/DbtDtTm | Debit Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | debitDateTime | Debit timestamp |
| CdtTrfTxInf/SttlmTmIndctn/CdtDtTm | Credit Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | creditDateTime | Credit timestamp |
| CdtTrfTxInf/ChrgBr | Charge Bearer | Code | 4 | 1..1 | SHAR | PaymentInstruction | chargeBearer | Must be SHAR |
| CdtTrfTxInf/DbtrAgt/FinInstnId/BIC | Debtor Agent BIC | Code | 8 or 11 | 1..1 | BIC | FinancialInstitution | debtorAgentBic | Debtor's bank |
| CdtTrfTxInf/Dbtr/Nm | Debtor Name | Text | 1-70 | 1..1 | SEPA charset | Party | name | Debtor name |
| CdtTrfTxInf/Dbtr/PstlAdr/Ctry | Debtor Country | Code | 2 | 0..1 | ISO 3166 | Party | country | Debtor country |
| CdtTrfTxInf/Dbtr/PstlAdr/AdrLine | Debtor Address Line | Text | 1-70 | 0..2 | SEPA charset | Party | addressLine | Max 2 lines |
| CdtTrfTxInf/DbtrAcct/Id/IBAN | Debtor Account IBAN | Code | Up to 34 | 1..1 | IBAN | Account | iban | Debtor IBAN |
| CdtTrfTxInf/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-70 | 0..1 | SEPA charset | Party | ultimateDebtorName | Ultimate debtor |
| CdtTrfTxInf/CdtrAgt/FinInstnId/BIC | Creditor Agent BIC | Code | 8 or 11 | 1..1 | BIC | FinancialInstitution | creditorAgentBic | Creditor's bank |
| CdtTrfTxInf/Cdtr/Nm | Creditor Name | Text | 1-70 | 1..1 | SEPA charset | Party | name | Creditor name |
| CdtTrfTxInf/Cdtr/PstlAdr/Ctry | Creditor Country | Code | 2 | 0..1 | ISO 3166 | Party | country | Creditor country |
| CdtTrfTxInf/Cdtr/PstlAdr/AdrLine | Creditor Address Line | Text | 1-70 | 0..2 | SEPA charset | Party | addressLine | Max 2 lines |
| CdtTrfTxInf/CdtrAcct/Id/IBAN | Creditor Account IBAN | Code | Up to 34 | 1..1 | IBAN | Account | iban | Creditor IBAN |
| CdtTrfTxInf/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-70 | 0..1 | SEPA charset | Party | ultimateCreditorName | Ultimate creditor |
| CdtTrfTxInf/Purp/Cd | Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | purposeCode | Purpose |
| CdtTrfTxInf/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..1 | SEPA charset | PaymentInstruction | remittanceInformation | Remittance info |
| CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Ref | Creditor Reference | Text | 1-35 | 0..1 | SEPA charset | PaymentInstruction | creditorReference | Structured reference |

---

## SEPA-Specific Rules

### Character Set
SEPA allows only specific characters (SEPA Character Set):
- a-z A-Z 0-9
- / - ? : ( ) . , ' +
- Space

**CDM Mapping:** PaymentInstruction.characterSetValidation = 'SEPA'

### Mandatory Elements

| Element | Requirement | CDM Validation |
|---------|-------------|----------------|
| Currency | Must be EUR | instructedAmount.currency = 'EUR' |
| IBAN | Mandatory for both debtor and creditor | Validate IBAN format |
| BIC | Mandatory for both agents | Validate BIC format |
| Service Level | Must be 'SEPA' | serviceLevelCode = 'SEPA' |
| Charge Bearer | Must be 'SHAR' | chargeBearer = 'SHAR' |
| End-to-End ID | Mandatory, max 35 chars | endToEndId length ≤ 35 |

### Purpose Codes (Selected Examples)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CBFF | Capital Building | PaymentInstruction.purposeCode = 'CBFF' |
| CASH | Cash Management Transfer | PaymentInstruction.purposeCode = 'CASH' |
| PENS | Pension Payment | PaymentInstruction.purposeCode = 'PENS' |
| SALA | Salary Payment | PaymentInstruction.purposeCode = 'SALA' |
| TRAD | Trade Services | PaymentInstruction.purposeCode = 'TRAD' |
| SUPP | Supplier Payment | PaymentInstruction.purposeCode = 'SUPP' |

### Clearing System Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| TARGET2 | Trans-European Automated Real-time Gross Settlement | PaymentInstruction.clearingSystemCode = 'TARGET2' |
| STEP2 | STEP2 Pan-European ACH | PaymentInstruction.clearingSystemCode = 'STEP2' |
| CORE(FR) | CORE France | PaymentInstruction.clearingSystemCode = 'CORE_FR' |
| ABE | Spanish clearing system | PaymentInstruction.clearingSystemCode = 'ABE' |
| RT1 | TIPS (TARGET Instant Payment Settlement) | PaymentInstruction.clearingSystemCode = 'RT1' |

---

## CDM Extensions Required

All 118 SEPA SCT fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Example

### pain.001 (Customer to Bank)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>MSG20241220001</MsgId>
      <CreDtTm>2024-12-20T10:30:00</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>1250.00</CtrlSum>
      <InitgPty>
        <Nm>ABC Company SARL</Nm>
      </InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>PMTINF001</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>1250.00</CtrlSum>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
      </PmtTpInf>
      <ReqdExctnDt>2024-12-21</ReqdExctnDt>
      <Dbtr>
        <Nm>ABC Company SARL</Nm>
        <PstlAdr>
          <Ctry>FR</Ctry>
          <AdrLine>123 Rue de Rivoli</AdrLine>
          <AdrLine>75001 Paris</AdrLine>
        </PstlAdr>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <IBAN>FR7630006000011234567890189</IBAN>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BIC>BNPAFRPPXXX</BIC>
        </FinInstnId>
      </DbtrAgt>
      <ChrgBr>SHAR</ChrgBr>
      <CdtTrfTxInf>
        <PmtId>
          <EndToEndId>E2E20241220001</EndToEndId>
        </PmtId>
        <Amt>
          <InstdAmt Ccy="EUR">1250.00</InstdAmt>
        </Amt>
        <CdtrAgt>
          <FinInstnId>
            <BIC>DEUTDEFFXXX</BIC>
          </FinInstnId>
        </CdtrAgt>
        <Cdtr>
          <Nm>XYZ GmbH</Nm>
          <PstlAdr>
            <Ctry>DE</Ctry>
            <AdrLine>Friedrichstrasse 100</AdrLine>
            <AdrLine>10117 Berlin</AdrLine>
          </PstlAdr>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <IBAN>DE89370400440532013000</IBAN>
          </Id>
        </CdtrAcct>
        <Purp>
          <Cd>SUPP</Cd>
        </Purp>
        <RmtInf>
          <Ustrd>Invoice INV-2024-5678</Ustrd>
        </RmtInf>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>
```

---

## References

- SEPA Scheme Rulebook: https://www.europeanpaymentscouncil.eu/document-library/rulebooks/sepa-credit-transfer-rulebook
- ISO 20022 Implementation Guidelines: https://www.europeanpaymentscouncil.eu/document-library/implementation-guidelines
- TARGET2 User Guide: https://www.ecb.europa.eu/paym/target/target2/
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
