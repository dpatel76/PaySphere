-- ============================================================================
-- MEPS_PLUS Field Coverage: Add missing columns and mappings for 100% coverage
-- ============================================================================

BEGIN;

-- ============================================================================
-- Part 1: Add missing columns to silver.stg_meps_plus
-- ============================================================================

-- App Header fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS business_message_identifier VARCHAR(255);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS business_service VARCHAR(255);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS copy_duplicate VARCHAR(50);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS app_header_creation_date TIMESTAMP;
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS from_bic VARCHAR(11);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS message_definition_identifier VARCHAR(255);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS possible_duplicate BOOLEAN;
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS to_bic VARCHAR(11);

-- Creditor (Financial Institution) fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_bic VARCHAR(11);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_clearing_system_code VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_clearing_system_member_id VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_lei VARCHAR(20);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_address_line1 VARCHAR(255);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_address_line2 VARCHAR(255);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_building_number VARCHAR(20);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_country VARCHAR(2);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_post_code VARCHAR(20);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_street_name VARCHAR(255);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_town_name VARCHAR(140);

-- Creditor Account fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_account_currency VARCHAR(3);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_account_iban VARCHAR(34);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_account_other VARCHAR(34);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_account_name VARCHAR(140);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_account_type VARCHAR(10);

-- Creditor Agent fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_agent_bic VARCHAR(11);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_agent_clearing_system_code VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_agent_clearing_member_id VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_agent_lei VARCHAR(20);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_agent_name VARCHAR(140);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_agent_country VARCHAR(2);

-- Charge fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS charge_bearer VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS charges_agent_bic VARCHAR(11);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS charges_amount NUMERIC(18,5);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS charges_currency VARCHAR(3);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS charge_type VARCHAR(10);

-- Debtor (Financial Institution) fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_bic VARCHAR(11);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_clearing_system_code VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_clearing_system_member_id VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_lei VARCHAR(20);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_address_line1 VARCHAR(255);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_address_line2 VARCHAR(255);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_building_number VARCHAR(20);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_country VARCHAR(2);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_post_code VARCHAR(20);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_street_name VARCHAR(255);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_town_name VARCHAR(140);

-- Debtor Account fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_account_currency VARCHAR(3);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_account_iban VARCHAR(34);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_account_other VARCHAR(34);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_account_name VARCHAR(140);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_account_type VARCHAR(10);

-- Debtor Agent fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_agent_bic VARCHAR(11);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_agent_clearing_system_code VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_agent_clearing_member_id VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_agent_lei VARCHAR(20);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_agent_name VARCHAR(140);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS debtor_agent_country VARCHAR(2);

-- Instruction fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS instruction_for_creditor_agent VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS instruction_for_creditor_agent_info VARCHAR(255);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS instruction_for_next_agent VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS instruction_for_next_agent_info VARCHAR(255);

-- Interbank Settlement fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS interbank_settlement_amount NUMERIC(18,5);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS interbank_settlement_currency VARCHAR(3);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS transaction_settlement_date DATE;

-- Intermediary Agent 1 fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS intermediary_agent1_bic VARCHAR(11);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS intermediary_agent1_lei VARCHAR(20);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS intermediary_agent1_name VARCHAR(140);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS intermediary_agent1_country VARCHAR(2);

-- Intermediary Agent 2 fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS intermediary_agent2_bic VARCHAR(11);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS intermediary_agent2_name VARCHAR(140);

-- Intermediary Agent 3 fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS intermediary_agent3_bic VARCHAR(11);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS intermediary_agent3_name VARCHAR(140);

-- Payment Identification fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS clearing_system_reference VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS end_to_end_identification VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS instruction_identification VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS transaction_identification VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS uetr VARCHAR(36);

-- Payment Type Information fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS clearing_channel_code VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS category_purpose_code VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS category_purpose_proprietary VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS instruction_priority VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS local_instrument_code VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS local_instrument_proprietary VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS settlement_priority VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS service_level_code VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS service_level_proprietary VARCHAR(35);

-- Previous Instructing Agent fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS previous_instructing_agent1_bic VARCHAR(11);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS previous_instructing_agent1_name VARCHAR(140);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS previous_instructing_agent2_bic VARCHAR(11);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS previous_instructing_agent3_bic VARCHAR(11);

-- Purpose fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS purpose_proprietary VARCHAR(35);

-- Regulatory Reporting fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS regulatory_authority_country VARCHAR(2);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS regulatory_authority_code VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS regulatory_reporting_code VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS regulatory_details_code VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS regulatory_details_info VARCHAR(255);

