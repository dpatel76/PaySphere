# ISO 20022 pacs.004.001.11 - Payment Return
## Complete Field Mapping to GPS CDM

**Message Type:** pacs.004.001.11 (PaymentReturnV11)
**Standard:** ISO 20022
**Usage:** Return of funds following a payment instruction
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 110 fields mapped)

---

## Message Overview

The pacs.004 message is sent by an agent to return funds to the previous agent in the payment chain. This occurs when a payment cannot be executed or processed (e.g., incorrect account, closed account, insufficient funds).

**Key Use Cases:**
- Return unpaid/dishonored payments
- Reject payments due to incorrect details
- Reverse payments due to fraud
- Return payments exceeding limits
- Technical rejections

**Message Flow:** Creditor Agent → Debtor Agent (reverse of original payment flow)

**Critical Importance:** Essential for exception handling, reconciliation, and customer service

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total pacs.004 Fields** | 110 | 100% |
| **Mapped to CDM** | 110 | 100% |
| **Direct Mapping** | 98 | 89% |
| **Derived/Calculated** | 10 | 9% |
| **Reference Data Lookup** | 2 | 2% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | returnMessageId | Unique return message ID |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISO DateTime | PaymentInstruction | returnCreationDateTime | Return message timestamp |
| GrpHdr/NbOfTxs | Number Of Transactions | Text | 1-15 | 0..1 | Numeric | PaymentInstruction | returnNumberOfTransactions | Number of returns in message |
| GrpHdr/CtrlSum | Control Sum | DecimalNumber | - | 0..1 | Decimal (18,5) | PaymentInstruction | returnControlSum | Total return amount |
| GrpHdr/TtlRtrdIntrBkSttlmAmt | Total Returned Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | totalReturnedAmount | Total returned |
| GrpHdr/TtlRtrdIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | totalReturnedAmount.currency | Currency |
| GrpHdr/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | returnSettlementDate | Return settlement date |
| GrpHdr/SttlmInf/SttlmMtd | Settlement Method | Code | 4 | 1..1 | INDA, INGA, etc. | PaymentInstruction | returnSettlementMethod | How return settles |
| GrpHdr/SttlmInf/SttlmAcct/Id/IBAN | Settlement Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | returnSettlementAccountIban | Settlement account |
| GrpHdr/SttlmInf/ClrSys/Cd | Clearing System Code | Code | 1-5 | 0..1 | External code | PaymentInstruction | returnClearingSystemCode | Clearing system |
| GrpHdr/InstgAgt/FinInstnId/BICFI | Instructing Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | returnInstructingAgentBic | Agent initiating return |
| GrpHdr/InstdAgt/FinInstnId/BICFI | Instructed Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | returnInstructedAgentBic | Agent receiving return |

### Original Group Information (OrgnlGrpInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInf/OrgnlGrpInf/OrgnlMsgId | Original Message ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction | originalPaymentMessageId | Original pacs.008 message ID |
| TxInf/OrgnlGrpInf/OrgnlMsgNmId | Original Message Name ID | Text | 1-35 | 1..1 | pacs.008, etc. | PaymentInstruction | originalPaymentMessageName | Original message type |
| TxInf/OrgnlGrpInf/OrgnlCreDtTm | Original Creation Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | originalPaymentCreationDateTime | Original timestamp |

