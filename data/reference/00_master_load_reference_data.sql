-- =====================================================================
-- Master Reference Data Loading Script
-- Purpose: Orchestrate loading of all regulatory reference data
-- =====================================================================
-- Execution Order:
--   1. Relationship to Beneficiary codes (25 codes)
--   2. China Purpose Codes (190 codes)
--   3. India Purpose Codes (80 codes)
--   4. Brazil Purpose Codes (40 codes)
--   5. Other Jurisdictions Purpose Codes (50+ codes)
-- Total Expected: 25 relationship codes + 360+ purpose codes
-- =====================================================================

-- =====================================================================
-- STEP 0: Pre-flight Checks
-- =====================================================================

-- Check if tables exist
SHOW TABLES IN cdm_silver LIKE 'relationship_to_beneficiary';
SHOW TABLES IN cdm_silver LIKE 'regulatory_purpose_code';

-- Backup existing data (if tables have data)
CREATE TABLE IF NOT EXISTS cdm_silver.relationship_to_beneficiary_backup_20241218
AS SELECT * FROM cdm_silver.relationship_to_beneficiary;

CREATE TABLE IF NOT EXISTS cdm_silver.regulatory_purpose_code_backup_20241218
AS SELECT * FROM cdm_silver.regulatory_purpose_code;

-- =====================================================================
-- STEP 1: Truncate Tables (Clean Load)
-- =====================================================================

-- WARNING: This will delete all existing reference data
-- Comment out if you want to append instead of replace

TRUNCATE TABLE cdm_silver.relationship_to_beneficiary;
TRUNCATE TABLE cdm_silver.regulatory_purpose_code;

-- =====================================================================
-- STEP 2: Load Relationship to Beneficiary Codes
-- =====================================================================

-- Execute: 01_load_relationship_to_beneficiary_codes.sql
-- This will load 25 codes (R01-R25)
!source /Users/dineshpatel/code/projects/gps_cdm/data/reference/01_load_relationship_to_beneficiary_codes.sql

-- Verify count
SELECT 'Relationship Codes Loaded' as status, COUNT(*) as count
FROM cdm_silver.relationship_to_beneficiary;
-- Expected: 25

-- =====================================================================
-- STEP 3: Load China Purpose Codes
-- =====================================================================

-- Execute: 02_load_regulatory_purpose_codes_china.sql
-- This will load 100+ codes (Part 1 of 190 total)
!source /Users/dineshpatel/code/projects/gps_cdm/data/reference/02_load_regulatory_purpose_codes_china.sql

-- Verify count
SELECT 'China Purpose Codes Loaded' as status, COUNT(*) as count
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction = 'CN';
-- Expected: 100+ (Part 1)

-- =====================================================================
-- STEP 4: Load India Purpose Codes
-- =====================================================================

-- Execute: 03_load_regulatory_purpose_codes_india.sql
-- This will load 80 codes
!source /Users/dineshpatel/code/projects/gps_cdm/data/reference/03_load_regulatory_purpose_codes_india.sql

-- Verify count
SELECT 'India Purpose Codes Loaded' as status, COUNT(*) as count
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction = 'IN';
-- Expected: 80

-- =====================================================================
-- STEP 5: Load Brazil Purpose Codes
-- =====================================================================

-- Execute: 04_load_regulatory_purpose_codes_brazil.sql
-- This will load 40 codes
!source /Users/dineshpatel/code/projects/gps_cdm/data/reference/04_load_regulatory_purpose_codes_brazil.sql

-- Verify count
SELECT 'Brazil Purpose Codes Loaded' as status, COUNT(*) as count
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction = 'BR';
-- Expected: 40

-- =====================================================================
-- STEP 6: Load Other Jurisdictions Purpose Codes
-- =====================================================================

-- Execute: 05_load_regulatory_purpose_codes_other_jurisdictions.sql
-- This will load 60+ codes for US, UK, SG, HK, TH, MY, PH, ID, VN, AE, SA, MX, AU, EU
!source /Users/dineshpatel/code/projects/gps_cdm/data/reference/05_load_regulatory_purpose_codes_other_jurisdictions.sql

-- Verify counts by jurisdiction
SELECT 'Other Jurisdictions Loaded' as status, COUNT(*) as count
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction IN ('US', 'GB', 'SG', 'HK', 'TH', 'MY', 'PH', 'ID', 'VN', 'AE', 'SA', 'MX', 'AU', 'EU');
-- Expected: 60+

-- =====================================================================
-- STEP 7: Final Validation
-- =====================================================================

-- Total counts
SELECT
  'Total Relationship Codes' as metric,
  COUNT(*) as count
FROM cdm_silver.relationship_to_beneficiary
UNION ALL
SELECT
  'Total Purpose Codes' as metric,
  COUNT(*) as count
FROM cdm_silver.regulatory_purpose_code;

-- Purpose codes by jurisdiction
SELECT
  jurisdiction,
  COUNT(*) as code_count,
  MIN(code_value) as min_code,
  MAX(code_value) as max_code
FROM cdm_silver.regulatory_purpose_code
GROUP BY jurisdiction
ORDER BY code_count DESC;

-- Relationship codes summary
SELECT
  category,
  COUNT(*) as code_count
FROM cdm_silver.relationship_to_beneficiary
GROUP BY category
ORDER BY category;

-- Check for duplicates (should be 0)
SELECT
  'Purpose Code Duplicates' as metric,
  COUNT(*) - COUNT(DISTINCT jurisdiction, code_value) as duplicate_count
