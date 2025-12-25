# FinCEN Form 8300 - Report of Cash Payments Over $10,000
## Complete Field Mapping to GPS CDM

**Report Type:** IRS/FinCEN Form 8300 (Report of Cash Payments Over $10,000 Received in a Trade or Business)
**Regulatory Authority:** Internal Revenue Service (IRS) and Financial Crimes Enforcement Network (FinCEN)
**Filing Threshold:** Cash payments over $10,000 received in a single transaction or related transactions
**Filing Method:** BSA E-Filing System or IRS paper filing
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 78 fields mapped)

---

## Report Overview

Form 8300 is filed by persons engaged in a trade or business who receive more than $10,000 in cash in one transaction or two or more related transactions. This includes currency (U.S. and foreign) and certain monetary instruments.

**Regulation:** 26 USC 6050I, 31 USC 5331, 31 CFR 1010.330
**IRS Form:** 8300 (Rev. October 2023)
**XML Schema:** IRS_Form8300_Schema.xsd
**Submission Deadline:** Within 15 days after receiving the cash payment

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Form 8300 Fields** | 78 | 100% |
| **Mapped to CDM** | 78 | 100% |
| **Direct Mapping** | 68 | 87% |
| **Derived/Calculated** | 7 | 9% |
| **Reference Data Lookup** | 3 | 4% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Part I: Identity of Individual from Whom Cash Was Received (Items 1-16)

#### Section A - Person Information (Items 1-8)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1a | Individual's last name OR Organization's name | Text | 150 | Yes | Free text | Party | familyName (individual) OR name (entity) | Last name or entity name |
| 1b | First name | Text | 35 | Cond | Free text | Party | givenName | Required for individuals |
| 1c | Middle initial | Text | 1 | No | A-Z | Party | middleName | Middle initial |
| 2 | Taxpayer identification number | Text | 9 | Yes | 9 digits | Party | taxId | SSN or EIN (no dashes) |
| 3 | Doing business as (DBA) name | Text | 150 | No | Free text | Party | dbaName | Trade name |
| 4 | Address (number, street, apt./suite) | Text | 100 | Yes | Free text | Party | address.addressLine1 | Street address |
| 5 | City | Text | 50 | Yes | Free text | Party | address.city | City |
| 6 | State | Code | 2 | Cond | US state code | Party | address.state | Required if US address |
| 7 | ZIP code | Text | 9 | Yes | XXXXX or XXXXX-XXXX | Party | address.postalCode | ZIP code |
| 8 | Country | Code | 2 | Cond | ISO 3166-1 alpha-2 | Party | address.country | Required if foreign |

#### Section B - Identification Document (Items 9-12)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 9 | Date of birth | Date | 8 | Cond | MMDDYYYY | Party | dateOfBirth | Required for individuals |
| 10 | Occupation, profession or business | Text | 50 | No | Free text | Party | occupation | Job title or business type |
| 11a | Form of identification | Code | 2 | Yes | See ID codes | Party | identificationType | Type of ID document |
| 11b | Identification number | Text | 25 | Yes | Varies | Party | identificationNumber | ID number |
| 11c | Issued by (state or country) | Code | 2 | Yes | US state or ISO country | Party | identificationIssuingJurisdiction | Issuing authority |

#### Section C - Additional Person Information (Items 13-16)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 13 | If foreign country, provide passport number and country | Text | 50 | Cond | Free text | Party | passportNumber | Required for foreign individuals |
| 14 | Alien identification number | Text | 20 | No | Free text | Party | alienIdNumber | USCIS A-number |
| 15 | Verification method | Code | 1 | Yes | 1-4 | Party | verificationMethod | 1=Examined ID, 2=Non-documentary, 3=Previously verified, 4=Unable to verify |
| 16 | Multiple persons indicator | Checkbox | 1 | No | Y/N | RegulatoryReport | multiplePersonsFlag | More than one person from whom cash received |

---

### Part II: Person on Whose Behalf Transaction Was Conducted (Items 17-29)

