-- GPS Payments CDM - Silver Zone Tables
-- Databricks Delta Lake DDL
-- Version: 1.0.0
-- Date: 2024-12-20

-- =============================================================================
-- SILVER ZONE: CDM-conformant, cleansed, validated data
-- - Transform to Payments CDM structure
-- - Apply data quality rules
-- - Enforce referential integrity
-- - Full lineage from bronze to CDM fields
-- - Bi-temporal versioning (valid_from, valid_to)
-- =============================================================================

USE CATALOG gps_cdm;

CREATE SCHEMA IF NOT EXISTS silver
COMMENT 'CDM-conformant payment data with data quality and lineage';

USE SCHEMA silver;

-- =============================================================================
-- PAYMENT CORE DOMAIN
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Payment (Root entity)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.payment (
    -- Primary Key
    payment_id STRING NOT NULL COMMENT 'UUID v4 primary key',

    -- Core Attributes
    payment_type STRING NOT NULL COMMENT 'CREDIT_TRANSFER, DIRECT_DEBIT, RETURN, REVERSAL',
    scheme_code STRING NOT NULL COMMENT 'ACH, FEDWIRE, SWIFT, SEPA, etc.',
    status STRING NOT NULL COMMENT 'Current lifecycle status',
    direction STRING NOT NULL COMMENT 'INBOUND, OUTBOUND, INTERNAL',
    cross_border_flag BOOLEAN DEFAULT FALSE,
    priority STRING DEFAULT 'NORM',

    -- Foreign Keys
    instruction_id STRING COMMENT 'FK to payment_instruction',
    settlement_id STRING COMMENT 'FK to settlement',

    -- Timestamps
    created_at TIMESTAMP NOT NULL,

    -- Bi-temporal Columns
    valid_from DATE NOT NULL,
    valid_to DATE,
    is_current BOOLEAN NOT NULL,

    -- Source Tracking
    source_system STRING NOT NULL,
    source_system_record_id STRING,
    source_message_type STRING,
    ingestion_timestamp TIMESTAMP,
    bronze_to_silver_timestamp TIMESTAMP,

    -- Data Quality
    data_quality_score DECIMAL(5,2),
    data_quality_dimensions MAP<STRING, DECIMAL(5,2)>,
    data_quality_issues ARRAY<STRING>,

    -- Lineage
    lineage_source_table STRING,
    lineage_batch_id STRING,
    lineage_pipeline_run_id STRING,

    -- Partitioning
    partition_year INT NOT NULL,
    partition_month INT NOT NULL,
    region STRING NOT NULL,
    product_type STRING,

    -- Audit Columns
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    last_updated_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    last_updated_by STRING DEFAULT 'SYSTEM',
    record_version INT DEFAULT 1,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_timestamp TIMESTAMP
)
USING DELTA
PARTITIONED BY (partition_year, partition_month, region)
CLUSTER BY (payment_type, status, created_at)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.logRetentionDuration' = '90 days',
    'delta.deletedFileRetentionDuration' = '30 days',
    'delta.enableChangeDataFeed' = 'true',
    'delta.columnMapping.mode' = 'name'
)
COMMENT 'Silver layer: Root payment entity with lifecycle tracking';

