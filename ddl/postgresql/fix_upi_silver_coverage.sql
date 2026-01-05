-- Fix UPI Standard -> Silver Field Coverage to 100%
-- This script adds missing columns to silver.stg_upi and creates mappings in silver_field_mappings
-- source_path MUST match standard_fields.field_path exactly for traceability

BEGIN;

-- ====================================================================================
-- STEP 1: Add missing columns to silver.stg_upi
-- ====================================================================================

-- Ack fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS ack_api VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS ack_err VARCHAR(100);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS ack_req_msg_id VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS ack_ts TIMESTAMP;

-- Head fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS head_msg_id VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS head_org_id VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS head_ts TIMESTAMP;
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS head_ver VARCHAR(10);

-- Meta fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS meta_name VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS meta_value VARCHAR(255);

-- Payee fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_addr VARCHAR(100);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_code VARCHAR(10);
-- payee_name already exists
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_seq_num VARCHAR(10);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_type VARCHAR(20);

-- Payee/Ac fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_ac_addr_type VARCHAR(20);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_ac_acnum VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_ac_actype VARCHAR(20);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_ac_ifsc VARCHAR(20);

-- Payee/Device fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_device_geocode VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_device_id VARCHAR(100);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_device_ip VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_device_location VARCHAR(100);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_device_mobile VARCHAR(20);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_device_os VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_device_type VARCHAR(20);

-- Payee/Info fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_identity_type VARCHAR(20);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_identity_verified_name VARCHAR(100);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_rating_verified_address VARCHAR(20);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payee_rating_whitelisted VARCHAR(10);

-- Payee/Merchant fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS merchant_id VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS merchant_sub_id VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS merchant_term_id VARCHAR(50);

-- Payer fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_addr VARCHAR(100);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_code VARCHAR(10);
-- payer_name already exists
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_seq_num VARCHAR(10);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_type VARCHAR(20);

-- Payer/Ac fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_ac_addr_type VARCHAR(20);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_ac_acnum VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_ac_actype VARCHAR(20);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_ac_ifsc VARCHAR(20);

-- Payer/Amount fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_amount_curr VARCHAR(3);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_amount_value DECIMAL(18,2);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_amount_split_name VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_amount_split_value DECIMAL(18,2);

-- Payer/Creds fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_cred_sub_type VARCHAR(20);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_cred_type VARCHAR(20);

-- Payer/Device fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_device_geocode VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_device_id VARCHAR(100);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_device_ip VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_device_location VARCHAR(100);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_device_mobile VARCHAR(20);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_device_os VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_device_type VARCHAR(20);

-- Payer/Info fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_identity_type VARCHAR(20);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_identity_verified_name VARCHAR(100);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_rating_verified_address VARCHAR(20);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS payer_rating_whitelisted VARCHAR(10);

-- Psp fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS psp_name VARCHAR(100);

-- Ref fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS ref_addr VARCHAR(100);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS ref_seq_num VARCHAR(10);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS ref_type VARCHAR(20);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS ref_value VARCHAR(255);

-- ReqAuthDetails fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS req_auth_api VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS req_auth_version VARCHAR(10);

-- Resp fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS resp_err_code VARCHAR(10);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS resp_msg_id VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS resp_req_msg_id VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS resp_result VARCHAR(20);

-- Txn fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS txn_cust_ref VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS txn_id VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS txn_note VARCHAR(255);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS txn_org_resp_code VARCHAR(10);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS txn_org_txn_id VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS txn_ref_id VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS txn_ref_url VARCHAR(255);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS txn_ts TIMESTAMP;
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS txn_type VARCHAR(20);

-- Txn/RiskScores fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS risk_score_provider VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS risk_score_type VARCHAR(20);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS risk_score_value VARCHAR(20);

-- Txn/Rules fields
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS rule_name VARCHAR(50);
ALTER TABLE silver.stg_upi ADD COLUMN IF NOT EXISTS rule_value VARCHAR(255);

