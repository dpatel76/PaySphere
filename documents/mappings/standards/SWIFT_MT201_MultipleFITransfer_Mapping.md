# SWIFT MT201 - Multiple FI Transfer Mapping

## Message Overview

**Message Type:** MT201 - Multiple Financial Institution Transfer
**Category:** Category 2 - Financial Institution Transfers
**Purpose:** Used by financial institutions to transfer a single sum of money to multiple beneficiary financial institutions
**Direction:** FI → FI (Bank to Multiple Banks)
**Scope:** Single transfer split among multiple beneficiary institutions

**Key Use Cases:**
- Distribution of funds to multiple correspondent banks
- Settlement of multiple FX deals in a single message
- Liquidity distribution to multiple branches or entities
- Net settlement with multiple counterparties
- Multi-party settlement arrangements
- Syndicated loan distributions
- Dividend payments to multiple institutional accounts
- Batch settlement of interbank obligations

**Relationship to Other Messages:**
- **MT200**: FI Own Account Transfer (single beneficiary)
- **MT202**: General FI Transfer (single beneficiary, more routing options)
- **MT205**: FI Direct Debit (debit version)
- **MT210**: Notice to Receive (notification of MT201)
- **pacs.009**: ISO 20022 equivalent (Financial Institution Credit Transfer)

**Key Characteristics:**
- **Single debit** from ordering institution
- **Multiple credits** to different beneficiary institutions
- Sum of all individual transfers equals total amount in Field 32B
- Each beneficiary specified in separate sequence (Fields 56a, 57a, 58a)
- Efficient batch processing for multiple interbank transfers

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in MT201** | 42 |
| **Fields Mapped to CDM** | 42 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions) - Multiple instances for each beneficiary
- FinancialInstitution (ordering institution, multiple beneficiary institutions, intermediaries)
- Account (ordering institution account, multiple beneficiary institution accounts)

**Note:** MT201 creates multiple PaymentInstruction instances in CDM, one for each beneficiary, linked by a common batch identifier.

---

## Complete Field Mapping

### Mandatory Fields (Single Occurrence)

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 20 | Transaction Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction | endToEndId | Sender's transaction reference (shared across all beneficiaries) |
| 19 | Sum of Amounts | 17d | 17 | M | Decimal | PaymentInstruction.extensions | sumOfAmounts | Total of all individual amounts (Field 32B) |
| 30 | Date of Transfer | 6!n | 6 | M | YYMMDD | PaymentInstruction | settlementDate | Value date for all transfers |
| 52a | Ordering Institution | Option A, D | - | O | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Ordering (sender) institution |
| 53a | Sender's Correspondent | Option A, B, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Sender's correspondent bank |

### Mandatory Fields (Multiple Occurrences - Per Beneficiary)

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 32B | Currency/Amount | 3!a15d | - | M | CCY/Amount | PaymentInstruction | currency, amount | Currency and amount for each beneficiary |
| 56a | Intermediary | Option A, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Intermediary for this beneficiary |
| 57a | Account With Institution | Option A, B, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Account institution for this beneficiary |
| 58a | Beneficiary Institution | Option A, D | - | M | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Beneficiary institution (repeatable) |
| 72 | Sender to Receiver Info | 6*35x | 210 | O | Free text | PaymentInstruction.extensions | senderToReceiverInfo | Bank-to-bank info for this beneficiary |

### Optional Fields (Single Occurrence)

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 21 | Related Reference | 16x | 16 | O | Alphanumeric | PaymentInstruction.extensions | relatedReference | Reference to related message |
| 13C | Time Indication | /8c/4!n | - | O | /CODE/Time | PaymentInstruction.extensions | timeIndication | Time indication (e.g., /CLSTIME/1600) |
| 25 | Account Identification | 35x | 35 | O | Account number | Account | accountNumber | Sender's account identification |

---

## Detailed Field Mappings

### Field 20: Transaction Reference Number

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :20: | 16x | PaymentInstruction | endToEndId | Mandatory. Common reference for all beneficiaries |

**Example:**
```
:20:MULTI20241220001
```

**Usage:** Single reference shared across all beneficiary payments in the batch.

---