-- -----------------------------------------------------------------------------
-- Payment Instruction
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.payment_instruction (
    instruction_id STRING NOT NULL,
    payment_id STRING NOT NULL COMMENT 'FK to payment',

    -- Identifiers
    end_to_end_id STRING COMMENT 'ISO 20022 E2E ID',
    uetr STRING COMMENT 'SWIFT UETR',
    transaction_id STRING,
    instruction_id_ext STRING,

    -- Parties
    debtor_id STRING NOT NULL COMMENT 'FK to party',
    debtor_account_id STRING COMMENT 'FK to account',
    debtor_agent_id STRING COMMENT 'FK to financial_institution',
    creditor_id STRING NOT NULL COMMENT 'FK to party',
    creditor_account_id STRING,
    creditor_agent_id STRING,

    -- Amount
    instructed_amount DECIMAL(18,4) NOT NULL,
    instructed_currency STRING NOT NULL,
    interbank_settlement_amount DECIMAL(18,4),
    interbank_settlement_currency STRING,
    exchange_rate DECIMAL(18,10),

    -- Dates
    requested_execution_date DATE NOT NULL,
    requested_execution_time TIMESTAMP,
    value_date DATE,
    settlement_date DATE,

    -- Purpose
    purpose STRING,
    purpose_description STRING,
    charge_bearer STRING DEFAULT 'SHAR',

    -- Compliance
    sanctions_screening_status STRING DEFAULT 'not_screened',
    sanctions_screening_timestamp TIMESTAMP,
    fraud_score DECIMAL(5,2),
    fraud_flags ARRAY<STRING>,
    aml_risk_rating STRING,
    pep_flag BOOLEAN DEFAULT FALSE,
    structuring_indicator BOOLEAN DEFAULT FALSE,

    -- Regulatory
    regulatory_reporting ARRAY<STRUCT<
        reporting_type: STRING,
        reporting_code: STRING,
        jurisdiction: STRING
    >>,

    -- Remittance
    remittance_unstructured ARRAY<STRING>,
    remittance_reference STRING,

    -- Extensions (STRUCT for regulatory-specific fields)
    extensions STRUCT<
        fatca: STRUCT<us_indicia: BOOLEAN, fatca_status: STRING>,
        austrac: STRUCT<ordering_institution: STRING, ifti_reporting: BOOLEAN>,
        fincen: STRUCT<ctr_eligible: BOOLEAN, sar_alert: STRING>
    >,

    -- Bi-temporal
    valid_from DATE NOT NULL,
    valid_to DATE,
    is_current BOOLEAN NOT NULL,

    -- Source Tracking
    source_system STRING NOT NULL,
    source_system_record_id STRING,
    source_message_content STRING COMMENT 'Original message for audit',
    ingestion_timestamp TIMESTAMP,
    bronze_to_silver_timestamp TIMESTAMP,

    -- Data Quality
    data_quality_score DECIMAL(5,2),
    data_quality_issues ARRAY<STRING>,

    -- Lineage
    lineage_source_table STRING,
    lineage_source_columns ARRAY<STRING>,

    -- Partitioning
    partition_year INT NOT NULL,
    partition_month INT NOT NULL,
    region STRING NOT NULL,
    product_type STRING,

    -- Audit
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    last_updated_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    last_updated_by STRING DEFAULT 'SYSTEM',
    record_version INT DEFAULT 1,
    is_deleted BOOLEAN DEFAULT FALSE
)
USING DELTA
PARTITIONED BY (partition_year, partition_month, region)
CLUSTER BY (payment_id, debtor_id, creditor_id)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.enableChangeDataFeed' = 'true',
    'delta.columnMapping.mode' = 'name'
);

