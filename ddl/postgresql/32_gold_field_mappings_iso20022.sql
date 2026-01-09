-- GPS CDM - Gold Field Mappings for ISO 20022 Message Types
-- ==========================================================
-- Maps Silver table columns to new semantic Gold tables
--
-- Version: 1.0
-- Date: 2026-01-08

-- =====================================================
-- Clear existing mappings for base formats to new Gold tables
-- =====================================================
DELETE FROM mapping.gold_field_mappings WHERE format_id IN (
    'pacs.008.base', 'pacs.009.base', 'pacs.002.base', 'pacs.004.base',
    'pain.001.base', 'pain.008.base', 'pain.002.base',
    'camt.053.base', 'camt.052.base', 'camt.054.base', 'camt.056.base',
    'pacs.003.base'
);

-- =====================================================
-- pacs.008.base → cdm_pacs_fi_customer_credit_transfer
-- =====================================================
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, transform_expression, ordinal_position, is_active)
VALUES
-- Primary key and lineage
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'transfer_id', '_GENERATED_UUID', NULL, NULL, 1, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'source_stg_id', '_CONTEXT.stg_id', NULL, NULL, 2, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'source_stg_table', '''stg_iso20022_pacs008''', NULL, NULL, 3, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'source_format', '_CONTEXT.format_id', NULL, NULL, 4, true),

-- Group Header
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'message_id', 'grp_hdr_msg_id', NULL, NULL, 10, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creation_datetime', 'grp_hdr_cre_dt_tm', NULL, NULL, 11, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'number_of_transactions', 'grp_hdr_nb_of_txs', NULL, NULL, 12, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'total_interbank_settlement_amount', 'grp_hdr_ctrl_sum', NULL, NULL, 13, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'settlement_method', 'grp_hdr_sttlm_mtd', NULL, NULL, 14, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'clearing_system_code', 'grp_hdr_clr_sys_cd', NULL, NULL, 15, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'clearing_system_proprietary', 'grp_hdr_clr_sys_prtry', NULL, NULL, 16, true),

-- Instructing/Instructed Agents
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'instructing_agent_bic', 'instg_agt_bic', NULL, NULL, 20, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'instructing_agent_lei', 'instg_agt_lei', NULL, NULL, 21, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'instructing_agent_clearing_id', 'instg_agt_clr_sys_mmb_id', NULL, NULL, 22, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'instructing_agent_name', 'instg_agt_nm', NULL, NULL, 23, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'instructing_agent_country', 'instg_agt_ctry', NULL, NULL, 24, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'instructed_agent_bic', 'instd_agt_bic', NULL, NULL, 25, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'instructed_agent_lei', 'instd_agt_lei', NULL, NULL, 26, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'instructed_agent_clearing_id', 'instd_agt_clr_sys_mmb_id', NULL, NULL, 27, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'instructed_agent_name', 'instd_agt_nm', NULL, NULL, 28, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'instructed_agent_country', 'instd_agt_ctry', NULL, NULL, 29, true),

-- Payment Identification
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'instruction_id', 'pmt_id_instr_id', NULL, NULL, 30, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'end_to_end_id', 'pmt_id_end_to_end_id', NULL, NULL, 31, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'uetr', 'pmt_id_uetr', NULL, NULL, 32, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'transaction_id', 'pmt_id_tx_id', NULL, NULL, 33, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'clearing_system_reference', 'pmt_id_clr_sys_ref', NULL, NULL, 34, true),

-- Payment Type
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'instruction_priority', 'pmt_tp_inf_instr_prty', NULL, NULL, 40, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'service_level_code', 'pmt_tp_inf_svc_lvl_cd', NULL, NULL, 41, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'service_level_proprietary', 'pmt_tp_inf_svc_lvl_prtry', NULL, NULL, 42, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'local_instrument_code', 'pmt_tp_inf_lcl_instrm_cd', NULL, NULL, 43, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'local_instrument_proprietary', 'pmt_tp_inf_lcl_instrm_prtry', NULL, NULL, 44, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'category_purpose_code', 'pmt_tp_inf_ctgy_purp_cd', NULL, NULL, 45, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'category_purpose_proprietary', 'pmt_tp_inf_ctgy_purp_prtry', NULL, NULL, 46, true),

-- Settlement
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'interbank_settlement_amount', 'intr_bk_sttlm_amt', NULL, NULL, 50, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'interbank_settlement_currency', 'intr_bk_sttlm_ccy', NULL, NULL, 51, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'interbank_settlement_date', 'intr_bk_sttlm_dt', NULL, NULL, 52, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'instructed_amount', 'instd_amt', NULL, NULL, 53, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'instructed_currency', 'instd_amt_ccy', NULL, NULL, 54, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'exchange_rate', 'xchg_rate', NULL, NULL, 55, true),

-- Charges
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'charge_bearer', 'chrg_br', NULL, NULL, 60, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'charges_amount', 'chrgs_inf_amt', NULL, NULL, 61, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'charges_currency', 'chrgs_inf_ccy', NULL, NULL, 62, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'charges_agent_bic', 'chrgs_inf_agt_bic', NULL, NULL, 63, true),

-- Debtor
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_name', 'dbtr_nm', NULL, NULL, 70, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_address_street', 'dbtr_pstl_adr_strt_nm', NULL, NULL, 71, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_address_building', 'dbtr_pstl_adr_bldg_nb', NULL, NULL, 72, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_address_postal_code', 'dbtr_pstl_adr_pst_cd', NULL, NULL, 73, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_address_town', 'dbtr_pstl_adr_twn_nm', NULL, NULL, 74, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_address_country_subdivision', 'dbtr_pstl_adr_ctry_sub_dvsn', NULL, NULL, 75, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_address_country', 'dbtr_pstl_adr_ctry', NULL, NULL, 76, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_address_lines', 'dbtr_pstl_adr_adr_line', NULL, NULL, 77, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_id_org_bic', 'dbtr_id_org_id_any_bic', NULL, NULL, 78, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_id_org_lei', 'dbtr_id_org_id_lei', NULL, NULL, 79, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_id_org_other', 'dbtr_id_org_id_othr_id', NULL, NULL, 80, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_id_org_other_scheme', 'dbtr_id_org_id_othr_schme_nm_cd', NULL, NULL, 81, true),

