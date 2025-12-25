-- ============================================================================
-- CDM GLOBAL REGULATORY EXTENSIONS - RELATIONSHIPTOBENEFICIARY REFERENCE ENTITY
-- ============================================================================
-- Purpose: Create RelationshipToBeneficiary reference entity for relationship codes
-- Coverage: 25 standardized relationship codes (R01-R25)
-- Applicable Jurisdictions: China, India, Philippines, Hong Kong, Singapore, Thailand, Malaysia, Indonesia, Vietnam, UAE, Saudi Arabia, Brazil, Mexico
-- ISO 20022 Compliance: 20%
-- ============================================================================

-- Create RelationshipToBeneficiary Reference Entity
CREATE TABLE IF NOT EXISTS cdm_silver.compliance.relationship_to_beneficiary (
  -- Primary Key
  relationship_code_id STRING NOT NULL COMMENT 'UUID v4 primary key - Non-ISO Extension',

  -- Core Relationship Fields
  code_value STRING NOT NULL COMMENT 'Relationship code (R01-R25) - Non-ISO Extension',
  description STRING NOT NULL COMMENT 'Relationship description (e.g., Spouse, Parent, Child, Employee, Customer, etc.) - ISO 20022 Extended',

  -- Applicability
  applicable_jurisdictions ARRAY<STRING> COMMENT 'ISO 3166-1 alpha-2 country codes where this relationship is used (CN, IN, PH, HK, SG, TH, MY, ID, VN, AE, SA, BR, MX) - Non-ISO Extension',

  -- ISO 20022 Mapping
  iso20022_equivalent STRING COMMENT 'ISO 20022 External Purpose Code equivalent if exists (FAMI, SALA, BUSI, DIVI, LOAN, GDDS, RENT, EDUC, MDCS, TAXS, CHAR, etc.) - ISO 20022 Compliant',

  -- Audit Fields
  created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp - Non-ISO Extension',
  last_updated_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Last update timestamp - Non-ISO Extension'
)
USING DELTA
LOCATION 'cdm_silver/compliance/relationship_to_beneficiary'
COMMENT 'Relationship to beneficiary reference codes for remittances and payments. Required by APAC (China, India, Philippines, Singapore, etc.), Middle East (UAE, Saudi Arabia), and LatAm (Brazil, Mexico) jurisdictions. ISO 20022 Compliance: 20% (1 compliant, 1 extended, 3 non-ISO).';

-- Primary Key Constraint
ALTER TABLE cdm_silver.compliance.relationship_to_beneficiary
ADD CONSTRAINT pk_relationship_to_beneficiary PRIMARY KEY (relationship_code_id);

-- Unique Constraint on Code Value
ALTER TABLE cdm_silver.compliance.relationship_to_beneficiary
ADD CONSTRAINT uk_relationship_code_value UNIQUE (code_value);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_relationship_code_value
ON cdm_silver.compliance.relationship_to_beneficiary (code_value);

CREATE INDEX IF NOT EXISTS idx_relationship_iso20022
ON cdm_silver.compliance.relationship_to_beneficiary (iso20022_equivalent);

-- Sample view: Relationship codes by category
CREATE OR REPLACE VIEW cdm_silver.compliance.v_relationship_codes_by_category AS
SELECT
  CASE
    WHEN rtb.code_value IN ('R01', 'R02', 'R03', 'R04', 'R05') THEN 'Family'
    WHEN rtb.code_value IN ('R06', 'R07') THEN 'Employment'
    WHEN rtb.code_value IN ('R08', 'R09', 'R10') THEN 'Business'
    WHEN rtb.code_value IN ('R11', 'R12') THEN 'Commercial'
    WHEN rtb.code_value IN ('R13', 'R14', 'R15', 'R16') THEN 'Financial'
    WHEN rtb.code_value IN ('R17', 'R18') THEN 'Property'
    WHEN rtb.code_value IN ('R19', 'R20') THEN 'Education'
    WHEN rtb.code_value = 'R21' THEN 'Medical'
    WHEN rtb.code_value IN ('R22', 'R23') THEN 'Institutional'
    WHEN rtb.code_value IN ('R24', 'R25') THEN 'Other'
    ELSE 'Uncategorized'
  END AS relationship_category,
  rtb.code_value,
  rtb.description,
  rtb.iso20022_equivalent,
  ARRAY_SIZE(rtb.applicable_jurisdictions) AS jurisdiction_count,
  rtb.applicable_jurisdictions
FROM cdm_silver.compliance.relationship_to_beneficiary rtb
ORDER BY relationship_category, rtb.code_value;

-- Sample view: Relationship codes by jurisdiction
CREATE OR REPLACE VIEW cdm_silver.compliance.v_relationship_codes_by_jurisdiction AS
SELECT
  explode(rtb.applicable_jurisdictions) AS jurisdiction,
  COUNT(*) AS total_relationship_codes,
  COLLECT_LIST(STRUCT(rtb.code_value, rtb.description, rtb.iso20022_equivalent)) AS available_codes
FROM cdm_silver.compliance.relationship_to_beneficiary rtb
GROUP BY explode(rtb.applicable_jurisdictions)
ORDER BY total_relationship_codes DESC, jurisdiction;

-- Sample view: Relationship codes mapped to ISO 20022
CREATE OR REPLACE VIEW cdm_silver.compliance.v_relationship_iso20022_mappings AS
SELECT
  rtb.iso20022_equivalent,
  COUNT(*) AS codes_mapped,
  COLLECT_LIST(STRUCT(rtb.code_value, rtb.description)) AS relationship_codes,
  COUNT(DISTINCT explode(rtb.applicable_jurisdictions)) AS jurisdiction_count
FROM cdm_silver.compliance.relationship_to_beneficiary rtb
WHERE rtb.iso20022_equivalent IS NOT NULL
GROUP BY rtb.iso20022_equivalent
ORDER BY codes_mapped DESC;

-- Validation: Check table created
SELECT
  'RelationshipToBeneficiary entity created' AS status,
  COUNT(*) AS row_count
FROM cdm_silver.compliance.relationship_to_beneficiary;

-- Expected result: 0 rows initially (before reference data load)