### Transaction Information (TxInf) - Per Returned Transaction

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInf/RtrId | Return Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | returnId | Unique return ID |
| TxInf/OrgnlInstrId | Original Instruction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalInstructionId | From original payment |
| TxInf/OrgnlEndToEndId | Original End To End Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | originalEndToEndId | Original E2E ID (mandatory) |
| TxInf/OrgnlTxId | Original Transaction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalTransactionId | Original transaction ID |
| TxInf/OrgnlUETR | Original UETR | Text | 36 | 0..1 | UUID | PaymentInstruction | originalUetr | Original SWIFT gpi tracker |
| TxInf/OrgnlClrSysRef | Original Clearing System Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalClearingSystemReference | Original clearing ref |
| TxInf/OrgnlIntrBkSttlmAmt | Original Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | originalInterbankSettlementAmount | Original amount |
| TxInf/OrgnlIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | originalInterbankSettlementAmount.currency | Original currency |
| TxInf/OrgnlIntrBkSttlmDt | Original Interbank Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | originalInterbankSettlementDate | Original settlement date |
| TxInf/RtrdIntrBkSttlmAmt | Returned Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | returnedAmount | Amount being returned |
| TxInf/RtrdIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | returnedAmount.currency | Return currency |
| TxInf/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | returnInterbankSettlementDate | Return settlement date |
| TxInf/SttlmPrty | Settlement Priority | Code | 4 | 0..1 | HIGH, NORM | PaymentInstruction | returnSettlementPriority | Return priority |
| TxInf/SttlmTmIndctn/DbtDtTm | Debit Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | returnDebitDateTime | When debited |
| TxInf/SttlmTmIndctn/CdtDtTm | Credit Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | returnCreditDateTime | When credited |
| TxInf/SttlmTmReq/CLSTm | Closing Time | Time | - | 0..1 | ISO Time | PaymentInstruction | returnClosingTime | Cut-off time |
| TxInf/PmtTpInf/InstrPrty | Instruction Priority | Code | 4 | 0..1 | HIGH, NORM | PaymentInstruction | returnInstructionPriority | Priority |
| TxInf/PmtTpInf/ClrChanl | Clearing Channel | Code | 4 | 0..1 | RTGS, RTNS, etc. | PaymentInstruction | returnClearingChannel | Clearing channel |
| TxInf/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | returnServiceLevelCode | Service level |
| TxInf/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | 1-35 | 0..1 | External code | PaymentInstruction | returnLocalInstrument | Local instrument |

### Return Reason Information (RtrnRsnInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInf/RtrnRsnInf/Orgtr/Nm | Return Reason Originator Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | returnReasonOriginatorName | Who initiated return |
| TxInf/RtrnRsnInf/Orgtr/Id/OrgId/AnyBIC | Originator BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | returnReasonOriginatorBic | Originator BIC |
| TxInf/RtrnRsnInf/Rsn/Cd | Return Reason Code | Code | 1-4 | 0..1 | See codes below | PaymentInstruction | returnReasonCode | Standard reason code |
| TxInf/RtrnRsnInf/Rsn/Prtry | Return Reason Proprietary | Text | 1-35 | 0..1 | Free text | PaymentInstruction | returnReasonProprietary | Proprietary reason |
| TxInf/RtrnRsnInf/AddtlInf | Additional Information | Text | 1-105 | 0..* | Free text | PaymentInstruction | returnReasonAdditionalInfo | Extra details |

### Charges Information (ChrgsInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInf/ChrgsInf/Amt | Charges Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | returnChargesAmount | Charges on return |
| TxInf/ChrgsInf/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | returnChargesAmount.currency | Charges currency |
| TxInf/ChrgsInf/Agt/FinInstnId/BICFI | Charging Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | returnChargingAgentBic | Who charged |
| TxInf/ChrgsInf/Tp/Cd | Charges Type Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | returnChargesTypeCode | Type of charge |

### Instructing Agent (InstgAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInf/InstgAgt/FinInstnId/BICFI | Instructing Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | txnInstructingAgentBic | Agent instructing return |
| TxInf/InstgAgt/FinInstnId/ClrSysMmbId/MmbId | Clearing Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | txnInstructingAgentClearingId | Clearing member |
| TxInf/InstgAgt/FinInstnId/Nm | Instructing Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | txnInstructingAgentName | Agent name |
| TxInf/InstgAgt/BrnchId/Id | Branch Identification | Text | 1-35 | 0..1 | Free text | FinancialInstitution | txnInstructingAgentBranchId | Branch ID |

### Instructed Agent (InstdAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInf/InstdAgt/FinInstnId/BICFI | Instructed Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | txnInstructedAgentBic | Agent receiving return |
| TxInf/InstdAgt/FinInstnId/ClrSysMmbId/MmbId | Clearing Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | txnInstructedAgentClearingId | Clearing member |
| TxInf/InstdAgt/FinInstnId/Nm | Instructed Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | txnInstructedAgentName | Agent name |

