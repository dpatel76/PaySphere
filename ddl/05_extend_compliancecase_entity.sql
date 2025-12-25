-- ============================================================================
-- CDM GLOBAL REGULATORY EXTENSIONS - COMPLIANCECASE ENTITY
-- ============================================================================
-- Purpose: Extend ComplianceCase entity for SAR and AML case management
-- Coverage: FinCEN SAR (US), global FIU referrals
-- Total New Attributes: 13 (all regional from previous phase)
-- ISO 20022 Compliance: 15%
-- ============================================================================

-- Regional Enhancements (from previous phase) - if not already applied
ALTER TABLE cdm_silver.compliance.compliance_case ADD COLUMNS IF NOT EXISTS (
  -- FinCEN SAR Narrative and Activity Classification
  sar_narrative STRING COMMENT 'FinCEN SAR Item 104 - Detailed SAR narrative (max 71,600 characters) - Non-ISO Extension',
  sar_activity_type_checkboxes ARRAY<STRING> COMMENT 'FinCEN SAR Items 52-68 - Activity type checkboxes: STRUCTURING, TERRORIST_FINANCING, FRAUD, IDENTITY_THEFT, CHECK_FRAUD, COUNTERFEIT_CHECK, WIRE_TRANSFER_FRAUD, ACH_FRAUD, CREDIT_CARD_FRAUD, MONEY_LAUNDERING, BRIBERY, EMBEZZLEMENT, MISUSE_OF_POSITION, CYBER_EVENT, UNAUTHORIZED_WIRE_TRANSFER, OTHER - Non-ISO Extension',

  -- Law Enforcement Interaction
  law_enforcement_contact_date DATE COMMENT 'FinCEN SAR Item 92 - Date law enforcement was contacted - ISO 20022 Compliant',
  law_enforcement_contact_name VARCHAR(140) COMMENT 'FinCEN SAR Item 92 - Law enforcement contact person name - ISO 20022 Compliant',
  law_enforcement_agency VARCHAR(200) COMMENT 'FinCEN SAR Item 92 - Law enforcement agency name (FBI, Secret Service, local police, etc.) - Non-ISO Extension',

  -- Financial Recovery and Loss
  recovered_amount DECIMAL(18,2) COMMENT 'Amount recovered from fraud/loss (FinCEN SAR follow-up reporting) - Non-ISO Extension',

  -- Suspect Status and Outcomes
  suspect_fled_indicator BOOLEAN COMMENT 'FinCEN SAR Item 51 - Suspect has fled jurisdiction flag - Non-ISO Extension',
  suspect_arrest_date DATE COMMENT 'Date suspect was arrested (FinCEN SAR follow-up) - Non-ISO Extension',
  suspect_conviction_date DATE COMMENT 'Date of suspect conviction (FinCEN SAR follow-up) - Non-ISO Extension',

  -- Case Management and Workflow
  investigation_status STRING COMMENT 'Investigation workflow status: open, under_investigation, closed, referred_to_law_enforcement, prosecuted - ISO 20022 Extended',

  -- Global FIU Referrals
  referral_to_fiu BOOLEAN COMMENT 'Referred to Financial Intelligence Unit (FIU) flag - Non-ISO Extension',
  fiu_referral_date DATE COMMENT 'Date case was referred to FIU - Non-ISO Extension',
  fiu_reference_number VARCHAR(100) COMMENT 'FIU reference number for tracking (FINTRAC, AUSTRAC, NCA, GAFI, etc.) - Non-ISO Extension'
);

-- Add table comment
COMMENT ON TABLE cdm_silver.compliance.compliance_case IS
'ComplianceCase entity - Enhanced with 13 new attributes for SAR and AML case management. Supports FinCEN SAR narrative and activity classification, law enforcement interaction tracking, suspect status, and global FIU referrals. ISO 20022 Compliance: 15% (2 compliant, 1 extended, 10 non-ISO).';

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_compliancecase_investigation_status
ON cdm_silver.compliance.compliance_case (investigation_status);

CREATE INDEX IF NOT EXISTS idx_compliancecase_le_contact
ON cdm_silver.compliance.compliance_case (law_enforcement_contact_date);

CREATE INDEX IF NOT EXISTS idx_compliancecase_fiu_referral
ON cdm_silver.compliance.compliance_case (referral_to_fiu, fiu_referral_date);

CREATE INDEX IF NOT EXISTS idx_compliancecase_suspect_fled
ON cdm_silver.compliance.compliance_case (suspect_fled_indicator);

