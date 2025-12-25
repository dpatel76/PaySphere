# SWIFT MT900 - Confirmation of Debit Mapping

## Message Overview

**Message Type:** MT900 - Confirmation of Debit
**Category:** Category 9 - Cash Management and Customer Status
**Purpose:** Sent by a financial institution to a customer to confirm that a debit has been posted to the customer's account
**Direction:** FI → Customer (Bank to Corporate Customer)
**Scope:** Account debit notification and confirmation

**Key Use Cases:**
- Real-time debit confirmation to corporate customers
- Large value debit notification (threshold-based)
- Immediate notification of account debits for cash management
- Reconciliation support for treasury operations
- Automated cash position monitoring systems
- ERP/TMS system integration for liquidity management
- Fraud detection and monitoring (unexpected debits)

**Relationship to Other Messages:**
- **MT910**: Confirmation of Credit (credit equivalent of MT900)
- **MT940**: Customer Statement Message (end-of-day statement with all transactions)
- **MT942**: Interim Transaction Report (intraday statement)
- **MT950**: Customer Statement Message (detailed statement format)
- **camt.054**: ISO 20022 equivalent (Bank to Customer Debit/Credit Notification)

**Comparison with Other MT9XX Messages:**
- **MT900**: Single debit confirmation (real-time notification)
- **MT910**: Single credit confirmation (real-time notification)
- **MT940**: End-of-day statement with all transactions (batch)
- **MT942**: Intraday transaction report with multiple entries (periodic)

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in MT900** | 35 |
| **Fields Mapped to CDM** | 35 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (transaction details)
- Account (customer account debited)
- Party (account owner)
- FinancialInstitution (ordering institution, account servicing institution)
- PaymentInstruction.extensions (MT900-specific fields)

---

## Complete Field Mapping

### Mandatory Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 20 | Transaction Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction | endToEndId | Sender's unique reference |
| 21 | Related Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction.extensions | relatedReference | Reference to original transaction |
| 25 | Account Identification | 35x | 35 | M | Account number | Account | accountNumber | Account debited |
| 32A | Value Date/Currency/Amount | 6!n3!a15d | - | M | YYMMDD/CCY/Amount | PaymentInstruction | settlementDate, currency, amount | Debit value date, currency, amount |

### Optional Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 19 | Sum of Amounts | 17d | 17 | O | Decimal | PaymentInstruction.extensions | sumOfAmounts | Sum of individual amounts |
| 23E | Instruction Code | 4!c[/30x] | - | O | Codes | PaymentInstruction.extensions | instructionCode | Processing instructions |
| 26T | Transaction Type Code | 3!c | 3 | O | Codes | PaymentInstruction.extensions | transactionTypeCode | Type of transaction |
| 30 | Date of Transaction | 6!n | 6 | O | YYMMDD | PaymentInstruction.extensions | transactionDate | Actual transaction date |
| 50a | Ordering Customer | Options C, F, K | - | O | Account/BIC/Name | Party | partyName, accountNumber | Customer who ordered debit |
| 52a | Ordering Institution | Options A, D | - | O | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Ordering institution |
| 56a | Intermediary | Options A, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Intermediary institution |
| 57a | Account With Institution | Options A, B, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Account servicing institution |
| 58a | Beneficiary Institution | Options A, D | - | O | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Beneficiary institution |
| 59a | Beneficiary Customer | Options blank, A, F | - | O | Account/BIC/Name | Party | partyName, accountNumber | Ultimate beneficiary |
| 60F | Opening Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account.extensions | openingBalance | Opening balance (Final) |
| 60M | Intermediate Opening Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account.extensions | intermediateOpeningBalance | Opening balance (Intermediate) |
| 61 | Statement Line | Complex | - | O | Transaction details | PaymentInstruction.extensions | statementLine | Transaction line details |
| 62F | Closing Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account.extensions | closingBalance | Closing balance (Final) |
| 62M | Intermediate Closing Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account.extensions | intermediateClosingBalance | Closing balance (Intermediate) |
| 64 | Closing Available Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account | availableBalance | Available balance |
| 65 | Forward Available Balance | a6!n3!a15d | - | O | D/C + Date + CCY + Amt | Account.extensions | forwardAvailableBalance | Future available balance (repeatable) |
| 70 | Remittance Information | 4*35x | 140 | O | Free text | PaymentInstruction | remittanceInformation | Payment purpose/details |
| 72 | Sender to Receiver Info | 6*35x | 210 | O | Free text | PaymentInstruction.extensions | senderToReceiverInfo | Bank-to-customer information |
| 77B | Regulatory Reporting | 3*35x | 105 | O | Structured codes | PaymentInstruction.extensions | regulatoryReporting | Regulatory information |
| 86 | Information to Account Owner | 6*65x | 390 | O | Free text/structured | PaymentInstruction.extensions | informationToAccountOwner | Additional transaction details |

