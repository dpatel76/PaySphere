-- ============================================================================
-- Fix camt.053 Silver Field Mappings to 100% Coverage
-- ============================================================================
-- This script inserts/updates all 211 silver_field_mappings for camt.053
--
-- Key rules:
-- - source_path MUST match standard_fields.field_path exactly for traceability
-- - parser_path contains the actual key used by the camt053 parser
-- - NO fallback values - if source doesn't have data, allow NULL
-- ============================================================================

BEGIN;

-- First, delete existing mappings to start fresh (preserves system mappings)
DELETE FROM mapping.silver_field_mappings
WHERE format_id = 'camt.053'
AND target_column NOT IN ('stg_id', 'raw_id', 'message_type', '_batch_id', '_processed_at', 'processing_status', 'processed_to_gold_at');

-- ============================================================================
-- GROUP HEADER MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'grp_hdr_addtl_inf', 'BkToCstmrStmt/GrpHdr/AddtlInf', 'grpHdr.addtlInf', 'VARCHAR', false, true),
('camt.053', 'grp_hdr_cre_dt_tm', 'BkToCstmrStmt/GrpHdr/CreDtTm', 'grpHdr.creDtTm', 'TIMESTAMP', true, true),
('camt.053', 'grp_hdr_msg_id', 'BkToCstmrStmt/GrpHdr/MsgId', 'grpHdr.msgId', 'VARCHAR', true, true),
('camt.053', 'grp_hdr_msg_pgntn_last_pg_ind', 'BkToCstmrStmt/GrpHdr/MsgPgntn/LastPgInd', 'grpHdr.msgPgntn.lastPgInd', 'BOOLEAN', false, true),
('camt.053', 'grp_hdr_msg_pgntn_pg_nb', 'BkToCstmrStmt/GrpHdr/MsgPgntn/PgNb', 'grpHdr.msgPgntn.pgNb', 'VARCHAR', false, true),
('camt.053', 'grp_hdr_msg_rcpt_id_org_id_any_bic', 'BkToCstmrStmt/GrpHdr/MsgRcpt/Id/OrgId/AnyBIC', 'grpHdr.msgRcpt.id.orgId.anyBic', 'VARCHAR', false, true),
('camt.053', 'grp_hdr_msg_rcpt_nm', 'BkToCstmrStmt/GrpHdr/MsgRcpt/Nm', 'grpHdr.msgRcpt.nm', 'VARCHAR', false, true),
('camt.053', 'grp_hdr_orgnl_biz_qry_msg_id', 'BkToCstmrStmt/GrpHdr/OrgnlBizQry/MsgId', 'grpHdr.orgnlBizQry.msgId', 'VARCHAR', false, true);

-- ============================================================================
-- ACCOUNT MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'acct_ccy', 'BkToCstmrStmt/Stmt/Acct/Ccy', 'stmt.acct.ccy', 'VARCHAR', false, true),
('camt.053', 'acct_id_iban', 'BkToCstmrStmt/Stmt/Acct/Id/IBAN', 'stmt.acct.id.iban', 'VARCHAR', false, true),
('camt.053', 'acct_id_othr_id', 'BkToCstmrStmt/Stmt/Acct/Id/Othr/Id', 'stmt.acct.id.othr.id', 'VARCHAR', false, true),
('camt.053', 'acct_id_othr_schme_nm_cd', 'BkToCstmrStmt/Stmt/Acct/Id/Othr/SchmeNm/Cd', 'stmt.acct.id.othr.schmeNm.cd', 'VARCHAR', false, true),
('camt.053', 'acct_id_othr_schme_nm_prtry', 'BkToCstmrStmt/Stmt/Acct/Id/Othr/SchmeNm/Prtry', 'stmt.acct.id.othr.schmeNm.prtry', 'VARCHAR', false, true),
('camt.053', 'acct_nm', 'BkToCstmrStmt/Stmt/Acct/Nm', 'stmt.acct.nm', 'VARCHAR', false, true),
('camt.053', 'acct_ownr_id_org_id_any_bic', 'BkToCstmrStmt/Stmt/Acct/Ownr/Id/OrgId/AnyBIC', 'stmt.acct.ownr.id.orgId.anyBic', 'VARCHAR', false, true),
('camt.053', 'acct_ownr_id_org_id_lei', 'BkToCstmrStmt/Stmt/Acct/Ownr/Id/OrgId/LEI', 'stmt.acct.ownr.id.orgId.lei', 'VARCHAR', false, true),
('camt.053', 'acct_ownr_id_org_id_othr_id', 'BkToCstmrStmt/Stmt/Acct/Ownr/Id/OrgId/Othr/Id', 'stmt.acct.ownr.id.orgId.othr.id', 'VARCHAR', false, true),
('camt.053', 'acct_ownr_nm', 'BkToCstmrStmt/Stmt/Acct/Ownr/Nm', 'stmt.acct.ownr.nm', 'VARCHAR', false, true),
('camt.053', 'acct_ownr_pstl_adr_bldg_nb', 'BkToCstmrStmt/Stmt/Acct/Ownr/PstlAdr/BldgNb', 'stmt.acct.ownr.pstlAdr.bldgNb', 'VARCHAR', false, true),
('camt.053', 'acct_ownr_pstl_adr_ctry', 'BkToCstmrStmt/Stmt/Acct/Ownr/PstlAdr/Ctry', 'stmt.acct.ownr.pstlAdr.ctry', 'VARCHAR', false, true),
('camt.053', 'acct_ownr_pstl_adr_pst_cd', 'BkToCstmrStmt/Stmt/Acct/Ownr/PstlAdr/PstCd', 'stmt.acct.ownr.pstlAdr.pstCd', 'VARCHAR', false, true),
('camt.053', 'acct_ownr_pstl_adr_strt_nm', 'BkToCstmrStmt/Stmt/Acct/Ownr/PstlAdr/StrtNm', 'stmt.acct.ownr.pstlAdr.strtNm', 'VARCHAR', false, true),
('camt.053', 'acct_ownr_pstl_adr_twn_nm', 'BkToCstmrStmt/Stmt/Acct/Ownr/PstlAdr/TwnNm', 'stmt.acct.ownr.pstlAdr.twnNm', 'VARCHAR', false, true),
('camt.053', 'acct_prxy_id', 'BkToCstmrStmt/Stmt/Acct/Prxy/Id', 'stmt.acct.prxy.id', 'VARCHAR', false, true),
('camt.053', 'acct_svcr_fin_instn_id_bicfi', 'BkToCstmrStmt/Stmt/Acct/Svcr/FinInstnId/BICFI', 'stmt.acct.svcr.finInstnId.bicfi', 'VARCHAR', false, true),
('camt.053', 'acct_svcr_fin_instn_id_clr_sys_mmb_id_mmb_id', 'BkToCstmrStmt/Stmt/Acct/Svcr/FinInstnId/ClrSysMmbId/MmbId', 'stmt.acct.svcr.finInstnId.clrSysMmbId.mmbId', 'VARCHAR', false, true),
('camt.053', 'acct_svcr_fin_instn_id_lei', 'BkToCstmrStmt/Stmt/Acct/Svcr/FinInstnId/LEI', 'stmt.acct.svcr.finInstnId.lei', 'VARCHAR', false, true),
('camt.053', 'acct_svcr_fin_instn_id_nm', 'BkToCstmrStmt/Stmt/Acct/Svcr/FinInstnId/Nm', 'stmt.acct.svcr.finInstnId.nm', 'VARCHAR', false, true),
('camt.053', 'acct_svcr_fin_instn_id_pstl_adr_ctry', 'BkToCstmrStmt/Stmt/Acct/Svcr/FinInstnId/PstlAdr/Ctry', 'stmt.acct.svcr.finInstnId.pstlAdr.ctry', 'VARCHAR', false, true),
('camt.053', 'acct_tp_cd', 'BkToCstmrStmt/Stmt/Acct/Tp/Cd', 'stmt.acct.tp.cd', 'VARCHAR', false, true),
('camt.053', 'acct_tp_prtry', 'BkToCstmrStmt/Stmt/Acct/Tp/Prtry', 'stmt.acct.tp.prtry', 'VARCHAR', false, true);

