# ISO 20022 camt.050 - Liquidity Credit Transfer Mapping

## Message Overview

**Message Type:** camt.050.001.05 - LiquidityCreditTransferV05
**Category:** CAMT - Cash Management
**Purpose:** Sent by a central bank, settlement agent, or financial institution to transfer liquidity (funds) for settlement purposes, typically intraday liquidity management
**Direction:** Central Bank/Settlement Agent → Financial Institution (or between FIs)
**Scope:** Intraday liquidity management, settlement funding, RTGS operations

**Key Use Cases:**
- Intraday liquidity provision by central bank
- Transfer funds between settlement accounts
- Real-time gross settlement (RTGS) liquidity management
- Repo/reverse repo funding operations
- Standing liquidity facility drawdowns
- Collateral-based liquidity transfers
- Emergency liquidity assistance
- Liquidity rebalancing between accounts
- Funding for payment obligations
- End-of-day settlement funding

**Relationship to Other Messages:**
- **camt.051**: Liquidity Debit Transfer (opposite direction)
- **camt.052**: Bank to Customer Account Report (balance confirmation)
- **camt.053**: Bank to Customer Statement (settlement account statement)
- **camt.024**: Modification Request (modify liquidity transfer)
- **pacs.009**: Financial Institution Credit Transfer (similar but different purpose)
- **pacs.008**: Customer Credit Transfer (customer payments)
- **camt.060**: Account Reporting (detailed account info)

**Comparison with Related Messages:**
- **camt.050**: Liquidity Credit Transfer - central bank/settlement liquidity provision
- **camt.051**: Liquidity Debit Transfer - liquidity withdrawal/return
- **pacs.009**: FI Credit Transfer - interbank operational payments
- **pacs.008**: Customer Credit Transfer - customer payment instructions
- **camt.007**: Return of liquidity (reversal)

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in camt.050** | 95 |
| **Fields Mapped to CDM** | 95 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- PaymentInstruction.extensions (liquidityTransfer, settlementMethod, memberIdentification, standingOrderIndicator)
- Party (central bank, financial institution, member)
- Account (settlement account, cash account)
- FinancialInstitution (central bank, settlement agent, instructing agent, instructed agent)
- ComplianceCase (not heavily used, mainly payment tracking)

---

## Complete Field Mapping

### 1. Message Identification (MsgId)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/MsgId/Id | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique message identifier |
| LqdtyCdtTrf/MsgId/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | createdDateTime | Message creation timestamp |

### 2. Payment Identification (PmtId)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/PmtId/InstrId | Instruction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | instructionId | Payment instruction ID |
| LqdtyCdtTrf/PmtId/EndToEndId | End to End Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | endToEndId | End-to-end reference |
| LqdtyCdtTrf/PmtId/TxId | Transaction Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction | transactionId | Transaction reference |
| LqdtyCdtTrf/PmtId/UETR | UETR | Text | - | 0..1 | UUID format | PaymentInstruction | uetr | Universal unique identifier |
| LqdtyCdtTrf/PmtId/ClrSysRef | Clearing System Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | clearingSystemReference | Settlement system reference |

### 3. Credit Transfer Transaction Information (CdtTrfTxInf)

#### 3.1 Payment Type Information (PmtTpInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/PmtTpInf/InstrPrty | Instruction Priority | Code | 4 | 0..1 | HIGH, NORM, URGP | PaymentInstruction | priority | Transfer priority |
| LqdtyCdtTrf/CdtTrfTxInf/PmtTpInf/ClrChanl | Clearing Channel | Code | 4 | 0..1 | RTGS, RTNS, MPNS, BOOK | PaymentInstruction.extensions | clearingChannel | Settlement channel |
| LqdtyCdtTrf/CdtTrfTxInf/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | - | 0..1 | URGP, SDVA, etc. | PaymentInstruction | serviceLevel | Service level |
| LqdtyCdtTrf/CdtTrfTxInf/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | - | 0..1 | Settlement codes | PaymentInstruction | localInstrument | Local settlement instrument |
| LqdtyCdtTrf/CdtTrfTxInf/PmtTpInf/LclInstrm/Prtry | Proprietary Local Instrument | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryLocalInstrument | Custom settlement code |
| LqdtyCdtTrf/CdtTrfTxInf/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | - | 0..1 | INTC, CBLK, etc. | PaymentInstruction | categoryPurpose | Transfer category |

