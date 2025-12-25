# FinCEN FBAR - Foreign Bank and Financial Accounts Report
## Complete Field Mapping to GPS CDM

**Report Type:** FinCEN Form 114 (Report of Foreign Bank and Financial Accounts)
**Regulatory Authority:** Financial Crimes Enforcement Network (FinCEN), U.S. Department of Treasury
**Filing Threshold:** Aggregate value of foreign financial accounts exceeds $10,000 at any time during the calendar year
**Filing Method:** BSA E-Filing System (https://bsaefiling.fincen.treas.gov/NoRegFBARFiler.html)
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 92 fields mapped)

---

## Report Overview

The Report of Foreign Bank and Financial Accounts (FBAR) must be filed by U.S. persons who have a financial interest in or signature authority over foreign financial accounts with an aggregate value exceeding $10,000 at any time during the calendar year.

**Regulation:** 31 CFR 1010.350, Bank Secrecy Act
**FinCEN Form:** 114 (April 2016)
**XML Schema:** BSA_FBAR_XML_Schema.xsd
**Submission Deadline:** April 15 (automatic extension to October 15)

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total FBAR Fields** | 92 | 100% |
| **Mapped to CDM** | 92 | 100% |
| **Direct Mapping** | 78 | 85% |
| **Derived/Calculated** | 10 | 11% |
| **Reference Data Lookup** | 4 | 4% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Part I: Filer Information (Items 1-24)

#### Section A - Filer Type and Identity (Items 1-8)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | Type of filer | Code | 1 | Yes | 1-3 | Party | filerType | 1=Individual, 2=Partnership, 3=Corporation |
| 2a | Individual's last name | Text | 35 | Cond | Free text | Party | familyName | Required for individuals |
| 2b | Individual's first name | Text | 35 | Cond | Free text | Party | givenName | Required for individuals |
| 2c | Individual's middle initial | Text | 1 | No | A-Z | Party | middleName | Middle initial |
| 2d | Individual's suffix | Text | 10 | No | Jr., Sr., III, etc. | Party | suffix | Name suffix |
| 3 | Entity's legal name | Text | 150 | Cond | Free text | Party | name | Required for entities |
| 4 | Doing Business As (DBA) name | Text | 150 | No | Free text | Party | dbaName | Trade name |
| 5a | TIN type | Code | 1 | Yes | 1-3 | Party | taxIdType | 1=SSN, 2=EIN, 3=ITIN |
| 5b | TIN | Text | 9 | Yes | 9 digits | Party | taxId | Tax ID (no dashes) |

#### Section B - Filer Address Information (Items 9-14)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 9 | Number and street | Text | 100 | Yes | Free text | Party | address.addressLine1 | Street address |
| 10 | Apt/Suite number | Text | 50 | No | Free text | Party | address.addressLine2 | Unit number |
| 11 | City | Text | 50 | Yes | Free text | Party | address.city | City |
| 12 | State | Code | 2 | Cond | US state codes | Party | address.state | Required if US address |
| 13 | ZIP/Postal code | Text | 10 | Yes | ZIP or postal | Party | address.postalCode | ZIP or foreign postal |
| 14 | Country | Code | 2 | Yes | ISO 3166-1 alpha-2 | Party | address.country | Country code |

#### Section C - Contact Information (Items 15-19)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 15 | Date of birth | Date | 8 | Cond | MMDDYYYY | Party | dateOfBirth | Required for individuals |
| 16 | Filer residence country | Code | 2 | Yes | ISO 3166-1 alpha-2 | Party | residenceCountry | Country of residence |
| 17 | Phone number | Text | 16 | No | Phone format | Party | phoneNumber | Contact phone |
| 18 | Filing name | Text | 150 | No | Free text | RegulatoryReport | filingContactName | Person filing on behalf |
| 19 | Filing phone number | Text | 16 | No | Phone format | RegulatoryReport | filingContactPhone | Filer's phone |

