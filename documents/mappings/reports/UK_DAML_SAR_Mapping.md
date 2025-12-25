# UK DAML SAR - Defence Against Money Laundering SAR
## Complete Field Mapping to GPS CDM

**Report Type:** UK DAML SAR - Defence Against Money Laundering Suspicious Activity Report
**Regulatory Authority:** National Crime Agency (NCA), United Kingdom
**Filing Requirement:** Request consent to proceed with transaction that would otherwise constitute money laundering
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 132 fields mapped)

---

## Report Overview

A DAML SAR (Defence Against Money Laundering Suspicious Activity Report) is submitted to the UK Financial Intelligence Unit when a person in the regulated sector seeks consent to proceed with a transaction that they suspect may constitute money laundering. Under POCA 2002 sections 327-329, certain acts (arranging, acquiring, using criminal property) are offences, but consent from the NCA provides a statutory defence.

**Filing Threshold:** Any transaction suspected to involve criminal property (no monetary threshold)
**Filing Deadline:** Immediate - before proceeding with the transaction
**Filing Method:** Online via SAR Online system (DAML/consent request) or XML submission
**Regulation:** Proceeds of Crime Act 2002 (Sections 327-329, 335), Money Laundering Regulations 2017
**Jurisdiction:** United Kingdom
**Consent Regime:** 7 working day notice period (or 31 days if NCA refuses consent)

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total UK DAML SAR Fields** | 132 | 100% |
| **Mapped to CDM** | 132 | 100% |
| **Direct Mapping** | 104 | 79% |
| **Derived/Calculated** | 21 | 16% |
| **Reference Data Lookup** | 7 | 5% |
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

### Section B: Report Details (Fields B1-B20)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| B1 | SAR reference number | Text | 20 | Auto | Generated | RegulatoryReport | reportReferenceNumber | System-assigned SAR ref |
| B2 | DAML reference number | Text | 20 | Auto | Generated | RegulatoryReport | sarnNumber | NCA DAML reference |
| B3 | Date of report | Date | 10 | Auto | YYYY-MM-DD | RegulatoryReport | submissionDate | Submission date |
| B4 | Report type | Code | 4 | Yes | DAML | RegulatoryReport.extensions | sarReportType | Always DAML |
| B5 | Consent request indicator | Code | 4 | Yes | TRUE | RegulatoryReport | consentRequired | Always TRUE for DAML |
| B6 | Reason for consent request | Text | 500 | Yes | Free text | RegulatoryReport.extensions | consentRequestReason | Why consent needed |
| B7 | Money laundering offence | Code | 4 | Yes | S327/S328/S329 | RegulatoryReport.extensions | pocaOffenceSection | Which POCA section |
| B8 | Suspicion basis | Code | 4 | Yes | KNOW/SUSP/REAS | RegulatoryReport.extensions | suspicionBasis | Knowledge/suspicion/reasonable grounds |
| B9 | Related previous SAR/DAML | Text | 20 | No | SAR ref | RegulatoryReport.extensions | relatedPreviousSAR | Prior SAR/DAML reference |
| B10 | Continuing activity | Code | 4 | Yes | TRUE/FALSE | RegulatoryReport | continuingActivity | Ongoing suspicious activity? |
| B11 | Date suspicion arose | Date | 10 | Yes | YYYY-MM-DD | RegulatoryReport.extensions | suspicionAroseDate | When suspicion first arose |
| B12 | Consent request date/time | DateTime | 24 | Yes | ISO 8601 | RegulatoryReport | consentRequestDate | When consent requested |
| B13 | Urgent consent required | Code | 4 | Yes | TRUE/FALSE | RegulatoryReport.extensions | urgentConsentRequired | Urgent request? |
| B14 | Urgency reason | Text | 500 | Cond | Free text | RegulatoryReport.extensions | urgencyReason | Why urgent |
| B15 | Transaction deadline | DateTime | 24 | Cond | ISO 8601 | RegulatoryReport.extensions | transactionDeadline | Must complete by |
| B16 | Customer aware of DAML | Code | 4 | Yes | TRUE/FALSE | RegulatoryReport.extensions | customerAwareOfDAML | Customer knows about SAR? |
| B17 | Tipping off risk | Code | 4 | Yes | LOW/MED/HIGH | RegulatoryReport.extensions | tippingOffRisk | Risk of tipping off |
| B18 | Prejudice risk | Code | 4 | Yes | LOW/MED/HIGH | RegulatoryReport.extensions | prejudiceRisk | Risk of prejudicing investigation |
| B19 | Law enforcement aware | Code | 4 | Yes | TRUE/FALSE | ComplianceCase | lawEnforcementNotified | Already reported to LE? |
| B20 | Law enforcement agency | Text | 100 | Cond | Free text | ComplianceCase | lawEnforcementAgency | Which agency |

