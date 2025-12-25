-- GPS CDM - Master DDL Script
-- =============================
-- Runs all DDL scripts in order to create complete database schema.
--
-- Usage:
--   createdb gps_cdm
--   psql -d gps_cdm -f 99_run_all.sql
--
-- Or run individual files:
--   psql -d gps_cdm -f 00_create_database.sql
--   psql -d gps_cdm -f 01_bronze_tables.sql
--   ... etc.

\echo '=========================================='
\echo 'GPS CDM - 4-Layer Medallion Architecture'
\echo '=========================================='
\echo ''

-- Step 0: Create schemas
\echo 'Step 0: Creating schemas...'
\i 00_create_database.sql
\echo ''

-- Step 1: Bronze layer (raw_*)
\echo 'Step 1: Creating Bronze layer tables (raw_*)...'
\i 01_bronze_tables.sql
\echo ''

-- Step 2: Silver layer (stg_*)
\echo 'Step 2: Creating Silver layer tables (stg_*)...'
\i 02_silver_tables.sql
\echo ''

-- Step 2b: Silver layer extended (all 63+ message types)
\echo 'Step 2b: Creating Silver layer extended tables (all message types)...'
\i 02b_silver_tables_extended.sql
\echo ''

-- Step 3: Gold layer (cdm_*)
\echo 'Step 3: Creating Gold layer tables (cdm_*)...'
\i 03_gold_cdm_tables.sql
\echo ''

-- Step 4: Analytical layer (anl_*)
\echo 'Step 4: Creating Analytical layer tables (anl_*)...'
\i 04_analytical_tables.sql
\echo ''

-- Step 5: Observability (obs_*)
\echo 'Step 5: Creating Observability tables (obs_*)...'
\i 05_observability_tables.sql
\echo ''

-- Step 6: Auth tables
\echo 'Step 6: Creating Auth tables...'
\i 06_auth_tables.sql
\echo ''

-- Step 7: CDC Triggers
\echo 'Step 7: Creating CDC triggers...'
\i 06_cdc_triggers.sql
\echo ''

-- Step 8: Exception Handling
\echo 'Step 8: Creating Exception handling functions...'
\i 07_exception_handling.sql
\echo ''

-- Summary
\echo '=========================================='
\echo 'Schema Creation Complete!'
\echo '=========================================='
\echo ''
\echo 'Layer Summary:'

SELECT schema_name, COUNT(*) as table_count
FROM information_schema.tables
WHERE table_schema IN ('bronze', 'silver', 'gold', 'analytical', 'observability')
GROUP BY schema_name
ORDER BY schema_name;

\echo ''
\echo 'Naming Convention:'
\echo '  Bronze:       raw_<source>'
\echo '  Silver:       stg_<message_type>'
\echo '  Gold:         cdm_<entity>'
\echo '  Analytical:   anl_<product>'
\echo '  Observability: obs_<function>'
\echo ''
\echo 'All tables created successfully!'
