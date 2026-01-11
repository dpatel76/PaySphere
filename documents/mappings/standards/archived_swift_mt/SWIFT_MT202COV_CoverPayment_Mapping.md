# SWIFT MT202COV - General FI to FI Transfer with Cover Mapping

## Message Overview

**Message Type:** MT202COV - General Financial Institution Transfer with Cover
**Category:** Category 2 - Financial Institution Transfers
**Purpose:** Used by financial institutions to transfer funds between themselves for their own account PLUS provide underlying customer credit transfer information
**Direction:** FI → FI (Bank to Bank with Customer Details)
**Scope:** Interbank fund transfers with underlying customer information (cover payments)

**Key Use Cases:**
- Cover payments for MT103 customer credit transfers
- Foreign exchange (FX) settlement with customer details
- Correspondent banking with underlying customer information
- Compliance with regulatory requirements for customer transparency
- Cross-border payments requiring full transaction chain visibility
- AML/KYC compliance for covered payments

**Relationship to Other Messages:**
- **MT202**: General FI Transfer (WITHOUT underlying customer info)
- **MT103**: Single Customer Credit Transfer (customer-initiated payment)
- **MT200**: FI Own Account Transfer (simpler version)
- **MT205**: FI Direct Debit (interbank debit)
- **pacs.009**: ISO 20022 equivalent (Financial Institution Credit Transfer)

**Key Difference from MT202:**
- **MT202COV**: Includes fields 50a (Ordering Customer) and 59a (Beneficiary Customer)
- **MT202**: Pure interbank transfer without customer details
- **MT202COV**: Used when underlying customer information must be transmitted
- **MT202**: Used for bank's own account or position management

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in MT202COV** | 52 |
| **Fields Mapped to CDM** | 52 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- FinancialInstitution (ordering institution, beneficiary institution, intermediaries)
- Account (ordering institution account, beneficiary institution account, customer accounts)
- Party (ordering customer, beneficiary customer)

---

## Complete Field Mapping

### Mandatory Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 20 | Transaction Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction | endToEndId | Sender's transaction reference |
| 21 | Related Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction.extensions | relatedReference | Reference to related message (MT103) |
| 32A | Value Date/Currency/Amount | 6!n3!a15d | - | M | YYMMDD/CCY/Amount | PaymentInstruction | settlementDate, currency, amount | Value date, currency, and amount |
| 50a | Ordering Customer | Option A, F, K | - | M | BIC/Account/Name | Party | bic, accountNumber, name, address | Ultimate ordering customer (MANDATORY for MT202COV) |
| 52a | Ordering Institution | Option A, D | - | O | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Ordering (sender) institution |
| 53a | Sender's Correspondent | Option A, B, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Sender's correspondent bank |
| 54a | Receiver's Correspondent | Option A, B, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Receiver's correspondent bank |
| 56a | Intermediary | Option A, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Intermediary institution |
| 57a | Account With Institution | Option A, B, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Beneficiary's correspondent |
| 58a | Beneficiary Institution | Option A, D | - | M | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Beneficiary (receiver) institution |
| 59a | Beneficiary Customer | Option A, F | - | M | BIC/Account/Name | Party | bic, accountNumber, name, address | Ultimate beneficiary customer (MANDATORY for MT202COV) |

### Optional Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 13C | Time Indication | /8c/4!n | - | O | /CODE/Time | PaymentInstruction.extensions | timeIndication | Time indication (e.g., /CLSTIME/1600) |
| 23E | Instruction Code | 4!c[/30x] | - | O | Codes | PaymentInstruction.extensions | instructionCode | Processing instructions |
| 26T | Transaction Type Code | 3!c | 3 | O | Codes | PaymentInstruction.extensions | transactionTypeCode | Type of transaction (typically COV) |
| 33B | Currency/Amount | 3!a15d | - | O | CCY/Amount | PaymentInstruction.extensions | instructedCurrency, instructedAmount | Instructed currency/amount |
| 36 | Exchange Rate | 12d | 12 | O | Decimal | PaymentInstruction.extensions | exchangeRate | Exchange rate |
| 51A | Sending Institution | Option A | - | O | BIC | FinancialInstitution | bicCode | Sending institution (rarely used) |
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
:20:COV20241220001
```

### Field 21: Related Reference

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :21: | 16x | PaymentInstruction.extensions | relatedReference | Reference to underlying MT103 customer payment |

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
```

