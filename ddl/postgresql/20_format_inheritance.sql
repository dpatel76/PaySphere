-- =============================================================================
-- GPS CDM - ISO 20022 Format Inheritance Schema
-- =============================================================================
-- This schema enables mapping inheritance based on ISO 20022 message hierarchy.
-- Payment systems (FEDWIRE, CHIPS, CHAPS, etc.) inherit from base ISO 20022
-- message types (pacs.008, pacs.009, pain.001, camt.053).
--
-- Benefits:
-- 1. Eliminates redundant mappings for ISO 20022-compliant systems
-- 2. Ensures consistent mapping updates across related formats
-- 3. Tracks which systems use which ISO 20022 message types
-- 4. Supports partial inheritance for systems with custom extensions
--
-- Inheritance Model:
--   pacs.008 (FI to FI Customer Credit Transfer)
--     └── FEDWIRE, CHIPS, CHAPS, FPS, FEDNOW, RTP, NPP, MEPS_PLUS, UAEFTS, RTGS_HK
--   pacs.009 (FI Credit Transfer - bank to bank)
--     └── TARGET2, CHIPS (cover payments)
--   pain.001 (Customer Credit Transfer Initiation)
--     └── SEPA
--   camt.053 (Bank to Customer Account Statement)
--     └── All statement implementations
-- =============================================================================

-- =============================================================================
-- Format Inheritance Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS mapping.format_inheritance (
    inheritance_id SERIAL PRIMARY KEY,

    -- Child format (the system-specific format, e.g., FEDWIRE)
    child_format_id VARCHAR(50) NOT NULL REFERENCES mapping.message_formats(format_id),

    -- Parent format (the base ISO 20022 message type, e.g., pacs.008)
    parent_format_id VARCHAR(50) NOT NULL REFERENCES mapping.message_formats(format_id),

    -- Inheritance type:
    -- COMPLETE: Child inherits all parent mappings (no overrides needed)
    -- PARTIAL: Child inherits parent mappings but has system-specific overrides
    -- EXTENSION: Child extends parent with additional fields only
    inheritance_type VARCHAR(20) NOT NULL
        CHECK (inheritance_type IN ('COMPLETE', 'PARTIAL', 'EXTENSION')),

    -- Priority for multiple inheritance (lower = higher priority)
    priority INTEGER DEFAULT 0,

    -- Description of the inheritance relationship
    description TEXT,

    -- Usage Guidelines Reference (URL to official documentation)
    usage_guidelines_url TEXT,

    -- ISO 20022 Version Information
    iso_version VARCHAR(30),          -- e.g., 'pacs.008.001.08'
    adopted_since DATE,               -- When the system adopted ISO 20022
    migration_status VARCHAR(20)      -- COMPLETED, IN_PROGRESS, PLANNED
        CHECK (migration_status IN ('COMPLETED', 'IN_PROGRESS', 'PLANNED')),

    -- Tracking
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'SYSTEM',

    UNIQUE(child_format_id, parent_format_id)
);

CREATE INDEX IF NOT EXISTS idx_format_inheritance_child
    ON mapping.format_inheritance(child_format_id) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_format_inheritance_parent
    ON mapping.format_inheritance(parent_format_id) WHERE is_active = TRUE;

COMMENT ON TABLE mapping.format_inheritance IS 'Tracks ISO 20022 inheritance relationships between payment formats';
COMMENT ON COLUMN mapping.format_inheritance.inheritance_type IS 'COMPLETE=full inheritance, PARTIAL=with overrides, EXTENSION=additional fields only';
COMMENT ON COLUMN mapping.format_inheritance.priority IS 'Resolution order for multiple inheritance (lower number = higher priority)';

-- =============================================================================
-- Add Inheritance Tracking to Field Mappings
-- =============================================================================
ALTER TABLE mapping.silver_field_mappings
    ADD COLUMN IF NOT EXISTS is_inherited BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS inherited_from_format VARCHAR(50);

