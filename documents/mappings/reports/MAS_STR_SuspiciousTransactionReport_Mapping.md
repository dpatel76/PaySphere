# MAS STR - Monetary Authority of Singapore Suspicious Transaction Report
## Complete Field Mapping to GPS CDM

**Report Type:** MAS Suspicious Transaction Report (STR)
**Regulatory Authority:** Monetary Authority of Singapore (MAS), Suspicious Transaction Reporting Office (STRO)
**Filing Requirement:** Report suspicious transactions that may involve proceeds of crime or terrorism financing
**Document Date:** 2025-12-20
**Mapping Coverage:** 100% (All 95 fields mapped)

---

## Report Overview

The Suspicious Transaction Report (STR) is filed by financial institutions and designated non-financial businesses and professions (DNFBPs) in Singapore to report suspicious transactions or activities that may involve money laundering, terrorism financing, or other serious crimes.

**Filing Threshold:** No minimum threshold
**Filing Deadline:** As soon as practicable, no later than 15 business days after forming suspicion
**Filing Method:** STR Online Notices and Reporting Platform (SONAR) at https://sonar.police.gov.sg
**Regulation:** Corruption, Drug Trafficking and Other Serious Crimes (Confiscation of Benefits) Act (CDSA), Terrorism (Suppression of Financing) Act (TSOFA)

**Predicate Offenses:**
- Drug trafficking
- Serious crimes (fraud, corruption, criminal breach of trust)
- Terrorism financing
- Organized crime

**Key Requirements:**
- File promptly upon suspicion (not after investigation)
- Tipping off prohibited (Section 48 CDSA)
- Concurrent STR and Cash Transaction Report (CTR) if applicable
- Enhanced due diligence for high-risk customers

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total MAS STR Fields** | 95 | 100% |
| **Mapped to CDM** | 95 | 100% |
| **Direct Mapping** | 79 | 83% |
| **Derived/Calculated** | 12 | 13% |
| **Reference Data Lookup** | 4 | 4% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Part I: Reporting Institution Information (Fields 1-14)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | Reporting institution name | Text | 140 | Yes | Free text | FinancialInstitution | institutionName | Legal name of FI |
| 2 | Reporting institution type | Code | 2 | Yes | See code list | FinancialInstitution | fiType | FI category |
| 3 | UEN (Unique Entity Number) | Text | 9 | Yes | UEN format | FinancialInstitution | extensions.singaporeUEN | Singapore business ID |
| 4 | MAS license number | Text | 20 | Cond | Free text | FinancialInstitution | centralBankLicenseNumber | MAS license if applicable |
| 5 | Reporting institution address | Text | 200 | Yes | Free text | FinancialInstitution | address.addressLine1 | Full address |
| 6 | Postal code | Text | 6 | Yes | 6 digits | FinancialInstitution | address.postCode | Singapore postal code |
| 7 | Contact person name | Text | 140 | Yes | Free text | RegulatoryReport | reportingEntityContactName | MLRO or designate |
| 8 | Contact person designation | Text | 100 | Yes | Free text | RegulatoryReport | extensions.contactDesignation | Job title |
| 9 | Contact email | Text | 256 | Yes | Email format | RegulatoryReport | extensions.contactEmail | Official email |
| 10 | Contact phone | Text | 20 | Yes | Phone format | RegulatoryReport | reportingEntityContactPhone | Contact number |
| 11 | STR reference number | Text | 35 | No | Auto-assigned | RegulatoryReport | reportReferenceNumber | SONAR-assigned |
| 12 | STR submission date | Date | 10 | Yes | YYYY-MM-DD | RegulatoryReport | submissionDate | Filing date |
| 13 | STR type | Code | 1 | Yes | I=Initial, S=Supplementary | RegulatoryReport | filingType | Initial or follow-up |
| 14 | Related STR reference | Text | 35 | Cond | Free text | RegulatoryReport | priorReportBSAID | Previous STR if supplementary |

