-- =============================================================================
-- Additional Base Format Mappings for ISO 20022 Message Types
-- Creates Silver and Gold mappings for: pacs.002.base, pacs.004.base,
-- pain.008.base, camt.056.base, and Gold mappings for pacs.009.base
-- =============================================================================

BEGIN;

-- =============================================================================
-- SECTION 1: pacs.002.base (Payment Status Report) Silver Mappings
-- =============================================================================

-- Clear existing mappings first
DELETE FROM mapping.silver_field_mappings WHERE format_id = 'pacs.002.base';

INSERT INTO mapping.silver_field_mappings
    (format_id, target_column, source_path, parser_path, is_required, is_active)
VALUES
    -- System fields
    ('pacs.002.base', 'stg_id', '_SYSTEM', '_GENERATED_UUID', true, true),
    ('pacs.002.base', 'raw_id', '_SYSTEM', '_RAW_ID', true, true),
    ('pacs.002.base', 'source_format', '_SYSTEM', '_SOURCE_FORMAT', true, true),
    ('pacs.002.base', '_batch_id', '_SYSTEM', '_BATCH_ID', false, true),

    -- Group Header
    ('pacs.002.base', 'grp_hdr_msg_id', 'GrpHdr/MsgId', 'messageId', true, true),
    ('pacs.002.base', 'grp_hdr_cre_dt_tm', 'GrpHdr/CreDtTm', 'creationDateTime', true, true),

    -- Original Group Information and Status
    ('pacs.002.base', 'orgnl_grp_inf_orgnl_msg_id', 'OrgnlGrpInfAndSts/OrgnlMsgId', 'originalMessageId', false, true),
    ('pacs.002.base', 'orgnl_grp_inf_orgnl_msg_nm_id', 'OrgnlGrpInfAndSts/OrgnlMsgNmId', 'originalMessageNameId', false, true),
    ('pacs.002.base', 'orgnl_grp_inf_orgnl_cre_dt_tm', 'OrgnlGrpInfAndSts/OrgnlCreDtTm', 'originalCreationDateTime', false, true),
    ('pacs.002.base', 'orgnl_grp_inf_orgnl_nb_of_txs', 'OrgnlGrpInfAndSts/OrgnlNbOfTxs', 'originalNumberOfTransactions', false, true),
    ('pacs.002.base', 'orgnl_grp_inf_grp_sts', 'OrgnlGrpInfAndSts/GrpSts', 'groupStatus', false, true),
    ('pacs.002.base', 'orgnl_grp_inf_sts_rsn_cd', 'OrgnlGrpInfAndSts/StsRsnInf/Rsn/Cd', 'statusReasonCode', false, true),
    ('pacs.002.base', 'orgnl_grp_inf_sts_rsn_addtl_inf', 'OrgnlGrpInfAndSts/StsRsnInf/AddtlInf', 'statusReasonAdditionalInfo', false, true),

    -- Transaction Information and Status
    ('pacs.002.base', 'tx_inf_sts_id', 'TxInfAndSts/StsId', 'statusId', false, true),
    ('pacs.002.base', 'tx_inf_orgnl_instr_id', 'TxInfAndSts/OrgnlInstrId', 'originalInstructionId', false, true),
    ('pacs.002.base', 'tx_inf_orgnl_end_to_end_id', 'TxInfAndSts/OrgnlEndToEndId', 'originalEndToEndId', false, true),
    ('pacs.002.base', 'tx_inf_orgnl_uetr', 'TxInfAndSts/OrgnlUETR', 'originalUETR', false, true),
    ('pacs.002.base', 'tx_inf_tx_sts', 'TxInfAndSts/TxSts', 'transactionStatus', false, true),
    ('pacs.002.base', 'tx_inf_sts_rsn_cd', 'TxInfAndSts/StsRsnInf/Rsn/Cd', 'txStatusReasonCode', false, true),
    ('pacs.002.base', 'tx_inf_sts_rsn_addtl_inf', 'TxInfAndSts/StsRsnInf/AddtlInf', 'txStatusReasonAdditionalInfo', false, true),
    ('pacs.002.base', 'tx_inf_accpt_dt_tm', 'TxInfAndSts/AccptncDtTm', 'acceptanceDateTime', false, true),
    ('pacs.002.base', 'tx_inf_acct_svcr_ref', 'TxInfAndSts/AcctSvcrRef', 'accountServicerReference', false, true),
    ('pacs.002.base', 'tx_inf_clr_sys_ref', 'TxInfAndSts/ClrSysRef', 'clearingSystemReference', false, true),

    -- Original Transaction Reference
    ('pacs.002.base', 'orgnl_tx_ref_intr_bk_sttlm_amt', 'TxInfAndSts/OrgnlTxRef/IntrBkSttlmAmt', 'originalSettlementAmount', false, true),
    ('pacs.002.base', 'orgnl_tx_ref_intr_bk_sttlm_ccy', 'TxInfAndSts/OrgnlTxRef/IntrBkSttlmAmt/@Ccy', 'originalSettlementCurrency', false, true),
    ('pacs.002.base', 'orgnl_tx_ref_intr_bk_sttlm_dt', 'TxInfAndSts/OrgnlTxRef/IntrBkSttlmDt', 'originalSettlementDate', false, true),
    ('pacs.002.base', 'orgnl_tx_ref_reqd_exctn_dt', 'TxInfAndSts/OrgnlTxRef/ReqdExctnDt/Dt', 'originalRequestedExecutionDate', false, true),
    ('pacs.002.base', 'orgnl_tx_ref_dbtr_nm', 'TxInfAndSts/OrgnlTxRef/Dbtr/Nm', 'originalDebtorName', false, true),
    ('pacs.002.base', 'orgnl_tx_ref_dbtr_acct_id_iban', 'TxInfAndSts/OrgnlTxRef/DbtrAcct/Id/IBAN', 'originalDebtorIBAN', false, true),
    ('pacs.002.base', 'orgnl_tx_ref_dbtr_acct_id_othr', 'TxInfAndSts/OrgnlTxRef/DbtrAcct/Id/Othr/Id', 'originalDebtorOtherAccount', false, true),
    ('pacs.002.base', 'orgnl_tx_ref_dbtr_agt_bic', 'TxInfAndSts/OrgnlTxRef/DbtrAgt/FinInstnId/BICFI', 'originalDebtorAgentBIC', false, true),
    ('pacs.002.base', 'orgnl_tx_ref_cdtr_nm', 'TxInfAndSts/OrgnlTxRef/Cdtr/Nm', 'originalCreditorName', false, true),
    ('pacs.002.base', 'orgnl_tx_ref_cdtr_acct_id_iban', 'TxInfAndSts/OrgnlTxRef/CdtrAcct/Id/IBAN', 'originalCreditorIBAN', false, true),
    ('pacs.002.base', 'orgnl_tx_ref_cdtr_acct_id_othr', 'TxInfAndSts/OrgnlTxRef/CdtrAcct/Id/Othr/Id', 'originalCreditorOtherAccount', false, true),
    ('pacs.002.base', 'orgnl_tx_ref_cdtr_agt_bic', 'TxInfAndSts/OrgnlTxRef/CdtrAgt/FinInstnId/BICFI', 'originalCreditorAgentBIC', false, true)
ON CONFLICT (format_id, target_column) DO UPDATE
SET source_path = EXCLUDED.source_path,
    parser_path = EXCLUDED.parser_path,
    is_required = EXCLUDED.is_required,
    is_active = true;

-- =============================================================================
-- SECTION 2: pacs.004.base (Payment Return) Silver Mappings
-- =============================================================================

DELETE FROM mapping.silver_field_mappings WHERE format_id = 'pacs.004.base';

INSERT INTO mapping.silver_field_mappings
    (format_id, target_column, source_path, parser_path, is_required, is_active)
