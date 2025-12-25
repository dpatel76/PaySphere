-- ============================================================================
-- CDM GLOBAL REGULATORY EXTENSIONS - FINANCIALINSTITUTION ENTITY
-- ============================================================================
-- Purpose: Extend FinancialInstitution entity with regulatory metadata
-- Coverage: US regulatory (FinCEN), Middle East/Islamic finance (Sharia)
-- Total New Attributes: 13 (8 regional + 5 global)
-- ISO 20022 Compliance: 15%
-- ============================================================================

-- Regional Enhancements (from previous phase) - if not already applied
ALTER TABLE cdm_silver.payments.financial_institution ADD COLUMNS IF NOT EXISTS (
  rssd_number VARCHAR(10) COMMENT 'FinCEN - RSSD number (Research, Statistics, Supervision, Discount) from Federal Reserve',
  tin_type VARCHAR(20) COMMENT 'FinCEN CTR Item 80/111 - TIN type: EIN, SSN, ITIN, Foreign - Non-ISO Extension',
  tin_value VARCHAR(50) COMMENT 'FinCEN CTR Item 81/112 - Tax Identification Number value - Non-ISO Extension',
  fi_type STRING COMMENT 'FinCEN - Financial institution type: DEPOSITORY_INSTITUTION, BROKER_DEALER, MSB, CASINO, INSURANCE_COMPANY, etc. - Non-ISO Extension',
  msb_registration_number VARCHAR(50) COMMENT 'FinCEN - Money Services Business registration number - Non-ISO Extension',
  primary_regulator VARCHAR(100) COMMENT 'FinCEN - Primary federal regulator: OCC, FDIC, FRB, NCUA, SEC, etc. - Non-ISO Extension',
  branch_country CHAR(2) COMMENT 'FinCEN - Branch country (ISO 3166-1 alpha-2) - ISO 20022 Compliant',
  branch_state VARCHAR(3) COMMENT 'FinCEN - Branch state/province (for US: 2-char state code, for others: ISO 3166-2) - ISO 20022 Compliant'
);

-- Phase 2: Middle East / Islamic Finance Extensions
ALTER TABLE cdm_silver.payments.financial_institution ADD COLUMNS IF NOT EXISTS (
  -- Islamic Finance / Sharia Compliance
  sharia_compliant_flag BOOLEAN COMMENT 'Islamic finance / Sharia-compliant institution flag - Non-ISO Extension',
  islamic_finance_type STRING COMMENT 'Type of Islamic finance institution: FULLY_SHARIA_COMPLIANT, SHARIA_COMPLIANT_WINDOW, TAKAFUL_PROVIDER, SUKUK_ISSUER, CONVENTIONAL - Non-ISO Extension',
  central_bank_license_number VARCHAR(50) COMMENT 'Central bank license number (global use) - ISO 20022 Compliant',
  islamic_financial_services_board BOOLEAN COMMENT 'IFSB (Islamic Financial Services Board) member flag - Non-ISO Extension',
  sharia_advisory_board BOOLEAN COMMENT 'Has Sharia advisory board (required for Islamic FIs) - Non-ISO Extension'
);

-- Add table comment
COMMENT ON TABLE cdm_silver.payments.financial_institution IS
'FinancialInstitution entity - Enhanced with 13 new attributes for regulatory reporting. Supports FinCEN identification requirements (RSSD, TIN, MSB registration) and Middle East/Islamic finance (Sharia compliance, IFSB membership). ISO 20022 Compliance: 15% (2 compliant, 0 extended, 11 non-ISO).';

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_fi_rssd_number
ON cdm_silver.payments.financial_institution (rssd_number);

CREATE INDEX IF NOT EXISTS idx_fi_tin
ON cdm_silver.payments.financial_institution (tin_type, tin_value);

CREATE INDEX IF NOT EXISTS idx_fi_type
ON cdm_silver.payments.financial_institution (fi_type);

CREATE INDEX IF NOT EXISTS idx_fi_sharia_compliant
ON cdm_silver.payments.financial_institution (sharia_compliant_flag);

CREATE INDEX IF NOT EXISTS idx_fi_islamic_finance_type
ON cdm_silver.payments.financial_institution (islamic_finance_type);

-- Sample query: Islamic financial institutions
CREATE OR REPLACE VIEW cdm_silver.compliance.v_islamic_financial_institutions AS
SELECT
  fi.financial_institution_id,
  fi.institution_name,
  fi.bic,
  fi.lei,
  fi.sharia_compliant_flag,
  fi.islamic_finance_type,
  fi.islamic_financial_services_board,
  fi.sharia_advisory_board,
  fi.central_bank_license_number,
  fi.country
FROM cdm_silver.payments.financial_institution fi
WHERE fi.sharia_compliant_flag = true
  AND fi.is_current = true;

-- Sample query: FinCEN-registered MSBs
CREATE OR REPLACE VIEW cdm_silver.compliance.v_fincen_msb_institutions AS
SELECT
  fi.financial_institution_id,
  fi.institution_name,
  fi.fi_type,
  fi.msb_registration_number,
  fi.tin_type,
  fi.tin_value,
  fi.primary_regulator,
  fi.rssd_number,
  fi.branch_country,
  fi.branch_state
FROM cdm_silver.payments.financial_institution fi
WHERE fi.fi_type = 'MSB'
  AND fi.msb_registration_number IS NOT NULL
  AND fi.is_current = true;

-- Sample query: Financial institutions by regulator
CREATE OR REPLACE VIEW cdm_silver.compliance.v_fi_by_regulator AS
SELECT
  fi.primary_regulator,
  fi.country,
  COUNT(DISTINCT fi.financial_institution_id) AS fi_count,
  COUNT(DISTINCT CASE WHEN fi.fi_type = 'DEPOSITORY_INSTITUTION' THEN fi.financial_institution_id END) AS depository_count,
  COUNT(DISTINCT CASE WHEN fi.fi_type = 'MSB' THEN fi.financial_institution_id END) AS msb_count,
  COUNT(DISTINCT CASE WHEN fi.fi_type = 'BROKER_DEALER' THEN fi.financial_institution_id END) AS broker_dealer_count,
  COUNT(DISTINCT CASE WHEN fi.sharia_compliant_flag = true THEN fi.financial_institution_id END) AS islamic_fi_count
FROM cdm_silver.payments.financial_institution fi
WHERE fi.is_current = true
GROUP BY fi.primary_regulator, fi.country
ORDER BY fi_count DESC;

-- Validation: Check that all new columns exist
SELECT
  'FinancialInstitution entity extended' AS status,
  COUNT(*) FILTER (WHERE column_name IN (
    'rssd_number', 'tin_type', 'tin_value', 'fi_type', 'msb_registration_number', 'primary_regulator', 'branch_country', 'branch_state',
    'sharia_compliant_flag', 'islamic_finance_type', 'central_bank_license_number', 'islamic_financial_services_board', 'sharia_advisory_board'
  )) AS new_columns_added
FROM information_schema.columns
WHERE table_schema = 'cdm_silver'
  AND table_name = 'financial_institution';

-- Expected result: 13 new columns added (or already exist)
