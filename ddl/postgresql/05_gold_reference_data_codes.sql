-- GPS CDM - Gold Layer Reference Data & Code Value Normalization
-- ==============================================================
-- Comprehensive framework for normalizing ALL coded values from 72+ payment standards
-- Includes user-overridable mappings with audit trail
--
-- 30 Code Categories Identified:
-- 1. Priority Codes                    16. Document Type Codes
-- 2. Charge Bearer Codes               17. Creditor Reference Type Codes
-- 3. Service Level Codes               18. Instruction Codes (SWIFT)
-- 4. Clearing System Codes             19. KYC/Compliance Codes
-- 5. Settlement Method Codes           20. Regulatory Codes
-- 6. Local Instrument Codes            21. Tax Period Codes
-- 7. Account Type Codes                22. Charge Type Codes
-- 8. Purpose Codes                     23. Proprietary Codes
-- 9. Transaction Type Codes            24. Remittance Location Method
-- 10. Bank Operation Codes             25. Payment Method Codes
-- 11. Business Function Codes          26. Payment Type Codes
-- 12. Standard Entry Class Codes       27. Addenda Type Codes
-- 13. Return Reason Codes              28. Originator Status Codes
-- 14. Cancellation Reason Codes        29. FX Rate Type Codes
-- 15. Payment Status Codes             30. Reopen Case Indicator

-- =====================================================
-- MASTER TABLE: Code Type Categories
-- =====================================================

CREATE TABLE IF NOT EXISTS gold.ref_code_type (
    code_type_id VARCHAR(50) PRIMARY KEY,
    code_type_name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    iso_standard VARCHAR(50),           -- ISO standard if applicable
    max_length INT,
    is_extensible BOOLEAN DEFAULT TRUE, -- Can users add custom values?
    validation_pattern VARCHAR(200),    -- Regex pattern for validation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) DEFAULT 'SYSTEM'
);

-- Insert all 30 code type categories
INSERT INTO gold.ref_code_type (code_type_id, code_type_name, description, iso_standard, max_length, is_extensible) VALUES
-- Priority & Service
('PRIORITY', 'Instruction Priority Code', 'Payment urgency/priority indicator', 'ISO 20022', 4, FALSE),
('CHARGE_BEARER', 'Charge Bearer Code', 'Who bears the charges for the payment', 'ISO 20022', 4, FALSE),
('SERVICE_LEVEL', 'Service Level Code', 'Service level agreement identifier', 'ISO 20022', 4, TRUE),
('CLEARING_SYSTEM', 'Clearing System Code', 'Payment clearing system identifier', 'ISO 20022', 10, TRUE),
('SETTLEMENT_METHOD', 'Settlement Method Code', 'How the payment is settled between agents', 'ISO 20022', 4, FALSE),
('LOCAL_INSTRUMENT', 'Local Instrument Code', 'Country/scheme-specific payment type', 'ISO 20022', 35, TRUE),

-- Account & Entity
('ACCOUNT_TYPE', 'Account Type Code', 'Type of bank account', 'ISO 20022', 4, TRUE),
('ACCOUNT_SCHEME', 'Account Scheme Name', 'Account number scheme (IBAN, BBAN)', 'ISO 20022', 4, FALSE),

-- Purpose & Category
('PURPOSE', 'Purpose Code', 'Purpose of the payment', 'ISO 20022', 4, TRUE),
('CATEGORY_PURPOSE', 'Category Purpose Code', 'High-level payment category', 'ISO 20022', 4, TRUE),

-- Transaction Classification
('TRANSACTION_TYPE', 'Transaction Type Code', 'Type of transaction (credit, debit)', NULL, 10, TRUE),
('BANK_OPERATION', 'Bank Operation Code', 'SWIFT MT bank operation type', 'SWIFT', 4, FALSE),
('BUSINESS_FUNCTION', 'Business Function Code', 'Fedwire business function', 'Fedwire', 3, FALSE),
('SEC_CODE', 'Standard Entry Class Code', 'ACH entry class code', 'NACHA', 3, FALSE),
('PAYMENT_METHOD', 'Payment Method Code', 'Method of payment execution', 'ISO 20022', 4, FALSE),
('PAYMENT_TYPE', 'Payment Type Code', 'Wire/message type indicator', NULL, 10, TRUE),

-- Status & Return
('PAYMENT_STATUS', 'Payment Status Code', 'Current status of payment processing', 'ISO 20022', 4, FALSE),
('ENTRY_STATUS', 'Entry Status Code', 'Bank statement entry status', 'ISO 20022', 4, FALSE),
('RETURN_REASON', 'Return Reason Code', 'Reason for returning payment', 'ISO 20022', 4, TRUE),
('ACH_RETURN', 'ACH Return Code', 'NACHA ACH return reason', 'NACHA', 3, FALSE),
('CANCELLATION_REASON', 'Cancellation Reason Code', 'Reason for cancelling payment', 'ISO 20022', 4, TRUE),

-- Documents & Remittance
('DOCUMENT_TYPE', 'Document Type Code', 'Type of referenced document', 'ISO 20022', 4, TRUE),
('CREDITOR_REF_TYPE', 'Creditor Reference Type', 'Type of creditor reference', 'ISO 20022', 4, FALSE),
('REMITTANCE_METHOD', 'Remittance Location Method', 'How remittance info is delivered', 'ISO 20022', 4, FALSE),

-- SWIFT Specific
('INSTRUCTION_CODE', 'Instruction Code', 'SWIFT payment instruction code', 'SWIFT', 4, FALSE),
('ADDENDA_TYPE', 'Addenda Type Code', 'ACH addenda record type', 'NACHA', 2, FALSE),

-- Regulatory & Compliance
('KYC_STATUS', 'KYC Status Code', 'Know Your Customer verification status', 'ISO 20022', 4, FALSE),
('KYC_DOC_TYPE', 'KYC Document Type', 'Type of KYC identification document', 'ISO 20022', 4, TRUE),
('REGULATORY_INDICATOR', 'Regulatory Indicator', 'Debit/Credit regulatory reporting', 'ISO 20022', 4, FALSE),
('TAX_PERIOD', 'Tax Period Type', 'Tax period classification', 'ISO 20022', 4, FALSE),

-- FX & Other
('FX_RATE_TYPE', 'FX Rate Type Code', 'Type of exchange rate', 'ISO 20022', 4, FALSE),
('ORIGINATOR_STATUS', 'Originator Status Code', 'ACH originator bank/non-bank', 'NACHA', 1, FALSE),
('CHARGE_TYPE', 'Charge Type Code', 'Type of charge being assessed', 'ISO 20022', 4, TRUE)

ON CONFLICT (code_type_id) DO UPDATE SET
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

-- =====================================================
-- CODE VALUES TABLE: All Standardized Code Values
-- =====================================================

