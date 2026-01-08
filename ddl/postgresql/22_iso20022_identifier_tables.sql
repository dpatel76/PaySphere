-- ============================================================================
-- ISO 20022 Normalized Identifier Tables
-- ============================================================================
-- This DDL creates separate tables for all identifier types following ISO 20022
-- data model. Each identifier table stores identifier_type and identifier_value.
--
-- ISO 20022 Identifier Types:
-- - Party: OrgId (LEI, BIC, DUNS, etc.), PrvtId (passport, tax ID, etc.)
-- - Account: IBAN, BBAN, UPIC, Othr (with scheme name)
-- - Financial Institution: BIC, LEI, ClrSysMmbId, Othr
-- - Payment: MsgId, PmtInfId, InstrId, EndToEndId, TxId, ClrSysRef, UETR
-- ============================================================================

-- ============================================================================
-- PARTY IDENTIFIER TABLE (ISO 20022 OrganisationIdentification / PrivateIdentification)
-- ============================================================================
-- Stores all party identifiers with their types
-- Maps to: OrgId (LEI, BIC, DUNS, TaxId, etc.) and PrvtId (Passport, DrvrsLic, etc.)

CREATE TABLE IF NOT EXISTS gold.cdm_party_identifier (
    party_identifier_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    party_id UUID NOT NULL REFERENCES gold.cdm_party(party_id) ON DELETE CASCADE,

    -- ISO 20022 identifier categorization
    identifier_category VARCHAR(20) NOT NULL CHECK (identifier_category IN ('ORG_ID', 'PRVT_ID')),

    -- ISO 20022 identifier type codes
    -- ORG_ID types: LEI, BIC, DUNS, TAX_ID, PRTRY (proprietary)
    -- PRVT_ID types: PASSPORT, TAX_ID, NATL_ID, DRVRS_LIC, SOC_SEC_NBR, CUST_NBR, PRTRY
    identifier_type VARCHAR(50) NOT NULL,

    -- The actual identifier value
    identifier_value VARCHAR(256) NOT NULL,

    -- ISO 20022 scheme information (for proprietary identifiers)
    scheme_name VARCHAR(140),           -- SchemeName/Prtry
    scheme_proprietary VARCHAR(35),     -- SchemeName/Cd
    issuer VARCHAR(140),                -- Issuer of the identifier

    -- ISO 20022 specific fields for OrgId
    any_bic VARCHAR(11),                -- AnyBIC (for BIC identification)
    lei VARCHAR(35),                    -- LEI code

    -- ISO 20022 specific fields for PrvtId
    date_of_birth DATE,                 -- DtAndPlcOfBirth/BirthDt
    province_of_birth VARCHAR(35),      -- DtAndPlcOfBirth/PrvcOfBirth
    city_of_birth VARCHAR(35),          -- DtAndPlcOfBirth/CityOfBirth
    country_of_birth VARCHAR(2),        -- DtAndPlcOfBirth/CtryOfBirth

    -- Validity period
    valid_from DATE,
    valid_to DATE,

    -- Metadata
    source_message_type VARCHAR(50),
    source_stg_id VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint to prevent duplicates
    UNIQUE(party_id, identifier_category, identifier_type, identifier_value)
);

-- Index for lookups by identifier
CREATE INDEX IF NOT EXISTS idx_party_identifier_lookup
ON gold.cdm_party_identifier(identifier_type, identifier_value);

CREATE INDEX IF NOT EXISTS idx_party_identifier_party
ON gold.cdm_party_identifier(party_id);

CREATE INDEX IF NOT EXISTS idx_party_identifier_lei
ON gold.cdm_party_identifier(lei) WHERE lei IS NOT NULL;

COMMENT ON TABLE gold.cdm_party_identifier IS 'ISO 20022 party identifiers - stores OrgId and PrvtId with type/value structure';

-- ============================================================================
-- ACCOUNT IDENTIFIER TABLE (ISO 20022 AccountIdentification)
-- ============================================================================
-- Stores all account identifiers with their types
-- Maps to: IBAN, BBAN, UPIC, MSISDN, Email, Othr

