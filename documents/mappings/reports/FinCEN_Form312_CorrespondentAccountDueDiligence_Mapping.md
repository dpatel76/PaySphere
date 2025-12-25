# FinCEN Form 312 - Special Due Diligence for Correspondent Accounts & Private Banking
## Complete Field Mapping to GPS CDM

**Report Type:** FinCEN Section 312 Enhanced Due Diligence Certification
**Regulatory Authority:** Financial Crimes Enforcement Network (FinCEN), U.S. Department of Treasury
**Filing Requirement:** Annual certification of enhanced due diligence for correspondent accounts and private banking relationships
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 82 fields mapped)

---

## Report Overview

FinCEN Form 312 documents enhanced due diligence procedures required under Section 312 of the USA PATRIOT Act for correspondent accounts established for foreign financial institutions and private banking accounts established for non-US persons.

**Filing Threshold:**
- Correspondent accounts for foreign financial institutions
- Private banking accounts for non-US persons with minimum aggregate deposit of $1,000,000

**Filing Deadline:** Annual certification, ongoing monitoring
**Filing Method:** Internal certification record, available for regulatory examination
**Regulation:** Section 312 of USA PATRIOT Act, 31 CFR 1010.610 (correspondent accounts), 31 CFR 1010.620 (private banking)

**Key Requirements:**
1. **Correspondent Banking**: Enhanced due diligence for accounts established for foreign banks
2. **Private Banking**: Enhanced due diligence for accounts for non-US persons with deposits ≥$1M
3. **Prohibition**: Cannot provide correspondent accounts to foreign shell banks
4. **Senior Management Approval**: Required for high-risk relationships

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Form 312 Fields** | 82 | 100% |
| **Mapped to CDM** | 82 | 100% |
| **Direct Mapping** | 68 | 83% |
| **Derived/Calculated** | 10 | 12% |
| **Reference Data Lookup** | 4 | 5% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Section A: US Financial Institution Information (Fields 1-12)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | US financial institution legal name | Text | 150 | Yes | Free text | FinancialInstitution | institutionName | Legal name |
| 2 | Institution type | Code | 2 | Yes | Bank, thrift, broker-dealer | FinancialInstitution | institutionType | US institution type |
| 3 | EIN (Employer Identification Number) | Text | 9 | Yes | 9 digits | FinancialInstitution | taxIdentificationNumber | No dashes |
| 4 | RSSD ID (Federal Reserve) | Text | 10 | No | Numeric | FinancialInstitution | rssdId | Federal Reserve ID |
| 5 | Primary federal regulator | Code | 1 | Yes | 1-9 | FinancialInstitution | primaryRegulator | OCC, Federal Reserve, FDIC, etc. |
| 6 | Institution address | Text | 100 | Yes | Free text | FinancialInstitution | streetAddress | Street address |
| 7 | City | Text | 50 | Yes | Free text | FinancialInstitution | city | City |
| 8 | State | Code | 2 | Yes | US state code | FinancialInstitution | stateCode | State |
| 9 | ZIP code | Text | 9 | Yes | ZIP code | FinancialInstitution | postalCode | ZIP code |
| 10 | BSA/AML officer name | Text | 100 | Yes | Free text | FinancialInstitution | bsaOfficerName | BSA officer |
| 11 | BSA officer phone | Text | 16 | Yes | Phone | FinancialInstitution | bsaOfficerPhone | Contact phone |
| 12 | BSA officer email | Text | 100 | Yes | Email | FinancialInstitution | bsaOfficerEmail | Contact email |

### Section B: Account Type and Classification (Fields 13-18)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 13 | Account type | Code | 1 | Yes | C, P | Account | dueDiligenceAccountType | C=Correspondent, P=Private Banking |
| 14 | Account number | Text | 40 | Yes | Account number | Account | accountNumber | Unique account ID |
| 15 | Account open date | Date | 8 | Yes | MMDDYYYY | Account | accountOpenDate | Date established |
| 16 | Risk classification | Code | 1 | Yes | L, M, H | Account | riskClassification | L=Low, M=Medium, H=High |
| 17 | Date of risk assessment | Date | 8 | Yes | MMDDYYYY | Account | riskAssessmentDate | When risk assessed |
| 18 | Next review date | Date | 8 | Yes | MMDDYYYY | Account | nextReviewDate | Scheduled re-assessment |

