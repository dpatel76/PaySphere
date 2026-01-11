-- =============================================================================
-- Migration: Add Entity FK References to ISO Semantic Tables (Phase 6)
-- =============================================================================
-- Part of GPS CDM Major Refactoring Plan
--
-- Purpose:
--   1. Add entity FK columns to ISO semantic tables (pain.*, pacs.*, camt.*)
--   2. Keep denormalized columns temporarily for backwards compatibility
--   3. Deprecate denormalized columns (will be removed in future migration)
--
-- Migration Strategy:
--   Phase 6a (this migration): ADD entity FK columns
--   Phase 6b (future): POPULATE FK columns from Silver → Gold mappings
--   Phase 6c (future): DROP denormalized columns after full migration
--
-- Date: 2026-01-10
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Add entity FK columns to cdm_pain_customer_credit_transfer_initiation
-- -----------------------------------------------------------------------------
ALTER TABLE gold.cdm_pain_customer_credit_transfer_initiation
    ADD COLUMN IF NOT EXISTS debtor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS debtor_account_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS debtor_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS creditor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS creditor_account_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS creditor_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS initiating_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS ultimate_debtor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS ultimate_creditor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS intermediary_agent1_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS intermediary_agent2_id VARCHAR(36);

-- Add comments to document FK relationships
COMMENT ON COLUMN gold.cdm_pain_customer_credit_transfer_initiation.debtor_party_id IS
    'FK to cdm_party: References the debtor (payer) party entity';
COMMENT ON COLUMN gold.cdm_pain_customer_credit_transfer_initiation.debtor_account_id IS
    'FK to cdm_account: References the debtor account entity';
COMMENT ON COLUMN gold.cdm_pain_customer_credit_transfer_initiation.debtor_agent_id IS
    'FK to cdm_financial_institution: References the debtor agent (bank)';
COMMENT ON COLUMN gold.cdm_pain_customer_credit_transfer_initiation.creditor_party_id IS
    'FK to cdm_party: References the creditor (payee) party entity';
COMMENT ON COLUMN gold.cdm_pain_customer_credit_transfer_initiation.creditor_account_id IS
    'FK to cdm_account: References the creditor account entity';
COMMENT ON COLUMN gold.cdm_pain_customer_credit_transfer_initiation.creditor_agent_id IS
    'FK to cdm_financial_institution: References the creditor agent (bank)';

-- Create indexes on FK columns
CREATE INDEX IF NOT EXISTS idx_pain_cct_init_debtor_party ON gold.cdm_pain_customer_credit_transfer_initiation(debtor_party_id);
CREATE INDEX IF NOT EXISTS idx_pain_cct_init_creditor_party ON gold.cdm_pain_customer_credit_transfer_initiation(creditor_party_id);
CREATE INDEX IF NOT EXISTS idx_pain_cct_init_debtor_agent ON gold.cdm_pain_customer_credit_transfer_initiation(debtor_agent_id);
CREATE INDEX IF NOT EXISTS idx_pain_cct_init_creditor_agent ON gold.cdm_pain_customer_credit_transfer_initiation(creditor_agent_id);

-- -----------------------------------------------------------------------------
-- 2. Add entity FK columns to cdm_pacs_fi_customer_credit_transfer (pacs.008)
-- -----------------------------------------------------------------------------
ALTER TABLE gold.cdm_pacs_fi_customer_credit_transfer
    ADD COLUMN IF NOT EXISTS debtor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS debtor_account_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS debtor_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS creditor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS creditor_account_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS creditor_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS instructing_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS instructed_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS ultimate_debtor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS ultimate_creditor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS intermediary_agent1_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS intermediary_agent2_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS intermediary_agent3_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS previous_instructing_agent_id VARCHAR(36);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_pacs_fi_cct_debtor_party ON gold.cdm_pacs_fi_customer_credit_transfer(debtor_party_id);
CREATE INDEX IF NOT EXISTS idx_pacs_fi_cct_creditor_party ON gold.cdm_pacs_fi_customer_credit_transfer(creditor_party_id);
CREATE INDEX IF NOT EXISTS idx_pacs_fi_cct_debtor_agent ON gold.cdm_pacs_fi_customer_credit_transfer(debtor_agent_id);
CREATE INDEX IF NOT EXISTS idx_pacs_fi_cct_creditor_agent ON gold.cdm_pacs_fi_customer_credit_transfer(creditor_agent_id);

