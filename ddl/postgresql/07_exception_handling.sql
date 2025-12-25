-- ============================================================================
-- GPS CDM - Exception Handling, Data Quality & Reconciliation Schema
-- ============================================================================
-- This script creates tables and structures for:
-- 1. Processing exception tracking across all pipeline stages
-- 2. Data quality validation results and metrics
-- 3. Bronze-to-Gold reconciliation
-- 4. Status tracking columns on data tables
-- ============================================================================

-- ============================================================================
-- PART 1: STATUS COLUMNS ON DATA TABLES
-- ============================================================================

-- Bronze layer: Add status tracking
ALTER TABLE bronze.raw_payment_messages
    ADD COLUMN IF NOT EXISTS processing_status VARCHAR(20) DEFAULT 'PENDING';
ALTER TABLE bronze.raw_payment_messages
    ADD COLUMN IF NOT EXISTS processing_error TEXT;
ALTER TABLE bronze.raw_payment_messages
    ADD COLUMN IF NOT EXISTS processing_attempts INTEGER DEFAULT 0;
ALTER TABLE bronze.raw_payment_messages
    ADD COLUMN IF NOT EXISTS last_processed_at TIMESTAMP;
ALTER TABLE bronze.raw_payment_messages
    ADD COLUMN IF NOT EXISTS promoted_to_silver_at TIMESTAMP;
ALTER TABLE bronze.raw_payment_messages
    ADD COLUMN IF NOT EXISTS silver_stg_id VARCHAR(36);

-- Add check constraint for processing_status (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'bronze_processing_status_check'
    ) THEN
        ALTER TABLE bronze.raw_payment_messages
        ADD CONSTRAINT bronze_processing_status_check
        CHECK (processing_status IN ('PENDING', 'PROCESSING', 'PROCESSED', 'FAILED', 'SKIPPED', 'REPROCESSING'));
    END IF;
END $$;

-- Silver layer: Add status and DQ tracking
ALTER TABLE silver.stg_pain001
    ADD COLUMN IF NOT EXISTS processing_status VARCHAR(20) DEFAULT 'PENDING';
ALTER TABLE silver.stg_pain001
    ADD COLUMN IF NOT EXISTS processing_error TEXT;
ALTER TABLE silver.stg_pain001
    ADD COLUMN IF NOT EXISTS dq_status VARCHAR(20) DEFAULT 'NOT_VALIDATED';
ALTER TABLE silver.stg_pain001
    ADD COLUMN IF NOT EXISTS dq_score DECIMAL(5,2);
ALTER TABLE silver.stg_pain001
    ADD COLUMN IF NOT EXISTS dq_validated_at TIMESTAMP;
ALTER TABLE silver.stg_pain001
    ADD COLUMN IF NOT EXISTS promoted_to_gold_at TIMESTAMP;
ALTER TABLE silver.stg_pain001
    ADD COLUMN IF NOT EXISTS gold_instruction_id VARCHAR(36);