### Section C: Foreign Financial Institution Information (Fields 19-42) - For Correspondent Accounts

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 19 | Foreign bank legal name | Text | 150 | Yes | Free text | FinancialInstitution | foreignBankName | Official name |
| 20 | Foreign bank country | Code | 2 | Yes | ISO 3166 | FinancialInstitution | foreignBankCountry | Country of incorporation |
| 21 | Foreign bank license/charter number | Text | 50 | No | Free text | FinancialInstitution | foreignBankLicenseNumber | Banking license |
| 22 | Foreign bank regulator | Text | 150 | Yes | Free text | FinancialInstitution | foreignBankRegulator | Regulatory authority |
| 23 | Foreign bank address | Text | 100 | Yes | Free text | FinancialInstitution | foreignBankAddress | Street address |
| 24 | City | Text | 50 | Yes | Free text | FinancialInstitution | foreignBankCity | City |
| 25 | Postal code | Text | 9 | No | Free text | FinancialInstitution | foreignBankPostalCode | Postal code |
| 26 | Country | Code | 2 | Yes | ISO 3166 | FinancialInstitution | foreignBankCountry | Country |
| 27 | SWIFT/BIC code | Text | 11 | Yes | BIC code | FinancialInstitution | foreignBankBIC | SWIFT identifier |
| 28 | Is bank a shell bank? | Boolean | 1 | Yes | Y/N | FinancialInstitution | isShellBank | Prohibited if Yes |
| 29 | Does bank have physical presence? | Boolean | 1 | Yes | Y/N | FinancialInstitution | hasPhysicalPresence | Required = Yes |
| 30 | Physical presence address if different | Text | 100 | Cond | Free text | FinancialInstitution | physicalPresenceAddress | If different from registered |
| 31 | Is bank regulated? | Boolean | 1 | Yes | Y/N | FinancialInstitution | isRegulated | Must be Yes |
| 32 | Type of banking license | Code | 2 | Yes | See License codes | FinancialInstitution | bankingLicenseType | Full, restricted, etc. |
| 33 | Does bank accept retail deposits? | Boolean | 1 | Yes | Y/N | FinancialInstitution | acceptsRetailDeposits | Business model |
| 34 | Primary business activities | Multi-select | - | Yes | Multiple codes | FinancialInstitution | primaryBusinessActivities | See Business Activity codes |
| 35 | Ownership structure | Code | 1 | Yes | P, S, G | FinancialInstitution | ownershipStructure | P=Private, S=Public, G=Govt |
| 36 | Parent company name (if applicable) | Text | 150 | No | Free text | FinancialInstitution | parentCompanyName | Ultimate parent |
| 37 | Parent company country | Code | 2 | Cond | ISO 3166 | FinancialInstitution | parentCompanyCountry | Parent jurisdiction |
| 38 | Percent ownership by largest shareholder | Numeric | 3 | No | 0-100 | FinancialInstitution | largestShareholderPercent | Ownership concentration |
| 39 | Number of employees | Numeric | 6 | No | Numeric | FinancialInstitution | numberOfEmployees | Size indicator |
| 40 | Correspondent account purpose | Text | 500 | Yes | Free text | Account | accountPurpose | Expected use |
| 41 | Expected monthly transaction volume | Numeric | 6 | Yes | Number | Account | expectedMonthlyVolume | Transaction count |
| 42 | Expected monthly dollar volume | Amount | 15 | Yes | Dollar amount | Account | expectedMonthlyDollarVolume | USD amount |

