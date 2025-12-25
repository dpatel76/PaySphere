-- GPS Payments CDM - Bronze Zone Tables
-- Databricks Delta Lake DDL
-- Version: 1.0.0
-- Date: 2024-12-20

-- =============================================================================
-- BRONZE ZONE: Raw data landing with minimal transformation
-- - Preserve original message format
-- - Add ingestion metadata
-- - Partition by date and source system
-- - Append-only writes
-- =============================================================================

-- Create Bronze catalog and schema
CREATE CATALOG IF NOT EXISTS gps_cdm;
USE CATALOG gps_cdm;

CREATE SCHEMA IF NOT EXISTS bronze
COMMENT 'Raw payment data landing zone with minimal transformation';

USE SCHEMA bronze;

-- =============================================================================
-- BRONZE TABLES
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Payment Messages (raw ingested data)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bronze.payment_messages (
    -- Message Metadata
    message_id STRING NOT NULL COMMENT 'Unique message identifier',
    message_type STRING NOT NULL COMMENT 'Message type: ISO20022, MT103, ACH, etc.',
    message_format STRING NOT NULL COMMENT 'Format: XML, JSON, CSV, FIXED',
    message_version STRING COMMENT 'Message version/schema version',

    -- Raw Content
    raw_content STRING NOT NULL COMMENT 'Original message content',
    raw_content_hash STRING COMMENT 'SHA-256 hash of raw content',
    content_size_bytes LONG COMMENT 'Content size in bytes',

    -- Source Tracking
    source_system STRING NOT NULL COMMENT 'Originating system',
    source_queue STRING COMMENT 'Source queue/topic name',
    source_file_path STRING COMMENT 'Source file path if from file',
    source_batch_id STRING COMMENT 'Source batch identifier',
    source_sequence_number LONG COMMENT 'Sequence within batch',

    -- Ingestion Metadata
    ingestion_timestamp TIMESTAMP NOT NULL COMMENT 'When message was ingested',
    ingestion_pipeline_id STRING COMMENT 'Ingestion pipeline identifier',
    ingestion_pipeline_run_id STRING COMMENT 'Pipeline run/job ID',
    ingestion_status STRING COMMENT 'SUCCESS, FAILED, PARTIAL',
    ingestion_error_message STRING COMMENT 'Error message if failed',

    -- Extracted Key Fields (for routing/filtering)
    extracted_payment_id STRING COMMENT 'Extracted payment ID',
    extracted_amount DECIMAL(18,4) COMMENT 'Extracted amount',
    extracted_currency STRING COMMENT 'Extracted currency',
    extracted_debtor_name STRING COMMENT 'Extracted debtor name',
    extracted_creditor_name STRING COMMENT 'Extracted creditor name',

    -- Processing Flags
    is_processed BOOLEAN DEFAULT FALSE COMMENT 'Processed to Silver',
    processed_timestamp TIMESTAMP COMMENT 'When processed to Silver',
    processing_attempts INT DEFAULT 0 COMMENT 'Number of processing attempts',

    -- Partitioning
    partition_date DATE NOT NULL COMMENT 'Partition date',
    region STRING NOT NULL COMMENT 'Region: US, EMEA, APAC, LATAM'
)
USING DELTA
PARTITIONED BY (partition_date, source_system, region)
CLUSTER BY (message_type, ingestion_timestamp)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.logRetentionDuration' = '30 days',
    'delta.deletedFileRetentionDuration' = '7 days',
    'delta.enableChangeDataFeed' = 'true'
)
COMMENT 'Bronze layer: Raw payment messages with ingestion metadata';

-- -----------------------------------------------------------------------------
-- Party Messages (customer/entity data from source systems)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bronze.party_messages (
    message_id STRING NOT NULL,
    message_type STRING NOT NULL COMMENT 'CUSTOMER, ENTITY, KYC, etc.',
    source_system STRING NOT NULL,
    raw_content STRING NOT NULL,
    raw_content_hash STRING,

    -- Extracted Keys
    extracted_party_id STRING,
    extracted_party_type STRING,
    extracted_name STRING,

    -- Ingestion Metadata
    ingestion_timestamp TIMESTAMP NOT NULL,
    ingestion_pipeline_id STRING,
    is_processed BOOLEAN DEFAULT FALSE,
    processed_timestamp TIMESTAMP,

    -- Partitioning
    partition_date DATE NOT NULL,
    region STRING NOT NULL
)
USING DELTA
PARTITIONED BY (partition_date, source_system)
CLUSTER BY (message_type)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- -----------------------------------------------------------------------------
-- Account Messages (account data from source systems)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bronze.account_messages (
    message_id STRING NOT NULL,
    message_type STRING NOT NULL,
    source_system STRING NOT NULL,
    raw_content STRING NOT NULL,
    raw_content_hash STRING,

    -- Extracted Keys
    extracted_account_id STRING,
    extracted_account_number STRING,
    extracted_owner_id STRING,

    -- Ingestion Metadata
    ingestion_timestamp TIMESTAMP NOT NULL,
    ingestion_pipeline_id STRING,
    is_processed BOOLEAN DEFAULT FALSE,
    processed_timestamp TIMESTAMP,

    -- Partitioning
    partition_date DATE NOT NULL,
    region STRING NOT NULL
)
USING DELTA
PARTITIONED BY (partition_date, source_system)
CLUSTER BY (message_type)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- -----------------------------------------------------------------------------
-- Reference Data Messages
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bronze.reference_data_messages (
    message_id STRING NOT NULL,
    reference_type STRING NOT NULL COMMENT 'FI, CLEARING_SYSTEM, CURRENCY, etc.',
    source_system STRING NOT NULL,
    raw_content STRING NOT NULL,

    -- Ingestion Metadata
    ingestion_timestamp TIMESTAMP NOT NULL,
    is_processed BOOLEAN DEFAULT FALSE,

    -- Partitioning
    partition_date DATE NOT NULL
)
USING DELTA
PARTITIONED BY (partition_date, reference_type)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- -----------------------------------------------------------------------------
-- Sanctions/Screening Results (external screening responses)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bronze.screening_results (
    result_id STRING NOT NULL,
    screening_type STRING NOT NULL COMMENT 'SANCTIONS, PEP, ADVERSE_MEDIA',
    provider STRING NOT NULL COMMENT 'Screening provider',
    raw_response STRING NOT NULL,

    -- Reference to screened entity
    entity_type STRING COMMENT 'PAYMENT, PARTY',
    entity_id STRING,

    -- Ingestion Metadata
    ingestion_timestamp TIMESTAMP NOT NULL,
    is_processed BOOLEAN DEFAULT FALSE,

    -- Partitioning
    partition_date DATE NOT NULL
)
USING DELTA
PARTITIONED BY (partition_date, screening_type)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.enableChangeDataFeed' = 'true'
);

-- =============================================================================
-- BRONZE ZONE INDEXES (Z-ORDER optimization)
-- =============================================================================

-- Optimize payment_messages for common query patterns
OPTIMIZE bronze.payment_messages ZORDER BY (message_type, ingestion_timestamp);

-- =============================================================================
-- BRONZE ZONE DATA QUALITY CONSTRAINTS
-- =============================================================================

-- Add constraints for data quality
ALTER TABLE bronze.payment_messages ADD CONSTRAINT pk_message_id PRIMARY KEY (message_id);
ALTER TABLE bronze.party_messages ADD CONSTRAINT pk_party_msg_id PRIMARY KEY (message_id);
ALTER TABLE bronze.account_messages ADD CONSTRAINT pk_account_msg_id PRIMARY KEY (message_id);