-- Add check constraints for silver
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'silver_processing_status_check'
    ) THEN
        ALTER TABLE silver.stg_pain001
        ADD CONSTRAINT silver_processing_status_check
        CHECK (processing_status IN ('PENDING', 'PROCESSING', 'PROCESSED', 'FAILED', 'SKIPPED', 'REPROCESSING'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'silver_dq_status_check'
    ) THEN
        ALTER TABLE silver.stg_pain001
        ADD CONSTRAINT silver_dq_status_check
        CHECK (dq_status IN ('NOT_VALIDATED', 'VALIDATING', 'PASSED', 'FAILED', 'WARNING'));
    END IF;
END $$;

-- Gold layer: Add DQ and reconciliation tracking
ALTER TABLE gold.cdm_payment_instruction
    ADD COLUMN IF NOT EXISTS dq_status VARCHAR(20) DEFAULT 'NOT_VALIDATED';
ALTER TABLE gold.cdm_payment_instruction
    ADD COLUMN IF NOT EXISTS dq_score DECIMAL(5,2);
ALTER TABLE gold.cdm_payment_instruction
    ADD COLUMN IF NOT EXISTS dq_validated_at TIMESTAMP;
ALTER TABLE gold.cdm_payment_instruction
    ADD COLUMN IF NOT EXISTS reconciliation_status VARCHAR(20) DEFAULT 'NOT_RECONCILED';
ALTER TABLE gold.cdm_payment_instruction
    ADD COLUMN IF NOT EXISTS reconciled_at TIMESTAMP;

-- Add check constraints for gold
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'gold_dq_status_check'
    ) THEN
        ALTER TABLE gold.cdm_payment_instruction
        ADD CONSTRAINT gold_dq_status_check
        CHECK (dq_status IN ('NOT_VALIDATED', 'VALIDATING', 'PASSED', 'FAILED', 'WARNING'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'gold_recon_status_check'
    ) THEN
        ALTER TABLE gold.cdm_payment_instruction
        ADD CONSTRAINT gold_recon_status_check
        CHECK (reconciliation_status IN ('NOT_RECONCILED', 'MATCHED', 'MISMATCHED', 'ORPHAN'));
    END IF;
END $$;

-- Create indexes for status queries
CREATE INDEX IF NOT EXISTS idx_bronze_processing_status ON bronze.raw_payment_messages(processing_status);
CREATE INDEX IF NOT EXISTS idx_silver_processing_status ON silver.stg_pain001(processing_status);
CREATE INDEX IF NOT EXISTS idx_silver_dq_status ON silver.stg_pain001(dq_status);
CREATE INDEX IF NOT EXISTS idx_gold_dq_status ON gold.cdm_payment_instruction(dq_status);
CREATE INDEX IF NOT EXISTS idx_gold_recon_status ON gold.cdm_payment_instruction(reconciliation_status);


-- ============================================================================
-- PART 2: PROCESSING EXCEPTIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS observability.obs_processing_exceptions (
    exception_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    batch_id VARCHAR(36) NOT NULL,
    pipeline_run_id VARCHAR(36),

    -- Source identification
    source_layer VARCHAR(20) NOT NULL,  -- bronze, silver, gold
    source_table VARCHAR(100) NOT NULL,
    source_record_id VARCHAR(36) NOT NULL,

    -- Target identification (where it failed to go)
    target_layer VARCHAR(20),
    target_table VARCHAR(100),

    -- Exception details
    exception_type VARCHAR(50) NOT NULL,
    exception_code VARCHAR(20),
    exception_message TEXT NOT NULL,
    exception_details JSONB,
    stack_trace TEXT,

    -- Affected field (for validation errors)
    field_name VARCHAR(100),
    field_value TEXT,
    expected_value TEXT,

    -- Severity and status
    severity VARCHAR(20) DEFAULT 'ERROR',
    status VARCHAR(20) DEFAULT 'NEW',
    resolution_notes TEXT,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP,

    -- Retry tracking
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    last_retry_at TIMESTAMP,
    next_retry_at TIMESTAMP,
    can_retry BOOLEAN DEFAULT true,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT exc_severity_check CHECK (severity IN ('WARNING', 'ERROR', 'CRITICAL')),
    CONSTRAINT exc_status_check CHECK (status IN ('NEW', 'ACKNOWLEDGED', 'IN_PROGRESS', 'RESOLVED', 'IGNORED', 'AUTO_RESOLVED'))
);

-- Exception type reference (for UI dropdowns)
COMMENT ON TABLE observability.obs_processing_exceptions IS 'Tracks all processing exceptions across the medallion pipeline';
COMMENT ON COLUMN observability.obs_processing_exceptions.exception_type IS
    'PARSE_ERROR, VALIDATION_ERROR, TRANSFORM_ERROR, DQ_FAILURE, MAPPING_ERROR, DB_ERROR, TIMEOUT, UNKNOWN';

-- Indexes for exception queries
CREATE INDEX IF NOT EXISTS idx_exc_batch ON observability.obs_processing_exceptions(batch_id);
CREATE INDEX IF NOT EXISTS idx_exc_source ON observability.obs_processing_exceptions(source_layer, source_table);
CREATE INDEX IF NOT EXISTS idx_exc_record ON observability.obs_processing_exceptions(source_record_id);
CREATE INDEX IF NOT EXISTS idx_exc_status ON observability.obs_processing_exceptions(status);
CREATE INDEX IF NOT EXISTS idx_exc_type ON observability.obs_processing_exceptions(exception_type);
CREATE INDEX IF NOT EXISTS idx_exc_severity ON observability.obs_processing_exceptions(severity);
CREATE INDEX IF NOT EXISTS idx_exc_created ON observability.obs_processing_exceptions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_exc_retry ON observability.obs_processing_exceptions(next_retry_at)
    WHERE status NOT IN ('RESOLVED', 'IGNORED') AND can_retry = true;


-- ============================================================================
-- PART 3: DATA QUALITY TABLES
-- ============================================================================

-- DQ Rules: Define validation rules
CREATE TABLE IF NOT EXISTS observability.obs_dq_rules (
    rule_id VARCHAR(50) PRIMARY KEY,
    rule_name VARCHAR(200) NOT NULL,
    rule_description TEXT,

    -- Scope
    layer VARCHAR(20) NOT NULL,  -- bronze, silver, gold
    table_name VARCHAR(100) NOT NULL,
    field_name VARCHAR(100),  -- NULL for record-level rules

    -- Rule definition
    rule_type VARCHAR(30) NOT NULL,  -- COMPLETENESS, VALIDITY, ACCURACY, CONSISTENCY, UNIQUENESS, TIMELINESS
    rule_expression TEXT NOT NULL,  -- SQL expression or Python expression
    expression_type VARCHAR(20) DEFAULT 'SQL',  -- SQL, PYTHON, REGEX

    -- Thresholds
    error_threshold DECIMAL(5,2),  -- Below this = FAIL
    warning_threshold DECIMAL(5,2),  -- Below this = WARNING

    -- Weighting
    weight DECIMAL(5,2) DEFAULT 1.0,

    -- Status
    is_active BOOLEAN DEFAULT true,
    is_blocking BOOLEAN DEFAULT false,  -- If true, stops pipeline on failure

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),

    CONSTRAINT dq_rule_type_check CHECK (rule_type IN (
        'COMPLETENESS', 'VALIDITY', 'ACCURACY', 'CONSISTENCY', 'UNIQUENESS', 'TIMELINESS', 'CUSTOM'
    ))
);

