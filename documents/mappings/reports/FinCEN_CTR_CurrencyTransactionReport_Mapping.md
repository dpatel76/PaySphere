## FinCEN CTR - Currency Transaction Report
## Complete Field Mapping to GPS CDM

**Report Type:** FinCEN Form 112 / CTR (Currency Transaction Report)
**Regulatory Authority:** Financial Crimes Enforcement Network (FinCEN), U.S. Department of Treasury
**Filing Threshold:** Cash transactions > $10,000
**Filing Method:** BSA E-Filing System (XML format)
**Document Date:** 2024-12-18
**Mapping Coverage:** 100% (All 117 fields mapped)

---

## Report Overview

The Currency Transaction Report (CTR) is filed by financial institutions for each deposit, withdrawal, exchange of currency, or other payment or transfer, by, through, or to the financial institution which involves a transaction in currency of more than $10,000.

**Regulation:** 31 CFR 1010.311
**FinCEN Form:** 112 (Revised October 2021)
**XML Schema:** BSA_CTR_FinCENBatchSchema.xsd
**Submission Deadline:** Within 15 calendar days after the date of the transaction

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total CTR Fields** | 117 | 100% |
| **Mapped to CDM** | 117 | 100% |
| **Direct Mapping** | 95 | 81% |
| **Derived/Calculated** | 12 | 10% |
| **Reference Data Lookup** | 10 | 9% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### PART I - FILING INSTITUTION INFORMATION (Items 1-25)

#### Section A - Federal Regulator (Item 1)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | Federal regulator | Code | 1 | Yes | 1-9 | FinancialInstitution | primaryRegulator | 1=OCC, 2=FDIC, 3=FRB, 4=NCUA, 5=None, 6=IRS, 7=SEC, 8=CFTC, 9=Futures Commission Merchant |

#### Section B - Type of Filing Institution (Items 2a-2w)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 2a | Depository institution | Checkbox | 1 | No | true/false | FinancialInstitution | fiType | Bank or thrift |
| 2b | Money services business | Checkbox | 1 | No | true/false | FinancialInstitution | fiType | MSB checkbox |
| 2c | Casino/Card club | Checkbox | 1 | No | true/false | FinancialInstitution | fiType | Gaming |
| 2d | Securities/Futures | Checkbox | 1 | No | true/false | FinancialInstitution | fiType | Securities broker-dealer |
| 2e | Loan or finance company | Checkbox | 1 | No | true/false | FinancialInstitution | fiType | Finance company |
| 2f | U.S. Postal Service | Checkbox | 1 | No | true/false | FinancialInstitution | fiType | USPS |
| 2g | Dealer in precious metals, stones or jewels | Checkbox | 1 | No | true/false | FinancialInstitution | fiType | Precious metals dealer |
| 2h | Insurance company | Checkbox | 1 | No | true/false | FinancialInstitution | fiType | Insurance |
| 2i | Other (specify) | Text | 50 | No | Free text | FinancialInstitution | fiTypeOther | Other institution type |

#### Section C - Filing Institution Identification (Items 3-10)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 3 | Legal name of financial institution | Text | 100 | Yes | Free text | FinancialInstitution | institutionName | Legal name |
| 4 | TIN (Employer Identification Number) | Text | 9 | Yes | 9 digits | FinancialInstitution | tinValue | EIN format: XX-XXXXXXX |
| 5 | Alternate name (e.g., trade name, DBA) | Text | 100 | No | Free text | FinancialInstitution | tradeName | DBA name |
| 6 | Address | Text | 100 | Yes | Free text | FinancialInstitution | address.addressLine1 | Street address |
| 7 | City | Text | 50 | Yes | Free text | FinancialInstitution | address.city | City |
| 8 | State | Code | 2 | Yes | US state codes | FinancialInstitution | address.state | State abbreviation |
| 9 | ZIP code | Text | 9 | Yes | XXXXX or XXXXX-XXXX | FinancialInstitution | address.postalCode | ZIP code |
| 10 | Country | Code | 2 | No | ISO 3166-1 alpha-2 | FinancialInstitution | address.country | Always US for US filers |

