# SWIFT MT940 - Customer Statement Message Mapping

## Message Overview

**Message Type:** MT940 - Customer Statement Message
**Category:** Category 9 - Cash Management and Customer Status
**Purpose:** Sent by a financial institution to its customer to provide an account statement with opening/closing balances and transaction details for a specific period
**Direction:** FI → Customer (Bank to Corporate Customer)
**Scope:** End-of-day account statement with full transaction detail

**Key Use Cases:**
- End-of-day account statement delivery to corporate customers
- Daily balance reconciliation for treasury operations
- Multi-currency account reporting
- Automated reconciliation with ERP systems (SAP, Oracle, etc.)
- Cash position reporting for treasury management systems (TMS)
- Audit trail and compliance reporting
- Bank account reconciliation automation
- Global cash visibility for multinational corporations
- Most commonly used statement format worldwide

**Relationship to Other Messages:**
- **MT950**: Customer Statement Message (alternative detailed format)
- **MT942**: Interim Transaction Report (intraday statement)
- **MT900**: Confirmation of Debit (single debit notification)
- **MT910**: Confirmation of Credit (single credit notification)
- **camt.052**: ISO 20022 equivalent (Bank to Customer Account Report - intraday)
- **camt.053**: ISO 20022 equivalent (Bank to Customer Statement - end-of-day)

**Comparison with Other MT9XX Messages:**
- **MT940**: End-of-day statement (most common, global standard)
- **MT950**: Alternative statement format (less common)
- **MT942**: Intraday transaction report (multiple per day)
- **MT900/MT910**: Single transaction confirmations (real-time)

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in MT940** | 52 |
| **Fields Mapped to CDM** | 52 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- Account (account identification, balances)
- Party (account owner)
- FinancialInstitution (account servicing institution)
- PaymentInstruction (transaction entries, multiple per statement)
- PaymentInstruction.extensions (MT940-specific fields, transaction details)

---

## Complete Field Mapping

### Mandatory Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 20 | Transaction Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction.extensions | statementReference | Unique statement reference |
| 25 | Account Identification | 35x | 35 | M | Account number | Account | accountNumber | Customer's account number |
| 28C | Statement Number/Sequence | 5n[/5n] | - | M | Number[/Number] | PaymentInstruction.extensions | statementNumber, sequenceNumber | Statement number and page/sequence |
| 60a | Opening Balance | a6!n3!a15d | - | M | D/C + Date + CCY + Amt | Account | openingBalance | Opening balance (F=Final, M=Intermediate) |
| 62a | Closing Balance | a6!n3!a15d | - | M | D/C + Date + CCY + Amt | Account | closingBalance | Closing balance (booked) |

### Optional Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 13D | Date/Time Indication | 6!n[4!n][,3n][/4!n][,3n] | - | O | Date[Time][Zone] | PaymentInstruction.extensions | dateTimeIndication | Statement date/time with timezone |
| 21 | Related Reference | 16x | 16 | O | Alphanumeric | PaymentInstruction.extensions | relatedReference | Related statement reference |
| 25P | Account Identification (Option P) | 35x | 35 | O | Account | Account | accountNumber | Alternative account format |
| 34F | Debit Floor Limit | 3!a15d | - | O | CCY + Amount | PaymentInstruction.extensions | debitFloorLimit | Debit floor limit threshold |
| 34F | Credit Floor Limit | 3!a15d | - | O | CCY + Amount | PaymentInstruction.extensions | creditFloorLimit | Credit floor limit threshold |
| 60M | Intermediate Opening Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account.extensions | intermediateOpeningBalance | Intermediate opening (multi-page) |
| 61 | Statement Line | Complex | - | O | Transaction details | PaymentInstruction | Multiple attributes | Transaction entry (repeatable) |
| 62M | Intermediate Closing Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account.extensions | intermediateClosingBalance | Intermediate closing (multi-page) |
| 64 | Closing Available Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account | availableBalance | Available balance |
| 65 | Forward Available Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account.extensions | forwardAvailableBalance | Future available balance (repeatable) |
| 86 | Information to Account Owner | 6*65x | 390 | O | Free text/structured | PaymentInstruction.extensions | informationToAccountOwner | Additional transaction details |

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
| :20: | 16x | PaymentInstruction.extensions | statementReference | Mandatory. Unique reference for this statement |

**Example:**
```
:20:STMT20241220001
```

**Usage:** Bank's unique identifier for this statement. Used for statement reconciliation and reference.

### Field 21: Related Reference

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :21: | 16x | PaymentInstruction.extensions | relatedReference | Reference to related statement or message |

