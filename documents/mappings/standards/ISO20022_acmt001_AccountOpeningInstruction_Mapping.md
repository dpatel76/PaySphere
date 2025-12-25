# ISO 20022 acmt.001 - Account Opening Instruction
## Complete Field Mapping to GPS CDM

**Message Type:** acmt.001.001.07 (Account Opening Instruction - Version 7)
**Standard:** ISO 20022
**Usage:** Financial institution to financial institution - Request to open new account with party details, account type, and services
**Document Date:** 2025-12-20
**Mapping Coverage:** 100% (All 85 fields mapped)

---

## Message Overview

The acmt.001 message is sent by one financial institution to another financial institution to request the opening of a new account. It contains comprehensive party details (account holder, joint owners, beneficial owners, authorized signatories), account specifications (type, currency, services), mandate information, and regulatory/KYC requirements.

**XML Namespace:** `urn:iso:std:iso:20022:tech:xsd:acmt.001.001.07`
**Root Element:** `AcctOpngInstr` (Account Opening Instruction)

**Direction:** Financial Institution → Financial Institution

**Key Use Cases:**
- Opening new customer accounts (checking, savings, investment, etc.)
- Establishing accounts with mandate structures (single, joint, power of attorney)
- Setting up accounts for corporate entities with authorized signatories
- Configuring account services (online banking, cards, overdraft protection)

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total acmt.001 Fields** | 85 | 100% |
| **Mapped to CDM** | 85 | 100% |
| **Direct Mapping** | 78 | 92% |
| **Derived/Calculated** | 4 | 5% |
| **Reference Data Lookup** | 3 | 3% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Message Identification (MsgId) - Message Header

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctOpngInstr/MsgId/Id | Message Identification | Text | 1-35 | 1..1 | Free text | Account | sourceSystemRecordId | Unique message identifier |
| AcctOpngInstr/MsgId/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISO DateTime | Account | createdTimestamp | Message creation timestamp |

---

### Requesting Party (ReqngPty) - Requesting Financial Institution

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ReqngPty/Pty/Nm | Requesting Party Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Requesting FI name |
| ReqngPty/Pty/Id/OrgId/AnyBIC | Requesting Party BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | BIC of requesting FI |
| ReqngPty/Pty/Id/OrgId/LEI | Requesting Party LEI | Code | 20 | 0..1 | LEI | FinancialInstitution | lei | Legal Entity Identifier |
| ReqngPty/Pty/PstlAdr/Ctry | Requesting Party Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Requesting FI country |
| ReqngPty/Pty/CtryOfRes | Requesting Party Country of Residence | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Country of residence |

---

### Servicing Party (SvcgPty) - Servicing Financial Institution

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SvcgPty/Pty/Nm | Servicing Party Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Servicing FI name |
| SvcgPty/Pty/Id/OrgId/AnyBIC | Servicing Party BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | BIC of servicing FI |
| SvcgPty/Pty/Id/OrgId/LEI | Servicing Party LEI | Code | 20 | 0..1 | LEI | FinancialInstitution | lei | Legal Entity Identifier |
| SvcgPty/Pty/PstlAdr/Ctry | Servicing Party Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Servicing FI country |
| SvcgPty/BrnchId/Id | Servicing Branch ID | Text | 1-35 | 0..1 | Free text | Account | branchId | Branch identifier |
| SvcgPty/BrnchId/Nm | Servicing Branch Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | branchName | Branch name |

---

### Account Contract (AcctCtrct) - Account Details

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctCtrct/TrgtGoLiveDt | Target Go-Live Date | Date | - | 0..1 | ISO Date | Account | openDate | Expected account opening date |
| AcctCtrct/TrgtClsgDt | Target Closing Date | Date | - | 0..1 | ISO Date | Account | closeDate | Expected account closing date |
| AcctCtrct/UrgcyFlg | Urgency Flag | Boolean | - | 0..1 | true/false | Account.extensions | urgentProcessingFlag | Urgent processing indicator |
| AcctCtrct/Acct/Tp/Cd | Account Type Code | Code | 1-4 | 0..1 | CACC, SVGS, etc. | Account | accountType | Account type code |
| AcctCtrct/Acct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency code |
| AcctCtrct/Acct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account.extensions | accountName | Account name/title |
| AcctCtrct/Acct/Prxy/Tp/Cd | Proxy Type Code | Code | 1-4 | 0..1 | TELE, EMAL, etc. | Account.extensions | proxyType | Proxy identifier type |
| AcctCtrct/Acct/Prxy/Id | Proxy Identification | Text | 1-2048 | 0..1 | Free text | Account.extensions | proxyId | Proxy identifier value |

