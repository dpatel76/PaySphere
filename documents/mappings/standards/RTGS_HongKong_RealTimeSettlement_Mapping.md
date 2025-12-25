# RTGS - Hong Kong Real Time Gross Settlement System
## Complete Field Mapping to GPS CDM

**Payment System:** RTGS (Real Time Gross Settlement)
**Country:** Hong Kong SAR
**Operator:** Hong Kong Monetary Authority (HKMA)
**Usage:** Real-time large-value and time-critical payment system in Hong Kong Dollar (HKD)
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 62 fields mapped)

---

## System Overview

The Hong Kong Dollar RTGS system is a real-time gross settlement payment system for the Hong Kong Dollar. It settles interbank payments on a transaction-by-transaction basis in real-time throughout the day.

**Key Characteristics:**
- Currency: HKD (Hong Kong Dollar)
- Settlement: Real-time gross settlement
- Operating hours:
  - Normal: 08:30-18:30 (Hong Kong Time)
  - Extended: Until 02:00 (next day) for USD/CNY FX PvP
- Transaction limit: No limit (typically > HKD 500,000)
- Message format: ISO 20022 XML / SWIFT MT
- Integration: Connected to FPS (Faster Payment System) for retail payments

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total RTGS Fields** | 62 | 100% |
| **Mapped to CDM** | 62 | 100% |
| **Direct Mapping** | 58 | 94% |
| **Derived/Calculated** | 3 | 5% |
| **Reference Data Lookup** | 1 | 1% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Transaction Identification

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | Message Identification | Text | 35 | Yes | Alphanumeric | PaymentInstruction | messageId | Message identifier |
| 2 | End to End Identification | Text | 35 | Yes | Alphanumeric | PaymentInstruction | endToEndId | E2E identifier |
| 3 | Transaction Identification | Text | 35 | Yes | Alphanumeric | PaymentInstruction | transactionId | Transaction ID |
| 4 | Instruction Identification | Text | 35 | Yes | Alphanumeric | PaymentInstruction | instructionId | Instruction ID |
| 5 | RTGS Reference Number | Text | 16 | Yes | System generated | PaymentInstruction | rtgsReferenceNumber | RTGS system ID |
| 6 | Sender's Reference | Text | 16 | Yes | Free text | PaymentInstruction | sendersReference | Sender reference |

### Amount and Currency

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 7 | Instructed Amount | Decimal | 18,2 | Yes | Numeric | PaymentInstruction | instructedAmount.amount | Transaction amount |
| 8 | Currency | Code | 3 | Yes | HKD | PaymentInstruction | instructedAmount.currency | Always HKD |
| 9 | Interbank Settlement Amount | Decimal | 18,2 | Yes | Numeric | PaymentInstruction | interbankSettlementAmount | Settlement amount |

### Payer (Debtor) Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 10 | Debtor name | Text | 140 | Yes | Free text | Party | name | Payer name |
| 11 | Debtor account number | Text | 34 | Yes | Alphanumeric | Account | accountNumber | Account identifier |
| 12 | Debtor account name | Text | 140 | No | Free text | Account | accountName | Account name |
| 13 | Debtor identification type | Code | 4 | No | HKID, CCPT, TXID, BREN | Party | identificationType | ID type |
| 14 | Debtor identification number | Text | 35 | No | Free text | Party | identificationNumber | HKID/BR number |
| 15 | Debtor address line 1 | Text | 70 | No | Free text | Party | addressLine1 | Address line 1 |
| 16 | Debtor address line 2 | Text | 70 | No | Free text | Party | addressLine2 | Address line 2 |
| 17 | Debtor city | Text | 35 | No | Free text | Party | city | City |
| 18 | Debtor country | Code | 2 | No | HK | Party | country | Country code |
| 19 | Debtor agent BIC | Code | 11 | Yes | SWIFT BIC | FinancialInstitution | bicCode | Bank identifier |
| 20 | Debtor agent name | Text | 140 | No | Free text | FinancialInstitution | name | Bank name |
| 21 | Debtor agent clearing code | Text | 3 | Yes | 3-digit code | FinancialInstitution | hkClearingCode | HK bank code |

