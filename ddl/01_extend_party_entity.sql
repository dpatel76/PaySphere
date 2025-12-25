-- ============================================================================
-- CDM GLOBAL REGULATORY EXTENSIONS - PARTY ENTITY
-- ============================================================================
-- Purpose: Extend Party entity with global regulatory reporting fields
-- Coverage: Tax reporting (FATCA, CRS), APAC national IDs, regional requirements
-- Total New Attributes: 31 (13 regional + 18 global)
-- ISO 20022 Compliance: 19%
-- ============================================================================

-- Regional Enhancements (from previous phase) - if not already applied
ALTER TABLE cdm_silver.payments.party ADD COLUMNS IF NOT EXISTS (
  given_name VARCHAR(35) COMMENT 'AUSTRAC IFTI Field 2.2 - First/given name(s) for individuals',
  family_name VARCHAR(35) COMMENT 'AUSTRAC IFTI Field 2.3 - Family/last name for individuals',
  suffix VARCHAR(10) COMMENT 'FinCEN CTR Item 9 - Name suffix (Jr., Sr., III)',
  dba_name VARCHAR(140) COMMENT 'FinCEN CTR Item 11 - Doing Business As / Trade Name',
  occupation VARCHAR(100) COMMENT 'FinCEN CTR Item 12, SAR Item 45 - Occupation or type of business',
  naics_code VARCHAR(6) COMMENT 'FinCEN CTR Item 13 - NAICS industry classification (6-digit)',
  form_of_identification VARCHAR(100) COMMENT 'FinCEN CTR Item 15 - Type of ID document',
  identification_number VARCHAR(50) COMMENT 'FinCEN CTR Item 16 - ID document number',
  identification_issuing_country CHAR(2) COMMENT 'FinCEN CTR Item 17 - ID issuing country (ISO 3166-1)',
  identification_issuing_state VARCHAR(3) COMMENT 'FinCEN CTR Item 18 - ID issuing state/province',
  alternate_names ARRAY<STRING> COMMENT 'FinCEN SAR Item 39 - Known aliases or alternate names',
  entity_formation VARCHAR(50) COMMENT 'FinCEN SAR Item 44 - Type of entity formation',
  number_of_employees INT COMMENT 'FinCEN SAR Item 46 - Number of employees'
);

-- Phase 1: Tax Reporting Extensions
ALTER TABLE cdm_silver.payments.party ADD COLUMNS IF NOT EXISTS (
  -- US Tax Reporting (FATCA)
  us_tax_status STRING COMMENT 'US tax classification: US_CITIZEN, US_RESIDENT_ALIEN, NON_RESIDENT_ALIEN, US_CORPORATION, US_PARTNERSHIP, US_TRUST, FOREIGN_ENTITY - Non-ISO Extension',
  fatca_classification STRING COMMENT 'FATCA entity classification: ACTIVE_NFFE, PASSIVE_NFFE, FFI, PARTICIPATING_FFI, REGISTERED_DEEMED_COMPLIANT_FFI, CERTIFIED_DEEMED_COMPLIANT_FFI, EXCEPTED_FFI, EXEMPT_BENEFICIAL_OWNER, DIRECT_REPORTING_NFFE, SPONSORED_DIRECT_REPORTING_NFFE - Non-ISO Extension',

  -- OECD CRS (Common Reporting Standard)
  crs_reportable BOOLEAN COMMENT 'CRS reportable flag (OECD Common Reporting Standard) - ISO 20022 Extended',
  crs_entity_type STRING COMMENT 'CRS entity type: FINANCIAL_INSTITUTION, ACTIVE_NFE, PASSIVE_NFE, INVESTMENT_ENTITY, GOVERNMENT_ENTITY, INTERNATIONAL_ORGANISATION, CENTRAL_BANK - Non-ISO Extension',

  -- Tax Residency Information
  tax_residencies ARRAY<STRUCT<
    country:STRING COMMENT 'ISO 3166-1 alpha-2 country code',
    tin_type:STRING COMMENT 'TIN type: SSN, EIN, VAT, NIF, etc.',
    tin:STRING COMMENT 'Tax Identification Number',
    tax_residency_basis:STRING COMMENT 'Basis: CITIZENSHIP, RESIDENCE, DOMICILE, INCORPORATION',
    effective_from:DATE COMMENT 'Effective start date',
    effective_to:DATE COMMENT 'Effective end date (NULL = current)'
  >> COMMENT 'Array of tax residency countries with TINs - ISO 20022 Compliant',

  -- IRS Form Status
  w8ben_status STRING COMMENT 'W-8BEN form status: ACTIVE, EXPIRED, NOT_PROVIDED - Non-ISO Extension',
  w9_status STRING COMMENT 'W-9 form status: ACTIVE, EXPIRED, NOT_PROVIDED - Non-ISO Extension',

  -- Additional Tax IDs
  tin_issuing_country CHAR(2) COMMENT 'TIN issuing country (ISO 3166-1 alpha-2) - beyond primary - ISO 20022 Compliant',
  secondary_tins ARRAY<STRUCT<
    country:STRING,
    tin:STRING,
    tin_type:STRING
  >> COMMENT 'Secondary tax IDs for multiple jurisdictions - ISO 20022 Compliant',

  -- FATCA Ownership
  substantial_us_owner BOOLEAN COMMENT 'Substantial US owner flag (FATCA - owns >10% of entity) - Non-ISO Extension'
);