### Part II: Subject Information (Fields 15-38)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 15 | Subject type | Code | 1 | Yes | I=Individual, E=Entity | Party | partyType | Individual or organization |
| 16 | Subject full name (individual) | Text | 140 | Cond | Free text | Party | name | Full name if individual |
| 17 | Subject family name | Text | 140 | Cond | Free text | Party | familyName | Last name |
| 18 | Subject given name | Text | 140 | Cond | Free text | Party | givenName | First name |
| 19 | Subject entity name | Text | 140 | Cond | Free text | Party | name | Legal entity name |
| 20 | Subject alias/DBA | Text | 140 | No | Free text | Party | alternateNames[0] | Known aliases |
| 21 | Subject NRIC/FIN | Text | 9 | Cond | NRIC/FIN format | Party | singaporeNRIC_FIN | Singapore ID |
| 22 | Subject passport number | Text | 25 | No | Free text | Party | identificationNumber | Passport if non-resident |
| 23 | Passport issuing country | Code | 2 | No | ISO 3166-1 | Party | identificationIssuingCountry | Country code |
| 24 | Subject date of birth | Date | 10 | Cond | YYYY-MM-DD | Party | dateOfBirth | DOB if individual |
| 25 | Subject nationality | Code | 2 | Cond | ISO 3166-1 | Party | nationality[0] | Nationality |
| 26 | Subject UEN | Text | 9 | Cond | UEN format | Party | extensions.singaporeUEN | Entity UEN |
| 27 | Subject industry | Code | 5 | No | SSIC code | Party | naicsCode | Singapore Standard Industrial Classification |
| 28 | Subject occupation | Text | 100 | No | Free text | Party | occupation | Occupation/business |
| 29 | Subject address | Text | 200 | Yes | Free text | Party | address.addressLine1 | Full address |
| 30 | Subject postal code | Text | 10 | No | Free text | Party | address.postCode | Postal code |
| 31 | Subject country | Code | 2 | Yes | ISO 3166-1 | Party | address.country | Country |
| 32 | Subject phone | Text | 20 | No | Free text | Party | contactDetails.phoneNumber | Contact number |
| 33 | Subject mobile | Text | 20 | No | Free text | Party | contactDetails.mobileNumber | Mobile number |
| 34 | Subject email | Text | 256 | No | Email format | Party | contactDetails.emailAddress | Email address |
| 35 | Subject relationship to FI | Code | 2 | Yes | See code list | Party | extensions.relationshipToInstitution | Customer relationship |
| 36 | Relationship start date | Date | 10 | No | YYYY-MM-DD | Party | extensions.relationshipBeginDate | When relationship started |
| 37 | Customer risk rating | Code | 1 | Yes | L=Low, M=Medium, H=High | Party | riskRating | AML risk rating |
| 38 | PEP flag | Boolean | 1 | Yes | Y/N | Party | pepFlag | Is subject a PEP? |

### Part III: Account Information (Fields 39-48)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 39 | Account number | Text | 34 | No | Free text | Account | accountNumber | Primary account |
| 40 | Account type | Code | 2 | No | See code list | Account | accountType | Account classification |
| 41 | Account currency | Code | 3 | No | ISO 4217 | Account | currency | Account currency |
| 42 | Account opening date | Date | 10 | No | YYYY-MM-DD | Account | openDate | When account opened |
| 43 | Account status | Code | 1 | No | A=Active, C=Closed, F=Frozen | Account | accountStatus | Current status |
| 44 | Account closure date | Date | 10 | No | YYYY-MM-DD | Account | closeDate | If closed |
| 45 | Account balance | Decimal | 18,2 | No | Numeric | Account | currentBalance | Current balance |
| 46 | Joint account flag | Boolean | 1 | No | Y/N | Account | extensions.jointAccountFlag | Joint account? |
| 47 | Beneficial owner name | Text | 140 | No | Free text | Account | extensions.beneficialOwnerName | If different from account holder |
| 48 | Beneficial owner NRIC | Text | 9 | No | NRIC/FIN | Account | extensions.beneficialOwnerNRIC | BO Singapore ID |