CREATE TABLE IF NOT EXISTS gold.ref_code_value (
    code_value_id SERIAL PRIMARY KEY,
    code_type_id VARCHAR(50) NOT NULL REFERENCES gold.ref_code_type(code_type_id),
    code_value VARCHAR(35) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    iso_code VARCHAR(10),               -- ISO reference code if different
    is_active BOOLEAN DEFAULT TRUE,
    is_deprecated BOOLEAN DEFAULT FALSE,
    deprecated_by VARCHAR(35),          -- Replacement code if deprecated
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) DEFAULT 'SYSTEM',
    UNIQUE(code_type_id, code_value)
);

-- =====================================================
-- Insert Priority Codes
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
('PRIORITY', 'HIGH', 'High Priority', 'High priority payment, process urgently', 1),
('PRIORITY', 'NORM', 'Normal Priority', 'Standard/normal priority', 2),
('PRIORITY', 'URGP', 'Urgent Payment', 'Urgent payment priority', 3),
('PRIORITY', 'URGN', 'Urgent (Legacy)', 'Urgent priority (older ISO versions)', 4)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- =====================================================
-- Insert Charge Bearer Codes
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
-- ISO 20022 codes
('CHARGE_BEARER', 'DEBT', 'Debtor Bears All', 'All charges are borne by the debtor', 1),
('CHARGE_BEARER', 'CRED', 'Creditor Bears All', 'All charges are borne by the creditor', 2),
('CHARGE_BEARER', 'SHAR', 'Shared', 'Charges shared between debtor and creditor', 3),
('CHARGE_BEARER', 'SLEV', 'Service Level', 'Charges as per service level agreement', 4),
-- SWIFT MT equivalents
('CHARGE_BEARER', 'OUR', 'Our Bank (OUR)', 'SWIFT: All charges paid by ordering customer', 5),
('CHARGE_BEARER', 'BEN', 'Beneficiary (BEN)', 'SWIFT: All charges paid by beneficiary', 6),
('CHARGE_BEARER', 'SHA', 'Shared (SHA)', 'SWIFT: Shared charges', 7)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- =====================================================
-- Insert Service Level Codes
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
('SERVICE_LEVEL', 'SEPA', 'SEPA', 'Single Euro Payments Area', 1),
('SERVICE_LEVEL', 'URGP', 'Urgent Payment', 'Urgent payment service level', 2),
('SERVICE_LEVEL', 'NURG', 'Non-Urgent', 'Non-urgent payment', 3),
('SERVICE_LEVEL', 'SDVA', 'Same Day Value', 'Same day value date', 4),
('SERVICE_LEVEL', 'PRPT', 'Priority Payment', 'Priority payment scheme', 5),
('SERVICE_LEVEL', 'G001', 'gpi Tracked', 'SWIFT gpi tracked payment', 6),
('SERVICE_LEVEL', 'G002', 'gpi Non-Tracked', 'SWIFT gpi non-tracked', 7),
('SERVICE_LEVEL', 'G003', 'gpi COV', 'SWIFT gpi cover payment', 8),
('SERVICE_LEVEL', 'G004', 'gpi STP', 'SWIFT gpi STP payment', 9)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- =====================================================
-- Insert Clearing System Codes
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
('CLEARING_SYSTEM', 'RTGS', 'RTGS', 'Real Time Gross Settlement', 1),
('CLEARING_SYSTEM', 'RTNS', 'RTNS', 'Real Time Net Settlement', 2),
('CLEARING_SYSTEM', 'MPNS', 'MPNS', 'Multiple Net Settlement', 3),
('CLEARING_SYSTEM', 'BOOK', 'Book Transfer', 'Internal book transfer', 4),
('CLEARING_SYSTEM', 'TGT', 'TARGET2', 'Trans-European Automated Real-time Gross settlement Express Transfer', 5),
('CLEARING_SYSTEM', 'FPS', 'Faster Payments', 'UK Faster Payments Service', 6),
('CLEARING_SYSTEM', 'CHAPS', 'CHAPS', 'Clearing House Automated Payment System (UK)', 7),
('CLEARING_SYSTEM', 'BACS', 'BACS', 'Bankers Automated Clearing Services (UK)', 8),
('CLEARING_SYSTEM', 'FEDWIRE', 'Fedwire', 'US Federal Reserve Wire Network', 9),
('CLEARING_SYSTEM', 'CHIPS', 'CHIPS', 'Clearing House Interbank Payments System', 10),
('CLEARING_SYSTEM', 'ACH', 'ACH', 'Automated Clearing House', 11),
('CLEARING_SYSTEM', 'USRTP', 'US RTP', 'US Real Time Payments', 12),
('CLEARING_SYSTEM', 'FEDNOW', 'FedNow', 'Federal Reserve FedNow Service', 13),
('CLEARING_SYSTEM', 'CNAPS', 'CNAPS', 'China National Advanced Payment System', 14),
('CLEARING_SYSTEM', 'PIX', 'PIX', 'Brazil Instant Payment System', 15),
('CLEARING_SYSTEM', 'UPI', 'UPI', 'India Unified Payments Interface', 16),
('CLEARING_SYSTEM', 'PAYNOW', 'PayNow', 'Singapore PayNow', 17),
('CLEARING_SYSTEM', 'INSTAPAY', 'InstaPay', 'Philippines InstaPay', 18),
('CLEARING_SYSTEM', 'PROMPTPAY', 'PromptPay', 'Thailand PromptPay', 19),
('CLEARING_SYSTEM', 'NPP', 'NPP', 'Australia New Payments Platform', 20),
('CLEARING_SYSTEM', 'MEPS', 'MEPS+', 'Singapore MAS Electronic Payment System', 21),
('CLEARING_SYSTEM', 'BOJNET', 'BOJ-NET', 'Japan Bank of Japan Financial Network', 22),
('CLEARING_SYSTEM', 'KFTC', 'KFTC', 'Korea Financial Telecommunications and Clearings', 23),
('CLEARING_SYSTEM', 'UAEFTS', 'UAEFTS', 'UAE Funds Transfer System', 24),
('CLEARING_SYSTEM', 'SARIE', 'SARIE', 'Saudi Arabia RTGS', 25),
('CLEARING_SYSTEM', 'RTGS_HK', 'RTGS HK', 'Hong Kong RTGS', 26)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- =====================================================
-- Insert Settlement Method Codes
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
('SETTLEMENT_METHOD', 'INDA', 'Instructed Agent', 'Settlement via instructed agent account', 1),
('SETTLEMENT_METHOD', 'INGA', 'Instructing Agent', 'Settlement via instructing agent account', 2),
('SETTLEMENT_METHOD', 'COVE', 'Cover Method', 'Settlement via cover payment', 3),
('SETTLEMENT_METHOD', 'CLRG', 'Clearing System', 'Settlement via clearing system', 4)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- =====================================================
-- Insert Account Type Codes
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
('ACCOUNT_TYPE', 'CACC', 'Current Account', 'Current/checking account', 1),
('ACCOUNT_TYPE', 'SVGS', 'Savings Account', 'Savings account', 2),
('ACCOUNT_TYPE', 'CASH', 'Cash Account', 'Cash management account', 3),
('ACCOUNT_TYPE', 'TRAD', 'Trading Account', 'Trading account', 4),
('ACCOUNT_TYPE', 'LOAN', 'Loan Account', 'Loan account', 5),
('ACCOUNT_TYPE', 'MOMA', 'Money Market Account', 'Money market account', 6),
('ACCOUNT_TYPE', 'NREX', 'Non-Resident External', 'Non-resident external account', 7),
('ACCOUNT_TYPE', 'OTHR', 'Other', 'Other account type', 8),
('ACCOUNT_TYPE', 'SACC', 'Settlement Account', 'Settlement account', 9),
('ACCOUNT_TYPE', 'SLRY', 'Salary Account', 'Salary account', 10)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- =====================================================
-- Insert Purpose Codes (Comprehensive list)
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
-- Trade & Commerce
('PURPOSE', 'GDDS', 'Purchase of Goods', 'Purchase/sale of goods', 1),
('PURPOSE', 'SVCS', 'Services', 'Payment for services', 2),
('PURPOSE', 'SUPP', 'Supplier Payment', 'Supplier payment', 3),
('PURPOSE', 'TRAD', 'Trade', 'Trade settlement', 4),
-- Employment
('PURPOSE', 'SALA', 'Salary', 'Salary payment', 10),
('PURPOSE', 'PENS', 'Pension', 'Pension payment', 11),
('PURPOSE', 'BONU', 'Bonus', 'Bonus payment', 12),
('PURPOSE', 'COMM', 'Commission', 'Commission payment', 13),
-- Financial
('PURPOSE', 'LOAN', 'Loan Payment', 'Loan repayment', 20),
('PURPOSE', 'RENT', 'Rent', 'Rent payment', 21),
('PURPOSE', 'DIVI', 'Dividend', 'Dividend payment', 22),
('PURPOSE', 'INTC', 'Intra-Company', 'Intra-company payment', 23),
('PURPOSE', 'CASH', 'Cash Management', 'Cash management transfer', 24),
('PURPOSE', 'TREA', 'Treasury', 'Treasury operation', 25),
-- Tax & Government
('PURPOSE', 'TAXS', 'Tax Payment', 'Tax payment', 30),
('PURPOSE', 'GOVT', 'Government Payment', 'Government payment', 31),
('PURPOSE', 'VATX', 'VAT Payment', 'VAT/sales tax payment', 32),
-- Investment & Securities
('PURPOSE', 'SECU', 'Securities', 'Securities transaction', 40),
('PURPOSE', 'DVPM', 'Delivery vs Payment', 'DVP settlement', 41),
('PURPOSE', 'CORT', 'Trade Settlement', 'Corporate trade settlement', 42),
-- Other
('PURPOSE', 'CHAR', 'Charity', 'Charitable donation', 50),
('PURPOSE', 'GIFT', 'Gift', 'Gift payment', 51),
('PURPOSE', 'ALMY', 'Alimony', 'Alimony payment', 52),
('PURPOSE', 'BEXP', 'Business Expenses', 'Business expenses', 53),
('PURPOSE', 'EDUC', 'Education', 'Education fees', 54),
('PURPOSE', 'MDCS', 'Medical Services', 'Medical services payment', 55),
('PURPOSE', 'UTIL', 'Utilities', 'Utility bill payment', 56),
('PURPOSE', 'INSU', 'Insurance', 'Insurance premium', 57),
('PURPOSE', 'OTHR', 'Other', 'Other purpose', 99)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- =====================================================
-- Insert Bank Operation Codes (SWIFT MT)
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
('BANK_OPERATION', 'CRED', 'Credit Transfer', 'Standard credit transfer (most common for STP)', 1),
('BANK_OPERATION', 'CRTS', 'Credit to Third Party', 'Credit transfer to third party', 2),
('BANK_OPERATION', 'SPAY', 'Special Payment', 'Special payment', 3),
('BANK_OPERATION', 'SPRI', 'Special Payment + Interest', 'Special payment with interest', 4),
('BANK_OPERATION', 'SSTD', 'Standard Delivery', 'Settle via standard delivery', 5)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- =====================================================
-- Insert Business Function Codes (Fedwire)
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
('BUSINESS_FUNCTION', 'BTR', 'Bank Transfer', 'Bank-to-bank transfer', 1),
('BUSINESS_FUNCTION', 'DRW', 'Drawdown', 'Customer/corporate drawdown request', 2),
('BUSINESS_FUNCTION', 'CKS', 'Check Same-Day', 'Check same-day settlement', 3),
('BUSINESS_FUNCTION', 'CTR', 'Customer Transfer Plus', 'Customer transfer plus', 4),
('BUSINESS_FUNCTION', 'DEP', 'Deposit', 'Deposit to sender account', 5),
('BUSINESS_FUNCTION', 'FFR', 'Fed Funds Returned', 'Federal funds returned', 6),
('BUSINESS_FUNCTION', 'FFS', 'Fed Funds Sold', 'Federal funds sold', 7),
('BUSINESS_FUNCTION', 'SVC', 'Service Message', 'Service message', 8)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- =====================================================
-- Insert ACH Standard Entry Class Codes
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
('SEC_CODE', 'PPD', 'Prearranged Payment/Deposit', 'Consumer credits/debits', 1),
('SEC_CODE', 'CCD', 'Corporate Credit/Debit', 'Corporate transactions', 2),
('SEC_CODE', 'CTX', 'Corporate Trade Exchange', 'Corporate trade with addenda', 3),
('SEC_CODE', 'WEB', 'Internet-Initiated', 'Internet-initiated entry', 4),
('SEC_CODE', 'TEL', 'Telephone-Initiated', 'Telephone-initiated entry', 5),
('SEC_CODE', 'CIE', 'Customer-Initiated', 'Customer-initiated entry', 6),
('SEC_CODE', 'POS', 'Point of Sale', 'Point-of-sale entry', 7),
('SEC_CODE', 'ARC', 'Accounts Receivable', 'Accounts receivable entry', 8),
('SEC_CODE', 'BOC', 'Back Office Conversion', 'Back office conversion', 9),
('SEC_CODE', 'POP', 'Point of Purchase', 'Point of purchase entry', 10),
('SEC_CODE', 'RCK', 'Re-presented Check', 'Re-presented check entry', 11),
('SEC_CODE', 'IAT', 'International ACH', 'International ACH transaction', 12)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- =====================================================
-- Insert Return Reason Codes (ISO 20022 - comprehensive)
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
-- Account Related (AC)
('RETURN_REASON', 'AC01', 'Incorrect Account Number', 'Format of account number is incorrect', 1),
('RETURN_REASON', 'AC02', 'Invalid Debtor Account', 'Invalid debtor account number', 2),
('RETURN_REASON', 'AC03', 'Invalid Creditor Account', 'Invalid creditor account number', 3),
('RETURN_REASON', 'AC04', 'Closed Account', 'Account is closed', 4),
('RETURN_REASON', 'AC05', 'Closed Debtor Account', 'Debtor account is closed', 5),
('RETURN_REASON', 'AC06', 'Blocked Account', 'Account is blocked', 6),
('RETURN_REASON', 'AC07', 'Closed Creditor Account', 'Creditor account is closed', 7),
-- Amount Related (AM)
('RETURN_REASON', 'AM01', 'Zero Amount', 'Amount is zero', 10),
('RETURN_REASON', 'AM02', 'Amount Not Allowed', 'Transaction amount not allowed', 11),
('RETURN_REASON', 'AM03', 'Currency Not Supported', 'Currency not supported', 12),
('RETURN_REASON', 'AM04', 'Insufficient Funds', 'Insufficient funds', 13),
('RETURN_REASON', 'AM05', 'Duplicate Payment', 'Duplicate payment', 14),
('RETURN_REASON', 'AM06', 'Too Low Amount', 'Amount too low', 15),
('RETURN_REASON', 'AM07', 'Blocked Amount', 'Amount blocked', 16),
('RETURN_REASON', 'AM09', 'Wrong Amount', 'Wrong amount', 17),
-- Agent Related (AG)
('RETURN_REASON', 'AG01', 'Transaction Forbidden', 'Transaction forbidden', 20),
('RETURN_REASON', 'AG02', 'Invalid Operation Code', 'Invalid bank operation code', 21),
('RETURN_REASON', 'AG03', 'Transaction Not Supported', 'Transaction type not supported', 22),
('RETURN_REASON', 'AG04', 'Invalid Agent Country', 'Invalid agent country', 23),
-- Regulatory (RR)
('RETURN_REASON', 'RR01', 'Missing Debtor Account', 'Regulatory - missing debtor account', 30),
('RETURN_REASON', 'RR02', 'Missing Debtor Name/Address', 'Regulatory - missing debtor details', 31),
('RETURN_REASON', 'RR03', 'Missing Creditor Name/Address', 'Regulatory - missing creditor details', 32),
('RETURN_REASON', 'RR04', 'Regulatory Reason', 'General regulatory reason', 33),
-- Mandate Related (MD)
('RETURN_REASON', 'MD01', 'No Mandate', 'No mandate found', 40),
('RETURN_REASON', 'MD02', 'Missing Creditor Info', 'Missing mandatory creditor info', 41),
('RETURN_REASON', 'MD06', 'Refund Request by End Customer', 'Refund request', 42),
('RETURN_REASON', 'MD07', 'End Customer Deceased', 'Customer deceased', 43),
-- Technical (BE, FF, MS, etc.)
('RETURN_REASON', 'BE01', 'Inconsistent with End Customer', 'Debtor info inconsistent', 50),
('RETURN_REASON', 'BE04', 'Missing Creditor Address', 'Missing creditor address', 51),
('RETURN_REASON', 'BE05', 'Unknown Creditor', 'Unrecognized creditor', 52),
('RETURN_REASON', 'FF01', 'Invalid File Format', 'Invalid file format', 60),
('RETURN_REASON', 'MS02', 'Not Specified Reason by Customer', 'Reason not specified', 70),
('RETURN_REASON', 'MS03', 'Not Specified Reason by Agent', 'Agent reason not specified', 71),
('RETURN_REASON', 'RC01', 'Bank Identifier Incorrect', 'BIC invalid', 80),
('RETURN_REASON', 'TM01', 'Cut-Off Time', 'Past cut-off time', 90),
('RETURN_REASON', 'NARR', 'Narrative', 'See narrative for reason', 99)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- =====================================================
-- Insert Payment Status Codes
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
('PAYMENT_STATUS', 'ACCC', 'Accepted Settlement Completed', 'Settlement completed on creditor', 1),
('PAYMENT_STATUS', 'ACCP', 'Accepted Customer Profile', 'Accepted technical validation', 2),
('PAYMENT_STATUS', 'ACSC', 'Accepted Settlement Clearing', 'Accepted in settlement, clearing', 3),
('PAYMENT_STATUS', 'ACSP', 'Accepted Settlement Processing', 'Accepted settlement in process', 4),
('PAYMENT_STATUS', 'ACTC', 'Accepted Technical', 'Accepted technical validation', 5),
('PAYMENT_STATUS', 'ACWC', 'Accepted With Change', 'Accepted with modification', 6),
('PAYMENT_STATUS', 'PDNG', 'Pending', 'Payment is pending', 7),
('PAYMENT_STATUS', 'RCVD', 'Received', 'Payment received', 8),
('PAYMENT_STATUS', 'RJCT', 'Rejected', 'Payment rejected', 9),
('PAYMENT_STATUS', 'CANC', 'Cancelled', 'Payment cancelled', 10),
('PAYMENT_STATUS', 'PART', 'Partially Accepted', 'Partially accepted', 11)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- =====================================================
-- Insert Document Type Codes
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
('DOCUMENT_TYPE', 'CINV', 'Commercial Invoice', 'Commercial invoice', 1),
('DOCUMENT_TYPE', 'CNFA', 'Credit Note', 'Credit note related to financial adjustment', 2),
('DOCUMENT_TYPE', 'DNFA', 'Debit Note', 'Debit note related to financial adjustment', 3),
('DOCUMENT_TYPE', 'MSIN', 'Metered Service Invoice', 'Metered service invoice', 4),
('DOCUMENT_TYPE', 'SOAC', 'Statement of Account', 'Statement of account', 5),
('DOCUMENT_TYPE', 'DISP', 'Dispatch Advice', 'Dispatch advice', 6),
('DOCUMENT_TYPE', 'PRWD', 'Priced Waybill', 'Priced waybill', 7),
('DOCUMENT_TYPE', 'AROI', 'Account Receivable Invoice', 'Accounts receivable invoice', 8),
('DOCUMENT_TYPE', 'TSUT', 'Trade Services Utility', 'Trade services utility transaction', 9),
('DOCUMENT_TYPE', 'PUOR', 'Purchase Order', 'Purchase order', 10)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- =====================================================
-- Insert Instruction Codes (SWIFT)
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
('INSTRUCTION_CODE', 'CHQB', 'Beneficiary Non-Bank', 'Pay by check to beneficiary who is not a bank', 1),
('INSTRUCTION_CODE', 'HOLD', 'Hold', 'Hold for pickup', 2),
('INSTRUCTION_CODE', 'INTC', 'Intra-Company', 'Intra-company payment', 3),
('INSTRUCTION_CODE', 'PHOB', 'Phone Beneficiary', 'Phone notification to beneficiary', 4),
('INSTRUCTION_CODE', 'PHOI', 'Phone Intermediary', 'Phone notification to intermediary', 5),
('INSTRUCTION_CODE', 'PHON', 'Phone', 'General phone notification', 6),
('INSTRUCTION_CODE', 'REPA', 'Rejected Payment', 'Rejected, pay alternate', 7),
('INSTRUCTION_CODE', 'SDVA', 'Same Day Value', 'Same day value', 8),
('INSTRUCTION_CODE', 'TELB', 'Telecom Beneficiary', 'Telecom notification to beneficiary', 9),
('INSTRUCTION_CODE', 'TELE', 'Telecom', 'General telecom notification', 10),
('INSTRUCTION_CODE', 'TELI', 'Telecom Intermediary', 'Telecom notification to intermediary', 11)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- =====================================================
-- Insert Payment Method Codes
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
('PAYMENT_METHOD', 'CHK', 'Check', 'Payment by check', 1),
('PAYMENT_METHOD', 'TRF', 'Transfer', 'Credit transfer', 2),
('PAYMENT_METHOD', 'TRA', 'Transfer Account', 'Transfer to account', 3),
('PAYMENT_METHOD', 'DD', 'Direct Debit', 'Direct debit', 4)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- =====================================================
-- Insert FX Rate Type Codes
-- =====================================================
INSERT INTO gold.ref_code_value (code_type_id, code_value, display_name, description, sort_order) VALUES
('FX_RATE_TYPE', 'SPOT', 'Spot Rate', 'Spot exchange rate', 1),
('FX_RATE_TYPE', 'SALE', 'Sale Rate', 'Sale exchange rate', 2),
('FX_RATE_TYPE', 'AGRD', 'Agreed Rate', 'Contracted/agreed rate', 3)
ON CONFLICT (code_type_id, code_value) DO NOTHING;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ref_code_value_type ON gold.ref_code_value(code_type_id);
CREATE INDEX IF NOT EXISTS idx_ref_code_value_active ON gold.ref_code_value(code_type_id, is_active) WHERE is_active = TRUE;

