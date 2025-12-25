# SWIFT MT910 - Confirmation of Credit Mapping

## Message Overview

**Message Type:** MT910 - Confirmation of Credit
**Category:** Category 9 - Cash Management and Customer Status
**Purpose:** Sent by a financial institution to a customer to confirm that a credit has been posted to the customer's account
**Direction:** FI → Customer (Bank to Corporate Customer)
**Scope:** Account credit notification and confirmation

**Key Use Cases:**
- Real-time credit confirmation to corporate customers
- Large value credit notification (threshold-based)
- Immediate notification of incoming payments for cash management
- Reconciliation support for treasury operations
- Automated cash position monitoring systems
- ERP/TMS system integration for receivables management
- Fraud detection and monitoring (unexpected credits)
- Payment receipt confirmation for trade finance

**Relationship to Other Messages:**
- **MT900**: Confirmation of Debit (debit equivalent of MT910)
- **MT940**: Customer Statement Message (end-of-day statement with all transactions)
- **MT942**: Interim Transaction Report (intraday statement)
- **MT950**: Customer Statement Message (detailed statement format)
- **MT103**: Single Customer Credit Transfer (original payment that triggered MT910)
- **camt.054**: ISO 20022 equivalent (Bank to Customer Debit/Credit Notification)

**Comparison with Other MT9XX Messages:**
- **MT910**: Single credit confirmation (real-time notification)
- **MT900**: Single debit confirmation (real-time notification)
- **MT940**: End-of-day statement with all transactions (batch)
- **MT942**: Intraday transaction report with multiple entries (periodic)

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in MT910** | 35 |
| **Fields Mapped to CDM** | 35 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (transaction details)
- Account (customer account credited)
- Party (account owner, ordering customer)
- FinancialInstitution (ordering institution, account servicing institution)
- PaymentInstruction.extensions (MT910-specific fields)

---

## Complete Field Mapping

### Mandatory Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 20 | Transaction Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction | endToEndId | Sender's unique reference |
| 21 | Related Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction.extensions | relatedReference | Reference to original transaction |
| 25 | Account Identification | 35x | 35 | M | Account number | Account | accountNumber | Account credited |
| 32A | Value Date/Currency/Amount | 6!n3!a15d | - | M | YYMMDD/CCY/Amount | PaymentInstruction | settlementDate, currency, amount | Credit value date, currency, amount |

### Optional Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 19 | Sum of Amounts | 17d | 17 | O | Decimal | PaymentInstruction.extensions | sumOfAmounts | Sum of individual amounts |
| 23E | Instruction Code | 4!c[/30x] | - | O | Codes | PaymentInstruction.extensions | instructionCode | Processing instructions |
| 26T | Transaction Type Code | 3!c | 3 | O | Codes | PaymentInstruction.extensions | transactionTypeCode | Type of transaction |
| 30 | Date of Transaction | 6!n | 6 | O | YYMMDD | PaymentInstruction.extensions | transactionDate | Actual transaction date |
| 50a | Ordering Customer | Options C, F, K | - | O | Account/BIC/Name | Party | partyName, accountNumber | Customer who ordered credit |
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
:20:CREDIT2024122001
```

### Field 21: Related Reference

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :21: | 16x | PaymentInstruction.extensions | relatedReference | Reference to original transaction that caused the credit |

**Example:**
```
:21:MT103-2024-5678
```

**Usage:** Links the MT910 confirmation to the original payment instruction (e.g., MT103 reference from sending bank).

### Field 25: Account Identification

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :25: | 35x | Account | accountNumber | Customer's account that was credited |

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
| :32A: | 6!n3!a15d | PaymentInstruction | settlementDate, currency, amount | Mandatory. Date, currency, and amount of credit |

**Example:**
```
:32A:241220USD750000,
```
- **241220** = December 20, 2024
- **USD** = US Dollars
- **750000,** = $750,000.00

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
:19:750000,
```

**Usage:** Used when multiple underlying transactions are aggregated. Total should match field 32A amount.

### Field 23E: Instruction Code

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :23E: | 4!c[/30x] | PaymentInstruction.extensions | instructionCode | Processing instructions (repeatable) |

