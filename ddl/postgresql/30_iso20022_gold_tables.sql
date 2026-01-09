-- GPS CDM - ISO 20022 Semantic Gold Tables
-- ==========================================
-- Each ISO 20022 message type maps to a dedicated Gold table with semantic naming.
-- Proprietary formats (MT103, FEDWIRE, ACH, etc.) map to their ISO equivalent table.
--
-- Table Naming Convention: cdm_{category}_{message_purpose}
--   - category: pain, pacs, camt
--   - message_purpose: semantic description of the message
--
-- Version: 1.0
-- Date: 2026-01-08

-- =====================================================
-- 1. cdm_pain_customer_credit_transfer_initiation (pain.001)
-- =====================================================
-- Purpose: Customer → Bank: "Please send this payment"
-- Formats: pain.001, SEPA_pain001
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_pain_customer_credit_transfer_initiation (
    -- Primary Key
    initiation_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,  -- pain.001, SEPA_pain001, etc.

    -- Message Identification
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,

    -- Initiating Party
    initiating_party_name VARCHAR(140),
    initiating_party_id VARCHAR(35),
    initiating_party_id_type VARCHAR(35),

    -- Payment Information (header level)
    payment_info_id VARCHAR(35),
    payment_method VARCHAR(3),  -- TRF, CHK, TRA
    batch_booking BOOLEAN,
    number_of_transactions INT,
    control_sum DECIMAL(18,4),
    requested_execution_date DATE,

    -- Service Level
    service_level_code VARCHAR(4),
    local_instrument_code VARCHAR(35),
    category_purpose_code VARCHAR(4),

    -- Debtor (Payer)
    debtor_name VARCHAR(140),
    debtor_address_street VARCHAR(70),
    debtor_address_building VARCHAR(16),
    debtor_address_postal_code VARCHAR(16),
    debtor_address_town VARCHAR(35),
    debtor_address_country VARCHAR(2),
    debtor_id VARCHAR(35),
    debtor_id_type VARCHAR(35),

    -- Debtor Account
    debtor_account_iban VARCHAR(34),
    debtor_account_other VARCHAR(34),
    debtor_account_currency VARCHAR(3),

    -- Debtor Agent (Bank)
    debtor_agent_bic VARCHAR(11),
    debtor_agent_name VARCHAR(140),
    debtor_agent_clearing_system_id VARCHAR(35),

    -- Transaction Details
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35),
    instructed_amount DECIMAL(18,4),
    instructed_currency VARCHAR(3),
    equivalent_amount DECIMAL(18,4),
    equivalent_currency VARCHAR(3),
    exchange_rate DECIMAL(18,10),
    charge_bearer VARCHAR(4),

    -- Creditor Agent (Bank)
    creditor_agent_bic VARCHAR(11),
    creditor_agent_name VARCHAR(140),
    creditor_agent_clearing_system_id VARCHAR(35),

    -- Creditor (Payee)
    creditor_name VARCHAR(140),
    creditor_address_street VARCHAR(70),
    creditor_address_building VARCHAR(16),
    creditor_address_postal_code VARCHAR(16),
    creditor_address_town VARCHAR(35),
    creditor_address_country VARCHAR(2),
    creditor_id VARCHAR(35),
    creditor_id_type VARCHAR(35),

    -- Creditor Account
    creditor_account_iban VARCHAR(34),
    creditor_account_other VARCHAR(34),
    creditor_account_currency VARCHAR(3),

    -- Ultimate Parties (optional)
    ultimate_debtor_name VARCHAR(140),
    ultimate_debtor_id VARCHAR(35),
    ultimate_creditor_name VARCHAR(140),
    ultimate_creditor_id VARCHAR(35),

    -- Remittance
    remittance_unstructured TEXT[],
    remittance_structured JSONB,
    purpose_code VARCHAR(4),
    purpose_proprietary VARCHAR(35),

    -- Regulatory
    regulatory_reporting JSONB,

    -- Supplementary (format-specific fields)
    supplementary_data JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);

CREATE INDEX IF NOT EXISTS idx_pain_cti_stg_id ON gold.cdm_pain_customer_credit_transfer_initiation(source_stg_id);
CREATE INDEX IF NOT EXISTS idx_pain_cti_msg_id ON gold.cdm_pain_customer_credit_transfer_initiation(message_id);
CREATE INDEX IF NOT EXISTS idx_pain_cti_e2e_id ON gold.cdm_pain_customer_credit_transfer_initiation(end_to_end_id);
CREATE INDEX IF NOT EXISTS idx_pain_cti_format ON gold.cdm_pain_customer_credit_transfer_initiation(source_format);
CREATE INDEX IF NOT EXISTS idx_pain_cti_batch ON gold.cdm_pain_customer_credit_transfer_initiation(_batch_id);