-- ====================================================================================
-- STEP 2: Delete existing UPI mappings (we'll recreate them all)
-- ====================================================================================

DELETE FROM mapping.silver_field_mappings WHERE format_id = 'UPI';

-- ====================================================================================
-- STEP 3: Insert new mappings for all 84 standard fields
-- source_path MUST match standard_fields.field_path exactly
-- parser_path contains the actual key from parser output
-- ordinal_position is required (NOT NULL)
-- ====================================================================================

-- System fields (not from standard but needed for silver table)
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'stg_id', '_GENERATED_UUID', NULL, 'VARCHAR', true, true, 'SYSTEM', 1),
    ('UPI', 'raw_id', '_RAW_ID', NULL, 'VARCHAR', true, true, 'SYSTEM', 2),
    ('UPI', '_batch_id', '_BATCH_ID', NULL, 'VARCHAR', false, true, 'SYSTEM', 3),
    ('UPI', 'message_type', '_MESSAGE_TYPE', NULL, 'VARCHAR', false, true, 'SYSTEM', 4);

-- Ack fields (4) - ordinal 5-8
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'ack_api', 'Ack/@api', 'ackApi', 'VARCHAR', false, true, 'STANDARD', 5),
    ('UPI', 'ack_err', 'Ack/@err', 'ackErr', 'VARCHAR', false, true, 'STANDARD', 6),
    ('UPI', 'ack_req_msg_id', 'Ack/@reqMsgId', 'ackReqMsgId', 'VARCHAR', false, true, 'STANDARD', 7),
    ('UPI', 'ack_ts', 'Ack/@ts', 'ackTs', 'TIMESTAMP', false, true, 'STANDARD', 8);

-- Head fields (4) - ordinal 9-12
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'head_msg_id', 'Head/@msgId', 'headMsgId', 'VARCHAR', true, true, 'STANDARD', 9),
    ('UPI', 'head_org_id', 'Head/@orgId', 'headOrgId', 'VARCHAR', true, true, 'STANDARD', 10),
    ('UPI', 'head_ts', 'Head/@ts', 'headTs', 'TIMESTAMP', true, true, 'STANDARD', 11),
    ('UPI', 'head_ver', 'Head/@ver', 'headVer', 'VARCHAR', true, true, 'STANDARD', 12);

-- Meta fields (2) - ordinal 13-14
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'meta_name', 'Meta/@name', 'metaName', 'VARCHAR', false, true, 'STANDARD', 13),
    ('UPI', 'meta_value', 'Meta/@value', 'metaValue', 'VARCHAR', false, true, 'STANDARD', 14);

-- Payee basic fields (5) - ordinal 15-19
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'payee_addr', 'Payee/@addr', 'payeeAddr', 'VARCHAR', true, true, 'STANDARD', 15),
    ('UPI', 'payee_code', 'Payee/@code', 'payeeCode', 'VARCHAR', false, true, 'STANDARD', 16),
    ('UPI', 'payee_name', 'Payee/@name', 'payeeName', 'VARCHAR', false, true, 'STANDARD', 17),
    ('UPI', 'payee_seq_num', 'Payee/@seqNum', 'payeeSeqNum', 'VARCHAR', false, true, 'STANDARD', 18),
    ('UPI', 'payee_type', 'Payee/@type', 'payeeType', 'VARCHAR', false, true, 'STANDARD', 19);

-- Payee/Ac fields (4) - ordinal 20-23
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'payee_ac_addr_type', 'Payee/Ac/@addrType', 'payeeAcAddrType', 'VARCHAR', false, true, 'STANDARD', 20),
    ('UPI', 'payee_ac_acnum', 'Payee/Ac/Detail[@name=ACNUM]/@value', 'payeeAcAcnum', 'VARCHAR', false, true, 'STANDARD', 21),
    ('UPI', 'payee_ac_actype', 'Payee/Ac/Detail[@name=ACTYPE]/@value', 'payeeAcActype', 'VARCHAR', false, true, 'STANDARD', 22),
    ('UPI', 'payee_ac_ifsc', 'Payee/Ac/Detail[@name=IFSC]/@value', 'payeeAcIfsc', 'VARCHAR', false, true, 'STANDARD', 23);