-- =====================================================
-- SOURCE MAPPING TABLE: Map source formats to CDM codes
-- Master table for all code mappings with full audit trail
-- =====================================================

CREATE TABLE IF NOT EXISTS gold.ref_code_source_mapping (
    mapping_id SERIAL PRIMARY KEY,

    -- Code Type Reference
    code_type_id VARCHAR(50) NOT NULL REFERENCES gold.ref_code_type(code_type_id),

    -- Source Message Format Details
    message_format VARCHAR(50) NOT NULL,        -- pain.001, MT103, FEDWIRE, pacs.008, etc.
    message_format_version VARCHAR(20),         -- Version of the message format (e.g., 001.001.11)
    source_field_name VARCHAR(100) NOT NULL,    -- Original field name in source standard
    source_field_path VARCHAR(300),             -- Full XPath or field path (e.g., GrpHdr/MsgId)

    -- Code Values
    source_code_value VARCHAR(35) NOT NULL,     -- Original code value in source format
    source_code_description VARCHAR(500),       -- Description from source standard
    cdm_code_value VARCHAR(35) NOT NULL,        -- Normalized CDM code value
    cdm_code_description VARCHAR(500),          -- CDM code description

    -- Mapping Metadata
    mapping_confidence VARCHAR(20) DEFAULT 'EXACT', -- EXACT, EQUIVALENT, APPROXIMATE, MANUAL
    mapping_rationale VARCHAR(1000),            -- Explanation of why this mapping was chosen
    is_default BOOLEAN DEFAULT FALSE,           -- Default mapping if ambiguous
    is_bidirectional BOOLEAN DEFAULT TRUE,      -- Can map both ways?

    -- Validity Period
    effective_start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    effective_end_date DATE,                    -- NULL = no end date (currently active)
    is_active BOOLEAN DEFAULT TRUE,

    -- Audit Trail
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NOT NULL DEFAULT 'SYSTEM',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) NOT NULL DEFAULT 'SYSTEM',

    -- Notes & Documentation
    notes VARCHAR(500),
    reference_document VARCHAR(200),            -- Reference to standard document
    reference_url VARCHAR(500),                 -- URL to official documentation

    UNIQUE(code_type_id, message_format, source_field_name, source_code_value, effective_start_date)
);

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_ref_code_map_effective ON gold.ref_code_source_mapping(effective_start_date, effective_end_date)
WHERE is_active = TRUE;

