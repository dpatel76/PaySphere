-- Fix entity mappings for ISO 20022 base formats
-- The entity mappings were using full expanded column names (e.g., creditor_name, debtor_agent_bic)
-- but the Silver tables use abbreviated ISO 20022 column names (e.g., cdtr_nm, dbtr_agt_bic)

-- This script updates the entity mappings to use the correct abbreviated Silver column names

-- =====================================================
-- pacs.008.base - cdm_party (DEBTOR)
-- =====================================================
UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_nm'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_party' AND gold_column = 'name' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_pstl_adr_strt_nm'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_party' AND gold_column = 'address_line1' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_pstl_adr_twn_nm'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_party' AND gold_column = 'city' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_pstl_adr_ctry'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_party' AND gold_column = 'country' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_pstl_adr_pst_cd'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_party' AND gold_column = 'postal_code' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_id_org_id_any_bic'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_party' AND gold_column = 'bic' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_id_org_id_lei'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_party' AND gold_column = 'lei' AND entity_role = 'DEBTOR';

-- =====================================================
-- pacs.008.base - cdm_party (CREDITOR)
-- =====================================================
UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_nm'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_party' AND gold_column = 'name' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_pstl_adr_strt_nm'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_party' AND gold_column = 'address_line1' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_pstl_adr_twn_nm'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_party' AND gold_column = 'city' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_pstl_adr_ctry'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_party' AND gold_column = 'country' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_pstl_adr_pst_cd'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_party' AND gold_column = 'postal_code' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_id_org_id_any_bic'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_party' AND gold_column = 'bic' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_id_org_id_lei'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_party' AND gold_column = 'lei' AND entity_role = 'CREDITOR';

-- =====================================================
-- pacs.008.base - cdm_account (DEBTOR)
-- =====================================================
UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_acct_id_iban'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_account' AND gold_column = 'iban' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_acct_id_othr_id'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_account' AND gold_column = 'account_number' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_acct_tp_cd'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_account' AND gold_column = 'account_type' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_acct_ccy'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_account' AND gold_column = 'currency' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_acct_nm'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_account' AND gold_column = 'account_name' AND entity_role = 'DEBTOR';

-- =====================================================
-- pacs.008.base - cdm_account (CREDITOR)
-- =====================================================
UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_acct_id_iban'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_account' AND gold_column = 'iban' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_acct_id_othr_id'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_account' AND gold_column = 'account_number' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_acct_tp_cd'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_account' AND gold_column = 'account_type' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_acct_ccy'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_account' AND gold_column = 'currency' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_acct_nm'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_account' AND gold_column = 'account_name' AND entity_role = 'CREDITOR';

-- =====================================================
-- pacs.008.base - cdm_financial_institution (DEBTOR_AGENT)
-- =====================================================
UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_agt_bic'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'bic' AND entity_role = 'DEBTOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_agt_lei'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'lei' AND entity_role = 'DEBTOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_agt_nm'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'institution_name' AND entity_role = 'DEBTOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_agt_clr_sys_mmb_id'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'clearing_system_id' AND entity_role = 'DEBTOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_agt_pstl_adr_ctry'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'country' AND entity_role = 'DEBTOR_AGENT';

-- =====================================================
-- pacs.008.base - cdm_financial_institution (CREDITOR_AGENT)
-- =====================================================
UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_agt_bic'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'bic' AND entity_role = 'CREDITOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_agt_lei'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'lei' AND entity_role = 'CREDITOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_agt_nm'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'institution_name' AND entity_role = 'CREDITOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_agt_clr_sys_mmb_id'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'clearing_system_id' AND entity_role = 'CREDITOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_agt_pstl_adr_ctry'
WHERE format_id = 'pacs.008.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'country' AND entity_role = 'CREDITOR_AGENT';


-- =====================================================
-- pacs.002.base - Fix entity mappings (similar pattern)
-- =====================================================

