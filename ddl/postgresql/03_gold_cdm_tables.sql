-- GPS CDM - Gold Layer Tables (cdm_*)
-- ====================================
-- Layer 3: CDM Normalized - Unified canonical model
-- All message types from Silver converge here into single CDM entities.

-- =====================================================
-- CDM_PAYMENT_INSTRUCTION (Unified from all message types)
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_payment_instruction (
    -- Primary Key
    instruction_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    payment_id VARCHAR(36) NOT NULL,

    -- Standard Identifiers
    end_to_end_id VARCHAR(35),
    uetr VARCHAR(36),
    transaction_id VARCHAR(50),
    instruction_id_ext VARCHAR(50),
    message_id VARCHAR(50),
    related_reference VARCHAR(50),

    -- Source Classification
    source_message_type VARCHAR(50) NOT NULL,  -- pain.001, MT103, ACH, FEDWIRE, SEPA, RTP
    source_stg_table VARCHAR(50) NOT NULL,     -- stg_pain001, stg_mt103, etc.
    source_stg_id VARCHAR(36) NOT NULL,        -- FK to silver staging table

    -- Payment Classification
    payment_type VARCHAR(50) NOT NULL,
    scheme_code VARCHAR(30) NOT NULL,
    direction VARCHAR(20) NOT NULL,
    cross_border_flag BOOLEAN DEFAULT FALSE,
    priority VARCHAR(10) DEFAULT 'NORM',
    service_level VARCHAR(30),
    local_instrument VARCHAR(50),
    category_purpose VARCHAR(10),

    -- Parties (Foreign Keys to CDM entities)
    debtor_id VARCHAR(36),
    debtor_account_id VARCHAR(36),
    debtor_agent_id VARCHAR(36),
    creditor_id VARCHAR(36),
    creditor_account_id VARCHAR(36),
    creditor_agent_id VARCHAR(36),
    intermediary_agent1_id VARCHAR(36),
    intermediary_agent2_id VARCHAR(36),
    ultimate_debtor_id VARCHAR(36),
    ultimate_creditor_id VARCHAR(36),

    -- Amounts
    instructed_amount DECIMAL(18,4) NOT NULL,
    instructed_currency VARCHAR(3) NOT NULL,
    interbank_settlement_amount DECIMAL(18,4),
    interbank_settlement_currency VARCHAR(3),
    exchange_rate DECIMAL(18,10),
    exchange_rate_type VARCHAR(20),

    -- Dates
    creation_datetime TIMESTAMP,
    requested_execution_date DATE,
    value_date DATE,
    settlement_date DATE,
    acceptance_datetime TIMESTAMP,
    completion_datetime TIMESTAMP,

    -- Purpose & Remittance
    purpose VARCHAR(10),
    purpose_description VARCHAR(200),
    charge_bearer VARCHAR(10) DEFAULT 'SHAR',
    remittance_unstructured TEXT[],
    remittance_reference VARCHAR(140),
    remittance_structured JSONB,

    -- Status
    current_status VARCHAR(30) DEFAULT 'RECEIVED',
    status_reason_code VARCHAR(10),
    status_reason_description VARCHAR(200),

    -- Compliance (populated by screening/AML systems)
    sanctions_screening_status VARCHAR(30) DEFAULT 'NOT_SCREENED',
    sanctions_screening_timestamp TIMESTAMP,
    fraud_score DECIMAL(5,2),
    fraud_flags TEXT[],
    aml_risk_rating VARCHAR(20),
    pep_flag BOOLEAN DEFAULT FALSE,
    structuring_indicator BOOLEAN DEFAULT FALSE,
    high_risk_country_flag BOOLEAN DEFAULT FALSE,

    -- Regulatory Extensions (JSONB for flexibility)
    regulatory_extensions JSONB,

    -- Source Tracking
    source_system VARCHAR(100) NOT NULL,
    source_raw_id VARCHAR(36),

    -- Bi-temporal
    valid_from DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to DATE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,

    -- Data Quality
    data_quality_score DECIMAL(5,2),
    data_quality_issues TEXT[],

    -- Lineage
    lineage_batch_id VARCHAR(36),
    lineage_pipeline_run_id VARCHAR(100),

    -- Partitioning
    partition_year INT NOT NULL,
    partition_month INT NOT NULL,
    region VARCHAR(20) NOT NULL DEFAULT 'GLOBAL',

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) DEFAULT 'SYSTEM',
    record_version INT DEFAULT 1,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for cdm_payment_instruction
