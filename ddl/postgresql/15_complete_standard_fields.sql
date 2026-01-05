-- =============================================================================
-- GPS CDM - Complete Standard Field Definitions
-- =============================================================================
-- This script populates standard_fields with the COMPLETE official field
-- definitions from each payment standard. This is the SOURCE OF TRUTH for
-- reconciliation and coverage tracking.
--
-- Key principle: source_path in silver_field_mappings MUST match field_path
-- in standard_fields for proper reconciliation.
-- =============================================================================

-- =============================================================================
-- First, clean up silver_field_mappings to remove inconsistent dot-notation paths
-- These should be replaced with proper source-native paths
-- =============================================================================

-- Delete old dot-notation paths that can't be reconciled
DELETE FROM mapping.silver_field_mappings
WHERE source_path LIKE '%.%'
  AND source_path NOT LIKE '%/%'  -- Keep proper path separators
  AND is_user_modified = FALSE;

-- =============================================================================
-- pain.001 - ISO 20022 Customer Credit Transfer Initiation
-- Complete field list from ISO 20022 pain.001.001.09 schema
-- =============================================================================
DELETE FROM mapping.standard_fields WHERE format_id = 'pain.001';

INSERT INTO mapping.standard_fields
    (format_id, field_name, field_path, field_description, data_type, max_length, is_mandatory, field_category)
