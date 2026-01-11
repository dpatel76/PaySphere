-- =============================================================================
-- Migration: Normalize Party Identifier Columns (Phase 5)
-- =============================================================================
-- Part of GPS CDM Major Refactoring Plan
--
-- Purpose:
--   1. Migrate party identifiers from cdm_party to cdm_party_identifiers table
--   2. Remove denormalized identifier columns from cdm_party
--   3. Keep BIC, LEI, and address fields in cdm_party for dual-access pattern
--
-- Design Decisions:
--   - BIC and LEI remain in BOTH cdm_party AND cdm_party_identifiers (dual access)
--   - TAX_ID, NATIONAL_ID, etc. move to cdm_party_identifiers only
--   - identification_country and identification_expiry are KEPT (context fields)
--   - tax_id_country is KEPT (country context for tax lookups)
--
-- Date: 2026-01-10
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Migrate existing identifiers to normalized table
-- -----------------------------------------------------------------------------
-- Note: cdm_party_identifiers uses "always INSERT" pattern going forward,
-- but for migration we use ON CONFLICT to avoid duplicates if re-run.

-- Migrate LEI (primary identifier for parties)
INSERT INTO gold.cdm_party_identifiers
    (party_identifier_id, party_id, identifier_type, identifier_value, is_primary,
     source_instruction_id, created_at)
SELECT
    uuid_generate_v4()::text,
    party_id,
    'LEI',
    lei,
    TRUE,
    source_instruction_id,
    created_at
FROM gold.cdm_party
WHERE lei IS NOT NULL
ON CONFLICT (party_id, identifier_type, identifier_value) DO NOTHING;

-- Migrate BIC (also kept in base table for quick lookups)
INSERT INTO gold.cdm_party_identifiers
    (party_identifier_id, party_id, identifier_type, identifier_value, is_primary,
     source_instruction_id, created_at)
SELECT
    uuid_generate_v4()::text,
    party_id,
    'BIC_PARTY',
    bic,
    FALSE,
    source_instruction_id,
    created_at
FROM gold.cdm_party
WHERE bic IS NOT NULL
ON CONFLICT (party_id, identifier_type, identifier_value) DO NOTHING;

-- Migrate TAX_ID (will be removed from base table)
INSERT INTO gold.cdm_party_identifiers
    (party_identifier_id, party_id, identifier_type, identifier_value, is_primary,
     source_instruction_id, created_at)
SELECT
    uuid_generate_v4()::text,
    party_id,
    'TAX_ID',
    tax_id,
    FALSE,
    source_instruction_id,
    created_at
FROM gold.cdm_party
WHERE tax_id IS NOT NULL
ON CONFLICT (party_id, identifier_type, identifier_value) DO NOTHING;

-- Migrate NATIONAL_ID (will be removed from base table)
INSERT INTO gold.cdm_party_identifiers
    (party_identifier_id, party_id, identifier_type, identifier_value, is_primary,
     source_instruction_id, created_at)
SELECT
    uuid_generate_v4()::text,
    party_id,
    'NATIONAL_ID',
    national_id_number,
    FALSE,
    source_instruction_id,
    created_at
FROM gold.cdm_party
WHERE national_id_number IS NOT NULL
ON CONFLICT (party_id, identifier_type, identifier_value) DO NOTHING;

-- Migrate generic identification_number (will be removed from base table)
INSERT INTO gold.cdm_party_identifiers
    (party_identifier_id, party_id, identifier_type, identifier_value, is_primary,
     source_instruction_id, created_at)
SELECT
    uuid_generate_v4()::text,
    party_id,
    COALESCE(identification_type, 'PARTY_PROPRIETARY'),
    identification_number,
    FALSE,
    source_instruction_id,
    created_at
FROM gold.cdm_party
WHERE identification_number IS NOT NULL
ON CONFLICT (party_id, identifier_type, identifier_value) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 2. Remove denormalized columns from cdm_party
-- -----------------------------------------------------------------------------
-- NOTE: These columns are being moved to cdm_party_identifiers
-- KEEP: bic, lei (dual access pattern)
-- KEEP: tax_id_country, identification_country, identification_expiry (context)

ALTER TABLE gold.cdm_party DROP COLUMN IF EXISTS tax_id;
ALTER TABLE gold.cdm_party DROP COLUMN IF EXISTS tax_id_type;
-- KEEP: tax_id_country (country context for tax lookups)

ALTER TABLE gold.cdm_party DROP COLUMN IF EXISTS identification_type;
ALTER TABLE gold.cdm_party DROP COLUMN IF EXISTS identification_number;
-- KEEP: identification_country, identification_expiry (context for any ID)

ALTER TABLE gold.cdm_party DROP COLUMN IF EXISTS national_id_type;
ALTER TABLE gold.cdm_party DROP COLUMN IF EXISTS national_id_number;

-- KEEP in cdm_party:
--   bic, lei (dual access - also in identifier table)
--   ultimate_debtor_bic, ultimate_creditor_bic (party references)
--   All address fields
--   All audit fields

-- -----------------------------------------------------------------------------
-- 3. Migrate FI identifiers to normalized table (for dual access)
-- -----------------------------------------------------------------------------
-- FI identifiers STAY in cdm_financial_institution AND go to identifier table

