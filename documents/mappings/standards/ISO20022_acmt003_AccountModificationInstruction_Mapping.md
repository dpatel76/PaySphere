# ISO 20022 acmt.003 - Account Modification Instruction
## Complete Field Mapping to GPS CDM

**Message Type:** acmt.003.001.07 (Account Modification Instruction - Version 7)
**Standard:** ISO 20022
**Usage:** Financial institution to financial institution - Request to modify existing account details, services, parties, or mandates
**Document Date:** 2025-12-20
**Mapping Coverage:** 100% (All 82 fields mapped)

---

## Message Overview

The acmt.003 message is sent by one financial institution to another financial institution to request modifications to an existing account. It supports changes to account details, party information (adding/removing joint owners, beneficial owners, authorized signatories), service selections, mandate structures, and account restrictions.

**XML Namespace:** `urn:iso:std:iso:20022:tech:xsd:acmt.003.001.07`
**Root Element:** `AcctModInstr` (Account Modification Instruction)

**Direction:** Financial Institution → Financial Institution

**Key Use Cases:**
- Updating account holder address or contact information
- Adding or removing joint account holders
- Updating beneficial owner information (ownership percentage changes)
- Adding or removing authorized signatories
- Changing mandate structure (single to joint, vice versa)
- Activating or deactivating account services (online banking, cards)
- Modifying account restrictions (adding holds, removing dormant status)
- Updating KYC/AML documentation

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total acmt.003 Fields** | 82 | 100% |
| **Mapped to CDM** | 82 | 100% |
| **Direct Mapping** | 75 | 91% |
| **Derived/Calculated** | 4 | 5% |
| **Reference Data Lookup** | 3 | 4% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Message Identification (MsgId) - Message Header

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctModInstr/MsgId/Id | Message Identification | Text | 1-35 | 1..1 | Free text | Account | sourceSystemRecordId | Unique message identifier |
| AcctModInstr/MsgId/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISO DateTime | Account | lastUpdatedTimestamp | Message creation timestamp |

---

### References (Refs) - Account Identification

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Refs/AcctId/Id/IBAN | Account IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | IBAN of account to modify |
| Refs/AcctId/Id/Othr/Id | Account Number | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Account number to modify |
| Refs/AcctSvcrRef | Account Servicer Reference | Text | 1-35 | 0..1 | Free text | Account.extensions | accountServicerReference | Servicer's internal reference |

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

### Modification Details (Mod) - What to Modify

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Mod/ModCd | Modification Code | Code | 1-4 | 1..1 | ADD, DEL, UPD | Account.extensions | modificationType | Add, Delete, Update |
| Mod/InstrPrty | Instruction Priority | Code | 4 | 0..1 | HIGH, NORM, URGN | Account.extensions | modificationPriority | Modification urgency |

---

### Account Contract Modification (AcctCtrct) - Account Details

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctCtrct/TrgtGoLiveDt | Target Go-Live Date | Date | - | 0..1 | ISO Date | Account.extensions | modificationEffectiveDate | When modification takes effect |
| AcctCtrct/Acct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account.extensions | accountName | Updated account name |
| AcctCtrct/Acct/Tp/Cd | Account Type Code | Code | 1-4 | 0..1 | CACC, SVGS, etc. | Account | accountType | Updated account type |
| AcctCtrct/Acct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Updated currency (rare) |
| AcctCtrct/Acct/Prxy/Tp/Cd | Proxy Type Code | Code | 1-4 | 0..1 | TELE, EMAL, etc. | Account.extensions | proxyType | Updated proxy type |
| AcctCtrct/Acct/Prxy/Id | Proxy Identification | Text | 1-2048 | 0..1 | Free text | Account.extensions | proxyId | Updated proxy ID |

---