CREATE TABLE IF NOT EXISTS gold.cdm_account_identifier (
    account_identifier_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES gold.cdm_account(account_id) ON DELETE CASCADE,

    -- ISO 20022 identifier type codes
    -- Types: IBAN, BBAN, UPIC, MSISDN, EMAIL, PROXY, PRTRY
    identifier_type VARCHAR(50) NOT NULL,

    -- The actual identifier value
    identifier_value VARCHAR(256) NOT NULL,

    -- ISO 20022 scheme information (for Othr/Prtry identifiers)
    scheme_name VARCHAR(140),           -- SchemeName (scheme name for proprietary)
    scheme_proprietary VARCHAR(35),     -- SchemeName/Cd code
    issuer VARCHAR(140),                -- Issuer of the identifier

    -- Proxy identification (ISO 20022 Prxy element)
    proxy_type VARCHAR(35),             -- Prxy/Tp/Cd or Prxy/Tp/Prtry
    proxy_type_proprietary VARCHAR(35), -- Prxy/Tp/Prtry

    -- Validity period
    valid_from DATE,
    valid_to DATE,

    -- Metadata
    source_message_type VARCHAR(50),
    source_stg_id VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint to prevent duplicates
    UNIQUE(account_id, identifier_type, identifier_value)
);

-- Indexes for lookups
CREATE INDEX IF NOT EXISTS idx_account_identifier_lookup
ON gold.cdm_account_identifier(identifier_type, identifier_value);

CREATE INDEX IF NOT EXISTS idx_account_identifier_account
ON gold.cdm_account_identifier(account_id);

CREATE INDEX IF NOT EXISTS idx_account_identifier_iban
ON gold.cdm_account_identifier(identifier_value)
WHERE identifier_type = 'IBAN';

COMMENT ON TABLE gold.cdm_account_identifier IS 'ISO 20022 account identifiers - stores IBAN, BBAN, proxy IDs with type/value structure';

-- ============================================================================
-- FINANCIAL INSTITUTION IDENTIFIER TABLE (ISO 20022 FinancialInstitutionIdentification)
-- ============================================================================
-- Stores all FI identifiers with their types
-- Maps to: BIC, LEI, ClrSysMmbId, Othr

CREATE TABLE IF NOT EXISTS gold.cdm_fi_identifier (
    fi_identifier_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fi_id UUID NOT NULL REFERENCES gold.cdm_financial_institution(fi_id) ON DELETE CASCADE,

    -- ISO 20022 identifier type codes
    -- Types: BIC, LEI, CLR_SYS_MMBR_ID, NCC, USABA, GBDSC, PRTRY
    identifier_type VARCHAR(50) NOT NULL,

    -- The actual identifier value
    identifier_value VARCHAR(256) NOT NULL,

    -- ISO 20022 scheme information
    scheme_name VARCHAR(140),           -- ClrSysMmbId/ClrSysId/Cd or Prtry
    scheme_proprietary VARCHAR(35),     -- ClrSysMmbId/ClrSysId/Prtry
    issuer VARCHAR(140),                -- Issuer

    -- Clearing system specific fields
    clearing_system_code VARCHAR(5),    -- Standard clearing system code (USABA, GBDSC, etc.)
    member_id VARCHAR(35),              -- ClrSysMmbId/MmbId

    -- Validity period
    valid_from DATE,
    valid_to DATE,

    -- Metadata
    source_message_type VARCHAR(50),
    source_stg_id VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint to prevent duplicates
    UNIQUE(fi_id, identifier_type, identifier_value)
);

-- Indexes for lookups
CREATE INDEX IF NOT EXISTS idx_fi_identifier_lookup
ON gold.cdm_fi_identifier(identifier_type, identifier_value);

CREATE INDEX IF NOT EXISTS idx_fi_identifier_fi
ON gold.cdm_fi_identifier(fi_id);

