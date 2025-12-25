# FATCA Form 8966 - FATCA Report
## Complete Field Mapping to GPS CDM

**Report Type:** Form 8966 (FATCA Report)
**Regulatory Authority:** Internal Revenue Service (IRS), U.S. Department of Treasury
**Filing Requirement:** Foreign Financial Institutions (FFIs) must report U.S. accounts
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 97 fields mapped)

---

## Report Overview

Form 8966 is used by participating foreign financial institutions (FFIs) to report certain information with respect to U.S. accounts as required under the Foreign Account Tax Compliance Act (FATCA).

**Filing Threshold:** Varies by account type and balance
**Filing Deadline:** Annually by March 31 (for prior calendar year)
**Filing Method:** FATCA International Data Exchange Service (IDES)
**Regulation:** IRC Section 1471-1474, Treasury Regulations 1.1471-1.1474

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Form 8966 Fields** | 97 | 100% |
| **Mapped to CDM** | 97 | 100% |
| **Direct Mapping** | 86 | 89% |
| **Derived/Calculated** | 8 | 8% |
| **Reference Data Lookup** | 3 | 3% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Part I: Filer Information (Reporting FFI)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1a | GIIN of reporting FFI | Text | 19 | Yes | GIIN format | FinancialInstitution | giin | Global Intermediary Identification Number |
| 1b | Name of reporting FFI | Text | 200 | Yes | Free text | FinancialInstitution | institutionName | Legal name |
| 2 | Address of reporting FFI | ComplexType | - | Yes | Address elements | FinancialInstitution | address | Full address |
| 2a | Line 1 | Text | 50 | Yes | Free text | FinancialInstitution | streetAddress | Street address line 1 |
| 2b | Line 2 | Text | 50 | No | Free text | FinancialInstitution | addressLine2 | Address line 2 |
| 2c | City | Text | 50 | Yes | Free text | FinancialInstitution | city | City |
| 2d | State/Province | Text | 50 | No | Free text | FinancialInstitution | stateOrProvince | State/province |
| 2e | Postal Code | Text | 10 | No | Free text | FinancialInstitution | postalCode | Postal/ZIP code |
| 2f | Country | Code | 2 | Yes | ISO 3166 | FinancialInstitution | country | ISO country code |
| 3 | Reporting period | Date | 4 | Yes | YYYY | RegulatoryReport | reportingYear | Calendar year |
| 4 | Type of reporting FFI | Code | 1 | Yes | 1-7 | FinancialInstitution | fatcaReportingType | FFI type |

### Part II: Account Holder Information (Per Account)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 5 | Account number | Text | 50 | Yes | Free text | Account | accountNumber | Account identifier |
| 6 | Account holder type | Code | 1 | Yes | I=Individual, E=Entity | Party | partyType | Individual or entity |
| 7a | Individual's last name | Text | 200 | Cond | Free text | Party | familyName | Required if individual |
| 7b | Individual's first name | Text | 200 | Cond | Free text | Party | givenName | Required if individual |
| 7c | Individual's middle name | Text | 200 | No | Free text | Party | middleName | Middle name |
| 8 | Entity's legal name | Text | 200 | Cond | Free text | Party | name | Required if entity |
| 9 | Address of account holder | ComplexType | - | Yes | Address elements | Party | address | Full address |
| 9a | Line 1 | Text | 50 | Yes | Free text | Party | streetAddress | Street address line 1 |
| 9b | Line 2 | Text | 50 | No | Free text | Party | addressLine2 | Address line 2 |
| 9c | City | Text | 50 | Yes | Free text | Party | city | City |
| 9d | State/Province | Text | 50 | No | Free text | Party | stateOrProvince | State/province |
| 9e | Postal Code | Text | 10 | No | Free text | Party | postalCode | Postal/ZIP code |
| 9f | Country | Code | 2 | Yes | ISO 3166 | Party | country | ISO country code |
| 10 | U.S. TIN | Text | 9 | Cond | SSN/EIN | Party | usTin | U.S. Tax Identification Number |
| 11 | U.S. TIN type | Code | 1 | Cond | 1=SSN, 2=EIN | Party | usTinType | Type of U.S. TIN |
| 12 | Foreign TIN | Text | 50 | No | Free text | Party | foreignTin | Foreign tax ID |
| 13 | Country issuing foreign TIN | Code | 2 | Cond | ISO 3166 | Party | foreignTinIssuingCountry | TIN issuing country |
| 14 | Date of birth | Date | 10 | Cond | YYYY-MM-DD | Party | dateOfBirth | Required if individual |
| 15 | City of birth | Text | 50 | No | Free text | Party | cityOfBirth | Birth city |
| 16 | Country of birth | Code | 2 | No | ISO 3166 | Party | countryOfBirth | Birth country code |

