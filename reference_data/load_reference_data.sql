-- ============================================================================
-- REFERENCE DATA LOADING SCRIPT
-- ============================================================================
-- Purpose: Load regulatory purpose codes and relationship to beneficiary codes
-- Source Files:
--   - regulatory_purpose_codes_sample.csv (75 sample codes)
--   - relationship_to_beneficiary_codes.csv (25 complete codes)
-- ============================================================================

-- ============================================================================
-- 1. LOAD REGULATORY PURPOSE CODES
-- ============================================================================

-- Load from CSV file using Databricks/Spark
COPY INTO cdm_silver.compliance.regulatory_purpose_code
FROM '/Users/dineshpatel/code/projects/gps_cdm/reference_data/regulatory_purpose_codes_sample.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true', 'nullValue' = '')
COPY_OPTIONS ('mergeSchema' = 'true');

-- Verify load
SELECT
  'RegulatoryPurposeCode loaded' AS status,
  COUNT(*) AS total_codes,
  COUNT(DISTINCT jurisdiction) AS jurisdictions_loaded,
  MIN(effective_from) AS earliest_code,
  MAX(effective_from) AS latest_code
FROM cdm_silver.compliance.regulatory_purpose_code;

-- Expected result: ~75 codes loaded from sample file

-- View codes by jurisdiction
SELECT
  jurisdiction,
  COUNT(*) AS code_count,
  COLLECT_LIST(code_value) AS sample_codes
FROM cdm_silver.compliance.regulatory_purpose_code
GROUP BY jurisdiction
ORDER BY code_count DESC;

-- ============================================================================
-- 2. LOAD RELATIONSHIP TO BENEFICIARY CODES
-- ============================================================================

-- Load from CSV file
COPY INTO cdm_silver.compliance.relationship_to_beneficiary
FROM '/Users/dineshpatel/code/projects/gps_cdm/reference_data/relationship_to_beneficiary_codes.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true', 'nullValue' = '')
COPY_OPTIONS ('mergeSchema' = 'true');

-- Verify load
SELECT
  'RelationshipToBeneficiary loaded' AS status,
  COUNT(*) AS total_codes
FROM cdm_silver.compliance.relationship_to_beneficiary;

-- Expected result: 25 codes loaded

-- View all relationship codes
SELECT
  code_value,
  description,
  iso20022_equivalent,
  ARRAY_SIZE(applicable_jurisdictions) AS jurisdiction_count,
  applicable_jurisdictions
FROM cdm_silver.compliance.relationship_to_beneficiary
ORDER BY code_value;

-- ============================================================================
-- 3. VALIDATION QUERIES
-- ============================================================================

-- Check for data quality issues in RegulatoryPurposeCode
SELECT
  'Data Quality Check - RegulatoryPurposeCode' AS check_name,
  COUNT(*) AS total_codes,
  SUM(CASE WHEN purpose_code_id IS NULL THEN 1 ELSE 0 END) AS missing_id,
  SUM(CASE WHEN jurisdiction IS NULL THEN 1 ELSE 0 END) AS missing_jurisdiction,
  SUM(CASE WHEN code_value IS NULL THEN 1 ELSE 0 END) AS missing_code_value,
  SUM(CASE WHEN code_description IS NULL THEN 1 ELSE 0 END) AS missing_description,
  SUM(CASE WHEN effective_from IS NULL THEN 1 ELSE 0 END) AS missing_effective_date
FROM cdm_silver.compliance.regulatory_purpose_code;

-- Expected: All missing counts should be 0

-- Check for data quality issues in RelationshipToBeneficiary
SELECT
  'Data Quality Check - RelationshipToBeneficiary' AS check_name,
  COUNT(*) AS total_codes,
  SUM(CASE WHEN relationship_code_id IS NULL THEN 1 ELSE 0 END) AS missing_id,
  SUM(CASE WHEN code_value IS NULL THEN 1 ELSE 0 END) AS missing_code_value,
  SUM(CASE WHEN description IS NULL THEN 1 ELSE 0 END) AS missing_description
FROM cdm_silver.compliance.relationship_to_beneficiary;

-- Expected: All missing counts should be 0