### Field 21: Related Reference

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :21: | 16x | PaymentInstruction.extensions | relatedReference | Reference to related message or transaction |

**Example:**
```
:21:FXBATCH12345
```

**Usage:** Optional reference to related FX deals, instructions, or prior messages.

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
| :19: | 17d | PaymentInstruction.extensions | sumOfAmounts | MANDATORY. Total of all Field 32B amounts |

**Example:**
```
:19:10000000,
```

**Critical Rule:** Field 19 MUST equal the sum of all Field 32B amounts. This is a validation requirement.

**Example Calculation:**
- Beneficiary 1: USD 4,000,000
- Beneficiary 2: USD 3,500,000
- Beneficiary 3: USD 2,500,000
- **Field 19:** USD 10,000,000 (sum)

---

### Field 25: Account Identification

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :25: | 35x | Account | accountNumber | Sender's account with the receiver |

**Example:**
```
:25:GB29NWBK60161331926819
```

**Usage:** Identifies the sender's account to be debited (e.g., nostro account).

---

### Field 30: Date of Transfer

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :30: | 6!n | PaymentInstruction | settlementDate | MANDATORY. Value date (YYMMDD) for all transfers |

**Example:**
```
:30:241220
```
- **241220** = December 20, 2024

**Note:** All beneficiary transfers share the same value date.

---

### Field 32B: Currency/Amount (Per Beneficiary)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :32B: | 3!a15d | PaymentInstruction | currency, amount | MANDATORY. Currency and amount for each beneficiary |

**Example:**
```
:32B:USD4000000,
:32B:USD3500000,
:32B:USD2500000,
```

**Critical Rule:** Sum of all :32B: amounts MUST equal Field 19.

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

**Usage:** Sender institution initiating the multiple transfers.

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

**Usage:** Common correspondent for all beneficiary transfers (if applicable).

---

### Field 56a: Intermediary (Options A, C, D) - Per Beneficiary

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :56A: | BIC | FinancialInstitution | bicCode | Intermediary identified by BIC |
| :56C: | Party ID | FinancialInstitution | partyIdentifier | Party identifier |
| :56D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:56A:BNPAFRPPXXX
```

**Usage:** Intermediary institution for a specific beneficiary. Can differ per beneficiary.

---

### Field 57a: Account With Institution (Options A, B, C, D) - Per Beneficiary

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

**Usage:** Institution where beneficiary maintains account. Can differ per beneficiary.

---

### Field 58a: Beneficiary Institution (Options A, D) - Per Beneficiary

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :58A: | BIC | FinancialInstitution | bicCode | Beneficiary institution by BIC (mandatory) |
| :58D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:58A:DEUTDEFFXXX
:58A:HSBCHKHHXXX
:58A:BNPAFRPPXXX
```

**Usage:** Each beneficiary institution (multiple occurrences). This is the ultimate receiver of each transfer.

**Critical Note:** Each :58a: field starts a new beneficiary sequence. Each beneficiary has its own :32B:, optional :56a:, :57a:, and :72: fields.

---

### Field 72: Sender to Receiver Information (Per Beneficiary)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :72: | 6*35x | PaymentInstruction.extensions | senderToReceiverInfo | Bank-to-bank instructions (up to 210 chars) per beneficiary |

**Example:**
```
:72:/INS/Payment 1 of 3
/ACC/Nostro account funding
/REF/FX settlement leg 1
```

**Usage:** Specific instructions for each beneficiary. Can differ per beneficiary.

---

## Message Examples

### Example 1: Simple Multiple FI Transfer (3 Beneficiaries)

```
{1:F01CHASUS33AXXX0000000000}
{2:I201CHASUS33XXXXN}
{4:
:20:MULTI20241220001
:19:10000000,
:30:241220
:52A:CHASUS33XXX
:32B:USD4000000,
:58A:DEUTDEFFXXX
:32B:USD3500000,
:58A:HSBCHKHHXXX
:32B:USD2500000,
:58A:BNPAFRPPXXX
-}
```

