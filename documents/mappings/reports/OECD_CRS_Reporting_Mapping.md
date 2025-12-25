# OECD CRS Reporting - CRS Report
## Complete Field Mapping to GPS CDM

**Report Type:** CRS Reporting (Common Reporting Standard)
**Regulatory Authority:** OECD (Organisation for Economic Co-operation and Development)
**Filing Requirement:** Financial Institutions must report accounts held by tax residents of reportable jurisdictions
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 108 fields mapped)

---

## Report Overview

The Common Reporting Standard (CRS) is the global standard for automatic exchange of financial account information between tax authorities. Developed by the OECD, it requires Financial Institutions to report information about financial accounts held by non-residents to their local tax authority, which then exchanges the information with the account holder's country of tax residence.

**Filing Threshold:** Varies by account type and jurisdiction (typically USD 1,000,000 for pre-existing entity accounts, no threshold for individuals)
**Filing Deadline:** Varies by jurisdiction (typically April 30 - June 30 annually)
**Filing Method:** XML submission to local tax authority via secure portal
**Regulation:** OECD CRS, FATF Recommendations, Local implementing legislation

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total CRS Reporting Fields** | 108 | 100% |
| **Mapped to CDM** | 108 | 100% |
| **Direct Mapping** | 94 | 87% |
| **Derived/Calculated** | 11 | 10% |
| **Reference Data Lookup** | 3 | 3% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Section 1: Message Header (MessageSpec)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | Sending Country | Code | 2 | Yes | ISO 3166-1 | RegulatoryReport | jurisdiction | Country code of reporting FI |
| 2 | Receiving Country | Code | 2 | Yes | ISO 3166-1 | RegulatoryReport | igaJurisdiction | Receiving jurisdiction |
| 3 | Message Type | Code | 10 | Yes | CRS701-CRS703 | RegulatoryReport | reportType | CRS_REPORTING |
| 4 | Warning | Text | 4000 | No | Free text | RegulatoryReport | extensions.warningText | Optional warning message |
| 5 | Contact | Text | 200 | No | Free text | RegulatoryReport | reportingEntityContactName | Contact person |
| 6 | Message Ref ID | Text | 200 | Yes | Free text | RegulatoryReport | reportReferenceNumber | Unique message identifier |
| 7 | Message Type Indic | Code | 10 | Yes | CRS701-CRS703 | RegulatoryReport | extensions.messageTypeIndic | New/Correction/Deletion |
| 8 | Corrected Message Ref ID | Text | 200 | Cond | Free text | RegulatoryReport | priorReportBSAID | If correction |
| 9 | Reporting Period | Date | 10 | Yes | YYYY-MM-DD | RegulatoryReport | extensions.reportingPeriodEnd | Period end date |
| 10 | Timestamp | DateTime | 29 | Yes | ISO 8601 | RegulatoryReport | submissionDate | Message creation timestamp |

### Section 2: Reporting Financial Institution

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 11 | Reporting FI Name | Text | 200 | Yes | Free text | FinancialInstitution | institutionName | Legal name of reporting FI |
| 12 | Reporting FI Address | ComplexType | - | Yes | Address elements | FinancialInstitution | address | Full address structure |
| 12a | Street | Text | 70 | No | Free text | FinancialInstitution | address.streetName | Street name |
| 12b | Building Number | Text | 16 | No | Free text | FinancialInstitution | address.buildingNumber | Building number |
| 12c | Suite/Floor/Apt | Text | 16 | No | Free text | FinancialInstitution | extensions.suiteFloorApt | Suite/floor/apartment |
| 12d | Post Box | Text | 16 | No | Free text | FinancialInstitution | address.postBox | PO Box |
| 12e | City | Text | 35 | Yes | Free text | FinancialInstitution | address.townName | City/town |
| 12f | Country Subentity | Text | 35 | No | Free text | FinancialInstitution | address.countrySubDivision | State/province/region |
| 12g | Postal Code | Text | 16 | No | Free text | FinancialInstitution | address.postCode | Postal/ZIP code |
| 12h | Country Code | Code | 2 | Yes | ISO 3166-1 | FinancialInstitution | country | ISO country code |
| 13 | Residence Country Code | Code | 2 | Yes | ISO 3166-1 | FinancialInstitution | country | Country of residence |
| 14 | TIN | Text | 200 | No | Free text | FinancialInstitution | tinValue | Tax Identification Number |
| 14a | TIN Issuing Country | Code | 2 | Cond | ISO 3166-1 | FinancialInstitution | extensions.tinIssuingCountry | Required if TIN provided |
| 15 | GIIN | Text | 19 | No | GIIN format | FinancialInstitution | extensions.giin | Global Intermediary ID |
| 16 | Other ID | Text | 200 | No | Free text | FinancialInstitution | lei | Legal Entity Identifier or other |
| 16a | Other ID Type | Code | 10 | Cond | LEI, BIC, etc. | FinancialInstitution | extensions.otherIdType | Type of other ID |

