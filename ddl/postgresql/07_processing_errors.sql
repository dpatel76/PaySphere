-- =============================================================================
-- GPS CDM - Processing Errors Table
-- =============================================================================
-- Tracks failed records across Bronze, Silver, and Gold zones for reprocessing.
-- Used by the admin dashboard for error management and analytics.
-- =============================================================================

-- Create the processing_errors table in bronze schema
-- (errors can occur at any zone, but we centralize tracking here)
CREATE TABLE IF NOT EXISTS bronze.processing_errors (
    -- Primary Key
    error_id VARCHAR(36) PRIMARY KEY,

    -- Batch Context
    batch_id VARCHAR(36) NOT NULL,
    chunk_index INT,
    total_chunks INT,

    -- Zone Information
    zone VARCHAR(10) NOT NULL CHECK (zone IN ('BRONZE', 'SILVER', 'GOLD')),

    -- Record Reference (depends on zone)
    -- BRONZE: raw_id is NULL (record wasn't created), content_hash identifies the message
    -- SILVER: raw_id is set (from bronze), stg_id is NULL
    -- GOLD: stg_id is set (from silver), raw_id traces back to bronze
    raw_id VARCHAR(36),
    stg_id VARCHAR(36),
    content_hash VARCHAR(64),  -- SHA-256 of original content for deduplication

    -- Message Context
    message_type VARCHAR(50) NOT NULL,
    message_id VARCHAR(100),  -- Original message ID from source content

    -- Error Details
    error_code VARCHAR(50),  -- Categorized error code (e.g., 'PARSE_ERROR', 'VALIDATION_ERROR', 'DB_ERROR')
    error_message TEXT NOT NULL,
    error_stack_trace TEXT,  -- Full stack trace for debugging

    -- Original Content (for manual inspection and retry)
    original_content TEXT,  -- Raw JSON/XML that failed

    -- Processing State
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'RETRYING', 'RESOLVED', 'SKIPPED', 'ABANDONED')),
    retry_count INT NOT NULL DEFAULT 0,
    max_retries INT NOT NULL DEFAULT 3,
    last_retry_at TIMESTAMP,
    next_retry_at TIMESTAMP,

    -- Resolution
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(100),
    resolution_notes TEXT,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_processing_errors_batch_id
    ON bronze.processing_errors(batch_id);

CREATE INDEX IF NOT EXISTS idx_processing_errors_zone
    ON bronze.processing_errors(zone);

CREATE INDEX IF NOT EXISTS idx_processing_errors_status
    ON bronze.processing_errors(status);

CREATE INDEX IF NOT EXISTS idx_processing_errors_message_type
    ON bronze.processing_errors(message_type);