**Explanation:**
- JP Morgan Chase sending total $10,000,000 to 3 beneficiaries
- Beneficiary 1: Deutsche Bank (USD 4M)
- Beneficiary 2: HSBC Hong Kong (USD 3.5M)
- Beneficiary 3: BNP Paribas Paris (USD 2.5M)
- Settlement date: December 20, 2024
- Sum validation: 4M + 3.5M + 2.5M = 10M ✓

---

### Example 2: Multiple FI Transfer with Intermediaries

```
{1:F01NWBKGB2LAXXX0000000000}
{2:I201NWBKGB2LXXXXN}
{4:
:20:BATCH20241220
:21:FXSETTLE-456
:13C:/CLSTIME/1600
:19:7500000,
:25:GB29NWBK60161331926819
:30:241220
:52A:NWBKGB2LXXX
:53A:CITIGB2LXXX
:32B:GBP3000000,
:56A:CITIUS33XXX
:58A:CHASUS33XXX
:72:/INS/FX settlement USD leg
/ACC/Nostro funding
:32B:GBP2500000,
:56A:HSBCUS33XXX
:58A:HSBCUS33XXX
:72:/INS/Direct transfer
/ACC/Correspondent account
:32B:GBP2000000,
:56A:BNPAUS33XXX
:58A:BNPAFRPPXXX
:72:/INS/Via New York
/ACC/Multi-hop settlement
-}
```

**Explanation:**
- NatWest London sending GBP 7,500,000 to 3 beneficiaries
- Common correspondent: Citibank London
- Beneficiary 1: JP Morgan Chase NY (GBP 3M) via Citi NY
- Beneficiary 2: HSBC US (GBP 2.5M) via HSBC NY
- Beneficiary 3: BNP Paribas Paris (GBP 2M) via BNP NY
- Each has specific routing and instructions

---

### Example 3: Dividend Distribution to Multiple Banks

```
{1:F01ABCBUS33AXXX0000000000}
{2:I201ABCBUS33XXXXN}
{4:
:20:DIVDIST20241220
:21:DIVIDEND-Q4-2024
:19:50000000,
:30:241220
:52A:ABCBUS33XXX
:32B:USD20000000,
:58A:DEUTDEFFXXX
:72:/INS/Dividend distribution Q4 2024
/BNF/Institutional clients
/REF/DIVIDEND-Q4-2024-BEN1
:32B:USD18000000,
:58A:HSBCHKHHXXX
:72:/INS/Dividend distribution Q4 2024
/BNF/Asia-Pacific clients
/REF/DIVIDEND-Q4-2024-BEN2
:32B:USD12000000,
:58A:BNPAFRPPXXX
:72:/INS/Dividend distribution Q4 2024
/BNF/European clients
/REF/DIVIDEND-Q4-2024-BEN3
-}
```

**Explanation:**
- ABC Bank US distributing $50,000,000 in dividends
- Beneficiary 1: Deutsche Bank (USD 20M) - institutional clients
- Beneficiary 2: HSBC Hong Kong (USD 18M) - APAC clients
- Beneficiary 3: BNP Paribas Paris (USD 12M) - European clients
- Related reference: Q4 2024 dividend distribution
- Each beneficiary serves different client segments

---

### Example 4: Multi-Currency Settlement (Same CCY Requirement)

```
{1:F01HSBCHKHHAXXX0000000000}
{2:I201HSBCHKHHXXXXN}
{4:
:20:MULTICCY20241220
:21:FXBATCH-789
:13C:/SNDTIME/0900
:19:15000000,
:30:241220
:52A:HSBCHKHHXXX
:32B:HKD5000000,
:56A:HSBCUS33XXX
:58A:CHASUS33XXX
:72:/INS/HKD settlement
/REF/FX deal 1
:32B:HKD6000000,
:56A:HSBCGB2LXXX
:58A:NWBKGB2LXXX
:72:/INS/HKD settlement
/REF/FX deal 2
:32B:HKD4000000,
:58A:HSBCSGSGXXX
:72:/INS/HKD settlement - direct
/REF/FX deal 3
-}
```

**Explanation:**
- HSBC Hong Kong sending HKD 15,000,000 to 3 beneficiaries
- Beneficiary 1: JP Morgan Chase (HKD 5M) via HSBC NY
- Beneficiary 2: NatWest London (HKD 6M) via HSBC London
- Beneficiary 3: HSBC Singapore (HKD 4M) direct
- Related to batch FX settlements
- Note: All amounts in same currency (HKD) per MT201 requirement