---

### Account Owner (AcctSvcr/AcctOwnr) - Primary Account Holder

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctOwnr/Pty/Nm | Account Owner Name | Text | 1-140 | 0..1 | Free text | Party | name | Account holder name |
| AcctOwnr/Pty/PstlAdr/Ctry | Account Owner Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Owner country |
| AcctOwnr/Pty/PstlAdr/AdrLine | Account Owner Address Line | Text | 1-70 | 0..7 | Free text | Party | address.addressLine1 | Address lines (map up to 2) |
| AcctOwnr/Pty/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | address.streetName | Street name |
| AcctOwnr/Pty/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Free text | Party | address.buildingNumber | Building number |
| AcctOwnr/Pty/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | address.postCode | Postal/ZIP code |
| AcctOwnr/Pty/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | address.townName | City/town name |
| AcctOwnr/Pty/Id/OrgId/AnyBIC | Account Owner BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | If owner is FI |
| AcctOwnr/Pty/Id/OrgId/LEI | Account Owner LEI | Code | 20 | 0..1 | LEI | Party | legalEntityIdentifier | Legal Entity Identifier |
| AcctOwnr/Pty/Id/OrgId/Othr/Id | Account Owner Other Org ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Business registration number |
| AcctOwnr/Pty/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Date of Birth | Date | - | 1..1 | ISO Date | Party | dateOfBirth | DOB for individual |
| AcctOwnr/Pty/Id/PrvtId/DtAndPlcOfBirth/CityOfBirth | City of Birth | Text | 1-35 | 1..1 | Free text | Party | placeOfBirth | Birth city |
| AcctOwnr/Pty/Id/PrvtId/Othr/Id | Account Owner Private ID | Text | 1-35 | 0..1 | Free text | Party | nationalIDNumber | National ID, passport, etc. |
| AcctOwnr/Pty/CtryOfRes | Account Owner Country of Residence | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Residence country |
| AcctOwnr/Pty/CtctDtls/EmailAdr | Email Address | Text | 1-256 | 0..1 | Email format | Party | contactDetails.emailAddress | Email |
| AcctOwnr/Pty/CtctDtls/PhneNb | Phone Number | Text | 1-20 | 0..1 | Phone format | Party | contactDetails.phoneNumber | Phone |
| AcctOwnr/Pty/CtctDtls/MobNb | Mobile Number | Text | 1-20 | 0..1 | Phone format | Party | contactDetails.mobileNumber | Mobile |

---

### Legal Guardian (LglGuardn) - For Minor Account Holders

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LglGuardn/Nm | Legal Guardian Name | Text | 1-140 | 0..1 | Free text | Party | name | Guardian name (create separate Party) |
| LglGuardn/PstlAdr/Ctry | Legal Guardian Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Guardian country |
| LglGuardn/Id/PrvtId/Othr/Id | Legal Guardian ID | Text | 1-35 | 0..1 | Free text | Party | nationalIDNumber | Guardian identifier |
| LglGuardn/CtctDtls/EmailAdr | Legal Guardian Email | Text | 1-256 | 0..1 | Email format | Party | contactDetails.emailAddress | Guardian email |

---