CREATE INDEX IF NOT EXISTS idx_fi_identifier_bic
ON gold.cdm_fi_identifier(identifier_value)
WHERE identifier_type = 'BIC';

CREATE INDEX IF NOT EXISTS idx_fi_identifier_clearing
ON gold.cdm_fi_identifier(clearing_system_code, member_id)
WHERE clearing_system_code IS NOT NULL;

COMMENT ON TABLE gold.cdm_fi_identifier IS 'ISO 20022 financial institution identifiers - stores BIC, LEI, clearing member IDs with type/value structure';

-- ============================================================================
-- PAYMENT TRANSACTION IDENTIFIER TABLE (ISO 20022 PaymentIdentification)
-- ============================================================================
-- Stores all payment/transaction identifiers with their types
-- Maps to: MsgId, PmtInfId, InstrId, EndToEndId, TxId, ClrSysRef, UETR

CREATE TABLE IF NOT EXISTS gold.cdm_payment_identifier (
    payment_identifier_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instruction_id UUID NOT NULL REFERENCES gold.cdm_payment_instruction(instruction_id) ON DELETE CASCADE,

    -- ISO 20022 identifier type codes
    -- Types: MSG_ID, PMT_INF_ID, INSTR_ID, END_TO_END_ID, TX_ID, CLR_SYS_REF, UETR, PRTRY
    identifier_type VARCHAR(50) NOT NULL,

    -- The actual identifier value
    identifier_value VARCHAR(256) NOT NULL,

    -- ISO 20022 identifier scope/context
    -- Indicates which party assigned this identifier
    identifier_scope VARCHAR(50),       -- INITIATING_PARTY, DEBTOR, CREDITOR, CLEARING_SYSTEM, NETWORK

    -- ISO 20022 proprietary scheme information
    scheme_name VARCHAR(140),
    scheme_proprietary VARCHAR(35),
    issuer VARCHAR(140),

    -- Relationship to other identifiers (for tracing)
    related_identifier_type VARCHAR(50),
    related_identifier_value VARCHAR(256),

    -- Metadata
    source_message_type VARCHAR(50),
    source_stg_id VARCHAR(100),
    is_original BOOLEAN DEFAULT TRUE,   -- TRUE if from original message, FALSE if from status update
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint - allow same identifier type/value from different sources
    UNIQUE(instruction_id, identifier_type, identifier_value, identifier_scope)
);

-- Indexes for lookups and correlation
CREATE INDEX IF NOT EXISTS idx_payment_identifier_lookup
ON gold.cdm_payment_identifier(identifier_type, identifier_value);

CREATE INDEX IF NOT EXISTS idx_payment_identifier_instruction
ON gold.cdm_payment_identifier(instruction_id);

CREATE INDEX IF NOT EXISTS idx_payment_identifier_e2e
ON gold.cdm_payment_identifier(identifier_value)
WHERE identifier_type = 'END_TO_END_ID';

CREATE INDEX IF NOT EXISTS idx_payment_identifier_uetr
ON gold.cdm_payment_identifier(identifier_value)
WHERE identifier_type = 'UETR';

CREATE INDEX IF NOT EXISTS idx_payment_identifier_txid
ON gold.cdm_payment_identifier(identifier_value)
WHERE identifier_type = 'TX_ID';

COMMENT ON TABLE gold.cdm_payment_identifier IS 'ISO 20022 payment identifiers - stores MsgId, E2EId, TxId, UETR with type/value structure';

-- ============================================================================
-- REFERENCE DATA: IDENTIFIER TYPE DEFINITIONS
-- ============================================================================
-- Reference table for valid identifier types with ISO 20022 mappings

