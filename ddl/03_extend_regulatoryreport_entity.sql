-- ============================================================================
-- CDM GLOBAL REGULATORY EXTENSIONS - REGULATORYREPORT ENTITY
-- ============================================================================
-- Purpose: Extend RegulatoryReport entity with global regulatory metadata
-- Coverage: Tax (FATCA, CRS), Sanctions, UK DAML workflow, Terrorist property
-- Total New Attributes: 37 (14 regional + 24 global - some overlap)
-- ISO 20022 Compliance: 5%
-- ============================================================================

-- Regional Enhancements (from previous phase) - if not already applied
ALTER TABLE cdm_silver.compliance.regulatory_report ADD COLUMNS IF NOT EXISTS (
  reporting_entity_abn VARCHAR(11) COMMENT 'AUSTRAC IFTI Field 1.1 - Australian Business Number',
  reporting_entity_branch VARCHAR(100) COMMENT 'AUSTRAC IFTI Field 1.3 - Branch name/identifier',
  reporting_entity_contact_name VARCHAR(140) COMMENT 'AUSTRAC/FinCEN - Contact person name',
  reporting_entity_contact_phone VARCHAR(25) COMMENT 'AUSTRAC/FinCEN - Contact phone number',
  filing_type STRING COMMENT 'initial, amendment, correction, late - AUSTRAC/FinCEN filing type',
  prior_report_bsa_id VARCHAR(50) COMMENT 'FinCEN - Prior report BSA ID for amendments',
  reporting_period_type STRING COMMENT 'single_transaction, aggregated, periodic',
  total_cash_in DECIMAL(18,2) COMMENT 'FinCEN CTR - Total cash received',
  total_cash_out DECIMAL(18,2) COMMENT 'FinCEN CTR - Total cash disbursed',
  foreign_cash_in ARRAY<STRUCT<country:STRING, currency:STRING, amount:DECIMAL(18,2)>> COMMENT 'FinCEN CTR Items 62-66',
  foreign_cash_out ARRAY<STRUCT<country:STRING, currency:STRING, amount:DECIMAL(18,2)>> COMMENT 'FinCEN CTR Items 68-72',
  multiple_persons_flag BOOLEAN COMMENT 'FinCEN CTR Item 3 - Multiple persons involved',
  aggregation_method VARCHAR(100) COMMENT 'Transaction aggregation methodology'
);

-- Phase 1: Tax Reporting Extensions
ALTER TABLE cdm_silver.compliance.regulatory_report ADD COLUMNS IF NOT EXISTS (
  -- FATCA Reporting
  tax_year INT COMMENT 'Tax reporting year (YYYY format) - Non-ISO Extension',
  reporting_fi_giin VARCHAR(19) COMMENT 'Reporting FI GIIN for FATCA (19 chars: XXXXXX.XXXXX.XX.XXX) - Non-ISO Extension',
  reporting_fi_tin VARCHAR(50) COMMENT 'Reporting FI Tax Identification Number - ISO 20022 Compliant',
  sponsor_giin VARCHAR(19) COMMENT 'Sponsor GIIN if sponsored FFI (19 chars) - Non-ISO Extension',

  -- FATCA/CRS Reporting Model
  reporting_model STRING COMMENT 'FATCA/CRS reporting model: MODEL1_IGA, MODEL2_IGA, NON_IGA_FATCA, CRS - Non-ISO Extension',
  iga_jurisdiction CHAR(2) COMMENT 'IGA (Intergovernmental Agreement) jurisdiction (ISO 3166-1 alpha-2) - Non-ISO Extension',

  -- FATCA Pool Reporting
  pool_report_type STRING COMMENT 'Pool reporting type: RECALCITRANT_ACCOUNT_HOLDERS_WITH_US_INDICIA, RECALCITRANT_ACCOUNT_HOLDERS_WITHOUT_US_INDICIA, DORMANT_ACCOUNTS, NON_PARTICIPATING_FFIS - Non-ISO Extension'
);

