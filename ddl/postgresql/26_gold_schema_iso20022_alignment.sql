-- ============================================================================
-- Gold Schema ISO 20022 Alignment
-- ============================================================================
-- This script aligns Gold schema column names with descriptive ISO 20022
-- terminology for semantic clarity while maintaining backward compatibility.
--
-- Naming Convention:
--   Silver: Abbreviated ISO 20022 names (e.g., intr_bk_sttlm_amt)
--   Gold: Full descriptive names (e.g., interbank_settlement_amount)
--
-- ISO 20022 Element → Gold Column Name mappings:
--   GrpHdr/MsgId         → group_header_message_id
--   GrpHdr/CreDtTm       → group_header_creation_datetime
--   GrpHdr/NbOfTxs       → number_of_transactions
--   GrpHdr/CtrlSum       → control_sum
--   GrpHdr/SttlmInf/SttlmMtd → settlement_method
--   IntrBkSttlmAmt       → interbank_settlement_amount
--   IntrBkSttlmCcy       → interbank_settlement_currency
--   IntrBkSttlmDt        → interbank_settlement_date
--   InstdAmt             → instructed_amount
--   InstdAmt/@Ccy        → instructed_currency
--   XchgRate             → exchange_rate
--   ChrgBr               → charge_bearer
--   PmtId/InstrId        → payment_instruction_identification
--   PmtId/EndToEndId     → end_to_end_identification
--   PmtId/UETR           → unique_end_to_end_transaction_reference
--   PmtId/TxId           → transaction_identification
--   PmtId/ClrSysRef      → clearing_system_reference
--   PmtTpInf/InstrPrty   → instruction_priority
--   PmtTpInf/SvcLvl/Cd   → service_level_code
--   PmtTpInf/LclInstrm   → local_instrument_code
--   PmtTpInf/CtgyPurp    → category_purpose_code
--   Purp/Cd              → purpose_code
--   RmtInf/Ustrd         → remittance_information_unstructured
--   RmtInf/Strd          → remittance_information_structured
-- ============================================================================

-- ============================================================================
-- STEP 1: Add new descriptive columns to cdm_payment_instruction
-- ============================================================================

-- Group Header fields
ALTER TABLE gold.cdm_payment_instruction
ADD COLUMN IF NOT EXISTS group_header_message_id VARCHAR(50);

ALTER TABLE gold.cdm_payment_instruction
ADD COLUMN IF NOT EXISTS group_header_creation_datetime TIMESTAMP;

-- Interbank Settlement fields (rename from amount/currency/settlement_*)
-- These are the core payment amount fields
COMMENT ON COLUMN gold.cdm_payment_instruction.amount IS
  'Interbank settlement amount - maps to ISO 20022 IntrBkSttlmAmt';

COMMENT ON COLUMN gold.cdm_payment_instruction.currency IS
  'Interbank settlement currency - maps to ISO 20022 IntrBkSttlmAmt/@Ccy';

-- Add interbank_settlement_date if not exists
ALTER TABLE gold.cdm_payment_instruction
ADD COLUMN IF NOT EXISTS interbank_settlement_date DATE;

-- Instructed Amount fields (original amount requested before FX)
ALTER TABLE gold.cdm_payment_instruction
ADD COLUMN IF NOT EXISTS instructed_amount NUMERIC(18,4);

ALTER TABLE gold.cdm_payment_instruction
ADD COLUMN IF NOT EXISTS instructed_currency VARCHAR(3);

-- Payment Identification fields
ALTER TABLE gold.cdm_payment_instruction
ADD COLUMN IF NOT EXISTS payment_instruction_identification VARCHAR(35);

ALTER TABLE gold.cdm_payment_instruction
ADD COLUMN IF NOT EXISTS unique_end_to_end_transaction_reference VARCHAR(36);

ALTER TABLE gold.cdm_payment_instruction
ADD COLUMN IF NOT EXISTS transaction_identification VARCHAR(50);

-- Payment Type Information fields
ALTER TABLE gold.cdm_payment_instruction
ADD COLUMN IF NOT EXISTS service_level_code VARCHAR(30);

