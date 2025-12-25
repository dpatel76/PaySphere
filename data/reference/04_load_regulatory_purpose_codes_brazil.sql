-- =====================================================================
-- Script: Load Brazil (BACEN) Regulatory Purpose Codes
-- Purpose: Populate 40 nature codes for PIX and cross-border reporting
-- Regulatory Authority: Banco Central do Brasil (BACEN)
-- Reference: PIX Nature Codes / BACEN Circular 3,691 (2013-2024)
-- =====================================================================

INSERT INTO cdm_silver.regulatory_purpose_code
(purpose_code_id, jurisdiction, code_value, code_description, category, sub_category, iso20022_mapping, applicable_payment_types, requires_supporting_documents, effective_from, effective_to, created_timestamp, last_updated_timestamp)
VALUES

-- =============================
-- CURRENT ACCOUNT (10000-10999)
-- =============================
(uuid(), 'BR', '10101', 'Goods import', 'Current Account', 'Trade in Goods', 'GDDS', array('SWIFT', 'Wire', 'PIX'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10102', 'Goods export', 'Current Account', 'Trade in Goods', 'GDDS', array('SWIFT', 'Wire', 'PIX'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10201', 'International freight', 'Current Account', 'Transportation', 'SVCS', array('SWIFT', 'Wire', 'PIX'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10202', 'Insurance and reinsurance', 'Current Account', 'Insurance', 'INSU', array('SWIFT', 'Wire'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10203', 'International travel', 'Current Account', 'Travel', 'TRAD', array('Wire', 'PIX', 'Mobile'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10204', 'Communications services', 'Current Account', 'Communication', 'SVCS', array('Wire', 'PIX'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10205', 'Construction services', 'Current Account', 'Construction', 'BUSI', array('SWIFT', 'Wire'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10206', 'Financial services', 'Current Account', 'Financial Services', 'BUSI', array('SWIFT', 'Wire'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10207', 'Computer and information services', 'Current Account', 'Technology', 'SVCS', array('Wire', 'PIX'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10208', 'Royalties and license fees', 'Current Account', 'Intellectual Property', 'LICE', array('SWIFT', 'Wire'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10209', 'Professional and consulting services', 'Current Account', 'Professional Services', 'BUSI', array('Wire', 'PIX'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10210', 'Technical and trade-related services', 'Current Account', 'Technical Services', 'BUSI', array('Wire', 'PIX'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10211', 'Operational leasing', 'Current Account', 'Leasing', 'RENT', array('Wire'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10212', 'Audiovisual and related services', 'Current Account', 'Media', 'SVCS', array('Wire', 'PIX'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10213', 'Other business services', 'Current Account', 'Business Services', 'BUSI', array('Wire', 'PIX'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),

-- Investment Income (10300-10399)
(uuid(), 'BR', '10301', 'Direct investment - dividends and profits', 'Current Account', 'Investment Income', 'DIVI', array('SWIFT', 'Wire', 'PIX'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10302', 'Direct investment - interest', 'Current Account', 'Investment Income', 'INTC', array('SWIFT', 'Wire'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10303', 'Portfolio investment - dividends', 'Current Account', 'Investment Income', 'DIVI', array('SWIFT', 'Wire'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10304', 'Portfolio investment - interest', 'Current Account', 'Investment Income', 'INTC', array('SWIFT', 'Wire'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10305', 'Other investment - interest', 'Current Account', 'Investment Income', 'INTC', array('SWIFT', 'Wire'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),

-- Current Transfers (10400-10499)
(uuid(), 'BR', '10401', 'Workers' remittances', 'Current Account', 'Remittances', 'SALA', array('Wire', 'PIX', 'Mobile'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10402', 'Family support and maintenance', 'Current Account', 'Remittances', 'FAMI', array('Wire', 'PIX', 'Mobile'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10403', 'Personal gifts and donations', 'Current Account', 'Remittances', 'CHAR', array('Wire', 'PIX'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10404', 'Educational support', 'Current Account', 'Remittances', 'EDUC', array('Wire', 'PIX'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '10405', 'Medical treatment', 'Current Account', 'Remittances', 'MDCS', array('Wire', 'PIX'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- CAPITAL ACCOUNT (20000-20999)
-- =============================
(uuid(), 'BR', '20101', 'Capital transfers - migrants', 'Capital Account', 'Capital Transfers', 'FAMI', array('Wire', 'PIX'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '20102', 'Debt forgiveness', 'Capital Account', 'Capital Transfers', 'CBFF', array('SWIFT', 'Wire'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '20103', 'Acquisition/disposal of non-financial assets', 'Capital Account', 'Non-financial Assets', 'BUSI', array('SWIFT', 'Wire'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- FINANCIAL ACCOUNT (30000-39999)
-- =============================

-- Direct Investment (30100-30199)
(uuid(), 'BR', '30101', 'Direct investment - equity capital (inward)', 'Financial Account', 'Direct Investment', 'DIVI', array('SWIFT', 'Wire'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '30102', 'Direct investment - equity capital (outward)', 'Financial Account', 'Direct Investment', 'DIVI', array('SWIFT', 'Wire'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '30103', 'Direct investment - reinvestment of earnings', 'Financial Account', 'Direct Investment', 'DIVI', array('Wire'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '30104', 'Direct investment - intercompany debt', 'Financial Account', 'Direct Investment', 'LOAN', array('SWIFT', 'Wire'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),

-- Portfolio Investment (30200-30299)
(uuid(), 'BR', '30201', 'Portfolio investment - equity securities (purchase)', 'Financial Account', 'Portfolio Investment', 'DIVI', array('SWIFT', 'Wire'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '30202', 'Portfolio investment - equity securities (sale)', 'Financial Account', 'Portfolio Investment', 'DIVI', array('SWIFT', 'Wire'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '30203', 'Portfolio investment - debt securities (purchase)', 'Financial Account', 'Portfolio Investment', 'INTC', array('SWIFT', 'Wire'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '30204', 'Portfolio investment - debt securities (sale)', 'Financial Account', 'Portfolio Investment', 'INTC', array('SWIFT', 'Wire'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),

-- Loans and Credits (30300-30399)
(uuid(), 'BR', '30301', 'Trade credits and advances', 'Financial Account', 'Loans', 'LOAN', array('SWIFT', 'Wire'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '30302', 'Financial credits and loans', 'Financial Account', 'Loans', 'LOAN', array('SWIFT', 'Wire'), true, '2013-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '30303', 'Repayment of loans', 'Financial Account', 'Loans', 'LOAN', array('SWIFT', 'Wire', 'PIX'), false, '2013-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- PIX-SPECIFIC (90000-90999)
-- =============================
(uuid(), 'BR', '90001', 'PIX - general transfer', 'PIX', 'General', NULL, array('PIX'), false, '2020-11-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'BR', '90002', 'PIX - salary payment', 'PIX', 'Salary', 'SALA', array('PIX'), false, '2020-11-01', NULL, current_timestamp(), current_timestamp());

-- =====================================================================
-- Validation Queries
-- =====================================================================

-- Count total Brazil codes
SELECT COUNT(*) as total_brazil_codes
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction = 'BR';
-- Expected: 40

-- Count by category
SELECT
  category,
  sub_category,
  COUNT(*) as code_count
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction = 'BR'
GROUP BY category, sub_category
ORDER BY category, sub_category;

-- Check PIX-specific codes
SELECT
  code_value,
  code_description,
  effective_from
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction = 'BR'
  AND category = 'PIX'
ORDER BY code_value;

-- Verify PIX payment type coverage
SELECT
  COUNT(*) as pix_enabled_codes
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction = 'BR'
  AND array_contains(applicable_payment_types, 'PIX');

-- Sample data
SELECT
  code_value,
  code_description,
  category,
  iso20022_mapping,
  applicable_payment_types
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction = 'BR'
ORDER BY code_value
LIMIT 10;
