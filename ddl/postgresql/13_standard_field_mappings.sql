-- =============================================================================
-- GPS CDM - Standard Field Definitions & Mapping Documentation
-- =============================================================================
-- This schema provides a source of truth for payment standard fields and tracks
-- mapping coverage from Standard → Bronze → Silver → Gold.
--
-- Key Tables:
-- 1. mapping.standard_fields - Official fields from payment standards (ISO 20022, SWIFT, etc.)
-- 2. Enhanced message_formats - Adds country, standard_name metadata
-- 3. Views for unified mapping documentation and coverage metrics
-- =============================================================================

-- =============================================================================
-- Enhance Message Formats Table with Additional Metadata
-- =============================================================================
ALTER TABLE mapping.message_formats
    ADD COLUMN IF NOT EXISTS country VARCHAR(50),
    ADD COLUMN IF NOT EXISTS standard_name VARCHAR(100),
    ADD COLUMN IF NOT EXISTS standard_version VARCHAR(50),
    ADD COLUMN IF NOT EXISTS standard_url TEXT,
    ADD COLUMN IF NOT EXISTS governing_body VARCHAR(100);

COMMENT ON COLUMN mapping.message_formats.country IS 'Country or region where this format is used (e.g., US, EU, UK, GLOBAL)';
COMMENT ON COLUMN mapping.message_formats.standard_name IS 'Official standard name (e.g., ISO 20022, SWIFT MT, NACHA)';
COMMENT ON COLUMN mapping.message_formats.standard_version IS 'Version of the standard (e.g., 2019, SRG 2023)';
COMMENT ON COLUMN mapping.message_formats.standard_url IS 'URL to official standard documentation';
COMMENT ON COLUMN mapping.message_formats.governing_body IS 'Organization that maintains the standard (e.g., ISO, SWIFT, Federal Reserve)';

-- Update existing message formats with country and standard metadata
UPDATE mapping.message_formats SET
    country = 'GLOBAL',
    standard_name = 'ISO 20022',
    governing_body = 'ISO TC 68'
WHERE format_category = 'ISO20022';

UPDATE mapping.message_formats SET
    country = 'GLOBAL',
    standard_name = 'SWIFT MT',
    governing_body = 'SWIFT'
WHERE format_category = 'SWIFT_MT';

UPDATE mapping.message_formats SET
    country = CASE
        WHEN format_id IN ('FEDWIRE', 'CHIPS', 'ACH') THEN 'US'
        WHEN format_id LIKE 'SEPA%' THEN 'EU'
        WHEN format_id IN ('BACS', 'CHAPS', 'FPS') THEN 'UK'
        WHEN format_id = 'NPP' THEN 'AU'
        ELSE 'GLOBAL'
    END,
    standard_name = CASE
        WHEN format_id = 'FEDWIRE' THEN 'Fedwire Funds Service'
        WHEN format_id = 'CHIPS' THEN 'CHIPS'
        WHEN format_id = 'ACH' THEN 'NACHA'
        WHEN format_id LIKE 'SEPA%' THEN 'SEPA Rulebook'
        WHEN format_id IN ('BACS', 'CHAPS', 'FPS') THEN 'UK Payments'
        WHEN format_id = 'NPP' THEN 'NPP Australia'
        ELSE format_id
    END,
    governing_body = CASE
        WHEN format_id = 'FEDWIRE' THEN 'Federal Reserve'
        WHEN format_id = 'CHIPS' THEN 'The Clearing House'
        WHEN format_id = 'ACH' THEN 'NACHA'
        WHEN format_id LIKE 'SEPA%' THEN 'European Payments Council'
        WHEN format_id IN ('BACS', 'CHAPS', 'FPS') THEN 'Pay.UK'
        WHEN format_id = 'NPP' THEN 'NPP Australia'
        ELSE NULL
    END
WHERE format_category = 'REGIONAL';

-- =============================================================================
-- Standard Fields Table - Source of Truth from Payment Standards
-- =============================================================================
-- This table contains the official field definitions from each payment standard.
-- It serves as the master reference for reconciliation and coverage tracking.
CREATE TABLE IF NOT EXISTS mapping.standard_fields (
    standard_field_id SERIAL PRIMARY KEY,
    format_id VARCHAR(50) NOT NULL REFERENCES mapping.message_formats(format_id),

    -- Standard Field Identification
    field_name VARCHAR(200) NOT NULL,              -- Official field name from standard (e.g., 'MsgId', 'CreDtTm')
    field_path VARCHAR(500) NOT NULL,              -- Full path in message (e.g., 'CstmrCdtTrfInitn/GrpHdr/MsgId')
    field_tag VARCHAR(50),                          -- Tag number for MT messages (e.g., ':20:', ':32A:')

    -- Field Metadata from Standard
    field_description TEXT,                         -- Official description from standard documentation
    data_type VARCHAR(50) NOT NULL,                 -- Data type from standard (e.g., 'Max35Text', 'ISODateTime', 'ActiveCurrencyAndAmount')
    min_length INTEGER,                             -- Minimum length if specified
    max_length INTEGER,                             -- Maximum length if specified
    allowed_values TEXT,                            -- Enumerated values or pattern (e.g., 'CRED|DEBT', '[A-Z]{3}')
    is_mandatory BOOLEAN DEFAULT FALSE,             -- Whether field is mandatory in the standard

    -- Field Classification
    field_category VARCHAR(50),                     -- Logical grouping (e.g., 'Header', 'Debtor', 'Creditor', 'Amount', 'Reference')
    business_component VARCHAR(100),                -- Business component this field belongs to

    -- Versioning
    introduced_version VARCHAR(20),                 -- Version when field was introduced
    deprecated_version VARCHAR(20),                 -- Version when field was deprecated (if applicable)

    -- Tracking
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) DEFAULT 'SYSTEM',

    UNIQUE(format_id, field_path)
);

