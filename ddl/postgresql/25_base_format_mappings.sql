-- GPS CDM - Base Format Mappings for ISO 20022
-- ============================================
-- These mappings are INHERITED by child formats (FEDWIRE, CHIPS, CHAPS, etc.)
-- through the mapping.format_inheritance table

-- =====================================================
-- PACS.008.BASE Silver Field Mappings
-- =====================================================

-- Clear any existing mappings for pacs.008.base
DELETE FROM mapping.silver_field_mappings WHERE format_id = 'pacs.008.base';

INSERT INTO mapping.silver_field_mappings
    (format_id, target_column, source_path, parser_path, data_type, ordinal_position, is_required, is_active)
VALUES
-- Group Header
('pacs.008.base', 'grp_hdr_msg_id', 'GrpHdr/MsgId', 'groupHeader.messageId', 'VARCHAR(35)', 1, true, true),
('pacs.008.base', 'grp_hdr_cre_dt_tm', 'GrpHdr/CreDtTm', 'groupHeader.creationDateTime', 'TIMESTAMP', 2, true, true),
('pacs.008.base', 'grp_hdr_nb_of_txs', 'GrpHdr/NbOfTxs', 'groupHeader.numberOfTransactions', 'INTEGER', 3, false, true),
('pacs.008.base', 'grp_hdr_ctrl_sum', 'GrpHdr/CtrlSum', 'groupHeader.controlSum', 'DECIMAL(18,4)', 4, false, true),
('pacs.008.base', 'grp_hdr_sttlm_mtd', 'GrpHdr/SttlmInf/SttlmMtd', 'groupHeader.settlementMethod', 'VARCHAR(4)', 5, false, true),
('pacs.008.base', 'grp_hdr_clr_sys_cd', 'GrpHdr/SttlmInf/ClrSys/Cd', 'groupHeader.clearingSystemCode', 'VARCHAR(35)', 6, false, true),
('pacs.008.base', 'grp_hdr_clr_sys_prtry', 'GrpHdr/SttlmInf/ClrSys/Prtry', 'groupHeader.clearingSystemProprietary', 'VARCHAR(35)', 7, false, true),

-- Instructing Agent
('pacs.008.base', 'instg_agt_bic', 'GrpHdr/InstgAgt/FinInstnId/BICFI', 'groupHeader.instructingAgent.bic', 'VARCHAR(11)', 10, false, true),
('pacs.008.base', 'instg_agt_lei', 'GrpHdr/InstgAgt/FinInstnId/LEI', 'groupHeader.instructingAgent.lei', 'VARCHAR(20)', 11, false, true),
('pacs.008.base', 'instg_agt_nm', 'GrpHdr/InstgAgt/FinInstnId/Nm', 'groupHeader.instructingAgent.name', 'VARCHAR(140)', 12, false, true),
('pacs.008.base', 'instg_agt_clr_sys_mmb_id', 'GrpHdr/InstgAgt/FinInstnId/ClrSysMmbId/MmbId', 'groupHeader.instructingAgent.clearingMemberId', 'VARCHAR(35)', 13, false, true),
('pacs.008.base', 'instg_agt_clr_sys_cd', 'GrpHdr/InstgAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd', 'groupHeader.instructingAgent.clearingSystemIdCode', 'VARCHAR(5)', 14, false, true),
('pacs.008.base', 'instg_agt_ctry', 'GrpHdr/InstgAgt/FinInstnId/PstlAdr/Ctry', 'groupHeader.instructingAgent.country', 'VARCHAR(2)', 15, false, true),

-- Instructed Agent
('pacs.008.base', 'instd_agt_bic', 'GrpHdr/InstdAgt/FinInstnId/BICFI', 'groupHeader.instructedAgent.bic', 'VARCHAR(11)', 20, false, true),
('pacs.008.base', 'instd_agt_lei', 'GrpHdr/InstdAgt/FinInstnId/LEI', 'groupHeader.instructedAgent.lei', 'VARCHAR(20)', 21, false, true),
('pacs.008.base', 'instd_agt_nm', 'GrpHdr/InstdAgt/FinInstnId/Nm', 'groupHeader.instructedAgent.name', 'VARCHAR(140)', 22, false, true),
('pacs.008.base', 'instd_agt_clr_sys_mmb_id', 'GrpHdr/InstdAgt/FinInstnId/ClrSysMmbId/MmbId', 'groupHeader.instructedAgent.clearingMemberId', 'VARCHAR(35)', 23, false, true),
('pacs.008.base', 'instd_agt_clr_sys_cd', 'GrpHdr/InstdAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd', 'groupHeader.instructedAgent.clearingSystemIdCode', 'VARCHAR(5)', 24, false, true),
('pacs.008.base', 'instd_agt_ctry', 'GrpHdr/InstdAgt/FinInstnId/PstlAdr/Ctry', 'groupHeader.instructedAgent.country', 'VARCHAR(2)', 25, false, true),

-- Payment Identification
('pacs.008.base', 'pmt_id_instr_id', 'CdtTrfTxInf/PmtId/InstrId', 'transaction.instructionId', 'VARCHAR(35)', 30, false, true),
('pacs.008.base', 'pmt_id_end_to_end_id', 'CdtTrfTxInf/PmtId/EndToEndId', 'transaction.endToEndId', 'VARCHAR(35)', 31, true, true),
('pacs.008.base', 'pmt_id_uetr', 'CdtTrfTxInf/PmtId/UETR', 'transaction.uetr', 'VARCHAR(36)', 32, false, true),
('pacs.008.base', 'pmt_id_tx_id', 'CdtTrfTxInf/PmtId/TxId', 'transaction.transactionId', 'VARCHAR(35)', 33, false, true),
('pacs.008.base', 'pmt_id_clr_sys_ref', 'CdtTrfTxInf/PmtId/ClrSysRef', 'transaction.clearingSystemReference', 'VARCHAR(35)', 34, false, true),

-- Payment Type Information
('pacs.008.base', 'pmt_tp_inf_instr_prty', 'CdtTrfTxInf/PmtTpInf/InstrPrty', 'transaction.instructionPriority', 'VARCHAR(4)', 40, false, true),
('pacs.008.base', 'pmt_tp_inf_svc_lvl_cd', 'CdtTrfTxInf/PmtTpInf/SvcLvl/Cd', 'transaction.serviceLevelCode', 'VARCHAR(4)', 41, false, true),
('pacs.008.base', 'pmt_tp_inf_svc_lvl_prtry', 'CdtTrfTxInf/PmtTpInf/SvcLvl/Prtry', 'transaction.serviceLevelProprietary', 'VARCHAR(35)', 42, false, true),
('pacs.008.base', 'pmt_tp_inf_lcl_instrm_cd', 'CdtTrfTxInf/PmtTpInf/LclInstrm/Cd', 'transaction.localInstrumentCode', 'VARCHAR(35)', 43, false, true),
('pacs.008.base', 'pmt_tp_inf_lcl_instrm_prtry', 'CdtTrfTxInf/PmtTpInf/LclInstrm/Prtry', 'transaction.localInstrumentProprietary', 'VARCHAR(35)', 44, false, true),
('pacs.008.base', 'pmt_tp_inf_ctgy_purp_cd', 'CdtTrfTxInf/PmtTpInf/CtgyPurp/Cd', 'transaction.categoryPurposeCode', 'VARCHAR(4)', 45, false, true),
('pacs.008.base', 'pmt_tp_inf_ctgy_purp_prtry', 'CdtTrfTxInf/PmtTpInf/CtgyPurp/Prtry', 'transaction.categoryPurposeProprietary', 'VARCHAR(35)', 46, false, true),
('pacs.008.base', 'pmt_tp_inf_clr_chanl', 'CdtTrfTxInf/PmtTpInf/ClrChanl', 'transaction.clearingChannel', 'VARCHAR(4)', 47, false, true),

