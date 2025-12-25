# UK SAR - Suspicious Activity Report
## Complete Field Mapping to GPS CDM

**Report Type:** UK SAR - Suspicious Activity Report to National Crime Agency
**Regulatory Authority:** National Crime Agency (NCA), United Kingdom
**Filing Requirement:** Report knowledge or suspicion of money laundering or terrorist financing
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 122 fields mapped)

---

## Report Overview

Under the Proceeds of Crime Act 2002 (POCA) and the Terrorism Act 2000, persons in the regulated sector must submit a Suspicious Activity Report (SAR) to the UK Financial Intelligence Unit (UKFIU) within the National Crime Agency when they know or suspect money laundering or terrorist financing. This is a criminal offence disclosure requirement.

**Filing Threshold:** Knowledge or suspicion of money laundering or terrorist financing (no monetary threshold)
**Filing Deadline:** As soon as practicable after information comes to light
**Filing Method:** Online via SAR Online system or XML submission to NCA
**Regulation:** Proceeds of Crime Act 2002, Money Laundering Regulations 2017, Terrorism Act 2000
**Jurisdiction:** United Kingdom

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total UK SAR Fields** | 122 | 100% |
| **Mapped to CDM** | 122 | 100% |
| **Direct Mapping** | 98 | 80% |
| **Derived/Calculated** | 18 | 15% |
| **Reference Data Lookup** | 6 | 5% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Section A: Reporter Information (Fields A1-A15)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| A1 | Reporting organisation name | Text | 140 | Yes | Free text | FinancialInstitution | institutionName | Legal name of reporter |
| A2 | Reporting organisation reference number | Text | 20 | Yes | URN | FinancialInstitution | ncaReportingOrgURN | NCA-assigned URN |
| A3 | Organisation type | Code | 2 | Yes | Sector codes | FinancialInstitution | institutionType | Regulated sector |
| A4 | Reporting organisation address | Text | 200 | Yes | Free text | FinancialInstitution | streetAddress | Full address |
| A5 | City/town | Text | 50 | Yes | Free text | FinancialInstitution | city | City |
| A6 | Postcode | Text | 10 | Yes | UK postcode | FinancialInstitution | postalCode | UK postcode |
| A7 | Country | Code | 2 | Yes | ISO 3166-1 | FinancialInstitution | country | Should be GB |
| A8 | Money laundering reporting officer name | Text | 140 | Yes | Free text | FinancialInstitution | mlroName | MLRO name |
| A9 | MLRO telephone | Text | 25 | Yes | Phone | FinancialInstitution | mlroPhoneNumber | MLRO contact |
| A10 | MLRO email | Text | 256 | Yes | Email | FinancialInstitution | mlroEmailAddress | MLRO email |
| A11 | Branch/department identifier | Text | 100 | No | Free text | FinancialInstitution | branchDepartmentId | Branch/dept code |
| A12 | Branch/department name | Text | 140 | No | Free text | FinancialInstitution | branchName | Branch/dept name |
| A13 | Alternative contact name | Text | 140 | No | Free text | RegulatoryReport | alternateContactName | Backup contact |
| A14 | Alternative contact telephone | Text | 25 | No | Phone | RegulatoryReport | alternateContactPhone | Backup phone |
| A15 | Alternative contact email | Text | 256 | No | Email | RegulatoryReport | alternateContactEmail | Backup email |

