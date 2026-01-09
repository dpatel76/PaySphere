-- Add FK columns to ISO 20022 semantic Gold tables for normalized reference data
-- This maintains the CDM design pattern of deduplicated parties, accounts, and financial institutions

-- =====================================================
-- cdm_pacs_fi_customer_credit_transfer (pacs.008)
-- =====================================================
ALTER TABLE gold.cdm_pacs_fi_customer_credit_transfer
ADD COLUMN IF NOT EXISTS debtor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS creditor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS ultimate_debtor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS ultimate_creditor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS debtor_account_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS creditor_account_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS debtor_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS creditor_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS instructing_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS instructed_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS intermediary_agent1_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS intermediary_agent2_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS intermediary_agent3_fi_id VARCHAR(50);

COMMENT ON COLUMN gold.cdm_pacs_fi_customer_credit_transfer.debtor_party_id IS 'FK to cdm_party for debtor';
COMMENT ON COLUMN gold.cdm_pacs_fi_customer_credit_transfer.creditor_party_id IS 'FK to cdm_party for creditor';
COMMENT ON COLUMN gold.cdm_pacs_fi_customer_credit_transfer.debtor_account_id IS 'FK to cdm_account for debtor account';
COMMENT ON COLUMN gold.cdm_pacs_fi_customer_credit_transfer.creditor_account_id IS 'FK to cdm_account for creditor account';
COMMENT ON COLUMN gold.cdm_pacs_fi_customer_credit_transfer.debtor_agent_fi_id IS 'FK to cdm_financial_institution for debtor agent';
COMMENT ON COLUMN gold.cdm_pacs_fi_customer_credit_transfer.creditor_agent_fi_id IS 'FK to cdm_financial_institution for creditor agent';

-- =====================================================
-- cdm_pacs_fi_credit_transfer (pacs.009)
-- =====================================================
ALTER TABLE gold.cdm_pacs_fi_credit_transfer
ADD COLUMN IF NOT EXISTS debtor_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS creditor_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS debtor_account_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS creditor_account_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS instructing_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS instructed_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS intermediary_agent1_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS intermediary_agent2_fi_id VARCHAR(50);

COMMENT ON COLUMN gold.cdm_pacs_fi_credit_transfer.debtor_fi_id IS 'FK to cdm_financial_institution for debtor FI';
COMMENT ON COLUMN gold.cdm_pacs_fi_credit_transfer.creditor_fi_id IS 'FK to cdm_financial_institution for creditor FI';

-- =====================================================
-- cdm_pacs_fi_payment_status_report (pacs.002)
-- =====================================================
ALTER TABLE gold.cdm_pacs_fi_payment_status_report
ADD COLUMN IF NOT EXISTS original_debtor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS original_creditor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS original_debtor_account_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS original_creditor_account_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS original_debtor_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS original_creditor_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS instructing_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS instructed_agent_fi_id VARCHAR(50);

COMMENT ON COLUMN gold.cdm_pacs_fi_payment_status_report.original_debtor_party_id IS 'FK to cdm_party for original debtor';
COMMENT ON COLUMN gold.cdm_pacs_fi_payment_status_report.original_creditor_party_id IS 'FK to cdm_party for original creditor';

-- =====================================================
-- cdm_pacs_payment_return (pacs.004)
-- =====================================================
ALTER TABLE gold.cdm_pacs_payment_return
ADD COLUMN IF NOT EXISTS return_debtor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS return_creditor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS original_debtor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS original_creditor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS return_debtor_account_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS return_creditor_account_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS original_debtor_account_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS original_creditor_account_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS return_debtor_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS return_creditor_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS original_debtor_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS original_creditor_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS instructing_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS instructed_agent_fi_id VARCHAR(50);

COMMENT ON COLUMN gold.cdm_pacs_payment_return.return_debtor_party_id IS 'FK to cdm_party for return debtor';
COMMENT ON COLUMN gold.cdm_pacs_payment_return.original_debtor_party_id IS 'FK to cdm_party for original debtor';