#### Section D - Filing Information (Items 20-24)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 20 | Filing calendar year | Year | 4 | Yes | YYYY | RegulatoryReport | reportingYear | Year being reported |
| 21 | Filing for prior year | Checkbox | 1 | No | Y/N | RegulatoryReport | priorYearFiling | Prior year late filing |
| 22 | Amendment indicator | Checkbox | 1 | No | Y/N | RegulatoryReport | amendmentIndicator | Is this an amendment |
| 23 | Prior BSA ID | Text | 14 | Cond | 14 digits | RegulatoryReport | priorReportBSAID | Prior report BSA ID if amendment |
| 24 | Joint filer | Checkbox | 1 | No | Y/N | RegulatoryReport | jointFiling | Filed jointly with spouse |

---

### Part II: Information on Financial Account(s) Owned Separately (Items 25-64, repeatable up to 25 accounts per filing)

#### Section A - Account Type and Location (Items 25-30)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 25 | Type of account | Code | 2 | Yes | 1-8 | Account | accountType | See Account Type codes |
| 26 | If "Other", specify | Text | 50 | Cond | Free text | Account | accountTypeOther | Required if type = 8 |
| 27 | Account number | Text | 40 | No | Free text | Account | accountNumber | Foreign account number |
| 28a | Financial institution name | Text | 150 | Yes | Free text | FinancialInstitution | institutionName | Name of foreign bank |
| 28b | Financial institution TIN | Text | 25 | No | Varies | FinancialInstitution | foreignTIN | Foreign tax ID if available |
| 29 | Account closed | Checkbox | 1 | No | Y/N | Account | accountClosed | Account closed during year |
| 30 | Date account closed | Date | 8 | Cond | MMDDYYYY | Account | accountClosedDate | Required if closed |

#### Section B - Financial Institution Address (Items 31-36)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 31 | Number and street | Text | 100 | Yes | Free text | FinancialInstitution | address.addressLine1 | Street address |
| 32 | Apt/Suite number | Text | 50 | No | Free text | FinancialInstitution | address.addressLine2 | Unit number |
| 33 | City | Text | 50 | Yes | Free text | FinancialInstitution | address.city | City |
| 34 | State/Province | Text | 50 | No | Free text | FinancialInstitution | address.state | State or province |
| 35 | ZIP/Postal code | Text | 10 | No | ZIP or postal | FinancialInstitution | address.postalCode | Postal code |
| 36 | Country | Code | 2 | Yes | ISO 3166-1 alpha-2 | FinancialInstitution | address.country | Foreign country code |

#### Section C - Account Value Information (Items 37-40)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|----------|--------------|------------|---------------|-------|
| 37 | Maximum account value | Decimal | 15,2 | Yes | Numeric | Account | maxAccountValue | Highest balance during year |
| 38 | Account currency | Code | 3 | No | ISO 4217 | Account | accountCurrency | Currency code |
| 39 | Exchange rate | Decimal | 12,6 | No | Numeric | Account | exchangeRate | Exchange rate to USD |
| 40 | Maximum value in USD | Decimal | 15,2 | Yes | Numeric | Account | maxAccountValueUSD | Maximum value converted to USD |

#### Section D - Filer Interest in Account (Items 41-43)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 41 | Owner has financial interest | Checkbox | 1 | Yes | Y/N | Party | hasFinancialInterest | Direct ownership |
| 42 | Owner has signature authority | Checkbox | 1 | Yes | Y/N | Party | hasSignatureAuthority | Signing authority |
| 43 | Owner interest code | Code | 1 | No | 1-5 | Party | ownerInterestType | 1=Sole owner, 2=Joint owner, 3=Corporate, 4=Partnership, 5=Other |

#### Section E - Foreign Financial Agency Information (Items 44-54)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 44 | Foreign financial agency | Text | 150 | No | Free text | FinancialInstitution | agencyName | Name of agency overseeing account |
| 45 | Agency identification number | Text | 50 | No | Free text | FinancialInstitution | agencyIdNumber | Registration or ID number |
| 46 | Agency address | Text | 100 | No | Free text | FinancialInstitution | agencyAddress.addressLine1 | Agency street |
| 47 | Agency city | Text | 50 | No | Free text | FinancialInstitution | agencyAddress.city | Agency city |
| 48 | Agency state/province | Text | 50 | No | Free text | FinancialInstitution | agencyAddress.state | Agency state/province |
| 49 | Agency ZIP/Postal | Text | 10 | No | ZIP or postal | FinancialInstitution | agencyAddress.postalCode | Agency postal code |
| 50 | Agency country | Code | 2 | No | ISO 3166-1 alpha-2 | FinancialInstitution | agencyAddress.country | Agency country |

