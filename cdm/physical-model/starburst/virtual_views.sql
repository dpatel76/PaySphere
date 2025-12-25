-- GPS Payments CDM - Starburst Virtual Views
-- Version: 1.0.0
-- Date: 2024-12-20
-- Purpose: Federated Query Layer for Cross-Platform Analytics

-- =============================================================================
-- STARBURST GALAXY / TRINO VIRTUAL VIEWS
-- Federated access across Databricks, Oracle, and external sources
-- =============================================================================

-- =============================================================================
-- 1. CATALOG CONFIGURATION
-- =============================================================================

-- Databricks Delta Lake Catalog
-- CREATE CATALOG databricks_cdm USING delta WITH (
--     "metastore-uri" = "thrift://databricks-metastore:9083",
--     "delta.unity-catalog-enabled" = "true"
-- );

-- Oracle Exadata Catalog (Source Systems)
-- CREATE CATALOG oracle_source USING oracle WITH (
--     "connection-url" = "jdbc:oracle:thin:@//oracle-host:1521/PAYDB",
--     "connection-user" = "${ORACLE_USER}",
--     "connection-password" = "${ORACLE_PASSWORD}"
-- );

-- =============================================================================
-- 2. FEDERATED PAYMENT VIEWS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Unified Payment View - Cross-platform payment data
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW starburst.cdm.v_unified_payments AS
SELECT
    -- From Databricks Silver
    p.payment_id,
    p.payment_type,
    p.scheme_code,
    p.status,
    p.direction,
    p.cross_border_flag,
    p.created_at,

    -- Payment Instruction
    pi.end_to_end_id,
    pi.uetr,
    pi.instructed_amount,
    pi.instructed_currency,
    pi.requested_execution_date,
    pi.settlement_date,
    pi.purpose,
    pi.charge_bearer,

    -- Debtor
    db.party_id AS debtor_party_id,
    db.name AS debtor_name,
    db.party_type AS debtor_type,
    dba.account_number AS debtor_account,
    dbfi.bic AS debtor_agent_bic,

    -- Creditor
    cr.party_id AS creditor_party_id,
    cr.name AS creditor_name,
    cr.party_type AS creditor_type,
    cra.account_number AS creditor_account,
    crfi.bic AS creditor_agent_bic,

    -- Compliance
    pi.sanctions_screening_status,
    pi.fraud_score,
    pi.aml_risk_rating,

    -- Source & Lineage
    p.source_system,
    p.ingestion_timestamp,
    p.data_quality_score,

    -- Partitioning
    p.partition_year,
    p.partition_month,
    p.region

FROM databricks_cdm.gps_cdm.silver.payment p
JOIN databricks_cdm.gps_cdm.silver.payment_instruction pi
    ON p.instruction_id = pi.instruction_id
LEFT JOIN databricks_cdm.gps_cdm.silver.party db
    ON pi.debtor_id = db.party_id AND db.is_current = TRUE
LEFT JOIN databricks_cdm.gps_cdm.silver.party cr
    ON pi.creditor_id = cr.party_id AND cr.is_current = TRUE
LEFT JOIN databricks_cdm.gps_cdm.silver.account dba
    ON pi.debtor_account_id = dba.account_id AND dba.is_current = TRUE
LEFT JOIN databricks_cdm.gps_cdm.silver.account cra
    ON pi.creditor_account_id = cra.account_id AND cra.is_current = TRUE
LEFT JOIN databricks_cdm.gps_cdm.silver.financial_institution dbfi
    ON pi.debtor_agent_id = dbfi.fi_id AND dbfi.is_current = TRUE
LEFT JOIN databricks_cdm.gps_cdm.silver.financial_institution crfi
    ON pi.creditor_agent_id = crfi.fi_id AND crfi.is_current = TRUE
WHERE p.is_current = TRUE;

