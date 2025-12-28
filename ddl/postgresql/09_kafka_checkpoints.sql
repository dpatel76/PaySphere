-- GPS CDM - Kafka Consumer Checkpoint Tables
-- ============================================
-- Provides exactly-once semantics and crash recovery for Kafka consumers.
-- Checkpoints are stored in PostgreSQL for durability across restarts.

-- =====================================================
-- KAFKA CONSUMER CHECKPOINTS
-- =====================================================
-- Stores Kafka consumer offsets and processing state.
-- Used for recovery when a consumer crashes mid-batch.

CREATE TABLE IF NOT EXISTS observability.kafka_consumer_checkpoints (
    checkpoint_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Consumer Identity
    consumer_group VARCHAR(100) NOT NULL,
    consumer_id VARCHAR(100) NOT NULL,           -- Unique per consumer instance
    topic VARCHAR(200) NOT NULL,
    partition_id INTEGER NOT NULL,

    -- Offset Tracking
    committed_offset BIGINT NOT NULL,            -- Last successfully committed offset
    pending_offset BIGINT,                       -- Offset currently being processed

    -- Batch State (for micro-batch recovery)
    current_batch_id VARCHAR(36),
    batch_start_offset BIGINT,
    batch_end_offset BIGINT,
    batch_record_count INTEGER DEFAULT 0,
    batch_state VARCHAR(20) DEFAULT 'NONE',      -- NONE, ACCUMULATING, FLUSHING, COMMITTED

    -- Processing State
    processing_status VARCHAR(20) DEFAULT 'ACTIVE',  -- ACTIVE, PAUSED, RECOVERING, FAILED
    last_heartbeat_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Recovery Data
    pending_records JSONB,                       -- Serialized records in current batch (for recovery)
    recovery_attempts INTEGER DEFAULT 0,
    last_recovery_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint for consumer-topic-partition combination
    CONSTRAINT uk_consumer_topic_partition
        UNIQUE (consumer_group, topic, partition_id)
);

CREATE INDEX IF NOT EXISTS idx_kafka_checkpoint_group
    ON observability.kafka_consumer_checkpoints(consumer_group);
CREATE INDEX IF NOT EXISTS idx_kafka_checkpoint_status
    ON observability.kafka_consumer_checkpoints(processing_status);
CREATE INDEX IF NOT EXISTS idx_kafka_checkpoint_batch
    ON observability.kafka_consumer_checkpoints(current_batch_id)
    WHERE current_batch_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_kafka_checkpoint_heartbeat
    ON observability.kafka_consumer_checkpoints(last_heartbeat_at);


-- =====================================================
-- MICRO-BATCH TRACKING
-- =====================================================
-- Tracks individual micro-batches through the pipeline.
-- Enables recovery of partially processed batches.