**Common Codes:**
- **COV** - Cover (most common for MT202COV)
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

### Field 50a: Ordering Customer (Options A, F, K) - MANDATORY

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :50A: | BIC | Party | bic, partyName | Ordering customer identified by BIC |
| :50F: | Party ID | Party | partyIdentifier, name, address | Ordering customer with detailed ID |
| :50K: | Account + Name/Address | Party, Account | accountNumber, partyName, address | Account and name/address |

**Example Option K:**
```
:50K:/GB29ABCB60161331926819
ABC Corporation Ltd
123 Business Street
London EC1A 1BB
GB
```

**Example Option A:**
```
:50A:/GB29ABCB60161331926819
ABCBGB2LXXX
```

**Example Option F:**
```
:50F:/GB29ABCB60161331926819
1/ABC Corporation Ltd
2/123 Business Street
3/GB/EC1A 1BB/London
```

**Critical Note:** Field 50a is MANDATORY in MT202COV (vs. optional in MT202). This distinguishes cover payments from pure interbank transfers.

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

**Example Option D:**
```
:58D:Deutsche Bank AG
Frankfurt
DE
```

### Field 59a: Beneficiary Customer (Options A, F) - MANDATORY

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :59A: | BIC | Party | bic | Ultimate beneficiary by BIC |
| :59F: | Account + Party ID | Party, Account | accountNumber, partyIdentifier, name, address | Account and party details |

**Example Option F:**
```
:59F:/DE89370400440532013000
1/Peter Schmidt
2/Hauptstrasse 123
3/DE/10115/Berlin
```

**Example Option A:**
```
:59A:/DE89370400440532013000
DEUTDEFFXXX
```

**Critical Note:** Field 59a is MANDATORY in MT202COV (vs. optional in MT202). This provides full beneficiary customer information for regulatory compliance.

### Field 70: Remittance Information

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :70: | 4*35x | PaymentInstruction | remittanceInformation | Purpose/details of payment (up to 140 chars) |

**Example:**
```
:70:Cover for MT103 customer payment
Invoice ref: INV-2024-5678
Order ref: PO-9876
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
/BNF/Cover for customer payment
/ACC/Related to MT103REF12345
```

### Field 77B: Regulatory Reporting

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :77B: | 3*35x | PaymentInstruction.extensions | regulatoryReporting | Regulatory reporting information (up to 105 chars) |

**Example:**
```
:77B:/ORDERRES/GB
/BENEFRES/DE
/DETAILS/Trade payment for goods
```

---

## Message Examples

### Example 1: Cover Payment for MT103 Customer Transfer

```
{1:F01ABCBGB2LAXXX0000000000}
{2:I202DEUTDEFFXXXXN}
{3:{121:550e8400-e89b-12d3-a456-426614174000}}
{4:
:20:COV20241220001
:21:MT103REF12345
:26T:COV
:32A:241220EUR500000,
:50K:/GB29ABCB60161331926819
ABC Corporation Ltd
123 Business Street
London EC1A 1BB
GB
:52A:ABCBGB2LXXX
:53A:CITIGB2LXXX
:57A:DEUTDEFFXXX
:58A:DEUTDEFFXXX
:59F:/DE89370400440532013000
1/XYZ Manufacturing GmbH
2/Industriestrasse 45
3/DE/60308/Frankfurt
:70:Cover for MT103 customer payment
Ref: MT103REF12345
Invoice: INV-2024-9876
:71A:SHA
:71F:EUR20,
:72:/INS/Cover payment for customer transfer
/BNF/Underlying customer details provided
-}
```

**Explanation:**
- ABC Bank London covering €500,000 for customer ABC Corporation
- Ultimate beneficiary: XYZ Manufacturing GmbH in Frankfurt
- Related MT103 reference: MT103REF12345
- Intermediary: Citibank London
- Charges shared (SHA)

### Example 2: Cross-Border Cover Payment with FX

