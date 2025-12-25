-- GPS CDM - Analytical Layer Tables (anl_*)
-- ==========================================
-- Layer 4: Data products for consumption
-- Denormalized, aggregated, optimized for specific use cases.

-- =====================================================
-- ANL_PAYMENT_360 (Denormalized payment view)
-- =====================================================
CREATE TABLE IF NOT EXISTS analytical.anl_payment_360 (
    payment_id VARCHAR(36) PRIMARY KEY,
    instruction_id VARCHAR(36),
    end_to_end_id VARCHAR(35),
    uetr VARCHAR(36),
    message_id VARCHAR(50),

    -- Source
    source_message_type VARCHAR(50) NOT NULL,
    source_system VARCHAR(100),

    -- Classification
    payment_type VARCHAR(50) NOT NULL,
    scheme_code VARCHAR(30) NOT NULL,
    direction VARCHAR(20) NOT NULL,
    cross_border_flag BOOLEAN,
    priority VARCHAR(10),

    -- Status
    current_status VARCHAR(30),
    status_timestamp TIMESTAMP,

    -- Debtor (denormalized)
    debtor_id VARCHAR(36),
    debtor_name VARCHAR(200),
    debtor_type VARCHAR(30),
    debtor_country VARCHAR(3),
    debtor_risk_rating VARCHAR(20),
    debtor_pep_flag BOOLEAN,

    -- Debtor Account
    debtor_account_number VARCHAR(50),
    debtor_iban VARCHAR(34),

    -- Debtor Agent
    debtor_agent_bic VARCHAR(11),
    debtor_agent_name VARCHAR(200),

    -- Creditor (denormalized)
    creditor_id VARCHAR(36),
    creditor_name VARCHAR(200),
    creditor_type VARCHAR(30),
    creditor_country VARCHAR(3),
    creditor_risk_rating VARCHAR(20),
    creditor_pep_flag BOOLEAN,

    -- Creditor Account
    creditor_account_number VARCHAR(50),
    creditor_iban VARCHAR(34),

    -- Creditor Agent
    creditor_agent_bic VARCHAR(11),
    creditor_agent_name VARCHAR(200),

    -- Amounts
    instructed_amount DECIMAL(18,4) NOT NULL,
    instructed_currency VARCHAR(3) NOT NULL,
    settlement_amount DECIMAL(18,4),
    settlement_currency VARCHAR(3),
    exchange_rate DECIMAL(18,10),
    total_charges DECIMAL(18,4),

    -- Dates
    creation_datetime TIMESTAMP,
    requested_execution_date DATE,
    value_date DATE,
    settlement_date DATE,
    completion_datetime TIMESTAMP,

    -- Timing (calculated)
    total_processing_time_ms BIGINT,
    sla_met BOOLEAN,

    -- Compliance
    sanctions_status VARCHAR(30),
    fraud_score DECIMAL(5,2),
    aml_risk_rating VARCHAR(20),
    pep_involved BOOLEAN,
    high_risk_country BOOLEAN,

    -- Regulatory
    ctr_eligible BOOLEAN DEFAULT FALSE,
    sar_filed BOOLEAN DEFAULT FALSE,
    ifti_eligible BOOLEAN DEFAULT FALSE,
    fatca_reportable BOOLEAN DEFAULT FALSE,
    crs_reportable BOOLEAN DEFAULT FALSE,
    ofac_blocked BOOLEAN DEFAULT FALSE,

    -- Remittance
    purpose VARCHAR(10),
    remittance_info TEXT,

    -- Quality
    dq_score DECIMAL(5,2),

    -- Partitioning
    partition_year INT NOT NULL,
    partition_month INT NOT NULL,
    region VARCHAR(20) NOT NULL,

    -- Refresh timestamp
    last_refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_anl_p360_e2e ON analytical.anl_payment_360(end_to_end_id);
CREATE INDEX IF NOT EXISTS idx_anl_p360_uetr ON analytical.anl_payment_360(uetr);
CREATE INDEX IF NOT EXISTS idx_anl_p360_debtor ON analytical.anl_payment_360(debtor_id);
CREATE INDEX IF NOT EXISTS idx_anl_p360_creditor ON analytical.anl_payment_360(creditor_id);
CREATE INDEX IF NOT EXISTS idx_anl_p360_status ON analytical.anl_payment_360(current_status);
CREATE INDEX IF NOT EXISTS idx_anl_p360_date ON analytical.anl_payment_360(creation_datetime);
CREATE INDEX IF NOT EXISTS idx_anl_p360_partition ON analytical.anl_payment_360(partition_year, partition_month, region);
CREATE INDEX IF NOT EXISTS idx_anl_p360_regulatory ON analytical.anl_payment_360(ctr_eligible, sar_filed, ifti_eligible);
CREATE INDEX IF NOT EXISTS idx_anl_p360_risk ON analytical.anl_payment_360(sanctions_status, aml_risk_rating);

-- =====================================================
-- ANL_PARTY_360 (Customer 360 view)
-- =====================================================
CREATE TABLE IF NOT EXISTS analytical.anl_party_360 (
    party_id VARCHAR(36) PRIMARY KEY,
    party_type VARCHAR(30) NOT NULL,
    name VARCHAR(200) NOT NULL,
    all_names TEXT[],

    -- Profile
    date_of_birth DATE,
    nationality VARCHAR(3)[],
    occupation VARCHAR(100),
    industry_code VARCHAR(20),
    pep_flag BOOLEAN,
    pep_category VARCHAR(50),

    -- Tax
    primary_tax_id VARCHAR(50),
    us_tax_status VARCHAR(30),
    fatca_classification VARCHAR(50),
    crs_reportable BOOLEAN,
    tax_residencies VARCHAR(3)[],

    -- Address
    primary_country VARCHAR(3),
    primary_address JSONB,

    -- Accounts (aggregated)
    total_accounts INT DEFAULT 0,
    active_accounts INT DEFAULT 0,
    accounts_summary JSONB,

    -- Payment Activity (aggregated)
    total_payments_sent BIGINT DEFAULT 0,
    total_amount_sent DECIMAL(22,4) DEFAULT 0,
    total_payments_received BIGINT DEFAULT 0,
    total_amount_received DECIMAL(22,4) DEFAULT 0,
    avg_payment_amount DECIMAL(18,4),
    last_payment_date DATE,
    first_payment_date DATE,

    -- Top Counterparties
    top_counterparties JSONB,

    -- Monthly Volume (last 12 months)
    monthly_volume JSONB,

    -- Risk
    risk_rating VARCHAR(20),
    risk_score DECIMAL(5,2),
    sanctions_status VARCHAR(30),
    aml_alerts_count INT DEFAULT 0,
    fraud_alerts_count INT DEFAULT 0,
    sar_filed_count INT DEFAULT 0,

    -- Compliance Flags
    ctr_eligible BOOLEAN DEFAULT FALSE,
    enhanced_due_diligence BOOLEAN DEFAULT FALSE,
    ofac_blocked BOOLEAN DEFAULT FALSE,

    -- KYC
    kyc_status VARCHAR(30),
    last_kyc_date DATE,
    next_kyc_due DATE,

    -- Quality
    dq_score DECIMAL(5,2),

    -- Metadata
    region VARCHAR(20),
    last_refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anl_party360_name ON analytical.anl_party_360(name);
CREATE INDEX IF NOT EXISTS idx_anl_party360_type ON analytical.anl_party_360(party_type);
CREATE INDEX IF NOT EXISTS idx_anl_party360_country ON analytical.anl_party_360(primary_country);
CREATE INDEX IF NOT EXISTS idx_anl_party360_risk ON analytical.anl_party_360(risk_rating);
CREATE INDEX IF NOT EXISTS idx_anl_party360_pep ON analytical.anl_party_360(pep_flag) WHERE pep_flag = TRUE;
CREATE INDEX IF NOT EXISTS idx_anl_party360_fatca ON analytical.anl_party_360(fatca_classification);

-- =====================================================
-- ANL_ACCOUNT_360
-- =====================================================
CREATE TABLE IF NOT EXISTS analytical.anl_account_360 (
    account_id VARCHAR(36) PRIMARY KEY,
    account_number VARCHAR(50) NOT NULL,
    iban VARCHAR(34),
    account_type VARCHAR(30) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status VARCHAR(20) NOT NULL,

    -- Owner (denormalized)
    owner_id VARCHAR(36),
    owner_name VARCHAR(200),
    owner_type VARCHAR(30),
    owner_country VARCHAR(3),

    -- Financial Institution
    fi_id VARCHAR(36),
    fi_name VARCHAR(200),
    fi_bic VARCHAR(11),
    fi_country VARCHAR(3),

    -- Activity (aggregated)
    total_debits_count BIGINT DEFAULT 0,
    total_debits_amount DECIMAL(22,4) DEFAULT 0,
    total_credits_count BIGINT DEFAULT 0,
    total_credits_amount DECIMAL(22,4) DEFAULT 0,
    avg_transaction_amount DECIMAL(18,4),
    last_transaction_date DATE,

    -- Monthly Activity
    monthly_activity JSONB,

    -- Risk
    risk_rating VARCHAR(20),
    sanctions_status VARCHAR(30),
    velocity_alerts INT DEFAULT 0,

    -- Tax
    fatca_status VARCHAR(30),
    crs_reportable BOOLEAN,

    -- Dates
    open_date DATE,
    close_date DATE,

    region VARCHAR(20),
    last_refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anl_acct360_number ON analytical.anl_account_360(account_number);
CREATE INDEX IF NOT EXISTS idx_anl_acct360_owner ON analytical.anl_account_360(owner_id);
CREATE INDEX IF NOT EXISTS idx_anl_acct360_fi ON analytical.anl_account_360(fi_id);

-- =====================================================
-- ANL_REGULATORY_READY (Pre-validated for reporting)
-- =====================================================
CREATE TABLE IF NOT EXISTS analytical.anl_regulatory_ready (
    payment_id VARCHAR(36) PRIMARY KEY,
    instruction_id VARCHAR(36),
    end_to_end_id VARCHAR(35),

    transaction_date DATE NOT NULL,
    amount DECIMAL(18,4) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    payment_type VARCHAR(50) NOT NULL,
    scheme_code VARCHAR(30) NOT NULL,

    -- Pre-formatted parties (regulatory format)
    ordering_party JSONB,
    beneficiary_party JSONB,
    ordering_institution JSONB,
    beneficiary_institution JSONB,

    -- Report Eligibility
    ctr_eligible BOOLEAN DEFAULT FALSE,
    sar_eligible BOOLEAN DEFAULT FALSE,
    ifti_eligible BOOLEAN DEFAULT FALSE,
    ttr_eligible BOOLEAN DEFAULT FALSE,
    smr_eligible BOOLEAN DEFAULT FALSE,
    fatca_eligible BOOLEAN DEFAULT FALSE,
    crs_eligible BOOLEAN DEFAULT FALSE,
    ofac_reportable BOOLEAN DEFAULT FALSE,
    psd2_fraud_reportable BOOLEAN DEFAULT FALSE,

    -- Converted Amounts
    amount_usd DECIMAL(18,4),
    amount_aud DECIMAL(18,4),
    amount_eur DECIMAL(18,4),
    amount_gbp DECIMAL(18,4),

    -- Risk
    overall_risk_score DECIMAL(5,2),
    fraud_score DECIMAL(5,2),
    aml_risk_rating VARCHAR(20),

    -- Flags
    cross_border BOOLEAN DEFAULT FALSE,
    cash_transaction BOOLEAN DEFAULT FALSE,
    pep_involved BOOLEAN DEFAULT FALSE,
    sanctions_hit BOOLEAN DEFAULT FALSE,
    structuring_indicator BOOLEAN DEFAULT FALSE,
    high_risk_country BOOLEAN DEFAULT FALSE,

    -- Countries
    origin_country VARCHAR(3),
    destination_country VARCHAR(3),

    -- Regulatory Fields
    regulatory_purpose_code VARCHAR(20),
    relationship_to_beneficiary VARCHAR(10),

    -- Report Status
    reports_generated JSONB,

    -- Validation
    last_validated_at TIMESTAMP,
    validation_passed BOOLEAN,
    validation_issues TEXT[],

    partition_year INT NOT NULL,
    partition_month INT NOT NULL,
    jurisdiction VARCHAR(10) NOT NULL,

    last_refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anl_rr_date ON analytical.anl_regulatory_ready(transaction_date);
CREATE INDEX IF NOT EXISTS idx_anl_rr_eligibility ON analytical.anl_regulatory_ready(ctr_eligible, sar_eligible, ifti_eligible);
CREATE INDEX IF NOT EXISTS idx_anl_rr_partition ON analytical.anl_regulatory_ready(partition_year, partition_month, jurisdiction);
CREATE INDEX IF NOT EXISTS idx_anl_rr_corridor ON analytical.anl_regulatory_ready(origin_country, destination_country);

-- =====================================================
-- ANL_DAILY_SUMMARY (Daily aggregated metrics)
-- =====================================================
CREATE TABLE IF NOT EXISTS analytical.anl_daily_summary (
    summary_date DATE NOT NULL,
    region VARCHAR(20) NOT NULL,
    payment_type VARCHAR(50) NOT NULL,
    scheme_code VARCHAR(30) NOT NULL,
    direction VARCHAR(20) NOT NULL,
    currency VARCHAR(3) NOT NULL,

    -- Volume
    total_count BIGINT NOT NULL,
    total_amount DECIMAL(22,4) NOT NULL,
    avg_amount DECIMAL(18,4),
    min_amount DECIMAL(18,4),
    max_amount DECIMAL(18,4),

    -- Status Breakdown
    completed_count BIGINT DEFAULT 0,
    failed_count BIGINT DEFAULT 0,
    returned_count BIGINT DEFAULT 0,
    pending_count BIGINT DEFAULT 0,

    -- Compliance
    ctr_count BIGINT DEFAULT 0,
    sar_count BIGINT DEFAULT 0,
    sanctions_hit_count BIGINT DEFAULT 0,
    fraud_alert_count BIGINT DEFAULT 0,

    -- Performance
    avg_processing_time_ms BIGINT,
    p95_processing_time_ms BIGINT,
    sla_breach_count BIGINT DEFAULT 0,

    -- Quality
    avg_dq_score DECIMAL(5,2),

    last_refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (summary_date, region, payment_type, scheme_code, direction, currency)
);

CREATE INDEX IF NOT EXISTS idx_anl_summary_date ON analytical.anl_daily_summary(summary_date);

-- =====================================================
-- ANL_CORRIDOR_METRICS (Cross-border analytics)
-- =====================================================
CREATE TABLE IF NOT EXISTS analytical.anl_corridor_metrics (
    metric_date DATE NOT NULL,
    origin_country VARCHAR(3) NOT NULL,
    destination_country VARCHAR(3) NOT NULL,
    currency VARCHAR(3) NOT NULL,

    transaction_count BIGINT NOT NULL,
    total_amount DECIMAL(22,4),
    total_amount_usd DECIMAL(22,4),
    avg_amount_usd DECIMAL(18,4),

    avg_completion_time_hours DECIMAL(10,2),
    success_rate DECIMAL(5,4),
    return_rate DECIMAL(5,4),

    avg_fx_rate DECIMAL(18,10),
    avg_fee_usd DECIMAL(10,4),

    avg_risk_score DECIMAL(5,2),
    high_risk_count BIGINT DEFAULT 0,

    last_refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (metric_date, origin_country, destination_country, currency)
);

CREATE INDEX IF NOT EXISTS idx_anl_corridor_date ON analytical.anl_corridor_metrics(metric_date);
CREATE INDEX IF NOT EXISTS idx_anl_corridor_countries ON analytical.anl_corridor_metrics(origin_country, destination_country);

-- =====================================================
-- ANL_FRAUD_FEATURES (Pre-computed for ML)
-- =====================================================
CREATE TABLE IF NOT EXISTS analytical.anl_fraud_features (
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(36) NOT NULL,
    feature_date DATE NOT NULL,

    -- Velocity Features
    txn_count_1h INT,
    txn_count_24h INT,
    txn_count_7d INT,
    txn_amount_1h DECIMAL(18,4),
    txn_amount_24h DECIMAL(18,4),
    txn_amount_7d DECIMAL(18,4),

    -- Behavioral Features
    avg_txn_amount_30d DECIMAL(18,4),
    std_txn_amount_30d DECIMAL(18,4),
    typical_txn_hour INT,
    unique_counterparties_7d INT,
    unique_countries_7d INT,

    -- Pattern Features
    structuring_score DECIMAL(5,2),
    round_tripping_score DECIMAL(5,2),
    layering_score DECIMAL(5,2),

    -- Composite
    composite_fraud_score DECIMAL(5,2),
    fraud_risk_tier VARCHAR(20),

    model_version VARCHAR(50),

    last_computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (entity_type, entity_id, feature_date)
);

CREATE INDEX IF NOT EXISTS idx_anl_fraud_entity ON analytical.anl_fraud_features(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_anl_fraud_score ON analytical.anl_fraud_features(composite_fraud_score);

-- Verify tables
SELECT 'analytical' as schema, table_name FROM information_schema.tables
WHERE table_schema = 'analytical' ORDER BY table_name;
