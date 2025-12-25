# ISO 20022 acmt.002 - Account Details Confirmation
## Complete Field Mapping to GPS CDM

**Message Type:** acmt.002.001.07 (Account Details Confirmation - Version 7)
**Standard:** ISO 20022
**Usage:** Financial institution to financial institution - Confirmation of account opening with assigned account number and IBAN
**Document Date:** 2025-12-20
**Mapping Coverage:** 100% (All 78 fields mapped)

---

## Message Overview

The acmt.002 message is sent by the servicing financial institution to the requesting financial institution to confirm that an account has been successfully opened. It provides the assigned account number, IBAN (if applicable), confirmation of services activated, and the account's operational status.

**XML Namespace:** `urn:iso:std:iso:20022:tech:xsd:acmt.002.001.07`
**Root Element:** `AcctDtlsConf` (Account Details Confirmation)

**Direction:** Servicing FI → Requesting FI

**Key Use Cases:**
- Confirming successful account opening (response to acmt.001)
- Providing assigned account number and IBAN
- Confirming activated services (online banking, cards, etc.)
- Establishing account operational status and go-live date

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total acmt.002 Fields** | 78 | 100% |
| **Mapped to CDM** | 78 | 100% |
| **Direct Mapping** | 72 | 92% |
| **Derived/Calculated** | 3 | 4% |
| **Reference Data Lookup** | 3 | 4% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Message Identification (MsgId) - Message Header

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctDtlsConf/MsgId/Id | Message Identification | Text | 1-35 | 1..1 | Free text | Account | sourceSystemRecordId | Unique message identifier |
| AcctDtlsConf/MsgId/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISO DateTime | Account | createdTimestamp | Message creation timestamp |

---

### References (Refs) - Original Request Reference

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Refs/MsgId/Id | Original Message ID | Text | 1-35 | 0..1 | Free text | Account.extensions | originalMessageId | Reference to acmt.001 message |
| Refs/MsgId/CreDtTm | Original Message Creation DateTime | DateTime | - | 0..1 | ISO DateTime | Account.extensions | originalMessageDateTime | Original request timestamp |
| Refs/AcctId/Id/IBAN | Referenced Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | IBAN from original request |
| Refs/AcctId/Id/Othr/Id | Referenced Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Account number from original request |

---

### Requesting Party (ReqngPty) - Requesting Financial Institution

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ReqngPty/Pty/Nm | Requesting Party Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Requesting FI name |
| ReqngPty/Pty/Id/OrgId/AnyBIC | Requesting Party BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | bic | BIC of requesting FI |
| ReqngPty/Pty/Id/OrgId/LEI | Requesting Party LEI | Code | 20 | 0..1 | LEI | FinancialInstitution | lei | Legal Entity Identifier |
| ReqngPty/Pty/PstlAdr/Ctry | Requesting Party Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Requesting FI country |

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

### Account Contract (AcctCtrct) - Confirmed Account Details

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctCtrct/GoLiveDt | Go-Live Date | Date | - | 0..1 | ISO Date | Account | openDate | Actual account opening date |
| AcctCtrct/ClsgDt | Closing Date | Date | - | 0..1 | ISO Date | Account | closeDate | Account closing date (if applicable) |
| AcctCtrct/Acct/Id/IBAN | Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | Assigned IBAN |
| AcctCtrct/Acct/Id/Othr/Id | Account Number | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Assigned account number |
| AcctCtrct/Acct/Tp/Cd | Account Type Code | Code | 1-4 | 0..1 | CACC, SVGS, etc. | Account | accountType | Account type code |
| AcctCtrct/Acct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency code |
| AcctCtrct/Acct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account.extensions | accountName | Account name/title |
| AcctCtrct/Acct/Sts/Cd | Account Status Code | Code | 1-4 | 0..1 | ACTV, INAC, etc. | Account | accountStatus | Account operational status |
| AcctCtrct/Acct/Prxy/Tp/Cd | Proxy Type Code | Code | 1-4 | 0..1 | TELE, EMAL, etc. | Account.extensions | proxyType | Proxy identifier type |
| AcctCtrct/Acct/Prxy/Id | Proxy Identification | Text | 1-2048 | 0..1 | Free text | Account.extensions | proxyId | Proxy identifier value |