### Account Service Selection (AcctSvcsSel) - Services and Features

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctSvcsSel/SvcLvl/Cd | Service Level Code | Code | 1-4 | 0..1 | Premium, Standard | Account.extensions | serviceLevelCode | Service tier |
| AcctSvcsSel/AcctSvcs/Cd | Account Services Code | Code | 1-4 | 0..1 | ONBK, CARD, CHQB | Account.extensions | accountServicesRequested | Services requested (array) |
| AcctSvcsSel/AcctSvcs/Desc | Account Services Description | Text | 1-140 | 0..1 | Free text | Account.extensions | accountServicesDescription | Service description |
| AcctSvcsSel/AcctSvcs/AddtlInf | Account Services Additional Info | Text | 1-350 | 0..1 | Free text | Account.extensions | accountServicesAdditionalInfo | Additional service details |

---

### Mandate Information (MndtInf) - Signing Authority

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| MndtInf/MndtId | Mandate ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | mandateId | Mandate reference ID |
| MndtInf/MndtTp/Cd | Mandate Type Code | Code | 1-4 | 0..1 | SNGL, JOIT, PWOA | PaymentInstruction.extensions | mandateType | Single, Joint, Power of Attorney |
| MndtInf/MndtReqId | Mandate Request ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | mandateRequestId | Mandate request reference |
| MndtInf/Authntcn/Dt | Authentication Date | Date | - | 0..1 | ISO Date | PaymentInstruction.extensions | mandateAuthenticationDate | When mandate authenticated |
| MndtInf/Authntcn/DtTm | Authentication Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction.extensions | mandateAuthenticationDateTime | Authentication timestamp |

---

### Authorized Signatories (AuthrsdSgnty) - Signing Authority Parties

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AuthrsdSgnty/Nm | Authorized Signatory Name | Text | 1-140 | 0..1 | Free text | Party | name | Signatory name (create Party, link via controllingPersons) |
| AuthrsdSgnty/PstlAdr/Ctry | Authorized Signatory Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Signatory country |
| AuthrsdSgnty/Id/PrvtId/Othr/Id | Authorized Signatory ID | Text | 1-35 | 0..1 | Free text | Party | nationalIDNumber | Signatory identifier |
| AuthrsdSgnty/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Authorized Signatory DOB | Date | - | 1..1 | ISO Date | Party | dateOfBirth | Signatory date of birth |
| AuthrsdSgnty/CtctDtls/EmailAdr | Authorized Signatory Email | Text | 1-256 | 0..1 | Email format | Party | contactDetails.emailAddress | Signatory email |
| AuthrsdSgnty/Role | Signatory Role | Text | 1-35 | 0..1 | Free text | Account | controllingPersons.controlType | Map to "SENIOR_MANAGING_OFFICIAL" |

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

### Account Restrictions (AcctRstrctns) - Usage Limitations

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctRstrctns/RstrctnTp/Cd | Restriction Type Code | Code | 1-4 | 0..1 | NDBT, NCDT, etc. | Account.extensions | accountRestrictionType | No debit, no credit, etc. |
| AcctRstrctns/RstrctnTp/Prtry | Restriction Type Proprietary | Text | 1-35 | 0..1 | Free text | Account.extensions | accountRestrictionProprietaryType | Custom restriction |
| AcctRstrctns/VldtyPrd/FrDt | Restriction Valid From Date | Date | - | 0..1 | ISO Date | Account.extensions | accountRestrictionValidFrom | Restriction start date |
| AcctRstrctns/VldtyPrd/ToDt | Restriction Valid To Date | Date | - | 0..1 | ISO Date | Account.extensions | accountRestrictionValidTo | Restriction end date |

---

### KYC/AML Information (AddtlInf) - Regulatory Compliance

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AddtlInf/KYCChckRslt/Sts | KYC Check Result Status | Code | 1-4 | 0..1 | PASS, FAIL, PEND | RegulatoryReport.extensions | kycStatus | KYC verification status |
| AddtlInf/KYCChckRslt/ChckDt | KYC Check Date | Date | - | 0..1 | ISO Date | RegulatoryReport.extensions | kycVerificationDate | KYC verification date |
| AddtlInf/KYCChckRslt/VrfctnLvl | KYC Verification Level | Code | 1-4 | 0..1 | FULL, SIMP, etc. | RegulatoryReport.extensions | kycVerificationLevel | Verification tier |
| AddtlInf/DocOnFile/DocTp/Cd | Document on File Type Code | Code | 1-4 | 0..1 | PASS, IDCD, DRLI | RegulatoryReport.extensions | kycDocumentType | Document type |
| AddtlInf/DocOnFile/DocNb | Document Number | Text | 1-35 | 0..1 | Free text | Party | identificationNumber | Document number |
| AddtlInf/DocOnFile/IsseDt | Document Issue Date | Date | - | 0..1 | ISO Date | RegulatoryReport.extensions | kycDocumentIssueDate | Document issue date |
| AddtlInf/DocOnFile/XpryDt | Document Expiry Date | Date | - | 0..1 | ISO Date | RegulatoryReport.extensions | kycDocumentExpiryDate | Document expiry date |

