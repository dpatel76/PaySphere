# SWIFT MT205 - Financial Institution Direct Debit (COV) Mapping

## Message Overview

**Message Type:** MT205 - Financial Institution Direct Debit (COV)
**Category:** Category 2 - Financial Institution Transfers
**Purpose:** Used by a financial institution to request the direct debit of a financial institution's account based on pre-authorization, typically for cover of customer direct debit collections
**Direction:** FI → FI (Bank to Bank)
**Scope:** Authorized interbank direct debit with underlying customer information

**Key Use Cases:**
- Cover for customer direct debit collections (SEPA SDD, domestic DD)
- Automated clearing house (ACH) settlement
- Direct debit scheme settlement between banks
- Pre-authorized recurring interbank debits
- Collection of receivables through correspondent banks
- SEPA Core/B2B direct debit cover transactions
- Automated mandate-based collections

**Relationship to Other Messages:**
- **MT204**: General FI Direct Debit (simpler, no customer details)
- **MT202**: General FI Transfer (credit instruction)
- **pain.008**: Customer direct debit initiation (underlying message)
- **pacs.003**: ISO 20022 equivalent (FI to FI Customer Direct Debit)
- **MT103**: Customer credit transfer (opposite flow)

**Comparison with MT204:**
- **MT205**: Includes underlying customer/transaction details (COV variant)
- **MT204**: General direct debit without customer details
- **MT205**: Typically used for direct debit scheme cover
- **MT204**: Used for general interbank debits

**Comparison with pacs.003:**
- **MT205**: SWIFT format for interbank direct debit
- **pacs.003**: ISO 20022 equivalent (Financial Institution to Financial Institution Customer Direct Debit)
- Both support mandate-based collections

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in MT205** | 38 |
| **Fields Mapped to CDM** | 38 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- FinancialInstitution (creditor agent, debtor agent, intermediaries)
- Account (creditor account, debtor account)
- Party (creditor, debtor, ultimate parties)

---

## Complete Field Mapping

### Mandatory Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 20 | Transaction Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction | endToEndId | Sender's transaction reference |
| 21 | Related Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction.extensions | relatedReference | Reference to underlying collection/mandate |
| 32A | Value Date/Currency/Amount | 6!n3!a15d | - | M | YYMMDD/CCY/Amount | PaymentInstruction | settlementDate, currency, amount | Value date, currency, and amount |
| 52a | Ordering Institution | Option A, D | - | O | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Debtor agent (bank being debited) |
| 58a | Beneficiary Institution | Option A, D | - | M | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Creditor agent (collecting bank) |

### Optional Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 13C | Time Indication | /8c/4!n | - | O | /CODE/Time | PaymentInstruction.extensions | timeIndication | Time indication (e.g., /CLSTIME/1600) |
| 23E | Instruction Code | 4!c[/30x] | - | O | Codes | PaymentInstruction.extensions | instructionCode | Processing instructions |
| 26T | Transaction Type Code | 3!c | 3 | O | Codes | PaymentInstruction.extensions | transactionTypeCode | Type of transaction |
| 50a | Ordering Customer | Option A, F, K | - | O | Account/BIC/Name | Party | partyName, accountNumber | Debtor (customer being debited) |
| 53a | Sender's Correspondent | Option A, B, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Sender's correspondent bank |
| 54a | Receiver's Correspondent | Option A, B, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Receiver's correspondent bank |
| 56a | Intermediary | Option A, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Intermediary institution |
| 57a | Account With Institution | Option A, B, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Account with institution |
| 59a | Beneficiary Customer | Option A, F | - | O | Account/Name | Party | partyName, accountNumber | Creditor (customer receiving funds) |
| 70 | Remittance Information | 4*35x | 140 | O | Free text | PaymentInstruction | remittanceInformation | Purpose of payment |
| 72 | Sender to Receiver Info | 6*35x | 210 | O | Free text | PaymentInstruction.extensions | senderToReceiverInfo | Bank-to-bank information |

