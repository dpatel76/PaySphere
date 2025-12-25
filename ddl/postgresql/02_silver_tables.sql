-- GPS CDM - Silver Layer Tables (stg_*)
-- ======================================
-- Layer 2: Structured per message type
-- Parsed from raw content but NOT unified to CDM yet.
-- Each message type has its own table matching source structure.

-- =====================================================
-- STG_PAIN001 (ISO 20022 pain.001 - Credit Transfer Initiation)
-- =====================================================
CREATE TABLE IF NOT EXISTS silver.stg_pain001 (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,               -- FK to bronze.raw_payment_messages

    -- Group Header (GrpHdr)
    msg_id VARCHAR(35) NOT NULL,
    creation_date_time TIMESTAMP,
    number_of_transactions INT,
    control_sum DECIMAL(18,4),
    initiating_party_name VARCHAR(140),
    initiating_party_id VARCHAR(35),

    -- Payment Information (PmtInf) - flattened for primary instruction
    payment_info_id VARCHAR(35),
    payment_method VARCHAR(3),                 -- TRF, CHK, TRA
    batch_booking BOOLEAN,
    requested_execution_date DATE,

    -- Debtor
    debtor_name VARCHAR(140),
    debtor_street_name VARCHAR(70),
    debtor_building_number VARCHAR(16),
    debtor_postal_code VARCHAR(16),
    debtor_town_name VARCHAR(35),
    debtor_country VARCHAR(2),
    debtor_id VARCHAR(35),
    debtor_id_type VARCHAR(35),                -- LEI, BIC, etc.

    -- Debtor Account
    debtor_account_iban VARCHAR(34),
    debtor_account_other VARCHAR(34),
    debtor_account_currency VARCHAR(3),

    -- Debtor Agent
    debtor_agent_bic VARCHAR(11),
    debtor_agent_name VARCHAR(140),
    debtor_agent_clearing_system VARCHAR(35),
    debtor_agent_member_id VARCHAR(35),

    -- Credit Transfer (CdtTrfTxInf) - primary instruction
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35),
    uetr VARCHAR(36),

    -- Amount
    instructed_amount DECIMAL(18,4),
    instructed_currency VARCHAR(3),
    equivalent_amount DECIMAL(18,4),
    equivalent_currency VARCHAR(3),

    -- Creditor Agent
    creditor_agent_bic VARCHAR(11),
    creditor_agent_name VARCHAR(140),
    creditor_agent_clearing_system VARCHAR(35),
    creditor_agent_member_id VARCHAR(35),

    -- Creditor
    creditor_name VARCHAR(140),
    creditor_street_name VARCHAR(70),
    creditor_building_number VARCHAR(16),
    creditor_postal_code VARCHAR(16),
    creditor_town_name VARCHAR(35),
    creditor_country VARCHAR(2),
    creditor_id VARCHAR(35),
    creditor_id_type VARCHAR(35),

    -- Creditor Account
    creditor_account_iban VARCHAR(34),
    creditor_account_other VARCHAR(34),
    creditor_account_currency VARCHAR(3),

    -- Purpose & Remittance
    purpose_code VARCHAR(4),
    purpose_proprietary VARCHAR(35),
    charge_bearer VARCHAR(4),                  -- DEBT, CRED, SHAR, SLEV
    remittance_information TEXT,
    structured_remittance JSONB,

    -- Regulatory Reporting
    regulatory_reporting JSONB,                -- Array of regulatory details

    -- Processing Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_gold_at TIMESTAMP,
    processing_error TEXT,

    -- Lineage
    source_raw_id VARCHAR(36),
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_pain001_msg ON silver.stg_pain001(msg_id);
CREATE INDEX IF NOT EXISTS idx_stg_pain001_e2e ON silver.stg_pain001(end_to_end_id);
CREATE INDEX IF NOT EXISTS idx_stg_pain001_status ON silver.stg_pain001(processing_status);
CREATE INDEX IF NOT EXISTS idx_stg_pain001_raw ON silver.stg_pain001(raw_id);

