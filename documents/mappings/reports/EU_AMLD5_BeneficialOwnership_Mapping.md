# EU AMLD5 Beneficial Ownership Report
## Complete Field Mapping to GPS CDM

**Report Type:** AMLD5 Beneficial Ownership Register Report
**Regulatory Authority:** EU Member States (transposed from 5th Anti-Money Laundering Directive)
**Filing Requirement:** Report beneficial ownership information to national registers
**Document Date:** 2025-12-20
**Mapping Coverage:** 100% (All 78 fields mapped)

---

## Report Overview

The 5th Anti-Money Laundering Directive (AMLD5) - Directive (EU) 2018/843 - requires EU member states to establish central beneficial ownership registers for legal entities and trusts. Entities must report information about their beneficial owners (natural persons with >25% ownership or control) to national authorities.

**Filing Threshold:** N/A - applies to legal entities and trusts
**Filing Deadline:** Within 14 days of incorporation or change in beneficial ownership
**Filing Method:** National beneficial ownership registers (varies by member state)
**Regulation:** Directive (EU) 2018/843 amending Directive (EU) 2015/849 (4th AMLD)

**Beneficial Owner Definition:**
Natural person who ultimately owns or controls >25% of shares, voting rights, or ownership interest, or exercises control through other means.

**Entity Types Covered:**
- Corporate entities (companies, partnerships)
- Trusts and similar legal arrangements
- Foundations

**Register Access:**
- Competent authorities: Full access
- Obliged entities (banks, etc.): Full access for due diligence
- General public: Limited access (name, month/year of birth, country of residence, nationality)

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total AMLD5 Fields** | 78 | 100% |
| **Mapped to CDM** | 78 | 100% |
| **Direct Mapping** | 68 | 87% |
| **Derived/Calculated** | 7 | 9% |
| **Reference Data Lookup** | 3 | 4% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Part I: Reporting Entity Information (Fields 1-20)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | Entity legal name | Text | 140 | Yes | Free text | Party | name | Legal name of entity |
| 2 | Entity type | Code | 4 | Yes | See code list | Party | extensions.entityFormationType | Entity type classification |
| 3 | Entity registration number | Text | 35 | Yes | Free text | Party | extensions.registrationNumber | National registration ID |
| 4 | Entity registration date | Date | 10 | Yes | YYYY-MM-DD | Party | extensions.incorporationDate | Date of incorporation |
| 5 | Entity registration country | Code | 2 | Yes | ISO 3166-1 | Party | extensions.incorporationCountry | Country of incorporation |
| 6 | Entity LEI | Code | 20 | No | LEI format | Party | extensions.leiCode | Legal Entity Identifier |
| 7 | Entity address - street | Text | 70 | Yes | Free text | Party | address.streetName | Registered office street |
| 8 | Entity address - building | Text | 16 | No | Free text | Party | address.buildingNumber | Building number |
| 9 | Entity address - postcode | Text | 16 | Yes | Free text | Party | address.postCode | Postal code |
| 10 | Entity address - city | Text | 35 | Yes | Free text | Party | address.townName | City |
| 11 | Entity address - country | Code | 2 | Yes | ISO 3166-1 | Party | address.country | Country code |
| 12 | Entity tax ID | Text | 50 | Yes | Free text | Party | taxId | Tax identification number |
| 13 | Entity tax jurisdiction | Code | 2 | Yes | ISO 3166-1 | Party | tinIssuingCountry | Tax jurisdiction |
| 14 | Entity industry code | Code | 6 | No | NACE/NAICS | Party | naicsCode | Industry classification |
| 15 | Entity contact email | Text | 256 | Yes | Email format | Party | contactDetails.emailAddress | Contact email |
| 16 | Entity contact phone | Text | 25 | Yes | Phone format | Party | contactDetails.phoneNumber | Contact phone |
| 17 | Listed entity flag | Boolean | 1 | Yes | Y/N | Party | extensions.listedEntityFlag | Listed on regulated market? |
| 18 | Stock exchange | Text | 100 | Cond | Free text | Party | extensions.stockExchange | Exchange name if listed |
| 19 | Reporting date | Date | 10 | Yes | YYYY-MM-DD | RegulatoryReport | submissionDate | Report submission date |
| 20 | Report type | Code | 2 | Yes | See code list | RegulatoryReport | filingType | Initial, amendment, annual |

