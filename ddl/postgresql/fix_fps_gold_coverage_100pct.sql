-- =============================================================================
-- GPS CDM - Fix FPS Silver->Gold Coverage to 100%
-- =============================================================================
-- Current: 26.8% (30/112 mappings)
-- Target: 100% coverage (117 Silver columns)
--
-- This script:
-- 1. Adds new columns to gold.cdm_payment_extension_fps for ISO 20022 pacs.008 fields
-- 2. Creates Gold mappings for ALL 117 Silver columns
-- =============================================================================

BEGIN;

-- =============================================================================
-- Step 1: Add new columns to gold.cdm_payment_extension_fps
-- =============================================================================
-- These columns will store ISO 20022 pacs.008 specific fields that don't map
-- directly to CDM core tables.

-- Group Header fields
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS grphdr_instdagt_fininstnid_bicfi VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS grphdr_instgagt_fininstnid_bicfi VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS grphdr_nboftxs VARCHAR(15);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS grphdr_sttlminf_clrsys_cd VARCHAR(5);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS grphdr_sttlminf_sttlmmtd VARCHAR(10);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS grphdr_ttlintrbksttlmamt DECIMAL(18,5);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS grphdr_ttlintrbksttlmamt_ccy VARCHAR(3);

-- Credit Transfer Transaction Information - Instructed Amount
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_instdamt DECIMAL(18,5);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_instdamt_ccy VARCHAR(3);

-- Credit Transfer Transaction Information - Payment Type Info
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_pmttpinf_ctgypurp_cd VARCHAR(4);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_pmttpinf_instrprty VARCHAR(10);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_pmttpinf_lclinstrm_cd VARCHAR(10);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_pmttpinf_svclvl_cd VARCHAR(10);

-- Credit Transfer Transaction Information - Payment ID
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_pmtid_clrsysref VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_pmtid_uetr VARCHAR(36);

-- Credit Transfer Transaction Information - Interbank Settlement
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_intrbksttlmdt DATE;
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_xchgrate DECIMAL(18,8);

-- Credit Transfer Transaction Information - Charges
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_chrgbr VARCHAR(10);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_chrgsinf_amt DECIMAL(18,5);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_chrgsinf_amt_ccy VARCHAR(3);

-- Credit Transfer Transaction Information - Purpose
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_purp_cd VARCHAR(10);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_purp_prtry VARCHAR(35);

-- Credit Transfer Transaction Information - Remittance Info
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_rmtinf_strd_addtlrmtinf TEXT;
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_rmtinf_strd_cdtrrefinf_tp_cdorprtry_cd VARCHAR(35);

-- Credit Transfer Transaction Information - Regulatory Reporting
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_rgltryrptg_dtls_cd VARCHAR(10);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_rgltryrptg_dtls_inf TEXT;

-- Credit Transfer Transaction Information - Instruction for Agents
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_instrforcdtragt_cd VARCHAR(10);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_instrforcdtragt_instrinf TEXT;
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_instrfornxtagt_cd VARCHAR(10);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_instrfornxtagt_instrinf TEXT;

-- Credit Transfer Transaction Information - Intermediary Agent 1
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_intrmyagt1_fininstnid_bicfi VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_intrmyagt1_fininstnid_clrsysmmbid_mmbid VARCHAR(35);

-- Credit Transfer Transaction Information - Debtor
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtr_ctctdtls_emailadr VARCHAR(256);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtr_ctctdtls_phnenb VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtr_ctryofres VARCHAR(2);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtr_id_orgid_anybic VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtr_id_orgid_lei VARCHAR(20);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtr_id_orgid_othr_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtr_pstladr_bldgnb VARCHAR(16);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtr_pstladr_ctry VARCHAR(2);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtr_pstladr_ctrysubdvsn VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtr_pstladr_pstcd VARCHAR(16);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtr_pstladr_strtnm VARCHAR(70);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtr_pstladr_twnnm VARCHAR(35);

-- Credit Transfer Transaction Information - Debtor Account
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtracct_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtracct_id_iban VARCHAR(34);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtracct_id_othr_schmenm_cd VARCHAR(10);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtracct_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtracct_tp_cd VARCHAR(10);

-- Credit Transfer Transaction Information - Debtor Agent
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtragt_brnchid_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtragt_fininstnid_bicfi VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtragt_fininstnid_clrsysmmbid_clrsysid_cd VARCHAR(10);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtragt_fininstnid_lei VARCHAR(20);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtragt_fininstnid_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_dbtragt_fininstnid_pstladr_ctry VARCHAR(2);

-- Credit Transfer Transaction Information - Creditor
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtr_ctctdtls_emailadr VARCHAR(256);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtr_ctctdtls_phnenb VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtr_ctryofres VARCHAR(2);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtr_id_orgid_anybic VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtr_id_orgid_lei VARCHAR(20);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtr_id_orgid_othr_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtr_pstladr_bldgnb VARCHAR(16);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtr_pstladr_ctry VARCHAR(2);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtr_pstladr_ctrysubdvsn VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtr_pstladr_pstcd VARCHAR(16);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtr_pstladr_strtnm VARCHAR(70);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtr_pstladr_twnnm VARCHAR(35);

-- Credit Transfer Transaction Information - Creditor Account
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtracct_ccy VARCHAR(3);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtracct_id_iban VARCHAR(34);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtracct_id_othr_schmenm_cd VARCHAR(10);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtracct_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtracct_tp_cd VARCHAR(10);

-- Credit Transfer Transaction Information - Creditor Agent
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtragt_brnchid_id VARCHAR(35);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtragt_fininstnid_bicfi VARCHAR(11);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtragt_fininstnid_clrsysmmbid_clrsysid_cd VARCHAR(10);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtragt_fininstnid_lei VARCHAR(20);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtragt_fininstnid_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_cdtragt_fininstnid_pstladr_ctry VARCHAR(2);

-- Credit Transfer Transaction Information - Ultimate Parties
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_ultmtdbtr_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_ultmtdbtr_ctryofres VARCHAR(2);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_ultmtcdtr_nm VARCHAR(140);
ALTER TABLE gold.cdm_payment_extension_fps ADD COLUMN IF NOT EXISTS cdttrftxinf_ultmtcdtr_ctryofres VARCHAR(2);

