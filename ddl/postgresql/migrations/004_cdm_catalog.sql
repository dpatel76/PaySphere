-- Migration 004: CDM Catalog
-- Creates the cdm_catalog table for storing business metadata about CDM data elements
-- and a view that joins catalog with legacy format mappings

-- ============================================================================
-- CDM Catalog Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS mapping.cdm_catalog (
    catalog_id SERIAL PRIMARY KEY,

    -- Physical Data Element (PDE) Reference
    pde_table_name VARCHAR(100) NOT NULL,      -- e.g., 'cdm_payment_instruction'
    pde_column_name VARCHAR(100) NOT NULL,     -- e.g., 'amount'
    pde_data_type VARCHAR(100),                -- e.g., 'NUMERIC(18,4)'
    pde_is_nullable BOOLEAN DEFAULT true,

    -- Business Metadata (Editable)
    business_name VARCHAR(200),                -- e.g., 'Instructed Amount'
    business_description TEXT,                 -- Business-friendly description
    data_format VARCHAR(200),                  -- e.g., 'Decimal with 4 decimal places'
    allowed_values JSONB,                      -- Array of {value, description} objects

    -- ISO 20022 Reference (Cross-checked)
    iso_element_name VARCHAR(200),             -- e.g., 'InstructedAmount'
    iso_element_description TEXT,              -- From ISO 20022 spec
    iso_element_path VARCHAR(500),             -- e.g., 'CdtTrfTxInf/Amt/InstdAmt'
    iso_data_type VARCHAR(100),                -- e.g., 'ActiveOrHistoricCurrencyAndAmount'

    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),

    UNIQUE(pde_table_name, pde_column_name)
);

-- Full-text search index for catalog search
CREATE INDEX IF NOT EXISTS idx_cdm_catalog_search ON mapping.cdm_catalog
USING gin(to_tsvector('english',
    COALESCE(business_name, '') || ' ' ||
    COALESCE(business_description, '') || ' ' ||
    COALESCE(pde_column_name, '') || ' ' ||
    COALESCE(iso_element_name, '') || ' ' ||
    COALESCE(iso_element_path, '')
));

-- Index for table-based queries
CREATE INDEX IF NOT EXISTS idx_cdm_catalog_table ON mapping.cdm_catalog(pde_table_name);

-- ============================================================================
-- CDM Catalog View with Legacy Mappings
-- ============================================================================

CREATE OR REPLACE VIEW mapping.v_cdm_catalog_with_mappings AS
SELECT
    c.catalog_id,
    c.pde_table_name,
    c.pde_column_name,
    c.pde_data_type,
    c.pde_is_nullable,
    c.business_name,
    c.business_description,
    c.data_format,
    c.allowed_values,
    c.iso_element_name,
    c.iso_element_description,
    c.iso_element_path,
    c.iso_data_type,
    c.is_active,
    c.updated_at,
    c.updated_by,
    -- Aggregate legacy mappings as JSON array
    COALESCE(
        jsonb_agg(
            DISTINCT jsonb_build_object(
                'format_id', gfm.format_id,
                'source_expression', gfm.source_expression,
                'transform_expression', gfm.transform_expression,
                'entity_role', gfm.entity_role
            )
        ) FILTER (WHERE gfm.format_id IS NOT NULL),
        '[]'::jsonb
    ) AS legacy_mappings,
    -- Count of legacy format mappings
    COUNT(DISTINCT gfm.format_id) AS legacy_mapping_count
FROM mapping.cdm_catalog c
LEFT JOIN mapping.gold_field_mappings gfm
    ON c.pde_table_name = gfm.gold_table
    AND c.pde_column_name = gfm.gold_column
    AND gfm.is_active = true
WHERE c.is_active = true
GROUP BY
    c.catalog_id, c.pde_table_name, c.pde_column_name, c.pde_data_type,
    c.pde_is_nullable, c.business_name, c.business_description, c.data_format,
    c.allowed_values, c.iso_element_name, c.iso_element_description,
    c.iso_element_path, c.iso_data_type, c.is_active, c.updated_at, c.updated_by;

-- ============================================================================
-- CDM Catalog Table Summary View
-- ============================================================================

CREATE OR REPLACE VIEW mapping.v_cdm_catalog_table_summary AS
SELECT
    pde_table_name AS table_name,
    COUNT(*) AS element_count,
    COUNT(*) FILTER (WHERE business_description IS NOT NULL AND business_description <> '') AS documented_count,
    COUNT(*) FILTER (WHERE iso_element_name IS NOT NULL AND iso_element_name <> '') AS iso_mapped_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE business_description IS NOT NULL AND business_description <> '') / COUNT(*), 1) AS documentation_pct