### Payee (Creditor) Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 22 | Creditor name | Text | 140 | Yes | Free text | Party | name | Payee name |
| 23 | Creditor account number | Text | 34 | Yes | Alphanumeric | Account | accountNumber | Account identifier |
| 24 | Creditor account name | Text | 140 | No | Free text | Account | accountName | Account name |
| 25 | Creditor identification type | Code | 4 | No | HKID, CCPT, TXID, BREN | Party | identificationType | ID type |
| 26 | Creditor identification number | Text | 35 | No | Free text | Party | identificationNumber | HKID/BR number |
| 27 | Creditor address line 1 | Text | 70 | No | Free text | Party | addressLine1 | Address line 1 |
| 28 | Creditor address line 2 | Text | 70 | No | Free text | Party | addressLine2 | Address line 2 |
| 29 | Creditor city | Text | 35 | No | Free text | Party | city | City |
| 30 | Creditor country | Code | 2 | No | HK | Party | country | Country code |
| 31 | Creditor agent BIC | Code | 11 | Yes | SWIFT BIC | FinancialInstitution | bicCode | Bank identifier |
| 32 | Creditor agent name | Text | 140 | No | Free text | FinancialInstitution | name | Bank name |
| 33 | Creditor agent clearing code | Text | 3 | Yes | 3-digit code | FinancialInstitution | hkClearingCode | HK bank code |

### Transaction Timing

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 34 | Creation date/time | DateTime | 24 | Yes | ISO 8601 | PaymentInstruction | creationTimestamp | YYYY-MM-DDTHH:MM:SS.sssZ |
| 35 | Value date | Date | 10 | Yes | YYYY-MM-DD | PaymentInstruction | valueDate | Value date |
| 36 | Interbank settlement date | Date | 10 | Yes | YYYY-MM-DD | PaymentInstruction | interbankSettlementDate | Settlement date |
| 37 | Settlement timestamp | DateTime | 24 | No | ISO 8601 | PaymentInstruction | settlementTimestamp | Actual settlement time |

### Remittance Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 38 | Remittance information unstructured | Text | 140 | No | Free text | PaymentInstruction | remittanceInformation | Unstructured remittance |
| 39 | Purpose code | Code | 4 | No | See purpose codes | PaymentInstruction | purposeCode | Payment purpose |
| 40 | Category purpose | Code | 4 | No | See category codes | PaymentInstruction | categoryPurpose | Category purpose |

### Payment Type and Priority

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 41 | Payment type information | Code | 3 | No | See payment types | PaymentInstruction | paymentTypeInformation | Type of payment |
| 42 | Local instrument | Code | 35 | No | RTGS, FPS | PaymentInstruction | localInstrument | System indicator |
| 43 | Service level code | Code | 4 | Yes | URGP | PaymentInstruction | serviceLevelCode | Urgent payment |
| 44 | Instruction priority | Code | 4 | No | HIGH, NORM | PaymentInstruction | priority | Priority indicator |
| 45 | Payment priority | Code | 1 | No | 1, 2, 3 | PaymentInstruction | paymentPriority | RTGS priority |

### Status and Response

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 46 | Transaction status | Code | 4 | Yes | ACCP, ACSC, RJCT | PaymentInstruction | transactionStatus | Status code |
| 47 | Status reason code | Code | 4 | Cond | See reason codes | PaymentInstruction | statusReasonCode | If rejected |
| 48 | Status reason information | Text | 105 | Cond | Free text | PaymentInstruction | statusReasonDescription | Reason details |

### Settlement Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 49 | Settlement method | Code | 4 | Yes | INDA | PaymentInstruction | settlementMethod | Instructed agent |
| 50 | Clearing system | Code | 5 | Yes | HKRTGS | PaymentInstruction | clearingSystem | HK RTGS system |
| 51 | Clearing channel | Code | 3 | No | RTG, ILF | PaymentInstruction | clearingChannel | Settlement channel |

### Charges Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 52 | Charge bearer | Code | 4 | No | DEBT, CRED, SHAR | PaymentInstruction | chargesBearer | Who pays charges |
| 53 | Charge amount | Decimal | 18,2 | No | Numeric | PaymentInstruction | chargeAmount | Charge amount |