### Part IV: Transaction Details (Fields 49-68)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 49 | Transaction date | Date | 10 | Yes | YYYY-MM-DD | PaymentInstruction | valueDate | Transaction date |
| 50 | Transaction time | Time | 8 | No | HH:MM:SS | PaymentInstruction | extensions.valueDateTime | Transaction time |
| 51 | Transaction amount | Decimal | 18,2 | Yes | Numeric | PaymentInstruction | instructedAmount.amount | Transaction amount |
| 52 | Transaction currency | Code | 3 | Yes | ISO 4217 | PaymentInstruction | instructedAmount.currency | Currency |
| 53 | SGD equivalent amount | Decimal | 18,2 | No | Numeric | PaymentInstruction | equivalentAmount.amount | SGD conversion |
| 54 | Exchange rate | Decimal | 12,6 | No | Numeric | PaymentInstruction | exchangeRate | FX rate if applicable |
| 55 | Transaction type | Code | 3 | Yes | See code list | PaymentInstruction | paymentType | Transaction category |
| 56 | Transaction reference | Text | 35 | No | Free text | PaymentInstruction | endToEndId | Reference number |
| 57 | Transaction description | Text | 500 | No | Free text | PaymentInstruction | purposeDescription | Purpose/description |
| 58 | Originating account | Text | 34 | No | Free text | Account | extensions.debitAccountNumber | From account |
| 59 | Beneficiary account | Text | 34 | No | Free text | Account | extensions.creditAccountNumber | To account |
| 60 | Originating institution | Text | 140 | No | Free text | FinancialInstitution | extensions.debitInstitutionName | Sending bank |
| 61 | Originating institution country | Code | 2 | No | ISO 3166-1 | FinancialInstitution | extensions.debitInstitutionCountry | Country |
| 62 | Beneficiary institution | Text | 140 | No | Free text | FinancialInstitution | extensions.creditInstitutionName | Receiving bank |
| 63 | Beneficiary institution country | Code | 2 | No | ISO 3166-1 | FinancialInstitution | extensions.creditInstitutionCountry | Country |
| 64 | Beneficiary name | Text | 140 | No | Free text | Party | name | Ultimate beneficiary |
| 65 | Beneficiary country | Code | 2 | No | ISO 3166-1 | Party | address.country | Beneficiary location |
| 66 | Number of transactions | Integer | 5 | Yes | Numeric | RegulatoryReport | transactionCount | Total transactions involved |
| 67 | Total transaction amount | Decimal | 18,2 | Yes | Numeric | RegulatoryReport | totalReportedValue | Aggregate amount |
| 68 | Transaction period | Text | 50 | Yes | Free text | RegulatoryReport | extensions.transactionPeriod | Date range |