-- =====================================================
-- 2. cdm_pain_customer_direct_debit_initiation (pain.008)
-- =====================================================
-- Purpose: Customer → Bank: "Please collect money from this debtor"
-- Formats: pain.008, SEPA_pain008, SEPA SDD
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_pain_customer_direct_debit_initiation (
    -- Primary Key
    initiation_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,

    -- Message Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,
    number_of_transactions INT,
    control_sum DECIMAL(18,4),

    -- Initiating Party
    initiating_party_name VARCHAR(140),
    initiating_party_id VARCHAR(35),

    -- Payment Information
    payment_info_id VARCHAR(35),
    payment_method VARCHAR(3),  -- DD
    batch_booking BOOLEAN,
    service_level_code VARCHAR(4),
    local_instrument_code VARCHAR(35),  -- CORE, B2B, COR1
    sequence_type VARCHAR(4),  -- FRST, RCUR, FNAL, OOFF
    category_purpose_code VARCHAR(4),
    requested_collection_date DATE,

    -- Creditor (Collecting Party)
    creditor_name VARCHAR(140),
    creditor_address_street VARCHAR(70),
    creditor_address_postal_code VARCHAR(16),
    creditor_address_town VARCHAR(35),
    creditor_address_country VARCHAR(2),
    creditor_id VARCHAR(35),  -- Creditor Scheme ID
    creditor_id_type VARCHAR(35),

    -- Creditor Account
    creditor_account_iban VARCHAR(34),
    creditor_account_other VARCHAR(35),
    creditor_account_currency VARCHAR(3),

    -- Creditor Agent
    creditor_agent_bic VARCHAR(11),
    creditor_agent_clearing_system_id VARCHAR(35),
    creditor_agent_name VARCHAR(140),

    -- Direct Debit Transaction
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35),
    instructed_amount DECIMAL(18,4),
    instructed_currency VARCHAR(3),
    charge_bearer VARCHAR(4),

    -- Mandate Information
    mandate_id VARCHAR(35),
    mandate_date_of_signature DATE,
    amendment_indicator BOOLEAN,
    amendment_info JSONB,

    -- Debtor Agent (Bank being debited)
    debtor_agent_bic VARCHAR(11),
    debtor_agent_clearing_system_id VARCHAR(35),
    debtor_agent_name VARCHAR(140),

    -- Debtor (Party being debited)
    debtor_name VARCHAR(140),
    debtor_address_street VARCHAR(70),
    debtor_address_postal_code VARCHAR(16),
    debtor_address_town VARCHAR(35),
    debtor_address_country VARCHAR(2),
    debtor_id VARCHAR(35),

    -- Debtor Account
    debtor_account_iban VARCHAR(34),
    debtor_account_other VARCHAR(35),

    -- Ultimate Parties
    ultimate_debtor_name VARCHAR(140),
    ultimate_creditor_name VARCHAR(140),

    -- Remittance
    remittance_unstructured TEXT[],
    remittance_structured_reference VARCHAR(35),
    purpose_code VARCHAR(4),

    -- Supplementary
    supplementary_data JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);

CREATE INDEX IF NOT EXISTS idx_pain_ddi_stg_id ON gold.cdm_pain_customer_direct_debit_initiation(source_stg_id);
CREATE INDEX IF NOT EXISTS idx_pain_ddi_msg_id ON gold.cdm_pain_customer_direct_debit_initiation(message_id);
CREATE INDEX IF NOT EXISTS idx_pain_ddi_mandate ON gold.cdm_pain_customer_direct_debit_initiation(mandate_id);
CREATE INDEX IF NOT EXISTS idx_pain_ddi_format ON gold.cdm_pain_customer_direct_debit_initiation(source_format);


-- =====================================================
-- 3. cdm_pain_customer_payment_status_report (pain.002)
-- =====================================================
-- Purpose: Bank → Customer: Payment status report
-- Formats: pain.002
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_pain_customer_payment_status_report (
    -- Primary Key
    status_report_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,

    -- Message Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,

    -- Original Message Reference
    original_message_id VARCHAR(35),
    original_message_name_id VARCHAR(35),
    original_creation_datetime TIMESTAMP,
    original_number_of_transactions INT,

    -- Group Status
    group_status VARCHAR(4),  -- ACCP, ACTC, ACSP, RJCT, etc.
    group_status_reason_code VARCHAR(4),
    group_status_reason_info TEXT,

    -- Transaction Status
    status_id VARCHAR(35),
    original_payment_info_id VARCHAR(35),
    original_instruction_id VARCHAR(35),
    original_end_to_end_id VARCHAR(35),
    transaction_status VARCHAR(4),
    status_reason_code VARCHAR(4),
    status_reason_info TEXT,

    -- Original Transaction Reference
    original_instructed_amount DECIMAL(18,4),
    original_instructed_currency VARCHAR(3),
    original_requested_execution_date DATE,

    -- Supplementary
    supplementary_data JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);

CREATE INDEX IF NOT EXISTS idx_pain_psr_stg_id ON gold.cdm_pain_customer_payment_status_report(source_stg_id);
CREATE INDEX IF NOT EXISTS idx_pain_psr_orig_msg ON gold.cdm_pain_customer_payment_status_report(original_message_id);