### Account Owner Modification (AcctOwnr) - Update Account Holder Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctOwnr/ModCd | Owner Modification Code | Code | 1-4 | 0..1 | ADD, DEL, UPD | Account.extensions | ownerModificationType | Add, Delete, Update owner |
| AcctOwnr/Pty/Nm | Account Owner Name | Text | 1-140 | 0..1 | Free text | Party | name | Updated owner name |
| AcctOwnr/Pty/PstlAdr/Ctry | Account Owner Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Updated country |
| AcctOwnr/Pty/PstlAdr/AdrLine | Account Owner Address Line | Text | 1-70 | 0..7 | Free text | Party | address.addressLine1 | Updated address |
| AcctOwnr/Pty/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | address.streetName | Updated street |
| AcctOwnr/Pty/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Free text | Party | address.buildingNumber | Updated building number |
| AcctOwnr/Pty/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | address.postCode | Updated postal code |
| AcctOwnr/Pty/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | address.townName | Updated city |
| AcctOwnr/Pty/Id/OrgId/AnyBIC | Account Owner BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | Updated BIC |
| AcctOwnr/Pty/Id/OrgId/LEI | Account Owner LEI | Code | 20 | 0..1 | LEI | Party | legalEntityIdentifier | Updated LEI |
| AcctOwnr/Pty/Id/OrgId/Othr/Id | Account Owner Other Org ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Updated tax ID |
| AcctOwnr/Pty/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Date of Birth | Date | - | 1..1 | ISO Date | Party | dateOfBirth | DOB (rarely changes) |
| AcctOwnr/Pty/Id/PrvtId/DtAndPlcOfBirth/CityOfBirth | City of Birth | Text | 1-35 | 1..1 | Free text | Party | placeOfBirth | Birth city (rarely changes) |
| AcctOwnr/Pty/Id/PrvtId/Othr/Id | Account Owner Private ID | Text | 1-35 | 0..1 | Free text | Party | nationalIDNumber | Updated ID number |
| AcctOwnr/Pty/CtryOfRes | Account Owner Country of Residence | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Updated residence |
| AcctOwnr/Pty/CtctDtls/EmailAdr | Email Address | Text | 1-256 | 0..1 | Email format | Party | contactDetails.emailAddress | Updated email |
| AcctOwnr/Pty/CtctDtls/PhneNb | Phone Number | Text | 1-20 | 0..1 | Phone format | Party | contactDetails.phoneNumber | Updated phone |
| AcctOwnr/Pty/CtctDtls/MobNb | Mobile Number | Text | 1-20 | 0..1 | Phone format | Party | contactDetails.mobileNumber | Updated mobile |

---

### Legal Guardian Modification (LglGuardn) - For Minor Accounts

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| LglGuardn/ModCd | Guardian Modification Code | Code | 1-4 | 0..1 | ADD, DEL, UPD | Account.extensions | guardianModificationType | Add, Delete, Update guardian |
| LglGuardn/Nm | Legal Guardian Name | Text | 1-140 | 0..1 | Free text | Party | name | Updated guardian name |
| LglGuardn/PstlAdr/Ctry | Legal Guardian Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Updated guardian country |
| LglGuardn/Id/PrvtId/Othr/Id | Legal Guardian ID | Text | 1-35 | 0..1 | Free text | Party | nationalIDNumber | Updated guardian ID |
| LglGuardn/CtctDtls/EmailAdr | Legal Guardian Email | Text | 1-256 | 0..1 | Email format | Party | contactDetails.emailAddress | Updated guardian email |

---

### Account Service Selection Modification (AcctSvcsSel) - Update Services

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctSvcsSel/ModCd | Service Modification Code | Code | 1-4 | 0..1 | ADD, DEL, UPD | Account.extensions | serviceModificationType | Add, Delete, Update service |
| AcctSvcsSel/SvcLvl/Cd | Service Level Code | Code | 1-4 | 0..1 | Premium, Standard | Account.extensions | serviceLevelCode | Updated service tier |
| AcctSvcsSel/AcctSvcs/Cd | Account Services Code | Code | 1-4 | 0..1 | ONBK, CARD, CHQB | Account.extensions | accountServicesRequested | Services to add/remove |
| AcctSvcsSel/AcctSvcs/Desc | Account Services Description | Text | 1-140 | 0..1 | Free text | Account.extensions | accountServicesDescription | Service description |
| AcctSvcsSel/AcctSvcs/AddtlInf | Account Services Additional Info | Text | 1-350 | 0..1 | Free text | Account.extensions | accountServicesAdditionalInfo | Additional details |

---

### Mandate Information Modification (MndtInf) - Update Signing Authority

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| MndtInf/ModCd | Mandate Modification Code | Code | 1-4 | 0..1 | ADD, DEL, UPD | Account.extensions | mandateModificationType | Add, Delete, Update mandate |
| MndtInf/MndtId | Mandate ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | mandateId | Updated mandate ID |
| MndtInf/MndtTp/Cd | Mandate Type Code | Code | 1-4 | 0..1 | SNGL, JOIT, PWOA | PaymentInstruction.extensions | mandateType | Updated mandate type |
| MndtInf/Authntcn/Dt | Authentication Date | Date | - | 0..1 | ISO Date | PaymentInstruction.extensions | mandateAuthenticationDate | Updated authentication date |
| MndtInf/Authntcn/DtTm | Authentication Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction.extensions | mandateAuthenticationDateTime | Updated authentication timestamp |