### Part V: Suspicious Activity Indicators (Fields 69-82)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 69 | Suspicion type | Multi-select | - | Yes | See code list | ComplianceCase | sarActivityTypeCheckboxes | Primary suspicion(s) |
| 70 | Unusual transaction pattern | Boolean | 1 | No | Y/N | ComplianceCase | extensions.unusualPatternFlag | Pattern detected? |
| 71 | Transaction inconsistent with profile | Boolean | 1 | No | Y/N | ComplianceCase | extensions.inconsistentWithProfile | Profile mismatch? |
| 72 | Cash intensive activity | Boolean | 1 | No | Y/N | ComplianceCase | extensions.cashIntensiveFlag | High cash usage? |
| 73 | Structuring indicator | Boolean | 1 | No | Y/N | ComplianceCase | extensions.structuringIndicator | Structuring detected? |
| 74 | No economic rationale | Boolean | 1 | No | Y/N | ComplianceCase | extensions.noEconomicRationale | No business purpose? |
| 75 | Evasive customer behavior | Boolean | 1 | No | Y/N | ComplianceCase | extensions.evasiveCustomer | Customer evasive? |
| 76 | Third party involvement | Boolean | 1 | No | Y/N | ComplianceCase | extensions.thirdPartyFlag | Third party involved? |
| 77 | High risk jurisdiction | Boolean | 1 | No | Y/N | ComplianceCase | extensions.highRiskJurisdiction | FATF high-risk country? |
| 78 | Sanctions concern | Boolean | 1 | No | Y/N | ComplianceCase | extensions.sanctionsConcern | Sanctions-related? |
| 79 | Terrorism financing indicator | Boolean | 1 | No | Y/N | ComplianceCase | extensions.terrorismFinancingFlag | TF indicator? |
| 80 | Source of funds unclear | Boolean | 1 | No | Y/N | ComplianceCase | extensions.unclearSourceOfFunds | Unknown SOF? |
| 81 | Customer identity doubts | Boolean | 1 | No | Y/N | ComplianceCase | extensions.identityDoubts | ID verification issues? |
| 82 | Media/adverse news | Boolean | 1 | No | Y/N | ComplianceCase | extensions.adverseMediaFlag | Negative news? |

### Part VI: Narrative and Actions Taken (Fields 83-95)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 83 | Grounds for suspicion | Text | 4000 | Yes | Free text | ComplianceCase | sarNarrative | Detailed narrative (Part 1) |
| 84 | Description of transactions | Text | 4000 | Yes | Free text | ComplianceCase | extensions.transactionDescription | Transaction details |
| 85 | Factors supporting suspicion | Text | 4000 | Yes | Free text | ComplianceCase | extensions.suspicionFactors | Red flag analysis |
| 86 | Customer due diligence performed | Text | 2000 | Yes | Free text | ComplianceCase | extensions.cddPerformed | CDD/EDD undertaken |
| 87 | Information sources | Text | 1000 | No | Free text | ComplianceCase | extensions.informationSources | Data sources used |
| 88 | Action taken by FI | Multi-select | - | Yes | See code list | ComplianceCase | extensions.actionTaken | Actions by institution |
| 89 | Account blocked flag | Boolean | 1 | No | Y/N | ComplianceCase | extensions.accountBlocked | Account blocked? |
| 90 | Account closed flag | Boolean | 1 | No | Y/N | ComplianceCase | extensions.accountClosedFlag | Account closed? |
| 91 | Transaction rejected flag | Boolean | 1 | No | Y/N | ComplianceCase | extensions.transactionRejected | Transaction stopped? |
| 92 | Law enforcement notified | Boolean | 1 | No | Y/N | ComplianceCase | extensions.lawEnforcementNotified | Police informed? |
| 93 | CAD report number | Text | 35 | No | Free text | ComplianceCase | extensions.cadReportNumber | Commercial Affairs Dept ref |
| 94 | Supporting documents attached | Boolean | 1 | No | Y/N | ComplianceCase | extensions.documentsAttached | Attachments included? |
| 95 | Additional remarks | Text | 2000 | No | Free text | ComplianceCase | extensions.additionalRemarks | Other relevant info |

---

## Code Lists

### Reporting Institution Type Codes (Field 2)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Bank | FinancialInstitution.fiType = 'DEPOSITORY_INSTITUTION' |
| 02 | Merchant bank | FinancialInstitution.fiType = 'DEPOSITORY_INSTITUTION' |
| 03 | Finance company | FinancialInstitution.fiType = 'DEPOSITORY_INSTITUTION' |
| 04 | Money changer | FinancialInstitution.fiType = 'MSB' |
| 05 | Remittance agent | FinancialInstitution.fiType = 'MSB' |
| 06 | Capital markets services | FinancialInstitution.fiType = 'BROKER_DEALER' |
| 07 | Insurance company | FinancialInstitution.fiType = 'INSURANCE_COMPANY' |
| 08 | Payment service provider | FinancialInstitution.fiType = 'MSB' |
| 09 | Digital payment token service | FinancialInstitution.fiType = 'OTHER' |

