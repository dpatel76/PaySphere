# CDM GLOBAL REGULATORY EXTENSIONS
## COMPREHENSIVE 3-PHASE ENHANCEMENT FOR 98% GLOBAL COVERAGE

**Document Version:** 1.0
**Date:** December 18, 2025
**Classification:** Technical Specification - Global Model Enhancement
**Target Coverage:** 98% of regulatory requirements across 69 jurisdictions

---

## EXECUTIVE SUMMARY

This document specifies comprehensive enhancements to the Payments Common Domain Model (CDM) to achieve **98% coverage** of regulatory reporting requirements across **69 global jurisdictions** where Bank of America operates.

**Enhancement Scope:**
- **Phase 1:** Critical Global Extensions (85% coverage target)
- **Phase 2:** Comprehensive Coverage (95% coverage target)
- **Phase 3:** Complete Coverage (98% coverage target)

**ISO 20022 Compliance Tracking:**
- ✅ **ISO 20022 Compliant:** Field exists in ISO 20022 standard (pain, pacs, camt messages)
- 🔶 **ISO 20022 Extended:** Field uses ISO 20022 structure but extended values/codes
- ❌ **Non-ISO Extension:** Field is jurisdiction-specific, not in ISO 20022

**Total Enhancements:**
- **New CDM Attributes:** 119 attributes
- **New Reference Entities:** 2 (RegulatoryPurposeCode, RelationshipToBeneficiary)
- **New Reference Codes:** 700+ codes
- **Implementation Effort:** 53 days

---

## TABLE OF CONTENTS

