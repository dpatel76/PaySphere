-- GPS Payments CDM - Gold Zone Tables
-- Databricks Delta Lake DDL
-- Version: 1.0.0
-- Date: 2024-12-20

-- =============================================================================
-- GOLD ZONE: Universal Business Entity Views & Data Products
-- - Consumption-pattern driven design
-- - Pre-built universal entity views (360 views)
-- - Domain-specific data products
-- - Self-service ready datasets
-- =============================================================================

USE CATALOG gps_cdm;

CREATE SCHEMA IF NOT EXISTS gold
COMMENT 'Consumption-ready analytics views and data products';

USE SCHEMA gold;

-- =============================================================================
-- UNIVERSAL BUSINESS ENTITY VIEWS (360 Views)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Party 360 - Complete view of counterparty across all interactions
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gold.party_360 (
    -- Identity
    party_id STRING NOT NULL,
    party_type STRING NOT NULL,
    primary_name STRING NOT NULL,
    all_names ARRAY<STRING>,

    -- Profile
    profile STRUCT<
        date_of_birth: DATE,
        nationality: ARRAY<STRING>,
        occupation: STRING,
        industry_code: STRING,
        pep_flag: BOOLEAN,
        pep_category: STRING
    >,

    -- Tax Information
    tax_profile STRUCT<
        primary_tax_id: STRING,
        tax_id_type: STRING,
        us_tax_status: STRING,
        fatca_classification: STRING,
        crs_reportable: BOOLEAN,
        tax_residencies: ARRAY<STRING>
    >,

    -- Address
    primary_address STRUCT<
        street: STRING,
        city: STRING,
        state: STRING,
        postal_code: STRING,
        country: STRING
    >,

    -- All Accounts
    accounts ARRAY<STRUCT<
        account_id: STRING,
        account_number: STRING,
        account_type: STRING,
        currency: STRING,
        current_balance: DECIMAL(18,4),
        status: STRING,
        ownership_type: STRING,
        ownership_percentage: DECIMAL(5,2)
    >>,
    total_accounts INT,

    -- Payment Activity
    payment_metrics STRUCT<
        total_payments_count: LONG,
        total_payments_value: DECIMAL(22,4),
        avg_payment_value: DECIMAL(18,4),
        last_payment_date: DATE,
        first_payment_date: DATE,
        payments_sent_count: LONG,
        payments_received_count: LONG,
        cross_border_count: LONG
    >,

    -- Payment Volume by Period
    monthly_volume ARRAY<STRUCT<
        year_month: STRING,
        payment_count: LONG,
        payment_value: DECIMAL(22,4)
    >>,

    -- Risk Assessment
    risk_profile STRUCT<
        risk_rating: STRING,
        risk_score: DECIMAL(5,2),
        sanctions_status: STRING,
        last_sanctions_check: TIMESTAMP,
        aml_alerts_count: INT,
        fraud_alerts_count: INT,
        structuring_indicator: BOOLEAN
    >,

    -- Relationships
    related_parties ARRAY<STRUCT<
        party_id: STRING,
        name: STRING,
        relationship_type: STRING,
        payment_count: LONG
    >>,

    -- Compliance Flags
    compliance_flags STRUCT<
        ctr_eligible: BOOLEAN,
        sar_filed: BOOLEAN,
        ofac_blocked: BOOLEAN,
        enhanced_due_diligence: BOOLEAN
    >,

    -- Metadata
    last_updated TIMESTAMP,
    data_quality_score DECIMAL(5,2),

    -- Partitioning
    region STRING NOT NULL
)
USING DELTA
PARTITIONED BY (region)
CLUSTER BY (party_type, primary_name)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
COMMENT 'Gold layer: 360-degree view of party with all related data';

