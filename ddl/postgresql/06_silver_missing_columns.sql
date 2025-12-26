-- GPS CDM - Silver Layer Missing Columns
-- =======================================
-- This script adds columns that were identified as MISSING during the field coverage audit.
-- 117 fields across 4 message formats were not being captured.
--
-- Run this after the base Silver tables are created.

-- ============================================================================
-- PAIN.001 MISSING COLUMNS (18 fields)
-- ============================================================================
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS initiating_party_id_type VARCHAR(35);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS initiating_party_country VARCHAR(2);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS service_level VARCHAR(35);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS local_instrument VARCHAR(35);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS category_purpose VARCHAR(35);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS debtor_country_sub_division VARCHAR(35);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS debtor_account_type VARCHAR(35);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS debtor_agent_country VARCHAR(2);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS exchange_rate DECIMAL(18,10);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS creditor_country_sub_division VARCHAR(35);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS creditor_account_type VARCHAR(35);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS creditor_agent_country VARCHAR(2);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS ultimate_debtor_name VARCHAR(140);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS ultimate_debtor_id VARCHAR(35);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS ultimate_debtor_id_type VARCHAR(35);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS ultimate_creditor_name VARCHAR(140);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS ultimate_creditor_id VARCHAR(35);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS ultimate_creditor_id_type VARCHAR(35);

-- ============================================================================
-- MT103 MISSING COLUMNS (19 fields)
-- ============================================================================
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS transaction_reference_number VARCHAR(16);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS instruction_code TEXT[];  -- Array of instruction codes
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS ordering_customer_party_id VARCHAR(35);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS ordering_customer_national_id VARCHAR(35);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS ordering_institution_name VARCHAR(140);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS ordering_institution_clearing_code VARCHAR(35);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS ordering_institution_country VARCHAR(2);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS senders_correspondent_account VARCHAR(35);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS senders_correspondent_name VARCHAR(140);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS receivers_correspondent_account VARCHAR(35);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS receivers_correspondent_name VARCHAR(140);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS intermediary_institution_bic VARCHAR(11);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS intermediary_institution_name VARCHAR(140);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS intermediary_institution_country VARCHAR(2);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS account_with_institution_name VARCHAR(140);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS account_with_institution_country VARCHAR(2);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS beneficiary_party_id VARCHAR(35);
ALTER TABLE silver.stg_mt103 ADD COLUMN IF NOT EXISTS sender_to_receiver_information JSONB;

-- ============================================================================
-- PACS.008 MISSING COLUMNS (39 fields)
-- ============================================================================
-- Instructing/Instructed Agent details
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS instructing_agent_name VARCHAR(140);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS instructing_agent_lei VARCHAR(20);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS instructing_agent_country VARCHAR(2);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS instructed_agent_name VARCHAR(140);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS instructed_agent_lei VARCHAR(20);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS instructed_agent_country VARCHAR(2);

-- Payment Type Information
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS instruction_priority VARCHAR(10);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS clearing_channel VARCHAR(10);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS service_level VARCHAR(35);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS local_instrument VARCHAR(35);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS category_purpose VARCHAR(35);

-- Debtor details (currently only name and country)
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS debtor_street_name VARCHAR(70);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS debtor_building_number VARCHAR(50);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS debtor_postal_code VARCHAR(16);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS debtor_town_name VARCHAR(35);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS debtor_country_sub_division VARCHAR(35);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS debtor_id VARCHAR(35);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS debtor_id_type VARCHAR(35);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS debtor_account_currency VARCHAR(3);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS debtor_account_type VARCHAR(35);

-- Debtor Agent details
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS debtor_agent_name VARCHAR(140);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS debtor_agent_clearing_member_id VARCHAR(35);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS debtor_agent_lei VARCHAR(20);

-- Creditor Agent details
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS creditor_agent_name VARCHAR(140);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS creditor_agent_clearing_member_id VARCHAR(35);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS creditor_agent_lei VARCHAR(20);

-- Creditor details (currently only name and country)
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS creditor_street_name VARCHAR(70);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS creditor_building_number VARCHAR(50);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS creditor_postal_code VARCHAR(16);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS creditor_town_name VARCHAR(35);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS creditor_country_sub_division VARCHAR(35);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS creditor_id VARCHAR(35);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS creditor_id_type VARCHAR(35);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS creditor_account_currency VARCHAR(3);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS creditor_account_type VARCHAR(35);

-- Ultimate parties (id and idType missing)
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS ultimate_debtor_id VARCHAR(35);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS ultimate_debtor_id_type VARCHAR(35);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS ultimate_creditor_id VARCHAR(35);
ALTER TABLE silver.stg_pacs008 ADD COLUMN IF NOT EXISTS ultimate_creditor_id_type VARCHAR(35);

-- ============================================================================
-- FEDWIRE MISSING COLUMNS (41 fields)
-- ============================================================================
-- Currency and amount details
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS currency VARCHAR(3);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS instructed_amount DECIMAL(18,4);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS instructed_currency VARCHAR(3);

-- Message routing
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS input_cycle_date DATE;
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS input_sequence_number VARCHAR(10);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS input_source VARCHAR(10);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS previous_message_id VARCHAR(35);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS beneficiary_reference VARCHAR(16);

-- Sender FI full details
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS sender_name VARCHAR(140);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS sender_bic VARCHAR(11);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS sender_lei VARCHAR(20);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS sender_address_line1 VARCHAR(35);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS sender_address_line2 VARCHAR(35);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS sender_city VARCHAR(35);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS sender_state VARCHAR(2);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS sender_zip_code VARCHAR(10);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS sender_country VARCHAR(2);

-- Receiver FI full details
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS receiver_name VARCHAR(140);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS receiver_bic VARCHAR(11);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS receiver_lei VARCHAR(20);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS receiver_address_line1 VARCHAR(35);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS receiver_address_line2 VARCHAR(35);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS receiver_city VARCHAR(35);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS receiver_state VARCHAR(2);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS receiver_zip_code VARCHAR(10);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS receiver_country VARCHAR(2);

-- Originator additional details
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS originator_account_number VARCHAR(35);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS originator_id_type VARCHAR(10);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS originator_city VARCHAR(35);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS originator_state VARCHAR(2);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS originator_zip_code VARCHAR(10);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS originator_country VARCHAR(2);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS originator_option_f JSONB;

-- Beneficiary additional details
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS beneficiary_account_number VARCHAR(35);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS beneficiary_id_type VARCHAR(10);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS beneficiary_city VARCHAR(35);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS beneficiary_state VARCHAR(2);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS beneficiary_zip_code VARCHAR(10);
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS beneficiary_country VARCHAR(2);

-- Beneficiary Bank additional details
ALTER TABLE silver.stg_fedwire ADD COLUMN IF NOT EXISTS beneficiary_fi_bic VARCHAR(11);

-- Intermediary Bank full details (currently only id and name)
-- Already has intermediary_fi_id and intermediary_fi_name

-- ============================================================================
-- VERIFICATION
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE 'Silver layer missing columns added successfully.';
    RAISE NOTICE 'pain.001: Added 18 columns';
    RAISE NOTICE 'MT103: Added 18 columns';
    RAISE NOTICE 'pacs.008: Added 39 columns';
    RAISE NOTICE 'FEDWIRE: Added 41 columns';
    RAISE NOTICE 'TOTAL: 116 new columns';
END $$;