-- =====================================================
-- STG_MT103 (SWIFT MT103 - Single Customer Credit Transfer)
-- =====================================================
CREATE TABLE IF NOT EXISTS silver.stg_mt103 (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,

    -- Basic Header
    sender_bic VARCHAR(12),
    receiver_bic VARCHAR(12),
    message_type VARCHAR(3) DEFAULT '103',

    -- Field 20 - Sender's Reference
    senders_reference VARCHAR(16),

    -- Field 21 - Related Reference (optional)
    related_reference VARCHAR(16),

    -- Field 23B - Bank Operation Code
    bank_operation_code VARCHAR(4),            -- CRED, CRTS, SPAY, SPRI, SSTD

    -- Field 23E - Instruction Code (optional, repeatable)
    instruction_codes TEXT[],

    -- Field 26T - Transaction Type Code (optional)
    transaction_type_code VARCHAR(3),

    -- Field 32A - Value Date/Currency/Amount
    value_date DATE,
    currency VARCHAR(3),
    amount DECIMAL(18,4),

    -- Field 33B - Currency/Instructed Amount (optional)
    instructed_currency VARCHAR(3),
    instructed_amount DECIMAL(18,4),

    -- Field 36 - Exchange Rate (optional)
    exchange_rate DECIMAL(18,10),

    -- Field 50a - Ordering Customer
    ordering_customer_account VARCHAR(34),
    ordering_customer_name VARCHAR(140),
    ordering_customer_address TEXT,
    ordering_customer_country VARCHAR(2),
    ordering_customer_id VARCHAR(35),

    -- Field 51A - Sending Institution (optional)
    sending_institution_bic VARCHAR(11),

    -- Field 52a - Ordering Institution (optional)
    ordering_institution_bic VARCHAR(11),
    ordering_institution_account VARCHAR(34),
    ordering_institution_name VARCHAR(140),

    -- Field 53a - Sender's Correspondent (optional)
    senders_correspondent_bic VARCHAR(11),
    senders_correspondent_account VARCHAR(34),
    senders_correspondent_location VARCHAR(35),

    -- Field 54a - Receiver's Correspondent (optional)
    receivers_correspondent_bic VARCHAR(11),
    receivers_correspondent_account VARCHAR(34),
    receivers_correspondent_location VARCHAR(35),

    -- Field 55a - Third Reimbursement Institution (optional)
    third_reimbursement_bic VARCHAR(11),

    -- Field 56a - Intermediary Institution (optional)
    intermediary_bic VARCHAR(11),
    intermediary_account VARCHAR(34),
    intermediary_name VARCHAR(140),

    -- Field 57a - Account With Institution
    account_with_institution_bic VARCHAR(11),
    account_with_institution_account VARCHAR(34),
    account_with_institution_name VARCHAR(140),

    -- Field 59a - Beneficiary Customer
    beneficiary_account VARCHAR(34),
    beneficiary_name VARCHAR(140),
    beneficiary_address TEXT,
    beneficiary_country VARCHAR(2),
    beneficiary_id VARCHAR(35),

    -- Field 70 - Remittance Information (optional)
    remittance_information TEXT,

    -- Field 71A - Details of Charges
    details_of_charges VARCHAR(3),             -- BEN, OUR, SHA

    -- Field 71F - Sender's Charges (optional, repeatable)
    senders_charges JSONB,                     -- Array of {currency, amount}

    -- Field 71G - Receiver's Charges (optional)
    receivers_charges_currency VARCHAR(3),
    receivers_charges_amount DECIMAL(18,4),

    -- Field 72 - Sender to Receiver Information (optional)
    sender_to_receiver_info TEXT,

    -- Field 77B - Regulatory Reporting (optional)
    regulatory_reporting TEXT,

    -- Field 77T - Envelope Contents (optional)
    envelope_contents TEXT,

    -- UETR (from Field 121 in gpi)
    uetr VARCHAR(36),

    -- Processing Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_gold_at TIMESTAMP,
    processing_error TEXT,

    -- Lineage
    source_raw_id VARCHAR(36),
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_mt103_ref ON silver.stg_mt103(senders_reference);
CREATE INDEX IF NOT EXISTS idx_stg_mt103_uetr ON silver.stg_mt103(uetr);
CREATE INDEX IF NOT EXISTS idx_stg_mt103_status ON silver.stg_mt103(processing_status);
CREATE INDEX IF NOT EXISTS idx_stg_mt103_raw ON silver.stg_mt103(raw_id);
CREATE INDEX IF NOT EXISTS idx_stg_mt103_date ON silver.stg_mt103(value_date);

-- =====================================================
-- STG_ACH (US ACH - Automated Clearing House)
-- =====================================================
CREATE TABLE IF NOT EXISTS silver.stg_ach (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,

    -- File Header
    immediate_destination VARCHAR(10),
    immediate_origin VARCHAR(10),
    file_creation_date DATE,
    file_creation_time TIME,
    file_id_modifier VARCHAR(1),

    -- Batch Header
    company_name VARCHAR(16),
    company_identification VARCHAR(10),
    standard_entry_class VARCHAR(3),           -- PPD, CCD, WEB, TEL, etc.
    company_entry_description VARCHAR(10),
    effective_entry_date DATE,
    settlement_date VARCHAR(3),
    originator_status_code VARCHAR(1),
    originating_dfi_id VARCHAR(8),
    batch_number INT,

    -- Entry Detail
    transaction_code VARCHAR(2),               -- 22, 23, 27, 32, etc.
    receiving_dfi_id VARCHAR(8),
    receiving_dfi_account VARCHAR(17),
    amount DECIMAL(18,2),
    individual_id VARCHAR(15),
    individual_name VARCHAR(22),
    discretionary_data VARCHAR(2),
    addenda_indicator VARCHAR(1),
    trace_number VARCHAR(15),

    -- Addenda (if present)
    addenda_type VARCHAR(2),
    addenda_info TEXT,

    -- Return/NOC fields
    return_reason_code VARCHAR(3),
    original_entry_trace VARCHAR(15),
    date_of_death DATE,
    original_receiving_dfi VARCHAR(8),

    -- Processing Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_gold_at TIMESTAMP,
    processing_error TEXT,

    source_raw_id VARCHAR(36),
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_ach_trace ON silver.stg_ach(trace_number);
CREATE INDEX IF NOT EXISTS idx_stg_ach_status ON silver.stg_ach(processing_status);
CREATE INDEX IF NOT EXISTS idx_stg_ach_date ON silver.stg_ach(effective_entry_date);

-- =====================================================
-- STG_FEDWIRE (US Fedwire Funds Transfer)
-- =====================================================
CREATE TABLE IF NOT EXISTS silver.stg_fedwire (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,

    -- Message Disposition
    type_code VARCHAR(2),                      -- 10=Funds, 15=Foreign, 16=Settlement
    subtype_code VARCHAR(2),                   -- 00=Basic, 01=Request for Reversal, etc.

    -- Sender/Receiver
    sender_aba VARCHAR(9),
    sender_short_name VARCHAR(18),
    receiver_aba VARCHAR(9),
    receiver_short_name VARCHAR(18),

    -- IMAD (Input Message Accountability Data)
    imad VARCHAR(22),

    -- OMAD (Output Message Accountability Data)
    omad VARCHAR(22),

    -- Amount
    amount DECIMAL(18,2),

    -- Sender Reference
    sender_reference VARCHAR(16),

    -- Previous Message Identifier (for reversals)
    previous_imad VARCHAR(22),

    -- Business Function Code
    business_function_code VARCHAR(3),         -- BTR, CTR, CTP, DRB, DRC, etc.

    -- Originator
    originator_id VARCHAR(34),
    originator_name VARCHAR(35),
    originator_address_line1 VARCHAR(35),
    originator_address_line2 VARCHAR(35),
    originator_address_line3 VARCHAR(35),

    -- Originator FI
    originator_fi_id VARCHAR(34),
    originator_fi_name VARCHAR(35),
    originator_fi_address VARCHAR(105),

    -- Beneficiary
    beneficiary_id VARCHAR(34),
    beneficiary_name VARCHAR(35),
    beneficiary_address_line1 VARCHAR(35),
    beneficiary_address_line2 VARCHAR(35),
    beneficiary_address_line3 VARCHAR(35),

    -- Beneficiary FI
    beneficiary_fi_id VARCHAR(34),
    beneficiary_fi_name VARCHAR(35),
    beneficiary_fi_address VARCHAR(105),

    -- Intermediary FI
    intermediary_fi_id VARCHAR(34),
    intermediary_fi_name VARCHAR(35),
    intermediary_fi_address VARCHAR(105),

    -- Charges
    charges VARCHAR(140),

    -- Instructing FI
    instructing_fi_id VARCHAR(34),
    instructing_fi_name VARCHAR(35),

    -- Originator to Beneficiary Info
    originator_to_beneficiary_info TEXT,

    -- FI to FI Info
    fi_to_fi_info TEXT,

    -- Processing Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_gold_at TIMESTAMP,
    processing_error TEXT,

    source_raw_id VARCHAR(36),
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_fedwire_imad ON silver.stg_fedwire(imad);
CREATE INDEX IF NOT EXISTS idx_stg_fedwire_ref ON silver.stg_fedwire(sender_reference);
CREATE INDEX IF NOT EXISTS idx_stg_fedwire_status ON silver.stg_fedwire(processing_status);

-- =====================================================
-- STG_SEPA (EU SEPA Credit Transfer / Direct Debit)
-- =====================================================
CREATE TABLE IF NOT EXISTS silver.stg_sepa (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,

    -- Message Type
    sepa_message_type VARCHAR(20),             -- pacs.008, pacs.003, pain.008, etc.
    sepa_scheme VARCHAR(10),                   -- SCT, SDD_CORE, SDD_B2B

    -- Group Header
    msg_id VARCHAR(35),
    creation_date_time TIMESTAMP,
    number_of_transactions INT,
    total_interbank_settlement_amount DECIMAL(18,4),
    interbank_settlement_date DATE,
    settlement_method VARCHAR(4),
    clearing_system VARCHAR(35),

    -- Transaction Info
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35),
    uetr VARCHAR(36),
    transaction_id VARCHAR(35),

    -- Amount
    instructed_amount DECIMAL(18,4),
    instructed_currency VARCHAR(3),
    interbank_settlement_amount DECIMAL(18,4),

    -- Debtor
    debtor_name VARCHAR(140),
    debtor_iban VARCHAR(34),
    debtor_bic VARCHAR(11),
    debtor_address TEXT,

    -- Debtor Agent
    debtor_agent_bic VARCHAR(11),

    -- Creditor
    creditor_name VARCHAR(140),
    creditor_iban VARCHAR(34),
    creditor_bic VARCHAR(11),
    creditor_address TEXT,

    -- Creditor Agent
    creditor_agent_bic VARCHAR(11),

    -- Purpose
    purpose_code VARCHAR(4),
    category_purpose VARCHAR(4),

    -- Remittance
    remittance_info TEXT,

    -- Direct Debit specific
    mandate_id VARCHAR(35),
    mandate_date DATE,
    sequence_type VARCHAR(4),                  -- FRST, RCUR, FNAL, OOFF
    creditor_id VARCHAR(35),

    -- Charges
    charge_bearer VARCHAR(4),

    -- Processing Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_gold_at TIMESTAMP,
    processing_error TEXT,

    source_raw_id VARCHAR(36),
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_sepa_msg ON silver.stg_sepa(msg_id);
CREATE INDEX IF NOT EXISTS idx_stg_sepa_e2e ON silver.stg_sepa(end_to_end_id);
CREATE INDEX IF NOT EXISTS idx_stg_sepa_status ON silver.stg_sepa(processing_status);

-- =====================================================
-- STG_RTP (US Real-Time Payments)
-- =====================================================
CREATE TABLE IF NOT EXISTS silver.stg_rtp (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,

    -- Message identification
    msg_id VARCHAR(35),
    creation_date_time TIMESTAMP,
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35),
    uetr VARCHAR(36),

    -- Transaction
    transaction_id VARCHAR(35),
    clearing_system_reference VARCHAR(35),

    -- Amount
    instructed_amount DECIMAL(18,4),
    instructed_currency VARCHAR(3),

    -- Debtor
    debtor_name VARCHAR(140),
    debtor_account VARCHAR(34),
    debtor_agent_id VARCHAR(35),

    -- Creditor
    creditor_name VARCHAR(140),
    creditor_account VARCHAR(34),
    creditor_agent_id VARCHAR(35),

    -- Purpose
    purpose_code VARCHAR(4),

    -- Remittance
    remittance_info TEXT,

    -- Processing Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_gold_at TIMESTAMP,
    processing_error TEXT,

    source_raw_id VARCHAR(36),
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_rtp_msg ON silver.stg_rtp(msg_id);
CREATE INDEX IF NOT EXISTS idx_stg_rtp_e2e ON silver.stg_rtp(end_to_end_id);
CREATE INDEX IF NOT EXISTS idx_stg_rtp_status ON silver.stg_rtp(processing_status);

-- Verify tables
SELECT 'silver' as schema, table_name FROM information_schema.tables
WHERE table_schema = 'silver' ORDER BY table_name;
