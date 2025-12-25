-- ============================================================================
-- GPS CDM - Gold Layer Tables (Common Data Model)
-- ============================================================================
-- Fully normalized CDM entities supporting all regulatory reporting requirements
-- Designed to generate: FinCEN SAR/CTR, AUSTRAC IFTI/TTR/SMR, FINTRAC STR/LCTR,
-- UK SAR, OFAC Blocking, OECD CRS, FATCA 8966, PSD2 Fraud, and 23 other reports
-- ============================================================================

USE CATALOG ${catalog};
USE SCHEMA ${schema};

-- ============================================================================
-- CDM PARTY - Individuals, Organizations, Beneficial Owners
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_cdm_party (
    party_id STRING NOT NULL,
    party_type STRING NOT NULL,  -- INDIVIDUAL, ORGANIZATION, TRUST, GOVERNMENT

    -- Core Identification
    name STRING NOT NULL,
    legal_name STRING,
    trade_name STRING,
    family_name STRING,
    given_name STRING,
    middle_name STRING,
    name_suffix STRING,
    name_prefix STRING,
    title STRING,
    gender STRING,

    -- Address - Primary
    address_type STRING,
    address_line1 STRING,
    address_line2 STRING,
    address_line3 STRING,
    street_name STRING,
    building_number STRING,
    suite_floor_apt STRING,
    city STRING,
    postal_code STRING,
    state_province STRING,
    country STRING,
    country_subdivision STRING,
    district_name STRING,
    post_box STRING,

    -- Address - Additional/Former
    former_address_line1 STRING,
    former_city STRING,
    former_country STRING,

    -- Identification Documents
    identification_type STRING,
    identification_number STRING,
    identification_issuing_country STRING,
    identification_issuing_state STRING,
    identification_expiry_date DATE,
    passport_number STRING,
    passport_country STRING,
    driving_licence_number STRING,
    national_insurance_number STRING,
    national_id_number STRING,

    -- Tax Identification
    tax_identification_number STRING,
    tax_id_type STRING,
    us_tin STRING,
    us_tin_type STRING,
    foreign_tin STRING,
    foreign_tin_issuing_country STRING,
    tin_unavailable_reason STRING,

    -- Organization Identifiers
    bic STRING,
    lei STRING,
    company_registration_number STRING,
    australian_business_number STRING,
    australian_company_number STRING,
    australian_registered_body_number STRING,
    tax_file_number STRING,
    incorporation_number STRING,
    incorporation_jurisdiction STRING,

    -- Biographical Data (Individuals)
    date_of_birth DATE,
    place_of_birth STRING,
    city_of_birth STRING,
    country_of_birth STRING,
    nationality STRING,
    country_of_residence STRING,
    country_of_domicile STRING,

    -- Occupation & Employment
    occupation STRING,
    employer STRING,
    nature_of_business STRING,
    business_name STRING,

    -- Contact Information
    phone_number STRING,
    residence_phone_number STRING,
    work_phone_number STRING,
    mobile_phone_number STRING,
    email_address STRING,
    website_url STRING,

    -- Financial Information
    source_of_wealth STRING,
    source_of_funds STRING,
    estimated_net_worth DECIMAL(18,2),
    expected_activity STRING,
    expected_monthly_volume INT,
    expected_monthly_dollar_volume DECIMAL(18,2),

    -- Risk & Compliance
    risk_rating STRING,
    risk_rating_date DATE,
    client_number STRING,
    customer_verified BOOLEAN,
    verification_method STRING,
    enhanced_due_diligence BOOLEAN,
    sanctions_screening_conducted BOOLEAN,
    sanctions_match BOOLEAN,
    sanctions_list STRING,

    -- PEP Status
    is_pep BOOLEAN,
    pep_relationship STRING,

    -- US Person Status (FATCA)
    is_us_person BOOLEAN,

    -- Relationship
    relationship_to_institution STRING,
    relationship_begin_date DATE,

    -- Aliases
    aliases STRING,  -- JSON array

    -- SDN/Sanctions Fields
    sdn_list_name STRING,
    sdn_list_id STRING,
    sdn_type STRING,
    sdn_program_codes STRING,  -- JSON array
    match_type STRING,
    match_strength STRING,
    name_match_percentage DECIMAL(5,2),

    -- Beneficial Owner Fields
    beneficial_owner_identified BOOLEAN,
    beneficial_owner_percent DECIMAL(5,2),

    -- CRS Classification
    crs_entity_type STRING,
    crs_controlling_person_type STRING,

    -- FATCA Classification
    fatca_classification STRING,

    -- Audit
    created_at TIMESTAMP DEFAULT current_timestamp(),
    updated_at TIMESTAMP DEFAULT current_timestamp(),
    created_by STRING,
    updated_by STRING,
    _batch_id STRING,
    _source_system STRING
)
USING DELTA
PARTITIONED BY (party_type);

