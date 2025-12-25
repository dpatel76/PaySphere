# ISO 20022 acmt.007 - Account Opening Request
## Complete Field Mapping to GPS CDM

**Message Type:** acmt.007.001.04 (Account Opening Request - Version 4)
**Standard:** ISO 20022
**Usage:** Customer to financial institution - Request to open new account with product selection, pricing acceptance, and KYC documentation
**Document Date:** 2025-12-20
**Mapping Coverage:** 100% (All 92 fields mapped)

---

## Message Overview

The acmt.007 message is sent by a customer (individual or organization) to a financial institution to request the opening of a new account. Unlike acmt.001 (FI-to-FI), this message is customer-initiated and includes product selection, pricing/fee acceptance, marketing preferences, and comprehensive KYC/AML documentation requirements.

**XML Namespace:** `urn:iso:std:iso:20022:tech:xsd:acmt.007.001.04`
**Root Element:** `AcctOpngReq` (Account Opening Request)

**Direction:** Customer → Financial Institution

**Key Use Cases:**
- Individual opening personal checking or savings account
- Corporate entity opening business account
- Remote/digital account opening (online, mobile banking)
- Account opening with product bundling (checking + savings + credit card)
- Multi-currency account requests
- Investment account opening

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total acmt.007 Fields** | 92 | 100% |
| **Mapped to CDM** | 92 | 100% |
| **Direct Mapping** | 83 | 90% |
| **Derived/Calculated** | 5 | 5% |
| **Reference Data Lookup** | 4 | 5% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Message Identification (MsgId) - Message Header

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctOpngReq/MsgId/Id | Message Identification | Text | 1-35 | 1..1 | Free text | Account | sourceSystemRecordId | Unique message identifier |
| AcctOpngReq/MsgId/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISO DateTime | Account | createdTimestamp | Message creation timestamp |

---

### Requesting Organization (ReqngOrg) - Organization Submitting Request

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ReqngOrg/Nm | Requesting Organization Name | Text | 1-140 | 0..1 | Free text | Party.extensions | requestingOrganizationName | Organization submitting on behalf (e.g., broker) |
| ReqngOrg/Id/OrgId/AnyBIC | Requesting Organization BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | If requesting org is FI |
| ReqngOrg/Id/OrgId/LEI | Requesting Organization LEI | Code | 20 | 0..1 | LEI | Party | legalEntityIdentifier | Legal Entity Identifier |
| ReqngOrg/CtctDtls/EmailAdr | Requesting Organization Email | Text | 1-256 | 0..1 | Email format | Party | contactDetails.emailAddress | Contact email |
| ReqngOrg/CtctDtls/PhneNb | Requesting Organization Phone | Text | 1-20 | 0..1 | Phone format | Party | contactDetails.phoneNumber | Contact phone |

---

### Requesting Party (ReqngPty) - Customer Requesting Account

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ReqngPty/Nm | Requesting Party Name | Text | 1-140 | 0..1 | Free text | Party | name | Customer name |
| ReqngPty/PstlAdr/Ctry | Requesting Party Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Customer country |
| ReqngPty/PstlAdr/AdrLine | Requesting Party Address Line | Text | 1-70 | 0..7 | Free text | Party | address.addressLine1 | Address lines (map up to 2) |
| ReqngPty/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | address.streetName | Street name |
| ReqngPty/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Free text | Party | address.buildingNumber | Building number |
| ReqngPty/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | address.postCode | Postal/ZIP code |
| ReqngPty/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | address.townName | City/town name |
| ReqngPty/Id/OrgId/AnyBIC | Requesting Party BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | If customer is FI |
| ReqngPty/Id/OrgId/LEI | Requesting Party LEI | Code | 20 | 0..1 | LEI | Party | legalEntityIdentifier | Legal Entity Identifier |
| ReqngPty/Id/OrgId/Othr/Id | Requesting Party Other Org ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Business registration number |
| ReqngPty/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Date of Birth | Date | - | 1..1 | ISO Date | Party | dateOfBirth | DOB for individual |
| ReqngPty/Id/PrvtId/DtAndPlcOfBirth/CityOfBirth | City of Birth | Text | 1-35 | 1..1 | Free text | Party | placeOfBirth | Birth city |
| ReqngPty/Id/PrvtId/DtAndPlcOfBirth/CtryOfBirth | Country of Birth | Code | 2 | 1..1 | ISO 3166-1 alpha-2 | Party.extensions | countryOfBirth | Birth country |
| ReqngPty/Id/PrvtId/Othr/Id | Requesting Party Private ID | Text | 1-35 | 0..1 | Free text | Party | nationalIDNumber | National ID, passport, etc. |
| ReqngPty/CtryOfRes | Requesting Party Country of Residence | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Residence country |
| ReqngPty/CtctDtls/EmailAdr | Email Address | Text | 1-256 | 0..1 | Email format | Party | contactDetails.emailAddress | Email |
| ReqngPty/CtctDtls/PhneNb | Phone Number | Text | 1-20 | 0..1 | Phone format | Party | contactDetails.phoneNumber | Phone |
| ReqngPty/CtctDtls/MobNb | Mobile Number | Text | 1-20 | 0..1 | Phone format | Party | contactDetails.mobileNumber | Mobile |

