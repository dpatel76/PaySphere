# Databricks notebook source
# MAGIC %md
# MAGIC # Silver to Gold Aggregation
# MAGIC
# MAGIC Aggregates silver layer CDM data into gold layer analytics-ready tables.
# MAGIC
# MAGIC ## Gold Layer Tables
# MAGIC - `gold.payment_daily_summary` - Daily payment aggregations
# MAGIC - `gold.regulatory_ready` - Transactions ready for regulatory reporting
# MAGIC - `gold.party_360` - Comprehensive party view
# MAGIC - `gold.fraud_signals` - Fraud detection signals
# MAGIC
# MAGIC ## Mapping References
# MAGIC Regulatory eligibility based on requirements in:
# MAGIC - `/registry/requirements/` - Regulatory requirement definitions
# MAGIC - `/documents/mappings/reports/` - Report field mappings

# COMMAND ----------

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col, lit, when, coalesce, sum, count, avg, min, max,
    current_timestamp, current_date, expr,
    collect_list, collect_set, first, last,
    datediff, months_between,
    window, row_number, dense_rank,
    array, array_contains, size,
    struct, to_json
)
from pyspark.sql.window import Window
from typing import Dict, List
from decimal import Decimal

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

CATALOG = "gps_cdm"
SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"
REGULATORY_SCHEMA = "regulatory"

# Regulatory thresholds (from /registry/requirements/)
THRESHOLDS = {
    # US - FinCEN
    "FINCEN_CTR": Decimal("10000.00"),  # USD
    "FINCEN_SAR": Decimal("5000.00"),   # USD

    # Australia - AUSTRAC
    "AUSTRAC_TTR": Decimal("10000.00"), # AUD
    "AUSTRAC_IFTI": None,               # All international transfers

    # Canada - FINTRAC
    "FINTRAC_LCTR": Decimal("10000.00"), # CAD
    "FINTRAC_EFTR": Decimal("10000.00"), # CAD

    # UK
    "UK_SAR": None,  # Suspicion-based
}

# COMMAND ----------

# MAGIC %md
# MAGIC ## Regulatory Eligibility Calculation
# MAGIC
# MAGIC Based on requirements defined in `/registry/requirements/`

# COMMAND ----------