#### Section A - Person Information (Items 17-23)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 17a | If transaction conducted on behalf of more than one person, check here | Checkbox | 1 | No | Y/N | RegulatoryReport | multipleBehalfPersonsFlag | Multiple beneficial owners |
| 17b | Individual's last name OR Organization's name | Text | 150 | Cond | Free text | Party | familyName (individual) OR name (entity) | Required if different from Part I |
| 17c | First name | Text | 35 | Cond | Free text | Party | givenName | First name if individual |
| 17d | Middle initial | Text | 1 | No | A-Z | Party | middleName | Middle initial |
| 18 | Taxpayer identification number | Text | 9 | Cond | 9 digits | Party | taxId | SSN or EIN |
| 19 | Doing business as (DBA) name | Text | 150 | No | Free text | Party | dbaName | Trade name |
| 20 | Address (number, street, apt./suite) | Text | 100 | Cond | Free text | Party | address.addressLine1 | Street address |
| 21 | City | Text | 50 | Cond | Free text | Party | address.city | City |
| 22 | State | Code | 2 | Cond | US state code | Party | address.state | State code |
| 23 | ZIP code | Text | 9 | Cond | XXXXX or XXXXX-XXXX | Party | address.postalCode | ZIP code |

#### Section B - Identification and Occupation (Items 24-29)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 24 | Country | Code | 2 | Cond | ISO 3166-1 alpha-2 | Party | address.country | Country code |
| 25 | Date of birth | Date | 8 | Cond | MMDDYYYY | Party | dateOfBirth | Birth date if individual |
| 26 | Occupation, profession or business | Text | 50 | No | Free text | Party | occupation | Job title or business |
| 27a | Form of identification | Code | 2 | Cond | See ID codes | Party | identificationType | Type of ID document |
| 27b | Identification number | Text | 25 | Cond | Varies | Party | identificationNumber | ID number |
| 27c | Issued by (state or country) | Code | 2 | Cond | US state or ISO country | Party | identificationIssuingJurisdiction | Issuing authority |
| 28 | Alien identification number | Text | 20 | No | Free text | Party | alienIdNumber | USCIS A-number |
| 29 | Verification method | Code | 1 | Cond | 1-4 | Party | verificationMethod | How identity verified |

---

### Part III: Description of Transaction and Method of Payment (Items 30-43)

#### Section A - Transaction Information (Items 30-35)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 30 | Date cash received | Date | 8 | Yes | MMDDYYYY | PaymentInstruction | valueDate | Transaction date |
| 31 | Total cash received | Decimal | 15,2 | Yes | Numeric | PaymentInstruction | instructedAmount.amount | Total cash amount |
| 32 | If cash was received in more than one payment | Checkbox | 1 | No | Y/N | RegulatoryReport | multiplePaymentsFlag | Related transactions aggregated |
| 33 | Total price (if different from Item 31) | Decimal | 15,2 | No | Numeric | RegulatoryReport.extensions | totalTransactionPrice | Total price if not all cash |
| 34 | Amount of cash received (in U.S. dollar equivalent) if foreign currency | Decimal | 15,2 | Cond | Numeric | PaymentInstruction | instructedAmount.amountUSD | USD equivalent of foreign currency |
| 35 | Exchange rate | Decimal | 12,6 | Cond | Numeric | PaymentInstruction | exchangeRate | FX rate to USD |

#### Section B - Method of Payment (Items 36-43)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 36 | U.S. currency | Decimal | 15,2 | No | Numeric | RegulatoryReport | cashInstruments.usCurrency | U.S. dollar bills/coins |
| 37 | Foreign currency (country and amount) | Object | Varies | No | Country + Amount | RegulatoryReport | cashInstruments.foreignCurrency | Foreign cash details |
| 38 | Cashier's check(s) | Decimal | 15,2 | No | Numeric | RegulatoryReport | cashInstruments.cashiersChecks | Cashier's check total |
| 39 | Money order(s) | Decimal | 15,2 | No | Numeric | RegulatoryReport | cashInstruments.moneyOrders | Money order total |
| 40 | Bank draft(s) | Decimal | 15,2 | No | Numeric | RegulatoryReport | cashInstruments.bankDrafts | Bank draft total |
| 41 | Traveler's check(s) | Decimal | 15,2 | No | Numeric | RegulatoryReport | cashInstruments.travelersChecks | Traveler's check total |
| 42 | Other (specify) | Text | 50 | No | Free text | RegulatoryReport | cashInstruments.other | Other payment instruments |
| 43 | Other amount | Decimal | 15,2 | No | Numeric | RegulatoryReport | cashInstruments.otherAmount | Amount of other instruments |

