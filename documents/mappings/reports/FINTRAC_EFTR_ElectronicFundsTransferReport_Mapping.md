# FINTRAC EFTR - Electronic Funds Transfer Report
## Complete Field Mapping to GPS CDM

**Report Type:** Electronic Funds Transfer Report (EFTR)
**Regulatory Authority:** FINTRAC (Financial Transactions and Reports Analysis Centre of Canada)
**Filing Requirement:** Report all international electronic funds transfers of CAD $10,000 or more
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 88 fields mapped)

---

## Report Overview

The EFTR is required under the Proceeds of Crime (Money Laundering) and Terrorist Financing Act (PCMLTFA). Reporting entities must submit an EFTR for every international electronic funds transfer they initiate, send, receive, or process on behalf of a client of CAD $10,000 or more.

**Filing Threshold:** CAD $10,000 or more (or foreign currency equivalent)
**Filing Deadline:** Within 5 working days after the transfer occurs
**Filing Method:** FINTRAC Web Reporting System (F2R) or batch file upload
**Regulation:** PCMLTFA, PCMLTFR (Regulations)

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total EFTR Fields** | 88 | 100% |
| **Mapped to CDM** | 88 | 100% |
| **Direct Mapping** | 80 | 91% |
| **Derived/Calculated** | 6 | 7% |
| **Reference Data Lookup** | 2 | 2% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Part A - Reporting Entity Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| A1 | Reporting entity report reference number | Text | 50 | Yes | Free text | RegulatoryReport | reportingEntityReferenceNumber | Internal reference |
| A2 | Reporting entity number | Text | 7 | Yes | 7 digits | FinancialInstitution | fintracReportingEntityNumber | FINTRAC assigned |
| A3 | Reporting entity legal name | Text | 300 | Yes | Free text | FinancialInstitution | institutionName | Legal entity name |
| A4 | Reporting entity business activity | Code | 2 | Yes | See activity codes | FinancialInstitution | businessActivity | Type of business |
| A5 | Contact person name | Text | 200 | Yes | Free text | RegulatoryReport | contactPersonName | Contact for report |
| A6 | Contact person phone | Text | 20 | Yes | Phone format | RegulatoryReport | contactPersonPhone | Contact phone |
| A7 | Contact person email | Text | 100 | No | Email format | RegulatoryReport | contactPersonEmail | Contact email |

### Part B - Location Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| B1 | Location type | Code | 1 | Yes | B=Branch, O=Office, M=Mobile | FinancialInstitution | locationType | Location type |
| B2 | Branch/office name | Text | 200 | No | Free text | FinancialInstitution | branchName | Branch/office name |
| B3 | Street address | Text | 200 | Yes | Free text | FinancialInstitution | branchStreetAddress | Street address |
| B4 | City | Text | 100 | Yes | Free text | FinancialInstitution | branchCity | City |
| B5 | Province/Territory | Code | 2 | Yes | ON, QC, BC, etc. | FinancialInstitution | branchProvince | Province code |
| B6 | Postal code | Text | 7 | Yes | A1A 1A1 format | FinancialInstitution | branchPostalCode | Postal code |
| B7 | Country | Code | 2 | Yes | CA | FinancialInstitution | branchCountry | Always CA |

### Part C - Transfer Information

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| C1 | Transfer direction | Code | 1 | Yes | I=Incoming, O=Outgoing | PaymentInstruction | transferDirection | Direction of transfer |
| C2 | Transfer date | Date | 10 | Yes | YYYY-MM-DD | PaymentInstruction | valueDate | Date of transfer |
| C3 | Transfer time | Time | 8 | No | HH:MM:SS | PaymentInstruction | executionTime | Time of transfer |
| C4 | Transfer amount (CAD) | Decimal | 15,2 | Yes | Numeric >= 10000 | PaymentInstruction | transferAmountCad | Amount in CAD |
| C5 | Transfer amount (foreign currency) | Decimal | 15,2 | No | Numeric | PaymentInstruction | instructedAmount.amount | Amount in foreign currency |
| C6 | Foreign currency code | Code | 3 | Cond | ISO 4217 | PaymentInstruction | instructedAmount.currency | ISO currency code |
| C7 | Exchange rate | Decimal | 10,6 | No | Numeric | PaymentInstruction | exchangeRate | Rate applied |
| C8 | Transfer type | Code | 2 | Yes | See transfer type codes | PaymentInstruction | transferType | SWIFT, wire, etc. |
| C9 | Unique transaction reference | Text | 50 | No | Free text | PaymentInstruction | endToEndId | Transaction reference |
| C10 | 24-hour rule indicator | Boolean | 1 | Yes | Y/N | PaymentInstruction | twentyFourHourRuleIndicator | Multiple related transfers |
| C11 | Ministerial directive indicator | Boolean | 1 | Yes | Y/N | PaymentInstruction | ministerialDirectiveIndicator | Special directive applies |

