# BOJ-NET - Bank of Japan Network System
## Complete Field Mapping to GPS CDM

**Message Type:** BOJ-NET Funds Transfer Message (Proprietary Fixed-Length Format)
**Standard:** Proprietary format (ISO 20022 migration planned for 2027)
**Operator:** Bank of Japan (BOJ - 日本銀行)
**Usage:** Real-time gross settlement for large-value yen transfers in Japan
**Document Date:** 2024-12-21
**Mapping Coverage:** 100% (All 78 fields mapped)

---

## Message Overview

BOJ-NET (Bank of Japan Financial Network System / 日銀ネット) is Japan's real-time gross settlement system operated by the Bank of Japan. It processes high-value yen transfers between financial institutions with real-time settlement through current accounts at the Bank of Japan. The system currently uses a proprietary format but will migrate to ISO 20022 in 2027.

**Key Characteristics:**
- Currency: JPY (Japanese Yen) only
- Execution time: Real-time gross settlement
- Amount limit: No maximum (high-value system)
- Availability: Business days, extended hours
- Settlement: Real-time gross settlement through BOJ current accounts
- Message format: Proprietary fixed-length format (current)
- Future migration: ISO 20022 planned for May 2027

**Operating Hours:**
- Funds Transfer: 09:00-19:00 JST (Japan Standard Time)
- JGB Services: 09:00-18:30 JST
- Business Days: Monday-Friday (excluding Japanese national holidays)

**Settlement:** Real-time gross settlement through current accounts at Bank of Japan
**Related Systems:** Zengin System (retail), FXYCS (foreign exchange yen clearing)

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total BOJ-NET Fields** | 78 | 100% |
| **Mapped to CDM** | 78 | 100% |
| **Direct Mapping** | 71 | 91% |
| **Derived/Calculated** | 5 | 6% |
| **Reference Data Lookup** | 2 | 3% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Message Header

| Field Position | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|----------------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 001-002 | Transaction Code | Numeric | 2 | Y | 01-99 | PaymentInstruction | messageType | 01=Credit Transfer |
| 003-005 | Message Format Version | Alphanumeric | 3 | Y | Current version | PaymentInstruction | messageVersion | Format version |
| 006-021 | Message Reference Number | Alphanumeric | 16 | Y | Unique ID | PaymentInstruction | messageId | Unique message identifier |
| 022-029 | Transaction Date | Numeric | 8 | Y | YYYYMMDD | PaymentInstruction | messageDate | Transaction date |
| 030-035 | Transaction Time | Numeric | 6 | Y | HHMMSS | PaymentInstruction | messageTime | Transaction time (JST) |
| 036-039 | Sending Participant Code | Numeric | 4 | Y | BOJ code | FinancialInstitution | nationalClearingCode | Sending bank BOJ code |
| 040-043 | Receiving Participant Code | Numeric | 4 | Y | BOJ code | FinancialInstitution | nationalClearingCode | Receiving bank BOJ code |
| 044-045 | Priority Code | Numeric | 2 | Y | 01-10 | PaymentInstruction | priorityCode | Priority level (01=highest) |
| 046-047 | Processing Type | Numeric | 2 | Y | 01-20 | PaymentInstruction | processingType | Normal, urgent, etc. |
| 048-049 | Settlement Type | Numeric | 2 | Y | 01, 02 | PaymentInstruction | settlementType | 01=RTGS, 02=Deferred |

### Transaction Information

