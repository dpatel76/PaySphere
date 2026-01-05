-- GPS CDM - Zone-Separated Observability Extensions
-- ==================================================
-- Additional tables for message-level tracking in zone-separated architecture.

-- =====================================================
-- OBS_MESSAGE_TRACKING (Per-message tracking across zones)
-- =====================================================
-- Tracks individual messages as they flow through Bronze → Silver → Gold.
-- Provides full transparency at the message level.

CREATE TABLE IF NOT EXISTS observability.obs_message_tracking (
    tracking_id VARCHAR(36) PRIMARY KEY,
    batch_id VARCHAR(36) NOT NULL,

    -- Message Identity
    message_id VARCHAR(36) NOT NULL,         -- Original message ID or generated
    message_type VARCHAR(50) NOT NULL,

    -- Current State
    current_zone VARCHAR(20) NOT NULL,       -- BRONZE, SILVER, GOLD, COMPLETE, FAILED
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, PROCESSING, SUCCESS, FAILED

    -- Zone IDs (populated as message moves through zones)
    bronze_raw_id VARCHAR(36),               -- ID in bronze.raw_payment_messages
    silver_stg_id VARCHAR(36),               -- ID in silver.stg_* table
    gold_instr_id VARCHAR(36),               -- ID in gold.cdm_payment_instruction

    -- Timing
    bronze_started_at TIMESTAMP,
    bronze_completed_at TIMESTAMP,
    silver_started_at TIMESTAMP,
    silver_completed_at TIMESTAMP,
    gold_started_at TIMESTAMP,
    gold_completed_at TIMESTAMP,

    -- Error Info
    error_zone VARCHAR(20),
    error_message TEXT,
    error_code VARCHAR(50),
    retry_count INT DEFAULT 0,

    -- Metadata
    source_file VARCHAR(500),
    kafka_topic VARCHAR(200),
    kafka_partition INT,
    kafka_offset BIGINT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_msg_tracking_batch FOREIGN KEY (batch_id)
        REFERENCES observability.obs_batch_tracking(batch_id) ON DELETE CASCADE
);

-- Indexes for message tracking queries
CREATE INDEX IF NOT EXISTS idx_obs_msg_batch ON observability.obs_message_tracking(batch_id);
CREATE INDEX IF NOT EXISTS idx_obs_msg_type ON observability.obs_message_tracking(message_type);
CREATE INDEX IF NOT EXISTS idx_obs_msg_zone ON observability.obs_message_tracking(current_zone);
CREATE INDEX IF NOT EXISTS idx_obs_msg_status ON observability.obs_message_tracking(status);
CREATE INDEX IF NOT EXISTS idx_obs_msg_bronze ON observability.obs_message_tracking(bronze_raw_id);
CREATE INDEX IF NOT EXISTS idx_obs_msg_silver ON observability.obs_message_tracking(silver_stg_id);
CREATE INDEX IF NOT EXISTS idx_obs_msg_gold ON observability.obs_message_tracking(gold_instr_id);
CREATE INDEX IF NOT EXISTS idx_obs_msg_failed ON observability.obs_message_tracking(status) WHERE status = 'FAILED';


-- =====================================================
-- Enhance OBS_DATA_LINEAGE for zone-separated architecture
-- =====================================================
-- Add columns for more granular lineage tracking if they don't exist.

