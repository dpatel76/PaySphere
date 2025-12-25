# Workstream 2: Common Domain Model (CDM) Development - Detailed Approach
## Bank of America - Global Payments Services

**Document Version:** 1.0
**Last Updated:** 2025-12-18
**Workstream Lead:** UK Resource (Data Architect - Payments Domain Expert)
**Support:** India Resource 2 (Data Engineer - Data Modeling Specialist)
**Duration:** Months 1-4 (16 weeks)
**Total Effort:** 360 person-days

---

## Table of Contents

1. [Workstream Overview](#overview)
2. [Phase 1: CDM Design Principles & Methodology (Weeks 1-2)](#phase1)
3. [Phase 2: Logical Common Domain Model (Weeks 3-8)](#phase2)
4. [Phase 3: Physical Common Domain Model (Weeks 9-14)](#phase3)
5. [Phase 4: CDM Governance Framework (Weeks 15-16)](#phase4)
6. [Dependencies & Sequencing](#dependencies)
7. [Risks & Mitigation](#risks)
8. [Quality Gates](#quality-gates)

---

## 1. Workstream Overview {#overview}

### Objective
Design and validate a comprehensive ISO 20022-based Common Domain Model (CDM) that serves as the canonical data model for all GPS payment types, enabling regulatory reporting, fraud detection, analytics, and operational processing.

### Scope
- ISO 20022 as foundational standard
- Coverage of all payment types (ACH, Wires, SWIFT, SEPA, BACS, FPS, RTP, FedNow, Zelle, etc.)
- 36+ core and supporting entities
- 2,000+ attributes with complete specifications
- 100% field mapping coverage from source systems
- Physical implementation in JSON Schema and Delta Lake DDL

### Key Deliverables
| Deliverable | Due Week | Owner |
|-------------|----------|-------|
| CDM Design Principles & Methodology | Week 2 | UK Lead |
| Logical CDM Model (Complete) | Week 8 | UK Lead |
| Physical CDM Model (JSON Schemas + DDL) | Week 14 | UK Lead |
| CDM Governance Framework | Week 16 | UK Lead |

### Success Criteria
- ✅ 99%+ field coverage for all payment products
- ✅ 100% source-to-CDM mapping reconciliation
- ✅ 0 gaps in regulatory data element coverage
- ✅ CDM validated by Payments SMEs and Compliance

---

## 2. Phase 1: CDM Design Principles & Methodology (Weeks 1-2) {#phase1}

**Total Effort:** 40 person-days (20 UK Lead + 20 India Eng 2)

### Activity 1.1: Guiding Principles Definition (Week 1) {#activity-1-1}

#### Task 1.1.1: ISO 20022 Foundation Analysis
**Effort:** 5 days (UK Lead: 3 days, India Eng 2: 2 days)
**Dependencies:** None
**Deliverable:** ISO 20022 foundation assessment

**Detailed Steps:**
1. **Analyze ISO 20022 Standard:**
   - Download ISO 20022 data dictionary (complete catalog)
   - Identify all payment-related message sets:
     - **pain (Payments Initiation):** pain.001, pain.002, pain.007, pain.008, pain.009-014, pain.017-018
     - **pacs (Payments Clearing & Settlement):** pacs.002, pacs.003, pacs.004, pacs.007, pacs.008, pacs.009, pacs.010, pacs.028
     - **camt (Cash Management):** camt.052, camt.053, camt.054, camt.056, camt.060
     - **acmt (Account Management):** acmt.001, acmt.002, etc.
     - **reda (Reference Data):** reda.001, etc.

2. **Extract Core ISO 20022 Entities:**
   - Document core message components (reusable across messages)
   - Group Header
   - Party Identification
   - Account Identification
   - Financial Institution Identification
   - Payment Type Information
   - Amount structures
   - Date/Time structures
   - Address structures
   - Document/Reference structures

3. **Map ISO 20022 to BofA Payment Products:**
   - Identify which ISO 20022 messages apply to which payment products
   - Example: pain.001 → ACH credit origination, Wire origination
   - Example: pacs.008 → FedNow, RTP, SEPA SCT Inst, SWIFT MX

**Outputs:**
- `cdm_iso20022_analysis.xlsx` - Complete ISO 20022 message catalog with BofA applicability
- `cdm_iso20022_core_components.xlsx` - Reusable message components

**Quality Check:**
- All relevant ISO 20022 messages identified?
- Core components extracted and documented?

---

#### Task 1.1.2: Define CDM Guiding Principles
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** Task 1.1.1
**Deliverable:** CDM guiding principles document

**Detailed Steps:**
1. Document 7 guiding principles:

**Principle 1: ISO 20022 as Canonical Foundation**
- ISO 20022 message structures as baseline
- Adopt ISO 20022 naming conventions, data types, code lists
- Rationale: Industry standard, regulatory adoption (SWIFT migration to MX), future-proof

**Principle 2: Extensibility for Proprietary Requirements**
- Allow extensions for BofA-specific fields (CashPro fields, internal IDs)
- Extensions namespace: `extensions` object in JSON
- Rationale: Balance between standardization and business needs

**Principle 3: Backward Compatibility During MT Transition**
- Support legacy SWIFT MT formats during multi-year transition to MX
- Map MT fields to CDM alongside MX fields
- Rationale: BofA and industry still processing MT messages until 2025-2027

**Principle 4: Regulatory Reporting as First-Class Design Driver**
- Every regulatory data element must be mappable to CDM
- Regulatory reporting fields prioritized in CDM design
- Rationale: Regulatory compliance is non-negotiable

**Principle 5: Analytics and AI-Readiness**
- CDM structure optimized for analytics queries (denormalization where appropriate)
- Feature engineering considerations (fraud detection, customer analytics)
- Rationale: Enable advanced analytics and ML use cases

**Principle 6: Multi-Product Harmonization**
- Single CDM for all payment products (not separate models per product)
- Product-specific extensions allowed, but core model shared
- Rationale: Enable cross-product analytics, reduce complexity

**Principle 7: Temporal Modeling for Historical Analysis**
- Slowly Changing Dimensions (SCD Type 2) for master data (Party, Account, FI)
- Full payment lifecycle events (status changes, amendments, cancellations)
- Rationale: Regulatory audit trails, historical trend analysis

**Outputs:**
- `DELIVERABLE_cdm_design_principles.docx` - Principles with rationale (15 pages)

---

#### Task 1.1.3: Domain-Driven Design (DDD) Methodology
**Effort:** 2 days (UK Lead: 2 days)
**Dependencies:** Task 1.1.2
**Deliverable:** DDD methodology document

**Detailed Steps:**
1. **Define Bounded Contexts:**
   - **Payment Instruction Context:** Core payment data (amount, parties, dates)
   - **Regulatory Compliance Context:** Screening, reporting, compliance data
   - **Operational Context:** Status, exceptions, manual interventions
   - **Reference Data Context:** Currencies, countries, codes, financial institutions

2. **Define Aggregates:**
   - **Payment Aggregate:** Payment Instruction (root), Parties, Accounts, Charges, Settlement, Status Events
   - **Compliance Aggregate:** Screening Result, AML Alert, Compliance Case
   - **Reference Aggregate:** Currency, Country, Financial Institution

3. **Define Domain Events:**
   - PaymentInitiated, PaymentValidated, PaymentCleared, PaymentSettled, PaymentReturned, PaymentCancelled
   - ScreeningCompleted, AlertRaised, CaseOpened, CaseClosed

4. **Event Sourcing Considerations:**
   - Evaluate event sourcing for payment lifecycle (all state changes captured)
   - Trade-offs: Complete audit trail vs. query complexity
   - Decision: Hybrid approach (events captured, but also current state maintained)

**Outputs:**
- `cdm_ddd_methodology.docx` - DDD approach documentation

---

### Activity 1.2: Reference Model Analysis (Week 2) {#activity-1-2}

#### Task 1.2.1: ISDA CDM Lessons Learned
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** Task 1.1.3
**Deliverable:** ISDA CDM analysis

**Detailed Steps:**
1. **Analyze ISDA Common Domain Model:**
   - Download ISDA CDM specifications (latest version)
   - Focus on derivatives lifecycle events (as analog to payment lifecycle)
   - Identify reusable patterns:
     - Event modeling approach
     - Lineage and provenance tracking
     - Rosetta DSL for model definition

2. **Extract Applicable Patterns:**
   - Lifecycle event modeling
   - Party role taxonomy
   - Document reference patterns
   - Regulatory reporting integration patterns

3. **Adapt to Payments Domain:**
   - Map ISDA patterns to payment lifecycle
   - Identify gaps (payments-specific requirements)

**Outputs:**
- `cdm_isda_cdm_analysis.pptx` - ISDA CDM lessons learned

---

#### Task 1.2.2: Digital Regulatory Reporting (DRR) Alignment
**Effort:** 2 days (UK Lead: 2 days)
**Dependencies:** Task 1.2.1
**Deliverable:** DRR alignment document

**Detailed Steps:**
1. **Analyze DRR Initiative:**
   - Review DRR principles (machine-readable regulations)
   - Identify regulatory reporting patterns

2. **Align CDM to DRR Principles:**
   - Embed regulatory codes and flags in CDM
   - Design CDM to support automated report generation
   - Map CDM to regulatory reporting templates

**Outputs:**
- `cdm_drr_alignment.docx`

---

#### Task 1.2.3: Consolidate Methodology
**Effort:** 2 days (UK Lead: 1 day, India Eng 2: 1 day)
**Dependencies:** Tasks 1.2.1, 1.2.2
**Deliverable:** Complete methodology document

**Detailed Steps:**
1. Consolidate all methodology inputs:
   - Guiding principles
   - DDD approach
   - ISDA CDM lessons
   - DRR alignment

2. Create master methodology document

**Outputs:**
- `DELIVERABLE_cdm_methodology.docx` - Complete CDM development methodology (25 pages)

---

## 3. Phase 2: Logical Common Domain Model (Weeks 3-8) {#phase2}

**Total Effort:** 120 person-days (60 UK Lead + 60 India Eng 2)

### Activity 2.1: Core Domain Entities (Weeks 3-5) {#activity-2-1}

#### Task 2.1.1: Payment Instruction Entity
**Effort:** 8 days (UK Lead: 5 days, India Eng 2: 3 days)
**Dependencies:** Phase 1 complete
**Deliverable:** Payment Instruction logical model

**Detailed Steps:**
1. **Define Payment Instruction Attributes:**

**(A) Identification:**
- payment_id (UUID, primary key, system-generated)
- end_to_end_id (ISO 20022: EndToEndId, business key)
- instruction_id (ISO 20022: InstrId)
- uetr (SWIFT Unique End-to-end Transaction Reference, for SWIFT payments)
- transaction_id (legacy system transaction ID)

**(B) Payment Type Classification:**
- payment_method (ENUM: 'WIRE', 'ACH', 'SWIFT_MT', 'SWIFT_MX', 'RTP', 'FEDNOW', 'SEPA_SCT', 'SEPA_SCT_INST', 'SEPA_SDD', 'BACS', 'FPS', 'CHAPS', 'ZELLE', 'CHECK', 'INTERNAL_TRANSFER')
- product_type (ISO 20022: CategoryPurpose)
- payment_instrument (ENUM: 'CREDIT_TRANSFER', 'DIRECT_DEBIT', 'CARD')
- priority (ENUM: 'HIGH', 'NORMAL', 'LOW')

**(C) Instruction Dates and Times:**
- creation_date_time (timestamp when instruction created)
- requested_execution_date (ISO 20022: ReqdExctnDt)
- interbank_settlement_date (ISO 20022: IntrBkSttlmDt, value date)
- acceptance_date_time (timestamp when accepted for processing)

**(D) Amount and Currency:**
- instructed_amount (STRUCT: {amount: DECIMAL(18,2), currency: CHAR(3)})
- interbank_settlement_amount (STRUCT: {amount: DECIMAL(18,2), currency: CHAR(3)}, post-FX)
- exchange_rate (if cross-currency)

**(E) Party References:**
- debtor_id (FK to Party, payer)
- creditor_id (FK to Party, payee)
- ultimate_debtor_id (FK to Party, if different from debtor)
- ultimate_creditor_id (FK to Party, if different from creditor)
- initiating_party_id (FK to Party, instruction originator)

**(F) Account References:**
- debtor_account_id (FK to Account)
- creditor_account_id (FK to Account)

**(G) Financial Institution References:**
- debtor_agent_id (FK to FinancialInstitution, debtor's bank)
- creditor_agent_id (FK to FinancialInstitution, creditor's bank)
- intermediary_agent_1_id (FK to FinancialInstitution, if routed through intermediary)
- intermediary_agent_2_id (FK to FinancialInstitution, second intermediary if applicable)

**(H) Charge Allocation:**
- charge_bearer (ISO 20022: ChrgBr, ENUM: 'DEBT', 'CRED', 'SHAR', 'SLEV')

**(I) Purpose and Remittance:**
- purpose_code (ISO 20022 external code list, e.g., 'SALA' for salary, 'SUPP' for supplier payment)
- category_purpose (ISO 20022: CtgyPurp)
- remittance_info_id (FK to RemittanceInformation)

**(J) Regulatory Reporting:**
- regulatory_reporting_code (ISO 20022: RgltryRptg)
- cross_border_flag (BOOLEAN)
- regulatory_product_type (e.g., FinCEN product code for CTR/SAR)

**(K) Status and Lifecycle:**
- current_status (ENUM: 'PENDING', 'VALIDATED', 'ACCEPTED', 'IN_PROCESS', 'SETTLED', 'RETURNED', 'CANCELLED', 'FAILED')
- current_status_timestamp

**(L) Operational:**
- processing_region (ENUM: 'US', 'EU', 'UK', 'APAC', 'LATAM')
- processing_channel (ENUM: 'CASHPRO', 'ONLINE_BANKING', 'BRANCH', 'API', 'FILE_UPLOAD')

**(M) Extensions:**
- extensions (JSON, for product-specific fields, e.g., CashPro approval workflow IDs, ACH addenda, SWIFT MT field 72)

2. **Define Logical Data Types:**
- Map to standard data types (STRING, DECIMAL, TIMESTAMP, BOOLEAN, ENUM, STRUCT, ARRAY, JSON)
- Document precision and scale for DECIMAL
- Document format for dates (ISO 8601)

3. **Define Constraints:**
- NOT NULL constraints
- UNIQUE constraints (end_to_end_id within partition)
- CHECK constraints (amount > 0, valid currency codes)
- Referential integrity (foreign keys)

4. **Cross-Reference to ISO 20022:**
- Map each attribute to ISO 20022 message element (if applicable)
- Document XPath for ISO 20022 XML messages

**Outputs:**
- `cdm_logical_payment_instruction.xlsx` - Complete attribute specification (150+ rows)
- `cdm_payment_instruction_iso20022_mapping.xlsx` - ISO 20022 cross-reference

**Quality Check:**
- All ISO 20022 pain/pacs message fields covered?
- Regulatory reporting codes included?

---

#### Task 2.1.2: Party Entity
**Effort:** 6 days (UK Lead: 4 days, India Eng 2: 2 days)
**Dependencies:** Task 2.1.1
**Deliverable:** Party logical model

**Detailed Steps:**
1. **Define Party Attributes:**

**(A) Identification:**
- party_id (UUID, primary key, SCD Type 2 surrogate key)
- party_business_id (natural key, e.g., customer ID, LEI, BIC)
- party_type (ENUM: 'INDIVIDUAL', 'CORPORATE', 'FINANCIAL_INSTITUTION', 'GOVERNMENT')

**(B) Party Name:**
- name (full name or legal entity name)
- name_prefix (Mr., Ms., Dr., etc., for individuals)
- first_name (for individuals)
- middle_name
- last_name
- legal_entity_name (for corporates)

**(C) Identification Schemes:**
- identifiers (ARRAY of STRUCT: {scheme: STRING, identifier: STRING}):
  - ISO 20022 ID schemes: BIC, LEI, DUNS, Tax ID (TIN, SSN, EIN), National ID, Passport, Driver's License
  - Example: {scheme: 'LEI', identifier: '54930084UKLVMY22DS16'}

**(D) Address:**
- address (STRUCT):
  - address_type (ENUM: 'POSTAL', 'RESIDENTIAL', 'BUSINESS', 'REGISTERED')
  - street_name
  - building_number
  - building_name
  - floor
  - post_box
  - room
  - post_code
  - town_name
  - town_location_name (district/suburb)
  - district_name (state/province)
  - country_sub_division
  - country (ISO 3166 alpha-2 code)
  - address_line (ARRAY, for unstructured addresses)

**(E) Contact Information:**
- phone_number
- mobile_number
- email_address

**(F) Dates:**
- date_of_birth (for individuals)
- place_of_birth (city, country)

**(G) Organizational:**
- country_of_residence (for individuals)
- country_of_registration (for corporates)
- incorporation_date (for corporates)

**(H) SCD Type 2 Fields:**
- effective_from_date (when this version became effective)
- effective_to_date (when this version was superseded, NULL for current version)
- is_current (BOOLEAN, TRUE for current version)
- record_hash (hash of business attributes for change detection)

**(I) Audit:**
- created_at
- updated_at
- created_by_user_id
- updated_by_user_id

**(J) Extensions:**
- extensions (JSON, for product-specific party data)

2. **Map to ISO 20022:**
- PartyIdentification structures (Dbtr, Cdtr, UltmtDbtr, UltmtCdtr)
- PostalAddress structures

**Outputs:**
- `cdm_logical_party.xlsx` - Complete Party specification (80+ attributes)

---

#### Task 2.1.3: Account Entity
**Effort:** 4 days (UK Lead: 3 days, India Eng 2: 1 day)
**Dependencies:** Task 2.1.1
**Deliverable:** Account logical model

**Detailed Steps:**
1. **Define Account Attributes:**

**(A) Identification:**
- account_id (UUID, primary key, SCD Type 2 surrogate key)
- account_number (business key, e.g., IBAN, account number)
- account_identification_scheme (ISO 20022: IBAN, BBAN, UPIC, etc.)

**(B) Account Type:**
- account_type_code (ISO 20022: CACC, SVGS, CASH, etc.)
- account_sub_type (e.g., DDA, SAV, MMDA)

**(C) Currency:**
- currency (ISO 4217 currency code)
- is_multi_currency (BOOLEAN)

**(D) Account Owner:**
- account_owner_party_id (FK to Party)

**(E) Account Servicer:**
- servicer_fi_id (FK to FinancialInstitution, bank servicing the account)

**(F) Account Relationship:**
- account_relationship (ENUM: 'NOSTRO', 'VOSTRO', 'CUSTOMER', 'INTERNAL')
- is_internal_account (BOOLEAN)

**(G) Account Status:**
- account_status (ENUM: 'ACTIVE', 'DORMANT', 'CLOSED', 'BLOCKED')

**(H) Account Name:**
- account_name (name on account)

**(I) SCD Type 2 Fields:**
- effective_from_date, effective_to_date, is_current, record_hash

**(J) Audit:**
- created_at, updated_at

**Outputs:**
- `cdm_logical_account.xlsx`

---

#### Task 2.1.4: Financial Institution Entity
**Effort:** 4 days (UK Lead: 3 days, India Eng 2: 1 day)
**Dependencies:** Task 2.1.1
**Deliverable:** Financial Institution logical model

**Detailed Steps:**
1. **Define Financial Institution Attributes:**

**(A) Identification:**
- fi_id (UUID, primary key, SCD Type 2)
- bic (SWIFT BIC code, 8 or 11 characters)
- lei (Legal Entity Identifier)
- national_clearing_code (e.g., ABA routing number in US, sort code in UK)
- clearing_system_id (ISO 20022: ClrSysId, e.g., 'USABA', 'GBDSC')

**(B) Institution Name:**
- institution_name
- institution_name_short

**(C) Address:**
- address (STRUCT, same structure as Party address)

**(D) Branch Information:**
- branch_identification
- branch_name
- branch_address

**(E) Clearing System Membership:**
- clearing_system_member_id (member ID in clearing system)
- clearing_systems (ARRAY of clearing systems: Fedwire, CHIPS, SWIFT, TARGET2, CHAPS, BACS, SEPA)

**(F) Correspondent Relationships:**
- correspondent_banks (ARRAY of FK to other FinancialInstitution entities)

**(G) Contact:**
- contact_phone, contact_email

**(H) SCD Type 2 Fields:**
- effective_from_date, effective_to_date, is_current, record_hash

**Outputs:**
- `cdm_logical_financial_institution.xlsx`

---

#### Task 2.1.5: Payment Status Entity
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** Task 2.1.1
**Deliverable:** Payment Status logical model

**Detailed Steps:**
1. **Define Payment Status Event Attributes:**

**(A) Identification:**
- status_event_id (UUID, primary key)
- payment_id (FK to PaymentInstruction)

**(B) Status:**
- status_code (ISO 20022 status codes: ACCP, ACSC, ACSP, RJCT, PDNG, etc.)
- status_reason_code (ISO 20022 reason codes)
- status_reason_additional_info (free text)

**(C) Timestamp:**
- status_timestamp (when status change occurred)

**(D) Processing Details:**
- processing_step (ENUM: 'VALIDATION', 'SCREENING', 'CLEARING', 'SETTLEMENT', etc.)
- processing_system (system that updated status)

**(E) Audit:**
- updated_by_user_id (if manual status change)

**Outputs:**
- `cdm_logical_status_event.xlsx`

---

### Activity 2.2: Settlement & Charges Entities (Week 6) {#activity-2-2}

#### Task 2.2.1: Settlement Entity
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** Task 2.1.1
**Deliverable:** Settlement logical model

**Detailed Steps:**
1. **Define Settlement Attributes:**
- settlement_id, payment_id (FK)
- settlement_method (ISO 20022: INDA, INGA, COVE, etc.)
- settlement_date
- settlement_amount (STRUCT: amount, currency)
- settlement_account_id (FK to Account, Nostro account)
- clearing_system_reference
- settlement_timestamp

**Outputs:**
- `cdm_logical_settlement.xlsx`

---

#### Task 2.2.2: Charge Entity
**Effort:** 2 days (UK Lead: 1 day, India Eng 2: 1 day)
**Dependencies:** Task 2.1.1
**Deliverable:** Charge logical model

**Detailed Steps:**
1. **Define Charge Attributes:**
- charge_id, payment_id (FK)
- charge_type (ISO 20022: CMSW, CMDT, CMRF, etc.)
- charge_amount (STRUCT: amount, currency)
- charge_bearer (DEBT, CRED, SHAR)
- tax_amount (if applicable)
- tax_type

**Outputs:**
- `cdm_logical_charge.xlsx`

---

### Activity 2.3: Regulatory & Remittance Entities (Week 6) {#activity-2-3}

#### Task 2.3.1: Regulatory Information Entity
**Effort:** 4 days (UK Lead: 3 days, India Eng 2: 1 day)
**Dependencies:** Task 2.1.1
**Deliverable:** Regulatory Information logical model

**Detailed Steps:**
1. **Define Regulatory Attributes:**
- regulatory_info_id, payment_id (FK)
- regulatory_authority (e.g., 'FINCEN', 'FCA', 'MAS')
- regulatory_reporting_type (e.g., 'CTR', 'SAR', 'IFTI', 'PSD2_SCA')
- transaction_reporting_id (unique ID for regulatory report)
- regulatory_product_code (product classification for regulatory purposes)
- cross_border_indicator
- purpose_of_payment (narrative for regulatory purposes)
- ultimate_beneficial_owner_id (FK to Party, for AML)
- sanctions_screening_result_id (FK to ScreeningResult)
- aml_risk_score (numeric risk score)
- regulatory_flags (JSON, jurisdiction-specific flags)

**Outputs:**
- `cdm_logical_regulatory_info.xlsx`

---

#### Task 2.3.2: Remittance Information Entity
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** Task 2.1.1
**Deliverable:** Remittance Information logical model

**Detailed Steps:**
1. **Define Remittance Attributes:**

**(A) Unstructured Remittance:**
- remittance_info_id, payment_id (FK)
- unstructured_remittance (ARRAY of STRING, up to 4 lines, 140 characters each)

**(B) Structured Remittance:**
- creditor_reference_type (ISO 11649 creditor reference)
- creditor_reference_value
- invoice_number (ARRAY of invoice references)
- invoice_date
- invoice_amount
- related_document_number
- related_document_date
- additional_remittance_info (ARRAY of STRUCT for multiple remittance items)

**Outputs:**
- `cdm_logical_remittance_info.xlsx`

---

### Activity 2.4: Payment Chain & Supporting Entities (Week 7) {#activity-2-4}

#### Task 2.4.1: Payment Chain Entity
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** Task 2.1.1
**Deliverable:** Payment Chain logical model

**Detailed Steps:**
1. **Define Payment Chain Attributes:**
- payment_chain_id, payment_id (FK to current payment)
- original_instruction_id (FK to original payment, if this is return/amendment)
- parent_payment_id (FK to parent payment, if cover payment)
- related_payment_ids (ARRAY of related payments)
- chain_relationship_type (ENUM: 'RETURN', 'RECALL', 'AMENDMENT', 'COVER', 'RELATED')
- return_reason_code (ISO 20022)

**Outputs:**
- `cdm_logical_payment_chain.xlsx`

---

#### Task 2.4.2: Reference Data Entities
**Effort:** 4 days (UK Lead: 2 days, India Eng 2: 2 days)
**Dependencies:** None (supporting entities)
**Deliverable:** Reference data logical models

**Detailed Steps:**
1. **Currency Reference:**
- currency_code (ISO 4217), currency_name, numeric_code, minor_units

2. **Country Reference:**
- country_code (ISO 3166 alpha-2), country_name, alpha-3_code, numeric_code, region

3. **Clearing System Reference:**
- clearing_system_code, clearing_system_name, country, type

4. **Purpose Code Reference:**
- purpose_code (ISO 20022 external code), purpose_description, category

5. **Charge Type Reference:**
- charge_type_code, charge_type_description

**Outputs:**
- `cdm_logical_reference_data.xlsx`

---

#### Task 2.4.3: Compliance & Screening Entities
**Effort:** 5 days (UK Lead: 3 days, India Eng 2: 2 days)
**Dependencies:** Task 2.1.1
**Deliverable:** Compliance entities logical model

**Detailed Steps:**
1. **Screening Result Entity:**
- screening_id, payment_id (FK), party_id (FK)
- screening_type (ENUM: 'SANCTIONS', 'AML', 'PEP', 'FRAUD')
- screening_list (e.g., 'OFAC_SDN', 'UN_SANCTIONS', 'EU_SANCTIONS')
- screening_result (ENUM: 'MATCH', 'POTENTIAL_MATCH', 'NO_MATCH')
- confidence_score (0-100%)
- matched_list_entry (reference to sanctions list entry)
- screening_timestamp
- false_positive_flag (if manually reviewed as false positive)

2. **AML Alert Entity:**
- alert_id, payment_id (FK)
- alert_type (e.g., 'STRUCTURING', 'UNUSUAL_PATTERN', 'HIGH_RISK_COUNTRY')
- alert_severity (ENUM: 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
- alert_details (JSON, detailed explanation)
- alert_status (ENUM: 'OPEN', 'UNDER_REVIEW', 'ESCALATED', 'CLOSED')
- investigation_notes
- assigned_analyst_id
- resolution_date

3. **Compliance Case Entity:**
- case_id, alert_id (FK), payment_id (FK)
- case_type (ENUM: 'SANCTIONS_HIT', 'SAR_FILING', 'INVESTIGATION')
- case_status (ENUM: 'OPEN', 'PENDING', 'CLOSED')
- case_priority
- case_owner_id
- sar_filing_required (BOOLEAN)
- sar_filing_date

**Outputs:**
- `cdm_logical_compliance_screening.xlsx`

---

#### Task 2.4.4: Operational Entities
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** Task 2.1.1
**Deliverable:** Operational entities logical model

**Detailed Steps:**
1. **Payment Exception Entity:**
- exception_id, payment_id (FK)
- exception_type (ENUM: 'VALIDATION_FAILURE', 'INSUFFICIENT_FUNDS', 'INVALID_ACCOUNT', 'DUPLICATE', 'TIMEOUT')
- exception_code, exception_description
- exception_timestamp
- resolution_status (ENUM: 'PENDING', 'RESOLVED', 'ESCALATED')
- resolution_action (e.g., 'RESUBMITTED', 'RETURNED', 'MANUAL_OVERRIDE')

2. **Manual Intervention Entity:**
- intervention_id, payment_id (FK)
- intervention_type (ENUM: 'APPROVAL', 'REPAIR', 'OVERRIDE', 'CANCELLATION')
- intervention_reason
- intervention_timestamp
- performed_by_user_id
- approval_required (BOOLEAN)
- approver_user_id

3. **Audit Trail Entity:**
- audit_id, payment_id (FK)
- audit_action (ENUM: 'CREATE', 'UPDATE', 'DELETE', 'STATUS_CHANGE', 'APPROVAL')
- audit_timestamp
- performed_by_user_id
- before_value (JSON), after_value (JSON)

**Outputs:**
- `cdm_logical_operational_entities.xlsx`

---

### Activity 2.5: Cross-Product Mapping (Week 8) {#activity-2-5}

#### Task 2.5.1: ACH → CDM Mapping
**Effort:** 5 days (UK Lead: 3 days, India Eng 2: 2 days)
**Dependencies:** Activity 2.1-2.4 complete
**Deliverable:** ACH to CDM mapping

**Detailed Steps:**
1. Map NACHA file format to CDM:
   - **File Header Record (Type 1):** Batch origination metadata
   - **Company/Batch Header Record (Type 5):** Company ID → initiating_party_id, Effective Entry Date → requested_execution_date
   - **Entry Detail Record (Type 6):**
     - Transaction Code → payment_method (PPD, CCD, WEB, etc.)
     - RDFI Routing Number → creditor_agent financial institution
     - DFI Account Number → creditor account
     - Amount → instructed_amount
     - Individual ID Number → creditor party identifier
     - Individual Name → creditor party name
     - Discretionary Data, Addenda Record Indicator → extensions
   - **Addenda Record (Type 7):** → remittance_info (unstructured or structured)
   - **Batch Control Record (Type 8):** Batch totals for reconciliation
   - **File Control Record (Type 9):** File totals

2. Map all SEC codes to payment_method extensions:
   - PPD (Prearranged Payment & Deposit) → payment_method: 'ACH', extensions.secCode: 'PPD'
   - CCD (Corporate Credit or Debit)
   - WEB (Internet-Initiated Entry)
   - TEL (Telephone-Initiated Entry)
   - CTX (Corporate Trade Exchange) with structured addenda
   - IAT (International ACH Transaction) with mandatory addenda

3. Map ACH return codes to status_reason_code:
   - R01 (Insufficient Funds) → status: 'RETURNED', reason: 'INSUFFICENT_FUNDS'
   - R02 (Account Closed)
   - R03 (No Account/Unable to Locate Account)
   - ... (all 80+ return codes)

4. Map NOC (Notification of Change) codes

**Outputs:**
- `cdm_mapping_ach_to_cdm.xlsx` - Complete NACHA field mapping (200+ fields)

**Quality Check:**
- All NACHA record types mapped?
- All SEC codes covered?
- All return codes mapped?

---

#### Task 2.5.2: Fedwire/CHIPS → CDM Mapping
**Effort:** 4 days (UK Lead: 3 days, India Eng 2: 1 day)
**Dependencies:** Activity 2.1-2.4 complete
**Deliverable:** Fedwire to CDM mapping

**Detailed Steps:**
1. Map Fedwire tag-value format to CDM:
   - **{1500} Message Type Indicator:** Determine payment type (Type 1000 vs. 1500)
   - **{1510} IMAD (Input Message Accountability Data):** → instruction_id
   - **{1520} OMAD (Output Message Accountability Data):** → settlement reference
   - **{2000} Amount:** → instructed_amount.amount
   - **{3100} Sender FI:** → debtor_agent (ABA routing, name, address)
   - **{3400} Receiver FI:** → creditor_agent
   - **{3600} Business Function Code:** → payment_method extension
   - **{4200} Beneficiary (Receiver) Info:** → creditor (account, name, address)
   - **{5000} Originator (Sender) Info:** → debtor
   - **{6000} Originator to Beneficiary Info:** → remittance_info (unstructured, up to 4 lines)
   - **{6100-6500} Additional Info:** Intermediary banks, previous message reference

2. Map Type 1500 (Customer Transfer Plus) additional fields:
   - Beneficiary reference
   - Originator reference
   - Related reference

**Outputs:**
- `cdm_mapping_fedwire_to_cdm.xlsx` - All Fedwire tags mapped (60+ tags)

---

#### Task 2.5.3: SWIFT MT → CDM Mapping
**Effort:** 6 days (UK Lead: 4 days, India Eng 2: 2 days)
**Dependencies:** Activity 2.1-2.4 complete
**Deliverable:** SWIFT MT to CDM mapping

**Detailed Steps:**
1. **MT103 (Single Customer Credit Transfer):**
   - Field 20 (Transaction Reference) → instruction_id
   - Field 23B (Bank Operation Code) → payment_type extension
   - Field 23E (Instruction Code) → processing_instructions
   - Field 32A (Value Date, Currency, Amount) → requested_execution_date, instructed_amount
   - Field 33B (Currency, Instructed Amount) → original amount if FX
   - Field 50A/F/K (Ordering Customer) → debtor (account, name, address)
   - Field 52A/D (Ordering Institution) → debtor_agent
   - Field 53A/B/D (Sender's Correspondent) → intermediary_agent_1
   - Field 54A/B/D (Receiver's Correspondent) → intermediary_agent_2
   - Field 56A/C/D (Intermediary) → additional intermediary
   - Field 57A/B/C/D (Account With Institution) → creditor_agent
   - Field 59/59A (Beneficiary) → creditor
   - Field 70 (Remittance Information) → remittance_info (unstructured)
   - Field 71A (Details of Charges) → charge_bearer
   - Field 71F/71G (Sender's/Receiver's Charges) → charge amounts
   - Field 72 (Sender to Receiver Information) → extensions (free-format instructions)
   - Field 77B (Regulatory Reporting) → regulatory_info

2. **MT103+ (STP-compliant MT103):** Same as MT103 with structured beneficiary/ordering customer

3. **MT202 (General FI Transfer):**
   - Similar structure to MT103 but for interbank transfers (no customer data)
   - Field 21 (Related Reference) → payment_chain original reference

4. **MT202COV (Cover for MT103):**
   - Links cover payment to underlying customer transfer
   - Field 50A/K (Ordering Customer from underlying) → ultimate_debtor
   - Field 59 (Beneficiary from underlying) → ultimate_creditor

**Outputs:**
- `cdm_mapping_swift_mt_to_cdm.xlsx` - MT103/MT202/MT202COV complete mapping (100+ fields)

---

#### Task 2.5.4: SWIFT MX (ISO 20022) → CDM Mapping
**Effort:** 5 days (UK Lead: 3 days, India Eng 2: 2 days)
**Dependencies:** Activity 2.1-2.4 complete, Task 1.1.1
**Deliverable:** SWIFT MX to CDM mapping

**Detailed Steps:**
1. **pain.001 (Customer Credit Transfer Initiation):** Direct mapping since CDM is ISO 20022-based
   - GrpHdr (Group Header) → instruction metadata
   - PmtInf (Payment Information) → payment batch info
   - CdtTrfTxInf (Credit Transfer Transaction Information) → PaymentInstruction entity (almost 1:1)

2. **pacs.008 (FI to FI Customer Credit Transfer):** Direct mapping
   - Similar structure to pain.001 but interbank perspective

3. **camt.053 (Bank to Customer Statement):** For reconciliation use cases
   - Ntry (Entry) → settled payment info

**Outputs:**
- `cdm_mapping_swift_mx_to_cdm.xlsx` - ISO 20022 message mapping

---

#### Task 2.5.5: RTP/FedNow → CDM Mapping
**Effort:** 4 days (UK Lead: 3 days, India Eng 2: 1 day)
**Dependencies:** Activity 2.1-2.4 complete
**Deliverable:** Real-time payments to CDM mapping

**Detailed Steps:**
1. Map RTP (The Clearing House) ISO 20022 messages:
   - RTP uses pain.013 (Creditor Payment Activation Request - Request for Payment)
   - RTP uses pacs.008 (Customer Credit Transfer)
   - Map to CDM (already ISO 20022-based)

2. Map FedNow (Federal Reserve) ISO 20022 messages:
   - FedNow uses pacs.008, pacs.002 (Payment Status Report), pacs.004 (Payment Return)
   - Map to CDM

3. Document real-time-specific fields:
   - payment_method: 'RTP' or 'FEDNOW'
   - SLA: sub-second processing
   - Irrevocability

**Outputs:**
- `cdm_mapping_rtp_fednow_to_cdm.xlsx`

---

#### Task 2.5.6: SEPA → CDM Mapping
**Effort:** 5 days (UK Lead: 3 days, India Eng 2: 2 days)
**Dependencies:** Activity 2.1-2.4 complete
**Deliverable:** SEPA to CDM mapping

**Detailed Steps:**
1. **SEPA Credit Transfer (SCT):** ISO 20022 pain.001, pacs.008 → CDM
2. **SEPA Instant Credit Transfer (SCT Inst):** pain.001, pacs.008 with instant processing
3. **SEPA Direct Debit (SDD Core and SDD B2B):** pain.008 (Direct Debit Initiation) → CDM
   - Mandate information → extensions.mandateId, extensions.sequenceType

**Outputs:**
- `cdm_mapping_sepa_to_cdm.xlsx`

---

#### Task 2.5.7: UK Payments (BACS/FPS/CHAPS) → CDM Mapping
**Effort:** 5 days (UK Lead: 4 days, India Eng 2: 1 day)
**Dependencies:** Activity 2.1-2.4 complete
**Deliverable:** UK payments to CDM mapping

**Detailed Steps:**
1. **BACS (Bulk ACH-like):** Proprietary format (Standard 18)
   - Direct Credit: Sort code, account number, amount, reference → CDM
   - Direct Debit: Similar to SEPA SDD

2. **Faster Payments (FPS):** ISO 20022-based (pain.001, pacs.008) → CDM

3. **CHAPS (High-value RTGS):** ISO 20022-based (pacs.008, pacs.009) → CDM

**Outputs:**
- `cdm_mapping_uk_payments_to_cdm.xlsx`

---

#### Task 2.5.8: Zelle → CDM Mapping
**Effort:** 2 days (UK Lead: 1 day, India Eng 2: 1 day)
**Dependencies:** Activity 2.1-2.4 complete
**Deliverable:** Zelle to CDM mapping

**Detailed Steps:**
1. Map Zelle proprietary format/API to CDM:
   - Sender phone/email → debtor identifier
   - Recipient phone/email → creditor identifier
   - Amount, message → instructed_amount, remittance_info
   - payment_method: 'ZELLE'

**Outputs:**
- `cdm_mapping_zelle_to_cdm.xlsx`

---

#### Task 2.5.9: Check/Image → CDM Mapping
**Effort:** 2 days (UK Lead: 1 day, India Eng 2: 1 day)
**Dependencies:** Activity 2.1-2.4 complete
**Deliverable:** Check to CDM mapping

**Detailed Steps:**
1. Map check clearing data (X9.37 image format) to CDM:
   - MICR line data → account, routing number
   - Check amount
   - Image reference → extensions.checkImageUrl
   - payment_method: 'CHECK'

**Outputs:**
- `cdm_mapping_check_to_cdm.xlsx`

---

### Activity 2.6: Reconciliation & Consolidation (Week 8) {#activity-2-6}

#### Task 2.6.1: Source-to-CDM Reconciliation
**Effort:** 5 days (UK Lead: 3 days, India Eng 2: 2 days)
**Dependencies:** Tasks 2.5.1-2.5.9 complete
**Deliverable:** 100% reconciliation matrix

**Detailed Steps:**
1. For each payment product, verify:
   - **Completeness:** All source fields mapped to CDM?
   - **Coverage:** All CDM entities populated by at least one source?
   - **Gaps:** Identify any source fields NOT mapped to CDM
   - **Enhancements:** Enhance CDM if critical fields missing

2. Reconciliation by product:
   - ACH: 200+ fields → CDM (target: 100%)
   - Fedwire: 60+ fields → CDM (target: 100%)
   - SWIFT MT: 100+ fields → CDM (target: 100%)
   - SWIFT MX: 1000+ fields → CDM (target: 99%+, some optional fields may not be used by BofA)
   - RTP/FedNow: 200+ fields → CDM (target: 100%)
   - SEPA: 300+ fields → CDM (target: 100%)
   - UK Payments: 150+ fields → CDM (target: 100%)
   - Zelle: 30+ fields → CDM (target: 100%)
   - Check: 20+ fields → CDM (target: 100%)

3. Document gaps and propose CDM enhancements

**Outputs:**
- `DELIVERABLE_cdm_reconciliation_matrix.xlsx` - Source-to-CDM reconciliation with gap analysis
- `cdm_enhancement_proposals.docx` - Proposed CDM enhancements for gaps

**Quality Gate:** 99%+ field coverage required before proceeding to physical model

---

#### Task 2.6.2: Logical Model Consolidation
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** Task 2.6.1
**Deliverable:** Complete logical CDM model

**Detailed Steps:**
1. Consolidate all entity specifications into master logical model document
2. Create Entity-Relationship Diagram (ERD):
   - 36+ entities
   - Primary keys, foreign keys, relationships (1:1, 1:N, M:N)
   - Cardinality

3. Document all attributes (2,000+ attributes across all entities)

4. Prepare executive summary (entity overview, coverage statistics)

**Outputs:**
- `DELIVERABLE_cdm_logical_model_complete.docx` - Complete logical model (150+ pages)
- `cdm_erd.vsdx` - Entity-Relationship Diagram
- `cdm_logical_model_executive_summary.pptx` - Executive summary

**Quality Gate:** Payments SME review and approval required

---

## 4. Phase 3: Physical Common Domain Model (Weeks 9-14) {#phase3}

**Total Effort:** 120 person-days (60 UK Lead + 60 India Eng 2)

### Activity 3.1: JSON Schema Development (Weeks 9-11) {#activity-3-1}

#### Task 3.1.1: JSON Schema Design Principles
**Effort:** 2 days (UK Lead: 2 days)
**Dependencies:** Logical model complete
**Deliverable:** JSON Schema design standards

**Detailed Steps:**
1. Define JSON Schema standards:
   - **Schema Draft:** JSON Schema Draft 2020-12
   - **Modularity:** Separate files for reusable components (Party, Account, Amount, DateTime, Address)
   - **Naming:** camelCase for properties, PascalCase for schema titles
   - **Documentation:** `description` field for every property and schema
   - **Validation:** Embedded validation rules (format, pattern, enum, min/max)
   - **Extensibility:** `additionalProperties: false` for strict validation, but `extensions` object allows flexibility

2. Define schema organization:
```
/schemas
  /core
    payment-instruction.schema.json
    party.schema.json
    account.schema.json
    financial-institution.schema.json
    amount.schema.json (reusable)
    date-time.schema.json (reusable)
    address.schema.json (reusable)
  /status
    payment-status.schema.json
  /settlement
    settlement.schema.json
  /regulatory
    regulatory-reporting.schema.json
    screening-result.schema.json
  /remittance
    remittance-information.schema.json
  /reference
    currency.schema.json
    country.schema.json
    purpose-codes.schema.json
  /products (extends core)
    ach-payment.schema.json
    wire-payment.schema.json
    swift-payment.schema.json
  /analytics
    payment-event.schema.json (event sourcing)
```

**Outputs:**
- `cdm_json_schema_standards.docx`

---

#### Task 3.1.2: Core Schemas Development
**Effort:** 10 days (UK Lead: 6 days, India Eng 2: 4 days)
**Dependencies:** Task 3.1.1
**Deliverable:** Core JSON schemas

**Detailed Steps:**
1. Develop JSON Schema for core entities:

**payment-instruction.schema.json** (example structure):
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://bofa.com/schemas/core/payment-instruction.schema.json",
  "title": "PaymentInstruction",
  "description": "Core payment instruction entity representing a payment order in the GPS Common Domain Model",
  "type": "object",
  "required": ["paymentId", "instructedAmount", "debtorId", "creditorId"],
  "properties": {
    "paymentId": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for the payment instruction (UUID v4)"
    },
    "endToEndId": {
      "type": "string",
      "maxLength": 35,
      "description": "ISO 20022 End-to-End Identification (business key)"
    },
    "instructedAmount": {
      "$ref": "amount.schema.json#/$defs/Amount",
      "description": "Instructed payment amount and currency"
    },
    "paymentMethod": {
      "type": "string",
      "enum": ["WIRE", "ACH", "SWIFT_MT", "SWIFT_MX", "RTP", "FEDNOW", "SEPA_SCT", "SEPA_SCT_INST", "ZELLE"],
      "description": "Payment method/product type"
    },
    "debtorId": {
      "type": "string",
      "format": "uuid",
      "description": "Reference to debtor Party (foreign key)"
    },
    "creditorId": {
      "type": "string",
      "format": "uuid",
      "description": "Reference to creditor Party (foreign key)"
    },
    "extensions": {
      "type": "object",
      "description": "Product-specific extensions (flexible JSON object)",
      "additionalProperties": true
    }
  },
  "additionalProperties": false
}
```

**amount.schema.json** (reusable component):
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://bofa.com/schemas/core/amount.schema.json",
  "title": "Amount",
  "$defs": {
    "Amount": {
      "type": "object",
      "required": ["amount", "currency"],
      "properties": {
        "amount": {
          "type": "number",
          "multipleOf": 0.01,
          "minimum": 0,
          "description": "Numeric amount value"
        },
        "currency": {
          "type": "string",
          "pattern": "^[A-Z]{3}$",
          "description": "ISO 4217 currency code (e.g., USD, EUR, GBP)"
        }
      }
    }
  }
}
```

2. Develop all core schemas (payment-instruction, party, account, financial-institution, amount, date-time, address)

**Outputs:**
- `/schemas/core/*.schema.json` - 10 core schemas
- `cdm_json_schema_samples.json` - Sample JSON documents for each schema

---

#### Task 3.1.3: Supporting Schemas Development
**Effort:** 6 days (UK Lead: 3 days, India Eng 2: 3 days)
**Dependencies:** Task 3.1.2
**Deliverable:** Supporting JSON schemas

**Detailed Steps:**
1. Develop schemas for:
   - status/, settlement/, regulatory/, remittance/, reference/, compliance/, operational/

**Outputs:**
- `/schemas/*/*.schema.json` - 20+ supporting schemas

---

#### Task 3.1.4: Product-Specific Schemas
**Effort:** 5 days (UK Lead: 3 days, India Eng 2: 2 days)
**Dependencies:** Task 3.1.2
**Deliverable:** Product extension schemas

**Detailed Steps:**
1. Develop product-specific schemas that extend core payment-instruction:

**ach-payment.schema.json** (extends payment-instruction):
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://bofa.com/schemas/products/ach-payment.schema.json",
  "title": "ACHPayment",
  "description": "ACH-specific payment extending PaymentInstruction",
  "allOf": [
    {
      "$ref": "../core/payment-instruction.schema.json"
    },
    {
      "type": "object",
      "properties": {
        "extensions": {
          "type": "object",
          "properties": {
            "secCode": {
              "type": "string",
              "enum": ["PPD", "CCD", "WEB", "TEL", "CTX", "IAT"],
              "description": "NACHA SEC (Standard Entry Class) code"
            },
            "companyId": {
              "type": "string",
              "maxLength": 10,
              "description": "Company Identification (originating company)"
            },
            "addendaRecords": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "addendaType": {"type": "string"},
                  "paymentRelatedInformation": {"type": "string", "maxLength": 80}
                }
              },
              "description": "ACH addenda records (Type 7)"
            }
          }
        }
      }
    }
  ]
}
```

2. Develop all product schemas (ach, wire, swift, sepa, rtp, etc.)

**Outputs:**
- `/schemas/products/*.schema.json` - 8 product schemas

---

#### Task 3.1.5: Schema Validation & Testing
**Effort:** 3 days (UK Lead: 1 day, India Eng 2: 2 days)
**Dependencies:** Tasks 3.1.2-3.1.4
**Deliverable:** Validated schemas

**Detailed Steps:**
1. Validate all schemas:
   - JSON Schema syntax validation
   - Cross-reference validation (verify all `$ref` links resolve)
   - Sample document validation (validate sample JSON documents against schemas)

2. Automated testing:
   - Python script using `jsonschema` library
   - Test positive cases (valid documents pass)
   - Test negative cases (invalid documents fail with expected errors)

**Outputs:**
- `cdm_schema_validation_report.txt` - Validation results
- `cdm_schema_test_suite.py` - Automated test suite

---

### Activity 3.2: Delta Lake DDL Development (Weeks 12-13) {#activity-3-2}

#### Task 3.2.1: Delta Lake Table Design Principles
**Effort:** 2 days (UK Lead: 2 days)
**Dependencies:** JSON schemas complete
**Deliverable:** Delta Lake design standards

**Detailed Steps:**
1. Define Delta Lake table design principles:
   - **Partitioning Strategy:** By date (year, month), region, product_type for payment_instruction
   - **Clustering:** Liquid Clustering for high-cardinality columns (debtor_id, creditor_id)
   - **Data Types:** Map JSON Schema types to Delta Lake/Spark SQL types
   - **SCD Type 2:** For Party, Account, FinancialInstitution tables
   - **Change Data Feed:** Enable for all tables (regulatory audit trail)
   - **Constraints:** NOT NULL, CHECK constraints

2. Define Bronze/Silver/Gold layering:
   - **Bronze:** Raw message formats (JSON/XML blobs)
   - **Silver:** CDM-conformant tables (payment_instruction, party, account, etc.)
   - **Gold:** Aggregated data products

**Outputs:**
- `cdm_delta_lake_design_standards.docx`

---

#### Task 3.2.2: Silver Layer DDL - Core Tables
**Effort:** 8 days (UK Lead: 5 days, India Eng 2: 3 days)
**Dependencies:** Task 3.2.1
**Deliverable:** Core table DDL

**Detailed Steps:**
1. Develop Delta Lake DDL for core tables:

**payment_instruction table:**
```sql
CREATE TABLE IF NOT EXISTS cdm_silver.payments.payment_instruction (
  -- Identification
  payment_id STRING NOT NULL COMMENT 'UUID v4 primary key',
  end_to_end_id STRING COMMENT 'ISO 20022 End-to-End Identification',
  instruction_id STRING COMMENT 'ISO 20022 Instruction Identification',
  uetr STRING COMMENT 'SWIFT Unique End-to-end Transaction Reference',

  -- Payment Type
  payment_method STRING NOT NULL COMMENT 'Payment method (WIRE, ACH, SWIFT_MT, etc.)',
  product_type STRING COMMENT 'ISO 20022 Category Purpose',

  -- Dates
  creation_date_time TIMESTAMP NOT NULL COMMENT 'Instruction creation timestamp',
  requested_execution_date DATE COMMENT 'ISO 20022 Requested Execution Date',
  interbank_settlement_date DATE COMMENT 'Value date',

  -- Amount
  instructed_amount STRUCT<amount: DECIMAL(18,2), currency: STRING> NOT NULL COMMENT 'Instructed amount and currency',
  interbank_settlement_amount STRUCT<amount: DECIMAL(18,2), currency: STRING> COMMENT 'Settlement amount (post-FX)',

  -- Parties (foreign keys)
  debtor_id STRING NOT NULL COMMENT 'FK to Party (debtor)',
  creditor_id STRING NOT NULL COMMENT 'FK to Party (creditor)',
  ultimate_debtor_id STRING COMMENT 'FK to Party (ultimate debtor)',
  ultimate_creditor_id STRING COMMENT 'FK to Party (ultimate creditor)',

  -- Accounts (foreign keys)
  debtor_account_id STRING NOT NULL COMMENT 'FK to Account (debtor account)',
  creditor_account_id STRING NOT NULL COMMENT 'FK to Account (creditor account)',

  -- Financial Institutions (foreign keys)
  debtor_agent_id STRING NOT NULL COMMENT 'FK to FinancialInstitution (debtor bank)',
  creditor_agent_id STRING NOT NULL COMMENT 'FK to FinancialInstitution (creditor bank)',
  intermediary_agent_1_id STRING COMMENT 'FK to FinancialInstitution (intermediary 1)',
  intermediary_agent_2_id STRING COMMENT 'FK to FinancialInstitution (intermediary 2)',

  -- Charges
  charge_bearer STRING COMMENT 'ISO 20022 Charge Bearer (DEBT, CRED, SHAR)',

  -- Remittance
  remittance_info_id STRING COMMENT 'FK to RemittanceInformation',

  -- Regulatory
  purpose_code STRING COMMENT 'ISO 20022 Purpose Code',
  cross_border_flag BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Cross-border payment indicator',
  regulatory_product_type STRING COMMENT 'Regulatory product classification',

  -- Status
  current_status STRING NOT NULL COMMENT 'Current payment status',
  current_status_timestamp TIMESTAMP NOT NULL COMMENT 'Current status timestamp',

  -- Operational
  processing_region STRING NOT NULL COMMENT 'Processing region (US, EU, UK, APAC, LATAM)',
  processing_channel STRING COMMENT 'Processing channel (CASHPRO, API, etc.)',

  -- Extensions
  extensions STRING COMMENT 'JSON string for product-specific extensions',

  -- Audit
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record creation timestamp',
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record update timestamp',

  -- Partitioning columns
  partition_year INT NOT NULL COMMENT 'Partition by year',
  partition_month INT NOT NULL COMMENT 'Partition by month',
  region STRING NOT NULL COMMENT 'Partition by region',
  product_type_partition STRING NOT NULL COMMENT 'Partition by product type'
)
USING DELTA
PARTITIONED BY (partition_year, partition_month, region, product_type_partition)
CLUSTER BY (debtor_id, creditor_id)
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.columnMapping.mode' = 'name',
  'delta.minReaderVersion' = '2',
  'delta.minWriterVersion' = '5',
  'delta.checkpoint.writeStatsAsStruct' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
)
COMMENT 'Core payment instruction entity - Common Domain Model';

-- Constraints
ALTER TABLE cdm_silver.payments.payment_instruction
ADD CONSTRAINT payment_instruction_pk PRIMARY KEY (payment_id);

ALTER TABLE cdm_silver.payments.payment_instruction
ADD CONSTRAINT amount_positive CHECK (instructed_amount.amount > 0);

ALTER TABLE cdm_silver.payments.payment_instruction
ADD CONSTRAINT currency_iso4217 CHECK (LENGTH(instructed_amount.currency) = 3);
```

2. Develop all core table DDLs (party, account, financial_institution, status_event, settlement, charge, regulatory_info, remittance_info, payment_chain, screening_result, aml_alert, compliance_case, payment_exception)

**Outputs:**
- `cdm_ddl_silver_core_tables.sql` - All core table DDLs (10 tables, 800+ lines of SQL)

---

#### Task 3.2.3: Silver Layer DDL - Reference & Supporting Tables
**Effort:** 4 days (UK Lead: 2 days, India Eng 2: 2 days)
**Dependencies:** Task 3.2.2
**Deliverable:** Reference table DDL

**Detailed Steps:**
1. Develop DDL for reference and supporting tables:
   - currency, country, clearing_system, purpose_code, charge_type

**Outputs:**
- `cdm_ddl_silver_reference_tables.sql`

---

#### Task 3.2.4: Bronze Layer DDL
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** None
**Deliverable:** Bronze layer DDL

**Detailed Steps:**
1. Design Bronze layer for raw message storage:

```sql
CREATE TABLE IF NOT EXISTS cdm_bronze.payments.raw_messages (
  message_id STRING NOT NULL COMMENT 'Unique message ID',
  source_system STRING NOT NULL COMMENT 'Source system (SWIFT, NACHA, CashPro, etc.)',
  message_type STRING NOT NULL COMMENT 'Message type (MT103, pain.001, ACH, etc.)',
  message_format STRING NOT NULL COMMENT 'Format (XML, FIN, TAG_VALUE, FIXED_WIDTH, JSON)',
  message_content STRING NOT NULL COMMENT 'Raw message content (full text)',
  ingestion_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() COMMENT 'Ingestion timestamp',
  partition_date DATE NOT NULL COMMENT 'Partition by date'
)
USING DELTA
PARTITIONED BY (partition_date, source_system)
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Bronze layer - raw payment messages';
```

**Outputs:**
- `cdm_ddl_bronze_tables.sql`

---

#### Task 3.2.5: Gold Layer DDL
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** Task 3.2.2
**Deliverable:** Gold layer DDL

**Detailed Steps:**
1. Design Gold layer for aggregated data products:

**Example: daily_payment_summary:**
```sql
CREATE TABLE IF NOT EXISTS cdm_gold.analytics.daily_payment_summary (
  summary_date DATE NOT NULL,
  region STRING NOT NULL,
  payment_method STRING NOT NULL,
  currency STRING NOT NULL,

  -- Metrics
  total_payment_count BIGINT NOT NULL,
  total_payment_volume DECIMAL(20,2) NOT NULL,
  avg_payment_amount DECIMAL(18,2),
  median_payment_amount DECIMAL(18,2),

  -- Status breakdown
  count_settled BIGINT,
  count_pending BIGINT,
  count_returned BIGINT,
  count_failed BIGINT,

  -- Calculated at
  calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
USING DELTA
PARTITIONED BY (summary_date, region)
COMMENT 'Gold layer - Daily payment summary data product';
```

2. Design additional Gold tables for common analytics use cases

**Outputs:**
- `cdm_ddl_gold_tables.sql`

---

### Activity 3.3: Physical Model Documentation (Week 14) {#activity-3-3}

#### Task 3.3.1: Consolidate Physical Model
**Effort:** 5 days (UK Lead: 3 days, India Eng 2: 2 days)
**Dependencies:** Activities 3.1, 3.2 complete
**Deliverable:** Complete physical CDM model

**Detailed Steps:**
1. Consolidate all physical model artifacts:
   - All JSON schemas (40+ schemas)
   - All Delta Lake DDLs (30+ tables across Bronze/Silver/Gold)
   - Sample JSON documents
   - Sample SQL queries

2. Create physical data model diagrams:
   - Bronze layer diagram
   - Silver layer ERD (with foreign keys)
   - Gold layer diagram

3. Document partitioning and clustering strategies

4. Document Unity Catalog structure:
   - Catalogs: cdm_bronze, cdm_silver, cdm_gold
   - Schemas: payments, compliance, reference, analytics

**Outputs:**
- `DELIVERABLE_cdm_physical_model_complete.docx` - Complete physical model (200+ pages)
- `cdm_physical_erd.vsdx` - Physical ERD
- `cdm_unity_catalog_structure.xlsx` - Catalog/schema/table hierarchy

---

#### Task 3.3.2: Sample Data & Query Examples
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** Task 3.3.1
**Deliverable:** Sample data and queries

**Detailed Steps:**
1. Create sample data for each CDM entity:
   - Generate realistic sample JSON documents (100+ samples)
   - Generate SQL INSERT statements for Delta Lake tables

2. Create sample queries:
   - Query 1: Retrieve payment with full party/account details (JOIN)
   - Query 2: Regulatory report generation (CTR)
   - Query 3: Payment status history
   - Query 4: Cross-border payments by corridor

**Outputs:**
- `cdm_sample_data.json` - Sample JSON documents
- `cdm_sample_queries.sql` - 20+ sample queries

---

## 5. Phase 4: CDM Governance Framework (Weeks 15-16) {#phase4}

**Total Effort:** 80 person-days (40 UK Lead + 40 India Eng 2)

### Activity 4.1: Model Governance (Week 15) {#activity-4-1}

#### Task 4.1.1: Change Control Process
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** Physical model complete
**Deliverable:** CDM change control process

**Detailed Steps:**
1. Define CDM change request process:
   - Change request template (requestor, rationale, impact analysis)
   - Impact categories (breaking change, non-breaking change, enhancement)
   - Review and approval workflow (CDM Working Group → Architecture Review Board)
   - Implementation timeline

2. Define change categories:
   - **Breaking Change:** Removing field, changing data type, changing cardinality (requires major version increment)
   - **Non-Breaking Change:** Adding optional field, adding enumeration value (minor version)
   - **Enhancement:** Adding new entity, adding extensions (minor version)

**Outputs:**
- `cdm_change_control_process.docx`
- `cdm_change_request_template.docx`

---

#### Task 4.1.2: Version Management Strategy
**Effort:** 2 days (UK Lead: 2 days)
**Dependencies:** Task 4.1.1
**Deliverable:** Versioning strategy

**Detailed Steps:**
1. Define semantic versioning for CDM:
   - **Major.Minor.Patch** (e.g., 1.0.0)
   - Major: Breaking changes
   - Minor: Non-breaking additions
   - Patch: Bug fixes, documentation

2. Schema version tracking:
   - `$schema` property in JSON Schema includes version
   - Delta Lake table properties include CDM version

3. Backward compatibility policy:
   - Support N-1 major version for 12 months
   - Deprecation notices for fields to be removed

**Outputs:**
- `cdm_version_management_strategy.docx`

---

#### Task 4.1.3: Extension Guidelines
**Effort:** 2 days (UK Lead: 1 day, India Eng 2: 1 day)
**Dependencies:** Task 4.1.2
**Deliverable:** Extension guidelines

**Detailed Steps:**
1. Define guidelines for `extensions` object:
   - Naming conventions (camelCase, descriptive names)
   - When to use extensions vs. core model change
   - Extension documentation requirements
   - Extension approval process (simpler than core model change)

**Outputs:**
- `cdm_extension_guidelines.docx`

---

#### Task 4.1.4: Collibra Integration for CDM
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** Task 4.1.1
**Deliverable:** Collibra integration plan

**Detailed Steps:**
1. Define CDM metadata in Collibra:
   - Import CDM entities as Business Assets
   - Import CDM attributes as Data Attributes
   - Link CDM to source systems (lineage)
   - Link CDM to regulations (compliance)

2. Define Collibra workflows:
   - CDM change requests initiated in Collibra
   - CDM documentation maintained in Collibra
   - Unity Catalog → Collibra metadata sync

**Outputs:**
- `cdm_collibra_integration_plan.docx`

---

### Activity 4.2: Data Quality Rules (Week 16) {#activity-4-2}

#### Task 4.2.1: Field-Level Validation Rules
**Effort:** 5 days (UK Lead: 3 days, India Eng 2: 2 days)
**Dependencies:** Physical model complete
**Deliverable:** Field validation rules catalog

**Detailed Steps:**
1. Define validation rules for each CDM field:
   - **Completeness Rules:** Required fields must be present (NOT NULL constraints)
   - **Validity Rules:** Data type, format, pattern, enumeration
   - **Range Rules:** Min/max values, length constraints

**Example rules:**
- `payment_id`: Required, UUID v4 format
- `instructed_amount.amount`: Required, > 0, DECIMAL(18,2)
- `instructed_amount.currency`: Required, ISO 4217 (3 characters, uppercase)
- `end_to_end_id`: Optional, max 35 characters, alphanumeric
- `payment_method`: Required, ENUM ('WIRE', 'ACH', ...)
- `debtor_id`: Required, UUID, must exist in Party table (referential integrity)

2. Implement rules in:
   - JSON Schema (format, pattern, enum, min/max)
   - Delta Lake CHECK constraints
   - PySpark validation logic

**Outputs:**
- `cdm_field_validation_rules.xlsx` - 500+ validation rules
- `cdm_validation_logic.py` - PySpark validation functions

---

#### Task 4.2.2: Cross-Field Validation Rules
**Effort:** 4 days (UK Lead: 3 days, India Eng 2: 1 day)
**Dependencies:** Task 4.2.1
**Deliverable:** Cross-field validation rules

**Detailed Steps:**
1. Define cross-field business rules:

**Example rules:**
- If `payment_method = 'ACH'`, then `extensions.secCode` must be present
- If `cross_border_flag = TRUE`, then `regulatory_reporting_code` must be present
- If `charge_bearer = 'SHAR'`, then both debtor and creditor may have charges
- If `payment_method = 'SEPA_SDD'`, then `extensions.mandateId` must be present
- `interbank_settlement_date >= requested_execution_date`
- If `intermediary_agent_1_id` is present, then payment is routed (multi-hop)

2. Implement as PySpark validations (applied during Bronze → Silver transformation)

**Outputs:**
- `cdm_cross_field_validation_rules.xlsx` - 100+ cross-field rules
- `cdm_cross_field_validation.py` - PySpark validation logic

---

#### Task 4.2.3: Business Rule Validation
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** Task 4.2.2
**Deliverable:** Business rule validation

**Detailed Steps:**
1. Define business rules (payment processing logic):

**Example rules:**
- ACH payments with `amount > $1,000,000` require dual approval
- Cross-border payments to high-risk countries require enhanced screening
- SEPA Instant payments must settle within 10 seconds (SLA)
- US domestic wires >$10,000 cash equivalent require CTR filing

2. Implement as configurable business rules engine

**Outputs:**
- `cdm_business_rules.xlsx` - 50+ business rules
- `cdm_business_rules_engine.py` - Rules engine implementation

---

#### Task 4.2.4: Quality Scoring Methodology
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** Tasks 4.2.1-4.2.3
**Deliverable:** Quality scoring framework

**Detailed Steps:**
1. Define data quality dimensions (ISO 8000 standard):
   - **Completeness:** % of required fields populated
   - **Validity:** % of fields passing format/type validation
   - **Consistency:** % of cross-field validations passed
   - **Accuracy:** % of fields matching reference data (e.g., valid BIC, valid currency)
   - **Timeliness:** % of records ingested within SLA

2. Define quality score calculation:
   - Dimension weights (Completeness: 30%, Validity: 25%, Consistency: 20%, Accuracy: 15%, Timeliness: 10%)
   - Aggregate score = weighted average (0-100%)

3. Define quality thresholds:
   - Acceptable: ≥95%
   - Warning: 90-95%
   - Critical: <90% (payment quarantined for review)

**Outputs:**
- `cdm_quality_scoring_methodology.docx`
- `cdm_quality_score_calculation.py` - Quality score calculation logic

---

### Activity 4.3: Governance Framework Consolidation (Week 16) {#activity-4-3}

#### Task 4.3.1: Consolidate Governance Framework
**Effort:** 3 days (UK Lead: 2 days, India Eng 2: 1 day)
**Dependencies:** Activities 4.1, 4.2 complete
**Deliverable:** Complete governance framework

**Detailed Steps:**
1. Consolidate all governance components:
   - Model governance (change control, versioning, extensions, Collibra)
   - Data quality rules (field, cross-field, business rules, scoring)

2. Create governance framework document (60+ pages)

**Outputs:**
- `DELIVERABLE_cdm_governance_framework.docx` - Complete governance framework

---

#### Task 4.3.2: Governance Review & Approval
**Effort:** 2 days (UK Lead: 2 days)
**Dependencies:** Task 4.3.1
**Deliverable:** Approved governance framework

**Detailed Steps:**
1. Present governance framework to CDM Working Group
2. Present to Architecture Review Board
3. Obtain approvals

**Quality Gate:** Governance framework approval required

---

## 6. Dependencies & Sequencing {#dependencies}

### Workstream-Level Dependencies

**External Dependencies (from other workstreams):**
- WS1 (Platform Modernization) → Phase 3 (Physical model requires platform selection for Delta Lake vs. Iceberg decision)
- WS4 (POC Planning) → Phase 4 (Governance framework tested in POC 2)

**Internal Dependencies (within WS2):**
```
Phase 1 (Principles & Methodology)
    ↓
Phase 2 (Logical Model) - requires methodology complete
    ↓
Phase 3 (Physical Model) - requires logical model complete, WS1 platform selection
    ↓
Phase 4 (Governance) - requires physical model complete
```

### Critical Path Activities

1. ISO 20022 Foundation Analysis (Week 1) → 5 days
2. Core Entity Development (Weeks 3-5) → 25 days (payment_instruction, party, account, fi, status)
3. Cross-Product Mapping (Week 8) → 33 days (all payment products)
4. Reconciliation (Week 8) → 5 days (critical for 99%+ coverage validation)
5. JSON Schema Development (Weeks 9-11) → 24 days
6. Delta Lake DDL Development (Weeks 12-13) → 18 days
7. Physical Model Consolidation (Week 14) → 8 days

**Total Critical Path:** ~118 days (~24 weeks with some parallelization)

---

## 7. Risks & Mitigation {#risks}

### Phase-Specific Risks

#### Phase 1 Risks (Principles & Methodology)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ISO 20022 standard too complex for 4-month timeline | Medium | High | Phased ISO 20022 adoption (prioritize pacs.008, pain.001); leverage existing SWIFT MX knowledge |
| ISDA CDM patterns not applicable to payments | Low | Medium | Focus on applicable patterns (event modeling, lineage); don't force-fit all ISDA concepts |

#### Phase 2 Risks (Logical Model)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| 99%+ field coverage unachievable (too many edge cases) | Medium | High | Accept 98% coverage with documented exceptions; prioritize high-volume payment types |
| Payments SMEs unavailable for model validation | High | High | Secure executive sponsorship; schedule SME sessions in Week 1; leverage UK resource's payments expertise |
| SWIFT MT → CDM mapping complexity underestimated | Medium | High | Allocate 6 days for MT mapping (largest effort in cross-product mapping); early spike if needed |
| Regulatory data elements missing from CDM | Medium | Critical | Partner with Compliance early (Week 1); cross-reference WS1 regulatory research |

#### Phase 3 Risks (Physical Model)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| JSON Schema 2020-12 tooling immature | Low | Medium | Fallback to Draft-07 if needed; test tooling early in Week 9 |
| Delta Lake vs. Iceberg decision delayed (waiting on WS1) | Medium | High | Assume Delta Lake (most likely choice); minor rework if Iceberg chosen |
| 40+ JSON schemas too many to maintain | Medium | Medium | Modular design with reusable components; automated validation scripts |

#### Phase 4 Risks (Governance)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data quality rules too strict (block legitimate payments) | High | High | Tiered quality thresholds (critical vs. warning); manual review queue for edge cases |
| Change control process too bureaucratic | Medium | Medium | Balance rigor with agility; fast-track for non-breaking changes |

---

## 8. Quality Gates {#quality-gates}

### Quality Gate 1: End of Week 2 (Methodology Complete)

**Criteria:**
- ✅ CDM design principles documented (7 principles with rationale)
- ✅ ISO 20022 foundation analysis complete
- ✅ DDD methodology documented
- ✅ ISDA CDM lessons learned captured

**Decision:** Proceed to Logical Model?

---

### Quality Gate 2: End of Week 8 (Logical Model Complete)

**Criteria:**
- ✅ All 36+ entities fully specified
- ✅ All payment products mapped to CDM (ACH, Wires, SWIFT, SEPA, UK, RTP, Zelle, Check)
- ✅ **99%+ field coverage** achieved (critical success criterion)
- ✅ 0 gaps in regulatory data elements
- ✅ Payments SME validation and approval

**Decision:** Proceed to Physical Model?

---

### Quality Gate 3: End of Week 14 (Physical Model Complete)

**Criteria:**
- ✅ All JSON schemas validated (40+ schemas, 0 syntax errors)
- ✅ All Delta Lake DDLs complete (Bronze/Silver/Gold, 30+ tables)
- ✅ Sample data and queries tested
- ✅ Physical ERD complete

**Decision:** Proceed to Governance Framework?

---

### Quality Gate 4: End of Week 16 (CDM Complete)

**Criteria:**
- ✅ CDM governance framework approved
- ✅ Data quality rules catalog complete (500+ field rules, 100+ cross-field rules)
- ✅ Change control process documented
- ✅ Collibra integration plan complete

**Decision:** Proceed to POC Execution (Workstream 4, POC 2)?

---

## Appendix: Deliverables Checklist

| Deliverable | File Name | Due Week | Status |
|-------------|-----------|----------|--------|
| CDM Design Principles & Methodology | `DELIVERABLE_cdm_methodology.docx` | Week 2 | |
| Logical CDM Model (Complete) | `DELIVERABLE_cdm_logical_model_complete.docx` | Week 8 | |
| CDM Entity-Relationship Diagram | `cdm_erd.vsdx` | Week 8 | |
| CDM Reconciliation Matrix | `DELIVERABLE_cdm_reconciliation_matrix.xlsx` | Week 8 | |
| JSON Schemas (40+ files) | `/schemas/**/*.schema.json` | Week 11 | |
| Delta Lake DDL (Bronze/Silver/Gold) | `cdm_ddl_*.sql` | Week 13 | |
| Physical CDM Model (Complete) | `DELIVERABLE_cdm_physical_model_complete.docx` | Week 14 | |
| CDM Governance Framework | `DELIVERABLE_cdm_governance_framework.docx` | Week 16 | |
| Data Quality Rules Catalog | `cdm_field_validation_rules.xlsx`, `cdm_cross_field_validation_rules.xlsx` | Week 16 | |

---

**Document Status:** COMPLETE ✅
**Review Date:** 2025-12-18
**Next Review:** At WS2 kickoff