**Example:**
```
:23E:TELE
:23E:PHOI/CONTACT ACCOUNTS RECEIVABLE
```

**Common Codes:**
- **CHQB** - Cheque book
- **HOLD** - Hold
- **INTC** - Intra-company payment
- **PHOB** - Phone beneficiary
- **PHOI** - Phone ordering customer
- **PHON** - Phone ordering institution
- **TELE** - Telex ordering institution
- **TELB** - Telex beneficiary
- **URGP** - Urgent payment

### Field 26T: Transaction Type Code

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :26T: | 3!c | PaymentInstruction.extensions | transactionTypeCode | Type of underlying transaction |

**Example:**
```
:26T:001
:26T:TRF
```

**Common Codes:**
- **001** - Type code 001 (bank-specific)
- **TRF** - Transfer
- **DIV** - Dividend
- **INT** - Interest
- **SAL** - Salary

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
:50K:/US12345678901234567890
Global Trading Corporation
100 Wall Street
New York NY 10005
US
```

**Example Option F:**
```
:50F:/US12345678901234567890
1/Global Trading Corporation
2/100 Wall Street
3/US/New York/10005
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
:57A:NWBKGB2LXXX
```

### Field 58a: Beneficiary Institution (Options A, D)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :58A: | BIC | FinancialInstitution | bicCode | Beneficiary institution by BIC |
| :58D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:58A:NWBKGB2LXXX
```

### Field 59a: Beneficiary Customer (Options blank, A, F)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :59: | Account + Name/Address | Party, Account | accountNumber, partyName, address | No option letter |
| :59A: | BIC | Party | bic | Ultimate beneficiary by BIC |
| :59F: | Account + Party ID | Party, Account | accountNumber, partyIdentifier | Account and party details |

**Example Option (no letter):**
```
:59:/GB29NWBK60161331926819
ABC Corporation Ltd
London
GB
```

### Field 60F/60M: Opening Balance

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :60F: | a6!n3!a15d | Account.extensions | openingBalance | Final opening balance |
| :60M: | a6!n3!a15d | Account.extensions | intermediateOpeningBalance | Intermediate opening balance |

