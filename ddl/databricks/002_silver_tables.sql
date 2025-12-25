-- ============================================================================
-- GPS CDM - Silver Layer Tables (Normalized Staging)
-- ============================================================================
-- Silver tables contain cleansed, normalized data with data quality scores
-- Tables are organized by message type family with consistent structure
-- ============================================================================

USE CATALOG ${catalog};
USE SCHEMA ${schema};

-- ============================================================================
-- ISO 20022 PAIN (Payments Initiation) - Silver Layer
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver_pain001 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'pain.001',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,
    control_sum DECIMAL(18,5),
    initiating_party_name STRING,
    initiating_party_id STRING,

    -- Payment Information
    payment_info_id STRING,
    payment_method STRING,
    batch_booking BOOLEAN,
    requested_execution_date DATE,

    -- Payment Type
    service_level STRING,
    local_instrument STRING,
    category_purpose STRING,
    instruction_priority STRING,

    -- Debtor (Payer)
    debtor_name STRING,
    debtor_address_line1 STRING,
    debtor_address_line2 STRING,
    debtor_city STRING,
    debtor_postal_code STRING,
    debtor_country STRING,
    debtor_id_type STRING,
    debtor_id_value STRING,
    debtor_lei STRING,
    debtor_date_of_birth DATE,

    -- Debtor Account
    debtor_account_iban STRING,
    debtor_account_number STRING,
    debtor_account_type STRING,
    debtor_account_currency STRING,

    -- Debtor Agent
    debtor_agent_bic STRING,
    debtor_agent_name STRING,
    debtor_agent_clearing_id STRING,

    -- Transaction
    instruction_id STRING,
    end_to_end_id STRING,
    uetr STRING,

    -- Amounts
    instructed_amount DECIMAL(18,5),
    instructed_currency STRING,
    equivalent_amount DECIMAL(18,5),
    equivalent_currency STRING,
    exchange_rate DECIMAL(12,6),

    -- Charges
    charge_bearer STRING,
    charges_amount DECIMAL(18,5),
    charges_currency STRING,

    -- Creditor (Payee)
    creditor_name STRING,
    creditor_address_line1 STRING,
    creditor_address_line2 STRING,
    creditor_city STRING,
    creditor_postal_code STRING,
    creditor_country STRING,
    creditor_id_type STRING,
    creditor_id_value STRING,
    creditor_lei STRING,

    -- Creditor Account
    creditor_account_iban STRING,
    creditor_account_number STRING,
    creditor_account_type STRING,
    creditor_account_currency STRING,

    -- Creditor Agent
    creditor_agent_bic STRING,
    creditor_agent_name STRING,
    creditor_agent_clearing_id STRING,

    -- Ultimate Parties
    ultimate_debtor_name STRING,
    ultimate_debtor_id STRING,
    ultimate_creditor_name STRING,
    ultimate_creditor_id STRING,

    -- Purpose
    purpose_code STRING,
    purpose_proprietary STRING,

    -- Remittance
    remittance_unstructured STRING,
    remittance_creditor_reference STRING,
    remittance_document_type STRING,
    remittance_document_number STRING,
    remittance_document_date DATE,

    -- Regulatory
    regulatory_reporting_code STRING,
    regulatory_authority_name STRING,
    regulatory_authority_country STRING,

    -- Tax Information
    tax_debtor_id STRING,
    tax_creditor_id STRING,
    tax_total_amount DECIMAL(18,5),

    -- Metadata
    source_system STRING,
    file_name STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP,
    _processed_at TIMESTAMP DEFAULT current_timestamp(),

    -- Data Quality
    dq_score DECIMAL(5,4),
    dq_issues STRING,
    dq_completeness_score DECIMAL(5,4),
    dq_accuracy_score DECIMAL(5,4),
    dq_consistency_score DECIMAL(5,4)
)
USING DELTA
PARTITIONED BY (message_type);