CREATE INDEX IF NOT EXISTS idx_standard_fields_format
    ON mapping.standard_fields(format_id, is_active);
CREATE INDEX IF NOT EXISTS idx_standard_fields_category
    ON mapping.standard_fields(format_id, field_category);

COMMENT ON TABLE mapping.standard_fields IS 'Official field definitions from payment standards - source of truth for mapping reconciliation';

-- =============================================================================
-- Enhance Silver Field Mappings with Standard Field Reference
-- =============================================================================
ALTER TABLE mapping.silver_field_mappings
    ADD COLUMN IF NOT EXISTS standard_field_id INTEGER REFERENCES mapping.standard_fields(standard_field_id),
    ADD COLUMN IF NOT EXISTS field_description TEXT,
    ADD COLUMN IF NOT EXISTS is_user_modified BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100) DEFAULT 'SYSTEM';

COMMENT ON COLUMN mapping.silver_field_mappings.standard_field_id IS 'Reference to official standard field definition';
COMMENT ON COLUMN mapping.silver_field_mappings.field_description IS 'Description of this mapping (can override standard description)';
COMMENT ON COLUMN mapping.silver_field_mappings.is_user_modified IS 'True if user has modified this mapping (preserved during sync)';

-- =============================================================================
-- Enhance Gold Field Mappings with Additional Metadata
-- =============================================================================
ALTER TABLE mapping.gold_field_mappings
    ADD COLUMN IF NOT EXISTS purpose_code VARCHAR(50),
    ADD COLUMN IF NOT EXISTS field_description TEXT,
    ADD COLUMN IF NOT EXISTS is_user_modified BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100) DEFAULT 'SYSTEM';

COMMENT ON COLUMN mapping.gold_field_mappings.purpose_code IS 'Business purpose code for this gold mapping (e.g., REGULATORY, REPORTING, ANALYTICS)';
COMMENT ON COLUMN mapping.gold_field_mappings.field_description IS 'Description of this gold mapping';

-- =============================================================================
-- View: Unified Mappings Documentation
-- =============================================================================
-- This view provides the complete mapping documentation in a single query,
-- joining standard fields with silver and gold mappings.
-- NOTE: Excludes 'complex' data type fields as they are containers, not leaf fields.
CREATE OR REPLACE VIEW mapping.v_mappings_documentation AS
SELECT
    -- Standard/Format Info
    mf.standard_name,
    mf.country,
    mf.format_id AS message_format,
    mf.format_name AS message_format_description,
    mf.format_category,
    mf.governing_body,

    -- Standard Field Info
    sf.standard_field_id,
    sf.field_name AS standard_field_name,
    sf.field_description AS standard_field_description,
    sf.data_type AS standard_field_data_type,
    sf.allowed_values AS standard_field_allowed_values,
    sf.field_path AS standard_field_path,
    sf.field_tag AS standard_field_tag,
    sf.is_mandatory AS standard_field_mandatory,
    sf.field_category,

    -- Bronze Info (derived from standard field path)
    mf.bronze_table,
    sf.field_path AS bronze_source_path,  -- In Bronze, we store raw content; path is the accessor

    -- Silver Mapping Info
    sm.mapping_id AS silver_mapping_id,
    'silver.' || mf.silver_table AS silver_table,
    sm.target_column AS silver_column,
    sm.data_type AS silver_data_type,
    sm.max_length AS silver_max_length,
    sm.source_path AS silver_source_path,
    sm.transform_function AS silver_transform,
    sm.is_required AS silver_is_required,
    CASE WHEN sm.mapping_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_mapped_to_silver,

    -- Gold Mapping Info
    gm.mapping_id AS gold_mapping_id,
    'gold.' || gm.gold_table AS gold_table,
    gm.gold_column,
    gm.data_type AS gold_data_type,
    gm.entity_role AS gold_entity_role,
    gm.purpose_code AS gold_purpose_code,
    gm.source_expression AS gold_source_expression,
    gm.transform_expression AS gold_transform,
    CASE WHEN gm.mapping_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_mapped_to_gold,

    -- Metadata
    sf.is_active,
    GREATEST(
        COALESCE(sf.updated_at, '1970-01-01'),
        COALESCE(sm.updated_at, '1970-01-01'),
        COALESCE(gm.updated_at, '1970-01-01')
    ) AS last_updated