-- ============================================================================
-- CDM ACCOUNT - All Account Types
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_cdm_account (
    account_id STRING NOT NULL,
    party_id STRING,

    -- Core Account Info
    account_number STRING NOT NULL,
    account_type STRING,
    account_name STRING,
    account_currency STRING,
    account_status STRING,

    -- International Identifiers
    iban STRING,
    bic_swift STRING,
    sort_code STRING,
    routing_number STRING,
    financial_institution_number STRING,
    branch_transit_number STRING,

    -- Account Lifecycle
    account_open_date DATE,
    account_closed_date DATE,
    account_closure_reason STRING,
    closed_by_institution BOOLEAN,
    dormant_account BOOLEAN,
    reactivation_date DATE,
    next_review_date DATE,
    risk_assessment_date DATE,

    -- Balance Information
    current_balance DECIMAL(18,2),
    account_balance_for_tax_reporting DECIMAL(18,2),
    total_deposits DECIMAL(18,2),
    account_balance_usd DECIMAL(18,2),

    -- Account Holder Relationship
    account_holder_type STRING,
    account_holder_relationship STRING,

    -- CRS/FATCA Fields
    preexisting_account BOOLEAN,
    high_value_account BOOLEAN,
    undocumented_account BOOLEAN,
    self_certification_date DATE,
    documentary_evidence BOOLEAN,
    crs_account_type STRING,

    -- Due Diligence
    due_diligence_account_type STRING,
    risk_classification STRING,
    account_purpose STRING,
    private_banking_purpose STRING,

    -- Account Status Flags
    frozen_indicator BOOLEAN,
    frozen_date DATE,
    unfrozen_date DATE,

    -- PIX/Instant Payment Fields
    pix_key STRING,
    pix_key_type STRING,
    dict_entry_id STRING,
    dict_key_status STRING,
    dict_registration_date DATE,

    -- Audit
    created_at TIMESTAMP DEFAULT current_timestamp(),
    updated_at TIMESTAMP DEFAULT current_timestamp(),
    _batch_id STRING,
    _source_system STRING
)
USING DELTA
PARTITIONED BY (account_type);