-- -----------------------------------------------------------------------------
-- Payment 360 - Full payment lifecycle with all related entities
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gold.payment_360 (
    -- Identity
    payment_id STRING NOT NULL,
    instruction_id STRING,
    end_to_end_id STRING,
    uetr STRING,

    -- Classification
    payment_type STRING NOT NULL,
    scheme_code STRING NOT NULL,
    direction STRING NOT NULL,
    cross_border_flag BOOLEAN,

    -- Current Status
    current_status STRING NOT NULL,
    status_timestamp TIMESTAMP,
    status_reason STRING,

    -- Full Lifecycle
    lifecycle_events ARRAY<STRUCT<
        event_type: STRING,
        event_timestamp: TIMESTAMP,
        previous_state: STRING,
        new_state: STRING,
        actor: STRING,
        duration_ms: LONG
    >>,

    -- Parties
    debtor STRUCT<
        party_id: STRING,
        name: STRING,
        party_type: STRING,
        country: STRING,
        risk_rating: STRING
    >,
    creditor STRUCT<
        party_id: STRING,
        name: STRING,
        party_type: STRING,
        country: STRING,
        risk_rating: STRING
    >,

    -- Accounts
    debtor_account STRUCT<
        account_id: STRING,
        account_number: STRING,
        account_type: STRING,
        currency: STRING
    >,
    creditor_account STRUCT<
        account_id: STRING,
        account_number: STRING,
        account_type: STRING,
        currency: STRING
    >,

    -- Agents
    debtor_agent STRUCT<
        fi_id: STRING,
        name: STRING,
        bic: STRING,
        country: STRING
    >,
    creditor_agent STRUCT<
        fi_id: STRING,
        name: STRING,
        bic: STRING,
        country: STRING
    >,
    intermediary_agents ARRAY<STRUCT<
        fi_id: STRING,
        name: STRING,
        bic: STRING,
        sequence: INT
    >>,

    -- Amounts
    instructed_amount DECIMAL(18,4) NOT NULL,
    instructed_currency STRING NOT NULL,
    settlement_amount DECIMAL(18,4),
    settlement_currency STRING,
    exchange_rate DECIMAL(18,10),
    total_charges DECIMAL(18,4),
    charge_details ARRAY<STRUCT<
        charge_type: STRING,
        amount: DECIMAL(18,4),
        currency: STRING,
        agent: STRING
    >>,

    -- Dates
    created_at TIMESTAMP,
    requested_execution_date DATE,
    value_date DATE,
    settlement_date DATE,
    completion_timestamp TIMESTAMP,

    -- Timing Metrics
    timing_metrics STRUCT<
        total_processing_time_ms: LONG,
        validation_time_ms: LONG,
        screening_time_ms: LONG,
        routing_time_ms: LONG,
        settlement_time_ms: LONG
    >,

    -- Compliance
    compliance_info STRUCT<
        sanctions_status: STRING,
        sanctions_check_timestamp: TIMESTAMP,
        fraud_score: DECIMAL(5,2),
        fraud_flags: ARRAY<STRING>,
        aml_risk_rating: STRING,
        pep_involved: BOOLEAN,
        ctr_eligible: BOOLEAN,
        sar_filed: BOOLEAN
    >,

    -- Remittance
    remittance_info STRUCT<
        unstructured: ARRAY<STRING>,
        creditor_reference: STRING,
        purpose: STRING,
        purpose_description: STRING
    >,

    -- Regulatory Reporting
    regulatory_reports ARRAY<STRUCT<
        report_type: STRING,
        jurisdiction: STRING,
        threshold_exceeded: BOOLEAN,
        report_status: STRING,
        report_date: DATE
    >>,

    -- Lineage
    lineage_path STRING COMMENT 'Source system -> Bronze -> Silver -> Gold',
    source_system STRING,
    source_message_type STRING,

    -- Data Quality
    dq_score DECIMAL(5,2),
    dq_issues ARRAY<STRING>,

    -- Partitioning
    partition_year INT NOT NULL,
    partition_month INT NOT NULL,
    region STRING NOT NULL
)
USING DELTA
PARTITIONED BY (partition_year, partition_month, region)
CLUSTER BY (payment_type, scheme_code, current_status)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
COMMENT 'Gold layer: Complete payment view with full lifecycle and all related entities';