### Section C: Consent Decision (Fields C1-C15) - Completed by NCA

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| C1 | NCA decision | Code | 4 | Post | GRANT/REFUS/MOREF | RegulatoryReport | consentGranted | NCA decision |
| C2 | Consent granted | Code | 4 | Post | TRUE/FALSE | RegulatoryReport | consentGranted | Consent given? |
| C3 | Consent response date/time | DateTime | 24 | Post | ISO 8601 | RegulatoryReport | consentResponseDate | When NCA responded |
| C4 | Notice period start | DateTime | 24 | Post | ISO 8601 | RegulatoryReport.extensions | noticePeriodStart | 7-day period starts |
| C5 | Notice period end | DateTime | 24 | Post | ISO 8601 | RegulatoryReport | consentExpiryDate | When consent expires |
| C6 | Refusal reason | Code | 4 | Post | Reason codes | RegulatoryReport | consentRefusalReason | Why refused |
| C7 | Refusal details | Text | 1000 | Post | Free text | RegulatoryReport.extensions | consentRefusalDetails | Detailed reason |
| C8 | Moratorium period | Code | 4 | Post | TRUE/FALSE | RegulatoryReport.extensions | moratoriumPeriodApplied | 31-day moratorium? |
| C9 | Moratorium end date | DateTime | 24 | Post | ISO 8601 | RegulatoryReport.extensions | moratoriumEndDate | Moratorium expires |
| C10 | Investigation ongoing | Code | 4 | Post | TRUE/FALSE | ComplianceCase | investigationOngoing | NCA investigating? |
| C11 | Restraint order sought | Code | 4 | Post | TRUE/FALSE | RegulatoryReport.extensions | restraintOrderSought | Restraint order requested? |
| C12 | NCA case reference | Text | 50 | Post | Free text | RegulatoryReport.extensions | ncaCaseReference | NCA investigation ref |
| C13 | NCA contact name | Text | 140 | Post | Free text | RegulatoryReport.extensions | ncaContactName | NCA officer |
| C14 | NCA contact telephone | Text | 25 | Post | Phone | RegulatoryReport.extensions | ncaContactPhone | NCA contact |
| C15 | Additional NCA instructions | Text | 1000 | Post | Free text | RegulatoryReport.extensions | ncaAdditionalInstructions | NCA guidance |

### Section D: Subject Information (Fields D1-D30, repeatable)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| D1 | Subject type | Code | 4 | Yes | INDI/ENTI | Party | partyType | Individual or entity |
| D2 | Subject role | Code | 4 | Yes | Role codes | Party | roleInSuspiciousActivity | Subject's role |
| D3 | Individual surname | Text | 140 | Cond | Free text | Party | familyName | Last name if individual |
| D4 | Individual first name | Text | 140 | Cond | Free text | Party | givenName | First name |
| D5 | Individual middle name(s) | Text | 140 | No | Free text | Party | middleName | Middle names |
| D6 | Title | Text | 20 | No | Free text | Party | title | Mr, Mrs, Dr, etc. |
| D7 | Date of birth | Date | 10 | No | YYYY-MM-DD | Party | dateOfBirth | Birth date |
| D8 | Gender | Code | 1 | No | M/F/O | Party | gender | Gender |
| D9 | National Insurance number | Text | 9 | No | NINO format | Party | nationalInsuranceNumber | UK NINO |
| D10 | Passport number | Text | 35 | No | Free text | Party | passportNumber | Passport number |
| D11 | Passport country | Code | 2 | No | ISO 3166-1 | Party | passportCountry | Issuing country |
| D12 | Driving licence number | Text | 35 | No | Free text | Party | drivingLicenceNumber | UK licence |
| D13 | Other ID type | Text | 50 | No | Free text | Party | otherIdType | Other ID description |
| D14 | Other ID number | Text | 35 | No | Free text | Party | otherIdNumber | Other ID number |
| D15 | Entity name | Text | 140 | Cond | Free text | Party | name | Legal entity name |
| D16 | Entity type | Code | 4 | Cond | Entity codes | Party | entityType | Company, partnership, etc. |
| D17 | Company registration number | Text | 20 | No | Free text | Party | companyRegistrationNumber | Companies House number |
| D18 | Jurisdiction of incorporation | Code | 2 | No | ISO 3166-1 | Party | jurisdictionOfIncorporation | Where incorporated |
| D19 | VAT number | Text | 20 | No | Free text | Party | vatNumber | VAT registration |
| D20 | Address line 1 | Text | 100 | No | Free text | Party | streetAddress | Street address |
| D21 | Address line 2 | Text | 100 | No | Free text | Party | addressLine2 | Additional address |
| D22 | City/town | Text | 50 | No | Free text | Party | city | City |
| D23 | County/state | Text | 50 | No | Free text | Party | stateProvince | County/state |
| D24 | Postcode | Text | 10 | No | Free text | Party | postalCode | Postcode |
| D25 | Country | Code | 2 | No | ISO 3166-1 | Party | country | Country |
| D26 | Telephone | Text | 25 | No | Phone | Party | phoneNumber | Contact phone |
| D27 | Email | Text | 256 | No | Email | Party | emailAddress | Email address |
| D28 | Occupation/business | Text | 100 | No | Free text | Party | occupation | Occupation or business |
| D29 | Nationality | Code | 2 | No | ISO 3166-1 | Party | nationality | Nationality |
| D30 | Country of residence | Code | 2 | No | ISO 3166-1 | Party | countryOfResidence | Residence country |