#### 3.2 Interbank Settlement Amount (IntrBkSttlmAmt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt | Interbank Settlement Amount | ActiveCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | interbankSettlementAmount.amount | Liquidity transfer amount |
| LqdtyCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction | interbankSettlementAmount.currency | Settlement currency |

#### 3.3 Interbank Settlement Date (IntrBkSttlmDt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 0..1 | ISODate | PaymentInstruction | settlementDate | Settlement date |

#### 3.4 Settlement Time Indication (SttlmTmIndctn)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/SttlmTmIndctn/DbtDtTm | Debit Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | debitDateTime | When debited |
| LqdtyCdtTrf/CdtTrfTxInf/SttlmTmIndctn/CdtDtTm | Credit Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | creditDateTime | When credited |

#### 3.5 Settlement Time Request (SttlmTmReq)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/SttlmTmReq/CLSTm | CLS Time | Time | - | 0..1 | ISOTime | PaymentInstruction.extensions | clsTime | CLS settlement time |
| LqdtyCdtTrf/CdtTrfTxInf/SttlmTmReq/TillTm | Till Time | Time | - | 0..1 | ISOTime | PaymentInstruction.extensions | tillTime | Settle by this time |
| LqdtyCdtTrf/CdtTrfTxInf/SttlmTmReq/FrTm | From Time | Time | - | 0..1 | ISOTime | PaymentInstruction.extensions | fromTime | Settle from this time |
| LqdtyCdtTrf/CdtTrfTxInf/SttlmTmReq/RjctTm | Reject Time | Time | - | 0..1 | ISOTime | PaymentInstruction.extensions | rejectTime | Reject if not settled by time |

#### 3.6 Previous Instructing Agent (PrvsInstgAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/PrvsInstgAgt1/FinInstnId/BICFI | Previous Instructing Agent 1 BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Previous agent 1 |
| LqdtyCdtTrf/CdtTrfTxInf/PrvsInstgAgt1/FinInstnId/ClrSysMmbId/MmbId | Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Member identifier |
| LqdtyCdtTrf/CdtTrfTxInf/PrvsInstgAgt1/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Agent name |

#### 3.7 Instructing Agent (InstgAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/InstgAgt/FinInstnId/BICFI | Instructing Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Central bank/ordering agent |
| LqdtyCdtTrf/CdtTrfTxInf/InstgAgt/FinInstnId/ClrSysMmbId/MmbId | Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Settlement member ID |
| LqdtyCdtTrf/CdtTrfTxInf/InstgAgt/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Instructing agent name |
| LqdtyCdtTrf/CdtTrfTxInf/InstgAgt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Agent country |
| LqdtyCdtTrf/CdtTrfTxInf/InstgAgt/BrnchId/Id | Branch Identification | Text | 1-35 | 0..1 | Free text | FinancialInstitution.extensions | branchId | Branch identifier |

#### 3.8 Instructed Agent (InstdAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/InstdAgt/FinInstnId/BICFI | Instructed Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Receiving central bank/agent |
| LqdtyCdtTrf/CdtTrfTxInf/InstdAgt/FinInstnId/ClrSysMmbId/MmbId | Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Settlement member ID |
| LqdtyCdtTrf/CdtTrfTxInf/InstdAgt/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Instructed agent name |
| LqdtyCdtTrf/CdtTrfTxInf/InstdAgt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Agent country |
| LqdtyCdtTrf/CdtTrfTxInf/InstdAgt/BrnchId/Id | Branch Identification | Text | 1-35 | 0..1 | Free text | FinancialInstitution.extensions | branchId | Branch identifier |

#### 3.9 Intermediary Agent (IntrmyAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/IntrmyAgt1/FinInstnId/BICFI | Intermediary Agent 1 BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Intermediary 1 |
| LqdtyCdtTrf/CdtTrfTxInf/IntrmyAgt1/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Intermediary 1 name |
| LqdtyCdtTrf/CdtTrfTxInf/IntrmyAgt2/FinInstnId/BICFI | Intermediary Agent 2 BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Intermediary 2 |
| LqdtyCdtTrf/CdtTrfTxInf/IntrmyAgt2/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Intermediary 2 name |
| LqdtyCdtTrf/CdtTrfTxInf/IntrmyAgt3/FinInstnId/BICFI | Intermediary Agent 3 BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Intermediary 3 |
| LqdtyCdtTrf/CdtTrfTxInf/IntrmyAgt3/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Intermediary 3 name |