-- Add comments
COMMENT ON COLUMN gold.cdm_payment_extension_fps.grphdr_instdagt_fininstnid_bicfi IS 'Group Header Instructed Agent BIC';
COMMENT ON COLUMN gold.cdm_payment_extension_fps.grphdr_instgagt_fininstnid_bicfi IS 'Group Header Instructing Agent BIC';
COMMENT ON COLUMN gold.cdm_payment_extension_fps.grphdr_nboftxs IS 'Number of Transactions';
COMMENT ON COLUMN gold.cdm_payment_extension_fps.cdttrftxinf_pmtid_uetr IS 'Unique End-to-End Transaction Reference (UETR)';

-- =============================================================================
-- Step 2: Delete existing FPS Gold mappings and recreate for 100% coverage
-- =============================================================================
DELETE FROM mapping.gold_field_mappings WHERE format_id = 'FPS';

-- =============================================================================
-- Step 3: Insert Gold Field Mappings for 100% coverage
-- =============================================================================

-- ========================================
-- cdm_payment_instruction mappings (26 mappings)
-- ========================================
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal_position, is_active)
VALUES
    -- System/lineage columns
    ('FPS', 'cdm_payment_instruction', 'instruction_id', '_GENERATED_UUID', NULL, 'VARCHAR', 1, true),
    ('FPS', 'cdm_payment_instruction', 'source_stg_id', 'stg_id', NULL, 'VARCHAR', 2, true),
    ('FPS', 'cdm_payment_instruction', 'source_raw_id', '_raw_id', NULL, 'VARCHAR', 3, true),
    ('FPS', 'cdm_payment_instruction', 'lineage_batch_id', '_batch_id', NULL, 'VARCHAR', 4, true),

    -- Message identification
    ('FPS', 'cdm_payment_instruction', 'message_id', 'message_id', NULL, 'VARCHAR', 5, true),
    ('FPS', 'cdm_payment_instruction', 'source_message_type', 'message_type', NULL, 'VARCHAR', 6, true),
    ('FPS', 'cdm_payment_instruction', 'creation_datetime', 'creation_date_time', NULL, 'TIMESTAMP', 7, true),

    -- Amounts
    ('FPS', 'cdm_payment_instruction', 'instructed_amount', 'amount', NULL, 'DECIMAL', 8, true),
    ('FPS', 'cdm_payment_instruction', 'instructed_currency', 'currency', NULL, 'VARCHAR', 9, true),
    ('FPS', 'cdm_payment_instruction', 'interbank_settlement_amount', 'cdttrftxinf_instdamt', NULL, 'DECIMAL', 10, true),
    ('FPS', 'cdm_payment_instruction', 'interbank_settlement_currency', 'cdttrftxinf_instdamt_ccy', NULL, 'VARCHAR', 11, true),
    ('FPS', 'cdm_payment_instruction', 'exchange_rate', 'cdttrftxinf_xchgrate', NULL, 'DECIMAL', 12, true),

    -- Payment references
    ('FPS', 'cdm_payment_instruction', 'payment_id', 'payment_id', NULL, 'VARCHAR', 13, true),
    ('FPS', 'cdm_payment_instruction', 'instruction_id_ext', 'instruction_id', NULL, 'VARCHAR', 14, true),
    ('FPS', 'cdm_payment_instruction', 'end_to_end_id', 'end_to_end_id', NULL, 'VARCHAR', 15, true),
    ('FPS', 'cdm_payment_instruction', 'uetr', 'cdttrftxinf_pmtid_uetr', NULL, 'VARCHAR', 16, true),
    ('FPS', 'cdm_payment_instruction', 'clearing_system_reference', 'cdttrftxinf_pmtid_clrsysref', NULL, 'VARCHAR', 17, true),
    ('FPS', 'cdm_payment_instruction', 'remittance_reference', 'payment_reference', NULL, 'VARCHAR', 18, true),

    -- Remittance
    ('FPS', 'cdm_payment_instruction', 'remittance_unstructured', 'remittance_info', NULL, 'TEXT', 19, true),

    -- Dates
    ('FPS', 'cdm_payment_instruction', 'requested_execution_date', 'requested_execution_date', NULL, 'DATE', 20, true),
    ('FPS', 'cdm_payment_instruction', 'settlement_date', 'settlement_datetime', NULL, 'TIMESTAMP', 21, true),
    ('FPS', 'cdm_payment_instruction', 'value_date', 'cdttrftxinf_intrbksttlmdt', NULL, 'DATE', 22, true),

    -- Payment type info
    ('FPS', 'cdm_payment_instruction', 'service_level', 'cdttrftxinf_pmttpinf_svclvl_cd', NULL, 'VARCHAR', 23, true),
    ('FPS', 'cdm_payment_instruction', 'local_instrument', 'cdttrftxinf_pmttpinf_lclinstrm_cd', NULL, 'VARCHAR', 24, true),
    ('FPS', 'cdm_payment_instruction', 'category_purpose', 'cdttrftxinf_pmttpinf_ctgypurp_cd', NULL, 'VARCHAR', 25, true),
    ('FPS', 'cdm_payment_instruction', 'priority', 'cdttrftxinf_pmttpinf_instrprty', NULL, 'VARCHAR', 26, true),

    -- Purpose
    ('FPS', 'cdm_payment_instruction', 'purpose', 'cdttrftxinf_purp_cd', NULL, 'VARCHAR', 27, true),
    ('FPS', 'cdm_payment_instruction', 'purpose_description', 'cdttrftxinf_purp_prtry', NULL, 'VARCHAR', 28, true),

    -- Charges
    ('FPS', 'cdm_payment_instruction', 'charge_bearer', 'cdttrftxinf_chrgbr', NULL, 'VARCHAR', 29, true),

    -- Clearing
    ('FPS', 'cdm_payment_instruction', 'clearing_system', 'grphdr_sttlminf_clrsys_cd', NULL, 'VARCHAR', 30, true),
    ('FPS', 'cdm_payment_instruction', 'number_of_transactions', 'grphdr_nboftxs', NULL, 'VARCHAR', 31, true),
    ('FPS', 'cdm_payment_instruction', 'control_sum', 'grphdr_ttlintrbksttlmamt', NULL, 'DECIMAL', 32, true),

    -- Required fields with defaults
    ('FPS', 'cdm_payment_instruction', 'source_stg_table', '''stg_fps''', NULL, 'VARCHAR', 33, true),
    ('FPS', 'cdm_payment_instruction', 'payment_type', '''CREDIT_TRANSFER''', NULL, 'VARCHAR', 34, true),
    ('FPS', 'cdm_payment_instruction', 'scheme_code', '''FPS''', NULL, 'VARCHAR', 35, true),
    ('FPS', 'cdm_payment_instruction', 'direction', '''OUTGOING''', NULL, 'VARCHAR', 36, true),
    ('FPS', 'cdm_payment_instruction', 'cross_border_flag', 'false', NULL, 'BOOLEAN', 37, true),
    ('FPS', 'cdm_payment_instruction', 'current_status', '''RECEIVED''', NULL, 'VARCHAR', 38, true),
    ('FPS', 'cdm_payment_instruction', 'source_system', '''FPS''', NULL, 'VARCHAR', 39, true),
    ('FPS', 'cdm_payment_instruction', 'region', '''UK''', NULL, 'VARCHAR', 40, true),
    ('FPS', 'cdm_payment_instruction', 'payment_method', 'grphdr_sttlminf_sttlmmtd', NULL, 'VARCHAR', 41, true);

