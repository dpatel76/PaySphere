-- GPS CDM - Gold Layer Extension Tables
-- ======================================
-- Scheme-specific extension tables for normalized design.
-- Each payment scheme has its own extension table linked to cdm_payment_instruction.

-- =====================================================
-- Common Fields Addition to cdm_payment_instruction
-- =====================================================
-- Add commonly used fields that apply across multiple schemes

ALTER TABLE gold.cdm_payment_instruction
    ADD COLUMN IF NOT EXISTS number_of_transactions INTEGER,
    ADD COLUMN IF NOT EXISTS control_sum DECIMAL(18,4),
    ADD COLUMN IF NOT EXISTS batch_booking BOOLEAN,
    ADD COLUMN IF NOT EXISTS payment_method VARCHAR(10),
    ADD COLUMN IF NOT EXISTS clearing_system VARCHAR(10),
    ADD COLUMN IF NOT EXISTS clearing_system_reference VARCHAR(50),
    ADD COLUMN IF NOT EXISTS sender_to_receiver_info TEXT;

COMMENT ON COLUMN gold.cdm_payment_instruction.number_of_transactions IS 'Number of transactions in batch';
COMMENT ON COLUMN gold.cdm_payment_instruction.control_sum IS 'Total amount of all transactions in batch';
COMMENT ON COLUMN gold.cdm_payment_instruction.batch_booking IS 'Indicates batch booking preference';
COMMENT ON COLUMN gold.cdm_payment_instruction.payment_method IS 'Payment method code (TRF, CHK, etc.)';
COMMENT ON COLUMN gold.cdm_payment_instruction.clearing_system IS 'Clearing system code';
COMMENT ON COLUMN gold.cdm_payment_instruction.clearing_system_reference IS 'Reference assigned by clearing system';
COMMENT ON COLUMN gold.cdm_payment_instruction.sender_to_receiver_info IS 'Bank-to-bank information';


-- =====================================================
-- FEDWIRE Extension Table
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_payment_extension_fedwire (
    extension_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    instruction_id VARCHAR(36) NOT NULL REFERENCES gold.cdm_payment_instruction(instruction_id) ON DELETE CASCADE,

    -- Wire Type Classification
    wire_type_code VARCHAR(10),                    -- Type/Subtype Code
    wire_subtype_code VARCHAR(10),

    -- Message References
    imad VARCHAR(50),                              -- Input Message Accountability Data
    omad VARCHAR(50),                              -- Output Message Accountability Data
    previous_imad VARCHAR(50),                     -- For related messages

    -- FI to FI Information
    fi_to_fi_info TEXT,                            -- Field 6000
    beneficiary_reference VARCHAR(35),             -- Beneficiary reference

    -- Input Processing
    input_cycle_date DATE,
    input_sequence_number VARCHAR(20),
    input_source VARCHAR(20),

    -- Originator/Beneficiary ID Details
    originator_id_type VARCHAR(10),                -- ID type code
    originator_option_f TEXT,                      -- Full Option F content
    beneficiary_id_type VARCHAR(10),

    -- Charges
    charges TEXT,                                  -- Charges information

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_fedwire_instruction UNIQUE (instruction_id)
);

CREATE INDEX IF NOT EXISTS idx_fedwire_ext_imad ON gold.cdm_payment_extension_fedwire(imad);
CREATE INDEX IF NOT EXISTS idx_fedwire_ext_omad ON gold.cdm_payment_extension_fedwire(omad);
CREATE INDEX IF NOT EXISTS idx_fedwire_ext_wire_type ON gold.cdm_payment_extension_fedwire(wire_type_code, wire_subtype_code);

COMMENT ON TABLE gold.cdm_payment_extension_fedwire IS 'FEDWIRE-specific payment attributes';


-- =====================================================
-- ACH Extension Table
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_payment_extension_ach (
    extension_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    instruction_id VARCHAR(36) NOT NULL REFERENCES gold.cdm_payment_instruction(instruction_id) ON DELETE CASCADE,

    -- File Header Fields
    immediate_destination VARCHAR(10),
    immediate_origin VARCHAR(10),
    file_creation_date DATE,
    file_creation_time VARCHAR(4),
    file_id_modifier VARCHAR(1),

    -- Batch Header Fields
    standard_entry_class VARCHAR(3),               -- CCD, PPD, CTX, WEB, TEL, etc.
    company_entry_description VARCHAR(10),
    batch_number INTEGER,
    originator_status_code VARCHAR(1),

    -- Entry Detail Fields
    transaction_code VARCHAR(2),                   -- 22, 23, 27, 28, 32, 33, 37, 38
    originating_dfi_id VARCHAR(8),
    receiving_dfi_id VARCHAR(8),
    individual_id VARCHAR(15),
    discretionary_data VARCHAR(2),

    -- Addenda Fields
    addenda_indicator VARCHAR(1),
    addenda_type VARCHAR(2),
    addenda_info TEXT,

    -- Return Fields
    return_reason_code VARCHAR(3),
    original_entry_trace VARCHAR(15),
    date_of_death DATE,
    original_receiving_dfi VARCHAR(8),

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_ach_instruction UNIQUE (instruction_id)
);