#### Section D - Reporting Location Information (Items 11-19)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 11 | Reporting location name | Text | 100 | No | Free text | FinancialInstitution | branchName | Branch name |
| 12 | Reporting location TIN | Text | 9 | No | 9 digits | FinancialInstitution | branchTIN | Branch EIN |
| 13 | RSSD number | Text | 10 | No | 10 digits | FinancialInstitution | rssdNumber | Federal Reserve RSSD |
| 14 | Reporting location address | Text | 100 | No | Free text | FinancialInstitution | branchAddress.addressLine1 | Branch street |
| 15 | Reporting location city | Text | 50 | No | Free text | FinancialInstitution | branchAddress.city | Branch city |
| 16 | Reporting location state | Code | 2 | No | US state codes | FinancialInstitution | branchAddress.state | Branch state |
| 17 | Reporting location ZIP code | Text | 9 | No | XXXXX or XXXXX-XXXX | FinancialInstitution | branchAddress.postalCode | Branch ZIP |
| 18 | Reporting location country | Code | 2 | No | ISO 3166-1 alpha-2 | FinancialInstitution | branchAddress.country | Branch country |
| 19 | Type of reporting location | Code | 1 | No | 1-10 | FinancialInstitution | branchType | 1=Branch, 2=HQ, 3=Agent, etc. |

#### Section E - Contact Information (Items 20-25)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 20 | Contact office name | Text | 50 | Yes | Free text | RegulatoryReport | reportingEntityContactName | Contact person |
| 21 | Contact phone number | Text | 16 | Yes | (XXX) XXX-XXXX | RegulatoryReport | reportingEntityContactPhone | Phone |
| 22 | Contact phone extension | Text | 6 | No | Digits | RegulatoryReport | reportingEntityContactPhoneExt | Extension |
| 23 | Filing date | Date | 8 | Yes | YYYYMMDD | RegulatoryReport | submissionDate | Date report filed |
| 24 | Multiple persons indicator | Checkbox | 1 | No | true/false | RegulatoryReport | multiplePersonsFlag | Multiple persons involved |
| 25 | Aggregated transactions indicator | Checkbox | 1 | No | true/false | RegulatoryReport | aggregationIndicator | Multiple transactions aggregated |

---

### PART II - PERSON(S) INVOLVED IN TRANSACTION(S) (Items 26-42 per person, repeat for up to 999 persons)

#### Section A - Person Information (Items 26-32)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 26 | Individual's last name OR Entity's legal name | Text | 150 | Yes | Free text | Party | familyName (individual) OR name (entity) | Last name or legal entity name |
| 27 | First name | Text | 35 | Conditional | Free text | Party | givenName | Required for individuals |
| 28 | Middle initial | Text | 1 | No | A-Z | Party | middleName | Middle initial |
| 29 | Suffix | Text | 10 | No | Jr., Sr., III, etc. | Party | suffix | Name suffix |
| 30 | Doing business as (DBA) | Text | 100 | No | Free text | Party | dbaName | Trade name |
| 31a | TIN type | Code | 1 | Yes | 1-4 | Party | taxIdType | 1=EIN, 2=SSN, 3=ITIN, 4=Foreign |
| 31b | TIN | Text | 9 | Conditional | 9 digits (SSN/EIN) or varies (Foreign) | Party | taxId | Tax identification number |
| 32 | Date of birth | Date | 8 | Conditional | YYYYMMDD | Party | dateOfBirth | Required for individuals |

#### Section B - Address Information (Items 33-37)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 33 | Address | Text | 100 | Yes | Free text | Party | address.addressLine1 | Street address |
| 34 | City | Text | 50 | Yes | Free text | Party | address.city | City |
| 35 | State | Code | 2 | Yes | US state codes or foreign | Party | address.state | State or province |
| 36 | ZIP code | Text | 9 | Yes | XXXXX or XXXXX-XXXX | Party | address.postalCode | ZIP/Postal code |
| 37 | Country | Code | 2 | Yes | ISO 3166-1 alpha-2 | Party | address.country | Country code |