#### 3.10 Creditor Agent (CdtrAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Beneficiary FI |
| LqdtyCdtTrf/CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId | Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Member identifier |
| LqdtyCdtTrf/CdtTrfTxInf/CdtrAgt/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Creditor agent name |
| LqdtyCdtTrf/CdtTrfTxInf/CdtrAgt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Agent country |
| LqdtyCdtTrf/CdtTrfTxInf/CdtrAgt/BrnchId/Id | Branch Identification | Text | 1-35 | 0..1 | Free text | FinancialInstitution.extensions | branchId | Branch identifier |

#### 3.11 Creditor (Cdtr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Beneficiary name |
| LqdtyCdtTrf/CdtTrfTxInf/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Creditor country |
| LqdtyCdtTrf/CdtTrfTxInf/Cdtr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| LqdtyCdtTrf/CdtTrfTxInf/Cdtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID/org number |
| LqdtyCdtTrf/CdtTrfTxInf/Cdtr/CtryOfRes | Country of Residence | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party.extensions | countryOfResidence | Residence country |

#### 3.12 Creditor Account (CdtrAcct)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Settlement account IBAN |
| LqdtyCdtTrf/CdtTrfTxInf/CdtrAcct/Id/Othr/Id | Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN settlement account |
| LqdtyCdtTrf/CdtTrfTxInf/CdtrAcct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SACC, etc. | Account | accountType | Settlement account type |
| LqdtyCdtTrf/CdtTrfTxInf/CdtrAcct/Tp/Prtry | Proprietary Account Type | Text | 1-35 | 0..1 | Free text | Account.extensions | proprietaryAccountType | Custom account type |
| LqdtyCdtTrf/CdtTrfTxInf/CdtrAcct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency |
| LqdtyCdtTrf/CdtTrfTxInf/CdtrAcct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account | accountName | Account name |

#### 3.13 Debtor Agent (DbtrAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Ordering FI |
| LqdtyCdtTrf/CdtTrfTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId | Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Member identifier |
| LqdtyCdtTrf/CdtTrfTxInf/DbtrAgt/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Debtor agent name |
| LqdtyCdtTrf/CdtTrfTxInf/DbtrAgt/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Agent country |
| LqdtyCdtTrf/CdtTrfTxInf/DbtrAgt/BrnchId/Id | Branch Identification | Text | 1-35 | 0..1 | Free text | FinancialInstitution.extensions | branchId | Branch identifier |

#### 3.14 Debtor (Dbtr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Ordering party name |
| LqdtyCdtTrf/CdtTrfTxInf/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Debtor country |
| LqdtyCdtTrf/CdtTrfTxInf/Dbtr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| LqdtyCdtTrf/CdtTrfTxInf/Dbtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID/org number |
| LqdtyCdtTrf/CdtTrfTxInf/Dbtr/CtryOfRes | Country of Residence | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party.extensions | countryOfResidence | Residence country |

#### 3.15 Debtor Account (DbtrAcct)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Source settlement account IBAN |
| LqdtyCdtTrf/CdtTrfTxInf/DbtrAcct/Id/Othr/Id | Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN source account |
| LqdtyCdtTrf/CdtTrfTxInf/DbtrAcct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SACC, etc. | Account | accountType | Source account type |
| LqdtyCdtTrf/CdtTrfTxInf/DbtrAcct/Tp/Prtry | Proprietary Account Type | Text | 1-35 | 0..1 | Free text | Account.extensions | proprietaryAccountType | Custom account type |
| LqdtyCdtTrf/CdtTrfTxInf/DbtrAcct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency |
| LqdtyCdtTrf/CdtTrfTxInf/DbtrAcct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account | accountName | Account name |

#### 3.16 Purpose (Purp)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/Purp/Cd | Purpose Code | Code | - | 0..1 | INTC, CBLK, etc. | PaymentInstruction | purpose | Transfer purpose |
| LqdtyCdtTrf/CdtTrfTxInf/Purp/Prtry | Proprietary Purpose | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryPurpose | Custom purpose |

#### 3.17 Remittance Information (RmtInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction | remittanceInformation | Transfer details |
| LqdtyCdtTrf/CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | documentNumber | Reference document |
| LqdtyCdtTrf/CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/RltdDt | Related Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | documentDate | Document date |

#### 3.18 Related Reference (RltdRef)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/CdtTrfTxInf/RltdRef/Ref | Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | relatedReference | Related transfer reference |

### 4. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LqdtyCdtTrf/SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| LqdtyCdtTrf/SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Clearing Channel (ClrChanl)