-- -----------------------------------------------------------------------------
-- Credit Transfer
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.credit_transfer (
    credit_transfer_id STRING NOT NULL,
    payment_id STRING NOT NULL,

    intermediary_agent_1_id STRING,
    intermediary_agent_2_id STRING,
    intermediary_agent_3_id STRING,
    instruction_for_creditor_agent STRING,
    instruction_for_next_agent STRING,
    previous_instructing_agent_id STRING,

    -- Audit
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    last_updated_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    record_version INT DEFAULT 1
)
USING DELTA
CLUSTER BY (payment_id)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- -----------------------------------------------------------------------------
-- Direct Debit
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.direct_debit (
    direct_debit_id STRING NOT NULL,
    payment_id STRING NOT NULL,

    mandate_id STRING NOT NULL,
    mandate_date DATE NOT NULL,
    sequence_type STRING NOT NULL COMMENT 'FRST, RCUR, FNAL, OOFF',
    creditor_scheme_id STRING,
    direct_debit_type STRING,
    amendment_indicator BOOLEAN DEFAULT FALSE,

    -- Audit
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    last_updated_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    record_version INT DEFAULT 1
)
USING DELTA
CLUSTER BY (payment_id, mandate_id)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- -----------------------------------------------------------------------------
-- Payment Return
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.payment_return (
    return_id STRING NOT NULL,
    original_payment_id STRING NOT NULL,
    return_payment_id STRING NOT NULL,

    return_reason_code STRING NOT NULL,
    return_reason_description STRING,
    original_end_to_end_id STRING,
    original_transaction_id STRING,
    return_amount DECIMAL(18,4) NOT NULL,
    return_currency STRING NOT NULL,
    return_date DATE NOT NULL,
    charges_information STRING,

    -- Audit
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    record_version INT DEFAULT 1
)
USING DELTA
CLUSTER BY (original_payment_id, return_date)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- -----------------------------------------------------------------------------
-- Payment Reversal
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.payment_reversal (
    reversal_id STRING NOT NULL,
    original_payment_id STRING NOT NULL,
    reversal_payment_id STRING NOT NULL,

    reversal_reason_code STRING NOT NULL,
    reversal_reason_description STRING,
    original_interbank_settlement_amount DECIMAL(18,4),
    original_interbank_settlement_currency STRING,
    reversal_date DATE NOT NULL,

    -- Audit
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    record_version INT DEFAULT 1
)
USING DELTA
CLUSTER BY (original_payment_id)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- -----------------------------------------------------------------------------
-- Payment Status Report
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.payment_status_report (
    status_report_id STRING NOT NULL,
    payment_id STRING NOT NULL,

    message_id STRING NOT NULL,
    creation_date_time TIMESTAMP NOT NULL,
    status_code STRING NOT NULL,
    status_reason_code STRING,
    status_reason_description STRING,
    acceptance_date_time TIMESTAMP,
    effective_interbank_settlement_date DATE,
    original_message_id STRING,

    -- Partitioning
    partition_year INT NOT NULL,
    partition_month INT NOT NULL,

    -- Audit
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    record_version INT DEFAULT 1
)
USING DELTA
PARTITIONED BY (partition_year, partition_month)
CLUSTER BY (payment_id, creation_date_time)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- =============================================================================
-- PARTY DOMAIN
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Party
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.party (
    party_id STRING NOT NULL,
    party_type STRING NOT NULL COMMENT 'INDIVIDUAL, ORGANIZATION, GOVERNMENT, FINANCIAL_INSTITUTION',

    -- Core Identification
    name STRING NOT NULL,
    given_name STRING,
    family_name STRING,
    suffix STRING,
    dba_name STRING,

    -- Personal Details (Individuals)
    date_of_birth DATE,
    place_of_birth STRING,
    nationality ARRAY<STRING>,

    -- Tax Information
    tax_id STRING,
    tax_id_type STRING,

    -- FATCA Extensions
    us_tax_status STRING,
    fatca_classification STRING,
    w8ben_status STRING,
    w9_status STRING,
    substantial_us_owner BOOLEAN,

    -- CRS Extensions
    crs_reportable BOOLEAN,
    crs_entity_type STRING,
    tax_residencies ARRAY<STRUCT<
        country: STRING,
        tin_type: STRING,
        tin: STRING,
        tax_residency_basis: STRING,
        effective_from: DATE,
        effective_to: DATE
    >>,

    -- FinCEN Extensions
    occupation STRING,
    naics_code STRING,
    form_of_identification STRING,
    identification_number STRING,
    identification_issuing_country STRING,
    identification_issuing_state STRING,
    alternate_names ARRAY<STRING>,

    -- APAC National IDs
    national_id_type STRING,
    national_id_number STRING,
    china_hukou STRING,
    india_aadhar_number STRING,
    india_pan_number STRING,
    japan_my_number STRING,
    singapore_nric_fin STRING,

    -- Address
    address STRUCT<
        street_name: STRING,
        building_number: STRING,
        building_name: STRING,
        floor: STRING,
        post_box: STRING,
        post_code: STRING,
        town_name: STRING,
        district_name: STRING,
        country_sub_division: STRING,
        country: STRING,
        address_line_1: STRING,
        address_line_2: STRING
    >,

    -- Contact
    contact_details STRUCT<
        email_address: STRING,
        phone_number: STRING,
        mobile_number: STRING
    >,

    -- Risk/Compliance
    pep_flag BOOLEAN DEFAULT FALSE,
    pep_category STRING,
    risk_rating STRING,
    sanctions_screening_status STRING DEFAULT 'not_screened',
    sanctions_list_match ARRAY<STRUCT<
        list_name: STRING,
        match_type: STRING,
        match_score: DECIMAL(5,2)
    >>,

    -- Bi-temporal
    valid_from DATE NOT NULL,
    valid_to DATE,
    is_current BOOLEAN NOT NULL,

    -- Source Tracking
    source_system STRING NOT NULL,
    source_system_record_id STRING,

    -- Partitioning
    partition_year INT NOT NULL,
    region STRING NOT NULL,

    -- Audit
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    last_updated_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    last_updated_by STRING DEFAULT 'SYSTEM',
    record_version INT DEFAULT 1,
    is_deleted BOOLEAN DEFAULT FALSE
)
USING DELTA
PARTITIONED BY (partition_year, region)
CLUSTER BY (party_type, name)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.enableChangeDataFeed' = 'true',
    'delta.columnMapping.mode' = 'name'
);