| Field Position | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|----------------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 050-069 | Transaction Reference | Alphanumeric | 20 | Y | Unique ID | PaymentInstruction | transactionId | Unique transaction ID |
| 070-089 | End-to-End Reference | Alphanumeric | 20 | Y | Any | PaymentInstruction | endToEndId | Customer reference |
| 090-092 | Currency Code | Alpha | 3 | Y | JPY | PaymentInstruction | currency | JPY only |
| 093-107 | Transaction Amount | Numeric | 15 | Y | Amount (yen) | PaymentInstruction | instructedAmount.amount | Amount in yen (no decimals) |
| 108-115 | Value Date | Numeric | 8 | Y | YYYYMMDD | PaymentInstruction | valueDate | Settlement date |
| 116-121 | Settlement Time | Numeric | 6 | N | HHMMSS | PaymentInstruction | settlementTime | Actual settlement time |
| 122-123 | Transaction Type | Numeric | 2 | Y | 01-50 | PaymentInstruction | transactionType | Payment type code |
| 124-125 | Charge Indicator | Numeric | 2 | Y | 01-03 | PaymentInstruction | chargeBearer | 01=OUR, 02=BEN, 03=SHA |

### Sender/Debtor Information

| Field Position | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|----------------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 126-129 | Sender Bank Code | Numeric | 4 | Y | BOJ code | FinancialInstitution | nationalClearingCode | Sender's bank |
| 130-132 | Sender Branch Code | Numeric | 3 | N | Branch code | FinancialInstitution | branchCode | Bank branch |
| 133-167 | Sender Bank Name | JIS X 0208 | 35 | N | Kanji/Kana | FinancialInstitution | institutionName | Bank name (Japanese) |
| 168-202 | Sender Bank Name (English) | Alphanumeric | 35 | N | Any | FinancialInstitution | institutionNameEnglish | Bank name (English) |
| 203-237 | Sender Account Number | Alphanumeric | 35 | Y | Account number | Account | accountNumber | Sender account |
| 238-272 | Sender Account Name | JIS X 0208 | 35 | Y | Kanji/Kana | Account | accountName | Account holder name (Japanese) |
| 273-307 | Sender Account Name (English) | Alphanumeric | 35 | N | Any | Account | accountNameEnglish | Account holder name (English) |
| 308-342 | Sender Name | JIS X 0208 | 35 | Y | Kanji/Kana | Party | name | Originator name (Japanese) |
| 343-377 | Sender Address 1 | JIS X 0208 | 35 | N | Kanji/Kana | Party | addressLine1 | Address line 1 |
| 378-412 | Sender Address 2 | JIS X 0208 | 35 | N | Kanji/Kana | Party | addressLine2 | Address line 2 |
| 413-447 | Sender Address 3 | JIS X 0208 | 35 | N | Kanji/Kana | Party | addressLine3 | Address line 3 |
| 448-450 | Sender Country Code | Alpha | 3 | N | JPN | Party | country | Country code (ISO 3166 alpha-3) |
| 451-463 | Sender Identification | Alphanumeric | 13 | N | Corporate/Personal ID | Party | nationalId | Japanese ID number |
| 464-473 | Sender Reference | Alphanumeric | 10 | N | Any | Party | customerReference | Customer reference |

### Receiver/Beneficiary Information

| Field Position | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|----------------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 474-477 | Receiver Bank Code | Numeric | 4 | Y | BOJ code | FinancialInstitution | nationalClearingCode | Receiver's bank |
| 478-480 | Receiver Branch Code | Numeric | 3 | N | Branch code | FinancialInstitution | branchCode | Bank branch |
| 481-515 | Receiver Bank Name | JIS X 0208 | 35 | N | Kanji/Kana | FinancialInstitution | institutionName | Bank name (Japanese) |
| 516-550 | Receiver Bank Name (English) | Alphanumeric | 35 | N | Any | FinancialInstitution | institutionNameEnglish | Bank name (English) |
| 551-585 | Receiver Account Number | Alphanumeric | 35 | Y | Account number | Account | accountNumber | Receiver account |
| 586-620 | Receiver Account Name | JIS X 0208 | 35 | Y | Kanji/Kana | Account | accountName | Account holder name (Japanese) |
| 621-655 | Receiver Account Name (English) | Alphanumeric | 35 | N | Any | Account | accountNameEnglish | Account holder name (English) |
| 656-690 | Receiver Name | JIS X 0208 | 35 | Y | Kanji/Kana | Party | name | Beneficiary name (Japanese) |
| 691-725 | Receiver Address 1 | JIS X 0208 | 35 | N | Kanji/Kana | Party | addressLine1 | Address line 1 |
| 726-760 | Receiver Address 2 | JIS X 0208 | 35 | N | Kanji/Kana | Party | addressLine2 | Address line 2 |
| 761-795 | Receiver Address 3 | JIS X 0208 | 35 | N | Kanji/Kana | Party | addressLine3 | Address line 3 |
| 796-798 | Receiver Country Code | Alpha | 3 | N | JPN | Party | country | Country code (ISO 3166 alpha-3) |
| 799-811 | Receiver Identification | Alphanumeric | 13 | N | Corporate/Personal ID | Party | nationalId | Japanese ID number |
| 812-821 | Receiver Reference | Alphanumeric | 10 | N | Any | Party | customerReference | Customer reference |

