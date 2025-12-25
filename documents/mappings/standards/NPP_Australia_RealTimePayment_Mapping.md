# NPP - New Payments Platform Australia
## Complete Field Mapping to GPS CDM

**Payment System:** NPP (New Payments Platform)
**Country:** Australia
**Operator:** NPP Australia Limited (NPPA)
**Usage:** Real-time payments platform in Australian Dollars (AUD)
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 64 fields mapped)

---

## System Overview

The New Payments Platform (NPP) is Australia's fast payment infrastructure that enables real-time, data-rich payments between accounts at participating financial institutions.

**Key Characteristics:**
- Currency: AUD (Australian Dollar)
- Settlement: Real-time (< 60 seconds)
- Operating hours: 24/7/365
- Transaction limit: No system-wide limit (bank-specific)
- Message format: ISO 20022 XML
- PayID: Addressing service using email, mobile, ABN, or Organisational ID

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total NPP Fields** | 64 | 100% |
| **Mapped to CDM** | 64 | 100% |
| **Direct Mapping** | 59 | 92% |
| **Derived/Calculated** | 4 | 6% |
| **Reference Data Lookup** | 1 | 2% |
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
| 5 | NPP Transaction ID | Text | 35 | Yes | Alphanumeric | PaymentInstruction | nppTransactionId | NPP system ID |

### Amount and Currency

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 6 | Instructed Amount | Decimal | 18,2 | Yes | Numeric | PaymentInstruction | instructedAmount.amount | Transaction amount |
| 7 | Currency | Code | 3 | Yes | AUD | PaymentInstruction | instructedAmount.currency | Always AUD |
| 8 | Interbank Settlement Amount | Decimal | 18,2 | Yes | Numeric | PaymentInstruction | interbankSettlementAmount | Settlement amount |

### Payer (Debtor) Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 9 | Debtor name | Text | 140 | Yes | Free text | Party | name | Payer name |
| 10 | Debtor account number | Text | 34 | Yes | Alphanumeric | Account | accountNumber | Account identifier |
| 11 | Debtor account name | Text | 140 | No | Free text | Account | accountName | Account name |
| 12 | Debtor BSB | Text | 6 | Yes | 6 digits | Account | bsbNumber | Bank State Branch code |
| 13 | Debtor PayID type | Code | 10 | Cond | EMAIL, MOBILE, ABN, ORGID | Account | payIdType | PayID type |
| 14 | Debtor PayID value | Text | 256 | Cond | See PayID types | Account | payIdValue | PayID identifier |
| 15 | Debtor identification type | Code | 4 | No | See ID types | Party | identificationType | ID type |
| 16 | Debtor identification number | Text | 35 | No | Free text | Party | identificationNumber | ID number |
| 17 | Debtor organisation ID type | Code | 4 | Cond | ABN, ACN, ARBN | Party | organisationIdType | Organisation ID type |
| 18 | Debtor organisation ID | Text | 35 | Cond | See org ID types | Party | organisationIdNumber | ABN/ACN/ARBN |
| 19 | Debtor mobile number | Text | 20 | No | +61XXXXXXXXX | Party | mobilePhoneNumber | Mobile number |
| 20 | Debtor email address | Text | 256 | No | email@domain | Party | emailAddress | Email address |
| 21 | Debtor agent BIC | Code | 11 | Yes | SWIFT BIC | FinancialInstitution | bicCode | Bank identifier |
| 22 | Debtor agent name | Text | 140 | No | Free text | FinancialInstitution | name | Bank name |
| 23 | Debtor agent APCA ID | Text | 6 | Yes | 6 digits | FinancialInstitution | apcaIdentifier | APCA member ID |

### Payee (Creditor) Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 24 | Creditor name | Text | 140 | Yes | Free text | Party | name | Payee name |
| 25 | Creditor account number | Text | 34 | Yes | Alphanumeric | Account | accountNumber | Account identifier |
| 26 | Creditor account name | Text | 140 | No | Free text | Account | accountName | Account name |
| 27 | Creditor BSB | Text | 6 | Yes | 6 digits | Account | bsbNumber | Bank State Branch code |
| 28 | Creditor PayID type | Code | 10 | Cond | EMAIL, MOBILE, ABN, ORGID | Account | payIdType | PayID type |
| 29 | Creditor PayID value | Text | 256 | Cond | See PayID types | Account | payIdValue | PayID identifier |
| 30 | Creditor identification type | Code | 4 | No | See ID types | Party | identificationType | ID type |
| 31 | Creditor identification number | Text | 35 | No | Free text | Party | identificationNumber | ID number |
| 32 | Creditor organisation ID type | Code | 4 | Cond | ABN, ACN, ARBN | Party | organisationIdType | Organisation ID type |
| 33 | Creditor organisation ID | Text | 35 | Cond | See org ID types | Party | organisationIdNumber | ABN/ACN/ARBN |
| 34 | Creditor mobile number | Text | 20 | No | +61XXXXXXXXX | Party | mobilePhoneNumber | Mobile number |
| 35 | Creditor email address | Text | 256 | No | email@domain | Party | emailAddress | Email address |
| 36 | Creditor agent BIC | Code | 11 | Yes | SWIFT BIC | FinancialInstitution | bicCode | Bank identifier |
| 37 | Creditor agent name | Text | 140 | No | Free text | FinancialInstitution | name | Bank name |
| 38 | Creditor agent APCA ID | Text | 6 | Yes | 6 digits | FinancialInstitution | apcaIdentifier | APCA member ID |