VALUES
    -- ==================== GROUP HEADER ====================
    ('pain.001', 'MsgId', 'CstmrCdtTrfInitn/GrpHdr/MsgId', 'Point to point reference assigned by the instructing party', 'Max35Text', 35, TRUE, 'GroupHeader'),
    ('pain.001', 'CreDtTm', 'CstmrCdtTrfInitn/GrpHdr/CreDtTm', 'Date and time at which the message was created', 'ISODateTime', NULL, TRUE, 'GroupHeader'),
    ('pain.001', 'Authstn/Cd', 'CstmrCdtTrfInitn/GrpHdr/Authstn/Cd', 'Authorisation code', 'Authorisation1Code', 4, FALSE, 'GroupHeader'),
    ('pain.001', 'Authstn/Prtry', 'CstmrCdtTrfInitn/GrpHdr/Authstn/Prtry', 'Proprietary authorisation', 'Max128Text', 128, FALSE, 'GroupHeader'),
    ('pain.001', 'NbOfTxs', 'CstmrCdtTrfInitn/GrpHdr/NbOfTxs', 'Number of individual transactions', 'Max15NumericText', 15, TRUE, 'GroupHeader'),
    ('pain.001', 'CtrlSum', 'CstmrCdtTrfInitn/GrpHdr/CtrlSum', 'Total of all individual amounts', 'DecimalNumber', NULL, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/Nm', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Nm', 'Name of initiating party', 'Max140Text', 140, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/AdrTp/Cd', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/AdrTp/Cd', 'Address type code', 'AddressType2Code', 4, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/Dept', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/Dept', 'Department', 'Max70Text', 70, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/SubDept', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/SubDept', 'Sub-department', 'Max70Text', 70, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/StrtNm', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/StrtNm', 'Street name', 'Max70Text', 70, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/BldgNb', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/BldgNb', 'Building number', 'Max16Text', 16, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/BldgNm', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/BldgNm', 'Building name', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/Flr', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/Flr', 'Floor', 'Max70Text', 70, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/PstBx', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/PstBx', 'Post box', 'Max16Text', 16, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/Room', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/Room', 'Room', 'Max70Text', 70, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/PstCd', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/PstCd', 'Postal code', 'Max16Text', 16, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/TwnNm', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/TwnNm', 'Town name', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/TwnLctnNm', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/TwnLctnNm', 'Town location name', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/DstrctNm', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/DstrctNm', 'District name', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/CtrySubDvsn', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/CtrySubDvsn', 'Country subdivision', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/Ctry', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/Ctry', 'Country', 'CountryCode', 2, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/PstlAdr/AdrLine', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/PstlAdr/AdrLine', 'Address line', 'Max70Text', 70, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/Id/OrgId/AnyBIC', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id/OrgId/AnyBIC', 'Any BIC', 'AnyBICDec2014Identifier', 11, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/Id/OrgId/LEI', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id/OrgId/LEI', 'Legal Entity Identifier', 'LEIIdentifier', 20, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/Id/OrgId/Othr/Id', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id/OrgId/Othr/Id', 'Other organisation ID', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/Id/OrgId/Othr/SchmeNm/Cd', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id/OrgId/Othr/SchmeNm/Cd', 'Scheme name code', 'ExternalOrganisationIdentification1Code', 4, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/Id/OrgId/Othr/SchmeNm/Prtry', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id/OrgId/Othr/SchmeNm/Prtry', 'Scheme name proprietary', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/Id/OrgId/Othr/Issr', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id/OrgId/Othr/Issr', 'Issuer', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/Id/PrvtId/DtAndPlcOfBirth/BirthDt', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id/PrvtId/DtAndPlcOfBirth/BirthDt', 'Birth date', 'ISODate', NULL, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/Id/PrvtId/DtAndPlcOfBirth/PrvcOfBirth', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id/PrvtId/DtAndPlcOfBirth/PrvcOfBirth', 'Province of birth', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/Id/PrvtId/DtAndPlcOfBirth/CityOfBirth', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id/PrvtId/DtAndPlcOfBirth/CityOfBirth', 'City of birth', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/Id/PrvtId/DtAndPlcOfBirth/CtryOfBirth', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id/PrvtId/DtAndPlcOfBirth/CtryOfBirth', 'Country of birth', 'CountryCode', 2, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/Id/PrvtId/Othr/Id', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id/PrvtId/Othr/Id', 'Other private ID', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/Id/PrvtId/Othr/SchmeNm/Cd', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id/PrvtId/Othr/SchmeNm/Cd', 'Private ID scheme code', 'ExternalPersonIdentification1Code', 4, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/Id/PrvtId/Othr/SchmeNm/Prtry', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id/PrvtId/Othr/SchmeNm/Prtry', 'Private ID scheme proprietary', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/Id/PrvtId/Othr/Issr', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id/PrvtId/Othr/Issr', 'Private ID issuer', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/CtryOfRes', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/CtryOfRes', 'Country of residence', 'CountryCode', 2, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/CtctDtls/NmPrfx', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/CtctDtls/NmPrfx', 'Name prefix', 'NamePrefix2Code', 4, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/CtctDtls/Nm', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/CtctDtls/Nm', 'Contact name', 'Max140Text', 140, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/CtctDtls/PhneNb', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/CtctDtls/PhneNb', 'Phone number', 'PhoneNumber', 30, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/CtctDtls/MobNb', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/CtctDtls/MobNb', 'Mobile number', 'PhoneNumber', 30, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/CtctDtls/FaxNb', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/CtctDtls/FaxNb', 'Fax number', 'PhoneNumber', 30, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/CtctDtls/EmailAdr', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/CtctDtls/EmailAdr', 'Email address', 'Max2048Text', 2048, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/CtctDtls/EmailPurp', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/CtctDtls/EmailPurp', 'Email purpose', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/CtctDtls/JobTitl', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/CtctDtls/JobTitl', 'Job title', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/CtctDtls/Rspnsblty', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/CtctDtls/Rspnsblty', 'Responsibility', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/CtctDtls/Dept', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/CtctDtls/Dept', 'Contact department', 'Max70Text', 70, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/CtctDtls/Othr/ChanlTp', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/CtctDtls/Othr/ChanlTp', 'Other channel type', 'Max4Text', 4, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/CtctDtls/Othr/Id', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/CtctDtls/Othr/Id', 'Other contact ID', 'Max128Text', 128, FALSE, 'GroupHeader'),
    ('pain.001', 'InitgPty/CtctDtls/PrefrdMtd', 'CstmrCdtTrfInitn/GrpHdr/InitgPty/CtctDtls/PrefrdMtd', 'Preferred contact method', 'PreferredContactMethod1Code', 4, FALSE, 'GroupHeader'),
    ('pain.001', 'FwdgAgt/FinInstnId/BICFI', 'CstmrCdtTrfInitn/GrpHdr/FwdgAgt/FinInstnId/BICFI', 'Forwarding agent BIC', 'BICFIDec2014Identifier', 11, FALSE, 'GroupHeader'),
    ('pain.001', 'FwdgAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd', 'CstmrCdtTrfInitn/GrpHdr/FwdgAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd', 'Forwarding agent clearing system code', 'ExternalClearingSystemIdentification1Code', 5, FALSE, 'GroupHeader'),
    ('pain.001', 'FwdgAgt/FinInstnId/ClrSysMmbId/MmbId', 'CstmrCdtTrfInitn/GrpHdr/FwdgAgt/FinInstnId/ClrSysMmbId/MmbId', 'Forwarding agent member ID', 'Max35Text', 35, FALSE, 'GroupHeader'),
    ('pain.001', 'FwdgAgt/FinInstnId/LEI', 'CstmrCdtTrfInitn/GrpHdr/FwdgAgt/FinInstnId/LEI', 'Forwarding agent LEI', 'LEIIdentifier', 20, FALSE, 'GroupHeader'),
    ('pain.001', 'FwdgAgt/FinInstnId/Nm', 'CstmrCdtTrfInitn/GrpHdr/FwdgAgt/FinInstnId/Nm', 'Forwarding agent name', 'Max140Text', 140, FALSE, 'GroupHeader'),
    ('pain.001', 'FwdgAgt/FinInstnId/PstlAdr/Ctry', 'CstmrCdtTrfInitn/GrpHdr/FwdgAgt/FinInstnId/PstlAdr/Ctry', 'Forwarding agent country', 'CountryCode', 2, FALSE, 'GroupHeader'),

    -- ==================== PAYMENT INFORMATION ====================
    ('pain.001', 'PmtInf/PmtInfId', 'CstmrCdtTrfInitn/PmtInf/PmtInfId', 'Unique identification of payment information block', 'Max35Text', 35, TRUE, 'PaymentInformation'),
    ('pain.001', 'PmtInf/PmtMtd', 'CstmrCdtTrfInitn/PmtInf/PmtMtd', 'Payment method (TRF, CHK, TRA)', 'PaymentMethod3Code', 3, TRUE, 'PaymentInformation'),
    ('pain.001', 'PmtInf/BtchBookg', 'CstmrCdtTrfInitn/PmtInf/BtchBookg', 'Batch booking indicator', 'BatchBookingIndicator', NULL, FALSE, 'PaymentInformation'),
    ('pain.001', 'PmtInf/NbOfTxs', 'CstmrCdtTrfInitn/PmtInf/NbOfTxs', 'Number of transactions in payment info block', 'Max15NumericText', 15, FALSE, 'PaymentInformation'),
    ('pain.001', 'PmtInf/CtrlSum', 'CstmrCdtTrfInitn/PmtInf/CtrlSum', 'Control sum for payment info block', 'DecimalNumber', NULL, FALSE, 'PaymentInformation'),
    ('pain.001', 'PmtInf/PmtTpInf/InstrPrty', 'CstmrCdtTrfInitn/PmtInf/PmtTpInf/InstrPrty', 'Instruction priority (HIGH, NORM)', 'Priority2Code', 4, FALSE, 'PaymentInformation'),
    ('pain.001', 'PmtInf/PmtTpInf/SvcLvl/Cd', 'CstmrCdtTrfInitn/PmtInf/PmtTpInf/SvcLvl/Cd', 'Service level code (SEPA, URGP)', 'ExternalServiceLevel1Code', 4, FALSE, 'PaymentInformation'),
    ('pain.001', 'PmtInf/PmtTpInf/SvcLvl/Prtry', 'CstmrCdtTrfInitn/PmtInf/PmtTpInf/SvcLvl/Prtry', 'Service level proprietary', 'Max35Text', 35, FALSE, 'PaymentInformation'),
    ('pain.001', 'PmtInf/PmtTpInf/LclInstrm/Cd', 'CstmrCdtTrfInitn/PmtInf/PmtTpInf/LclInstrm/Cd', 'Local instrument code', 'ExternalLocalInstrument1Code', 35, FALSE, 'PaymentInformation'),
    ('pain.001', 'PmtInf/PmtTpInf/LclInstrm/Prtry', 'CstmrCdtTrfInitn/PmtInf/PmtTpInf/LclInstrm/Prtry', 'Local instrument proprietary', 'Max35Text', 35, FALSE, 'PaymentInformation'),
    ('pain.001', 'PmtInf/PmtTpInf/CtgyPurp/Cd', 'CstmrCdtTrfInitn/PmtInf/PmtTpInf/CtgyPurp/Cd', 'Category purpose code', 'ExternalCategoryPurpose1Code', 4, FALSE, 'PaymentInformation'),
    ('pain.001', 'PmtInf/PmtTpInf/CtgyPurp/Prtry', 'CstmrCdtTrfInitn/PmtInf/PmtTpInf/CtgyPurp/Prtry', 'Category purpose proprietary', 'Max35Text', 35, FALSE, 'PaymentInformation'),
    ('pain.001', 'PmtInf/ReqdExctnDt/Dt', 'CstmrCdtTrfInitn/PmtInf/ReqdExctnDt/Dt', 'Requested execution date', 'ISODate', NULL, FALSE, 'PaymentInformation'),
    ('pain.001', 'PmtInf/ReqdExctnDt/DtTm', 'CstmrCdtTrfInitn/PmtInf/ReqdExctnDt/DtTm', 'Requested execution date time', 'ISODateTime', NULL, FALSE, 'PaymentInformation'),
    ('pain.001', 'PmtInf/PoolgAdjstmntDt', 'CstmrCdtTrfInitn/PmtInf/PoolgAdjstmntDt', 'Pooling adjustment date', 'ISODate', NULL, FALSE, 'PaymentInformation'),

    -- ==================== DEBTOR (Payer) ====================
    ('pain.001', 'PmtInf/Dbtr/Nm', 'CstmrCdtTrfInitn/PmtInf/Dbtr/Nm', 'Debtor name', 'Max140Text', 140, TRUE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/AdrTp/Cd', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/AdrTp/Cd', 'Debtor address type', 'AddressType2Code', 4, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/Dept', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/Dept', 'Debtor department', 'Max70Text', 70, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/SubDept', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/SubDept', 'Debtor sub-department', 'Max70Text', 70, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/StrtNm', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/StrtNm', 'Debtor street name', 'Max70Text', 70, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/BldgNb', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/BldgNb', 'Debtor building number', 'Max16Text', 16, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/BldgNm', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/BldgNm', 'Debtor building name', 'Max35Text', 35, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/Flr', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/Flr', 'Debtor floor', 'Max70Text', 70, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/PstBx', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/PstBx', 'Debtor post box', 'Max16Text', 16, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/Room', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/Room', 'Debtor room', 'Max70Text', 70, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/PstCd', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/PstCd', 'Debtor postal code', 'Max16Text', 16, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/TwnNm', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/TwnNm', 'Debtor town name', 'Max35Text', 35, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/TwnLctnNm', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/TwnLctnNm', 'Debtor town location name', 'Max35Text', 35, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/DstrctNm', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/DstrctNm', 'Debtor district name', 'Max35Text', 35, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/CtrySubDvsn', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/CtrySubDvsn', 'Debtor country subdivision', 'Max35Text', 35, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/Ctry', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/Ctry', 'Debtor country', 'CountryCode', 2, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/PstlAdr/AdrLine', 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/AdrLine', 'Debtor address line', 'Max70Text', 70, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/Id/OrgId/AnyBIC', 'CstmrCdtTrfInitn/PmtInf/Dbtr/Id/OrgId/AnyBIC', 'Debtor BIC', 'AnyBICDec2014Identifier', 11, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/Id/OrgId/LEI', 'CstmrCdtTrfInitn/PmtInf/Dbtr/Id/OrgId/LEI', 'Debtor LEI', 'LEIIdentifier', 20, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/Id/OrgId/Othr/Id', 'CstmrCdtTrfInitn/PmtInf/Dbtr/Id/OrgId/Othr/Id', 'Debtor organisation ID', 'Max35Text', 35, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/Id/OrgId/Othr/SchmeNm/Cd', 'CstmrCdtTrfInitn/PmtInf/Dbtr/Id/OrgId/Othr/SchmeNm/Cd', 'Debtor org ID scheme code', 'ExternalOrganisationIdentification1Code', 4, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/Id/OrgId/Othr/Issr', 'CstmrCdtTrfInitn/PmtInf/Dbtr/Id/OrgId/Othr/Issr', 'Debtor org ID issuer', 'Max35Text', 35, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/Id/PrvtId/DtAndPlcOfBirth/BirthDt', 'CstmrCdtTrfInitn/PmtInf/Dbtr/Id/PrvtId/DtAndPlcOfBirth/BirthDt', 'Debtor birth date', 'ISODate', NULL, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/Id/PrvtId/DtAndPlcOfBirth/CityOfBirth', 'CstmrCdtTrfInitn/PmtInf/Dbtr/Id/PrvtId/DtAndPlcOfBirth/CityOfBirth', 'Debtor city of birth', 'Max35Text', 35, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/Id/PrvtId/DtAndPlcOfBirth/CtryOfBirth', 'CstmrCdtTrfInitn/PmtInf/Dbtr/Id/PrvtId/DtAndPlcOfBirth/CtryOfBirth', 'Debtor country of birth', 'CountryCode', 2, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/Id/PrvtId/Othr/Id', 'CstmrCdtTrfInitn/PmtInf/Dbtr/Id/PrvtId/Othr/Id', 'Debtor private ID', 'Max35Text', 35, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/Id/PrvtId/Othr/SchmeNm/Cd', 'CstmrCdtTrfInitn/PmtInf/Dbtr/Id/PrvtId/Othr/SchmeNm/Cd', 'Debtor private ID scheme code', 'ExternalPersonIdentification1Code', 4, FALSE, 'Debtor'),
    ('pain.001', 'PmtInf/Dbtr/CtryOfRes', 'CstmrCdtTrfInitn/PmtInf/Dbtr/CtryOfRes', 'Debtor country of residence', 'CountryCode', 2, FALSE, 'Debtor'),

    -- ==================== DEBTOR ACCOUNT ====================
    ('pain.001', 'PmtInf/DbtrAcct/Id/IBAN', 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Id/IBAN', 'Debtor IBAN', 'IBAN2007Identifier', 34, FALSE, 'DebtorAccount'),
    ('pain.001', 'PmtInf/DbtrAcct/Id/Othr/Id', 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Id/Othr/Id', 'Debtor other account ID', 'Max34Text', 34, FALSE, 'DebtorAccount'),
    ('pain.001', 'PmtInf/DbtrAcct/Id/Othr/SchmeNm/Cd', 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Id/Othr/SchmeNm/Cd', 'Debtor account scheme code', 'ExternalAccountIdentification1Code', 4, FALSE, 'DebtorAccount'),
    ('pain.001', 'PmtInf/DbtrAcct/Id/Othr/SchmeNm/Prtry', 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Id/Othr/SchmeNm/Prtry', 'Debtor account scheme proprietary', 'Max35Text', 35, FALSE, 'DebtorAccount'),
    ('pain.001', 'PmtInf/DbtrAcct/Id/Othr/Issr', 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Id/Othr/Issr', 'Debtor account issuer', 'Max35Text', 35, FALSE, 'DebtorAccount'),
    ('pain.001', 'PmtInf/DbtrAcct/Tp/Cd', 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Tp/Cd', 'Debtor account type code', 'ExternalCashAccountType1Code', 4, FALSE, 'DebtorAccount'),
    ('pain.001', 'PmtInf/DbtrAcct/Tp/Prtry', 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Tp/Prtry', 'Debtor account type proprietary', 'Max35Text', 35, FALSE, 'DebtorAccount'),
    ('pain.001', 'PmtInf/DbtrAcct/Ccy', 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Ccy', 'Debtor account currency', 'ActiveOrHistoricCurrencyCode', 3, FALSE, 'DebtorAccount'),
    ('pain.001', 'PmtInf/DbtrAcct/Nm', 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Nm', 'Debtor account name', 'Max70Text', 70, FALSE, 'DebtorAccount'),
    ('pain.001', 'PmtInf/DbtrAcct/Prxy/Tp/Cd', 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Prxy/Tp/Cd', 'Debtor account proxy type code', 'ExternalProxyAccountType1Code', 4, FALSE, 'DebtorAccount'),
    ('pain.001', 'PmtInf/DbtrAcct/Prxy/Id', 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Prxy/Id', 'Debtor account proxy ID', 'Max2048Text', 2048, FALSE, 'DebtorAccount'),

    -- ==================== DEBTOR AGENT ====================
    ('pain.001', 'PmtInf/DbtrAgt/FinInstnId/BICFI', 'CstmrCdtTrfInitn/PmtInf/DbtrAgt/FinInstnId/BICFI', 'Debtor agent BIC', 'BICFIDec2014Identifier', 11, FALSE, 'DebtorAgent'),
    ('pain.001', 'PmtInf/DbtrAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd', 'CstmrCdtTrfInitn/PmtInf/DbtrAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd', 'Debtor agent clearing system code', 'ExternalClearingSystemIdentification1Code', 5, FALSE, 'DebtorAgent'),
    ('pain.001', 'PmtInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'CstmrCdtTrfInitn/PmtInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'Debtor agent member ID', 'Max35Text', 35, FALSE, 'DebtorAgent'),
    ('pain.001', 'PmtInf/DbtrAgt/FinInstnId/LEI', 'CstmrCdtTrfInitn/PmtInf/DbtrAgt/FinInstnId/LEI', 'Debtor agent LEI', 'LEIIdentifier', 20, FALSE, 'DebtorAgent'),
    ('pain.001', 'PmtInf/DbtrAgt/FinInstnId/Nm', 'CstmrCdtTrfInitn/PmtInf/DbtrAgt/FinInstnId/Nm', 'Debtor agent name', 'Max140Text', 140, FALSE, 'DebtorAgent'),
    ('pain.001', 'PmtInf/DbtrAgt/FinInstnId/PstlAdr/TwnNm', 'CstmrCdtTrfInitn/PmtInf/DbtrAgt/FinInstnId/PstlAdr/TwnNm', 'Debtor agent town', 'Max35Text', 35, FALSE, 'DebtorAgent'),
    ('pain.001', 'PmtInf/DbtrAgt/FinInstnId/PstlAdr/Ctry', 'CstmrCdtTrfInitn/PmtInf/DbtrAgt/FinInstnId/PstlAdr/Ctry', 'Debtor agent country', 'CountryCode', 2, FALSE, 'DebtorAgent'),
    ('pain.001', 'PmtInf/DbtrAgt/BrnchId/Id', 'CstmrCdtTrfInitn/PmtInf/DbtrAgt/BrnchId/Id', 'Debtor agent branch ID', 'Max35Text', 35, FALSE, 'DebtorAgent'),
    ('pain.001', 'PmtInf/DbtrAgt/BrnchId/LEI', 'CstmrCdtTrfInitn/PmtInf/DbtrAgt/BrnchId/LEI', 'Debtor agent branch LEI', 'LEIIdentifier', 20, FALSE, 'DebtorAgent'),
    ('pain.001', 'PmtInf/DbtrAgt/BrnchId/Nm', 'CstmrCdtTrfInitn/PmtInf/DbtrAgt/BrnchId/Nm', 'Debtor agent branch name', 'Max140Text', 140, FALSE, 'DebtorAgent'),

    -- ==================== ULTIMATE DEBTOR ====================
    ('pain.001', 'PmtInf/UltmtDbtr/Nm', 'CstmrCdtTrfInitn/PmtInf/UltmtDbtr/Nm', 'Ultimate debtor name', 'Max140Text', 140, FALSE, 'UltimateDebtor'),
    ('pain.001', 'PmtInf/UltmtDbtr/Id/OrgId/AnyBIC', 'CstmrCdtTrfInitn/PmtInf/UltmtDbtr/Id/OrgId/AnyBIC', 'Ultimate debtor BIC', 'AnyBICDec2014Identifier', 11, FALSE, 'UltimateDebtor'),
    ('pain.001', 'PmtInf/UltmtDbtr/Id/OrgId/LEI', 'CstmrCdtTrfInitn/PmtInf/UltmtDbtr/Id/OrgId/LEI', 'Ultimate debtor LEI', 'LEIIdentifier', 20, FALSE, 'UltimateDebtor'),
    ('pain.001', 'PmtInf/UltmtDbtr/Id/OrgId/Othr/Id', 'CstmrCdtTrfInitn/PmtInf/UltmtDbtr/Id/OrgId/Othr/Id', 'Ultimate debtor org ID', 'Max35Text', 35, FALSE, 'UltimateDebtor'),
    ('pain.001', 'PmtInf/UltmtDbtr/CtryOfRes', 'CstmrCdtTrfInitn/PmtInf/UltmtDbtr/CtryOfRes', 'Ultimate debtor country of residence', 'CountryCode', 2, FALSE, 'UltimateDebtor'),

    -- ==================== CHARGES ====================
    ('pain.001', 'PmtInf/ChrgBr', 'CstmrCdtTrfInitn/PmtInf/ChrgBr', 'Charge bearer', 'ChargeBearerType1Code', 4, FALSE, 'Charges'),
    ('pain.001', 'PmtInf/ChrgsAcct/Id/IBAN', 'CstmrCdtTrfInitn/PmtInf/ChrgsAcct/Id/IBAN', 'Charges account IBAN', 'IBAN2007Identifier', 34, FALSE, 'Charges'),
    ('pain.001', 'PmtInf/ChrgsAcct/Id/Othr/Id', 'CstmrCdtTrfInitn/PmtInf/ChrgsAcct/Id/Othr/Id', 'Charges account other ID', 'Max34Text', 34, FALSE, 'Charges'),
    ('pain.001', 'PmtInf/ChrgsAcctAgt/FinInstnId/BICFI', 'CstmrCdtTrfInitn/PmtInf/ChrgsAcctAgt/FinInstnId/BICFI', 'Charges account agent BIC', 'BICFIDec2014Identifier', 11, FALSE, 'Charges'),

    -- ==================== CREDIT TRANSFER TRANSACTION INFO ====================
    ('pain.001', 'PmtInf/CdtTrfTxInf/PmtId/InstrId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtId/InstrId', 'Instruction ID', 'Max35Text', 35, FALSE, 'Transaction'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/PmtId/EndToEndId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtId/EndToEndId', 'End-to-end ID', 'Max35Text', 35, TRUE, 'Transaction'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/PmtId/TxId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtId/TxId', 'Transaction ID', 'Max35Text', 35, FALSE, 'Transaction'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/PmtId/UETR', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtId/UETR', 'UETR', 'UUIDv4Identifier', 36, FALSE, 'Transaction'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/PmtTpInf/InstrPrty', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtTpInf/InstrPrty', 'Transaction instruction priority', 'Priority2Code', 4, FALSE, 'Transaction'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/PmtTpInf/SvcLvl/Cd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtTpInf/SvcLvl/Cd', 'Transaction service level code', 'ExternalServiceLevel1Code', 4, FALSE, 'Transaction'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/PmtTpInf/LclInstrm/Cd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtTpInf/LclInstrm/Cd', 'Transaction local instrument code', 'ExternalLocalInstrument1Code', 35, FALSE, 'Transaction'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/PmtTpInf/CtgyPurp/Cd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtTpInf/CtgyPurp/Cd', 'Transaction category purpose code', 'ExternalCategoryPurpose1Code', 4, FALSE, 'Transaction'),

    -- ==================== AMOUNT ====================
    ('pain.001', 'PmtInf/CdtTrfTxInf/Amt/InstdAmt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Amt/InstdAmt', 'Instructed amount', 'ActiveOrHistoricCurrencyAndAmount', NULL, TRUE, 'Amount'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Amt/InstdAmt/@Ccy', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Amt/InstdAmt/@Ccy', 'Instructed amount currency', 'ActiveOrHistoricCurrencyCode', 3, TRUE, 'Amount'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Amt/EqvtAmt/Amt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Amt/EqvtAmt/Amt', 'Equivalent amount', 'ActiveOrHistoricCurrencyAndAmount', NULL, FALSE, 'Amount'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Amt/EqvtAmt/CcyOfTrf', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Amt/EqvtAmt/CcyOfTrf', 'Currency of transfer', 'ActiveOrHistoricCurrencyCode', 3, FALSE, 'Amount'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/XchgRateInf/UnitCcy', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/XchgRateInf/UnitCcy', 'Exchange rate unit currency', 'ActiveOrHistoricCurrencyCode', 3, FALSE, 'Amount'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/XchgRateInf/XchgRt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/XchgRateInf/XchgRt', 'Exchange rate', 'BaseOneRate', NULL, FALSE, 'Amount'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/XchgRateInf/RateTp', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/XchgRateInf/RateTp', 'Exchange rate type', 'ExchangeRateType1Code', 4, FALSE, 'Amount'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/XchgRateInf/CtrctId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/XchgRateInf/CtrctId', 'Exchange rate contract ID', 'Max35Text', 35, FALSE, 'Amount'),

    -- ==================== CREDITOR AGENT ====================
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI', 'Creditor agent BIC', 'BICFIDec2014Identifier', 11, FALSE, 'CreditorAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/ClrSysId/Cd', 'Creditor agent clearing system code', 'ExternalClearingSystemIdentification1Code', 5, FALSE, 'CreditorAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', 'Creditor agent member ID', 'Max35Text', 35, FALSE, 'CreditorAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/LEI', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/LEI', 'Creditor agent LEI', 'LEIIdentifier', 20, FALSE, 'CreditorAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/Nm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/Nm', 'Creditor agent name', 'Max140Text', 140, FALSE, 'CreditorAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/PstlAdr/TwnNm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/PstlAdr/TwnNm', 'Creditor agent town', 'Max35Text', 35, FALSE, 'CreditorAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/PstlAdr/Ctry', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/PstlAdr/Ctry', 'Creditor agent country', 'CountryCode', 2, FALSE, 'CreditorAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAgt/BrnchId/Id', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAgt/BrnchId/Id', 'Creditor agent branch ID', 'Max35Text', 35, FALSE, 'CreditorAgent'),

    -- ==================== CREDITOR (Beneficiary) ====================
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/Nm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/Nm', 'Creditor name', 'Max140Text', 140, TRUE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/AdrTp/Cd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/AdrTp/Cd', 'Creditor address type', 'AddressType2Code', 4, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/Dept', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/Dept', 'Creditor department', 'Max70Text', 70, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/SubDept', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/SubDept', 'Creditor sub-department', 'Max70Text', 70, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/StrtNm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/StrtNm', 'Creditor street name', 'Max70Text', 70, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/BldgNb', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/BldgNb', 'Creditor building number', 'Max16Text', 16, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/BldgNm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/BldgNm', 'Creditor building name', 'Max35Text', 35, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/Flr', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/Flr', 'Creditor floor', 'Max70Text', 70, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/PstBx', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/PstBx', 'Creditor post box', 'Max16Text', 16, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/Room', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/Room', 'Creditor room', 'Max70Text', 70, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/PstCd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/PstCd', 'Creditor postal code', 'Max16Text', 16, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/TwnNm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/TwnNm', 'Creditor town name', 'Max35Text', 35, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/TwnLctnNm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/TwnLctnNm', 'Creditor town location name', 'Max35Text', 35, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/DstrctNm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/DstrctNm', 'Creditor district name', 'Max35Text', 35, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/CtrySubDvsn', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/CtrySubDvsn', 'Creditor country subdivision', 'Max35Text', 35, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/Ctry', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/Ctry', 'Creditor country', 'CountryCode', 2, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/AdrLine', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/AdrLine', 'Creditor address line', 'Max70Text', 70, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/Id/OrgId/AnyBIC', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/Id/OrgId/AnyBIC', 'Creditor BIC', 'AnyBICDec2014Identifier', 11, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/Id/OrgId/LEI', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/Id/OrgId/LEI', 'Creditor LEI', 'LEIIdentifier', 20, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/Id/OrgId/Othr/Id', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/Id/OrgId/Othr/Id', 'Creditor organisation ID', 'Max35Text', 35, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/Id/PrvtId/DtAndPlcOfBirth/BirthDt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/Id/PrvtId/DtAndPlcOfBirth/BirthDt', 'Creditor birth date', 'ISODate', NULL, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/Id/PrvtId/DtAndPlcOfBirth/CityOfBirth', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/Id/PrvtId/DtAndPlcOfBirth/CityOfBirth', 'Creditor city of birth', 'Max35Text', 35, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/Id/PrvtId/DtAndPlcOfBirth/CtryOfBirth', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/Id/PrvtId/DtAndPlcOfBirth/CtryOfBirth', 'Creditor country of birth', 'CountryCode', 2, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/Id/PrvtId/Othr/Id', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/Id/PrvtId/Othr/Id', 'Creditor private ID', 'Max35Text', 35, FALSE, 'Creditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Cdtr/CtryOfRes', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/CtryOfRes', 'Creditor country of residence', 'CountryCode', 2, FALSE, 'Creditor'),

    -- ==================== CREDITOR ACCOUNT ====================
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAcct/Id/IBAN', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Id/IBAN', 'Creditor IBAN', 'IBAN2007Identifier', 34, FALSE, 'CreditorAccount'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAcct/Id/Othr/Id', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Id/Othr/Id', 'Creditor other account ID', 'Max34Text', 34, FALSE, 'CreditorAccount'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAcct/Id/Othr/SchmeNm/Cd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Id/Othr/SchmeNm/Cd', 'Creditor account scheme code', 'ExternalAccountIdentification1Code', 4, FALSE, 'CreditorAccount'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAcct/Tp/Cd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Tp/Cd', 'Creditor account type code', 'ExternalCashAccountType1Code', 4, FALSE, 'CreditorAccount'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAcct/Ccy', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Ccy', 'Creditor account currency', 'ActiveOrHistoricCurrencyCode', 3, FALSE, 'CreditorAccount'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAcct/Nm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Nm', 'Creditor account name', 'Max70Text', 70, FALSE, 'CreditorAccount'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAcct/Prxy/Tp/Cd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Prxy/Tp/Cd', 'Creditor account proxy type code', 'ExternalProxyAccountType1Code', 4, FALSE, 'CreditorAccount'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/CdtrAcct/Prxy/Id', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Prxy/Id', 'Creditor account proxy ID', 'Max2048Text', 2048, FALSE, 'CreditorAccount'),

    -- ==================== ULTIMATE CREDITOR ====================
    ('pain.001', 'PmtInf/CdtTrfTxInf/UltmtCdtr/Nm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/UltmtCdtr/Nm', 'Ultimate creditor name', 'Max140Text', 140, FALSE, 'UltimateCreditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/UltmtCdtr/Id/OrgId/AnyBIC', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/UltmtCdtr/Id/OrgId/AnyBIC', 'Ultimate creditor BIC', 'AnyBICDec2014Identifier', 11, FALSE, 'UltimateCreditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/UltmtCdtr/Id/OrgId/LEI', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/UltmtCdtr/Id/OrgId/LEI', 'Ultimate creditor LEI', 'LEIIdentifier', 20, FALSE, 'UltimateCreditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/UltmtCdtr/Id/OrgId/Othr/Id', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/UltmtCdtr/Id/OrgId/Othr/Id', 'Ultimate creditor org ID', 'Max35Text', 35, FALSE, 'UltimateCreditor'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/UltmtCdtr/CtryOfRes', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/UltmtCdtr/CtryOfRes', 'Ultimate creditor country of residence', 'CountryCode', 2, FALSE, 'UltimateCreditor'),

    -- ==================== INTERMEDIARY AGENTS ====================
    ('pain.001', 'PmtInf/CdtTrfTxInf/IntrmyAgt1/FinInstnId/BICFI', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/IntrmyAgt1/FinInstnId/BICFI', 'Intermediary agent 1 BIC', 'BICFIDec2014Identifier', 11, FALSE, 'IntermediaryAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/IntrmyAgt1/FinInstnId/ClrSysMmbId/MmbId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/IntrmyAgt1/FinInstnId/ClrSysMmbId/MmbId', 'Intermediary agent 1 member ID', 'Max35Text', 35, FALSE, 'IntermediaryAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/IntrmyAgt1/FinInstnId/LEI', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/IntrmyAgt1/FinInstnId/LEI', 'Intermediary agent 1 LEI', 'LEIIdentifier', 20, FALSE, 'IntermediaryAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/IntrmyAgt1/FinInstnId/Nm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/IntrmyAgt1/FinInstnId/Nm', 'Intermediary agent 1 name', 'Max140Text', 140, FALSE, 'IntermediaryAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/IntrmyAgt1Acct/Id/IBAN', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/IntrmyAgt1Acct/Id/IBAN', 'Intermediary agent 1 account IBAN', 'IBAN2007Identifier', 34, FALSE, 'IntermediaryAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/IntrmyAgt2/FinInstnId/BICFI', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/IntrmyAgt2/FinInstnId/BICFI', 'Intermediary agent 2 BIC', 'BICFIDec2014Identifier', 11, FALSE, 'IntermediaryAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/IntrmyAgt2/FinInstnId/Nm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/IntrmyAgt2/FinInstnId/Nm', 'Intermediary agent 2 name', 'Max140Text', 140, FALSE, 'IntermediaryAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/IntrmyAgt3/FinInstnId/BICFI', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/IntrmyAgt3/FinInstnId/BICFI', 'Intermediary agent 3 BIC', 'BICFIDec2014Identifier', 11, FALSE, 'IntermediaryAgent'),

    -- ==================== PURPOSE ====================
    ('pain.001', 'PmtInf/CdtTrfTxInf/Purp/Cd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Purp/Cd', 'Purpose code', 'ExternalPurpose1Code', 4, FALSE, 'Purpose'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Purp/Prtry', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Purp/Prtry', 'Purpose proprietary', 'Max35Text', 35, FALSE, 'Purpose'),

    -- ==================== REGULATORY REPORTING ====================
    ('pain.001', 'PmtInf/CdtTrfTxInf/RgltryRptg/DbtCdtRptgInd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RgltryRptg/DbtCdtRptgInd', 'Debit credit reporting indicator', 'RegulatoryReportingType1Code', 4, FALSE, 'RegulatoryReporting'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RgltryRptg/Authrty/Nm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RgltryRptg/Authrty/Nm', 'Reporting authority name', 'Max140Text', 140, FALSE, 'RegulatoryReporting'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RgltryRptg/Authrty/Ctry', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RgltryRptg/Authrty/Ctry', 'Reporting authority country', 'CountryCode', 2, FALSE, 'RegulatoryReporting'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RgltryRptg/Dtls/Tp', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RgltryRptg/Dtls/Tp', 'Regulatory details type', 'Max35Text', 35, FALSE, 'RegulatoryReporting'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RgltryRptg/Dtls/Dt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RgltryRptg/Dtls/Dt', 'Regulatory details date', 'ISODate', NULL, FALSE, 'RegulatoryReporting'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RgltryRptg/Dtls/Ctry', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RgltryRptg/Dtls/Ctry', 'Regulatory details country', 'CountryCode', 2, FALSE, 'RegulatoryReporting'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RgltryRptg/Dtls/Cd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RgltryRptg/Dtls/Cd', 'Regulatory details code', 'Max10Text', 10, FALSE, 'RegulatoryReporting'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RgltryRptg/Dtls/Amt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RgltryRptg/Dtls/Amt', 'Regulatory details amount', 'ActiveOrHistoricCurrencyAndAmount', NULL, FALSE, 'RegulatoryReporting'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RgltryRptg/Dtls/Inf', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RgltryRptg/Dtls/Inf', 'Regulatory details information', 'Max35Text', 35, FALSE, 'RegulatoryReporting'),

    -- ==================== TAX ====================
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Cdtr/TaxId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Cdtr/TaxId', 'Tax creditor ID', 'Max35Text', 35, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Cdtr/RegnId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Cdtr/RegnId', 'Tax creditor registration ID', 'Max35Text', 35, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Cdtr/TaxTp', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Cdtr/TaxTp', 'Tax creditor type', 'Max35Text', 35, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Dbtr/TaxId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Dbtr/TaxId', 'Tax debtor ID', 'Max35Text', 35, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Dbtr/RegnId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Dbtr/RegnId', 'Tax debtor registration ID', 'Max35Text', 35, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Dbtr/TaxTp', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Dbtr/TaxTp', 'Tax debtor type', 'Max35Text', 35, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/UltmtDbtr/TaxId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/UltmtDbtr/TaxId', 'Tax ultimate debtor ID', 'Max35Text', 35, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/AdmstnZone', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/AdmstnZone', 'Tax administration zone', 'Max35Text', 35, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/RefNb', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/RefNb', 'Tax reference number', 'Max140Text', 140, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Mtd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Mtd', 'Tax method', 'Max35Text', 35, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/TtlTaxblBaseAmt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/TtlTaxblBaseAmt', 'Total taxable base amount', 'ActiveOrHistoricCurrencyAndAmount', NULL, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/TtlTaxAmt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/TtlTaxAmt', 'Total tax amount', 'ActiveOrHistoricCurrencyAndAmount', NULL, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Dt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Dt', 'Tax date', 'ISODate', NULL, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/SeqNb', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/SeqNb', 'Tax sequence number', 'Number', NULL, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Rcrd/Tp', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Rcrd/Tp', 'Tax record type', 'Max35Text', 35, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Rcrd/Ctgy', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Rcrd/Ctgy', 'Tax record category', 'Max35Text', 35, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Rcrd/CtgyDtls', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Rcrd/CtgyDtls', 'Tax record category details', 'Max35Text', 35, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Rcrd/DbtrSts', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Rcrd/DbtrSts', 'Tax debtor status', 'Max35Text', 35, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Rcrd/CertId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Rcrd/CertId', 'Tax certificate ID', 'Max35Text', 35, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Rcrd/FrmsCd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Rcrd/FrmsCd', 'Tax forms code', 'Max35Text', 35, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Rcrd/Prd/Yr', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Rcrd/Prd/Yr', 'Tax period year', 'ISOYear', 4, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Rcrd/Prd/Tp', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Rcrd/Prd/Tp', 'Tax period type', 'TaxRecordPeriod1Code', 4, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Rcrd/Prd/FrToDt/FrDt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Rcrd/Prd/FrToDt/FrDt', 'Tax period from date', 'ISODate', NULL, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Rcrd/Prd/FrToDt/ToDt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Rcrd/Prd/FrToDt/ToDt', 'Tax period to date', 'ISODate', NULL, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Rcrd/TaxAmt/Rate', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Rcrd/TaxAmt/Rate', 'Tax rate', 'PercentageRate', NULL, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Rcrd/TaxAmt/TaxblBaseAmt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Rcrd/TaxAmt/TaxblBaseAmt', 'Taxable base amount', 'ActiveOrHistoricCurrencyAndAmount', NULL, FALSE, 'Tax'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/Tax/Rcrd/TaxAmt/TtlAmt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Tax/Rcrd/TaxAmt/TtlAmt', 'Tax total amount', 'ActiveOrHistoricCurrencyAndAmount', NULL, FALSE, 'Tax'),

    -- ==================== REMITTANCE INFORMATION ====================
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Ustrd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Ustrd', 'Unstructured remittance info', 'Max140Text', 140, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd', 'Referred document type code', 'DocumentType6Code', 4, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Prtry', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Prtry', 'Referred document type proprietary', 'Max35Text', 35, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Tp/Issr', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Tp/Issr', 'Referred document issuer', 'Max35Text', 35, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Nb', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Nb', 'Referred document number', 'Max35Text', 35, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/RltdDt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/RltdDt', 'Referred document related date', 'ISODate', NULL, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/DuePyblAmt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/DuePyblAmt', 'Due payable amount', 'ActiveOrHistoricCurrencyAndAmount', NULL, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/DscntApldAmt/Amt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/DscntApldAmt/Amt', 'Discount applied amount', 'ActiveOrHistoricCurrencyAndAmount', NULL, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/CdtNoteAmt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/CdtNoteAmt', 'Credit note amount', 'ActiveOrHistoricCurrencyAndAmount', NULL, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/TaxAmt/Amt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/TaxAmt/Amt', 'Tax amount in remittance', 'ActiveOrHistoricCurrencyAndAmount', NULL, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/AdjstmntAmtAndRsn/Amt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/AdjstmntAmtAndRsn/Amt', 'Adjustment amount', 'ActiveOrHistoricCurrencyAndAmount', NULL, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/AdjstmntAmtAndRsn/CdtDbtInd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/AdjstmntAmtAndRsn/CdtDbtInd', 'Adjustment credit/debit indicator', 'CreditDebitCode', 4, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/AdjstmntAmtAndRsn/Rsn', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/AdjstmntAmtAndRsn/Rsn', 'Adjustment reason', 'Max4Text', 4, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/AdjstmntAmtAndRsn/AddtlInf', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/AdjstmntAmtAndRsn/AddtlInf', 'Adjustment additional info', 'Max140Text', 140, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/RmtdAmt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/RfrdDocAmt/RmtdAmt', 'Remitted amount', 'ActiveOrHistoricCurrencyAndAmount', NULL, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Tp/CdOrPrtry/Cd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Tp/CdOrPrtry/Cd', 'Creditor reference type code', 'DocumentType3Code', 4, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Tp/CdOrPrtry/Prtry', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Tp/CdOrPrtry/Prtry', 'Creditor reference type proprietary', 'Max35Text', 35, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Tp/Issr', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Tp/Issr', 'Creditor reference issuer', 'Max35Text', 35, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Ref', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Ref', 'Creditor reference', 'Max35Text', 35, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/Invcr/Nm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/Invcr/Nm', 'Invoicer name', 'Max140Text', 140, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/Invcee/Nm', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/Invcee/Nm', 'Invoicee name', 'Max140Text', 140, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/TaxRmt/Cdtr/TaxId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/TaxRmt/Cdtr/TaxId', 'Tax remittance creditor tax ID', 'Max35Text', 35, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/TaxRmt/Dbtr/TaxId', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/TaxRmt/Dbtr/TaxId', 'Tax remittance debtor tax ID', 'Max35Text', 35, FALSE, 'RemittanceInformation'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/RmtInf/Strd/AddtlRmtInf', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd/AddtlRmtInf', 'Additional remittance information', 'Max140Text', 140, FALSE, 'RemittanceInformation'),

    -- ==================== INSTRUCTION FOR AGENTS ====================
    ('pain.001', 'PmtInf/CdtTrfTxInf/InstrForCdtrAgt/Cd', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/InstrForCdtrAgt/Cd', 'Instruction for creditor agent code', 'Instruction3Code', 4, FALSE, 'InstructionForAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/InstrForCdtrAgt/InstrInf', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/InstrForCdtrAgt/InstrInf', 'Instruction for creditor agent info', 'Max140Text', 140, FALSE, 'InstructionForAgent'),
    ('pain.001', 'PmtInf/CdtTrfTxInf/InstrForDbtrAgt', 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/InstrForDbtrAgt', 'Instruction for debtor agent', 'Max140Text', 140, FALSE, 'InstructionForAgent'),

    -- ==================== SUPPLEMENTARY DATA ====================
    ('pain.001', 'SplmtryData/PlcAndNm', 'CstmrCdtTrfInitn/SplmtryData/PlcAndNm', 'Supplementary data placement and name', 'Max350Text', 350, FALSE, 'SupplementaryData'),
    ('pain.001', 'SplmtryData/Envlp', 'CstmrCdtTrfInitn/SplmtryData/Envlp', 'Supplementary data envelope', 'SupplementaryDataEnvelope1', NULL, FALSE, 'SupplementaryData')

ON CONFLICT (format_id, field_path) DO UPDATE SET
    field_name = EXCLUDED.field_name,
    field_description = EXCLUDED.field_description,
    data_type = EXCLUDED.data_type,
    max_length = EXCLUDED.max_length,
    is_mandatory = EXCLUDED.is_mandatory,
    field_category = EXCLUDED.field_category,
    updated_at = CURRENT_TIMESTAMP;

-- Count what we inserted
-- SELECT COUNT(*) as pain001_standard_fields FROM mapping.standard_fields WHERE format_id = 'pain.001';
