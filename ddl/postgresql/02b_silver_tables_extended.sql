-- GPS CDM - Extended Silver Layer Tables (PostgreSQL)
-- =====================================================
-- Extended Silver tables for all 63+ payment message types
-- Run after 02_silver_tables.sql

-- =====================================================
-- ISO 20022 PACS (Clearing & Settlement) - Silver Layer
-- =====================================================

CREATE TABLE IF NOT EXISTS silver.stg_pacs008 (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'pacs.008',

    -- Message Header
    msg_id VARCHAR(35),
    creation_date_time TIMESTAMP,
    number_of_transactions INT,

    -- Settlement
    settlement_method VARCHAR(10),
    clearing_system VARCHAR(35),
    interbank_settlement_date DATE,
    total_interbank_settlement_amount DECIMAL(18,5),
    total_interbank_settlement_currency VARCHAR(3),

    -- Agents
    instructing_agent_bic VARCHAR(11),
    instructed_agent_bic VARCHAR(11),

    -- Transaction
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35),
    transaction_id VARCHAR(35),
    uetr VARCHAR(36),
    clearing_system_reference VARCHAR(50),

    -- Amounts
    interbank_settlement_amount DECIMAL(18,5),
    interbank_settlement_currency VARCHAR(3),
    instructed_amount DECIMAL(18,5),
    instructed_currency VARCHAR(3),
    exchange_rate DECIMAL(12,6),

    -- Charges
    charge_bearer VARCHAR(10),
    charges_amount DECIMAL(18,5),
    charges_currency VARCHAR(3),

    -- Debtor
    debtor_name VARCHAR(140),
    debtor_address TEXT,
    debtor_country VARCHAR(2),
    debtor_account_iban VARCHAR(34),
    debtor_agent_bic VARCHAR(11),

    -- Creditor
    creditor_name VARCHAR(140),
    creditor_address TEXT,
    creditor_country VARCHAR(2),
    creditor_account_iban VARCHAR(34),
    creditor_agent_bic VARCHAR(11),

    -- Ultimate Parties
    ultimate_debtor_name VARCHAR(140),
    ultimate_creditor_name VARCHAR(140),

    -- Intermediary Agents (up to 3)
    intermediary_agent_1_bic VARCHAR(11),
    intermediary_agent_2_bic VARCHAR(11),
    intermediary_agent_3_bic VARCHAR(11),

    -- Purpose
    purpose_code VARCHAR(10),
    remittance_info TEXT,
    structured_remittance JSONB,
    regulatory_reporting JSONB,

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_gold_at TIMESTAMP,
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_pacs008_msg ON silver.stg_pacs008(msg_id);
CREATE INDEX IF NOT EXISTS idx_stg_pacs008_e2e ON silver.stg_pacs008(end_to_end_id);
CREATE INDEX IF NOT EXISTS idx_stg_pacs008_uetr ON silver.stg_pacs008(uetr);
CREATE INDEX IF NOT EXISTS idx_stg_pacs008_status ON silver.stg_pacs008(processing_status);

-- =====================================================
-- ISO 20022 CAMT Messages - Silver Layer
-- =====================================================