-- Debtor Account
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_account_iban', 'dbtr_acct_id_iban', NULL, NULL, 90, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_account_other', 'dbtr_acct_id_othr_id', NULL, NULL, 91, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_account_other_scheme', 'dbtr_acct_id_othr_schme_nm_cd', NULL, NULL, 92, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_account_type', 'dbtr_acct_tp_cd', NULL, NULL, 93, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_account_currency', 'dbtr_acct_ccy', NULL, NULL, 94, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_account_name', 'dbtr_acct_nm', NULL, NULL, 95, true),

-- Debtor Agent
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_agent_bic', 'dbtr_agt_bic', NULL, NULL, 100, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_agent_lei', 'dbtr_agt_lei', NULL, NULL, 101, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_agent_clearing_id', 'dbtr_agt_clr_sys_mmb_id', NULL, NULL, 102, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_agent_clearing_system', 'dbtr_agt_clr_sys_cd', NULL, NULL, 103, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_agent_name', 'dbtr_agt_nm', NULL, NULL, 104, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_agent_address_street', 'dbtr_agt_pstl_adr_strt_nm', NULL, NULL, 105, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_agent_address_town', 'dbtr_agt_pstl_adr_twn_nm', NULL, NULL, 106, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_agent_address_country', 'dbtr_agt_pstl_adr_ctry', NULL, NULL, 107, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_agent_branch_id', 'dbtr_agt_brnch_id', NULL, NULL, 108, true),

-- Creditor Agent
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_agent_bic', 'cdtr_agt_bic', NULL, NULL, 110, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_agent_lei', 'cdtr_agt_lei', NULL, NULL, 111, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_agent_clearing_id', 'cdtr_agt_clr_sys_mmb_id', NULL, NULL, 112, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_agent_clearing_system', 'cdtr_agt_clr_sys_cd', NULL, NULL, 113, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_agent_name', 'cdtr_agt_nm', NULL, NULL, 114, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_agent_address_street', 'cdtr_agt_pstl_adr_strt_nm', NULL, NULL, 115, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_agent_address_town', 'cdtr_agt_pstl_adr_twn_nm', NULL, NULL, 116, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_agent_address_country', 'cdtr_agt_pstl_adr_ctry', NULL, NULL, 117, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_agent_branch_id', 'cdtr_agt_brnch_id', NULL, NULL, 118, true),

-- Creditor
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_name', 'cdtr_nm', NULL, NULL, 120, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_address_street', 'cdtr_pstl_adr_strt_nm', NULL, NULL, 121, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_address_building', 'cdtr_pstl_adr_bldg_nb', NULL, NULL, 122, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_address_postal_code', 'cdtr_pstl_adr_pst_cd', NULL, NULL, 123, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_address_town', 'cdtr_pstl_adr_twn_nm', NULL, NULL, 124, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_address_country_subdivision', 'cdtr_pstl_adr_ctry_sub_dvsn', NULL, NULL, 125, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_address_country', 'cdtr_pstl_adr_ctry', NULL, NULL, 126, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_address_lines', 'cdtr_pstl_adr_adr_line', NULL, NULL, 127, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_id_org_bic', 'cdtr_id_org_id_any_bic', NULL, NULL, 128, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_id_org_lei', 'cdtr_id_org_id_lei', NULL, NULL, 129, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_id_org_other', 'cdtr_id_org_id_othr_id', NULL, NULL, 130, true),

-- Creditor Account
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_account_iban', 'cdtr_acct_id_iban', NULL, NULL, 140, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_account_other', 'cdtr_acct_id_othr_id', NULL, NULL, 141, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_account_other_scheme', 'cdtr_acct_id_othr_schme_nm_cd', NULL, NULL, 142, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_account_type', 'cdtr_acct_tp_cd', NULL, NULL, 143, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_account_currency', 'cdtr_acct_ccy', NULL, NULL, 144, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_account_name', 'cdtr_acct_nm', NULL, NULL, 145, true),

-- Intermediary Agents
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent1_bic', 'intrmy_agt1_bic', NULL, NULL, 150, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent1_lei', 'intrmy_agt1_lei', NULL, NULL, 151, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent1_clearing_id', 'intrmy_agt1_clr_sys_mmb_id', NULL, NULL, 152, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent1_name', 'intrmy_agt1_nm', NULL, NULL, 153, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent1_country', 'intrmy_agt1_ctry', NULL, NULL, 154, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent2_bic', 'intrmy_agt2_bic', NULL, NULL, 155, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent2_lei', 'intrmy_agt2_lei', NULL, NULL, 156, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent2_clearing_id', 'intrmy_agt2_clr_sys_mmb_id', NULL, NULL, 157, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent2_name', 'intrmy_agt2_nm', NULL, NULL, 158, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent2_country', 'intrmy_agt2_ctry', NULL, NULL, 159, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent3_bic', 'intrmy_agt3_bic', NULL, NULL, 160, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent3_clearing_id', 'intrmy_agt3_clr_sys_mmb_id', NULL, NULL, 161, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent3_country', 'intrmy_agt3_ctry', NULL, NULL, 162, true),

-- Ultimate Parties
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'ultimate_debtor_name', 'ultmt_dbtr_nm', NULL, NULL, 170, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'ultimate_debtor_address_country', 'ultmt_dbtr_pstl_adr_ctry', NULL, NULL, 171, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'ultimate_debtor_id', 'ultmt_dbtr_id_org_id_othr_id', NULL, NULL, 172, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'ultimate_creditor_name', 'ultmt_cdtr_nm', NULL, NULL, 173, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'ultimate_creditor_address_country', 'ultmt_cdtr_pstl_adr_ctry', NULL, NULL, 174, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'ultimate_creditor_id', 'ultmt_cdtr_id_org_id_othr_id', NULL, NULL, 175, true),