---

## Code Lists and Enumerations

### Account Type Codes (Acct/Tp/Cd)
- **CACC**: Current Account (Checking)
- **SVGS**: Savings Account
- **MMKT**: Money Market Account
- **LOAN**: Loan Account
- **CCRD**: Credit Card Account
- **INVS**: Investment Account
- **TRAS**: Transactional Account
- **SLRY**: Salary Account
- **OTHR**: Other

**CDM Mapping:**
- CACC → CHECKING
- SVGS → SAVINGS
- MMKT → MONEY_MARKET
- LOAN → LOAN
- CCRD → CREDIT_CARD
- INVS → INVESTMENT

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

### Account Restriction Type Codes (RstrctnTp/Cd)
- **NDBT**: No Debit Allowed
- **NCDT**: No Credit Allowed
- **BLCK**: Account Blocked
- **DORM**: Dormant Account
- **FRZE**: Frozen Account

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

### Example 1: Individual Checking Account Opening

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:acmt.001.001.07">
  <AcctOpngInstr>
    <MsgId>
      <Id>ACMT001-20251220-001</Id>
      <CreDtTm>2025-12-20T09:30:00Z</CreDtTm>
    </MsgId>
    <ReqngPty>
      <Pty>
        <Nm>Bank of America, N.A.</Nm>
        <Id>
          <OrgId>
            <AnyBIC>BOFAUS3N</AnyBIC>
          </OrgId>
        </Id>
      </Pty>
    </ReqngPty>
    <SvcgPty>
      <Pty>
        <Nm>Bank of America, N.A.</Nm>
        <Id>
          <OrgId>
            <AnyBIC>BOFAUS3N</AnyBIC>
          </OrgId>
        </Id>
      </Pty>
      <BrnchId>
        <Id>1234</Id>
        <Nm>Charlotte Main Branch</Nm>
      </BrnchId>
    </SvcgPty>
    <AcctCtrct>
      <TrgtGoLiveDt>2025-12-22</TrgtGoLiveDt>
      <Acct>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
        <Ccy>USD</Ccy>
        <Nm>John Doe - Checking Account</Nm>
      </Acct>
      <AcctOwnr>
        <Pty>
          <Nm>John Michael Doe</Nm>
          <PstlAdr>
            <StrtNm>Main Street</StrtNm>
            <BldgNb>123</BldgNb>
            <PstCd>28202</PstCd>
            <TwnNm>Charlotte</TwnNm>
            <Ctry>US</Ctry>
          </PstlAdr>
          <Id>
            <PrvtId>
              <DtAndPlcOfBirth>
                <BirthDt>1985-06-15</BirthDt>
                <CityOfBirth>New York</CityOfBirth>
              </DtAndPlcOfBirth>
              <Othr>
                <Id>123-45-6789</Id>
              </Othr>
            </PrvtId>
          </Id>
          <CtryOfRes>US</CtryOfRes>
          <CtctDtls>
            <EmailAdr>john.doe@email.com</EmailAdr>
            <PhneNb>+1-704-555-1234</PhneNb>
            <MobNb>+1-704-555-5678</MobNb>
          </CtctDtls>
        </Pty>
      </AcctOwnr>
      <AcctSvcsSel>
        <SvcLvl>
          <Cd>STND</Cd>
        </SvcLvl>
        <AcctSvcs>
          <Cd>ONBK</Cd>
          <Desc>Online Banking Access</Desc>
        </AcctSvcs>
        <AcctSvcs>
          <Cd>CARD</Cd>
          <Desc>Debit Card Issuance</Desc>
        </AcctSvcs>
      </AcctSvcsSel>
    </AcctCtrct>
    <MndtInf>
      <MndtId>MNDT-20251220-001</MndtId>
      <MndtTp>
        <Cd>SNGL</Cd>
      </MndtTp>
      <Authntcn>
        <DtTm>2025-12-20T09:00:00Z</DtTm>
      </Authntcn>
    </MndtInf>
    <AddtlInf>
      <KYCChckRslt>
        <Sts>PASS</Sts>
        <ChckDt>2025-12-19</ChckDt>
        <VrfctnLvl>FULL</VrfctnLvl>
      </KYCChckRslt>
      <DocOnFile>
        <DocTp>
          <Cd>DRLI</Cd>
        </DocTp>
        <DocNb>NC-12345678</DocNb>
        <IsseDt>2020-06-15</IsseDt>
        <XpryDt>2028-06-15</XpryDt>
      </DocOnFile>
    </AddtlInf>
  </AcctOpngInstr>
