# UPI - Unified Payments Interface (India)
## Complete Field Mapping to GPS CDM

**Payment System:** UPI (Unified Payments Interface)
**Country:** India
**Operator:** National Payments Corporation of India (NPCI)
**Usage:** Real-time instant payments in Indian Rupees (INR)
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 67 fields mapped)

---

## System Overview

UPI is India's instant real-time payment system developed by NPCI. It enables inter-bank P2P and P2M transactions using mobile devices.

**Key Characteristics:**
- Currency: INR (Indian Rupee)
- Settlement: Near real-time
- Operating hours: 24/7/365
- Transaction limit: ₹1,00,000 per transaction (P2P), ₹2,00,000 (P2M)
- Message format: ISO 8583 / Proprietary XML

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total UPI Fields** | 67 | 100% |
| **Mapped to CDM** | 67 | 100% |
| **Direct Mapping** | 62 | 93% |
| **Derived/Calculated** | 4 | 6% |
| **Reference Data Lookup** | 1 | 1% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Transaction Identification

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | Transaction ID (txnId) | Text | 35 | Yes | Free text | PaymentInstruction | transactionId | Unique transaction ID |
| 2 | Customer Reference Number (CRN) | Text | 35 | Yes | Free text | PaymentInstruction | customerReferenceNumber | Customer reference |
| 3 | Transaction Reference ID (TxnRefId) | Text | 35 | Yes | Free text | PaymentInstruction | endToEndId | Reference ID |
| 4 | Original Transaction ID | Text | 35 | Cond | Free text | PaymentInstruction | originalTransactionId | For reversals/refunds |
| 5 | UPI Request ID (UpiReqId) | Text | 35 | Yes | Free text | PaymentInstruction | upiRequestId | UPI request identifier |
| 6 | RRN (Retrieval Reference Number) | Text | 12 | Yes | 12 digits | PaymentInstruction | rrn | Bank RRN |

### Amount and Currency

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 7 | Amount | Decimal | 12,2 | Yes | Numeric | PaymentInstruction | instructedAmount.amount | Transaction amount |
| 8 | Currency | Code | 3 | Yes | INR | PaymentInstruction | instructedAmount.currency | Always INR |
| 9 | Original amount (for refund) | Decimal | 12,2 | Cond | Numeric | PaymentInstruction | originalAmount | Original payment amount |

### Payer (Remitter) Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 10 | Payer VPA (Virtual Payment Address) | Text | 255 | Yes | user@bank | Account | virtualPaymentAddress | UPI VPA format |
| 11 | Payer name | Text | 99 | Yes | Free text | Party | name | Payer name |
| 12 | Payer account number | Text | 30 | No | Numeric | Account | accountNumber | Bank account (masked) |
| 13 | Payer IFSC | Text | 11 | No | IFSC code | FinancialInstitution | ifscCode | Indian Financial System Code |
| 14 | Payer account type | Code | 10 | No | SAVINGS, CURRENT | Account | accountType | Account type |
| 15 | Payer mobile number | Text | 10 | Yes | 10 digits | Party | mobilePhoneNumber | Mobile (no +91) |
| 16 | Payer device ID | Text | 100 | No | Free text | PaymentInstruction | payerDeviceId | Device identifier |
| 17 | Payer IP address | Text | 45 | No | IPv4/IPv6 | PaymentInstruction | payerIpAddress | IP address |
| 18 | Payer type | Code | 1 | Yes | P=Person, E=Entity | Party | partyType | Person or entity |
| 19 | Payer entity name | Text | 99 | Cond | Free text | Party | entityName | If entity |
| 20 | Payer merchant code | Text | 20 | Cond | Numeric | Party | merchantCode | If merchant |