-- Payee/Device fields (7) - ordinal 24-30
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'payee_device_geocode', 'Payee/Device/Tag[@name=GEOCODE]/@value', 'payeeDeviceGeocode', 'VARCHAR', false, true, 'STANDARD', 24),
    ('UPI', 'payee_device_id', 'Payee/Device/Tag[@name=ID]/@value', 'payeeDeviceId', 'VARCHAR', false, true, 'STANDARD', 25),
    ('UPI', 'payee_device_ip', 'Payee/Device/Tag[@name=IP]/@value', 'payeeDeviceIp', 'VARCHAR', false, true, 'STANDARD', 26),
    ('UPI', 'payee_device_location', 'Payee/Device/Tag[@name=LOCATION]/@value', 'payeeDeviceLocation', 'VARCHAR', false, true, 'STANDARD', 27),
    ('UPI', 'payee_device_mobile', 'Payee/Device/Tag[@name=MOBILE]/@value', 'payeeDeviceMobile', 'VARCHAR', false, true, 'STANDARD', 28),
    ('UPI', 'payee_device_os', 'Payee/Device/Tag[@name=OS]/@value', 'payeeDeviceOs', 'VARCHAR', false, true, 'STANDARD', 29),
    ('UPI', 'payee_device_type', 'Payee/Device/Tag[@name=TYPE]/@value', 'payeeDeviceType', 'VARCHAR', false, true, 'STANDARD', 30);

-- Payee/Info fields (4) - ordinal 31-34
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'payee_identity_type', 'Payee/Info/Identity/@type', 'payeeIdentityType', 'VARCHAR', false, true, 'STANDARD', 31),
    ('UPI', 'payee_identity_verified_name', 'Payee/Info/Identity/@verifiedName', 'payeeIdentityVerifiedName', 'VARCHAR', false, true, 'STANDARD', 32),
    ('UPI', 'payee_rating_verified_address', 'Payee/Info/Rating/@VerifiedAddress', 'payeeRatingVerifiedAddress', 'VARCHAR', false, true, 'STANDARD', 33),
    ('UPI', 'payee_rating_whitelisted', 'Payee/Info/Rating/@whiteListed', 'payeeRatingWhitelisted', 'VARCHAR', false, true, 'STANDARD', 34);

-- Payee/Merchant fields (3) - ordinal 35-37
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'merchant_id', 'Payee/Merchant/@id', 'merchantId', 'VARCHAR', false, true, 'STANDARD', 35),
    ('UPI', 'merchant_sub_id', 'Payee/Merchant/@subId', 'merchantSubId', 'VARCHAR', false, true, 'STANDARD', 36),
    ('UPI', 'merchant_term_id', 'Payee/Merchant/@termId', 'merchantTermId', 'VARCHAR', false, true, 'STANDARD', 37);

-- Payer basic fields (5) - ordinal 38-42
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'payer_addr', 'Payer/@addr', 'payerAddr', 'VARCHAR', true, true, 'STANDARD', 38),
    ('UPI', 'payer_code', 'Payer/@code', 'payerCode', 'VARCHAR', false, true, 'STANDARD', 39),
    ('UPI', 'payer_name', 'Payer/@name', 'payerName', 'VARCHAR', false, true, 'STANDARD', 40),
    ('UPI', 'payer_seq_num', 'Payer/@seqNum', 'payerSeqNum', 'VARCHAR', false, true, 'STANDARD', 41),
    ('UPI', 'payer_type', 'Payer/@type', 'payerType', 'VARCHAR', false, true, 'STANDARD', 42);

-- Payer/Ac fields (4) - ordinal 43-46
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'payer_ac_addr_type', 'Payer/Ac/@addrType', 'payerAcAddrType', 'VARCHAR', false, true, 'STANDARD', 43),
    ('UPI', 'payer_ac_acnum', 'Payer/Ac/Detail[@name=ACNUM]/@value', 'payerAcAcnum', 'VARCHAR', false, true, 'STANDARD', 44),
    ('UPI', 'payer_ac_actype', 'Payer/Ac/Detail[@name=ACTYPE]/@value', 'payerAcActype', 'VARCHAR', false, true, 'STANDARD', 45),
    ('UPI', 'payer_ac_ifsc', 'Payer/Ac/Detail[@name=IFSC]/@value', 'payerAcIfsc', 'VARCHAR', false, true, 'STANDARD', 46);