CREATE INDEX IF NOT EXISTS idx_cdm_pi_payment ON gold.cdm_payment_instruction(payment_id);
CREATE INDEX IF NOT EXISTS idx_cdm_pi_e2e ON gold.cdm_payment_instruction(end_to_end_id);
CREATE INDEX IF NOT EXISTS idx_cdm_pi_uetr ON gold.cdm_payment_instruction(uetr);
CREATE INDEX IF NOT EXISTS idx_cdm_pi_source ON gold.cdm_payment_instruction(source_message_type);
CREATE INDEX IF NOT EXISTS idx_cdm_pi_debtor ON gold.cdm_payment_instruction(debtor_id);
CREATE INDEX IF NOT EXISTS idx_cdm_pi_creditor ON gold.cdm_payment_instruction(creditor_id);
CREATE INDEX IF NOT EXISTS idx_cdm_pi_date ON gold.cdm_payment_instruction(requested_execution_date);
CREATE INDEX IF NOT EXISTS idx_cdm_pi_status ON gold.cdm_payment_instruction(current_status);
CREATE INDEX IF NOT EXISTS idx_cdm_pi_partition ON gold.cdm_payment_instruction(partition_year, partition_month, region);
CREATE INDEX IF NOT EXISTS idx_cdm_pi_batch ON gold.cdm_payment_instruction(lineage_batch_id);
CREATE INDEX IF NOT EXISTS idx_cdm_pi_stg ON gold.cdm_payment_instruction(source_stg_table, source_stg_id);

-- =====================================================
-- CDM_PARTY (Unified party entity)
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_party (
    party_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    party_type VARCHAR(30) NOT NULL,

    -- Core Identification
    name VARCHAR(200) NOT NULL,
    given_name VARCHAR(100),
    family_name VARCHAR(100),
    name_suffix VARCHAR(20),
    dba_name VARCHAR(200),

    -- Personal Details
    date_of_birth DATE,
    place_of_birth VARCHAR(100),
    city_of_birth VARCHAR(100),          -- CDM Enhancement v0.5
    country_of_birth VARCHAR(3),          -- CDM Enhancement v0.5
    nationality VARCHAR(3)[],

    -- Organization
    legal_entity_type VARCHAR(50),
    registration_number VARCHAR(50),
    registration_country VARCHAR(3),
    industry_code VARCHAR(20),
    bic VARCHAR(11),                      -- CDM Enhancement v0.5: Party BIC (for organizations)
    lei VARCHAR(20),                      -- CDM Enhancement v0.5: Legal Entity Identifier

    -- Tax (identifiers in cdm_party_identifiers; keep country context here)
    tax_id_country VARCHAR(3),            -- Country context for tax lookups

    -- FATCA
    us_tax_status VARCHAR(30),
    fatca_classification VARCHAR(50),
    fatca_giin VARCHAR(19),

    -- CRS
    crs_reportable BOOLEAN DEFAULT FALSE,
    crs_entity_type VARCHAR(50),
    tax_residencies JSONB,

    -- Identification (identifiers in cdm_party_identifiers; keep context fields here)
    identification_country VARCHAR(3),    -- Country context for any ID
    identification_expiry DATE,           -- Expiry context for any ID

    -- Address
    address_line1 VARCHAR(200),
    address_line2 VARCHAR(200),
    street_name VARCHAR(100),
    building_number VARCHAR(50),
    post_code VARCHAR(20),
    town_name VARCHAR(100),
    country_sub_division VARCHAR(50),
    country VARCHAR(3),
    country_of_residence VARCHAR(3),      -- CDM Enhancement v0.5: May differ from address country

    -- Ultimate Party References (stored on DEBTOR/CREDITOR parties)
    ultimate_debtor_bic VARCHAR(11),      -- CDM Enhancement v0.5: BIC of ultimate debtor
    ultimate_creditor_bic VARCHAR(11),    -- CDM Enhancement v0.5: BIC of ultimate creditor

    -- Contact
    email_address VARCHAR(254),
    phone_number VARCHAR(30),

    -- Risk/Compliance
    pep_flag BOOLEAN DEFAULT FALSE,
    pep_category VARCHAR(50),
    risk_rating VARCHAR(20),
    sanctions_screening_status VARCHAR(30) DEFAULT 'NOT_SCREENED',
    sanctions_list_match TEXT[],

    -- Source
    source_system VARCHAR(100) NOT NULL,
    source_message_type VARCHAR(50),
    source_stg_id VARCHAR(36),
    source_instruction_id VARCHAR(36),  -- References payment instruction that created this entity

    -- Bi-temporal
    valid_from DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to DATE,
    is_current BOOLEAN DEFAULT TRUE,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    record_version INT DEFAULT 1,
    is_deleted BOOLEAN DEFAULT FALSE,

    -- Partitioning
    region VARCHAR(20) DEFAULT 'GLOBAL'
);