-- Insert key mappings for Charge Bearer (SWIFT MT to ISO 20022)
INSERT INTO gold.ref_code_source_mapping (
    code_type_id, message_format, message_format_version, source_field_name, source_field_path,
    source_code_value, source_code_description, cdm_code_value, cdm_code_description,
    mapping_confidence, mapping_rationale, effective_start_date, created_by, notes
) VALUES
-- MT103 Charge Bearer mappings
('CHARGE_BEARER', 'MT103', '2023', 'Field71A', ':71A:', 'OUR', 'All charges paid by ordering customer', 'DEBT', 'Debtor bears all charges', 'EQUIVALENT', 'SWIFT OUR semantically equivalent to ISO DEBT - both mean ordering party pays all charges', '2024-01-01', 'SYSTEM', 'SWIFT MT to ISO 20022 mapping'),
('CHARGE_BEARER', 'MT103', '2023', 'Field71A', ':71A:', 'BEN', 'All charges paid by beneficiary', 'CRED', 'Creditor bears all charges', 'EQUIVALENT', 'SWIFT BEN semantically equivalent to ISO CRED - both mean beneficiary pays all charges', '2024-01-01', 'SYSTEM', 'SWIFT MT to ISO 20022 mapping'),
('CHARGE_BEARER', 'MT103', '2023', 'Field71A', ':71A:', 'SHA', 'Charges shared', 'SHAR', 'Charges shared between debtor and creditor', 'EQUIVALENT', 'SWIFT SHA semantically equivalent to ISO SHAR - both mean shared charges', '2024-01-01', 'SYSTEM', 'SWIFT MT to ISO 20022 mapping'),

