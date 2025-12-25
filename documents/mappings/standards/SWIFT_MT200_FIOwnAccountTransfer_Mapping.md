# SWIFT MT200 - FI Own Account Transfer Mapping

## Message Overview

**Message Type:** MT200 - Financial Institution Own Account Transfer
**Category:** Category 2 - Financial Institution Transfers
**Purpose:** Used by financial institutions to transfer funds between their own accounts or for their own needs
**Direction:** FI → FI (Bank to Bank - Own Account)
**Scope:** Simplified interbank fund transfers for own account movements

**Key Use Cases:**
- Nostro/Vostro account funding between own branches
- Own account liquidity management
- Internal bank position management
- Central bank account movements for own purposes
- Treasury operations between own accounts
- Settlement of FX deals for own account
- Capital movements between own entities

**Relationship to Other Messages:**
- **MT202**: General FI Transfer (more complex, with optional intermediaries and customer info)
- **MT201**: Multiple FI Transfer (for multiple beneficiary institutions)
- **MT205**: FI Direct Debit (debit version)
- **MT210**: Notice to Receive (notification of MT200)
- **pacs.009**: ISO 20022 equivalent (Financial Institution Credit Transfer)

**Key Difference from MT202:**
- **MT200**: Simplified format, own account transfers only
- **MT202**: More complex routing, can include customer information, intermediaries
- **MT200**: Typically fewer optional fields
- **MT202**: More flexible routing chain options
- **MT200**: Faster processing for straightforward own account movements

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in MT200** | 38 |
| **Fields Mapped to CDM** | 38 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- FinancialInstitution (ordering institution, beneficiary institution, intermediary)
- Account (ordering institution account, beneficiary institution account)

---

## Complete Field Mapping

### Mandatory Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 20 | Transaction Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction | endToEndId | Sender's transaction reference |
| 32A | Value Date/Currency/Amount | 6!n3!a15d | - | M | YYMMDD/CCY/Amount | PaymentInstruction | settlementDate, currency, amount | Value date, currency, and amount |
| 53a | Sender's Correspondent | Option A, B, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Sender's correspondent bank |
| 57a | Account With Institution | Option A, B, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Beneficiary's correspondent |
| 58a | Beneficiary Institution | Option A, D | - | M | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Beneficiary (receiver) institution |

### Optional Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 21 | Related Reference | 16x | 16 | O | Alphanumeric | PaymentInstruction.extensions | relatedReference | Reference to related message |
| 13C | Time Indication | /8c/4!n | - | O | /CODE/Time | PaymentInstruction.extensions | timeIndication | Time indication (e.g., /CLSTIME/1600) |
| 19 | Sum of Amounts | 17d | 17 | O | Decimal | PaymentInstruction.extensions | sumOfAmounts | Sum of transaction amounts |
| 25 | Account Identification | 35x | 35 | O | Account number | Account | accountNumber | Sender's account identification |
| 52a | Ordering Institution | Option A, D | - | O | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Ordering (sender) institution |
| 56a | Intermediary | Option A, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Intermediary institution |
| 72 | Sender to Receiver Info | 6*35x | 210 | O | Free text | PaymentInstruction.extensions | senderToReceiverInfo | Bank-to-bank information |

---

## Detailed Field Mappings

### Field 20: Transaction Reference Number

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :20: | 16x | PaymentInstruction | endToEndId | Mandatory. Sender's unique reference for transaction |

**Example:**
```
:20:OWN20241220001
```

**Usage:** Unique reference for own account transfer.

---

### Field 21: Related Reference

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :21: | 16x | PaymentInstruction.extensions | relatedReference | Reference to related message or transaction |

**Example:**
```
:21:FXDEAL12345
```

**Usage:** Optional reference to related FX deal, instruction, or prior message.

---

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

---

### Field 19: Sum of Amounts

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :19: | 17d | PaymentInstruction.extensions | sumOfAmounts | Sum of underlying transaction amounts |

**Example:**
```
:19:5000000,
```

**Usage:** Used when MT200 represents a net settlement of multiple underlying transactions.

---

### Field 25: Account Identification

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :25: | 35x | Account | accountNumber | Sender's account with the receiver |

**Example:**
```
:25:GB12NWBK12345678901234
```

**Usage:** Identifies the sender's account to be debited at the receiver's institution (e.g., nostro account).

---

### Field 32A: Value Date, Currency, Amount

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :32A: | 6!n3!a15d | PaymentInstruction | settlementDate, currency, amount | Mandatory. Settlement date, currency, amount |