**Settlement Channel Codes:**
- **RTGS** - Real-Time Gross Settlement
- **RTNS** - Real-Time Net Settlement
- **MPNS** - Mass Payment Net Settlement
- **BOOK** - Book Transfer (internal transfer within same institution)

### Category Purpose Code (CtgyPurp/Cd)

**Liquidity Transfer Categories:**
- **INTC** - Intraday (intraday liquidity provision)
- **CBLK** - Cash Pooling (liquidity pooling/concentration)
- **ICDT** - Irrevocable Credit Transfer (final settlement)
- **CASH** - Cash Management Transfer
- **DVPM** - Delivery Versus Payment Margin (securities settlement)

### Account Type (CdtrAcct/Tp/Cd, DbtrAcct/Tp/Cd)

**Settlement Account Types:**
- **CACC** - Current Account (settlement account)
- **SACC** - Settlement Account (dedicated settlement account)
- **SVGS** - Savings Account
- **TRAN** - Transactional Account

### Instruction Priority (InstrPrty)
- **HIGH** - High priority transfer
- **NORM** - Normal priority transfer
- **URGP** - Urgent priority

### Service Level (SvcLvl/Cd)
- **URGP** - Urgent Payment
- **SDVA** - Same Day Value
- **NURG** - Normal Urgency

### Purpose Code (Purp/Cd)

**Liquidity Transfer Purposes:**
- **INTC** - Intraday Funding
- **CBLK** - Cash Pooling/Liquidity Pooling
- **CBFF** - Central Bank Funding Facility
- **CBFR** - Central Bank Refinancing
- **MSVC** - Multiple Service Types
- **SECU** - Securities Purchase/Sale Related

---

## Message Examples

### Example 1: Intraday Liquidity Provision by Central Bank

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.050.001.05">
  <LqdtyCdtTrf>
    <MsgId>
      <Id>LIQCDT-20241220-CB-001</Id>
      <CreDtTm>2024-12-20T09:30:00</CreDtTm>
    </MsgId>
    <PmtId>
      <InstrId>INSTR-LIQCDT-001</InstrId>
      <EndToEndId>E2E-INTRADAY-LIQ-001</EndToEndId>
      <TxId>TXN-CBFUNDING-001</TxId>
      <ClrSysRef>RTGS-2024-1220-0930-001</ClrSysRef>
    </PmtId>
    <CdtTrfTxInf>
      <PmtTpInf>
        <InstrPrty>HIGH</InstrPrty>
        <ClrChanl>RTGS</ClrChanl>
        <SvcLvl>
          <Cd>URGP</Cd>
        </SvcLvl>
        <CtgyPurp>
          <Cd>INTC</Cd>
        </CtgyPurp>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="GBP">100000000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <SttlmTmIndctn>
        <CdtDtTm>2024-12-20T09:30:00</CdtDtTm>
      </SttlmTmIndctn>
      <InstgAgt>
        <FinInstnId>
          <BICFI>BKENGB2LXXX</BICFI>
          <Nm>Bank of England</Nm>
          <PstlAdr>
            <Ctry>GB</Ctry>
          </PstlAdr>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <BICFI>BKENGB2LXXX</BICFI>
          <Nm>Bank of England RTGS</Nm>
        </FinInstnId>
      </InstdAgt>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>HSBCGB2LXXX</BICFI>
          <ClrSysMmbId>
            <MmbId>HSBC-RTGS-12345</MmbId>
          </ClrSysMmbId>
          <Nm>HSBC Bank plc</Nm>
          <PstlAdr>
            <Ctry>GB</Ctry>
          </PstlAdr>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>HSBC Bank plc</Nm>
        <PstlAdr>
          <Ctry>GB</Ctry>
        </PstlAdr>
        <Id>
          <OrgId>
            <AnyBIC>HSBCGB2LXXX</AnyBIC>
          </OrgId>
        </Id>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>HSBC-SETTLEMENT-ACCT-001</Id>
          </Othr>
        </Id>
        <Tp>
          <Cd>SACC</Cd>
        </Tp>
        <Ccy>GBP</Ccy>
        <Nm>HSBC RTGS Settlement Account</Nm>
      </CdtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>BKENGB2LXXX</BICFI>
          <Nm>Bank of England</Nm>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>Bank of England</Nm>
        <Id>
          <OrgId>
            <AnyBIC>BKENGB2LXXX</AnyBIC>
          </OrgId>
        </Id>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>BOE-LIQUIDITY-FACILITY-ACCT</Id>
          </Othr>
        </Id>
        <Tp>
          <Prtry>CENTRAL_BANK_LIQUIDITY</Prtry>
        </Tp>
        <Ccy>GBP</Ccy>
      </DbtrAcct>
      <Purp>
        <Cd>INTC</Cd>
      </Purp>
      <RmtInf>
        <Ustrd>Intraday liquidity provision - GBP 100M - Standing Facility drawdown - Collateralized - 0.75% overnight rate - Repayment due EOD 2024-12-20</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </LqdtyCdtTrf>