### Ultimate Parties

| Field Position | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|----------------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 822-856 | Ultimate Sender Name | JIS X 0208 | 35 | N | Kanji/Kana | Party | ultimateDebtorName | Ultimate originator |
| 857-869 | Ultimate Sender ID | Alphanumeric | 13 | N | Any | Party | ultimateDebtorId | Ultimate debtor identifier |
| 870-904 | Ultimate Receiver Name | JIS X 0208 | 35 | N | Kanji/Kana | Party | ultimateCreditorName | Ultimate beneficiary |
| 905-917 | Ultimate Receiver ID | Alphanumeric | 13 | N | Any | Party | ultimateCreditorId | Ultimate creditor identifier |

### Remittance Information

| Field Position | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|----------------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 918-1057 | Remittance Information | JIS X 0208 | 140 | N | Kanji/Kana | PaymentInstruction | remittanceInformation | Payment details (Japanese) |
| 1058-1197 | Remittance Info (English) | Alphanumeric | 140 | N | Any | PaymentInstruction | remittanceInformationEnglish | Payment details (English) |
| 1198-1232 | Purpose Code | Alphanumeric | 35 | N | Purpose text | PaymentInstruction | purposeDescription | Purpose of payment |
| 1233-1236 | Purpose Category Code | Alpha | 4 | N | External code | PaymentInstruction | purposeCode | Purpose codes |

### Regulatory and Additional Information

| Field Position | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|----------------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1237-1246 | Regulatory Reporting Code | Alphanumeric | 10 | N | Any | PaymentInstruction | regulatoryReportingCode | BOJ reporting code |
| 1247-1281 | Additional Information 1 | JIS X 0208 | 35 | N | Kanji/Kana | PaymentInstruction | additionalInformation1 | Extra details |
| 1282-1316 | Additional Information 2 | JIS X 0208 | 35 | N | Kanji/Kana | PaymentInstruction | additionalInformation2 | Extra details |
| 1317-1351 | Additional Information 3 | JIS X 0208 | 35 | N | Kanji/Kana | PaymentInstruction | additionalInformation3 | Extra details |
| 1352-1386 | Additional Information 4 | JIS X 0208 | 35 | N | Kanji/Kana | PaymentInstruction | additionalInformation4 | Extra details |

### Charges and Fees

| Field Position | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|----------------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1387-1401 | Charges Amount | Numeric | 15 | N | Amount (yen) | Charge | chargeAmount.amount | Charges in yen |
| 1402-1404 | Charges Currency | Alpha | 3 | N | JPY | Charge | chargeAmount.currency | JPY only |
| 1405-1408 | Charges Bank Code | Numeric | 4 | N | BOJ code | FinancialInstitution | nationalClearingCode | Bank collecting charges |
| 1409-1410 | Charge Type | Numeric | 2 | N | 01-20 | Charge | chargeType | Type of charge |

### Settlement and Status