CREATE TABLE IF NOT EXISTS silver_pain008 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'pain.008',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,
    control_sum DECIMAL(18,5),

    -- Payment Information
    payment_info_id STRING,
    payment_method STRING,
    requested_collection_date DATE,

    -- Payment Type
    service_level STRING,
    local_instrument STRING,
    sequence_type STRING,
    category_purpose STRING,

    -- Creditor (Collector)
    creditor_name STRING,
    creditor_address_line1 STRING,
    creditor_city STRING,
    creditor_postal_code STRING,
    creditor_country STRING,
    creditor_id STRING,

    -- Creditor Account
    creditor_account_iban STRING,
    creditor_account_number STRING,

    -- Creditor Agent
    creditor_agent_bic STRING,

    -- Creditor Scheme
    creditor_scheme_id STRING,
    creditor_scheme_name STRING,

    -- Mandate
    mandate_id STRING,
    mandate_date_of_signature DATE,
    amendment_indicator BOOLEAN,
    original_mandate_id STRING,
    original_creditor_scheme_id STRING,
    original_debtor_account STRING,
    original_debtor_agent STRING,

    -- Transaction
    instruction_id STRING,
    end_to_end_id STRING,

    -- Amounts
    instructed_amount DECIMAL(18,5),
    instructed_currency STRING,

    -- Debtor (Payer)
    debtor_name STRING,
    debtor_address_line1 STRING,
    debtor_city STRING,
    debtor_postal_code STRING,
    debtor_country STRING,
    debtor_id STRING,

    -- Debtor Account
    debtor_account_iban STRING,
    debtor_account_number STRING,

    -- Debtor Agent
    debtor_agent_bic STRING,

    -- Ultimate Parties
    ultimate_debtor_name STRING,
    ultimate_creditor_name STRING,

    -- Purpose & Remittance
    purpose_code STRING,
    remittance_info STRING,

    -- Metadata
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP,
    _processed_at TIMESTAMP DEFAULT current_timestamp(),
    dq_score DECIMAL(5,4),
    dq_issues STRING
)
USING DELTA
PARTITIONED BY (message_type);

-- ============================================================================
-- ISO 20022 PACS (Clearing & Settlement) - Silver Layer
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver_pacs008 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'pacs.008',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,

    -- Settlement
    settlement_method STRING,
    clearing_system STRING,
    interbank_settlement_date DATE,
    total_interbank_settlement_amount DECIMAL(18,5),
    total_interbank_settlement_currency STRING,

    -- Instructing/Instructed Agents
    instructing_agent_bic STRING,
    instructed_agent_bic STRING,

    -- Payment Type
    instruction_priority STRING,
    clearing_channel STRING,
    service_level STRING,
    local_instrument STRING,
    category_purpose STRING,

    -- Transaction IDs
    instruction_id STRING,
    end_to_end_id STRING,
    transaction_id STRING,
    uetr STRING,
    clearing_system_reference STRING,

    -- Amounts
    interbank_settlement_amount DECIMAL(18,5),
    interbank_settlement_currency STRING,
    instructed_amount DECIMAL(18,5),
    instructed_currency STRING,
    exchange_rate DECIMAL(12,6),

    -- Charges
    charge_bearer STRING,
    charges_amount DECIMAL(18,5),
    charges_currency STRING,
    charges_agent_bic STRING,

    -- Debtor
    debtor_name STRING,
    debtor_address_line1 STRING,
    debtor_address_line2 STRING,
    debtor_city STRING,
    debtor_postal_code STRING,
    debtor_country STRING,
    debtor_id STRING,
    debtor_lei STRING,

    -- Debtor Account
    debtor_account_iban STRING,
    debtor_account_number STRING,

    -- Debtor Agent
    debtor_agent_bic STRING,
    debtor_agent_name STRING,
    debtor_agent_clearing_id STRING,

    -- Creditor
    creditor_name STRING,
    creditor_address_line1 STRING,
    creditor_address_line2 STRING,
    creditor_city STRING,
    creditor_postal_code STRING,
    creditor_country STRING,
    creditor_id STRING,
    creditor_lei STRING,

    -- Creditor Account
    creditor_account_iban STRING,
    creditor_account_number STRING,

    -- Creditor Agent
    creditor_agent_bic STRING,
    creditor_agent_name STRING,
    creditor_agent_clearing_id STRING,

    -- Intermediary Agents
    intermediary_agent1_bic STRING,
    intermediary_agent1_name STRING,
    intermediary_agent2_bic STRING,
    intermediary_agent2_name STRING,
    intermediary_agent3_bic STRING,
    intermediary_agent3_name STRING,

    -- Ultimate Parties
    ultimate_debtor_name STRING,
    ultimate_debtor_id STRING,
    ultimate_creditor_name STRING,
    ultimate_creditor_id STRING,

    -- Purpose & Remittance
    purpose_code STRING,
    remittance_info STRING,
    remittance_creditor_reference STRING,

    -- Regulatory
    regulatory_reporting STRING,

    -- Metadata
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP,
    _processed_at TIMESTAMP DEFAULT current_timestamp(),
    dq_score DECIMAL(5,4),
    dq_issues STRING
)
USING DELTA
PARTITIONED BY (message_type);

