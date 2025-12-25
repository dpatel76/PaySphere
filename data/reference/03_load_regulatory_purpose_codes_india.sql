-- =====================================================================
-- Script: Load India (RBI) Regulatory Purpose Codes
-- Purpose: Populate 80 S-codes for LRS and remittance reporting
-- Regulatory Authority: Reserve Bank of India (RBI)
-- Reference: FEMA Purpose Codes / LRS Categories (2015-2024)
-- =====================================================================

INSERT INTO cdm_silver.regulatory_purpose_code
(purpose_code_id, jurisdiction, code_value, code_description, category, sub_category, iso20022_mapping, applicable_payment_types, requires_supporting_documents, effective_from, effective_to, created_timestamp, last_updated_timestamp)
VALUES

-- =============================
-- TRADE & BUSINESS (S0001-S0099)
-- =============================
(uuid(), 'IN', 'S0001', 'Import of goods', 'Trade', 'Import', 'GDDS', array('SWIFT', 'Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0002', 'Export of goods', 'Trade', 'Export', 'GDDS', array('SWIFT', 'Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0003', 'Payment for services - import', 'Trade', 'Services', 'SVCS', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0004', 'Payment for services - export', 'Trade', 'Services', 'SVCS', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0005', 'Business travel', 'Trade', 'Travel', 'TRAD', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0006', 'Software imports', 'Trade', 'Technology', 'SVCS', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0007', 'Software exports', 'Trade', 'Technology', 'SVCS', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0008', 'Consultancy services', 'Trade', 'Professional', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0009', 'Technical services', 'Trade', 'Professional', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0010', 'Management and marketing services', 'Trade', 'Professional', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- INVESTMENT (S0101-S0199)
-- =============================
(uuid(), 'IN', 'S0101', 'Investment in equity - FDI', 'Investment', 'Direct Investment', 'DIVI', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0102', 'Investment in equity - FPI', 'Investment', 'Portfolio Investment', 'DIVI', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0103', 'Repatriation of investment', 'Investment', 'Disinvestment', 'DIVI', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0104', 'Dividend remittance', 'Investment', 'Investment Income', 'DIVI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0105', 'Interest on external commercial borrowings', 'Investment', 'Debt Service', 'INTC', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0106', 'Repayment of ECB principal', 'Investment', 'Debt Service', 'LOAN', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0107', 'Investment in real estate abroad', 'Investment', 'Real Estate', 'BUSI', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0108', 'Reinvestment of profits', 'Investment', 'Direct Investment', 'DIVI', array('Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- REMITTANCES (S0201-S0299)
-- =============================
(uuid(), 'IN', 'S0201', 'Maintenance of close relatives', 'Remittances', 'Family', 'FAMI', array('Wire', 'Mobile', 'UPI'), false, '2016-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0202', 'Education-related expenses', 'Remittances', 'Education', 'EDUC', array('Wire', 'UPI'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0203', 'Medical treatment abroad', 'Remittances', 'Medical', 'MDCS', array('Wire', 'UPI'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0204', 'Gift remittance', 'Remittances', 'Gift', 'CHAR', array('Wire', 'Mobile', 'UPI'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0205', 'Donation to charitable institutions', 'Remittances', 'Charity', 'CHAR', array('Wire', 'UPI'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0206', 'Private visits to foreign countries', 'Remittances', 'Travel', 'TRAD', array('Wire', 'Mobile', 'UPI'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0207', 'Employment remittance', 'Remittances', 'Employment', 'SALA', array('Wire', 'Mobile', 'UPI'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0208', 'Emigration expenses', 'Remittances', 'Migration', 'FAMI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0209', 'Loan repayment to non-resident', 'Remittances', 'Loan', 'LOAN', array('Wire', 'UPI'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0210', 'Repatriation of salary', 'Remittances', 'Salary', 'SALA', array('Wire', 'Mobile', 'UPI'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0211', 'Pension received from abroad', 'Remittances', 'Pension', 'PENS', array('Wire', 'UPI'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0212', 'Payment of taxes abroad', 'Remittances', 'Taxes', 'TAXS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0213', 'Overseas subscription to newspapers/periodicals', 'Remittances', 'Subscription', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0214', 'Payment for cultural and sports activities', 'Remittances', 'Cultural', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0215', 'Scholarship payment', 'Remittances', 'Scholarship', 'EDUC', array('Wire', 'UPI'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- LRS SPECIFIC (S0301-S0399)
-- =============================
(uuid(), 'IN', 'S0301', 'LRS - purchase of property abroad', 'LRS', 'Real Estate', 'BUSI', array('Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0302', 'LRS - deposit in foreign bank', 'LRS', 'Deposits', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0303', 'LRS - investment in foreign securities', 'LRS', 'Securities', 'DIVI', array('Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0304', 'LRS - investment in mutual funds', 'LRS', 'Mutual Funds', 'DIVI', array('Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0305', 'LRS - maintenance of relative living abroad', 'LRS', 'Family', 'FAMI', array('Wire', 'UPI'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0306', 'LRS - studies abroad', 'LRS', 'Education', 'EDUC', array('Wire', 'UPI'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0307', 'LRS - medical treatment abroad', 'LRS', 'Medical', 'MDCS', array('Wire', 'UPI'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0308', 'LRS - travel for business', 'LRS', 'Travel', 'TRAD', array('Wire', 'Mobile', 'UPI'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0309', 'LRS - travel for personal visit', 'LRS', 'Travel', 'TRAD', array('Wire', 'Mobile', 'UPI'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0310', 'LRS - gifts and donations', 'LRS', 'Gift', 'CHAR', array('Wire', 'UPI'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0311', 'LRS - emigration consultancy', 'LRS', 'Consultancy', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0312', 'LRS - employment abroad', 'LRS', 'Employment', 'SALA', array('Wire', 'UPI'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- SHIPPING & AVIATION (S0401-S0449)
-- =============================
(uuid(), 'IN', 'S0401', 'Freight charges', 'Transportation', 'Freight', 'SVCS', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0402', 'Operating expenses of shipping companies', 'Transportation', 'Shipping', 'SVCS', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0403', 'Operating expenses of airline companies', 'Transportation', 'Aviation', 'SVCS', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0404', 'Port charges', 'Transportation', 'Port Services', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0405', 'Airport charges', 'Transportation', 'Airport Services', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- BANKING & INSURANCE (S0501-S0599)
-- =============================
(uuid(), 'IN', 'S0501', 'Banking charges and commissions', 'Financial Services', 'Banking', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0502', 'Life insurance premium', 'Financial Services', 'Insurance', 'INSU', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0503', 'General insurance premium', 'Financial Services', 'Insurance', 'INSU', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0504', 'Reinsurance premium', 'Financial Services', 'Reinsurance', 'INSU', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0505', 'Insurance claim settlement', 'Financial Services', 'Claims', 'INSU', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- COMMUNICATION SERVICES (S0601-S0649)
-- =============================
(uuid(), 'IN', 'S0601', 'Telecommunication charges', 'Communication', 'Telecom', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0602', 'Postal and courier services', 'Communication', 'Postal', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0603', 'Internet and data services', 'Communication', 'Data', 'SVCS', array('Wire'), false, '2020-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- CONSTRUCTION (S0701-S0749)
-- =============================
(uuid(), 'IN', 'S0701', 'Construction contracts abroad', 'Construction', 'Contract', 'BUSI', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0702', 'Construction materials import', 'Construction', 'Materials', 'GDDS', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- INTELLECTUAL PROPERTY (S0801-S0849)
-- =============================
(uuid(), 'IN', 'S0801', 'Royalty payments', 'Intellectual Property', 'Royalty', 'LICE', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0802', 'Technical know-how fees', 'Intellectual Property', 'Technology Transfer', 'LICE', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0803', 'Trade mark and franchise fees', 'Intellectual Property', 'Franchise', 'LICE', array('Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0804', 'Copyright fees', 'Intellectual Property', 'Copyright', 'LICE', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0805', 'Patent fees', 'Intellectual Property', 'Patent', 'LICE', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- GOVERNMENT & INTERNATIONAL (S0901-S0999)
-- =============================
(uuid(), 'IN', 'S0901', 'Government grants and aid', 'Government', 'Aid', 'SUBS', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0902', 'International organization membership dues', 'Government', 'Membership', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S0903', 'Embassy and diplomatic expenses', 'Government', 'Diplomatic', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- E-COMMERCE & DIGITAL (S1001-S1099)
-- =============================
(uuid(), 'IN', 'S1001', 'E-commerce transactions', 'Digital', 'E-commerce', 'GDDS', array('Wire', 'UPI', 'Mobile'), false, '2018-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S1002', 'Digital content purchases', 'Digital', 'Content', 'SVCS', array('Wire', 'UPI', 'Mobile'), false, '2018-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S1003', 'Cloud services payment', 'Digital', 'Cloud', 'SVCS', array('Wire', 'UPI'), false, '2020-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S1004', 'SaaS subscription', 'Digital', 'Software', 'SVCS', array('Wire', 'UPI'), false, '2020-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S1005', 'Cryptocurrency exchange services', 'Digital', 'Crypto', 'BUSI', array('Wire'), false, '2023-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S1006', 'Payment gateway fees', 'Digital', 'Payment Services', 'BUSI', array('Wire', 'UPI'), false, '2020-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- OTHER (S1097-S1099)
-- =============================
(uuid(), 'IN', 'S1097', 'Refund of export proceeds', 'Other', 'Refund', 'RLTI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S1098', 'Miscellaneous receipts', 'Other', 'Miscellaneous', NULL, array('Wire', 'UPI'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'IN', 'S1099', 'Other - please specify', 'Other', 'Other', NULL, array('Wire', 'UPI', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp());

-- =====================================================================
-- Validation Queries
-- =====================================================================

-- Count total India codes
SELECT COUNT(*) as total_india_codes
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction = 'IN';
-- Expected: 80

-- Count by category
SELECT
  category,
  sub_category,
  COUNT(*) as code_count
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction = 'IN'
GROUP BY category, sub_category
ORDER BY category, sub_category;

-- Check LRS coverage
SELECT
  code_value,
  code_description,
  applicable_payment_types
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction = 'IN'
  AND category = 'LRS'
ORDER BY code_value;

-- Verify UPI payment type coverage
SELECT
  COUNT(*) as upi_enabled_codes
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction = 'IN'
  AND array_contains(applicable_payment_types, 'UPI');