-- =====================================================
-- 4. cdm_pacs_fi_customer_credit_transfer (pacs.008)
-- =====================================================
-- Purpose: Bank → Bank: Interbank customer credit transfer
-- Formats: pacs.008, MT103, FEDWIRE, CHIPS, ACH, CHAPS, FPS, BACS,
--          FEDNOW, RTP, NPP, SEPA, MEPS_PLUS, RTGS_HK, UAEFTS,
--          INSTAPAY, PIX, UPI, PROMPTPAY, PAYNOW, and all *_pacs008 variants
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_pacs_fi_customer_credit_transfer (
    -- Primary Key
    transfer_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,

    -- Group Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,
    number_of_transactions INT,
    total_interbank_settlement_amount DECIMAL(18,4),
    total_interbank_settlement_currency VARCHAR(3),
    settlement_method VARCHAR(4),  -- INDA, INGA, COVE, CLRG
    clearing_system_code VARCHAR(35),
    clearing_system_proprietary VARCHAR(35),

    -- Instructing/Instructed Agents (message level)
    instructing_agent_bic VARCHAR(11),
    instructing_agent_lei VARCHAR(20),
    instructing_agent_clearing_id VARCHAR(35),
    instructing_agent_name VARCHAR(140),
    instructing_agent_country VARCHAR(2),
    instructed_agent_bic VARCHAR(11),
    instructed_agent_lei VARCHAR(20),
    instructed_agent_clearing_id VARCHAR(35),
    instructed_agent_name VARCHAR(140),
    instructed_agent_country VARCHAR(2),

    -- Payment Identification
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35),
    uetr VARCHAR(36),  -- Unique End-to-end Transaction Reference
    transaction_id VARCHAR(35),
    clearing_system_reference VARCHAR(35),

    -- Payment Type
    instruction_priority VARCHAR(4),
    service_level_code VARCHAR(4),
    service_level_proprietary VARCHAR(35),
    local_instrument_code VARCHAR(35),
    local_instrument_proprietary VARCHAR(35),
    category_purpose_code VARCHAR(4),
    category_purpose_proprietary VARCHAR(35),

    -- Settlement
    interbank_settlement_amount DECIMAL(18,4),
    interbank_settlement_currency VARCHAR(3),
    interbank_settlement_date DATE,
    instructed_amount DECIMAL(18,4),
    instructed_currency VARCHAR(3),
    exchange_rate DECIMAL(18,10),

    -- Charges
    charge_bearer VARCHAR(4),
    charges_amount DECIMAL(18,4),
    charges_currency VARCHAR(3),
    charges_agent_bic VARCHAR(11),

    -- Debtor (Payer - Customer)
    debtor_name VARCHAR(140),
    debtor_address_street VARCHAR(70),
    debtor_address_building VARCHAR(16),
    debtor_address_postal_code VARCHAR(16),
    debtor_address_town VARCHAR(35),
    debtor_address_country_subdivision VARCHAR(35),
    debtor_address_country VARCHAR(2),
    debtor_address_lines TEXT[],
    debtor_id_org_bic VARCHAR(11),
    debtor_id_org_lei VARCHAR(20),
    debtor_id_org_other VARCHAR(35),
    debtor_id_org_other_scheme VARCHAR(35),
    debtor_id_private_other VARCHAR(35),
    debtor_id_private_birth_date DATE,
    debtor_id_private_birth_country VARCHAR(2),

    -- Debtor Account
    debtor_account_iban VARCHAR(34),
    debtor_account_other VARCHAR(34),
    debtor_account_other_scheme VARCHAR(35),
    debtor_account_type VARCHAR(4),
    debtor_account_currency VARCHAR(3),
    debtor_account_name VARCHAR(70),
    debtor_account_proxy_type VARCHAR(4),
    debtor_account_proxy_id VARCHAR(256),

    -- Debtor Agent (Debtor's Bank)
    debtor_agent_bic VARCHAR(11),
    debtor_agent_lei VARCHAR(20),
    debtor_agent_clearing_id VARCHAR(35),
    debtor_agent_clearing_system VARCHAR(5),
    debtor_agent_name VARCHAR(140),
    debtor_agent_address_street VARCHAR(70),
    debtor_agent_address_town VARCHAR(35),
    debtor_agent_address_country VARCHAR(2),
    debtor_agent_branch_id VARCHAR(35),

    -- Creditor Agent (Creditor's Bank)
    creditor_agent_bic VARCHAR(11),
    creditor_agent_lei VARCHAR(20),
    creditor_agent_clearing_id VARCHAR(35),
    creditor_agent_clearing_system VARCHAR(5),
    creditor_agent_name VARCHAR(140),
    creditor_agent_address_street VARCHAR(70),
    creditor_agent_address_town VARCHAR(35),
    creditor_agent_address_country VARCHAR(2),
    creditor_agent_branch_id VARCHAR(35),

    -- Creditor (Payee - Customer)
    creditor_name VARCHAR(140),
    creditor_address_street VARCHAR(70),
    creditor_address_building VARCHAR(16),
    creditor_address_postal_code VARCHAR(16),
    creditor_address_town VARCHAR(35),
    creditor_address_country_subdivision VARCHAR(35),
    creditor_address_country VARCHAR(2),
    creditor_address_lines TEXT[],
    creditor_id_org_bic VARCHAR(11),
    creditor_id_org_lei VARCHAR(20),
    creditor_id_org_other VARCHAR(35),
    creditor_id_org_other_scheme VARCHAR(35),
    creditor_id_private_other VARCHAR(35),
    creditor_id_private_birth_date DATE,
    creditor_id_private_birth_country VARCHAR(2),

    -- Creditor Account
    creditor_account_iban VARCHAR(34),
    creditor_account_other VARCHAR(34),
    creditor_account_other_scheme VARCHAR(35),
    creditor_account_type VARCHAR(4),
    creditor_account_currency VARCHAR(3),
    creditor_account_name VARCHAR(70),
    creditor_account_proxy_type VARCHAR(4),
    creditor_account_proxy_id VARCHAR(256),

    -- Intermediary Agents
    intermediary_agent1_bic VARCHAR(11),
    intermediary_agent1_lei VARCHAR(20),
    intermediary_agent1_clearing_id VARCHAR(35),
    intermediary_agent1_name VARCHAR(140),
    intermediary_agent1_country VARCHAR(2),
    intermediary_agent1_account VARCHAR(34),
    intermediary_agent2_bic VARCHAR(11),
    intermediary_agent2_lei VARCHAR(20),
    intermediary_agent2_clearing_id VARCHAR(35),
    intermediary_agent2_name VARCHAR(140),
    intermediary_agent2_country VARCHAR(2),
    intermediary_agent2_account VARCHAR(34),
    intermediary_agent3_bic VARCHAR(11),
    intermediary_agent3_clearing_id VARCHAR(35),
    intermediary_agent3_country VARCHAR(2),

    -- Ultimate Parties
    ultimate_debtor_name VARCHAR(140),
    ultimate_debtor_address_country VARCHAR(2),
    ultimate_debtor_id VARCHAR(35),
    ultimate_creditor_name VARCHAR(140),
    ultimate_creditor_address_country VARCHAR(2),
    ultimate_creditor_id VARCHAR(35),

    -- Remittance
    remittance_unstructured TEXT[],
    remittance_structured JSONB,
    purpose_code VARCHAR(4),
    purpose_proprietary VARCHAR(35),

    -- Regulatory & Tax
    regulatory_reporting JSONB,
    tax_information JSONB,

    -- Supplementary (format-specific fields)
    supplementary_data JSONB,
    scheme_identifiers JSONB,  -- {"fedwire_imad": "...", "chips_ssn": "..."}

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);

CREATE INDEX IF NOT EXISTS idx_pacs_cct_stg_id ON gold.cdm_pacs_fi_customer_credit_transfer(source_stg_id);
CREATE INDEX IF NOT EXISTS idx_pacs_cct_msg_id ON gold.cdm_pacs_fi_customer_credit_transfer(message_id);
CREATE INDEX IF NOT EXISTS idx_pacs_cct_e2e_id ON gold.cdm_pacs_fi_customer_credit_transfer(end_to_end_id);
CREATE INDEX IF NOT EXISTS idx_pacs_cct_uetr ON gold.cdm_pacs_fi_customer_credit_transfer(uetr);
CREATE INDEX IF NOT EXISTS idx_pacs_cct_format ON gold.cdm_pacs_fi_customer_credit_transfer(source_format);
CREATE INDEX IF NOT EXISTS idx_pacs_cct_sttlm_dt ON gold.cdm_pacs_fi_customer_credit_transfer(interbank_settlement_date);
CREATE INDEX IF NOT EXISTS idx_pacs_cct_batch ON gold.cdm_pacs_fi_customer_credit_transfer(_batch_id);
CREATE INDEX IF NOT EXISTS idx_pacs_cct_dbtr_agt ON gold.cdm_pacs_fi_customer_credit_transfer(debtor_agent_bic);
CREATE INDEX IF NOT EXISTS idx_pacs_cct_cdtr_agt ON gold.cdm_pacs_fi_customer_credit_transfer(creditor_agent_bic);


-- =====================================================
-- 5. cdm_pacs_fi_credit_transfer (pacs.009)
-- =====================================================
-- Purpose: Bank → Bank: Bank's own funds transfer (not customer funds)
-- Formats: pacs.009, MT202, MT202COV, TARGET2, and all *_pacs009 variants
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_pacs_fi_credit_transfer (
    -- Primary Key
    transfer_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,

    -- Group Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,
    number_of_transactions INT,
    total_settlement_amount DECIMAL(18,4),
    total_settlement_currency VARCHAR(3),
    settlement_method VARCHAR(4),
    clearing_system_code VARCHAR(35),
    clearing_system_proprietary VARCHAR(35),

    -- Instructing/Instructed Agents (message level)
    instructing_agent_bic VARCHAR(11),
    instructing_agent_lei VARCHAR(20),
    instructing_agent_clearing_id VARCHAR(35),
    instructing_agent_name VARCHAR(140),
    instructed_agent_bic VARCHAR(11),
    instructed_agent_lei VARCHAR(20),
    instructed_agent_clearing_id VARCHAR(35),
    instructed_agent_name VARCHAR(140),

    -- Payment Identification
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35),
    uetr VARCHAR(36),
    transaction_id VARCHAR(35),
    clearing_system_reference VARCHAR(35),

    -- Payment Type
    instruction_priority VARCHAR(4),
    service_level_code VARCHAR(4),
    service_level_proprietary VARCHAR(35),
    local_instrument_code VARCHAR(35),

    -- Settlement
    interbank_settlement_amount DECIMAL(18,4),
    interbank_settlement_currency VARCHAR(3),
    interbank_settlement_date DATE,

    -- Debtor Agent (Sending FI - owns the funds)
    debtor_agent_bic VARCHAR(11),
    debtor_agent_lei VARCHAR(20),
    debtor_agent_clearing_id VARCHAR(35),
    debtor_agent_clearing_system VARCHAR(5),
    debtor_agent_name VARCHAR(140),
    debtor_agent_address_street VARCHAR(70),
    debtor_agent_address_town VARCHAR(35),
    debtor_agent_address_country VARCHAR(2),
    debtor_agent_account_iban VARCHAR(34),
    debtor_agent_account_other VARCHAR(34),
    debtor_agent_account_currency VARCHAR(3),

    -- Creditor Agent (Receiving FI - receives the funds)
    creditor_agent_bic VARCHAR(11),
    creditor_agent_lei VARCHAR(20),
    creditor_agent_clearing_id VARCHAR(35),
    creditor_agent_clearing_system VARCHAR(5),
    creditor_agent_name VARCHAR(140),
    creditor_agent_address_street VARCHAR(70),
    creditor_agent_address_town VARCHAR(35),
    creditor_agent_address_country VARCHAR(2),
    creditor_agent_account_iban VARCHAR(34),
    creditor_agent_account_other VARCHAR(34),
    creditor_agent_account_currency VARCHAR(3),

    -- Intermediary Agents
    intermediary_agent1_bic VARCHAR(11),
    intermediary_agent1_lei VARCHAR(20),
    intermediary_agent1_clearing_id VARCHAR(35),
    intermediary_agent1_country VARCHAR(2),
    intermediary_agent1_account VARCHAR(34),
    intermediary_agent2_bic VARCHAR(11),
    intermediary_agent2_clearing_id VARCHAR(35),
    intermediary_agent2_country VARCHAR(2),
    intermediary_agent2_account VARCHAR(34),

    -- Underlying Customer Credit Transfer (for cover payments)
    underlying_customer_transfer JSONB,

    -- Remittance & Purpose
    remittance_unstructured TEXT[],
    purpose_code VARCHAR(4),
    purpose_proprietary VARCHAR(35),

    -- Supplementary
    supplementary_data JSONB,
    scheme_identifiers JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);

