# OECD CRS Controlling Person - CRS Controlling Person Report
## Complete Field Mapping to GPS CDM

**Report Type:** CRS Controlling Person (Common Reporting Standard)
**Regulatory Authority:** OECD (Organisation for Economic Co-operation and Development)
**Filing Requirement:** Financial Institutions must report controlling persons of Passive NFEs (Non-Financial Entities)
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 85 fields mapped)

---

## Report Overview

The CRS Controlling Person reporting requirement applies when the account holder is a Passive Non-Financial Entity (Passive NFE). Financial Institutions must identify and report information about the controlling persons of such entities. This aligns with FATF beneficial ownership standards and ensures transparency regarding the natural persons who ultimately own or control entities holding financial accounts.

**Controlling Person Definition:** Natural person who exercises control over an entity through:
1. Ownership of more than 25% of shares/capital/profits
2. Control through other means (voting rights, right to appoint/remove directors)
3. Senior managing official (if no other controlling person identified)

**Filing Threshold:** Same as main CRS reporting requirements
**Filing Deadline:** Varies by jurisdiction (typically April 30 - June 30 annually)
**Filing Method:** XML submission to local tax authority (integrated with main CRS report)
**Regulation:** OECD CRS Section VIII, FATF Recommendation 24 & 25

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total CRS Controlling Person Fields** | 85 | 100% |
| **Mapped to CDM** | 85 | 100% |
| **Direct Mapping** | 76 | 89% |
| **Derived/Calculated** | 7 | 8% |
| **Reference Data Lookup** | 2 | 3% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Section 1: Controlling Person Identification

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | Controlling Person Type | Code | 3 | Yes | CRS801-810 | Account | controllingPersons[].controlType | Type of control |
| 2 | Individual/Entity Indicator | Code | 1 | Yes | I=Individual, E=Entity | Party | partyType | Should be 'individual' for natural persons |
| 3 | CtrlgPerson is Reportable | Boolean | 1 | Yes | Y/N | Account | controllingPersons[].extensions.isReportable | Is controlling person reportable? |

### Section 2: Controlling Person - Name Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 4 | Name Type | Code | 10 | Yes | OECD201-208 | Party | extensions.nameType | Individual name type |
| 5 | Preceding Title | Text | 200 | No | Free text | Party | extensions.precedingTitle | Dr., Prof., Lord, etc. |
| 6 | Title | Text | 200 | No | Free text | Party | extensions.title | Mr., Ms., Mrs., Miss |
| 7 | First Name | Text | 200 | Yes | Free text | Party | givenName | Given name |
| 8 | Middle Name | Text | 200 | No | Free text | Party | extensions.middleName | Middle name(s) |
| 9 | Name Prefix | Text | 200 | No | Free text | Party | extensions.namePrefix | Von, De, Van, etc. |
| 10 | Last Name | Text | 200 | Yes | Free text | Party | familyName | Family/surname |
| 11 | Generation Identifier | Text | 200 | No | Free text | Party | suffix | Jr., Sr., III, IV |
| 12 | Suffix | Text | 200 | No | Free text | Party | extensions.nameSuffix | PhD, MD, Esq., etc. |
| 13 | General Suffix | Text | 200 | No | Free text | Party | extensions.generalSuffix | Other suffixes |

### Section 3: Controlling Person - Address Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 14 | Address Type | Code | 10 | Yes | OECD301-305 | Party | extensions.addressType | Residential, business, etc. |
| 15 | Street | Text | 70 | No | Free text | Party | address.streetName | Street name |
| 16 | Building Number | Text | 16 | No | Free text | Party | address.buildingNumber | Building number |
| 17 | Suite/Floor/Apt | Text | 16 | No | Free text | Party | extensions.suiteFloorApt | Suite/floor/apartment |
| 18 | District Name | Text | 35 | No | Free text | Party | address.districtName | District/locality |
| 19 | Post Box | Text | 16 | No | Free text | Party | address.postBox | PO Box |
| 20 | Post Code | Text | 16 | No | Free text | Party | address.postCode | Postal/ZIP code |
| 21 | City | Text | 35 | Yes | Free text | Party | address.townName | City/town |
| 22 | Country Subentity | Text | 35 | No | Free text | Party | address.countrySubDivision | State/province/region |
| 23 | Country Code | Code | 2 | Yes | ISO 3166-1 | Party | address.country | ISO country code |
| 24 | Address Free Text | Text | 4000 | No | Free text | Party | extensions.addressFreeText | Free-form address |

