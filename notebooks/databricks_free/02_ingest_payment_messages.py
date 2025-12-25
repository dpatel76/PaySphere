# Databricks notebook source
# MAGIC %md
# MAGIC # GPS CDM - Ingest Payment Messages
# MAGIC
# MAGIC Processes ISO 20022 payment messages through the medallion architecture.
# MAGIC **Run 01_setup_gps_cdm first!**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Auto-Detect Configuration

# COMMAND ----------

from datetime import datetime
from pyspark.sql.functions import lit, current_timestamp, col
from pyspark.sql.types import DecimalType
import uuid
import xml.etree.ElementTree as ET

# Always auto-detect configuration (Spark conf doesn't persist across sessions)
print("Detecting configuration...")
SCHEMA = "cdm_dev"
CATALOG = None
USE_UNITY_CATALOG = False

try:
    catalogs_df = spark.sql("SHOW CATALOGS")
    catalogs = [row.catalog for row in catalogs_df.collect()]
    current_catalog = spark.sql("SELECT current_catalog()").collect()[0][0]
    print(f"Available catalogs: {catalogs}")
    print(f"Current catalog: {current_catalog}")

    if current_catalog and current_catalog not in ['spark_catalog', 'hive_metastore']:
        CATALOG = current_catalog
        USE_UNITY_CATALOG = True
    elif 'main' in catalogs:
        CATALOG = 'main'
        USE_UNITY_CATALOG = True
    elif catalogs:
        CATALOG = next((c for c in catalogs if c not in ['spark_catalog', 'hive_metastore']), None)
        USE_UNITY_CATALOG = CATALOG is not None
    else:
        CATALOG = None
        USE_UNITY_CATALOG = False
except Exception as e:
    print(f"Catalog detection failed: {e}")
    CATALOG = None
    USE_UNITY_CATALOG = False

VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/cdm_data" if USE_UNITY_CATALOG and CATALOG else None

# Helper function
def get_table_name(table):
    if USE_UNITY_CATALOG and CATALOG:
        return f"{CATALOG}.{SCHEMA}.{table}"
    return f"{SCHEMA}.{table}"