FROM mapping.message_formats mf
LEFT JOIN mapping.standard_fields sf ON mf.format_id = sf.format_id
    AND sf.is_active = TRUE
    AND sf.data_type <> 'complex'  -- Exclude complex container types
LEFT JOIN mapping.silver_field_mappings sm ON sf.format_id = sm.format_id
    AND (sf.standard_field_id = sm.standard_field_id OR sf.field_path = sm.source_path)
    AND sm.is_active = TRUE
LEFT JOIN mapping.gold_field_mappings gm ON sm.format_id = gm.format_id
    AND sm.target_column = gm.source_expression
    AND gm.is_active = TRUE
WHERE mf.is_active = TRUE
ORDER BY mf.format_category, mf.format_id, sf.field_category, sf.field_name;

COMMENT ON VIEW mapping.v_mappings_documentation IS 'Unified view of all field mappings from Standard → Bronze → Silver → Gold (excludes complex container types)';

-- =============================================================================
-- View: Mapping Coverage Summary
-- =============================================================================
-- NOTE: Excludes 'complex' data type fields as they are containers, not leaf fields.
CREATE OR REPLACE VIEW mapping.v_mapping_coverage AS
SELECT
    mf.format_id,
    mf.format_name,
    mf.standard_name,
    mf.country,
    COUNT(DISTINCT sf.standard_field_id) AS total_standard_fields,
    COUNT(DISTINCT CASE WHEN sf.is_mandatory THEN sf.standard_field_id END) AS mandatory_fields,
    COUNT(DISTINCT sm.mapping_id) AS mapped_to_silver,
    COUNT(DISTINCT gm.mapping_id) AS mapped_to_gold,
    ROUND(
        COUNT(DISTINCT sm.mapping_id)::NUMERIC / NULLIF(COUNT(DISTINCT sf.standard_field_id), 0) * 100,
        1
    ) AS silver_coverage_pct,
    ROUND(
        COUNT(DISTINCT gm.mapping_id)::NUMERIC / NULLIF(COUNT(DISTINCT sm.mapping_id), 0) * 100,
        1
    ) AS gold_coverage_pct,
    COUNT(DISTINCT sf.standard_field_id) - COUNT(DISTINCT sm.mapping_id) AS unmapped_fields
FROM mapping.message_formats mf
LEFT JOIN mapping.standard_fields sf ON mf.format_id = sf.format_id
    AND sf.is_active = TRUE
    AND sf.data_type <> 'complex'  -- Exclude complex container types
LEFT JOIN mapping.silver_field_mappings sm ON sf.format_id = sm.format_id
    AND (sf.standard_field_id = sm.standard_field_id OR sf.field_path = sm.source_path)
    AND sm.is_active = TRUE
LEFT JOIN mapping.gold_field_mappings gm ON sm.format_id = gm.format_id
    AND sm.target_column = gm.source_expression
    AND gm.is_active = TRUE
WHERE mf.is_active = TRUE
GROUP BY mf.format_id, mf.format_name, mf.standard_name, mf.country
ORDER BY mf.format_category, mf.format_id;

COMMENT ON VIEW mapping.v_mapping_coverage IS 'Coverage metrics showing how many standard fields are mapped to Silver and Gold (excludes complex container types)';

-- =============================================================================
-- View: Unmapped Standard Fields
-- =============================================================================
-- NOTE: Excludes 'complex' data type fields as they are containers, not leaf fields.
CREATE OR REPLACE VIEW mapping.v_unmapped_fields AS
SELECT
    mf.format_id,
    mf.format_name,
    sf.field_name,
    sf.field_path,
    sf.field_description,
    sf.data_type,
    sf.is_mandatory,
    sf.field_category,
    'NOT_MAPPED_TO_SILVER' AS gap_type
FROM mapping.message_formats mf
JOIN mapping.standard_fields sf ON mf.format_id = sf.format_id
    AND sf.is_active = TRUE
    AND sf.data_type <> 'complex'  -- Exclude complex container types
LEFT JOIN mapping.silver_field_mappings sm ON sf.format_id = sm.format_id
    AND (sf.standard_field_id = sm.standard_field_id OR sf.field_path = sm.source_path)
    AND sm.is_active = TRUE
WHERE mf.is_active = TRUE AND sm.mapping_id IS NULL

UNION ALL

SELECT
    mf.format_id,
    mf.format_name,
    sm.target_column AS field_name,
    sm.source_path AS field_path,
    sm.field_description,
    sm.data_type,
    sm.is_required AS is_mandatory,
    NULL AS field_category,
    'NOT_MAPPED_TO_GOLD' AS gap_type
FROM mapping.message_formats mf
JOIN mapping.silver_field_mappings sm ON mf.format_id = sm.format_id AND sm.is_active = TRUE
LEFT JOIN mapping.gold_field_mappings gm ON sm.format_id = gm.format_id
    AND sm.target_column = gm.source_expression
    AND gm.is_active = TRUE
WHERE mf.is_active = TRUE AND gm.mapping_id IS NULL

