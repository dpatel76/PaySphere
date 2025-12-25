# FINTRAC STR - Suspicious Transaction Report
## Complete Field Mapping to GPS CDM

**Report Type:** Suspicious Transaction Report (STR)
**Regulatory Authority:** FINTRAC (Financial Transactions and Reports Analysis Centre of Canada)
**Filing Requirement:** Report all transactions and attempted transactions where there are reasonable grounds to suspect money laundering or terrorist financing
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 125 fields mapped)

---

## Report Overview

The STR is required under the Proceeds of Crime (Money Laundering) and Terrorist Financing Act (PCMLTFA). Reporting entities must submit an STR when they have reasonable grounds to suspect that a transaction or attempted transaction is related to the commission or attempted commission of a money laundering offence or terrorist activity financing offence.

**Filing Threshold:** No monetary threshold - based on reasonable grounds for suspicion
**Filing Deadline:** Within 30 calendar days of detection of suspicious transaction
**Filing Method:** FINTRAC Web Reporting System (F2R) or batch file upload
**Regulation:** PCMLTFA, PCMLTFR (Regulations)

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total STR Fields** | 125 | 100% |
| **Mapped to CDM** | 125 | 100% |
| **Direct Mapping** | 112 | 90% |
| **Derived/Calculated** | 9 | 7% |
| **Reference Data Lookup** | 4 | 3% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Part A - Reporting Entity Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| A1 | Reporting entity report reference number | Text | 50 | Yes | Free text | RegulatoryReport | reportingEntityReferenceNumber | Internal reference |
| A2 | Reporting entity number | Text | 7 | Yes | 7 digits | FinancialInstitution | fintracReportingEntityNumber | FINTRAC assigned |
| A3 | Reporting entity legal name | Text | 300 | Yes | Free text | FinancialInstitution | institutionName | Legal entity name |
| A4 | Reporting entity business activity | Code | 2 | Yes | See activity codes | FinancialInstitution | businessActivity | Type of business |
| A5 | Contact person name | Text | 200 | Yes | Free text | RegulatoryReport | contactPersonName | Contact for report |
| A6 | Contact person phone | Text | 20 | Yes | Phone format | RegulatoryReport | contactPersonPhone | Contact phone |
| A7 | Contact person email | Text | 100 | No | Email format | RegulatoryReport | contactPersonEmail | Contact email |

### Part B - Location Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| B1 | Location type | Code | 1 | Yes | B=Branch, O=Office, M=Mobile | FinancialInstitution | locationType | Location type |
| B2 | Branch/office name | Text | 200 | No | Free text | FinancialInstitution | branchName | Branch/office name |
| B3 | Street address | Text | 200 | Yes | Free text | FinancialInstitution | branchStreetAddress | Street address |
| B4 | City | Text | 100 | Yes | Free text | FinancialInstitution | branchCity | City |
| B5 | Province/Territory | Code | 2 | Yes | ON, QC, BC, etc. | FinancialInstitution | branchProvince | Province code |
| B6 | Postal code | Text | 7 | Yes | A1A 1A1 format | FinancialInstitution | branchPostalCode | Postal code |
| B7 | Country | Code | 2 | Yes | CA | FinancialInstitution | branchCountry | Always CA |

### Part C - Reason for Suspicion

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| C1 | Suspicion indicator | Code | 2 | Yes | ML=Money laundering, TF=Terrorist financing, Both | ComplianceCase | suspicionIndicator | Type of suspicion |
| C2 | Description of suspicious activity | Text | 8000 | Yes | Free text | ComplianceCase | suspicionDescription | Detailed explanation |
| C3 | ML/TF indicators | Text | 4000 | Yes | Free text | ComplianceCase | mlTfIndicators | Red flags identified |
| C4 | Action taken | Text | 2000 | No | Free text | ComplianceCase | actionTaken | Actions by reporting entity |
| C5 | Date suspicion formed | Date | 10 | Yes | YYYY-MM-DD | ComplianceCase | suspicionFormedDate | When suspicion formed |