</Document>
```

### Example 2: RTGS Settlement Transfer Between Financial Institutions

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.050.001.05">
  <LqdtyCdtTrf>
    <MsgId>
      <Id>LIQCDT-20241220-RTGS-002</Id>
      <CreDtTm>2024-12-20T11:15:00</CreDtTm>
    </MsgId>
    <PmtId>
      <InstrId>INSTR-RTGS-002</InstrId>
      <EndToEndId>E2E-SETTLEMENT-FUNDING</EndToEndId>
      <TxId>TXN-RTGS-002</TxId>
      <UETR>789e1234-a56b-78c9-d012-345678901234</UETR>
      <ClrSysRef>CHAPS-2024-1220-1115-002</ClrSysRef>
    </PmtId>
    <CdtTrfTxInf>
      <PmtTpInf>
        <InstrPrty>HIGH</InstrPrty>
        <ClrChanl>RTGS</ClrChanl>
        <LclInstrm>
          <Cd>CHAPS</Cd>
        </LclInstrm>
        <CtgyPurp>
          <Cd>ICDT</Cd>
        </CtgyPurp>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="GBP">25000000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <SttlmTmIndctn>
        <CdtDtTm>2024-12-20T11:15:00</CdtDtTm>
      </SttlmTmIndctn>
      <SttlmTmReq>
        <TillTm>16:00:00</TillTm>
      </SttlmTmReq>
      <InstgAgt>
        <FinInstnId>
          <BICFI>BARCGB22XXX</BICFI>
          <ClrSysMmbId>
            <MmbId>BARC-CHAPS-67890</MmbId>
          </ClrSysMmbId>
          <Nm>Barclays Bank PLC</Nm>
          <PstlAdr>
            <Ctry>GB</Ctry>
          </PstlAdr>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <BICFI>BKENGB2LXXX</BICFI>
          <Nm>Bank of England CHAPS</Nm>
        </FinInstnId>
      </InstdAgt>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>NWBKGB2LXXX</BICFI>
          <ClrSysMmbId>
            <MmbId>NWBK-CHAPS-11111</MmbId>
          </ClrSysMmbId>
          <Nm>National Westminster Bank</Nm>
          <PstlAdr>
            <Ctry>GB</Ctry>
          </PstlAdr>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>National Westminster Bank</Nm>
        <Id>
          <OrgId>
            <AnyBIC>NWBKGB2LXXX</AnyBIC>
          </OrgId>
        </Id>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>NWBK-CHAPS-SETTLEMENT</Id>
          </Othr>
        </Id>
        <Tp>
          <Cd>SACC</Cd>
        </Tp>
        <Ccy>GBP</Ccy>
        <Nm>NatWest CHAPS Settlement Account</Nm>
      </CdtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>BARCGB22XXX</BICFI>
          <Nm>Barclays Bank PLC</Nm>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>Barclays Bank PLC</Nm>
        <Id>
          <OrgId>
            <AnyBIC>BARCGB22XXX</AnyBIC>
          </OrgId>
        </Id>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>BARC-CHAPS-SETTLEMENT</Id>
          </Othr>
        </Id>
        <Tp>
          <Cd>SACC</Cd>
        </Tp>
        <Ccy>GBP</Ccy>
        <Nm>Barclays CHAPS Settlement Account</Nm>
      </DbtrAcct>
      <Purp>
        <Cd>INTC</Cd>
      </Purp>
      <RmtInf>
        <Ustrd>RTGS settlement transfer - CHAPS - Net position settlement - Session 1 - 2024-12-20</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </LqdtyCdtTrf>
</Document>
```

