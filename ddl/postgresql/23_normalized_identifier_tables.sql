-- ============================================================================
-- Normalized Identifier Tables for GPS CDM
-- ============================================================================
-- Design principles:
-- 1. Each identifier table stores type + value pairs (fully normalized)
-- 2. Additional attributes stored in a separate attributes table
-- 3. No type-specific columns in main identifier table
-- 4. Easy to add new identifier types without schema changes
-- ============================================================================

-- ============================================================================
-- REFERENCE TABLE: Identifier Types
-- ============================================================================
-- Defines all valid identifier types with their metadata

DROP TABLE IF EXISTS gold.cdm_identifier_type CASCADE;
CREATE TABLE gold.cdm_identifier_type (
    identifier_type_code VARCHAR(50) PRIMARY KEY,
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('PARTY', 'ACCOUNT', 'FI', 'PAYMENT')),
    identifier_category VARCHAR(20),  -- For party: ORG_ID, PRVT_ID
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    iso20022_element VARCHAR(256),    -- ISO 20022 element path
    validation_regex VARCHAR(256),
    max_length INT,
    is_globally_unique BOOLEAN DEFAULT FALSE,
    requires_issuer BOOLEAN DEFAULT FALSE,
    requires_scheme BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert ISO 20022 identifier types
INSERT INTO gold.cdm_identifier_type
(identifier_type_code, entity_type, identifier_category, display_name, description, iso20022_element, validation_regex, max_length, is_globally_unique)
VALUES
    -- Party Organization Identifiers (OrgId)
    ('LEI', 'PARTY', 'ORG_ID', 'Legal Entity Identifier', 'ISO 17442 Legal Entity Identifier', 'OrgId/LEI', '^[A-Z0-9]{18}[0-9]{2}$', 20, TRUE),
    ('BIC_PARTY', 'PARTY', 'ORG_ID', 'Party BIC', 'Business Identifier Code for party', 'OrgId/AnyBIC', '^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', 11, TRUE),
    ('DUNS', 'PARTY', 'ORG_ID', 'D-U-N-S Number', 'Dun & Bradstreet Number', 'OrgId/Othr', '^[0-9]{9}$', 9, TRUE),
    ('TAX_ID_ORG', 'PARTY', 'ORG_ID', 'Organization Tax ID', 'Tax identification number for organization', 'OrgId/Othr', NULL, 35, FALSE),
    ('CUST_ID', 'PARTY', 'ORG_ID', 'Customer ID', 'Customer identifier assigned by institution', 'OrgId/Othr', NULL, 35, FALSE),
    ('REG_NBR', 'PARTY', 'ORG_ID', 'Registration Number', 'Company registration number', 'OrgId/Othr', NULL, 35, FALSE),
    ('PRTRY_ORG', 'PARTY', 'ORG_ID', 'Proprietary Org ID', 'Other proprietary organization identifier', 'OrgId/Othr', NULL, 256, FALSE),

    -- Party Private Identifiers (PrvtId)
    ('PASSPORT', 'PARTY', 'PRVT_ID', 'Passport', 'Passport number', 'PrvtId/Othr', NULL, 35, FALSE),
    ('NATIONAL_ID', 'PARTY', 'PRVT_ID', 'National ID', 'National identification number', 'PrvtId/Othr', NULL, 35, FALSE),
    ('DRIVERS_LIC', 'PARTY', 'PRVT_ID', 'Drivers License', 'Drivers license number', 'PrvtId/Othr', NULL, 35, FALSE),
    ('SOC_SEC_NBR', 'PARTY', 'PRVT_ID', 'Social Security Number', 'Social security/insurance number', 'PrvtId/Othr', NULL, 35, FALSE),
    ('TAX_ID_PRVT', 'PARTY', 'PRVT_ID', 'Individual Tax ID', 'Tax identification number for individual', 'PrvtId/Othr', NULL, 35, FALSE),
    ('ALIEN_REG', 'PARTY', 'PRVT_ID', 'Alien Registration', 'Alien registration number', 'PrvtId/Othr', NULL, 35, FALSE),
    ('PRTRY_PRVT', 'PARTY', 'PRVT_ID', 'Proprietary Private ID', 'Other proprietary private identifier', 'PrvtId/Othr', NULL, 256, FALSE),

    -- Account Identifiers
    ('IBAN', 'ACCOUNT', NULL, 'IBAN', 'International Bank Account Number', 'Id/IBAN', '^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$', 34, TRUE),
    ('BBAN', 'ACCOUNT', NULL, 'BBAN', 'Basic Bank Account Number', 'Id/Othr', NULL, 30, FALSE),
    ('UPIC', 'ACCOUNT', NULL, 'UPIC', 'Universal Payment Identification Code', 'Id/Othr', NULL, 17, TRUE),
    ('ACCT_NBR', 'ACCOUNT', NULL, 'Account Number', 'Bank account number', 'Id/Othr', NULL, 35, FALSE),
    ('MSISDN', 'ACCOUNT', NULL, 'MSISDN', 'Mobile phone number for account', 'Prxy/Id', '^\\+?[0-9]{10,15}$', 15, FALSE),
    ('EMAIL_PROXY', 'ACCOUNT', NULL, 'Email Proxy', 'Email address as proxy identifier', 'Prxy/Id', NULL, 256, FALSE),
    ('PAY_ID', 'ACCOUNT', NULL, 'PayID', 'Payment proxy identifier', 'Prxy/Id', NULL, 256, FALSE),
    ('PIX_KEY', 'ACCOUNT', NULL, 'PIX Key', 'Brazil PIX payment key', 'Prxy/Id', NULL, 256, FALSE),
    ('UPI_VPA', 'ACCOUNT', NULL, 'UPI VPA', 'India UPI Virtual Payment Address', 'Prxy/Id', NULL, 256, FALSE),
    ('PRTRY_ACCT', 'ACCOUNT', NULL, 'Proprietary Account ID', 'Other proprietary account identifier', 'Id/Othr', NULL, 256, FALSE),

    -- Financial Institution Identifiers
    ('BIC', 'FI', NULL, 'BIC', 'Bank Identifier Code', 'FinInstnId/BICFI', '^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', 11, TRUE),
    ('LEI_FI', 'FI', NULL, 'FI LEI', 'Legal Entity Identifier for FI', 'FinInstnId/LEI', '^[A-Z0-9]{18}[0-9]{2}$', 20, TRUE),
    ('USABA', 'FI', NULL, 'ABA Routing', 'US ABA Routing Transit Number', 'FinInstnId/ClrSysMmbId', '^[0-9]{9}$', 9, FALSE),
    ('GBDSC', 'FI', NULL, 'UK Sort Code', 'UK Domestic Sort Code', 'FinInstnId/ClrSysMmbId', '^[0-9]{6}$', 6, FALSE),
    ('DEBLZ', 'FI', NULL, 'German Bankleitzahl', 'German Bank Code', 'FinInstnId/ClrSysMmbId', '^[0-9]{8}$', 8, FALSE),
    ('CHBCC', 'FI', NULL, 'Swiss BC Number', 'Swiss Bank Clearing Number', 'FinInstnId/ClrSysMmbId', '^[0-9]{5}$', 5, FALSE),
    ('INFSC', 'FI', NULL, 'India IFSC', 'Indian Financial System Code', 'FinInstnId/ClrSysMmbId', '^[A-Z]{4}0[A-Z0-9]{6}$', 11, FALSE),
    ('CNAPS', 'FI', NULL, 'China CNAPS', 'China National Advanced Payment System Code', 'FinInstnId/ClrSysMmbId', '^[0-9]{12}$', 12, FALSE),
    ('AUBSB', 'FI', NULL, 'Australia BSB', 'Australian Bank-State-Branch Number', 'FinInstnId/ClrSysMmbId', '^[0-9]{6}$', 6, FALSE),
    ('CACPA', 'FI', NULL, 'Canada CPA', 'Canadian Payments Association Number', 'FinInstnId/ClrSysMmbId', NULL, 9, FALSE),
    ('JPZGN', 'FI', NULL, 'Japan Zengin', 'Japan Zengin Bank Code', 'FinInstnId/ClrSysMmbId', '^[0-9]{7}$', 7, FALSE),
    ('KRBOK', 'FI', NULL, 'Korea BOK Code', 'Bank of Korea Financial Institution Code', 'FinInstnId/ClrSysMmbId', NULL, 10, FALSE),
    ('NCC', 'FI', NULL, 'National Clearing Code', 'Generic national clearing code', 'FinInstnId/ClrSysMmbId', NULL, 35, FALSE),
    ('PRTRY_FI', 'FI', NULL, 'Proprietary FI ID', 'Other proprietary FI identifier', 'FinInstnId/Othr', NULL, 256, FALSE),

    -- Payment/Transaction Identifiers
    ('MSG_ID', 'PAYMENT', NULL, 'Message ID', 'ISO 20022 Message Identification', 'GrpHdr/MsgId', NULL, 35, FALSE),
    ('PMT_INF_ID', 'PAYMENT', NULL, 'Payment Info ID', 'Payment Information Identification', 'PmtInf/PmtInfId', NULL, 35, FALSE),
    ('INSTR_ID', 'PAYMENT', NULL, 'Instruction ID', 'Instruction Identification', 'PmtId/InstrId', NULL, 35, FALSE),
    ('END_TO_END_ID', 'PAYMENT', NULL, 'End-to-End ID', 'End-to-End Identification', 'PmtId/EndToEndId', NULL, 35, FALSE),
    ('TX_ID', 'PAYMENT', NULL, 'Transaction ID', 'Transaction Identification', 'PmtId/TxId', NULL, 35, FALSE),
    ('UETR', 'PAYMENT', NULL, 'UETR', 'Unique End-to-End Transaction Reference', 'PmtId/UETR', '^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$', 36, TRUE),
    ('CLR_SYS_REF', 'PAYMENT', NULL, 'Clearing System Ref', 'Clearing System Reference', 'PmtId/ClrSysRef', NULL, 35, FALSE),
    ('ORGNL_MSG_ID', 'PAYMENT', NULL, 'Original Message ID', 'Original Message Identification (status)', 'OrgnlGrpInf/OrgnlMsgId', NULL, 35, FALSE),
    ('ORGNL_E2E_ID', 'PAYMENT', NULL, 'Original E2E ID', 'Original End-to-End ID (status)', 'TxInfAndSts/OrgnlEndToEndId', NULL, 35, FALSE),
    ('PRTRY_PMT', 'PAYMENT', NULL, 'Proprietary Payment ID', 'Other proprietary payment identifier', 'PmtId/Prtry', NULL, 256, FALSE)