-- Phase 1: Sanctions Reporting Extensions
ALTER TABLE cdm_silver.compliance.regulatory_report ADD COLUMNS IF NOT EXISTS (
  sanctions_blocking_date DATE COMMENT 'Date property was blocked due to sanctions - Non-ISO Extension',
  property_blocked STRING COMMENT 'Description of blocked property (funds, assets, etc.) - Non-ISO Extension',
  estimated_property_value DECIMAL(18,2) COMMENT 'Estimated value of blocked property in USD - Non-ISO Extension',
  sanctions_program STRING COMMENT 'Sanctions program name (Iran, Russia, North Korea, ISIL, etc.) - Non-ISO Extension'
);

-- Phase 2: Regional Workflow Extensions (UK DAML)
ALTER TABLE cdm_silver.compliance.regulatory_report ADD COLUMNS IF NOT EXISTS (
  -- UK Defence Against Money Laundering (DAML) Consent Regime
  defence_against_money_laundering_flag BOOLEAN COMMENT 'UK DAML SAR flag (consent regime) - Non-ISO Extension',
  consent_required BOOLEAN COMMENT 'Consent required to proceed with transaction - Non-ISO Extension',
  consent_granted BOOLEAN COMMENT 'Consent granted by UK NCA (National Crime Agency) - Non-ISO Extension',
  consent_refusal_reason STRING COMMENT 'Reason for consent refusal from NCA - Non-ISO Extension',
  consent_request_date TIMESTAMP COMMENT 'When consent was requested from UK NCA - Non-ISO Extension',
  consent_response_date TIMESTAMP COMMENT 'When consent response received from NCA - Non-ISO Extension',
  consent_expiry_date TIMESTAMP COMMENT 'Consent expiry (7 business days default, or 31 days if refused) - Non-ISO Extension',
  sarn_number VARCHAR(20) COMMENT 'SAR reference number from UK NCA - Non-ISO Extension'
);

-- Phase 3: Terrorist Property Reporting
ALTER TABLE cdm_silver.compliance.regulatory_report ADD COLUMNS IF NOT EXISTS (
  terrorist_property_flag BOOLEAN COMMENT 'Terrorist property report indicator (Canada, South Africa, etc.) - Non-ISO Extension',
  terrorist_entity_name VARCHAR(200) COMMENT 'Listed terrorist entity name - ISO 20022 Compliant',
  terrorist_list_source VARCHAR(100) COMMENT 'List source: UN, domestic list, etc. - ISO 20022 Extended',
  property_description STRING COMMENT 'Description of terrorist property - ISO 20022 Compliant',
  property_seized BOOLEAN COMMENT 'Property seized flag - Non-ISO Extension'
);

-- Add table comment
COMMENT ON TABLE cdm_silver.compliance.regulatory_report IS
'RegulatoryReport entity - Enhanced with 24 new attributes for global regulatory reporting. Supports tax reporting (FATCA, CRS), sanctions blocking, UK DAML consent workflow, and terrorist property reporting. ISO 20022 Compliance: 5% (2 compliant, 0 extended, 35 non-ISO).';

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_regulatoryreport_tax_year
ON cdm_silver.compliance.regulatory_report (tax_year);

CREATE INDEX IF NOT EXISTS idx_regulatoryreport_reporting_model
ON cdm_silver.compliance.regulatory_report (reporting_model);

CREATE INDEX IF NOT EXISTS idx_regulatoryreport_sanctions_blocking
ON cdm_silver.compliance.regulatory_report (sanctions_blocking_date);

CREATE INDEX IF NOT EXISTS idx_regulatoryreport_daml_consent
ON cdm_silver.compliance.regulatory_report (defence_against_money_laundering_flag, consent_granted);

CREATE INDEX IF NOT EXISTS idx_regulatoryreport_terrorist_property
ON cdm_silver.compliance.regulatory_report (terrorist_property_flag);