CREATE INDEX IF NOT EXISTS idx_pacs_fct_stg_id ON gold.cdm_pacs_fi_credit_transfer(source_stg_id);
CREATE INDEX IF NOT EXISTS idx_pacs_fct_msg_id ON gold.cdm_pacs_fi_credit_transfer(message_id);
CREATE INDEX IF NOT EXISTS idx_pacs_fct_e2e_id ON gold.cdm_pacs_fi_credit_transfer(end_to_end_id);
CREATE INDEX IF NOT EXISTS idx_pacs_fct_uetr ON gold.cdm_pacs_fi_credit_transfer(uetr);
CREATE INDEX IF NOT EXISTS idx_pacs_fct_format ON gold.cdm_pacs_fi_credit_transfer(source_format);
CREATE INDEX IF NOT EXISTS idx_pacs_fct_sttlm_dt ON gold.cdm_pacs_fi_credit_transfer(interbank_settlement_date);


-- =====================================================
-- 6. cdm_pacs_fi_payment_status_report (pacs.002)
-- =====================================================
-- Purpose: Bank → Bank: Status report on a previous payment
-- Formats: pacs.002, and all *_pacs002 variants
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_pacs_fi_payment_status_report (
    -- Primary Key
    status_report_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,

    -- Message Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,

    -- Original Group Information
    original_message_id VARCHAR(35),
    original_message_name_id VARCHAR(35),
    original_creation_datetime TIMESTAMP,
    original_number_of_transactions INT,

    -- Group Status (if applicable)
    group_status VARCHAR(4),  -- ACCP, ACTC, ACSP, ACWC, PART, PDNG, RCVD, RJCT
    group_status_reason_code VARCHAR(4),
    group_status_reason_proprietary VARCHAR(35),
    group_status_reason_info TEXT,

    -- Transaction Status
    status_id VARCHAR(35),
    original_instruction_id VARCHAR(35),
    original_end_to_end_id VARCHAR(35),
    original_transaction_id VARCHAR(35),
    original_uetr VARCHAR(36),
    transaction_status VARCHAR(4),  -- ACCP, ACTC, ACSP, ACWC, PART, PDNG, RCVD, RJCT
    status_reason_code VARCHAR(4),
    status_reason_proprietary VARCHAR(35),
    status_reason_info TEXT,
    acceptance_datetime TIMESTAMP,
    effective_settlement_date DATE,
    account_servicer_reference VARCHAR(35),
    clearing_system_reference VARCHAR(35),

    -- Original Transaction Reference (partial copy)
    original_settlement_amount DECIMAL(18,4),
    original_settlement_currency VARCHAR(3),
    original_settlement_date DATE,
    original_requested_execution_date DATE,

    -- Original Parties (summary)
    original_debtor_name VARCHAR(140),
    original_debtor_account_iban VARCHAR(34),
    original_debtor_account_other VARCHAR(35),
    original_debtor_agent_bic VARCHAR(11),
    original_creditor_name VARCHAR(140),
    original_creditor_account_iban VARCHAR(34),
    original_creditor_account_other VARCHAR(35),
    original_creditor_agent_bic VARCHAR(11),

    -- Supplementary
    supplementary_data JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);