CREATE TABLE IF NOT EXISTS silver_pacs004 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'pacs.004',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,

    -- Settlement
    settlement_method STRING,
    interbank_settlement_date DATE,

    -- Return Information
    return_id STRING,
    original_message_id STRING,
    original_message_type STRING,
    original_instruction_id STRING,
    original_end_to_end_id STRING,
    original_transaction_id STRING,
    original_uetr STRING,

    -- Return Reason
    return_reason_code STRING,
    return_reason_proprietary STRING,
    return_reason_info STRING,

    -- Returned Amount
    returned_interbank_settlement_amount DECIMAL(18,5),
    returned_interbank_settlement_currency STRING,

    -- Agents
    instructing_agent_bic STRING,
    instructed_agent_bic STRING,
    return_chain_bic STRING,

    -- Charge Bearer
    charge_bearer STRING,

    -- Metadata
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP,
    _processed_at TIMESTAMP DEFAULT current_timestamp(),
    dq_score DECIMAL(5,4),
    dq_issues STRING
)
USING DELTA
PARTITIONED BY (message_type);

CREATE TABLE IF NOT EXISTS silver_pacs002 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'pacs.002',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Original Message
    original_message_id STRING,
    original_message_type STRING,

    -- Status
    group_status STRING,
    transaction_status STRING,
    status_reason_code STRING,
    status_reason_proprietary STRING,
    status_reason_info STRING,

    -- Original Transaction
    original_instruction_id STRING,
    original_end_to_end_id STRING,
    original_transaction_id STRING,
    original_uetr STRING,

    -- Timing
    acceptance_datetime TIMESTAMP,

    -- Clearing Reference
    clearing_system_reference STRING,

    -- Metadata
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP,
    _processed_at TIMESTAMP DEFAULT current_timestamp(),
    dq_score DECIMAL(5,4),
    dq_issues STRING
)
USING DELTA
PARTITIONED BY (message_type);

-- ============================================================================
-- ISO 20022 CAMT (Cash Management) - Silver Layer
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver_camt053 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'camt.053',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Statement Info
    statement_id STRING,
    sequence_number STRING,
    legal_sequence_number STRING,
    from_date DATE,
    to_date DATE,

    -- Account
    account_iban STRING,
    account_number STRING,
    account_currency STRING,
    account_owner_name STRING,
    account_servicer_bic STRING,

    -- Opening Balance
    opening_balance_type STRING,
    opening_balance_amount DECIMAL(18,5),
    opening_balance_currency STRING,
    opening_balance_credit_debit STRING,
    opening_balance_date DATE,

    -- Closing Balance
    closing_balance_type STRING,
    closing_balance_amount DECIMAL(18,5),
    closing_balance_currency STRING,
    closing_balance_credit_debit STRING,
    closing_balance_date DATE,

    -- Summary
    number_of_entries INT,
    sum_of_entries DECIMAL(18,5),
    number_of_credit_entries INT,
    sum_of_credit_entries DECIMAL(18,5),
    number_of_debit_entries INT,
    sum_of_debit_entries DECIMAL(18,5),

    -- Metadata
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP,
    _processed_at TIMESTAMP DEFAULT current_timestamp(),
    dq_score DECIMAL(5,4),
    dq_issues STRING
)
USING DELTA
PARTITIONED BY (message_type);