-- Remittance Information fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_reference VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS creditor_reference_type VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS invoice_number VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS invoice_date DATE;
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS remittance_unstructured TEXT;

-- Supplementary Data (MEPS+ specific)
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS liquidity_optimization BOOLEAN;
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS mas_reference_number VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS meps_sequence_number VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS payment_priority_meps VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS singapore_bank_code VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS singapore_branch_code VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS settlement_window VARCHAR(10);

-- Settlement Time fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS settlement_time_credit_dt_tm TIMESTAMP;
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS settlement_time_indication TIMESTAMP;
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS settlement_time_request TIME;

-- Group Header fields
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS group_header_creation_date_time TIMESTAMP;
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS instructed_agent_bic VARCHAR(11);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS instructed_agent_lei VARCHAR(20);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS instructed_agent_name VARCHAR(140);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS instructing_agent_bic VARCHAR(11);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS instructing_agent_lei VARCHAR(20);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS instructing_agent_name VARCHAR(140);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS interbank_settlement_date DATE;
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS message_identification VARCHAR(35);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS number_of_transactions INTEGER;
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS clearing_system_code VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS settlement_method VARCHAR(10);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS total_interbank_settlement_amount NUMERIC(18,5);
ALTER TABLE silver.stg_meps_plus ADD COLUMN IF NOT EXISTS total_interbank_settlement_currency VARCHAR(3);

COMMIT;

-- ============================================================================
-- Part 2: Clear existing MEPS_PLUS mappings and add all 128+ mappings
-- ============================================================================

BEGIN;

-- Remove existing MEPS_PLUS silver mappings to avoid duplicates
DELETE FROM mapping.silver_field_mappings WHERE format_id = 'MEPS_PLUS';

-- Insert all mappings with ordinal_position
-- source_path = field_path from standard_fields for traceability
-- parser_path is the snake_case key the parser outputs

-- System columns (3)
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'stg_id', '_GENERATED_UUID', NULL, 'VARCHAR', true, 1, true),
('MEPS_PLUS', 'raw_id', '_RAW_ID', NULL, 'VARCHAR', true, 2, true),
('MEPS_PLUS', '_batch_id', '_BATCH_ID', NULL, 'VARCHAR', false, 3, true),
('MEPS_PLUS', 'message_type', '_MESSAGE_TYPE', 'message_type', 'VARCHAR', false, 4, true);

-- App Header fields (8) - ordinal 5-12
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'business_message_identifier', 'AppHdr/BizMsgIdr', 'business_message_identifier', 'VARCHAR', false, 5, true),
('MEPS_PLUS', 'business_service', 'AppHdr/BizSvc', 'business_service', 'VARCHAR', false, 6, true),
('MEPS_PLUS', 'copy_duplicate', 'AppHdr/CpyDplct', 'copy_duplicate', 'VARCHAR', false, 7, true),
('MEPS_PLUS', 'app_header_creation_date', 'AppHdr/CreDt', 'app_header_creation_date', 'DATETIME', false, 8, true),
('MEPS_PLUS', 'from_bic', 'AppHdr/Fr/FIId/FinInstnId/BICFI', 'from_bic', 'VARCHAR', false, 9, true),
('MEPS_PLUS', 'message_definition_identifier', 'AppHdr/MsgDefIdr', 'message_definition_identifier', 'VARCHAR', false, 10, true),
('MEPS_PLUS', 'possible_duplicate', 'AppHdr/PssblDplct', 'possible_duplicate', 'BOOLEAN', false, 11, true),
('MEPS_PLUS', 'to_bic', 'AppHdr/To/FIId/FinInstnId/BICFI', 'to_bic', 'VARCHAR', false, 12, true);