CREATE INDEX IF NOT EXISTS idx_ach_ext_sec ON gold.cdm_payment_extension_ach(standard_entry_class);
CREATE INDEX IF NOT EXISTS idx_ach_ext_originating_dfi ON gold.cdm_payment_extension_ach(originating_dfi_id);
CREATE INDEX IF NOT EXISTS idx_ach_ext_receiving_dfi ON gold.cdm_payment_extension_ach(receiving_dfi_id);
CREATE INDEX IF NOT EXISTS idx_ach_ext_return_reason ON gold.cdm_payment_extension_ach(return_reason_code) WHERE return_reason_code IS NOT NULL;

COMMENT ON TABLE gold.cdm_payment_extension_ach IS 'NACHA ACH-specific payment attributes';


-- =====================================================
-- SEPA Extension Table
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_payment_extension_sepa (
    extension_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    instruction_id VARCHAR(36) NOT NULL REFERENCES gold.cdm_payment_instruction(instruction_id) ON DELETE CASCADE,

    -- SEPA Scheme Info
    sepa_message_type VARCHAR(35),                 -- pain.001.001.09, pain.008.001.08, etc.
    sepa_scheme VARCHAR(4),                        -- CORE, B2B, INST

    -- Settlement
    settlement_method VARCHAR(4),                  -- CLRG, INGA, etc.

    -- Direct Debit Mandate
    mandate_id VARCHAR(35),
    mandate_date DATE,
    sequence_type VARCHAR(4),                      -- FRST, RCUR, FNAL, OOFF
    creditor_scheme_id VARCHAR(35),                -- Creditor Identifier

    -- Amendment Info (for mandate changes)
    amendment_indicator BOOLEAN DEFAULT FALSE,
    original_mandate_id VARCHAR(35),
    original_creditor_scheme_id VARCHAR(35),
    original_debtor_account VARCHAR(34),
    original_debtor_agent VARCHAR(11),

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_sepa_instruction UNIQUE (instruction_id)
);

CREATE INDEX IF NOT EXISTS idx_sepa_ext_scheme ON gold.cdm_payment_extension_sepa(sepa_scheme);
CREATE INDEX IF NOT EXISTS idx_sepa_ext_mandate ON gold.cdm_payment_extension_sepa(mandate_id) WHERE mandate_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_sepa_ext_creditor_scheme ON gold.cdm_payment_extension_sepa(creditor_scheme_id) WHERE creditor_scheme_id IS NOT NULL;

COMMENT ON TABLE gold.cdm_payment_extension_sepa IS 'SEPA-specific payment attributes';


-- =====================================================
-- SWIFT MT Extension Table
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_payment_extension_swift (
    extension_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    instruction_id VARCHAR(36) NOT NULL REFERENCES gold.cdm_payment_instruction(instruction_id) ON DELETE CASCADE,

    -- Message Header
    swift_message_type VARCHAR(10),                -- MT103, MT202, MT202COV, etc.
    sender_bic VARCHAR(11),
    receiver_bic VARCHAR(11),
    message_priority VARCHAR(1),                   -- S, U, N

    -- Correspondent Banks
    senders_correspondent_bic VARCHAR(11),
    senders_correspondent_account VARCHAR(34),
    senders_correspondent_location VARCHAR(35),
    receivers_correspondent_bic VARCHAR(11),
    receivers_correspondent_account VARCHAR(34),
    receivers_correspondent_location VARCHAR(35),
    third_reimbursement_bic VARCHAR(11),

    -- Ordering/Intermediary Institutions
    ordering_institution_bic VARCHAR(11),
    ordering_institution_account VARCHAR(34),
    account_with_institution_bic VARCHAR(11),
    account_with_institution_account VARCHAR(34),

    -- Charges
    sender_charges_amount DECIMAL(18,4),
    sender_charges_currency VARCHAR(3),
    receiver_charges_amount DECIMAL(18,4),
    receiver_charges_currency VARCHAR(3),

    -- Additional Info
    sender_to_receiver_information TEXT,           -- Field 72
    envelope_contents TEXT,                        -- Full envelope if needed
    regulatory_reporting TEXT,                     -- Field 77B

    -- Instruction Codes
    instruction_codes VARCHAR(100),                -- Field 23E codes

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_swift_instruction UNIQUE (instruction_id)
);

CREATE INDEX IF NOT EXISTS idx_swift_ext_msg_type ON gold.cdm_payment_extension_swift(swift_message_type);
CREATE INDEX IF NOT EXISTS idx_swift_ext_sender ON gold.cdm_payment_extension_swift(sender_bic);
CREATE INDEX IF NOT EXISTS idx_swift_ext_receiver ON gold.cdm_payment_extension_swift(receiver_bic);