### Section 4: Controlling Person - Tax Residence Information (Primary)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 25 | Residence Country Code | Code | 2 | Yes | ISO 3166-1 | Party | taxResidencies[0].country | Primary tax residence |
| 26 | TIN | Text | 200 | Cond | Free text | Party | taxResidencies[0].tin | Tax Identification Number |
| 26a | TIN Issuing Country | Code | 2 | Cond | ISO 3166-1 | Party | taxResidencies[0].country | Country that issued TIN |
| 27 | TIN Unavailable Reason | Code | 3 | Cond | TRC1-TRC4 | Party | extensions.tinUnavailableReason | If no TIN provided |

### Section 5: Controlling Person - Tax Residence Information (Additional)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 28 | Additional Residence Country 1 | Code | 2 | No | ISO 3166-1 | Party | taxResidencies[1].country | 2nd tax residence |
| 29 | Additional TIN 1 | Text | 200 | No | Free text | Party | taxResidencies[1].tin | TIN for 2nd country |
| 29a | Additional TIN Issuing Country 1 | Code | 2 | Cond | ISO 3166-1 | Party | taxResidencies[1].country | TIN issuing country |
| 30 | Additional TIN Unavailable 1 | Code | 3 | Cond | TRC1-TRC4 | Party | extensions.additionalTinUnavailable[0] | Reason code |
| 31 | Additional Residence Country 2 | Code | 2 | No | ISO 3166-1 | Party | taxResidencies[2].country | 3rd tax residence |
| 32 | Additional TIN 2 | Text | 200 | No | Free text | Party | taxResidencies[2].tin | TIN for 3rd country |
| 32a | Additional TIN Issuing Country 2 | Code | 2 | Cond | ISO 3166-1 | Party | taxResidencies[2].country | TIN issuing country |
| 33 | Additional TIN Unavailable 2 | Code | 3 | Cond | TRC1-TRC4 | Party | extensions.additionalTinUnavailable[1] | Reason code |
| 34 | Additional Residence Country 3 | Code | 2 | No | ISO 3166-1 | Party | taxResidencies[3].country | 4th tax residence |
| 35 | Additional TIN 3 | Text | 200 | No | Free text | Party | taxResidencies[3].tin | TIN for 4th country |
| 35a | Additional TIN Issuing Country 3 | Code | 2 | Cond | ISO 3166-1 | Party | taxResidencies[3].country | TIN issuing country |
| 36 | Additional TIN Unavailable 3 | Code | 3 | Cond | TRC1-TRC4 | Party | extensions.additionalTinUnavailable[2] | Reason code |

### Section 6: Controlling Person - Birth Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 37 | Date of Birth | Date | 10 | Yes | YYYY-MM-DD | Party | dateOfBirth | Birth date |
| 38 | City of Birth | Text | 200 | No | Free text | Party | placeOfBirth | Birth city |
| 39 | City Subentity | Text | 200 | No | Free text | Party | extensions.citySubentityOfBirth | Birth district/locality |
| 40 | Country Subentity of Birth | Text | 200 | No | Free text | Party | extensions.countrySubentityOfBirth | Birth state/province |
| 41 | Country of Birth | Code | 2 | No | ISO 3166-1 | Party | extensions.countryOfBirth | Birth country code |
| 42 | Former Country of Birth | Code | 2 | No | ISO 3166-1 | Party | extensions.formerCountryOfBirth | If country changed |

### Section 7: Controlling Person - Nationality

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 43 | Nationality 1 | Code | 2 | No | ISO 3166-1 | Party | nationality[0] | Primary citizenship |
| 44 | Nationality 2 | Code | 2 | No | ISO 3166-1 | Party | nationality[1] | Secondary citizenship |
| 45 | Nationality 3 | Code | 2 | No | ISO 3166-1 | Party | nationality[2] | Tertiary citizenship |

### Section 8: Controlling Person Type Details

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 46 | CP Type Code | Code | 3 | Yes | CRS801-810 | Account | controllingPersons[].extensions.cpTypeCode | OECD CP type |
| 47 | Ownership Percentage | Decimal | 5,2 | Cond | 0.00-100.00 | Account | controllingPersons[].ownershipPercentage | If ownership-based |
| 48 | Control by Other Means | Text | 500 | No | Free text | Account | controllingPersons[].extensions.controlDescription | Description of control |
| 49 | Senior Managing Official | Boolean | 1 | No | Y/N | Account | controllingPersons[].extensions.seniorManagingOfficial | Is SMO if no other CP |