-- Remittance
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'remittance_unstructured', 'rmt_inf_ustrd', NULL, NULL, 180, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'remittance_structured', 'rmt_inf_strd', NULL, NULL, 181, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'purpose_code', 'purp_cd', NULL, NULL, 182, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'purpose_proprietary', 'purp_prtry', NULL, NULL, 183, true),

-- Regulatory & Supplementary
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'regulatory_reporting', 'rgltry_rptg', NULL, NULL, 190, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'tax_information', 'tax', NULL, NULL, 191, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'supplementary_data', 'splmtry_data', NULL, NULL, 192, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'scheme_identifiers', 'scheme_identifiers', NULL, NULL, 193, true),

-- Metadata
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', 'created_at', '_CONTEXT.now', NULL, NULL, 200, true),
('pacs.008.base', 'cdm_pacs_fi_customer_credit_transfer', '_batch_id', '_CONTEXT.batch_id', NULL, NULL, 201, true);



-- =====================================================
-- pacs.009.base → cdm_pacs_fi_credit_transfer
-- =====================================================
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, transform_expression, ordinal_position, is_active)
VALUES
-- Primary key and lineage
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'transfer_id', '_GENERATED_UUID', NULL, NULL, 1, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'source_stg_id', '_CONTEXT.stg_id', NULL, NULL, 2, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'source_stg_table', '''stg_iso20022_pacs009''', NULL, NULL, 3, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'source_format', '_CONTEXT.format_id', NULL, NULL, 4, true),

-- Group Header
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'message_id', 'grp_hdr_msg_id', NULL, NULL, 10, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'creation_datetime', 'grp_hdr_cre_dt_tm', NULL, NULL, 11, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'number_of_transactions', 'grp_hdr_nb_of_txs', NULL, NULL, 12, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'total_settlement_amount', 'grp_hdr_ctrl_sum', NULL, NULL, 13, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'settlement_method', 'grp_hdr_sttlm_mtd', NULL, NULL, 14, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'clearing_system_code', 'grp_hdr_clr_sys_cd', NULL, NULL, 15, true),

-- Instructing/Instructed Agents
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'instructing_agent_bic', 'instg_agt_bic', NULL, NULL, 20, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'instructing_agent_lei', 'instg_agt_lei', NULL, NULL, 21, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'instructed_agent_bic', 'instd_agt_bic', NULL, NULL, 22, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'instructed_agent_lei', 'instd_agt_lei', NULL, NULL, 23, true),

-- Payment Identification
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'instruction_id', 'pmt_id_instr_id', NULL, NULL, 30, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'end_to_end_id', 'pmt_id_end_to_end_id', NULL, NULL, 31, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'uetr', 'pmt_id_uetr', NULL, NULL, 32, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'transaction_id', 'pmt_id_tx_id', NULL, NULL, 33, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'clearing_system_reference', 'pmt_id_clr_sys_ref', NULL, NULL, 34, true),

-- Payment Type
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'instruction_priority', 'pmt_tp_inf_instr_prty', NULL, NULL, 40, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'service_level_code', 'pmt_tp_inf_svc_lvl_cd', NULL, NULL, 41, true),

-- Settlement
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'interbank_settlement_amount', 'intr_bk_sttlm_amt', NULL, NULL, 50, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'interbank_settlement_currency', 'intr_bk_sttlm_ccy', NULL, NULL, 51, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'interbank_settlement_date', 'intr_bk_sttlm_dt', NULL, NULL, 52, true),

-- Debtor Agent (Sending FI)
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'debtor_agent_bic', 'dbtr_agt_bic', NULL, NULL, 60, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'debtor_agent_lei', 'dbtr_agt_lei', NULL, NULL, 61, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'debtor_agent_clearing_id', 'dbtr_agt_clr_sys_mmb_id', NULL, NULL, 62, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'debtor_agent_name', 'dbtr_agt_nm', NULL, NULL, 63, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'debtor_agent_address_country', 'dbtr_agt_ctry', NULL, NULL, 64, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'debtor_agent_account_iban', 'dbtr_agt_acct_id', NULL, NULL, 65, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'debtor_agent_account_currency', 'dbtr_agt_acct_ccy', NULL, NULL, 66, true),

-- Creditor Agent (Receiving FI)
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'creditor_agent_bic', 'cdtr_agt_bic', NULL, NULL, 70, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'creditor_agent_lei', 'cdtr_agt_lei', NULL, NULL, 71, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'creditor_agent_clearing_id', 'cdtr_agt_clr_sys_mmb_id', NULL, NULL, 72, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'creditor_agent_name', 'cdtr_agt_nm', NULL, NULL, 73, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'creditor_agent_address_country', 'cdtr_agt_ctry', NULL, NULL, 74, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'creditor_agent_account_iban', 'cdtr_agt_acct_id', NULL, NULL, 75, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'creditor_agent_account_currency', 'cdtr_agt_acct_ccy', NULL, NULL, 76, true),

-- Intermediary Agents
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'intermediary_agent1_bic', 'intrmy_agt1_bic', NULL, NULL, 80, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'intermediary_agent1_clearing_id', 'intrmy_agt1_clr_sys_mmb_id', NULL, NULL, 81, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'intermediary_agent1_country', 'intrmy_agt1_ctry', NULL, NULL, 82, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'intermediary_agent2_bic', 'intrmy_agt2_bic', NULL, NULL, 83, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'intermediary_agent2_clearing_id', 'intrmy_agt2_clr_sys_mmb_id', NULL, NULL, 84, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'intermediary_agent2_country', 'intrmy_agt2_ctry', NULL, NULL, 85, true),

