# FinCEN 314(b) - Information Sharing Notice
## Complete Field Mapping to GPS CDM

**Report Type:** USA PATRIOT Act Section 314(b) Information Sharing Notice
**Regulatory Authority:** Financial Crimes Enforcement Network (FinCEN), U.S. Department of Treasury
**Purpose:** Voluntary information sharing between financial institutions on suspected money laundering or terrorist activity
**Filing Method:** FinCEN 314(b) Registration Portal (one-time registration)
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 38 fields mapped)

---

## Report Overview

Section 314(b) of the USA PATRIOT Act permits financial institutions to share information with each other regarding individuals, entities, organizations, and countries suspected of possible terrorist activity or money laundering. This is a **voluntary** information sharing program that requires one-time registration with FinCEN.

**Regulation:** 31 USC 5318(g)(3), 31 CFR 1010.540
**Registration Required:** One-time filing with FinCEN
**Renewal:** Annual confirmation of participation
**Safe Harbor:** Liability protection for good faith sharing

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total 314(b) Fields** | 38 | 100% |
| **Mapped to CDM** | 38 | 100% |
| **Direct Mapping** | 33 | 87% |
| **Derived/Calculated** | 4 | 10% |
| **Reference Data Lookup** | 1 | 3% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Part I: Registering Institution Information (Items 1-12)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | Legal name of financial institution | Text | 150 | Yes | Free text | FinancialInstitution | institutionName | Legal name |
| 2 | Type of financial institution | Code | 2 | Yes | See FI type codes | FinancialInstitution | institutionType | Bank, broker-dealer, MSB, etc. |
| 3 | Employer Identification Number (EIN) | Text | 9 | Yes | 9 digits | FinancialInstitution | taxIdentificationNumber | FI's EIN (no dashes) |
| 4 | RSSD number (if applicable) | Text | 10 | No | 10 digits | FinancialInstitution | rssdNumber | Federal Reserve RSSD ID |
| 5 | Primary federal regulator | Code | 1 | Yes | 1-9 | FinancialInstitution | primaryRegulator | OCC, FDIC, FRB, etc. |
| 6 | Street address | Text | 100 | Yes | Free text | FinancialInstitution | address.addressLine1 | Street address |
| 7 | City | Text | 50 | Yes | Free text | FinancialInstitution | address.city | City |
| 8 | State | Code | 2 | Yes | US state code | FinancialInstitution | address.state | State abbreviation |
| 9 | ZIP code | Text | 9 | Yes | XXXXX or XXXXX-XXXX | FinancialInstitution | address.postalCode | ZIP code |
| 10 | Country | Code | 2 | No | ISO 3166-1 alpha-2 | FinancialInstitution | address.country | Country (US default) |
| 11 | Institution phone number | Text | 16 | Yes | Phone format | FinancialInstitution | phoneNumber | Main phone |
| 12 | Institution website | Text | 200 | No | URL | FinancialInstitution | websiteUrl | Website URL |

---

### Part II: BSA Compliance Contact Information (Items 13-20)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 13 | BSA officer name | Text | 100 | Yes | Free text | FinancialInstitution | bsaOfficerName | BSA/AML officer |
| 14 | BSA officer title | Text | 50 | Yes | Free text | FinancialInstitution | bsaOfficerTitle | Job title |
| 15 | BSA officer email | Text | 100 | Yes | Email | FinancialInstitution | bsaOfficerEmail | Contact email |
| 16 | BSA officer phone | Text | 16 | Yes | Phone format | FinancialInstitution | bsaOfficerPhone | Contact phone |
| 17 | BSA officer phone extension | Text | 6 | No | Numeric | FinancialInstitution | bsaOfficerPhoneExt | Extension |
| 18 | Alternate contact name | Text | 100 | No | Free text | FinancialInstitution | alternateContactName | Backup contact |
| 19 | Alternate contact email | Text | 100 | No | Email | FinancialInstitution | alternateContactEmail | Backup email |
| 20 | Alternate contact phone | Text | 16 | No | Phone format | FinancialInstitution | alternateContactPhone | Backup phone |

---

### Part III: Registration Details (Items 21-28)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 21 | Registration date | Date | 8 | Yes | MMDDYYYY | RegulatoryReport | registrationDate | Initial registration date |
| 22 | Registration type | Code | 1 | Yes | I, R, A | RegulatoryReport | registrationType | I=Initial, R=Renewal, A=Amendment |
| 23 | Prior registration ID | Text | 20 | Cond | Alphanumeric | RegulatoryReport | priorRegistrationId | Required if renewal/amendment |
| 24 | Registration ID | Text | 20 | System | Alphanumeric | RegulatoryReport | reportReferenceNumber | Assigned by FinCEN |
| 25 | Effective date | Date | 8 | System | MMDDYYYY | RegulatoryReport | effectiveDate | When registration becomes active |
| 26 | Expiration date | Date | 8 | System | MMDDYYYY | RegulatoryReport | expirationDate | Annual renewal required |
| 27 | Participation status | Code | 1 | System | A, I, E | RegulatoryReport | participationStatus | A=Active, I=Inactive, E=Expired |
| 28 | Annual confirmation date | Date | 8 | System | MMDDYYYY | RegulatoryReport | annualConfirmationDate | Last annual confirmation |