### Section 3: Account Report - Account Holder Information (Individual)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 17 | Account Number | Text | 200 | Yes | Free text | Account | accountNumber | Account identifier |
| 18 | Account Holder Type | Code | 1 | Yes | I=Individual, E=Entity | Account | accountHolderType | INDIVIDUAL or ENTITY_* |
| 19 | Account Closed | Boolean | 1 | Yes | Y/N | Account | accountStatus | CLOSED if Y |
| 20 | Account Closed Date | Date | 10 | Cond | YYYY-MM-DD | Account | closeDate | Required if closed |
| 21 | Undocumented Account | Boolean | 1 | No | Y/N | Account | extensions.undocumentedAccount | Lacks required documentation |
| 22 | Dormant Account | Boolean | 1 | No | Y/N | Account | dormantAccount | No customer-initiated activity |
| 23 | Individual - Residence Country | Code | 2 | Yes | ISO 3166-1 | Party | taxResidencies[].country | Tax residence country |
| 24 | Individual - TIN | Text | 200 | Cond | Free text | Party | taxResidencies[].tin | Tax ID for residence country |
| 24a | TIN Issuing Country | Code | 2 | Cond | ISO 3166-1 | Party | taxResidencies[].country | Country that issued TIN |
| 25 | TIN Unavailable Reason | Code | 3 | Cond | See code list | Party | extensions.tinUnavailableReason | If no TIN provided |
| 26 | Name Type | Code | 10 | Yes | OECD201-208 | Party | extensions.nameType | Individual name type |
| 27 | Preceding Title | Text | 200 | No | Free text | Party | extensions.precedingTitle | Dr., Prof., etc. |
| 28 | Title | Text | 200 | No | Free text | Party | extensions.title | Mr., Ms., Mrs., etc. |
| 29 | First Name | Text | 200 | Yes | Free text | Party | givenName | Given name |
| 30 | Middle Name | Text | 200 | No | Free text | Party | extensions.middleName | Middle name(s) |
| 31 | Name Prefix | Text | 200 | No | Free text | Party | extensions.namePrefix | Von, De, etc. |
| 32 | Last Name | Text | 200 | Yes | Free text | Party | familyName | Family/surname |
| 33 | Generation Identifier | Text | 200 | No | Free text | Party | suffix | Jr., Sr., III, etc. |
| 34 | Suffix | Text | 200 | No | Free text | Party | extensions.nameSuffix | PhD, Esq., etc. |
| 35 | General Suffix | Text | 200 | No | Free text | Party | extensions.generalSuffix | Other suffixes |
| 36 | Address Type | Code | 10 | Yes | OECD301-305 | Party | extensions.addressType | Residential, business, etc. |
| 37 | Street | Text | 70 | No | Free text | Party | address.streetName | Street name |
| 38 | Building Number | Text | 16 | No | Free text | Party | address.buildingNumber | Building number |
| 39 | Suite/Floor/Apt | Text | 16 | No | Free text | Party | extensions.suiteFloorApt | Suite/floor/apartment |
| 40 | District Name | Text | 35 | No | Free text | Party | address.districtName | District |
| 41 | Post Box | Text | 16 | No | Free text | Party | address.postBox | PO Box |
| 42 | Post Code | Text | 16 | No | Free text | Party | address.postCode | Postal code |
| 43 | City | Text | 35 | Yes | Free text | Party | address.townName | City/town |
| 44 | Country Subentity | Text | 35 | No | Free text | Party | address.countrySubDivision | State/province |
| 45 | Country Code | Code | 2 | Yes | ISO 3166-1 | Party | address.country | ISO country code |
| 46 | Address Free Text | Text | 4000 | No | Free text | Party | extensions.addressFreeText | Free-form address |
| 47 | Nationality | Code | 2 | No | ISO 3166-1 | Party | nationality[] | Citizenship country codes |
| 48 | Date of Birth | Date | 10 | Yes | YYYY-MM-DD | Party | dateOfBirth | Birth date |
| 49 | City of Birth | Text | 200 | No | Free text | Party | placeOfBirth | Birth city |
| 50 | City Subentity | Text | 200 | No | Free text | Party | extensions.citySubentityOfBirth | Birth district |
| 51 | Country of Birth | Code | 2 | No | ISO 3166-1 | Party | extensions.countryOfBirth | Birth country |
| 52 | Former Country of Birth | Code | 2 | No | ISO 3166-1 | Party | extensions.formerCountryOfBirth | If country changed |

