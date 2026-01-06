-- =============================================================================
-- Migration: Fix _batch_id max_length in Silver Field Mappings
-- =============================================================================
-- Issue: Some silver_field_mappings had max_length = 35 for _batch_id column,
-- but UUIDs are 36 characters. This caused batch_id truncation and broke
-- Bronze → Silver → Gold linkage queries.
--
-- Date: 2026-01-06
-- =============================================================================

-- Fix max_length for _batch_id to 36 (UUID length)
UPDATE mapping.silver_field_mappings
SET max_length = 36
WHERE target_column = '_batch_id'
  AND (max_length IS NULL OR max_length < 36);

-- Also fix any truncated batch_ids in Silver tables
-- (Run this separately for each affected Silver table)

-- Fix truncated batch_ids by matching with Bronze records
DO $$
DECLARE
    tbl TEXT;
    fix_count INT;
BEGIN
    FOR tbl IN
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'silver' AND table_name LIKE 'stg_%'
    LOOP
        EXECUTE format('
            UPDATE silver.%I s
            SET _batch_id = b._batch_id
            FROM bronze.raw_payment_messages b
            WHERE b._batch_id LIKE s._batch_id || ''%%''
              AND LENGTH(s._batch_id) = 35
              AND LENGTH(b._batch_id) = 36
              AND s._batch_id ~ ''^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{11}$''
        ', tbl);
        GET DIAGNOSTICS fix_count = ROW_COUNT;
        IF fix_count > 0 THEN
            RAISE NOTICE 'Fixed % truncated batch_ids in %', fix_count, tbl;
        END IF;
    END LOOP;
END $$;

-- Fix truncated lineage_batch_id in Gold payment instructions
DO $$
DECLARE
    tbl TEXT;
    fix_count INT;
BEGIN
    FOR tbl IN
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'silver' AND table_name LIKE 'stg_%'
    LOOP
        EXECUTE format('
            UPDATE gold.cdm_payment_instruction g
            SET lineage_batch_id = s._batch_id
            FROM silver.%I s
            WHERE g.source_stg_id = s.stg_id
              AND LENGTH(g.lineage_batch_id) = 35
              AND LENGTH(s._batch_id) = 36
        ', tbl);
        GET DIAGNOSTICS fix_count = ROW_COUNT;
        IF fix_count > 0 THEN
            RAISE NOTICE 'Fixed % truncated lineage_batch_ids from %', fix_count, tbl;
        END IF;
    END LOOP;
END $$;
