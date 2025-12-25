# SWIFT MT942 - Interim Transaction Report Mapping

## Message Overview

**Message Type:** MT942 - Interim Transaction Report
**Category:** Category 9 - Cash Management and Customer Status
**Purpose:** Sent by a financial institution to its customer to provide an intraday account statement with transaction details that exceed specified floor limits
**Direction:** FI → Customer (Bank to Corporate Customer)
**Scope:** Intraday transaction reporting for real-time cash position monitoring

**Key Use Cases:**
- Intraday cash position monitoring (multiple reports per day)
- Real-time liquidity management for treasury operations
- Large value transaction notification (above floor limits)
- Automated cash forecasting and positioning
- Working capital optimization
- Real-time account reconciliation for treasury management systems (TMS)
- Fraud detection and monitoring (immediate notification of large transactions)
- Payment exception handling and investigation
- High-frequency trading account monitoring
- Zero-balance account (ZBA) sweeping triggers

**Relationship to Other Messages:**
- **MT940**: Customer Statement Message (end-of-day statement)
- **MT950**: Customer Statement Message (alternative end-of-day format)
- **MT900**: Confirmation of Debit (single debit notification)
- **MT910**: Confirmation of Credit (single credit notification)
- **camt.052**: ISO 20022 equivalent (Bank to Customer Account Report - intraday)

**Comparison with Other MT9XX Messages:**
- **MT942**: Intraday transaction report (multiple per day, floor limit based)
- **MT940**: End-of-day statement (once per day, all transactions)
- **MT950**: End-of-day statement alternative format
- **MT900/MT910**: Single transaction confirmations (immediate, individual)

**Key Difference - Floor Limit:**
MT942 uses floor limits (Field 34F) to filter transactions. Only transactions above the specified threshold are reported, making it ideal for monitoring large-value movements without overwhelming customers with small transactions.

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in MT942** | 48 |
| **Fields Mapped to CDM** | 48 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- Account (account identification, balances)
- Party (account owner)
- FinancialInstitution (account servicing institution)
- PaymentInstruction (transaction entries, multiple per report)
- PaymentInstruction.extensions (MT942-specific fields, floor limits)

---

## Complete Field Mapping

### Mandatory Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 20 | Transaction Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction.extensions | interimReportReference | Unique interim report reference |
| 25 | Account Identification | 35x | 35 | M | Account number | Account | accountNumber | Customer's account number |
| 28C | Statement Number/Sequence | 5n[/5n] | - | M | Number[/Number] | PaymentInstruction.extensions | statementNumber, sequenceNumber | Report number and sequence |
| 34F | Floor Limit Indicator | 3!a15d | - | M | CCY + Amount | PaymentInstruction.extensions | floorLimitDebit, floorLimitCredit | Debit/Credit floor limits |
| 13D | Date/Time Indication | 6!n4!n | - | M | YYMMDDTHHMM | PaymentInstruction.extensions | reportDateTime | Report creation date/time |

### Optional Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 21 | Related Reference | 16x | 16 | O | Alphanumeric | PaymentInstruction.extensions | relatedReference | Related report reference |
| 25P | Account Identification (Option P) | 35x | 35 | O | Account | Account | accountNumber | Alternative account format |
| 60F | Opening Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account | openingBalance | Opening balance (Final) |
| 60M | Intermediate Opening Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account.extensions | intermediateOpeningBalance | Opening balance (Intermediate) |
| 61 | Statement Line | Complex | - | O | Transaction details | PaymentInstruction | Multiple attributes | Transaction entry (repeatable) |
| 62F | Closing Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account | closingBalance | Closing balance (Final) |
| 62M | Intermediate Closing Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account.extensions | intermediateClosingBalance | Closing balance (Intermediate) |
| 64 | Closing Available Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account | availableBalance | Available balance |
| 65 | Forward Available Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account.extensions | forwardAvailableBalance | Future available balance (repeatable) |
| 86 | Information to Account Owner | 6*65x | 390 | O | Free text/structured | PaymentInstruction.extensions | informationToAccountOwner | Additional transaction details |
| 90D | Number and Sum of Debit Entries | 5n15d | - | O | Count + Total | PaymentInstruction.extensions | numberOfDebits, sumOfDebits | Debit transaction summary |
| 90C | Number and Sum of Credit Entries | 5n15d | - | O | Count + Total | PaymentInstruction.extensions | numberOfCredits, sumOfCredits | Credit transaction summary |

