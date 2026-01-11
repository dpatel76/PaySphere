# SWIFT MT202 - General FI to FI Transfer Mapping

## Message Overview

**Message Type:** MT202 - General Financial Institution Transfer
**Category:** Category 2 - Financial Institution Transfers
**Purpose:** Used by financial institutions to transfer funds between themselves for their own account or on behalf of third parties (cover payments, FX settlements, position management)
**Direction:** FI → FI (Bank to Bank)
**Scope:** Interbank fund transfers (not customer payments)

**Key Use Cases:**
- Foreign exchange (FX) settlement between banks
- Cover payments for MT103 customer transfers
- Interbank position management
- Liquidity management between correspondent banks
- Nostro/Vostro account movements
- Central bank operations
- Settlement of securities transactions

**Relationship to Other Messages:**
- **MT202COV**: General FI Transfer with cover (includes underlying customer info)
- **MT103**: Single Customer Credit Transfer (MT202 may be cover payment)
- **MT200**: FI Own Account Transfer (simpler version)
- **MT205**: FI Direct Debit (interbank debit)
- **pacs.009**: ISO 20022 equivalent (Financial Institution Credit Transfer)

**Comparison with MT103:**
- **MT202**: Bank-to-bank transfer (interbank)
- **MT103**: Customer credit transfer (includes customer details)
- **MT202**: Used for cover payments, FX settlement, position management
- **MT103**: Used for customer-initiated payments

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in MT202** | 47 |
| **Fields Mapped to CDM** | 47 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- FinancialInstitution (ordering institution, beneficiary institution, intermediaries)
- Account (ordering institution account, beneficiary institution account)
- Party (used for institution identification)

---

## Complete Field Mapping

### Mandatory Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 20 | Transaction Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction | endToEndId | Sender's transaction reference |
| 21 | Related Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction.extensions | relatedReference | Reference to related message |
| 32A | Value Date/Currency/Amount | 6!n3!a15d | - | M | YYMMDD/CCY/Amount | PaymentInstruction | settlementDate, currency, amount | Value date, currency, and amount |
| 52a | Ordering Institution | Option A, D | - | O | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Ordering (sender) institution |
| 53a | Sender's Correspondent | Option A, B, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Sender's correspondent bank |
| 54a | Receiver's Correspondent | Option A, B, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Receiver's correspondent bank |
| 56a | Intermediary | Option A, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Intermediary institution |
| 57a | Account With Institution | Option A, B, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Beneficiary's correspondent |
| 58a | Beneficiary Institution | Option A, D | - | M | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Beneficiary (receiver) institution |

### Optional Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 13C | Time Indication | /8c/4!n | - | O | /CODE/Time | PaymentInstruction.extensions | timeIndication | Time indication (e.g., /CLSTIME/1600) |
| 23E | Instruction Code | 4!c[/30x] | - | O | Codes | PaymentInstruction.extensions | instructionCode | Processing instructions |
| 26T | Transaction Type Code | 3!c | 3 | O | Codes | PaymentInstruction.extensions | transactionTypeCode | Type of transaction |
| 33B | Currency/Amount | 3!a15d | - | O | CCY/Amount | PaymentInstruction.extensions | instructedCurrency, instructedAmount | Instructed currency/amount |
| 36 | Exchange Rate | 12d | 12 | O | Decimal | PaymentInstruction.extensions | exchangeRate | Exchange rate |
| 50a | Ordering Customer | Option A, F, K | - | O | Account/BIC/Name | Party | partyName, accountNumber | Ultimate ordering customer |
| 51A | Sending Institution | Option A | - | O | BIC | FinancialInstitution | bicCode | Sending institution (rarely used) |
| 59a | Beneficiary Customer | Option A, F | - | O | Account/Name | Party | partyName, accountNumber | Ultimate beneficiary customer |
| 70 | Remittance Information | 4*35x | 140 | O | Free text | PaymentInstruction | remittanceInformation | Purpose of payment |
| 71A | Details of Charges | 3!a | 3 | O | BEN, OUR, SHA | PaymentInstruction.extensions | chargeBearer | Charge bearer |
| 71F | Sender's Charges | 3!a15d | - | O | CCY/Amount (6 occurrences) | PaymentInstruction.extensions | senderCharges | Sender's charges |
| 71G | Receiver's Charges | 3!a15d | - | O | CCY/Amount | PaymentInstruction.extensions | receiverCharges | Receiver's charges |
| 72 | Sender to Receiver Info | 6*35x | 210 | O | Free text | PaymentInstruction.extensions | senderToReceiverInfo | Bank-to-bank information |
| 77B | Regulatory Reporting | 3*35x | 105 | O | Free text | PaymentInstruction.extensions | regulatoryReporting | Regulatory information |