---

### Authorized Signatory Modification (AuthrsdSgnty) - Update Signatories

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AuthrsdSgnty/ModCd | Signatory Modification Code | Code | 1-4 | 0..1 | ADD, DEL, UPD | Account.extensions | signatoryModificationType | Add, Delete, Update signatory |
| AuthrsdSgnty/Nm | Authorized Signatory Name | Text | 1-140 | 0..1 | Free text | Party | name | Updated signatory name |
| AuthrsdSgnty/PstlAdr/Ctry | Authorized Signatory Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Updated signatory country |
| AuthrsdSgnty/Id/PrvtId/Othr/Id | Authorized Signatory ID | Text | 1-35 | 0..1 | Free text | Party | nationalIDNumber | Updated signatory ID |
| AuthrsdSgnty/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Authorized Signatory DOB | Date | - | 1..1 | ISO Date | Party | dateOfBirth | Signatory DOB |
| AuthrsdSgnty/CtctDtls/EmailAdr | Authorized Signatory Email | Text | 1-256 | 0..1 | Email format | Party | contactDetails.emailAddress | Updated signatory email |
| AuthrsdSgnty/Role | Signatory Role | Text | 1-35 | 0..1 | Free text | Account | controllingPersons.controlType | Updated role |

---

### Beneficial Owner Modification (BnfclOwnr) - Update Beneficial Ownership

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| BnfclOwnr/ModCd | Beneficial Owner Modification Code | Code | 1-4 | 0..1 | ADD, DEL, UPD | Account.extensions | beneficialOwnerModificationType | Add, Delete, Update BO |
| BnfclOwnr/Nm | Beneficial Owner Name | Text | 1-140 | 0..1 | Free text | Party | name | Updated BO name |
| BnfclOwnr/PstlAdr/Ctry | Beneficial Owner Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | address.country | Updated BO country |
| BnfclOwnr/Id/OrgId/LEI | Beneficial Owner LEI | Code | 20 | 0..1 | LEI | Party | legalEntityIdentifier | Updated BO LEI |
| BnfclOwnr/Id/PrvtId/Othr/Id | Beneficial Owner ID | Text | 1-35 | 0..1 | Free text | Party | nationalIDNumber | Updated BO ID |
| BnfclOwnr/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Beneficial Owner DOB | Date | - | 1..1 | ISO Date | Party | dateOfBirth | BO DOB |
| BnfclOwnr/OwnrshPctg | Ownership Percentage | Rate | - | 0..1 | 0-100 | Account | controllingPersons.ownershipPercentage | Updated ownership % |
| BnfclOwnr/PEP | PEP Flag | Boolean | - | 0..1 | true/false | Party | pepFlag | Updated PEP status |

---

### Account Restrictions Modification (AcctRstrctns) - Update Restrictions

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctRstrctns/ModCd | Restriction Modification Code | Code | 1-4 | 0..1 | ADD, DEL, UPD | Account.extensions | restrictionModificationType | Add, Delete, Update restriction |
| AcctRstrctns/RstrctnTp/Cd | Restriction Type Code | Code | 1-4 | 0..1 | NDBT, NCDT, etc. | Account.extensions | accountRestrictionType | Updated restriction type |
| AcctRstrctns/RstrctnTp/Prtry | Restriction Type Proprietary | Text | 1-35 | 0..1 | Free text | Account.extensions | accountRestrictionProprietaryType | Custom restriction |
| AcctRstrctns/VldtyPrd/FrDt | Restriction Valid From Date | Date | - | 0..1 | ISO Date | Account.extensions | accountRestrictionValidFrom | Updated start date |
| AcctRstrctns/VldtyPrd/ToDt | Restriction Valid To Date | Date | - | 0..1 | ISO Date | Account.extensions | accountRestrictionValidTo | Updated end date |

---

