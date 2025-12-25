-- ============================================================================
-- GPS CDM - Bronze Layer Tables (Raw Ingestion)
-- ============================================================================
-- Each message type has its own Bronze table to preserve source fidelity
-- Tables are partitioned by ingestion date for efficient querying
-- ============================================================================

-- Use the CDM catalog and schema
USE CATALOG ${catalog};
USE SCHEMA ${schema};

-- ============================================================================
-- ISO 20022 PAIN (Payments Initiation) Messages
-- ============================================================================

CREATE TABLE IF NOT EXISTS bronze_pain001 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,
    control_sum DECIMAL(18,5),
    initiating_party_name STRING,
    payment_info_id STRING,
    payment_method STRING,
    batch_booking BOOLEAN,
    requested_execution_date DATE,
    debtor_name STRING,
    debtor_address STRING,
    debtor_country STRING,
    debtor_id STRING,
    debtor_account_iban STRING,
    debtor_account_number STRING,
    debtor_agent_bic STRING,
    instruction_id STRING,
    end_to_end_id STRING,
    uetr STRING,
    instructed_amount DECIMAL(18,5),
    instructed_currency STRING,
    equivalent_amount DECIMAL(18,5),
    equivalent_currency STRING,
    exchange_rate DECIMAL(12,6),
    charge_bearer STRING,
    creditor_name STRING,
    creditor_address STRING,
    creditor_country STRING,
    creditor_id STRING,
    creditor_account_iban STRING,
    creditor_account_number STRING,
    creditor_agent_bic STRING,
    ultimate_debtor_name STRING,
    ultimate_creditor_name STRING,
    purpose_code STRING,
    category_purpose STRING,
    service_level STRING,
    local_instrument STRING,
    remittance_unstructured STRING,
    remittance_structured STRING,
    regulatory_reporting STRING,
    raw_xml STRING,
    file_name STRING,
    file_path STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp(),
    _data_quality_score DECIMAL(5,4)
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at))
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE TABLE IF NOT EXISTS bronze_pain002 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    original_message_id STRING,
    original_message_type STRING,
    group_status STRING,
    status_reason_code STRING,
    status_reason_info STRING,
    original_end_to_end_id STRING,
    original_instruction_id STRING,
    transaction_status STRING,
    acceptance_datetime TIMESTAMP,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_pain007 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    original_message_id STRING,
    original_payment_info_id STRING,
    reversal_reason_code STRING,
    reversal_reason_info STRING,
    reversed_amount DECIMAL(18,5),
    reversed_currency STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_pain008 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,
    control_sum DECIMAL(18,5),
    payment_info_id STRING,
    payment_method STRING,
    requested_collection_date DATE,
    creditor_name STRING,
    creditor_account_iban STRING,
    creditor_agent_bic STRING,
    creditor_scheme_id STRING,
    mandate_id STRING,
    mandate_date_of_signature DATE,
    sequence_type STRING,
    amendment_indicator BOOLEAN,
    debtor_name STRING,
    debtor_account_iban STRING,
    debtor_agent_bic STRING,
    instructed_amount DECIMAL(18,5),
    instructed_currency STRING,
    end_to_end_id STRING,
    purpose_code STRING,
    remittance_info STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_pain013 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    original_message_id STRING,
    amendment_reason STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_pain014 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    original_message_id STRING,
    activation_status STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

-- ============================================================================
-- ISO 20022 PACS (Payments Clearing & Settlement) Messages
-- ============================================================================