-- Creditor (FI) fields (12) - ordinal 13-24
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'creditor_bic', 'Document/FICdtTrf/CdtTrfTxInf/Cdtr/FinInstnId/BICFI', 'creditor_bic', 'VARCHAR', true, 13, true),
('MEPS_PLUS', 'creditor_clearing_system_code', 'Document/FICdtTrf/CdtTrfTxInf/Cdtr/FinInstnId/ClrSysMmbId/ClrSysId/Cd', 'creditor_clearing_system_code', 'VARCHAR', false, 14, true),
('MEPS_PLUS', 'creditor_clearing_system_member_id', 'Document/FICdtTrf/CdtTrfTxInf/Cdtr/FinInstnId/ClrSysMmbId/MmbId', 'creditor_clearing_system_member_id', 'VARCHAR', false, 15, true),
('MEPS_PLUS', 'creditor_lei', 'Document/FICdtTrf/CdtTrfTxInf/Cdtr/FinInstnId/LEI', 'creditor_lei', 'VARCHAR', false, 16, true),
('MEPS_PLUS', 'creditor_name', 'Document/FICdtTrf/CdtTrfTxInf/Cdtr/FinInstnId/Nm', 'creditor_name', 'VARCHAR', false, 17, true),
('MEPS_PLUS', 'creditor_address_line1', 'Document/FICdtTrf/CdtTrfTxInf/Cdtr/FinInstnId/PstlAdr/AdrLine[1]', 'creditor_address_line1', 'VARCHAR', false, 18, true),
('MEPS_PLUS', 'creditor_address_line2', 'Document/FICdtTrf/CdtTrfTxInf/Cdtr/FinInstnId/PstlAdr/AdrLine[2]', 'creditor_address_line2', 'VARCHAR', false, 19, true),
('MEPS_PLUS', 'creditor_building_number', 'Document/FICdtTrf/CdtTrfTxInf/Cdtr/FinInstnId/PstlAdr/BldgNb', 'creditor_building_number', 'VARCHAR', false, 20, true),
('MEPS_PLUS', 'creditor_country', 'Document/FICdtTrf/CdtTrfTxInf/Cdtr/FinInstnId/PstlAdr/Ctry', 'creditor_country', 'VARCHAR', false, 21, true),
('MEPS_PLUS', 'creditor_post_code', 'Document/FICdtTrf/CdtTrfTxInf/Cdtr/FinInstnId/PstlAdr/PstCd', 'creditor_post_code', 'VARCHAR', false, 22, true),
('MEPS_PLUS', 'creditor_street_name', 'Document/FICdtTrf/CdtTrfTxInf/Cdtr/FinInstnId/PstlAdr/StrtNm', 'creditor_street_name', 'VARCHAR', false, 23, true),
('MEPS_PLUS', 'creditor_town_name', 'Document/FICdtTrf/CdtTrfTxInf/Cdtr/FinInstnId/PstlAdr/TwnNm', 'creditor_town_name', 'VARCHAR', false, 24, true);

-- Creditor Account fields (5) - ordinal 25-29
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'creditor_account_currency', 'Document/FICdtTrf/CdtTrfTxInf/CdtrAcct/Ccy', 'creditor_account_currency', 'VARCHAR', false, 25, true),
('MEPS_PLUS', 'creditor_account_iban', 'Document/FICdtTrf/CdtTrfTxInf/CdtrAcct/Id/IBAN', 'creditor_account_iban', 'VARCHAR', false, 26, true),
('MEPS_PLUS', 'creditor_account_other', 'Document/FICdtTrf/CdtTrfTxInf/CdtrAcct/Id/Othr/Id', 'creditor_account_other', 'VARCHAR', false, 27, true),
('MEPS_PLUS', 'creditor_account_name', 'Document/FICdtTrf/CdtTrfTxInf/CdtrAcct/Nm', 'creditor_account_name', 'VARCHAR', false, 28, true),
('MEPS_PLUS', 'creditor_account_type', 'Document/FICdtTrf/CdtTrfTxInf/CdtrAcct/Tp/Cd', 'creditor_account_type', 'VARCHAR', false, 29, true);

-- Creditor Agent fields (6) - ordinal 30-35
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'creditor_agent_bic', 'Document/FICdtTrf/CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI', 'creditor_agent_bic', 'VARCHAR', false, 30, true),
('MEPS_PLUS', 'creditor_agent_clearing_system_code', 'Document/FICdtTrf/CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd', 'creditor_agent_clearing_system_code', 'VARCHAR', false, 31, true),
('MEPS_PLUS', 'creditor_agent_clearing_member_id', 'Document/FICdtTrf/CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'creditor_agent_clearing_member_id', 'VARCHAR', false, 32, true),
('MEPS_PLUS', 'creditor_agent_lei', 'Document/FICdtTrf/CdtTrfTxInf/CdtrAgt/FinInstnId/LEI', 'creditor_agent_lei', 'VARCHAR', false, 33, true),
('MEPS_PLUS', 'creditor_agent_name', 'Document/FICdtTrf/CdtTrfTxInf/CdtrAgt/FinInstnId/Nm', 'creditor_agent_name', 'VARCHAR', false, 34, true),
('MEPS_PLUS', 'creditor_agent_country', 'Document/FICdtTrf/CdtTrfTxInf/CdtrAgt/FinInstnId/PstlAdr/Ctry', 'creditor_agent_country', 'VARCHAR', false, 35, true);

-- Charges fields (5) - ordinal 36-40
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'charge_bearer', 'Document/FICdtTrf/CdtTrfTxInf/ChrgBr', 'charge_bearer', 'VARCHAR', false, 36, true),
('MEPS_PLUS', 'charges_agent_bic', 'Document/FICdtTrf/CdtTrfTxInf/ChrgsInf/Agt/FinInstnId/BICFI', 'charges_agent_bic', 'VARCHAR', false, 37, true),
('MEPS_PLUS', 'charges_amount', 'Document/FICdtTrf/CdtTrfTxInf/ChrgsInf/Amt', 'charges_amount', 'DECIMAL', false, 38, true),
('MEPS_PLUS', 'charges_currency', 'Document/FICdtTrf/CdtTrfTxInf/ChrgsInf/Amt/@Ccy', 'charges_currency', 'VARCHAR', false, 39, true),
('MEPS_PLUS', 'charge_type', 'Document/FICdtTrf/CdtTrfTxInf/ChrgsInf/Tp/Cd', 'charge_type', 'VARCHAR', false, 40, true);