-- Check ISO 20022 mapping coverage
SELECT
  'ISO 20022 Mapping Coverage' AS metric,
  COUNT(*) AS total_purpose_codes,
  SUM(CASE WHEN iso20022_mapping IS NOT NULL THEN 1 ELSE 0 END) AS codes_with_iso_mapping,
  ROUND(SUM(CASE WHEN iso20022_mapping IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS mapping_percentage
FROM cdm_silver.compliance.regulatory_purpose_code;

SELECT
  'ISO 20022 Mapping Coverage - Relationship' AS metric,
  COUNT(*) AS total_relationship_codes,
  SUM(CASE WHEN iso20022_equivalent IS NOT NULL THEN 1 ELSE 0 END) AS codes_with_iso_mapping,
  ROUND(SUM(CASE WHEN iso20022_equivalent IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS mapping_percentage
FROM cdm_silver.compliance.relationship_to_beneficiary;

-- ============================================================================
-- 4. USAGE EXAMPLES
-- ============================================================================

-- Example 1: Find China trade-related purpose codes
SELECT
  code_value,
  code_description,
  category,
  sub_category,
  iso20022_mapping,
  requires_supporting_documents
FROM cdm_silver.compliance.regulatory_purpose_code
WHERE jurisdiction = 'CN'
  AND category = 'Trade in Goods'
ORDER BY code_value;

-- Example 2: Find India remittance codes
SELECT
  code_value,
  code_description,
  category,
  applicable_payment_types
FROM cdm_silver.compliance.regulatory_purpose_code
WHERE jurisdiction = 'IN'
  AND category = 'Remittances'
ORDER BY code_value;

-- Example 3: Find all family relationship codes
SELECT
  code_value,
  description,
  iso20022_equivalent,
  applicable_jurisdictions
FROM cdm_silver.compliance.relationship_to_beneficiary
WHERE code_value IN ('R01', 'R02', 'R03', 'R04', 'R05')
ORDER BY code_value;

-- Example 4: Find relationship codes applicable to Singapore
SELECT
  code_value,
  description,
  iso20022_equivalent
FROM cdm_silver.compliance.relationship_to_beneficiary
WHERE ARRAY_CONTAINS(applicable_jurisdictions, 'SG')
ORDER BY code_value;

-- Example 5: Cross-reference purpose codes with relationship codes by ISO 20022 mapping
SELECT
  rpc.iso20022_mapping,
  COUNT(DISTINCT rpc.code_value) AS purpose_code_count,
  COUNT(DISTINCT rtb.code_value) AS relationship_code_count,
  COLLECT_LIST(DISTINCT rpc.jurisdiction) AS jurisdictions_with_purpose_codes,
  COLLECT_LIST(DISTINCT rtb.code_value) AS related_relationship_codes
FROM cdm_silver.compliance.regulatory_purpose_code rpc
LEFT JOIN cdm_silver.compliance.relationship_to_beneficiary rtb
  ON rpc.iso20022_mapping = rtb.iso20022_equivalent
WHERE rpc.iso20022_mapping IS NOT NULL
GROUP BY rpc.iso20022_mapping
ORDER BY purpose_code_count DESC;

-- ============================================================================
-- 5. REFERENCE DATA STATISTICS
-- ============================================================================

-- Summary statistics
SELECT
  'Purpose Codes by Category' AS metric_name,
  category,
  COUNT(*) AS code_count,
  COUNT(DISTINCT jurisdiction) AS jurisdictions,
  COLLECT_LIST(DISTINCT jurisdiction) AS jurisdiction_list
FROM cdm_silver.compliance.regulatory_purpose_code
GROUP BY category
ORDER BY code_count DESC;

SELECT
  'Relationship Codes by ISO 20022 Mapping' AS metric_name,
  iso20022_equivalent,
  COUNT(*) AS code_count,
  COLLECT_LIST(code_value) AS codes
FROM cdm_silver.compliance.relationship_to_beneficiary
WHERE iso20022_equivalent IS NOT NULL
GROUP BY iso20022_equivalent
ORDER BY code_count DESC;

-- ============================================================================
-- NOTES:
-- 1. The sample CSV contains 75 purpose codes. The full dataset should contain 350+ codes:
--    - China: 190 codes
--    - India: 80 codes
--    - Brazil: 40 codes
--    - Others: 40+ codes
--
-- 2. The relationship CSV contains all 25 codes (R01-R25) - complete dataset
--
-- 3. For production use, expand the purpose codes CSV to include all codes from
--    regulatory sources (PBoC, RBI, BACEN, etc.)
--
-- 4. Timestamps (created_timestamp, last_updated_timestamp) will be auto-populated
--    with current timestamp on insert
-- ============================================================================
