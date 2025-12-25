-- ============================================================================
-- CDM GLOBAL REGULATORY EXTENSIONS - ACCOUNT ENTITY
-- ============================================================================
-- Purpose: Extend Account entity with tax reporting and regulatory fields
-- Coverage: FATCA, CRS, controlling persons, account-level tax data
-- Total New Attributes: 10 (2 regional + 8 global)
-- ISO 20022 Compliance: 40%
-- ============================================================================

-- Regional Enhancements (from previous phase) - if not already applied
ALTER TABLE cdm_silver.payments.account ADD COLUMNS IF NOT EXISTS (
  loan_amount DECIMAL(18,2) COMMENT 'FinCEN SAR Item 59 - Loan amount if applicable',
  loan_origination DATE COMMENT 'FinCEN SAR Item 60 - Loan origination date'
);

-- Phase 1: Tax Reporting Extensions
ALTER TABLE cdm_silver.payments.account ADD COLUMNS IF NOT EXISTS (
  -- FATCA Account Status
  fatca_status STRING COMMENT 'FATCA status: PARTICIPATING_FFI_ACCOUNT, NON_PARTICIPATING_FFI_ACCOUNT, US_REPORTABLE_ACCOUNT, RECALCITRANT_ACCOUNT, DORMANT_ACCOUNT, EXEMPT_ACCOUNT - Non-ISO Extension',
  fatca_giin VARCHAR(19) COMMENT 'Global Intermediary Identification Number (19 chars: XXXXXX.XXXXX.XX.XXX) - Non-ISO Extension',

  -- CRS Reporting
  crs_reportable_account BOOLEAN COMMENT 'CRS reportable account flag - ISO 20022 Extended',

  -- Account Holder Classification
  account_holder_type STRING COMMENT 'FATCA/CRS account holder type: INDIVIDUAL, ENTITY_ACTIVE_NFE, ENTITY_PASSIVE_NFE, ENTITY_FINANCIAL_INSTITUTION, ENTITY_GOVERNMENT, ENTITY_INTERNATIONAL_ORG - Non-ISO Extension',

  -- Controlling Persons (for entity accounts)
  controlling_persons ARRAY<STRUCT<
    party_id:STRING COMMENT 'UUID reference to Party entity',
    control_type:STRING COMMENT 'Control type: OWNERSHIP, SENIOR_MANAGING_OFFICIAL, CONTROLLING_PERSON',
    ownership_percentage:DECIMAL(5,2) COMMENT 'Ownership percentage (0-100)',
    tax_residence:ARRAY<STRING> COMMENT 'Array of ISO country codes for tax residence',
    tin:STRING COMMENT 'Tax Identification Number',
    tin_type:STRING COMMENT 'TIN type: SSN, EIN, etc.',
    is_pep:BOOLEAN COMMENT 'Politically Exposed Person flag'
  >> COMMENT 'Controlling persons for entities (FATCA/CRS requirement) - ISO 20022 Compliant',

  -- Account Activity Status
  dormant_account BOOLEAN COMMENT 'Dormant/inactive account flag (no activity for specified period) - ISO 20022 Compliant',

  -- Tax Reporting Balances
  account_balance_for_tax_reporting DECIMAL(18,2) COMMENT 'Account balance for tax reporting purposes (year-end or period-end) - ISO 20022 Compliant',

  -- Withholding Tax
  withholding_tax_rate DECIMAL(5,2) COMMENT 'Applicable withholding tax rate (0-100 percent) - ISO 20022 Compliant'
);

-- Add table comment
COMMENT ON TABLE cdm_silver.payments.account IS
'Account entity - Enhanced with 10 new attributes for global tax reporting (FATCA, CRS). Supports controlling persons, dormant account classification, and tax-specific balances. ISO 20022 Compliance: 40% (4 compliant, 1 extended, 5 non-ISO).';

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_account_fatca_status
ON cdm_silver.payments.account (fatca_status);

CREATE INDEX IF NOT EXISTS idx_account_crs_reportable
ON cdm_silver.payments.account (crs_reportable_account);

CREATE INDEX IF NOT EXISTS idx_account_holder_type
ON cdm_silver.payments.account (account_holder_type);

CREATE INDEX IF NOT EXISTS idx_account_dormant
ON cdm_silver.payments.account (dormant_account);

-- Sample queries for tax reporting

-- FATCA Form 8966 - Identify US reportable accounts
CREATE OR REPLACE VIEW cdm_silver.compliance.v_fatca_reportable_accounts AS
SELECT
  a.account_id,
  a.account_number,
  a.fatca_status,
  a.fatca_giin,
  a.account_holder_type,
  a.account_balance_for_tax_reporting,
  a.withholding_tax_rate,
  p.party_id,
  p.name AS account_holder_name,
  p.us_tax_status,
  p.tax_residencies,
  a.controlling_persons
FROM cdm_silver.payments.account a
JOIN cdm_silver.payments.party p ON a.account_owner = p.party_id
WHERE a.fatca_status = 'US_REPORTABLE_ACCOUNT'
  AND a.dormant_account = false
  AND a.account_balance_for_tax_reporting > 0
  AND p.is_current = true
  AND a.is_current = true;

-- CRS Reporting - Identify CRS reportable accounts
CREATE OR REPLACE VIEW cdm_silver.compliance.v_crs_reportable_accounts AS
SELECT
  a.account_id,
  a.account_number,
  a.crs_reportable_account,
  a.account_holder_type,
  a.account_balance_for_tax_reporting,
  p.party_id,
  p.name AS account_holder_name,
  p.crs_reportable,
  p.crs_entity_type,
  p.tax_residencies,
  a.controlling_persons
FROM cdm_silver.payments.account a
JOIN cdm_silver.payments.party p ON a.account_owner = p.party_id
WHERE a.crs_reportable_account = true
  AND a.dormant_account = false
  AND p.is_current = true
  AND a.is_current = true;

-- Validation: Check that all new columns exist
SELECT
  'Account entity extended' AS status,
  COUNT(*) FILTER (WHERE column_name IN (
    'loan_amount', 'loan_origination',
    'fatca_status', 'fatca_giin', 'crs_reportable_account', 'account_holder_type',
    'controlling_persons', 'dormant_account', 'account_balance_for_tax_reporting', 'withholding_tax_rate'
  )) AS new_columns_added
FROM information_schema.columns
WHERE table_schema = 'cdm_silver'
  AND table_name = 'account';

-- Expected result: 10 new columns added (or already exist)