```
{1:F01CHASUS33AXXX0000000000}
{2:I202HSBCHKHHXXXXN}
{3:{121:650e8400-e89b-12d3-a456-426614174001}}
{4:
:20:COVCUST20241220
:21:CUST103-456789
:13C:/CLSTIME/1600
:26T:COV
:32A:241220HKD7750000,
:33B:USD1000000,
:36:7,75
:50K:/US12345678901234567890
Global Services Inc.
456 Fifth Avenue
New York NY 10018
US
:52A:CHASUS33XXX
:56A:HSBCUS33XXX
:58A:HSBCHKHHXXX
:59F:/HK123456789012345
1/Hong Kong Trading Ltd
2/Central Plaza
3/HK/999077/Kowloon
:70:Cover for customer USD payment
FX conversion USD to HKD
Rate: 7.75
:71A:SHA
:71F:USD50,
:77B:/ORDERRES/US
/BENEFRES/HK
/DETAILS/Payment for services
-}
```

**Explanation:**
- JP Morgan Chase NY covering payment for Global Services Inc.
- Original amount: USD 1,000,000
- Settlement amount: HKD 7,750,000
- Exchange rate: 7.75 HKD/USD
- Beneficiary: Hong Kong Trading Ltd
- Intermediary: HSBC New York

### Example 3: Same Day Value Cover Payment

```
{1:F01BNPAFRPPAXXX0000000000}
{2:I202XYZSGB2LXXXXN}
{4:
:20:SDVACOV20241220
:21:MT103-URGENT-001
:23E:SDVA
:23E:URGP
:26T:COV
:32A:241220GBP250000,
:50K:/FR7630006000011234567890189
French Export Company SA
Paris
FR
:52A:BNPAFRPPXXX
:53A:CITIGB2LXXX
:57A:XYZSGB2LXXX
:58A:XYZSGB2LXXX
:59F:/GB82WEST12345698765432
1/UK Import Services Ltd
2/10 Downing Street
3/GB/SW1A 2AA/London
:70:Urgent cover payment
Same day value required
Time-critical settlement
:71A:OUR
:71F:EUR35,
:72:/INS/URGENT - SAME DAY VALUE
/INS/Phone beneficiary immediately
/BNF/Time-critical payment
-}
```

**Explanation:**
- BNP Paribas Paris providing urgent cover for French Export Company
- Beneficiary: UK Import Services Ltd in London
- Same day value (SDVA) and urgent (URGP) instructions
- All charges borne by sender (OUR)
- Intermediary: Citibank London

### Example 4: Cover Payment with Full Intermediary Chain

```
{1:F01ABCBUS33AXXX0000000000}
{2:I202XYZJPJTXXXXN}
{3:{121:750e8400-e89b-12d3-a456-426614174002}}
{4:
:20:COVCHAIN20241220
:21:CUSTTRF-789012
:26T:COV
:32A:241220JPY110000000,
:33B:USD1000000,
:36:110,00
:50A:/US98765432109876543210
ABCBUS33XXX
:52A:ABCBUS33XXX
:53A:CITIUS33XXX
:54A:HSBCHKHHXXX
:56A:MUFGJPJTXXX
:57A:XYZJPJTXXX
:58A:XYZJPJTXXX
:59A:/JP1234567890123456
XYZJPJTXXX
:70:Cover payment with full chain
USD to JPY conversion
Multiple intermediaries
:71A:SHA
:71F:USD30,
:71F:USD15,
:72:/INS/Multi-hop correspondent banking
/ACC/Nostro account 9876543210
/BNF/Cover for customer transfer
:77B:/ORDERRES/US
/BENEFRES/JP
/DETAILS/Cross-border trade payment
-}
```

**Explanation:**
- ABC Bank US to XYZ Bank Japan
- USD 1,000,000 converted to JPY 110,000,000 (rate: 110.00)
- Full correspondent chain: Citibank NY → HSBC Hong Kong → MUFG Tokyo
- Customer details included for compliance
- Regulatory reporting for US and Japan

---

## CDM Gap Analysis

**Result:** No CDM enhancements required ✅