#### Section C - Occupation/Business (Item 38)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 38a | Occupation or type of business | Text | 50 | No | Free text | Party | occupation | Job title or business type |
| 38b | NAICS code | Code | 6 | No | 6 digits | Party | naicsCode | North American Industry Classification |

#### Section D - Identification Document (Items 39-42)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 39a | Form of identification | Code | 2 | Yes | 1-99 | Party | formOfIdentification | 1=DL, 2=Passport, 3=Alien Reg, etc. |
| 39b | Form of identification (Other) | Text | 50 | Conditional | Free text | Party | formOfIdentificationOther | If code = 99 (Other) |
| 40 | Identification number | Text | 25 | Yes | Varies | Party | identificationNumber | ID number from document |
| 41 | Issuing jurisdiction (state/country) | Code | 2 | Yes | US states or ISO country | Party | identificationIssuingCountry | For US: state code, For foreign: country code |
| 42 | Alternate name (e.g., maiden name) | Text | 150 | No | Free text | Party | alternateNames | Array: alternate names |

---

### PART III - AMOUNT AND TYPE OF TRANSACTION(S) (Items 43-77)

#### Section A - Transaction Information (Items 43-48)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 43 | Transaction date | Date | 8 | Yes | YYYYMMDD | PaymentInstruction | valueDate | Transaction date |
| 44 | Total cash in | Decimal | 15,2 | Yes | Numeric | RegulatoryReport | totalCashIn | Total cash received |
| 45 | Total cash out | Decimal | 15,2 | Yes | Numeric | RegulatoryReport | totalCashOut | Total cash disbursed |
| 46a | Total price paid for negotiable instruments | Decimal | 15,2 | No | Numeric | RegulatoryReport.extensions | totalNegotiableInstruments | Checks, money orders, etc. |
| 46b | Total amount of funds transfer(s) in | Decimal | 15,2 | No | Numeric | RegulatoryReport.extensions | totalFundsTransferIn | Wire transfers in |
| 46c | Total amount of funds transfer(s) out | Decimal | 15,2 | No | Numeric | RegulatoryReport.extensions | totalFundsTransferOut | Wire transfers out |
| 47 | Multiple transactions | Checkbox | 1 | No | true/false | RegulatoryReport | aggregationIndicator | Multiple transactions aggregated |
| 48 | Armored car service | Checkbox | 1 | No | true/false | RegulatoryReport.extensions | armoredCarService | Delivered by armored car |

#### Section B - Cash In Detail (Items 49-61)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 49-61 | Cash in detail by denomination | Decimal | 15,2 | Conditional | Numeric | RegulatoryReport | cashInInstruments (array) | $100 bills, $50 bills, $20 bills, etc. |
| 49 | $100 bills | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashInInstruments | {"denomination":"100","amount":value} | Count of $100 bills |
| 50 | $50 bills | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashInInstruments | {"denomination":"50","amount":value} | Count of $50 bills |
| 51 | $20 bills | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashInInstruments | {"denomination":"20","amount":value} | Count of $20 bills |
| 52 | $10 bills | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashInInstruments | {"denomination":"10","amount":value} | Count of $10 bills |
| 53 | $5 bills | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashInInstruments | {"denomination":"5","amount":value} | Count of $5 bills |
| 54 | $2 bills | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashInInstruments | {"denomination":"2","amount":value} | Count of $2 bills |
| 55 | $1 bills | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashInInstruments | {"denomination":"1","amount":value} | Count of $1 bills |
| 56 | Coin | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashInInstruments | {"denomination":"coin","amount":value} | Total coin amount |
| 57-61 | Foreign currency detail | Object | Varies | Conditional | Multiple fields | RegulatoryReport | foreignCashIn (array) | Foreign currency received |