-- ============================================================================
-- CDM FINANCIAL INSTITUTION
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_cdm_financial_institution (
    fi_id STRING NOT NULL,

    -- Core Identification
    institution_name STRING NOT NULL,
    institution_type STRING,
    institution_abbreviation STRING,
    country STRING,

    -- Regulatory Identifiers
    bic STRING,
    lei STRING,
    routing_number STRING,
    sort_code STRING,
    clearing_member_id STRING,
    national_clearing_code STRING,
    rssd_id STRING,
    msb_registration_number STRING,
    giin STRING,

    -- Tax Identification
    tax_identification_number STRING,
    tin_type STRING,
    registration_number STRING,

    -- Regulatory Oversight
    primary_regulator STRING,
    primary_regulator_other STRING,
    regulatory_authority STRING,

    -- Business Information
    business_activity STRING,
    business_activity_code STRING,
    naics_code STRING,
    fi_type STRING,
    fi_type_other STRING,

    -- Address
    street_address STRING,
    address_line2 STRING,
    city STRING,
    state_code STRING,
    postal_code STRING,

    -- Branch Information
    branch_name STRING,
    branch_tin STRING,
    branch_street_address STRING,
    branch_city STRING,
    branch_state_code STRING,
    branch_postal_code STRING,
    branch_country STRING,
    branch_type STRING,
    branch_department_id STRING,
    branch_identification STRING,

    -- Contact Information
    contact_officer_name STRING,
    contact_title STRING,
    contact_phone_number STRING,
    contact_phone_extension STRING,
    contact_email STRING,
    bsa_officer_name STRING,
    bsa_officer_phone STRING,
    bsa_officer_email STRING,
    mlro_name STRING,
    mlro_phone_number STRING,
    mlro_email_address STRING,

    -- FATCA Fields
    fatca_reporting_type STRING,

    -- Foreign Bank Assessment (Form 312)
    foreign_bank_name STRING,
    foreign_bank_country STRING,
    foreign_bank_license_number STRING,
    foreign_bank_regulator STRING,
    foreign_bank_bic STRING,
    is_shell_bank BOOLEAN,
    has_physical_presence BOOLEAN,
    physical_presence_address STRING,
    is_regulated BOOLEAN,
    banking_license_type STRING,
    accepts_retail_deposits BOOLEAN,
    primary_business_activities STRING,
    ownership_structure STRING,
    parent_company_name STRING,
    parent_company_country STRING,
    largest_shareholder_percent DECIMAL(5,2),
    number_of_employees INT,

    -- AML Program Assessment
    has_aml_program BOOLEAN,
    aml_program_rating STRING,
    screens_against_ofac BOOLEAN,
    files_suspicious_activity_reports BOOLEAN,
    performs_cdd BOOLEAN,
    performs_edd BOOLEAN,
    monitors_transactions BOOLEAN,
    aml_officer_name STRING,
    aml_officer_email STRING,
    aml_officer_phone STRING,
    aml_program_review_date DATE,
    aml_info_source STRING,

    -- Country Risk Assessment
    country_risk_rating STRING,
    is_fatf_member BOOLEAN,
    on_fatf_blacklist BOOLEAN,
    on_fatf_greylist BOOLEAN,
    corruption_perception_index INT,
    us_sanctions_against_country BOOLEAN,
    un_sanctions_against_country BOOLEAN,
    is_tax_haven BOOLEAN,

    -- Audit
    created_at TIMESTAMP DEFAULT current_timestamp(),
    updated_at TIMESTAMP DEFAULT current_timestamp(),
    _batch_id STRING,
    _source_system STRING
)
USING DELTA
PARTITIONED BY (institution_type);