ON CONFLICT (identifier_type_code) DO UPDATE SET
    entity_type = EXCLUDED.entity_type,
    identifier_category = EXCLUDED.identifier_category,
    display_name = EXCLUDED.display_name,
    description = EXCLUDED.description,
    iso20022_element = EXCLUDED.iso20022_element,
    validation_regex = EXCLUDED.validation_regex,
    max_length = EXCLUDED.max_length,
    is_globally_unique = EXCLUDED.is_globally_unique;

COMMENT ON TABLE gold.cdm_identifier_type IS 'Reference table defining all valid identifier types with ISO 20022 mappings';

-- ============================================================================
-- PARTY IDENTIFIERS (Normalized)
-- ============================================================================

DROP TABLE IF EXISTS gold.cdm_party_id CASCADE;
CREATE TABLE gold.cdm_party_id (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    party_id VARCHAR(100) NOT NULL,  -- FK to cdm_party.party_id
    identifier_type VARCHAR(50) NOT NULL REFERENCES gold.cdm_identifier_type(identifier_type_code),
    identifier_value VARCHAR(256) NOT NULL,

    -- Optional scheme information (for proprietary types)
    scheme_name VARCHAR(140),
    issuer VARCHAR(140),
    issuing_country VARCHAR(2),

    -- Validity and status
    valid_from DATE,
    valid_to DATE,
    is_primary BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,

    -- Lineage
    source_message_type VARCHAR(50),
    source_stg_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Prevent duplicate identifiers
    UNIQUE(party_id, identifier_type, identifier_value)
);