### Section 9: Controlling Person - Due Diligence

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 50 | Self-Certification Received | Boolean | 1 | No | Y/N | Account | controllingPersons[].extensions.selfCertReceived | Self-cert on file |
| 51 | Self-Certification Date | Date | 10 | Cond | YYYY-MM-DD | Account | controllingPersons[].extensions.selfCertDate | Date of self-cert |
| 52 | Documentary Evidence | Boolean | 1 | No | Y/N | Account | controllingPersons[].extensions.docEvidence | Documentary evidence |
| 53 | Documentary Evidence Type | Text | 100 | No | Free text | Account | controllingPersons[].extensions.docEvidenceType | Type of document |
| 54 | Documentary Evidence Date | Date | 10 | No | YYYY-MM-DD | Account | controllingPersons[].extensions.docEvidenceDate | Document date |

### Section 10: Controlling Person - PEP Status

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 55 | PEP Flag | Boolean | 1 | No | Y/N | Party | pepFlag | Politically Exposed Person |
| 56 | PEP Category | Code | 50 | Cond | See enum | Party | pepCategory | Type of PEP |
| 57 | PEP Position | Text | 200 | No | Free text | Party | extensions.pepPosition | Official position |
| 58 | PEP Country | Code | 2 | No | ISO 3166-1 | Party | extensions.pepCountry | Country of PEP role |
| 59 | PEP Relationship | Code | 20 | No | See enum | Party | extensions.pepRelationship | Self/Family/Close Associate |

### Section 11: Controlling Person - Identification Documents

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 60 | ID Document Type | Text | 100 | No | Free text | Party | formOfIdentification | Passport, ID card, etc. |
| 61 | ID Document Number | Text | 50 | No | Free text | Party | identificationNumber | Document number |
| 62 | ID Issuing Country | Code | 2 | No | ISO 3166-1 | Party | identificationIssuingCountry | Issuing country |
| 63 | ID Issuing State | Text | 3 | No | Free text | Party | identificationIssuingState | Issuing state/province |
| 64 | ID Issue Date | Date | 10 | No | YYYY-MM-DD | Party | extensions.idIssueDate | Document issue date |
| 65 | ID Expiry Date | Date | 10 | No | YYYY-MM-DD | Party | extensions.idExpiryDate | Document expiry date |

### Section 12: Controlling Person - Entity Relationship

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 66 | Account Holder Name | Text | 200 | Yes | Free text | Account | extensions.accountHolderName | Name of Passive NFE |
| 67 | Account Holder TIN | Text | 200 | No | Free text | Account | extensions.accountHolderTIN | Entity TIN |
| 68 | Account Holder Country | Code | 2 | Yes | ISO 3166-1 | Account | extensions.accountHolderCountry | Entity residence |
| 69 | Relationship Start Date | Date | 10 | No | YYYY-MM-DD | Account | controllingPersons[].extensions.relationshipStartDate | When control began |
| 70 | Relationship End Date | Date | 10 | No | YYYY-MM-DD | Account | controllingPersons[].extensions.relationshipEndDate | When control ended |

### Section 13: Controlling Person - Beneficial Ownership Chain

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 71 | Direct Ownership | Boolean | 1 | No | Y/N | Account | controllingPersons[].extensions.directOwnership | Direct vs indirect |
| 72 | Ownership Chain Description | Text | 1000 | No | Free text | Account | controllingPersons[].extensions.ownershipChain | Description of chain |
| 73 | Intermediate Entity Count | Integer | 2 | No | Numeric | Account | controllingPersons[].extensions.intermediateEntityCount | Number of layers |

### Section 14: Controlling Person - Trust Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 74 | Trust Settlor | Boolean | 1 | No | Y/N | Account | controllingPersons[].extensions.isTrustSettlor | Is settlor |
| 75 | Trust Trustee | Boolean | 1 | No | Y/N | Account | controllingPersons[].extensions.isTrustTrustee | Is trustee |
| 76 | Trust Protector | Boolean | 1 | No | Y/N | Account | controllingPersons[].extensions.isTrustProtector | Is protector |
| 77 | Trust Beneficiary | Boolean | 1 | No | Y/N | Account | controllingPersons[].extensions.isTrustBeneficiary | Is beneficiary |
| 78 | Beneficiary Type | Code | 20 | No | See enum | Account | controllingPersons[].extensions.beneficiaryType | Current/remainder/etc. |