-- Debtor (FI) fields (12) - ordinal 41-52
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'debtor_bic', 'Document/FICdtTrf/CdtTrfTxInf/Dbtr/FinInstnId/BICFI', 'debtor_bic', 'VARCHAR', true, 41, true),
('MEPS_PLUS', 'debtor_clearing_system_code', 'Document/FICdtTrf/CdtTrfTxInf/Dbtr/FinInstnId/ClrSysMmbId/ClrSysId/Cd', 'debtor_clearing_system_code', 'VARCHAR', false, 42, true),
('MEPS_PLUS', 'debtor_clearing_system_member_id', 'Document/FICdtTrf/CdtTrfTxInf/Dbtr/FinInstnId/ClrSysMmbId/MmbId', 'debtor_clearing_system_member_id', 'VARCHAR', false, 43, true),
('MEPS_PLUS', 'debtor_lei', 'Document/FICdtTrf/CdtTrfTxInf/Dbtr/FinInstnId/LEI', 'debtor_lei', 'VARCHAR', false, 44, true),
('MEPS_PLUS', 'debtor_name', 'Document/FICdtTrf/CdtTrfTxInf/Dbtr/FinInstnId/Nm', 'debtor_name', 'VARCHAR', false, 45, true),
('MEPS_PLUS', 'debtor_address_line1', 'Document/FICdtTrf/CdtTrfTxInf/Dbtr/FinInstnId/PstlAdr/AdrLine[1]', 'debtor_address_line1', 'VARCHAR', false, 46, true),
('MEPS_PLUS', 'debtor_address_line2', 'Document/FICdtTrf/CdtTrfTxInf/Dbtr/FinInstnId/PstlAdr/AdrLine[2]', 'debtor_address_line2', 'VARCHAR', false, 47, true),
('MEPS_PLUS', 'debtor_building_number', 'Document/FICdtTrf/CdtTrfTxInf/Dbtr/FinInstnId/PstlAdr/BldgNb', 'debtor_building_number', 'VARCHAR', false, 48, true),
('MEPS_PLUS', 'debtor_country', 'Document/FICdtTrf/CdtTrfTxInf/Dbtr/FinInstnId/PstlAdr/Ctry', 'debtor_country', 'VARCHAR', false, 49, true),
('MEPS_PLUS', 'debtor_post_code', 'Document/FICdtTrf/CdtTrfTxInf/Dbtr/FinInstnId/PstlAdr/PstCd', 'debtor_post_code', 'VARCHAR', false, 50, true),
('MEPS_PLUS', 'debtor_street_name', 'Document/FICdtTrf/CdtTrfTxInf/Dbtr/FinInstnId/PstlAdr/StrtNm', 'debtor_street_name', 'VARCHAR', false, 51, true),
('MEPS_PLUS', 'debtor_town_name', 'Document/FICdtTrf/CdtTrfTxInf/Dbtr/FinInstnId/PstlAdr/TwnNm', 'debtor_town_name', 'VARCHAR', false, 52, true);

