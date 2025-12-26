-- =============================================================================
-- GPS CDM - Zone Transformation Mappings
-- =============================================================================
-- Database-driven field mappings for Bronze → Silver → Gold transformations.
-- Enables dynamic INSERT statement generation based on message type.
--
-- Benefits:
-- 1. No code changes needed to add new message formats
-- 2. Batch INSERT optimization through dynamic SQL generation
-- 3. Centralized mapping management
-- 4. Audit trail for mapping changes
-- =============================================================================

-- Create mapping schema for better organization
CREATE SCHEMA IF NOT EXISTS mapping;

-- =============================================================================
-- Message Format Registry
-- =============================================================================
-- Master list of supported message formats with metadata
CREATE TABLE IF NOT EXISTS mapping.message_formats (
    format_id VARCHAR(50) PRIMARY KEY,
    format_name VARCHAR(100) NOT NULL,
    format_category VARCHAR(30) NOT NULL,  -- 'ISO20022', 'SWIFT_MT', 'REGIONAL', 'PROPRIETARY'
    schema_version VARCHAR(20),
    description TEXT,
    bronze_table VARCHAR(100) DEFAULT 'raw_payment_messages',
    silver_table VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'SYSTEM'
);

-- =============================================================================
-- Silver Zone Field Mappings
-- =============================================================================
-- Maps source JSON paths to target Silver table columns
CREATE TABLE IF NOT EXISTS mapping.silver_field_mappings (
    mapping_id SERIAL PRIMARY KEY,
    format_id VARCHAR(50) NOT NULL REFERENCES mapping.message_formats(format_id),
    target_column VARCHAR(100) NOT NULL,
    source_path VARCHAR(500) NOT NULL,  -- JSON path, e.g., 'debtor.name', 'paymentInformation.paymentMethod'
    data_type VARCHAR(30) NOT NULL DEFAULT 'VARCHAR',  -- VARCHAR, INTEGER, DECIMAL, TIMESTAMP, JSONB, BOOLEAN
    max_length INTEGER,  -- For VARCHAR truncation
    is_required BOOLEAN DEFAULT FALSE,
    default_value TEXT,
    transform_function VARCHAR(100),  -- Optional: 'TO_UPPER', 'TO_DATE', 'TRIM', etc.
    transform_expression TEXT,  -- Custom SQL expression for complex transforms
    ordinal_position INTEGER NOT NULL,  -- Column order for INSERT
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(format_id, target_column)
);

-- Index for fast lookups by format
CREATE INDEX IF NOT EXISTS idx_silver_mappings_format
    ON mapping.silver_field_mappings(format_id, is_active, ordinal_position);