CREATE TABLE IF NOT EXISTS silver_camt053_entries (
    entry_id STRING NOT NULL,
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,

    -- Entry Details
    entry_reference STRING,
    entry_amount DECIMAL(18,5),
    entry_currency STRING,
    entry_credit_debit STRING,
    entry_status STRING,
    booking_date DATE,
    value_date DATE,

    -- Transaction Details
    end_to_end_id STRING,
    instruction_id STRING,
    transaction_id STRING,

    -- Related Parties
    debtor_name STRING,
    debtor_account STRING,
    creditor_name STRING,
    creditor_account STRING,

    -- Remittance
    remittance_info STRING,

    -- Metadata
    _batch_id STRING,
    _processed_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(booking_date));

-- ============================================================================
-- SWIFT MT - Silver Layer
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver_mt103 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'MT103',

    -- Header
    sender_bic STRING,
    receiver_bic STRING,
    message_priority STRING,

    -- Transaction Reference
    transaction_reference STRING,
    bank_operation_code STRING,

    -- Value Date & Amount
    value_date DATE,
    currency STRING,
    amount DECIMAL(18,5),

    -- Instructed Amount
    instructed_currency STRING,
    instructed_amount DECIMAL(18,5),
    exchange_rate DECIMAL(12,6),

    -- Ordering Customer (Debtor)
    ordering_customer_account STRING,
    ordering_customer_name STRING,
    ordering_customer_address STRING,

    -- Ordering Institution
    ordering_institution_bic STRING,

    -- Correspondent Banks
    senders_correspondent_bic STRING,
    receivers_correspondent_bic STRING,
    intermediary_bic STRING,
    account_with_institution_bic STRING,

    -- Beneficiary Customer (Creditor)
    beneficiary_customer_account STRING,
    beneficiary_customer_name STRING,
    beneficiary_customer_address STRING,

    -- Remittance
    remittance_information STRING,

    -- Charges
    details_of_charges STRING,
    senders_charges_currency STRING,
    senders_charges_amount DECIMAL(18,5),
    receivers_charges_currency STRING,
    receivers_charges_amount DECIMAL(18,5),

    -- Additional Info
    sender_to_receiver_info STRING,
    regulatory_reporting STRING,

    -- gSPI
    uetr STRING,

    -- Metadata
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP,
    _processed_at TIMESTAMP DEFAULT current_timestamp(),
    dq_score DECIMAL(5,4),
    dq_issues STRING
)
USING DELTA
PARTITIONED BY (message_type);

CREATE TABLE IF NOT EXISTS silver_mt202 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'MT202',

    -- Header
    sender_bic STRING,
    receiver_bic STRING,

    -- References
    transaction_reference STRING,
    related_reference STRING,

    -- Value Date & Amount
    value_date DATE,
    currency STRING,
    amount DECIMAL(18,5),

    -- Agents
    ordering_institution_bic STRING,
    senders_correspondent_bic STRING,
    receivers_correspondent_bic STRING,
    intermediary_bic STRING,
    account_with_institution_bic STRING,
    beneficiary_institution_bic STRING,

    -- Additional Info
    sender_to_receiver_info STRING,

    -- gSPI
    uetr STRING,

    -- Metadata
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP,
    _processed_at TIMESTAMP DEFAULT current_timestamp(),
    dq_score DECIMAL(5,4),
    dq_issues STRING
)
USING DELTA
PARTITIONED BY (message_type);