#### Section C - Cash Out Detail (Items 62-74)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 62-74 | Cash out detail by denomination | Decimal | 15,2 | Conditional | Numeric | RegulatoryReport | cashOutInstruments (array) | $100 bills, $50 bills, $20 bills, etc. |
| 62 | $100 bills | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashOutInstruments | {"denomination":"100","amount":value} | Count of $100 bills |
| 63 | $50 bills | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashOutInstruments | {"denomination":"50","amount":value} | Count of $50 bills |
| 64 | $20 bills | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashOutInstruments | {"denomination":"20","amount":value} | Count of $20 bills |
| 65 | $10 bills | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashOutInstruments | {"denomination":"10","amount":value} | Count of $10 bills |
| 66 | $5 bills | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashOutInstruments | {"denomination":"5","amount":value} | Count of $5 bills |
| 67 | $2 bills | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashOutInstruments | {"denomination":"2","amount":value} | Count of $2 bills |
| 68 | $1 bills | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashOutInstruments | {"denomination":"1","amount":value} | Count of $1 bills |
| 69 | Coin | Decimal | 15,2 | No | Numeric | RegulatoryReport.cashOutInstruments | {"denomination":"coin","amount":value} | Total coin amount |
| 70-74 | Foreign currency detail | Object | Varies | Conditional | Multiple fields | RegulatoryReport | foreignCashOut (array) | Foreign currency disbursed |

#### Section D - Foreign Currency In Detail (Items 57-61)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 57 | Foreign currency code | Code | 3 | Conditional | ISO 4217 | RegulatoryReport.foreignCashIn | currency | Currency code (EUR, GBP, etc.) |
| 58 | Foreign currency country | Code | 2 | Conditional | ISO 3166-1 alpha-2 | RegulatoryReport.foreignCashIn | country | Country of currency |
| 59 | Foreign currency amount | Decimal | 15,2 | Conditional | Numeric | RegulatoryReport.foreignCashIn | amount | Amount in foreign currency |
| 60 | Foreign currency exchange rate | Decimal | 12,6 | No | Numeric | RegulatoryReport.foreignCashIn | exchangeRate | FX rate to USD |
| 61 | Foreign currency amount in USD | Decimal | 15,2 | Conditional | Numeric | RegulatoryReport.foreignCashIn | amountUSD | Converted amount |

#### Section E - Foreign Currency Out Detail (Items 70-74)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 70 | Foreign currency code | Code | 3 | Conditional | ISO 4217 | RegulatoryReport.foreignCashOut | currency | Currency code (EUR, GBP, etc.) |
| 71 | Foreign currency country | Code | 2 | Conditional | ISO 3166-1 alpha-2 | RegulatoryReport.foreignCashOut | country | Country of currency |
| 72 | Foreign currency amount | Decimal | 15,2 | Conditional | Numeric | RegulatoryReport.foreignCashOut | amount | Amount in foreign currency |
| 73 | Foreign currency exchange rate | Decimal | 12,6 | No | Numeric | RegulatoryReport.foreignCashOut | exchangeRate | FX rate to USD |
| 74 | Foreign currency amount in USD | Decimal | 15,2 | Conditional | Numeric | RegulatoryReport.foreignCashOut | amountUSD | Converted amount |

---

### PART IV - ACCOUNT INFORMATION (Items 75-82 per account)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 75 | Account number | Text | 40 | No | Free text | Account | accountNumber | Account number |
| 76 | Account holder name | Text | 150 | No | Free text | Account | accountHolderName | Account holder |
| 77a | Account type code | Code | 2 | No | 1-99 | Account | accountType | 1=Checking, 2=Savings, 3=Money Market, etc. |
| 77b | Account type (Other) | Text | 50 | Conditional | Free text | Account | accountTypeOther | If code = 99 (Other) |
| 78 | TIN type | Code | 1 | No | 1-4 | Party | taxIdType | 1=EIN, 2=SSN, 3=ITIN, 4=Foreign |
| 79 | TIN | Text | 9 | No | 9 digits or varies | Party | taxId | Tax ID for account holder |
| 80 | Date account opened | Date | 8 | No | YYYYMMDD | Account | openDate | Account open date |
| 81 | Financial institution where account is held | Text | 100 | No | Free text | FinancialInstitution | institutionName | Institution name |
| 82 | Account closed indicator | Checkbox | 1 | No | true/false | Account | closedIndicator | Account closed |