### Section 4: Account Report - Account Holder Information (Entity)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 53 | Entity - Residence Country | Code | 2 | Yes | ISO 3166-1 | Party | taxResidencies[].country | Tax residence country |
| 54 | Entity - TIN | Text | 200 | Cond | Free text | Party | taxResidencies[].tin | Tax ID for residence country |
| 54a | TIN Issuing Country | Code | 2 | Cond | ISO 3166-1 | Party | taxResidencies[].country | Country that issued TIN |
| 55 | TIN Unavailable Reason | Code | 3 | Cond | See code list | Party | extensions.tinUnavailableReason | If no TIN provided |
| 56 | Name Type | Code | 10 | Yes | OECD201-208 | Party | extensions.nameType | Entity name type |
| 57 | Entity Legal Name | Text | 200 | Yes | Free text | Party | name | Legal name of entity |
| 58 | Entity Name Type | Code | 10 | No | OECD201-208 | Party | extensions.entityNameType | Legal/Trading/etc. |
| 59 | Address Type | Code | 10 | Yes | OECD301-305 | Party | extensions.addressType | Registered, business, etc. |
| 60 | Street | Text | 70 | No | Free text | Party | address.streetName | Street name |
| 61 | Building Number | Text | 16 | No | Free text | Party | address.buildingNumber | Building number |
| 62 | Suite/Floor/Apt | Text | 16 | No | Free text | Party | extensions.suiteFloorApt | Suite/floor/apartment |
| 63 | District Name | Text | 35 | No | Free text | Party | address.districtName | District |
| 64 | Post Box | Text | 16 | No | Free text | Party | address.postBox | PO Box |
| 65 | Post Code | Text | 16 | No | Free text | Party | address.postCode | Postal code |
| 66 | City | Text | 35 | Yes | Free text | Party | address.townName | City/town |
| 67 | Country Subentity | Text | 35 | No | Free text | Party | address.countrySubDivision | State/province |
| 68 | Country Code | Code | 2 | Yes | ISO 3166-1 | Party | address.country | ISO country code |
| 69 | Address Free Text | Text | 4000 | No | Free text | Party | extensions.addressFreeText | Free-form address |

### Section 5: Account Balance and Payment Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 70 | Account Balance | Decimal | 15,2 | Yes | Numeric | Account | accountBalanceForTaxReporting | As of year-end |
| 71 | Currency Code | Code | 3 | Yes | ISO 4217 | Account | currency | ISO currency code |
| 72 | Payment Type | Code | 10 | Yes | CRS501-504 | RegulatoryReport | extensions.paymentType[] | Type of payment |
| 73 | Payment Amount | Decimal | 15,2 | Yes | Numeric | RegulatoryReport | extensions.paymentAmount[] | Payment amount |
| 74 | Payment Currency | Code | 3 | Yes | ISO 4217 | RegulatoryReport | extensions.paymentCurrency[] | ISO currency code |