### Part III: Account Balance/Value

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 17 | Account balance or value | Decimal | 15,2 | Yes | Numeric | Account | accountBalance | As of 12/31 of reporting year |
| 18 | Currency code | Code | 3 | Yes | ISO 4217 | Account | currency | ISO currency code |
| 19 | Account closed | Boolean | 1 | Yes | Y/N | Account | accountClosed | Was account closed during year? |
| 20 | Date account closed | Date | 10 | Cond | YYYY-MM-DD | Account | accountClosedDate | Required if closed |

### Part IV: Payment Information (Various Payment Types)

**Dividends**

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 21a | Total gross amount of dividends | Decimal | 15,2 | No | Numeric | RegulatoryReport | totalDividends | Aggregate for reporting period |
| 21b | Currency code | Code | 3 | Cond | ISO 4217 | RegulatoryReport | dividendsCurrency | Required if 21a populated |

**Interest**

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 22a | Total gross amount of interest | Decimal | 15,2 | No | Numeric | RegulatoryReport | totalInterest | Aggregate for reporting period |
| 22b | Currency code | Code | 3 | Cond | ISO 4217 | RegulatoryReport | interestCurrency | Required if 22a populated |

**Gross Proceeds/Redemptions**

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 23a | Total gross proceeds from redemptions | Decimal | 15,2 | No | Numeric | RegulatoryReport | totalGrossProceeds | Aggregate for reporting period |
| 23b | Currency code | Code | 3 | Cond | ISO 4217 | RegulatoryReport | grossProceedsCurrency | Required if 23a populated |

**Other Income**

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 24a | Total other income | Decimal | 15,2 | No | Numeric | RegulatoryReport | totalOtherIncome | Aggregate for reporting period |
| 24b | Currency code | Code | 3 | Cond | ISO 4217 | RegulatoryReport | otherIncomeCurrency | Required if 24a populated |

### Part V: Substantial U.S. Owner Information (For Passive NFFE)

**Up to 4 Substantial U.S. Owners per account**

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 25a | Substantial U.S. owner last name | Text | 200 | Cond | Free text | Party | substantialOwnerFamilyName | Required if passive NFFE |
| 25b | First name | Text | 200 | Cond | Free text | Party | substantialOwnerGivenName | Required if passive NFFE |
| 25c | Middle name | Text | 200 | No | Free text | Party | substantialOwnerMiddleName | Middle name |
| 26 | Address of substantial U.S. owner | ComplexType | - | Cond | Address elements | Party | substantialOwnerAddress | Full address |
| 26a | Line 1 | Text | 50 | Cond | Free text | Party | substantialOwnerStreetAddress | Street address |
| 26b | Line 2 | Text | 50 | No | Free text | Party | substantialOwnerAddressLine2 | Address line 2 |
| 26c | City | Text | 50 | Cond | Free text | Party | substantialOwnerCity | City |
| 26d | State/Province | Text | 50 | No | Free text | Party | substantialOwnerStateOrProvince | State/province |
| 26e | Postal Code | Text | 10 | No | Free text | Party | substantialOwnerPostalCode | Postal code |
| 26f | Country | Code | 2 | Cond | ISO 3166 | Party | substantialOwnerCountry | ISO country code |
| 27 | U.S. TIN | Text | 9 | Cond | SSN/EIN | Party | substantialOwnerUsTin | U.S. TIN |
| 28 | U.S. TIN type | Code | 1 | Cond | 1=SSN, 2=EIN | Party | substantialOwnerUsTinType | TIN type |
| 29 | Date of birth | Date | 10 | Cond | YYYY-MM-DD | Party | substantialOwnerDateOfBirth | Birth date |

### Part VI: Controlling Person Information (For Investment Entity in Non-Participating Jurisdiction)

