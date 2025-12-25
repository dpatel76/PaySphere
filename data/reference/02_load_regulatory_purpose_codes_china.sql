-- =====================================================================
-- Script: Load China (PBoC) Regulatory Purpose Codes
-- Purpose: Populate 190 purpose codes for cross-border RMB reporting
-- Regulatory Authority: People's Bank of China (PBoC)
-- Reference: Safe Payment Code List (2015-2024)
-- =====================================================================

-- Insert China purpose codes (190 codes organized by category)

INSERT INTO cdm_silver.regulatory_purpose_code
(purpose_code_id, jurisdiction, code_value, code_description, category, sub_category, iso20022_mapping, applicable_payment_types, requires_supporting_documents, effective_from, effective_to, created_timestamp, last_updated_timestamp)
VALUES

-- =============================
-- TRADE IN GOODS (121000-122999)
-- =============================

-- Export (121000-121999)
(uuid(), 'CN', '121010', 'General merchandise trade - export', 'Trade in Goods', 'Export', 'GDDS', array('SWIFT', 'Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '121020', 'Processing trade - export', 'Trade in Goods', 'Export', 'GDDS', array('SWIFT', 'Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '121030', 'Border/coastal trade - export', 'Trade in Goods', 'Export', 'GDDS', array('Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '121040', 'Barter trade - export', 'Trade in Goods', 'Export', 'GDDS', array('Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '121050', 'Consignment export goods', 'Trade in Goods', 'Export', 'GDDS', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '121060', 'Equipment for outward processing', 'Trade in Goods', 'Export', 'GDDS', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '121070', 'Leasing trade - export', 'Trade in Goods', 'Export', 'GDDS', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '121080', 'Outward processing of goods', 'Trade in Goods', 'Export', 'GDDS', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '121090', 'Export of donated goods', 'Trade in Goods', 'Export', 'CHAR', array('Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '121100', 'Export of sample goods', 'Trade in Goods', 'Export', 'GDDS', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- Import (122000-122999)
(uuid(), 'CN', '122010', 'General merchandise trade - import', 'Trade in Goods', 'Import', 'GDDS', array('SWIFT', 'Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '122020', 'Processing trade - import', 'Trade in Goods', 'Import', 'GDDS', array('SWIFT', 'Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '122030', 'Border/coastal trade - import', 'Trade in Goods', 'Import', 'GDDS', array('Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '122040', 'Barter trade - import', 'Trade in Goods', 'Import', 'GDDS', array('Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '122050', 'Consignment import goods', 'Trade in Goods', 'Import', 'GDDS', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '122060', 'Equipment for inward processing', 'Trade in Goods', 'Import', 'GDDS', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '122070', 'Leasing trade - import', 'Trade in Goods', 'Import', 'GDDS', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '122080', 'Inward processing of goods', 'Trade in Goods', 'Import', 'GDDS', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '122090', 'Import of donated goods', 'Trade in Goods', 'Import', 'CHAR', array('Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '122100', 'Import of sample goods', 'Trade in Goods', 'Import', 'GDDS', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '122110', 'Import of equipment', 'Trade in Goods', 'Import', 'GDDS', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '122120', 'Import of raw materials', 'Trade in Goods', 'Import', 'GDDS', array('SWIFT', 'Wire', 'RTGS'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- TRADE IN SERVICES (221000-228999)
-- =============================

-- Transportation Services (221000-221999)
(uuid(), 'CN', '221010', 'Sea freight - payment', 'Trade in Services', 'Transportation', 'SVCS', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '221020', 'Air freight - payment', 'Trade in Services', 'Transportation', 'SVCS', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '221030', 'Land freight - payment', 'Trade in Services', 'Transportation', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '221040', 'Railway freight - payment', 'Trade in Services', 'Transportation', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '221050', 'Postal and courier services', 'Trade in Services', 'Transportation', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '221060', 'Port and terminal services', 'Trade in Services', 'Transportation', 'SVCS', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '221070', 'Warehousing and storage', 'Trade in Services', 'Transportation', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '221080', 'Supporting transportation services', 'Trade in Services', 'Transportation', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- Travel Services (222000-222999)
(uuid(), 'CN', '222010', 'Business travel expenses', 'Trade in Services', 'Travel', 'TRAD', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '222020', 'Personal travel expenses', 'Trade in Services', 'Travel', 'TRAD', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '222030', 'Education-related travel', 'Trade in Services', 'Travel', 'EDUC', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '222040', 'Health-related travel', 'Trade in Services', 'Travel', 'MDCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '222050', 'Package tour services', 'Trade in Services', 'Travel', 'TRAD', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- Construction Services (223000-223999)
(uuid(), 'CN', '223010', 'Construction abroad - payment', 'Trade in Services', 'Construction', 'BUSI', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '223020', 'Construction in China - receipt', 'Trade in Services', 'Construction', 'BUSI', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '223030', 'Construction equipment rental', 'Trade in Services', 'Construction', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '223040', 'Installation and assembly', 'Trade in Services', 'Construction', 'BUSI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- Insurance Services (224000-224999)
(uuid(), 'CN', '224010', 'Life insurance - premium', 'Trade in Services', 'Insurance', 'INSU', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '224020', 'Non-life insurance - premium', 'Trade in Services', 'Insurance', 'INSU', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '224030', 'Reinsurance - premium', 'Trade in Services', 'Insurance', 'INSU', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '224040', 'Insurance claim - payout', 'Trade in Services', 'Insurance', 'INSU', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '224050', 'Auxiliary insurance services', 'Trade in Services', 'Insurance', 'INSU', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- Financial Services (225000-225999)
(uuid(), 'CN', '225010', 'Explicitly charged financial services', 'Trade in Services', 'Financial', 'BUSI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '225020', 'Securities brokerage fees', 'Trade in Services', 'Financial', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '225030', 'Asset management fees', 'Trade in Services', 'Financial', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '225040', 'Custody fees', 'Trade in Services', 'Financial', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '225050', 'Financial advisory and credit rating', 'Trade in Services', 'Financial', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- Intellectual Property (226000-226999)
(uuid(), 'CN', '226010', 'Franchises and trademark licensing fees', 'Trade in Services', 'Intellectual Property', 'LICE', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '226020', 'Licenses for products of R&D', 'Trade in Services', 'Intellectual Property', 'LICE', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '226030', 'Licenses for computer software', 'Trade in Services', 'Intellectual Property', 'LICE', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '226040', 'Licenses under industrial processes', 'Trade in Services', 'Intellectual Property', 'LICE', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '226050', 'Copyright fees', 'Trade in Services', 'Intellectual Property', 'LICE', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- Telecommunications Services (227000-227999)
(uuid(), 'CN', '227010', 'Telecommunications services', 'Trade in Services', 'Telecommunications', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '227020', 'Computer services', 'Trade in Services', 'Telecommunications', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '227030', 'Information services', 'Trade in Services', 'Telecommunications', 'SVCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '227040', 'Cloud computing services', 'Trade in Services', 'Telecommunications', 'SVCS', array('Wire'), false, '2020-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '227050', 'Data processing services', 'Trade in Services', 'Telecommunications', 'SVCS', array('Wire'), false, '2020-01-01', NULL, current_timestamp(), current_timestamp()),

-- Business and Professional Services (228000-228999)
(uuid(), 'CN', '228010', 'Legal services', 'Trade in Services', 'Professional Services', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '228020', 'Accounting and auditing services', 'Trade in Services', 'Professional Services', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '228030', 'Tax consulting services', 'Trade in Services', 'Professional Services', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '228040', 'Management consulting services', 'Trade in Services', 'Professional Services', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '228050', 'Advertising and market research', 'Trade in Services', 'Professional Services', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '228060', 'Architectural and engineering services', 'Trade in Services', 'Professional Services', 'BUSI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '228070', 'R&D services', 'Trade in Services', 'Professional Services', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '228080', 'Industrial design services', 'Trade in Services', 'Professional Services', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- INCOME (421000-424999)
-- =============================

-- Investment Income (421000-421999)
(uuid(), 'CN', '421010', 'Dividends - equity securities', 'Income', 'Investment Income', 'DIVI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '421020', 'Profit distribution - direct investment', 'Income', 'Investment Income', 'DIVI', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '421030', 'Interest - bonds', 'Income', 'Investment Income', 'INTC', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '421040', 'Interest - deposits', 'Income', 'Investment Income', 'INTC', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '421050', 'Interest - loans', 'Income', 'Investment Income', 'INTC', array('SWIFT', 'Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '421060', 'Investment fund distributions', 'Income', 'Investment Income', 'DIVI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- Compensation of Employees (422000-422999)
(uuid(), 'CN', '422010', 'Wages and salaries - cash', 'Income', 'Compensation', 'SALA', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '422020', 'Bonus payments', 'Income', 'Compensation', 'SALA', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '422030', 'Allowances and benefits', 'Income', 'Compensation', 'SALA', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '422040', 'Pension contributions', 'Income', 'Compensation', 'PENS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- Rental Income (423000-423999)
(uuid(), 'CN', '423010', 'Rent - real estate', 'Income', 'Property Income', 'RENT', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '423020', 'Rent - equipment and machinery', 'Income', 'Property Income', 'RENT', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '423030', 'Rent - vehicles', 'Income', 'Property Income', 'RENT', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- Other Income (424000-424999)
(uuid(), 'CN', '424010', 'Taxes on products and imports', 'Income', 'Government', 'TAXS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '424020', 'Subsidies received', 'Income', 'Government', 'SUBS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- CURRENT TRANSFERS (521000-524999)
-- =============================

-- Personal Remittances (521000-521999)
(uuid(), 'CN', '521010', 'Family maintenance - remittance', 'Current Transfers', 'Remittances', 'FAMI', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '521020', 'Living expenses - overseas', 'Current Transfers', 'Remittances', 'FAMI', array('Wire', 'Mobile'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '521030', 'Educational support', 'Current Transfers', 'Remittances', 'EDUC', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '521040', 'Medical support', 'Current Transfers', 'Remittances', 'MDCS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '521050', 'Gift and donation', 'Current Transfers', 'Remittances', 'CHAR', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- Social Benefits (522000-522999)
(uuid(), 'CN', '522010', 'Pension and retirement benefits', 'Current Transfers', 'Social Benefits', 'PENS', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '522020', 'Social security benefits', 'Current Transfers', 'Social Benefits', 'SSBE', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '522030', 'Social assistance benefits', 'Current Transfers', 'Social Benefits', 'SSBE', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- Insurance-related Transfers (523000-523999)
(uuid(), 'CN', '523010', 'Non-life insurance claims', 'Current Transfers', 'Insurance', 'INSU', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '523020', 'Life insurance claims', 'Current Transfers', 'Insurance', 'INSU', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- Other Current Transfers (524000-524999)
(uuid(), 'CN', '524010', 'Charitable donations', 'Current Transfers', 'Other', 'CHAR', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '524020', 'Compensation payments', 'Current Transfers', 'Other', 'BENE', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '524030', 'Lottery and gambling winnings', 'Current Transfers', 'Other', 'GAMI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '524040', 'Refunds', 'Current Transfers', 'Other', 'RLTI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- =============================
-- CAPITAL ACCOUNT (621000-622999)
-- =============================

-- Capital Transfers (621000-621999)
(uuid(), 'CN', '621010', 'Debt forgiveness', 'Capital Account', 'Capital Transfers', 'CBFF', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '621020', 'Investment grants', 'Capital Account', 'Capital Transfers', 'BUSI', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '621030', 'Migrants' transfers', 'Capital Account', 'Capital Transfers', 'FAMI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),

-- Acquisition/Disposal of Non-financial Assets (622000-622999)
(uuid(), 'CN', '622010', 'Acquisition of land and natural resources', 'Capital Account', 'Non-financial Assets', 'BUSI', array('SWIFT', 'Wire'), true, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '622020', 'Acquisition of intangible assets', 'Capital Account', 'Non-financial Assets', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp()),
(uuid(), 'CN', '622030', 'Disposal of fixed assets', 'Capital Account', 'Non-financial Assets', 'BUSI', array('Wire'), false, '2015-01-01', NULL, current_timestamp(), current_timestamp());

-- =====================================================================
-- Additional codes to reach 190 total will follow in part 2
-- This is Part 1 covering the major categories (100 codes shown)
-- =====================================================================

-- Validation query
SELECT
  category,
  sub_category,
  COUNT(*) as code_count
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction = 'CN'
GROUP BY category, sub_category
ORDER BY category, sub_category;
