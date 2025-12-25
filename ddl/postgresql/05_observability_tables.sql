-- GPS CDM - Observability Layer Tables (obs_*)
-- =============================================
-- Operational metadata: Lineage, errors, batch tracking, DQ metrics, CDC.

-- =====================================================
-- OBS_BATCH_TRACKING (Pipeline execution tracking)
-- =====================================================
CREATE TABLE IF NOT EXISTS observability.obs_batch_tracking (
    batch_id VARCHAR(36) PRIMARY KEY,

    -- Source
    source_path VARCHAR(500),
    source_system VARCHAR(100),
    mapping_id VARCHAR(100),
    message_type VARCHAR(50),

    -- Pipeline
    pipeline_id VARCHAR(100),
    pipeline_run_id VARCHAR(100),
    pipeline_version VARCHAR(50),

    -- Layer Tracking
    current_layer VARCHAR(20),                 -- bronze, silver, gold, analytical

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',

    -- Record Counts per Layer
    bronze_records BIGINT DEFAULT 0,
    silver_records BIGINT DEFAULT 0,
    gold_records BIGINT DEFAULT 0,
    analytical_records BIGINT DEFAULT 0,
    failed_records BIGINT DEFAULT 0,

    -- Checkpoint/Restart (Record-Level)
    checkpoint_layer VARCHAR(20),
    checkpoint_offset BIGINT DEFAULT 0,
    checkpoint_partition VARCHAR(100),
    checkpoint_key VARCHAR(200),
    checkpoint_data JSONB,
    last_checkpoint_at TIMESTAMP,

    -- Timing
    started_at TIMESTAMP,
    bronze_completed_at TIMESTAMP,
    silver_completed_at TIMESTAMP,
    gold_completed_at TIMESTAMP,
    analytical_completed_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds DECIMAL(10,2),

    -- Error Handling
    error_message TEXT,
    error_layer VARCHAR(20),
    error_count INT DEFAULT 0,
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,

    -- Metadata
    metadata JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_obs_batch_status ON observability.obs_batch_tracking(status);
CREATE INDEX IF NOT EXISTS idx_obs_batch_pipeline ON observability.obs_batch_tracking(pipeline_run_id);
CREATE INDEX IF NOT EXISTS idx_obs_batch_created ON observability.obs_batch_tracking(created_at);

-- =====================================================
-- OBS_DATA_LINEAGE (Table-level lineage)
-- =====================================================
CREATE TABLE IF NOT EXISTS observability.obs_data_lineage (
    lineage_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    batch_id VARCHAR(36) NOT NULL,
    pipeline_run_id VARCHAR(100),

    -- Source
    source_layer VARCHAR(20) NOT NULL,
    source_table VARCHAR(100) NOT NULL,
    source_record_count BIGINT,

    -- Target
    target_layer VARCHAR(20) NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    target_record_count BIGINT,

    -- Mapping
    mapping_id VARCHAR(100),
    mapping_version VARCHAR(50),

    -- Summary
    field_mappings_count INT,
    transformation_types TEXT[],

    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms BIGINT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_lineage_batch FOREIGN KEY (batch_id)
        REFERENCES observability.obs_batch_tracking(batch_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_obs_lineage_batch ON observability.obs_data_lineage(batch_id);
CREATE INDEX IF NOT EXISTS idx_obs_lineage_source ON observability.obs_data_lineage(source_layer, source_table);
CREATE INDEX IF NOT EXISTS idx_obs_lineage_target ON observability.obs_data_lineage(target_layer, target_table);

-- =====================================================
-- OBS_FIELD_LINEAGE (Field-level lineage)
-- =====================================================
CREATE TABLE IF NOT EXISTS observability.obs_field_lineage (
    lineage_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    batch_id VARCHAR(36) NOT NULL,
    pipeline_run_id VARCHAR(100),

    -- Source
    source_layer VARCHAR(20) NOT NULL,
    source_table VARCHAR(100) NOT NULL,
    source_field VARCHAR(100) NOT NULL,
    source_field_path VARCHAR(500),

    -- Target
    target_layer VARCHAR(20) NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    target_field VARCHAR(100) NOT NULL,
    target_field_path VARCHAR(500),

    -- Transformation
    transformation_type VARCHAR(50) NOT NULL,
    transformation_logic TEXT,
    transformation_version VARCHAR(50),

    -- Lookup (if applicable)
    lookup_table VARCHAR(100),
    lookup_key VARCHAR(100),
    lookup_value VARCHAR(100),

    -- Mapping Reference
    mapping_id VARCHAR(100) NOT NULL,
    mapping_field_index INT,

    -- Quality
    confidence_score DECIMAL(5,4),

    -- Validity
    effective_from TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    effective_to TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_field_lineage_batch FOREIGN KEY (batch_id)
        REFERENCES observability.obs_batch_tracking(batch_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_obs_field_lineage_batch ON observability.obs_field_lineage(batch_id);
CREATE INDEX IF NOT EXISTS idx_obs_field_lineage_source ON observability.obs_field_lineage(source_table, source_field);
CREATE INDEX IF NOT EXISTS idx_obs_field_lineage_target ON observability.obs_field_lineage(target_table, target_field);
CREATE INDEX IF NOT EXISTS idx_obs_field_lineage_mapping ON observability.obs_field_lineage(mapping_id);

-- =====================================================
-- OBS_DQ_RESULTS (Per-record data quality)
-- =====================================================
CREATE TABLE IF NOT EXISTS observability.obs_dq_results (
    dq_result_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    batch_id VARCHAR(36) NOT NULL,

    -- Record
    layer VARCHAR(20) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(36) NOT NULL,
    record_key VARCHAR(200),

    -- Scores
    overall_score DECIMAL(5,2) NOT NULL,
    completeness_score DECIMAL(5,2),
    accuracy_score DECIMAL(5,2),
    validity_score DECIMAL(5,2),
    timeliness_score DECIMAL(5,2),
    consistency_score DECIMAL(5,2),

    -- Rule Summary
    rules_executed INT DEFAULT 0,
    rules_passed INT DEFAULT 0,
    rules_failed INT DEFAULT 0,
    rules_warned INT DEFAULT 0,

    -- Details
    rule_results JSONB,
    issues TEXT[],

    -- Remediation
    remediation_status VARCHAR(30) DEFAULT 'NEW',
    remediation_notes TEXT,
    remediated_at TIMESTAMP,

    evaluated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_dq_results_batch FOREIGN KEY (batch_id)
        REFERENCES observability.obs_batch_tracking(batch_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_obs_dq_batch ON observability.obs_dq_results(batch_id);
CREATE INDEX IF NOT EXISTS idx_obs_dq_entity ON observability.obs_dq_results(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_obs_dq_score ON observability.obs_dq_results(overall_score);
CREATE INDEX IF NOT EXISTS idx_obs_dq_status ON observability.obs_dq_results(remediation_status);

-- =====================================================
-- OBS_DQ_METRICS (Aggregated DQ metrics)
-- =====================================================
CREATE TABLE IF NOT EXISTS observability.obs_dq_metrics (
    metric_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    batch_id VARCHAR(36),

    metric_date DATE NOT NULL,
    metric_hour INT,

    layer VARCHAR(20),
    entity_type VARCHAR(50),
    source_message_type VARCHAR(50),
    region VARCHAR(20),

    -- Scores
    avg_overall_score DECIMAL(5,2),
    min_overall_score DECIMAL(5,2),
    max_overall_score DECIMAL(5,2),
    avg_completeness DECIMAL(5,2),
    avg_validity DECIMAL(5,2),

    -- Counts
    total_records BIGINT NOT NULL,
    records_above_threshold BIGINT,
    records_below_threshold BIGINT,

    -- Rules
    total_rules_executed BIGINT,
    total_rules_passed BIGINT,
    total_rules_failed BIGINT,

    -- Top Issues
    top_failing_rules JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_obs_dq_metrics_date ON observability.obs_dq_metrics(metric_date);
CREATE INDEX IF NOT EXISTS idx_obs_dq_metrics_entity ON observability.obs_dq_metrics(entity_type);

-- =====================================================
-- OBS_PROCESSING_ERRORS (Dead letter)
-- =====================================================
CREATE TABLE IF NOT EXISTS observability.obs_processing_errors (
    error_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    batch_id VARCHAR(36) NOT NULL,

    -- Location
    layer VARCHAR(20) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(100),
    record_key VARCHAR(200),

    -- Error
    error_type VARCHAR(100) NOT NULL,
    error_code VARCHAR(50),
    error_message TEXT NOT NULL,
    error_stack TEXT,
    severity VARCHAR(20) DEFAULT 'ERROR',

    -- Context
    record_data JSONB,
    field_name VARCHAR(100),
    field_value TEXT,

    -- Resolution
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    resolution_action VARCHAR(50),

    -- Retry
    retry_count INT DEFAULT 0,
    next_retry_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_errors_batch FOREIGN KEY (batch_id)
        REFERENCES observability.obs_batch_tracking(batch_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_obs_errors_batch ON observability.obs_processing_errors(batch_id);
CREATE INDEX IF NOT EXISTS idx_obs_errors_type ON observability.obs_processing_errors(error_type);
CREATE INDEX IF NOT EXISTS idx_obs_errors_layer ON observability.obs_processing_errors(layer);
CREATE INDEX IF NOT EXISTS idx_obs_errors_unresolved ON observability.obs_processing_errors(is_resolved) WHERE is_resolved = FALSE;

-- =====================================================
-- OBS_CDC_TRACKING (Change Data Capture)
-- =====================================================
CREATE TABLE IF NOT EXISTS observability.obs_cdc_tracking (
    cdc_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Change
    layer VARCHAR(20) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL,

    -- Data
    old_data JSONB,
    new_data JSONB,
    changed_fields TEXT[],

    -- Tracking
    change_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(36),

    -- Sync Status
    sync_status VARCHAR(20) DEFAULT 'PENDING',
    synced_to TEXT[],
    last_sync_attempt TIMESTAMP,
    sync_attempt_count INT DEFAULT 0,
    sync_error TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_obs_cdc_status ON observability.obs_cdc_tracking(sync_status);
CREATE INDEX IF NOT EXISTS idx_obs_cdc_table ON observability.obs_cdc_tracking(table_name, change_timestamp);
CREATE INDEX IF NOT EXISTS idx_obs_cdc_pending ON observability.obs_cdc_tracking(sync_status) WHERE sync_status = 'PENDING';

-- =====================================================
-- OBS_VALIDATION_RULES (Rule registry)
-- =====================================================
CREATE TABLE IF NOT EXISTS observability.obs_validation_rules (
    rule_id VARCHAR(36) PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL UNIQUE,
    rule_description TEXT,

    layer VARCHAR(20) NOT NULL,
    target_entity VARCHAR(50) NOT NULL,
    target_field VARCHAR(100),

    rule_type VARCHAR(30) NOT NULL,
    dimension VARCHAR(30) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'ERROR',

    rule_expression TEXT NOT NULL,
    error_message_template TEXT,
    weight DECIMAL(3,2) DEFAULT 1.0,

    applies_to_message_types TEXT[],
    applies_to_regions TEXT[],

    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE DEFAULT CURRENT_DATE,
    effective_to DATE,

    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INT DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_obs_rules_entity ON observability.obs_validation_rules(target_entity);
CREATE INDEX IF NOT EXISTS idx_obs_rules_active ON observability.obs_validation_rules(is_active) WHERE is_active = TRUE;

-- =====================================================
-- OBS_MAPPING_REGISTRY (Deployed mappings)
-- =====================================================
CREATE TABLE IF NOT EXISTS observability.obs_mapping_registry (
    mapping_id VARCHAR(100) PRIMARY KEY,
    mapping_name VARCHAR(200) NOT NULL,
    mapping_version VARCHAR(50) NOT NULL,

    -- Transformation
    source_layer VARCHAR(20) NOT NULL,
    target_layer VARCHAR(20) NOT NULL,
    source_format VARCHAR(30) NOT NULL,
    source_message_type VARCHAR(50) NOT NULL,
    target_entity VARCHAR(50) NOT NULL,

    -- Content
    mapping_yaml TEXT NOT NULL,
    mapping_hash VARCHAR(64),

    -- Stats
    field_count INT,
    validation_rule_count INT,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    deployed_at TIMESTAMP,
    deployed_by VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_obs_mapping_type ON observability.obs_mapping_registry(source_message_type);
CREATE INDEX IF NOT EXISTS idx_obs_mapping_layers ON observability.obs_mapping_registry(source_layer, target_layer);
CREATE INDEX IF NOT EXISTS idx_obs_mapping_active ON observability.obs_mapping_registry(is_active) WHERE is_active = TRUE;

-- Verify tables
SELECT 'observability' as schema, table_name FROM information_schema.tables
WHERE table_schema = 'observability' ORDER BY table_name;