-- =============================================================================
-- Gold Zone Field Mappings
-- =============================================================================
-- Maps Silver columns to Gold entity tables
CREATE TABLE IF NOT EXISTS mapping.gold_field_mappings (
    mapping_id SERIAL PRIMARY KEY,
    format_id VARCHAR(50) NOT NULL REFERENCES mapping.message_formats(format_id),
    gold_table VARCHAR(100) NOT NULL,  -- 'cdm_party', 'cdm_account', 'cdm_financial_institution', 'cdm_payment_instruction'
    gold_column VARCHAR(100) NOT NULL,
    source_expression VARCHAR(500) NOT NULL,  -- Silver column name or expression
    entity_role VARCHAR(50),  -- 'DEBTOR', 'CREDITOR', 'DEBTOR_AGENT', 'CREDITOR_AGENT', etc.
    data_type VARCHAR(30) NOT NULL DEFAULT 'VARCHAR',
    is_required BOOLEAN DEFAULT FALSE,
    default_value TEXT,
    transform_expression TEXT,
    ordinal_position INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(format_id, gold_table, gold_column, entity_role)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_gold_mappings_format
    ON mapping.gold_field_mappings(format_id, gold_table, is_active, ordinal_position);

-- =============================================================================
-- Mapping Version History (for audit trail)
-- =============================================================================
CREATE TABLE IF NOT EXISTS mapping.mapping_history (
    history_id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,  -- 'silver_field_mappings' or 'gold_field_mappings'
    mapping_id INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL,  -- 'INSERT', 'UPDATE', 'DELETE'
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100) DEFAULT 'SYSTEM',
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- Insert Core Message Format Registrations
-- =============================================================================
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description) VALUES
    -- ISO 20022 Messages
    ('pain.001', 'Customer Credit Transfer Initiation', 'ISO20022', 'stg_pain001', 'ISO 20022 pain.001 - Customer initiating credit transfers'),
    ('pain.002', 'Customer Payment Status Report', 'ISO20022', 'stg_pain002', 'ISO 20022 pain.002 - Payment status report from bank to customer'),
    ('pain.008', 'Customer Direct Debit Initiation', 'ISO20022', 'stg_pain008', 'ISO 20022 pain.008 - Customer initiating direct debits'),
    ('pacs.002', 'FI Payment Status Report', 'ISO20022', 'stg_pacs002', 'ISO 20022 pacs.002 - Interbank payment status report'),
    ('pacs.003', 'FI Direct Debit', 'ISO20022', 'stg_pacs003', 'ISO 20022 pacs.003 - Interbank direct debit'),
    ('pacs.004', 'Payment Return', 'ISO20022', 'stg_pacs004', 'ISO 20022 pacs.004 - Payment return message'),
    ('pacs.008', 'FI Credit Transfer', 'ISO20022', 'stg_pacs008', 'ISO 20022 pacs.008 - Interbank credit transfer'),
    ('pacs.009', 'FI Credit Transfer', 'ISO20022', 'stg_pacs009', 'ISO 20022 pacs.009 - Financial institution credit transfer'),
    ('camt.052', 'Account Report', 'ISO20022', 'stg_camt052', 'ISO 20022 camt.052 - Intraday account report'),
    ('camt.053', 'Account Statement', 'ISO20022', 'stg_camt053', 'ISO 20022 camt.053 - End-of-day account statement'),
    ('camt.054', 'Credit/Debit Notification', 'ISO20022', 'stg_camt054', 'ISO 20022 camt.054 - Credit/debit notifications'),

    -- SWIFT MT Messages
    ('MT103', 'Single Customer Credit Transfer', 'SWIFT_MT', 'stg_mt103', 'SWIFT MT103 - Single customer credit transfer'),
    ('MT103STP', 'Single Customer Credit Transfer STP', 'SWIFT_MT', 'stg_mt103', 'SWIFT MT103 STP - Straight through processing variant'),
    ('MT101', 'Request for Transfer', 'SWIFT_MT', 'stg_mt101', 'SWIFT MT101 - Request for transfer'),
    ('MT202', 'General Financial Institution Transfer', 'SWIFT_MT', 'stg_mt202', 'SWIFT MT202 - Bank-to-bank transfer'),
    ('MT202COV', 'Cover Payment', 'SWIFT_MT', 'stg_mt202', 'SWIFT MT202 COV - Cover payment for MT103'),
    ('MT199', 'Free Format Message', 'SWIFT_MT', 'stg_mt199', 'SWIFT MT199 - Free format message for exceptions'),
    ('MT900', 'Confirmation of Debit', 'SWIFT_MT', 'stg_mt900', 'SWIFT MT900 - Debit confirmation'),
    ('MT910', 'Confirmation of Credit', 'SWIFT_MT', 'stg_mt910', 'SWIFT MT910 - Credit confirmation'),
    ('MT940', 'Customer Statement', 'SWIFT_MT', 'stg_mt940', 'SWIFT MT940 - Customer account statement'),
    ('MT950', 'Statement Message', 'SWIFT_MT', 'stg_mt950', 'SWIFT MT950 - Statement message'),

    -- Regional Payment Systems
    ('FEDWIRE', 'Fedwire Funds Transfer', 'REGIONAL', 'stg_fedwire', 'US Federal Reserve Wire Network'),
    ('CHIPS', 'CHIPS Payment', 'REGIONAL', 'stg_chips', 'US Clearing House Interbank Payments System'),
    ('ACH', 'ACH Payment', 'REGIONAL', 'stg_ach', 'US Automated Clearing House'),
    ('SEPA_SCT', 'SEPA Credit Transfer', 'REGIONAL', 'stg_sepa_sct', 'Single Euro Payments Area Credit Transfer'),
    ('SEPA_SDD', 'SEPA Direct Debit', 'REGIONAL', 'stg_sepa_sdd', 'Single Euro Payments Area Direct Debit'),
    ('SEPA_INST', 'SEPA Instant', 'REGIONAL', 'stg_sepa_inst', 'SEPA Instant Credit Transfer'),
    ('BACS', 'UK BACS Payment', 'REGIONAL', 'stg_bacs', 'UK Bankers Automated Clearing Services'),
    ('CHAPS', 'UK CHAPS Payment', 'REGIONAL', 'stg_chaps', 'UK Clearing House Automated Payment System'),
    ('FPS', 'UK Faster Payments', 'REGIONAL', 'stg_fps', 'UK Faster Payments Service'),
    ('NPP', 'Australia New Payments Platform', 'REGIONAL', 'stg_npp', 'Australia New Payments Platform'),
    ('RTGS', 'Real Time Gross Settlement', 'REGIONAL', 'stg_rtgs', 'Generic RTGS system')
