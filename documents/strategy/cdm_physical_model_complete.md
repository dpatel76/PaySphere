# PAYMENTS COMMON DOMAIN MODEL (CDM)
## COMPLETE PHYSICAL DATA MODEL

**Document Version:** 1.0
**Date:** December 18, 2025
**Classification:** Technical Specification - Complete Physical Model

---

## TABLE OF CONTENTS

1. [Physical Model Overview](#physical-model-overview)
2. [Delta Lake Table Specifications](#delta-lake-table-specifications)
3. [JSON Schema Definitions](#json-schema-definitions)
4. [Partitioning and Optimization](#partitioning-and-optimization)
5. [Indexing Strategies](#indexing-strategies)
6. [Sample Data](#sample-data)

---

## PHYSICAL MODEL OVERVIEW

### Architecture

**Databricks Lakehouse (Primary Storage):**
- Format: Delta Lake
- Catalog: Unity Catalog
- Storage: ADLS Gen2 / S3
- Compute: Databricks SQL, Spark

**Neo4j Graph Database (Relationship Queries):**
- Format: Native graph storage
- Purpose: Payment flows, network analysis, fraud detection
- Sync: Real-time CDC from Delta Lake

### Layer Structure

**Bronze Layer** (Raw ingestion):
- Schema: As-received from source
- Format: Delta Lake
- Partitioning: Ingestion date
- Retention: 90 days

**Silver Layer** (Cleansed, enriched):
- Schema: CDM schema (this document)
- Format: Delta Lake
- Partitioning: Business keys
- Retention: 7 years (hot/warm/cold)

**Gold Layer** (Curated, aggregated):
- Schema: Analytics-optimized
- Format: Delta Lake
- Partitioning: Analysis dimensions
- Retention: 5 years

---

## DELTA LAKE TABLE SPECIFICATIONS

### Table 1: payment_instruction

**Database:** `cdm_silver.payments`
**Table:** `payment_instruction`
**Partitioning:** `partition_year`, `partition_month`, `region`, `product_type`

```sql
CREATE TABLE IF NOT EXISTS cdm_silver.payments.payment_instruction (
  -- Primary Key
  payment_id STRING NOT NULL COMMENT 'UUID v4 primary key',

  -- Payment Identifiers
  end_to_end_id STRING COMMENT 'End-to-end identification (ISO 20022)',
  uetr STRING COMMENT 'SWIFT UETR (UUID format)',
  instruction_id STRING COMMENT 'Instruction identification',
  transaction_id STRING COMMENT 'Transaction identification',

  -- Payment Classification
  payment_type STRING NOT NULL COMMENT 'Payment type classification',
  product_code STRING COMMENT 'BofA product code',
  scheme_code STRING NOT NULL COMMENT 'Payment scheme code',
  service_level STRING COMMENT 'Service level code (ISO 20022)',
  local_instrument STRING COMMENT 'Local instrument code',
  category_purpose STRING COMMENT 'Category purpose code',

  -- Amount Information
  instructed_amount STRUCT<
    amount: DECIMAL(18,2),
    currency: STRING
  > NOT NULL COMMENT 'Instructed amount and currency',
  interbank_settlement_amount STRUCT<
    amount: DECIMAL(18,2),
    currency: STRING
  > COMMENT 'Interbank settlement amount',
  equivalent_amount STRUCT<
    amount: DECIMAL(18,2),
    currency: STRING
  > COMMENT 'Equivalent amount in different currency',
  exchange_rate DECIMAL(15,10) COMMENT 'Exchange rate',
  charge_bearer STRING COMMENT 'Charge bearer (DEBT/CRED/SHAR/SLEV)',

  -- Date/Time Information
  creation_date_time TIMESTAMP NOT NULL COMMENT 'Creation timestamp',
  acceptance_date_time TIMESTAMP COMMENT 'Acceptance timestamp',
  requested_execution_date DATE NOT NULL COMMENT 'Requested execution date',
  requested_execution_time STRING COMMENT 'Requested execution time',
  value_date DATE COMMENT 'Value date',
  settlement_date DATE COMMENT 'Settlement date',
  interbank_settlement_date DATE COMMENT 'Interbank settlement date',

  -- Party References (Foreign Keys)
  debtor_id STRING NOT NULL COMMENT 'FK to party.party_id',
  debtor_account_id STRING COMMENT 'FK to account.account_id',
  debtor_agent_id STRING COMMENT 'FK to financial_institution.financial_institution_id',
  creditor_id STRING NOT NULL COMMENT 'FK to party.party_id',
  creditor_account_id STRING COMMENT 'FK to account.account_id',
  creditor_agent_id STRING COMMENT 'FK to financial_institution.financial_institution_id',
  intermediary_agent1_id STRING COMMENT 'FK to financial_institution.financial_institution_id',
  intermediary_agent2_id STRING COMMENT 'FK to financial_institution.financial_institution_id',
  intermediary_agent3_id STRING COMMENT 'FK to financial_institution.financial_institution_id',

  -- Purpose Information
  purpose STRING COMMENT 'Purpose code (ISO 20022)',
  purpose_description STRING COMMENT 'Purpose description',
  priority STRING DEFAULT 'NORM' COMMENT 'Payment priority (HIGH/NORM/URGP)',
  instruction_priority STRING COMMENT 'Instruction priority code',

  -- Status Information
  current_status STRING NOT NULL COMMENT 'Current payment status',
  status_reason STRING COMMENT 'Status reason code',
  status_reason_description STRING COMMENT 'Status reason text',
  status_timestamp TIMESTAMP NOT NULL COMMENT 'Last status change timestamp',
  previous_status STRING COMMENT 'Previous status',
  number_of_status_changes INT DEFAULT 0 COMMENT 'Count of status changes',

  -- Regulatory Information
  regulatory_reporting ARRAY<STRUCT<
    reporting_type: STRING,
    reporting_code: STRING,
    reporting_details: STRING,
    jurisdiction: STRING
  >> COMMENT 'Regulatory reporting details',
  cross_border_flag BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Cross-border indicator',
  cross_border_type STRING COMMENT 'Cross-border type',

  -- Compliance Screening
  sanctions_screening_status STRING DEFAULT 'not_screened' COMMENT 'Sanctions screening status',
  sanctions_screening_timestamp TIMESTAMP COMMENT 'Sanctions screening timestamp',
  fraud_score DECIMAL(5,2) COMMENT 'Fraud risk score (0-100)',
  fraud_score_version STRING COMMENT 'Fraud scoring model version',
  fraud_flags ARRAY<STRING> COMMENT 'Fraud alert flags',
  aml_risk_rating STRING COMMENT 'AML risk rating',
  aml_alert_id STRING COMMENT 'FK to aml_alert.aml_alert_id',
  pep_flag BOOLEAN DEFAULT FALSE COMMENT 'PEP involved indicator',
  structuring_indicator BOOLEAN DEFAULT FALSE COMMENT 'Structuring indicator',

  -- Source System Information
  source_system STRING NOT NULL COMMENT 'Source system identifier',
  source_system_record_id STRING COMMENT 'Source system record ID',
  source_message_type STRING COMMENT 'Source message type',
  source_message_content STRING COMMENT 'Original source message',
  ingestion_timestamp TIMESTAMP NOT NULL COMMENT 'Bronze layer ingestion timestamp',
  bronze_to_silver_timestamp TIMESTAMP COMMENT 'Silver transformation timestamp',

  -- Data Quality
  data_quality_score DECIMAL(5,2) COMMENT 'Overall data quality score',
  data_quality_dimensions STRUCT<
    completeness: DECIMAL(5,2),
    validity: DECIMAL(5,2),
    consistency: DECIMAL(5,2),
    accuracy: DECIMAL(5,2),
    timeliness: DECIMAL(5,2)
  > COMMENT 'Individual DQ dimension scores',
  data_quality_issues ARRAY<STRING> COMMENT 'Data quality issues',

  -- Lineage
  lineage_source_table STRING COMMENT 'Source table for lineage',
  lineage_source_columns ARRAY<STRING> COMMENT 'Source columns for lineage',

  -- Partitioning Columns
  partition_year INT NOT NULL COMMENT 'Partition: Year',
  partition_month INT NOT NULL COMMENT 'Partition: Month',
  region STRING NOT NULL COMMENT 'Partition: Region (US/EMEA/APAC)',
  product_type STRING NOT NULL COMMENT 'Partition: Product type',

  -- Audit Columns
  created_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp() COMMENT 'Record creation timestamp',
  last_updated_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp() COMMENT 'Last update timestamp',
  last_updated_by STRING DEFAULT 'SYSTEM' COMMENT 'Last updated by',
  record_version INT DEFAULT 1 COMMENT 'Record version',
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Soft delete flag',
  deleted_timestamp TIMESTAMP COMMENT 'Soft delete timestamp',

  -- Product-Specific Extensions (JSON)
  extensions STRING COMMENT 'Product-specific extension fields (JSON)'
)
USING DELTA
PARTITIONED BY (partition_year, partition_month, region, product_type)
LOCATION 'abfss://silver@cdmstorage.dfs.core.windows.net/payments/payment_instruction'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.deletedFileRetentionDuration' = 'interval 30 days',
  'delta.logRetentionDuration' = 'interval 90 days',
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'delta.columnMapping.mode' = 'name',
  'delta.minReaderVersion' = '2',
  'delta.minWriterVersion' = '5'
);

-- Create Primary Key Constraint
ALTER TABLE cdm_silver.payments.payment_instruction
ADD CONSTRAINT pk_payment_instruction PRIMARY KEY (payment_id);

-- Create Check Constraints
ALTER TABLE cdm_silver.payments.payment_instruction
ADD CONSTRAINT chk_payment_amount CHECK (instructed_amount.amount > 0);

ALTER TABLE cdm_silver.payments.payment_instruction
ADD CONSTRAINT chk_partition_month CHECK (partition_month BETWEEN 1 AND 12);

-- Create indexes using Databricks Liquid Clustering (DBR 13.3+)
ALTER TABLE cdm_silver.payments.payment_instruction
CLUSTER BY (payment_id, debtor_id, creditor_id, current_status);
```

---

### Table 2: party

```sql
CREATE TABLE IF NOT EXISTS cdm_silver.master_data.party (
  -- Primary Key
  party_id STRING NOT NULL COMMENT 'UUID v4 primary key',

  -- Basic Information
  party_type STRING NOT NULL COMMENT 'Party type: individual/organization/government/financial_institution',
  name STRING NOT NULL COMMENT 'Party name (standardized)',
  name_line2 STRING COMMENT 'Additional name line',
  legal_name STRING COMMENT 'Official legal name',
  short_name STRING COMMENT 'Short name',
  name_standardization_score DECIMAL(5,2) COMMENT 'Name standardization confidence',

  -- Organization Details
  organization_type STRING COMMENT 'Organization type',
  industry_classification STRING COMMENT 'NAICS or SIC code',
  date_of_incorporation DATE COMMENT 'Incorporation date',
  country_of_incorporation STRING COMMENT 'Country of incorporation (ISO 3166-1)',
  registration_number STRING COMMENT 'Business registration number',

  -- Individual Details
  date_of_birth DATE COMMENT 'Date of birth',
  place_of_birth STRING COMMENT 'Place of birth',
  country_of_birth STRING COMMENT 'Country of birth (ISO 3166-1)',
  nationality STRING COMMENT 'Nationality (ISO 3166-1)',

  -- Identifications
  identifications ARRAY<STRUCT<
    scheme: STRING,
    identification: STRING,
    issuing_country: STRING,
    issuer: STRING,
    valid_from: DATE,
    valid_to: DATE
  >> COMMENT 'Party identification schemes',
  tax_identification_number STRING COMMENT 'Primary tax ID',
  tax_residence_country STRING COMMENT 'Tax residence country',

  -- Address Information
  postal_address STRUCT<
    address_type: STRING,
    department: STRING,
    sub_department: STRING,
    street_name: STRING,
    building_number: STRING,
    building_name: STRING,
    floor: STRING,
    post_box: STRING,
    room: STRING,
    post_code: STRING,
    town_name: STRING,
    town_location_name: STRING,
    district_name: STRING,
    country_sub_division: STRING,
    country: STRING,
    address_line: ARRAY<STRING>,
    geolocation: STRUCT<latitude: DECIMAL(10,8), longitude: DECIMAL(11,8)>,
    valid_from: DATE,
    valid_to: DATE
  > COMMENT 'Primary postal address',
  residential_address STRUCT<
    address_type: STRING,
    street_name: STRING,
    building_number: STRING,
    post_code: STRING,
    town_name: STRING,
    country_sub_division: STRING,
    country: STRING,
    address_line: ARRAY<STRING>
  > COMMENT 'Residential address',
  registered_address STRUCT<
    address_type: STRING,
    street_name: STRING,
    building_number: STRING,
    post_code: STRING,
    town_name: STRING,
    country_sub_division: STRING,
    country: STRING,
    address_line: ARRAY<STRING>
  > COMMENT 'Registered address',
  address_standardization_score DECIMAL(5,2) COMMENT 'Address standardization confidence',

  -- Contact Information
  phone_number STRING COMMENT 'Primary phone (E.164 format)',
  mobile_number STRING COMMENT 'Mobile phone',
  fax_number STRING COMMENT 'Fax number',
  email_address STRING COMMENT 'Primary email',
  website_url STRING COMMENT 'Website URL',

  -- Compliance Flags
  is_pep BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Politically Exposed Person flag',
  pep_type STRING COMMENT 'PEP type',
  pep_since DATE COMMENT 'Date identified as PEP',
  pep_position STRING COMMENT 'PEP position/role',
  is_sanctioned BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Sanctioned party flag',
  sanctioned_by ARRAY<STRING> COMMENT 'Sanctioning authorities',
  sanction_list_names ARRAY<STRING> COMMENT 'Sanction list names',
  sanctioned_since DATE COMMENT 'Date added to sanctions',
  high_risk_jurisdiction BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'High-risk jurisdiction flag',
  high_risk_jurisdiction_list ARRAY<STRING> COMMENT 'High-risk countries',
  adverse_media_flag BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Adverse media flag',
  adverse_media_summary STRING COMMENT 'Adverse media summary',
  adverse_media_last_checked DATE COMMENT 'Last adverse media check',

  -- Customer Relationship
  customer_since DATE COMMENT 'Customer relationship start date',
  customer_segment STRING COMMENT 'Customer segment',
  relationship_manager STRING COMMENT 'Assigned relationship manager',

  -- Risk and KYC
  risk_rating STRING COMMENT 'Overall risk rating',
  risk_rating_date DATE COMMENT 'Risk rating date',
  risk_rating_rationale STRING COMMENT 'Risk rating rationale',
  kyc_status STRING COMMENT 'KYC status',
  kyc_completion_date DATE COMMENT 'KYC completion date',
  kyc_expiry_date DATE COMMENT 'KYC expiry date',
  kyc_next_review_date DATE COMMENT 'Next KYC review',
  kyc_documents ARRAY<STRUCT<
    document_type: STRING,
    document_id: STRING,
    issue_date: DATE,
    expiry_date: DATE
  >> COMMENT 'KYC documents',
  edd_required BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'EDD required flag',
  edd_completed_date DATE COMMENT 'EDD completion date',

  -- Beneficial Ownership
  beneficial_owners ARRAY<STRUCT<
    name: STRING,
    ownership: DECIMAL(5,2),
    is_pep: BOOLEAN,
    is_controller: BOOLEAN
  >> COMMENT 'Beneficial owners',
  controlling_persons ARRAY<STRUCT<
    name: STRING,
    role: STRING,
    is_pep: BOOLEAN
  >> COMMENT 'Controlling persons',
  related_parties ARRAY<STRING> COMMENT 'Related party IDs',

  -- Data Quality
  data_source STRING COMMENT 'Primary data source',
  data_quality_score DECIMAL(5,2) COMMENT 'Data quality score',
  standardization_status STRING DEFAULT 'raw' COMMENT 'Data standardization status',
  last_verification_date DATE COMMENT 'Last verification date',
  next_verification_date DATE COMMENT 'Next verification date',

  -- SCD Type 2 Columns
  effective_from TIMESTAMP NOT NULL DEFAULT current_timestamp() COMMENT 'Effective start date',
  effective_to TIMESTAMP COMMENT 'Effective end date (NULL = current)',
  is_current BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Current version flag',

  -- Audit Columns
  created_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  last_updated_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  last_updated_by STRING DEFAULT 'SYSTEM',
  record_version INT DEFAULT 1,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE
)
USING DELTA
LOCATION 'abfss://silver@cdmstorage.dfs.core.windows.net/master_data/party'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.deletedFileRetentionDuration' = 'interval 30 days',
  'delta.logRetentionDuration' = 'interval 90 days',
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);

ALTER TABLE cdm_silver.master_data.party
ADD CONSTRAINT pk_party PRIMARY KEY (party_id);

ALTER TABLE cdm_silver.master_data.party
CLUSTER BY (party_id, name, tax_identification_number);
```

---

### Table 3: account

```sql
CREATE TABLE IF NOT EXISTS cdm_silver.master_data.account (
  -- Primary Key
  account_id STRING NOT NULL COMMENT 'UUID v4 primary key',

  -- Account Identifiers
  iban STRING COMMENT 'IBAN (ISO 13616)',
  bban STRING COMMENT 'Basic Bank Account Number',
  account_number STRING NOT NULL COMMENT 'Account number',
  check_digit STRING COMMENT 'Check digit',
  account_name STRING COMMENT 'Account name/title',

  -- Account Classification
  account_type STRING NOT NULL COMMENT 'Account type',
  account_sub_type STRING COMMENT 'Account subtype',
  currency STRING NOT NULL DEFAULT 'USD' COMMENT 'Account currency (ISO 4217)',
  multi_currency_flag BOOLEAN DEFAULT FALSE COMMENT 'Multi-currency support',
  supported_currencies ARRAY<STRING> COMMENT 'Supported currencies',

  -- Financial Institution
  servicer STRING COMMENT 'FK to financial_institution.financial_institution_id',
  branch STRING COMMENT 'Branch identifier',
  sort_code STRING COMMENT 'UK sort code',
  routing_number STRING COMMENT 'US routing number (ABA)',
  swift_bic STRING COMMENT 'SWIFT BIC',

  -- Ownership
  account_owner STRING COMMENT 'FK to party.party_id',
  account_relationship STRING NOT NULL COMMENT 'Relationship type',
  beneficial_owners ARRAY<STRING> COMMENT 'FK to party.party_id',
  joint_account_holders ARRAY<STRING> COMMENT 'FK to party.party_id',

  -- Account Status
  account_status STRING NOT NULL DEFAULT 'active' COMMENT 'Account status',
  status_reason STRING COMMENT 'Status reason',
  status_effective_date DATE COMMENT 'Status effective date',
  opened_date DATE COMMENT 'Account opening date',
  closed_date DATE COMMENT 'Account closure date',
  last_activity_date DATE COMMENT 'Last transaction date',
  dormant_since DATE COMMENT 'Dormant since date',

  -- Balance Information (optional snapshot)
  available_balance DECIMAL(18,2) COMMENT 'Available balance',
  ledger_balance DECIMAL(18,2) COMMENT 'Ledger balance',
  hold_amount DECIMAL(18,2) COMMENT 'Amount on hold',
  minimum_balance DECIMAL(18,2) COMMENT 'Minimum balance requirement',
  maximum_balance DECIMAL(18,2) COMMENT 'Maximum balance allowed',
  overdraft_limit DECIMAL(18,2) COMMENT 'Overdraft limit',
  balance_last_updated TIMESTAMP COMMENT 'Balance update timestamp',

  -- Restrictions and Limits
  restrictions ARRAY<STRING> COMMENT 'Account restrictions',
  daily_debit_limit DECIMAL(18,2) COMMENT 'Daily debit limit',
  daily_credit_limit DECIMAL(18,2) COMMENT 'Daily credit limit',
  single_transaction_limit DECIMAL(18,2) COMMENT 'Single transaction limit',
  monthly_transaction_limit DECIMAL(18,2) COMMENT 'Monthly transaction limit',

  -- Mandates
  account_purpose STRING COMMENT 'Purpose of account',
  mandate_required BOOLEAN DEFAULT FALSE COMMENT 'Mandate required flag',
  active_mandates ARRAY<STRING> COMMENT 'Active mandate references',

  -- Interest and Tax
  interest_rate DECIMAL(6,4) COMMENT 'Interest rate',
  interest_accrual_method STRING COMMENT 'Interest accrual method',
  tax_withholding_rate DECIMAL(5,2) COMMENT 'Tax withholding rate',

  -- Statements
  statement_frequency STRING COMMENT 'Statement frequency',
  last_statement_date DATE COMMENT 'Last statement date',

  -- Correspondent Banking
  correspondent_bank_account STRING COMMENT 'Correspondent bank account',
  correspondent_bank_bic STRING COMMENT 'Correspondent bank BIC',
  correspondent_relationship_type STRING COMMENT 'Correspondent relationship type',

  -- Regulatory and Accounting
  regulatory_classification STRING COMMENT 'Regulatory classification',
  accounting_gl_code STRING COMMENT 'GL code',
  profit_center STRING COMMENT 'Profit center',
  cost_center STRING COMMENT 'Cost center',

  -- Compliance
  risk_rating STRING COMMENT 'Account risk rating',
  sanctions_screening_status STRING COMMENT 'Sanctions screening status',
  aml_risk_rating STRING COMMENT 'AML risk rating',

  -- Data Quality
  data_source STRING COMMENT 'Data source',
  data_quality_score DECIMAL(5,2) COMMENT 'Data quality score',

  -- SCD Type 2
  effective_from TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  effective_to TIMESTAMP,
  is_current BOOLEAN NOT NULL DEFAULT TRUE,

  -- Audit
  created_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  last_updated_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  last_updated_by STRING DEFAULT 'SYSTEM',
  record_version INT DEFAULT 1,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE
)
USING DELTA
LOCATION 'abfss://silver@cdmstorage.dfs.core.windows.net/master_data/account'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.deletedFileRetentionDuration' = 'interval 30 days',
  'delta.autoOptimize.optimizeWrite' = 'true'
);

ALTER TABLE cdm_silver.master_data.account
ADD CONSTRAINT pk_account PRIMARY KEY (account_id);

ALTER TABLE cdm_silver.master_data.account
CLUSTER BY (account_id, iban, account_number);
```

---

### Table 4: financial_institution

```sql
CREATE TABLE IF NOT EXISTS cdm_silver.master_data.financial_institution (
  -- Primary Key
  financial_institution_id STRING NOT NULL COMMENT 'UUID v4 primary key',

  -- Basic Identifiers
  bic STRING COMMENT 'SWIFT BIC (ISO 9362)',
  lei STRING COMMENT 'Legal Entity Identifier (ISO 17442)',
  name STRING NOT NULL COMMENT 'Financial institution name',
  legal_name STRING COMMENT 'Legal name',
  short_name STRING COMMENT 'Short name',

  -- Classification
  financial_institution_type STRING COMMENT 'FI type',
  regulatory_category STRING COMMENT 'Regulatory category',
  branch_identification STRING COMMENT 'Branch identifier',
  branch_name STRING COMMENT 'Branch name',
  branch_type STRING COMMENT 'Branch type',

  -- Address
  postal_address STRUCT<
    street_name: STRING,
    building_number: STRING,
    post_code: STRING,
    town_name: STRING,
    country_sub_division: STRING,
    country: STRING,
    address_line: ARRAY<STRING>
  >,
  registered_address STRUCT<
    street_name: STRING,
    building_number: STRING,
    post_code: STRING,
    town_name: STRING,
    country_sub_division: STRING,
    country: STRING
  >,

  -- Contact
  phone_number STRING,
  email_address STRING,
  website_url STRING,

  -- Clearing System Memberships
  clearing_system_memberships ARRAY<STRUCT<
    clearing_system: STRING,
    member_id: STRING,
    membership_type: STRING,
    membership_status: STRING,
    member_since: DATE,
    termination_date: DATE,
    role: STRING
  >>,
  fedwire_member_id STRING COMMENT 'Fedwire routing number',
  chips_member_id STRING COMMENT 'CHIPS UID',
  target_member_id STRING COMMENT 'TARGET2 BIC',
  chaps_member_id STRING COMMENT 'CHAPS sort code',
  rtp_member_id STRING COMMENT 'RTP routing number',

  -- Correspondent Relationships
  correspondent_relationships ARRAY<STRUCT<
    counterparty_fi: STRING,
    relationship_type: STRING,
    currency: STRING,
    account_number: STRING,
    status: STRING,
    approved_date: DATE,
    effective_date: DATE,
    expiry_date: DATE,
    review_date: DATE,
    transaction_limit: DECIMAL(18,2),
    outstanding_limit: DECIMAL(18,2),
    products: ARRAY<STRING>,
    purpose: STRING
  >>,
  nostro_accounts ARRAY<STRUCT<
    currency: STRING,
    account_number: STRING,
    counterparty_fi: STRING
  >>,
  vostro_accounts ARRAY<STRUCT<
    currency: STRING,
    account_number: STRING,
    counterparty_fi: STRING
  >>,

  -- SWIFT Membership
  swift_membership_status STRING,
  swift_member_since DATE,

  -- Regulatory
  primary_regulator STRING,
  additional_regulators ARRAY<STRING>,
  jurisdiction STRING COMMENT 'ISO 3166-1',
  operating_jurisdictions ARRAY<STRING>,
  regulatory_licenses ARRAY<STRUCT<
    license_type: STRING,
    license_number: STRING,
    issuing_authority: STRING,
    issue_date: DATE,
    expiry_date: DATE
  >>,
  banking_license BOOLEAN DEFAULT FALSE,
  payment_services_license BOOLEAN DEFAULT FALSE,

  -- Corporate Structure
  stock_exchange_listing ARRAY<STRING>,
  publicly_traded BOOLEAN DEFAULT FALSE,
  parent_company STRING COMMENT 'FK to financial_institution_id',
  subsidiaries ARRAY<STRING> COMMENT 'FK to financial_institution_id',
  affiliates ARRAY<STRING> COMMENT 'FK to financial_institution_id',

  -- Due Diligence
  due_diligence_status STRING,
  due_diligence_completed_date DATE,
  due_diligence_expiry_date DATE,
  next_due_diligence_review_date DATE,
  due_diligence_documents ARRAY<STRING>,

  -- Risk
  risk_rating STRING,
  risk_rating_date DATE,
  risk_rating_rationale STRING,
  sanctioned_fi BOOLEAN NOT NULL DEFAULT FALSE,
  sanctioned_by ARRAY<STRING>,
  high_risk_jurisdiction BOOLEAN NOT NULL DEFAULT FALSE,
  adverse_media_flag BOOLEAN NOT NULL DEFAULT FALSE,
  restricted_fi BOOLEAN NOT NULL DEFAULT FALSE,
  restriction_reasons ARRAY<STRING>,

  -- Approval
  approved_for_correspondent_banking BOOLEAN NOT NULL DEFAULT FALSE,
  approved_products ARRAY<STRING>,
  blocked_products ARRAY<STRING>,
  transaction_limits ARRAY<STRUCT<
    product: STRING,
    limit: DECIMAL(18,2),
    currency: STRING
  >>,

  -- Financial Strength
  credit_rating STRING,
  credit_rating_agency STRING,
  credit_rating_date DATE,
  financial_strength STRING,
  capital_adequacy_ratio DECIMAL(5,2),
  total_assets DECIMAL(18,2) COMMENT 'In millions USD',

  -- Data Quality
  data_source STRING,
  data_quality_score DECIMAL(5,2),

  -- SCD Type 2
  effective_from TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  effective_to TIMESTAMP,
  is_current BOOLEAN NOT NULL DEFAULT TRUE,

  -- Audit
  created_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  last_updated_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  last_updated_by STRING DEFAULT 'SYSTEM',
  record_version INT DEFAULT 1,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE
)
USING DELTA
LOCATION 'abfss://silver@cdmstorage.dfs.core.windows.net/master_data/financial_institution'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true'
);

ALTER TABLE cdm_silver.master_data.financial_institution
ADD CONSTRAINT pk_financial_institution PRIMARY KEY (financial_institution_id);

ALTER TABLE cdm_silver.master_data.financial_institution
CLUSTER BY (financial_institution_id, bic, lei);
```

---

## JSON SCHEMA DEFINITIONS

### PaymentInstruction JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://bofa.com/schemas/cdm/payment-instruction/v1",
  "title": "PaymentInstruction",
  "description": "Complete payment instruction entity",
  "type": "object",
  "required": [
    "paymentId",
    "paymentType",
    "schemeCode",
    "instructedAmount",
    "creationDateTime",
    "requestedExecutionDate",
    "debtorId",
    "creditorId",
    "currentStatus",
    "sourceSystem",
    "partitionYear",
    "partitionMonth",
    "region",
    "productType"
  ],
  "properties": {
    "paymentId": {
      "type": "string",
      "format": "uuid",
      "description": "Unique payment identifier"
    },
    "endToEndId": {
      "type": "string",
      "maxLength": 35,
      "description": "End-to-end identification (ISO 20022)"
    },
    "uetr": {
      "type": "string",
      "format": "uuid",
      "description": "SWIFT UETR for gpi payments"
    },
    "instructionId": {
      "type": "string",
      "maxLength": 35
    },
    "transactionId": {
      "type": "string",
      "maxLength": 35
    },
    "paymentType": {
      "type": "string",
      "enum": [
        "ACH_CREDIT",
        "ACH_DEBIT",
        "WIRE_DOMESTIC",
        "WIRE_INTERNATIONAL",
        "SWIFT_MT103",
        "SWIFT_MT202",
        "SEPA_SCT",
        "SEPA_INST",
        "SEPA_SDD_CORE",
        "SEPA_SDD_B2B",
        "RTP",
        "FEDNOW",
        "ZELLE",
        "BACS_DIRECT_CREDIT",
        "BACS_DIRECT_DEBIT",
        "FASTER_PAYMENTS",
        "CHAPS",
        "PIX",
        "CIPS",
        "CHECK"
      ]
    },
    "productCode": {
      "type": "string",
      "maxLength": 50
    },
    "schemeCode": {
      "type": "string",
      "enum": ["ACH", "FEDWIRE", "CHIPS", "SWIFT", "SEPA", "RTP", "FEDNOW", "BACS", "FPS", "CHAPS", "PIX", "CIPS", "CHECK"]
    },
    "serviceLevel": {
      "type": "string",
      "maxLength": 4,
      "examples": ["URGP", "SEPA", "SDVA"]
    },
    "localInstrument": {
      "type": "string",
      "maxLength": 35
    },
    "categoryPurpose": {
      "type": "string",
      "maxLength": 4
    },
    "instructedAmount": {
      "type": "object",
      "required": ["amount", "currency"],
      "properties": {
        "amount": {
          "type": "number",
          "minimum": 0.01,
          "multipleOf": 0.01
        },
        "currency": {
          "type": "string",
          "pattern": "^[A-Z]{3}$",
          "description": "ISO 4217 currency code"
        }
      }
    },
    "interbankSettlementAmount": {
      "type": "object",
      "properties": {
        "amount": {"type": "number"},
        "currency": {"type": "string", "pattern": "^[A-Z]{3}$"}
      }
    },
    "equivalentAmount": {
      "type": "object",
      "properties": {
        "amount": {"type": "number"},
        "currency": {"type": "string", "pattern": "^[A-Z]{3}$"}
      }
    },
    "exchangeRate": {
      "type": "number",
      "minimum": 0
    },
    "chargeBearer": {
      "type": "string",
      "enum": ["DEBT", "CRED", "SHAR", "SLEV"],
      "default": "SHAR"
    },
    "creationDateTime": {
      "type": "string",
      "format": "date-time"
    },
    "acceptanceDateTime": {
      "type": "string",
      "format": "date-time"
    },
    "requestedExecutionDate": {
      "type": "string",
      "format": "date"
    },
    "requestedExecutionTime": {
      "type": "string",
      "format": "time"
    },
    "valueDate": {
      "type": "string",
      "format": "date"
    },
    "settlementDate": {
      "type": "string",
      "format": "date"
    },
    "debtorId": {
      "type": "string",
      "format": "uuid",
      "description": "FK to Party"
    },
    "debtorAccountId": {
      "type": "string",
      "format": "uuid",
      "description": "FK to Account"
    },
    "debtorAgentId": {
      "type": "string",
      "format": "uuid",
      "description": "FK to FinancialInstitution"
    },
    "creditorId": {
      "type": "string",
      "format": "uuid",
      "description": "FK to Party"
    },
    "creditorAccountId": {
      "type": "string",
      "format": "uuid"
    },
    "creditorAgentId": {
      "type": "string",
      "format": "uuid"
    },
    "intermediaryAgent1Id": {
      "type": "string",
      "format": "uuid"
    },
    "intermediaryAgent2Id": {
      "type": "string",
      "format": "uuid"
    },
    "intermediaryAgent3Id": {
      "type": "string",
      "format": "uuid"
    },
    "purpose": {
      "type": "string",
      "maxLength": 4,
      "description": "ISO 20022 external purpose code"
    },
    "purposeDescription": {
      "type": "string",
      "maxLength": 500
    },
    "priority": {
      "type": "string",
      "enum": ["HIGH", "NORM", "URGP"],
      "default": "NORM"
    },
    "currentStatus": {
      "type": "string",
      "enum": [
        "initiated", "received", "accepted", "validation_pending", "validated",
        "validation_failed", "fraud_screening", "fraud_clear", "fraud_hold",
        "fraud_reject", "sanctions_screening", "sanctions_clear", "sanctions_hit",
        "sanctions_rejected", "compliance_review", "compliance_approved",
        "compliance_rejected", "enrichment_pending", "enriched", "processing",
        "queued", "routed", "transmitted", "in_clearing", "clearing_failed",
        "settled", "settlement_pending", "settlement_failed", "completed",
        "returned", "reversed", "cancelled", "rejected", "failed", "suspended",
        "on_hold", "awaiting_approval", "approved", "partially_settled"
      ]
    },
    "statusReason": {
      "type": "string",
      "maxLength": 4
    },
    "statusReasonDescription": {
      "type": "string",
      "maxLength": 500
    },
    "statusTimestamp": {
      "type": "string",
      "format": "date-time"
    },
    "previousStatus": {
      "type": "string"
    },
    "numberOfStatusChanges": {
      "type": "integer",
      "minimum": 0,
      "default": 0
    },
    "regulatoryReporting": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "reportingType": {"type": "string"},
          "reportingCode": {"type": "string"},
          "reportingDetails": {"type": "string"},
          "jurisdiction": {"type": "string", "pattern": "^[A-Z]{2}$"}
        }
      }
    },
    "crossBorderFlag": {
      "type": "boolean",
      "default": false
    },
    "crossBorderType": {
      "type": "string",
      "enum": ["domestic", "intra_eu", "cross_border"]
    },
    "sanctionsScreeningStatus": {
      "type": "string",
      "enum": ["not_screened", "clear", "hit", "pending", "false_positive", "blocked"],
      "default": "not_screened"
    },
    "sanctionsScreeningTimestamp": {
      "type": "string",
      "format": "date-time"
    },
    "fraudScore": {
      "type": "number",
      "minimum": 0,
      "maximum": 100
    },
    "fraudScoreVersion": {
      "type": "string"
    },
    "fraudFlags": {
      "type": "array",
      "items": {"type": "string"}
    },
    "amlRiskRating": {
      "type": "string",
      "enum": ["low", "medium", "high", "very_high"]
    },
    "amlAlertId": {
      "type": "string",
      "format": "uuid"
    },
    "pepFlag": {
      "type": "boolean",
      "default": false
    },
    "structuringIndicator": {
      "type": "boolean",
      "default": false
    },
    "sourceSystem": {
      "type": "string",
      "maxLength": 100
    },
    "sourceSystemRecordId": {
      "type": "string",
      "maxLength": 100
    },
    "sourceMessageType": {
      "type": "string",
      "maxLength": 50,
      "examples": ["MT103", "pain.001.001.09", "ACH_FILE", "FEDWIRE_1000"]
    },
    "sourceMessageContent": {
      "type": "string",
      "description": "Original message for audit"
    },
    "ingestionTimestamp": {
      "type": "string",
      "format": "date-time"
    },
    "bronzeToSilverTimestamp": {
      "type": "string",
      "format": "date-time"
    },
    "dataQualityScore": {
      "type": "number",
      "minimum": 0,
      "maximum": 100
    },
    "dataQualityDimensions": {
      "type": "object",
      "properties": {
        "completeness": {"type": "number", "minimum": 0, "maximum": 100},
        "validity": {"type": "number", "minimum": 0, "maximum": 100},
        "consistency": {"type": "number", "minimum": 0, "maximum": 100},
        "accuracy": {"type": "number", "minimum": 0, "maximum": 100},
        "timeliness": {"type": "number", "minimum": 0, "maximum": 100}
      }
    },
    "dataQualityIssues": {
      "type": "array",
      "items": {"type": "string"}
    },
    "lineageSourceTable": {
      "type": "string"
    },
    "lineageSourceColumns": {
      "type": "array",
      "items": {"type": "string"}
    },
    "partitionYear": {
      "type": "integer",
      "minimum": 2020,
      "maximum": 2100
    },
    "partitionMonth": {
      "type": "integer",
      "minimum": 1,
      "maximum": 12
    },
    "region": {
      "type": "string",
      "enum": ["US", "EMEA", "APAC", "LATAM"]
    },
    "productType": {
      "type": "string",
      "maxLength": 50
    },
    "createdTimestamp": {
      "type": "string",
      "format": "date-time"
    },
    "lastUpdatedTimestamp": {
      "type": "string",
      "format": "date-time"
    },
    "lastUpdatedBy": {
      "type": "string",
      "default": "SYSTEM"
    },
    "recordVersion": {
      "type": "integer",
      "minimum": 1,
      "default": 1
    },
    "isDeleted": {
      "type": "boolean",
      "default": false
    },
    "deletedTimestamp": {
      "type": "string",
      "format": "date-time"
    },
    "extensions": {
      "type": "object",
      "description": "Product-specific extensions",
      "properties": {
        "achSECCode": {"type": "string", "maxLength": 3},
        "achCompanyName": {"type": "string", "maxLength": 16},
        "achCompanyID": {"type": "string", "maxLength": 10},
        "achTraceNumber": {"type": "string", "maxLength": 15},
        "achTransactionCode": {"type": "string", "maxLength": 2},
        "achSameDayFlag": {"type": "boolean"},
        "fedwireIMAD": {"type": "string", "maxLength": 15},
        "fedwireOMAD": {"type": "string", "maxLength": 15},
        "fedwireBusinessFunctionCode": {"type": "string", "maxLength": 3},
        "chipsUID": {"type": "string", "maxLength": 6},
        "swiftMessageType": {"type": "string"},
        "swiftGPIFlag": {"type": "boolean"},
        "sepaScheme": {"type": "string", "enum": ["SCT", "SCT_INST", "SDD_CORE", "SDD_B2B"]},
        "sepaCreditorIdentifier": {"type": "string", "maxLength": 35},
        "sepaMandateReference": {"type": "string", "maxLength": 35"},
        "bacsUserNumber": {"type": "string", "maxLength": 6},
        "bacsProcessingDay": {"type": "integer"}
      },
      "additionalProperties": true
    }
  },
  "additionalProperties": false
}
```

---

### Party JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://bofa.com/schemas/cdm/party/v1",
  "title": "Party",
  "description": "Complete party entity (debtor, creditor, beneficial owner)",
  "type": "object",
  "required": ["partyId", "partyType", "name", "effectiveFrom", "isCurrent"],
  "properties": {
    "partyId": {
      "type": "string",
      "format": "uuid"
    },
    "partyType": {
      "type": "string",
      "enum": ["individual", "organization", "government", "financial_institution"]
    },
    "name": {
      "type": "string",
      "maxLength": 140,
      "description": "Standardized party name"
    },
    "nameLine2": {
      "type": "string",
      "maxLength": 140
    },
    "legalName": {
      "type": "string",
      "maxLength": 140
    },
    "shortName": {
      "type": "string",
      "maxLength": 35
    },
    "nameStandardizationScore": {
      "type": "number",
      "minimum": 0,
      "maximum": 100
    },
    "organizationType": {
      "type": "string",
      "enum": ["corporation", "partnership", "trust", "sole_proprietorship", "nonprofit", "government_entity"]
    },
    "industryClassification": {
      "type": "string",
      "maxLength": 10,
      "description": "NAICS or SIC code"
    },
    "dateOfBirth": {
      "type": "string",
      "format": "date",
      "description": "For individuals"
    },
    "placeOfBirth": {
      "type": "string",
      "maxLength": 100
    },
    "countryOfBirth": {
      "type": "string",
      "pattern": "^[A-Z]{2}$"
    },
    "nationality": {
      "type": "string",
      "pattern": "^[A-Z]{2}$"
    },
    "countryOfIncorporation": {
      "type": "string",
      "pattern": "^[A-Z]{2}$"
    },
    "dateOfIncorporation": {
      "type": "string",
      "format": "date"
    },
    "registrationNumber": {
      "type": "string",
      "maxLength": 50
    },
    "identifications": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["scheme", "identification"],
        "properties": {
          "scheme": {
            "type": "string",
            "enum": ["PASSPORT", "NATIONAL_ID", "TAX_ID", "SSN", "EIN", "LEI", "DUNS", "OTHER"]
          },
          "identification": {"type": "string", "maxLength": 50},
          "issuingCountry": {"type": "string", "pattern": "^[A-Z]{2}$"},
          "issuer": {"type": "string"},
          "validFrom": {"type": "string", "format": "date"},
          "validTo": {"type": "string", "format": "date"}
        }
      }
    },
    "taxIdentificationNumber": {
      "type": "string",
      "maxLength": 50
    },
    "taxResidenceCountry": {
      "type": "string",
      "pattern": "^[A-Z]{2}$"
    },
    "postalAddress": {
      "$ref": "#/definitions/address"
    },
    "residentialAddress": {
      "$ref": "#/definitions/address"
    },
    "registeredAddress": {
      "$ref": "#/definitions/address"
    },
    "addressStandardizationScore": {
      "type": "number",
      "minimum": 0,
      "maximum": 100
    },
    "phoneNumber": {
      "type": "string",
      "maxLength": 25,
      "pattern": "^\\+?[0-9]{7,15}$"
    },
    "mobileNumber": {
      "type": "string",
      "maxLength": 25
    },
    "faxNumber": {
      "type": "string",
      "maxLength": 25
    },
    "emailAddress": {
      "type": "string",
      "format": "email",
      "maxLength": 255
    },
    "websiteURL": {
      "type": "string",
      "format": "uri",
      "maxLength": 255
    },
    "isPEP": {
      "type": "boolean",
      "default": false
    },
    "pepType": {
      "type": "string",
      "enum": ["domestic_pep", "foreign_pep", "international_organization", "rca"]
    },
    "pepSince": {
      "type": "string",
      "format": "date"
    },
    "pepPosition": {
      "type": "string",
      "maxLength": 200
    },
    "isSanctioned": {
      "type": "boolean",
      "default": false
    },
    "sanctionedBy": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["OFAC", "UN", "EU", "UK_HMT", "DFAT", "OTHER"]
      }
    },
    "sanctionListNames": {
      "type": "array",
      "items": {"type": "string"}
    },
    "sanctionedSince": {
      "type": "string",
      "format": "date"
    },
    "highRiskJurisdiction": {
      "type": "boolean",
      "default": false
    },
    "highRiskJurisdictionList": {
      "type": "array",
      "items": {"type": "string", "pattern": "^[A-Z]{2}$"}
    },
    "adverseMediaFlag": {
      "type": "boolean",
      "default": false
    },
    "adverseMediaSummary": {
      "type": "string"
    },
    "adverseMediaLastChecked": {
      "type": "string",
      "format": "date"
    },
    "customerSince": {
      "type": "string",
      "format": "date"
    },
    "customerSegment": {
      "type": "string",
      "enum": ["retail", "commercial", "corporate", "institutional", "government"]
    },
    "relationshipManager": {
      "type": "string",
      "maxLength": 100
    },
    "riskRating": {
      "type": "string",
      "enum": ["low", "medium", "high", "very_high"]
    },
    "riskRatingDate": {
      "type": "string",
      "format": "date"
    },
    "riskRatingRationale": {
      "type": "string"
    },
    "kycStatus": {
      "type": "string",
      "enum": ["pending", "in_progress", "approved", "expired", "rejected"]
    },
    "kycCompletionDate": {
      "type": "string",
      "format": "date"
    },
    "kycExpiryDate": {
      "type": "string",
      "format": "date"
    },
    "kycNextReviewDate": {
      "type": "string",
      "format": "date"
    },
    "kycDocuments": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "documentType": {"type": "string"},
          "documentID": {"type": "string"},
          "issueDate": {"type": "string", "format": "date"},
          "expiryDate": {"type": "string", "format": "date"}
        }
      }
    },
    "eddRequired": {
      "type": "boolean",
      "default": false
    },
    "eddCompletedDate": {
      "type": "string",
      "format": "date"
    },
    "beneficialOwners": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "ownership"],
        "properties": {
          "name": {"type": "string"},
          "ownership": {"type": "number", "minimum": 0, "maximum": 100},
          "isPEP": {"type": "boolean"},
          "isController": {"type": "boolean"}
        }
      }
    },
    "controllingPersons": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "role": {"type": "string"},
          "isPEP": {"type": "boolean"}
        }
      }
    },
    "relatedParties": {
      "type": "array",
      "items": {"type": "string", "format": "uuid"}
    },
    "dataSource": {
      "type": "string"
    },
    "dataQualityScore": {
      "type": "number",
      "minimum": 0,
      "maximum": 100
    },
    "standardizationStatus": {
      "type": "string",
      "enum": ["raw", "standardized", "verified", "certified"],
      "default": "raw"
    },
    "lastVerificationDate": {
      "type": "string",
      "format": "date"
    },
    "nextVerificationDate": {
      "type": "string",
      "format": "date"
    },
    "effectiveFrom": {
      "type": "string",
      "format": "date-time"
    },
    "effectiveTo": {
      "type": "string",
      "format": "date-time"
    },
    "isCurrent": {
      "type": "boolean",
      "default": true
    },
    "createdTimestamp": {
      "type": "string",
      "format": "date-time"
    },
    "lastUpdatedTimestamp": {
      "type": "string",
      "format": "date-time"
    },
    "lastUpdatedBy": {
      "type": "string",
      "default": "SYSTEM"
    },
    "recordVersion": {
      "type": "integer",
      "minimum": 1,
      "default": 1
    },
    "isDeleted": {
      "type": "boolean",
      "default": false
    }
  },
  "definitions": {
    "address": {
      "type": "object",
      "properties": {
        "addressType": {
          "type": "string",
          "enum": ["postal", "residential", "registered", "business", "po_box"]
        },
        "department": {"type": "string", "maxLength": 70},
        "subDepartment": {"type": "string", "maxLength": 70},
        "streetName": {"type": "string", "maxLength": 70},
        "buildingNumber": {"type": "string", "maxLength": 16},
        "buildingName": {"type": "string", "maxLength": 35},
        "floor": {"type": "string", "maxLength": 70},
        "postBox": {"type": "string", "maxLength": 16},
        "room": {"type": "string", "maxLength": 70},
        "postCode": {"type": "string", "maxLength": 16},
        "townName": {"type": "string", "maxLength": 35},
        "townLocationName": {"type": "string", "maxLength": 35},
        "districtName": {"type": "string", "maxLength": 35},
        "countrySubDivision": {"type": "string", "maxLength": 35},
        "country": {"type": "string", "pattern": "^[A-Z]{2}$"},
        "addressLine": {
          "type": "array",
          "items": {"type": "string", "maxLength": 70},
          "maxItems": 7
        },
        "geolocation": {
          "type": "object",
          "properties": {
            "latitude": {"type": "number", "minimum": -90, "maximum": 90},
            "longitude": {"type": "number", "minimum": -180, "maximum": 180}
          }
        },
        "validFrom": {"type": "string", "format": "date"},
        "validTo": {"type": "string", "format": "date"}
      }
    }
  },
  "additionalProperties": false
}
```

---

## PARTITIONING AND OPTIMIZATION

### Partitioning Strategy

**Payment Instruction (Fact Table):**
```sql
-- Multi-column partitioning for optimal query performance
PARTITIONED BY (partition_year, partition_month, region, product_type)

-- Example partitions:
-- /partition_year=2025/partition_month=12/region=US/product_type=ACH_CREDIT/
-- /partition_year=2025/partition_month=12/region=EMEA/product_type=SEPA_SCT/
-- /partition_year=2025/partition_month=12/region=APAC/product_type=SWIFT_MT103/

-- Partition pruning queries:
SELECT * FROM payment_instruction
WHERE partition_year = 2025
  AND partition_month = 12
  AND region = 'US'
  AND current_status = 'completed';
-- This query scans only US/Dec 2025 partitions
```

**Dimension Tables (Party, Account, FI):**
- No partitioning (small enough for full table scans with SCD Type 2)
- Liquid clustering on frequently queried columns

### Liquid Clustering (DBR 13.3+)

```sql
-- PaymentInstruction: Cluster by query patterns
ALTER TABLE payment_instruction
CLUSTER BY (payment_id, debtor_id, creditor_id, current_status);

-- Party: Cluster by lookup patterns
ALTER TABLE party
CLUSTER BY (party_id, name, tax_identification_number);

-- Account: Cluster by account lookups
ALTER TABLE account
CLUSTER BY (account_id, iban, account_number);

-- FinancialInstitution: Cluster by BIC/LEI
ALTER TABLE financial_institution
CLUSTER BY (financial_institution_id, bic, lei);
```

### Z-Ordering (Alternative to Liquid Clustering)

```sql
-- For older Databricks versions
OPTIMIZE payment_instruction
ZORDER BY (payment_id, debtor_id, creditor_id, current_status);

OPTIMIZE party
ZORDER BY (party_id, name, tax_identification_number);
```

### Data Compaction

```sql
-- Auto-compaction enabled via TBLPROPERTIES
'delta.autoOptimize.optimizeWrite' = 'true'
'delta.autoOptimize.autoCompact' = 'true'

-- Manual optimization (scheduled nightly)
OPTIMIZE payment_instruction;
OPTIMIZE party;
OPTIMIZE account;
OPTIMIZE financial_institution;

-- Vacuum old versions (retention: 30 days)
VACUUM payment_instruction RETAIN 720 HOURS;
```

---

## INDEXING STRATEGIES

### Databricks SQL Indexes

```sql
-- Bloom filter indexes for high-cardinality columns
CREATE BLOOMFILTER INDEX idx_payment_id
ON payment_instruction (payment_id);

CREATE BLOOMFILTER INDEX idx_end_to_end_id
ON payment_instruction (end_to_end_id);

CREATE BLOOMFILTER INDEX idx_uetr
ON payment_instruction (uetr);

-- Composite indexes using Liquid Clustering (preferred)
-- Already defined in table DDL
```

### Neo4j Indexes

```cypher
-- Node indexes
CREATE INDEX payment_id_index FOR (p:PaymentInstruction) ON (p.paymentId);
CREATE INDEX party_id_index FOR (p:Party) ON (p.partyId);
CREATE INDEX account_id_index FOR (a:Account) ON (a.accountId);
CREATE INDEX fi_id_index FOR (f:FinancialInstitution) ON (f.financialInstitutionId);

-- Composite indexes for common query patterns
CREATE INDEX payment_status_date FOR (p:PaymentInstruction) ON (p.currentStatus, p.settlementDate);
CREATE INDEX party_name_tax FOR (p:Party) ON (p.name, p.taxIdentificationNumber);

-- Full-text search indexes
CREATE FULLTEXT INDEX party_name_search FOR (p:Party) ON EACH [p.name, p.legalName];
CREATE FULLTEXT INDEX fi_name_search FOR (f:FinancialInstitution) ON EACH [f.name, f.legalName];

-- Constraint indexes (automatically created)
CREATE CONSTRAINT payment_pk IF NOT EXISTS FOR (p:PaymentInstruction) REQUIRE p.paymentId IS UNIQUE;
CREATE CONSTRAINT party_pk IF NOT EXISTS FOR (p:Party) REQUIRE p.partyId IS UNIQUE;
```

---

## SAMPLE DATA

### Sample PaymentInstruction Record (JSON)

```json
{
  "paymentId": "550e8400-e29b-41d4-a716-446655440000",
  "endToEndId": "BOFA20251218ACH12345",
  "uetr": null,
  "instructionId": "ACH-BATCH-20251218-001",
  "transactionId": "TXN-20251218-123456",
  "paymentType": "ACH_CREDIT",
  "productCode": "ACH_PPD_CREDIT",
  "schemeCode": "ACH",
  "serviceLevel": "SDVA",
  "localInstrument": "PPD",
  "categoryPurpose": "CASH",
  "instructedAmount": {
    "amount": 1500.00,
    "currency": "USD"
  },
  "interbankSettlementAmount": null,
  "equivalentAmount": null,
  "exchangeRate": null,
  "chargeBearer": "DEBT",
  "creationDateTime": "2025-12-18T10:30:00Z",
  "acceptanceDateTime": "2025-12-18T10:30:15Z",
  "requestedExecutionDate": "2025-12-19",
  "requestedExecutionTime": null,
  "valueDate": "2025-12-19",
  "settlementDate": "2025-12-19",
  "interbankSettlementDate": null,
  "debtorId": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "debtorAccountId": "b2c3d4e5-f6a7-5b6c-9d0e-1f2a3b4c5d6e",
  "debtorAgentId": "c3d4e5f6-a7b8-6c7d-0e1f-2a3b4c5d6e7f",
  "creditorId": "d4e5f6a7-b8c9-7d8e-1f2a-3b4c5d6e7f8a",
  "creditorAccountId": "e5f6a7b8-c9d0-8e9f-2a3b-4c5d6e7f8a9b",
  "creditorAgentId": "f6a7b8c9-d0e1-9f0a-3b4c-5d6e7f8a9b0c",
  "intermediaryAgent1Id": null,
  "intermediaryAgent2Id": null,
  "intermediaryAgent3Id": null,
  "purpose": "SALA",
  "purposeDescription": "Payroll payment",
  "priority": "NORM",
  "instructionPriority": null,
  "currentStatus": "completed",
  "statusReason": null,
  "statusReasonDescription": null,
  "statusTimestamp": "2025-12-19T09:00:00Z",
  "previousStatus": "settled",
  "numberOfStatusChanges": 8,
  "regulatoryReporting": [],
  "crossBorderFlag": false,
  "crossBorderType": "domestic",
  "sanctionsScreeningStatus": "clear",
  "sanctionsScreeningTimestamp": "2025-12-18T10:30:05Z",
  "fraudScore": 15.5,
  "fraudScoreVersion": "v2.3.1",
  "fraudFlags": [],
  "amlRiskRating": "low",
  "amlAlertId": null,
  "pepFlag": false,
  "structuringIndicator": false,
  "sourceSystem": "CASHPRO_ACH",
  "sourceSystemRecordId": "CP-ACH-20251218-123456",
  "sourceMessageType": "ACH_FILE",
  "sourceMessageContent": "101 026009593 0260095931...",
  "ingestionTimestamp": "2025-12-18T10:29:55Z",
  "bronzeToSilverTimestamp": "2025-12-18T10:30:10Z",
  "dataQualityScore": 98.5,
  "dataQualityDimensions": {
    "completeness": 100.0,
    "validity": 100.0,
    "consistency": 97.0,
    "accuracy": 98.0,
    "timeliness": 100.0
  },
  "dataQualityIssues": [],
  "lineageSourceTable": "bronze.cashpro_ach.ach_payments",
  "lineageSourceColumns": ["payment_record", "batch_header", "file_header"],
  "partitionYear": 2025,
  "partitionMonth": 12,
  "region": "US",
  "productType": "ACH_CREDIT",
  "createdTimestamp": "2025-12-18T10:30:10Z",
  "lastUpdatedTimestamp": "2025-12-19T09:00:00Z",
  "lastUpdatedBy": "SYSTEM",
  "recordVersion": 1,
  "isDeleted": false,
  "deletedTimestamp": null,
  "extensions": {
    "achSECCode": "PPD",
    "achCompanyName": "ACME CORPORATION",
    "achCompanyID": "1234567890",
    "achCompanyEntryDescription": "PAYROLL",
    "achOriginatingDFI": "02600959",
    "achReceivingDFI": "12345678",
    "achTraceNumber": "026009590000001",
    "achTransactionCode": "22",
    "achAddendaRecordIndicator": "0",
    "achEffectiveEntryDate": "251219",
    "achBatchNumber": "0000001",
    "achSameDayFlag": false
  }
}
```

---

### Table 5: settlement

```sql
CREATE TABLE IF NOT EXISTS cdm_silver.payments.settlement (
  settlement_id STRING NOT NULL COMMENT 'UUID v4 primary key',
  payment_id STRING NOT NULL COMMENT 'FK to payment_instruction.payment_id',

  settlement_method STRING NOT NULL COMMENT 'INDA/INGA/COVE/CLRG',
  settlement_account STRING COMMENT 'FK to account.account_id',
  settlement_amount STRUCT<amount: DECIMAL(18,2), currency: STRING> NOT NULL,
  settlement_date DATE NOT NULL,
  settlement_time STRING,
  settlement_priority STRING DEFAULT 'normal',

  clearing_channel STRING COMMENT 'RTGS/DNS/mixed',
  clearing_system STRING,
  clearing_system_reference STRING,
  clearing_system_proprietary_code STRING,

  interbank_settlement_amount DECIMAL(18,2),
  instructed_amount DECIMAL(18,2),
  counter_value_amount STRUCT<amount: DECIMAL(18,2), currency: STRING>,
  exchange_rate DECIMAL(15,10),

  settlement_status STRING NOT NULL DEFAULT 'pending',
  settlement_status_timestamp TIMESTAMP NOT NULL,
  failure_reason STRING,
  failure_description STRING,

  nostro_account_debit STRING COMMENT 'FK to account.account_id',
  nostro_account_credit STRING COMMENT 'FK to account.account_id',
  settling_agent STRING COMMENT 'FK to financial_institution.financial_institution_id',
  settlement_instruction_id STRING,

  net_settlement_amount DECIMAL(18,2),
  gross_settlement_amount DECIMAL(18,2),
  settlement_batch_id STRING,
  settlement_cycle STRING,

  confirmation_received BOOLEAN NOT NULL DEFAULT FALSE,
  confirmation_timestamp TIMESTAMP,
  confirmation_reference STRING,

  data_source STRING,
  created_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  last_updated_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  last_updated_by STRING DEFAULT 'SYSTEM',
  record_version INT DEFAULT 1,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE
)
USING DELTA
PARTITIONED BY (settlement_date)
LOCATION 'abfss://silver@cdmstorage.dfs.core.windows.net/payments/settlement'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true'
);

ALTER TABLE cdm_silver.payments.settlement
ADD CONSTRAINT pk_settlement PRIMARY KEY (settlement_id);

ALTER TABLE cdm_silver.payments.settlement
CLUSTER BY (settlement_id, payment_id, settlement_status);
```

---

### Table 6: charge

```sql
CREATE TABLE IF NOT EXISTS cdm_silver.payments.charge (
  charge_id STRING NOT NULL COMMENT 'UUID v4 primary key',
  payment_id STRING NOT NULL COMMENT 'FK to payment_instruction.payment_id',

  charge_type STRING NOT NULL COMMENT 'CRED/DEBT/SHAR/INST/CORR/OTHR',
  charge_category STRING,
  charge_bearer STRING NOT NULL,
  charge_amount STRUCT<amount: DECIMAL(18,2), currency: STRING> NOT NULL,
  equivalent_amount STRUCT<amount: DECIMAL(18,2), currency: STRING>,

  tax_amount DECIMAL(18,2),
  tax_rate DECIMAL(5,2),
  tax_type STRING,

  base_amount DECIMAL(18,2),
  charge_rate DECIMAL(8,5),
  minimum_charge DECIMAL(18,2),
  maximum_charge DECIMAL(18,2),

  charge_agent_id STRING COMMENT 'FK to financial_institution.financial_institution_id',
  charge_account STRING COMMENT 'FK to account.account_id',
  charge_description STRING,
  charge_purpose STRING,

  regulatory_charge BOOLEAN NOT NULL DEFAULT FALSE,
  regulatory_authority STRING,

  waived_flag BOOLEAN NOT NULL DEFAULT FALSE,
  waived_reason STRING,
  waived_by STRING,
  waived_timestamp TIMESTAMP,

  charge_status STRING NOT NULL DEFAULT 'calculated',
  charge_timestamp TIMESTAMP,

  reversal_flag BOOLEAN NOT NULL DEFAULT FALSE,
  reversal_reason STRING,
  reversal_timestamp TIMESTAMP,

  charge_reference STRING,
  gl_account STRING,
  revenue_recognition STRING,

  data_source STRING,
  created_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  last_updated_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  last_updated_by STRING DEFAULT 'SYSTEM',
  record_version INT DEFAULT 1,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE
)
USING DELTA
PARTITIONED BY (charge_status)
LOCATION 'abfss://silver@cdmstorage.dfs.core.windows.net/payments/charge'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true'
);

ALTER TABLE cdm_silver.payments.charge
ADD CONSTRAINT pk_charge PRIMARY KEY (charge_id);
```

---

### Table 7: status_event

```sql
CREATE TABLE IF NOT EXISTS cdm_silver.payments.status_event (
  status_event_id STRING NOT NULL COMMENT 'UUID v4 primary key',
  payment_id STRING NOT NULL COMMENT 'FK to payment_instruction.payment_id',

  event_sequence INT NOT NULL,
  status STRING NOT NULL,
  previous_status STRING,
  status_reason STRING,
  status_reason_text STRING,
  status_category STRING,

  event_timestamp TIMESTAMP NOT NULL,
  event_source STRING,
  event_type STRING NOT NULL,
  is_terminal_status BOOLEAN DEFAULT FALSE,

  error_code STRING,
  error_message STRING,
  error_severity STRING,

  processing_stage STRING,
  system_component STRING,
  user_id STRING,
  automated_flag BOOLEAN NOT NULL DEFAULT TRUE,

  notification_sent BOOLEAN NOT NULL DEFAULT FALSE,
  notification_channels ARRAY<STRING>,
  notification_timestamp TIMESTAMP,

  retry_attempt INT DEFAULT 0,
  max_retries INT,
  retry_timestamp TIMESTAMP,

  sla_breach_flag BOOLEAN NOT NULL DEFAULT FALSE,
  sla_due_timestamp TIMESTAMP,
  sla_actual_timestamp TIMESTAMP,
  sla_variance INT COMMENT 'In seconds',

  settlement_timestamp TIMESTAMP,
  confirmation_received BOOLEAN,
  external_reference STRING,
  additional_data STRING COMMENT 'JSON',

  data_source STRING,
  created_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(event_timestamp))
LOCATION 'abfss://silver@cdmstorage.dfs.core.windows.net/payments/status_event'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.logRetentionDuration' = 'interval 30 days'
);

ALTER TABLE cdm_silver.payments.status_event
ADD CONSTRAINT pk_status_event PRIMARY KEY (status_event_id);

ALTER TABLE cdm_silver.payments.status_event
CLUSTER BY (payment_id, event_timestamp, status);
```

---

### Table 8: compliance.screening_result

```sql
CREATE TABLE IF NOT EXISTS cdm_silver.compliance.screening_result (
  screening_result_id STRING NOT NULL COMMENT 'UUID v4 primary key',
  payment_id STRING COMMENT 'FK to payment_instruction.payment_id',
  party_id STRING COMMENT 'FK to party.party_id',

  screening_type STRING NOT NULL,
  screening_timestamp TIMESTAMP NOT NULL,
  screening_system STRING,
  screening_version STRING,

  screening_result STRING NOT NULL,
  match_score DECIMAL(5,2),
  matched_list_name STRING,
  matched_list_type STRING,
  matched_entity_name STRING,
  matched_entity_id STRING,
  matched_fields ARRAY<STRING>,
  match_reason STRING,

  false_positive_reason STRING,
  reviewed_by STRING,
  review_timestamp TIMESTAMP,
  review_decision STRING,
  review_notes STRING,

  escalation_level INT,
  escalated_to STRING,
  escalation_timestamp TIMESTAMP,

  blocked_transaction BOOLEAN NOT NULL DEFAULT FALSE,
  rejected_transaction BOOLEAN NOT NULL DEFAULT FALSE,
  ofac_reported BOOLEAN NOT NULL DEFAULT FALSE,
  ofac_report_timestamp TIMESTAMP,

  created_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  last_updated_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(screening_timestamp))
LOCATION 'abfss://silver@cdmstorage.dfs.core.windows.net/compliance/screening_result'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.deletedFileRetentionDuration' = 'interval 90 days'
);

ALTER TABLE cdm_silver.compliance.screening_result
ADD CONSTRAINT pk_screening_result PRIMARY KEY (screening_result_id);
```

---

### Table 9: reference_data.currency

```sql
CREATE TABLE IF NOT EXISTS cdm_silver.reference_data.currency (
  currency_code STRING NOT NULL COMMENT 'ISO 4217 alpha-3',
  currency_number STRING COMMENT 'ISO 4217 numeric',
  currency_name STRING NOT NULL,
  currency_symbol STRING,
  minor_unit INT DEFAULT 2,
  countries ARRAY<STRING>,
  central_bank STRING,
  is_fiat BOOLEAN DEFAULT TRUE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  withdrawn_date DATE,
  replaced_by_currency STRING,
  peg STRING,
  volatility STRING,
  convertibility_status STRING,
  capital_controls_apply BOOLEAN,
  effective_from DATE NOT NULL,
  effective_to DATE,
  last_updated_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp()
)
USING DELTA
LOCATION 'abfss://silver@cdmstorage.dfs.core.windows.net/reference_data/currency'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

ALTER TABLE cdm_silver.reference_data.currency
ADD CONSTRAINT pk_currency PRIMARY KEY (currency_code);
```

---

### Table 10: reference_data.country

```sql
CREATE TABLE IF NOT EXISTS cdm_silver.reference_data.country (
  country_code STRING NOT NULL COMMENT 'ISO 3166-1 alpha-2',
  country_code3 STRING COMMENT 'ISO 3166-1 alpha-3',
  country_numeric STRING COMMENT 'ISO 3166-1 numeric',
  country_name STRING NOT NULL,
  official_language STRING,
  region STRING,
  sub_region STRING,
  continent STRING,
  currency STRING COMMENT 'FK to currency.currency_code',
  phone_prefix STRING,
  timezone STRING,
  capital_city STRING,
  is_eu_member BOOLEAN DEFAULT FALSE,
  is_oecd_member BOOLEAN DEFAULT FALSE,
  is_sepa_country BOOLEAN DEFAULT FALSE,
  fatf_member BOOLEAN DEFAULT FALSE,
  fatf_jurisdiction STRING,
  high_risk_jurisdiction BOOLEAN NOT NULL DEFAULT FALSE,
  sanctioned_country BOOLEAN NOT NULL DEFAULT FALSE,
  sanctioning_authorities ARRAY<STRING>,
  data_privacy_regime STRING,
  tax_haven BOOLEAN,
  crs_participant BOOLEAN,
  fatca_iga STRING,
  political_stability_rating STRING,
  corruption_index DECIMAL(5,2),
  effective_from DATE NOT NULL,
  effective_to DATE,
  last_updated_timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp()
)
USING DELTA
LOCATION 'abfss://silver@cdmstorage.dfs.core.windows.net/reference_data/country'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

ALTER TABLE cdm_silver.reference_data.country
ADD CONSTRAINT pk_country PRIMARY KEY (country_code);
```

---

## NEO4J GRAPH SCHEMA

### Node Labels and Properties

```cypher
// Create node constraints and indexes
CREATE CONSTRAINT payment_pk IF NOT EXISTS
FOR (p:PaymentInstruction) REQUIRE p.paymentId IS UNIQUE;

CREATE CONSTRAINT party_pk IF NOT EXISTS
FOR (p:Party) REQUIRE p.partyId IS UNIQUE;

CREATE CONSTRAINT account_pk IF NOT EXISTS
FOR (a:Account) REQUIRE a.accountId IS UNIQUE;

CREATE CONSTRAINT fi_pk IF NOT EXISTS
FOR (f:FinancialInstitution) REQUIRE f.financialInstitutionId IS UNIQUE;

// PaymentInstruction node
CREATE INDEX payment_status_idx IF NOT EXISTS
FOR (p:PaymentInstruction) ON (p.currentStatus);

CREATE INDEX payment_date_idx IF NOT EXISTS
FOR (p:PaymentInstruction) ON (p.settlementDate);

CREATE INDEX payment_type_idx IF NOT EXISTS
FOR (p:PaymentInstruction) ON (p.paymentType);

// Party node
CREATE INDEX party_name_idx IF NOT EXISTS
FOR (p:Party) ON (p.name);

CREATE INDEX party_tax_idx IF NOT EXISTS
FOR (p:Party) ON (p.taxIdentificationNumber);

CREATE FULLTEXT INDEX party_fulltext IF NOT EXISTS
FOR (p:Party) ON EACH [p.name, p.legalName];

// Account node
CREATE INDEX account_iban_idx IF NOT EXISTS
FOR (a:Account) ON (a.iban);

CREATE INDEX account_number_idx IF NOT EXISTS
FOR (a:Account) ON (a.accountNumber);

// FinancialInstitution node
CREATE INDEX fi_bic_idx IF NOT EXISTS
FOR (f:FinancialInstitution) ON (f.bic);

CREATE INDEX fi_lei_idx IF NOT EXISTS
FOR (f:FinancialInstitution) ON (f.lei);
```

### Sample Graph Data Load

```cypher
// Load PaymentInstruction nodes from Delta Lake
CALL apoc.load.jdbc(
  'jdbc:databricks://...',
  'SELECT payment_id, payment_type, instructed_amount, current_status,
          debtor_id, creditor_id, settlement_date
   FROM cdm_silver.payments.payment_instruction
   WHERE partition_year = 2025 AND partition_month = 12'
) YIELD row
CREATE (p:PaymentInstruction {
  paymentId: row.payment_id,
  paymentType: row.payment_type,
  instructedAmount: row.instructed_amount.amount,
  currency: row.instructed_amount.currency,
  currentStatus: row.current_status,
  settlementDate: date(row.settlement_date)
});

// Create relationships
MATCH (p:PaymentInstruction)
MATCH (debtor:Party {partyId: p.debtorId})
MATCH (creditor:Party {partyId: p.creditorId})
CREATE (p)-[:HAS_DEBTOR]->(debtor)
CREATE (p)-[:HAS_CREDITOR]->(creditor);

// Create payment flow relationships
MATCH (p:PaymentInstruction)
WHERE p.debtorAgentId IS NOT NULL
MATCH (da:FinancialInstitution {financialInstitutionId: p.debtorAgentId})
CREATE (p)-[:DEBTOR_AGENT]->(da);

MATCH (p:PaymentInstruction)
WHERE p.creditorAgentId IS NOT NULL
MATCH (ca:FinancialInstitution {financialInstitutionId: p.creditorAgentId})
CREATE (p)-[:CREDITOR_AGENT]->(ca);
```

---

## UNITY CATALOG CONFIGURATION

### Catalog Structure

```sql
-- Create catalogs
CREATE CATALOG IF NOT EXISTS cdm_bronze
  COMMENT 'Bronze layer - raw ingestion';

CREATE CATALOG IF NOT EXISTS cdm_silver
  COMMENT 'Silver layer - cleansed CDM data';

CREATE CATALOG IF NOT EXISTS cdm_gold
  COMMENT 'Gold layer - curated analytics';

-- Create schemas in Silver catalog
CREATE SCHEMA IF NOT EXISTS cdm_silver.payments
  COMMENT 'Payment transaction data';

CREATE SCHEMA IF NOT EXISTS cdm_silver.master_data
  COMMENT 'Master data (Party, Account, FI)';

CREATE SCHEMA IF NOT EXISTS cdm_silver.reference_data
  COMMENT 'Reference data (Currency, Country, etc.)';

CREATE SCHEMA IF NOT EXISTS cdm_silver.compliance
  COMMENT 'Compliance and regulatory data';

CREATE SCHEMA IF NOT EXISTS cdm_silver.operational
  COMMENT 'Operational data (exceptions, audit, etc.)';

CREATE SCHEMA IF NOT EXISTS cdm_silver.analytics
  COMMENT 'Analytics entities';

-- Grant permissions
GRANT USE CATALOG ON CATALOG cdm_silver TO `data_engineers`;
GRANT USE SCHEMA ON SCHEMA cdm_silver.payments TO `data_engineers`;
GRANT SELECT ON SCHEMA cdm_silver.payments TO `data_analysts`;
GRANT MODIFY ON SCHEMA cdm_silver.payments TO `etl_service_account`;

-- Row-level security example
CREATE FUNCTION cdm_silver.mask_pii(col STRING)
RETURN CASE
  WHEN is_account_group_member('compliance_team') THEN col
  ELSE 'REDACTED'
END;

-- Apply masking
ALTER TABLE cdm_silver.master_data.party
ALTER COLUMN tax_identification_number
SET MASK cdm_silver.mask_pii;
```

---

## DATA RETENTION AND ARCHIVAL

### Retention Policies

```sql
-- Configure retention for hot/warm/cold data
-- Hot: 0-90 days (all queries)
-- Warm: 91-730 days (analytics, compliance)
-- Cold: 731-2555 days (archive, compliance only)

-- Example: Move to cold storage after 2 years
CREATE OR REPLACE TABLE cdm_silver.payments.payment_instruction_cold
DEEP CLONE cdm_silver.payments.payment_instruction
WHERE settlement_date < current_date() - INTERVAL 2 YEARS;

-- Delete from hot table
DELETE FROM cdm_silver.payments.payment_instruction
WHERE settlement_date < current_date() - INTERVAL 2 YEARS;

-- Vacuum to reclaim space
VACUUM cdm_silver.payments.payment_instruction RETAIN 168 HOURS;

-- Archive to cheaper storage tier
ALTER TABLE cdm_silver.payments.payment_instruction_cold
SET TBLPROPERTIES (
  'storage.tier' = 'ARCHIVE'
);
```

---

## CHANGE DATA CAPTURE (CDC)

### Delta Lake CDC Configuration

```sql
-- Enable CDC on all tables
ALTER TABLE cdm_silver.payments.payment_instruction
SET TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');

-- Read CDC changes
SELECT * FROM table_changes('cdm_silver.payments.payment_instruction', 0)
WHERE _change_type IN ('insert', 'update_postimage')
  AND _commit_timestamp > current_timestamp() - INTERVAL 1 HOUR;

-- Stream CDC to Neo4j
CREATE OR REPLACE STREAMING LIVE TABLE payment_cdc_stream
AS SELECT
  payment_id,
  debtor_id,
  creditor_id,
  current_status,
  settlement_date,
  _change_type,
  _commit_timestamp
FROM cloud_files(
  'abfss://silver@cdmstorage.dfs.core.windows.net/payments/payment_instruction/_change_data',
  'delta'
)
WHERE _change_type IN ('insert', 'update_postimage');
```

### Neo4j Sync Process

```python
# Databricks notebook to sync to Neo4j
from neo4j import GraphDatabase
from pyspark.sql import functions as F

# Read CDC stream
payment_changes = spark.readStream \
  .format("delta") \
  .table("cdm_silver.payments.payment_instruction") \
  .where("_change_type IN ('insert', 'update_postimage')")

# Write to Neo4j
def write_to_neo4j(batch_df, batch_id):
    driver = GraphDatabase.driver(
        "neo4j://neo4j-cluster:7687",
        auth=("neo4j", dbutils.secrets.get("neo4j", "password"))
    )

    with driver.session() as session:
        for row in batch_df.collect():
            session.run("""
                MERGE (p:PaymentInstruction {paymentId: $paymentId})
                SET p.currentStatus = $status,
                    p.settlementDate = date($settlementDate),
                    p.lastUpdated = datetime()
            """,
            paymentId=row.payment_id,
            status=row.current_status,
            settlementDate=str(row.settlement_date))

    driver.close()

# Start streaming write
query = payment_changes.writeStream \
  .foreachBatch(write_to_neo4j) \
  .outputMode("update") \
  .trigger(processingTime="1 minute") \
  .start()
```

---

## PERFORMANCE BENCHMARKS

### Query Performance Targets

| Query Type | Target Latency | Notes |
|------------|----------------|-------|
| Payment lookup by ID | < 100ms | Using Liquid Clustering |
| Party/Account lookup | < 50ms | SCD Type 2 with clustering |
| Payment status history | < 500ms | StatusEvent partitioned by date |
| Daily settlement report | < 5 seconds | Partition pruning on settlement_date |
| Fraud pattern detection | < 10 seconds | Neo4j graph queries |
| Sanctions screening batch | < 1 minute | Parallel processing in Databricks |
| Monthly reconciliation | < 30 minutes | Full table scans with optimization |

### Optimization Techniques

```sql
-- Example: Optimized settlement report query
SELECT
  settlement_date,
  region,
  COUNT(*) as payment_count,
  SUM(instructed_amount.amount) as total_value
FROM cdm_silver.payments.payment_instruction
WHERE partition_year = 2025
  AND partition_month = 12
  AND settlement_date = '2025-12-18'
  AND current_status = 'settled'
GROUP BY settlement_date, region;
-- Execution: Scans only 1 day's partitions, uses Liquid Clustering

-- Example: Multi-hop payment chain (Neo4j)
MATCH path = (start:PaymentInstruction)-[:COVERS|RELATED_TO*1..5]->(end:PaymentInstruction)
WHERE start.paymentId = '550e8400-e29b-41d4-a716-446655440000'
RETURN path;
-- Execution: < 1 second with proper indexes
```

---

## DISASTER RECOVERY

### Backup Strategy

```sql
-- Daily full backup to separate region
CREATE TABLE IF NOT EXISTS cdm_backup_dr.payments.payment_instruction
DEEP CLONE cdm_silver.payments.payment_instruction;

-- Incremental backup using time travel
CREATE OR REPLACE TABLE cdm_backup_dr.payments.payment_instruction_incremental
AS SELECT * FROM cdm_silver.payments.payment_instruction
VERSION AS OF (SELECT MAX(version) - 1 FROM
  (DESCRIBE HISTORY cdm_silver.payments.payment_instruction));

-- Point-in-time restore
RESTORE TABLE cdm_silver.payments.payment_instruction
TO VERSION AS OF 12345;

-- Restore from timestamp
RESTORE TABLE cdm_silver.payments.payment_instruction
TO TIMESTAMP AS OF '2025-12-18T00:00:00Z';
```

### Cross-Region Replication

```sql
-- Replicate to DR region (async)
CREATE OR REPLACE TABLE cdm_dr_eastus2.payments.payment_instruction
SHALLOW CLONE cdm_silver.payments.payment_instruction;

-- Schedule incremental replication (every 15 minutes)
CREATE OR REPLACE JOB dr_replication_job
SCHEDULE CRON '*/15 * * * *'
AS
  INSERT OVERWRITE cdm_dr_eastus2.payments.payment_instruction
  SELECT * FROM cdm_silver.payments.payment_instruction
  WHERE last_updated_timestamp > (
    SELECT COALESCE(MAX(last_updated_timestamp), '1970-01-01')
    FROM cdm_dr_eastus2.payments.payment_instruction
  );
```

---

## DOCUMENT STATUS

**Completeness Level**: 100%

**Components Documented**:
- ✅ Core Tables (PaymentInstruction, Party, Account, FinancialInstitution, Settlement, Charge, StatusEvent)
- ✅ Compliance Tables (ScreeningResult)
- ✅ Reference Tables (Currency, Country)
- ✅ JSON Schemas (PaymentInstruction, Party)
- ✅ Partitioning Strategies
- ✅ Indexing (Databricks Liquid Clustering, Neo4j)
- ✅ Sample Data
- ✅ Neo4j Graph Schema
- ✅ Unity Catalog Configuration
- ✅ Data Retention and Archival
- ✅ CDC Configuration
- ✅ Performance Benchmarks
- ✅ Disaster Recovery

**Total Tables Defined**: 10 core + compliance + reference = Full physical model

**Storage Architecture**: Databricks Delta Lake + Neo4j Graph Database

**Document Version**: 1.0 - COMPLETE

**Last Updated**: December 18, 2025

---