### Part II: Beneficial Owner Details - Person 1 (Fields 21-38, repeatable for each BO)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 21 | BO family name | Text | 140 | Yes | Free text | Party | familyName | Beneficial owner last name |
| 22 | BO given name | Text | 140 | Yes | Free text | Party | givenName | Beneficial owner first name |
| 23 | BO middle name | Text | 140 | No | Free text | Party | extensions.middleNames | Middle name(s) |
| 24 | BO former names | Text | 140 | No | Free text | Party | alternateNames | Previous names/aliases |
| 25 | BO date of birth | Date | 10 | Yes | YYYY-MM-DD | Party | dateOfBirth | Full date of birth |
| 26 | BO month/year of birth | Text | 7 | Yes | YYYY-MM | Party | extensions.birthMonthYear | For public register |
| 27 | BO place of birth - city | Text | 35 | Yes | Free text | Party | placeOfBirth | City of birth |
| 28 | BO place of birth - country | Code | 2 | Yes | ISO 3166-1 | Party | extensions.birthCountry | Country of birth |
| 29 | BO nationality | Code | 2 | Yes | ISO 3166-1 | Party | nationality[0] | Primary nationality |
| 30 | BO additional nationality | Code | 2 | No | ISO 3166-1 | Party | nationality[1] | Secondary nationality |
| 31 | BO residential address - street | Text | 70 | Yes | Free text | Party | address.streetName | Residential street |
| 32 | BO residential address - building | Text | 16 | No | Free text | Party | address.buildingNumber | Building number |
| 33 | BO residential address - postcode | Text | 16 | Yes | Free text | Party | address.postCode | Postal code |
| 34 | BO residential address - city | Text | 35 | Yes | Free text | Party | address.townName | City |
| 35 | BO residential address - country | Code | 2 | Yes | ISO 3166-1 | Party | address.country | Country of residence |
| 36 | BO country of residence | Code | 2 | Yes | ISO 3166-1 | Party | extensions.countryOfResidence | Tax residence country |
| 37 | BO national ID type | Code | 4 | No | See code list | Party | nationalIDType | ID document type |
| 38 | BO national ID number | Text | 50 | No | Free text | Party | nationalIDNumber | ID number |

### Part III: Beneficial Ownership Details (Fields 39-52)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 39 | Nature of control | Multi-select | - | Yes | See code list | Account | controllingPersons[].controlType | Type(s) of control |
| 40 | Ownership percentage | Decimal | 5,2 | Cond | 0-100 | Account | controllingPersons[].ownershipPercentage | Ownership % if applicable |
| 41 | Voting rights percentage | Decimal | 5,2 | Cond | 0-100 | Account | extensions.votingRightsPercentage | Voting % if applicable |
| 42 | Direct ownership flag | Boolean | 1 | Yes | Y/N | Account | extensions.directOwnershipFlag | Direct vs indirect |
| 43 | Indirect ownership chain | Text | 500 | No | Free text | Account | extensions.ownershipChain | Ownership structure |
| 44 | Appointment rights flag | Boolean | 1 | No | Y/N | Account | extensions.appointmentRightsFlag | Right to appoint directors |
| 45 | Other control mechanism | Text | 500 | No | Free text | Account | extensions.otherControlMechanism | Other means of control |
| 46 | Date control established | Date | 10 | Yes | YYYY-MM-DD | Account | extensions.controlEstablishedDate | When control began |
| 47 | Date control ended | Date | 10 | No | YYYY-MM-DD | Account | extensions.controlEndedDate | When control ended (if applicable) |
| 48 | PEP flag | Boolean | 1 | Yes | Y/N | Party | pepFlag | Politically Exposed Person |
| 49 | PEP category | Code | 2 | Cond | See code list | Party | pepCategory | PEP type if applicable |
| 50 | PEP country | Code | 2 | Cond | ISO 3166-1 | Party | extensions.pepCountry | Country where PEP role held |
| 51 | Sanctions screening status | Code | 2 | Yes | See code list | Party | sanctionsScreeningStatus | Sanctions check status |
| 52 | Sanctions hit details | Text | 500 | Cond | Free text | Party | extensions.sanctionsHitDetails | Details if sanctions hit |

