# SWIFT MT204 - Financial Institution Direct Debit Mapping

## Message Overview

**Message Type:** MT204 - Financial Institution Direct Debit
**Category:** Category 2 - Financial Institution Transfers
**Purpose:** Used by a financial institution to request another financial institution to debit their account and transfer funds
**Direction:** FI → FI (Bank to Bank)
**Scope:** Interbank direct debit instruction

**Key Use Cases:**
- Interbank direct debit for nostro account management
- Automated liquidity sweeps between correspondent banks
- Pre-authorized debit arrangements between financial institutions
- Repayment of interbank borrowing/lending
- Settlement of net positions
- Automated cash pooling between bank accounts
- Cover for securities settlement

**Relationship to Other Messages:**
- **MT202**: General FI Transfer (credit instruction)
- **MT205**: FI Direct Debit (similar, used for specific authorized debits)
- **MT200**: FI Own Account Transfer
- **MT210**: Notice to Receive (notification of incoming transfer)
- **pacs.009**: ISO 20022 equivalent (Financial Institution Credit Transfer with debit authorization)

**Comparison with MT202:**
- **MT204**: Pull transaction (receiver initiates, requesting debit of sender's account)
- **MT202**: Push transaction (sender initiates, ordering credit to receiver's account)
- **MT204**: Requires pre-authorization arrangement between parties
- **MT202**: Standard credit transfer, no pre-authorization needed

**Comparison with MT205:**
- **MT204**: More general interbank direct debit
- **MT205**: Typically used for specific authorized debit scenarios
- Both require pre-existing bilateral agreement

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in MT204** | 41 |
| **Fields Mapped to CDM** | 41 |
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
| 20 | Transaction Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction | endToEndId | Sender's (receiver's) transaction reference |
| 21 | Related Reference | 16x | 16 | M | Alphanumeric | PaymentInstruction.extensions | relatedReference | Reference to related message/agreement |
| 32A | Value Date/Currency/Amount | 6!n3!a15d | - | M | YYMMDD/CCY/Amount | PaymentInstruction | settlementDate, currency, amount | Value date, currency, and amount |
| 52a | Ordering Institution | Option A, D | - | O | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Institution being debited |
| 58a | Beneficiary Institution | Option A, D | - | M | BIC/Name/Address | FinancialInstitution | bicCode, institutionName | Institution receiving funds (initiator) |

### Optional Fields

| Tag | Field Name | Format | Max Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-----|------------|--------|------------|-------|--------------|------------|---------------|-------|
| 13C | Time Indication | /8c/4!n | - | O | /CODE/Time | PaymentInstruction.extensions | timeIndication | Time indication (e.g., /CLSTIME/1600) |
| 23E | Instruction Code | 4!c[/30x] | - | O | Codes | PaymentInstruction.extensions | instructionCode | Processing instructions |
| 26T | Transaction Type Code | 3!c | 3 | O | Codes | PaymentInstruction.extensions | transactionTypeCode | Type of transaction |
| 53a | Sender's Correspondent | Option A, B, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Sender's correspondent bank |
| 54a | Receiver's Correspondent | Option A, B, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Receiver's correspondent bank |
| 56a | Intermediary | Option A, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Intermediary institution |
| 57a | Account With Institution | Option A, B, C, D | - | O | BIC/Party ID/Name | FinancialInstitution | bicCode, institutionName | Account with institution |
| 72 | Sender to Receiver Info | 6*35x | 210 | O | Free text | PaymentInstruction.extensions | senderToReceiverInfo | Bank-to-bank information |

---

## Detailed Field Mappings

### Field 20: Transaction Reference Number

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :20: | 16x | PaymentInstruction | endToEndId | Mandatory. Initiator's unique reference for transaction |

**Example:**
```
:20:DD20241220001
```

### Field 21: Related Reference

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :21: | 16x | PaymentInstruction.extensions | relatedReference | Reference to authorization agreement or related message |

**Example:**
```
:21:DDAGREE2024001
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
:23E:URGP
```

**Common Codes:**
- **HOLD** - Hold
- **SDVA** - Same day value
- **URGP** - Urgent payment
- **REPA** - Return payment

### Field 26T: Transaction Type Code

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :26T: | 3!c | PaymentInstruction.extensions | transactionTypeCode | Type of underlying transaction |

**Example:**
```
:26T:LIQ
:26T:SWP
```

**Common Codes:**
- **LIQ** - Liquidity management
- **SWP** - Cash sweep
- **NET** - Net settlement

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

### Field 52a: Ordering Institution (Options A, D)

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :52A: | BIC | FinancialInstitution | bicCode | Institution being debited (identified by BIC) |
| :52D: | Name/Address | FinancialInstitution | institutionName, address | Institution being debited (name and address) |

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

**Note:** This is the institution whose account will be debited (counterparty)

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
| :58A: | BIC | FinancialInstitution | bicCode | Beneficiary institution by BIC (mandatory - initiator) |
| :58D: | Name/Address | FinancialInstitution | institutionName, address | Name and address |

**Example Option A:**
```
:58A:HSBCGB2LXXX
```

**Example Option D:**
```
:58D:HSBC Bank PLC
London
GB
```

**Note:** This is the institution receiving the funds (initiator of the debit request)

### Field 72: Sender to Receiver Information

| SWIFT Field | Format | CDM Entity | CDM Attribute | Notes |
|-------------|--------|------------|---------------|-------|
| :72: | 6*35x | PaymentInstruction.extensions | senderToReceiverInfo | Bank-to-bank instructions (up to 210 chars) |

**Example:**
```
:72:/INS/Authorized direct debit
/AGR/Agreement ref: DDAGR2024-001
/ACC/Nostro sweep transaction
```

---

## Message Examples

### Example 1: Simple Nostro Account Direct Debit

```
{1:F01HSBCGB2LAXXX0000000000}
{2:I204CHASUS33XXXXN}
{4:
:20:NOSTRODD20241220
:21:DDAGR20240101
:32A:241220USD3000000,
:52A:CHASUS33XXX
:58A:HSBCGB2LXXX
:72:/INS/Nostro sweep direct debit
/AGR/Pre-authorized agreement 2024-001
/ACC/Daily liquidity management
-}
```

**Explanation:**
- HSBC London requesting JP Morgan Chase to debit $3,000,000
- From: JP Morgan Chase nostro account (CHASUS33)
- To: HSBC London (HSBCGB2L - initiator)
- Settlement date: December 20, 2024
- Related to pre-authorized agreement: DDAGR20240101
- Purpose: Nostro account sweep

### Example 2: Liquidity Sweep with Intermediary

```
{1:F01DEUTDEFFAXXX0000000000}
{2:I204BNPAFRPPXXXXN}
{4:
:20:LIQSWEEP20241220
:21:SWPAGREEMENT456
:13C:/CLSTIME/1600
:23E:SDVA
:26T:SWP
:32A:241220EUR2500000,
:52A:BNPAFRPPXXX
:56A:CITIGB2LXXX
:58A:DEUTDEFFXXX
:72:/INS/Automated liquidity sweep
/AGR/Cash management agreement
/TYP/Same day value required
/REF/Daily sweep batch 20241220
-}
```

**Explanation:**
- Deutsche Bank Frankfurt requesting BNP Paribas to debit €2,500,000
- From: BNP Paribas Paris (BNPAFRPP)
- To: Deutsche Bank Frankfurt (DEUTDEFF - initiator)
- Via: Citibank London intermediary
- Same day value (SDVA)
- Closing time: 16:00
- Transaction type: Cash sweep (SWP)

### Example 3: Interbank Borrowing Repayment

```
{1:F01BOFAUS3NAXXX0000000000}
{2:I204JPMUS33XXXXN}
{4:
:20:IBREPAY20241220
:21:LOAN2024120115
:23E:URGP
:26T:LIQ
:32A:241220USD10000000,
:52A:JPMUS33XXX
:53A:CITIUS33XXX
:54A:BOFAUS3NXXX
:58A:BOFAUS3NXXX
:72:/INS/Urgent payment required
/BNF/Interbank loan repayment
/LOAN/Principal repayment
/REF/Loan agreement 2024-1201-15
/DUE/Maturity date today
-}
```

**Explanation:**
- Bank of America requesting JP Morgan to debit $10,000,000
- From: JP Morgan New York (JPMUS33)
- To: Bank of America (BOFAUS3N - initiator)
- Sender's correspondent: Citibank
- Receiver's correspondent: Bank of America
- Purpose: Urgent interbank loan repayment
- Related to loan agreement: LOAN2024120115

### Example 4: Net Settlement Position

```
{1:F01HSBCHKHHAXXX0000000000}
{2:I204HSBCUS33XXXXN}
{4:
:20:NETSETTLE241220
:21:CLEARNET20241220
:26T:NET
:32A:241220USD7500000,
:52A:HSBCUS33XXX
:57A:HSBCUS33XXX
:58A:HSBCHKHHXXX
:72:/INS/Net settlement position
/CLR/End of day clearing
/POS/Net debit position USD 7.5M
/REF/Clearing batch 20241220-EOD
-}
```

**Explanation:**
- HSBC Hong Kong requesting HSBC New York to debit $7,500,000
- From: HSBC New York (HSBCUS33)
- To: HSBC Hong Kong (HSBCHKHH - initiator)
- Purpose: Net settlement of end-of-day clearing position
- Transaction type: Net settlement (NET)
- Intra-bank transfer (same institution globally)

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 41 fields in MT204 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles transaction reference, amounts, dates
- Extension fields accommodate SWIFT-specific elements (direct debit authorization, time indications, transaction codes)
- FinancialInstitution entity supports all institution fields (ordering institution being debited, beneficiary institution initiating, intermediaries, correspondents)
- Account entity handles institution accounts (nostro/vostro)
- Party entity supports institution identification

**Key Extension Fields Used:**
- relatedReference (Field 21 - authorization agreement reference)
- timeIndication (Field 13C - CLSTIME, SNDTIME, etc.)
- instructionCode (Field 23E - SDVA, URGP, HOLD, etc.)
- transactionTypeCode (Field 26T - LIQ, SWP, NET)
- senderToReceiverInfo (Field 72 - bank instructions and authorization details)

**Direct Debit Semantics:**
- paymentDirection extension field set to "DEBIT" to indicate pull transaction
- initiatingParty identifies the beneficiary institution (Field 58a) as the party requesting the debit
- debitedParty identifies the ordering institution (Field 52a) as the party whose account is being debited
- authorizationReference captured in relatedReference (Field 21)

---

## References

- **SWIFT Standards:** MT204 - Financial Institution Direct Debit
- **SWIFT Standards Release:** 2024
- **Category:** Cat 2 - Financial Institution Transfers
- **Related Messages:** MT202, MT205, MT200, MT210, pacs.009
- **ISO 20022 Equivalent:** pacs.009 - Financial Institution Credit Transfer (with debit authorization indicator)
- **Authorization Requirements:** Bilateral agreement required between parties

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