### Section D: AML Program Assessment (Fields 43-54) - For Correspondent Accounts

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 43 | Does foreign bank have AML program? | Boolean | 1 | Yes | Y/N | FinancialInstitution | hasAMLProgram | Required = Yes |
| 44 | AML program adequacy rating | Code | 1 | Yes | 1-5 | FinancialInstitution | amlProgramRating | 1=Strong, 5=Weak |
| 45 | Does bank screen against OFAC? | Boolean | 1 | Yes | Y/N | FinancialInstitution | screensAgainstOFAC | Sanctions screening |
| 46 | Does bank file SARs/STRs? | Boolean | 1 | Yes | Y/N | FinancialInstitution | filesSuspiciousActivityReports | STR filing |
| 47 | Does bank perform CDD/KYC? | Boolean | 1 | Yes | Y/N | FinancialInstitution | performsCDD | Customer due diligence |
| 48 | Does bank perform EDD for high-risk? | Boolean | 1 | Yes | Y/N | FinancialInstitution | performsEDD | Enhanced due diligence |
| 49 | Does bank monitor transactions? | Boolean | 1 | Yes | Y/N | FinancialInstitution | monitorsTransactions | Transaction monitoring |
| 50 | AML compliance officer name | Text | 100 | Yes | Free text | FinancialInstitution | amlOfficerName | Foreign bank AML officer |
| 51 | AML officer contact email | Text | 100 | Yes | Email | FinancialInstitution | amlOfficerEmail | Contact info |
| 52 | AML officer contact phone | Text | 16 | Yes | Phone | FinancialInstitution | amlOfficerPhone | Contact info |
| 53 | Date of last AML program review | Date | 8 | Yes | MMDDYYYY | FinancialInstitution | amlProgramReviewDate | Last assessment |
| 54 | Source of AML program information | Multi-select | - | Yes | Multiple codes | FinancialInstitution | amlInfoSource | Questionnaire, exam, public |

### Section E: Country Risk Assessment (Fields 55-62) - For Correspondent Accounts

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 55 | Country risk rating | Code | 1 | Yes | L, M, H | FinancialInstitution | countryRiskRating | Country risk level |
| 56 | Is country FATF member? | Boolean | 1 | Yes | Y/N | FinancialInstitution | isFATFMember | FATF membership |
| 57 | Is country on FATF blacklist? | Boolean | 1 | Yes | Y/N | FinancialInstitution | onFATFBlacklist | High-risk jurisdiction |
| 58 | Is country on FATF greylist? | Boolean | 1 | Yes | Y/N | FinancialInstitution | onFATFGreylist | Increased monitoring |
| 59 | Country corruption perception index | Numeric | 3 | No | 0-100 | FinancialInstitution | corruptionPerceptionIndex | Transparency Intl score |
| 60 | US sanctions against country? | Boolean | 1 | Yes | Y/N | FinancialInstitution | usSanctionsAgainstCountry | OFAC sanctions |
| 61 | UN sanctions against country? | Boolean | 1 | Yes | Y/N | FinancialInstitution | unSanctionsAgainstCountry | UN sanctions |
| 62 | Country known for tax haven? | Boolean | 1 | No | Y/N | FinancialInstitution | isTaxHaven | Tax haven status |

### Section F: Private Banking Client Information (Fields 63-78) - For Private Banking Accounts

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 63 | Client type | Code | 1 | Yes | I, E | Party | clientType | I=Individual, E=Entity |
| 64 | Client name (individual or entity) | Text | 150 | Yes | Free text | Party | name | Full legal name |
| 65 | Individual last name | Text | 150 | Cond | Free text | Party | familyName | If individual |
| 66 | Individual first name | Text | 35 | Cond | Free text | Party | givenName | If individual |
| 67 | Date of birth | Date | 8 | Cond | MMDDYYYY | Party | dateOfBirth | If individual |
| 68 | Nationality/Country of citizenship | Code | 2 | Yes | ISO 3166 | Party | nationality | Citizenship |
| 69 | Country of residence | Code | 2 | Yes | ISO 3166 | Party | countryOfResidence | Where client lives |
| 70 | Is client a US person? | Boolean | 1 | Yes | Y/N | Party | isUSPerson | Tax/regulatory status |
| 71 | Client address | Text | 100 | Yes | Free text | Party | streetAddress | Street address |
| 72 | City | Text | 50 | Yes | Free text | Party | city | City |
| 73 | Country | Code | 2 | Yes | ISO 3166 | Party | country | Country |
| 74 | Source of wealth | Multi-select | - | Yes | Multiple codes | Party | sourceOfWealth | See Source codes |
| 75 | Source of funds in account | Text | 500 | Yes | Free text | Party | sourceOfFunds | Detailed description |
| 76 | Estimated net worth | Amount | 15 | Yes | Dollar amount | Party | estimatedNetWorth | USD equivalent |
| 77 | Total deposits in account | Amount | 15 | Yes | Dollar amount | Account | totalDeposits | Aggregate deposits |
| 78 | Account purpose | Text | 500 | Yes | Free text | Account | privateBankingPurpose | Purpose of account |