-- Migrate BIC (also kept in base table)
INSERT INTO gold.cdm_institution_identifiers
    (institution_identifier_id, financial_institution_id, identifier_type, identifier_value, is_primary,
     source_instruction_id, created_at)
SELECT
    uuid_generate_v4()::text,
    fi_id,
    'BIC',
    bic,
    TRUE,
    source_instruction_id,
    created_at
FROM gold.cdm_financial_institution
WHERE bic IS NOT NULL
ON CONFLICT (financial_institution_id, identifier_type, identifier_value) DO NOTHING;

-- Migrate LEI (also kept in base table)
INSERT INTO gold.cdm_institution_identifiers
    (institution_identifier_id, financial_institution_id, identifier_type, identifier_value, is_primary,
     source_instruction_id, created_at)
SELECT
    uuid_generate_v4()::text,
    fi_id,
    'LEI_FI',
    lei,
    FALSE,
    source_instruction_id,
    created_at
FROM gold.cdm_financial_institution
WHERE lei IS NOT NULL
ON CONFLICT (financial_institution_id, identifier_type, identifier_value) DO NOTHING;

-- Migrate national clearing code (also kept in base table)
INSERT INTO gold.cdm_institution_identifiers
    (institution_identifier_id, financial_institution_id, identifier_type, identifier_value, is_primary,
     source_instruction_id, created_at)
SELECT
    uuid_generate_v4()::text,
    fi_id,
    'NATIONAL_CLR_CODE',
    national_clearing_code,
    FALSE,
    source_instruction_id,
    created_at
FROM gold.cdm_financial_institution
WHERE national_clearing_code IS NOT NULL
ON CONFLICT (financial_institution_id, identifier_type, identifier_value) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 4. Migrate Account identifiers to normalized table (for dual access)
-- -----------------------------------------------------------------------------

-- Migrate IBAN (also kept in base table)
INSERT INTO gold.cdm_account_identifiers
    (account_identifier_id, account_id, identifier_type, identifier_value, is_primary,
     source_instruction_id, created_at)
SELECT
    uuid_generate_v4()::text,
    account_id,
    'IBAN',
    iban,
    TRUE,
    source_instruction_id,
    created_at
FROM gold.cdm_account
WHERE iban IS NOT NULL
ON CONFLICT (account_id, identifier_type, identifier_value) DO NOTHING;

-- Migrate account_number (also kept in base table)
INSERT INTO gold.cdm_account_identifiers
    (account_identifier_id, account_id, identifier_type, identifier_value, is_primary,
     source_instruction_id, created_at)
SELECT
    uuid_generate_v4()::text,
    account_id,
    'ACCOUNT_NUM',
    account_number,
    FALSE,
    source_instruction_id,
    created_at
FROM gold.cdm_account
WHERE account_number IS NOT NULL
ON CONFLICT (account_id, identifier_type, identifier_value) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 5. Verification queries
-- -----------------------------------------------------------------------------

-- Count migrated party identifiers
SELECT 'cdm_party_identifiers' as table_name, identifier_type, COUNT(*) as cnt
FROM gold.cdm_party_identifiers
GROUP BY identifier_type
ORDER BY identifier_type;

-- Count migrated FI identifiers
SELECT 'cdm_institution_identifiers' as table_name, identifier_type, COUNT(*) as cnt
FROM gold.cdm_institution_identifiers
GROUP BY identifier_type
ORDER BY identifier_type;

-- Count migrated account identifiers
SELECT 'cdm_account_identifiers' as table_name, identifier_type, COUNT(*) as cnt
FROM gold.cdm_account_identifiers
GROUP BY identifier_type
ORDER BY identifier_type;

-- Verify columns removed from cdm_party
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'gold'
  AND table_name = 'cdm_party'
  AND column_name IN ('tax_id', 'tax_id_type', 'identification_type',
                      'identification_number', 'national_id_type', 'national_id_number');
-- Expected: 0 rows (all removed)

-- Verify columns kept in cdm_party
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'gold'
  AND table_name = 'cdm_party'
  AND column_name IN ('bic', 'lei', 'tax_id_country', 'identification_country',
                      'identification_expiry', 'ultimate_debtor_bic', 'ultimate_creditor_bic');
-- Expected: 7 rows (all kept)

-- -----------------------------------------------------------------------------
-- 6. Deactivate Gold mappings for removed columns
-- -----------------------------------------------------------------------------
-- These mappings targeted columns that have been removed from cdm_party.
-- Identifiers are now routed to identifier tables via _persist_party_identifiers.

UPDATE mapping.gold_field_mappings
SET is_active = FALSE
WHERE gold_table = 'cdm_party'
  AND gold_column IN ('tax_id', 'tax_id_type', 'identification_type',
                      'identification_number', 'national_id_type', 'national_id_number');

-- Verify deactivated mappings
SELECT format_id, gold_column, is_active
FROM mapping.gold_field_mappings
WHERE gold_table = 'cdm_party'
  AND gold_column IN ('tax_id', 'tax_id_type', 'identification_type',
                      'identification_number', 'national_id_type', 'national_id_number');
-- Expected: All rows should have is_active = FALSE