CREATE INDEX IF NOT EXISTS idx_processing_errors_created_at
    ON bronze.processing_errors(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_processing_errors_raw_id
    ON bronze.processing_errors(raw_id) WHERE raw_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_processing_errors_stg_id
    ON bronze.processing_errors(stg_id) WHERE stg_id IS NOT NULL;

-- Composite index for dashboard filtering
CREATE INDEX IF NOT EXISTS idx_processing_errors_dashboard
    ON bronze.processing_errors(status, zone, message_type, created_at DESC);

-- Index for retry scheduling
CREATE INDEX IF NOT EXISTS idx_processing_errors_retry
    ON bronze.processing_errors(status, next_retry_at)
    WHERE status IN ('PENDING', 'RETRYING');

-- =============================================================================
-- Error Code Reference Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS bronze.error_codes (
    error_code VARCHAR(50) PRIMARY KEY,
    error_category VARCHAR(30) NOT NULL,  -- PARSE, VALIDATION, DATABASE, NETWORK, UNKNOWN
    description TEXT,
    is_retryable BOOLEAN NOT NULL DEFAULT TRUE,
    suggested_action TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert common error codes
INSERT INTO bronze.error_codes (error_code, error_category, description, is_retryable, suggested_action) VALUES
    ('PARSE_ERROR', 'PARSE', 'Failed to parse message content (invalid JSON/XML)', FALSE, 'Review and fix message format manually'),
    ('VALIDATION_ERROR', 'VALIDATION', 'Message failed schema validation', FALSE, 'Check message against schema requirements'),
    ('MISSING_REQUIRED_FIELD', 'VALIDATION', 'Required field is missing from message', FALSE, 'Add missing required fields'),
    ('INVALID_FIELD_VALUE', 'VALIDATION', 'Field value does not match expected format/range', FALSE, 'Correct the invalid field value'),
    ('DUPLICATE_MESSAGE', 'VALIDATION', 'Message with same ID already processed', FALSE, 'Skip or use different message ID'),
    ('DB_CONNECTION_ERROR', 'DATABASE', 'Failed to connect to database', TRUE, 'Retry - database may be temporarily unavailable'),
    ('DB_CONSTRAINT_VIOLATION', 'DATABASE', 'Database constraint violated (FK, unique, check)', FALSE, 'Review data relationships and constraints'),
    ('DB_TIMEOUT', 'DATABASE', 'Database operation timed out', TRUE, 'Retry - database may be under load'),
    ('EXTRACTOR_NOT_FOUND', 'PARSE', 'No extractor registered for message type', FALSE, 'Implement extractor for this message type'),
    ('SILVER_TABLE_NOT_FOUND', 'DATABASE', 'Silver staging table does not exist', FALSE, 'Create staging table for this message type'),
    ('NETWORK_TIMEOUT', 'NETWORK', 'Network request timed out', TRUE, 'Retry - network issue may be transient'),
    ('CELERY_TASK_TIMEOUT', 'NETWORK', 'Celery task exceeded time limit', TRUE, 'Retry - task may have been processing large batch'),
    ('UNKNOWN_ERROR', 'UNKNOWN', 'Unexpected error occurred', TRUE, 'Review stack trace for root cause')
ON CONFLICT (error_code) DO NOTHING;

-- =============================================================================
-- Processing Error History (for audit trail)
-- =============================================================================
CREATE TABLE IF NOT EXISTS bronze.processing_error_history (
    history_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    error_id VARCHAR(36) NOT NULL REFERENCES bronze.processing_errors(error_id),
    action VARCHAR(30) NOT NULL,  -- CREATED, RETRY_ATTEMPTED, RETRY_SUCCEEDED, RETRY_FAILED, RESOLVED, SKIPPED, ABANDONED
    action_by VARCHAR(100),
    action_notes TEXT,
    previous_status VARCHAR(20),
    new_status VARCHAR(20),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_error_history_error_id
    ON bronze.processing_error_history(error_id);

CREATE INDEX IF NOT EXISTS idx_error_history_created_at
    ON bronze.processing_error_history(created_at DESC);

-- =============================================================================
-- Trigger to update updated_at timestamp
-- =============================================================================
CREATE OR REPLACE FUNCTION bronze.update_processing_errors_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_processing_errors_updated_at ON bronze.processing_errors;
CREATE TRIGGER trg_processing_errors_updated_at
    BEFORE UPDATE ON bronze.processing_errors
    FOR EACH ROW
    EXECUTE FUNCTION bronze.update_processing_errors_timestamp();

-- =============================================================================
-- View for Dashboard Summary Statistics
-- =============================================================================
CREATE OR REPLACE VIEW bronze.v_error_stats AS
SELECT
    zone,
    message_type,
    status,
    COUNT(*) as error_count,
    MIN(created_at) as oldest_error,
    MAX(created_at) as newest_error,
    AVG(retry_count)::NUMERIC(5,2) as avg_retry_count,
    COUNT(CASE WHEN retry_count >= max_retries THEN 1 END) as max_retries_reached
FROM bronze.processing_errors
GROUP BY zone, message_type, status;

-- =============================================================================
-- View for Pending Retries
-- =============================================================================
CREATE OR REPLACE VIEW bronze.v_pending_retries AS
SELECT
    error_id,
    batch_id,
    zone,
    raw_id,
    stg_id,
    message_type,
    error_code,
    error_message,
    retry_count,
    max_retries,
    next_retry_at,
    created_at
FROM bronze.processing_errors
WHERE status IN ('PENDING', 'RETRYING')
  AND (next_retry_at IS NULL OR next_retry_at <= CURRENT_TIMESTAMP)
  AND retry_count < max_retries
ORDER BY created_at ASC;

-- =============================================================================
-- Comments
-- =============================================================================
COMMENT ON TABLE bronze.processing_errors IS 'Centralized error tracking for Bronze, Silver, and Gold zone processing failures';
COMMENT ON TABLE bronze.error_codes IS 'Reference table of error codes with retry guidance';
COMMENT ON TABLE bronze.processing_error_history IS 'Audit trail of all actions taken on processing errors';
COMMENT ON VIEW bronze.v_error_stats IS 'Aggregated error statistics for dashboard';
COMMENT ON VIEW bronze.v_pending_retries IS 'Errors ready for retry processing';