VALUES
    -- System fields
    ('pacs.004.base', 'stg_id', '_SYSTEM', '_GENERATED_UUID', true, true),
    ('pacs.004.base', 'raw_id', '_SYSTEM', '_RAW_ID', true, true),
    ('pacs.004.base', 'source_format', '_SYSTEM', '_SOURCE_FORMAT', true, true),
    ('pacs.004.base', '_batch_id', '_SYSTEM', '_BATCH_ID', false, true),

    -- Group Header
    ('pacs.004.base', 'grp_hdr_msg_id', 'GrpHdr/MsgId', 'messageId', true, true),
    ('pacs.004.base', 'grp_hdr_cre_dt_tm', 'GrpHdr/CreDtTm', 'creationDateTime', true, true),
    ('pacs.004.base', 'grp_hdr_nb_of_txs', 'GrpHdr/NbOfTxs', 'numberOfTransactions', false, true),
    ('pacs.004.base', 'grp_hdr_sttlm_mtd', 'GrpHdr/SttlmInf/SttlmMtd', 'settlementMethod', false, true),
    ('pacs.004.base', 'grp_hdr_clr_sys_cd', 'GrpHdr/SttlmInf/ClrSys/Cd', 'clearingSystemCode', false, true),

    -- Original Group Information
    ('pacs.004.base', 'orgnl_grp_inf_orgnl_msg_id', 'OrgnlGrpInf/OrgnlMsgId', 'originalMessageId', false, true),
    ('pacs.004.base', 'orgnl_grp_inf_orgnl_msg_nm_id', 'OrgnlGrpInf/OrgnlMsgNmId', 'originalMessageNameId', false, true),
    ('pacs.004.base', 'orgnl_grp_inf_orgnl_cre_dt_tm', 'OrgnlGrpInf/OrgnlCreDtTm', 'originalCreationDateTime', false, true),

    -- Transaction Information
    ('pacs.004.base', 'tx_inf_rtr_id', 'TxInf/RtrId', 'returnId', false, true),
    ('pacs.004.base', 'tx_inf_orgnl_instr_id', 'TxInf/OrgnlInstrId', 'originalInstructionId', false, true),
    ('pacs.004.base', 'tx_inf_orgnl_end_to_end_id', 'TxInf/OrgnlEndToEndId', 'originalEndToEndId', false, true),
    ('pacs.004.base', 'tx_inf_orgnl_tx_id', 'TxInf/OrgnlTxId', 'originalTransactionId', false, true),
    ('pacs.004.base', 'tx_inf_orgnl_uetr', 'TxInf/OrgnlUETR', 'originalUETR', false, true),
    ('pacs.004.base', 'tx_inf_orgnl_clr_sys_ref', 'TxInf/OrgnlClrSysRef', 'originalClearingSystemReference', false, true),

    -- Return Reason
    ('pacs.004.base', 'tx_inf_rtr_rsn_cd', 'TxInf/RtrRsnInf/Rsn/Cd', 'returnReasonCode', false, true),
    ('pacs.004.base', 'tx_inf_rtr_rsn_prtry', 'TxInf/RtrRsnInf/Rsn/Prtry', 'returnReasonProprietary', false, true),
    ('pacs.004.base', 'tx_inf_rtr_rsn_addtl_inf', 'TxInf/RtrRsnInf/AddtlInf', 'returnReasonAdditionalInfo', false, true),

    -- Return Amount
    ('pacs.004.base', 'tx_inf_rtrd_intr_bk_sttlm_amt', 'TxInf/RtrdIntrBkSttlmAmt', 'returnedSettlementAmount', false, true),
    ('pacs.004.base', 'tx_inf_rtrd_intr_bk_sttlm_ccy', 'TxInf/RtrdIntrBkSttlmAmt/@Ccy', 'returnedSettlementCurrency', false, true),
    ('pacs.004.base', 'tx_inf_intr_bk_sttlm_dt', 'TxInf/IntrBkSttlmDt', 'interbankSettlementDate', false, true),

    -- Original Transaction Reference
    ('pacs.004.base', 'orgnl_tx_ref_intr_bk_sttlm_amt', 'TxInf/OrgnlTxRef/IntrBkSttlmAmt', 'originalSettlementAmount', false, true),
    ('pacs.004.base', 'orgnl_tx_ref_intr_bk_sttlm_ccy', 'TxInf/OrgnlTxRef/IntrBkSttlmAmt/@Ccy', 'originalSettlementCurrency', false, true),
    ('pacs.004.base', 'orgnl_tx_ref_intr_bk_sttlm_dt', 'TxInf/OrgnlTxRef/IntrBkSttlmDt', 'originalSettlementDate', false, true),

    -- Original Debtor
    ('pacs.004.base', 'orgnl_tx_ref_dbtr_nm', 'TxInf/OrgnlTxRef/Dbtr/Nm', 'originalDebtorName', false, true),
    ('pacs.004.base', 'orgnl_tx_ref_dbtr_pstl_adr_ctry', 'TxInf/OrgnlTxRef/Dbtr/PstlAdr/Ctry', 'originalDebtorCountry', false, true),
    ('pacs.004.base', 'orgnl_tx_ref_dbtr_acct_id_iban', 'TxInf/OrgnlTxRef/DbtrAcct/Id/IBAN', 'originalDebtorIBAN', false, true),
    ('pacs.004.base', 'orgnl_tx_ref_dbtr_acct_id_othr', 'TxInf/OrgnlTxRef/DbtrAcct/Id/Othr/Id', 'originalDebtorOtherAccount', false, true),
    ('pacs.004.base', 'orgnl_tx_ref_dbtr_agt_bic', 'TxInf/OrgnlTxRef/DbtrAgt/FinInstnId/BICFI', 'originalDebtorAgentBIC', false, true),
    ('pacs.004.base', 'orgnl_tx_ref_dbtr_agt_clr_sys_mmb_id', 'TxInf/OrgnlTxRef/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'originalDebtorAgentMemberId', false, true),

    -- Original Creditor
    ('pacs.004.base', 'orgnl_tx_ref_cdtr_nm', 'TxInf/OrgnlTxRef/Cdtr/Nm', 'originalCreditorName', false, true),
    ('pacs.004.base', 'orgnl_tx_ref_cdtr_pstl_adr_ctry', 'TxInf/OrgnlTxRef/Cdtr/PstlAdr/Ctry', 'originalCreditorCountry', false, true),
    ('pacs.004.base', 'orgnl_tx_ref_cdtr_acct_id_iban', 'TxInf/OrgnlTxRef/CdtrAcct/Id/IBAN', 'originalCreditorIBAN', false, true),
    ('pacs.004.base', 'orgnl_tx_ref_cdtr_acct_id_othr', 'TxInf/OrgnlTxRef/CdtrAcct/Id/Othr/Id', 'originalCreditorOtherAccount', false, true),
    ('pacs.004.base', 'orgnl_tx_ref_cdtr_agt_bic', 'TxInf/OrgnlTxRef/CdtrAgt/FinInstnId/BICFI', 'originalCreditorAgentBIC', false, true),
    ('pacs.004.base', 'orgnl_tx_ref_cdtr_agt_clr_sys_mmb_id', 'TxInf/OrgnlTxRef/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'originalCreditorAgentMemberId', false, true),

    -- Instructing/Instructed Agents
    ('pacs.004.base', 'instg_agt_bic', 'GrpHdr/InstgAgt/FinInstnId/BICFI', 'instructingAgentBIC', false, true),
    ('pacs.004.base', 'instg_agt_clr_sys_mmb_id', 'GrpHdr/InstgAgt/FinInstnId/ClrSysMmbId/MmbId', 'instructingAgentMemberId', false, true),
    ('pacs.004.base', 'instd_agt_bic', 'GrpHdr/InstdAgt/FinInstnId/BICFI', 'instructedAgentBIC', false, true),
    ('pacs.004.base', 'instd_agt_clr_sys_mmb_id', 'GrpHdr/InstdAgt/FinInstnId/ClrSysMmbId/MmbId', 'instructedAgentMemberId', false, true),

    -- Remittance
    ('pacs.004.base', 'rmt_inf_ustrd', 'TxInf/OrgnlTxRef/RmtInf/Ustrd', 'remittanceUnstructured', false, true)
ON CONFLICT (format_id, target_column) DO UPDATE
SET source_path = EXCLUDED.source_path,
    parser_path = EXCLUDED.parser_path,
    is_required = EXCLUDED.is_required,
    is_active = true;

-- =============================================================================
-- SECTION 3: pain.008.base (Direct Debit Initiation) Silver Mappings
-- =============================================================================

DELETE FROM mapping.silver_field_mappings WHERE format_id = 'pain.008.base';

INSERT INTO mapping.silver_field_mappings
    (format_id, target_column, source_path, parser_path, is_required, is_active)
VALUES
    -- System fields
    ('pain.008.base', 'stg_id', '_SYSTEM', '_GENERATED_UUID', true, true),
    ('pain.008.base', 'raw_id', '_SYSTEM', '_RAW_ID', true, true),
    ('pain.008.base', 'source_format', '_SYSTEM', '_SOURCE_FORMAT', true, true),
    ('pain.008.base', '_batch_id', '_SYSTEM', '_BATCH_ID', false, true),

    -- Group Header
    ('pain.008.base', 'grp_hdr_msg_id', 'GrpHdr/MsgId', 'messageId', true, true),
    ('pain.008.base', 'grp_hdr_cre_dt_tm', 'GrpHdr/CreDtTm', 'creationDateTime', true, true),
    ('pain.008.base', 'grp_hdr_nb_of_txs', 'GrpHdr/NbOfTxs', 'numberOfTransactions', false, true),
    ('pain.008.base', 'grp_hdr_ctrl_sum', 'GrpHdr/CtrlSum', 'controlSum', false, true),
    ('pain.008.base', 'grp_hdr_initg_pty_nm', 'GrpHdr/InitgPty/Nm', 'initiatingPartyName', false, true),
    ('pain.008.base', 'grp_hdr_initg_pty_id_org_id_othr_id', 'GrpHdr/InitgPty/Id/OrgId/Othr/Id', 'initiatingPartyOrgId', false, true),

    -- Payment Information
    ('pain.008.base', 'pmt_inf_id', 'PmtInf/PmtInfId', 'paymentInformationId', false, true),
    ('pain.008.base', 'pmt_mtd', 'PmtInf/PmtMtd', 'paymentMethod', false, true),
    ('pain.008.base', 'pmt_tp_inf_svc_lvl_cd', 'PmtInf/PmtTpInf/SvcLvl/Cd', 'serviceLevel', false, true),
    ('pain.008.base', 'pmt_tp_inf_lcl_instrm_cd', 'PmtInf/PmtTpInf/LclInstrm/Cd', 'localInstrument', false, true),
    ('pain.008.base', 'pmt_tp_inf_seq_tp', 'PmtInf/PmtTpInf/SeqTp', 'sequenceType', false, true),
    ('pain.008.base', 'pmt_tp_inf_ctgy_purp_cd', 'PmtInf/PmtTpInf/CtgyPurp/Cd', 'categoryPurpose', false, true),
    ('pain.008.base', 'reqd_colltn_dt', 'PmtInf/ReqdColltnDt', 'requestedCollectionDate', false, true),

    -- Creditor
    ('pain.008.base', 'cdtr_nm', 'PmtInf/Cdtr/Nm', 'creditorName', false, true),
    ('pain.008.base', 'cdtr_pstl_adr_strt_nm', 'PmtInf/Cdtr/PstlAdr/StrtNm', 'creditorStreet', false, true),
    ('pain.008.base', 'cdtr_pstl_adr_bldg_nb', 'PmtInf/Cdtr/PstlAdr/BldgNb', 'creditorBuildingNumber', false, true),
    ('pain.008.base', 'cdtr_pstl_adr_pst_cd', 'PmtInf/Cdtr/PstlAdr/PstCd', 'creditorPostalCode', false, true),
    ('pain.008.base', 'cdtr_pstl_adr_twn_nm', 'PmtInf/Cdtr/PstlAdr/TwnNm', 'creditorCity', false, true),
    ('pain.008.base', 'cdtr_pstl_adr_ctry', 'PmtInf/Cdtr/PstlAdr/Ctry', 'creditorCountry', false, true),
    ('pain.008.base', 'cdtr_id_prvt_id_othr_id', 'PmtInf/Cdtr/Id/PrvtId/Othr/Id', 'creditorPrivateId', false, true),
    ('pain.008.base', 'cdtr_id_prvt_id_othr_schme_nm_prtry', 'PmtInf/Cdtr/Id/PrvtId/Othr/SchmeNm/Prtry', 'creditorIdSchemeProprietary', false, true),
    ('pain.008.base', 'cdtr_id_org_id_othr_id', 'PmtInf/Cdtr/Id/OrgId/Othr/Id', 'creditorOrgId', false, true),
    ('pain.008.base', 'cdtr_acct_id_iban', 'PmtInf/CdtrAcct/Id/IBAN', 'creditorIBAN', false, true),
    ('pain.008.base', 'cdtr_acct_id_othr_id', 'PmtInf/CdtrAcct/Id/Othr/Id', 'creditorOtherAccount', false, true),
    ('pain.008.base', 'cdtr_acct_ccy', 'PmtInf/CdtrAcct/Ccy', 'creditorAccountCurrency', false, true),
    ('pain.008.base', 'cdtr_agt_bic', 'PmtInf/CdtrAgt/FinInstnId/BICFI', 'creditorAgentBIC', false, true),
    ('pain.008.base', 'cdtr_agt_clr_sys_mmb_id', 'PmtInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'creditorAgentMemberId', false, true),

    -- Direct Debit Transaction Information
    ('pain.008.base', 'drct_dbt_tx_inf_pmt_id_instr_id', 'PmtInf/DrctDbtTxInf/PmtId/InstrId', 'instructionId', false, true),
    ('pain.008.base', 'drct_dbt_tx_inf_pmt_id_end_to_end_id', 'PmtInf/DrctDbtTxInf/PmtId/EndToEndId', 'endToEndId', true, true),
    ('pain.008.base', 'drct_dbt_tx_inf_instd_amt', 'PmtInf/DrctDbtTxInf/InstdAmt', 'amount', true, true),
    ('pain.008.base', 'drct_dbt_tx_inf_instd_amt_ccy', 'PmtInf/DrctDbtTxInf/InstdAmt/@Ccy', 'currency', true, true),
    ('pain.008.base', 'drct_dbt_tx_inf_chrgbr', 'PmtInf/DrctDbtTxInf/ChrgBr', 'chargeBearer', false, true),

    -- Mandate Related Information
    ('pain.008.base', 'drct_dbt_tx_inf_mndt_id', 'PmtInf/DrctDbtTxInf/DrctDbtTx/MndtRltdInf/MndtId', 'mandateId', false, true),
    ('pain.008.base', 'drct_dbt_tx_inf_mndt_dt_of_sgntr', 'PmtInf/DrctDbtTxInf/DrctDbtTx/MndtRltdInf/DtOfSgntr', 'mandateSignatureDate', false, true),
    ('pain.008.base', 'drct_dbt_tx_inf_mndt_amdmnt_ind', 'PmtInf/DrctDbtTxInf/DrctDbtTx/MndtRltdInf/AmdmntInd', 'mandateAmendmentIndicator', false, true),

    -- Debtor
    ('pain.008.base', 'dbtr_agt_bic', 'PmtInf/DrctDbtTxInf/DbtrAgt/FinInstnId/BICFI', 'debtorAgentBIC', false, true),
    ('pain.008.base', 'dbtr_agt_clr_sys_mmb_id', 'PmtInf/DrctDbtTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'debtorAgentMemberId', false, true),
    ('pain.008.base', 'dbtr_nm', 'PmtInf/DrctDbtTxInf/Dbtr/Nm', 'debtorName', false, true),
    ('pain.008.base', 'dbtr_pstl_adr_strt_nm', 'PmtInf/DrctDbtTxInf/Dbtr/PstlAdr/StrtNm', 'debtorStreet', false, true),
    ('pain.008.base', 'dbtr_pstl_adr_pst_cd', 'PmtInf/DrctDbtTxInf/Dbtr/PstlAdr/PstCd', 'debtorPostalCode', false, true),
    ('pain.008.base', 'dbtr_pstl_adr_twn_nm', 'PmtInf/DrctDbtTxInf/Dbtr/PstlAdr/TwnNm', 'debtorCity', false, true),
    ('pain.008.base', 'dbtr_pstl_adr_ctry', 'PmtInf/DrctDbtTxInf/Dbtr/PstlAdr/Ctry', 'debtorCountry', false, true),
    ('pain.008.base', 'dbtr_acct_id_iban', 'PmtInf/DrctDbtTxInf/DbtrAcct/Id/IBAN', 'debtorIBAN', false, true),
    ('pain.008.base', 'dbtr_acct_id_othr_id', 'PmtInf/DrctDbtTxInf/DbtrAcct/Id/Othr/Id', 'debtorOtherAccount', false, true),

    -- Remittance
    ('pain.008.base', 'rmt_inf_ustrd', 'PmtInf/DrctDbtTxInf/RmtInf/Ustrd', 'remittanceUnstructured', false, true),
    ('pain.008.base', 'rmt_inf_strd_cdtr_ref_inf_ref', 'PmtInf/DrctDbtTxInf/RmtInf/Strd/CdtrRefInf/Ref', 'creditorReference', false, true),
    ('pain.008.base', 'purp_cd', 'PmtInf/DrctDbtTxInf/Purp/Cd', 'purposeCode', false, true)
ON CONFLICT (format_id, target_column) DO UPDATE
SET source_path = EXCLUDED.source_path,
    parser_path = EXCLUDED.parser_path,
    is_required = EXCLUDED.is_required,
    is_active = true;

-- =============================================================================
-- SECTION 4: pacs.002.base Gold Mappings
-- =============================================================================

DELETE FROM mapping.gold_field_mappings WHERE format_id = 'pacs.002.base';

INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, transform_expression, is_active)
VALUES
    -- Payment Instruction (status report treated as a reference to original payment)
    ('pacs.002.base', 'cdm_payment_instruction', 'instruction_id', '_GENERATED_UUID', NULL, NULL, true),
    ('pacs.002.base', 'cdm_payment_instruction', 'stg_id', '_CONTEXT.stg_id', NULL, NULL, true),
    ('pacs.002.base', 'cdm_payment_instruction', 'batch_id', '_CONTEXT.batch_id', NULL, NULL, true),
    ('pacs.002.base', 'cdm_payment_instruction', 'message_id', 'grp_hdr_msg_id', NULL, NULL, true),
    ('pacs.002.base', 'cdm_payment_instruction', 'creation_date_time', 'grp_hdr_cre_dt_tm', NULL, 'TO_TIMESTAMP', true),
    ('pacs.002.base', 'cdm_payment_instruction', 'end_to_end_id', 'tx_inf_orgnl_end_to_end_id', NULL, NULL, true),
    ('pacs.002.base', 'cdm_payment_instruction', 'instruction_id_ref', 'tx_inf_orgnl_instr_id', NULL, NULL, true),
    ('pacs.002.base', 'cdm_payment_instruction', 'uetr', 'tx_inf_orgnl_uetr', NULL, NULL, true),
    ('pacs.002.base', 'cdm_payment_instruction', 'amount', 'orgnl_tx_ref_intr_bk_sttlm_amt', NULL, 'TO_DECIMAL', true),
    ('pacs.002.base', 'cdm_payment_instruction', 'currency', 'orgnl_tx_ref_intr_bk_sttlm_ccy', NULL, 'COALESCE:XXX', true),
    ('pacs.002.base', 'cdm_payment_instruction', 'settlement_date', 'orgnl_tx_ref_intr_bk_sttlm_dt', NULL, 'TO_DATE', true),
    ('pacs.002.base', 'cdm_payment_instruction', 'payment_status', 'tx_inf_tx_sts', NULL, NULL, true),
    ('pacs.002.base', 'cdm_payment_instruction', 'status_reason_code', 'tx_inf_sts_rsn_cd', NULL, NULL, true),
    ('pacs.002.base', 'cdm_payment_instruction', 'source_message_type', '''pacs.002''', NULL, NULL, true),
    ('pacs.002.base', 'cdm_payment_instruction', 'source_format', 'source_format', NULL, NULL, true),

    -- Original Debtor Party
    ('pacs.002.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'DEBTOR', NULL, true),
    ('pacs.002.base', 'cdm_party', 'instruction_id', '_CONTEXT.instruction_id', 'DEBTOR', NULL, true),
    ('pacs.002.base', 'cdm_party', 'name', 'orgnl_tx_ref_dbtr_nm', 'DEBTOR', NULL, true),
    ('pacs.002.base', 'cdm_party', 'role', '''DEBTOR''', 'DEBTOR', NULL, true),
    ('pacs.002.base', 'cdm_party', 'source_message_type', '''pacs.002''', 'DEBTOR', NULL, true),

    -- Original Creditor Party
    ('pacs.002.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'CREDITOR', NULL, true),
    ('pacs.002.base', 'cdm_party', 'instruction_id', '_CONTEXT.instruction_id', 'CREDITOR', NULL, true),
    ('pacs.002.base', 'cdm_party', 'name', 'orgnl_tx_ref_cdtr_nm', 'CREDITOR', NULL, true),
    ('pacs.002.base', 'cdm_party', 'role', '''CREDITOR''', 'CREDITOR', NULL, true),
    ('pacs.002.base', 'cdm_party', 'source_message_type', '''pacs.002''', 'CREDITOR', NULL, true),

    -- Original Debtor Account
    ('pacs.002.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'DEBTOR', NULL, true),
    ('pacs.002.base', 'cdm_account', 'instruction_id', '_CONTEXT.instruction_id', 'DEBTOR', NULL, true),
    ('pacs.002.base', 'cdm_account', 'account_number', 'orgnl_tx_ref_dbtr_acct_id_othr', 'DEBTOR', 'COALESCE_IBAN', true),
    ('pacs.002.base', 'cdm_account', 'iban', 'orgnl_tx_ref_dbtr_acct_id_iban', 'DEBTOR', NULL, true),
    ('pacs.002.base', 'cdm_account', 'account_type', '''CACC''', 'DEBTOR', NULL, true),
    ('pacs.002.base', 'cdm_account', 'currency', 'orgnl_tx_ref_intr_bk_sttlm_ccy', 'DEBTOR', 'COALESCE:XXX', true),
    ('pacs.002.base', 'cdm_account', 'role', '''DEBTOR''', 'DEBTOR', NULL, true),
    ('pacs.002.base', 'cdm_account', 'source_message_type', '''pacs.002''', 'DEBTOR', NULL, true),

    -- Original Creditor Account
    ('pacs.002.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'CREDITOR', NULL, true),
    ('pacs.002.base', 'cdm_account', 'instruction_id', '_CONTEXT.instruction_id', 'CREDITOR', NULL, true),
    ('pacs.002.base', 'cdm_account', 'account_number', 'orgnl_tx_ref_cdtr_acct_id_othr', 'CREDITOR', 'COALESCE_IBAN', true),
    ('pacs.002.base', 'cdm_account', 'iban', 'orgnl_tx_ref_cdtr_acct_id_iban', 'CREDITOR', NULL, true),
    ('pacs.002.base', 'cdm_account', 'account_type', '''CACC''', 'CREDITOR', NULL, true),
    ('pacs.002.base', 'cdm_account', 'currency', 'orgnl_tx_ref_intr_bk_sttlm_ccy', 'CREDITOR', 'COALESCE:XXX', true),
    ('pacs.002.base', 'cdm_account', 'role', '''CREDITOR''', 'CREDITOR', NULL, true),
    ('pacs.002.base', 'cdm_account', 'source_message_type', '''pacs.002''', 'CREDITOR', NULL, true),

    -- Original Debtor Agent
    ('pacs.002.base', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'DEBTOR_AGENT', NULL, true),
    ('pacs.002.base', 'cdm_financial_institution', 'instruction_id', '_CONTEXT.instruction_id', 'DEBTOR_AGENT', NULL, true),
    ('pacs.002.base', 'cdm_financial_institution', 'bic', 'orgnl_tx_ref_dbtr_agt_bic', 'DEBTOR_AGENT', NULL, true),
    ('pacs.002.base', 'cdm_financial_institution', 'name', 'orgnl_tx_ref_dbtr_agt_bic', 'DEBTOR_AGENT', 'COALESCE_BIC', true),
    ('pacs.002.base', 'cdm_financial_institution', 'country', 'orgnl_tx_ref_dbtr_agt_bic', 'DEBTOR_AGENT', 'COUNTRY_FROM_BIC', true),
    ('pacs.002.base', 'cdm_financial_institution', 'role', '''DEBTOR_AGENT''', 'DEBTOR_AGENT', NULL, true),
    ('pacs.002.base', 'cdm_financial_institution', 'source_message_type', '''pacs.002''', 'DEBTOR_AGENT', NULL, true),

    -- Original Creditor Agent
    ('pacs.002.base', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'CREDITOR_AGENT', NULL, true),
    ('pacs.002.base', 'cdm_financial_institution', 'instruction_id', '_CONTEXT.instruction_id', 'CREDITOR_AGENT', NULL, true),
    ('pacs.002.base', 'cdm_financial_institution', 'bic', 'orgnl_tx_ref_cdtr_agt_bic', 'CREDITOR_AGENT', NULL, true),
    ('pacs.002.base', 'cdm_financial_institution', 'name', 'orgnl_tx_ref_cdtr_agt_bic', 'CREDITOR_AGENT', 'COALESCE_BIC', true),
    ('pacs.002.base', 'cdm_financial_institution', 'country', 'orgnl_tx_ref_cdtr_agt_bic', 'CREDITOR_AGENT', 'COUNTRY_FROM_BIC', true),
    ('pacs.002.base', 'cdm_financial_institution', 'role', '''CREDITOR_AGENT''', 'CREDITOR_AGENT', NULL, true),
    ('pacs.002.base', 'cdm_financial_institution', 'source_message_type', '''pacs.002''', 'CREDITOR_AGENT', NULL, true)
;

-- =============================================================================
-- SECTION 5: pacs.004.base Gold Mappings
-- =============================================================================

DELETE FROM mapping.gold_field_mappings WHERE format_id = 'pacs.004.base';

INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, transform_expression, is_active)
VALUES
    -- Payment Instruction (return transaction)
    ('pacs.004.base', 'cdm_payment_instruction', 'instruction_id', '_GENERATED_UUID', NULL, NULL, true),
    ('pacs.004.base', 'cdm_payment_instruction', 'stg_id', '_CONTEXT.stg_id', NULL, NULL, true),
    ('pacs.004.base', 'cdm_payment_instruction', 'batch_id', '_CONTEXT.batch_id', NULL, NULL, true),
    ('pacs.004.base', 'cdm_payment_instruction', 'message_id', 'grp_hdr_msg_id', NULL, NULL, true),
    ('pacs.004.base', 'cdm_payment_instruction', 'creation_date_time', 'grp_hdr_cre_dt_tm', NULL, 'TO_TIMESTAMP', true),
    ('pacs.004.base', 'cdm_payment_instruction', 'end_to_end_id', 'tx_inf_orgnl_end_to_end_id', NULL, NULL, true),
    ('pacs.004.base', 'cdm_payment_instruction', 'instruction_id_ref', 'tx_inf_orgnl_instr_id', NULL, NULL, true),
    ('pacs.004.base', 'cdm_payment_instruction', 'transaction_id', 'tx_inf_rtr_id', NULL, NULL, true),
    ('pacs.004.base', 'cdm_payment_instruction', 'uetr', 'tx_inf_orgnl_uetr', NULL, NULL, true),
    ('pacs.004.base', 'cdm_payment_instruction', 'amount', 'tx_inf_rtrd_intr_bk_sttlm_amt', NULL, 'TO_DECIMAL', true),
    ('pacs.004.base', 'cdm_payment_instruction', 'currency', 'tx_inf_rtrd_intr_bk_sttlm_ccy', NULL, 'COALESCE:XXX', true),
    ('pacs.004.base', 'cdm_payment_instruction', 'settlement_date', 'tx_inf_intr_bk_sttlm_dt', NULL, 'TO_DATE', true),
    ('pacs.004.base', 'cdm_payment_instruction', 'payment_status', '''RETURNED''', NULL, NULL, true),
    ('pacs.004.base', 'cdm_payment_instruction', 'status_reason_code', 'tx_inf_rtr_rsn_cd', NULL, NULL, true),
    ('pacs.004.base', 'cdm_payment_instruction', 'number_of_transactions', 'grp_hdr_nb_of_txs', NULL, 'TO_INTEGER', true),
    ('pacs.004.base', 'cdm_payment_instruction', 'settlement_method', 'grp_hdr_sttlm_mtd', NULL, NULL, true),
    ('pacs.004.base', 'cdm_payment_instruction', 'clearing_system_code', 'grp_hdr_clr_sys_cd', NULL, NULL, true),
    ('pacs.004.base', 'cdm_payment_instruction', 'source_message_type', '''pacs.004''', NULL, NULL, true),
    ('pacs.004.base', 'cdm_payment_instruction', 'source_format', 'source_format', NULL, NULL, true),

    -- Original Debtor Party
    ('pacs.004.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'DEBTOR', NULL, true),
    ('pacs.004.base', 'cdm_party', 'instruction_id', '_CONTEXT.instruction_id', 'DEBTOR', NULL, true),
    ('pacs.004.base', 'cdm_party', 'name', 'orgnl_tx_ref_dbtr_nm', 'DEBTOR', NULL, true),
    ('pacs.004.base', 'cdm_party', 'country', 'orgnl_tx_ref_dbtr_pstl_adr_ctry', 'DEBTOR', 'COALESCE:XX', true),
    ('pacs.004.base', 'cdm_party', 'role', '''DEBTOR''', 'DEBTOR', NULL, true),
    ('pacs.004.base', 'cdm_party', 'source_message_type', '''pacs.004''', 'DEBTOR', NULL, true),

    -- Original Creditor Party
    ('pacs.004.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'CREDITOR', NULL, true),
    ('pacs.004.base', 'cdm_party', 'instruction_id', '_CONTEXT.instruction_id', 'CREDITOR', NULL, true),
    ('pacs.004.base', 'cdm_party', 'name', 'orgnl_tx_ref_cdtr_nm', 'CREDITOR', NULL, true),
    ('pacs.004.base', 'cdm_party', 'country', 'orgnl_tx_ref_cdtr_pstl_adr_ctry', 'CREDITOR', 'COALESCE:XX', true),
    ('pacs.004.base', 'cdm_party', 'role', '''CREDITOR''', 'CREDITOR', NULL, true),
    ('pacs.004.base', 'cdm_party', 'source_message_type', '''pacs.004''', 'CREDITOR', NULL, true),

    -- Original Debtor Account
    ('pacs.004.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'DEBTOR', NULL, true),
    ('pacs.004.base', 'cdm_account', 'instruction_id', '_CONTEXT.instruction_id', 'DEBTOR', NULL, true),
    ('pacs.004.base', 'cdm_account', 'account_number', 'orgnl_tx_ref_dbtr_acct_id_othr', 'DEBTOR', 'COALESCE_IBAN', true),
    ('pacs.004.base', 'cdm_account', 'iban', 'orgnl_tx_ref_dbtr_acct_id_iban', 'DEBTOR', NULL, true),
    ('pacs.004.base', 'cdm_account', 'account_type', '''CACC''', 'DEBTOR', NULL, true),
    ('pacs.004.base', 'cdm_account', 'currency', 'orgnl_tx_ref_intr_bk_sttlm_ccy', 'DEBTOR', 'COALESCE:XXX', true),
    ('pacs.004.base', 'cdm_account', 'role', '''DEBTOR''', 'DEBTOR', NULL, true),
    ('pacs.004.base', 'cdm_account', 'source_message_type', '''pacs.004''', 'DEBTOR', NULL, true),

    -- Original Creditor Account
    ('pacs.004.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'CREDITOR', NULL, true),
    ('pacs.004.base', 'cdm_account', 'instruction_id', '_CONTEXT.instruction_id', 'CREDITOR', NULL, true),
    ('pacs.004.base', 'cdm_account', 'account_number', 'orgnl_tx_ref_cdtr_acct_id_othr', 'CREDITOR', 'COALESCE_IBAN', true),
    ('pacs.004.base', 'cdm_account', 'iban', 'orgnl_tx_ref_cdtr_acct_id_iban', 'CREDITOR', NULL, true),
    ('pacs.004.base', 'cdm_account', 'account_type', '''CACC''', 'CREDITOR', NULL, true),
    ('pacs.004.base', 'cdm_account', 'currency', 'orgnl_tx_ref_intr_bk_sttlm_ccy', 'CREDITOR', 'COALESCE:XXX', true),
    ('pacs.004.base', 'cdm_account', 'role', '''CREDITOR''', 'CREDITOR', NULL, true),
    ('pacs.004.base', 'cdm_account', 'source_message_type', '''pacs.004''', 'CREDITOR', NULL, true),

    -- Original Debtor Agent
    ('pacs.004.base', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'DEBTOR_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'instruction_id', '_CONTEXT.instruction_id', 'DEBTOR_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'bic', 'orgnl_tx_ref_dbtr_agt_bic', 'DEBTOR_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'clearing_system_member_id', 'orgnl_tx_ref_dbtr_agt_clr_sys_mmb_id', 'DEBTOR_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'name', 'orgnl_tx_ref_dbtr_agt_bic', 'DEBTOR_AGENT', 'COALESCE_BIC', true),
    ('pacs.004.base', 'cdm_financial_institution', 'country', 'orgnl_tx_ref_dbtr_agt_bic', 'DEBTOR_AGENT', 'COUNTRY_FROM_BIC', true),
    ('pacs.004.base', 'cdm_financial_institution', 'role', '''DEBTOR_AGENT''', 'DEBTOR_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'source_message_type', '''pacs.004''', 'DEBTOR_AGENT', NULL, true),

    -- Original Creditor Agent
    ('pacs.004.base', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'CREDITOR_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'instruction_id', '_CONTEXT.instruction_id', 'CREDITOR_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'bic', 'orgnl_tx_ref_cdtr_agt_bic', 'CREDITOR_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'clearing_system_member_id', 'orgnl_tx_ref_cdtr_agt_clr_sys_mmb_id', 'CREDITOR_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'name', 'orgnl_tx_ref_cdtr_agt_bic', 'CREDITOR_AGENT', 'COALESCE_BIC', true),
    ('pacs.004.base', 'cdm_financial_institution', 'country', 'orgnl_tx_ref_cdtr_agt_bic', 'CREDITOR_AGENT', 'COUNTRY_FROM_BIC', true),
    ('pacs.004.base', 'cdm_financial_institution', 'role', '''CREDITOR_AGENT''', 'CREDITOR_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'source_message_type', '''pacs.004''', 'CREDITOR_AGENT', NULL, true),

    -- Instructing Agent
    ('pacs.004.base', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'INSTRUCTING_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'instruction_id', '_CONTEXT.instruction_id', 'INSTRUCTING_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'bic', 'instg_agt_bic', 'INSTRUCTING_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'clearing_system_member_id', 'instg_agt_clr_sys_mmb_id', 'INSTRUCTING_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'name', 'instg_agt_bic', 'INSTRUCTING_AGENT', 'COALESCE_BIC', true),
    ('pacs.004.base', 'cdm_financial_institution', 'country', 'instg_agt_bic', 'INSTRUCTING_AGENT', 'COUNTRY_FROM_BIC', true),
    ('pacs.004.base', 'cdm_financial_institution', 'role', '''INSTRUCTING_AGENT''', 'INSTRUCTING_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'source_message_type', '''pacs.004''', 'INSTRUCTING_AGENT', NULL, true),

    -- Instructed Agent
    ('pacs.004.base', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'INSTRUCTED_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'instruction_id', '_CONTEXT.instruction_id', 'INSTRUCTED_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'bic', 'instd_agt_bic', 'INSTRUCTED_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'clearing_system_member_id', 'instd_agt_clr_sys_mmb_id', 'INSTRUCTED_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'name', 'instd_agt_bic', 'INSTRUCTED_AGENT', 'COALESCE_BIC', true),
    ('pacs.004.base', 'cdm_financial_institution', 'country', 'instd_agt_bic', 'INSTRUCTED_AGENT', 'COUNTRY_FROM_BIC', true),
    ('pacs.004.base', 'cdm_financial_institution', 'role', '''INSTRUCTED_AGENT''', 'INSTRUCTED_AGENT', NULL, true),
    ('pacs.004.base', 'cdm_financial_institution', 'source_message_type', '''pacs.004''', 'INSTRUCTED_AGENT', NULL, true)
;

-- =============================================================================
-- SECTION 6: pain.008.base Gold Mappings
-- =============================================================================

DELETE FROM mapping.gold_field_mappings WHERE format_id = 'pain.008.base';

INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, transform_expression, is_active)
VALUES
    -- Payment Instruction
    ('pain.008.base', 'cdm_payment_instruction', 'instruction_id', '_GENERATED_UUID', NULL, NULL, true),
    ('pain.008.base', 'cdm_payment_instruction', 'stg_id', '_CONTEXT.stg_id', NULL, NULL, true),
    ('pain.008.base', 'cdm_payment_instruction', 'batch_id', '_CONTEXT.batch_id', NULL, NULL, true),
    ('pain.008.base', 'cdm_payment_instruction', 'message_id', 'grp_hdr_msg_id', NULL, NULL, true),
    ('pain.008.base', 'cdm_payment_instruction', 'creation_date_time', 'grp_hdr_cre_dt_tm', NULL, 'TO_TIMESTAMP', true),
    ('pain.008.base', 'cdm_payment_instruction', 'payment_information_id', 'pmt_inf_id', NULL, NULL, true),
    ('pain.008.base', 'cdm_payment_instruction', 'end_to_end_id', 'drct_dbt_tx_inf_pmt_id_end_to_end_id', NULL, NULL, true),
    ('pain.008.base', 'cdm_payment_instruction', 'instruction_id_ref', 'drct_dbt_tx_inf_pmt_id_instr_id', NULL, NULL, true),
    ('pain.008.base', 'cdm_payment_instruction', 'amount', 'drct_dbt_tx_inf_instd_amt', NULL, 'TO_DECIMAL', true),
    ('pain.008.base', 'cdm_payment_instruction', 'currency', 'drct_dbt_tx_inf_instd_amt_ccy', NULL, 'COALESCE:XXX', true),
    ('pain.008.base', 'cdm_payment_instruction', 'requested_execution_date', 'reqd_colltn_dt', NULL, 'TO_DATE', true),
    ('pain.008.base', 'cdm_payment_instruction', 'payment_method', 'pmt_mtd', NULL, NULL, true),
    ('pain.008.base', 'cdm_payment_instruction', 'service_level', 'pmt_tp_inf_svc_lvl_cd', NULL, NULL, true),
    ('pain.008.base', 'cdm_payment_instruction', 'local_instrument', 'pmt_tp_inf_lcl_instrm_cd', NULL, NULL, true),
    ('pain.008.base', 'cdm_payment_instruction', 'sequence_type', 'pmt_tp_inf_seq_tp', NULL, NULL, true),
    ('pain.008.base', 'cdm_payment_instruction', 'category_purpose', 'pmt_tp_inf_ctgy_purp_cd', NULL, NULL, true),
    ('pain.008.base', 'cdm_payment_instruction', 'charge_bearer', 'drct_dbt_tx_inf_chrgbr', NULL, NULL, true),
    ('pain.008.base', 'cdm_payment_instruction', 'number_of_transactions', 'grp_hdr_nb_of_txs', NULL, 'TO_INTEGER', true),
    ('pain.008.base', 'cdm_payment_instruction', 'control_sum', 'grp_hdr_ctrl_sum', NULL, 'TO_DECIMAL', true),
    ('pain.008.base', 'cdm_payment_instruction', 'purpose_code', 'purp_cd', NULL, NULL, true),
    ('pain.008.base', 'cdm_payment_instruction', 'remittance_unstructured', 'rmt_inf_ustrd', NULL, 'TO_ARRAY', true),
    ('pain.008.base', 'cdm_payment_instruction', 'source_message_type', '''pain.008''', NULL, NULL, true),
    ('pain.008.base', 'cdm_payment_instruction', 'source_format', 'source_format', NULL, NULL, true),

    -- Initiating Party
    ('pain.008.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'INITIATING_PARTY', NULL, true),
    ('pain.008.base', 'cdm_party', 'instruction_id', '_CONTEXT.instruction_id', 'INITIATING_PARTY', NULL, true),
    ('pain.008.base', 'cdm_party', 'name', 'grp_hdr_initg_pty_nm', 'INITIATING_PARTY', NULL, true),
    ('pain.008.base', 'cdm_party', 'organisation_id', 'grp_hdr_initg_pty_id_org_id_othr_id', 'INITIATING_PARTY', NULL, true),
    ('pain.008.base', 'cdm_party', 'role', '''INITIATING_PARTY''', 'INITIATING_PARTY', NULL, true),
    ('pain.008.base', 'cdm_party', 'source_message_type', '''pain.008''', 'INITIATING_PARTY', NULL, true),

    -- Creditor Party (DD Creditor = Payment Beneficiary)
    ('pain.008.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'CREDITOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'instruction_id', '_CONTEXT.instruction_id', 'CREDITOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'name', 'cdtr_nm', 'CREDITOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'street_name', 'cdtr_pstl_adr_strt_nm', 'CREDITOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'building_number', 'cdtr_pstl_adr_bldg_nb', 'CREDITOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'postal_code', 'cdtr_pstl_adr_pst_cd', 'CREDITOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'city', 'cdtr_pstl_adr_twn_nm', 'CREDITOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'country', 'cdtr_pstl_adr_ctry', 'CREDITOR', 'COALESCE:XX', true),
    ('pain.008.base', 'cdm_party', 'private_id', 'cdtr_id_prvt_id_othr_id', 'CREDITOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'organisation_id', 'cdtr_id_org_id_othr_id', 'CREDITOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'role', '''CREDITOR''', 'CREDITOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'source_message_type', '''pain.008''', 'CREDITOR', NULL, true),

    -- Debtor Party (DD Debtor = Payer)
    ('pain.008.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'DEBTOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'instruction_id', '_CONTEXT.instruction_id', 'DEBTOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'name', 'dbtr_nm', 'DEBTOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'street_name', 'dbtr_pstl_adr_strt_nm', 'DEBTOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'postal_code', 'dbtr_pstl_adr_pst_cd', 'DEBTOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'city', 'dbtr_pstl_adr_twn_nm', 'DEBTOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'country', 'dbtr_pstl_adr_ctry', 'DEBTOR', 'COALESCE:XX', true),
    ('pain.008.base', 'cdm_party', 'role', '''DEBTOR''', 'DEBTOR', NULL, true),
    ('pain.008.base', 'cdm_party', 'source_message_type', '''pain.008''', 'DEBTOR', NULL, true),

    -- Creditor Account
    ('pain.008.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'CREDITOR', NULL, true),
    ('pain.008.base', 'cdm_account', 'instruction_id', '_CONTEXT.instruction_id', 'CREDITOR', NULL, true),
    ('pain.008.base', 'cdm_account', 'account_number', 'cdtr_acct_id_othr_id', 'CREDITOR', 'COALESCE_IBAN', true),
    ('pain.008.base', 'cdm_account', 'iban', 'cdtr_acct_id_iban', 'CREDITOR', NULL, true),
    ('pain.008.base', 'cdm_account', 'account_type', '''CACC''', 'CREDITOR', NULL, true),
    ('pain.008.base', 'cdm_account', 'currency', 'cdtr_acct_ccy', 'CREDITOR', 'COALESCE:XXX', true),
    ('pain.008.base', 'cdm_account', 'role', '''CREDITOR''', 'CREDITOR', NULL, true),
    ('pain.008.base', 'cdm_account', 'source_message_type', '''pain.008''', 'CREDITOR', NULL, true),

    -- Debtor Account
    ('pain.008.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'DEBTOR', NULL, true),
    ('pain.008.base', 'cdm_account', 'instruction_id', '_CONTEXT.instruction_id', 'DEBTOR', NULL, true),
    ('pain.008.base', 'cdm_account', 'account_number', 'dbtr_acct_id_othr_id', 'DEBTOR', 'COALESCE_IBAN', true),
    ('pain.008.base', 'cdm_account', 'iban', 'dbtr_acct_id_iban', 'DEBTOR', NULL, true),
    ('pain.008.base', 'cdm_account', 'account_type', '''CACC''', 'DEBTOR', NULL, true),
    ('pain.008.base', 'cdm_account', 'currency', 'drct_dbt_tx_inf_instd_amt_ccy', 'DEBTOR', 'COALESCE:XXX', true),
    ('pain.008.base', 'cdm_account', 'role', '''DEBTOR''', 'DEBTOR', NULL, true),
    ('pain.008.base', 'cdm_account', 'source_message_type', '''pain.008''', 'DEBTOR', NULL, true),

    -- Creditor Agent
    ('pain.008.base', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'CREDITOR_AGENT', NULL, true),
    ('pain.008.base', 'cdm_financial_institution', 'instruction_id', '_CONTEXT.instruction_id', 'CREDITOR_AGENT', NULL, true),
    ('pain.008.base', 'cdm_financial_institution', 'bic', 'cdtr_agt_bic', 'CREDITOR_AGENT', NULL, true),
    ('pain.008.base', 'cdm_financial_institution', 'clearing_system_member_id', 'cdtr_agt_clr_sys_mmb_id', 'CREDITOR_AGENT', NULL, true),
    ('pain.008.base', 'cdm_financial_institution', 'name', 'cdtr_agt_bic', 'CREDITOR_AGENT', 'COALESCE_BIC', true),
    ('pain.008.base', 'cdm_financial_institution', 'country', 'cdtr_agt_bic', 'CREDITOR_AGENT', 'COUNTRY_FROM_BIC', true),
    ('pain.008.base', 'cdm_financial_institution', 'role', '''CREDITOR_AGENT''', 'CREDITOR_AGENT', NULL, true),
    ('pain.008.base', 'cdm_financial_institution', 'source_message_type', '''pain.008''', 'CREDITOR_AGENT', NULL, true),

    -- Debtor Agent
    ('pain.008.base', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'DEBTOR_AGENT', NULL, true),
    ('pain.008.base', 'cdm_financial_institution', 'instruction_id', '_CONTEXT.instruction_id', 'DEBTOR_AGENT', NULL, true),
    ('pain.008.base', 'cdm_financial_institution', 'bic', 'dbtr_agt_bic', 'DEBTOR_AGENT', NULL, true),
    ('pain.008.base', 'cdm_financial_institution', 'clearing_system_member_id', 'dbtr_agt_clr_sys_mmb_id', 'DEBTOR_AGENT', NULL, true),
    ('pain.008.base', 'cdm_financial_institution', 'name', 'dbtr_agt_bic', 'DEBTOR_AGENT', 'COALESCE_BIC', true),
    ('pain.008.base', 'cdm_financial_institution', 'country', 'dbtr_agt_bic', 'DEBTOR_AGENT', 'COUNTRY_FROM_BIC', true),
    ('pain.008.base', 'cdm_financial_institution', 'role', '''DEBTOR_AGENT''', 'DEBTOR_AGENT', NULL, true),
    ('pain.008.base', 'cdm_financial_institution', 'source_message_type', '''pain.008''', 'DEBTOR_AGENT', NULL, true)
;

-- =============================================================================
-- SECTION 7: pacs.009.base Gold Mappings (CRITICAL - was missing!)
-- =============================================================================

DELETE FROM mapping.gold_field_mappings WHERE format_id = 'pacs.009.base';

INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, transform_expression, is_active)
VALUES
    -- Payment Instruction
    ('pacs.009.base', 'cdm_payment_instruction', 'instruction_id', '_GENERATED_UUID', NULL, NULL, true),
    ('pacs.009.base', 'cdm_payment_instruction', 'stg_id', '_CONTEXT.stg_id', NULL, NULL, true),
    ('pacs.009.base', 'cdm_payment_instruction', 'batch_id', '_CONTEXT.batch_id', NULL, NULL, true),
    ('pacs.009.base', 'cdm_payment_instruction', 'message_id', 'grp_hdr_msg_id', NULL, NULL, true),
    ('pacs.009.base', 'cdm_payment_instruction', 'creation_date_time', 'grp_hdr_cre_dt_tm', NULL, 'TO_TIMESTAMP', true),
    ('pacs.009.base', 'cdm_payment_instruction', 'end_to_end_id', 'pmt_id_end_to_end_id', NULL, NULL, true),
    ('pacs.009.base', 'cdm_payment_instruction', 'instruction_id_ref', 'pmt_id_instr_id', NULL, NULL, true),
    ('pacs.009.base', 'cdm_payment_instruction', 'transaction_id', 'pmt_id_tx_id', NULL, NULL, true),
    ('pacs.009.base', 'cdm_payment_instruction', 'uetr', 'pmt_id_uetr', NULL, NULL, true),
    ('pacs.009.base', 'cdm_payment_instruction', 'clearing_system_reference', 'pmt_id_clr_sys_ref', NULL, NULL, true),
    ('pacs.009.base', 'cdm_payment_instruction', 'amount', 'intr_bk_sttlm_amt', NULL, 'TO_DECIMAL', true),
    ('pacs.009.base', 'cdm_payment_instruction', 'currency', 'intr_bk_sttlm_ccy', NULL, 'COALESCE:XXX', true),
    ('pacs.009.base', 'cdm_payment_instruction', 'settlement_date', 'intr_bk_sttlm_dt', NULL, 'TO_DATE', true),
    ('pacs.009.base', 'cdm_payment_instruction', 'settlement_priority', 'sttlm_prty', NULL, NULL, true),
    ('pacs.009.base', 'cdm_payment_instruction', 'settlement_method', 'grp_hdr_sttlm_mtd', NULL, NULL, true),
    ('pacs.009.base', 'cdm_payment_instruction', 'clearing_system_code', 'grp_hdr_clr_sys_cd', NULL, NULL, true),
    ('pacs.009.base', 'cdm_payment_instruction', 'number_of_transactions', 'grp_hdr_nb_of_txs', NULL, 'TO_INTEGER', true),
    ('pacs.009.base', 'cdm_payment_instruction', 'control_sum', 'grp_hdr_ctrl_sum', NULL, 'TO_DECIMAL', true),
    ('pacs.009.base', 'cdm_payment_instruction', 'charge_bearer', 'chrg_br', NULL, NULL, true),
    ('pacs.009.base', 'cdm_payment_instruction', 'source_message_type', '''pacs.009''', NULL, NULL, true),
    ('pacs.009.base', 'cdm_payment_instruction', 'source_format', 'source_format', NULL, NULL, true),

    -- Debtor (Financial Institution)
    ('pacs.009.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'DEBTOR', NULL, true),
    ('pacs.009.base', 'cdm_party', 'instruction_id', '_CONTEXT.instruction_id', 'DEBTOR', NULL, true),
    ('pacs.009.base', 'cdm_party', 'name', 'dbtr_nm', 'DEBTOR', NULL, true),
    ('pacs.009.base', 'cdm_party', 'country', 'dbtr_pstl_adr_ctry', 'DEBTOR', 'COALESCE:XX', true),
    ('pacs.009.base', 'cdm_party', 'role', '''DEBTOR''', 'DEBTOR', NULL, true),
    ('pacs.009.base', 'cdm_party', 'source_message_type', '''pacs.009''', 'DEBTOR', NULL, true),

    -- Creditor (Financial Institution)
    ('pacs.009.base', 'cdm_party', 'party_id', '_GENERATED_UUID', 'CREDITOR', NULL, true),
    ('pacs.009.base', 'cdm_party', 'instruction_id', '_CONTEXT.instruction_id', 'CREDITOR', NULL, true),
    ('pacs.009.base', 'cdm_party', 'name', 'cdtr_nm', 'CREDITOR', NULL, true),
    ('pacs.009.base', 'cdm_party', 'country', 'cdtr_pstl_adr_ctry', 'CREDITOR', 'COALESCE:XX', true),
    ('pacs.009.base', 'cdm_party', 'role', '''CREDITOR''', 'CREDITOR', NULL, true),
    ('pacs.009.base', 'cdm_party', 'source_message_type', '''pacs.009''', 'CREDITOR', NULL, true),

    -- Debtor Account
    ('pacs.009.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'DEBTOR', NULL, true),
    ('pacs.009.base', 'cdm_account', 'instruction_id', '_CONTEXT.instruction_id', 'DEBTOR', NULL, true),
    ('pacs.009.base', 'cdm_account', 'account_number', 'dbtr_acct_id_othr', 'DEBTOR', 'COALESCE_IBAN', true),
    ('pacs.009.base', 'cdm_account', 'iban', 'dbtr_acct_id_iban', 'DEBTOR', NULL, true),
    ('pacs.009.base', 'cdm_account', 'account_type', '''CACC''', 'DEBTOR', NULL, true),
    ('pacs.009.base', 'cdm_account', 'currency', 'intr_bk_sttlm_ccy', 'DEBTOR', 'COALESCE:XXX', true),
    ('pacs.009.base', 'cdm_account', 'role', '''DEBTOR''', 'DEBTOR', NULL, true),
    ('pacs.009.base', 'cdm_account', 'source_message_type', '''pacs.009''', 'DEBTOR', NULL, true),

    -- Creditor Account
    ('pacs.009.base', 'cdm_account', 'account_id', '_GENERATED_UUID', 'CREDITOR', NULL, true),
    ('pacs.009.base', 'cdm_account', 'instruction_id', '_CONTEXT.instruction_id', 'CREDITOR', NULL, true),
    ('pacs.009.base', 'cdm_account', 'account_number', 'cdtr_acct_id_othr', 'CREDITOR', 'COALESCE_IBAN', true),
    ('pacs.009.base', 'cdm_account', 'iban', 'cdtr_acct_id_iban', 'CREDITOR', NULL, true),
    ('pacs.009.base', 'cdm_account', 'account_type', '''CACC''', 'CREDITOR', NULL, true),
    ('pacs.009.base', 'cdm_account', 'currency', 'intr_bk_sttlm_ccy', 'CREDITOR', 'COALESCE:XXX', true),
    ('pacs.009.base', 'cdm_account', 'role', '''CREDITOR''', 'CREDITOR', NULL, true),
    ('pacs.009.base', 'cdm_account', 'source_message_type', '''pacs.009''', 'CREDITOR', NULL, true),

    -- Debtor Agent
    ('pacs.009.base', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'DEBTOR_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'instruction_id', '_CONTEXT.instruction_id', 'DEBTOR_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'bic', 'dbtr_agt_bic', 'DEBTOR_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'lei', 'dbtr_agt_lei', 'DEBTOR_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'clearing_system_member_id', 'dbtr_agt_clr_sys_mmb_id', 'DEBTOR_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'name', 'dbtr_agt_bic', 'DEBTOR_AGENT', 'COALESCE_BIC', true),
    ('pacs.009.base', 'cdm_financial_institution', 'country', 'dbtr_agt_bic', 'DEBTOR_AGENT', 'COUNTRY_FROM_BIC', true),
    ('pacs.009.base', 'cdm_financial_institution', 'role', '''DEBTOR_AGENT''', 'DEBTOR_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'source_message_type', '''pacs.009''', 'DEBTOR_AGENT', NULL, true),

    -- Creditor Agent
    ('pacs.009.base', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'CREDITOR_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'instruction_id', '_CONTEXT.instruction_id', 'CREDITOR_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'bic', 'cdtr_agt_bic', 'CREDITOR_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'lei', 'cdtr_agt_lei', 'CREDITOR_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'clearing_system_member_id', 'cdtr_agt_clr_sys_mmb_id', 'CREDITOR_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'name', 'cdtr_agt_bic', 'CREDITOR_AGENT', 'COALESCE_BIC', true),
    ('pacs.009.base', 'cdm_financial_institution', 'country', 'cdtr_agt_bic', 'CREDITOR_AGENT', 'COUNTRY_FROM_BIC', true),
    ('pacs.009.base', 'cdm_financial_institution', 'role', '''CREDITOR_AGENT''', 'CREDITOR_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'source_message_type', '''pacs.009''', 'CREDITOR_AGENT', NULL, true),

    -- Instructing Agent
    ('pacs.009.base', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'INSTRUCTING_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'instruction_id', '_CONTEXT.instruction_id', 'INSTRUCTING_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'bic', 'instg_agt_bic', 'INSTRUCTING_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'lei', 'instg_agt_lei', 'INSTRUCTING_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'name', 'instg_agt_bic', 'INSTRUCTING_AGENT', 'COALESCE_BIC', true),
    ('pacs.009.base', 'cdm_financial_institution', 'country', 'instg_agt_bic', 'INSTRUCTING_AGENT', 'COUNTRY_FROM_BIC', true),
    ('pacs.009.base', 'cdm_financial_institution', 'role', '''INSTRUCTING_AGENT''', 'INSTRUCTING_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'source_message_type', '''pacs.009''', 'INSTRUCTING_AGENT', NULL, true),

    -- Instructed Agent
    ('pacs.009.base', 'cdm_financial_institution', 'institution_id', '_GENERATED_UUID', 'INSTRUCTED_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'instruction_id', '_CONTEXT.instruction_id', 'INSTRUCTED_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'bic', 'instd_agt_bic', 'INSTRUCTED_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'lei', 'instd_agt_lei', 'INSTRUCTED_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'name', 'instd_agt_bic', 'INSTRUCTED_AGENT', 'COALESCE_BIC', true),
    ('pacs.009.base', 'cdm_financial_institution', 'country', 'instd_agt_bic', 'INSTRUCTED_AGENT', 'COUNTRY_FROM_BIC', true),
    ('pacs.009.base', 'cdm_financial_institution', 'role', '''INSTRUCTED_AGENT''', 'INSTRUCTED_AGENT', NULL, true),
    ('pacs.009.base', 'cdm_financial_institution', 'source_message_type', '''pacs.009''', 'INSTRUCTED_AGENT', NULL, true)
;

COMMIT;

-- =============================================================================
-- Verification Queries
-- =============================================================================

SELECT 'BASE FORMAT MAPPING COUNTS AFTER INSERT:' as info;

SELECT
    format_id,
    (SELECT COUNT(*) FROM mapping.silver_field_mappings WHERE format_id = mf.format_id AND is_active = true) as silver_mappings,
    (SELECT COUNT(*) FROM mapping.gold_field_mappings WHERE format_id = mf.format_id AND is_active = true) as gold_mappings
FROM mapping.message_formats mf
WHERE format_id IN ('pacs.002.base', 'pacs.004.base', 'pacs.009.base', 'pain.008.base', 'camt.056.base', 'pacs.008.base', 'pain.001.base')
ORDER BY format_id;
