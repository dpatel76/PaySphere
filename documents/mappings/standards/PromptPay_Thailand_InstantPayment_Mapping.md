# PromptPay - Thailand Instant Payment System
## Complete Field Mapping to GPS CDM

**Payment System:** PromptPay
**Country:** Thailand
**Operator:** National ITMX Co., Ltd. (ITMX)
**Usage:** Real-time instant payments in Thai Baht (THB)
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 48 fields mapped)

---

## System Overview

PromptPay is Thailand's national e-payment scheme that enables real-time fund transfers using mobile phone numbers, National ID numbers, or e-Wallet IDs as proxies.

**Key Characteristics:**
- Currency: THB (Thai Baht)
- Settlement: Real-time (< 15 seconds)
- Operating hours: 24/7/365
- Transaction limit: THB 2,000,000 per transaction (varies by bank)
- Message format: ISO 20022 XML

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total PromptPay Fields** | 48 | 100% |
| **Mapped to CDM** | 48 | 100% |
| **Direct Mapping** | 45 | 94% |
| **Derived/Calculated** | 2 | 4% |
| **Reference Data Lookup** | 1 | 2% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Transaction Identification

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | Transaction Reference Number | Text | 35 | Yes | Alphanumeric | PaymentInstruction | transactionId | Unique transaction ID |
| 2 | End to End ID | Text | 35 | Yes | Alphanumeric | PaymentInstruction | endToEndId | E2E identifier |
| 3 | Message ID | Text | 35 | Yes | Alphanumeric | PaymentInstruction | messageId | Message identifier |
| 4 | PromptPay Reference Number | Text | 35 | Yes | Alphanumeric | PaymentInstruction | promptPayReferenceId | PromptPay system ID |

### Amount and Currency

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 5 | Amount | Decimal | 18,2 | Yes | Numeric | PaymentInstruction | instructedAmount.amount | Transaction amount |
| 6 | Currency | Code | 3 | Yes | THB | PaymentInstruction | instructedAmount.currency | Always THB |

### Payer (Debtor) Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 7 | Payer Proxy Type | Code | 10 | Yes | MSISDN, NATID, EWAL, ACCT | Account | promptPayProxyType | Proxy identifier type |
| 8 | Payer Proxy ID | Text | 50 | Yes | See proxy types | Account | promptPayProxyId | Mobile/NatID/eWallet |
| 9 | Payer name | Text | 140 | Yes | Thai/English | Party | name | Payer name |
| 10 | Payer account number | Text | 34 | Yes | Numeric | Account | accountNumber | Account identifier |
| 11 | Payer identification type | Code | 4 | Yes | NIDN, CCPT, TXID | Party | identificationType | ID type |
| 12 | Payer identification number | Text | 35 | Yes | 13 digits (NIDN) | Party | identificationNumber | National ID |
| 13 | Payer bank identification | Text | 11 | Yes | Thai Bank Code | FinancialInstitution | bankCode | 3-digit bank code |
| 14 | Payer bank name | Text | 140 | No | Free text | FinancialInstitution | name | Bank name |
| 15 | Payer mobile number | Text | 15 | Cond | 66XXXXXXXXX | Party | mobilePhoneNumber | If proxy is mobile |

### Payee (Creditor) Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 16 | Payee Proxy Type | Code | 10 | Yes | MSISDN, NATID, EWAL, ACCT | Account | promptPayProxyType | Proxy identifier type |
| 17 | Payee Proxy ID | Text | 50 | Yes | See proxy types | Account | promptPayProxyId | Mobile/NatID/eWallet |
| 18 | Payee name | Text | 140 | Yes | Thai/English | Party | name | Payee name |
| 19 | Payee account number | Text | 34 | Yes | Numeric | Account | accountNumber | Account identifier |
| 20 | Payee identification type | Code | 4 | Yes | NIDN, CCPT, TXID | Party | identificationType | ID type |
| 21 | Payee identification number | Text | 35 | Yes | 13 digits (NIDN) | Party | identificationNumber | National ID or Tax ID |
| 22 | Payee bank identification | Text | 11 | Yes | Thai Bank Code | FinancialInstitution | bankCode | 3-digit bank code |
| 23 | Payee bank name | Text | 140 | No | Free text | FinancialInstitution | name | Bank name |
| 24 | Payee mobile number | Text | 15 | Cond | 66XXXXXXXXX | Party | mobilePhoneNumber | If proxy is mobile |