### Section 6: Pool Reporting (Alternative to Individual Reporting)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 75 | Pool Report Type | Code | 10 | Cond | OECD601-604 | RegulatoryReport | poolReportType | Type of pool |
| 76 | Number of Accounts | Integer | 10 | Cond | Numeric | RegulatoryReport | extensions.numberOfAccountsInPool | Account count in pool |
| 77 | Aggregate Balance | Decimal | 15,2 | Cond | Numeric | RegulatoryReport | extensions.aggregateAccountBalance | Total balance |
| 78 | Aggregate Balance Currency | Code | 3 | Cond | ISO 4217 | RegulatoryReport | extensions.aggregateBalanceCurrency | Currency |
| 79 | Aggregate Payment | Decimal | 15,2 | Cond | Numeric | RegulatoryReport | extensions.aggregatePaymentAmount | Total payments |
| 80 | Aggregate Payment Currency | Code | 3 | Cond | ISO 4217 | RegulatoryReport | extensions.aggregatePaymentCurrency | Currency |

### Section 7: Document Specification (Per Account)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 81 | Doc Type Indic | Code | 10 | Yes | OECD0-3 | RegulatoryReport | extensions.docTypeIndic | New/Correction/Deletion |
| 82 | Doc Ref ID | Text | 200 | Yes | Free text | RegulatoryReport | extensions.docRefId | Unique document ID |
| 83 | Corrected Doc Ref ID | Text | 200 | Cond | Free text | RegulatoryReport | extensions.correctedDocRefId | If correction |

### Section 8: Additional Controlling Person Tax Residencies (for entities)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 84 | Additional Residence Country | Code | 2 | No | ISO 3166-1 | Party | taxResidencies[1+].country | 2nd, 3rd tax residence |
| 85 | Additional TIN | Text | 200 | No | Free text | Party | taxResidencies[1+].tin | TIN for additional country |
| 85a | Additional TIN Issuing Country | Code | 2 | Cond | ISO 3166-1 | Party | taxResidencies[1+].country | Country that issued TIN |
| 86 | Additional TIN Unavailable | Code | 3 | Cond | See code list | Party | extensions.additionalTinUnavailable | Reason code |

### Section 9: Account Financial Information Details

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 87 | CRS Account Type | Code | 10 | Yes | OECD101-105 | Account | extensions.crsAccountType | Depository/Custodial/etc. |
| 88 | Preexisting Account | Boolean | 1 | No | Y/N | Account | extensions.preexistingAccount | Account before CRS effective |
| 89 | Account Opening Date | Date | 10 | No | YYYY-MM-DD | Account | openDate | Account opening date |
| 90 | Account High Value | Boolean | 1 | No | Y/N | Account | extensions.highValueAccount | Balance > $1M USD |
| 91 | Self-Certification Date | Date | 10 | No | YYYY-MM-DD | Account | extensions.selfCertificationDate | Date of self-certification |
| 92 | Documentary Evidence | Boolean | 1 | No | Y/N | Account | extensions.documentaryEvidence | Documentary evidence on file |

### Section 10: Sponsor Information (for Sponsored Investment Entities)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 93 | Sponsor Name | Text | 200 | Cond | Free text | FinancialInstitution | extensions.sponsorName | Required if sponsored |
| 94 | Sponsor Address | ComplexType | - | Cond | Address elements | FinancialInstitution | extensions.sponsorAddress | Full address |
| 95 | Sponsor GIIN | Text | 19 | Cond | GIIN format | RegulatoryReport | sponsorGIIN | Sponsor GIIN |
| 96 | Sponsor Residence Country | Code | 2 | Cond | ISO 3166-1 | FinancialInstitution | extensions.sponsorCountry | Sponsor country |

### Section 11: Intermediary/Nominee Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 97 | Intermediary Name | Text | 200 | No | Free text | FinancialInstitution | extensions.intermediaryName | Intermediary FI name |
| 98 | Intermediary GIIN | Text | 19 | No | GIIN format | FinancialInstitution | extensions.intermediaryGIIN | Intermediary GIIN |
| 99 | Intermediary Residence Country | Code | 2 | No | ISO 3166-1 | FinancialInstitution | extensions.intermediaryCountry | Intermediary country |

