-- GPS CDM - Bronze Layer Tables (raw_*)
-- ======================================
-- Layer 1: Raw data as-is - immutable, append-only
-- No transformation, just store the original message with metadata.

-- =====================================================
-- RAW PAYMENT MESSAGES
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze.raw_payment_messages (
    -- Identity
    raw_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Message Classification
    message_type VARCHAR(50) NOT NULL,         -- pain.001, MT103, ACH, FEDWIRE, SEPA, etc.
    message_format VARCHAR(20) NOT NULL,       -- XML, SWIFT_MT, JSON, CSV, FIXED
    message_version VARCHAR(30),               -- pain.001.001.09, MT103_2020, etc.

    -- Raw Content (IMMUTABLE - stored exactly as received)
    raw_content TEXT NOT NULL,
    raw_content_hash VARCHAR(64),              -- SHA-256 for deduplication
    content_size_bytes BIGINT,
    content_encoding VARCHAR(20) DEFAULT 'UTF-8',

    -- Source Tracking
    source_system VARCHAR(100) NOT NULL,       -- CashPro, SWIFT_Alliance, FedLine, etc.
    source_channel VARCHAR(50),                -- MQ, FILE, API, KAFKA
    source_queue VARCHAR(200),
    source_file_path VARCHAR(500),
    source_batch_id VARCHAR(36),
    source_sequence_number BIGINT,
    source_timestamp TIMESTAMP,                -- When source system created it

    -- Ingestion Metadata
    ingestion_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ingestion_pipeline_id VARCHAR(100),
    ingestion_pipeline_run_id VARCHAR(100),

    -- Processing State (for Bronze→Silver tracking)
    processing_status VARCHAR(20) DEFAULT 'PENDING',  -- PENDING, PROCESSING, COMPLETED, FAILED
    processed_to_silver_at TIMESTAMP,
    processing_attempts INT DEFAULT 0,
    processing_error TEXT,

    -- Partitioning
    partition_date DATE NOT NULL DEFAULT CURRENT_DATE,
    region VARCHAR(20) DEFAULT 'GLOBAL',

    -- Internal Batch
    _batch_id VARCHAR(36),
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_raw_pm_type ON bronze.raw_payment_messages(message_type);
CREATE INDEX IF NOT EXISTS idx_raw_pm_status ON bronze.raw_payment_messages(processing_status);
CREATE INDEX IF NOT EXISTS idx_raw_pm_date ON bronze.raw_payment_messages(partition_date);
CREATE INDEX IF NOT EXISTS idx_raw_pm_batch ON bronze.raw_payment_messages(_batch_id);
CREATE INDEX IF NOT EXISTS idx_raw_pm_hash ON bronze.raw_payment_messages(raw_content_hash);
CREATE INDEX IF NOT EXISTS idx_raw_pm_source ON bronze.raw_payment_messages(source_system, source_batch_id);

-- =====================================================
-- RAW PARTY MESSAGES
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze.raw_party_messages (
    raw_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    message_type VARCHAR(50) NOT NULL,
    message_format VARCHAR(20) NOT NULL,

    raw_content TEXT NOT NULL,
    raw_content_hash VARCHAR(64),

    source_system VARCHAR(100) NOT NULL,
    source_batch_id VARCHAR(36),

    ingestion_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_silver_at TIMESTAMP,

    partition_date DATE NOT NULL DEFAULT CURRENT_DATE,
    region VARCHAR(20) DEFAULT 'GLOBAL',

    _batch_id VARCHAR(36),
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_raw_party_type ON bronze.raw_party_messages(message_type);
CREATE INDEX IF NOT EXISTS idx_raw_party_status ON bronze.raw_party_messages(processing_status);

-- =====================================================
-- RAW ACCOUNT MESSAGES
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze.raw_account_messages (
    raw_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    message_type VARCHAR(50) NOT NULL,
    message_format VARCHAR(20) NOT NULL,

    raw_content TEXT NOT NULL,
    raw_content_hash VARCHAR(64),

    source_system VARCHAR(100) NOT NULL,
    source_batch_id VARCHAR(36),

    ingestion_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(20) DEFAULT 'PENDING',
    processed_to_silver_at TIMESTAMP,

    partition_date DATE NOT NULL DEFAULT CURRENT_DATE,
    region VARCHAR(20) DEFAULT 'GLOBAL',

    _batch_id VARCHAR(36),
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_raw_account_type ON bronze.raw_account_messages(message_type);
CREATE INDEX IF NOT EXISTS idx_raw_account_status ON bronze.raw_account_messages(processing_status);

-- =====================================================
-- RAW REFERENCE DATA
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze.raw_reference_data (
    raw_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    reference_type VARCHAR(100) NOT NULL,      -- FI_DIRECTORY, CURRENCY_RATES, CLEARING_CODES

    raw_content TEXT NOT NULL,
    raw_content_hash VARCHAR(64),

    source_system VARCHAR(100) NOT NULL,
    effective_date DATE,

    ingestion_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(20) DEFAULT 'PENDING',

    _batch_id VARCHAR(36),
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_raw_ref_type ON bronze.raw_reference_data(reference_type);

-- =====================================================
-- RAW SCREENING RESULTS
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze.raw_screening_results (
    raw_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    screening_type VARCHAR(50) NOT NULL,       -- SANCTIONS, PEP, ADVERSE_MEDIA
    screening_provider VARCHAR(100) NOT NULL,

    raw_response TEXT NOT NULL,

    entity_type VARCHAR(50),
    entity_id VARCHAR(100),

    ingestion_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(20) DEFAULT 'PENDING',

    _batch_id VARCHAR(36),
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_raw_screening_type ON bronze.raw_screening_results(screening_type);
CREATE INDEX IF NOT EXISTS idx_raw_screening_entity ON bronze.raw_screening_results(entity_type, entity_id);

-- Verify tables
SELECT 'bronze' as schema, table_name FROM information_schema.tables
WHERE table_schema = 'bronze' ORDER BY table_name;
