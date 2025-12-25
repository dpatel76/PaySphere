# GPS Payments CDM - Logical Model Specification

**Version:** 1.0.0
**Date:** 2024-12-20
**Status:** Phase 1.1 Complete

---

## 1. Overview

The GPS Payments Common Domain Model (CDM) defines 29 entities organized into 8 logical domains. This specification provides the complete logical model for the payments analytics platform supporting:

- 16 payment standards (ISO 20022, SWIFT MT, regional systems)
- 13 regulatory reports (FinCEN, AUSTRAC, IRS, OFAC, EBA, UK NCA)
- End-to-end data lineage from source to report
- Fraud detection via graph analytics

### 1.1 Design Principles

| Principle | Description |
|-----------|-------------|
| **Normalisation** | Common components abstracted to reduce duplication |
| **Composability** | Entities built bottom-up with qualification at each layer |
| **Bi-temporal** | All entities track valid_from/valid_to and system timestamps |
| **Lineage-native** | Lineage metadata embedded in every entity |
| **ISO 20022 aligned** | Core structure follows ISO 20022 message components |
| **Regulatory complete** | Extensions for FATCA, CRS, FinCEN, AUSTRAC requirements |

### 1.2 Entity Summary by Domain

| Domain | Entities | Description |
|--------|----------|-------------|
| **Payment Core** | 7 | Core payment types and lifecycle |
| **Party** | 5 | Counterparties and identifications |
| **Account** | 3 | Account types and ownership |
| **Amount** | 3 | Monetary amounts and charges |
| **Settlement** | 3 | Settlement and clearing |
| **Reference** | 4 | Reference data and metadata |
| **Events** | 2 | Lifecycle and workflow events |
| **Lineage** | 2 | Data lineage and audit trail |
| **Total** | **29** | |

---

## 2. Entity Relationship Diagram

