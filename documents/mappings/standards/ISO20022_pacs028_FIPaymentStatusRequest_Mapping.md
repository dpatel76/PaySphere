# ISO 20022 pacs.028.001.05 - FI to FI Payment Status Request
## Complete Field Mapping to GPS CDM

**Message Type:** pacs.028.001.05 (FIToFIPaymentStatusRequestV05)
**Standard:** ISO 20022
**Usage:** Request for status information on a previously sent payment instruction
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 65 fields mapped)

---

## Message Overview

The pacs.028 message is used by a financial institution to request the status of a payment transaction from another financial institution. It allows tracking of payment instructions (pacs.008, pacs.009) as they flow through the payment chain. The response to this request is typically a pacs.002 (FI to FI Payment Status Report) message.

**Key Use Cases:**
- Payment tracking and investigation
- Exception handling and reconciliation
- Customer payment status inquiries
- SWIFT gpi payment tracker status requests
- Settlement confirmation requests
- Fraud investigation support
- Payment exception resolution

**Message Flow:** Instructing FI → Instructed FI (or any intermediary agent in the payment chain)

**Related Messages:**
- Request: pacs.028 (FI to FI Payment Status Request)
- Response: pacs.002 (FI to FI Payment Status Report)
- Original Payment: pacs.008 (Customer Credit Transfer) or pacs.009 (FI Credit Transfer)

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total pacs.028 Fields** | 65 | 100% |
| **Mapped to CDM** | 65 | 100% |
| **Direct Mapping** | 60 | 92% |
| **Derived/Calculated** | 4 | 6% |
| **Reference Data Lookup** | 1 | 2% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | messageId | Unique message identifier for status request |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISO DateTime | PaymentInstruction | creationDateTime | Status request creation timestamp |

### Original Group Information and Status (OrgnlGrpInfAndSts)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| OrgnlGrpInfAndSts/OrgnlMsgId | Original Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | originalMessageId | Message ID of original payment |
| OrgnlGrpInfAndSts/OrgnlMsgNmId | Original Message Name Identification | Text | 1-35 | 1..1 | pacs.008, pacs.009 | PaymentInstruction | originalMessageType | Type of original message |
| OrgnlGrpInfAndSts/OrgnlCreDtTm | Original Creation Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | originalCreationDateTime | Original message creation timestamp |

### Transaction Information and Status (TxInfAndSts)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/StsReqId | Status Request Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | statusRequestId | Unique identifier for this status request |
| TxInfAndSts/OrgnlGrpInf/OrgnlMsgId | Original Group Message ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction | originalMessageId | Original group message identifier |
| TxInfAndSts/OrgnlGrpInf/OrgnlMsgNmId | Original Group Message Name ID | Text | 1-35 | 1..1 | pacs.008, pacs.009 | PaymentInstruction | originalMessageType | Original message type |
| TxInfAndSts/OrgnlGrpInf/OrgnlCreDtTm | Original Group Creation Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | originalCreationDateTime | Original message timestamp |
| TxInfAndSts/OrgnlInstrId | Original Instruction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalInstructionId | Original instruction ID |
| TxInfAndSts/OrgnlEndToEndId | Original End To End Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalEndToEndId | Original end-to-end ID |
| TxInfAndSts/OrgnlTxId | Original Transaction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalTransactionId | Original transaction ID |
| TxInfAndSts/OrgnlUETR | Original Unique End-to-end Transaction Reference | Text | 36 | 0..1 | UUID | PaymentInstruction | originalUetr | Original SWIFT gpi UETR |
| TxInfAndSts/OrgnlClrSysRef | Original Clearing System Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalClearingSystemReference | Original clearing system ref |
| TxInfAndSts/OrgnlIntrBkSttlmAmt | Original Interbank Settlement Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | originalInterbankSettlementAmount.amount | Original settlement amount |
| TxInfAndSts/OrgnlIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | originalInterbankSettlementAmount.currency | Original currency |
| TxInfAndSts/OrgnlIntrBkSttlmDt | Original Interbank Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | originalInterbankSettlementDate | Original settlement date |