CREATE INDEX IF NOT EXISTS idx_pacs_psr_stg_id ON gold.cdm_pacs_fi_payment_status_report(source_stg_id);
CREATE INDEX IF NOT EXISTS idx_pacs_psr_msg_id ON gold.cdm_pacs_fi_payment_status_report(message_id);
CREATE INDEX IF NOT EXISTS idx_pacs_psr_orig_msg ON gold.cdm_pacs_fi_payment_status_report(original_message_id);
CREATE INDEX IF NOT EXISTS idx_pacs_psr_orig_uetr ON gold.cdm_pacs_fi_payment_status_report(original_uetr);
CREATE INDEX IF NOT EXISTS idx_pacs_psr_format ON gold.cdm_pacs_fi_payment_status_report(source_format);
CREATE INDEX IF NOT EXISTS idx_pacs_psr_tx_status ON gold.cdm_pacs_fi_payment_status_report(transaction_status);


-- =====================================================
-- 7. cdm_pacs_payment_return (pacs.004)
-- =====================================================
-- Purpose: Bank → Bank: Return/reversal of a previous payment
-- Formats: pacs.004, and all *_pacs004 variants
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_pacs_payment_return (
    -- Primary Key
    return_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,

    -- Message Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,
    number_of_transactions INT,
    settlement_method VARCHAR(4),
    clearing_system_code VARCHAR(5),

    -- Original Group Information
    original_message_id VARCHAR(35),
    original_message_name_id VARCHAR(35),
    original_creation_datetime TIMESTAMP,

    -- Return Transaction
    return_identification VARCHAR(35),
    original_instruction_id VARCHAR(35),
    original_end_to_end_id VARCHAR(35),
    original_transaction_id VARCHAR(35),
    original_uetr VARCHAR(36),
    original_clearing_system_reference VARCHAR(35),

    -- Return Reason
    return_reason_code VARCHAR(4),  -- AC01, AC04, AM04, etc.
    return_reason_proprietary VARCHAR(35),
    return_reason_info TEXT,
    return_originator_name VARCHAR(140),
    return_originator_bic VARCHAR(11),
    return_originator_id VARCHAR(35),

    -- Returned Amount
    returned_settlement_amount DECIMAL(18,4),
    returned_settlement_currency VARCHAR(3),
    return_settlement_date DATE,
    charge_bearer VARCHAR(4),

    -- Original Transaction Reference
    original_settlement_amount DECIMAL(18,4),
    original_settlement_currency VARCHAR(3),
    original_settlement_date DATE,

    -- Original Debtor (now receives funds back)
    original_debtor_name VARCHAR(140),
    original_debtor_address_country VARCHAR(2),
    original_debtor_account_iban VARCHAR(34),
    original_debtor_account_other VARCHAR(35),
    original_debtor_agent_bic VARCHAR(11),
    original_debtor_agent_clearing_id VARCHAR(35),
    original_debtor_agent_name VARCHAR(140),

    -- Original Creditor (returning funds)
    original_creditor_name VARCHAR(140),
    original_creditor_address_country VARCHAR(2),
    original_creditor_account_iban VARCHAR(34),
    original_creditor_account_other VARCHAR(35),
    original_creditor_agent_bic VARCHAR(11),
    original_creditor_agent_clearing_id VARCHAR(35),
    original_creditor_agent_name VARCHAR(140),

    -- Instructing/Instructed Agents (for return message)
    instructing_agent_bic VARCHAR(11),
    instructing_agent_clearing_id VARCHAR(35),
    instructed_agent_bic VARCHAR(11),
    instructed_agent_clearing_id VARCHAR(35),

    -- Remittance
    remittance_unstructured TEXT[],

    -- Supplementary
    supplementary_data JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);