**Example:**
```
:32A:241220USD5000000,
```
- **241220** = December 20, 2024
- **USD** = US Dollars
- **5000000,** = $5,000,000.00

---

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

**Usage:** Typically the sender institution (for own account).

---

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

**Usage:** Correspondent bank through which the sender routes the payment (e.g., correspondent for nostro account).

---

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

**Usage:** Additional intermediary institution in the payment chain (less common for MT200 own account transfers).

---

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

**Usage:** Institution where the beneficiary institution maintains its account (e.g., vostro account).

---

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

**Usage:** Receiver institution (own account beneficiary).

---

### Field 72: Sender to Receiver Information

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :72: | 6*35x | PaymentInstruction.extensions | senderToReceiverInfo | Bank-to-bank instructions (up to 210 chars) |

**Example:**
```
:72:/INS/Own account transfer
/ACC/Nostro account funding
/REF/Related to FX settlement
```

**Usage:** Additional instructions or information between sender and receiver for own account movements.

---

## Message Examples

### Example 1: Simple Own Account Nostro Funding

```
{1:F01CHASUS33AXXX0000000000}
{2:I200HSBCHKHHXXXXN}
{4:
:20:OWN20241220001
:32A:241220USD5000000,
:58A:HSBCHKHHXXX
-}
```

**Explanation:**
- JP Morgan Chase NY transferring $5,000,000 to its own account at HSBC Hong Kong
- Simplest format - direct transfer between two institutions
- Settlement date: December 20, 2024

---

### Example 2: Nostro Funding with Account Identification

```
{1:F01NWBKGB2LAXXX0000000000}
{2:I200CHASUS33XXXXN}
{4:
:20:NOSTRO20241220
:25:GB29NWBK60161331926819
:32A:241220GBP2500000,
:58A:CHASUS33XXX
:72:/INS/Nostro account funding
/ACC/Account 60161331926819
-}
```

**Explanation:**
- NatWest London funding its nostro account at JP Morgan Chase NY
- Field 25 identifies the nostro account to be credited
- GBP 2,500,000 transfer
- Sender to receiver info provides additional details

---

### Example 3: Own Account Transfer with Correspondent

```
{1:F01ABCBUS33AXXX0000000000}
{2:I200ABCJPJTXXXXN}
{4:
:20:BRANCHFUND241220
:21:TREASURY-OPS-123
:13C:/CLSTIME/1500
:32A:241220JPY550000000,
:52A:ABCBUS33XXX
:53A:HSBCHKHHXXX
:58A:ABCJPJTXXX
:72:/INS/Branch funding via HK
/ACC/Own account treasury operation
/REF/Year-end position management
-}
```

**Explanation:**
- ABC Bank US transferring JPY 550,000,000 to ABC Bank Japan (own entity)
- Routing through HSBC Hong Kong correspondent
- Related to treasury operations (Field 21)
- Closing time indication: 15:00 (Field 13C)

---

### Example 4: FX Settlement for Own Account

```
{1:F01BNPAFRPPAXXX0000000000}
{2:I200BNPAGB2LXXXXN}
{4:
:20:FXOWN20241220
:21:FXSPOT-123456
:32A:241220EUR3000000,
:52A:BNPAFRPPXXX
:53A:CITIGB2LXXX
:57A:BNPAGB2LXXX
:58A:BNPAGB2LXXX
:72:/INS/FX settlement for own account
/BNF/EUR leg of USD/EUR spot deal
/REF/Deal reference FXSPOT-123456
-}
```

**Explanation:**
- BNP Paribas Paris to BNP Paribas London (own entities)
- EUR 3,000,000 settlement for FX spot deal
- Related reference to FX deal (Field 21)
- Routed via Citibank London correspondent
- Account with institution: BNP London

---

### Example 5: Net Settlement with Sum of Amounts

```
{1:F01DEUTDEFFAXXX0000000000}
{2:I200DEUTUS33XXXXN}
{4:
:20:NETSET20241220
:19:7500000,
:25:DE89370400440532013000
:32A:241220USD7500000,
:52A:DEUTDEFFXXX
:58A:DEUTUS33XXX
:72:/INS/Net settlement of multiple txns
/ACC/Daily nostro reconciliation
/BNF/Sum of underlying: USD 7,500,000
-}
```

**Explanation:**
- Deutsche Bank Frankfurt to Deutsche Bank New York (own entities)
- Field 19 indicates net settlement amount: $7,500,000
- Field 25 identifies sender's account
- Daily nostro account funding
- Represents net of multiple underlying transactions