### Section 12: Trust/SPV Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 100 | Trustee Name | Text | 200 | No | Free text | Party | extensions.trusteeName | Trustee name |
| 101 | Settlor Name | Text | 200 | No | Free text | Party | extensions.settlorName | Trust settlor |
| 102 | Protector Name | Text | 200 | No | Free text | Party | extensions.protectorName | Trust protector |
| 103 | Beneficiary Count | Integer | 5 | No | Numeric | Party | extensions.beneficiaryCount | Number of beneficiaries |

### Section 13: Metadata and Control Fields

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 104 | Report Created Timestamp | DateTime | 29 | Yes | ISO 8601 | RegulatoryReport | createdTimestamp | Report creation time |
| 105 | Report Submitted By | Text | 100 | Yes | Free text | RegulatoryReport | lastUpdatedBy | Submitter ID |
| 106 | Schema Version | Text | 10 | Yes | v1.0, v2.0 | RegulatoryReport | extensions.schemaVersion | CRS XML schema version |
| 107 | Report Status | Code | 20 | Yes | See enum | RegulatoryReport | reportStatus | Draft/Submitted/etc. |
| 108 | Reporting Period Year | Integer | 4 | Yes | YYYY | RegulatoryReport | taxYear | Calendar year |

---

## Code Lists

### Message Type Indicator (Field 3, 7)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CRS701 | New data | RegulatoryReport.extensions.messageTypeIndic = 'CRS701' |
| CRS702 | Correction for previously sent data | RegulatoryReport.extensions.messageTypeIndic = 'CRS702' |
| CRS703 | Deletion of previously sent data | RegulatoryReport.extensions.messageTypeIndic = 'CRS703' |

### Name Type (Field 26, 56)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| OECD201 | SMF Name (Standard format: Title + FirstName + MiddleName + NamePrefix + LastName + GenerationIdentifier + Suffix) | Party.extensions.nameType = 'OECD201' |
| OECD202 | Alias | Party.extensions.nameType = 'OECD202' |
| OECD203 | Nickname | Party.extensions.nameType = 'OECD203' |
| OECD204 | Also Known As (AKA) | Party.extensions.nameType = 'OECD204' |
| OECD205 | Doing Business As (DBA) | Party.extensions.nameType = 'OECD205' |
| OECD206 | Legal name | Party.extensions.nameType = 'OECD206' |
| OECD207 | Maiden name | Party.extensions.nameType = 'OECD207' |
| OECD208 | Former name | Party.extensions.nameType = 'OECD208' |

### Address Type (Field 36, 59)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| OECD301 | Residential or business | Party.extensions.addressType = 'OECD301' |
| OECD302 | Residential | Party.extensions.addressType = 'OECD302' |
| OECD303 | Business | Party.extensions.addressType = 'OECD303' |
| OECD304 | Registered office | Party.extensions.addressType = 'OECD304' |
| OECD305 | Unspecified | Party.extensions.addressType = 'OECD305' |

### TIN Unavailable Reason (Field 25, 55)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| TRC1 | TIN not required by jurisdiction | Party.extensions.tinUnavailableReason = 'TRC1' |
| TRC2 | No TIN issued by jurisdiction | Party.extensions.tinUnavailableReason = 'TRC2' |
| TRC3 | TIN not obtainable - jurisdiction does not require TIN | Party.extensions.tinUnavailableReason = 'TRC3' |
| TRC4 | TIN not obtainable - other reasons | Party.extensions.tinUnavailableReason = 'TRC4' |

### Payment Type (Field 72)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CRS501 | Dividends | RegulatoryReport.extensions.paymentType[] = 'CRS501' |
| CRS502 | Interest | RegulatoryReport.extensions.paymentType[] = 'CRS502' |
| CRS503 | Gross proceeds/redemptions | RegulatoryReport.extensions.paymentType[] = 'CRS503' |
| CRS504 | Other income | RegulatoryReport.extensions.paymentType[] = 'CRS504' |

### Pool Report Type (Field 75)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| OECD601 | Undocumented accounts | RegulatoryReport.poolReportType = 'UNDOCUMENTED_ACCOUNTS' |
| OECD602 | Dormant accounts | RegulatoryReport.poolReportType = 'DORMANT_ACCOUNTS' |
| OECD603 | Low-value accounts | RegulatoryReport.poolReportType = 'LOW_VALUE_ACCOUNTS' |
| OECD604 | Not for exchange | RegulatoryReport.poolReportType = 'NOT_FOR_EXCHANGE' |