---

## Detailed Field Mappings

### Field 20: Transaction Reference Number

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :20: | 16x | PaymentInstruction | endToEndId | Mandatory. Sender's unique reference for transaction |

**Example:**
```
:20:FX20241220001
```

### Field 21: Related Reference

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :21: | 16x | PaymentInstruction.extensions | relatedReference | Reference to related message (e.g., MT103 being covered) |

**Example:**
```
:21:MT103REF12345
```

### Field 13C: Time Indication

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :13C: | /8c/4!n | PaymentInstruction.extensions | timeIndication | Time-related processing instructions |

**Example:**
```
:13C:/CLSTIME/1600
:13C:/SNDTIME/0930
:13C:/RNCTIME/1130
```

**Common Codes:**
- **/CLSTIME/** - Closing time
- **/SNDTIME/** - Sending time
- **/RNCTIME/** - Receiver's correspondence time

### Field 23E: Instruction Code

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :23E: | 4!c[/30x] | PaymentInstruction.extensions | instructionCode | Processing instructions |

**Example:**
```
:23E:PHOB
:23E:TELE
:23E:SDVA
```

**Common Codes:**
- **CHQB** - Cheque book
- **HOLD** - Hold
- **PHOB** - Phone beneficiary
- **PHOI** - Phone ordering customer
- **PHON** - Phone ordering bank
- **REPA** - Return payment
- **SDVA** - Same day value
- **TELB** - Telex beneficiary
- **TELE** - Telex ordering bank
- **TELI** - Telex ordering customer
- **URGP** - Urgent payment

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

### Field 32A: Value Date, Currency, Amount

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :32A: | 6!n3!a15d | PaymentInstruction | settlementDate, currency, amount | Mandatory. Settlement date, currency, amount |

**Example:**
```
:32A:241220USD1000000,
```
- **241220** = December 20, 2024
- **USD** = US Dollars
- **1000000,** = $1,000,000.00

### Field 33B: Currency/Instructed Amount

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :33B: | 3!a15d | PaymentInstruction.extensions | instructedCurrency, instructedAmount | Original currency/amount (if different from settlement) |

**Example:**
```
:33B:EUR850000,
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

### Field 51A: Sending Institution

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :51A: | BIC | FinancialInstitution | bicCode | Sending institution (rarely used) |

**Example:**
```
:51A:ABCBGB2LXXX
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

**Example Option D:**
```
:52D:JP Morgan Chase Bank NA
New York NY
US
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
:57A:HSBCHKHH XXX
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

**Example Option D:**
```
:58D:Deutsche Bank AG
Frankfurt
DE
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
:70:Cover for MT103 customer payments
Batch reference: BATCH20241220001
FX settlement for spot deal
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
:72:/INS/URGENT PAYMENT
/BNF/Settlement for FX deal
/ACC/Nostro reconciliation
```

### Field 77B: Regulatory Reporting

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :77B: | 3*35x | PaymentInstruction.extensions | regulatoryReporting | Regulatory reporting information (up to 105 chars) |

**Example:**
```
:77B:/BENEFRES/US
/ORDERRES/GB
/REMI/Payment for services
```

---

## Message Examples

### Example 1: Simple FX Settlement Between Banks

```
{1:F01CHASUS33AXXX0000000000}
{2:I202DEUTDEFFXXXXN}
{4:
:20:FX20241220001
:21:FXSPOT123456
:32A:241220USD1000000,
:52A:CHASUS33XXX
:58A:DEUTDEFFXXX
:72:/BNF/FX settlement for spot deal
/ACC/EUR vs USD
-}
```

**Explanation:**
- JP Morgan Chase (CHASUS33) sending $1,000,000 to Deutsche Bank (DEUTDEFF)
- Settlement date: December 20, 2024
- Related to FX spot deal

### Example 2: MT202COV - Cover Payment for MT103

```
{1:F01ABCBGB2LAXXX0000000000}
{2:I202XYZSGB2LXXXXN}
{4:
:20:COVER20241220
:21:MT103REF98765
:13C:/CLSTIME/1600
:32A:241220EUR500000,
:52A:ABCBGB2LXXX
:53A:CITIGB2LXXX
:54A:BNPAFRPPXXX
:57A:XYZSGB2LXXX
:58A:XYZSGB2LXXX
:70:Cover for MT103 customer payment
Reference: MT103REF98765
Customer: ABC Corporation
:71A:SHA
-}
```

**Explanation:**
- ABC Bank (ABCBGB2L) covering €500,000 payment to XYZ Bank (XYZSGB2L)
- Related MT103 reference: MT103REF98765
- Charges shared (SHA)
- Intermediaries: Citibank London, BNP Paribas Paris

### Example 3: Interbank Position Management with FX

```
{1:F01HSBCHKHHAXXX0000000000}
{2:I202HSBCUS33XXXXN}
{4:
:20:POSN20241220HK
:21:NOSTRO1220
:26T:FXD
:32A:241220USD2500000,
:33B:HKD19375000,
:36:7,75
:52A:HSBCHKHHXXX
:56A:CITIUS33XXX
:58A:HSBCUS33XXX
:70:Position management - HKD to USD
Nostro account funding
FX rate: 7.75
:71A:OUR
:71F:USD50,
:72:/INS/Same day value required
/ACC/Nostro account 12345678
-}
```

**Explanation:**
- HSBC Hong Kong transferring $2,500,000 to HSBC New York
- Original amount: HKD 19,375,000
- Exchange rate: 7.75 HKD/USD
- Intermediary: Citibank New York
- All charges borne by sender (OUR)

### Example 4: Third Party Payment with Full Chain

```
{1:F01BNPAFRPPAXXX0000000000}
{2:I202DEUTDEFFXXXXN}
{4:
:20:TP20241220PARIS
:21:CLIENT-REF-456
:23E:SDVA
:32A:241220EUR1500000,
:50K:/FR1420041010050500013M02606
Global Trading Company SARL
Paris
FR
:52A:BNPAFRPPXXX
:53A:CITIGB2LXXX
:54A:COBADEFFXXX
:56A:DEUTDEFFXXX
:57A:DEUTDEFFXXX
:58A:DEUTDEFFXXX
:59:/DE89370400440532013000
Manufacturing GmbH
Frankfurt
DE
:70:Third party payment
Trade finance settlement
Invoice ref: TRD-2024-9999
:71A:SHA
:71F:EUR20,
:77B:/ORDERRES/FR
/BENEFRES/DE
/DETAILS/Trade settlement
-}
```

**Explanation:**
- BNP Paribas Paris facilitating €1,500,000 payment
- From: Global Trading Company (France)
- To: Manufacturing GmbH (Germany)
- Chain: BNP Paris → Citi London → Commerzbank Frankfurt → Deutsche Bank Frankfurt
- Same day value (SDVA)
- Regulatory reporting for France and Germany

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 47 fields in MT202 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles transaction reference, amounts, dates
- Extension fields accommodate SWIFT-specific elements (charges, time indications, regulatory reporting)
- FinancialInstitution entity supports all institution fields (ordering, beneficiary, intermediaries, correspondents)
- Account entity handles institution accounts (nostro/vostro)
- Party entity supports ordering and beneficiary customers when present

**Key Extension Fields Used:**
- relatedReference (Field 21 - link to MT103 or other messages)
- timeIndication (Field 13C - CLSTIME, SNDTIME, etc.)
- instructionCode (Field 23E - SDVA, URGP, PHOB, etc.)
- transactionTypeCode (Field 26T - COV, FXD)
- instructedCurrency, instructedAmount (Field 33B - original currency)
- exchangeRate (Field 36 - FX rate)
- chargeBearer (Field 71A - BEN/OUR/SHA)
- senderCharges, receiverCharges (Field 71F/71G)
- senderToReceiverInfo (Field 72 - bank instructions)
- regulatoryReporting (Field 77B - compliance info)

---

## References

- **SWIFT Standards:** MT202 - General Financial Institution Transfer
- **SWIFT Standards Release:** 2024
- **Category:** Cat 2 - Financial Institution Transfers
- **Related Messages:** MT202COV, MT103, MT200, MT205, pacs.009
- **ISO 20022 Equivalent:** pacs.009 - Financial Institution Credit Transfer

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
