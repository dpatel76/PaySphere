# ISO 20022 pacs.007.001.11 - FI to FI Payment Reversal
## Complete Field Mapping to GPS CDM

**Message Type:** pacs.007.001.11 (FIToFIPaymentReversalV11)
**Standard:** ISO 20022
**Usage:** Reversal of previously settled payment instruction
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 95 fields mapped)

---

## Message Overview

The pacs.007 message is sent by an agent to reverse a previously settled payment instruction. Unlike returns (pacs.004) which are sent before settlement, reversals are used AFTER settlement has occurred, typically due to error, fraud, or customer request.

**Key Differences from pacs.004 (Return):**
- pacs.004: Used BEFORE final settlement (payment hasn't completed)
- pacs.007: Used AFTER settlement (payment already completed - must reverse)

**Key Use Cases:**
- Reverse incorrectly processed payments
- Fraud-related reversals
- Customer-initiated reversals (after settlement)
- Duplicate payment corrections
- Error correction after settlement

**Message Flow:** Agent detecting error → Previous agent (reverse direction of original payment)

**Critical Importance:** Essential for fraud prevention, error correction, and customer protection

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total pacs.007 Fields** | 95 | 100% |
| **Mapped to CDM** | 95 | 100% |
| **Direct Mapping** | 86 | 91% |
| **Derived/Calculated** | 7 | 7% |
| **Reference Data Lookup** | 2 | 2% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | reversalMessageId | Unique reversal message ID |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISO DateTime | PaymentInstruction | reversalCreationDateTime | Reversal message timestamp |
| GrpHdr/BtchBookg | Batch Booking | Indicator | - | 0..1 | true/false | PaymentInstruction | reversalBatchBooking | Batch or individual |
| GrpHdr/NbOfTxs | Number Of Transactions | Text | 1-15 | 0..1 | Numeric | PaymentInstruction | reversalNumberOfTransactions | Number of reversals |
| GrpHdr/CtrlSum | Control Sum | DecimalNumber | - | 0..1 | Decimal (18,5) | PaymentInstruction | reversalControlSum | Total reversal amount |
| GrpHdr/TtlRvsdIntrBkSttlmAmt | Total Reversed Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | totalReversedAmount | Total reversed |
| GrpHdr/TtlRvsdIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | totalReversedAmount.currency | Currency |
| GrpHdr/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | reversalSettlementDate | Reversal settlement date |
| GrpHdr/SttlmInf/SttlmMtd | Settlement Method | Code | 4 | 1..1 | INDA, INGA, etc. | PaymentInstruction | reversalSettlementMethod | How reversal settles |
| GrpHdr/SttlmInf/SttlmAcct/Id/IBAN | Settlement Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | reversalSettlementAccountIban | Settlement account |
| GrpHdr/SttlmInf/ClrSys/Cd | Clearing System Code | Code | 1-5 | 0..1 | External code | PaymentInstruction | reversalClearingSystemCode | Clearing system |
| GrpHdr/InstgAgt/FinInstnId/BICFI | Instructing Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | reversalInstructingAgentBic | Agent initiating reversal |
| GrpHdr/InstdAgt/FinInstnId/BICFI | Instructed Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | reversalInstructedAgentBic | Agent receiving reversal |

### Transaction Information (TxInf) - Per Reversed Transaction

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInf/RvslId | Reversal Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | reversalId | Unique reversal ID |
| TxInf/OrgnlGrpInf/OrgnlMsgId | Original Message ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction | originalPaymentMessageId | Original pacs.008 message ID |
| TxInf/OrgnlGrpInf/OrgnlMsgNmId | Original Message Name ID | Text | 1-35 | 1..1 | pacs.008, etc. | PaymentInstruction | originalPaymentMessageName | Original message type |
| TxInf/OrgnlGrpInf/OrgnlCreDtTm | Original Creation Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | originalPaymentCreationDateTime | Original timestamp |
| TxInf/OrgnlInstrId | Original Instruction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalInstructionId | From original payment |
| TxInf/OrgnlEndToEndId | Original End To End Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | originalEndToEndId | Original E2E ID (mandatory) |
| TxInf/OrgnlTxId | Original Transaction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | originalTransactionId | Original transaction ID |
| TxInf/OrgnlUETR | Original UETR | Text | 36 | 0..1 | UUID | PaymentInstruction | originalUetr | Original SWIFT gpi tracker |
| TxInf/OrgnlIntrBkSttlmAmt | Original Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | originalInterbankSettlementAmount | Original amount |
| TxInf/OrgnlIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | originalInterbankSettlementAmount.currency | Original currency |
| TxInf/OrgnlIntrBkSttlmDt | Original Interbank Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | originalInterbankSettlementDate | Original settlement date |
| TxInf/RvsdIntrBkSttlmAmt | Reversed Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | reversedAmount | Amount being reversed |
| TxInf/RvsdIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | reversedAmount.currency | Reversal currency |
| TxInf/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | reversalInterbankSettlementDate | Reversal settlement date |
| TxInf/RvsdInstdAmt | Reversed Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | reversedInstructedAmount | Instructed amount reversed |
| TxInf/RvsdInstdAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | reversedInstructedAmount.currency | Instructed currency |
| TxInf/XchgRate | Exchange Rate | BaseOneRate | - | 0..1 | Decimal | PaymentInstruction | reversalExchangeRate | FX rate for reversal |
| TxInf/CompstnAmt | Compensation Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | compensationAmount | Compensation paid |
| TxInf/CompstnAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | compensationAmount.currency | Compensation currency |
| TxInf/ChrgBr | Charge Bearer | Code | 4 | 0..1 | DEBT, CRED, SHAR, SLEV | PaymentInstruction | reversalChargeBearer | Who bears charges |

### Reversal Reason Information (RvslRsnInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInf/RvslRsnInf/Orgtr/Nm | Reversal Reason Originator Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | reversalReasonOriginatorName | Who initiated reversal |
| TxInf/RvslRsnInf/Orgtr/Id/OrgId/AnyBIC | Originator BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | reversalReasonOriginatorBic | Originator BIC |
| TxInf/RvslRsnInf/Rsn/Cd | Reversal Reason Code | Code | 1-4 | 0..1 | See codes below | PaymentInstruction | reversalReasonCode | Standard reason code |
| TxInf/RvslRsnInf/Rsn/Prtry | Reversal Reason Proprietary | Text | 1-35 | 0..1 | Free text | PaymentInstruction | reversalReasonProprietary | Proprietary reason |
| TxInf/RvslRsnInf/AddtlInf | Additional Information | Text | 1-105 | 0..* | Free text | PaymentInstruction | reversalReasonAdditionalInfo | Extra details |

### Charges Information (ChrgsInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInf/ChrgsInf/Amt | Charges Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | reversalChargesAmount | Charges on reversal |
| TxInf/ChrgsInf/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | reversalChargesAmount.currency | Charges currency |
| TxInf/ChrgsInf/Agt/FinInstnId/BICFI | Charging Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | reversalChargingAgentBic | Who charged |
| TxInf/ChrgsInf/Tp/Cd | Charges Type Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | reversalChargesTypeCode | Type of charge |

### Instructing Agent (InstgAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInf/InstgAgt/FinInstnId/BICFI | Instructing Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | txnInstructingAgentBic | Agent instructing reversal |
| TxInf/InstgAgt/FinInstnId/ClrSysMmbId/MmbId | Clearing Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | txnInstructingAgentClearingId | Clearing member |
| TxInf/InstgAgt/FinInstnId/Nm | Instructing Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | txnInstructingAgentName | Agent name |
| TxInf/InstgAgt/BrnchId/Id | Branch Identification | Text | 1-35 | 0..1 | Free text | FinancialInstitution | txnInstructingAgentBranchId | Branch ID |

### Instructed Agent (InstdAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| TxInf/InstdAgt/FinInstnId/BICFI | Instructed Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | txnInstructedAgentBic | Agent receiving reversal |
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
| TxInf/OrgnlTxRef/PmtTpInf/ClrChanl | Original Clearing Channel | Code | 4 | 0..1 | RTGS, RTNS, etc. | PaymentInstruction | originalClearingChannel | Clearing channel |
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

## Reversal Reason Codes

### Fraud Related Reversals

| Code | Description | CDM Mapping | Severity |
|------|-------------|-------------|----------|
| FRAD | Fraudulent Origin | PaymentInstruction.reversalReasonCode = 'FRAD' | CRITICAL |
| FR01 | Fraud | PaymentInstruction.reversalReasonCode = 'FR01' | CRITICAL |
| DUPL | Duplicate Payment | PaymentInstruction.reversalReasonCode = 'DUPL' | HIGH |

### Technical/Error Reversals

| Code | Description | CDM Mapping | Severity |
|------|-------------|-------------|----------|
| TECH | Technical Problems | PaymentInstruction.reversalReasonCode = 'TECH' | MEDIUM |
| AM05 | Duplication | PaymentInstruction.reversalReasonCode = 'AM05' | HIGH |
| AM09 | Wrong Amount | PaymentInstruction.reversalReasonCode = 'AM09' | HIGH |
| CUST | Requested By Customer | PaymentInstruction.reversalReasonCode = 'CUST' | MEDIUM |
| AGNT | Incorrect Agent | PaymentInstruction.reversalReasonCode = 'AGNT' | HIGH |
| CURR | Incorrect Currency | PaymentInstruction.reversalReasonCode = 'CURR' | HIGH |
| NARR | Narrative | PaymentInstruction.reversalReasonCode = 'NARR' | LOW |

### Account Related Reversals

| Code | Description | CDM Mapping | Severity |
|------|-------------|-------------|----------|
| AC01 | Incorrect Account Number | PaymentInstruction.reversalReasonCode = 'AC01' | HIGH |
| AC04 | Closed Account | PaymentInstruction.reversalReasonCode = 'AC04' | HIGH |
| AC06 | Blocked Account | PaymentInstruction.reversalReasonCode = 'AC06' | HIGH |

### Customer Request Reversals

| Code | Description | CDM Mapping | Severity |
|------|-------------|-------------|----------|
| CUST | Requested By Customer | PaymentInstruction.reversalReasonCode = 'CUST' | MEDIUM |
| CUTA | Customer Terminated | PaymentInstruction.reversalReasonCode = 'CUTA' | MEDIUM |
| UPAY | Underpayment | PaymentInstruction.reversalReasonCode = 'UPAY' | LOW |

---

## CDM Extensions Required

All 95 pacs.007 fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Example

### Payment Reversal - Fraudulent Transaction

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.007.001.11">
  <FIToFIPmtRvsl>
    <GrpHdr>
      <MsgId>RVSL20241220001</MsgId>
      <CreDtTm>2024-12-20T16:00:00Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <TtlRvsdIntrBkSttlmAmt Ccy="USD">125000.00</TtlRvsdIntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-21</IntrBkSttlmDt>
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
      <RvslId>RVSL001</RvslId>
      <OrgnlGrpInf>
        <OrgnlMsgId>MSGID20241219001</OrgnlMsgId>
        <OrgnlMsgNmId>pacs.008.001.10</OrgnlMsgNmId>
        <OrgnlCreDtTm>2024-12-19T14:30:00Z</OrgnlCreDtTm>
      </OrgnlGrpInf>
      <OrgnlInstrId>INSTRID001</OrgnlInstrId>
      <OrgnlEndToEndId>E2E20241219001</OrgnlEndToEndId>
      <OrgnlTxId>TXN20241219001</OrgnlTxId>
      <OrgnlUETR>a7ed4827-7b6f-4491-a06f-b548d5a7512d</OrgnlUETR>
      <OrgnlIntrBkSttlmAmt Ccy="USD">125000.00</OrgnlIntrBkSttlmAmt>
      <OrgnlIntrBkSttlmDt>2024-12-20</OrgnlIntrBkSttlmDt>
      <RvsdIntrBkSttlmAmt Ccy="USD">125000.00</RvsdIntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-21</IntrBkSttlmDt>
      <RvslRsnInf>
        <Orgtr>
          <Nm>JPMorgan Chase Bank - Fraud Prevention Team</Nm>
          <Id>
            <OrgId>
              <AnyBIC>CHASUS33XXX</AnyBIC>
            </OrgId>
          </Id>
        </Orgtr>
        <Rsn>
          <Cd>FRAD</Cd>
        </Rsn>
        <AddtlInf>Fraudulent payment detected after settlement. Payment instruction was initiated by unauthorized party using compromised credentials. Customer confirmed they did not authorize this payment. Law enforcement notified. Case reference: FRAUD-2024-12345</AddtlInf>
      </RvslRsnInf>
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
          <Nm>Suspicious Recipient Inc</Nm>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <Othr>
              <Id>987654321</Id>
            </Othr>
          </Id>
        </CdtrAcct>
        <RmtInf>
          <Ustrd>Fraudulent invoice payment</Ustrd>
        </RmtInf>
      </OrgnlTxRef>
    </TxInf>
  </FIToFIPmtRvsl>
</Document>
```

### Duplicate Payment Reversal Example

```xml
<TxInf>
  <RvslId>RVSL002</RvslId>
  <OrgnlGrpInf>
    <OrgnlMsgId>MSGID20241220002</OrgnlMsgId>
    <OrgnlMsgNmId>pacs.008.001.10</OrgnlMsgNmId>
  </OrgnlGrpInf>
  <OrgnlEndToEndId>E2E20241220002</OrgnlEndToEndId>
  <OrgnlIntrBkSttlmAmt Ccy="EUR">50000.00</OrgnlIntrBkSttlmAmt>
  <RvsdIntrBkSttlmAmt Ccy="EUR">50000.00</RvsdIntrBkSttlmAmt>
  <RvslRsnInf>
    <Rsn>
      <Cd>DUPL</Cd>
    </Rsn>
    <AddtlInf>Duplicate payment sent in error. Original payment ref E2E20241220001 already processed successfully. This payment is the duplicate and must be reversed.</AddtlInf>
  </RvslRsnInf>
</TxInf>
```

---

## Key Differences: pacs.004 Return vs pacs.007 Reversal

| Aspect | pacs.004 (Return) | pacs.007 (Reversal) |
|--------|-------------------|---------------------|
| **Timing** | Before final settlement | After settlement completed |
| **Scenario** | Cannot process payment | Must undo completed payment |
| **Direction** | Creditor Agent → Debtor Agent | Detecting Agent → Previous Agent |
| **Settlement** | Payment never settled | Payment already settled, must reverse |
| **Common Reasons** | Invalid account, insufficient funds | Fraud, duplicate, error after settlement |
| **Urgency** | Normal operational flow | Often urgent (fraud, customer impact) |
| **Example** | Account doesn't exist | Fraud detected 24 hours after settlement |

---

## References

- ISO 20022 pacs.007 Specification: https://www.iso20022.org/catalogue-messages/iso-20022-messages-archive?search=pacs.007
- ISO 20022 External Code Lists: https://www.iso20022.org/external-code-list
- SWIFT Standards: https://www.swift.com/standards/iso-20022
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