-- -----------------------------------------------------------------------------
-- 3. Add entity FK columns to cdm_pacs_fi_credit_transfer (pacs.009)
-- -----------------------------------------------------------------------------
ALTER TABLE gold.cdm_pacs_fi_credit_transfer
    ADD COLUMN IF NOT EXISTS debtor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS debtor_account_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS debtor_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS creditor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS creditor_account_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS creditor_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS instructing_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS instructed_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS intermediary_agent1_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS intermediary_agent2_id VARCHAR(36);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_pacs_fi_ct_debtor_agent ON gold.cdm_pacs_fi_credit_transfer(debtor_agent_id);
CREATE INDEX IF NOT EXISTS idx_pacs_fi_ct_creditor_agent ON gold.cdm_pacs_fi_credit_transfer(creditor_agent_id);

-- -----------------------------------------------------------------------------
-- 4. Add entity FK columns to cdm_pacs_payment_return (pacs.004)
-- -----------------------------------------------------------------------------
ALTER TABLE gold.cdm_pacs_payment_return
    ADD COLUMN IF NOT EXISTS return_debtor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS return_debtor_account_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS return_debtor_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS return_creditor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS return_creditor_account_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS return_creditor_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS instructing_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS instructed_agent_id VARCHAR(36);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_pacs_return_debtor_agent ON gold.cdm_pacs_payment_return(return_debtor_agent_id);
CREATE INDEX IF NOT EXISTS idx_pacs_return_creditor_agent ON gold.cdm_pacs_payment_return(return_creditor_agent_id);

-- -----------------------------------------------------------------------------
-- 5. Add entity FK columns to cdm_pacs_fi_payment_status_report (pacs.002)
-- -----------------------------------------------------------------------------
ALTER TABLE gold.cdm_pacs_fi_payment_status_report
    ADD COLUMN IF NOT EXISTS instructing_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS instructed_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS debtor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS debtor_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS creditor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS creditor_agent_id VARCHAR(36);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_pacs_status_debtor_agent ON gold.cdm_pacs_fi_payment_status_report(debtor_agent_id);
CREATE INDEX IF NOT EXISTS idx_pacs_status_creditor_agent ON gold.cdm_pacs_fi_payment_status_report(creditor_agent_id);

-- -----------------------------------------------------------------------------
-- 6. Add entity FK columns to cdm_camt_bank_to_customer_statement (camt.053)
-- -----------------------------------------------------------------------------
ALTER TABLE gold.cdm_camt_bank_to_customer_statement
    ADD COLUMN IF NOT EXISTS account_owner_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS account_servicer_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS statement_account_id VARCHAR(36);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_camt_stmt_owner ON gold.cdm_camt_bank_to_customer_statement(account_owner_party_id);
CREATE INDEX IF NOT EXISTS idx_camt_stmt_servicer ON gold.cdm_camt_bank_to_customer_statement(account_servicer_id);
CREATE INDEX IF NOT EXISTS idx_camt_stmt_account ON gold.cdm_camt_bank_to_customer_statement(statement_account_id);

-- -----------------------------------------------------------------------------
-- 7. Add entity FK columns to cdm_pain_customer_direct_debit_initiation (pain.008)
-- -----------------------------------------------------------------------------
ALTER TABLE gold.cdm_pain_customer_direct_debit_initiation
    ADD COLUMN IF NOT EXISTS creditor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS creditor_account_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS creditor_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS debtor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS debtor_account_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS debtor_agent_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS initiating_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS ultimate_creditor_party_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS ultimate_debtor_party_id VARCHAR(36);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_pain_ddi_creditor_party ON gold.cdm_pain_customer_direct_debit_initiation(creditor_party_id);
CREATE INDEX IF NOT EXISTS idx_pain_ddi_debtor_party ON gold.cdm_pain_customer_direct_debit_initiation(debtor_party_id);
CREATE INDEX IF NOT EXISTS idx_pain_ddi_creditor_agent ON gold.cdm_pain_customer_direct_debit_initiation(creditor_agent_id);
CREATE INDEX IF NOT EXISTS idx_pain_ddi_debtor_agent ON gold.cdm_pain_customer_direct_debit_initiation(debtor_agent_id);