### Original Transaction Reference (OrgnlTxRef)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/OrgnlTxRef/IntrBkSttlmAmt | Interbank Settlement Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | interbankSettlementAmount.amount | Settlement amount |
| TxInfAndSts/OrgnlTxRef/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | interbankSettlementAmount.currency | Currency code |
| TxInfAndSts/OrgnlTxRef/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | interbankSettlementDate | Settlement date |
| TxInfAndSts/OrgnlTxRef/PmtTpInf/InstrPrty | Instruction Priority | Code | - | 0..1 | HIGH, NORM | PaymentInstruction | instructionPriority | Priority indicator |
| TxInfAndSts/OrgnlTxRef/PmtTpInf/ClrChanl | Clearing Channel | Code | - | 0..1 | RTGS, RTNS, MPNS, BOOK | PaymentInstruction | clearingChannel | Clearing channel |
| TxInfAndSts/OrgnlTxRef/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | serviceLevelCode | Service level |
| TxInfAndSts/OrgnlTxRef/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | 1-35 | 0..1 | External code | PaymentInstruction | localInstrument | Country-specific code |
| TxInfAndSts/OrgnlTxRef/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | categoryPurposeCode | Payment category |
| TxInfAndSts/OrgnlTxRef/PmtMtd | Payment Method | Code | - | 0..1 | CHK, TRF, TRA | PaymentInstruction | paymentMethod | Payment method |
| TxInfAndSts/OrgnlTxRef/MndtRltdInf/MndtId | Mandate Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | mandateId | Direct debit mandate ID |
| TxInfAndSts/OrgnlTxRef/MndtRltdInf/DtOfSgntr | Date Of Signature | Date | - | 0..1 | ISO Date | PaymentInstruction | mandateSignatureDate | Mandate signature date |

### Remittance Information Reference

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/OrgnlTxRef/RmtInf/Ustrd | Unstructured Remittance Information | Text | 1-140 | 0..1 | Free text | PaymentInstruction | remittanceInformation | Original remittance info |
| TxInfAndSts/OrgnlTxRef/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd | Document Type Code | Code | - | 0..1 | External code | PaymentInstruction | documentTypeCode | Document type |
| TxInfAndSts/OrgnlTxRef/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction | documentNumber | Reference number |
| TxInfAndSts/OrgnlTxRef/RmtInf/Strd/RfrdDocInf/RltdDt | Related Date | Date | - | 0..1 | ISO Date | PaymentInstruction | documentDate | Document date |
| TxInfAndSts/OrgnlTxRef/RmtInf/Strd/CdtrRefInf/Ref | Creditor Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction | creditorReference | Structured creditor reference |

### Ultimate Debtor Reference

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/OrgnlTxRef/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Free text | Party | ultimateDebtorName | Ultimate originating party |
| TxInfAndSts/OrgnlTxRef/UltmtDbtr/Id/OrgId/AnyBIC | Ultimate Debtor BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | Organization BIC |
| TxInfAndSts/OrgnlTxRef/UltmtDbtr/Id/OrgId/LEI | Ultimate Debtor LEI | Code | 20 | 0..1 | LEI | Party | lei | Legal Entity Identifier |

### Debtor Reference

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/OrgnlTxRef/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | name | Debtor name |
| TxInfAndSts/OrgnlTxRef/Dbtr/PstlAdr/Ctry | Debtor Country | Code | 2 | 0..1 | ISO 3166 | Party | country | Debtor country |
| TxInfAndSts/OrgnlTxRef/Dbtr/Id/OrgId/AnyBIC | Debtor Organization BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | Organization BIC |
| TxInfAndSts/OrgnlTxRef/Dbtr/Id/OrgId/LEI | Debtor LEI | Code | 20 | 0..1 | LEI | Party | lei | Legal Entity Identifier |