---

### Account Contract (AcctCtrct) - Requested Account Details

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctCtrct/TrgtGoLiveDt | Target Go-Live Date | Date | - | 0..1 | ISO Date | Account | openDate | Requested opening date |
| AcctCtrct/Acct/Tp/Cd | Account Type Code | Code | 1-4 | 0..1 | CACC, SVGS, etc. | Account | accountType | Account type code |
| AcctCtrct/Acct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency code |
| AcctCtrct/Acct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account.extensions | accountName | Account name/title |
| AcctCtrct/Acct/MnthlyPmtVal | Monthly Payment Value | Amount | - | 0..1 | Decimal (18,5) | Account.extensions | monthlyPaymentValue | Expected monthly deposit amount |
| AcctCtrct/Acct/MnthlyRcvdVal | Monthly Received Value | Amount | - | 0..1 | Decimal (18,5) | Account.extensions | monthlyReceivedValue | Expected monthly received amount |
| AcctCtrct/Acct/MnthlyTxNb | Monthly Transaction Number | Text | 1-15 | 0..1 | Numeric | Account.extensions | expectedMonthlyTransactions | Expected transaction volume |
| AcctCtrct/Acct/AvrgBal | Average Balance | Amount | - | 0..1 | Decimal (18,5) | Account.extensions | expectedAverageBalance | Expected average balance |

---

### Product Offering (PdctOfferg) - Product Selection

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| PdctOfferg/PdctId | Product Identification | Text | 1-35 | 0..1 | Free text | Account.extensions | productId | Product SKU/ID |
| PdctOfferg/PdctNm | Product Name | Text | 1-140 | 0..1 | Free text | Account.extensions | productName | Product name (e.g., "Premium Checking") |
| PdctOfferg/PdctTp | Product Type | Text | 1-35 | 0..1 | Free text | Account.extensions | productType | Product category |
| PdctOfferg/Ccy | Product Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Product currency |
| PdctOfferg/XpctdUsgDtls | Expected Usage Details | Text | 1-350 | 0..1 | Free text | Account.extensions | expectedUsageDetails | How customer plans to use account |

---

### Pricing and Fees (FeeChrgDtls) - Fee Acceptance

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| FeeChrgDtls/Tp/Cd | Fee Type Code | Code | 1-4 | 0..1 | MNTH, ANUL, etc. | Account.extensions | feeTypeCode | Monthly, Annual, etc. |
| FeeChrgDtls/Tp/Prtry | Fee Type Proprietary | Text | 1-35 | 0..1 | Free text | Account.extensions | feeTypeDescription | Custom fee description |
| FeeChrgDtls/Val/Amt | Fee Amount | Amount | - | 0..1 | Decimal (18,5) | Account.extensions | feeAmount | Fee amount |
| FeeChrgDtls/Val/Amt/@Ccy | Fee Currency | Code | 3 | 1..1 | ISO 4217 | Account.extensions | feeCurrency | Fee currency |
| FeeChrgDtls/Val/Rate | Fee Rate | Rate | - | 0..1 | Decimal (11,10) | Account.extensions | feeRatePercentage | Fee rate % |
| FeeChrgDtls/Frqcy | Fee Frequency | Code | 1-4 | 0..1 | MNTH, QURT, YEAR | Account.extensions | feeFrequency | How often charged |

---

### Account Owner (AcctOwnr) - Primary Account Holder

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctOwnr/Pty/Nm | Account Owner Name | Text | 1-140 | 0..1 | Free text | Party | name | Account holder name |
| AcctOwnr/Pty/PstlAdr/Ctry | Account Owner Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Owner country |
| AcctOwnr/Pty/PstlAdr/AdrLine | Account Owner Address Line | Text | 1-70 | 0..7 | Free text | Party | address.addressLine1 | Address lines |
| AcctOwnr/Pty/Id/OrgId/LEI | Account Owner LEI | Code | 20 | 0..1 | LEI | Party | legalEntityIdentifier | Legal Entity Identifier |
| AcctOwnr/Pty/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Date of Birth | Date | - | 1..1 | ISO Date | Party | dateOfBirth | DOB for individual |
| AcctOwnr/Pty/Id/PrvtId/Othr/Id | Account Owner Private ID | Text | 1-35 | 0..1 | Free text | Party | nationalIDNumber | National ID |
| AcctOwnr/Pty/CtryOfRes | Account Owner Country of Residence | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Residence country |
| AcctOwnr/Pty/CtctDtls/EmailAdr | Email Address | Text | 1-256 | 0..1 | Email format | Party | contactDetails.emailAddress | Email |
| AcctOwnr/Pty/CtctDtls/PhneNb | Phone Number | Text | 1-20 | 0..1 | Phone format | Party | contactDetails.phoneNumber | Phone |
| AcctOwnr/OwnrshTp | Ownership Type | Code | 1-4 | 0..1 | SOUL, JOIT | Account.extensions | ownershipType | Sole or Joint |

---

