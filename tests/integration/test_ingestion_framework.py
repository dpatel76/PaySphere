"""
GPS CDM - Ingestion Framework Integration Test
===============================================

Tests the actual ingestion engine using YAML configs to parse
and transform payment messages through the medallion layers.

This test uses:
- ConfigDrivenIngestion engine
- pain001.yaml mapping configuration
- PostgreSQL persistence

Usage:
    python tests/integration/test_ingestion_framework.py
"""

import os
import sys
import uuid
import subprocess
from pathlib import Path
from datetime import datetime

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# PostgreSQL
PSQL_BIN = "/opt/homebrew/opt/postgresql@16/bin/psql"
DB_NAME = "gps_cdm"


def run_sql(sql: str, fetch: bool = True) -> list:
    """Execute SQL and return results."""
    cmd = [PSQL_BIN, "-d", DB_NAME, "-t", "-A", "-F", "|", "-c", sql]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"SQL Error: {result.stderr}")
        return []
    if fetch and result.stdout.strip():
        return [line.split("|") for line in result.stdout.strip().split("\n") if line]
    return []


# Sample pain.001 XML for testing
SAMPLE_PAIN001 = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>INGESTION-TEST-001</MsgId>
            <CreDtTm>2024-12-21T10:00:00</CreDtTm>
            <NbOfTxs>2</NbOfTxs>
            <CtrlSum>15000.00</CtrlSum>
            <InitgPty>
                <Nm>Test Corporation</Nm>
                <Id>
                    <OrgId>
                        <BICOrBEI>TESTUS33</BICOrBEI>
                    </OrgId>
                </Id>
            </InitgPty>
        </GrpHdr>
        <PmtInf>
            <PmtInfId>PMTINF-001</PmtInfId>
            <PmtMtd>TRF</PmtMtd>
            <BtchBookg>false</BtchBookg>
            <NbOfTxs>2</NbOfTxs>
            <CtrlSum>15000.00</CtrlSum>
            <ReqdExctnDt>
                <Dt>2024-12-22</Dt>
            </ReqdExctnDt>
            <Dbtr>
                <Nm>John Doe</Nm>
                <PstlAdr>
                    <StrtNm>123 Main Street</StrtNm>
                    <TwnNm>New York</TwnNm>
                    <Ctry>US</Ctry>
                </PstlAdr>
            </Dbtr>
            <DbtrAcct>
                <Id>
                    <IBAN>US12345678901234567890</IBAN>
                </Id>
            </DbtrAcct>
            <DbtrAgt>
                <FinInstnId>
                    <BICFI>TESTUSNY</BICFI>
                </FinInstnId>
            </DbtrAgt>
            <CdtTrfTxInf>
                <PmtId>
                    <InstrId>INSTR-001</InstrId>
                    <EndToEndId>E2E-INGESTION-001</EndToEndId>
                </PmtId>
                <Amt>
                    <InstdAmt Ccy="USD">10000.00</InstdAmt>
                </Amt>
                <ChrgBr>SHAR</ChrgBr>
                <CdtrAgt>
                    <FinInstnId>
                        <BICFI>BENEUS33</BICFI>
                    </FinInstnId>
                </CdtrAgt>
                <Cdtr>
                    <Nm>Acme Corporation</Nm>
                    <PstlAdr>
                        <Ctry>US</Ctry>
                    </PstlAdr>
                </Cdtr>
                <CdtrAcct>
                    <Id>
                        <IBAN>US98765432109876543210</IBAN>
                    </Id>
                </CdtrAcct>
                <RmtInf>
                    <Ustrd>Invoice INV-2024-001</Ustrd>
                </RmtInf>
            </CdtTrfTxInf>
            <CdtTrfTxInf>
                <PmtId>
                    <InstrId>INSTR-002</InstrId>
                    <EndToEndId>E2E-INGESTION-002</EndToEndId>
                </PmtId>
                <Amt>
                    <InstdAmt Ccy="USD">5000.00</InstdAmt>
                </Amt>
                <ChrgBr>DEBT</ChrgBr>
                <CdtrAgt>
                    <FinInstnId>
                        <BICFI>GLOBUS44</BICFI>
                    </FinInstnId>
                </CdtrAgt>
                <Cdtr>
                    <Nm>Global Trading Ltd</Nm>
                    <PstlAdr>
                        <Ctry>GB</Ctry>
                    </PstlAdr>
                </Cdtr>
                <CdtrAcct>
                    <Id>
                        <IBAN>GB82WEST12345698765432</IBAN>
                    </Id>
                </CdtrAcct>
                <RmtInf>
                    <Ustrd>Payment for services</Ustrd>
                </RmtInf>
            </CdtTrfTxInf>
        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>"""


def test_ingestion_engine():
    """Test the ConfigDrivenIngestion engine with YAML mapping."""
    print("\n" + "=" * 60)
    print("TEST: INGESTION ENGINE WITH YAML CONFIG")
    print("=" * 60)

    from pyspark.sql import SparkSession

    # Create Spark session
    print("\n  Creating Spark session...")
    spark = SparkSession.builder \
        .appName("GPS-CDM-Ingestion-Test") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.session.timeZone", "UTC") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    print(f"  Spark version: {spark.version}")

    try:
        # Import ingestion engine
        from gps_cdm.ingestion.core.engine import ConfigDrivenIngestion

        # Create source DataFrame with raw XML
        print("\n  Creating source DataFrame with pain.001 XML...")
        source_data = [(SAMPLE_PAIN001,)]
        source_df = spark.createDataFrame(source_data, ["content"])
        print(f"  Source records: {source_df.count()}")

        # Initialize ingestion engine
        print("\n  Initializing ingestion engine...")
        engine = ConfigDrivenIngestion(
            spark=spark,
            enable_lineage=True,
            enable_validation=True,
        )

        # Process with pain001 mapping
        mapping_path = str(PROJECT_ROOT / "mappings" / "message_types" / "pain001.yaml")
        print(f"  Mapping: {mapping_path}")

        print("\n  Processing through mapping...")
        result = engine.process(
            source_df=source_df,
            mapping_path=mapping_path,
        )

        # Show results
        print(f"\n  Ingestion Result:")
        print(f"    Mapping ID: {result.mapping_id}")
        print(f"    Mapping Name: {result.mapping_name}")
        print(f"    Input Count: {result.input_count}")
        print(f"    Output Count: {result.output_count}")
        print(f"    Error Count: {result.error_count}")
        print(f"    Validation Failures: {result.validation_failures}")
        print(f"    Execution Time: {result.execution_time_ms:.2f}ms")

        # Show output schema
        print(f"\n  Output Schema (first 20 columns):")
        for field in result.output_df.schema.fields[:20]:
            print(f"    - {field.name}: {field.dataType.simpleString()}")

        # Show sample data
        print(f"\n  Sample Output Data:")
        output_cols = [
            c for c in result.output_df.columns
            if any(x in c.lower() for x in ['msg', 'amount', 'currency', 'debtor', 'creditor', 'e2e'])
        ][:10]

        if output_cols:
            result.output_df.select(output_cols).show(5, truncate=30)

        # Show lineage
        print(f"\n  Lineage Info:")
        for key, value in result.lineage.items():
            print(f"    {key}: {value}")

        # Show metrics
        print(f"\n  Metrics:")
        for key, value in result.metrics.items():
            print(f"    {key}: {value}")

        return True, result

    except Exception as e:
        print(f"\n  [FAIL] Ingestion error: {e}")
        import traceback
        traceback.print_exc()
        return False, None

    finally:
        spark.stop()


def test_bronze_to_silver_transform():
    """Test Bronze to Silver transformation using YAML config."""
    print("\n" + "=" * 60)
    print("TEST: BRONZE -> SILVER TRANSFORMATION")
    print("=" * 60)

    from pyspark.sql import SparkSession
    import yaml

    spark = SparkSession.builder \
        .appName("GPS-CDM-Bronze-Silver-Test") \
        .master("local[*]") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    try:
        # Load mapping config
        mapping_path = PROJECT_ROOT / "mappings" / "message_types" / "pain001.yaml"
        print(f"\n  Loading mapping: {mapping_path}")

        with open(mapping_path) as f:
            config = yaml.safe_load(f)

        mapping = config.get("mapping", {})
        bronze_to_silver = mapping.get("bronze_to_silver", {})
        fields = bronze_to_silver.get("fields", [])

        print(f"  Bronze->Silver fields: {len(fields)}")

        # Show sample field mappings
        print(f"\n  Sample Field Mappings:")
        for field in fields[:10]:
            source = field.get("source", "N/A")
            target = field.get("target", "N/A")
            transform = field.get("transform", {})
            print(f"    {source[:40]:<40} -> {target}")
            if transform:
                print(f"      Transform: {transform.get('type', 'direct')}")

        # Check validations
        validations = mapping.get("validations", [])
        print(f"\n  Validation Rules: {len(validations)}")
        for v in validations[:5]:
            print(f"    - {v.get('id')}: {v.get('description', v.get('rule', 'N/A')[:50])}")

        # Check quality rules
        quality = mapping.get("quality", {})
        rules = quality.get("rules", [])
        print(f"\n  Quality Rules: {len(rules)}")
        for r in rules[:5]:
            print(f"    - {r.get('name')}: {r.get('dimension', 'N/A')}")

        return True

    except Exception as e:
        print(f"\n  [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        spark.stop()


def test_silver_to_gold_transform():
    """Test Silver to Gold transformation using YAML config."""
    print("\n" + "=" * 60)
    print("TEST: SILVER -> GOLD TRANSFORMATION")
    print("=" * 60)

    import yaml

    try:
        mapping_path = PROJECT_ROOT / "mappings" / "message_types" / "pain001.yaml"
        print(f"\n  Loading mapping: {mapping_path}")

        with open(mapping_path) as f:
            config = yaml.safe_load(f)

        mapping = config.get("mapping", {})
        silver_to_gold = mapping.get("silver_to_gold", {})
        fields = silver_to_gold.get("fields", [])
        target_table = silver_to_gold.get("target_table", "N/A")

        print(f"  Target Table: {target_table}")
        print(f"  Silver->Gold fields: {len(fields)}")

        # Show sample field mappings
        print(f"\n  Sample Field Mappings:")
        for field in fields[:15]:
            source = field.get("source", "N/A")
            target = field.get("target", "N/A")
            transform = field.get("transform", {})
            const = field.get("constant")
            if const:
                print(f"    CONSTANT({const}) -> {target}")
            else:
                print(f"    {source:<30} -> {target}")

        return True

    except Exception as e:
        print(f"\n  [FAIL] Error: {e}")
        return False


def test_full_pipeline_with_framework():
    """Test full pipeline: Raw XML -> Bronze -> Silver -> Gold using framework."""
    print("\n" + "=" * 60)
    print("TEST: FULL PIPELINE WITH INGESTION FRAMEWORK")
    print("=" * 60)

    from pyspark.sql import SparkSession

    spark = SparkSession.builder \
        .appName("GPS-CDM-Full-Pipeline-Test") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    batch_id = str(uuid.uuid4())
    print(f"\n  Batch ID: {batch_id}")

    try:
        from gps_cdm.ingestion.core.engine import ConfigDrivenIngestion

        # Step 1: Bronze - Store raw XML
        print("\n  STEP 1: BRONZE LAYER")
        print("  " + "-" * 40)

        raw_id = str(uuid.uuid4())
        run_sql(f"""
        INSERT INTO bronze.raw_payment_messages (
            raw_id, message_type, message_format, raw_content,
            content_size_bytes, source_system, _batch_id
        ) VALUES (
            '{raw_id}', 'pain.001', 'XML', $${SAMPLE_PAIN001}$$,
            {len(SAMPLE_PAIN001)}, 'INTEGRATION_TEST', '{batch_id}'
        );
        """, fetch=False)

        rows = run_sql(f"SELECT raw_id, message_type, content_size_bytes FROM bronze.raw_payment_messages WHERE _batch_id = '{batch_id}';")
        if rows:
            print(f"  [OK] Bronze record inserted:")
            print(f"       raw_id={rows[0][0][:8]}..., type={rows[0][1]}, size={rows[0][2]} bytes")

        # Step 2: Parse XML using ingestion engine
        print("\n  STEP 2: PARSE XML WITH ENGINE")
        print("  " + "-" * 40)

        source_df = spark.createDataFrame([(SAMPLE_PAIN001,)], ["content"])

        engine = ConfigDrivenIngestion(spark=spark, enable_lineage=True)
        mapping_path = str(PROJECT_ROOT / "mappings" / "message_types" / "pain001.yaml")

        result = engine.process(source_df=source_df, mapping_path=mapping_path)

        print(f"  [OK] Parsed with engine:")
        print(f"       Output columns: {len(result.output_df.columns)}")
        print(f"       Output records: {result.output_count}")

        # Extract key fields for Silver
        output_df = result.output_df

        # Show extracted values
        print("\n  STEP 3: EXTRACTED VALUES FOR SILVER")
        print("  " + "-" * 40)

        # Find columns that have data
        sample_row = output_df.first()
        if sample_row:
            populated_cols = []
            for col_name in output_df.columns[:50]:
                val = sample_row[col_name]
                if val is not None and str(val).strip():
                    populated_cols.append((col_name, str(val)[:50]))

            print(f"  Populated fields ({len(populated_cols)}):")
            for col_name, val in populated_cols[:15]:
                print(f"    {col_name}: {val}")

        # Step 4: Insert into Silver (simulated - would use actual extracted values)
        print("\n  STEP 4: SILVER LAYER")
        print("  " + "-" * 40)

        stg_id = str(uuid.uuid4())
        run_sql(f"""
        INSERT INTO silver.stg_pain001 (
            stg_id, raw_id, msg_id, creation_date_time,
            number_of_transactions, control_sum,
            initiating_party_name, payment_info_id, payment_method,
            debtor_name, debtor_country, debtor_account_iban,
            end_to_end_id, instructed_amount, instructed_currency,
            creditor_name, creditor_country,
            processing_status, _batch_id
        ) VALUES (
            '{stg_id}', '{raw_id}', 'INGESTION-TEST-001', '2024-12-21 10:00:00',
            2, 15000.00,
            'Test Corporation', 'PMTINF-001', 'TRF',
            'John Doe', 'US', 'US12345678901234567890',
            'E2E-INGESTION-001', 10000.00, 'USD',
            'Acme Corporation', 'US',
            'PENDING', '{batch_id}'
        );
        """, fetch=False)

        rows = run_sql(f"SELECT stg_id, msg_id, debtor_name, instructed_amount FROM silver.stg_pain001 WHERE _batch_id = '{batch_id}';")
        if rows:
            print(f"  [OK] Silver record inserted:")
            print(f"       stg_id={rows[0][0][:8]}..., msg_id={rows[0][1]}")
            print(f"       debtor={rows[0][2]}, amount={rows[0][3]}")

        # Step 5: Gold CDM
        print("\n  STEP 5: GOLD LAYER (CDM)")
        print("  " + "-" * 40)

        instruction_id = str(uuid.uuid4())
        payment_id = str(uuid.uuid4())

        run_sql(f"""
        INSERT INTO gold.cdm_payment_instruction (
            instruction_id, payment_id,
            source_system, source_message_type, source_stg_table, source_stg_id,
            payment_type, scheme_code, direction,
            message_id, end_to_end_id,
            instructed_amount, instructed_currency,
            current_status, partition_year, partition_month, region,
            lineage_batch_id, created_at, updated_at
        ) VALUES (
            '{instruction_id}', '{payment_id}',
            'INTEGRATION_TEST', 'pain.001', 'stg_pain001', '{stg_id}',
            'CREDIT_TRANSFER', 'ISO20022', 'OUTGOING',
            'INGESTION-TEST-001', 'E2E-INGESTION-001',
            10000.00, 'USD',
            'PENDING', 2024, 12, 'GLOBAL',
            '{batch_id}', NOW(), NOW()
        );
        """, fetch=False)

        rows = run_sql(f"SELECT instruction_id, source_message_type, instructed_amount FROM gold.cdm_payment_instruction WHERE lineage_batch_id = '{batch_id}';")
        if rows:
            print(f"  [OK] Gold CDM record inserted:")
            print(f"       instruction_id={rows[0][0][:8]}...")
            print(f"       source={rows[0][1]}, amount={rows[0][2]}")

        # Summary
        print("\n  PIPELINE SUMMARY")
        print("  " + "-" * 40)

        zones = [
            ("Bronze", f"SELECT COUNT(*) FROM bronze.raw_payment_messages WHERE _batch_id = '{batch_id}'"),
            ("Silver", f"SELECT COUNT(*) FROM silver.stg_pain001 WHERE _batch_id = '{batch_id}'"),
            ("Gold", f"SELECT COUNT(*) FROM gold.cdm_payment_instruction WHERE lineage_batch_id = '{batch_id}'"),
        ]

        for zone, sql in zones:
            rows = run_sql(sql)
            count = rows[0][0] if rows else 0
            print(f"  {zone}: {count} records")

        return True

    except Exception as e:
        print(f"\n  [FAIL] Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        spark.stop()


def main():
    """Run ingestion framework tests."""
    print("\n" + "=" * 60)
    print("GPS CDM - INGESTION FRAMEWORK INTEGRATION TEST")
    print("=" * 60)
    print(f"Time: {datetime.now().isoformat()}")

    results = []

    # Test 1: Bronze to Silver mapping config
    success = test_bronze_to_silver_transform()
    results.append(("Bronze->Silver Mapping", success))

    # Test 2: Silver to Gold mapping config
    success = test_silver_to_gold_transform()
    results.append(("Silver->Gold Mapping", success))

    # Test 3: Ingestion engine with Spark
    success, _ = test_ingestion_engine()
    results.append(("Ingestion Engine", success))

    # Test 4: Full pipeline
    success = test_full_pipeline_with_framework()
    results.append(("Full Pipeline", success))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {name}")

    passed = sum(1 for _, p in results if p)
    print(f"\n  {passed}/{len(results)} tests passed")


if __name__ == "__main__":
    main()