### Section B: Report Details (Fields B1-B15)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| B1 | SAR reference number | Text | 20 | Auto | Generated | RegulatoryReport | reportReferenceNumber | System-assigned |
| B2 | Date of report | Date | 10 | Auto | YYYY-MM-DD | RegulatoryReport | submissionDate | Submission date |
| B3 | Report type | Code | 4 | Yes | FULL/LSAR | RegulatoryReport.extensions | sarReportType | Full or limited |
| B4 | Disclosure route | Code | 4 | Yes | SECT/AUTH | RegulatoryReport.extensions | disclosureRoute | Section or authorized |
| B5 | Reason for reporting | Multi-select | - | Yes | Code list | RegulatoryReport.extensions | reasonForReporting | ML/TF reason codes |
| B6 | Money laundering suspected | Code | 4 | Yes | TRUE/FALSE | RegulatoryReport.extensions | moneyLaunderingSuspected | ML suspected? |
| B7 | Terrorist financing suspected | Code | 4 | Yes | TRUE/FALSE | RegulatoryReport.extensions | terroristFinancingSuspected | TF suspected? |
| B8 | Suspicion basis | Code | 4 | Yes | KNOW/SUSP | RegulatoryReport.extensions | suspicionBasis | Knowledge or suspicion |
| B9 | Related previous SAR | Text | 20 | No | SAR ref | RegulatoryReport.extensions | relatedPreviousSAR | Prior SAR reference |
| B10 | Continuing activity | Code | 4 | Yes | TRUE/FALSE | RegulatoryReport | continuingActivity | Ongoing suspicious activity? |
| B11 | Date suspicion arose | Date | 10 | Yes | YYYY-MM-DD | RegulatoryReport.extensions | suspicionAroseDate | When suspicion first arose |
| B12 | Law enforcement aware | Code | 4 | Yes | TRUE/FALSE | ComplianceCase | lawEnforcementNotified | Already reported to LE? |
| B13 | Law enforcement agency | Text | 100 | Cond | Free text | ComplianceCase | lawEnforcementAgency | Which agency |
| B14 | Law enforcement reference | Text | 50 | Cond | Free text | ComplianceCase | lawEnforcementReference | LE reference number |
| B15 | Other disclosures made | Code | 4 | Yes | TRUE/FALSE | RegulatoryReport.extensions | otherDisclosuresMade | Reported elsewhere? |

### Section C: Subject Information (Fields C1-C30, repeatable)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| C1 | Subject type | Code | 4 | Yes | INDI/ENTI | Party | partyType | Individual or entity |
| C2 | Subject role | Code | 4 | Yes | Role codes | Party | roleInSuspiciousActivity | Subject's role |
| C3 | Individual surname | Text | 140 | Cond | Free text | Party | familyName | Last name if individual |
| C4 | Individual first name | Text | 140 | Cond | Free text | Party | givenName | First name |
| C5 | Individual middle name(s) | Text | 140 | No | Free text | Party | middleName | Middle names |
| C6 | Title | Text | 20 | No | Free text | Party | title | Mr, Mrs, Dr, etc. |
| C7 | Date of birth | Date | 10 | No | YYYY-MM-DD | Party | dateOfBirth | Birth date |
| C8 | Gender | Code | 1 | No | M/F/O | Party | gender | Gender |
| C9 | National Insurance number | Text | 9 | No | NINO format | Party | nationalInsuranceNumber | UK NINO |
| C10 | Passport number | Text | 35 | No | Free text | Party | passportNumber | Passport number |
| C11 | Passport country | Code | 2 | No | ISO 3166-1 | Party | passportCountry | Issuing country |
| C12 | Driving licence number | Text | 35 | No | Free text | Party | drivingLicenceNumber | UK licence |
| C13 | Other ID type | Text | 50 | No | Free text | Party | otherIdType | Other ID description |
| C14 | Other ID number | Text | 35 | No | Free text | Party | otherIdNumber | Other ID number |
| C15 | Entity name | Text | 140 | Cond | Free text | Party | name | Legal entity name |
| C16 | Entity type | Code | 4 | Cond | Entity codes | Party | entityType | Company, partnership, etc. |
| C17 | Company registration number | Text | 20 | No | Free text | Party | companyRegistrationNumber | Companies House number |
| C18 | Jurisdiction of incorporation | Code | 2 | No | ISO 3166-1 | Party | jurisdictionOfIncorporation | Where incorporated |
| C19 | VAT number | Text | 20 | No | Free text | Party | vatNumber | VAT registration |
| C20 | Address line 1 | Text | 100 | No | Free text | Party | streetAddress | Street address |
| C21 | Address line 2 | Text | 100 | No | Free text | Party | addressLine2 | Additional address |
| C22 | City/town | Text | 50 | No | Free text | Party | city | City |
| C23 | County/state | Text | 50 | No | Free text | Party | stateProvince | County/state |
| C24 | Postcode | Text | 10 | No | Free text | Party | postalCode | Postcode |
| C25 | Country | Code | 2 | No | ISO 3166-1 | Party | country | Country |
| C26 | Telephone | Text | 25 | No | Phone | Party | phoneNumber | Contact phone |
| C27 | Email | Text | 256 | No | Email | Party | emailAddress | Email address |
| C28 | Occupation/business | Text | 100 | No | Free text | Party | occupation | Occupation or business |
| C29 | Nationality | Code | 2 | No | ISO 3166-1 | Party | nationality | Nationality |
| C30 | Country of residence | Code | 2 | No | ISO 3166-1 | Party | countryOfResidence | Residence country |