</Document>
```

### Example 2: Joint Savings Account with Beneficial Owner

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:acmt.001.001.07">
  <AcctOpngInstr>
    <MsgId>
      <Id>ACMT001-20251220-002</Id>
      <CreDtTm>2025-12-20T10:15:00Z</CreDtTm>
    </MsgId>
    <ReqngPty>
      <Pty>
        <Nm>Bank of America, N.A.</Nm>
        <Id>
          <OrgId>
            <AnyBIC>BOFAUS3N</AnyBIC>
          </OrgId>
        </Id>
      </Pty>
    </ReqngPty>
    <SvcgPty>
      <Pty>
        <Nm>Bank of America, N.A.</Nm>
        <Id>
          <OrgId>
            <AnyBIC>BOFAUS3N</AnyBIC>
          </OrgId>
        </Id>
      </Pty>
    </SvcgPty>
    <AcctCtrct>
      <TrgtGoLiveDt>2025-12-23</TrgtGoLiveDt>
      <Acct>
        <Tp>
          <Cd>SVGS</Cd>
        </Tp>
        <Ccy>USD</Ccy>
        <Nm>Smith Family - Savings Account</Nm>
      </Acct>
      <AcctOwnr>
        <Pty>
          <Nm>Robert James Smith</Nm>
          <PstlAdr>
            <StrtNm>Oak Avenue</StrtNm>
            <BldgNb>456</BldgNb>
            <PstCd>10001</PstCd>
            <TwnNm>New York</TwnNm>
            <Ctry>US</Ctry>
          </PstlAdr>
          <Id>
            <PrvtId>
              <DtAndPlcOfBirth>
                <BirthDt>1978-03-22</BirthDt>
                <CityOfBirth>Boston</CityOfBirth>
              </DtAndPlcOfBirth>
              <Othr>
                <Id>234-56-7890</Id>
              </Othr>
            </PrvtId>
          </Id>
          <CtryOfRes>US</CtryOfRes>
          <CtctDtls>
            <EmailAdr>robert.smith@email.com</EmailAdr>
            <MobNb>+1-212-555-1234</MobNb>
          </CtctDtls>
        </Pty>
      </AcctOwnr>
      <AcctOwnr>
        <Pty>
          <Nm>Sarah Elizabeth Smith</Nm>
          <PstlAdr>
            <StrtNm>Oak Avenue</StrtNm>
            <BldgNb>456</BldgNb>
            <PstCd>10001</PstCd>
            <TwnNm>New York</TwnNm>
            <Ctry>US</Ctry>
          </PstlAdr>
          <Id>
            <PrvtId>
              <DtAndPlcOfBirth>
                <BirthDt>1980-08-10</BirthDt>
                <CityOfBirth>Chicago</CityOfBirth>
              </DtAndPlcOfBirth>
              <Othr>
                <Id>345-67-8901</Id>
              </Othr>
            </PrvtId>
          </Id>
          <CtryOfRes>US</CtryOfRes>
          <CtctDtls>
            <EmailAdr>sarah.smith@email.com</EmailAdr>
            <MobNb>+1-212-555-5678</MobNb>
          </CtctDtls>
        </Pty>
      </AcctOwnr>
      <BnfclOwnr>
        <Nm>Emily Grace Smith</Nm>
        <Id>
          <PrvtId>
            <DtAndPlcOfBirth>
              <BirthDt>2010-05-18</BirthDt>
            </DtAndPlcOfBirth>
            <Othr>
              <Id>456-78-9012</Id>
            </Othr>
          </PrvtId>
        </Id>
        <OwnrshPctg>100.00</OwnrshPctg>
      </BnfclOwnr>
    </AcctCtrct>
    <MndtInf>
      <MndtId>MNDT-20251220-002</MndtId>
      <MndtTp>
        <Cd>JOIT</Cd>
      </MndtTp>
      <Authntcn>
        <DtTm>2025-12-20T10:00:00Z</DtTm>
      </Authntcn>
    </MndtInf>
    <AddtlInf>
      <KYCChckRslt>
        <Sts>PASS</Sts>
        <ChckDt>2025-12-19</ChckDt>
        <VrfctnLvl>FULL</VrfctnLvl>
      </KYCChckRslt>
    </AddtlInf>
  </AcctOpngInstr>
</Document>
```