ALTER TABLE gold.cdm_payment_instruction
ADD COLUMN IF NOT EXISTS local_instrument_code VARCHAR(50);

ALTER TABLE gold.cdm_payment_instruction
ADD COLUMN IF NOT EXISTS category_purpose_code VARCHAR(10);

-- Purpose fields
ALTER TABLE gold.cdm_payment_instruction
ADD COLUMN IF NOT EXISTS purpose_code VARCHAR(10);

-- Remittance Information
ALTER TABLE gold.cdm_payment_instruction
ADD COLUMN IF NOT EXISTS remittance_information_unstructured TEXT[];

ALTER TABLE gold.cdm_payment_instruction
ADD COLUMN IF NOT EXISTS remittance_information_structured JSONB;

-- Acceptance and Settlement timestamps
ALTER TABLE gold.cdm_payment_instruction
ADD COLUMN IF NOT EXISTS acceptance_datetime TIMESTAMP;

-- ============================================================================
-- STEP 2: Migrate data from old columns to new columns (if applicable)
-- ============================================================================

-- Copy existing data to new columns where appropriate
UPDATE gold.cdm_payment_instruction
SET
    group_header_message_id = message_id,
    group_header_creation_datetime = creation_datetime,
    payment_instruction_identification = instruction_identification,
    unique_end_to_end_transaction_reference = uetr,
    service_level_code = service_level,
    local_instrument_code = local_instrument,
    category_purpose_code = category_purpose,
    purpose_code = purpose,
    remittance_information_unstructured = remittance_unstructured,
    remittance_information_structured = remittance_structured
WHERE group_header_message_id IS NULL AND message_id IS NOT NULL;

-- ============================================================================
-- STEP 3: Add comments for documentation
-- ============================================================================

COMMENT ON COLUMN gold.cdm_payment_instruction.group_header_message_id IS
  'ISO 20022 GrpHdr/MsgId - Point to point reference for the message';

COMMENT ON COLUMN gold.cdm_payment_instruction.group_header_creation_datetime IS
  'ISO 20022 GrpHdr/CreDtTm - Date and time the message was created';

COMMENT ON COLUMN gold.cdm_payment_instruction.interbank_settlement_date IS
  'ISO 20022 IntrBkSttlmDt - Date on which interbank settlement occurs';

COMMENT ON COLUMN gold.cdm_payment_instruction.instructed_amount IS
  'ISO 20022 InstdAmt - Original amount instructed before currency conversion';

COMMENT ON COLUMN gold.cdm_payment_instruction.instructed_currency IS
  'ISO 20022 InstdAmt/@Ccy - Currency of the instructed amount';

COMMENT ON COLUMN gold.cdm_payment_instruction.payment_instruction_identification IS
  'ISO 20022 PmtId/InstrId - Unique identification assigned by instructing party';

COMMENT ON COLUMN gold.cdm_payment_instruction.unique_end_to_end_transaction_reference IS
  'ISO 20022 UETR - Universally unique identifier for end-to-end transaction reference';

COMMENT ON COLUMN gold.cdm_payment_instruction.transaction_identification IS
  'ISO 20022 PmtId/TxId - Unique identification assigned by first instructing agent';

COMMENT ON COLUMN gold.cdm_payment_instruction.service_level_code IS
  'ISO 20022 PmtTpInf/SvcLvl/Cd - Agreement under which the payment must be processed';

COMMENT ON COLUMN gold.cdm_payment_instruction.local_instrument_code IS
  'ISO 20022 PmtTpInf/LclInstrm/Cd - Community specific local instrument code';

COMMENT ON COLUMN gold.cdm_payment_instruction.category_purpose_code IS
  'ISO 20022 PmtTpInf/CtgyPurp/Cd - High level purpose of the instruction';

COMMENT ON COLUMN gold.cdm_payment_instruction.purpose_code IS
  'ISO 20022 Purp/Cd - Underlying reason for the payment transaction';

COMMENT ON COLUMN gold.cdm_payment_instruction.remittance_information_unstructured IS
  'ISO 20022 RmtInf/Ustrd - Unstructured information to enable matching';