### Intermediary Bank Information (if applicable)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 54 | Intermediary agent BIC | Code | 11 | No | SWIFT BIC | FinancialInstitution | intermediaryAgentBic | Intermediary bank BIC |
| 55 | Intermediary agent name | Text | 140 | No | Free text | FinancialInstitution | intermediaryAgentName | Intermediary bank name |
| 56 | Intermediary agent clearing code | Text | 3 | No | 3-digit code | FinancialInstitution | intermediaryAgentClearingCode | HK bank code |

### Additional Metadata

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 57 | Instructing agent BIC | Code | 11 | No | SWIFT BIC | FinancialInstitution | instructingAgentBic | Instructing bank |
| 58 | Instructed agent BIC | Code | 11 | No | SWIFT BIC | FinancialInstitution | instructedAgentBic | Instructed bank |
| 59 | Ultimate debtor name | Text | 140 | No | Free text | Party | ultimateDebtorName | Ultimate payer |
| 60 | Ultimate creditor name | Text | 140 | No | Free text | Party | ultimateCreditorName | Ultimate payee |
| 61 | Related reference | Text | 35 | No | Alphanumeric | PaymentInstruction | relatedReference | Related message ref |
| 62 | Channel code | Code | 4 | No | MOBL, INTB, BRNC | PaymentInstruction | channelCode | Originating channel |

---

## Code Lists

### Identification Types

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| HKID | Hong Kong Identity Card | Party.identificationType = 'HKID' |
| CCPT | Passport | Party.identificationType = 'CCPT' |
| TXID | Tax Identification Number | Party.identificationType = 'TXID' |
| BREN | Business Registration Number | Party.identificationType = 'BREN' |

### Transaction Status Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| ACCP | Accepted Customer Profile | PaymentInstruction.transactionStatus = 'ACCP' |
| ACSC | Accepted Settlement Completed | PaymentInstruction.transactionStatus = 'ACSC' |
| ACTC | Accepted Technical Validation | PaymentInstruction.transactionStatus = 'ACTC' |
| RJCT | Rejected | PaymentInstruction.transactionStatus = 'RJCT' |
| PDNG | Pending | PaymentInstruction.transactionStatus = 'PDNG' |

### Status Reason Codes (Selected)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| AC01 | Incorrect account number | PaymentInstruction.statusReasonCode = 'AC01' |
| AC03 | Invalid creditor account | PaymentInstruction.statusReasonCode = 'AC03' |
| AC04 | Closed account | PaymentInstruction.statusReasonCode = 'AC04' |
| AC06 | Blocked account | PaymentInstruction.statusReasonCode = 'AC06' |
| AG01 | Transaction forbidden | PaymentInstruction.statusReasonCode = 'AG01' |
| AG02 | Invalid bank operation code | PaymentInstruction.statusReasonCode = 'AG02' |
| AM04 | Insufficient funds | PaymentInstruction.statusReasonCode = 'AM04' |
| AM05 | Duplicate payment | PaymentInstruction.statusReasonCode = 'AM05' |
| BE05 | Unrecognized initiating party | PaymentInstruction.statusReasonCode = 'BE05' |
| DT01 | Invalid date | PaymentInstruction.statusReasonCode = 'DT01' |

### Purpose Codes (Selected)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| BONU | Bonus payment | PaymentInstruction.purposeCode = 'BONU' |
| CASH | Cash management transfer | PaymentInstruction.purposeCode = 'CASH' |
| DVPM | Delivery vs payment | PaymentInstruction.purposeCode = 'DVPM' |
| INTC | Intra-company payment | PaymentInstruction.purposeCode = 'INTC' |
| SALA | Salary payment | PaymentInstruction.purposeCode = 'SALA' |
| SECU | Securities purchase/sale | PaymentInstruction.purposeCode = 'SECU' |
| SUPP | Supplier payment | PaymentInstruction.purposeCode = 'SUPP' |
| TREA | Treasury payment | PaymentInstruction.purposeCode = 'TREA' |

### Category Purpose Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CASH | Cash management transfer | PaymentInstruction.categoryPurpose = 'CASH' |
| CORT | Corporate trade | PaymentInstruction.categoryPurpose = 'CORT' |
| INTC | Intra-company | PaymentInstruction.categoryPurpose = 'INTC' |
| TREA | Treasury | PaymentInstruction.categoryPurpose = 'TREA' |

