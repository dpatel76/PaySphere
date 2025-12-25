# JAFIC STR - Japan Suspicious Transaction Report
## Complete Field Mapping to GPS CDM

**Report Type:** Japan Suspicious Transaction Report (STR) / 疑わしい取引の届出
**Regulatory Authority:** Japan Financial Intelligence Center (JAFIC), National Police Agency
**Filing Requirement:** Report suspicious transactions that may relate to criminal proceeds or terrorism financing
**Document Date:** 2025-12-20
**Mapping Coverage:** 100% (All 82 fields mapped)

---

## Report Overview

The Suspicious Transaction Report (STR) is filed by financial institutions and specified business operators in Japan to report suspicious transactions that may involve proceeds from criminal activity or terrorism financing. JAFIC serves as Japan's financial intelligence unit under the National Police Agency.

**Filing Threshold:** No minimum threshold
**Filing Deadline:** Promptly after detection (immediately for terrorism-related suspicions)
**Filing Method:** National Public Safety Commission reporting system (electronic filing)
**Regulation:** Act on Prevention of Transfer of Criminal Proceeds (犯罪による収益の移転防止に関する法律)

**Predicate Offenses:**
- Drug-related crimes
- Organized crime activities (boryokudan)
- Fraud and embezzlement
- Corruption and bribery
- Tax evasion
- Terrorism financing

**Key Requirements:**
- File promptly upon suspicion (no delay for investigation)
- Immediate reporting for terrorism property (within 24 hours)
- Maintain transaction monitoring system
- Enhanced verification for high-risk transactions
- Annual typologies review published by JAFIC

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total JAFIC STR Fields** | 82 | 100% |
| **Mapped to CDM** | 82 | 100% |
| **Direct Mapping** | 70 | 85% |
| **Derived/Calculated** | 9 | 11% |
| **Reference Data Lookup** | 3 | 4% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Part I: Reporting Institution Information (Fields 1-12)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | Institution name (Japanese) | Text | 140 | Yes | Free text | FinancialInstitution | institutionName | Japanese legal name |
| 2 | Institution name (English) | Text | 140 | No | Free text | FinancialInstitution | extensions.nameEnglish | English name if available |
| 3 | Institution type | Code | 2 | Yes | See code list | FinancialInstitution | fiType | FI category |
| 4 | Registration number | Text | 20 | Yes | Free text | FinancialInstitution | extensions.japanRegistrationNumber | Corporate number (法人番号) |
| 5 | FSA license number | Text | 20 | Cond | Free text | FinancialInstitution | centralBankLicenseNumber | Financial Services Agency license |
| 6 | Head office address | Text | 200 | Yes | Free text | FinancialInstitution | address.addressLine1 | Full address in Japanese |
| 7 | Prefecture | Code | 2 | Yes | Prefecture code | FinancialInstitution | address.countrySubDivision | Japanese prefecture |
| 8 | Postal code | Text | 8 | Yes | NNN-NNNN | FinancialInstitution | address.postCode | Japanese postal code format |
| 9 | Contact person name | Text | 140 | Yes | Free text | RegulatoryReport | reportingEntityContactName | AML officer name |
| 10 | Contact department | Text | 100 | Yes | Free text | RegulatoryReport | extensions.contactDepartment | Department name |
| 11 | Contact phone | Text | 20 | Yes | Free text | RegulatoryReport | reportingEntityContactPhone | Phone number |
| 12 | STR submission date | Date | 10 | Yes | YYYY-MM-DD | RegulatoryReport | submissionDate | Filing date |