CREATE INDEX idx_party_id_lookup ON gold.cdm_party_id(identifier_type, identifier_value);
CREATE INDEX idx_party_id_party ON gold.cdm_party_id(party_id);
CREATE INDEX idx_party_id_stg ON gold.cdm_party_id(source_stg_id);

COMMENT ON TABLE gold.cdm_party_id IS 'Normalized party identifiers - type/value pairs only';

-- ============================================================================
-- ACCOUNT IDENTIFIERS (Normalized)
-- ============================================================================

DROP TABLE IF EXISTS gold.cdm_account_id CASCADE;
CREATE TABLE gold.cdm_account_id (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id VARCHAR(100) NOT NULL,  -- FK to cdm_account.account_id
    identifier_type VARCHAR(50) NOT NULL REFERENCES gold.cdm_identifier_type(identifier_type_code),
    identifier_value VARCHAR(256) NOT NULL,

    -- Optional scheme information
    scheme_name VARCHAR(140),
    issuer VARCHAR(140),

    -- Validity and status
    valid_from DATE,
    valid_to DATE,
    is_primary BOOLEAN DEFAULT FALSE,

    -- Lineage
    source_message_type VARCHAR(50),
    source_stg_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(account_id, identifier_type, identifier_value)
);

CREATE INDEX idx_account_id_lookup ON gold.cdm_account_id(identifier_type, identifier_value);
CREATE INDEX idx_account_id_account ON gold.cdm_account_id(account_id);
CREATE INDEX idx_account_id_stg ON gold.cdm_account_id(source_stg_id);
CREATE INDEX idx_account_id_iban ON gold.cdm_account_id(identifier_value) WHERE identifier_type = 'IBAN';