```
                                    +-------------------+
                                    |     Payment       |
                                    +-------------------+
                                    | payment_id (PK)   |
                                    | payment_type      |
                                    | status            |
                                    +--------+----------+
                                             |
              +------------------------------+------------------------------+
              |                              |                              |
              v                              v                              v
+-------------------+          +-------------------+          +-------------------+
| PaymentInstruction|          |   CreditTransfer  |          |    DirectDebit    |
+-------------------+          +-------------------+          +-------------------+
| instruction_id    |          | credit_transfer_id|          | direct_debit_id   |
| payment_id (FK)   |          | payment_id (FK)   |          | payment_id (FK)   |
| debtor_id (FK)    |--------->| creditor_id (FK)  |          | debtor_id (FK)    |
| creditor_id (FK)  |          | amount_id (FK)    |          | mandate_id        |
+--------+----------+          +-------------------+          +-------------------+
         |
         |     +-------------------+          +-------------------+
         +---->|  PaymentReturn    |          | PaymentReversal   |
         |     +-------------------+          +-------------------+
         |     | return_id (PK)    |          | reversal_id (PK)  |
         |     | original_payment  |          | original_payment  |
         |     | return_reason     |          | reversal_reason   |
         |     +-------------------+          +-------------------+
         |
         v     +-------------------+
               | PaymentStatusRpt  |
               +-------------------+
               | status_report_id  |
               | payment_id (FK)   |
               | status_code       |
               +-------------------+

+-------------------+          +-------------------+          +-------------------+
|      Party        |          |      Account      |          |  FinancialInst    |
+-------------------+          +-------------------+          +-------------------+
| party_id (PK)     |<-------->| account_id (PK)   |          | fi_id (PK)        |
| party_type        |          | account_number    |          | bic               |
| name              |          | account_owner(FK) |<-------->| lei               |
+--------+----------+          | fi_id (FK)        |          | routing_code      |
         |                     +-------------------+          +-------------------+
         |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
+-------------------+ +-------------------+ +-------------------+
| PartyIdentification| |      Person       | |   Organisation   |
+-------------------+ +-------------------+ +-------------------+
| identification_id | | person_id (PK)    | | org_id (PK)      |
| party_id (FK)     | | party_id (FK)     | | party_id (FK)    |
| id_type           | | date_of_birth     | | registration_no  |
| id_value          | | nationality       | | industry_code    |
+-------------------+ +-------------------+ +-------------------+

+-------------------+          +-------------------+          +-------------------+
|      Amount       |          | CurrencyExchange  |          |     Charges       |
+-------------------+          +-------------------+          +-------------------+
| amount_id (PK)    |          | exchange_id (PK)  |          | charge_id (PK)    |
| value             |<-------->| source_currency   |          | payment_id (FK)   |
| currency          |          | target_currency   |          | charge_type       |
| amount_type       |          | rate              |          | amount            |
+-------------------+          +-------------------+          +-------------------+

+-------------------+          +-------------------+          +-------------------+
|    Settlement     |          |SettlementInstruct |          |  ClearingSystem   |
+-------------------+          +-------------------+          +-------------------+
| settlement_id (PK)|          | instruction_id    |          | clearing_id (PK)  |
| payment_id (FK)   |<-------->| settlement_id(FK) |          | system_code       |
| settlement_date   |          | account_id (FK)   |          | system_name       |
| settlement_amount |          | instruction_type  |          +-------------------+
+-------------------+          +-------------------+

+-------------------+          +-------------------+          +-------------------+
| PaymentTypeInfo   |          |RegulatoryReporting|          | RemittanceInfo    |
+-------------------+          +-------------------+          +-------------------+
| type_info_id (PK) |          | reporting_id (PK) |          | remittance_id(PK) |
| payment_id (FK)   |          | payment_id (FK)   |          | payment_id (FK)   |
| service_level     |          | reporting_code    |          | unstructured      |
| local_instrument  |          | jurisdiction      |          | structured        |
+-------------------+          +-------------------+          +-------------------+

+-------------------+          +-------------------+
|     Document      |          |  PaymentEvent     |
+-------------------+          +-------------------+
| document_id (PK)  |          | event_id (PK)     |
| payment_id (FK)   |          | payment_id (FK)   |
| document_type     |          | event_type        |
| reference         |          | event_timestamp   |
+-------------------+          | previous_state    |
                               | new_state         |
+-------------------+          +-------------------+
|  WorkflowEvent    |
+-------------------+          +-------------------+          +-------------------+
| workflow_id (PK)  |          | LineageMetadata   |          |    AuditTrail     |
| entity_type       |          +-------------------+          +-------------------+
| entity_id         |          | lineage_id (PK)   |          | audit_id (PK)     |
| event_type        |          | entity_type       |          | entity_type       |
| actor             |          | entity_id         |          | entity_id         |
+-------------------+          | source_system     |          | action            |
                               | source_field      |          | actor             |
                               | target_field      |          | timestamp         |
                               +-------------------+          +-------------------+
```

---

## 3. Domain Specifications

### 3.1 Payment Core Domain (7 Entities)

#### 3.1.1 Payment

The root entity representing a payment transaction.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| payment_id | UUID | Y | Primary key |
| payment_type | Enum | Y | CREDIT_TRANSFER, DIRECT_DEBIT, RETURN, REVERSAL |
| scheme_code | Enum | Y | ACH, FEDWIRE, SWIFT, SEPA, RTP, PIX, UPI, etc. |
| status | Enum | Y | Current lifecycle status |
| created_at | Timestamp | Y | Creation timestamp |
| valid_from | Date | Y | Business validity start |
| valid_to | Date | N | Business validity end |

**Status Enum Values:**
- initiated, received, accepted, validated, validation_failed
- fraud_screening, fraud_clear, fraud_hold, fraud_reject
- sanctions_screening, sanctions_clear, sanctions_hit
- processing, queued, routed, transmitted
- in_clearing, clearing_failed
- settled, settlement_pending, settlement_failed
- completed, returned, reversed, cancelled, rejected, failed

#### 3.1.2 PaymentInstruction