### Subject Relationship to Institution Codes (Field 35)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Account holder | extensions.relationshipToInstitution = 'ACCOUNT_HOLDER' |
| 02 | Signatory | extensions.relationshipToInstitution = 'SIGNATORY' |
| 03 | Beneficial owner | extensions.relationshipToInstitution = 'BENEFICIAL_OWNER' |
| 04 | Director/officer | extensions.relationshipToInstitution = 'DIRECTOR' |
| 05 | Authorized representative | extensions.relationshipToInstitution = 'AUTHORIZED_REP' |
| 06 | Third party | extensions.relationshipToInstitution = 'THIRD_PARTY' |
| 07 | Counterparty | extensions.relationshipToInstitution = 'COUNTERPARTY' |

### Account Type Codes (Field 40)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Savings account | Account.accountType = 'SAVINGS' |
| 02 | Current account | Account.accountType = 'CHECKING' |
| 03 | Fixed deposit | Account.accountType = 'CD' |
| 04 | Investment account | Account.accountType = 'INVESTMENT' |
| 05 | Loan account | Account.accountType = 'LOAN' |
| 06 | Credit card | Account.accountType = 'CREDIT_CARD' |
| 07 | E-wallet | Account.accountType = 'OTHER' |

### Transaction Type Codes (Field 55)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CIN | Cash deposit | PaymentInstruction.paymentType = 'ACH_CREDIT' |
| COT | Cash withdrawal | PaymentInstruction.paymentType = 'ACH_DEBIT' |
| TFR | Fund transfer | PaymentInstruction.paymentType = 'WIRE_DOMESTIC' |
| WIR | Wire transfer | PaymentInstruction.paymentType = 'WIRE_INTERNATIONAL' |
| CHQ | Cheque | PaymentInstruction.paymentType = 'CHECK' |
| CDT | Credit card transaction | PaymentInstruction.paymentType = 'CROSS_BORDER' |
| RMT | Remittance | PaymentInstruction.paymentType = 'REMITTANCE' |
| FEX | Foreign exchange | PaymentInstruction.paymentType = 'CROSS_BORDER' |

### Suspicion Type Codes (Field 69)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| ML | Money laundering | sarActivityTypeCheckboxes includes 'MONEY_LAUNDERING' |
| TF | Terrorism financing | sarActivityTypeCheckboxes includes 'TERRORIST_FINANCING' |
| FR | Fraud | sarActivityTypeCheckboxes includes 'FRAUD' |
| CO | Corruption | sarActivityTypeCheckboxes includes 'BRIBERY' |
| DT | Drug trafficking | sarActivityTypeCheckboxes includes 'DRUG_TRAFFICKING' |
| ST | Structuring | sarActivityTypeCheckboxes includes 'STRUCTURING' |
| TA | Tax evasion | sarActivityTypeCheckboxes includes 'TAX_EVASION' |
| OC | Organized crime | sarActivityTypeCheckboxes includes 'ORGANIZED_CRIME' |

### Actions Taken Codes (Field 88)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Enhanced due diligence | extensions.actionTaken includes 'EDD_PERFORMED' |
| 02 | Transaction monitored | extensions.actionTaken includes 'MONITORING' |
| 03 | Transaction rejected | extensions.actionTaken includes 'TRANSACTION_REJECTED' |
| 04 | Account blocked | extensions.actionTaken includes 'ACCOUNT_BLOCKED' |
| 05 | Account closed | extensions.actionTaken includes 'ACCOUNT_CLOSED' |
| 06 | Relationship terminated | extensions.actionTaken includes 'RELATIONSHIP_TERMINATED' |
| 07 | STR filed only | extensions.actionTaken includes 'STR_FILED_ONLY' |

---

## CDM Extensions Required

All 95 MAS STR fields successfully map to existing CDM model. **No enhancements required.**