COMMENT ON TABLE gold.cdm_account_id IS 'Normalized account identifiers - type/value pairs only';

-- ============================================================================
-- FINANCIAL INSTITUTION IDENTIFIERS (Normalized)
-- ============================================================================

DROP TABLE IF EXISTS gold.cdm_fi_id CASCADE;
CREATE TABLE gold.cdm_fi_id (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fi_id VARCHAR(100) NOT NULL,  -- FK to cdm_financial_institution.fi_id
    identifier_type VARCHAR(50) NOT NULL REFERENCES gold.cdm_identifier_type(identifier_type_code),
    identifier_value VARCHAR(256) NOT NULL,

    -- Optional scheme information
    scheme_name VARCHAR(140),
    clearing_system VARCHAR(35),  -- For national clearing codes

    -- Validity and status
    valid_from DATE,
    valid_to DATE,
    is_primary BOOLEAN DEFAULT FALSE,

    -- Lineage
    source_message_type VARCHAR(50),
    source_stg_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(fi_id, identifier_type, identifier_value)
);

CREATE INDEX idx_fi_id_lookup ON gold.cdm_fi_id(identifier_type, identifier_value);
CREATE INDEX idx_fi_id_fi ON gold.cdm_fi_id(fi_id);
CREATE INDEX idx_fi_id_stg ON gold.cdm_fi_id(source_stg_id);
CREATE INDEX idx_fi_id_bic ON gold.cdm_fi_id(identifier_value) WHERE identifier_type = 'BIC';
CREATE INDEX idx_fi_id_clearing ON gold.cdm_fi_id(clearing_system, identifier_value) WHERE clearing_system IS NOT NULL;