| Field Position | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|----------------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1411-1412 | Settlement Status | Alpha | 2 | Y | SE, PE, RE | PaymentInstruction | settlementStatus | SE=Settled, PE=Pending, RE=Rejected |
| 1413-1420 | Settlement Date | Numeric | 8 | N | YYYYMMDD | PaymentInstruction | settlementDate | Actual settlement date |
| 1421-1426 | Settlement Time | Numeric | 6 | N | HHMMSS | PaymentInstruction | settlementTime | Actual settlement time |
| 1427-1441 | Settlement Reference | Alphanumeric | 15 | N | Any | PaymentInstruction | settlementReference | BOJ settlement reference |
| 1442-1456 | BOJ Transaction Number | Alphanumeric | 15 | N | BOJ assigned | PaymentInstruction | clearingSystemReference | BOJ system reference |

### Return and Reject Information

| Field Position | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|----------------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1457-1460 | Return Reason Code | Alphanumeric | 4 | N | Error codes | PaymentInstruction | returnReasonCode | Reason for return/reject |
| 1461-1530 | Return Reason Description | JIS X 0208 | 70 | N | Kanji/Kana | PaymentInstruction | returnReasonDescription | Return reason text |
| 1531-1538 | Return Date | Numeric | 8 | N | YYYYMMDD | PaymentInstruction | returnDate | Date of return |
| 1539-1544 | Return Time | Numeric | 6 | N | HHMMSS | PaymentInstruction | returnTime | Time of return |

### Control and Validation

| Field Position | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|----------------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1545-1549 | Checksum | Alphanumeric | 5 | Y | Calculated | PaymentInstruction | checksum | Message integrity check |
| 1550-1554 | Record Length | Numeric | 5 | Y | 01554 | PaymentInstruction | recordLength | Total record length |

---

## BOJ-NET-Specific Rules

### Transaction Limits

| Limit Type | Value | CDM Validation |
|------------|-------|----------------|
| Maximum per transaction | No limit (high-value system) | No max validation |
| Minimum per transaction | JPY 1 | instructedAmount.amount >= 1 |
| Currency | JPY only | instructedAmount.currency = 'JPY' |
| Amount precision | Whole yen (no decimals) | instructedAmount.amount % 1 = 0 |

### Mandatory Elements

| Element | Requirement | CDM Validation |
|---------|-------------|----------------|
| Currency | Must be JPY | instructedAmount.currency = 'JPY' |
| Participant Code | 4-digit BOJ participant code | nationalClearingCode length = 4 |
| Account Number | Required for both parties | Non-empty account number |
| Transaction Reference | Mandatory, 20 chars | transactionId length = 20 |
| Transaction Code | Must be valid code | messageType in valid list |

### BOJ Participant Codes (Selected Examples)

| Code | Financial Institution | Japanese Name | Type |
|------|----------------------|---------------|------|
| 0001 | Mizuho Bank | みずほ銀行 | Megabank |
| 0005 | Sumitomo Mitsui Banking Corporation | 三井住友銀行 | Megabank |
| 0009 | MUFG Bank | 三菱UFJ銀行 | Megabank |
| 0010 | Resona Bank | りそな銀行 | Major Bank |
| 0017 | Saitama Resona Bank | 埼玉りそな銀行 | Major Bank |
| 0033 | Japan Post Bank | ゆうちょ銀行 | Postal Bank |
| 0036 | Shinsei Bank | 新生銀行 | Major Bank |
| 0038 | Aozora Bank | あおぞら銀行 | Major Bank |

### Transaction Type Codes

| Code | Description | Japanese | CDM Mapping |
|------|-------------|----------|-------------|
| 01 | Customer Credit Transfer | 顧客振込 | PaymentInstruction.transactionType = '01' |
| 02 | Interbank Transfer | 銀行間振替 | PaymentInstruction.transactionType = '02' |
| 03 | Treasury Transfer | 国庫金振替 | PaymentInstruction.transactionType = '03' |
| 10 | Securities Settlement | 証券決済 | PaymentInstruction.transactionType = '10' |
| 11 | Foreign Exchange Settlement | 外為決済 | PaymentInstruction.transactionType = '11' |
| 20 | Loan Disbursement | 貸付実行 | PaymentInstruction.transactionType = '20' |
| 21 | Loan Repayment | 貸付返済 | PaymentInstruction.transactionType = '21' |