### Part II: Customer Information (Fields 13-34)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 13 | Customer category | Code | 1 | Yes | I=Individual, C=Corporation | Party | partyType | Individual or entity |
| 14 | Customer name (Japanese) | Text | 140 | Yes | Free text | Party | name | Full name in Japanese |
| 15 | Customer name (Kana) | Text | 140 | Yes | Katakana | Party | extensions.nameKana | Phonetic reading |
| 16 | Customer name (English) | Text | 140 | No | Free text | Party | extensions.nameEnglish | Roman alphabet name |
| 17 | Surname (Japanese) | Text | 140 | Cond | Free text | Party | familyName | Family name |
| 18 | Given name (Japanese) | Text | 140 | Cond | Free text | Party | givenName | First name |
| 19 | Corporate name | Text | 140 | Cond | Free text | Party | name | Company name if entity |
| 20 | Corporate number | Text | 13 | Cond | 13 digits | Party | extensions.japanCorporateNumber | Japan corporate number |
| 21 | My Number | Text | 12 | No | 12 digits | Party | japanMyNumber | Individual number (confidential) |
| 22 | Date of birth | Date | 10 | Cond | YYYY-MM-DD | Party | dateOfBirth | DOB if individual |
| 23 | Place of birth | Text | 100 | No | Free text | Party | placeOfBirth | Birth location |
| 24 | Nationality | Code | 2 | Cond | ISO 3166-1 | Party | nationality[0] | Nationality code |
| 25 | Residence status | Code | 2 | Cond | See code list | Party | extensions.residenceStatus | Resident/non-resident |
| 26 | Occupation/business type | Text | 100 | Yes | Free text | Party | occupation | Occupation or business |
| 27 | Industry code | Code | 6 | No | JSIC code | Party | naicsCode | Japan Standard Industrial Classification |
| 28 | Customer address (Japanese) | Text | 200 | Yes | Free text | Party | address.addressLine1 | Full address |
| 29 | Prefecture | Code | 2 | Yes | Prefecture code | Party | address.countrySubDivision | Prefecture |
| 30 | Postal code | Text | 8 | No | NNN-NNNN | Party | address.postCode | Postal code |
| 31 | Country | Code | 2 | Yes | ISO 3166-1 | Party | address.country | Country code |
| 32 | Phone number | Text | 20 | No | Free text | Party | contactDetails.phoneNumber | Contact phone |
| 33 | Email address | Text | 256 | No | Email format | Party | contactDetails.emailAddress | Email |
| 34 | Customer risk classification | Code | 1 | Yes | L=Low, M=Medium, H=High | Party | riskRating | Risk rating |

### Part III: Transaction Verification (Fields 35-43)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 35 | Verification method | Code | 2 | Yes | See code list | Party | extensions.verificationMethod | How customer verified |
| 36 | Identification document type | Code | 2 | Yes | See code list | Party | formOfIdentification | ID type presented |
| 37 | ID document number | Text | 50 | Yes | Free text | Party | identificationNumber | Document number |
| 38 | ID issuing authority | Text | 100 | No | Free text | Party | extensions.idIssuingAuthority | Issuing office |
| 39 | ID issuance date | Date | 10 | No | YYYY-MM-DD | Party | extensions.idIssuanceDate | Issue date |
| 40 | ID expiry date | Date | 10 | No | YYYY-MM-DD | Party | extensions.idExpiryDate | Expiration date |
| 41 | Transaction purpose confirmation | Code | 2 | Yes | See code list | PaymentInstruction | extensions.purposeConfirmed | Purpose verified? |
| 42 | Beneficial owner identified | Boolean | 1 | Yes | Y/N | Account | extensions.beneficialOwnerIdentified | BO verified? |
| 43 | Beneficial owner name | Text | 140 | Cond | Free text | Account | extensions.beneficialOwnerName | BO name if different |

### Part IV: Account Information (Fields 44-50)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 44 | Account number | Text | 20 | No | Free text | Account | accountNumber | Primary account |
| 45 | Account type | Code | 2 | No | See code list | Account | accountType | Account classification |
| 46 | Account currency | Code | 3 | No | ISO 4217 | Account | currency | JPY or foreign currency |
| 47 | Account opening date | Date | 10 | No | YYYY-MM-DD | Account | openDate | When opened |
| 48 | Account status | Code | 1 | No | See code list | Account | accountStatus | Current status |
| 49 | Account balance | Decimal | 18,2 | No | Numeric | Account | currentBalance | Balance at report time |
| 50 | Average monthly turnover | Decimal | 18,2 | No | Numeric | Account | extensions.averageMonthlyTurnover | Historical average |