### Clearing Channels

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| RTG | Real-Time Gross Settlement | PaymentInstruction.clearingChannel = 'RTG' |
| ILF | Intraday Liquidity Facility | PaymentInstruction.clearingChannel = 'ILF' |

### Payment Priority

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 1 | Highest priority | PaymentInstruction.paymentPriority = '1' |
| 2 | Normal priority | PaymentInstruction.paymentPriority = '2' |
| 3 | Lowest priority | PaymentInstruction.paymentPriority = '3' |

---

## CDM Extensions Required

All 62 RTGS fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>RTGS20241220143025</MsgId>
      <CreDtTm>2024-12-20T14:30:25.123+08:00</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <SttlmInf>
        <SttlmMtd>INDA</SttlmMtd>
        <ClrSys>
          <Cd>HKRTGS</Cd>
        </ClrSys>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>INSTR20241220143025</InstrId>
        <EndToEndId>E2E20241220143025</EndToEndId>
        <TxId>TXN20241220143025</TxId>
      </PmtId>
      <PmtTpInf>
        <InstrPrty>HIGH</InstrPrty>
        <SvcLvl>
          <Cd>URGP</Cd>
        </SvcLvl>
        <LclInstrm>
          <Prtry>RTGS</Prtry>
        </LclInstrm>
        <CtgyPurp>
          <Cd>CASH</Cd>
        </CtgyPurp>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="HKD">50000000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <InstdAmt Ccy="HKD">50000000.00</InstdAmt>
      <ChrgBr>SHAR</ChrgBr>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>HSBCHKHHXXX</BICFI>
          <ClrSysMmbId>
            <ClrSysId>
              <Cd>HKNCC</Cd>
            </ClrSysId>
            <MmbId>004</MmbId>
          </ClrSysMmbId>
          <Nm>The Hongkong and Shanghai Banking Corporation Limited</Nm>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>ABC Trading Company Limited</Nm>
        <PstlAdr>
          <AdrLine>18/F, Central Plaza, 18 Harbour Road</AdrLine>
          <AdrLine>Wan Chai</AdrLine>
          <TwnNm>Hong Kong</TwnNm>
          <Ctry>HK</Ctry>
        </PstlAdr>
        <Id>
          <OrgId>
            <Othr>
              <Id>12345678</Id>
              <SchmeNm>
                <Cd>BREN</Cd>
              </SchmeNm>
            </Othr>
          </OrgId>
        </Id>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>004-123456-789</Id>
          </Othr>
        </Id>
        <Nm>ABC Trading Company USD Account</Nm>
      </DbtrAcct>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>BKCHHKHHXXX</BICFI>
          <ClrSysMmbId>
            <ClrSysId>
              <Cd>HKNCC</Cd>
            </ClrSysId>
            <MmbId>012</MmbId>
          </ClrSysMmbId>
          <Nm>Bank of China (Hong Kong) Limited</Nm>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>XYZ Investments Limited</Nm>
        <PstlAdr>
          <AdrLine>Suite 2501, Tower 1, Times Square</AdrLine>
          <AdrLine>Causeway Bay</AdrLine>
          <TwnNm>Hong Kong</TwnNm>
          <Ctry>HK</Ctry>
        </PstlAdr>
        <Id>
          <OrgId>
            <Othr>
              <Id>87654321</Id>
              <SchmeNm>
                <Cd>BREN</Cd>
              </SchmeNm>
            </Othr>
          </OrgId>
        </Id>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>012-987654-321</Id>
          </Othr>
        </Id>
        <Nm>XYZ Investments Corporate Account</Nm>
      </CdtrAcct>
      <Purp>
        <Cd>SECU</Cd>
      </Purp>
      <RmtInf>
        <Ustrd>Payment for securities settlement - Trade Ref: TRD20241220001</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
```

---

## References

- Hong Kong Monetary Authority (HKMA): https://www.hkma.gov.hk/
- RTGS System Overview: https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/financial-market-infrastructure/payment-systems/
- Hong Kong Interbank Clearing Limited (HKICL): https://www.hkicl.com.hk/
- Faster Payment System (FPS): https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/financial-market-infrastructure/payment-systems/faster-payment-system/
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
