# Databricks notebook source
# MAGIC %md
# MAGIC # GPS CDM - Ingest Payment Messages
# MAGIC
# MAGIC This notebook ingests ISO 20022 payment messages through the medallion architecture:
# MAGIC 1. **Bronze**: Raw XML storage
# MAGIC 2. **Silver**: Standardized/cleansed data
# MAGIC 3. **Gold**: CDM entity extraction
# MAGIC
# MAGIC ## Input
# MAGIC - Upload XML files to `/cdm/raw_input/`
# MAGIC - Supported: pain.001, pain.002, camt.053, camt.054, pacs.008

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

from datetime import datetime
from pyspark.sql.functions import lit, current_timestamp, col, udf
from pyspark.sql.types import StringType, StructType, StructField, DecimalType, DateType
import uuid
from lxml import etree

CDM_DATABASE = "cdm_dev"
INPUT_PATH = "/cdm/raw_input"

# Generate batch ID for this run
BATCH_ID = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
print(f"Processing batch: {BATCH_ID}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: List Available Input Files

# COMMAND ----------

try:
    files = dbutils.fs.ls(INPUT_PATH)
    xml_files = [f for f in files if f.name.endswith('.xml')]
    print(f"Found {len(xml_files)} XML files to process:")
    for f in xml_files:
        print(f"  - {f.name} ({f.size} bytes)")
except Exception as e:
    print(f"No files found at {INPUT_PATH}. Please upload XML files first.")
    print(f"Error: {e}")
    dbutils.notebook.exit("No input files")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Record Batch Start

# COMMAND ----------

from pyspark.sql.functions import lit

# Create batch tracking record
batch_record = [{
    "batch_id": BATCH_ID,
    "source_path": INPUT_PATH,
    "mapping_id": "auto_detect",
    "status": "PROCESSING",
    "total_records": len(xml_files),
    "processed_records": 0,
    "failed_records": 0,
    "checkpoint_offset": 0,
    "started_at": datetime.utcnow(),
    "completed_at": None,
    "last_checkpoint_at": None,
    "error_message": None,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}]

df_batch = spark.createDataFrame(batch_record)
df_batch.write.format("delta").mode("append").saveAsTable(f"{CDM_DATABASE}.batch_tracking")
print(f"Batch {BATCH_ID} started")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Bronze Layer - Raw XML Ingestion

# COMMAND ----------

# Parse XML and extract key metadata
def detect_message_type(xml_content):
    """Detect ISO 20022 message type from XML namespace/root element."""
    try:
        root = etree.fromstring(xml_content.encode())
        # Check root element
        tag = root.tag
        if 'pain.001' in tag or 'CstmrCdtTrfInitn' in tag:
            return 'pain.001'
        elif 'pain.002' in tag or 'CstmrPmtStsRpt' in tag:
            return 'pain.002'
        elif 'camt.053' in tag or 'BkToCstmrStmt' in tag:
            return 'camt.053'
        elif 'camt.054' in tag or 'BkToCstmrDbtCdtNtfctn' in tag:
            return 'camt.054'
        elif 'pacs.008' in tag or 'FIToFICstmrCdtTrf' in tag:
            return 'pacs.008'
        else:
            return 'unknown'
    except:
        return 'unknown'

def extract_message_id(xml_content, message_type):
    """Extract message ID from ISO 20022 XML."""
    try:
        root = etree.fromstring(xml_content.encode())
        # Common XPath for message ID
        ns = {'ns': root.nsmap.get(None, '')}

        # Try common message ID paths
        paths = [
            './/MsgId/text()',
            './/GrpHdr/MsgId/text()',
            './/{*}MsgId/text()',
        ]

        for path in paths:
            result = root.xpath(path, namespaces=ns if ns['ns'] else {})
            if result:
                return str(result[0])
        return None
    except:
        return None

detect_type_udf = udf(detect_message_type, StringType())
extract_id_udf = udf(extract_message_id, StringType())

# COMMAND ----------

# Read and process XML files
bronze_records = []

for f in xml_files:
    file_path = f.path
    file_name = f.name

    try:
        # Read file content
        content = dbutils.fs.head(file_path, 1024*1024)  # Max 1MB per file

        message_type = detect_message_type(content)
        message_id = extract_message_id(content, message_type)

        bronze_records.append({
            "raw_id": str(uuid.uuid4()),
            "message_type": message_type,
            "message_id": message_id,
            "creation_datetime": datetime.utcnow(),
            "raw_xml": content,
            "file_name": file_name,
            "file_path": file_path,
            "_batch_id": BATCH_ID,
            "_ingested_at": datetime.utcnow()
        })

        print(f"Processed: {file_name} -> {message_type}")

    except Exception as e:
        print(f"Error processing {file_name}: {e}")

print(f"\nTotal records for bronze layer: {len(bronze_records)}")

# COMMAND ----------

# Write to bronze layer
if bronze_records:
    df_bronze = spark.createDataFrame(bronze_records)
    df_bronze.write.format("delta").mode("append").partitionBy("message_type").saveAsTable(f"{CDM_DATABASE}.bronze_raw_payment")
    print(f"Wrote {len(bronze_records)} records to bronze layer")
else:
    print("No records to write to bronze layer")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Silver Layer - Standardize and Cleanse

# COMMAND ----------

def extract_payment_details(raw_id, message_type, raw_xml):
    """Extract standardized payment details from ISO 20022 XML."""
    try:
        root = etree.fromstring(raw_xml.encode())

        # Common extraction for pain.001
        result = {
            "stg_id": str(uuid.uuid4()),
            "raw_id": raw_id,
            "message_type": message_type,
            "message_id": None,
            "payment_id": None,
            "end_to_end_id": None,
            "instruction_id": None,
            "amount": None,
            "currency": None,
            "debtor_name": None,
            "debtor_account": None,
            "creditor_name": None,
            "creditor_account": None,
            "creditor_agent_bic": None,
            "debtor_agent_bic": None,
            "execution_date": None,
            "created_at": datetime.utcnow(),
            "dq_score": 1.0,
            "dq_issues": None
        }

        # Extract fields using XPath (namespace-agnostic)
        xpath_mappings = {
            "message_id": ".//{*}MsgId/text()",
            "payment_id": ".//{*}PmtInfId/text()",
            "end_to_end_id": ".//{*}EndToEndId/text()",
            "instruction_id": ".//{*}InstrId/text()",
            "amount": ".//{*}Amt//{*}InstdAmt/text()",
            "currency": ".//{*}Amt//{*}InstdAmt/@Ccy",
            "debtor_name": ".//{*}Dbtr/{*}Nm/text()",
            "debtor_account": ".//{*}DbtrAcct/{*}Id/{*}IBAN/text()",
            "creditor_name": ".//{*}Cdtr/{*}Nm/text()",
            "creditor_account": ".//{*}CdtrAcct/{*}Id/{*}IBAN/text()",
            "creditor_agent_bic": ".//{*}CdtrAgt/{*}FinInstnId/{*}BIC/text()",
            "debtor_agent_bic": ".//{*}DbtrAgt/{*}FinInstnId/{*}BIC/text()",
        }

        for field, xpath in xpath_mappings.items():
            matches = root.xpath(xpath)
            if matches:
                result[field] = str(matches[0])

        # Calculate DQ score based on completeness
        required_fields = ['message_id', 'amount', 'debtor_name', 'creditor_name']
        filled = sum(1 for f in required_fields if result.get(f))
        result['dq_score'] = round(filled / len(required_fields), 4)

        return result

    except Exception as e:
        return {
            "stg_id": str(uuid.uuid4()),
            "raw_id": raw_id,
            "message_type": message_type,
            "dq_score": 0.0,
            "dq_issues": str(e),
            "created_at": datetime.utcnow()
        }

# COMMAND ----------

# Process bronze records to silver
bronze_df = spark.sql(f"""
    SELECT raw_id, message_type, raw_xml
    FROM {CDM_DATABASE}.bronze_raw_payment
    WHERE _batch_id = '{BATCH_ID}'
""")

bronze_records = bronze_df.collect()
silver_records = []

for row in bronze_records:
    silver_record = extract_payment_details(row.raw_id, row.message_type, row.raw_xml)
    silver_record["_batch_id"] = BATCH_ID
    silver_record["_ingested_at"] = datetime.utcnow()
    silver_records.append(silver_record)

print(f"Processed {len(silver_records)} records for silver layer")

# COMMAND ----------

# Write to silver layer
if silver_records:
    df_silver = spark.createDataFrame(silver_records)

    # Cast amount to decimal
    df_silver = df_silver.withColumn("amount", col("amount").cast(DecimalType(18, 2)))

    df_silver.write.format("delta").mode("append").partitionBy("message_type").saveAsTable(f"{CDM_DATABASE}.silver_stg_payment_instruction")
    print(f"Wrote {len(silver_records)} records to silver layer")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Gold Layer - CDM Entity Extraction

# COMMAND ----------

def extract_cdm_entities(silver_records):
    """Extract CDM entities from silver layer records."""
    payment_instructions = []
    parties = {}  # Deduplicate by name
    accounts = {}  # Deduplicate by account number
    fis = {}  # Deduplicate by BIC

    for rec in silver_records:
        stg_id = rec.get('stg_id')

        # Payment Instruction
        payment_instructions.append({
            "instruction_id": str(uuid.uuid4()),
            "stg_id": stg_id,
            "message_type": rec.get('message_type'),
            "payment_type": "CREDIT_TRANSFER",
            "amount": rec.get('amount'),
            "currency": rec.get('currency'),
            "debtor_party_id": None,  # Will link later
            "creditor_party_id": None,
            "debtor_account_id": None,
            "creditor_account_id": None,
            "debtor_agent_id": None,
            "creditor_agent_id": None,
            "execution_date": None,
            "value_date": None,
            "status": "PENDING",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "_batch_id": rec.get('_batch_id'),
            "_ingested_at": datetime.utcnow()
        })

        # Debtor Party
        if rec.get('debtor_name'):
            party_key = rec['debtor_name']
            if party_key not in parties:
                parties[party_key] = {
                    "party_id": str(uuid.uuid4()),
                    "party_type": "DEBTOR",
                    "name": rec['debtor_name'],
                    "legal_name": rec['debtor_name'],
                    "country": None,
                    "address_line1": None,
                    "address_line2": None,
                    "city": None,
                    "postal_code": None,
                    "identification_type": None,
                    "identification_value": None,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "_batch_id": rec.get('_batch_id'),
                    "_ingested_at": datetime.utcnow()
                }

        # Creditor Party
        if rec.get('creditor_name'):
            party_key = rec['creditor_name']
            if party_key not in parties:
                parties[party_key] = {
                    "party_id": str(uuid.uuid4()),
                    "party_type": "CREDITOR",
                    "name": rec['creditor_name'],
                    "legal_name": rec['creditor_name'],
                    "country": None,
                    "address_line1": None,
                    "address_line2": None,
                    "city": None,
                    "postal_code": None,
                    "identification_type": None,
                    "identification_value": None,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "_batch_id": rec.get('_batch_id'),
                    "_ingested_at": datetime.utcnow()
                }

        # Debtor Account
        if rec.get('debtor_account'):
            acc_key = rec['debtor_account']
            if acc_key not in accounts:
                accounts[acc_key] = {
                    "account_id": str(uuid.uuid4()),
                    "party_id": parties.get(rec.get('debtor_name', ''), {}).get('party_id'),
                    "account_number": rec['debtor_account'],
                    "account_type": "IBAN",
                    "currency": rec.get('currency'),
                    "iban": rec['debtor_account'],
                    "bic": rec.get('debtor_agent_bic'),
                    "account_name": None,
                    "status": "ACTIVE",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "_batch_id": rec.get('_batch_id'),
                    "_ingested_at": datetime.utcnow()
                }

        # Creditor Account
        if rec.get('creditor_account'):
            acc_key = rec['creditor_account']
            if acc_key not in accounts:
                accounts[acc_key] = {
                    "account_id": str(uuid.uuid4()),
                    "party_id": parties.get(rec.get('creditor_name', ''), {}).get('party_id'),
                    "account_number": rec['creditor_account'],
                    "account_type": "IBAN",
                    "currency": rec.get('currency'),
                    "iban": rec['creditor_account'],
                    "bic": rec.get('creditor_agent_bic'),
                    "account_name": None,
                    "status": "ACTIVE",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "_batch_id": rec.get('_batch_id'),
                    "_ingested_at": datetime.utcnow()
                }

        # Financial Institutions
        for bic_field, fi_type in [('debtor_agent_bic', 'DEBTOR_AGENT'), ('creditor_agent_bic', 'CREDITOR_AGENT')]:
            if rec.get(bic_field):
                bic = rec[bic_field]
                if bic not in fis:
                    fis[bic] = {
                        "fi_id": str(uuid.uuid4()),
                        "bic": bic,
                        "name": None,
                        "lei": None,
                        "country": bic[4:6] if len(bic) >= 6 else None,  # Extract country from BIC
                        "clearing_system": None,
                        "clearing_member_id": None,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "_batch_id": rec.get('_batch_id'),
                        "_ingested_at": datetime.utcnow()
                    }

    return {
        "payment_instructions": payment_instructions,
        "parties": list(parties.values()),
        "accounts": list(accounts.values()),
        "financial_institutions": list(fis.values())
    }

# COMMAND ----------

# Extract CDM entities
entities = extract_cdm_entities(silver_records)

print(f"Extracted CDM entities:")
print(f"  - Payment Instructions: {len(entities['payment_instructions'])}")
print(f"  - Parties: {len(entities['parties'])}")
print(f"  - Accounts: {len(entities['accounts'])}")
print(f"  - Financial Institutions: {len(entities['financial_institutions'])}")

# COMMAND ----------

# Write to gold layer tables
from decimal import Decimal

# Payment Instructions
if entities['payment_instructions']:
    df_pi = spark.createDataFrame(entities['payment_instructions'])
    df_pi = df_pi.withColumn("amount", col("amount").cast(DecimalType(18, 2)))
    df_pi.write.format("delta").mode("append").partitionBy("message_type").saveAsTable(f"{CDM_DATABASE}.gold_cdm_payment_instruction")

# Parties
if entities['parties']:
    df_parties = spark.createDataFrame(entities['parties'])
    df_parties.write.format("delta").mode("append").saveAsTable(f"{CDM_DATABASE}.gold_cdm_party")

# Accounts
if entities['accounts']:
    df_accounts = spark.createDataFrame(entities['accounts'])
    df_accounts.write.format("delta").mode("append").saveAsTable(f"{CDM_DATABASE}.gold_cdm_account")

# Financial Institutions
if entities['financial_institutions']:
    df_fis = spark.createDataFrame(entities['financial_institutions'])
    df_fis.write.format("delta").mode("append").saveAsTable(f"{CDM_DATABASE}.gold_cdm_financial_institution")

print("Gold layer tables updated successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Update Batch Status

# COMMAND ----------

# Update batch tracking to completed
spark.sql(f"""
UPDATE {CDM_DATABASE}.batch_tracking
SET
    status = 'COMPLETED',
    processed_records = {len(bronze_records)},
    failed_records = 0,
    completed_at = current_timestamp(),
    updated_at = current_timestamp()
WHERE batch_id = '{BATCH_ID}'
""")

print(f"Batch {BATCH_ID} completed successfully!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Write Lineage Records

# COMMAND ----------

lineage_records = [
    {
        "lineage_id": str(uuid.uuid4()),
        "batch_id": BATCH_ID,
        "source_layer": "raw_input",
        "target_layer": "bronze",
        "source_table": "xml_files",
        "target_table": "bronze_raw_payment",
        "record_count": len(bronze_records),
        "mapping_id": "xml_ingest",
        "field_mappings": "{}",
        "created_at": datetime.utcnow()
    },
    {
        "lineage_id": str(uuid.uuid4()),
        "batch_id": BATCH_ID,
        "source_layer": "bronze",
        "target_layer": "silver",
        "source_table": "bronze_raw_payment",
        "target_table": "silver_stg_payment_instruction",
        "record_count": len(silver_records),
        "mapping_id": "iso20022_standardize",
        "field_mappings": "{}",
        "created_at": datetime.utcnow()
    },
    {
        "lineage_id": str(uuid.uuid4()),
        "batch_id": BATCH_ID,
        "source_layer": "silver",
        "target_layer": "gold",
        "source_table": "silver_stg_payment_instruction",
        "target_table": "gold_cdm_*",
        "record_count": len(entities['payment_instructions']),
        "mapping_id": "cdm_entity_extract",
        "field_mappings": "{}",
        "created_at": datetime.utcnow()
    }
]

df_lineage = spark.createDataFrame(lineage_records)
df_lineage.write.format("delta").mode("append").saveAsTable(f"{CDM_DATABASE}.data_lineage")

print(f"Wrote {len(lineage_records)} lineage records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

# Display summary statistics
print("="*60)
print("GPS CDM Ingestion Complete")
print("="*60)
print(f"\nBatch ID: {BATCH_ID}")
print(f"\nRecords processed:")
print(f"  Bronze (raw):    {len(bronze_records)}")
print(f"  Silver (staged): {len(silver_records)}")
print(f"  Gold entities:")
print(f"    - Payment Instructions: {len(entities['payment_instructions'])}")
print(f"    - Parties: {len(entities['parties'])}")
print(f"    - Accounts: {len(entities['accounts'])}")
print(f"    - Financial Institutions: {len(entities['financial_institutions'])}")

# Show sample data
display(spark.sql(f"SELECT * FROM {CDM_DATABASE}.gold_cdm_payment_instruction WHERE _batch_id = '{BATCH_ID}' LIMIT 5"))