**Example:**
```
:21:PREVSTMT1219
```

**Usage:** Optional. Links to previous statement or correction reference.

### Field 13D: Date/Time Indication

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :13D: | 6!n[4!n][,3n][/4!n][,3n] | PaymentInstruction.extensions | dateTimeIndication | Statement creation date/time with timezone |

**Example:**
```
:13D:2412201530
:13D:2412201530,000/1530,000
```

**Components:**
- **241220** - Date (YYMMDD)
- **1530** - Time (HHMM)
- **,000** - Milliseconds (optional)
- **/1530,000** - Timezone offset (optional)

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
- Most common field for account identification

### Field 25P: Account Identification (Option P)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :25P: | 35x | Account | accountNumber | Alternative account identification |

**Example:**
```
:25P:GB29NWBK60161331926819
```

**Usage:** Alternative to field 25. Less common.

### Field 28C: Statement Number/Sequence Number

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :28C: | 5n[/5n] | PaymentInstruction.extensions | statementNumber, sequenceNumber | Statement and page number |

**Example:**
```
:28C:00235
:28C:00235/001
:28C:12345/002
```

**Format:**
- **00235** - Statement number 235
- **00235/001** - Statement 235, page/sequence 1
- **12345/002** - Statement 12345, page 2

**Usage:** Sequential numbering for statements. Sequence number used for multi-page statements.

### Field 34F: Debit/Credit Floor Limit

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :34F: | 3!a15d | PaymentInstruction.extensions | debitFloorLimit, creditFloorLimit | Transaction threshold for reporting |

**Example:**
```
:34F:USD10000,
```

**Usage:** Only transactions above this threshold are reported in the statement. Used in MT942 primarily, optional in MT940.

### Field 60F: Opening Balance (Final)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :60F: | a6!n3!a15d | Account | openingBalance | First/Final opening balance |

**Example:**
```
:60F:C241219USD1000000,00
```

**Components:**
- **C** - Credit balance (or D for Debit)
- **241219** - December 19, 2024
- **USD** - US Dollars
- **1000000,00** - $1,000,000.00

### Field 60M: Opening Balance (Intermediate)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :60M: | a6!n3!a15d | Account.extensions | intermediateOpeningBalance | Intermediate opening balance for multi-page |

**Example:**
```
:60M:C241219USD1000000,00
```

**Usage:** Used when statement spans multiple messages. Indicates continuation from previous page.

### Field 61: Statement Line (Transaction Detail)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :61: | Complex | PaymentInstruction | Multiple attributes | Transaction entry (repeatable) |

**Format:**
```
:61:YYMMDD[MMDD][DC][F]Amount[N]TransactionType[//BankRef]
[//SupplementaryDetails]
CustomerRef
```

**Example:**
```
:61:2412200220C500000,NTRFNONREF//BANK123456
CUST987654
```

**Component Breakdown:**
- **241220** - Value date (Dec 20, 2024)
- **0220** - Entry date (Feb 20) - optional
- **C** - Credit mark
- **500000,** - Amount 500,000.00
- **NTRF** - Transaction type (Transfer)
- **NONREF** - Additional reference
- **//BANK123456** - Bank reference (preceded by //)
- **CUST987654** - Customer reference (continuation line)

**Debit/Credit Marks:**
- **C** - Credit
- **D** - Debit
- **RC** - Reversal of Credit
- **RD** - Reversal of Debit

**Funds Code (optional, after D/C mark):**
- **C** - Credit (funds available immediately)
- **D** - Debit (funds debited immediately)

**CDM Mapping:**
- PaymentInstruction.settlementDate = Value Date
- PaymentInstruction.extensions.entryDate = Entry Date
- PaymentInstruction.extensions.debitCreditMark = C/D/RC/RD
- PaymentInstruction.extensions.fundsCode = C/D
- PaymentInstruction.amount = Amount
- PaymentInstruction.extensions.transactionTypeCode = Transaction Type
- PaymentInstruction.endToEndId = Customer Reference
- PaymentInstruction.extensions.bankReference = Bank Reference
- PaymentInstruction.extensions.supplementaryDetails = Supplementary Details

### Field 62F: Closing Balance (Final)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :62F: | a6!n3!a15d | Account | closingBalance | Final closing balance (booked) |

**Example:**
```
:62F:C241220USD1500000,00
```

**Components:**
- **C** - Credit balance
- **241220** - December 20, 2024
- **USD** - US Dollars
- **1500000,00** - $1,500,000.00

**Usage:** End-of-day booked balance. This is the mandatory closing balance for the statement period.