-- Sample query: FATCA reports pending submission
CREATE OR REPLACE VIEW cdm_silver.compliance.v_fatca_reports_pending AS
SELECT
  rr.regulatory_report_id,
  rr.report_type,
  rr.tax_year,
  rr.reporting_fi_giin,
  rr.reporting_model,
  rr.iga_jurisdiction,
  rr.report_status,
  rr.due_date,
  rr.transaction_count,
  rr.total_reported_value
FROM cdm_silver.compliance.regulatory_report rr
WHERE rr.report_type IN ('FATCA_FORM_8966', 'FATCA_FORM_8966_POOL')
  AND rr.report_status IN ('draft', 'pending_review', 'approved')
  AND rr.submission_date IS NULL;

-- Sample query: UK DAML SARs awaiting NCA consent
CREATE OR REPLACE VIEW cdm_silver.compliance.v_uk_daml_sars_awaiting_consent AS
SELECT
  rr.regulatory_report_id,
  rr.report_reference_number,
  rr.sarn_number,
  rr.consent_required,
  rr.consent_granted,
  rr.consent_request_date,
  rr.consent_response_date,
  rr.consent_expiry_date,
  rr.consent_refusal_reason,
  DATEDIFF(DAY, rr.consent_request_date, CURRENT_TIMESTAMP) AS days_waiting,
  CASE
    WHEN rr.consent_expiry_date < CURRENT_TIMESTAMP THEN 'EXPIRED'
    WHEN DATEDIFF(DAY, rr.consent_request_date, CURRENT_TIMESTAMP) > 7 AND rr.consent_granted IS NULL THEN 'OVERDUE'
    ELSE 'PENDING'
  END AS consent_status
FROM cdm_silver.compliance.regulatory_report rr
WHERE rr.report_type = 'UK_SAR_DAML'
  AND rr.defence_against_money_laundering_flag = true
  AND rr.consent_required = true
  AND (rr.consent_granted IS NULL OR rr.consent_granted = false);

-- Sample query: Sanctions blocking reports
CREATE OR REPLACE VIEW cdm_silver.compliance.v_sanctions_blocking_reports AS
SELECT
  rr.regulatory_report_id,
  rr.report_type,
  rr.sanctions_blocking_date,
  rr.sanctions_program,
  rr.property_blocked,
  rr.estimated_property_value,
  rr.submission_date,
  rr.report_status
FROM cdm_silver.compliance.regulatory_report rr
WHERE rr.sanctions_blocking_date IS NOT NULL
  AND rr.report_status IN ('draft', 'pending_review', 'approved', 'submitted');

-- Validation: Check that all new columns exist
SELECT
  'RegulatoryReport entity extended' AS status,
  COUNT(*) FILTER (WHERE column_name IN (
    'reporting_entity_abn', 'reporting_entity_branch', 'reporting_entity_contact_name', 'reporting_entity_contact_phone',
    'filing_type', 'prior_report_bsa_id', 'reporting_period_type',
    'total_cash_in', 'total_cash_out', 'foreign_cash_in', 'foreign_cash_out', 'multiple_persons_flag', 'aggregation_method',
    'tax_year', 'reporting_fi_giin', 'reporting_fi_tin', 'sponsor_giin', 'reporting_model', 'iga_jurisdiction', 'pool_report_type',
    'sanctions_blocking_date', 'property_blocked', 'estimated_property_value', 'sanctions_program',
    'defence_against_money_laundering_flag', 'consent_required', 'consent_granted', 'consent_refusal_reason',
    'consent_request_date', 'consent_response_date', 'consent_expiry_date', 'sarn_number',
    'terrorist_property_flag', 'terrorist_entity_name', 'terrorist_list_source', 'property_description', 'property_seized'
  )) AS new_columns_added
FROM information_schema.columns
WHERE table_schema = 'cdm_silver'
  AND table_name = 'regulatory_report';

-- Expected result: 37 new columns added (or already exist)