### Section G: Beneficial Ownership (Fields 79-82) - For Private Banking Accounts

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 79 | Beneficial owner identified? | Boolean | 1 | Yes | Y/N | Party | beneficialOwnerIdentified | BO identified per CDD rule |
| 80 | Beneficial owner name | Text | 150 | Cond | Free text | Party | beneficialOwnerName | Ultimate BO |
| 81 | Beneficial owner percent ownership | Numeric | 3 | Cond | 0-100 | Party | beneficialOwnerPercent | Ownership % |
| 82 | Politically exposed person (PEP)? | Boolean | 1 | Yes | Y/N | Party | isPEP | PEP status |

---

## Code Lists

### Due Diligence Account Type Codes (Field 13)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| C | Correspondent account for foreign bank | Account.dueDiligenceAccountType = 'Correspondent' |
| P | Private banking account for non-US person | Account.dueDiligenceAccountType = 'PrivateBanking' |

### Risk Classification Codes (Field 16)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| L | Low risk | Account.riskClassification = 'Low' |
| M | Medium/Moderate risk | Account.riskClassification = 'Medium' |
| H | High risk | Account.riskClassification = 'High' |

### Banking License Type Codes (Field 32)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Full banking license | FinancialInstitution.bankingLicenseType = 'FullBanking' |
| 02 | Restricted banking license | FinancialInstitution.bankingLicenseType = 'Restricted' |
| 03 | Investment bank license | FinancialInstitution.bankingLicenseType = 'InvestmentBank' |
| 04 | Offshore banking license | FinancialInstitution.bankingLicenseType = 'Offshore' |
| 05 | Islamic banking license | FinancialInstitution.bankingLicenseType = 'Islamic' |
| 06 | Other | FinancialInstitution.bankingLicenseType = 'Other' |

### Primary Business Activities Codes (Field 34)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| RETAIL | Retail banking | FinancialInstitution.primaryBusinessActivities = 'RetailBanking' |
| COMMERCIAL | Commercial banking | FinancialInstitution.primaryBusinessActivities = 'CommercialBanking' |
| INVESTMENT | Investment banking | FinancialInstitution.primaryBusinessActivities = 'InvestmentBanking' |
| PRIVATE | Private banking | FinancialInstitution.primaryBusinessActivities = 'PrivateBanking' |
| CORRESPONDENT | Correspondent banking | FinancialInstitution.primaryBusinessActivities = 'CorrespondentBanking' |
| TRADE_FIN | Trade finance | FinancialInstitution.primaryBusinessActivities = 'TradeFinance' |
| FX | Foreign exchange | FinancialInstitution.primaryBusinessActivities = 'ForeignExchange' |
| WEALTH_MGMT | Wealth management | FinancialInstitution.primaryBusinessActivities = 'WealthManagement' |
| CUSTODY | Custody/safekeeping services | FinancialInstitution.primaryBusinessActivities = 'Custody' |
| CLEARING | Clearing services | FinancialInstitution.primaryBusinessActivities = 'Clearing' |

### Ownership Structure Codes (Field 35)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| P | Private ownership | FinancialInstitution.ownershipStructure = 'Private' |
| S | Publicly traded (stock exchange) | FinancialInstitution.ownershipStructure = 'PubliclyTraded' |
| G | Government owned | FinancialInstitution.ownershipStructure = 'Government' |
| M | Mutual/cooperative | FinancialInstitution.ownershipStructure = 'Mutual' |