-- -----------------------------------------------------------------------------
-- 8. Verification queries
-- -----------------------------------------------------------------------------

-- Verify FK columns added to ISO semantic tables
SELECT table_name, column_name
FROM information_schema.columns
WHERE table_schema = 'gold'
  AND column_name LIKE '%_party_id' OR column_name LIKE '%_agent_id' OR column_name LIKE '%_account_id'
  AND table_name LIKE 'cdm_pain_%' OR table_name LIKE 'cdm_pacs_%' OR table_name LIKE 'cdm_camt_%'
ORDER BY table_name, column_name;

-- Summary: count FK columns per table
SELECT table_name,
       COUNT(*) FILTER (WHERE column_name LIKE '%_party_id') as party_fks,
       COUNT(*) FILTER (WHERE column_name LIKE '%_agent_id') as agent_fks,
       COUNT(*) FILTER (WHERE column_name LIKE '%_account_id') as account_fks
FROM information_schema.columns
WHERE table_schema = 'gold'
  AND (table_name LIKE 'cdm_pain_%' OR table_name LIKE 'cdm_pacs_%' OR table_name LIKE 'cdm_camt_%')
  AND (column_name LIKE '%_party_id' OR column_name LIKE '%_agent_id' OR column_name LIKE '%_account_id')
GROUP BY table_name
ORDER BY table_name;

-- -----------------------------------------------------------------------------
-- 9. Add Gold field mappings for entity FK columns
-- -----------------------------------------------------------------------------
-- These mappings use _ENTITY_REF expressions to reference entity IDs created
-- during the same Gold processing run.