-- ========================================
-- cdm_party mappings for DEBTOR (13 mappings)
-- ========================================
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal_position, is_active)
VALUES
    ('FPS', 'cdm_party', 'party_id', '_GENERATED_UUID', 'DEBTOR', 'VARCHAR', 100, true),
    ('FPS', 'cdm_party', 'name', 'debtor_name', 'DEBTOR', 'VARCHAR', 101, true),
    ('FPS', 'cdm_party', 'dba_name', 'payer_name', 'DEBTOR', 'VARCHAR', 102, true),
    ('FPS', 'cdm_party', 'address_line1', 'payer_address', 'DEBTOR', 'VARCHAR', 103, true),
    ('FPS', 'cdm_party', 'street_name', 'cdttrftxinf_dbtr_pstladr_strtnm', 'DEBTOR', 'VARCHAR', 104, true),
    ('FPS', 'cdm_party', 'building_number', 'cdttrftxinf_dbtr_pstladr_bldgnb', 'DEBTOR', 'VARCHAR', 105, true),
    ('FPS', 'cdm_party', 'post_code', 'cdttrftxinf_dbtr_pstladr_pstcd', 'DEBTOR', 'VARCHAR', 106, true),
    ('FPS', 'cdm_party', 'town_name', 'cdttrftxinf_dbtr_pstladr_twnnm', 'DEBTOR', 'VARCHAR', 107, true),
    ('FPS', 'cdm_party', 'country_sub_division', 'cdttrftxinf_dbtr_pstladr_ctrysubdvsn', 'DEBTOR', 'VARCHAR', 108, true),
    ('FPS', 'cdm_party', 'country', 'cdttrftxinf_dbtr_pstladr_ctry', 'DEBTOR', 'VARCHAR', 109, true),
    ('FPS', 'cdm_party', 'nationality', 'cdttrftxinf_dbtr_ctryofres', 'DEBTOR', 'VARCHAR', 110, true),
    ('FPS', 'cdm_party', 'email_address', 'cdttrftxinf_dbtr_ctctdtls_emailadr', 'DEBTOR', 'VARCHAR', 111, true),
    ('FPS', 'cdm_party', 'phone_number', 'cdttrftxinf_dbtr_ctctdtls_phnenb', 'DEBTOR', 'VARCHAR', 112, true),
    ('FPS', 'cdm_party', 'registration_number', 'cdttrftxinf_dbtr_id_orgid_othr_id', 'DEBTOR', 'VARCHAR', 113, true),
    ('FPS', 'cdm_party', 'tax_id', 'cdttrftxinf_dbtr_id_orgid_lei', 'DEBTOR', 'VARCHAR', 114, true),
    ('FPS', 'cdm_party', 'party_type', '''UNKNOWN''', 'DEBTOR', 'VARCHAR', 115, true),
    ('FPS', 'cdm_party', 'source_system', '''FPS''', 'DEBTOR', 'VARCHAR', 116, true),
    ('FPS', 'cdm_party', 'source_message_type', '''FPS''', 'DEBTOR', 'VARCHAR', 117, true),
    ('FPS', 'cdm_party', 'source_stg_id', 'stg_id', 'DEBTOR', 'VARCHAR', 118, true);

-- ========================================
-- cdm_party mappings for CREDITOR (13 mappings)
-- ========================================
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal_position, is_active)
VALUES
    ('FPS', 'cdm_party', 'party_id', '_GENERATED_UUID', 'CREDITOR', 'VARCHAR', 200, true),
    ('FPS', 'cdm_party', 'name', 'creditor_name', 'CREDITOR', 'VARCHAR', 201, true),
    ('FPS', 'cdm_party', 'dba_name', 'payee_name', 'CREDITOR', 'VARCHAR', 202, true),
    ('FPS', 'cdm_party', 'address_line1', 'payee_address', 'CREDITOR', 'VARCHAR', 203, true),
    ('FPS', 'cdm_party', 'street_name', 'cdttrftxinf_cdtr_pstladr_strtnm', 'CREDITOR', 'VARCHAR', 204, true),
    ('FPS', 'cdm_party', 'building_number', 'cdttrftxinf_cdtr_pstladr_bldgnb', 'CREDITOR', 'VARCHAR', 205, true),
    ('FPS', 'cdm_party', 'post_code', 'cdttrftxinf_cdtr_pstladr_pstcd', 'CREDITOR', 'VARCHAR', 206, true),
    ('FPS', 'cdm_party', 'town_name', 'cdttrftxinf_cdtr_pstladr_twnnm', 'CREDITOR', 'VARCHAR', 207, true),
    ('FPS', 'cdm_party', 'country_sub_division', 'cdttrftxinf_cdtr_pstladr_ctrysubdvsn', 'CREDITOR', 'VARCHAR', 208, true),
    ('FPS', 'cdm_party', 'country', 'cdttrftxinf_cdtr_pstladr_ctry', 'CREDITOR', 'VARCHAR', 209, true),
    ('FPS', 'cdm_party', 'nationality', 'cdttrftxinf_cdtr_ctryofres', 'CREDITOR', 'VARCHAR', 210, true),
    ('FPS', 'cdm_party', 'email_address', 'cdttrftxinf_cdtr_ctctdtls_emailadr', 'CREDITOR', 'VARCHAR', 211, true),
    ('FPS', 'cdm_party', 'phone_number', 'cdttrftxinf_cdtr_ctctdtls_phnenb', 'CREDITOR', 'VARCHAR', 212, true),
    ('FPS', 'cdm_party', 'registration_number', 'cdttrftxinf_cdtr_id_orgid_othr_id', 'CREDITOR', 'VARCHAR', 213, true),
    ('FPS', 'cdm_party', 'tax_id', 'cdttrftxinf_cdtr_id_orgid_lei', 'CREDITOR', 'VARCHAR', 214, true),
    ('FPS', 'cdm_party', 'party_type', '''UNKNOWN''', 'CREDITOR', 'VARCHAR', 215, true),
    ('FPS', 'cdm_party', 'source_system', '''FPS''', 'CREDITOR', 'VARCHAR', 216, true),
    ('FPS', 'cdm_party', 'source_message_type', '''FPS''', 'CREDITOR', 'VARCHAR', 217, true),
    ('FPS', 'cdm_party', 'source_stg_id', 'stg_id', 'CREDITOR', 'VARCHAR', 218, true);