COMMENT ON TABLE gold.cdm_fi_id IS 'Normalized financial institution identifiers - type/value pairs only';

-- ============================================================================
-- PAYMENT IDENTIFIERS (Normalized)
-- ============================================================================

DROP TABLE IF EXISTS gold.cdm_payment_id CASCADE;
CREATE TABLE gold.cdm_payment_id (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instruction_id UUID NOT NULL,  -- FK to cdm_payment_instruction.instruction_id
    identifier_type VARCHAR(50) NOT NULL REFERENCES gold.cdm_identifier_type(identifier_type_code),
    identifier_value VARCHAR(256) NOT NULL,

    -- Identifier context
    identifier_scope VARCHAR(50),  -- INITIATING_PARTY, DEBTOR, CREDITOR, CLEARING_SYSTEM

    -- Optional scheme information
    scheme_name VARCHAR(140),

    -- For status tracking - link to original identifier
    related_identifier_type VARCHAR(50),
    related_identifier_value VARCHAR(256),
    is_original BOOLEAN DEFAULT TRUE,  -- FALSE if from status message

    -- Lineage
    source_message_type VARCHAR(50),
    source_stg_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(instruction_id, identifier_type, identifier_value, identifier_scope)
);

CREATE INDEX idx_payment_id_lookup ON gold.cdm_payment_id(identifier_type, identifier_value);
CREATE INDEX idx_payment_id_instruction ON gold.cdm_payment_id(instruction_id);
CREATE INDEX idx_payment_id_stg ON gold.cdm_payment_id(source_stg_id);
CREATE INDEX idx_payment_id_e2e ON gold.cdm_payment_id(identifier_value) WHERE identifier_type = 'END_TO_END_ID';
CREATE INDEX idx_payment_id_uetr ON gold.cdm_payment_id(identifier_value) WHERE identifier_type = 'UETR';
CREATE INDEX idx_payment_id_txid ON gold.cdm_payment_id(identifier_value) WHERE identifier_type = 'TX_ID';

COMMENT ON TABLE gold.cdm_payment_id IS 'Normalized payment identifiers - type/value pairs only';

-- ============================================================================
-- IDENTIFIER ATTRIBUTES (For additional metadata)
-- ============================================================================
-- Stores optional attributes that don't fit in the main tables
-- This allows extensibility without schema changes

DROP TABLE IF EXISTS gold.cdm_identifier_attribute CASCADE;
CREATE TABLE gold.cdm_identifier_attribute (
    attribute_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('PARTY', 'ACCOUNT', 'FI', 'PAYMENT')),
    identifier_id UUID NOT NULL,  -- References the specific identifier table
    attribute_name VARCHAR(50) NOT NULL,
    attribute_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(entity_type, identifier_id, attribute_name)
);

CREATE INDEX idx_id_attr_lookup ON gold.cdm_identifier_attribute(entity_type, identifier_id);

COMMENT ON TABLE gold.cdm_identifier_attribute IS 'Additional attributes for identifiers (extensible key-value store)';

-- ============================================================================
-- CONSOLIDATED VIEW: All Identifiers for a Payment
-- ============================================================================

CREATE OR REPLACE VIEW gold.v_payment_identifiers AS
SELECT
    pi.instruction_id,
    'PAYMENT' as entity_type,
    pid.id as identifier_id,
    pid.identifier_type,
    pid.identifier_value,
    pid.identifier_scope,
    pid.scheme_name,
    NULL::VARCHAR as entity_role,
    it.display_name as type_display_name,
    it.is_globally_unique
FROM gold.cdm_payment_instruction pi
JOIN gold.cdm_payment_id pid ON pi.instruction_id = pid.instruction_id
LEFT JOIN gold.cdm_identifier_type it ON pid.identifier_type = it.identifier_type_code