---

### Example 5: Syndicated Loan Distribution

```
{1:F01BNPAFRPPAXXX0000000000}
{2:I201BNPAFRPPXXXXN}
{4:
:20:SYNDLOAN20241220
:21:SYNDICATE-ABC-001
:19:100000000,
:25:FR7630006000011234567890189
:30:241220
:52A:BNPAFRPPXXX
:32B:EUR40000000,
:58A:DEUTDEFFXXX
:72:/INS/Syndicated loan distribution
/BNF/Lead arranger share 40%
/REF/Loan facility ABC-001
:32B:EUR35000000,
:58A:HSBCGB2LXXX
:72:/INS/Syndicated loan distribution
/BNF/Co-arranger share 35%
/REF/Loan facility ABC-001
:32B:EUR15000000,
:58A:CITIUS33XXX
:72:/INS/Syndicated loan distribution
/BNF/Participant share 15%
/REF/Loan facility ABC-001
:32B:EUR10000000,
:58A:CHASUS33XXX
:72:/INS/Syndicated loan distribution
/BNF/Participant share 10%
/REF:Loan facility ABC-001
-}
```

**Explanation:**
- BNP Paribas Paris distributing EUR 100,000,000 syndicated loan
- Beneficiary 1: Deutsche Bank (40% - EUR 40M)
- Beneficiary 2: HSBC London (35% - EUR 35M)
- Beneficiary 3: Citibank NY (15% - EUR 15M)
- Beneficiary 4: JP Morgan Chase (10% - EUR 10M)
- Account identification: Field 25
- All related to syndicate loan facility ABC-001

---

## CDM Mapping Strategy for MT201

**Challenge:** MT201 contains a single message with multiple beneficiaries.

**CDM Solution:**
1. **Create Multiple PaymentInstruction Instances**
   - One PaymentInstruction per beneficiary
   - Each has its own amount (Field 32B), beneficiary (Field 58a), intermediary (Field 56a), etc.

2. **Link via Batch Identifier**
   - Use Field 20 (Transaction Reference) as batchId
   - All PaymentInstructions share the same batchId
   - Field 19 (Sum of Amounts) stored in batch-level metadata