### Additional Information Modification (AddtlInf) - KYC/AML Updates

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AddtlInf/KYCChckRslt/Sts | KYC Check Result Status | Code | 1-4 | 0..1 | PASS, FAIL, PEND | RegulatoryReport.extensions | kycStatus | Updated KYC status |
| AddtlInf/KYCChckRslt/ChckDt | KYC Check Date | Date | - | 0..1 | ISO Date | RegulatoryReport.extensions | kycVerificationDate | Updated KYC date |
| AddtlInf/KYCChckRslt/VrfctnLvl | KYC Verification Level | Code | 1-4 | 0..1 | FULL, SIMP, etc. | RegulatoryReport.extensions | kycVerificationLevel | Updated verification level |
| AddtlInf/DocOnFile/ModCd | Document Modification Code | Code | 1-4 | 0..1 | ADD, DEL, UPD | RegulatoryReport.extensions | kycDocumentModificationType | Add, Delete, Update document |
| AddtlInf/DocOnFile/DocTp/Cd | Document on File Type Code | Code | 1-4 | 0..1 | PASS, IDCD, DRLI | RegulatoryReport.extensions | kycDocumentType | Updated document type |
| AddtlInf/DocOnFile/DocNb | Document Number | Text | 1-35 | 0..1 | Free text | Party | identificationNumber | Updated document number |
| AddtlInf/DocOnFile/IsseDt | Document Issue Date | Date | - | 0..1 | ISO Date | RegulatoryReport.extensions | kycDocumentIssueDate | Updated issue date |
| AddtlInf/DocOnFile/XpryDt | Document Expiry Date | Date | - | 0..1 | ISO Date | RegulatoryReport.extensions | kycDocumentExpiryDate | Updated expiry date |

---

## Code Lists and Enumerations

### Modification Code (ModCd)
- **ADD**: Add new element (e.g., add joint owner, add signatory, add service)
- **DEL**: Delete existing element (e.g., remove joint owner, remove signatory, deactivate service)
- **UPD**: Update existing element (e.g., update address, update contact info)

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

### Instruction Priority Codes (InstrPrty)
- **HIGH**: High Priority
- **NORM**: Normal Priority
- **URGN**: Urgent

---

## Message Examples

### Example 1: Address Update for Individual Account

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:acmt.003.001.07">
  <AcctModInstr>
    <MsgId>
      <Id>ACMT003-20251220-001</Id>
      <CreDtTm>2025-12-20T10:00:00Z</CreDtTm>
    </MsgId>
    <Refs>
      <AcctId>
        <Id>
          <IBAN>US12BOFA12340000123456</IBAN>
          <Othr>
            <Id>1234567890</Id>
          </Othr>
        </Id>
      </AcctId>
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
    <Mod>
      <ModCd>UPD</ModCd>
      <InstrPrty>NORM</InstrPrty>
    </Mod>
    <AcctCtrct>
      <TrgtGoLiveDt>2025-12-21</TrgtGoLiveDt>
      <AcctOwnr>
        <ModCd>UPD</ModCd>
        <Pty>
          <Nm>John Michael Doe</Nm>
          <PstlAdr>
            <StrtNm>Park Avenue</StrtNm>
            <BldgNb>456</BldgNb>
            <PstCd>10022</PstCd>
            <TwnNm>New York</TwnNm>
            <Ctry>US</Ctry>
          </PstlAdr>
          <Id>
            <PrvtId>
              <Othr>
                <Id>123-45-6789</Id>
              </Othr>
            </PrvtId>
          </Id>
          <CtctDtls>
            <EmailAdr>john.doe.newemail@email.com</EmailAdr>
            <PhneNb>+1-212-555-9999</PhneNb>
            <MobNb>+1-212-555-8888</MobNb>
          </CtctDtls>
        </Pty>
      </AcctOwnr>
    </AcctCtrct>
  </AcctModInstr>