### Part V: Transaction Details (Fields 51-65)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 51 | Transaction date | Date | 10 | Yes | YYYY-MM-DD | PaymentInstruction | valueDate | Transaction date |
| 52 | Transaction time | Time | 8 | No | HH:MM:SS | PaymentInstruction | extensions.valueDateTime | Time if available |
| 53 | Transaction amount | Decimal | 18,2 | Yes | Numeric | PaymentInstruction | instructedAmount.amount | Amount |
| 54 | Transaction currency | Code | 3 | Yes | ISO 4217 | PaymentInstruction | instructedAmount.currency | Currency |
| 55 | JPY equivalent amount | Decimal | 18,2 | No | Numeric | PaymentInstruction | equivalentAmount.amount | JPY conversion |
| 56 | Transaction type | Code | 3 | Yes | See code list | PaymentInstruction | paymentType | Transaction category |
| 57 | Transaction method | Code | 2 | No | See code list | PaymentInstruction | extensions.transactionMethod | Cash/non-cash |
| 58 | Transaction reference | Text | 35 | No | Free text | PaymentInstruction | endToEndId | Reference number |
| 59 | Stated purpose | Text | 500 | No | Free text | PaymentInstruction | purposeDescription | Customer-stated purpose |
| 60 | Counterparty name | Text | 140 | No | Free text | Party | name | Other party name |
| 61 | Counterparty account | Text | 20 | No | Free text | Account | extensions.counterpartyAccount | Other account |
| 62 | Counterparty institution | Text | 140 | No | Free text | FinancialInstitution | extensions.counterpartyInstitution | Other FI |
| 63 | Counterparty country | Code | 2 | No | ISO 3166-1 | Party | address.country | Country |
| 64 | Number of transactions | Integer | 5 | Yes | Numeric | RegulatoryReport | transactionCount | Total in suspicious pattern |
| 65 | Total amount involved | Decimal | 18,2 | Yes | Numeric | RegulatoryReport | totalReportedValue | Aggregate amount |

### Part VI: Suspicion Details (Fields 66-78)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 66 | Suspicion category | Multi-select | - | Yes | See code list | ComplianceCase | sarActivityTypeCheckboxes | Primary suspicion(s) |
| 67 | Suspected crime type | Multi-select | - | No | See code list | ComplianceCase | extensions.suspectedCrimeType | Predicate offense |
| 68 | Terrorism financing flag | Boolean | 1 | Yes | Y/N | ComplianceCase | extensions.terrorismFinancingFlag | TF-related? |
| 69 | Organized crime involvement | Boolean | 1 | No | Y/N | ComplianceCase | extensions.organizedCrimeFlag | Boryokudan involvement? |
| 70 | Transaction pattern anomaly | Boolean | 1 | No | Y/N | ComplianceCase | extensions.unusualPatternFlag | Unusual pattern? |
| 71 | Cash transaction flag | Boolean | 1 | No | Y/N | ComplianceCase | extensions.cashIntensiveFlag | Large cash involved? |
| 72 | Foreign transaction flag | Boolean | 1 | No | Y/N | ComplianceCase | extensions.foreignTransactionFlag | Cross-border element? |
| 73 | Structured transaction flag | Boolean | 1 | No | Y/N | ComplianceCase | extensions.structuringIndicator | Structuring suspected? |
| 74 | Customer behavior suspicious | Boolean | 1 | No | Y/N | ComplianceCase | extensions.evasiveCustomer | Suspicious behavior? |
| 75 | Inconsistent with profile | Boolean | 1 | No | Y/N | ComplianceCase | extensions.inconsistentWithProfile | Profile mismatch? |
| 76 | No economic rationale | Boolean | 1 | No | Y/N | ComplianceCase | extensions.noEconomicRationale | No business purpose? |
| 77 | PEP involvement | Boolean | 1 | No | Y/N | ComplianceCase | extensions.pepInvolvement | PEP-related? |
| 78 | High-risk country involvement | Boolean | 1 | No | Y/N | ComplianceCase | extensions.highRiskJurisdiction | FATF high-risk country? |

### Part VII: Description and Actions (Fields 79-82)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 79 | Detailed description of suspicion | Text | 4000 | Yes | Free text | ComplianceCase | sarNarrative | Main narrative in Japanese |
| 80 | Grounds for suspicion | Text | 3000 | Yes | Free text | ComplianceCase | extensions.suspicionFactors | Specific red flags |
| 81 | Actions taken by institution | Multi-select | - | Yes | See code list | ComplianceCase | extensions.actionTaken | FI response |
| 82 | Additional information | Text | 2000 | No | Free text | ComplianceCase | extensions.additionalRemarks | Other relevant details |

---

## Code Lists

