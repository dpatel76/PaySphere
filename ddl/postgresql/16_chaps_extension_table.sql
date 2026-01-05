-- GPS CDM - CHAPS Extension Table Schema
-- ==========================================
-- Defines the cdm_payment_extension_chaps table for UK CHAPS-specific payment attributes.
-- This table stores fields from the Silver stg_chaps table that don't fit in the normalized CDM tables.
--
-- Created: 2026-01-05
-- Coverage: 100% Silver->Gold mapping for CHAPS format

-- =====================================================
-- CHAPS Extension Table (UK RTGS)
-- =====================================================
CREATE TABLE IF NOT EXISTS gold.cdm_payment_extension_chaps (
    extension_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    instruction_id VARCHAR(36) REFERENCES gold.cdm_payment_instruction(instruction_id) ON DELETE CASCADE,

    -- Format identification
    format_id VARCHAR(10),
    message_type VARCHAR(35),
    raw_id VARCHAR(36),

    -- Settlement
    settlement_date DATE,
    settlement_method VARCHAR(10),
    value_date VARCHAR(20),
    uetr VARCHAR(36),

    -- Group header totals
    nb_of_txs INTEGER,
    ttl_intr_bk_sttlm_amt NUMERIC(18,4),
    ttl_intr_bk_sttlm_amt_ccy VARCHAR(3),

    -- Settlement info
    sttlm_inf_clr_sys VARCHAR(10),
    sttlm_acct VARCHAR(34),

    -- Instructing Agent
    instg_agt_bicfi VARCHAR(11),
    instg_agt_lei VARCHAR(20),
    instg_agt_clr_sys_mmb_id VARCHAR(20),

    -- Instructed Agent
    instd_agt_bicfi VARCHAR(11),
    instd_agt_lei VARCHAR(20),
    instd_agt_clr_sys_mmb_id VARCHAR(20),

    -- Payment type info
    instr_prty VARCHAR(10),
    svc_lvl_cd VARCHAR(10),
    svc_lvl_prtry VARCHAR(35),
    lcl_instrm_cd VARCHAR(10),
    lcl_instrm_prtry VARCHAR(35),
    ctgy_purp_cd VARCHAR(10),
    ctgy_purp_prtry VARCHAR(35),

    -- Transaction identification
    instruction_id_orig VARCHAR(35),
    tx_id VARCHAR(35),
    clr_sys_ref VARCHAR(50),

    -- Amounts
    instd_amt NUMERIC(18,4),
    instd_amt_ccy VARCHAR(3),
    xchg_rate NUMERIC(18,10),
    chrg_br VARCHAR(10),

    -- Purpose
    purp_cd VARCHAR(10),
    purp_prtry VARCHAR(35),

    -- Instructions
    instr_for_cdtr_agt TEXT,
    instr_for_nxt_agt TEXT,

    -- Structured remittance
    rmt_inf_strd_cdtr_ref_inf_tp VARCHAR(35),
    rmt_inf_strd_cdtr_ref_inf_ref VARCHAR(35),
    rmt_inf_strd_rfrd_doc_inf_tp VARCHAR(35),
    rmt_inf_strd_rfrd_doc_inf_nb VARCHAR(35),
    rmt_inf_strd_rfrd_doc_inf_rltd_dt DATE,
    rmt_inf_strd_rfrd_doc_inf_amt_due_pybl_amt NUMERIC(18,4),
    rmt_inf_strd_rfrd_doc_inf_amt_rmtd_amt NUMERIC(18,4),
    rmt_inf_strd_addtl_rmt_inf TEXT,

    -- Regulatory reporting
    rgltry_rptg_dbt_cdt_rptg_ind VARCHAR(10),
    rgltry_rptg_authrty_cd VARCHAR(10),
    rgltry_rptg_authrty_ctry VARCHAR(2),
    rgltry_rptg_dtls_cd VARCHAR(10),
    rgltry_rptg_dtls_inf TEXT,

    -- Tax
    tax_ttl_tax_amt NUMERIC(18,4),
    tax_dbtr_tax_id VARCHAR(35),
    tax_cdtr_tax_id VARCHAR(35),

    -- Intermediary agents
    intrmy_agt1_bicfi VARCHAR(11),
    intrmy_agt1_lei VARCHAR(20),
    intrmy_agt1_clr_sys_mmb_id VARCHAR(20),
    intrmy_agt1_acct VARCHAR(34),
    intrmy_agt2_bicfi VARCHAR(11),
    intrmy_agt2_lei VARCHAR(20),
    intrmy_agt3_bicfi VARCHAR(11),

    -- Debtor account details
    dbtr_acct_iban VARCHAR(34),
    dbtr_acct_tp VARCHAR(10),
    dbtr_acct_ccy VARCHAR(3),
    dbtr_acct_nm VARCHAR(140),
    dbtr_acct_othr_schme_nm_cd VARCHAR(35),

    -- Creditor account details
    cdtr_acct_iban VARCHAR(34),
    cdtr_acct_tp VARCHAR(10),
    cdtr_acct_ccy VARCHAR(3),
    cdtr_acct_nm VARCHAR(140),
    cdtr_acct_othr_schme_nm_cd VARCHAR(35),

    -- Debtor agent details
    dbtr_agt_nm VARCHAR(140),
    dbtr_agt_pstl_adr_ctry VARCHAR(2),
    dbtr_agt_clr_sys_id_cd VARCHAR(10),

    -- Creditor agent details
    cdtr_agt_nm VARCHAR(140),
    cdtr_agt_pstl_adr_ctry VARCHAR(2),
    cdtr_agt_clr_sys_id_cd VARCHAR(10),

    -- Debtor party extended details
    dbtr_adr_line_3 VARCHAR(140),
    dbtr_ctct_nm VARCHAR(140),
    dbtr_ctry_of_birth VARCHAR(2),
    dbtr_bic VARCHAR(11),

    -- Creditor party extended details
    cdtr_adr_line_3 VARCHAR(140),
    cdtr_ctct_nm VARCHAR(140),
    cdtr_ctry_of_birth VARCHAR(2),
    cdtr_bic VARCHAR(11),

    -- Processing
    processing_status VARCHAR(20),

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_chaps_instruction UNIQUE (instruction_id)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_chaps_ext_uetr ON gold.cdm_payment_extension_chaps(uetr) WHERE uetr IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_chaps_ext_sttlm_date ON gold.cdm_payment_extension_chaps(settlement_date);
CREATE INDEX IF NOT EXISTS idx_chaps_ext_clr_sys_ref ON gold.cdm_payment_extension_chaps(clr_sys_ref) WHERE clr_sys_ref IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_chaps_ext_processing_status ON gold.cdm_payment_extension_chaps(processing_status);

COMMENT ON TABLE gold.cdm_payment_extension_chaps IS 'UK CHAPS-specific payment attributes for RTGS payments';

-- =====================================================
-- Migration: Add any columns that may be missing
-- =====================================================
ALTER TABLE gold.cdm_payment_extension_chaps
    ADD COLUMN IF NOT EXISTS dbtr_acct_iban VARCHAR(34),
    ADD COLUMN IF NOT EXISTS dbtr_acct_tp VARCHAR(10),
    ADD COLUMN IF NOT EXISTS dbtr_acct_ccy VARCHAR(3),
    ADD COLUMN IF NOT EXISTS cdtr_acct_iban VARCHAR(34),
    ADD COLUMN IF NOT EXISTS cdtr_acct_tp VARCHAR(10),
    ADD COLUMN IF NOT EXISTS cdtr_acct_ccy VARCHAR(3),
    ADD COLUMN IF NOT EXISTS dbtr_agt_nm VARCHAR(140),
    ADD COLUMN IF NOT EXISTS dbtr_agt_pstl_adr_ctry VARCHAR(2),
    ADD COLUMN IF NOT EXISTS cdtr_agt_nm VARCHAR(140),
    ADD COLUMN IF NOT EXISTS cdtr_agt_pstl_adr_ctry VARCHAR(2),
    ADD COLUMN IF NOT EXISTS processing_status VARCHAR(20),
    ADD COLUMN IF NOT EXISTS dbtr_adr_line_3 VARCHAR(140),
    ADD COLUMN IF NOT EXISTS cdtr_adr_line_3 VARCHAR(140),
    ADD COLUMN IF NOT EXISTS dbtr_ctct_nm VARCHAR(140),
    ADD COLUMN IF NOT EXISTS cdtr_ctct_nm VARCHAR(140),
    ADD COLUMN IF NOT EXISTS dbtr_ctry_of_birth VARCHAR(2),
    ADD COLUMN IF NOT EXISTS cdtr_ctry_of_birth VARCHAR(2),
    ADD COLUMN IF NOT EXISTS dbtr_bic VARCHAR(11),
    ADD COLUMN IF NOT EXISTS cdtr_bic VARCHAR(11),
    ADD COLUMN IF NOT EXISTS dbtr_acct_nm VARCHAR(140),
    ADD COLUMN IF NOT EXISTS cdtr_acct_nm VARCHAR(140),
    ADD COLUMN IF NOT EXISTS dbtr_acct_othr_schme_nm_cd VARCHAR(35),
    ADD COLUMN IF NOT EXISTS cdtr_acct_othr_schme_nm_cd VARCHAR(35),
    ADD COLUMN IF NOT EXISTS dbtr_agt_clr_sys_id_cd VARCHAR(10),
    ADD COLUMN IF NOT EXISTS cdtr_agt_clr_sys_id_cd VARCHAR(10);