### Transaction Timing

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 25 | Creation date/time | DateTime | 24 | Yes | ISO 8601 | PaymentInstruction | creationTimestamp | YYYY-MM-DDTHH:MM:SS.sssZ |
| 26 | Interbank settlement date | Date | 10 | Yes | YYYY-MM-DD | PaymentInstruction | interbankSettlementDate | Settlement date |
| 27 | Request timestamp | DateTime | 24 | Yes | ISO 8601 | PaymentInstruction | requestTimestamp | Request time |
| 28 | Response timestamp | DateTime | 24 | Yes | ISO 8601 | PaymentInstruction | responseTimestamp | Response time |

### Remittance Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 29 | Remittance information | Text | 140 | No | Thai/English | PaymentInstruction | remittanceInformation | Unstructured remittance |
| 30 | Purpose code | Code | 4 | No | See purpose codes | PaymentInstruction | purposeCode | Payment purpose |

### Payment Type and Channel

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 31 | Service type | Code | 4 | Yes | P2P, P2M, B2P, B2B | PaymentInstruction | serviceType | Type of payment |
| 32 | Channel code | Code | 4 | No | MOBL, INTB, ATM, BRNC | PaymentInstruction | channelCode | Channel used |
| 33 | Local instrument | Code | 35 | No | PROMPTPAY | PaymentInstruction | localInstrument | PromptPay indicator |

### Status and Response

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 34 | Transaction status | Code | 4 | Yes | ACCP, ACSC, RJCT, PDNG | PaymentInstruction | transactionStatus | Status code |
| 35 | Status reason code | Code | 4 | Cond | See reason codes | PaymentInstruction | statusReasonCode | If rejected |
| 36 | Status reason | Text | 140 | Cond | Free text | PaymentInstruction | statusReasonDescription | Reason details |
| 37 | Response code | Code | 4 | Yes | 0000, 0001, etc. | PaymentInstruction | responseCode | PromptPay response code |

### Settlement Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 38 | Settlement method | Code | 4 | Yes | INDA | PaymentInstruction | settlementMethod | Instructed agent |
| 39 | Clearing system | Code | 10 | Yes | PROMPTPAY | PaymentInstruction | clearingSystem | PromptPay system |
| 40 | ITMX Transaction ID | Text | 35 | Yes | Alphanumeric | PaymentInstruction | itmxTransactionId | ITMX system reference |

### QR Code Information (if applicable)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 41 | QR type | Code | 10 | Cond | STATIC, DYNAMIC | PaymentInstruction | qrCodeType | QR type |
| 42 | QR code data | Text | 512 | Cond | EMV format | PaymentInstruction | qrCodeData | Thai QR payload |
| 43 | Merchant ID | Text | 15 | Cond | 15 digits | Party | merchantId | Tax ID for merchant |
| 44 | Merchant name | Text | 25 | Cond | Free text | Party | merchantName | For QR payments |

### Additional Metadata

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 45 | Instruction priority | Code | 4 | No | HIGH, NORM | PaymentInstruction | priority | Priority indicator |
| 46 | Charges bearer | Code | 4 | No | DEBT, CRED, SHAR | PaymentInstruction | chargesBearer | Who pays charges |
| 47 | BOT Reporting Code | Code | 5 | No | See codes | PaymentInstruction | botReportingCode | Bank of Thailand reporting |
| 48 | Reference 1 | Text | 35 | No | Free text | PaymentInstruction | additionalReference1 | Additional reference |

---

## Code Lists

### PromptPay Proxy Types

| Code | Description | Format | CDM Mapping |
|------|-------------|--------|-------------|
| MSISDN | Mobile phone number | 66XXXXXXXXX (10 digits after 66) | Account.promptPayProxyType = 'MSISDN' |
| NATID | National ID number | 13 digits | Account.promptPayProxyType = 'NATID' |
| EWAL | e-Wallet ID | Varies | Account.promptPayProxyType = 'EWAL' |
| ACCT | Account number | Bank-specific | Account.promptPayProxyType = 'ACCT' |

### Identification Types

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| NIDN | National Identity Number | Party.identificationType = 'NIDN' |
| CCPT | Passport | Party.identificationType = 'CCPT' |
| TXID | Tax Identification Number | Party.identificationType = 'TXID' |

### Service Types

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| P2P | Person to Person | PaymentInstruction.serviceType = 'P2P' |
| P2M | Person to Merchant | PaymentInstruction.serviceType = 'P2M' |
| B2P | Business to Person | PaymentInstruction.serviceType = 'B2P' |
| B2B | Business to Business | PaymentInstruction.serviceType = 'B2B' |

