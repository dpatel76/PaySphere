-- GPS CDM - PostgreSQL Database Schema Creation
-- ================================================
-- 4-Layer Medallion Architecture:
--   1. Bronze (raw_)     - Raw data as-is
--   2. Silver (stg_)     - Structured per message type
--   3. Gold (cdm_)       - CDM normalized/unified
--   4. Analytical (anl_) - Data products for consumption
--
-- Run with: psql -d gps_cdm -f 00_create_database.sql

-- Create schemas for 4-Layer Architecture
CREATE SCHEMA IF NOT EXISTS bronze;      -- Raw data as-is
CREATE SCHEMA IF NOT EXISTS silver;      -- Structured per message type
CREATE SCHEMA IF NOT EXISTS gold;        -- CDM normalized
CREATE SCHEMA IF NOT EXISTS analytical;  -- Data products
CREATE SCHEMA IF NOT EXISTS observability; -- Operational metadata

-- Add schema comments
COMMENT ON SCHEMA bronze IS 'Layer 1: Raw data as-is - immutable, append-only (prefix: raw_)';
COMMENT ON SCHEMA silver IS 'Layer 2: Structured per message type - parsed but not unified (prefix: stg_)';
COMMENT ON SCHEMA gold IS 'Layer 3: CDM normalized - unified canonical model (prefix: cdm_)';
COMMENT ON SCHEMA analytical IS 'Layer 4: Data products for consumption - denormalized, aggregated (prefix: anl_)';
COMMENT ON SCHEMA observability IS 'Operational: Lineage, errors, batch tracking, DQ metrics (prefix: obs_)';

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Naming Convention Reference:
-- =============================
-- Bronze:     raw_<source>           e.g., raw_payment_messages
-- Silver:     stg_<message_type>     e.g., stg_pain001, stg_mt103, stg_ach
-- Gold:       cdm_<entity>           e.g., cdm_payment_instruction, cdm_party
-- Analytical: anl_<product>          e.g., anl_payment_360, anl_regulatory_ready
-- Observability: obs_<function>      e.g., obs_batch_tracking, obs_field_lineage

-- Verify schemas created
SELECT schema_name,
       obj_description(oid) as description
FROM pg_namespace
WHERE schema_name IN ('bronze', 'silver', 'gold', 'analytical', 'observability')
ORDER BY schema_name;