-- Amounts
('pacs.008.base', 'intr_bk_sttlm_amt', 'CdtTrfTxInf/IntrBkSttlmAmt', 'transaction.interbankSettlementAmount', 'DECIMAL(18,4)', 50, true, true),
('pacs.008.base', 'intr_bk_sttlm_ccy', 'CdtTrfTxInf/IntrBkSttlmAmt/@Ccy', 'transaction.interbankSettlementCurrency', 'VARCHAR(3)', 51, true, true),
('pacs.008.base', 'intr_bk_sttlm_dt', 'CdtTrfTxInf/IntrBkSttlmDt', 'transaction.interbankSettlementDate', 'DATE', 52, true, true),
('pacs.008.base', 'instd_amt', 'CdtTrfTxInf/InstdAmt', 'transaction.instructedAmount', 'DECIMAL(18,4)', 53, false, true),
('pacs.008.base', 'instd_amt_ccy', 'CdtTrfTxInf/InstdAmt/@Ccy', 'transaction.instructedCurrency', 'VARCHAR(3)', 54, false, true),
('pacs.008.base', 'xchg_rate', 'CdtTrfTxInf/XchgRate', 'transaction.exchangeRate', 'DECIMAL(18,10)', 55, false, true),

-- Charges
('pacs.008.base', 'chrg_br', 'CdtTrfTxInf/ChrgBr', 'transaction.chargeBearer', 'VARCHAR(4)', 56, false, true),
('pacs.008.base', 'chrgs_inf_amt', 'CdtTrfTxInf/ChrgsInf/Amt', 'transaction.chargesAmount', 'DECIMAL(18,4)', 57, false, true),
('pacs.008.base', 'chrgs_inf_ccy', 'CdtTrfTxInf/ChrgsInf/Amt/@Ccy', 'transaction.chargesCurrency', 'VARCHAR(3)', 58, false, true),
('pacs.008.base', 'chrgs_inf_agt_bic', 'CdtTrfTxInf/ChrgsInf/Agt/FinInstnId/BICFI', 'transaction.chargesAgent.bic', 'VARCHAR(11)', 59, false, true),

-- Debtor
('pacs.008.base', 'dbtr_nm', 'CdtTrfTxInf/Dbtr/Nm', 'transaction.debtor.name', 'VARCHAR(140)', 60, true, true),
('pacs.008.base', 'dbtr_pstl_adr_dept', 'CdtTrfTxInf/Dbtr/PstlAdr/Dept', 'transaction.debtor.department', 'VARCHAR(70)', 61, false, true),
('pacs.008.base', 'dbtr_pstl_adr_strt_nm', 'CdtTrfTxInf/Dbtr/PstlAdr/StrtNm', 'transaction.debtor.streetName', 'VARCHAR(70)', 62, false, true),
('pacs.008.base', 'dbtr_pstl_adr_bldg_nb', 'CdtTrfTxInf/Dbtr/PstlAdr/BldgNb', 'transaction.debtor.buildingNumber', 'VARCHAR(16)', 63, false, true),
('pacs.008.base', 'dbtr_pstl_adr_pst_cd', 'CdtTrfTxInf/Dbtr/PstlAdr/PstCd', 'transaction.debtor.postalCode', 'VARCHAR(16)', 64, false, true),
('pacs.008.base', 'dbtr_pstl_adr_twn_nm', 'CdtTrfTxInf/Dbtr/PstlAdr/TwnNm', 'transaction.debtor.townName', 'VARCHAR(35)', 65, false, true),
('pacs.008.base', 'dbtr_pstl_adr_ctry_sub_dvsn', 'CdtTrfTxInf/Dbtr/PstlAdr/CtrySubDvsn', 'transaction.debtor.countrySubDivision', 'VARCHAR(35)', 66, false, true),
('pacs.008.base', 'dbtr_pstl_adr_ctry', 'CdtTrfTxInf/Dbtr/PstlAdr/Ctry', 'transaction.debtor.country', 'VARCHAR(2)', 67, false, true),
('pacs.008.base', 'dbtr_pstl_adr_adr_line', 'CdtTrfTxInf/Dbtr/PstlAdr/AdrLine', 'transaction.debtor.addressLines', 'TEXT[]', 68, false, true),
('pacs.008.base', 'dbtr_id_org_id_any_bic', 'CdtTrfTxInf/Dbtr/Id/OrgId/AnyBIC', 'transaction.debtor.orgBic', 'VARCHAR(11)', 69, false, true),
('pacs.008.base', 'dbtr_id_org_id_lei', 'CdtTrfTxInf/Dbtr/Id/OrgId/LEI', 'transaction.debtor.lei', 'VARCHAR(20)', 70, false, true),
('pacs.008.base', 'dbtr_id_org_id_othr_id', 'CdtTrfTxInf/Dbtr/Id/OrgId/Othr/Id', 'transaction.debtor.orgOtherId', 'VARCHAR(35)', 71, false, true),
('pacs.008.base', 'dbtr_id_org_id_othr_schme_nm_cd', 'CdtTrfTxInf/Dbtr/Id/OrgId/Othr/SchmeNm/Cd', 'transaction.debtor.orgOtherSchemeCode', 'VARCHAR(4)', 72, false, true),
('pacs.008.base', 'dbtr_id_org_id_othr_schme_nm_prtry', 'CdtTrfTxInf/Dbtr/Id/OrgId/Othr/SchmeNm/Prtry', 'transaction.debtor.orgOtherSchemeProprietary', 'VARCHAR(35)', 73, false, true),
('pacs.008.base', 'dbtr_id_org_id_othr_issr', 'CdtTrfTxInf/Dbtr/Id/OrgId/Othr/Issr', 'transaction.debtor.orgOtherIssuer', 'VARCHAR(35)', 74, false, true),
('pacs.008.base', 'dbtr_id_prvt_id_othr_id', 'CdtTrfTxInf/Dbtr/Id/PrvtId/Othr/Id', 'transaction.debtor.privateOtherId', 'VARCHAR(35)', 75, false, true),
('pacs.008.base', 'dbtr_id_prvt_id_othr_schme_nm_cd', 'CdtTrfTxInf/Dbtr/Id/PrvtId/Othr/SchmeNm/Cd', 'transaction.debtor.privateOtherSchemeCode', 'VARCHAR(4)', 76, false, true),
('pacs.008.base', 'dbtr_ctct_dtls_nm', 'CdtTrfTxInf/Dbtr/CtctDtls/Nm', 'transaction.debtor.contactName', 'VARCHAR(140)', 77, false, true),
('pacs.008.base', 'dbtr_ctct_dtls_phne_nb', 'CdtTrfTxInf/Dbtr/CtctDtls/PhneNb', 'transaction.debtor.contactPhone', 'VARCHAR(35)', 78, false, true),
('pacs.008.base', 'dbtr_ctct_dtls_email_adr', 'CdtTrfTxInf/Dbtr/CtctDtls/EmailAdr', 'transaction.debtor.contactEmail', 'VARCHAR(256)', 79, false, true),