-- ============================================================================
-- CDM PAYMENT INSTRUCTION - All Payment Types
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_cdm_payment_instruction (
    instruction_id STRING NOT NULL,
    stg_id STRING,

    -- Message Identification
    message_type STRING NOT NULL,
    message_id STRING,
    payment_type STRING,

    -- Transaction IDs
    end_to_end_id STRING,
    transaction_id STRING,
    instruction_identification STRING,
    uetr STRING,
    clearing_system_reference STRING,

    -- Party References
    debtor_party_id STRING,
    creditor_party_id STRING,
    ultimate_debtor_party_id STRING,
    ultimate_creditor_party_id STRING,

    -- Account References
    debtor_account_id STRING,
    creditor_account_id STRING,

    -- FI References
    debtor_agent_id STRING,
    creditor_agent_id STRING,
    intermediary_agent1_id STRING,
    intermediary_agent2_id STRING,
    intermediary_agent3_id STRING,
    instructing_agent_id STRING,
    instructed_agent_id STRING,

    -- Amounts
    instructed_amount DECIMAL(18,5),
    instructed_currency STRING,
    interbank_settlement_amount DECIMAL(18,5),
    interbank_settlement_currency STRING,
    equivalent_amount DECIMAL(18,5),
    equivalent_currency STRING,
    exchange_rate DECIMAL(12,6),

    -- Charges
    charge_bearer STRING,
    charges_amount DECIMAL(18,5),
    charges_currency STRING,

    -- Dates & Times
    creation_datetime TIMESTAMP,
    requested_execution_date DATE,
    requested_collection_date DATE,
    value_date DATE,
    settlement_date DATE,
    interbank_settlement_date DATE,
    acceptance_datetime TIMESTAMP,
    debit_datetime TIMESTAMP,
    credit_datetime TIMESTAMP,

    -- Payment Type Information
    payment_method STRING,
    service_level STRING,
    local_instrument STRING,
    category_purpose STRING,
    instruction_priority STRING,
    settlement_method STRING,
    clearing_system STRING,
    clearing_channel STRING,

    -- Purpose
    purpose_code STRING,
    purpose_proprietary STRING,

    -- Remittance
    remittance_unstructured STRING,
    remittance_creditor_reference STRING,
    remittance_document_type STRING,
    remittance_document_number STRING,
    remittance_document_date DATE,
    remittance_due_amount DECIMAL(18,5),

    -- Regulatory
    regulatory_reporting_code STRING,
    regulatory_authority_name STRING,
    regulatory_authority_country STRING,
    regulatory_information STRING,

    -- Direct Debit Specific
    mandate_id STRING,
    mandate_date_of_signature DATE,
    sequence_type STRING,
    amendment_indicator BOOLEAN,
    creditor_scheme_id STRING,

    -- Return/Reversal Information
    return_reason_code STRING,
    return_reason_info STRING,
    original_message_id STRING,
    original_end_to_end_id STRING,
    original_uetr STRING,

    -- Status
    status STRING,
    status_reason_code STRING,
    status_reason_info STRING,

    -- Cross-Border Flag
    cross_border BOOLEAN,

    -- Fraud Detection (Real-Time Payments)
    fraud_score INT,
    fraud_risk_level STRING,
    payer_ip_address STRING,
    payer_device_id STRING,
    payer_geolocation STRING,

    -- SWIFT MT Specific
    bank_operation_code STRING,
    sender_to_receiver_info STRING,

    -- Batch Information
    batch_booking BOOLEAN,
    number_of_transactions INT,
    control_sum DECIMAL(18,5),

    -- Audit
    created_at TIMESTAMP DEFAULT current_timestamp(),
    updated_at TIMESTAMP DEFAULT current_timestamp(),
    _batch_id STRING,
    _source_system STRING
)
USING DELTA
PARTITIONED BY (message_type);

-- ============================================================================
-- CDM TRANSACTION - Cash and Non-Payment Transactions
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_cdm_transaction (
    transaction_id STRING NOT NULL,

    -- Core Transaction Data
    transaction_type STRING NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_time TIME,
    transaction_datetime TIMESTAMP,

    -- Amount
    amount DECIMAL(18,5) NOT NULL,
    currency STRING NOT NULL,
    amount_usd DECIMAL(18,5),
    exchange_rate DECIMAL(12,6),

    -- Reference
    transaction_reference STRING,
    end_to_end_id STRING,
    batch_number STRING,

    -- Party References
    originator_party_id STRING,
    beneficiary_party_id STRING,

    -- Account References
    debit_account_id STRING,
    credit_account_id STRING,

    -- FI References
    debit_institution_id STRING,
    credit_institution_id STRING,
    intermediary_institution_id STRING,

    -- Transaction Routing
    wire_transfer_direction STRING,
    transfer_direction STRING,
    payment_method STRING,
    swift_message_type STRING,
    channel_code STRING,

    -- Cash Transaction Details
    cash_in_amount DECIMAL(18,5),
    cash_in_currency STRING,
    cash_out_amount DECIMAL(18,5),
    cash_out_currency STRING,
    foreign_cash_in_amount DECIMAL(18,5),
    foreign_cash_in_currency STRING,
    foreign_cash_out_amount DECIMAL(18,5),
    foreign_cash_out_currency STRING,
    cash_in_instruments STRING,  -- JSON
    cash_out_instruments STRING,  -- JSON

    -- Transaction Indicators
    multiple_transactions_indicator BOOLEAN,
    twenty_four_hour_rule_indicator BOOLEAN,
    ministerial_directive_indicator BOOLEAN,

    -- Transaction Purpose
    transaction_purpose STRING,
    source_of_funds STRING,
    source_of_cash STRING,
    disposition_of_funds STRING,
    disposition_of_cash STRING,
    remittance_information STRING,

    -- AUSTRAC LCTR Fields
    starting_action_type STRING,
    starting_action_details STRING,
    completing_action_type STRING,
    completing_action_details STRING,

    -- Transaction Status
    transaction_status STRING,
    attempted_transaction BOOLEAN,
    transaction_refused BOOLEAN,
    refusal_reason STRING,

    -- Audit
    created_at TIMESTAMP DEFAULT current_timestamp(),
    updated_at TIMESTAMP DEFAULT current_timestamp(),
    _batch_id STRING,
    _source_system STRING
)
USING DELTA
PARTITIONED BY (transaction_type);