ON CONFLICT (format_id) DO UPDATE SET
    updated_at = CURRENT_TIMESTAMP;

-- =============================================================================
-- Insert Silver Field Mappings for pain.001
-- =============================================================================
INSERT INTO mapping.silver_field_mappings
    (format_id, target_column, source_path, data_type, max_length, is_required, ordinal_position)
VALUES
    -- Core identifiers (generated, not from source)
    ('pain.001', 'stg_id', '_GENERATED_UUID', 'VARCHAR', 36, TRUE, 1),
    ('pain.001', 'raw_id', '_RAW_ID', 'VARCHAR', 36, TRUE, 2),

    -- Message header
    ('pain.001', 'msg_id', 'messageId', 'VARCHAR', 35, TRUE, 3),
    ('pain.001', 'creation_date_time', 'creationDateTime', 'TIMESTAMP', NULL, FALSE, 4),
    ('pain.001', 'number_of_transactions', 'numberOfTransactions', 'INTEGER', NULL, FALSE, 5),
    ('pain.001', 'control_sum', 'controlSum', 'DECIMAL', NULL, FALSE, 6),

    -- Initiating party
    ('pain.001', 'initiating_party_name', 'initiatingParty.name', 'VARCHAR', 140, FALSE, 7),
    ('pain.001', 'initiating_party_id', 'initiatingParty.id', 'VARCHAR', 35, FALSE, 8),

    -- Payment info
    ('pain.001', 'payment_info_id', 'paymentInformation.paymentInfoId', 'VARCHAR', 35, FALSE, 9),
    ('pain.001', 'payment_method', 'paymentInformation.paymentMethod', 'VARCHAR', 3, FALSE, 10),
    ('pain.001', 'batch_booking', 'paymentInformation.batchBooking', 'BOOLEAN', NULL, FALSE, 11),
    ('pain.001', 'requested_execution_date', 'paymentInformation.requestedExecutionDate', 'DATE', NULL, FALSE, 12),

    -- Debtor
    ('pain.001', 'debtor_name', 'debtor.name', 'VARCHAR', 140, FALSE, 13),
    ('pain.001', 'debtor_street_name', 'debtor.streetName', 'VARCHAR', 70, FALSE, 14),
    ('pain.001', 'debtor_building_number', 'debtor.buildingNumber', 'VARCHAR', 16, FALSE, 15),
    ('pain.001', 'debtor_postal_code', 'debtor.postalCode', 'VARCHAR', 16, FALSE, 16),
    ('pain.001', 'debtor_town_name', 'debtor.townName', 'VARCHAR', 35, FALSE, 17),
    ('pain.001', 'debtor_country', 'debtor.country', 'VARCHAR', 2, FALSE, 18),
    ('pain.001', 'debtor_id', 'debtor.id', 'VARCHAR', 35, FALSE, 19),
    ('pain.001', 'debtor_id_type', 'debtor.idType', 'VARCHAR', 35, FALSE, 20),

    -- Debtor account
    ('pain.001', 'debtor_account_iban', 'debtorAccount.iban', 'VARCHAR', 34, FALSE, 21),
    ('pain.001', 'debtor_account_other', 'debtorAccount.other', 'VARCHAR', 34, FALSE, 22),
    ('pain.001', 'debtor_account_currency', 'debtorAccount.currency', 'VARCHAR', 3, FALSE, 23),

    -- Debtor agent
    ('pain.001', 'debtor_agent_bic', 'debtorAgent.bic', 'VARCHAR', 11, FALSE, 24),
    ('pain.001', 'debtor_agent_name', 'debtorAgent.name', 'VARCHAR', 140, FALSE, 25),
    ('pain.001', 'debtor_agent_clearing_system', 'debtorAgent.clearingSystem', 'VARCHAR', 35, FALSE, 26),
    ('pain.001', 'debtor_agent_member_id', 'debtorAgent.memberId', 'VARCHAR', 35, FALSE, 27),

    -- Instruction
    ('pain.001', 'instruction_id', 'instructionId', 'VARCHAR', 35, FALSE, 28),
    ('pain.001', 'end_to_end_id', 'endToEndId', 'VARCHAR', 35, FALSE, 29),
    ('pain.001', 'uetr', 'uetr', 'VARCHAR', 36, FALSE, 30),

    -- Amounts
    ('pain.001', 'instructed_amount', 'instructedAmount', 'DECIMAL', NULL, FALSE, 31),
    ('pain.001', 'instructed_currency', 'instructedCurrency', 'VARCHAR', 3, FALSE, 32),
    ('pain.001', 'equivalent_amount', 'equivalentAmount', 'DECIMAL', NULL, FALSE, 33),
    ('pain.001', 'equivalent_currency', 'equivalentCurrency', 'VARCHAR', 3, FALSE, 34),

    -- Creditor agent
    ('pain.001', 'creditor_agent_bic', 'creditorAgent.bic', 'VARCHAR', 11, FALSE, 35),
    ('pain.001', 'creditor_agent_name', 'creditorAgent.name', 'VARCHAR', 140, FALSE, 36),
    ('pain.001', 'creditor_agent_clearing_system', 'creditorAgent.clearingSystem', 'VARCHAR', 35, FALSE, 37),
    ('pain.001', 'creditor_agent_member_id', 'creditorAgent.memberId', 'VARCHAR', 35, FALSE, 38),

    -- Creditor
    ('pain.001', 'creditor_name', 'creditor.name', 'VARCHAR', 140, FALSE, 39),
    ('pain.001', 'creditor_street_name', 'creditor.streetName', 'VARCHAR', 70, FALSE, 40),
    ('pain.001', 'creditor_building_number', 'creditor.buildingNumber', 'VARCHAR', 16, FALSE, 41),
    ('pain.001', 'creditor_postal_code', 'creditor.postalCode', 'VARCHAR', 16, FALSE, 42),
    ('pain.001', 'creditor_town_name', 'creditor.townName', 'VARCHAR', 35, FALSE, 43),
    ('pain.001', 'creditor_country', 'creditor.country', 'VARCHAR', 2, FALSE, 44),
    ('pain.001', 'creditor_id', 'creditor.id', 'VARCHAR', 35, FALSE, 45),
    ('pain.001', 'creditor_id_type', 'creditor.idType', 'VARCHAR', 35, FALSE, 46),

    -- Creditor account
    ('pain.001', 'creditor_account_iban', 'creditorAccount.iban', 'VARCHAR', 34, FALSE, 47),
    ('pain.001', 'creditor_account_other', 'creditorAccount.other', 'VARCHAR', 34, FALSE, 48),
    ('pain.001', 'creditor_account_currency', 'creditorAccount.currency', 'VARCHAR', 3, FALSE, 49),

    -- Purpose & charges
    ('pain.001', 'purpose_code', 'purposeCode', 'VARCHAR', 4, FALSE, 50),
    ('pain.001', 'purpose_proprietary', 'purposeProprietary', 'VARCHAR', 35, FALSE, 51),
    ('pain.001', 'charge_bearer', 'chargeBearer', 'VARCHAR', 4, FALSE, 52),

    -- Remittance & regulatory (stored as JSON)
    ('pain.001', 'remittance_information', 'remittanceInformation.unstructured', 'VARCHAR', 140, FALSE, 53),
    ('pain.001', 'structured_remittance', 'remittanceInformation.structured', 'JSONB', NULL, FALSE, 54),
    ('pain.001', 'regulatory_reporting', 'regulatoryReporting', 'JSONB', NULL, FALSE, 55),

    -- Batch info
    ('pain.001', '_batch_id', '_BATCH_ID', 'VARCHAR', 36, TRUE, 56),

    -- Extended fields
    ('pain.001', 'initiating_party_id_type', 'initiatingParty.idType', 'VARCHAR', 35, FALSE, 57),
    ('pain.001', 'initiating_party_country', 'initiatingParty.country', 'VARCHAR', 2, FALSE, 58),
    ('pain.001', 'service_level', 'paymentInformation.serviceLevel', 'VARCHAR', 35, FALSE, 59),
    ('pain.001', 'local_instrument', 'paymentInformation.localInstrument', 'VARCHAR', 35, FALSE, 60),
    ('pain.001', 'category_purpose', 'paymentInformation.categoryPurpose', 'VARCHAR', 35, FALSE, 61),
    ('pain.001', 'debtor_country_sub_division', 'debtor.countrySubDivision', 'VARCHAR', 35, FALSE, 62),
    ('pain.001', 'debtor_account_type', 'debtorAccount.accountType', 'VARCHAR', 35, FALSE, 63),
    ('pain.001', 'debtor_agent_country', 'debtorAgent.country', 'VARCHAR', 2, FALSE, 64),
    ('pain.001', 'exchange_rate', 'exchangeRate', 'DECIMAL', NULL, FALSE, 65),
    ('pain.001', 'creditor_country_sub_division', 'creditor.countrySubDivision', 'VARCHAR', 35, FALSE, 66),
    ('pain.001', 'creditor_account_type', 'creditorAccount.accountType', 'VARCHAR', 35, FALSE, 67),
    ('pain.001', 'creditor_agent_country', 'creditorAgent.country', 'VARCHAR', 2, FALSE, 68),
    ('pain.001', 'ultimate_debtor_name', 'ultimateDebtor.name', 'VARCHAR', 140, FALSE, 69),
    ('pain.001', 'ultimate_debtor_id', 'ultimateDebtor.id', 'VARCHAR', 35, FALSE, 70),
    ('pain.001', 'ultimate_debtor_id_type', 'ultimateDebtor.idType', 'VARCHAR', 35, FALSE, 71),
    ('pain.001', 'ultimate_creditor_name', 'ultimateCreditor.name', 'VARCHAR', 140, FALSE, 72),
    ('pain.001', 'ultimate_creditor_id', 'ultimateCreditor.id', 'VARCHAR', 35, FALSE, 73),
    ('pain.001', 'ultimate_creditor_id_type', 'ultimateCreditor.idType', 'VARCHAR', 35, FALSE, 74)
