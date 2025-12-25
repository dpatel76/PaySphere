# SWIFT MT203 - Multiple FI to FI Transfer Mapping

## Message Overview

**Message Type:** MT203 - Multiple General Financial Institution Transfer
**Category:** Category 2 - Financial Institution Transfers
**Purpose:** Used by financial institutions to instruct the transfer of funds from one ordering institution to multiple beneficiary institutions in a single message
**Direction:** FI → FI (Bank to Bank)
**Scope:** Multiple interbank fund transfers (payment splitting/distribution)

**Key Use Cases:**
- Payment splitting to multiple beneficiary banks
- Distribution of settlement proceeds
- Multi-party FX settlement transactions
- Dividend distributions to multiple banks
- Funds distribution from central clearing
- Multi-beneficiary nostro funding
- Split liquidity transfers

**Relationship to Other Messages:**
- **MT202**: Single FI Transfer (one beneficiary)
- **MT205**: FI Direct Debit (debit instruction)
- **MT200**: FI Own Account Transfer
- **pacs.009**: ISO 20022 equivalent (Financial Institution Credit Transfer)

**Comparison with MT202:**
- **MT203**: One sender to multiple beneficiaries (1-to-many)
- **MT202**: One sender to one beneficiary (1-to-1)
- **MT203**: Used for payment splitting, distribution scenarios
- **MT202**: Used for single fund transfers

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in MT203** | 44 |
| **Fields Mapped to CDM** | 44 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- FinancialInstitution (ordering institution, multiple beneficiary institutions, intermediaries)
- Account (ordering institution account, multiple beneficiary institution accounts)
- Party (used for institution identification)

---

## Complete Field Mapping

### Mandatory Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 20 | Transaction Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction | endToEndId | Sender's transaction reference |
| 19 | Sum of Amounts | 17d | 17 | M | Decimal | PaymentInstruction.extensions | totalAmount | Total of all individual amounts |
| 30 | Value Date | 6!n | 6 | M | YYMMDD | PaymentInstruction | settlementDate | Value date for all transfers |
| 52a | Ordering Institution | Option A, D | - | O | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Ordering (sender) institution |
| 72 | Sender to Receiver Info | 6*35x | 210 | O | Free text | PaymentInstruction.extensions | senderToReceiverInfo | Bank-to-bank information |

### Repeating Transaction Details (Occurs Multiple Times)

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 21 | Related Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction.extensions | relatedReference | Reference for this transaction |
| 32B | Currency/Amount | 3!a15d | - | M | CCY/Amount | PaymentInstruction | currency, amount | Transaction currency and amount |
| 53a | Sender's Correspondent | Option A, B, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Sender's correspondent bank |
| 54a | Receiver's Correspondent | Option A, B, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Receiver's correspondent bank |
| 56a | Intermediary | Option A, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Intermediary institution |
| 57a | Account With Institution | Option A, B, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Beneficiary's correspondent |
| 58a | Beneficiary Institution | Option A, D | - | M | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Beneficiary (receiver) institution |

### Optional Fields (Per Transaction)

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 26T | Transaction Type Code | 3!c | 3 | O | Codes | PaymentInstruction.extensions | transactionTypeCode | Type of transaction |
| 33B | Currency/Instructed Amount | 3!a15d | - | O | CCY/Amount | PaymentInstruction.extensions | instructedCurrency, instructedAmount | Original currency/amount |
| 36 | Exchange Rate | 12d | 12 | O | Decimal | PaymentInstruction.extensions | exchangeRate | Exchange rate |
| 50a | Ordering Customer | Option A, F, K | - | O | Account/BIC/Name | Party | partyName, accountNumber | Ultimate ordering customer |
| 59a | Beneficiary Customer | Option A, F | - | O | Account/Name | Party | partyName, accountNumber | Ultimate beneficiary customer |
| 70 | Remittance Information | 4*35x | 140 | O | Free text | PaymentInstruction | remittanceInformation | Purpose of payment |
| 71A | Details of Charges | 3!a | 3 | O | BEN, OUR, SHA | PaymentInstruction.extensions | chargeBearer | Charge bearer |
| 71F | Sender's Charges | 3!a15d | - | O | CCY/Amount (6 occurrences) | PaymentInstruction.extensions | senderCharges | Sender's charges |
| 71G | Receiver's Charges | 3!a15d | - | O | CCY/Amount | PaymentInstruction.extensions | receiverCharges | Receiver's charges |
| 77B | Regulatory Reporting | 3*35x | 105 | O | Free text | PaymentInstruction.extensions | regulatoryReporting | Regulatory information |