DO $$
BEGIN
    -- Add source_zone column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'observability'
        AND table_name = 'obs_data_lineage'
        AND column_name = 'source_zone'
    ) THEN
        ALTER TABLE observability.obs_data_lineage ADD COLUMN source_zone VARCHAR(20);
    END IF;

    -- Add target_zone column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'observability'
        AND table_name = 'obs_data_lineage'
        AND column_name = 'target_zone'
    ) THEN
        ALTER TABLE observability.obs_data_lineage ADD COLUMN target_zone VARCHAR(20);
    END IF;

    -- Add source_id column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'observability'
        AND table_name = 'obs_data_lineage'
        AND column_name = 'source_id'
    ) THEN
        ALTER TABLE observability.obs_data_lineage ADD COLUMN source_id VARCHAR(36);
    END IF;

    -- Add target_id column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'observability'
        AND table_name = 'obs_data_lineage'
        AND column_name = 'target_id'
    ) THEN
        ALTER TABLE observability.obs_data_lineage ADD COLUMN target_id VARCHAR(36);
    END IF;

    -- Add transformation column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'observability'
        AND table_name = 'obs_data_lineage'
        AND column_name = 'transformation'
    ) THEN
        ALTER TABLE observability.obs_data_lineage ADD COLUMN transformation VARCHAR(50);
    END IF;

    -- Add field_mappings column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'observability'
        AND table_name = 'obs_data_lineage'
        AND column_name = 'field_mappings'
    ) THEN
        ALTER TABLE observability.obs_data_lineage ADD COLUMN field_mappings JSONB;
    END IF;
END $$;

-- Indexes for enhanced lineage queries
CREATE INDEX IF NOT EXISTS idx_obs_lineage_source_id ON observability.obs_data_lineage(source_id);
CREATE INDEX IF NOT EXISTS idx_obs_lineage_target_id ON observability.obs_data_lineage(target_id);
CREATE INDEX IF NOT EXISTS idx_obs_lineage_zones ON observability.obs_data_lineage(source_zone, target_zone);


-- =====================================================
-- KAFKA_CONSUMER_CHECKPOINTS (Zone-specific checkpoints)
-- =====================================================
-- Track Kafka consumer offsets for zone-separated consumers.

CREATE TABLE IF NOT EXISTS observability.kafka_zone_checkpoints (
    checkpoint_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Consumer Identity
    zone VARCHAR(20) NOT NULL,               -- bronze, silver, gold
    consumer_group VARCHAR(100) NOT NULL,
    consumer_id VARCHAR(100),

    -- Kafka Position
    topic VARCHAR(200) NOT NULL,
    partition_id INT NOT NULL,
    committed_offset BIGINT NOT NULL DEFAULT 0,
    pending_offset BIGINT,

    -- Batch State
    current_batch_id VARCHAR(36),
    batch_record_count INT DEFAULT 0,
    batch_state VARCHAR(20) DEFAULT 'NONE', -- NONE, ACCUMULATING, FLUSHING, COMMITTED

    -- Health
    processing_status VARCHAR(20) DEFAULT 'ACTIVE', -- ACTIVE, PAUSED, RECOVERING, FAILED
    last_heartbeat_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (consumer_group, topic, partition_id)
);

CREATE INDEX IF NOT EXISTS idx_kafka_zone_ckpt_zone ON observability.kafka_zone_checkpoints(zone);
CREATE INDEX IF NOT EXISTS idx_kafka_zone_ckpt_topic ON observability.kafka_zone_checkpoints(topic);
CREATE INDEX IF NOT EXISTS idx_kafka_zone_ckpt_status ON observability.kafka_zone_checkpoints(processing_status);


-- =====================================================
-- VIEW: Message Lineage Summary
-- =====================================================
-- Shows complete lineage for each message across all zones.

CREATE OR REPLACE VIEW observability.v_message_lineage AS
SELECT
    mt.batch_id,
    mt.message_id,
    mt.message_type,
    mt.current_zone,
    mt.status,

    -- Bronze
    mt.bronze_raw_id,
    mt.bronze_started_at,
    mt.bronze_completed_at,
    EXTRACT(EPOCH FROM (mt.bronze_completed_at - mt.bronze_started_at)) * 1000 AS bronze_duration_ms,

    -- Silver
    mt.silver_stg_id,
    mt.silver_started_at,
    mt.silver_completed_at,
    EXTRACT(EPOCH FROM (mt.silver_completed_at - mt.silver_started_at)) * 1000 AS silver_duration_ms,

    -- Gold
    mt.gold_instr_id,
    mt.gold_started_at,
    mt.gold_completed_at,
    EXTRACT(EPOCH FROM (mt.gold_completed_at - mt.gold_started_at)) * 1000 AS gold_duration_ms,

    -- Total
    EXTRACT(EPOCH FROM (COALESCE(mt.gold_completed_at, mt.silver_completed_at, mt.bronze_completed_at)
                        - mt.bronze_started_at)) * 1000 AS total_duration_ms,

    -- Error
    mt.error_zone,
    mt.error_message,
    mt.retry_count