-- DQ Results: Per-record validation results
CREATE TABLE IF NOT EXISTS observability.obs_data_quality_results (
    dq_result_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    batch_id VARCHAR(36) NOT NULL,
    pipeline_run_id VARCHAR(36),

    -- Record identification
    layer VARCHAR(20) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(36) NOT NULL,

    -- Rule execution
    rule_id VARCHAR(50) NOT NULL,
    rule_name VARCHAR(200),
    rule_type VARCHAR(50),
    rule_expression TEXT,

    -- Result
    passed BOOLEAN NOT NULL,
    actual_value TEXT,
    expected_value TEXT,
    error_message TEXT,

    -- Scoring
    weight DECIMAL(5,2) DEFAULT 1.0,
    score DECIMAL(5,2),  -- 0-100

    -- Metadata
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DQ Metrics: Aggregated quality metrics
CREATE TABLE IF NOT EXISTS observability.obs_data_quality_metrics (
    metric_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    batch_id VARCHAR(36),
    pipeline_run_id VARCHAR(36),

    -- Scope
    layer VARCHAR(20) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    field_name VARCHAR(100),  -- NULL for table-level metrics

    -- Dimension scores (0-100)
    completeness_score DECIMAL(5,2),
    validity_score DECIMAL(5,2),
    accuracy_score DECIMAL(5,2),
    consistency_score DECIMAL(5,2),
    uniqueness_score DECIMAL(5,2),
    timeliness_score DECIMAL(5,2),

    -- Overall
    overall_score DECIMAL(5,2),
    overall_status VARCHAR(20),  -- PASSED, WARNING, FAILED

    -- Counts
    total_records INTEGER,
    passed_records INTEGER,
    failed_records INTEGER,
    warning_records INTEGER,

    -- Rules executed
    rules_executed INTEGER,
    rules_passed INTEGER,
    rules_failed INTEGER,

    -- Period
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT dq_metrics_status_check CHECK (overall_status IN ('PASSED', 'WARNING', 'FAILED'))
);

-- Indexes for DQ queries
CREATE INDEX IF NOT EXISTS idx_dq_results_batch ON observability.obs_data_quality_results(batch_id);
CREATE INDEX IF NOT EXISTS idx_dq_results_record ON observability.obs_data_quality_results(layer, table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_dq_results_rule ON observability.obs_data_quality_results(rule_id);
CREATE INDEX IF NOT EXISTS idx_dq_results_failed ON observability.obs_data_quality_results(passed) WHERE passed = false;
CREATE INDEX IF NOT EXISTS idx_dq_metrics_table ON observability.obs_data_quality_metrics(layer, table_name);
CREATE INDEX IF NOT EXISTS idx_dq_metrics_batch ON observability.obs_data_quality_metrics(batch_id);


-- ============================================================================
-- PART 4: RECONCILIATION TABLES
-- ============================================================================

-- Reconciliation Runs: Track each reconciliation execution
CREATE TABLE IF NOT EXISTS observability.obs_reconciliation_runs (
    recon_run_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Scope
    batch_id VARCHAR(36),  -- NULL for full reconciliation
    source_layer VARCHAR(20) DEFAULT 'bronze',
    target_layer VARCHAR(20) DEFAULT 'gold',

    -- Execution
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'RUNNING',

    -- Summary counts
    total_source_records INTEGER,
    total_target_records INTEGER,
    matched_count INTEGER DEFAULT 0,
    partial_match_count INTEGER DEFAULT 0,
    mismatched_count INTEGER DEFAULT 0,
    source_only_count INTEGER DEFAULT 0,
    target_only_count INTEGER DEFAULT 0,

    -- Match rate
    match_rate DECIMAL(5,2),  -- Percentage matched

    -- Metadata
    initiated_by VARCHAR(100),
    notes TEXT,

    CONSTRAINT recon_run_status_check CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED'))
);

-- Reconciliation Results: Per-record comparison
CREATE TABLE IF NOT EXISTS observability.obs_reconciliation_results (
    recon_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    recon_run_id VARCHAR(36) NOT NULL REFERENCES observability.obs_reconciliation_runs(recon_run_id),
    batch_id VARCHAR(36),

    -- Source (Bronze)
    bronze_raw_id VARCHAR(36),
    bronze_message_type VARCHAR(50),
    bronze_key_fields JSONB,

    -- Intermediate (Silver)
    silver_stg_id VARCHAR(36),

    -- Target (Gold)
    gold_instruction_id VARCHAR(36),
    gold_key_fields JSONB,

    -- Reconciliation result
    match_status VARCHAR(20) NOT NULL,

    -- Field-level comparison
    field_comparisons JSONB,
    mismatched_fields TEXT[],
    total_fields_compared INTEGER,
    fields_matched INTEGER,

    -- Investigation
    investigation_status VARCHAR(20) DEFAULT 'NOT_INVESTIGATED',
    investigation_notes TEXT,
    investigated_by VARCHAR(100),
    investigated_at TIMESTAMP,

    -- Resolution
    resolution_action VARCHAR(50),
    resolution_notes TEXT,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP,

    -- Metadata
    reconciled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT recon_match_status_check CHECK (match_status IN (
        'MATCHED', 'PARTIAL_MATCH', 'MISMATCHED', 'BRONZE_ONLY', 'GOLD_ONLY', 'MULTIPLE_MATCHES'
    )),
    CONSTRAINT recon_investigation_check CHECK (investigation_status IN (
        'NOT_INVESTIGATED', 'INVESTIGATING', 'INVESTIGATED', 'REQUIRES_ACTION'
    )),
    CONSTRAINT recon_resolution_check CHECK (resolution_action IN (
        'ACCEPTED', 'CORRECTED', 'REJECTED', 'REPROCESSED', 'MANUAL_FIX', NULL
    ))
);

-- Indexes for reconciliation queries
CREATE INDEX IF NOT EXISTS idx_recon_run ON observability.obs_reconciliation_results(recon_run_id);
CREATE INDEX IF NOT EXISTS idx_recon_status ON observability.obs_reconciliation_results(match_status);
CREATE INDEX IF NOT EXISTS idx_recon_bronze ON observability.obs_reconciliation_results(bronze_raw_id);
CREATE INDEX IF NOT EXISTS idx_recon_gold ON observability.obs_reconciliation_results(gold_instruction_id);
CREATE INDEX IF NOT EXISTS idx_recon_investigation ON observability.obs_reconciliation_results(investigation_status)
    WHERE investigation_status != 'INVESTIGATED';


-- ============================================================================
-- PART 5: PIPELINE PROGRESS TRACKING (Enhanced)
-- ============================================================================

-- Add columns to existing batch tracking if needed
ALTER TABLE observability.obs_batch_tracking
    ADD COLUMN IF NOT EXISTS exceptions_count INTEGER DEFAULT 0;
ALTER TABLE observability.obs_batch_tracking
    ADD COLUMN IF NOT EXISTS dq_score DECIMAL(5,2);
ALTER TABLE observability.obs_batch_tracking
    ADD COLUMN IF NOT EXISTS dq_status VARCHAR(20);
ALTER TABLE observability.obs_batch_tracking
    ADD COLUMN IF NOT EXISTS recon_status VARCHAR(20);
ALTER TABLE observability.obs_batch_tracking
    ADD COLUMN IF NOT EXISTS recon_match_rate DECIMAL(5,2);


-- ============================================================================
-- PART 6: DEFAULT DQ RULES FOR PAIN.001
-- ============================================================================

INSERT INTO observability.obs_dq_rules (rule_id, rule_name, rule_description, layer, table_name, field_name, rule_type, rule_expression, is_blocking, weight)
VALUES
    -- Completeness rules (required fields)
    ('PAIN001_COMP_001', 'Message ID Required', 'Message ID must be present', 'silver', 'stg_pain001', 'msg_id', 'COMPLETENESS', 'msg_id IS NOT NULL AND msg_id != ''''', true, 1.0),
    ('PAIN001_COMP_002', 'End-to-End ID Required', 'End-to-End ID must be present', 'silver', 'stg_pain001', 'end_to_end_id', 'COMPLETENESS', 'end_to_end_id IS NOT NULL AND end_to_end_id != ''''', true, 1.0),
    ('PAIN001_COMP_003', 'Debtor Name Required', 'Debtor name must be present', 'silver', 'stg_pain001', 'debtor_name', 'COMPLETENESS', 'debtor_name IS NOT NULL AND debtor_name != ''''', true, 1.0),
    ('PAIN001_COMP_004', 'Creditor Name Required', 'Creditor name must be present', 'silver', 'stg_pain001', 'creditor_name', 'COMPLETENESS', 'creditor_name IS NOT NULL AND creditor_name != ''''', true, 1.0),
    ('PAIN001_COMP_005', 'Amount Required', 'Instructed amount must be present', 'silver', 'stg_pain001', 'instructed_amount', 'COMPLETENESS', 'instructed_amount IS NOT NULL', true, 1.0),
    ('PAIN001_COMP_006', 'Currency Required', 'Currency must be present', 'silver', 'stg_pain001', 'instructed_currency', 'COMPLETENESS', 'instructed_currency IS NOT NULL AND instructed_currency != ''''', true, 1.0),

    -- Validity rules (format/range checks)
    ('PAIN001_VAL_001', 'Amount Positive', 'Amount must be greater than zero', 'silver', 'stg_pain001', 'instructed_amount', 'VALIDITY', 'instructed_amount > 0', true, 1.0),
    ('PAIN001_VAL_002', 'Currency Format', 'Currency must be 3 characters', 'silver', 'stg_pain001', 'instructed_currency', 'VALIDITY', 'LENGTH(instructed_currency) = 3', true, 1.0),
    ('PAIN001_VAL_003', 'Country Code Format', 'Debtor country must be 2 characters', 'silver', 'stg_pain001', 'debtor_country', 'VALIDITY', 'debtor_country IS NULL OR LENGTH(debtor_country) = 2', false, 0.8),
    ('PAIN001_VAL_004', 'BIC Format', 'Debtor agent BIC must be 8 or 11 characters', 'silver', 'stg_pain001', 'debtor_agent_bic', 'VALIDITY', 'debtor_agent_bic IS NULL OR LENGTH(debtor_agent_bic) IN (8, 11)', false, 0.8),
    ('PAIN001_VAL_005', 'IBAN Format', 'Debtor IBAN must be 15-34 characters', 'silver', 'stg_pain001', 'debtor_account_iban', 'VALIDITY', 'debtor_account_iban IS NULL OR LENGTH(debtor_account_iban) BETWEEN 15 AND 34', false, 0.8),
    ('PAIN001_VAL_006', 'UETR Format', 'UETR must be valid UUID format (36 chars)', 'silver', 'stg_pain001', 'uetr', 'VALIDITY', 'uetr IS NULL OR LENGTH(uetr) = 36', false, 0.7),

    -- Accuracy rules (business logic)
    ('PAIN001_ACC_001', 'Amount Range Check', 'Amount should be reasonable (<100M)', 'silver', 'stg_pain001', 'instructed_amount', 'ACCURACY', 'instructed_amount < 100000000', false, 0.5),

    -- Consistency rules
    ('PAIN001_CON_001', 'Transaction Count Match', 'Number of transactions should match control', 'silver', 'stg_pain001', 'number_of_transactions', 'CONSISTENCY', 'number_of_transactions IS NULL OR number_of_transactions >= 1', false, 0.7)

ON CONFLICT (rule_id) DO UPDATE SET
    rule_name = EXCLUDED.rule_name,
    rule_expression = EXCLUDED.rule_expression,
    updated_at = CURRENT_TIMESTAMP;


-- ============================================================================
-- PART 7: VIEWS FOR EASY QUERYING
-- ============================================================================

-- View: Pipeline Progress by Batch
CREATE OR REPLACE VIEW observability.v_pipeline_progress AS
SELECT
    b._batch_id as batch_id,
    b.message_type,
    -- Bronze counts
    COUNT(DISTINCT b.raw_id) as bronze_total,
    COUNT(DISTINCT b.raw_id) FILTER (WHERE b.processing_status = 'PROCESSED') as bronze_processed,
    COUNT(DISTINCT b.raw_id) FILTER (WHERE b.processing_status = 'FAILED') as bronze_failed,
    -- Silver counts
    COUNT(DISTINCT s.stg_id) as silver_total,
    COUNT(DISTINCT s.stg_id) FILTER (WHERE s.processing_status = 'PROCESSED') as silver_processed,
    COUNT(DISTINCT s.stg_id) FILTER (WHERE s.processing_status = 'FAILED') as silver_failed,
    COUNT(DISTINCT s.stg_id) FILTER (WHERE s.dq_status = 'PASSED') as silver_dq_passed,
    COUNT(DISTINCT s.stg_id) FILTER (WHERE s.dq_status = 'FAILED') as silver_dq_failed,
    -- Gold counts
    COUNT(DISTINCT g.instruction_id) as gold_total,
    COUNT(DISTINCT g.instruction_id) FILTER (WHERE g.dq_status = 'PASSED') as gold_dq_passed,
    COUNT(DISTINCT g.instruction_id) FILTER (WHERE g.dq_status = 'FAILED') as gold_dq_failed,
    COUNT(DISTINCT g.instruction_id) FILTER (WHERE g.reconciliation_status = 'MATCHED') as gold_reconciled
FROM bronze.raw_payment_messages b
LEFT JOIN silver.stg_pain001 s ON b.silver_stg_id = s.stg_id
LEFT JOIN gold.cdm_payment_instruction g ON s.gold_instruction_id = g.instruction_id
GROUP BY b._batch_id, b.message_type;


-- View: Exception Summary
CREATE OR REPLACE VIEW observability.v_exception_summary AS
SELECT
    source_layer,
    exception_type,
    severity,
    status,
    COUNT(*) as exception_count,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '24 hours') as last_24h,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '1 hour') as last_1h
FROM observability.obs_processing_exceptions
GROUP BY source_layer, exception_type, severity, status
ORDER BY source_layer, exception_count DESC;


-- View: DQ Summary by Table
CREATE OR REPLACE VIEW observability.v_dq_summary AS
SELECT
    layer,
    table_name,
    AVG(overall_score) as avg_score,
    AVG(completeness_score) as avg_completeness,
    AVG(validity_score) as avg_validity,
    AVG(accuracy_score) as avg_accuracy,
    SUM(total_records) as total_records,
    SUM(passed_records) as passed_records,
    SUM(failed_records) as failed_records,
    ROUND(100.0 * SUM(passed_records) / NULLIF(SUM(total_records), 0), 2) as pass_rate
FROM observability.obs_data_quality_metrics
WHERE calculated_at > NOW() - INTERVAL '7 days'
GROUP BY layer, table_name;


-- View: Records Stuck at Each Stage
CREATE OR REPLACE VIEW observability.v_stuck_records AS
-- Bronze records not promoted to Silver
SELECT
    'BRONZE_TO_SILVER' as stage,
    b.raw_id as record_id,
    b._batch_id as batch_id,
    b.processing_status,
    b.processing_error,
    b.ingestion_timestamp as created_at
FROM bronze.raw_payment_messages b
WHERE b.processing_status = 'FAILED'
   OR (b.processing_status = 'PROCESSED' AND b.silver_stg_id IS NULL)

UNION ALL

-- Silver records not promoted to Gold
SELECT
    'SILVER_TO_GOLD' as stage,
    s.stg_id as record_id,
    s._batch_id as batch_id,
    s.processing_status,
    s.processing_error,
    s._processed_at as created_at
FROM silver.stg_pain001 s
WHERE s.processing_status = 'FAILED'
   OR (s.processing_status = 'PROCESSED' AND s.gold_instruction_id IS NULL)

UNION ALL

-- Gold records with DQ failures
SELECT
    'GOLD_DQ_FAILURE' as stage,
    g.instruction_id as record_id,
    g.lineage_batch_id as batch_id,
    g.dq_status as processing_status,
    NULL as processing_error,
    g.created_at
FROM gold.cdm_payment_instruction g
WHERE g.dq_status = 'FAILED';


-- ============================================================================
-- PART 8: TRIGGER FOR AUTOMATIC UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION observability.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to exception table
DROP TRIGGER IF EXISTS trg_exceptions_updated ON observability.obs_processing_exceptions;
CREATE TRIGGER trg_exceptions_updated
    BEFORE UPDATE ON observability.obs_processing_exceptions
    FOR EACH ROW EXECUTE FUNCTION observability.update_timestamp();


-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA observability TO PUBLIC;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA observability TO PUBLIC;


-- ============================================================================
-- DONE
-- ============================================================================
SELECT 'Exception handling schema created successfully' as status;