---

### Part IV: Information Sharing Request/Response (Items 29-38)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 29 | Sharing request ID | Text | 20 | Yes | Alphanumeric | RegulatoryReport | sharingRequestId | Unique sharing request ID |
| 30 | Requesting institution name | Text | 150 | Yes | Free text | FinancialInstitution | requestingInstitutionName | FI requesting information |
| 31 | Requesting institution EIN | Text | 9 | Yes | 9 digits | FinancialInstitution | requestingInstitutionEIN | Requesting FI's EIN |
| 32 | Request date | Date | 8 | Yes | MMDDYYYY | RegulatoryReport | requestDate | Date of information request |
| 33 | Subject of inquiry | Text | 150 | Yes | Free text | Party | name | Person/entity being inquired about |
| 34 | Subject TIN (if known) | Text | 9 | No | 9 digits | Party | taxId | SSN or EIN if available |
| 35 | Reason for inquiry | Text | 1000 | Yes | Free text | ComplianceCase | reasonForInquiry | Why information is being requested |
| 36 | Response institution name | Text | 150 | Yes | Free text | FinancialInstitution | respondingInstitutionName | FI responding to request |
| 37 | Response date | Date | 8 | Yes | MMDDYYYY | RegulatoryReport | submissionDate | Date response provided |
| 38 | Information shared indicator | Checkbox | 1 | Yes | Y/N | RegulatoryReport | informationShared | Was information provided |

---

## CDM Extensions Required

All 38 Section 314(b) fields successfully map to existing CDM model. **No enhancements required.**

### RegulatoryReport Entity - Core Fields
✅ All core 314(b) fields mapped (reportType, reportReferenceNumber, registrationDate, etc.)

### RegulatoryReport Entity - Extensions
✅ 314(b)-specific fields already in schema:
- registrationType
- priorRegistrationId
- effectiveDate
- expirationDate
- participationStatus
- annualConfirmationDate
- sharingRequestId
- requestDate
- informationShared

### FinancialInstitution Entity
✅ All FI fields covered:
- institutionName, institutionType
- taxIdentificationNumber, rssdNumber
- primaryRegulator
- address fields
- phoneNumber, websiteUrl
- bsaOfficerName, bsaOfficerTitle, bsaOfficerEmail, bsaOfficerPhone
- alternateContactName, alternateContactEmail, alternateContactPhone
- requestingInstitutionName, requestingInstitutionEIN
- respondingInstitutionName

### Party Entity
✅ All subject fields covered:
- name, taxId

### ComplianceCase Entity
✅ All inquiry fields covered:
- reasonForInquiry

---

## No CDM Gaps Identified ✅

All 38 FinCEN 314(b) fields successfully map to existing CDM model. No enhancements required.

---

## Code Lists and Valid Values

### Financial Institution Type Codes (Item 2)
| Code | Description |
|------|-------------|
| 01 | Depository institution (bank or thrift) |
| 02 | Broker or dealer in securities |
| 03 | Money services business |
| 04 | Insurance company |
| 05 | Futures commission merchant |
| 06 | Introducing broker in commodities |
| 07 | Mutual fund |
| 08 | Casino or card club |
| 99 | Other |

### Primary Federal Regulator Codes (Item 5)
| Code | Description |
|------|-------------|
| 1 | Office of the Comptroller of the Currency (OCC) |
| 2 | Federal Deposit Insurance Corporation (FDIC) |
| 3 | Board of Governors of the Federal Reserve System (FRB) |
| 4 | National Credit Union Administration (NCUA) |
| 5 | Financial institution does not have a Federal regulator |
| 6 | Internal Revenue Service (IRS) |
| 7 | Securities and Exchange Commission (SEC) |
| 8 | Commodity Futures Trading Commission (CFTC) |
| 9 | Other |

### Registration Type Codes (Item 22)
| Code | Description |
|------|-------------|
| I | Initial registration |
| R | Annual renewal |
| A | Amendment to existing registration |

### Participation Status Codes (Item 27)
| Code | Description |
|------|-------------|
| A | Active - currently participating |
| I | Inactive - registration suspended |
| E | Expired - renewal required |

---

## JSON Structure Example

### Registration Filing