-- ============================================================================
-- BALANCE MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'bal_amt', 'BkToCstmrStmt/Stmt/Bal/Amt', 'stmt.bal.amt', 'DECIMAL', true, true),
('camt.053', 'bal_amt_ccy', 'BkToCstmrStmt/Stmt/Bal/Amt/@Ccy', 'stmt.bal.amt.ccy', 'VARCHAR', true, true),
('camt.053', 'bal_avlbty_amt', 'BkToCstmrStmt/Stmt/Bal/Avlbty/Amt', 'stmt.bal.avlbty.amt', 'DECIMAL', false, true),
('camt.053', 'bal_avlbty_amt_ccy', 'BkToCstmrStmt/Stmt/Bal/Avlbty/Amt/@Ccy', 'stmt.bal.avlbty.amt.ccy', 'VARCHAR', false, true),
('camt.053', 'bal_avlbty_cdt_dbt_ind', 'BkToCstmrStmt/Stmt/Bal/Avlbty/CdtDbtInd', 'stmt.bal.avlbty.cdtDbtInd', 'VARCHAR', false, true),
('camt.053', 'bal_avlbty_dt_actl_dt', 'BkToCstmrStmt/Stmt/Bal/Avlbty/Dt/ActlDt', 'stmt.bal.avlbty.dt.actlDt', 'DATE', false, true),
('camt.053', 'bal_avlbty_dt_nb_of_days', 'BkToCstmrStmt/Stmt/Bal/Avlbty/Dt/NbOfDays', 'stmt.bal.avlbty.dt.nbOfDays', 'VARCHAR', false, true),
('camt.053', 'bal_cdt_dbt_ind', 'BkToCstmrStmt/Stmt/Bal/CdtDbtInd', 'stmt.bal.cdtDbtInd', 'VARCHAR', true, true),
('camt.053', 'bal_cdt_line_amt', 'BkToCstmrStmt/Stmt/Bal/CdtLine/Amt', 'stmt.bal.cdtLine.amt', 'DECIMAL', false, true),
('camt.053', 'bal_cdt_line_amt_ccy', 'BkToCstmrStmt/Stmt/Bal/CdtLine/Amt/@Ccy', 'stmt.bal.cdtLine.amt.ccy', 'VARCHAR', false, true),
('camt.053', 'bal_cdt_line_incl', 'BkToCstmrStmt/Stmt/Bal/CdtLine/Incl', 'stmt.bal.cdtLine.incl', 'BOOLEAN', false, true),
('camt.053', 'bal_dt_dt', 'BkToCstmrStmt/Stmt/Bal/Dt/Dt', 'stmt.bal.dt.dt', 'DATE', false, true),
('camt.053', 'bal_dt_dt_tm', 'BkToCstmrStmt/Stmt/Bal/Dt/DtTm', 'stmt.bal.dt.dtTm', 'TIMESTAMP', false, true),
('camt.053', 'bal_tp_cd_or_prtry_cd', 'BkToCstmrStmt/Stmt/Bal/Tp/CdOrPrtry/Cd', 'stmt.bal.tp.cdOrPrtry.cd', 'VARCHAR', false, true),
('camt.053', 'bal_tp_cd_or_prtry_prtry', 'BkToCstmrStmt/Stmt/Bal/Tp/CdOrPrtry/Prtry', 'stmt.bal.tp.cdOrPrtry.prtry', 'VARCHAR', false, true),
('camt.053', 'bal_tp_sub_tp_cd', 'BkToCstmrStmt/Stmt/Bal/Tp/SubTp/Cd', 'stmt.bal.tp.subTp.cd', 'VARCHAR', false, true),
('camt.053', 'bal_tp_sub_tp_prtry', 'BkToCstmrStmt/Stmt/Bal/Tp/SubTp/Prtry', 'stmt.bal.tp.subTp.prtry', 'VARCHAR', false, true);