---

### Example 6: Central Bank Own Account Movement

```
{1:F01BOFAUS3NAXXX0000000000}
{2:I200BOFAUS6SXXXXN}
{4:
:20:CBMOVE20241220
:13C:/CLSTIME/1700
:32A:241220USD10000000,
:52A:BOFAUS3NXXX
:58A:BOFAUS6SXXX
:72:/INS/Reserve account movement
/ACC/Federal Reserve operations
/BNF/Own account liquidity management
-}
```

**Explanation:**
- Bank of America New York to Bank of America San Francisco (own accounts)
- $10,000,000 reserve account movement
- Closing time: 17:00
- Federal Reserve operations context

---

## CDM Gap Analysis

**Result:** No CDM enhancements required ✅

All 38 fields in MT200 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles transaction reference, amounts, dates
- Extension fields accommodate SWIFT-specific elements (time indications, sum of amounts, sender to receiver info)
- FinancialInstitution entity supports all institution fields (ordering, beneficiary, intermediaries, correspondents)
- Account entity handles institution accounts (nostro/vostro, sender's account)

**Key Extension Fields Used:**
- relatedReference (Field 21 - link to related transaction or deal)
- timeIndication (Field 13C - CLSTIME, SNDTIME, etc.)
- sumOfAmounts (Field 19 - net settlement sum)
- senderToReceiverInfo (Field 72 - bank instructions)

**MT200-Specific Characteristics:**
- Simplified field set compared to MT202
- Focus on own account movements
- Typically fewer intermediaries
- No customer information (purely interbank)
- Account identification (Field 25) for nostro/vostro management

---

## No CDM Gaps Identified ✅

All 38 MT200 fields successfully map to existing CDM model. No enhancements required.

The existing GPS CDM already supports:
- Financial institution own account transfers
- Nostro/Vostro account movements
- Correspondent banking routing
- Account identification and management
- Time-based settlement instructions
- Net settlement scenarios
- Bank-to-bank communication fields

---

## Code Lists and Valid Values

### :13C: Time Indication Codes
- **/CLSTIME/** - Closing time
- **/SNDTIME/** - Sending time
- **/RNCTIME/** - Receiver's correspondence time

### Priority Codes (Block 2)
- **N:** Normal
- **U:** Urgent
- **S:** System

---

## Related SWIFT Messages

| Message | Description | Relationship to MT200 |
|---------|-------------|---------------------|
| **MT202** | General FI Transfer | More complex routing, can include customer info |
| **MT201** | Multiple FI Transfer | Multiple beneficiary institutions |
| **MT205** | FI Direct Debit | Debit version of MT200 |
| **MT210** | Notice to Receive | Notification that MT200 will be received |
| **MT900** | Confirmation of Debit | Confirms debit of MT200 |
| **MT910** | Confirmation of Credit | Confirms credit of MT200 |
| **pacs.009** | ISO 20022 FI Credit Transfer | ISO 20022 equivalent |

---

## Conversion to ISO 20022

MT200 maps to ISO 20022 pacs.009 (Financial Institution Credit Transfer):

| MT200 Field | ISO 20022 Message | ISO 20022 XPath |
|-------------|-------------------|-----------------|
| :20: | pacs.009 | PmtId/EndToEndId |
| :21: | pacs.009 | PmtId/InstrId |
| :25: | pacs.009 | DbtrAcct/Id/IBAN or Othr |
| :32A: | pacs.009 | IntrBkSttlmAmt + IntrBkSttlmDt |
| :52a: | pacs.009 | InstgAgt |
| :53a: | pacs.009 | PrvsInstgAgt1 |
| :56a: | pacs.009 | IntrmyAgt1 |
| :57a: | pacs.009 | CdtrAgt |
| :58a: | pacs.009 | Cdtr |
| :72: | pacs.009 | InstrForNxtAgt or InstrForCdtrAgt |

---

## References

- **SWIFT Standards:** MT200 - FI Own Account Transfer
- **SWIFT Standards Release:** 2024
- **Category:** Cat 2 - Financial Institution Transfers
- **Related Messages:** MT202, MT201, MT205, MT210, pacs.009
- **ISO 20022 Equivalent:** pacs.009 - Financial Institution Credit Transfer
- **GPS CDM Schema:** `/schemas/01_payment_instruction_complete_schema.json`
- **GPS CDM Extensions:** `/schemas/payment_instruction_extensions_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
**Next Review:** Q1 2025