ALTER TABLE mapping.gold_field_mappings
    ADD COLUMN IF NOT EXISTS is_inherited BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS inherited_from_format VARCHAR(50);

COMMENT ON COLUMN mapping.silver_field_mappings.is_inherited IS 'True if this mapping was inherited from a parent format';
COMMENT ON COLUMN mapping.silver_field_mappings.inherited_from_format IS 'Parent format_id this mapping was inherited from';
COMMENT ON COLUMN mapping.gold_field_mappings.is_inherited IS 'True if this mapping was inherited from a parent format';
COMMENT ON COLUMN mapping.gold_field_mappings.inherited_from_format IS 'Parent format_id this mapping was inherited from';

-- =============================================================================
-- Insert Base ISO 20022 Message Types (if not already present)
-- =============================================================================
INSERT INTO mapping.message_formats (format_id, format_name, format_category, country, standard_name, governing_body)
VALUES
    ('pacs.008.base', 'ISO 20022 pacs.008 Base (FI to FI Customer Credit Transfer)', 'ISO20022_BASE', 'GLOBAL', 'ISO 20022', 'ISO TC 68'),
    ('pacs.009.base', 'ISO 20022 pacs.009 Base (FI Credit Transfer)', 'ISO20022_BASE', 'GLOBAL', 'ISO 20022', 'ISO TC 68'),
    ('pain.001.base', 'ISO 20022 pain.001 Base (Customer Credit Transfer Initiation)', 'ISO20022_BASE', 'GLOBAL', 'ISO 20022', 'ISO TC 68'),
    ('camt.053.base', 'ISO 20022 camt.053 Base (Bank to Customer Account Statement)', 'ISO20022_BASE', 'GLOBAL', 'ISO 20022', 'ISO TC 68')
ON CONFLICT (format_id) DO UPDATE SET
    format_name = EXCLUDED.format_name,
    format_category = 'ISO20022_BASE',
    standard_name = 'ISO 20022',
    governing_body = 'ISO TC 68';

-- =============================================================================
-- Register ISO 20022 Inheritance Relationships
-- =============================================================================
-- Systems using pacs.008 (FI to FI Customer Credit Transfer)
INSERT INTO mapping.format_inheritance
    (child_format_id, parent_format_id, inheritance_type, iso_version, adopted_since, migration_status, description)
VALUES
    -- US Payment Systems
    ('FEDWIRE', 'pacs.008.base', 'COMPLETE', 'pacs.008.001.08', '2025-03-10', 'COMPLETED',
     'Fedwire ISO 20022 migration completed March 2025'),
    ('CHIPS', 'pacs.008.base', 'COMPLETE', 'pacs.008.001.08', '2023-11-13', 'COMPLETED',
     'CHIPS ISO 20022 migration completed November 2023'),
    ('FEDNOW', 'pacs.008.base', 'COMPLETE', 'pacs.008.001.08', '2023-07-20', 'COMPLETED',
     'FedNow launched with ISO 20022 native format'),

    -- UK Payment Systems (via Bank of England / Pay.UK)
    ('CHAPS', 'pacs.008.base', 'PARTIAL', 'pacs.008.001.08', '2023-04-01', 'COMPLETED',
     'CHAPS uses BoE ISO 20022 usage guidelines with UK-specific extensions'),
    ('FPS', 'pacs.008.base', 'PARTIAL', 'pacs.008.001.08', '2023-04-01', 'COMPLETED',
     'Faster Payments uses Pay.UK ISO 20022 usage guidelines'),

    -- US Real-Time Payments
    ('RTP', 'pacs.008.base', 'PARTIAL', 'pacs.008.001.08', '2017-11-13', 'COMPLETED',
     'The Clearing House RTP uses TCH ISO 20022 usage guidelines'),

    -- Australia
    ('NPP', 'pacs.008.base', 'COMPLETE', 'pacs.008.001.08', '2018-02-13', 'COMPLETED',
     'NPP Australia uses ISO 20022 native format'),

    -- Singapore
    ('MEPS_PLUS', 'pacs.008.base', 'COMPLETE', 'pacs.008.001.08', '2014-12-08', 'COMPLETED',
     'MAS MEPS+ RTGS uses ISO 20022'),

    -- Hong Kong
    ('RTGS_HK', 'pacs.008.base', 'COMPLETE', 'pacs.008.001.08', '2021-06-01', 'COMPLETED',
     'HKMA RTGS uses ISO 20022'),

    -- UAE
    ('UAEFTS', 'pacs.008.base', 'COMPLETE', 'pacs.008.001.08', '2022-01-01', 'COMPLETED',
     'UAE Central Bank FTS uses ISO 20022'),

    -- Philippines
    ('INSTAPAY', 'pacs.008.base', 'COMPLETE', 'pacs.008.001.08', '2019-04-01', 'COMPLETED',
     'Bangko Sentral InstaPay uses ISO 20022')
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET
    inheritance_type = EXCLUDED.inheritance_type,
    iso_version = EXCLUDED.iso_version,
    adopted_since = EXCLUDED.adopted_since,
    migration_status = EXCLUDED.migration_status,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