-- cdm_party - DEBTOR (original party from original payment)
UPDATE mapping.gold_field_mappings SET source_expression = 'orgnl_dbtr_nm'
WHERE format_id = 'pacs.002.base' AND gold_table = 'cdm_party' AND gold_column = 'name' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'orgnl_dbtr_pstl_adr_strt_nm'
WHERE format_id = 'pacs.002.base' AND gold_table = 'cdm_party' AND gold_column = 'address_line1' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'orgnl_dbtr_pstl_adr_twn_nm'
WHERE format_id = 'pacs.002.base' AND gold_table = 'cdm_party' AND gold_column = 'city' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'orgnl_dbtr_pstl_adr_ctry'
WHERE format_id = 'pacs.002.base' AND gold_table = 'cdm_party' AND gold_column = 'country' AND entity_role = 'DEBTOR';

-- cdm_party - CREDITOR (original party from original payment)
UPDATE mapping.gold_field_mappings SET source_expression = 'orgnl_cdtr_nm'
WHERE format_id = 'pacs.002.base' AND gold_table = 'cdm_party' AND gold_column = 'name' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'orgnl_cdtr_pstl_adr_strt_nm'
WHERE format_id = 'pacs.002.base' AND gold_table = 'cdm_party' AND gold_column = 'address_line1' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'orgnl_cdtr_pstl_adr_twn_nm'
WHERE format_id = 'pacs.002.base' AND gold_table = 'cdm_party' AND gold_column = 'city' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'orgnl_cdtr_pstl_adr_ctry'
WHERE format_id = 'pacs.002.base' AND gold_table = 'cdm_party' AND gold_column = 'country' AND entity_role = 'CREDITOR';

-- cdm_financial_institution - INSTRUCTING_AGENT
UPDATE mapping.gold_field_mappings SET source_expression = 'instg_agt_bic'
WHERE format_id = 'pacs.002.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'bic' AND entity_role = 'INSTRUCTING_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'instg_agt_nm'
WHERE format_id = 'pacs.002.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'institution_name' AND entity_role = 'INSTRUCTING_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'instg_agt_ctry'
WHERE format_id = 'pacs.002.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'country' AND entity_role = 'INSTRUCTING_AGENT';

-- cdm_financial_institution - INSTRUCTED_AGENT
UPDATE mapping.gold_field_mappings SET source_expression = 'instd_agt_bic'
WHERE format_id = 'pacs.002.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'bic' AND entity_role = 'INSTRUCTED_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'instd_agt_nm'
WHERE format_id = 'pacs.002.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'institution_name' AND entity_role = 'INSTRUCTED_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'instd_agt_ctry'
WHERE format_id = 'pacs.002.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'country' AND entity_role = 'INSTRUCTED_AGENT';


-- =====================================================
-- pacs.004.base - Fix entity mappings (payment return)
-- =====================================================

-- cdm_party - DEBTOR (return debtor / original creditor who returned)
UPDATE mapping.gold_field_mappings SET source_expression = 'rtr_dbtr_nm'
WHERE format_id = 'pacs.004.base' AND gold_table = 'cdm_party' AND gold_column = 'name' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'rtr_dbtr_pstl_adr_strt_nm'
WHERE format_id = 'pacs.004.base' AND gold_table = 'cdm_party' AND gold_column = 'address_line1' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'rtr_dbtr_pstl_adr_ctry'
WHERE format_id = 'pacs.004.base' AND gold_table = 'cdm_party' AND gold_column = 'country' AND entity_role = 'DEBTOR';

-- cdm_party - CREDITOR (return creditor / original debtor receiving return)
UPDATE mapping.gold_field_mappings SET source_expression = 'rtr_cdtr_nm'
WHERE format_id = 'pacs.004.base' AND gold_table = 'cdm_party' AND gold_column = 'name' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'rtr_cdtr_pstl_adr_strt_nm'
WHERE format_id = 'pacs.004.base' AND gold_table = 'cdm_party' AND gold_column = 'address_line1' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'rtr_cdtr_pstl_adr_ctry'
WHERE format_id = 'pacs.004.base' AND gold_table = 'cdm_party' AND gold_column = 'country' AND entity_role = 'CREDITOR';