-- Debtor Account fields (5) - ordinal 53-57
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'debtor_account_currency', 'Document/FICdtTrf/CdtTrfTxInf/DbtrAcct/Ccy', 'debtor_account_currency', 'VARCHAR', false, 53, true),
('MEPS_PLUS', 'debtor_account_iban', 'Document/FICdtTrf/CdtTrfTxInf/DbtrAcct/Id/IBAN', 'debtor_account_iban', 'VARCHAR', false, 54, true),
('MEPS_PLUS', 'debtor_account_other', 'Document/FICdtTrf/CdtTrfTxInf/DbtrAcct/Id/Othr/Id', 'debtor_account_other', 'VARCHAR', false, 55, true),
('MEPS_PLUS', 'debtor_account_name', 'Document/FICdtTrf/CdtTrfTxInf/DbtrAcct/Nm', 'debtor_account_name', 'VARCHAR', false, 56, true),
('MEPS_PLUS', 'debtor_account_type', 'Document/FICdtTrf/CdtTrfTxInf/DbtrAcct/Tp/Cd', 'debtor_account_type', 'VARCHAR', false, 57, true);

-- Debtor Agent fields (6) - ordinal 58-63
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'debtor_agent_bic', 'Document/FICdtTrf/CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI', 'debtor_agent_bic', 'VARCHAR', false, 58, true),
('MEPS_PLUS', 'debtor_agent_clearing_system_code', 'Document/FICdtTrf/CdtTrfTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd', 'debtor_agent_clearing_system_code', 'VARCHAR', false, 59, true),
('MEPS_PLUS', 'debtor_agent_clearing_member_id', 'Document/FICdtTrf/CdtTrfTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'debtor_agent_clearing_member_id', 'VARCHAR', false, 60, true),
('MEPS_PLUS', 'debtor_agent_lei', 'Document/FICdtTrf/CdtTrfTxInf/DbtrAgt/FinInstnId/LEI', 'debtor_agent_lei', 'VARCHAR', false, 61, true),
('MEPS_PLUS', 'debtor_agent_name', 'Document/FICdtTrf/CdtTrfTxInf/DbtrAgt/FinInstnId/Nm', 'debtor_agent_name', 'VARCHAR', false, 62, true),
('MEPS_PLUS', 'debtor_agent_country', 'Document/FICdtTrf/CdtTrfTxInf/DbtrAgt/FinInstnId/PstlAdr/Ctry', 'debtor_agent_country', 'VARCHAR', false, 63, true);

-- Instruction fields (4) - ordinal 64-67
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'instruction_for_creditor_agent', 'Document/FICdtTrf/CdtTrfTxInf/InstrForCdtrAgt/Cd', 'instruction_for_creditor_agent', 'VARCHAR', false, 64, true),
('MEPS_PLUS', 'instruction_for_creditor_agent_info', 'Document/FICdtTrf/CdtTrfTxInf/InstrForCdtrAgt/InstrInf', 'instruction_for_creditor_agent_info', 'VARCHAR', false, 65, true),
('MEPS_PLUS', 'instruction_for_next_agent', 'Document/FICdtTrf/CdtTrfTxInf/InstrForNxtAgt/Cd', 'instruction_for_next_agent', 'VARCHAR', false, 66, true),
('MEPS_PLUS', 'instruction_for_next_agent_info', 'Document/FICdtTrf/CdtTrfTxInf/InstrForNxtAgt/InstrInf', 'instruction_for_next_agent_info', 'VARCHAR', false, 67, true);

-- Interbank Settlement fields (3) - ordinal 68-70
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'interbank_settlement_amount', 'Document/FICdtTrf/CdtTrfTxInf/IntrBkSttlmAmt', 'interbank_settlement_amount', 'DECIMAL', true, 68, true),
('MEPS_PLUS', 'interbank_settlement_currency', 'Document/FICdtTrf/CdtTrfTxInf/IntrBkSttlmAmt/@Ccy', 'interbank_settlement_currency', 'VARCHAR', true, 69, true),
('MEPS_PLUS', 'transaction_settlement_date', 'Document/FICdtTrf/CdtTrfTxInf/IntrBkSttlmDt', 'transaction_settlement_date', 'DATE', true, 70, true);

-- Intermediary Agent 1 fields (4) - ordinal 71-74
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'intermediary_agent1_bic', 'Document/FICdtTrf/CdtTrfTxInf/IntrmyAgt1/FinInstnId/BICFI', 'intermediary_agent1_bic', 'VARCHAR', false, 71, true),
('MEPS_PLUS', 'intermediary_agent1_lei', 'Document/FICdtTrf/CdtTrfTxInf/IntrmyAgt1/FinInstnId/LEI', 'intermediary_agent1_lei', 'VARCHAR', false, 72, true),
('MEPS_PLUS', 'intermediary_agent1_name', 'Document/FICdtTrf/CdtTrfTxInf/IntrmyAgt1/FinInstnId/Nm', 'intermediary_agent1_name', 'VARCHAR', false, 73, true),
('MEPS_PLUS', 'intermediary_agent1_country', 'Document/FICdtTrf/CdtTrfTxInf/IntrmyAgt1/FinInstnId/PstlAdr/Ctry', 'intermediary_agent1_country', 'VARCHAR', false, 74, true);