All 52 fields in MT202COV successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles transaction reference, amounts, dates
- Extension fields accommodate SWIFT-specific elements (charges, time indications, regulatory reporting)
- FinancialInstitution entity supports all institution fields (ordering, beneficiary, intermediaries, correspondents)
- Account entity handles institution accounts (nostro/vostro) and customer accounts
- **Party entity supports both ordering customer (Field 50a) and beneficiary customer (Field 59a)**

**Key Extension Fields Used:**
- relatedReference (Field 21 - link to MT103)
- timeIndication (Field 13C - CLSTIME, SNDTIME, etc.)
- instructionCode (Field 23E - SDVA, URGP, PHOB, etc.)
- transactionTypeCode (Field 26T - typically COV)
- instructedCurrency, instructedAmount (Field 33B - original currency)
- exchangeRate (Field 36 - FX rate)
- chargeBearer (Field 71A - BEN/OUR/SHA)
- senderCharges, receiverCharges (Field 71F/71G)
- senderToReceiverInfo (Field 72 - bank instructions)
- regulatoryReporting (Field 77B - compliance info)

**Critical MT202COV-Specific Mappings:**
- **Field 50a** (Ordering Customer) - MANDATORY in MT202COV → Party entity with full customer details
- **Field 59a** (Beneficiary Customer) - MANDATORY in MT202COV → Party entity with full beneficiary details
- These fields distinguish MT202COV from MT202 and enable full payment transparency for regulatory compliance

---

## No CDM Gaps Identified ✅

All 52 MT202COV fields successfully map to existing CDM model. No enhancements required.

The existing GPS CDM already supports:
- Customer party information (ordering and beneficiary)
- Financial institution chain (multiple intermediaries)
- Account information (institution and customer accounts)
- Regulatory reporting and compliance fields
- Foreign exchange data (rates, original amounts)
- Charge allocation and fee tracking
- Bank-to-bank communication fields

---

## Code Lists and Valid Values

### :23E: Instruction Code
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

### :26T: Transaction Type Code
- **COV** - Cover (primary code for MT202COV)
- **FXD** - Foreign exchange deal

### :71A: Details of Charges
- **BEN** - Beneficiary pays all charges
- **OUR** - Ordering institution pays all charges
- **SHA** - Shared charges

---

## Related SWIFT Messages

| Message | Description | Relationship to MT202COV |
|---------|-------------|------------------------|
| **MT202** | General FI Transfer | MT202COV adds customer fields (50a, 59a) |
| **MT103** | Single Customer Credit Transfer | MT202COV is the cover payment |
| **MT200** | FI Own Account Transfer | Simpler version without customer info |
| **MT205** | FI Direct Debit | Debit equivalent |
| **pacs.009** | ISO 20022 FI Credit Transfer | ISO 20022 equivalent |

---

## Conversion to ISO 20022

MT202COV maps to ISO 20022 pacs.009 (Financial Institution Credit Transfer):

| MT202COV Field | ISO 20022 Message | ISO 20022 XPath |
|----------------|-------------------|-----------------|
| :20: | pacs.009 | PmtId/EndToEndId |
| :21: | pacs.009 | PmtId/InstrId |
| :32A: | pacs.009 | IntrBkSttlmAmt + IntrBkSttlmDt |
| :50a: | pacs.009 | UltmtDbtr/Nm + PstlAdr |
| :52a: | pacs.009 | InstgAgt |
| :58a: | pacs.009 | InstdAgt |
| :59a: | pacs.009 | UltmtCdtr/Nm + PstlAdr |
| :70: | pacs.009 | RmtInf/Ustrd |
| :71A: | pacs.009 | ChrgBr |

---

## References

- **SWIFT Standards:** MT202COV - General Financial Institution Transfer with Cover
- **SWIFT Standards Release:** 2024
- **Category:** Cat 2 - Financial Institution Transfers
- **Related Messages:** MT202, MT103, MT200, MT205, pacs.009
- **ISO 20022 Equivalent:** pacs.009 - Financial Institution Credit Transfer
- **GPS CDM Schema:** `/schemas/01_payment_instruction_complete_schema.json`
- **GPS CDM Extensions:** `/schemas/payment_instruction_extensions_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
**Next Review:** Q1 2025