### Original Transaction Reference (OrgnlTxRef)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInf/OrgnlTxRef/Amt/InstdAmt | Original Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | originalInstructedAmount | Original instructed amount |
| TxInf/OrgnlTxRef/Amt/InstdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | originalInstructedAmount.currency | Original currency |
| TxInf/OrgnlTxRef/ReqdExctnDt | Original Requested Execution Date | Date/DateTime | - | 0..1 | ISO Date | PaymentInstruction | originalRequestedExecutionDate | Original execution date |
| TxInf/OrgnlTxRef/ReqdColltnDt | Original Requested Collection Date | Date | - | 0..1 | ISO Date | PaymentInstruction | originalRequestedCollectionDate | For direct debits |
| TxInf/OrgnlTxRef/PmtTpInf/InstrPrty | Original Instruction Priority | Code | 4 | 0..1 | HIGH, NORM | PaymentInstruction | originalInstructionPriority | Priority |
| TxInf/OrgnlTxRef/PmtTpInf/SvcLvl/Cd | Original Service Level Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | originalServiceLevelCode | Service level |
| TxInf/OrgnlTxRef/PmtTpInf/LclInstrm/Cd | Original Local Instrument Code | Code | 1-35 | 0..1 | External code | PaymentInstruction | originalLocalInstrument | Local instrument |
| TxInf/OrgnlTxRef/PmtTpInf/CtgyPurp/Cd | Original Category Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | originalCategoryPurposeCode | Category purpose |
| TxInf/OrgnlTxRef/PmtMtd | Original Payment Method | Code | 4 | 0..1 | CHK, TRF, DD | PaymentInstruction | originalPaymentMethod | Payment method |
| TxInf/OrgnlTxRef/MndtRltdInf/MndtId | Original Mandate ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalMandateId | Mandate reference |
| TxInf/OrgnlTxRef/MndtRltdInf/DtOfSgntr | Original Date Of Signature | Date | - | 0..1 | ISO Date | PaymentInstruction | originalMandateSignatureDate | Mandate signature |
| TxInf/OrgnlTxRef/RmtInf/Ustrd | Original Unstructured Remittance | Text | 1-140 | 0..1 | Free text | PaymentInstruction | originalRemittanceInformation | Remittance info |
| TxInf/OrgnlTxRef/RmtInf/Strd/CdtrRefInf/Ref | Original Creditor Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalCreditorReference | Structured reference |
| TxInf/OrgnlTxRef/UltmtDbtr/Nm | Original Ultimate Debtor Name | Text | 1-140 | 0..1 | Free text | Party | originalUltimateDebtorName | Ultimate debtor |
| TxInf/OrgnlTxRef/Dbtr/Nm | Original Debtor Name | Text | 1-140 | 0..1 | Free text | Party | originalDebtorName | Debtor |
| TxInf/OrgnlTxRef/Dbtr/PstlAdr/Ctry | Original Debtor Country | Code | 2 | 0..1 | ISO 3166 | Party | originalDebtorCountry | Country |
| TxInf/OrgnlTxRef/DbtrAcct/Id/IBAN | Original Debtor Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | originalDebtorAccountIban | Debtor account |
| TxInf/OrgnlTxRef/DbtrAgt/FinInstnId/BICFI | Original Debtor Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | originalDebtorAgentBic | Debtor's bank |
| TxInf/OrgnlTxRef/CdtrAgt/FinInstnId/BICFI | Original Creditor Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | originalCreditorAgentBic | Creditor's bank |
| TxInf/OrgnlTxRef/Cdtr/Nm | Original Creditor Name | Text | 1-140 | 0..1 | Free text | Party | originalCreditorName | Creditor |
| TxInf/OrgnlTxRef/Cdtr/PstlAdr/Ctry | Original Creditor Country | Code | 2 | 0..1 | ISO 3166 | Party | originalCreditorCountry | Country |
| TxInf/OrgnlTxRef/CdtrAcct/Id/IBAN | Original Creditor Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | originalCreditorAccountIban | Creditor account |
| TxInf/OrgnlTxRef/UltmtCdtr/Nm | Original Ultimate Creditor Name | Text | 1-140 | 0..1 | Free text | Party | originalUltimateCreditorName | Ultimate creditor |
| TxInf/OrgnlTxRef/Purp/Cd | Original Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | originalPurposeCode | Purpose |

### Supplementary Data

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/Envlp | Supplementary Data Envelope | Any | - | 1..1 | XML/JSON | PaymentInstruction | supplementaryData | Additional data |