-- Systems using pacs.009 (FI Credit Transfer - bank to bank)
INSERT INTO mapping.format_inheritance
    (child_format_id, parent_format_id, inheritance_type, iso_version, adopted_since, migration_status, description)
VALUES
    ('TARGET2', 'pacs.009.base', 'COMPLETE', 'pacs.009.001.08', '2022-11-21', 'COMPLETED',
     'TARGET2/T2 consolidated platform uses pacs.009 for FI transfers')
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET
    inheritance_type = EXCLUDED.inheritance_type,
    iso_version = EXCLUDED.iso_version,
    adopted_since = EXCLUDED.adopted_since,
    migration_status = EXCLUDED.migration_status,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

-- Systems using pain.001 (Customer Credit Transfer Initiation)
INSERT INTO mapping.format_inheritance
    (child_format_id, parent_format_id, inheritance_type, iso_version, adopted_since, migration_status, description)
VALUES
    ('SEPA', 'pain.001.base', 'PARTIAL', 'pain.001.001.09', '2008-01-28', 'COMPLETED',
     'SEPA Credit Transfer uses EPC pain.001 usage guidelines')
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET
    inheritance_type = EXCLUDED.inheritance_type,
    iso_version = EXCLUDED.iso_version,
    adopted_since = EXCLUDED.adopted_since,
    migration_status = EXCLUDED.migration_status,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

-- =============================================================================
-- View: Format Inheritance Hierarchy
-- =============================================================================
-- Shows the complete inheritance hierarchy for all formats
CREATE OR REPLACE VIEW mapping.v_format_inheritance_hierarchy AS
SELECT
    fi.child_format_id AS format_id,
    mf_child.format_name,
    mf_child.format_category,
    fi.parent_format_id AS inherits_from,
    mf_parent.format_name AS parent_format_name,
    fi.inheritance_type,
    fi.iso_version,
    fi.adopted_since,
    fi.migration_status,
    fi.description AS inheritance_notes
FROM mapping.format_inheritance fi
JOIN mapping.message_formats mf_child ON fi.child_format_id = mf_child.format_id
JOIN mapping.message_formats mf_parent ON fi.parent_format_id = mf_parent.format_id
WHERE fi.is_active = TRUE
ORDER BY fi.parent_format_id, fi.child_format_id;

COMMENT ON VIEW mapping.v_format_inheritance_hierarchy IS 'Shows which payment systems inherit from which ISO 20022 base message types';