-- -----------------------------------------------------------------------------
-- Real-time Payment Status (joins with source system)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW starburst.cdm.v_payment_status_realtime AS
SELECT
    p.payment_id,
    p.payment_type,
    p.scheme_code,
    p.status AS cdm_status,
    src.current_status AS source_status,
    src.last_status_update AS source_status_time,
    CASE
        WHEN p.status != src.current_status THEN 'SYNC_PENDING'
        ELSE 'IN_SYNC'
    END AS sync_status,
    pi.instructed_amount,
    pi.instructed_currency,
    p.created_at,
    CURRENT_TIMESTAMP - p.created_at AS age

FROM databricks_cdm.gps_cdm.silver.payment p
JOIN databricks_cdm.gps_cdm.silver.payment_instruction pi
    ON p.instruction_id = pi.instruction_id
LEFT JOIN oracle_source.payments.payment_status src
    ON p.source_system_record_id = src.payment_ref
WHERE p.is_current = TRUE
  AND p.status NOT IN ('completed', 'settled', 'cancelled', 'rejected', 'failed');

-- =============================================================================
-- 3. FEDERATED PARTY VIEWS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Unified Party View with KYC data from source
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW starburst.cdm.v_unified_parties AS
SELECT
    -- CDM Party Data
    p.party_id,
    p.party_type,
    p.name,
    p.given_name,
    p.family_name,
    p.date_of_birth,
    p.nationality,
    p.tax_id,
    p.tax_id_type,

    -- Risk & Compliance
    p.pep_flag,
    p.risk_rating,
    p.sanctions_screening_status,

    -- FATCA/CRS
    p.fatca_classification,
    p.crs_reportable,

    -- KYC from Source System
    kyc.kyc_status,
    kyc.kyc_date,
    kyc.next_review_date,
    kyc.risk_assessment_score,
    kyc.onboarding_date,

    -- Address
    p.address,

    -- Metadata
    p.source_system,
    p.valid_from,
    p.valid_to,
    p.is_current

FROM databricks_cdm.gps_cdm.silver.party p
LEFT JOIN oracle_source.customer.kyc_profile kyc
    ON p.source_system_record_id = kyc.customer_id
WHERE p.is_current = TRUE;

-- =============================================================================
-- 4. FEDERATED ACCOUNT VIEWS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Unified Account View with real-time balance
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW starburst.cdm.v_unified_accounts AS
SELECT
    -- CDM Account Data
    a.account_id,
    a.account_number,
    a.iban,
    a.account_type,
    a.currency,
    a.account_status,

    -- CDM Balance (as of last refresh)
    a.current_balance AS cdm_balance,
    a.available_balance AS cdm_available_balance,

    -- Real-time Balance from Source
    bal.ledger_balance AS realtime_ledger_balance,
    bal.available_balance AS realtime_available_balance,
    bal.as_of_timestamp AS balance_timestamp,

    -- Owner
    o.name AS primary_owner_name,
    o.party_type AS primary_owner_type,

    -- Financial Institution
    fi.institution_name,
    fi.bic,
    fi.country AS fi_country,

    -- Tax Reporting
    a.fatca_status,
    a.crs_reportable_account,

    -- Metadata
    a.open_date,
    a.source_system

FROM databricks_cdm.gps_cdm.silver.account a
LEFT JOIN databricks_cdm.gps_cdm.silver.account_owner ao
    ON a.account_id = ao.account_id
    AND ao.ownership_type = 'PRIMARY'
    AND ao.is_current = TRUE
LEFT JOIN databricks_cdm.gps_cdm.silver.party o
    ON ao.party_id = o.party_id
    AND o.is_current = TRUE
LEFT JOIN databricks_cdm.gps_cdm.silver.financial_institution fi
    ON a.financial_institution_id = fi.fi_id
    AND fi.is_current = TRUE
LEFT JOIN oracle_source.accounts.realtime_balance bal
    ON a.source_system_record_id = bal.account_ref
WHERE a.is_current = TRUE;