CREATE TABLE IF NOT EXISTS gold.ref_identifier_type (
    identifier_type_id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,       -- PARTY, ACCOUNT, FI, PAYMENT
    identifier_type VARCHAR(50) NOT NULL,
    identifier_category VARCHAR(50),         -- For party: ORG_ID or PRVT_ID
    iso20022_path VARCHAR(256),             -- XPath in ISO 20022 message
    description VARCHAR(256),
    validation_pattern VARCHAR(256),        -- Regex for validation
    max_length INT,
    is_standard BOOLEAN DEFAULT TRUE,       -- FALSE for proprietary types
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(entity_type, identifier_type)
);

-- Populate reference data for identifier types
INSERT INTO gold.ref_identifier_type (entity_type, identifier_type, identifier_category, iso20022_path, description, validation_pattern, max_length)
VALUES
    -- Party Organization Identifiers (OrgId)
    ('PARTY', 'LEI', 'ORG_ID', 'OrgId/LEI', 'Legal Entity Identifier (20 chars)', '^[A-Z0-9]{18}[0-9]{2}$', 20),
    ('PARTY', 'BIC', 'ORG_ID', 'OrgId/AnyBIC', 'Business Identifier Code (8 or 11 chars)', '^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', 11),
    ('PARTY', 'DUNS', 'ORG_ID', 'OrgId/Othr (Prtry=DUNS)', 'Dun & Bradstreet Number', '^[0-9]{9}$', 9),
    ('PARTY', 'TAX_ID', 'ORG_ID', 'OrgId/Othr (Prtry=TXID)', 'Tax Identification Number', NULL, 35),
    ('PARTY', 'CUST_ID', 'ORG_ID', 'OrgId/Othr (Prtry=CUST)', 'Customer ID assigned by institution', NULL, 35),
    ('PARTY', 'ORG_PRTRY', 'ORG_ID', 'OrgId/Othr', 'Other proprietary organization ID', NULL, 256),

    -- Party Private Identifiers (PrvtId)
    ('PARTY', 'PASSPORT', 'PRVT_ID', 'PrvtId/Othr (Prtry=PASSPORT)', 'Passport number', NULL, 35),
    ('PARTY', 'NATL_REG_NBR', 'PRVT_ID', 'PrvtId/Othr (Prtry=NRIN)', 'National registration number', NULL, 35),
    ('PARTY', 'DRVRS_LIC', 'PRVT_ID', 'PrvtId/Othr (Prtry=DRLC)', 'Drivers license number', NULL, 35),
    ('PARTY', 'SOC_SEC_NBR', 'PRVT_ID', 'PrvtId/Othr (Prtry=SOSE)', 'Social security number', NULL, 35),
    ('PARTY', 'ALIEN_REG_NBR', 'PRVT_ID', 'PrvtId/Othr (Prtry=ARNU)', 'Alien registration number', NULL, 35),
    ('PARTY', 'PRVT_TAX_ID', 'PRVT_ID', 'PrvtId/Othr (Prtry=TXID)', 'Private tax identification', NULL, 35),
    ('PARTY', 'PRVT_PRTRY', 'PRVT_ID', 'PrvtId/Othr', 'Other proprietary private ID', NULL, 256),

    -- Account Identifiers
    ('ACCOUNT', 'IBAN', NULL, 'Id/IBAN', 'International Bank Account Number', '^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$', 34),
    ('ACCOUNT', 'BBAN', NULL, 'Id/Othr (Prtry=BBAN)', 'Basic Bank Account Number', NULL, 30),
    ('ACCOUNT', 'UPIC', NULL, 'Id/Othr (Prtry=UPIC)', 'Universal Payment Identification Code', NULL, 17),
    ('ACCOUNT', 'MSISDN', NULL, 'Prxy/Id (Tp=TELE)', 'Mobile phone number', '^\\+?[0-9]{10,15}$', 15),
    ('ACCOUNT', 'EMAIL', NULL, 'Prxy/Id (Tp=EMAL)', 'Email address', NULL, 256),
    ('ACCOUNT', 'ACCT_PRTRY', NULL, 'Id/Othr', 'Other proprietary account ID', NULL, 256),
    ('ACCOUNT', 'PROXY', NULL, 'Prxy/Id', 'Proxy identifier (PayID, PIX key, etc.)', NULL, 256),

    -- Financial Institution Identifiers
    ('FI', 'BIC', NULL, 'FinInstnId/BICFI', 'Business Identifier Code', '^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', 11),
    ('FI', 'LEI', NULL, 'FinInstnId/LEI', 'Legal Entity Identifier', '^[A-Z0-9]{18}[0-9]{2}$', 20),
    ('FI', 'USABA', NULL, 'FinInstnId/ClrSysMmbId (Cd=USABA)', 'US ABA Routing Number', '^[0-9]{9}$', 9),
    ('FI', 'GBDSC', NULL, 'FinInstnId/ClrSysMmbId (Cd=GBDSC)', 'UK Sort Code', '^[0-9]{6}$', 6),
    ('FI', 'DEBLZ', NULL, 'FinInstnId/ClrSysMmbId (Cd=DEBLZ)', 'German Bankleitzahl', '^[0-9]{8}$', 8),
    ('FI', 'CHBCC', NULL, 'FinInstnId/ClrSysMmbId (Cd=CHBCC)', 'Swiss BC Number', NULL, 5),
    ('FI', 'INFSC', NULL, 'FinInstnId/ClrSysMmbId (Cd=INFSC)', 'India IFSC Code', '^[A-Z]{4}0[A-Z0-9]{6}$', 11),
    ('FI', 'CNAPS', NULL, 'FinInstnId/ClrSysMmbId (Cd=CNAPS)', 'China CNAPS Code', '^[0-9]{12}$', 12),
    ('FI', 'AUBSB', NULL, 'FinInstnId/ClrSysMmbId (Cd=AUBSB)', 'Australia BSB Number', '^[0-9]{6}$', 6),
    ('FI', 'CACPA', NULL, 'FinInstnId/ClrSysMmbId (Cd=CACPA)', 'Canada Payments Association', NULL, 9),
    ('FI', 'NCC', NULL, 'FinInstnId/ClrSysMmbId', 'National Clearing Code (generic)', NULL, 35),
    ('FI', 'FI_PRTRY', NULL, 'FinInstnId/Othr', 'Other proprietary FI identifier', NULL, 256),

    -- Payment Transaction Identifiers
    ('PAYMENT', 'MSG_ID', NULL, 'GrpHdr/MsgId', 'Message Identification', NULL, 35),
    ('PAYMENT', 'PMT_INF_ID', NULL, 'PmtInf/PmtInfId', 'Payment Information Identification', NULL, 35),
    ('PAYMENT', 'INSTR_ID', NULL, 'CdtTrfTxInf/PmtId/InstrId', 'Instruction Identification', NULL, 35),
    ('PAYMENT', 'END_TO_END_ID', NULL, 'CdtTrfTxInf/PmtId/EndToEndId', 'End-to-End Identification', NULL, 35),
    ('PAYMENT', 'TX_ID', NULL, 'CdtTrfTxInf/PmtId/TxId', 'Transaction Identification', NULL, 35),
    ('PAYMENT', 'CLR_SYS_REF', NULL, 'CdtTrfTxInf/PmtId/ClrSysRef', 'Clearing System Reference', NULL, 35),
    ('PAYMENT', 'UETR', NULL, 'CdtTrfTxInf/PmtId/UETR', 'Unique End-to-End Transaction Reference', '^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$', 36),
    ('PAYMENT', 'ORGTR_MSG_ID', NULL, 'OrgnlGrpInf/OrgnlMsgId', 'Original Message ID (for status)', NULL, 35),
    ('PAYMENT', 'ORGTR_END_TO_END_ID', NULL, 'TxInfAndSts/OrgnlEndToEndId', 'Original End-to-End ID (for status)', NULL, 35),
    ('PAYMENT', 'PMT_PRTRY', NULL, 'PmtId/Prtry', 'Proprietary payment identifier', NULL, 256)