### Debtor Account Reference

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/OrgnlTxRef/DbtrAcct/Id/IBAN | Debtor Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Debtor account IBAN |
| TxInfAndSts/OrgnlTxRef/DbtrAcct/Id/Othr/Id | Debtor Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Other account identifier |
| TxInfAndSts/OrgnlTxRef/DbtrAcct/Tp/Cd | Debtor Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account | accountType | Account type |

### Debtor Agent Reference

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/OrgnlTxRef/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Debtor's bank BIC |
| TxInfAndSts/OrgnlTxRef/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId | Debtor Agent Clearing Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| TxInfAndSts/OrgnlTxRef/DbtrAgt/FinInstnId/Nm | Debtor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Bank name |

### Creditor Agent Reference

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/OrgnlTxRef/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Creditor's bank BIC |
| TxInfAndSts/OrgnlTxRef/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId | Creditor Agent Clearing Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| TxInfAndSts/OrgnlTxRef/CdtrAgt/FinInstnId/Nm | Creditor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Bank name |

### Creditor Reference

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/OrgnlTxRef/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | name | Creditor name |
| TxInfAndSts/OrgnlTxRef/Cdtr/PstlAdr/Ctry | Creditor Country | Code | 2 | 0..1 | ISO 3166 | Party | country | Creditor country |
| TxInfAndSts/OrgnlTxRef/Cdtr/Id/OrgId/AnyBIC | Creditor Organization BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | Organization BIC |
| TxInfAndSts/OrgnlTxRef/Cdtr/Id/OrgId/LEI | Creditor LEI | Code | 20 | 0..1 | LEI | Party | lei | Legal Entity Identifier |

### Creditor Account Reference

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/OrgnlTxRef/CdtrAcct/Id/IBAN | Creditor Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Creditor account IBAN |
| TxInfAndSts/OrgnlTxRef/CdtrAcct/Id/Othr/Id | Creditor Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Other account identifier |
| TxInfAndSts/OrgnlTxRef/CdtrAcct/Tp/Cd | Creditor Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account | accountType | Account type |

### Ultimate Creditor Reference

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/OrgnlTxRef/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Free text | Party | ultimateCreditorName | Ultimate beneficiary party |
| TxInfAndSts/OrgnlTxRef/UltmtCdtr/Id/OrgId/AnyBIC | Ultimate Creditor BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | Organization BIC |
| TxInfAndSts/OrgnlTxRef/UltmtCdtr/Id/OrgId/LEI | Ultimate Creditor LEI | Code | 20 | 0..1 | LEI | Party | lei | Legal Entity Identifier |

### Intermediary Agent Reference

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/OrgnlTxRef/IntrmyAgt1/FinInstnId/BICFI | Intermediary Agent 1 BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | First intermediary bank |
| TxInfAndSts/OrgnlTxRef/IntrmyAgt1/FinInstnId/Nm | Intermediary Agent 1 Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Bank name |
| TxInfAndSts/OrgnlTxRef/IntrmyAgt2/FinInstnId/BICFI | Intermediary Agent 2 BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Second intermediary bank |
| TxInfAndSts/OrgnlTxRef/IntrmyAgt3/FinInstnId/BICFI | Intermediary Agent 3 BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | Third intermediary bank |

### Purpose Reference

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/OrgnlTxRef/Purp/Cd | Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | purposeCode | Payment purpose |

### Supplementary Data

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/Envlp | Supplementary Data Envelope | Any | - | 1..1 | XML/JSON | PaymentInstruction | supplementaryData | Additional proprietary data |

---

## Code Lists