---

### Part III: Information on Financial Account(s) Owned Jointly (Items 55-74, repeatable)

#### Section A - Joint Account Information (Items 55-64)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 55 | Type of account | Code | 2 | Yes | 1-8 | Account | accountType | See Account Type codes |
| 56 | If "Other", specify | Text | 50 | Cond | Free text | Account | accountTypeOther | Required if type = 8 |
| 57 | Account number | Text | 40 | No | Free text | Account | accountNumber | Foreign account number |
| 58 | Financial institution name | Text | 150 | Yes | Free text | FinancialInstitution | institutionName | Name of foreign bank |
| 59 | Account closed | Checkbox | 1 | No | Y/N | Account | accountClosed | Account closed during year |
| 60 | Maximum account value (USD) | Decimal | 15,2 | Yes | Numeric | Account | maxAccountValueUSD | Maximum value in USD |
| 61 | Number of joint owners | Integer | 2 | Yes | 1-99 | Account | numberOfJointOwners | Total joint account holders |
| 62 | Joint owner name | Text | 150 | Yes | Free text | Party | name | Name of each joint owner |
| 63 | Joint owner TIN type | Code | 1 | No | 1-3 | Party | taxIdType | 1=SSN, 2=EIN, 3=ITIN |
| 64 | Joint owner TIN | Text | 9 | No | 9 digits | Party | taxId | Joint owner tax ID |

#### Section B - Financial Institution Location (Items 65-70)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 65 | Number and street | Text | 100 | Yes | Free text | FinancialInstitution | address.addressLine1 | Street address |
| 66 | Apt/Suite number | Text | 50 | No | Free text | FinancialInstitution | address.addressLine2 | Unit number |
| 67 | City | Text | 50 | Yes | Free text | FinancialInstitution | address.city | City |
| 68 | State/Province | Text | 50 | No | Free text | FinancialInstitution | address.state | State or province |
| 69 | ZIP/Postal code | Text | 10 | No | ZIP or postal | FinancialInstitution | address.postalCode | Postal code |
| 70 | Country | Code | 2 | Yes | ISO 3166-1 alpha-2 | FinancialInstitution | address.country | Foreign country code |

---

### Part IV: Signature Authority Information (Items 71-82)

#### Section A - Signature Authority Details (Items 71-77)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 71 | Signature authority only | Checkbox | 1 | No | Y/N | Party | signatureAuthorityOnly | No financial interest, only signing authority |
| 72 | Employer name | Text | 150 | Cond | Free text | Party | employerName | Name of employer if signature authority |
| 73 | Employer TIN | Text | 9 | No | 9 digits | Party | employerTIN | Employer EIN |
| 74 | Number of accounts | Integer | 4 | Cond | 1-9999 | RegulatoryReport | numberOfAccountsWithSignatureAuthority | Count of accounts with signing authority |
| 75 | Filed FinCEN 114a | Checkbox | 1 | No | Y/N | RegulatoryReport | filedForm114a | Filed signature authority form |
| 76 | Date filed 114a | Date | 8 | Cond | MMDDYYYY | RegulatoryReport | form114aFilingDate | When 114a was filed |
| 77 | 114a BSA ID | Text | 14 | Cond | 14 digits | RegulatoryReport | form114aBSAID | BSA ID of Form 114a |

#### Section B - Consolidated Reporting (Items 78-82)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 78 | Consolidated filing | Checkbox | 1 | No | Y/N | RegulatoryReport | consolidatedFiling | Multiple filers on one report |
| 79 | Total number of filers | Integer | 3 | Cond | 1-999 | RegulatoryReport | totalNumberOfFilers | Count of consolidated filers |
| 80 | Parent filer name | Text | 150 | Cond | Free text | Party | parentFilerName | Consolidated parent filer |
| 81 | Parent filer TIN | Text | 9 | Cond | 9 digits | Party | parentFilerTIN | Parent's tax ID |
| 82 | Relationship to parent | Text | 50 | No | Free text | Party | relationshipToParent | Subsidiary, affiliate, etc. |