```json
{
  "registration": {
    "registrationType": "I",
    "registrationDate": "2024-12-20",
    "institution": {
      "legalName": "First National Bank",
      "institutionType": "01",
      "ein": "123456789",
      "rssdNumber": "1234567890",
      "primaryRegulator": "1",
      "address": {
        "street": "100 Main Street",
        "city": "New York",
        "state": "NY",
        "zip": "10001",
        "country": "US"
      },
      "phone": "(212) 555-1000",
      "website": "www.firstnationalbank.com"
    },
    "bsaContact": {
      "name": "Jennifer Martinez",
      "title": "BSA/AML Officer",
      "email": "jennifer.martinez@fnb.com",
      "phone": "(212) 555-1001",
      "extension": "2345"
    },
    "alternateContact": {
      "name": "Robert Chen",
      "email": "robert.chen@fnb.com",
      "phone": "(212) 555-1002"
    }
  },
  "systemFields": {
    "registrationId": "314B-REG-2024-00123",
    "effectiveDate": "2024-12-21",
    "expirationDate": "2025-12-20",
    "participationStatus": "A"
  }
}
```

### Information Sharing Request

```json
{
  "sharingRequest": {
    "requestId": "314B-REQ-2024-1220-456",
    "requestingInstitution": {
      "name": "Second National Bank",
      "ein": "987654321"
    },
    "requestDate": "2024-12-20",
    "subject": {
      "name": "Acme Trading LLC",
      "tin": "555666777"
    },
    "reasonForInquiry": "We received a large wire transfer ($2.5M) from this entity with unclear business purpose. The entity opened an account at our institution last month and immediately requested international wire transfers to high-risk jurisdictions. We suspect possible trade-based money laundering. Requesting information on account history, transaction patterns, and any prior suspicious activity reporting.",
    "respondingInstitution": {
      "name": "First National Bank"
    },
    "responseDate": "2024-12-22",
    "informationShared": true,
    "responseSummary": "Acme Trading LLC maintained business checking account 2019-2024. Account closed due to suspicious activity patterns including structured deposits and high-volume international wires to shell companies. Two SARs filed (BSA IDs: 12345678901234, 12345678901235). Subject also used multiple DBA names. Detailed records available upon subpoena."
  }
}
```

---

## 314(b) Information Sharing Process

### Step 1: Initial Registration (One-Time)
1. Financial institution submits 314(b) registration to FinCEN
2. FinCEN reviews and approves registration
3. Institution receives Registration ID
4. Registration becomes effective
5. Institution added to 314(b) participant list

### Step 2: Annual Renewal
- **Deadline:** Annually on anniversary of registration
- **Process:** Confirm continued participation via FinCEN portal
- **Update:** Provide any changes to contact information
- **Renewal:** Registration auto-expires if not renewed

### Step 3: Information Sharing Between FIs
1. **Requesting FI:** Identifies need to share information (e.g., SAR filed, suspicious customer)
2. **Contact Registered FI:** Reach out to another 314(b) registered institution
3. **Verification:** Both parties verify 314(b) registration status
4. **Share Information:** Exchange relevant information on suspected money laundering/terrorism
5. **Document:** Maintain records of information shared

### Step 4: Record Retention
- **Retain for 5 years:** All 314(b) information requests and responses
- **Document:** Who shared, what was shared, when, why
- **Audit Trail:** Compliance tracking

---

## Permitted Information Sharing

### What Can Be Shared
- Customer/account identification information
- Transaction patterns and history
- Suspicious activity information
- SAR filing history (that SAR was filed, not SAR itself)
- Account relationship details
- Know Your Customer (KYC) information
- Due diligence findings

### What Information Is Covered
Information must relate to:
- **Money laundering activities**
- **Terrorist financing**
- Transactions, accounts, or customers suspected of involvement in illegal activity

### Scope Limitations
- Information sharing must be for **BSA/AML purposes only**
- Cannot be used for competitive purposes
- Cannot be shared with non-314(b) participants
- Subject to safe harbor protections

---

## Safe Harbor Protections

### Liability Protection
Financial institutions that share information under 314(b) receive **safe harbor** from liability for:
- Civil liability for good faith disclosures
- Disclosure of customer information
- Breach of privacy claims

### Requirements for Safe Harbor
1. Both institutions must be registered under 314(b)
2. Information shared relates to possible money laundering or terrorist activity
3. Disclosure made in good faith
4. Information sharing documented

### Exclusions from Safe Harbor
- Bad faith disclosures
- Gross negligence
- Intentional misconduct
- Sharing for non-BSA/AML purposes

---

## Confidentiality Requirements

### Prohibition on Disclosure
- **NO disclosure to subject:** Do not notify customers that information about them was shared
- **"Tipping off" violations:** Criminal penalties apply
- **Internal use only:** Information used for BSA/AML compliance purposes only