-- ============================================================================
-- CDM REGULATORY REPORT - All Report Types
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_cdm_regulatory_report (
    report_id STRING NOT NULL,

    -- Report Identification
    report_type STRING NOT NULL,
    jurisdiction STRING NOT NULL,
    report_reference_number STRING,
    submission_date TIMESTAMP,
    filing_date DATE,
    report_status STRING,
    reporting_year INT,
    reporting_period STRING,
    reporting_entity_reference_number STRING,

    -- Reporting Entity Reference
    reporting_entity_fi_id STRING,

    -- Subject Matter Fields
    suspicious_activity_from_date DATE,
    suspicious_activity_to_date DATE,
    total_amount_involved DECIMAL(18,2),
    narrative_description STRING,
    continuing_activity BOOLEAN,
    corrected_report BOOLEAN,

    -- Financial Data Fields
    total_cash_in DECIMAL(18,2),
    total_cash_out DECIMAL(18,2),
    total_dividends DECIMAL(18,2),
    total_interest DECIMAL(18,2),
    total_gross_proceeds DECIMAL(18,2),
    total_other_income DECIMAL(18,2),

    -- Contact Information
    contact_person_name STRING,
    contact_person_phone STRING,
    contact_person_email STRING,
    alternate_contact_name STRING,
    alternate_contact_phone STRING,
    alternate_contact_email STRING,

    -- Reference Fields
    prior_report_bsa_id STRING,
    bsa_identifier STRING,
    acknowledgment_number STRING,
    fintrac_acknowledgment_number STRING,
    austrac_acknowledgment_number STRING,
    fincen_acceptance_date DATE,

    -- SAR-Specific Fields
    sar_report_type STRING,
    disclosure_route STRING,
    reason_for_reporting STRING,
    money_laundering_suspected BOOLEAN,
    terrorist_financing_suspected BOOLEAN,
    suspicion_basis STRING,
    suspicion_arose_date DATE,
    related_previous_sar STRING,
    other_disclosures_made BOOLEAN,
    suspicion_type STRING,  -- JSON array
    predicate_offence STRING,  -- JSON array
    geographic_risk STRING,  -- JSON array
    red_flag_indicators STRING,  -- JSON array
    supporting_documentation BOOLEAN,
    deviation_from_expected STRING,

    -- CRS/FATCA Fields
    message_type_indic STRING,
    reporting_period_end DATE,
    pool_report_type STRING,
    number_of_accounts_in_pool INT,
    aggregate_account_balance DECIMAL(18,2),
    aggregate_payment_amount DECIMAL(18,2),
    doc_type_indic STRING,
    doc_ref_id STRING,
    corrected_doc_ref_id STRING,
    payment_types STRING,  -- JSON array
    payment_amounts STRING,  -- JSON array
    payment_currencies STRING,  -- JSON array
    schema_version STRING,
    warning_text STRING,
    pool_balance_currency STRING,
    pool_payments_currency STRING,
    giin STRING,

    -- OFAC Blocking Fields
    blocking_date DATE,
    blocking_time TIME,
    blocking_action_type STRING,
    blocking_reason STRING,  -- JSON array
    sanctions_program STRING,  -- JSON array
    property_released BOOLEAN,
    release_date DATE,
    release_reason STRING,
    ofac_license_number STRING,
    immediate_phone_notification BOOLEAN,
    blocked_property_value DECIMAL(18,2),
    original_currency STRING,
    original_currency_amount DECIMAL(18,2),
    property_type STRING,  -- JSON array

    -- Law Enforcement
    law_enforcement_notified BOOLEAN,
    law_enforcement_agency STRING,
    law_enforcement_reference STRING,
    law_enforcement_contact_date DATE,
    action_taken STRING,

    -- Audit
    created_at TIMESTAMP DEFAULT current_timestamp(),
    updated_at TIMESTAMP DEFAULT current_timestamp(),
    created_by STRING,
    _batch_id STRING,
    _source_system STRING
)
USING DELTA
PARTITIONED BY (report_type, jurisdiction);