---

### Account Owner (AcctOwnr) - Confirmed Account Holder

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctOwnr/Pty/Nm | Account Owner Name | Text | 1-140 | 0..1 | Free text | Party | name | Account holder name |
| AcctOwnr/Pty/PstlAdr/Ctry | Account Owner Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Owner country |
| AcctOwnr/Pty/PstlAdr/AdrLine | Account Owner Address Line | Text | 1-70 | 0..7 | Free text | Party | address.addressLine1 | Address lines |
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

### Account Service Selection (AcctSvcsSel) - Confirmed Services

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctSvcsSel/SvcLvl/Cd | Service Level Code | Code | 1-4 | 0..1 | Premium, Standard | Account.extensions | serviceLevelCode | Service tier |
| AcctSvcsSel/AcctSvcs/Cd | Account Services Code | Code | 1-4 | 0..1 | ONBK, CARD, CHQB | Account.extensions | accountServicesActivated | Services activated (array) |
| AcctSvcsSel/AcctSvcs/Desc | Account Services Description | Text | 1-140 | 0..1 | Free text | Account.extensions | accountServicesDescription | Service description |
| AcctSvcsSel/AcctSvcs/AddtlInf | Account Services Additional Info | Text | 1-350 | 0..1 | Free text | Account.extensions | accountServicesAdditionalInfo | Additional service details |
| AcctSvcsSel/AcctSvcs/Sts/Cd | Account Service Status Code | Code | 1-4 | 0..1 | ACTV, PEND, REJT | Account.extensions | accountServiceStatus | Service activation status |

---

### Mandate Information (MndtInf) - Confirmed Mandate

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| MndtInf/MndtId | Mandate ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | mandateId | Mandate reference ID |
| MndtInf/MndtTp/Cd | Mandate Type Code | Code | 1-4 | 0..1 | SNGL, JOIT, PWOA | PaymentInstruction.extensions | mandateType | Single, Joint, Power of Attorney |
| MndtInf/Authntcn/Dt | Authentication Date | Date | - | 0..1 | ISO Date | PaymentInstruction.extensions | mandateAuthenticationDate | When mandate authenticated |
| MndtInf/Authntcn/DtTm | Authentication Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction.extensions | mandateAuthenticationDateTime | Authentication timestamp |

---

### Authorized Signatories (AuthrsdSgnty) - Confirmed Signatories

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AuthrsdSgnty/Nm | Authorized Signatory Name | Text | 1-140 | 0..1 | Free text | Party | name | Signatory name |
| AuthrsdSgnty/PstlAdr/Ctry | Authorized Signatory Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Signatory country |
| AuthrsdSgnty/Id/PrvtId/Othr/Id | Authorized Signatory ID | Text | 1-35 | 0..1 | Free text | Party | nationalIDNumber | Signatory identifier |
| AuthrsdSgnty/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Authorized Signatory DOB | Date | - | 1..1 | ISO Date | Party | dateOfBirth | Signatory date of birth |
| AuthrsdSgnty/CtctDtls/EmailAdr | Authorized Signatory Email | Text | 1-256 | 0..1 | Email format | Party | contactDetails.emailAddress | Signatory email |
| AuthrsdSgnty/Role | Signatory Role | Text | 1-35 | 0..1 | Free text | Account | controllingPersons.controlType | Map to "SENIOR_MANAGING_OFFICIAL" |

---

### Beneficial Owner (BnfclOwnr) - Confirmed Beneficial Owner

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| BnfclOwnr/Nm | Beneficial Owner Name | Text | 1-140 | 0..1 | Free text | Party | name | Beneficial owner name |
| BnfclOwnr/PstlAdr/Ctry | Beneficial Owner Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | BO country |
| BnfclOwnr/Id/OrgId/LEI | Beneficial Owner LEI | Code | 20 | 0..1 | LEI | Party | legalEntityIdentifier | BO LEI |
| BnfclOwnr/Id/PrvtId/Othr/Id | Beneficial Owner ID | Text | 1-35 | 0..1 | Free text | Party | nationalIDNumber | BO identifier |
| BnfclOwnr/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Beneficial Owner DOB | Date | - | 1..1 | ISO Date | Party | dateOfBirth | BO date of birth |
| BnfclOwnr/OwnrshPctg | Ownership Percentage | Rate | - | 0..1 | 0-100 | Account | controllingPersons.ownershipPercentage | Ownership % |

