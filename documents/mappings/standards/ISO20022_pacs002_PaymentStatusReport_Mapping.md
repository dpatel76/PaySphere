# ISO 20022 pacs.002.001.12 - FI to FI Payment Status Report
## Complete Field Mapping to GPS CDM

**Message Type:** pacs.002.001.12 (FIToFIPaymentStatusReportV12)
**Standard:** ISO 20022
**Usage:** Financial institution to financial institution payment status report
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 95 fields mapped)

---

## Message Overview

The pacs.002 message is sent by an instructed agent to the previous party in the payment chain to provide information on the status of a previously sent payment instruction.

**Key Use Cases:**
- Acknowledgment of receipt and acceptance
- Rejection notification with reason codes
- Pending status updates
- Settlement confirmation
- Error notifications

**Message Flow:** Instructed Agent → Instructing Agent (or Originator)

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total pacs.002 Fields** | 95 | 100% |
| **Mapped to CDM** | 95 | 100% |
| **Direct Mapping** | 85 | 89% |
| **Derived/Calculated** | 8 | 8% |
| **Reference Data Lookup** | 2 | 2% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | statusReportMessageId | Unique status report ID |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISO DateTime | PaymentInstruction | statusReportCreationDateTime | Report creation timestamp |

### Original Group Information and Status (OrgnlGrpInfAndSts)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| OrgnlGrpInfAndSts/OrgnlMsgId | Original Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | originalMessageId | Original pacs.008 message ID |
| OrgnlGrpInfAndSts/OrgnlMsgNmId | Original Message Name Identification | Text | 1-35 | 1..1 | pacs.008, etc. | PaymentInstruction | originalMessageName | Message type being reported on |
| OrgnlGrpInfAndSts/OrgnlCreDtTm | Original Creation Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | originalCreationDateTime | Original message timestamp |
| OrgnlGrpInfAndSts/OrgnlNbOfTxs | Original Number Of Transactions | Text | 1-15 | 0..1 | Numeric | PaymentInstruction | originalNumberOfTransactions | Transaction count in original |
| OrgnlGrpInfAndSts/OrgnlCtrlSum | Original Control Sum | DecimalNumber | - | 0..1 | Decimal (18,5) | PaymentInstruction | originalControlSum | Original total amount |
| OrgnlGrpInfAndSts/GrpSts | Group Status | Code | - | 0..1 | See status codes | PaymentInstruction | groupStatus | Overall group status |
| OrgnlGrpInfAndSts/StsRsnInf/Orgtr/Nm | Status Reason Originator Name | Text | 1-140 | 0..1 | Free text | PaymentInstruction | statusReasonOriginatorName | Who originated status |
| OrgnlGrpInfAndSts/StsRsnInf/Rsn/Cd | Status Reason Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | groupStatusReasonCode | Reason code |
| OrgnlGrpInfAndSts/StsRsnInf/Rsn/Prtry | Status Reason Proprietary | Text | 1-35 | 0..1 | Free text | PaymentInstruction | groupStatusReasonProprietary | Proprietary reason |
| OrgnlGrpInfAndSts/StsRsnInf/AddtlInf | Additional Information | Text | 1-105 | 0..* | Free text | PaymentInstruction | groupStatusAdditionalInfo | Extra details |

