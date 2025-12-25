# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze to Silver Transformation
# MAGIC
# MAGIC Transforms raw payment messages from bronze layer to CDM-conformant silver layer.
# MAGIC
# MAGIC ## Mapping References
# MAGIC Comprehensive field mappings are documented in:
# MAGIC - `/documents/mappings/standards/` - Payment standard mappings (69 standards)
# MAGIC - `/documents/mappings/reports/` - Regulatory report mappings (32+ reports)
# MAGIC
# MAGIC Note: CDM attribute names may differ slightly from mapping documents.
# MAGIC This notebook implements the canonical CDM transformations.

# COMMAND ----------

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col, lit, when, coalesce, concat, concat_ws,
    current_timestamp, expr, from_json, get_json_object,
    regexp_extract, split, trim, upper, lower,
    to_date, to_timestamp, date_format,
    sha2, md5, uuid,
    struct, array, map_from_arrays,
    row_number, lead, lag
)
from pyspark.sql.types import (
    StructType, StructField, StringType, DecimalType,
    TimestampType, DateType, BooleanType, IntegerType,
    ArrayType, MapType
)
from pyspark.sql.window import Window
from typing import Dict, List, Optional
from datetime import datetime
import json

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Catalog and schema configuration
CATALOG = "gps_cdm"
BRONZE_SCHEMA = "bronze"
SILVER_SCHEMA = "silver"

# Batch configuration
spark.conf.set("spark.sql.shuffle.partitions", "200")
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Mapping Registry
# MAGIC
# MAGIC Field mappings based on comprehensive documents in /documents/mappings/

# COMMAND ----------