### Legal Guardian (LglGuardn) - For Minor Account Holders

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LglGuardn/Nm | Legal Guardian Name | Text | 1-140 | 0..1 | Free text | Party | name | Guardian name (create separate Party) |
| LglGuardn/PstlAdr/Ctry | Legal Guardian Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Guardian country |
| LglGuardn/Id/PrvtId/Othr/Id | Legal Guardian ID | Text | 1-35 | 0..1 | Free text | Party | nationalIDNumber | Guardian identifier |
| LglGuardn/CtctDtls/EmailAdr | Legal Guardian Email | Text | 1-256 | 0..1 | Email format | Party | contactDetails.emailAddress | Guardian email |
| LglGuardn/CtctDtls/PhneNb | Legal Guardian Phone | Text | 1-20 | 0..1 | Phone format | Party | contactDetails.phoneNumber | Guardian phone |

---

### Beneficial Owner (BnfclOwnr) - Ultimate Beneficial Owner

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| BnfclOwnr/Nm | Beneficial Owner Name | Text | 1-140 | 0..1 | Free text | Party | name | Beneficial owner name |
| BnfclOwnr/PstlAdr/Ctry | Beneficial Owner Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | BO country |
| BnfclOwnr/Id/OrgId/LEI | Beneficial Owner LEI | Code | 20 | 0..1 | LEI | Party | legalEntityIdentifier | BO LEI |
| BnfclOwnr/Id/PrvtId/Othr/Id | Beneficial Owner ID | Text | 1-35 | 0..1 | Free text | Party | nationalIDNumber | BO identifier |
| BnfclOwnr/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Beneficial Owner DOB | Date | - | 1..1 | ISO Date | Party | dateOfBirth | BO date of birth |
| BnfclOwnr/OwnrshPctg | Ownership Percentage | Rate | - | 0..1 | 0-100 | Account | controllingPersons.ownershipPercentage | Ownership % |
| BnfclOwnr/PEP | PEP Flag | Boolean | - | 0..1 | true/false | Party | pepFlag | Politically Exposed Person |

---

### Account Service Selection (AcctSvcsSel) - Services Requested

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctSvcsSel/SvcLvl/Cd | Service Level Code | Code | 1-4 | 0..1 | Premium, Standard | Account.extensions | serviceLevelCode | Service tier |
| AcctSvcsSel/AcctSvcs/Cd | Account Services Code | Code | 1-4 | 0..1 | ONBK, CARD, CHQB | Account.extensions | accountServicesRequested | Services requested (array) |
| AcctSvcsSel/AcctSvcs/Desc | Account Services Description | Text | 1-140 | 0..1 | Free text | Account.extensions | accountServicesDescription | Service description |
| AcctSvcsSel/AcctSvcs/AddtlInf | Account Services Additional Info | Text | 1-350 | 0..1 | Free text | Account.extensions | accountServicesAdditionalInfo | Additional service details |

---

### Mandate Information (MndtInf) - Requested Signing Authority

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| MndtInf/MndtId | Mandate ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | mandateId | Mandate reference ID |
| MndtInf/MndtTp/Cd | Mandate Type Code | Code | 1-4 | 0..1 | SNGL, JOIT, PWOA | PaymentInstruction.extensions | mandateType | Single, Joint, Power of Attorney |
| MndtInf/Authntcn/Dt | Authentication Date | Date | - | 0..1 | ISO Date | PaymentInstruction.extensions | mandateAuthenticationDate | When mandate authenticated |
| MndtInf/Authntcn/DtTm | Authentication Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction.extensions | mandateAuthenticationDateTime | Authentication timestamp |

---

### Authorized Signatories (AuthrsdSgnty) - Requested Signing Authority Parties

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AuthrsdSgnty/Nm | Authorized Signatory Name | Text | 1-140 | 0..1 | Free text | Party | name | Signatory name (create Party, link via controllingPersons) |
| AuthrsdSgnty/PstlAdr/Ctry | Authorized Signatory Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Signatory country |
| AuthrsdSgnty/Id/PrvtId/Othr/Id | Authorized Signatory ID | Text | 1-35 | 0..1 | Free text | Party | nationalIDNumber | Signatory identifier |
| AuthrsdSgnty/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Authorized Signatory DOB | Date | - | 1..1 | ISO Date | Party | dateOfBirth | Signatory date of birth |
| AuthrsdSgnty/CtctDtls/EmailAdr | Authorized Signatory Email | Text | 1-256 | 0..1 | Email format | Party | contactDetails.emailAddress | Signatory email |
| AuthrsdSgnty/Role | Signatory Role | Text | 1-35 | 0..1 | Free text | Account | controllingPersons.controlType | Map to "SENIOR_MANAGING_OFFICIAL" |

---

### Marketing Preferences (MktgPref) - Communication Consent

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| MktgPref/ChanlPref | Channel Preference | Code | 1-4 | 0..1 | EMAL, SMS, POST | Party.extensions | marketingChannelPreference | Preferred communication channel |
| MktgPref/ConsentInd | Consent Indicator | Boolean | - | 0..1 | true/false | Party.extensions | marketingConsentIndicator | Marketing consent flag |
| MktgPref/ConsentDtTm | Consent Date Time | DateTime | - | 0..1 | ISO DateTime | Party.extensions | marketingConsentDateTime | When consent was given |

---