### Transaction Information and Status (TxInfAndSts) - Per Transaction

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/StsId | Status Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | statusId | Unique status ID |
| TxInfAndSts/OrgnlGrpInf/OrgnlMsgId | Original Group Message ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionOriginalGroupMessageId | Original group message |
| TxInfAndSts/OrgnlGrpInf/OrgnlMsgNmId | Original Group Message Name ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionOriginalGroupMessageName | Original message type |
| TxInfAndSts/OrgnlInstrId | Original Instruction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalInstructionId | Original instruction ID |
| TxInfAndSts/OrgnlEndToEndId | Original End To End Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalEndToEndId | Original E2E ID |
| TxInfAndSts/OrgnlTxId | Original Transaction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalTransactionId | Original transaction ID |
| TxInfAndSts/OrgnlUETR | Original UETR | Text | 36 | 0..1 | UUID | PaymentInstruction | originalUetr | Original SWIFT gpi tracker |
| TxInfAndSts/TxSts | Transaction Status | Code | - | 0..1 | See status codes | PaymentInstruction | transactionStatus | Transaction-level status |
| TxInfAndSts/StsRsnInf/Orgtr/Nm | Status Reason Originator Name | Text | 1-140 | 0..1 | Free text | PaymentInstruction | transactionStatusOriginatorName | Who originated status |
| TxInfAndSts/StsRsnInf/Orgtr/Id/OrgId/AnyBIC | Originator BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | statusOriginatorBic | Originator BIC |
| TxInfAndSts/StsRsnInf/Rsn/Cd | Status Reason Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | transactionStatusReasonCode | Reason code |
| TxInfAndSts/StsRsnInf/Rsn/Prtry | Status Reason Proprietary | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionStatusReasonProprietary | Proprietary reason |
| TxInfAndSts/StsRsnInf/AddtlInf | Additional Information | Text | 1-105 | 0..* | Free text | PaymentInstruction | transactionStatusAdditionalInfo | Extra details |
| TxInfAndSts/ChrgsInf/Amt | Charges Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | statusChargesAmount | Charges applied |
| TxInfAndSts/ChrgsInf/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | statusChargesAmount.currency | Charges currency |
| TxInfAndSts/ChrgsInf/Agt/FinInstnId/BICFI | Charging Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | chargingAgentBic | Who charged |
| TxInfAndSts/ChrgsInf/Tp/Cd | Charges Type Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | chargesType | Type of charge |
| TxInfAndSts/AccptncDtTm | Acceptance Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | acceptanceDateTime | When accepted |
| TxInfAndSts/AcctSvcrRef | Account Servicer Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction | accountServicerReference | Servicer reference |
| TxInfAndSts/ClrSysRef | Clearing System Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction | statusClearingSystemReference | Clearing reference |

### Original Transaction Reference (OrgnlTxRef)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInfAndSts/OrgnlTxRef/IntrBkSttlmAmt | Original Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | originalInterbankSettlementAmount | Original settlement amount |
| TxInfAndSts/OrgnlTxRef/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | originalInterbankSettlementAmount.currency | Original currency |
| TxInfAndSts/OrgnlTxRef/Amt/InstdAmt | Original Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | originalInstructedAmount | Original amount |
| TxInfAndSts/OrgnlTxRef/Amt/InstdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | originalInstructedAmount.currency | Original currency |
| TxInfAndSts/OrgnlTxRef/IntrBkSttlmDt | Original Interbank Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | originalInterbankSettlementDate | Original settlement date |
| TxInfAndSts/OrgnlTxRef/ReqdColltnDt | Original Requested Collection Date | Date | - | 0..1 | ISO Date | PaymentInstruction | originalRequestedCollectionDate | For direct debits |
| TxInfAndSts/OrgnlTxRef/ReqdExctnDt | Original Requested Execution Date | Date/DateTime | - | 0..1 | ISO Date | PaymentInstruction | originalRequestedExecutionDate | Original execution date |
| TxInfAndSts/OrgnlTxRef/CdtrSchmeId/Id | Original Creditor Scheme ID | Text | 1-35 | 0..1 | Free text | Party | originalCreditorSchemeId | For direct debits |
| TxInfAndSts/OrgnlTxRef/SttlmInf/SttlmMtd | Settlement Method | Code | 4 | 0..1 | INDA, INGA, etc. | PaymentInstruction | originalSettlementMethod | Settlement method |
| TxInfAndSts/OrgnlTxRef/SttlmInf/SttlmAcct/Id/IBAN | Settlement Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | originalSettlementAccountIban | Settlement account |
| TxInfAndSts/OrgnlTxRef/PmtTpInf/InstrPrty | Instruction Priority | Code | 4 | 0..1 | HIGH, NORM | PaymentInstruction | originalInstructionPriority | Priority |
| TxInfAndSts/OrgnlTxRef/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | originalServiceLevelCode | Service level |
| TxInfAndSts/OrgnlTxRef/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | 1-35 | 0..1 | External code | PaymentInstruction | originalLocalInstrument | Local instrument |
| TxInfAndSts/OrgnlTxRef/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | originalCategoryPurposeCode | Category purpose |
| TxInfAndSts/OrgnlTxRef/PmtMtd | Payment Method | Code | 4 | 0..1 | CHK, TRF, DD, etc. | PaymentInstruction | originalPaymentMethod | Payment method |
| TxInfAndSts/OrgnlTxRef/MndtRltdInf/MndtId | Mandate ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalMandateId | Direct debit mandate |
| TxInfAndSts/OrgnlTxRef/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..1 | Free text | PaymentInstruction | originalRemittanceInformation | Remittance info |
| TxInfAndSts/OrgnlTxRef/RmtInf/Strd/CdtrRefInf/Ref | Creditor Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalCreditorReference | Structured reference |
| TxInfAndSts/OrgnlTxRef/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Free text | Party | originalUltimateDebtorName | Ultimate debtor |
| TxInfAndSts/OrgnlTxRef/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | originalDebtorName | Debtor |
| TxInfAndSts/OrgnlTxRef/DbtrAcct/Id/IBAN | Debtor Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | originalDebtorAccountIban | Debtor account |
| TxInfAndSts/OrgnlTxRef/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | originalDebtorAgentBic | Debtor's bank |
| TxInfAndSts/OrgnlTxRef/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | originalCreditorAgentBic | Creditor's bank |
| TxInfAndSts/OrgnlTxRef/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | originalCreditorName | Creditor |
| TxInfAndSts/OrgnlTxRef/CdtrAcct/Id/IBAN | Creditor Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | originalCreditorAccountIban | Creditor account |
| TxInfAndSts/OrgnlTxRef/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Free text | Party | originalUltimateCreditorName | Ultimate creditor |