-- ============================================================================
-- CDM COMPLIANCE CASE - Investigations and Blocking
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_cdm_compliance_case (
    case_id STRING NOT NULL,

    -- Case Identification
    case_status STRING,
    case_type STRING,
    suspicion_indicator STRING,
    suspicion_formed_date DATE,
    date_created DATE,
    date_closed DATE,

    -- Suspicion Details
    suspicion_description STRING,
    ml_tf_indicators STRING,
    action_taken STRING,

    -- Related Report
    regulatory_report_id STRING,

    -- OFAC Blocking
    blocking_date DATE,
    blocking_time TIME,
    blocking_action_type STRING,
    blocking_reason STRING,
    sanctions_program STRING,
    property_released BOOLEAN,
    release_date DATE,
    release_reason STRING,
    blocked_property_value DECIMAL(18,2),
    property_type STRING,
    original_currency STRING,
    original_currency_amount DECIMAL(18,2),
    ofac_license_number STRING,
    immediate_phone_notification BOOLEAN,

    -- Investigation
    investigation_conducted BOOLEAN,
    investigation_findings STRING,
    source_of_funds_determination STRING,

    -- Documentation
    supporting_documentation BOOLEAN,
    additional_comments STRING,

    -- Audit
    created_at TIMESTAMP DEFAULT current_timestamp(),
    updated_at TIMESTAMP DEFAULT current_timestamp(),
    _batch_id STRING,
    _source_system STRING
)
USING DELTA
PARTITIONED BY (case_type);

-- ============================================================================
-- CDM CHARGES - Payment Charges/Fees
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_cdm_charges (
    charge_id STRING NOT NULL,
    payment_instruction_id STRING,

    -- Charge Details
    charge_type STRING,
    charge_amount DECIMAL(18,5),
    charge_currency STRING,
    charge_agent_id STRING,
    charge_agent_bic STRING,

    -- Audit
    created_at TIMESTAMP DEFAULT current_timestamp(),
    _batch_id STRING
)
USING DELTA;

-- ============================================================================
-- CDM TAX RESIDENCIES - Multiple Tax Residences per Party
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_cdm_tax_residencies (
    tax_residency_id STRING NOT NULL,
    party_id STRING NOT NULL,

    -- Tax Residence Details
    country STRING NOT NULL,
    tin STRING,
    tin_type STRING,
    tin_unavailable_reason STRING,

    -- Audit
    created_at TIMESTAMP DEFAULT current_timestamp(),
    _batch_id STRING
)
USING DELTA;

-- ============================================================================
-- CDM STATEMENT ENTRIES - Account Statement Line Items
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_cdm_statement_entries (
    entry_id STRING NOT NULL,
    statement_id STRING,
    account_id STRING,

    -- Entry Details
    entry_reference STRING,
    entry_amount DECIMAL(18,5),
    entry_currency STRING,
    credit_debit STRING,
    entry_status STRING,
    booking_date DATE,
    value_date DATE,

    -- Transaction Reference
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

    -- Audit
    created_at TIMESTAMP DEFAULT current_timestamp(),
    _batch_id STRING
)
USING DELTA
PARTITIONED BY (DATE(booking_date));