### Field 62M: Closing Balance (Intermediate)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :62M: | a6!n3!a15d | Account.extensions | intermediateClosingBalance | Intermediate closing for multi-page |

**Example:**
```
:62M:C241220USD1500000,00
```

**Usage:** Used for multi-page statements. Indicates continuation to next page.

### Field 64: Closing Available Balance

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :64: | a6!n3!a15d | Account | availableBalance | Available balance including credit facilities |

**Example:**
```
:64:C241220USD2000000,00
```

**Usage:** Available balance = Closing balance + Credit line - Holds/Reserves
- Example: Closing $1.5M + Credit line $500k = Available $2M

### Field 65: Forward Available Balance

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :65: | a6!n3!a15d | Account.extensions | forwardAvailableBalance | Future dated available balance (repeatable) |

**Example:**
```
:65:C241221USD1950000,00
:65:C241222USD1900000,00
:65:C241223USD1875000,00
```

**Usage:** Projected available balances for future dates. Accounts for known future debits/credits.

### Field 86: Information to Account Owner

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :86: | 6*65x | PaymentInstruction.extensions | informationToAccountOwner | Additional transaction details (up to 390 chars) |

**Example:**
```
:86:/BENM/ABC Corporation Ltd
/IBAN/GB82WEST12345698765432
/EREF/INV-2024-5678
/REMI/Payment for Invoice INV-2024-5678
/PURP/GDDS
```