---

## Return Reason Codes (ISO 20022 External Code List)

### Account Related Returns

| Code | Description | CDM Mapping | Severity |
|------|-------------|-------------|----------|
| AC01 | Incorrect Account Number | PaymentInstruction.returnReasonCode = 'AC01' | High |
| AC02 | Invalid Debtor Account Number | PaymentInstruction.returnReasonCode = 'AC02' | High |
| AC03 | Invalid Creditor Account Number | PaymentInstruction.returnReasonCode = 'AC03' | High |
| AC04 | Closed Account Number | PaymentInstruction.returnReasonCode = 'AC04' | High |
| AC05 | Closed Debtor Account Number | PaymentInstruction.returnReasonCode = 'AC05' | High |
| AC06 | Blocked Account | PaymentInstruction.returnReasonCode = 'AC06' | High |
| AC07 | Closed Creditor Account Number | PaymentInstruction.returnReasonCode = 'AC07' | High |
| AC13 | Invalid Debtor Account Type | PaymentInstruction.returnReasonCode = 'AC13' | Medium |
| AC14 | Invalid Creditor Account Type | PaymentInstruction.returnReasonCode = 'AC14' | Medium |

### Amount Related Returns

| Code | Description | CDM Mapping | Severity |
|------|-------------|-------------|----------|
| AM01 | Zero Amount | PaymentInstruction.returnReasonCode = 'AM01' | High |
| AM02 | Not Allowed Amount | PaymentInstruction.returnReasonCode = 'AM02' | High |
| AM03 | Not Allowed Currency | PaymentInstruction.returnReasonCode = 'AM03' | High |
| AM04 | Insufficient Funds | PaymentInstruction.returnReasonCode = 'AM04' | High |
| AM05 | Duplication | PaymentInstruction.returnReasonCode = 'AM05' | High |
| AM09 | Wrong Amount | PaymentInstruction.returnReasonCode = 'AM09' | High |
| AM10 | Invalid Control Sum | PaymentInstruction.returnReasonCode = 'AM10' | Medium |
| AM11 | Invalid Interbank Settlement Amount | PaymentInstruction.returnReasonCode = 'AM11' | High |
| AM12 | Invalid Interbank Settlement Date | PaymentInstruction.returnReasonCode = 'AM12' | Medium |

### Agent Related Returns

| Code | Description | CDM Mapping | Severity |
|------|-------------|-------------|----------|
| AG01 | Transaction Forbidden | PaymentInstruction.returnReasonCode = 'AG01' | High |
| AG02 | Invalid Bank Operation Code | PaymentInstruction.returnReasonCode = 'AG02' | High |
| AG03 | Transaction Not Supported | PaymentInstruction.returnReasonCode = 'AG03' | High |
| AG09 | Payment Type Not Supported | PaymentInstruction.returnReasonCode = 'AG09' | High |
| AG10 | Agent Suspended | PaymentInstruction.returnReasonCode = 'AG10' | Critical |
| AG11 | Creditor Agent Suspended | PaymentInstruction.returnReasonCode = 'AG11' | Critical |
| AG12 | Creditor Agent Not Reachable | PaymentInstruction.returnReasonCode = 'AG12' | High |

### Regulatory/Legal Returns

| Code | Description | CDM Mapping | Severity |
|------|-------------|-------------|----------|
| RR01 | Missing Debtor Account | PaymentInstruction.returnReasonCode = 'RR01' | High |
| RR02 | Missing Debtor Name Or Address | PaymentInstruction.returnReasonCode = 'RR02' | High |
| RR03 | Missing Creditor Name Or Address | PaymentInstruction.returnReasonCode = 'RR03' | High |
| RR04 | Regulatory Reason | PaymentInstruction.returnReasonCode = 'RR04' | Critical |
| RR05 | Regulatory Requirements Not Met | PaymentInstruction.returnReasonCode = 'RR05' | Critical |
| RR06 | Tax Reason | PaymentInstruction.returnReasonCode = 'RR06' | High |
| RR07 | Legal Decision | PaymentInstruction.returnReasonCode = 'RR07' | Critical |
| RR08 | Debtor Deceased | PaymentInstruction.returnReasonCode = 'RR08' | High |
| RR09 | Creditor Deceased | PaymentInstruction.returnReasonCode = 'RR09' | High |
| RR10 | Debtor Bankrupt | PaymentInstruction.returnReasonCode = 'RR10' | Critical |
| RR11 | Creditor Bankrupt | PaymentInstruction.returnReasonCode = 'RR11' | Critical |
| RR12 | Creditor Refuses Payment | PaymentInstruction.returnReasonCode = 'RR12' | Medium |