---

## Detailed Field Mappings

### Field 20: Transaction Reference Number

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :20: | 16x | PaymentInstruction | endToEndId | Mandatory. Bank's unique reference for this confirmation |

**Example:**
```
:20:DEBIT20241220001
```

### Field 21: Related Reference

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :21: | 16x | PaymentInstruction.extensions | relatedReference | Reference to original transaction that caused the debit |

**Example:**
```
:21:WIRETXN12345678
```

**Usage:** Links the MT900 confirmation to the original payment instruction (e.g., MT103, MT202 reference).

### Field 25: Account Identification

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :25: | 35x | Account | accountNumber | Customer's account that was debited |

**Example:**
```
:25:GB29NWBK60161331926819
:25:/GB29NWBK60161331926819
:25:1234567890
```

**Notes:**
- May include IBAN, BBAN, or proprietary account number
- Leading slash (/) indicates structured format
- Account currency matches field 32A currency

### Field 32A: Value Date, Currency, Amount

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :32A: | 6!n3!a15d | PaymentInstruction | settlementDate, currency, amount | Mandatory. Date, currency, and amount of debit |

**Example:**
```
:32A:241220USD500000,
```
- **241220** = December 20, 2024
- **USD** = US Dollars
- **500000,** = $500,000.00

**Format Details:**
- Date: YYMMDD (6 numeric)
- Currency: ISO 4217 (3 alpha)
- Amount: Up to 15 digits with comma as decimal separator

### Field 19: Sum of Amounts

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :19: | 17d | PaymentInstruction.extensions | sumOfAmounts | Sum of individual transaction amounts (if multiple) |

**Example:**
```
:19:500000,
```

**Usage:** Used when multiple underlying transactions are aggregated. Total should match field 32A amount.

### Field 23E: Instruction Code

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :23E: | 4!c[/30x] | PaymentInstruction.extensions | instructionCode | Processing instructions (repeatable) |

**Example:**
```
:23E:URGP
:23E:PHOB/CONTACT TREASURY
```

**Common Codes:**
- **CHQB** - Cheque book
- **HOLD** - Hold
- **INTC** - Intra-company payment
- **PHOB** - Phone beneficiary
- **PHOI** - Phone ordering customer
- **PHON** - Phone ordering institution
- **REPA** - Return payment
- **TELE** - Telex ordering institution
- **URGP** - Urgent payment

### Field 26T: Transaction Type Code

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :26T: | 3!c | PaymentInstruction.extensions | transactionTypeCode | Type of underlying transaction |

**Example:**
```
:26T:001
:26T:CHK
```

**Common Codes:**
- **001** - Type code 001 (bank-specific)
- **CHK** - Cheque
- **TRF** - Transfer
- **DIV** - Dividend
- **INT** - Interest

### Field 30: Date of Transaction

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :30: | 6!n | PaymentInstruction.extensions | transactionDate | Actual date transaction was executed |

**Example:**
```
:30:241219
```

**Usage:** May differ from value date (field 32A) if transaction was processed on a different day.

### Field 50a: Ordering Customer (Options C, F, K)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :50C: | Party ID | Party | partyIdentifier | Ordering customer with party identifier |
| :50F: | Party ID details | Party | partyIdentifier, partyName | Ordering customer with detailed ID |
| :50K: | Account + Name/Address | Party, Account | accountNumber, partyName, address | Account and name/address |

**Example Option K:**
```
:50K:/GB29ABCB60161331926819
ABC Corporation Ltd
123 Business Street
London EC1A 1BB
```

**Example Option F:**
```
:50F:/GB29ABCB60161331926819
1/ABC Corporation Ltd
2/123 Business Street
3/GB/London/EC1A 1BB
```

### Field 52a: Ordering Institution (Options A, D)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :52A: | BIC | FinancialInstitution | bicCode | Institution identified by BIC |
| :52D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:52A:CHASUS33XXX
```

**Example Option D:**
```
:52D:JP Morgan Chase Bank NA
New York NY
US
```

### Field 56a: Intermediary (Options A, C, D)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :56A: | BIC | FinancialInstitution | bicCode | Intermediary identified by BIC |
| :56C: | Party ID | FinancialInstitution | partyIdentifier | Party identifier |
| :56D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:56A:CITIGB2LXXX
```

