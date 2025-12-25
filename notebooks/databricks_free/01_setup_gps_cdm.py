# Databricks notebook source
# MAGIC %md
# MAGIC # GPS CDM - Databricks Free Edition Setup
# MAGIC
# MAGIC This notebook sets up the GPS CDM data processing pipeline on Databricks Free Edition.
# MAGIC It auto-detects your catalog and handles different workspace configurations.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Discover Available Catalogs

# COMMAND ----------

# Discover what catalogs are available
print("Discovering available catalogs...")

try:
    catalogs_df = spark.sql("SHOW CATALOGS")
    catalogs = [row.catalog for row in catalogs_df.collect()]
    print(f"Available catalogs: {catalogs}")
except Exception as e:
    print(f"Could not list catalogs: {e}")
    catalogs = []

# Try to get current catalog
try:
    current_catalog = spark.sql("SELECT current_catalog()").collect()[0][0]
    print(f"Current catalog: {current_catalog}")
except Exception as e:
    current_catalog = None
    print(f"Could not get current catalog: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Select or Create Catalog

# COMMAND ----------

# Configuration - will auto-detect or use defaults
SCHEMA = "cdm_dev"
VOLUME_NAME = "cdm_data"

# Determine which catalog to use
if current_catalog and current_catalog not in ['spark_catalog', 'hive_metastore']:
    # Use current Unity Catalog
    CATALOG = current_catalog
    USE_UNITY_CATALOG = True
    print(f"Using Unity Catalog: {CATALOG}")
elif 'main' in catalogs:
    CATALOG = 'main'
    USE_UNITY_CATALOG = True
    print(f"Using 'main' catalog")
elif 'hive_metastore' in catalogs or current_catalog == 'spark_catalog':
    # Fallback to Hive metastore (no Unity Catalog)
    CATALOG = None
    USE_UNITY_CATALOG = False
    print("Unity Catalog not available - using Hive metastore")
elif catalogs:
    # Use first available catalog that's not spark_catalog
    CATALOG = next((c for c in catalogs if c not in ['spark_catalog', 'hive_metastore']), catalogs[0])
    USE_UNITY_CATALOG = True
    print(f"Using catalog: {CATALOG}")
else:
    # Default fallback
    CATALOG = None
    USE_UNITY_CATALOG = False
    print("No catalogs found - using default database")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Create Schema/Database

# COMMAND ----------

if USE_UNITY_CATALOG and CATALOG:
    # Unity Catalog mode
    FULL_SCHEMA = f"{CATALOG}.{SCHEMA}"
    spark.sql(f"USE CATALOG {CATALOG}")
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
    print(f"Created schema: {FULL_SCHEMA}")

    # Create volume for file storage
    try:
        spark.sql(f"""
            CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.{VOLUME_NAME}
            COMMENT 'GPS CDM data storage volume'
        """)
        VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME_NAME}"
        print(f"Created volume: {VOLUME_PATH}")
    except Exception as e:
        print(f"Could not create volume (may already exist or not supported): {e}")
        VOLUME_PATH = None