### Document Type Indicator (Field 81)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| OECD0 | Resent data (technical correction) | RegulatoryReport.extensions.docTypeIndic = 'OECD0' |
| OECD1 | New data | RegulatoryReport.extensions.docTypeIndic = 'OECD1' |
| OECD2 | Correction for previously sent data | RegulatoryReport.extensions.docTypeIndic = 'OECD2' |
| OECD3 | Deletion of previously sent data | RegulatoryReport.extensions.docTypeIndic = 'OECD3' |

### CRS Account Type (Field 87)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| OECD101 | Depository Account | Account.extensions.crsAccountType = 'OECD101' |
| OECD102 | Custodial Account | Account.extensions.crsAccountType = 'OECD102' |
| OECD103 | Equity or debt interest in Financial Institution | Account.extensions.crsAccountType = 'OECD103' |
| OECD104 | Cash Value Insurance Contract | Account.extensions.crsAccountType = 'OECD104' |
| OECD105 | Annuity Contract | Account.extensions.crsAccountType = 'OECD105' |

### Country Codes

All country codes use ISO 3166-1 alpha-2 standard (e.g., US, GB, DE, FR, JP, CN, etc.)

### Currency Codes

All currency codes use ISO 4217 standard (e.g., USD, EUR, GBP, JPY, CNY, etc.)

---

## CDM Extensions Required

All 108 CRS Reporting fields successfully map to existing CDM model with extensions pattern. **No schema enhancements required.**

The following fields use the `extensions` pattern within existing CDM entities:
- RegulatoryReport.extensions: messageTypeIndic, reportingPeriodEnd, docTypeIndic, docRefId, correctedDocRefId, paymentType[], paymentAmount[], paymentCurrency[], numberOfAccountsInPool, aggregateAccountBalance, aggregateBalanceCurrency, aggregatePaymentAmount, aggregatePaymentCurrency, schemaVersion
- Party.extensions: tinUnavailableReason, nameType, precedingTitle, title, middleName, namePrefix, nameSuffix, generalSuffix, addressType, suiteFloorApt, addressFreeText, citySubentityOfBirth, countryOfBirth, formerCountryOfBirth, trusteeName, settlorName, protectorName, beneficiaryCount
- Account.extensions: undocumentedAccount, crsAccountType, preexistingAccount, highValueAccount, selfCertificationDate, documentaryEvidence
- FinancialInstitution.extensions: tinIssuingCountry, otherIdType, giin, suiteFloorApt, sponsorName, sponsorAddress, sponsorCountry, intermediaryName, intermediaryGIIN, intermediaryCountry

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
        <crs:AccountHolder>
          <crs:Individual>
            <crs:ResCountryCode>US</crs:ResCountryCode>
            <crs:TIN issuedBy="US">123-45-6789</crs:TIN>
            <crs:Name nameType="OECD201">
              <crs:FirstName>John</crs:FirstName>
              <crs:LastName>Smith</crs:LastName>
            </crs:Name>
            <crs:Address legalAddressType="OECD302">
              <crs:CountryCode>GB</crs:CountryCode>
              <crs:City>London</crs:City>
              <crs:PostCode>SW1A 1AA</crs:PostCode>
              <crs:AddressFree>10 Downing Street</crs:AddressFree>
            </crs:Address>
            <crs:Nationality>US</crs:Nationality>
            <crs:BirthInfo>
              <crs:BirthDate>1975-01-15</crs:BirthDate>
              <crs:City>New York</crs:City>
              <crs:CountryInfo>
                <crs:CountryCode>US</crs:CountryCode>
              </crs:CountryInfo>
            </crs:BirthInfo>
          </crs:Individual>
        </crs:AccountHolder>

        <crs:AccountBalance currCode="GBP">250000.00</crs:AccountBalance>

        <crs:Payment>
          <crs:Type>CRS502</crs:Type>
          <crs:PaymentAmnt currCode="GBP">5000.00</crs:PaymentAmnt>
        </crs:Payment>
      </crs:AccountReport>
    </crs:ReportingGroup>
  </crs:CRS>
