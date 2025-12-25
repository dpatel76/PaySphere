-- ============================================================================
-- CDM GLOBAL REGULATORY EXTENSIONS - REGULATORYPURPOSECODE REFERENCE ENTITY
-- ============================================================================
-- Purpose: Create RegulatoryPurposeCode reference entity for purpose codes
-- Coverage: 69 jurisdictions (China 190 codes, India 80, others 80+)
-- Total Codes: 350+
-- ISO 20022 Compliance: 40%
-- ============================================================================

-- Create RegulatoryPurposeCode Reference Entity
CREATE TABLE IF NOT EXISTS cdm_silver.compliance.regulatory_purpose_code (
  -- Primary Key
  purpose_code_id STRING NOT NULL COMMENT 'UUID v4 primary key - Non-ISO Extension',

  -- Core Purpose Code Fields
  jurisdiction STRING NOT NULL COMMENT 'ISO 3166-1 alpha-2 country code (CN, IN, BR, KR, etc.) - ISO 20022 Compliant',
  code_value STRING NOT NULL COMMENT 'Jurisdiction-specific purpose code value (e.g., 121010 for China, S0001 for India, 10101 for Brazil) - Non-ISO Extension',
  code_description STRING NOT NULL COMMENT 'Purpose code description (e.g., General merchandise trade - export) - ISO 20022 Compliant',

  -- Categorization
  category STRING COMMENT 'High-level category: Trade in Goods, Trade in Services, Income, Current Transfers, Capital Account, Financial Account, etc. - ISO 20022 Extended',
  sub_category STRING COMMENT 'Sub-category: Export, Import, Processing Trade, General Merchandise, Software, Professional Services, etc. - ISO 20022 Extended',

  -- ISO 20022 Mapping
  iso20022_mapping STRING COMMENT 'ISO 20022 External Purpose Code equivalent (GDDS, SVCS, SALA, DIVI, LOAN, etc.) - ISO 20022 Compliant',

  -- Applicability
  applicable_payment_types ARRAY<STRING> COMMENT 'Payment types where code applies: SWIFT, Wire, RTGS, ACH, Mobile, etc. - Non-ISO Extension',
  requires_supporting_documents BOOLEAN COMMENT 'Documentation requirements flag (true if trade documents, invoices, contracts required) - Non-ISO Extension',

  -- Temporal Validity
  effective_from DATE NOT NULL COMMENT 'Effective start date - ISO 20022 Compliant',
  effective_to DATE COMMENT 'Effective end date (NULL = currently active) - Non-ISO Extension',

  -- Audit Fields
  created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp - Non-ISO Extension',
  last_updated_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Last update timestamp - Non-ISO Extension'
)
USING DELTA
PARTITIONED BY (jurisdiction)
LOCATION 'cdm_silver/compliance/regulatory_purpose_code'
COMMENT 'Regulatory purpose codes for cross-border payments across 69 jurisdictions. Supports China PBoC (190 codes), India RBI (80 codes), Brazil BACEN (40 codes), and other jurisdictions (80+ codes). ISO 20022 Compliance: 40% (4 compliant, 2 extended, 4 non-ISO).';

-- Primary Key Constraint
ALTER TABLE cdm_silver.compliance.regulatory_purpose_code
ADD CONSTRAINT pk_regulatory_purpose_code PRIMARY KEY (purpose_code_id);

-- Unique Constraint on Jurisdiction + Code Value
ALTER TABLE cdm_silver.compliance.regulatory_purpose_code
ADD CONSTRAINT uk_jurisdiction_code_value UNIQUE (jurisdiction, code_value, effective_from);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_purpose_code_jurisdiction_code
ON cdm_silver.compliance.regulatory_purpose_code (jurisdiction, code_value);

CREATE INDEX IF NOT EXISTS idx_purpose_code_category
ON cdm_silver.compliance.regulatory_purpose_code (category, sub_category);

CREATE INDEX IF NOT EXISTS idx_purpose_code_iso20022
ON cdm_silver.compliance.regulatory_purpose_code (iso20022_mapping);

CREATE INDEX IF NOT EXISTS idx_purpose_code_effective
ON cdm_silver.compliance.regulatory_purpose_code (effective_from, effective_to);

-- Sample view: Active purpose codes by jurisdiction
CREATE OR REPLACE VIEW cdm_silver.compliance.v_active_purpose_codes AS
SELECT
  rpc.jurisdiction,
  COUNT(*) AS total_codes,
  COUNT(DISTINCT rpc.category) AS total_categories,
  COUNT(DISTINCT rpc.iso20022_mapping) AS distinct_iso_mappings,
  MIN(rpc.effective_from) AS earliest_effective_date,
  MAX(rpc.effective_from) AS latest_effective_date,
  SUM(CASE WHEN rpc.requires_supporting_documents = true THEN 1 ELSE 0 END) AS codes_requiring_documents
FROM cdm_silver.compliance.regulatory_purpose_code rpc
WHERE rpc.effective_to IS NULL OR rpc.effective_to > CURRENT_DATE
GROUP BY rpc.jurisdiction
ORDER BY total_codes DESC;

-- Sample view: Purpose code mappings to ISO 20022
CREATE OR REPLACE VIEW cdm_silver.compliance.v_purpose_code_iso_mappings AS
SELECT
  rpc.iso20022_mapping,
  COUNT(DISTINCT rpc.jurisdiction) AS jurisdictions_using,
  COUNT(*) AS total_codes,
  COLLECT_LIST(DISTINCT rpc.jurisdiction) AS applicable_jurisdictions,
  COLLECT_LIST(STRUCT(rpc.jurisdiction, rpc.code_value, rpc.code_description)) AS sample_codes
FROM cdm_silver.compliance.regulatory_purpose_code rpc
WHERE rpc.effective_to IS NULL OR rpc.effective_to > CURRENT_DATE
  AND rpc.iso20022_mapping IS NOT NULL
GROUP BY rpc.iso20022_mapping
ORDER BY jurisdictions_using DESC, total_codes DESC;

-- Sample view: Trade-related purpose codes
CREATE OR REPLACE VIEW cdm_silver.compliance.v_trade_purpose_codes AS
SELECT
  rpc.jurisdiction,
  rpc.code_value,
  rpc.code_description,
  rpc.category,
  rpc.sub_category,
  rpc.iso20022_mapping,
  rpc.requires_supporting_documents,
  rpc.applicable_payment_types
FROM cdm_silver.compliance.regulatory_purpose_code rpc
WHERE (rpc.category LIKE '%Trade%' OR rpc.iso20022_mapping IN ('GDDS', 'SVCS'))
  AND (rpc.effective_to IS NULL OR rpc.effective_to > CURRENT_DATE)
ORDER BY rpc.jurisdiction, rpc.code_value;

-- Validation: Check table created
SELECT
  'RegulatoryPurposeCode entity created' AS status,
  COUNT(*) AS row_count
FROM cdm_silver.compliance.regulatory_purpose_code;

-- Expected result: 0 rows initially (before reference data load)
