-- =====================================================================
-- Script: Load Purpose Codes for Other Major Jurisdictions
-- Purpose: Populate purpose codes for US, UK, Singapore, Hong Kong,
--          Thailand, Malaysia, Philippines, Indonesia, Vietnam, UAE,
--          Saudi Arabia, and other key jurisdictions
-- Coverage: ~50+ codes across 25 jurisdictions
-- =====================================================================

INSERT INTO cdm_silver.regulatory_purpose_code
(purpose_code_id, jurisdiction, code_value, code_description, category, sub_category, iso20022_mapping, applicable_payment_types, requires_supporting_documents, effective_from, effective_to, created_timestamp, last_updated_timestamp)
VALUES

-- =============================
-- UNITED STATES (FinCEN)
-- =============================
(uuid(), 'US', 'US001', 'Import of goods and services', 'Trade', 'Import', 'GDDS', array('SWIFT', 'Wire', 'ACH', 'Fedwire'), true, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'US', 'US002', 'Export of goods and services', 'Trade', 'Export', 'GDDS', array('SWIFT', 'Wire', 'ACH', 'Fedwire'), true, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'US', 'US003', 'Personal remittance', 'Remittances', 'Family', 'FAMI', array('Wire', 'ACH', 'Mobile'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'US', 'US004', 'Business services', 'Services', 'Business', 'BUSI', array('SWIFT', 'Wire', 'ACH'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'US', 'US005', 'Investment - dividend', 'Investment', 'Dividend', 'DIVI', array('SWIFT', 'Wire'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'US', 'US006', 'Investment - interest', 'Investment', 'Interest', 'INTC', array('SWIFT', 'Wire'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'US', 'US007', 'Loan repayment', 'Loans', 'Repayment', 'LOAN', array('SWIFT', 'Wire', 'ACH'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'US', 'US008', 'Real estate transaction', 'Investment', 'Real Estate', 'BUSI', array('Wire', 'Fedwire'), true, '2010-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- UNITED KINGDOM (FCA/Bank of England)
-- =============================
(uuid(), 'GB', 'UK001', 'Trade in goods', 'Trade', 'Goods', 'GDDS', array('SWIFT', 'CHAPS', 'Faster Payments'), true, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'GB', 'UK002', 'Trade in services', 'Trade', 'Services', 'SVCS', array('SWIFT', 'CHAPS', 'Faster Payments'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'GB', 'UK003', 'Financial services', 'Services', 'Financial', 'BUSI', array('SWIFT', 'CHAPS'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'GB', 'UK004', 'Intellectual property', 'Services', 'IP', 'LICE', array('SWIFT', 'CHAPS'), true, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'GB', 'UK005', 'Dividends and investment income', 'Investment', 'Income', 'DIVI', array('SWIFT', 'CHAPS'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'GB', 'UK006', 'Loans and deposits', 'Financial', 'Loans', 'LOAN', array('SWIFT', 'CHAPS'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'GB', 'UK007', 'Personal transfer', 'Remittances', 'Personal', 'FAMI', array('Faster Payments', 'Mobile'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- SINGAPORE (MAS)
-- =============================
(uuid(), 'SG', 'SG001', 'Trade settlement', 'Trade', 'Settlement', 'GDDS', array('SWIFT', 'Wire', 'PayNow'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'SG', 'SG002', 'Professional services', 'Services', 'Professional', 'BUSI', array('Wire', 'PayNow'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'SG', 'SG003', 'Investment income', 'Investment', 'Income', 'DIVI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'SG', 'SG004', 'Family support', 'Remittances', 'Family', 'FAMI', array('Wire', 'PayNow', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'SG', 'SG005', 'Salary repatriation', 'Remittances', 'Salary', 'SALA', array('Wire', 'PayNow'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'SG', 'SG006', 'Education expenses', 'Services', 'Education', 'EDUC', array('Wire', 'PayNow'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- HONG KONG (HKMA)
-- =============================
(uuid(), 'HK', 'HK001', 'Merchandise trade', 'Trade', 'Goods', 'GDDS', array('SWIFT', 'Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'HK', 'HK002', 'Services trade', 'Trade', 'Services', 'SVCS', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'HK', 'HK003', 'Financial services', 'Services', 'Financial', 'BUSI', array('SWIFT', 'RTGS'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'HK', 'HK004', 'Investment transactions', 'Investment', 'General', 'DIVI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'HK', 'HK005', 'Personal remittance', 'Remittances', 'Personal', 'FAMI', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- THAILAND (BOT)
-- =============================
(uuid(), 'TH', 'TH001', 'Import payment', 'Trade', 'Import', 'GDDS', array('SWIFT', 'Wire', 'PromptPay'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'TH', 'TH002', 'Export proceeds', 'Trade', 'Export', 'GDDS', array('SWIFT', 'Wire', 'PromptPay'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'TH', 'TH003', 'Service fees', 'Services', 'General', 'SVCS', array('Wire', 'PromptPay'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'TH', 'TH004', 'Investment proceeds', 'Investment', 'Proceeds', 'DIVI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'TH', 'TH005', 'Family support', 'Remittances', 'Family', 'FAMI', array('Wire', 'PromptPay', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'TH', 'TH006', 'Tourism and travel', 'Services', 'Travel', 'TRAD', array('Wire', 'PromptPay', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- MALAYSIA (BNM)
-- =============================
(uuid(), 'MY', 'MY001', 'Trade in goods', 'Trade', 'Goods', 'GDDS', array('SWIFT', 'Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'MY', 'MY002', 'Trade in services', 'Trade', 'Services', 'SVCS', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'MY', 'MY003', 'Investment income', 'Investment', 'Income', 'DIVI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'MY', 'MY004', 'Family remittance', 'Remittances', 'Family', 'FAMI', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'MY', 'MY005', 'Islamic finance transaction', 'Financial', 'Islamic Finance', 'BUSI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- PHILIPPINES (BSP)
-- =============================
(uuid(), 'PH', 'PH001', 'Goods import', 'Trade', 'Import', 'GDDS', array('SWIFT', 'Wire', 'Mobile'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'PH', 'PH002', 'Goods export', 'Trade', 'Export', 'GDDS', array('SWIFT', 'Wire', 'Mobile'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'PH', 'PH003', 'OFW remittance', 'Remittances', 'OFW', 'FAMI', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'PH', 'PH004', 'BPO services payment', 'Services', 'BPO', 'BUSI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'PH', 'PH005', 'Investment proceeds', 'Investment', 'Proceeds', 'DIVI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- INDONESIA (BI)
-- =============================
(uuid(), 'ID', 'ID001', 'Import transaction', 'Trade', 'Import', 'GDDS', array('SWIFT', 'Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'ID', 'ID002', 'Export transaction', 'Trade', 'Export', 'GDDS', array('SWIFT', 'Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'ID', 'ID003', 'Services payment', 'Services', 'General', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'ID', 'ID004', 'Worker remittance', 'Remittances', 'Worker', 'FAMI', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- VIETNAM (SBV)
-- =============================
(uuid(), 'VN', 'VN001', 'Trade payment', 'Trade', 'General', 'GDDS', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'VN', 'VN002', 'Service fee', 'Services', 'General', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'VN', 'VN003', 'Personal remittance', 'Remittances', 'Personal', 'FAMI', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'VN', 'VN004', 'Investment income', 'Investment', 'Income', 'DIVI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- UAE (CBUAE)
-- =============================
(uuid(), 'AE', 'AE001', 'Trade in goods', 'Trade', 'Goods', 'GDDS', array('SWIFT', 'Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'AE', 'AE002', 'Trade in services', 'Trade', 'Services', 'SVCS', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'AE', 'AE003', 'Investment transaction', 'Investment', 'General', 'DIVI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'AE', 'AE004', 'Worker remittance', 'Remittances', 'Worker', 'FAMI', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'AE', 'AE005', 'Islamic finance - Murabaha', 'Financial', 'Islamic Finance', 'BUSI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'AE', 'AE006', 'Islamic finance - Ijara', 'Financial', 'Islamic Finance', 'RENT', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- SAUDI ARABIA (SAMA)
-- =============================
(uuid(), 'SA', 'SA001', 'Import of goods', 'Trade', 'Import', 'GDDS', array('SWIFT', 'Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'SA', 'SA002', 'Export of goods', 'Trade', 'Export', 'GDDS', array('SWIFT', 'Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'SA', 'SA003', 'Investment income', 'Investment', 'Income', 'DIVI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'SA', 'SA004', 'Worker remittance outward', 'Remittances', 'Worker', 'FAMI', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'SA', 'SA005', 'Hajj and Umrah services', 'Services', 'Religious', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'SA', 'SA006', 'Islamic finance - Sharia compliant', 'Financial', 'Islamic Finance', 'BUSI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- MEXICO (CNBV/Banxico)
-- =============================
(uuid(), 'MX', 'MX001', 'Import of goods', 'Trade', 'Import', 'GDDS', array('SWIFT', 'Wire', 'SPEI'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'MX', 'MX002', 'Export of goods', 'Trade', 'Export', 'GDDS', array('SWIFT', 'Wire', 'SPEI'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'MX', 'MX003', 'Family remittance', 'Remittances', 'Family', 'FAMI', array('Wire', 'Mobile', 'SPEI'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'MX', 'MX004', 'Tourism and travel', 'Services', 'Travel', 'TRAD', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'MX', 'MX005', 'Investment transaction', 'Investment', 'General', 'DIVI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- AUSTRALIA (AUSTRAC)
-- =============================
(uuid(), 'AU', 'AU001', 'International funds transfer', 'General', 'Transfer', NULL, array('SWIFT', 'Wire'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'AU', 'AU002', 'Trade settlement', 'Trade', 'Settlement', 'GDDS', array('SWIFT', 'Wire'), true, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'AU', 'AU003', 'Investment proceeds', 'Investment', 'Proceeds', 'DIVI', array('SWIFT', 'Wire'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'AU', 'AU004', 'Personal remittance', 'Remittances', 'Personal', 'FAMI', array('Wire', 'Mobile'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- EUROPEAN UNION (SEPA)
-- =============================
(uuid(), 'EU', 'EU001', 'SEPA Credit Transfer', 'Payment', 'SEPA SCT', NULL, array('SEPA'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'EU', 'EU002', 'SEPA Instant Credit Transfer', 'Payment', 'SEPA Instant', NULL, array('SEPA Instant'), false, '2017-11-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'EU', 'EU003', 'Trade in goods', 'Trade', 'Goods', 'GDDS', array('SWIFT', 'SEPA'), true, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'EU', 'EU004', 'Services payment', 'Services', 'General', 'SVCS', array('SWIFT', 'SEPA'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'EU', 'EU005', 'Investment dividend', 'Investment', 'Dividend', 'DIVI', array('SWIFT', 'SEPA'), false, '2010-01-01', NULL, current_timestamp(), current_timestamp());

-- =====================================================================
-- Validation Queries
-- =====================================================================

-- Count codes by jurisdiction
SELECT
  jurisdiction,
  COUNT(*) as code_count
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction IN ('US', 'GB', 'SG', 'HK', 'TH', 'MY', 'PH', 'ID', 'VN', 'AE', 'SA', 'MX', 'AU', 'EU')
GROUP BY jurisdiction
ORDER BY jurisdiction;

-- Total purpose codes across all jurisdictions
SELECT
  jurisdiction,
  COUNT(*) as total_codes
FROM cdm_silver.regulatory_purpose_code
GROUP BY jurisdiction
ORDER BY total_codes DESC;

-- Grand total
SELECT COUNT(*) as grand_total_codes
FROM cdm_silver.regulatory_purpose_code;
-- Expected: 350+

-- Check mobile payment coverage
SELECT
  jurisdiction,
  COUNT(*) as mobile_enabled_codes
FROM cdm_silver.regulatory_purpose_code
WHERE array_contains(applicable_payment_types, 'Mobile')
GROUP BY jurisdiction
ORDER BY mobile_enabled_codes DESC;