-- ============================================================================
-- Domestic Schemes - Silver Layer
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver_sepa_sct (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'SEPA_SCT',

    -- Message Info
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,
    control_sum DECIMAL(18,5),

    -- Payment Info
    payment_info_id STRING,
    payment_method STRING,
    requested_execution_date DATE,

    -- Debtor
    debtor_name STRING,
    debtor_iban STRING,
    debtor_bic STRING,

    -- Transaction
    instruction_id STRING,
    end_to_end_id STRING,
    instructed_amount DECIMAL(18,5),

    -- Creditor
    creditor_name STRING,
    creditor_iban STRING,
    creditor_bic STRING,

    -- Additional
    charge_bearer STRING,
    purpose_code STRING,
    remittance_info STRING,

    -- Metadata
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP,
    _processed_at TIMESTAMP DEFAULT current_timestamp(),
    dq_score DECIMAL(5,4),
    dq_issues STRING
)
USING DELTA
PARTITIONED BY (message_type);

CREATE TABLE IF NOT EXISTS silver_nacha_ach (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'NACHA_ACH',

    -- Batch Info
    company_name STRING,
    company_id STRING,
    standard_entry_class STRING,
    company_entry_description STRING,
    effective_entry_date DATE,

    -- Transaction
    transaction_code STRING,
    trace_number STRING,

    -- Originator
    originating_dfi_id STRING,

    -- Receiver
    receiving_dfi_id STRING,
    receiving_dfi_account STRING,

    -- Amount
    amount DECIMAL(18,5),

    -- Individual
    individual_id STRING,
    individual_name STRING,

    -- Addenda
    discretionary_data STRING,
    addenda_type_code STRING,
    payment_related_info STRING,

    -- Metadata
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP,
    _processed_at TIMESTAMP DEFAULT current_timestamp(),
    dq_score DECIMAL(5,4),
    dq_issues STRING
)
USING DELTA
PARTITIONED BY (message_type);

CREATE TABLE IF NOT EXISTS silver_fedwire (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'FEDWIRE',

    -- Message Info
    imad STRING,
    omad STRING,
    type_subtype STRING,
    business_function_code STRING,

    -- Sender/Receiver
    sender_aba STRING,
    sender_short_name STRING,
    receiver_aba STRING,
    receiver_short_name STRING,

    -- Amount
    amount DECIMAL(18,5),

    -- References
    sender_reference STRING,
    previous_message_id STRING,

    -- Originator
    originator_name STRING,
    originator_address STRING,
    originator_id STRING,
    originator_fi_name STRING,
    originator_fi_id STRING,

    -- Instructing FI
    instructing_fi_name STRING,
    instructing_fi_id STRING,

    -- Beneficiary FI
    beneficiary_fi_name STRING,
    beneficiary_fi_id STRING,

    -- Beneficiary
    beneficiary_name STRING,
    beneficiary_address STRING,
    beneficiary_id STRING,

    -- Additional Info
    originator_to_beneficiary_info STRING,
    fi_to_fi_info STRING,

    -- Metadata
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP,
    _processed_at TIMESTAMP DEFAULT current_timestamp(),
    dq_score DECIMAL(5,4),
    dq_issues STRING
)
USING DELTA
PARTITIONED BY (message_type);

-- ============================================================================
-- Real-Time Payments - Silver Layer
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver_fednow (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'FEDNOW',

    -- Message Info
    message_id STRING,
    creation_datetime TIMESTAMP,
    settlement_method STRING,
    interbank_settlement_date DATE,

    -- Amount
    interbank_settlement_amount DECIMAL(18,5),
    interbank_settlement_currency STRING,

    -- Agents
    instructing_agent_routing STRING,
    instructed_agent_routing STRING,

    -- Transaction IDs
    end_to_end_id STRING,
    transaction_id STRING,
    uetr STRING,

    -- Debtor
    debtor_name STRING,
    debtor_account STRING,
    debtor_agent_routing STRING,

    -- Creditor
    creditor_name STRING,
    creditor_account STRING,
    creditor_agent_routing STRING,

    -- Purpose & Remittance
    purpose_code STRING,
    remittance_info STRING,

    -- Fraud Detection
    fraud_score INT,
    fraud_risk_level STRING,

    -- Timing
    acceptance_datetime TIMESTAMP,

    -- Metadata
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP,
    _processed_at TIMESTAMP DEFAULT current_timestamp(),
    dq_score DECIMAL(5,4),
    dq_issues STRING
)
USING DELTA
PARTITIONED BY (message_type);

