-- GPS Payments CDM - Requirement Traceability Tables
-- Databricks Delta Lake DDL
-- Version: 1.1.0
-- Date: 2024-12-21

-- =============================================================================
-- REGULATORY REQUIREMENT TRACEABILITY SCHEMA
-- Links regulatory requirements → CDM fields → source systems → lineage
-- Supports 32+ regulatory reports across 11 regulators
-- =============================================================================

USE CATALOG gps_cdm;

CREATE SCHEMA IF NOT EXISTS regulatory
COMMENT 'Regulatory requirement traceability and compliance tracking';

USE SCHEMA regulatory;

-- =============================================================================
-- REFERENCE TABLES: Regulators, Reports, and Requirements
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Regulator Reference
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS regulatory.regulator (
    regulator_id STRING NOT NULL,
    regulator_code STRING NOT NULL,
    regulator_name STRING NOT NULL,
    jurisdiction STRING NOT NULL,
    country_code STRING,
    website STRING,

    -- Contact
    contact_email STRING,
    contact_phone STRING,

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    last_updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

    CONSTRAINT pk_regulator PRIMARY KEY (regulator_id)
)
USING DELTA
COMMENT 'Reference table of regulatory authorities';

-- Insert all regulators
INSERT INTO regulatory.regulator VALUES
    -- United States
    ('REG-001', 'FINCEN', 'Financial Crimes Enforcement Network', 'US', 'US', 'https://www.fincen.gov/', NULL, NULL, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('REG-002', 'IRS', 'Internal Revenue Service', 'US', 'US', 'https://www.irs.gov/', NULL, NULL, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('REG-003', 'OFAC', 'Office of Foreign Assets Control', 'US', 'US', 'https://ofac.treasury.gov/', NULL, NULL, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

    -- Australia
    ('REG-004', 'AUSTRAC', 'Australian Transaction Reports and Analysis Centre', 'AU', 'AU', 'https://www.austrac.gov.au/', NULL, NULL, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

    -- Canada
    ('REG-005', 'FINTRAC', 'Financial Transactions and Reports Analysis Centre of Canada', 'CA', 'CA', 'https://www.fintrac-canafe.gc.ca/', NULL, NULL, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

    -- Europe
    ('REG-006', 'EBA', 'European Banking Authority', 'EU', NULL, 'https://www.eba.europa.eu/', NULL, NULL, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('REG-007', 'ESMA', 'European Securities and Markets Authority', 'EU', NULL, 'https://www.esma.europa.eu/', NULL, NULL, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

    -- United Kingdom
    ('REG-008', 'UK_NCA', 'UK National Crime Agency', 'UK', 'GB', 'https://www.nationalcrimeagency.gov.uk/', NULL, NULL, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

    -- International
    ('REG-009', 'OECD', 'Organisation for Economic Co-operation and Development', 'INTERNATIONAL', NULL, 'https://www.oecd.org/', NULL, NULL, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

    -- Asia-Pacific
    -- Note: HKMA is the regulator/supervisor, JFIU is the FIU where STRs are filed
    ('REG-010', 'JFIU', 'Joint Financial Intelligence Unit (Hong Kong)', 'HK', 'HK', 'https://www.jfiu.gov.hk/', NULL, NULL, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('REG-011', 'STRO', 'Suspicious Transaction Reporting Office (Singapore)', 'SG', 'SG', 'https://www.police.gov.sg/stro', NULL, NULL, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('REG-012', 'JAFIC', 'Japan Financial Intelligence Center', 'JP', 'JP', 'https://www.npa.go.jp/sosikihanzai/jafic/', NULL, NULL, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    -- Supervisory authorities (not FIUs, but set regulations)
    ('REG-013', 'HKMA', 'Hong Kong Monetary Authority', 'HK', 'HK', 'https://www.hkma.gov.hk/', NULL, NULL, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('REG-014', 'MAS', 'Monetary Authority of Singapore', 'SG', 'SG', 'https://www.mas.gov.sg/', NULL, NULL, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

-- -----------------------------------------------------------------------------
-- Report Type Reference
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS regulatory.report_type (
    report_type_id STRING NOT NULL,
    report_code STRING NOT NULL,
    report_name STRING NOT NULL,
    regulator_id STRING NOT NULL,

    -- Report Details
    form_number STRING,
    regulation_reference STRING,
    filing_frequency STRING NOT NULL,
    filing_deadline STRING,
    output_format STRING,
    submission_method STRING,
    submission_url STRING,

    -- Thresholds
    threshold_amount DECIMAL(18,4),
    threshold_currency STRING,
    threshold_description STRING,

    -- Requirements Summary
    total_requirements INT,
    mandatory_requirements INT,

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    last_updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

    CONSTRAINT pk_report_type PRIMARY KEY (report_type_id),
    CONSTRAINT fk_report_regulator FOREIGN KEY (regulator_id) REFERENCES regulatory.regulator(regulator_id)
)
USING DELTA
COMMENT 'Reference table of regulatory report types';

-- Insert all 32 report types
INSERT INTO regulatory.report_type VALUES
    -- FinCEN (7 reports)
    ('RPT-001', 'FINCEN_CTR', 'Currency Transaction Report', 'REG-001', 'Form 112', '31 CFR 1010.311-1010.314', 'DAILY', '15 days after transaction', 'XML', 'BSA E-Filing', 'https://bsaefiling.fincen.treas.gov/', 10000, 'USD', 'Cash transactions >= $10,000', 117, 98, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-002', 'FINCEN_SAR', 'Suspicious Activity Report', 'REG-001', 'Form 111', '31 CFR 1020.320', 'EVENT_DRIVEN', '30 days after detection', 'XML', 'BSA E-Filing', 'https://bsaefiling.fincen.treas.gov/', 5000, 'USD', 'Suspicious activity >= $5,000', 184, 156, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-003', 'FINCEN_FBAR', 'Foreign Bank Account Report', 'REG-001', 'Form 114', '31 CFR 1010.350', 'ANNUAL', 'April 15', 'XML', 'BSA E-Filing', 'https://bsaefiling.fincen.treas.gov/', 10000, 'USD', 'Foreign account aggregate > $10,000', 92, 78, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-004', 'FINCEN_8300', 'Cash Payments Over $10,000', 'REG-001', 'Form 8300', '26 USC 6050I', 'EVENT_DRIVEN', '15 days after receipt', 'XML', 'BSA E-Filing', NULL, 10000, 'USD', 'Cash receipt >= $10,000', 78, 65, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-005', 'FINCEN_CMIR', 'Currency and Monetary Instrument Report', 'REG-001', 'Form 104', '31 CFR 1010.340', 'EVENT_DRIVEN', 'At time of transport', 'XML', 'BSA E-Filing', NULL, 10000, 'USD', 'Transport >= $10,000', 85, 72, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-006', 'FINCEN_314A', 'Information Request', 'REG-001', NULL, '31 CFR 1010.520', 'ON_DEMAND', 'Within 2 weeks', 'XML', 'Secure Email', NULL, NULL, NULL, 'Law enforcement request', 45, 38, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-007', 'FINCEN_314B', 'Information Sharing Notice', 'REG-001', NULL, '31 CFR 1010.540', 'EVENT_DRIVEN', 'Prior to sharing', 'XML', 'Secure Portal', NULL, NULL, NULL, 'Voluntary info sharing', 38, 32, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

    -- AUSTRAC (5 reports)
    ('RPT-010', 'AUSTRAC_IFTI', 'International Funds Transfer Instruction', 'REG-004', NULL, 'AML/CTF Act 2006 Part 4', 'REAL_TIME', '10 business days', 'XML', 'AUSTRAC Online', 'https://online.austrac.gov.au/', NULL, NULL, 'All international transfers', 87, 74, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-011', 'AUSTRAC_IFTI_IN', 'IFTI Inbound', 'REG-004', NULL, 'AML/CTF Act 2006 Part 4', 'REAL_TIME', '10 business days', 'XML', 'AUSTRAC Online', 'https://online.austrac.gov.au/', NULL, NULL, 'Inbound international transfers', 83, 71, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-012', 'AUSTRAC_IFTI_OUT', 'IFTI Outbound', 'REG-004', NULL, 'AML/CTF Act 2006 Part 4', 'REAL_TIME', '10 business days', 'XML', 'AUSTRAC Online', 'https://online.austrac.gov.au/', NULL, NULL, 'Outbound international transfers', 83, 71, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-013', 'AUSTRAC_TTR', 'Threshold Transaction Report', 'REG-004', NULL, 'AML/CTF Act 2006 Section 43', 'EVENT_DRIVEN', '10 business days', 'XML', 'AUSTRAC Online', 'https://online.austrac.gov.au/', 10000, 'AUD', 'Cash >= AUD 10,000', 76, 65, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-014', 'AUSTRAC_SMR', 'Suspicious Matter Report', 'REG-004', NULL, 'AML/CTF Act 2006 Section 41', 'EVENT_DRIVEN', '24h (terrorism) / 3 days', 'XML', 'AUSTRAC Online', 'https://online.austrac.gov.au/', NULL, NULL, 'Suspicious matters', 92, 78, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

    -- FINTRAC (4 reports)
    ('RPT-020', 'FINTRAC_LCTR', 'Large Cash Transaction Report', 'REG-005', NULL, 'PCMLTFA Section 7', 'EVENT_DRIVEN', '15 calendar days', 'XML', 'FINTRAC Web Reporting', 'https://www.fintrac-canafe.gc.ca/', 10000, 'CAD', 'Cash >= CAD 10,000', 95, 82, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-021', 'FINTRAC_STR', 'Suspicious Transaction Report', 'REG-005', NULL, 'PCMLTFA Section 7', 'EVENT_DRIVEN', '30 calendar days', 'XML', 'FINTRAC Web Reporting', 'https://www.fintrac-canafe.gc.ca/', NULL, NULL, 'Suspicious transactions', 125, 108, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-022', 'FINTRAC_EFTR', 'Electronic Funds Transfer Report', 'REG-005', NULL, 'PCMLTFA Section 9.3', 'EVENT_DRIVEN', '5 business days', 'XML', 'FINTRAC Web Reporting', 'https://www.fintrac-canafe.gc.ca/', 10000, 'CAD', 'EFT >= CAD 10,000', 88, 75, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-023', 'FINTRAC_TPR', 'Terrorist Property Report', 'REG-005', NULL, 'Criminal Code Section 83.1', 'IMMEDIATE', 'Immediately', 'XML', 'FINTRAC Web Reporting', 'https://www.fintrac-canafe.gc.ca/', NULL, NULL, 'Terrorist property', 62, 55, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

    -- IRS/OECD (4 reports)
    ('RPT-030', 'FATCA_8966', 'FATCA Form 8966', 'REG-002', 'Form 8966', 'IRC 1471-1474', 'ANNUAL', 'March 31', 'XML', 'IDES', 'https://www.irs.gov/businesses/corporations/fatca-ides-technical-faqs', NULL, NULL, 'US reportable accounts', 97, 85, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-031', 'FATCA_POOL', 'FATCA Pool Report', 'REG-002', NULL, 'IRC 1471-1474', 'ANNUAL', 'March 31', 'XML', 'IDES', 'https://www.irs.gov/businesses/corporations/fatca-ides-technical-faqs', NULL, NULL, 'Pooled reporting', 67, 58, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-032', 'OECD_CRS', 'Common Reporting Standard', 'REG-009', NULL, 'OECD CRS', 'ANNUAL', 'Varies by jurisdiction', 'XML', 'Varies', NULL, NULL, NULL, 'Reportable accounts', 108, 92, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-033', 'OECD_CRS_CP', 'CRS Controlling Person Report', 'REG-009', NULL, 'OECD CRS', 'ANNUAL', 'Varies by jurisdiction', 'XML', 'Varies', NULL, NULL, NULL, 'Controlling persons', 85, 72, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

    -- EBA (1 report)
    ('RPT-040', 'EBA_PSD2_FRAUD', 'PSD2 Payment Fraud Statistical Report', 'REG-006', NULL, 'PSD2 2015/2366', 'SEMI_ANNUAL', 'End of June/December', 'XML', 'NCA Portal', NULL, NULL, NULL, 'Payment fraud statistics', 87, 74, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

    -- ESMA (1 payment-relevant report + 2 securities/trade reports marked inactive for payments)
    -- NOTE: MiFID II and EMIR are securities/derivatives trade reports, NOT payment reports
    -- They are included for completeness but marked with is_active=FALSE for payment processing
    ('RPT-041', 'ESMA_MIFID_II', 'MiFID II Transaction Report', 'REG-007', NULL, 'MiFIR Article 26', 'DAILY', 'T+1', 'XML', 'ARM', NULL, NULL, NULL, 'SECURITIES/TRADE - Not payment-relevant', 142, 125, FALSE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-042', 'ESMA_EMIR', 'EMIR Trade Report', 'REG-007', NULL, 'EMIR Article 9', 'DAILY', 'T+1', 'XML', 'Trade Repository', NULL, NULL, NULL, 'SECURITIES/TRADE - Not payment-relevant', 156, 138, FALSE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-043', 'ESMA_MAR_STOR', 'Suspicious Transaction and Order Report', 'REG-007', NULL, 'MAR Article 16', 'EVENT_DRIVEN', 'Without delay', 'XML', 'NCA Portal', NULL, NULL, NULL, 'Market abuse suspicion', 98, 85, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

    -- UK NCA (2 reports)
    ('RPT-050', 'UK_SAR', 'UK Suspicious Activity Report', 'REG-008', NULL, 'POCA 2002, TA 2000', 'EVENT_DRIVEN', 'As soon as practicable', 'XML', 'SAR Online', 'https://www.ukciu.gov.uk/', NULL, NULL, 'Suspicious activity', 122, 105, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-051', 'UK_DAML_SAR', 'Defence Against Money Laundering SAR', 'REG-008', NULL, 'POCA 2002 Section 338', 'EVENT_DRIVEN', 'Before proceeding', 'XML', 'SAR Online', 'https://www.ukciu.gov.uk/', NULL, NULL, 'Consent request', 132, 115, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

    -- APAC (3 STR reports - filed with respective FIUs)
    -- Note: HKMA/MAS are supervisory authorities; JFIU/STRO are where STRs are actually filed
    ('RPT-060', 'JFIU_STR', 'Hong Kong Suspicious Transaction Report', 'REG-010', NULL, 'AMLO Cap. 615 (HKMA supervised)', 'EVENT_DRIVEN', 'As soon as practicable', 'XML', 'JFIU Portal', 'https://www.jfiu.gov.hk/', NULL, NULL, 'Suspicious transactions (HK)', 105, 92, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-061', 'STRO_STR', 'Singapore Suspicious Transaction Report', 'REG-011', NULL, 'CDSA Section 39 (MAS supervised)', 'EVENT_DRIVEN', 'As soon as practicable', 'XML', 'STRO Portal', 'https://www.police.gov.sg/stro', NULL, NULL, 'Suspicious transactions (SG)', 112, 98, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('RPT-062', 'JAFIC_STR', 'Japan Suspicious Transaction Report', 'REG-012', NULL, 'Act on Prevention of Transfer of Criminal Proceeds', 'EVENT_DRIVEN', 'Promptly', 'XML', 'JAFIC Portal', 'https://www.npa.go.jp/sosikihanzai/jafic/', NULL, NULL, 'Suspicious transactions (JP)', 98, 85, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

    -- OFAC (1 report)
    ('RPT-070', 'OFAC_BLOCKING', 'OFAC Blocked Property Report', 'REG-003', NULL, '31 CFR Part 501', 'EVENT_DRIVEN', '10 business days', 'PDF/Online', 'OFAC Reporting', 'https://ofac.treasury.gov/', NULL, NULL, 'Blocked transactions', 72, 62, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

    -- Multi-jurisdiction (1 report)
    ('RPT-080', 'TERRORIST_PROPERTY', 'Terrorist Property Report', 'REG-009', NULL, 'UN SCR', 'IMMEDIATE', 'Immediately', 'Varies', 'National FIU', NULL, NULL, NULL, 'Terrorist property', 62, 55, TRUE, '2020-01-01', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

-- -----------------------------------------------------------------------------
-- Regulatory Requirement Master
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS regulatory.requirement (
    requirement_id STRING NOT NULL,
    report_type_id STRING NOT NULL,

    -- Identification
    requirement_code STRING NOT NULL,
    requirement_title STRING NOT NULL,
    requirement_description STRING,

    -- Classification
    category STRING NOT NULL COMMENT 'ELIGIBILITY, FIELD, VALIDATION, FORMAT, TIMING, SUBMISSION',
    criticality STRING NOT NULL COMMENT 'MANDATORY, RECOMMENDED, OPTIONAL, CONDITIONAL',

    -- CDM Mapping
    cdm_entity STRING COMMENT 'Primary CDM entity',
    cdm_field STRING COMMENT 'Primary CDM field',
    cdm_field_path STRING COMMENT 'Full JSON path if nested',

    -- Source Mapping (for lineage)
    source_systems ARRAY<STRING>,
    source_fields ARRAY<STRING>,

    -- Transformation
    transformation_logic STRING,
    validation_rule STRING,
    default_value STRING,

    -- Dependencies
    depends_on ARRAY<STRING> COMMENT 'Other requirement IDs this depends on',

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    version STRING DEFAULT '1.0',
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    last_updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

    CONSTRAINT pk_requirement PRIMARY KEY (requirement_id),
    CONSTRAINT fk_requirement_report FOREIGN KEY (report_type_id) REFERENCES regulatory.report_type(report_type_id)
)
USING DELTA
PARTITIONED BY (report_type_id)
COMMENT 'Master table of all regulatory requirements';

-- -----------------------------------------------------------------------------
-- Requirement to CDM Field Mapping (Traceability)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS regulatory.requirement_cdm_mapping (
    mapping_id STRING NOT NULL,
    requirement_id STRING NOT NULL,

    -- CDM Target
    cdm_entity STRING NOT NULL,
    cdm_field STRING NOT NULL,
    cdm_field_path STRING,
    cdm_data_type STRING,

    -- Mapping Details
    mapping_type STRING NOT NULL COMMENT 'DIRECT, DERIVED, LOOKUP, AGGREGATED, CONDITIONAL',
    transformation_logic STRING,

    -- Source (for lineage)
    source_system STRING,
    source_table STRING,
    source_field STRING,
    source_field_path STRING,

    -- Validation
    validation_rule STRING,
    nullable BOOLEAN DEFAULT TRUE,
    default_value STRING,

    -- Coverage
    coverage_percentage DECIMAL(5,2) COMMENT 'Percentage of source data that maps',
    quality_score DECIMAL(5,2),

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    last_updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

    CONSTRAINT pk_req_cdm_mapping PRIMARY KEY (mapping_id),
    CONSTRAINT fk_mapping_requirement FOREIGN KEY (requirement_id) REFERENCES regulatory.requirement(requirement_id)
)
USING DELTA
PARTITIONED BY (cdm_entity)
COMMENT 'Maps regulatory requirements to CDM fields for traceability';

-- =============================================================================
-- OPERATIONAL TABLES: Eligibility & Filing Status
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Transaction Regulatory Eligibility (Real-time)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS regulatory.transaction_eligibility (
    transaction_id STRING NOT NULL,
    payment_id STRING NOT NULL,
    evaluation_timestamp TIMESTAMP NOT NULL,

    -- FinCEN (US)
    fincen_ctr_eligible BOOLEAN DEFAULT FALSE,
    fincen_ctr_reason STRING,
    fincen_sar_eligible BOOLEAN DEFAULT FALSE,
    fincen_sar_indicators ARRAY<STRING>,
    fincen_8300_eligible BOOLEAN DEFAULT FALSE,
    fincen_cmir_eligible BOOLEAN DEFAULT FALSE,

    -- AUSTRAC (Australia)
    austrac_ifti_eligible BOOLEAN DEFAULT FALSE,
    austrac_ifti_direction STRING COMMENT 'IN, OUT',
    austrac_ttr_eligible BOOLEAN DEFAULT FALSE,
    austrac_smr_eligible BOOLEAN DEFAULT FALSE,
    austrac_smr_indicators ARRAY<STRING>,

    -- FINTRAC (Canada)
    fintrac_lctr_eligible BOOLEAN DEFAULT FALSE,
    fintrac_str_eligible BOOLEAN DEFAULT FALSE,
    fintrac_eftr_eligible BOOLEAN DEFAULT FALSE,
    fintrac_tpr_eligible BOOLEAN DEFAULT FALSE,

    -- IRS/OECD (Tax)
    fatca_8966_eligible BOOLEAN DEFAULT FALSE,
    fatca_pool_eligible BOOLEAN DEFAULT FALSE,
    crs_eligible BOOLEAN DEFAULT FALSE,
    crs_jurisdictions ARRAY<STRING>,

    -- EBA/ESMA (EU) - Payment-relevant only
    psd2_fraud_eligible BOOLEAN DEFAULT FALSE,
    mar_stor_eligible BOOLEAN DEFAULT FALSE,
    -- NOTE: MiFID II and EMIR are securities/trade reports - not applicable for payments
    -- Removed: mifid_ii_eligible, emir_eligible

    -- UK NCA
    uk_sar_eligible BOOLEAN DEFAULT FALSE,
    uk_daml_sar_eligible BOOLEAN DEFAULT FALSE,

    -- APAC (Filed with respective FIUs, supervised by HKMA/MAS)
    jfiu_str_eligible BOOLEAN DEFAULT FALSE COMMENT 'Hong Kong - filed with JFIU',
    stro_str_eligible BOOLEAN DEFAULT FALSE COMMENT 'Singapore - filed with STRO',
    jafic_str_eligible BOOLEAN DEFAULT FALSE COMMENT 'Japan - filed with JAFIC',

    -- OFAC
    ofac_blocking_eligible BOOLEAN DEFAULT FALSE,
    ofac_blocking_reason STRING,

    -- Multi-jurisdiction
    terrorist_property_eligible BOOLEAN DEFAULT FALSE,

    -- Computed Amounts (for threshold comparison)
    amount_usd DECIMAL(18,4),
    amount_aud DECIMAL(18,4),
    amount_cad DECIMAL(18,4),
    amount_gbp DECIMAL(18,4),
    amount_eur DECIMAL(18,4),
    amount_hkd DECIMAL(18,4),
    amount_sgd DECIMAL(18,4),
    amount_jpy DECIMAL(18,4),

    -- Risk Indicators
    cash_transaction BOOLEAN DEFAULT FALSE,
    cross_border BOOLEAN DEFAULT FALSE,
    pep_involved BOOLEAN DEFAULT FALSE,
    sanctions_hit BOOLEAN DEFAULT FALSE,
    structuring_indicator BOOLEAN DEFAULT FALSE,

    -- Metadata
    rules_version STRING,
    partition_date DATE NOT NULL,

    CONSTRAINT pk_txn_eligibility PRIMARY KEY (transaction_id, evaluation_timestamp)
)
USING DELTA
PARTITIONED BY (partition_date)
CLUSTER BY (payment_id, fincen_ctr_eligible, austrac_ifti_eligible)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
COMMENT 'Real-time regulatory eligibility flags for each transaction';

-- -----------------------------------------------------------------------------
-- Regulatory Filing Status
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS regulatory.filing_status (
    filing_id STRING NOT NULL,
    report_type_id STRING NOT NULL,

    -- Reference
    payment_id STRING,
    party_id STRING,
    account_id STRING,

    -- Filing Details
    filing_date DATE NOT NULL,
    filing_period_start DATE,
    filing_period_end DATE,

    -- Status
    status STRING NOT NULL COMMENT 'PENDING, SUBMITTED, ACCEPTED, REJECTED, AMENDED',
    submission_timestamp TIMESTAMP,
    confirmation_number STRING,

    -- Amounts
    reported_amount DECIMAL(18,4),
    reported_currency STRING,

    -- Response
    regulator_response STRING,
    rejection_reason STRING,
    amendment_reason STRING,

    -- Audit
    submitted_by STRING,
    approved_by STRING,
    approval_timestamp TIMESTAMP,

    -- Metadata
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    last_updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

    CONSTRAINT pk_filing_status PRIMARY KEY (filing_id)
)
USING DELTA
PARTITIONED BY (report_type_id, filing_date)
COMMENT 'Tracks regulatory filing status';

-- =============================================================================
-- VIEWS FOR REQUIREMENT TRACEABILITY
-- =============================================================================

-- -----------------------------------------------------------------------------
-- View: Complete Requirement Traceability
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW regulatory.v_requirement_traceability AS
SELECT
    r.requirement_id,
    r.requirement_code,
    r.requirement_title,
    r.category,
    r.criticality,
    rt.report_code,
    rt.report_name,
    reg.regulator_code,
    reg.regulator_name,
    reg.jurisdiction,
    m.cdm_entity,
    m.cdm_field,
    m.cdm_field_path,
    m.mapping_type,
    m.source_system,
    m.source_table,
    m.source_field,
    m.transformation_logic,
    m.validation_rule,
    m.coverage_percentage,
    m.quality_score
FROM regulatory.requirement r
JOIN regulatory.report_type rt ON r.report_type_id = rt.report_type_id
JOIN regulatory.regulator reg ON rt.regulator_id = reg.regulator_id
LEFT JOIN regulatory.requirement_cdm_mapping m ON r.requirement_id = m.requirement_id
WHERE r.is_active = TRUE
  AND rt.is_active = TRUE
  AND reg.is_active = TRUE;

-- -----------------------------------------------------------------------------
-- View: CDM Field to Requirements (Impact Analysis)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW regulatory.v_cdm_field_requirements AS
SELECT
    m.cdm_entity,
    m.cdm_field,
    COUNT(DISTINCT r.requirement_id) AS requirement_count,
    COUNT(DISTINCT rt.report_type_id) AS report_count,
    COUNT(DISTINCT reg.regulator_id) AS regulator_count,
    COLLECT_SET(rt.report_code) AS affected_reports,
    COLLECT_SET(reg.regulator_code) AS affected_regulators,
    COLLECT_SET(reg.jurisdiction) AS affected_jurisdictions,
    MAX(CASE WHEN r.criticality = 'MANDATORY' THEN 1 ELSE 0 END) AS has_mandatory_requirement
FROM regulatory.requirement_cdm_mapping m
JOIN regulatory.requirement r ON m.requirement_id = r.requirement_id
JOIN regulatory.report_type rt ON r.report_type_id = rt.report_type_id
JOIN regulatory.regulator reg ON rt.regulator_id = reg.regulator_id
WHERE m.is_active = TRUE
GROUP BY m.cdm_entity, m.cdm_field;

-- -----------------------------------------------------------------------------
-- View: Eligibility Summary by Report
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW regulatory.v_eligibility_summary AS
SELECT
    partition_date,
    -- US (FinCEN)
    SUM(CASE WHEN fincen_ctr_eligible THEN 1 ELSE 0 END) AS ctr_eligible_count,
    SUM(CASE WHEN fincen_sar_eligible THEN 1 ELSE 0 END) AS fincen_sar_eligible_count,
    -- Australia (AUSTRAC)
    SUM(CASE WHEN austrac_ifti_eligible THEN 1 ELSE 0 END) AS ifti_eligible_count,
    SUM(CASE WHEN austrac_ttr_eligible THEN 1 ELSE 0 END) AS ttr_eligible_count,
    SUM(CASE WHEN austrac_smr_eligible THEN 1 ELSE 0 END) AS smr_eligible_count,
    -- Canada (FINTRAC)
    SUM(CASE WHEN fintrac_lctr_eligible THEN 1 ELSE 0 END) AS lctr_eligible_count,
    SUM(CASE WHEN fintrac_str_eligible THEN 1 ELSE 0 END) AS fintrac_str_eligible_count,
    SUM(CASE WHEN fintrac_eftr_eligible THEN 1 ELSE 0 END) AS eftr_eligible_count,
    -- Tax (FATCA/CRS)
    SUM(CASE WHEN fatca_8966_eligible THEN 1 ELSE 0 END) AS fatca_eligible_count,
    SUM(CASE WHEN crs_eligible THEN 1 ELSE 0 END) AS crs_eligible_count,
    -- EU (EBA/ESMA - payment-relevant only)
    SUM(CASE WHEN psd2_fraud_eligible THEN 1 ELSE 0 END) AS psd2_eligible_count,
    SUM(CASE WHEN mar_stor_eligible THEN 1 ELSE 0 END) AS mar_stor_eligible_count,
    -- UK (NCA)
    SUM(CASE WHEN uk_sar_eligible THEN 1 ELSE 0 END) AS uk_sar_eligible_count,
    -- APAC (Filed with FIUs)
    SUM(CASE WHEN jfiu_str_eligible THEN 1 ELSE 0 END) AS jfiu_str_eligible_count,  -- Hong Kong
    SUM(CASE WHEN stro_str_eligible THEN 1 ELSE 0 END) AS stro_str_eligible_count,  -- Singapore
    SUM(CASE WHEN jafic_str_eligible THEN 1 ELSE 0 END) AS jafic_str_eligible_count, -- Japan
    -- Sanctions (OFAC)
    SUM(CASE WHEN ofac_blocking_eligible THEN 1 ELSE 0 END) AS ofac_eligible_count,
    -- Totals
    COUNT(*) AS total_transactions
FROM regulatory.transaction_eligibility
GROUP BY partition_date;

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

-- Grant read access to analytics users
-- GRANT SELECT ON SCHEMA regulatory TO `analytics_users`;

-- Grant full access to compliance team
-- GRANT ALL PRIVILEGES ON SCHEMA regulatory TO `compliance_team`;
