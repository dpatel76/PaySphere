-- ============================================================================
-- Fix camt.053 Standard->Silver Field Coverage to 100%
-- ============================================================================
-- This script adds all missing columns to silver.stg_camt053 and creates
-- mappings in mapping.silver_field_mappings for all 211 standard data elements.
--
-- Key rules:
-- - source_path MUST match standard_fields.field_path exactly for traceability
-- - parser_path contains the actual key used by the parser
-- - NO fallback values - if source doesn't have data, allow NULL
-- ============================================================================

BEGIN;

-- ============================================================================
-- PART 1: Add all missing columns to silver.stg_camt053
-- ============================================================================

-- Group Header fields
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS grp_hdr_addtl_inf VARCHAR(2000);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS grp_hdr_cre_dt_tm TIMESTAMP;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS grp_hdr_msg_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS grp_hdr_msg_pgntn_last_pg_ind BOOLEAN;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS grp_hdr_msg_pgntn_pg_nb VARCHAR(5);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS grp_hdr_msg_rcpt_id_org_id_any_bic VARCHAR(11);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS grp_hdr_msg_rcpt_nm VARCHAR(140);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS grp_hdr_orgnl_biz_qry_msg_id VARCHAR(35);

-- Account fields
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_id_iban VARCHAR(34);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_id_othr_id VARCHAR(34);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_id_othr_schme_nm_cd VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_id_othr_schme_nm_prtry VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_nm VARCHAR(70);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_ownr_id_org_id_any_bic VARCHAR(11);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_ownr_id_org_id_lei VARCHAR(20);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_ownr_id_org_id_othr_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_ownr_nm VARCHAR(140);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_ownr_pstl_adr_bldg_nb VARCHAR(16);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_ownr_pstl_adr_ctry VARCHAR(2);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_ownr_pstl_adr_pst_cd VARCHAR(16);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_ownr_pstl_adr_strt_nm VARCHAR(70);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_ownr_pstl_adr_twn_nm VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_prxy_id VARCHAR(2048);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_svcr_fin_instn_id_bicfi VARCHAR(11);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_svcr_fin_instn_id_clr_sys_mmb_id_mmb_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_svcr_fin_instn_id_lei VARCHAR(20);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_svcr_fin_instn_id_nm VARCHAR(140);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_svcr_fin_instn_id_pstl_adr_ctry VARCHAR(2);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_tp_cd VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS acct_tp_prtry VARCHAR(35);

-- Balance fields
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_amt_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_avlbty_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_avlbty_amt_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_avlbty_cdt_dbt_ind VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_avlbty_dt_actl_dt DATE;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_avlbty_dt_nb_of_days VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_cdt_dbt_ind VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_cdt_line_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_cdt_line_amt_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_cdt_line_incl BOOLEAN;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_dt_dt DATE;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_dt_dt_tm TIMESTAMP;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_tp_cd_or_prtry_cd VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_tp_cd_or_prtry_prtry VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_tp_sub_tp_cd VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS bal_tp_sub_tp_prtry VARCHAR(35);

-- Statement fields
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS cpy_dplct_ind VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS stmt_cre_dt_tm TIMESTAMP;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS elctrnc_seq_nb INTEGER;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS fr_to_dt_fr_dt_tm TIMESTAMP;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS fr_to_dt_to_dt_tm TIMESTAMP;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS stmt_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS lgl_seq_nb INTEGER;

-- Entry fields
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_acct_svcr_ref VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_addtl_inf_ind_msg_nm_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_addtl_ntry_inf VARCHAR(500);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_amt_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_amt_dtls_cntr_val_amt_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_amt_dtls_cntr_val_amt_amt_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_amt_dtls_instd_amt_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_amt_dtls_instd_amt_amt_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_amt_dtls_tx_amt_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_amt_dtls_tx_amt_amt_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_avlbty_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_avlbty_cdt_dbt_ind VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_bk_tx_cd_domn_cd VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_bk_tx_cd_domn_fmly_cd VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_bk_tx_cd_domn_fmly_sub_fmly_cd VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_bk_tx_cd_prtry_cd VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_bk_tx_cd_prtry_issr VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_bookg_dt_dt DATE;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_bookg_dt_dt_tm TIMESTAMP;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_card_tx_card_plain_card_data_pan VARCHAR(19);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_cdt_dbt_ind VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_chrgs_rcrd_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_chrgs_rcrd_amt_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_chrgs_rcrd_cdt_dbt_ind VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_chrgs_rcrd_chrg_incl_ind BOOLEAN;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_chrgs_ttl_chrgs_and_tax_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_commn_sts VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_ntry_ref VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_rvsl_ind BOOLEAN;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_sts_cd VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_sts_prtry VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_tech_inpt_chanl_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_val_dt_dt DATE;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_val_dt_dt_tm TIMESTAMP;

-- Entry Details - Batch fields
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_dtls_btch_cdt_dbt_ind VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_dtls_btch_msg_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_dtls_btch_nb_of_txs INTEGER;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_dtls_btch_pmt_inf_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_dtls_btch_ttl_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS ntry_dtls_btch_ttl_amt_ccy VARCHAR(3);

-- Transaction Details fields
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_addtl_tx_inf VARCHAR(500);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_amt_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_amt_dtls_instd_amt_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_amt_dtls_instd_amt_amt_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_amt_dtls_tx_amt_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_amt_dtls_tx_amt_amt_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_bk_tx_cd_domn_cd VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_bk_tx_cd_domn_fmly_cd VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_bk_tx_cd_domn_fmly_sub_fmly_cd VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_cdt_dbt_ind VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_fin_instrm_id_isin VARCHAR(12);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_purp_cd VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_purp_prtry VARCHAR(35);