-- Payer/Amount fields (4) - ordinal 47-50
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'payer_amount_curr', 'Payer/Amount/@curr', 'payerAmountCurr', 'VARCHAR', true, true, 'STANDARD', 47),
    ('UPI', 'payer_amount_value', 'Payer/Amount/@value', 'payerAmountValue', 'DECIMAL', true, true, 'STANDARD', 48),
    ('UPI', 'payer_amount_split_name', 'Payer/Amount/Split/@name', 'payerAmountSplitName', 'VARCHAR', false, true, 'STANDARD', 49),
    ('UPI', 'payer_amount_split_value', 'Payer/Amount/Split/@value', 'payerAmountSplitValue', 'DECIMAL', false, true, 'STANDARD', 50);

-- Payer/Creds fields (2) - ordinal 51-52
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'payer_cred_sub_type', 'Payer/Creds/Cred/@subType', 'payerCredSubType', 'VARCHAR', false, true, 'STANDARD', 51),
    ('UPI', 'payer_cred_type', 'Payer/Creds/Cred/@type', 'payerCredType', 'VARCHAR', false, true, 'STANDARD', 52);

-- Payer/Device fields (7) - ordinal 53-59
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'payer_device_geocode', 'Payer/Device/Tag[@name=GEOCODE]/@value', 'payerDeviceGeocode', 'VARCHAR', false, true, 'STANDARD', 53),
    ('UPI', 'payer_device_id', 'Payer/Device/Tag[@name=ID]/@value', 'payerDeviceId', 'VARCHAR', false, true, 'STANDARD', 54),
    ('UPI', 'payer_device_ip', 'Payer/Device/Tag[@name=IP]/@value', 'payerDeviceIp', 'VARCHAR', false, true, 'STANDARD', 55),
    ('UPI', 'payer_device_location', 'Payer/Device/Tag[@name=LOCATION]/@value', 'payerDeviceLocation', 'VARCHAR', false, true, 'STANDARD', 56),
    ('UPI', 'payer_device_mobile', 'Payer/Device/Tag[@name=MOBILE]/@value', 'payerDeviceMobile', 'VARCHAR', false, true, 'STANDARD', 57),
    ('UPI', 'payer_device_os', 'Payer/Device/Tag[@name=OS]/@value', 'payerDeviceOs', 'VARCHAR', false, true, 'STANDARD', 58),
    ('UPI', 'payer_device_type', 'Payer/Device/Tag[@name=TYPE]/@value', 'payerDeviceType', 'VARCHAR', false, true, 'STANDARD', 59);

-- Payer/Info fields (4) - ordinal 60-63
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'payer_identity_type', 'Payer/Info/Identity/@type', 'payerIdentityType', 'VARCHAR', false, true, 'STANDARD', 60),
    ('UPI', 'payer_identity_verified_name', 'Payer/Info/Identity/@verifiedName', 'payerIdentityVerifiedName', 'VARCHAR', false, true, 'STANDARD', 61),
    ('UPI', 'payer_rating_verified_address', 'Payer/Info/Rating/@VerifiedAddress', 'payerRatingVerifiedAddress', 'VARCHAR', false, true, 'STANDARD', 62),
    ('UPI', 'payer_rating_whitelisted', 'Payer/Info/Rating/@whiteListed', 'payerRatingWhitelisted', 'VARCHAR', false, true, 'STANDARD', 63);

-- Psp fields (1) - ordinal 64
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'psp_name', 'Psp/@name', 'pspName', 'VARCHAR', false, true, 'STANDARD', 64);

-- Ref fields (4) - ordinal 65-68
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'ref_addr', 'Ref/@addr', 'refAddr', 'VARCHAR', false, true, 'STANDARD', 65),
    ('UPI', 'ref_seq_num', 'Ref/@seqNum', 'refSeqNum', 'VARCHAR', false, true, 'STANDARD', 66),
    ('UPI', 'ref_type', 'Ref/@type', 'refType', 'VARCHAR', false, true, 'STANDARD', 67),
    ('UPI', 'ref_value', 'Ref/@value', 'refValue', 'VARCHAR', false, true, 'STANDARD', 68);

-- ReqAuthDetails fields (2) - ordinal 69-70
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'req_auth_api', 'ReqAuthDetails/@api', 'reqAuthApi', 'VARCHAR', false, true, 'STANDARD', 69),
    ('UPI', 'req_auth_version', 'ReqAuthDetails/@version', 'reqAuthVersion', 'VARCHAR', false, true, 'STANDARD', 70);