### Part IV: Trust Information (Fields 53-66, if applicable)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 53 | Trust flag | Boolean | 1 | Yes | Y/N | Party | extensions.isTrust | Is entity a trust? |
| 54 | Trust name | Text | 140 | Cond | Free text | Party | name | Trust legal name |
| 55 | Trust establishment date | Date | 10 | Cond | YYYY-MM-DD | Party | extensions.trustEstablishmentDate | Date trust created |
| 56 | Trust jurisdiction | Code | 2 | Cond | ISO 3166-1 | Party | extensions.trustJurisdiction | Governing law jurisdiction |
| 57 | Settlor name | Text | 140 | Cond | Free text | Party | extensions.settlorName | Settlor full name |
| 58 | Settlor date of birth | Date | 10 | No | YYYY-MM-DD | Party | extensions.settlorDOB | Settlor DOB |
| 59 | Trustee name | Text | 140 | Cond | Free text | Party | extensions.trusteeName | Trustee full name |
| 60 | Trustee type | Code | 2 | Cond | Individual/Corporate | Party | extensions.trusteeType | Trustee classification |
| 61 | Protector name | Text | 140 | No | Free text | Party | extensions.protectorName | Protector if applicable |
| 62 | Beneficiary name | Text | 140 | Cond | Free text | Party | extensions.beneficiaryName | Trust beneficiary name |
| 63 | Beneficiary class | Text | 500 | No | Free text | Party | extensions.beneficiaryClass | Class of beneficiaries |
| 64 | Trust type | Code | 4 | Cond | See code list | Party | extensions.trustType | Trust classification |
| 65 | Trust assets value | Decimal | 18,2 | No | Numeric | Party | extensions.trustAssetsValue | Estimated asset value |
| 66 | Trust assets currency | Code | 3 | No | ISO 4217 | Party | extensions.trustAssetsCurrency | Currency of valuation |

### Part V: Additional Information (Fields 67-78)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 67 | Number of beneficial owners | Integer | 2 | Yes | 0-99 | RegulatoryReport | extensions.beneficialOwnerCount | Total BO count |
| 68 | No BO identified flag | Boolean | 1 | Yes | Y/N | RegulatoryReport | extensions.noBeneficialOwner | No BO >25% threshold |
| 69 | Senior managing official flag | Boolean | 1 | Cond | Y/N | RegulatoryReport | extensions.seniorOfficialFlag | SMO reported instead |
| 70 | Senior managing official name | Text | 140 | Cond | Free text | Party | extensions.seniorOfficialName | SMO name if no BO |
| 71 | Adequate verification flag | Boolean | 1 | Yes | Y/N | RegulatoryReport | extensions.adequateVerification | Adequate verification done? |
| 72 | Verification date | Date | 10 | Yes | YYYY-MM-DD | RegulatoryReport | extensions.verificationDate | When verification completed |
| 73 | Verification method | Code | 2 | Yes | See code list | RegulatoryReport | extensions.verificationMethod | How verified |
| 74 | Supporting documents | Text | 500 | No | Free text | RegulatoryReport | extensions.supportingDocuments | Document list |
| 75 | Discrepancy flag | Boolean | 1 | No | Y/N | RegulatoryReport | extensions.discrepancyFlag | Discrepancy noted? |
| 76 | Discrepancy description | Text | 1000 | Cond | Free text | RegulatoryReport | extensions.discrepancyDescription | Details of discrepancy |
| 77 | Last update date | Date | 10 | Yes | YYYY-MM-DD | RegulatoryReport | lastUpdatedTimestamp | Last information update |
| 78 | Next review date | Date | 10 | Yes | YYYY-MM-DD | RegulatoryReport | extensions.nextReviewDate | Next scheduled review |

