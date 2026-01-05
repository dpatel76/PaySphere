-- GPS CDM - Complete SEPA Gold Field Mappings
-- =============================================
-- This script adds all Gold mappings for SEPA format to achieve 100% coverage.
-- Run after extend_sepa_extension_table.sql

-- Get next ordinal position (run manually to adjust starting point)
-- SELECT COALESCE(MAX(ordinal_position), 200) + 1 FROM mapping.gold_field_mappings WHERE format_id = 'SEPA';

-- INITIATING_PARTY mappings
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
SELECT * FROM (VALUES
    ('SEPA', 'cdm_party', 'party_id', 'MD5(CONCAT(stg_id, ''_INITIATING_PARTY''))', 'INITIATING_PARTY', 'VARCHAR', true, 201, true),
    ('SEPA', 'cdm_party', 'name', 'initiating_party_name', 'INITIATING_PARTY', 'VARCHAR', false, 202, true),
    ('SEPA', 'cdm_party', 'party_type', '''ORGANIZATION''', 'INITIATING_PARTY', 'VARCHAR', false, 203, true),
    ('SEPA', 'cdm_party', 'identification_number', 'initg_pty_othr_id', 'INITIATING_PARTY', 'VARCHAR', false, 204, true),
    ('SEPA', 'cdm_party', 'identification_type', '''OTHER''', 'INITIATING_PARTY', 'VARCHAR', false, 205, true),
    ('SEPA', 'cdm_party', 'address_line1', 'initg_pty_address_line', 'INITIATING_PARTY', 'VARCHAR', false, 206, true),
    ('SEPA', 'cdm_party', 'building_number', 'initg_pty_building_number', 'INITIATING_PARTY', 'VARCHAR', false, 207, true),
    ('SEPA', 'cdm_party', 'street_name', 'initg_pty_street_name', 'INITIATING_PARTY', 'VARCHAR', false, 208, true),
    ('SEPA', 'cdm_party', 'post_code', 'initg_pty_post_code', 'INITIATING_PARTY', 'VARCHAR', false, 209, true),
    ('SEPA', 'cdm_party', 'town_name', 'initg_pty_town_name', 'INITIATING_PARTY', 'VARCHAR', false, 210, true),
    ('SEPA', 'cdm_party', 'country', 'initg_pty_country', 'INITIATING_PARTY', 'VARCHAR', false, 211, true),
    ('SEPA', 'cdm_party', 'source_message_type', '''SEPA''', 'INITIATING_PARTY', 'VARCHAR', true, 212, true),
    ('SEPA', 'cdm_party', 'source_stg_id', 'stg_id', 'INITIATING_PARTY', 'VARCHAR', true, 213, true),
    ('SEPA', 'cdm_party', 'source_system', '''GPS_CDM''', 'INITIATING_PARTY', 'VARCHAR', true, 214, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
WHERE NOT EXISTS (
    SELECT 1 FROM mapping.gold_field_mappings m
    WHERE m.format_id = v.format_id AND m.gold_table = v.gold_table
    AND m.gold_column = v.gold_column AND m.entity_role = v.entity_role
);

-- ULTIMATE_DEBTOR mappings
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
SELECT * FROM (VALUES
    ('SEPA', 'cdm_party', 'party_id', 'MD5(CONCAT(stg_id, ''_ULTIMATE_DEBTOR''))', 'ULTIMATE_DEBTOR', 'VARCHAR', true, 215, true),
    ('SEPA', 'cdm_party', 'name', 'ultmt_dbtr_name', 'ULTIMATE_DEBTOR', 'VARCHAR', false, 216, true),
    ('SEPA', 'cdm_party', 'party_type', '''ORGANIZATION''', 'ULTIMATE_DEBTOR', 'VARCHAR', false, 217, true),
    ('SEPA', 'cdm_party', 'source_message_type', '''SEPA''', 'ULTIMATE_DEBTOR', 'VARCHAR', true, 218, true),
    ('SEPA', 'cdm_party', 'source_stg_id', 'stg_id', 'ULTIMATE_DEBTOR', 'VARCHAR', true, 219, true),
    ('SEPA', 'cdm_party', 'source_system', '''GPS_CDM''', 'ULTIMATE_DEBTOR', 'VARCHAR', true, 220, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
WHERE NOT EXISTS (
    SELECT 1 FROM mapping.gold_field_mappings m
    WHERE m.format_id = v.format_id AND m.gold_table = v.gold_table
    AND m.gold_column = v.gold_column AND m.entity_role = v.entity_role
);

-- ULTIMATE_CREDITOR mappings
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
SELECT * FROM (VALUES
    ('SEPA', 'cdm_party', 'party_id', 'MD5(CONCAT(stg_id, ''_ULTIMATE_CREDITOR''))', 'ULTIMATE_CREDITOR', 'VARCHAR', true, 221, true),
    ('SEPA', 'cdm_party', 'name', 'ultmt_cdtr_name', 'ULTIMATE_CREDITOR', 'VARCHAR', false, 222, true),
    ('SEPA', 'cdm_party', 'party_type', '''ORGANIZATION''', 'ULTIMATE_CREDITOR', 'VARCHAR', false, 223, true),
    ('SEPA', 'cdm_party', 'source_message_type', '''SEPA''', 'ULTIMATE_CREDITOR', 'VARCHAR', true, 224, true),
    ('SEPA', 'cdm_party', 'source_stg_id', 'stg_id', 'ULTIMATE_CREDITOR', 'VARCHAR', true, 225, true),
    ('SEPA', 'cdm_party', 'source_system', '''GPS_CDM''', 'ULTIMATE_CREDITOR', 'VARCHAR', true, 226, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
WHERE NOT EXISTS (
    SELECT 1 FROM mapping.gold_field_mappings m
    WHERE m.format_id = v.format_id AND m.gold_table = v.gold_table
    AND m.gold_column = v.gold_column AND m.entity_role = v.entity_role
);

-- Financial Institution additional mappings
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
SELECT * FROM (VALUES
    ('SEPA', 'cdm_financial_institution', 'institution_name', 'dbtr_agt_nm', 'DEBTOR_AGENT', 'VARCHAR', false, 229, true),
    ('SEPA', 'cdm_financial_institution', 'national_clearing_code', 'dbtr_agt_mmb_id', 'DEBTOR_AGENT', 'VARCHAR', false, 230, true),
    ('SEPA', 'cdm_financial_institution', 'institution_name', 'cdtr_agt_nm', 'CREDITOR_AGENT', 'VARCHAR', false, 231, true),
    ('SEPA', 'cdm_financial_institution', 'national_clearing_code', 'cdtr_agt_mmb_id', 'CREDITOR_AGENT', 'VARCHAR', false, 232, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
WHERE NOT EXISTS (
    SELECT 1 FROM mapping.gold_field_mappings m
    WHERE m.format_id = v.format_id AND m.gold_table = v.gold_table
    AND m.gold_column = v.gold_column AND m.entity_role = v.entity_role
);

-- Payment Instruction additional mappings
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
SELECT * FROM (VALUES
    ('SEPA', 'cdm_payment_instruction', 'payment_method', 'payment_method', NULL::VARCHAR, 'VARCHAR', false, 233, true),
    ('SEPA', 'cdm_payment_instruction', 'priority', 'instruction_priority', NULL::VARCHAR, 'VARCHAR', false, 234, true),
    ('SEPA', 'cdm_payment_instruction', 'exchange_rate', 'exchange_rate', NULL::VARCHAR, 'DECIMAL', false, 235, true),
    ('SEPA', 'cdm_payment_instruction', 'exchange_rate_type', 'exchange_rate_type', NULL::VARCHAR, 'VARCHAR', false, 236, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
WHERE NOT EXISTS (
    SELECT 1 FROM mapping.gold_field_mappings m
    WHERE m.format_id = v.format_id AND m.gold_table = v.gold_table
    AND m.gold_column = v.gold_column AND (m.entity_role IS NULL AND v.entity_role IS NULL)
);

-- SEPA Extension mappings - Initiating Party
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
SELECT * FROM (VALUES
    ('SEPA', 'cdm_payment_extension_sepa', 'initiating_party_name', 'initiating_party_name', NULL::VARCHAR, 'VARCHAR', false, 237, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'initg_pty_any_bic', 'initg_pty_any_bic', NULL::VARCHAR, 'VARCHAR', false, 238, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'initg_pty_othr_id', 'initg_pty_othr_id', NULL::VARCHAR, 'VARCHAR', false, 239, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'initg_pty_prvt_othr_id', 'initg_pty_prvt_othr_id', NULL::VARCHAR, 'VARCHAR', false, 240, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'initg_pty_address_line', 'initg_pty_address_line', NULL::VARCHAR, 'VARCHAR', false, 241, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'initg_pty_building_number', 'initg_pty_building_number', NULL::VARCHAR, 'VARCHAR', false, 242, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'initg_pty_country', 'initg_pty_country', NULL::VARCHAR, 'VARCHAR', false, 243, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'initg_pty_post_code', 'initg_pty_post_code', NULL::VARCHAR, 'VARCHAR', false, 244, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'initg_pty_street_name', 'initg_pty_street_name', NULL::VARCHAR, 'VARCHAR', false, 245, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'initg_pty_town_name', 'initg_pty_town_name', NULL::VARCHAR, 'VARCHAR', false, 246, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
WHERE NOT EXISTS (
    SELECT 1 FROM mapping.gold_field_mappings m
    WHERE m.format_id = v.format_id AND m.gold_table = v.gold_table
    AND m.gold_column = v.gold_column
);

-- SEPA Extension mappings - Payment Information
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
SELECT * FROM (VALUES
    ('SEPA', 'cdm_payment_extension_sepa', 'payment_information_id', 'payment_information_id', NULL::VARCHAR, 'VARCHAR', false, 247, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'payment_method', 'payment_method', NULL::VARCHAR, 'VARCHAR', false, 248, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'instruction_priority', 'instruction_priority', NULL::VARCHAR, 'VARCHAR', false, 249, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'local_instrument_code', 'local_instrument_code', NULL::VARCHAR, 'VARCHAR', false, 250, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'service_level_code', 'service_level_code', NULL::VARCHAR, 'VARCHAR', false, 251, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'category_purpose_code', 'category_purpose_code', NULL::VARCHAR, 'VARCHAR', false, 252, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'requested_execution_date', 'requested_execution_date', NULL::VARCHAR, 'DATE', false, 253, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'batch_booking', 'batch_booking', NULL::VARCHAR, 'BOOLEAN', false, 254, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'pmt_inf_ctrl_sum', 'pmt_inf_ctrl_sum', NULL::VARCHAR, 'DECIMAL', false, 255, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'pmt_inf_nb_of_txs', 'pmt_inf_nb_of_txs', NULL::VARCHAR, 'INTEGER', false, 256, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'control_sum', 'control_sum', NULL::VARCHAR, 'DECIMAL', false, 257, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'debtor_id', 'debtor_id', NULL::VARCHAR, 'VARCHAR', false, 258, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
WHERE NOT EXISTS (
    SELECT 1 FROM mapping.gold_field_mappings m
    WHERE m.format_id = v.format_id AND m.gold_table = v.gold_table
    AND m.gold_column = v.gold_column
);

-- SEPA Extension mappings - Debtor Extended
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
SELECT * FROM (VALUES
    ('SEPA', 'cdm_payment_extension_sepa', 'ultmt_dbtr_name', 'ultmt_dbtr_name', NULL::VARCHAR, 'VARCHAR', false, 259, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_bic_or_bei', 'dbtr_bic_or_bei', NULL::VARCHAR, 'VARCHAR', false, 260, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_org_othr_id', 'dbtr_org_othr_id', NULL::VARCHAR, 'VARCHAR', false, 261, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_org_othr_schme_cd', 'dbtr_org_othr_schme_cd', NULL::VARCHAR, 'VARCHAR', false, 262, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_birth_date', 'dbtr_birth_date', NULL::VARCHAR, 'DATE', false, 263, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_city_of_birth', 'dbtr_city_of_birth', NULL::VARCHAR, 'VARCHAR', false, 264, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_ctry_of_birth', 'dbtr_ctry_of_birth', NULL::VARCHAR, 'VARCHAR', false, 265, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_prvt_othr_id', 'dbtr_prvt_othr_id', NULL::VARCHAR, 'VARCHAR', false, 266, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_address_line', 'dbtr_address_line', NULL::VARCHAR, 'VARCHAR', false, 267, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_building_number', 'dbtr_building_number', NULL::VARCHAR, 'VARCHAR', false, 268, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_country', 'dbtr_country', NULL::VARCHAR, 'VARCHAR', false, 269, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_post_code', 'dbtr_post_code', NULL::VARCHAR, 'VARCHAR', false, 270, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_street_name', 'dbtr_street_name', NULL::VARCHAR, 'VARCHAR', false, 271, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_town_name', 'dbtr_town_name', NULL::VARCHAR, 'VARCHAR', false, 272, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'debtor_bic', 'debtor_bic', NULL::VARCHAR, 'VARCHAR', false, 273, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_acct_ccy', 'dbtr_acct_ccy', NULL::VARCHAR, 'VARCHAR', false, 274, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_acct_nm', 'dbtr_acct_nm', NULL::VARCHAR, 'VARCHAR', false, 275, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_acct_type_cd', 'dbtr_acct_type_cd', NULL::VARCHAR, 'VARCHAR', false, 276, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_agt_mmb_id', 'dbtr_agt_mmb_id', NULL::VARCHAR, 'VARCHAR', false, 277, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_agt_nm', 'dbtr_agt_nm', NULL::VARCHAR, 'VARCHAR', false, 278, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'dbtr_agt_othr_id', 'dbtr_agt_othr_id', NULL::VARCHAR, 'VARCHAR', false, 279, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
WHERE NOT EXISTS (
    SELECT 1 FROM mapping.gold_field_mappings m
    WHERE m.format_id = v.format_id AND m.gold_table = v.gold_table
    AND m.gold_column = v.gold_column
);

-- SEPA Extension mappings - Transaction and Creditor Extended
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
SELECT * FROM (VALUES
    ('SEPA', 'cdm_payment_extension_sepa', 'tx_chrg_br', 'tx_chrg_br', NULL::VARCHAR, 'VARCHAR', false, 280, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'tx_ctgy_purp_cd', 'tx_ctgy_purp_cd', NULL::VARCHAR, 'VARCHAR', false, 281, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'tx_lcl_instrm_cd', 'tx_lcl_instrm_cd', NULL::VARCHAR, 'VARCHAR', false, 282, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'tx_svc_lvl_cd', 'tx_svc_lvl_cd', NULL::VARCHAR, 'VARCHAR', false, 283, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'purpose_proprietary', 'purpose_proprietary', NULL::VARCHAR, 'VARCHAR', false, 284, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'eqvt_amt_value', 'eqvt_amt_value', NULL::VARCHAR, 'DECIMAL', false, 285, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'eqvt_amt_ccy_of_trf', 'eqvt_amt_ccy_of_trf', NULL::VARCHAR, 'VARCHAR', false, 286, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'ultmt_cdtr_name', 'ultmt_cdtr_name', NULL::VARCHAR, 'VARCHAR', false, 287, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_bic_or_bei', 'cdtr_bic_or_bei', NULL::VARCHAR, 'VARCHAR', false, 288, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_org_othr_id', 'cdtr_org_othr_id', NULL::VARCHAR, 'VARCHAR', false, 289, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_org_othr_schme_cd', 'cdtr_org_othr_schme_cd', NULL::VARCHAR, 'VARCHAR', false, 290, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_birth_date', 'cdtr_birth_date', NULL::VARCHAR, 'DATE', false, 291, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_city_of_birth', 'cdtr_city_of_birth', NULL::VARCHAR, 'VARCHAR', false, 292, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_ctry_of_birth', 'cdtr_ctry_of_birth', NULL::VARCHAR, 'VARCHAR', false, 293, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_prvt_othr_id', 'cdtr_prvt_othr_id', NULL::VARCHAR, 'VARCHAR', false, 294, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_address_line', 'cdtr_address_line', NULL::VARCHAR, 'VARCHAR', false, 295, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_building_number', 'cdtr_building_number', NULL::VARCHAR, 'VARCHAR', false, 296, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_country', 'cdtr_country', NULL::VARCHAR, 'VARCHAR', false, 297, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_post_code', 'cdtr_post_code', NULL::VARCHAR, 'VARCHAR', false, 298, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_street_name', 'cdtr_street_name', NULL::VARCHAR, 'VARCHAR', false, 299, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_town_name', 'cdtr_town_name', NULL::VARCHAR, 'VARCHAR', false, 300, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'creditor_bic', 'creditor_bic', NULL::VARCHAR, 'VARCHAR', false, 301, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
WHERE NOT EXISTS (
    SELECT 1 FROM mapping.gold_field_mappings m
    WHERE m.format_id = v.format_id AND m.gold_table = v.gold_table
    AND m.gold_column = v.gold_column
);

-- SEPA Extension mappings - Creditor Account, Agent, Regulatory, etc.
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
SELECT * FROM (VALUES
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_acct_ccy', 'cdtr_acct_ccy', NULL::VARCHAR, 'VARCHAR', false, 302, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_acct_nm', 'cdtr_acct_nm', NULL::VARCHAR, 'VARCHAR', false, 303, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_acct_type_cd', 'cdtr_acct_type_cd', NULL::VARCHAR, 'VARCHAR', false, 304, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_agt_mmb_id', 'cdtr_agt_mmb_id', NULL::VARCHAR, 'VARCHAR', false, 305, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_agt_nm', 'cdtr_agt_nm', NULL::VARCHAR, 'VARCHAR', false, 306, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_agt_othr_id', 'cdtr_agt_othr_id', NULL::VARCHAR, 'VARCHAR', false, 307, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_agt_ctry', 'cdtr_agt_ctry', NULL::VARCHAR, 'VARCHAR', false, 308, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'rgltry_rptg_cd', 'rgltry_rptg_cd', NULL::VARCHAR, 'VARCHAR', false, 309, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'rgltry_rptg_inf', 'rgltry_rptg_inf', NULL::VARCHAR, 'TEXT', false, 310, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_ref', 'cdtr_ref', NULL::VARCHAR, 'VARCHAR', false, 311, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_ref_tp_cd', 'cdtr_ref_tp_cd', NULL::VARCHAR, 'VARCHAR', false, 312, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'cdtr_ref_tp_issr', 'cdtr_ref_tp_issr', NULL::VARCHAR, 'VARCHAR', false, 313, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'rfrd_doc_nb', 'rfrd_doc_nb', NULL::VARCHAR, 'VARCHAR', false, 314, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'rfrd_doc_rltd_dt', 'rfrd_doc_rltd_dt', NULL::VARCHAR, 'DATE', false, 315, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'rfrd_doc_tp_cd', 'rfrd_doc_tp_cd', NULL::VARCHAR, 'VARCHAR', false, 316, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'rmt_inf_unstructured', 'rmt_inf_unstructured', NULL::VARCHAR, 'TEXT', false, 317, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'tax_ttl_tax_amt', 'tax_ttl_tax_amt', NULL::VARCHAR, 'DECIMAL', false, 318, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'tax_ttl_taxbl_base_amt', 'tax_ttl_taxbl_base_amt', NULL::VARCHAR, 'DECIMAL', false, 319, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'exchange_rate_type', 'exchange_rate_type', NULL::VARCHAR, 'VARCHAR', false, 320, true),
    ('SEPA', 'cdm_payment_extension_sepa', 'exchange_rate', 'exchange_rate', NULL::VARCHAR, 'DECIMAL', false, 321, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, is_required, ordinal_position, is_active)
WHERE NOT EXISTS (
    SELECT 1 FROM mapping.gold_field_mappings m
    WHERE m.format_id = v.format_id AND m.gold_table = v.gold_table
    AND m.gold_column = v.gold_column
);

-- Verify final coverage
SELECT
    'SEPA Silver-to-Gold Coverage' as metric,
    COUNT(*) FILTER (WHERE is_mapped = 1) || '/' || COUNT(*) as coverage,
    ROUND(100.0 * COUNT(*) FILTER (WHERE is_mapped = 1) / COUNT(*), 1) || '%' as percentage
FROM (
    SELECT
        s.column_name,
        CASE WHEN EXISTS (
            SELECT 1 FROM mapping.gold_field_mappings m
            WHERE m.format_id = 'SEPA' AND m.is_active = true
            AND (m.source_expression = s.column_name OR m.source_expression LIKE '%' || s.column_name || '%')
        ) THEN 1 ELSE 0 END as is_mapped
    FROM information_schema.columns s
    WHERE s.table_schema = 'silver' AND s.table_name = 'stg_sepa'
    AND s.column_name NOT IN ('_processed_at', 'processed_to_gold_at', 'processing_error', 'processing_status')
) coverage;