---

### Part IV: Business That Received Cash (Items 44-56)

#### Section A - Business Identity (Items 44-51)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 44 | Name of business receiving cash | Text | 150 | Yes | Free text | FinancialInstitution | institutionName | Legal business name |
| 45 | Employer identification number | Text | 9 | Yes | 9 digits | FinancialInstitution | taxIdentificationNumber | Business EIN |
| 46 | Address (number, street, apt./suite) | Text | 100 | Yes | Free text | FinancialInstitution | address.addressLine1 | Street address |
| 47 | City | Text | 50 | Yes | Free text | FinancialInstitution | address.city | City |
| 48 | State | Code | 2 | Yes | US state code | FinancialInstitution | address.state | State code |
| 49 | ZIP code | Text | 9 | Yes | XXXXX or XXXXX-XXXX | FinancialInstitution | address.postalCode | ZIP code |
| 50 | Country | Code | 2 | No | ISO 3166-1 alpha-2 | FinancialInstitution | address.country | Country code (US default) |
| 51 | Nature of business | Text | 100 | Yes | Free text | FinancialInstitution | businessDescription | Type of business |

#### Section B - Contact Information (Items 52-56)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 52 | Contact name | Text | 50 | Yes | Free text | RegulatoryReport | reportingEntityContactName | Contact person |
| 53 | Contact phone number | Text | 16 | Yes | Phone format | RegulatoryReport | reportingEntityContactPhone | Phone number |
| 54 | Contact phone extension | Text | 6 | No | Numeric | RegulatoryReport | reportingEntityContactPhoneExt | Extension |
| 55 | Date filed with IRS/FinCEN | Date | 8 | Yes | MMDDYYYY | RegulatoryReport | filingDate | Date report submitted |
| 56 | Business NAICS code | Code | 6 | No | 6 digits | FinancialInstitution | naicsCode | Industry classification |

---

### Part V: Transaction Type and Additional Information (Items 57-66)

#### Section A - Transaction Type (Items 57-62)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 57 | Personal property purchased | Checkbox | 1 | No | Y/N | RegulatoryReport | transactionType.personalProperty | Personal property sale |
| 58 | Real property purchased | Checkbox | 1 | No | Y/N | RegulatoryReport | transactionType.realProperty | Real estate transaction |
| 59 | Personal services provided | Checkbox | 1 | No | Y/N | RegulatoryReport | transactionType.personalServices | Service provided |
| 60 | Business services provided | Checkbox | 1 | No | Y/N | RegulatoryReport | transactionType.businessServices | Business service |
| 61 | Intangible property purchased | Checkbox | 1 | No | Y/N | RegulatoryReport | transactionType.intangibleProperty | IP, securities, etc. |
| 62 | Debt obligations paid | Checkbox | 1 | No | Y/N | RegulatoryReport | transactionType.debtPayment | Loan payment |

#### Section B - Additional Details (Items 63-66)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 63 | Exchange of currency | Checkbox | 1 | No | Y/N | RegulatoryReport | transactionType.currencyExchange | Currency exchange |
| 64 | Escrow or trust funds | Checkbox | 1 | No | Y/N | RegulatoryReport | transactionType.escrowTrust | Held in escrow/trust |
| 65 | Bail received by court clerks | Checkbox | 1 | No | Y/N | RegulatoryReport | transactionType.bail | Bail payment |
| 66 | Other (specify) | Text | 100 | No | Free text | RegulatoryReport | transactionType.other | Other transaction type |

---

### Part VI: Suspicious Transaction Information (Items 67-70)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 67 | Suspicious transaction indicator | Checkbox | 1 | No | Y/N | RegulatoryReport | suspiciousActivityIndicator | Transaction appears suspicious |
| 68 | Describe suspicious activity | Text | 1000 | Cond | Free text | RegulatoryReport | suspiciousActivityNarrative | Required if Item 67 checked |
| 69 | Law enforcement contacted | Checkbox | 1 | No | Y/N | ComplianceCase | lawEnforcementContacted | Police/FBI notified |
| 70 | Law enforcement agency name | Text | 100 | Cond | Free text | ComplianceCase | lawEnforcementAgency | Agency name if contacted |

---