CREATE INDEX IF NOT EXISTS idx_pacs_rtn_stg_id ON gold.cdm_pacs_payment_return(source_stg_id);
CREATE INDEX IF NOT EXISTS idx_pacs_rtn_msg_id ON gold.cdm_pacs_payment_return(message_id);
CREATE INDEX IF NOT EXISTS idx_pacs_rtn_orig_msg ON gold.cdm_pacs_payment_return(original_message_id);
CREATE INDEX IF NOT EXISTS idx_pacs_rtn_orig_uetr ON gold.cdm_pacs_payment_return(original_uetr);
CREATE INDEX IF NOT EXISTS idx_pacs_rtn_format ON gold.cdm_pacs_payment_return(source_format);
CREATE INDEX IF NOT EXISTS idx_pacs_rtn_reason ON gold.cdm_pacs_payment_return(return_reason_code);


-- =====================================================
-- 8. cdm_pacs_fi_direct_debit (pacs.003)
-- =====================================================
-- Purpose: Bank → Bank: Interbank direct debit execution
-- Formats: pacs.003
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_pacs_fi_direct_debit (
    -- Primary Key
    direct_debit_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,

    -- Group Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,
    number_of_transactions INT,
    total_settlement_amount DECIMAL(18,4),
    total_settlement_currency VARCHAR(3),
    settlement_method VARCHAR(4),
    clearing_system_code VARCHAR(35),

    -- Instructing/Instructed Agents
    instructing_agent_bic VARCHAR(11),
    instructing_agent_clearing_id VARCHAR(35),
    instructed_agent_bic VARCHAR(11),
    instructed_agent_clearing_id VARCHAR(35),

    -- Payment Identification
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35),
    uetr VARCHAR(36),
    transaction_id VARCHAR(35),

    -- Payment Type
    service_level_code VARCHAR(4),
    local_instrument_code VARCHAR(35),
    sequence_type VARCHAR(4),
    category_purpose_code VARCHAR(4),

    -- Settlement
    interbank_settlement_amount DECIMAL(18,4),
    interbank_settlement_currency VARCHAR(3),
    interbank_settlement_date DATE,
    instructed_amount DECIMAL(18,4),
    instructed_currency VARCHAR(3),
    charge_bearer VARCHAR(4),

    -- Creditor (Collecting Party)
    creditor_name VARCHAR(140),
    creditor_address_country VARCHAR(2),
    creditor_account_iban VARCHAR(34),
    creditor_account_other VARCHAR(35),
    creditor_agent_bic VARCHAR(11),
    creditor_agent_clearing_id VARCHAR(35),

    -- Creditor Scheme Identification
    creditor_scheme_id VARCHAR(35),
    creditor_scheme_name VARCHAR(35),

    -- Debtor (Party being debited)
    debtor_name VARCHAR(140),
    debtor_address_country VARCHAR(2),
    debtor_account_iban VARCHAR(34),
    debtor_account_other VARCHAR(35),
    debtor_agent_bic VARCHAR(11),
    debtor_agent_clearing_id VARCHAR(35),

    -- Mandate Information
    mandate_id VARCHAR(35),
    mandate_date_of_signature DATE,

    -- Remittance
    remittance_unstructured TEXT[],
    purpose_code VARCHAR(4),

    -- Supplementary
    supplementary_data JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);

CREATE INDEX IF NOT EXISTS idx_pacs_dd_stg_id ON gold.cdm_pacs_fi_direct_debit(source_stg_id);
CREATE INDEX IF NOT EXISTS idx_pacs_dd_msg_id ON gold.cdm_pacs_fi_direct_debit(message_id);
CREATE INDEX IF NOT EXISTS idx_pacs_dd_mandate ON gold.cdm_pacs_fi_direct_debit(mandate_id);