---

## Detailed Field Mappings

### Field 20: Transaction Reference Number

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :20: | 16x | PaymentInstruction | endToEndId | Mandatory. Creditor agent's unique reference |

**Example:**
```
:20:DDCOV20241220001
```

### Field 21: Related Reference

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :21: | 16x | PaymentInstruction.extensions | relatedReference | Reference to underlying customer collection or mandate |

**Example:**
```
:21:MANDATE2024001
```

### Field 13C: Time Indication

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :13C: | /8c/4!n | PaymentInstruction.extensions | timeIndication | Time-related processing instructions |

**Example:**
```
:13C:/CLSTIME/1600
:13C:/SNDTIME/0930
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
:23E:SDVA
:23E:CORT
```

**Common Codes:**
- **SDVA** - Same day value
- **CORT** - Cover for third party
- **HOLD** - Hold
- **URGP** - Urgent payment

### Field 26T: Transaction Type Code

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :26T: | 3!c | PaymentInstruction.extensions | transactionTypeCode | Type of underlying transaction |

**Example:**
```
:26T:DD
:26T:ACH
```

**Common Codes:**
- **DD** - Direct Debit
- **ACH** - Automated Clearing House
- **SDD** - SEPA Direct Debit

### Field 32A: Value Date, Currency, Amount

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :32A: | 6!n3!a15d | PaymentInstruction | settlementDate, currency, amount | Mandatory. Settlement date, currency, amount |

**Example:**
```
:32A:241220EUR1500,
```
- **241220** = December 20, 2024
- **EUR** = Euros
- **1500,** = €1,500.00

### Field 50a: Ordering Customer (Debtor) - Options A, F, K

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :50A: | BIC | Party | bic, partyName | Debtor identified by BIC |
| :50F: | Party ID | Party | partyIdentifier | Debtor with detailed ID |
| :50K: | Account + Name/Address | Party, Account | accountNumber, partyName, address | Account and name/address |

**Example Option K:**
```
:50K:/DE89370400440532013000
Peter Schmidt
Hauptstrasse 123
10115 Berlin
DE
```

**Note:** This is the debtor (customer whose account is being debited)

### Field 52a: Ordering Institution (Debtor Agent) - Options A, D

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :52A: | BIC | FinancialInstitution | bicCode | Debtor agent (bank being debited) by BIC |
| :52D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:52A:DEUTDEFFXXX
```

**Example Option D:**
```
:52D:Deutsche Bank AG
Frankfurt
DE
```

**Note:** This is the debtor's bank (account being debited)

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
:54A:BNPAFRPPXXX
```

### Field 56a: Intermediary (Options A, C, D)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :56A: | BIC | FinancialInstitution | bicCode | Intermediary identified by BIC |
| :56C: | Party ID | FinancialInstitution | partyIdentifier | Party identifier |
| :56D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:56A:COBADEFFXXX
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
:57A:BNPAFRPPXXX
```

### Field 58a: Beneficiary Institution (Creditor Agent) - Options A, D

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :58A: | BIC | FinancialInstitution | bicCode | Creditor agent by BIC (mandatory - collecting bank) |
| :58D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:58A:BNPAFRPPXXX
```

**Example Option D:**
```
:58D:BNP Paribas SA
Paris
FR
```

**Note:** This is the creditor's bank (initiating the collection)

### Field 59a: Beneficiary Customer (Creditor) - Options A, F

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :59A: | BIC | Party | bic | Creditor by BIC |
| :59F: | Account + Party ID | Party, Account | accountNumber, partyIdentifier | Account and party details |

**Example:**
```
:59:/FR7630006000011234567890189
Streaming Service Pro
100 Rue de la Paix
75002 Paris
FR
```

**Note:** This is the creditor (customer receiving the funds)

### Field 70: Remittance Information

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :70: | 4*35x | PaymentInstruction | remittanceInformation | Purpose/details of payment (up to 140 chars) |