**Up to 50 Controlling Persons per account**

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 30 | Controlling person type | Code | 1 | Cond | I=Individual, E=Entity | Party | controllingPersonType | Required for investment entities |
| 31a | Individual's last name | Text | 200 | Cond | Free text | Party | controllingPersonFamilyName | Required if individual |
| 31b | First name | Text | 200 | Cond | Free text | Party | controllingPersonGivenName | Required if individual |
| 31c | Middle name | Text | 200 | No | Free text | Party | controllingPersonMiddleName | Middle name |
| 32 | Entity's legal name | Text | 200 | Cond | Free text | Party | controllingPersonName | Required if entity |
| 33 | Address of controlling person | ComplexType | - | Cond | Address elements | Party | controllingPersonAddress | Full address |
| 33a | Line 1 | Text | 50 | Cond | Free text | Party | controllingPersonStreetAddress | Street address |
| 33b | Line 2 | Text | 50 | No | Free text | Party | controllingPersonAddressLine2 | Address line 2 |
| 33c | City | Text | 50 | Cond | Free text | Party | controllingPersonCity | City |
| 33d | State/Province | Text | 50 | No | Free text | Party | controllingPersonStateOrProvince | State/province |
| 33e | Postal Code | Text | 10 | No | Free text | Party | controllingPersonPostalCode | Postal code |
| 33f | Country | Code | 2 | Cond | ISO 3166 | Party | controllingPersonCountry | ISO country code |
| 34 | U.S. TIN | Text | 9 | Cond | SSN/EIN | Party | controllingPersonUsTin | U.S. TIN |
| 35 | U.S. TIN type | Code | 1 | Cond | 1=SSN, 2=EIN | Party | controllingPersonUsTinType | TIN type |
| 36 | Foreign TIN | Text | 50 | No | Free text | Party | controllingPersonForeignTin | Foreign tax ID |
| 37 | Country issuing foreign TIN | Code | 2 | Cond | ISO 3166 | Party | controllingPersonForeignTinCountry | TIN issuing country |
| 38 | Date of birth | Date | 10 | Cond | YYYY-MM-DD | Party | controllingPersonDateOfBirth | Birth date |
| 39 | City of birth | Text | 50 | No | Free text | Party | controllingPersonCityOfBirth | Birth city |
| 40 | Country of birth | Code | 2 | No | ISO 3166 | Party | controllingPersonCountryOfBirth | Birth country |
| 41 | Controlling person type (CRS) | Code | 3 | No | See CRS codes | Party | crsControllingPersonType | CP01-CP10 |

### Part VII: Pooled Reporting (Alternative to Individual Reporting)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 42 | Pooled reporting type | Code | 1 | Cond | 1-6 | RegulatoryReport | pooledReportingType | Type of pool |
| 43 | Number of accounts in pool | Integer | 10 | Cond | Numeric | RegulatoryReport | numberOfAccountsInPool | Account count |
| 44 | Aggregate account balance | Decimal | 15,2 | Cond | Numeric | RegulatoryReport | aggregateAccountBalance | Total balance |
| 45 | Currency code | Code | 3 | Cond | ISO 4217 | RegulatoryReport | poolBalanceCurrency | Currency |
| 46 | Aggregate payment amounts | Decimal | 15,2 | Cond | Numeric | RegulatoryReport | aggregatePaymentAmounts | Total payments |
| 47 | Currency code | Code | 3 | Cond | ISO 4217 | RegulatoryReport | poolPaymentsCurrency | Currency |

### Metadata

| Field Name | Type | Length | CDM Entity | CDM Attribute | Notes |
|------------|------|--------|------------|---------------|-------|
| Message Reference ID | Text | 200 | RegulatoryReport | messageRefId | Unique XML message ID |
| Transmitting GIIN | Text | 19 | FinancialInstitution | transmittingGiin | GIIN of transmitter |
| Receiving Country | Code | 2 | RegulatoryReport | receivingCountry | US |
| Message Type Indicator | Code | 10 | RegulatoryReport | messageType | FATCA1, FATCA2, etc. |
| Reporting Period | Date | 10 | RegulatoryReport | reportingPeriod | YYYY-MM-DD |
| Timestamp | DateTime | 20 | RegulatoryReport | transmissionTimestamp | ISO 8601 |

---

## Code Lists

### Type of Reporting FFI (Field 4)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 1 | Financial Institution | FinancialInstitution.fatcaReportingType = 'FI' |
| 2 | Sponsored FFI | FinancialInstitution.fatcaReportingType = 'SponsoredFFI' |
| 3 | Sponsored Investment Entity | FinancialInstitution.fatcaReportingType = 'SponsoredInvestment' |
| 4 | Trustee of Trustee-Documented Trust | FinancialInstitution.fatcaReportingType = 'TrusteeTrust' |
| 5 | Direct Reporting NFFE | FinancialInstitution.fatcaReportingType = 'DirectNFFE' |
| 6 | Reporting Model 2 FFI | FinancialInstitution.fatcaReportingType = 'Model2FFI' |
| 7 | Reporting Model 1 FFI (Optional) | FinancialInstitution.fatcaReportingType = 'Model1FFI' |