Detailed instruction for payment execution.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| instruction_id | UUID | Y | Primary key |
| payment_id | UUID | Y | FK to Payment |
| end_to_end_id | String(35) | N | End-to-end identification |
| uetr | UUID | N | SWIFT UETR for gpi payments |
| transaction_id | String(35) | N | Transaction identification |
| debtor_id | UUID | Y | FK to Party (payer) |
| debtor_account_id | UUID | N | FK to Account |
| debtor_agent_id | UUID | N | FK to FinancialInstitution |
| creditor_id | UUID | Y | FK to Party (payee) |
| creditor_account_id | UUID | N | FK to Account |
| creditor_agent_id | UUID | N | FK to FinancialInstitution |
| instructed_amount_id | UUID | Y | FK to Amount |
| requested_execution_date | Date | Y | Requested execution date |
| purpose | String(4) | N | ISO 20022 purpose code |
| priority | Enum | N | HIGH, NORM, URGP |
| charge_bearer | Enum | N | DEBT, CRED, SHAR, SLEV |

#### 3.1.3 CreditTransfer

Credit transfer specific details.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| credit_transfer_id | UUID | Y | Primary key |
| payment_id | UUID | Y | FK to Payment |
| intermediary_agent_1_id | UUID | N | FK to FinancialInstitution |
| intermediary_agent_2_id | UUID | N | FK to FinancialInstitution |
| intermediary_agent_3_id | UUID | N | FK to FinancialInstitution |
| instruction_for_creditor_agent | String(140) | N | Instructions text |
| instruction_for_next_agent | String(140) | N | Instructions text |

#### 3.1.4 DirectDebit

Direct debit specific details.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| direct_debit_id | UUID | Y | Primary key |
| payment_id | UUID | Y | FK to Payment |
| mandate_id | String(35) | Y | Direct debit mandate reference |
| mandate_date | Date | Y | Mandate signing date |
| sequence_type | Enum | Y | FRST, RCUR, FNAL, OOFF |
| creditor_scheme_id | String(35) | N | Creditor scheme identification |
| direct_debit_type | Enum | N | B2B, CORE |

#### 3.1.5 PaymentReturn

Payment return details.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| return_id | UUID | Y | Primary key |
| original_payment_id | UUID | Y | FK to original Payment |
| return_payment_id | UUID | Y | FK to return Payment |
| return_reason_code | String(4) | Y | ISO 20022 return reason code |
| return_reason_description | String(500) | N | Detailed reason |
| original_end_to_end_id | String(35) | N | Original E2E ID |
| return_amount_id | UUID | Y | FK to Amount |
| return_date | Date | Y | Date of return |

#### 3.1.6 PaymentReversal

Payment reversal details.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| reversal_id | UUID | Y | Primary key |
| original_payment_id | UUID | Y | FK to original Payment |
| reversal_payment_id | UUID | Y | FK to reversal Payment |
| reversal_reason_code | String(4) | Y | ISO 20022 reversal reason code |
| reversal_reason_description | String(500) | N | Detailed reason |
| original_interbank_settlement_amount_id | UUID | N | FK to Amount |
| reversal_date | Date | Y | Date of reversal |

#### 3.1.7 PaymentStatusReport

Payment status report for tracking.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| status_report_id | UUID | Y | Primary key |
| payment_id | UUID | Y | FK to Payment |
| message_id | String(35) | Y | Status message ID |
| creation_date_time | Timestamp | Y | Report creation time |
| status_code | String(4) | Y | ISO 20022 status code |
| status_reason_code | String(4) | N | Reason code |
| status_reason_description | String(500) | N | Detailed reason |
| acceptance_date_time | Timestamp | N | Acceptance timestamp |
| effective_interbank_settlement_date | Date | N | Settlement date |

---

### 3.2 Party Domain (5 Entities)

#### 3.2.1 Party

Core party entity (counterparty in payment).

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| party_id | UUID | Y | Primary key |
| party_type | Enum | Y | INDIVIDUAL, ORGANIZATION, GOVERNMENT, FINANCIAL_INSTITUTION |
| name | String(140) | Y | Full legal name |
| given_name | String(35) | N | First name (individuals) |
| family_name | String(35) | N | Last name (individuals) |
| date_of_birth | Date | N | DOB for individuals |
| nationality | Array[String(2)] | N | ISO country codes |
| tax_id | String(50) | N | Primary tax ID |
| tax_id_type | Enum | N | SSN, EIN, ITIN, VAT, TIN |
| pep_flag | Boolean | N | Politically Exposed Person |
| risk_rating | Enum | N | low, medium, high, very_high |
| sanctions_screening_status | Enum | N | not_screened, clear, hit, pending |
| effective_from | Date | Y | Validity start |
| effective_to | Date | N | Validity end |
| is_current | Boolean | Y | Current record flag |

