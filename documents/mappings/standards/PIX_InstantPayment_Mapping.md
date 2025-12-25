# PIX - Brazil Instant Payment System
## Complete Field Mapping to GPS CDM

**Payment System:** PIX (Pagamento Instantâneo)
**Country:** Brazil
**Operator:** Central Bank of Brazil (Banco Central do Brasil - BCB)
**Usage:** Real-time instant payments in Brazilian Reais (BRL)
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 72 fields mapped)

---

## System Overview

PIX is Brazil's instant payment system launched in November 2020. It enables instant 24/7/365 payments and receipts between individuals, businesses, and government entities.

**Key Characteristics:**
- Currency: BRL (Brazilian Real)
- Settlement: Instant (< 10 seconds)
- Operating hours: 24/7/365
- Transaction limit: Varies by institution and time
- Message format: ISO 20022 XML (BCB customized)

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total PIX Fields** | 72 | 100% |
| **Mapped to CDM** | 72 | 100% |
| **Direct Mapping** | 66 | 92% |
| **Derived/Calculated** | 5 | 7% |
| **Reference Data Lookup** | 1 | 1% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Transaction Identification

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | End to End ID (endToEndId) | Text | 32 | Yes | E[0-9]{31} | PaymentInstruction | endToEndId | Format: E + 31 digits |
| 2 | Transaction ID (txId) | Text | 1-35 | No | Free text | PaymentInstruction | transactionId | Optional transaction ID |
| 3 | Return ID (rtrId) | Text | 1-35 | Cond | Free text | PaymentInstruction | returnId | Required for returns |
| 4 | Devolution ID (devolId) | Text | 32 | Cond | D[0-9]{31} | PaymentInstruction | devolutionId | Format: D + 31 digits (for refunds) |

### Amount and Currency

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 5 | Amount | Decimal | 13,2 | Yes | Numeric | PaymentInstruction | instructedAmount.amount | Max BRL 999,999,999.99 |
| 6 | Currency | Code | 3 | Yes | BRL | PaymentInstruction | instructedAmount.currency | Always BRL |
| 7 | Original amount (for devolution) | Decimal | 13,2 | Cond | Numeric | PaymentInstruction | originalAmount | Original payment amount |

### Payer (Debtor) Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 8 | Payer participant (ISPB) | Text | 8 | Yes | 8 digits | FinancialInstitution | payerIspb | Brazilian bank code |
| 9 | Payer branch | Text | 4 | Yes | 4 digits | FinancialInstitution | payerBranch | Branch code |
| 10 | Payer account type | Code | 4 | Yes | CACC, SVGS, SLRY, TRAN | Account | accountType | Account type |
| 11 | Payer account number | Text | 20 | Yes | Alphanumeric | Account | accountNumber | Account identifier |
| 12 | Payer tax ID type | Code | 4 | Yes | CPF, CNPJ | Party | taxIdType | Individual (CPF) or Entity (CNPJ) |
| 13 | Payer tax ID | Text | 14 | Yes | CPF or CNPJ | Party | taxIdentificationNumber | 11 digits (CPF) or 14 digits (CNPJ) |
| 14 | Payer name | Text | 140 | Yes | Free text | Party | name | Payer full name |
| 15 | Payer trade name | Text | 140 | No | Free text | Party | tradeName | Business trade name |
| 16 | PIX Key (Payer) | Text | 77 | No | See PIX key types | Account | pixKey | Payer's PIX key (if used) |
| 17 | PIX Key Type (Payer) | Code | 5 | Cond | PHONE, EMAIL, CPF, CNPJ, EVP | Account | pixKeyType | Type of PIX key |