### Field 61 Statement Line Sub-components

| Component | Description | Format | CDM Entity | CDM Attribute | Notes |
|-----------|-------------|--------|------------|---------------|-------|
| Value Date | Transaction value date | 6!n | PaymentInstruction | settlementDate | YYMMDD |
| Entry Date | Booking entry date | 4!n | PaymentInstruction.extensions | entryDate | MMDD (optional) |
| Debit/Credit Mark | Transaction direction | 2a | PaymentInstruction.extensions | debitCreditMark | C, D, RC, RD |
| Funds Code | Funds availability | a | PaymentInstruction.extensions | fundsCode | C, D (optional) |
| Amount | Transaction amount | 15d | PaymentInstruction | amount | Decimal with comma |
| Transaction Type | Transaction type code | 4!a | PaymentInstruction.extensions | transactionTypeCode | NTRF, NCHK, etc. |
| Reference for Account Owner | Customer reference | 16x | PaymentInstruction | endToEndId | Customer's reference |
| Bank Reference | Bank's reference | 16x | PaymentInstruction.extensions | bankReference | Bank reference (optional) |
| Supplementary Details | Additional info | 34x | PaymentInstruction.extensions | supplementaryDetails | Extra details (optional) |

---

## Detailed Field Mappings

### Field 20: Transaction Reference Number

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :20: | 16x | PaymentInstruction.extensions | interimReportReference | Mandatory. Unique reference for this interim report |

**Example:**
```
:20:INTRADAY20241220
```

**Usage:** Bank's unique identifier for this intraday report. Differentiates from end-of-day MT940 statement reference.

### Field 21: Related Reference

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :21: | 16x | PaymentInstruction.extensions | relatedReference | Reference to related report or previous interim report |

**Example:**
```
:21:PREVREPORT1219
```

**Usage:** Optional. Links to previous interim report or references related message.

### Field 13D: Date/Time Indication

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :13D: | 6!n4!n | PaymentInstruction.extensions | reportDateTime | Mandatory. Report creation date and time |

**Example:**
```
:13D:2412201030
:13D:2412201530
:13D:2412201800
```

**Components:**
- **241220** - Date (YYMMDD) - December 20, 2024
- **1030** - Time (HHMM) - 10:30 AM
- **1530** - Time (HHMM) - 3:30 PM
- **1800** - Time (HHMM) - 6:00 PM

**Usage:** Critical for intraday reporting. Multiple MT942 messages sent throughout the day have different timestamps. This allows customers to track the sequence and timing of intraday reports.

### Field 25: Account Identification

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :25: | 35x | Account | accountNumber | Mandatory. Customer's account number |

**Example:**
```
:25:GB29NWBK60161331926819
:25:/GB29NWBK60161331926819
:25:1234567890
```

**Notes:**
- May include IBAN, BBAN, or proprietary account number
- Leading slash (/) indicates structured format
- Same account may receive multiple MT942 reports per day

### Field 25P: Account Identification (Option P)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :25P: | 35x | Account | accountNumber | Alternative account identification |

**Example:**
```
:25P:GB29NWBK60161331926819
```

**Usage:** Alternative to field 25. Less common in MT942.

### Field 28C: Statement Number/Sequence Number

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :28C: | 5n[/5n] | PaymentInstruction.extensions | statementNumber, sequenceNumber | Report number and page/sequence |

**Example:**
```
:28C:00001/001
:28C:00001/002
:28C:00002/001
```

**Format:**
- **00001/001** - Report 1, page 1 (morning report)
- **00001/002** - Report 1, page 2 (continuation)
- **00002/001** - Report 2, page 1 (afternoon report)

**Usage:** Sequential numbering for intraday reports. First number increments for each new interim report; second number for multi-page reports.

### Field 34F: Floor Limit Indicator (CRITICAL FOR MT942)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :34F: | 3!a15d | PaymentInstruction.extensions | floorLimitDebit, floorLimitCredit | Mandatory. Transaction threshold for reporting |

**Example:**
```
:34F:USD100000,
:34F:EUR50000,
```

**Usage:**
- **CRITICAL FIELD** - Defines minimum transaction size to be reported
- Only transactions >= floor limit are included in MT942
- Debit floor limit: Only debits above this amount reported
- Credit floor limit: Only credits above this amount reported
- Reduces message volume by filtering small transactions
- Different floor limits can be set for debits vs credits
- Floor limits typically set based on customer requirements and risk tolerance