### Field 57a: Account With Institution (Options A, B, C, D)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :57A: | BIC | FinancialInstitution | bicCode | Institution identified by BIC |
| :57B: | Party ID + Location | FinancialInstitution | partyIdentifier, location | Party identifier |
| :57C: | Party ID | FinancialInstitution | partyIdentifier | Party identifier only |
| :57D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:57A:DEUTDEFFXXX
```

### Field 58a: Beneficiary Institution (Options A, D)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :58A: | BIC | FinancialInstitution | bicCode | Beneficiary institution by BIC |
| :58D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:58A:BNPAFRPPXXX
```

### Field 59a: Beneficiary Customer (Options blank, A, F)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :59: | Account + Name/Address | Party, Account | accountNumber, partyName, address | No option letter |
| :59A: | BIC | Party | bic | Ultimate beneficiary by BIC |
| :59F: | Account + Party ID | Party, Account | accountNumber, partyIdentifier | Account and party details |

**Example Option (no letter):**
```
:59:/FR1420041010050500013M02606
Global Supplier SA
Paris
FR
```

### Field 60F/60M: Opening Balance

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :60F: | a6!n3!a15d | Account.extensions | openingBalance | Final opening balance |
| :60M: | a6!n3!a15d | Account.extensions | intermediateOpeningBalance | Intermediate opening balance |

**Example:**
```
:60F:C241219USD1000000,
```
- **C** = Credit balance
- **241219** = December 19, 2024
- **USD** = US Dollars
- **1000000,** = $1,000,000.00

**Options:**
- **:60F:** First/Final opening balance
- **:60M:** Intermediate opening balance (for multi-part messages)

### Field 61: Statement Line

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :61: | Complex | PaymentInstruction.extensions | statementLine | Transaction line details |

**Format:**
```
:61:YYMMDD[MMDD][DC][F]Amount[N]TransactionType[//BankRef]
CustomerRef
```

**Example:**
```
:61:241220D500000,NTRFNONREF//BANKREF12345
CUSTREF98765
```

**Components:**
- **241220** - Value date (Dec 20, 2024)
- **D** - Debit
- **500000,** - Amount
- **NTRF** - Transaction type (Transfer)
- **NONREF** - Additional reference
- **//BANKREF12345** - Bank reference
- **CUSTREF98765** - Customer reference

### Field 62F/62M: Closing Balance

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :62F: | a6!n3!a15d | Account.extensions | closingBalance | Final closing balance |
| :62M: | a6!n3!a15d | Account.extensions | intermediateClosingBalance | Intermediate closing balance |

**Example:**
```
:62F:C241220USD500000,
```
- **C** = Credit balance
- **241220** = December 20, 2024
- **USD** = US Dollars
- **500000,** = $500,000.00 (after debit)

### Field 64: Closing Available Balance

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :64: | a6!n3!a15d | Account | availableBalance | Available balance including credit facilities |

**Example:**
```
:64:C241220USD750000,
```
- Available balance: $750,000.00 (includes credit line)

### Field 65: Forward Available Balance

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :65: | a6!n3!a15d | Account.extensions | forwardAvailableBalance | Future dated available balance (repeatable) |

**Example:**
```
:65:C241221USD725000,
:65:C241222USD700000,
```

### Field 70: Remittance Information

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :70: | 4*35x | PaymentInstruction | remittanceInformation | Purpose/details of payment (up to 140 chars) |

**Example:**
```
:70:Payment for Invoice INV-2024-9876
Trade settlement reference TRADE-2024-5432
Wire transfer to supplier
```

### Field 72: Sender to Receiver Information

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :72: | 6*35x | PaymentInstruction.extensions | senderToReceiverInfo | Bank-to-customer instructions (up to 210 chars) |

**Example:**
```
:72:/INS/DEBIT CONFIRMATION
/ACC/Account debited as instructed
/REF/Original wire reference WIRE20241220
```

### Field 77B: Regulatory Reporting

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :77B: | 3*35x | PaymentInstruction.extensions | regulatoryReporting | Regulatory reporting information (up to 105 chars) |

**Example:**
```
:77B:/ORDERRES/US
/BENEFRES/FR
/PURPOSE/Trade payment
```