-- Resp fields (4) - ordinal 71-74
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'resp_err_code', 'Resp/@errCode', 'respErrCode', 'VARCHAR', false, true, 'STANDARD', 71),
    ('UPI', 'resp_msg_id', 'Resp/@msgId', 'respMsgId', 'VARCHAR', true, true, 'STANDARD', 72),
    ('UPI', 'resp_req_msg_id', 'Resp/@reqMsgId', 'respReqMsgId', 'VARCHAR', false, true, 'STANDARD', 73),
    ('UPI', 'resp_result', 'Resp/@result', 'respResult', 'VARCHAR', true, true, 'STANDARD', 74);

-- Txn basic fields (9) - ordinal 75-83
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'txn_cust_ref', 'Txn/@custRef', 'txnCustRef', 'VARCHAR', false, true, 'STANDARD', 75),
    ('UPI', 'txn_id', 'Txn/@id', 'txnId', 'VARCHAR', true, true, 'STANDARD', 76),
    ('UPI', 'txn_note', 'Txn/@note', 'txnNote', 'VARCHAR', false, true, 'STANDARD', 77),
    ('UPI', 'txn_org_resp_code', 'Txn/@orgRespCode', 'txnOrgRespCode', 'VARCHAR', false, true, 'STANDARD', 78),
    ('UPI', 'txn_org_txn_id', 'Txn/@orgTxnId', 'txnOrgTxnId', 'VARCHAR', false, true, 'STANDARD', 79),
    ('UPI', 'txn_ref_id', 'Txn/@refId', 'txnRefId', 'VARCHAR', false, true, 'STANDARD', 80),
    ('UPI', 'txn_ref_url', 'Txn/@refUrl', 'txnRefUrl', 'VARCHAR', false, true, 'STANDARD', 81),
    ('UPI', 'txn_ts', 'Txn/@ts', 'txnTs', 'TIMESTAMP', false, true, 'STANDARD', 82),
    ('UPI', 'txn_type', 'Txn/@type', 'txnType', 'VARCHAR', true, true, 'STANDARD', 83);

-- Txn/RiskScores fields (3) - ordinal 84-86
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'risk_score_provider', 'Txn/RiskScores/Score/@provider', 'riskScoreProvider', 'VARCHAR', false, true, 'STANDARD', 84),
    ('UPI', 'risk_score_type', 'Txn/RiskScores/Score/@type', 'riskScoreType', 'VARCHAR', false, true, 'STANDARD', 85),
    ('UPI', 'risk_score_value', 'Txn/RiskScores/Score/@value', 'riskScoreValue', 'VARCHAR', false, true, 'STANDARD', 86);

-- Txn/Rules fields (2) - ordinal 87-88
INSERT INTO mapping.silver_field_mappings (format_id, target_column, source_path, parser_path, data_type, is_required, is_active, source, ordinal_position)
VALUES
    ('UPI', 'rule_name', 'Txn/Rules/Rule/@name', 'ruleName', 'VARCHAR', false, true, 'STANDARD', 87),
    ('UPI', 'rule_value', 'Txn/Rules/Rule/@value', 'ruleValue', 'VARCHAR', false, true, 'STANDARD', 88);

-- ====================================================================================
-- STEP 4: Link standard_field_id to silver mappings for traceability
-- ====================================================================================

UPDATE mapping.silver_field_mappings sfm
SET standard_field_id = sf.standard_field_id
FROM mapping.standard_fields sf
WHERE sfm.format_id = 'UPI'
  AND sf.format_id = 'UPI'
  AND sfm.source_path = sf.field_path
  AND sfm.source = 'STANDARD';

COMMIT;

-- ====================================================================================
-- VERIFICATION: Check coverage
-- ====================================================================================

SELECT
    'STANDARD FIELDS' as category,
    COUNT(*) as count
FROM mapping.standard_fields
WHERE format_id = 'UPI' AND LOWER(data_type) <> 'complex'
UNION ALL
SELECT
    'SILVER MAPPINGS (STANDARD)',
    COUNT(*)
FROM mapping.silver_field_mappings
WHERE format_id = 'UPI' AND is_active = true AND source = 'STANDARD'
UNION ALL
SELECT
    'SILVER MAPPINGS (ALL)',
    COUNT(*)
FROM mapping.silver_field_mappings
WHERE format_id = 'UPI' AND is_active = true;