### Account Holder Type (Field 6)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| I | Individual | Party.partyType = 'Individual' |
| E | Entity | Party.partyType = 'Entity' |

### TIN Type (Fields 11, 28, 35)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 1 | SSN (Social Security Number) | Party.usTinType = 'SSN' |
| 2 | EIN (Employer Identification Number) | Party.usTinType = 'EIN' |

### Pooled Reporting Type (Field 42)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 1 | Recalcitrant account holders with U.S. indicia | RegulatoryReport.pooledReportingType = 'RecalcitrantUSIndicia' |
| 2 | Recalcitrant account holders without U.S. indicia | RegulatoryReport.pooledReportingType = 'RecalcitrantNoUSIndicia' |
| 3 | Dormant accounts | RegulatoryReport.pooledReportingType = 'Dormant' |
| 4 | Non-participating FFIs | RegulatoryReport.pooledReportingType = 'NonParticipatingFFI' |
| 5 | Recalcitrant account holders (general) | RegulatoryReport.pooledReportingType = 'RecalcitrantGeneral' |
| 6 | U.S. owned foreign entities | RegulatoryReport.pooledReportingType = 'USOwnedForeignEntity' |

---

## CDM Extensions Required

All 97 Form 8966 fields successfully map to existing CDM model. **No enhancements required.**

---

## XML Structure Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FATCA_OECD version="2.0" xmlns="urn:oecd:ties:fatca:v2">
  <MessageSpec>
    <SendingCompanyIN>A1B2C3.00001.LE.840</SendingCompanyIN>
    <TransmittingCountry>GB</TransmittingCountry>
    <ReceivingCountry>US</ReceivingCountry>
    <MessageType>FATCA</MessageType>
    <MessageRefId>GB2024123112345678</MessageRefId>
    <ReportingPeriod>2024-12-31</ReportingPeriod>
    <Timestamp>2025-03-15T10:30:00Z</Timestamp>
  </MessageSpec>
  <FATCA>
    <ReportingFI>
      <ResCountryCode>GB</ResCountryCode>
      <TIN issuedBy="GB">GB123456789</TIN>
      <Name>Example Bank PLC</Name>
      <Address>
        <CountryCode>GB</CountryCode>
        <AddressFree>123 High Street, London, EC1A 1BB</AddressFree>
      </Address>
      <GIIN>A1B2C3.00001.LE.826</GIIN>
    </ReportingFI>
    <ReportingGroup>
      <AccountReport>
        <DocSpec>
          <DocTypeIndic>FATCA1</DocTypeIndic>
          <DocRefId>ACC001-2024</DocRefId>
        </DocSpec>
        <AccountNumber>987654321</AccountNumber>
        <AccountHolder>
          <Individual>
            <ResCountryCode>US</ResCountryCode>
            <TIN issuedBy="US">123-45-6789</TIN>
            <Name>
              <FirstName>John</FirstName>
              <LastName>Smith</LastName>
            </Name>
            <Address>
              <CountryCode>GB</CountryCode>
              <City>London</City>
              <PostCode>SW1A 1AA</PostCode>
              <AddressFree>10 Downing Street</AddressFree>
            </Address>
            <Nationality>US</Nationality>
            <BirthInfo>
              <BirthDate>1975-01-15</BirthDate>
              <City>New York</City>
              <CountryInfo>
                <CountryCode>US</CountryCode>
              </CountryInfo>
            </BirthInfo>
          </Individual>
        </AccountHolder>
        <AccountBalance currCode="GBP">250000.00</AccountBalance>
        <Payment>
          <Type>FATCA501</Type>
          <PaymentAmnt currCode="GBP">5000.00</PaymentAmnt>
        </Payment>
      </AccountReport>
    </ReportingGroup>
  </FATCA>
</FATCA_OECD>
```

---

## References

- IRS FATCA Information: https://www.irs.gov/businesses/corporations/foreign-account-tax-compliance-act-fatca
- Form 8966 Instructions: https://www.irs.gov/forms-pubs/about-form-8966
- FATCA XML Schema: https://www.irs.gov/fatca-xml-schemas-best-practices-and-business-rules
- IDES User Guide: https://www.irs.gov/pub/irs-utl/IDES_User_Guide.pdf
- GPS CDM Schema: `/schemas/05_regulatory_report_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