print(f"Catalog: {CATALOG or 'Hive Metastore'}")
print(f"Schema: {SCHEMA}")
print(f"Unity Catalog: {USE_UNITY_CATALOG}")
print(f"Volume Path: {VOLUME_PATH or 'Using DBFS'}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Determine Input Path

# COMMAND ----------

# Try multiple possible input paths
possible_paths = []

if VOLUME_PATH:
    possible_paths.append(f"{VOLUME_PATH}/raw_input")

# DBFS fallbacks
possible_paths.extend([
    "/FileStore/cdm/raw_input",
    "/dbfs/cdm/raw_input",
    "/Workspace/PaymentsCDM/data/raw_input"
])

INPUT_PATH = None
xml_files = []

for path in possible_paths:
    try:
        # Normalize path for dbutils
        check_path = path.replace("/Volumes", "/Volumes")
        files = dbutils.fs.ls(check_path)
        xml_files = [f for f in files if f.name.endswith('.xml')]
        if xml_files:
            INPUT_PATH = path
            print(f"Found {len(xml_files)} XML files at: {path}")
            for f in xml_files:
                print(f"  - {f.name} ({f.size} bytes)")
            break
    except Exception as e:
        continue

if not INPUT_PATH:
    print("No XML files found. Tried:")
    for p in possible_paths:
        print(f"  - {p}")
    print("\nPlease upload XML files to one of these locations.")
    print("You can also paste XML content directly below.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2b: Manual XML Input (Optional)
# MAGIC
# MAGIC If no files found, you can paste XML here:

# COMMAND ----------

# Uncomment and paste XML here if needed:
MANUAL_XML = None

# MANUAL_XML = '''<?xml version="1.0" encoding="UTF-8"?>
# <Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
#   ...your XML here...
# </Document>'''

if not xml_files and MANUAL_XML:
    print("Using manual XML input")
    xml_files = [{"name": "manual_input.xml", "content": MANUAL_XML}]
elif not xml_files:
    # Create sample for demo
    print("No input found - creating sample data for demo...")
    sample_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
  <CstmrCdtTrfInitn>
    <GrpHdr><MsgId>DEMO001</MsgId><CreDtTm>2024-01-15T10:00:00</CreDtTm></GrpHdr>
    <PmtInf>
      <PmtInfId>PMT001</PmtInfId>
      <Dbtr><Nm>Demo Debtor</Nm></Dbtr>
      <DbtrAcct><Id><IBAN>DE89370400440532013000</IBAN></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BIC>COBADEFFXXX</BIC></FinInstnId></DbtrAgt>
      <CdtTrfTxInf>
        <Amt><InstdAmt Ccy="EUR">500.00</InstdAmt></Amt>
        <Cdtr><Nm>Demo Creditor</Nm></Cdtr>
        <CdtrAcct><Id><IBAN>FR1420041010050500013M02606</IBAN></Id></CdtrAcct>
        <CdtrAgt><FinInstnId><BIC>BNPAFRPPXXX</BIC></FinInstnId></CdtrAgt>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>'''
    xml_files = [{"name": "demo_sample.xml", "content": sample_xml, "path": "demo"}]

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Create Batch

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, StringType, LongType, TimestampType

BATCH_ID = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
now = datetime.utcnow()

# Explicit schema for batch tracking
batch_schema = StructType([
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

batch_record = [(
    BATCH_ID,
    INPUT_PATH or "manual_input",
    "auto_detect",
    "PROCESSING",
    len(xml_files),
    0,
    0,
    0,
    now,
    None,
    None,
    None,
    now,
    now
)]

df_batch = spark.createDataFrame(batch_record, batch_schema)
df_batch.write.format("delta").mode("append").saveAsTable(get_table_name('obs_batch_tracking'))
print(f"Started batch: {BATCH_ID}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Bronze Layer

# COMMAND ----------

def detect_message_type(xml_content):
    try:
        root = ET.fromstring(xml_content)
        tag = root.tag.lower()
        if 'pain.001' in tag or 'cstmrcdttrfinitn' in tag:
            return 'pain.001'
        elif 'pain.002' in tag or 'cstmrpmtstsrpt' in tag:
            return 'pain.002'
        elif 'camt.053' in tag or 'bktocstmrstmt' in tag:
            return 'camt.053'
        elif 'camt.054' in tag:
            return 'camt.054'
        elif 'pacs.008' in tag:
            return 'pacs.008'
        return 'unknown'
    except:
        return 'unknown'

def extract_message_id(xml_content):
    try:
        root = ET.fromstring(xml_content)
        for elem in root.iter():
            if elem.tag.endswith('MsgId'):
                return elem.text
        return None
    except:
        return None

# Process files
bronze_records = []

for f in xml_files:
    try:
        # Handle different input types
        if isinstance(f, dict):
            file_name = f.get("name", "unknown.xml")
            content = f.get("content")
            file_path = f.get("path", "manual")
        else:
            file_name = f.name
            file_path = f.path
            content = dbutils.fs.head(file_path, 1024*1024)

        message_type = detect_message_type(content)
        message_id = extract_message_id(content)

        bronze_records.append({
            "raw_id": str(uuid.uuid4()),
            "message_type": message_type,
            "message_id": message_id,
            "creation_datetime": datetime.utcnow(),
            "raw_xml": content,
            "file_name": file_name,
            "file_path": str(file_path),
            "_batch_id": BATCH_ID,
            "_ingested_at": datetime.utcnow()
        })
        print(f"Processed: {file_name} -> {message_type}")

    except Exception as e:
        print(f"Error: {e}")

print(f"\nBronze records: {len(bronze_records)}")

# COMMAND ----------

# Write bronze with explicit schema
bronze_schema = StructType([
    StructField("raw_id", StringType(), False),
    StructField("message_type", StringType(), False),
    StructField("message_id", StringType(), True),
    StructField("creation_datetime", TimestampType(), True),
    StructField("raw_xml", StringType(), True),
    StructField("file_name", StringType(), True),
    StructField("file_path", StringType(), True),
    StructField("_batch_id", StringType(), True),
    StructField("_ingested_at", TimestampType(), True),
])

if bronze_records:
    bronze_tuples = [(
        r["raw_id"], r["message_type"], r.get("message_id"), r.get("creation_datetime"),
        r.get("raw_xml"), r.get("file_name"), r.get("file_path"),
        r.get("_batch_id"), r.get("_ingested_at")
    ) for r in bronze_records]
    df_bronze = spark.createDataFrame(bronze_tuples, bronze_schema)
    df_bronze.write.format("delta").mode("append").partitionBy("message_type") \
        .saveAsTable(get_table_name('bronze_raw_payment'))
    print(f"Wrote {len(bronze_records)} records to bronze")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Silver Layer

# COMMAND ----------

def extract_payment_details(raw_id, message_type, raw_xml):
    result = {
        "stg_id": str(uuid.uuid4()),
        "raw_id": raw_id,
        "message_type": message_type,
        "message_id": None, "payment_id": None, "end_to_end_id": None,
        "instruction_id": None, "amount": None, "currency": None,
        "debtor_name": None, "debtor_account": None,
        "creditor_name": None, "creditor_account": None,
        "creditor_agent_bic": None, "debtor_agent_bic": None,
        "execution_date": None, "created_at": datetime.utcnow(),
        "dq_score": 1.0, "dq_issues": None,
        "_batch_id": None, "_ingested_at": None
    }

    try:
        root = ET.fromstring(raw_xml)

        for elem in root.iter():
            tag = elem.tag.lower()
            text = elem.text

            if 'msgid' in tag and not result["message_id"]:
                result["message_id"] = text
            elif 'pmtinfid' in tag and not result["payment_id"]:
                result["payment_id"] = text
            elif 'endtoendid' in tag and not result["end_to_end_id"]:
                result["end_to_end_id"] = text
            elif 'instdamt' in tag:
                result["amount"] = text
                result["currency"] = elem.get("Ccy")

        # Debtor/Creditor extraction
        for elem in root.iter():
            tag = elem.tag.lower()
            if 'dbtr' in tag and tag.endswith('nm') and not result["debtor_name"]:
                result["debtor_name"] = elem.text
            elif 'cdtr' in tag and tag.endswith('nm') and not result["creditor_name"]:
                result["creditor_name"] = elem.text
            elif 'iban' in tag:
                parent_tag = ""
                for p in root.iter():
                    if elem in p:
                        parent_tag = p.tag.lower()
                        break
                if 'dbtr' in parent_tag and not result["debtor_account"]:
                    result["debtor_account"] = elem.text
                elif 'cdtr' in parent_tag and not result["creditor_account"]:
                    result["creditor_account"] = elem.text

        # Simple IBAN extraction fallback
        ibans = []
        for elem in root.iter():
            if 'iban' in elem.tag.lower() and elem.text:
                ibans.append(elem.text)
        if ibans and not result["debtor_account"]:
            result["debtor_account"] = ibans[0]
        if len(ibans) > 1 and not result["creditor_account"]:
            result["creditor_account"] = ibans[1]

        # BIC extraction
        bics = []
        for elem in root.iter():
            if 'bic' in elem.tag.lower() and elem.text:
                bics.append(elem.text)
        if bics:
            result["debtor_agent_bic"] = bics[0]
        if len(bics) > 1:
            result["creditor_agent_bic"] = bics[1]

        # DQ Score
        required = ['message_id', 'amount', 'debtor_name', 'creditor_name']
        filled = sum(1 for f in required if result.get(f))
        result['dq_score'] = round(filled / len(required), 4)

    except Exception as e:
        result['dq_score'] = 0.0
        result['dq_issues'] = str(e)

    return result

# COMMAND ----------

# Process to silver
silver_records = []
for rec in bronze_records:
    silver_rec = extract_payment_details(rec['raw_id'], rec['message_type'], rec['raw_xml'])
    silver_rec["_batch_id"] = BATCH_ID
    silver_rec["_ingested_at"] = datetime.utcnow()
    silver_records.append(silver_rec)

print(f"Silver records: {len(silver_records)}")

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, StringType, DecimalType, DateType, TimestampType

# Write silver with explicit schema
silver_schema = StructType([
    StructField("stg_id", StringType(), False),
    StructField("raw_id", StringType(), True),
    StructField("message_type", StringType(), False),
    StructField("message_id", StringType(), True),
    StructField("payment_id", StringType(), True),
    StructField("end_to_end_id", StringType(), True),
    StructField("instruction_id", StringType(), True),
    StructField("amount", StringType(), True),  # Will cast to Decimal after
    StructField("currency", StringType(), True),
    StructField("debtor_name", StringType(), True),
    StructField("debtor_account", StringType(), True),
    StructField("creditor_name", StringType(), True),
    StructField("creditor_account", StringType(), True),
    StructField("creditor_agent_bic", StringType(), True),
    StructField("debtor_agent_bic", StringType(), True),
    StructField("execution_date", DateType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("dq_score", StringType(), True),  # Will handle as string
    StructField("dq_issues", StringType(), True),
    StructField("_batch_id", StringType(), True),
    StructField("_ingested_at", TimestampType(), True),
])

if silver_records:
    # Convert to tuples in schema order
    silver_tuples = []
    for r in silver_records:
        silver_tuples.append((
            r.get("stg_id"),
            r.get("raw_id"),
            r.get("message_type"),
            r.get("message_id"),
            r.get("payment_id"),
            r.get("end_to_end_id"),
            r.get("instruction_id"),
            str(r.get("amount")) if r.get("amount") else None,
            r.get("currency"),
            r.get("debtor_name"),
            r.get("debtor_account"),
            r.get("creditor_name"),
            r.get("creditor_account"),
            r.get("creditor_agent_bic"),
            r.get("debtor_agent_bic"),
            r.get("execution_date"),
            r.get("created_at"),
            str(r.get("dq_score")) if r.get("dq_score") is not None else None,
            r.get("dq_issues"),
            r.get("_batch_id"),
            r.get("_ingested_at"),
        ))

    df_silver = spark.createDataFrame(silver_tuples, silver_schema)
    df_silver = df_silver.withColumn("amount", col("amount").cast(DecimalType(18, 2)))
    df_silver = df_silver.withColumn("dq_score", col("dq_score").cast(DecimalType(5, 4)))
    df_silver.write.format("delta").mode("append").partitionBy("message_type") \
        .saveAsTable(get_table_name('silver_stg_payment_instruction'))
    print(f"Wrote {len(silver_records)} records to silver")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Gold Layer

# COMMAND ----------

payment_instructions = []
parties = {}
accounts = {}
fis = {}

for rec in silver_records:
    # Payment
    payment_instructions.append({
        "instruction_id": str(uuid.uuid4()),
        "stg_id": rec.get('stg_id'),
        "message_type": rec.get('message_type'),
        "payment_type": "CREDIT_TRANSFER",
        "amount": rec.get('amount'),
        "currency": rec.get('currency'),
        "status": "PENDING",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "_batch_id": BATCH_ID,
        "_ingested_at": datetime.utcnow()
    })

    # Parties
    for name, ptype in [('debtor_name', 'DEBTOR'), ('creditor_name', 'CREDITOR')]:
        if rec.get(name) and rec[name] not in parties:
            parties[rec[name]] = {
                "party_id": str(uuid.uuid4()), "party_type": ptype,
                "name": rec[name], "legal_name": rec[name],
                "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(),
                "_batch_id": BATCH_ID, "_ingested_at": datetime.utcnow()
            }

    # Accounts
    for acc, bic in [('debtor_account', 'debtor_agent_bic'), ('creditor_account', 'creditor_agent_bic')]:
        if rec.get(acc) and rec[acc] not in accounts:
            accounts[rec[acc]] = {
                "account_id": str(uuid.uuid4()), "account_number": rec[acc],
                "account_type": "IBAN", "iban": rec[acc], "bic": rec.get(bic),
                "currency": rec.get('currency'), "status": "ACTIVE",
                "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(),
                "_batch_id": BATCH_ID, "_ingested_at": datetime.utcnow()
            }

    # FIs
    for bic_f in ['debtor_agent_bic', 'creditor_agent_bic']:
        bic = rec.get(bic_f)
        if bic and bic not in fis:
            fis[bic] = {
                "fi_id": str(uuid.uuid4()), "bic": bic,
                "country": bic[4:6] if len(bic) >= 6 else None,
                "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(),
                "_batch_id": BATCH_ID, "_ingested_at": datetime.utcnow()
            }

print(f"Gold entities: {len(payment_instructions)} payments, {len(parties)} parties, {len(accounts)} accounts, {len(fis)} FIs")

# COMMAND ----------

# Define schemas for gold layer tables
payment_schema = StructType([
    StructField("instruction_id", StringType(), False),
    StructField("stg_id", StringType(), True),
    StructField("message_type", StringType(), False),
    StructField("payment_type", StringType(), True),
    StructField("amount", StringType(), True),
    StructField("currency", StringType(), True),
    StructField("status", StringType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("updated_at", TimestampType(), True),
    StructField("_batch_id", StringType(), True),
    StructField("_ingested_at", TimestampType(), True),
])

party_schema = StructType([
    StructField("party_id", StringType(), False),
    StructField("party_type", StringType(), True),
    StructField("name", StringType(), True),
    StructField("legal_name", StringType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("updated_at", TimestampType(), True),
    StructField("_batch_id", StringType(), True),
    StructField("_ingested_at", TimestampType(), True),
])

account_schema = StructType([
    StructField("account_id", StringType(), False),
    StructField("account_number", StringType(), True),
    StructField("account_type", StringType(), True),
    StructField("iban", StringType(), True),
    StructField("bic", StringType(), True),
    StructField("currency", StringType(), True),
    StructField("status", StringType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("updated_at", TimestampType(), True),
    StructField("_batch_id", StringType(), True),
    StructField("_ingested_at", TimestampType(), True),
])

fi_schema = StructType([
    StructField("fi_id", StringType(), False),
    StructField("bic", StringType(), True),
    StructField("country", StringType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("updated_at", TimestampType(), True),
    StructField("_batch_id", StringType(), True),
    StructField("_ingested_at", TimestampType(), True),
])

# Write gold with explicit schemas
if payment_instructions:
    pi_tuples = [(
        p["instruction_id"], p.get("stg_id"), p["message_type"], p.get("payment_type"),
        str(p.get("amount")) if p.get("amount") else None, p.get("currency"), p.get("status"),
        p.get("created_at"), p.get("updated_at"), p.get("_batch_id"), p.get("_ingested_at")
    ) for p in payment_instructions]
    df = spark.createDataFrame(pi_tuples, payment_schema)
    df = df.withColumn("amount", col("amount").cast(DecimalType(18, 2)))
    df.write.format("delta").mode("append").partitionBy("message_type") \
        .saveAsTable(get_table_name('gold_cdm_payment_instruction'))
    print(f"Wrote {len(payment_instructions)} payment instructions")

if list(parties.values()):
    party_tuples = [(
        p["party_id"], p.get("party_type"), p.get("name"), p.get("legal_name"),
        p.get("created_at"), p.get("updated_at"), p.get("_batch_id"), p.get("_ingested_at")
    ) for p in parties.values()]
    spark.createDataFrame(party_tuples, party_schema).write.format("delta").mode("append") \
        .saveAsTable(get_table_name('gold_cdm_party'))
    print(f"Wrote {len(parties)} parties")

if list(accounts.values()):
    acc_tuples = [(
        a["account_id"], a.get("account_number"), a.get("account_type"), a.get("iban"),
        a.get("bic"), a.get("currency"), a.get("status"),
        a.get("created_at"), a.get("updated_at"), a.get("_batch_id"), a.get("_ingested_at")
    ) for a in accounts.values()]
    spark.createDataFrame(acc_tuples, account_schema).write.format("delta").mode("append") \
        .saveAsTable(get_table_name('gold_cdm_account'))
    print(f"Wrote {len(accounts)} accounts")

if list(fis.values()):
    fi_tuples = [(
        f["fi_id"], f.get("bic"), f.get("country"),
        f.get("created_at"), f.get("updated_at"), f.get("_batch_id"), f.get("_ingested_at")
    ) for f in fis.values()]
    spark.createDataFrame(fi_tuples, fi_schema).write.format("delta").mode("append") \
        .saveAsTable(get_table_name('gold_cdm_financial_institution'))
    print(f"Wrote {len(fis)} financial institutions")

print("Gold layer updated")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Complete Batch

# COMMAND ----------

spark.sql(f"""
UPDATE {get_table_name('obs_batch_tracking')}
SET status = 'COMPLETED',
    processed_records = {len(bronze_records)},
    completed_at = current_timestamp(),
    updated_at = current_timestamp()
WHERE batch_id = '{BATCH_ID}'
""")

print(f"Batch {BATCH_ID} completed!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("="*60)
print("GPS CDM Ingestion Complete")
print("="*60)
print(f"\nBatch: {BATCH_ID}")
print(f"\nRecords:")
print(f"  Bronze: {len(bronze_records)}")
print(f"  Silver: {len(silver_records)}")
print(f"  Gold Payments: {len(payment_instructions)}")
print(f"  Gold Parties: {len(parties)}")
print(f"  Gold Accounts: {len(accounts)}")
print(f"  Gold FIs: {len(fis)}")

# Show results
display(spark.sql(f"""
    SELECT instruction_id, message_type, amount, currency, status, created_at
    FROM {get_table_name('gold_cdm_payment_instruction')}
    WHERE _batch_id = '{BATCH_ID}'
"""))