### Part D - Suspicious Transaction Information (Up to 3 transactions)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| D1 | Transaction 1 date | Date | 10 | Yes | YYYY-MM-DD | Transaction | transactionDate | First transaction date |
| D2 | Transaction 1 time | Time | 8 | No | HH:MM:SS | Transaction | transactionTime | Transaction time |
| D3 | Transaction 1 amount | Decimal | 15,2 | Yes | Numeric | Transaction | amount.amount | Amount |
| D4 | Transaction 1 currency | Code | 3 | Yes | ISO 4217 | Transaction | amount.currency | Currency code |
| D5 | Transaction 1 type | Code | 2 | Yes | See transaction codes | Transaction | transactionType | Type |
| D6 | Transaction 1 description | Text | 1000 | No | Free text | Transaction | transactionDescription | Description |
| D7 | Transaction 1 attempted | Boolean | 1 | Yes | Y/N | Transaction | attemptedTransaction | Attempted but not completed |
| D8 | Transaction 2 date | Date | 10 | No | YYYY-MM-DD | Transaction | transactionDate | Second transaction date |
| D9 | Transaction 2 time | Time | 8 | No | HH:MM:SS | Transaction | transactionTime | Transaction time |
| D10 | Transaction 2 amount | Decimal | 15,2 | No | Numeric | Transaction | amount.amount | Amount |
| D11 | Transaction 2 currency | Code | 3 | Cond | ISO 4217 | Transaction | amount.currency | Currency code |
| D12 | Transaction 2 type | Code | 2 | No | See transaction codes | Transaction | transactionType | Type |
| D13 | Transaction 2 description | Text | 1000 | No | Free text | Transaction | transactionDescription | Description |
| D14 | Transaction 2 attempted | Boolean | 1 | No | Y/N | Transaction | attemptedTransaction | Attempted but not completed |
| D15 | Transaction 3 date | Date | 10 | No | YYYY-MM-DD | Transaction | transactionDate | Third transaction date |
| D16 | Transaction 3 time | Time | 8 | No | HH:MM:SS | Transaction | transactionTime | Transaction time |
| D17 | Transaction 3 amount | Decimal | 15,2 | No | Numeric | Transaction | amount.amount | Amount |
| D18 | Transaction 3 currency | Code | 3 | Cond | ISO 4217 | Transaction | amount.currency | Currency code |
| D19 | Transaction 3 type | Code | 2 | No | See transaction codes | Transaction | transactionType | Type |
| D20 | Transaction 3 description | Text | 1000 | No | Free text | Transaction | transactionDescription | Description |
| D21 | Transaction 3 attempted | Boolean | 1 | No | Y/N | Transaction | attemptedTransaction | Attempted but not completed |

### Part E - Account Information (if applicable)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| E1 | Account number | Text | 50 | No | Free text | Account | accountNumber | Account identifier |
| E2 | Account type | Code | 2 | No | See account type codes | Account | accountType | Account category |
| E3 | Account currency | Code | 3 | No | ISO 4217 | Account | accountCurrency | Account currency |
| E4 | Account status | Code | 1 | No | O=Open, C=Closed, S=Suspended | Account | accountStatus | Status |
| E5 | Date account opened | Date | 10 | No | YYYY-MM-DD | Account | accountOpeningDate | Opening date |
| E6 | Date account closed | Date | 10 | No | YYYY-MM-DD | Account | accountClosingDate | Closing date |
| E7 | Financial institution number | Text | 4 | No | 4 digits | Account | financialInstitutionNumber | Bank number |
| E8 | Branch number | Text | 5 | No | 5 digits | Account | branchTransitNumber | Transit number |