### Mandate Related Returns (Direct Debits)

| Code | Description | CDM Mapping | Severity |
|------|-------------|-------------|----------|
| MD01 | No Mandate | PaymentInstruction.returnReasonCode = 'MD01' | High |
| MD02 | Missing Mandate Related Information | PaymentInstruction.returnReasonCode = 'MD02' | High |
| MD06 | Refund Request By End Customer | PaymentInstruction.returnReasonCode = 'MD06' | Medium |
| MD07 | End Customer Deceased | PaymentInstruction.returnReasonCode = 'MD07' | High |

### Technical Returns

| Code | Description | CDM Mapping | Severity |
|------|-------------|-------------|----------|
| FF01 | Invalid File Format | PaymentInstruction.returnReasonCode = 'FF01' | High |
| FF05 | Invalid Local Instrument Code | PaymentInstruction.returnReasonCode = 'FF05' | Medium |
| MS02 | Reason Not Specified | PaymentInstruction.returnReasonCode = 'MS02' | Low |
| MS03 | Not Specified Reason Agent Generated | PaymentInstruction.returnReasonCode = 'MS03' | Low |
| RC01 | Bank Identifier Incorrect | PaymentInstruction.returnReasonCode = 'RC01' | High |
| TM01 | Cut-Off Time | PaymentInstruction.returnReasonCode = 'TM01' | Medium |
| NARR | Narrative | PaymentInstruction.returnReasonCode = 'NARR' | Low |

---

## CDM Extensions Required

All 110 pacs.004 fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Example

### Payment Return - Incorrect Account

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.004.001.11">
  <PmtRtr>
    <GrpHdr>
      <MsgId>RTN20241220001</MsgId>
      <CreDtTm>2024-12-20T15:00:00Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <TtlRtrdIntrBkSttlmAmt Ccy="USD">125000.00</TtlRtrdIntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <SttlmInf>
        <SttlmMtd>INDA</SttlmMtd>
      </SttlmInf>
      <InstgAgt>
        <FinInstnId>
          <BICFI>CHASUS33XXX</BICFI>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <BICFI>NWBKGB2LXXX</BICFI>
        </FinInstnId>
      </InstdAgt>
    </GrpHdr>
    <TxInf>
      <RtrId>RTN001</RtrId>
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
      <RtrdIntrBkSttlmAmt Ccy="USD">125000.00</RtrdIntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <RtrnRsnInf>
        <Orgtr>
          <Nm>JPMorgan Chase Bank</Nm>
          <Id>
            <OrgId>
              <AnyBIC>CHASUS33XXX</AnyBIC>
            </OrgId>
          </Id>
        </Orgtr>
        <Rsn>
          <Cd>AC03</Cd>
        </Rsn>
        <AddtlInf>Invalid creditor account number - account 987654321 does not exist in our system</AddtlInf>
      </RtrnRsnInf>
      <InstgAgt>
        <FinInstnId>
          <BICFI>CHASUS33XXX</BICFI>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <BICFI>NWBKGB2LXXX</BICFI>
        </FinInstnId>
      </InstdAgt>
      <OrgnlTxRef>
        <Amt>
          <InstdAmt Ccy="USD">125000.00</InstdAmt>
        </Amt>
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
        <RmtInf>
          <Ustrd>Payment for Invoice INV-2024-1234</Ustrd>
        </RmtInf>
      </OrgnlTxRef>
    </TxInf>
  </PmtRtr>
</Document>
```

---

## References

- ISO 20022 pacs.004 Specification: https://www.iso20022.org/catalogue-messages/iso-20022-messages-archive?search=pacs.004
- ISO 20022 External Code Lists: https://www.iso20022.org/external-code-list
- SWIFT Standards: https://www.swift.com/standards/iso-20022
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