-- =============================================================================
-- View: Effective Mappings with Inheritance
-- =============================================================================
-- This view resolves inherited mappings, showing the effective mapping for each format
CREATE OR REPLACE VIEW mapping.v_effective_silver_mappings AS
WITH inherited_mappings AS (
    -- Get direct mappings
    SELECT
        sfm.format_id,
        sfm.target_column,
        sfm.source_path,
        sfm.parser_path,
        sfm.default_value,
        sfm.transform_expression,
        sfm.is_required,
        FALSE AS is_inherited,
        sfm.format_id AS effective_from_format
    FROM mapping.silver_field_mappings sfm
    WHERE sfm.is_active = TRUE

    UNION ALL

    -- Get inherited mappings from parent (only for columns not already defined)
    SELECT
        fi.child_format_id AS format_id,
        sfm.target_column,
        sfm.source_path,
        sfm.parser_path,
        sfm.default_value,
        sfm.transform_expression,
        sfm.is_required,
        TRUE AS is_inherited,
        fi.parent_format_id AS effective_from_format
    FROM mapping.format_inheritance fi
    JOIN mapping.silver_field_mappings sfm ON sfm.format_id = fi.parent_format_id
    WHERE fi.is_active = TRUE
      AND sfm.is_active = TRUE
      AND NOT EXISTS (
          -- Don't inherit if child has its own mapping for this column
          SELECT 1 FROM mapping.silver_field_mappings child_sfm
          WHERE child_sfm.format_id = fi.child_format_id
            AND child_sfm.target_column = sfm.target_column
            AND child_sfm.is_active = TRUE
      )
)
SELECT DISTINCT ON (format_id, target_column)
    format_id,
    target_column,
    source_path,
    parser_path,
    default_value,
    transform_expression,
    is_required,
    is_inherited,
    effective_from_format
FROM inherited_mappings
ORDER BY format_id, target_column, is_inherited ASC;  -- Prefer direct mappings

COMMENT ON VIEW mapping.v_effective_silver_mappings IS 'Resolved Silver mappings with inheritance - shows effective mapping source';

-- =============================================================================
-- View: Effective Gold Mappings with Inheritance
-- =============================================================================
CREATE OR REPLACE VIEW mapping.v_effective_gold_mappings AS
WITH inherited_mappings AS (
    -- Get direct mappings
    SELECT
        gfm.format_id,
        gfm.gold_table,
        gfm.gold_column,
        gfm.source_expression,
        gfm.entity_role,
        gfm.transform_expression,
        gfm.default_value,
        FALSE AS is_inherited,
        gfm.format_id AS effective_from_format
    FROM mapping.gold_field_mappings gfm
    WHERE gfm.is_active = TRUE

    UNION ALL

    -- Get inherited mappings from parent
    SELECT
        fi.child_format_id AS format_id,
        gfm.gold_table,
        gfm.gold_column,
        gfm.source_expression,
        gfm.entity_role,
        gfm.transform_expression,
        gfm.default_value,
        TRUE AS is_inherited,
        fi.parent_format_id AS effective_from_format
    FROM mapping.format_inheritance fi
    JOIN mapping.gold_field_mappings gfm ON gfm.format_id = fi.parent_format_id
    WHERE fi.is_active = TRUE
      AND gfm.is_active = TRUE
      AND NOT EXISTS (
          -- Don't inherit if child has its own mapping
          SELECT 1 FROM mapping.gold_field_mappings child_gfm
          WHERE child_gfm.format_id = fi.child_format_id
            AND child_gfm.gold_table = gfm.gold_table
            AND child_gfm.gold_column = gfm.gold_column
            AND COALESCE(child_gfm.entity_role, '') = COALESCE(gfm.entity_role, '')
            AND child_gfm.is_active = TRUE
      )
)
SELECT DISTINCT ON (format_id, gold_table, gold_column, entity_role)
    format_id,
    gold_table,
    gold_column,
    source_expression,
    entity_role,
    transform_expression,
    default_value,
    is_inherited,
    effective_from_format
FROM inherited_mappings
ORDER BY format_id, gold_table, gold_column, entity_role, is_inherited ASC;

COMMENT ON VIEW mapping.v_effective_gold_mappings IS 'Resolved Gold mappings with inheritance - shows effective mapping source';

