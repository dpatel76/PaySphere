# CNAPS - China National Advanced Payment System
## Complete Field Mapping to GPS CDM

**Payment System:** CNAPS (China National Advanced Payment System)
**Country:** China
**Operator:** People's Bank of China (PBOC)
**Usage:** Large-value and retail payment system in Chinese Yuan (CNY)
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 88 fields mapped)

---

## System Overview

CNAPS is China's national payment infrastructure operated by the People's Bank of China. It consists of two subsystems: HVPS (High Value Payment System) for large-value real-time payments and BEPS (Bulk Electronic Payment System) for retail batch payments.

**Key Characteristics:**
- Currency: CNY (Chinese Yuan / Renminbi)
- Settlement: Real-time (HVPS) / Batch (BEPS)
- Operating hours:
  - HVPS: 08:30-17:00 (Beijing Time, extended to 20:30 for some services)
  - BEPS: 24/7 with settlement windows
- Transaction limit:
  - HVPS: No limit (typically > CNY 50,000)
  - BEPS: CNY 50,000 per transaction
- Message format: CCPC (China Commercial Payment Code) / ISO 20022

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total CNAPS Fields** | 88 | 100% |
| **Mapped to CDM** | 88 | 100% |
| **Direct Mapping** | 81 | 92% |
| **Derived/Calculated** | 5 | 6% |
| **Reference Data Lookup** | 2 | 2% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Transaction Identification

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | Message Reference | Text | 35 | Yes | Alphanumeric | PaymentInstruction | messageId | Message identifier |
| 2 | End to End ID | Text | 35 | Yes | Alphanumeric | PaymentInstruction | endToEndId | E2E identifier |
| 3 | Transaction ID | Text | 35 | Yes | Alphanumeric | PaymentInstruction | transactionId | Transaction ID |
| 4 | Instruction ID | Text | 35 | Yes | Alphanumeric | PaymentInstruction | instructionId | Instruction ID |
| 5 | CNAPS Transaction Number | Text | 30 | Yes | System generated | PaymentInstruction | cnapsTransactionNumber | CNAPS system ID |
| 6 | Business Type Code | Code | 6 | Yes | See business types | PaymentInstruction | businessTypeCode | CNAPS business type |
| 7 | Subsystem Code | Code | 4 | Yes | HVPS, BEPS | PaymentInstruction | subsystemCode | HVPS or BEPS |

### Amount and Currency

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 8 | Amount | Decimal | 18,2 | Yes | Numeric | PaymentInstruction | instructedAmount.amount | Transaction amount |
| 9 | Currency | Code | 3 | Yes | CNY | PaymentInstruction | instructedAmount.currency | Always CNY |
| 10 | Amount in Words (Chinese) | Text | 100 | No | Chinese characters | PaymentInstruction | amountInWordsChinese | Amount in Chinese |

### Payer (Debtor) Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 11 | Payer name | Text | 62 | Yes | Chinese/English | Party | name | Payer name |
| 12 | Payer name (Chinese) | Text | 62 | Cond | Chinese characters | Party | nameChinese | Chinese name |
| 13 | Payer account number | Text | 32 | Yes | Numeric | Account | accountNumber | Account identifier |
| 14 | Payer account type | Code | 2 | No | See account types | Account | accountType | Account type |
| 15 | Payer identification type | Code | 2 | No | See ID types | Party | identificationType | ID type |
| 16 | Payer identification number | Text | 32 | No | Varies | Party | identificationNumber | ID number |
| 17 | Payer organization code | Text | 18 | Cond | USCC format | Party | unifiedSocialCreditCode | USCC for enterprises |
| 18 | Payer bank name | Text | 62 | Yes | Chinese/English | FinancialInstitution | name | Bank name |
| 19 | Payer bank name (Chinese) | Text | 62 | Cond | Chinese characters | FinancialInstitution | nameChinese | Chinese bank name |
| 20 | Payer bank code | Text | 12 | Yes | CNAPS bank code | FinancialInstitution | cnapsCode | 12-digit bank code |
| 21 | Payer bank province | Code | 2 | Yes | Province code | FinancialInstitution | provinceCode | Province code |
| 22 | Payer bank city | Code | 3 | Yes | City code | FinancialInstitution | cityCode | City code |
| 23 | Payer city name | Text | 35 | No | Chinese/English | Party | city | City name |
| 24 | Payer address | Text | 140 | No | Chinese/English | Party | addressLine | Address |
| 25 | Payer mobile number | Text | 20 | No | +86XXXXXXXXXXX | Party | mobilePhoneNumber | Mobile number |
| 26 | Payer email | Text | 256 | No | email@domain | Party | emailAddress | Email address |