UNION ALL

SELECT
    pi.instruction_id,
    'PARTY' as entity_type,
    prid.id as identifier_id,
    prid.identifier_type,
    prid.identifier_value,
    it.identifier_category as identifier_scope,
    prid.scheme_name,
    p.role as entity_role,
    it.display_name,
    it.is_globally_unique
FROM gold.cdm_payment_instruction pi
JOIN gold.cdm_party p ON pi.source_stg_id = p.source_stg_id
JOIN gold.cdm_party_id prid ON p.party_id = prid.party_id
LEFT JOIN gold.cdm_identifier_type it ON prid.identifier_type = it.identifier_type_code

UNION ALL

SELECT
    pi.instruction_id,
    'ACCOUNT' as entity_type,
    aid.id as identifier_id,
    aid.identifier_type,
    aid.identifier_value,
    NULL as identifier_scope,
    aid.scheme_name,
    a.role as entity_role,
    it.display_name,
    it.is_globally_unique
FROM gold.cdm_payment_instruction pi
JOIN gold.cdm_account a ON pi.source_stg_id = a.source_stg_id
JOIN gold.cdm_account_id aid ON a.account_id = aid.account_id
LEFT JOIN gold.cdm_identifier_type it ON aid.identifier_type = it.identifier_type_code

UNION ALL

SELECT
    pi.instruction_id,
    'FI' as entity_type,
    fid.id as identifier_id,
    fid.identifier_type,
    fid.identifier_value,
    fid.clearing_system as identifier_scope,
    fid.scheme_name,
    fi.role as entity_role,
    it.display_name,
    it.is_globally_unique
FROM gold.cdm_payment_instruction pi
JOIN gold.cdm_financial_institution fi ON pi.source_stg_id = fi.source_stg_id
JOIN gold.cdm_fi_id fid ON fi.fi_id = fid.fi_id
LEFT JOIN gold.cdm_identifier_type it ON fid.identifier_type = it.identifier_type_code;

COMMENT ON VIEW gold.v_payment_identifiers IS 'Consolidated view of all identifiers for a payment transaction';

-- ============================================================================
-- LOOKUP VIEW: Find Payment by Any Identifier
-- ============================================================================

CREATE OR REPLACE VIEW gold.v_identifier_lookup AS
SELECT
    'PAYMENT' as entity_type,
    instruction_id,
    identifier_type,
    identifier_value,
    identifier_scope,
    source_message_type,
    created_at
FROM gold.cdm_payment_id

UNION ALL

SELECT
    'PARTY' as entity_type,
    p.source_stg_id::UUID as instruction_id,
    prid.identifier_type,
    prid.identifier_value,
    prid.scheme_name as identifier_scope,
    prid.source_message_type,
    prid.created_at
FROM gold.cdm_party_id prid
JOIN gold.cdm_party p ON prid.party_id = p.party_id

UNION ALL

SELECT
    'ACCOUNT' as entity_type,
    a.source_stg_id::UUID as instruction_id,
    aid.identifier_type,
    aid.identifier_value,
    aid.scheme_name as identifier_scope,
    aid.source_message_type,
    aid.created_at
FROM gold.cdm_account_id aid
JOIN gold.cdm_account a ON aid.account_id = a.account_id

UNION ALL

SELECT
    'FI' as entity_type,
    pi.instruction_id,
    fid.identifier_type,
    fid.identifier_value,
    fid.clearing_system as identifier_scope,
    fid.source_message_type,
    fid.created_at
FROM gold.cdm_fi_id fid
JOIN gold.cdm_financial_institution fi ON fid.fi_id = fi.fi_id
JOIN gold.cdm_payment_instruction pi ON pi.source_stg_id = fi.source_stg_id;

COMMENT ON VIEW gold.v_identifier_lookup IS 'Lookup view to find payments by any identifier type/value';

