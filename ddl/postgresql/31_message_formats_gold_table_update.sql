-- GPS CDM - Update message_formats with Gold Table References
-- ============================================================
-- Adds gold_table column and updates all formats to point to appropriate Gold table
--
-- Version: 1.0
-- Date: 2026-01-08

-- Add gold_table column if not exists
ALTER TABLE mapping.message_formats
ADD COLUMN IF NOT EXISTS gold_table VARCHAR(100);

-- Add comment
COMMENT ON COLUMN mapping.message_formats.gold_table IS 'Target Gold table for this message format';


-- =====================================================
-- Update Base Formats with Gold Table References
-- =====================================================

-- pain.001 base → cdm_pain_customer_credit_transfer_initiation
UPDATE mapping.message_formats
SET gold_table = 'cdm_pain_customer_credit_transfer_initiation'
WHERE format_id = 'pain.001.base';

UPDATE mapping.message_formats
SET gold_table = 'cdm_pain_customer_credit_transfer_initiation'
WHERE format_id = 'pain.001';

-- pain.002 → cdm_pain_customer_payment_status_report
UPDATE mapping.message_formats
SET gold_table = 'cdm_pain_customer_payment_status_report'
WHERE format_id = 'pain.002';

-- pain.008 base → cdm_pain_customer_direct_debit_initiation
UPDATE mapping.message_formats
SET gold_table = 'cdm_pain_customer_direct_debit_initiation'
WHERE format_id = 'pain.008.base';

UPDATE mapping.message_formats
SET gold_table = 'cdm_pain_customer_direct_debit_initiation'
WHERE format_id = 'pain.008';

-- pacs.002 base → cdm_pacs_fi_payment_status_report
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_payment_status_report'
WHERE format_id = 'pacs.002.base';

UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_payment_status_report'
WHERE format_id = 'pacs.002';

-- pacs.003 → cdm_pacs_fi_direct_debit
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_direct_debit'
WHERE format_id = 'pacs.003';

-- pacs.004 base → cdm_pacs_payment_return
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_payment_return'
WHERE format_id = 'pacs.004.base';

UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_payment_return'
WHERE format_id = 'pacs.004';

-- pacs.008 base → cdm_pacs_fi_customer_credit_transfer
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_customer_credit_transfer'
WHERE format_id = 'pacs.008.base';

UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_customer_credit_transfer'
WHERE format_id = 'pacs.008';

-- pacs.009 base → cdm_pacs_fi_credit_transfer
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_credit_transfer'
WHERE format_id = 'pacs.009.base';

UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_credit_transfer'
WHERE format_id = 'pacs.009';

-- camt.052 → cdm_camt_bank_to_customer_account_report
UPDATE mapping.message_formats
SET gold_table = 'cdm_camt_bank_to_customer_account_report'
WHERE format_id = 'camt.052';

-- camt.053 base → cdm_camt_bank_to_customer_statement
UPDATE mapping.message_formats
SET gold_table = 'cdm_camt_bank_to_customer_statement'
WHERE format_id = 'camt.053.base';

UPDATE mapping.message_formats
SET gold_table = 'cdm_camt_bank_to_customer_statement'
WHERE format_id = 'camt.053';

-- camt.054 → cdm_camt_bank_to_customer_debit_credit_notification
UPDATE mapping.message_formats
SET gold_table = 'cdm_camt_bank_to_customer_debit_credit_notification'
WHERE format_id = 'camt.054';

-- camt.056 base → cdm_camt_fi_payment_cancellation_request
UPDATE mapping.message_formats
SET gold_table = 'cdm_camt_fi_payment_cancellation_request'
WHERE format_id = 'camt.056.base';


-- =====================================================
-- Update Regional/Composite Formats (inherit from base)
-- =====================================================

-- All *_pacs008 formats → cdm_pacs_fi_customer_credit_transfer
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_customer_credit_transfer'
WHERE format_id LIKE '%_pacs008'
   OR format_id IN ('FEDWIRE_pacs008', 'CHIPS_pacs008', 'CHAPS_pacs008', 'FPS_pacs008',
                    'FEDNOW_pacs008', 'RTP_pacs008', 'NPP_pacs008', 'SEPA_pacs008',
                    'SEPA_INST_pacs008', 'MEPS_PLUS_pacs008', 'RTGS_HK_pacs008',
                    'UAEFTS_pacs008', 'INSTAPAY_pacs008', 'TARGET2_pacs008');