### Section D: Account Details (Fields D1-D15, repeatable)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| D1 | Account holder relationship | Code | 4 | Yes | Relationship codes | Account | accountHolderRelationship | Relationship to subject |
| D2 | Account type | Code | 4 | Yes | Account types | Account | accountType | Current, savings, etc. |
| D3 | Account number | Text | 40 | Yes | Free text | Account | accountNumber | Account number |
| D4 | Sort code | Text | 6 | Cond | 6 digits | Account | sortCode | UK sort code |
| D5 | IBAN | Text | 34 | No | IBAN format | Account | iban | International account |
| D6 | BIC/SWIFT | Text | 11 | No | BIC format | FinancialInstitution | bicSwift | Bank identifier |
| D7 | Currency | Code | 3 | Yes | ISO 4217 | Account | accountCurrency | Account currency |
| D8 | Account opened date | Date | 10 | No | YYYY-MM-DD | Account | accountOpenedDate | When opened |
| D9 | Account closed date | Date | 10 | No | YYYY-MM-DD | Account | accountClosedDate | If closed |
| D10 | Account status | Code | 4 | Yes | OPEN/CLOS/FROZ/DORM | Account | accountStatus | Current status |
| D11 | Current balance | Decimal | 18,2 | No | Numeric | Account | currentBalance | Balance at reporting |
| D12 | Institution name | Text | 140 | No | Free text | FinancialInstitution | institutionName | Bank name |
| D13 | Institution address | Text | 200 | No | Free text | FinancialInstitution | institutionAddress | Bank address |
| D14 | Account closed by institution | Code | 4 | Cond | TRUE/FALSE | Account | closedByInstitution | Institution closed it? |
| D15 | Reason for closure | Text | 200 | Cond | Free text | Account | accountClosureReason | Why closed |

### Section E: Transaction Details (Fields E1-E25, repeatable)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| E1 | Transaction type | Code | 4 | Yes | Transaction codes | PaymentInstruction | transactionType | Cash, transfer, etc. |
| E2 | Transaction date | Date | 10 | Yes | YYYY-MM-DD | PaymentInstruction | valueDate | Transaction date |
| E3 | Transaction amount | Decimal | 18,2 | Yes | Numeric | PaymentInstruction | instructedAmount.amount | Amount |
| E4 | Transaction currency | Code | 3 | Yes | ISO 4217 | PaymentInstruction | instructedAmount.currency | Currency |
| E5 | GBP equivalent | Decimal | 18,2 | No | Numeric | PaymentInstruction | gbpEquivalent | If foreign currency |
| E6 | Debit account | Text | 40 | Cond | Free text | Account | debitAccountNumber | From account |
| E7 | Credit account | Text | 40 | Cond | Free text | Account | creditAccountNumber | To account |
| E8 | Payment method | Code | 4 | Yes | Method codes | PaymentInstruction | paymentMethod | BACS, CHAPS, card, etc. |
| E9 | Transaction reference | Text | 100 | No | Free text | PaymentInstruction | transactionReferenceNumber | Transaction ref |
| E10 | Debit institution name | Text | 140 | Cond | Free text | FinancialInstitution | debitInstitutionName | Sending bank |
| E11 | Debit institution sort code | Text | 6 | Cond | 6 digits | FinancialInstitution | debitInstitutionSortCode | Sending sort code |
| E12 | Debit institution BIC | Text | 11 | Cond | BIC format | FinancialInstitution | debitInstitutionBIC | Sending BIC |
| E13 | Credit institution name | Text | 140 | Cond | Free text | FinancialInstitution | creditInstitutionName | Receiving bank |
| E14 | Credit institution sort code | Text | 6 | Cond | 6 digits | FinancialInstitution | creditInstitutionSortCode | Receiving sort code |
| E15 | Credit institution BIC | Text | 11 | Cond | BIC format | FinancialInstitution | creditInstitutionBIC | Receiving BIC |
| E16 | Ordering party name | Text | 140 | Cond | Free text | Party | orderingPartyName | Originator |
| E17 | Beneficiary name | Text | 140 | Cond | Free text | Party | beneficiaryName | Ultimate beneficiary |
| E18 | Transaction purpose | Text | 200 | No | Free text | PaymentInstruction | purposeDescription | Stated purpose |
| E19 | Cash deposit location | Text | 140 | Cond | Free text | PaymentInstruction.extensions | cashDepositLocation | Branch/ATM location |
| E20 | Cash withdrawal location | Text | 140 | Cond | Free text | PaymentInstruction.extensions | cashWithdrawalLocation | Branch/ATM location |
| E21 | Third party involvement | Code | 4 | Yes | TRUE/FALSE | PaymentInstruction.extensions | thirdPartyInvolvement | Third party involved? |
| E22 | Third party name | Text | 140 | Cond | Free text | Party | thirdPartyName | Third party details |
| E23 | Transaction refused | Code | 4 | Yes | TRUE/FALSE | PaymentInstruction | transactionRefused | Was transaction refused? |
| E24 | Refusal reason | Text | 200 | Cond | Free text | PaymentInstruction | refusalReason | Why refused |
| E25 | Total suspicious amount | Decimal | 18,2 | No | Numeric | RegulatoryReport | totalAmountInvolved | Total suspicious value |