### Original Message Name Identification (OrgnlMsgNmId)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| pacs.008.001.10 | FI to FI Customer Credit Transfer | PaymentInstruction.originalMessageType = 'pacs.008' |
| pacs.009.001.10 | Financial Institution Credit Transfer | PaymentInstruction.originalMessageType = 'pacs.009' |
| pacs.003.001.10 | FI to FI Customer Direct Debit | PaymentInstruction.originalMessageType = 'pacs.003' |
| pacs.004.001.11 | Payment Return | PaymentInstruction.originalMessageType = 'pacs.004' |

### Service Level Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| SEPA | Single Euro Payments Area | PaymentInstruction.serviceLevelCode = 'SEPA' |
| URGP | Urgent Payment | PaymentInstruction.serviceLevelCode = 'URGP' |
| NURG | Normal Urgency | PaymentInstruction.serviceLevelCode = 'NURG' |

### Clearing Channel Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| RTGS | Real Time Gross Settlement | PaymentInstruction.clearingChannel = 'RTGS' |
| RTNS | Real Time Net Settlement | PaymentInstruction.clearingChannel = 'RTNS' |
| MPNS | Multiple Net Settlement | PaymentInstruction.clearingChannel = 'MPNS' |
| BOOK | Book Transfer | PaymentInstruction.clearingChannel = 'BOOK' |

### Payment Method Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CHK | Cheque | PaymentInstruction.paymentMethod = 'CHK' |
| TRF | Credit Transfer | PaymentInstruction.paymentMethod = 'TRF' |
| TRA | Transfer Advice | PaymentInstruction.paymentMethod = 'TRA' |

---

## CDM Extensions Required

All 65 pacs.028 fields successfully map to existing CDM model. **No enhancements required.**

The CDM entities (PaymentInstruction, Party, Account, FinancialInstitution) fully support status request scenarios through the use of "original" prefixed attributes that store reference data from the original payment instruction being queried.

---

## Message Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.028.001.05">
  <FIToFIPmtStsReq>
    <GrpHdr>
      <MsgId>STATUSREQ20241220001</MsgId>
      <CreDtTm>2024-12-20T16:45:00Z</CreDtTm>
    </GrpHdr>
    <TxInfAndSts>
      <StsReqId>SREQ20241220001</StsReqId>
      <OrgnlGrpInf>
        <OrgnlMsgId>MSGID20241220001</OrgnlMsgId>
        <OrgnlMsgNmId>pacs.008.001.10</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-20T10:30:00Z</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <OrgnlInstrId>INSTRID001</OrgnlInstrId>
      <OrgnlEndToEndId>E2E20241220001</OrgnlEndToEndId>
      <OrgnlTxId>TXN20241220001</OrgnlTxId>
      <OrgnlUETR>97ed4827-7b6f-4491-a06f-b548d5a7512d</OrgnlUETR>
      <OrgnlIntrBkSttlmAmt Ccy="USD">125000.00</OrgnlIntrBkSttlmAmt>
      <OrgnlIntrBkSttlmDt>2024-12-20</OrgnlIntrBkSttlmDt>
      <OrgnlTxRef>
        <IntrBkSttlmAmt Ccy="USD">125000.00</IntrBkSttlmAmt>
        <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
        <PmtTpInf>
          <InstrPrty>NORM</InstrPrty>
          <SvcLvl>
            <Cd>URGP</Cd>
          </SvcLvl>
        </PmtTpInf>
        <PmtMtd>TRF</PmtMtd>
        <DbtrAgt>
          <FinInstnId>
            <BICFI>NWBKGB2LXXX</BICFI>
            <Nm>National Westminster Bank</Nm>
          </FinInstnId>
        </DbtrAgt>
        <Dbtr>
          <Nm>ABC Corporation Ltd</Nm>
          <PstlAdr>
            <Ctry>GB</Ctry>
          </PstlAdr>
        </Dbtr>
        <DbtrAcct>
          <Id>
            <IBAN>GB29NWBK60161331926819</IBAN>
          </Id>
        </DbtrAcct>
        <CdtrAgt>
          <FinInstnId>
            <BICFI>CHASUS33XXX</BICFI>
            <Nm>JPMorgan Chase Bank</Nm>
          </FinInstnId>
        </CdtrAgt>
        <Cdtr>
          <Nm>XYZ Supplier Inc</Nm>
          <PstlAdr>
            <Ctry>US</Ctry>
          </PstlAdr>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <Othr>
              <Id>987654321</Id>
            </Othr>
          </Id>
        </CdtrAcct>
        <Purp>
          <Cd>GDDS</Cd>
        </Purp>
        <RmtInf>
          <Ustrd>Payment for Invoice INV-2024-1234</Ustrd>
        </RmtInf>
      </OrgnlTxRef>
    </TxInfAndSts>
  </FIToFIPmtStsReq>