-- cdm_financial_institution - DEBTOR_AGENT
UPDATE mapping.gold_field_mappings SET source_expression = 'rtr_dbtr_agt_bic'
WHERE format_id = 'pacs.004.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'bic' AND entity_role = 'DEBTOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'rtr_dbtr_agt_nm'
WHERE format_id = 'pacs.004.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'institution_name' AND entity_role = 'DEBTOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'rtr_dbtr_agt_ctry'
WHERE format_id = 'pacs.004.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'country' AND entity_role = 'DEBTOR_AGENT';

-- cdm_financial_institution - CREDITOR_AGENT
UPDATE mapping.gold_field_mappings SET source_expression = 'rtr_cdtr_agt_bic'
WHERE format_id = 'pacs.004.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'bic' AND entity_role = 'CREDITOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'rtr_cdtr_agt_nm'
WHERE format_id = 'pacs.004.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'institution_name' AND entity_role = 'CREDITOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'rtr_cdtr_agt_ctry'
WHERE format_id = 'pacs.004.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'country' AND entity_role = 'CREDITOR_AGENT';


-- =====================================================
-- pacs.009.base - Fix entity mappings (FI credit transfer)
-- =====================================================

-- cdm_financial_institution - DEBTOR (debtor FI)
UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_bic'
WHERE format_id = 'pacs.009.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'bic' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_lei'
WHERE format_id = 'pacs.009.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'lei' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_nm'
WHERE format_id = 'pacs.009.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'institution_name' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_ctry'
WHERE format_id = 'pacs.009.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'country' AND entity_role = 'DEBTOR';

-- cdm_financial_institution - CREDITOR (creditor FI)
UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_bic'
WHERE format_id = 'pacs.009.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'bic' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_lei'
WHERE format_id = 'pacs.009.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'lei' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_nm'
WHERE format_id = 'pacs.009.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'institution_name' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_ctry'
WHERE format_id = 'pacs.009.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'country' AND entity_role = 'CREDITOR';


-- =====================================================
-- pain.001.base - Fix entity mappings
-- =====================================================

-- cdm_party - INITIATING_PARTY
UPDATE mapping.gold_field_mappings SET source_expression = 'initg_pty_nm'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_party' AND gold_column = 'name' AND entity_role = 'INITIATING_PARTY';

UPDATE mapping.gold_field_mappings SET source_expression = 'initg_pty_id_org_id_lei'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_party' AND gold_column = 'lei' AND entity_role = 'INITIATING_PARTY';

UPDATE mapping.gold_field_mappings SET source_expression = 'initg_pty_id_org_id_any_bic'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_party' AND gold_column = 'bic' AND entity_role = 'INITIATING_PARTY';

-- cdm_party - DEBTOR
UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_nm'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_party' AND gold_column = 'name' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_pstl_adr_strt_nm'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_party' AND gold_column = 'address_line1' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_pstl_adr_twn_nm'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_party' AND gold_column = 'city' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_pstl_adr_ctry'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_party' AND gold_column = 'country' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_pstl_adr_pst_cd'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_party' AND gold_column = 'postal_code' AND entity_role = 'DEBTOR';

-- cdm_party - CREDITOR
UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_nm'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_party' AND gold_column = 'name' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_pstl_adr_strt_nm'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_party' AND gold_column = 'address_line1' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_pstl_adr_twn_nm'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_party' AND gold_column = 'city' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_pstl_adr_ctry'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_party' AND gold_column = 'country' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_pstl_adr_pst_cd'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_party' AND gold_column = 'postal_code' AND entity_role = 'CREDITOR';

-- cdm_account - DEBTOR
UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_acct_id_iban'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_account' AND gold_column = 'iban' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_acct_id_othr_id'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_account' AND gold_column = 'account_number' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_acct_tp_cd'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_account' AND gold_column = 'account_type' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_acct_ccy'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_account' AND gold_column = 'currency' AND entity_role = 'DEBTOR';

-- cdm_account - CREDITOR
UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_acct_id_iban'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_account' AND gold_column = 'iban' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_acct_id_othr_id'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_account' AND gold_column = 'account_number' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_acct_tp_cd'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_account' AND gold_column = 'account_type' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_acct_ccy'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_account' AND gold_column = 'currency' AND entity_role = 'CREDITOR';