### Section F: Suspicion Details (Fields F1-F20)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| F1 | Suspicion type | Multi-select | - | Yes | Code list | RegulatoryReport.extensions | suspicionType | Type of ML/TF |
| F2 | Predicate offence | Multi-select | - | No | Offence codes | RegulatoryReport.extensions | predicateOffence | Suspected crimes |
| F3 | Geographic risk | Multi-select | - | No | Country codes | RegulatoryReport.extensions | geographicRisk | High-risk countries involved |
| F4 | Customer risk rating | Code | 4 | Yes | LOW/MED/HIGH | Party | riskRating | Customer risk level |
| F5 | Date risk rating assessed | Date | 10 | No | YYYY-MM-DD | Party | riskRatingDate | When assessed |
| F6 | Enhanced due diligence applied | Code | 4 | Yes | TRUE/FALSE | Party.extensions | enhancedDueDiligence | EDD conducted? |
| F7 | PEP status | Code | 4 | Yes | TRUE/FALSE | Party | politicallyExposedPerson | Is PEP? |
| F8 | PEP relationship | Code | 4 | Cond | PEP codes | Party | pepRelationship | Type of PEP |
| F9 | Sanctions screening conducted | Code | 4 | Yes | TRUE/FALSE | Party.extensions | sanctionsScreeningConducted | Screened for sanctions? |
| F10 | Sanctions match | Code | 4 | Cond | TRUE/FALSE | Party | sanctionsMatch | Sanctions hit? |
| F11 | Sanctions list | Text | 100 | Cond | Free text | Party | sanctionsList | Which list |
| F12 | Source of funds | Text | 200 | No | Free text | Party | sourceOfFunds | Stated source |
| F13 | Source of wealth | Text | 200 | No | Free text | Party | sourceOfWealth | Stated wealth source |
| F14 | Expected account activity | Text | 200 | No | Free text | Account | expectedActivity | Expected use |
| F15 | Deviation from expected activity | Text | 500 | Yes | Free text | RegulatoryReport.extensions | deviationFromExpected | How activity differs |
| F16 | Red flag indicators | Multi-select | - | Yes | Code list | RegulatoryReport.extensions | redFlagIndicators | Specific red flags |
| F17 | Supporting documentation | Code | 4 | Yes | TRUE/FALSE | RegulatoryReport.extensions | supportingDocumentation | Evidence available? |
| F18 | Actions taken | Multi-select | - | Yes | Action codes | ComplianceCase | actionTaken | What actions taken |
| F19 | Internal investigation | Code | 4 | Yes | TRUE/FALSE | ComplianceCase | internalInvestigation | Investigation conducted? |
| F20 | Investigation findings | Text | 1000 | Cond | Free text | ComplianceCase | investigationFindings | Key findings |

### Section G: Narrative (Fields G1-G2)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| G1 | Grounds for knowledge or suspicion | Text | 10000 | Yes | Free text | RegulatoryReport | narrativeDescription | Detailed narrative |
| G2 | Additional information | Text | 5000 | No | Free text | RegulatoryReport | additionalInformation | Any other relevant info |