---

## Detailed Field Mappings

### Field 20: Transaction Reference Number

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :20: | 16x | PaymentInstruction | endToEndId | Mandatory. Sender's unique reference for entire message |

**Example:**
```
:20:MULTI20241220001
```

### Field 19: Sum of Amounts

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :19: | 17d | PaymentInstruction.extensions | totalAmount | Mandatory. Sum of all field 32B amounts (validation) |

**Example:**
```
:19:5000000,
```

### Field 30: Value Date

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :30: | 6!n | PaymentInstruction | settlementDate | Mandatory. Value date for all transfers (YYMMDD) |

**Example:**
```
:30:241220
```
- **241220** = December 20, 2024

### Field 21: Related Reference

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :21: | 16x | PaymentInstruction.extensions | relatedReference | Reference for individual transaction (repeating) |

**Example:**
```
:21:TXN001
:21:TXN002
:21:TXN003
```

### Field 26T: Transaction Type Code

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :26T: | 3!c | PaymentInstruction.extensions | transactionTypeCode | Type of underlying transaction |

**Example:**
```
:26T:COV
:26T:FXD
```

**Common Codes:**
- **COV** - Cover
- **FXD** - Foreign exchange deal

### Field 32B: Currency/Amount

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :32B: | 3!a15d | PaymentInstruction | currency, amount | Mandatory for each transaction. Currency and amount |

**Example:**
```
:32B:USD2000000,
:32B:USD1500000,
:32B:USD1500000,
```

### Field 33B: Currency/Instructed Amount

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :33B: | 3!a15d | PaymentInstruction.extensions | instructedCurrency, instructedAmount | Original currency/amount (if different from settlement) |

**Example:**
```
:33B:EUR1700000,
```

### Field 36: Exchange Rate

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :36: | 12d | PaymentInstruction.extensions | exchangeRate | Exchange rate applied |

**Example:**
```
:36:1,175
```

### Field 50a: Ordering Customer (Options A, F, K)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :50A: | BIC | Party | bic, partyName | Ordering customer identified by BIC |
| :50F: | Party ID | Party | partyIdentifier | Ordering customer with detailed ID |
| :50K: | Account + Name/Address | Party, Account | accountNumber, partyName, address | Account and name/address |

**Example Option K:**
```
:50K:/GB29ABCB60161331926819
ABC Corporation Ltd
123 Business Street
London EC1A 1BB
GB
```

### Field 52a: Ordering Institution (Options A, D)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :52A: | BIC | FinancialInstitution | bicCode | Ordering institution identified by BIC |
| :52D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:52A:CHASUS33XXX
```

### Field 53a: Sender's Correspondent (Options A, B, D)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :53A: | BIC | FinancialInstitution | bicCode | Correspondent identified by BIC |
| :53B: | Party ID + Location | FinancialInstitution | partyIdentifier, location | Party identifier |
| :53D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:53A:CITIGB2LXXX
```

### Field 54a: Receiver's Correspondent (Options A, B, D)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :54A: | BIC | FinancialInstitution | bicCode | Correspondent identified by BIC |
| :54B: | Party ID + Location | FinancialInstitution | partyIdentifier, location | Party identifier |
| :54D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:54A:DEUTDEFFXXX
```

### Field 56a: Intermediary (Options A, C, D)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :56A: | BIC | FinancialInstitution | bicCode | Intermediary identified by BIC |
| :56C: | Party ID | FinancialInstitution | partyIdentifier | Party identifier |
| :56D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:56A:BNPAFRPPXXX
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
:57A:HSBCHKHHXXX
```