-- pain.001 Charge Bearer mappings (direct/exact)
('CHARGE_BEARER', 'pain.001', '001.001.11', 'ChrgBr', 'PmtInf/ChrgBr', 'DEBT', 'Debtor bears charges', 'DEBT', 'Debtor bears all charges', 'EXACT', 'Direct ISO 20022 mapping - same code', '2024-01-01', 'SYSTEM', 'ISO 20022 native'),
('CHARGE_BEARER', 'pain.001', '001.001.11', 'ChrgBr', 'PmtInf/ChrgBr', 'CRED', 'Creditor bears charges', 'CRED', 'Creditor bears all charges', 'EXACT', 'Direct ISO 20022 mapping - same code', '2024-01-01', 'SYSTEM', 'ISO 20022 native'),
('CHARGE_BEARER', 'pain.001', '001.001.11', 'ChrgBr', 'PmtInf/ChrgBr', 'SHAR', 'Charges shared', 'SHAR', 'Charges shared between debtor and creditor', 'EXACT', 'Direct ISO 20022 mapping - same code', '2024-01-01', 'SYSTEM', 'ISO 20022 native'),
('CHARGE_BEARER', 'pain.001', '001.001.11', 'ChrgBr', 'PmtInf/ChrgBr', 'SLEV', 'Service level', 'SLEV', 'Charges as per service level agreement', 'EXACT', 'Direct ISO 20022 mapping - same code', '2024-01-01', 'SYSTEM', 'ISO 20022 native'),