else:
    # Hive metastore mode (no Unity Catalog)
    FULL_SCHEMA = SCHEMA
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")
    spark.sql(f"USE {SCHEMA}")
    print(f"Created database: {SCHEMA}")
    VOLUME_PATH = None
    print("Note: Volumes not available without Unity Catalog. Use DBFS for file storage.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Show Current Configuration

# COMMAND ----------

print("="*60)
print("GPS CDM Configuration")
print("="*60)
print(f"Unity Catalog Mode: {USE_UNITY_CATALOG}")
print(f"Catalog: {CATALOG or 'N/A (Hive metastore)'}")
print(f"Schema: {SCHEMA}")
print(f"Full Schema Path: {FULL_SCHEMA}")
print(f"Volume Path: {VOLUME_PATH or 'N/A (use DBFS)'}")
print("="*60)

# Note: spark.conf.set doesn't work in serverless mode
# The ingestion notebook will auto-detect the same configuration

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Create Observability Tables

# COMMAND ----------

def get_table_name(table):
    """Get full table name based on catalog mode."""
    if USE_UNITY_CATALOG and CATALOG:
        return f"{CATALOG}.{SCHEMA}.{table}"
    return f"{SCHEMA}.{table}"

# Data Lineage Table
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {get_table_name('obs_data_lineage')} (
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
""")
print(f"Created: {get_table_name('obs_data_lineage')}")

# Processing Errors Table
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {get_table_name('obs_processing_errors')} (
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
PARTITIONED BY (layer)
""")
print(f"Created: {get_table_name('obs_processing_errors')}")

# Batch Tracking Table
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {get_table_name('obs_batch_tracking')} (
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
""")
print(f"Created: {get_table_name('obs_batch_tracking')}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Create Bronze Layer Tables

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {get_table_name('bronze_raw_payment')} (
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
PARTITIONED BY (message_type)
""")
print(f"Created: {get_table_name('bronze_raw_payment')}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Create Silver Layer Tables

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {get_table_name('silver_stg_payment_instruction')} (
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
PARTITIONED BY (message_type)
""")
print(f"Created: {get_table_name('silver_stg_payment_instruction')}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8: Create Gold Layer Tables

# COMMAND ----------

# Payment Instruction
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {get_table_name('gold_cdm_payment_instruction')} (
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
PARTITIONED BY (message_type)
""")
print(f"Created: {get_table_name('gold_cdm_payment_instruction')}")

# Party
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {get_table_name('gold_cdm_party')} (
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
""")
print(f"Created: {get_table_name('gold_cdm_party')}")

# Account
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {get_table_name('gold_cdm_account')} (
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
""")
print(f"Created: {get_table_name('gold_cdm_account')}")

# Financial Institution
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {get_table_name('gold_cdm_financial_institution')} (
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
""")
print(f"Created: {get_table_name('gold_cdm_financial_institution')}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 9: Validate Setup

# COMMAND ----------

# List all tables
if USE_UNITY_CATALOG and CATALOG:
    tables = spark.sql(f"SHOW TABLES IN {CATALOG}.{SCHEMA}").collect()
else:
    tables = spark.sql(f"SHOW TABLES IN {SCHEMA}").collect()

print(f"\n{'='*60}")
print("GPS CDM Setup Complete!")
print(f"{'='*60}")
print(f"\nMode: {'Unity Catalog' if USE_UNITY_CATALOG else 'Hive Metastore'}")
print(f"Catalog: {CATALOG or 'N/A'}")
print(f"Schema: {SCHEMA}")
if VOLUME_PATH:
    print(f"Volume: {VOLUME_PATH}")
print(f"\nTables created ({len(tables)}):")
for t in tables:
    print(f"  - {t.tableName}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 10: Test Write/Read

# COMMAND ----------

from datetime import datetime
from pyspark.sql.types import StructType, StructField, StringType, LongType, TimestampType
import uuid

test_batch_id = f"test_{uuid.uuid4().hex[:8]}"
now = datetime.utcnow()

# Define explicit schema to avoid type inference issues with None values
schema = StructType([
    StructField("batch_id", StringType(), False),
    StructField("source_path", StringType(), True),
    StructField("mapping_id", StringType(), True),
    StructField("status", StringType(), False),
    StructField("total_records", LongType(), True),
    StructField("processed_records", LongType(), True),
    StructField("failed_records", LongType(), True),
    StructField("checkpoint_offset", LongType(), True),
    StructField("started_at", TimestampType(), True),
    StructField("completed_at", TimestampType(), True),
    StructField("last_checkpoint_at", TimestampType(), True),
    StructField("error_message", StringType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("updated_at", TimestampType(), True),
])

test_data = [(
    test_batch_id,      # batch_id
    "/test/sample.xml", # source_path
    "pain.001_v3",      # mapping_id
    "COMPLETED",        # status
    100,                # total_records
    95,                 # processed_records
    5,                  # failed_records
    0,                  # checkpoint_offset
    now,                # started_at
    now,                # completed_at
    None,               # last_checkpoint_at
    None,               # error_message
    now,                # created_at
    now,                # updated_at
)]

df = spark.createDataFrame(test_data, schema)
df.write.format("delta").mode("append").saveAsTable(get_table_name('obs_batch_tracking'))

result = spark.sql(f"""
    SELECT batch_id, status, total_records, processed_records
    FROM {get_table_name('obs_batch_tracking')}
    WHERE batch_id = '{test_batch_id}'
""")
display(result)

print(f"\nTest successful! Batch ID: {test_batch_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 11: Create Sample Data
# MAGIC
# MAGIC Run this cell to create a sample XML file for testing.

# COMMAND ----------

sample_pain001 = '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>MSG001</MsgId>
      <CreDtTm>2024-01-15T10:00:00</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>PMT001</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <Dbtr>
        <Nm>John Doe</Nm>
      </Dbtr>
      <DbtrAcct>
        <Id><IBAN>DE89370400440532013000</IBAN></Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId><BIC>COBADEFFXXX</BIC></FinInstnId>
      </DbtrAgt>
      <CdtTrfTxInf>
        <PmtId>
          <EndToEndId>E2E001</EndToEndId>
        </PmtId>
        <Amt>
          <InstdAmt Ccy="EUR">1000.00</InstdAmt>
        </Amt>
        <Cdtr>
          <Nm>Jane Smith</Nm>
        </Cdtr>
        <CdtrAcct>
          <Id><IBAN>FR1420041010050500013M02606</IBAN></Id>
        </CdtrAcct>
        <CdtrAgt>
          <FinInstnId><BIC>BNPAFRPPXXX</BIC></FinInstnId>
        </CdtrAgt>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>'''

# Store sample data based on available storage
if VOLUME_PATH:
    # Unity Catalog with Volumes
    sample_path = f"{VOLUME_PATH}/raw_input/sample_pain001.xml"
    try:
        dbutils.fs.mkdirs(f"{VOLUME_PATH}/raw_input")
        dbutils.fs.put(sample_path, sample_pain001, overwrite=True)
        print(f"Created sample file: {sample_path}")
    except Exception as e:
        print(f"Could not write to volume: {e}")
        print("You can manually upload the XML via the Catalog UI")
else:
    # Fallback to DBFS
    sample_path = "/FileStore/cdm/raw_input/sample_pain001.xml"
    try:
        dbutils.fs.mkdirs("/FileStore/cdm/raw_input")
        dbutils.fs.put(sample_path, sample_pain001, overwrite=True)
        print(f"Created sample file: {sample_path}")
    except Exception as e:
        print(f"Could not write to DBFS: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup Complete!
# MAGIC
# MAGIC You can now run the ingestion notebook. It will auto-detect the same configuration.

# COMMAND ----------

print("="*60)
print("SETUP COMPLETE!")
print("="*60)
print(f"""
Configuration detected:
  Catalog: {CATALOG or 'Hive Metastore'}
  Schema: {SCHEMA}
  Tables: {FULL_SCHEMA}.*

Next steps:
  1. Upload XML files to the volume (or use the sample data created above)
  2. Run 02_ingest_payment_messages notebook
""")