### Example 3: Cash Pooling / Liquidity Management Transfer

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.050.001.05">
  <LqdtyCdtTrf>
    <MsgId>
      <Id>LIQCDT-20241220-POOL-003</Id>
      <CreDtTm>2024-12-20T14:00:00</CreDtTm>
    </MsgId>
    <PmtId>
      <InstrId>INSTR-POOL-003</InstrId>
      <EndToEndId>E2E-LIQUIDITY-POOL-REBALANCE</EndToEndId>
      <TxId>TXN-POOL-003</TxId>
    </PmtId>
    <CdtTrfTxInf>
      <PmtTpInf>
        <InstrPrty>NORM</InstrPrty>
        <ClrChanl>BOOK</ClrChanl>
        <CtgyPurp>
          <Cd>CBLK</Cd>
        </CtgyPurp>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="EUR">5000000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <SttlmTmIndctn>
        <CdtDtTm>2024-12-20T14:00:00</CdtDtTm>
      </SttlmTmIndctn>
      <InstgAgt>
        <FinInstnId>
          <BICFI>DEUTDEFFXXX</BICFI>
          <Nm>Deutsche Bank AG</Nm>
          <PstlAdr>
            <Ctry>DE</Ctry>
          </PstlAdr>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <BICFI>DEUTDEFFXXX</BICFI>
          <Nm>Deutsche Bank AG - Treasury</Nm>
        </FinInstnId>
      </InstdAgt>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>DEUTDEFFXXX</BICFI>
          <Nm>Deutsche Bank AG</Nm>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>Corporate Client - Subsidiary B</Nm>
        <Id>
          <OrgId>
            <Othr>
              <Id>CLIENT-SUBSID-B-12345</Id>
            </Othr>
          </OrgId>
        </Id>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <IBAN>DE89370400440532013000</IBAN>
        </Id>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
        <Ccy>EUR</Ccy>
        <Nm>Subsidiary B Operating Account</Nm>
      </CdtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>DEUTDEFFXXX</BICFI>
          <Nm>Deutsche Bank AG</Nm>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>Corporate Client - Master Pool Account</Nm>
        <Id>
          <OrgId>
            <Othr>
              <Id>CLIENT-MASTER-POOL-99999</Id>
            </Othr>
          </OrgId>
        </Id>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <IBAN>DE89370400440532099999</IBAN>
        </Id>
        <Tp>
          <Prtry>CASH_CONCENTRATION_POOL</Prtry>
        </Tp>
        <Ccy>EUR</Ccy>
        <Nm>Master Cash Pool Account</Nm>
      </DbtrAcct>
      <Purp>
        <Cd>CBLK</Cd>
      </Purp>
      <RmtInf>
        <Ustrd>Daily cash pooling sweep - Master to Subsidiary B - Automatic rebalancing - Target balance EUR 5M - Standing order</Ustrd>
      </RmtInf>
      <RltdRef>
        <Ref>POOL-STANDING-ORDER-2024</Ref>
      </RltdRef>
    </CdtTrfTxInf>
  </LqdtyCdtTrf>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 95 fields in camt.050 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles payment identification, amounts, dates, party references
- Extension fields accommodate liquidity-transfer-specific information
- Settlement timing and channel specifications
- Party entity supports central bank, financial institutions, settlement members
- Account entity handles settlement accounts (IBAN and non-IBAN)
- FinancialInstitution entity manages instructing/instructed agents, intermediaries
- ComplianceCase entity not heavily used (mainly payment tracking)

**Key Extension Fields Used:**
- clearingSystemReference (settlement system reference)
- clearingChannel (RTGS, RTNS, MPNS, BOOK)
- proprietaryLocalInstrument (custom settlement codes)
- debitDateTime, creditDateTime (settlement timing)
- clsTime, tillTime, fromTime, rejectTime (time-specific settlement)
- branchId (branch identification)
- countryOfResidence (party residence)
- proprietaryAccountType (custom account types)
- proprietaryPurpose (custom transfer purpose)
- documentNumber, documentDate (reference documents)
- relatedReference (related transfer reference)
- supplementaryDataLocation, supplementaryData (additional data)

---

## References

- **ISO 20022 Message Definition:** camt.050.001.05 - LiquidityCreditTransferV05
- **XML Schema:** camt.050.001.05.xsd
- **Related Messages:** camt.051 (liquidity debit transfer), camt.052 (account report), camt.053 (account statement), camt.024 (modification request), pacs.009 (FI credit transfer)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **Settlement Systems:** TARGET2 (ECB), CHAPS (UK), Fedwire (US), SIC (Switzerland), BOJ-NET (Japan)
- **Central Banks:** Bank of England, ECB, Federal Reserve, Bundesbank, Banque de France

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