### Permitted Disclosures
- Between 314(b) registered institutions
- To FinCEN or regulators
- To law enforcement pursuant to legal process
- Within institution on need-to-know basis

### Prohibited Disclosures
- To the subject of the inquiry
- To non-registered financial institutions
- For marketing or business development purposes
- To the public or media

---

## Comparison: 314(a) vs. 314(b)

| Feature | 314(a) | 314(b) |
|---------|--------|--------|
| **Purpose** | LE request for information | FI-to-FI information sharing |
| **Participation** | Mandatory for all FIs | Voluntary - registration required |
| **Direction** | Government to FI | FI to FI |
| **Initiator** | Law enforcement via FinCEN | Financial institution |
| **Frequency** | Biweekly (FinCEN distributions) | Ongoing as needed |
| **Response time** | 14 days | Not specified |
| **Registration** | None required (automatic) | One-time registration with FinCEN |
| **Safe harbor** | Not applicable | Yes - liability protection |
| **Renewal** | N/A | Annual confirmation |

---

## Best Practices for 314(b) Participation

### 1. Registration Management
- Designate BSA officer as primary contact
- Maintain current contact information
- Set calendar reminder for annual renewal
- Document registration and renewal dates

### 2. Information Request Protocols
- Verify recipient is 314(b) registered before sharing
- Use secure communication channels (encrypted email, secure portal)
- Document all requests and responses
- Limit sharing to need-to-know staff

### 3. Documentation Requirements
- Maintain log of all 314(b) requests sent
- Maintain log of all 314(b) responses received
- Document reason for each information request
- Retain records for 5 years

### 4. Training and Procedures
- Train BSA/AML staff on 314(b) procedures
- Create internal policies for 314(b) sharing
- Establish escalation procedures
- Conduct periodic audits

### 5. Coordination with SAR Filing
- Consider 314(b) sharing when unusual activity detected
- Use 314(b) to gather additional information before SAR filing
- Share information after SAR filed (do not delay SAR)
- Reference 314(b) sharing in SAR narrative if relevant

---

## Common Use Cases

### Scenario 1: Account Opening Red Flags
Bank A receives account opening application from business with vague purpose. Bank A contacts Bank B (where business previously banked) via 314(b) to inquire about prior relationship and any concerns.

### Scenario 2: Large Wire Transfer
Bank A receives incoming wire for $5M from foreign entity to new customer. Bank A contacts Bank B (correspondent bank) via 314(b) to inquire about sending party's history and transaction patterns.

### Scenario 3: Structuring Suspected
Bank A detects customer making structured deposits just under $10,000. Customer claims they also bank at Bank B. Bank A contacts Bank B via 314(b) to determine if similar patterns observed.

### Scenario 4: Post-SAR Investigation
Bank A files SAR on customer for suspected money laundering. Bank A learns customer has accounts at Bank B and Bank C. Bank A contacts both via 314(b) to share concerns and gather additional intelligence.

---

## Record Retention Requirements

### Registration Records
- Initial registration filing: **5 years** from registration
- Annual renewal confirmations: **5 years** from renewal
- Amendment filings: **5 years** from amendment

### Information Sharing Records
- All 314(b) requests sent: **5 years** from request
- All 314(b) responses received: **5 years** from response
- Supporting documentation: **5 years** from sharing
- Log of information shared: **5 years** from sharing

### Audit Documentation
- Internal audit reports: **5 years**
- Policy and procedure documents: Current + **5 years**
- Training materials and attendance: **5 years**

---

## Penalties and Enforcement

### Registration Violations
- Failure to register: Loss of safe harbor protection
- Failure to renew: Expiration of registration
- Sharing without registration: No liability protection

### Confidentiality Violations
- "Tipping off" subject: Criminal penalties up to $250,000 and/or 5 years
- Unauthorized disclosure: Civil and criminal penalties
- Use for non-BSA purposes: Regulatory sanctions

### Regulatory Actions
- Consent orders for program deficiencies
- Civil money penalties
- Restrictions on information sharing
- Enhanced monitoring

---

## References

- FinCEN 314(b) Fact Sheet: https://www.fincen.gov/resources/statutes-and-regulations/usa-patriot-act/314b-fact-sheet
- USA PATRIOT Act Section 314(b): 31 USC 5318(g)(3)
- Regulation: 31 CFR 1010.540
- FinCEN 314(b) Registration Portal: https://314b.fincen.treas.gov
- Safe Harbor Guidance: https://www.fincen.gov/resources/statutes-and-regulations/guidance/safe-harbor-information-sharing
- BSA/AML Examination Manual: https://bsaaml.ffiec.gov/manual
- GPS CDM Schemas: `/schemas/05_regulatory_report_complete_schema.json`, `/schemas/06_compliance_case_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