ON CONFLICT (entity_type, identifier_type) DO UPDATE SET
    identifier_category = EXCLUDED.identifier_category,
    iso20022_path = EXCLUDED.iso20022_path,
    description = EXCLUDED.description,
    validation_pattern = EXCLUDED.validation_pattern,
    max_length = EXCLUDED.max_length;

COMMENT ON TABLE gold.ref_identifier_type IS 'Reference data for ISO 20022 identifier types with validation patterns';

-- ============================================================================
-- VIEWS FOR CONSOLIDATED IDENTIFIER ACCESS
-- ============================================================================

-- View: All identifiers for a payment (payment + parties + accounts + FIs)
CREATE OR REPLACE VIEW gold.v_payment_all_identifiers AS
SELECT
    pi.instruction_id,
    'PAYMENT' as entity_type,
    pi.instruction_id::text as entity_id,
    pid.identifier_type,
    pid.identifier_value,
    pid.identifier_scope,
    pid.scheme_name,
    NULL as role
FROM gold.cdm_payment_instruction pi
JOIN gold.cdm_payment_identifier pid ON pi.instruction_id = pid.instruction_id

UNION ALL

SELECT
    pi.instruction_id,
    'PARTY' as entity_type,
    p.party_id::text as entity_id,
    prid.identifier_type,
    prid.identifier_value,
    prid.identifier_category as identifier_scope,
    prid.scheme_name,
    p.role