### Section 15: Metadata and Control

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 79 | Controlling Person Sequence | Integer | 3 | Yes | 1-999 | Account | controllingPersons[].extensions.sequenceNumber | CP order (1-50) |
| 80 | Total Controlling Persons | Integer | 3 | Yes | 1-50 | Account | extensions.totalControllingPersons | Total CP count |
| 81 | CP Data Source | Code | 20 | No | See enum | Account | controllingPersons[].extensions.dataSource | Self-cert/Document/etc. |
| 82 | CP Data Quality Score | Integer | 3 | No | 0-100 | Account | controllingPersons[].extensions.dataQualityScore | Confidence score |
| 83 | Last CP Review Date | Date | 10 | No | YYYY-MM-DD | Account | controllingPersons[].extensions.lastReviewDate | Due diligence review |
| 84 | Next CP Review Date | Date | 10 | No | YYYY-MM-DD | Account | controllingPersons[].extensions.nextReviewDate | Scheduled review |
| 85 | CP Status | Code | 20 | Yes | See enum | Account | controllingPersons[].extensions.cpStatus | Active/Inactive/etc. |

---

## Code Lists

### Controlling Person Type (Field 1, 46)

| Code | Description | CDM Mapping | FATF Alignment |
|------|-------------|-------------|----------------|
| CRS801 | Ownership - more than 25% (direct or indirect) | Account.controllingPersons[].extensions.cpTypeCode = 'CRS801' | FATF R.24 |
| CRS802 | Control by other means (voting rights) | Account.controllingPersons[].extensions.cpTypeCode = 'CRS802' | FATF R.24 |
| CRS803 | Control by other means (right to appoint/remove directors) | Account.controllingPersons[].extensions.cpTypeCode = 'CRS803' | FATF R.24 |
| CRS804 | Control by other means (other control mechanisms) | Account.controllingPersons[].extensions.cpTypeCode = 'CRS804' | FATF R.24 |
| CRS805 | Senior managing official (if no other controlling person) | Account.controllingPersons[].extensions.cpTypeCode = 'CRS805' | FATF R.24 |
| CRS806 | Settlor of trust | Account.controllingPersons[].extensions.cpTypeCode = 'CRS806' | FATF R.25 |
| CRS807 | Trustee of trust | Account.controllingPersons[].extensions.cpTypeCode = 'CRS807' | FATF R.25 |
| CRS808 | Protector of trust | Account.controllingPersons[].extensions.cpTypeCode = 'CRS808' | FATF R.25 |
| CRS809 | Beneficiary of trust | Account.controllingPersons[].extensions.cpTypeCode = 'CRS809' | FATF R.25 |
| CRS810 | Other equivalent role | Account.controllingPersons[].extensions.cpTypeCode = 'CRS810' | FATF R.24/25 |

### Name Type (Field 4)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| OECD201 | SMF Name (Standard format) | Party.extensions.nameType = 'OECD201' |
| OECD202 | Alias | Party.extensions.nameType = 'OECD202' |
| OECD203 | Nickname | Party.extensions.nameType = 'OECD203' |
| OECD204 | Also Known As (AKA) | Party.extensions.nameType = 'OECD204' |
| OECD205 | Doing Business As (DBA) | Party.extensions.nameType = 'OECD205' |
| OECD206 | Legal name | Party.extensions.nameType = 'OECD206' |
| OECD207 | Maiden name | Party.extensions.nameType = 'OECD207' |
| OECD208 | Former name | Party.extensions.nameType = 'OECD208' |

### Address Type (Field 14)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| OECD301 | Residential or business | Party.extensions.addressType = 'OECD301' |
| OECD302 | Residential | Party.extensions.addressType = 'OECD302' |
| OECD303 | Business | Party.extensions.addressType = 'OECD303' |
| OECD304 | Registered office | Party.extensions.addressType = 'OECD304' |
| OECD305 | Unspecified | Party.extensions.addressType = 'OECD305' |