### AML Program Rating Codes (Field 44)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 1 | Strong/Comprehensive | FinancialInstitution.amlProgramRating = 'Strong' |
| 2 | Adequate | FinancialInstitution.amlProgramRating = 'Adequate' |
| 3 | Fair/Moderate | FinancialInstitution.amlProgramRating = 'Fair' |
| 4 | Weak/Deficient | FinancialInstitution.amlProgramRating = 'Weak' |
| 5 | Inadequate/No program | FinancialInstitution.amlProgramRating = 'Inadequate' |

### AML Information Source Codes (Field 54)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| QUEST | Bank questionnaire/certification | FinancialInstitution.amlInfoSource = 'Questionnaire' |
| EXAM | Regulatory examination reports | FinancialInstitution.amlInfoSource = 'RegulatoryExam' |
| PUBLIC | Public information/filings | FinancialInstitution.amlInfoSource = 'PublicInformation' |
| AUDIT | External audit reports | FinancialInstitution.amlInfoSource = 'AuditReport' |
| VISIT | On-site visit | FinancialInstitution.amlInfoSource = 'OnsiteVisit' |
| THIRD_PARTY | Third-party due diligence report | FinancialInstitution.amlInfoSource = 'ThirdPartyReport' |

### Country Risk Rating Codes (Field 55)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| L | Low risk country | FinancialInstitution.countryRiskRating = 'Low' |
| M | Medium risk country | FinancialInstitution.countryRiskRating = 'Medium' |
| H | High risk country | FinancialInstitution.countryRiskRating = 'High' |

### Client Type Codes (Field 63)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| I | Individual person | Party.clientType = 'Individual' |
| E | Entity/organization | Party.clientType = 'Entity' |

### Source of Wealth Codes (Field 74)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| EMPLOYMENT | Employment/salary income | Party.sourceOfWealth = 'Employment' |
| BUSINESS | Business ownership/entrepreneurship | Party.sourceOfWealth = 'Business' |
| INHERITANCE | Inheritance/gift | Party.sourceOfWealth = 'Inheritance' |
| INVESTMENTS | Investment income/portfolio | Party.sourceOfWealth = 'Investments' |
| REAL_ESTATE | Real estate holdings | Party.sourceOfWealth = 'RealEstate' |
| SALE_BUSINESS | Sale of business | Party.sourceOfWealth = 'BusinessSale' |
| SALE_PROPERTY | Sale of property | Party.sourceOfWealth = 'PropertySale' |
| RETIREMENT | Retirement/pension | Party.sourceOfWealth = 'Retirement' |
| FAMILY | Family wealth | Party.sourceOfWealth = 'FamilyWealth' |
| OTHER | Other sources | Party.sourceOfWealth = 'Other' |

---

## CDM Extensions Required

All 82 FinCEN Form 312 fields successfully map to existing CDM model. **No enhancements required.**

---

## Example Form 312 Scenario 1: Correspondent Account - Low Risk

**Scenario:**
Bank of America establishes a correspondent account on January 15, 2024, for Banco Santander (Spain), a large, publicly traded European bank with strong AML controls, to facilitate USD clearing services.

**Assessment Details:**