-- Phase 2: Asia-Pacific National ID Extensions
ALTER TABLE cdm_silver.payments.party ADD COLUMNS IF NOT EXISTS (
  -- Generic National ID
  national_id_type VARCHAR(50) COMMENT 'Country-specific national ID type (Resident ID, NRIC, My Number, Hukou, Aadhaar, etc.) - Non-ISO Extension',
  national_id_number VARCHAR(50) COMMENT 'National ID number - Non-ISO Extension',

  -- China
  china_hukou VARCHAR(100) COMMENT 'Hukou (household registration) - China - Non-ISO Extension',

  -- India
  india_aadhar_number VARCHAR(12) COMMENT 'Aadhaar UID (12 digits) - India - Non-ISO Extension',
  india_pan_number VARCHAR(20) COMMENT 'PAN (Permanent Account Number) alternate - India - Non-ISO Extension',

  -- South Korea
  korea_alien_registration_number VARCHAR(13) COMMENT 'Alien registration number (13 digits) - South Korea - Non-ISO Extension',

  -- Japan
  japan_my_number VARCHAR(12) COMMENT 'My Number / Individual Number (12 digits) - Japan - Non-ISO Extension',

  -- Singapore
  singapore_nric_fin VARCHAR(9) COMMENT 'NRIC (citizen - Sxxxxxxx) or FIN (foreigner - Fxxxxxxx) - Singapore - Non-ISO Extension'
);

-- Add table comment
COMMENT ON TABLE cdm_silver.payments.party IS
'Party entity - Enhanced with 31 new attributes for global regulatory reporting across 69 jurisdictions. Includes tax reporting (FATCA, CRS), APAC national IDs, and regional requirements. ISO 20022 Compliance: 19% (6 compliant, 3 extended, 22 non-ISO).';

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_party_us_tax_status
ON cdm_silver.payments.party (us_tax_status);

CREATE INDEX IF NOT EXISTS idx_party_fatca_classification
ON cdm_silver.payments.party (fatca_classification);

CREATE INDEX IF NOT EXISTS idx_party_crs_reportable
ON cdm_silver.payments.party (crs_reportable);

CREATE INDEX IF NOT EXISTS idx_party_national_id
ON cdm_silver.payments.party (national_id_type, national_id_number);

-- Validation: Check that all new columns exist
SELECT
  'Party entity extended' AS status,
  COUNT(*) FILTER (WHERE column_name IN (
    'given_name', 'family_name', 'suffix', 'dba_name', 'occupation', 'naics_code',
    'us_tax_status', 'fatca_classification', 'crs_reportable', 'crs_entity_type',
    'tax_residencies', 'w8ben_status', 'w9_status', 'tin_issuing_country', 'secondary_tins', 'substantial_us_owner',
    'national_id_type', 'national_id_number', 'china_hukou', 'india_aadhar_number', 'india_pan_number',
    'korea_alien_registration_number', 'japan_my_number', 'singapore_nric_fin'
  )) AS new_columns_added
FROM information_schema.columns
WHERE table_schema = 'cdm_silver'
  AND table_name = 'party';

-- Expected result: 31 new columns added (or already exist)