FROM gold.cdm_payment_instruction pi
JOIN gold.cdm_party p ON pi.instruction_id = p.instruction_id
JOIN gold.cdm_party_identifier prid ON p.party_id = prid.party_id

UNION ALL

SELECT
    pi.instruction_id,
    'ACCOUNT' as entity_type,
    a.account_id::text as entity_id,
    aid.identifier_type,
    aid.identifier_value,
    NULL as identifier_scope,
    aid.scheme_name,
    a.role
FROM gold.cdm_payment_instruction pi
JOIN gold.cdm_account a ON pi.instruction_id = a.instruction_id
JOIN gold.cdm_account_identifier aid ON a.account_id = aid.account_id

UNION ALL

SELECT
    pi.instruction_id,
    'FI' as entity_type,
    fi.fi_id::text as entity_id,
    fid.identifier_type,
    fid.identifier_value,
    fid.clearing_system_code as identifier_scope,
    fid.scheme_name,
    fi.role
FROM gold.cdm_payment_instruction pi
JOIN gold.cdm_financial_institution fi ON pi.instruction_id = fi.instruction_id
JOIN gold.cdm_fi_identifier fid ON fi.fi_id = fid.fi_id;

COMMENT ON VIEW gold.v_payment_all_identifiers IS 'Consolidated view of all identifiers for a payment transaction';

-- View: Lookup payment by any identifier
CREATE OR REPLACE VIEW gold.v_identifier_lookup AS
SELECT
    'PAYMENT' as entity_type,
    pi.instruction_id,
    pid.identifier_type,
    pid.identifier_value,
    pi.source_message_type,
    pi.created_at
FROM gold.cdm_payment_instruction pi
JOIN gold.cdm_payment_identifier pid ON pi.instruction_id = pid.instruction_id

UNION ALL

SELECT
    'PARTY' as entity_type,
    p.instruction_id,
    prid.identifier_type,
    prid.identifier_value,
    p.source_message_type,
    prid.created_at
FROM gold.cdm_party p
JOIN gold.cdm_party_identifier prid ON p.party_id = prid.party_id

UNION ALL

SELECT
    'ACCOUNT' as entity_type,
    a.instruction_id,
    aid.identifier_type,
    aid.identifier_value,
    a.source_message_type,
    aid.created_at
FROM gold.cdm_account a
JOIN gold.cdm_account_identifier aid ON a.account_id = aid.account_id

UNION ALL

SELECT
    'FI' as entity_type,
    fi.instruction_id,
    fid.identifier_type,
    fid.identifier_value,
    fi.source_message_type,
    fid.created_at
FROM gold.cdm_financial_institution fi
JOIN gold.cdm_fi_identifier fid ON fi.fi_id = fid.fi_id;

