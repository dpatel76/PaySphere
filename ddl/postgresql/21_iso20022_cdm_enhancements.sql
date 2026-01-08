-- =============================================================================
-- GPS CDM - ISO 20022 Data Model Enhancements
-- =============================================================================
-- This DDL enhances the Gold CDM tables to align more closely with ISO 20022
-- data structures, enabling seamless mapping from ISO 20022 messages.
--
-- ISO 20022 Message → CDM Entity Mapping:
--   pacs.008 / pain.001:
--     - GrpHdr → cdm_payment_instruction (message-level)
--     - CdtTrfTxInf → cdm_payment_instruction (transaction-level)
--     - Dbtr/Cdtr → cdm_party
--     - DbtrAcct/CdtrAcct → cdm_account
--     - DbtrAgt/CdtrAgt → cdm_financial_institution
--
-- Key ISO 20022 Element Paths (for lineage):
--   - Party: Dbtr/Nm, Dbtr/PstlAdr/*, Dbtr/Id/OrgId/*, Dbtr/Id/PrvtId/*
--   - Account: DbtrAcct/Id/IBAN, DbtrAcct/Id/Othr/Id, DbtrAcct/Tp/Cd
--   - Agent: DbtrAgt/FinInstnId/BICFI, DbtrAgt/FinInstnId/ClrSysMmbId/*
--   - Amount: IntrBkSttlmAmt/@Ccy, InstdAmt/@Ccy
--   - References: PmtId/EndToEndId, PmtId/TxId, PmtId/UETR
-- =============================================================================

-- =============================================================================
-- CDM_PAYMENT_INSTRUCTION Enhancements
-- Add ISO 20022-specific fields for full pacs.008/pain.001 support
-- =============================================================================

-- Payment Identification (ISO 20022 PmtId element)
ALTER TABLE gold.cdm_payment_instruction
    ADD COLUMN IF NOT EXISTS instruction_identification VARCHAR(35),  -- InstrId
    ADD COLUMN IF NOT EXISTS clearing_system_reference VARCHAR(35);   -- ClrSysRef

-- Settlement Information (ISO 20022 SttlmInf element)
ALTER TABLE gold.cdm_payment_instruction
    ADD COLUMN IF NOT EXISTS settlement_method VARCHAR(10),           -- SttlmMtd (INDA, INGA, COVE, CLRG)
    ADD COLUMN IF NOT EXISTS settlement_account_iban VARCHAR(34),     -- SttlmAcct/Id/IBAN
    ADD COLUMN IF NOT EXISTS clearing_system VARCHAR(20);             -- ClrSys/Cd (e.g., FEDWIRE, CHIPS)

-- Payment Type Information (ISO 20022 PmtTpInf element)
ALTER TABLE gold.cdm_payment_instruction
    ADD COLUMN IF NOT EXISTS instruction_priority VARCHAR(10),        -- InstrPrty (HIGH, NORM)
    ADD COLUMN IF NOT EXISTS clearing_channel VARCHAR(20),            -- ClrChanl
    ADD COLUMN IF NOT EXISTS sequence_type VARCHAR(10);               -- SeqTp (for direct debits)

-- Regulatory Reporting (ISO 20022 RgltryRptg element)
ALTER TABLE gold.cdm_payment_instruction
    ADD COLUMN IF NOT EXISTS regulatory_reporting JSONB;              -- Full RgltryRptg structure

-- Related Remittance Information (ISO 20022 RltdRmtInf element)
ALTER TABLE gold.cdm_payment_instruction
    ADD COLUMN IF NOT EXISTS related_remittance_info JSONB;           -- RltdRmtInf array

-- Underlying Customer Credit Transfer (for cover payments)
ALTER TABLE gold.cdm_payment_instruction
    ADD COLUMN IF NOT EXISTS underlying_customer_transfer JSONB;      -- UndrlygCstmrCdtTrf

COMMENT ON COLUMN gold.cdm_payment_instruction.instruction_identification IS 'ISO 20022 PmtId/InstrId - Unique instruction ID assigned by instructing party';
COMMENT ON COLUMN gold.cdm_payment_instruction.clearing_system_reference IS 'ISO 20022 PmtId/ClrSysRef - Reference assigned by clearing system';
COMMENT ON COLUMN gold.cdm_payment_instruction.settlement_method IS 'ISO 20022 SttlmInf/SttlmMtd - INDA (Instructed Agent), INGA (Instructing Agent), COVE (Cover), CLRG (Clearing)';
COMMENT ON COLUMN gold.cdm_payment_instruction.clearing_system IS 'ISO 20022 ClrSys/Cd - Clearing system code (FEDWIRE, CHIPS, TARGET2, etc.)';


-- =============================================================================
-- CDM_PARTY Enhancements
-- Add ISO 20022 PartyIdentification fields
-- =============================================================================

-- Organization Identification (ISO 20022 OrgId element)
ALTER TABLE gold.cdm_party
    ADD COLUMN IF NOT EXISTS org_id_any_bic VARCHAR(11),              -- AnyBIC
    ADD COLUMN IF NOT EXISTS org_id_lei VARCHAR(20),                  -- LEI (already exists, ensure)
    ADD COLUMN IF NOT EXISTS org_id_other_id VARCHAR(50),             -- Othr/Id
    ADD COLUMN IF NOT EXISTS org_id_other_scheme_name VARCHAR(35),    -- Othr/SchmeNm/Cd or Prtry
    ADD COLUMN IF NOT EXISTS org_id_other_issuer VARCHAR(35);         -- Othr/Issr

-- Private Identification (ISO 20022 PrvtId element)
ALTER TABLE gold.cdm_party
    ADD COLUMN IF NOT EXISTS prvt_id_birth_date DATE,                 -- DtAndPlcOfBirth/BirthDt (already exists as date_of_birth)
    ADD COLUMN IF NOT EXISTS prvt_id_birth_province VARCHAR(35),      -- DtAndPlcOfBirth/PrvcOfBirth
    ADD COLUMN IF NOT EXISTS prvt_id_birth_city VARCHAR(35),          -- DtAndPlcOfBirth/CityOfBirth
    ADD COLUMN IF NOT EXISTS prvt_id_birth_country VARCHAR(3),        -- DtAndPlcOfBirth/CtryOfBirth
    ADD COLUMN IF NOT EXISTS prvt_id_other_id VARCHAR(50),            -- Othr/Id
    ADD COLUMN IF NOT EXISTS prvt_id_scheme_name VARCHAR(35),         -- Othr/SchmeNm/Cd
    ADD COLUMN IF NOT EXISTS prvt_id_issuer VARCHAR(35);              -- Othr/Issr

-- Contact Details (ISO 20022 CtctDtls element)
ALTER TABLE gold.cdm_party
    ADD COLUMN IF NOT EXISTS contact_name VARCHAR(140),               -- CtctDtls/Nm
    ADD COLUMN IF NOT EXISTS contact_phone VARCHAR(35),               -- CtctDtls/PhneNb
    ADD COLUMN IF NOT EXISTS contact_mobile VARCHAR(35),              -- CtctDtls/MobNb
    ADD COLUMN IF NOT EXISTS contact_fax VARCHAR(35),                 -- CtctDtls/FaxNb
    ADD COLUMN IF NOT EXISTS contact_email_address VARCHAR(254),      -- CtctDtls/EmailAdr
    ADD COLUMN IF NOT EXISTS contact_other VARCHAR(35);               -- CtctDtls/Othr

-- Postal Address Enhancements (ISO 20022 PstlAdr element - additional fields)
ALTER TABLE gold.cdm_party
    ADD COLUMN IF NOT EXISTS address_type VARCHAR(10),                -- AdrTp (ADDR, PBOX, HOME, BIZZ, MLTO, DLVY)
    ADD COLUMN IF NOT EXISTS department VARCHAR(70),                  -- Dept
    ADD COLUMN IF NOT EXISTS sub_department VARCHAR(70),              -- SubDept
    ADD COLUMN IF NOT EXISTS street_building_id VARCHAR(35),          -- BldgNb (already exists as building_number)
    ADD COLUMN IF NOT EXISTS floor VARCHAR(70),                       -- Flr
    ADD COLUMN IF NOT EXISTS room VARCHAR(70),                        -- Room
    ADD COLUMN IF NOT EXISTS post_box VARCHAR(16),                    -- PstBx
    ADD COLUMN IF NOT EXISTS district_name VARCHAR(35),               -- DstrctNm
    ADD COLUMN IF NOT EXISTS address_line3 VARCHAR(70),               -- AdrLine[3]
    ADD COLUMN IF NOT EXISTS address_line4 VARCHAR(70),               -- AdrLine[4]
    ADD COLUMN IF NOT EXISTS address_line5 VARCHAR(70),               -- AdrLine[5]
    ADD COLUMN IF NOT EXISTS address_line6 VARCHAR(70),               -- AdrLine[6]
    ADD COLUMN IF NOT EXISTS address_line7 VARCHAR(70);               -- AdrLine[7]

COMMENT ON COLUMN gold.cdm_party.org_id_any_bic IS 'ISO 20022 Id/OrgId/AnyBIC - Organization BIC code';
COMMENT ON COLUMN gold.cdm_party.org_id_lei IS 'ISO 20022 Id/OrgId/LEI - Legal Entity Identifier (20 chars)';
COMMENT ON COLUMN gold.cdm_party.address_type IS 'ISO 20022 PstlAdr/AdrTp - ADDR (Postal), PBOX (PO Box), HOME, BIZZ (Business), MLTO (Mail To), DLVY (Delivery)';


-- =============================================================================
-- CDM_ACCOUNT Enhancements
-- Add ISO 20022 CashAccount fields
-- =============================================================================

-- Account Identification (ISO 20022 Acct/Id element)
ALTER TABLE gold.cdm_account
    ADD COLUMN IF NOT EXISTS account_id_other VARCHAR(50),            -- Othr/Id (non-IBAN identifier)
    ADD COLUMN IF NOT EXISTS account_scheme_name VARCHAR(35),         -- Othr/SchmeNm/Cd or Prtry
    ADD COLUMN IF NOT EXISTS account_scheme_issuer VARCHAR(35);       -- Othr/Issr

-- Account Type (ISO 20022 Acct/Tp element)
ALTER TABLE gold.cdm_account
    ADD COLUMN IF NOT EXISTS account_type_code VARCHAR(10),           -- Tp/Cd (CACC, SVGS, LOAN, etc.)
    ADD COLUMN IF NOT EXISTS account_type_proprietary VARCHAR(35);    -- Tp/Prtry

-- Proxy (ISO 20022 Prxy element - for PayID, Proxy, Alias)
ALTER TABLE gold.cdm_account
    ADD COLUMN IF NOT EXISTS proxy_type VARCHAR(35),                  -- Prxy/Tp/Cd (TELE, EMAL, DNAM, etc.)
    ADD COLUMN IF NOT EXISTS proxy_id VARCHAR(256);                   -- Prxy/Id

-- Servicing Institution
ALTER TABLE gold.cdm_account
    ADD COLUMN IF NOT EXISTS servicing_institution_bic VARCHAR(11);   -- Svcr/FinInstnId/BICFI

COMMENT ON COLUMN gold.cdm_account.account_id_other IS 'ISO 20022 Acct/Id/Othr/Id - Non-IBAN account identifier';
COMMENT ON COLUMN gold.cdm_account.proxy_type IS 'ISO 20022 Prxy/Tp - PayID/Proxy type (TELE=phone, EMAL=email, DNAM=domain)';
COMMENT ON COLUMN gold.cdm_account.proxy_id IS 'ISO 20022 Prxy/Id - PayID/Proxy value (e.g., email@domain.com)';


-- =============================================================================
-- CDM_FINANCIAL_INSTITUTION Enhancements
-- Add ISO 20022 FinancialInstitutionIdentification fields
-- =============================================================================

-- Financial Institution Identification (ISO 20022 FinInstnId element)
ALTER TABLE gold.cdm_financial_institution
    ADD COLUMN IF NOT EXISTS clearing_system_member_id VARCHAR(35),   -- ClrSysMmbId/MmbId
    ADD COLUMN IF NOT EXISTS clearing_system_id VARCHAR(20),          -- ClrSysMmbId/ClrSysId/Cd
    ADD COLUMN IF NOT EXISTS clearing_system_proprietary VARCHAR(35); -- ClrSysMmbId/ClrSysId/Prtry

-- Other Identification
ALTER TABLE gold.cdm_financial_institution
    ADD COLUMN IF NOT EXISTS other_id VARCHAR(50),                    -- Othr/Id
    ADD COLUMN IF NOT EXISTS other_scheme_name VARCHAR(35),           -- Othr/SchmeNm/Cd
    ADD COLUMN IF NOT EXISTS other_issuer VARCHAR(35);                -- Othr/Issr

-- Postal Address (same structure as Party)
ALTER TABLE gold.cdm_financial_institution
    ADD COLUMN IF NOT EXISTS address_line2 VARCHAR(70),               -- PstlAdr/AdrLine[2]
    ADD COLUMN IF NOT EXISTS country_sub_division VARCHAR(35);        -- PstlAdr/CtrySubDvsn

-- Branch (ISO 20022 BrnchId element)
ALTER TABLE gold.cdm_financial_institution
    ADD COLUMN IF NOT EXISTS branch_identification_code VARCHAR(35),  -- BrnchId/Id
    ADD COLUMN IF NOT EXISTS branch_lei VARCHAR(20);                  -- BrnchId/LEI

COMMENT ON COLUMN gold.cdm_financial_institution.clearing_system_member_id IS 'ISO 20022 ClrSysMmbId/MmbId - Clearing system member ID (e.g., ABA RTN, Sort Code)';
COMMENT ON COLUMN gold.cdm_financial_institution.clearing_system_id IS 'ISO 20022 ClrSysMmbId/ClrSysId/Cd - Clearing system code (USABA, GBDSC, CHIPS, etc.)';


-- =============================================================================
-- CDM_REMITTANCE_INFORMATION (New Table)
-- ISO 20022 RmtInf structure - structured remittance data
-- =============================================================================
CREATE TABLE IF NOT EXISTS gold.cdm_remittance_information (
    remittance_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    payment_id VARCHAR(36) NOT NULL,

    -- Unstructured (ISO 20022 RmtInf/Ustrd)
    unstructured TEXT[],                                              -- Ustrd array (up to 140 chars each)

    -- Structured - Referred Document (ISO 20022 RmtInf/Strd/RfrdDocInf)
    document_type_code VARCHAR(10),                                   -- RfrdDocInf/Tp/CdOrPrtry/Cd (CINV, CREN, DEBN, etc.)
    document_type_proprietary VARCHAR(35),                            -- RfrdDocInf/Tp/CdOrPrtry/Prtry
    document_number VARCHAR(35),                                      -- RfrdDocInf/Nb
    document_related_date DATE,                                       -- RfrdDocInf/RltdDt
    document_line_details JSONB,                                      -- RfrdDocInf/LineDtls (array)

    -- Structured - Referred Document Amount (ISO 20022 RmtInf/Strd/RfrdDocAmt)
    due_payable_amount DECIMAL(18,4),                                 -- RfrdDocAmt/DuePyblAmt
    due_payable_currency VARCHAR(3),
    discount_applied_amount DECIMAL(18,4),                            -- RfrdDocAmt/DscntApldAmt
    credit_note_amount DECIMAL(18,4),                                 -- RfrdDocAmt/CdtNoteAmt
    tax_amount DECIMAL(18,4),                                         -- RfrdDocAmt/TaxAmt
    remitted_amount DECIMAL(18,4),                                    -- RfrdDocAmt/RmtdAmt
    remitted_currency VARCHAR(3),

    -- Structured - Creditor Reference (ISO 20022 RmtInf/Strd/CdtrRefInf)
    creditor_reference_type VARCHAR(10),                              -- CdtrRefInf/Tp/CdOrPrtry/Cd (RADM, RPIN, FXDR, etc.)
    creditor_reference VARCHAR(35),                                   -- CdtrRefInf/Ref

    -- Structured - Invoicer/Invoicee
    invoicer_name VARCHAR(140),                                       -- Invcr/Nm
    invoicee_name VARCHAR(140),                                       -- Invcee/Nm

    -- Additional Remittance Information
    additional_info TEXT,                                             -- AddtlRmtInf

    -- Source
    source_system VARCHAR(100) NOT NULL,
    source_message_type VARCHAR(50),
    source_stg_id VARCHAR(36),

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    record_version INT DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_cdm_remit_payment ON gold.cdm_remittance_information(payment_id);
CREATE INDEX IF NOT EXISTS idx_cdm_remit_doc ON gold.cdm_remittance_information(document_number);
CREATE INDEX IF NOT EXISTS idx_cdm_remit_ref ON gold.cdm_remittance_information(creditor_reference);

COMMENT ON TABLE gold.cdm_remittance_information IS 'ISO 20022 RmtInf structure - Structured and unstructured remittance data associated with payments';


-- =============================================================================
-- CDM_REGULATORY_REPORTING (New Table)
-- ISO 20022 RgltryRptg structure
-- =============================================================================
CREATE TABLE IF NOT EXISTS gold.cdm_regulatory_reporting (
    reporting_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    payment_id VARCHAR(36) NOT NULL,

    -- Authority (ISO 20022 RgltryRptg/Authrty)
    authority_name VARCHAR(140),                                      -- Authrty/Nm
    authority_country VARCHAR(3),                                     -- Authrty/Ctry

    -- Details (ISO 20022 RgltryRptg/Dtls)
    reporting_type VARCHAR(10),                                       -- Dtls/Tp (CRED, DEBT, BOTH)
    reporting_date DATE,                                              -- Dtls/Dt
    reporting_country VARCHAR(3),                                     -- Dtls/Ctry
    reporting_code VARCHAR(10),                                       -- Dtls/Cd
    reporting_amount DECIMAL(18,4),                                   -- Dtls/Amt
    reporting_currency VARCHAR(3),
    reporting_information TEXT,                                       -- Dtls/Inf

    -- Source
    source_system VARCHAR(100) NOT NULL,
    source_message_type VARCHAR(50),
    source_stg_id VARCHAR(36),

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    record_version INT DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_cdm_regrpt_payment ON gold.cdm_regulatory_reporting(payment_id);
CREATE INDEX IF NOT EXISTS idx_cdm_regrpt_country ON gold.cdm_regulatory_reporting(authority_country);

COMMENT ON TABLE gold.cdm_regulatory_reporting IS 'ISO 20022 RgltryRptg structure - Regulatory reporting requirements for cross-border payments';


-- =============================================================================
-- CDM_PAYMENT_STATUS (New Table)
-- ISO 20022 pacs.002 / pain.002 status tracking
-- =============================================================================
CREATE TABLE IF NOT EXISTS gold.cdm_payment_status (
    status_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    payment_id VARCHAR(36) NOT NULL,

    -- Original Reference (ISO 20022 OrgnlGrpInfAndSts / OrgnlPmtInfAndSts)
    original_message_id VARCHAR(35),                                  -- OrgnlMsgId
    original_message_name_id VARCHAR(35),                             -- OrgnlMsgNmId
    original_end_to_end_id VARCHAR(35),                               -- OrgnlEndToEndId
    original_transaction_id VARCHAR(35),                              -- OrgnlTxId
    original_uetr VARCHAR(36),                                        -- OrgnlUETR

    -- Status (ISO 20022 TxInfAndSts)
    group_status VARCHAR(10),                                         -- GrpSts (ACCP, RJCT, PDNG, etc.)
    transaction_status VARCHAR(10),                                   -- TxSts
    status_reason_code VARCHAR(10),                                   -- StsRsnInf/Rsn/Cd
    status_reason_proprietary VARCHAR(35),                            -- StsRsnInf/Rsn/Prtry
    additional_status_info TEXT,                                      -- StsRsnInf/AddtlInf

    -- Acceptance Date Time
    acceptance_datetime TIMESTAMP,                                    -- AccptncDtTm

    -- Tracking Indicator
    tracker_reason_code VARCHAR(10),                                  -- TrckrData/TrackerRcrd/TrackerSts/Rsn

    -- Source
    source_system VARCHAR(100) NOT NULL,
    source_message_type VARCHAR(50),                                  -- pacs.002, pain.002, etc.
    source_stg_id VARCHAR(36),

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    record_version INT DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_cdm_status_payment ON gold.cdm_payment_status(payment_id);
CREATE INDEX IF NOT EXISTS idx_cdm_status_orig ON gold.cdm_payment_status(original_message_id);
CREATE INDEX IF NOT EXISTS idx_cdm_status_e2e ON gold.cdm_payment_status(original_end_to_end_id);
CREATE INDEX IF NOT EXISTS idx_cdm_status_uetr ON gold.cdm_payment_status(original_uetr);
CREATE INDEX IF NOT EXISTS idx_cdm_status_code ON gold.cdm_payment_status(transaction_status);

COMMENT ON TABLE gold.cdm_payment_status IS 'ISO 20022 Status messages (pacs.002/pain.002) - Tracks payment status updates with original references';


-- =============================================================================
-- Add Role column to entity tables (for relationship tracking)
-- =============================================================================
ALTER TABLE gold.cdm_party
    ADD COLUMN IF NOT EXISTS role VARCHAR(30);                        -- DEBTOR, CREDITOR, ULTIMATE_DEBTOR, ULTIMATE_CREDITOR, INITIATING_PARTY

ALTER TABLE gold.cdm_account
    ADD COLUMN IF NOT EXISTS role VARCHAR(30);                        -- DEBTOR, CREDITOR

ALTER TABLE gold.cdm_financial_institution
    ADD COLUMN IF NOT EXISTS role VARCHAR(30);                        -- DEBTOR_AGENT, CREDITOR_AGENT, INTERMEDIARY_AGENT1, INTERMEDIARY_AGENT2

-- Create indexes for role lookups
CREATE INDEX IF NOT EXISTS idx_cdm_party_role ON gold.cdm_party(role);
CREATE INDEX IF NOT EXISTS idx_cdm_account_role ON gold.cdm_account(role);
CREATE INDEX IF NOT EXISTS idx_cdm_fi_role ON gold.cdm_financial_institution(role);

COMMENT ON COLUMN gold.cdm_party.role IS 'ISO 20022 party role in payment: DEBTOR, CREDITOR, ULTIMATE_DEBTOR, ULTIMATE_CREDITOR, INITIATING_PARTY';
COMMENT ON COLUMN gold.cdm_account.role IS 'ISO 20022 account role in payment: DEBTOR, CREDITOR';
COMMENT ON COLUMN gold.cdm_financial_institution.role IS 'ISO 20022 agent role: DEBTOR_AGENT, CREDITOR_AGENT, INTERMEDIARY_AGENT1, INTERMEDIARY_AGENT2, INSTRUCTING_AGENT, INSTRUCTED_AGENT';


-- =============================================================================
-- View: ISO 20022 Payment Summary
-- Consolidated view of payment with all related ISO 20022 entities
-- =============================================================================
CREATE OR REPLACE VIEW gold.v_iso20022_payment_summary AS
SELECT
    pi.instruction_id,
    pi.payment_id,
    pi.source_message_type,
    pi.end_to_end_id,
    pi.uetr,
    pi.transaction_id,

    -- Amounts
    pi.instructed_amount,
    pi.instructed_currency,
    pi.interbank_settlement_amount,
    pi.interbank_settlement_currency,

    -- Dates
    pi.creation_datetime,
    pi.requested_execution_date,
    pi.settlement_date,

    -- Debtor (Dbtr)
    dbtr.name AS debtor_name,
    dbtr.country AS debtor_country,
    dbtr_acct.iban AS debtor_iban,
    dbtr_acct.account_number AS debtor_account,
    dbtr_agt.bic AS debtor_agent_bic,
    dbtr_agt.institution_name AS debtor_agent_name,

    -- Creditor (Cdtr)
    cdtr.name AS creditor_name,
    cdtr.country AS creditor_country,
    cdtr_acct.iban AS creditor_iban,
    cdtr_acct.account_number AS creditor_account,
    cdtr_agt.bic AS creditor_agent_bic,
    cdtr_agt.institution_name AS creditor_agent_name,

    -- Purpose & Remittance
    pi.purpose,
    pi.purpose_description,
    pi.remittance_unstructured,
    pi.remittance_reference,

    -- Status
    pi.current_status,
    pi.status_reason_code,

    -- Clearing
    pi.clearing_system,
    pi.settlement_method,

    -- Metadata
    pi.created_at,
    pi.lineage_batch_id

FROM gold.cdm_payment_instruction pi
LEFT JOIN gold.cdm_party dbtr ON pi.debtor_id = dbtr.party_id
LEFT JOIN gold.cdm_account dbtr_acct ON pi.debtor_account_id = dbtr_acct.account_id
LEFT JOIN gold.cdm_financial_institution dbtr_agt ON pi.debtor_agent_id = dbtr_agt.fi_id
LEFT JOIN gold.cdm_party cdtr ON pi.creditor_id = cdtr.party_id
LEFT JOIN gold.cdm_account cdtr_acct ON pi.creditor_account_id = cdtr_acct.account_id
LEFT JOIN gold.cdm_financial_institution cdtr_agt ON pi.creditor_agent_id = cdtr_agt.fi_id
WHERE pi.is_current = TRUE AND pi.is_deleted = FALSE;

COMMENT ON VIEW gold.v_iso20022_payment_summary IS 'Consolidated ISO 20022 payment view with denormalized debtor/creditor/agent details';


-- =============================================================================
-- Summary
-- =============================================================================
DO $$
BEGIN
    RAISE NOTICE 'ISO 20022 CDM Enhancements Complete';
    RAISE NOTICE '===================================';
    RAISE NOTICE 'Enhanced tables:';
    RAISE NOTICE '  - cdm_payment_instruction: Added PmtId, SttlmInf, PmtTpInf fields';
    RAISE NOTICE '  - cdm_party: Added OrgId, PrvtId, CtctDtls, extended PstlAdr';
    RAISE NOTICE '  - cdm_account: Added Othr identification, Prxy (PayID), Tp fields';
    RAISE NOTICE '  - cdm_financial_institution: Added ClrSysMmbId, Othr, BrnchId';
    RAISE NOTICE 'New tables:';
    RAISE NOTICE '  - cdm_remittance_information: ISO 20022 RmtInf structure';
    RAISE NOTICE '  - cdm_regulatory_reporting: ISO 20022 RgltryRptg structure';
    RAISE NOTICE '  - cdm_payment_status: ISO 20022 pacs.002/pain.002 status tracking';
END $$;