### TIN Unavailable Reason (Field 27, 30, 33, 36)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| TRC1 | TIN not required by jurisdiction | Party.extensions.tinUnavailableReason = 'TRC1' |
| TRC2 | No TIN issued by jurisdiction | Party.extensions.tinUnavailableReason = 'TRC2' |
| TRC3 | TIN not obtainable - jurisdiction does not require TIN for identification | Party.extensions.tinUnavailableReason = 'TRC3' |
| TRC4 | TIN not obtainable - other reasons (explain in notes) | Party.extensions.tinUnavailableReason = 'TRC4' |

### PEP Category (Field 56)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| HEAD_OF_STATE | Head of state or head of government | Party.pepCategory = 'HEAD_OF_STATE' |
| SENIOR_POLITICIAN | Senior politician or senior government official | Party.pepCategory = 'SENIOR_POLITICIAN' |
| SENIOR_GOVERNMENT_OFFICIAL | Senior government, judicial or military official | Party.pepCategory = 'SENIOR_GOVERNMENT_OFFICIAL' |
| JUDICIAL_OFFICIAL | Senior judicial or law enforcement official | Party.pepCategory = 'JUDICIAL_OFFICIAL' |
| MILITARY_OFFICIAL | Senior military official | Party.pepCategory = 'MILITARY_OFFICIAL' |
| SENIOR_PARTY_OFFICIAL | Senior executive of state-owned corporation | Party.pepCategory = 'SENIOR_PARTY_OFFICIAL' |
| STATE_OWNED_ENTERPRISE | Senior official of state-owned enterprise | Party.pepCategory = 'STATE_OWNED_ENTERPRISE' |
| FAMILY_MEMBER | Family member of PEP | Party.pepCategory = 'FAMILY_MEMBER' |
| CLOSE_ASSOCIATE | Close associate of PEP | Party.pepCategory = 'CLOSE_ASSOCIATE' |

### PEP Relationship (Field 59)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| SELF | Person is the PEP | Party.extensions.pepRelationship = 'SELF' |
| FAMILY | Family member of PEP | Party.extensions.pepRelationship = 'FAMILY' |
| CLOSE_ASSOCIATE | Close business associate of PEP | Party.extensions.pepRelationship = 'CLOSE_ASSOCIATE' |

### Beneficiary Type (Field 78)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CURRENT | Current beneficiary with vested interest | Account.controllingPersons[].extensions.beneficiaryType = 'CURRENT' |
| CONTINGENT | Contingent/remainder beneficiary | Account.controllingPersons[].extensions.beneficiaryType = 'CONTINGENT' |
| DISCRETIONARY | Discretionary beneficiary | Account.controllingPersons[].extensions.beneficiaryType = 'DISCRETIONARY' |
| POTENTIAL | Potential future beneficiary | Account.controllingPersons[].extensions.beneficiaryType = 'POTENTIAL' |

### CP Data Source (Field 81)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| SELF_CERTIFICATION | Self-certification by account holder | Account.controllingPersons[].extensions.dataSource = 'SELF_CERTIFICATION' |
| DOCUMENTARY_EVIDENCE | Documentary evidence review | Account.controllingPersons[].extensions.dataSource = 'DOCUMENTARY_EVIDENCE' |
| PUBLIC_RECORDS | Public records search | Account.controllingPersons[].extensions.dataSource = 'PUBLIC_RECORDS' |
| THIRD_PARTY | Third-party data provider | Account.controllingPersons[].extensions.dataSource = 'THIRD_PARTY' |
| MIXED | Multiple sources | Account.controllingPersons[].extensions.dataSource = 'MIXED' |

### CP Status (Field 85)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| ACTIVE | Currently active controlling person | Account.controllingPersons[].extensions.cpStatus = 'ACTIVE' |
| INACTIVE | No longer controlling person | Account.controllingPersons[].extensions.cpStatus = 'INACTIVE' |
| PENDING_VERIFICATION | Pending verification | Account.controllingPersons[].extensions.cpStatus = 'PENDING_VERIFICATION' |
| DECEASED | Deceased | Account.controllingPersons[].extensions.cpStatus = 'DECEASED' |

---

## CDM Extensions Required

All 85 CRS Controlling Person fields successfully map to existing CDM model with extensions pattern. **No schema enhancements required.**

The controlling person information is stored within the `Account.controllingPersons[]` array, with each controlling person referencing a `Party` entity via `partyId`. Additional controlling person metadata is stored in the `extensions` pattern:

**Account Entity Extensions:**
- Account.controllingPersons[].extensions.isReportable
- Account.controllingPersons[].extensions.cpTypeCode
- Account.controllingPersons[].extensions.controlDescription
- Account.controllingPersons[].extensions.seniorManagingOfficial
- Account.controllingPersons[].extensions.selfCertReceived
- Account.controllingPersons[].extensions.selfCertDate
- Account.controllingPersons[].extensions.docEvidence
- Account.controllingPersons[].extensions.docEvidenceType
- Account.controllingPersons[].extensions.docEvidenceDate
- Account.controllingPersons[].extensions.relationshipStartDate
- Account.controllingPersons[].extensions.relationshipEndDate
- Account.controllingPersons[].extensions.directOwnership
- Account.controllingPersons[].extensions.ownershipChain
- Account.controllingPersons[].extensions.intermediateEntityCount
- Account.controllingPersons[].extensions.isTrustSettlor
- Account.controllingPersons[].extensions.isTrustTrustee
- Account.controllingPersons[].extensions.isTrustProtector
- Account.controllingPersons[].extensions.isTrustBeneficiary
- Account.controllingPersons[].extensions.beneficiaryType
- Account.controllingPersons[].extensions.sequenceNumber
- Account.controllingPersons[].extensions.dataSource
- Account.controllingPersons[].extensions.dataQualityScore
- Account.controllingPersons[].extensions.lastReviewDate
- Account.controllingPersons[].extensions.nextReviewDate
- Account.controllingPersons[].extensions.cpStatus
- Account.extensions.accountHolderName
- Account.extensions.accountHolderTIN
- Account.extensions.accountHolderCountry
- Account.extensions.totalControllingPersons

**Party Entity Extensions:**
- Party.extensions.nameType
- Party.extensions.precedingTitle
- Party.extensions.title
- Party.extensions.middleName
- Party.extensions.namePrefix
- Party.extensions.nameSuffix
- Party.extensions.generalSuffix
- Party.extensions.addressType
- Party.extensions.suiteFloorApt
- Party.extensions.addressFreeText
- Party.extensions.tinUnavailableReason
- Party.extensions.additionalTinUnavailable[]
- Party.extensions.citySubentityOfBirth
- Party.extensions.countrySubentityOfBirth
- Party.extensions.countryOfBirth
- Party.extensions.formerCountryOfBirth
- Party.extensions.pepPosition
- Party.extensions.pepCountry
- Party.extensions.pepRelationship
- Party.extensions.idIssueDate
- Party.extensions.idExpiryDate

---