-- -----------------------------------------------------------------------------
-- Account 360 - Account activity, balances, and relationships
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gold.account_360 (
    -- Identity
    account_id STRING NOT NULL,
    account_number STRING NOT NULL,
    iban STRING,
    account_type STRING NOT NULL,
    currency STRING NOT NULL,
    status STRING NOT NULL,

    -- Financial Institution
    financial_institution STRUCT<
        fi_id: STRING,
        name: STRING,
        bic: STRING,
        country: STRING
    >,

    -- Owners
    owners ARRAY<STRUCT<
        party_id: STRING,
        name: STRING,
        ownership_type: STRING,
        ownership_percentage: DECIMAL(5,2),
        is_primary: BOOLEAN
    >>,

    -- Balances
    current_balance DECIMAL(18,4),
    available_balance DECIMAL(18,4),
    balance_history ARRAY<STRUCT<
        as_of_date: DATE,
        balance: DECIMAL(18,4)
    >>,

    -- Activity Metrics
    activity_metrics STRUCT<
        total_debits_count: LONG,
        total_debits_value: DECIMAL(22,4),
        total_credits_count: LONG,
        total_credits_value: DECIMAL(22,4),
        avg_daily_balance: DECIMAL(18,4),
        last_debit_date: DATE,
        last_credit_date: DATE,
        dormant: BOOLEAN,
        days_since_last_activity: INT
    >,

    -- Monthly Activity
    monthly_activity ARRAY<STRUCT<
        year_month: STRING,
        debit_count: LONG,
        debit_value: DECIMAL(22,4),
        credit_count: LONG,
        credit_value: DECIMAL(22,4),
        ending_balance: DECIMAL(18,4)
    >>,

    -- Risk Indicators
    risk_indicators STRUCT<
        risk_rating: STRING,
        sanctions_status: STRING,
        unusual_activity_flag: BOOLEAN,
        velocity_alerts: INT,
        high_risk_counterparties: INT
    >,

    -- Tax Reporting
    tax_reporting STRUCT<
        fatca_status: STRING,
        crs_reportable: BOOLEAN,
        year_end_balance: DECIMAL(18,4),
        withholding_rate: DECIMAL(5,2)
    >,

    -- Linked Parties
    linked_parties ARRAY<STRUCT<
        party_id: STRING,
        name: STRING,
        relationship: STRING,
        transaction_count: LONG
    >>,

    -- Metadata
    open_date DATE,
    last_updated TIMESTAMP,
    data_quality_score DECIMAL(5,2),

    -- Partitioning
    region STRING NOT NULL
)
USING DELTA
PARTITIONED BY (region)
CLUSTER BY (account_type, status)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
COMMENT 'Gold layer: 360-degree view of account with activity and relationships';

-- =============================================================================
-- DOMAIN-SPECIFIC DATA PRODUCTS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Regulatory Ready - Pre-validated data for regulatory reports
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gold.regulatory_ready (
    -- Payment Reference
    payment_id STRING NOT NULL,
    instruction_id STRING,
    end_to_end_id STRING,

    -- Transaction Details
    transaction_date DATE NOT NULL,
    amount DECIMAL(18,4) NOT NULL,
    currency STRING NOT NULL,
    payment_type STRING NOT NULL,
    scheme_code STRING NOT NULL,

    -- Parties
    ordering_party STRUCT<
        party_id: STRING,
        name: STRING,
        address: STRING,
        country: STRING,
        tax_id: STRING,
        date_of_birth: DATE,
        occupation: STRING,
        identification: STRING
    >,
    beneficiary_party STRUCT<
        party_id: STRING,
        name: STRING,
        address: STRING,
        country: STRING
    >,

    -- Financial Institutions
    ordering_institution STRUCT<
        fi_id: STRING,
        name: STRING,
        bic: STRING,
        routing_code: STRING,
        country: STRING
    >,
    beneficiary_institution STRUCT<
        fi_id: STRING,
        name: STRING,
        bic: STRING,
        routing_code: STRING,
        country: STRING
    >,

    -- Report Eligibility Flags
    ctr_eligible BOOLEAN DEFAULT FALSE COMMENT 'FinCEN CTR: amount >= $10,000 cash',
    sar_eligible BOOLEAN DEFAULT FALSE COMMENT 'SAR candidate',
    ifti_eligible BOOLEAN DEFAULT FALSE COMMENT 'AUSTRAC IFTI: international transfer',
    ttr_eligible BOOLEAN DEFAULT FALSE COMMENT 'AUSTRAC TTR: amount >= AUD $10,000 cash',
    fatca_eligible BOOLEAN DEFAULT FALSE COMMENT 'FATCA reportable',
    crs_eligible BOOLEAN DEFAULT FALSE COMMENT 'CRS reportable',
    ofac_reportable BOOLEAN DEFAULT FALSE COMMENT 'OFAC blocking/rejection',

    -- Threshold Amounts (pre-calculated in local currencies)
    amount_usd DECIMAL(18,4),
    amount_aud DECIMAL(18,4),
    amount_gbp DECIMAL(18,4),
    amount_eur DECIMAL(18,4),

    -- Risk Scores
    risk_score DECIMAL(5,2),
    fraud_score DECIMAL(5,2),
    aml_risk_rating STRING,

    -- Compliance Flags
    cross_border BOOLEAN,
    cash_transaction BOOLEAN,
    pep_involved BOOLEAN,
    sanctions_hit BOOLEAN,
    structuring_indicator BOOLEAN,

    -- Metadata
    last_validated TIMESTAMP,
    validation_rules_version STRING,

    -- Partitioning
    partition_year INT NOT NULL,
    partition_month INT NOT NULL,
    jurisdiction STRING NOT NULL
)
USING DELTA
PARTITIONED BY (partition_year, partition_month, jurisdiction)
CLUSTER BY (ctr_eligible, sar_eligible, transaction_date)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
COMMENT 'Gold layer: Pre-validated data for regulatory report generation';