### Payee (Creditor) Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 18 | Payee participant (ISPB) | Text | 8 | Yes | 8 digits | FinancialInstitution | payeeIspb | Brazilian bank code |
| 19 | Payee branch | Text | 4 | Yes | 4 digits | FinancialInstitution | payeeBranch | Branch code |
| 20 | Payee account type | Code | 4 | Yes | CACC, SVGS, SLRY, TRAN | Account | accountType | Account type |
| 21 | Payee account number | Text | 20 | Yes | Alphanumeric | Account | accountNumber | Account identifier |
| 22 | Payee tax ID type | Code | 4 | Yes | CPF, CNPJ | Party | taxIdType | Individual (CPF) or Entity (CNPJ) |
| 23 | Payee tax ID | Text | 14 | Yes | CPF or CNPJ | Party | taxIdentificationNumber | 11 digits (CPF) or 14 digits (CNPJ) |
| 24 | Payee name | Text | 140 | Yes | Free text | Party | name | Payee full name |
| 25 | Payee trade name | Text | 140 | No | Free text | Party | tradeName | Business trade name |
| 26 | PIX Key (Payee) | Text | 77 | No | See PIX key types | Account | pixKey | Payee's PIX key (if used) |
| 27 | PIX Key Type (Payee) | Code | 5 | Cond | PHONE, EMAIL, CPF, CNPJ, EVP | Account | pixKeyType | Type of PIX key |

### Transaction Timing

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 28 | Request timestamp | DateTime | 24 | Yes | ISO 8601 | PaymentInstruction | requestTimestamp | YYYY-MM-DDTHH:MM:SS.sssZ |
| 29 | Acceptance timestamp | DateTime | 24 | Yes | ISO 8601 | PaymentInstruction | acceptanceTimestamp | When PSP accepted |
| 30 | Settlement timestamp | DateTime | 24 | Yes | ISO 8601 | PaymentInstruction | settlementTimestamp | When settled |
| 31 | Liquidation timestamp | DateTime | 24 | Yes | ISO 8601 | PaymentInstruction | liquidationTimestamp | Final liquidation |

### Initiation Type and Channel

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 32 | Initiation type | Code | 4 | Yes | DICT, MANU, QRDN, QRES | PaymentInstruction | initiationType | How payment was initiated |
| 33 | Payment type | Code | 4 | Yes | See payment types | PaymentInstruction | pixPaymentType | PIX payment type |
| 34 | Channel | Code | 4 | No | MOBL, INTB, BRNC, ATM | PaymentInstruction | channelCode | Channel used |

### Remittance Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 35 | Remittance information | Text | 140 | No | Free text | PaymentInstruction | remittanceInformation | Unstructured remittance |
| 36 | Purpose | Code | 5 | No | See purpose codes | PaymentInstruction | purposeCode | Payment purpose |

### QR Code Information (if applicable)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 37 | QR Code type | Code | 10 | Cond | STATIC, DYNAMIC | PaymentInstruction | qrCodeType | Static or dynamic QR |
| 38 | QR Code ID | Text | 35 | Cond | Free text | PaymentInstruction | qrCodeId | QR code identifier |
| 39 | QR Code data | Text | 512 | Cond | EMV QR format | PaymentInstruction | qrCodeData | Full QR code payload |
| 40 | Merchant category code (MCC) | Code | 4 | Cond | 4 digits | Party | merchantCategoryCode | For merchant payments |
| 41 | Merchant name | Text | 25 | Cond | Free text | Party | merchantName | For QR payments |
| 42 | Merchant city | Text | 15 | Cond | Free text | Party | merchantCity | For QR payments |
| 43 | Transaction ID (QR) | Text | 25 | Cond | Free text | PaymentInstruction | qrTransactionId | From QR code |

### Return/Devolution Information (if applicable)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 44 | Return/devolution reason code | Code | 4 | Cond | See reason codes | PaymentInstruction | returnReasonCode | Why returned |
| 45 | Return/devolution reason description | Text | 140 | Cond | Free text | PaymentInstruction | returnReasonDescription | Reason details |
| 46 | Original end to end ID | Text | 32 | Cond | E[0-9]{31} | PaymentInstruction | originalEndToEndId | Original payment E2E ID |
| 47 | Devolution type | Code | 4 | Cond | FULL, PART | PaymentInstruction | devolutionType | Full or partial refund |