**Regulatory Extensions:**
- FATCA fields: us_tax_status, fatca_classification, w8ben_status, w9_status, substantial_us_owner
- CRS fields: crs_reportable, crs_entity_type, tax_residencies[]
- FinCEN fields: occupation, naics_code, form_of_identification, dba_name, alternate_names
- APAC fields: china_hukou, india_aadhar, japan_my_number, singapore_nric

#### 3.2.2 PartyIdentification

Additional party identification documents.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| identification_id | UUID | Y | Primary key |
| party_id | UUID | Y | FK to Party |
| identification_type | Enum | Y | PASSPORT, NATIONAL_ID, DRIVERS_LICENSE, etc. |
| identification_number | String(50) | Y | ID number |
| issuing_country | String(2) | Y | ISO country code |
| issuing_authority | String(100) | N | Issuing authority name |
| issue_date | Date | N | Issue date |
| expiry_date | Date | N | Expiry date |
| is_primary | Boolean | N | Primary ID flag |

#### 3.2.3 Person

Individual-specific attributes (extends Party).

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| person_id | UUID | Y | Primary key |
| party_id | UUID | Y | FK to Party |
| title | String(10) | N | Mr, Ms, Dr, etc. |
| suffix | String(10) | N | Jr, Sr, III |
| place_of_birth | String(100) | N | Birth place |
| country_of_birth | String(2) | N | ISO country code |
| gender | Enum | N | M, F, O |
| marital_status | Enum | N | SINGLE, MARRIED, DIVORCED, WIDOWED |
| employer_name | String(140) | N | Current employer |
| employment_status | Enum | N | EMPLOYED, SELF_EMPLOYED, UNEMPLOYED, RETIRED |

#### 3.2.4 Organisation

Organisation-specific attributes (extends Party).

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| organisation_id | UUID | Y | Primary key |
| party_id | UUID | Y | FK to Party |
| registration_number | String(50) | N | Business registration |
| registration_country | String(2) | N | ISO country code |
| legal_form | String(50) | N | LLC, Corp, Ltd, etc. |
| industry_code | String(10) | N | NAICS/SIC code |
| industry_description | String(200) | N | Industry description |
| incorporation_date | Date | N | Incorporation date |
| number_of_employees | Integer | N | Employee count |
| annual_revenue | Decimal | N | Annual revenue |
| public_company | Boolean | N | Publicly traded flag |
| stock_exchange | String(20) | N | Stock exchange code |
| ticker_symbol | String(10) | N | Stock ticker |

#### 3.2.5 FinancialInstitution

Financial institution entity.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| fi_id | UUID | Y | Primary key |
| institution_name | String(140) | Y | Legal name |
| bic | String(11) | N | SWIFT BIC code |
| lei | String(20) | N | Legal Entity Identifier |
| national_clearing_code | String(35) | N | Routing/Sort code/BSB |
| national_clearing_system | Enum | N | USABA, AUBSB, GBSORTCODE, etc. |
| country | String(2) | Y | ISO country code |
| fi_type | Enum | N | BANK, BROKER_DEALER, MSB, etc. |
| primary_regulator | Enum | N | OCC, FDIC, FRB, etc. |
| rssd_number | String(10) | N | Federal Reserve RSSD |
| fatca_giin | String(19) | N | FATCA Global Intermediary ID |
| sharia_compliant | Boolean | N | Islamic finance flag |

---

### 3.3 Account Domain (3 Entities)

#### 3.3.1 Account

Core account entity.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| account_id | UUID | Y | Primary key |
| account_number | String(34) | Y | Account number |
| iban | String(34) | N | IBAN (if applicable) |
| account_type | Enum | Y | CHECKING, SAVINGS, LOAN, etc. |
| currency | String(3) | Y | ISO 4217 currency |
| financial_institution_id | UUID | Y | FK to FinancialInstitution |
| account_status | Enum | Y | ACTIVE, INACTIVE, DORMANT, CLOSED |
| open_date | Date | Y | Account opening date |
| close_date | Date | N | Account closing date |
| current_balance | Decimal | N | Current balance |
| available_balance | Decimal | N | Available balance |
| effective_from | Date | Y | Validity start |
| effective_to | Date | N | Validity end |
| is_current | Boolean | Y | Current record flag |