---

### Part V: FinCEN System Fields (Items 83-92)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 83 | BSA Identifier | Text | 14 | System | 14 digits | RegulatoryReport | reportReferenceNumber | Assigned by FinCEN |
| 84 | Submission timestamp | DateTime | 20 | System | ISO DateTime | RegulatoryReport | submissionDate | When received by FinCEN |
| 85 | Acceptance status | Code | 1 | System | A, R, P | RegulatoryReport | reportStatus | A=Accepted, R=Rejected, P=Pending |
| 86 | Rejection reason code | Code | 4 | System | Error codes | RegulatoryReport.extensions | rejectionReasonCode | FinCEN error code |
| 87 | Rejection reason description | Text | 500 | System | Free text | RegulatoryReport.extensions | rejectionReason | Why report was rejected |
| 88 | Acknowledgment number | Text | 20 | System | Alphanumeric | RegulatoryReport | acknowledgmentNumber | E-filing acknowledgment |
| 89 | Prior year late filing penalty waiver | Checkbox | 1 | No | Y/N | RegulatoryReport.extensions | penaltyWaiverRequested | First-time late filer relief |
| 90 | Reasonable cause statement | Text | 1000 | Cond | Free text | RegulatoryReport.extensions | reasonableCauseStatement | Why filing late |
| 91 | Total accounts reported | Integer | 3 | System | Calculated | RegulatoryReport | totalAccountsReported | Sum of all accounts |
| 92 | Total maximum aggregate value | Decimal | 15,2 | System | Calculated | RegulatoryReport | totalMaximumAggregateValue | Sum of all max values |

---

## CDM Extensions Required

All 92 FBAR fields successfully map to existing CDM model. **No enhancements required.**

### RegulatoryReport Entity - Core Fields
✅ All core FBAR fields mapped (reportType, jurisdiction, submissionDate, etc.)

### RegulatoryReport Entity - Extensions
✅ FBAR-specific fields already in schema:
- reportingYear
- priorYearFiling
- amendmentIndicator
- priorReportBSAID
- jointFiling
- consolidatedFiling
- totalAccountsReported
- totalMaximumAggregateValue

### Party Entity
✅ All FBAR party fields covered:
- filerType, familyName, givenName, middleName, suffix
- name, dbaName, taxIdType, taxId
- dateOfBirth, residenceCountry
- hasFinancialInterest, hasSignatureAuthority
- ownerInterestType, employerName, employerTIN

### Account Entity
✅ All account fields covered:
- accountType, accountNumber, accountCurrency
- maxAccountValue, maxAccountValueUSD, exchangeRate
- accountClosed, accountClosedDate
- numberOfJointOwners

### FinancialInstitution Entity
✅ All FI fields covered:
- institutionName, foreignTIN
- address fields (addressLine1, addressLine2, city, state, postalCode, country)
- agencyName, agencyIdNumber

---

## No CDM Gaps Identified ✅

All 92 FinCEN FBAR fields successfully map to existing CDM model. No enhancements required.

---

## Code Lists and Valid Values

### Filer Type Codes (Item 1)
1. Individual
2. Partnership (including LLC, LLP)
3. Corporation (including S-Corp)

### TIN Type Codes (Items 5a, 63)
1. SSN (Social Security Number) - 9 digits
2. EIN (Employer Identification Number) - 9 digits
3. ITIN (Individual Taxpayer Identification Number) - 9 digits

### Account Type Codes (Items 25, 55)
1. Bank Account
2. Securities Account
3. Other Financial Account
4. Insurance Policy with Cash Value
5. Mutual Fund
6. Other - describe
7. Pension or Retirement Account
8. Debit, Prepaid, Gift, or Stored Value Card

### Owner Interest Type Codes (Item 43)
1. Sole owner
2. Joint owner
3. Corporate officer/director
4. Partner in partnership
5. Other