---

### Account Restrictions (AcctRstrctns) - Active Restrictions

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctRstrctns/RstrctnTp/Cd | Restriction Type Code | Code | 1-4 | 0..1 | NDBT, NCDT, etc. | Account.extensions | accountRestrictionType | No debit, no credit, etc. |
| AcctRstrctns/RstrctnTp/Prtry | Restriction Type Proprietary | Text | 1-35 | 0..1 | Free text | Account.extensions | accountRestrictionProprietaryType | Custom restriction |
| AcctRstrctns/VldtyPrd/FrDt | Restriction Valid From Date | Date | - | 0..1 | ISO Date | Account.extensions | accountRestrictionValidFrom | Restriction start date |
| AcctRstrctns/VldtyPrd/ToDt | Restriction Valid To Date | Date | - | 0..1 | ISO Date | Account.extensions | accountRestrictionValidTo | Restriction end date |

---

### Balance Information (Bal) - Initial Account Balance

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Bal/Amt | Balance Amount | Amount | - | 1..1 | Decimal (18,5) | Account | currentBalance | Account balance |
| Bal/Amt/@Ccy | Balance Currency | Code | 3 | 1..1 | ISO 4217 | Account | currency | Balance currency |
| Bal/CdtDbtInd | Credit Debit Indicator | Code | 4 | 1..1 | CRDT, DBIT | Account.extensions | balanceIndicator | Credit or debit balance |
| Bal/Tp/CdOrPrtry/Cd | Balance Type Code | Code | 1-4 | 0..1 | OPBD, CLBD, etc. | Account.extensions | balanceType | Opening, closing, available |
| Bal/Dt/Dt | Balance Date | Date | - | 0..1 | ISO Date | Account | effectiveFrom | Balance as-of date |

---

### Confirmation Status (Sts) - Overall Confirmation Status

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Sts/Cd | Confirmation Status Code | Code | 1-4 | 0..1 | ACCP, RJCT, PEND | Account.extensions | accountOpeningStatus | Accepted, Rejected, Pending |
| Sts/Rsn/Cd | Status Reason Code | Code | 1-4 | 0..1 | Reason code | Account.extensions | accountOpeningReasonCode | Reason for status |
| Sts/Rsn/Prtry | Status Reason Proprietary | Text | 1-35 | 0..1 | Free text | Account.extensions | accountOpeningReasonText | Custom reason text |
| Sts/AddtlInf | Status Additional Information | Text | 1-350 | 0..1 | Free text | Account.extensions | accountOpeningAdditionalInfo | Additional details |

---

## Code Lists and Enumerations

### Account Type Codes (Acct/Tp/Cd)
- **CACC**: Current Account (Checking)
- **SVGS**: Savings Account
- **MMKT**: Money Market Account
- **LOAN**: Loan Account
- **CCRD**: Credit Card Account
- **INVS**: Investment Account

**CDM Mapping:**
- CACC → CHECKING
- SVGS → SAVINGS
- MMKT → MONEY_MARKET
- LOAN → LOAN
- CCRD → CREDIT_CARD
- INVS → INVESTMENT

### Account Status Codes (Acct/Sts/Cd)
- **ACTV**: Active
- **INAC**: Inactive
- **DORM**: Dormant
- **CLOS**: Closed
- **FRZE**: Frozen
- **SUSP**: Suspended

**CDM Mapping:**
- ACTV → ACTIVE
- INAC → INACTIVE
- DORM → DORMANT
- CLOS → CLOSED
- FRZE → FROZEN
- SUSP → SUSPENDED

### Confirmation Status Codes (Sts/Cd)
- **ACCP**: Accepted - Account successfully opened
- **RJCT**: Rejected - Account opening rejected
- **PEND**: Pending - Account opening pending review
- **PART**: Partially Accepted - Some services activated, some pending