-- -----------------------------------------------------------------------------
-- Financial Institution
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.financial_institution (
    fi_id STRING NOT NULL,
    institution_name STRING NOT NULL,

    -- Identifiers
    bic STRING,
    lei STRING,
    national_clearing_code STRING,
    national_clearing_system STRING,

    -- FinCEN Fields
    rssd_number STRING,
    tin_type STRING,
    tin_value STRING,
    fi_type STRING,
    msb_registration_number STRING,
    primary_regulator STRING,

    -- FATCA
    fatca_giin STRING,

    -- Islamic Finance
    sharia_compliant BOOLEAN DEFAULT FALSE,
    islamic_finance_type STRING,

    -- Address
    address STRUCT<
        street_name: STRING,
        building_number: STRING,
        post_code: STRING,
        town_name: STRING,
        country_sub_division: STRING,
        country: STRING
    >,
    country STRING NOT NULL,
    branch_identification STRING,
    branch_name STRING,

    -- Bi-temporal
    valid_from DATE NOT NULL,
    valid_to DATE,
    is_current BOOLEAN NOT NULL,

    -- Source
    source_system STRING NOT NULL,

    -- Audit
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    last_updated_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    record_version INT DEFAULT 1,
    is_deleted BOOLEAN DEFAULT FALSE
)
USING DELTA
CLUSTER BY (bic, country)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- =============================================================================
-- ACCOUNT DOMAIN
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Account
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.account (
    account_id STRING NOT NULL,
    account_number STRING NOT NULL,
    iban STRING,
    account_type STRING NOT NULL,
    currency STRING NOT NULL,

    financial_institution_id STRING NOT NULL,
    branch_id STRING,
    account_status STRING NOT NULL,

    open_date DATE NOT NULL,
    close_date DATE,

    -- Balances
    current_balance DECIMAL(18,4),
    available_balance DECIMAL(18,4),
    ledger_balance DECIMAL(18,4),
    last_transaction_date TIMESTAMP,

    -- FATCA/CRS
    fatca_status STRING,
    fatca_giin STRING,
    account_holder_type STRING,
    crs_reportable_account BOOLEAN,
    controlling_persons ARRAY<STRUCT<
        party_id: STRING,
        control_type: STRING,
        ownership_percentage: DECIMAL(5,2),
        tax_residence: ARRAY<STRING>,
        tin: STRING,
        tin_type: STRING,
        is_pep: BOOLEAN
    >>,
    dormant_account BOOLEAN,
    account_balance_for_tax_reporting DECIMAL(18,4),
    withholding_tax_rate DECIMAL(5,2),

    -- FinCEN
    loan_amount DECIMAL(18,2),
    loan_origination DATE,

    -- Risk
    sanctions_screening_status STRING DEFAULT 'not_screened',
    risk_rating STRING,

    -- Bi-temporal
    valid_from DATE NOT NULL,
    valid_to DATE,
    is_current BOOLEAN NOT NULL,

    -- Source
    source_system STRING NOT NULL,
    source_system_record_id STRING,

    -- Partitioning
    partition_year INT NOT NULL,
    region STRING NOT NULL,

    -- Audit
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    last_updated_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    record_version INT DEFAULT 1,
    is_deleted BOOLEAN DEFAULT FALSE
)
USING DELTA
PARTITIONED BY (partition_year, region)
CLUSTER BY (account_number, account_type)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- -----------------------------------------------------------------------------
-- Account Owner
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.account_owner (
    account_owner_id STRING NOT NULL,
    account_id STRING NOT NULL,
    party_id STRING NOT NULL,

    ownership_type STRING NOT NULL,
    ownership_percentage DECIMAL(5,2),
    role STRING,
    signing_authority STRING,
    signing_limit DECIMAL(18,2),

    -- CRS/FATCA
    is_controlling_person BOOLEAN DEFAULT FALSE,
    control_type STRING,
    tax_residence ARRAY<STRING>,

    -- Bi-temporal
    effective_from DATE NOT NULL,
    effective_to DATE,
    is_current BOOLEAN NOT NULL,

    -- Audit
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    last_updated_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    record_version INT DEFAULT 1
)
USING DELTA
CLUSTER BY (account_id, party_id)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- =============================================================================
-- SETTLEMENT DOMAIN
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Settlement
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.settlement (
    settlement_id STRING NOT NULL,
    payment_id STRING NOT NULL,

    settlement_date DATE NOT NULL,
    settlement_amount DECIMAL(18,4) NOT NULL,
    settlement_currency STRING NOT NULL,
    settlement_method STRING NOT NULL,
    settlement_status STRING NOT NULL,

    clearing_system_id STRING,
    clearing_system_code STRING,
    settlement_cycle STRING,

    interbank_settlement_date DATE,
    interbank_settlement_amount DECIMAL(18,4),
    interbank_settlement_currency STRING,

    settlement_account_id STRING,
    settlement_time TIMESTAMP,
    settlement_reference STRING,
    batch_id STRING,
    netting_indicator BOOLEAN DEFAULT FALSE,

    -- Partitioning
    partition_year INT NOT NULL,
    partition_month INT NOT NULL,

    -- Audit
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    settled_timestamp TIMESTAMP,
    last_updated_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    record_version INT DEFAULT 1
)
USING DELTA
PARTITIONED BY (partition_year, partition_month)
CLUSTER BY (payment_id, settlement_date)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- -----------------------------------------------------------------------------
-- Clearing System (Reference Data)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.clearing_system (
    clearing_system_id STRING NOT NULL,
    system_code STRING NOT NULL,
    system_name STRING NOT NULL,
    system_type STRING NOT NULL,
    country STRING NOT NULL,
    currency STRING NOT NULL,
    operating_hours STRING,
    cut_off_time STRING,
    settlement_cycle STRING,
    operator STRING,
    max_transaction_amount DECIMAL(18,2),
    min_transaction_amount DECIMAL(18,2),

    -- Bi-temporal
    valid_from DATE NOT NULL,
    valid_to DATE,
    is_current BOOLEAN NOT NULL,

    -- Audit
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    last_updated_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    record_version INT DEFAULT 1
)
USING DELTA
CLUSTER BY (system_code, country)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true'
);