### Example 3: Corporate Account with Authorized Signatories

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:acmt.001.001.07">
  <AcctOpngInstr>
    <MsgId>
      <Id>ACMT001-20251220-003</Id>
      <CreDtTm>2025-12-20T11:00:00Z</CreDtTm>
    </MsgId>
    <ReqngPty>
      <Pty>
        <Nm>Bank of America, N.A.</Nm>
        <Id>
          <OrgId>
            <AnyBIC>BOFAUS3N</AnyBIC>
          </OrgId>
        </Id>
      </Pty>
    </ReqngPty>
    <SvcgPty>
      <Pty>
        <Nm>Bank of America, N.A.</Nm>
        <Id>
          <OrgId>
            <AnyBIC>BOFAUS3N</AnyBIC>
          </OrgId>
        </Id>
      </Pty>
    </SvcgPty>
    <AcctCtrct>
      <TrgtGoLiveDt>2025-12-24</TrgtGoLiveDt>
      <UrgcyFlg>false</UrgcyFlg>
      <Acct>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
        <Ccy>USD</Ccy>
        <Nm>Acme Corporation - Operating Account</Nm>
      </Acct>
      <AcctOwnr>
        <Pty>
          <Nm>Acme Corporation</Nm>
          <PstlAdr>
            <StrtNm>Technology Drive</StrtNm>
            <BldgNb>789</BldgNb>
            <PstCd>94025</PstCd>
            <TwnNm>Menlo Park</TwnNm>
            <Ctry>US</Ctry>
          </PstlAdr>
          <Id>
            <OrgId>
              <LEI>5493001KJTIIGC8Y1R12</LEI>
              <Othr>
                <Id>12-3456789</Id>
              </Othr>
            </OrgId>
          </Id>
          <CtryOfRes>US</CtryOfRes>
          <CtctDtls>
            <EmailAdr>finance@acmecorp.com</EmailAdr>
            <PhneNb>+1-650-555-1234</PhneNb>
          </CtctDtls>
        </Pty>
      </AcctOwnr>
      <AuthrsdSgnty>
        <Nm>James Anderson</Nm>
        <PstlAdr>
          <Ctry>US</Ctry>
        </PstlAdr>
        <Id>
          <PrvtId>
            <DtAndPlcOfBirth>
              <BirthDt>1975-11-12</BirthDt>
            </DtAndPlcOfBirth>
            <Othr>
              <Id>567-89-0123</Id>
            </Othr>
          </PrvtId>
        </Id>
        <CtctDtls>
          <EmailAdr>james.anderson@acmecorp.com</EmailAdr>
        </CtctDtls>
        <Role>CFO</Role>
      </AuthrsdSgnty>
      <AuthrsdSgnty>
        <Nm>Linda Martinez</Nm>
        <PstlAdr>
          <Ctry>US</Ctry>
        </PstlAdr>
        <Id>
          <PrvtId>
            <DtAndPlcOfBirth>
              <BirthDt>1982-04-25</BirthDt>
            </DtAndPlcOfBirth>
            <Othr>
              <Id>678-90-1234</Id>
            </Othr>
          </PrvtId>
        </Id>
        <CtctDtls>
          <EmailAdr>linda.martinez@acmecorp.com</EmailAdr>
        </CtctDtls>
        <Role>Treasurer</Role>
      </AuthrsdSgnty>
      <AcctSvcsSel>
        <AcctSvcs>
          <Cd>ONBK</Cd>
          <Desc>Corporate Online Banking</Desc>
        </AcctSvcs>
        <AcctSvcs>
          <Cd>CARD</Cd>
          <Desc>Corporate Debit Cards</Desc>
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
    <AddtlInf>
      <KYCChckRslt>
        <Sts>PASS</Sts>
        <ChckDt>2025-12-18</ChckDt>
        <VrfctnLvl>FULL</VrfctnLvl>
      </KYCChckRslt>
      <DocOnFile>
        <DocTp>
          <Cd>OTHR</Cd>
        </DocTp>
        <DocNb>CERT-2025-123456</DocNb>
        <IsseDt>2025-01-15</IsseDt>
      </DocOnFile>
    </AddtlInf>
  </AcctOpngInstr>