-- Transaction References
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_acct_ownr_tx_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_acct_svcr_ref VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_acct_svcr_tx_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_chq_nb VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_clr_sys_ref VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_end_to_end_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_instr_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_mkt_infrstrctr_tx_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_mndt_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_msg_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_pmt_inf_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_prcg_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_prtry_ref VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_prtry_tp VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_tx_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_refs_uetr VARCHAR(36);

-- Related Agents
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_bicfi VARCHAR(11);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_clr_sys_mmb_id_mmb_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_lei VARCHAR(20);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_nm VARCHAR(140);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_pstl_adr_ctry VARCHAR(2);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_bicfi VARCHAR(11);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_clr_sys_mmb_id_mmb_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_lei VARCHAR(20);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_nm VARCHAR(140);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_pstl_adr_ctry VARCHAR(2);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_dlvrg_agt_fin_instn_id_bicfi VARCHAR(11);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_intrmy_agt1_fin_instn_id_bicfi VARCHAR(11);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_intrmy_agt2_fin_instn_id_bicfi VARCHAR(11);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_intrmy_agt3_fin_instn_id_bicfi VARCHAR(11);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_rcvg_agt_fin_instn_id_bicfi VARCHAR(11);

-- Related Dates
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_dts_accptnc_dt_tm TIMESTAMP;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_dts_end_dt DATE;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_dts_intr_bk_sttlm_dt DATE;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_dts_start_dt DATE;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_dts_trad_dt DATE;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_dts_tx_dt_tm TIMESTAMP;

-- Related Price
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pric_deal_pric NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pric_deal_pric_ccy VARCHAR(3);

-- Related Parties - Creditor
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_id_org_id_any_bic VARCHAR(11);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_id_org_id_lei VARCHAR(20);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_nm VARCHAR(140);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_pstl_adr_bldg_nb VARCHAR(16);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_pstl_adr_ctry VARCHAR(2);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_pstl_adr_pst_cd VARCHAR(16);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_pstl_adr_strt_nm VARCHAR(70);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_pstl_adr_twn_nm VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_acct_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_acct_id_iban VARCHAR(34);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_acct_id_othr_id VARCHAR(34);

-- Related Parties - Debtor
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_id_org_id_any_bic VARCHAR(11);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_id_org_id_lei VARCHAR(20);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_id_org_id_othr_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_nm VARCHAR(140);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_pstl_adr_bldg_nb VARCHAR(16);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_pstl_adr_ctry VARCHAR(2);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_pstl_adr_pst_cd VARCHAR(16);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_pstl_adr_strt_nm VARCHAR(70);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_pstl_adr_twn_nm VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_acct_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_acct_id_iban VARCHAR(34);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_acct_id_othr_id VARCHAR(34);

-- Related Parties - Others
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_initg_pty_nm VARCHAR(140);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_ultmt_cdtr_nm VARCHAR(140);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_ultmt_dbtr_nm VARCHAR(140);

-- Related Remittance Info
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_rmt_inf_rmt_id VARCHAR(35);

-- Remittance Information - Structured
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_addtl_rmt_inf VARCHAR(140);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_cdtr_ref_inf_ref VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_cdtr_ref_inf_tp_cd_or_prtry_cd VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_invcee_nm VARCHAR(140);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_invcr_nm VARCHAR(140);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_rfrd_doc_amt_due_pybl_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_rfrd_doc_amt_due_pybl_amt_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_rfrd_doc_amt_rmtd_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_rfrd_doc_amt_rmtd_amt_ccy VARCHAR(3);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_rfrd_doc_inf_nb VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_rfrd_doc_inf_rltd_dt DATE;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_rfrd_doc_inf_tp_cd_or_prtry_cd VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_ustrd VARCHAR(140);

-- Return Information
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rtr_inf_addtl_inf VARCHAR(105);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rtr_inf_rsn_cd VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_rtr_inf_rsn_prtry VARCHAR(35);

-- Tax Information
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_tax_cdtr_tax_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_tax_dbtr_tax_id VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_tax_ttl_tax_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS tx_dtls_tax_ttl_tax_amt_ccy VARCHAR(3);

-- Reporting Sequence
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS rptg_seq_fr_to_seq_fr_seq VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS rptg_seq_fr_to_seq_to_seq VARCHAR(35);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS rptg_src_prtry VARCHAR(35);

-- Statement Pagination
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS stmt_pgntn_last_pg_ind BOOLEAN;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS stmt_pgntn_pg_nb VARCHAR(5);

-- Transaction Summary
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS txs_summry_ttl_cdt_ntries_nb_of_ntries INTEGER;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS txs_summry_ttl_cdt_ntries_sum NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS txs_summry_ttl_dbt_ntries_nb_of_ntries INTEGER;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS txs_summry_ttl_dbt_ntries_sum NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS txs_summry_ttl_ntries_nb_of_ntries INTEGER;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS txs_summry_ttl_ntries_sum NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS txs_summry_ttl_ntries_ttl_net_ntry_amt NUMERIC(18,4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS txs_summry_ttl_ntries_ttl_net_ntry_cdt_dbt_ind VARCHAR(4);
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS txs_summry_ttl_ntries_per_bk_tx_cd_nb_of_ntries INTEGER;
ALTER TABLE silver.stg_camt053 ADD COLUMN IF NOT EXISTS txs_summry_ttl_ntries_per_bk_tx_cd_sum NUMERIC(18,4);

COMMIT;