-- Debtor Account
('pacs.008.base', 'dbtr_acct_id_iban', 'CdtTrfTxInf/DbtrAcct/Id/IBAN', 'transaction.debtorAccount.iban', 'VARCHAR(34)', 80, false, true),
('pacs.008.base', 'dbtr_acct_id_othr_id', 'CdtTrfTxInf/DbtrAcct/Id/Othr/Id', 'transaction.debtorAccount.otherId', 'VARCHAR(34)', 81, false, true),
('pacs.008.base', 'dbtr_acct_id_othr_schme_nm_cd', 'CdtTrfTxInf/DbtrAcct/Id/Othr/SchmeNm/Cd', 'transaction.debtorAccount.schemeCode', 'VARCHAR(4)', 82, false, true),
('pacs.008.base', 'dbtr_acct_id_othr_schme_nm_prtry', 'CdtTrfTxInf/DbtrAcct/Id/Othr/SchmeNm/Prtry', 'transaction.debtorAccount.schemeProprietary', 'VARCHAR(35)', 83, false, true),
('pacs.008.base', 'dbtr_acct_tp_cd', 'CdtTrfTxInf/DbtrAcct/Tp/Cd', 'transaction.debtorAccount.typeCode', 'VARCHAR(4)', 84, false, true),
('pacs.008.base', 'dbtr_acct_tp_prtry', 'CdtTrfTxInf/DbtrAcct/Tp/Prtry', 'transaction.debtorAccount.typeProprietary', 'VARCHAR(35)', 85, false, true),
('pacs.008.base', 'dbtr_acct_ccy', 'CdtTrfTxInf/DbtrAcct/Ccy', 'transaction.debtorAccount.currency', 'VARCHAR(3)', 86, false, true),
('pacs.008.base', 'dbtr_acct_nm', 'CdtTrfTxInf/DbtrAcct/Nm', 'transaction.debtorAccount.name', 'VARCHAR(70)', 87, false, true),
('pacs.008.base', 'dbtr_acct_prxy_tp_cd', 'CdtTrfTxInf/DbtrAcct/Prxy/Tp/Cd', 'transaction.debtorAccount.proxyTypeCode', 'VARCHAR(4)', 88, false, true),
('pacs.008.base', 'dbtr_acct_prxy_id', 'CdtTrfTxInf/DbtrAcct/Prxy/Id', 'transaction.debtorAccount.proxyId', 'VARCHAR(256)', 89, false, true),