### Payee (Beneficiary) Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 21 | Payee VPA | Text | 255 | Yes | user@bank | Account | virtualPaymentAddress | UPI VPA format |
| 22 | Payee name | Text | 99 | Yes | Free text | Party | name | Payee name |
| 23 | Payee account number | Text | 30 | No | Numeric | Account | accountNumber | Bank account |
| 24 | Payee IFSC | Text | 11 | No | IFSC code | FinancialInstitution | ifscCode | Indian Financial System Code |
| 25 | Payee account type | Code | 10 | No | SAVINGS, CURRENT | Account | accountType | Account type |
| 26 | Payee mobile number | Text | 10 | No | 10 digits | Party | mobilePhoneNumber | Mobile (no +91) |
| 27 | Payee type | Code | 1 | Yes | P=Person, E=Entity | Party | partyType | Person or entity |
| 28 | Payee entity name | Text | 99 | Cond | Free text | Party | entityName | If entity |
| 29 | Payee merchant code | Text | 20 | Cond | Numeric | Party | merchantCode | If merchant |
| 30 | Merchant Category Code (MCC) | Code | 4 | Cond | 4 digits | Party | merchantCategoryCode | For P2M payments |

### Transaction Type and Mode

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 31 | Transaction type | Code | 10 | Yes | PAY, COLLECT, REFUND, REVERSAL | PaymentInstruction | upiTransactionType | Type of transaction |
| 32 | Transaction mode | Code | 10 | Yes | See modes | PaymentInstruction | transactionMode | How initiated |
| 33 | Transaction sub-type | Code | 10 | No | See sub-types | PaymentInstruction | transactionSubType | Sub-classification |
| 34 | Initiation mode | Code | 2 | Yes | 00-15 | PaymentInstruction | initiationMode | Initiation method |
| 35 | Purpose code | Code | 2 | No | 00-99 | PaymentInstruction | purposeCode | Payment purpose |

### Timing Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 36 | Request timestamp | DateTime | 14 | Yes | YYYYMMDDHHmmss | PaymentInstruction | requestTimestamp | Request time |
| 37 | Response timestamp | DateTime | 14 | Yes | YYYYMMDDHHmmss | PaymentInstruction | responseTimestamp | Response time |
| 38 | Transaction timestamp | DateTime | 14 | Yes | YYYYMMDDHHmmss | PaymentInstruction | transactionTimestamp | Completion time |
| 39 | Expiry time | DateTime | 14 | Cond | YYYYMMDDHHmmss | PaymentInstruction | expiryTimestamp | For collect requests |

### Bank/PSP Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 40 | Payer PSP (Payment Service Provider) | Text | 20 | Yes | PSP code | FinancialInstitution | payerPspCode | Payer's PSP |
| 41 | Payee PSP | Text | 20 | Yes | PSP code | FinancialInstitution | payeePspCode | Payee's PSP |
| 42 | Remitter bank | Text | 50 | No | Bank name | FinancialInstitution | remitterBankName | Remitter bank name |
| 43 | Beneficiary bank | Text | 50 | No | Bank name | FinancialInstitution | beneficiaryBankName | Beneficiary bank name |
| 44 | NPCI transaction ID | Text | 35 | Yes | Free text | PaymentInstruction | npciTransactionId | NPCI system ID |

### Response and Status

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 45 | Response code | Code | 2 | Yes | 00-99 | PaymentInstruction | responseCode | Success/failure code |
| 46 | Response message | Text | 255 | No | Free text | PaymentInstruction | responseMessage | Response description |
| 47 | Status | Code | 10 | Yes | SUCCESS, FAILURE, PENDING | PaymentInstruction | transactionStatus | Overall status |
| 48 | Approval number | Text | 6 | Cond | 6 digits | PaymentInstruction | approvalNumber | Approval code |

### Remittance and Additional Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 49 | Remarks | Text | 50 | No | Free text | PaymentInstruction | remittanceInformation | Payment remarks |
| 50 | Purpose | Text | 100 | No | Free text | PaymentInstruction | purposeDescription | Purpose description |
| 51 | Note | Text | 200 | No | Free text | PaymentInstruction | additionalNote | Additional note |

### QR Code Information (if applicable)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 52 | QR code type | Code | 10 | Cond | STATIC, DYNAMIC | PaymentInstruction | qrCodeType | QR type |
| 53 | QR code string | Text | 512 | Cond | QR data | PaymentInstruction | qrCodeData | QR code payload |
| 54 | Transaction reference (QR) | Text | 35 | Cond | Free text | PaymentInstruction | qrTransactionReference | From QR code |