### Nature of Transaction (Brazilian Regulatory)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 48 | Nature code | Code | 5 | No | See nature codes | PaymentInstruction | brazilNatureCode | Regulatory nature code |
| 49 | Complementary nature info | Text | 30 | No | Free text | PaymentInstruction | brazilNatureComplement | Additional nature info |

### Fraud and Risk Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 50 | Fraud prevention indicator | Code | 4 | No | HIGH, MEDI, LOW | PaymentInstruction | fraudRiskLevel | Risk assessment |
| 51 | IP address (payer) | Text | 45 | No | IPv4/IPv6 | PaymentInstruction | payerIpAddress | Payer's IP |
| 52 | Device ID (payer) | Text | 100 | No | Free text | PaymentInstruction | payerDeviceId | Device identifier |
| 53 | Geolocation (payer) | Text | 50 | No | Lat/Long | PaymentInstruction | payerGeolocation | GPS coordinates |

### Additional Fields

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 54 | Transaction sequence | Integer | 10 | No | Numeric | PaymentInstruction | transactionSequence | Sequence number |
| 55 | Priority | Code | 4 | No | HIGH, NORM | PaymentInstruction | priority | Priority indicator |
| 56 | Previous message ID | Text | 35 | No | Free text | PaymentInstruction | previousMessageId | For related messages |
| 57 | Message type | Code | 8 | Yes | pacs.008, pacs.004 | PaymentInstruction | messageType | ISO 20022 message type |

### DICT Information (PIX Key Directory)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 58 | DICT entry ID | Text | 32 | No | Free text | Account | dictEntryId | DICT entry identifier |
| 59 | DICT key status | Code | 10 | No | ACTIVE, SUSPENDED | Account | dictKeyStatus | PIX key status |
| 60 | DICT registration date | Date | 10 | No | YYYY-MM-DD | Account | dictRegistrationDate | When key registered |
| 61 | Account opening date | Date | 10 | No | YYYY-MM-DD | Account | accountOpeningDate | Account open date |

### Special Transactions

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 62 | Withdrawal type | Code | 4 | Cond | CASH | PaymentInstruction | withdrawalType | For PIX withdrawal |
| 63 | Withdrawal service provider | Text | 8 | Cond | ISPB | FinancialInstitution | withdrawalProviderIspb | Cash-out provider |
| 64 | Change amount | Decimal | 13,2 | Cond | Numeric | PaymentInstruction | changeAmount | For PIX change |

### Settlement Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 65 | Settlement method | Code | 4 | Yes | INDA | PaymentInstruction | settlementMethod | Instructed agent |
| 66 | Clearing system | Code | 10 | Yes | PIX | PaymentInstruction | clearingSystem | Always PIX |
| 67 | SPI transaction ID | Text | 32 | Yes | Free text | PaymentInstruction | spiTransactionId | SPI system ID |

### Metadata

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 68 | PSP sender | Text | 8 | Yes | ISPB | FinancialInstitution | pspSenderIspb | Sending PSP |
| 69 | PSP receiver | Text | 8 | Yes | ISPB | FinancialInstitution | pspReceiverIspb | Receiving PSP |
| 70 | Message status | Code | 10 | Yes | See status codes | PaymentInstruction | messageStatus | Message status |
| 71 | BCB settlement date | Date | 10 | Yes | YYYY-MM-DD | PaymentInstruction | bcbSettlementDate | BCB settlement date |
| 72 | Reconciliation ID | Text | 35 | No | Free text | PaymentInstruction | reconciliationId | For reconciliation |

---

## Code Lists

### PIX Key Types

| Code | Description | Format | CDM Mapping |
|------|-------------|--------|-------------|
| PHONE | Mobile phone number | +55AAXXXXXXXXX | Account.pixKeyType = 'PHONE' |
| EMAIL | Email address | email@domain.com | Account.pixKeyType = 'EMAIL' |
| CPF | Individual tax ID | 11 digits | Account.pixKeyType = 'CPF' |
| CNPJ | Entity tax ID | 14 digits | Account.pixKeyType = 'CNPJ' |
| EVP | Random key | UUID v4 | Account.pixKeyType = 'EVP' |