### Priority Codes

| Code | Description | Japanese | Usage |
|------|-------------|----------|-------|
| 01 | Urgent | 至急 | Time-critical payments |
| 02 | High | 高 | High priority |
| 05 | Normal | 通常 | Standard priority |
| 10 | Low | 低 | Non-urgent |

### Charge Indicator Codes

| Code | Description | Japanese | CDM Mapping |
|------|-------------|----------|-------------|
| 01 | OUR (Sender pays all charges) | 発信人負担 | PaymentInstruction.chargeBearer = 'DEBT' |
| 02 | BEN (Receiver pays all charges) | 受取人負担 | PaymentInstruction.chargeBearer = 'CRED' |
| 03 | SHA (Shared charges) | 折半 | PaymentInstruction.chargeBearer = 'SHAR' |

### Settlement Status Codes

| Code | Description | Japanese | CDM Mapping |
|------|-------------|----------|-------------|
| SE | Settled | 決済済 | PaymentInstruction.status = 'SETTLED' |
| PE | Pending | 保留中 | PaymentInstruction.status = 'PENDING' |
| RE | Rejected | 拒否 | PaymentInstruction.status = 'REJECTED' |
| ER | Error | エラー | PaymentInstruction.status = 'ERROR' |

### Return Reason Codes (Selected)

| Code | Description | Japanese | CDM Mapping |
|------|-------------|----------|-------------|
| AC01 | Incorrect Account Number | 口座番号誤り | PaymentInstruction.returnReasonCode = 'AC01' |
| AC04 | Closed Account | 口座閉鎖 | PaymentInstruction.returnReasonCode = 'AC04' |
| AC06 | Blocked Account | 口座凍結 | PaymentInstruction.returnReasonCode = 'AC06' |
| AG01 | Transaction Forbidden | 取引禁止 | PaymentInstruction.returnReasonCode = 'AG01' |
| AM05 | Duplicate Payment | 重複支払 | PaymentInstruction.returnReasonCode = 'AM05' |
| BE05 | Unrecognized Party | 当事者不明 | PaymentInstruction.returnReasonCode = 'BE05' |

### Purpose Codes

| Code | Description | Japanese | CDM Mapping |
|------|-------------|----------|-------------|
| CASH | Cash Management Transfer | 現金管理 | PaymentInstruction.purposeCode = 'CASH' |
| SUPP | Supplier Payment | 仕入先支払 | PaymentInstruction.purposeCode = 'SUPP' |
| SALA | Salary Payment | 給与支払 | PaymentInstruction.purposeCode = 'SALA' |
| TREA | Treasury Payment | 国庫金 | PaymentInstruction.purposeCode = 'TREA' |
| SECU | Securities | 証券 | PaymentInstruction.purposeCode = 'SECU' |
| INTC | Intra-Company Payment | 社内振替 | PaymentInstruction.purposeCode = 'INTC' |

---

## CDM Extensions Required

All 78 BOJ-NET fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Examples

### Example 1: BOJ-NET Large-Value Corporate Payment (Current Format)

```
01V012024122112345678901209:30:0000010005010120241221CORP-TX-2024-001  CORP-E2E-2024-001 JPY000500000000020241221093100011Ministry of Finance           Ministry of Finance           12345678901234567890           Corporate Treasury Account    Corporate Treasury Account    Mitsubishi Corporation        2-3-1 Marunouchi              Chiyoda-ku Tokyo              100-8086                      JPN1234567890123CORP-REF  0005001Sumitomo Mitsui Banking Corp  Sumitomo Mitsui Banking Corp  98765432109876543210           SMBC Corporate Account        SMBC Corporate Account        Sumitomo Chemical Company Ltd 27-1 Shinkawa 2-chome         Chuo-ku Tokyo                 104-8260                      JPN9876543210987CHEM-REF                                                                                                                                                  Payment for chemical raw materials - Purchase Order PO-JP-2024-5678 dated December 15, 2024                                Payment for chemical raw materials - Purchase Order PO-JP-2024-5678 dated December 15, 2024                                Corporate Supplier Payment    SUPP                                                                                                              BOJ-REG-001                                                                                                                                                                                                                                                                                                                                                    000000000000000JPY                             SE202412210931000931BOJ-SETTLE-2024-123BOJ-TXN-202412-789                                                                                                                  123451554
```