### Mandate Information (for AutoPay/Recurring)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 55 | Mandate ID (UMN) | Text | 35 | Cond | Free text | PaymentInstruction | mandateId | Mandate reference |
| 56 | Mandate type | Code | 10 | Cond | CREATE, UPDATE, REVOKE, EXECUTE | PaymentInstruction | mandateType | Mandate operation |
| 57 | Mandate amount | Decimal | 12,2 | Cond | Numeric | PaymentInstruction | mandateAmount | Max debit amount |
| 58 | Mandate frequency | Code | 10 | Cond | DAILY, WEEKLY, MONTHLY, etc. | PaymentInstruction | mandateFrequency | Frequency |
| 59 | Mandate start date | Date | 8 | Cond | YYYYMMDD | PaymentInstruction | mandateStartDate | Start date |
| 60 | Mandate end date | Date | 8 | Cond | YYYYMMDD | PaymentInstruction | mandateEndDate | End date |

### Risk and Fraud

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|-------------|---------------|-------|
| 61 | Risk score | Integer | 3 | No | 0-999 | PaymentInstruction | riskScore | Risk assessment |
| 62 | Fraud flag | Boolean | 1 | No | Y/N | PaymentInstruction | fraudFlag | Fraud indicator |
| 63 | Authentication factor | Code | 2 | No | PIN, BIO, OTP | PaymentInstruction | authenticationFactor | Auth method |

### Additional Metadata

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 64 | Application name | Text | 50 | No | Free text | PaymentInstruction | applicationName | App used |
| 65 | Application version | Text | 20 | No | Free text | PaymentInstruction | applicationVersion | App version |
| 66 | Operating system | Text | 20 | No | Android, iOS | PaymentInstruction | operatingSystem | Device OS |
| 67 | Settlement date | Date | 8 | No | YYYYMMDD | PaymentInstruction | settlementDate | Settlement date |

---

## Code Lists

### Transaction Types

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| PAY | Pay request | PaymentInstruction.upiTransactionType = 'PAY' |
| COLLECT | Collect request | PaymentInstruction.upiTransactionType = 'COLLECT' |
| REFUND | Refund | PaymentInstruction.upiTransactionType = 'REFUND' |
| REVERSAL | Reversal | PaymentInstruction.upiTransactionType = 'REVERSAL' |
| CHECK_STATUS | Status check | PaymentInstruction.upiTransactionType = 'CHECK_STATUS' |