FROM observability.obs_message_tracking mt
ORDER BY mt.created_at DESC;


-- =====================================================
-- VIEW: Batch Progress Summary
-- =====================================================
-- Shows progress of each batch through zones.

CREATE OR REPLACE VIEW observability.v_batch_progress AS
SELECT
    bt.batch_id,
    bt.message_type,
    bt.status,
    bt.current_layer,

    -- Record Counts
    bt.bronze_records,
    bt.silver_records,
    bt.gold_records,
    bt.failed_records,

    -- Progress Percentages
    CASE WHEN bt.bronze_records > 0
        THEN ROUND((bt.silver_records::numeric / bt.bronze_records) * 100, 1)
        ELSE 0
    END AS bronze_to_silver_pct,

    CASE WHEN bt.silver_records > 0
        THEN ROUND((bt.gold_records::numeric / bt.silver_records) * 100, 1)
        ELSE 0
    END AS silver_to_gold_pct,

    -- Timing
    bt.started_at,
    bt.bronze_completed_at,
    bt.silver_completed_at,
    bt.gold_completed_at,
    bt.completed_at,

    -- Duration
    EXTRACT(EPOCH FROM (COALESCE(bt.completed_at, CURRENT_TIMESTAMP) - bt.started_at)) AS duration_seconds,

    -- Message-level Stats (from message tracking)
    (SELECT COUNT(*) FROM observability.obs_message_tracking mt
     WHERE mt.batch_id = bt.batch_id AND mt.status = 'SUCCESS') AS success_count,

    (SELECT COUNT(*) FROM observability.obs_message_tracking mt
     WHERE mt.batch_id = bt.batch_id AND mt.status = 'FAILED') AS failed_count

FROM observability.obs_batch_tracking bt
ORDER BY bt.created_at DESC;


-- =====================================================
-- VIEW: Zone Health Dashboard
-- =====================================================
-- Shows health metrics for each zone's consumers.

CREATE OR REPLACE VIEW observability.v_zone_health AS
SELECT
    zone,
    COUNT(DISTINCT consumer_group) AS consumer_groups,
    COUNT(*) AS total_partitions,

    -- Offset Stats
    SUM(committed_offset) AS total_committed_offsets,
    MAX(committed_offset) AS max_offset,

    -- Status Counts
    SUM(CASE WHEN processing_status = 'ACTIVE' THEN 1 ELSE 0 END) AS active_consumers,
    SUM(CASE WHEN processing_status = 'PAUSED' THEN 1 ELSE 0 END) AS paused_consumers,
    SUM(CASE WHEN processing_status = 'FAILED' THEN 1 ELSE 0 END) AS failed_consumers,

    -- Lag (simplified - would need Kafka metadata for actual lag)
    SUM(COALESCE(pending_offset, 0) - committed_offset) AS pending_messages,

    -- Last Activity
    MAX(last_heartbeat_at) AS last_activity,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - MAX(last_heartbeat_at))) AS seconds_since_activity

FROM observability.kafka_zone_checkpoints
GROUP BY zone;


-- =====================================================
-- Verify Tables
-- =====================================================
SELECT 'observability' AS schema, table_name
FROM information_schema.tables
WHERE table_schema = 'observability'
  AND table_name IN ('obs_message_tracking', 'kafka_zone_checkpoints')
ORDER BY table_name;