### Field 58a: Beneficiary Institution (Options A, D)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :58A: | BIC | FinancialInstitution | bicCode | Beneficiary institution by BIC (mandatory) |
| :58D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:58A:DEUTDEFFXXX
```

### Field 59a: Beneficiary Customer (Options A, F)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :59A: | BIC | Party | bic | Ultimate beneficiary by BIC |
| :59F: | Account + Party ID | Party, Account | accountNumber, partyIdentifier | Account and party details |

**Example Option F:**
```
:59F:/DE89370400440532013000
/DRLC/DE/12345678
1/Peter Schmidt
2/Hauptstrasse 123
3/DE/10115/Berlin
```

### Field 70: Remittance Information

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :70: | 4*35x | PaymentInstruction | remittanceInformation | Purpose/details of payment (up to 140 chars) |

**Example:**
```
:70:Distribution of FX settlement proceeds
Multi-party transaction settlement
Reference: FXSET-20241220-001
```

### Field 71A: Details of Charges

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :71A: | 3!a | PaymentInstruction.extensions | chargeBearer | Who bears charges |

**Example:**
```
:71A:SHA
```

**Valid Codes:**
- **BEN** - Beneficiary pays all charges
- **OUR** - Ordering institution pays all charges
- **SHA** - Charges shared (sender pays sender's bank, receiver pays receiver's bank)

### Field 71F: Sender's Charges

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :71F: | 3!a15d | PaymentInstruction.extensions | senderCharges | Sender's charges (up to 6 occurrences) |

**Example:**
```
:71F:USD25,
:71F:USD10,
```

### Field 71G: Receiver's Charges

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :71G: | 3!a15d | PaymentInstruction.extensions | receiverCharges | Receiver's charges |

**Example:**
```
:71G:EUR15,
```

### Field 72: Sender to Receiver Information

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :72: | 6*35x | PaymentInstruction.extensions | senderToReceiverInfo | Bank-to-bank instructions (up to 210 chars) |

**Example:**
```
:72:/INS/Multi-party settlement
/BNF/FX deal distribution
/ACC/Multiple beneficiary accounts
```

### Field 77B: Regulatory Reporting

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :77B: | 3*35x | PaymentInstruction.extensions | regulatoryReporting | Regulatory reporting information (up to 105 chars) |

**Example:**
```
:77B:/ORDERRES/US
/BENEFRES/DE,FR,GB
/REMI/Multi-party settlement
```

---

## Message Examples

### Example 1: FX Settlement Distribution to Three Banks

```
{1:F01CHASUS33AXXX0000000000}
{2:I203CITIGB2LXXXXN}
{4:
:20:FXDIST20241220
:19:5000000,
:30:241220
:52A:CHASUS33XXX
:21:BENEF1
:32B:USD2000000,
:58A:DEUTDEFFXXX
:70:FX settlement distribution - EUR/USD
Beneficiary 1 of 3
:21:BENEF2
:32B:USD1500000,
:58A:BNPAFRPPXXX
:70:FX settlement distribution - EUR/USD
Beneficiary 2 of 3
:21:BENEF3
:32B:USD1500000,
:58A:HSBCGB2LXXX
:70:FX settlement distribution - EUR/USD
Beneficiary 3 of 3
:72:/INS/Multi-party FX settlement
/ACC/Nostro funding distribution
-}
```

**Explanation:**
- JP Morgan Chase (CHASUS33) distributing $5,000,000 to three beneficiaries
- Deutsche Bank Frankfurt: $2,000,000
- BNP Paribas Paris: $1,500,000
- HSBC London: $1,500,000
- Settlement date: December 20, 2024
- Total amount (Field 19): $5,000,000

### Example 2: Dividend Distribution with Intermediaries

```
{1:F01HSBCHKHHAXXX0000000000}
{2:I203CITIUS33XXXXN}
{4:
:20:DIV20241220HK
:19:10000000,
:30:241220
:52A:HSBCHKHHXXX
:21:DIV-TXN-001
:32B:USD4000000,
:56A:CITIUS33XXX
:58A:HSBCUS33XXX
:70:Dividend distribution - tranche 1
Corporate action reference: CA2024-999
:71A:OUR
:21:DIV-TXN-002
:32B:USD3500000,
:56A:JPMUS33XXX
:58A:BOFAUS3NXXX
:70:Dividend distribution - tranche 2
Corporate action reference: CA2024-999
:71A:OUR
:21:DIV-TXN-003
:32B:USD2500000,
:56A:WELLSFARGOXXX
:58A:CHASUS33XXX
:70:Dividend distribution - tranche 3
Corporate action reference: CA2024-999
:71A:OUR
:72:/INS/All charges OUR basis
/BNF/Same day value required
:77B:/ORDERRES/HK
/BENEFRES/US
-}
```

**Explanation:**
- HSBC Hong Kong distributing $10,000,000 dividend to three US banks
- HSBC New York: $4,000,000 (via Citibank)
- Bank of America: $3,500,000 (via JP Morgan)
- Chase: $2,500,000 (via Wells Fargo)
- All charges borne by ordering institution (OUR)

### Example 3: Central Clearing Distribution with FX

```
{1:F01BNPAFRPPAXXX0000000000}
{2:I203CITIGB2LXXXXN}
{4:
:20:CLEAR20241220
:19:7500000,
:30:241220
:52A:BNPAFRPPXXX
:21:CLR-001-EUR
:26T:FXD
:32B:EUR2500000,
:33B:USD2937500,
:36:1,175
:56A:CITIGB2LXXX
:58A:DEUTDEFFXXX
:70:Clearing settlement - EUR leg
FX rate: 1.175
:71A:SHA
:21:CLR-002-EUR
:26T:FXD
:32B:EUR2500000,
:33B:USD2937500,
:36:1,175
:56A:CITIGB2LXXX
:58A:COBADEFFXXX
:70:Clearing settlement - EUR leg
FX rate: 1.175
:71A:SHA
:21:CLR-003-EUR
:26T:FXD
:32B:EUR2500000,
:33B:USD2937500,
:36:1,175
:56A:CITIGB2LXXX
:58A:DRESDEFFXXX
:70:Clearing settlement - EUR leg
FX rate: 1.175
:71A:SHA
:72:/INS/Central clearing distribution
/ACC/FX settlement EUR vs USD
/RATE/1.175
-}
```

**Explanation:**
- BNP Paribas Paris distributing €7,500,000 to three German banks
- Deutsche Bank Frankfurt: €2,500,000 (USD $2,937,500)
- Commerzbank Frankfurt: €2,500,000 (USD $2,937,500)
- Dresdner Bank Frankfurt: €2,500,000 (USD $2,937,500)
- Exchange rate: 1.175 EUR/USD
- Intermediary for all: Citibank London
- Charges shared (SHA)

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 44 fields in MT203 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles transaction reference, amounts, dates
- Extension fields accommodate SWIFT-specific elements (total amount, charges, regulatory reporting)
- FinancialInstitution entity supports all institution fields including multiple beneficiaries
- Account entity handles institution accounts
- Party entity supports ordering and beneficiary customers when present
- Multiple transactions represented as separate PaymentInstruction instances with shared parent reference

**Key Extension Fields Used:**
- totalAmount (Field 19 - sum of all individual amounts for validation)
- relatedReference (Field 21 - individual transaction reference within message)
- transactionTypeCode (Field 26T - COV, FXD)
- instructedCurrency, instructedAmount (Field 33B - original currency)
- exchangeRate (Field 36 - FX rate)
- chargeBearer (Field 71A - BEN/OUR/SHA)
- senderCharges, receiverCharges (Field 71F/71G)
- senderToReceiverInfo (Field 72 - bank instructions)
- regulatoryReporting (Field 77B - compliance info)

**Multi-Beneficiary Handling:**
- Each beneficiary transaction creates a separate PaymentInstruction instance
- All instances share the same endToEndId (Field 20) as parent reference
- Individual transactions distinguished by relatedReference (Field 21)
- Total amount validation using totalAmount extension field (Field 19)

---

## References

- **SWIFT Standards:** MT203 - Multiple General Financial Institution Transfer
- **SWIFT Standards Release:** 2024
- **Category:** Cat 2 - Financial Institution Transfers
- **Related Messages:** MT202, MT205, MT200, pacs.009
- **ISO 20022 Equivalent:** pacs.009 - Financial Institution Credit Transfer (with multiple credit transactions)

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