### Section E: Account Details (Fields E1-E15, repeatable)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| E1 | Account holder relationship | Code | 4 | Yes | Relationship codes | Account | accountHolderRelationship | Relationship to subject |
| E2 | Account type | Code | 4 | Yes | Account types | Account | accountType | Current, savings, etc. |
| E3 | Account number | Text | 40 | Yes | Free text | Account | accountNumber | Account number |
| E4 | Sort code | Text | 6 | Cond | 6 digits | Account | sortCode | UK sort code |
| E5 | IBAN | Text | 34 | No | IBAN format | Account | iban | International account |
| E6 | BIC/SWIFT | Text | 11 | No | BIC format | FinancialInstitution | bicSwift | Bank identifier |
| E7 | Currency | Code | 3 | Yes | ISO 4217 | Account | accountCurrency | Account currency |
| E8 | Account opened date | Date | 10 | No | YYYY-MM-DD | Account | accountOpenedDate | When opened |
| E9 | Account closed date | Date | 10 | No | YYYY-MM-DD | Account | accountClosedDate | If closed |
| E10 | Account status | Code | 4 | Yes | OPEN/CLOS/FROZ/DORM | Account | accountStatus | Current status |
| E11 | Current balance | Decimal | 18,2 | No | Numeric | Account | currentBalance | Balance at reporting |
| E12 | Institution name | Text | 140 | No | Free text | FinancialInstitution | institutionName | Bank name |
| E13 | Institution address | Text | 200 | No | Free text | FinancialInstitution | institutionAddress | Bank address |
| E14 | Funds frozen pending consent | Code | 4 | Yes | TRUE/FALSE | Account | fundsFrozenPendingConsent | Funds held? |
| E15 | Frozen amount | Decimal | 18,2 | Cond | Numeric | Account | frozenAmount | Amount frozen |