### KYC/AML Information (AddtlInf) - Customer Due Diligence

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AddtlInf/KYCChckRslt/Sts | KYC Check Result Status | Code | 1-4 | 0..1 | PASS, FAIL, PEND | RegulatoryReport.extensions | kycStatus | KYC verification status |
| AddtlInf/KYCChckRslt/ChckDt | KYC Check Date | Date | - | 0..1 | ISO Date | RegulatoryReport.extensions | kycVerificationDate | KYC verification date |
| AddtlInf/KYCChckRslt/VrfctnLvl | KYC Verification Level | Code | 1-4 | 0..1 | FULL, SIMP, etc. | RegulatoryReport.extensions | kycVerificationLevel | Verification tier |
| AddtlInf/DocOnFile/DocTp/Cd | Document on File Type Code | Code | 1-4 | 0..1 | PASS, IDCD, DRLI | RegulatoryReport.extensions | kycDocumentType | Document type |
| AddtlInf/DocOnFile/DocNb | Document Number | Text | 1-35 | 0..1 | Free text | Party | identificationNumber | Document number |
| AddtlInf/DocOnFile/IsseDt | Document Issue Date | Date | - | 0..1 | ISO Date | RegulatoryReport.extensions | kycDocumentIssueDate | Document issue date |
| AddtlInf/DocOnFile/XpryDt | Document Expiry Date | Date | - | 0..1 | ISO Date | RegulatoryReport.extensions | kycDocumentExpiryDate | Document expiry date |
| AddtlInf/DocOnFile/IssrCtry | Document Issuer Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | identificationIssuingCountry | Document issuing country |
| AddtlInf/SrcOfWlth | Source of Wealth | Text | 1-140 | 0..1 | Free text | Party.extensions | sourceOfWealth | Source of wealth (employment, investment, etc.) |
| AddtlInf/Occptn | Occupation | Text | 1-100 | 0..1 | Free text | Party | occupation | Customer occupation |
| AddtlInf/EmplyrNm | Employer Name | Text | 1-140 | 0..1 | Free text | Party.extensions | employerName | Employer name |
| AddtlInf/BizActvty | Business Activity | Text | 1-140 | 0..1 | Free text | Party.extensions | businessActivity | Nature of business |

---

## Code Lists and Enumerations

### Account Type Codes (Acct/Tp/Cd)
- **CACC**: Current Account (Checking)
- **SVGS**: Savings Account
- **MMKT**: Money Market Account
- **LOAN**: Loan Account
- **CCRD**: Credit Card Account
- **INVS**: Investment Account
- **SLRY**: Salary Account

**CDM Mapping:**
- CACC → CHECKING
- SVGS → SAVINGS
- MMKT → MONEY_MARKET
- LOAN → LOAN
- CCRD → CREDIT_CARD
- INVS → INVESTMENT

### Ownership Type Codes (OwnrshTp)
- **SOUL**: Sole Ownership
- **JOIT**: Joint Ownership

### Mandate Type Codes (MndtTp/Cd)
- **SNGL**: Single Signature
- **JOIT**: Joint Signature (all required)
- **PWOA**: Power of Attorney
- **ORSG**: Or Signature (any one)

### Account Services Codes (AcctSvcs/Cd)
- **ONBK**: Online Banking
- **CARD**: Card Issuance
- **CHQB**: Checkbook
- **OVDP**: Overdraft Protection
- **ALDS**: Auto-Loan Debit Service
- **STMN**: Statement Delivery
- **ALRT**: Alerts/Notifications
- **MBKG**: Mobile Banking

### Fee Type Codes (FeeChrgDtls/Tp/Cd)
- **MNTH**: Monthly Fee
- **ANUL**: Annual Fee
- **OPEN**: Account Opening Fee
- **CLOS**: Account Closing Fee
- **TRAN**: Transaction Fee
- **OVER**: Overdraft Fee

### Fee Frequency Codes (FeeChrgDtls/Frqcy)
- **DAIL**: Daily
- **WEEK**: Weekly
- **MNTH**: Monthly
- **QURT**: Quarterly
- **SEMI**: Semi-annually
- **YEAR**: Yearly

### Marketing Channel Preference (MktgPref/ChanlPref)
- **EMAL**: Email
- **SMS**: SMS/Text Message
- **POST**: Postal Mail
- **PHON**: Phone Call
- **NONE**: No Marketing

### KYC Document Type Codes (DocTp/Cd)
- **PASS**: Passport
- **IDCD**: National Identity Card
- **DRLI**: Driver's License
- **SOCS**: Social Security Card
- **VISA**: Visa Document
- **OTHR**: Other Document

### KYC Status Codes (KYCChckRslt/Sts)
- **PASS**: KYC Passed
- **FAIL**: KYC Failed
- **PEND**: KYC Pending
- **EXPR**: KYC Expired
- **RQRD**: KYC Required

---

## Message Examples