-- Underlying Customer Transfer
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'underlying_customer_transfer', 'undrlyg_cstmr_cdt_trf', NULL, NULL, 90, true),

-- Remittance & Purpose
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'remittance_unstructured', 'rmt_inf_ustrd', NULL, NULL, 100, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'purpose_code', 'purp_cd', NULL, NULL, 101, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'supplementary_data', 'splmtry_data', NULL, NULL, 102, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'scheme_identifiers', 'scheme_identifiers', NULL, NULL, 103, true),

-- Metadata
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', 'created_at', '_CONTEXT.now', NULL, NULL, 200, true),
('pacs.009.base', 'cdm_pacs_fi_credit_transfer', '_batch_id', '_CONTEXT.batch_id', NULL, NULL, 201, true);



-- =====================================================
-- pacs.002.base → cdm_pacs_fi_payment_status_report
-- =====================================================
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, transform_expression, ordinal_position, is_active)
VALUES
-- Primary key and lineage
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'status_report_id', '_GENERATED_UUID', NULL, NULL, 1, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'source_stg_id', '_CONTEXT.stg_id', NULL, NULL, 2, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'source_stg_table', '''stg_iso20022_pacs002''', NULL, NULL, 3, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'source_format', '_CONTEXT.format_id', NULL, NULL, 4, true),

-- Message Header
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'message_id', 'grp_hdr_msg_id', NULL, NULL, 10, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'creation_datetime', 'grp_hdr_cre_dt_tm', NULL, NULL, 11, true),

-- Original Group Information
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_message_id', 'orgnl_grp_inf_orgnl_msg_id', NULL, NULL, 20, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_message_name_id', 'orgnl_grp_inf_orgnl_msg_nm_id', NULL, NULL, 21, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_creation_datetime', 'orgnl_grp_inf_orgnl_cre_dt_tm', NULL, NULL, 22, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_number_of_transactions', 'orgnl_grp_inf_orgnl_nb_of_txs', NULL, NULL, 23, true),

-- Group Status
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'group_status', 'orgnl_grp_inf_grp_sts', NULL, NULL, 30, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'group_status_reason_code', 'orgnl_grp_inf_sts_rsn_cd', NULL, NULL, 31, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'group_status_reason_info', 'orgnl_grp_inf_sts_rsn_addtl_inf', NULL, NULL, 32, true),

-- Transaction Status
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'status_id', 'tx_inf_sts_id', NULL, NULL, 40, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_instruction_id', 'tx_inf_orgnl_instr_id', NULL, NULL, 41, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_end_to_end_id', 'tx_inf_orgnl_end_to_end_id', NULL, NULL, 42, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_uetr', 'tx_inf_orgnl_uetr', NULL, NULL, 43, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'transaction_status', 'tx_inf_tx_sts', NULL, NULL, 44, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'status_reason_code', 'tx_inf_sts_rsn_cd', NULL, NULL, 45, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'status_reason_info', 'tx_inf_sts_rsn_addtl_inf', NULL, NULL, 46, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'acceptance_datetime', 'tx_inf_accpt_dt_tm', NULL, NULL, 47, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'clearing_system_reference', 'tx_inf_clr_sys_ref', NULL, NULL, 48, true),

-- Original Transaction Reference
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_settlement_amount', 'orgnl_tx_ref_intr_bk_sttlm_amt', NULL, NULL, 50, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_settlement_currency', 'orgnl_tx_ref_intr_bk_sttlm_ccy', NULL, NULL, 51, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_settlement_date', 'orgnl_tx_ref_intr_bk_sttlm_dt', NULL, NULL, 52, true),

-- Original Parties
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_debtor_name', 'orgnl_tx_ref_dbtr_nm', NULL, NULL, 60, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_debtor_account_iban', 'orgnl_tx_ref_dbtr_acct_id_iban', NULL, NULL, 61, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_debtor_agent_bic', 'orgnl_tx_ref_dbtr_agt_bic', NULL, NULL, 62, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_creditor_name', 'orgnl_tx_ref_cdtr_nm', NULL, NULL, 63, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_creditor_account_iban', 'orgnl_tx_ref_cdtr_acct_id_iban', NULL, NULL, 64, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'original_creditor_agent_bic', 'orgnl_tx_ref_cdtr_agt_bic', NULL, NULL, 65, true),

-- Metadata
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', 'created_at', '_CONTEXT.now', NULL, NULL, 200, true),
('pacs.002.base', 'cdm_pacs_fi_payment_status_report', '_batch_id', '_CONTEXT.batch_id', NULL, NULL, 201, true);



-- =====================================================
-- pacs.004.base → cdm_pacs_payment_return
-- =====================================================
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, transform_expression, ordinal_position, is_active)
VALUES
-- Primary key and lineage
('pacs.004.base', 'cdm_pacs_payment_return', 'return_id', '_GENERATED_UUID', NULL, NULL, 1, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'source_stg_id', '_CONTEXT.stg_id', NULL, NULL, 2, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'source_stg_table', '''stg_iso20022_pacs004''', NULL, NULL, 3, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'source_format', '_CONTEXT.format_id', NULL, NULL, 4, true),

-- Message Header
('pacs.004.base', 'cdm_pacs_payment_return', 'message_id', 'grp_hdr_msg_id', NULL, NULL, 10, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'creation_datetime', 'grp_hdr_cre_dt_tm', NULL, NULL, 11, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'number_of_transactions', 'grp_hdr_nb_of_txs', NULL, NULL, 12, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'settlement_method', 'grp_hdr_sttlm_mtd', NULL, NULL, 13, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'clearing_system_code', 'grp_hdr_clr_sys_cd', NULL, NULL, 14, true),