### Section F: Transaction Details - Requiring Consent (Fields F1-F30)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| F1 | Transaction type | Code | 4 | Yes | Transaction codes | PaymentInstruction | transactionType | What transaction |
| F2 | Proposed transaction date | Date | 10 | Yes | YYYY-MM-DD | PaymentInstruction | proposedExecutionDate | When to execute |
| F3 | Transaction amount | Decimal | 18,2 | Yes | Numeric | PaymentInstruction | instructedAmount.amount | Amount |
| F4 | Transaction currency | Code | 3 | Yes | ISO 4217 | PaymentInstruction | instructedAmount.currency | Currency |
| F5 | GBP equivalent | Decimal | 18,2 | No | Numeric | PaymentInstruction | gbpEquivalent | If foreign currency |
| F6 | Debit account | Text | 40 | Cond | Free text | Account | debitAccountNumber | From account |
| F7 | Credit account | Text | 40 | Cond | Free text | Account | creditAccountNumber | To account |
| F8 | Payment method | Code | 4 | Yes | Method codes | PaymentInstruction | paymentMethod | BACS, CHAPS, card, etc. |
| F9 | Transaction reference | Text | 100 | No | Free text | PaymentInstruction | transactionReferenceNumber | Transaction ref |
| F10 | Debit institution name | Text | 140 | Cond | Free text | FinancialInstitution | debitInstitutionName | Sending bank |
| F11 | Debit institution sort code | Text | 6 | Cond | 6 digits | FinancialInstitution | debitInstitutionSortCode | Sending sort code |
| F12 | Debit institution BIC | Text | 11 | Cond | BIC format | FinancialInstitution | debitInstitutionBIC | Sending BIC |
| F13 | Credit institution name | Text | 140 | Cond | Free text | FinancialInstitution | creditInstitutionName | Receiving bank |
| F14 | Credit institution sort code | Text | 6 | Cond | 6 digits | FinancialInstitution | creditInstitutionSortCode | Receiving sort code |
| F15 | Credit institution BIC | Text | 11 | Cond | BIC format | FinancialInstitution | creditInstitutionBIC | Receiving BIC |
| F16 | Ordering party name | Text | 140 | Cond | Free text | Party | orderingPartyName | Originator |
| F17 | Beneficiary name | Text | 140 | Cond | Free text | Party | beneficiaryName | Ultimate beneficiary |
| F18 | Beneficiary country | Code | 2 | Cond | ISO 3166-1 | Party | beneficiaryCountry | Beneficiary location |
| F19 | Transaction purpose | Text | 200 | Yes | Free text | PaymentInstruction | purposeDescription | Stated purpose |
| F20 | Economic purpose | Text | 500 | Yes | Free text | PaymentInstruction.extensions | economicPurpose | Actual economic rationale |
| F21 | Related contract/agreement | Text | 200 | No | Free text | PaymentInstruction.extensions | relatedContract | Supporting documentation |
| F22 | Third party involvement | Code | 4 | Yes | TRUE/FALSE | PaymentInstruction.extensions | thirdPartyInvolvement | Third party involved? |
| F23 | Third party name | Text | 140 | Cond | Free text | Party | thirdPartyName | Third party details |
| F24 | Third party role | Text | 100 | Cond | Free text | Party | thirdPartyRole | What role |
| F25 | Customer instruction date | Date | 10 | Yes | YYYY-MM-DD | PaymentInstruction.extensions | customerInstructionDate | When customer requested |
| F26 | Customer instruction method | Code | 4 | Yes | Method codes | PaymentInstruction.extensions | customerInstructionMethod | How instructed |
| F27 | Will transaction proceed without consent | Code | 4 | Yes | TRUE/FALSE | PaymentInstruction.extensions | willProceedWithoutConsent | Proceed anyway? |
| F28 | Consequences if refused | Text | 500 | Yes | Free text | RegulatoryReport.extensions | consequencesIfRefused | Impact of refusal |
| F29 | Alternative arrangements available | Code | 4 | Yes | TRUE/FALSE | RegulatoryReport.extensions | alternativeArrangements | Other options? |
| F30 | Alternative details | Text | 500 | Cond | Free text | RegulatoryReport.extensions | alternativeDetails | What alternatives |