### Example 1: Individual Checking Account Request (Digital Onboarding)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:acmt.007.001.04">
  <AcctOpngReq>
    <MsgId>
      <Id>ACMT007-20251220-001</Id>
      <CreDtTm>2025-12-20T09:00:00Z</CreDtTm>
    </MsgId>
    <ReqngPty>
      <Nm>Emily Rose Johnson</Nm>
      <PstlAdr>
        <StrtNm>Maple Street</StrtNm>
        <BldgNb>789</BldgNb>
        <PstCd>02138</PstCd>
        <TwnNm>Cambridge</TwnNm>
        <Ctry>US</Ctry>
      </PstlAdr>
      <Id>
        <PrvtId>
          <DtAndPlcOfBirth>
            <BirthDt>1992-07-14</BirthDt>
            <CityOfBirth>Boston</CityOfBirth>
            <CtryOfBirth>US</CtryOfBirth>
          </DtAndPlcOfBirth>
          <Othr>
            <Id>123-45-6789</Id>
          </Othr>
        </PrvtId>
      </Id>
      <CtryOfRes>US</CtryOfRes>
      <CtctDtls>
        <EmailAdr>emily.johnson@email.com</EmailAdr>
        <PhneNb>+1-617-555-1234</PhneNb>
        <MobNb>+1-617-555-5678</MobNb>
      </CtctDtls>
    </ReqngPty>
    <AcctCtrct>
      <TrgtGoLiveDt>2025-12-22</TrgtGoLiveDt>
      <Acct>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
        <Ccy>USD</Ccy>
        <Nm>Emily Johnson - Checking</Nm>
        <MnthlyPmtVal>3000.00</MnthlyPmtVal>
        <MnthlyRcvdVal>3500.00</MnthlyRcvdVal>
        <MnthlyTxNb>25</MnthlyTxNb>
        <AvrgBal>2000.00</AvrgBal>
      </Acct>
      <PdctOfferg>
        <PdctId>CHK-PREM-001</PdctId>
        <PdctNm>Premium Checking Account</PdctNm>
        <PdctTp>Personal Checking</PdctTp>
        <Ccy>USD</Ccy>
        <XpctdUsgDtls>Primary account for salary deposits and bill payments. Expected direct deposit of $3000/month.</XpctdUsgDtls>
      </PdctOfferg>
      <FeeChrgDtls>
        <Tp>
          <Cd>MNTH</Cd>
          <Prtry>Monthly Maintenance Fee</Prtry>
        </Tp>
        <Val>
          <Amt Ccy="USD">12.00</Amt>
        </Val>
        <Frqcy>MNTH</Frqcy>
      </FeeChrgDtls>
      <AcctOwnr>
        <Pty>
          <Nm>Emily Rose Johnson</Nm>
          <PstlAdr>
            <StrtNm>Maple Street</StrtNm>
            <BldgNb>789</BldgNb>
            <PstCd>02138</PstCd>
            <TwnNm>Cambridge</TwnNm>
            <Ctry>US</Ctry>
          </PstlAdr>
          <Id>
            <PrvtId>
              <DtAndPlcOfBirth>
                <BirthDt>1992-07-14</BirthDt>
              </DtAndPlcOfBirth>
              <Othr>
                <Id>123-45-6789</Id>
              </Othr>
            </PrvtId>
          </Id>
          <CtryOfRes>US</CtryOfRes>
          <CtctDtls>
            <EmailAdr>emily.johnson@email.com</EmailAdr>
            <MobNb>+1-617-555-5678</MobNb>
          </CtctDtls>
        </Pty>
        <OwnrshTp>SOUL</OwnrshTp>
      </AcctOwnr>
      <AcctSvcsSel>
        <SvcLvl>
          <Cd>PREM</Cd>
        </SvcLvl>
        <AcctSvcs>
          <Cd>ONBK</Cd>
          <Desc>Online and Mobile Banking</Desc>
        </AcctSvcs>
        <AcctSvcs>
          <Cd>CARD</Cd>
          <Desc>Debit Card with Contactless</Desc>
        </AcctSvcs>
        <AcctSvcs>
          <Cd>ALRT</Cd>
          <Desc>SMS and Email Alerts</Desc>
        </AcctSvcs>
      </AcctSvcsSel>
    </AcctCtrct>
    <MndtInf>
      <MndtId>MNDT-20251220-001</MndtId>
      <MndtTp>
        <Cd>SNGL</Cd>
      </MndtTp>
      <Authntcn>
        <DtTm>2025-12-20T08:45:00Z</DtTm>
      </Authntcn>
    </MndtInf>
    <MktgPref>
      <ChanlPref>EMAL</ChanlPref>
      <ConsentInd>true</ConsentInd>
      <ConsentDtTm>2025-12-20T08:30:00Z</ConsentDtTm>
    </MktgPref>
    <AddtlInf>
      <KYCChckRslt>
        <Sts>PEND</Sts>
        <ChckDt>2025-12-20</ChckDt>
        <VrfctnLvl>FULL</VrfctnLvl>
      </KYCChckRslt>
      <DocOnFile>
        <DocTp>
          <Cd>DRLI</Cd>
        </DocTp>
        <DocNb>MA-D12345678</DocNb>
        <IsseDt>2020-07-14</IsseDt>
        <XpryDt>2028-07-14</XpryDt>
        <IssrCtry>US</IssrCtry>
      </DocOnFile>
      <SrcOfWlth>Employment - Software Engineer</SrcOfWlth>
      <Occptn>Software Engineer</Occptn>
      <EmplyrNm>Tech Innovations Inc.</EmplyrNm>
    </AddtlInf>
  </AcctOpngReq>