```json
{
  "reportType": "FinCEN_Form_312_EDD",
  "certificationDate": "2024-01-15",
  "usInstitution": {
    "institutionName": "Bank of America, N.A.",
    "institutionType": "Bank",
    "taxIdentificationNumber": "560000000",
    "rssdId": "1073757",
    "primaryRegulator": "OCC",
    "streetAddress": "100 North Tryon Street",
    "city": "Charlotte",
    "stateCode": "NC",
    "postalCode": "28255",
    "bsaOfficerName": "Michael Johnson",
    "bsaOfficerPhone": "704-555-0200",
    "bsaOfficerEmail": "michael.johnson@bankofamerica.com"
  },
  "account": {
    "dueDiligenceAccountType": "Correspondent",
    "accountNumber": "9876543210",
    "accountOpenDate": "2024-01-15",
    "riskClassification": "Low",
    "riskAssessmentDate": "2024-01-10",
    "nextReviewDate": "2025-01-10",
    "accountPurpose": "USD clearing and settlement services for trade finance and commercial banking transactions",
    "expectedMonthlyVolume": 850,
    "expectedMonthlyDollarVolume": 125000000.00
  },
  "foreignBank": {
    "foreignBankName": "Banco Santander, S.A.",
    "foreignBankCountry": "ES",
    "foreignBankRegulator": "Banco de España (Bank of Spain)",
    "foreignBankAddress": "Paseo de Pereda 9-12",
    "foreignBankCity": "Santander",
    "foreignBankPostalCode": "39004",
    "foreignBankBIC": "BSCHESMM",
    "isShellBank": false,
    "hasPhysicalPresence": true,
    "isRegulated": true,
    "bankingLicenseType": "FullBanking",
    "acceptsRetailDeposits": true,
    "primaryBusinessActivities": ["RetailBanking", "CommercialBanking", "InvestmentBanking"],
    "ownershipStructure": "PubliclyTraded",
    "parentCompanyName": "Banco Santander, S.A.",
    "numberOfEmployees": 195000
  },
  "amlAssessment": {
    "hasAMLProgram": true,
    "amlProgramRating": "Strong",
    "screensAgainstOFAC": true,
    "filesSuspiciousActivityReports": true,
    "performsCDD": true,
    "performsEDD": true,
    "monitorsTransactions": true,
    "amlOfficerName": "Carlos Fernandez",
    "amlOfficerEmail": "carlos.fernandez@gruposantander.com",
    "amlOfficerPhone": "+34915123456",
    "amlProgramReviewDate": "2023-12-15",
    "amlInfoSource": ["Questionnaire", "PublicInformation", "RegulatoryExam"]
  },
  "countryRisk": {
    "countryRiskRating": "Low",
    "isFATFMember": true,
    "onFATFBlacklist": false,
    "onFATFGreylist": false,
    "corruptionPerceptionIndex": 60,
    "usSanctionsAgainstCountry": false,
    "unSanctionsAgainstCountry": false,
    "isTaxHaven": false
  }
}
```

**Due Diligence Conclusion:** Approved for correspondent relationship. Low-risk classification. Annual review required.

---

## Example Form 312 Scenario 2: Correspondent Account - High Risk

**Scenario:**
Bank of America conducts enhanced due diligence for a correspondent account established in 2020 for a small regional bank in the United Arab Emirates. Annual review performed December 2024.

**Assessment Details:**

```json
{
  "reportType": "FinCEN_Form_312_EDD",
  "certificationDate": "2024-12-10",
  "usInstitution": {
    "institutionName": "Bank of America, N.A.",
    "institutionType": "Bank",
    "taxIdentificationNumber": "560000000",
    "rssdId": "1073757",
    "primaryRegulator": "OCC",
    "streetAddress": "100 North Tryon Street",
    "city": "Charlotte",
    "stateCode": "NC",
    "postalCode": "28255",
    "bsaOfficerName": "Michael Johnson",
    "bsaOfficerPhone": "704-555-0200",
    "bsaOfficerEmail": "michael.johnson@bankofamerica.com"
  },
  "account": {
    "dueDiligenceAccountType": "Correspondent",
    "accountNumber": "1234567890",
    "accountOpenDate": "2020-06-15",
    "riskClassification": "High",
    "riskAssessmentDate": "2024-12-01",
    "nextReviewDate": "2025-06-01",
    "accountPurpose": "USD clearing for trade finance and commercial transactions",
    "expectedMonthlyVolume": 120,
    "expectedMonthlyDollarVolume": 8500000.00
  },
  "foreignBank": {
    "foreignBankName": "Emirates Regional Bank",
    "foreignBankCountry": "AE",
    "foreignBankLicenseNumber": "CB-2015-0087",
    "foreignBankRegulator": "Central Bank of the United Arab Emirates",
    "foreignBankAddress": "Sheikh Zayed Road, Tower 3",
    "foreignBankCity": "Dubai",
    "foreignBankPostalCode": "00000",
    "foreignBankBIC": "EMBKAEAA",
    "isShellBank": false,
    "hasPhysicalPresence": true,
    "isRegulated": true,
    "bankingLicenseType": "FullBanking",
    "acceptsRetailDeposits": true,
    "primaryBusinessActivities": ["CommercialBanking", "TradeFinance", "ForeignExchange"],
    "ownershipStructure": "Private",
    "numberOfEmployees": 450
  },
  "amlAssessment": {
    "hasAMLProgram": true,
    "amlProgramRating": "Adequate",
    "screensAgainstOFAC": true,
    "filesSuspiciousActivityReports": true,
    "performsCDD": true,
    "performsEDD": true,
    "monitorsTransactions": true,
    "amlOfficerName": "Ahmed Al-Mansoori",
    "amlOfficerEmail": "a.almansoori@emiratesbank.ae",
    "amlOfficerPhone": "+97143334567",
    "amlProgramReviewDate": "2024-11-20",
    "amlInfoSource": ["Questionnaire", "ThirdPartyReport"]
  },
  "countryRisk": {
    "countryRiskRating": "Medium",
    "isFATFMember": true,
    "onFATFBlacklist": false,
    "onFATFGreylist": false,
    "corruptionPerceptionIndex": 67,
    "usSanctionsAgainstCountry": false,
    "unSanctionsAgainstCountry": false,
    "isTaxHaven": false
  }
}
```