CREATE TABLE IF NOT EXISTS silver.stg_camt053 (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'camt.053',

    -- Message Header
    msg_id VARCHAR(35),
    creation_date_time TIMESTAMP,

    -- Statement Info
    statement_id VARCHAR(35),
    sequence_number VARCHAR(10),
    from_date DATE,
    to_date DATE,

    -- Account
    account_iban VARCHAR(34),
    account_number VARCHAR(50),
    account_currency VARCHAR(3),
    account_owner_name VARCHAR(140),
    account_servicer_bic VARCHAR(11),

    -- Opening Balance
    opening_balance_amount DECIMAL(18,5),
    opening_balance_currency VARCHAR(3),
    opening_balance_credit_debit VARCHAR(4),
    opening_balance_date DATE,

    -- Closing Balance
    closing_balance_amount DECIMAL(18,5),
    closing_balance_currency VARCHAR(3),
    closing_balance_credit_debit VARCHAR(4),
    closing_balance_date DATE,

    -- Summary
    number_of_entries INT,
    sum_of_entries DECIMAL(18,5),

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_camt053_stmt ON silver.stg_camt053(statement_id);
CREATE INDEX IF NOT EXISTS idx_stg_camt053_acct ON silver.stg_camt053(account_iban);

-- =====================================================
-- Additional SWIFT MT Messages - Silver Layer
-- =====================================================

CREATE TABLE IF NOT EXISTS silver.stg_mt202 (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(10) DEFAULT 'MT202',

    -- Header
    sender_bic VARCHAR(12),
    receiver_bic VARCHAR(12),

    -- References
    transaction_reference VARCHAR(16),
    related_reference VARCHAR(16),

    -- Value Date & Amount
    value_date DATE,
    currency VARCHAR(3),
    amount DECIMAL(18,5),

    -- Agents
    ordering_institution_bic VARCHAR(11),
    senders_correspondent_bic VARCHAR(11),
    receivers_correspondent_bic VARCHAR(11),
    intermediary_bic VARCHAR(11),
    account_with_institution_bic VARCHAR(11),
    beneficiary_institution_bic VARCHAR(11),

    -- Additional Info
    sender_to_receiver_info TEXT,

    -- gSPI
    uetr VARCHAR(36),

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_mt202_ref ON silver.stg_mt202(transaction_reference);
CREATE INDEX IF NOT EXISTS idx_stg_mt202_uetr ON silver.stg_mt202(uetr);

CREATE TABLE IF NOT EXISTS silver.stg_mt940 (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(10) DEFAULT 'MT940',

    -- Header
    sender_bic VARCHAR(12),
    receiver_bic VARCHAR(12),

    -- Transaction Reference
    transaction_reference VARCHAR(16),

    -- Account
    account_identification VARCHAR(50),

    -- Statement
    statement_number VARCHAR(10),
    sequence_number VARCHAR(10),

    -- Opening Balance
    opening_balance_date DATE,
    opening_balance_currency VARCHAR(3),
    opening_balance_amount DECIMAL(18,5),
    opening_balance_indicator VARCHAR(2),

    -- Closing Balance
    closing_balance_date DATE,
    closing_balance_currency VARCHAR(3),
    closing_balance_amount DECIMAL(18,5),
    closing_balance_indicator VARCHAR(2),

    -- Number of lines
    number_of_lines INT,

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_mt940_ref ON silver.stg_mt940(transaction_reference);
CREATE INDEX IF NOT EXISTS idx_stg_mt940_acct ON silver.stg_mt940(account_identification);

-- =====================================================
-- Real-Time Payments - Silver Layer
-- =====================================================

CREATE TABLE IF NOT EXISTS silver.stg_fednow (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'FEDNOW',

    -- Message Info
    msg_id VARCHAR(35),
    creation_date_time TIMESTAMP,
    settlement_method VARCHAR(10),
    interbank_settlement_date DATE,

    -- Amount
    interbank_settlement_amount DECIMAL(18,5),
    interbank_settlement_currency VARCHAR(3),

    -- Agents
    instructing_agent_routing VARCHAR(20),
    instructed_agent_routing VARCHAR(20),

    -- Transaction IDs
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35),
    transaction_id VARCHAR(35),
    uetr VARCHAR(36),

    -- Debtor
    debtor_name VARCHAR(140),
    debtor_account VARCHAR(50),
    debtor_agent_routing VARCHAR(20),

    -- Creditor
    creditor_name VARCHAR(140),
    creditor_account VARCHAR(50),
    creditor_agent_routing VARCHAR(20),

    -- Purpose & Remittance
    purpose_code VARCHAR(10),
    remittance_info TEXT,

    -- Fraud Detection
    fraud_score INT,
    fraud_risk_level VARCHAR(20),

    -- Timing
    acceptance_datetime TIMESTAMP,

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_fednow_msg ON silver.stg_fednow(msg_id);
CREATE INDEX IF NOT EXISTS idx_stg_fednow_e2e ON silver.stg_fednow(end_to_end_id);

CREATE TABLE IF NOT EXISTS silver.stg_pix (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'PIX',

    -- Transaction Info
    end_to_end_id VARCHAR(50),
    creation_date_time TIMESTAMP,
    local_instrument VARCHAR(20),

    -- Payer
    payer_ispb VARCHAR(10),
    payer_branch VARCHAR(10),
    payer_account VARCHAR(30),
    payer_account_type VARCHAR(10),
    payer_name VARCHAR(140),
    payer_cpf_cnpj VARCHAR(20),
    payer_pix_key VARCHAR(100),
    payer_pix_key_type VARCHAR(20),

    -- Payee
    payee_ispb VARCHAR(10),
    payee_branch VARCHAR(10),
    payee_account VARCHAR(30),
    payee_account_type VARCHAR(10),
    payee_name VARCHAR(140),
    payee_cpf_cnpj VARCHAR(20),
    payee_pix_key VARCHAR(100),
    payee_pix_key_type VARCHAR(20),

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'BRL',

    -- Transaction Type
    qr_code_type VARCHAR(20),
    initiation_type VARCHAR(20),
    payment_type VARCHAR(20),

    -- Remittance
    remittance_info TEXT,

    -- Fraud Detection
    fraud_score INT,

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_pix_e2e ON silver.stg_pix(end_to_end_id);

CREATE TABLE IF NOT EXISTS silver.stg_npp (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'NPP',

    -- Message Info
    payment_id VARCHAR(50),
    creation_date_time TIMESTAMP,

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'AUD',

    -- Payer
    payer_bsb VARCHAR(10),
    payer_account VARCHAR(20),
    payer_name VARCHAR(140),
    payer_payid VARCHAR(100),
    payer_payid_type VARCHAR(20),

    -- Payee
    payee_bsb VARCHAR(10),
    payee_account VARCHAR(20),
    payee_name VARCHAR(140),
    payee_payid VARCHAR(100),
    payee_payid_type VARCHAR(20),

    -- Reference
    end_to_end_id VARCHAR(50),
    payment_reference VARCHAR(100),

    -- Remittance
    remittance_info TEXT,

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_npp_pid ON silver.stg_npp(payment_id);

CREATE TABLE IF NOT EXISTS silver.stg_upi (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'UPI',

    -- Transaction Info
    transaction_id VARCHAR(50),
    transaction_ref_id VARCHAR(50),
    creation_date_time TIMESTAMP,

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'INR',

    -- Payer
    payer_vpa VARCHAR(100),
    payer_name VARCHAR(140),
    payer_account VARCHAR(50),
    payer_ifsc VARCHAR(20),
    payer_mobile VARCHAR(20),

    -- Payee
    payee_vpa VARCHAR(100),
    payee_name VARCHAR(140),
    payee_account VARCHAR(50),
    payee_ifsc VARCHAR(20),
    payee_mobile VARCHAR(20),

    -- Transaction Type
    transaction_type VARCHAR(20),
    sub_type VARCHAR(20),

    -- Remittance
    remittance_info TEXT,

    -- Status
    transaction_status VARCHAR(20),
    response_code VARCHAR(10),

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_upi_tid ON silver.stg_upi(transaction_id);

CREATE TABLE IF NOT EXISTS silver.stg_paynow (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'PAYNOW',

    -- Transaction Info
    transaction_id VARCHAR(50),
    creation_date_time TIMESTAMP,

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'SGD',

    -- Payer
    payer_proxy_type VARCHAR(20),
    payer_proxy_value VARCHAR(100),
    payer_name VARCHAR(140),
    payer_bank_code VARCHAR(20),
    payer_account VARCHAR(50),

    -- Payee
    payee_proxy_type VARCHAR(20),
    payee_proxy_value VARCHAR(100),
    payee_name VARCHAR(140),
    payee_bank_code VARCHAR(20),
    payee_account VARCHAR(50),

    -- Reference
    end_to_end_id VARCHAR(50),

    -- Remittance
    remittance_info TEXT,

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_paynow_tid ON silver.stg_paynow(transaction_id);

CREATE TABLE IF NOT EXISTS silver.stg_promptpay (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'PROMPTPAY',

    -- Transaction Info
    transaction_id VARCHAR(50),
    creation_date_time TIMESTAMP,

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'THB',

    -- Payer
    payer_proxy_type VARCHAR(20),
    payer_proxy_value VARCHAR(100),
    payer_name VARCHAR(140),
    payer_bank_code VARCHAR(20),
    payer_account VARCHAR(50),

    -- Payee
    payee_proxy_type VARCHAR(20),
    payee_proxy_value VARCHAR(100),
    payee_name VARCHAR(140),
    payee_bank_code VARCHAR(20),
    payee_account VARCHAR(50),

    -- Reference
    end_to_end_id VARCHAR(50),
    qr_code_data TEXT,

    -- Remittance
    remittance_info TEXT,

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_promptpay_tid ON silver.stg_promptpay(transaction_id);

CREATE TABLE IF NOT EXISTS silver.stg_instapay (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'INSTAPAY',

    -- Transaction Info
    transaction_id VARCHAR(50),
    creation_date_time TIMESTAMP,

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'PHP',

    -- Sender
    sender_bank_code VARCHAR(20),
    sender_account VARCHAR(50),
    sender_name VARCHAR(140),

    -- Receiver
    receiver_bank_code VARCHAR(20),
    receiver_account VARCHAR(50),
    receiver_name VARCHAR(140),

    -- Reference
    reference_number VARCHAR(50),

    -- Remittance
    remittance_info TEXT,

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_instapay_tid ON silver.stg_instapay(transaction_id);

-- =====================================================
-- RTGS Systems - Silver Layer
-- =====================================================

CREATE TABLE IF NOT EXISTS silver.stg_target2 (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'TARGET2',

    -- Message Info
    msg_id VARCHAR(35),
    creation_date_time TIMESTAMP,

    -- Settlement
    settlement_date DATE,
    settlement_method VARCHAR(10),

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'EUR',

    -- Agents
    instructing_agent_bic VARCHAR(11),
    instructed_agent_bic VARCHAR(11),
    debtor_agent_bic VARCHAR(11),
    creditor_agent_bic VARCHAR(11),

    -- Transaction IDs
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35),
    transaction_id VARCHAR(35),
    uetr VARCHAR(36),

    -- Debtor
    debtor_name VARCHAR(140),
    debtor_account VARCHAR(50),

    -- Creditor
    creditor_name VARCHAR(140),
    creditor_account VARCHAR(50),

    -- Payment Type
    payment_type VARCHAR(20),
    service_level VARCHAR(20),

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_target2_msg ON silver.stg_target2(msg_id);

CREATE TABLE IF NOT EXISTS silver.stg_sarie (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'SARIE',

    -- Message Info
    message_id VARCHAR(50),
    creation_date_time TIMESTAMP,

    -- Settlement
    settlement_date DATE,

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'SAR',

    -- Participants
    sending_bank_code VARCHAR(20),
    receiving_bank_code VARCHAR(20),

    -- Transaction Reference
    transaction_reference VARCHAR(50),

    -- Originator
    originator_name VARCHAR(140),
    originator_account VARCHAR(50),
    originator_id VARCHAR(50),

    -- Beneficiary
    beneficiary_name VARCHAR(140),
    beneficiary_account VARCHAR(50),
    beneficiary_id VARCHAR(50),

    -- Purpose
    purpose VARCHAR(100),

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_sarie_ref ON silver.stg_sarie(transaction_reference);

CREATE TABLE IF NOT EXISTS silver.stg_uaefts (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'UAEFTS',

    -- Message Info
    message_id VARCHAR(50),
    creation_date_time TIMESTAMP,

    -- Settlement
    settlement_date DATE,

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'AED',

    -- Participants
    sending_bank_code VARCHAR(20),
    receiving_bank_code VARCHAR(20),

    -- Transaction Reference
    transaction_reference VARCHAR(50),

    -- Originator
    originator_name VARCHAR(140),
    originator_account VARCHAR(50),
    originator_address TEXT,

    -- Beneficiary
    beneficiary_name VARCHAR(140),
    beneficiary_account VARCHAR(50),
    beneficiary_address TEXT,

    -- Purpose
    purpose VARCHAR(100),

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_uaefts_ref ON silver.stg_uaefts(transaction_reference);

CREATE TABLE IF NOT EXISTS silver.stg_kftc (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'KFTC',

    -- Message Info
    message_id VARCHAR(50),
    creation_date_time TIMESTAMP,

    -- Settlement
    settlement_date DATE,

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'KRW',

    -- Participants
    sending_bank_code VARCHAR(20),
    receiving_bank_code VARCHAR(20),

    -- Transaction Reference
    transaction_reference VARCHAR(50),

    -- Payer
    payer_name VARCHAR(140),
    payer_account VARCHAR(50),

    -- Payee
    payee_name VARCHAR(140),
    payee_account VARCHAR(50),

    -- Purpose
    purpose VARCHAR(100),

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_kftc_ref ON silver.stg_kftc(transaction_reference);

CREATE TABLE IF NOT EXISTS silver.stg_cnaps (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'CNAPS',

    -- Message Info
    message_id VARCHAR(50),
    creation_date_time TIMESTAMP,

    -- Settlement
    settlement_date DATE,
    business_type VARCHAR(20),

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'CNY',

    -- Participants
    sending_bank_code VARCHAR(20),
    receiving_bank_code VARCHAR(20),

    -- Payer
    payer_name VARCHAR(140),
    payer_account VARCHAR(50),
    payer_bank_name VARCHAR(140),

    -- Payee
    payee_name VARCHAR(140),
    payee_account VARCHAR(50),
    payee_bank_name VARCHAR(140),

    -- Transaction Reference
    transaction_reference VARCHAR(50),

    -- Purpose
    purpose VARCHAR(100),

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_cnaps_ref ON silver.stg_cnaps(transaction_reference);

CREATE TABLE IF NOT EXISTS silver.stg_bojnet (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'BOJNET',

    -- Message Info
    message_id VARCHAR(50),
    creation_date_time TIMESTAMP,

    -- Settlement
    settlement_date DATE,

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'JPY',

    -- Participants
    sending_participant_code VARCHAR(20),
    receiving_participant_code VARCHAR(20),

    -- Transaction Reference
    transaction_reference VARCHAR(50),
    related_reference VARCHAR(50),

    -- Account Info
    debit_account VARCHAR(50),
    credit_account VARCHAR(50),

    -- Payment Type
    payment_type VARCHAR(20),

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_bojnet_ref ON silver.stg_bojnet(transaction_reference);

CREATE TABLE IF NOT EXISTS silver.stg_meps_plus (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'MEPS_PLUS',

    -- Message Info
    message_id VARCHAR(50),
    creation_date_time TIMESTAMP,

    -- Settlement
    settlement_date DATE,

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'SGD',

    -- Participants
    sending_bank_bic VARCHAR(11),
    receiving_bank_bic VARCHAR(11),

    -- Transaction Reference
    transaction_reference VARCHAR(50),

    -- Debtor
    debtor_name VARCHAR(140),
    debtor_account VARCHAR(50),

    -- Creditor
    creditor_name VARCHAR(140),
    creditor_account VARCHAR(50),

    -- Purpose
    purpose_code VARCHAR(10),
    remittance_info TEXT,

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_meps_plus_ref ON silver.stg_meps_plus(transaction_reference);

CREATE TABLE IF NOT EXISTS silver.stg_rtgs_hk (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'RTGS_HK',

    -- Message Info
    message_id VARCHAR(50),
    creation_date_time TIMESTAMP,

    -- Settlement
    settlement_date DATE,
    settlement_currency VARCHAR(3),

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'HKD',

    -- Participants
    sending_bank_code VARCHAR(20),
    receiving_bank_code VARCHAR(20),

    -- Transaction Reference
    transaction_reference VARCHAR(50),

    -- Payer
    payer_name VARCHAR(140),
    payer_account VARCHAR(50),

    -- Payee
    payee_name VARCHAR(140),
    payee_account VARCHAR(50),

    -- Purpose
    purpose VARCHAR(100),

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_rtgs_hk_ref ON silver.stg_rtgs_hk(transaction_reference);

-- =====================================================
-- UK Payment Schemes - Silver Layer
-- =====================================================

CREATE TABLE IF NOT EXISTS silver.stg_bacs (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'BACS',

    -- Service User Info
    service_user_number VARCHAR(20),
    service_user_name VARCHAR(50),

    -- Processing Date
    processing_date DATE,

    -- Transaction
    transaction_type VARCHAR(10),
    originating_sort_code VARCHAR(10),
    originating_account VARCHAR(20),
    destination_sort_code VARCHAR(10),
    destination_account VARCHAR(20),

    -- Amount
    amount DECIMAL(18,5),

    -- Reference
    reference VARCHAR(50),
    beneficiary_name VARCHAR(100),

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_bacs_ref ON silver.stg_bacs(reference);

CREATE TABLE IF NOT EXISTS silver.stg_chaps (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'CHAPS',

    -- Message Info
    message_id VARCHAR(50),
    creation_date_time TIMESTAMP,

    -- Settlement
    settlement_date DATE,
    settlement_method VARCHAR(20),

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'GBP',

    -- Debtor
    debtor_name VARCHAR(140),
    debtor_address TEXT,
    debtor_sort_code VARCHAR(10),
    debtor_account VARCHAR(20),
    debtor_agent_bic VARCHAR(11),

    -- Creditor
    creditor_name VARCHAR(140),
    creditor_address TEXT,
    creditor_sort_code VARCHAR(10),
    creditor_account VARCHAR(20),
    creditor_agent_bic VARCHAR(11),

    -- References
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35),
    uetr VARCHAR(36),

    -- Remittance
    remittance_info TEXT,

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_chaps_msg ON silver.stg_chaps(message_id);

CREATE TABLE IF NOT EXISTS silver.stg_faster_payments (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'FASTER_PAYMENTS',

    -- Message Info
    payment_id VARCHAR(50),
    creation_date_time TIMESTAMP,

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'GBP',

    -- Payer
    payer_sort_code VARCHAR(10),
    payer_account VARCHAR(20),
    payer_name VARCHAR(140),
    payer_address TEXT,

    -- Payee
    payee_sort_code VARCHAR(10),
    payee_account VARCHAR(20),
    payee_name VARCHAR(140),
    payee_address TEXT,

    -- References
    end_to_end_id VARCHAR(50),
    payment_reference VARCHAR(50),

    -- Timing
    requested_execution_date DATE,
    settlement_datetime TIMESTAMP,

    -- Remittance
    remittance_info TEXT,

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_fp_pid ON silver.stg_faster_payments(payment_id);

-- =====================================================
-- US Payment Schemes - Silver Layer (extended)
-- =====================================================

CREATE TABLE IF NOT EXISTS silver.stg_chips (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'CHIPS',

    -- Message Info
    sequence_number VARCHAR(20),
    message_type_code VARCHAR(10),

    -- Participants
    sending_participant VARCHAR(20),
    receiving_participant VARCHAR(20),

    -- Amount
    amount DECIMAL(18,5),
    currency VARCHAR(3) DEFAULT 'USD',

    -- Value Date
    value_date DATE,

    -- References
    sender_reference VARCHAR(50),
    related_reference VARCHAR(50),

    -- Originator
    originator_name VARCHAR(140),
    originator_address TEXT,
    originator_account VARCHAR(50),

    -- Beneficiary
    beneficiary_name VARCHAR(140),
    beneficiary_address TEXT,
    beneficiary_account VARCHAR(50),

    -- Correspondent Banks
    originator_bank VARCHAR(50),
    beneficiary_bank VARCHAR(50),
    intermediary_bank VARCHAR(50),

    -- Payment Details
    payment_details TEXT,

    -- Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_chips_seq ON silver.stg_chips(sequence_number);

-- Verify tables
SELECT 'silver' as schema, table_name FROM information_schema.tables
WHERE table_schema = 'silver' ORDER BY table_name;