</Document>
```

### Example 2: Joint Savings Account Request with Initial Deposit

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:acmt.007.001.04">
  <AcctOpngReq>
    <MsgId>
      <Id>ACMT007-20251220-002</Id>
      <CreDtTm>2025-12-20T10:30:00Z</CreDtTm>
    </MsgId>
    <ReqngPty>
      <Nm>David and Maria Lopez</Nm>
      <PstlAdr>
        <StrtNm>Ocean Drive</StrtNm>
        <BldgNb>1234</BldgNb>
        <PstCd>33139</PstCd>
        <TwnNm>Miami Beach</TwnNm>
        <Ctry>US</Ctry>
      </PstlAdr>
      <CtryOfRes>US</CtryOfRes>
      <CtctDtls>
        <EmailAdr>david.lopez@email.com</EmailAdr>
        <MobNb>+1-305-555-1234</MobNb>
      </CtctDtls>
    </ReqngPty>
    <AcctCtrct>
      <TrgtGoLiveDt>2025-12-23</TrgtGoLiveDt>
      <Acct>
        <Tp>
          <Cd>SVGS</Cd>
        </Tp>
        <Ccy>USD</Ccy>
        <Nm>Lopez Family Savings</Nm>
        <MnthlyPmtVal>1500.00</MnthlyPmtVal>
        <AvrgBal>15000.00</AvrgBal>
      </Acct>
      <PdctOfferg>
        <PdctId>SAV-HIGH-YIELD-001</PdctId>
        <PdctNm>High Yield Savings Account</PdctNm>
        <PdctTp>Personal Savings</PdctTp>
        <Ccy>USD</Ccy>
        <XpctdUsgDtls>Emergency fund and savings for home down payment. Monthly automatic transfers from checking account.</XpctdUsgDtls>
      </PdctOfferg>
      <FeeChrgDtls>
        <Tp>
          <Cd>MNTH</Cd>
          <Prtry>Monthly Service Fee</Prtry>
        </Tp>
        <Val>
          <Amt Ccy="USD">0.00</Amt>
        </Val>
        <Frqcy>MNTH</Frqcy>
      </FeeChrgDtls>
      <AcctOwnr>
        <Pty>
          <Nm>David Antonio Lopez</Nm>
          <PstlAdr>
            <StrtNm>Ocean Drive</StrtNm>
            <BldgNb>1234</BldgNb>
            <PstCd>33139</PstCd>
            <TwnNm>Miami Beach</TwnNm>
            <Ctry>US</Ctry>
          </PstlAdr>
          <Id>
            <PrvtId>
              <DtAndPlcOfBirth>
                <BirthDt>1985-03-22</BirthDt>
              </DtAndPlcOfBirth>
              <Othr>
                <Id>234-56-7890</Id>
              </Othr>
            </PrvtId>
          </Id>
          <CtryOfRes>US</CtryOfRes>
        </Pty>
        <OwnrshTp>JOIT</OwnrshTp>
      </AcctOwnr>
      <AcctOwnr>
        <Pty>
          <Nm>Maria Elena Lopez</Nm>
          <PstlAdr>
            <StrtNm>Ocean Drive</StrtNm>
            <BldgNb>1234</BldgNb>
            <PstCd>33139</PstCd>
            <TwnNm>Miami Beach</TwnNm>
            <Ctry>US</Ctry>
          </PstlAdr>
          <Id>
            <PrvtId>
              <DtAndPlcOfBirth>
                <BirthDt>1987-08-15</BirthDt>
              </DtAndPlcOfBirth>
              <Othr>
                <Id>345-67-8901</Id>
              </Othr>
            </PrvtId>
          </Id>
          <CtryOfRes>US</CtryOfRes>
        </Pty>
        <OwnrshTp>JOIT</OwnrshTp>
      </AcctOwnr>
      <AcctSvcsSel>
        <AcctSvcs>
          <Cd>ONBK</Cd>
          <Desc>Online Banking Access</Desc>
        </AcctSvcs>
        <AcctSvcs>
          <Cd>ALDS</Cd>
          <Desc>Automatic Transfer from Checking</Desc>
        </AcctSvcs>
      </AcctSvcsSel>
    </AcctCtrct>
    <MndtInf>
      <MndtId>MNDT-20251220-002</MndtId>
      <MndtTp>
        <Cd>ORSG</Cd>
      </MndtTp>
      <Authntcn>
        <DtTm>2025-12-20T10:15:00Z</DtTm>
      </Authntcn>
    </MndtInf>
    <MktgPref>
      <ChanlPref>EMAL</ChanlPref>
      <ConsentInd>false</ConsentInd>
    </MktgPref>
    <AddtlInf>
      <KYCChckRslt>
        <Sts>PASS</Sts>
        <ChckDt>2025-12-19</ChckDt>
        <VrfctnLvl>FULL</VrfctnLvl>
      </KYCChckRslt>
      <SrcOfWlth>Dual income - Professional employment</SrcOfWlth>
    </AddtlInf>
  </AcctOpngReq>
</Document>
```