-- ============================================================================
-- STATEMENT MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'cpy_dplct_ind', 'BkToCstmrStmt/Stmt/CpyDplctInd', 'stmt.cpyDplctInd', 'VARCHAR', false, true),
('camt.053', 'stmt_cre_dt_tm', 'BkToCstmrStmt/Stmt/CreDtTm', 'stmt.creDtTm', 'TIMESTAMP', false, true),
('camt.053', 'elctrnc_seq_nb', 'BkToCstmrStmt/Stmt/ElctrncSeqNb', 'stmt.elctrncSeqNb', 'INTEGER', false, true),
('camt.053', 'fr_to_dt_fr_dt_tm', 'BkToCstmrStmt/Stmt/FrToDt/FrDtTm', 'stmt.frToDt.frDtTm', 'TIMESTAMP', false, true),
('camt.053', 'fr_to_dt_to_dt_tm', 'BkToCstmrStmt/Stmt/FrToDt/ToDtTm', 'stmt.frToDt.toDtTm', 'TIMESTAMP', false, true),
('camt.053', 'stmt_id', 'BkToCstmrStmt/Stmt/Id', 'stmt.id', 'VARCHAR', true, true),
('camt.053', 'lgl_seq_nb', 'BkToCstmrStmt/Stmt/LglSeqNb', 'stmt.lglSeqNb', 'INTEGER', false, true);

-- ============================================================================
-- ENTRY MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'ntry_acct_svcr_ref', 'BkToCstmrStmt/Stmt/Ntry/AcctSvcrRef', 'stmt.ntry.acctSvcrRef', 'VARCHAR', false, true),
('camt.053', 'ntry_addtl_inf_ind_msg_nm_id', 'BkToCstmrStmt/Stmt/Ntry/AddtlInfInd/MsgNmId', 'stmt.ntry.addtlInfInd.msgNmId', 'VARCHAR', false, true),
('camt.053', 'ntry_addtl_ntry_inf', 'BkToCstmrStmt/Stmt/Ntry/AddtlNtryInf', 'stmt.ntry.addtlNtryInf', 'VARCHAR', false, true),
('camt.053', 'ntry_amt', 'BkToCstmrStmt/Stmt/Ntry/Amt', 'stmt.ntry.amt', 'DECIMAL', true, true),
('camt.053', 'ntry_amt_ccy', 'BkToCstmrStmt/Stmt/Ntry/Amt/@Ccy', 'stmt.ntry.amt.ccy', 'VARCHAR', true, true),
('camt.053', 'ntry_amt_dtls_cntr_val_amt_amt', 'BkToCstmrStmt/Stmt/Ntry/AmtDtls/CntrValAmt/Amt', 'stmt.ntry.amtDtls.cntrValAmt.amt', 'DECIMAL', false, true),
('camt.053', 'ntry_amt_dtls_cntr_val_amt_amt_ccy', 'BkToCstmrStmt/Stmt/Ntry/AmtDtls/CntrValAmt/Amt/@Ccy', 'stmt.ntry.amtDtls.cntrValAmt.amt.ccy', 'VARCHAR', false, true),
('camt.053', 'ntry_amt_dtls_instd_amt_amt', 'BkToCstmrStmt/Stmt/Ntry/AmtDtls/InstdAmt/Amt', 'stmt.ntry.amtDtls.instdAmt.amt', 'DECIMAL', false, true),
('camt.053', 'ntry_amt_dtls_instd_amt_amt_ccy', 'BkToCstmrStmt/Stmt/Ntry/AmtDtls/InstdAmt/Amt/@Ccy', 'stmt.ntry.amtDtls.instdAmt.amt.ccy', 'VARCHAR', false, true),
('camt.053', 'ntry_amt_dtls_tx_amt_amt', 'BkToCstmrStmt/Stmt/Ntry/AmtDtls/TxAmt/Amt', 'stmt.ntry.amtDtls.txAmt.amt', 'DECIMAL', false, true),
('camt.053', 'ntry_amt_dtls_tx_amt_amt_ccy', 'BkToCstmrStmt/Stmt/Ntry/AmtDtls/TxAmt/Amt/@Ccy', 'stmt.ntry.amtDtls.txAmt.amt.ccy', 'VARCHAR', false, true),
('camt.053', 'ntry_avlbty_amt', 'BkToCstmrStmt/Stmt/Ntry/Avlbty/Amt', 'stmt.ntry.avlbty.amt', 'DECIMAL', false, true),
('camt.053', 'ntry_avlbty_cdt_dbt_ind', 'BkToCstmrStmt/Stmt/Ntry/Avlbty/CdtDbtInd', 'stmt.ntry.avlbty.cdtDbtInd', 'VARCHAR', false, true),
('camt.053', 'ntry_bk_tx_cd_domn_cd', 'BkToCstmrStmt/Stmt/Ntry/BkTxCd/Domn/Cd', 'stmt.ntry.bkTxCd.domn.cd', 'VARCHAR', false, true),
('camt.053', 'ntry_bk_tx_cd_domn_fmly_cd', 'BkToCstmrStmt/Stmt/Ntry/BkTxCd/Domn/Fmly/Cd', 'stmt.ntry.bkTxCd.domn.fmly.cd', 'VARCHAR', false, true),
('camt.053', 'ntry_bk_tx_cd_domn_fmly_sub_fmly_cd', 'BkToCstmrStmt/Stmt/Ntry/BkTxCd/Domn/Fmly/SubFmlyCd', 'stmt.ntry.bkTxCd.domn.fmly.subFmlyCd', 'VARCHAR', false, true),
('camt.053', 'ntry_bk_tx_cd_prtry_cd', 'BkToCstmrStmt/Stmt/Ntry/BkTxCd/Prtry/Cd', 'stmt.ntry.bkTxCd.prtry.cd', 'VARCHAR', false, true),
('camt.053', 'ntry_bk_tx_cd_prtry_issr', 'BkToCstmrStmt/Stmt/Ntry/BkTxCd/Prtry/Issr', 'stmt.ntry.bkTxCd.prtry.issr', 'VARCHAR', false, true),
('camt.053', 'ntry_bookg_dt_dt', 'BkToCstmrStmt/Stmt/Ntry/BookgDt/Dt', 'stmt.ntry.bookgDt.dt', 'DATE', false, true),
('camt.053', 'ntry_bookg_dt_dt_tm', 'BkToCstmrStmt/Stmt/Ntry/BookgDt/DtTm', 'stmt.ntry.bookgDt.dtTm', 'TIMESTAMP', false, true),
('camt.053', 'ntry_card_tx_card_plain_card_data_pan', 'BkToCstmrStmt/Stmt/Ntry/CardTx/Card/PlainCardData/PAN', 'stmt.ntry.cardTx.card.plainCardData.pan', 'VARCHAR', false, true),
('camt.053', 'ntry_cdt_dbt_ind', 'BkToCstmrStmt/Stmt/Ntry/CdtDbtInd', 'stmt.ntry.cdtDbtInd', 'VARCHAR', true, true),
('camt.053', 'ntry_chrgs_rcrd_amt', 'BkToCstmrStmt/Stmt/Ntry/Chrgs/Rcrd/Amt', 'stmt.ntry.chrgs.rcrd.amt', 'DECIMAL', false, true),
('camt.053', 'ntry_chrgs_rcrd_amt_ccy', 'BkToCstmrStmt/Stmt/Ntry/Chrgs/Rcrd/Amt/@Ccy', 'stmt.ntry.chrgs.rcrd.amt.ccy', 'VARCHAR', false, true),
('camt.053', 'ntry_chrgs_rcrd_cdt_dbt_ind', 'BkToCstmrStmt/Stmt/Ntry/Chrgs/Rcrd/CdtDbtInd', 'stmt.ntry.chrgs.rcrd.cdtDbtInd', 'VARCHAR', false, true),
('camt.053', 'ntry_chrgs_rcrd_chrg_incl_ind', 'BkToCstmrStmt/Stmt/Ntry/Chrgs/Rcrd/ChrgInclInd', 'stmt.ntry.chrgs.rcrd.chrgInclInd', 'BOOLEAN', false, true),
('camt.053', 'ntry_chrgs_ttl_chrgs_and_tax_amt', 'BkToCstmrStmt/Stmt/Ntry/Chrgs/TtlChrgsAndTaxAmt', 'stmt.ntry.chrgs.ttlChrgsAndTaxAmt', 'DECIMAL', false, true),
('camt.053', 'ntry_commn_sts', 'BkToCstmrStmt/Stmt/Ntry/CommnSts', 'stmt.ntry.commnSts', 'VARCHAR', false, true),
('camt.053', 'ntry_ntry_ref', 'BkToCstmrStmt/Stmt/Ntry/NtryRef', 'stmt.ntry.ntryRef', 'VARCHAR', false, true),
('camt.053', 'ntry_rvsl_ind', 'BkToCstmrStmt/Stmt/Ntry/RvslInd', 'stmt.ntry.rvslInd', 'BOOLEAN', false, true),
('camt.053', 'ntry_sts_cd', 'BkToCstmrStmt/Stmt/Ntry/Sts/Cd', 'stmt.ntry.sts.cd', 'VARCHAR', false, true),
('camt.053', 'ntry_sts_prtry', 'BkToCstmrStmt/Stmt/Ntry/Sts/Prtry', 'stmt.ntry.sts.prtry', 'VARCHAR', false, true),
('camt.053', 'ntry_tech_inpt_chanl_id', 'BkToCstmrStmt/Stmt/Ntry/TechInptChanl/Id', 'stmt.ntry.techInptChanl.id', 'VARCHAR', false, true),
('camt.053', 'ntry_val_dt_dt', 'BkToCstmrStmt/Stmt/Ntry/ValDt/Dt', 'stmt.ntry.valDt.dt', 'DATE', false, true),
('camt.053', 'ntry_val_dt_dt_tm', 'BkToCstmrStmt/Stmt/Ntry/ValDt/DtTm', 'stmt.ntry.valDt.dtTm', 'TIMESTAMP', false, true);