**Example Scenarios:**
- Floor limit USD 100,000: Only transactions >= $100k reported
- Small transactions (< floor) appear only in end-of-day MT940
- Large transactions (>= floor) appear in MT942 AND MT940

**CDM Mapping:**
- First occurrence: floorLimitDebit (if debit indicator)
- Second occurrence: floorLimitCredit (if credit indicator)
- Or: Single floor limit applies to both debits and credits

### Field 60F: Opening Balance (Final)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :60F: | a6!n3!a15d | Account | openingBalance | First/Final opening balance |

**Example:**
```
:60F:C241220USD5000000,00
```

**Components:**
- **C** - Credit balance (or D for Debit)
- **241220** - December 20, 2024 (same day as report for intraday)
- **USD** - US Dollars
- **5000000,00** - $5,000,000.00

**Usage:** Opening balance at start of business day (or start of reporting period for this interim report).

### Field 60M: Opening Balance (Intermediate)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :60M: | a6!n3!a15d | Account.extensions | intermediateOpeningBalance | Intermediate opening balance |

**Example:**
```
:60M:C241220USD5000000,00
```

**Usage:** Used for multi-page interim reports. Indicates balance from previous page.

### Field 61: Statement Line (Transaction Detail)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :61: | Complex | PaymentInstruction | Multiple attributes | Transaction entry (repeatable, floor limit filtered) |

**Format:**
```
:61:YYMMDD[MMDD][DC][F]Amount[N]TransactionType[//BankRef]
[//SupplementaryDetails]
CustomerRef
```

**Example:**
```
:61:2412201220C2500000,NTRFNONREF//WIRE-IN-12345
CLIENT-PMT-20241220
```

**Component Breakdown:**
- **241220** - Value date (Dec 20, 2024)
- **1220** - Entry date/time (12:20) - hour and minute for intraday
- **C** - Credit mark
- **2500000,** - Amount 2,500,000.00 (ABOVE FLOOR LIMIT)
- **NTRF** - Transaction type (Transfer)
- **NONREF** - Additional reference
- **//WIRE-IN-12345** - Bank reference
- **CLIENT-PMT-20241220** - Customer reference

**IMPORTANT:** Only transactions meeting or exceeding field 34F floor limit are included.

**Debit/Credit Marks:**
- **C** - Credit
- **D** - Debit
- **RC** - Reversal of Credit
- **RD** - Reversal of Debit

**CDM Mapping:**
- PaymentInstruction.settlementDate = Value Date
- PaymentInstruction.extensions.entryDate = Entry Date/Time
- PaymentInstruction.extensions.debitCreditMark = C/D/RC/RD
- PaymentInstruction.extensions.fundsCode = C/D
- PaymentInstruction.amount = Amount (>= floor limit)
- PaymentInstruction.extensions.transactionTypeCode = Transaction Type
- PaymentInstruction.endToEndId = Customer Reference
- PaymentInstruction.extensions.bankReference = Bank Reference
- PaymentInstruction.extensions.supplementaryDetails = Supplementary Details

### Field 62F: Closing Balance (Final)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :62F: | a6!n3!a15d | Account | closingBalance | Final closing balance at time of report |

**Example:**
```
:62F:C241220USD7000000,00
```

**Components:**
- **C** - Credit balance
- **241220** - December 20, 2024 (same day - intraday balance)
- **USD** - US Dollars
- **7000000,00** - $7,000,000.00

**Usage:** Current balance at the time of this interim report. This is an intraday snapshot, not final end-of-day balance.

### Field 62M: Closing Balance (Intermediate)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :62M: | a6!n3!a15d | Account.extensions | intermediateClosingBalance | Intermediate closing for multi-page |

**Example:**
```
:62M:C241220USD7000000,00
```

**Usage:** Used for multi-page interim reports. Balance continues to next page.

### Field 64: Closing Available Balance

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :64: | a6!n3!a15d | Account | availableBalance | Available balance at time of report |

**Example:**
```
:64:C241220USD8000000,00
```

**Usage:** Available balance = Closing balance + Credit line - Holds/Reserves
- Example: Closing $7M + Credit line $1M = Available $8M
- Critical for intraday liquidity management

### Field 65: Forward Available Balance

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :65: | a6!n3!a15d | Account.extensions | forwardAvailableBalance | Future dated available balance (repeatable) |