-- Intermediary Agent 2 fields (2) - ordinal 75-76
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'intermediary_agent2_bic', 'Document/FICdtTrf/CdtTrfTxInf/IntrmyAgt2/FinInstnId/BICFI', 'intermediary_agent2_bic', 'VARCHAR', false, 75, true),
('MEPS_PLUS', 'intermediary_agent2_name', 'Document/FICdtTrf/CdtTrfTxInf/IntrmyAgt2/FinInstnId/Nm', 'intermediary_agent2_name', 'VARCHAR', false, 76, true);

-- Intermediary Agent 3 fields (2) - ordinal 77-78
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'intermediary_agent3_bic', 'Document/FICdtTrf/CdtTrfTxInf/IntrmyAgt3/FinInstnId/BICFI', 'intermediary_agent3_bic', 'VARCHAR', false, 77, true),
('MEPS_PLUS', 'intermediary_agent3_name', 'Document/FICdtTrf/CdtTrfTxInf/IntrmyAgt3/FinInstnId/Nm', 'intermediary_agent3_name', 'VARCHAR', false, 78, true);

-- Payment Identification fields (5) - ordinal 79-83
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'clearing_system_reference', 'Document/FICdtTrf/CdtTrfTxInf/PmtId/ClrSysRef', 'clearing_system_reference', 'VARCHAR', false, 79, true),
('MEPS_PLUS', 'end_to_end_identification', 'Document/FICdtTrf/CdtTrfTxInf/PmtId/EndToEndId', 'end_to_end_identification', 'VARCHAR', true, 80, true),
('MEPS_PLUS', 'instruction_identification', 'Document/FICdtTrf/CdtTrfTxInf/PmtId/InstrId', 'instruction_identification', 'VARCHAR', false, 81, true),
('MEPS_PLUS', 'transaction_identification', 'Document/FICdtTrf/CdtTrfTxInf/PmtId/TxId', 'transaction_identification', 'VARCHAR', true, 82, true),
('MEPS_PLUS', 'uetr', 'Document/FICdtTrf/CdtTrfTxInf/PmtId/UETR', 'uetr', 'VARCHAR', true, 83, true);

-- Payment Type Information fields (9) - ordinal 84-92
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'clearing_channel_code', 'Document/FICdtTrf/CdtTrfTxInf/PmtTpInf/ClrChanl', 'clearing_channel_code', 'VARCHAR', false, 84, true),
('MEPS_PLUS', 'category_purpose_code', 'Document/FICdtTrf/CdtTrfTxInf/PmtTpInf/CtgyPurp/Cd', 'category_purpose_code', 'VARCHAR', false, 85, true),
('MEPS_PLUS', 'category_purpose_proprietary', 'Document/FICdtTrf/CdtTrfTxInf/PmtTpInf/CtgyPurp/Prtry', 'category_purpose_proprietary', 'VARCHAR', false, 86, true),
('MEPS_PLUS', 'instruction_priority', 'Document/FICdtTrf/CdtTrfTxInf/PmtTpInf/InstrPrty', 'instruction_priority', 'VARCHAR', false, 87, true),
('MEPS_PLUS', 'local_instrument_code', 'Document/FICdtTrf/CdtTrfTxInf/PmtTpInf/LclInstrm/Cd', 'local_instrument_code', 'VARCHAR', false, 88, true),
('MEPS_PLUS', 'local_instrument_proprietary', 'Document/FICdtTrf/CdtTrfTxInf/PmtTpInf/LclInstrm/Prtry', 'local_instrument_proprietary', 'VARCHAR', false, 89, true),
('MEPS_PLUS', 'settlement_priority', 'Document/FICdtTrf/CdtTrfTxInf/PmtTpInf/SttlmPrty', 'settlement_priority', 'VARCHAR', false, 90, true),
('MEPS_PLUS', 'service_level_code', 'Document/FICdtTrf/CdtTrfTxInf/PmtTpInf/SvcLvl/Cd', 'service_level_code', 'VARCHAR', true, 91, true),
('MEPS_PLUS', 'service_level_proprietary', 'Document/FICdtTrf/CdtTrfTxInf/PmtTpInf/SvcLvl/Prtry', 'service_level_proprietary', 'VARCHAR', false, 92, true);