-- -----------------------------------------------------------------------------
-- Fraud Features - Pre-computed fraud detection features for ML
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gold.fraud_features (
    -- Entity Reference
    entity_type STRING NOT NULL COMMENT 'PAYMENT, PARTY, ACCOUNT',
    entity_id STRING NOT NULL,

    -- Feature Timestamp
    feature_timestamp TIMESTAMP NOT NULL,
    feature_date DATE NOT NULL,

    -- Velocity Features
    velocity_features STRUCT<
        txn_count_1h: INT,
        txn_count_24h: INT,
        txn_count_7d: INT,
        txn_count_30d: INT,
        txn_amount_1h: DECIMAL(22,4),
        txn_amount_24h: DECIMAL(22,4),
        txn_amount_7d: DECIMAL(22,4),
        txn_amount_30d: DECIMAL(22,4),
        unique_counterparties_24h: INT,
        unique_counterparties_7d: INT,
        unique_countries_7d: INT
    >,

    -- Behavioral Features
    behavioral_features STRUCT<
        avg_txn_amount_30d: DECIMAL(18,4),
        std_txn_amount_30d: DECIMAL(18,4),
        max_txn_amount_30d: DECIMAL(18,4),
        typical_txn_hour: INT,
        typical_txn_day_of_week: INT,
        new_counterparty_flag: BOOLEAN,
        new_country_flag: BOOLEAN,
        round_amount_flag: BOOLEAN
    >,

    -- Network Features (from graph)
    network_features STRUCT<
        degree_centrality: DECIMAL(10,6),
        betweenness_centrality: DECIMAL(10,6),
        connected_high_risk_parties: INT,
        connected_sar_parties: INT,
        cluster_id: STRING,
        community_risk_score: DECIMAL(5,2)
    >,

    -- Pattern Features
    pattern_features STRUCT<
        structuring_score: DECIMAL(5,2),
        round_tripping_score: DECIMAL(5,2),
        layering_score: DECIMAL(5,2),
        rapid_movement_score: DECIMAL(5,2),
        dormant_reactivation: BOOLEAN
    >,

    -- Aggregate Risk Score
    composite_fraud_score DECIMAL(5,2),
    fraud_risk_tier STRING COMMENT 'LOW, MEDIUM, HIGH, CRITICAL',

    -- Model Metadata
    model_version STRING,
    feature_version STRING,

    -- Partitioning
    partition_date DATE NOT NULL
)
USING DELTA
PARTITIONED BY (partition_date, entity_type)
CLUSTER BY (entity_id, feature_timestamp)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
COMMENT 'Gold layer: Pre-computed fraud detection features for ML models';