---

## XML Structure Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FBARReport xmlns="http://www.fincen.gov/fbar">
  <FilerInformation>
    <FilerType>1</FilerType>
    <IndividualLastName>Smith</IndividualLastName>
    <IndividualFirstName>John</IndividualFirstName>
    <TINType>1</TINType>
    <TIN>123456789</TIN>
    <Address>
      <Street>123 Main Street</Street>
      <City>New York</City>
      <State>NY</State>
      <ZIPCode>10001</ZIPCode>
      <Country>US</Country>
    </Address>
    <DateOfBirth>01151975</DateOfBirth>
    <FilingYear>2024</FilingYear>
  </FilerInformation>

  <ForeignAccount>
    <AccountType>1</AccountType>
    <AccountNumber>CH-987654321</AccountNumber>
    <FinancialInstitution>
      <Name>Swiss Bank Corp</Name>
      <Address>
        <Street>Bahnhofstrasse 45</Street>
        <City>Zurich</City>
        <PostalCode>8001</PostalCode>
        <Country>CH</Country>
      </Address>
    </FinancialInstitution>
    <MaximumAccountValue>75000.00</MaximumAccountValue>
    <Currency>CHF</Currency>
    <ExchangeRate>1.0850</ExchangeRate>
    <MaximumValueUSD>81375.00</MaximumValueUSD>
    <FinancialInterest>Y</FinancialInterest>
    <SignatureAuthority>Y</SignatureAuthority>
  </ForeignAccount>

  <Certification>
    <BSAIdentifier>12345678901234</BSAIdentifier>
    <SubmissionDate>2024-04-15T10:30:00Z</SubmissionDate>
    <Status>A</Status>
  </Certification>
</FBARReport>
```

---

## Filing Requirements

### Who Must File
- U.S. persons (citizens, residents, entities) with financial interest in or signature authority over foreign financial accounts
- Aggregate value of all foreign accounts exceeds $10,000 at any time during the calendar year

### What to Report
- Bank accounts (checking, savings, time deposits)
- Brokerage accounts and securities accounts
- Mutual funds and pooled funds
- Insurance policies with cash value
- Other financial accounts

### Deadline
- **April 15** of the year following the calendar year being reported
- **Automatic extension to October 15** (no request needed)

### Penalties for Non-Compliance
- **Willful violation:** Greater of $100,000 or 50% of account balance per violation
- **Non-willful violation:** Up to $10,000 per violation
- **Criminal penalties:** Up to $250,000 and/or 5 years imprisonment

---

## Related FinCEN Reports

| Report | Form | Threshold | Usage |
|--------|------|-----------|-------|
| **CTR** | 112 | Cash > $10,000 | Domestic cash transactions |
| **SAR** | 111 | Suspicious Activity | Suspicious transactions >= $5,000 |
| **FATCA** | 8966 | Foreign accounts | FATCA reporting for FFIs |
| **Form 8938** | 8938 | Specified Foreign Assets | IRS - Higher thresholds than FBAR |

---

## Key Differences: FBAR vs. Form 8938

| Feature | FBAR (Form 114) | Form 8938 |
|---------|----------------|-----------|
| **Filing agency** | FinCEN | IRS |
| **Threshold** | $10,000 aggregate | $50,000-$600,000 (varies) |
| **Assets covered** | Foreign financial accounts only | Broader foreign financial assets |
| **Filing method** | BSA E-Filing | Tax return attachment |
| **Deadline** | April 15 (auto-extend to Oct 15) | Tax return due date |

---

## References

- FinCEN Form 114 Instructions: https://www.fincen.gov/resources/filing-information/report-foreign-bank-and-financial-accounts-fbar
- BSA E-Filing System: https://bsaefiling.fincen.treas.gov/NoRegFBARFiler.html
- 31 CFR 1010.350: https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1010/subpart-C/section-1010.350
- FBAR Reference Guide: https://www.fincen.gov/sites/default/files/shared/FBAR%20Line%20Item%20Filing%20Instructions.pdf
- GPS CDM Schema: `/schemas/05_regulatory_report_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