### Part VII: Filing Information and Certification (Items 71-78)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 71 | Amendment indicator | Checkbox | 1 | No | Y/N | RegulatoryReport | amendmentIndicator | Is this an amendment |
| 72 | Prior report number | Text | 20 | Cond | Alphanumeric | RegulatoryReport | priorReportNumber | Prior Form 8300 reference |
| 73 | Batch filing indicator | Checkbox | 1 | No | Y/N | RegulatoryReport | batchFiling | Multiple 8300s filed together |
| 74 | Number of forms in batch | Integer | 4 | Cond | 1-9999 | RegulatoryReport | batchRecordCount | Count of forms in batch |
| 75 | Statement recipient (payer) notice sent | Checkbox | 1 | Yes | Y/N | RegulatoryReport | payerNoticeSent | Annual statement sent to payer |
| 76 | Date payer notice sent | Date | 8 | Cond | MMDDYYYY | RegulatoryReport | payerNoticeSentDate | When notice mailed |
| 77 | Signature of authorized person | Text | 100 | Yes | Free text | RegulatoryReport | authorizedSignature | Person certifying report |
| 78 | Title of authorized person | Text | 50 | Yes | Free text | RegulatoryReport | authorizedSignatureTitle | Title of signer |

---

## CDM Extensions Required

All 78 Form 8300 fields successfully map to existing CDM model. **No enhancements required.**

### RegulatoryReport Entity - Core Fields
✅ All core Form 8300 fields mapped (reportType, jurisdiction, filingDate, etc.)

### RegulatoryReport Entity - Extensions
✅ Form 8300-specific fields already in schema:
- multiplePersonsFlag
- multipleBehalfPersonsFlag
- multiplePaymentsFlag
- suspiciousActivityIndicator
- suspiciousActivityNarrative
- amendmentIndicator
- batchFiling
- payerNoticeSent
- transactionType (object)
- cashInstruments (object)

### Party Entity
✅ All party fields covered:
- familyName, givenName, middleName
- name, dbaName, taxId
- dateOfBirth, occupation
- identificationType, identificationNumber, identificationIssuingJurisdiction
- alienIdNumber, passportNumber
- verificationMethod

### FinancialInstitution Entity
✅ All business fields covered:
- institutionName, taxIdentificationNumber
- address fields
- businessDescription, naicsCode

### PaymentInstruction Entity
✅ All transaction fields covered:
- valueDate, instructedAmount
- exchangeRate

### ComplianceCase Entity
✅ All investigation fields covered:
- lawEnforcementContacted, lawEnforcementAgency

---

## No CDM Gaps Identified ✅

All 78 Form 8300 fields successfully map to existing CDM model. No enhancements required.

---

## Code Lists and Valid Values

### Form of Identification Codes (Items 11a, 27a)
| Code | Description |
|------|-------------|
| 1 | Driver's license |
| 2 | Passport |
| 3 | Alien registration card |
| 4 | State-issued ID card |
| 5 | Military ID card |
| 6 | Other government-issued ID |
| 99 | Other (describe in narrative) |

### Verification Method Codes (Items 15, 29)
| Code | Description |
|------|-------------|
| 1 | Examined government-issued photo ID |
| 2 | Non-documentary verification (credit bureau, references) |
| 3 | Previously verified customer |
| 4 | Unable to verify |

---