-- =============================================================================
-- 5. REGULATORY REPORTING VIEWS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- CTR Eligible Transactions
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW starburst.cdm.v_ctr_eligible AS
SELECT
    p.payment_id,
    pi.end_to_end_id,
    p.created_at AS transaction_date,
    pi.instructed_amount,
    pi.instructed_currency,

    -- Debtor Information
    db.party_id AS person_involved_id,
    db.name AS person_name,
    db.date_of_birth,
    db.tax_id AS ssn_ein,
    db.occupation,
    db.naics_code,
    db.address,

    -- Account Information
    dba.account_number,

    -- Filing Institution
    fi.institution_name AS filing_institution,
    fi.rssd_number,
    fi.tin_value AS fi_ein,

    -- Threshold Check
    CASE
        WHEN pi.instructed_currency = 'USD' AND pi.instructed_amount >= 10000 THEN TRUE
        WHEN pi.instructed_currency != 'USD' AND
             pi.instructed_amount * fx.rate >= 10000 THEN TRUE
        ELSE FALSE
    END AS over_threshold,

    p.source_system,
    p.partition_year,
    p.partition_month

FROM databricks_cdm.gps_cdm.silver.payment p
JOIN databricks_cdm.gps_cdm.silver.payment_instruction pi
    ON p.instruction_id = pi.instruction_id
JOIN databricks_cdm.gps_cdm.silver.party db
    ON pi.debtor_id = db.party_id AND db.is_current = TRUE
LEFT JOIN databricks_cdm.gps_cdm.silver.account dba
    ON pi.debtor_account_id = dba.account_id AND dba.is_current = TRUE
LEFT JOIN databricks_cdm.gps_cdm.silver.financial_institution fi
    ON pi.debtor_agent_id = fi.fi_id AND fi.is_current = TRUE
LEFT JOIN databricks_cdm.gps_cdm.reference.fx_rates fx
    ON pi.instructed_currency = fx.currency
    AND DATE(p.created_at) = fx.rate_date
WHERE p.is_current = TRUE
  AND p.status = 'completed'
  AND p.region = 'US';

-- -----------------------------------------------------------------------------
-- IFTI Eligible Transactions (AUSTRAC)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW starburst.cdm.v_ifti_eligible AS
SELECT
    p.payment_id,
    pi.end_to_end_id,
    p.created_at AS transfer_date,
    pi.instructed_amount,
    pi.instructed_currency,

    -- Ordering Customer
    db.name AS ordering_customer_name,
    db.address AS ordering_customer_address,
    db.date_of_birth AS ordering_customer_dob,

    -- Ordering Institution
    dbfi.institution_name AS ordering_institution,
    dbfi.bic AS ordering_institution_bic,
    dbfi.country AS ordering_country,

    -- Beneficiary
    cr.name AS beneficiary_name,
    cr.address AS beneficiary_address,

    -- Beneficiary Institution
    crfi.institution_name AS beneficiary_institution,
    crfi.bic AS beneficiary_institution_bic,
    crfi.country AS beneficiary_country,

    -- Direction
    CASE
        WHEN dbfi.country = 'AU' AND crfi.country != 'AU' THEN 'OUTWARD'
        WHEN dbfi.country != 'AU' AND crfi.country = 'AU' THEN 'INWARD'
        ELSE 'UNKNOWN'
    END AS transfer_direction,

    p.source_system

FROM databricks_cdm.gps_cdm.silver.payment p
JOIN databricks_cdm.gps_cdm.silver.payment_instruction pi
    ON p.instruction_id = pi.instruction_id
JOIN databricks_cdm.gps_cdm.silver.party db
    ON pi.debtor_id = db.party_id AND db.is_current = TRUE
JOIN databricks_cdm.gps_cdm.silver.party cr
    ON pi.creditor_id = cr.party_id AND cr.is_current = TRUE
LEFT JOIN databricks_cdm.gps_cdm.silver.financial_institution dbfi
    ON pi.debtor_agent_id = dbfi.fi_id AND dbfi.is_current = TRUE
LEFT JOIN databricks_cdm.gps_cdm.silver.financial_institution crfi
    ON pi.creditor_agent_id = crfi.fi_id AND crfi.is_current = TRUE
WHERE p.is_current = TRUE
  AND p.status = 'completed'
  AND p.cross_border_flag = TRUE
  AND (dbfi.country = 'AU' OR crfi.country = 'AU');