### Transaction Status Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| ACCP | Accepted Customer Profile | PaymentInstruction.transactionStatus = 'ACCP' |
| ACSC | Accepted Settlement Completed | PaymentInstruction.transactionStatus = 'ACSC' |
| RJCT | Rejected | PaymentInstruction.transactionStatus = 'RJCT' |
| PDNG | Pending | PaymentInstruction.transactionStatus = 'PDNG' |

### Status Reason Codes (Selected)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| AC01 | Incorrect account number | PaymentInstruction.statusReasonCode = 'AC01' |
| AC03 | Invalid creditor account number | PaymentInstruction.statusReasonCode = 'AC03' |
| AC04 | Closed account | PaymentInstruction.statusReasonCode = 'AC04' |
| AC06 | Blocked account | PaymentInstruction.statusReasonCode = 'AC06' |
| AG01 | Transaction forbidden | PaymentInstruction.statusReasonCode = 'AG01' |
| AM04 | Insufficient funds | PaymentInstruction.statusReasonCode = 'AM04' |
| BE05 | Unrecognized party | PaymentInstruction.statusReasonCode = 'BE05' |
| TECH | Technical problem | PaymentInstruction.statusReasonCode = 'TECH' |

### Response Codes (Selected)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 0000 | Success | PaymentInstruction.responseCode = '0000' |
| 0001 | Pending | PaymentInstruction.responseCode = '0001' |
| 1001 | Invalid proxy | PaymentInstruction.responseCode = '1001' |
| 1002 | Proxy not found | PaymentInstruction.responseCode = '1002' |
| 2001 | Insufficient balance | PaymentInstruction.responseCode = '2001' |
| 3001 | System error | PaymentInstruction.responseCode = '3001' |

### Purpose Codes (Selected)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| GDDS | Goods | PaymentInstruction.purposeCode = 'GDDS' |
| SERV | Services | PaymentInstruction.purposeCode = 'SERV' |
| SALA | Salary | PaymentInstruction.purposeCode = 'SALA' |
| OTHR | Other | PaymentInstruction.purposeCode = 'OTHR' |

---

## CDM Extensions Required

All 48 PromptPay fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>PP20241220143025001</MsgId>
      <CreDtTm>2024-12-20T14:30:25.000Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <SttlmInf>
        <SttlmMtd>INDA</SttlmMtd>
        <ClrSys>
          <Cd>PROMPTPAY</Cd>
        </ClrSys>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>ITMX20241220143025001</InstrId>
        <EndToEndId>E2E20241220143025001</EndToEndId>
        <TxId>TXN20241220143025001</TxId>
      </PmtId>
      <IntrBkSttlmAmt Ccy="THB">1500.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <DbtrAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>002</MmbId>
          </ClrSysMmbId>
          <Nm>Bangkok Bank Public Company Limited</Nm>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>สมชาย ใจดี</Nm>
        <Id>
          <PrvtId>
            <Othr>
              <Id>1234567890123</Id>
              <SchmeNm>
                <Cd>NIDN</Cd>
              </SchmeNm>
            </Othr>
          </PrvtId>
        </Id>
        <CtctDtls>
          <MobNb>66812345678</MobNb>
        </CtctDtls>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>1234567890</Id>
          </Othr>
        </Id>
        <Prxy>
          <Tp>
            <Cd>MSISDN</Cd>
          </Tp>
          <Id>66812345678</Id>
        </Prxy>
      </DbtrAcct>
      <CdtrAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>014</MmbId>
          </ClrSysMmbId>
          <Nm>Siam Commercial Bank Public Company Limited</Nm>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>สมหญิง รักดี</Nm>
        <Id>
          <PrvtId>
            <Othr>
              <Id>9876543210987</Id>
              <SchmeNm>
                <Cd>NIDN</Cd>
              </SchmeNm>
            </Othr>
          </PrvtId>
        </Id>
        <CtctDtls>
          <MobNb>66898765432</MobNb>
        </CtctDtls>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>9876543210</Id>
          </Othr>
        </Id>
        <Prxy>
          <Tp>
            <Cd>MSISDN</Cd>
          </Tp>
          <Id>66898765432</Id>
        </Prxy>
      </CdtrAcct>
      <RmtInf>
        <Ustrd>ค่าอาหารกลางวัน</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
```

---

## References

- Bank of Thailand - PromptPay: https://www.bot.or.th/English/PaymentSystems/PSServices/PromptPay/Pages/default.aspx
- National ITMX: https://www.itmx.co.th/
- PromptPay Specifications: https://www.bot.or.th/English/PaymentSystems/PolicyPS/Documents/PromptPay_Handbook_EN.pdf
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