-- ============================================================================
-- Relationship Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_cdm_party_account_rel (
    rel_id STRING NOT NULL,
    party_id STRING NOT NULL,
    account_id STRING NOT NULL,
    relationship_type STRING,  -- HOLDER, SIGNATORY, BENEFICIARY, POWER_OF_ATTORNEY
    relationship_start_date DATE,
    relationship_end_date DATE,
    is_primary BOOLEAN,
    created_at TIMESTAMP DEFAULT current_timestamp(),
    _batch_id STRING
)
USING DELTA;

CREATE TABLE IF NOT EXISTS gold_cdm_party_fi_rel (
    rel_id STRING NOT NULL,
    party_id STRING NOT NULL,
    fi_id STRING NOT NULL,
    relationship_type STRING,  -- EMPLOYEE, OFFICER, DIRECTOR, CUSTOMER
    relationship_start_date DATE,
    relationship_end_date DATE,
    created_at TIMESTAMP DEFAULT current_timestamp(),
    _batch_id STRING
)
USING DELTA;

CREATE TABLE IF NOT EXISTS gold_cdm_beneficial_owner_rel (
    rel_id STRING NOT NULL,
    entity_party_id STRING NOT NULL,
    owner_party_id STRING NOT NULL,
    ownership_percentage DECIMAL(5,2),
    control_type STRING,  -- OWNERSHIP, CONTROL, OTHER
    is_verified BOOLEAN,
    verification_date DATE,
    created_at TIMESTAMP DEFAULT current_timestamp(),
    _batch_id STRING
)
USING DELTA;

CREATE TABLE IF NOT EXISTS gold_cdm_report_party_rel (
    rel_id STRING NOT NULL,
    report_id STRING NOT NULL,
    party_id STRING NOT NULL,
    party_role STRING,  -- SUBJECT, FILER, CONTACT, BENEFICIAL_OWNER, SIGNATORY
    created_at TIMESTAMP DEFAULT current_timestamp(),
    _batch_id STRING
)
USING DELTA;

CREATE TABLE IF NOT EXISTS gold_cdm_report_transaction_rel (
    rel_id STRING NOT NULL,
    report_id STRING NOT NULL,
    transaction_id STRING,
    payment_instruction_id STRING,
    created_at TIMESTAMP DEFAULT current_timestamp(),
    _batch_id STRING
)
USING DELTA;

CREATE TABLE IF NOT EXISTS gold_cdm_report_account_rel (
    rel_id STRING NOT NULL,
    report_id STRING NOT NULL,
    account_id STRING NOT NULL,
    account_role STRING,  -- AFFECTED, BLOCKED, REPORTED
    created_at TIMESTAMP DEFAULT current_timestamp(),
    _batch_id STRING
)
USING DELTA;

-- ============================================================================
-- Create Foreign Key Constraints (Informational - Not Enforced by Databricks)
-- ============================================================================

-- Note: Databricks Delta does not enforce FK constraints but documents relationships
-- These can be used by BI tools and data catalogs

-- ALTER TABLE gold_cdm_account ADD CONSTRAINT fk_account_party
--     FOREIGN KEY (party_id) REFERENCES gold_cdm_party(party_id);

-- ALTER TABLE gold_cdm_payment_instruction ADD CONSTRAINT fk_payment_debtor
--     FOREIGN KEY (debtor_party_id) REFERENCES gold_cdm_party(party_id);

-- etc.

-- ============================================================================
-- Create Indexes via OPTIMIZE + ZORDER
-- ============================================================================

-- Run these periodically for query performance:
-- OPTIMIZE gold_cdm_party ZORDER BY (party_id, name, country);
-- OPTIMIZE gold_cdm_account ZORDER BY (account_id, party_id, account_number);
-- OPTIMIZE gold_cdm_payment_instruction ZORDER BY (instruction_id, message_type, end_to_end_id);
-- OPTIMIZE gold_cdm_transaction ZORDER BY (transaction_id, transaction_date, transaction_type);
-- OPTIMIZE gold_cdm_regulatory_report ZORDER BY (report_id, report_type, jurisdiction);