COMMENT ON TABLE gold.cdm_payment_extension_swift IS 'SWIFT MT message-specific payment attributes';


-- =====================================================
-- RTP Extension Table
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_payment_extension_rtp (
    extension_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    instruction_id VARCHAR(36) NOT NULL REFERENCES gold.cdm_payment_instruction(instruction_id) ON DELETE CASCADE,

    -- RTP Network Info
    rtp_message_type VARCHAR(35),                  -- pacs.008, pacs.002, etc.

    -- Agent Routing Numbers
    debtor_agent_rtn VARCHAR(9),
    creditor_agent_rtn VARCHAR(9),

    -- Request for Payment (RfP) fields
    rfp_reference VARCHAR(35),
    rfp_expiry_datetime TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_rtp_instruction UNIQUE (instruction_id)
);

CREATE INDEX IF NOT EXISTS idx_rtp_ext_debtor_rtn ON gold.cdm_payment_extension_rtp(debtor_agent_rtn);
CREATE INDEX IF NOT EXISTS idx_rtp_ext_creditor_rtn ON gold.cdm_payment_extension_rtp(creditor_agent_rtn);

COMMENT ON TABLE gold.cdm_payment_extension_rtp IS 'TCH RTP-specific payment attributes';


-- =====================================================
-- ISO 20022 Extension Table (for pain.001, pacs.008, etc.)
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_payment_extension_iso20022 (
    extension_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    instruction_id VARCHAR(36) NOT NULL REFERENCES gold.cdm_payment_instruction(instruction_id) ON DELETE CASCADE,

    -- Message Info
    message_definition VARCHAR(50),                -- pain.001.001.09, pacs.008.001.08
    message_namespace VARCHAR(100),

    -- Group Header
    payment_info_id VARCHAR(35),
    initiating_party_name VARCHAR(140),
    initiating_party_id VARCHAR(35),

    -- Payment Type Information
    instruction_priority VARCHAR(10),              -- HIGH, NORM
    clearing_channel VARCHAR(10),                  -- RTGS, RTNS, etc.

    -- Regulatory Reporting
    regulatory_reporting_code VARCHAR(10),
    regulatory_reporting_amount DECIMAL(18,4),
    regulatory_reporting_currency VARCHAR(3),
    regulatory_reporting_info TEXT,

    -- Structured Remittance (beyond what fits in main table)
    creditor_reference VARCHAR(35),
    creditor_reference_type VARCHAR(35),
    invoices JSONB,                               -- Array of invoice references

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_iso20022_instruction UNIQUE (instruction_id)
);

CREATE INDEX IF NOT EXISTS idx_iso20022_ext_msg_def ON gold.cdm_payment_extension_iso20022(message_definition);
CREATE INDEX IF NOT EXISTS idx_iso20022_ext_payment_info ON gold.cdm_payment_extension_iso20022(payment_info_id);

COMMENT ON TABLE gold.cdm_payment_extension_iso20022 IS 'ISO 20022 message-specific payment attributes';


-- =====================================================
-- View: Unified Payment with Extensions
-- =====================================================
CREATE OR REPLACE VIEW gold.vw_payment_with_extensions AS
SELECT
    pi.*,
    -- FEDWIRE
    fw.wire_type_code,
    fw.wire_subtype_code,
    fw.imad,
    fw.omad,
    fw.fi_to_fi_info AS fedwire_fi_info,
    -- ACH
    ach.standard_entry_class,
    ach.transaction_code AS ach_transaction_code,
    ach.originating_dfi_id,
    ach.receiving_dfi_id,
    ach.addenda_info,
    ach.return_reason_code,
    -- SEPA
    sepa.sepa_scheme,
    sepa.mandate_id,
    sepa.sequence_type,
    sepa.creditor_scheme_id,
    -- SWIFT
    swift.swift_message_type,
    swift.sender_bic,
    swift.receiver_bic,
    swift.instruction_codes,
    -- RTP
    rtp.debtor_agent_rtn,
    rtp.creditor_agent_rtn,
    -- ISO 20022
    iso.message_definition,
    iso.payment_info_id,
    iso.creditor_reference
FROM gold.cdm_payment_instruction pi
LEFT JOIN gold.cdm_payment_extension_fedwire fw ON pi.instruction_id = fw.instruction_id
LEFT JOIN gold.cdm_payment_extension_ach ach ON pi.instruction_id = ach.instruction_id
LEFT JOIN gold.cdm_payment_extension_sepa sepa ON pi.instruction_id = sepa.instruction_id
LEFT JOIN gold.cdm_payment_extension_swift swift ON pi.instruction_id = swift.instruction_id
LEFT JOIN gold.cdm_payment_extension_rtp rtp ON pi.instruction_id = rtp.instruction_id
LEFT JOIN gold.cdm_payment_extension_iso20022 iso ON pi.instruction_id = iso.instruction_id;

COMMENT ON VIEW gold.vw_payment_with_extensions IS 'Denormalized view of payments with all scheme-specific extensions';