class MappingRegistry:
    """
    Field mapping registry for bronze to silver transformation.

    References comprehensive mapping documents:
    - standards/ISO20022_pain001_CustomerCreditTransfer_Mapping.md
    - standards/ISO20022_pacs008_FICreditTransfer_Mapping.md
    - standards/SWIFT_MT103_SingleCustomerCreditTransfer_Mapping.md
    - etc.
    """

    # ISO 20022 pain.001 mappings (from mapping doc: 156 fields)
    PAIN001_MAPPINGS = {
        # Group Header
        "GrpHdr.MsgId": ("payment_instruction", "end_to_end_id"),
        "GrpHdr.CreDtTm": ("payment", "created_at"),
        "GrpHdr.NbOfTxs": ("payment", "transaction_count"),
        "GrpHdr.InitgPty.Nm": ("party", "name"),

        # Payment Info
        "PmtInf.PmtInfId": ("payment_instruction", "instruction_id_ext"),
        "PmtInf.PmtMtd": ("payment_instruction", "payment_method"),
        "PmtInf.ReqdExctnDt": ("payment_instruction", "requested_execution_date"),
        "PmtInf.PmtTpInf.InstrPrty": ("payment", "priority"),
        "PmtInf.PmtTpInf.SvcLvl.Cd": ("payment_instruction", "service_level"),
        "PmtInf.ChrgBr": ("payment_instruction", "charge_bearer"),

        # Debtor
        "PmtInf.Dbtr.Nm": ("party", "name"),
        "PmtInf.Dbtr.PstlAdr.Ctry": ("party", "address_country"),
        "PmtInf.DbtrAcct.Id.IBAN": ("account", "iban"),
        "PmtInf.DbtrAcct.Id.Othr.Id": ("account", "account_number"),
        "PmtInf.DbtrAgt.FinInstnId.BICFI": ("financial_institution", "bic"),

        # Credit Transfer Transaction
        "CdtTrfTxInf.PmtId.InstrId": ("payment_instruction", "instruction_id_ext"),
        "CdtTrfTxInf.PmtId.EndToEndId": ("payment_instruction", "end_to_end_id"),
        "CdtTrfTxInf.PmtId.UETR": ("payment_instruction", "uetr"),
        "CdtTrfTxInf.Amt.InstdAmt": ("payment_instruction", "instructed_amount"),
        "CdtTrfTxInf.Amt.InstdAmt.Ccy": ("payment_instruction", "instructed_currency"),
        "CdtTrfTxInf.XchgRateInf.XchgRate": ("payment_instruction", "exchange_rate"),

        # Creditor
        "CdtTrfTxInf.Cdtr.Nm": ("party", "name"),
        "CdtTrfTxInf.Cdtr.PstlAdr.Ctry": ("party", "address_country"),
        "CdtTrfTxInf.CdtrAcct.Id.IBAN": ("account", "iban"),
        "CdtTrfTxInf.CdtrAgt.FinInstnId.BICFI": ("financial_institution", "bic"),

        # Remittance
        "CdtTrfTxInf.RmtInf.Ustrd": ("payment_instruction", "remittance_unstructured"),
    }

    # ISO 20022 pacs.008 mappings (from mapping doc: 142 fields)
    PACS008_MAPPINGS = {
        "GrpHdr.MsgId": ("payment", "message_id"),
        "GrpHdr.CreDtTm": ("payment", "created_at"),
        "CdtTrfTxInf.PmtId.InstrId": ("payment_instruction", "instruction_id_ext"),
        "CdtTrfTxInf.PmtId.EndToEndId": ("payment_instruction", "end_to_end_id"),
        "CdtTrfTxInf.PmtId.TxId": ("payment_instruction", "transaction_id"),
        "CdtTrfTxInf.PmtId.UETR": ("payment_instruction", "uetr"),
        "CdtTrfTxInf.IntrBkSttlmAmt": ("payment_instruction", "interbank_settlement_amount"),
        "CdtTrfTxInf.IntrBkSttlmDt": ("payment_instruction", "settlement_date"),
        "CdtTrfTxInf.InstdAmt": ("payment_instruction", "instructed_amount"),
        "CdtTrfTxInf.XchgRate": ("payment_instruction", "exchange_rate"),
        "CdtTrfTxInf.ChrgBr": ("payment_instruction", "charge_bearer"),
    }

    # SWIFT MT103 mappings (from mapping doc: 58 fields)
    MT103_MAPPINGS = {
        "F20": ("payment_instruction", "transaction_id"),
        "F21": ("payment_instruction", "end_to_end_id"),
        "F32A_Date": ("payment_instruction", "value_date"),
        "F32A_Currency": ("payment_instruction", "instructed_currency"),
        "F32A_Amount": ("payment_instruction", "instructed_amount"),
        "F50K": ("party", "name"),  # Ordering customer
        "F52A": ("financial_institution", "bic"),  # Ordering institution
        "F53A": ("financial_institution", "bic"),  # Sender's correspondent
        "F54A": ("financial_institution", "bic"),  # Receiver's correspondent
        "F56A": ("financial_institution", "bic"),  # Intermediary
        "F57A": ("financial_institution", "bic"),  # Account with institution
        "F59": ("party", "name"),  # Beneficiary
        "F70": ("payment_instruction", "remittance_unstructured"),
        "F71A": ("payment_instruction", "charge_bearer"),
        "F121": ("payment_instruction", "uetr"),
    }

    # Priority code mapping
    PRIORITY_CODES = {
        "HIGH": "HIGH",
        "NORM": "NORM",
        "URGN": "URGP",
        "LOWPRTY": "LOW",
    }

    # Charge bearer mapping
    CHARGE_BEARER_CODES = {
        "DEBT": "DEBT",
        "CRED": "CRED",
        "SHAR": "SHAR",
        "SLEV": "SLEV",
        "BEN": "CRED",  # MT103
        "OUR": "DEBT",  # MT103
        "SHA": "SHAR",  # MT103
    }

    @classmethod
    def get_mappings_for_format(cls, message_type: str) -> Dict:
        """Get field mappings for a specific message type."""
        format_mappings = {
            "pain.001": cls.PAIN001_MAPPINGS,
            "pacs.008": cls.PACS008_MAPPINGS,
            "MT103": cls.MT103_MAPPINGS,
        }
        return format_mappings.get(message_type, {})

# COMMAND ----------

# MAGIC %md
# MAGIC ## Bronze to Silver Transformers

# COMMAND ----------