COMMENT ON COLUMN gold.cdm_payment_instruction.remittance_information_structured IS
  'ISO 20022 RmtInf/Strd - Structured reference information for reconciliation';

COMMENT ON COLUMN gold.cdm_payment_instruction.acceptance_datetime IS
  'ISO 20022 AccptncDtTm - Date and time payment instruction was accepted';

-- ============================================================================
-- STEP 4: Create index for new columns used in queries
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_cdm_payment_instruction_grp_hdr_msg_id
ON gold.cdm_payment_instruction(group_header_message_id);

CREATE INDEX IF NOT EXISTS idx_cdm_payment_instruction_intr_bk_sttlm_dt
ON gold.cdm_payment_instruction(interbank_settlement_date);

CREATE INDEX IF NOT EXISTS idx_cdm_payment_instruction_pmt_instr_id
ON gold.cdm_payment_instruction(payment_instruction_identification);

-- ============================================================================
-- STEP 5: Update Gold field mappings for pacs.008.base
-- ============================================================================

-- Deactivate old mappings for columns that are being renamed/replaced
UPDATE mapping.gold_field_mappings
SET is_active = false
WHERE format_id = 'pacs.008.base'
  AND gold_table = 'cdm_payment_instruction'
  AND gold_column IN ('message_id', 'instruction_identification', 'uetr',
                       'service_level', 'local_instrument', 'category_purpose',
                       'purpose', 'remittance_unstructured', 'remittance_structured');

-- Insert new mappings with descriptive column names
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, ordinal_position, is_active)
VALUES
    -- Group Header fields
    ('pacs.008.base', 'cdm_payment_instruction', 'group_header_message_id', 'grp_hdr_msg_id', NULL, 10, true),
    ('pacs.008.base', 'cdm_payment_instruction', 'group_header_creation_datetime', 'grp_hdr_cre_dt_tm', NULL, 11, true),

    -- Interbank Settlement fields
    ('pacs.008.base', 'cdm_payment_instruction', 'interbank_settlement_date', 'intr_bk_sttlm_dt', NULL, 55, true),

    -- Instructed Amount fields
    ('pacs.008.base', 'cdm_payment_instruction', 'instructed_amount', 'instd_amt', NULL, 56, true),
    ('pacs.008.base', 'cdm_payment_instruction', 'instructed_currency', 'instd_amt_ccy', NULL, 57, true),

    -- Payment Identification fields
    ('pacs.008.base', 'cdm_payment_instruction', 'payment_instruction_identification', 'pmt_id_instr_id', NULL, 20, true),
    ('pacs.008.base', 'cdm_payment_instruction', 'unique_end_to_end_transaction_reference', 'pmt_id_uetr', NULL, 22, true),
    ('pacs.008.base', 'cdm_payment_instruction', 'transaction_identification', 'pmt_id_tx_id', NULL, 23, true),

    -- Payment Type Information fields
    ('pacs.008.base', 'cdm_payment_instruction', 'service_level_code', 'pmt_tp_inf_svc_lvl_cd', NULL, 30, true),
    ('pacs.008.base', 'cdm_payment_instruction', 'local_instrument_code', 'pmt_tp_inf_lcl_instrm_cd', NULL, 31, true),
    ('pacs.008.base', 'cdm_payment_instruction', 'category_purpose_code', 'pmt_tp_inf_ctgy_purp_cd', NULL, 32, true),

    -- Purpose fields
    ('pacs.008.base', 'cdm_payment_instruction', 'purpose_code', 'purp_cd', NULL, 60, true),

    -- Acceptance datetime
    ('pacs.008.base', 'cdm_payment_instruction', 'acceptance_datetime', 'accptnc_dt_tm', NULL, 61, true)
ON CONFLICT (format_id, gold_table, gold_column, entity_role)
DO UPDATE SET
    source_expression = EXCLUDED.source_expression,
    ordinal_position = EXCLUDED.ordinal_position,
    is_active = true;

-- Keep the existing amount/currency mappings as they are (renamed from instructed_* to amount/currency)
-- These map to intr_bk_sttlm_amt and intr_bk_sttlm_ccy

SELECT 'Gold schema ISO 20022 alignment complete' as status;