-- Get max ordinal for pain.001 mappings
WITH max_ord AS (
    SELECT COALESCE(MAX(ordinal), 0) as max_ordinal
    FROM mapping.gold_field_mappings
    WHERE format_id = 'pain.001'
)
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal, is_active)
SELECT * FROM (VALUES
    ('pain.001', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_party_id', '_ENTITY_REF.debtor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 1, true),
    ('pain.001', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_account_id', '_ENTITY_REF.debtor_account_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 2, true),
    ('pain.001', 'cdm_pain_customer_credit_transfer_initiation', 'debtor_agent_id', '_ENTITY_REF.debtor_agent_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 3, true),
    ('pain.001', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_party_id', '_ENTITY_REF.creditor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 4, true),
    ('pain.001', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_account_id', '_ENTITY_REF.creditor_account_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 5, true),
    ('pain.001', 'cdm_pain_customer_credit_transfer_initiation', 'creditor_agent_id', '_ENTITY_REF.creditor_agent_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 6, true),
    ('pain.001', 'cdm_pain_customer_credit_transfer_initiation', 'ultimate_debtor_party_id', '_ENTITY_REF.ultimate_debtor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 7, true),
    ('pain.001', 'cdm_pain_customer_credit_transfer_initiation', 'ultimate_creditor_party_id', '_ENTITY_REF.ultimate_creditor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 8, true),
    ('pain.001', 'cdm_pain_customer_credit_transfer_initiation', 'intermediary_agent1_id', '_ENTITY_REF.intermediary_agent1_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 9, true),
    ('pain.001', 'cdm_pain_customer_credit_transfer_initiation', 'intermediary_agent2_id', '_ENTITY_REF.intermediary_agent2_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 10, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal, is_active)
ON CONFLICT (format_id, gold_table, gold_column, COALESCE(entity_role, '')) DO UPDATE
    SET source_expression = EXCLUDED.source_expression, is_active = true;

-- pacs.008 mappings
WITH max_ord AS (
    SELECT COALESCE(MAX(ordinal), 0) as max_ordinal
    FROM mapping.gold_field_mappings
    WHERE format_id = 'pacs.008'
)
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal, is_active)
SELECT * FROM (VALUES
    ('pacs.008', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_party_id', '_ENTITY_REF.debtor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 1, true),
    ('pacs.008', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_account_id', '_ENTITY_REF.debtor_account_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 2, true),
    ('pacs.008', 'cdm_pacs_fi_customer_credit_transfer', 'debtor_agent_id', '_ENTITY_REF.debtor_agent_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 3, true),
    ('pacs.008', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_party_id', '_ENTITY_REF.creditor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 4, true),
    ('pacs.008', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_account_id', '_ENTITY_REF.creditor_account_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 5, true),
    ('pacs.008', 'cdm_pacs_fi_customer_credit_transfer', 'creditor_agent_id', '_ENTITY_REF.creditor_agent_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 6, true),
    ('pacs.008', 'cdm_pacs_fi_customer_credit_transfer', 'ultimate_debtor_party_id', '_ENTITY_REF.ultimate_debtor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 7, true),
    ('pacs.008', 'cdm_pacs_fi_customer_credit_transfer', 'ultimate_creditor_party_id', '_ENTITY_REF.ultimate_creditor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 8, true),
    ('pacs.008', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent1_id', '_ENTITY_REF.intermediary_agent1_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 9, true),
    ('pacs.008', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent2_id', '_ENTITY_REF.intermediary_agent2_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 10, true),
    ('pacs.008', 'cdm_pacs_fi_customer_credit_transfer', 'intermediary_agent3_id', '_ENTITY_REF.intermediary_agent3_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 11, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal, is_active)
ON CONFLICT (format_id, gold_table, gold_column, COALESCE(entity_role, '')) DO UPDATE
    SET source_expression = EXCLUDED.source_expression, is_active = true;

-- camt.053 mappings
WITH max_ord AS (
    SELECT COALESCE(MAX(ordinal), 0) as max_ordinal
    FROM mapping.gold_field_mappings
    WHERE format_id = 'camt.053'
)
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal, is_active)
SELECT * FROM (VALUES
    ('camt.053', 'cdm_camt_bank_to_customer_statement', 'account_owner_party_id', '_ENTITY_REF.debtor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 1, true),
    ('camt.053', 'cdm_camt_bank_to_customer_statement', 'account_servicer_id', '_ENTITY_REF.debtor_agent_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 2, true),
    ('camt.053', 'cdm_camt_bank_to_customer_statement', 'statement_account_id', '_ENTITY_REF.debtor_account_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 3, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal, is_active)
ON CONFLICT (format_id, gold_table, gold_column, COALESCE(entity_role, '')) DO UPDATE
    SET source_expression = EXCLUDED.source_expression, is_active = true;

-- pacs.009 mappings
WITH max_ord AS (
    SELECT COALESCE(MAX(ordinal), 0) as max_ordinal
    FROM mapping.gold_field_mappings
    WHERE format_id = 'pacs.009'
)
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal, is_active)
SELECT * FROM (VALUES
    ('pacs.009', 'cdm_pacs_fi_credit_transfer', 'debtor_party_id', '_ENTITY_REF.debtor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 1, true),
    ('pacs.009', 'cdm_pacs_fi_credit_transfer', 'debtor_account_id', '_ENTITY_REF.debtor_account_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 2, true),
    ('pacs.009', 'cdm_pacs_fi_credit_transfer', 'debtor_agent_id', '_ENTITY_REF.debtor_agent_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 3, true),
    ('pacs.009', 'cdm_pacs_fi_credit_transfer', 'creditor_party_id', '_ENTITY_REF.creditor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 4, true),
    ('pacs.009', 'cdm_pacs_fi_credit_transfer', 'creditor_account_id', '_ENTITY_REF.creditor_account_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 5, true),
    ('pacs.009', 'cdm_pacs_fi_credit_transfer', 'creditor_agent_id', '_ENTITY_REF.creditor_agent_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 6, true),
    ('pacs.009', 'cdm_pacs_fi_credit_transfer', 'intermediary_agent1_id', '_ENTITY_REF.intermediary_agent1_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 7, true),
    ('pacs.009', 'cdm_pacs_fi_credit_transfer', 'intermediary_agent2_id', '_ENTITY_REF.intermediary_agent2_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 8, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal, is_active)
ON CONFLICT (format_id, gold_table, gold_column, COALESCE(entity_role, '')) DO UPDATE
    SET source_expression = EXCLUDED.source_expression, is_active = true;

-- pacs.002 mappings
WITH max_ord AS (
    SELECT COALESCE(MAX(ordinal), 0) as max_ordinal
    FROM mapping.gold_field_mappings
    WHERE format_id = 'pacs.002'
)
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal, is_active)
SELECT * FROM (VALUES
    ('pacs.002', 'cdm_pacs_fi_payment_status_report', 'debtor_party_id', '_ENTITY_REF.debtor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 1, true),
    ('pacs.002', 'cdm_pacs_fi_payment_status_report', 'debtor_agent_id', '_ENTITY_REF.debtor_agent_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 2, true),
    ('pacs.002', 'cdm_pacs_fi_payment_status_report', 'creditor_party_id', '_ENTITY_REF.creditor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 3, true),
    ('pacs.002', 'cdm_pacs_fi_payment_status_report', 'creditor_agent_id', '_ENTITY_REF.creditor_agent_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 4, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal, is_active)
ON CONFLICT (format_id, gold_table, gold_column, COALESCE(entity_role, '')) DO UPDATE
    SET source_expression = EXCLUDED.source_expression, is_active = true;

-- pacs.004 mappings
WITH max_ord AS (
    SELECT COALESCE(MAX(ordinal), 0) as max_ordinal
    FROM mapping.gold_field_mappings
    WHERE format_id = 'pacs.004'
)
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal, is_active)
SELECT * FROM (VALUES
    ('pacs.004', 'cdm_pacs_payment_return', 'return_debtor_party_id', '_ENTITY_REF.debtor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 1, true),
    ('pacs.004', 'cdm_pacs_payment_return', 'return_debtor_account_id', '_ENTITY_REF.debtor_account_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 2, true),
    ('pacs.004', 'cdm_pacs_payment_return', 'return_debtor_agent_id', '_ENTITY_REF.debtor_agent_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 3, true),
    ('pacs.004', 'cdm_pacs_payment_return', 'return_creditor_party_id', '_ENTITY_REF.creditor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 4, true),
    ('pacs.004', 'cdm_pacs_payment_return', 'return_creditor_account_id', '_ENTITY_REF.creditor_account_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 5, true),
    ('pacs.004', 'cdm_pacs_payment_return', 'return_creditor_agent_id', '_ENTITY_REF.creditor_agent_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 6, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal, is_active)
ON CONFLICT (format_id, gold_table, gold_column, COALESCE(entity_role, '')) DO UPDATE
    SET source_expression = EXCLUDED.source_expression, is_active = true;

-- pain.008 mappings
WITH max_ord AS (
    SELECT COALESCE(MAX(ordinal), 0) as max_ordinal
    FROM mapping.gold_field_mappings
    WHERE format_id = 'pain.008'
)
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal, is_active)
SELECT * FROM (VALUES
    ('pain.008', 'cdm_pain_customer_direct_debit_initiation', 'debtor_party_id', '_ENTITY_REF.debtor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 1, true),
    ('pain.008', 'cdm_pain_customer_direct_debit_initiation', 'debtor_account_id', '_ENTITY_REF.debtor_account_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 2, true),
    ('pain.008', 'cdm_pain_customer_direct_debit_initiation', 'debtor_agent_id', '_ENTITY_REF.debtor_agent_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 3, true),
    ('pain.008', 'cdm_pain_customer_direct_debit_initiation', 'creditor_party_id', '_ENTITY_REF.creditor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 4, true),
    ('pain.008', 'cdm_pain_customer_direct_debit_initiation', 'creditor_account_id', '_ENTITY_REF.creditor_account_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 5, true),
    ('pain.008', 'cdm_pain_customer_direct_debit_initiation', 'creditor_agent_id', '_ENTITY_REF.creditor_agent_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 6, true),
    ('pain.008', 'cdm_pain_customer_direct_debit_initiation', 'ultimate_debtor_party_id', '_ENTITY_REF.ultimate_debtor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 7, true),
    ('pain.008', 'cdm_pain_customer_direct_debit_initiation', 'ultimate_creditor_party_id', '_ENTITY_REF.ultimate_creditor_id', NULL, 'VARCHAR', (SELECT max_ordinal FROM max_ord) + 8, true)
) AS v(format_id, gold_table, gold_column, source_expression, entity_role, data_type, ordinal, is_active)
ON CONFLICT (format_id, gold_table, gold_column, COALESCE(entity_role, '')) DO UPDATE
    SET source_expression = EXCLUDED.source_expression, is_active = true;

-- Verify FK mappings created
SELECT format_id, gold_table, gold_column, source_expression
FROM mapping.gold_field_mappings
WHERE source_expression LIKE '_ENTITY_REF.%'
ORDER BY format_id, gold_table, gold_column;