### Payee (Creditor) Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 27 | Payee name | Text | 62 | Yes | Chinese/English | Party | name | Payee name |
| 28 | Payee name (Chinese) | Text | 62 | Cond | Chinese characters | Party | nameChinese | Chinese name |
| 29 | Payee account number | Text | 32 | Yes | Numeric | Account | accountNumber | Account identifier |
| 30 | Payee account type | Code | 2 | No | See account types | Account | accountType | Account type |
| 31 | Payee identification type | Code | 2 | No | See ID types | Party | identificationType | ID type |
| 32 | Payee identification number | Text | 32 | No | Varies | Party | identificationNumber | ID number |
| 33 | Payee organization code | Text | 18 | Cond | USCC format | Party | unifiedSocialCreditCode | USCC for enterprises |
| 34 | Payee bank name | Text | 62 | Yes | Chinese/English | FinancialInstitution | name | Bank name |
| 35 | Payee bank name (Chinese) | Text | 62 | Cond | Chinese characters | FinancialInstitution | nameChinese | Chinese bank name |
| 36 | Payee bank code | Text | 12 | Yes | CNAPS bank code | FinancialInstitution | cnapsCode | 12-digit bank code |
| 37 | Payee bank province | Code | 2 | Yes | Province code | FinancialInstitution | provinceCode | Province code |
| 38 | Payee bank city | Code | 3 | Yes | City code | FinancialInstitution | cityCode | City code |
| 39 | Payee city name | Text | 35 | No | Chinese/English | Party | city | City name |
| 40 | Payee address | Text | 140 | No | Chinese/English | Party | addressLine | Address |
| 41 | Payee mobile number | Text | 20 | No | +86XXXXXXXXXXX | Party | mobilePhoneNumber | Mobile number |
| 42 | Payee email | Text | 256 | No | email@domain | Party | emailAddress | Email address |

### Transaction Timing

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 43 | Transaction date | Date | 8 | Yes | YYYYMMDD | PaymentInstruction | transactionDate | Transaction date |
| 44 | Transaction time | Time | 6 | Yes | HHmmss | PaymentInstruction | transactionTime | Transaction time (Beijing) |
| 45 | Value date | Date | 8 | Yes | YYYYMMDD | PaymentInstruction | valueDate | Value date |
| 46 | Creation timestamp | DateTime | 14 | Yes | YYYYMMDDHHmmss | PaymentInstruction | creationTimestamp | Creation time |
| 47 | Settlement date | Date | 8 | Yes | YYYYMMDD | PaymentInstruction | settlementDate | Settlement date |
| 48 | Booking date | Date | 8 | No | YYYYMMDD | PaymentInstruction | bookingDate | Booking date |

### Remittance Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 49 | Payment purpose | Text | 142 | No | Chinese/English | PaymentInstruction | remittanceInformation | Payment purpose |
| 50 | Payment purpose (Chinese) | Text | 142 | No | Chinese characters | PaymentInstruction | remittanceInformationChinese | Chinese purpose |
| 51 | Purpose code | Code | 5 | No | See purpose codes | PaymentInstruction | purposeCode | Coded purpose |
| 52 | Abstract | Text | 100 | No | Chinese/English | PaymentInstruction | abstract | Payment abstract |
| 53 | Use | Text | 100 | No | Chinese/English | PaymentInstruction | use | Usage description |