### Part D - Initiator Information (Person Who Requested Transfer)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| D1 | Initiator entity type | Code | 1 | Yes | P=Person, E=Entity | Party | initiatorType | Person or entity |
| D2 | Initiator surname | Text | 150 | Cond | Free text | Party | initiatorSurname | Last name if person |
| D3 | Initiator given name | Text | 150 | Cond | Free text | Party | initiatorGivenName | First name if person |
| D4 | Initiator other names | Text | 150 | No | Free text | Party | initiatorMiddleName | Middle/other names |
| D5 | Initiator entity name | Text | 300 | Cond | Free text | Party | initiatorName | Legal name if entity |
| D6 | Initiator client number | Text | 50 | No | Free text | Party | initiatorClientNumber | Internal client ID |
| D7 | Initiator street address | Text | 200 | No | Free text | Party | initiatorStreetAddress | Street address |
| D8 | Initiator city | Text | 100 | No | Free text | Party | initiatorCity | City |
| D9 | Initiator province/state | Code | 3 | No | Province/state code | Party | initiatorStateOrProvince | Province/state |
| D10 | Initiator postal/ZIP code | Text | 10 | No | Postal/ZIP | Party | initiatorPostalCode | Postal/ZIP code |
| D11 | Initiator country | Code | 2 | No | ISO 3166 | Party | initiatorCountry | ISO country code |
| D12 | Initiator telephone | Text | 20 | No | Phone format | Party | initiatorPhoneNumber | Phone number |
| D13 | Initiator date of birth | Date | 10 | No | YYYY-MM-DD | Party | initiatorDateOfBirth | Birth date if person |
| D14 | Initiator occupation | Text | 100 | No | Free text | Party | initiatorOccupation | Occupation/business type |
| D15 | Initiator account number | Text | 50 | No | Free text | Account | initiatorAccountNumber | Account identifier |

### Part E - Sender Financial Institution (Ordering Institution)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| E1 | Sender institution name | Text | 300 | Yes | Free text | FinancialInstitution | senderInstitutionName | Sending bank |
| E2 | Sender institution number | Text | 4 | No | 4 digits | FinancialInstitution | senderInstitutionNumber | Bank number |
| E3 | Sender branch number | Text | 5 | No | 5 digits | FinancialInstitution | senderBranchNumber | Transit number |
| E4 | Sender SWIFT/BIC | Text | 11 | No | BIC | FinancialInstitution | senderInstitutionBic | BIC code |
| E5 | Sender street address | Text | 200 | No | Free text | FinancialInstitution | senderInstitutionAddress | Street address |
| E6 | Sender city | Text | 100 | No | Free text | FinancialInstitution | senderInstitutionCity | City |
| E7 | Sender province/state | Text | 100 | No | Free text | FinancialInstitution | senderInstitutionState | Province/state |
| E8 | Sender country | Code | 2 | Yes | ISO 3166 | FinancialInstitution | senderInstitutionCountry | ISO country code |
| E9 | Sender postal/ZIP code | Text | 10 | No | Postal/ZIP | FinancialInstitution | senderInstitutionPostalCode | Postal/ZIP code |

### Part F - Receiver Financial Institution (Beneficiary Institution)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| F1 | Receiver institution name | Text | 300 | Yes | Free text | FinancialInstitution | receiverInstitutionName | Receiving bank |
| F2 | Receiver institution number | Text | 4 | No | 4 digits | FinancialInstitution | receiverInstitutionNumber | Bank number |
| F3 | Receiver branch number | Text | 5 | No | 5 digits | FinancialInstitution | receiverBranchNumber | Transit number |
| F4 | Receiver SWIFT/BIC | Text | 11 | No | BIC | FinancialInstitution | receiverInstitutionBic | BIC code |
| F5 | Receiver street address | Text | 200 | No | Free text | FinancialInstitution | receiverInstitutionAddress | Street address |
| F6 | Receiver city | Text | 100 | No | Free text | FinancialInstitution | receiverInstitutionCity | City |
| F7 | Receiver province/state | Text | 100 | No | Free text | FinancialInstitution | receiverInstitutionState | Province/state |
| F8 | Receiver country | Code | 2 | Yes | ISO 3166 | FinancialInstitution | receiverInstitutionCountry | ISO country code |
| F9 | Receiver postal/ZIP code | Text | 10 | No | Postal/ZIP | FinancialInstitution | receiverInstitutionPostalCode | Postal/ZIP code |