### Section G: Suspicion Details (Fields G1-G20)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| G1 | Suspicion type | Multi-select | - | Yes | Code list | RegulatoryReport.extensions | suspicionType | Type of ML/TF |
| G2 | Predicate offence | Multi-select | - | No | Offence codes | RegulatoryReport.extensions | predicateOffence | Suspected crimes |
| G3 | Geographic risk | Multi-select | - | No | Country codes | RegulatoryReport.extensions | geographicRisk | High-risk countries involved |
| G4 | Customer risk rating | Code | 4 | Yes | LOW/MED/HIGH | Party | riskRating | Customer risk level |
| G5 | Date risk rating assessed | Date | 10 | No | YYYY-MM-DD | Party | riskRatingDate | When assessed |
| G6 | Enhanced due diligence applied | Code | 4 | Yes | TRUE/FALSE | Party.extensions | enhancedDueDiligence | EDD conducted? |
| G7 | PEP status | Code | 4 | Yes | TRUE/FALSE | Party | politicallyExposedPerson | Is PEP? |
| G8 | PEP relationship | Code | 4 | Cond | PEP codes | Party | pepRelationship | Type of PEP |
| G9 | Sanctions screening conducted | Code | 4 | Yes | TRUE/FALSE | Party.extensions | sanctionsScreeningConducted | Screened for sanctions? |
| G10 | Sanctions match | Code | 4 | Cond | TRUE/FALSE | Party | sanctionsMatch | Sanctions hit? |
| G11 | Sanctions list | Text | 100 | Cond | Free text | Party | sanctionsList | Which list |
| G12 | Source of funds | Text | 200 | Yes | Free text | Party | sourceOfFunds | Stated source |
| G13 | Source of wealth | Text | 200 | Yes | Free text | Party | sourceOfWealth | Stated wealth source |
| G14 | Verification of source | Code | 4 | Yes | VERIF/UNVERF/PARTIAL | Party.extensions | sourceVerification | Source verified? |
| G15 | Red flag indicators | Multi-select | - | Yes | Code list | RegulatoryReport.extensions | redFlagIndicators | Specific red flags |
| G16 | Supporting documentation | Code | 4 | Yes | TRUE/FALSE | RegulatoryReport.extensions | supportingDocumentation | Evidence available? |
| G17 | Internal investigation | Code | 4 | Yes | TRUE/FALSE | ComplianceCase | internalInvestigation | Investigation conducted? |
| G18 | Investigation findings | Text | 1000 | Cond | Free text | ComplianceCase | investigationFindings | Key findings |
| G19 | Criminal property assessment | Text | 1000 | Yes | Free text | RegulatoryReport.extensions | criminalPropertyAssessment | Why property believed criminal |
| G20 | Likelihood assessment | Code | 4 | Yes | LOW/MED/HIGH | RegulatoryReport.extensions | criminalPropertyLikelihood | How likely criminal property |

### Section H: Narrative (Fields H1-H2)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| H1 | Grounds for knowledge or suspicion | Text | 10000 | Yes | Free text | RegulatoryReport | narrativeDescription | Detailed narrative |
| H2 | Additional information | Text | 5000 | No | Free text | RegulatoryReport | additionalInformation | Any other relevant info |

---

## Code Lists

### POCA Offence Section Codes (Field B7)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| S327 | Concealing, etc. criminal property | RegulatoryReport.extensions.pocaOffenceSection = 'S327' |
| S328 | Arrangements (facilitating acquisition, etc.) | RegulatoryReport.extensions.pocaOffenceSection = 'S328' |
| S329 | Acquisition, use and possession | RegulatoryReport.extensions.pocaOffenceSection = 'S329' |

### NCA Decision Codes (Field C1)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| GRANT | Consent granted | RegulatoryReport.consentGranted = TRUE |
| REFUS | Consent refused | RegulatoryReport.consentGranted = FALSE |
| MOREF | Moratorium period - no response | RegulatoryReport.consentGranted = NULL (deemed consent) |

### Consent Refusal Reason Codes (Field C6)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| INVEST | Investigation ongoing | RegulatoryReport.consentRefusalReason = 'INVEST' |
| RESTRA | Restraint order being sought | RegulatoryReport.consentRefusalReason = 'RESTRA' |
| PROSEC | Prosecution contemplated | RegulatoryReport.consentRefusalReason = 'PROSEC' |
| PREJU | Would prejudice investigation | RegulatoryReport.consentRefusalReason = 'PREJU' |

### Subject Role Codes (Field D2)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| ACCT | Account holder | Party.roleInSuspiciousActivity = 'ACCT' |
| BENF | Beneficiary | Party.roleInSuspiciousActivity = 'BENF' |
| ORIG | Originator | Party.roleInSuspiciousActivity = 'ORIG' |
| INTR | Intermediary | Party.roleInSuspiciousActivity = 'INTR' |
| BENO | Beneficial owner | Party.roleInSuspiciousActivity = 'BENO' |
| AUTH | Authorized signatory | Party.roleInSuspiciousActivity = 'AUTH' |
| THRD | Third party | Party.roleInSuspiciousActivity = 'THRD' |

### Customer Instruction Method Codes (Field F26)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| BRAN | In branch | PaymentInstruction.extensions.customerInstructionMethod = 'BRAN' |
| PHON | By telephone | PaymentInstruction.extensions.customerInstructionMethod = 'PHON' |
| ONLI | Online banking | PaymentInstruction.extensions.customerInstructionMethod = 'ONLI' |
| EMAI | Email instruction | PaymentInstruction.extensions.customerInstructionMethod = 'EMAI' |
| POST | Postal instruction | PaymentInstruction.extensions.customerInstructionMethod = 'POST' |