-- ============================================================================
-- ENTRY DETAILS - BATCH MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'ntry_dtls_btch_cdt_dbt_ind', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/Btch/CdtDbtInd', 'stmt.ntry.ntryDtls.btch.cdtDbtInd', 'VARCHAR', false, true),
('camt.053', 'ntry_dtls_btch_msg_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/Btch/MsgId', 'stmt.ntry.ntryDtls.btch.msgId', 'VARCHAR', false, true),
('camt.053', 'ntry_dtls_btch_nb_of_txs', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/Btch/NbOfTxs', 'stmt.ntry.ntryDtls.btch.nbOfTxs', 'INTEGER', false, true),
('camt.053', 'ntry_dtls_btch_pmt_inf_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/Btch/PmtInfId', 'stmt.ntry.ntryDtls.btch.pmtInfId', 'VARCHAR', false, true),
('camt.053', 'ntry_dtls_btch_ttl_amt', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/Btch/TtlAmt', 'stmt.ntry.ntryDtls.btch.ttlAmt', 'DECIMAL', false, true),
('camt.053', 'ntry_dtls_btch_ttl_amt_ccy', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/Btch/TtlAmt/@Ccy', 'stmt.ntry.ntryDtls.btch.ttlAmt.ccy', 'VARCHAR', false, true);

-- ============================================================================
-- TRANSACTION DETAILS MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'tx_dtls_addtl_tx_inf', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/AddtlTxInf', 'stmt.ntry.ntryDtls.txDtls.addtlTxInf', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_amt', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Amt', 'stmt.ntry.ntryDtls.txDtls.amt', 'DECIMAL', false, true),
('camt.053', 'tx_dtls_amt_ccy', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Amt/@Ccy', 'stmt.ntry.ntryDtls.txDtls.amt.ccy', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_amt_dtls_instd_amt_amt', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/AmtDtls/InstdAmt/Amt', 'stmt.ntry.ntryDtls.txDtls.amtDtls.instdAmt.amt', 'DECIMAL', false, true),
('camt.053', 'tx_dtls_amt_dtls_instd_amt_amt_ccy', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/AmtDtls/InstdAmt/Amt/@Ccy', 'stmt.ntry.ntryDtls.txDtls.amtDtls.instdAmt.amt.ccy', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_amt_dtls_tx_amt_amt', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/AmtDtls/TxAmt/Amt', 'stmt.ntry.ntryDtls.txDtls.amtDtls.txAmt.amt', 'DECIMAL', false, true),
('camt.053', 'tx_dtls_amt_dtls_tx_amt_amt_ccy', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/AmtDtls/TxAmt/Amt/@Ccy', 'stmt.ntry.ntryDtls.txDtls.amtDtls.txAmt.amt.ccy', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_bk_tx_cd_domn_cd', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/BkTxCd/Domn/Cd', 'stmt.ntry.ntryDtls.txDtls.bkTxCd.domn.cd', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_bk_tx_cd_domn_fmly_cd', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/BkTxCd/Domn/Fmly/Cd', 'stmt.ntry.ntryDtls.txDtls.bkTxCd.domn.fmly.cd', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_bk_tx_cd_domn_fmly_sub_fmly_cd', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/BkTxCd/Domn/Fmly/SubFmlyCd', 'stmt.ntry.ntryDtls.txDtls.bkTxCd.domn.fmly.subFmlyCd', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_cdt_dbt_ind', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/CdtDbtInd', 'stmt.ntry.ntryDtls.txDtls.cdtDbtInd', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_fin_instrm_id_isin', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/FinInstrmId/ISIN', 'stmt.ntry.ntryDtls.txDtls.finInstrmId.isin', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_purp_cd', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Purp/Cd', 'stmt.ntry.ntryDtls.txDtls.purp.cd', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_purp_prtry', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Purp/Prtry', 'stmt.ntry.ntryDtls.txDtls.purp.prtry', 'VARCHAR', false, true);

-- ============================================================================
-- TRANSACTION REFERENCES MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'tx_dtls_refs_acct_ownr_tx_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/AcctOwnrTxId', 'stmt.ntry.ntryDtls.txDtls.refs.acctOwnrTxId', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_refs_acct_svcr_ref', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/AcctSvcrRef', 'stmt.ntry.ntryDtls.txDtls.refs.acctSvcrRef', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_refs_acct_svcr_tx_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/AcctSvcrTxId', 'stmt.ntry.ntryDtls.txDtls.refs.acctSvcrTxId', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_refs_chq_nb', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/ChqNb', 'stmt.ntry.ntryDtls.txDtls.refs.chqNb', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_refs_clr_sys_ref', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/ClrSysRef', 'stmt.ntry.ntryDtls.txDtls.refs.clrSysRef', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_refs_end_to_end_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/EndToEndId', 'stmt.ntry.ntryDtls.txDtls.refs.endToEndId', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_refs_instr_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/InstrId', 'stmt.ntry.ntryDtls.txDtls.refs.instrId', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_refs_mkt_infrstrctr_tx_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/MktInfrstrctrTxId', 'stmt.ntry.ntryDtls.txDtls.refs.mktInfrstrctrTxId', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_refs_mndt_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/MndtId', 'stmt.ntry.ntryDtls.txDtls.refs.mndtId', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_refs_msg_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/MsgId', 'stmt.ntry.ntryDtls.txDtls.refs.msgId', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_refs_pmt_inf_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/PmtInfId', 'stmt.ntry.ntryDtls.txDtls.refs.pmtInfId', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_refs_prcg_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/PrcgId', 'stmt.ntry.ntryDtls.txDtls.refs.prcgId', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_refs_prtry_ref', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/Prtry/Ref', 'stmt.ntry.ntryDtls.txDtls.refs.prtry.ref', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_refs_prtry_tp', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/Prtry/Tp', 'stmt.ntry.ntryDtls.txDtls.refs.prtry.tp', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_refs_tx_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/TxId', 'stmt.ntry.ntryDtls.txDtls.refs.txId', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_refs_uetr', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Refs/UETR', 'stmt.ntry.ntryDtls.txDtls.refs.uetr', 'VARCHAR', false, true);

-- ============================================================================
-- RELATED AGENTS MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_bicfi', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/BICFI', 'stmt.ntry.ntryDtls.txDtls.rltdAgts.cdtrAgt.finInstnId.bicfi', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_clr_sys_mmb_id_mmb_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'stmt.ntry.ntryDtls.txDtls.rltdAgts.cdtrAgt.finInstnId.clrSysMmbId.mmbId', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_lei', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/LEI', 'stmt.ntry.ntryDtls.txDtls.rltdAgts.cdtrAgt.finInstnId.lei', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_nm', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/Nm', 'stmt.ntry.ntryDtls.txDtls.rltdAgts.cdtrAgt.finInstnId.nm', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_pstl_adr_ctry', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/PstlAdr/Ctry', 'stmt.ntry.ntryDtls.txDtls.rltdAgts.cdtrAgt.finInstnId.pstlAdr.ctry', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_bicfi', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/BICFI', 'stmt.ntry.ntryDtls.txDtls.rltdAgts.dbtrAgt.finInstnId.bicfi', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_clr_sys_mmb_id_mmb_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'stmt.ntry.ntryDtls.txDtls.rltdAgts.dbtrAgt.finInstnId.clrSysMmbId.mmbId', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_lei', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/LEI', 'stmt.ntry.ntryDtls.txDtls.rltdAgts.dbtrAgt.finInstnId.lei', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_nm', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/Nm', 'stmt.ntry.ntryDtls.txDtls.rltdAgts.dbtrAgt.finInstnId.nm', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_pstl_adr_ctry', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/PstlAdr/Ctry', 'stmt.ntry.ntryDtls.txDtls.rltdAgts.dbtrAgt.finInstnId.pstlAdr.ctry', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_agts_dlvrg_agt_fin_instn_id_bicfi', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/DlvrgAgt/FinInstnId/BICFI', 'stmt.ntry.ntryDtls.txDtls.rltdAgts.dlvrgAgt.finInstnId.bicfi', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_agts_intrmy_agt1_fin_instn_id_bicfi', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/IntrmyAgt1/FinInstnId/BICFI', 'stmt.ntry.ntryDtls.txDtls.rltdAgts.intrmyAgt1.finInstnId.bicfi', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_agts_intrmy_agt2_fin_instn_id_bicfi', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/IntrmyAgt2/FinInstnId/BICFI', 'stmt.ntry.ntryDtls.txDtls.rltdAgts.intrmyAgt2.finInstnId.bicfi', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_agts_intrmy_agt3_fin_instn_id_bicfi', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/IntrmyAgt3/FinInstnId/BICFI', 'stmt.ntry.ntryDtls.txDtls.rltdAgts.intrmyAgt3.finInstnId.bicfi', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_agts_rcvg_agt_fin_instn_id_bicfi', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/RcvgAgt/FinInstnId/BICFI', 'stmt.ntry.ntryDtls.txDtls.rltdAgts.rcvgAgt.finInstnId.bicfi', 'VARCHAR', false, true);

-- ============================================================================
-- RELATED DATES MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'tx_dtls_rltd_dts_accptnc_dt_tm', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdDts/AccptncDtTm', 'stmt.ntry.ntryDtls.txDtls.rltdDts.accptncDtTm', 'TIMESTAMP', false, true),
('camt.053', 'tx_dtls_rltd_dts_end_dt', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdDts/EndDt', 'stmt.ntry.ntryDtls.txDtls.rltdDts.endDt', 'DATE', false, true),
('camt.053', 'tx_dtls_rltd_dts_intr_bk_sttlm_dt', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdDts/IntrBkSttlmDt', 'stmt.ntry.ntryDtls.txDtls.rltdDts.intrBkSttlmDt', 'DATE', false, true),
('camt.053', 'tx_dtls_rltd_dts_start_dt', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdDts/StartDt', 'stmt.ntry.ntryDtls.txDtls.rltdDts.startDt', 'DATE', false, true),
('camt.053', 'tx_dtls_rltd_dts_trad_dt', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdDts/TradDt', 'stmt.ntry.ntryDtls.txDtls.rltdDts.tradDt', 'DATE', false, true),
('camt.053', 'tx_dtls_rltd_dts_tx_dt_tm', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdDts/TxDtTm', 'stmt.ntry.ntryDtls.txDtls.rltdDts.txDtTm', 'TIMESTAMP', false, true);

-- ============================================================================
-- RELATED PRICE MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'tx_dtls_rltd_pric_deal_pric', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPric/DealPric', 'stmt.ntry.ntryDtls.txDtls.rltdPric.dealPric', 'DECIMAL', false, true),
('camt.053', 'tx_dtls_rltd_pric_deal_pric_ccy', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPric/DealPric/@Ccy', 'stmt.ntry.ntryDtls.txDtls.rltdPric.dealPric.ccy', 'VARCHAR', false, true);

-- ============================================================================
-- RELATED PARTIES - CREDITOR MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'tx_dtls_rltd_pties_cdtr_id_org_id_any_bic', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Id/OrgId/AnyBIC', 'stmt.ntry.ntryDtls.txDtls.rltdPties.cdtr.id.orgId.anyBic', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_cdtr_id_org_id_lei', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Id/OrgId/LEI', 'stmt.ntry.ntryDtls.txDtls.rltdPties.cdtr.id.orgId.lei', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_cdtr_nm', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Nm', 'stmt.ntry.ntryDtls.txDtls.rltdPties.cdtr.nm', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_cdtr_pstl_adr_bldg_nb', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/BldgNb', 'stmt.ntry.ntryDtls.txDtls.rltdPties.cdtr.pstlAdr.bldgNb', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_cdtr_pstl_adr_ctry', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/Ctry', 'stmt.ntry.ntryDtls.txDtls.rltdPties.cdtr.pstlAdr.ctry', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_cdtr_pstl_adr_pst_cd', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/PstCd', 'stmt.ntry.ntryDtls.txDtls.rltdPties.cdtr.pstlAdr.pstCd', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_cdtr_pstl_adr_strt_nm', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/StrtNm', 'stmt.ntry.ntryDtls.txDtls.rltdPties.cdtr.pstlAdr.strtNm', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_cdtr_pstl_adr_twn_nm', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/TwnNm', 'stmt.ntry.ntryDtls.txDtls.rltdPties.cdtr.pstlAdr.twnNm', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_cdtr_acct_ccy', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/CdtrAcct/Ccy', 'stmt.ntry.ntryDtls.txDtls.rltdPties.cdtrAcct.ccy', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_cdtr_acct_id_iban', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/CdtrAcct/Id/IBAN', 'stmt.ntry.ntryDtls.txDtls.rltdPties.cdtrAcct.id.iban', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_cdtr_acct_id_othr_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/CdtrAcct/Id/Othr/Id', 'stmt.ntry.ntryDtls.txDtls.rltdPties.cdtrAcct.id.othr.id', 'VARCHAR', false, true);

-- ============================================================================
-- RELATED PARTIES - DEBTOR MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'tx_dtls_rltd_pties_dbtr_id_org_id_any_bic', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Id/OrgId/AnyBIC', 'stmt.ntry.ntryDtls.txDtls.rltdPties.dbtr.id.orgId.anyBic', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_dbtr_id_org_id_lei', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Id/OrgId/LEI', 'stmt.ntry.ntryDtls.txDtls.rltdPties.dbtr.id.orgId.lei', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_dbtr_id_org_id_othr_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Id/OrgId/Othr/Id', 'stmt.ntry.ntryDtls.txDtls.rltdPties.dbtr.id.orgId.othr.id', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_dbtr_nm', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Nm', 'stmt.ntry.ntryDtls.txDtls.rltdPties.dbtr.nm', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_dbtr_pstl_adr_bldg_nb', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/BldgNb', 'stmt.ntry.ntryDtls.txDtls.rltdPties.dbtr.pstlAdr.bldgNb', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_dbtr_pstl_adr_ctry', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/Ctry', 'stmt.ntry.ntryDtls.txDtls.rltdPties.dbtr.pstlAdr.ctry', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_dbtr_pstl_adr_pst_cd', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/PstCd', 'stmt.ntry.ntryDtls.txDtls.rltdPties.dbtr.pstlAdr.pstCd', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_dbtr_pstl_adr_strt_nm', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/StrtNm', 'stmt.ntry.ntryDtls.txDtls.rltdPties.dbtr.pstlAdr.strtNm', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_dbtr_pstl_adr_twn_nm', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/TwnNm', 'stmt.ntry.ntryDtls.txDtls.rltdPties.dbtr.pstlAdr.twnNm', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_dbtr_acct_ccy', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/DbtrAcct/Ccy', 'stmt.ntry.ntryDtls.txDtls.rltdPties.dbtrAcct.ccy', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_dbtr_acct_id_iban', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/DbtrAcct/Id/IBAN', 'stmt.ntry.ntryDtls.txDtls.rltdPties.dbtrAcct.id.iban', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_dbtr_acct_id_othr_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/DbtrAcct/Id/Othr/Id', 'stmt.ntry.ntryDtls.txDtls.rltdPties.dbtrAcct.id.othr.id', 'VARCHAR', false, true);

-- ============================================================================
-- RELATED PARTIES - OTHERS MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'tx_dtls_rltd_pties_initg_pty_nm', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/InitgPty/Nm', 'stmt.ntry.ntryDtls.txDtls.rltdPties.initgPty.nm', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_ultmt_cdtr_nm', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/UltmtCdtr/Nm', 'stmt.ntry.ntryDtls.txDtls.rltdPties.ultmtCdtr.nm', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rltd_pties_ultmt_dbtr_nm', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdPties/UltmtDbtr/Nm', 'stmt.ntry.ntryDtls.txDtls.rltdPties.ultmtDbtr.nm', 'VARCHAR', false, true);

-- ============================================================================
-- RELATED REMITTANCE INFO MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'tx_dtls_rltd_rmt_inf_rmt_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RltdRmtInf/RmtId', 'stmt.ntry.ntryDtls.txDtls.rltdRmtInf.rmtId', 'VARCHAR', false, true);

-- ============================================================================
-- REMITTANCE INFORMATION - STRUCTURED MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'tx_dtls_rmt_inf_strd_addtl_rmt_inf', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/AddtlRmtInf', 'stmt.ntry.ntryDtls.txDtls.rmtInf.strd.addtlRmtInf', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rmt_inf_strd_cdtr_ref_inf_ref', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/CdtrRefInf/Ref', 'stmt.ntry.ntryDtls.txDtls.rmtInf.strd.cdtrRefInf.ref', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rmt_inf_strd_cdtr_ref_inf_tp_cd_or_prtry_cd', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/CdtrRefInf/Tp/CdOrPrtry/Cd', 'stmt.ntry.ntryDtls.txDtls.rmtInf.strd.cdtrRefInf.tp.cdOrPrtry.cd', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rmt_inf_strd_invcee_nm', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/Invcee/Nm', 'stmt.ntry.ntryDtls.txDtls.rmtInf.strd.invcee.nm', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rmt_inf_strd_invcr_nm', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/Invcr/Nm', 'stmt.ntry.ntryDtls.txDtls.rmtInf.strd.invcr.nm', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rmt_inf_strd_rfrd_doc_amt_due_pybl_amt', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocAmt/DuePyblAmt', 'stmt.ntry.ntryDtls.txDtls.rmtInf.strd.rfrdDocAmt.duePyblAmt', 'DECIMAL', false, true),
('camt.053', 'tx_dtls_rmt_inf_strd_rfrd_doc_amt_due_pybl_amt_ccy', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocAmt/DuePyblAmt/@Ccy', 'stmt.ntry.ntryDtls.txDtls.rmtInf.strd.rfrdDocAmt.duePyblAmt.ccy', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rmt_inf_strd_rfrd_doc_amt_rmtd_amt', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocAmt/RmtdAmt', 'stmt.ntry.ntryDtls.txDtls.rmtInf.strd.rfrdDocAmt.rmtdAmt', 'DECIMAL', false, true),
('camt.053', 'tx_dtls_rmt_inf_strd_rfrd_doc_amt_rmtd_amt_ccy', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocAmt/RmtdAmt/@Ccy', 'stmt.ntry.ntryDtls.txDtls.rmtInf.strd.rfrdDocAmt.rmtdAmt.ccy', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rmt_inf_strd_rfrd_doc_inf_nb', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocInf/Nb', 'stmt.ntry.ntryDtls.txDtls.rmtInf.strd.rfrdDocInf.nb', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rmt_inf_strd_rfrd_doc_inf_rltd_dt', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocInf/RltdDt', 'stmt.ntry.ntryDtls.txDtls.rmtInf.strd.rfrdDocInf.rltdDt', 'DATE', false, true),
('camt.053', 'tx_dtls_rmt_inf_strd_rfrd_doc_inf_tp_cd_or_prtry_cd', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd', 'stmt.ntry.ntryDtls.txDtls.rmtInf.strd.rfrdDocInf.tp.cdOrPrtry.cd', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rmt_inf_ustrd', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Ustrd', 'stmt.ntry.ntryDtls.txDtls.rmtInf.ustrd', 'VARCHAR', false, true);

-- ============================================================================
-- RETURN INFORMATION MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'tx_dtls_rtr_inf_addtl_inf', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RtrInf/AddtlInf', 'stmt.ntry.ntryDtls.txDtls.rtrInf.addtlInf', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rtr_inf_rsn_cd', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RtrInf/Rsn/Cd', 'stmt.ntry.ntryDtls.txDtls.rtrInf.rsn.cd', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_rtr_inf_rsn_prtry', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/RtrInf/Rsn/Prtry', 'stmt.ntry.ntryDtls.txDtls.rtrInf.rsn.prtry', 'VARCHAR', false, true);

-- ============================================================================
-- TAX INFORMATION MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'tx_dtls_tax_cdtr_tax_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Tax/Cdtr/TaxId', 'stmt.ntry.ntryDtls.txDtls.tax.cdtr.taxId', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_tax_dbtr_tax_id', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Tax/Dbtr/TaxId', 'stmt.ntry.ntryDtls.txDtls.tax.dbtr.taxId', 'VARCHAR', false, true),
('camt.053', 'tx_dtls_tax_ttl_tax_amt', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Tax/TtlTaxAmt', 'stmt.ntry.ntryDtls.txDtls.tax.ttlTaxAmt', 'DECIMAL', false, true),
('camt.053', 'tx_dtls_tax_ttl_tax_amt_ccy', 'BkToCstmrStmt/Stmt/Ntry/NtryDtls/TxDtls/Tax/TtlTaxAmt/@Ccy', 'stmt.ntry.ntryDtls.txDtls.tax.ttlTaxAmt.ccy', 'VARCHAR', false, true);

-- ============================================================================
-- REPORTING SEQUENCE MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'rptg_seq_fr_to_seq_fr_seq', 'BkToCstmrStmt/Stmt/RptgSeq/FrToSeq/FrSeq', 'stmt.rptgSeq.frToSeq.frSeq', 'VARCHAR', false, true),
('camt.053', 'rptg_seq_fr_to_seq_to_seq', 'BkToCstmrStmt/Stmt/RptgSeq/FrToSeq/ToSeq', 'stmt.rptgSeq.frToSeq.toSeq', 'VARCHAR', false, true),
('camt.053', 'rptg_src_prtry', 'BkToCstmrStmt/Stmt/RptgSrc/Prtry', 'stmt.rptgSrc.prtry', 'VARCHAR', false, true);

-- ============================================================================
-- STATEMENT PAGINATION MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'stmt_pgntn_last_pg_ind', 'BkToCstmrStmt/Stmt/StmtPgntn/LastPgInd', 'stmt.stmtPgntn.lastPgInd', 'BOOLEAN', false, true),
('camt.053', 'stmt_pgntn_pg_nb', 'BkToCstmrStmt/Stmt/StmtPgntn/PgNb', 'stmt.stmtPgntn.pgNb', 'VARCHAR', false, true);

-- ============================================================================
-- TRANSACTION SUMMARY MAPPINGS
-- ============================================================================
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'txs_summry_ttl_cdt_ntries_nb_of_ntries', 'BkToCstmrStmt/Stmt/TxsSummry/TtlCdtNtries/NbOfNtries', 'stmt.txsSummry.ttlCdtNtries.nbOfNtries', 'INTEGER', false, true),
('camt.053', 'txs_summry_ttl_cdt_ntries_sum', 'BkToCstmrStmt/Stmt/TxsSummry/TtlCdtNtries/Sum', 'stmt.txsSummry.ttlCdtNtries.sum', 'DECIMAL', false, true),
('camt.053', 'txs_summry_ttl_dbt_ntries_nb_of_ntries', 'BkToCstmrStmt/Stmt/TxsSummry/TtlDbtNtries/NbOfNtries', 'stmt.txsSummry.ttlDbtNtries.nbOfNtries', 'INTEGER', false, true),
('camt.053', 'txs_summry_ttl_dbt_ntries_sum', 'BkToCstmrStmt/Stmt/TxsSummry/TtlDbtNtries/Sum', 'stmt.txsSummry.ttlDbtNtries.sum', 'DECIMAL', false, true),
('camt.053', 'txs_summry_ttl_ntries_nb_of_ntries', 'BkToCstmrStmt/Stmt/TxsSummry/TtlNtries/NbOfNtries', 'stmt.txsSummry.ttlNtries.nbOfNtries', 'INTEGER', false, true),
('camt.053', 'txs_summry_ttl_ntries_sum', 'BkToCstmrStmt/Stmt/TxsSummry/TtlNtries/Sum', 'stmt.txsSummry.ttlNtries.sum', 'DECIMAL', false, true),
('camt.053', 'txs_summry_ttl_ntries_ttl_net_ntry_amt', 'BkToCstmrStmt/Stmt/TxsSummry/TtlNtries/TtlNetNtry/Amt', 'stmt.txsSummry.ttlNtries.ttlNetNtry.amt', 'DECIMAL', false, true),
('camt.053', 'txs_summry_ttl_ntries_ttl_net_ntry_cdt_dbt_ind', 'BkToCstmrStmt/Stmt/TxsSummry/TtlNtries/TtlNetNtry/CdtDbtInd', 'stmt.txsSummry.ttlNtries.ttlNetNtry.cdtDbtInd', 'VARCHAR', false, true),
('camt.053', 'txs_summry_ttl_ntries_per_bk_tx_cd_nb_of_ntries', 'BkToCstmrStmt/Stmt/TxsSummry/TtlNtriesPerBkTxCd/NbOfNtries', 'stmt.txsSummry.ttlNtriesPerBkTxCd.nbOfNtries', 'INTEGER', false, true),
('camt.053', 'txs_summry_ttl_ntries_per_bk_tx_cd_sum', 'BkToCstmrStmt/Stmt/TxsSummry/TtlNtriesPerBkTxCd/Sum', 'stmt.txsSummry.ttlNtriesPerBkTxCd.sum', 'DECIMAL', false, true);

-- ============================================================================
-- SYSTEM MAPPINGS (Re-add system mappings that were preserved)
-- ============================================================================
-- These should already exist from the preserved DELETE clause above,
-- but add them if they're missing

INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'stg_id', '_GENERATED_UUID', '', 'VARCHAR', true, true)
ON CONFLICT (format_id, target_column) DO NOTHING;

INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'raw_id', '_RAW_ID', '', 'VARCHAR', true, true)
ON CONFLICT (format_id, target_column) DO NOTHING;

INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'message_type', 'messageType', '', 'VARCHAR', false, true)
ON CONFLICT (format_id, target_column) DO NOTHING;

INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', '_batch_id', '_BATCH_ID', '', 'VARCHAR', false, true)
ON CONFLICT (format_id, target_column) DO NOTHING;

INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', '_processed_at', '_PROCESSED_AT', '', 'TIMESTAMP', false, true)
ON CONFLICT (format_id, target_column) DO NOTHING;

INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'processing_status', '_PROCESSING_STATUS', '', 'VARCHAR', false, true)
ON CONFLICT (format_id, target_column) DO NOTHING;

INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active) VALUES
('camt.053', 'processed_to_gold_at', '_PROCESSED_TO_GOLD_AT', '', 'TIMESTAMP', false, true)
ON CONFLICT (format_id, target_column) DO NOTHING;

COMMIT;

-- ============================================================================
-- Verify coverage
-- ============================================================================
SELECT 'Standard fields (data elements)' as metric, COUNT(*) as count
FROM mapping.standard_fields
WHERE format_id = 'camt.053' AND data_type <> 'complex'
UNION ALL
SELECT 'Silver field mappings' as metric, COUNT(*) as count
FROM mapping.silver_field_mappings
WHERE format_id = 'camt.053' AND is_active = true
UNION ALL
SELECT 'Silver table columns' as metric, COUNT(*) as count
FROM information_schema.columns
WHERE table_schema = 'silver' AND table_name = 'stg_camt053';