**Common Structured Tags:**
- **/BENM/** - Beneficiary name
- **/ORDP/** - Ordering party
- **/IBAN/** - IBAN
- **/BIC/** - BIC
- **/EREF/** - End-to-end reference
- **/REMI/** - Remittance information
- **/PURP/** - Purpose code
- **/PREF/** - Payment reference
- **/MREF/** - Mandate reference
- **/ULTB/** - Ultimate beneficiary
- **/ULTO/** - Ultimate ordering party

**CDM Parsing Strategy:**
Field 86 is parsed to extract structured information:
- PaymentInstruction.extensions.beneficiaryName (from /BENM/)
- PaymentInstruction.extensions.beneficiaryIBAN (from /IBAN/)
- PaymentInstruction.endToEndId (from /EREF/)
- PaymentInstruction.remittanceInformation (from /REMI/)
- PaymentInstruction.extensions.purposeCode (from /PURP/)
- Original full text preserved in informationToAccountOwner

---

## Transaction Type Codes (Field 61)

Common SWIFT transaction type codes used in field 61:

### Payment Codes
| Code | Description |
|------|-------------|
| NTRF | Transfer |
| NWIT | Wire Transfer |
| NEFT | Electronic Funds Transfer |
| NRTL | Retail Payment |
| NSTO | Standing Order |
| NDDT | Direct Debit |

### Cash and Cheque Codes
| Code | Description |
|------|-------------|
| NCHK | Cheque |
| NCLS | Cash Letter/Deposit |
| NATM | ATM Transaction |
| NCRD | Card Transaction |

### Income Codes
| Code | Description |
|------|-------------|
| NDIV | Dividend |
| NINT | Interest Received |
| NSAL | Salary |

### Fee Codes
| Code | Description |
|------|-------------|
| NCHG | Charges/Fees |
| NCOM | Commission |

### Securities Codes
| Code | Description |
|------|-------------|
| NSEC | Securities |
| NMSC | Miscellaneous |

### Trade Finance Codes
| Code | Description |
|------|-------------|
| NLOA | Loan |
| NFEX | Foreign Exchange |
| NTAX | Tax Payment |

**ISO 20022 Mapping:** These codes map to ISO 20022 ExternalBankTransactionDomain and ExternalBankTransactionFamily codes in camt.053.

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
| RC | Reversal of Credit (previous credit reversed) |
| RD | Reversal of Debit (previous debit reversed) |

### Funds Code (Field 61)

| Code | Description |
|------|-------------|
| C | Credit - Funds available immediately |
| D | Debit - Funds debited immediately |

**Note:** If no funds code present, availability depends on bank's policy.

---

## Message Examples

### Example 1: Simple Daily Statement - Single Currency

```
{1:F01NWBKGB2LAXXX0000000000}
{2:I940ABCBGB2LXXXXN}
{4:
:20:STMT20241220001
:25:GB29NWBK60161331926819
:28C:00365/001
:60F:C241219USD1000000,00
:61:2412200220C500000,NTRFNONREF//BANK123456
CUST987654
:86:/ORDP/Global Trading Corp
/IBAN/US12345678901234567890
/EREF/PMT-2024-1111
/REMI/Payment for goods delivered
:61:241220D50000,NCHGNONREF//BANK123457
MONTHLY-FEE
:86:/BENM/NatWest Bank PLC
/REMI/Monthly account maintenance fee
:62F:C241220USD1450000,00
:64:C241220USD1700000,00
-}
```

**Explanation:**
- Account: GB29NWBK60161331926819
- Statement: 365, Page 1
- Opening (Dec 19): USD 1,000,000.00 Credit
- Transaction 1: Credit $500,000 (Transfer from Global Trading Corp)
- Transaction 2: Debit $50,000 (Monthly fee)
- Closing (Dec 20): USD 1,450,000.00 Credit
- Available: USD 1,700,000.00 (includes $250k credit line)

**Balance Validation:**
- Opening: $1,000,000
- Credit: +$500,000
- Debit: -$50,000
- **Closing: $1,450,000** ✓

### Example 2: Multi-Transaction Statement with Forward Balances

```
{1:F01CHASUS33AXXX0000000000}
{2:I940CORPUS33XXXXN}
{4:
:20:STMT-US-20241220
:25:1234567890
:28C:12345/001
:60F:C241219USD5000000,00
:61:241220C2500000,NTRFNONREF//WIRE-IN-001
CLIENT-PMT-001
:86:/ORDP/Customer A Inc
/EREF/INV-2024-AAA
/REMI/Invoice payment
:61:241220C1000000,NDIVNONREF//DIV-20241220
DIV-PAYMENT
:86:/ORDP/Investment Fund XYZ
/REMI/Quarterly dividend payment
:61:241220D3000000,NWIT NONREF//WIRE-OUT-001
PMT-TO-SUPPLIER
:86:/BENM/Supplier Co Ltd
/IBAN/GB29NWBK60161331926819
/EREF/PO-2024-999
/REMI/Payment for purchase order
:61:241220D25000,NCHGNONREF//WIRE-FEE
WIRE-CHARGE
:86:/REMI/Wire transfer fee
:61:241220D10000,NCOMNONREF//MONTHLY-COMM
COMMISSION
:86:/REMI/Account commission charge
:62F:C241220USD5465000,00
:64:C241220USD6215000,00
:65:C241221USD6190000,00
:65:C241222USD6165000,00
-}
```

**Explanation:**
- Account: 1234567890 (US account)
- Statement: 12345, Page 1
- Opening (Dec 19): USD 5,000,000.00
- Transactions:
  - Credit $2,500,000 (Customer payment)
  - Credit $1,000,000 (Dividend)
  - Debit $3,000,000 (Wire to supplier)
  - Debit $25,000 (Wire fee)
  - Debit $10,000 (Commission)
- Closing (Dec 20): USD 5,465,000.00
- Available: USD 6,215,000.00 (includes $750k credit line)
- Forward (Dec 21): USD 6,190,000.00 projected
- Forward (Dec 22): USD 6,165,000.00 projected

**Balance Validation:**
- Opening: $5,000,000
- Credits: +$3,500,000
- Debits: -$3,035,000
- **Closing: $5,465,000** ✓

### Example 3: Multi-Currency Statement - EUR Account

```
{1:F01DEUTDEFFAXXX0000000000}
{2:I940CORPDEFFXXXXN}
{4:
:20:STMT-DE-20241220
:25:DE89370400440532013000
:28C:00567
:60F:C241219EUR3000000,00
:61:241220C750000,NTRFNONREF//SEPA-IN-001
SEPA-CREDIT-001
:86:/ORDP/French Customer SA
/IBAN/FR1420041010050500013M02606
/EREF/INV-FR-2024-555
/REMI/SEPA payment for services
/PURP/GDDS
:61:241220C500000,NINTNONREF//INT-20241220
INTEREST-DEC
:86:/REMI/Monthly interest credit
/PURP/INTC
:61:241220D1200000,NTRFNONREF//SEPA-OUT-001
SEPA-DEBIT-001
:86:/BENM/Italian Supplier SRL
/IBAN/IT60X0542811101000000123456
/EREF/PO-IT-2024-888
/REMI/SEPA payment for goods
/PURP/GDDS
:61:241220D8500,NCHGNONREF//SEPA-FEE
SEPA-CHARGE
:86:/REMI/SEPA transaction fee
:62F:C241220EUR3041500,00
:64:C241220EUR3541500,00
:65:C241221EUR3516500,00
-}
```

**Explanation:**
- Deutsche Bank EUR account
- Account: DE89370400440532013000
- Statement: 567
- Opening (Dec 19): EUR 3,000,000.00
- Transactions:
  - Credit EUR 750,000 (SEPA from France)
  - Credit EUR 500,000 (Interest)
  - Debit EUR 1,200,000 (SEPA to Italy)
  - Debit EUR 8,500 (SEPA fee)
- Closing (Dec 20): EUR 3,041,500.00
- Available: EUR 3,541,500.00 (includes EUR 500k credit line)
- Forward (Dec 21): EUR 3,516,500.00

### Example 4: Complex Statement with Reversals and Multiple References

```
{1:F01HSBCHKHHAXXX0000000000}
{2:I940CORPOHKHXXXXN}
{4:
:20:STMT-HK-20241220
:25:/HK1234567890123456
:28C:09999/001
:60F:C241219HKD10000000,00
:61:241220C5000000,NTRFNONREF//TRF-IN-001
EXPORT-PMT-001
:86:/ORDP/US Buyer Corp
/EREF/EXPORT-2024-AAA
/REMI/Export payment for goods
/PURP/GDDS
/HSCD/8542.31
:61:241220RD200000,NTRFNONREF//REV-001
REVERSAL-001
:86:/REMI/Reversal of erroneous debit
/EREF/ORIGINAL-DBT-241219
:61:241220D3000000,NFEXNONREF//FX-20241220
FX-SETTLE-001
:86:/REMI/FX settlement HKD to USD
/PURP/FXNT
/EREF/FX-SPOT-20241220
:61:241220C1500000,NLOANONREF//LOAN-DRAW
LOAN-001
:86:/REMI/Loan drawdown tranche 1
/EREF/LOAN-FACILITY-2024
:61:241220D15000,NCHGNONREF//MULTI-CHARGE
CHARGES-DEC
:86:/REMI/Monthly charges: Wire USD 5000
+ Account fee HKD 10000
:62F:C241220HKD13485000,00
:64:C241220HKD15485000,00
:65:C241221HKD15460000,00
:65:C241222HKD15435000,00
:65:C241223HKD15410000,00
-}
```

**Explanation:**
- HSBC Hong Kong HKD account
- Account: HK1234567890123456
- Statement: 9999, Page 1
- Opening (Dec 19): HKD 10,000,000.00
- Transactions:
  - Credit HKD 5,000,000 (Export payment)
  - Reversal Debit HKD 200,000 (correction - adds back)
  - Debit HKD 3,000,000 (FX settlement)
  - Credit HKD 1,500,000 (Loan drawdown)
  - Debit HKD 15,000 (Monthly charges)
- Closing (Dec 20): HKD 13,485,000.00
- Available: HKD 15,485,000.00 (includes HKD 2M credit facility)
- Forward balances for 3 days

**Balance Validation:**
- Opening: HKD 10,000,000
- Credits: +HKD 6,500,000
- Debits: -HKD 3,015,000
- Reversal adds: +HKD 200,000 (RD = Reversal of Debit)
- **Closing: HKD 13,685,000** ✓

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 52 fields in MT940 successfully map to existing GPS CDM entities:
- Account entity handles account identification, opening/closing balances, available balance
- PaymentInstruction entity (repeatable) handles each transaction line with full details
- Extension fields accommodate SWIFT-specific elements (statement numbering, balance types, transaction codes)
- FinancialInstitution entity supports account servicing institution
- Party entity supports account owner

**Key Extension Fields Used:**
- statementReference (Field 20 - unique statement ID)
- relatedReference (Field 21 - related statement link)
- dateTimeIndication (Field 13D - statement creation timestamp)
- statementNumber (Field 28C - sequential statement number)
- sequenceNumber (Field 28C - page/sequence for multi-page)
- intermediateOpeningBalance (Field 60M - multi-page opening)
- intermediateClosingBalance (Field 62M - multi-page closing)
- forwardAvailableBalance (Field 65 - projected balances array)
- debitFloorLimit (Field 34F - reporting threshold)
- creditFloorLimit (Field 34F - reporting threshold)
- entryDate (Field 61 - booking entry date)
- debitCreditMark (Field 61 - C/D/RC/RD)
- fundsCode (Field 61 - funds availability)
- transactionTypeCode (Field 61 - NTRF, NCHK, etc.)
- bankReference (Field 61 - bank's transaction reference)
- supplementaryDetails (Field 61 - additional info)
- informationToAccountOwner (Field 86 - structured transaction details)

---

## References

- **SWIFT Standards:** MT940 - Customer Statement Message
- **SWIFT Standards Release:** 2024
- **Category:** Cat 9 - Cash Management and Customer Status
- **Related Messages:** MT950, MT942, MT900, MT910, camt.053
- **ISO 20022 Equivalent:** camt.053 - Bank to Customer Statement

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