### Part G - Beneficiary Information (Person Receiving Transfer)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| G1 | Beneficiary entity type | Code | 1 | Yes | P=Person, E=Entity | Party | beneficiaryType | Person or entity |
| G2 | Beneficiary surname | Text | 150 | Cond | Free text | Party | beneficiarySurname | Last name if person |
| G3 | Beneficiary given name | Text | 150 | Cond | Free text | Party | beneficiaryGivenName | First name if person |
| G4 | Beneficiary other names | Text | 150 | No | Free text | Party | beneficiaryMiddleName | Middle/other names |
| G5 | Beneficiary entity name | Text | 300 | Cond | Free text | Party | beneficiaryName | Legal name if entity |
| G6 | Beneficiary client number | Text | 50 | No | Free text | Party | beneficiaryClientNumber | Internal client ID |
| G7 | Beneficiary street address | Text | 200 | No | Free text | Party | beneficiaryStreetAddress | Street address |
| G8 | Beneficiary city | Text | 100 | No | Free text | Party | beneficiaryCity | City |
| G9 | Beneficiary province/state | Code | 3 | No | Province/state code | Party | beneficiaryStateOrProvince | Province/state |
| G10 | Beneficiary postal/ZIP code | Text | 10 | No | Postal/ZIP | Party | beneficiaryPostalCode | Postal/ZIP code |
| G11 | Beneficiary country | Code | 2 | No | ISO 3166 | Party | beneficiaryCountry | ISO country code |
| G12 | Beneficiary telephone | Text | 20 | No | Phone format | Party | beneficiaryPhoneNumber | Phone number |
| G13 | Beneficiary date of birth | Date | 10 | No | YYYY-MM-DD | Party | beneficiaryDateOfBirth | Birth date if person |
| G14 | Beneficiary occupation | Text | 100 | No | Free text | Party | beneficiaryOccupation | Occupation/business type |
| G15 | Beneficiary account number | Text | 50 | No | Free text | Account | beneficiaryAccountNumber | Account identifier |

### Part H - Identification of Initiator (if Person)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| H1 | Identification type | Code | 2 | No | See ID type codes | Party | initiatorIdType | ID document type |
| H2 | Identification number | Text | 50 | No | Free text | Party | initiatorIdNumber | ID document number |
| H3 | Jurisdiction (country/province) | Text | 100 | No | Free text | Party | initiatorIdJurisdiction | Issuing jurisdiction |
| H4 | Issuing authority | Text | 200 | No | Free text | Party | initiatorIdIssuingAuthority | Authority that issued ID |

### Part I - Intermediary Financial Institution (if applicable)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| I1 | Intermediary institution exists | Boolean | 1 | Yes | Y/N | FinancialInstitution | intermediaryInstitutionExists | Intermediary bank involved |
| I2 | Intermediary institution name | Text | 300 | No | Free text | FinancialInstitution | intermediaryInstitutionName | Intermediary bank |
| I3 | Intermediary institution number | Text | 4 | No | 4 digits | FinancialInstitution | intermediaryInstitutionNumber | Bank number |
| I4 | Intermediary branch number | Text | 5 | No | 5 digits | FinancialInstitution | intermediaryBranchNumber | Transit number |
| I5 | Intermediary SWIFT/BIC | Text | 11 | No | BIC | FinancialInstitution | intermediaryInstitutionBic | BIC code |
| I6 | Intermediary country | Code | 2 | No | ISO 3166 | FinancialInstitution | intermediaryInstitutionCountry | ISO country code |

### Part J - Payment Details

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| J1 | Purpose of payment | Text | 1000 | No | Free text | PaymentInstruction | remittanceInformation | Payment purpose/details |
| J2 | Payment instructions | Text | 500 | No | Free text | PaymentInstruction | instructionForNextAgent | Special instructions |

### Metadata

| Field# | Field Name | Type | Length | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|------------|---------------|-------|
| - | FINTRAC acknowledgment number | Text | 50 | RegulatoryReport | fintracAcknowledgmentNumber | Assigned by FINTRAC |
| - | Report status | Code | 2 | RegulatoryReport | reportStatus | Submitted, Accepted, Rejected |
| - | Submission timestamp | DateTime | 20 | RegulatoryReport | submissionTimestamp | When submitted |

---

## Code Lists