FROM mapping.cdm_catalog
WHERE is_active = true
GROUP BY pde_table_name
ORDER BY pde_table_name;

-- ============================================================================
-- Function to refresh catalog from CDM schema
-- ============================================================================

CREATE OR REPLACE FUNCTION mapping.refresh_cdm_catalog_from_schema()
RETURNS TABLE(inserted_count INT, updated_count INT) AS $$
DECLARE
    v_inserted INT := 0;
    v_updated INT := 0;
BEGIN
    -- Insert new columns from gold schema that don't exist in catalog
    WITH gold_columns AS (
        SELECT
            c.table_name AS pde_table_name,
            c.column_name AS pde_column_name,
            UPPER(c.data_type) ||
                CASE
                    WHEN c.character_maximum_length IS NOT NULL THEN '(' || c.character_maximum_length || ')'
                    WHEN c.numeric_precision IS NOT NULL AND c.numeric_scale IS NOT NULL THEN '(' || c.numeric_precision || ',' || c.numeric_scale || ')'
                    ELSE ''
                END AS pde_data_type,
            c.is_nullable = 'YES' AS pde_is_nullable
        FROM information_schema.columns c
        WHERE c.table_schema = 'gold'
          AND c.table_name LIKE 'cdm_%'
          -- Exclude system columns
          AND c.column_name NOT IN ('created_at', 'updated_at', 'create_date', 'update_date',
                                     '_ingested_at', '_batch_id', '_source_file', 'is_active',
                                     '_processed_at', '_created_at', '_updated_at')
    )
    INSERT INTO mapping.cdm_catalog (pde_table_name, pde_column_name, pde_data_type, pde_is_nullable)
    SELECT gc.pde_table_name, gc.pde_column_name, gc.pde_data_type, gc.pde_is_nullable
    FROM gold_columns gc
    WHERE NOT EXISTS (
        SELECT 1 FROM mapping.cdm_catalog cc
        WHERE cc.pde_table_name = gc.pde_table_name
          AND cc.pde_column_name = gc.pde_column_name
    );

    GET DIAGNOSTICS v_inserted = ROW_COUNT;

    -- Update data types for existing columns if schema changed
    WITH gold_columns AS (
        SELECT
            c.table_name AS pde_table_name,
            c.column_name AS pde_column_name,
            UPPER(c.data_type) ||
                CASE
                    WHEN c.character_maximum_length IS NOT NULL THEN '(' || c.character_maximum_length || ')'
                    WHEN c.numeric_precision IS NOT NULL AND c.numeric_scale IS NOT NULL THEN '(' || c.numeric_precision || ',' || c.numeric_scale || ')'
                    ELSE ''
                END AS pde_data_type,
            c.is_nullable = 'YES' AS pde_is_nullable
        FROM information_schema.columns c
        WHERE c.table_schema = 'gold'
          AND c.table_name LIKE 'cdm_%'
    )
    UPDATE mapping.cdm_catalog cc
    SET pde_data_type = gc.pde_data_type,
        pde_is_nullable = gc.pde_is_nullable,
        updated_at = CURRENT_TIMESTAMP
    FROM gold_columns gc
    WHERE cc.pde_table_name = gc.pde_table_name
      AND cc.pde_column_name = gc.pde_column_name
      AND (cc.pde_data_type IS DISTINCT FROM gc.pde_data_type
           OR cc.pde_is_nullable IS DISTINCT FROM gc.pde_is_nullable);

    GET DIAGNOSTICS v_updated = ROW_COUNT;

    RETURN QUERY SELECT v_inserted, v_updated;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Grant permissions
-- ============================================================================

GRANT SELECT, INSERT, UPDATE ON mapping.cdm_catalog TO gps_cdm_svc;
GRANT USAGE, SELECT ON SEQUENCE mapping.cdm_catalog_catalog_id_seq TO gps_cdm_svc;
GRANT SELECT ON mapping.v_cdm_catalog_with_mappings TO gps_cdm_svc;
GRANT SELECT ON mapping.v_cdm_catalog_table_summary TO gps_cdm_svc;
GRANT EXECUTE ON FUNCTION mapping.refresh_cdm_catalog_from_schema() TO gps_cdm_svc;

COMMENT ON TABLE mapping.cdm_catalog IS 'CDM Data Catalog - stores business metadata for each CDM data element';
COMMENT ON VIEW mapping.v_cdm_catalog_with_mappings IS 'CDM Catalog with aggregated legacy format mappings';
COMMENT ON VIEW mapping.v_cdm_catalog_table_summary IS 'Summary statistics for catalog by CDM table';
COMMENT ON FUNCTION mapping.refresh_cdm_catalog_from_schema() IS 'Populates catalog from gold schema information_schema';
