-- ============================================================================
-- ISO 20022 MESSAGE FORMAT MIGRATION
-- ============================================================================
-- This script:
-- 1. Creates missing base format entries (pacs.002.base, pacs.004.base, etc.)
-- 2. Creates new payment system format entries with message type suffix
-- 3. Creates inheritance relationships
-- 4. Deactivates old format entries
-- ============================================================================

BEGIN;

-- ============================================================================
-- PHASE 1: Create Missing Base Format Entries
-- ============================================================================

-- pacs.002.base - Payment Status Report
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES ('pacs.002.base', 'Payment Status Report - Base', 'ISO20022_BASE', 'stg_iso20022_pacs002', 'ISO 20022 pacs.002 base message type', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- pacs.004.base - Payment Return
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES ('pacs.004.base', 'Payment Return - Base', 'ISO20022_BASE', 'stg_iso20022_pacs004', 'ISO 20022 pacs.004 base message type', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- pain.008.base - Customer Direct Debit Initiation
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES ('pain.008.base', 'Customer Direct Debit Initiation - Base', 'ISO20022_BASE', 'stg_iso20022_pain008', 'ISO 20022 pain.008 base message type', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- camt.056.base - Cancellation Request
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES ('camt.056.base', 'Cancellation Request - Base', 'ISO20022_BASE', 'stg_iso20022_camt056', 'ISO 20022 camt.056 base message type', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- ============================================================================
-- PHASE 2: Create New Payment System Format Entries
-- ============================================================================

-- ----------------------------------------------------------------------------
-- TARGET2 (EU RTGS) - pacs.008, pacs.009, pacs.004, pacs.002
-- ----------------------------------------------------------------------------
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES
    ('TARGET2_pacs008', 'TARGET2 Customer Credit Transfer', 'EU Regional', 'stg_iso20022_pacs008', 'TARGET2 pacs.008 - FI to FI Customer Credit Transfer', true),
    ('TARGET2_pacs009', 'TARGET2 FI Credit Transfer', 'EU Regional', 'stg_iso20022_pacs009', 'TARGET2 pacs.009 - Financial Institution Credit Transfer', true),
    ('TARGET2_pacs004', 'TARGET2 Payment Return', 'EU Regional', 'stg_iso20022_pacs004', 'TARGET2 pacs.004 - Payment Return', true),
    ('TARGET2_pacs002', 'TARGET2 Payment Status Report', 'EU Regional', 'stg_iso20022_pacs002', 'TARGET2 pacs.002 - Payment Status Report', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- ----------------------------------------------------------------------------
-- CHAPS (UK RTGS) - pacs.008, pacs.009, pacs.004, pacs.002
-- ----------------------------------------------------------------------------
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES
    ('CHAPS_pacs008', 'CHAPS Customer Credit Transfer', 'REGIONAL', 'stg_iso20022_pacs008', 'CHAPS pacs.008 - FI to FI Customer Credit Transfer', true),
    ('CHAPS_pacs009', 'CHAPS FI Credit Transfer', 'REGIONAL', 'stg_iso20022_pacs009', 'CHAPS pacs.009 - Financial Institution Credit Transfer', true),
    ('CHAPS_pacs004', 'CHAPS Payment Return', 'REGIONAL', 'stg_iso20022_pacs004', 'CHAPS pacs.004 - Payment Return', true),
    ('CHAPS_pacs002', 'CHAPS Payment Status Report', 'REGIONAL', 'stg_iso20022_pacs002', 'CHAPS pacs.002 - Payment Status Report', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- ----------------------------------------------------------------------------
-- FPS (UK Faster Payments) - pacs.008, pacs.002
-- ----------------------------------------------------------------------------
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES
    ('FPS_pacs008', 'FPS Credit Transfer', 'REGIONAL', 'stg_iso20022_pacs008', 'FPS pacs.008 - Faster Payment Credit Transfer', true),
    ('FPS_pacs002', 'FPS Payment Status Report', 'REGIONAL', 'stg_iso20022_pacs002', 'FPS pacs.002 - Payment Status Report', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- ----------------------------------------------------------------------------
-- SEPA (EU Payments) - pain.001, pacs.008, pain.008, pacs.002
-- ----------------------------------------------------------------------------
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES
    ('SEPA_pain001', 'SEPA Credit Transfer Initiation', 'EU Regional', 'stg_iso20022_pain001', 'SEPA pain.001 - Customer Credit Transfer Initiation', true),
    ('SEPA_pacs008', 'SEPA Interbank Credit Transfer', 'EU Regional', 'stg_iso20022_pacs008', 'SEPA pacs.008 - Interbank Credit Transfer', true),
    ('SEPA_pain008', 'SEPA Direct Debit Initiation', 'EU Regional', 'stg_iso20022_pain008', 'SEPA pain.008 - Customer Direct Debit Initiation', true),
    ('SEPA_pacs002', 'SEPA Payment Status Report', 'EU Regional', 'stg_iso20022_pacs002', 'SEPA pacs.002 - Payment Status Report', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- ----------------------------------------------------------------------------
-- SEPA_INST (SEPA Instant) - pacs.008, pacs.002
-- ----------------------------------------------------------------------------
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES
    ('SEPA_INST_pacs008', 'SEPA Instant Credit Transfer', 'EU Regional', 'stg_iso20022_pacs008', 'SEPA Instant pacs.008 - Instant Credit Transfer', true),
    ('SEPA_INST_pacs002', 'SEPA Instant Status Report', 'EU Regional', 'stg_iso20022_pacs002', 'SEPA Instant pacs.002 - Payment Status Report', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- ----------------------------------------------------------------------------
-- FEDNOW (US Instant) - pacs.008, pacs.009, pacs.004, pacs.002
-- ----------------------------------------------------------------------------
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES
    ('FEDNOW_pacs008', 'FedNow Customer Credit Transfer', 'US Regional', 'stg_iso20022_pacs008', 'FedNow pacs.008 - Customer Credit Transfer', true),
    ('FEDNOW_pacs009', 'FedNow FI Credit Transfer', 'US Regional', 'stg_iso20022_pacs009', 'FedNow pacs.009 - Financial Institution Credit Transfer', true),
    ('FEDNOW_pacs004', 'FedNow Payment Return', 'US Regional', 'stg_iso20022_pacs004', 'FedNow pacs.004 - Payment Return', true),
    ('FEDNOW_pacs002', 'FedNow Payment Status Report', 'US Regional', 'stg_iso20022_pacs002', 'FedNow pacs.002 - Payment Status Report', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- ----------------------------------------------------------------------------
-- RTP (US TCH Real-Time) - pacs.008, pacs.002
-- ----------------------------------------------------------------------------
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES
    ('RTP_pacs008', 'RTP Credit Transfer', 'US Regional', 'stg_iso20022_pacs008', 'RTP pacs.008 - Real-Time Payment Credit Transfer', true),
    ('RTP_pacs002', 'RTP Payment Status Report', 'US Regional', 'stg_iso20022_pacs002', 'RTP pacs.002 - Payment Status Report', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- ----------------------------------------------------------------------------
-- NPP (Australia) - pacs.008, pacs.004, pacs.002
-- ----------------------------------------------------------------------------
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES
    ('NPP_pacs008', 'NPP Credit Transfer', 'REGIONAL', 'stg_iso20022_pacs008', 'NPP pacs.008 - New Payments Platform Credit Transfer', true),
    ('NPP_pacs004', 'NPP Payment Return', 'REGIONAL', 'stg_iso20022_pacs004', 'NPP pacs.004 - Payment Return', true),
    ('NPP_pacs002', 'NPP Payment Status Report', 'REGIONAL', 'stg_iso20022_pacs002', 'NPP pacs.002 - Payment Status Report', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- ----------------------------------------------------------------------------
-- MEPS_PLUS (Singapore) - pacs.008, pacs.009, pacs.002
-- ----------------------------------------------------------------------------
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES
    ('MEPS_PLUS_pacs008', 'MEPS+ Customer Credit Transfer', 'REGIONAL', 'stg_iso20022_pacs008', 'MEPS+ pacs.008 - Customer Credit Transfer', true),
    ('MEPS_PLUS_pacs009', 'MEPS+ FI Credit Transfer', 'REGIONAL', 'stg_iso20022_pacs009', 'MEPS+ pacs.009 - Financial Institution Credit Transfer', true),
    ('MEPS_PLUS_pacs002', 'MEPS+ Payment Status Report', 'REGIONAL', 'stg_iso20022_pacs002', 'MEPS+ pacs.002 - Payment Status Report', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- ----------------------------------------------------------------------------
-- RTGS_HK (Hong Kong CHATS) - pacs.008, pacs.009, pacs.002
-- ----------------------------------------------------------------------------
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES
    ('RTGS_HK_pacs008', 'RTGS HK Customer Credit Transfer', 'REGIONAL', 'stg_iso20022_pacs008', 'Hong Kong CHATS pacs.008 - Customer Credit Transfer', true),
    ('RTGS_HK_pacs009', 'RTGS HK FI Credit Transfer', 'REGIONAL', 'stg_iso20022_pacs009', 'Hong Kong CHATS pacs.009 - FI Credit Transfer', true),
    ('RTGS_HK_pacs002', 'RTGS HK Payment Status Report', 'REGIONAL', 'stg_iso20022_pacs002', 'Hong Kong CHATS pacs.002 - Payment Status Report', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- ----------------------------------------------------------------------------
-- UAEFTS (UAE) - pacs.008, pacs.009, pacs.002
-- ----------------------------------------------------------------------------
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES
    ('UAEFTS_pacs008', 'UAEFTS Customer Credit Transfer', 'REGIONAL', 'stg_iso20022_pacs008', 'UAE FTS pacs.008 - Customer Credit Transfer', true),
    ('UAEFTS_pacs009', 'UAEFTS FI Credit Transfer', 'REGIONAL', 'stg_iso20022_pacs009', 'UAE FTS pacs.009 - FI Credit Transfer', true),
    ('UAEFTS_pacs002', 'UAEFTS Payment Status Report', 'REGIONAL', 'stg_iso20022_pacs002', 'UAE FTS pacs.002 - Payment Status Report', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- ----------------------------------------------------------------------------
-- INSTAPAY (Philippines) - pacs.008, pacs.009, pacs.002
-- ----------------------------------------------------------------------------
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES
    ('INSTAPAY_pacs008', 'InstaPay Customer Credit Transfer', 'REGIONAL', 'stg_iso20022_pacs008', 'InstaPay pacs.008 - Customer Credit Transfer', true),
    ('INSTAPAY_pacs009', 'InstaPay FI Credit Transfer', 'REGIONAL', 'stg_iso20022_pacs009', 'InstaPay pacs.009 - FI Credit Transfer', true),
    ('INSTAPAY_pacs002', 'InstaPay Payment Status Report', 'REGIONAL', 'stg_iso20022_pacs002', 'InstaPay pacs.002 - Payment Status Report', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- ----------------------------------------------------------------------------
-- CHIPS (US) - pacs.008, pacs.009, pacs.002
-- ----------------------------------------------------------------------------
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES
    ('CHIPS_pacs008', 'CHIPS Customer Credit Transfer', 'US Regional', 'stg_iso20022_pacs008', 'CHIPS pacs.008 - Customer Credit Transfer', true),
    ('CHIPS_pacs009', 'CHIPS FI Credit Transfer', 'US Regional', 'stg_iso20022_pacs009', 'CHIPS pacs.009 - FI Credit Transfer', true),
    ('CHIPS_pacs002', 'CHIPS Payment Status Report', 'US Regional', 'stg_iso20022_pacs002', 'CHIPS pacs.002 - Payment Status Report', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- ----------------------------------------------------------------------------
-- FEDWIRE (US) - pacs.008, pacs.009, pacs.004, pacs.002
-- ----------------------------------------------------------------------------
INSERT INTO mapping.message_formats (format_id, format_name, format_category, silver_table, description, is_active)
VALUES
    ('FEDWIRE_pacs008', 'Fedwire Customer Credit Transfer', 'US Regional', 'stg_iso20022_pacs008', 'Fedwire pacs.008 - Customer Credit Transfer', true),
    ('FEDWIRE_pacs009', 'Fedwire FI Credit Transfer', 'US Regional', 'stg_iso20022_pacs009', 'Fedwire pacs.009 - FI Credit Transfer', true),
    ('FEDWIRE_pacs004', 'Fedwire Payment Return', 'US Regional', 'stg_iso20022_pacs004', 'Fedwire pacs.004 - Payment Return', true),
    ('FEDWIRE_pacs002', 'Fedwire Payment Status Report', 'US Regional', 'stg_iso20022_pacs002', 'Fedwire pacs.002 - Payment Status Report', true)
ON CONFLICT (format_id) DO UPDATE SET is_active = true, silver_table = EXCLUDED.silver_table;

-- ============================================================================
-- PHASE 3: Create Inheritance Relationships
-- ============================================================================

-- Clear existing inheritance for formats we're replacing
DELETE FROM mapping.format_inheritance
WHERE child_format_id IN (
    'TARGET2', 'CHAPS', 'FPS', 'SEPA', 'SEPA_INST', 'FEDNOW', 'RTP',
    'NPP', 'MEPS_PLUS', 'RTGS_HK', 'UAEFTS', 'INSTAPAY', 'CHIPS', 'FEDWIRE'
);

-- TARGET2
INSERT INTO mapping.format_inheritance (child_format_id, parent_format_id, inheritance_type, is_active)
VALUES
    ('TARGET2_pacs008', 'pacs.008.base', 'COMPLETE', true),
    ('TARGET2_pacs009', 'pacs.009.base', 'COMPLETE', true),
    ('TARGET2_pacs004', 'pacs.004.base', 'COMPLETE', true),
    ('TARGET2_pacs002', 'pacs.002.base', 'COMPLETE', true)
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET is_active = true;

-- CHAPS
INSERT INTO mapping.format_inheritance (child_format_id, parent_format_id, inheritance_type, is_active)
VALUES
    ('CHAPS_pacs008', 'pacs.008.base', 'COMPLETE', true),
    ('CHAPS_pacs009', 'pacs.009.base', 'COMPLETE', true),
    ('CHAPS_pacs004', 'pacs.004.base', 'COMPLETE', true),
    ('CHAPS_pacs002', 'pacs.002.base', 'COMPLETE', true)
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET is_active = true;

-- FPS
INSERT INTO mapping.format_inheritance (child_format_id, parent_format_id, inheritance_type, is_active)
VALUES
    ('FPS_pacs008', 'pacs.008.base', 'COMPLETE', true),
    ('FPS_pacs002', 'pacs.002.base', 'COMPLETE', true)
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET is_active = true;

-- SEPA
INSERT INTO mapping.format_inheritance (child_format_id, parent_format_id, inheritance_type, is_active)
VALUES
    ('SEPA_pain001', 'pain.001.base', 'COMPLETE', true),
    ('SEPA_pacs008', 'pacs.008.base', 'COMPLETE', true),
    ('SEPA_pain008', 'pain.008.base', 'COMPLETE', true),
    ('SEPA_pacs002', 'pacs.002.base', 'COMPLETE', true)
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET is_active = true;

-- SEPA_INST
INSERT INTO mapping.format_inheritance (child_format_id, parent_format_id, inheritance_type, is_active)
VALUES
    ('SEPA_INST_pacs008', 'pacs.008.base', 'COMPLETE', true),
    ('SEPA_INST_pacs002', 'pacs.002.base', 'COMPLETE', true)
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET is_active = true;

-- FEDNOW
INSERT INTO mapping.format_inheritance (child_format_id, parent_format_id, inheritance_type, is_active)
VALUES
    ('FEDNOW_pacs008', 'pacs.008.base', 'COMPLETE', true),
    ('FEDNOW_pacs009', 'pacs.009.base', 'COMPLETE', true),
    ('FEDNOW_pacs004', 'pacs.004.base', 'COMPLETE', true),
    ('FEDNOW_pacs002', 'pacs.002.base', 'COMPLETE', true)
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET is_active = true;

-- RTP
INSERT INTO mapping.format_inheritance (child_format_id, parent_format_id, inheritance_type, is_active)
VALUES
    ('RTP_pacs008', 'pacs.008.base', 'COMPLETE', true),
    ('RTP_pacs002', 'pacs.002.base', 'COMPLETE', true)
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET is_active = true;

-- NPP
INSERT INTO mapping.format_inheritance (child_format_id, parent_format_id, inheritance_type, is_active)
VALUES
    ('NPP_pacs008', 'pacs.008.base', 'COMPLETE', true),
    ('NPP_pacs004', 'pacs.004.base', 'COMPLETE', true),
    ('NPP_pacs002', 'pacs.002.base', 'COMPLETE', true)
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET is_active = true;

-- MEPS_PLUS
INSERT INTO mapping.format_inheritance (child_format_id, parent_format_id, inheritance_type, is_active)
VALUES
    ('MEPS_PLUS_pacs008', 'pacs.008.base', 'COMPLETE', true),
    ('MEPS_PLUS_pacs009', 'pacs.009.base', 'COMPLETE', true),
    ('MEPS_PLUS_pacs002', 'pacs.002.base', 'COMPLETE', true)
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET is_active = true;

-- RTGS_HK
INSERT INTO mapping.format_inheritance (child_format_id, parent_format_id, inheritance_type, is_active)
VALUES
    ('RTGS_HK_pacs008', 'pacs.008.base', 'COMPLETE', true),
    ('RTGS_HK_pacs009', 'pacs.009.base', 'COMPLETE', true),
    ('RTGS_HK_pacs002', 'pacs.002.base', 'COMPLETE', true)
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET is_active = true;

-- UAEFTS
INSERT INTO mapping.format_inheritance (child_format_id, parent_format_id, inheritance_type, is_active)
VALUES
    ('UAEFTS_pacs008', 'pacs.008.base', 'COMPLETE', true),
    ('UAEFTS_pacs009', 'pacs.009.base', 'COMPLETE', true),
    ('UAEFTS_pacs002', 'pacs.002.base', 'COMPLETE', true)
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET is_active = true;

-- INSTAPAY
INSERT INTO mapping.format_inheritance (child_format_id, parent_format_id, inheritance_type, is_active)
VALUES
    ('INSTAPAY_pacs008', 'pacs.008.base', 'COMPLETE', true),
    ('INSTAPAY_pacs009', 'pacs.009.base', 'COMPLETE', true),
    ('INSTAPAY_pacs002', 'pacs.002.base', 'COMPLETE', true)
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET is_active = true;

-- CHIPS
INSERT INTO mapping.format_inheritance (child_format_id, parent_format_id, inheritance_type, is_active)
VALUES
    ('CHIPS_pacs008', 'pacs.008.base', 'COMPLETE', true),
    ('CHIPS_pacs009', 'pacs.009.base', 'COMPLETE', true),
    ('CHIPS_pacs002', 'pacs.002.base', 'COMPLETE', true)
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET is_active = true;

-- FEDWIRE
INSERT INTO mapping.format_inheritance (child_format_id, parent_format_id, inheritance_type, is_active)
VALUES
    ('FEDWIRE_pacs008', 'pacs.008.base', 'COMPLETE', true),
    ('FEDWIRE_pacs009', 'pacs.009.base', 'COMPLETE', true),
    ('FEDWIRE_pacs004', 'pacs.004.base', 'COMPLETE', true),
    ('FEDWIRE_pacs002', 'pacs.002.base', 'COMPLETE', true)
ON CONFLICT (child_format_id, parent_format_id) DO UPDATE SET is_active = true;

-- ============================================================================
-- PHASE 4: Deactivate Old Format Entries (ISO 20022 adopters only)
-- ============================================================================

-- Deactivate old formats that are now split by message type
UPDATE mapping.message_formats
SET is_active = false
WHERE format_id IN (
    'TARGET2',   -- Now TARGET2_pacs008, TARGET2_pacs009, etc.
    'CHAPS',     -- Now CHAPS_pacs008, CHAPS_pacs009, etc.
    'FPS',       -- Now FPS_pacs008
    'SEPA',      -- Now SEPA_pain001, SEPA_pacs008, etc.
    'SEPA_INST', -- Now SEPA_INST_pacs008
    'FEDNOW',    -- Now FEDNOW_pacs008, FEDNOW_pacs009, etc.
    'RTP',       -- Now RTP_pacs008
    'NPP',       -- Now NPP_pacs008
    'MEPS_PLUS', -- Now MEPS_PLUS_pacs008, MEPS_PLUS_pacs009
    'RTGS_HK',   -- Now RTGS_HK_pacs008, RTGS_HK_pacs009
    'UAEFTS',    -- Now UAEFTS_pacs008, UAEFTS_pacs009
    'INSTAPAY',  -- Now INSTAPAY_pacs008, INSTAPAY_pacs009
    'CHIPS',     -- Now CHIPS_pacs008, CHIPS_pacs009
    'FEDWIRE'    -- Now FEDWIRE_pacs008, FEDWIRE_pacs009
);

-- Keep these formats active (proprietary, not ISO 20022):
-- ACH, BACS, PIX, UPI, PROMPTPAY, PAYNOW, CNAPS, BOJNET, KFTC, SARIE
-- MT103, MT202, MT940
-- camt.053 (statement format - different use case)

COMMIT;

-- ============================================================================
-- PHASE 5: Summary Report
-- ============================================================================

-- Show all new format entries created
SELECT 'NEW FORMATS CREATED:' as info;
SELECT format_id, format_category, silver_table, is_active
FROM mapping.message_formats
WHERE format_id LIKE '%_pacs%' OR format_id LIKE '%_pain%'
ORDER BY format_id;

-- Show inheritance relationships
SELECT 'INHERITANCE RELATIONSHIPS:' as info;
SELECT child_format_id, parent_format_id, inheritance_type
FROM mapping.format_inheritance
WHERE is_active = true
  AND (child_format_id LIKE '%_pacs%' OR child_format_id LIKE '%_pain%')
ORDER BY child_format_id;

-- Show deactivated formats
SELECT 'DEACTIVATED FORMATS:' as info;
SELECT format_id, is_active
FROM mapping.message_formats
WHERE is_active = false
  AND format_id IN ('TARGET2', 'CHAPS', 'FPS', 'SEPA', 'SEPA_INST', 'FEDNOW', 'RTP',
                    'NPP', 'MEPS_PLUS', 'RTGS_HK', 'UAEFTS', 'INSTAPAY', 'CHIPS', 'FEDWIRE');

-- Show base formats with mapping counts
SELECT 'BASE FORMAT MAPPING COUNTS:' as info;
SELECT
    mf.format_id,
    (SELECT COUNT(*) FROM mapping.silver_field_mappings WHERE format_id = mf.format_id AND is_active = true) as silver_mappings,
    (SELECT COUNT(*) FROM mapping.gold_field_mappings WHERE format_id = mf.format_id AND is_active = true) as gold_mappings
FROM mapping.message_formats mf
WHERE mf.format_id LIKE '%.base'
ORDER BY mf.format_id;