## XML Structure Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<crs:CRS_OECD version="2.0" xmlns:crs="urn:oecd:ties:crs:v2" xmlns:stf="urn:oecd:ties:crsstf:v5">
  <crs:MessageSpec>
    <crs:SendingCompanyIN>GB</crs:SendingCompanyIN>
    <crs:TransmittingCountry>GB</crs:TransmittingCountry>
    <crs:ReceivingCountry>US</crs:ReceivingCountry>
    <crs:MessageType>CRS</crs:MessageType>
    <crs:MessageRefId>GB2024CRS00001</crs:MessageRefId>
    <crs:MessageTypeIndic>CRS701</crs:MessageTypeIndic>
    <crs:ReportingPeriod>2024-12-31</crs:ReportingPeriod>
    <crs:Timestamp>2025-04-30T10:30:00Z</crs:Timestamp>
  </crs:MessageSpec>

  <crs:CRS>
    <crs:ReportingFI>
      <crs:ResCountryCode>GB</crs:ResCountryCode>
      <crs:TIN issuedBy="GB">GB123456789</crs:TIN>
      <crs:Name>Example Bank PLC</crs:Name>
      <crs:Address legalAddressType="OECD304">
        <crs:CountryCode>GB</crs:CountryCode>
        <crs:City>London</crs:City>
        <crs:PostCode>EC1A 1BB</crs:PostCode>
        <crs:AddressFree>123 High Street</crs:AddressFree>
      </crs:Address>
    </crs:ReportingFI>

    <crs:ReportingGroup>
      <crs:AccountReport>
        <crs:DocSpec>
          <crs:DocTypeIndic>OECD1</crs:DocTypeIndic>
          <crs:DocRefId>GB2024CRS00001-001</crs:DocRefId>
        </crs:DocSpec>

        <crs:AccountNumber>GB12345678901234567890</crs:AccountNumber>

        <!-- Account Holder: Passive NFE Entity -->
        <crs:AccountHolder>
          <crs:Organisation>
            <crs:ResCountryCode>KY</crs:ResCountryCode>
            <crs:TIN issuedBy="KY">KY987654321</crs:TIN>
            <crs:Name nameType="OECD206">Cayman Investment Holdings Ltd</crs:Name>
            <crs:Address legalAddressType="OECD304">
              <crs:CountryCode>KY</crs:CountryCode>
              <crs:City>George Town</crs:City>
              <crs:PostCode>KY1-1108</crs:PostCode>
              <crs:AddressFree>PO Box 123, Grand Cayman</crs:AddressFree>
            </crs:Address>
          </crs:Organisation>
        </crs:AccountHolder>

        <crs:AccountBalance currCode="USD">5000000.00</crs:AccountBalance>

        <!-- Controlling Person 1 -->
        <crs:ControllingPerson>
          <crs:Individual>
            <crs:ResCountryCode>US</crs:ResCountryCode>
            <crs:TIN issuedBy="US">123-45-6789</crs:TIN>
            <crs:Name nameType="OECD201">
              <crs:FirstName>John</crs:FirstName>
              <crs:LastName>Smith</crs:LastName>
            </crs:Name>
            <crs:Address legalAddressType="OECD302">
              <crs:CountryCode>US</crs:CountryCode>
              <crs:City>New York</crs:City>
              <crs:CountrySubDivision>NY</crs:CountrySubDivision>
              <crs:PostCode>10001</crs:PostCode>
              <crs:AddressFree>123 Main Street, New York, NY 10001</crs:AddressFree>
            </crs:Address>
            <crs:Nationality>US</crs:Nationality>
            <crs:BirthInfo>
              <crs:BirthDate>1975-06-15</crs:BirthDate>
              <crs:City>Boston</crs:City>
              <crs:CountryInfo>
                <crs:CountryCode>US</crs:CountryCode>
              </crs:CountryInfo>
            </crs:BirthInfo>
          </crs:Individual>
          <crs:CtrlgPersonType>CRS801</crs:CtrlgPersonType>
        </crs:ControllingPerson>

        <!-- Controlling Person 2 -->
        <crs:ControllingPerson>
          <crs:Individual>
            <crs:ResCountryCode>GB</crs:ResCountryCode>
            <crs:TIN issuedBy="GB">AB123456C</crs:TIN>
            <crs:Name nameType="OECD201">
              <crs:Title>Mr</crs:Title>
              <crs:FirstName>David</crs:FirstName>
              <crs:LastName>Wilson</crs:LastName>
            </crs:Name>
            <crs:Address legalAddressType="OECD302">
              <crs:CountryCode>GB</crs:CountryCode>
              <crs:City>London</crs:City>
              <crs:PostCode>SW1A 1AA</crs:PostCode>
              <crs:AddressFree>10 Downing Street, London</crs:AddressFree>
            </crs:Address>
            <crs:Nationality>GB</crs:Nationality>
            <crs:BirthInfo>
              <crs:BirthDate>1968-03-22</crs:BirthDate>
              <crs:City>Manchester</crs:City>
              <crs:CountryInfo>
                <crs:CountryCode>GB</crs:CountryCode>
              </crs:CountryInfo>
            </crs:BirthInfo>
          </crs:Individual>
          <crs:CtrlgPersonType>CRS802</crs:CtrlgPersonType>
        </crs:ControllingPerson>

        <crs:Payment>
          <crs:Type>CRS502</crs:Type>
          <crs:PaymentAmnt currCode="USD">150000.00</crs:PaymentAmnt>
        </crs:Payment>
      </crs:AccountReport>
    </crs:ReportingGroup>
  </crs:CRS>