1. [Phase 1: Critical Global Extensions (85% Coverage)](#phase-1-critical-global-extensions)
2. [Phase 2: Comprehensive Coverage (95% Coverage)](#phase-2-comprehensive-coverage)
3. [Phase 3: Complete Coverage (98% Coverage)](#phase-3-complete-coverage)
4. [Entity-by-Entity Extensions](#entity-by-entity-extensions)
5. [ISO 20022 Compliance Matrix](#iso-20022-compliance-matrix)
6. [Reference Entities and Code Lists](#reference-entities-and-code-lists)
7. [Implementation DDL](#implementation-ddl)
8. [Testing and Validation](#testing-and-validation)

---

## PHASE 1: CRITICAL GLOBAL EXTENSIONS (85% COVERAGE)

**Target:** 2,380 of 2,800 global fields (85%)
**Effort:** 25 days
**Priority Jurisdictions:** Top 10 by BofA payment volume

### Phase 1 Extensions Summary

| Category | Attributes | ISO 20022 | Extended | Non-ISO | Reference Codes |
|----------|------------|-----------|----------|---------|-----------------|
| Tax Reporting | 25 | 10 | 8 | 7 | - |
| Sanctions Reporting | 15 | 5 | 3 | 7 | - |
| Cross-Border Purpose Codes | 10 | 5 | 5 | 0 | 350 codes |
| Jurisdiction-Specific | 10 | 0 | 2 | 8 | - |
| **TOTAL** | **60** | **20** | **18** | **22** | **350** |

---

### 1. TAX REPORTING EXTENSIONS

#### 1.1 Party Entity Extensions - Tax

| Attribute | Type | Constraints | ISO 20022 | Description | Jurisdictions |
|-----------|------|-------------|-----------|-------------|---------------|
| usTaxStatus | ENUM | See codes below | ❌ Non-ISO | US tax classification | US (FATCA) |
| fatcaClassification | ENUM | See codes below | ❌ Non-ISO | FATCA entity classification | US, Global |
| crsReportable | BOOLEAN | Not Null | 🔶 Extended | CRS reportable account flag | Global (OECD CRS) |
| crsEntityType | ENUM | See codes below | ❌ Non-ISO | CRS entity type classification | Global (OECD CRS) |
| taxResidencies | ARRAY<STRUCT> | See structure | ✅ ISO 20022 | Array of tax residency countries | Global |
| w8benStatus | ENUM | Active/Expired/NotProvided | ❌ Non-ISO | W-8BEN form status | US |
| w9Status | ENUM | Active/Expired/NotProvided | ❌ Non-ISO | W-9 form status | US |
| tinIssuingCountry | CHAR(2) | ISO 3166-1 | ✅ ISO 20022 | TIN issuing country (beyond primary) | Global |
| secondaryTINs | ARRAY<STRUCT> | country, tin, tinType | ✅ ISO 20022 | Secondary tax IDs for multiple jurisdictions | Global |
| substantialUSOwner | BOOLEAN | | ❌ Non-ISO | Substantial US owner flag (FATCA) | US, Global |

**usTaxStatus Codes:**
- US_CITIZEN
- US_RESIDENT_ALIEN
- NON_RESIDENT_ALIEN
- US_CORPORATION
- US_PARTNERSHIP
- US_TRUST
- FOREIGN_ENTITY

**fatcaClassification Codes:**
- ACTIVE_NFFE (Active Non-Financial Foreign Entity)
- PASSIVE_NFFE (Passive NFFE)
- FFI (Foreign Financial Institution)
- PARTICIPATING_FFI
- REGISTERED_DEEMED_COMPLIANT_FFI
- CERTIFIED_DEEMED_COMPLIANT_FFI
- EXCEPTED_FFI
- EXEMPT_BENEFICIAL_OWNER
- DIRECT_REPORTING_NFFE
- SPONSORED_DIRECT_REPORTING_NFFE

**crsEntityType Codes:**
- FINANCIAL_INSTITUTION
- ACTIVE_NFE (Non-Financial Entity)
- PASSIVE_NFE
- INVESTMENT_ENTITY
- GOVERNMENT_ENTITY
- INTERNATIONAL_ORGANISATION
- CENTRAL_BANK

**taxResidencies Structure:**
```json
{
  "country": "US",  // ISO 3166-1 alpha-2
  "tinType": "EIN",  // SSN, EIN, VAT, etc.
  "tin": "12-3456789",
  "taxResidencyBasis": "CITIZENSHIP",  // CITIZENSHIP, RESIDENCE, DOMICILE, INCORPORATION
  "effectiveFrom": "2020-01-01",
  "effectiveTo": null  // NULL = current
}
```

#### 1.2 Account Entity Extensions - Tax

| Attribute | Type | Constraints | ISO 20022 | Description | Jurisdictions |
|-----------|------|-------------|-----------|-------------|---------------|
| fatcaStatus | ENUM | See codes | ❌ Non-ISO | FATCA status of account | US, Global |
| fatcaGIIN | VARCHAR(19) | Format: XXXXXX.XXXXX.XX.XXX | ❌ Non-ISO | Global Intermediary Identification Number | US, Global |
| crsReportableAccount | BOOLEAN | | 🔶 Extended | CRS reportable flag | Global (100+ jurisdictions) |
| accountHolderType | ENUM | See codes | ❌ Non-ISO | FATCA/CRS account holder type | Global |
| controllingPersons | ARRAY<STRUCT> | See structure | ✅ ISO 20022 | Controlling persons for entities | Global |
| dormantAccount | BOOLEAN | | ✅ ISO 20022 | Dormant/inactive account flag | Global |
| accountBalanceForTaxReporting | DECIMAL(18,2) | | ✅ ISO 20022 | Account balance for tax reporting | Global |
| withholdingTaxRate | DECIMAL(5,2) | 0-100 | ✅ ISO 20022 | Applicable withholding tax rate | Global |

**fatcaStatus Codes:**
- PARTICIPATING_FFI_ACCOUNT
- NON_PARTICIPATING_FFI_ACCOUNT
- US_REPORTABLE_ACCOUNT
- RECALCITRANT_ACCOUNT
- DORMANT_ACCOUNT
- EXEMPT_ACCOUNT

**accountHolderType Codes:**
- INDIVIDUAL
- ENTITY_ACTIVE_NFE
- ENTITY_PASSIVE_NFE
- ENTITY_FINANCIAL_INSTITUTION
- ENTITY_GOVERNMENT
- ENTITY_INTERNATIONAL_ORG

**controllingPersons Structure:**
```json
{
  "partyId": "uuid-ref-to-party",
  "controlType": "OWNERSHIP",  // OWNERSHIP, SENIOR_MANAGING_OFFICIAL, CONTROLLING_PERSON
  "ownershipPercentage": 25.5,
  "taxResidence": ["US", "GB"],  // Array of ISO country codes
  "tin": "123-45-6789",
  "tinType": "SSN",
  "isPEP": false
}
```

#### 1.3 RegulatoryReport Entity Extensions - Tax

| Attribute | Type | Constraints | ISO 20022 | Description | Jurisdictions |
|-----------|------|-------------|-----------|-------------|---------------|
| taxYear | INTEGER | YYYY format | ❌ Non-ISO | Tax reporting year | Global |
| reportingFI_GIIN | VARCHAR(19) | FATCA GIIN format | ❌ Non-ISO | Reporting FI GIIN (FATCA) | US, Global |
| reportingFI_TIN | VARCHAR(50) | | ✅ ISO 20022 | Reporting FI TIN | Global |
| sponsorGIIN | VARCHAR(19) | | ❌ Non-ISO | Sponsor GIIN (if sponsored FFI) | US, Global |
| reportingModel | ENUM | Model1_IGA, Model2_IGA, NonIGA_FATCA, CRS | ❌ Non-ISO | FATCA/CRS reporting model | Global |
| IGAJurisdiction | CHAR(2) | ISO 3166-1 | ❌ Non-ISO | IGA (Intergovernmental Agreement) jurisdiction | Global |
| poolReportType | ENUM | See codes | ❌ Non-ISO | Pool reporting type (FATCA) | US |

**poolReportType Codes:**
- RECALCITRANT_ACCOUNT_HOLDERS_WITH_US_INDICIA
- RECALCITRANT_ACCOUNT_HOLDERS_WITHOUT_US_INDICIA
- DORMANT_ACCOUNTS
- NON_PARTICIPATING_FFIS

---

### 2. SANCTIONS REPORTING EXTENSIONS

#### 2.1 PaymentInstruction.extensions - Sanctions

| Field | Type | ISO 20022 | Description | Jurisdictions |
|-------|------|-----------|-------------|---------------|
| sanctionsMatchScore | DECIMAL(5,2) | ❌ Non-ISO | Fuzzy match score (0-100) | Global |
| sanctionsListName | VARCHAR(100) | 🔶 Extended | Sanctions list name | Global |
| sanctionsListSource | ENUM | See codes | ❌ Non-ISO | Sanctions list source authority | Global |
| sanctionsMatchType | ENUM | See codes | ❌ Non-ISO | Type of sanctions match | Global |
| sanctionsMatchedField | VARCHAR(50) | ❌ Non-ISO | Which field matched (name, address, etc.) | Global |
| blockingAuthority | VARCHAR(100) | ❌ Non-ISO | Authority requiring block | Global |
| blockingDate | DATE | ❌ Non-ISO | Date transaction was blocked | Global |
| blockingReason | TEXT | ❌ Non-ISO | Detailed blocking reason | Global |
| licenseException | VARCHAR(100) | ❌ Non-ISO | OFAC license exception number | US |
| licenseRequested | BOOLEAN | ❌ Non-ISO | License requested flag | US |
| licenseRequestDate | DATE | ❌ Non-ISO | License request date | US |
| licenseApprovalDate | DATE | ❌ Non-ISO | License approval date | US |
| licenseNumber | VARCHAR(50) | ❌ Non-ISO | OFAC license number | US |

**sanctionsListSource Codes:**
- OFAC (US Office of Foreign Assets Control)
- UN_CONSOLIDATED (United Nations)
- EU_CONSOLIDATED (European Union)
- UK_HMT (UK HM Treasury)
- DFAT (Australia Department of Foreign Affairs and Trade)
- MAS_SINGAPORE
- HKMA_HONG_KONG
- CBUAE_UAE
- SAMA_SAUDI_ARABIA
- PBOC_CHINA
- INTERNAL_WATCHLIST

**sanctionsMatchType Codes:**
- EXACT_MATCH
- FUZZY_MATCH
- PARTIAL_NAME_MATCH
- ADDRESS_MATCH
- DATE_OF_BIRTH_MATCH
- IDENTIFICATION_MATCH
- VESSEL_MATCH
- AIRCRAFT_MATCH
- FALSE_POSITIVE (after review)

#### 2.2 RegulatoryReport Entity Extensions - Sanctions

| Attribute | Type | Constraints | ISO 20022 | Description | Jurisdictions |
|-----------|------|-------------|-----------|-------------|---------------|
| sanctionsBlockingDate | DATE | | ❌ Non-ISO | Date property was blocked | Global |
| propertyBlocked | TEXT | | ❌ Non-ISO | Description of blocked property | Global |
| estimatedPropertyValue | DECIMAL(18,2) | | ❌ Non-ISO | Estimated value of blocked property | Global |
| sanctionsProgram | VARCHAR(100) | | ❌ Non-ISO | Sanctions program name (Iran, Russia, etc.) | Global |

---

### 3. CROSS-BORDER PURPOSE CODE TAXONOMY

#### 3.1 New Reference Entity: RegulatoryPurposeCode

**Purpose:** Comprehensive taxonomy of payment purpose codes across all jurisdictions

**Entity Structure:**

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| purposeCodeId | UUID | PK, Not Null | Unique identifier |
| jurisdiction | CHAR(2) | ISO 3166-1 | Jurisdiction (CN, IN, BR, etc.) |
| codeValue | VARCHAR(10) | Not Null | Code value (e.g., "1010" for China) |
| codeDescription | VARCHAR(500) | Not Null | Purpose description |
| category | VARCHAR(100) | | Category (Trade, Services, Investment, etc.) |
| subCategory | VARCHAR(100) | | Sub-category |
| iso20022Mapping | VARCHAR(4) | ISO External Purpose | ISO 20022 equivalent code if exists |
| applicablePaymentTypes | ARRAY<VARCHAR> | | Payment types where code applies |
| requiresSupporting Documents | BOOLEAN | | Documentation requirements |
| effectiveFrom | DATE | Not Null | Effective start date |
| effectiveTo | DATE | | Effective end date (NULL = current) |

**Purpose Code Categories by Jurisdiction:**

##### 3.1.1 China (PBOC) - 190 Purpose Codes

**Categories:**
1. **Trade in Goods (Codes 100000-199999):** 80 codes
   - General trade (121010, 121020, 121030)
   - Processing trade (122010, 122020)
   - Border/small-scale trade (123010)
   - Re-export trade (124010)
   - Barter trade (125010)
   - Bonded warehouse trade (126010)
   - Etc.

2. **Trade in Services (Codes 200000-299999):** 60 codes
   - Transportation services (221010-221050)
   - Travel services (222010-222030)
   - Communication services (223010)
   - Construction services (224010)
   - Insurance services (225010-225030)
   - Financial services (226010)
   - Computer/information services (227010)
   - Royalties and license fees (228010-228050)
   - Other business services (229010-229090)

3. **Income (Codes 300000-399999):** 30 codes
   - Compensation of employees (310000)
   - Investment income (321010-329030)

4. **Current Transfers (Codes 400000-499999):** 20 codes
   - Donations/grants (421010-421030)
   - Tax payments (422010)
   - Other transfers (429010-429090)

**Sample China Purpose Codes:**
```
121010 - General merchandise trade export
121020 - General merchandise trade import
122010 - Processing with imported materials (export)
122020 - Processing with imported materials (import)
221010 - Sea freight
221020 - Air freight
222010 - Business travel
222020 - Personal travel
228010 - Patent royalties
228020 - Trademark licensing fees
228030 - Software licensing
321010 - Equity investment income - dividends
321020 - Debt investment income - interest
622011 - Outward direct investment - equity investment
```

##### 3.1.2 India (RBI) - 80 Purpose Codes

**Categories:**
1. **Export of Goods and Services:** S0001 - S0099
2. **Import of Goods and Services:** S0101 - S0199
3. **Private Transfers:** S0201 - S0299
4. **Government Transfers:** S0301 - S0399
5. **Investment Income:** S0401 - S0499
6. **Loans:** S0501 - S0599
7. **Capital Account Transactions:** S1001 - S1099

**Sample India Purpose Codes:**
```
S0001 - Exports of goods
S0002 - Exports of software services
S0003 - Exports of business services
S0101 - Imports of goods
S0201 - Maintenance of close relatives
S0202 - Education-related expenses
S0203 - Medical treatment expenses
S0401 - Interest on loans
S0402 - Dividend income
S1001 - Foreign direct investment (equity)
S1002 - Portfolio investment
```

##### 3.1.3 Brazil (BACEN) - 40 Purpose Codes

**Categories:**
1. **International Trade:** 10100-10999
2. **Services:** 20100-20999
3. **Income:** 30100-30999
4. **Transfers:** 40100-40999
5. **Financial Capital:** 50100-50999

**Sample Brazil Purpose Codes:**
```
10101 - Export of goods - general merchandise
10201 - Import of goods - general merchandise
20101 - International freight
20201 - Insurance premiums
20301 - Travel expenses
30101 - Interest on loans
30201 - Dividends
40101 - Family support
50101 - Foreign direct investment
```

##### 3.1.4 Other Jurisdictions - Purpose Code Counts

| Jurisdiction | Code Count | Primary Categories |
|--------------|------------|-------------------|
| South Korea | 50 | Trade, Services, Investment, Transfers |
| Taiwan | 45 | Trade, Services, Income, Capital |
| Thailand | 40 | Trade, Services, Remittances |
| Philippines | 35 | OFW remittances, Trade, Investment |
| Malaysia | 35 | Trade, Services, Investment |
| Indonesia | 40 | Trade, Services, Remittances |
| Mexico | 30 | Trade, Remittances, Investment |
| Chile | 25 | Trade, Services, Investment |
| Colombia | 30 | Trade, Services, Remittances |
| South Africa | 40 | Trade, Services, Investment, CMA codes |

**Total Purpose Codes:** 350+ unique codes (China 190, India 80, other jurisdictions 80+)

#### 3.2 PaymentInstruction Extensions - Purpose Codes

| Field | Type | ISO 20022 | Description |
|-------|------|-----------|-------------|
| regulatoryPurposeCode | VARCHAR(10) | 🔶 Extended | Jurisdiction-specific purpose code |
| regulatoryPurposeCodeId | UUID | 🔶 Extended | FK to RegulatoryPurposeCode entity |
| purposeCategory | VARCHAR(100) | ✅ ISO 20022 | Purpose category |
| purposeSubCategory | VARCHAR(100) | 🔶 Extended | Purpose sub-category |
| tradeInvoiceNumber | VARCHAR(50) | ✅ ISO 20022 | Trade invoice number |
| tradeInvoiceDate | DATE | ✅ ISO 20022 | Trade invoice date |
| tradeContractNumber | VARCHAR(50) | 🔶 Extended | Trade contract number |
| goodsDescription | VARCHAR(500) | ✅ ISO 20022 | Description of goods (for trade) |
| hsCode | VARCHAR(10) | ❌ Non-ISO | Harmonized System commodity code |
| sourceOfFunds | VARCHAR(100) | 🔶 Extended | Source of funds description |

---

### 4. RELATIONSHIP TO BENEFICIARY TAXONOMY

#### 4.1 New Reference Entity: RelationshipToBeneficiary

**Purpose:** Standardized relationship codes required by multiple jurisdictions

**Entity Structure:**

| Attribute | Type | Description |
|-----------|------|-------------|
| relationshipCodeId | UUID | PK, Unique identifier |
| codeValue | VARCHAR(10) | Code value (R01, R02, etc.) |
| description | VARCHAR(200) | Relationship description |
| applicableJurisdictions | ARRAY<CHAR(2)> | Where code is used |
| iso20022Equivalent | VARCHAR(50) | ISO 20022 mapping if exists |

**Relationship Codes (25 codes):**

```
R01 - Spouse
R02 - Parent
R03 - Child
R04 - Sibling
R05 - Other Family Member
R06 - Employee (remitter is employer)
R07 - Employer (remitter is employee - salary)
R08 - Business Partner
R09 - Shareholder
R10 - Director/Officer
R11 - Customer (payment for goods/services purchased)
R12 - Supplier (payment for goods/services sold)
R13 - Lender (loan repayment)
R14 - Borrower (loan disbursement)
R15 - Investor (investment distribution)
R16 - Investee (capital contribution)
R17 - Tenant (rent payment)
R18 - Landlord (property owner)
R19 - Student (tuition payment)
R20 - Educational Institution
R21 - Medical Provider/Patient
R22 - Government Entity
R23 - Charity/Non-Profit
R24 - Self (own accounts)
R25 - No Relationship (third party)
```

#### 4.2 PaymentInstruction Extensions - Relationship

| Field | Type | ISO 20022 | Description | Jurisdictions |
|-------|------|-----------|-------------|---------------|
| relationshipToBeneficiary | VARCHAR(10) | 🔶 Extended | Relationship code | China, India, Philippines, Hong Kong, Singapore, UAE, others |
| relationshipToBeneficiaryId | UUID | 🔶 Extended | FK to reference entity | Global |
| relationshipDescription | VARCHAR(200) | 🔶 Extended | Free-text relationship | Global |

---

### 5. JURISDICTION-SPECIFIC EXTENSIONS

#### 5.1 China-Specific Extensions

| Field | Type | ISO 20022 | Description |
|-------|------|-----------|-------------|
| chinaSubjectCode | VARCHAR(10) | ❌ Non-ISO | China 190-code purpose taxonomy |
| chinaTradeTypeCode | VARCHAR(10) | ❌ Non-ISO | Trade type (general, processing, border, etc.) |
| chinaTransactionNature | VARCHAR(50) | ❌ Non-ISO | Transaction nature classification |
| chinaCustomsDeclarationNumber | VARCHAR(50) | ❌ Non-ISO | Customs declaration number (for trade) |

#### 5.2 India-Specific Extensions

| Field | Type | ISO 20022 | Description |
|-------|------|-----------|-------------|
| indiaRemittancePurpose | VARCHAR(10) | ❌ Non-ISO | India RBI purpose code (S0001-S1099) |
| indiaLRSCategory | VARCHAR(50) | ❌ Non-ISO | Liberalized Remittance Scheme category |
| indiaFEMACategory | VARCHAR(50) | ❌ Non-ISO | FEMA (Foreign Exchange Management Act) category |

#### 5.3 Brazil-Specific Extensions

| Field | Type | ISO 20022 | Description |
|-------|------|-----------|-------------|
| brazilPixKeyType | ENUM | ❌ Non-ISO | CPF, CNPJ, EMAIL, PHONE, EVP |
| brazilPixKey | VARCHAR(100) | ❌ Non-ISO | PIX key value |
| brazilNatureCode | VARCHAR(10) | ❌ Non-ISO | BACEN nature code (10100-50999) |
| brazilTransactionCode | VARCHAR(10) | ❌ Non-ISO | BACEN transaction code |

#### 5.4 Other Jurisdiction-Specific

| Field | Type | ISO 20022 | Description | Jurisdictions |
|-------|------|-----------|-------------|---------------|
| thaiPromptPayID | VARCHAR(50) | ❌ Non-ISO | Thailand PromptPay ID | Thailand |
| indiaUPIID | VARCHAR(100) | ❌ Non-ISO | India UPI ID (vpa@bank) | India |
| singaporePayNowID | VARCHAR(50) | ❌ Non-ISO | Singapore PayNow ID | Singapore |

---

## PHASE 2: COMPREHENSIVE COVERAGE (95% COVERAGE)

**Target:** 2,660 of 2,800 global fields (95%)
**Effort:** 18 days
**Scope:** All G20 + major APAC/LatAm jurisdictions

### Phase 2 Extensions Summary

| Category | Attributes | ISO 20022 | Extended | Non-ISO |
|----------|------------|-----------|----------|---------|
| Asia-Pacific Party Extensions | 8 | 2 | 1 | 5 |
| Mobile Money/Instant Payments | 10 | 0 | 3 | 7 |
| Middle East FI Extensions | 5 | 2 | 1 | 2 |
| Regional Reporting Workflows | 8 | 3 | 2 | 3 |
| Trade Finance Reporting | 8 | 6 | 2 | 0 |
| **TOTAL** | **39** | **13** | **9** | **17** |

---

### 6. ASIA-PACIFIC PARTY EXTENSIONS

#### 6.1 Party Entity Extensions - APAC

| Attribute | Type | ISO 20022 | Description | Jurisdictions |
|-----------|------|-----------|-------------|---------------|
| nationalIDType | VARCHAR(50) | ❌ Non-ISO | Country-specific national ID type | China, Korea, Taiwan, Japan, Singapore, Malaysia, Thailand, Indonesia, Philippines |
| nationalIDNumber | VARCHAR(50) | ❌ Non-ISO | National ID number | All APAC |
| chinaHukou | VARCHAR(100) | ❌ Non-ISO | Hukou (household registration) | China |
| indiaAadharNumber | VARCHAR(12) | ❌ Non-ISO | Aadhaar number (12-digit UID) | India |
| indiaCANNumber | VARCHAR(20) | ❌ Non-ISO | PAN (Permanent Account Number) alternate | India |
| koreaAlienRegistrationNumber | VARCHAR(13) | ❌ Non-ISO | Alien registration number | South Korea |
| japanMyNumber | VARCHAR(12) | ❌ Non-ISO | My Number (Individual Number) | Japan |
| singaporeNRIC_FIN | VARCHAR(9) | ❌ Non-ISO | NRIC (citizen) or FIN (foreigner) | Singapore |

**National ID Types by Jurisdiction:**

**China:**
- Resident Identity Card (居民身份证)
- Military ID
- Passport
- Hukou

**India:**
- Aadhaar (UID)
- PAN (Permanent Account Number)
- Voter ID
- Driving License
- Passport

**South Korea:**
- Resident Registration Number (주민등록번호) - 13 digits
- Alien Registration Number (외국인등록번호) - 13 digits
- Passport

**Japan:**
- My Number (マイナンバー) - 12 digits
- Resident Card (在留カード)
- Passport

**Singapore:**
- NRIC (National Registration Identity Card) - Sxxxxxxx format
- FIN (Foreign Identification Number) - for foreigners

**Thailand:**
- Thai National ID Card - 13 digits
- Passport

**Philippines:**
- PhilSys ID (National ID)
- SSS Number
- TIN (Tax Identification Number)
- Passport

**Malaysia:**
- MyKad (Malaysian Identity Card) - 12 digits
- Passport

**Indonesia:**
- KTP (Kartu Tanda Penduduk) - 16 digits
- NPWP (tax number)
- Passport

---

### 7. MOBILE MONEY & INSTANT PAYMENT EXTENSIONS

#### 7.1 PaymentInstruction.extensions - Mobile/Instant

| Field | Type | ISO 20022 | Description | Jurisdictions |
|-------|------|-----------|-------------|---------------|
| mobileMoneyProvider | VARCHAR(100) | ❌ Non-ISO | Mobile money provider name | Africa, APAC |
| mobileWalletID | VARCHAR(100) | 🔶 Extended | Mobile wallet identifier | Global |
| mobilePhoneNumber | VARCHAR(25) | 🔶 Extended | Mobile phone (E.164 format) | Global |
| pixKeyType | ENUM | ❌ Non-ISO | CPF, CNPJ, EMAIL, PHONE, EVP (random key) | Brazil |
| pixKey | VARCHAR(100) | ❌ Non-ISO | PIX key value | Brazil |
| pixTransactionID | VARCHAR(32) | ❌ Non-ISO | E2E ID for PIX | Brazil |
| upiID | VARCHAR(100) | ❌ Non-ISO | UPI Virtual Payment Address (vpa@bank) | India |
| upiTransactionID | VARCHAR(35) | ❌ Non-ISO | UPI transaction reference | India |
| promptPayID | VARCHAR(50) | ❌ Non-ISO | Thailand PromptPay citizen ID or phone | Thailand |
| payNowID | VARCHAR(50) | ❌ Non-ISO | Singapore PayNow ID | Singapore |

**Mobile Money Providers:**
- M-Pesa (Kenya, Tanzania, South Africa)
- MTN Mobile Money (Uganda, Ghana, Côte d'Ivoire, others)
- Airtel Money (multiple African countries)
- Orange Money (Francophone Africa)
- GCash (Philippines)
- PayMaya (Philippines)
- Touch 'n Go eWallet (Malaysia)
- GrabPay (Singapore, Malaysia, Philippines)
- Alipay (China)
- WeChat Pay (China)
- PhonePe (India)
- Paytm (India)
- Dana (Indonesia)
- OVO (Indonesia)
- TrueMoney (Thailand)

---

### 8. MIDDLE EAST FINANCIAL INSTITUTION EXTENSIONS

#### 8.1 FinancialInstitution Entity Extensions - Middle East

| Attribute | Type | ISO 20022 | Description | Jurisdictions |
|-----------|------|-----------|-------------|---------------|
| shariaCompliantFlag | BOOLEAN | ❌ Non-ISO | Islamic finance / Sharia-compliant | UAE, Saudi Arabia, Bahrain, Qatar, Kuwait, Oman, Malaysia |
| islamicFinanceType | ENUM | ❌ Non-ISO | Type of Islamic finance institution | GCC, Malaysia |
| centralBankLicenseNumber | VARCHAR(50) | ✅ ISO 20022 | Central bank license number | Middle East, Global |
| islamicFinancialServicesBoard | BOOLEAN | ❌ Non-ISO | IFSB member flag | Global |
| shariaAdvisoryBoard | BOOLEAN | ❌ Non-ISO | Has Sharia advisory board | GCC, Malaysia |

**islamicFinanceType Codes:**
- FULLY_SHARIA_COMPLIANT
- SHARIA_COMPLIANT_WINDOW (Islamic window within conventional bank)
- TAKAFUL_PROVIDER (Islamic insurance)
- SUKUK_ISSUER (Islamic bonds)
- CONVENTIONAL (not Sharia-compliant)

---

### 9. REGIONAL REPORTING WORKFLOW EXTENSIONS

#### 9.1 RegulatoryReport Entity Extensions - Regional Workflows

| Attribute | Type | ISO 20022 | Description | Jurisdictions |
|-----------|------|-----------|-------------|---------------|
| defenceAgainstMoneyLaunderingFlag | BOOLEAN | ❌ Non-ISO | DAML SAR flag (consent regime) | UK |
| consentRequired | BOOLEAN | ❌ Non-ISO | Consent required to proceed | UK |
| consentGranted | BOOLEAN | ❌ Non-ISO | Consent granted by NCA | UK |
| consentRefusalReason | TEXT | ❌ Non-ISO | Reason for consent refusal | UK |
| consentRequestDate | TIMESTAMP | ❌ Non-ISO | When consent was requested | UK |
| consentResponseDate | TIMESTAMP | ❌ Non-ISO | When consent response received | UK |
| consentExpiryDate | TIMESTAMP | ❌ Non-ISO | Consent expiry (7 days default) | UK |
| sarnNumber | VARCHAR(20) | ❌ Non-ISO | SAR reference number from NCA | UK |

**UK DAML (Defence Against Money Laundering) Workflow:**

The UK has a unique "consent regime" for SARs:
1. If a financial institution identifies a suspicious transaction and proceeding with it might constitute a money laundering offense, they must file a DAML SAR requesting consent.
2. The NCA (National Crime Agency) has 7 business days to respond (or 31 days if they refuse consent initially).
3. If consent is granted or no response within 7 days → proceed.
4. If consent is refused → cannot proceed with transaction for 31 days.

These fields track this workflow in the CDM.

---

### 10. TRADE FINANCE REPORTING EXTENSIONS

#### 10.1 PaymentInstruction.extensions - Trade Finance

| Field | Type | ISO 20022 | Description | Jurisdictions |
|-------|------|-----------|-------------|---------------|
| letterOfCreditNumber | VARCHAR(50) | ✅ ISO 20022 | L/C reference number | Global (trade finance) |
| billOfLadingNumber | VARCHAR(50) | ✅ ISO 20022 | Bill of lading number | Global (trade finance) |
| billOfLadingDate | DATE | ✅ ISO 20022 | B/L date | Global |
| hsCode | VARCHAR(10) | 🔶 Extended | Harmonized System commodity code | Global (customs) |
| tradeDocumentType | VARCHAR(50) | ✅ ISO 20022 | Type of trade document | Global |
| incoterms | VARCHAR(3) | ✅ ISO 20022 | Incoterms code (FOB, CIF, etc.) | Global (trade) |
| exportLicenseNumber | VARCHAR(50) | 🔶 Extended | Export license number | Global |
| importLicenseNumber | VARCHAR(50) | 🔶 Extended | Import license number | Global |

**Trade Document Types:**
- COMMERCIAL_INVOICE
- PROFORMA_INVOICE
- PACKING_LIST
- CERTIFICATE_OF_ORIGIN
- INSPECTION_CERTIFICATE
- INSURANCE_CERTIFICATE
- BILL_OF_LADING
- AIRWAY_BILL
- LETTER_OF_CREDIT
- SHIPPING_ADVICE

**Incoterms 2020:**
- EXW - Ex Works
- FCA - Free Carrier
- CPT - Carriage Paid To
- CIP - Carriage and Insurance Paid To
- DAP - Delivered at Place
- DPU - Delivered at Place Unloaded
- DDP - Delivered Duty Paid
- FAS - Free Alongside Ship
- FOB - Free on Board
- CFR - Cost and Freight
- CIF - Cost, Insurance and Freight

---

## PHASE 3: COMPLETE COVERAGE (98% COVERAGE)

**Target:** 2,744 of 2,800 global fields (98%)
**Effort:** 10 days
**Scope:** Edge cases, specialized reporting

### Phase 3 Extensions Summary

| Category | Attributes | ISO 20022 | Extended | Non-ISO |
|----------|------------|-----------|----------|---------|
| Counterfeit Currency Reporting | 5 | 1 | 1 | 3 |
| Casino/Gaming Reporting | 4 | 0 | 1 | 3 |
| Terrorist Property Reporting | 5 | 2 | 1 | 2 |
| Virtual Asset/Crypto Reporting | 6 | 0 | 2 | 4 |
| **TOTAL** | **20** | **3** | **5** | **12** |

---

### 11. COUNTERFEIT CURRENCY REPORTING (India CCR)

#### 11.1 PaymentInstruction.extensions - Counterfeit Currency

| Field | Type | ISO 20022 | Description | Jurisdictions |
|-------|------|-----------|-------------|---------------|
| counterfeitCurrencyDetected | BOOLEAN | ❌ Non-ISO | Counterfeit currency detected flag | India, others |
| counterfeitCurrencyAmount | DECIMAL(18,2) | ✅ ISO 20022 | Amount of counterfeit currency | India |
| counterfeitDenominations | ARRAY<STRUCT> | 🔶 Extended | Denominations detected | India |
| counterfeitSerialNumbers | ARRAY<VARCHAR> | ❌ Non-ISO | Serial numbers of counterfeit notes | India |
| counterfeitDetectionMethod | VARCHAR(100) | ❌ Non-ISO | How detected (UV, watermark, etc.) | India |

**counterfeitDenominations Structure:**
```json
{
  "currency": "INR",
  "denomination": 500,  // Note value
  "quantity": 5,  // Number of notes
  "totalAmount": 2500
}
```

---

### 12. CASINO/GAMING REPORTING (Canada)

#### 12.1 PaymentInstruction.extensions - Casino

| Field | Type | ISO 20022 | Description | Jurisdictions |
|-------|------|-----------|-------------|---------------|
| casinoDisbursement | BOOLEAN | ❌ Non-ISO | Casino disbursement flag | Canada |
| casinoName | VARCHAR(200) | ❌ Non-ISO | Casino name | Canada |
| casinoLicenseNumber | VARCHAR(50) | ❌ Non-ISO | Casino gaming license number | Canada |
| disbursementReason | ENUM | 🔶 Extended | WINNINGS, CASH_OUT, REFUND | Canada |

---

### 13. TERRORIST PROPERTY REPORTING

#### 13.1 RegulatoryReport Entity Extensions - Terrorist Property

| Attribute | Type | ISO 20022 | Description | Jurisdictions |
|-----------|------|-----------|-------------|---------------|
| terroristPropertyFlag | BOOLEAN | ❌ Non-ISO | Terrorist property report | Canada, South Africa, others |
| terroristEntityName | VARCHAR(200) | ✅ ISO 20022 | Listed terrorist entity name | Global |
| terroristListSource | VARCHAR(100) | 🔶 Extended | UN, domestic list, etc. | Global |
| propertyDescription | TEXT | ✅ ISO 20022 | Description of property | Global |
| propertySeized | BOOLEAN | ❌ Non-ISO | Property seized flag | Global |

---

### 14. VIRTUAL ASSET/CRYPTOCURRENCY REPORTING

#### 14.1 PaymentInstruction.extensions - Virtual Assets

| Field | Type | ISO 20022 | Description | Jurisdictions |
|-------|------|-----------|-------------|---------------|
| virtualAssetFlag | BOOLEAN | ❌ Non-ISO | Virtual asset transaction | Global (emerging) |
| virtualAssetType | ENUM | ❌ Non-ISO | BTC, ETH, USDT, etc. | Global |
| blockchainAddress | VARCHAR(100) | ❌ Non-ISO | Blockchain wallet address | Global |
| transactionHash | VARCHAR(100) | ❌ Non-ISO | Blockchain transaction hash | Global |
| vasp_Name | VARCHAR(200) | 🔶 Extended | Virtual Asset Service Provider name | Global |
| vasp_RegistrationNumber | VARCHAR(100) | 🔶 Extended | VASP registration number | Varies (Singapore, UAE, others) |

**virtualAssetType Codes:**
- BTC (Bitcoin)
- ETH (Ethereum)
- USDT (Tether)
- USDC (USD Coin)
- XRP (Ripple)
- ADA (Cardano)
- SOL (Solana)
- STABLECOIN_OTHER
- CRYPTO_OTHER

**Note:** Virtual asset reporting is emerging globally, led by:
- Singapore MAS (Payment Services Act)
- UAE VASP regulations
- Hong Kong VASP licensing
- Japan (already regulated since 2017)
- EU MiCA (Markets in Crypto-Assets) - effective 2024-2025

---

## ENTITY-BY-ENTITY EXTENSIONS COMPLETE SUMMARY

### Extended Entity 1: Party

**Total New Attributes:** 18

| Attribute | Phase | ISO 20022 |
|-----------|-------|-----------|
| usTaxStatus | 1 | ❌ |
| fatcaClassification | 1 | ❌ |
| crsReportable | 1 | 🔶 |
| crsEntityType | 1 | ❌ |
| taxResidencies | 1 | ✅ |
| w8benStatus | 1 | ❌ |
| w9Status | 1 | ❌ |
| tinIssuingCountry | 1 | ✅ |
| secondaryTINs | 1 | ✅ |
| substantialUSOwner | 1 | ❌ |
| nationalIDType | 2 | ❌ |
| nationalIDNumber | 2 | ❌ |
| chinaHukou | 2 | ❌ |
| indiaAadharNumber | 2 | ❌ |
| indiaCANNumber | 2 | ❌ |
| koreaAlienRegistrationNumber | 2 | ❌ |
| japanMyNumber | 2 | ❌ |
| singaporeNRIC_FIN | 2 | ❌ |

**ISO 20022 Compliance:** 3 compliant, 2 extended, 13 non-ISO (17% compliant)

---

### Extended Entity 2: Account

**Total New Attributes:** 8 (6 from Phase 1 Tax + 2 existing from previous enhancement)

| Attribute | Phase | ISO 20022 |
|-----------|-------|-----------|
| fatcaStatus | 1 | ❌ |
| fatcaGIIN | 1 | ❌ |
| crsReportableAccount | 1 | 🔶 |
| accountHolderType | 1 | ❌ |
| controllingPersons | 1 | ✅ |
| dormantAccount | 1 | ✅ |
| accountBalanceForTaxReporting | 1 | ✅ |
| withholdingTaxRate | 1 | ✅ |

**ISO 20022 Compliance:** 4 compliant, 1 extended, 3 non-ISO (50% compliant)

---

### Extended Entity 3: PaymentInstruction.extensions (JSON)

**Total New Fields:** 64

| Category | Fields | Phase | ISO 20022 Compliant |
|----------|--------|-------|---------------------|
| Sanctions | 13 | 1 | 0% |
| Purpose Codes | 10 | 1 | 50% |
| Relationship to Beneficiary | 3 | 1 | 33% |
| China-Specific | 4 | 1 | 0% |
| India-Specific | 3 | 1 | 0% |
| Brazil-Specific | 4 | 1 | 0% |
| Other Jurisdiction-Specific | 3 | 1 | 0% |
| Mobile Money/Instant | 10 | 2 | 20% |
| Trade Finance | 8 | 2 | 75% |
| Counterfeit Currency | 5 | 3 | 20% |
| Casino | 4 | 3 | 25% |
| Virtual Assets | 6 | 3 | 33% |
| **TOTAL** | **64** | **1-3** | **~28%** |

---

### Extended Entity 4: RegulatoryReport

**Total New Attributes:** 19

| Attribute | Phase | ISO 20022 |
|-----------|-------|-----------|
| taxYear | 1 | ❌ |
| reportingFI_GIIN | 1 | ❌ |
| reportingFI_TIN | 1 | ✅ |
| sponsorGIIN | 1 | ❌ |
| reportingModel | 1 | ❌ |
| IGAJurisdiction | 1 | ❌ |
| poolReportType | 1 | ❌ |
| sanctionsBlockingDate | 1 | ❌ |
| propertyBlocked | 1 | ❌ |
| estimatedPropertyValue | 1 | ❌ |
| sanctionsProgram | 1 | ❌ |
| defenceAgainstMoneyLaunderingFlag | 2 | ❌ |
| consentRequired | 2 | ❌ |
| consentGranted | 2 | ❌ |
| consentRefusalReason | 2 | ❌ |
| consentRequestDate | 2 | ❌ |
| consentResponseDate | 2 | ❌ |
| consentExpiryDate | 2 | ❌ |
| sarnNumber | 2 | ❌ |

**ISO 20022 Compliance:** 1 compliant, 0 extended, 18 non-ISO (5% compliant)

---

### Extended Entity 5: FinancialInstitution

**Total New Attributes:** 5

| Attribute | Phase | ISO 20022 |
|-----------|-------|-----------|
| shariaCompliantFlag | 2 | ❌ |
| islamicFinanceType | 2 | ❌ |
| centralBankLicenseNumber | 2 | ✅ |
| islamicFinancialServicesBoard | 2 | ❌ |
| shariaAdvisoryBoard | 2 | ❌ |

**ISO 20022 Compliance:** 1 compliant, 0 extended, 4 non-ISO (20% compliant)

---

### New Entity 6: RegulatoryPurposeCode (Reference Entity)

**Total Attributes:** 10
**Total Codes:** 350+

| Attribute | ISO 20022 |
|-----------|-----------|
| purposeCodeId | ❌ |
| jurisdiction | ✅ |
| codeValue | ❌ |
| codeDescription | ✅ |
| category | 🔶 |
| subCategory | 🔶 |
| iso20022Mapping | ✅ |
| applicablePaymentTypes | ❌ |
| requiresSupportingDocuments | ❌ |
| effectiveFrom | ✅ |

---

### New Entity 7: RelationshipToBeneficiary (Reference Entity)

**Total Attributes:** 5
**Total Codes:** 25

| Attribute | ISO 20022 |
|-----------|-----------|
| relationshipCodeId | ❌ |
| codeValue | ❌ |
| description | 🔶 |
| applicableJurisdictions | ❌ |
| iso20022Equivalent | ✅ |

---

## ISO 20022 COMPLIANCE MATRIX

### Overall Compliance Summary

| Entity | Total New Attributes | ISO 20022 Compliant | Extended | Non-ISO | Compliance % |
|--------|---------------------|---------------------|----------|---------|--------------|
| Party | 18 | 3 | 2 | 13 | 17% |
| Account | 8 | 4 | 1 | 3 | 50% |
| PaymentInstruction.extensions | 64 | 18 | 12 | 34 | 28% |
| RegulatoryReport | 19 | 1 | 0 | 18 | 5% |
| FinancialInstitution | 5 | 1 | 0 | 4 | 20% |
| RegulatoryPurposeCode | 10 | 4 | 2 | 4 | 40% |
| RelationshipToBeneficiary | 5 | 1 | 1 | 3 | 20% |
| **TOTAL** | **129** | **32** | **18** | **79** | **25%** |

**Key Insight:** 75% of global regulatory requirements are jurisdiction-specific extensions beyond ISO 20022, which is expected since ISO 20022 is a messaging standard, not a comprehensive regulatory reporting framework.

### ISO 20022 Compliant Fields (32 fields)

✅ **Fully Compliant with ISO 20022:**
- Party: taxResidencies, tinIssuingCountry, secondaryTINs
- Account: controllingPersons, dormantAccount, accountBalanceForTaxReporting, withholdingTaxRate
- PaymentInstruction: purposeCategory, tradeInvoiceNumber, tradeInvoiceDate, goodsDescription, letterOfCreditNumber, billOfLadingNumber, billOfLadingDate, tradeDocumentType, incoterms, counterfeitCurrencyAmount, terroristEntityName, propertyDescription
- RegulatoryReport: reportingFI_TIN
- FinancialInstitution: centralBankLicenseNumber
- RegulatoryPurposeCode: jurisdiction, codeDescription, iso20022Mapping, effectiveFrom
- RelationshipToBeneficiary: iso20022Equivalent

### ISO 20022 Extended Fields (18 fields)

🔶 **Uses ISO 20022 Structure, Extended Values:**
- Party: crsReportable
- Account: crsReportableAccount
- PaymentInstruction: regulatoryPurposeCode, regulatoryPurposeCodeId, purposeSubCategory, sourceOfFunds, relationshipToBeneficiary, relationshipToBeneficiaryId, relationshipDescription, mobileWalletID, mobilePhoneNumber, hsCode, exportLicenseNumber, importLicenseNumber, counterfeitDenominations, disbursementReason, terroristListSource, vasp_Name, vasp_RegistrationNumber
- RegulatoryPurposeCode: category, subCategory
- RelationshipToBeneficiary: description

### Non-ISO Extensions (79 fields)

❌ **Jurisdiction-Specific, Not in ISO 20022:**
All tax reporting fields (FATCA, CRS), sanctions fields, China/India/Brazil-specific fields, mobile money provider-specific fields, casino/counterfeit currency fields, etc.

---

## REFERENCE ENTITIES AND CODE LISTS

### 1. RegulatoryPurposeCode Entity

**Total Codes:** 350+

**Load Strategy:**
```sql
-- China Purpose Codes (190 codes)
INSERT INTO cdm_silver.compliance.regulatory_purpose_code VALUES
  ('uuid1', 'CN', '121010', 'General merchandise trade - export', 'Trade in Goods', 'Export', 'GDDS', ARRAY('SWIFT','Wire'), false, '2015-01-01', NULL),
  ('uuid2', 'CN', '121020', 'General merchandise trade - import', 'Trade in Goods', 'Import', 'GDDS', ARRAY('SWIFT','Wire'), false, '2015-01-01', NULL),
  ('uuid3', 'CN', '122010', 'Processing with imported materials - export', 'Trade in Goods', 'Processing Trade', 'GDDS', ARRAY('SWIFT','Wire'), true, '2015-01-01', NULL),
  -- ... 187 more China codes

-- India Purpose Codes (80 codes)
  ('uuid191', 'IN', 'S0001', 'Exports of goods', 'Export of Goods and Services', 'Goods', 'GDDS', ARRAY('Wire','RTGS'), false, '2016-01-01', NULL),
  ('uuid192', 'IN', 'S0002', 'Exports of software services', 'Export of Goods and Services', 'Software', 'GDDS', ARRAY('Wire','RTGS'), false, '2016-01-01', NULL),
  -- ... 78 more India codes

-- Brazil, Korea, Taiwan, ASEAN, etc. (80+ codes)
  -- ...
;
```

### 2. RelationshipToBeneficiary Entity

**Total Codes:** 25

**Load Strategy:**
```sql
INSERT INTO cdm_silver.compliance.relationship_to_beneficiary VALUES
  ('uuid1', 'R01', 'Spouse', ARRAY('CN','IN','PH','HK','SG','TH','MY','ID','VN','AE','SA'), 'FAMI'),
  ('uuid2', 'R02', 'Parent', ARRAY('CN','IN','PH','HK','SG','TH','MY','ID','VN','AE','SA'), 'FAMI'),
  ('uuid3', 'R03', 'Child', ARRAY('CN','IN','PH','HK','SG','TH','MY','ID','VN','AE','SA'), 'FAMI'),
  ('uuid4', 'R04', 'Sibling', ARRAY('CN','IN','PH','HK','SG','TH','MY','ID','VN'), 'FAMI'),
  ('uuid5', 'R05', 'Other Family Member', ARRAY('CN','IN','PH','HK','SG','TH','MY','ID','VN','AE','SA'), 'FAMI'),
  ('uuid6', 'R06', 'Employee (remitter is employer)', ARRAY('CN','IN','PH','HK','SG','TH','MY','ID','VN','AE','SA','BR','MX'), 'SALA'),
  ('uuid7', 'R07', 'Employer (remitter is employee - salary)', ARRAY('CN','IN','PH','HK','SG','TH','MY','ID','VN','AE','SA'), 'SALA'),
  ('uuid8', 'R08', 'Business Partner', ARRAY('CN','IN','HK','SG','AE','SA'), 'BUSI'),
  ('uuid9', 'R09', 'Shareholder', ARRAY('CN','IN','HK','SG','AE'), 'DIVI'),
  ('uuid10', 'R10', 'Director/Officer', ARRAY('CN','IN','HK','SG','AE'), NULL),
  ('uuid11', 'R11', 'Customer (payment for goods/services purchased)', ARRAY('CN','IN','PH','HK','SG','TH','MY','ID','VN','AE','SA','BR','MX'), 'GDDS'),
  ('uuid12', 'R12', 'Supplier (payment for goods/services sold)', ARRAY('CN','IN','PH','HK','SG','TH','MY','ID','VN','AE','SA','BR','MX'), 'GDDS'),
  ('uuid13', 'R13', 'Lender (loan repayment)', ARRAY('CN','IN','HK','SG','AE'), 'LOAN'),
  ('uuid14', 'R14', 'Borrower (loan disbursement)', ARRAY('CN','IN','HK','SG','AE'), 'LOAN'),
  ('uuid15', 'R15', 'Investor (investment distribution)', ARRAY('CN','IN','HK','SG','AE'), 'DIVI'),
  ('uuid16', 'R16', 'Investee (capital contribution)', ARRAY('CN','IN','HK','SG','AE'), NULL),
  ('uuid17', 'R17', 'Tenant (rent payment)', ARRAY('CN','IN','PH','HK','SG','AE'), 'RENT'),
  ('uuid18', 'R18', 'Landlord (property owner)', ARRAY('CN','IN','PH','HK','SG','AE'), NULL),
  ('uuid19', 'R19', 'Student (tuition payment)', ARRAY('CN','IN','PH','HK','SG','TH','MY','ID','VN','AE','SA','BR'), 'EDUC'),
  ('uuid20', 'R20', 'Educational Institution', ARRAY('CN','IN','PH','HK','SG','TH','MY','ID','VN','AE','SA'), 'EDUC'),
  ('uuid21', 'R21', 'Medical Provider/Patient', ARRAY('IN','PH','SG','TH','MY','AE','SA'), 'MDCS'),
  ('uuid22', 'R22', 'Government Entity', ARRAY('CN','IN','PH','HK','SG','TH','MY','ID','VN','AE','SA','BR','MX'), 'TAXS'),
  ('uuid23', 'R23', 'Charity/Non-Profit', ARRAY('IN','PH','SG','AE','SA','BR'), 'CHAR'),
  ('uuid24', 'R24', 'Self (own accounts)', ARRAY('CN','IN','PH','HK','SG','TH','MY','ID','VN','AE','SA','BR','MX'), NULL),
  ('uuid25', 'R25', 'No Relationship (third party)', ARRAY('CN','IN','PH','HK','SG'), NULL)
;
```

---

## IMPLEMENTATION DDL

### Phase 1 DDL

```sql
-- ============================================================================
-- PHASE 1: CRITICAL GLOBAL EXTENSIONS (85% COVERAGE)
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. NEW REFERENCE ENTITY: RegulatoryPurposeCode
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cdm_silver.compliance.regulatory_purpose_code (
  purpose_code_id STRING NOT NULL COMMENT 'UUID v4 primary key',
  jurisdiction STRING NOT NULL COMMENT 'ISO 3166-1 alpha-2 country code',
  code_value STRING NOT NULL COMMENT 'Purpose code value (e.g., 121010 for China)',
  code_description STRING NOT NULL COMMENT 'Purpose description',
  category STRING COMMENT 'Category (Trade, Services, Investment, etc.)',
  sub_category STRING COMMENT 'Sub-category',
  iso20022_mapping STRING COMMENT 'ISO 20022 External Purpose Code equivalent',
  applicable_payment_types ARRAY<STRING> COMMENT 'Payment types where code applies',
  requires_supporting_documents BOOLEAN COMMENT 'Documentation requirements',
  effective_from DATE NOT NULL COMMENT 'Effective start date',
  effective_to DATE COMMENT 'Effective end date (NULL = current)',
  created_timestamp TIMESTAMP NOT NULL COMMENT 'Record creation timestamp',
  last_updated_timestamp TIMESTAMP NOT NULL COMMENT 'Last update timestamp'
)
USING DELTA
PARTITIONED BY (jurisdiction)
COMMENT 'Regulatory purpose codes for cross-border payments across 69 jurisdictions';

ALTER TABLE cdm_silver.compliance.regulatory_purpose_code
ADD CONSTRAINT pk_regulatory_purpose_code PRIMARY KEY (purpose_code_id);

CREATE INDEX idx_purpose_code_jurisdiction_code
ON cdm_silver.compliance.regulatory_purpose_code (jurisdiction, code_value);

-- ---------------------------------------------------------------------------
-- 2. NEW REFERENCE ENTITY: RelationshipToBeneficiary
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cdm_silver.compliance.relationship_to_beneficiary (
  relationship_code_id STRING NOT NULL COMMENT 'UUID v4 primary key',
  code_value STRING NOT NULL COMMENT 'Relationship code (R01-R25)',
  description STRING NOT NULL COMMENT 'Relationship description',
  applicable_jurisdictions ARRAY<STRING> COMMENT 'ISO country codes where used',
  iso20022_equivalent STRING COMMENT 'ISO 20022 mapping if exists',
  created_timestamp TIMESTAMP NOT NULL COMMENT 'Record creation timestamp',
  last_updated_timestamp TIMESTAMP NOT NULL COMMENT 'Last update timestamp'
)
USING DELTA
COMMENT 'Relationship to beneficiary reference codes';

ALTER TABLE cdm_silver.compliance.relationship_to_beneficiary
ADD CONSTRAINT pk_relationship_to_beneficiary PRIMARY KEY (relationship_code_id);

-- ---------------------------------------------------------------------------
-- 3. PARTY ENTITY EXTENSIONS - Tax Reporting
-- ---------------------------------------------------------------------------

ALTER TABLE cdm_silver.payments.party ADD COLUMNS (
  -- Tax Reporting Extensions
  us_tax_status STRING COMMENT 'US tax classification: US_CITIZEN, US_RESIDENT_ALIEN, NON_RESIDENT_ALIEN, US_CORPORATION, etc.',
  fatca_classification STRING COMMENT 'FATCA entity classification: ACTIVE_NFFE, PASSIVE_NFFE, FFI, PARTICIPATING_FFI, etc.',
  crs_reportable BOOLEAN COMMENT 'CRS reportable flag (OECD Common Reporting Standard)',
  crs_entity_type STRING COMMENT 'CRS entity type: FINANCIAL_INSTITUTION, ACTIVE_NFE, PASSIVE_NFE, etc.',
  tax_residencies ARRAY<STRUCT<country:STRING, tin_type:STRING, tin:STRING, tax_residency_basis:STRING, effective_from:DATE, effective_to:DATE>>
    COMMENT 'Array of tax residency countries with TINs',
  w8ben_status STRING COMMENT 'W-8BEN form status: ACTIVE, EXPIRED, NOT_PROVIDED',
  w9_status STRING COMMENT 'W-9 form status: ACTIVE, EXPIRED, NOT_PROVIDED',
  tin_issuing_country STRING COMMENT 'TIN issuing country (ISO 3166-1 alpha-2) - beyond primary',
  secondary_tins ARRAY<STRUCT<country:STRING, tin:STRING, tin_type:STRING>>
    COMMENT 'Secondary tax IDs for multiple jurisdictions',
  substantial_us_owner BOOLEAN COMMENT 'Substantial US owner flag (FATCA)'
);

-- ---------------------------------------------------------------------------
-- 4. ACCOUNT ENTITY EXTENSIONS - Tax Reporting
-- ---------------------------------------------------------------------------

ALTER TABLE cdm_silver.payments.account ADD COLUMNS (
  -- Tax Reporting Extensions
  fatca_status STRING COMMENT 'FATCA status: PARTICIPATING_FFI_ACCOUNT, NON_PARTICIPATING_FFI_ACCOUNT, US_REPORTABLE_ACCOUNT, etc.',
  fatca_giin STRING COMMENT 'Global Intermediary Identification Number (19 chars: XXXXXX.XXXXX.XX.XXX)',
  crs_reportable_account BOOLEAN COMMENT 'CRS reportable account flag',
  account_holder_type STRING COMMENT 'FATCA/CRS account holder type: INDIVIDUAL, ENTITY_ACTIVE_NFE, ENTITY_PASSIVE_NFE, etc.',
  controlling_persons ARRAY<STRUCT<party_id:STRING, control_type:STRING, ownership_percentage:DECIMAL(5,2), tax_residence:ARRAY<STRING>, tin:STRING, tin_type:STRING, is_pep:BOOLEAN>>
    COMMENT 'Controlling persons for entities (FATCA/CRS)',
  dormant_account BOOLEAN COMMENT 'Dormant/inactive account flag',
  account_balance_for_tax_reporting DECIMAL(18,2) COMMENT 'Account balance for tax reporting purposes',
  withholding_tax_rate DECIMAL(5,2) COMMENT 'Applicable withholding tax rate (0-100)'
);

-- ---------------------------------------------------------------------------
-- 5. REGULATORYREPORT ENTITY EXTENSIONS - Tax Reporting
-- ---------------------------------------------------------------------------

ALTER TABLE cdm_silver.compliance.regulatory_report ADD COLUMNS (
  -- Tax Reporting Extensions
  tax_year INT COMMENT 'Tax reporting year (YYYY)',
  reporting_fi_giin STRING COMMENT 'Reporting FI GIIN for FATCA (19 chars)',
  reporting_fi_tin STRING COMMENT 'Reporting FI TIN',
  sponsor_giin STRING COMMENT 'Sponsor GIIN if sponsored FFI (19 chars)',
  reporting_model STRING COMMENT 'FATCA/CRS reporting model: MODEL1_IGA, MODEL2_IGA, NON_IGA_FATCA, CRS',
  iga_jurisdiction STRING COMMENT 'IGA (Intergovernmental Agreement) jurisdiction (ISO 3166-1)',
  pool_report_type STRING COMMENT 'Pool reporting type: RECALCITRANT_ACCOUNT_HOLDERS_WITH_US_INDICIA, RECALCITRANT_ACCOUNT_HOLDERS_WITHOUT_US_INDICIA, DORMANT_ACCOUNTS, NON_PARTICIPATING_FFIS',

  -- Sanctions Reporting Extensions
  sanctions_blocking_date DATE COMMENT 'Date property was blocked due to sanctions',
  property_blocked STRING COMMENT 'Description of blocked property',
  estimated_property_value DECIMAL(18,2) COMMENT 'Estimated value of blocked property',
  sanctions_program STRING COMMENT 'Sanctions program name (Iran, Russia, North Korea, etc.)'
);

-- ---------------------------------------------------------------------------
-- 6. PAYMENTINSTRUCTION.EXTENSIONS JSON EXTENSIONS - Phase 1
-- ---------------------------------------------------------------------------

-- Note: PaymentInstruction.extensions is a JSON column, so we document the schema here
-- rather than ALTER TABLE. Validation via JSON Schema in application layer.

/*
PaymentInstruction.extensions JSON Schema Additions - Phase 1:

{
  "sanctions": {
    "sanctionsMatchScore": 95.5,  // DECIMAL(5,2)
    "sanctionsListName": "OFAC SDN List",
    "sanctionsListSource": "OFAC",  // ENUM
    "sanctionsMatchType": "FUZZY_MATCH",  // ENUM
    "sanctionsMatchedField": "beneficiary_name",
    "blockingAuthority": "US OFAC",
    "blockingDate": "2025-12-15",  // DATE
    "blockingReason": "Matched to SDN List entry #12345",
    "licenseException": "GL-10",
    "licenseRequested": true,  // BOOLEAN
    "licenseRequestDate": "2025-12-16",
    "licenseApprovalDate": null,
    "licenseNumber": null
  },

  "purposeCode": {
    "regulatoryPurposeCode": "121010",  // China code for general trade export
    "regulatoryPurposeCodeId": "uuid-ref-to-purpose-code-entity",
    "purposeCategory": "Trade in Goods",
    "purposeSubCategory": "Export",
    "tradeInvoiceNumber": "INV-2025-001234",
    "tradeInvoiceDate": "2025-12-10",
    "tradeContractNumber": "TC-2025-5678",
    "goodsDescription": "Electronic components for manufacturing",
    "hsCode": "8542.31",  // Harmonized System commodity code
    "sourceOfFunds": "Business revenue from operations"
  },

  "relationshipToBeneficiary": {
    "relationshipToBeneficiary": "R11",  // Customer
    "relationshipToBeneficiaryId": "uuid-ref-to-relationship-entity",
    "relationshipDescription": "Payment for goods purchased"
  },

  "chinaSpecific": {
    "chinaSubjectCode": "121010",
    "chinaTradeTypeCode": "GENERAL_TRADE",
    "chinaTransactionNature": "EXPORT",
    "chinaCustomsDeclarationNumber": "CN-2025-DEC-001234"
  },

  "indiaSpecific": {
    "indiaRemittancePurpose": "S0001",  // Exports of goods
    "indiaLRSCategory": "INVESTMENT",
    "indiaFEMACategory": "CURRENT_ACCOUNT"
  },

  "brazilSpecific": {
    "brazilPixKeyType": "CPF",  // CPF, CNPJ, EMAIL, PHONE, EVP
    "brazilPixKey": "123.456.789-00",
    "brazilNatureCode": "10101",
    "brazilTransactionCode": "8001"
  }
}
*/

COMMENT ON COLUMN cdm_silver.payments.payment_instruction.extensions IS
'JSON extensions for product-specific and regulatory fields. Phase 1 adds: sanctions (13 fields), purpose codes (10 fields), relationship to beneficiary (3 fields), China-specific (4 fields), India-specific (3 fields), Brazil-specific (4 fields). See cdm_global_regulatory_extensions.md for complete schema.';

```

### Phase 2 DDL

```sql
-- ============================================================================
-- PHASE 2: COMPREHENSIVE GLOBAL COVERAGE (95% COVERAGE)
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 7. PARTY ENTITY EXTENSIONS - Asia-Pacific
-- ---------------------------------------------------------------------------

ALTER TABLE cdm_silver.payments.party ADD COLUMNS (
  -- Asia-Pacific National ID Extensions
  national_id_type STRING COMMENT 'Country-specific national ID type (Resident ID, NRIC, My Number, etc.)',
  national_id_number STRING COMMENT 'National ID number',
  china_hukou STRING COMMENT 'Hukou (household registration) - China',
  india_aadhar_number STRING COMMENT 'Aadhaar UID (12 digits) - India',
  india_pan_number STRING COMMENT 'PAN (Permanent Account Number) - India (already exists as taxIdentificationNumber, this is alternate)',
  korea_alien_registration_number STRING COMMENT 'Alien registration number (13 digits) - South Korea',
  japan_my_number STRING COMMENT 'My Number / Individual Number (12 digits) - Japan',
  singapore_nric_fin STRING COMMENT 'NRIC (citizen) or FIN (foreigner) - Singapore (9 chars)'
);

-- ---------------------------------------------------------------------------
-- 8. FINANCIALINSTITUTION ENTITY EXTENSIONS - Middle East
-- ---------------------------------------------------------------------------

ALTER TABLE cdm_silver.payments.financial_institution ADD COLUMNS (
  -- Middle East / Islamic Finance Extensions
  sharia_compliant_flag BOOLEAN COMMENT 'Islamic finance / Sharia-compliant institution',
  islamic_finance_type STRING COMMENT 'Type: FULLY_SHARIA_COMPLIANT, SHARIA_COMPLIANT_WINDOW, TAKAFUL_PROVIDER, SUKUK_ISSUER, CONVENTIONAL',
  central_bank_license_number STRING COMMENT 'Central bank license number',
  islamic_financial_services_board BOOLEAN COMMENT 'IFSB (Islamic Financial Services Board) member',
  sharia_advisory_board BOOLEAN COMMENT 'Has Sharia advisory board'
);

-- ---------------------------------------------------------------------------
-- 9. REGULATORYREPORT ENTITY EXTENSIONS - Regional Workflows
-- ---------------------------------------------------------------------------

ALTER TABLE cdm_silver.compliance.regulatory_report ADD COLUMNS (
  -- UK DAML (Defence Against Money Laundering) Workflow Extensions
  defence_against_money_laundering_flag BOOLEAN COMMENT 'UK DAML SAR flag (consent regime)',
  consent_required BOOLEAN COMMENT 'Consent required to proceed with transaction',
  consent_granted BOOLEAN COMMENT 'Consent granted by NCA (National Crime Agency)',
  consent_refusal_reason STRING COMMENT 'Reason for consent refusal',
  consent_request_date TIMESTAMP COMMENT 'When consent was requested from NCA',
  consent_response_date TIMESTAMP COMMENT 'When consent response received from NCA',
  consent_expiry_date TIMESTAMP COMMENT 'Consent expiry (7 business days default, or 31 days if refused)',
  sarn_number STRING COMMENT 'SAR reference number from UK NCA'
);

-- ---------------------------------------------------------------------------
-- 10. PAYMENTINSTRUCTION.EXTENSIONS JSON EXTENSIONS - Phase 2
-- ---------------------------------------------------------------------------

/*
PaymentInstruction.extensions JSON Schema Additions - Phase 2:

{
  "mobileMoney": {
    "mobileMoneyProvider": "M-Pesa",
    "mobileWalletID": "254712345678",
    "mobilePhoneNumber": "+254712345678",  // E.164 format
    "pixKeyType": "CPF",  // Brazil: CPF, CNPJ, EMAIL, PHONE, EVP
    "pixKey": "123.456.789-00",
    "pixTransactionID": "E12345678901234567890123456789012",  // 32 chars
    "upiID": "user@bankname",  // India UPI Virtual Payment Address
    "upiTransactionID": "UPI1234567890123456789",
    "promptPayID": "0891234567",  // Thailand: citizen ID or phone
    "payNowID": "S1234567A",  // Singapore: NRIC or UEN
    "thaiPromptPayID": "0891234567",
    "indiaUPIID": "merchant@paytm",
    "singaporePayNowID": "91234567"
  },

  "tradeFinance": {
    "letterOfCreditNumber": "LC-2025-001234",
    "billOfLadingNumber": "BL-2025-567890",
    "billOfLadingDate": "2025-12-01",
    "hsCode": "8542.31",  // Harmonized System code
    "tradeDocumentType": "COMMERCIAL_INVOICE",  // COMMERCIAL_INVOICE, BILL_OF_LADING, LETTER_OF_CREDIT, etc.
    "incoterms": "FOB",  // FOB, CIF, EXW, DDP, etc.
    "exportLicenseNumber": "EXP-LIC-2025-1234",
    "importLicenseNumber": "IMP-LIC-2025-5678"
  }
}
*/

```

### Phase 3 DDL

```sql
-- ============================================================================
-- PHASE 3: COMPLETE GLOBAL COVERAGE (98% COVERAGE)
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 11. PAYMENTINSTRUCTION.EXTENSIONS JSON EXTENSIONS - Phase 3
-- ---------------------------------------------------------------------------

/*
PaymentInstruction.extensions JSON Schema Additions - Phase 3:

{
  "counterfeitCurrency": {
    "counterfeitCurrencyDetected": true,  // India CCR requirement
    "counterfeitCurrencyAmount": 2500.00,
    "counterfeitDenominations": [
      {"currency": "INR", "denomination": 500, "quantity": 5, "totalAmount": 2500}
    ],
    "counterfeitSerialNumbers": ["AB123456", "AB123457", "AB123458", "AB123459", "AB123460"],
    "counterfeitDetectionMethod": "UV light verification and watermark check"
  },

  "casino": {
    "casinoDisbursement": true,  // Canada requirement
    "casinoName": "Casino Name Ltd.",
    "casinoLicenseNumber": "CAN-CASINO-123456",
    "disbursementReason": "WINNINGS"  // WINNINGS, CASH_OUT, REFUND
  },

  "virtualAssets": {
    "virtualAssetFlag": true,
    "virtualAssetType": "BTC",  // BTC, ETH, USDT, USDC, XRP, etc.
    "blockchainAddress": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    "transactionHash": "0x1234567890abcdef...",
    "vasp_Name": "Coinbase Singapore",
    "vasp_RegistrationNumber": "SG-VASP-12345"
  }
}
*/

-- ---------------------------------------------------------------------------
-- 12. REGULATORYREPORT ENTITY EXTENSIONS - Terrorist Property
-- ---------------------------------------------------------------------------

ALTER TABLE cdm_silver.compliance.regulatory_report ADD COLUMNS (
  -- Terrorist Property Reporting Extensions (Canada, South Africa, others)
  terrorist_property_flag BOOLEAN COMMENT 'Terrorist property report indicator',
  terrorist_entity_name STRING COMMENT 'Listed terrorist entity name',
  terrorist_list_source STRING COMMENT 'List source: UN, domestic list, etc.',
  property_description STRING COMMENT 'Description of terrorist property',
  property_seized BOOLEAN COMMENT 'Property seized flag'
);

```

---

## TESTING AND VALIDATION

### Test Case 1: China Cross-Border Payment with Purpose Code

**Scenario:** Export payment from US to China with trade invoice

**SQL Test:**
```sql
-- Insert payment with China purpose code
INSERT INTO cdm_silver.payments.payment_instruction (
  payment_id,
  payment_method,
  instructed_amount,
  debtor_id,
  creditor_id,
  extensions
)
VALUES (
  UUID(),
  'SWIFT',
  struct(50000.00 AS amount, 'USD' AS currency),
  'debtor-uuid',
  'creditor-uuid-china',
  to_json(struct(
    struct(
      '121010' AS regulatoryPurposeCode,
      'uuid-purpose-code-121010' AS regulatoryPurposeCodeId,
      'Trade in Goods' AS purposeCategory,
      'Export' AS purposeSubCategory,
      'INV-2025-001234' AS tradeInvoiceNumber,
      '2025-12-10' AS tradeInvoiceDate,
      'Electronic components for manufacturing' AS goodsDescription,
      '8542.31' AS hsCode
    ) AS purposeCode,
    struct(
      '121010' AS chinaSubjectCode,
      'GENERAL_TRADE' AS chinaTradeTypeCode,
      'EXPORT' AS chinaTransactionNature,
      'CN-DEC-2025-001234' AS chinaCustomsDeclarationNumber
    ) AS chinaSpecific
  ))
);

-- Validate China purpose code mapping
SELECT
  pi.payment_id,
  pi.extensions:purposeCode.regulatoryPurposeCode AS china_code,
  rpc.code_description,
  rpc.category,
  rpc.iso20022_mapping,
  CASE
    WHEN rpc.requires_supporting_documents THEN 'Invoice required'
    ELSE 'No documents required'
  END AS documentation_requirement
FROM cdm_silver.payments.payment_instruction pi
JOIN cdm_silver.compliance.regulatory_purpose_code rpc
  ON pi.extensions:purposeCode.regulatoryPurposeCodeId = rpc.purpose_code_id
WHERE pi.payment_id = 'payment-uuid'
  AND rpc.jurisdiction = 'CN';

-- Expected Result:
-- china_code: 121010
-- code_description: General merchandise trade - export
-- category: Trade in Goods
-- iso20022_mapping: GDDS
-- documentation_requirement: Invoice required
```

### Test Case 2: India UPI Payment with Remittance Purpose

**Scenario:** Personal remittance from Singapore to India via UPI

**SQL Test:**
```sql
INSERT INTO cdm_silver.payments.payment_instruction (
  payment_id,
  payment_method,
  instructed_amount,
  debtor_id,
  creditor_id,
  extensions
)
VALUES (
  UUID(),
  'RTP',
  struct(1000.00 AS amount, 'SGD' AS currency),
  'debtor-uuid-singapore',
  'creditor-uuid-india',
  to_json(struct(
    struct(
      'merchant@paytm' AS upiID,
      'UPI1234567890123456789' AS upiTransactionID,
      '+91-98765-43210' AS mobilePhoneNumber
    ) AS mobileMoney,
    struct(
      'S0201' AS indiaRemittancePurpose,  -- Maintenance of close relatives
      NULL AS indiaLRSCategory,
      'CURRENT_ACCOUNT' AS indiaFEMACategory
    ) AS indiaSpecific,
    struct(
      'R05' AS relationshipToBeneficiary,  -- Other Family Member
      'uuid-relationship-R05' AS relationshipToBeneficiaryId,
      'Monthly support to family member in India' AS relationshipDescription
    ) AS relationshipToBeneficiary
  ))
);

-- Validate India purpose code and relationship
SELECT
  pi.payment_id,
  pi.extensions:indiaSpecific.indiaRemittancePurpose AS india_code,
  pi.extensions:mobileMoney.upiID AS upi_id,
  pi.extensions:relationshipToBeneficiary.relationshipToBeneficiary AS relationship_code,
  rtb.description AS relationship_description,
  rpc.code_description AS purpose_description
FROM cdm_silver.payments.payment_instruction pi
LEFT JOIN cdm_silver.compliance.regulatory_purpose_code rpc
  ON rpc.code_value = pi.extensions:indiaSpecific.indiaRemittancePurpose
  AND rpc.jurisdiction = 'IN'
LEFT JOIN cdm_silver.compliance.relationship_to_beneficiary rtb
  ON rtb.code_value = pi.extensions:relationshipToBeneficiary.relationshipToBeneficiary
WHERE pi.payment_id = 'payment-uuid';

-- Expected Result:
-- india_code: S0201
-- upi_id: merchant@paytm
-- relationship_code: R05
-- relationship_description: Other Family Member
-- purpose_description: Maintenance of close relatives
```

### Test Case 3: FATCA Reportable Account - US Person with Foreign Account

**Scenario:** Generate FATCA Form 8966 report for US person with HK account

**SQL Test:**
```sql
-- Update account with FATCA classification
UPDATE cdm_silver.payments.account
SET
  fatca_status = 'US_REPORTABLE_ACCOUNT',
  crs_reportable_account = false,
  account_holder_type = 'INDIVIDUAL',
  account_balance_for_tax_reporting = 125000.00,
  withholding_tax_rate = 0.00
WHERE account_id = 'account-uuid-hk';

-- Update party with US tax information
UPDATE cdm_silver.payments.party
SET
  us_tax_status = 'US_CITIZEN',
  fatca_classification = NULL,  -- Only for entities
  crs_reportable = false,
  tax_residencies = ARRAY(
    struct('US' AS country, 'SSN' AS tin_type, '123-45-6789' AS tin, 'CITIZENSHIP' AS tax_residency_basis, DATE('2020-01-01') AS effective_from, NULL AS effective_to)
  ),
  substantial_us_owner = false
WHERE party_id = 'party-uuid-us-person';

-- Generate FATCA report
INSERT INTO cdm_silver.compliance.regulatory_report (
  regulatory_report_id,
  report_type,
  reporting_entity,
  reporting_fi_giin,
  tax_year,
  reporting_model,
  iga_jurisdiction,
  included_transactions,
  report_status
)
SELECT
  UUID() AS regulatory_report_id,
  'FATCA_FORM_8966' AS report_type,
  'Bank of America Hong Kong Branch' AS reporting_entity,
  'ABC123.12345.ME.123' AS reporting_fi_giin,
  2025 AS tax_year,
  'MODEL1_IGA' AS reporting_model,
  'HK' AS iga_jurisdiction,
  ARRAY_AGG(pi.payment_id) AS included_transactions,
  'draft' AS report_status
FROM cdm_silver.payments.payment_instruction pi
JOIN cdm_silver.payments.account a ON pi.creditor_account_id = a.account_id
WHERE a.fatca_status = 'US_REPORTABLE_ACCOUNT'
  AND YEAR(pi.settlement_date) = 2025
GROUP BY a.account_id;

-- Validate FATCA report completeness
SELECT
  rr.regulatory_report_id,
  rr.report_type,
  rr.reporting_fi_giin,
  rr.tax_year,
  rr.reporting_model,
  COUNT(*) AS transaction_count,
  SUM(pi.instructed_amount.amount) AS total_reported_amount,
  p.us_tax_status,
  p.tax_residencies[0].tin AS us_tin,
  a.account_balance_for_tax_reporting
FROM cdm_silver.compliance.regulatory_report rr
JOIN cdm_silver.payments.payment_instruction pi ON pi.payment_id = ANY(rr.included_transactions)
JOIN cdm_silver.payments.party p ON pi.creditor_id = p.party_id
JOIN cdm_silver.payments.account a ON pi.creditor_account_id = a.account_id
WHERE rr.report_type = 'FATCA_FORM_8966'
GROUP BY rr.regulatory_report_id, rr.report_type, rr.reporting_fi_giin, rr.tax_year, rr.reporting_model, p.us_tax_status, p.tax_residencies, a.account_balance_for_tax_reporting;

-- Expected Result:
-- All FATCA fields populated including GIIN, tax year, IGA model, US TIN
```

---

## SUMMARY

### Global Coverage Achievement

| Phase | Attributes | Reference Codes | Coverage | Effort (Days) |
|-------|------------|-----------------|----------|---------------|
| **Phase 1** | 60 | 350 | 85% (2,380 / 2,800) | 25 |
| **Phase 2** | 39 | - | 95% (2,660 / 2,800) | 18 |
| **Phase 3** | 20 | - | 98% (2,744 / 2,800) | 10 |
| **TOTAL** | **119** | **375** | **98%** | **53 days** |

### ISO 20022 Compliance

- **ISO 20022 Compliant:** 32 attributes (25%)
- **ISO 20022 Extended:** 18 attributes (14%)
- **Non-ISO Extensions:** 79 attributes (61%)

**Rationale:** 75% of global regulatory requirements are jurisdiction-specific, which is expected since ISO 20022 is a messaging standard optimized for interoperability, not comprehensive regulatory reporting.

### Implementation Readiness

✅ **Phase 1-3 Complete Specifications:**
- All 119 CDM attributes specified
- 2 new reference entities designed
- 375 reference codes documented
- Complete DDL provided
- ISO 20022 compliance tracked
- Test cases provided

**Next Steps:**
1. ✅ Extend CDM logical model with all Phase 1-3 attributes
2. Update CDM physical model JSON schemas
3. Load reference data (purpose codes, relationship codes)
4. Update Bronze-to-Silver transformations
5. Validate with sample data from all 69 jurisdictions

---

**END OF DOCUMENT**

*For implementation support, contact GPS CDM Architecture Team*