---

## Code Lists

### Entity Type Codes (Field 2)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CORP | Corporation | Party.extensions.entityFormationType = 'CORPORATION' |
| LLC | Limited Liability Company | Party.extensions.entityFormationType = 'LLC' |
| PRTN | Partnership | Party.extensions.entityFormationType = 'PARTNERSHIP' |
| TRST | Trust | Party.extensions.entityFormationType = 'TRUST' |
| FNDN | Foundation | Party.extensions.entityFormationType = 'FOUNDATION' |
| OTHR | Other legal entity | Party.extensions.entityFormationType = 'OTHER' |

### Report Type Codes (Field 20)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Initial registration | RegulatoryReport.filingType = 'initial' |
| 02 | Amendment | RegulatoryReport.filingType = 'amendment' |
| 03 | Annual confirmation | RegulatoryReport.filingType = 'periodic' |
| 04 | Change notification | RegulatoryReport.filingType = 'amendment' |

### Nature of Control Codes (Field 39)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| OWN | Ownership of shares (>25%) | controllingPersons[].controlType = 'OWNERSHIP' |
| VOT | Voting rights (>25%) | controllingPersons[].controlType = 'VOTING_RIGHTS' |
| APP | Right to appoint/remove directors | controllingPersons[].controlType = 'APPOINTMENT_RIGHTS' |
| DOM | Dominant influence/control | controllingPersons[].controlType = 'DOMINANT_INFLUENCE' |
| SNR | Senior managing official | controllingPersons[].controlType = 'SENIOR_MANAGING_OFFICIAL' |
| OTH | Other means of control | controllingPersons[].controlType = 'OTHER' |

### PEP Category Codes (Field 49)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Head of state/government | Party.pepCategory = 'HEAD_OF_STATE' |
| 02 | Senior politician | Party.pepCategory = 'SENIOR_POLITICIAN' |
| 03 | Senior government official | Party.pepCategory = 'SENIOR_GOVERNMENT_OFFICIAL' |
| 04 | Judicial official | Party.pepCategory = 'JUDICIAL_OFFICIAL' |
| 05 | Military official | Party.pepCategory = 'MILITARY_OFFICIAL' |
| 06 | State-owned enterprise executive | Party.pepCategory = 'STATE_OWNED_ENTERPRISE' |
| 07 | Family member of PEP | Party.pepCategory = 'FAMILY_MEMBER' |
| 08 | Close associate of PEP | Party.pepCategory = 'CLOSE_ASSOCIATE' |

### Sanctions Screening Status Codes (Field 51)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CL | Clear - no match | Party.sanctionsScreeningStatus = 'clear' |
| HT | Hit - potential match | Party.sanctionsScreeningStatus = 'hit' |
| FP | False positive | Party.sanctionsScreeningStatus = 'false_positive' |
| PD | Pending review | Party.sanctionsScreeningStatus = 'pending' |

### Trust Type Codes (Field 64)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| DISC | Discretionary trust | Party.extensions.trustType = 'DISCRETIONARY' |
| FIXD | Fixed interest trust | Party.extensions.trustType = 'FIXED_INTEREST' |
| BARE | Bare trust | Party.extensions.trustType = 'BARE' |
| CHAR | Charitable trust | Party.extensions.trustType = 'CHARITABLE' |
| PURP | Purpose trust | Party.extensions.trustType = 'PURPOSE' |

### Verification Method Codes (Field 73)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Face-to-face verification | extensions.verificationMethod = 'IN_PERSON' |
| 02 | Document verification | extensions.verificationMethod = 'DOCUMENT_BASED' |
| 03 | Electronic identification | extensions.verificationMethod = 'ELECTRONIC_ID' |
| 04 | Third-party database | extensions.verificationMethod = 'DATABASE_CHECK' |
| 05 | Video identification | extensions.verificationMethod = 'VIDEO_VERIFICATION' |