ON CONFLICT (format_id, target_column) DO UPDATE SET
    source_path = EXCLUDED.source_path,
    data_type = EXCLUDED.data_type,
    max_length = EXCLUDED.max_length,
    ordinal_position = EXCLUDED.ordinal_position,
    updated_at = CURRENT_TIMESTAMP;

-- =============================================================================
-- Insert Silver Field Mappings for MT103
-- =============================================================================
INSERT INTO mapping.silver_field_mappings
    (format_id, target_column, source_path, data_type, max_length, is_required, ordinal_position)
VALUES
    ('MT103', 'stg_id', '_GENERATED_UUID', 'VARCHAR', 36, TRUE, 1),
    ('MT103', 'raw_id', '_RAW_ID', 'VARCHAR', 36, TRUE, 2),
    ('MT103', 'sender_bic', 'senderBIC', 'VARCHAR', 11, FALSE, 3),
    ('MT103', 'receiver_bic', 'receiverBIC', 'VARCHAR', 11, FALSE, 4),
    ('MT103', 'senders_reference', 'sendersReference', 'VARCHAR', 16, FALSE, 5),
    ('MT103', 'related_reference', 'relatedReference', 'VARCHAR', 16, FALSE, 6),
    ('MT103', 'bank_operation_code', 'bankOperationCode', 'VARCHAR', 4, FALSE, 7),
    ('MT103', 'instruction_codes', 'instructionCodes', 'JSONB', NULL, FALSE, 8),
    ('MT103', 'value_date', 'valueDate', 'DATE', NULL, FALSE, 9),
    ('MT103', 'currency', 'currency', 'VARCHAR', 3, FALSE, 10),
    ('MT103', 'amount', 'amount', 'DECIMAL', NULL, FALSE, 11),
    ('MT103', 'instructed_currency', 'instructedCurrency', 'VARCHAR', 3, FALSE, 12),
    ('MT103', 'instructed_amount', 'instructedAmount', 'DECIMAL', NULL, FALSE, 13),
    ('MT103', 'exchange_rate', 'exchangeRate', 'DECIMAL', NULL, FALSE, 14),
    ('MT103', 'ordering_customer_account', 'orderingCustomer.account', 'VARCHAR', 35, FALSE, 15),
    ('MT103', 'ordering_customer_name', 'orderingCustomer.name', 'VARCHAR', 140, FALSE, 16),
    ('MT103', 'ordering_customer_address', 'orderingCustomer.address', 'VARCHAR', 140, FALSE, 17),
    ('MT103', 'ordering_customer_country', 'orderingCustomer.country', 'VARCHAR', 2, FALSE, 18),
    ('MT103', 'ordering_institution_bic', 'orderingInstitution.bic', 'VARCHAR', 11, FALSE, 19),
    ('MT103', 'ordering_institution_name', 'orderingInstitution.name', 'VARCHAR', 140, FALSE, 20),
    ('MT103', 'senders_correspondent_bic', 'sendersCorrespondent.bic', 'VARCHAR', 11, FALSE, 21),
    ('MT103', 'receivers_correspondent_bic', 'receiversCorrespondent.bic', 'VARCHAR', 11, FALSE, 22),
    ('MT103', 'intermediary_institution_bic', 'intermediaryInstitution.bic', 'VARCHAR', 11, FALSE, 23),
    ('MT103', 'account_with_institution_bic', 'accountWithInstitution.bic', 'VARCHAR', 11, FALSE, 24),
    ('MT103', 'beneficiary_customer_account', 'beneficiaryCustomer.account', 'VARCHAR', 35, FALSE, 25),
    ('MT103', 'beneficiary_customer_name', 'beneficiaryCustomer.name', 'VARCHAR', 140, FALSE, 26),
    ('MT103', 'beneficiary_customer_address', 'beneficiaryCustomer.address', 'VARCHAR', 140, FALSE, 27),
    ('MT103', 'beneficiary_customer_country', 'beneficiaryCustomer.country', 'VARCHAR', 2, FALSE, 28),
    ('MT103', 'remittance_information', 'remittanceInformation', 'VARCHAR', 140, FALSE, 29),
    ('MT103', 'details_of_charges', 'detailsOfCharges', 'VARCHAR', 3, FALSE, 30),
    ('MT103', 'sender_to_receiver_info', 'senderToReceiverInfo', 'VARCHAR', 210, FALSE, 31),
    ('MT103', 'regulatory_reporting', 'regulatoryReporting', 'JSONB', NULL, FALSE, 32),
    ('MT103', '_batch_id', '_BATCH_ID', 'VARCHAR', 36, TRUE, 33)