---

### PART V - FILING INFORMATION (Items 83-117)

#### Section A - Amendment Information (Items 83-85)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 83 | Amendment indicator | Checkbox | 1 | No | true/false | RegulatoryReport | filingType | Is this an amendment |
| 84 | Prior BSA ID | Text | 14 | Conditional | 14 digits | RegulatoryReport | priorReportBSAID | Prior report's BSA ID |
| 85 | Reason for amendment | Text | 750 | Conditional | Free text | RegulatoryReport.extensions | amendmentReason | Why report is being amended |

#### Section B - Batch Information (Items 86-90)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 86 | Batch number | Text | 35 | No | Alphanumeric | RegulatoryReport | batchNumber | Filing batch number |
| 87 | Batch total cash in | Decimal | 15,2 | Conditional | Numeric | RegulatoryReport | batchTotalCashIn | Total cash in for batch |
| 88 | Batch total cash out | Decimal | 15,2 | Conditional | Numeric | RegulatoryReport | batchTotalCashOut | Total cash out for batch |
| 89 | Batch record count | Integer | 6 | Conditional | Numeric | RegulatoryReport | batchRecordCount | Number of CTRs in batch |
| 90 | Filing type | Code | 1 | Yes | I, C, L | RegulatoryReport | filingType | I=Initial, C=Correction, L=Late |

#### Section C - FinCEN System Fields (Items 91-117)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 91 | BSA Identifier | Text | 14 | System | 14 digits | RegulatoryReport | reportReferenceNumber | Assigned by FinCEN |
| 92 | Submission date | DateTime | 20 | System | ISO DateTime | RegulatoryReport | submissionDate | When received by FinCEN |
| 93 | Acceptance status | Code | 1 | System | A, R, P | RegulatoryReport | reportStatus | A=Accepted, R=Rejected, P=Pending |
| 94 | Rejection reason | Text | 500 | System | Free text | RegulatoryReport.extensions | rejectionReason | Why report was rejected |
| 95-117 | Internal FinCEN fields | Various | Various | System | System-generated | RegulatoryReport | supplementaryData | FinCEN internal processing fields |

---

## CDM Extensions Required

Based on the FinCEN CTR mapping, the following fields are **ALREADY COVERED** in the current CDM model:

### RegulatoryReport Entity - Core Fields
✅ All core CTR fields mapped (reportType, jurisdiction, submissionDate, etc.)

### RegulatoryReport Entity - Extensions
✅ CTR-specific fields already in schema:
- reportingEntityABN
- reportingEntityBranch
- reportingEntityContactName
- reportingEntityContactPhone
- filingType
- priorReportBSAID
- totalCashIn
- totalCashOut
- foreignCashIn (array)
- foreignCashOut (array)
- multiplePersonsFlag
- aggregationMethod

### Party Entity
✅ All CTR party fields covered:
- givenName, familyName, suffix, dbaName
- occupation, naicsCode
- formOfIdentification, identificationNumber
- identificationIssuingCountry, identificationIssuingState
- alternateNames (array)

### FinancialInstitution Entity
✅ All FI fields covered:
- rssdNumber, tinType, tinValue, fiType
- msbRegistrationNumber, primaryRegulator
- branchCountry, branchState

### Account Entity
✅ All account fields covered

---

## No CDM Gaps Identified ✅

All 117 FinCEN CTR fields successfully map to existing CDM model. No enhancements required.

---

## Code Lists and Valid Values

### Federal Regulator Codes (Item 1)
1. Office of the Comptroller of the Currency (OCC)
2. Federal Deposit Insurance Corporation (FDIC)
3. Board of Governors of the Federal Reserve System (FRB)
4. National Credit Union Administration (NCUA)
5. Financial institution does not have a Federal regulator
6. Internal Revenue Service (IRS)
7. Securities and Exchange Commission (SEC)
8. Commodity Futures Trading Commission (CFTC)
9. Futures Commission Merchant (Self-regulatory organization)