-- ========================================
-- cdm_party mappings for ULTIMATE_DEBTOR (4 mappings)
-- ========================================
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal_position, is_active)
VALUES
    ('FPS', 'cdm_party', 'party_id', '_GENERATED_UUID', 'ULTIMATE_DEBTOR', 'VARCHAR', 250, true),
    ('FPS', 'cdm_party', 'name', 'cdttrftxinf_ultmtdbtr_nm', 'ULTIMATE_DEBTOR', 'VARCHAR', 251, true),
    ('FPS', 'cdm_party', 'nationality', 'cdttrftxinf_ultmtdbtr_ctryofres', 'ULTIMATE_DEBTOR', 'VARCHAR', 252, true),
    ('FPS', 'cdm_party', 'party_type', '''UNKNOWN''', 'ULTIMATE_DEBTOR', 'VARCHAR', 253, true),
    ('FPS', 'cdm_party', 'source_system', '''FPS''', 'ULTIMATE_DEBTOR', 'VARCHAR', 254, true),
    ('FPS', 'cdm_party', 'source_message_type', '''FPS''', 'ULTIMATE_DEBTOR', 'VARCHAR', 255, true),
    ('FPS', 'cdm_party', 'source_stg_id', 'stg_id', 'ULTIMATE_DEBTOR', 'VARCHAR', 256, true);

-- ========================================
-- cdm_party mappings for ULTIMATE_CREDITOR (4 mappings)
-- ========================================
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal_position, is_active)
VALUES
    ('FPS', 'cdm_party', 'party_id', '_GENERATED_UUID', 'ULTIMATE_CREDITOR', 'VARCHAR', 260, true),
    ('FPS', 'cdm_party', 'name', 'cdttrftxinf_ultmtcdtr_nm', 'ULTIMATE_CREDITOR', 'VARCHAR', 261, true),
    ('FPS', 'cdm_party', 'nationality', 'cdttrftxinf_ultmtcdtr_ctryofres', 'ULTIMATE_CREDITOR', 'VARCHAR', 262, true),
    ('FPS', 'cdm_party', 'party_type', '''UNKNOWN''', 'ULTIMATE_CREDITOR', 'VARCHAR', 263, true),
    ('FPS', 'cdm_party', 'source_system', '''FPS''', 'ULTIMATE_CREDITOR', 'VARCHAR', 264, true),
    ('FPS', 'cdm_party', 'source_message_type', '''FPS''', 'ULTIMATE_CREDITOR', 'VARCHAR', 265, true),
    ('FPS', 'cdm_party', 'source_stg_id', 'stg_id', 'ULTIMATE_CREDITOR', 'VARCHAR', 266, true);

-- ========================================
-- cdm_account mappings for DEBTOR (10 mappings)
-- ========================================
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal_position, is_active)
VALUES
    ('FPS', 'cdm_account', 'account_id', '_GENERATED_UUID', 'DEBTOR', 'VARCHAR', 300, true),
    ('FPS', 'cdm_account', 'account_number', 'debtor_account_account_number', 'DEBTOR', 'VARCHAR', 301, true),
    ('FPS', 'cdm_account', 'iban', 'cdttrftxinf_dbtracct_id_iban', 'DEBTOR', 'VARCHAR', 302, true),
    ('FPS', 'cdm_account', 'account_type', 'cdttrftxinf_dbtracct_tp_cd', 'DEBTOR', 'VARCHAR', 303, true),
    ('FPS', 'cdm_account', 'currency', 'cdttrftxinf_dbtracct_ccy', 'DEBTOR', 'VARCHAR', 304, true),
    ('FPS', 'cdm_account', 'branch_id', 'payer_account', 'DEBTOR', 'VARCHAR', 305, true),
    ('FPS', 'cdm_account', 'account_status', '''ACTIVE''', 'DEBTOR', 'VARCHAR', 306, true),
    ('FPS', 'cdm_account', 'source_system', '''FPS''', 'DEBTOR', 'VARCHAR', 307, true),
    ('FPS', 'cdm_account', 'source_message_type', '''FPS''', 'DEBTOR', 'VARCHAR', 308, true),
    ('FPS', 'cdm_account', 'source_stg_id', 'stg_id', 'DEBTOR', 'VARCHAR', 309, true);