-- Original Group Information
('pacs.004.base', 'cdm_pacs_payment_return', 'original_message_id', 'orgnl_grp_inf_orgnl_msg_id', NULL, NULL, 20, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_message_name_id', 'orgnl_grp_inf_orgnl_msg_nm_id', NULL, NULL, 21, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_creation_datetime', 'orgnl_grp_inf_orgnl_cre_dt_tm', NULL, NULL, 22, true),

-- Return Transaction
('pacs.004.base', 'cdm_pacs_payment_return', 'return_identification', 'tx_inf_rtr_id', NULL, NULL, 30, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_instruction_id', 'tx_inf_orgnl_instr_id', NULL, NULL, 31, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_end_to_end_id', 'tx_inf_orgnl_end_to_end_id', NULL, NULL, 32, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_transaction_id', 'tx_inf_orgnl_tx_id', NULL, NULL, 33, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_uetr', 'tx_inf_orgnl_uetr', NULL, NULL, 34, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_clearing_system_reference', 'tx_inf_orgnl_clr_sys_ref', NULL, NULL, 35, true),

-- Return Reason
('pacs.004.base', 'cdm_pacs_payment_return', 'return_reason_code', 'tx_inf_rtr_rsn_cd', NULL, NULL, 40, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'return_reason_proprietary', 'tx_inf_rtr_rsn_prtry', NULL, NULL, 41, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'return_reason_info', 'tx_inf_rtr_rsn_addtl_inf', NULL, NULL, 42, true),

-- Returned Amount
('pacs.004.base', 'cdm_pacs_payment_return', 'returned_settlement_amount', 'tx_inf_rtrd_intr_bk_sttlm_amt', NULL, NULL, 50, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'returned_settlement_currency', 'tx_inf_rtrd_intr_bk_sttlm_ccy', NULL, NULL, 51, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'return_settlement_date', 'tx_inf_intr_bk_sttlm_dt', NULL, NULL, 52, true),

-- Original Transaction Reference
('pacs.004.base', 'cdm_pacs_payment_return', 'original_settlement_amount', 'orgnl_tx_ref_intr_bk_sttlm_amt', NULL, NULL, 60, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_settlement_currency', 'orgnl_tx_ref_intr_bk_sttlm_ccy', NULL, NULL, 61, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_settlement_date', 'orgnl_tx_ref_intr_bk_sttlm_dt', NULL, NULL, 62, true),

-- Original Parties
('pacs.004.base', 'cdm_pacs_payment_return', 'original_debtor_name', 'orgnl_tx_ref_dbtr_nm', NULL, NULL, 70, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_debtor_address_country', 'orgnl_tx_ref_dbtr_pstl_adr_ctry', NULL, NULL, 71, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_debtor_account_iban', 'orgnl_tx_ref_dbtr_acct_id_iban', NULL, NULL, 72, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_debtor_agent_bic', 'orgnl_tx_ref_dbtr_agt_bic', NULL, NULL, 73, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_creditor_name', 'orgnl_tx_ref_cdtr_nm', NULL, NULL, 74, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_creditor_address_country', 'orgnl_tx_ref_cdtr_pstl_adr_ctry', NULL, NULL, 75, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_creditor_account_iban', 'orgnl_tx_ref_cdtr_acct_id_iban', NULL, NULL, 76, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'original_creditor_agent_bic', 'orgnl_tx_ref_cdtr_agt_bic', NULL, NULL, 77, true),

-- Instructing/Instructed Agents
('pacs.004.base', 'cdm_pacs_payment_return', 'instructing_agent_bic', 'instg_agt_bic', NULL, NULL, 80, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'instructing_agent_clearing_id', 'instg_agt_clr_sys_mmb_id', NULL, NULL, 81, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'instructed_agent_bic', 'instd_agt_bic', NULL, NULL, 82, true),
('pacs.004.base', 'cdm_pacs_payment_return', 'instructed_agent_clearing_id', 'instd_agt_clr_sys_mmb_id', NULL, NULL, 83, true),

-- Remittance
('pacs.004.base', 'cdm_pacs_payment_return', 'remittance_unstructured', 'rmt_inf_ustrd', NULL, NULL, 90, true),

-- Metadata
('pacs.004.base', 'cdm_pacs_payment_return', 'created_at', '_CONTEXT.now', NULL, NULL, 200, true),
('pacs.004.base', 'cdm_pacs_payment_return', '_batch_id', '_CONTEXT.batch_id', NULL, NULL, 201, true);



-- =====================================================
-- pain.001.base → cdm_pain_customer_credit_transfer_initiation
-- =====================================================
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, transform_expression, ordinal_position, is_active)
VALUES
-- Primary key and lineage
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'initiation_id', '_GENERATED_UUID', NULL, NULL, 1, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'source_stg_id', '_CONTEXT.stg_id', NULL, NULL, 2, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'source_stg_table', '''stg_iso20022_pain001''', NULL, NULL, 3, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'source_format', '_CONTEXT.format_id', NULL, NULL, 4, true),

-- Message Header
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'message_id', 'grp_hdr_msg_id', NULL, NULL, 10, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'creation_datetime', 'grp_hdr_cre_dt_tm', NULL, NULL, 11, true),

-- Initiating Party
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'initiating_party_name', 'grp_hdr_initg_pty_nm', NULL, NULL, 20, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'initiating_party_id', 'grp_hdr_initg_pty_id_org_id_othr_id', NULL, NULL, 21, true),

-- Payment Information
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'payment_info_id', 'pmt_inf_id', NULL, NULL, 30, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'payment_method', 'pmt_mtd', NULL, NULL, 31, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'batch_booking', 'btch_bookg', NULL, NULL, 32, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'number_of_transactions', 'nb_of_txs', NULL, NULL, 33, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'control_sum', 'ctrl_sum', NULL, NULL, 34, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'requested_execution_date', 'reqd_exctn_dt', NULL, NULL, 35, true),