-- pacs.008 Charge Bearer mappings (direct/exact)
('CHARGE_BEARER', 'pacs.008', '008.001.10', 'ChrgBr', 'CdtTrfTxInf/ChrgBr', 'DEBT', 'Debtor bears charges', 'DEBT', 'Debtor bears all charges', 'EXACT', 'Direct ISO 20022 mapping - same code', '2024-01-01', 'SYSTEM', 'ISO 20022 native'),
('CHARGE_BEARER', 'pacs.008', '008.001.10', 'ChrgBr', 'CdtTrfTxInf/ChrgBr', 'CRED', 'Creditor bears charges', 'CRED', 'Creditor bears all charges', 'EXACT', 'Direct ISO 20022 mapping - same code', '2024-01-01', 'SYSTEM', 'ISO 20022 native'),
('CHARGE_BEARER', 'pacs.008', '008.001.10', 'ChrgBr', 'CdtTrfTxInf/ChrgBr', 'SHAR', 'Charges shared', 'SHAR', 'Charges shared between debtor and creditor', 'EXACT', 'Direct ISO 20022 mapping - same code', '2024-01-01', 'SYSTEM', 'ISO 20022 native'),
('CHARGE_BEARER', 'pacs.008', '008.001.10', 'ChrgBr', 'CdtTrfTxInf/ChrgBr', 'SLEV', 'Service level', 'SLEV', 'Charges as per service level agreement', 'EXACT', 'Direct ISO 20022 mapping - same code', '2024-01-01', 'SYSTEM', 'ISO 20022 native'),

-- FEDWIRE Charge Bearer mappings
('CHARGE_BEARER', 'FEDWIRE', '2024', 'ChargeBearer', '{6200}', 'OUR', 'All charges paid by originator', 'DEBT', 'Debtor bears all charges', 'EQUIVALENT', 'Fedwire charge instruction mapped to ISO equivalent', '2024-01-01', 'SYSTEM', 'Fedwire to ISO 20022 mapping'),
('CHARGE_BEARER', 'FEDWIRE', '2024', 'ChargeBearer', '{6200}', 'BEN', 'All charges paid by beneficiary', 'CRED', 'Creditor bears all charges', 'EQUIVALENT', 'Fedwire charge instruction mapped to ISO equivalent', '2024-01-01', 'SYSTEM', 'Fedwire to ISO 20022 mapping'),
('CHARGE_BEARER', 'FEDWIRE', '2024', 'ChargeBearer', '{6200}', 'SHA', 'Charges shared', 'SHAR', 'Charges shared between debtor and creditor', 'EQUIVALENT', 'Fedwire charge instruction mapped to ISO equivalent', '2024-01-01', 'SYSTEM', 'Fedwire to ISO 20022 mapping')

ON CONFLICT (code_type_id, message_format, source_field_name, source_code_value, effective_start_date) DO NOTHING;

-- Insert mappings for Business Function to Purpose (Fedwire to ISO)
INSERT INTO gold.ref_code_source_mapping (
    code_type_id, message_format, message_format_version, source_field_name, source_field_path,
    source_code_value, source_code_description, cdm_code_value, cdm_code_description,
    mapping_confidence, mapping_rationale, effective_start_date, created_by, notes
) VALUES
('PURPOSE', 'FEDWIRE', '2024', 'BusinessFunctionCode', '{3600}', 'BTR', 'Bank Transfer', 'CASH', 'Cash Management', 'APPROXIMATE', 'Bank transfer typically used for cash management between banks', '2024-01-01', 'SYSTEM', 'Fedwire business function to ISO purpose'),
('PURPOSE', 'FEDWIRE', '2024', 'BusinessFunctionCode', '{3600}', 'CTR', 'Customer Transfer Plus', 'TRAD', 'Trade', 'APPROXIMATE', 'Customer transfer often relates to trade settlements', '2024-01-01', 'SYSTEM', 'Fedwire business function to ISO purpose'),
('PURPOSE', 'FEDWIRE', '2024', 'BusinessFunctionCode', '{3600}', 'DRW', 'Drawdown Request', 'LOAN', 'Loan Payment', 'APPROXIMATE', 'Drawdown typically relates to loan/credit facility utilization', '2024-01-01', 'SYSTEM', 'Fedwire business function to ISO purpose'),
('PURPOSE', 'FEDWIRE', '2024', 'BusinessFunctionCode', '{3600}', 'DEP', 'Deposit', 'CASH', 'Cash Management', 'APPROXIMATE', 'Deposit is a cash management function', '2024-01-01', 'SYSTEM', 'Fedwire business function to ISO purpose'),
('PURPOSE', 'FEDWIRE', '2024', 'BusinessFunctionCode', '{3600}', 'FFS', 'Fed Funds Sold', 'TREA', 'Treasury', 'APPROXIMATE', 'Fed funds sold is a treasury operation', '2024-01-01', 'SYSTEM', 'Fedwire business function to ISO purpose'),
('PURPOSE', 'FEDWIRE', '2024', 'BusinessFunctionCode', '{3600}', 'FFR', 'Fed Funds Returned', 'TREA', 'Treasury', 'APPROXIMATE', 'Fed funds returned is a treasury operation', '2024-01-01', 'SYSTEM', 'Fedwire business function to ISO purpose')

ON CONFLICT (code_type_id, message_format, source_field_name, source_code_value, effective_start_date) DO NOTHING;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ref_code_map_type ON gold.ref_code_source_mapping(code_type_id);
CREATE INDEX IF NOT EXISTS idx_ref_code_map_format ON gold.ref_code_source_mapping(message_format);
CREATE INDEX IF NOT EXISTS idx_ref_code_map_lookup ON gold.ref_code_source_mapping(code_type_id, message_format, source_code_value);

-- =====================================================
-- USER OVERRIDE TABLE: Allow users to override mappings
-- =====================================================

CREATE TABLE IF NOT EXISTS gold.code_mapping_override (
    override_id SERIAL PRIMARY KEY,

    -- What is being overridden
    override_type VARCHAR(30) NOT NULL,         -- CODE_VALUE, SOURCE_MAPPING
    code_type_id VARCHAR(50) NOT NULL REFERENCES gold.ref_code_type(code_type_id),

    -- For CODE_VALUE overrides
    code_value VARCHAR(35),
    new_display_name VARCHAR(100),
    new_description VARCHAR(500),

    -- For SOURCE_MAPPING overrides
    message_format VARCHAR(50),
    source_field_name VARCHAR(100),
    source_code_value VARCHAR(35),
    original_cdm_code_value VARCHAR(35),
    override_cdm_code_value VARCHAR(35),

    -- Validity
    effective_from DATE NOT NULL DEFAULT CURRENT_DATE,
    effective_to DATE,                          -- NULL = no end date
    is_active BOOLEAN DEFAULT TRUE,

    -- Approval workflow
    status VARCHAR(20) DEFAULT 'PENDING',       -- PENDING, APPROVED, REJECTED
    requested_by VARCHAR(100) NOT NULL,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    request_reason VARCHAR(500),
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    rejection_reason VARCHAR(500),

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_override_type CHECK (
        (override_type = 'CODE_VALUE' AND code_value IS NOT NULL) OR
        (override_type = 'SOURCE_MAPPING' AND message_format IS NOT NULL AND source_code_value IS NOT NULL)
    )
);