CREATE TABLE IF NOT EXISTS silver_pix (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'PIX',

    -- Transaction Info
    end_to_end_id STRING,
    creation_datetime TIMESTAMP,
    local_instrument STRING,

    -- Payer
    payer_ispb STRING,
    payer_branch STRING,
    payer_account STRING,
    payer_account_type STRING,
    payer_name STRING,
    payer_cpf_cnpj STRING,
    payer_pix_key STRING,
    payer_pix_key_type STRING,

    -- Payee
    payee_ispb STRING,
    payee_branch STRING,
    payee_account STRING,
    payee_account_type STRING,
    payee_name STRING,
    payee_cpf_cnpj STRING,
    payee_pix_key STRING,
    payee_pix_key_type STRING,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Transaction Type
    qr_code_type STRING,
    initiation_type STRING,
    payment_type STRING,

    -- Remittance
    remittance_info STRING,

    -- Fraud Detection
    fraud_score INT,

    -- Metadata
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP,
    _processed_at TIMESTAMP DEFAULT current_timestamp(),
    dq_score DECIMAL(5,4),
    dq_issues STRING
)
USING DELTA
PARTITIONED BY (message_type);

CREATE TABLE IF NOT EXISTS silver_rtp (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'RTP',

    -- Message Info
    message_id STRING,
    creation_datetime TIMESTAMP,
    settlement_date DATE,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Sender
    sender_routing_number STRING,
    sender_account STRING,
    sender_name STRING,

    -- Receiver
    receiver_routing_number STRING,
    receiver_account STRING,
    receiver_name STRING,

    -- Transaction IDs
    end_to_end_id STRING,
    uetr STRING,

    -- Remittance
    remittance_info STRING,

    -- Timing
    acceptance_datetime TIMESTAMP,

    -- Metadata
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP,
    _processed_at TIMESTAMP DEFAULT current_timestamp(),
    dq_score DECIMAL(5,4),
    dq_issues STRING
)
USING DELTA
PARTITIONED BY (message_type);

-- ============================================================================
-- Unified Silver View (for cross-message-type queries)
-- ============================================================================

CREATE OR REPLACE VIEW silver_payments_unified AS
SELECT
    stg_id,
    raw_id,
    message_type,
    message_id,
    creation_datetime,
    instructed_amount AS amount,
    instructed_currency AS currency,
    debtor_name,
    debtor_account_iban AS debtor_account,
    debtor_agent_bic,
    creditor_name,
    creditor_account_iban AS creditor_account,
    creditor_agent_bic,
    end_to_end_id,
    uetr,
    purpose_code,
    charge_bearer,
    dq_score,
    _batch_id,
    _processed_at
FROM silver_pain001

UNION ALL

SELECT
    stg_id,
    raw_id,
    message_type,
    message_id,
    creation_datetime,
    interbank_settlement_amount AS amount,
    interbank_settlement_currency AS currency,
    debtor_name,
    debtor_account_iban AS debtor_account,
    debtor_agent_bic,
    creditor_name,
    creditor_account_iban AS creditor_account,
    creditor_agent_bic,
    end_to_end_id,
    uetr,
    purpose_code,
    charge_bearer,
    dq_score,
    _batch_id,
    _processed_at
FROM silver_pacs008

UNION ALL

SELECT
    stg_id,
    raw_id,
    message_type,
    transaction_reference AS message_id,
    NULL AS creation_datetime,
    amount,
    currency,
    ordering_customer_name AS debtor_name,
    ordering_customer_account AS debtor_account,
    ordering_institution_bic AS debtor_agent_bic,
    beneficiary_customer_name AS creditor_name,
    beneficiary_customer_account AS creditor_account,
    account_with_institution_bic AS creditor_agent_bic,
    transaction_reference AS end_to_end_id,
    uetr,
    NULL AS purpose_code,
    details_of_charges AS charge_bearer,
    dq_score,
    _batch_id,
    _processed_at
FROM silver_mt103;