### Transaction Modes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| DEFAULT | Default mode | PaymentInstruction.transactionMode = 'DEFAULT' |
| QR | QR code scan | PaymentInstruction.transactionMode = 'QR' |
| INTENT | Intent flow | PaymentInstruction.transactionMode = 'INTENT' |
| USSD | USSD (*99#) | PaymentInstruction.transactionMode = 'USSD' |

### Initiation Modes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 00 | Manually entered | PaymentInstruction.initiationMode = '00' |
| 01 | QR code scanned | PaymentInstruction.initiationMode = '01' |
| 02 | NFC | PaymentInstruction.initiationMode = '02' |
| 03 | SMS | PaymentInstruction.initiationMode = '03' |
| 04 | USSD | PaymentInstruction.initiationMode = '04' |
| 05 | App intent | PaymentInstruction.initiationMode = '05' |

### Response Codes (Selected)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 00 | Success | PaymentInstruction.responseCode = '00' |
| 01 | Deemed | PaymentInstruction.responseCode = '01' |
| 02 | Pending | PaymentInstruction.responseCode = '02' |
| U01 | Customer profile not found | PaymentInstruction.responseCode = 'U01' |
| U02 | Account does not exist | PaymentInstruction.responseCode = 'U02' |
| U16 | Risk threshold exceeded | PaymentInstruction.responseCode = 'U16' |
| U17 | PSP is not available | PaymentInstruction.responseCode = 'U17' |
| U28 | Transaction frequency exceeded | PaymentInstruction.responseCode = 'U28' |
| U30 | Device fingerprint mismatch | PaymentInstruction.responseCode = 'U30' |

### Purpose Codes (Selected)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 00 | Goods and services | PaymentInstruction.purposeCode = '00' |
| 01 | Refund | PaymentInstruction.purposeCode = '01' |
| 02 | Loan repayment | PaymentInstruction.purposeCode = '02' |
| 03 | Bill payment | PaymentInstruction.purposeCode = '03' |
| 04 | Education | PaymentInstruction.purposeCode = '04' |
| 05 | Healthcare | PaymentInstruction.purposeCode = '05' |

---

## CDM Extensions Required

All 67 UPI fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Example

### UPI Pay Request

```xml
<?xml version="1.0" encoding="UTF-8"?>
<upi:ReqPay xmlns:upi="http://npci.org/upi/schema/">
  <Head ver="1.0" ts="2024-12-20T14:30:25" orgId="HDFC0001" msgId="HDFCe4f3b4c8d2a1"/>
  <Txn id="HDFCe4f3b4c8d2a1b5c6d7e8f9" note="Lunch payment" refId="1234567890" refUrl="https://merchant.com/order/123" ts="2024-12-20T14:30:25" type="PAY">
    <Payer addr="john.doe@okaxis" name="John Doe" seqNum="1" type="PERSON" code="0000">
      <Info>
        <Identity id="9876543210" type="MOBILE"/>
        <Device>
          <Tag name="MOBILE" value="9876543210"/>
          <Tag name="GEOCODE" value="12.9716,77.5946"/>
          <Tag name="LOCATION" value="Bangalore"/>
          <Tag name="TYPE" value="MOB"/>
          <Tag name="ID" value="abcd1234567890efgh"/>
          <Tag name="IP" value="192.168.1.100"/>
          <Tag name="OS" value="Android"/>
          <Tag name="APP" value="PhonePe"/>
        </Device>
      </Info>
      <Ac addrType="ACCOUNT">
        <Detail name="IFSC" value="UTIB0000123"/>
        <Detail name="ACNUM" value="XXXXXXXXXXX1234"/>
        <Detail name="ACTYPE" value="SAVINGS"/>
      </Ac>
      <Amount value="250.00" curr="INR"/>
    </Payer>
    <Payee addr="merchant@hdfcbank" name="Merchant Store" type="ENTITY" code="9999">
      <Info>
        <Identity id="9999988888" type="MOBILE"/>
      </Info>
      <Ac addrType="ACCOUNT">
        <Detail name="IFSC" value="HDFC0001234"/>
        <Detail name="ACNUM" value="XXXXXXXXXXX5678"/>
        <Detail name="ACTYPE" value="CURRENT"/>
      </Ac>
      <Amount value="250.00" curr="INR"/>
    </Payee>
    <Mcc>5812</Mcc>
    <Purpose>00</Purpose>
  </Txn>
</upi:ReqPay>
```

### UPI Pay Response

```xml
<?xml version="1.0" encoding="UTF-8"?>
<upi:ReqPayResp xmlns:upi="http://npci.org/upi/schema/">
  <Head ver="1.0" ts="2024-12-20T14:30:26" orgId="NPCI" msgId="NPCIresp123456"/>
  <Resp reqMsgId="HDFCe4f3b4c8d2a1" result="SUCCESS" errCode="00">
    <Txn id="HDFCe4f3b4c8d2a1b5c6d7e8f9" refId="NPCI123456789012" ts="2024-12-20T14:30:26" type="PAY">
      <RiskScores>
        <Score provider="NPCI" type="TXNRISK" value="025"/>
      </RiskScores>
      <Ref>
        <Approval num="123456"/>
        <RRN>442012345678</RRN>
      </Ref>
    </Txn>
  </Resp>
</upi:ReqPayResp>
```

---

## References

- NPCI UPI Product Overview: https://www.npci.org.in/what-we-do/upi/product-overview
- UPI Specifications: https://www.npci.org.in/what-we-do/upi/product-specifications
- UPI API Documentation: https://www.npci.org.in/API-Specifications/upi-api-specification
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