def calculate_regulatory_eligibility(df: DataFrame) -> DataFrame:
    """
    Calculate regulatory report eligibility for each transaction.

    References:
    - /registry/requirements/fincen/ctr/index.yaml - CTR thresholds
    - /registry/requirements/fincen/sar/index.yaml - SAR indicators
    - /registry/requirements/austrac/ifti/index.yaml - IFTI requirements
    - /registry/requirements/fintrac/lctr/index.yaml - LCTR thresholds
    """
    return df.withColumn(
        # FinCEN CTR - Cash >= $10,000 USD
        "fincen_ctr_eligible",
        when(
            (col("instructed_currency") == "USD") &
            (col("instructed_amount") >= 10000) &
            (col("cash_indicator") == True),
            True
        ).otherwise(False)
    ).withColumn(
        "fincen_ctr_reason",
        when(col("fincen_ctr_eligible"), "Cash transaction >= $10,000 USD")
    ).withColumn(
        # FinCEN SAR - Suspicious activity >= $5,000
        "fincen_sar_eligible",
        when(
            (col("instructed_currency") == "USD") &
            (col("instructed_amount") >= 5000) &
            (
                (col("fraud_score") >= 0.7) |
                (col("structuring_indicator") == True) |
                (col("sanctions_hit") == True) |
                (size(col("suspicious_indicators")) > 0)
            ),
            True
        ).otherwise(False)
    ).withColumn(
        "fincen_sar_indicators",
        when(
            col("fincen_sar_eligible"),
            col("suspicious_indicators")
        )
    ).withColumn(
        # AUSTRAC IFTI - All international transfers
        "austrac_ifti_eligible",
        when(
            (col("cross_border_flag") == True) &
            (
                (col("debtor_country") == "AU") |
                (col("creditor_country") == "AU")
            ),
            True
        ).otherwise(False)
    ).withColumn(
        "austrac_ifti_direction",
        when(
            col("austrac_ifti_eligible") & (col("debtor_country") == "AU"),
            "OUT"
        ).when(
            col("austrac_ifti_eligible") & (col("creditor_country") == "AU"),
            "IN"
        )
    ).withColumn(
        # AUSTRAC TTR - Cash >= AUD 10,000
        "austrac_ttr_eligible",
        when(
            (col("instructed_currency") == "AUD") &
            (col("instructed_amount") >= 10000) &
            (col("cash_indicator") == True),
            True
        ).otherwise(False)
    ).withColumn(
        # AUSTRAC SMR - Suspicious matters
        "austrac_smr_eligible",
        when(
            (
                (col("debtor_country") == "AU") |
                (col("creditor_country") == "AU")
            ) &
            (
                (col("fraud_score") >= 0.7) |
                (col("pep_involved") == True) |
                (col("sanctions_hit") == True)
            ),
            True
        ).otherwise(False)
    ).withColumn(
        # FINTRAC LCTR - Cash >= CAD 10,000
        "fintrac_lctr_eligible",
        when(
            (col("instructed_currency") == "CAD") &
            (col("instructed_amount") >= 10000) &
            (col("cash_indicator") == True),
            True
        ).otherwise(False)
    ).withColumn(
        # FINTRAC STR - Suspicious transactions
        "fintrac_str_eligible",
        when(
            (
                (col("debtor_country") == "CA") |
                (col("creditor_country") == "CA")
            ) &
            (
                (col("fraud_score") >= 0.7) |
                (col("structuring_indicator") == True)
            ),
            True
        ).otherwise(False)
    ).withColumn(
        # FINTRAC EFTR - EFT >= CAD 10,000
        "fintrac_eftr_eligible",
        when(
            (col("instructed_currency") == "CAD") &
            (col("instructed_amount") >= 10000) &
            (col("cross_border_flag") == True),
            True
        ).otherwise(False)
    ).withColumn(
        # UK SAR - Suspicious activity
        "uk_sar_eligible",
        when(
            (
                (col("debtor_country") == "GB") |
                (col("creditor_country") == "GB")
            ) &
            (
                (col("fraud_score") >= 0.7) |
                (col("pep_involved") == True) |
                (col("sanctions_hit") == True)
            ),
            True
        ).otherwise(False)
    ).withColumn(
        # APAC STRs - JFIU (HK), STRO (SG), JAFIC (JP)
        "jfiu_str_eligible",
        when(
            (col("debtor_country") == "HK") | (col("creditor_country") == "HK"),
            col("fraud_score") >= 0.7
        ).otherwise(False)
    ).withColumn(
        "stro_str_eligible",
        when(
            (col("debtor_country") == "SG") | (col("creditor_country") == "SG"),
            col("fraud_score") >= 0.7
        ).otherwise(False)
    ).withColumn(
        "jafic_str_eligible",
        when(
            (col("debtor_country") == "JP") | (col("creditor_country") == "JP"),
            col("fraud_score") >= 0.7
        ).otherwise(False)
    ).withColumn(
        # OFAC Blocking
        "ofac_blocking_eligible",
        col("sanctions_hit") == True
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Table Builders

# COMMAND ----------

def build_payment_daily_summary() -> DataFrame:
    """
    Build daily payment summary aggregations.

    Aggregates by date, scheme, currency, direction.
    """
    payments = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.payment")
    instructions = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.payment_instruction")

    # Join payment with instruction
    joined = payments.join(
        instructions,
        payments.payment_id == instructions.payment_id,
        "left"
    )

    # Aggregate by day
    summary = joined.groupBy(
        expr("date(created_at)").alias("transaction_date"),
        "scheme_code",
        "instructed_currency",
        "direction",
        "region"
    ).agg(
        count("*").alias("transaction_count"),
        sum("instructed_amount").alias("total_amount"),
        avg("instructed_amount").alias("avg_amount"),
        min("instructed_amount").alias("min_amount"),
        max("instructed_amount").alias("max_amount"),
        sum(when(col("cross_border_flag"), 1).otherwise(0)).alias("cross_border_count"),
        sum(when(col("status") == "COMPLETED", 1).otherwise(0)).alias("completed_count"),
        sum(when(col("status") == "FAILED", 1).otherwise(0)).alias("failed_count"),
        sum(when(col("status") == "RETURNED", 1).otherwise(0)).alias("returned_count"),
    ).withColumn(
        "success_rate",
        col("completed_count") / col("transaction_count") * 100
    ).withColumn(
        "cross_border_percentage",
        col("cross_border_count") / col("transaction_count") * 100
    ).withColumn(
        "generated_timestamp",
        current_timestamp()
    )

    return summary


def build_regulatory_ready() -> DataFrame:
    """
    Build regulatory-ready transaction view with all eligibility flags.

    References:
    - /cdm/physical-model/databricks/04_requirement_traceability.sql
    - /registry/requirements/
    """
    payments = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.payment")
    instructions = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.payment_instruction")
    parties = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.party")

    # Join payment with instruction
    joined = payments.join(
        instructions,
        payments.payment_id == instructions.payment_id,
        "left"
    )

    # Add compliance fields (would come from compliance tables)
    with_compliance = joined.withColumn(
        "cash_indicator", lit(False)  # Placeholder
    ).withColumn(
        "fraud_score", lit(0.0)
    ).withColumn(
        "structuring_indicator", lit(False)
    ).withColumn(
        "sanctions_hit", lit(False)
    ).withColumn(
        "pep_involved", lit(False)
    ).withColumn(
        "suspicious_indicators", array()
    ).withColumn(
        "debtor_country", lit("US")  # Would come from party
    ).withColumn(
        "creditor_country", lit("US")  # Would come from party
    )

    # Calculate eligibility
    regulatory_ready = calculate_regulatory_eligibility(with_compliance)

    # Select final columns
    result = regulatory_ready.select(
        col("payment_id").alias("transaction_id"),
        "payment_id",
        current_timestamp().alias("evaluation_timestamp"),

        # FinCEN
        "fincen_ctr_eligible",
        "fincen_ctr_reason",
        "fincen_sar_eligible",
        "fincen_sar_indicators",

        # AUSTRAC
        "austrac_ifti_eligible",
        "austrac_ifti_direction",
        "austrac_ttr_eligible",
        "austrac_smr_eligible",

        # FINTRAC
        "fintrac_lctr_eligible",
        "fintrac_str_eligible",
        "fintrac_eftr_eligible",

        # UK
        "uk_sar_eligible",

        # APAC
        "jfiu_str_eligible",
        "stro_str_eligible",
        "jafic_str_eligible",

        # OFAC
        "ofac_blocking_eligible",

        # Amounts for threshold comparison
        col("instructed_amount").alias("amount_original"),
        col("instructed_currency").alias("currency_original"),

        # Risk indicators
        "cash_indicator",
        "cross_border_flag",
        "pep_involved",
        "sanctions_hit",
        "structuring_indicator",

        # Metadata
        current_date().alias("partition_date"),
    )

    return result


def build_party_360() -> DataFrame:
    """
    Build comprehensive party view with transaction history.

    Aggregates all party interactions for KYC/AML analysis.
    """
    parties = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.party")
    instructions = spark.table(f"{CATALOG}.{SILVER_SCHEMA}.payment_instruction")

    # Get transaction counts by party
    debtor_txns = instructions.groupBy("debtor_id").agg(
        count("*").alias("debtor_transaction_count"),
        sum("instructed_amount").alias("total_sent_amount"),
        max("requested_execution_date").alias("last_sent_date"),
    ).withColumnRenamed("debtor_id", "party_id")

    creditor_txns = instructions.groupBy("creditor_id").agg(
        count("*").alias("creditor_transaction_count"),
        sum("instructed_amount").alias("total_received_amount"),
        max("requested_execution_date").alias("last_received_date"),
    ).withColumnRenamed("creditor_id", "party_id")

    # Join with party master
    party_360 = parties.join(
        debtor_txns, "party_id", "left"
    ).join(
        creditor_txns, "party_id", "left"
    ).withColumn(
        "total_transaction_count",
        coalesce(col("debtor_transaction_count"), lit(0)) +
        coalesce(col("creditor_transaction_count"), lit(0))
    ).withColumn(
        "total_amount",
        coalesce(col("total_sent_amount"), lit(0)) +
        coalesce(col("total_received_amount"), lit(0))
    ).withColumn(
        "last_activity_date",
        when(
            col("last_sent_date") > col("last_received_date"),
            col("last_sent_date")
        ).otherwise(col("last_received_date"))
    ).withColumn(
        "generated_timestamp",
        current_timestamp()
    )

    return party_360

# COMMAND ----------

# MAGIC %md
# MAGIC ## Main Pipeline

# COMMAND ----------

def run_silver_to_gold_aggregation() -> Dict[str, int]:
    """
    Run all silver to gold aggregations.

    Returns:
        Dictionary with record counts per gold table
    """
    results = {}

    # Build payment daily summary
    summary_df = build_payment_daily_summary()
    summary_df.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(f"{CATALOG}.{GOLD_SCHEMA}.payment_daily_summary")
    results["payment_daily_summary"] = summary_df.count()

    # Build regulatory ready
    regulatory_df = build_regulatory_ready()
    regulatory_df.write \
        .format("delta") \
        .mode("overwrite") \
        .partitionBy("partition_date") \
        .saveAsTable(f"{CATALOG}.{GOLD_SCHEMA}.regulatory_ready")
    results["regulatory_ready"] = regulatory_df.count()

    # Build party 360
    party_df = build_party_360()
    party_df.write \
        .format("delta") \
        .mode("overwrite") \
        .saveAsTable(f"{CATALOG}.{GOLD_SCHEMA}.party_360")
    results["party_360"] = party_df.count()

    return results

# COMMAND ----------

# MAGIC %md
# MAGIC ## Execute

# COMMAND ----------

# Uncomment to run:
# results = run_silver_to_gold_aggregation()
# print(f"Gold layer results: {results}")