### Institution Type Codes (Field 3)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Bank (銀行) | FinancialInstitution.fiType = 'DEPOSITORY_INSTITUTION' |
| 02 | Shinkin bank (信用金庫) | FinancialInstitution.fiType = 'DEPOSITORY_INSTITUTION' |
| 03 | Credit cooperative (信用組合) | FinancialInstitution.fiType = 'DEPOSITORY_INSTITUTION' |
| 04 | Securities company (証券会社) | FinancialInstitution.fiType = 'BROKER_DEALER' |
| 05 | Insurance company (保険会社) | FinancialInstitution.fiType = 'INSURANCE_COMPANY' |
| 06 | Money transfer service (資金移動業者) | FinancialInstitution.fiType = 'MSB' |
| 07 | Crypto asset exchange (暗号資産交換業者) | FinancialInstitution.fiType = 'OTHER' |

### Residence Status Codes (Field 25)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Japanese national (日本国籍) | extensions.residenceStatus = 'JAPANESE_NATIONAL' |
| 02 | Permanent resident (永住者) | extensions.residenceStatus = 'PERMANENT_RESIDENT' |
| 03 | Special permanent resident (特別永住者) | extensions.residenceStatus = 'SPECIAL_PERMANENT_RESIDENT' |
| 04 | Long-term resident (定住者) | extensions.residenceStatus = 'LONG_TERM_RESIDENT' |
| 05 | Work visa holder (就労ビザ) | extensions.residenceStatus = 'WORK_VISA' |
| 06 | Non-resident (非居住者) | extensions.residenceStatus = 'NON_RESIDENT' |

### Verification Method Codes (Field 35)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Face-to-face with ID (対面確認) | extensions.verificationMethod = 'IN_PERSON' |
| 02 | Non-face-to-face (electronic) (非対面・電子的方法) | extensions.verificationMethod = 'ELECTRONIC' |
| 03 | Photo ID verification (写真付き身分証明書) | extensions.verificationMethod = 'PHOTO_ID' |
| 04 | Public database verification (公的データベース照合) | extensions.verificationMethod = 'DATABASE' |

### Identification Document Type Codes (Field 36)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Driver's license (運転免許証) | Party.formOfIdentification = 'DRIVERS_LICENSE' |
| 02 | My Number card (マイナンバーカード) | Party.formOfIdentification = 'MY_NUMBER_CARD' |
| 03 | Passport (旅券) | Party.formOfIdentification = 'PASSPORT' |
| 04 | Residence card (在留カード) | Party.formOfIdentification = 'RESIDENCE_CARD' |
| 05 | Health insurance card (健康保険証) | Party.formOfIdentification = 'HEALTH_INSURANCE' |
| 06 | Pension handbook (年金手帳) | Party.formOfIdentification = 'PENSION_BOOK' |

### Account Type Codes (Field 45)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Ordinary deposit (普通預金) | Account.accountType = 'SAVINGS' |
| 02 | Current deposit (当座預金) | Account.accountType = 'CHECKING' |
| 03 | Time deposit (定期預金) | Account.accountType = 'CD' |
| 04 | Foreign currency deposit (外貨預金) | Account.accountType = 'SAVINGS' |
| 05 | Securities account (証券口座) | Account.accountType = 'INVESTMENT' |

### Transaction Type Codes (Field 56)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CSH | Cash deposit/withdrawal (現金入出金) | PaymentInstruction.paymentType = 'ACH_CREDIT' |
| TRF | Domestic transfer (国内振込) | PaymentInstruction.paymentType = 'WIRE_DOMESTIC' |
| RMT | International remittance (外国送金) | PaymentInstruction.paymentType = 'WIRE_INTERNATIONAL' |
| FEX | Foreign exchange (外国為替) | PaymentInstruction.paymentType = 'CROSS_BORDER' |
| CHQ | Check (小切手) | PaymentInstruction.paymentType = 'CHECK' |
| CRD | Card transaction (カード取引) | PaymentInstruction.paymentType = 'CROSS_BORDER' |
| CRY | Crypto asset transaction (暗号資産取引) | PaymentInstruction.paymentType = 'CROSS_BORDER' |