-- Debtor Agent
('pacs.008.base', 'dbtr_agt_bic', 'CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI', 'transaction.debtorAgent.bic', 'VARCHAR(11)', 90, false, true),
('pacs.008.base', 'dbtr_agt_lei', 'CdtTrfTxInf/DbtrAgt/FinInstnId/LEI', 'transaction.debtorAgent.lei', 'VARCHAR(20)', 91, false, true),
('pacs.008.base', 'dbtr_agt_nm', 'CdtTrfTxInf/DbtrAgt/FinInstnId/Nm', 'transaction.debtorAgent.name', 'VARCHAR(140)', 92, false, true),
('pacs.008.base', 'dbtr_agt_clr_sys_mmb_id', 'CdtTrfTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'transaction.debtorAgent.clearingMemberId', 'VARCHAR(35)', 93, false, true),
('pacs.008.base', 'dbtr_agt_clr_sys_cd', 'CdtTrfTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd', 'transaction.debtorAgent.clearingSystemIdCode', 'VARCHAR(5)', 94, false, true),
('pacs.008.base', 'dbtr_agt_pstl_adr_strt_nm', 'CdtTrfTxInf/DbtrAgt/FinInstnId/PstlAdr/StrtNm', 'transaction.debtorAgent.streetName', 'VARCHAR(70)', 95, false, true),
('pacs.008.base', 'dbtr_agt_pstl_adr_twn_nm', 'CdtTrfTxInf/DbtrAgt/FinInstnId/PstlAdr/TwnNm', 'transaction.debtorAgent.townName', 'VARCHAR(35)', 96, false, true),
('pacs.008.base', 'dbtr_agt_pstl_adr_ctry_sub_dvsn', 'CdtTrfTxInf/DbtrAgt/FinInstnId/PstlAdr/CtrySubDvsn', 'transaction.debtorAgent.countrySubDivision', 'VARCHAR(35)', 97, false, true),
('pacs.008.base', 'dbtr_agt_pstl_adr_ctry', 'CdtTrfTxInf/DbtrAgt/FinInstnId/PstlAdr/Ctry', 'transaction.debtorAgent.country', 'VARCHAR(2)', 98, false, true),
('pacs.008.base', 'dbtr_agt_brnch_id', 'CdtTrfTxInf/DbtrAgt/BrnchId/Id', 'transaction.debtorAgent.branchId', 'VARCHAR(35)', 99, false, true),

-- Creditor Agent
('pacs.008.base', 'cdtr_agt_bic', 'CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI', 'transaction.creditorAgent.bic', 'VARCHAR(11)', 100, false, true),
('pacs.008.base', 'cdtr_agt_lei', 'CdtTrfTxInf/CdtrAgt/FinInstnId/LEI', 'transaction.creditorAgent.lei', 'VARCHAR(20)', 101, false, true),
('pacs.008.base', 'cdtr_agt_nm', 'CdtTrfTxInf/CdtrAgt/FinInstnId/Nm', 'transaction.creditorAgent.name', 'VARCHAR(140)', 102, false, true),
('pacs.008.base', 'cdtr_agt_clr_sys_mmb_id', 'CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'transaction.creditorAgent.clearingMemberId', 'VARCHAR(35)', 103, false, true),
('pacs.008.base', 'cdtr_agt_clr_sys_cd', 'CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd', 'transaction.creditorAgent.clearingSystemIdCode', 'VARCHAR(5)', 104, false, true),
('pacs.008.base', 'cdtr_agt_pstl_adr_strt_nm', 'CdtTrfTxInf/CdtrAgt/FinInstnId/PstlAdr/StrtNm', 'transaction.creditorAgent.streetName', 'VARCHAR(70)', 105, false, true),
('pacs.008.base', 'cdtr_agt_pstl_adr_twn_nm', 'CdtTrfTxInf/CdtrAgt/FinInstnId/PstlAdr/TwnNm', 'transaction.creditorAgent.townName', 'VARCHAR(35)', 106, false, true),
('pacs.008.base', 'cdtr_agt_pstl_adr_ctry_sub_dvsn', 'CdtTrfTxInf/CdtrAgt/FinInstnId/PstlAdr/CtrySubDvsn', 'transaction.creditorAgent.countrySubDivision', 'VARCHAR(35)', 107, false, true),
('pacs.008.base', 'cdtr_agt_pstl_adr_ctry', 'CdtTrfTxInf/CdtrAgt/FinInstnId/PstlAdr/Ctry', 'transaction.creditorAgent.country', 'VARCHAR(2)', 108, false, true),
('pacs.008.base', 'cdtr_agt_brnch_id', 'CdtTrfTxInf/CdtrAgt/BrnchId/Id', 'transaction.creditorAgent.branchId', 'VARCHAR(35)', 109, false, true),

-- Creditor
('pacs.008.base', 'cdtr_nm', 'CdtTrfTxInf/Cdtr/Nm', 'transaction.creditor.name', 'VARCHAR(140)', 110, true, true),
('pacs.008.base', 'cdtr_pstl_adr_dept', 'CdtTrfTxInf/Cdtr/PstlAdr/Dept', 'transaction.creditor.department', 'VARCHAR(70)', 111, false, true),
('pacs.008.base', 'cdtr_pstl_adr_strt_nm', 'CdtTrfTxInf/Cdtr/PstlAdr/StrtNm', 'transaction.creditor.streetName', 'VARCHAR(70)', 112, false, true),
('pacs.008.base', 'cdtr_pstl_adr_bldg_nb', 'CdtTrfTxInf/Cdtr/PstlAdr/BldgNb', 'transaction.creditor.buildingNumber', 'VARCHAR(16)', 113, false, true),
('pacs.008.base', 'cdtr_pstl_adr_pst_cd', 'CdtTrfTxInf/Cdtr/PstlAdr/PstCd', 'transaction.creditor.postalCode', 'VARCHAR(16)', 114, false, true),
('pacs.008.base', 'cdtr_pstl_adr_twn_nm', 'CdtTrfTxInf/Cdtr/PstlAdr/TwnNm', 'transaction.creditor.townName', 'VARCHAR(35)', 115, false, true),
('pacs.008.base', 'cdtr_pstl_adr_ctry_sub_dvsn', 'CdtTrfTxInf/Cdtr/PstlAdr/CtrySubDvsn', 'transaction.creditor.countrySubDivision', 'VARCHAR(35)', 116, false, true),
('pacs.008.base', 'cdtr_pstl_adr_ctry', 'CdtTrfTxInf/Cdtr/PstlAdr/Ctry', 'transaction.creditor.country', 'VARCHAR(2)', 117, false, true),
('pacs.008.base', 'cdtr_pstl_adr_adr_line', 'CdtTrfTxInf/Cdtr/PstlAdr/AdrLine', 'transaction.creditor.addressLines', 'TEXT[]', 118, false, true),
('pacs.008.base', 'cdtr_id_org_id_any_bic', 'CdtTrfTxInf/Cdtr/Id/OrgId/AnyBIC', 'transaction.creditor.orgBic', 'VARCHAR(11)', 119, false, true),
('pacs.008.base', 'cdtr_id_org_id_lei', 'CdtTrfTxInf/Cdtr/Id/OrgId/LEI', 'transaction.creditor.lei', 'VARCHAR(20)', 120, false, true),
('pacs.008.base', 'cdtr_id_org_id_othr_id', 'CdtTrfTxInf/Cdtr/Id/OrgId/Othr/Id', 'transaction.creditor.orgOtherId', 'VARCHAR(35)', 121, false, true),
('pacs.008.base', 'cdtr_id_org_id_othr_schme_nm_cd', 'CdtTrfTxInf/Cdtr/Id/OrgId/Othr/SchmeNm/Cd', 'transaction.creditor.orgOtherSchemeCode', 'VARCHAR(4)', 122, false, true),
('pacs.008.base', 'cdtr_id_prvt_id_othr_id', 'CdtTrfTxInf/Cdtr/Id/PrvtId/Othr/Id', 'transaction.creditor.privateOtherId', 'VARCHAR(35)', 123, false, true),
('pacs.008.base', 'cdtr_id_prvt_id_othr_schme_nm_cd', 'CdtTrfTxInf/Cdtr/Id/PrvtId/Othr/SchmeNm/Cd', 'transaction.creditor.privateOtherSchemeCode', 'VARCHAR(4)', 124, false, true),

-- Creditor Account
('pacs.008.base', 'cdtr_acct_id_iban', 'CdtTrfTxInf/CdtrAcct/Id/IBAN', 'transaction.creditorAccount.iban', 'VARCHAR(34)', 130, false, true),
('pacs.008.base', 'cdtr_acct_id_othr_id', 'CdtTrfTxInf/CdtrAcct/Id/Othr/Id', 'transaction.creditorAccount.otherId', 'VARCHAR(34)', 131, false, true),
('pacs.008.base', 'cdtr_acct_id_othr_schme_nm_cd', 'CdtTrfTxInf/CdtrAcct/Id/Othr/SchmeNm/Cd', 'transaction.creditorAccount.schemeCode', 'VARCHAR(4)', 132, false, true),
('pacs.008.base', 'cdtr_acct_tp_cd', 'CdtTrfTxInf/CdtrAcct/Tp/Cd', 'transaction.creditorAccount.typeCode', 'VARCHAR(4)', 133, false, true),
('pacs.008.base', 'cdtr_acct_ccy', 'CdtTrfTxInf/CdtrAcct/Ccy', 'transaction.creditorAccount.currency', 'VARCHAR(3)', 134, false, true),
('pacs.008.base', 'cdtr_acct_nm', 'CdtTrfTxInf/CdtrAcct/Nm', 'transaction.creditorAccount.name', 'VARCHAR(70)', 135, false, true),
('pacs.008.base', 'cdtr_acct_prxy_tp_cd', 'CdtTrfTxInf/CdtrAcct/Prxy/Tp/Cd', 'transaction.creditorAccount.proxyTypeCode', 'VARCHAR(4)', 136, false, true),
('pacs.008.base', 'cdtr_acct_prxy_id', 'CdtTrfTxInf/CdtrAcct/Prxy/Id', 'transaction.creditorAccount.proxyId', 'VARCHAR(256)', 137, false, true),

-- Intermediary Agents
('pacs.008.base', 'intrmy_agt1_bic', 'CdtTrfTxInf/IntrmyAgt1/FinInstnId/BICFI', 'transaction.intermediaryAgent1.bic', 'VARCHAR(11)', 140, false, true),
('pacs.008.base', 'intrmy_agt1_lei', 'CdtTrfTxInf/IntrmyAgt1/FinInstnId/LEI', 'transaction.intermediaryAgent1.lei', 'VARCHAR(20)', 141, false, true),
('pacs.008.base', 'intrmy_agt1_nm', 'CdtTrfTxInf/IntrmyAgt1/FinInstnId/Nm', 'transaction.intermediaryAgent1.name', 'VARCHAR(140)', 142, false, true),
('pacs.008.base', 'intrmy_agt1_clr_sys_mmb_id', 'CdtTrfTxInf/IntrmyAgt1/FinInstnId/ClrSysMmbId/MmbId', 'transaction.intermediaryAgent1.clearingMemberId', 'VARCHAR(35)', 143, false, true),
('pacs.008.base', 'intrmy_agt1_clr_sys_cd', 'CdtTrfTxInf/IntrmyAgt1/FinInstnId/ClrSysMmbId/ClrSysId/Cd', 'transaction.intermediaryAgent1.clearingSystemIdCode', 'VARCHAR(5)', 144, false, true),
('pacs.008.base', 'intrmy_agt1_ctry', 'CdtTrfTxInf/IntrmyAgt1/FinInstnId/PstlAdr/Ctry', 'transaction.intermediaryAgent1.country', 'VARCHAR(2)', 145, false, true),
('pacs.008.base', 'intrmy_agt1_acct_id', 'CdtTrfTxInf/IntrmyAgt1Acct/Id/Othr/Id', 'transaction.intermediaryAgent1.accountId', 'VARCHAR(34)', 146, false, true),
('pacs.008.base', 'intrmy_agt2_bic', 'CdtTrfTxInf/IntrmyAgt2/FinInstnId/BICFI', 'transaction.intermediaryAgent2.bic', 'VARCHAR(11)', 150, false, true),
('pacs.008.base', 'intrmy_agt2_lei', 'CdtTrfTxInf/IntrmyAgt2/FinInstnId/LEI', 'transaction.intermediaryAgent2.lei', 'VARCHAR(20)', 151, false, true),
('pacs.008.base', 'intrmy_agt2_nm', 'CdtTrfTxInf/IntrmyAgt2/FinInstnId/Nm', 'transaction.intermediaryAgent2.name', 'VARCHAR(140)', 152, false, true),
('pacs.008.base', 'intrmy_agt2_clr_sys_mmb_id', 'CdtTrfTxInf/IntrmyAgt2/FinInstnId/ClrSysMmbId/MmbId', 'transaction.intermediaryAgent2.clearingMemberId', 'VARCHAR(35)', 153, false, true),
('pacs.008.base', 'intrmy_agt2_ctry', 'CdtTrfTxInf/IntrmyAgt2/FinInstnId/PstlAdr/Ctry', 'transaction.intermediaryAgent2.country', 'VARCHAR(2)', 154, false, true),
('pacs.008.base', 'intrmy_agt2_acct_id', 'CdtTrfTxInf/IntrmyAgt2Acct/Id/Othr/Id', 'transaction.intermediaryAgent2.accountId', 'VARCHAR(34)', 155, false, true),
('pacs.008.base', 'intrmy_agt3_bic', 'CdtTrfTxInf/IntrmyAgt3/FinInstnId/BICFI', 'transaction.intermediaryAgent3.bic', 'VARCHAR(11)', 156, false, true),
('pacs.008.base', 'intrmy_agt3_clr_sys_mmb_id', 'CdtTrfTxInf/IntrmyAgt3/FinInstnId/ClrSysMmbId/MmbId', 'transaction.intermediaryAgent3.clearingMemberId', 'VARCHAR(35)', 157, false, true),
('pacs.008.base', 'intrmy_agt3_ctry', 'CdtTrfTxInf/IntrmyAgt3/FinInstnId/PstlAdr/Ctry', 'transaction.intermediaryAgent3.country', 'VARCHAR(2)', 158, false, true),

-- Ultimate Parties
('pacs.008.base', 'ultmt_dbtr_nm', 'CdtTrfTxInf/UltmtDbtr/Nm', 'transaction.ultimateDebtor.name', 'VARCHAR(140)', 160, false, true),
('pacs.008.base', 'ultmt_dbtr_pstl_adr_ctry', 'CdtTrfTxInf/UltmtDbtr/PstlAdr/Ctry', 'transaction.ultimateDebtor.country', 'VARCHAR(2)', 161, false, true),
('pacs.008.base', 'ultmt_dbtr_id_org_id_lei', 'CdtTrfTxInf/UltmtDbtr/Id/OrgId/LEI', 'transaction.ultimateDebtor.lei', 'VARCHAR(20)', 162, false, true),
('pacs.008.base', 'ultmt_dbtr_id_org_id_othr_id', 'CdtTrfTxInf/UltmtDbtr/Id/OrgId/Othr/Id', 'transaction.ultimateDebtor.orgOtherId', 'VARCHAR(35)', 163, false, true),
('pacs.008.base', 'ultmt_dbtr_id_prvt_id_othr_id', 'CdtTrfTxInf/UltmtDbtr/Id/PrvtId/Othr/Id', 'transaction.ultimateDebtor.privateOtherId', 'VARCHAR(35)', 164, false, true),
('pacs.008.base', 'ultmt_cdtr_nm', 'CdtTrfTxInf/UltmtCdtr/Nm', 'transaction.ultimateCreditor.name', 'VARCHAR(140)', 165, false, true),
('pacs.008.base', 'ultmt_cdtr_pstl_adr_ctry', 'CdtTrfTxInf/UltmtCdtr/PstlAdr/Ctry', 'transaction.ultimateCreditor.country', 'VARCHAR(2)', 166, false, true),
('pacs.008.base', 'ultmt_cdtr_id_org_id_lei', 'CdtTrfTxInf/UltmtCdtr/Id/OrgId/LEI', 'transaction.ultimateCreditor.lei', 'VARCHAR(20)', 167, false, true),
('pacs.008.base', 'ultmt_cdtr_id_org_id_othr_id', 'CdtTrfTxInf/UltmtCdtr/Id/OrgId/Othr/Id', 'transaction.ultimateCreditor.orgOtherId', 'VARCHAR(35)', 168, false, true),
('pacs.008.base', 'ultmt_cdtr_id_prvt_id_othr_id', 'CdtTrfTxInf/UltmtCdtr/Id/PrvtId/Othr/Id', 'transaction.ultimateCreditor.privateOtherId', 'VARCHAR(35)', 169, false, true),

-- Remittance Information
('pacs.008.base', 'rmt_inf_ustrd', 'CdtTrfTxInf/RmtInf/Ustrd', 'transaction.remittanceUnstructured', 'TEXT[]', 170, false, true),
('pacs.008.base', 'rmt_inf_strd_rfrd_doc_tp_cd_or_prtry', 'CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd', 'transaction.remittanceReferredDocTypeCode', 'VARCHAR(35)', 171, false, true),
('pacs.008.base', 'rmt_inf_strd_rfrd_doc_nb', 'CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Nb', 'transaction.remittanceReferredDocNumber', 'VARCHAR(35)', 172, false, true),
('pacs.008.base', 'rmt_inf_strd_rfrd_doc_rltd_dt', 'CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/RltdDt', 'transaction.remittanceReferredDocDate', 'DATE', 173, false, true),
('pacs.008.base', 'rmt_inf_strd_cdtr_ref_inf_tp_cd_or_prtry', 'CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Tp/CdOrPrtry/Cd', 'transaction.remittanceCreditorRefTypeCode', 'VARCHAR(35)', 174, false, true),
('pacs.008.base', 'rmt_inf_strd_cdtr_ref_inf_ref', 'CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Ref', 'transaction.remittanceCreditorRef', 'VARCHAR(35)', 175, false, true),
('pacs.008.base', 'rmt_inf_strd', 'CdtTrfTxInf/RmtInf/Strd', 'transaction.remittanceStructured', 'JSONB', 176, false, true),

-- Purpose & Regulatory
('pacs.008.base', 'purp_cd', 'CdtTrfTxInf/Purp/Cd', 'transaction.purposeCode', 'VARCHAR(4)', 180, false, true),
('pacs.008.base', 'purp_prtry', 'CdtTrfTxInf/Purp/Prtry', 'transaction.purposeProprietary', 'VARCHAR(35)', 181, false, true),
('pacs.008.base', 'rgltry_rptg', 'CdtTrfTxInf/RgltryRptg', 'transaction.regulatoryReporting', 'JSONB', 182, false, true),
('pacs.008.base', 'tax', 'CdtTrfTxInf/Tax', 'transaction.tax', 'JSONB', 183, false, true),
('pacs.008.base', 'splmtry_data', 'CdtTrfTxInf/SplmtryData', 'transaction.supplementaryData', 'JSONB', 184, false, true),
('pacs.008.base', 'scheme_identifiers', 'CdtTrfTxInf/_SchemeIdentifiers', 'transaction.schemeIdentifiers', 'JSONB', 185, false, true),

-- Processing metadata
('pacs.008.base', 'source_format', '_SOURCE_FORMAT', '_sourceFormat', 'VARCHAR(20)', 200, true, true),
('pacs.008.base', 'raw_id', '_RAW_ID', '_rawId', 'VARCHAR(36)', 201, true, true),
('pacs.008.base', '_batch_id', '_BATCH_ID', '_batchId', 'VARCHAR(36)', 202, true, true);

-- =====================================================
-- PACS.008.BASE Gold Field Mappings
-- Maps from Silver columns to CDM Gold tables
-- =====================================================

DELETE FROM mapping.gold_field_mappings WHERE format_id = 'pacs.008.base';

-- CDM Payment Instruction
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, transform_expression, default_value, is_active)
VALUES
-- Core identifiers
('pacs.008.base', 'cdm_payment_instruction', 'instruction_id', '_GENERATED_UUID', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'instruction_id_ext', 'pmt_id_instr_id', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'message_id', 'grp_hdr_msg_id', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'end_to_end_id', 'pmt_id_end_to_end_id', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'uetr', 'pmt_id_uetr', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'transaction_id', 'pmt_id_tx_id', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'clearing_system_reference', 'pmt_id_clr_sys_ref', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'payment_id', 'grp_hdr_msg_id', NULL, NULL, NULL, true),

-- Timestamps
('pacs.008.base', 'cdm_payment_instruction', 'creation_datetime', 'grp_hdr_cre_dt_tm', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'settlement_date', 'intr_bk_sttlm_dt', NULL, NULL, NULL, true),

-- Amounts
('pacs.008.base', 'cdm_payment_instruction', 'interbank_settlement_amount', 'intr_bk_sttlm_amt', NULL, 'TO_DECIMAL', NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'interbank_settlement_currency', 'intr_bk_sttlm_ccy', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'instructed_amount', 'instd_amt', NULL, 'TO_DECIMAL', NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'instructed_currency', 'instd_amt_ccy', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'exchange_rate', 'xchg_rate', NULL, 'TO_DECIMAL', NULL, true),

-- Payment Type Info
('pacs.008.base', 'cdm_payment_instruction', 'priority', 'pmt_tp_inf_instr_prty', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'service_level', 'pmt_tp_inf_svc_lvl_cd', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'local_instrument', 'pmt_tp_inf_lcl_instrm_cd', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'category_purpose', 'pmt_tp_inf_ctgy_purp_cd', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'clearing_channel', 'pmt_tp_inf_clr_chanl', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'clearing_system', 'grp_hdr_clr_sys_cd', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'settlement_method', 'grp_hdr_sttlm_mtd', NULL, NULL, NULL, true),

-- Charges
('pacs.008.base', 'cdm_payment_instruction', 'charge_bearer', 'chrg_br', NULL, NULL, NULL, true),

-- Purpose & Remittance
('pacs.008.base', 'cdm_payment_instruction', 'purpose', 'purp_cd', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'remittance_unstructured', 'rmt_inf_ustrd', NULL, 'TO_ARRAY', NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'remittance_structured', 'rmt_inf_strd', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'regulatory_reporting', 'rgltry_rptg', NULL, NULL, NULL, true),

-- Classification
('pacs.008.base', 'cdm_payment_instruction', 'payment_type', '''CREDIT_TRANSFER''', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'scheme_code', '''pacs.008''', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'source_message_type', 'source_format', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'direction', '''OUTBOUND''', NULL, NULL, 'OUTBOUND', true),
('pacs.008.base', 'cdm_payment_instruction', 'number_of_transactions', 'grp_hdr_nb_of_txs', NULL, NULL, '1', true),

-- Cross-border flag derived from country comparison
('pacs.008.base', 'cdm_payment_instruction', 'cross_border_flag', 'CASE WHEN dbtr_pstl_adr_ctry != cdtr_pstl_adr_ctry THEN true ELSE false END', NULL, NULL, 'false', true),

-- Lineage
('pacs.008.base', 'cdm_payment_instruction', 'lineage_batch_id', '_batch_id', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'source_stg_id', '_CONTEXT.stg_id', NULL, NULL, NULL, true),
('pacs.008.base', 'cdm_payment_instruction', 'is_current', 'true', NULL, NULL, 'true', true),

-- CDM Party - Debtor
('pacs.008.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'name', 'dbtr_nm', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'street_name', 'dbtr_pstl_adr_strt_nm', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'building_number', 'dbtr_pstl_adr_bldg_nb', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'postal_code', 'dbtr_pstl_adr_pst_cd', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'town_name', 'dbtr_pstl_adr_twn_nm', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'country_sub_division', 'dbtr_pstl_adr_ctry_sub_dvsn', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'country', 'dbtr_pstl_adr_ctry', 'DEBTOR', NULL, 'XX', true),
('pacs.008.base', 'cdm_party', 'address_lines', 'dbtr_pstl_adr_adr_line', 'DEBTOR', 'TO_ARRAY', NULL, true),
('pacs.008.base', 'cdm_party', 'org_id_bic', 'dbtr_id_org_id_any_bic', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'org_id_lei', 'dbtr_id_org_id_lei', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'org_id_other', 'dbtr_id_org_id_othr_id', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'org_id_other_scheme', 'dbtr_id_org_id_othr_schme_nm_cd', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'private_id_other', 'dbtr_id_prvt_id_othr_id', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'contact_name', 'dbtr_ctct_dtls_nm', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'contact_phone', 'dbtr_ctct_dtls_phne_nb', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'contact_email', 'dbtr_ctct_dtls_email_adr', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'role', '''DEBTOR''', 'DEBTOR', NULL, 'DEBTOR', true),
('pacs.008.base', 'cdm_party', 'source_message_type', 'source_format', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'source_stg_id', '_CONTEXT.stg_id', 'DEBTOR', NULL, NULL, true),

-- CDM Party - Creditor
('pacs.008.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'name', 'cdtr_nm', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'street_name', 'cdtr_pstl_adr_strt_nm', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'building_number', 'cdtr_pstl_adr_bldg_nb', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'postal_code', 'cdtr_pstl_adr_pst_cd', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'town_name', 'cdtr_pstl_adr_twn_nm', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'country_sub_division', 'cdtr_pstl_adr_ctry_sub_dvsn', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'country', 'cdtr_pstl_adr_ctry', 'CREDITOR', NULL, 'XX', true),
('pacs.008.base', 'cdm_party', 'address_lines', 'cdtr_pstl_adr_adr_line', 'CREDITOR', 'TO_ARRAY', NULL, true),
('pacs.008.base', 'cdm_party', 'org_id_bic', 'cdtr_id_org_id_any_bic', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'org_id_lei', 'cdtr_id_org_id_lei', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'org_id_other', 'cdtr_id_org_id_othr_id', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'org_id_other_scheme', 'cdtr_id_org_id_othr_schme_nm_cd', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'private_id_other', 'cdtr_id_prvt_id_othr_id', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'role', '''CREDITOR''', 'CREDITOR', NULL, 'CREDITOR', true),
('pacs.008.base', 'cdm_party', 'source_message_type', 'source_format', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'source_stg_id', '_CONTEXT.stg_id', 'CREDITOR', NULL, NULL, true),

-- CDM Party - Ultimate Debtor
('pacs.008.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'ULTIMATE_DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'name', 'ultmt_dbtr_nm', 'ULTIMATE_DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'country', 'ultmt_dbtr_pstl_adr_ctry', 'ULTIMATE_DEBTOR', NULL, 'XX', true),
('pacs.008.base', 'cdm_party', 'org_id_lei', 'ultmt_dbtr_id_org_id_lei', 'ULTIMATE_DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'org_id_other', 'ultmt_dbtr_id_org_id_othr_id', 'ULTIMATE_DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'private_id_other', 'ultmt_dbtr_id_prvt_id_othr_id', 'ULTIMATE_DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'role', '''ULTIMATE_DEBTOR''', 'ULTIMATE_DEBTOR', NULL, 'ULTIMATE_DEBTOR', true),
('pacs.008.base', 'cdm_party', 'source_message_type', 'source_format', 'ULTIMATE_DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'source_stg_id', '_CONTEXT.stg_id', 'ULTIMATE_DEBTOR', NULL, NULL, true),

-- CDM Party - Ultimate Creditor
('pacs.008.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'ULTIMATE_CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'name', 'ultmt_cdtr_nm', 'ULTIMATE_CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'country', 'ultmt_cdtr_pstl_adr_ctry', 'ULTIMATE_CREDITOR', NULL, 'XX', true),
('pacs.008.base', 'cdm_party', 'org_id_lei', 'ultmt_cdtr_id_org_id_lei', 'ULTIMATE_CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'org_id_other', 'ultmt_cdtr_id_org_id_othr_id', 'ULTIMATE_CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'private_id_other', 'ultmt_cdtr_id_prvt_id_othr_id', 'ULTIMATE_CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'role', '''ULTIMATE_CREDITOR''', 'ULTIMATE_CREDITOR', NULL, 'ULTIMATE_CREDITOR', true),
('pacs.008.base', 'cdm_party', 'source_message_type', 'source_format', 'ULTIMATE_CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_party', 'source_stg_id', '_CONTEXT.stg_id', 'ULTIMATE_CREDITOR', NULL, NULL, true),

-- CDM Account - Debtor Account
('pacs.008.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'iban', 'dbtr_acct_id_iban', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'account_number', 'dbtr_acct_id_othr_id', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'account_type', 'dbtr_acct_tp_cd', 'DEBTOR', NULL, 'CACC', true),
('pacs.008.base', 'cdm_account', 'currency', 'dbtr_acct_ccy', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'name', 'dbtr_acct_nm', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'proxy_type', 'dbtr_acct_prxy_tp_cd', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'proxy_id', 'dbtr_acct_prxy_id', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'role', '''DEBTOR''', 'DEBTOR', NULL, 'DEBTOR', true),
('pacs.008.base', 'cdm_account', 'source_message_type', 'source_format', 'DEBTOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'source_stg_id', '_CONTEXT.stg_id', 'DEBTOR', NULL, NULL, true),

-- CDM Account - Creditor Account
('pacs.008.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'iban', 'cdtr_acct_id_iban', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'account_number', 'cdtr_acct_id_othr_id', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'account_type', 'cdtr_acct_tp_cd', 'CREDITOR', NULL, 'CACC', true),
('pacs.008.base', 'cdm_account', 'currency', 'cdtr_acct_ccy', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'name', 'cdtr_acct_nm', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'proxy_type', 'cdtr_acct_prxy_tp_cd', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'proxy_id', 'cdtr_acct_prxy_id', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'role', '''CREDITOR''', 'CREDITOR', NULL, 'CREDITOR', true),
('pacs.008.base', 'cdm_account', 'source_message_type', 'source_format', 'CREDITOR', NULL, NULL, true),
('pacs.008.base', 'cdm_account', 'source_stg_id', '_CONTEXT.stg_id', 'CREDITOR', NULL, NULL, true),

-- CDM Financial Institution - Debtor Agent
('pacs.008.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'DEBTOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'bic', 'dbtr_agt_bic', 'DEBTOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'lei', 'dbtr_agt_lei', 'DEBTOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'name', 'dbtr_agt_nm', 'DEBTOR_AGENT', 'COALESCE_BIC', NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'clearing_system_member_id', 'dbtr_agt_clr_sys_mmb_id', 'DEBTOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'clearing_system_id', 'dbtr_agt_clr_sys_cd', 'DEBTOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'street_name', 'dbtr_agt_pstl_adr_strt_nm', 'DEBTOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'town_name', 'dbtr_agt_pstl_adr_twn_nm', 'DEBTOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'country_sub_division', 'dbtr_agt_pstl_adr_ctry_sub_dvsn', 'DEBTOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'country', 'dbtr_agt_pstl_adr_ctry', 'DEBTOR_AGENT', 'COUNTRY_FROM_BIC', 'XX', true),
('pacs.008.base', 'cdm_financial_institution', 'branch_id', 'dbtr_agt_brnch_id', 'DEBTOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'role', '''DEBTOR_AGENT''', 'DEBTOR_AGENT', NULL, 'DEBTOR_AGENT', true),
('pacs.008.base', 'cdm_financial_institution', 'source_message_type', 'source_format', 'DEBTOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'DEBTOR_AGENT', NULL, NULL, true),

-- CDM Financial Institution - Creditor Agent
('pacs.008.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'CREDITOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'bic', 'cdtr_agt_bic', 'CREDITOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'lei', 'cdtr_agt_lei', 'CREDITOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'name', 'cdtr_agt_nm', 'CREDITOR_AGENT', 'COALESCE_BIC', NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'clearing_system_member_id', 'cdtr_agt_clr_sys_mmb_id', 'CREDITOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'clearing_system_id', 'cdtr_agt_clr_sys_cd', 'CREDITOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'street_name', 'cdtr_agt_pstl_adr_strt_nm', 'CREDITOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'town_name', 'cdtr_agt_pstl_adr_twn_nm', 'CREDITOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'country_sub_division', 'cdtr_agt_pstl_adr_ctry_sub_dvsn', 'CREDITOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'country', 'cdtr_agt_pstl_adr_ctry', 'CREDITOR_AGENT', 'COUNTRY_FROM_BIC', 'XX', true),
('pacs.008.base', 'cdm_financial_institution', 'branch_id', 'cdtr_agt_brnch_id', 'CREDITOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'role', '''CREDITOR_AGENT''', 'CREDITOR_AGENT', NULL, 'CREDITOR_AGENT', true),
('pacs.008.base', 'cdm_financial_institution', 'source_message_type', 'source_format', 'CREDITOR_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'CREDITOR_AGENT', NULL, NULL, true),

-- CDM Financial Institution - Intermediary Agent 1
('pacs.008.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'INTERMEDIARY_AGENT1', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'bic', 'intrmy_agt1_bic', 'INTERMEDIARY_AGENT1', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'lei', 'intrmy_agt1_lei', 'INTERMEDIARY_AGENT1', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'name', 'intrmy_agt1_nm', 'INTERMEDIARY_AGENT1', 'COALESCE_BIC', NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'clearing_system_member_id', 'intrmy_agt1_clr_sys_mmb_id', 'INTERMEDIARY_AGENT1', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'clearing_system_id', 'intrmy_agt1_clr_sys_cd', 'INTERMEDIARY_AGENT1', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'country', 'intrmy_agt1_ctry', 'INTERMEDIARY_AGENT1', 'COUNTRY_FROM_BIC', 'XX', true),
('pacs.008.base', 'cdm_financial_institution', 'role', '''INTERMEDIARY_AGENT1''', 'INTERMEDIARY_AGENT1', NULL, 'INTERMEDIARY_AGENT1', true),
('pacs.008.base', 'cdm_financial_institution', 'source_message_type', 'source_format', 'INTERMEDIARY_AGENT1', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'INTERMEDIARY_AGENT1', NULL, NULL, true),

-- CDM Financial Institution - Intermediary Agent 2
('pacs.008.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'INTERMEDIARY_AGENT2', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'bic', 'intrmy_agt2_bic', 'INTERMEDIARY_AGENT2', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'lei', 'intrmy_agt2_lei', 'INTERMEDIARY_AGENT2', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'name', 'intrmy_agt2_nm', 'INTERMEDIARY_AGENT2', 'COALESCE_BIC', NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'clearing_system_member_id', 'intrmy_agt2_clr_sys_mmb_id', 'INTERMEDIARY_AGENT2', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'country', 'intrmy_agt2_ctry', 'INTERMEDIARY_AGENT2', 'COUNTRY_FROM_BIC', 'XX', true),
('pacs.008.base', 'cdm_financial_institution', 'role', '''INTERMEDIARY_AGENT2''', 'INTERMEDIARY_AGENT2', NULL, 'INTERMEDIARY_AGENT2', true),
('pacs.008.base', 'cdm_financial_institution', 'source_message_type', 'source_format', 'INTERMEDIARY_AGENT2', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'INTERMEDIARY_AGENT2', NULL, NULL, true),

-- CDM Financial Institution - Instructing Agent
('pacs.008.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'INSTRUCTING_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'bic', 'instg_agt_bic', 'INSTRUCTING_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'lei', 'instg_agt_lei', 'INSTRUCTING_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'name', 'instg_agt_nm', 'INSTRUCTING_AGENT', 'COALESCE_BIC', NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'clearing_system_member_id', 'instg_agt_clr_sys_mmb_id', 'INSTRUCTING_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'clearing_system_id', 'instg_agt_clr_sys_cd', 'INSTRUCTING_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'country', 'instg_agt_ctry', 'INSTRUCTING_AGENT', 'COUNTRY_FROM_BIC', 'XX', true),
('pacs.008.base', 'cdm_financial_institution', 'role', '''INSTRUCTING_AGENT''', 'INSTRUCTING_AGENT', NULL, 'INSTRUCTING_AGENT', true),
('pacs.008.base', 'cdm_financial_institution', 'source_message_type', 'source_format', 'INSTRUCTING_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'INSTRUCTING_AGENT', NULL, NULL, true),

-- CDM Financial Institution - Instructed Agent
('pacs.008.base', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'INSTRUCTED_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'bic', 'instd_agt_bic', 'INSTRUCTED_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'lei', 'instd_agt_lei', 'INSTRUCTED_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'name', 'instd_agt_nm', 'INSTRUCTED_AGENT', 'COALESCE_BIC', NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'clearing_system_member_id', 'instd_agt_clr_sys_mmb_id', 'INSTRUCTED_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'clearing_system_id', 'instd_agt_clr_sys_cd', 'INSTRUCTED_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'country', 'instd_agt_ctry', 'INSTRUCTED_AGENT', 'COUNTRY_FROM_BIC', 'XX', true),
('pacs.008.base', 'cdm_financial_institution', 'role', '''INSTRUCTED_AGENT''', 'INSTRUCTED_AGENT', NULL, 'INSTRUCTED_AGENT', true),
('pacs.008.base', 'cdm_financial_institution', 'source_message_type', 'source_format', 'INSTRUCTED_AGENT', NULL, NULL, true),
('pacs.008.base', 'cdm_financial_institution', 'source_stg_id', '_CONTEXT.stg_id', 'INSTRUCTED_AGENT', NULL, NULL, true);

-- Verify counts
SELECT 'pacs.008.base Silver mappings: ' || COUNT(*) FROM mapping.silver_field_mappings WHERE format_id = 'pacs.008.base';
SELECT 'pacs.008.base Gold mappings: ' || COUNT(*) FROM mapping.gold_field_mappings WHERE format_id = 'pacs.008.base';