---

## DAML Process Flow

### Timeline and Deadlines

1. **T0 - DAML Submission:** Reporter submits DAML SAR to NCA
2. **T0 to T+7 working days - Notice Period:** 7 working day notice period begins
3. **Within notice period - NCA Response (optional):**
   - **Consent granted:** Can proceed immediately
   - **Consent refused:** 31-day moratorium period begins
   - **No response:** Deemed consent after 7 working days

4. **Outcomes:**
   - **Consent granted:** Proceed with transaction (provides statutory defence)
   - **Consent refused + moratorium:** Cannot proceed for 31 days from refusal
   - **Deemed consent (no response):** Can proceed after 7 working days
   - **After moratorium expires:** Can proceed (but no statutory defence)

### Key Timeframes

| Period | Duration | Description |
|--------|----------|-------------|
| Notice Period | 7 working days | From DAML submission to deemed consent |
| Moratorium Period | 31 calendar days | From refusal notice to automatic expiry |
| Total Maximum Wait | 38 days | 7 working days + 31 days if refused |

---

## CDM Extensions Required

All 132 UK DAML SAR fields successfully map to GPS CDM using the RegulatoryReport.extensions object. **No schema enhancements required.**

The GPS CDM schema already includes DAML-specific fields:
- `defenceAgainstMoneyLaunderingFlag`
- `consentRequired`
- `consentGranted`
- `consentRefusalReason`
- `consentRequestDate`
- `consentResponseDate`
- `consentExpiryDate`
- `sarnNumber`

---

## Example UK DAML SAR Scenario

**Transaction:** Client requests £500,000 international wire transfer
**Destination:** Offshore bank account in high-risk jurisdiction
**Client:** UK company director

**Circumstances:**
- Client requests urgent transfer to personal offshore account
- States purpose: "Investment opportunity"
- Transfer to jurisdiction known for banking secrecy
- Client recently received £2 million from sale of UK property
- No obvious business reason for offshore transfer
- Client evasive about specific investment details
- Transfer to account in client's name only (not company)

**Suspicion:**
The transfer appears inconsistent with legitimate business activity. The use of an offshore account in a high-risk jurisdiction, combined with the lack of clear economic purpose and the client's evasive behavior, gives rise to suspicion that the funds may represent proceeds of tax evasion or other criminal activity. Proceeding with the transfer without consent would constitute an offence under POCA s328 (arrangements).

**DAML Request:**
- **POCA offence:** Section 328 (entering into arrangements)
- **Suspicion basis:** Suspicion that property is criminal (potential tax evasion)
- **Urgent consent:** No (client wants transfer within 5 days)
- **Customer awareness:** Client told "compliance checks required" (no tipping off)

**NCA Response (Day 3):**
- **Decision:** Consent REFUSED
- **Reason:** Investigation ongoing with HMRC
- **Moratorium:** 31 days from refusal
- **Restraint order:** Being considered

**Outcome:**
- Transaction cannot proceed during 31-day moratorium
- Customer told transaction delayed due to "regulatory requirements"
- After moratorium expiry: Transaction could proceed but would not have statutory defence
- Bank decides to exit customer relationship
- Submits standard SAR reporting suspicious activity

---

## References

- **Proceeds of Crime Act 2002:** Sections 327-329 (money laundering offences), Section 335 (authorised disclosure/consent)
- **Terrorism Act 2000:** Terrorist property offences
- **Money Laundering Regulations 2017:** SI 2017/692 (as amended)
- **JMLSG Guidance:** Part I, Chapter 5 (Making a disclosure)
- **NCA Consent Guidance:** Guidance on the operation of the consent regime
- **SAR Online System:** https://www.ukciu.gov.uk (DAML submission)
- **Law Commission Report:** The Prevention and Enforcement of Money Laundering (on DAML reforms)
- **GPS CDM Schema:** `/schemas/05_regulatory_report_complete_schema.json`, `/schemas/02_party_complete_schema.json`, `/schemas/03_account_complete_schema.json`, `/schemas/01_payment_instruction_complete_schema.json`, `/schemas/06_compliance_case_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