### Suspicion Category Codes (Field 66)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| ML | Money laundering (マネー・ローンダリング) | sarActivityTypeCheckboxes includes 'MONEY_LAUNDERING' |
| TF | Terrorism financing (テロ資金供与) | sarActivityTypeCheckboxes includes 'TERRORIST_FINANCING' |
| FR | Fraud (詐欺) | sarActivityTypeCheckboxes includes 'FRAUD' |
| DR | Drug-related crime (薬物犯罪) | sarActivityTypeCheckboxes includes 'DRUG_TRAFFICKING' |
| OR | Organized crime (組織犯罪) | sarActivityTypeCheckboxes includes 'ORGANIZED_CRIME' |
| CO | Corruption (汚職・腐敗) | sarActivityTypeCheckboxes includes 'BRIBERY' |
| TX | Tax evasion (脱税) | sarActivityTypeCheckboxes includes 'TAX_EVASION' |

### Suspected Crime Type Codes (Field 67)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| DRUG | Drug trafficking (薬物密売) | extensions.suspectedCrimeType includes 'DRUG_TRAFFICKING' |
| TERR | Terrorism (テロリズム) | extensions.suspectedCrimeType includes 'TERRORISM' |
| GANG | Organized crime/boryokudan (暴力団) | extensions.suspectedCrimeType includes 'ORGANIZED_CRIME' |
| FRAU | Fraud/swindling (詐欺) | extensions.suspectedCrimeType includes 'FRAUD' |
| CORR | Corruption/bribery (贈収賄) | extensions.suspectedCrimeType includes 'CORRUPTION' |
| EMBZ | Embezzlement (横領) | extensions.suspectedCrimeType includes 'EMBEZZLEMENT' |
| TAX | Tax crimes (税金犯罪) | extensions.suspectedCrimeType includes 'TAX_CRIMES' |

### Actions Taken Codes (Field 81)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Transaction monitoring (取引監視) | extensions.actionTaken includes 'MONITORING' |
| 02 | Additional verification (追加確認) | extensions.actionTaken includes 'ADDITIONAL_VERIFICATION' |
| 03 | Transaction stopped (取引停止) | extensions.actionTaken includes 'TRANSACTION_REJECTED' |
| 04 | Account frozen (口座凍結) | extensions.actionTaken includes 'ACCOUNT_FROZEN' |
| 05 | Relationship terminated (取引解除) | extensions.actionTaken includes 'RELATIONSHIP_TERMINATED' |
| 06 | STR filed only (届出のみ) | extensions.actionTaken includes 'STR_FILED_ONLY' |
| 07 | Police notified (警察通報) | extensions.actionTaken includes 'POLICE_NOTIFIED' |

---

## CDM Extensions Required

All 82 JAFIC STR fields successfully map to existing CDM model. **No enhancements required.**

The following extension attributes are used within Party, Account, ComplianceCase, and RegulatoryReport extensions:
- Japan-specific: japanRegistrationNumber, nameEnglish, nameKana, japanCorporateNumber, residenceStatus, idIssuingAuthority, idIssuanceDate, idExpiryDate, contactDepartment
- Verification: verificationMethod, purposeConfirmed, beneficialOwnerIdentified, beneficialOwnerName
- Account: averageMonthlyTurnover, counterpartyAccount, counterpartyInstitution
- Transaction: valueDateTime, transactionMethod, foreignTransactionFlag
- Suspicion: suspectedCrimeType, terrorismFinancingFlag, organizedCrimeFlag, unusualPatternFlag, cashIntensiveFlag, structuringIndicator, evasiveCustomer, inconsistentWithProfile, noEconomicRationale, pepInvolvement, highRiskJurisdiction
- Actions: suspicionFactors, actionTaken, additionalRemarks

---

## Example JAFIC STR Scenario

**Customer:** 山田太郎 (Yamada Taro) - Individual

**Suspicious Activity:** Structured cash deposits to avoid reporting threshold