-- Previous Instructing Agent fields (4) - ordinal 93-96
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'previous_instructing_agent1_bic', 'Document/FICdtTrf/CdtTrfTxInf/PrvsInstgAgt1/FinInstnId/BICFI', 'previous_instructing_agent1_bic', 'VARCHAR', false, 93, true),
('MEPS_PLUS', 'previous_instructing_agent1_name', 'Document/FICdtTrf/CdtTrfTxInf/PrvsInstgAgt1/FinInstnId/Nm', 'previous_instructing_agent1_name', 'VARCHAR', false, 94, true),
('MEPS_PLUS', 'previous_instructing_agent2_bic', 'Document/FICdtTrf/CdtTrfTxInf/PrvsInstgAgt2/FinInstnId/BICFI', 'previous_instructing_agent2_bic', 'VARCHAR', false, 95, true),
('MEPS_PLUS', 'previous_instructing_agent3_bic', 'Document/FICdtTrf/CdtTrfTxInf/PrvsInstgAgt3/FinInstnId/BICFI', 'previous_instructing_agent3_bic', 'VARCHAR', false, 96, true);

-- Purpose fields (2) - ordinal 97-98
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'purpose_code', 'Document/FICdtTrf/CdtTrfTxInf/Purp/Cd', 'purpose_code', 'VARCHAR', false, 97, true),
('MEPS_PLUS', 'purpose_proprietary', 'Document/FICdtTrf/CdtTrfTxInf/Purp/Prtry', 'purpose_proprietary', 'VARCHAR', false, 98, true);

-- Regulatory Reporting fields (5) - ordinal 99-103
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'regulatory_authority_country', 'Document/FICdtTrf/CdtTrfTxInf/RgltryRptg/Authrty/Ctry', 'regulatory_authority_country', 'VARCHAR', false, 99, true),
('MEPS_PLUS', 'regulatory_authority_code', 'Document/FICdtTrf/CdtTrfTxInf/RgltryRptg/Authrty/Nm', 'regulatory_authority_code', 'VARCHAR', false, 100, true),
('MEPS_PLUS', 'regulatory_reporting_code', 'Document/FICdtTrf/CdtTrfTxInf/RgltryRptg/DbtCdtRptgInd', 'regulatory_reporting_code', 'VARCHAR', false, 101, true),
('MEPS_PLUS', 'regulatory_details_code', 'Document/FICdtTrf/CdtTrfTxInf/RgltryRptg/Dtls/Cd', 'regulatory_details_code', 'VARCHAR', false, 102, true),
('MEPS_PLUS', 'regulatory_details_info', 'Document/FICdtTrf/CdtTrfTxInf/RgltryRptg/Dtls/Inf', 'regulatory_details_info', 'VARCHAR', false, 103, true);

-- Remittance Information fields (5) - ordinal 104-108
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'creditor_reference', 'Document/FICdtTrf/CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Ref', 'creditor_reference', 'VARCHAR', false, 104, true),
('MEPS_PLUS', 'creditor_reference_type', 'Document/FICdtTrf/CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Tp/CdOrPrtry/Cd', 'creditor_reference_type', 'VARCHAR', false, 105, true),
('MEPS_PLUS', 'invoice_number', 'Document/FICdtTrf/CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Nb', 'invoice_number', 'VARCHAR', false, 106, true),
('MEPS_PLUS', 'invoice_date', 'Document/FICdtTrf/CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/RltdDt', 'invoice_date', 'DATE', false, 107, true),
('MEPS_PLUS', 'remittance_unstructured', 'Document/FICdtTrf/CdtTrfTxInf/RmtInf/Ustrd', 'remittance_unstructured', 'VARCHAR', false, 108, true);

-- Supplementary Data - MEPS+ specific fields (7) - ordinal 109-115
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'liquidity_optimization', 'Document/FICdtTrf/CdtTrfTxInf/SplmtryData/Envlp/LqdtyOpt', 'liquidity_optimization', 'BOOLEAN', false, 109, true),
('MEPS_PLUS', 'mas_reference_number', 'Document/FICdtTrf/CdtTrfTxInf/SplmtryData/Envlp/MASRef', 'mas_reference_number', 'VARCHAR', false, 110, true),
('MEPS_PLUS', 'meps_sequence_number', 'Document/FICdtTrf/CdtTrfTxInf/SplmtryData/Envlp/MEPSSeqNb', 'meps_sequence_number', 'VARCHAR', false, 111, true),
('MEPS_PLUS', 'payment_priority_meps', 'Document/FICdtTrf/CdtTrfTxInf/SplmtryData/Envlp/PmtPrty', 'payment_priority_meps', 'VARCHAR', false, 112, true),
('MEPS_PLUS', 'singapore_bank_code', 'Document/FICdtTrf/CdtTrfTxInf/SplmtryData/Envlp/SGBankCd', 'singapore_bank_code', 'VARCHAR', false, 113, true),
('MEPS_PLUS', 'singapore_branch_code', 'Document/FICdtTrf/CdtTrfTxInf/SplmtryData/Envlp/SGBranchCd', 'singapore_branch_code', 'VARCHAR', false, 114, true),
('MEPS_PLUS', 'settlement_window', 'Document/FICdtTrf/CdtTrfTxInf/SplmtryData/Envlp/SttlmWndw', 'settlement_window', 'VARCHAR', false, 115, true);