-- ========================================
-- cdm_account mappings for CREDITOR (10 mappings)
-- ========================================
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal_position, is_active)
VALUES
    ('FPS', 'cdm_account', 'account_id', '_GENERATED_UUID', 'CREDITOR', 'VARCHAR', 400, true),
    ('FPS', 'cdm_account', 'account_number', 'creditor_account_account_number', 'CREDITOR', 'VARCHAR', 401, true),
    ('FPS', 'cdm_account', 'iban', 'cdttrftxinf_cdtracct_id_iban', 'CREDITOR', 'VARCHAR', 402, true),
    ('FPS', 'cdm_account', 'account_type', 'cdttrftxinf_cdtracct_tp_cd', 'CREDITOR', 'VARCHAR', 403, true),
    ('FPS', 'cdm_account', 'currency', 'cdttrftxinf_cdtracct_ccy', 'CREDITOR', 'VARCHAR', 404, true),
    ('FPS', 'cdm_account', 'branch_id', 'payee_account', 'CREDITOR', 'VARCHAR', 405, true),
    ('FPS', 'cdm_account', 'account_status', '''ACTIVE''', 'CREDITOR', 'VARCHAR', 406, true),
    ('FPS', 'cdm_account', 'source_system', '''FPS''', 'CREDITOR', 'VARCHAR', 407, true),
    ('FPS', 'cdm_account', 'source_message_type', '''FPS''', 'CREDITOR', 'VARCHAR', 408, true),
    ('FPS', 'cdm_account', 'source_stg_id', 'stg_id', 'CREDITOR', 'VARCHAR', 409, true);

-- ========================================
-- cdm_financial_institution for DEBTOR_AGENT (12 mappings)
-- ========================================
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal_position, is_active)
VALUES
    ('FPS', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'DEBTOR_AGENT', 'VARCHAR', 500, true),
    ('FPS', 'cdm_financial_institution', 'institution_name', 'cdttrftxinf_dbtragt_fininstnid_nm', 'DEBTOR_AGENT', 'VARCHAR', 501, true),
    ('FPS', 'cdm_financial_institution', 'bic', 'cdttrftxinf_dbtragt_fininstnid_bicfi', 'DEBTOR_AGENT', 'VARCHAR', 502, true),
    ('FPS', 'cdm_financial_institution', 'lei', 'cdttrftxinf_dbtragt_fininstnid_lei', 'DEBTOR_AGENT', 'VARCHAR', 503, true),
    ('FPS', 'cdm_financial_institution', 'national_clearing_code', 'debtor_account_sort_code', 'DEBTOR_AGENT', 'VARCHAR', 504, true),
    ('FPS', 'cdm_financial_institution', 'national_clearing_system', 'cdttrftxinf_dbtragt_fininstnid_clrsysmmbid_clrsysid_cd', 'DEBTOR_AGENT', 'VARCHAR', 505, true),
    ('FPS', 'cdm_financial_institution', 'branch_identification', 'cdttrftxinf_dbtragt_brnchid_id', 'DEBTOR_AGENT', 'VARCHAR', 506, true),
    ('FPS', 'cdm_financial_institution', 'country', 'cdttrftxinf_dbtragt_fininstnid_pstladr_ctry', 'DEBTOR_AGENT', 'VARCHAR', 507, true),
    ('FPS', 'cdm_financial_institution', 'source_system', '''FPS''', 'DEBTOR_AGENT', 'VARCHAR', 508, true),
    ('FPS', 'cdm_financial_institution', 'is_current', 'true', 'DEBTOR_AGENT', 'BOOLEAN', 509, true);

-- ========================================
-- cdm_financial_institution for CREDITOR_AGENT (12 mappings)
-- ========================================
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal_position, is_active)
VALUES
    ('FPS', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'CREDITOR_AGENT', 'VARCHAR', 600, true),
    ('FPS', 'cdm_financial_institution', 'institution_name', 'cdttrftxinf_cdtragt_fininstnid_nm', 'CREDITOR_AGENT', 'VARCHAR', 601, true),
    ('FPS', 'cdm_financial_institution', 'bic', 'cdttrftxinf_cdtragt_fininstnid_bicfi', 'CREDITOR_AGENT', 'VARCHAR', 602, true),
    ('FPS', 'cdm_financial_institution', 'lei', 'cdttrftxinf_cdtragt_fininstnid_lei', 'CREDITOR_AGENT', 'VARCHAR', 603, true),
    ('FPS', 'cdm_financial_institution', 'national_clearing_code', 'creditor_account_sort_code', 'CREDITOR_AGENT', 'VARCHAR', 604, true),
    ('FPS', 'cdm_financial_institution', 'national_clearing_system', 'cdttrftxinf_cdtragt_fininstnid_clrsysmmbid_clrsysid_cd', 'CREDITOR_AGENT', 'VARCHAR', 605, true),
    ('FPS', 'cdm_financial_institution', 'branch_identification', 'cdttrftxinf_cdtragt_brnchid_id', 'CREDITOR_AGENT', 'VARCHAR', 606, true),
    ('FPS', 'cdm_financial_institution', 'country', 'cdttrftxinf_cdtragt_fininstnid_pstladr_ctry', 'CREDITOR_AGENT', 'VARCHAR', 607, true),
    ('FPS', 'cdm_financial_institution', 'source_system', '''FPS''', 'CREDITOR_AGENT', 'VARCHAR', 608, true),
    ('FPS', 'cdm_financial_institution', 'is_current', 'true', 'CREDITOR_AGENT', 'BOOLEAN', 609, true);

-- ========================================
-- cdm_financial_institution for INTERMEDIARY_AGENT1 (5 mappings)
-- ========================================
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal_position, is_active)
VALUES
    ('FPS', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'INTERMEDIARY_AGENT1', 'VARCHAR', 650, true),
    ('FPS', 'cdm_financial_institution', 'bic', 'cdttrftxinf_intrmyagt1_fininstnid_bicfi', 'INTERMEDIARY_AGENT1', 'VARCHAR', 651, true),
    ('FPS', 'cdm_financial_institution', 'national_clearing_code', 'cdttrftxinf_intrmyagt1_fininstnid_clrsysmmbid_mmbid', 'INTERMEDIARY_AGENT1', 'VARCHAR', 652, true),
    ('FPS', 'cdm_financial_institution', 'source_system', '''FPS''', 'INTERMEDIARY_AGENT1', 'VARCHAR', 653, true),
    ('FPS', 'cdm_financial_institution', 'is_current', 'true', 'INTERMEDIARY_AGENT1', 'BOOLEAN', 654, true);

