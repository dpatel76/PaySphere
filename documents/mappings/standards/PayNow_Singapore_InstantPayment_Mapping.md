# PayNow - Singapore Instant Payment System
## Complete Field Mapping to GPS CDM

**Payment System:** PayNow
**Country:** Singapore
**Operator:** Payments Network Singapore (PayNow)
**Usage:** Real-time instant payments in Singapore Dollars (SGD)
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 51 fields mapped)

---

## System Overview

PayNow is Singapore's instant payment system that enables real-time peer-to-peer (P2P) and peer-to-merchant (P2M) fund transfers using mobile numbers, NRIC/FIN, or UEN as payment identifiers.

**Key Characteristics:**
- Currency: SGD (Singapore Dollar)
- Settlement: Real-time (< 20 seconds)
- Operating hours: 24/7/365
- Transaction limit: SGD 200,000 per transaction (varies by bank)
- Message format: ISO 20022 XML

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total PayNow Fields** | 51 | 100% |
| **Mapped to CDM** | 51 | 100% |
| **Direct Mapping** | 47 | 92% |
| **Derived/Calculated** | 3 | 6% |
| **Reference Data Lookup** | 1 | 2% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Transaction Identification

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | End to End ID | Text | 35 | Yes | Alphanumeric | PaymentInstruction | endToEndId | Unique E2E identifier |
| 2 | Transaction ID | Text | 35 | Yes | Alphanumeric | PaymentInstruction | transactionId | Transaction reference |
| 3 | Message ID | Text | 35 | Yes | Alphanumeric | PaymentInstruction | messageId | Message identifier |
| 4 | PayNow Reference ID | Text | 35 | Yes | Alphanumeric | PaymentInstruction | payNowReferenceId | PayNow system ID |

### Amount and Currency

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 5 | Amount | Decimal | 18,2 | Yes | Numeric | PaymentInstruction | instructedAmount.amount | Transaction amount |
| 6 | Currency | Code | 3 | Yes | SGD | PaymentInstruction | instructedAmount.currency | Always SGD |

### Payer (Debtor) Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 7 | Payer PayNow Proxy Type | Code | 10 | Yes | MOBILE, NRIC, UEN, VPA | Account | payNowProxyType | Proxy identifier type |
| 8 | Payer PayNow Proxy Value | Text | 20 | Yes | See proxy types | Account | payNowProxyValue | Mobile/NRIC/UEN/VPA |
| 9 | Payer name | Text | 140 | Yes | Free text | Party | name | Payer full name |
| 10 | Payer account number | Text | 34 | Yes | Alphanumeric | Account | accountNumber | Account identifier |
| 11 | Payer identification type | Code | 4 | Yes | NRIC, FIN, PASS, TXID | Party | identificationType | ID document type |
| 12 | Payer identification number | Text | 35 | Yes | Alphanumeric | Party | identificationNumber | ID number |
| 13 | Payer bank BIC | Code | 11 | Yes | BIC code | FinancialInstitution | bicCode | Bank identifier |
| 14 | Payer bank name | Text | 140 | No | Free text | FinancialInstitution | name | Bank name |
| 15 | Payer mobile number | Text | 15 | Cond | +65XXXXXXXX | Party | mobilePhoneNumber | If proxy is mobile |

### Payee (Creditor) Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 16 | Payee PayNow Proxy Type | Code | 10 | Yes | MOBILE, NRIC, UEN, VPA | Account | payNowProxyType | Proxy identifier type |
| 17 | Payee PayNow Proxy Value | Text | 20 | Yes | See proxy types | Account | payNowProxyValue | Mobile/NRIC/UEN/VPA |
| 18 | Payee name | Text | 140 | Yes | Free text | Party | name | Payee full name |
| 19 | Payee account number | Text | 34 | Yes | Alphanumeric | Account | accountNumber | Account identifier |
| 20 | Payee identification type | Code | 4 | Yes | NRIC, FIN, PASS, UEN, TXID | Party | identificationType | ID document type |
| 21 | Payee identification number | Text | 35 | Yes | Alphanumeric | Party | identificationNumber | ID number |
| 22 | Payee bank BIC | Code | 11 | Yes | BIC code | FinancialInstitution | bicCode | Bank identifier |
| 23 | Payee bank name | Text | 140 | No | Free text | FinancialInstitution | name | Bank name |
| 24 | Payee mobile number | Text | 15 | Cond | +65XXXXXXXX | Party | mobilePhoneNumber | If proxy is mobile |