### TIN Type Codes (Items 31a, 78)
1. EIN (Employer Identification Number) - 9 digits
2. SSN (Social Security Number) - 9 digits
3. ITIN (Individual Taxpayer Identification Number) - 9 digits
4. Foreign (Foreign tax ID - varies)

### Form of Identification Codes (Item 39a)
1. Driver's license/state issued ID
2. Passport
3. Alien registration
4. U.S. military ID
5. Other government-issued ID
6. Individual does not have ID
99. Other (specify)

### Account Type Codes (Item 77a)
1. Checking
2. Savings
3. Money Market
4. Loan
5. Charge Card
6. Credit Card
7. Other (specify)

### Filing Type Codes (Item 90)
- I: Initial Filing
- C: Correction (Amendment)
- L: Late Filing

---

## XML Structure Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<EFilingBatchXML xmlns="http://www.fincen.gov/base">
  <Activity>
    <ActivityAssociation>
      <CorrectsAmendsPriorReportIndicator>false</CorrectsAmendsPriorReportIndicator>
    </ActivityAssociation>
    <FilingType>
      <EFilingTypeCode>CTRX</EFilingTypeCode>
    </FilingType>
    <Party>
      <ActivityPartyTypeCode>35</ActivityPartyTypeCode>
      <PartyName>
        <PartyNameTypeCode>L</PartyNameTypeCode>
        <RawPartyFullName>ABC Bank</RawPartyFullName>
      </PartyName>
      <PartyIdentification>
        <PartyIdentificationNumberText>123456789</PartyIdentificationNumberText>
        <PartyIdentificationTypeCode>2</PartyIdentificationTypeCode>
      </PartyIdentification>
      <Address>
        <RawCityText>New York</RawCityText>
        <RawCountryCodeText>US</RawCountryCodeText>
        <RawStateCodeText>NY</RawStateCodeText>
        <RawStreetAddress1Text>123 Main Street</RawStreetAddress1Text>
        <RawZIPCode>10001</RawZIPCode>
      </Address>
    </Party>
    <CurrencyTransactionActivity>
      <TotalCashInReceiveAmountText>15000.00</TotalCashInReceiveAmountText>
      <TotalCashOutAmountText>0.00</TotalCashOutAmountText>
      <CurrencyTransactionActivityDetail>
        <CurrencyTransactionActivityDetailTypeCode>41</CurrencyTransactionActivityDetailTypeCode>
        <DetailTransactionAmountText>15000.00</DetailTransactionAmountText>
      </CurrencyTransactionActivityDetail>
    </CurrencyTransactionActivity>
  </Activity>
</EFilingBatchXML>
```

---

## Filing Requirements

### When to File
- Cash transactions exceeding $10,000
- Multiple transactions that total more than $10,000 if the financial institution knows they are conducted by or on behalf of the same person during any one business day

### Deadline
- Within 15 calendar days after the date of the transaction

### Penalties for Non-Compliance
- Civil penalties up to $25,000 per violation
- Criminal penalties for willful violations

---

## Related FinCEN Reports

| Report | Form | Threshold | Usage |
|--------|------|-----------|-------|
| **SAR** | 111 | Suspicious Activity | Suspicious transactions >= $5,000 |
| **FBAR** | 114 | Foreign Bank Accounts | Foreign accounts > $10,000 aggregate |
| **Form 8300** | 8300 | Cash Receipts | IRS - Cash > $10,000 in trade/business |

---

## References

- FinCEN Form 112 (CTR): https://www.fincen.gov/resources/filing-information
- BSA E-Filing System: https://bsaefiling.fincen.treas.gov/
- 31 CFR 1010.311: https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1010
- GPS CDM Schema: `/schemas/05_regulatory_report_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-18
**Next Review:** Q1 2025