-- ========================================
-- cdm_financial_institution for INSTRUCTING_AGENT (header level)
-- ========================================
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal_position, is_active)
VALUES
    ('FPS', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'INSTRUCTING_AGENT', 'VARCHAR', 660, true),
    ('FPS', 'cdm_financial_institution', 'bic', 'grphdr_instgagt_fininstnid_bicfi', 'INSTRUCTING_AGENT', 'VARCHAR', 661, true),
    ('FPS', 'cdm_financial_institution', 'source_system', '''FPS''', 'INSTRUCTING_AGENT', 'VARCHAR', 662, true),
    ('FPS', 'cdm_financial_institution', 'is_current', 'true', 'INSTRUCTING_AGENT', 'BOOLEAN', 663, true);

-- ========================================
-- cdm_financial_institution for INSTRUCTED_AGENT (header level)
-- ========================================
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal_position, is_active)
VALUES
    ('FPS', 'cdm_financial_institution', 'fi_id', '_GENERATED_UUID', 'INSTRUCTED_AGENT', 'VARCHAR', 670, true),
    ('FPS', 'cdm_financial_institution', 'bic', 'grphdr_instdagt_fininstnid_bicfi', 'INSTRUCTED_AGENT', 'VARCHAR', 671, true),
    ('FPS', 'cdm_financial_institution', 'source_system', '''FPS''', 'INSTRUCTED_AGENT', 'VARCHAR', 672, true),
    ('FPS', 'cdm_financial_institution', 'is_current', 'true', 'INSTRUCTED_AGENT', 'BOOLEAN', 673, true);