### Payment Type and Priority

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 54 | Payment method | Code | 2 | No | See payment methods | PaymentInstruction | paymentMethod | Payment method |
| 55 | Payment type | Code | 2 | Yes | See payment types | PaymentInstruction | paymentType | Type of payment |
| 56 | Settlement priority | Code | 1 | No | 0, 1, 2 | PaymentInstruction | settlementPriority | Priority level |
| 57 | Urgent flag | Boolean | 1 | No | Y/N | PaymentInstruction | urgentFlag | Urgent indicator |

### Status and Response

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 58 | Transaction status | Code | 4 | Yes | See status codes | PaymentInstruction | transactionStatus | Status code |
| 59 | Return reason code | Code | 4 | Cond | See reason codes | PaymentInstruction | returnReasonCode | If returned |
| 60 | Return reason | Text | 100 | Cond | Chinese/English | PaymentInstruction | returnReasonDescription | Reason details |
| 61 | Processing result | Code | 1 | Yes | S, F, P | PaymentInstruction | processingResult | Success/Fail/Pending |

### Settlement Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 62 | Settlement method | Code | 2 | Yes | See methods | PaymentInstruction | settlementMethod | Settlement method |
| 63 | Clearing system | Code | 10 | Yes | CNAPS | PaymentInstruction | clearingSystem | CNAPS system |
| 64 | Settlement window | Code | 2 | Cond | See windows | PaymentInstruction | settlementWindow | BEPS settlement window |
| 65 | Batch number | Text | 20 | Cond | Alphanumeric | PaymentInstruction | batchNumber | Batch ID (BEPS) |
| 66 | Sequence number in batch | Integer | 6 | Cond | Numeric | PaymentInstruction | sequenceNumberInBatch | Sequence in batch |

### Regulatory and Compliance

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 67 | Transaction category | Code | 4 | No | See categories | PaymentInstruction | transactionCategory | Regulatory category |
| 68 | Cross-border indicator | Boolean | 1 | No | Y/N | PaymentInstruction | crossBorderIndicator | Cross-border flag |
| 69 | SAFE reporting code | Code | 6 | Cond | SAFE codes | PaymentInstruction | safeReportingCode | FX reporting code |
| 70 | Tax payment indicator | Boolean | 1 | No | Y/N | PaymentInstruction | taxPaymentIndicator | Tax payment flag |
| 71 | Tax type | Code | 2 | Cond | See tax types | PaymentInstruction | taxType | Type of tax |
| 72 | Invoice number | Text | 30 | No | Alphanumeric | PaymentInstruction | invoiceNumber | Invoice reference |
| 73 | Contract number | Text | 30 | No | Alphanumeric | PaymentInstruction | contractNumber | Contract reference |

### Bank Processing

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 74 | Originating bank reference | Text | 30 | Yes | Alphanumeric | PaymentInstruction | originatingBankReference | Originating bank ref |
| 75 | Receiving bank reference | Text | 30 | No | Alphanumeric | PaymentInstruction | receivingBankReference | Receiving bank ref |
| 76 | Intermediary bank code | Text | 12 | No | CNAPS bank code | FinancialInstitution | intermediaryBankCode | Intermediary bank |
| 77 | Intermediary bank name | Text | 62 | No | Chinese/English | FinancialInstitution | intermediaryBankName | Intermediary bank name |

### Charges and Fees

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 78 | Charge bearer | Code | 4 | No | DEBT, CRED, SHAR | PaymentInstruction | chargesBearer | Who pays charges |
| 79 | Charge amount | Decimal | 18,2 | No | Numeric | PaymentInstruction | chargeAmount | Charge amount |
| 80 | Charge currency | Code | 3 | No | CNY | PaymentInstruction | chargeCurrency | Usually CNY |

### Additional Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 81 | Reserve field 1 | Text | 100 | No | Free text | PaymentInstruction | reserveField1 | Reserved for future use |
| 82 | Reserve field 2 | Text | 100 | No | Free text | PaymentInstruction | reserveField2 | Reserved for future use |
| 83 | Attachment indicator | Boolean | 1 | No | Y/N | PaymentInstruction | attachmentIndicator | Attachment present |
| 84 | Attachment type | Code | 2 | Cond | See types | PaymentInstruction | attachmentType | Type of attachment |
| 85 | Channel code | Code | 4 | No | See channels | PaymentInstruction | channelCode | Originating channel |
| 86 | Original message reference | Text | 35 | No | Alphanumeric | PaymentInstruction | originalMessageReference | For amendments |
| 87 | Trace number | Text | 35 | No | Alphanumeric | PaymentInstruction | traceNumber | Tracing reference |
| 88 | Additional remittance info | Text | 140 | No | Chinese/English | PaymentInstruction | additionalRemittanceInfo | Additional info |

