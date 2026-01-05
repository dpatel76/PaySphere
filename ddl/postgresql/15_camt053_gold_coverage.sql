-- =============================================================================
-- Fix camt.053 Silver->Gold Coverage to 100%
-- =============================================================================
-- This script extends cdm_payment_extension_iso20022 to handle camt.053 statement
-- data and creates gold_field_mappings for ALL 218 silver columns.
--
-- camt.053 is a Bank to Customer Statement message - NOT a payment instruction.
-- Most data goes to cdm_payment_extension_iso20022 extension table.
-- =============================================================================

BEGIN;

-- =============================================================================
-- PART 1: Extend cdm_payment_extension_iso20022 for camt.053
-- =============================================================================

-- Group Header fields
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS grp_hdr_addtl_inf VARCHAR(2000);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS grp_hdr_msg_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS grp_hdr_cre_dt_tm TIMESTAMP;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS grp_hdr_msg_pgntn_last_pg_ind BOOLEAN;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS grp_hdr_msg_pgntn_pg_nb VARCHAR(5);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS grp_hdr_msg_rcpt_id_org_id_any_bic VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS grp_hdr_msg_rcpt_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS grp_hdr_orgnl_biz_qry_msg_id VARCHAR(35);

-- Statement fields
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS stmt_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS stmt_cre_dt_tm TIMESTAMP;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS elctrnc_seq_nb INTEGER;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS lgl_seq_nb INTEGER;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS fr_to_dt_fr_dt_tm TIMESTAMP;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS fr_to_dt_to_dt_tm TIMESTAMP;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS cpy_dplct_ind VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS rptg_src_prtry VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS rptg_seq_fr_to_seq_fr_seq VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS rptg_seq_fr_to_seq_to_seq VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS stmt_pgntn_last_pg_ind BOOLEAN;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS stmt_pgntn_pg_nb VARCHAR(5);

-- Account fields
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_id_iban VARCHAR(34);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_id_othr_id VARCHAR(34);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_id_othr_schme_nm_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_id_othr_schme_nm_prtry VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_tp_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_tp_prtry VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_nm VARCHAR(70);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_prxy_id VARCHAR(2048);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_ownr_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_ownr_id_org_id_any_bic VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_ownr_id_org_id_lei VARCHAR(20);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_ownr_id_org_id_othr_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_ownr_pstl_adr_strt_nm VARCHAR(70);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_ownr_pstl_adr_bldg_nb VARCHAR(16);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_ownr_pstl_adr_pst_cd VARCHAR(16);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_ownr_pstl_adr_twn_nm VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_ownr_pstl_adr_ctry VARCHAR(2);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_svcr_fin_instn_id_bicfi VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_svcr_fin_instn_id_clr_sys_mmb_id_mmb_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_svcr_fin_instn_id_lei VARCHAR(20);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_svcr_fin_instn_id_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS acct_svcr_fin_instn_id_pstl_adr_ctry VARCHAR(2);

-- Balance fields (generic - first balance)
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_tp_cd_or_prtry_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_tp_cd_or_prtry_prtry VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_tp_sub_tp_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_tp_sub_tp_prtry VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_amt_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_cdt_dbt_ind VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_dt_dt DATE;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_dt_dt_tm TIMESTAMP;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_avlbty_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_avlbty_amt_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_avlbty_cdt_dbt_ind VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_avlbty_dt_actl_dt DATE;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_avlbty_dt_nb_of_days VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_cdt_line_incl BOOLEAN;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_cdt_line_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS bal_cdt_line_amt_ccy VARCHAR(3);

-- Transaction Summary fields
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS txs_summry_ttl_ntries_nb_of_ntries INTEGER;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS txs_summry_ttl_ntries_sum NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS txs_summry_ttl_ntries_ttl_net_ntry_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS txs_summry_ttl_ntries_ttl_net_ntry_cdt_dbt_ind VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS txs_summry_ttl_cdt_ntries_nb_of_ntries INTEGER;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS txs_summry_ttl_cdt_ntries_sum NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS txs_summry_ttl_dbt_ntries_nb_of_ntries INTEGER;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS txs_summry_ttl_dbt_ntries_sum NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS txs_summry_ttl_ntries_per_bk_tx_cd_nb_of_ntries INTEGER;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS txs_summry_ttl_ntries_per_bk_tx_cd_sum NUMERIC(18,4);

-- Entry fields (first entry)
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_ntry_ref VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_amt_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_cdt_dbt_ind VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_rvsl_ind BOOLEAN;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_sts_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_sts_prtry VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_bookg_dt_dt DATE;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_bookg_dt_dt_tm TIMESTAMP;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_val_dt_dt DATE;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_val_dt_dt_tm TIMESTAMP;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_acct_svcr_ref VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_avlbty_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_avlbty_cdt_dbt_ind VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_bk_tx_cd_domn_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_bk_tx_cd_domn_fmly_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_bk_tx_cd_domn_fmly_sub_fmly_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_bk_tx_cd_prtry_cd VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_bk_tx_cd_prtry_issr VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_commn_sts VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_addtl_inf_ind_msg_nm_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_addtl_ntry_inf VARCHAR(500);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_tech_inpt_chanl_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_card_tx_card_plain_card_data_pan VARCHAR(19);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_chrgs_ttl_chrgs_and_tax_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_chrgs_rcrd_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_chrgs_rcrd_amt_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_chrgs_rcrd_cdt_dbt_ind VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_chrgs_rcrd_chrg_incl_ind BOOLEAN;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_amt_dtls_instd_amt_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_amt_dtls_instd_amt_amt_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_amt_dtls_tx_amt_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_amt_dtls_tx_amt_amt_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_amt_dtls_cntr_val_amt_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_amt_dtls_cntr_val_amt_amt_ccy VARCHAR(3);

-- Entry Details Batch fields
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_dtls_btch_msg_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_dtls_btch_pmt_inf_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_dtls_btch_nb_of_txs INTEGER;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_dtls_btch_ttl_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_dtls_btch_ttl_amt_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS ntry_dtls_btch_cdt_dbt_ind VARCHAR(4);

-- Transaction Details fields
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_amt_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_cdt_dbt_ind VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_amt_dtls_instd_amt_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_amt_dtls_instd_amt_amt_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_amt_dtls_tx_amt_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_amt_dtls_tx_amt_amt_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_bk_tx_cd_domn_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_bk_tx_cd_domn_fmly_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_bk_tx_cd_domn_fmly_sub_fmly_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_purp_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_purp_prtry VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_fin_instrm_id_isin VARCHAR(12);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_addtl_tx_inf VARCHAR(500);

-- Transaction References
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_msg_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_acct_svcr_ref VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_pmt_inf_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_instr_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_end_to_end_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_tx_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_mndt_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_chq_nb VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_clr_sys_ref VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_acct_ownr_tx_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_acct_svcr_tx_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_mkt_infrstrctr_tx_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_prcg_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_uetr VARCHAR(36);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_prtry_ref VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_refs_prtry_tp VARCHAR(35);

-- Related Dates
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_dts_accptnc_dt_tm TIMESTAMP;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_dts_trad_dt DATE;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_dts_intr_bk_sttlm_dt DATE;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_dts_start_dt DATE;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_dts_end_dt DATE;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_dts_tx_dt_tm TIMESTAMP;

-- Related Price
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pric_deal_pric NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pric_deal_pric_ccy VARCHAR(3);