CREATE INDEX IF NOT EXISTS idx_cdm_party_name ON gold.cdm_party(name);
CREATE INDEX IF NOT EXISTS idx_cdm_party_src_instr ON gold.cdm_party(source_instruction_id);
CREATE INDEX IF NOT EXISTS idx_cdm_party_type ON gold.cdm_party(party_type);
CREATE INDEX IF NOT EXISTS idx_cdm_party_tax_country ON gold.cdm_party(tax_id_country);
CREATE INDEX IF NOT EXISTS idx_cdm_party_country ON gold.cdm_party(country);
CREATE INDEX IF NOT EXISTS idx_cdm_party_pep ON gold.cdm_party(pep_flag) WHERE pep_flag = TRUE;
CREATE INDEX IF NOT EXISTS idx_cdm_party_fatca ON gold.cdm_party(fatca_classification);
CREATE INDEX IF NOT EXISTS idx_cdm_party_crs ON gold.cdm_party(crs_reportable) WHERE crs_reportable = TRUE;
CREATE INDEX IF NOT EXISTS idx_cdm_party_bic ON gold.cdm_party(bic);  -- CDM Enhancement v0.5
CREATE INDEX IF NOT EXISTS idx_cdm_party_lei ON gold.cdm_party(lei);  -- CDM Enhancement v0.5

