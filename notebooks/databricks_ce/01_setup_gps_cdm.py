# Databricks notebook source
# MAGIC %md
# MAGIC # GPS CDM - Databricks Community Edition Setup
# MAGIC
# MAGIC This notebook sets up the GPS CDM data processing pipeline on Databricks Community Edition.
# MAGIC
# MAGIC ## Prerequisites
# MAGIC - Databricks Community Edition account (free at https://community.cloud.databricks.com)
# MAGIC - Upload the GPS CDM wheel package to DBFS
# MAGIC
# MAGIC ## What this notebook does:
# MAGIC 1. Installs the GPS CDM package
# MAGIC 2. Creates the database and tables
# MAGIC 3. Validates the setup

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Install GPS CDM Package
# MAGIC
# MAGIC First, upload the GPS CDM wheel to DBFS, then install it.

# COMMAND ----------

# Install the GPS CDM package from DBFS
# Replace with your actual wheel file path after uploading
# dbutils.library.installPyPI("pyyaml")
# %pip install /dbfs/packages/gps_cdm-0.1.0-py3-none-any.whl

# For development, install dependencies first
%pip install pyyaml pyspark delta-spark lxml

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Configure Storage Paths

# COMMAND ----------

# Configuration - adjust these as needed
CDM_DATABASE = "cdm_dev"
CDM_STORAGE_PATH = "/dbfs/cdm"  # DBFS path for data

# Create base directories
dbutils.fs.mkdirs("/cdm/bronze")
dbutils.fs.mkdirs("/cdm/silver")
dbutils.fs.mkdirs("/cdm/gold")
dbutils.fs.mkdirs("/cdm/observability")
dbutils.fs.mkdirs("/cdm/raw_input")

print(f"Created CDM directories at {CDM_STORAGE_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Create Database and Tables

# COMMAND ----------

# Create the CDM database
spark.sql(f"CREATE DATABASE IF NOT EXISTS {CDM_DATABASE}")
spark.sql(f"USE {CDM_DATABASE}")

print(f"Created and using database: {CDM_DATABASE}")

# COMMAND ----------

# Create observability tables for lineage and error tracking

# Data Lineage Table
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CDM_DATABASE}.data_lineage (
    lineage_id STRING NOT NULL,
    batch_id STRING NOT NULL,
    source_layer STRING NOT NULL,
    target_layer STRING NOT NULL,
    source_table STRING NOT NULL,
    target_table STRING NOT NULL,
    record_count BIGINT,
    mapping_id STRING,
    field_mappings STRING,
    created_at TIMESTAMP
)
USING DELTA
LOCATION '/cdm/observability/data_lineage'
""")

# Processing Errors Table
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CDM_DATABASE}.processing_errors (
    error_id STRING NOT NULL,
    batch_id STRING NOT NULL,
    layer STRING NOT NULL,
    table_name STRING NOT NULL,
    error_type STRING NOT NULL,
    error_message STRING,
    record_data STRING,
    record_id STRING,
    created_at TIMESTAMP
)
USING DELTA
LOCATION '/cdm/observability/processing_errors'
PARTITIONED BY (layer)
""")

# Batch Tracking Table
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CDM_DATABASE}.batch_tracking (
    batch_id STRING NOT NULL,
    source_path STRING,
    mapping_id STRING,
    status STRING NOT NULL,
    total_records BIGINT,
    processed_records BIGINT,
    failed_records BIGINT,
    checkpoint_offset BIGINT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_checkpoint_at TIMESTAMP,
    error_message STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
USING DELTA
LOCATION '/cdm/observability/batch_tracking'
""")

print("Created observability tables: data_lineage, processing_errors, batch_tracking")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Create Bronze Layer Tables (Raw Payment Messages)

# COMMAND ----------

# Bronze layer table for raw ISO 20022 payment messages
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CDM_DATABASE}.bronze_raw_payment (
    raw_id STRING NOT NULL,
    message_type STRING NOT NULL,
    message_id STRING,
    creation_datetime TIMESTAMP,
    raw_xml STRING,
    file_name STRING,
    file_path STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP
)
USING DELTA
LOCATION '/cdm/bronze/raw_payment'
PARTITIONED BY (message_type)
""")

print("Created bronze layer table: bronze_raw_payment")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Create Silver Layer Tables (Standardized CDM)

# COMMAND ----------