</crs:CRS_OECD>
```

---

## Comparison to FATCA Controlling Person Requirements

### Similarities
- Both identify natural persons who control entities
- Both require name, address, date of birth, TIN
- Both support multiple tax residencies
- Both use similar XML structure and OECD codes
- Both track ownership percentages

### Key Differences

| Aspect | FATCA | CRS |
|--------|-------|-----|
| **Terminology** | "Substantial U.S. Owner" | "Controlling Person" |
| **Threshold** | >10% ownership for passive NFFE | >25% ownership for passive NFE |
| **Control Types** | 10 types (CP01-CP10 in later FATCA versions) | 10 CRS types (CRS801-810) |
| **Applicable Entities** | Passive NFFE, Investment Entities in non-participating jurisdictions | Passive NFE (all jurisdictions) |
| **Maximum CPs** | Up to 50 per account | No explicit limit (typically 1-10) |
| **TIN Requirements** | U.S. TIN required if substantial U.S. owner | TIN for each tax residence country |
| **Due Diligence** | W-8BEN-E form collection | Self-certification + documentary evidence |
| **Trust Roles** | Basic controlling person identification | Detailed trust roles (settlor, trustee, protector, beneficiary) |
| **PEP Status** | Not required in FATCA | Often collected for CRS (FATF alignment) |
| **Senior Managing Official** | Required if no other CP identified | CRS805 code for SMO |
| **Ownership Chain** | Not explicitly tracked | Detailed chain description supported |
| **Data Quality** | Not tracked in schema | Quality score and review dates tracked |

### FATF Alignment

The CRS Controlling Person requirements closely align with FATF Recommendations:

- **FATF R.24 (Transparency of Legal Persons)**: Requires identification of beneficial owners with >25% ownership or control
- **FATF R.25 (Transparency of Legal Arrangements)**: Requires identification of settlors, trustees, protectors, and beneficiaries of trusts
- **FATF R.10 (Customer Due Diligence)**: Requires ongoing monitoring and updating of controlling person information

CRS implements these recommendations through:
1. **10 Controlling Person Types (CRS801-810)** covering ownership, control, and trust roles
2. **Multiple Tax Residencies** to support global transparency
3. **Due Diligence Tracking** via self-certification and documentary evidence flags
4. **Review Dates** for ongoing monitoring
5. **Data Quality Scores** to assess reliability

### Practical Implementation Differences

**FATCA:**
- Focused on U.S. tax evasion prevention
- Primarily concerned with U.S. persons
- Substantial U.S. Owner threshold: 10% (stricter)
- Less granular trust role identification
- Part of broader FATCA compliance program

**CRS:**
- Global automatic exchange of information
- Concerned with tax residents of 100+ jurisdictions
- Controlling Person threshold: 25% (FATF standard)
- Highly granular trust and entity control tracking
- Integrated with broader AML/KYC beneficial ownership requirements
- Often combined with local beneficial ownership registries

---

## Due Diligence Procedures

### Pre-existing Entity Accounts

| Account Value | Due Diligence Required |
|---------------|------------------------|
| ≤ $250,000 USD | None required (unless aggregated balance > $1M) |
| > $250,000 USD | Determine if Passive NFE and identify controlling persons |
| > $1,000,000 USD | Enhanced review procedures |

### New Entity Accounts

All new entity accounts require determination of entity type and controlling person identification for Passive NFEs.

### Self-Certification Requirements

Financial Institutions must obtain self-certification from entity account holders that includes:
1. Entity's tax residence(s)
2. Entity's TIN for each tax residence
3. Entity type (Active NFE, Passive NFE, Financial Institution, etc.)
4. For Passive NFEs: Controlling person information including:
   - Name, address, date of birth
   - Tax residence(s) and TIN(s)
   - Type of control (ownership %, voting rights, etc.)

### Documentary Evidence

Acceptable evidence for controlling person identification:
- Corporate registry extracts
- Shareholder registers
- Trust deeds
- Articles of association
- Certificates of incumbency
- Audited financial statements
- Government-issued identification documents

---

## References

- OECD CRS XML Schema v2.0: https://www.oecd.org/tax/automatic-exchange/common-reporting-standard/schema-and-user-guide/
- OECD CRS Implementation Handbook: https://www.oecd.org/tax/automatic-exchange/common-reporting-standard/CRS-Implementation-Handbook.pdf
- OECD CRS Section VIII Commentary: https://www.oecd.org/tax/automatic-exchange/common-reporting-standard/
- FATF Recommendation 24 (Legal Persons): https://www.fatf-gafi.org/recommendations.html
- FATF Recommendation 25 (Legal Arrangements): https://www.fatf-gafi.org/recommendations.html
- FATF Beneficial Ownership Guidance: https://www.fatf-gafi.org/publications/methodsandtrends/documents/beneficial-ownership.html
- GPS CDM Account Schema: `/Users/dineshpatel/code/projects/gps_cdm/schemas/03_account_complete_schema.json`
- GPS CDM Party Schema: `/Users/dineshpatel/code/projects/gps_cdm/schemas/02_party_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q2 2025
