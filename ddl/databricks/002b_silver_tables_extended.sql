-- ============================================================================
-- GPS CDM - Silver Layer Extended Tables (All 72+ Standards)
-- ============================================================================
-- This file extends the base Silver layer with tables for all payment standards
-- Run after 002_silver_tables.sql
-- ============================================================================

USE CATALOG ${catalog};
USE SCHEMA ${schema};

-- ============================================================================
-- ISO 20022 PAIN (Payments Initiation) - Additional Silver Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver_pain002 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'pain.002',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Original Message Reference
    original_message_id STRING,
    original_message_type STRING,
    original_creation_datetime TIMESTAMP,

    -- Status Information
    group_status STRING,
    status_reason_code STRING,
    status_reason_proprietary STRING,
    status_additional_info STRING,

    -- Original Transaction Reference
    original_payment_info_id STRING,
    original_instruction_id STRING,
    original_end_to_end_id STRING,
    transaction_status STRING,

    -- Initiating Party
    initiating_party_name STRING,
    initiating_party_id STRING,

    -- Debtor
    debtor_name STRING,
    debtor_account_iban STRING,
    debtor_agent_bic STRING,

    -- Creditor
    creditor_name STRING,
    creditor_account_iban STRING,
    creditor_agent_bic STRING,

    -- Amounts
    original_instructed_amount DECIMAL(18,5),
    original_instructed_currency STRING,

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

CREATE TABLE IF NOT EXISTS silver_pain007 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'pain.007',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Reversal Info
    original_message_id STRING,
    original_message_type STRING,
    original_payment_info_id STRING,
    original_instruction_id STRING,
    original_end_to_end_id STRING,

    -- Reversal Reason
    reversal_reason_code STRING,
    reversal_reason_proprietary STRING,
    reversal_additional_info STRING,

    -- Original Transaction
    original_amount DECIMAL(18,5),
    original_currency STRING,
    original_debtor_name STRING,
    original_creditor_name STRING,

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

CREATE TABLE IF NOT EXISTS silver_pain013 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'pain.013',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,
    control_sum DECIMAL(18,5),

    -- Initiating Party
    initiating_party_name STRING,
    initiating_party_id STRING,

    -- Request Type
    request_type STRING,

    -- Mandate Request Info
    mandate_request_id STRING,
    mandate_type STRING,
    occurrence_type STRING,

    -- Debtor
    debtor_name STRING,
    debtor_address STRING,
    debtor_country STRING,
    debtor_account_iban STRING,
    debtor_agent_bic STRING,

    -- Creditor
    creditor_name STRING,
    creditor_id STRING,
    creditor_scheme_id STRING,
    creditor_scheme_name STRING,
    creditor_account_iban STRING,
    creditor_agent_bic STRING,

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

CREATE TABLE IF NOT EXISTS silver_pain014 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'pain.014',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Original Mandate Reference
    original_mandate_request_id STRING,

    -- Status
    mandate_status STRING,
    status_reason_code STRING,
    status_reason_info STRING,

    -- Accepted Mandate Info
    mandate_id STRING,
    mandate_date_of_signature DATE,

    -- Debtor
    debtor_name STRING,
    debtor_account_iban STRING,
    debtor_agent_bic STRING,

    -- Creditor
    creditor_name STRING,
    creditor_id STRING,
    creditor_scheme_id STRING,

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
-- ISO 20022 PACS (Clearing & Settlement) - Additional Silver Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver_pacs003 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'pacs.003',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,

    -- Settlement Info
    settlement_method STRING,
    clearing_system STRING,
    interbank_settlement_date DATE,

    -- Direct Debit Transaction
    payment_id STRING,
    instruction_id STRING,
    end_to_end_id STRING,

    -- Amount
    instructed_amount DECIMAL(18,5),
    instructed_currency STRING,
    interbank_settlement_amount DECIMAL(18,5),
    interbank_settlement_currency STRING,

    -- Mandate
    mandate_id STRING,

    -- Creditor (Collector)
    creditor_name STRING,
    creditor_account_iban STRING,
    creditor_agent_bic STRING,
    creditor_scheme_id STRING,

    -- Debtor
    debtor_name STRING,
    debtor_account_iban STRING,
    debtor_agent_bic STRING,

    -- Agents
    instructing_agent_bic STRING,
    instructed_agent_bic STRING,

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