ORDER BY format_id, gap_type, field_name;

COMMENT ON VIEW mapping.v_unmapped_fields IS 'Lists standard fields not yet mapped to Silver or Silver fields not mapped to Gold (excludes complex container types)';

-- =============================================================================
-- Insert Sample Standard Fields for pain.001
-- =============================================================================
INSERT INTO mapping.standard_fields
    (format_id, field_name, field_path, field_description, data_type, max_length, is_mandatory, field_category)
VALUES
    -- Group Header
    ('pain.001', 'MsgId', 'CstmrCdtTrfInitn/GrpHdr/MsgId', 'Point to point reference assigned by the instructing party to identify the message', 'Max35Text', 35, TRUE, 'Header'),
    ('pain.001', 'CreDtTm', 'CstmrCdtTrfInitn/GrpHdr/CreDtTm', 'Date and time at which the message was created', 'ISODateTime', NULL, TRUE, 'Header'),
    ('pain.001', 'NbOfTxs', 'CstmrCdtTrfInitn/GrpHdr/NbOfTxs', 'Number of individual transactions in the message', 'Max15NumericText', 15, TRUE, 'Header'),
    ('pain.001', 'CtrlSum', 'CstmrCdtTrfInitn/GrpHdr/CtrlSum', 'Total of all amounts in the message', 'DecimalNumber', NULL, FALSE, 'Header'),
    ('pain.001', 'InitgPty/Nm', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Nm', 'Name of the party initiating the payment', 'Max140Text', 140, FALSE, 'Header'),
    ('pain.001', 'InitgPty/Id', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id', 'Identification of the initiating party', 'Max35Text', 35, FALSE, 'Header'),

    -- Payment Information
    ('pain.001', 'PmtInfId', 'CstmrCdtTrfInitn/PmtInf/PmtInfId', 'Unique identification of the payment information block', 'Max35Text', 35, TRUE, 'PaymentInfo'),
    ('pain.001', 'PmtMtd', 'CstmrCdtTrfInitn/PmtInf/PmtMtd', 'Payment method - TRF for credit transfer', 'PaymentMethod3Code', 3, TRUE, 'PaymentInfo'),
    ('pain.001', 'BtchBookg', 'CstmrCdtTrfInitn/PmtInf/BtchBookg', 'Indicates if batch booking is requested', 'BatchBookingIndicator', NULL, FALSE, 'PaymentInfo'),
    ('pain.001', 'ReqdExctnDt', 'CstmrCdtTrfInitn/PmtInf/ReqdExctnDt', 'Date on which the payment is to be executed', 'ISODate', NULL, TRUE, 'PaymentInfo'),

    -- Debtor
    ('pain.001', 'Dbtr/Nm', 'CstmrCdtTrfInitn/PmtInf/Dbtr/Nm', 'Name of the debtor (payer)', 'Max140Text', 140, TRUE, 'Debtor'),
    ('pain.001', 'Dbtr/PstlAdr/StrtNm', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/StrtNm', 'Street name of debtor address', 'Max70Text', 70, FALSE, 'Debtor'),
    ('pain.001', 'Dbtr/PstlAdr/BldgNb', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/BldgNb', 'Building number of debtor address', 'Max16Text', 16, FALSE, 'Debtor'),
    ('pain.001', 'Dbtr/PstlAdr/PstCd', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/PstCd', 'Postal code of debtor address', 'Max16Text', 16, FALSE, 'Debtor'),
    ('pain.001', 'Dbtr/PstlAdr/TwnNm', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/TwnNm', 'Town/city name of debtor address', 'Max35Text', 35, FALSE, 'Debtor'),
    ('pain.001', 'Dbtr/PstlAdr/Ctry', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/Ctry', 'Country code of debtor address', 'CountryCode', 2, FALSE, 'Debtor'),
    ('pain.001', 'Dbtr/Id', 'CstmrCdtTrfInitn/PmtInf/Dbtr/Id', 'Identification of the debtor', 'Max35Text', 35, FALSE, 'Debtor'),

    -- Debtor Account
    ('pain.001', 'DbtrAcct/Id/IBAN', 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Id/IBAN', 'IBAN of the debtor account', 'IBAN2007Identifier', 34, FALSE, 'DebtorAccount'),
    ('pain.001', 'DbtrAcct/Id/Othr/Id', 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Id/Othr/Id', 'Other account identifier', 'Max34Text', 34, FALSE, 'DebtorAccount'),
    ('pain.001', 'DbtrAcct/Ccy', 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Ccy', 'Currency of the debtor account', 'ActiveOrHistoricCurrencyCode', 3, FALSE, 'DebtorAccount'),

    -- Debtor Agent
    ('pain.001', 'DbtrAgt/FinInstnId/BIC', 'CstmrCdtTrfInitn/PmtInf/DbtrAgt/FinInstnId/BIC', 'BIC of the debtor agent (bank)', 'BICIdentifier', 11, FALSE, 'DebtorAgent'),
    ('pain.001', 'DbtrAgt/FinInstnId/Nm', 'CstmrCdtTrfInitn/PmtInf/DbtrAgt/FinInstnId/Nm', 'Name of the debtor agent', 'Max140Text', 140, FALSE, 'DebtorAgent'),
    ('pain.001', 'DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'CstmrCdtTrfInitn/PmtInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'Clearing system member ID', 'Max35Text', 35, FALSE, 'DebtorAgent'),

    -- Credit Transfer Transaction Information
    ('pain.001', 'InstrId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtId/InstrId', 'Unique instruction identification', 'Max35Text', 35, FALSE, 'Transaction'),
    ('pain.001', 'EndToEndId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtId/EndToEndId', 'End-to-end identification assigned by initiating party', 'Max35Text', 35, TRUE, 'Transaction'),
    ('pain.001', 'UETR', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtId/UETR', 'Unique End-to-end Transaction Reference', 'UUIDv4Identifier', 36, FALSE, 'Transaction'),

    -- Amount
    ('pain.001', 'InstdAmt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Amt/InstdAmt', 'Amount to be transferred in the instructed currency', 'ActiveOrHistoricCurrencyAndAmount', NULL, TRUE, 'Amount'),
    ('pain.001', 'InstdAmt/@Ccy', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Amt/InstdAmt/@Ccy', 'Currency of the instructed amount', 'ActiveOrHistoricCurrencyCode', 3, TRUE, 'Amount'),
    ('pain.001', 'EqvtAmt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Amt/EqvtAmt/Amt', 'Equivalent amount in a different currency', 'ActiveOrHistoricCurrencyAndAmount', NULL, FALSE, 'Amount'),
    ('pain.001', 'XchgRate', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/XchgRateInf/XchgRate', 'Exchange rate between instructed and equivalent amounts', 'BaseOneRate', NULL, FALSE, 'Amount'),

    -- Creditor Agent
    ('pain.001', 'CdtrAgt/FinInstnId/BIC', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/BIC', 'BIC of the creditor agent (bank)', 'BICIdentifier', 11, FALSE, 'CreditorAgent'),
    ('pain.001', 'CdtrAgt/FinInstnId/Nm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/Nm', 'Name of the creditor agent', 'Max140Text', 140, FALSE, 'CreditorAgent'),
    ('pain.001', 'CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'Clearing system member ID of creditor agent', 'Max35Text', 35, FALSE, 'CreditorAgent'),

    -- Creditor
    ('pain.001', 'Cdtr/Nm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/Nm', 'Name of the creditor (beneficiary)', 'Max140Text', 140, TRUE, 'Creditor'),
    ('pain.001', 'Cdtr/PstlAdr/StrtNm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/StrtNm', 'Street name of creditor address', 'Max70Text', 70, FALSE, 'Creditor'),
    ('pain.001', 'Cdtr/PstlAdr/BldgNb', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/BldgNb', 'Building number of creditor address', 'Max16Text', 16, FALSE, 'Creditor'),
    ('pain.001', 'Cdtr/PstlAdr/PstCd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/PstCd', 'Postal code of creditor address', 'Max16Text', 16, FALSE, 'Creditor'),
    ('pain.001', 'Cdtr/PstlAdr/TwnNm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/TwnNm', 'Town/city name of creditor address', 'Max35Text', 35, FALSE, 'Creditor'),
    ('pain.001', 'Cdtr/PstlAdr/Ctry', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/Ctry', 'Country code of creditor address', 'CountryCode', 2, FALSE, 'Creditor'),
    ('pain.001', 'Cdtr/Id', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/Id', 'Identification of the creditor', 'Max35Text', 35, FALSE, 'Creditor'),

    -- Creditor Account
    ('pain.001', 'CdtrAcct/Id/IBAN', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Id/IBAN', 'IBAN of the creditor account', 'IBAN2007Identifier', 34, FALSE, 'CreditorAccount'),
    ('pain.001', 'CdtrAcct/Id/Othr/Id', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Id/Othr/Id', 'Other creditor account identifier', 'Max34Text', 34, FALSE, 'CreditorAccount'),
    ('pain.001', 'CdtrAcct/Ccy', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Ccy', 'Currency of the creditor account', 'ActiveOrHistoricCurrencyCode', 3, FALSE, 'CreditorAccount'),

    -- Purpose and Charges
    ('pain.001', 'Purp/Cd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Purp/Cd', 'Purpose code for the payment', 'ExternalPurpose1Code', 4, FALSE, 'Purpose'),
    ('pain.001', 'Purp/Prtry', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Purp/Prtry', 'Proprietary purpose code', 'Max35Text', 35, FALSE, 'Purpose'),
    ('pain.001', 'ChrgBr', 'CstmrCdtTrfInitn/PmtInf/ChrgBr', 'Charge bearer - who pays the charges', 'ChargeBearerType1Code', 4, FALSE, 'Charges'),

    -- Remittance Information
    ('pain.001', 'RmtInf/Ustrd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Ustrd', 'Unstructured remittance information', 'Max140Text', 140, FALSE, 'Remittance'),
    ('pain.001', 'RmtInf/Strd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd', 'Structured remittance information', 'StructuredRemittanceInformation', NULL, FALSE, 'Remittance'),

    -- Regulatory Reporting
    ('pain.001', 'RgltryRptg', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RgltryRptg', 'Regulatory reporting information', 'RegulatoryReporting', NULL, FALSE, 'Regulatory'),

    -- Ultimate Parties
    ('pain.001', 'UltmtDbtr/Nm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/UltmtDbtr/Nm', 'Name of ultimate debtor (original payer)', 'Max140Text', 140, FALSE, 'UltimateDebtor'),
    ('pain.001', 'UltmtDbtr/Id', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/UltmtDbtr/Id', 'Identification of ultimate debtor', 'Max35Text', 35, FALSE, 'UltimateDebtor'),
    ('pain.001', 'UltmtCdtr/Nm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/UltmtCdtr/Nm', 'Name of ultimate creditor (final beneficiary)', 'Max140Text', 140, FALSE, 'UltimateCreditor'),
    ('pain.001', 'UltmtCdtr/Id', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/UltmtCdtr/Id', 'Identification of ultimate creditor', 'Max35Text', 35, FALSE, 'UltimateCreditor')
ON CONFLICT (format_id, field_path) DO UPDATE SET
    field_name = EXCLUDED.field_name,
    field_description = EXCLUDED.field_description,
    data_type = EXCLUDED.data_type,
    max_length = EXCLUDED.max_length,
    is_mandatory = EXCLUDED.is_mandatory,
    field_category = EXCLUDED.field_category,
    updated_at = CURRENT_TIMESTAMP;

-- =============================================================================
-- Insert Sample Standard Fields for MT103
-- =============================================================================
INSERT INTO mapping.standard_fields
    (format_id, field_name, field_path, field_tag, field_description, data_type, max_length, is_mandatory, field_category, allowed_values)
VALUES
    -- Block 1 - Basic Header
    ('MT103', 'Sender BIC', 'Block1/LogicalTerminalAddress', NULL, 'BIC of the sending institution', 'BICIdentifier', 11, TRUE, 'Header', NULL),

    -- Block 2 - Application Header
    ('MT103', 'Receiver BIC', 'Block2/ReceiverAddress', NULL, 'BIC of the receiving institution', 'BICIdentifier', 11, TRUE, 'Header', NULL),

    -- Block 4 - Text Block
    ('MT103', 'Senders Reference', 'Block4/Tag20', ':20:', 'Senders reference number', 'Max16Text', 16, TRUE, 'Reference', NULL),
    ('MT103', 'Related Reference', 'Block4/Tag21', ':21:', 'Related reference (optional)', 'Max16Text', 16, FALSE, 'Reference', NULL),
    ('MT103', 'Bank Operation Code', 'Block4/Tag23B', ':23B:', 'Type of operation', 'Code', 4, TRUE, 'Transaction', 'CRED|CRTS|SPAY|SPRI|SSTD'),
    ('MT103', 'Instruction Code', 'Block4/Tag23E', ':23E:', 'Instruction code', 'Code', 4, FALSE, 'Transaction', 'CHQB|CORT|HOLD|INTC|PHOB|PHOI|PHON|REPA|SDVA|TELB|TELE|TELI'),
    ('MT103', 'Value Date/Currency/Amount', 'Block4/Tag32A', ':32A:', 'Value date, currency and settlement amount', 'DateTime+Currency+Amount', NULL, TRUE, 'Amount', NULL),
    ('MT103', 'Instructed Currency/Amount', 'Block4/Tag33B', ':33B:', 'Original instructed currency and amount', 'Currency+Amount', NULL, FALSE, 'Amount', NULL),
    ('MT103', 'Exchange Rate', 'Block4/Tag36', ':36:', 'Exchange rate applied', 'Rate', NULL, FALSE, 'Amount', NULL),
    ('MT103', 'Ordering Customer', 'Block4/Tag50a', ':50A:|:50F:|:50K:', 'Ordering customer (payer)', 'PartyIdentification', 140, TRUE, 'Debtor', NULL),
    ('MT103', 'Ordering Institution', 'Block4/Tag52a', ':52A:|:52D:', 'Ordering institution', 'PartyIdentification', 140, FALSE, 'DebtorAgent', NULL),
    ('MT103', 'Senders Correspondent', 'Block4/Tag53a', ':53A:|:53B:|:53D:', 'Senders correspondent bank', 'PartyIdentification', 140, FALSE, 'Correspondent', NULL),
    ('MT103', 'Receivers Correspondent', 'Block4/Tag54a', ':54A:|:54B:|:54D:', 'Receivers correspondent bank', 'PartyIdentification', 140, FALSE, 'Correspondent', NULL),
    ('MT103', 'Third Reimbursement Institution', 'Block4/Tag55a', ':55A:|:55B:|:55D:', 'Third reimbursement institution', 'PartyIdentification', 140, FALSE, 'Correspondent', NULL),
    ('MT103', 'Intermediary Institution', 'Block4/Tag56a', ':56A:|:56C:|:56D:', 'Intermediary institution', 'PartyIdentification', 140, FALSE, 'Intermediary', NULL),
    ('MT103', 'Account With Institution', 'Block4/Tag57a', ':57A:|:57B:|:57C:|:57D:', 'Account with institution (creditor agent)', 'PartyIdentification', 140, FALSE, 'CreditorAgent', NULL),
    ('MT103', 'Beneficiary Customer', 'Block4/Tag59', ':59:|:59A:|:59F:', 'Beneficiary customer (creditor)', 'PartyIdentification', 140, TRUE, 'Creditor', NULL),
    ('MT103', 'Remittance Information', 'Block4/Tag70', ':70:', 'Remittance information', 'Max140Text', 140, FALSE, 'Remittance', NULL),
    ('MT103', 'Details of Charges', 'Block4/Tag71A', ':71A:', 'Details of charges', 'Code', 3, TRUE, 'Charges', 'BEN|OUR|SHA'),
    ('MT103', 'Senders Charges', 'Block4/Tag71F', ':71F:', 'Senders charges', 'Currency+Amount', NULL, FALSE, 'Charges', NULL),
    ('MT103', 'Receivers Charges', 'Block4/Tag71G', ':71G:', 'Receivers charges', 'Currency+Amount', NULL, FALSE, 'Charges', NULL),
    ('MT103', 'Sender to Receiver Information', 'Block4/Tag72', ':72:', 'Sender to receiver information', 'Max210Text', 210, FALSE, 'Information', NULL),
    ('MT103', 'Regulatory Reporting', 'Block4/Tag77B', ':77B:', 'Regulatory reporting', 'Max105Text', 105, FALSE, 'Regulatory', NULL)
ON CONFLICT (format_id, field_path) DO UPDATE SET
    field_name = EXCLUDED.field_name,
    field_tag = EXCLUDED.field_tag,
    field_description = EXCLUDED.field_description,
    data_type = EXCLUDED.data_type,
    max_length = EXCLUDED.max_length,
    is_mandatory = EXCLUDED.is_mandatory,
    field_category = EXCLUDED.field_category,
    allowed_values = EXCLUDED.allowed_values,
    updated_at = CURRENT_TIMESTAMP;

-- =============================================================================
-- Insert Sample Standard Fields for FEDWIRE
-- =============================================================================
INSERT INTO mapping.standard_fields
    (format_id, field_name, field_path, field_tag, field_description, data_type, max_length, is_mandatory, field_category, allowed_values)
VALUES
    -- Type and Subtype
    ('FEDWIRE', 'Type Code', 'TypeSubType/TypeCode', '{1510}', 'Type of Fedwire message', 'Code', 2, TRUE, 'Header', '10|15|16'),
    ('FEDWIRE', 'Subtype Code', 'TypeSubType/SubTypeCode', '{1510}', 'Subtype of Fedwire message', 'Code', 2, TRUE, 'Header', '00|02|08'),

    -- IMAD/OMAD
    ('FEDWIRE', 'IMAD', 'MessageDisposition/IMAD', '{1520}', 'Input Message Accountability Data', 'IMACFormat', 22, TRUE, 'Reference', NULL),
    ('FEDWIRE', 'OMAD', 'MessageDisposition/OMAD', '{1120}', 'Output Message Accountability Data', 'OMACFormat', 22, FALSE, 'Reference', NULL),

    -- Amount
    ('FEDWIRE', 'Amount', 'Amount/Value', '{2000}', 'Transfer amount in cents', 'Amount', 12, TRUE, 'Amount', NULL),

    -- Sender Information
    ('FEDWIRE', 'Sender ABA', 'Sender/RoutingNumber', '{3100}', 'ABA routing number of sender', 'ABARoutingNumber', 9, TRUE, 'Sender', NULL),
    ('FEDWIRE', 'Sender Short Name', 'Sender/ShortName', '{3100}', 'Short name of sender FI', 'Max18Text', 18, FALSE, 'Sender', NULL),

    -- Receiver Information
    ('FEDWIRE', 'Receiver ABA', 'Receiver/RoutingNumber', '{3400}', 'ABA routing number of receiver', 'ABARoutingNumber', 9, TRUE, 'Receiver', NULL),
    ('FEDWIRE', 'Receiver Short Name', 'Receiver/ShortName', '{3400}', 'Short name of receiver FI', 'Max18Text', 18, FALSE, 'Receiver', NULL),

    -- Business Function
    ('FEDWIRE', 'Business Function Code', 'BusinessFunctionCode', '{3600}', 'Business function code', 'Code', 3, TRUE, 'Transaction', 'BTR|CTR|CTP|DRC|DRW|FFR|FFS|SVC'),

    -- Sender Reference
    ('FEDWIRE', 'Sender Reference', 'SenderReference', '{3320}', 'Sender supplied reference', 'Max16Text', 16, FALSE, 'Reference', NULL),

    -- Originator
    ('FEDWIRE', 'Originator Name', 'Originator/Name', '{5000}', 'Name of originator', 'Max35Text', 35, TRUE, 'Originator', NULL),
    ('FEDWIRE', 'Originator Account', 'Originator/AccountNumber', '{5000}', 'Account number of originator', 'Max34Text', 34, FALSE, 'Originator', NULL),
    ('FEDWIRE', 'Originator Address Line 1', 'Originator/Address/Line1', '{5000}', 'First line of originator address', 'Max35Text', 35, FALSE, 'Originator', NULL),
    ('FEDWIRE', 'Originator Address Line 2', 'Originator/Address/Line2', '{5000}', 'Second line of originator address', 'Max35Text', 35, FALSE, 'Originator', NULL),
    ('FEDWIRE', 'Originator Address Line 3', 'Originator/Address/Line3', '{5000}', 'Third line of originator address', 'Max35Text', 35, FALSE, 'Originator', NULL),

    -- Beneficiary
    ('FEDWIRE', 'Beneficiary Name', 'Beneficiary/Name', '{4200}', 'Name of beneficiary', 'Max35Text', 35, TRUE, 'Beneficiary', NULL),
    ('FEDWIRE', 'Beneficiary Account', 'Beneficiary/AccountNumber', '{4200}', 'Account number of beneficiary', 'Max34Text', 34, FALSE, 'Beneficiary', NULL),
    ('FEDWIRE', 'Beneficiary Address Line 1', 'Beneficiary/Address/Line1', '{4200}', 'First line of beneficiary address', 'Max35Text', 35, FALSE, 'Beneficiary', NULL),
    ('FEDWIRE', 'Beneficiary Address Line 2', 'Beneficiary/Address/Line2', '{4200}', 'Second line of beneficiary address', 'Max35Text', 35, FALSE, 'Beneficiary', NULL),
    ('FEDWIRE', 'Beneficiary Address Line 3', 'Beneficiary/Address/Line3', '{4200}', 'Third line of beneficiary address', 'Max35Text', 35, FALSE, 'Beneficiary', NULL),

    -- Beneficiary FI
    ('FEDWIRE', 'Beneficiary FI ABA', 'BeneficiaryFI/RoutingNumber', '{4100}', 'ABA routing number of beneficiary FI', 'ABARoutingNumber', 9, FALSE, 'BeneficiaryFI', NULL),
    ('FEDWIRE', 'Beneficiary FI Name', 'BeneficiaryFI/Name', '{4100}', 'Name of beneficiary FI', 'Max35Text', 35, FALSE, 'BeneficiaryFI', NULL),

    -- Additional Information
    ('FEDWIRE', 'Originator to Beneficiary Info', 'OriginatorToBeneficiaryInfo', '{6000}', 'Information from originator to beneficiary', 'Max140Text', 140, FALSE, 'Information', NULL),
    ('FEDWIRE', 'FI to FI Info', 'FIToFIInfo', '{6100}', 'Information between financial institutions', 'Max210Text', 210, FALSE, 'Information', NULL),

    -- Charges
    ('FEDWIRE', 'Charge Details', 'ChargeDetails', '{3700}', 'Who bears the charges', 'Code', 1, FALSE, 'Charges', 'B|S')
ON CONFLICT (format_id, field_path) DO UPDATE SET
    field_name = EXCLUDED.field_name,
    field_tag = EXCLUDED.field_tag,
    field_description = EXCLUDED.field_description,
    data_type = EXCLUDED.data_type,
    max_length = EXCLUDED.max_length,
    is_mandatory = EXCLUDED.is_mandatory,
    field_category = EXCLUDED.field_category,
    allowed_values = EXCLUDED.allowed_values,
    updated_at = CURRENT_TIMESTAMP;

-- =============================================================================
-- Triggers for Audit History
-- =============================================================================
CREATE OR REPLACE FUNCTION mapping.log_standard_field_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO mapping.mapping_history (table_name, mapping_id, action, old_values, new_values, changed_by)
        VALUES ('standard_fields', OLD.standard_field_id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), NEW.updated_by);
        NEW.updated_at := CURRENT_TIMESTAMP;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO mapping.mapping_history (table_name, mapping_id, action, old_values, new_values, changed_by)
        VALUES ('standard_fields', OLD.standard_field_id, 'DELETE', to_jsonb(OLD), NULL, 'SYSTEM');
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO mapping.mapping_history (table_name, mapping_id, action, old_values, new_values, changed_by)
        VALUES ('standard_fields', NEW.standard_field_id, 'INSERT', NULL, to_jsonb(NEW), NEW.updated_by);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_standard_fields_audit ON mapping.standard_fields;
CREATE TRIGGER trg_standard_fields_audit
    AFTER INSERT OR UPDATE OR DELETE ON mapping.standard_fields
    FOR EACH ROW EXECUTE FUNCTION mapping.log_standard_field_changes();

-- =============================================================================
-- Comments
-- =============================================================================
COMMENT ON VIEW mapping.v_mappings_documentation IS 'Complete mapping documentation joining standard fields with silver and gold mappings';
COMMENT ON VIEW mapping.v_mapping_coverage IS 'Coverage metrics showing percentage of standard fields mapped';
COMMENT ON VIEW mapping.v_unmapped_fields IS 'List of standard fields not yet mapped to Silver or Gold';