-- =============================================================================
-- View: ISO 20022 Adoption Status
-- =============================================================================
CREATE OR REPLACE VIEW mapping.v_iso20022_adoption_status AS
SELECT
    mf.format_id,
    mf.format_name,
    mf.format_category,
    mf.country,
    COALESCE(fi.parent_format_id, 'NONE') AS iso20022_base,
    fi.iso_version,
    fi.inheritance_type,
    fi.adopted_since,
    fi.migration_status,
    CASE
        WHEN fi.inheritance_id IS NOT NULL THEN 'ISO 20022 Compliant'
        WHEN mf.format_category = 'ISO20022' THEN 'ISO 20022 Native'
        WHEN mf.format_category = 'ISO20022_BASE' THEN 'ISO 20022 Base Type'
        ELSE 'Non-ISO 20022'
    END AS compliance_status
FROM mapping.message_formats mf
LEFT JOIN mapping.format_inheritance fi ON mf.format_id = fi.child_format_id AND fi.is_active = TRUE
WHERE mf.is_active = TRUE
ORDER BY
    CASE
        WHEN fi.inheritance_id IS NOT NULL THEN 1
        WHEN mf.format_category LIKE 'ISO20022%' THEN 2
        ELSE 3
    END,
    mf.format_id;

COMMENT ON VIEW mapping.v_iso20022_adoption_status IS 'Shows ISO 20022 adoption status for all payment formats';

-- =============================================================================
-- Function: Get Effective Mappings for Format
-- =============================================================================
-- This function returns all effective Silver mappings for a format,
-- including inherited mappings from parent formats.
CREATE OR REPLACE FUNCTION mapping.get_effective_silver_mappings(p_format_id VARCHAR)
RETURNS TABLE (
    target_column VARCHAR,
    source_path VARCHAR,
    parser_path VARCHAR,
    default_value VARCHAR,
    transform_expression VARCHAR,
    is_required BOOLEAN,
    is_inherited BOOLEAN,
    from_format VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        vm.target_column::VARCHAR,
        vm.source_path::VARCHAR,
        vm.parser_path::VARCHAR,
        vm.default_value::VARCHAR,
        vm.transform_expression::VARCHAR,
        vm.is_required,
        vm.is_inherited,
        vm.effective_from_format::VARCHAR AS from_format
    FROM mapping.v_effective_silver_mappings vm
    WHERE vm.format_id = p_format_id;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION mapping.get_effective_silver_mappings(VARCHAR) IS 'Returns all effective Silver mappings for a format including inherited mappings';

-- =============================================================================
-- Function: Get Effective Gold Mappings for Format
-- =============================================================================
CREATE OR REPLACE FUNCTION mapping.get_effective_gold_mappings(p_format_id VARCHAR)
RETURNS TABLE (
    gold_table VARCHAR,
    gold_column VARCHAR,
    source_expression VARCHAR,
    entity_role VARCHAR,
    transform_expression VARCHAR,
    default_value VARCHAR,
    is_inherited BOOLEAN,
    from_format VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        vm.gold_table::VARCHAR,
        vm.gold_column::VARCHAR,
        vm.source_expression::VARCHAR,
        vm.entity_role::VARCHAR,
        vm.transform_expression::VARCHAR,
        vm.default_value::VARCHAR,
        vm.is_inherited,
        vm.effective_from_format::VARCHAR AS from_format
    FROM mapping.v_effective_gold_mappings vm
    WHERE vm.format_id = p_format_id;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION mapping.get_effective_gold_mappings(VARCHAR) IS 'Returns all effective Gold mappings for a format including inherited mappings';

-- =============================================================================
-- Summary Query: Inheritance Statistics
-- =============================================================================
-- Run this to see inheritance statistics after setup
DO $$
BEGIN
    RAISE NOTICE 'ISO 20022 Format Inheritance Setup Complete';
    RAISE NOTICE '==========================================';
END $$;

SELECT
    parent_format_id,
    COUNT(*) AS child_formats,
    STRING_AGG(child_format_id, ', ' ORDER BY child_format_id) AS formats
FROM mapping.format_inheritance
WHERE is_active = TRUE
GROUP BY parent_format_id
ORDER BY parent_format_id;