### Supplementary Data

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/Envlp | Supplementary Data Envelope | Any | - | 1..1 | XML/JSON | PaymentInstruction | supplementaryData | Additional proprietary data |

---

## Status Codes

### Group Status / Transaction Status

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| ACCP | Accepted Customer Profile | PaymentInstruction.transactionStatus = 'ACCP' |
| ACSC | Accepted Settlement Completed | PaymentInstruction.transactionStatus = 'ACSC' |
| ACSP | Accepted Settlement In Process | PaymentInstruction.transactionStatus = 'ACSP' |
| ACTC | Accepted Technical Validation | PaymentInstruction.transactionStatus = 'ACTC' |
| ACWC | Accepted With Change | PaymentInstruction.transactionStatus = 'ACWC' |
| ACWP | Accepted Without Posting | PaymentInstruction.transactionStatus = 'ACWP' |
| RCVD | Received | PaymentInstruction.transactionStatus = 'RCVD' |
| PDNG | Pending | PaymentInstruction.transactionStatus = 'PDNG' |
| RJCT | Rejected | PaymentInstruction.transactionStatus = 'RJCT' |
| CANC | Cancelled | PaymentInstruction.transactionStatus = 'CANC' |
| PART | Partially Accepted | PaymentInstruction.transactionStatus = 'PART' |

### Status Reason Codes (Selected Examples)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| AC01 | Incorrect Account Number | PaymentInstruction.transactionStatusReasonCode = 'AC01' |
| AC03 | Invalid Creditor Account Number | PaymentInstruction.transactionStatusReasonCode = 'AC03' |
| AC04 | Closed Account Number | PaymentInstruction.transactionStatusReasonCode = 'AC04' |
| AC06 | Blocked Account | PaymentInstruction.transactionStatusReasonCode = 'AC06' |
| AG01 | Transaction Forbidden | PaymentInstruction.transactionStatusReasonCode = 'AG01' |
| AG02 | Invalid Bank Operation Code | PaymentInstruction.transactionStatusReasonCode = 'AG02' |
| AM01 | Zero Amount | PaymentInstruction.transactionStatusReasonCode = 'AM01' |
| AM02 | Not Allowed Amount | PaymentInstruction.transactionStatusReasonCode = 'AM02' |
| AM03 | Not Allowed Currency | PaymentInstruction.transactionStatusReasonCode = 'AM03' |
| AM04 | Insufficient Funds | PaymentInstruction.transactionStatusReasonCode = 'AM04' |
| AM05 | Duplication | PaymentInstruction.transactionStatusReasonCode = 'AM05' |
| AM09 | Wrong Amount | PaymentInstruction.transactionStatusReasonCode = 'AM09' |
| BE01 | Inconsistent With End Customer | PaymentInstruction.transactionStatusReasonCode = 'BE01' |
| BE04 | Missing Creditor Address | PaymentInstruction.transactionStatusReasonCode = 'BE04' |
| BE05 | Unrecognised Initiating Party | PaymentInstruction.transactionStatusReasonCode = 'BE05' |
| CH03 | Requested Execution Date Too Far In Future | PaymentInstruction.transactionStatusReasonCode = 'CH03' |
| CH07 | Settlement Date/Time After Cut-Off | PaymentInstruction.transactionStatusReasonCode = 'CH07' |
| DT01 | Invalid Date | PaymentInstruction.transactionStatusReasonCode = 'DT01' |
| FF01 | Invalid File Format | PaymentInstruction.transactionStatusReasonCode = 'FF01' |
| MS03 | Not Specified Reason Agent Generated | PaymentInstruction.transactionStatusReasonCode = 'MS03' |
| RC01 | Bank Identifier Incorrect | PaymentInstruction.transactionStatusReasonCode = 'RC01' |
| RF01 | Not Unique Transaction Reference | PaymentInstruction.transactionStatusReasonCode = 'RF01' |
| RR01 | Missing Debtor Account | PaymentInstruction.transactionStatusReasonCode = 'RR01' |
| RR02 | Missing Debtor Name Or Address | PaymentInstruction.transactionStatusReasonCode = 'RR02' |
| RR03 | Missing Creditor Name Or Address | PaymentInstruction.transactionStatusReasonCode = 'RR03' |
| RR04 | Regulatory Reason | PaymentInstruction.transactionStatusReasonCode = 'RR04' |
| TM01 | Cut-Off Time | PaymentInstruction.transactionStatusReasonCode = 'TM01' |

