-- =============================================================================
-- Migration: Add source_instruction_id to Entity Tables
-- =============================================================================
-- Phase 1 of GPS CDM Major Refactoring Plan
--
-- Purpose: Add source_instruction_id columns to entity tables to enable:
--   1. Traceability from entities back to the source payment instruction
--   2. Support for "always INSERT" entity persistence (preserve payment-level history)
--   3. Ability to query all entity records created for a specific payment
--
-- Affected Tables:
--   - gold.cdm_party
--   - gold.cdm_account
--   - gold.cdm_financial_institution
--   - gold.cdm_party_identifier
--   - gold.cdm_account_identifier
--   - gold.cdm_institution_identifier
--
-- Date: 2026-01-10
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Add source_instruction_id to cdm_party
-- -----------------------------------------------------------------------------
ALTER TABLE gold.cdm_party
ADD COLUMN IF NOT EXISTS source_instruction_id VARCHAR(36);

COMMENT ON COLUMN gold.cdm_party.source_instruction_id IS
'References the payment instruction that created this party record. Enables payment-level entity history.';

CREATE INDEX IF NOT EXISTS idx_cdm_party_src_instr
ON gold.cdm_party(source_instruction_id);

-- -----------------------------------------------------------------------------
-- 2. Add source_instruction_id to cdm_account
-- -----------------------------------------------------------------------------
ALTER TABLE gold.cdm_account
ADD COLUMN IF NOT EXISTS source_instruction_id VARCHAR(36);

COMMENT ON COLUMN gold.cdm_account.source_instruction_id IS
'References the payment instruction that created this account record. Enables payment-level entity history.';

CREATE INDEX IF NOT EXISTS idx_cdm_account_src_instr
ON gold.cdm_account(source_instruction_id);

-- -----------------------------------------------------------------------------
-- 3. Add source_instruction_id to cdm_financial_institution
-- -----------------------------------------------------------------------------
ALTER TABLE gold.cdm_financial_institution
ADD COLUMN IF NOT EXISTS source_instruction_id VARCHAR(36);

COMMENT ON COLUMN gold.cdm_financial_institution.source_instruction_id IS
'References the payment instruction that created this FI record. Enables payment-level entity history.';

CREATE INDEX IF NOT EXISTS idx_cdm_fi_src_instr
ON gold.cdm_financial_institution(source_instruction_id);

-- -----------------------------------------------------------------------------
-- 4. Add source_instruction_id to cdm_party_identifiers (plural)
-- -----------------------------------------------------------------------------
ALTER TABLE gold.cdm_party_identifiers
ADD COLUMN IF NOT EXISTS source_instruction_id VARCHAR(36);

COMMENT ON COLUMN gold.cdm_party_identifiers.source_instruction_id IS
'References the payment instruction that created this identifier record. Enables payment-level history.';

CREATE INDEX IF NOT EXISTS idx_cdm_party_ids_src_instr
ON gold.cdm_party_identifiers(source_instruction_id);

-- -----------------------------------------------------------------------------
-- 5. Add source_instruction_id to cdm_account_identifiers (plural)
-- -----------------------------------------------------------------------------
ALTER TABLE gold.cdm_account_identifiers
ADD COLUMN IF NOT EXISTS source_instruction_id VARCHAR(36);

COMMENT ON COLUMN gold.cdm_account_identifiers.source_instruction_id IS
'References the payment instruction that created this identifier record. Enables payment-level history.';

CREATE INDEX IF NOT EXISTS idx_cdm_acct_ids_src_instr
ON gold.cdm_account_identifiers(source_instruction_id);

-- -----------------------------------------------------------------------------
-- 6. Add source_instruction_id to cdm_institution_identifiers (plural)
-- -----------------------------------------------------------------------------
ALTER TABLE gold.cdm_institution_identifiers
ADD COLUMN IF NOT EXISTS source_instruction_id VARCHAR(36);

COMMENT ON COLUMN gold.cdm_institution_identifiers.source_instruction_id IS
'References the payment instruction that created this identifier record. Enables payment-level history.';

CREATE INDEX IF NOT EXISTS idx_cdm_inst_ids_src_instr
ON gold.cdm_institution_identifiers(source_instruction_id);

-- -----------------------------------------------------------------------------
-- 7. Verification queries
-- -----------------------------------------------------------------------------

-- Verify columns were added
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'gold'
  AND column_name = 'source_instruction_id'
ORDER BY table_name;

-- Verify indexes were created
SELECT
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'gold'
  AND indexname LIKE '%src_instr%'
ORDER BY tablename;