-- cdm_financial_institution - DEBTOR_AGENT
UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_agt_bic'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'bic' AND entity_role = 'DEBTOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_agt_nm'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'institution_name' AND entity_role = 'DEBTOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_agt_ctry'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'country' AND entity_role = 'DEBTOR_AGENT';

-- cdm_financial_institution - CREDITOR_AGENT
UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_agt_bic'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'bic' AND entity_role = 'CREDITOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_agt_nm'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'institution_name' AND entity_role = 'CREDITOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_agt_ctry'
WHERE format_id = 'pain.001.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'country' AND entity_role = 'CREDITOR_AGENT';


-- =====================================================
-- pain.008.base - Fix entity mappings (direct debit)
-- =====================================================

-- cdm_party - INITIATING_PARTY
UPDATE mapping.gold_field_mappings SET source_expression = 'initg_pty_nm'
WHERE format_id = 'pain.008.base' AND gold_table = 'cdm_party' AND gold_column = 'name' AND entity_role = 'INITIATING_PARTY';

-- cdm_party - DEBTOR (the account being debited)
UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_nm'
WHERE format_id = 'pain.008.base' AND gold_table = 'cdm_party' AND gold_column = 'name' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_pstl_adr_strt_nm'
WHERE format_id = 'pain.008.base' AND gold_table = 'cdm_party' AND gold_column = 'address_line1' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_pstl_adr_ctry'
WHERE format_id = 'pain.008.base' AND gold_table = 'cdm_party' AND gold_column = 'country' AND entity_role = 'DEBTOR';

-- cdm_party - CREDITOR (the party initiating the debit)
UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_nm'
WHERE format_id = 'pain.008.base' AND gold_table = 'cdm_party' AND gold_column = 'name' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_pstl_adr_strt_nm'
WHERE format_id = 'pain.008.base' AND gold_table = 'cdm_party' AND gold_column = 'address_line1' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_pstl_adr_ctry'
WHERE format_id = 'pain.008.base' AND gold_table = 'cdm_party' AND gold_column = 'country' AND entity_role = 'CREDITOR';

-- cdm_account - DEBTOR
UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_acct_id_iban'
WHERE format_id = 'pain.008.base' AND gold_table = 'cdm_account' AND gold_column = 'iban' AND entity_role = 'DEBTOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_acct_id_othr_id'
WHERE format_id = 'pain.008.base' AND gold_table = 'cdm_account' AND gold_column = 'account_number' AND entity_role = 'DEBTOR';

-- cdm_account - CREDITOR
UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_acct_id_iban'
WHERE format_id = 'pain.008.base' AND gold_table = 'cdm_account' AND gold_column = 'iban' AND entity_role = 'CREDITOR';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_acct_id_othr_id'
WHERE format_id = 'pain.008.base' AND gold_table = 'cdm_account' AND gold_column = 'account_number' AND entity_role = 'CREDITOR';

-- cdm_financial_institution - DEBTOR_AGENT
UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_agt_bic'
WHERE format_id = 'pain.008.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'bic' AND entity_role = 'DEBTOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'dbtr_agt_nm'
WHERE format_id = 'pain.008.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'institution_name' AND entity_role = 'DEBTOR_AGENT';

-- cdm_financial_institution - CREDITOR_AGENT
UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_agt_bic'
WHERE format_id = 'pain.008.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'bic' AND entity_role = 'CREDITOR_AGENT';

UPDATE mapping.gold_field_mappings SET source_expression = 'cdtr_agt_nm'
WHERE format_id = 'pain.008.base' AND gold_table = 'cdm_financial_institution' AND gold_column = 'institution_name' AND entity_role = 'CREDITOR_AGENT';


-- Verify the updates
SELECT format_id, gold_table, gold_column, source_expression, entity_role
FROM mapping.gold_field_mappings
WHERE format_id LIKE '%.base'
  AND gold_table IN ('cdm_party', 'cdm_account', 'cdm_financial_institution')
ORDER BY format_id, gold_table, entity_role, gold_column;