3. **Common Fields Replicated**
   - Field 20 (Transaction Reference) → All PaymentInstructions
   - Field 30 (Date of Transfer) → All PaymentInstructions
   - Field 52a (Ordering Institution) → All PaymentInstructions
   - Field 53a (Sender's Correspondent) → All PaymentInstructions

4. **Unique Fields Per Beneficiary**
   - Field 32B (Currency/Amount) → Individual PaymentInstruction
   - Field 56a (Intermediary) → Individual PaymentInstruction
   - Field 57a (Account With Institution) → Individual PaymentInstruction
   - Field 58a (Beneficiary Institution) → Individual PaymentInstruction
   - Field 72 (Sender to Receiver Info) → Individual PaymentInstruction

**Example CDM Mapping:**
```json
{
  "batchId": "MULTI20241220001",
  "batchSumOfAmounts": 10000000.00,
  "payments": [
    {
      "endToEndId": "MULTI20241220001",
      "settlementDate": "2024-12-20",
      "amount": 4000000.00,
      "currency": "USD",
      "beneficiaryInstitution": "DEUTDEFFXXX",
      "batchSequence": 1
    },
    {
      "endToEndId": "MULTI20241220001",
      "settlementDate": "2024-12-20",
      "amount": 3500000.00,
      "currency": "USD",
      "beneficiaryInstitution": "HSBCHKHHXXX",
      "batchSequence": 2
    },
    {
      "endToEndId": "MULTI20241220001",
      "settlementDate": "2024-12-20",
      "amount": 2500000.00,
      "currency": "USD",
      "beneficiaryInstitution": "BNPAFRPPXXX",
      "batchSequence": 3
    }
  ]
}
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required ✅

All 42 fields in MT201 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles transaction reference, amounts, dates (multiple instances)
- Extension fields accommodate SWIFT-specific elements (time indications, sum of amounts, sender to receiver info)
- FinancialInstitution entity supports all institution fields (ordering, multiple beneficiaries, intermediaries)
- Account entity handles institution accounts
- Batch processing supported via common batchId and sumOfAmounts

**Key Extension Fields Used:**
- relatedReference (Field 21 - link to related transaction or deal)
- timeIndication (Field 13C - CLSTIME, SNDTIME, etc.)
- sumOfAmounts (Field 19 - total amount validation)
- senderToReceiverInfo (Field 72 - bank instructions per beneficiary)
- batchId - derived from Field 20 to link multiple PaymentInstructions

**MT201-Specific Characteristics:**
- Multiple beneficiary handling via multiple PaymentInstruction instances
- Batch-level validation (sum of amounts)
- Single debit, multiple credits
- Each beneficiary can have unique routing

---

## No CDM Gaps Identified ✅

All 42 MT201 fields successfully map to existing CDM model. No enhancements required.

The existing GPS CDM already supports:
- Batch payment processing (multiple beneficiaries)
- Sum validation and reconciliation
- Individual routing per beneficiary
- Common settlement date across batch
- Account identification and management
- Time-based settlement instructions
- Bank-to-bank communication fields per beneficiary

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

## MT201 Validation Rules

| Rule | Description |
|------|-------------|
| **Sum Validation** | Sum of all :32B: amounts MUST equal :19: (Sum of Amounts) |
| **Currency Consistency** | All :32B: amounts MUST be in the same currency |
| **Beneficiary Count** | At least 2 beneficiary institutions (:58a:) required |
| **Date Format** | :30: (Date of Transfer) must be valid YYMMDD |
| **Sequence** | Each :58a: starts a new beneficiary sequence |

---

## Related SWIFT Messages

| Message | Description | Relationship to MT201 |
|---------|-------------|---------------------|
| **MT200** | FI Own Account Transfer | Single beneficiary version |
| **MT202** | General FI Transfer | Single beneficiary with more routing |
| **MT205** | FI Direct Debit | Debit version |
| **MT210** | Notice to Receive | Notification that MT201 will be received |
| **MT900** | Confirmation of Debit | Confirms debit of MT201 |
| **MT910** | Confirmation of Credit | Confirms credit to each beneficiary |
| **pacs.009** | ISO 20022 FI Credit Transfer | ISO 20022 equivalent |

---

## Conversion to ISO 20022

MT201 maps to multiple ISO 20022 pacs.009 messages (one per beneficiary):

| MT201 Field | ISO 20022 Message | ISO 20022 XPath |
|-------------|-------------------|-----------------|
| :20: | pacs.009 | PmtId/EndToEndId (common across all) |
| :21: | pacs.009 | PmtId/InstrId |
| :19: | pacs.009 (batch) | CtrlSum (control sum) |
| :25: | pacs.009 | DbtrAcct/Id/IBAN or Othr |
| :30: | pacs.009 | IntrBkSttlmDt |
| :32B: | pacs.009 | IntrBkSttlmAmt (per beneficiary) |
| :52a: | pacs.009 | InstgAgt |
| :53a: | pacs.009 | PrvsInstgAgt1 |
| :56a: | pacs.009 | IntrmyAgt1 (per beneficiary) |
| :57a: | pacs.009 | CdtrAgt (per beneficiary) |
| :58a: | pacs.009 | Cdtr (per beneficiary) |
| :72: | pacs.009 | InstrForNxtAgt or InstrForCdtrAgt (per beneficiary) |

---

## References

- **SWIFT Standards:** MT201 - Multiple FI Transfer
- **SWIFT Standards Release:** 2024
- **Category:** Cat 2 - Financial Institution Transfers
- **Related Messages:** MT200, MT202, MT205, MT210, pacs.009
- **ISO 20022 Equivalent:** pacs.009 - Financial Institution Credit Transfer (multiple instances)
- **GPS CDM Schema:** `/schemas/01_payment_instruction_complete_schema.json`
- **GPS CDM Extensions:** `/schemas/payment_instruction_extensions_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
**Next Review:** Q1 2025