-- Related Parties (stored as reference since actual entities go to cdm_party)
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_id_org_id_any_bic VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_id_org_id_lei VARCHAR(20);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_id_org_id_othr_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_pstl_adr_strt_nm VARCHAR(70);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_pstl_adr_bldg_nb VARCHAR(16);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_pstl_adr_pst_cd VARCHAR(16);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_pstl_adr_twn_nm VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_pstl_adr_ctry VARCHAR(2);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_acct_id_iban VARCHAR(34);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_acct_id_othr_id VARCHAR(34);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_dbtr_acct_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_id_org_id_any_bic VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_id_org_id_lei VARCHAR(20);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_pstl_adr_strt_nm VARCHAR(70);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_pstl_adr_bldg_nb VARCHAR(16);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_pstl_adr_pst_cd VARCHAR(16);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_pstl_adr_twn_nm VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_pstl_adr_ctry VARCHAR(2);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_acct_id_iban VARCHAR(34);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_acct_id_othr_id VARCHAR(34);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_cdtr_acct_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_ultmt_dbtr_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_ultmt_cdtr_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_pties_initg_pty_nm VARCHAR(140);

-- Related Agents (stored as reference)
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_bicfi VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_clr_sys_mmb_id_mmb_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_lei VARCHAR(20);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_pstl_adr_ctry VARCHAR(2);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_bicfi VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_clr_sys_mmb_id_mmb_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_lei VARCHAR(20);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_pstl_adr_ctry VARCHAR(2);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_intrmy_agt1_fin_instn_id_bicfi VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_intrmy_agt2_fin_instn_id_bicfi VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_intrmy_agt3_fin_instn_id_bicfi VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_dlvrg_agt_fin_instn_id_bicfi VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_agts_rcvg_agt_fin_instn_id_bicfi VARCHAR(11);

-- Related Remittance Info
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rltd_rmt_inf_rmt_id VARCHAR(35);

-- Remittance Information - Structured
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_ustrd VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_cdtr_ref_inf_tp_cd_or_prtry_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_cdtr_ref_inf_ref VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_invcr_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_invcee_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_rfrd_doc_inf_tp_cd_or_prtry_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_rfrd_doc_inf_nb VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_rfrd_doc_inf_rltd_dt DATE;
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_rfrd_doc_amt_due_pybl_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_rfrd_doc_amt_due_pybl_amt_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_rfrd_doc_amt_rmtd_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_rfrd_doc_amt_rmtd_amt_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rmt_inf_strd_addtl_rmt_inf VARCHAR(140);

-- Return Information
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rtr_inf_rsn_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rtr_inf_rsn_prtry VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_rtr_inf_addtl_inf VARCHAR(105);

-- Tax Information
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_tax_cdtr_tax_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_tax_dbtr_tax_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_tax_ttl_tax_amt NUMERIC(18,4);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS tx_dtls_tax_ttl_tax_amt_ccy VARCHAR(3);

-- Source tracking
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS source_stg_id VARCHAR(36);
ALTER TABLE gold.cdm_payment_extension_iso20022 ADD COLUMN IF NOT EXISTS source_batch_id VARCHAR(36);

COMMIT;

-- =============================================================================
-- PART 2: Clear and insert fresh Gold Field Mappings for camt.053
-- =============================================================================

BEGIN;

-- First delete existing camt.053 gold mappings to start fresh
DELETE FROM mapping.gold_field_mappings WHERE format_id = 'camt.053';