CREATE TABLE IF NOT EXISTS observability.micro_batch_tracking (
    batch_id VARCHAR(36) PRIMARY KEY,

    -- Source
    consumer_group VARCHAR(100) NOT NULL,
    topic VARCHAR(200) NOT NULL,
    partitions INTEGER[],                        -- Partitions included in batch

    -- Offset Range
    min_offset BIGINT NOT NULL,
    max_offset BIGINT NOT NULL,
    record_count INTEGER NOT NULL,

    -- Message Info
    message_type VARCHAR(50) NOT NULL,

    -- Processing State
    state VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    -- States: PENDING, WRITING_BRONZE, BRONZE_COMPLETE,
    --         WRITING_SILVER, SILVER_COMPLETE,
    --         WRITING_GOLD, GOLD_COMPLETE,
    --         COMMITTING, COMMITTED, FAILED

    -- Layer Progress
    bronze_written_at TIMESTAMP,
    bronze_record_count INTEGER,
    silver_written_at TIMESTAMP,
    silver_record_count INTEGER,
    gold_written_at TIMESTAMP,
    gold_record_count INTEGER,

    -- Kafka Offset Commit
    offsets_committed BOOLEAN DEFAULT FALSE,
    offsets_committed_at TIMESTAMP,

    -- Error Handling
    error_message TEXT,
    error_layer VARCHAR(20),
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,

    -- Timing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms BIGINT,

    -- Recovery
    recovery_batch_id VARCHAR(36),               -- Original batch ID if this is a retry
    is_recovery BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_micro_batch_state
    ON observability.micro_batch_tracking(state);
CREATE INDEX IF NOT EXISTS idx_micro_batch_consumer
    ON observability.micro_batch_tracking(consumer_group);
CREATE INDEX IF NOT EXISTS idx_micro_batch_topic
    ON observability.micro_batch_tracking(topic, message_type);
CREATE INDEX IF NOT EXISTS idx_micro_batch_pending
    ON observability.micro_batch_tracking(state)
    WHERE state IN ('PENDING', 'WRITING_BRONZE', 'WRITING_SILVER', 'WRITING_GOLD');
CREATE INDEX IF NOT EXISTS idx_micro_batch_failed
    ON observability.micro_batch_tracking(state)
    WHERE state = 'FAILED';


-- =====================================================
-- BRONZE STAGING TABLE (for atomic batch writes)
-- =====================================================
-- Temporary staging for bulk COPY operations.
-- Records are written here first, then moved to main Bronze table.

CREATE UNLOGGED TABLE IF NOT EXISTS bronze.raw_payment_messages_staging (
    LIKE bronze.raw_payment_messages INCLUDING DEFAULTS
);

-- Drop constraints for faster bulk loading
ALTER TABLE bronze.raw_payment_messages_staging
    DROP CONSTRAINT IF EXISTS raw_payment_messages_staging_pkey;


-- =====================================================
-- BULK WRITE TRACKING
-- =====================================================
-- Tracks individual bulk write operations for recovery.

CREATE TABLE IF NOT EXISTS observability.bulk_write_log (
    write_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Batch Reference
    batch_id VARCHAR(36) NOT NULL,

    -- Target
    target_layer VARCHAR(20) NOT NULL,           -- bronze, silver, gold
    target_table VARCHAR(100) NOT NULL,

    -- Write Details
    record_count INTEGER NOT NULL,
    write_method VARCHAR(20) NOT NULL,           -- COPY, INSERT, UPSERT

    -- State
    state VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    -- States: PENDING, WRITING, STAGED, COMMITTED, FAILED, ROLLED_BACK

    -- Staging Info (for two-phase writes)
    staging_table VARCHAR(100),
    staging_complete BOOLEAN DEFAULT FALSE,

    -- Commit Info
    committed_at TIMESTAMP,

    -- Error
    error_message TEXT,

    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms BIGINT,
    rows_per_second DECIMAL(10,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bulk_write_batch
    ON observability.bulk_write_log(batch_id);
CREATE INDEX IF NOT EXISTS idx_bulk_write_state
    ON observability.bulk_write_log(state);
CREATE INDEX IF NOT EXISTS idx_bulk_write_pending
    ON observability.bulk_write_log(state)
    WHERE state IN ('PENDING', 'WRITING', 'STAGED');


-- =====================================================
-- DEAD LETTER QUEUE FOR FAILED BATCHES
-- =====================================================
-- Stores failed batches for manual review and replay.

CREATE TABLE IF NOT EXISTS observability.kafka_dead_letter_queue (
    dlq_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Original Batch Info
    batch_id VARCHAR(36) NOT NULL,
    consumer_group VARCHAR(100) NOT NULL,
    topic VARCHAR(200) NOT NULL,
    message_type VARCHAR(50) NOT NULL,

    -- Kafka Offsets
    partitions INTEGER[],
    min_offset BIGINT,
    max_offset BIGINT,

    -- Failed Records (stored for replay)
    record_count INTEGER NOT NULL,
    records JSONB NOT NULL,                      -- Serialized records

    -- Error Info
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    error_stack TEXT,
    failed_at_layer VARCHAR(20),

    -- Retry Info
    retry_count INTEGER DEFAULT 0,
    last_retry_at TIMESTAMP,
    next_retry_at TIMESTAMP,

    -- Resolution
    resolution_status VARCHAR(30) DEFAULT 'PENDING',
    -- Statuses: PENDING, RETRYING, RESOLVED, SKIPPED, MANUAL_REVIEW
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(100),
    resolution_notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dlq_status
    ON observability.kafka_dead_letter_queue(resolution_status);
CREATE INDEX IF NOT EXISTS idx_dlq_topic
    ON observability.kafka_dead_letter_queue(topic, message_type);
CREATE INDEX IF NOT EXISTS idx_dlq_pending
    ON observability.kafka_dead_letter_queue(resolution_status)
    WHERE resolution_status = 'PENDING';


-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to claim stale consumer checkpoints (for failover)
CREATE OR REPLACE FUNCTION observability.claim_stale_checkpoint(
    p_consumer_group VARCHAR,
    p_new_consumer_id VARCHAR,
    p_stale_threshold_seconds INTEGER DEFAULT 60
) RETURNS TABLE (
    topic VARCHAR,
    partition_id INTEGER,
    committed_offset BIGINT,
    pending_offset BIGINT,
    batch_id VARCHAR,
    pending_records JSONB
) AS $$
BEGIN
    RETURN QUERY
    UPDATE observability.kafka_consumer_checkpoints
    SET
        consumer_id = p_new_consumer_id,
        processing_status = 'RECOVERING',
        last_heartbeat_at = CURRENT_TIMESTAMP,
        recovery_attempts = recovery_attempts + 1,
        last_recovery_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE consumer_group = p_consumer_group
      AND last_heartbeat_at < CURRENT_TIMESTAMP - (p_stale_threshold_seconds || ' seconds')::INTERVAL
      AND processing_status != 'FAILED'
    RETURNING
        kafka_consumer_checkpoints.topic,
        kafka_consumer_checkpoints.partition_id,
        kafka_consumer_checkpoints.committed_offset,
        kafka_consumer_checkpoints.pending_offset,
        kafka_consumer_checkpoints.current_batch_id,
        kafka_consumer_checkpoints.pending_records;
END;
$$ LANGUAGE plpgsql;


-- Function to get incomplete micro-batches for recovery
CREATE OR REPLACE FUNCTION observability.get_incomplete_batches(
    p_consumer_group VARCHAR,
    p_max_age_minutes INTEGER DEFAULT 60
) RETURNS TABLE (
    batch_id VARCHAR,
    topic VARCHAR,
    message_type VARCHAR,
    state VARCHAR,
    min_offset BIGINT,
    max_offset BIGINT,
    record_count INTEGER,
    error_message TEXT,
    retry_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        mbt.batch_id,
        mbt.topic,
        mbt.message_type,
        mbt.state,
        mbt.min_offset,
        mbt.max_offset,
        mbt.record_count,
        mbt.error_message,
        mbt.retry_count
    FROM observability.micro_batch_tracking mbt
    WHERE mbt.consumer_group = p_consumer_group
      AND mbt.state NOT IN ('COMMITTED', 'FAILED')
      AND mbt.created_at > CURRENT_TIMESTAMP - (p_max_age_minutes || ' minutes')::INTERVAL
    ORDER BY mbt.created_at;
END;
$$ LANGUAGE plpgsql;


-- Function to recover a failed batch from DLQ
CREATE OR REPLACE FUNCTION observability.recover_from_dlq(
    p_dlq_id VARCHAR
) RETURNS VARCHAR AS $$
DECLARE
    v_new_batch_id VARCHAR;
    v_dlq_record RECORD;
BEGIN
    -- Get DLQ record
    SELECT * INTO v_dlq_record
    FROM observability.kafka_dead_letter_queue
    WHERE dlq_id = p_dlq_id AND resolution_status = 'PENDING';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'DLQ record not found or already resolved: %', p_dlq_id;
    END IF;

    -- Generate new batch ID
    v_new_batch_id := uuid_generate_v4()::text;

    -- Create new micro-batch tracking entry
    INSERT INTO observability.micro_batch_tracking (
        batch_id, consumer_group, topic, partitions,
        min_offset, max_offset, record_count, message_type,
        state, recovery_batch_id, is_recovery
    ) VALUES (
        v_new_batch_id, v_dlq_record.consumer_group, v_dlq_record.topic,
        v_dlq_record.partitions, v_dlq_record.min_offset, v_dlq_record.max_offset,
        v_dlq_record.record_count, v_dlq_record.message_type,
        'PENDING', v_dlq_record.batch_id, TRUE
    );

    -- Update DLQ status
    UPDATE observability.kafka_dead_letter_queue
    SET resolution_status = 'RETRYING',
        last_retry_at = CURRENT_TIMESTAMP,
        retry_count = retry_count + 1
    WHERE dlq_id = p_dlq_id;

    RETURN v_new_batch_id;
END;
$$ LANGUAGE plpgsql;


-- Verify tables
SELECT 'observability' as schema, table_name FROM information_schema.tables
WHERE table_schema = 'observability'
  AND table_name LIKE '%kafka%' OR table_name LIKE '%micro_batch%' OR table_name LIKE '%bulk_write%'
ORDER BY table_name;
