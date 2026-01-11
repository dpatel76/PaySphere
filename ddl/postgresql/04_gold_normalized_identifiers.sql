-- GPS CDM - Gold Layer Normalized Identifier Tables
-- ==================================================
-- These tables normalize ALL identifier types from 72+ payment standards
-- into a unified structure with standardized identifier type codes.
--
-- Design Principles:
-- 1. Each identifier type from any standard maps to a standardized CDM type
-- 2. Source message format is tracked for provenance
-- 3. All identifier values are stored with their original format
-- 4. Cross-references link identifiers to their parent entities

-- =====================================================
-- REFERENCE TABLE: Identifier Type Codes
-- =====================================================
-- Standardized codes for all identifier types across 72+ payment standards

CREATE TABLE IF NOT EXISTS gold.ref_identifier_type (
    identifier_type_code VARCHAR(30) PRIMARY KEY,
    identifier_category VARCHAR(30) NOT NULL,  -- TRANSACTION, PARTY, ACCOUNT, INSTITUTION, DOCUMENT
    description VARCHAR(200) NOT NULL,
    max_length INT,
    format_pattern VARCHAR(100),  -- Regex or description of valid format
    iso_standard VARCHAR(50),     -- ISO standard if applicable (e.g., ISO 17442 for LEI)
    is_globally_unique BOOLEAN DEFAULT FALSE,
    validation_rules JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert all standardized identifier types
INSERT INTO gold.ref_identifier_type (identifier_type_code, identifier_category, description, max_length, format_pattern, iso_standard, is_globally_unique) VALUES
-- Transaction/Message Identifiers (24 types)
('END_TO_END_ID', 'TRANSACTION', 'End-to-end unique identifier passed through entire payment chain', 35, 'Alphanumeric', 'ISO 20022', FALSE),
('UETR', 'TRANSACTION', 'Universal End-to-End Transaction Reference (UUID format)', 36, 'UUID v4', 'SWIFT gpi', TRUE),
('TRANSACTION_ID', 'TRANSACTION', 'Transaction identification assigned by instructing agent', 35, 'Alphanumeric', 'ISO 20022', FALSE),
('INSTRUCTION_ID', 'TRANSACTION', 'Instruction identification for a single transaction', 35, 'Alphanumeric', 'ISO 20022', FALSE),
('MESSAGE_ID', 'TRANSACTION', 'Message-level unique identifier', 35, 'Alphanumeric', 'ISO 20022', FALSE),
('PAYMENT_INFO_ID', 'TRANSACTION', 'Payment Information identification (batch level)', 35, 'Alphanumeric', 'ISO 20022', FALSE),
('IMAD', 'TRANSACTION', 'Input Message Accountability Data (Fedwire)', 32, 'Alphanumeric', 'Fedwire', TRUE),
('OMAD', 'TRANSACTION', 'Output Message Accountability Data (Fedwire)', 32, 'Alphanumeric', 'Fedwire', TRUE),
('SENDER_REF', 'TRANSACTION', 'Sender reference number (SWIFT MT Field 20)', 16, 'Alphanumeric', 'SWIFT MT', FALSE),
('RELATED_REF', 'TRANSACTION', 'Related reference (SWIFT MT Field 21)', 16, 'Alphanumeric', 'SWIFT MT', FALSE),
('CHIPS_UID', 'TRANSACTION', 'CHIPS Universal Payment Identifier', 16, 'YYYYMMDDNNNNNNNN', 'CHIPS', TRUE),
('CHIPS_SEQUENCE', 'TRANSACTION', 'CHIPS Sequence Number', 6, 'Numeric', 'CHIPS', FALSE),
('CLEARING_SYS_REF', 'TRANSACTION', 'Clearing System Reference', 35, 'Alphanumeric', 'ISO 20022', FALSE),
('ACH_TRACE', 'TRANSACTION', 'ACH Trace Number (Routing + Sequence)', 15, 'Numeric', 'NACHA', FALSE),
('ACH_BATCH', 'TRANSACTION', 'ACH Batch Number', 7, 'Numeric', 'NACHA', FALSE),
('PIX_E2E_ID', 'TRANSACTION', 'PIX End-to-End Identifier', 32, 'E[0-9]{31}', 'PIX/BCB', TRUE),
('PIX_RETURN_ID', 'TRANSACTION', 'PIX Return Identifier', 35, 'Alphanumeric', 'PIX/BCB', FALSE),
('PIX_DEVOLUTION_ID', 'TRANSACTION', 'PIX Devolution Identifier', 32, 'D[0-9]{31}', 'PIX/BCB', FALSE),
('MANDATE_ID', 'TRANSACTION', 'Direct Debit Mandate Identifier', 35, 'Alphanumeric', 'ISO 20022', FALSE),
('ORIGINAL_MSG_ID', 'TRANSACTION', 'Original Message ID for returns/reversals', 35, 'Alphanumeric', 'ISO 20022', FALSE),
('MUR', 'TRANSACTION', 'Message User Reference (SWIFT Block 3)', 16, 'Alphanumeric', 'SWIFT MT', FALSE),
('SEPA_TXN_ID', 'TRANSACTION', 'SEPA Transaction Identifier', 35, 'Alphanumeric', 'SEPA', FALSE),
('RTP_TXN_ID', 'TRANSACTION', 'RTP Transaction Identifier', 35, 'Alphanumeric', 'TCH RTP', FALSE),
('RECONCILIATION_ID', 'TRANSACTION', 'Reconciliation Identifier', 35, 'Alphanumeric', NULL, FALSE),

-- Party Identifiers (15 types)
('LEI', 'PARTY', 'Legal Entity Identifier', 20, '[A-Z0-9]{4}00[A-Z0-9]{12}[0-9]{2}', 'ISO 17442', TRUE),
('BIC_PARTY', 'PARTY', 'BIC for non-FI party identification', 11, 'BIC format', 'ISO 9362', FALSE),
('TAX_ID', 'PARTY', 'Tax Identification Number (generic)', 35, 'Alphanumeric', NULL, FALSE),
('TIN_US', 'PARTY', 'US Tax Identification Number (EIN/SSN)', 11, 'Numeric with hyphen', 'IRS', FALSE),
('CPF', 'PARTY', 'Brazil Individual Tax ID (CPF)', 11, 'Numeric', 'Brazil RFB', FALSE),
('CNPJ', 'PARTY', 'Brazil Entity Tax ID (CNPJ)', 14, 'Numeric', 'Brazil RFB', FALSE),
('NATIONAL_ID', 'PARTY', 'National ID Card Number', 35, 'Alphanumeric', NULL, FALSE),
('PASSPORT', 'PARTY', 'Passport Number', 35, 'Alphanumeric', 'ICAO', FALSE),
('DRIVERS_LICENSE', 'PARTY', 'Drivers License Number', 35, 'Alphanumeric', NULL, FALSE),
('REGISTRATION_NUM', 'PARTY', 'Company Registration Number', 35, 'Alphanumeric', NULL, FALSE),
('CUSTOMER_ID', 'PARTY', 'Proprietary Customer Identifier', 35, 'Alphanumeric', NULL, FALSE),
('CREDITOR_SCHEME_ID', 'PARTY', 'SEPA Creditor Scheme Identifier', 35, 'Alphanumeric', 'SEPA', FALSE),
('PIX_KEY', 'PARTY', 'PIX Key (Phone/Email/CPF/CNPJ/EVP)', 77, 'Various formats', 'PIX/BCB', FALSE),
('INDIVIDUAL_ID', 'PARTY', 'ACH Individual Identification Number', 15, 'Alphanumeric', 'NACHA', FALSE),
('PARTY_PROPRIETARY', 'PARTY', 'Other proprietary party identifier', 35, 'Alphanumeric', NULL, FALSE),

-- Account Identifiers (12 types)
('IBAN', 'ACCOUNT', 'International Bank Account Number', 34, '[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}', 'ISO 13616', FALSE),
('BBAN', 'ACCOUNT', 'Basic Bank Account Number', 30, 'Alphanumeric', NULL, FALSE),
('ACCOUNT_NUM', 'ACCOUNT', 'Proprietary Account Number', 34, 'Alphanumeric', NULL, FALSE),
('DFI_ACCOUNT', 'ACCOUNT', 'DFI Account Number (ACH)', 17, 'Alphanumeric', 'NACHA', FALSE),
('CHIPS_ACCOUNT', 'ACCOUNT', 'CHIPS Participant Account', 34, 'Alphanumeric', 'CHIPS', FALSE),
('PIX_ACCOUNT', 'ACCOUNT', 'PIX Account Identifier', 20, 'Alphanumeric', 'PIX/BCB', FALSE),
('UPIC', 'ACCOUNT', 'Universal Payment Identification Code', 12, 'Numeric', 'NACHA', FALSE),
('VIRTUAL_ACCOUNT', 'ACCOUNT', 'Virtual Account Number', 34, 'Alphanumeric', NULL, FALSE),
('WALLET_ID', 'ACCOUNT', 'Digital Wallet Identifier', 50, 'Alphanumeric', NULL, FALSE),
('CARD_PAN', 'ACCOUNT', 'Card Primary Account Number (masked)', 19, 'Numeric', 'ISO 7812', FALSE),
('PROXY_ID', 'ACCOUNT', 'Proxy/Alias Account Identifier', 50, 'Alphanumeric', NULL, FALSE),
('ACCOUNT_PROPRIETARY', 'ACCOUNT', 'Other proprietary account identifier', 34, 'Alphanumeric', NULL, FALSE),

-- Institution Identifiers (18 types)
('BIC', 'INSTITUTION', 'Bank Identifier Code (SWIFT)', 11, '[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?', 'ISO 9362', TRUE),
('ABA_RTN', 'INSTITUTION', 'ABA Routing Transit Number', 9, 'Numeric', 'ABA', FALSE),
('CHIPS_PARTICIPANT', 'INSTITUTION', 'CHIPS Participant Identifier', 4, 'Numeric', 'CHIPS', FALSE),
('CHIPS_UID_INST', 'INSTITUTION', 'CHIPS Universal Identifier for FI', 6, 'Numeric', 'CHIPS', FALSE),
('SORT_CODE', 'INSTITUTION', 'UK Sort Code', 6, 'Numeric', 'UK Payments', FALSE),
('BSB', 'INSTITUTION', 'Australian Bank-State-Branch Code', 6, 'Numeric', 'APCA', FALSE),
('IFSC', 'INSTITUTION', 'Indian Financial System Code', 11, '[A-Z]{4}0[A-Z0-9]{6}', 'RBI', FALSE),
('CNAPS', 'INSTITUTION', 'China National Advanced Payment System Code', 12, 'Numeric', 'PBOC', FALSE),
('ISPB', 'INSTITUTION', 'Brazil Institution Code (ISPB)', 8, 'Numeric', 'BCB', FALSE),
('SWIFT_CODE', 'INSTITUTION', 'SWIFT Code (alias for BIC)', 11, 'BIC format', 'ISO 9362', TRUE),
('NATIONAL_CLR_CODE', 'INSTITUTION', 'National Clearing System Member ID', 35, 'Alphanumeric', NULL, FALSE),
('RSSD', 'INSTITUTION', 'Federal Reserve RSSD ID', 10, 'Numeric', 'FRB', FALSE),
('LEI_FI', 'INSTITUTION', 'LEI for Financial Institution', 20, 'LEI format', 'ISO 17442', TRUE),
('BRANCH_ID', 'INSTITUTION', 'Branch Identifier', 35, 'Alphanumeric', NULL, FALSE),
('CLEARING_MEMBER_ID', 'INSTITUTION', 'Clearing System Member ID', 35, 'Alphanumeric', NULL, FALSE),
('ZENGIN_CODE', 'INSTITUTION', 'Japan Zengin Bank Code', 7, 'Numeric', 'JBA', FALSE),
('TRANSIT_NUM', 'INSTITUTION', 'Canadian Transit Number', 9, 'Numeric', 'CPA', FALSE),
('INSTITUTION_PROPRIETARY', 'INSTITUTION', 'Other proprietary institution identifier', 35, 'Alphanumeric', NULL, FALSE),

-- Document/Remittance Identifiers (10 types)
('INVOICE_NUM', 'DOCUMENT', 'Invoice Number', 35, 'Alphanumeric', NULL, FALSE),
('PURCHASE_ORDER', 'DOCUMENT', 'Purchase Order Number', 35, 'Alphanumeric', NULL, FALSE),
('CREDITOR_REF', 'DOCUMENT', 'Creditor Reference (ISO 11649)', 35, 'RF[0-9]{2}[A-Z0-9]{1,21}', 'ISO 11649', FALSE),
('DOCUMENT_NUM', 'DOCUMENT', 'Generic Document Number', 35, 'Alphanumeric', NULL, FALSE),
('CONTRACT_NUM', 'DOCUMENT', 'Contract Number', 35, 'Alphanumeric', NULL, FALSE),
('REMITTANCE_ID', 'DOCUMENT', 'Remittance Information Identifier', 35, 'Alphanumeric', NULL, FALSE),
('CREDIT_NOTE', 'DOCUMENT', 'Credit Note Number', 35, 'Alphanumeric', NULL, FALSE),
('DEBIT_NOTE', 'DOCUMENT', 'Debit Note Number', 35, 'Alphanumeric', NULL, FALSE),
('TAX_REF', 'DOCUMENT', 'Tax Reference Number', 140, 'Alphanumeric', NULL, FALSE),
('REGULATORY_CODE', 'DOCUMENT', 'Regulatory Reporting Code', 10, 'Alphanumeric', NULL, FALSE)

ON CONFLICT (identifier_type_code) DO UPDATE SET
    description = EXCLUDED.description,
    max_length = EXCLUDED.max_length;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ref_id_type_category ON gold.ref_identifier_type(identifier_category);

-- =====================================================
-- REFERENCE TABLE: Message Format to Identifier Type Mapping
-- =====================================================
-- Maps source message format identifier names to standardized types

CREATE TABLE IF NOT EXISTS gold.ref_identifier_source_mapping (
    mapping_id SERIAL PRIMARY KEY,
    message_format VARCHAR(50) NOT NULL,        -- pain.001, MT103, FEDWIRE, pacs.008, etc.
    source_field_name VARCHAR(100) NOT NULL,    -- Original field name in source standard
    source_field_path VARCHAR(200),             -- XPath or field path in source
    identifier_type_code VARCHAR(30) NOT NULL REFERENCES gold.ref_identifier_type(identifier_type_code),
    identifier_category VARCHAR(30) NOT NULL,   -- TRANSACTION, PARTY, ACCOUNT, INSTITUTION, DOCUMENT
    entity_role VARCHAR(50),                    -- DEBTOR, CREDITOR, DEBTOR_AGENT, CREDITOR_AGENT, etc.
    notes VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(message_format, source_field_name, entity_role)
);

-- Insert mappings for pain.001
INSERT INTO gold.ref_identifier_source_mapping (message_format, source_field_name, source_field_path, identifier_type_code, identifier_category, entity_role, notes) VALUES
-- pain.001 Transaction Identifiers
('pain.001', 'MsgId', 'GrpHdr/MsgId', 'MESSAGE_ID', 'TRANSACTION', NULL, 'Message-level unique identifier'),
('pain.001', 'PmtInfId', 'PmtInf/PmtInfId', 'PAYMENT_INFO_ID', 'TRANSACTION', NULL, 'Payment Information batch ID'),
('pain.001', 'InstrId', 'CdtTrfTxInf/PmtId/InstrId', 'INSTRUCTION_ID', 'TRANSACTION', NULL, 'Instruction ID per transaction'),
('pain.001', 'EndToEndId', 'CdtTrfTxInf/PmtId/EndToEndId', 'END_TO_END_ID', 'TRANSACTION', NULL, 'End-to-end unique reference'),
('pain.001', 'UETR', 'CdtTrfTxInf/PmtId/UETR', 'UETR', 'TRANSACTION', NULL, 'SWIFT gpi UETR'),
-- pain.001 Party Identifiers
('pain.001', 'InitgPty/LEI', 'GrpHdr/InitgPty/Id/OrgId/LEI', 'LEI', 'PARTY', 'INITIATING_PARTY', 'Initiating party LEI'),
('pain.001', 'InitgPty/OthrId', 'GrpHdr/InitgPty/Id/OrgId/Othr/Id', 'PARTY_PROPRIETARY', 'PARTY', 'INITIATING_PARTY', 'Initiating party other ID'),
('pain.001', 'Dbtr/LEI', 'PmtInf/Dbtr/Id/OrgId/LEI', 'LEI', 'PARTY', 'DEBTOR', 'Debtor LEI'),
('pain.001', 'Dbtr/OthrId', 'PmtInf/Dbtr/Id/OrgId/Othr/Id', 'PARTY_PROPRIETARY', 'PARTY', 'DEBTOR', 'Debtor other ID'),
('pain.001', 'Dbtr/TaxId', 'PmtInf/Dbtr/Id/PrvtId/Othr/Id', 'TAX_ID', 'PARTY', 'DEBTOR', 'Debtor Tax ID'),
('pain.001', 'UltmtDbtr/LEI', 'PmtInf/UltmtDbtr/Id/OrgId/LEI', 'LEI', 'PARTY', 'ULTIMATE_DEBTOR', 'Ultimate debtor LEI'),
('pain.001', 'Cdtr/LEI', 'CdtTrfTxInf/Cdtr/Id/OrgId/LEI', 'LEI', 'PARTY', 'CREDITOR', 'Creditor LEI'),
('pain.001', 'Cdtr/OthrId', 'CdtTrfTxInf/Cdtr/Id/OrgId/Othr/Id', 'PARTY_PROPRIETARY', 'PARTY', 'CREDITOR', 'Creditor other ID'),
('pain.001', 'UltmtCdtr/LEI', 'CdtTrfTxInf/UltmtCdtr/Id/OrgId/LEI', 'LEI', 'PARTY', 'ULTIMATE_CREDITOR', 'Ultimate creditor LEI'),
-- pain.001 Account Identifiers
('pain.001', 'DbtrAcct/IBAN', 'PmtInf/DbtrAcct/Id/IBAN', 'IBAN', 'ACCOUNT', 'DEBTOR', 'Debtor account IBAN'),
('pain.001', 'DbtrAcct/Othr', 'PmtInf/DbtrAcct/Id/Othr/Id', 'ACCOUNT_NUM', 'ACCOUNT', 'DEBTOR', 'Debtor account other'),
('pain.001', 'CdtrAcct/IBAN', 'CdtTrfTxInf/CdtrAcct/Id/IBAN', 'IBAN', 'ACCOUNT', 'CREDITOR', 'Creditor account IBAN'),
('pain.001', 'CdtrAcct/Othr', 'CdtTrfTxInf/CdtrAcct/Id/Othr/Id', 'ACCOUNT_NUM', 'ACCOUNT', 'CREDITOR', 'Creditor account other'),
-- pain.001 Institution Identifiers
('pain.001', 'DbtrAgt/BIC', 'PmtInf/DbtrAgt/FinInstnId/BICFI', 'BIC', 'INSTITUTION', 'DEBTOR_AGENT', 'Debtor agent BIC'),
('pain.001', 'DbtrAgt/ClrSysMmbId', 'PmtInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'NATIONAL_CLR_CODE', 'INSTITUTION', 'DEBTOR_AGENT', 'Debtor agent clearing member ID'),
('pain.001', 'CdtrAgt/BIC', 'CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI', 'BIC', 'INSTITUTION', 'CREDITOR_AGENT', 'Creditor agent BIC'),
('pain.001', 'CdtrAgt/ClrSysMmbId', 'CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'NATIONAL_CLR_CODE', 'INSTITUTION', 'CREDITOR_AGENT', 'Creditor agent clearing member ID'),
('pain.001', 'IntrmyAgt1/BIC', 'CdtTrfTxInf/IntrmyAgt1/FinInstnId/BICFI', 'BIC', 'INSTITUTION', 'INTERMEDIARY_1', 'Intermediary agent 1 BIC'),
('pain.001', 'IntrmyAgt2/BIC', 'CdtTrfTxInf/IntrmyAgt2/FinInstnId/BICFI', 'BIC', 'INSTITUTION', 'INTERMEDIARY_2', 'Intermediary agent 2 BIC'),
('pain.001', 'IntrmyAgt3/BIC', 'CdtTrfTxInf/IntrmyAgt3/FinInstnId/BICFI', 'BIC', 'INSTITUTION', 'INTERMEDIARY_3', 'Intermediary agent 3 BIC'),
-- pain.001 Document Identifiers
('pain.001', 'CdtrRefInf/Ref', 'CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Ref', 'CREDITOR_REF', 'DOCUMENT', NULL, 'Creditor reference'),
('pain.001', 'RfrdDocInf/Nb', 'CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Nb', 'DOCUMENT_NUM', 'DOCUMENT', NULL, 'Referenced document number')

ON CONFLICT (message_format, source_field_name, entity_role) DO NOTHING;

-- Insert mappings for MT103
INSERT INTO gold.ref_identifier_source_mapping (message_format, source_field_name, source_field_path, identifier_type_code, identifier_category, entity_role, notes) VALUES
-- MT103 Transaction Identifiers
('MT103', 'Field20', ':20:', 'SENDER_REF', 'TRANSACTION', NULL, 'Transaction Reference Number (max 16 chars)'),
('MT103', 'Field21', ':21:', 'RELATED_REF', 'TRANSACTION', NULL, 'Related Reference'),
('MT103', 'MUR', '{108:}', 'MUR', 'TRANSACTION', NULL, 'Message User Reference'),
('MT103', 'UETR', '{121:}', 'UETR', 'TRANSACTION', NULL, 'SWIFT gpi UETR'),
-- MT103 Party Identifiers
('MT103', 'Field50K', ':50K:', 'CUSTOMER_ID', 'PARTY', 'DEBTOR', 'Ordering Customer (4x35)'),
('MT103', 'Field50A/BIC', ':50A:', 'BIC_PARTY', 'PARTY', 'DEBTOR', 'Ordering Customer BIC'),
('MT103', 'Field50F/ID', ':50F:', 'PARTY_PROPRIETARY', 'PARTY', 'DEBTOR', 'Ordering Customer structured ID'),
('MT103', 'Field59', ':59:', 'CUSTOMER_ID', 'PARTY', 'CREDITOR', 'Beneficiary Customer (4x35)'),
('MT103', 'Field59A/BIC', ':59A:', 'BIC_PARTY', 'PARTY', 'CREDITOR', 'Beneficiary Customer BIC'),
('MT103', 'Field59F/ID', ':59F:', 'PARTY_PROPRIETARY', 'PARTY', 'CREDITOR', 'Beneficiary Customer structured ID'),
-- MT103 Account Identifiers
('MT103', 'Field50/Account', ':50:', 'ACCOUNT_NUM', 'ACCOUNT', 'DEBTOR', 'Ordering Customer Account'),
('MT103', 'Field59/Account', ':59:', 'ACCOUNT_NUM', 'ACCOUNT', 'CREDITOR', 'Beneficiary Account'),
-- MT103 Institution Identifiers
('MT103', 'SenderBIC', 'Block1', 'BIC', 'INSTITUTION', 'SENDER', 'Sender Logical Terminal BIC'),
('MT103', 'ReceiverBIC', 'Block2', 'BIC', 'INSTITUTION', 'RECEIVER', 'Receiver BIC'),
('MT103', 'Field51A', ':51A:', 'BIC', 'INSTITUTION', 'SENDING_INSTITUTION', 'Sending Institution BIC'),
('MT103', 'Field52A', ':52A:', 'BIC', 'INSTITUTION', 'ORDERING_INSTITUTION', 'Ordering Institution BIC'),
('MT103', 'Field53A', ':53A:', 'BIC', 'INSTITUTION', 'SENDERS_CORRESPONDENT', 'Senders Correspondent BIC'),
('MT103', 'Field54A', ':54A:', 'BIC', 'INSTITUTION', 'RECEIVERS_CORRESPONDENT', 'Receivers Correspondent BIC'),
('MT103', 'Field55A', ':55A:', 'BIC', 'INSTITUTION', 'THIRD_REIMBURSEMENT', 'Third Reimbursement Institution BIC'),
('MT103', 'Field56A', ':56A:', 'BIC', 'INSTITUTION', 'INTERMEDIARY', 'Intermediary Institution BIC'),
('MT103', 'Field57A', ':57A:', 'BIC', 'INSTITUTION', 'ACCOUNT_WITH_INSTITUTION', 'Account With Institution BIC')

ON CONFLICT (message_format, source_field_name, entity_role) DO NOTHING;

-- Insert mappings for FEDWIRE
INSERT INTO gold.ref_identifier_source_mapping (message_format, source_field_name, source_field_path, identifier_type_code, identifier_category, entity_role, notes) VALUES
-- FEDWIRE Transaction Identifiers
('FEDWIRE', 'IMAD', '{1520}', 'IMAD', 'TRANSACTION', NULL, 'Input Message Accountability Data'),
('FEDWIRE', 'OMAD', '{7059}', 'OMAD', 'TRANSACTION', NULL, 'Output Message Accountability Data'),
('FEDWIRE', 'SenderReference', '{1500}', 'SENDER_REF', 'TRANSACTION', NULL, 'Sender Reference (16 chars)'),
('FEDWIRE', 'ReceiverReference', '{1510}', 'RELATED_REF', 'TRANSACTION', NULL, 'Receiver Reference'),
('FEDWIRE', 'PreviousIMAD', '{6000}', 'ORIGINAL_MSG_ID', 'TRANSACTION', NULL, 'Previous Message IMAD'),
-- FEDWIRE Party Identifiers
('FEDWIRE', 'Originator', '{4000}', 'CUSTOMER_ID', 'PARTY', 'DEBTOR', 'Originator (4x35)'),
('FEDWIRE', 'Beneficiary', '{4200}', 'CUSTOMER_ID', 'PARTY', 'CREDITOR', 'Beneficiary (4x35)'),
-- FEDWIRE Account Identifiers
('FEDWIRE', 'BeneficiaryReference', '{4400}', 'ACCOUNT_NUM', 'ACCOUNT', 'CREDITOR', 'Beneficiary Account Number'),
('FEDWIRE', 'DrawdownDebitAccount', '{4500}', 'ACCOUNT_NUM', 'ACCOUNT', 'DEBTOR', 'Drawdown Debit Account'),
-- FEDWIRE Institution Identifiers
('FEDWIRE', 'SenderABA', '{2100}', 'ABA_RTN', 'INSTITUTION', 'SENDER', 'Sender ABA Routing Number'),
('FEDWIRE', 'ReceiverABA', '{1600}', 'ABA_RTN', 'INSTITUTION', 'RECEIVER', 'Receiver ABA Routing Number'),
('FEDWIRE', 'SenderFI', '{3320}', 'ABA_RTN', 'INSTITUTION', 'SENDER', 'Sender FI Routing + Name'),
('FEDWIRE', 'ReceiverFI', '{3400}', 'ABA_RTN', 'INSTITUTION', 'RECEIVER', 'Receiver FI Routing + Name'),
('FEDWIRE', 'OriginatorFI', '{4100}', 'ABA_RTN', 'INSTITUTION', 'DEBTOR_AGENT', 'Originator FI Routing'),
('FEDWIRE', 'BeneficiaryFI', '{4300}', 'ABA_RTN', 'INSTITUTION', 'CREDITOR_AGENT', 'Beneficiary FI Routing'),
('FEDWIRE', 'InstructingFI', '{6400}', 'ABA_RTN', 'INSTITUTION', 'INSTRUCTING_AGENT', 'Instructing FI'),
('FEDWIRE', 'IntermediaryFI', '{6500}', 'ABA_RTN', 'INSTITUTION', 'INTERMEDIARY', 'Intermediary FI')

ON CONFLICT (message_format, source_field_name, entity_role) DO NOTHING;

-- Insert mappings for pacs.008
INSERT INTO gold.ref_identifier_source_mapping (message_format, source_field_name, source_field_path, identifier_type_code, identifier_category, entity_role, notes) VALUES
-- pacs.008 Transaction Identifiers
('pacs.008', 'MsgId', 'GrpHdr/MsgId', 'MESSAGE_ID', 'TRANSACTION', NULL, 'Message Identification'),
('pacs.008', 'InstrId', 'CdtTrfTxInf/PmtId/InstrId', 'INSTRUCTION_ID', 'TRANSACTION', NULL, 'Instruction Identification'),
('pacs.008', 'EndToEndId', 'CdtTrfTxInf/PmtId/EndToEndId', 'END_TO_END_ID', 'TRANSACTION', NULL, 'End-to-End Identification'),
('pacs.008', 'TxId', 'CdtTrfTxInf/PmtId/TxId', 'TRANSACTION_ID', 'TRANSACTION', NULL, 'Transaction Identification'),
('pacs.008', 'UETR', 'CdtTrfTxInf/PmtId/UETR', 'UETR', 'TRANSACTION', NULL, 'SWIFT gpi UETR'),
('pacs.008', 'ClrSysRef', 'CdtTrfTxInf/PmtId/ClrSysRef', 'CLEARING_SYS_REF', 'TRANSACTION', NULL, 'Clearing System Reference'),
-- pacs.008 Party Identifiers
('pacs.008', 'Dbtr/LEI', 'CdtTrfTxInf/Dbtr/Id/OrgId/LEI', 'LEI', 'PARTY', 'DEBTOR', 'Debtor LEI'),
('pacs.008', 'Dbtr/BIC', 'CdtTrfTxInf/Dbtr/Id/OrgId/AnyBIC', 'BIC_PARTY', 'PARTY', 'DEBTOR', 'Debtor BIC'),
('pacs.008', 'UltmtDbtr/LEI', 'CdtTrfTxInf/UltmtDbtr/Id/OrgId/LEI', 'LEI', 'PARTY', 'ULTIMATE_DEBTOR', 'Ultimate Debtor LEI'),
('pacs.008', 'Cdtr/LEI', 'CdtTrfTxInf/Cdtr/Id/OrgId/LEI', 'LEI', 'PARTY', 'CREDITOR', 'Creditor LEI'),
('pacs.008', 'Cdtr/BIC', 'CdtTrfTxInf/Cdtr/Id/OrgId/AnyBIC', 'BIC_PARTY', 'PARTY', 'CREDITOR', 'Creditor BIC'),
('pacs.008', 'UltmtCdtr/LEI', 'CdtTrfTxInf/UltmtCdtr/Id/OrgId/LEI', 'LEI', 'PARTY', 'ULTIMATE_CREDITOR', 'Ultimate Creditor LEI'),
-- pacs.008 Account Identifiers
('pacs.008', 'DbtrAcct/IBAN', 'CdtTrfTxInf/DbtrAcct/Id/IBAN', 'IBAN', 'ACCOUNT', 'DEBTOR', 'Debtor Account IBAN'),
('pacs.008', 'DbtrAcct/Othr', 'CdtTrfTxInf/DbtrAcct/Id/Othr/Id', 'ACCOUNT_NUM', 'ACCOUNT', 'DEBTOR', 'Debtor Account Other'),
('pacs.008', 'CdtrAcct/IBAN', 'CdtTrfTxInf/CdtrAcct/Id/IBAN', 'IBAN', 'ACCOUNT', 'CREDITOR', 'Creditor Account IBAN'),
('pacs.008', 'CdtrAcct/Othr', 'CdtTrfTxInf/CdtrAcct/Id/Othr/Id', 'ACCOUNT_NUM', 'ACCOUNT', 'CREDITOR', 'Creditor Account Other'),
-- pacs.008 Institution Identifiers
('pacs.008', 'InstgAgt/BIC', 'GrpHdr/InstgAgt/FinInstnId/BICFI', 'BIC', 'INSTITUTION', 'INSTRUCTING_AGENT', 'Instructing Agent BIC'),
('pacs.008', 'InstdAgt/BIC', 'GrpHdr/InstdAgt/FinInstnId/BICFI', 'BIC', 'INSTITUTION', 'INSTRUCTED_AGENT', 'Instructed Agent BIC'),
('pacs.008', 'DbtrAgt/BIC', 'CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI', 'BIC', 'INSTITUTION', 'DEBTOR_AGENT', 'Debtor Agent BIC'),
('pacs.008', 'DbtrAgt/ClrSysMmbId', 'CdtTrfTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'CLEARING_MEMBER_ID', 'INSTITUTION', 'DEBTOR_AGENT', 'Debtor Agent Clearing Member'),
('pacs.008', 'CdtrAgt/BIC', 'CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI', 'BIC', 'INSTITUTION', 'CREDITOR_AGENT', 'Creditor Agent BIC'),
('pacs.008', 'CdtrAgt/ClrSysMmbId', 'CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'CLEARING_MEMBER_ID', 'INSTITUTION', 'CREDITOR_AGENT', 'Creditor Agent Clearing Member'),
('pacs.008', 'IntrmyAgt1/BIC', 'CdtTrfTxInf/IntrmyAgt1/FinInstnId/BICFI', 'BIC', 'INSTITUTION', 'INTERMEDIARY_1', 'Intermediary Agent 1 BIC'),
('pacs.008', 'IntrmyAgt2/BIC', 'CdtTrfTxInf/IntrmyAgt2/FinInstnId/BICFI', 'BIC', 'INSTITUTION', 'INTERMEDIARY_2', 'Intermediary Agent 2 BIC'),
('pacs.008', 'IntrmyAgt3/BIC', 'CdtTrfTxInf/IntrmyAgt3/FinInstnId/BICFI', 'BIC', 'INSTITUTION', 'INTERMEDIARY_3', 'Intermediary Agent 3 BIC'),
-- pacs.008 Document Identifiers
('pacs.008', 'CdtrRefInf/Ref', 'CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Ref', 'CREDITOR_REF', 'DOCUMENT', NULL, 'Creditor Reference'),
('pacs.008', 'RfrdDocInf/Nb', 'CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Nb', 'DOCUMENT_NUM', 'DOCUMENT', NULL, 'Referenced Document Number')

ON CONFLICT (message_format, source_field_name, entity_role) DO NOTHING;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ref_id_map_format ON gold.ref_identifier_source_mapping(message_format);
CREATE INDEX IF NOT EXISTS idx_ref_id_map_type ON gold.ref_identifier_source_mapping(identifier_type_code);
CREATE INDEX IF NOT EXISTS idx_ref_id_map_category ON gold.ref_identifier_source_mapping(identifier_category);

-- =====================================================
-- CDM_TRANSACTION_IDENTIFIER (Normalized)
-- =====================================================
-- All transaction/message identifiers in normalized form

CREATE TABLE IF NOT EXISTS gold.cdm_transaction_identifier (
    txn_identifier_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Link to parent payment instruction
    payment_instruction_id VARCHAR(36) NOT NULL,

    -- Identifier details
    identifier_type VARCHAR(30) NOT NULL,      -- References ref_identifier_type
    identifier_value VARCHAR(50) NOT NULL,

    -- Source tracking
    source_message_format VARCHAR(50) NOT NULL,  -- pain.001, MT103, FEDWIRE, pacs.008
    source_field_name VARCHAR(100),              -- Original field name
    source_stg_id VARCHAR(36),                   -- FK to silver staging record

    -- Flags
    is_primary BOOLEAN DEFAULT FALSE,            -- Primary identifier for this payment
    is_globally_unique BOOLEAN DEFAULT FALSE,    -- UETR, IMAD are globally unique

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_txn_id_type FOREIGN KEY (identifier_type) REFERENCES gold.ref_identifier_type(identifier_type_code)
);

-- Indexes for transaction identifiers
CREATE INDEX IF NOT EXISTS idx_cdm_txn_id_payment ON gold.cdm_transaction_identifier(payment_instruction_id);
CREATE INDEX IF NOT EXISTS idx_cdm_txn_id_type ON gold.cdm_transaction_identifier(identifier_type);
CREATE INDEX IF NOT EXISTS idx_cdm_txn_id_value ON gold.cdm_transaction_identifier(identifier_value);
CREATE INDEX IF NOT EXISTS idx_cdm_txn_id_uetr ON gold.cdm_transaction_identifier(identifier_value) WHERE identifier_type = 'UETR';
CREATE INDEX IF NOT EXISTS idx_cdm_txn_id_e2e ON gold.cdm_transaction_identifier(identifier_value) WHERE identifier_type = 'END_TO_END_ID';
CREATE INDEX IF NOT EXISTS idx_cdm_txn_id_imad ON gold.cdm_transaction_identifier(identifier_value) WHERE identifier_type = 'IMAD';
CREATE UNIQUE INDEX IF NOT EXISTS idx_cdm_txn_id_unique ON gold.cdm_transaction_identifier(payment_instruction_id, identifier_type, source_message_format);

-- =====================================================
-- CDM_PARTY_IDENTIFIER (Normalized)
-- =====================================================
-- All party identifiers (LEI, Tax ID, National ID, etc.)

CREATE TABLE IF NOT EXISTS gold.cdm_party_identifier (
    party_identifier_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Link to parent party
    party_id VARCHAR(36) NOT NULL,

    -- Identifier details
    identifier_type VARCHAR(30) NOT NULL,      -- LEI, TAX_ID, CPF, CNPJ, NATIONAL_ID, etc.
    identifier_value VARCHAR(77) NOT NULL,     -- 77 for PIX keys

    -- Additional context
    issuing_country VARCHAR(3),                -- ISO 3166 country code
    issuer_name VARCHAR(100),                  -- Issuing authority
    issue_date DATE,
    expiry_date DATE,

    -- Source tracking
    source_message_format VARCHAR(50) NOT NULL,
    source_field_name VARCHAR(100),
    source_stg_id VARCHAR(36),
    source_instruction_id VARCHAR(36),          -- References payment instruction that created this identifier
    entity_role VARCHAR(50),                    -- DEBTOR, CREDITOR, INITIATING_PARTY, etc.

    -- Flags
    is_primary BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_from DATE DEFAULT CURRENT_DATE,
    valid_to DATE,

    CONSTRAINT fk_party_id_type FOREIGN KEY (identifier_type) REFERENCES gold.ref_identifier_type(identifier_type_code)
);

-- Indexes for party identifiers
CREATE INDEX IF NOT EXISTS idx_cdm_party_id_party ON gold.cdm_party_identifier(party_id);
CREATE INDEX IF NOT EXISTS idx_cdm_party_id_type ON gold.cdm_party_identifier(identifier_type);
CREATE INDEX IF NOT EXISTS idx_cdm_party_id_value ON gold.cdm_party_identifier(identifier_value);
CREATE INDEX IF NOT EXISTS idx_cdm_party_id_lei ON gold.cdm_party_identifier(identifier_value) WHERE identifier_type = 'LEI';
CREATE INDEX IF NOT EXISTS idx_cdm_party_id_tax ON gold.cdm_party_identifier(identifier_value) WHERE identifier_type IN ('TAX_ID', 'TIN_US', 'CPF', 'CNPJ');
CREATE INDEX IF NOT EXISTS idx_cdm_party_id_role ON gold.cdm_party_identifier(entity_role);
CREATE INDEX IF NOT EXISTS idx_cdm_party_id_src_instr ON gold.cdm_party_identifier(source_instruction_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_cdm_party_id_unique ON gold.cdm_party_identifier(party_id, identifier_type, identifier_value);

-- =====================================================
-- CDM_ACCOUNT_IDENTIFIER (Normalized)
-- =====================================================
-- All account identifiers (IBAN, BBAN, Account Numbers, etc.)

CREATE TABLE IF NOT EXISTS gold.cdm_account_identifier (
    account_identifier_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Link to parent account
    account_id VARCHAR(36) NOT NULL,

    -- Identifier details
    identifier_type VARCHAR(30) NOT NULL,      -- IBAN, BBAN, ACCOUNT_NUM, DFI_ACCOUNT, etc.
    identifier_value VARCHAR(50) NOT NULL,

    -- Account context
    account_currency VARCHAR(3),               -- ISO 4217
    account_type VARCHAR(10),                  -- CACC, SVGS, etc.

    -- Source tracking
    source_message_format VARCHAR(50) NOT NULL,
    source_field_name VARCHAR(100),
    source_stg_id VARCHAR(36),
    source_instruction_id VARCHAR(36),         -- References payment instruction that created this identifier
    entity_role VARCHAR(50),                   -- DEBTOR, CREDITOR, INTERMEDIARY, etc.

    -- Flags
    is_primary BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_from DATE DEFAULT CURRENT_DATE,
    valid_to DATE,

    CONSTRAINT fk_acct_id_type FOREIGN KEY (identifier_type) REFERENCES gold.ref_identifier_type(identifier_type_code)
);

-- Indexes for account identifiers
CREATE INDEX IF NOT EXISTS idx_cdm_acct_id_account ON gold.cdm_account_identifier(account_id);
CREATE INDEX IF NOT EXISTS idx_cdm_acct_id_type ON gold.cdm_account_identifier(identifier_type);
CREATE INDEX IF NOT EXISTS idx_cdm_acct_id_value ON gold.cdm_account_identifier(identifier_value);
CREATE INDEX IF NOT EXISTS idx_cdm_acct_id_iban ON gold.cdm_account_identifier(identifier_value) WHERE identifier_type = 'IBAN';
CREATE INDEX IF NOT EXISTS idx_cdm_acct_id_role ON gold.cdm_account_identifier(entity_role);
CREATE INDEX IF NOT EXISTS idx_cdm_acct_id_src_instr ON gold.cdm_account_identifier(source_instruction_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_cdm_acct_id_unique ON gold.cdm_account_identifier(account_id, identifier_type, identifier_value);

-- =====================================================
-- CDM_INSTITUTION_IDENTIFIER (Normalized)
-- =====================================================
-- All financial institution identifiers (BIC, ABA, Sort Code, etc.)

CREATE TABLE IF NOT EXISTS gold.cdm_institution_identifier (
    institution_identifier_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Link to parent financial institution
    financial_institution_id VARCHAR(36) NOT NULL,

    -- Identifier details
    identifier_type VARCHAR(30) NOT NULL,      -- BIC, ABA_RTN, SORT_CODE, IFSC, CNAPS, ISPB, etc.
    identifier_value VARCHAR(35) NOT NULL,

    -- Institution context
    institution_country VARCHAR(3),            -- ISO 3166
    clearing_system VARCHAR(30),               -- TARGET2, CHIPS, FEDWIRE, BACS, etc.

    -- Source tracking
    source_message_format VARCHAR(50) NOT NULL,
    source_field_name VARCHAR(100),
    source_stg_id VARCHAR(36),
    source_instruction_id VARCHAR(36),         -- References payment instruction that created this identifier
    entity_role VARCHAR(50),                   -- DEBTOR_AGENT, CREDITOR_AGENT, INTERMEDIARY_1, etc.

    -- Flags
    is_primary BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_from DATE DEFAULT CURRENT_DATE,
    valid_to DATE,

    CONSTRAINT fk_inst_id_type FOREIGN KEY (identifier_type) REFERENCES gold.ref_identifier_type(identifier_type_code)
);

-- Indexes for institution identifiers
CREATE INDEX IF NOT EXISTS idx_cdm_inst_id_fi ON gold.cdm_institution_identifier(financial_institution_id);
CREATE INDEX IF NOT EXISTS idx_cdm_inst_id_type ON gold.cdm_institution_identifier(identifier_type);
CREATE INDEX IF NOT EXISTS idx_cdm_inst_id_value ON gold.cdm_institution_identifier(identifier_value);
CREATE INDEX IF NOT EXISTS idx_cdm_inst_id_bic ON gold.cdm_institution_identifier(identifier_value) WHERE identifier_type = 'BIC';
CREATE INDEX IF NOT EXISTS idx_cdm_inst_id_aba ON gold.cdm_institution_identifier(identifier_value) WHERE identifier_type = 'ABA_RTN';
CREATE INDEX IF NOT EXISTS idx_cdm_inst_id_role ON gold.cdm_institution_identifier(entity_role);
CREATE INDEX IF NOT EXISTS idx_cdm_inst_id_clearing ON gold.cdm_institution_identifier(clearing_system);
CREATE INDEX IF NOT EXISTS idx_cdm_inst_id_src_instr ON gold.cdm_institution_identifier(source_instruction_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_cdm_inst_id_unique ON gold.cdm_institution_identifier(financial_institution_id, identifier_type, identifier_value);

-- =====================================================
-- CDM_DOCUMENT_IDENTIFIER (Normalized)
-- =====================================================
-- All document/remittance identifiers (Invoice, PO, Creditor Ref, etc.)

CREATE TABLE IF NOT EXISTS gold.cdm_document_identifier (
    document_identifier_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Link to parent payment instruction
    payment_instruction_id VARCHAR(36) NOT NULL,

    -- Identifier details
    identifier_type VARCHAR(30) NOT NULL,      -- INVOICE_NUM, PURCHASE_ORDER, CREDITOR_REF, etc.
    identifier_value VARCHAR(140) NOT NULL,    -- Up to 140 for tax references

    -- Document context
    document_type_code VARCHAR(10),            -- MSIN, CINV, DNFA, etc.
    document_date DATE,
    document_amount DECIMAL(18,4),
    document_currency VARCHAR(3),

    -- Source tracking
    source_message_format VARCHAR(50) NOT NULL,
    source_field_name VARCHAR(100),
    source_stg_id VARCHAR(36),

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_doc_id_type FOREIGN KEY (identifier_type) REFERENCES gold.ref_identifier_type(identifier_type_code)
);

-- Indexes for document identifiers
CREATE INDEX IF NOT EXISTS idx_cdm_doc_id_payment ON gold.cdm_document_identifier(payment_instruction_id);
CREATE INDEX IF NOT EXISTS idx_cdm_doc_id_type ON gold.cdm_document_identifier(identifier_type);
CREATE INDEX IF NOT EXISTS idx_cdm_doc_id_value ON gold.cdm_document_identifier(identifier_value);
CREATE INDEX IF NOT EXISTS idx_cdm_doc_id_invoice ON gold.cdm_document_identifier(identifier_value) WHERE identifier_type = 'INVOICE_NUM';
CREATE INDEX IF NOT EXISTS idx_cdm_doc_id_creditor_ref ON gold.cdm_document_identifier(identifier_value) WHERE identifier_type = 'CREDITOR_REF';

-- =====================================================
-- Views for common identifier lookups
-- =====================================================

-- View: All identifiers for a payment (flattened)
CREATE OR REPLACE VIEW gold.vw_payment_all_identifiers AS
SELECT
    pi.instruction_id AS payment_instruction_id,
    pi.source_message_type,
    'TRANSACTION' AS identifier_category,
    ti.identifier_type,
    ti.identifier_value,
    ti.is_primary,
    ti.source_field_name
FROM gold.cdm_payment_instruction pi
JOIN gold.cdm_transaction_identifier ti ON pi.instruction_id = ti.payment_instruction_id

UNION ALL

SELECT
    pi.instruction_id AS payment_instruction_id,
    pi.source_message_type,
    'PARTY' AS identifier_category,
    pai.identifier_type,
    pai.identifier_value,
    pai.is_primary,
    pai.source_field_name
FROM gold.cdm_payment_instruction pi
JOIN gold.cdm_party p ON p.party_id IN (pi.debtor_id, pi.creditor_id, pi.ultimate_debtor_id, pi.ultimate_creditor_id)
JOIN gold.cdm_party_identifier pai ON p.party_id = pai.party_id

UNION ALL

SELECT
    pi.instruction_id AS payment_instruction_id,
    pi.source_message_type,
    'ACCOUNT' AS identifier_category,
    ai.identifier_type,
    ai.identifier_value,
    ai.is_primary,
    ai.source_field_name
FROM gold.cdm_payment_instruction pi
JOIN gold.cdm_account a ON a.account_id IN (pi.debtor_account_id, pi.creditor_account_id)
JOIN gold.cdm_account_identifier ai ON a.account_id = ai.account_id

UNION ALL

SELECT
    pi.instruction_id AS payment_instruction_id,
    pi.source_message_type,
    'INSTITUTION' AS identifier_category,
    ii.identifier_type,
    ii.identifier_value,
    ii.is_primary,
    ii.source_field_name
FROM gold.cdm_payment_instruction pi
JOIN gold.cdm_financial_institution fi ON fi.fi_id IN (pi.debtor_agent_id, pi.creditor_agent_id, pi.intermediary_agent1_id, pi.intermediary_agent2_id)
JOIN gold.cdm_institution_identifier ii ON fi.fi_id = ii.financial_institution_id

UNION ALL

SELECT
    pi.instruction_id AS payment_instruction_id,
    pi.source_message_type,
    'DOCUMENT' AS identifier_category,
    di.identifier_type,
    di.identifier_value,
    FALSE AS is_primary,
    di.source_field_name
FROM gold.cdm_payment_instruction pi
JOIN gold.cdm_document_identifier di ON pi.instruction_id = di.payment_instruction_id;

-- View: Lookup payment by any identifier
CREATE OR REPLACE VIEW gold.vw_identifier_payment_lookup AS
SELECT
    ti.identifier_type,
    ti.identifier_value,
    'TRANSACTION' AS identifier_category,
    pi.instruction_id,
    pi.payment_id,
    pi.source_message_type,
    pi.current_status,
    pi.instructed_amount,
    pi.instructed_currency,
    pi.created_at
FROM gold.cdm_transaction_identifier ti
JOIN gold.cdm_payment_instruction pi ON ti.payment_instruction_id = pi.instruction_id;

-- View: Identifier statistics by type and source
CREATE OR REPLACE VIEW gold.vw_identifier_statistics AS
SELECT
    'TRANSACTION' AS category,
    identifier_type,
    source_message_format,
    COUNT(*) AS identifier_count,
    COUNT(DISTINCT payment_instruction_id) AS payment_count
FROM gold.cdm_transaction_identifier
GROUP BY identifier_type, source_message_format

UNION ALL

SELECT
    'PARTY' AS category,
    identifier_type,
    source_message_format,
    COUNT(*) AS identifier_count,
    COUNT(DISTINCT party_id) AS entity_count
FROM gold.cdm_party_identifier
GROUP BY identifier_type, source_message_format

UNION ALL

SELECT
    'ACCOUNT' AS category,
    identifier_type,
    source_message_format,
    COUNT(*) AS identifier_count,
    COUNT(DISTINCT account_id) AS entity_count
FROM gold.cdm_account_identifier
GROUP BY identifier_type, source_message_format

UNION ALL

SELECT
    'INSTITUTION' AS category,
    identifier_type,
    source_message_format,
    COUNT(*) AS identifier_count,
    COUNT(DISTINCT financial_institution_id) AS entity_count
FROM gold.cdm_institution_identifier
GROUP BY identifier_type, source_message_format

UNION ALL

SELECT
    'DOCUMENT' AS category,
    identifier_type,
    source_message_format,
    COUNT(*) AS identifier_count,
    COUNT(DISTINCT payment_instruction_id) AS entity_count
FROM gold.cdm_document_identifier
GROUP BY identifier_type, source_message_format;

-- Verify tables
SELECT 'gold' as schema, table_name, 'TABLE' as type
FROM information_schema.tables
WHERE table_schema = 'gold'
AND table_name LIKE '%identifier%'
ORDER BY table_name;