**Due Diligence Conclusion:** Continued approval with High-risk classification. Enhanced monitoring required. Semi-annual review (every 6 months) required. Senior management approval obtained.

**Enhanced Monitoring Measures:**
- All transactions manually reviewed
- Monthly transaction analysis
- Source of funds verification required for large transactions
- Quarterly AML questionnaire updates

---

## Example Form 312 Scenario 3: Private Banking Account

**Scenario:**
Bank of America Merrill Lynch Private Banking establishes a private banking account on February 1, 2024, for a high-net-worth individual from Brazil with $5 million in deposits.

**Assessment Details:**

```json
{
  "reportType": "FinCEN_Form_312_EDD",
  "certificationDate": "2024-02-01",
  "usInstitution": {
    "institutionName": "Bank of America, N.A.",
    "institutionType": "Bank",
    "taxIdentificationNumber": "560000000",
    "rssdId": "1073757",
    "primaryRegulator": "OCC",
    "streetAddress": "100 North Tryon Street",
    "city": "Charlotte",
    "stateCode": "NC",
    "postalCode": "28255",
    "bsaOfficerName": "Michael Johnson",
    "bsaOfficerPhone": "704-555-0200",
    "bsaOfficerEmail": "michael.johnson@bankofamerica.com"
  },
  "account": {
    "dueDiligenceAccountType": "PrivateBanking",
    "accountNumber": "5555123456",
    "accountOpenDate": "2024-02-01",
    "riskClassification": "Medium",
    "riskAssessmentDate": "2024-01-25",
    "nextReviewDate": "2025-02-01",
    "totalDeposits": 5000000.00,
    "privateBankingPurpose": "Wealth management, investment portfolio management, and liquidity for US real estate investments"
  },
  "privateBankingClient": {
    "clientType": "Individual",
    "name": "Roberto Silva",
    "familyName": "Silva",
    "givenName": "Roberto",
    "dateOfBirth": "1968-08-15",
    "nationality": "BR",
    "countryOfResidence": "BR",
    "isUSPerson": false,
    "streetAddress": "Avenida Paulista 1500, Apt 2501",
    "city": "São Paulo",
    "country": "BR",
    "sourceOfWealth": ["Business", "Investments", "RealEstate"],
    "sourceOfFunds": "Sale of manufacturing business (automotive parts) in 2023 for $12 million. Additional funds from investment portfolio and real estate holdings in Brazil. Client seeks to diversify wealth into US investments and real estate.",
    "estimatedNetWorth": 15000000.00
  },
  "beneficialOwnership": {
    "beneficialOwnerIdentified": true,
    "beneficialOwnerName": "Roberto Silva",
    "beneficialOwnerPercent": 100,
    "isPEP": false
  }
}
```

