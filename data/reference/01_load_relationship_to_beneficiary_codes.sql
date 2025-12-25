-- =====================================================================
-- Script: Load RelationshipToBeneficiary Reference Data
-- Purpose: Populate 25 standardized relationship codes (R01-R25)
-- Jurisdiction Coverage: 13 APAC/Middle East/LatAm jurisdictions
-- =====================================================================

-- Drop and recreate table if needed for clean load
-- DROP TABLE IF EXISTS cdm_silver.relationship_to_beneficiary;

-- Insert 25 relationship codes
INSERT INTO cdm_silver.relationship_to_beneficiary
(relationship_code_id, code_value, description, applicable_jurisdictions, iso20022_equivalent, category, created_timestamp, last_updated_timestamp)
VALUES

-- =============================
-- FAMILY RELATIONSHIPS (R01-R09)
-- =============================
(
  uuid(),
  'R01',
  'Spouse',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'FAMI',
  'Family',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R02',
  'Parent',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'FAMI',
  'Family',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R03',
  'Child',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'FAMI',
  'Family',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R04',
  'Sibling',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'FAMI',
  'Family',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R05',
  'Grandparent',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'BR', 'MX'),
  'FAMI',
  'Family',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R06',
  'Grandchild',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'BR', 'MX'),
  'FAMI',
  'Family',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R07',
  'Other relative',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'FAMI',
  'Family',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R08',
  'Dependent',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'BR', 'MX'),
  'FAMI',
  'Family',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R09',
  'Family support',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'FAMI',
  'Family',
  current_timestamp(),
  current_timestamp()
),

-- =============================
-- EMPLOYMENT (R10)
-- =============================
(
  uuid(),
  'R10',
  'Employee (salary payment)',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'SALA',
  'Employment',
  current_timestamp(),
  current_timestamp()
),

-- =============================
-- COMMERCIAL (R11-R15)
-- =============================
(
  uuid(),
  'R11',
  'Customer (payment for goods/services purchased)',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'GDDS',
  'Commercial',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R12',
  'Supplier/Vendor (payment for goods/services rendered)',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'GDDS',
  'Commercial',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R13',
  'Business partner',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'BUSI',
  'Business',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R14',
  'Shareholder/Investor (dividend payment)',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'DIVI',
  'Financial',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R15',
  'Debtor/Borrower (loan repayment)',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'LOAN',
  'Financial',
  current_timestamp(),
  current_timestamp()
),

-- =============================
-- PROPERTY (R16-R17)
-- =============================
(
  uuid(),
  'R16',
  'Landlord (rent payment)',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'RENT',
  'Property',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R17',
  'Tenant (rent receipt)',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'RENT',
  'Property',
  current_timestamp(),
  current_timestamp()
),

-- =============================
-- INSTITUTIONAL (R18-R22)
-- =============================
(
  uuid(),
  'R18',
  'Educational institution (tuition)',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'EDUC',
  'Educational',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R19',
  'Student (tuition payment)',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'EDUC',
  'Educational',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R20',
  'Medical service provider (hospital/clinic)',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'MDCS',
  'Medical',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R21',
  'Government authority (tax/fee payment)',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'TAXS',
  'Institutional',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R22',
  'Charity/Non-profit organization',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  'CHAR',
  'Institutional',
  current_timestamp(),
  current_timestamp()
),

-- =============================
-- OTHER (R23-R25)
-- =============================
(
  uuid(),
  'R23',
  'Friend',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  NULL,
  'Other',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R24',
  'Self (own account transfer)',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  NULL,
  'Other',
  current_timestamp(),
  current_timestamp()
),

(
  uuid(),
  'R25',
  'Other (specify in additional details)',
  array('CN', 'IN', 'PH', 'HK', 'SG', 'TH', 'MY', 'ID', 'VN', 'AE', 'SA', 'BR', 'MX'),
  NULL,
  'Other',
  current_timestamp(),
  current_timestamp()
);

-- =====================================================================
-- Validation Queries
-- =====================================================================

-- Count total codes
SELECT COUNT(*) as total_codes FROM cdm_silver.relationship_to_beneficiary;
-- Expected: 25

-- Count by category
SELECT category, COUNT(*) as code_count
FROM cdm_silver.relationship_to_beneficiary
GROUP BY category
ORDER BY category;

-- Verify pattern compliance (R01-R25)
SELECT code_value, description
FROM cdm_silver.relationship_to_beneficiary
WHERE code_value NOT REGEXP '^R(0[1-9]|1[0-9]|2[0-5])$';
-- Expected: 0 rows (all should match pattern)

-- Check ISO 20022 mapping coverage
SELECT
  category,
  COUNT(*) as total_codes,
  SUM(CASE WHEN iso20022_equivalent IS NOT NULL THEN 1 ELSE 0 END) as mapped_codes,
  ROUND(100.0 * SUM(CASE WHEN iso20022_equivalent IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) as mapping_pct
FROM cdm_silver.relationship_to_beneficiary
GROUP BY category
ORDER BY category;

-- Sample data verification
SELECT
  code_value,
  description,
  iso20022_equivalent,
  category,
  CARDINALITY(applicable_jurisdictions) as jurisdiction_count
FROM cdm_silver.relationship_to_beneficiary
ORDER BY code_value;