**Example:**
```
:65:C241221USD7500000,00
:65:C241222USD7000000,00
```

**Usage:** Projected available balances for future dates based on known scheduled transactions.

### Field 86: Information to Account Owner

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :86: | 6*65x | PaymentInstruction.extensions | informationToAccountOwner | Additional transaction details (up to 390 chars) |

**Example:**
```
:86:/ORDP/Large Customer Corp
/IBAN/US12345678901234567890
/EREF/URGENT-PMT-20241220
/REMI/Time-sensitive payment
/PURP/GDDS
```

**Common Structured Tags:**
- **/ORDP/** - Ordering party
- **/BENM/** - Beneficiary name
- **/IBAN/** - IBAN
- **/BIC/** - BIC
- **/EREF/** - End-to-end reference
- **/REMI/** - Remittance information
- **/PURP/** - Purpose code

### Field 90D: Number and Sum of Debit Entries

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :90D: | 5n15d | PaymentInstruction.extensions | numberOfDebits, sumOfDebits | Summary of debit transactions |

**Example:**
```
:90D:000053500000,00
```

**Components:**
- **00005** - 5 debit transactions (above floor limit)
- **3500000,00** - Total debits: $3,500,000.00

**Usage:** Summary count and total for all debits in this interim report (floor limit filtered).

### Field 90C: Number and Sum of Credit Entries

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :90C: | 5n15d | PaymentInstruction.extensions | numberOfCredits, sumOfCredits | Summary of credit transactions |

**Example:**
```
:90C:000085000000,00
```

**Components:**
- **00008** - 8 credit transactions (above floor limit)
- **5000000,00** - Total credits: $5,000,000.00

**Usage:** Summary count and total for all credits in this interim report (floor limit filtered).

---

## Transaction Type Codes (Field 61)

Common SWIFT transaction type codes in MT942 (same as MT940):

### Large Value Payment Codes (Common in MT942)
| Code | Description |
|------|-------------|
| NTRF | Transfer (most common for large transactions) |
| NWIT | Wire Transfer (domestic/international large value) |
| NFEX | Foreign Exchange (FX settlement) |
| NSEC | Securities (settlement payments) |

### Other Codes
| Code | Description |
|------|-------------|
| NEFT | Electronic Funds Transfer |
| NCHK | Cheque (large value checks) |
| NLOA | Loan (disbursement/repayment) |
| NDIV | Dividend (large dividend payments) |
| NINT | Interest (large interest payments) |
| NCHG | Charges/Fees |

**Note:** Small transaction codes (NATM, NCRD, NRTL) rarely appear in MT942 due to floor limits.

---

## Code Lists and Enumerations

### Debit/Credit Indicators (Fields 60, 62, 64, 65)

| Code | Description |
|------|-------------|
| C | Credit balance |
| D | Debit balance |

### Debit/Credit Marks (Field 61)

| Code | Description |
|------|-------------|
| C | Credit (funds added) |
| D | Debit (funds removed) |
| RC | Reversal of Credit |
| RD | Reversal of Debit |

### Funds Code (Field 61)

| Code | Description |
|------|-------------|
| C | Credit - Funds available immediately |
| D | Debit - Funds debited immediately |

---

## Message Examples

### Example 1: Morning Interim Report (10:30 AM) - Large Wire Received

```
{1:F01NWBKGB2LAXXX0000000000}
{2:I942ABCBGB2LXXXXN}
{4:
:20:INTRA-20241220-01
:25:GB29NWBK60161331926819
:28C:00001/001
:34F:USD100000,
:13D:2412201030
:60F:C241220USD5000000,00
:61:2412200925C2500000,NWIT NONREF//WIRE-IN-001
CLIENT-PMT-001
:86:/ORDP/Global Customer Corp
/IBAN/US12345678901234567890
/EREF/URGENT-PMT-DEC20
/REMI/Large payment received
/PURP/SUPP
:62F:C241220USD7500000,00
:64:C241220USD8250000,00
:90D:0000000000,00
:90C:000012500000,00
-}
```

**Explanation:**
- First interim report of the day (10:30 AM)
- Floor limit: USD 100,000 (only transactions >= $100k reported)
- Opening balance (start of day): USD 5,000,000.00
- Transaction at 09:25: Credit $2,500,000 wire received (ABOVE floor limit)
- Closing balance (at 10:30 AM): USD 7,500,000.00
- Available: USD 8,250,000.00 (includes $750k credit line)
- Summary: 0 debits, 1 credit totaling $2.5M

### Example 2: Midday Interim Report (2:30 PM) - Multiple Large Transactions

```
{1:F01CHASUS33AXXX0000000000}
{2:I942CORPUS33XXXXN}
{4:
:20:INTRA-20241220-02
:25:1234567890
:28C:00002/001
:34F:USD500000,
:13D:2412201430
:60F:C241220USD10000000,00
:61:2412201015C1500000,NTRFNONREF//TRF-IN-002
EXPORT-PMT-001
:86:/ORDP/International Buyer
/EREF/EXPORT-2024-555
/REMI/Export payment for goods
:61:2412201145D3000000,NWIT NONREF//WIRE-OUT-001
SUPPLIER-PMT-001
:86:/BENM/Equipment Supplier Inc
/IBAN/GB29NWBK60161331926819
/EREF/PO-2024-9999
/REMI/Payment for equipment
:61:2412201320C5000000,NSECNONREF//SEC-SETTLE-001
SECURITIES-001
:86:/REMI/Securities settlement
/PURP/SECU
:62F:C241220USD13500000,00
:64:C241220USD15500000,00
:65:C241221USD15000000,00
:90D:000013000000,00
:90C:000026500000,00
-}
```

**Explanation:**
- Second interim report (2:30 PM)
- Floor limit: USD 500,000 (higher threshold)
- Opening (start of day): USD 10,000,000.00
- Transactions (all >= $500k floor):
  - 10:15 AM: Credit $1,500,000 (Export payment)
  - 11:45 AM: Debit $3,000,000 (Wire to supplier)
  - 1:20 PM: Credit $5,000,000 (Securities settlement)
- Closing (at 2:30 PM): USD 13,500,000.00
- Available: USD 15,500,000.00
- Forward (Dec 21): USD 15,000,000.00
- Summary: 1 debit ($3M), 2 credits ($6.5M)
- Small transactions (< $500k) not shown, will appear in MT940

### Example 3: End-of-Day Interim Report (5:00 PM) - EUR Account

```
{1:F01DEUTDEFFAXXX0000000000}
{2:I942CORPDEFFXXXXN}
{4:
:20:INTRA-20241220-03
:25:DE89370400440532013000
:28C:00003/001
:34F:EUR250000,
:13D:2412201700
:60F:C241220EUR8000000,00
:61:2412201505D2000000,NFEXNONREF//FX-EUR-USD
FX-SETTLE-001
:86:/REMI/FX settlement EUR to USD
/PURP/FXNT
/EREF/FX-SPOT-20241220
:61:2412201545C3500000,NTRFNONREF//SEPA-IN-001
SEPA-LARGE-001
:86:/ORDP/French Customer SA
/IBAN/FR1420041010050500013M02606
/EREF/INV-FR-2024-888
/REMI/Large SEPA payment
:61:2412201635D500000,NLOANONREF//LOAN-PMT
LOAN-REPAY-001
:86:/REMI/Loan repayment installment
/EREF/LOAN-2024-001
:62F:C241220EUR9000000,00
:64:C241220EUR10000000,00
:65:C241221EUR9750000,00
:90D:000022500000,00
:90C:000013500000,00
-}
```

**Explanation:**
- Third interim report (5:00 PM, late afternoon)
- Floor limit: EUR 250,000
- Opening (start of day): EUR 8,000,000.00
- Large transactions during afternoon:
  - 3:05 PM: Debit EUR 2,000,000 (FX settlement)
  - 3:45 PM: Credit EUR 3,500,000 (Large SEPA)
  - 4:35 PM: Debit EUR 500,000 (Loan repayment)
- Closing (at 5:00 PM): EUR 9,000,000.00
- Available: EUR 10,000,000.00
- Summary: 2 debits (EUR 2.5M), 1 credit (EUR 3.5M)

### Example 4: High-Frequency Trading Account - Multiple Interim Reports

```
{1:F01HSBCHKHHAXXX0000000000}
{2:I942TRADEHKHXXXXN}
{4:
:20:INTRA-20241220-05
:25:/HK9876543210987654
:28C:00005/001
:34F:HKD5000000,
:13D:2412201545
:60F:C241220HKD50000000,00
:61:2412201510C15000000,NSECNONREF//SEC-BUY-001
TRADE-001
:86:/REMI/Securities purchase
/PURP/SECU
:61:2412201525D20000000,NSECNONREF//SEC-SELL-001
TRADE-002
:86:/REMI/Securities sale
/PURP/SECU
:61:2412201535C25000000,NFEXNONREF//FX-HKD-USD
FX-TRADE-001
:86:/REMI/FX trade settlement
/PURP/FXNT
:61:2412201542D8000000,NSECNONREF//SEC-BUY-002
TRADE-003
:86:/REMI/Securities purchase
/PURP/SECU
:62F:C241220HKD62000000,00
:64:C241220HKD65000000,00
:90D:0000228000000,00
:90C:0000240000000,00
-}
```

**Explanation:**
- Fifth interim report of the day (3:45 PM) - high frequency trading
- Floor limit: HKD 5,000,000 (very active account)
- Opening: HKD 50,000,000.00
- 4 large transactions in 35 minutes:
  - 3:10 PM: Credit HKD 15M (Securities buy)
  - 3:25 PM: Debit HKD 20M (Securities sell)
  - 3:35 PM: Credit HKD 25M (FX trade)
  - 3:42 PM: Debit HKD 8M (Securities buy)
- Closing (at 3:45 PM): HKD 62,000,000.00
- Available: HKD 65,000,000.00
- Summary: 2 debits (HKD 28M), 2 credits (HKD 40M)
- Multiple reports per day for active trading account

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 48 fields in MT942 successfully map to existing GPS CDM entities:
- Account entity handles account identification, intraday balances
- PaymentInstruction entity (repeatable) handles each large transaction
- Extension fields accommodate MT942-specific elements (floor limits, report timing, intraday numbering)
- FinancialInstitution entity supports account servicing institution
- Party entity supports account owner

**Key Extension Fields Used:**
- interimReportReference (Field 20 - unique interim report ID)
- relatedReference (Field 21 - related report link)
- reportDateTime (Field 13D - mandatory report timestamp for intraday tracking)
- statementNumber (Field 28C - incremental report number)
- sequenceNumber (Field 28C - page for multi-page reports)
- floorLimitDebit (Field 34F - mandatory debit threshold)
- floorLimitCredit (Field 34F - mandatory credit threshold)
- intermediateOpeningBalance (Field 60M - multi-page opening)
- intermediateClosingBalance (Field 62M - multi-page closing)
- forwardAvailableBalance (Field 65 - projected balances)
- numberOfDebits (Field 90D - count of large debits)
- sumOfDebits (Field 90D - total of large debits)
- numberOfCredits (Field 90C - count of large credits)
- sumOfCredits (Field 90C - total of large credits)
- entryDate (Field 61 - intraday timestamp critical for sequencing)
- debitCreditMark (Field 61 - C/D/RC/RD)
- fundsCode (Field 61 - funds availability)
- transactionTypeCode (Field 61 - NTRF, NWIT, NSEC, etc.)
- bankReference (Field 61 - bank's transaction reference)
- supplementaryDetails (Field 61 - additional info)
- informationToAccountOwner (Field 86 - structured transaction details)

**Floor Limit Processing:**
- MT942 messages filter transactions based on field 34F floor limit
- PaymentInstruction records flagged with `aboveFloorLimit: true` attribute
- Transactions below floor limit stored but not reported in MT942
- All transactions (including below-floor) appear in end-of-day MT940

---

## MT942 vs MT940 Comparison

| Aspect | MT942 (Interim) | MT940 (Statement) |
|--------|-----------------|-------------------|
| **Frequency** | Multiple per day (intraday) | Once per day (end-of-day) |
| **Field 13D** | Mandatory (timestamp critical) | Optional |
| **Field 34F** | Mandatory (floor limit required) | Optional (rarely used) |
| **Transactions** | Only above floor limit | All transactions |
| **Purpose** | Real-time monitoring | Daily reconciliation |
| **Timing** | Throughout business day | After close of business |
| **Balances** | Intraday snapshots | Final daily balances |
| **Volume** | Lower (filtered) | Higher (complete) |
| **Use Case** | Liquidity management | Accounting reconciliation |

---

## References

- **SWIFT Standards:** MT942 - Interim Transaction Report
- **SWIFT Standards Release:** 2024
- **Category:** Cat 9 - Cash Management and Customer Status
- **Related Messages:** MT940, MT950, MT900, MT910, camt.052
- **ISO 20022 Equivalent:** camt.052 - Bank to Customer Account Report (Interim)

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