-- =====================================================
-- 9. cdm_camt_bank_to_customer_statement (camt.053)
-- =====================================================
-- Purpose: Bank → Customer: End-of-day account statement
-- Formats: camt.053, MT940, BAI2
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_camt_bank_to_customer_statement (
    -- Primary Key
    statement_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,

    -- Message Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,
    message_recipient_name VARCHAR(140),

    -- Statement Identification
    statement_reference VARCHAR(35),
    electronic_sequence_number BIGINT,
    legal_sequence_number BIGINT,
    statement_creation_datetime TIMESTAMP,
    from_datetime TIMESTAMP,
    to_datetime TIMESTAMP,

    -- Account
    account_iban VARCHAR(34),
    account_other_id VARCHAR(34),
    account_other_scheme VARCHAR(35),
    account_currency VARCHAR(3),
    account_name VARCHAR(70),
    account_owner_name VARCHAR(140),
    account_owner_address_country VARCHAR(2),
    account_servicer_bic VARCHAR(11),
    account_servicer_name VARCHAR(140),

    -- Opening Balance
    opening_balance_type VARCHAR(4),  -- OPBD, PRCD
    opening_balance_amount DECIMAL(18,4),
    opening_balance_currency VARCHAR(3),
    opening_balance_credit_debit VARCHAR(4),  -- CRDT, DBIT
    opening_balance_date DATE,

    -- Closing Balance
    closing_balance_type VARCHAR(4),  -- CLBD, CLAV
    closing_balance_amount DECIMAL(18,4),
    closing_balance_currency VARCHAR(3),
    closing_balance_credit_debit VARCHAR(4),
    closing_balance_date DATE,

    -- Available Balance
    available_balance_amount DECIMAL(18,4),
    available_balance_currency VARCHAR(3),
    available_balance_credit_debit VARCHAR(4),
    available_balance_date DATE,

    -- Forward Available Balance
    forward_balance_amount DECIMAL(18,4),
    forward_balance_currency VARCHAR(3),
    forward_balance_date DATE,

    -- Transaction Summary
    total_number_of_entries INT,
    total_sum_of_entries DECIMAL(18,4),
    total_net_entry_amount DECIMAL(18,4),
    total_net_entry_credit_debit VARCHAR(4),
    total_credit_entries_count INT,
    total_credit_entries_sum DECIMAL(18,4),
    total_debit_entries_count INT,
    total_debit_entries_sum DECIMAL(18,4),

    -- Entries (stored as JSON array for flexibility)
    entries_count INT,
    entries JSONB,  -- Array of entry summaries

    -- Supplementary
    supplementary_data JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);

CREATE INDEX IF NOT EXISTS idx_camt_stmt_stg_id ON gold.cdm_camt_bank_to_customer_statement(source_stg_id);
CREATE INDEX IF NOT EXISTS idx_camt_stmt_msg_id ON gold.cdm_camt_bank_to_customer_statement(message_id);
CREATE INDEX IF NOT EXISTS idx_camt_stmt_ref ON gold.cdm_camt_bank_to_customer_statement(statement_reference);
CREATE INDEX IF NOT EXISTS idx_camt_stmt_acct ON gold.cdm_camt_bank_to_customer_statement(account_iban);
CREATE INDEX IF NOT EXISTS idx_camt_stmt_format ON gold.cdm_camt_bank_to_customer_statement(source_format);
CREATE INDEX IF NOT EXISTS idx_camt_stmt_period ON gold.cdm_camt_bank_to_customer_statement(from_datetime, to_datetime);


-- =====================================================
-- 10. cdm_camt_bank_to_customer_account_report (camt.052)
-- =====================================================
-- Purpose: Bank → Customer: Intraday account report
-- Formats: camt.052, MT942
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_camt_bank_to_customer_account_report (
    -- Primary Key
    report_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,

    -- Message Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,
    message_recipient_name VARCHAR(140),

    -- Report Identification
    report_reference VARCHAR(35),
    electronic_sequence_number BIGINT,
    report_creation_datetime TIMESTAMP,
    from_datetime TIMESTAMP,
    to_datetime TIMESTAMP,

    -- Account
    account_iban VARCHAR(34),
    account_other_id VARCHAR(34),
    account_currency VARCHAR(3),
    account_owner_name VARCHAR(140),
    account_servicer_bic VARCHAR(11),

    -- Balances
    booked_balance_amount DECIMAL(18,4),
    booked_balance_currency VARCHAR(3),
    booked_balance_credit_debit VARCHAR(4),
    booked_balance_date DATE,
    available_balance_amount DECIMAL(18,4),
    available_balance_currency VARCHAR(3),
    available_balance_date DATE,

    -- Transaction Summary
    total_number_of_entries INT,
    total_credit_entries_count INT,
    total_credit_entries_sum DECIMAL(18,4),
    total_debit_entries_count INT,
    total_debit_entries_sum DECIMAL(18,4),

    -- Entries
    entries_count INT,
    entries JSONB,

    -- Supplementary
    supplementary_data JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);

CREATE INDEX IF NOT EXISTS idx_camt_rpt_stg_id ON gold.cdm_camt_bank_to_customer_account_report(source_stg_id);
CREATE INDEX IF NOT EXISTS idx_camt_rpt_msg_id ON gold.cdm_camt_bank_to_customer_account_report(message_id);
CREATE INDEX IF NOT EXISTS idx_camt_rpt_acct ON gold.cdm_camt_bank_to_customer_account_report(account_iban);


-- =====================================================
-- 11. cdm_camt_bank_to_customer_debit_credit_notification (camt.054)
-- =====================================================
-- Purpose: Bank → Customer: Transaction notification
-- Formats: camt.054, MT900, MT910
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_camt_bank_to_customer_debit_credit_notification (
    -- Primary Key
    notification_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,

    -- Message Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,
    message_recipient_name VARCHAR(140),

    -- Notification Identification
    notification_reference VARCHAR(35),
    notification_creation_datetime TIMESTAMP,

    -- Account
    account_iban VARCHAR(34),
    account_other_id VARCHAR(34),
    account_currency VARCHAR(3),
    account_owner_name VARCHAR(140),
    account_servicer_bic VARCHAR(11),

    -- Entry Details
    entry_reference VARCHAR(35),
    entry_amount DECIMAL(18,4),
    entry_currency VARCHAR(3),
    entry_credit_debit VARCHAR(4),  -- CRDT, DBIT
    entry_status VARCHAR(4),  -- BOOK, PDNG
    entry_booking_date DATE,
    entry_value_date DATE,
    entry_account_servicer_reference VARCHAR(35),

    -- Transaction Details
    transaction_end_to_end_id VARCHAR(35),
    transaction_instruction_id VARCHAR(35),
    transaction_amount DECIMAL(18,4),
    transaction_currency VARCHAR(3),

    -- Counterparty
    counterparty_name VARCHAR(140),
    counterparty_account_iban VARCHAR(34),
    counterparty_account_other VARCHAR(35),
    counterparty_agent_bic VARCHAR(11),

    -- Remittance
    remittance_unstructured TEXT[],

    -- Supplementary
    supplementary_data JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);

