# Databricks notebook source
# MAGIC %md
# MAGIC # GPS CDM - Explore CDM Data
# MAGIC
# MAGIC This notebook provides views and queries for exploring the CDM data lake.
# MAGIC
# MAGIC ## Contents
# MAGIC 1. Pipeline Overview - Batch statistics and lineage
# MAGIC 2. Bronze Layer - Raw payment messages
# MAGIC 3. Silver Layer - Standardized data with DQ scores
# MAGIC 4. Gold Layer - CDM entities
# MAGIC 5. Data Quality Analysis
# MAGIC 6. Time Travel Examples

# COMMAND ----------

CDM_DATABASE = "cdm_dev"
spark.sql(f"USE {CDM_DATABASE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Pipeline Overview

# COMMAND ----------

# MAGIC %md
# MAGIC ### Recent Batches

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     batch_id,
# MAGIC     status,
# MAGIC     total_records,
# MAGIC     processed_records,
# MAGIC     failed_records,
# MAGIC     ROUND((processed_records / NULLIF(total_records, 0)) * 100, 2) as success_rate_pct,
# MAGIC     started_at,
# MAGIC     completed_at,
# MAGIC     ROUND(TIMESTAMPDIFF(SECOND, started_at, completed_at), 2) as duration_seconds
# MAGIC FROM batch_tracking
# MAGIC ORDER BY started_at DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ### Data Lineage Trail

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     batch_id,
# MAGIC     source_layer,
# MAGIC     target_layer,
# MAGIC     source_table,
# MAGIC     target_table,
# MAGIC     record_count,
# MAGIC     created_at
# MAGIC FROM data_lineage
# MAGIC ORDER BY created_at DESC
# MAGIC LIMIT 20

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Bronze Layer - Raw Messages

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Message type distribution
# MAGIC SELECT
# MAGIC     message_type,
# MAGIC     COUNT(*) as message_count,
# MAGIC     MIN(creation_datetime) as first_message,
# MAGIC     MAX(creation_datetime) as last_message
# MAGIC FROM bronze_raw_payment
# MAGIC GROUP BY message_type
# MAGIC ORDER BY message_count DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Recent raw messages
# MAGIC SELECT
# MAGIC     raw_id,
# MAGIC     message_type,
# MAGIC     message_id,
# MAGIC     file_name,
# MAGIC     LENGTH(raw_xml) as xml_size_bytes,
# MAGIC     _ingested_at
# MAGIC FROM bronze_raw_payment
# MAGIC ORDER BY _ingested_at DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Silver Layer - Standardized Data

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Silver layer summary
# MAGIC SELECT
# MAGIC     message_type,
# MAGIC     COUNT(*) as record_count,
# MAGIC     ROUND(AVG(dq_score), 4) as avg_dq_score,
# MAGIC     SUM(CASE WHEN dq_score >= 0.75 THEN 1 ELSE 0 END) as high_quality_count,
# MAGIC     SUM(CASE WHEN dq_score < 0.75 THEN 1 ELSE 0 END) as low_quality_count,
# MAGIC     ROUND(SUM(amount), 2) as total_amount
# MAGIC FROM silver_stg_payment_instruction
# MAGIC GROUP BY message_type

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Sample silver records with all fields
# MAGIC SELECT
# MAGIC     stg_id,
# MAGIC     message_type,
# MAGIC     message_id,
# MAGIC     payment_id,
# MAGIC     amount,
# MAGIC     currency,
# MAGIC     debtor_name,
# MAGIC     debtor_account,
# MAGIC     creditor_name,
# MAGIC     creditor_account,
# MAGIC     dq_score
# MAGIC FROM silver_stg_payment_instruction
# MAGIC ORDER BY _ingested_at DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Gold Layer - CDM Entities

# COMMAND ----------

# MAGIC %md
# MAGIC ### Payment Instructions

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     instruction_id,
# MAGIC     message_type,
# MAGIC     payment_type,
# MAGIC     amount,
# MAGIC     currency,
# MAGIC     status,
# MAGIC     execution_date,
# MAGIC     created_at
# MAGIC FROM gold_cdm_payment_instruction
# MAGIC ORDER BY created_at DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ### Parties

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     party_id,
# MAGIC     party_type,
# MAGIC     name,
# MAGIC     country,
# MAGIC     identification_type,
# MAGIC     created_at
# MAGIC FROM gold_cdm_party
# MAGIC ORDER BY created_at DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ### Accounts

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     a.account_id,
# MAGIC     a.account_number,
# MAGIC     a.account_type,
# MAGIC     a.iban,
# MAGIC     a.bic,
# MAGIC     a.currency,
# MAGIC     a.status,
# MAGIC     p.name as party_name
# MAGIC FROM gold_cdm_account a
# MAGIC LEFT JOIN gold_cdm_party p ON a.party_id = p.party_id
# MAGIC ORDER BY a.created_at DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ### Financial Institutions

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     fi_id,
# MAGIC     bic,
# MAGIC     name,
# MAGIC     lei,
# MAGIC     country,
# MAGIC     clearing_system
# MAGIC FROM gold_cdm_financial_institution
# MAGIC ORDER BY created_at DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Data Quality Analysis

# COMMAND ----------

# MAGIC %sql
# MAGIC -- DQ Score Distribution
# MAGIC SELECT
# MAGIC     CASE
# MAGIC         WHEN dq_score >= 0.9 THEN 'Excellent (90-100%)'
# MAGIC         WHEN dq_score >= 0.75 THEN 'Good (75-89%)'
# MAGIC         WHEN dq_score >= 0.5 THEN 'Fair (50-74%)'
# MAGIC         ELSE 'Poor (<50%)'
# MAGIC     END as quality_tier,
# MAGIC     COUNT(*) as record_count,
# MAGIC     ROUND(AVG(dq_score) * 100, 2) as avg_score_pct
# MAGIC FROM silver_stg_payment_instruction
# MAGIC GROUP BY
# MAGIC     CASE
# MAGIC         WHEN dq_score >= 0.9 THEN 'Excellent (90-100%)'
# MAGIC         WHEN dq_score >= 0.75 THEN 'Good (75-89%)'
# MAGIC         WHEN dq_score >= 0.5 THEN 'Fair (50-74%)'
# MAGIC         ELSE 'Poor (<50%)'
# MAGIC     END
# MAGIC ORDER BY avg_score_pct DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Records with DQ issues
# MAGIC SELECT
# MAGIC     stg_id,
# MAGIC     message_type,
# MAGIC     dq_score,
# MAGIC     dq_issues,
# MAGIC     debtor_name,
# MAGIC     amount
# MAGIC FROM silver_stg_payment_instruction
# MAGIC WHERE dq_score < 0.75
# MAGIC ORDER BY dq_score ASC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Time Travel Examples

# COMMAND ----------

# MAGIC %md
# MAGIC ### View Table History

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE HISTORY silver_stg_payment_instruction LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ### Query Historical Version

# COMMAND ----------

# Example: Query data from a specific version
# Uncomment and adjust version number as needed

# %sql
# SELECT COUNT(*) as record_count
# FROM silver_stg_payment_instruction VERSION AS OF 0

# COMMAND ----------

# MAGIC %md
# MAGIC ### Query Data at Specific Timestamp

# COMMAND ----------

# Example: Query data from a specific timestamp
# Uncomment and adjust timestamp as needed

# %sql
# SELECT COUNT(*) as record_count
# FROM silver_stg_payment_instruction TIMESTAMP AS OF '2024-01-15 10:00:00'

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Processing Errors

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     batch_id,
# MAGIC     layer,
# MAGIC     table_name,
# MAGIC     error_type,
# MAGIC     COUNT(*) as error_count
# MAGIC FROM processing_errors
# MAGIC GROUP BY batch_id, layer, table_name, error_type
# MAGIC ORDER BY error_count DESC
# MAGIC LIMIT 20

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. CDM Entity Relationship View

# COMMAND ----------

# Create comprehensive view of payment with all related entities
payment_view = spark.sql("""
    SELECT
        pi.instruction_id,
        pi.message_type,
        pi.amount,
        pi.currency,
        pi.status,
        pi.execution_date,

        -- Debtor info
        dp.name as debtor_name,
        da.iban as debtor_iban,
        dfi.bic as debtor_bank_bic,

        -- Creditor info
        cp.name as creditor_name,
        ca.iban as creditor_iban,
        cfi.bic as creditor_bank_bic,

        pi.created_at

    FROM gold_cdm_payment_instruction pi
    LEFT JOIN gold_cdm_party dp ON pi.debtor_party_id = dp.party_id
    LEFT JOIN gold_cdm_party cp ON pi.creditor_party_id = cp.party_id
    LEFT JOIN gold_cdm_account da ON pi.debtor_account_id = da.account_id
    LEFT JOIN gold_cdm_account ca ON pi.creditor_account_id = ca.account_id
    LEFT JOIN gold_cdm_financial_institution dfi ON pi.debtor_agent_id = dfi.fi_id
    LEFT JOIN gold_cdm_financial_institution cfi ON pi.creditor_agent_id = cfi.fi_id
    ORDER BY pi.created_at DESC
    LIMIT 20
""")

display(payment_view)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary Statistics

# COMMAND ----------

# Overall statistics
print("="*60)
print("GPS CDM Data Lake Summary")
print("="*60)

stats = {
    "Bronze - Raw Messages": spark.sql("SELECT COUNT(*) as cnt FROM bronze_raw_payment").collect()[0].cnt,
    "Silver - Staged Payments": spark.sql("SELECT COUNT(*) as cnt FROM silver_stg_payment_instruction").collect()[0].cnt,
    "Gold - Payment Instructions": spark.sql("SELECT COUNT(*) as cnt FROM gold_cdm_payment_instruction").collect()[0].cnt,
    "Gold - Parties": spark.sql("SELECT COUNT(*) as cnt FROM gold_cdm_party").collect()[0].cnt,
    "Gold - Accounts": spark.sql("SELECT COUNT(*) as cnt FROM gold_cdm_account").collect()[0].cnt,
    "Gold - Financial Institutions": spark.sql("SELECT COUNT(*) as cnt FROM gold_cdm_financial_institution").collect()[0].cnt,
    "Batches Processed": spark.sql("SELECT COUNT(*) as cnt FROM batch_tracking WHERE status = 'COMPLETED'").collect()[0].cnt,
    "Total Errors": spark.sql("SELECT COUNT(*) as cnt FROM processing_errors").collect()[0].cnt
}

for layer, count in stats.items():
    print(f"  {layer}: {count:,}")