-- Settlement Time fields (3) - ordinal 116-118
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'settlement_time_credit_dt_tm', 'Document/FICdtTrf/CdtTrfTxInf/SttlmTmIndctn/CdtDtTm', 'settlement_time_credit_dt_tm', 'DATETIME', false, 116, true),
('MEPS_PLUS', 'settlement_time_indication', 'Document/FICdtTrf/CdtTrfTxInf/SttlmTmIndctn/DbtDtTm', 'settlement_time_indication', 'DATETIME', false, 117, true),
('MEPS_PLUS', 'settlement_time_request', 'Document/FICdtTrf/CdtTrfTxInf/SttlmTmReq/CLSTm', 'settlement_time_request', 'TIME', false, 118, true);

-- Group Header fields (14) - ordinal 119-132
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, ordinal_position, is_active)
VALUES
('MEPS_PLUS', 'group_header_creation_date_time', 'Document/FICdtTrf/GrpHdr/CreDtTm', 'group_header_creation_date_time', 'DATETIME', true, 119, true),
('MEPS_PLUS', 'instructed_agent_bic', 'Document/FICdtTrf/GrpHdr/InstdAgt/FinInstnId/BICFI', 'instructed_agent_bic', 'VARCHAR', true, 120, true),
('MEPS_PLUS', 'instructed_agent_lei', 'Document/FICdtTrf/GrpHdr/InstdAgt/FinInstnId/LEI', 'instructed_agent_lei', 'VARCHAR', false, 121, true),
('MEPS_PLUS', 'instructed_agent_name', 'Document/FICdtTrf/GrpHdr/InstdAgt/FinInstnId/Nm', 'instructed_agent_name', 'VARCHAR', false, 122, true),
('MEPS_PLUS', 'instructing_agent_bic', 'Document/FICdtTrf/GrpHdr/InstgAgt/FinInstnId/BICFI', 'instructing_agent_bic', 'VARCHAR', true, 123, true),
('MEPS_PLUS', 'instructing_agent_lei', 'Document/FICdtTrf/GrpHdr/InstgAgt/FinInstnId/LEI', 'instructing_agent_lei', 'VARCHAR', false, 124, true),
('MEPS_PLUS', 'instructing_agent_name', 'Document/FICdtTrf/GrpHdr/InstgAgt/FinInstnId/Nm', 'instructing_agent_name', 'VARCHAR', false, 125, true),
('MEPS_PLUS', 'interbank_settlement_date', 'Document/FICdtTrf/GrpHdr/IntrBkSttlmDt', 'interbank_settlement_date', 'DATE', false, 126, true),
('MEPS_PLUS', 'message_identification', 'Document/FICdtTrf/GrpHdr/MsgId', 'message_identification', 'VARCHAR', true, 127, true),
('MEPS_PLUS', 'number_of_transactions', 'Document/FICdtTrf/GrpHdr/NbOfTxs', 'number_of_transactions', 'INTEGER', true, 128, true),
('MEPS_PLUS', 'clearing_system_code', 'Document/FICdtTrf/GrpHdr/SttlmInf/ClrSys/Cd', 'clearing_system_code', 'VARCHAR', false, 129, true),
('MEPS_PLUS', 'settlement_method', 'Document/FICdtTrf/GrpHdr/SttlmInf/SttlmMtd', 'settlement_method', 'VARCHAR', false, 130, true),
('MEPS_PLUS', 'total_interbank_settlement_amount', 'Document/FICdtTrf/GrpHdr/TtlIntrBkSttlmAmt', 'total_interbank_settlement_amount', 'DECIMAL', false, 131, true),
('MEPS_PLUS', 'total_interbank_settlement_currency', 'Document/FICdtTrf/GrpHdr/TtlIntrBkSttlmAmt/@Ccy', 'total_interbank_settlement_currency', 'VARCHAR', false, 132, true);

COMMIT;