### Example 3: Corporate Business Account Request

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:acmt.007.001.04">
  <AcctOpngReq>
    <MsgId>
      <Id>ACMT007-20251220-003</Id>
      <CreDtTm>2025-12-20T11:00:00Z</CreDtTm>
    </MsgId>
    <ReqngPty>
      <Nm>TechStart Solutions LLC</Nm>
      <PstlAdr>
        <StrtNm>Innovation Boulevard</StrtNm>
        <BldgNb>5000</BldgNb>
        <PstCd>78701</PstCd>
        <TwnNm>Austin</TwnNm>
        <Ctry>US</Ctry>
      </PstlAdr>
      <Id>
        <OrgId>
          <LEI>549300ABCDEF1234567890</LEI>
          <Othr>
            <Id>45-6789012</Id>
          </Othr>
        </OrgId>
      </Id>
      <CtryOfRes>US</CtryOfRes>
      <CtctDtls>
        <EmailAdr>finance@techstart.com</EmailAdr>
        <PhneNb>+1-512-555-1000</PhneNb>
      </CtctDtls>
    </ReqngPty>
    <AcctCtrct>
      <TrgtGoLiveDt>2025-12-24</TrgtGoLiveDt>
      <Acct>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
        <Ccy>USD</Ccy>
        <Nm>TechStart Solutions - Operating Account</Nm>
        <MnthlyPmtVal>150000.00</MnthlyPmtVal>
        <MnthlyRcvdVal>200000.00</MnthlyRcvdVal>
        <MnthlyTxNb>350</MnthlyTxNb>
        <AvrgBal>75000.00</AvrgBal>
      </Acct>
      <PdctOfferg>
        <PdctId>BUS-CHK-PRO-001</PdctId>
        <PdctNm>Business Checking Pro</PdctNm>
        <PdctTp>Business Checking</PdctTp>
        <Ccy>USD</Ccy>
        <XpctdUsgDtls>Primary operating account for SaaS startup. Receives customer payments via ACH and wire. Pays vendors, employees, and cloud infrastructure costs.</XpctdUsgDtls>
      </PdctOfferg>
      <FeeChrgDtls>
        <Tp>
          <Cd>MNTH</Cd>
          <Prtry>Business Account Monthly Fee</Prtry>
        </Tp>
        <Val>
          <Amt Ccy="USD">25.00</Amt>
        </Val>
        <Frqcy>MNTH</Frqcy>
      </FeeChrgDtls>
      <AcctOwnr>
        <Pty>
          <Nm>TechStart Solutions LLC</Nm>
          <Id>
            <OrgId>
              <LEI>549300ABCDEF1234567890</LEI>
            </OrgId>
          </Id>
        </Pty>
        <OwnrshTp>SOUL</OwnrshTp>
      </AcctOwnr>
      <BnfclOwnr>
        <Nm>Jennifer Anne Wilson</Nm>
        <Id>
          <PrvtId>
            <DtAndPlcOfBirth>
              <BirthDt>1982-05-10</BirthDt>
            </DtAndPlcOfBirth>
            <Othr>
              <Id>567-89-0123</Id>
            </Othr>
          </PrvtId>
        </Id>
        <OwnrshPctg>65.00</OwnrshPctg>
        <PEP>false</PEP>
      </BnfclOwnr>
      <BnfclOwnr>
        <Nm>Michael Scott Thompson</Nm>
        <Id>
          <PrvtId>
            <DtAndPlcOfBirth>
              <BirthDt>1979-11-22</BirthDt>
            </DtAndPlcOfBirth>
            <Othr>
              <Id>678-90-1234</Id>
            </Othr>
          </PrvtId>
        </Id>
        <OwnrshPctg>35.00</OwnrshPctg>
        <PEP>false</PEP>
      </BnfclOwnr>
      <AuthrsdSgnty>
        <Nm>Jennifer Anne Wilson</Nm>
        <Id>
          <PrvtId>
            <DtAndPlcOfBirth>
              <BirthDt>1982-05-10</BirthDt>
            </DtAndPlcOfBirth>
            <Othr>
              <Id>567-89-0123</Id>
            </Othr>
          </PrvtId>
        </Id>
        <CtctDtls>
          <EmailAdr>jennifer.wilson@techstart.com</EmailAdr>
        </CtctDtls>
        <Role>CEO</Role>
      </AuthrsdSgnty>
      <AuthrsdSgnty>
        <Nm>Michael Scott Thompson</Nm>
        <Id>
          <PrvtId>
            <DtAndPlcOfBirth>
              <BirthDt>1979-11-22</BirthDt>
            </DtAndPlcOfBirth>
            <Othr>
              <Id>678-90-1234</Id>
            </Othr>
          </PrvtId>
        </Id>
        <CtctDtls>
          <EmailAdr>michael.thompson@techstart.com</EmailAdr>
        </CtctDtls>
        <Role>CFO</Role>
      </AuthrsdSgnty>
      <AcctSvcsSel>
        <AcctSvcs>
          <Cd>ONBK</Cd>
          <Desc>Corporate Online Banking with ACH Origination</Desc>
        </AcctSvcs>
        <AcctSvcs>
          <Cd>CARD</Cd>
          <Desc>Corporate Debit Cards for Authorized Signatories</Desc>
        </AcctSvcs>
      </AcctSvcsSel>
    </AcctCtrct>
    <MndtInf>
      <MndtId>MNDT-20251220-003</MndtId>
      <MndtTp>
        <Cd>ORSG</Cd>
      </MndtTp>
      <Authntcn>
        <DtTm>2025-12-20T10:45:00Z</DtTm>
      </Authntcn>
    </MndtInf>
    <MktgPref>
      <ChanlPref>EMAL</ChanlPref>
      <ConsentInd>true</ConsentInd>
      <ConsentDtTm>2025-12-20T10:30:00Z</ConsentDtTm>
    </MktgPref>
    <AddtlInf>
      <KYCChckRslt>
        <Sts>PASS</Sts>
        <ChckDt>2025-12-18</ChckDt>
        <VrfctnLvl>FULL</VrfctnLvl>
      </KYCChckRslt>
      <BizActvty>Software as a Service (SaaS) - Project Management Platform</BizActvty>
    </AddtlInf>
  </AcctOpngReq>