ON CONFLICT (format_id, target_column) DO UPDATE SET
    source_path = EXCLUDED.source_path,
    updated_at = CURRENT_TIMESTAMP;

-- =============================================================================
-- Insert Silver Field Mappings for FEDWIRE
-- =============================================================================
INSERT INTO mapping.silver_field_mappings
    (format_id, target_column, source_path, data_type, max_length, is_required, ordinal_position)
VALUES
    ('FEDWIRE', 'stg_id', '_GENERATED_UUID', 'VARCHAR', 36, TRUE, 1),
    ('FEDWIRE', 'raw_id', '_RAW_ID', 'VARCHAR', 36, TRUE, 2),
    ('FEDWIRE', 'message_id', 'messageId', 'VARCHAR', 35, FALSE, 3),
    ('FEDWIRE', 'type_code', 'typeCode', 'VARCHAR', 4, FALSE, 4),
    ('FEDWIRE', 'subtype_code', 'subtypeCode', 'VARCHAR', 4, FALSE, 5),
    ('FEDWIRE', 'imad', 'imad', 'VARCHAR', 22, FALSE, 6),
    ('FEDWIRE', 'omad', 'omad', 'VARCHAR', 22, FALSE, 7),
    ('FEDWIRE', 'input_cycle_date', 'inputCycleDate', 'DATE', NULL, FALSE, 8),
    ('FEDWIRE', 'input_source', 'inputSource', 'VARCHAR', 8, FALSE, 9),
    ('FEDWIRE', 'input_sequence_number', 'inputSequenceNumber', 'VARCHAR', 6, FALSE, 10),
    ('FEDWIRE', 'amount', 'amount', 'DECIMAL', NULL, FALSE, 11),
    ('FEDWIRE', 'currency', 'currency', 'VARCHAR', 3, FALSE, 12),
    ('FEDWIRE', 'sender_reference', 'senderReference', 'VARCHAR', 16, FALSE, 13),
    ('FEDWIRE', 'business_function_code', 'businessFunctionCode', 'VARCHAR', 3, FALSE, 14),
    ('FEDWIRE', 'sender_routing_number', 'sender.routingNumber', 'VARCHAR', 9, FALSE, 15),
    ('FEDWIRE', 'sender_name', 'sender.name', 'VARCHAR', 140, FALSE, 16),
    ('FEDWIRE', 'sender_bic', 'sender.bic', 'VARCHAR', 11, FALSE, 17),
    ('FEDWIRE', 'receiver_routing_number', 'receiver.routingNumber', 'VARCHAR', 9, FALSE, 18),
    ('FEDWIRE', 'receiver_name', 'receiver.name', 'VARCHAR', 140, FALSE, 19),
    ('FEDWIRE', 'receiver_bic', 'receiver.bic', 'VARCHAR', 11, FALSE, 20),
    ('FEDWIRE', 'originator_name', 'originator.name', 'VARCHAR', 140, FALSE, 21),
    ('FEDWIRE', 'originator_account_number', 'originator.accountNumber', 'VARCHAR', 35, FALSE, 22),
    ('FEDWIRE', 'originator_address', 'originator.address.line1', 'VARCHAR', 140, FALSE, 23),
    ('FEDWIRE', 'originator_city', 'originator.address.city', 'VARCHAR', 35, FALSE, 24),
    ('FEDWIRE', 'originator_state', 'originator.address.state', 'VARCHAR', 2, FALSE, 25),
    ('FEDWIRE', 'originator_country', 'originator.address.country', 'VARCHAR', 2, FALSE, 26),
    ('FEDWIRE', 'beneficiary_name', 'beneficiary.name', 'VARCHAR', 140, FALSE, 27),
    ('FEDWIRE', 'beneficiary_account_number', 'beneficiary.accountNumber', 'VARCHAR', 35, FALSE, 28),
    ('FEDWIRE', 'beneficiary_address', 'beneficiary.address.line1', 'VARCHAR', 140, FALSE, 29),
    ('FEDWIRE', 'beneficiary_city', 'beneficiary.address.city', 'VARCHAR', 35, FALSE, 30),
    ('FEDWIRE', 'beneficiary_state', 'beneficiary.address.state', 'VARCHAR', 2, FALSE, 31),
    ('FEDWIRE', 'beneficiary_country', 'beneficiary.address.country', 'VARCHAR', 2, FALSE, 32),
    ('FEDWIRE', 'beneficiary_bank_routing_number', 'beneficiaryBank.routingNumber', 'VARCHAR', 9, FALSE, 33),
    ('FEDWIRE', 'beneficiary_bank_name', 'beneficiaryBank.name', 'VARCHAR', 140, FALSE, 34),
    ('FEDWIRE', 'originator_to_beneficiary_info', 'originatorToBeneficiaryInfo', 'VARCHAR', 140, FALSE, 35),
    ('FEDWIRE', 'fi_to_fi_info', 'fiToFiInfo', 'VARCHAR', 210, FALSE, 36),
    ('FEDWIRE', 'charge_details', 'chargeDetails', 'VARCHAR', 3, FALSE, 37),
    ('FEDWIRE', '_batch_id', '_BATCH_ID', 'VARCHAR', 36, TRUE, 38)