CREATE TABLE IF NOT EXISTS silver_pacs007 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'pacs.007',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,

    -- Reversal Info
    original_message_id STRING,
    original_message_type STRING,
    original_instruction_id STRING,
    original_end_to_end_id STRING,
    original_transaction_id STRING,
    original_interbank_settlement_date DATE,

    -- Reversal Reason
    reversal_reason_code STRING,
    reversal_reason_info STRING,

    -- Reversed Amount
    reversed_interbank_settlement_amount DECIMAL(18,5),
    reversed_interbank_settlement_currency STRING,

    -- Agents
    instructing_agent_bic STRING,
    instructed_agent_bic STRING,

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

CREATE TABLE IF NOT EXISTS silver_pacs009 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'pacs.009',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,

    -- Settlement
    settlement_method STRING,
    interbank_settlement_date DATE,

    -- Financial Institution Credit Transfer
    instruction_id STRING,
    end_to_end_id STRING,
    transaction_id STRING,
    uetr STRING,

    -- Amount
    interbank_settlement_amount DECIMAL(18,5),
    interbank_settlement_currency STRING,

    -- Agents
    instructing_agent_bic STRING,
    instructed_agent_bic STRING,
    debtor_agent_bic STRING,
    creditor_agent_bic STRING,
    intermediary_agent1_bic STRING,
    intermediary_agent2_bic STRING,

    -- Underlying Customer Transaction
    underlying_instruction_id STRING,
    underlying_end_to_end_id STRING,
    underlying_debtor_name STRING,
    underlying_creditor_name STRING,

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

CREATE TABLE IF NOT EXISTS silver_pacs028 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'pacs.028',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Status Request Info
    original_message_id STRING,
    original_message_type STRING,
    original_creation_datetime TIMESTAMP,

    -- Transaction to Request Status
    original_instruction_id STRING,
    original_end_to_end_id STRING,
    original_transaction_id STRING,
    original_uetr STRING,

    -- Request Type
    status_request_type STRING,

    -- Agents
    instructing_agent_bic STRING,
    instructed_agent_bic STRING,

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
-- ISO 20022 CAMT (Cash Management) - Additional Silver Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver_camt026 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'camt.026',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Unable To Apply Info
    case_id STRING,
    case_creator STRING,

    -- Original Transaction
    original_message_id STRING,
    original_message_type STRING,
    original_instruction_id STRING,
    original_end_to_end_id STRING,
    original_uetr STRING,

    -- Missing/Incorrect Info
    missing_or_incorrect_info_code STRING,
    missing_or_incorrect_info_text STRING,

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

CREATE TABLE IF NOT EXISTS silver_camt027 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'camt.027',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Claim Info
    case_id STRING,
    case_creator STRING,

    -- Original Transaction
    original_message_id STRING,
    original_instruction_id STRING,
    original_end_to_end_id STRING,
    original_uetr STRING,

    -- Claim Type
    claim_type STRING,
    claim_reason_code STRING,
    claim_additional_info STRING,

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

CREATE TABLE IF NOT EXISTS silver_camt029 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'camt.029',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Resolution Info
    case_id STRING,
    case_creator STRING,
    resolution_status STRING,

    -- Original Transaction
    original_message_id STRING,
    original_instruction_id STRING,
    original_end_to_end_id STRING,
    original_uetr STRING,

    -- Cancellation Details
    cancellation_status STRING,
    cancellation_reason_code STRING,

    -- Refund Info
    refund_amount DECIMAL(18,5),
    refund_currency STRING,

    -- Charges
    charges_amount DECIMAL(18,5),
    charges_currency STRING,

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

CREATE TABLE IF NOT EXISTS silver_camt052 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'camt.052',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Report Info
    report_id STRING,
    sequence_number STRING,
    from_datetime TIMESTAMP,
    to_datetime TIMESTAMP,

    -- Account
    account_iban STRING,
    account_number STRING,
    account_currency STRING,
    account_owner_name STRING,
    account_servicer_bic STRING,

    -- Balance
    balance_type STRING,
    balance_amount DECIMAL(18,5),
    balance_currency STRING,
    balance_credit_debit STRING,
    balance_datetime TIMESTAMP,

    -- Entry Summary
    number_of_entries INT,
    sum_of_entries DECIMAL(18,5),

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

CREATE TABLE IF NOT EXISTS silver_camt054 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'camt.054',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Notification Info
    notification_id STRING,
    notification_pagination STRING,

    -- Account
    account_iban STRING,
    account_number STRING,
    account_currency STRING,

    -- Entry
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
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP,
    _processed_at TIMESTAMP DEFAULT current_timestamp(),
    dq_score DECIMAL(5,4),
    dq_issues STRING
)
USING DELTA
PARTITIONED BY (message_type);