-- ========================================
-- cdm_payment_extension_fps mappings (ALL remaining fields)
-- ========================================
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal_position, is_active)
VALUES
    -- Core extension fields
    ('FPS', 'cdm_payment_extension_fps', 'extension_id', '_GENERATED_UUID', NULL, 'VARCHAR', 700, true),
    ('FPS', 'cdm_payment_extension_fps', 'instruction_id', '_PARENT_INSTRUCTION_ID', NULL, 'VARCHAR', 701, true),
    ('FPS', 'cdm_payment_extension_fps', 'format_id', '''FPS''', NULL, 'VARCHAR', 702, true),
    ('FPS', 'cdm_payment_extension_fps', 'message_type', 'message_type', NULL, 'VARCHAR', 703, true),
    ('FPS', 'cdm_payment_extension_fps', 'payment_id', 'payment_id', NULL, 'VARCHAR', 704, true),
    ('FPS', 'cdm_payment_extension_fps', 'payment_reference', 'payment_reference', NULL, 'VARCHAR', 705, true),
    ('FPS', 'cdm_payment_extension_fps', 'raw_id', 'raw_id', NULL, 'VARCHAR', 706, true),
    ('FPS', 'cdm_payment_extension_fps', 'requested_execution_date', 'requested_execution_date', NULL, 'DATE', 707, true),
    ('FPS', 'cdm_payment_extension_fps', 'settlement_datetime', 'settlement_datetime', NULL, 'TIMESTAMP', 708, true),

    -- FPS-specific sort codes and accounts
    ('FPS', 'cdm_payment_extension_fps', 'payer_sort_code', 'payer_sort_code', NULL, 'VARCHAR', 709, true),
    ('FPS', 'cdm_payment_extension_fps', 'payee_sort_code', 'payee_sort_code', NULL, 'VARCHAR', 710, true),
    ('FPS', 'cdm_payment_extension_fps', 'payer_account_number', 'payer_account', NULL, 'VARCHAR', 711, true),
    ('FPS', 'cdm_payment_extension_fps', 'payee_account_number', 'payee_account', NULL, 'VARCHAR', 712, true),
    ('FPS', 'cdm_payment_extension_fps', 'payer_address', 'payer_address', NULL, 'TEXT', 713, true),
    ('FPS', 'cdm_payment_extension_fps', 'payee_address', 'payee_address', NULL, 'TEXT', 714, true),
    ('FPS', 'cdm_payment_extension_fps', 'fps_payment_id', 'payment_id', NULL, 'VARCHAR', 715, true),
    ('FPS', 'cdm_payment_extension_fps', 'clearing_system', 'grphdr_sttlminf_clrsys_cd', NULL, 'VARCHAR', 716, true),

    -- Group Header fields
    ('FPS', 'cdm_payment_extension_fps', 'grphdr_instdagt_fininstnid_bicfi', 'grphdr_instdagt_fininstnid_bicfi', NULL, 'VARCHAR', 720, true),
    ('FPS', 'cdm_payment_extension_fps', 'grphdr_instgagt_fininstnid_bicfi', 'grphdr_instgagt_fininstnid_bicfi', NULL, 'VARCHAR', 721, true),
    ('FPS', 'cdm_payment_extension_fps', 'grphdr_nboftxs', 'grphdr_nboftxs', NULL, 'VARCHAR', 722, true),
    ('FPS', 'cdm_payment_extension_fps', 'grphdr_sttlminf_clrsys_cd', 'grphdr_sttlminf_clrsys_cd', NULL, 'VARCHAR', 723, true),
    ('FPS', 'cdm_payment_extension_fps', 'grphdr_sttlminf_sttlmmtd', 'grphdr_sttlminf_sttlmmtd', NULL, 'VARCHAR', 724, true),
    ('FPS', 'cdm_payment_extension_fps', 'grphdr_ttlintrbksttlmamt', 'grphdr_ttlintrbksttlmamt', NULL, 'DECIMAL', 725, true),
    ('FPS', 'cdm_payment_extension_fps', 'grphdr_ttlintrbksttlmamt_ccy', 'grphdr_ttlintrbksttlmamt_ccy', NULL, 'VARCHAR', 726, true),

    -- Payment Type Info
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_pmttpinf_ctgypurp_cd', 'cdttrftxinf_pmttpinf_ctgypurp_cd', NULL, 'VARCHAR', 730, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_pmttpinf_instrprty', 'cdttrftxinf_pmttpinf_instrprty', NULL, 'VARCHAR', 731, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_pmttpinf_lclinstrm_cd', 'cdttrftxinf_pmttpinf_lclinstrm_cd', NULL, 'VARCHAR', 732, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_pmttpinf_svclvl_cd', 'cdttrftxinf_pmttpinf_svclvl_cd', NULL, 'VARCHAR', 733, true),

    -- Payment ID
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_pmtid_clrsysref', 'cdttrftxinf_pmtid_clrsysref', NULL, 'VARCHAR', 734, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_pmtid_uetr', 'cdttrftxinf_pmtid_uetr', NULL, 'VARCHAR', 735, true),

    -- Amounts
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_instdamt', 'cdttrftxinf_instdamt', NULL, 'DECIMAL', 736, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_instdamt_ccy', 'cdttrftxinf_instdamt_ccy', NULL, 'VARCHAR', 737, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_xchgrate', 'cdttrftxinf_xchgrate', NULL, 'DECIMAL', 738, true),

    -- Interbank Settlement
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_intrbksttlmdt', 'cdttrftxinf_intrbksttlmdt', NULL, 'DATE', 739, true),

    -- Charges
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_chrgbr', 'cdttrftxinf_chrgbr', NULL, 'VARCHAR', 740, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_chrgsinf_amt', 'cdttrftxinf_chrgsinf_amt', NULL, 'DECIMAL', 741, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_chrgsinf_amt_ccy', 'cdttrftxinf_chrgsinf_amt_ccy', NULL, 'VARCHAR', 742, true),

    -- Purpose
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_purp_cd', 'cdttrftxinf_purp_cd', NULL, 'VARCHAR', 743, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_purp_prtry', 'cdttrftxinf_purp_prtry', NULL, 'VARCHAR', 744, true),

    -- Regulatory Reporting
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_rgltryrptg_dtls_cd', 'cdttrftxinf_rgltryrptg_dtls_cd', NULL, 'VARCHAR', 745, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_rgltryrptg_dtls_inf', 'cdttrftxinf_rgltryrptg_dtls_inf', NULL, 'TEXT', 746, true),

    -- Remittance Info (structured)
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_rmtinf_strd_addtlrmtinf', 'cdttrftxinf_rmtinf_strd_addtlrmtinf', NULL, 'TEXT', 747, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_rmtinf_strd_cdtrrefinf_tp_cdorprtry_cd', 'cdttrftxinf_rmtinf_strd_cdtrrefinf_tp_cdorprtry_cd', NULL, 'VARCHAR', 748, true),

    -- Instruction for Agents
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_instrforcdtragt_cd', 'cdttrftxinf_instrforcdtragt_cd', NULL, 'VARCHAR', 749, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_instrforcdtragt_instrinf', 'cdttrftxinf_instrforcdtragt_instrinf', NULL, 'TEXT', 750, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_instrfornxtagt_cd', 'cdttrftxinf_instrfornxtagt_cd', NULL, 'VARCHAR', 751, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_instrfornxtagt_instrinf', 'cdttrftxinf_instrfornxtagt_instrinf', NULL, 'TEXT', 752, true),

    -- Intermediary Agent 1
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_intrmyagt1_fininstnid_bicfi', 'cdttrftxinf_intrmyagt1_fininstnid_bicfi', NULL, 'VARCHAR', 753, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_intrmyagt1_fininstnid_clrsysmmbid_mmbid', 'cdttrftxinf_intrmyagt1_fininstnid_clrsysmmbid_mmbid', NULL, 'VARCHAR', 754, true),

    -- Debtor Info
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtr_ctctdtls_emailadr', 'cdttrftxinf_dbtr_ctctdtls_emailadr', NULL, 'VARCHAR', 760, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtr_ctctdtls_phnenb', 'cdttrftxinf_dbtr_ctctdtls_phnenb', NULL, 'VARCHAR', 761, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtr_ctryofres', 'cdttrftxinf_dbtr_ctryofres', NULL, 'VARCHAR', 762, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtr_id_orgid_anybic', 'cdttrftxinf_dbtr_id_orgid_anybic', NULL, 'VARCHAR', 763, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtr_id_orgid_lei', 'cdttrftxinf_dbtr_id_orgid_lei', NULL, 'VARCHAR', 764, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtr_id_orgid_othr_id', 'cdttrftxinf_dbtr_id_orgid_othr_id', NULL, 'VARCHAR', 765, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtr_pstladr_bldgnb', 'cdttrftxinf_dbtr_pstladr_bldgnb', NULL, 'VARCHAR', 766, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtr_pstladr_ctry', 'cdttrftxinf_dbtr_pstladr_ctry', NULL, 'VARCHAR', 767, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtr_pstladr_ctrysubdvsn', 'cdttrftxinf_dbtr_pstladr_ctrysubdvsn', NULL, 'VARCHAR', 768, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtr_pstladr_pstcd', 'cdttrftxinf_dbtr_pstladr_pstcd', NULL, 'VARCHAR', 769, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtr_pstladr_strtnm', 'cdttrftxinf_dbtr_pstladr_strtnm', NULL, 'VARCHAR', 770, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtr_pstladr_twnnm', 'cdttrftxinf_dbtr_pstladr_twnnm', NULL, 'VARCHAR', 771, true),

    -- Debtor Account
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtracct_ccy', 'cdttrftxinf_dbtracct_ccy', NULL, 'VARCHAR', 772, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtracct_id_iban', 'cdttrftxinf_dbtracct_id_iban', NULL, 'VARCHAR', 773, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtracct_id_othr_schmenm_cd', 'cdttrftxinf_dbtracct_id_othr_schmenm_cd', NULL, 'VARCHAR', 774, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtracct_nm', 'cdttrftxinf_dbtracct_nm', NULL, 'VARCHAR', 775, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtracct_tp_cd', 'cdttrftxinf_dbtracct_tp_cd', NULL, 'VARCHAR', 776, true),

    -- Debtor Agent
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtragt_brnchid_id', 'cdttrftxinf_dbtragt_brnchid_id', NULL, 'VARCHAR', 777, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtragt_fininstnid_bicfi', 'cdttrftxinf_dbtragt_fininstnid_bicfi', NULL, 'VARCHAR', 778, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtragt_fininstnid_clrsysmmbid_clrsysid_cd', 'cdttrftxinf_dbtragt_fininstnid_clrsysmmbid_clrsysid_cd', NULL, 'VARCHAR', 779, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtragt_fininstnid_lei', 'cdttrftxinf_dbtragt_fininstnid_lei', NULL, 'VARCHAR', 780, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtragt_fininstnid_nm', 'cdttrftxinf_dbtragt_fininstnid_nm', NULL, 'VARCHAR', 781, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_dbtragt_fininstnid_pstladr_ctry', 'cdttrftxinf_dbtragt_fininstnid_pstladr_ctry', NULL, 'VARCHAR', 782, true),

    -- Creditor Info
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtr_ctctdtls_emailadr', 'cdttrftxinf_cdtr_ctctdtls_emailadr', NULL, 'VARCHAR', 790, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtr_ctctdtls_phnenb', 'cdttrftxinf_cdtr_ctctdtls_phnenb', NULL, 'VARCHAR', 791, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtr_ctryofres', 'cdttrftxinf_cdtr_ctryofres', NULL, 'VARCHAR', 792, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtr_id_orgid_anybic', 'cdttrftxinf_cdtr_id_orgid_anybic', NULL, 'VARCHAR', 793, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtr_id_orgid_lei', 'cdttrftxinf_cdtr_id_orgid_lei', NULL, 'VARCHAR', 794, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtr_id_orgid_othr_id', 'cdttrftxinf_cdtr_id_orgid_othr_id', NULL, 'VARCHAR', 795, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtr_pstladr_bldgnb', 'cdttrftxinf_cdtr_pstladr_bldgnb', NULL, 'VARCHAR', 796, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtr_pstladr_ctry', 'cdttrftxinf_cdtr_pstladr_ctry', NULL, 'VARCHAR', 797, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtr_pstladr_ctrysubdvsn', 'cdttrftxinf_cdtr_pstladr_ctrysubdvsn', NULL, 'VARCHAR', 798, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtr_pstladr_pstcd', 'cdttrftxinf_cdtr_pstladr_pstcd', NULL, 'VARCHAR', 799, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtr_pstladr_strtnm', 'cdttrftxinf_cdtr_pstladr_strtnm', NULL, 'VARCHAR', 800, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtr_pstladr_twnnm', 'cdttrftxinf_cdtr_pstladr_twnnm', NULL, 'VARCHAR', 801, true),

    -- Creditor Account
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtracct_ccy', 'cdttrftxinf_cdtracct_ccy', NULL, 'VARCHAR', 802, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtracct_id_iban', 'cdttrftxinf_cdtracct_id_iban', NULL, 'VARCHAR', 803, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtracct_id_othr_schmenm_cd', 'cdttrftxinf_cdtracct_id_othr_schmenm_cd', NULL, 'VARCHAR', 804, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtracct_nm', 'cdttrftxinf_cdtracct_nm', NULL, 'VARCHAR', 805, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtracct_tp_cd', 'cdttrftxinf_cdtracct_tp_cd', NULL, 'VARCHAR', 806, true),

    -- Creditor Agent
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtragt_brnchid_id', 'cdttrftxinf_cdtragt_brnchid_id', NULL, 'VARCHAR', 807, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtragt_fininstnid_bicfi', 'cdttrftxinf_cdtragt_fininstnid_bicfi', NULL, 'VARCHAR', 808, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtragt_fininstnid_clrsysmmbid_clrsysid_cd', 'cdttrftxinf_cdtragt_fininstnid_clrsysmmbid_clrsysid_cd', NULL, 'VARCHAR', 809, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtragt_fininstnid_lei', 'cdttrftxinf_cdtragt_fininstnid_lei', NULL, 'VARCHAR', 810, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtragt_fininstnid_nm', 'cdttrftxinf_cdtragt_fininstnid_nm', NULL, 'VARCHAR', 811, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_cdtragt_fininstnid_pstladr_ctry', 'cdttrftxinf_cdtragt_fininstnid_pstladr_ctry', NULL, 'VARCHAR', 812, true),

    -- Ultimate Parties
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_ultmtdbtr_nm', 'cdttrftxinf_ultmtdbtr_nm', NULL, 'VARCHAR', 820, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_ultmtdbtr_ctryofres', 'cdttrftxinf_ultmtdbtr_ctryofres', NULL, 'VARCHAR', 821, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_ultmtcdtr_nm', 'cdttrftxinf_ultmtcdtr_nm', NULL, 'VARCHAR', 822, true),
    ('FPS', 'cdm_payment_extension_fps', 'cdttrftxinf_ultmtcdtr_ctryofres', 'cdttrftxinf_ultmtcdtr_ctryofres', NULL, 'VARCHAR', 823, true);