-- All *_pacs009 formats → cdm_pacs_fi_credit_transfer
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_credit_transfer'
WHERE format_id LIKE '%_pacs009'
   OR format_id IN ('TARGET2_pacs009', 'CHAPS_pacs009', 'CHIPS_pacs009', 'FEDNOW_pacs009',
                    'FEDWIRE_pacs009', 'INSTAPAY_pacs009', 'MEPS_PLUS_pacs009',
                    'RTGS_HK_pacs009', 'UAEFTS_pacs009');

-- All *_pacs002 formats → cdm_pacs_fi_payment_status_report
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_payment_status_report'
WHERE format_id LIKE '%_pacs002'
   OR format_id IN ('FEDWIRE_pacs002', 'CHIPS_pacs002', 'CHAPS_pacs002', 'FPS_pacs002',
                    'FEDNOW_pacs002', 'RTP_pacs002', 'NPP_pacs002', 'SEPA_pacs002',
                    'SEPA_INST_pacs002', 'MEPS_PLUS_pacs002', 'RTGS_HK_pacs002',
                    'UAEFTS_pacs002', 'INSTAPAY_pacs002', 'TARGET2_pacs002');

-- All *_pacs004 formats → cdm_pacs_payment_return
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_payment_return'
WHERE format_id LIKE '%_pacs004'
   OR format_id IN ('FEDWIRE_pacs004', 'CHAPS_pacs004', 'FEDNOW_pacs004',
                    'NPP_pacs004', 'TARGET2_pacs004');

-- All *_pain001 formats → cdm_pain_customer_credit_transfer_initiation
UPDATE mapping.message_formats
SET gold_table = 'cdm_pain_customer_credit_transfer_initiation'
WHERE format_id LIKE '%_pain001'
   OR format_id = 'SEPA_pain001';

-- All *_pain008 formats → cdm_pain_customer_direct_debit_initiation
UPDATE mapping.message_formats
SET gold_table = 'cdm_pain_customer_direct_debit_initiation'
WHERE format_id LIKE '%_pain008'
   OR format_id = 'SEPA_pain008';


-- =====================================================
-- Update Proprietary Formats to Map to ISO Equivalents
-- =====================================================

-- SWIFT MT formats
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_customer_credit_transfer'
WHERE format_id IN ('MT103', 'MT103STP');

UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_credit_transfer'
WHERE format_id IN ('MT202', 'MT202COV');

UPDATE mapping.message_formats
SET gold_table = 'cdm_camt_bank_to_customer_statement'
WHERE format_id = 'MT940';

UPDATE mapping.message_formats
SET gold_table = 'cdm_camt_bank_to_customer_account_report'
WHERE format_id = 'MT942';

UPDATE mapping.message_formats
SET gold_table = 'cdm_camt_bank_to_customer_debit_credit_notification'
WHERE format_id IN ('MT900', 'MT910');

-- US Regional formats
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_customer_credit_transfer'
WHERE format_id IN ('FEDWIRE', 'CHIPS', 'ACH', 'FEDNOW', 'RTP');

-- UK Regional formats
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_customer_credit_transfer'
WHERE format_id IN ('CHAPS', 'FPS', 'BACS');

-- EU Regional formats
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_customer_credit_transfer'
WHERE format_id IN ('SEPA', 'TARGET2')
  AND gold_table IS NULL;  -- Don't override if already set

-- Asia-Pacific formats
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_customer_credit_transfer'
WHERE format_id IN ('NPP', 'MEPS_PLUS', 'RTGS_HK', 'INSTAPAY', 'CNAPS', 'BOJNET', 'KFTC');

-- Middle East formats
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_customer_credit_transfer'
WHERE format_id IN ('UAEFTS', 'SARIE');

-- Latin America & Others
UPDATE mapping.message_formats
SET gold_table = 'cdm_pacs_fi_customer_credit_transfer'
WHERE format_id IN ('PIX', 'UPI', 'PROMPTPAY', 'PAYNOW');


-- =====================================================
-- Verify Updates
-- =====================================================
-- SELECT format_id, format_category, silver_table, gold_table
-- FROM mapping.message_formats
-- WHERE gold_table IS NOT NULL
-- ORDER BY gold_table, format_id;