CREATE TABLE IF NOT EXISTS bronze_pacs002 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    original_message_id STRING,
    original_message_type STRING,
    group_status STRING,
    transaction_status STRING,
    status_reason_code STRING,
    status_reason_info STRING,
    original_end_to_end_id STRING,
    original_transaction_id STRING,
    original_uetr STRING,
    acceptance_datetime TIMESTAMP,
    clearing_system_reference STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_pacs003 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,
    settlement_method STRING,
    settlement_date DATE,
    instructing_agent_bic STRING,
    instructed_agent_bic STRING,
    end_to_end_id STRING,
    transaction_id STRING,
    mandate_id STRING,
    creditor_name STRING,
    creditor_account STRING,
    debtor_name STRING,
    debtor_account STRING,
    interbank_settlement_amount DECIMAL(18,5),
    interbank_settlement_currency STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_pacs004 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,
    settlement_method STRING,
    return_id STRING,
    original_message_id STRING,
    original_message_type STRING,
    original_end_to_end_id STRING,
    original_transaction_id STRING,
    original_uetr STRING,
    return_reason_code STRING,
    return_reason_info STRING,
    returned_amount DECIMAL(18,5),
    returned_currency STRING,
    interbank_settlement_date DATE,
    charge_bearer STRING,
    instructing_agent_bic STRING,
    instructed_agent_bic STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_pacs007 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    original_message_id STRING,
    original_instruction_id STRING,
    reversal_reason_code STRING,
    reversal_reason_info STRING,
    reversed_amount DECIMAL(18,5),
    reversed_currency STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_pacs008 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,
    total_interbank_settlement_amount DECIMAL(18,5),
    total_interbank_settlement_currency STRING,
    interbank_settlement_date DATE,
    settlement_method STRING,
    clearing_system STRING,
    instructing_agent_bic STRING,
    instructed_agent_bic STRING,
    instruction_id STRING,
    end_to_end_id STRING,
    transaction_id STRING,
    uetr STRING,
    clearing_system_reference STRING,
    interbank_settlement_amount DECIMAL(18,5),
    interbank_settlement_currency STRING,
    instructed_amount DECIMAL(18,5),
    instructed_currency STRING,
    exchange_rate DECIMAL(12,6),
    charge_bearer STRING,
    charges_amount DECIMAL(18,5),
    charges_currency STRING,
    charges_agent_bic STRING,
    debtor_name STRING,
    debtor_address STRING,
    debtor_country STRING,
    debtor_account_iban STRING,
    debtor_agent_bic STRING,
    creditor_name STRING,
    creditor_address STRING,
    creditor_country STRING,
    creditor_account_iban STRING,
    creditor_agent_bic STRING,
    intermediary_agent1_bic STRING,
    intermediary_agent2_bic STRING,
    intermediary_agent3_bic STRING,
    purpose_code STRING,
    remittance_info STRING,
    regulatory_reporting STRING,
    instruction_priority STRING,
    service_level STRING,
    clearing_channel STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_pacs009 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,
    settlement_method STRING,
    interbank_settlement_date DATE,
    instructing_agent_bic STRING,
    instructed_agent_bic STRING,
    end_to_end_id STRING,
    transaction_id STRING,
    uetr STRING,
    interbank_settlement_amount DECIMAL(18,5),
    interbank_settlement_currency STRING,
    debtor_agent_bic STRING,
    creditor_agent_bic STRING,
    intermediary_agent_bic STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_pacs028 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    original_message_id STRING,
    original_end_to_end_id STRING,
    original_uetr STRING,
    status_request_reason STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

-- ============================================================================
-- ISO 20022 CAMT (Cash Management) Messages
-- ============================================================================