-- -----------------------------------------------------------------------------
-- Daily Payment Summary - Aggregated daily metrics
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gold.daily_payment_summary (
    summary_date DATE NOT NULL,
    region STRING NOT NULL,
    payment_type STRING NOT NULL,
    scheme_code STRING NOT NULL,
    direction STRING NOT NULL,

    -- Volume Metrics
    total_count LONG NOT NULL,
    total_amount DECIMAL(22,4) NOT NULL,
    avg_amount DECIMAL(18,4),
    min_amount DECIMAL(18,4),
    max_amount DECIMAL(18,4),

    -- Status Breakdown
    completed_count LONG,
    completed_amount DECIMAL(22,4),
    failed_count LONG,
    failed_amount DECIMAL(22,4),
    returned_count LONG,
    returned_amount DECIMAL(22,4),
    pending_count LONG,

    -- Cross-border
    cross_border_count LONG,
    cross_border_amount DECIMAL(22,4),

    -- Compliance
    ctr_count LONG,
    sar_count LONG,
    sanctions_hit_count LONG,
    fraud_alert_count LONG,

    -- Performance
    avg_processing_time_ms LONG,
    p95_processing_time_ms LONG,
    sla_breach_count LONG,

    -- Currency Breakdown
    currency_breakdown ARRAY<STRUCT<
        currency: STRING,
        count: LONG,
        amount: DECIMAL(22,4)
    >>,

    -- Metadata
    last_updated TIMESTAMP
)
USING DELTA
PARTITIONED BY (summary_date, region)
CLUSTER BY (payment_type, scheme_code)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true'
)
COMMENT 'Gold layer: Daily aggregated payment metrics';

-- -----------------------------------------------------------------------------
-- Corridor Metrics - Payment corridor analytics
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gold.corridor_metrics (
    metric_date DATE NOT NULL,
    origin_country STRING NOT NULL,
    destination_country STRING NOT NULL,
    payment_type STRING,
    scheme_code STRING,

    -- Volume
    transaction_count LONG NOT NULL,
    total_amount_usd DECIMAL(22,4),

    -- Performance
    avg_completion_time_hours DECIMAL(10,2),
    success_rate DECIMAL(5,4),
    return_rate DECIMAL(5,4),

    -- Cost
    avg_fx_rate DECIMAL(18,10),
    avg_fee_amount_usd DECIMAL(10,4),
    avg_fee_percentage DECIMAL(5,4),

    -- Top Currencies
    top_currencies ARRAY<STRUCT<
        currency: STRING,
        count: LONG,
        amount: DECIMAL(22,4)
    >>,

    -- Metadata
    last_updated TIMESTAMP
)
USING DELTA
PARTITIONED BY (metric_date)
CLUSTER BY (origin_country, destination_country)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true'
)
COMMENT 'Gold layer: Cross-border corridor metrics';

-- =============================================================================
-- GOLD ZONE VIEWS (Virtual aggregations)
-- =============================================================================

-- Real-time payment status view
CREATE OR REPLACE VIEW gold.v_payment_status_realtime AS
SELECT
    p.payment_id,
    p.payment_type,
    p.scheme_code,
    p.status AS current_status,
    pi.instructed_amount,
    pi.instructed_currency,
    pi.end_to_end_id,
    p.created_at,
    TIMESTAMPDIFF(MINUTE, p.created_at, CURRENT_TIMESTAMP()) AS age_minutes
FROM silver.payment p
JOIN silver.payment_instruction pi ON p.instruction_id = pi.instruction_id
WHERE p.is_current = TRUE
  AND p.status NOT IN ('completed', 'settled', 'cancelled', 'rejected', 'failed');

-- High-risk payments view
CREATE OR REPLACE VIEW gold.v_high_risk_payments AS
SELECT
    p.payment_id,
    p.payment_type,
    pi.instructed_amount,
    pi.instructed_currency,
    pi.fraud_score,
    pi.sanctions_screening_status,
    pi.aml_risk_rating,
    db.name AS debtor_name,
    cr.name AS creditor_name,
    p.created_at
FROM silver.payment p
JOIN silver.payment_instruction pi ON p.instruction_id = pi.instruction_id
JOIN silver.party db ON pi.debtor_id = db.party_id AND db.is_current = TRUE
JOIN silver.party cr ON pi.creditor_id = cr.party_id AND cr.is_current = TRUE
WHERE p.is_current = TRUE
  AND (
    pi.fraud_score >= 80
    OR pi.sanctions_screening_status = 'hit'
    OR pi.aml_risk_rating IN ('high', 'very_high')
  );