-- Create indexes for override lookups
CREATE INDEX IF NOT EXISTS idx_override_type ON gold.code_mapping_override(code_type_id, override_type);
CREATE INDEX IF NOT EXISTS idx_override_active ON gold.code_mapping_override(is_active, status) WHERE is_active = TRUE AND status = 'APPROVED';
CREATE INDEX IF NOT EXISTS idx_override_effective ON gold.code_mapping_override(effective_from, effective_to);

-- =====================================================
-- AUDIT LOG TABLE: Track all changes to reference data
-- =====================================================

CREATE TABLE IF NOT EXISTS gold.ref_data_audit_log (
    audit_id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,           -- Which reference table
    record_id VARCHAR(100) NOT NULL,            -- Primary key of changed record
    action VARCHAR(20) NOT NULL,                -- INSERT, UPDATE, DELETE
    old_values JSONB,                           -- Previous values (for UPDATE/DELETE)
    new_values JSONB,                           -- New values (for INSERT/UPDATE)
    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_reason VARCHAR(500),
    ip_address VARCHAR(45),
    user_agent VARCHAR(500)
);

-- Create indexes for audit queries
CREATE INDEX IF NOT EXISTS idx_audit_table ON gold.ref_data_audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_record ON gold.ref_data_audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_time ON gold.ref_data_audit_log(changed_at);
CREATE INDEX IF NOT EXISTS idx_audit_user ON gold.ref_data_audit_log(changed_by);

-- =====================================================
-- VIEWS: For easy querying and UI display
-- =====================================================

-- View: All active code values with type info
CREATE OR REPLACE VIEW gold.vw_active_code_values AS
SELECT
    ct.code_type_id,
    ct.code_type_name,
    ct.description AS type_description,
    ct.iso_standard,
    cv.code_value,
    cv.display_name,
    cv.description AS value_description,
    cv.is_deprecated,
    cv.deprecated_by,
    cv.sort_order
FROM gold.ref_code_type ct
JOIN gold.ref_code_value cv ON ct.code_type_id = cv.code_type_id
WHERE cv.is_active = TRUE
ORDER BY ct.code_type_id, cv.sort_order;

-- View: Code mappings with override support (for data processing pipeline)
-- This view returns ONLY the effective mappings that should be applied during Gold transformation
CREATE OR REPLACE VIEW gold.vw_effective_code_mappings AS
SELECT
    sm.code_type_id,
    sm.message_format,
    sm.message_format_version,
    sm.source_field_name,
    sm.source_field_path,
    sm.source_code_value,
    sm.source_code_description,
    -- Apply override if exists, otherwise use base mapping
    COALESCE(ov.override_cdm_code_value, sm.cdm_code_value) AS effective_cdm_code_value,
    COALESCE(
        (SELECT cv.display_name FROM gold.ref_code_value cv
         WHERE cv.code_type_id = sm.code_type_id
         AND cv.code_value = COALESCE(ov.override_cdm_code_value, sm.cdm_code_value)),
        sm.cdm_code_description
    ) AS effective_cdm_description,
    sm.cdm_code_value AS original_cdm_code_value,
    sm.cdm_code_description AS original_cdm_description,
    -- Override tracking
    CASE WHEN ov.override_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_overridden,
    ov.override_id,
    ov.request_reason AS override_reason,
    ov.approved_by AS override_approved_by,
    ov.approved_at AS override_approved_at,
    -- Mapping metadata
    sm.mapping_confidence,
    sm.mapping_rationale,
    sm.is_bidirectional,
    -- Effective dates (use override dates if overridden, otherwise base mapping dates)
    COALESCE(ov.effective_from, sm.effective_start_date) AS effective_from,
    COALESCE(ov.effective_to, sm.effective_end_date) AS effective_to,
    sm.notes,
    sm.reference_document
FROM gold.ref_code_source_mapping sm
LEFT JOIN gold.code_mapping_override ov ON
    ov.code_type_id = sm.code_type_id
    AND ov.message_format = sm.message_format
    AND ov.source_code_value = sm.source_code_value
    AND ov.override_type = 'SOURCE_MAPPING'
    AND ov.is_active = TRUE
    AND ov.status = 'APPROVED'
    AND CURRENT_DATE >= ov.effective_from
    AND (ov.effective_to IS NULL OR CURRENT_DATE <= ov.effective_to)
WHERE sm.is_active = TRUE
  AND CURRENT_DATE >= sm.effective_start_date
  AND (sm.effective_end_date IS NULL OR CURRENT_DATE <= sm.effective_end_date);

-- View: Pending override requests
CREATE OR REPLACE VIEW gold.vw_pending_override_requests AS
SELECT
    o.*,
    ct.code_type_name,
    CASE
        WHEN o.override_type = 'CODE_VALUE' THEN cv.display_name
        ELSE sm.cdm_code_value
    END AS original_value_display
FROM gold.code_mapping_override o
JOIN gold.ref_code_type ct ON o.code_type_id = ct.code_type_id
LEFT JOIN gold.ref_code_value cv ON o.code_type_id = cv.code_type_id AND o.code_value = cv.code_value
LEFT JOIN gold.ref_code_source_mapping sm ON
    o.code_type_id = sm.code_type_id
    AND o.message_format = sm.message_format
    AND o.source_code_value = sm.source_code_value
WHERE o.status = 'PENDING'
ORDER BY o.requested_at;

-- View: Reference data statistics
CREATE OR REPLACE VIEW gold.vw_reference_data_stats AS
SELECT
    ct.code_type_id,
    ct.code_type_name,
    COUNT(DISTINCT cv.code_value) AS total_values,
    COUNT(DISTINCT cv.code_value) FILTER (WHERE cv.is_active) AS active_values,
    COUNT(DISTINCT sm.mapping_id) AS total_mappings,
    COUNT(DISTINCT sm.message_format) AS formats_mapped,
    COUNT(DISTINCT ov.override_id) FILTER (WHERE ov.is_active AND ov.status = 'APPROVED') AS active_overrides
FROM gold.ref_code_type ct
LEFT JOIN gold.ref_code_value cv ON ct.code_type_id = cv.code_type_id
LEFT JOIN gold.ref_code_source_mapping sm ON ct.code_type_id = sm.code_type_id
LEFT JOIN gold.code_mapping_override ov ON ct.code_type_id = ov.code_type_id
GROUP BY ct.code_type_id, ct.code_type_name
ORDER BY ct.code_type_id;