-- ============================================================================
-- FUNCTIONS FOR IDENTIFIER MANAGEMENT
-- ============================================================================

-- Add/upsert party identifier
CREATE OR REPLACE FUNCTION gold.upsert_party_identifier(
    p_party_id VARCHAR,
    p_identifier_type VARCHAR,
    p_identifier_value VARCHAR,
    p_scheme_name VARCHAR DEFAULT NULL,
    p_issuer VARCHAR DEFAULT NULL,
    p_issuing_country VARCHAR DEFAULT NULL,
    p_is_primary BOOLEAN DEFAULT FALSE,
    p_source_message_type VARCHAR DEFAULT NULL,
    p_source_stg_id VARCHAR DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO gold.cdm_party_id (
        party_id, identifier_type, identifier_value,
        scheme_name, issuer, issuing_country,
        is_primary, source_message_type, source_stg_id
    )
    VALUES (
        p_party_id, p_identifier_type, p_identifier_value,
        p_scheme_name, p_issuer, p_issuing_country,
        p_is_primary, p_source_message_type, p_source_stg_id
    )
    ON CONFLICT (party_id, identifier_type, identifier_value)
    DO UPDATE SET
        scheme_name = COALESCE(EXCLUDED.scheme_name, gold.cdm_party_id.scheme_name),
        issuer = COALESCE(EXCLUDED.issuer, gold.cdm_party_id.issuer),
        is_primary = COALESCE(EXCLUDED.is_primary, gold.cdm_party_id.is_primary)
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Add/upsert account identifier
CREATE OR REPLACE FUNCTION gold.upsert_account_identifier(
    p_account_id VARCHAR,
    p_identifier_type VARCHAR,
    p_identifier_value VARCHAR,
    p_scheme_name VARCHAR DEFAULT NULL,
    p_is_primary BOOLEAN DEFAULT FALSE,
    p_source_message_type VARCHAR DEFAULT NULL,
    p_source_stg_id VARCHAR DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO gold.cdm_account_id (
        account_id, identifier_type, identifier_value,
        scheme_name, is_primary, source_message_type, source_stg_id
    )
    VALUES (
        p_account_id, p_identifier_type, p_identifier_value,
        p_scheme_name, p_is_primary, p_source_message_type, p_source_stg_id
    )
    ON CONFLICT (account_id, identifier_type, identifier_value)
    DO UPDATE SET
        scheme_name = COALESCE(EXCLUDED.scheme_name, gold.cdm_account_id.scheme_name),
        is_primary = COALESCE(EXCLUDED.is_primary, gold.cdm_account_id.is_primary)
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Add/upsert FI identifier
CREATE OR REPLACE FUNCTION gold.upsert_fi_identifier(
    p_fi_id VARCHAR,
    p_identifier_type VARCHAR,
    p_identifier_value VARCHAR,
    p_clearing_system VARCHAR DEFAULT NULL,
    p_scheme_name VARCHAR DEFAULT NULL,
    p_is_primary BOOLEAN DEFAULT FALSE,
    p_source_message_type VARCHAR DEFAULT NULL,
    p_source_stg_id VARCHAR DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO gold.cdm_fi_id (
        fi_id, identifier_type, identifier_value,
        clearing_system, scheme_name, is_primary,
        source_message_type, source_stg_id
    )
    VALUES (
        p_fi_id, p_identifier_type, p_identifier_value,
        p_clearing_system, p_scheme_name, p_is_primary,
        p_source_message_type, p_source_stg_id
    )
    ON CONFLICT (fi_id, identifier_type, identifier_value)
    DO UPDATE SET
        clearing_system = COALESCE(EXCLUDED.clearing_system, gold.cdm_fi_id.clearing_system),
        scheme_name = COALESCE(EXCLUDED.scheme_name, gold.cdm_fi_id.scheme_name),
        is_primary = COALESCE(EXCLUDED.is_primary, gold.cdm_fi_id.is_primary)
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Add/upsert payment identifier
CREATE OR REPLACE FUNCTION gold.upsert_payment_identifier(
    p_instruction_id UUID,
    p_identifier_type VARCHAR,
    p_identifier_value VARCHAR,
    p_identifier_scope VARCHAR DEFAULT 'INITIATING_PARTY',
    p_scheme_name VARCHAR DEFAULT NULL,
    p_source_message_type VARCHAR DEFAULT NULL,
    p_source_stg_id VARCHAR DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO gold.cdm_payment_id (
        instruction_id, identifier_type, identifier_value,
        identifier_scope, scheme_name, source_message_type, source_stg_id
    )
    VALUES (
        p_instruction_id, p_identifier_type, p_identifier_value,
        p_identifier_scope, p_scheme_name, p_source_message_type, p_source_stg_id
    )
    ON CONFLICT (instruction_id, identifier_type, identifier_value, identifier_scope)
    DO UPDATE SET
        scheme_name = COALESCE(EXCLUDED.scheme_name, gold.cdm_payment_id.scheme_name)
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Find payment by any identifier
CREATE OR REPLACE FUNCTION gold.find_by_identifier(
    p_identifier_type VARCHAR,
    p_identifier_value VARCHAR
)
RETURNS TABLE (
    entity_type VARCHAR,
    instruction_id UUID,
    entity_id VARCHAR,
    identifier_scope VARCHAR,
    source_message_type VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        il.entity_type::VARCHAR,
        il.instruction_id,
        il.identifier_value as entity_id,
        il.identifier_scope::VARCHAR,
        il.source_message_type
    FROM gold.v_identifier_lookup il
    WHERE il.identifier_type = p_identifier_type
      AND il.identifier_value = p_identifier_value;
END;
$$ LANGUAGE plpgsql;

-- Add identifier attribute
CREATE OR REPLACE FUNCTION gold.add_identifier_attribute(
    p_entity_type VARCHAR,
    p_identifier_id UUID,
    p_attribute_name VARCHAR,
    p_attribute_value TEXT
)
RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO gold.cdm_identifier_attribute (
        entity_type, identifier_id, attribute_name, attribute_value
    )
    VALUES (
        p_entity_type, p_identifier_id, p_attribute_name, p_attribute_value
    )
    ON CONFLICT (entity_type, identifier_id, attribute_name)
    DO UPDATE SET attribute_value = EXCLUDED.attribute_value
    RETURNING attribute_id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON gold.cdm_identifier_type TO gps_cdm_svc;
GRANT SELECT, INSERT, UPDATE ON gold.cdm_party_id TO gps_cdm_svc;
GRANT SELECT, INSERT, UPDATE ON gold.cdm_account_id TO gps_cdm_svc;
GRANT SELECT, INSERT, UPDATE ON gold.cdm_fi_id TO gps_cdm_svc;
GRANT SELECT, INSERT, UPDATE ON gold.cdm_payment_id TO gps_cdm_svc;
GRANT SELECT, INSERT, UPDATE ON gold.cdm_identifier_attribute TO gps_cdm_svc;
GRANT SELECT ON gold.v_payment_identifiers TO gps_cdm_svc;
GRANT SELECT ON gold.v_identifier_lookup TO gps_cdm_svc;
GRANT EXECUTE ON FUNCTION gold.upsert_party_identifier TO gps_cdm_svc;
GRANT EXECUTE ON FUNCTION gold.upsert_account_identifier TO gps_cdm_svc;
GRANT EXECUTE ON FUNCTION gold.upsert_fi_identifier TO gps_cdm_svc;
GRANT EXECUTE ON FUNCTION gold.upsert_payment_identifier TO gps_cdm_svc;
GRANT EXECUTE ON FUNCTION gold.find_by_identifier TO gps_cdm_svc;
GRANT EXECUTE ON FUNCTION gold.add_identifier_attribute TO gps_cdm_svc;