### Transaction Timing

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 39 | Creation date/time | DateTime | 24 | Yes | ISO 8601 | PaymentInstruction | creationTimestamp | YYYY-MM-DDTHH:MM:SS.sssZ |
| 40 | Interbank settlement date | Date | 10 | Yes | YYYY-MM-DD | PaymentInstruction | interbankSettlementDate | Settlement date |
| 41 | Settlement time indication | DateTime | 24 | No | ISO 8601 | PaymentInstruction | settlementTimestamp | Actual settlement time |
| 42 | Acceptance date/time | DateTime | 24 | No | ISO 8601 | PaymentInstruction | acceptanceTimestamp | When accepted |

### Remittance Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 43 | Remittance information unstructured | Text | 280 | No | Free text | PaymentInstruction | remittanceInformation | Extended remittance (280 chars) |
| 44 | Purpose code | Code | 4 | No | See purpose codes | PaymentInstruction | purposeCode | Payment purpose |
| 45 | Category purpose | Code | 4 | No | CASH, SUPP, SALA | PaymentInstruction | categoryPurpose | Category purpose |

### Payment Type and Channel

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 46 | Payment type information | Code | 3 | No | See payment types | PaymentInstruction | paymentTypeInformation | Type of payment |
| 47 | Local instrument | Code | 35 | No | NPP | PaymentInstruction | localInstrument | NPP indicator |
| 48 | Service level code | Code | 4 | Yes | NPPR | PaymentInstruction | serviceLevelCode | NPP real-time |
| 49 | Channel code | Code | 4 | No | MOBL, INTB, BRNC | PaymentInstruction | channelCode | Channel used |

### Status and Response

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 50 | Transaction status | Code | 4 | Yes | ACCP, ACSC, RJCT | PaymentInstruction | transactionStatus | Status code |
| 51 | Status reason code | Code | 4 | Cond | See reason codes | PaymentInstruction | statusReasonCode | If rejected |
| 52 | Status reason information | Text | 105 | Cond | Free text | PaymentInstruction | statusReasonDescription | Reason details |

### Settlement Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 53 | Settlement method | Code | 4 | Yes | INDA | PaymentInstruction | settlementMethod | Instructed agent |
| 54 | Clearing system | Code | 5 | Yes | NPP | PaymentInstruction | clearingSystem | NPP system |
| 55 | Number of transactions | Integer | 15 | No | Numeric | PaymentInstruction | numberOfTransactions | Batch count |
| 56 | Settlement account | Text | 34 | No | Alphanumeric | FinancialInstitution | settlementAccount | Settlement account |

### Osko Specific Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 57 | Osko payment indicator | Boolean | 1 | No | true/false | PaymentInstruction | oskoPaymentIndicator | Osko branded payment |
| 58 | Osko notification preference | Code | 4 | No | EMAIL, SMS, NONE | PaymentInstruction | notificationPreference | Notification method |

### Additional Metadata

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 59 | Instruction priority | Code | 4 | No | HIGH, NORM | PaymentInstruction | priority | Priority indicator |
| 60 | Charge bearer | Code | 4 | No | DEBT, CRED, SHAR | PaymentInstruction | chargesBearer | Who pays charges |
| 61 | Instructing agent BIC | Code | 11 | No | BIC code | FinancialInstitution | instructingAgentBic | Instructing bank |
| 62 | Instructed agent BIC | Code | 11 | No | BIC code | FinancialInstitution | instructedAgentBic | Instructed bank |
| 63 | Ultimate debtor name | Text | 140 | No | Free text | Party | ultimateDebtorName | Ultimate payer |
| 64 | Ultimate creditor name | Text | 140 | No | Free text | Party | ultimateCreditorName | Ultimate payee |

---

## Code Lists

### PayID Types

| Code | Description | Format | CDM Mapping |
|------|-------------|--------|-------------|
| EMAIL | Email address | email@domain.com | Account.payIdType = 'EMAIL' |
| MOBILE | Mobile phone number | +61XXXXXXXXX | Account.payIdType = 'MOBILE' |
| ABN | Australian Business Number | 11 digits | Account.payIdType = 'ABN' |
| ORGID | Organisation Identifier | Varies | Account.payIdType = 'ORGID' |