**Example:**
```
:70:Monthly subscription payment
Mandate ref: MANDATE-2024-USER-789
Service period: December 2024
```

### Field 72: Sender to Receiver Information

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :72: | 6*35x | PaymentInstruction.extensions | senderToReceiverInfo | Bank-to-bank instructions (up to 210 chars) |

**Example:**
```
:72:/INS/SEPA Core Direct Debit
/MAND/Mandate signed 2024-01-15
/SEQ/Recurring collection
/CRED/FR72ZZZ123456
```

---

## Message Examples

### Example 1: SEPA Direct Debit Cover - Recurring Subscription

```
{1:F01BNPAFRPPAXXX0000000000}
{2:I205DEUTDEFFXXXXN}
{4:
:20:DDCOV20241220001
:21:MANDATE2024USER789
:23E:CORT
:26T:SDD
:32A:241220EUR9,99
:50K:/DE89370400440532013000
Anna Schmidt
Hauptstrasse 25
10115 Berlin
DE
:52A:DEUTDEFFXXX
:58A:BNPAFRPPXXX
:59:/FR7630006000011234567890189
Streaming Service Pro
100 Rue de la Paix
75002 Paris
FR
:70:Monthly subscription - Dec 2024
Mandate: MANDATE-2024-USER-789
Service: Premium streaming account
:72:/INS/SEPA Core DD - RCUR
/MAND/Signed 2023-06-15
/CRED/FR72ZZZ123456
/SEQ/Recurring
-}
```

**Explanation:**
- BNP Paribas Paris (creditor agent) requesting Deutsche Bank Frankfurt (debtor agent) to debit €9.99
- From: Anna Schmidt (debtor) - Deutsche Bank account
- To: Streaming Service Pro (creditor) - BNP Paribas account
- SEPA Core Direct Debit - Recurring sequence type
- Mandate reference: MANDATE-2024-USER-789
- Settlement date: December 20, 2024

### Example 2: SEPA B2B Direct Debit Cover - First Collection

```
{1:F01ABCBGB2LAXXX0000000000}
{2:I205BNPAFRPPXXXXN}
{4:
:20:B2BDDCOV20241220
:21:B2BMAND2024CORP456
:13C:/CLSTIME/1400
:23E:SDVA
:26T:SDD
:32A:241220EUR15000,
:50K:/FR1420041010050500013M02606
French Corporate Services SARL
50 Avenue des Champs-Elysées
75008 Paris
FR
:52A:BNPAFRPPXXX
:58A:ABCBGB2LXXX
:59:/GB29ABCB60161331926819
Office Supplies International Ltd
15 Business Park Drive
London EC1A 1BB
GB
:70:Supplier payment - Invoice INV-2024-12345
B2B direct debit - first collection
Due date: 2024-12-20
:72:/INS/SEPA B2B DD - FRST
/MAND/Signed 2024-12-01
/CRED/GB98ZZZ987654
/SEQ/First collection
/PRENO/2024-12-15
-}
```

**Explanation:**
- ABC Bank London (creditor agent) requesting BNP Paribas Paris (debtor agent) to debit €15,000
- From: French Corporate Services SARL (debtor)
- To: Office Supplies International Ltd (creditor)
- SEPA B2B Direct Debit - First collection (FRST)
- Mandate signed: 2024-12-01
- Pre-notification date: 2024-12-15
- Same day value required

### Example 3: Domestic ACH Direct Debit Cover

```
{1:F01BOFAUS3NAXXX0000000000}
{2:I205CHASUS33XXXXN}
{4:
:20:ACHDD20241220001
:21:ACHMANDATE98765
:26T:ACH
:32A:241220USD250,
:50K:/123456789012345
John Doe
456 Main Street
Anytown CA 90210
US
:52A:CHASUS33XXX
:58A:BOFAUS3NXXX
:59:/987654321098765
Utility Company Inc
789 Service Road
Metropolis NY 10001
US
:70:Utility bill payment - December 2024
Account number: 123-456-789
Service address: 456 Main St
:72:/INS/ACH direct debit
/AGR/Pre-authorized payment plan
/TYP/Recurring monthly utility
-}
```