### Reporting Entity Business Activity Codes (Field A4)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Bank | FinancialInstitution.businessActivity = 'Bank' |
| 02 | Credit union/caisse populaire | FinancialInstitution.businessActivity = 'CreditUnion' |
| 03 | Money services business | FinancialInstitution.businessActivity = 'MSB' |
| 04 | Securities dealer | FinancialInstitution.businessActivity = 'SecuritiesDealer' |
| 99 | Other | FinancialInstitution.businessActivity = 'Other' |

### Transfer Direction Codes (Field C1)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| I | Incoming (INTO Canada) | PaymentInstruction.transferDirection = 'Incoming' |
| O | Outgoing (OUT OF Canada) | PaymentInstruction.transferDirection = 'Outgoing' |

### Transfer Type Codes (Field C8)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | SWIFT | PaymentInstruction.transferType = 'SWIFT' |
| 02 | Wire transfer | PaymentInstruction.transferType = 'WireTransfer' |
| 03 | EFT | PaymentInstruction.transferType = 'EFT' |
| 04 | ACH | PaymentInstruction.transferType = 'ACH' |
| 99 | Other | PaymentInstruction.transferType = 'Other' |

### Entity Type Codes (Fields D1, G1)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| P | Person | Party.partyType = 'Person' |
| E | Entity | Party.partyType = 'Entity' |

### Identification Type Codes (Field H1)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| 01 | Driver's licence | Party.identificationType = 'DriversLicence' |
| 02 | Passport | Party.identificationType = 'Passport' |
| 03 | Record of landing | Party.identificationType = 'RecordOfLanding' |
| 04 | Permanent resident card | Party.identificationType = 'PermanentResidentCard' |
| 05 | Provincial/territorial ID | Party.identificationType = 'ProvincialId' |
| 06 | Certificate of Indian status | Party.identificationType = 'CertificateIndianStatus' |
| 99 | Other | Party.identificationType = 'Other' |

---

## CDM Extensions Required

All 88 EFTR fields successfully map to existing CDM model. **No enhancements required.**

---

## Example EFTR Report

### Outgoing Transfer from Canada to USA

```
Part A - Reporting Entity
A1: REF-EFTR-20241220-001
A2: BC12345
A3: Royal Bank of Canada
A4: 01 (Bank)
A5: Sarah Johnson
A6: +1-416-555-0100
A7: sarah.johnson@rbc.ca

Part B - Location
B1: B (Branch)
B2: Toronto King Street Branch
B3: 200 King Street West
B4: Toronto
B5: ON
B6: M5H 1K4
B7: CA

Part C - Transfer Information
C1: O (Outgoing)
C2: 2024-12-18
C3: 14:30:00
C4: 100000.00 (CAD)
C5: 74500.00 (USD)
C6: USD
C7: 0.7450
C8: 01 (SWIFT)
C9: RBC20241218001234
C10: N
C11: N

Part D - Initiator (Canadian person sending)
D1: E (Entity)
D5: Canadian Maple Products Inc
D6: CLI-2024-3456
D7: 150 Queen Street
D8: Toronto
D9: ON
D10: M5H 2N2
D11: CA
D12: +1-416-555-0200
D14: Food manufacturing
D15: 1234567890

Part E - Sender Institution (Canadian - RBC)
E1: Royal Bank of Canada
E2: 0003
E3: 01234
E4: ROYCCAT2XXX
E5: 200 Bay Street
E6: Toronto
E7: ON
E8: CA
E9: M5J 2J5

Part F - Receiver Institution (US - Bank of America)
F1: Bank of America N.A.
F4: BOFAUS3NXXX
F5: 100 North Tryon Street
F6: Charlotte
F7: NC
F8: US
F9: 28255

Part G - Beneficiary (US person receiving)
G1: E (Entity)
G5: American Food Distributors LLC
G6: US-2024-7890
G7: 500 Main Street
G8: New York
G9: NY
G10: 10001
G11: US
G12: +1-212-555-0300
G14: Food distribution
G15: 9876543210

Part H - Identification
(Not applicable - entity initiator)

Part I - Intermediary
I1: N

Part J - Payment Details
J1: Payment for invoice INV-2024-9876 - Maple syrup shipment
J2: Urgent payment - please credit beneficiary same day
```

---

## References

- FINTRAC EFTR Guidance: https://fintrac-canafe.canada.ca/guidance-directives/transaction-operation/eft-dt/eft-dt-eng
- FINTRAC Web Reporting: https://f2r.fintrac-canafe.gc.ca/
- PCMLTFA: https://laws-lois.justice.gc.ca/eng/acts/P-24.501/
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`, `/schemas/05_regulatory_report_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