class PaymentTransformer:
    """Transform bronze payment messages to silver CDM entities."""

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.registry = MappingRegistry()

    def transform_iso20022_pain001(self, df: DataFrame) -> Dict[str, DataFrame]:
        """
        Transform ISO 20022 pain.001 messages to CDM.

        Reference: /documents/mappings/standards/ISO20022_pain001_CustomerCreditTransfer_Mapping.md
        """
        # Parse JSON payload
        parsed_df = df.withColumn(
            "parsed",
            from_json(col("raw_payload"), self._get_pain001_schema())
        )

        # Create Payment entity
        payment_df = parsed_df.select(
            expr("uuid()").alias("payment_id"),
            lit("CREDIT_TRANSFER").alias("payment_type"),
            col("source_scheme").alias("scheme_code"),
            lit("INITIATED").alias("status"),
            when(col("parsed.cross_border_indicator") == "true", lit("OUTBOUND"))
                .otherwise(lit("INTERNAL")).alias("direction"),
            col("parsed.cross_border_indicator").cast("boolean").alias("cross_border_flag"),
            coalesce(
                col("parsed.GrpHdr.PmtTpInf.InstrPrty"),
                lit("NORM")
            ).alias("priority"),
            to_timestamp(col("parsed.GrpHdr.CreDtTm")).alias("created_at"),
            current_timestamp().alias("valid_from"),
            lit(None).cast("date").alias("valid_to"),
            lit(True).alias("is_current"),
            col("source_system"),
            col("source_record_id").alias("source_system_record_id"),
            lit("pain.001").alias("source_message_type"),
            col("ingestion_timestamp"),
            current_timestamp().alias("bronze_to_silver_timestamp"),
            # Partitioning
            expr("year(current_date())").alias("partition_year"),
            expr("month(current_date())").alias("partition_month"),
            coalesce(col("region"), lit("GLOBAL")).alias("region"),
        )

        # Create PaymentInstruction entity
        instruction_df = parsed_df.select(
            expr("uuid()").alias("instruction_id"),
            expr("uuid()").alias("payment_id"),  # Will be joined
            col("parsed.CdtTrfTxInf.PmtId.EndToEndId").alias("end_to_end_id"),
            col("parsed.CdtTrfTxInf.PmtId.UETR").alias("uetr"),
            col("parsed.CdtTrfTxInf.PmtId.InstrId").alias("instruction_id_ext"),
            col("parsed.CdtTrfTxInf.Amt.InstdAmt._text").cast("decimal(18,4)").alias("instructed_amount"),
            col("parsed.CdtTrfTxInf.Amt.InstdAmt.Ccy").alias("instructed_currency"),
            to_date(col("parsed.PmtInf.ReqdExctnDt")).alias("requested_execution_date"),
            self._map_charge_bearer(col("parsed.PmtInf.ChrgBr")).alias("charge_bearer"),
            col("parsed.CdtTrfTxInf.RmtInf.Ustrd").alias("remittance_unstructured"),
        )

        # Create Party entities (Debtor)
        debtor_df = parsed_df.select(
            expr("uuid()").alias("party_id"),
            lit("INDIVIDUAL").alias("party_type"),
            col("parsed.PmtInf.Dbtr.Nm").alias("name"),
            col("parsed.PmtInf.Dbtr.PstlAdr.Ctry").alias("address_country"),
            lit("DEBTOR").alias("party_role"),
        )

        # Create Party entities (Creditor)
        creditor_df = parsed_df.select(
            expr("uuid()").alias("party_id"),
            lit("INDIVIDUAL").alias("party_type"),
            col("parsed.CdtTrfTxInf.Cdtr.Nm").alias("name"),
            col("parsed.CdtTrfTxInf.Cdtr.PstlAdr.Ctry").alias("address_country"),
            lit("CREDITOR").alias("party_role"),
        )

        parties_df = debtor_df.union(creditor_df)

        return {
            "payment": payment_df,
            "payment_instruction": instruction_df,
            "party": parties_df,
        }

    def transform_swift_mt103(self, df: DataFrame) -> Dict[str, DataFrame]:
        """
        Transform SWIFT MT103 messages to CDM.

        Reference: /documents/mappings/standards/SWIFT_MT103_SingleCustomerCreditTransfer_Mapping.md
        """
        # Parse MT103 fields from raw content
        parsed_df = df.withColumn(
            "F20", regexp_extract(col("raw_payload"), r":20:(.+?)(?:\r?\n|$)", 1)
        ).withColumn(
            "F21", regexp_extract(col("raw_payload"), r":21:(.+?)(?:\r?\n|$)", 1)
        ).withColumn(
            "F32A", regexp_extract(col("raw_payload"), r":32A:(\d{6})([A-Z]{3})([\d,\.]+)", 0)
        ).withColumn(
            "F32A_Date", regexp_extract(col("raw_payload"), r":32A:(\d{6})", 1)
        ).withColumn(
            "F32A_Currency", regexp_extract(col("raw_payload"), r":32A:\d{6}([A-Z]{3})", 1)
        ).withColumn(
            "F32A_Amount", regexp_extract(col("raw_payload"), r":32A:\d{6}[A-Z]{3}([\d,\.]+)", 1)
        ).withColumn(
            "F50K", regexp_extract(col("raw_payload"), r":50[AFK]:(.+?)(?=:\d{2}[A-Z]?:|$)", 1)
        ).withColumn(
            "F59", regexp_extract(col("raw_payload"), r":59[A]?:(.+?)(?=:\d{2}[A-Z]?:|$)", 1)
        ).withColumn(
            "F71A", regexp_extract(col("raw_payload"), r":71A:(.+?)(?:\r?\n|$)", 1)
        ).withColumn(
            "F121", regexp_extract(col("raw_payload"), r"\{121:([A-Fa-f0-9\-]+)\}", 1)
        )

        # Create Payment entity
        payment_df = parsed_df.select(
            expr("uuid()").alias("payment_id"),
            lit("CREDIT_TRANSFER").alias("payment_type"),
            lit("SWIFT").alias("scheme_code"),
            lit("INITIATED").alias("status"),
            lit("OUTBOUND").alias("direction"),
            lit(True).alias("cross_border_flag"),
            lit("NORM").alias("priority"),
            current_timestamp().alias("created_at"),
            current_timestamp().alias("valid_from"),
            lit(None).cast("date").alias("valid_to"),
            lit(True).alias("is_current"),
            col("source_system"),
            col("F20").alias("source_system_record_id"),
            lit("MT103").alias("source_message_type"),
            col("ingestion_timestamp"),
            current_timestamp().alias("bronze_to_silver_timestamp"),
            expr("year(current_date())").alias("partition_year"),
            expr("month(current_date())").alias("partition_month"),
            lit("GLOBAL").alias("region"),
        )

        # Create PaymentInstruction entity
        instruction_df = parsed_df.select(
            expr("uuid()").alias("instruction_id"),
            expr("uuid()").alias("payment_id"),
            col("F20").alias("transaction_id"),
            col("F21").alias("end_to_end_id"),
            col("F121").alias("uetr"),
            expr("regexp_replace(F32A_Amount, ',', '.')").cast("decimal(18,4)").alias("instructed_amount"),
            col("F32A_Currency").alias("instructed_currency"),
            expr("to_date(F32A_Date, 'yyMMdd')").alias("value_date"),
            self._map_mt103_charges(col("F71A")).alias("charge_bearer"),
        )

        return {
            "payment": payment_df,
            "payment_instruction": instruction_df,
        }

    def _map_charge_bearer(self, col_expr):
        """Map charge bearer code to CDM enum."""
        return when(col_expr == "DEBT", "DEBT") \
            .when(col_expr == "CRED", "CRED") \
            .when(col_expr == "SHAR", "SHAR") \
            .when(col_expr == "SLEV", "SLEV") \
            .otherwise("SHAR")

    def _map_mt103_charges(self, col_expr):
        """Map MT103 charges code to CDM enum."""
        return when(col_expr == "BEN", "CRED") \
            .when(col_expr == "OUR", "DEBT") \
            .when(col_expr == "SHA", "SHAR") \
            .otherwise("SHAR")

    def _get_pain001_schema(self) -> StructType:
        """Get schema for pain.001 parsed JSON."""
        return StructType([
            StructField("GrpHdr", StructType([
                StructField("MsgId", StringType()),
                StructField("CreDtTm", StringType()),
                StructField("NbOfTxs", StringType()),
                StructField("PmtTpInf", StructType([
                    StructField("InstrPrty", StringType()),
                    StructField("SvcLvl", StructType([
                        StructField("Cd", StringType()),
                    ])),
                ])),
            ])),
            StructField("PmtInf", StructType([
                StructField("PmtInfId", StringType()),
                StructField("ReqdExctnDt", StringType()),
                StructField("ChrgBr", StringType()),
                StructField("Dbtr", StructType([
                    StructField("Nm", StringType()),
                    StructField("PstlAdr", StructType([
                        StructField("Ctry", StringType()),
                    ])),
                ])),
            ])),
            StructField("CdtTrfTxInf", StructType([
                StructField("PmtId", StructType([
                    StructField("InstrId", StringType()),
                    StructField("EndToEndId", StringType()),
                    StructField("UETR", StringType()),
                ])),
                StructField("Amt", StructType([
                    StructField("InstdAmt", StructType([
                        StructField("_text", StringType()),
                        StructField("Ccy", StringType()),
                    ])),
                ])),
                StructField("Cdtr", StructType([
                    StructField("Nm", StringType()),
                    StructField("PstlAdr", StructType([
                        StructField("Ctry", StringType()),
                    ])),
                ])),
                StructField("RmtInf", StructType([
                    StructField("Ustrd", StringType()),
                ])),
            ])),
            StructField("cross_border_indicator", StringType()),
        ])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Main Transformation Pipeline