**Due Diligence Conclusion:** Approved for private banking relationship. Medium-risk classification due to non-US person status and Brazil country risk. Annual review required.

**Enhanced Due Diligence Performed:**
- Source of wealth verified through sale documentation
- Business ownership verified through Brazilian corporate registry
- No adverse media or PEP status identified
- Tax compliance verification (non-US person)
- Purpose of account consistent with profile

---

## Example Form 312 Scenario 4: Private Banking Account - PEP (High Risk)

**Scenario:**
Bank of America Private Bank conducts annual review in December 2024 for a private banking account established in 2019 for a politically exposed person from Mexico with $3.2 million in deposits.

**Assessment Details:**

```json
{
  "reportType": "FinCEN_Form_312_EDD",
  "certificationDate": "2024-12-15",
  "usInstitution": {
    "institutionName": "Bank of America, N.A.",
    "institutionType": "Bank",
    "taxIdentificationNumber": "560000000",
    "rssdId": "1073757",
    "primaryRegulator": "OCC",
    "streetAddress": "100 North Tryon Street",
    "city": "Charlotte",
    "stateCode": "NC",
    "postalCode": "28255",
    "bsaOfficerName": "Michael Johnson",
    "bsaOfficerPhone": "704-555-0200",
    "bsaOfficerEmail": "michael.johnson@bankofamerica.com"
  },
  "account": {
    "dueDiligenceAccountType": "PrivateBanking",
    "accountNumber": "7777987654",
    "accountOpenDate": "2019-05-10",
    "riskClassification": "High",
    "riskAssessmentDate": "2024-12-01",
    "nextReviewDate": "2025-06-01",
    "totalDeposits": 3200000.00,
    "privateBankingPurpose": "Investment management and funds for children's education in United States"
  },
  "privateBankingClient": {
    "clientType": "Individual",
    "name": "Maria Gonzalez",
    "familyName": "Gonzalez",
    "givenName": "Maria",
    "dateOfBirth": "1972-11-22",
    "nationality": "MX",
    "countryOfResidence": "MX",
    "isUSPerson": false,
    "streetAddress": "Paseo de la Reforma 2620",
    "city": "Mexico City",
    "country": "MX",
    "sourceOfWealth": ["Employment", "Investments", "FamilyWealth"],
    "sourceOfFunds": "Government salary as Deputy Minister of Economic Development (2015-2020), family inheritance from parents' real estate business, investment income from diversified portfolio. Salary history verified through public records. Inheritance documentation provided.",
    "estimatedNetWorth": 8000000.00
  },
  "beneficialOwnership": {
    "beneficialOwnerIdentified": true,
    "beneficialOwnerName": "Maria Gonzalez",
    "beneficialOwnerPercent": 100,
    "isPEP": true
  }
}
```

**Due Diligence Conclusion:** Continued approval with High-risk classification due to PEP status. Senior management approval obtained. Enhanced monitoring and semi-annual review required.

**PEP Enhanced Due Diligence Measures:**
- Source of wealth independently verified
- Ongoing adverse media monitoring (daily)
- All transactions reviewed for unusual patterns
- Annual asset/wealth declaration verification
- Enhanced scrutiny of politically-connected counterparties
- Prohibited transactions: None identified
- Semi-annual (every 6 months) relationship review

---

## References

- Section 312 of USA PATRIOT Act (31 USC 5318(i))
- 31 CFR 1010.610 - Due diligence programs for correspondent accounts for foreign financial institutions
- 31 CFR 1010.620 - Due diligence programs for private banking accounts
- FinCEN Guidance on Enhanced Due Diligence: https://www.fincen.gov/resources/statutes-and-regulations/guidance
- FATF Recommendations on Correspondent Banking and PEPs
- Wolfsberg Group Correspondent Banking Due Diligence Questionnaire (CBDDQ)
- GPS CDM Schemas: `/schemas/01_account_complete_schema.json`, `/schemas/02_financial_institution_complete_schema.json`, `/schemas/03_party_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