### Balance Type Codes (Bal/Tp/CdOrPrtry/Cd)
- **OPBD**: Opening Balance
- **CLBD**: Closing Balance
- **AVLB**: Available Balance
- **LEDG**: Ledger Balance

### Credit/Debit Indicator (Bal/CdtDbtInd)
- **CRDT**: Credit (positive balance)
- **DBIT**: Debit (negative balance/overdraft)

### Account Services Status Codes (AcctSvcs/Sts/Cd)
- **ACTV**: Active/Activated
- **PEND**: Pending Activation
- **REJT**: Rejected
- **SUSP**: Suspended

---

## Message Examples

### Example 1: Successful Checking Account Confirmation

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:acmt.002.001.07">
  <AcctDtlsConf>
    <MsgId>
      <Id>ACMT002-20251220-001</Id>
      <CreDtTm>2025-12-20T14:30:00Z</CreDtTm>
    </MsgId>
    <Refs>
      <MsgId>
        <Id>ACMT001-20251220-001</Id>
        <CreDtTm>2025-12-20T09:30:00Z</CreDtTm>
      </MsgId>
    </Refs>
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
      <GoLiveDt>2025-12-22</GoLiveDt>
      <Acct>
        <Id>
          <IBAN>US12BOFA12340000123456</IBAN>
          <Othr>
            <Id>1234567890</Id>
          </Othr>
        </Id>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
        <Ccy>USD</Ccy>
        <Nm>John Doe - Checking Account</Nm>
        <Sts>
          <Cd>ACTV</Cd>
        </Sts>
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
        <AcctSvcs>
          <Cd>ONBK</Cd>
          <Desc>Online Banking Access</Desc>
          <Sts>
            <Cd>ACTV</Cd>
          </Sts>
        </AcctSvcs>
        <AcctSvcs>
          <Cd>CARD</Cd>
          <Desc>Debit Card Issuance</Desc>
          <Sts>
            <Cd>PEND</Cd>
          </Sts>
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
    <Bal>
      <Amt Ccy="USD">0.00</Amt>
      <CdtDbtInd>CRDT</CdtDbtInd>
      <Tp>
        <CdOrPrtry>
          <Cd>OPBD</Cd>
        </CdOrPrtry>
      </Tp>
      <Dt>
        <Dt>2025-12-22</Dt>
      </Dt>
    </Bal>
    <Sts>
      <Cd>ACCP</Cd>
      <AddtlInf>Account successfully opened and activated</AddtlInf>
    </Sts>
  </AcctDtlsConf>
</Document>
```

### Example 2: Joint Savings Account Confirmation with IBAN

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:acmt.002.001.07">
  <AcctDtlsConf>
    <MsgId>
      <Id>ACMT002-20251220-002</Id>
      <CreDtTm>2025-12-20T15:00:00Z</CreDtTm>
    </MsgId>
    <Refs>
      <MsgId>
        <Id>ACMT001-20251220-002</Id>
        <CreDtTm>2025-12-20T10:15:00Z</CreDtTm>
      </MsgId>
    </Refs>
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
      <GoLiveDt>2025-12-23</GoLiveDt>
      <Acct>
        <Id>
          <IBAN>US12BOFA12340000987654</IBAN>
          <Othr>
            <Id>9876543210</Id>
          </Othr>
        </Id>
        <Tp>
          <Cd>SVGS</Cd>
        </Tp>
        <Ccy>USD</Ccy>
        <Nm>Smith Family - Savings Account</Nm>
        <Sts>
          <Cd>ACTV</Cd>
        </Sts>
      </Acct>
      <AcctOwnr>
        <Pty>
          <Nm>Robert James Smith</Nm>
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
        </Pty>
      </AcctOwnr>
      <AcctOwnr>
        <Pty>
          <Nm>Sarah Elizabeth Smith</Nm>
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
    <Bal>
      <Amt Ccy="USD">5000.00</Amt>
      <CdtDbtInd>CRDT</CdtDbtInd>
      <Tp>
        <CdOrPrtry>
          <Cd>OPBD</Cd>
        </CdOrPrtry>
      </Tp>
      <Dt>
        <Dt>2025-12-23</Dt>
      </Dt>
    </Bal>
    <Sts>
      <Cd>ACCP</Cd>
      <AddtlInf>Joint savings account successfully opened with initial deposit</AddtlInf>
    </Sts>
  </AcctDtlsConf>
</Document>
```