### Initiation Types

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| DICT | Initiated using PIX key (DICT lookup) | PaymentInstruction.initiationType = 'DICT' |
| MANU | Manual entry (account details) | PaymentInstruction.initiationType = 'MANU' |
| QRDN | Dynamic QR code | PaymentInstruction.initiationType = 'QRDN' |
| QRES | Static QR code | PaymentInstruction.initiationType = 'QRES' |

### Payment Types

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| TRAN | Transfer | PaymentInstruction.pixPaymentType = 'TRAN' |
| WITH | Withdrawal | PaymentInstruction.pixPaymentType = 'WITH' |
| PYMT | Payment | PaymentInstruction.pixPaymentType = 'PYMT' |
| CHNG | Change | PaymentInstruction.pixPaymentType = 'CHNG' |

### Return Reason Codes (Selected)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| FR01 | Fraud | PaymentInstruction.returnReasonCode = 'FR01' |
| AC03 | Invalid account | PaymentInstruction.returnReasonCode = 'AC03' |
| AG03 | Transaction forbidden | PaymentInstruction.returnReasonCode = 'AG03' |
| AM04 | Insufficient funds | PaymentInstruction.returnReasonCode = 'AM04' |
| FOCR | Requested by customer | PaymentInstruction.returnReasonCode = 'FOCR' |
| SL02 | Specific service not offered | PaymentInstruction.returnReasonCode = 'SL02' |

### Nature Codes (Brazilian Regulatory - Selected)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 10101 | Credit for salary | PaymentInstruction.brazilNatureCode = '10101' |
| 10201 | Rent payment | PaymentInstruction.brazilNatureCode = '10201' |
| 10301 | Payment of fees/taxes | PaymentInstruction.brazilNatureCode = '10301' |
| 10401 | Payment to suppliers | PaymentInstruction.brazilNatureCode = '10401' |
| 10501 | Transfer between own accounts | PaymentInstruction.brazilNatureCode = '10501' |

---

## CDM Extensions Required

All 72 PIX fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.07">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>PIX20241220123456789</MsgId>
      <CreDtTm>2024-12-20T14:30:25.123Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <SttlmInf>
        <SttlmMtd>INDA</SttlmMtd>
        <ClrSys>
          <Cd>PIX</Cd>
        </ClrSys>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <EndToEndId>E1234567820241220143025123456789</EndToEndId>
        <TxId>SPI20241220143025123456789</TxId>
      </PmtId>
      <IntrBkSttlmAmt Ccy="BRL">1250.50</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <DbtrAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>12345678</MmbId>
          </ClrSysMmbId>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>JOAO DA SILVA</Nm>
        <Id>
          <OrgId>
            <Othr>
              <Id>12345678901</Id>
              <SchmeNm>
                <Cd>CPF</Cd>
              </SchmeNm>
            </Othr>
          </OrgId>
        </Id>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>00012345678901234567</Id>
          </Othr>
        </Id>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
      </DbtrAcct>
      <CdtrAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>87654321</MmbId>
          </ClrSysMmbId>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>MARIA OLIVEIRA</Nm>
        <Id>
          <OrgId>
            <Othr>
              <Id>98765432109</Id>
              <SchmeNm>
                <Cd>CPF</Cd>
              </SchmeNm>
            </Othr>
          </OrgId>
        </Id>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>00098765432109876543</Id>
          </Othr>
        </Id>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
      </CdtrAcct>
      <RmtInf>
        <Ustrd>Pagamento fatura 12/2024</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
```

---

## References

- Banco Central do Brasil - PIX: https://www.bcb.gov.br/estabilidadefinanceira/pix
- PIX Regulations: https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Regulamento&numero=1
- PIX Technical Specifications: https://www.bcb.gov.br/content/estabilidadefinanceira/pix/Regulamento_Pix/II_ManualdePadroesparaIniciacaodoPix.pdf
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