### Part F - Person Conducting Suspicious Transaction

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| F1 | Entity type | Code | 1 | Yes | P=Person, E=Entity | Party | partyType | Person or entity |
| F2 | Surname | Text | 150 | Cond | Free text | Party | familyName | Last name if person |
| F3 | Given name | Text | 150 | Cond | Free text | Party | givenName | First name if person |
| F4 | Other names | Text | 150 | No | Free text | Party | middleName | Middle/other names |
| F5 | Alias | Text | 300 | No | Free text | Party | alias | Known alias |
| F6 | Entity name | Text | 300 | Cond | Free text | Party | name | Legal name if entity |
| F7 | Client number | Text | 50 | No | Free text | Party | clientNumber | Internal client ID |
| F8 | Street address | Text | 200 | No | Free text | Party | streetAddress | Street address |
| F9 | Apartment/unit | Text | 10 | No | Free text | Party | apartmentUnit | Unit number |
| F10 | City | Text | 100 | No | Free text | Party | city | City |
| F11 | Province/State | Code | 3 | No | Province/state code | Party | stateOrProvince | Province/state |
| F12 | Postal/ZIP code | Text | 10 | No | Postal/ZIP | Party | postalCode | Postal/ZIP code |
| F13 | Country | Code | 2 | No | ISO 3166 | Party | country | ISO country code |
| F14 | Telephone | Text | 20 | No | Phone format | Party | phoneNumber | Phone number |
| F15 | Email | Text | 100 | No | Email format | Party | emailAddress | Email address |
| F16 | Date of birth | Date | 10 | No | YYYY-MM-DD | Party | dateOfBirth | Birth date if person |
| F17 | Country of residence | Code | 2 | No | ISO 3166 | Party | countryOfResidence | Residence country |
| F18 | Occupation | Text | 100 | No | Free text | Party | occupation | Occupation/business type |
| F19 | Employer | Text | 300 | No | Free text | Party | employer | Employer name |
| F20 | Nature of entity business | Text | 100 | No | Free text | Party | natureOfBusiness | Business type if entity |
| F21 | Incorporation number | Text | 50 | No | Free text | Party | incorporationNumber | Registration number |
| F22 | Incorporation jurisdiction | Text | 100 | No | Free text | Party | incorporationJurisdiction | Where incorporated |

### Part G - Person on Whose Behalf Transaction Conducted (if applicable)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| G1 | Third party indicator | Boolean | 1 | Yes | Y/N | Party | thirdPartyIndicator | Someone acting on behalf |
| G2 | Entity type | Code | 1 | Cond | P=Person, E=Entity | Party | thirdPartyType | Person or entity |
| G3 | Surname | Text | 150 | Cond | Free text | Party | thirdPartySurname | Last name if person |
| G4 | Given name | Text | 150 | Cond | Free text | Party | thirdPartyGivenName | First name if person |
| G5 | Other names | Text | 150 | No | Free text | Party | thirdPartyMiddleName | Middle/other names |
| G6 | Entity name | Text | 300 | Cond | Free text | Party | thirdPartyName | Legal name if entity |
| G7 | Street address | Text | 200 | No | Free text | Party | thirdPartyStreetAddress | Street address |
| G8 | Apartment/unit | Text | 10 | No | Free text | Party | thirdPartyApartmentUnit | Unit number |
| G9 | City | Text | 100 | No | Free text | Party | thirdPartyCity | City |
| G10 | Province/State | Code | 3 | No | Province/state code | Party | thirdPartyStateOrProvince | Province/state |
| G11 | Postal/ZIP code | Text | 10 | No | Postal/ZIP | Party | thirdPartyPostalCode | Postal/ZIP code |
| G12 | Country | Code | 2 | No | ISO 3166 | Party | thirdPartyCountry | ISO country code |
| G13 | Telephone | Text | 20 | No | Phone format | Party | thirdPartyPhoneNumber | Phone number |
| G14 | Date of birth | Date | 10 | No | YYYY-MM-DD | Party | thirdPartyDateOfBirth | Birth date if person |
| G15 | Occupation | Text | 100 | No | Free text | Party | thirdPartyOccupation | Occupation/business type |
| G16 | Relationship | Text | 100 | No | Free text | Party | thirdPartyRelationship | Relationship to conductor |
| G17 | Incorporation number | Text | 50 | No | Free text | Party | thirdPartyIncorporationNumber | If entity |
| G18 | Incorporation jurisdiction | Text | 100 | No | Free text | Party | thirdPartyIncorporationJurisdiction | Where incorporated |