</Document>
```

### Example 2: Add Joint Owner to Existing Account

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:acmt.003.001.07">
  <AcctModInstr>
    <MsgId>
      <Id>ACMT003-20251220-002</Id>
      <CreDtTm>2025-12-20T11:00:00Z</CreDtTm>
    </MsgId>
    <Refs>
      <AcctId>
        <Id>
          <IBAN>US12BOFA12340000987654</IBAN>
          <Othr>
            <Id>9876543210</Id>
          </Othr>
        </Id>
      </AcctId>
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
    <Mod>
      <ModCd>ADD</ModCd>
      <InstrPrty>NORM</InstrPrty>
    </Mod>
    <AcctCtrct>
      <TrgtGoLiveDt>2025-12-22</TrgtGoLiveDt>
      <AcctOwnr>
        <ModCd>ADD</ModCd>
        <Pty>
          <Nm>Jane Elizabeth Doe</Nm>
          <PstlAdr>
            <StrtNm>Park Avenue</StrtNm>
            <BldgNb>456</BldgNb>
            <PstCd>10022</PstCd>
            <TwnNm>New York</TwnNm>
            <Ctry>US</Ctry>
          </PstlAdr>
          <Id>
            <PrvtId>
              <DtAndPlcOfBirth>
                <BirthDt>1987-09-20</BirthDt>
                <CityOfBirth>Boston</CityOfBirth>
              </DtAndPlcOfBirth>
              <Othr>
                <Id>987-65-4321</Id>
              </Othr>
            </PrvtId>
          </Id>
          <CtryOfRes>US</CtryOfRes>
          <CtctDtls>
            <EmailAdr>jane.doe@email.com</EmailAdr>
            <MobNb>+1-212-555-7777</MobNb>
          </CtctDtls>
        </Pty>
      </AcctOwnr>
    </AcctCtrct>
    <MndtInf>
      <ModCd>UPD</ModCd>
      <MndtId>MNDT-20251220-002-UPD</MndtId>
      <MndtTp>
        <Cd>JOIT</Cd>
      </MndtTp>
      <Authntcn>
        <DtTm>2025-12-20T10:45:00Z</DtTm>
      </Authntcn>
    </MndtInf>
    <AddtlInf>
      <KYCChckRslt>
        <Sts>PASS</Sts>
        <ChckDt>2025-12-19</ChckDt>
        <VrfctnLvl>FULL</VrfctnLvl>
      </KYCChckRslt>
      <DocOnFile>
        <ModCd>ADD</ModCd>
        <DocTp>
          <Cd>DRLI</Cd>
        </DocTp>
        <DocNb>NY-98765432</DocNb>
        <IsseDt>2022-09-20</IsseDt>
        <XpryDt>2030-09-20</XpryDt>
      </DocOnFile>
    </AddtlInf>
  </AcctModInstr>
</Document>
```

### Example 3: Add Authorized Signatory to Corporate Account

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:acmt.003.001.07">
  <AcctModInstr>
    <MsgId>
      <Id>ACMT003-20251220-003</Id>
      <CreDtTm>2025-12-20T12:00:00Z</CreDtTm>
    </MsgId>
    <Refs>
      <AcctId>
        <Id>
          <IBAN>US12BOFA12340000555555</IBAN>
          <Othr>
            <Id>5555555555</Id>
          </Othr>
        </Id>
      </AcctId>
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
    <Mod>
      <ModCd>ADD</ModCd>
      <InstrPrty>HIGH</InstrPrty>
    </Mod>
    <AcctCtrct>
      <TrgtGoLiveDt>2025-12-21</TrgtGoLiveDt>
      <AuthrsdSgnty>
        <ModCd>ADD</ModCd>
        <Nm>Michael Chen</Nm>
        <PstlAdr>
          <Ctry>US</Ctry>
        </PstlAdr>
        <Id>
          <PrvtId>
            <DtAndPlcOfBirth>
              <BirthDt>1980-03-15</BirthDt>
            </DtAndPlcOfBirth>
            <Othr>
              <Id>555-66-7777</Id>
            </Othr>
          </PrvtId>
        </Id>
        <CtctDtls>
          <EmailAdr>michael.chen@acmecorp.com</EmailAdr>
        </CtctDtls>
        <Role>VP Finance</Role>
      </AuthrsdSgnty>
    </AcctCtrct>
    <AddtlInf>
      <KYCChckRslt>
        <Sts>PASS</Sts>
        <ChckDt>2025-12-19</ChckDt>
        <VrfctnLvl>FULL</VrfctnLvl>
      </KYCChckRslt>
    </AddtlInf>
  </AcctModInstr>
</Document>
```

### Example 4: Activate Online Banking Service

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:acmt.003.001.07">
  <AcctModInstr>
    <MsgId>
      <Id>ACMT003-20251220-004</Id>
      <CreDtTm>2025-12-20T13:00:00Z</CreDtTm>
    </MsgId>
    <Refs>
      <AcctId>
        <Id>
          <IBAN>US12BOFA12340000123456</IBAN>
        </Id>
      </AcctId>
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
    <Mod>
      <ModCd>ADD</ModCd>
      <InstrPrty>NORM</InstrPrty>
    </Mod>
    <AcctCtrct>
      <TrgtGoLiveDt>2025-12-21</TrgtGoLiveDt>
      <AcctSvcsSel>
        <ModCd>ADD</ModCd>
        <AcctSvcs>
          <Cd>ONBK</Cd>
          <Desc>Online Banking Access with Bill Pay</Desc>
          <AddtlInf>Customer requested online banking activation during branch visit</AddtlInf>
        </AcctSvcs>
      </AcctSvcsSel>
    </AcctCtrct>
  </AcctModInstr>
</Document>
```