CREATE TABLE IF NOT EXISTS silver_camt055 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'camt.055',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,

    -- Cancellation Request
    case_id STRING,
    case_creator STRING,

    -- Original Transaction
    original_message_id STRING,
    original_message_type STRING,
    original_creation_datetime TIMESTAMP,
    original_instruction_id STRING,
    original_end_to_end_id STRING,
    original_uetr STRING,

    -- Cancellation Reason
    cancellation_reason_code STRING,
    cancellation_reason_info STRING,

    -- Original Transaction Details
    original_amount DECIMAL(18,5),
    original_currency STRING,
    original_debtor_name STRING,
    original_creditor_name STRING,

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

CREATE TABLE IF NOT EXISTS silver_camt056 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'camt.056',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- FI to FI Cancellation Request
    case_id STRING,
    case_creator STRING,

    -- Original Transaction
    original_message_id STRING,
    original_message_type STRING,
    original_instruction_id STRING,
    original_end_to_end_id STRING,
    original_transaction_id STRING,
    original_uetr STRING,
    original_interbank_settlement_date DATE,

    -- Cancellation Reason
    cancellation_reason_code STRING,
    cancellation_reason_info STRING,

    -- Original Amount
    original_interbank_settlement_amount DECIMAL(18,5),
    original_interbank_settlement_currency STRING,

    -- Agents
    instructing_agent_bic STRING,
    instructed_agent_bic STRING,

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

CREATE TABLE IF NOT EXISTS silver_camt057 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'camt.057',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Notification to Receive
    notification_id STRING,

    -- Expected Amount
    expected_value_date DATE,
    expected_amount DECIMAL(18,5),
    expected_currency STRING,

    -- Debtor Info
    debtor_name STRING,
    debtor_account STRING,
    debtor_agent_bic STRING,

    -- Creditor Info
    creditor_account_iban STRING,
    creditor_account_number STRING,

    -- Transaction Reference
    end_to_end_id STRING,
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

CREATE TABLE IF NOT EXISTS silver_camt058 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'camt.058',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Notification to Receive Cancellation Advice
    original_notification_id STRING,
    cancellation_reason_code STRING,
    cancellation_reason_info STRING,

    -- Original Expected Transaction
    original_expected_amount DECIMAL(18,5),
    original_expected_currency STRING,
    original_expected_value_date DATE,

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

CREATE TABLE IF NOT EXISTS silver_camt059 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'camt.059',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Notification to Receive Status Report
    original_notification_id STRING,
    status STRING,
    status_reason_code STRING,
    status_reason_info STRING,

    -- Matched Transaction
    matched_amount DECIMAL(18,5),
    matched_currency STRING,
    matched_value_date DATE,
    matched_reference STRING,

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

CREATE TABLE IF NOT EXISTS silver_camt060 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'camt.060',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Account Reporting Request
    request_type STRING,
    requested_message_type STRING,

    -- Account
    account_iban STRING,
    account_number STRING,
    account_currency STRING,

    -- Reporting Period
    from_date DATE,
    to_date DATE,
    from_datetime TIMESTAMP,
    to_datetime TIMESTAMP,

    -- Reporting Criteria
    entry_type STRING,
    entry_status STRING,

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

CREATE TABLE IF NOT EXISTS silver_camt086 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'camt.086',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Bank Services Billing Statement
    statement_id STRING,
    statement_date DATE,
    from_date DATE,
    to_date DATE,

    -- Account
    account_iban STRING,
    account_number STRING,
    account_currency STRING,

    -- Service Provider
    servicer_bic STRING,
    servicer_name STRING,

    -- Billing Summary
    total_tax_amount DECIMAL(18,5),
    total_charges_amount DECIMAL(18,5),
    total_amount DECIMAL(18,5),
    billing_currency STRING,

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