-- =====================================================
-- cdm_pain_customer_credit_transfer_initiation (pain.001)
-- =====================================================
ALTER TABLE gold.cdm_pain_customer_credit_transfer_initiation
ADD COLUMN IF NOT EXISTS initiating_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS debtor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS creditor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS ultimate_debtor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS ultimate_creditor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS debtor_account_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS creditor_account_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS debtor_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS creditor_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS intermediary_agent1_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS intermediary_agent2_fi_id VARCHAR(50);

COMMENT ON COLUMN gold.cdm_pain_customer_credit_transfer_initiation.initiating_party_id IS 'FK to cdm_party for initiating party';
COMMENT ON COLUMN gold.cdm_pain_customer_credit_transfer_initiation.debtor_party_id IS 'FK to cdm_party for debtor';
COMMENT ON COLUMN gold.cdm_pain_customer_credit_transfer_initiation.creditor_party_id IS 'FK to cdm_party for creditor';

-- =====================================================
-- cdm_pain_customer_direct_debit_initiation (pain.008)
-- =====================================================
ALTER TABLE gold.cdm_pain_customer_direct_debit_initiation
ADD COLUMN IF NOT EXISTS initiating_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS debtor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS creditor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS ultimate_debtor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS ultimate_creditor_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS debtor_account_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS creditor_account_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS debtor_agent_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS creditor_agent_fi_id VARCHAR(50);

COMMENT ON COLUMN gold.cdm_pain_customer_direct_debit_initiation.initiating_party_id IS 'FK to cdm_party for initiating party';
COMMENT ON COLUMN gold.cdm_pain_customer_direct_debit_initiation.debtor_party_id IS 'FK to cdm_party for debtor';

-- =====================================================
-- cdm_camt_bank_to_customer_statement (camt.053)
-- =====================================================
ALTER TABLE gold.cdm_camt_bank_to_customer_statement
ADD COLUMN IF NOT EXISTS account_owner_party_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS account_servicer_fi_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS account_id VARCHAR(50);

COMMENT ON COLUMN gold.cdm_camt_bank_to_customer_statement.account_owner_party_id IS 'FK to cdm_party for account owner';
COMMENT ON COLUMN gold.cdm_camt_bank_to_customer_statement.account_servicer_fi_id IS 'FK to cdm_financial_institution for servicer';
COMMENT ON COLUMN gold.cdm_camt_bank_to_customer_statement.account_id IS 'FK to cdm_account';

-- =====================================================
-- Create indexes for FK lookups
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_pacs008_debtor_party ON gold.cdm_pacs_fi_customer_credit_transfer(debtor_party_id);
CREATE INDEX IF NOT EXISTS idx_pacs008_creditor_party ON gold.cdm_pacs_fi_customer_credit_transfer(creditor_party_id);
CREATE INDEX IF NOT EXISTS idx_pacs008_debtor_account ON gold.cdm_pacs_fi_customer_credit_transfer(debtor_account_id);
CREATE INDEX IF NOT EXISTS idx_pacs008_creditor_account ON gold.cdm_pacs_fi_customer_credit_transfer(creditor_account_id);
CREATE INDEX IF NOT EXISTS idx_pacs008_debtor_agent ON gold.cdm_pacs_fi_customer_credit_transfer(debtor_agent_fi_id);
CREATE INDEX IF NOT EXISTS idx_pacs008_creditor_agent ON gold.cdm_pacs_fi_customer_credit_transfer(creditor_agent_fi_id);

CREATE INDEX IF NOT EXISTS idx_pacs009_debtor_fi ON gold.cdm_pacs_fi_credit_transfer(debtor_fi_id);
CREATE INDEX IF NOT EXISTS idx_pacs009_creditor_fi ON gold.cdm_pacs_fi_credit_transfer(creditor_fi_id);

CREATE INDEX IF NOT EXISTS idx_pain001_debtor_party ON gold.cdm_pain_customer_credit_transfer_initiation(debtor_party_id);
CREATE INDEX IF NOT EXISTS idx_pain001_creditor_party ON gold.cdm_pain_customer_credit_transfer_initiation(creditor_party_id);

CREATE INDEX IF NOT EXISTS idx_pain008_debtor_party ON gold.cdm_pain_customer_direct_debit_initiation(debtor_party_id);
CREATE INDEX IF NOT EXISTS idx_pain008_creditor_party ON gold.cdm_pain_customer_direct_debit_initiation(creditor_party_id);