**Regulatory Extensions:**
- FATCA: fatca_status, fatca_giin, account_holder_type
- CRS: crs_reportable_account, controlling_persons[]
- Tax: account_balance_for_tax_reporting, withholding_tax_rate

#### 3.3.2 CashAccount

Cash account specific attributes.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| cash_account_id | UUID | Y | Primary key |
| account_id | UUID | Y | FK to Account |
| cash_account_type | Enum | Y | CACC (Current), SVGS (Savings), etc. |
| proprietary_type | String(35) | N | Proprietary account type |
| secondary_id | String(34) | N | Secondary identification |
| overdraft_limit | Decimal | N | Overdraft limit |
| interest_rate | Decimal | N | Current interest rate |

#### 3.3.3 AccountOwner

Account ownership relationship.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| account_owner_id | UUID | Y | Primary key |
| account_id | UUID | Y | FK to Account |
| party_id | UUID | Y | FK to Party |
| ownership_type | Enum | Y | PRIMARY, JOINT, BENEFICIAL, AUTHORIZED_SIGNER |
| ownership_percentage | Decimal | N | Ownership percentage (0-100) |
| role | Enum | N | OWNER, SIGNATORY, TRUSTEE, NOMINEE |
| effective_from | Date | Y | Relationship start date |
| effective_to | Date | N | Relationship end date |
| is_current | Boolean | Y | Current relationship flag |

---

### 3.4 Amount Domain (3 Entities)

#### 3.4.1 Amount

Monetary amount entity.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| amount_id | UUID | Y | Primary key |
| value | Decimal(18,4) | Y | Amount value |
| currency | String(3) | Y | ISO 4217 currency code |
| amount_type | Enum | Y | INSTRUCTED, SETTLEMENT, EQUIVALENT, RETURN |
| precision | Integer | N | Decimal precision |
| minor_units | Integer | N | Currency minor units |

#### 3.4.2 CurrencyExchange

Currency exchange details.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| exchange_id | UUID | Y | Primary key |
| payment_id | UUID | Y | FK to Payment |
| source_currency | String(3) | Y | Source currency code |
| target_currency | String(3) | Y | Target currency code |
| exchange_rate | Decimal(18,10) | Y | Exchange rate |
| unit_currency | String(3) | N | Unit currency |
| contract_id | String(35) | N | FX contract reference |
| quotation_date | Date | N | Rate quotation date |
| rate_type | Enum | N | SPOT, FORWARD, AGREED |

#### 3.4.3 Charges

Payment charges and fees.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| charge_id | UUID | Y | Primary key |
| payment_id | UUID | Y | FK to Payment |
| charge_type | Enum | Y | AGENT, CLEARING, TRANSFER, etc. |
| charge_bearer | Enum | Y | DEBT, CRED, SHAR |
| amount_id | UUID | Y | FK to Amount |
| agent_id | UUID | N | FK to FinancialInstitution |
| tax_amount_id | UUID | N | FK to Amount (tax component) |
| charge_reason | String(140) | N | Charge description |

---

### 3.5 Settlement Domain (3 Entities)

#### 3.5.1 Settlement

Settlement record.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| settlement_id | UUID | Y | Primary key |
| payment_id | UUID | Y | FK to Payment |
| settlement_date | Date | Y | Settlement date |
| settlement_amount_id | UUID | Y | FK to Amount |
| settlement_method | Enum | Y | INDA, INGA, COVE |
| clearing_system_id | UUID | N | FK to ClearingSystem |
| settlement_status | Enum | Y | PENDING, SETTLED, FAILED |
| settlement_cycle | String(10) | N | T+0, T+1, T+2 |
| interbank_settlement_date | Date | N | Interbank settlement date |

#### 3.5.2 SettlementInstruction

Settlement instruction details.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| instruction_id | UUID | Y | Primary key |
| settlement_id | UUID | Y | FK to Settlement |
| account_id | UUID | Y | FK to Account (settlement account) |
| instruction_type | Enum | Y | CREDIT, DEBIT |
| instruction_priority | Enum | N | HIGH, NORM |
| instruction_for_creditor_agent | String(140) | N | Instructions |
| instruction_for_debtor_agent | String(140) | N | Instructions |