-- =============================================================================
-- EVENTS DOMAIN
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Payment Event
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.payment_event (
    event_id STRING NOT NULL,
    payment_id STRING NOT NULL,

    event_type STRING NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    previous_state STRING,
    new_state STRING NOT NULL,

    actor STRING,
    actor_type STRING,
    actor_id STRING,

    details STRING COMMENT 'JSON details',
    correlation_id STRING,
    parent_event_id STRING,
    duration_ms LONG,

    error_code STRING,
    error_message STRING,
    source_system STRING,
    external_reference STRING,

    -- Partitioning
    partition_year INT NOT NULL,
    partition_month INT NOT NULL,

    -- Audit
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
USING DELTA
PARTITIONED BY (partition_year, partition_month)
CLUSTER BY (payment_id, event_type, event_timestamp)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- =============================================================================
-- LINEAGE DOMAIN
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Lineage Metadata
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.lineage_metadata (
    lineage_id STRING NOT NULL,
    entity_type STRING NOT NULL,
    entity_id STRING NOT NULL,
    field_name STRING NOT NULL,
    field_path STRING,

    source_system STRING NOT NULL,
    source_database STRING,
    source_schema STRING,
    source_table STRING,
    source_field STRING NOT NULL,
    source_field_path STRING,

    transformation_type STRING NOT NULL,
    transformation_logic STRING,
    transformation_version STRING,

    lookup_table STRING,
    lookup_key STRING,
    confidence_score DECIMAL(5,4),
    data_quality_impact STRING,

    effective_from TIMESTAMP NOT NULL,
    effective_to TIMESTAMP,

    created_by STRING,
    created_timestamp TIMESTAMP NOT NULL,
    batch_id STRING,
    pipeline_id STRING,
    pipeline_run_id STRING
)
USING DELTA
CLUSTER BY (entity_type, entity_id, field_name)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- -----------------------------------------------------------------------------
-- Audit Trail
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.audit_trail (
    audit_id STRING NOT NULL,
    entity_type STRING NOT NULL,
    entity_id STRING NOT NULL,

    action STRING NOT NULL,
    action_timestamp TIMESTAMP NOT NULL,

    actor STRING NOT NULL,
    actor_type STRING NOT NULL,
    actor_ip STRING,
    actor_location STRING,
    session_id STRING,
    request_id STRING,
    correlation_id STRING,

    old_values STRING COMMENT 'JSON of old values',
    new_values STRING COMMENT 'JSON of new values',
    changed_fields ARRAY<STRING>,

    change_reason STRING,
    change_ticket STRING,
    approval_id STRING,
    approved_by STRING,
    approval_timestamp TIMESTAMP,

    data_classification STRING,
    retention_period_days INT,
    is_sensitive BOOLEAN DEFAULT FALSE,
    metadata STRING COMMENT 'JSON metadata',

    -- Partitioning
    partition_year INT NOT NULL,
    partition_month INT NOT NULL
)
USING DELTA
PARTITIONED BY (partition_year, partition_month)
CLUSTER BY (entity_type, entity_id, action_timestamp)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- =============================================================================
-- FOREIGN KEY CONSTRAINTS (Logical - enforced at application level)
-- =============================================================================

-- Note: Databricks Delta Lake supports constraints but doesn't enforce FK constraints
-- These are documented for reference and enforced in application logic

-- payment.instruction_id -> payment_instruction.instruction_id
-- payment_instruction.payment_id -> payment.payment_id
-- payment_instruction.debtor_id -> party.party_id
-- payment_instruction.creditor_id -> party.party_id
-- payment_instruction.debtor_account_id -> account.account_id
-- payment_instruction.creditor_account_id -> account.account_id
-- account.financial_institution_id -> financial_institution.fi_id
-- account_owner.account_id -> account.account_id
-- account_owner.party_id -> party.party_id
-- settlement.payment_id -> payment.payment_id
-- payment_event.payment_id -> payment.payment_id