FROM cdm_silver.regulatory_purpose_code
UNION ALL
SELECT
  'Relationship Code Duplicates' as metric,
  COUNT(*) - COUNT(DISTINCT code_value) as duplicate_count
FROM cdm_silver.relationship_to_beneficiary;

-- Check for NULLs in required fields
SELECT
  'Purpose Codes with NULL jurisdiction' as issue,
  COUNT(*) as count
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction IS NULL
UNION ALL
SELECT
  'Purpose Codes with NULL code_value' as issue,
  COUNT(*) as count
FROM cdm_silver.regulatory_purpose_code
WHERE code_value IS NULL
UNION ALL
SELECT
  'Relationship Codes with NULL code_value' as issue,
  COUNT(*) as count
FROM cdm_silver.relationship_to_beneficiary
WHERE code_value IS NULL;

-- ISO 20022 mapping coverage
SELECT
  'Purpose Codes with ISO Mapping' as metric,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM cdm_silver.regulatory_purpose_code), 1) as pct
FROM cdm_silver.regulatory_purpose_code
WHERE iso20022_mapping IS NOT NULL
UNION ALL
SELECT
  'Relationship Codes with ISO Equivalent' as metric,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM cdm_silver.relationship_to_beneficiary), 1) as pct
FROM cdm_silver.relationship_to_beneficiary
WHERE iso20022_equivalent IS NOT NULL;

-- Payment type coverage
SELECT
  payment_type,
  COUNT(DISTINCT jurisdiction) as jurisdiction_count,
  COUNT(*) as code_count
FROM cdm_silver.regulatory_purpose_code
LATERAL VIEW explode(applicable_payment_types) exploded AS payment_type
GROUP BY payment_type
ORDER BY code_count DESC;

-- =====================================================================
-- STEP 8: Data Quality Checks
-- =====================================================================

-- Check effective dates
SELECT
  'Future Effective Dates' as check_name,
  COUNT(*) as count
FROM cdm_silver.regulatory_purpose_code
WHERE effective_from > CURRENT_DATE();
-- Expected: Some codes may have future effective dates

-- Check expired codes
SELECT
  'Expired Codes (effective_to in past)' as check_name,
  COUNT(*) as count
FROM cdm_silver.regulatory_purpose_code
WHERE effective_to IS NOT NULL
  AND effective_to < CURRENT_DATE();
-- Expected: Some older codes may be expired

-- Check codes requiring supporting documents
SELECT
  jurisdiction,
  COUNT(*) as total_codes,
  SUM(CASE WHEN requires_supporting_documents = true THEN 1 ELSE 0 END) as requires_docs,
  ROUND(100.0 * SUM(CASE WHEN requires_supporting_documents = true THEN 1 ELSE 0 END) / COUNT(*), 1) as requires_docs_pct
FROM cdm_silver.regulatory_purpose_code
GROUP BY jurisdiction
ORDER BY jurisdiction;

-- =====================================================================
-- STEP 9: Create Summary Report
-- =====================================================================

SELECT '======================================' as report;
SELECT 'REFERENCE DATA LOAD SUMMARY' as report;
SELECT '======================================' as report;

SELECT
  'Load Date' as attribute,
  CURRENT_TIMESTAMP() as value
UNION ALL
SELECT
  'Relationship Codes Loaded' as attribute,
  CAST(COUNT(*) AS STRING) as value
FROM cdm_silver.relationship_to_beneficiary
UNION ALL
SELECT
  'Purpose Codes Loaded' as attribute,
  CAST(COUNT(*) AS STRING) as value
FROM cdm_silver.regulatory_purpose_code
UNION ALL
SELECT
  'Jurisdictions Covered' as attribute,
  CAST(COUNT(DISTINCT jurisdiction) AS STRING) as value
FROM cdm_silver.regulatory_purpose_code
UNION ALL
SELECT
  'ISO 20022 Mapping Coverage' as attribute,
  CONCAT(CAST(ROUND(100.0 * SUM(CASE WHEN iso20022_mapping IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS STRING), '%') as value
FROM cdm_silver.regulatory_purpose_code;

-- =====================================================================
-- STEP 10: Create Indexes for Performance (Optional)
-- =====================================================================

-- Note: Delta Lake uses data skipping instead of traditional indexes
-- OPTIMIZE and ZORDER are recommended for better query performance

OPTIMIZE cdm_silver.relationship_to_beneficiary
ZORDER BY (code_value);

OPTIMIZE cdm_silver.regulatory_purpose_code
ZORDER BY (jurisdiction, code_value);

-- =====================================================================
-- STEP 11: Grant Permissions (Optional)
-- =====================================================================

-- Grant read access to consuming applications
-- GRANT SELECT ON cdm_silver.relationship_to_beneficiary TO ROLE payment_processor;
-- GRANT SELECT ON cdm_silver.regulatory_purpose_code TO ROLE payment_processor;

-- =====================================================================
-- Completion Message
-- =====================================================================

SELECT '======================================' as status;
SELECT 'REFERENCE DATA LOAD COMPLETE' as status;
SELECT '======================================' as status;
SELECT 'Next Steps:' as status;
SELECT '1. Validate data in development environment' as status;
SELECT '2. Run reconciliation against regulatory requirements' as status;
SELECT '3. Deploy to QA environment for testing' as status;
SELECT '4. Integrate with payment validation pipeline' as status;
SELECT '5. Schedule quarterly review for new codes' as status;
SELECT '======================================' as status;
