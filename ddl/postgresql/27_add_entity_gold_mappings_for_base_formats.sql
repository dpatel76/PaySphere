-- Add Gold field mappings for normalized entity tables (cdm_party, cdm_account, cdm_financial_institution)
-- to the base ISO 20022 formats (.base formats)
-- These are essential for maintaining deduplicated reference data

-- First, delete any existing entity mappings for these formats to avoid conflicts
DELETE FROM mapping.gold_field_mappings
WHERE format_id IN ('pacs.008.base', 'pacs.002.base', 'pacs.004.base', 'pacs.009.base', 'pain.001.base', 'pain.008.base')
  AND gold_table IN ('cdm_party', 'cdm_account', 'cdm_financial_institution');

-- =====================================================
-- pacs.008.base - Parties, Accounts, FIs
-- =====================================================

-- Debtor Party
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, is_active, ordinal_position)
VALUES
('pacs.008.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'DEBTOR', 'VARCHAR', true, true, 1),
('pacs.008.base', 'cdm_party', 'name', 'debtor_name', 'DEBTOR', 'VARCHAR', true, true, 2),
('pacs.008.base', 'cdm_party', 'party_type', '''INDIVIDUAL''', 'DEBTOR', 'VARCHAR', false, true, 3),
('pacs.008.base', 'cdm_party', 'role', '''DEBTOR''', 'DEBTOR', 'VARCHAR', true, true, 4),
('pacs.008.base', 'cdm_party', 'country', 'debtor_address_country', 'DEBTOR', 'VARCHAR', false, true, 5),
('pacs.008.base', 'cdm_party', 'address_line1', 'debtor_address_street', 'DEBTOR', 'VARCHAR', false, true, 6),
('pacs.008.base', 'cdm_party', 'city', 'debtor_address_town', 'DEBTOR', 'VARCHAR', false, true, 7),
('pacs.008.base', 'cdm_party', 'postal_code', 'debtor_address_postal_code', 'DEBTOR', 'VARCHAR', false, true, 8),
('pacs.008.base', 'cdm_party', 'lei', 'debtor_id_org_lei', 'DEBTOR', 'VARCHAR', false, true, 9),
('pacs.008.base', 'cdm_party', 'bic', 'debtor_id_org_bic', 'DEBTOR', 'VARCHAR', false, true, 10),
('pacs.008.base', 'cdm_party', 'source_stg_id', '_CONTEXT.stg_id', 'DEBTOR', 'VARCHAR', false, true, 11),
('pacs.008.base', 'cdm_party', 'source_message_type', '_CONTEXT.format_id', 'DEBTOR', 'VARCHAR', false, true, 12);

-- Creditor Party
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, is_active, ordinal_position)
VALUES
('pacs.008.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'CREDITOR', 'VARCHAR', true, true, 1),
('pacs.008.base', 'cdm_party', 'name', 'creditor_name', 'CREDITOR', 'VARCHAR', true, true, 2),
('pacs.008.base', 'cdm_party', 'party_type', '''INDIVIDUAL''', 'CREDITOR', 'VARCHAR', false, true, 3),
('pacs.008.base', 'cdm_party', 'role', '''CREDITOR''', 'CREDITOR', 'VARCHAR', true, true, 4),
('pacs.008.base', 'cdm_party', 'country', 'creditor_address_country', 'CREDITOR', 'VARCHAR', false, true, 5),
('pacs.008.base', 'cdm_party', 'address_line1', 'creditor_address_street', 'CREDITOR', 'VARCHAR', false, true, 6),
('pacs.008.base', 'cdm_party', 'city', 'creditor_address_town', 'CREDITOR', 'VARCHAR', false, true, 7),
('pacs.008.base', 'cdm_party', 'postal_code', 'creditor_address_postal_code', 'CREDITOR', 'VARCHAR', false, true, 8),
('pacs.008.base', 'cdm_party', 'lei', 'creditor_id_org_lei', 'CREDITOR', 'VARCHAR', false, true, 9),
('pacs.008.base', 'cdm_party', 'bic', 'creditor_id_org_bic', 'CREDITOR', 'VARCHAR', false, true, 10),
('pacs.008.base', 'cdm_party', 'source_stg_id', '_CONTEXT.stg_id', 'CREDITOR', 'VARCHAR', false, true, 11),
('pacs.008.base', 'cdm_party', 'source_message_type', '_CONTEXT.format_id', 'CREDITOR', 'VARCHAR', false, true, 12);

-- Debtor Account
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, is_required, is_active, ordinal_position)
VALUES
('pacs.008.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'DEBTOR', 'VARCHAR', NULL, true, true, 1),
('pacs.008.base', 'cdm_account', 'account_number', 'debtor_account_other', 'DEBTOR', 'VARCHAR', 'COALESCE_IBAN', false, true, 2),
('pacs.008.base', 'cdm_account', 'iban', 'debtor_account_iban', 'DEBTOR', 'VARCHAR', NULL, false, true, 3),
('pacs.008.base', 'cdm_account', 'account_type', 'debtor_account_type', 'DEBTOR', 'VARCHAR', 'COALESCE:CACC', false, true, 4),
('pacs.008.base', 'cdm_account', 'currency', 'debtor_account_currency', 'DEBTOR', 'VARCHAR', 'COALESCE:USD', false, true, 5),
('pacs.008.base', 'cdm_account', 'account_name', 'debtor_account_name', 'DEBTOR', 'VARCHAR', NULL, false, true, 6),
('pacs.008.base', 'cdm_account', 'role', '''DEBTOR''', 'DEBTOR', 'VARCHAR', NULL, true, true, 7),
('pacs.008.base', 'cdm_account', 'source_stg_id', '_CONTEXT.stg_id', 'DEBTOR', 'VARCHAR', NULL, false, true, 8),
('pacs.008.base', 'cdm_account', 'source_message_type', '_CONTEXT.format_id', 'DEBTOR', 'VARCHAR', NULL, false, true, 9);

-- Creditor Account
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, is_required, is_active, ordinal_position)
VALUES
('pacs.008.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'CREDITOR', 'VARCHAR', NULL, true, true, 1),
('pacs.008.base', 'cdm_account', 'account_number', 'creditor_account_other', 'CREDITOR', 'VARCHAR', 'COALESCE_IBAN', false, true, 2),
('pacs.008.base', 'cdm_account', 'iban', 'creditor_account_iban', 'CREDITOR', 'VARCHAR', NULL, false, true, 3),
('pacs.008.base', 'cdm_account', 'account_type', 'creditor_account_type', 'CREDITOR', 'VARCHAR', 'COALESCE:CACC', false, true, 4),
('pacs.008.base', 'cdm_account', 'currency', 'creditor_account_currency', 'CREDITOR', 'VARCHAR', 'COALESCE:USD', false, true, 5),
('pacs.008.base', 'cdm_account', 'account_name', 'creditor_account_name', 'CREDITOR', 'VARCHAR', NULL, false, true, 6),
('pacs.008.base', 'cdm_account', 'role', '''CREDITOR''', 'CREDITOR', 'VARCHAR', NULL, true, true, 7),
('pacs.008.base', 'cdm_account', 'source_stg_id', '_CONTEXT.stg_id', 'CREDITOR', 'VARCHAR', NULL, false, true, 8),
('pacs.008.base', 'cdm_account', 'source_message_type', '_CONTEXT.format_id', 'CREDITOR', 'VARCHAR', NULL, false, true, 9);

-- Debtor Agent FI
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, default_value, is_required, is_active, ordinal_position)
VALUES
('pacs.008.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, true, true, 1),
('pacs.008.base', 'cdm_financial_institution', 'bic', 'debtor_agent_bic', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 2),
('pacs.008.base', 'cdm_financial_institution', 'lei', 'debtor_agent_lei', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 3),
('pacs.008.base', 'cdm_financial_institution', 'clearing_system_id', 'debtor_agent_clearing_id', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 4),
('pacs.008.base', 'cdm_financial_institution', 'institution_name', 'debtor_agent_name', 'DEBTOR_AGENT', 'VARCHAR', 'COALESCE_BIC', NULL, false, true, 5),
('pacs.008.base', 'cdm_financial_institution', 'country', 'debtor_agent_address_country', 'DEBTOR_AGENT', 'VARCHAR', 'COUNTRY_FROM_BIC', 'XX', false, true, 6),
('pacs.008.base', 'cdm_financial_institution', 'role', '''DEBTOR_AGENT''', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, true, true, 7),
('pacs.008.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 8),
('pacs.008.base', 'cdm_financial_institution', 'source_message_type', '_CONTEXT.format_id', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 9);

-- Creditor Agent FI
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, default_value, is_required, is_active, ordinal_position)
VALUES
('pacs.008.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, true, true, 1),
('pacs.008.base', 'cdm_financial_institution', 'bic', 'creditor_agent_bic', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 2),
('pacs.008.base', 'cdm_financial_institution', 'lei', 'creditor_agent_lei', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 3),
('pacs.008.base', 'cdm_financial_institution', 'clearing_system_id', 'creditor_agent_clearing_id', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 4),
('pacs.008.base', 'cdm_financial_institution', 'institution_name', 'creditor_agent_name', 'CREDITOR_AGENT', 'VARCHAR', 'COALESCE_BIC', NULL, false, true, 5),
('pacs.008.base', 'cdm_financial_institution', 'country', 'creditor_agent_address_country', 'CREDITOR_AGENT', 'VARCHAR', 'COUNTRY_FROM_BIC', 'XX', false, true, 6),
('pacs.008.base', 'cdm_financial_institution', 'role', '''CREDITOR_AGENT''', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, true, true, 7),
('pacs.008.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 8),
('pacs.008.base', 'cdm_financial_institution', 'source_message_type', '_CONTEXT.format_id', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 9);

-- =====================================================
-- pacs.002.base - Payment Status Report entities
-- =====================================================

-- Instructing Agent FI
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, default_value, is_required, is_active, ordinal_position)
VALUES
('pacs.002.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'INSTRUCTING_AGENT', 'VARCHAR', NULL, NULL, true, true, 1),
('pacs.002.base', 'cdm_financial_institution', 'bic', 'instructing_agent_bic', 'INSTRUCTING_AGENT', 'VARCHAR', NULL, NULL, false, true, 2),
('pacs.002.base', 'cdm_financial_institution', 'institution_name', 'instructing_agent_name', 'INSTRUCTING_AGENT', 'VARCHAR', 'COALESCE_BIC', NULL, false, true, 3),
('pacs.002.base', 'cdm_financial_institution', 'country', 'instructing_agent_country', 'INSTRUCTING_AGENT', 'VARCHAR', 'COUNTRY_FROM_BIC', 'XX', false, true, 4),
('pacs.002.base', 'cdm_financial_institution', 'role', '''INSTRUCTING_AGENT''', 'INSTRUCTING_AGENT', 'VARCHAR', NULL, NULL, true, true, 5),
('pacs.002.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'INSTRUCTING_AGENT', 'VARCHAR', NULL, NULL, false, true, 6),
('pacs.002.base', 'cdm_financial_institution', 'source_message_type', '_CONTEXT.format_id', 'INSTRUCTING_AGENT', 'VARCHAR', NULL, NULL, false, true, 7);

-- Instructed Agent FI
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, default_value, is_required, is_active, ordinal_position)
VALUES
('pacs.002.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'INSTRUCTED_AGENT', 'VARCHAR', NULL, NULL, true, true, 1),
('pacs.002.base', 'cdm_financial_institution', 'bic', 'instructed_agent_bic', 'INSTRUCTED_AGENT', 'VARCHAR', NULL, NULL, false, true, 2),
('pacs.002.base', 'cdm_financial_institution', 'institution_name', 'instructed_agent_name', 'INSTRUCTED_AGENT', 'VARCHAR', 'COALESCE_BIC', NULL, false, true, 3),
('pacs.002.base', 'cdm_financial_institution', 'country', 'instructed_agent_country', 'INSTRUCTED_AGENT', 'VARCHAR', 'COUNTRY_FROM_BIC', 'XX', false, true, 4),
('pacs.002.base', 'cdm_financial_institution', 'role', '''INSTRUCTED_AGENT''', 'INSTRUCTED_AGENT', 'VARCHAR', NULL, NULL, true, true, 5),
('pacs.002.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'INSTRUCTED_AGENT', 'VARCHAR', NULL, NULL, false, true, 6),
('pacs.002.base', 'cdm_financial_institution', 'source_message_type', '_CONTEXT.format_id', 'INSTRUCTED_AGENT', 'VARCHAR', NULL, NULL, false, true, 7);

-- =====================================================
-- pacs.004.base - Payment Return entities
-- =====================================================

-- Original Debtor Party
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, is_active, ordinal_position)
VALUES
('pacs.004.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'ORIGINAL_DEBTOR', 'VARCHAR', true, true, 1),
('pacs.004.base', 'cdm_party', 'name', 'original_debtor_name', 'ORIGINAL_DEBTOR', 'VARCHAR', true, true, 2),
('pacs.004.base', 'cdm_party', 'party_type', '''INDIVIDUAL''', 'ORIGINAL_DEBTOR', 'VARCHAR', false, true, 3),
('pacs.004.base', 'cdm_party', 'role', '''ORIGINAL_DEBTOR''', 'ORIGINAL_DEBTOR', 'VARCHAR', true, true, 4),
('pacs.004.base', 'cdm_party', 'country', 'original_debtor_country', 'ORIGINAL_DEBTOR', 'VARCHAR', false, true, 5),
('pacs.004.base', 'cdm_party', 'source_stg_id', '_CONTEXT.stg_id', 'ORIGINAL_DEBTOR', 'VARCHAR', false, true, 6),
('pacs.004.base', 'cdm_party', 'source_message_type', '_CONTEXT.format_id', 'ORIGINAL_DEBTOR', 'VARCHAR', false, true, 7);

-- Original Creditor Party
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, is_active, ordinal_position)
VALUES
('pacs.004.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'ORIGINAL_CREDITOR', 'VARCHAR', true, true, 1),
('pacs.004.base', 'cdm_party', 'name', 'original_creditor_name', 'ORIGINAL_CREDITOR', 'VARCHAR', true, true, 2),
('pacs.004.base', 'cdm_party', 'party_type', '''INDIVIDUAL''', 'ORIGINAL_CREDITOR', 'VARCHAR', false, true, 3),
('pacs.004.base', 'cdm_party', 'role', '''ORIGINAL_CREDITOR''', 'ORIGINAL_CREDITOR', 'VARCHAR', true, true, 4),
('pacs.004.base', 'cdm_party', 'country', 'original_creditor_country', 'ORIGINAL_CREDITOR', 'VARCHAR', false, true, 5),
('pacs.004.base', 'cdm_party', 'source_stg_id', '_CONTEXT.stg_id', 'ORIGINAL_CREDITOR', 'VARCHAR', false, true, 6),
('pacs.004.base', 'cdm_party', 'source_message_type', '_CONTEXT.format_id', 'ORIGINAL_CREDITOR', 'VARCHAR', false, true, 7);

-- Return Reason Originator FI
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, default_value, is_required, is_active, ordinal_position)
VALUES
('pacs.004.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'RETURN_REASON_ORIGINATOR', 'VARCHAR', NULL, NULL, true, true, 1),
('pacs.004.base', 'cdm_financial_institution', 'bic', 'return_reason_originator_bic', 'RETURN_REASON_ORIGINATOR', 'VARCHAR', NULL, NULL, false, true, 2),
('pacs.004.base', 'cdm_financial_institution', 'institution_name', 'return_reason_originator_name', 'RETURN_REASON_ORIGINATOR', 'VARCHAR', 'COALESCE_BIC', NULL, false, true, 3),
('pacs.004.base', 'cdm_financial_institution', 'country', NULL, 'RETURN_REASON_ORIGINATOR', 'VARCHAR', 'COUNTRY_FROM_BIC', 'XX', false, true, 4),
('pacs.004.base', 'cdm_financial_institution', 'role', '''RETURN_REASON_ORIGINATOR''', 'RETURN_REASON_ORIGINATOR', 'VARCHAR', NULL, NULL, true, true, 5),
('pacs.004.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'RETURN_REASON_ORIGINATOR', 'VARCHAR', NULL, NULL, false, true, 6),
('pacs.004.base', 'cdm_financial_institution', 'source_message_type', '_CONTEXT.format_id', 'RETURN_REASON_ORIGINATOR', 'VARCHAR', NULL, NULL, false, true, 7);

-- =====================================================
-- pacs.009.base - FI Credit Transfer entities (FI-to-FI)
-- =====================================================

-- Debtor FI (debtor is an FI in pacs.009)
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, default_value, is_required, is_active, ordinal_position)
VALUES
('pacs.009.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'DEBTOR', 'VARCHAR', NULL, NULL, true, true, 1),
('pacs.009.base', 'cdm_financial_institution', 'bic', 'debtor_bic', 'DEBTOR', 'VARCHAR', NULL, NULL, false, true, 2),
('pacs.009.base', 'cdm_financial_institution', 'lei', 'debtor_lei', 'DEBTOR', 'VARCHAR', NULL, NULL, false, true, 3),
('pacs.009.base', 'cdm_financial_institution', 'institution_name', 'debtor_name', 'DEBTOR', 'VARCHAR', 'COALESCE_BIC', NULL, false, true, 4),
('pacs.009.base', 'cdm_financial_institution', 'country', 'debtor_country', 'DEBTOR', 'VARCHAR', 'COUNTRY_FROM_BIC', 'XX', false, true, 5),
('pacs.009.base', 'cdm_financial_institution', 'role', '''DEBTOR''', 'DEBTOR', 'VARCHAR', NULL, NULL, true, true, 6),
('pacs.009.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'DEBTOR', 'VARCHAR', NULL, NULL, false, true, 7),
('pacs.009.base', 'cdm_financial_institution', 'source_message_type', '_CONTEXT.format_id', 'DEBTOR', 'VARCHAR', NULL, NULL, false, true, 8);

-- Creditor FI
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, default_value, is_required, is_active, ordinal_position)
VALUES
('pacs.009.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'CREDITOR', 'VARCHAR', NULL, NULL, true, true, 1),
('pacs.009.base', 'cdm_financial_institution', 'bic', 'creditor_bic', 'CREDITOR', 'VARCHAR', NULL, NULL, false, true, 2),
('pacs.009.base', 'cdm_financial_institution', 'lei', 'creditor_lei', 'CREDITOR', 'VARCHAR', NULL, NULL, false, true, 3),
('pacs.009.base', 'cdm_financial_institution', 'institution_name', 'creditor_name', 'CREDITOR', 'VARCHAR', 'COALESCE_BIC', NULL, false, true, 4),
('pacs.009.base', 'cdm_financial_institution', 'country', 'creditor_country', 'CREDITOR', 'VARCHAR', 'COUNTRY_FROM_BIC', 'XX', false, true, 5),
('pacs.009.base', 'cdm_financial_institution', 'role', '''CREDITOR''', 'CREDITOR', 'VARCHAR', NULL, NULL, true, true, 6),
('pacs.009.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'CREDITOR', 'VARCHAR', NULL, NULL, false, true, 7),
('pacs.009.base', 'cdm_financial_institution', 'source_message_type', '_CONTEXT.format_id', 'CREDITOR', 'VARCHAR', NULL, NULL, false, true, 8);

-- =====================================================
-- pain.001.base - Customer Credit Transfer Initiation
-- =====================================================

-- Initiating Party
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, is_active, ordinal_position)
VALUES
('pain.001.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'INITIATING_PARTY', 'VARCHAR', true, true, 1),
('pain.001.base', 'cdm_party', 'name', 'initiating_party_name', 'INITIATING_PARTY', 'VARCHAR', true, true, 2),
('pain.001.base', 'cdm_party', 'party_type', '''INDIVIDUAL''', 'INITIATING_PARTY', 'VARCHAR', false, true, 3),
('pain.001.base', 'cdm_party', 'role', '''INITIATING_PARTY''', 'INITIATING_PARTY', 'VARCHAR', true, true, 4),
('pain.001.base', 'cdm_party', 'lei', 'initiating_party_lei', 'INITIATING_PARTY', 'VARCHAR', false, true, 5),
('pain.001.base', 'cdm_party', 'source_stg_id', '_CONTEXT.stg_id', 'INITIATING_PARTY', 'VARCHAR', false, true, 6),
('pain.001.base', 'cdm_party', 'source_message_type', '_CONTEXT.format_id', 'INITIATING_PARTY', 'VARCHAR', false, true, 7);

-- Debtor Party
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, is_active, ordinal_position)
VALUES
('pain.001.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'DEBTOR', 'VARCHAR', true, true, 1),
('pain.001.base', 'cdm_party', 'name', 'debtor_name', 'DEBTOR', 'VARCHAR', true, true, 2),
('pain.001.base', 'cdm_party', 'party_type', '''INDIVIDUAL''', 'DEBTOR', 'VARCHAR', false, true, 3),
('pain.001.base', 'cdm_party', 'role', '''DEBTOR''', 'DEBTOR', 'VARCHAR', true, true, 4),
('pain.001.base', 'cdm_party', 'country', 'debtor_country', 'DEBTOR', 'VARCHAR', false, true, 5),
('pain.001.base', 'cdm_party', 'address_line1', 'debtor_address_line', 'DEBTOR', 'VARCHAR', false, true, 6),
('pain.001.base', 'cdm_party', 'city', 'debtor_town', 'DEBTOR', 'VARCHAR', false, true, 7),
('pain.001.base', 'cdm_party', 'postal_code', 'debtor_postal_code', 'DEBTOR', 'VARCHAR', false, true, 8),
('pain.001.base', 'cdm_party', 'source_stg_id', '_CONTEXT.stg_id', 'DEBTOR', 'VARCHAR', false, true, 9),
('pain.001.base', 'cdm_party', 'source_message_type', '_CONTEXT.format_id', 'DEBTOR', 'VARCHAR', false, true, 10);

-- Creditor Party
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, is_active, ordinal_position)
VALUES
('pain.001.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'CREDITOR', 'VARCHAR', true, true, 1),
('pain.001.base', 'cdm_party', 'name', 'creditor_name', 'CREDITOR', 'VARCHAR', true, true, 2),
('pain.001.base', 'cdm_party', 'party_type', '''INDIVIDUAL''', 'CREDITOR', 'VARCHAR', false, true, 3),
('pain.001.base', 'cdm_party', 'role', '''CREDITOR''', 'CREDITOR', 'VARCHAR', true, true, 4),
('pain.001.base', 'cdm_party', 'country', 'creditor_country', 'CREDITOR', 'VARCHAR', false, true, 5),
('pain.001.base', 'cdm_party', 'address_line1', 'creditor_address_line', 'CREDITOR', 'VARCHAR', false, true, 6),
('pain.001.base', 'cdm_party', 'city', 'creditor_town', 'CREDITOR', 'VARCHAR', false, true, 7),
('pain.001.base', 'cdm_party', 'postal_code', 'creditor_postal_code', 'CREDITOR', 'VARCHAR', false, true, 8),
('pain.001.base', 'cdm_party', 'source_stg_id', '_CONTEXT.stg_id', 'CREDITOR', 'VARCHAR', false, true, 9),
('pain.001.base', 'cdm_party', 'source_message_type', '_CONTEXT.format_id', 'CREDITOR', 'VARCHAR', false, true, 10);

-- Debtor Account
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, is_required, is_active, ordinal_position)
VALUES
('pain.001.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'DEBTOR', 'VARCHAR', NULL, true, true, 1),
('pain.001.base', 'cdm_account', 'account_number', 'debtor_account_other_id', 'DEBTOR', 'VARCHAR', 'COALESCE_IBAN', false, true, 2),
('pain.001.base', 'cdm_account', 'iban', 'debtor_account_iban', 'DEBTOR', 'VARCHAR', NULL, false, true, 3),
('pain.001.base', 'cdm_account', 'account_type', 'debtor_account_type', 'DEBTOR', 'VARCHAR', 'COALESCE:CACC', false, true, 4),
('pain.001.base', 'cdm_account', 'currency', 'debtor_account_currency', 'DEBTOR', 'VARCHAR', 'COALESCE:USD', false, true, 5),
('pain.001.base', 'cdm_account', 'role', '''DEBTOR''', 'DEBTOR', 'VARCHAR', NULL, true, true, 6),
('pain.001.base', 'cdm_account', 'source_stg_id', '_CONTEXT.stg_id', 'DEBTOR', 'VARCHAR', NULL, false, true, 7),
('pain.001.base', 'cdm_account', 'source_message_type', '_CONTEXT.format_id', 'DEBTOR', 'VARCHAR', NULL, false, true, 8);

-- Creditor Account
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, is_required, is_active, ordinal_position)
VALUES
('pain.001.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'CREDITOR', 'VARCHAR', NULL, true, true, 1),
('pain.001.base', 'cdm_account', 'account_number', 'creditor_account_other_id', 'CREDITOR', 'VARCHAR', 'COALESCE_IBAN', false, true, 2),
('pain.001.base', 'cdm_account', 'iban', 'creditor_account_iban', 'CREDITOR', 'VARCHAR', NULL, false, true, 3),
('pain.001.base', 'cdm_account', 'account_type', 'creditor_account_type', 'CREDITOR', 'VARCHAR', 'COALESCE:CACC', false, true, 4),
('pain.001.base', 'cdm_account', 'currency', 'creditor_account_currency', 'CREDITOR', 'VARCHAR', 'COALESCE:USD', false, true, 5),
('pain.001.base', 'cdm_account', 'role', '''CREDITOR''', 'CREDITOR', 'VARCHAR', NULL, true, true, 6),
('pain.001.base', 'cdm_account', 'source_stg_id', '_CONTEXT.stg_id', 'CREDITOR', 'VARCHAR', NULL, false, true, 7),
('pain.001.base', 'cdm_account', 'source_message_type', '_CONTEXT.format_id', 'CREDITOR', 'VARCHAR', NULL, false, true, 8);

-- Debtor Agent FI
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, default_value, is_required, is_active, ordinal_position)
VALUES
('pain.001.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, true, true, 1),
('pain.001.base', 'cdm_financial_institution', 'bic', 'debtor_agent_bic', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 2),
('pain.001.base', 'cdm_financial_institution', 'institution_name', 'debtor_agent_name', 'DEBTOR_AGENT', 'VARCHAR', 'COALESCE_BIC', NULL, false, true, 3),
('pain.001.base', 'cdm_financial_institution', 'country', 'debtor_agent_country', 'DEBTOR_AGENT', 'VARCHAR', 'COUNTRY_FROM_BIC', 'XX', false, true, 4),
('pain.001.base', 'cdm_financial_institution', 'role', '''DEBTOR_AGENT''', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, true, true, 5),
('pain.001.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 6),
('pain.001.base', 'cdm_financial_institution', 'source_message_type', '_CONTEXT.format_id', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 7);

-- Creditor Agent FI
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, default_value, is_required, is_active, ordinal_position)
VALUES
('pain.001.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, true, true, 1),
('pain.001.base', 'cdm_financial_institution', 'bic', 'creditor_agent_bic', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 2),
('pain.001.base', 'cdm_financial_institution', 'institution_name', 'creditor_agent_name', 'CREDITOR_AGENT', 'VARCHAR', 'COALESCE_BIC', NULL, false, true, 3),
('pain.001.base', 'cdm_financial_institution', 'country', 'creditor_agent_country', 'CREDITOR_AGENT', 'VARCHAR', 'COUNTRY_FROM_BIC', 'XX', false, true, 4),
('pain.001.base', 'cdm_financial_institution', 'role', '''CREDITOR_AGENT''', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, true, true, 5),
('pain.001.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 6),
('pain.001.base', 'cdm_financial_institution', 'source_message_type', '_CONTEXT.format_id', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 7);

-- =====================================================
-- pain.008.base - Direct Debit Initiation entities
-- =====================================================

-- Initiating Party
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, is_active, ordinal_position)
VALUES
('pain.008.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'INITIATING_PARTY', 'VARCHAR', true, true, 1),
('pain.008.base', 'cdm_party', 'name', 'initiating_party_name', 'INITIATING_PARTY', 'VARCHAR', true, true, 2),
('pain.008.base', 'cdm_party', 'party_type', '''INDIVIDUAL''', 'INITIATING_PARTY', 'VARCHAR', false, true, 3),
('pain.008.base', 'cdm_party', 'role', '''INITIATING_PARTY''', 'INITIATING_PARTY', 'VARCHAR', true, true, 4),
('pain.008.base', 'cdm_party', 'source_stg_id', '_CONTEXT.stg_id', 'INITIATING_PARTY', 'VARCHAR', false, true, 5),
('pain.008.base', 'cdm_party', 'source_message_type', '_CONTEXT.format_id', 'INITIATING_PARTY', 'VARCHAR', false, true, 6);

-- Creditor Party
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, is_active, ordinal_position)
VALUES
('pain.008.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'CREDITOR', 'VARCHAR', true, true, 1),
('pain.008.base', 'cdm_party', 'name', 'creditor_name', 'CREDITOR', 'VARCHAR', true, true, 2),
('pain.008.base', 'cdm_party', 'party_type', '''INDIVIDUAL''', 'CREDITOR', 'VARCHAR', false, true, 3),
('pain.008.base', 'cdm_party', 'role', '''CREDITOR''', 'CREDITOR', 'VARCHAR', true, true, 4),
('pain.008.base', 'cdm_party', 'country', 'creditor_country', 'CREDITOR', 'VARCHAR', false, true, 5),
('pain.008.base', 'cdm_party', 'source_stg_id', '_CONTEXT.stg_id', 'CREDITOR', 'VARCHAR', false, true, 6),
('pain.008.base', 'cdm_party', 'source_message_type', '_CONTEXT.format_id', 'CREDITOR', 'VARCHAR', false, true, 7);

-- Debtor Party
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, is_active, ordinal_position)
VALUES
('pain.008.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'DEBTOR', 'VARCHAR', true, true, 1),
('pain.008.base', 'cdm_party', 'name', 'debtor_name', 'DEBTOR', 'VARCHAR', true, true, 2),
('pain.008.base', 'cdm_party', 'party_type', '''INDIVIDUAL''', 'DEBTOR', 'VARCHAR', false, true, 3),
('pain.008.base', 'cdm_party', 'role', '''DEBTOR''', 'DEBTOR', 'VARCHAR', true, true, 4),
('pain.008.base', 'cdm_party', 'country', 'debtor_country', 'DEBTOR', 'VARCHAR', false, true, 5),
('pain.008.base', 'cdm_party', 'source_stg_id', '_CONTEXT.stg_id', 'DEBTOR', 'VARCHAR', false, true, 6),
('pain.008.base', 'cdm_party', 'source_message_type', '_CONTEXT.format_id', 'DEBTOR', 'VARCHAR', false, true, 7);

-- Creditor Account
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, is_required, is_active, ordinal_position)
VALUES
('pain.008.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'CREDITOR', 'VARCHAR', NULL, true, true, 1),
('pain.008.base', 'cdm_account', 'iban', 'creditor_account_iban', 'CREDITOR', 'VARCHAR', NULL, false, true, 2),
('pain.008.base', 'cdm_account', 'account_number', 'creditor_account_other_id', 'CREDITOR', 'VARCHAR', 'COALESCE_IBAN', false, true, 3),
('pain.008.base', 'cdm_account', 'currency', 'creditor_account_currency', 'CREDITOR', 'VARCHAR', 'COALESCE:EUR', false, true, 4),
('pain.008.base', 'cdm_account', 'role', '''CREDITOR''', 'CREDITOR', 'VARCHAR', NULL, true, true, 5),
('pain.008.base', 'cdm_account', 'source_stg_id', '_CONTEXT.stg_id', 'CREDITOR', 'VARCHAR', NULL, false, true, 6),
('pain.008.base', 'cdm_account', 'source_message_type', '_CONTEXT.format_id', 'CREDITOR', 'VARCHAR', NULL, false, true, 7);

-- Debtor Account
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, is_required, is_active, ordinal_position)
VALUES
('pain.008.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'DEBTOR', 'VARCHAR', NULL, true, true, 1),
('pain.008.base', 'cdm_account', 'iban', 'debtor_account_iban', 'DEBTOR', 'VARCHAR', NULL, false, true, 2),
('pain.008.base', 'cdm_account', 'account_number', 'debtor_account_other_id', 'DEBTOR', 'VARCHAR', 'COALESCE_IBAN', false, true, 3),
('pain.008.base', 'cdm_account', 'currency', 'debtor_account_currency', 'DEBTOR', 'VARCHAR', 'COALESCE:EUR', false, true, 4),
('pain.008.base', 'cdm_account', 'role', '''DEBTOR''', 'DEBTOR', 'VARCHAR', NULL, true, true, 5),
('pain.008.base', 'cdm_account', 'source_stg_id', '_CONTEXT.stg_id', 'DEBTOR', 'VARCHAR', NULL, false, true, 6),
('pain.008.base', 'cdm_account', 'source_message_type', '_CONTEXT.format_id', 'DEBTOR', 'VARCHAR', NULL, false, true, 7);

-- Creditor Agent FI
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, default_value, is_required, is_active, ordinal_position)
VALUES
('pain.008.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, true, true, 1),
('pain.008.base', 'cdm_financial_institution', 'bic', 'creditor_agent_bic', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 2),
('pain.008.base', 'cdm_financial_institution', 'institution_name', 'creditor_agent_name', 'CREDITOR_AGENT', 'VARCHAR', 'COALESCE_BIC', NULL, false, true, 3),
('pain.008.base', 'cdm_financial_institution', 'country', 'creditor_agent_country', 'CREDITOR_AGENT', 'VARCHAR', 'COUNTRY_FROM_BIC', 'XX', false, true, 4),
('pain.008.base', 'cdm_financial_institution', 'role', '''CREDITOR_AGENT''', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, true, true, 5),
('pain.008.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 6),
('pain.008.base', 'cdm_financial_institution', 'source_message_type', '_CONTEXT.format_id', 'CREDITOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 7);

-- Debtor Agent FI
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, transform_expression, default_value, is_required, is_active, ordinal_position)
VALUES
('pain.008.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, true, true, 1),
('pain.008.base', 'cdm_financial_institution', 'bic', 'debtor_agent_bic', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 2),
('pain.008.base', 'cdm_financial_institution', 'institution_name', 'debtor_agent_name', 'DEBTOR_AGENT', 'VARCHAR', 'COALESCE_BIC', NULL, false, true, 3),
('pain.008.base', 'cdm_financial_institution', 'country', 'debtor_agent_country', 'DEBTOR_AGENT', 'VARCHAR', 'COUNTRY_FROM_BIC', 'XX', false, true, 4),
('pain.008.base', 'cdm_financial_institution', 'role', '''DEBTOR_AGENT''', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, true, true, 5),
('pain.008.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 6),
('pain.008.base', 'cdm_financial_institution', 'source_message_type', '_CONTEXT.format_id', 'DEBTOR_AGENT', 'VARCHAR', NULL, NULL, false, true, 7);

-- Verify counts after insert
SELECT format_id, gold_table, entity_role, COUNT(*) as mapping_count
FROM mapping.gold_field_mappings
WHERE format_id LIKE '%.base'
  AND gold_table IN ('cdm_party', 'cdm_account', 'cdm_financial_institution')
  AND is_active = TRUE
GROUP BY format_id, gold_table, entity_role
ORDER BY format_id, gold_table, entity_role;