#### 3.5.3 ClearingSystem

Clearing system reference.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| clearing_system_id | UUID | Y | Primary key |
| system_code | String(10) | Y | ACH, FEDWIRE, TARGET2, etc. |
| system_name | String(100) | Y | Full system name |
| system_type | Enum | Y | RTGS, ACH, HYBRID |
| country | String(2) | Y | Operating country |
| currency | String(3) | Y | Settlement currency |
| operating_hours | String(50) | N | Operating hours |
| cut_off_time | Time | N | Cut-off time |
| member_id | String(35) | N | Membership ID |

---

### 3.6 Reference Domain (4 Entities)

#### 3.6.1 PaymentTypeInformation

Payment type classification.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| type_info_id | UUID | Y | Primary key |
| payment_id | UUID | Y | FK to Payment |
| service_level | String(4) | N | SEPA, URGP, SDVA, etc. |
| local_instrument | String(35) | N | Local instrument code |
| category_purpose | String(4) | N | Category purpose code |
| clearing_channel | Enum | N | RTGS, RTNS, ACH, BOOK |
| instruction_priority | Enum | N | HIGH, NORM |
| sequence_type | Enum | N | FRST, RCUR, FNAL, OOFF |

#### 3.6.2 RegulatoryReporting

Regulatory reporting information.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| reporting_id | UUID | Y | Primary key |
| payment_id | UUID | Y | FK to Payment |
| jurisdiction | String(2) | Y | ISO country code |
| reporting_type | String(35) | Y | Report type code |
| reporting_code | String(10) | N | Regulatory code |
| reporting_amount_id | UUID | N | FK to Amount |
| reporting_details | String(500) | N | Additional details |
| threshold_indicator | Boolean | N | Above reporting threshold |

#### 3.6.3 RemittanceInformation

Payment remittance details.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| remittance_id | UUID | Y | Primary key |
| payment_id | UUID | Y | FK to Payment |
| unstructured | Array[String(140)] | N | Unstructured remittance |
| structured_type | Enum | N | RADM, RPIN, FXDR, DISP, PUOR, SCOR |
| creditor_reference | String(35) | N | Creditor reference |
| invoiced_amount_id | UUID | N | FK to Amount |
| due_date | Date | N | Payment due date |
| document_id | UUID | N | FK to Document |

#### 3.6.4 Document

Related document reference.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| document_id | UUID | Y | Primary key |
| payment_id | UUID | Y | FK to Payment |
| document_type | Enum | Y | INVOICE, CREDIT_NOTE, ORDER, CONTRACT |
| document_reference | String(35) | Y | Document reference number |
| document_date | Date | N | Document date |
| line_items | Array[Object] | N | Line item details |
| related_dates | Array[Date] | N | Related date references |
| amounts | Array[UUID] | N | Related Amount references |

---

### 3.7 Events Domain (2 Entities)

#### 3.7.1 PaymentEvent

Payment lifecycle event.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| event_id | UUID | Y | Primary key |
| payment_id | UUID | Y | FK to Payment |
| event_type | Enum | Y | STATUS_CHANGE, VALIDATION, SCREENING, etc. |
| event_timestamp | Timestamp | Y | Event occurrence time |
| previous_state | String(50) | N | Previous status/state |
| new_state | String(50) | Y | New status/state |
| actor | String(100) | N | System/user causing event |
| actor_type | Enum | N | SYSTEM, USER, EXTERNAL |
| details | JSON | N | Event-specific details |
| correlation_id | UUID | N | Correlation identifier |

**Event Types:**
- STATUS_CHANGE, VALIDATION_PASSED, VALIDATION_FAILED
- SANCTIONS_SCREENING, FRAUD_SCREENING
- ENRICHMENT, TRANSFORMATION
- TRANSMISSION, ACKNOWLEDGEMENT
- SETTLEMENT, COMPLETION
- EXCEPTION, ERROR, TIMEOUT

#### 3.7.2 WorkflowEvent

