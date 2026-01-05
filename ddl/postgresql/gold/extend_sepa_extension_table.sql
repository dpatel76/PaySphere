-- GPS CDM - Extend SEPA Extension Table for 100% Silver-Gold Coverage
-- ====================================================================
-- This migration adds additional columns to cdm_payment_extension_sepa
-- to capture all SEPA-specific fields from Silver for complete coverage.

-- Extend cdm_payment_extension_sepa table with additional SEPA-specific columns
ALTER TABLE gold.cdm_payment_extension_sepa
    -- Initiating Party
    ADD COLUMN IF NOT EXISTS initiating_party_name VARCHAR(140),
    ADD COLUMN IF NOT EXISTS initg_pty_any_bic VARCHAR(11),
    ADD COLUMN IF NOT EXISTS initg_pty_othr_id VARCHAR(35),
    ADD COLUMN IF NOT EXISTS initg_pty_prvt_othr_id VARCHAR(35),
    ADD COLUMN IF NOT EXISTS initg_pty_address_line VARCHAR(140),
    ADD COLUMN IF NOT EXISTS initg_pty_building_number VARCHAR(16),
    ADD COLUMN IF NOT EXISTS initg_pty_country VARCHAR(2),
    ADD COLUMN IF NOT EXISTS initg_pty_post_code VARCHAR(16),
    ADD COLUMN IF NOT EXISTS initg_pty_street_name VARCHAR(70),
    ADD COLUMN IF NOT EXISTS initg_pty_town_name VARCHAR(35),
    -- Payment Information
    ADD COLUMN IF NOT EXISTS payment_information_id VARCHAR(35),
    ADD COLUMN IF NOT EXISTS payment_method VARCHAR(10),
    ADD COLUMN IF NOT EXISTS instruction_priority VARCHAR(10),
    ADD COLUMN IF NOT EXISTS local_instrument_code VARCHAR(35),
    ADD COLUMN IF NOT EXISTS service_level_code VARCHAR(35),
    ADD COLUMN IF NOT EXISTS category_purpose_code VARCHAR(35),
    ADD COLUMN IF NOT EXISTS requested_execution_date DATE,
    ADD COLUMN IF NOT EXISTS batch_booking BOOLEAN,
    ADD COLUMN IF NOT EXISTS pmt_inf_ctrl_sum DECIMAL(18,4),
    ADD COLUMN IF NOT EXISTS pmt_inf_nb_of_txs INTEGER,
    ADD COLUMN IF NOT EXISTS control_sum DECIMAL(18,4),
    ADD COLUMN IF NOT EXISTS debtor_id VARCHAR(35),
    -- Debtor Extended
    ADD COLUMN IF NOT EXISTS ultmt_dbtr_name VARCHAR(140),
    ADD COLUMN IF NOT EXISTS dbtr_bic_or_bei VARCHAR(35),
    ADD COLUMN IF NOT EXISTS dbtr_org_othr_id VARCHAR(35),
    ADD COLUMN IF NOT EXISTS dbtr_org_othr_schme_cd VARCHAR(35),
    ADD COLUMN IF NOT EXISTS dbtr_birth_date DATE,
    ADD COLUMN IF NOT EXISTS dbtr_city_of_birth VARCHAR(35),
    ADD COLUMN IF NOT EXISTS dbtr_ctry_of_birth VARCHAR(2),
    ADD COLUMN IF NOT EXISTS dbtr_prvt_othr_id VARCHAR(35),
    ADD COLUMN IF NOT EXISTS dbtr_address_line VARCHAR(140),
    ADD COLUMN IF NOT EXISTS dbtr_building_number VARCHAR(16),
    ADD COLUMN IF NOT EXISTS dbtr_country VARCHAR(2),
    ADD COLUMN IF NOT EXISTS dbtr_post_code VARCHAR(16),
    ADD COLUMN IF NOT EXISTS dbtr_street_name VARCHAR(70),
    ADD COLUMN IF NOT EXISTS dbtr_town_name VARCHAR(35),
    ADD COLUMN IF NOT EXISTS debtor_bic VARCHAR(11),
    -- Debtor Account Extended
    ADD COLUMN IF NOT EXISTS dbtr_acct_ccy VARCHAR(3),
    ADD COLUMN IF NOT EXISTS dbtr_acct_nm VARCHAR(140),
    ADD COLUMN IF NOT EXISTS dbtr_acct_type_cd VARCHAR(35),
    -- Debtor Agent Extended
    ADD COLUMN IF NOT EXISTS dbtr_agt_mmb_id VARCHAR(35),
    ADD COLUMN IF NOT EXISTS dbtr_agt_nm VARCHAR(140),
    ADD COLUMN IF NOT EXISTS dbtr_agt_othr_id VARCHAR(35),
    -- Transaction Level
    ADD COLUMN IF NOT EXISTS tx_chrg_br VARCHAR(4),
    ADD COLUMN IF NOT EXISTS tx_ctgy_purp_cd VARCHAR(35),
    ADD COLUMN IF NOT EXISTS tx_lcl_instrm_cd VARCHAR(35),
    ADD COLUMN IF NOT EXISTS tx_svc_lvl_cd VARCHAR(35),
    ADD COLUMN IF NOT EXISTS purpose_proprietary VARCHAR(35),
    ADD COLUMN IF NOT EXISTS eqvt_amt_value DECIMAL(18,4),
    ADD COLUMN IF NOT EXISTS eqvt_amt_ccy_of_trf VARCHAR(3),
    -- Creditor Extended
    ADD COLUMN IF NOT EXISTS ultmt_cdtr_name VARCHAR(140),
    ADD COLUMN IF NOT EXISTS cdtr_bic_or_bei VARCHAR(35),
    ADD COLUMN IF NOT EXISTS cdtr_org_othr_id VARCHAR(35),
    ADD COLUMN IF NOT EXISTS cdtr_org_othr_schme_cd VARCHAR(35),
    ADD COLUMN IF NOT EXISTS cdtr_birth_date DATE,
    ADD COLUMN IF NOT EXISTS cdtr_city_of_birth VARCHAR(35),
    ADD COLUMN IF NOT EXISTS cdtr_ctry_of_birth VARCHAR(2),
    ADD COLUMN IF NOT EXISTS cdtr_prvt_othr_id VARCHAR(35),
    ADD COLUMN IF NOT EXISTS cdtr_address_line VARCHAR(140),
    ADD COLUMN IF NOT EXISTS cdtr_building_number VARCHAR(16),
    ADD COLUMN IF NOT EXISTS cdtr_country VARCHAR(2),
    ADD COLUMN IF NOT EXISTS cdtr_post_code VARCHAR(16),
    ADD COLUMN IF NOT EXISTS cdtr_street_name VARCHAR(70),
    ADD COLUMN IF NOT EXISTS cdtr_town_name VARCHAR(35),
    ADD COLUMN IF NOT EXISTS creditor_bic VARCHAR(11),
    -- Creditor Account Extended
    ADD COLUMN IF NOT EXISTS cdtr_acct_ccy VARCHAR(3),
    ADD COLUMN IF NOT EXISTS cdtr_acct_nm VARCHAR(140),
    ADD COLUMN IF NOT EXISTS cdtr_acct_type_cd VARCHAR(35),
    -- Creditor Agent Extended
    ADD COLUMN IF NOT EXISTS cdtr_agt_mmb_id VARCHAR(35),
    ADD COLUMN IF NOT EXISTS cdtr_agt_nm VARCHAR(140),
    ADD COLUMN IF NOT EXISTS cdtr_agt_othr_id VARCHAR(35),
    ADD COLUMN IF NOT EXISTS cdtr_agt_ctry VARCHAR(2),
    -- Regulatory Reporting
    ADD COLUMN IF NOT EXISTS rgltry_rptg_cd VARCHAR(10),
    ADD COLUMN IF NOT EXISTS rgltry_rptg_inf TEXT,
    -- Creditor Reference
    ADD COLUMN IF NOT EXISTS cdtr_ref VARCHAR(35),
    ADD COLUMN IF NOT EXISTS cdtr_ref_tp_cd VARCHAR(35),
    ADD COLUMN IF NOT EXISTS cdtr_ref_tp_issr VARCHAR(35),
    -- Referred Document
    ADD COLUMN IF NOT EXISTS rfrd_doc_nb VARCHAR(35),
    ADD COLUMN IF NOT EXISTS rfrd_doc_rltd_dt DATE,
    ADD COLUMN IF NOT EXISTS rfrd_doc_tp_cd VARCHAR(35),
    -- Remittance Info
    ADD COLUMN IF NOT EXISTS rmt_inf_unstructured TEXT,
    -- Tax
    ADD COLUMN IF NOT EXISTS tax_ttl_tax_amt DECIMAL(18,4),
    ADD COLUMN IF NOT EXISTS tax_ttl_taxbl_base_amt DECIMAL(18,4),
    -- Exchange Rate
    ADD COLUMN IF NOT EXISTS exchange_rate_type VARCHAR(10),
    ADD COLUMN IF NOT EXISTS exchange_rate DECIMAL(18,10);

-- Add comments for documentation
COMMENT ON COLUMN gold.cdm_payment_extension_sepa.initiating_party_name IS 'Name of the party initiating the payment';
COMMENT ON COLUMN gold.cdm_payment_extension_sepa.payment_information_id IS 'Payment Information Block ID';
COMMENT ON COLUMN gold.cdm_payment_extension_sepa.ultmt_dbtr_name IS 'Ultimate Debtor Name';
COMMENT ON COLUMN gold.cdm_payment_extension_sepa.ultmt_cdtr_name IS 'Ultimate Creditor Name';
COMMENT ON COLUMN gold.cdm_payment_extension_sepa.rgltry_rptg_cd IS 'Regulatory Reporting Code';
COMMENT ON COLUMN gold.cdm_payment_extension_sepa.cdtr_ref IS 'Creditor Reference (Structured Remittance)';