-- =====================================================
-- FUNCTION: Get effective code mapping with override
-- Used by data processing pipeline during Gold transformation
-- =====================================================

CREATE OR REPLACE FUNCTION gold.get_effective_code_mapping(
    p_code_type VARCHAR(50),
    p_message_format VARCHAR(50),
    p_source_code VARCHAR(35),
    p_as_of_date DATE DEFAULT CURRENT_DATE
) RETURNS VARCHAR(35) AS $$
DECLARE
    v_result VARCHAR(35);
BEGIN
    -- First check for active, approved override effective on the given date
    SELECT override_cdm_code_value INTO v_result
    FROM gold.code_mapping_override
    WHERE code_type_id = p_code_type
      AND message_format = p_message_format
      AND source_code_value = p_source_code
      AND override_type = 'SOURCE_MAPPING'
      AND is_active = TRUE
      AND status = 'APPROVED'
      AND p_as_of_date >= effective_from
      AND (effective_to IS NULL OR p_as_of_date <= effective_to)
    ORDER BY effective_from DESC  -- Most recent effective override
    LIMIT 1;

    -- If no override, get standard mapping effective on the given date
    IF v_result IS NULL THEN
        SELECT cdm_code_value INTO v_result
        FROM gold.ref_code_source_mapping
        WHERE code_type_id = p_code_type
          AND message_format = p_message_format
          AND source_code_value = p_source_code
          AND is_active = TRUE
          AND p_as_of_date >= effective_start_date
          AND (effective_end_date IS NULL OR p_as_of_date <= effective_end_date)
        ORDER BY effective_start_date DESC  -- Most recent effective mapping
        LIMIT 1;
    END IF;

    -- If still no mapping, return original value (pass-through)
    IF v_result IS NULL THEN
        v_result := p_source_code;
    END IF;

    RETURN v_result;
END;
$$ LANGUAGE plpgsql STABLE;

-- =====================================================
-- FUNCTION: Get effective code mapping with full details
-- Returns more information for auditing/logging purposes
-- =====================================================

CREATE OR REPLACE FUNCTION gold.get_effective_code_mapping_details(
    p_code_type VARCHAR(50),
    p_message_format VARCHAR(50),
    p_source_code VARCHAR(35),
    p_as_of_date DATE DEFAULT CURRENT_DATE
) RETURNS TABLE (
    cdm_code_value VARCHAR(35),
    cdm_description VARCHAR(500),
    mapping_confidence VARCHAR(20),
    is_overridden BOOLEAN,
    override_id INT,
    effective_from DATE,
    effective_to DATE,
    mapping_source VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(ov.override_cdm_code_value, sm.cdm_code_value) AS cdm_code_value,
        COALESCE(ov.override_cdm_code_value, sm.cdm_code_description) AS cdm_description,
        sm.mapping_confidence,
        CASE WHEN ov.override_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_overridden,
        ov.override_id,
        COALESCE(ov.effective_from, sm.effective_start_date) AS effective_from,
        COALESCE(ov.effective_to, sm.effective_end_date) AS effective_to,
        CASE WHEN ov.override_id IS NOT NULL THEN 'OVERRIDE' ELSE 'BASE_MAPPING' END AS mapping_source
    FROM gold.ref_code_source_mapping sm
    LEFT JOIN gold.code_mapping_override ov ON
        ov.code_type_id = sm.code_type_id
        AND ov.message_format = sm.message_format
        AND ov.source_code_value = sm.source_code_value
        AND ov.override_type = 'SOURCE_MAPPING'
        AND ov.is_active = TRUE
        AND ov.status = 'APPROVED'
        AND p_as_of_date >= ov.effective_from
        AND (ov.effective_to IS NULL OR p_as_of_date <= ov.effective_to)
    WHERE sm.code_type_id = p_code_type
      AND sm.message_format = p_message_format
      AND sm.source_code_value = p_source_code
      AND sm.is_active = TRUE
      AND p_as_of_date >= sm.effective_start_date
      AND (sm.effective_end_date IS NULL OR p_as_of_date <= sm.effective_end_date)
    ORDER BY COALESCE(ov.effective_from, sm.effective_start_date) DESC
    LIMIT 1;

    -- If no result, return pass-through
    IF NOT FOUND THEN
        RETURN QUERY SELECT
            p_source_code::VARCHAR(35) AS cdm_code_value,
            'No mapping found - pass-through'::VARCHAR(500) AS cdm_description,
            'NONE'::VARCHAR(20) AS mapping_confidence,
            FALSE AS is_overridden,
            NULL::INT AS override_id,
            NULL::DATE AS effective_from,
            NULL::DATE AS effective_to,
            'PASS_THROUGH'::VARCHAR(50) AS mapping_source;
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;

-- =====================================================
-- FUNCTION: Batch get all effective mappings for a message format
-- Used by pipeline to load all mappings at once for performance
-- =====================================================

CREATE OR REPLACE FUNCTION gold.get_all_effective_mappings_for_format(
    p_message_format VARCHAR(50),
    p_as_of_date DATE DEFAULT CURRENT_DATE
) RETURNS TABLE (
    code_type_id VARCHAR(50),
    source_code_value VARCHAR(35),
    cdm_code_value VARCHAR(35),
    mapping_confidence VARCHAR(20),
    is_overridden BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (sm.code_type_id, sm.source_code_value)
        sm.code_type_id,
        sm.source_code_value,
        COALESCE(ov.override_cdm_code_value, sm.cdm_code_value) AS cdm_code_value,
        sm.mapping_confidence,
        CASE WHEN ov.override_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_overridden
    FROM gold.ref_code_source_mapping sm
    LEFT JOIN gold.code_mapping_override ov ON
        ov.code_type_id = sm.code_type_id
        AND ov.message_format = sm.message_format
        AND ov.source_code_value = sm.source_code_value
        AND ov.override_type = 'SOURCE_MAPPING'
        AND ov.is_active = TRUE
        AND ov.status = 'APPROVED'
        AND p_as_of_date >= ov.effective_from
        AND (ov.effective_to IS NULL OR p_as_of_date <= ov.effective_to)
    WHERE sm.message_format = p_message_format
      AND sm.is_active = TRUE
      AND p_as_of_date >= sm.effective_start_date
      AND (sm.effective_end_date IS NULL OR p_as_of_date <= sm.effective_end_date)
    ORDER BY sm.code_type_id, sm.source_code_value, COALESCE(ov.effective_from, sm.effective_start_date) DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- =====================================================
-- Verify tables created
-- =====================================================
SELECT 'gold' as schema, table_name, 'TABLE' as type
FROM information_schema.tables
WHERE table_schema = 'gold'
AND table_name LIKE 'ref_%'
ORDER BY table_name;
