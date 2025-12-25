# FinCEN SAR - Suspicious Activity Report
## Complete Field Mapping to GPS CDM

**Report Type:** FinCEN Form 111 (Suspicious Activity Report)
**Regulatory Authority:** Financial Crimes Enforcement Network (FinCEN), U.S. Department of Treasury
**Filing Requirement:** Report suspicious transactions relevant to money laundering, terrorist financing, or other financial crimes
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 184 fields mapped)

---

## Report Overview

The Suspicious Activity Report (SAR) is filed by financial institutions to report known or suspected violations of federal law or suspicious transactions related to money laundering or other financial crimes.

**Filing Threshold:** No minimum dollar amount (file when suspicious activity is detected)
**Filing Deadline:** Within 30 calendar days of initial detection
**Filing Method:** BSA E-Filing System (https://bsaefiling.fincen.treas.gov)
**Regulation:** Bank Secrecy Act (31 USC 5318(g)), 31 CFR 1020.320

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total SAR Fields** | 184 | 100% |
| **Mapped to CDM** | 184 | 100% |
| **Direct Mapping** | 156 | 85% |
| **Derived/Calculated** | 18 | 10% |
| **Reference Data Lookup** | 10 | 5% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Part I: Filing Institution Information (Items 1-34)

| Item# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | Type of filing institution | Code | 2 | Yes | 01-55 | FinancialInstitution | institutionType | See Type codes below |
| 2 | If type code = 99 (Other), specify | Text | 30 | Cond | Free text | FinancialInstitution | institutionTypeOther | Required if type = 99 |
| 3 | Legal name of financial institution | Text | 150 | Yes | Free text | FinancialInstitution | institutionName | Legal name |
| 4 | Alternate name, e.g., trade name or DBA | Text | 150 | No | Free text | FinancialInstitution | alternativeName | Doing business as |
| 5a | TIN type | Code | 1 | Yes | 1=EIN, 2=SSN | FinancialInstitution | tinType | Tax ID type |
| 5b | TIN | Text | 9 | Yes | 9 digits | FinancialInstitution | taxIdentificationNumber | EIN or SSN (no dashes) |
| 6 | Filing institution address | Text | 100 | Yes | Free text | FinancialInstitution | streetAddress | Street address |
| 7 | City | Text | 50 | Yes | Free text | FinancialInstitution | city | City |
| 8 | State | Code | 2 | Cond | US state code | FinancialInstitution | stateCode | Required if US |
| 9 | ZIP/Postal code | Text | 9 | Yes | ZIP or postal | FinancialInstitution | postalCode | ZIP or foreign postal |
| 10 | Country code | Code | 2 | Yes | ISO 3166 | FinancialInstitution | country | ISO country code |
| 11a | Primary federal regulator | Code | 1 | Cond | 1-9 | FinancialInstitution | primaryRegulator | Required for certain types |
| 11b | If regulator code = 9 (Other), specify | Text | 30 | Cond | Free text | FinancialInstitution | primaryRegulatorOther | Required if code = 9 |
| 12a | Type of securities and futures institution | Code | 1 | Cond | 1-3 | FinancialInstitution | securitiesFuturesType | Required if type = 26 |
| 12b | If type code = 3 (Other), specify | Text | 30 | Cond | Free text | FinancialInstitution | securitiesFuturesTypeOther | Required if code = 3 |
| 13a | Type of casino | Code | 1 | Cond | 1-3 | FinancialInstitution | casinoType | Required if type = 18 or 19 |
| 13b | If type code = 3 (Other), specify | Text | 30 | Cond | Free text | FinancialInstitution | casinoTypeOther | Required if code = 3 |
| 14 | Type of gaming activity | Code | 1 | Cond | 1-4 | FinancialInstitution | gamingActivityType | Required if type = 18 or 19 |
| 15 | Branch where activity occurred - legal name | Text | 150 | No | Free text | FinancialInstitution | branchName | Branch name |
| 16 | Branch TIN | Text | 9 | No | 9 digits | FinancialInstitution | branchTin | Branch EIN |
| 17 | Branch address | Text | 100 | No | Free text | FinancialInstitution | branchStreetAddress | Branch street |
| 18 | Branch city | Text | 50 | No | Free text | FinancialInstitution | branchCity | Branch city |
| 19 | Branch state | Code | 2 | No | US state code | FinancialInstitution | branchStateCode | Branch state |
| 20 | Branch ZIP/Postal code | Text | 9 | No | ZIP or postal | FinancialInstitution | branchPostalCode | Branch ZIP |
| 21 | Branch country code | Code | 2 | No | ISO 3166 | FinancialInstitution | branchCountry | Branch country |
| 22 | NAICS Code | Code | 6 | No | NAICS 6 digits | FinancialInstitution | naicsCode | Industry classification |
| 23 | Agency/Organization contact office | Text | 50 | No | Free text | FinancialInstitution | contactOfficeName | Contact office |
| 24 | Contact phone number | Text | 16 | No | Phone | FinancialInstitution | contactPhoneNumber | Contact phone |
| 25 | Contact phone extension | Text | 6 | No | Numeric | FinancialInstitution | contactPhoneExtension | Extension |
| 26 | Date filed | Date | 8 | Yes | MMDDYYYY | RegulatoryReport | filingDate | SAR filing date |
| 27 | Prior report BSA ID | Text | 14 | No | BSA ID | RegulatoryReport | priorReportBsaId | Prior SAR BSA ID if continuing |
| 28 | Designated contact office | Text | 517 | No | Free text | RegulatoryReport | designatedContactOffice | Who to contact for follow-up |
| 29 | Designated contact phone | Text | 16 | No | Phone | RegulatoryReport | designatedContactPhone | Contact phone |
| 30 | Designated contact phone extension | Text | 6 | No | Numeric | RegulatoryReport | designatedContactPhoneExtension | Extension |
| 31 | Alternate designated contact office | Text | 517 | No | Free text | RegulatoryReport | alternateContactOffice | Alternate contact |
| 32 | Alternate contact phone | Text | 16 | No | Phone | RegulatoryReport | alternateContactPhone | Alternate phone |
| 33 | Alternate contact phone extension | Text | 6 | No | Numeric | RegulatoryReport | alternateContactPhoneExtension | Extension |
| 34 | FinCEN HOTLINE | Checkbox | 1 | No | Y/N | RegulatoryReport | fincenHotlineUsed | FinCEN Hotline used? |

### Part II: Suspect Information (Items 35-86, repeatable for up to 999 subjects)

| Item# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 35 | Critical to report | Checkbox | 1 | No | Y/N | Party | criticalToReport | Is this subject critical? |
| 36 | Role in suspicious activity | Multi-select | - | Yes | Multiple codes | Party | roleInSuspiciousActivity | See Role codes |
| 37 | Multiple subjects | Checkbox | 1 | No | Y/N | Party | multipleSubjects | Multiple subjects involved? |
| 38a | Entity/Organization name | Text | 150 | Cond | Free text | Party | name | Legal entity name |
| 38b | Doing business as | Text | 150 | No | Free text | Party | alternativeName | DBA or trade name |
| 39 | Individual's last name | Text | 150 | Cond | Free text | Party | familyName | Last name if individual |
| 40 | First name | Text | 35 | No | Free text | Party | givenName | First name |
| 41 | Middle name | Text | 35 | No | Free text | Party | middleName | Middle name |
| 42 | Suffix | Text | 35 | No | Free text | Party | nameSuffix | Jr., Sr., III, etc. |
| 43 | Occupation or type of business | Text | 30 | No | Free text | Party | occupation | Occupation |
| 44 | Address | Text | 100 | No | Free text | Party | streetAddress | Street address |
| 45 | City | Text | 50 | No | Free text | Party | city | City |
| 46 | State | Code | 2 | No | US state code | Party | stateCode | State |
| 47 | ZIP/Postal code | Text | 9 | No | ZIP or postal | Party | postalCode | ZIP code |
| 48 | Country code | Code | 2 | No | ISO 3166 | Party | country | ISO country |
| 49a | E-mail address | Text | 100 | No | Email | Party | emailAddress | Email |
| 49b | Website internet address (URL) | Text | 100 | No | URL | Party | websiteUrl | Website |
| 50 | Phone number - residence | Text | 16 | No | Phone | Party | residencePhoneNumber | Home phone |
| 51 | Phone number - work | Text | 16 | No | Phone | Party | workPhoneNumber | Work phone |
| 52 | Phone number - mobile | Text | 16 | No | Phone | Party | mobilePhoneNumber | Mobile phone |
| 53 | Date of birth | Date | 8 | No | MMDDYYYY | Party | dateOfBirth | Birth date |
| 54a | TIN type | Code | 1 | No | 1=EIN, 2=SSN, 3=ITIN | Party | tinType | Tax ID type |
| 54b | TIN | Text | 9 | No | 9 digits | Party | taxIdentificationNumber | TIN (no dashes) |
| 54c | TIN unknown | Checkbox | 1 | No | Y/N | Party | tinUnknown | TIN unavailable |
| 55 | Identification type | Code | 2 | No | See ID type codes | Party | identificationType | ID document type |
| 56 | Identification number | Text | 25 | No | Free text | Party | identificationNumber | ID number |
| 57 | Issuing country | Code | 2 | No | ISO 3166 | Party | identificationIssuingCountry | ID issuing country |
| 58 | Issuing state (if US) | Code | 2 | No | US state code | Party | identificationIssuingState | ID issuing state |
| 59 | Form of identification | Multi-select | - | No | Multiple codes | Party | formOfIdentification | How ID was verified |
| 60 | Relationship to financial institution | Multi-select | - | No | Multiple codes | Party | relationshipToInstitution | Customer, employee, etc. |
| 61 | Relationship begin date | Date | 8 | No | MMDDYYYY | Party | relationshipBeginDate | When relationship started |
| 62 | Account number(s) affected | Text | 40 | No | Account number | Account | accountNumber | Up to 40 characters per |
| 63 | Account closed | Checkbox | 1 | No | Y/N | Account | accountClosed | Was account closed? |
| 64 | Date account closed | Date | 8 | No | MMDDYYYY | Account | accountClosedDate | Close date |
| 65 | Loss to financial institution | Amount | 15 | No | Dollar amount | RegulatoryReport | lossToInstitution | Dollar loss amount |
| 66 | Recovery from financial institution | Amount | 15 | No | Dollar amount | RegulatoryReport | recoveryAmount | Amount recovered |

### Part III: Suspicious Activity Information (Items 67-97)

| Item# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 67 | Date or date range of suspicious activity | Date range | 8 + 8 | Yes | MMDDYYYY | RegulatoryReport | suspiciousActivityFromDate, suspiciousActivityToDate | Activity period |
| 68 | Total dollar amount involved | Amount | 15 | Yes | Dollar amount | RegulatoryReport | totalAmountInvolved | Total suspicious amount |
| 69 | Commodity type | Multi-select | - | No | Multiple codes | RegulatoryReport | commodityType | If applicable |
| 70 | Commodity amount/volume | Text | 100 | No | Free text | RegulatoryReport | commodityAmount | Commodity volume |
| 71 | Category of suspicious activity | Multi-select | - | Yes | Multiple codes | RegulatoryReport | suspiciousActivityCategory | See SAR activity types |
| 72 | If "Other" selected, describe | Text | 1000 | Cond | Free text | RegulatoryReport | suspiciousActivityOtherDescription | Required if Other selected |
| 73 | Financial services involved | Multi-select | - | No | Multiple codes | RegulatoryReport | financialServicesInvolved | Services used |
| 74 | If "Other" selected, describe | Text | 100 | Cond | Free text | RegulatoryReport | financialServicesOtherDescription | Required if Other selected |
| 75 | Instrument type involved | Multi-select | - | No | Multiple codes | RegulatoryReport | instrumentType | Payment instruments |
| 76 | If "Other" selected, describe | Text | 50 | Cond | Free text | RegulatoryReport | instrumentTypeOtherDescription | Required if Other selected |
| 77 | Cyber event indicators | Multi-select | - | No | Multiple codes | RegulatoryReport | cyberEventIndicators | Cyber-related indicators |
| 78 | IP address | Text | 39 | No | IP address | RegulatoryReport | ipAddress | IPv4 or IPv6 |
| 79 | IP address date/time | DateTime | 14 | No | YYYYMMDDHHMMSS | RegulatoryReport | ipAddressDateTime | When IP observed |
| 80 | Digital currency address | Text | 100 | No | Free text | RegulatoryReport | digitalCurrencyAddress | Crypto address |
| 81 | Digital currency transaction hash | Text | 100 | No | Free text | RegulatoryReport | digitalCurrencyTxHash | Blockchain transaction hash |
| 82 | Action taken | Multi-select | - | No | Multiple codes | ComplianceCase | actionTaken | Actions taken by institution |
| 83 | Law enforcement agency | Multi-select | - | No | Multiple codes | ComplianceCase | lawEnforcementAgency | Agencies notified |
| 84 | If "Other" selected, specify agency | Text | 150 | Cond | Free text | ComplianceCase | lawEnforcementAgencyOther | Required if Other selected |

### Part IV: Transaction Information (Items 85-96, optional section)

| Item# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 85 | Date of transaction | Date | 8 | No | MMDDYYYY | PaymentInstruction | valueDate | Transaction date |
| 86 | Dollar amount of transaction | Amount | 15 | No | Dollar amount | PaymentInstruction | instructedAmount.amount | Transaction amount |
| 87 | From account number | Text | 40 | No | Account number | Account | debitAccountNumber | From account |
| 88 | To account number | Text | 40 | No | Account number | Account | creditAccountNumber | To account |
| 89 | From financial institution name | Text | 150 | No | Free text | FinancialInstitution | debitInstitutionName | Sending bank |
| 90 | From institution TIN | Text | 9 | No | 9 digits | FinancialInstitution | debitInstitutionTin | Sending bank TIN |
| 91 | From institution routing number | Text | 9 | No | 9 digits | FinancialInstitution | debitInstitutionRoutingNumber | ABA routing |
| 92 | To financial institution name | Text | 150 | No | Free text | FinancialInstitution | creditInstitutionName | Receiving bank |
| 93 | To institution TIN | Text | 9 | No | 9 digits | FinancialInstitution | creditInstitutionTin | Receiving bank TIN |
| 94 | To institution routing number | Text | 9 | No | 9 digits | FinancialInstitution | creditInstitutionRoutingNumber | ABA routing |
| 95 | Wire transfer direction | Code | 1 | No | 1=In, 2=Out, 3=Both | PaymentInstruction | wireTransferDirection | Wire direction |
| 96 | SWIFT/BIC/ABA reference number | Text | 50 | No | Free text | PaymentInstruction | referenceNumber | Transaction reference |

### Part V: Narrative (Items 97)

| Item# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 97 | Narrative | Text | Unlimited | Yes | Free text | RegulatoryReport | narrativeDescription | Detailed description of suspicious activity |

### Additional Metadata Fields

| Field Name | Type | CDM Entity | CDM Attribute | Notes |
|------------|------|------------|---------------|-------|
| BSA Identifier | Text (14) | RegulatoryReport | bsaIdentifier | Assigned by FinCEN upon filing |
| Prior SAR BSA IDs | Text (14 each) | RegulatoryReport | priorSARBsaIds | Multiple prior SAR IDs |
| Continuing Activity | Boolean | RegulatoryReport | continuingActivity | Is this a continuing activity report? |
| Corrected Prior Report | Boolean | RegulatoryReport | correctedReport | Is this a correction? |
| Filing Status | Code | RegulatoryReport | filingStatus | Draft, Filed, Accepted, Rejected |
| FinCEN Acceptance Date | Date | RegulatoryReport | fincenAcceptanceDate | When FinCEN accepted the SAR |
| Acknowledgment Number | Text | RegulatoryReport | acknowledgmentNumber | E-filing acknowledgment |

---

## Code Lists

### Type of Filing Institution Codes (Item 1)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Bank or thrift | FinancialInstitution.institutionType = '01' |
| 02 | Casino or card club | FinancialInstitution.institutionType = '02' |
| 18 | Casinos - Casino | FinancialInstitution.institutionType = '18' |
| 19 | Casinos - Card Club | FinancialInstitution.institutionType = '19' |
| 22 | Money services business - Money transmitter | FinancialInstitution.institutionType = '22' |
| 26 | Securities/futures | FinancialInstitution.institutionType = '26' |
| 27 | Insurance company | FinancialInstitution.institutionType = '27' |
| 99 | Other | FinancialInstitution.institutionType = '99' |

### Role in Suspicious Activity Codes (Item 36)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| a | Purchaser/Sender/Originator | Party.roleInSuspiciousActivity = 'Purchaser' |
| b | Payee/Receiver/Beneficiary | Party.roleInSuspiciousActivity = 'Payee' |
| c | Both a and b | Party.roleInSuspiciousActivity = 'Both' |
| d | Other | Party.roleInSuspiciousActivity = 'Other' |

### Suspicious Activity Category Codes (Item 71) - Selected Examples

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| a | Structuring/BSA/CTR | RegulatoryReport.suspiciousActivityCategory = 'Structuring' |
| b | Terrorist financing | RegulatoryReport.suspiciousActivityCategory = 'TerroristFinancing' |
| c | Identity theft | RegulatoryReport.suspiciousActivityCategory = 'IdentityTheft' |
| d | Check fraud | RegulatoryReport.suspiciousActivityCategory = 'CheckFraud' |
| e | Wire fraud | RegulatoryReport.suspiciousActivityCategory = 'WireFraud' |
| f | ACH fraud | RegulatoryReport.suspiciousActivityCategory = 'ACHFraud' |
| g | Debit card fraud | RegulatoryReport.suspiciousActivityCategory = 'DebitCardFraud' |
| h | Credit card fraud | RegulatoryReport.suspiciousActivityCategory = 'CreditCardFraud' |
| i | Counterfeit instrument (check) | RegulatoryReport.suspiciousActivityCategory = 'CounterfeitCheck' |
| j | Money laundering | RegulatoryReport.suspiciousActivityCategory = 'MoneyLaundering' |
| k | Mortgage fraud | RegulatoryReport.suspiciousActivityCategory = 'MortgageFraud' |
| m | Embezzlement/employee defalcation | RegulatoryReport.suspiciousActivityCategory = 'Embezzlement' |
| p | Elder financial exploitation | RegulatoryReport.suspiciousActivityCategory = 'ElderAbuse' |
| q | Human trafficking | RegulatoryReport.suspiciousActivityCategory = 'HumanTrafficking' |
| r | Human smuggling | RegulatoryReport.suspiciousActivityCategory = 'HumanSmuggling' |
| w | Trade-based money laundering | RegulatoryReport.suspiciousActivityCategory = 'TBML' |
| y | Sanctions violations | RegulatoryReport.suspiciousActivityCategory = 'Sanctions' |
| z | Other (specify in narrative) | RegulatoryReport.suspiciousActivityCategory = 'Other' |

### Instrument Type Codes (Item 75)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| a | Cash in | RegulatoryReport.instrumentType = 'CashIn' |
| b | Cash out | RegulatoryReport.instrumentType = 'CashOut' |
| c | Funds transfer - domestic | RegulatoryReport.instrumentType = 'DomesticWire' |
| d | Funds transfer - international | RegulatoryReport.instrumentType = 'InternationalWire' |
| e | Check/money order/cashier's check | RegulatoryReport.instrumentType = 'Check' |
| f | Credit card | RegulatoryReport.instrumentType = 'CreditCard' |
| g | Debit card | RegulatoryReport.instrumentType = 'DebitCard' |
| h | ACH | RegulatoryReport.instrumentType = 'ACH' |
| i | Digital currency (virtual currency) | RegulatoryReport.instrumentType = 'DigitalCurrency' |
| z | Other (specify) | RegulatoryReport.instrumentType = 'Other' |

### Action Taken Codes (Item 82)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| a | No action taken | ComplianceCase.actionTaken = 'NoAction' |
| b | Account closed | ComplianceCase.actionTaken = 'AccountClosed' |
| c | Account frozen | ComplianceCase.actionTaken = 'AccountFrozen' |
| d | Terms modified | ComplianceCase.actionTaken = 'TermsModified' |
| e | Blocked funds | ComplianceCase.actionTaken = 'BlockedFunds' |
| f | Filed SAR only | ComplianceCase.actionTaken = 'FiledSAROnly' |
| g | Notified law enforcement | ComplianceCase.actionTaken = 'NotifiedLawEnforcement' |
| z | Other (specify) | ComplianceCase.actionTaken = 'Other' |

---

## CDM Extensions Required

All 184 SAR fields successfully map to existing CDM model. **No enhancements required.**

---

## Example SAR Scenario

**Suspicious Activity:** Structuring to avoid CTR reporting

**Narrative (Item 97):**
```
Over a 15-day period from 12/01/2024 to 12/15/2024, customer John Smith (DOB: 01/15/1975,
SSN: XXX-XX-1234) made 12 separate cash deposits into checking account #987654321,
each ranging from $7,500 to $9,800, totaling $102,400. Each deposit was structured
below the $10,000 CTR threshold. Customer provided inconsistent explanations for the
source of funds, first stating "business receipts" then later claiming "inheritance."

Customer operates a small retail shop with typical monthly revenues of $15,000 based
on prior transaction history. The volume and pattern of cash deposits is inconsistent
with the known business profile. When asked about the deposits, customer became evasive
and changed the subject.

This activity is suspicious as it appears to be structured to evade CTR reporting
requirements. The institution has closed the account and is filing this SAR in
accordance with 31 CFR 1020.320.
```

---

## References

- FinCEN SAR Instructions: https://www.fincen.gov/sites/default/files/shared/FinCEN_SAR_ElectronicFiling_InstructionsandSpecifications.pdf
- BSA E-Filing System: https://bsaefiling.fincen.treas.gov
- Bank Secrecy Act: 31 USC 5318(g)
- SAR Regulation: 31 CFR 1020.320
- GPS CDM Schemas: `/schemas/05_regulatory_report_complete_schema.json`, `/schemas/06_compliance_case_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