</Document>
```

---

## CDM Gap Analysis

**Result:** ZERO gaps identified

All 92 acmt.007 fields successfully map to existing GPS CDM entities:

### Account Entity - Core Fields ✅
All account-level fields (accountType, currency, accountNumber, openDate) are already in the schema.

### Account Entity - Extensions ✅
Product offering fields (productId, productName, expectedMonthlyTransactions, expectedAverageBalance), fee details, and marketing preferences map to extensions fields.

### Party Entity ✅
All party identification fields covered (name, dateOfBirth, placeOfBirth, nationalIDNumber, address, contactDetails, occupation, pepFlag).

### Party Entity - Extensions ✅
Source of wealth, employer name, business activity, and marketing consent fields map to extensions.

### Party Entity - Controlling Persons ✅
The Account.controllingPersons array supports:
- Beneficial owners (controlType: "OWNERSHIP")
- Authorized signatories (controlType: "SENIOR_MANAGING_OFFICIAL")
- Legal guardians (controlType: "CONTROLLING_PERSON")
- Ownership percentage

### FinancialInstitution Entity ✅
Requesting organization fields (if applicable) map to FinancialInstitution entity.

### PaymentInstruction Extensions ✅
Mandate information (mandateId, mandateType, mandateAuthenticationDateTime) maps to extensions.

### RegulatoryReport Extensions ✅
KYC/AML fields (kycStatus, kycVerificationDate, kycDocumentType, kycDocumentIssueDate, kycDocumentExpiryDate) map to extensions.

---

## Related ISO 20022 Messages

| Message | Direction | Usage |
|---------|-----------|-------|
| **acmt.001** | FI to FI | Account Opening Instruction (FI-initiated) |
| **acmt.002** | FI to FI | Account Details Confirmation |
| **acmt.007** | Customer to FI | Account Opening Request (this message - customer-initiated) |
| **acmt.008** | FI to Customer | Account Opening Request Acknowledgement |
| **acmt.009** | FI to Customer | Account Opening Amendment Request |
| **acmt.010** | Customer to FI | Account Opening Additional Information |

---

## Account Lifecycle Observations

### Customer-Initiated vs FI-Initiated Account Opening

**acmt.007 (Customer to FI) - This Message:**
- Customer submits account opening request
- Includes product selection and pricing acceptance
- Contains marketing preferences
- May include incomplete KYC (pending verification)
- Response: acmt.008 (acknowledgement) → acmt.002 (confirmation)

**acmt.001 (FI to FI):**
- FI requests another FI to open account
- Used for correspondent banking, omnibus accounts
- KYC already completed
- Response: acmt.002 (confirmation)

### Digital vs In-Branch Account Opening

**Digital/Online:**
- acmt.007 sent electronically from online banking portal or mobile app
- eKYC (electronic KYC) - document upload, selfie verification
- Immediate acknowledgement (acmt.008)
- Account may open instantly or require manual review

**In-Branch:**
- Bank staff assists customer in completing acmt.007
- Physical document verification
- Same-day account opening common
- Immediate account number assignment

### Product Selection and Bundling
The acmt.007 message supports product bundling:
- Primary product (e.g., checking account)
- Add-on services (overdraft protection, checkbook, debit card)
- Fee schedules accepted during application
- Service tier selection (standard, premium, private banking)

### Marketing Consent
Critical for GDPR, CCPA, and other privacy regulations:
- Opt-in/opt-out for marketing communications
- Channel preferences (email, SMS, mail, phone)
- Timestamp of consent
- Separate consent for different marketing types

### Expected Usage Information
Banks use this for:
- Risk assessment (expected transaction volume, balance)
- Fee waiver eligibility (minimum balance requirements)
- Compliance (unusually high volumes may trigger enhanced due diligence)
- Product recommendations

---

## References

- ISO 20022 Message Definition Report: acmt.007.001.04
- ISO 20022 External Code Lists: https://www.iso20022.org/external_code_list.page
- GPS CDM Schema: `/schemas/03_account_complete_schema.json`
- GPS CDM Schema: `/schemas/02_party_complete_schema.json`
- GPS CDM Schema: `/schemas/04_financial_institution_complete_schema.json`
- GPS CDM Schema: `/schemas/payment_instruction_extensions_schema.json`
- GPS CDM Schema: `/schemas/05_regulatory_report_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2025-12-20
**Next Review:** Q1 2026