CREATE TABLE IF NOT EXISTS silver_camt087 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'camt.087',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Request to Modify Payment
    case_id STRING,
    case_creator STRING,

    -- Original Transaction
    original_message_id STRING,
    original_message_type STRING,
    original_instruction_id STRING,
    original_end_to_end_id STRING,
    original_uetr STRING,

    -- Modification Request
    modification_type STRING,
    requested_modification_code STRING,

    -- Requested Changes
    new_creditor_name STRING,
    new_creditor_account STRING,
    new_creditor_agent_bic STRING,
    new_remittance_info STRING,

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
-- ISO 20022 ACMT (Account Management) - Silver Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver_acmt001 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'acmt.001',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Account Opening Request
    request_type STRING,
    account_type STRING,
    account_currency STRING,

    -- Account Holder
    account_holder_name STRING,
    account_holder_address STRING,
    account_holder_country STRING,
    account_holder_id_type STRING,
    account_holder_id_value STRING,
    account_holder_date_of_birth DATE,
    account_holder_nationality STRING,

    -- Organization Details
    organization_name STRING,
    organization_id STRING,
    organization_lei STRING,
    organization_country_of_registration STRING,

    -- Account Servicer
    servicer_bic STRING,
    servicer_name STRING,
    branch_id STRING,

    -- Requested Features
    overdraft_requested BOOLEAN,
    credit_line_requested BOOLEAN,

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

CREATE TABLE IF NOT EXISTS silver_acmt002 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'acmt.002',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Account Opening Response
    original_request_id STRING,
    account_status STRING,

    -- Opened Account Details
    account_iban STRING,
    account_number STRING,
    account_type STRING,
    account_currency STRING,
    account_opening_date DATE,

    -- Status Info
    status_reason_code STRING,
    status_additional_info STRING,

    -- Account Servicer
    servicer_bic STRING,
    servicer_name STRING,

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

CREATE TABLE IF NOT EXISTS silver_acmt003 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'acmt.003',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Account Report
    report_type STRING,
    report_period_from DATE,
    report_period_to DATE,

    -- Account
    account_iban STRING,
    account_number STRING,
    account_type STRING,
    account_currency STRING,
    account_status STRING,

    -- Account Holder
    account_holder_name STRING,
    account_holder_id STRING,

    -- Account Features
    overdraft_limit DECIMAL(18,5),
    credit_line_limit DECIMAL(18,5),
    interest_rate DECIMAL(8,5),

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

CREATE TABLE IF NOT EXISTS silver_acmt007 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'acmt.007',

    -- Message Header
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Account Closure Request
    closure_reason_code STRING,
    closure_reason_info STRING,
    requested_closure_date DATE,

    -- Account to Close
    account_iban STRING,
    account_number STRING,
    account_holder_name STRING,

    -- Transfer Remaining Balance
    transfer_account_iban STRING,
    transfer_account_number STRING,
    transfer_account_holder_name STRING,
    transfer_account_servicer_bic STRING,

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
-- SWIFT MT - Additional Silver Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver_mt200 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'MT200',

    -- Header
    sender_bic STRING,
    receiver_bic STRING,

    -- Transaction Reference
    transaction_reference STRING,

    -- Value Date & Amount
    value_date DATE,
    currency STRING,
    amount DECIMAL(18,5),

    -- Account
    ordering_institution_account STRING,

    -- Intermediary
    intermediary_bic STRING,

    -- Account With Institution
    account_with_institution_bic STRING,

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