# Silver layer - Standardized payment instruction
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CDM_DATABASE}.silver_stg_payment_instruction (
    stg_id STRING NOT NULL,
    raw_id STRING,
    message_type STRING NOT NULL,
    message_id STRING,
    payment_id STRING,
    end_to_end_id STRING,
    instruction_id STRING,
    amount DECIMAL(18,2),
    currency STRING,
    debtor_name STRING,
    debtor_account STRING,
    creditor_name STRING,
    creditor_account STRING,
    creditor_agent_bic STRING,
    debtor_agent_bic STRING,
    execution_date DATE,
    created_at TIMESTAMP,
    dq_score DECIMAL(5,4),
    dq_issues STRING,
    _batch_id STRING,
    _ingested_at TIMESTAMP
)
USING DELTA
LOCATION '/cdm/silver/stg_payment_instruction'
PARTITIONED BY (message_type)
""")

print("Created silver layer table: silver_stg_payment_instruction")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Create Gold Layer Tables (CDM Entities)

# COMMAND ----------

# Gold layer - CDM Payment Instruction
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CDM_DATABASE}.gold_cdm_payment_instruction (
    instruction_id STRING NOT NULL,
    stg_id STRING,
    message_type STRING NOT NULL,
    payment_type STRING,
    amount DECIMAL(18,2),
    currency STRING,
    debtor_party_id STRING,
    creditor_party_id STRING,
    debtor_account_id STRING,
    creditor_account_id STRING,
    debtor_agent_id STRING,
    creditor_agent_id STRING,
    execution_date DATE,
    value_date DATE,
    status STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _batch_id STRING,
    _ingested_at TIMESTAMP
)
USING DELTA
LOCATION '/cdm/gold/cdm_payment_instruction'
PARTITIONED BY (message_type)
""")

# Gold layer - CDM Party
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CDM_DATABASE}.gold_cdm_party (
    party_id STRING NOT NULL,
    party_type STRING,
    name STRING,
    legal_name STRING,
    country STRING,
    address_line1 STRING,
    address_line2 STRING,
    city STRING,
    postal_code STRING,
    identification_type STRING,
    identification_value STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _batch_id STRING,
    _ingested_at TIMESTAMP
)
USING DELTA
LOCATION '/cdm/gold/cdm_party'
""")

# Gold layer - CDM Account
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CDM_DATABASE}.gold_cdm_account (
    account_id STRING NOT NULL,
    party_id STRING,
    account_number STRING,
    account_type STRING,
    currency STRING,
    iban STRING,
    bic STRING,
    account_name STRING,
    status STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _batch_id STRING,
    _ingested_at TIMESTAMP
)
USING DELTA
LOCATION '/cdm/gold/cdm_account'
""")

# Gold layer - CDM Financial Institution
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CDM_DATABASE}.gold_cdm_financial_institution (
    fi_id STRING NOT NULL,
    bic STRING,
    name STRING,
    lei STRING,
    country STRING,
    clearing_system STRING,
    clearing_member_id STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _batch_id STRING,
    _ingested_at TIMESTAMP
)
USING DELTA
LOCATION '/cdm/gold/cdm_financial_institution'
""")

print("Created gold layer tables: cdm_payment_instruction, cdm_party, cdm_account, cdm_financial_institution")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Validate Setup

# COMMAND ----------

# List all tables in the database
tables = spark.sql(f"SHOW TABLES IN {CDM_DATABASE}").collect()

print(f"\n{'='*60}")
print(f"GPS CDM Setup Complete!")
print(f"{'='*60}")
print(f"\nDatabase: {CDM_DATABASE}")
print(f"Storage Path: {CDM_STORAGE_PATH}")
print(f"\nTables created ({len(tables)}):")
for table in tables:
    print(f"  - {table.tableName}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8: Test Write and Read

# COMMAND ----------

from datetime import datetime
from pyspark.sql.functions import lit, current_timestamp
import uuid

# Test data
test_batch_id = str(uuid.uuid4())[:8]

test_batch = [{
    "batch_id": f"test_{test_batch_id}",
    "source_path": "/cdm/raw_input/test.xml",
    "mapping_id": "pain.001_v3",
    "status": "COMPLETED",
    "total_records": 100,
    "processed_records": 95,
    "failed_records": 5,
    "checkpoint_offset": 0,
    "started_at": datetime.utcnow(),
    "completed_at": datetime.utcnow(),
    "last_checkpoint_at": None,
    "error_message": None,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}]

# Write test record
df = spark.createDataFrame(test_batch)
df.write.format("delta").mode("append").saveAsTable(f"{CDM_DATABASE}.batch_tracking")

# Read back
result = spark.sql(f"SELECT * FROM {CDM_DATABASE}.batch_tracking WHERE batch_id = 'test_{test_batch_id}'")
display(result)

print(f"\nTest write/read successful! Batch ID: test_{test_batch_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps
# MAGIC
# MAGIC 1. Upload your ISO 20022 XML files to `/cdm/raw_input/`
# MAGIC 2. Run the `02_ingest_payment_messages` notebook to process files
# MAGIC 3. View results in the `03_explore_cdm_data` notebook
# MAGIC
# MAGIC ### Supported Message Types
# MAGIC - pain.001 (Customer Credit Transfer Initiation)
# MAGIC - pain.002 (Payment Status Report)
# MAGIC - camt.053 (Bank to Customer Statement)
# MAGIC - camt.054 (Bank to Customer Debit Credit Notification)
# MAGIC - pacs.008 (FI to FI Customer Credit Transfer)