COMMENT ON VIEW gold.v_identifier_lookup IS 'Lookup view to find payments by any identifier type/value';

-- Create index to support identifier lookups (via materialized view if needed for performance)
-- For now, the indexes on individual tables should suffice

-- ============================================================================
-- FUNCTIONS FOR IDENTIFIER MANAGEMENT
-- ============================================================================

-- Function: Add party identifier
CREATE OR REPLACE FUNCTION gold.add_party_identifier(
    p_party_id UUID,
    p_identifier_type VARCHAR(50),
    p_identifier_value VARCHAR(256),
    p_identifier_category VARCHAR(20) DEFAULT 'ORG_ID',
    p_scheme_name VARCHAR(140) DEFAULT NULL,
    p_is_primary BOOLEAN DEFAULT FALSE,
    p_source_message_type VARCHAR(50) DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_identifier_id UUID;
BEGIN
    INSERT INTO gold.cdm_party_identifier (
        party_id, identifier_category, identifier_type, identifier_value,
        scheme_name, is_primary, source_message_type
    )
    VALUES (
        p_party_id, p_identifier_category, p_identifier_type, p_identifier_value,
        p_scheme_name, p_is_primary, p_source_message_type
    )
    ON CONFLICT (party_id, identifier_category, identifier_type, identifier_value)
    DO UPDATE SET
        is_primary = COALESCE(EXCLUDED.is_primary, gold.cdm_party_identifier.is_primary),
        updated_at = CURRENT_TIMESTAMP
    RETURNING party_identifier_id INTO v_identifier_id;

    RETURN v_identifier_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Add account identifier
CREATE OR REPLACE FUNCTION gold.add_account_identifier(
    p_account_id UUID,
    p_identifier_type VARCHAR(50),
    p_identifier_value VARCHAR(256),
    p_scheme_name VARCHAR(140) DEFAULT NULL,
    p_is_primary BOOLEAN DEFAULT FALSE,
    p_source_message_type VARCHAR(50) DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_identifier_id UUID;
BEGIN
    INSERT INTO gold.cdm_account_identifier (
        account_id, identifier_type, identifier_value,
        scheme_name, is_primary, source_message_type
    )
    VALUES (
        p_account_id, p_identifier_type, p_identifier_value,
        p_scheme_name, p_is_primary, p_source_message_type
    )
    ON CONFLICT (account_id, identifier_type, identifier_value)
    DO UPDATE SET
        is_primary = COALESCE(EXCLUDED.is_primary, gold.cdm_account_identifier.is_primary),
        updated_at = CURRENT_TIMESTAMP
    RETURNING account_identifier_id INTO v_identifier_id;

    RETURN v_identifier_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Add FI identifier
CREATE OR REPLACE FUNCTION gold.add_fi_identifier(
    p_fi_id UUID,
    p_identifier_type VARCHAR(50),
    p_identifier_value VARCHAR(256),
    p_clearing_system_code VARCHAR(5) DEFAULT NULL,
    p_member_id VARCHAR(35) DEFAULT NULL,
    p_scheme_name VARCHAR(140) DEFAULT NULL,
    p_is_primary BOOLEAN DEFAULT FALSE,
    p_source_message_type VARCHAR(50) DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_identifier_id UUID;
BEGIN
    INSERT INTO gold.cdm_fi_identifier (
        fi_id, identifier_type, identifier_value,
        clearing_system_code, member_id, scheme_name,
        is_primary, source_message_type
    )
    VALUES (
        p_fi_id, p_identifier_type, p_identifier_value,
        p_clearing_system_code, p_member_id, p_scheme_name,
        p_is_primary, p_source_message_type
    )
    ON CONFLICT (fi_id, identifier_type, identifier_value)
    DO UPDATE SET
        clearing_system_code = COALESCE(EXCLUDED.clearing_system_code, gold.cdm_fi_identifier.clearing_system_code),
        member_id = COALESCE(EXCLUDED.member_id, gold.cdm_fi_identifier.member_id),
        is_primary = COALESCE(EXCLUDED.is_primary, gold.cdm_fi_identifier.is_primary),
        updated_at = CURRENT_TIMESTAMP
    RETURNING fi_identifier_id INTO v_identifier_id;

    RETURN v_identifier_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Add payment identifier
CREATE OR REPLACE FUNCTION gold.add_payment_identifier(
    p_instruction_id UUID,
    p_identifier_type VARCHAR(50),
    p_identifier_value VARCHAR(256),
    p_identifier_scope VARCHAR(50) DEFAULT 'INITIATING_PARTY',
    p_scheme_name VARCHAR(140) DEFAULT NULL,
    p_source_message_type VARCHAR(50) DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_identifier_id UUID;
BEGIN
    INSERT INTO gold.cdm_payment_identifier (
        instruction_id, identifier_type, identifier_value,
        identifier_scope, scheme_name, source_message_type
    )
    VALUES (
        p_instruction_id, p_identifier_type, p_identifier_value,
        p_identifier_scope, p_scheme_name, p_source_message_type
    )
    ON CONFLICT (instruction_id, identifier_type, identifier_value, identifier_scope)
    DO UPDATE SET
        scheme_name = COALESCE(EXCLUDED.scheme_name, gold.cdm_payment_identifier.scheme_name),
        updated_at = CURRENT_TIMESTAMP
    RETURNING payment_identifier_id INTO v_identifier_id;

    RETURN v_identifier_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Find payment by identifier
CREATE OR REPLACE FUNCTION gold.find_payment_by_identifier(
    p_identifier_type VARCHAR(50),
    p_identifier_value VARCHAR(256)
)
RETURNS TABLE (
    instruction_id UUID,
    entity_type VARCHAR(20),
    entity_id UUID,
    source_message_type VARCHAR(50),
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        il.instruction_id,
        il.entity_type::VARCHAR(20),
        il.instruction_id as entity_id,
        il.source_message_type,
        il.created_at
    FROM gold.v_identifier_lookup il
    WHERE il.identifier_type = p_identifier_type
      AND il.identifier_value = p_identifier_value;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION gold.add_party_identifier IS 'Add or update a party identifier with upsert semantics';
COMMENT ON FUNCTION gold.add_account_identifier IS 'Add or update an account identifier with upsert semantics';
COMMENT ON FUNCTION gold.add_fi_identifier IS 'Add or update a financial institution identifier with upsert semantics';
COMMENT ON FUNCTION gold.add_payment_identifier IS 'Add or update a payment identifier with upsert semantics';
COMMENT ON FUNCTION gold.find_payment_by_identifier IS 'Find payments by any identifier type and value';

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON gold.cdm_party_identifier TO gps_cdm_svc;
GRANT SELECT, INSERT, UPDATE ON gold.cdm_account_identifier TO gps_cdm_svc;
GRANT SELECT, INSERT, UPDATE ON gold.cdm_fi_identifier TO gps_cdm_svc;
GRANT SELECT, INSERT, UPDATE ON gold.cdm_payment_identifier TO gps_cdm_svc;
GRANT SELECT, INSERT, UPDATE ON gold.ref_identifier_type TO gps_cdm_svc;
GRANT SELECT ON gold.v_payment_all_identifiers TO gps_cdm_svc;
GRANT SELECT ON gold.v_identifier_lookup TO gps_cdm_svc;
GRANT EXECUTE ON FUNCTION gold.add_party_identifier TO gps_cdm_svc;
GRANT EXECUTE ON FUNCTION gold.add_account_identifier TO gps_cdm_svc;
GRANT EXECUTE ON FUNCTION gold.add_fi_identifier TO gps_cdm_svc;
GRANT EXECUTE ON FUNCTION gold.add_payment_identifier TO gps_cdm_svc;
GRANT EXECUTE ON FUNCTION gold.find_payment_by_identifier TO gps_cdm_svc;