-- Sample query: Active SAR cases awaiting law enforcement action
CREATE OR REPLACE VIEW cdm_silver.compliance.v_active_sar_cases AS
SELECT
  cc.compliance_case_id,
  cc.case_number,
  cc.case_type,
  cc.investigation_status,
  cc.sar_narrative,
  cc.sar_activity_type_checkboxes,
  cc.law_enforcement_contact_date,
  cc.law_enforcement_contact_name,
  cc.law_enforcement_agency,
  cc.suspect_fled_indicator,
  cc.recovered_amount,
  cc.total_transaction_amount,
  cc.created_timestamp,
  DATEDIFF(DAY, cc.created_timestamp, CURRENT_TIMESTAMP) AS days_open
FROM cdm_silver.compliance.compliance_case cc
WHERE cc.case_type = 'SAR'
  AND cc.investigation_status IN ('open', 'under_investigation', 'referred_to_law_enforcement')
  AND cc.is_current = true
ORDER BY cc.created_timestamp ASC;

-- Sample query: FIU referrals by country
CREATE OR REPLACE VIEW cdm_silver.compliance.v_fiu_referrals AS
SELECT
  cc.compliance_case_id,
  cc.case_number,
  cc.case_type,
  cc.referral_to_fiu,
  cc.fiu_referral_date,
  cc.fiu_reference_number,
  cc.investigation_status,
  cc.total_transaction_amount,
  rr.jurisdiction AS fiu_jurisdiction,
  rr.regulatory_authority AS fiu_name
FROM cdm_silver.compliance.compliance_case cc
LEFT JOIN cdm_silver.compliance.regulatory_report rr
  ON cc.compliance_case_id = rr.related_compliance_case_id
WHERE cc.referral_to_fiu = true
  AND cc.is_current = true
ORDER BY cc.fiu_referral_date DESC;

-- Sample query: SAR activity type distribution (for risk analytics)
CREATE OR REPLACE VIEW cdm_silver.compliance.v_sar_activity_type_distribution AS
SELECT
  explode(cc.sar_activity_type_checkboxes) AS activity_type,
  COUNT(DISTINCT cc.compliance_case_id) AS case_count,
  SUM(cc.total_transaction_amount) AS total_amount,
  AVG(cc.total_transaction_amount) AS avg_amount,
  MIN(cc.created_timestamp) AS first_case_date,
  MAX(cc.created_timestamp) AS most_recent_case_date
FROM cdm_silver.compliance.compliance_case cc
WHERE cc.case_type = 'SAR'
  AND cc.sar_activity_type_checkboxes IS NOT NULL
  AND cc.is_current = true
GROUP BY explode(cc.sar_activity_type_checkboxes)
ORDER BY case_count DESC;

-- Sample query: Cases with suspect arrests/convictions
CREATE OR REPLACE VIEW cdm_silver.compliance.v_suspect_outcomes AS
SELECT
  cc.compliance_case_id,
  cc.case_number,
  cc.case_type,
  cc.suspect_fled_indicator,
  cc.suspect_arrest_date,
  cc.suspect_conviction_date,
  cc.recovered_amount,
  cc.total_transaction_amount,
  CASE
    WHEN cc.suspect_conviction_date IS NOT NULL THEN 'CONVICTED'
    WHEN cc.suspect_arrest_date IS NOT NULL THEN 'ARRESTED'
    WHEN cc.suspect_fled_indicator = true THEN 'FLED'
    ELSE 'UNDER_INVESTIGATION'
  END AS suspect_status,
  CASE
    WHEN cc.recovered_amount IS NOT NULL AND cc.total_transaction_amount > 0
    THEN (cc.recovered_amount / cc.total_transaction_amount) * 100
    ELSE 0
  END AS recovery_percentage
FROM cdm_silver.compliance.compliance_case cc
WHERE cc.is_current = true
  AND (cc.suspect_arrest_date IS NOT NULL
       OR cc.suspect_conviction_date IS NOT NULL
       OR cc.suspect_fled_indicator = true
       OR cc.recovered_amount IS NOT NULL);

-- Validation: Check that all new columns exist
SELECT
  'ComplianceCase entity extended' AS status,
  COUNT(*) FILTER (WHERE column_name IN (
    'sar_narrative', 'sar_activity_type_checkboxes', 'law_enforcement_contact_date', 'law_enforcement_contact_name', 'law_enforcement_agency',
    'recovered_amount', 'suspect_fled_indicator', 'suspect_arrest_date', 'suspect_conviction_date',
    'investigation_status', 'referral_to_fiu', 'fiu_referral_date', 'fiu_reference_number'
  )) AS new_columns_added
FROM information_schema.columns
WHERE table_schema = 'cdm_silver'
  AND table_name = 'compliance_case';

-- Expected result: 13 new columns added (or already exist)