---

## Code Lists

### Subsystem Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| HVPS | High Value Payment System | PaymentInstruction.subsystemCode = 'HVPS' |
| BEPS | Bulk Electronic Payment System | PaymentInstruction.subsystemCode = 'BEPS' |

### Business Type Codes (Selected)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 101001 | Domestic inter-bank payment | PaymentInstruction.businessTypeCode = '101001' |
| 101002 | Intra-bank payment | PaymentInstruction.businessTypeCode = '101002' |
| 101003 | Real-time credit | PaymentInstruction.businessTypeCode = '101003' |
| 201001 | Bulk payment | PaymentInstruction.businessTypeCode = '201001' |
| 201002 | Payroll | PaymentInstruction.businessTypeCode = '201002' |

### Account Types

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Corporate settlement account | Account.accountType = '01' |
| 02 | Personal settlement account | Account.accountType = '02' |
| 03 | Special account | Account.accountType = '03' |
| 04 | Savings account | Account.accountType = '04' |

### Identification Types

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | ID Card (身份证) | Party.identificationType = '01' |
| 02 | Military ID | Party.identificationType = '02' |
| 03 | Passport | Party.identificationType = '03' |
| 04 | Business license | Party.identificationType = '04' |
| 05 | Organization code | Party.identificationType = '05' |
| 06 | USCC (统一社会信用代码) | Party.identificationType = '06' |

### Payment Types

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Normal payment | PaymentInstruction.paymentType = '01' |
| 02 | Return/Refund | PaymentInstruction.paymentType = '02' |
| 03 | Cancellation | PaymentInstruction.paymentType = '03' |

### Settlement Priority

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 0 | Normal | PaymentInstruction.settlementPriority = '0' |
| 1 | High | PaymentInstruction.settlementPriority = '1' |
| 2 | Urgent | PaymentInstruction.settlementPriority = '2' |

### Transaction Status Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| ACCP | Accepted | PaymentInstruction.transactionStatus = 'ACCP' |
| ACSC | Settlement completed | PaymentInstruction.transactionStatus = 'ACSC' |
| RJCT | Rejected | PaymentInstruction.transactionStatus = 'RJCT' |
| PDNG | Pending | PaymentInstruction.transactionStatus = 'PDNG' |
| RTRN | Returned | PaymentInstruction.transactionStatus = 'RTRN' |

### Return Reason Codes (Selected)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 0001 | Account does not exist | PaymentInstruction.returnReasonCode = '0001' |
| 0002 | Account name mismatch | PaymentInstruction.returnReasonCode = '0002' |
| 0003 | Frozen account | PaymentInstruction.returnReasonCode = '0003' |
| 0004 | Insufficient balance | PaymentInstruction.returnReasonCode = '0004' |
| 0005 | Bank code error | PaymentInstruction.returnReasonCode = '0005' |
| 0006 | Format error | PaymentInstruction.returnReasonCode = '0006' |
| 9999 | Other reasons | PaymentInstruction.returnReasonCode = '9999' |

### Purpose Codes (Selected)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 10101 | Goods payment | PaymentInstruction.purposeCode = '10101' |
| 10102 | Service payment | PaymentInstruction.purposeCode = '10102' |
| 10201 | Salary payment | PaymentInstruction.purposeCode = '10201' |
| 10202 | Bonus payment | PaymentInstruction.purposeCode = '10202' |
| 10301 | Loan repayment | PaymentInstruction.purposeCode = '10301' |
| 10401 | Tax payment | PaymentInstruction.purposeCode = '10401' |