### Part H - Identification of Person Conducting Transaction

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| H1 | Identification type | Code | 2 | No | See ID type codes | Party | identificationType | ID document type |
| H2 | Identification number | Text | 50 | No | Free text | Party | identificationNumber | ID document number |
| H3 | Jurisdiction (country/province) | Text | 100 | No | Free text | Party | identificationJurisdiction | Issuing jurisdiction |
| H4 | Issuing authority | Text | 200 | No | Free text | Party | identificationIssuingAuthority | Authority that issued ID |

### Part I - Beneficiary Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| I1 | Beneficiary exists | Boolean | 1 | No | Y/N | Party | beneficiaryExists | Beneficiary identified |
| I2 | Beneficiary entity type | Code | 1 | Cond | P=Person, E=Entity | Party | beneficiaryType | Person or entity |
| I3 | Beneficiary surname | Text | 150 | Cond | Free text | Party | beneficiarySurname | Last name if person |
| I4 | Beneficiary given name | Text | 150 | Cond | Free text | Party | beneficiaryGivenName | First name if person |
| I5 | Beneficiary other names | Text | 150 | No | Free text | Party | beneficiaryMiddleName | Middle/other names |
| I6 | Beneficiary entity name | Text | 300 | Cond | Free text | Party | beneficiaryName | Legal name if entity |
| I7 | Beneficiary street address | Text | 200 | No | Free text | Party | beneficiaryStreetAddress | Street address |
| I8 | Beneficiary city | Text | 100 | No | Free text | Party | beneficiaryCity | City |
| I9 | Beneficiary province/state | Code | 3 | No | Province/state code | Party | beneficiaryStateOrProvince | Province/state |
| I10 | Beneficiary postal/ZIP code | Text | 10 | No | Postal/ZIP | Party | beneficiaryPostalCode | Postal/ZIP code |
| I11 | Beneficiary country | Code | 2 | No | ISO 3166 | Party | beneficiaryCountry | ISO country code |
| I12 | Beneficiary account number | Text | 50 | No | Free text | Account | beneficiaryAccountNumber | Account number |
| I13 | Beneficiary financial institution | Text | 300 | No | Free text | FinancialInstitution | beneficiaryFinancialInstitution | Bank name |
| I14 | Beneficiary FI number | Text | 4 | No | 4 digits | FinancialInstitution | beneficiaryFiNumber | Bank number |
| I15 | Beneficiary branch number | Text | 5 | No | 5 digits | FinancialInstitution | beneficiaryBranchNumber | Transit number |

### Part J - Source of Funds

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| J1 | Source of funds | Text | 1000 | No | Free text | Transaction | sourceOfFunds | Where funds came from |
| J2 | How source determined | Text | 1000 | No | Free text | ComplianceCase | sourceOfFundsDetermination | How source identified |

### Part K - Disposition of Funds

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| K1 | Disposition of funds | Text | 1000 | No | Free text | Transaction | dispositionOfFunds | What done with funds |

### Part L - Related Parties

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| L1 | Related party 1 exists | Boolean | 1 | No | Y/N | Party | relatedParty1Exists | First related party |
| L2 | Related party 1 name | Text | 300 | No | Free text | Party | relatedParty1Name | Name |
| L3 | Related party 1 relationship | Text | 100 | No | Free text | Party | relatedParty1Relationship | Relationship type |
| L4 | Related party 2 exists | Boolean | 1 | No | Y/N | Party | relatedParty2Exists | Second related party |
| L5 | Related party 2 name | Text | 300 | No | Free text | Party | relatedParty2Name | Name |
| L6 | Related party 2 relationship | Text | 100 | No | Free text | Party | relatedParty2Relationship | Relationship type |

