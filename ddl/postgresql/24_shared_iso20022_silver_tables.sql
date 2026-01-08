-- GPS CDM - Shared ISO 20022 Silver Tables
-- ==========================================
-- Optimization: Single Silver table per ISO 20022 message type
-- All formats based on the same ISO 20022 message share one staging table
-- Discriminator column (source_format) identifies the originating scheme

-- =====================================================
-- STG_ISO20022_PACS008 - FI-to-FI Customer Credit Transfer
-- Used by: pacs.008, FEDWIRE, CHIPS, CHAPS, FPS, FEDNOW, RTP,
--          NPP, MEPS_PLUS, RTGS_HK, UAEFTS, INSTAPAY
-- =====================================================
CREATE TABLE IF NOT EXISTS silver.stg_iso20022_pacs008 (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,                        -- FK to bronze.raw_payment_messages
    source_format VARCHAR(20) NOT NULL,                 -- FEDWIRE, CHIPS, CHAPS, etc.

    -- ========================================
    -- Group Header (GrpHdr)
    -- ========================================
    grp_hdr_msg_id VARCHAR(35),                         -- GrpHdr/MsgId
    grp_hdr_cre_dt_tm TIMESTAMP,                        -- GrpHdr/CreDtTm
    grp_hdr_nb_of_txs INT,                              -- GrpHdr/NbOfTxs
    grp_hdr_ctrl_sum DECIMAL(18,4),                     -- GrpHdr/CtrlSum
    grp_hdr_sttlm_mtd VARCHAR(4),                       -- GrpHdr/SttlmInf/SttlmMtd (INDA, INGA, COVE, CLRG)
    grp_hdr_clr_sys_cd VARCHAR(35),                     -- GrpHdr/SttlmInf/ClrSys/Cd
    grp_hdr_clr_sys_prtry VARCHAR(35),                  -- GrpHdr/SttlmInf/ClrSys/Prtry
    grp_hdr_instr_for_nxt_agt TEXT,                     -- GrpHdr/SttlmInf/InstrdAgt instructions

    -- Instructing Agent (GrpHdr/InstgAgt)
    instg_agt_bic VARCHAR(11),                          -- InstgAgt/FinInstnId/BICFI
    instg_agt_lei VARCHAR(20),                          -- InstgAgt/FinInstnId/LEI
    instg_agt_nm VARCHAR(140),                          -- InstgAgt/FinInstnId/Nm
    instg_agt_clr_sys_mmb_id VARCHAR(35),               -- InstgAgt/FinInstnId/ClrSysMmbId/MmbId
    instg_agt_clr_sys_cd VARCHAR(5),                    -- InstgAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd
    instg_agt_ctry VARCHAR(2),                          -- InstgAgt/FinInstnId/PstlAdr/Ctry

    -- Instructed Agent (GrpHdr/InstdAgt)
    instd_agt_bic VARCHAR(11),                          -- InstdAgt/FinInstnId/BICFI
    instd_agt_lei VARCHAR(20),                          -- InstdAgt/FinInstnId/LEI
    instd_agt_nm VARCHAR(140),                          -- InstdAgt/FinInstnId/Nm
    instd_agt_clr_sys_mmb_id VARCHAR(35),               -- InstdAgt/FinInstnId/ClrSysMmbId/MmbId
    instd_agt_clr_sys_cd VARCHAR(5),                    -- InstdAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd
    instd_agt_ctry VARCHAR(2),                          -- InstdAgt/FinInstnId/PstlAdr/Ctry

    -- ========================================
    -- Credit Transfer Transaction (CdtTrfTxInf)
    -- ========================================
    -- Payment Identification
    pmt_id_instr_id VARCHAR(35),                        -- CdtTrfTxInf/PmtId/InstrId
    pmt_id_end_to_end_id VARCHAR(35),                   -- CdtTrfTxInf/PmtId/EndToEndId
    pmt_id_uetr VARCHAR(36),                            -- CdtTrfTxInf/PmtId/UETR
    pmt_id_tx_id VARCHAR(35),                           -- CdtTrfTxInf/PmtId/TxId
    pmt_id_clr_sys_ref VARCHAR(35),                     -- CdtTrfTxInf/PmtId/ClrSysRef

    -- Payment Type Information
    pmt_tp_inf_instr_prty VARCHAR(4),                   -- PmtTpInf/InstrPrty (HIGH, NORM)
    pmt_tp_inf_svc_lvl_cd VARCHAR(4),                   -- PmtTpInf/SvcLvl/Cd (SEPA, SDVA, etc.)
    pmt_tp_inf_svc_lvl_prtry VARCHAR(35),               -- PmtTpInf/SvcLvl/Prtry
    pmt_tp_inf_lcl_instrm_cd VARCHAR(35),               -- PmtTpInf/LclInstrm/Cd
    pmt_tp_inf_lcl_instrm_prtry VARCHAR(35),            -- PmtTpInf/LclInstrm/Prtry
    pmt_tp_inf_ctgy_purp_cd VARCHAR(4),                 -- PmtTpInf/CtgyPurp/Cd
    pmt_tp_inf_ctgy_purp_prtry VARCHAR(35),             -- PmtTpInf/CtgyPurp/Prtry
    pmt_tp_inf_clr_chanl VARCHAR(4),                    -- PmtTpInf/ClrChanl

    -- Amounts
    intr_bk_sttlm_amt DECIMAL(18,4),                    -- CdtTrfTxInf/IntrBkSttlmAmt
    intr_bk_sttlm_ccy VARCHAR(3),                       -- CdtTrfTxInf/IntrBkSttlmAmt/@Ccy
    intr_bk_sttlm_dt DATE,                              -- CdtTrfTxInf/IntrBkSttlmDt
    instd_amt DECIMAL(18,4),                            -- CdtTrfTxInf/InstdAmt
    instd_amt_ccy VARCHAR(3),                           -- CdtTrfTxInf/InstdAmt/@Ccy
    xchg_rate DECIMAL(18,10),                           -- CdtTrfTxInf/XchgRate

    -- Charge Information
    chrg_br VARCHAR(4),                                 -- CdtTrfTxInf/ChrgBr (DEBT, CRED, SHAR, SLEV)
    chrgs_inf_amt DECIMAL(18,4),                        -- CdtTrfTxInf/ChrgsInf/Amt
    chrgs_inf_ccy VARCHAR(3),                           -- CdtTrfTxInf/ChrgsInf/Amt/@Ccy
    chrgs_inf_agt_bic VARCHAR(11),                      -- CdtTrfTxInf/ChrgsInf/Agt/FinInstnId/BICFI
    chrgs_inf_tp_cd VARCHAR(4),                         -- CdtTrfTxInf/ChrgsInf/Tp/Cd

    -- ========================================
    -- Debtor (Dbtr)
    -- ========================================
    dbtr_nm VARCHAR(140),                               -- Dbtr/Nm
    dbtr_pstl_adr_dept VARCHAR(70),                     -- Dbtr/PstlAdr/Dept
    dbtr_pstl_adr_sub_dept VARCHAR(70),                 -- Dbtr/PstlAdr/SubDept
    dbtr_pstl_adr_strt_nm VARCHAR(70),                  -- Dbtr/PstlAdr/StrtNm
    dbtr_pstl_adr_bldg_nb VARCHAR(16),                  -- Dbtr/PstlAdr/BldgNb
    dbtr_pstl_adr_bldg_nm VARCHAR(35),                  -- Dbtr/PstlAdr/BldgNm
    dbtr_pstl_adr_flr VARCHAR(70),                      -- Dbtr/PstlAdr/Flr
    dbtr_pstl_adr_pst_bx VARCHAR(16),                   -- Dbtr/PstlAdr/PstBx
    dbtr_pstl_adr_room VARCHAR(70),                     -- Dbtr/PstlAdr/Room
    dbtr_pstl_adr_pst_cd VARCHAR(16),                   -- Dbtr/PstlAdr/PstCd
    dbtr_pstl_adr_twn_nm VARCHAR(35),                   -- Dbtr/PstlAdr/TwnNm
    dbtr_pstl_adr_twn_lctn_nm VARCHAR(35),              -- Dbtr/PstlAdr/TwnLctnNm
    dbtr_pstl_adr_dstrct_nm VARCHAR(35),                -- Dbtr/PstlAdr/DstrctNm
    dbtr_pstl_adr_ctry_sub_dvsn VARCHAR(35),            -- Dbtr/PstlAdr/CtrySubDvsn
    dbtr_pstl_adr_ctry VARCHAR(2),                      -- Dbtr/PstlAdr/Ctry
    dbtr_pstl_adr_adr_line TEXT[],                      -- Dbtr/PstlAdr/AdrLine (repeatable)
    -- Debtor Identification
    dbtr_id_org_id_any_bic VARCHAR(11),                 -- Dbtr/Id/OrgId/AnyBIC
    dbtr_id_org_id_lei VARCHAR(20),                     -- Dbtr/Id/OrgId/LEI
    dbtr_id_org_id_othr_id VARCHAR(35),                 -- Dbtr/Id/OrgId/Othr/Id
    dbtr_id_org_id_othr_schme_nm_cd VARCHAR(4),         -- Dbtr/Id/OrgId/Othr/SchmeNm/Cd
    dbtr_id_org_id_othr_schme_nm_prtry VARCHAR(35),     -- Dbtr/Id/OrgId/Othr/SchmeNm/Prtry
    dbtr_id_org_id_othr_issr VARCHAR(35),               -- Dbtr/Id/OrgId/Othr/Issr
    dbtr_id_prvt_id_dt_and_plc_of_birth_dt DATE,        -- Dbtr/Id/PrvtId/DtAndPlcOfBirth/BirthDt
    dbtr_id_prvt_id_dt_and_plc_of_birth_ctry VARCHAR(2),-- Dbtr/Id/PrvtId/DtAndPlcOfBirth/CtryOfBirth
    dbtr_id_prvt_id_othr_id VARCHAR(35),                -- Dbtr/Id/PrvtId/Othr/Id
    dbtr_id_prvt_id_othr_schme_nm_cd VARCHAR(4),        -- Dbtr/Id/PrvtId/Othr/SchmeNm/Cd
    dbtr_ctct_dtls_nm VARCHAR(140),                     -- Dbtr/CtctDtls/Nm
    dbtr_ctct_dtls_phne_nb VARCHAR(35),                 -- Dbtr/CtctDtls/PhneNb
    dbtr_ctct_dtls_email_adr VARCHAR(256),              -- Dbtr/CtctDtls/EmailAdr

    -- ========================================
    -- Debtor Account (DbtrAcct)
    -- ========================================
    dbtr_acct_id_iban VARCHAR(34),                      -- DbtrAcct/Id/IBAN
    dbtr_acct_id_othr_id VARCHAR(34),                   -- DbtrAcct/Id/Othr/Id
    dbtr_acct_id_othr_schme_nm_cd VARCHAR(4),           -- DbtrAcct/Id/Othr/SchmeNm/Cd
    dbtr_acct_id_othr_schme_nm_prtry VARCHAR(35),       -- DbtrAcct/Id/Othr/SchmeNm/Prtry
    dbtr_acct_tp_cd VARCHAR(4),                         -- DbtrAcct/Tp/Cd (CACC, SVGS, etc.)
    dbtr_acct_tp_prtry VARCHAR(35),                     -- DbtrAcct/Tp/Prtry
    dbtr_acct_ccy VARCHAR(3),                           -- DbtrAcct/Ccy
    dbtr_acct_nm VARCHAR(70),                           -- DbtrAcct/Nm
    dbtr_acct_prxy_tp_cd VARCHAR(4),                    -- DbtrAcct/Prxy/Tp/Cd
    dbtr_acct_prxy_id VARCHAR(256),                     -- DbtrAcct/Prxy/Id

    -- ========================================
    -- Debtor Agent (DbtrAgt)
    -- ========================================
    dbtr_agt_bic VARCHAR(11),                           -- DbtrAgt/FinInstnId/BICFI
    dbtr_agt_lei VARCHAR(20),                           -- DbtrAgt/FinInstnId/LEI
    dbtr_agt_nm VARCHAR(140),                           -- DbtrAgt/FinInstnId/Nm
    dbtr_agt_clr_sys_mmb_id VARCHAR(35),                -- DbtrAgt/FinInstnId/ClrSysMmbId/MmbId
    dbtr_agt_clr_sys_cd VARCHAR(5),                     -- DbtrAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd
    dbtr_agt_pstl_adr_strt_nm VARCHAR(70),              -- DbtrAgt/FinInstnId/PstlAdr/StrtNm
    dbtr_agt_pstl_adr_twn_nm VARCHAR(35),               -- DbtrAgt/FinInstnId/PstlAdr/TwnNm
    dbtr_agt_pstl_adr_ctry_sub_dvsn VARCHAR(35),        -- DbtrAgt/FinInstnId/PstlAdr/CtrySubDvsn
    dbtr_agt_pstl_adr_ctry VARCHAR(2),                  -- DbtrAgt/FinInstnId/PstlAdr/Ctry
    dbtr_agt_pstl_adr_adr_line TEXT[],                  -- DbtrAgt/FinInstnId/PstlAdr/AdrLine
    dbtr_agt_brnch_id VARCHAR(35),                      -- DbtrAgt/BrnchId/Id
    dbtr_agt_brnch_lei VARCHAR(20),                     -- DbtrAgt/BrnchId/LEI
    dbtr_agt_brnch_nm VARCHAR(140),                     -- DbtrAgt/BrnchId/Nm

    -- ========================================
    -- Creditor Agent (CdtrAgt)
    -- ========================================
    cdtr_agt_bic VARCHAR(11),                           -- CdtrAgt/FinInstnId/BICFI
    cdtr_agt_lei VARCHAR(20),                           -- CdtrAgt/FinInstnId/LEI
    cdtr_agt_nm VARCHAR(140),                           -- CdtrAgt/FinInstnId/Nm
    cdtr_agt_clr_sys_mmb_id VARCHAR(35),                -- CdtrAgt/FinInstnId/ClrSysMmbId/MmbId
    cdtr_agt_clr_sys_cd VARCHAR(5),                     -- CdtrAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd
    cdtr_agt_pstl_adr_strt_nm VARCHAR(70),              -- CdtrAgt/FinInstnId/PstlAdr/StrtNm
    cdtr_agt_pstl_adr_twn_nm VARCHAR(35),               -- CdtrAgt/FinInstnId/PstlAdr/TwnNm
    cdtr_agt_pstl_adr_ctry_sub_dvsn VARCHAR(35),        -- CdtrAgt/FinInstnId/PstlAdr/CtrySubDvsn
    cdtr_agt_pstl_adr_ctry VARCHAR(2),                  -- CdtrAgt/FinInstnId/PstlAdr/Ctry
    cdtr_agt_pstl_adr_adr_line TEXT[],                  -- CdtrAgt/FinInstnId/PstlAdr/AdrLine
    cdtr_agt_brnch_id VARCHAR(35),                      -- CdtrAgt/BrnchId/Id
    cdtr_agt_brnch_lei VARCHAR(20),                     -- CdtrAgt/BrnchId/LEI
    cdtr_agt_brnch_nm VARCHAR(140),                     -- CdtrAgt/BrnchId/Nm

    -- ========================================
    -- Creditor (Cdtr)
    -- ========================================
    cdtr_nm VARCHAR(140),                               -- Cdtr/Nm
    cdtr_pstl_adr_dept VARCHAR(70),                     -- Cdtr/PstlAdr/Dept
    cdtr_pstl_adr_sub_dept VARCHAR(70),                 -- Cdtr/PstlAdr/SubDept
    cdtr_pstl_adr_strt_nm VARCHAR(70),                  -- Cdtr/PstlAdr/StrtNm
    cdtr_pstl_adr_bldg_nb VARCHAR(16),                  -- Cdtr/PstlAdr/BldgNb
    cdtr_pstl_adr_bldg_nm VARCHAR(35),                  -- Cdtr/PstlAdr/BldgNm
    cdtr_pstl_adr_flr VARCHAR(70),                      -- Cdtr/PstlAdr/Flr
    cdtr_pstl_adr_pst_bx VARCHAR(16),                   -- Cdtr/PstlAdr/PstBx
    cdtr_pstl_adr_room VARCHAR(70),                     -- Cdtr/PstlAdr/Room
    cdtr_pstl_adr_pst_cd VARCHAR(16),                   -- Cdtr/PstlAdr/PstCd
    cdtr_pstl_adr_twn_nm VARCHAR(35),                   -- Cdtr/PstlAdr/TwnNm
    cdtr_pstl_adr_twn_lctn_nm VARCHAR(35),              -- Cdtr/PstlAdr/TwnLctnNm
    cdtr_pstl_adr_dstrct_nm VARCHAR(35),                -- Cdtr/PstlAdr/DstrctNm
    cdtr_pstl_adr_ctry_sub_dvsn VARCHAR(35),            -- Cdtr/PstlAdr/CtrySubDvsn
    cdtr_pstl_adr_ctry VARCHAR(2),                      -- Cdtr/PstlAdr/Ctry
    cdtr_pstl_adr_adr_line TEXT[],                      -- Cdtr/PstlAdr/AdrLine (repeatable)
    -- Creditor Identification
    cdtr_id_org_id_any_bic VARCHAR(11),                 -- Cdtr/Id/OrgId/AnyBIC
    cdtr_id_org_id_lei VARCHAR(20),                     -- Cdtr/Id/OrgId/LEI
    cdtr_id_org_id_othr_id VARCHAR(35),                 -- Cdtr/Id/OrgId/Othr/Id
    cdtr_id_org_id_othr_schme_nm_cd VARCHAR(4),         -- Cdtr/Id/OrgId/Othr/SchmeNm/Cd
    cdtr_id_org_id_othr_schme_nm_prtry VARCHAR(35),     -- Cdtr/Id/OrgId/Othr/SchmeNm/Prtry
    cdtr_id_org_id_othr_issr VARCHAR(35),               -- Cdtr/Id/OrgId/Othr/Issr
    cdtr_id_prvt_id_dt_and_plc_of_birth_dt DATE,        -- Cdtr/Id/PrvtId/DtAndPlcOfBirth/BirthDt
    cdtr_id_prvt_id_dt_and_plc_of_birth_ctry VARCHAR(2),-- Cdtr/Id/PrvtId/DtAndPlcOfBirth/CtryOfBirth
    cdtr_id_prvt_id_othr_id VARCHAR(35),                -- Cdtr/Id/PrvtId/Othr/Id
    cdtr_id_prvt_id_othr_schme_nm_cd VARCHAR(4),        -- Cdtr/Id/PrvtId/Othr/SchmeNm/Cd
    cdtr_ctct_dtls_nm VARCHAR(140),                     -- Cdtr/CtctDtls/Nm
    cdtr_ctct_dtls_phne_nb VARCHAR(35),                 -- Cdtr/CtctDtls/PhneNb
    cdtr_ctct_dtls_email_adr VARCHAR(256),              -- Cdtr/CtctDtls/EmailAdr

    -- ========================================
    -- Creditor Account (CdtrAcct)
    -- ========================================
    cdtr_acct_id_iban VARCHAR(34),                      -- CdtrAcct/Id/IBAN
    cdtr_acct_id_othr_id VARCHAR(34),                   -- CdtrAcct/Id/Othr/Id
    cdtr_acct_id_othr_schme_nm_cd VARCHAR(4),           -- CdtrAcct/Id/Othr/SchmeNm/Cd
    cdtr_acct_id_othr_schme_nm_prtry VARCHAR(35),       -- CdtrAcct/Id/Othr/SchmeNm/Prtry
    cdtr_acct_tp_cd VARCHAR(4),                         -- CdtrAcct/Tp/Cd (CACC, SVGS, etc.)
    cdtr_acct_tp_prtry VARCHAR(35),                     -- CdtrAcct/Tp/Prtry
    cdtr_acct_ccy VARCHAR(3),                           -- CdtrAcct/Ccy
    cdtr_acct_nm VARCHAR(70),                           -- CdtrAcct/Nm
    cdtr_acct_prxy_tp_cd VARCHAR(4),                    -- CdtrAcct/Prxy/Tp/Cd
    cdtr_acct_prxy_id VARCHAR(256),                     -- CdtrAcct/Prxy/Id

    -- ========================================
    -- Intermediary Agents (optional)
    -- ========================================
    -- Intermediary Agent 1
    intrmy_agt1_bic VARCHAR(11),                        -- IntrmyAgt1/FinInstnId/BICFI
    intrmy_agt1_lei VARCHAR(20),                        -- IntrmyAgt1/FinInstnId/LEI
    intrmy_agt1_nm VARCHAR(140),                        -- IntrmyAgt1/FinInstnId/Nm
    intrmy_agt1_clr_sys_mmb_id VARCHAR(35),             -- IntrmyAgt1/FinInstnId/ClrSysMmbId/MmbId
    intrmy_agt1_clr_sys_cd VARCHAR(5),                  -- IntrmyAgt1/FinInstnId/ClrSysMmbId/ClrSysId/Cd
    intrmy_agt1_ctry VARCHAR(2),                        -- IntrmyAgt1/FinInstnId/PstlAdr/Ctry
    intrmy_agt1_acct_id VARCHAR(34),                    -- IntrmyAgt1Acct/Id/IBAN or Othr/Id
    -- Intermediary Agent 2
    intrmy_agt2_bic VARCHAR(11),                        -- IntrmyAgt2/FinInstnId/BICFI
    intrmy_agt2_lei VARCHAR(20),                        -- IntrmyAgt2/FinInstnId/LEI
    intrmy_agt2_nm VARCHAR(140),                        -- IntrmyAgt2/FinInstnId/Nm
    intrmy_agt2_clr_sys_mmb_id VARCHAR(35),             -- IntrmyAgt2/FinInstnId/ClrSysMmbId/MmbId
    intrmy_agt2_clr_sys_cd VARCHAR(5),                  -- IntrmyAgt2/FinInstnId/ClrSysMmbId/ClrSysId/Cd
    intrmy_agt2_ctry VARCHAR(2),                        -- IntrmyAgt2/FinInstnId/PstlAdr/Ctry
    intrmy_agt2_acct_id VARCHAR(34),                    -- IntrmyAgt2Acct/Id/IBAN or Othr/Id
    -- Intermediary Agent 3
    intrmy_agt3_bic VARCHAR(11),                        -- IntrmyAgt3/FinInstnId/BICFI
    intrmy_agt3_clr_sys_mmb_id VARCHAR(35),             -- IntrmyAgt3/FinInstnId/ClrSysMmbId/MmbId
    intrmy_agt3_ctry VARCHAR(2),                        -- IntrmyAgt3/FinInstnId/PstlAdr/Ctry

    -- ========================================
    -- Ultimate Parties (optional)
    -- ========================================
    -- Ultimate Debtor
    ultmt_dbtr_nm VARCHAR(140),                         -- UltmtDbtr/Nm
    ultmt_dbtr_pstl_adr_ctry VARCHAR(2),                -- UltmtDbtr/PstlAdr/Ctry
    ultmt_dbtr_id_org_id_lei VARCHAR(20),               -- UltmtDbtr/Id/OrgId/LEI
    ultmt_dbtr_id_org_id_othr_id VARCHAR(35),           -- UltmtDbtr/Id/OrgId/Othr/Id
    ultmt_dbtr_id_prvt_id_othr_id VARCHAR(35),          -- UltmtDbtr/Id/PrvtId/Othr/Id
    -- Ultimate Creditor
    ultmt_cdtr_nm VARCHAR(140),                         -- UltmtCdtr/Nm
    ultmt_cdtr_pstl_adr_ctry VARCHAR(2),                -- UltmtCdtr/PstlAdr/Ctry
    ultmt_cdtr_id_org_id_lei VARCHAR(20),               -- UltmtCdtr/Id/OrgId/LEI
    ultmt_cdtr_id_org_id_othr_id VARCHAR(35),           -- UltmtCdtr/Id/OrgId/Othr/Id
    ultmt_cdtr_id_prvt_id_othr_id VARCHAR(35),          -- UltmtCdtr/Id/PrvtId/Othr/Id

    -- ========================================
    -- Remittance Information (RmtInf)
    -- ========================================
    rmt_inf_ustrd TEXT[],                               -- RmtInf/Ustrd (repeatable)
    -- Structured Remittance
    rmt_inf_strd_rfrd_doc_tp_cd_or_prtry VARCHAR(35),   -- RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd
    rmt_inf_strd_rfrd_doc_nb VARCHAR(35),               -- RmtInf/Strd/RfrdDocInf/Nb
    rmt_inf_strd_rfrd_doc_rltd_dt DATE,                 -- RmtInf/Strd/RfrdDocInf/RltdDt
    rmt_inf_strd_cdtr_ref_inf_tp_cd_or_prtry VARCHAR(35),-- RmtInf/Strd/CdtrRefInf/Tp/CdOrPrtry/Cd
    rmt_inf_strd_cdtr_ref_inf_ref VARCHAR(35),          -- RmtInf/Strd/CdtrRefInf/Ref
    rmt_inf_strd_invr_nm VARCHAR(140),                  -- RmtInf/Strd/Invr/Nm
    rmt_inf_strd_invcee_nm VARCHAR(140),                -- RmtInf/Strd/Invcee/Nm
    rmt_inf_strd JSONB,                                 -- Full structured remittance as JSON

    -- ========================================
    -- Purpose & Regulatory
    -- ========================================
    purp_cd VARCHAR(4),                                 -- Purp/Cd (ISO 20022 purpose code)
    purp_prtry VARCHAR(35),                             -- Purp/Prtry
    rgltry_rptg JSONB,                                  -- RgltryRptg array as JSON
    tax JSONB,                                          -- Tax element as JSON

    -- ========================================
    -- Additional Scheme-Specific Fields
    -- ========================================
    -- These capture any scheme-specific extensions
    splmtry_data JSONB,                                 -- SplmtryData elements as JSON

    -- Scheme-specific identifiers stored as JSON for flexibility
    scheme_identifiers JSONB,                           -- E.g., {"fedwire_imad": "...", "chips_ssn": "..."}

    -- ========================================
    -- Processing Metadata
    -- ========================================
    processing_status VARCHAR(20) DEFAULT 'PENDING',    -- PENDING, PROCESSED, FAILED
    processed_to_gold_at TIMESTAMP,
    processing_error TEXT,

    -- Lineage
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs008_source ON silver.stg_iso20022_pacs008(source_format);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs008_msg_id ON silver.stg_iso20022_pacs008(grp_hdr_msg_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs008_e2e ON silver.stg_iso20022_pacs008(pmt_id_end_to_end_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs008_uetr ON silver.stg_iso20022_pacs008(pmt_id_uetr);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs008_status ON silver.stg_iso20022_pacs008(processing_status);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs008_raw ON silver.stg_iso20022_pacs008(raw_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs008_sttlm_dt ON silver.stg_iso20022_pacs008(intr_bk_sttlm_dt);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs008_batch ON silver.stg_iso20022_pacs008(_batch_id);


-- =====================================================
-- STG_ISO20022_PACS009 - FI-to-FI Institution Credit Transfer
-- Used by: pacs.009, TARGET2
-- =====================================================
CREATE TABLE IF NOT EXISTS silver.stg_iso20022_pacs009 (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    source_format VARCHAR(20) NOT NULL,                 -- TARGET2, pacs.009

    -- Group Header
    grp_hdr_msg_id VARCHAR(35),
    grp_hdr_cre_dt_tm TIMESTAMP,
    grp_hdr_nb_of_txs INT,
    grp_hdr_ctrl_sum DECIMAL(18,4),
    grp_hdr_sttlm_mtd VARCHAR(4),
    grp_hdr_clr_sys_cd VARCHAR(35),
    grp_hdr_clr_sys_prtry VARCHAR(35),
    instg_agt_bic VARCHAR(11),
    instg_agt_lei VARCHAR(20),
    instd_agt_bic VARCHAR(11),
    instd_agt_lei VARCHAR(20),

    -- Credit Transfer Transaction
    pmt_id_instr_id VARCHAR(35),
    pmt_id_end_to_end_id VARCHAR(35),
    pmt_id_uetr VARCHAR(36),
    pmt_id_tx_id VARCHAR(35),
    pmt_id_clr_sys_ref VARCHAR(35),
    pmt_tp_inf_instr_prty VARCHAR(4),
    pmt_tp_inf_svc_lvl_cd VARCHAR(4),

    -- Amounts
    intr_bk_sttlm_amt DECIMAL(18,4),
    intr_bk_sttlm_ccy VARCHAR(3),
    intr_bk_sttlm_dt DATE,

    -- Debtor Agent (initiating FI in pacs.009)
    dbtr_agt_bic VARCHAR(11),
    dbtr_agt_lei VARCHAR(20),
    dbtr_agt_nm VARCHAR(140),
    dbtr_agt_clr_sys_mmb_id VARCHAR(35),
    dbtr_agt_clr_sys_cd VARCHAR(5),
    dbtr_agt_ctry VARCHAR(2),
    dbtr_agt_acct_id VARCHAR(34),
    dbtr_agt_acct_ccy VARCHAR(3),

    -- Creditor Agent (receiving FI in pacs.009)
    cdtr_agt_bic VARCHAR(11),
    cdtr_agt_lei VARCHAR(20),
    cdtr_agt_nm VARCHAR(140),
    cdtr_agt_clr_sys_mmb_id VARCHAR(35),
    cdtr_agt_clr_sys_cd VARCHAR(5),
    cdtr_agt_ctry VARCHAR(2),
    cdtr_agt_acct_id VARCHAR(34),
    cdtr_agt_acct_ccy VARCHAR(3),

    -- Intermediary Agents
    intrmy_agt1_bic VARCHAR(11),
    intrmy_agt1_clr_sys_mmb_id VARCHAR(35),
    intrmy_agt1_ctry VARCHAR(2),
    intrmy_agt2_bic VARCHAR(11),
    intrmy_agt2_clr_sys_mmb_id VARCHAR(35),
    intrmy_agt2_ctry VARCHAR(2),

    -- Underlying Customer Credit Transfer (optional cover info)
    undrlyg_cstmr_cdt_trf JSONB,

    -- Remittance & Purpose
    rmt_inf_ustrd TEXT[],
    purp_cd VARCHAR(4),
    purp_prtry VARCHAR(35),
    splmtry_data JSONB,
    scheme_identifiers JSONB,

    -- Processing Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_gold_at TIMESTAMP,
    processing_error TEXT,
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs009_source ON silver.stg_iso20022_pacs009(source_format);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs009_msg_id ON silver.stg_iso20022_pacs009(grp_hdr_msg_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs009_status ON silver.stg_iso20022_pacs009(processing_status);


-- =====================================================
-- STG_ISO20022_PAIN001 - Customer Credit Transfer Initiation
-- Used by: pain.001, SEPA
-- =====================================================
CREATE TABLE IF NOT EXISTS silver.stg_iso20022_pain001 (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    source_format VARCHAR(20) NOT NULL,                 -- pain.001, SEPA

    -- Group Header
    grp_hdr_msg_id VARCHAR(35),
    grp_hdr_cre_dt_tm TIMESTAMP,
    grp_hdr_nb_of_txs INT,
    grp_hdr_ctrl_sum DECIMAL(18,4),
    grp_hdr_initg_pty_nm VARCHAR(140),
    grp_hdr_initg_pty_id_org_id_lei VARCHAR(20),
    grp_hdr_initg_pty_id_org_id_othr_id VARCHAR(35),

    -- Payment Information
    pmt_inf_id VARCHAR(35),
    pmt_mtd VARCHAR(3),                                 -- TRF, CHK, TRA
    btch_bookg BOOLEAN,
    nb_of_txs INT,
    ctrl_sum DECIMAL(18,4),
    pmt_tp_inf_instr_prty VARCHAR(4),
    pmt_tp_inf_svc_lvl_cd VARCHAR(4),
    pmt_tp_inf_lcl_instrm_cd VARCHAR(35),
    pmt_tp_inf_ctgy_purp_cd VARCHAR(4),
    reqd_exctn_dt DATE,

    -- Debtor
    dbtr_nm VARCHAR(140),
    dbtr_pstl_adr_strt_nm VARCHAR(70),
    dbtr_pstl_adr_bldg_nb VARCHAR(16),
    dbtr_pstl_adr_pst_cd VARCHAR(16),
    dbtr_pstl_adr_twn_nm VARCHAR(35),
    dbtr_pstl_adr_ctry VARCHAR(2),
    dbtr_id_org_id_lei VARCHAR(20),
    dbtr_id_org_id_othr_id VARCHAR(35),
    dbtr_id_prvt_id_othr_id VARCHAR(35),

    -- Debtor Account
    dbtr_acct_id_iban VARCHAR(34),
    dbtr_acct_id_othr_id VARCHAR(34),
    dbtr_acct_ccy VARCHAR(3),

    -- Debtor Agent
    dbtr_agt_bic VARCHAR(11),
    dbtr_agt_clr_sys_mmb_id VARCHAR(35),
    dbtr_agt_nm VARCHAR(140),

    -- Credit Transfer Transaction
    pmt_id_instr_id VARCHAR(35),
    pmt_id_end_to_end_id VARCHAR(35),
    instd_amt DECIMAL(18,4),
    instd_amt_ccy VARCHAR(3),
    eqvt_amt DECIMAL(18,4),
    eqvt_amt_ccy VARCHAR(3),
    xchg_rate_inf_xchg_rate DECIMAL(18,10),
    chrg_br VARCHAR(4),

    -- Creditor Agent
    cdtr_agt_bic VARCHAR(11),
    cdtr_agt_clr_sys_mmb_id VARCHAR(35),
    cdtr_agt_nm VARCHAR(140),

    -- Creditor
    cdtr_nm VARCHAR(140),
    cdtr_pstl_adr_strt_nm VARCHAR(70),
    cdtr_pstl_adr_bldg_nb VARCHAR(16),
    cdtr_pstl_adr_pst_cd VARCHAR(16),
    cdtr_pstl_adr_twn_nm VARCHAR(35),
    cdtr_pstl_adr_ctry VARCHAR(2),
    cdtr_id_org_id_lei VARCHAR(20),
    cdtr_id_org_id_othr_id VARCHAR(35),
    cdtr_id_prvt_id_othr_id VARCHAR(35),

    -- Creditor Account
    cdtr_acct_id_iban VARCHAR(34),
    cdtr_acct_id_othr_id VARCHAR(34),
    cdtr_acct_ccy VARCHAR(3),

    -- Ultimate Parties
    ultmt_dbtr_nm VARCHAR(140),
    ultmt_dbtr_id_org_id_othr_id VARCHAR(35),
    ultmt_cdtr_nm VARCHAR(140),
    ultmt_cdtr_id_org_id_othr_id VARCHAR(35),

    -- Remittance & Purpose
    purp_cd VARCHAR(4),
    purp_prtry VARCHAR(35),
    rmt_inf_ustrd TEXT[],
    rmt_inf_strd JSONB,
    rgltry_rptg JSONB,
    splmtry_data JSONB,
    scheme_identifiers JSONB,

    -- Processing Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_gold_at TIMESTAMP,
    processing_error TEXT,
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pain001_source ON silver.stg_iso20022_pain001(source_format);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pain001_msg_id ON silver.stg_iso20022_pain001(grp_hdr_msg_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pain001_status ON silver.stg_iso20022_pain001(processing_status);


-- =====================================================
-- STG_ISO20022_CAMT053 - Bank-to-Customer Account Statement
-- Used by: camt.053
-- =====================================================
CREATE TABLE IF NOT EXISTS silver.stg_iso20022_camt053 (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    source_format VARCHAR(20) NOT NULL,                 -- camt.053

    -- Group Header
    grp_hdr_msg_id VARCHAR(35),
    grp_hdr_cre_dt_tm TIMESTAMP,
    grp_hdr_msg_rcpt_nm VARCHAR(140),

    -- Statement
    stmt_id VARCHAR(35),
    stmt_elctrnc_seq_nb BIGINT,
    stmt_cre_dt_tm TIMESTAMP,
    stmt_fr_dt_tm TIMESTAMP,
    stmt_to_dt_tm TIMESTAMP,

    -- Account
    acct_id_iban VARCHAR(34),
    acct_id_othr_id VARCHAR(34),
    acct_ccy VARCHAR(3),
    acct_ownr_nm VARCHAR(140),
    acct_svcr_bic VARCHAR(11),
    acct_svcr_nm VARCHAR(140),

    -- Balances
    bal_tp_cd_cd VARCHAR(4),                            -- OPBD, CLBD, ITBD, etc.
    bal_amt DECIMAL(18,4),
    bal_ccy VARCHAR(3),
    bal_cdt_dbt_ind VARCHAR(4),                         -- CRDT, DBIT
    bal_dt DATE,
    opening_bal DECIMAL(18,4),
    opening_bal_ccy VARCHAR(3),
    closing_bal DECIMAL(18,4),
    closing_bal_ccy VARCHAR(3),
    available_bal DECIMAL(18,4),
    available_bal_ccy VARCHAR(3),

    -- Transaction Summary
    ttl_nb_of_ntries INT,
    ttl_sum DECIMAL(18,4),
    ttl_cdt_nb_of_ntries INT,
    ttl_cdt_sum DECIMAL(18,4),
    ttl_dbt_nb_of_ntries INT,
    ttl_dbt_sum DECIMAL(18,4),

    -- Entry details (often stored separately, but summary here)
    ntry_count INT,
    ntries JSONB,                                       -- Array of entries as JSON

    -- Processing Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_gold_at TIMESTAMP,
    processing_error TEXT,
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_iso20022_camt053_source ON silver.stg_iso20022_camt053(source_format);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_camt053_stmt ON silver.stg_iso20022_camt053(stmt_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_camt053_acct ON silver.stg_iso20022_camt053(acct_id_iban);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_camt053_status ON silver.stg_iso20022_camt053(processing_status);


-- =====================================================
-- Update message_formats to point to shared tables
-- =====================================================
-- This will be done via UPDATE statements to change silver_table
-- for all pacs.008-based formats to use stg_iso20022_pacs008


-- Views to maintain backward compatibility with old table names
-- =====================================================
CREATE OR REPLACE VIEW silver.stg_pacs008_v AS
SELECT * FROM silver.stg_iso20022_pacs008 WHERE source_format = 'pacs.008';

CREATE OR REPLACE VIEW silver.stg_fedwire_v AS
SELECT * FROM silver.stg_iso20022_pacs008 WHERE source_format = 'FEDWIRE';

CREATE OR REPLACE VIEW silver.stg_chips_v AS
SELECT * FROM silver.stg_iso20022_pacs008 WHERE source_format = 'CHIPS';

CREATE OR REPLACE VIEW silver.stg_chaps_v AS
SELECT * FROM silver.stg_iso20022_pacs008 WHERE source_format = 'CHAPS';

CREATE OR REPLACE VIEW silver.stg_fps_v AS
SELECT * FROM silver.stg_iso20022_pacs008 WHERE source_format = 'FPS';

CREATE OR REPLACE VIEW silver.stg_fednow_v AS
SELECT * FROM silver.stg_iso20022_pacs008 WHERE source_format = 'FEDNOW';

CREATE OR REPLACE VIEW silver.stg_rtp_v AS
SELECT * FROM silver.stg_iso20022_pacs008 WHERE source_format = 'RTP';

CREATE OR REPLACE VIEW silver.stg_npp_v AS
SELECT * FROM silver.stg_iso20022_pacs008 WHERE source_format = 'NPP';

CREATE OR REPLACE VIEW silver.stg_meps_plus_v AS
SELECT * FROM silver.stg_iso20022_pacs008 WHERE source_format = 'MEPS_PLUS';

CREATE OR REPLACE VIEW silver.stg_rtgs_hk_v AS
SELECT * FROM silver.stg_iso20022_pacs008 WHERE source_format = 'RTGS_HK';

CREATE OR REPLACE VIEW silver.stg_uaefts_v AS
SELECT * FROM silver.stg_iso20022_pacs008 WHERE source_format = 'UAEFTS';

CREATE OR REPLACE VIEW silver.stg_instapay_v AS
SELECT * FROM silver.stg_iso20022_pacs008 WHERE source_format = 'INSTAPAY';

CREATE OR REPLACE VIEW silver.stg_target2_v AS
SELECT * FROM silver.stg_iso20022_pacs009 WHERE source_format = 'TARGET2';

CREATE OR REPLACE VIEW silver.stg_sepa_v AS
SELECT * FROM silver.stg_iso20022_pain001 WHERE source_format = 'SEPA';


-- =====================================================
-- STG_ISO20022_PACS002 - Payment Status Report
-- Used by: pacs.002, STATUS reports for all payment systems
-- =====================================================
CREATE TABLE IF NOT EXISTS silver.stg_iso20022_pacs002 (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    source_format VARCHAR(20) NOT NULL,

    -- Group Header
    grp_hdr_msg_id VARCHAR(35),
    grp_hdr_cre_dt_tm TIMESTAMP,

    -- Original Group Information
    orgnl_grp_inf_orgnl_msg_id VARCHAR(35),
    orgnl_grp_inf_orgnl_msg_nm_id VARCHAR(35),
    orgnl_grp_inf_orgnl_cre_dt_tm TIMESTAMP,
    orgnl_grp_inf_orgnl_nb_of_txs INT,
    orgnl_grp_inf_grp_sts VARCHAR(4),
    orgnl_grp_inf_sts_rsn_cd VARCHAR(4),
    orgnl_grp_inf_sts_rsn_addtl_inf TEXT,

    -- Transaction Information and Status
    tx_inf_sts_id VARCHAR(35),
    tx_inf_orgnl_instr_id VARCHAR(35),
    tx_inf_orgnl_end_to_end_id VARCHAR(35),
    tx_inf_orgnl_uetr VARCHAR(36),
    tx_inf_tx_sts VARCHAR(4),
    tx_inf_sts_rsn_cd VARCHAR(4),
    tx_inf_sts_rsn_addtl_inf TEXT,
    tx_inf_accpt_dt_tm TIMESTAMP,
    tx_inf_acct_svcr_ref VARCHAR(35),
    tx_inf_clr_sys_ref VARCHAR(35),

    -- Original Transaction Reference
    orgnl_tx_ref_intr_bk_sttlm_amt DECIMAL(18,4),
    orgnl_tx_ref_intr_bk_sttlm_ccy VARCHAR(3),
    orgnl_tx_ref_intr_bk_sttlm_dt DATE,
    orgnl_tx_ref_reqd_exctn_dt DATE,

    -- Debtor Information (from original)
    orgnl_tx_ref_dbtr_nm VARCHAR(140),
    orgnl_tx_ref_dbtr_acct_id_iban VARCHAR(34),
    orgnl_tx_ref_dbtr_acct_id_othr VARCHAR(35),
    orgnl_tx_ref_dbtr_agt_bic VARCHAR(11),

    -- Creditor Information (from original)
    orgnl_tx_ref_cdtr_nm VARCHAR(140),
    orgnl_tx_ref_cdtr_acct_id_iban VARCHAR(34),
    orgnl_tx_ref_cdtr_acct_id_othr VARCHAR(35),
    orgnl_tx_ref_cdtr_agt_bic VARCHAR(11),

    -- Processing Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_gold_at TIMESTAMP,
    processing_error TEXT,
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs002_raw_id ON silver.stg_iso20022_pacs002(raw_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs002_batch_id ON silver.stg_iso20022_pacs002(_batch_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs002_msg_id ON silver.stg_iso20022_pacs002(grp_hdr_msg_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs002_orgnl_msg_id ON silver.stg_iso20022_pacs002(orgnl_grp_inf_orgnl_msg_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs002_source ON silver.stg_iso20022_pacs002(source_format);


-- =====================================================
-- STG_ISO20022_PACS004 - Payment Return
-- Used by: pacs.004, RETURN messages for all payment systems
-- =====================================================
CREATE TABLE IF NOT EXISTS silver.stg_iso20022_pacs004 (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    source_format VARCHAR(20) NOT NULL,

    -- Group Header
    grp_hdr_msg_id VARCHAR(35),
    grp_hdr_cre_dt_tm TIMESTAMP,
    grp_hdr_nb_of_txs INT,
    grp_hdr_sttlm_mtd VARCHAR(4),
    grp_hdr_clr_sys_cd VARCHAR(5),

    -- Original Group Information
    orgnl_grp_inf_orgnl_msg_id VARCHAR(35),
    orgnl_grp_inf_orgnl_msg_nm_id VARCHAR(35),
    orgnl_grp_inf_orgnl_cre_dt_tm TIMESTAMP,

    -- Transaction Information
    tx_inf_rtr_id VARCHAR(35),
    tx_inf_orgnl_instr_id VARCHAR(35),
    tx_inf_orgnl_end_to_end_id VARCHAR(35),
    tx_inf_orgnl_tx_id VARCHAR(35),
    tx_inf_orgnl_uetr VARCHAR(36),
    tx_inf_orgnl_clr_sys_ref VARCHAR(35),

    -- Return Reason
    tx_inf_rtr_rsn_cd VARCHAR(4),
    tx_inf_rtr_rsn_prtry VARCHAR(35),
    tx_inf_rtr_rsn_addtl_inf TEXT,

    -- Returned Amount
    tx_inf_rtrd_intr_bk_sttlm_amt DECIMAL(18,4),
    tx_inf_rtrd_intr_bk_sttlm_ccy VARCHAR(3),
    tx_inf_intr_bk_sttlm_dt DATE,

    -- Original Transaction Reference
    orgnl_tx_ref_intr_bk_sttlm_amt DECIMAL(18,4),
    orgnl_tx_ref_intr_bk_sttlm_ccy VARCHAR(3),
    orgnl_tx_ref_intr_bk_sttlm_dt DATE,

    -- Debtor (Original)
    orgnl_tx_ref_dbtr_nm VARCHAR(140),
    orgnl_tx_ref_dbtr_pstl_adr_ctry VARCHAR(2),
    orgnl_tx_ref_dbtr_acct_id_iban VARCHAR(34),
    orgnl_tx_ref_dbtr_acct_id_othr VARCHAR(35),
    orgnl_tx_ref_dbtr_agt_bic VARCHAR(11),
    orgnl_tx_ref_dbtr_agt_clr_sys_mmb_id VARCHAR(35),

    -- Creditor (Original)
    orgnl_tx_ref_cdtr_nm VARCHAR(140),
    orgnl_tx_ref_cdtr_pstl_adr_ctry VARCHAR(2),
    orgnl_tx_ref_cdtr_acct_id_iban VARCHAR(34),
    orgnl_tx_ref_cdtr_acct_id_othr VARCHAR(35),
    orgnl_tx_ref_cdtr_agt_bic VARCHAR(11),
    orgnl_tx_ref_cdtr_agt_clr_sys_mmb_id VARCHAR(35),

    -- Instructing/Instructed Agents
    instg_agt_bic VARCHAR(11),
    instg_agt_clr_sys_mmb_id VARCHAR(35),
    instd_agt_bic VARCHAR(11),
    instd_agt_clr_sys_mmb_id VARCHAR(35),

    -- Remittance Information
    rmt_inf_ustrd TEXT[],

    -- Processing Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_gold_at TIMESTAMP,
    processing_error TEXT,
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs004_raw_id ON silver.stg_iso20022_pacs004(raw_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs004_batch_id ON silver.stg_iso20022_pacs004(_batch_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs004_msg_id ON silver.stg_iso20022_pacs004(grp_hdr_msg_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs004_orgnl_msg_id ON silver.stg_iso20022_pacs004(orgnl_grp_inf_orgnl_msg_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pacs004_source ON silver.stg_iso20022_pacs004(source_format);


-- =====================================================
-- STG_ISO20022_PAIN008 - Customer Direct Debit Initiation
-- Used by: pain.008, SEPA SDD
-- =====================================================
CREATE TABLE IF NOT EXISTS silver.stg_iso20022_pain008 (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    source_format VARCHAR(20) NOT NULL,

    -- Group Header
    grp_hdr_msg_id VARCHAR(35),
    grp_hdr_cre_dt_tm TIMESTAMP,
    grp_hdr_nb_of_txs INT,
    grp_hdr_ctrl_sum DECIMAL(18,4),
    grp_hdr_initg_pty_nm VARCHAR(140),
    grp_hdr_initg_pty_id_org_id_othr_id VARCHAR(35),

    -- Payment Information
    pmt_inf_id VARCHAR(35),
    pmt_mtd VARCHAR(3),
    pmt_tp_inf_svc_lvl_cd VARCHAR(4),
    pmt_tp_inf_lcl_instrm_cd VARCHAR(35),
    pmt_tp_inf_seq_tp VARCHAR(4),
    pmt_tp_inf_ctgy_purp_cd VARCHAR(4),
    reqd_colltn_dt DATE,

    -- Creditor (Initiating Party)
    cdtr_nm VARCHAR(140),
    cdtr_pstl_adr_strt_nm VARCHAR(70),
    cdtr_pstl_adr_bldg_nb VARCHAR(16),
    cdtr_pstl_adr_pst_cd VARCHAR(16),
    cdtr_pstl_adr_twn_nm VARCHAR(35),
    cdtr_pstl_adr_ctry VARCHAR(2),
    cdtr_id_prvt_id_othr_id VARCHAR(35),
    cdtr_id_prvt_id_othr_schme_nm_prtry VARCHAR(35),
    cdtr_id_org_id_othr_id VARCHAR(35),

    -- Creditor Account
    cdtr_acct_id_iban VARCHAR(34),
    cdtr_acct_id_othr_id VARCHAR(35),
    cdtr_acct_ccy VARCHAR(3),

    -- Creditor Agent
    cdtr_agt_bic VARCHAR(11),
    cdtr_agt_clr_sys_mmb_id VARCHAR(35),

    -- Direct Debit Transaction Information
    drct_dbt_tx_inf_pmt_id_instr_id VARCHAR(35),
    drct_dbt_tx_inf_pmt_id_end_to_end_id VARCHAR(35),
    drct_dbt_tx_inf_instd_amt DECIMAL(18,4),
    drct_dbt_tx_inf_instd_amt_ccy VARCHAR(3),
    drct_dbt_tx_inf_chrgbr VARCHAR(4),

    -- Mandate Information
    drct_dbt_tx_inf_mndt_id VARCHAR(35),
    drct_dbt_tx_inf_mndt_dt_of_sgntr DATE,
    drct_dbt_tx_inf_mndt_amdmnt_ind BOOLEAN,

    -- Debtor Agent
    dbtr_agt_bic VARCHAR(11),
    dbtr_agt_clr_sys_mmb_id VARCHAR(35),

    -- Debtor
    dbtr_nm VARCHAR(140),
    dbtr_pstl_adr_strt_nm VARCHAR(70),
    dbtr_pstl_adr_pst_cd VARCHAR(16),
    dbtr_pstl_adr_twn_nm VARCHAR(35),
    dbtr_pstl_adr_ctry VARCHAR(2),

    -- Debtor Account
    dbtr_acct_id_iban VARCHAR(34),
    dbtr_acct_id_othr_id VARCHAR(35),

    -- Remittance Information
    rmt_inf_ustrd TEXT[],
    rmt_inf_strd_cdtr_ref_inf_ref VARCHAR(35),

    -- Purpose
    purp_cd VARCHAR(4),

    -- Processing Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_gold_at TIMESTAMP,
    processing_error TEXT,
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pain008_raw_id ON silver.stg_iso20022_pain008(raw_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pain008_batch_id ON silver.stg_iso20022_pain008(_batch_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pain008_msg_id ON silver.stg_iso20022_pain008(grp_hdr_msg_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pain008_pmt_inf_id ON silver.stg_iso20022_pain008(pmt_inf_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_pain008_source ON silver.stg_iso20022_pain008(source_format);


-- =====================================================
-- STG_ISO20022_CAMT056 - Cancellation Request
-- Used by: camt.056, Cancellation requests for all payment systems
-- =====================================================
CREATE TABLE IF NOT EXISTS silver.stg_iso20022_camt056 (
    stg_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    raw_id VARCHAR(36) NOT NULL,
    source_format VARCHAR(20) NOT NULL,

    -- Assignment
    assgnmt_id VARCHAR(35),
    assgnmt_cre_dt_tm TIMESTAMP,
    assgnmt_assgne_agt_bic VARCHAR(11),
    assgnmt_assgnr_agt_bic VARCHAR(11),

    -- Case
    case_id VARCHAR(35),
    case_crtr_pty_nm VARCHAR(140),

    -- Underlying
    undrlyg_orgnl_grp_inf_orgnl_msg_id VARCHAR(35),
    undrlyg_orgnl_grp_inf_orgnl_msg_nm_id VARCHAR(35),
    undrlyg_orgnl_grp_inf_orgnl_cre_dt_tm TIMESTAMP,

    -- Transaction Information
    tx_inf_cxl_id VARCHAR(35),
    tx_inf_orgnl_instr_id VARCHAR(35),
    tx_inf_orgnl_end_to_end_id VARCHAR(35),
    tx_inf_orgnl_tx_id VARCHAR(35),
    tx_inf_orgnl_uetr VARCHAR(36),
    tx_inf_orgnl_clr_sys_ref VARCHAR(35),

    -- Cancellation Reason
    tx_inf_cxl_rsn_cd VARCHAR(4),
    tx_inf_cxl_rsn_prtry VARCHAR(35),
    tx_inf_cxl_rsn_addtl_inf TEXT,

    -- Original Transaction Reference
    orgnl_tx_ref_intr_bk_sttlm_amt DECIMAL(18,4),
    orgnl_tx_ref_intr_bk_sttlm_ccy VARCHAR(3),
    orgnl_tx_ref_intr_bk_sttlm_dt DATE,

    -- Debtor (Original)
    orgnl_tx_ref_dbtr_nm VARCHAR(140),
    orgnl_tx_ref_dbtr_acct_id_iban VARCHAR(34),
    orgnl_tx_ref_dbtr_agt_bic VARCHAR(11),

    -- Creditor (Original)
    orgnl_tx_ref_cdtr_nm VARCHAR(140),
    orgnl_tx_ref_cdtr_acct_id_iban VARCHAR(34),
    orgnl_tx_ref_cdtr_agt_bic VARCHAR(11),

    -- Processing Metadata
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_gold_at TIMESTAMP,
    processing_error TEXT,
    _batch_id VARCHAR(36),
    _processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stg_iso20022_camt056_raw_id ON silver.stg_iso20022_camt056(raw_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_camt056_batch_id ON silver.stg_iso20022_camt056(_batch_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_camt056_assgnmt_id ON silver.stg_iso20022_camt056(assgnmt_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_camt056_case_id ON silver.stg_iso20022_camt056(case_id);
CREATE INDEX IF NOT EXISTS idx_stg_iso20022_camt056_source ON silver.stg_iso20022_camt056(source_format);