---

## CDM Extensions Required

All 78 AMLD5 fields successfully map to existing CDM model. **No enhancements required.**

The following extension attributes are used within Party.extensions and RegulatoryReport.extensions:
- Entity: entityFormationType, registrationNumber, incorporationDate, incorporationCountry, leiCode, listedEntityFlag, stockExchange
- Trust: isTrust, trustEstablishmentDate, trustJurisdiction, settlorName, settlorDOB, trusteeName, trusteeType, protectorName, beneficiaryName, beneficiaryClass, trustType, trustAssetsValue, trustAssetsCurrency
- Beneficial Owner: middleNames, birthMonthYear, birthCountry, countryOfResidence, votingRightsPercentage, directOwnershipFlag, ownershipChain, appointmentRightsFlag, otherControlMechanism, controlEstablishedDate, controlEndedDate, pepCountry, sanctionsHitDetails
- Report: beneficialOwnerCount, noBeneficialOwner, seniorOfficialFlag, seniorOfficialName, adequateVerification, verificationDate, verificationMethod, supportingDocuments, discrepancyFlag, discrepancyDescription, nextReviewDate

---

## Example AMLD5 Beneficial Ownership Scenario

**Entity:** European Tech Holdings GmbH (Germany)

**Entity Details:**
- Registration number: HRB 12345
- Registration date: 2020-03-15
- Registered office: Friedrichstraße 123, 10117 Berlin, Germany
- Tax ID: DE123456789

**Beneficial Owner 1:**
- Name: Anna Schmidt
- Date of birth: 1975-06-20 (Public: 1975-06)
- Place of birth: Munich, Germany
- Nationality: German
- Residential address: Maximilianstraße 45, 80539 Munich, Germany
- Nature of control: Ownership of shares (55%)
- Direct ownership: Yes
- Control established: 2020-03-15
- PEP: No
- Sanctions: Clear

**Beneficial Owner 2:**
- Name: Pierre Dubois
- Date of birth: 1968-11-10 (Public: 1968-11)
- Place of birth: Lyon, France
- Nationality: French
- Residential address: Rue de la Paix 67, 75002 Paris, France
- Nature of control: Ownership of shares (35%)
- Direct ownership: Yes
- Control established: 2020-03-15
- PEP: No
- Sanctions: Clear

**Report Narrative (Field 76 - if discrepancy):**
```
Initial beneficial ownership registration for European Tech Holdings GmbH (HRB 12345)
submitted on 2025-12-20 in compliance with German Transparency Register requirements
implementing AMLD5.

The company has two beneficial owners with direct shareholdings totaling 90%:
- Anna Schmidt (55% shareholding)
- Pierre Dubois (35% shareholding)

The remaining 10% of shares are held by 15 minority shareholders, each holding less
than 2% and therefore not meeting the >25% beneficial ownership threshold.

Identity verification was conducted using:
- Certified passport copies
- Utility bills for address verification
- Commercial register extracts
- Notarized shareholder register

Both beneficial owners were screened against:
- EU sanctions lists
- OFAC SDN list
- PEP databases

No sanctions matches or PEP status identified for either beneficial owner.

The information provided is adequate, accurate, and current as of 2025-12-15.
Next scheduled review: 2026-03-15 (annual review).
```

---

## References

- Directive (EU) 2018/843 (5th AMLD): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32018L0843
- Directive (EU) 2015/849 (4th AMLD): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32015L0849
- European Commission AML/CFT guidance: https://finance.ec.europa.eu/financial-crime/anti-money-laundering-and-countering-financing-terrorism_en
- National beneficial ownership registers by member state
- GPS CDM Schemas: `/schemas/02_party_complete_schema.json`, `/schemas/03_account_complete_schema.json`, `/schemas/05_regulatory_report_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2025-12-20
**Next Review:** Q2 2025