ON CONFLICT (format_id, target_column) DO UPDATE SET
    source_path = EXCLUDED.source_path,
    updated_at = CURRENT_TIMESTAMP;

-- =============================================================================
-- Insert Gold Field Mappings for cdm_party (pain.001 example)
-- =============================================================================
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position)
VALUES
    -- Debtor party
    ('pain.001', 'cdm_party', 'party_id', '_GENERATED_UUID', 'DEBTOR', 'VARCHAR', TRUE, 1),
    ('pain.001', 'cdm_party', 'name', 'debtor_name', 'DEBTOR', 'VARCHAR', TRUE, 2),
    ('pain.001', 'cdm_party', 'party_type', '''ORGANIZATION''', 'DEBTOR', 'VARCHAR', FALSE, 3),
    ('pain.001', 'cdm_party', 'country', 'debtor_country', 'DEBTOR', 'VARCHAR', FALSE, 4),
    ('pain.001', 'cdm_party', 'street_address', 'debtor_street_name', 'DEBTOR', 'VARCHAR', FALSE, 5),
    ('pain.001', 'cdm_party', 'city', 'debtor_town_name', 'DEBTOR', 'VARCHAR', FALSE, 6),
    ('pain.001', 'cdm_party', 'postal_code', 'debtor_postal_code', 'DEBTOR', 'VARCHAR', FALSE, 7),
    ('pain.001', 'cdm_party', 'state_province', 'debtor_country_sub_division', 'DEBTOR', 'VARCHAR', FALSE, 8),

    -- Creditor party
    ('pain.001', 'cdm_party', 'party_id', '_GENERATED_UUID', 'CREDITOR', 'VARCHAR', TRUE, 1),
    ('pain.001', 'cdm_party', 'name', 'creditor_name', 'CREDITOR', 'VARCHAR', TRUE, 2),
    ('pain.001', 'cdm_party', 'party_type', '''ORGANIZATION''', 'CREDITOR', 'VARCHAR', FALSE, 3),
    ('pain.001', 'cdm_party', 'country', 'creditor_country', 'CREDITOR', 'VARCHAR', FALSE, 4),
    ('pain.001', 'cdm_party', 'street_address', 'creditor_street_name', 'CREDITOR', 'VARCHAR', FALSE, 5),
    ('pain.001', 'cdm_party', 'city', 'creditor_town_name', 'CREDITOR', 'VARCHAR', FALSE, 6),
    ('pain.001', 'cdm_party', 'postal_code', 'creditor_postal_code', 'CREDITOR', 'VARCHAR', FALSE, 7),
    ('pain.001', 'cdm_party', 'state_province', 'creditor_country_sub_division', 'CREDITOR', 'VARCHAR', FALSE, 8)