Workflow/process event.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| workflow_event_id | UUID | Y | Primary key |
| entity_type | String(50) | Y | Entity type (Payment, Party, etc.) |
| entity_id | UUID | Y | Entity identifier |
| workflow_type | Enum | Y | APPROVAL, REVIEW, INVESTIGATION |
| event_type | Enum | Y | STARTED, ASSIGNED, COMPLETED, ESCALATED |
| event_timestamp | Timestamp | Y | Event timestamp |
| actor | String(100) | Y | Actor identifier |
| actor_role | String(50) | N | Actor role |
| previous_assignee | String(100) | N | Previous assignee |
| current_assignee | String(100) | N | Current assignee |
| comments | String(1000) | N | Event comments |
| attachments | Array[UUID] | N | Document attachments |

---

### 3.8 Lineage Domain (2 Entities)

#### 3.8.1 LineageMetadata

Field-level lineage metadata.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| lineage_id | UUID | Y | Primary key |
| entity_type | String(50) | Y | CDM entity type |
| entity_id | UUID | Y | CDM entity ID |
| field_name | String(100) | Y | Target field name |
| field_path | String(500) | N | Full JSON path |
| source_system | String(100) | Y | Source system name |
| source_table | String(200) | N | Source table/collection |
| source_field | String(200) | Y | Source field name |
| source_field_path | String(500) | N | Source JSON path |
| transformation_type | Enum | Y | DIRECT, DERIVED, LOOKUP, AGGREGATED |
| transformation_logic | String(1000) | N | Transformation expression |
| confidence_score | Decimal(5,4) | N | Mapping confidence (0-1) |
| effective_from | Timestamp | Y | Lineage validity start |
| effective_to | Timestamp | N | Lineage validity end |

**Transformation Types:**
- DIRECT: 1:1 field mapping
- DERIVED: Calculated from source fields
- LOOKUP: Reference data lookup
- AGGREGATED: Aggregation/summary
- CONSTANT: Constant value assignment
- DEFAULT: Default value when source null

#### 3.8.2 AuditTrail

Audit trail for all entity changes.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| audit_id | UUID | Y | Primary key |
| entity_type | String(50) | Y | Entity type |
| entity_id | UUID | Y | Entity ID |
| action | Enum | Y | CREATE, UPDATE, DELETE, READ |
| action_timestamp | Timestamp | Y | Action timestamp |
| actor | String(100) | Y | Actor identifier |
| actor_type | Enum | Y | USER, SYSTEM, API, BATCH |
| actor_ip | String(45) | N | Actor IP address |
| session_id | String(100) | N | Session identifier |
| old_values | JSON | N | Previous field values |
| new_values | JSON | N | New field values |
| change_reason | String(500) | N | Reason for change |
| correlation_id | UUID | N | Request correlation ID |

---

## 4. Common Patterns

### 4.1 Bi-Temporal Columns

All Silver/Gold entities include:

| Column | Type | Description |
|--------|------|-------------|
| valid_from | Date | Business validity start |
| valid_to | Date | Business validity end (null = current) |
| is_current | Boolean | Current record indicator |
| created_timestamp | Timestamp | Record creation time |
| last_updated_timestamp | Timestamp | Last update time |
| last_updated_by | String | Update actor |
| record_version | Integer | Optimistic lock version |
| is_deleted | Boolean | Soft delete flag |
| deleted_timestamp | Timestamp | Deletion time |

### 4.2 Source Tracking Columns

All CDM entities include:

| Column | Type | Description |
|--------|------|-------------|
| source_system | String | Originating system |
| source_system_record_id | String | Source record identifier |
| source_message_type | String | Source message type |
| ingestion_timestamp | Timestamp | Bronze ingestion time |
| bronze_to_silver_timestamp | Timestamp | Silver transformation time |

### 4.3 Data Quality Columns

| Column | Type | Description |
|--------|------|-------------|
| data_quality_score | Decimal | Overall DQ score (0-100) |
| data_quality_dimensions | JSON | Dimension scores |
| data_quality_issues | Array[String] | Identified issues |

### 4.4 Partitioning Strategy

| Entity Type | Partition Keys | Clustering Keys |
|-------------|----------------|-----------------|
| Payment* | partition_year, partition_month, region | payment_type, status |
| Party | partition_year, region | party_type |
| Account | partition_year, region | account_type |
| Event | partition_year, partition_month | event_type |
| Lineage | entity_type | source_system |