### Transaction Timing

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 25 | Creation date/time | DateTime | 24 | Yes | ISO 8601 | PaymentInstruction | creationTimestamp | YYYY-MM-DDTHH:MM:SS.sssZ |
| 26 | Acceptance date/time | DateTime | 24 | Yes | ISO 8601 | PaymentInstruction | acceptanceTimestamp | When accepted |
| 27 | Settlement date/time | DateTime | 24 | Yes | ISO 8601 | PaymentInstruction | settlementTimestamp | When settled |
| 28 | Interbank settlement date | Date | 10 | Yes | YYYY-MM-DD | PaymentInstruction | interbankSettlementDate | Settlement date |

### Remittance Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 29 | Remittance information | Text | 140 | No | Free text | PaymentInstruction | remittanceInformation | Unstructured remittance |
| 30 | Purpose code | Code | 4 | No | See purpose codes | PaymentInstruction | purposeCode | Payment purpose |

### Payment Type and Channel

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 31 | Payment type | Code | 10 | Yes | TRANSFER, PAYMENT | PaymentInstruction | paymentType | Type of payment |
| 32 | Initiation channel | Code | 4 | No | MOBL, INTB, BRNC | PaymentInstruction | channelCode | Channel used |
| 33 | Service level | Code | 4 | Yes | URGP | PaymentInstruction | serviceLevelCode | Urgent payment |

### Status and Response

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 34 | Transaction status | Code | 4 | Yes | ACCP, ACTC, ACSC, RJCT | PaymentInstruction | transactionStatus | Status code |
| 35 | Status reason code | Code | 4 | Cond | See reason codes | PaymentInstruction | statusReasonCode | If rejected/returned |
| 36 | Status reason description | Text | 105 | Cond | Free text | PaymentInstruction | statusReasonDescription | Reason details |

### Settlement Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 37 | Settlement method | Code | 4 | Yes | INDA | PaymentInstruction | settlementMethod | Instructed agent |
| 38 | Clearing system | Code | 5 | Yes | PAYNOW | PaymentInstruction | clearingSystem | PayNow system |
| 39 | MEPS+ Reference | Text | 35 | No | Alphanumeric | PaymentInstruction | mepsReferenceId | MEPS+ system reference |

### QR Code Information (if applicable)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 40 | QR code type | Code | 10 | Cond | STATIC, DYNAMIC | PaymentInstruction | qrCodeType | QR type |
| 41 | QR code data | Text | 512 | Cond | SGQR format | PaymentInstruction | qrCodeData | SGQR payload |
| 42 | Merchant category code | Code | 4 | Cond | 4 digits | Party | merchantCategoryCode | For merchant payments |
| 43 | Merchant name | Text | 25 | Cond | Free text | Party | merchantName | For QR payments |

### Regulatory and Compliance

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 44 | Regulatory reporting code | Code | 3 | No | See codes | PaymentInstruction | regulatoryReportingCode | MAS reporting |
| 45 | Tax reference | Text | 35 | No | Free text | PaymentInstruction | taxReference | Tax reference |

### Additional Metadata

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 46 | Instruction priority | Code | 4 | No | HIGH, NORM | PaymentInstruction | priority | Priority indicator |
| 47 | Charges bearer | Code | 4 | No | DEBT, CRED, SHAR, SLEV | PaymentInstruction | chargesBearer | Who pays charges |
| 48 | Number of transactions | Integer | 15 | No | Numeric | PaymentInstruction | numberOfTransactions | Batch count |
| 49 | Instructed agent BIC | Code | 11 | No | BIC code | FinancialInstitution | instructedAgentBic | Instructed bank |
| 50 | Instructing agent BIC | Code | 11 | No | BIC code | FinancialInstitution | instructingAgentBic | Instructing bank |
| 51 | Ultimate debtor name | Text | 140 | No | Free text | Party | ultimateDebtorName | Ultimate payer |

---

## Code Lists

### PayNow Proxy Types

| Code | Description | Format | CDM Mapping |
|------|-------------|--------|-------------|
| MOBILE | Mobile phone number | +65XXXXXXXX | Account.payNowProxyType = 'MOBILE' |
| NRIC | National Registration ID | SXXXXXXXA | Account.payNowProxyType = 'NRIC' |
| UEN | Unique Entity Number | XXXXXXXXXXA | Account.payNowProxyType = 'UEN' |
| VPA | Virtual Payment Address | user@bank | Account.payNowProxyType = 'VPA' |