CREATE INDEX IF NOT EXISTS idx_camt_ntf_stg_id ON gold.cdm_camt_bank_to_customer_debit_credit_notification(source_stg_id);
CREATE INDEX IF NOT EXISTS idx_camt_ntf_msg_id ON gold.cdm_camt_bank_to_customer_debit_credit_notification(message_id);
CREATE INDEX IF NOT EXISTS idx_camt_ntf_acct ON gold.cdm_camt_bank_to_customer_debit_credit_notification(account_iban);
CREATE INDEX IF NOT EXISTS idx_camt_ntf_e2e ON gold.cdm_camt_bank_to_customer_debit_credit_notification(transaction_end_to_end_id);


-- =====================================================
-- 12. cdm_camt_fi_payment_cancellation_request (camt.056)
-- =====================================================
-- Purpose: Bank → Bank: Request to cancel a previous payment
-- Formats: camt.056
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_camt_fi_payment_cancellation_request (
    -- Primary Key
    cancellation_request_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,

    -- Assignment
    assignment_id VARCHAR(35),
    assignment_creation_datetime TIMESTAMP,
    assigner_agent_bic VARCHAR(11),
    assigner_agent_name VARCHAR(140),
    assignee_agent_bic VARCHAR(11),
    assignee_agent_name VARCHAR(140),

    -- Case
    case_id VARCHAR(35),
    case_creator_name VARCHAR(140),
    case_creator_bic VARCHAR(11),

    -- Control Data
    number_of_transactions_requested INT,
    control_sum DECIMAL(18,4),

    -- Original Group Information
    original_message_id VARCHAR(35),
    original_message_name_id VARCHAR(35),
    original_creation_datetime TIMESTAMP,

    -- Transaction to Cancel
    cancellation_id VARCHAR(35),
    original_instruction_id VARCHAR(35),
    original_end_to_end_id VARCHAR(35),
    original_transaction_id VARCHAR(35),
    original_uetr VARCHAR(36),
    original_clearing_system_reference VARCHAR(35),

    -- Cancellation Reason
    cancellation_reason_code VARCHAR(4),  -- CUST, DUPL, TECH, FRAD, etc.
    cancellation_reason_proprietary VARCHAR(35),
    cancellation_reason_info TEXT,

    -- Original Transaction Reference
    original_settlement_amount DECIMAL(18,4),
    original_settlement_currency VARCHAR(3),
    original_settlement_date DATE,

    -- Original Parties
    original_debtor_name VARCHAR(140),
    original_debtor_account_iban VARCHAR(34),
    original_debtor_account_other VARCHAR(35),
    original_debtor_agent_bic VARCHAR(11),
    original_creditor_name VARCHAR(140),
    original_creditor_account_iban VARCHAR(34),
    original_creditor_account_other VARCHAR(35),
    original_creditor_agent_bic VARCHAR(11),

    -- Supplementary
    supplementary_data JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);

CREATE INDEX IF NOT EXISTS idx_camt_cxl_stg_id ON gold.cdm_camt_fi_payment_cancellation_request(source_stg_id);
CREATE INDEX IF NOT EXISTS idx_camt_cxl_assign ON gold.cdm_camt_fi_payment_cancellation_request(assignment_id);
CREATE INDEX IF NOT EXISTS idx_camt_cxl_case ON gold.cdm_camt_fi_payment_cancellation_request(case_id);
CREATE INDEX IF NOT EXISTS idx_camt_cxl_orig_msg ON gold.cdm_camt_fi_payment_cancellation_request(original_message_id);
CREATE INDEX IF NOT EXISTS idx_camt_cxl_orig_uetr ON gold.cdm_camt_fi_payment_cancellation_request(original_uetr);


-- =====================================================
-- COMMENTS
-- =====================================================
COMMENT ON TABLE gold.cdm_pain_customer_credit_transfer_initiation IS 'ISO 20022 pain.001 - Customer Credit Transfer Initiation';
COMMENT ON TABLE gold.cdm_pain_customer_direct_debit_initiation IS 'ISO 20022 pain.008 - Customer Direct Debit Initiation';
COMMENT ON TABLE gold.cdm_pain_customer_payment_status_report IS 'ISO 20022 pain.002 - Customer Payment Status Report';
COMMENT ON TABLE gold.cdm_pacs_fi_customer_credit_transfer IS 'ISO 20022 pacs.008 - FI to FI Customer Credit Transfer';
COMMENT ON TABLE gold.cdm_pacs_fi_credit_transfer IS 'ISO 20022 pacs.009 - Financial Institution Credit Transfer';
COMMENT ON TABLE gold.cdm_pacs_fi_payment_status_report IS 'ISO 20022 pacs.002 - FI to FI Payment Status Report';
COMMENT ON TABLE gold.cdm_pacs_payment_return IS 'ISO 20022 pacs.004 - Payment Return';
COMMENT ON TABLE gold.cdm_pacs_fi_direct_debit IS 'ISO 20022 pacs.003 - FI to FI Direct Debit';
COMMENT ON TABLE gold.cdm_camt_bank_to_customer_statement IS 'ISO 20022 camt.053 - Bank to Customer Statement';
COMMENT ON TABLE gold.cdm_camt_bank_to_customer_account_report IS 'ISO 20022 camt.052 - Bank to Customer Account Report';
COMMENT ON TABLE gold.cdm_camt_bank_to_customer_debit_credit_notification IS 'ISO 20022 camt.054 - Bank to Customer Debit Credit Notification';
COMMENT ON TABLE gold.cdm_camt_fi_payment_cancellation_request IS 'ISO 20022 camt.056 - FI to FI Payment Cancellation Request';