### Organisation ID Types

| Code | Description | Format | CDM Mapping |
|------|-------------|--------|-------------|
| ABN | Australian Business Number | 11 digits | Party.organisationIdType = 'ABN' |
| ACN | Australian Company Number | 9 digits | Party.organisationIdType = 'ACN' |
| ARBN | Australian Registered Body Number | 9 digits | Party.organisationIdType = 'ARBN' |

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
| CUST | Requested by customer | PaymentInstruction.statusReasonCode = 'CUST' |
| MS02 | Reason not specified | PaymentInstruction.statusReasonCode = 'MS02' |
| MS03 | Not specified reason agent generated | PaymentInstruction.statusReasonCode = 'MS03' |

### Purpose Codes (Selected)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CBFF | Capital building | PaymentInstruction.purposeCode = 'CBFF' |
| GDDS | Purchase of goods | PaymentInstruction.purposeCode = 'GDDS' |
| CASH | Cash management | PaymentInstruction.purposeCode = 'CASH' |
| OTHR | Other | PaymentInstruction.purposeCode = 'OTHR' |
| SALA | Salary payment | PaymentInstruction.purposeCode = 'SALA' |
| SUPP | Supplier payment | PaymentInstruction.purposeCode = 'SUPP' |
| PENS | Pension payment | PaymentInstruction.purposeCode = 'PENS' |

### Category Purpose Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CASH | Cash management transfer | PaymentInstruction.categoryPurpose = 'CASH' |
| SUPP | Supplier payment | PaymentInstruction.categoryPurpose = 'SUPP' |
| SALA | Salary payment | PaymentInstruction.categoryPurpose = 'SALA' |

---

## CDM Extensions Required

All 64 NPP fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>NPP20241220143025001</MsgId>
      <CreDtTm>2024-12-20T14:30:25.123Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <SttlmInf>
        <SttlmMtd>INDA</SttlmMtd>
        <ClrSys>
          <Cd>NPP</Cd>
        </ClrSys>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>INSTR20241220143025001</InstrId>
        <EndToEndId>E2E20241220143025001</EndToEndId>
        <TxId>TXN20241220143025001</TxId>
      </PmtId>
      <PmtTpInf>
        <SvcLvl>
          <Cd>NPPR</Cd>
        </SvcLvl>
        <LclInstrm>
          <Prtry>NPP</Prtry>
        </LclInstrm>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="AUD">1500.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <InstdAmt Ccy="AUD">1500.00</InstdAmt>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>CTBAAU2SXXX</BICFI>
          <ClrSysMmbId>
            <ClrSysId>
              <Cd>AUNPP</Cd>
            </ClrSysId>
            <MmbId>063000</MmbId>
          </ClrSysMmbId>
          <Nm>Commonwealth Bank of Australia</Nm>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>JOHN SMITH</Nm>
        <Id>
          <OrgId>
            <Othr>
              <Id>51824753556</Id>
              <SchmeNm>
                <Cd>ABN</Cd>
              </SchmeNm>
            </Othr>
          </OrgId>
        </Id>
        <CtctDtls>
          <MobNb>+61412345678</MobNb>
          <EmailAdr>john.smith@email.com.au</EmailAdr>
        </CtctDtls>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>063000-12345678</Id>
          </Othr>
        </Id>
        <Nm>John Smith Business Account</Nm>
        <Prxy>
          <Tp>
            <Cd>EMAL</Cd>
          </Tp>
          <Id>john.smith@email.com.au</Id>
        </Prxy>
      </DbtrAcct>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>NATAAU3303M</BICFI>
          <ClrSysMmbId>
            <ClrSysId>
              <Cd>AUNPP</Cd>
            </ClrSysId>
            <MmbId>082000</MmbId>
          </ClrSysMmbId>
          <Nm>National Australia Bank Limited</Nm>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>JANE DOE</Nm>
        <CtctDtls>
          <MobNb>+61498765432</MobNb>
          <EmailAdr>jane.doe@email.com.au</EmailAdr>
        </CtctDtls>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>082000-98765432</Id>
          </Othr>
        </Id>
        <Nm>Jane Doe Savings</Nm>
        <Prxy>
          <Tp>
            <Cd>TELE</Cd>
          </Tp>
          <Id>+61498765432</Id>
        </Prxy>
      </CdtrAcct>
      <Purp>
        <Cd>SUPP</Cd>
      </Purp>
      <RmtInf>
        <Ustrd>Invoice INV-2024-12345 payment for consulting services rendered in December 2024. Reference: Project Alpha Phase 1.</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
```

---

## References

- NPP Australia: https://www.nppa.com.au/
- PayID: https://payid.com.au/
- Osko by BPAY: https://www.osko.com.au/
- NPP API Framework: https://www.nppa.com.au/the-platform/platform-documentation/
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