### Identification Types

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| NRIC | National Registration Identity Card | Party.identificationType = 'NRIC' |
| FIN | Foreign Identification Number | Party.identificationType = 'FIN' |
| PASS | Passport | Party.identificationType = 'PASS' |
| UEN | Unique Entity Number | Party.identificationType = 'UEN' |
| TXID | Tax Identification | Party.identificationType = 'TXID' |

### Transaction Status Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| ACCP | Accepted Customer Profile | PaymentInstruction.transactionStatus = 'ACCP' |
| ACTC | Accepted Technical Validation | PaymentInstruction.transactionStatus = 'ACTC' |
| ACSC | Accepted Settlement Completed | PaymentInstruction.transactionStatus = 'ACSC' |
| RJCT | Rejected | PaymentInstruction.transactionStatus = 'RJCT' |

### Status Reason Codes (Selected)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| AC01 | Incorrect account number | PaymentInstruction.statusReasonCode = 'AC01' |
| AC04 | Closed account | PaymentInstruction.statusReasonCode = 'AC04' |
| AC06 | Blocked account | PaymentInstruction.statusReasonCode = 'AC06' |
| AG01 | Transaction forbidden | PaymentInstruction.statusReasonCode = 'AG01' |
| AM04 | Insufficient funds | PaymentInstruction.statusReasonCode = 'AM04' |
| BE05 | Unrecognized initiating party | PaymentInstruction.statusReasonCode = 'BE05' |
| CUST | Requested by customer | PaymentInstruction.statusReasonCode = 'CUST' |

### Purpose Codes (Selected)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CBFF | Capital building | PaymentInstruction.purposeCode = 'CBFF' |
| GDDS | Purchase of goods | PaymentInstruction.purposeCode = 'GDDS' |
| OTHR | Other | PaymentInstruction.purposeCode = 'OTHR' |
| SALA | Salary payment | PaymentInstruction.purposeCode = 'SALA' |
| SUPP | Supplier payment | PaymentInstruction.purposeCode = 'SUPP' |

---

## CDM Extensions Required

All 51 PayNow fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>PAYNOW20241220143025123</MsgId>
      <CreDtTm>2024-12-20T14:30:25.123Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <SttlmInf>
        <SttlmMtd>INDA</SttlmMtd>
        <ClrSys>
          <Cd>PAYNOW</Cd>
        </ClrSys>
        <InstrPrty>NORM</InstrPrty>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>PAYNOW202412201430251</InstrId>
        <EndToEndId>E2E20241220143025123456</EndToEndId>
        <TxId>TXN20241220143025123456</TxId>
      </PmtId>
      <IntrBkSttlmAmt Ccy="SGD">500.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <SttlmTmIndctn>
        <CdtDtTm>2024-12-20T14:30:26.000Z</CdtDtTm>
      </SttlmTmIndctn>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>DBSSSGSGXXX</BICFI>
          <Nm>DBS Bank Ltd</Nm>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>TAN AH KOW</Nm>
        <Id>
          <PrvtId>
            <Othr>
              <Id>S1234567A</Id>
              <SchmeNm>
                <Cd>NRIC</Cd>
              </SchmeNm>
            </Othr>
          </PrvtId>
        </Id>
        <CtctDtls>
          <MobNb>+6591234567</MobNb>
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
            <Cd>MOBL</Cd>
          </Tp>
          <Id>+6591234567</Id>
        </Prxy>
      </DbtrAcct>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>OCBCSGSGXXX</BICFI>
          <Nm>Oversea-Chinese Banking Corp Ltd</Nm>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>LIM MEI LING</Nm>
        <Id>
          <PrvtId>
            <Othr>
              <Id>S9876543B</Id>
              <SchmeNm>
                <Cd>NRIC</Cd>
              </SchmeNm>
            </Othr>
          </PrvtId>
        </Id>
        <CtctDtls>
          <MobNb>+6598765432</MobNb>
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
            <Cd>MOBL</Cd>
          </Tp>
          <Id>+6598765432</Id>
        </Prxy>
      </CdtrAcct>
      <RmtInf>
        <Ustrd>Lunch payment</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
```

---

## References

- PayNow Official Website: https://www.paynow.gov.sg/
- ABS (Association of Banks in Singapore): https://abs.org.sg/
- FAST and PayNow System Rules: https://abs.org.sg/docs/library/fast-paynow-scheme-rules.pdf
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