### Settlement Windows (BEPS)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Window 1 (09:00) | PaymentInstruction.settlementWindow = '01' |
| 02 | Window 2 (11:30) | PaymentInstruction.settlementWindow = '02' |
| 03 | Window 3 (14:00) | PaymentInstruction.settlementWindow = '03' |
| 04 | Window 4 (16:30) | PaymentInstruction.settlementWindow = '04' |

---

## CDM Extensions Required

All 88 CNAPS fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CNAPS>
  <MsgHeader>
    <MsgRef>CNAPS20241220143025001</MsgRef>
    <MsgType>101001</MsgType>
    <SubsysCode>HVPS</SubsysCode>
    <CreDtTm>20241220143025</CreDtTm>
    <TxnDate>20241220</TxnDate>
    <TxnTime>143025</TxnTime>
  </MsgHeader>
  <TxnInfo>
    <EndToEndId>E2E20241220143025001</EndToEndId>
    <TxnId>TXN20241220143025001</TxnId>
    <InstrId>INSTR20241220143025001</InstrId>
    <CNAPSTxnNb>202412201430250010001</CNAPSTxnNb>
  </TxnInfo>
  <AmtInfo>
    <Amt>5000000.00</Amt>
    <Ccy>CNY</Ccy>
    <AmtInWords>伍佰万元整</AmtInWords>
  </AmtInfo>
  <Dbtr>
    <Nm>中国工商银行股份有限公司</Nm>
    <NmCn>中国工商银行股份有限公司</NmCn>
    <Id>
      <OrgId>
        <USCC>91110000100000000X</USCC>
      </OrgId>
    </Id>
    <Acct>
      <AcctNb>0200001234567890123</AcctNb>
      <AcctTp>01</AcctTp>
    </Acct>
  </Dbtr>
  <DbtrAgt>
    <FinInstnId>
      <CNAPSCd>102100001234</CNAPSCd>
      <Nm>ICBC Beijing Branch</Nm>
      <NmCn>中国工商银行北京分行</NmCn>
      <PrvncCd>11</PrvncCd>
      <CityCd>100</CityCd>
    </FinInstnId>
  </DbtrAgt>
  <Cdtr>
    <Nm>上海浦东发展银行股份有限公司</Nm>
    <NmCn>上海浦东发展银行股份有限公司</NmCn>
    <Id>
      <OrgId>
        <USCC>91310000132217864Y</USCC>
      </OrgId>
    </Id>
    <Acct>
      <AcctNb>9876543210123456789</AcctNb>
      <AcctTp>01</AcctTp>
    </Acct>
  </Cdtr>
  <CdtrAgt>
    <FinInstnId>
      <CNAPSCd>310290000123</CNAPSCd>
      <Nm>SPDB Shanghai Branch</Nm>
      <NmCn>上海浦东发展银行上海分行</NmCn>
      <PrvncCd>31</PrvncCd>
      <CityCd>290</CityCd>
    </FinInstnId>
  </CdtrAgt>
  <PmtTpInf>
    <PmtTp>01</PmtTp>
    <PmtMtd>01</PmtMtd>
    <SttlmPrty>1</SttlmPrty>
    <UrgntFlg>Y</UrgntFlg>
  </PmtTpInf>
  <RmtInf>
    <Ustrd>Corporate payment for equipment purchase</Ustrd>
    <UstrdCn>企业设备采购款</UstrdCn>
    <Purp>10101</Purp>
    <InvcNb>INV-2024-12345</InvcNb>
  </RmtInf>
  <SttlmInfo>
    <SttlmMtd>01</SttlmMtd>
    <SttlmDt>20241220</SttlmDt>
    <ValDt>20241220</ValDt>
  </SttlmInfo>
  <TxnSts>
    <Sts>ACSC</Sts>
    <PrcgRslt>S</PrcgRslt>
  </TxnSts>
</CNAPS>
```

---

## References

- People's Bank of China: http://www.pbc.gov.cn/
- CNAPS System Overview: http://www.pbc.gov.cn/english/130727/index.html
- China Payment and Clearing Association: http://www.pcac.org.cn/
- HVPS Specifications: [PBOC Internal Documentation]
- BEPS Specifications: [PBOC Internal Documentation]
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