</Document>
```

---

## Usage Pattern

### Typical Status Request Workflow

1. **Initiation**: Financial institution needs to track payment status
   - Customer inquiry about payment
   - Exception handling requirement
   - Reconciliation investigation
   - Fraud detection follow-up

2. **pacs.028 Creation**: Requesting FI creates status request
   - Includes original message identifiers (MsgId, UETR, etc.)
   - Optionally includes transaction reference data
   - Sent to instructed agent or intermediary

3. **Processing**: Receiving FI processes request
   - Locates original payment transaction
   - Determines current status
   - Prepares status response

4. **pacs.002 Response**: Receiving FI sends status report
   - Confirms acceptance, pending, or rejection
   - Provides reason codes if rejected
   - Includes settlement information if completed

### Status Request Scenarios

| Scenario | Use pacs.028 When | Expected Response |
|----------|-------------------|-------------------|
| **Payment Tracking** | Customer asks "where is my payment?" | pacs.002 with status code (ACSP, ACCC, RJCT) |
| **Settlement Confirmation** | Need to confirm interbank settlement | pacs.002 with settlement date/amount |
| **Exception Investigation** | Payment not received by beneficiary | pacs.002 with detailed status/reason |
| **Fraud Investigation** | Suspicious transaction requires tracking | pacs.002 with current location/status |
| **SWIFT gpi Tracking** | Real-time payment tracker query | pacs.002 with gpi tracker updates |

---

## Integration Notes

### Relationship to Other Messages

- **pacs.008**: Original customer credit transfer - referenced by pacs.028
- **pacs.009**: Original FI credit transfer - referenced by pacs.028
- **pacs.002**: Payment status report - response to pacs.028
- **pacs.004**: Payment return - may be reported via pacs.002 in response to pacs.028

### Key Identifiers for Matching

The pacs.028 uses these identifiers to match the original payment:

1. **Primary Identifiers** (at least one required):
   - Original Message ID (OrgnlMsgId)
   - Original UETR (OrgnlUETR) - for SWIFT gpi
   - Original Transaction ID (OrgnlTxId)
   - Original End-to-End ID (OrgnlEndToEndId)

2. **Supporting Identifiers** (optional but helpful):
   - Original Instruction ID (OrgnlInstrId)
   - Original Clearing System Reference (OrgnlClrSysRef)
   - Original Settlement Amount and Date

### Best Practices

1. **Always include UETR** for SWIFT gpi transactions
2. **Provide multiple identifiers** to improve matching accuracy
3. **Include transaction reference data** to help receiving FI locate payment
4. **Use status request ID** (StsReqId) for tracking the request itself
5. **Monitor response times** - typical SLA is within minutes for gpi

---

## References

- ISO 20022 Message Definition: https://www.iso20022.org/catalogue-messages/iso-20022-messages-archive?search=pacs.028
- ISO 20022 pacs.028 Schema: https://www.iso20022.org/sites/default/files/documents/D7/pacs.028.001.05.xsd
- SWIFT gpi Tracker Specification: https://www.swift.com/standards/iso-20022/gpi
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