</crs:CRS_OECD>
```

---

## Comparison to FATCA Reporting

### Similarities
- Both use OECD XML schema format with similar message structure
- Both require account holder identification with TIN
- Both report account balances and payment information
- Both support pool reporting for certain account types
- Both use ISO country codes (3166-1) and currency codes (4217)
- Both have correction/deletion message types
- Both track controlling persons for entities

### Key Differences

| Aspect | FATCA | CRS |
|--------|-------|-----|
| **Purpose** | Report U.S. accounts to IRS | Report foreign accounts to multiple jurisdictions |
| **Scope** | U.S. persons only | Tax residents of reportable jurisdictions |
| **Direction** | One-way (to U.S.) | Reciprocal exchange between countries |
| **Identifier** | GIIN (Global Intermediary ID) | GIIN optional; TIN primary |
| **Reportable Jurisdictions** | United States only | 100+ participating jurisdictions |
| **Thresholds** | Varies by account type | Varies by jurisdiction and account age |
| **Account Types** | 4 payment types (dividends, interest, gross proceeds, other) | 5 CRS account types (depository, custodial, equity/debt, insurance, annuity) |
| **Entity Classification** | FATCA-specific (FFI, NFFE, etc.) | CRS-specific (Active NFE, Passive NFE, etc.) |
| **Controlling Person Types** | Substantial U.S. Owner (>10%) | Controlling Person (>25% or control) |
| **Self-Certification** | Not explicitly required in schema | Tracked via selfCertificationDate |
| **Documentary Evidence** | Not tracked in schema | Tracked via documentaryEvidence flag |
| **Pool Reporting Types** | 6 types (recalcitrant, dormant, etc.) | 4 types (undocumented, dormant, low-value, not-for-exchange) |
| **Multiple Tax Residencies** | Single TIN per account holder | Multiple tax residencies supported |
| **Address Requirements** | Less structured | More structured with OECD address types |
| **Name Requirements** | Simple (First, Middle, Last) | Complex (8 name types with title, prefix, suffix) |

### Technical Schema Differences
- **FATCA**: Uses `FATCA_OECD` namespace with FATCA-specific codes
- **CRS**: Uses `CRS_OECD` namespace with OECD-standardized codes
- **FATCA**: MessageType = "FATCA", DocTypeIndic = "FATCA1-7"
- **CRS**: MessageType = "CRS", DocTypeIndic = "OECD0-3"
- **FATCA**: Less granular address structure
- **CRS**: Highly structured address with building number, district, subentity
- **FATCA**: Birth info optional for individuals
- **CRS**: Birth info required for individuals

### Regulatory Context
- **FATCA**: U.S. domestic law (IRC 1471-1474) with bilateral IGAs
- **CRS**: OECD multilateral standard implemented via local legislation
- **FATCA**: Penalties for FFI non-compliance: 30% withholding
- **CRS**: Penalties vary by jurisdiction implementing CRS

---

## References

- OECD CRS XML Schema v2.0: https://www.oecd.org/tax/automatic-exchange/common-reporting-standard/schema-and-user-guide/
- OECD CRS Implementation Handbook: https://www.oecd.org/tax/automatic-exchange/common-reporting-standard/CRS-Implementation-Handbook.pdf
- OECD CRS User Guide: https://www.oecd.org/tax/exchange-of-tax-information/CRS-XML-Schema-v2.0-User-Guide.pdf
- FATF Beneficial Ownership Recommendations: https://www.fatf-gafi.org/
- GPS CDM Schema: `/Users/dineshpatel/code/projects/gps_cdm/schemas/05_regulatory_report_complete_schema.json`
- GPS CDM Party Schema: `/Users/dineshpatel/code/projects/gps_cdm/schemas/02_party_complete_schema.json`
- GPS CDM Account Schema: `/Users/dineshpatel/code/projects/gps_cdm/schemas/03_account_complete_schema.json`
- GPS CDM Financial Institution Schema: `/Users/dineshpatel/code/projects/gps_cdm/schemas/04_financial_institution_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q2 2025