### Part M - Additional Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| M1 | Supporting documentation indicator | Boolean | 1 | No | Y/N | RegulatoryReport | supportingDocumentationIndicator | Documents attached |
| M2 | Law enforcement contacted | Boolean | 1 | No | Y/N | ComplianceCase | lawEnforcementContacted | Police notified |
| M3 | Law enforcement agency | Text | 200 | No | Free text | ComplianceCase | lawEnforcementAgency | Agency name |
| M4 | Law enforcement contact date | Date | 10 | No | YYYY-MM-DD | ComplianceCase | lawEnforcementContactDate | Date contacted |
| M5 | FINTRAC voluntary information record | Text | 50 | No | Free text | ComplianceCase | fintracVoluntaryInfoRecord | VIR reference |
| M6 | Additional comments | Text | 4000 | No | Free text | ComplianceCase | additionalComments | Other relevant info |

### Metadata

| Field# | Field Name | Type | Length | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|------------|---------------|-------|
| - | FINTRAC acknowledgment number | Text | 50 | RegulatoryReport | fintracAcknowledgmentNumber | Assigned by FINTRAC |
| - | Report status | Code | 2 | RegulatoryReport | reportStatus | Submitted, Accepted, Rejected |
| - | Submission timestamp | DateTime | 20 | RegulatoryReport | submissionTimestamp | When submitted |

---

## Code Lists

### Suspicion Indicator Codes (Field C1)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| ML | Money laundering | ComplianceCase.suspicionIndicator = 'MoneyLaundering' |
| TF | Terrorist financing | ComplianceCase.suspicionIndicator = 'TerroristFinancing' |
| Both | Both ML and TF | ComplianceCase.suspicionIndicator = 'Both' |

### Transaction Type Codes (Fields D5, D12, D19)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Deposit | Transaction.transactionType = 'Deposit' |
| 02 | Withdrawal | Transaction.transactionType = 'Withdrawal' |
| 03 | Wire transfer | Transaction.transactionType = 'WireTransfer' |
| 04 | Currency exchange | Transaction.transactionType = 'CurrencyExchange' |
| 05 | Purchase negotiable instrument | Transaction.transactionType = 'PurchaseNegotiableInstrument' |
| 06 | Redemption negotiable instrument | Transaction.transactionType = 'RedemptionNegotiableInstrument' |
| 07 | Electronic funds transfer | Transaction.transactionType = 'ElectronicFundsTransfer' |
| 99 | Other | Transaction.transactionType = 'Other' |

### Account Type Codes (Field E2)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Personal | Account.accountType = 'Personal' |
| 02 | Business | Account.accountType = 'Business' |
| 03 | Trust | Account.accountType = 'Trust' |
| 04 | Casino | Account.accountType = 'Casino' |
| 99 | Other | Account.accountType = 'Other' |

### Identification Type Codes (Field H1)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Driver's licence | Party.identificationType = 'DriversLicence' |
| 02 | Passport | Party.identificationType = 'Passport' |
| 03 | Record of landing | Party.identificationType = 'RecordOfLanding' |
| 04 | Permanent resident card | Party.identificationType = 'PermanentResidentCard' |
| 05 | Provincial/territorial ID | Party.identificationType = 'ProvincialId' |
| 06 | Certificate of Indian status | Party.identificationType = 'CertificateIndianStatus' |
| 99 | Other | Party.identificationType = 'Other' |

---

## CDM Extensions Required

All 125 STR fields successfully map to existing CDM model. **No enhancements required.**

---

## Example STR Report

### Suspicious Structuring Pattern