-- =============================================================================
-- Step 4: Verify coverage
-- =============================================================================
-- Count Silver columns in actual table
SELECT 'Silver columns in stg_fps table' as metric, COUNT(*) as count
FROM information_schema.columns
WHERE table_schema = 'silver' AND table_name = 'stg_fps';

-- Count Gold mappings
SELECT 'Gold mappings for FPS' as metric, COUNT(*) as count
FROM mapping.gold_field_mappings
WHERE format_id = 'FPS' AND is_active = true;

-- Show Gold mappings by table
SELECT gold_table, entity_role, COUNT(*) as count
FROM mapping.gold_field_mappings
WHERE format_id = 'FPS' AND is_active = true
GROUP BY gold_table, entity_role
ORDER BY gold_table, entity_role;

-- Calculate coverage: Silver columns with at least one Gold mapping
WITH silver_cols AS (
    SELECT column_name as col FROM information_schema.columns
    WHERE table_schema = 'silver' AND table_name = 'stg_fps'
    -- Exclude system/metadata columns that don't need Gold mappings
    AND column_name NOT IN ('_ingested_at', '_processed_at', '_source_file', 'processed_to_gold_at', 'processing_status')
),
gold_mapped AS (
    SELECT DISTINCT source_expression as col
    FROM mapping.gold_field_mappings
    WHERE format_id = 'FPS'
    AND is_active = true
    AND source_expression NOT LIKE '''%'''
    AND source_expression NOT IN ('_GENERATED_UUID', '_PARENT_INSTRUCTION_ID', 'true', 'false')
)
SELECT
    (SELECT COUNT(*) FROM silver_cols) as total_silver_cols,
    (SELECT COUNT(*) FROM silver_cols s WHERE EXISTS (SELECT 1 FROM gold_mapped g WHERE g.col = s.col)) as mapped_silver_cols,
    ROUND(
        (SELECT COUNT(*) FROM silver_cols s WHERE EXISTS (SELECT 1 FROM gold_mapped g WHERE g.col = s.col))::NUMERIC /
        (SELECT COUNT(*) FROM silver_cols) * 100, 1
    ) as coverage_pct;

COMMIT;