CREATE TABLE IF NOT EXISTS bronze_camt026 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    assignment_id STRING,
    original_message_id STRING,
    original_end_to_end_id STRING,
    unable_to_apply_code STRING,
    additional_info STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_camt027 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    original_message_id STRING,
    original_end_to_end_id STRING,
    claim_non_receipt_reason STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_camt029 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    original_message_id STRING,
    investigation_status STRING,
    resolution_type STRING,
    charges_info STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_camt050 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    liquidity_transfer_id STRING,
    creditor_account STRING,
    debtor_account STRING,
    transfer_amount DECIMAL(18,5),
    transfer_currency STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_camt052 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    report_id STRING,
    report_pagination STRING,
    account_iban STRING,
    account_owner_name STRING,
    account_servicer_bic STRING,
    from_datetime TIMESTAMP,
    to_datetime TIMESTAMP,
    balance_type STRING,
    balance_amount DECIMAL(18,5),
    balance_currency STRING,
    balance_credit_debit STRING,
    number_of_entries INT,
    sum_of_entries DECIMAL(18,5),
    entries_json STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_camt053 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    statement_id STRING,
    sequence_number STRING,
    legal_sequence_number STRING,
    account_iban STRING,
    account_owner_name STRING,
    account_servicer_bic STRING,
    from_date DATE,
    to_date DATE,
    opening_balance_amount DECIMAL(18,5),
    opening_balance_currency STRING,
    opening_balance_credit_debit STRING,
    closing_balance_amount DECIMAL(18,5),
    closing_balance_currency STRING,
    closing_balance_credit_debit STRING,
    number_of_entries INT,
    sum_of_entries DECIMAL(18,5),
    entries_json STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_camt054 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    notification_id STRING,
    account_iban STRING,
    account_owner_name STRING,
    entry_amount DECIMAL(18,5),
    entry_currency STRING,
    entry_credit_debit STRING,
    entry_status STRING,
    booking_date DATE,
    value_date DATE,
    entry_reference STRING,
    end_to_end_id STRING,
    debtor_name STRING,
    creditor_name STRING,
    remittance_info STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_camt055 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    original_message_id STRING,
    original_message_type STRING,
    cancellation_reason_code STRING,
    cancellation_reason_info STRING,
    original_end_to_end_id STRING,
    original_amount DECIMAL(18,5),
    original_currency STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_camt056 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    original_message_id STRING,
    original_message_type STRING,
    cancellation_reason_code STRING,
    cancellation_reason_info STRING,
    original_transaction_id STRING,
    original_uetr STRING,
    original_amount DECIMAL(18,5),
    original_currency STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_camt057 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    notification_id STRING,
    account_iban STRING,
    expected_value_date DATE,
    expected_amount DECIMAL(18,5),
    expected_currency STRING,
    debtor_name STRING,
    debtor_agent_bic STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_camt058 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    original_notification_id STRING,
    cancellation_reason STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_camt059 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    request_type STRING,
    account_iban STRING,
    from_date DATE,
    to_date DATE,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_camt060 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    request_type STRING,
    account_iban STRING,
    reporting_period STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_camt086 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    billing_id STRING,
    billing_period_start DATE,
    billing_period_end DATE,
    total_charges DECIMAL(18,5),
    total_charges_currency STRING,
    service_details_json STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_camt087 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    original_message_id STRING,
    original_end_to_end_id STRING,
    modification_type STRING,
    modified_amount DECIMAL(18,5),
    modified_currency STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

-- ============================================================================
-- ISO 20022 ACMT (Account Management) Messages
-- ============================================================================

CREATE TABLE IF NOT EXISTS bronze_acmt001 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    instruction_id STRING,
    account_type STRING,
    account_currency STRING,
    account_name STRING,
    account_holder_name STRING,
    account_holder_address STRING,
    account_holder_country STRING,
    account_holder_id STRING,
    account_servicer_bic STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_acmt002 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    account_number STRING,
    account_iban STRING,
    confirmation_status STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_acmt003 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    account_iban STRING,
    modification_type STRING,
    modified_fields_json STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_acmt007 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    request_type STRING,
    account_details_json STRING,
    applicant_name STRING,
    applicant_address STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

-- ============================================================================
-- SWIFT MT Messages
-- ============================================================================