# COMMAND ----------

def run_bronze_to_silver_transformation(
    message_type: str,
    batch_id: str = None,
    process_date: str = None
) -> Dict[str, int]:
    """
    Run bronze to silver transformation for specified message type.

    Args:
        message_type: Source message type (pain.001, pacs.008, MT103, etc.)
        batch_id: Optional batch identifier for incremental processing
        process_date: Optional date filter (YYYY-MM-DD)

    Returns:
        Dictionary with record counts per entity
    """
    transformer = PaymentTransformer(spark)
    results = {}

    # Read from bronze
    bronze_df = spark.table(f"{CATALOG}.{BRONZE_SCHEMA}.raw_messages")

    # Filter by message type
    filtered_df = bronze_df.filter(col("message_type") == message_type)

    # Apply date filter if provided
    if process_date:
        filtered_df = filtered_df.filter(
            col("ingestion_date") == process_date
        )

    # Apply batch filter if provided
    if batch_id:
        filtered_df = filtered_df.filter(
            col("batch_id") == batch_id
        )

    # Transform based on message type
    if message_type == "pain.001":
        entities = transformer.transform_iso20022_pain001(filtered_df)
    elif message_type == "MT103":
        entities = transformer.transform_swift_mt103(filtered_df)
    else:
        raise ValueError(f"Unsupported message type: {message_type}")

    # Write to silver tables
    for entity_name, entity_df in entities.items():
        table_name = f"{CATALOG}.{SILVER_SCHEMA}.{entity_name}"

        # Merge into existing table
        entity_df.write \
            .format("delta") \
            .mode("append") \
            .option("mergeSchema", "true") \
            .saveAsTable(table_name)

        results[entity_name] = entity_df.count()

    return results

# COMMAND ----------

# MAGIC %md
# MAGIC ## Execute Transformation

# COMMAND ----------

# Example execution
# Uncomment to run:
# results = run_bronze_to_silver_transformation(
#     message_type="pain.001",
#     process_date="2024-12-21"
# )
# print(f"Transformation results: {results}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Mapping Reference Summary
# MAGIC
# MAGIC The comprehensive field mappings in `/documents/mappings/` provide:
# MAGIC
# MAGIC | Category | Documents | Total Fields |
# MAGIC |----------|-----------|--------------|
# MAGIC | ISO 20022 Standards | 34 | ~3,775 |
# MAGIC | SWIFT MT Messages | 20 | ~932 |
# MAGIC | Regional Systems | 20 | ~1,558 |
# MAGIC | Regulatory Reports | 32+ | ~3,900 |
# MAGIC | **Total** | **106+** | **~10,165** |
# MAGIC
# MAGIC This notebook implements core transformations. Full field coverage
# MAGIC should reference the detailed mapping documents.