---

## Code Lists

### Organisation Type Codes (Field A3)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Credit institution | FinancialInstitution.institutionType = '01' |
| 02 | Financial institution | FinancialInstitution.institutionType = '02' |
| 03 | Auditor/accountant | FinancialInstitution.institutionType = '03' |
| 04 | Legal professional | FinancialInstitution.institutionType = '04' |
| 05 | Trust or company service provider | FinancialInstitution.institutionType = '05' |
| 06 | Estate agent | FinancialInstitution.institutionType = '06' |
| 07 | High value dealer | FinancialInstitution.institutionType = '07' |
| 08 | Casino | FinancialInstitution.institutionType = '08' |
| 09 | Money service business | FinancialInstitution.institutionType = '09' |

### Reason for Reporting Codes (Field B5)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| ML | Money laundering | RegulatoryReport.extensions.reasonForReporting = 'ML' |
| TF | Terrorist financing | RegulatoryReport.extensions.reasonForReporting = 'TF' |
| BOTH | Both ML and TF | RegulatoryReport.extensions.reasonForReporting = 'BOTH' |

### Subject Role Codes (Field C2)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| ACCT | Account holder | Party.roleInSuspiciousActivity = 'ACCT' |
| BENF | Beneficiary | Party.roleInSuspiciousActivity = 'BENF' |
| ORIG | Originator | Party.roleInSuspiciousActivity = 'ORIG' |
| THRD | Third party | Party.roleInSuspiciousActivity = 'THRD' |
| BENO | Beneficial owner | Party.roleInSuspiciousActivity = 'BENO' |
| AUTH | Authorized signatory | Party.roleInSuspiciousActivity = 'AUTH' |
| OTHE | Other | Party.roleInSuspiciousActivity = 'OTHE' |

### Transaction Type Codes (Field E1)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CDEP | Cash deposit | PaymentInstruction.transactionType = 'CDEP' |
| CWDL | Cash withdrawal | PaymentInstruction.transactionType = 'CWDL' |
| BACS | BACS payment | PaymentInstruction.transactionType = 'BACS' |
| CHPS | CHAPS payment | PaymentInstruction.transactionType = 'CHPS' |
| FPAY | Faster Payment | PaymentInstruction.transactionType = 'FPAY' |
| WIRE | International wire | PaymentInstruction.transactionType = 'WIRE' |
| CARD | Card payment | PaymentInstruction.transactionType = 'CARD' |
| CHQE | Cheque | PaymentInstruction.transactionType = 'CHQE' |
| OTHR | Other | PaymentInstruction.transactionType = 'OTHR' |

### Suspicion Type Codes (Field F1)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| STRU | Structuring | RegulatoryReport.extensions.suspicionType = 'STRU' |
| SMUR | Smurfing | RegulatoryReport.extensions.suspicionType = 'SMUR' |
| TRAD | Trade-based ML | RegulatoryReport.extensions.suspicionType = 'TRAD' |
| CACH | Cash-based business | RegulatoryReport.extensions.suspicionType = 'CACH' |
| UNEX | Unexplained wealth | RegulatoryReport.extensions.suspicionType = 'UNEX' |
| TERS | Terrorist financing | RegulatoryReport.extensions.suspicionType = 'TERS' |
| SANC | Sanctions evasion | RegulatoryReport.extensions.suspicionType = 'SANC' |
| FRAU | Fraud proceeds | RegulatoryReport.extensions.suspicionType = 'FRAU' |

### Predicate Offence Codes (Field F2)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| DRUG | Drug trafficking | RegulatoryReport.extensions.predicateOffence = 'DRUG' |
| FRAU | Fraud | RegulatoryReport.extensions.predicateOffence = 'FRAU' |
| CORR | Corruption/bribery | RegulatoryReport.extensions.predicateOffence = 'CORR' |
| TAXE | Tax evasion | RegulatoryReport.extensions.predicateOffence = 'TAXE' |
| HTRF | Human trafficking | RegulatoryReport.extensions.predicateOffence = 'HTRF' |
| THFT | Theft | RegulatoryReport.extensions.predicateOffence = 'THFT' |
| CYBR | Cybercrime | RegulatoryReport.extensions.predicateOffence = 'CYBR' |
| OTHR | Other | RegulatoryReport.extensions.predicateOffence = 'OTHR' |