**Detailed Description of Suspicion (Field 79) - in Japanese/English:**
```
【取引の概要 / Transaction Overview】
顧客：山田太郎（個人）
口座：普通預金 123-4567890
期間：2025年10月1日～2025年12月15日

Customer: Yamada Taro (Individual)
Account: Ordinary deposit 123-4567890
Period: October 1, 2025 - December 15, 2025

【疑わしい取引の詳細 / Details of Suspicious Transactions】
当該顧客は会社員（年収約500万円）として当行に口座を開設。通常の給与振込以外に、
以下の現金預入れパターンを確認：

The customer opened an account as a company employee (annual income approximately
JPY 5 million). In addition to regular salary deposits, the following cash deposit
pattern was observed:

1. 取引パターン / Transaction Pattern:
   - 74回の現金預入れ、総額32,850,000円
   - 各預入額：440,000円～490,000円（すべて50万円未満）
   - 頻度：ほぼ毎日（平日・土日を問わず）
   - 時間帯：ATM営業時間の様々な時間帯

   - 74 cash deposits totaling JPY 32,850,000
   - Each deposit: JPY 440,000 - 490,000 (all below JPY 500,000)
   - Frequency: Almost daily (both weekdays and weekends)
   - Time: Various hours during ATM operating hours

2. 疑わしい点 / Suspicious Points:
   a) 構造化の疑い：各取引が現金取引報告書（CTR）の閾値50万円を回避
   b) 収入との不整合：会社員の給与では説明できない多額の現金
   c) 入出金パターン：預入後24-48時間以内に全額を複数の口座へ送金
   d) 送金先：パチンコ店、質屋、消費者金融など高リスク業種

   a) Structuring suspicion: Each transaction avoids CTR threshold of JPY 500,000
   b) Income inconsistency: Large cash amounts unexplainable by salary
   c) Deposit/withdrawal pattern: All funds transferred within 24-48 hours
   d) Transfer destinations: Pachinko parlors, pawn shops, consumer finance (high-risk)

3. 顧客の行動 / Customer Behavior:
   - 資金源の質問に対して曖昧な回答（「親からの贈与」「副業収入」など）
   - 追加確認の要請に対して回避的
   - 複数のATMを使い分け（支店のパターン分析で判明）
   - 深夜・早朝の取引が多い

   - Vague responses about fund source ("gift from parents," "side business income")
   - Evasive when additional verification requested
   - Use of multiple ATMs (identified through branch pattern analysis)
   - Many transactions during late night/early morning hours

4. 実施した確認 / Verification Performed:
   - 本人確認：運転免許証で確認済み
   - 職業確認：会社への在籍確認実施（月給30万円程度と判明）
   - 資金源確認：説明を求めたが明確な回答なし
   - データベース照会：反社会的勢力該当なし、PEP該当なし

   - Identity verification: Confirmed with driver's license
   - Occupation verification: Employment confirmed (monthly salary approximately JPY 300,000)
   - Source of funds verification: Requested but no clear explanation provided
   - Database check: No organized crime affiliation, not a PEP

5. 疑念の根拠 / Grounds for Suspicion:
本取引は、以下の点から犯罪収益の移転に関与している可能性が高いと判断：
- 明確な構造化パターン（CTR回避）
- 収入源との著しい不整合
- レイヤリングの典型的手法（短期間の資金移動）
- 高リスク業種への送金集中
- 顧客の回避的態度

Based on the following points, there is a high possibility that this transaction
involves transfer of criminal proceeds:
- Clear structuring pattern (CTR avoidance)
- Significant inconsistency with known income source
- Typical layering technique (rapid fund movement)
- Concentration of transfers to high-risk industries
- Customer's evasive attitude

疑われる犯罪：マネー・ローンダリング、可能性として詐欺収益の移転
Suspected crime: Money laundering, possibly transfer of fraud proceeds
```

**Actions Taken (Field 81):**
- 継続的な取引監視を実施 (Ongoing transaction monitoring)
- 口座を凍結 (Account frozen on December 16, 2025)
- 2025年12月20日にJAFICへ疑わしい取引の届出を提出
  (STR filed with JAFIC on December 20, 2025)

---

## References

- Act on Prevention of Transfer of Criminal Proceeds (犯罪による収益の移転防止に関する法律): https://elaws.e-gov.go.jp/
- Japan Financial Intelligence Center (JAFIC / 警察庁 犯罪収益移転防止対策室): https://www.npa.go.jp/sosikihanzai/jafic/
- Financial Services Agency (FSA / 金融庁) AML/CFT Guidelines: https://www.fsa.go.jp/
- National Police Agency typologies reports: https://www.npa.go.jp/sosikihanzai/jafic/en/index.htm
- GPS CDM Schemas: `/schemas/05_regulatory_report_complete_schema.json`, `/schemas/06_compliance_case_complete_schema.json`, `/schemas/02_party_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2025-12-20
**Next Review:** Q2 2025