-- Service Level
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'service_level_code', 'pmt_tp_inf_svc_lvl_cd', NULL, NULL, 40, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'local_instrument_code', 'pmt_tp_inf_lcl_instrm_cd', NULL, NULL, 41, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'category_purpose_code', 'pmt_tp_inf_ctgy_purp_cd', NULL, NULL, 42, true),

-- Debtor
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_name', 'dbtr_nm', NULL, NULL, 50, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_address_street', 'dbtr_pstl_adr_strt_nm', NULL, NULL, 51, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_address_building', 'dbtr_pstl_adr_bldg_nb', NULL, NULL, 52, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_address_postal_code', 'dbtr_pstl_adr_pst_cd', NULL, NULL, 53, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_address_town', 'dbtr_pstl_adr_twn_nm', NULL, NULL, 54, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_address_country', 'dbtr_pstl_adr_ctry', NULL, NULL, 55, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_id', 'dbtr_id_org_id_othr_id', NULL, NULL, 56, true),

-- Debtor Account
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_account_iban', 'dbtr_acct_id_iban', NULL, NULL, 60, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_account_other', 'dbtr_acct_id_othr_id', NULL, NULL, 61, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_account_currency', 'dbtr_acct_ccy', NULL, NULL, 62, true),

-- Debtor Agent
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_agent_bic', 'dbtr_agt_bic', NULL, NULL, 70, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_agent_clearing_system_id', 'dbtr_agt_clr_sys_mmb_id', NULL, NULL, 71, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_agent_name', 'dbtr_agt_nm', NULL, NULL, 72, true),

-- Transaction Details
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'instruction_id', 'pmt_id_instr_id', NULL, NULL, 80, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'end_to_end_id', 'pmt_id_end_to_end_id', NULL, NULL, 81, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'instructed_amount', 'instd_amt', NULL, NULL, 82, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'instructed_currency', 'instd_amt_ccy', NULL, NULL, 83, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'charge_bearer', 'chrg_br', NULL, NULL, 84, true),

-- Creditor Agent
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_agent_bic', 'cdtr_agt_bic', NULL, NULL, 90, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_agent_clearing_system_id', 'cdtr_agt_clr_sys_mmb_id', NULL, NULL, 91, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_agent_name', 'cdtr_agt_nm', NULL, NULL, 92, true),

-- Creditor
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_name', 'cdtr_nm', NULL, NULL, 100, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_address_street', 'cdtr_pstl_adr_strt_nm', NULL, NULL, 101, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_address_building', 'cdtr_pstl_adr_bldg_nb', NULL, NULL, 102, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_address_postal_code', 'cdtr_pstl_adr_pst_cd', NULL, NULL, 103, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_address_town', 'cdtr_pstl_adr_twn_nm', NULL, NULL, 104, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_address_country', 'cdtr_pstl_adr_ctry', NULL, NULL, 105, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_id', 'cdtr_id_org_id_othr_id', NULL, NULL, 106, true),

-- Creditor Account
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_account_iban', 'cdtr_acct_id_iban', NULL, NULL, 110, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_account_other', 'cdtr_acct_id_othr_id', NULL, NULL, 111, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_account_currency', 'cdtr_acct_ccy', NULL, NULL, 112, true),

-- Ultimate Parties
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'ultimate_debtor_name', 'ultmt_dbtr_nm', NULL, NULL, 120, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'ultimate_creditor_name', 'ultmt_cdtr_nm', NULL, NULL, 121, true),

-- Remittance
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'remittance_unstructured', 'rmt_inf_ustrd', NULL, NULL, 130, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'remittance_structured', 'rmt_inf_strd', NULL, NULL, 131, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'purpose_code', 'purp_cd', NULL, NULL, 132, true),

-- Regulatory
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'regulatory_reporting', 'rgltry_rptg', NULL, NULL, 140, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'supplementary_data', 'splmtry_data', NULL, NULL, 141, true),

-- Metadata
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', 'created_at', '_CONTEXT.now', NULL, NULL, 200, true),
('pain.001.base', 'cdm_pain_customer_credit_transfer_initiation', '_batch_id', '_CONTEXT.batch_id', NULL, NULL, 201, true);



-- =====================================================
-- pain.008.base → cdm_pain_customer_direct_debit_initiation
-- =====================================================
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, transform_expression, ordinal_position, is_active)
VALUES
-- Primary key and lineage
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'initiation_id', '_GENERATED_UUID', NULL, NULL, 1, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'source_stg_id', '_CONTEXT.stg_id', NULL, NULL, 2, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'source_stg_table', '''stg_iso20022_pain008''', NULL, NULL, 3, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'source_format', '_CONTEXT.format_id', NULL, NULL, 4, true),

-- Message Header
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'message_id', 'grp_hdr_msg_id', NULL, NULL, 10, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'creation_datetime', 'grp_hdr_cre_dt_tm', NULL, NULL, 11, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'number_of_transactions', 'grp_hdr_nb_of_txs', NULL, NULL, 12, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'control_sum', 'grp_hdr_ctrl_sum', NULL, NULL, 13, true),

-- Initiating Party
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'initiating_party_name', 'grp_hdr_initg_pty_nm', NULL, NULL, 20, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'initiating_party_id', 'grp_hdr_initg_pty_id_org_id_othr_id', NULL, NULL, 21, true),

-- Payment Information
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'payment_info_id', 'pmt_inf_id', NULL, NULL, 30, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'payment_method', 'pmt_mtd', NULL, NULL, 31, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'service_level_code', 'pmt_tp_inf_svc_lvl_cd', NULL, NULL, 32, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'local_instrument_code', 'pmt_tp_inf_lcl_instrm_cd', NULL, NULL, 33, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'sequence_type', 'pmt_tp_inf_seq_tp', NULL, NULL, 34, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'category_purpose_code', 'pmt_tp_inf_ctgy_purp_cd', NULL, NULL, 35, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'requested_collection_date', 'reqd_colltn_dt', NULL, NULL, 36, true),