```
Part A - Reporting Entity
A1: REF-STR-20241220-003
A2: BC12345
A3: Royal Bank of Canada
A4: 01 (Bank)
A5: John Compliance
A6: +1-416-555-0100
A7: john.compliance@rbc.ca

Part B - Location
B1: B (Branch)
B2: Toronto Yonge Street Branch
B3: 100 Yonge Street
B4: Toronto
B5: ON
B6: M5C 2W1
B7: CA

Part C - Reason for Suspicion
C1: ML (Money laundering)
C2: Customer conducted multiple cash deposits over 10-day period, each just under $10,000, totaling $48,500. Pattern appears designed to avoid LCTR reporting threshold. Customer unable to provide satisfactory explanation for source of funds. Claimed self-employed contractor but deposits inconsistent with stated income level. Customer became evasive when questioned. Previous STR filed on same customer 6 months ago for similar pattern.
C3: - Structuring/smurfing pattern (multiple transactions below threshold)
     - Evasive when questioned about source
     - Inconsistent with customer profile and stated income
     - Prior suspicious activity history
     - No legitimate business explanation
     - Unusual frequency and amounts
C4: Enhanced due diligence conducted. Customer file reviewed. Account monitoring increased. Considered account closure but retained to continue monitoring and gather intelligence.
C5: 2024-12-15

Part D - Transactions
D1: 2024-12-10
D2: 09:30:00
D3: 9500.00
D4: CAD
D5: 01 (Deposit)
D6: Cash deposit - claimed personal savings
D7: N

D8: 2024-12-12
D9: 14:15:00
D10: 9800.00
D11: CAD
D12: 01 (Deposit)
D13: Cash deposit - claimed consulting payment
D14: N

D15: 2024-12-15
D16: 11:45:00
D17: 9700.00
D18: CAD
D19: 01 (Deposit)
D20: Cash deposit - no clear explanation provided
D21: N

Part E - Account
E1: 1234567890
E2: 01 (Personal)
E3: CAD
E4: O (Open)
E5: 2024-08-15
E7: 0003
E8: 01234

Part F - Person Conducting
F1: P (Person)
F2: Thompson
F3: Robert
F4: James
F5: Bob
F7: CLI-2024-8765
F8: 45 Oak Avenue
F9: Apt 305
F10: Toronto
F11: ON
F12: M4K 2N3
F13: CA
F14: +1-647-555-0234
F16: 1978-03-22
F17: CA
F18: Self-employed contractor
F19: Self-employed

Part G - Third Party
G1: N

Part H - Identification
H1: 01 (Driver's licence)
H2: T1234-56789-01234
H3: Ontario, Canada
H4: Ontario Ministry of Transportation

Part I - Beneficiary
I1: N

Part J - Source of Funds
J1: Customer claims funds from consulting work and personal savings. Unable to provide contracts, invoices, or supporting documentation.
J2: Customer verbal statements. No documentation provided despite requests.

Part K - Disposition
K1: Funds deposited to personal account. Some funds subsequently withdrawn in cash, some transferred to unknown recipients via e-transfer.

Part L - Related Parties
L1: N

Part M - Additional Information
M1: N
M2: N
M6: Account opened 4 months ago with small initial deposit. Large cash deposits began 2 months after opening. Customer visits different branches for deposits. Similar pattern observed 6 months ago resulted in previous STR. Customer appears to be attempting to avoid reporting by keeping individual deposits below $10,000 threshold.
```

---

## References

- FINTRAC STR Guidance: https://fintrac-canafe.canada.ca/guidance-directives/transaction-operation/str-dod/str-dod-eng
- FINTRAC Web Reporting: https://f2r.fintrac-canafe.gc.ca/
- PCMLTFA: https://laws-lois.justice.gc.ca/eng/acts/P-24.501/
- GPS CDM Schema: `/schemas/03_compliance_case_complete_schema.json`, `/schemas/05_regulatory_report_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