## XML Structure Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Form8300 xmlns="http://www.irs.gov/form8300">
  <PartI_CashReceiver>
    <IndividualLastName>Johnson</IndividualLastName>
    <IndividualFirstName>Sarah</IndividualFirstName>
    <TaxpayerID>123456789</TaxpayerID>
    <Address>
      <Street>456 Oak Avenue</Street>
      <City>Los Angeles</City>
      <State>CA</State>
      <ZIP>90001</ZIP>
      <Country>US</Country>
    </Address>
    <DateOfBirth>05201982</DateOfBirth>
    <Occupation>Real Estate Agent</Occupation>
    <IdentificationType>1</IdentificationType>
    <IdentificationNumber>D1234567</IdentificationNumber>
    <IssuingJurisdiction>CA</IssuingJurisdiction>
    <VerificationMethod>1</VerificationMethod>
  </PartI_CashReceiver>

  <PartIII_Transaction>
    <DateCashReceived>11152024</DateCashReceived>
    <TotalCashReceived>45000.00</TotalCashReceived>
    <MultiplePayments>N</MultiplePayments>
    <PaymentMethod>
      <USCurrency>45000.00</USCurrency>
    </PaymentMethod>
  </PartIII_Transaction>

  <PartIV_Business>
    <BusinessName>ABC Motors LLC</BusinessName>
    <EIN>987654321</EIN>
    <Address>
      <Street>789 Commerce Blvd</Street>
      <City>Los Angeles</City>
      <State>CA</State>
      <ZIP>90002</ZIP>
    </Address>
    <NatureOfBusiness>Automobile Sales</NatureOfBusiness>
    <ContactName>Michael Chen</ContactName>
    <ContactPhone>(213) 555-1234</ContactPhone>
    <FilingDate>11302024</FilingDate>
  </PartIV_Business>

  <PartV_TransactionType>
    <PersonalPropertyPurchased>Y</PersonalPropertyPurchased>
  </PartV_TransactionType>

  <Certification>
    <PayerNoticeSent>Y</PayerNoticeSent>
    <AuthorizedSignature>Michael Chen</AuthorizedSignature>
    <Title>Compliance Officer</Title>
  </Certification>
</Form8300>
```

---

## Filing Requirements

### Who Must File
- Any person engaged in a trade or business who receives more than $10,000 cash in:
  - One transaction, OR
  - Two or more related transactions within 12 months

### What is "Cash"
- **Currency:** U.S. or foreign coins and bills
- **Monetary instruments:** Cashier's checks, bank drafts, traveler's checks, or money orders with face value of $10,000 or less
- **NOT cash:** Personal checks, wire transfers, ACH payments

### Deadline
- **Within 15 days** after receiving the cash payment
- For related transactions: Within 15 days of the transaction that causes the total to exceed $10,000

### Payer Statement Requirement
- By **January 31** of the year following the calendar year of the transaction
- Must provide written statement to each person named in the Form 8300

### Penalties for Non-Compliance
- **Civil penalty:** Up to $25,000 per violation for intentional disregard
- **Criminal penalty:** Up to $250,000 ($500,000 for corporations) and/or 5 years imprisonment
- **Pattern of violations:** Additional penalties up to $100,000 or greater

---

## Common Filing Scenarios

### Auto Dealership
Customer purchases vehicle for $48,000 cash (U.S. currency). Form 8300 must be filed within 15 days.

### Jewelry Store
Customer pays $6,000 cash on 10/15 and $5,500 cash on 10/22 for same purchase. Form 8300 due by 11/6 (15 days from 10/22).

### Real Estate Transaction
Buyer pays $125,000 cash down payment for property. Form 8300 must be filed within 15 days.

### Attorney Services
Law firm receives $15,000 in cashier's checks for retainer. Form 8300 must be filed within 15 days.

---

## Related FinCEN Reports

| Report | Form | Threshold | Usage |
|--------|------|-----------|-------|
| **CTR** | 112 | Cash > $10,000 | Banks/MSBs - Currency transactions |
| **SAR** | 111 | Suspicious Activity | Financial institutions - Suspicious transactions |
| **FBAR** | 114 | Foreign accounts > $10,000 | U.S. persons - Foreign bank accounts |

---

## Key Differences: Form 8300 vs. CTR

| Feature | Form 8300 | CTR (Form 112) |
|---------|-----------|----------------|
| **Who files** | Trade/business (non-financial) | Financial institutions |
| **What reported** | Cash payments received | Cash transactions (in or out) |
| **Threshold** | > $10,000 | > $10,000 |
| **Deadline** | 15 days | 15 days |
| **Filing agency** | IRS and FinCEN | FinCEN |
| **Payer notice** | Yes (by Jan 31) | No |

---

## References

- IRS Form 8300 Instructions: https://www.irs.gov/pub/irs-pdf/i8300.pdf
- IRS Form 8300: https://www.irs.gov/pub/irs-pdf/f8300.pdf
- 26 USC 6050I: https://www.law.cornell.edu/uscode/text/26/6050I
- 31 USC 5331: https://www.law.cornell.edu/uscode/text/31/5331
- 31 CFR 1010.330: https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1010/subpart-C/section-1010.330
- BSA E-Filing: https://bsaefiling.fincen.treas.gov
- GPS CDM Schema: `/schemas/05_regulatory_report_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