---

## 5. Validation Rules

### 5.1 Referential Integrity

| From Entity | To Entity | Cardinality | Constraint |
|-------------|-----------|-------------|------------|
| PaymentInstruction | Payment | N:1 | Required |
| PaymentInstruction | Party (debtor) | N:1 | Required |
| PaymentInstruction | Party (creditor) | N:1 | Required |
| PaymentInstruction | Account | N:1 | Optional |
| Account | FinancialInstitution | N:1 | Required |
| AccountOwner | Account | N:1 | Required |
| AccountOwner | Party | N:1 | Required |
| Settlement | Payment | N:1 | Required |
| PaymentEvent | Payment | N:1 | Required |

### 5.2 Business Rules

| Rule ID | Entity | Rule Description |
|---------|--------|------------------|
| BUS-001 | Amount | Value must be > 0 |
| BUS-002 | Amount | Currency must be valid ISO 4217 |
| BUS-003 | Party | INDIVIDUAL requires date_of_birth |
| BUS-004 | Party | ORGANIZATION requires registration_number |
| BUS-005 | Account | IBAN must match country format |
| BUS-006 | Payment | Status transitions must follow FSM |
| BUS-007 | Settlement | Settlement date >= execution date |
| BUS-008 | DirectDebit | Mandate required |

---

## 6. Entity Cross-Reference

### 6.1 Mapping to Existing Schemas

| CDM Entity | Existing Schema | Status |
|------------|-----------------|--------|
| Payment | - | New |
| PaymentInstruction | 01_payment_instruction_complete_schema.json | Exists |
| CreditTransfer | (embedded in PaymentInstruction) | Extract |
| DirectDebit | (embedded in PaymentInstruction) | Extract |
| PaymentReturn | (embedded in PaymentInstruction) | Extract |
| PaymentReversal | (embedded in PaymentInstruction) | Extract |
| PaymentStatusReport | - | New |
| Party | 02_party_complete_schema.json | Exists |
| PartyIdentification | (embedded in Party) | Extract |
| Person | (embedded in Party) | Extract |
| Organisation | (embedded in Party) | Extract |
| FinancialInstitution | 04_financial_institution_complete_schema.json | Exists |
| Account | 03_account_complete_schema.json | Exists |
| CashAccount | (embedded in Account) | Extract |
| AccountOwner | (embedded in Account) | Extract |
| Amount | (embedded in PaymentInstruction) | Extract |
| CurrencyExchange | (embedded in PaymentInstruction) | Extract |
| Charges | (embedded in PaymentInstruction) | Extract |
| Settlement | - | New |
| SettlementInstruction | - | New |
| ClearingSystem | - | New |
| PaymentTypeInformation | (embedded in PaymentInstruction) | Extract |
| RegulatoryReporting | 05_regulatory_report_complete_schema.json | Exists |
| RemittanceInformation | (embedded in PaymentInstruction) | Extract |
| Document | - | New |
| PaymentEvent | - | New |
| WorkflowEvent | - | New |
| LineageMetadata | - | New |
| AuditTrail | - | New |

### 6.2 Regulatory Field Mapping Summary

| Regulatory Requirement | CDM Entity | Key Fields |
|------------------------|------------|------------|
| FinCEN CTR | Party, Account, Payment | occupation, naics_code, tin, amount > $10K |
| FinCEN SAR | Party, Payment, ComplianceCase | suspicious_activity, narrative |
| AUSTRAC IFTI | Payment, Party | international_transfer, ordering_customer |
| AUSTRAC TTR | Payment | cash_threshold > AUD $10K |
| FATCA 8966 | Party, Account | us_indicia, fatca_classification, giin |
| CRS | Party, Account | tax_residencies, controlling_persons |
| OFAC Sanctions | Party, Payment | sdn_match, blocking_status |
| UK SAR | Party, Payment | suspicious_activity, daml_consent |
| PSD2 Fraud | Payment | fraud_type, authentication_method |

---

## 7. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2024-12-20 | GPS CDM Team | Initial logical model with 29 entities |

---

**Document Status:** Complete - Ready for Phase 1.2 Physical Model Design