-- Creditor (Collecting Party)
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'creditor_name', 'cdtr_nm', NULL, NULL, 40, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'creditor_address_street', 'cdtr_pstl_adr_strt_nm', NULL, NULL, 41, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'creditor_address_postal_code', 'cdtr_pstl_adr_pst_cd', NULL, NULL, 42, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'creditor_address_town', 'cdtr_pstl_adr_twn_nm', NULL, NULL, 43, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'creditor_address_country', 'cdtr_pstl_adr_ctry', NULL, NULL, 44, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'creditor_id', 'cdtr_id_prvt_id_othr_id', NULL, NULL, 45, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'creditor_id_type', 'cdtr_id_prvt_id_othr_schme_nm_prtry', NULL, NULL, 46, true),

-- Creditor Account
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'creditor_account_iban', 'cdtr_acct_id_iban', NULL, NULL, 50, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'creditor_account_other', 'cdtr_acct_id_othr_id', NULL, NULL, 51, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'creditor_account_currency', 'cdtr_acct_ccy', NULL, NULL, 52, true),

-- Creditor Agent
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'creditor_agent_bic', 'cdtr_agt_bic', NULL, NULL, 60, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'creditor_agent_clearing_system_id', 'cdtr_agt_clr_sys_mmb_id', NULL, NULL, 61, true),

-- Direct Debit Transaction
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'instruction_id', 'drct_dbt_tx_inf_pmt_id_instr_id', NULL, NULL, 70, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'end_to_end_id', 'drct_dbt_tx_inf_pmt_id_end_to_end_id', NULL, NULL, 71, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'instructed_amount', 'drct_dbt_tx_inf_instd_amt', NULL, NULL, 72, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'instructed_currency', 'drct_dbt_tx_inf_instd_amt_ccy', NULL, NULL, 73, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'charge_bearer', 'drct_dbt_tx_inf_chrgbr', NULL, NULL, 74, true),

-- Mandate Information
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'mandate_id', 'drct_dbt_tx_inf_mndt_id', NULL, NULL, 80, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'mandate_date_of_signature', 'drct_dbt_tx_inf_mndt_dt_of_sgntr', NULL, NULL, 81, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'amendment_indicator', 'drct_dbt_tx_inf_mndt_amdmnt_ind', NULL, NULL, 82, true),

-- Debtor Agent
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'debtor_agent_bic', 'dbtr_agt_bic', NULL, NULL, 90, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'debtor_agent_clearing_system_id', 'dbtr_agt_clr_sys_mmb_id', NULL, NULL, 91, true),

-- Debtor
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'debtor_name', 'dbtr_nm', NULL, NULL, 100, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'debtor_address_street', 'dbtr_pstl_adr_strt_nm', NULL, NULL, 101, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'debtor_address_postal_code', 'dbtr_pstl_adr_pst_cd', NULL, NULL, 102, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'debtor_address_town', 'dbtr_pstl_adr_twn_nm', NULL, NULL, 103, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'debtor_address_country', 'dbtr_pstl_adr_ctry', NULL, NULL, 104, true),

-- Debtor Account
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'debtor_account_iban', 'dbtr_acct_id_iban', NULL, NULL, 110, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'debtor_account_other', 'dbtr_acct_id_othr_id', NULL, NULL, 111, true),

-- Remittance
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'remittance_unstructured', 'rmt_inf_ustrd', NULL, NULL, 120, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'remittance_structured_reference', 'rmt_inf_strd_cdtr_ref_inf_ref', NULL, NULL, 121, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'purpose_code', 'purp_cd', NULL, NULL, 122, true),

-- Supplementary
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'supplementary_data', 'splmtry_data', NULL, NULL, 130, true),

-- Metadata
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', 'created_at', '_CONTEXT.now', NULL, NULL, 200, true),
('pain.008.base', 'cdm_pain_customer_direct_debit_initiation', '_batch_id', '_CONTEXT.batch_id', NULL, NULL, 201, true);



-- =====================================================
-- camt.053.base → cdm_camt_bank_to_customer_statement
-- =====================================================
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, transform_expression, ordinal_position, is_active)
VALUES
-- Primary key and lineage
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'statement_id', '_GENERATED_UUID', NULL, NULL, 1, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'source_stg_id', '_CONTEXT.stg_id', NULL, NULL, 2, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'source_stg_table', '''stg_iso20022_camt053''', NULL, NULL, 3, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'source_format', '_CONTEXT.format_id', NULL, NULL, 4, true),

-- Message Header
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'message_id', 'grp_hdr_msg_id', NULL, NULL, 10, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'creation_datetime', 'grp_hdr_cre_dt_tm', NULL, NULL, 11, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'message_recipient_name', 'grp_hdr_msg_rcpt_nm', NULL, NULL, 12, true),

-- Statement Identification
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'statement_reference', 'stmt_id', NULL, NULL, 20, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'electronic_sequence_number', 'stmt_elctrnc_seq_nb', NULL, NULL, 21, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'statement_creation_datetime', 'stmt_cre_dt_tm', NULL, NULL, 22, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'from_datetime', 'stmt_fr_dt_tm', NULL, NULL, 23, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'to_datetime', 'stmt_to_dt_tm', NULL, NULL, 24, true),

-- Account
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'account_iban', 'acct_id_iban', NULL, NULL, 30, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'account_other_id', 'acct_id_othr_id', NULL, NULL, 31, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'account_currency', 'acct_ccy', NULL, NULL, 32, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'account_owner_name', 'acct_ownr_nm', NULL, NULL, 33, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'account_servicer_bic', 'acct_svcr_bic', NULL, NULL, 34, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'account_servicer_name', 'acct_svcr_nm', NULL, NULL, 35, true),

-- Opening Balance
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'opening_balance_amount', 'opening_bal', NULL, NULL, 40, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'opening_balance_currency', 'opening_bal_ccy', NULL, NULL, 41, true),