-- =============================================================================
-- cdm_payment_extension_iso20022 mappings (statement-specific data)
-- All camt.053 Silver columns map to the extension table
-- =============================================================================
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal_position, is_active)
VALUES
    -- Core identifiers
    ('camt.053', 'cdm_payment_extension_iso20022', 'extension_id', '_GENERATED_UUID', NULL, 'VARCHAR', 1, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'instruction_id', '_CONTEXT.instruction_id', NULL, 'VARCHAR', 2, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'message_definition', '''camt.053''', NULL, 'VARCHAR', 3, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'message_namespace', '''urn:iso:std:iso:20022:tech:xsd:camt.053.001.08''', NULL, 'VARCHAR', 4, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'source_stg_id', 'stg_id', NULL, 'VARCHAR', 5, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'source_batch_id', '_batch_id', NULL, 'VARCHAR', 6, true),

    -- Group Header
    ('camt.053', 'cdm_payment_extension_iso20022', 'grp_hdr_msg_id', 'grp_hdr_msg_id', NULL, 'VARCHAR', 10, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'grp_hdr_cre_dt_tm', 'grp_hdr_cre_dt_tm', NULL, 'TIMESTAMP', 11, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'grp_hdr_addtl_inf', 'grp_hdr_addtl_inf', NULL, 'VARCHAR', 12, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'grp_hdr_msg_pgntn_last_pg_ind', 'grp_hdr_msg_pgntn_last_pg_ind', NULL, 'BOOLEAN', 13, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'grp_hdr_msg_pgntn_pg_nb', 'grp_hdr_msg_pgntn_pg_nb', NULL, 'VARCHAR', 14, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'grp_hdr_msg_rcpt_id_org_id_any_bic', 'grp_hdr_msg_rcpt_id_org_id_any_bic', NULL, 'VARCHAR', 15, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'grp_hdr_msg_rcpt_nm', 'grp_hdr_msg_rcpt_nm', NULL, 'VARCHAR', 16, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'grp_hdr_orgnl_biz_qry_msg_id', 'grp_hdr_orgnl_biz_qry_msg_id', NULL, 'VARCHAR', 17, true),

    -- Statement
    ('camt.053', 'cdm_payment_extension_iso20022', 'stmt_id', 'stmt_id', NULL, 'VARCHAR', 20, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'stmt_cre_dt_tm', 'stmt_cre_dt_tm', NULL, 'TIMESTAMP', 21, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'elctrnc_seq_nb', 'elctrnc_seq_nb', NULL, 'INTEGER', 22, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'lgl_seq_nb', 'lgl_seq_nb', NULL, 'INTEGER', 23, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'fr_to_dt_fr_dt_tm', 'fr_to_dt_fr_dt_tm', NULL, 'TIMESTAMP', 24, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'fr_to_dt_to_dt_tm', 'fr_to_dt_to_dt_tm', NULL, 'TIMESTAMP', 25, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'cpy_dplct_ind', 'cpy_dplct_ind', NULL, 'VARCHAR', 26, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'rptg_src_prtry', 'rptg_src_prtry', NULL, 'VARCHAR', 27, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'rptg_seq_fr_to_seq_fr_seq', 'rptg_seq_fr_to_seq_fr_seq', NULL, 'VARCHAR', 28, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'rptg_seq_fr_to_seq_to_seq', 'rptg_seq_fr_to_seq_to_seq', NULL, 'VARCHAR', 29, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'stmt_pgntn_last_pg_ind', 'stmt_pgntn_last_pg_ind', NULL, 'BOOLEAN', 30, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'stmt_pgntn_pg_nb', 'stmt_pgntn_pg_nb', NULL, 'VARCHAR', 31, true),

    -- Account
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_id_iban', 'acct_id_iban', NULL, 'VARCHAR', 40, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_id_othr_id', 'acct_id_othr_id', NULL, 'VARCHAR', 41, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_id_othr_schme_nm_cd', 'acct_id_othr_schme_nm_cd', NULL, 'VARCHAR', 42, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_id_othr_schme_nm_prtry', 'acct_id_othr_schme_nm_prtry', NULL, 'VARCHAR', 43, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_tp_cd', 'acct_tp_cd', NULL, 'VARCHAR', 44, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_tp_prtry', 'acct_tp_prtry', NULL, 'VARCHAR', 45, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_ccy', 'acct_ccy', NULL, 'VARCHAR', 46, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_nm', 'acct_nm', NULL, 'VARCHAR', 47, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_prxy_id', 'acct_prxy_id', NULL, 'VARCHAR', 48, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_ownr_nm', 'acct_ownr_nm', NULL, 'VARCHAR', 49, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_ownr_id_org_id_any_bic', 'acct_ownr_id_org_id_any_bic', NULL, 'VARCHAR', 50, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_ownr_id_org_id_lei', 'acct_ownr_id_org_id_lei', NULL, 'VARCHAR', 51, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_ownr_id_org_id_othr_id', 'acct_ownr_id_org_id_othr_id', NULL, 'VARCHAR', 52, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_ownr_pstl_adr_strt_nm', 'acct_ownr_pstl_adr_strt_nm', NULL, 'VARCHAR', 53, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_ownr_pstl_adr_bldg_nb', 'acct_ownr_pstl_adr_bldg_nb', NULL, 'VARCHAR', 54, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_ownr_pstl_adr_pst_cd', 'acct_ownr_pstl_adr_pst_cd', NULL, 'VARCHAR', 55, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_ownr_pstl_adr_twn_nm', 'acct_ownr_pstl_adr_twn_nm', NULL, 'VARCHAR', 56, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_ownr_pstl_adr_ctry', 'acct_ownr_pstl_adr_ctry', NULL, 'VARCHAR', 57, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_svcr_fin_instn_id_bicfi', 'acct_svcr_fin_instn_id_bicfi', NULL, 'VARCHAR', 58, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_svcr_fin_instn_id_clr_sys_mmb_id_mmb_id', 'acct_svcr_fin_instn_id_clr_sys_mmb_id_mmb_id', NULL, 'VARCHAR', 59, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_svcr_fin_instn_id_lei', 'acct_svcr_fin_instn_id_lei', NULL, 'VARCHAR', 60, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_svcr_fin_instn_id_nm', 'acct_svcr_fin_instn_id_nm', NULL, 'VARCHAR', 61, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'acct_svcr_fin_instn_id_pstl_adr_ctry', 'acct_svcr_fin_instn_id_pstl_adr_ctry', NULL, 'VARCHAR', 62, true),

    -- Balance
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_tp_cd_or_prtry_cd', 'bal_tp_cd_or_prtry_cd', NULL, 'VARCHAR', 70, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_tp_cd_or_prtry_prtry', 'bal_tp_cd_or_prtry_prtry', NULL, 'VARCHAR', 71, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_tp_sub_tp_cd', 'bal_tp_sub_tp_cd', NULL, 'VARCHAR', 72, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_tp_sub_tp_prtry', 'bal_tp_sub_tp_prtry', NULL, 'VARCHAR', 73, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_amt', 'bal_amt', NULL, 'DECIMAL', 74, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_amt_ccy', 'bal_amt_ccy', NULL, 'VARCHAR', 75, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_cdt_dbt_ind', 'bal_cdt_dbt_ind', NULL, 'VARCHAR', 76, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_dt_dt', 'bal_dt_dt', NULL, 'DATE', 77, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_dt_dt_tm', 'bal_dt_dt_tm', NULL, 'TIMESTAMP', 78, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_avlbty_amt', 'bal_avlbty_amt', NULL, 'DECIMAL', 79, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_avlbty_amt_ccy', 'bal_avlbty_amt_ccy', NULL, 'VARCHAR', 80, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_avlbty_cdt_dbt_ind', 'bal_avlbty_cdt_dbt_ind', NULL, 'VARCHAR', 81, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_avlbty_dt_actl_dt', 'bal_avlbty_dt_actl_dt', NULL, 'DATE', 82, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_avlbty_dt_nb_of_days', 'bal_avlbty_dt_nb_of_days', NULL, 'VARCHAR', 83, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_cdt_line_incl', 'bal_cdt_line_incl', NULL, 'BOOLEAN', 84, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_cdt_line_amt', 'bal_cdt_line_amt', NULL, 'DECIMAL', 85, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'bal_cdt_line_amt_ccy', 'bal_cdt_line_amt_ccy', NULL, 'VARCHAR', 86, true),

    -- Transaction Summary
    ('camt.053', 'cdm_payment_extension_iso20022', 'txs_summry_ttl_ntries_nb_of_ntries', 'txs_summry_ttl_ntries_nb_of_ntries', NULL, 'INTEGER', 90, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'txs_summry_ttl_ntries_sum', 'txs_summry_ttl_ntries_sum', NULL, 'DECIMAL', 91, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'txs_summry_ttl_ntries_ttl_net_ntry_amt', 'txs_summry_ttl_ntries_ttl_net_ntry_amt', NULL, 'DECIMAL', 92, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'txs_summry_ttl_ntries_ttl_net_ntry_cdt_dbt_ind', 'txs_summry_ttl_ntries_ttl_net_ntry_cdt_dbt_ind', NULL, 'VARCHAR', 93, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'txs_summry_ttl_cdt_ntries_nb_of_ntries', 'txs_summry_ttl_cdt_ntries_nb_of_ntries', NULL, 'INTEGER', 94, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'txs_summry_ttl_cdt_ntries_sum', 'txs_summry_ttl_cdt_ntries_sum', NULL, 'DECIMAL', 95, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'txs_summry_ttl_dbt_ntries_nb_of_ntries', 'txs_summry_ttl_dbt_ntries_nb_of_ntries', NULL, 'INTEGER', 96, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'txs_summry_ttl_dbt_ntries_sum', 'txs_summry_ttl_dbt_ntries_sum', NULL, 'DECIMAL', 97, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'txs_summry_ttl_ntries_per_bk_tx_cd_nb_of_ntries', 'txs_summry_ttl_ntries_per_bk_tx_cd_nb_of_ntries', NULL, 'INTEGER', 98, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'txs_summry_ttl_ntries_per_bk_tx_cd_sum', 'txs_summry_ttl_ntries_per_bk_tx_cd_sum', NULL, 'DECIMAL', 99, true),

    -- Entry fields
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_ntry_ref', 'ntry_ntry_ref', NULL, 'VARCHAR', 100, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_amt', 'ntry_amt', NULL, 'DECIMAL', 101, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_amt_ccy', 'ntry_amt_ccy', NULL, 'VARCHAR', 102, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_cdt_dbt_ind', 'ntry_cdt_dbt_ind', NULL, 'VARCHAR', 103, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_rvsl_ind', 'ntry_rvsl_ind', NULL, 'BOOLEAN', 104, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_sts_cd', 'ntry_sts_cd', NULL, 'VARCHAR', 105, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_sts_prtry', 'ntry_sts_prtry', NULL, 'VARCHAR', 106, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_bookg_dt_dt', 'ntry_bookg_dt_dt', NULL, 'DATE', 107, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_bookg_dt_dt_tm', 'ntry_bookg_dt_dt_tm', NULL, 'TIMESTAMP', 108, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_val_dt_dt', 'ntry_val_dt_dt', NULL, 'DATE', 109, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_val_dt_dt_tm', 'ntry_val_dt_dt_tm', NULL, 'TIMESTAMP', 110, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_acct_svcr_ref', 'ntry_acct_svcr_ref', NULL, 'VARCHAR', 111, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_avlbty_amt', 'ntry_avlbty_amt', NULL, 'DECIMAL', 112, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_avlbty_cdt_dbt_ind', 'ntry_avlbty_cdt_dbt_ind', NULL, 'VARCHAR', 113, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_bk_tx_cd_domn_cd', 'ntry_bk_tx_cd_domn_cd', NULL, 'VARCHAR', 114, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_bk_tx_cd_domn_fmly_cd', 'ntry_bk_tx_cd_domn_fmly_cd', NULL, 'VARCHAR', 115, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_bk_tx_cd_domn_fmly_sub_fmly_cd', 'ntry_bk_tx_cd_domn_fmly_sub_fmly_cd', NULL, 'VARCHAR', 116, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_bk_tx_cd_prtry_cd', 'ntry_bk_tx_cd_prtry_cd', NULL, 'VARCHAR', 117, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_bk_tx_cd_prtry_issr', 'ntry_bk_tx_cd_prtry_issr', NULL, 'VARCHAR', 118, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_commn_sts', 'ntry_commn_sts', NULL, 'VARCHAR', 119, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_addtl_inf_ind_msg_nm_id', 'ntry_addtl_inf_ind_msg_nm_id', NULL, 'VARCHAR', 120, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_addtl_ntry_inf', 'ntry_addtl_ntry_inf', NULL, 'VARCHAR', 121, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_tech_inpt_chanl_id', 'ntry_tech_inpt_chanl_id', NULL, 'VARCHAR', 122, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_card_tx_card_plain_card_data_pan', 'ntry_card_tx_card_plain_card_data_pan', NULL, 'VARCHAR', 123, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_chrgs_ttl_chrgs_and_tax_amt', 'ntry_chrgs_ttl_chrgs_and_tax_amt', NULL, 'DECIMAL', 124, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_chrgs_rcrd_amt', 'ntry_chrgs_rcrd_amt', NULL, 'DECIMAL', 125, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_chrgs_rcrd_amt_ccy', 'ntry_chrgs_rcrd_amt_ccy', NULL, 'VARCHAR', 126, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_chrgs_rcrd_cdt_dbt_ind', 'ntry_chrgs_rcrd_cdt_dbt_ind', NULL, 'VARCHAR', 127, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_chrgs_rcrd_chrg_incl_ind', 'ntry_chrgs_rcrd_chrg_incl_ind', NULL, 'BOOLEAN', 128, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_amt_dtls_instd_amt_amt', 'ntry_amt_dtls_instd_amt_amt', NULL, 'DECIMAL', 129, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_amt_dtls_instd_amt_amt_ccy', 'ntry_amt_dtls_instd_amt_amt_ccy', NULL, 'VARCHAR', 130, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_amt_dtls_tx_amt_amt', 'ntry_amt_dtls_tx_amt_amt', NULL, 'DECIMAL', 131, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_amt_dtls_tx_amt_amt_ccy', 'ntry_amt_dtls_tx_amt_amt_ccy', NULL, 'VARCHAR', 132, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_amt_dtls_cntr_val_amt_amt', 'ntry_amt_dtls_cntr_val_amt_amt', NULL, 'DECIMAL', 133, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_amt_dtls_cntr_val_amt_amt_ccy', 'ntry_amt_dtls_cntr_val_amt_amt_ccy', NULL, 'VARCHAR', 134, true),

    -- Entry Details Batch
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_dtls_btch_msg_id', 'ntry_dtls_btch_msg_id', NULL, 'VARCHAR', 140, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_dtls_btch_pmt_inf_id', 'ntry_dtls_btch_pmt_inf_id', NULL, 'VARCHAR', 141, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_dtls_btch_nb_of_txs', 'ntry_dtls_btch_nb_of_txs', NULL, 'INTEGER', 142, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_dtls_btch_ttl_amt', 'ntry_dtls_btch_ttl_amt', NULL, 'DECIMAL', 143, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_dtls_btch_ttl_amt_ccy', 'ntry_dtls_btch_ttl_amt_ccy', NULL, 'VARCHAR', 144, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'ntry_dtls_btch_cdt_dbt_ind', 'ntry_dtls_btch_cdt_dbt_ind', NULL, 'VARCHAR', 145, true),

    -- Transaction Details
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_amt', 'tx_dtls_amt', NULL, 'DECIMAL', 150, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_amt_ccy', 'tx_dtls_amt_ccy', NULL, 'VARCHAR', 151, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_cdt_dbt_ind', 'tx_dtls_cdt_dbt_ind', NULL, 'VARCHAR', 152, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_amt_dtls_instd_amt_amt', 'tx_dtls_amt_dtls_instd_amt_amt', NULL, 'DECIMAL', 153, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_amt_dtls_instd_amt_amt_ccy', 'tx_dtls_amt_dtls_instd_amt_amt_ccy', NULL, 'VARCHAR', 154, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_amt_dtls_tx_amt_amt', 'tx_dtls_amt_dtls_tx_amt_amt', NULL, 'DECIMAL', 155, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_amt_dtls_tx_amt_amt_ccy', 'tx_dtls_amt_dtls_tx_amt_amt_ccy', NULL, 'VARCHAR', 156, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_bk_tx_cd_domn_cd', 'tx_dtls_bk_tx_cd_domn_cd', NULL, 'VARCHAR', 157, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_bk_tx_cd_domn_fmly_cd', 'tx_dtls_bk_tx_cd_domn_fmly_cd', NULL, 'VARCHAR', 158, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_bk_tx_cd_domn_fmly_sub_fmly_cd', 'tx_dtls_bk_tx_cd_domn_fmly_sub_fmly_cd', NULL, 'VARCHAR', 159, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_purp_cd', 'tx_dtls_purp_cd', NULL, 'VARCHAR', 160, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_purp_prtry', 'tx_dtls_purp_prtry', NULL, 'VARCHAR', 161, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_fin_instrm_id_isin', 'tx_dtls_fin_instrm_id_isin', NULL, 'VARCHAR', 162, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_addtl_tx_inf', 'tx_dtls_addtl_tx_inf', NULL, 'VARCHAR', 163, true),

    -- Transaction References
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_msg_id', 'tx_dtls_refs_msg_id', NULL, 'VARCHAR', 170, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_acct_svcr_ref', 'tx_dtls_refs_acct_svcr_ref', NULL, 'VARCHAR', 171, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_pmt_inf_id', 'tx_dtls_refs_pmt_inf_id', NULL, 'VARCHAR', 172, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_instr_id', 'tx_dtls_refs_instr_id', NULL, 'VARCHAR', 173, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_end_to_end_id', 'tx_dtls_refs_end_to_end_id', NULL, 'VARCHAR', 174, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_tx_id', 'tx_dtls_refs_tx_id', NULL, 'VARCHAR', 175, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_mndt_id', 'tx_dtls_refs_mndt_id', NULL, 'VARCHAR', 176, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_chq_nb', 'tx_dtls_refs_chq_nb', NULL, 'VARCHAR', 177, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_clr_sys_ref', 'tx_dtls_refs_clr_sys_ref', NULL, 'VARCHAR', 178, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_acct_ownr_tx_id', 'tx_dtls_refs_acct_ownr_tx_id', NULL, 'VARCHAR', 179, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_acct_svcr_tx_id', 'tx_dtls_refs_acct_svcr_tx_id', NULL, 'VARCHAR', 180, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_mkt_infrstrctr_tx_id', 'tx_dtls_refs_mkt_infrstrctr_tx_id', NULL, 'VARCHAR', 181, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_prcg_id', 'tx_dtls_refs_prcg_id', NULL, 'VARCHAR', 182, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_uetr', 'tx_dtls_refs_uetr', NULL, 'VARCHAR', 183, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_prtry_ref', 'tx_dtls_refs_prtry_ref', NULL, 'VARCHAR', 184, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_refs_prtry_tp', 'tx_dtls_refs_prtry_tp', NULL, 'VARCHAR', 185, true),

    -- Related Dates
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_dts_accptnc_dt_tm', 'tx_dtls_rltd_dts_accptnc_dt_tm', NULL, 'TIMESTAMP', 190, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_dts_trad_dt', 'tx_dtls_rltd_dts_trad_dt', NULL, 'DATE', 191, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_dts_intr_bk_sttlm_dt', 'tx_dtls_rltd_dts_intr_bk_sttlm_dt', NULL, 'DATE', 192, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_dts_start_dt', 'tx_dtls_rltd_dts_start_dt', NULL, 'DATE', 193, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_dts_end_dt', 'tx_dtls_rltd_dts_end_dt', NULL, 'DATE', 194, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_dts_tx_dt_tm', 'tx_dtls_rltd_dts_tx_dt_tm', NULL, 'TIMESTAMP', 195, true),

    -- Related Price
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pric_deal_pric', 'tx_dtls_rltd_pric_deal_pric', NULL, 'DECIMAL', 196, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pric_deal_pric_ccy', 'tx_dtls_rltd_pric_deal_pric_ccy', NULL, 'VARCHAR', 197, true),

    -- Related Parties (denormalized copies)
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_dbtr_nm', 'tx_dtls_rltd_pties_dbtr_nm', NULL, 'VARCHAR', 200, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_dbtr_id_org_id_any_bic', 'tx_dtls_rltd_pties_dbtr_id_org_id_any_bic', NULL, 'VARCHAR', 201, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_dbtr_id_org_id_lei', 'tx_dtls_rltd_pties_dbtr_id_org_id_lei', NULL, 'VARCHAR', 202, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_dbtr_id_org_id_othr_id', 'tx_dtls_rltd_pties_dbtr_id_org_id_othr_id', NULL, 'VARCHAR', 203, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_dbtr_pstl_adr_strt_nm', 'tx_dtls_rltd_pties_dbtr_pstl_adr_strt_nm', NULL, 'VARCHAR', 204, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_dbtr_pstl_adr_bldg_nb', 'tx_dtls_rltd_pties_dbtr_pstl_adr_bldg_nb', NULL, 'VARCHAR', 205, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_dbtr_pstl_adr_pst_cd', 'tx_dtls_rltd_pties_dbtr_pstl_adr_pst_cd', NULL, 'VARCHAR', 206, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_dbtr_pstl_adr_twn_nm', 'tx_dtls_rltd_pties_dbtr_pstl_adr_twn_nm', NULL, 'VARCHAR', 207, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_dbtr_pstl_adr_ctry', 'tx_dtls_rltd_pties_dbtr_pstl_adr_ctry', NULL, 'VARCHAR', 208, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_dbtr_acct_id_iban', 'tx_dtls_rltd_pties_dbtr_acct_id_iban', NULL, 'VARCHAR', 209, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_dbtr_acct_id_othr_id', 'tx_dtls_rltd_pties_dbtr_acct_id_othr_id', NULL, 'VARCHAR', 210, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_dbtr_acct_ccy', 'tx_dtls_rltd_pties_dbtr_acct_ccy', NULL, 'VARCHAR', 211, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_cdtr_nm', 'tx_dtls_rltd_pties_cdtr_nm', NULL, 'VARCHAR', 212, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_cdtr_id_org_id_any_bic', 'tx_dtls_rltd_pties_cdtr_id_org_id_any_bic', NULL, 'VARCHAR', 213, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_cdtr_id_org_id_lei', 'tx_dtls_rltd_pties_cdtr_id_org_id_lei', NULL, 'VARCHAR', 214, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_cdtr_pstl_adr_strt_nm', 'tx_dtls_rltd_pties_cdtr_pstl_adr_strt_nm', NULL, 'VARCHAR', 215, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_cdtr_pstl_adr_bldg_nb', 'tx_dtls_rltd_pties_cdtr_pstl_adr_bldg_nb', NULL, 'VARCHAR', 216, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_cdtr_pstl_adr_pst_cd', 'tx_dtls_rltd_pties_cdtr_pstl_adr_pst_cd', NULL, 'VARCHAR', 217, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_cdtr_pstl_adr_twn_nm', 'tx_dtls_rltd_pties_cdtr_pstl_adr_twn_nm', NULL, 'VARCHAR', 218, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_cdtr_pstl_adr_ctry', 'tx_dtls_rltd_pties_cdtr_pstl_adr_ctry', NULL, 'VARCHAR', 219, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_cdtr_acct_id_iban', 'tx_dtls_rltd_pties_cdtr_acct_id_iban', NULL, 'VARCHAR', 220, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_cdtr_acct_id_othr_id', 'tx_dtls_rltd_pties_cdtr_acct_id_othr_id', NULL, 'VARCHAR', 221, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_cdtr_acct_ccy', 'tx_dtls_rltd_pties_cdtr_acct_ccy', NULL, 'VARCHAR', 222, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_ultmt_dbtr_nm', 'tx_dtls_rltd_pties_ultmt_dbtr_nm', NULL, 'VARCHAR', 223, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_ultmt_cdtr_nm', 'tx_dtls_rltd_pties_ultmt_cdtr_nm', NULL, 'VARCHAR', 224, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_pties_initg_pty_nm', 'tx_dtls_rltd_pties_initg_pty_nm', NULL, 'VARCHAR', 225, true),

    -- Related Agents (denormalized copies)
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_bicfi', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_bicfi', NULL, 'VARCHAR', 230, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_clr_sys_mmb_id_mmb_id', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_clr_sys_mmb_id_mmb_id', NULL, 'VARCHAR', 231, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_lei', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_lei', NULL, 'VARCHAR', 232, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_nm', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_nm', NULL, 'VARCHAR', 233, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_pstl_adr_ctry', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_pstl_adr_ctry', NULL, 'VARCHAR', 234, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_bicfi', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_bicfi', NULL, 'VARCHAR', 235, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_clr_sys_mmb_id_mmb_id', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_clr_sys_mmb_id_mmb_id', NULL, 'VARCHAR', 236, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_lei', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_lei', NULL, 'VARCHAR', 237, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_nm', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_nm', NULL, 'VARCHAR', 238, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_pstl_adr_ctry', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_pstl_adr_ctry', NULL, 'VARCHAR', 239, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_agts_intrmy_agt1_fin_instn_id_bicfi', 'tx_dtls_rltd_agts_intrmy_agt1_fin_instn_id_bicfi', NULL, 'VARCHAR', 240, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_agts_intrmy_agt2_fin_instn_id_bicfi', 'tx_dtls_rltd_agts_intrmy_agt2_fin_instn_id_bicfi', NULL, 'VARCHAR', 241, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_agts_intrmy_agt3_fin_instn_id_bicfi', 'tx_dtls_rltd_agts_intrmy_agt3_fin_instn_id_bicfi', NULL, 'VARCHAR', 242, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_agts_dlvrg_agt_fin_instn_id_bicfi', 'tx_dtls_rltd_agts_dlvrg_agt_fin_instn_id_bicfi', NULL, 'VARCHAR', 243, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_agts_rcvg_agt_fin_instn_id_bicfi', 'tx_dtls_rltd_agts_rcvg_agt_fin_instn_id_bicfi', NULL, 'VARCHAR', 244, true),

    -- Remittance Info
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rltd_rmt_inf_rmt_id', 'tx_dtls_rltd_rmt_inf_rmt_id', NULL, 'VARCHAR', 250, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rmt_inf_ustrd', 'tx_dtls_rmt_inf_ustrd', NULL, 'VARCHAR', 251, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rmt_inf_strd_cdtr_ref_inf_tp_cd_or_prtry_cd', 'tx_dtls_rmt_inf_strd_cdtr_ref_inf_tp_cd_or_prtry_cd', NULL, 'VARCHAR', 252, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rmt_inf_strd_cdtr_ref_inf_ref', 'tx_dtls_rmt_inf_strd_cdtr_ref_inf_ref', NULL, 'VARCHAR', 253, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rmt_inf_strd_invcr_nm', 'tx_dtls_rmt_inf_strd_invcr_nm', NULL, 'VARCHAR', 254, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rmt_inf_strd_invcee_nm', 'tx_dtls_rmt_inf_strd_invcee_nm', NULL, 'VARCHAR', 255, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rmt_inf_strd_rfrd_doc_inf_tp_cd_or_prtry_cd', 'tx_dtls_rmt_inf_strd_rfrd_doc_inf_tp_cd_or_prtry_cd', NULL, 'VARCHAR', 256, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rmt_inf_strd_rfrd_doc_inf_nb', 'tx_dtls_rmt_inf_strd_rfrd_doc_inf_nb', NULL, 'VARCHAR', 257, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rmt_inf_strd_rfrd_doc_inf_rltd_dt', 'tx_dtls_rmt_inf_strd_rfrd_doc_inf_rltd_dt', NULL, 'DATE', 258, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rmt_inf_strd_rfrd_doc_amt_due_pybl_amt', 'tx_dtls_rmt_inf_strd_rfrd_doc_amt_due_pybl_amt', NULL, 'DECIMAL', 259, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rmt_inf_strd_rfrd_doc_amt_due_pybl_amt_ccy', 'tx_dtls_rmt_inf_strd_rfrd_doc_amt_due_pybl_amt_ccy', NULL, 'VARCHAR', 260, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rmt_inf_strd_rfrd_doc_amt_rmtd_amt', 'tx_dtls_rmt_inf_strd_rfrd_doc_amt_rmtd_amt', NULL, 'DECIMAL', 261, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rmt_inf_strd_rfrd_doc_amt_rmtd_amt_ccy', 'tx_dtls_rmt_inf_strd_rfrd_doc_amt_rmtd_amt_ccy', NULL, 'VARCHAR', 262, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rmt_inf_strd_addtl_rmt_inf', 'tx_dtls_rmt_inf_strd_addtl_rmt_inf', NULL, 'VARCHAR', 263, true),

    -- Return Info
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rtr_inf_rsn_cd', 'tx_dtls_rtr_inf_rsn_cd', NULL, 'VARCHAR', 270, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rtr_inf_rsn_prtry', 'tx_dtls_rtr_inf_rsn_prtry', NULL, 'VARCHAR', 271, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_rtr_inf_addtl_inf', 'tx_dtls_rtr_inf_addtl_inf', NULL, 'VARCHAR', 272, true),

    -- Tax Info
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_tax_cdtr_tax_id', 'tx_dtls_tax_cdtr_tax_id', NULL, 'VARCHAR', 280, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_tax_dbtr_tax_id', 'tx_dtls_tax_dbtr_tax_id', NULL, 'VARCHAR', 281, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_tax_ttl_tax_amt', 'tx_dtls_tax_ttl_tax_amt', NULL, 'DECIMAL', 282, true),
    ('camt.053', 'cdm_payment_extension_iso20022', 'tx_dtls_tax_ttl_tax_amt_ccy', 'tx_dtls_tax_ttl_tax_amt_ccy', NULL, 'VARCHAR', 283, true),

    -- =============================================================================
    -- Legacy columns from original stg_camt053 (for backward compatibility)
    -- These use different naming conventions but map to same Gold columns
    -- =============================================================================

    -- Original message header columns (msg_id -> grp_hdr_msg_id)
    -- These are already mapped above through the new naming, no need to duplicate

    -- Original account columns
    ('camt.053', 'cdm_account', 'account_id', '_GENERATED_UUID', 'STATEMENT_ACCOUNT', 'VARCHAR', 290, true),
    ('camt.053', 'cdm_account', 'iban', 'COALESCE(acct_id_iban, account_iban)', 'STATEMENT_ACCOUNT', 'VARCHAR', 291, true),
    ('camt.053', 'cdm_account', 'account_number', 'COALESCE(acct_id_othr_id, account_number)', 'STATEMENT_ACCOUNT', 'VARCHAR', 292, true),
    ('camt.053', 'cdm_account', 'currency', 'COALESCE(acct_ccy, account_currency)', 'STATEMENT_ACCOUNT', 'VARCHAR', 293, true),
    ('camt.053', 'cdm_account', 'account_type', '''CACC''', 'STATEMENT_ACCOUNT', 'VARCHAR', 294, true),
    ('camt.053', 'cdm_account', 'source_message_type', '''camt.053''', 'STATEMENT_ACCOUNT', 'VARCHAR', 295, true),
    ('camt.053', 'cdm_account', 'source_stg_id', 'stg_id', 'STATEMENT_ACCOUNT', 'VARCHAR', 296, true),

    -- Account Owner Party
    ('camt.053', 'cdm_party', 'party_id', '_GENERATED_UUID', 'ACCOUNT_OWNER', 'VARCHAR', 300, true),
    ('camt.053', 'cdm_party', 'name', 'COALESCE(acct_ownr_nm, account_owner_name)', 'ACCOUNT_OWNER', 'VARCHAR', 301, true),
    ('camt.053', 'cdm_party', 'party_type', '''ORGANISATION''', 'ACCOUNT_OWNER', 'VARCHAR', 302, true),
    ('camt.053', 'cdm_party', 'country', 'acct_ownr_pstl_adr_ctry', 'ACCOUNT_OWNER', 'VARCHAR', 303, true),
    ('camt.053', 'cdm_party', 'street_name', 'acct_ownr_pstl_adr_strt_nm', 'ACCOUNT_OWNER', 'VARCHAR', 304, true),
    ('camt.053', 'cdm_party', 'building_number', 'acct_ownr_pstl_adr_bldg_nb', 'ACCOUNT_OWNER', 'VARCHAR', 305, true),
    ('camt.053', 'cdm_party', 'post_code', 'acct_ownr_pstl_adr_pst_cd', 'ACCOUNT_OWNER', 'VARCHAR', 306, true),
    ('camt.053', 'cdm_party', 'town_name', 'acct_ownr_pstl_adr_twn_nm', 'ACCOUNT_OWNER', 'VARCHAR', 307, true),
    ('camt.053', 'cdm_party', 'lei', 'acct_ownr_id_org_id_lei', 'ACCOUNT_OWNER', 'VARCHAR', 308, true),
    ('camt.053', 'cdm_party', 'bic', 'acct_ownr_id_org_id_any_bic', 'ACCOUNT_OWNER', 'VARCHAR', 309, true),
    ('camt.053', 'cdm_party', 'registration_number', 'acct_ownr_id_org_id_othr_id', 'ACCOUNT_OWNER', 'VARCHAR', 310, true),
    ('camt.053', 'cdm_party', 'source_message_type', '''camt.053''', 'ACCOUNT_OWNER', 'VARCHAR', 311, true),
    ('camt.053', 'cdm_party', 'source_stg_id', 'stg_id', 'ACCOUNT_OWNER', 'VARCHAR', 312, true),

    -- Account Servicer Financial Institution
    ('camt.053', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'ACCOUNT_SERVICER', 'VARCHAR', 320, true),
    ('camt.053', 'cdm_financial_institution', 'bic', 'COALESCE(acct_svcr_fin_instn_id_bicfi, account_servicer_bic)', 'ACCOUNT_SERVICER', 'VARCHAR', 321, true),
    ('camt.053', 'cdm_financial_institution', 'institution_name', 'acct_svcr_fin_instn_id_nm', 'ACCOUNT_SERVICER', 'VARCHAR', 322, true),
    ('camt.053', 'cdm_financial_institution', 'lei', 'acct_svcr_fin_instn_id_lei', 'ACCOUNT_SERVICER', 'VARCHAR', 323, true),
    ('camt.053', 'cdm_financial_institution', 'national_clearing_code', 'acct_svcr_fin_instn_id_clr_sys_mmb_id_mmb_id', 'ACCOUNT_SERVICER', 'VARCHAR', 324, true),
    ('camt.053', 'cdm_financial_institution', 'country', 'acct_svcr_fin_instn_id_pstl_adr_ctry', 'ACCOUNT_SERVICER', 'VARCHAR', 325, true),
    ('camt.053', 'cdm_financial_institution', 'source_system', '''camt.053''', 'ACCOUNT_SERVICER', 'VARCHAR', 326, true),
    ('camt.053', 'cdm_financial_institution', 'is_current', 'true', 'ACCOUNT_SERVICER', 'BOOLEAN', 327, true),

    -- Debtor from Transaction Details
    ('camt.053', 'cdm_party', 'party_id', '_GENERATED_UUID', 'DEBTOR', 'VARCHAR', 330, true),
    ('camt.053', 'cdm_party', 'name', 'tx_dtls_rltd_pties_dbtr_nm', 'DEBTOR', 'VARCHAR', 331, true),
    ('camt.053', 'cdm_party', 'party_type', '''ORGANISATION''', 'DEBTOR', 'VARCHAR', 332, true),
    ('camt.053', 'cdm_party', 'country', 'tx_dtls_rltd_pties_dbtr_pstl_adr_ctry', 'DEBTOR', 'VARCHAR', 333, true),
    ('camt.053', 'cdm_party', 'street_name', 'tx_dtls_rltd_pties_dbtr_pstl_adr_strt_nm', 'DEBTOR', 'VARCHAR', 334, true),
    ('camt.053', 'cdm_party', 'building_number', 'tx_dtls_rltd_pties_dbtr_pstl_adr_bldg_nb', 'DEBTOR', 'VARCHAR', 335, true),
    ('camt.053', 'cdm_party', 'post_code', 'tx_dtls_rltd_pties_dbtr_pstl_adr_pst_cd', 'DEBTOR', 'VARCHAR', 336, true),
    ('camt.053', 'cdm_party', 'town_name', 'tx_dtls_rltd_pties_dbtr_pstl_adr_twn_nm', 'DEBTOR', 'VARCHAR', 337, true),
    ('camt.053', 'cdm_party', 'lei', 'tx_dtls_rltd_pties_dbtr_id_org_id_lei', 'DEBTOR', 'VARCHAR', 338, true),
    ('camt.053', 'cdm_party', 'bic', 'tx_dtls_rltd_pties_dbtr_id_org_id_any_bic', 'DEBTOR', 'VARCHAR', 339, true),
    ('camt.053', 'cdm_party', 'registration_number', 'tx_dtls_rltd_pties_dbtr_id_org_id_othr_id', 'DEBTOR', 'VARCHAR', 340, true),
    ('camt.053', 'cdm_party', 'tax_id', 'tx_dtls_tax_dbtr_tax_id', 'DEBTOR', 'VARCHAR', 341, true),
    ('camt.053', 'cdm_party', 'source_message_type', '''camt.053''', 'DEBTOR', 'VARCHAR', 342, true),
    ('camt.053', 'cdm_party', 'source_stg_id', 'stg_id', 'DEBTOR', 'VARCHAR', 343, true),

    -- Debtor Account
    ('camt.053', 'cdm_account', 'account_id', '_GENERATED_UUID', 'DEBTOR', 'VARCHAR', 350, true),
    ('camt.053', 'cdm_account', 'iban', 'tx_dtls_rltd_pties_dbtr_acct_id_iban', 'DEBTOR', 'VARCHAR', 351, true),
    ('camt.053', 'cdm_account', 'account_number', 'tx_dtls_rltd_pties_dbtr_acct_id_othr_id', 'DEBTOR', 'VARCHAR', 352, true),
    ('camt.053', 'cdm_account', 'currency', 'tx_dtls_rltd_pties_dbtr_acct_ccy', 'DEBTOR', 'VARCHAR', 353, true),
    ('camt.053', 'cdm_account', 'account_type', '''CACC''', 'DEBTOR', 'VARCHAR', 354, true),
    ('camt.053', 'cdm_account', 'source_message_type', '''camt.053''', 'DEBTOR', 'VARCHAR', 355, true),
    ('camt.053', 'cdm_account', 'source_stg_id', 'stg_id', 'DEBTOR', 'VARCHAR', 356, true),

    -- Creditor from Transaction Details
    ('camt.053', 'cdm_party', 'party_id', '_GENERATED_UUID', 'CREDITOR', 'VARCHAR', 360, true),
    ('camt.053', 'cdm_party', 'name', 'tx_dtls_rltd_pties_cdtr_nm', 'CREDITOR', 'VARCHAR', 361, true),
    ('camt.053', 'cdm_party', 'party_type', '''ORGANISATION''', 'CREDITOR', 'VARCHAR', 362, true),
    ('camt.053', 'cdm_party', 'country', 'tx_dtls_rltd_pties_cdtr_pstl_adr_ctry', 'CREDITOR', 'VARCHAR', 363, true),
    ('camt.053', 'cdm_party', 'street_name', 'tx_dtls_rltd_pties_cdtr_pstl_adr_strt_nm', 'CREDITOR', 'VARCHAR', 364, true),
    ('camt.053', 'cdm_party', 'building_number', 'tx_dtls_rltd_pties_cdtr_pstl_adr_bldg_nb', 'CREDITOR', 'VARCHAR', 365, true),
    ('camt.053', 'cdm_party', 'post_code', 'tx_dtls_rltd_pties_cdtr_pstl_adr_pst_cd', 'CREDITOR', 'VARCHAR', 366, true),
    ('camt.053', 'cdm_party', 'town_name', 'tx_dtls_rltd_pties_cdtr_pstl_adr_twn_nm', 'CREDITOR', 'VARCHAR', 367, true),
    ('camt.053', 'cdm_party', 'lei', 'tx_dtls_rltd_pties_cdtr_id_org_id_lei', 'CREDITOR', 'VARCHAR', 368, true),
    ('camt.053', 'cdm_party', 'bic', 'tx_dtls_rltd_pties_cdtr_id_org_id_any_bic', 'CREDITOR', 'VARCHAR', 369, true),
    ('camt.053', 'cdm_party', 'tax_id', 'tx_dtls_tax_cdtr_tax_id', 'CREDITOR', 'VARCHAR', 370, true),
    ('camt.053', 'cdm_party', 'source_message_type', '''camt.053''', 'CREDITOR', 'VARCHAR', 371, true),
    ('camt.053', 'cdm_party', 'source_stg_id', 'stg_id', 'CREDITOR', 'VARCHAR', 372, true),

    -- Creditor Account
    ('camt.053', 'cdm_account', 'account_id', '_GENERATED_UUID', 'CREDITOR', 'VARCHAR', 380, true),
    ('camt.053', 'cdm_account', 'iban', 'tx_dtls_rltd_pties_cdtr_acct_id_iban', 'CREDITOR', 'VARCHAR', 381, true),
    ('camt.053', 'cdm_account', 'account_number', 'tx_dtls_rltd_pties_cdtr_acct_id_othr_id', 'CREDITOR', 'VARCHAR', 382, true),
    ('camt.053', 'cdm_account', 'currency', 'tx_dtls_rltd_pties_cdtr_acct_ccy', 'CREDITOR', 'VARCHAR', 383, true),
    ('camt.053', 'cdm_account', 'account_type', '''CACC''', 'CREDITOR', 'VARCHAR', 384, true),
    ('camt.053', 'cdm_account', 'source_message_type', '''camt.053''', 'CREDITOR', 'VARCHAR', 385, true),
    ('camt.053', 'cdm_account', 'source_stg_id', 'stg_id', 'CREDITOR', 'VARCHAR', 386, true),

    -- Ultimate Parties
    ('camt.053', 'cdm_party', 'party_id', '_GENERATED_UUID', 'ULTIMATE_DEBTOR', 'VARCHAR', 390, true),
    ('camt.053', 'cdm_party', 'name', 'tx_dtls_rltd_pties_ultmt_dbtr_nm', 'ULTIMATE_DEBTOR', 'VARCHAR', 391, true),
    ('camt.053', 'cdm_party', 'party_type', '''ORGANISATION''', 'ULTIMATE_DEBTOR', 'VARCHAR', 392, true),
    ('camt.053', 'cdm_party', 'source_message_type', '''camt.053''', 'ULTIMATE_DEBTOR', 'VARCHAR', 393, true),
    ('camt.053', 'cdm_party', 'source_stg_id', 'stg_id', 'ULTIMATE_DEBTOR', 'VARCHAR', 394, true),

    ('camt.053', 'cdm_party', 'party_id', '_GENERATED_UUID', 'ULTIMATE_CREDITOR', 'VARCHAR', 400, true),
    ('camt.053', 'cdm_party', 'name', 'tx_dtls_rltd_pties_ultmt_cdtr_nm', 'ULTIMATE_CREDITOR', 'VARCHAR', 401, true),
    ('camt.053', 'cdm_party', 'party_type', '''ORGANISATION''', 'ULTIMATE_CREDITOR', 'VARCHAR', 402, true),
    ('camt.053', 'cdm_party', 'source_message_type', '''camt.053''', 'ULTIMATE_CREDITOR', 'VARCHAR', 403, true),
    ('camt.053', 'cdm_party', 'source_stg_id', 'stg_id', 'ULTIMATE_CREDITOR', 'VARCHAR', 404, true),

    -- Initiating Party
    ('camt.053', 'cdm_party', 'party_id', '_GENERATED_UUID', 'INITIATING_PARTY', 'VARCHAR', 410, true),
    ('camt.053', 'cdm_party', 'name', 'tx_dtls_rltd_pties_initg_pty_nm', 'INITIATING_PARTY', 'VARCHAR', 411, true),
    ('camt.053', 'cdm_party', 'party_type', '''ORGANISATION''', 'INITIATING_PARTY', 'VARCHAR', 412, true),
    ('camt.053', 'cdm_party', 'source_message_type', '''camt.053''', 'INITIATING_PARTY', 'VARCHAR', 413, true),
    ('camt.053', 'cdm_party', 'source_stg_id', 'stg_id', 'INITIATING_PARTY', 'VARCHAR', 414, true),

    -- Financial Institutions - Debtor Agent
    ('camt.053', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'DEBTOR_AGENT', 'VARCHAR', 420, true),
    ('camt.053', 'cdm_financial_institution', 'bic', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_bicfi', 'DEBTOR_AGENT', 'VARCHAR', 421, true),
    ('camt.053', 'cdm_financial_institution', 'institution_name', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_nm', 'DEBTOR_AGENT', 'VARCHAR', 422, true),
    ('camt.053', 'cdm_financial_institution', 'lei', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_lei', 'DEBTOR_AGENT', 'VARCHAR', 423, true),
    ('camt.053', 'cdm_financial_institution', 'national_clearing_code', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_clr_sys_mmb_id_mmb_id', 'DEBTOR_AGENT', 'VARCHAR', 424, true),
    ('camt.053', 'cdm_financial_institution', 'country', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_pstl_adr_ctry', 'DEBTOR_AGENT', 'VARCHAR', 425, true),
    ('camt.053', 'cdm_financial_institution', 'source_system', '''camt.053''', 'DEBTOR_AGENT', 'VARCHAR', 426, true),
    ('camt.053', 'cdm_financial_institution', 'is_current', 'true', 'DEBTOR_AGENT', 'BOOLEAN', 427, true),

    -- Financial Institutions - Creditor Agent
    ('camt.053', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'CREDITOR_AGENT', 'VARCHAR', 430, true),
    ('camt.053', 'cdm_financial_institution', 'bic', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_bicfi', 'CREDITOR_AGENT', 'VARCHAR', 431, true),
    ('camt.053', 'cdm_financial_institution', 'institution_name', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_nm', 'CREDITOR_AGENT', 'VARCHAR', 432, true),
    ('camt.053', 'cdm_financial_institution', 'lei', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_lei', 'CREDITOR_AGENT', 'VARCHAR', 433, true),
    ('camt.053', 'cdm_financial_institution', 'national_clearing_code', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_clr_sys_mmb_id_mmb_id', 'CREDITOR_AGENT', 'VARCHAR', 434, true),
    ('camt.053', 'cdm_financial_institution', 'country', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_pstl_adr_ctry', 'CREDITOR_AGENT', 'VARCHAR', 435, true),
    ('camt.053', 'cdm_financial_institution', 'source_system', '''camt.053''', 'CREDITOR_AGENT', 'VARCHAR', 436, true),
    ('camt.053', 'cdm_financial_institution', 'is_current', 'true', 'CREDITOR_AGENT', 'BOOLEAN', 437, true),

    -- Financial Institutions - Intermediary Agents
    ('camt.053', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'INTERMEDIARY_AGENT1', 'VARCHAR', 440, true),
    ('camt.053', 'cdm_financial_institution', 'bic', 'tx_dtls_rltd_agts_intrmy_agt1_fin_instn_id_bicfi', 'INTERMEDIARY_AGENT1', 'VARCHAR', 441, true),
    ('camt.053', 'cdm_financial_institution', 'source_system', '''camt.053''', 'INTERMEDIARY_AGENT1', 'VARCHAR', 442, true),
    ('camt.053', 'cdm_financial_institution', 'is_current', 'true', 'INTERMEDIARY_AGENT1', 'BOOLEAN', 443, true),

    ('camt.053', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'INTERMEDIARY_AGENT2', 'VARCHAR', 450, true),
    ('camt.053', 'cdm_financial_institution', 'bic', 'tx_dtls_rltd_agts_intrmy_agt2_fin_instn_id_bicfi', 'INTERMEDIARY_AGENT2', 'VARCHAR', 451, true),
    ('camt.053', 'cdm_financial_institution', 'source_system', '''camt.053''', 'INTERMEDIARY_AGENT2', 'VARCHAR', 452, true),
    ('camt.053', 'cdm_financial_institution', 'is_current', 'true', 'INTERMEDIARY_AGENT2', 'BOOLEAN', 453, true),

    ('camt.053', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'INTERMEDIARY_AGENT3', 'VARCHAR', 460, true),
    ('camt.053', 'cdm_financial_institution', 'bic', 'tx_dtls_rltd_agts_intrmy_agt3_fin_instn_id_bicfi', 'INTERMEDIARY_AGENT3', 'VARCHAR', 461, true),
    ('camt.053', 'cdm_financial_institution', 'source_system', '''camt.053''', 'INTERMEDIARY_AGENT3', 'VARCHAR', 462, true),
    ('camt.053', 'cdm_financial_institution', 'is_current', 'true', 'INTERMEDIARY_AGENT3', 'BOOLEAN', 463, true),

    -- Financial Institutions - Delivering and Receiving Agents
    ('camt.053', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'DELIVERING_AGENT', 'VARCHAR', 470, true),
    ('camt.053', 'cdm_financial_institution', 'bic', 'tx_dtls_rltd_agts_dlvrg_agt_fin_instn_id_bicfi', 'DELIVERING_AGENT', 'VARCHAR', 471, true),
    ('camt.053', 'cdm_financial_institution', 'source_system', '''camt.053''', 'DELIVERING_AGENT', 'VARCHAR', 472, true),
    ('camt.053', 'cdm_financial_institution', 'is_current', 'true', 'DELIVERING_AGENT', 'BOOLEAN', 473, true),

    ('camt.053', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'RECEIVING_AGENT', 'VARCHAR', 480, true),
    ('camt.053', 'cdm_financial_institution', 'bic', 'tx_dtls_rltd_agts_rcvg_agt_fin_instn_id_bicfi', 'RECEIVING_AGENT', 'VARCHAR', 481, true),
    ('camt.053', 'cdm_financial_institution', 'source_system', '''camt.053''', 'RECEIVING_AGENT', 'VARCHAR', 482, true),
    ('camt.053', 'cdm_financial_institution', 'is_current', 'true', 'RECEIVING_AGENT', 'BOOLEAN', 483, true)
ON CONFLICT (format_id, gold_table, gold_column, entity_role) DO UPDATE SET
    source_expression = EXCLUDED.source_expression,
    ordinal_position = EXCLUDED.ordinal_position,
    is_active = EXCLUDED.is_active,
    updated_at = CURRENT_TIMESTAMP;

COMMIT;

-- =============================================================================
-- PART 3: Verification Query
-- =============================================================================
-- Run this to check coverage:

-- SELECT 'Silver columns' as metric, COUNT(*) as count
-- FROM information_schema.columns
-- WHERE table_schema = 'silver' AND table_name = 'stg_camt053'
-- UNION ALL
-- SELECT 'Gold mappings' as metric, COUNT(*) as count
-- FROM mapping.gold_field_mappings
-- WHERE format_id = 'camt.053' AND is_active = true;