CREATE TABLE IF NOT EXISTS silver_mt202cov (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'MT202COV',

    -- Same as MT202 fields
    sender_bic STRING,
    receiver_bic STRING,
    transaction_reference STRING,
    related_reference STRING,
    value_date DATE,
    currency STRING,
    amount DECIMAL(18,5),
    ordering_institution_bic STRING,
    beneficiary_institution_bic STRING,

    -- Underlying Customer Credit Transfer
    underlying_ordering_customer_name STRING,
    underlying_ordering_customer_account STRING,
    underlying_ordering_customer_address STRING,
    underlying_beneficiary_customer_name STRING,
    underlying_beneficiary_customer_account STRING,
    underlying_beneficiary_customer_address STRING,
    underlying_remittance_info STRING,

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

CREATE TABLE IF NOT EXISTS silver_mt900 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'MT900',

    -- Header
    sender_bic STRING,
    receiver_bic STRING,

    -- Transaction Reference
    transaction_reference STRING,
    related_reference STRING,

    -- Account
    account_identification STRING,

    -- Value Date & Amount
    value_date DATE,
    currency STRING,
    amount DECIMAL(18,5),

    -- Ordering Customer
    ordering_customer_name STRING,

    -- Ordering Institution
    ordering_institution_bic STRING,

    -- Intermediary
    intermediary_bic STRING,

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

CREATE TABLE IF NOT EXISTS silver_mt910 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'MT910',

    -- Header
    sender_bic STRING,
    receiver_bic STRING,

    -- Transaction Reference
    transaction_reference STRING,
    related_reference STRING,

    -- Account
    account_identification STRING,

    -- Value Date & Amount
    value_date DATE,
    currency STRING,
    amount DECIMAL(18,5),

    -- Ordering Customer
    ordering_customer_name STRING,

    -- Ordering Institution
    ordering_institution_bic STRING,

    -- Intermediary/Sender Correspondent
    intermediary_bic STRING,

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

CREATE TABLE IF NOT EXISTS silver_mt940 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'MT940',

    -- Header
    sender_bic STRING,
    receiver_bic STRING,

    -- Transaction Reference
    transaction_reference STRING,
    related_reference STRING,

    -- Account
    account_identification STRING,

    -- Statement Number
    statement_number STRING,
    sequence_number STRING,

    -- Opening Balance
    opening_balance_indicator STRING,
    opening_balance_date DATE,
    opening_balance_currency STRING,
    opening_balance_amount DECIMAL(18,5),

    -- Statement Lines Count
    number_of_lines INT,

    -- Closing Balance
    closing_balance_indicator STRING,
    closing_balance_date DATE,
    closing_balance_currency STRING,
    closing_balance_amount DECIMAL(18,5),

    -- Closing Available Balance
    closing_available_balance_indicator STRING,
    closing_available_balance_date DATE,
    closing_available_balance_currency STRING,
    closing_available_balance_amount DECIMAL(18,5),

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

CREATE TABLE IF NOT EXISTS silver_mt942 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'MT942',

    -- Header
    sender_bic STRING,
    receiver_bic STRING,

    -- Transaction Reference
    transaction_reference STRING,
    related_reference STRING,

    -- Account
    account_identification STRING,

    -- Statement Number
    statement_number STRING,
    sequence_number STRING,

    -- Floor Limit (optional)
    floor_limit_indicator STRING,
    floor_limit_currency STRING,
    floor_limit_amount DECIMAL(18,5),

    -- Report Datetime
    report_datetime TIMESTAMP,

    -- Number of Transactions
    number_of_debit_entries INT,
    debit_entries_amount DECIMAL(18,5),
    number_of_credit_entries INT,
    credit_entries_amount DECIMAL(18,5),

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

CREATE TABLE IF NOT EXISTS silver_mt950 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'MT950',

    -- Header
    sender_bic STRING,
    receiver_bic STRING,

    -- Transaction Reference
    transaction_reference STRING,

    -- Account
    account_identification STRING,

    -- Statement Number
    statement_number STRING,
    sequence_number STRING,

    -- Opening Balance
    opening_balance_indicator STRING,
    opening_balance_date DATE,
    opening_balance_currency STRING,
    opening_balance_amount DECIMAL(18,5),

    -- Number of Statement Lines
    number_of_lines INT,

    -- Closing Balance
    closing_balance_indicator STRING,
    closing_balance_date DATE,
    closing_balance_currency STRING,
    closing_balance_amount DECIMAL(18,5),

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
-- Domestic Schemes - Additional Silver Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver_sepa_sdd (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'SEPA_SDD',
    scheme_type STRING, -- 'CORE' or 'B2B'

    -- Message Info
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,
    control_sum DECIMAL(18,5),

    -- Payment Info
    payment_info_id STRING,
    payment_method STRING,
    requested_collection_date DATE,

    -- Creditor (Collector)
    creditor_name STRING,
    creditor_iban STRING,
    creditor_bic STRING,
    creditor_id STRING,
    creditor_scheme_id STRING,

    -- Mandate
    mandate_id STRING,
    mandate_date_of_signature DATE,
    sequence_type STRING,

    -- Transaction
    instruction_id STRING,
    end_to_end_id STRING,
    instructed_amount DECIMAL(18,5),

    -- Debtor
    debtor_name STRING,
    debtor_iban STRING,
    debtor_bic STRING,

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
PARTITIONED BY (message_type, scheme_type);

CREATE TABLE IF NOT EXISTS silver_sepa_sct_inst (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'SEPA_SCT_INST',

    -- Same structure as SEPA SCT but for instant
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

    -- Instant Payment Specific
    acceptance_datetime TIMESTAMP,
    settlement_datetime TIMESTAMP,

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

CREATE TABLE IF NOT EXISTS silver_chips (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'CHIPS',

    -- Message Info
    sequence_number STRING,
    message_type_code STRING,

    -- Participants
    sending_participant STRING,
    receiving_participant STRING,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Value Date
    value_date DATE,

    -- References
    sender_reference STRING,
    related_reference STRING,

    -- Originator
    originator_name STRING,
    originator_address STRING,
    originator_account STRING,

    -- Beneficiary
    beneficiary_name STRING,
    beneficiary_address STRING,
    beneficiary_account STRING,

    -- Correspondent Banks
    originator_bank STRING,
    beneficiary_bank STRING,
    intermediary_bank STRING,

    -- Payment Details
    payment_details STRING,

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

CREATE TABLE IF NOT EXISTS silver_bacs (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'BACS',

    -- Service User Info
    service_user_number STRING,
    service_user_name STRING,

    -- Processing Date
    processing_date DATE,

    -- Transaction
    transaction_type STRING,
    originating_sort_code STRING,
    originating_account STRING,
    destination_sort_code STRING,
    destination_account STRING,

    -- Amount
    amount DECIMAL(18,5),

    -- Reference
    reference STRING,
    beneficiary_name STRING,

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

CREATE TABLE IF NOT EXISTS silver_chaps (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'CHAPS',

    -- Message Info
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Settlement
    settlement_date DATE,
    settlement_method STRING,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Debtor
    debtor_name STRING,
    debtor_address STRING,
    debtor_sort_code STRING,
    debtor_account STRING,
    debtor_agent_bic STRING,

    -- Creditor
    creditor_name STRING,
    creditor_address STRING,
    creditor_sort_code STRING,
    creditor_account STRING,
    creditor_agent_bic STRING,

    -- References
    instruction_id STRING,
    end_to_end_id STRING,
    uetr STRING,

    -- Remittance
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

CREATE TABLE IF NOT EXISTS silver_faster_payments (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'FASTER_PAYMENTS',

    -- Message Info
    payment_id STRING,
    creation_datetime TIMESTAMP,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Payer
    payer_sort_code STRING,
    payer_account STRING,
    payer_name STRING,
    payer_address STRING,

    -- Payee
    payee_sort_code STRING,
    payee_account STRING,
    payee_name STRING,
    payee_address STRING,

    -- References
    end_to_end_id STRING,
    payment_reference STRING,

    -- Timing
    requested_execution_date DATE,
    settlement_datetime TIMESTAMP,

    -- Remittance
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
-- Real-Time Payments - Additional Silver Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver_npp (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'NPP',

    -- Message Info
    payment_id STRING,
    creation_datetime TIMESTAMP,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Payer
    payer_bsb STRING,
    payer_account STRING,
    payer_name STRING,
    payer_payid STRING,
    payer_payid_type STRING,

    -- Payee
    payee_bsb STRING,
    payee_account STRING,
    payee_name STRING,
    payee_payid STRING,
    payee_payid_type STRING,

    -- References
    end_to_end_id STRING,
    payment_reference STRING,

    -- Overlay Service
    overlay_service STRING,

    -- Remittance
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

CREATE TABLE IF NOT EXISTS silver_upi (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'UPI',

    -- Transaction Info
    transaction_id STRING,
    transaction_ref_id STRING,
    creation_datetime TIMESTAMP,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Payer
    payer_vpa STRING,
    payer_name STRING,
    payer_account STRING,
    payer_ifsc STRING,
    payer_mobile STRING,

    -- Payee
    payee_vpa STRING,
    payee_name STRING,
    payee_account STRING,
    payee_ifsc STRING,
    payee_mobile STRING,

    -- Transaction Type
    transaction_type STRING,
    sub_type STRING,

    -- QR Code Info
    qr_code_type STRING,
    merchant_code STRING,

    -- Remittance
    remittance_info STRING,

    -- Status
    transaction_status STRING,
    response_code STRING,

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

CREATE TABLE IF NOT EXISTS silver_paynow (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'PAYNOW',

    -- Transaction Info
    transaction_id STRING,
    creation_datetime TIMESTAMP,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Payer
    payer_proxy_type STRING,
    payer_proxy_value STRING,
    payer_name STRING,
    payer_bank_code STRING,
    payer_account STRING,

    -- Payee
    payee_proxy_type STRING,
    payee_proxy_value STRING,
    payee_name STRING,
    payee_bank_code STRING,
    payee_account STRING,

    -- Reference
    end_to_end_id STRING,

    -- Remittance
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

CREATE TABLE IF NOT EXISTS silver_promptpay (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'PROMPTPAY',

    -- Transaction Info
    transaction_id STRING,
    creation_datetime TIMESTAMP,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Payer
    payer_proxy_type STRING,
    payer_proxy_value STRING,
    payer_name STRING,
    payer_bank_code STRING,
    payer_account STRING,

    -- Payee
    payee_proxy_type STRING,
    payee_proxy_value STRING,
    payee_name STRING,
    payee_bank_code STRING,
    payee_account STRING,

    -- Reference
    end_to_end_id STRING,
    qr_code_data STRING,

    -- Remittance
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

CREATE TABLE IF NOT EXISTS silver_instapay (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'INSTAPAY',

    -- Transaction Info
    transaction_id STRING,
    creation_datetime TIMESTAMP,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Sender
    sender_bank_code STRING,
    sender_account STRING,
    sender_name STRING,

    -- Receiver
    receiver_bank_code STRING,
    receiver_account STRING,
    receiver_name STRING,

    -- Reference
    reference_number STRING,

    -- Remittance
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
-- RTGS Systems - Silver Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver_target2 (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'TARGET2',

    -- Message Info
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Settlement
    settlement_date DATE,
    settlement_method STRING,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Agents
    instructing_agent_bic STRING,
    instructed_agent_bic STRING,
    debtor_agent_bic STRING,
    creditor_agent_bic STRING,

    -- Transaction IDs
    instruction_id STRING,
    end_to_end_id STRING,
    transaction_id STRING,
    uetr STRING,

    -- Debtor
    debtor_name STRING,
    debtor_account STRING,

    -- Creditor
    creditor_name STRING,
    creditor_account STRING,

    -- Payment Type
    payment_type STRING,
    service_level STRING,

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

CREATE TABLE IF NOT EXISTS silver_bojnet (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'BOJNET',

    -- Message Info
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Settlement
    settlement_date DATE,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Participants
    sending_participant_code STRING,
    receiving_participant_code STRING,

    -- Transaction Reference
    transaction_reference STRING,
    related_reference STRING,

    -- Account Info
    debit_account STRING,
    credit_account STRING,

    -- Payment Type
    payment_type STRING,

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

CREATE TABLE IF NOT EXISTS silver_cnaps (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'CNAPS',

    -- Message Info
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Settlement
    settlement_date DATE,
    business_type STRING,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Participants
    sending_bank_code STRING,
    receiving_bank_code STRING,

    -- Payer
    payer_name STRING,
    payer_account STRING,
    payer_bank_name STRING,

    -- Payee
    payee_name STRING,
    payee_account STRING,
    payee_bank_name STRING,

    -- Transaction Reference
    transaction_reference STRING,

    -- Purpose
    purpose STRING,

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

CREATE TABLE IF NOT EXISTS silver_meps_plus (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'MEPS_PLUS',

    -- Message Info
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Settlement
    settlement_date DATE,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Participants
    sending_bank_bic STRING,
    receiving_bank_bic STRING,

    -- Transaction Reference
    transaction_reference STRING,

    -- Debtor
    debtor_name STRING,
    debtor_account STRING,

    -- Creditor
    creditor_name STRING,
    creditor_account STRING,

    -- Purpose
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

CREATE TABLE IF NOT EXISTS silver_rtgs_hk (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'RTGS_HK',

    -- Message Info
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Settlement
    settlement_date DATE,
    settlement_currency STRING,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Participants
    sending_bank_code STRING,
    receiving_bank_code STRING,

    -- Transaction Reference
    transaction_reference STRING,

    -- Payer
    payer_name STRING,
    payer_account STRING,

    -- Payee
    payee_name STRING,
    payee_account STRING,

    -- Purpose
    purpose STRING,

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

CREATE TABLE IF NOT EXISTS silver_sarie (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'SARIE',

    -- Message Info
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Settlement
    settlement_date DATE,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Participants
    sending_bank_code STRING,
    receiving_bank_code STRING,

    -- Transaction Reference
    transaction_reference STRING,

    -- Originator
    originator_name STRING,
    originator_account STRING,
    originator_id STRING,

    -- Beneficiary
    beneficiary_name STRING,
    beneficiary_account STRING,
    beneficiary_id STRING,

    -- Purpose
    purpose STRING,

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

CREATE TABLE IF NOT EXISTS silver_uaefts (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'UAEFTS',

    -- Message Info
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Settlement
    settlement_date DATE,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Participants
    sending_bank_code STRING,
    receiving_bank_code STRING,

    -- Transaction Reference
    transaction_reference STRING,

    -- Originator
    originator_name STRING,
    originator_account STRING,
    originator_address STRING,

    -- Beneficiary
    beneficiary_name STRING,
    beneficiary_account STRING,
    beneficiary_address STRING,

    -- Purpose
    purpose STRING,

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

CREATE TABLE IF NOT EXISTS silver_kftc (
    stg_id STRING NOT NULL,
    raw_id STRING NOT NULL,
    message_type STRING DEFAULT 'KFTC',

    -- Message Info
    message_id STRING,
    creation_datetime TIMESTAMP,

    -- Settlement
    settlement_date DATE,

    -- Amount
    amount DECIMAL(18,5),
    currency STRING,

    -- Participants
    sending_bank_code STRING,
    receiving_bank_code STRING,

    -- Transaction Reference
    transaction_reference STRING,

    -- Payer
    payer_name STRING,
    payer_account STRING,

    -- Payee
    payee_name STRING,
    payee_account STRING,

    -- Purpose
    purpose STRING,

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
-- Extended Unified Silver View
-- ============================================================================

CREATE OR REPLACE VIEW silver_all_payments_unified AS
SELECT
    stg_id, raw_id, message_type,
    COALESCE(message_id, transaction_reference) AS message_id,
    COALESCE(creation_datetime, CAST(value_date AS TIMESTAMP)) AS transaction_datetime,
    COALESCE(instructed_amount, interbank_settlement_amount, amount) AS amount,
    COALESCE(instructed_currency, interbank_settlement_currency, currency) AS currency,
    debtor_name,
    COALESCE(debtor_account_iban, debtor_account, ordering_customer_account) AS debtor_account,
    COALESCE(debtor_agent_bic, ordering_institution_bic) AS debtor_agent,
    creditor_name,
    COALESCE(creditor_account_iban, creditor_account, beneficiary_customer_account) AS creditor_account,
    COALESCE(creditor_agent_bic, account_with_institution_bic) AS creditor_agent,
    end_to_end_id,
    uetr,
    dq_score,
    _batch_id,
    _processed_at
FROM silver_pain001
UNION ALL SELECT stg_id, raw_id, message_type, message_id, creation_datetime, interbank_settlement_amount, interbank_settlement_currency, debtor_name, debtor_account_iban, debtor_agent_bic, creditor_name, creditor_account_iban, creditor_agent_bic, end_to_end_id, uetr, dq_score, _batch_id, _processed_at FROM silver_pacs008
UNION ALL SELECT stg_id, raw_id, message_type, transaction_reference, CAST(value_date AS TIMESTAMP), amount, currency, ordering_customer_name, ordering_customer_account, ordering_institution_bic, beneficiary_customer_name, beneficiary_customer_account, account_with_institution_bic, transaction_reference, uetr, dq_score, _batch_id, _processed_at FROM silver_mt103
UNION ALL SELECT stg_id, raw_id, message_type, message_id, creation_datetime, instructed_amount, 'EUR', debtor_name, debtor_iban, debtor_bic, creditor_name, creditor_iban, creditor_bic, end_to_end_id, NULL, dq_score, _batch_id, _processed_at FROM silver_sepa_sct
UNION ALL SELECT stg_id, raw_id, message_type, trace_number, CAST(effective_entry_date AS TIMESTAMP), amount, 'USD', NULL, receiving_dfi_account, originating_dfi_id, individual_name, receiving_dfi_account, receiving_dfi_id, trace_number, NULL, dq_score, _batch_id, _processed_at FROM silver_nacha_ach
UNION ALL SELECT stg_id, raw_id, message_type, imad, CAST(NULL AS TIMESTAMP), amount, 'USD', originator_name, NULL, sender_aba, beneficiary_name, NULL, receiver_aba, sender_reference, NULL, dq_score, _batch_id, _processed_at FROM silver_fedwire
UNION ALL SELECT stg_id, raw_id, message_type, message_id, creation_datetime, interbank_settlement_amount, interbank_settlement_currency, debtor_name, debtor_account, debtor_agent_routing, creditor_name, creditor_account, creditor_agent_routing, end_to_end_id, uetr, dq_score, _batch_id, _processed_at FROM silver_fednow
UNION ALL SELECT stg_id, raw_id, message_type, end_to_end_id, creation_datetime, amount, currency, payer_name, payer_account, payer_ispb, payee_name, payee_account, payee_ispb, end_to_end_id, NULL, dq_score, _batch_id, _processed_at FROM silver_pix
UNION ALL SELECT stg_id, raw_id, message_type, message_id, creation_datetime, amount, currency, sender_name, sender_account, sender_routing_number, receiver_name, receiver_account, receiver_routing_number, end_to_end_id, uetr, dq_score, _batch_id, _processed_at FROM silver_rtp;