-- Closing Balance
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'closing_balance_amount', 'closing_bal', NULL, NULL, 50, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'closing_balance_currency', 'closing_bal_ccy', NULL, NULL, 51, true),

-- Available Balance
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'available_balance_amount', 'available_bal', NULL, NULL, 60, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'available_balance_currency', 'available_bal_ccy', NULL, NULL, 61, true),

-- Transaction Summary
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'total_number_of_entries', 'ttl_nb_of_ntries', NULL, NULL, 70, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'total_sum_of_entries', 'ttl_sum', NULL, NULL, 71, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'total_credit_entries_count', 'ttl_cdt_nb_of_ntries', NULL, NULL, 72, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'total_credit_entries_sum', 'ttl_cdt_sum', NULL, NULL, 73, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'total_debit_entries_count', 'ttl_dbt_nb_of_ntries', NULL, NULL, 74, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'total_debit_entries_sum', 'ttl_dbt_sum', NULL, NULL, 75, true),

-- Entries
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'entries_count', 'ntry_count', NULL, NULL, 80, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'entries', 'ntries', NULL, NULL, 81, true),

-- Metadata
('camt.053.base', 'cdm_camt_bank_to_customer_statement', 'created_at', '_CONTEXT.now', NULL, NULL, 200, true),
('camt.053.base', 'cdm_camt_bank_to_customer_statement', '_batch_id', '_CONTEXT.batch_id', NULL, NULL, 201, true);



-- =====================================================
-- camt.056.base → cdm_camt_fi_payment_cancellation_request
-- =====================================================
INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, transform_expression, ordinal_position, is_active)
VALUES
-- Primary key and lineage
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'cancellation_request_id', '_GENERATED_UUID', NULL, NULL, 1, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'source_stg_id', '_CONTEXT.stg_id', NULL, NULL, 2, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'source_stg_table', '''stg_iso20022_camt056''', NULL, NULL, 3, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'source_format', '_CONTEXT.format_id', NULL, NULL, 4, true),

-- Assignment
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'assignment_id', 'assgnmt_id', NULL, NULL, 10, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'assignment_creation_datetime', 'assgnmt_cre_dt_tm', NULL, NULL, 11, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'assigner_agent_bic', 'assgnr_agt_bic', NULL, NULL, 12, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'assigner_agent_name', 'assgnr_agt_nm', NULL, NULL, 13, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'assignee_agent_bic', 'assgne_agt_bic', NULL, NULL, 14, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'assignee_agent_name', 'assgne_agt_nm', NULL, NULL, 15, true),

-- Case Information
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'case_id', 'case_id', NULL, NULL, 20, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'case_creator_name', 'case_cretr_nm', NULL, NULL, 21, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'case_creator_bic', 'case_cretr_bic', NULL, NULL, 22, true),

-- Control
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'number_of_transactions_requested', 'nb_of_txs', NULL, NULL, 30, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'control_sum', 'ctrl_sum', NULL, NULL, 31, true),

-- Original Group Information
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_message_id', 'orgnl_grp_inf_orgnl_msg_id', NULL, NULL, 40, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_message_name_id', 'orgnl_grp_inf_orgnl_msg_nm_id', NULL, NULL, 41, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_creation_datetime', 'orgnl_grp_inf_orgnl_cre_dt_tm', NULL, NULL, 42, true),

-- Transaction Information
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'cancellation_id', 'tx_inf_cxl_id', NULL, NULL, 50, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_instruction_id', 'tx_inf_orgnl_instr_id', NULL, NULL, 51, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_end_to_end_id', 'tx_inf_orgnl_end_to_end_id', NULL, NULL, 52, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_transaction_id', 'tx_inf_orgnl_tx_id', NULL, NULL, 53, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_uetr', 'tx_inf_orgnl_uetr', NULL, NULL, 54, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_clearing_system_reference', 'tx_inf_orgnl_clr_sys_ref', NULL, NULL, 55, true),

-- Cancellation Reason
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'cancellation_reason_code', 'tx_inf_cxl_rsn_cd', NULL, NULL, 60, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'cancellation_reason_proprietary', 'tx_inf_cxl_rsn_prtry', NULL, NULL, 61, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'cancellation_reason_info', 'tx_inf_cxl_rsn_addtl_inf', NULL, NULL, 62, true),

-- Original Transaction Reference
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_settlement_amount', 'orgnl_tx_ref_intr_bk_sttlm_amt', NULL, NULL, 70, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_settlement_currency', 'orgnl_tx_ref_intr_bk_sttlm_ccy', NULL, NULL, 71, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_settlement_date', 'orgnl_tx_ref_intr_bk_sttlm_dt', NULL, NULL, 72, true),

-- Original Parties
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_debtor_name', 'orgnl_tx_ref_dbtr_nm', NULL, NULL, 80, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_debtor_account_iban', 'orgnl_tx_ref_dbtr_acct_id_iban', NULL, NULL, 81, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_debtor_account_other', 'orgnl_tx_ref_dbtr_acct_id_othr_id', NULL, NULL, 82, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_debtor_agent_bic', 'orgnl_tx_ref_dbtr_agt_bic', NULL, NULL, 83, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_creditor_name', 'orgnl_tx_ref_cdtr_nm', NULL, NULL, 84, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_creditor_account_iban', 'orgnl_tx_ref_cdtr_acct_id_iban', NULL, NULL, 85, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_creditor_account_other', 'orgnl_tx_ref_cdtr_acct_id_othr_id', NULL, NULL, 86, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'original_creditor_agent_bic', 'orgnl_tx_ref_cdtr_agt_bic', NULL, NULL, 87, true),

-- Supplementary
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'supplementary_data', 'splmtry_data', NULL, NULL, 90, true),

-- Metadata
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', 'created_at', '_CONTEXT.now', NULL, NULL, 200, true),
('camt.056.base', 'cdm_camt_fi_payment_cancellation_request', '_batch_id', '_CONTEXT.batch_id', NULL, NULL, 201, true);