**Example:**
```
:60F:C241219USD500000,
```
- **C** = Credit balance
- **241219** = December 19, 2024
- **USD** = US Dollars
- **500000,** = $500,000.00

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
:61:241220C750000,NTRFNONREF//BANKREF98765
CUSTREF12345
```

**Components:**
- **241220** - Value date (Dec 20, 2024)
- **C** - Credit
- **750000,** - Amount
- **NTRF** - Transaction type (Transfer)
- **NONREF** - Additional reference
- **//BANKREF98765** - Bank reference
- **CUSTREF12345** - Customer reference

### Field 62F/62M: Closing Balance

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :62F: | a6!n3!a15d | Account.extensions | closingBalance | Final closing balance |
| :62M: | a6!n3!a15d | Account.extensions | intermediateClosingBalance | Intermediate closing balance |

**Example:**
```
:62F:C241220USD1250000,
```
- **C** = Credit balance
- **241220** = December 20, 2024
- **USD** = US Dollars
- **1250000,** = $1,250,000.00 (after credit)

### Field 64: Closing Available Balance

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :64: | a6!n3!a15d | Account | availableBalance | Available balance including credit facilities |

**Example:**
```
:64:C241220USD1500000,
```
- Available balance: $1,500,000.00 (includes credit line)

### Field 65: Forward Available Balance

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :65: | a6!n3!a15d | Account.extensions | forwardAvailableBalance | Future dated available balance (repeatable) |

**Example:**
```
:65:C241221USD1475000,
:65:C241222USD1450000,
```

### Field 70: Remittance Information

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :70: | 4*35x | PaymentInstruction | remittanceInformation | Purpose/details of payment (up to 140 chars) |

**Example:**
```
:70:Payment for Invoice INV-2024-5432
Customer payment received
Reference: CUST-PMT-20241220
```

### Field 72: Sender to Receiver Information

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :72: | 6*35x | PaymentInstruction.extensions | senderToReceiverInfo | Bank-to-customer instructions (up to 210 chars) |

**Example:**
```
:72:/INS/CREDIT CONFIRMATION
/ACC/Account credited as per instruction
/REF/Original payment MT103-2024-5678
```

### Field 77B: Regulatory Reporting

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :77B: | 3*35x | PaymentInstruction.extensions | regulatoryReporting | Regulatory reporting information (up to 105 chars) |

**Example:**
```
:77B:/ORDERRES/US
/BENEFRES/GB
/PURPOSE/Trade payment received
```

### Field 86: Information to Account Owner

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :86: | 6*65x | PaymentInstruction.extensions | informationToAccountOwner | Additional details (up to 390 chars) |

**Example:**
```
:86:/ORDP/Global Trading Corporation
/IBAN/US12345678901234567890
/EREF/MT103-2024-5678
/REMI/Payment for goods delivered
/PURP/GDDS
```

**Common Structured Tags:**
- **/ORDP/** - Ordering party
- **/IBAN/** - IBAN
- **/BIC/** - BIC
- **/EREF/** - End-to-end reference
- **/REMI/** - Remittance information
- **/PURP/** - Purpose code
- **/BENM/** - Beneficiary name

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
| NSAL | Salary Payment |

### Instruction Codes (Field 23E)

| Code | Description |
|------|-------------|
| CHQB | Cheque book |
| HOLD | Hold |
| INTC | Intra-company payment |
| PHOB | Phone beneficiary |
| PHOI | Phone ordering customer |
| PHON | Phone ordering institution |
| TELE | Telex ordering institution |
| TELB | Telex beneficiary |
| URGP | Urgent payment |

---

## Message Examples

### Example 1: Simple Credit Confirmation - Customer Payment Received

```
{1:F01NWBKGB2LAXXX0000000000}
{2:I910ABCBGB2LXXXXN}
{4:
:20:CREDIT2024122001
:21:MT103-2024-5678
:25:GB29NWBK60161331926819
:32A:241220USD750000,
:50K:/US12345678901234567890
Global Trading Corporation
New York NY
US
:52A:CHASUS33XXX
:70:Payment for Invoice INV-2024-5432
Customer payment
:72:/INS/CREDIT CONFIRMATION
/ACC/Your account has been credited
-}
```

**Explanation:**
- NatWest Bank (NWBKGB2L) confirms credit to customer ABC Bank
- Account credited: GB29NWBK60161331926819
- Amount: USD 750,000.00
- Value date: December 20, 2024
- Ordering customer: Global Trading Corporation (US)
- Ordering institution: JP Morgan Chase
- Related to MT103-2024-5678

### Example 2: Credit Confirmation with Balances

```
{1:F01DEUTDEFFAXXX0000000000}
{2:I910CORPDEFFXXXXN}
{4:
:20:CRD-20241220-1234
:21:PMT-RECV-456789
:25:DE89370400440532013000
:32A:241220EUR500000,
:50K:/GB29ABCB60161331926819
UK Customer Ltd
London
GB
:52A:NWBKGB2LXXX
:60F:C241219EUR800000,
:62F:C241220EUR1300000,
:64:C241220EUR1550000,
:70:Payment received from customer
Invoice settlement INV-2024-7890
:86:/ORDP/UK Customer Ltd
/IBAN/GB29ABCB60161331926819
/EREF/INV-2024-7890
/REMI/Invoice payment for goods
/PURP/GDDS
-}
```

**Explanation:**
- Deutsche Bank confirms credit to corporate customer
- Account: DE89370400440532013000
- Amount: EUR 500,000.00
- Opening balance: EUR 800,000.00 (Credit)
- Closing balance: EUR 1,300,000.00 (Credit) - increased by credit
- Available balance: EUR 1,550,000.00 (includes EUR 250k credit line)
- Ordering customer: UK Customer Ltd via NatWest

### Example 3: Large Value Credit with Regulatory Reporting

```
{1:F01HSBCHKHHAXXX0000000000}
{2:I910EXPORTHKXXXXN}
{4:
:20:LVC20241220HK002
:21:EXPORT-PMT-999
:23E:TELE
:25:/HK9876543210987654
:30:241220
:32A:241220USD3000000,
:50K:/US55555555555555555555
International Buyer Corp
Los Angeles CA
US
:52A:CITIUS33XXX
:56A:HSBCHKHHXXX
:60F:C241219USD2000000,
:61:241220C3000000,NTRFNONREF//HK-EXPORT-PMT
EXPORT-999
:62F:C241220USD5000000,
:64:C241220USD5250000,
:70:Export payment for goods shipped
Bill of lading BL-2024-8888
Commercial invoice CI-2024-9999
:77B:/ORDERRES/US
/BENEFRES/HK
/PURPOSE/Trade goods payment
:86:/ORDP/International Buyer Corp
/EREF/EXPORT-PMT-999
/PURP/GDDS
/REMI/Payment for manufactured goods
/HSCD/8542.31
-}
```

**Explanation:**
- HSBC Hong Kong confirms large export payment credit
- Account: HK9876543210987654
- Amount: USD 3,000,000.00
- Transaction type: Transfer (NTRF)
- Opening: USD 2M → Closing: USD 5M after credit
- Available: USD 5.25M (includes credit facility)
- Ordering customer: International Buyer Corp (US)
- Via Citibank New York, intermediary HSBC HK
- Regulatory reporting: US to HK payment
- HS Code included for trade goods

### Example 4: Intercompany Credit with Multiple Details

```
{1:F01BNPAFRPPAXXX0000000000}
{2:I910SUBFRPPXXXXN}
{4:
:20:CONF-CRD-241220
:21:INTERCO-REF-111
:23E:INTC
:23E:PHOI/NOTIFY FINANCE DEPT
:25:FR1420041010050500013M02606
:30:241219
:32A:241220EUR1200000,
:50K:/DE89370400440532013000
Parent Company GmbH
Frankfurt
DE
:52A:DEUTDEFFXXX
:56A:BNPAFRPPXXX
:59:/FR1420041010050500013M02606
French Subsidiary SA
Paris
FR
:60F:C241219EUR3000000,
:61:241220C1200000,NTRFNONREF//FR-INTERCO-20241220
INTERCO-111
:62F:C241220EUR4200000,
:64:C241220EUR4950000,
:65:C241221EUR4925000,
:70:Intercompany funding
Subsidiary capital injection
Board resolution BR-2024-12
:72:/INS/CREDIT POSTED
/ACC/Funds received via SWIFT
/BNF/Notify CFO immediately
:86:/ORDP/Parent Company GmbH
/BENM/French Subsidiary SA
/EREF/INTERCO-REF-111
/REMI/Capital injection per resolution
/PURP/INTC
-}
```

**Explanation:**
- BNP Paribas confirms intercompany credit
- From: Parent Company GmbH (Germany)
- To: French Subsidiary SA (France)
- Amount: EUR 1,200,000.00
- Via Deutsche Bank, BNP Paribas
- Transaction date: Dec 19, Value date: Dec 20
- Opening: EUR 3M → Closing: EUR 4.2M
- Available: EUR 4.95M (includes EUR 750k credit line)
- Forward balance (Dec 21): EUR 4.925M projected
- Intra-company payment code (INTC)
- Phone ordering institution instruction

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 35 fields in MT910 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles transaction reference, amounts, dates, remittance information
- Extension fields accommodate SWIFT-specific elements (related reference, instruction codes, transaction type codes, regulatory reporting)
- Account entity supports account identification, balances (current, available, forward)
- FinancialInstitution entity supports all institution fields (ordering, intermediaries, beneficiary)
- Party entity supports ordering customer and beneficiary customer details

**Key Extension Fields Used:**
- relatedReference (Field 21 - link to original transaction, typically MT103)
- sumOfAmounts (Field 19 - aggregated amounts)
- instructionCode (Field 23E - TELE, PHOI, INTC, etc.)
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

- **SWIFT Standards:** MT910 - Confirmation of Credit
- **SWIFT Standards Release:** 2024
- **Category:** Cat 9 - Cash Management and Customer Status
- **Related Messages:** MT900, MT940, MT942, MT950, MT103, camt.054
- **ISO 20022 Equivalent:** camt.054 - Bank to Customer Debit/Credit Notification

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