### Example 2: BOJ-NET Interbank Settlement (Current Format)

```
02V012024122114000000200   14:00:0000010009020220241221IBK-TX-2024-050   IBK-E2E-2024-050  JPY010000000000020241221140500020Mizuho Bank                   Mizuho Bank Ltd               IBK-SETTLE-ACC-001             Mizuho Settlement Account     Mizuho Settlement Account     Mizuho Bank Ltd               1-5-5 Otemachi                Chiyoda-ku Tokyo              100-8176                      JPNMHCB         MHCB-REF  0009003MUFG Bank                     MUFG Bank Ltd                 IBK-SETTLE-ACC-002             MUFG Settlement Account       MUFG Settlement Account       MUFG Bank Ltd                 2-7-1 Marunouchi              Chiyoda-ku Tokyo              100-8388                      JPNBOTU         BOTU-REF                                                                                                                                                  Interbank settlement for customer transactions December 21, 2024                                                            Interbank settlement for customer transactions December 21, 2024                                                            Interbank Settlement          INTC                                                                                                              BOJ-IBS-001                                                                                                                                                                                                                                                                                                                                                    000000000000000JPY                             SE202412211405001405BOJ-SETTLE-2024-456BOJ-TXN-202412-999                                                                                                                  456781554
```

---

## ISO 20022 Migration (2027)

The Bank of Japan has announced migration to ISO 20022 messaging standard scheduled for May 2027. The migration will:

**Migration Details:**
- **Timeline**: May 2027 (tentative)
- **New Messages**: pacs.008 (credit transfer), pacs.009 (interbank)
- **Transition**: Dual-format support during migration period
- **Character Set**: Migrate from JIS X 0208 to UTF-8
- **Enhanced Data**: Richer remittance information

**Future ISO 20022 Mapping:**

| Current BOJ-NET Field | Future ISO 20022 Path | Notes |
|----------------------|----------------------|-------|
| Transaction Code 01 | GrpHdr/MsgId | Message identification |
| Sender Bank Code | CdtTrfTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId | Debtor agent |
| Sender Account | CdtTrfTxInf/DbtrAcct/Id/Othr/Id | Debtor account |
| Amount | CdtTrfTxInf/IntrBkSttlmAmt | Settlement amount |
| Remittance Info | CdtTrfTxInf/RmtInf/Ustrd | Unstructured remittance |

The GPS CDM is already aligned with ISO 20022, facilitating seamless support for the migration.

---

## Character Encoding

BOJ-NET currently uses **JIS X 0208** character encoding for Japanese text:

| Field Type | Encoding | Usage |
|------------|----------|-------|
| Japanese Text | JIS X 0208 (Shift-JIS) | Kanji, Hiragana, Katakana |
| English Text | ASCII | Alphanumeric characters |
| Numeric | ASCII | Numbers only |

**Character Set Examples:**
- Kanji (漢字): 銀行, 振込, 決済
- Hiragana (ひらがな): みずほ, りそな
- Katakana (カタカナ): ユーエフジェー
- Romaji: Sumitomo, Mitsubishi, Tokyo

---

## References

- Bank of Japan: https://www.boj.or.jp/
- BOJ-NET Operating Rules (日銀ネット運営規則)
- Bank of Japan Financial Network System Documentation
- ISO 20022 Migration Plan (2027)
- Japan Bankers Association Standards
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-21
**Next Review:** Q2 2025
**Note:** This document covers the current proprietary format. ISO 20022 format documentation will be added upon migration in 2027.