-- =====================================================
-- CDM_ACCOUNT
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_account (
    account_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    account_number VARCHAR(50) NOT NULL,
    iban VARCHAR(34),
    account_name VARCHAR(200),            -- CDM Enhancement v0.5: Account holder name/label
    account_type VARCHAR(30) NOT NULL,
    currency VARCHAR(3) NOT NULL,

    owner_id VARCHAR(36),
    financial_institution_id VARCHAR(36),
    branch_id VARCHAR(50),

    account_status VARCHAR(20) NOT NULL,
    open_date DATE,
    close_date DATE,

    -- FATCA/CRS
    fatca_status VARCHAR(30),
    crs_reportable_account BOOLEAN DEFAULT FALSE,
    controlling_persons JSONB,

    -- Risk
    sanctions_screening_status VARCHAR(30) DEFAULT 'NOT_SCREENED',
    risk_rating VARCHAR(20),

    -- Source
    source_system VARCHAR(100) NOT NULL,
    source_message_type VARCHAR(50),
    source_stg_id VARCHAR(36),
    source_instruction_id VARCHAR(36),  -- References payment instruction that created this entity

    -- Bi-temporal
    valid_from DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to DATE,
    is_current BOOLEAN DEFAULT TRUE,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    record_version INT DEFAULT 1,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_cdm_account_number ON gold.cdm_account(account_number);
CREATE INDEX IF NOT EXISTS idx_cdm_account_src_instr ON gold.cdm_account(source_instruction_id);
CREATE INDEX IF NOT EXISTS idx_cdm_account_iban ON gold.cdm_account(iban);
CREATE INDEX IF NOT EXISTS idx_cdm_account_owner ON gold.cdm_account(owner_id);
CREATE INDEX IF NOT EXISTS idx_cdm_account_fi ON gold.cdm_account(financial_institution_id);

-- =====================================================
-- CDM_FINANCIAL_INSTITUTION
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_financial_institution (
    fi_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    institution_name VARCHAR(200) NOT NULL,
    short_name VARCHAR(50),
    bic VARCHAR(11),
    lei VARCHAR(20),
    national_clearing_code VARCHAR(30),
    national_clearing_system VARCHAR(30),

    -- FinCEN
    rssd_number VARCHAR(20),
    fi_type VARCHAR(50),

    -- FATCA
    fatca_giin VARCHAR(19),
    fatca_status VARCHAR(30),

    -- Address
    address_line1 VARCHAR(200),
    post_code VARCHAR(20),
    town_name VARCHAR(100),
    country VARCHAR(3) NOT NULL,

    -- Branch
    branch_identification VARCHAR(50),
    branch_name VARCHAR(200),
    is_branch BOOLEAN DEFAULT FALSE,
    parent_fi_id VARCHAR(36),

    -- Source
    source_system VARCHAR(100) NOT NULL,
    source_instruction_id VARCHAR(36),  -- References payment instruction that created this entity

    -- Bi-temporal
    valid_from DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to DATE,
    is_current BOOLEAN DEFAULT TRUE,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    record_version INT DEFAULT 1,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_cdm_fi_bic ON gold.cdm_financial_institution(bic);
CREATE INDEX IF NOT EXISTS idx_cdm_fi_src_instr ON gold.cdm_financial_institution(source_instruction_id);
CREATE INDEX IF NOT EXISTS idx_cdm_fi_lei ON gold.cdm_financial_institution(lei);
CREATE INDEX IF NOT EXISTS idx_cdm_fi_clearing ON gold.cdm_financial_institution(national_clearing_code, national_clearing_system);
CREATE INDEX IF NOT EXISTS idx_cdm_fi_country ON gold.cdm_financial_institution(country);

-- =====================================================
-- CDM_SETTLEMENT
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_settlement (
    settlement_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    payment_id VARCHAR(36) NOT NULL,

    settlement_date DATE NOT NULL,
    settlement_amount DECIMAL(18,4) NOT NULL,
    settlement_currency VARCHAR(3) NOT NULL,
    settlement_method VARCHAR(50) NOT NULL,
    settlement_status VARCHAR(30) NOT NULL,

    clearing_system_code VARCHAR(30),
    settlement_cycle VARCHAR(20),

    interbank_settlement_date DATE,
    interbank_settlement_amount DECIMAL(18,4),
    interbank_settlement_currency VARCHAR(3),

    settlement_account_id VARCHAR(36),
    settlement_reference VARCHAR(100),

    batch_id VARCHAR(36),
    netting_indicator BOOLEAN DEFAULT FALSE,

    source_system VARCHAR(100) NOT NULL,

    partition_year INT NOT NULL,
    partition_month INT NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    record_version INT DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_cdm_settlement_payment ON gold.cdm_settlement(payment_id);
CREATE INDEX IF NOT EXISTS idx_cdm_settlement_date ON gold.cdm_settlement(settlement_date);
CREATE INDEX IF NOT EXISTS idx_cdm_settlement_status ON gold.cdm_settlement(settlement_status);

-- =====================================================
-- CDM_CHARGE
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_charge (
    charge_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    payment_id VARCHAR(36) NOT NULL,

    charge_type VARCHAR(50) NOT NULL,
    charge_bearer VARCHAR(10),
    amount DECIMAL(18,4) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    agent_id VARCHAR(36),

    charge_reason VARCHAR(200),
    charge_date DATE,

    source_system VARCHAR(100) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    record_version INT DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_cdm_charge_payment ON gold.cdm_charge(payment_id);

-- =====================================================
-- CDM_PAYMENT_EVENT (Lifecycle tracking)
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_payment_event (
    event_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    payment_id VARCHAR(36) NOT NULL,
    instruction_id VARCHAR(36),

    event_type VARCHAR(50) NOT NULL,           -- CREATED, VALIDATED, SCREENED, CLEARED, SETTLED, etc.
    event_timestamp TIMESTAMP NOT NULL,

    previous_status VARCHAR(30),
    new_status VARCHAR(30),

    actor VARCHAR(100),
    actor_type VARCHAR(30),

    details JSONB,

    source_system VARCHAR(100),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cdm_event_payment ON gold.cdm_payment_event(payment_id);
CREATE INDEX IF NOT EXISTS idx_cdm_event_type ON gold.cdm_payment_event(event_type);
CREATE INDEX IF NOT EXISTS idx_cdm_event_time ON gold.cdm_payment_event(event_timestamp);

-- Verify tables
SELECT 'gold' as schema, table_name FROM information_schema.tables
WHERE table_schema = 'gold' ORDER BY table_name;