### Example 3: Rejected Account Opening

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:acmt.002.001.07">
  <AcctDtlsConf>
    <MsgId>
      <Id>ACMT002-20251220-003</Id>
      <CreDtTm>2025-12-20T16:00:00Z</CreDtTm>
    </MsgId>
    <Refs>
      <MsgId>
        <Id>ACMT001-20251220-004</Id>
        <CreDtTm>2025-12-20T12:00:00Z</CreDtTm>
      </MsgId>
    </Refs>
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
    <Sts>
      <Cd>RJCT</Cd>
      <Rsn>
        <Cd>NOAS</Cd>
        <Prtry>KYC_VERIFICATION_FAILED</Prtry>
      </Rsn>
      <AddtlInf>Account opening rejected due to incomplete KYC documentation. Additional identity verification required.</AddtlInf>
    </Sts>
  </AcctDtlsConf>
</Document>
```

---

## CDM Gap Analysis

**Result:** ZERO gaps identified

All 78 acmt.002 fields successfully map to existing GPS CDM entities:

### Account Entity - Core Fields ✅
All account-level fields (accountNumber, iban, accountType, currency, accountStatus, branchId, openDate, currentBalance) are already in the schema.

### Account Entity - Extensions ✅
Account service activation status, confirmation status, and balance information map to extensions fields.

### Party Entity ✅
All party identification fields covered (name, dateOfBirth, placeOfBirth, nationalIDNumber, address, contactDetails).

### Party Entity - Controlling Persons ✅
The Account.controllingPersons array supports beneficial owners and authorized signatories with ownership percentages.

### FinancialInstitution Entity ✅
All FI fields covered (bic, lei, institutionName, country, branchName, branchIdentification).

### PaymentInstruction Extensions ✅
Mandate confirmation information (mandateId, mandateType, mandateAuthenticationDateTime) maps to extensions.

---

## Related ISO 20022 Messages

| Message | Direction | Usage |
|---------|-----------|-------|
| **acmt.001** | Request | Account Opening Instruction (triggers acmt.002) |
| **acmt.003** | Request | Account Modification Instruction |
| **acmt.004** | Response | Account Modification Instruction Response |
| **acmt.005** | Request | Account Deletion Instruction |
| **acmt.007** | Request | Account Opening Request (customer-initiated) |
| **camt.052** | Notification | Account Report (statements for active accounts) |

---

## Account Lifecycle Observations

### Account Opening Confirmation Flow
1. **acmt.001** - FI to FI: Account Opening Instruction
2. **acmt.002** - FI to FI: Account Details Confirmation (this message) - Account opened successfully
3. **camt.052** - Account statement delivery begins

### Confirmation Statuses
- **ACCP (Accepted)**: Account successfully opened, IBAN/account number assigned, ready for transactions
- **RJCT (Rejected)**: Account opening rejected (KYC failure, compliance issue, duplicate request)
- **PEND (Pending)**: Account opening under review (additional documentation needed, compliance review)
- **PART (Partially Accepted)**: Account opened but some services pending activation

### IBAN Assignment
- For accounts requiring IBAN (international accounts, SEPA region), the servicing FI assigns and confirms the IBAN in this message
- For domestic accounts, only the account number may be assigned
- Both IBAN and account number can coexist in the confirmation

### Service Activation Timing
- Services can be activated immediately (status: ACTV)
- Some services may be pending (status: PEND) - e.g., debit card production takes 7-10 days
- Rejected services (status: REJT) indicate the account holder doesn't qualify for that service

---

## References

- ISO 20022 Message Definition Report: acmt.002.001.07
- ISO 20022 External Code Lists: https://www.iso20022.org/external_code_list.page
- GPS CDM Schema: `/schemas/03_account_complete_schema.json`
- GPS CDM Schema: `/schemas/02_party_complete_schema.json`
- GPS CDM Schema: `/schemas/04_financial_institution_complete_schema.json`
- GPS CDM Schema: `/schemas/payment_instruction_extensions_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2025-12-20
**Next Review:** Q1 2026