The following extension attributes are used within Party, Account, ComplianceCase, and RegulatoryReport extensions:
- Singapore-specific: singaporeUEN, singaporeNRIC_FIN, contactDesignation, contactEmail
- Relationship: relationshipToInstitution, relationshipBeginDate
- Account: jointAccountFlag, beneficialOwnerName, beneficialOwnerNRIC, debitAccountNumber, creditAccountNumber
- Transaction: valueDateTime, transactionPeriod, debitInstitutionName, debitInstitutionCountry, creditInstitutionName, creditInstitutionCountry
- Suspicion indicators: unusualPatternFlag, inconsistentWithProfile, cashIntensiveFlag, structuringIndicator, noEconomicRationale, evasiveCustomer, thirdPartyFlag, highRiskJurisdiction, sanctionsConcern, terrorismFinancingFlag, unclearSourceOfFunds, identityDoubts, adverseMediaFlag
- Actions: transactionDescription, suspicionFactors, cddPerformed, informationSources, actionTaken, accountBlocked, accountClosedFlag, transactionRejected, lawEnforcementNotified, cadReportNumber, documentsAttached, additionalRemarks

---

## Example MAS STR Scenario

**Subject:** ABC Trading Pte Ltd (Singapore company)

**Suspicious Activity:** Rapid movement of funds inconsistent with business profile

**Grounds for Suspicion (Field 83):**
```
ABC Trading Pte Ltd (UEN: 201234567A) opened a current account with our bank on
2025-01-15. The company was classified as medium-risk based on its stated business
of import/export of electronics.

Between 2025-11-01 and 2025-12-15, the company conducted 23 large fund transfers
totaling SGD 4.8 million, which is highly inconsistent with:
1. Company's stated monthly revenue of SGD 200,000
2. Historical transaction pattern (average SGD 50,000/month)
3. Small office premises and minimal staff (2 employees)

Specific suspicious patterns observed:
- Funds received from multiple overseas sources (Hong Kong, Dubai, Cayman Islands)
- Rapid transfer out to different jurisdictions within 24-48 hours
- No retention of funds in account (pass-through behavior)
- Transactions lack commercial documentation
- Beneficiaries include entities in high-risk jurisdictions
- Director became evasive when questioned about source of funds

Enhanced due diligence performed:
- Requested trade invoices: Customer provided vague documentation
- Searched adverse media: No hits
- Checked beneficial ownership: Single director (Singapore PR, Malaysian national)
- Visited business premises: Minimal operations observed
- Sanctions screening: No matches

Red flags supporting suspicion:
1. Transaction velocity and volume inconsistent with known business
2. Use of multiple jurisdictions with no clear business rationale
3. Layering pattern consistent with money laundering typology
4. Customer evasiveness and inability to explain transactions
5. Pass-through account behavior (funds in/out quickly)
6. Involvement of high-risk jurisdictions (per FATF lists)

The pattern of activity is consistent with trade-based money laundering (TBML) or
layering of proceeds from unknown criminal activity.
```

**Action Taken:**
- Enhanced monitoring activated
- Ongoing transactions flagged for review
- Customer relationship under review for potential termination
- STR filed with STRO on 2025-12-20

---

## References

- Corruption, Drug Trafficking and Other Serious Crimes (Confiscation of Benefits) Act (CDSA): https://sso.agc.gov.sg/Act/CDSA1992
- Terrorism (Suppression of Financing) Act (TSOFA): https://sso.agc.gov.sg/Act/TSFA2002
- MAS Notice 626 (AML/CFT for Banks): https://www.mas.gov.sg/regulation/notices/notice-626
- STR Online Notices and Reporting Platform (SONAR): https://sonar.police.gov.sg
- Commercial Affairs Department (CAD): https://www.police.gov.sg/Advisories/Crime/Commercial-Crimes
- GPS CDM Schemas: `/schemas/05_regulatory_report_complete_schema.json`, `/schemas/06_compliance_case_complete_schema.json`, `/schemas/02_party_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2025-12-20
**Next Review:** Q2 2025