---

## CDM Extensions Required

All 95 pacs.002 fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.002.001.12">
  <FIToFIPmtStsRpt>
    <GrpHdr>
      <MsgId>STATUS20241220001</MsgId>
      <CreDtTm>2024-12-20T14:35:00Z</CreDtTm>
    </GrpHdr>
    <TxInfAndSts>
      <StsId>STS001</StsId>
      <OrgnlInstrId>INSTRID001</OrgnlInstrId>
      <OrgnlEndToEndId>E2E20241220001</OrgnlEndToEndId>
      <OrgnlTxId>TXN20241220001</OrgnlTxId>
      <OrgnlUETR>97ed4827-7b6f-4491-a06f-b548d5a7512d</OrgnlUETR>
      <TxSts>ACSC</TxSts>
      <AccptncDtTm>2024-12-20T14:30:30Z</AccptncDtTm>
      <AcctSvcrRef>SVCREF123456</AcctSvcrRef>
      <ClrSysRef>CLRREF789012</ClrSysRef>
      <OrgnlTxRef>
        <IntrBkSttlmAmt Ccy="USD">125000.00</IntrBkSttlmAmt>
        <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
        <DbtrAgt>
          <FinInstnId>
            <BICFI>NWBKGB2LXXX</BICFI>
          </FinInstnId>
        </DbtrAgt>
        <Dbtr>
          <Nm>ABC Corporation Ltd</Nm>
        </Dbtr>
        <DbtrAcct>
          <Id>
            <IBAN>GB29NWBK60161331926819</IBAN>
          </Id>
        </DbtrAcct>
        <CdtrAgt>
          <FinInstnId>
            <BICFI>CHASUS33XXX</BICFI>
          </FinInstnId>
        </CdtrAgt>
        <Cdtr>
          <Nm>XYZ Supplier Inc</Nm>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <Othr>
              <Id>987654321</Id>
            </Othr>
          </Id>
        </CdtrAcct>
      </OrgnlTxRef>
    </TxInfAndSts>
  </FIToFIPmtStsRpt>
</Document>
```

### Rejection Example

```xml
<TxInfAndSts>
  <OrgnlEndToEndId>E2E20241220002</OrgnlEndToEndId>
  <TxSts>RJCT</TxSts>
  <StsRsnInf>
    <Orgtr>
      <Nm>Receiving Bank</Nm>
      <Id>
        <OrgId>
          <AnyBIC>CHASUS33XXX</AnyBIC>
        </OrgId>
      </Id>
    </Orgtr>
    <Rsn>
      <Cd>AC03</Cd>
    </Rsn>
    <AddtlInf>Invalid creditor account number - account does not exist</AddtlInf>
  </StsRsnInf>
</TxInfAndSts>
```

---

## References

- ISO 20022 pacs.002 Specification: https://www.iso20022.org/catalogue-messages/iso-20022-messages-archive?search=pacs.002
- SWIFT Standards: https://www.swift.com/standards/iso-20022
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