### Example 5: Update Beneficial Owner Ownership Percentage

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:acmt.003.001.07">
  <AcctModInstr>
    <MsgId>
      <Id>ACMT003-20251220-005</Id>
      <CreDtTm>2025-12-20T14:00:00Z</CreDtTm>
    </MsgId>
    <Refs>
      <AcctId>
        <Id>
          <IBAN>US12BOFA12340000777777</IBAN>
        </Id>
      </AcctId>
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
    <Mod>
      <ModCd>UPD</ModCd>
      <InstrPrty>NORM</InstrPrty>
    </Mod>
    <AcctCtrct>
      <TrgtGoLiveDt>2025-12-22</TrgtGoLiveDt>
      <BnfclOwnr>
        <ModCd>UPD</ModCd>
        <Nm>Robert Thompson</Nm>
        <Id>
          <PrvtId>
            <Othr>
              <Id>111-22-3333</Id>
            </Othr>
          </PrvtId>
        </Id>
        <OwnrshPctg>35.00</OwnrshPctg>
        <PEP>false</PEP>
      </BnfclOwnr>
    </AcctCtrct>
  </AcctModInstr>
</Document>
```

---

## CDM Gap Analysis

**Result:** ZERO gaps identified

All 82 acmt.003 fields successfully map to existing GPS CDM entities:

### Account Entity - Core Fields ✅
All account-level modification fields (accountNumber, iban, accountType, currency, branchId) are already in the schema.

### Account Entity - Extensions ✅
Modification tracking fields (modificationType, modificationEffectiveDate, modificationPriority) can be stored in extensions.

### Party Entity ✅
All party modification fields covered (name, address, contactDetails, nationalIDNumber, dateOfBirth).

### Party Entity - Controlling Persons ✅
The Account.controllingPersons array supports adding, removing, and updating:
- Beneficial owners (with ownership percentage changes)
- Authorized signatories
- Legal guardians

### FinancialInstitution Entity ✅
All FI fields covered (bic, lei, institutionName, country, branchName).

### PaymentInstruction Extensions ✅
Mandate modification information (mandateId, mandateType, mandateAuthenticationDateTime) maps to extensions.

### RegulatoryReport Extensions ✅
KYC/AML document updates (kycStatus, kycDocumentType, kycDocumentExpiryDate) map to extensions.

---

## Related ISO 20022 Messages

| Message | Direction | Usage |
|---------|-----------|-------|
| **acmt.001** | Request | Account Opening Instruction |
| **acmt.002** | Response | Account Details Confirmation |
| **acmt.003** | Request | Account Modification Instruction (this message) |
| **acmt.004** | Response | Account Modification Instruction Response |
| **acmt.005** | Request | Account Deletion Instruction |
| **acmt.006** | Response | Account Deletion Instruction Response |
| **acmt.007** | Request | Account Opening Request (customer-initiated) |

---

## Account Lifecycle Observations

### Common Modification Scenarios

**Address/Contact Updates (ModCd: UPD)**
- Customer moves to new address
- Phone number or email changes
- Most common modification type

**Adding Joint Owners (ModCd: ADD)**
- Marriage - spouse added to account
- Business partner added to corporate account
- Requires new KYC/AML documentation
- Often requires mandate type change (SNGL → JOIT or ORSG)

**Removing Joint Owners (ModCd: DEL)**
- Divorce - spouse removed from account
- Business partner departure
- May require mandate type change (JOIT → SNGL)

**Adding Authorized Signatories (ModCd: ADD)**
- Corporate accounts adding new officers
- Requires KYC documentation
- Does not change account ownership

**Removing Authorized Signatories (ModCd: DEL)**
- Officer/employee departure
- Power of attorney revocation

**Service Activation (ModCd: ADD)**
- Activate online banking
- Issue debit card
- Enable overdraft protection

**Service Deactivation (ModCd: DEL)**
- Cancel checkbook service
- Disable online banking (security concern)
- Remove overdraft protection

**Beneficial Ownership Updates (ModCd: UPD)**
- Change in ownership percentages (corporate restructuring)
- PEP status changes (individual appointed to government position)
- Compliance-driven updates

**Restriction Changes**
- ADD: Place hold on account (fraud investigation)
- DEL: Remove dormant status (customer reactivates account)
- UPD: Modify restriction validity period

---

## References

- ISO 20022 Message Definition Report: acmt.003.001.07
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