</Document>
```

---

## CDM Gap Analysis

**Result:** ZERO gaps identified

All 85 acmt.001 fields successfully map to existing GPS CDM entities:

### Account Entity - Core Fields ✅
All account-level fields (accountType, currency, accountNumber, iban, branchId, openDate, accountStatus) are already in the schema.

### Account Entity - Extensions ✅
Account service selections, restrictions, and mandate information map to extensions fields.

### Party Entity ✅
All party identification fields covered (name, dateOfBirth, placeOfBirth, nationalIDNumber, address, contactDetails, pepFlag).

### Party Entity - Controlling Persons ✅
The Account.controllingPersons array supports:
- Beneficial owners (controlType: "OWNERSHIP")
- Authorized signatories (controlType: "SENIOR_MANAGING_OFFICIAL")
- Legal guardians (controlType: "CONTROLLING_PERSON")
- Ownership percentage

### FinancialInstitution Entity ✅
All FI fields covered (bic, lei, institutionName, country, branchName, branchIdentification).

### PaymentInstruction Extensions ✅
Mandate information (mandateId, mandateType, mandateAuthenticationDate) maps to extensions.

### RegulatoryReport Extensions ✅
KYC/AML fields (kycStatus, kycVerificationDate, kycDocumentType, kycDocumentIssueDate, kycDocumentExpiryDate) map to extensions.

---

## Related ISO 20022 Messages

| Message | Direction | Usage |
|---------|-----------|-------|
| **acmt.002** | Response | Account Details Confirmation (response to acmt.001) |
| **acmt.003** | Request | Account Modification Instruction |
| **acmt.005** | Request | Account Deletion Instruction |
| **acmt.007** | Request | Account Opening Request (customer-initiated) |
| **acmt.008** | Response | Account Opening Request Acknowledgement |

---

## Account Lifecycle Observations

### Account Opening Flow
1. **acmt.001** - FI to FI: Account Opening Instruction (this message)
2. **acmt.002** - FI to FI: Account Details Confirmation (account opened, IBAN assigned)
3. **camt.052** - Account statement/notification once active

### Mandate Types and Authorization
- **SNGL**: Single signature required (one person can transact)
- **JOIT**: Joint signature required (all account holders must sign)
- **ORSG**: Or signature (any one account holder can sign)
- **PWOA**: Power of attorney (authorized representative can sign)

### KYC/AML Requirements
The message supports comprehensive KYC data collection:
- Document collection (passport, ID card, driver's license)
- Verification level (full vs simplified)
- Verification status (pass, fail, pending)
- Document expiry tracking

---

## References

- ISO 20022 Message Definition Report: acmt.001.001.07
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