CREATE TABLE IF NOT EXISTS bronze_mt103 (
    raw_id STRING NOT NULL,
    sender_bic STRING,
    receiver_bic STRING,
    message_type STRING,
    priority STRING,
    transaction_reference STRING,
    bank_operation_code STRING,
    value_date DATE,
    currency STRING,
    amount DECIMAL(18,5),
    instructed_currency STRING,
    instructed_amount DECIMAL(18,5),
    exchange_rate DECIMAL(12,6),
    ordering_customer_account STRING,
    ordering_customer_name STRING,
    ordering_customer_address STRING,
    ordering_institution_bic STRING,
    senders_correspondent_bic STRING,
    receivers_correspondent_bic STRING,
    intermediary_bic STRING,
    account_with_institution_bic STRING,
    beneficiary_customer_account STRING,
    beneficiary_customer_name STRING,
    beneficiary_customer_address STRING,
    remittance_information STRING,
    details_of_charges STRING,
    senders_charges STRING,
    receivers_charges STRING,
    sender_to_receiver_info STRING,
    regulatory_reporting STRING,
    uetr STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_mt103_stp (
    raw_id STRING NOT NULL,
    sender_bic STRING,
    receiver_bic STRING,
    transaction_reference STRING,
    bank_operation_code STRING,
    value_date DATE,
    currency STRING,
    amount DECIMAL(18,5),
    ordering_customer_bic STRING,
    ordering_customer_account STRING,
    ordering_institution_bic STRING,
    account_with_institution_bic STRING,
    beneficiary_customer_bic STRING,
    beneficiary_customer_account STRING,
    remittance_information STRING,
    details_of_charges STRING,
    uetr STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_mt200 (
    raw_id STRING NOT NULL,
    sender_bic STRING,
    receiver_bic STRING,
    transaction_reference STRING,
    value_date DATE,
    currency STRING,
    amount DECIMAL(18,5),
    ordering_institution_bic STRING,
    correspondent_bic STRING,
    sender_to_receiver_info STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_mt202 (
    raw_id STRING NOT NULL,
    sender_bic STRING,
    receiver_bic STRING,
    transaction_reference STRING,
    related_reference STRING,
    value_date DATE,
    currency STRING,
    amount DECIMAL(18,5),
    ordering_institution_bic STRING,
    senders_correspondent_bic STRING,
    receivers_correspondent_bic STRING,
    intermediary_bic STRING,
    account_with_institution_bic STRING,
    beneficiary_institution_bic STRING,
    sender_to_receiver_info STRING,
    uetr STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_mt202cov (
    raw_id STRING NOT NULL,
    sender_bic STRING,
    receiver_bic STRING,
    transaction_reference STRING,
    related_reference STRING,
    value_date DATE,
    currency STRING,
    amount DECIMAL(18,5),
    ordering_institution_bic STRING,
    beneficiary_institution_bic STRING,
    underlying_customer_credit_transfer STRING,
    ordering_customer_name STRING,
    ordering_customer_account STRING,
    beneficiary_customer_name STRING,
    beneficiary_customer_account STRING,
    uetr STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_mt900 (
    raw_id STRING NOT NULL,
    sender_bic STRING,
    receiver_bic STRING,
    transaction_reference STRING,
    related_reference STRING,
    account_identification STRING,
    value_date DATE,
    currency STRING,
    amount DECIMAL(18,5),
    ordering_customer STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_mt910 (
    raw_id STRING NOT NULL,
    sender_bic STRING,
    receiver_bic STRING,
    transaction_reference STRING,
    related_reference STRING,
    account_identification STRING,
    value_date DATE,
    currency STRING,
    amount DECIMAL(18,5),
    ordering_customer STRING,
    ordering_institution_bic STRING,
    intermediary_bic STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_mt940 (
    raw_id STRING NOT NULL,
    sender_bic STRING,
    receiver_bic STRING,
    transaction_reference STRING,
    account_identification STRING,
    statement_number STRING,
    sequence_number STRING,
    opening_balance_type STRING,
    opening_balance_date DATE,
    opening_balance_currency STRING,
    opening_balance_amount DECIMAL(18,5),
    closing_balance_type STRING,
    closing_balance_date DATE,
    closing_balance_currency STRING,
    closing_balance_amount DECIMAL(18,5),
    closing_available_balance_amount DECIMAL(18,5),
    number_of_entries INT,
    entries_json STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_mt950 (
    raw_id STRING NOT NULL,
    sender_bic STRING,
    receiver_bic STRING,
    transaction_reference STRING,
    account_identification STRING,
    statement_number STRING,
    opening_balance_date DATE,
    opening_balance_currency STRING,
    opening_balance_amount DECIMAL(18,5),
    closing_balance_date DATE,
    closing_balance_currency STRING,
    closing_balance_amount DECIMAL(18,5),
    entries_json STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

-- ============================================================================
-- Domestic Payment Schemes
-- ============================================================================

CREATE TABLE IF NOT EXISTS bronze_sepa_sct (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    number_of_transactions INT,
    control_sum DECIMAL(18,5),
    payment_info_id STRING,
    payment_method STRING,
    requested_execution_date DATE,
    debtor_name STRING,
    debtor_iban STRING,
    debtor_bic STRING,
    instruction_id STRING,
    end_to_end_id STRING,
    instructed_amount DECIMAL(18,5),
    creditor_name STRING,
    creditor_iban STRING,
    creditor_bic STRING,
    charge_bearer STRING,
    purpose_code STRING,
    remittance_info STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_sepa_sct_inst (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    debtor_name STRING,
    debtor_iban STRING,
    debtor_bic STRING,
    end_to_end_id STRING,
    instructed_amount DECIMAL(18,5),
    creditor_name STRING,
    creditor_iban STRING,
    creditor_bic STRING,
    acceptance_datetime TIMESTAMP,
    settlement_datetime TIMESTAMP,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_sepa_sdd_core (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    payment_info_id STRING,
    requested_collection_date DATE,
    creditor_name STRING,
    creditor_iban STRING,
    creditor_bic STRING,
    creditor_scheme_id STRING,
    mandate_id STRING,
    mandate_date_of_signature DATE,
    sequence_type STRING,
    debtor_name STRING,
    debtor_iban STRING,
    debtor_bic STRING,
    end_to_end_id STRING,
    instructed_amount DECIMAL(18,5),
    remittance_info STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_sepa_sdd_b2b (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    payment_info_id STRING,
    requested_collection_date DATE,
    creditor_name STRING,
    creditor_iban STRING,
    creditor_scheme_id STRING,
    mandate_id STRING,
    sequence_type STRING,
    debtor_name STRING,
    debtor_iban STRING,
    end_to_end_id STRING,
    instructed_amount DECIMAL(18,5),
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_nacha_ach (
    raw_id STRING NOT NULL,
    file_header_record STRING,
    batch_header_record STRING,
    company_name STRING,
    company_id STRING,
    standard_entry_class STRING,
    company_entry_description STRING,
    effective_entry_date DATE,
    originating_dfi_id STRING,
    transaction_code STRING,
    receiving_dfi_id STRING,
    receiving_dfi_account STRING,
    amount DECIMAL(18,5),
    individual_id STRING,
    individual_name STRING,
    discretionary_data STRING,
    addenda_record_indicator BOOLEAN,
    addenda_type_code STRING,
    payment_related_info STRING,
    trace_number STRING,
    raw_record STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_fedwire (
    raw_id STRING NOT NULL,
    type_subtype STRING,
    imad STRING,
    omad STRING,
    sender_aba STRING,
    sender_short_name STRING,
    receiver_aba STRING,
    receiver_short_name STRING,
    business_function_code STRING,
    amount DECIMAL(18,5),
    sender_reference STRING,
    previous_message_id STRING,
    originator_name STRING,
    originator_address STRING,
    originator_id STRING,
    originator_fi_name STRING,
    originator_fi_id STRING,
    instructing_fi_name STRING,
    instructing_fi_id STRING,
    beneficiary_fi_name STRING,
    beneficiary_fi_id STRING,
    beneficiary_name STRING,
    beneficiary_address STRING,
    beneficiary_id STRING,
    originator_to_beneficiary_info STRING,
    fi_to_fi_info STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_chips (
    raw_id STRING NOT NULL,
    message_type STRING,
    sequence_number STRING,
    sender_chips_uid STRING,
    receiver_chips_uid STRING,
    amount DECIMAL(18,5),
    currency STRING,
    value_date DATE,
    originator_name STRING,
    originator_account STRING,
    beneficiary_name STRING,
    beneficiary_account STRING,
    payment_details STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_bacs (
    raw_id STRING NOT NULL,
    record_type STRING,
    originating_sort_code STRING,
    originating_account_number STRING,
    destination_sort_code STRING,
    destination_account_number STRING,
    amount DECIMAL(18,5),
    transaction_code STRING,
    originator_name STRING,
    reference STRING,
    processing_date DATE,
    raw_record STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_chaps (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    settlement_date DATE,
    settlement_method STRING,
    instructing_agent_sort_code STRING,
    instructed_agent_sort_code STRING,
    debtor_name STRING,
    debtor_account STRING,
    debtor_sort_code STRING,
    creditor_name STRING,
    creditor_account STRING,
    creditor_sort_code STRING,
    amount DECIMAL(18,5),
    currency STRING,
    end_to_end_id STRING,
    remittance_info STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_faster_payments (
    raw_id STRING NOT NULL,
    fps_id STRING,
    creation_datetime TIMESTAMP,
    settlement_datetime TIMESTAMP,
    originating_sort_code STRING,
    originating_account STRING,
    destination_sort_code STRING,
    destination_account STRING,
    amount DECIMAL(18,5),
    currency STRING,
    reference STRING,
    remittance_info STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

-- ============================================================================
-- Real-Time Payment Systems
-- ============================================================================

CREATE TABLE IF NOT EXISTS bronze_fednow (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    message_type STRING,
    settlement_method STRING,
    interbank_settlement_date DATE,
    interbank_settlement_amount DECIMAL(18,5),
    interbank_settlement_currency STRING,
    instructing_agent_routing STRING,
    instructed_agent_routing STRING,
    end_to_end_id STRING,
    transaction_id STRING,
    uetr STRING,
    debtor_name STRING,
    debtor_account STRING,
    debtor_agent_routing STRING,
    creditor_name STRING,
    creditor_account STRING,
    creditor_agent_routing STRING,
    purpose_code STRING,
    remittance_info STRING,
    fraud_score INT,
    fraud_risk_level STRING,
    acceptance_datetime TIMESTAMP,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_rtp (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    message_type STRING,
    settlement_date DATE,
    amount DECIMAL(18,5),
    currency STRING,
    sender_routing_number STRING,
    sender_account STRING,
    sender_name STRING,
    receiver_routing_number STRING,
    receiver_account STRING,
    receiver_name STRING,
    end_to_end_id STRING,
    uetr STRING,
    remittance_info STRING,
    acceptance_datetime TIMESTAMP,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_pix (
    raw_id STRING NOT NULL,
    end_to_end_id STRING,
    creation_datetime TIMESTAMP,
    local_instrument STRING,
    payer_ispb STRING,
    payer_branch STRING,
    payer_account STRING,
    payer_account_type STRING,
    payer_name STRING,
    payer_cpf_cnpj STRING,
    payer_pix_key STRING,
    payer_pix_key_type STRING,
    payee_ispb STRING,
    payee_branch STRING,
    payee_account STRING,
    payee_account_type STRING,
    payee_name STRING,
    payee_cpf_cnpj STRING,
    payee_pix_key STRING,
    payee_pix_key_type STRING,
    amount DECIMAL(18,5),
    currency STRING,
    remittance_info STRING,
    qr_code_type STRING,
    initiation_type STRING,
    payment_type STRING,
    fraud_score INT,
    raw_json STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_npp (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    settlement_date DATE,
    amount DECIMAL(18,5),
    currency STRING,
    payer_bsb STRING,
    payer_account STRING,
    payer_name STRING,
    payee_bsb STRING,
    payee_account STRING,
    payee_name STRING,
    payee_payid STRING,
    payee_payid_type STRING,
    end_to_end_id STRING,
    remittance_info STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_upi (
    raw_id STRING NOT NULL,
    transaction_id STRING,
    creation_datetime TIMESTAMP,
    payer_vpa STRING,
    payer_name STRING,
    payer_ifsc STRING,
    payer_account STRING,
    payee_vpa STRING,
    payee_name STRING,
    payee_ifsc STRING,
    payee_account STRING,
    amount DECIMAL(18,5),
    currency STRING,
    purpose_code STRING,
    remittance_info STRING,
    device_id STRING,
    raw_json STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

-- Additional Real-Time Payment Systems
CREATE TABLE IF NOT EXISTS bronze_paynow (
    raw_id STRING NOT NULL,
    transaction_id STRING,
    creation_datetime TIMESTAMP,
    payer_uen STRING,
    payer_nric STRING,
    payer_mobile STRING,
    payer_name STRING,
    payer_bank_code STRING,
    payer_account STRING,
    payee_uen STRING,
    payee_nric STRING,
    payee_mobile STRING,
    payee_name STRING,
    payee_bank_code STRING,
    payee_account STRING,
    amount DECIMAL(18,5),
    currency STRING,
    reference STRING,
    raw_json STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_promptpay (
    raw_id STRING NOT NULL,
    transaction_id STRING,
    creation_datetime TIMESTAMP,
    payer_promptpay_id STRING,
    payer_name STRING,
    payer_bank_code STRING,
    payer_account STRING,
    payee_promptpay_id STRING,
    payee_name STRING,
    payee_bank_code STRING,
    payee_account STRING,
    amount DECIMAL(18,5),
    currency STRING,
    reference STRING,
    raw_json STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_instapay (
    raw_id STRING NOT NULL,
    transaction_id STRING,
    creation_datetime TIMESTAMP,
    sender_bank_code STRING,
    sender_account STRING,
    sender_name STRING,
    receiver_bank_code STRING,
    receiver_account STRING,
    receiver_name STRING,
    amount DECIMAL(18,5),
    currency STRING,
    reference STRING,
    raw_json STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

-- ============================================================================
-- RTGS Systems
-- ============================================================================

CREATE TABLE IF NOT EXISTS bronze_target2 (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    settlement_date DATE,
    settlement_method STRING,
    sender_bic STRING,
    receiver_bic STRING,
    amount DECIMAL(18,5),
    currency STRING,
    debtor_name STRING,
    debtor_iban STRING,
    creditor_name STRING,
    creditor_iban STRING,
    end_to_end_id STRING,
    raw_xml STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_bojnet (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    settlement_date DATE,
    sender_bank_code STRING,
    receiver_bank_code STRING,
    amount DECIMAL(18,5),
    currency STRING,
    remittance_info STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_cnaps (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    settlement_date DATE,
    sender_cnaps_code STRING,
    receiver_cnaps_code STRING,
    amount DECIMAL(18,5),
    currency STRING,
    payer_name STRING,
    payer_account STRING,
    payee_name STRING,
    payee_account STRING,
    purpose_code STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_meps_plus (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    settlement_date DATE,
    sender_bank_code STRING,
    receiver_bank_code STRING,
    amount DECIMAL(18,5),
    currency STRING,
    remittance_info STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_rtgs_hk (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    settlement_date DATE,
    sender_bank_code STRING,
    receiver_bank_code STRING,
    amount DECIMAL(18,5),
    currency STRING,
    remittance_info STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_sarie (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    settlement_date DATE,
    sender_bank_code STRING,
    receiver_bank_code STRING,
    amount DECIMAL(18,5),
    currency STRING,
    payer_name STRING,
    payee_name STRING,
    purpose_code STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_uaefts (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    settlement_date DATE,
    sender_bank_code STRING,
    receiver_bank_code STRING,
    amount DECIMAL(18,5),
    currency STRING,
    payer_name STRING,
    payee_name STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

CREATE TABLE IF NOT EXISTS bronze_kftc (
    raw_id STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    settlement_date DATE,
    sender_bank_code STRING,
    receiver_bank_code STRING,
    amount DECIMAL(18,5),
    currency STRING,
    payer_name STRING,
    payee_name STRING,
    raw_message STRING,
    file_name STRING,
    source_system STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP DEFAULT current_timestamp()
)
USING DELTA
PARTITIONED BY (DATE(_ingested_at));

-- ============================================================================
-- Create indexes and optimize tables
-- ============================================================================

-- Note: Databricks Delta automatically creates indexes on partition columns
-- Additional OPTIMIZE and ZORDER commands can be run periodically for performance