ON CONFLICT (format_id, gold_table, gold_column, entity_role) DO UPDATE SET
    source_expression = EXCLUDED.source_expression,
    updated_at = CURRENT_TIMESTAMP;

-- =============================================================================
-- Function: Get Silver Mapping Columns
-- =============================================================================
CREATE OR REPLACE FUNCTION mapping.get_silver_columns(p_format_id VARCHAR)
RETURNS TABLE (
    target_column VARCHAR,
    source_path VARCHAR,
    data_type VARCHAR,
    max_length INTEGER,
    ordinal_position INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sfm.target_column::VARCHAR,
        sfm.source_path::VARCHAR,
        sfm.data_type::VARCHAR,
        sfm.max_length,
        sfm.ordinal_position
    FROM mapping.silver_field_mappings sfm
    WHERE sfm.format_id = p_format_id
      AND sfm.is_active = TRUE
    ORDER BY sfm.ordinal_position;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Function: Generate Silver INSERT SQL
-- =============================================================================
CREATE OR REPLACE FUNCTION mapping.generate_silver_insert_sql(p_format_id VARCHAR)
RETURNS TEXT AS $$
DECLARE
    v_table_name VARCHAR;
    v_columns TEXT;
    v_placeholders TEXT;
    v_sql TEXT;
BEGIN
    -- Get target table
    SELECT silver_table INTO v_table_name
    FROM mapping.message_formats
    WHERE format_id = p_format_id AND is_active = TRUE;

    IF v_table_name IS NULL THEN
        RAISE EXCEPTION 'Unknown format_id: %', p_format_id;
    END IF;

    -- Build column list
    SELECT string_agg(target_column, ', ' ORDER BY ordinal_position) INTO v_columns
    FROM mapping.silver_field_mappings
    WHERE format_id = p_format_id AND is_active = TRUE;

    -- Build placeholder list
    SELECT string_agg('%s', ', ' ORDER BY ordinal_position) INTO v_placeholders
    FROM mapping.silver_field_mappings
    WHERE format_id = p_format_id AND is_active = TRUE;

    -- Build INSERT statement
    v_sql := format(
        'INSERT INTO silver.%I (%s) VALUES (%s) ON CONFLICT (stg_id) DO NOTHING RETURNING stg_id',
        v_table_name, v_columns, v_placeholders
    );

    RETURN v_sql;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- View: Active Mappings Summary
-- =============================================================================
CREATE OR REPLACE VIEW mapping.v_mapping_summary AS
SELECT
    mf.format_id,
    mf.format_name,
    mf.format_category,
    mf.silver_table,
    COUNT(DISTINCT sfm.target_column) as silver_column_count,
    COUNT(DISTINCT gfm.mapping_id) as gold_mapping_count,
    mf.is_active
FROM mapping.message_formats mf
LEFT JOIN mapping.silver_field_mappings sfm ON mf.format_id = sfm.format_id AND sfm.is_active = TRUE
LEFT JOIN mapping.gold_field_mappings gfm ON mf.format_id = gfm.format_id AND gfm.is_active = TRUE
GROUP BY mf.format_id, mf.format_name, mf.format_category, mf.silver_table, mf.is_active
ORDER BY mf.format_category, mf.format_id;

-- =============================================================================
-- Comments
-- =============================================================================
COMMENT ON SCHEMA mapping IS 'Database-driven field mappings for zone transformations';
COMMENT ON TABLE mapping.message_formats IS 'Registry of supported message formats with metadata';
COMMENT ON TABLE mapping.silver_field_mappings IS 'JSON path to Silver column mappings per message format';
COMMENT ON TABLE mapping.gold_field_mappings IS 'Silver column to Gold entity mappings per message format';
COMMENT ON FUNCTION mapping.get_silver_columns IS 'Returns ordered list of Silver columns for a message format';
COMMENT ON FUNCTION mapping.generate_silver_insert_sql IS 'Generates dynamic INSERT SQL for Silver table';