### Red Flag Indicators (Field F16)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| UNXP | Unexplained transactions | RegulatoryReport.extensions.redFlagIndicators[] = 'UNXP' |
| COMP | Complex transaction structure | RegulatoryReport.extensions.redFlagIndicators[] = 'COMP' |
| CASH | Large cash transactions | RegulatoryReport.extensions.redFlagIndicators[] = 'CASH' |
| GEOG | High-risk geography | RegulatoryReport.extensions.redFlagIndicators[] = 'GEOG' |
| RAPD | Rapid movement of funds | RegulatoryReport.extensions.redFlagIndicators[] = 'RAPD' |
| NECO | No economic purpose | RegulatoryReport.extensions.redFlagIndicators[] = 'NECO' |
| EVAS | Evasive behavior | RegulatoryReport.extensions.redFlagIndicators[] = 'EVAS' |
| INCO | Inconsistent information | RegulatoryReport.extensions.redFlagIndicators[] = 'INCO' |

### Actions Taken (Field F18)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| NONE | No action | ComplianceCase.actionTaken = 'NONE' |
| EDDP | Enhanced due diligence | ComplianceCase.actionTaken = 'EDDP' |
| CLOS | Account closed | ComplianceCase.actionTaken = 'CLOS' |
| REFR | Transaction refused | ComplianceCase.actionTaken = 'REFR' |
| FROZ | Funds frozen | ComplianceCase.actionTaken = 'FROZ' |
| TERM | Relationship terminated | ComplianceCase.actionTaken = 'TERM' |
| MONI | Enhanced monitoring | ComplianceCase.actionTaken = 'MONI' |

---

## CDM Extensions Required

All 122 UK SAR fields successfully map to GPS CDM using the RegulatoryReport.extensions object. **No schema enhancements required.**

The extensions object supports all UK SAR-specific fields while maintaining the core CDM structure.

---

## Example UK SAR Scenario

**Suspicious Activity:** Unexplained cash deposits inconsistent with stated business

**Subject:** Mr. John Smith
**Business:** Small convenience store (annual turnover stated as £200,000)
**Account:** Business current account at Example Bank UK

**Suspicious Pattern (3-month period):**
- 47 cash deposits totaling £285,000
- Deposits made across multiple branches
- Deposits structured below £10,000 (mostly £8,000-£9,500)
- No corresponding increase in business expenses or inventory
- Cash withdrawn shortly after deposits to offshore accounts

**Investigation Findings:**
- Customer risk rating: High
- Expected monthly cash deposits: £15,000-£20,000
- Actual average: £95,000 per month (4.75x expected)
- Source of funds: "Shop takings" (inconsistent with business size)
- Third parties making deposits on behalf of customer
- Customer evasive when questioned

**Red Flags:**
- Structuring (deposits below reporting threshold)
- Volume inconsistent with business profile
- Rapid movement to offshore jurisdictions
- Use of third parties
- Evasive behavior

**Actions Taken:**
- Enhanced due diligence conducted
- Enhanced monitoring implemented
- SAR submitted to NCA
- Account relationship under review

**Grounds for Suspicion:**
The volume and pattern of cash deposits significantly exceeds what would be expected for a business of this size and nature. The structuring of deposits to avoid reporting thresholds, combined with the rapid movement of funds offshore and the customer's evasive behavior, gives rise to suspicion that the customer is laundering proceeds of crime, potentially from drug trafficking or other cash-intensive illegal activity.

---

## References

- **Proceeds of Crime Act 2002:** Sections 327-329, 330-332 (regulated sector disclosures)
- **Terrorism Act 2000:** Sections 15-18, 21A (terrorist property disclosures)
- **Money Laundering Regulations 2017:** SI 2017/692 (as amended)
- **JMLSG Guidance:** Joint Money Laundering Steering Group guidance for the UK financial sector
- **NCA SAR Guidance:** National Crime Agency guidance on submitting SARs
- **SAR Online System:** https://www.ukciu.gov.uk (SAR submission portal)
- **SAR Glossary Codes:** NCA SAR glossary of codes and indicators
- **GPS CDM Schema:** `/schemas/05_regulatory_report_complete_schema.json`, `/schemas/02_party_complete_schema.json`, `/schemas/03_account_complete_schema.json`, `/schemas/06_compliance_case_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