-- =============================================================================
-- 6. ANALYTICS VIEWS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Payment Volume by Corridor
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW starburst.cdm.v_corridor_volume AS
SELECT
    DATE(p.created_at) AS transaction_date,
    dbfi.country AS origin_country,
    crfi.country AS destination_country,
    p.payment_type,
    p.scheme_code,
    COUNT(*) AS transaction_count,
    SUM(pi.instructed_amount) AS total_amount,
    AVG(pi.instructed_amount) AS avg_amount,
    pi.instructed_currency AS currency

FROM databricks_cdm.gps_cdm.silver.payment p
JOIN databricks_cdm.gps_cdm.silver.payment_instruction pi
    ON p.instruction_id = pi.instruction_id
LEFT JOIN databricks_cdm.gps_cdm.silver.financial_institution dbfi
    ON pi.debtor_agent_id = dbfi.fi_id AND dbfi.is_current = TRUE
LEFT JOIN databricks_cdm.gps_cdm.silver.financial_institution crfi
    ON pi.creditor_agent_id = crfi.fi_id AND crfi.is_current = TRUE
WHERE p.is_current = TRUE
  AND p.cross_border_flag = TRUE
GROUP BY
    DATE(p.created_at),
    dbfi.country,
    crfi.country,
    p.payment_type,
    p.scheme_code,
    pi.instructed_currency;

-- -----------------------------------------------------------------------------
-- Daily Payment Summary by Region
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW starburst.cdm.v_daily_summary AS
SELECT
    DATE(p.created_at) AS summary_date,
    p.region,
    p.payment_type,
    p.scheme_code,
    p.status,
    COUNT(*) AS payment_count,
    SUM(pi.instructed_amount) AS total_amount,
    AVG(pi.instructed_amount) AS avg_amount,
    MIN(pi.instructed_amount) AS min_amount,
    MAX(pi.instructed_amount) AS max_amount

FROM databricks_cdm.gps_cdm.silver.payment p
JOIN databricks_cdm.gps_cdm.silver.payment_instruction pi
    ON p.instruction_id = pi.instruction_id
WHERE p.is_current = TRUE
GROUP BY
    DATE(p.created_at),
    p.region,
    p.payment_type,
    p.scheme_code,
    p.status;

-- =============================================================================
-- 7. DATA QUALITY VIEWS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Data Quality Dashboard View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW starburst.cdm.v_data_quality_summary AS
SELECT
    'payment' AS entity_type,
    p.source_system,
    p.partition_year,
    p.partition_month,
    COUNT(*) AS record_count,
    AVG(p.data_quality_score) AS avg_dq_score,
    COUNT(CASE WHEN p.data_quality_score < 80 THEN 1 END) AS low_quality_count,
    COUNT(CASE WHEN CARDINALITY(pi.data_quality_issues) > 0 THEN 1 END) AS records_with_issues

FROM databricks_cdm.gps_cdm.silver.payment p
JOIN databricks_cdm.gps_cdm.silver.payment_instruction pi
    ON p.instruction_id = pi.instruction_id
WHERE p.is_current = TRUE
GROUP BY
    p.source_system,
    p.partition_year,
    p.partition_month

UNION ALL

SELECT
    'party' AS entity_type,
    source_system,
    partition_year,
    NULL AS partition_month,
    COUNT(*) AS record_count,
    NULL AS avg_dq_score,
    NULL AS low_quality_count,
    NULL AS records_with_issues

FROM databricks_cdm.gps_cdm.silver.party
WHERE is_current = TRUE
GROUP BY source_system, partition_year;

-- =============================================================================
-- 8. LINEAGE VIEWS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Field Lineage Summary
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW starburst.cdm.v_field_lineage AS
SELECT
    lm.entity_type,
    lm.field_name,
    lm.source_system,
    lm.source_table,
    lm.source_field,
    lm.transformation_type,
    lm.transformation_logic,
    lm.confidence_score,
    lm.effective_from,
    lm.effective_to

FROM databricks_cdm.gps_cdm.silver.lineage_metadata lm
WHERE lm.effective_to IS NULL
ORDER BY lm.entity_type, lm.field_name;