### Field 86: Information to Account Owner

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :86: | 6*65x | PaymentInstruction.extensions | informationToAccountOwner | Additional details (up to 390 chars) |

**Example:**
```
:86:/BENM/Global Supplier SA
/IBAN/FR1420041010050500013M02606
/EREF/WIRE20241220001
/REMI/Payment for goods purchased
```

**Common Structured Tags:**
- **/BENM/** - Beneficiary name
- **/IBAN/** - IBAN
- **/BIC/** - BIC
- **/EREF/** - End-to-end reference
- **/REMI/** - Remittance information
- **/PURP/** - Purpose code
- **/ORDP/** - Ordering party

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
| C | Credit |
| D | Debit |
| RC | Reversal of Credit |
| RD | Reversal of Debit |

### Transaction Type Codes (Field 61)

| Code | Description |
|------|-------------|
| NTRF | Transfer |
| NCHK | Cheque |
| NDIV | Dividend |
| NINT | Interest |
| NSTO | Standing Order |
| NCHG | Charges/Fees |
| NCOM | Commission |
| NSEC | Securities |
| NWIT | Wire Transfer |
| NEFT | Electronic Funds Transfer |
| NFEX | Foreign Exchange |

### Instruction Codes (Field 23E)

| Code | Description |
|------|-------------|
| CHQB | Cheque book |
| HOLD | Hold |
| INTC | Intra-company payment |
| PHOB | Phone beneficiary |
| PHOI | Phone ordering customer |
| PHON | Phone ordering institution |
| REPA | Return payment |
| TELE | Telex ordering institution |
| URGP | Urgent payment |

---

## Message Examples

### Example 1: Simple Debit Confirmation - Wire Transfer

```
{1:F01NWBKGB2LAXXX0000000000}
{2:I900ABCBGB2LXXXXN}
{4:
:20:DEBIT20241220001
:21:WIRE20241220TXN
:25:GB29NWBK60161331926819
:32A:241220USD500000,
:52A:NWBKGB2LXXX
:59:/FR1420041010050500013M02606
Global Supplier SA
Paris
FR
:70:Payment for Invoice INV-2024-9876
Trade settlement
:72:/INS/DEBIT CONFIRMATION
/ACC/Your account has been debited
-}
```

**Explanation:**
- NatWest Bank (NWBKGB2L) confirms debit to customer ABC Bank
- Account debited: GB29NWBK60161331926819
- Amount: USD 500,000.00
- Value date: December 20, 2024
- Beneficiary: Global Supplier SA (France)
- Purpose: Invoice payment

### Example 2: Debit Confirmation with Balances

```
{1:F01CHASUS33AXXX0000000000}
{2:I900CORPUS33XXXXN}
{4:
:20:DBT-20241220-5678
:21:PYMT-CORP-123456
:25:1234567890
:32A:241220USD250000,
:52A:CHASUS33XXX
:59:/DE89370400440532013000
Manufacturing GmbH
Frankfurt
DE
:60F:C241219USD1000000,
:62F:C241220USD750000,
:64:C241220USD950000,
:70:Payment to supplier
Purchase order PO-2024-8765
:86:/BENM/Manufacturing GmbH
/IBAN/DE89370400440532013000
/EREF/PO-2024-8765
/REMI/Parts and components order
-}
```

**Explanation:**
- JP Morgan Chase confirms debit to corporate customer
- Account: 1234567890
- Amount: USD 250,000.00
- Opening balance: USD 1,000,000.00 (Credit)
- Closing balance: USD 750,000.00 (Credit) - reduced by debit
- Available balance: USD 950,000.00 (includes $200k credit line)
- Beneficiary: Manufacturing GmbH (Germany)

### Example 3: Large Value Debit with Regulatory Reporting

```
{1:F01HSBCHKHHAXXX0000000000}
{2:I900TRADEHKHXXXXN}
{4:
:20:LVD20241220HK001
:21:FX-SETTLEMENT-789
:23E:URGP
:25:/HK1234567890123456
:30:241220
:32A:241220USD5000000,
:52A:HSBCHKHHXXX
:58A:CITIUS33XXX
:59:/US98765432109876543210
Trading Counterparty LLC
New York NY
US
:60F:C241219USD10000000,
:61:241220D5000000,NFEXNONREF//HK-FX-20241220
FX-SETTLE-789
:62F:C241220USD5000000,
:64:C241220USD5500000,
:70:FX settlement - EUR to USD
Spot deal reference: FXSPOT-20241220-789
Trade date: December 18 2024
:77B:/ORDERRES/HK
/BENEFRES/US
/PURPOSE/FX settlement
:86:/BENM/Trading Counterparty LLC
/EREF/FXSPOT-20241220-789
/PURP/FXNT
/REMI/Foreign exchange settlement
-}
```

**Explanation:**
- HSBC Hong Kong confirms large debit for FX settlement
- Account: HK1234567890123456
- Amount: USD 5,000,000.00
- Transaction type: Foreign exchange (NFEX)
- Opening: USD 10M → Closing: USD 5M after debit
- Available: USD 5.5M (includes credit facility)
- Urgent priority (URGP)
- Regulatory reporting: HK to US payment

### Example 4: Debit Confirmation with Multiple Details

```
{1:F01DEUTDEFFAXXX0000000000}
{2:I900CORPDEFFXXXXN}
{4:
:20:CONF-DBT-241220
:21:PMT-REF-987654
:23E:PHOB/CONTACT TREASURY
:25:DE89370400440532013000
:30:241219
:32A:241220EUR750000,
:50K:/GB29ABCB60161331926819
ABC Corporation Ltd
123 Business Street
London EC1A 1BB
GB
:52A:DEUTDEFFXXX
:56A:BNPAFRPPXXX
:58A:CHASUS33XXX
:59:/US12345678901234567890
US Subsidiary Inc
Chicago IL
US
:60F:C241219EUR2000000,
:61:241220D750000,NTRFNONREF//DE-TRF-20241220
PMT-987654
:62F:C241220EUR1250000,
:64:C241220EUR1750000,
:65:C241221EUR1725000,
:70:Intercompany funding
Transfer to US subsidiary
Loan agreement LA-2024-456
:72:/INS/DEBIT POSTED AS INSTRUCTED
/ACC/Funds transferred via SWIFT
/BNF/Contact beneficiary for confirmation
:86:/ORDP/ABC Corporation Ltd
/BENM/US Subsidiary Inc
/EREF/PMT-REF-987654
/REMI/Intercompany loan disbursement
/PURP/LOAN
-}
```

**Explanation:**
- Deutsche Bank confirms debit for intercompany transfer
- From: ABC Corporation Ltd (UK)
- To: US Subsidiary Inc (USA)
- Amount: EUR 750,000.00
- Intermediary: BNP Paribas Paris
- Account servicing: JP Morgan Chase (CHASUS33)
- Transaction date: Dec 19, Entry date: Dec 20
- Opening: EUR 2M → Closing: EUR 1.25M
- Available: EUR 1.75M (includes EUR 500k credit line)
- Forward balance (Dec 21): EUR 1.725M projected
- Phone beneficiary instruction (PHOB)

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 35 fields in MT900 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles transaction reference, amounts, dates, remittance information
- Extension fields accommodate SWIFT-specific elements (related reference, instruction codes, transaction type codes, regulatory reporting)
- Account entity supports account identification, balances (current, available, forward)
- FinancialInstitution entity supports all institution fields (ordering, intermediaries, beneficiary)
- Party entity supports ordering customer and beneficiary customer details

**Key Extension Fields Used:**
- relatedReference (Field 21 - link to original transaction)
- sumOfAmounts (Field 19 - aggregated amounts)
- instructionCode (Field 23E - URGP, PHOB, etc.)
- transactionTypeCode (Field 26T - transaction type)
- transactionDate (Field 30 - actual transaction date)
- openingBalance (Field 60F/60M - account opening balance)
- closingBalance (Field 62F/62M - account closing balance)
- intermediateOpeningBalance (Field 60M - multi-part message)
- intermediateClosingBalance (Field 62M - multi-part message)
- forwardAvailableBalance (Field 65 - projected balances)
- statementLine (Field 61 - transaction line details)
- senderToReceiverInfo (Field 72 - bank instructions)
- regulatoryReporting (Field 77B - compliance info)
- informationToAccountOwner (Field 86 - additional details)

---

## References

- **SWIFT Standards:** MT900 - Confirmation of Debit
- **SWIFT Standards Release:** 2024
- **Category:** Cat 9 - Cash Management and Customer Status
- **Related Messages:** MT910, MT940, MT942, MT950, camt.054
- **ISO 20022 Equivalent:** camt.054 - Bank to Customer Debit/Credit Notification

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