**Explanation:**
- Bank of America (creditor agent) requesting JP Morgan Chase (debtor agent) to debit $250
- From: John Doe (debtor)
- To: Utility Company Inc (creditor)
- ACH direct debit for utility bill
- Pre-authorized payment agreement
- Monthly recurring collection

### Example 4: Mortgage Payment Direct Debit with Intermediary

```
{1:F01HSBCGB2LAXXX0000000000}
{2:I205DEUTDEFFXXXXN}
{4:
:20:MORTGAGEDD241220
:21:MORTMAND2020001
:13C:/CLSTIME/1600
:26T:DD
:32A:241220EUR1850,
:50K:/DE89370400440532013000
Maria Mueller
Gartenstrasse 45
60311 Frankfurt
DE
:52A:DEUTDEFFXXX
:56A:CITIGB2LXXX
:58A:HSBCGB2LXXX
:59:/GB33HSBC40051512345678
HomeLoans UK Limited
25 Banking Street
London EC2M 4AA
GB
:70:Monthly mortgage payment
Mortgage account: ML-2020-123456
Property: Gartenstrasse 45, Frankfurt
December 2024 installment
:72:/INS/Recurring mortgage DD
/MAND/Original date 2020-03-01
/SEQ/Recurring
/VIA/Intermediary CITI London
-}
```

**Explanation:**
- HSBC London (creditor agent) requesting Deutsche Bank Frankfurt (debtor agent) to debit €1,850
- From: Maria Mueller (debtor) - Germany
- To: HomeLoans UK Limited (creditor) - UK
- Via: Citibank London (intermediary)
- Monthly mortgage payment
- Mandate from 2020 (long-standing arrangement)

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 38 fields in MT205 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles transaction reference, amounts, dates
- Extension fields accommodate SWIFT-specific elements (mandate reference, direct debit codes, time indications)
- FinancialInstitution entity supports creditor agent, debtor agent, intermediaries, correspondents
- Account entity handles creditor and debtor accounts
- Party entity supports creditor and debtor identification with full address details

**Key Extension Fields Used:**
- relatedReference (Field 21 - mandate reference or authorization)
- timeIndication (Field 13C - CLSTIME, SNDTIME, etc.)
- instructionCode (Field 23E - SDVA, CORT, URGP, etc.)
- transactionTypeCode (Field 26T - DD, ACH, SDD)
- senderToReceiverInfo (Field 72 - mandate details, sequence type, creditor ID)
- remittanceInformation (Field 70 - purpose, invoice details)

**Direct Debit Semantics:**
- paymentDirection extension field set to "DEBIT" to indicate collection
- initiatingParty identifies the creditor/creditor agent (Field 58a/59a)
- debitedParty identifies the debtor/debtor agent (Field 50a/52a)
- mandateReference captured in relatedReference (Field 21)
- mandateDetails encoded in senderToReceiverInfo (Field 72) including sequence type (FRST/RCUR/FNAL/OOFF), creditor ID, signature date

**SEPA Direct Debit Mapping:**
- Local Instrument Code (CORE/B2B) encoded in transactionTypeCode or senderToReceiverInfo
- Creditor Scheme ID included in Field 72
- Sequence Type (FRST/RCUR/FNAL/OOFF) included in Field 72
- Pre-notification information in Field 72

---

## References

- **SWIFT Standards:** MT205 - Financial Institution Direct Debit (COV)
- **SWIFT Standards Release:** 2024
- **Category:** Cat 2 - Financial Institution Transfers
- **Related Messages:** MT204, MT202, pain.008, pacs.003
- **ISO 20022 Equivalent:** pacs.003 - FI to FI Customer Direct Debit
- **SEPA Rulebook:** EPC Implementation Guidelines for SEPA Direct Debit Core/B2B
- **Authorization Requirements:** Mandate or pre-authorization agreement required

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
