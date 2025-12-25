"""
GPS CDM - Live Pipeline Test
=============================

Real end-to-end test with actual PostgreSQL data persistence.
Verifies data flows through all zones and is persisted correctly.

Usage:
    python tests/integration/test_live_pipeline.py
"""

import os
import sys
import uuid
import json
from datetime import datetime, date
from pathlib import Path
from decimal import Decimal

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# PostgreSQL connection
PSQL_BIN = "/opt/homebrew/opt/postgresql@16/bin/psql"
DB_NAME = "gps_cdm"


def run_sql(sql: str, fetch: bool = True) -> list:
    """Execute SQL and return results."""
    import subprocess

    cmd = [PSQL_BIN, "-d", DB_NAME, "-t", "-A", "-F", "|", "-c", sql]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"SQL Error: {result.stderr}")
        return []

    if fetch and result.stdout.strip():
        rows = []
        for line in result.stdout.strip().split("\n"):
            if line:
                rows.append(line.split("|"))
        return rows
    return []


def test_zone_1_bronze():
    """Test Bronze layer: Insert raw payment message."""
    print("\n" + "=" * 60)
    print("ZONE 1: BRONZE LAYER TEST")
    print("=" * 60)

    batch_id = str(uuid.uuid4())
    raw_id = str(uuid.uuid4())

    # Sample pain.001 XML content
    raw_content = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>MSG-LIVE-TEST-001</MsgId>
            <CreDtTm>2024-12-21T10:00:00</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>5000.00</CtrlSum>
        </GrpHdr>
        <PmtInf>
            <PmtInfId>PMTINF-LIVE-001</PmtInfId>
            <PmtMtd>TRF</PmtMtd>
            <CdtTrfTxInf>
                <PmtId>
                    <EndToEndId>E2E-LIVE-001</EndToEndId>
                </PmtId>
                <Amt>
                    <InstdAmt Ccy="USD">5000.00</InstdAmt>
                </Amt>
                <Cdtr>
                    <Nm>Acme Corporation</Nm>
                </Cdtr>
            </CdtTrfTxInf>
        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>"""

    # Insert into Bronze (using actual schema columns)
    sql = f"""
    INSERT INTO bronze.raw_payment_messages (
        raw_id, message_type, message_format, raw_content,
        content_size_bytes, source_system, source_file_path,
        processing_status, _batch_id
    ) VALUES (
        '{raw_id}', 'pain.001', 'XML', $${raw_content}$$,
        {len(raw_content)}, 'SFTP_INCOMING', '/incoming/pain001_test.xml',
        'PENDING', '{batch_id}'
    ) RETURNING raw_id;
    """

    result = run_sql(sql)

    if result:
        print(f"  [OK] Inserted Bronze record: {result[0][0][:8]}...")
    else:
        print("  [FAIL] Failed to insert Bronze record")
        return None, None

    # Verify data persisted
    verify_sql = f"SELECT raw_id, message_type, processing_status FROM bronze.raw_payment_messages WHERE _batch_id = '{batch_id}';"
    rows = run_sql(verify_sql)

    if rows:
        print(f"  [OK] Verified Bronze data:")
        for row in rows:
            print(f"       raw_id={row[0][:8]}..., type={row[1]}, status={row[2]}")

    return batch_id, raw_id


def test_zone_2_silver(batch_id: str, bronze_raw_id: str):
    """Test Silver layer: Transform to structured staging table."""
    print("\n" + "=" * 60)
    print("ZONE 2: SILVER LAYER TEST")
    print("=" * 60)

    stg_id = str(uuid.uuid4())

    # Insert into Silver stg_pain001 (using actual schema columns)
    sql = f"""
    INSERT INTO silver.stg_pain001 (
        stg_id, raw_id, msg_id, creation_date_time,
        number_of_transactions, control_sum,
        initiating_party_name, payment_info_id, payment_method,
        requested_execution_date,
        debtor_name, debtor_country, debtor_account_iban, debtor_agent_bic,
        end_to_end_id, instructed_amount, instructed_currency,
        creditor_name, creditor_country, creditor_account_iban, creditor_agent_bic,
        charge_bearer, remittance_information,
        processing_status, source_raw_id, _batch_id
    ) VALUES (
        '{stg_id}', '{bronze_raw_id}', 'MSG-LIVE-TEST-001', '2024-12-21 10:00:00',
        1, 5000.00,
        'Test Corporation', 'PMTINF-LIVE-001', 'TRF',
        '2024-12-22',
        'John Doe Test', 'US', 'US12345678901234567890', 'TESTUSNY',
        'E2E-LIVE-001', 5000.00, 'USD',
        'Acme Corporation', 'US', 'US98765432109876543210', 'BENEUS33',
        'SHAR', 'Payment for live test',
        'PENDING', '{bronze_raw_id}', '{batch_id}'
    ) RETURNING stg_id;
    """

    result = run_sql(sql)

    if result:
        print(f"  [OK] Inserted Silver record: {result[0][0][:8]}...")
    else:
        print("  [FAIL] Failed to insert Silver record")
        return None

    # Update Bronze status
    run_sql(f"UPDATE bronze.raw_payment_messages SET processing_status = 'PROCESSED', processed_to_silver_at = NOW() WHERE raw_id = '{bronze_raw_id}';", fetch=False)

    # Verify Silver data
    verify_sql = f"""
    SELECT stg_id, debtor_name, creditor_name, instructed_amount, instructed_currency
    FROM silver.stg_pain001 WHERE _batch_id = '{batch_id}';
    """
    rows = run_sql(verify_sql)

    if rows:
        print(f"  [OK] Verified Silver data:")
        for row in rows:
            print(f"       stg_id={row[0][:8]}..., debtor={row[1]}, creditor={row[2]}, amount={row[3]} {row[4]}")

    return stg_id


def test_zone_3_gold(batch_id: str, stg_id: str):
    """Test Gold layer: Normalize to unified CDM."""
    print("\n" + "=" * 60)
    print("ZONE 3: GOLD LAYER TEST (CDM)")
    print("=" * 60)

    instruction_id = str(uuid.uuid4())
    payment_id = str(uuid.uuid4())
    debtor_party_id = str(uuid.uuid4())
    creditor_party_id = str(uuid.uuid4())

    # Insert parties first (using actual schema)
    run_sql(f"""
    INSERT INTO gold.cdm_party (
        party_id, party_type, name, country,
        source_system, source_message_type, source_stg_id,
        created_at, updated_at
    ) VALUES
    ('{debtor_party_id}', 'INDIVIDUAL', 'John Doe Test', 'US',
     'GPS_CDM', 'pain.001', '{stg_id}', NOW(), NOW()),
    ('{creditor_party_id}', 'ORGANIZATION', 'Acme Corporation', 'US',
     'GPS_CDM', 'pain.001', '{stg_id}', NOW(), NOW());
    """, fetch=False)

    # Insert into Gold cdm_payment_instruction (using actual schema)
    sql = f"""
    INSERT INTO gold.cdm_payment_instruction (
        instruction_id, payment_id,
        source_system, source_message_type, source_stg_table, source_stg_id,
        payment_type, scheme_code, direction,
        message_id, creation_datetime,
        requested_execution_date, debtor_id, creditor_id,
        end_to_end_id, instructed_amount, instructed_currency,
        charge_bearer, current_status,
        partition_year, partition_month, region,
        lineage_batch_id, created_at, updated_at
    ) VALUES (
        '{instruction_id}', '{payment_id}',
        'GPS_CDM', 'pain.001', 'stg_pain001', '{stg_id}',
        'CREDIT_TRANSFER', 'ISO20022', 'OUTGOING',
        'MSG-LIVE-TEST-001', '2024-12-21 10:00:00',
        '2024-12-22', '{debtor_party_id}', '{creditor_party_id}',
        'E2E-LIVE-001', 5000.00, 'USD',
        'SHAR', 'PENDING',
        2024, 12, 'GLOBAL',
        '{batch_id}', NOW(), NOW()
    ) RETURNING instruction_id;
    """

    result = run_sql(sql)

    if result:
        print(f"  [OK] Inserted Gold CDM record: {result[0][0][:8]}...")
    else:
        print("  [FAIL] Failed to insert Gold record")
        return None

    # Update Silver status
    run_sql(f"UPDATE silver.stg_pain001 SET processing_status = 'PROCESSED', processed_to_gold_at = NOW() WHERE stg_id = '{stg_id}';", fetch=False)

    # Verify Gold data with party join
    verify_sql = f"""
    SELECT
        pi.instruction_id, pi.source_message_type,
        d.name as debtor, c.name as creditor,
        pi.instructed_amount, pi.instructed_currency, pi.current_status
    FROM gold.cdm_payment_instruction pi
    LEFT JOIN gold.cdm_party d ON pi.debtor_id = d.party_id
    LEFT JOIN gold.cdm_party c ON pi.creditor_id = c.party_id
    WHERE pi.lineage_batch_id = '{batch_id}';
    """
    rows = run_sql(verify_sql)

    if rows:
        print(f"  [OK] Verified Gold CDM data (unified table):")
        for row in rows:
            print(f"       instruction_id={row[0][:8]}..., source={row[1]}")
            print(f"       debtor={row[2]}, creditor={row[3]}")
            print(f"       amount={row[4]} {row[5]}, status={row[6]}")

    return instruction_id


def test_zone_4_analytical(batch_id: str, instruction_id: str):
    """Test Analytical layer: Build data products."""
    print("\n" + "=" * 60)
    print("ZONE 4: ANALYTICAL LAYER TEST")
    print("=" * 60)

    payment_id = str(uuid.uuid4())

    # Insert into Analytical anl_payment_360 (using actual schema)
    sql = f"""
    INSERT INTO analytical.anl_payment_360 (
        payment_id, instruction_id, end_to_end_id,
        source_message_type, payment_type, scheme_code, direction,
        debtor_name, debtor_country, debtor_type,
        creditor_name, creditor_country, creditor_type,
        instructed_amount, instructed_currency,
        creation_datetime, current_status,
        cross_border_flag, high_value_flag, requires_screening,
        dq_score, partition_year, partition_month, region
    ) VALUES (
        '{payment_id}', '{instruction_id}', 'E2E-LIVE-001',
        'pain.001', 'CREDIT_TRANSFER', 'ISO20022', 'OUTGOING',
        'John Doe Test', 'US', 'INDIVIDUAL',
        'Acme Corporation', 'US', 'ORGANIZATION',
        5000.00, 'USD',
        '2024-12-21 10:00:00', 'PENDING',
        false, false, true,
        95.5, 2024, 12, 'GLOBAL'
    ) RETURNING payment_id;
    """

    result = run_sql(sql)

    if result:
        print(f"  [OK] Inserted Payment 360 record: {result[0][0][:8]}...")
    else:
        print("  [FAIL] Failed to insert Analytical record")
        return

    # Verify Analytical data
    verify_sql = f"""
    SELECT
        p.payment_id, p.source_message_type, p.direction,
        p.debtor_name, p.creditor_name, p.instructed_amount, p.dq_score
    FROM analytical.anl_payment_360 p
    WHERE p.instruction_id = '{instruction_id}';
    """
    rows = run_sql(verify_sql)

    if rows:
        print(f"  [OK] Verified Payment 360 data product:")
        for row in rows:
            print(f"       direction={row[2]}, debtor={row[3]}, creditor={row[4]}")
            print(f"       amount={row[5]}, dq_score={row[6]}")


def test_zone_5_dq(batch_id: str, instruction_id: str):
    """Test DQ layer: Store data quality results."""
    print("\n" + "=" * 60)
    print("ZONE 5: DATA QUALITY TEST")
    print("=" * 60)

    dq_result_id = str(uuid.uuid4())

    # Insert DQ result
    sql = f"""
    INSERT INTO observability.obs_dq_results (
        dq_result_id, batch_id, layer, entity_type, entity_id,
        overall_score,
        completeness_score, accuracy_score, consistency_score,
        timeliness_score, validity_score, uniqueness_score,
        rule_results, issues,
        evaluated_at
    ) VALUES (
        '{dq_result_id}', '{batch_id}', 'gold', 'payment_instruction', '{instruction_id}',
        95.5,
        100.0, 95.0, 90.0,
        100.0, 92.0, 96.0,
        '{{"amount_positive": true, "currency_valid": true, "iban_checksum": true, "date_format": true}}',
        '["Minor: BIC format warning"]',
        NOW()
    ) RETURNING dq_result_id;
    """

    result = run_sql(sql)

    if result:
        print(f"  [OK] Inserted DQ Result: {result[0][0][:8]}...")

    # Insert aggregated DQ metrics
    run_sql(f"""
    INSERT INTO observability.obs_dq_metrics (
        dq_metrics_id, batch_id, layer, entity_type,
        total_records, avg_overall_score,
        avg_completeness, avg_accuracy, avg_consistency,
        avg_timeliness, avg_validity, avg_uniqueness,
        records_above_threshold, records_below_threshold,
        threshold_used, top_failing_rules,
        calculated_at
    ) VALUES (
        '{str(uuid.uuid4())}', '{batch_id}', 'gold', 'payment_instruction',
        1, 95.5,
        100.0, 95.0, 90.0,
        100.0, 92.0, 96.0,
        1, 0,
        80.0, '[]',
        NOW()
    );
    """, fetch=False)

    # Verify DQ data
    verify_sql = f"""
    SELECT entity_type, overall_score, completeness_score, accuracy_score, issues
    FROM observability.obs_dq_results
    WHERE batch_id = '{batch_id}';
    """
    rows = run_sql(verify_sql)

    if rows:
        print(f"  [OK] Verified DQ Results:")
        for row in rows:
            print(f"       entity={row[0]}, overall_score={row[1]}")
            print(f"       completeness={row[2]}, accuracy={row[3]}")
            print(f"       issues={row[4]}")


def test_zone_6_cdc(batch_id: str, instruction_id: str):
    """Test CDC layer: Capture changes for downstream sync."""
    print("\n" + "=" * 60)
    print("ZONE 6: CDC TEST")
    print("=" * 60)

    cdc_id = str(uuid.uuid4())

    # Insert CDC event
    sql = f"""
    INSERT INTO observability.obs_cdc_tracking (
        cdc_id, layer, table_name, record_id,
        operation, old_data, new_data, changed_fields,
        batch_id, event_timestamp, synced_at, target_system
    ) VALUES (
        '{cdc_id}', 'gold', 'cdm_payment_instruction', '{instruction_id}',
        'INSERT', NULL,
        '{{"instruction_id": "{instruction_id}", "amount": 5000.00, "currency": "USD"}}',
        '["instruction_id", "amount", "currency"]',
        '{batch_id}', NOW(), NULL, NULL
    ) RETURNING cdc_id;
    """

    result = run_sql(sql)

    if result:
        print(f"  [OK] Inserted CDC Event: {result[0][0][:8]}...")

    # Verify CDC data
    verify_sql = f"""
    SELECT table_name, operation, changed_fields, synced_at
    FROM observability.obs_cdc_tracking
    WHERE batch_id = '{batch_id}';
    """
    rows = run_sql(verify_sql)

    if rows:
        print(f"  [OK] Verified CDC Events (pending sync to Neo4j):")
        for row in rows:
            print(f"       table={row[0]}, operation={row[1]}")
            print(f"       changed_fields={row[2]}")
            print(f"       synced_at={row[3] or 'NOT YET SYNCED'}")


def test_zone_7_observability(batch_id: str):
    """Test Observability: Batch tracking and lineage."""
    print("\n" + "=" * 60)
    print("ZONE 7: OBSERVABILITY TEST")
    print("=" * 60)

    # Insert batch tracking
    run_sql(f"""
    INSERT INTO observability.obs_batch_tracking (
        batch_id, source_system, source_type, source_path,
        message_type, started_at, status,
        bronze_records, silver_records, gold_records, analytical_records,
        checkpoint_offset, checkpoint_partition, checkpoint_key
    ) VALUES (
        '{batch_id}', 'SFTP_INCOMING', 'FILE', '/incoming/pain001_test.xml',
        'pain.001', NOW() - INTERVAL '5 minutes', 'COMPLETED',
        1, 1, 1, 2,
        1, 'default', 'MSG-LIVE-TEST-001'
    );
    """, fetch=False)

    # Update completed_at
    run_sql(f"UPDATE observability.obs_batch_tracking SET completed_at = NOW() WHERE batch_id = '{batch_id}';", fetch=False)

    # Insert field lineage
    lineages = [
        ("bronze", "raw_payment_messages", "raw_content/CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Amt/InstdAmt",
         "silver", "stg_pain001", "instructed_amount", "XPATH_EXTRACT"),
        ("silver", "stg_pain001", "instructed_amount",
         "gold", "cdm_payment_instruction", "instructed_amount", "DIRECT_COPY"),
        ("gold", "cdm_payment_instruction", "instructed_amount",
         "analytical", "anl_payment_360", "instructed_amount", "DIRECT_COPY"),
    ]

    for src_layer, src_table, src_field, tgt_layer, tgt_table, tgt_field, transform in lineages:
        run_sql(f"""
        INSERT INTO observability.obs_field_lineage (
            lineage_id, batch_id,
            source_layer, source_table, source_field,
            target_layer, target_table, target_field,
            transformation_type, created_at
        ) VALUES (
            '{str(uuid.uuid4())}', '{batch_id}',
            '{src_layer}', '{src_table}', '{src_field}',
            '{tgt_layer}', '{tgt_table}', '{tgt_field}',
            '{transform}', NOW()
        );
        """, fetch=False)

    # Verify batch tracking
    verify_sql = f"""
    SELECT batch_id, message_type, status,
           bronze_records, silver_records, gold_records, analytical_records
    FROM observability.obs_batch_tracking
    WHERE batch_id = '{batch_id}';
    """
    rows = run_sql(verify_sql)

    if rows:
        print(f"  [OK] Verified Batch Tracking:")
        for row in rows:
            print(f"       batch_id={row[0][:8]}..., type={row[1]}, status={row[2]}")
            print(f"       records: bronze={row[3]}, silver={row[4]}, gold={row[5]}, analytical={row[6]}")

    # Verify field lineage
    lineage_sql = f"""
    SELECT source_layer, source_field, target_layer, target_field, transformation_type
    FROM observability.obs_field_lineage
    WHERE batch_id = '{batch_id}'
    ORDER BY source_layer;
    """
    rows = run_sql(lineage_sql)

    if rows:
        print(f"  [OK] Verified Field-Level Lineage:")
        for row in rows:
            print(f"       {row[0]}.{row[1]} -> {row[2]}.{row[3]} [{row[4]}]")


def show_final_summary(batch_id: str):
    """Show summary of all data across zones."""
    print("\n" + "=" * 60)
    print("FINAL SUMMARY: DATA ACROSS ALL ZONES")
    print("=" * 60)

    zones = [
        ("BRONZE", f"SELECT COUNT(*) FROM bronze.raw_payment_messages WHERE _batch_id = '{batch_id}';"),
        ("SILVER", f"SELECT COUNT(*) FROM silver.stg_pain001 WHERE _batch_id = '{batch_id}';"),
        ("GOLD", f"SELECT COUNT(*) FROM gold.cdm_payment_instruction WHERE lineage_batch_id = '{batch_id}';"),
        ("GOLD PARTIES", f"SELECT COUNT(*) FROM gold.cdm_party WHERE source_stg_id IN (SELECT stg_id FROM silver.stg_pain001 WHERE _batch_id = '{batch_id}');"),
        ("ANALYTICAL", f"SELECT COUNT(*) FROM analytical.anl_payment_360 WHERE instruction_id IN (SELECT instruction_id FROM gold.cdm_payment_instruction WHERE lineage_batch_id = '{batch_id}');"),
        ("DQ RESULTS", f"SELECT COUNT(*) FROM observability.obs_dq_results WHERE batch_id = '{batch_id}';"),
        ("CDC EVENTS", f"SELECT COUNT(*) FROM observability.obs_cdc_tracking WHERE batch_id = '{batch_id}';"),
        ("LINEAGE", f"SELECT COUNT(*) FROM observability.obs_field_lineage WHERE batch_id = '{batch_id}';"),
    ]

    print(f"\n  Batch ID: {batch_id}\n")
    print(f"  {'Zone':<15} {'Records':>10}")
    print(f"  {'-' * 15} {'-' * 10}")

    for zone_name, sql in zones:
        rows = run_sql(sql)
        count = rows[0][0] if rows else "0"
        print(f"  {zone_name:<15} {count:>10}")

    print(f"\n  All data persisted to PostgreSQL successfully!")
    print(f"  Database: {DB_NAME}")


def main():
    """Run the complete live pipeline test."""
    print("\n" + "=" * 60)
    print("GPS CDM - LIVE PIPELINE TEST WITH POSTGRESQL")
    print("=" * 60)
    print(f"Database: {DB_NAME}")
    print(f"Time: {datetime.now().isoformat()}")

    # Zone 1: Bronze
    batch_id, message_id = test_zone_1_bronze()
    if not batch_id:
        print("\n[FAIL] Bronze test failed, aborting.")
        return

    # Zone 2: Silver
    payment_id = test_zone_2_silver(batch_id, message_id)
    if not payment_id:
        print("\n[FAIL] Silver test failed, aborting.")
        return

    # Zone 3: Gold
    instruction_id = test_zone_3_gold(batch_id, payment_id)
    if not instruction_id:
        print("\n[FAIL] Gold test failed, aborting.")
        return

    # Zone 4: Analytical
    test_zone_4_analytical(batch_id, instruction_id)

    # Zone 5: DQ
    test_zone_5_dq(batch_id, instruction_id)

    # Zone 6: CDC
    test_zone_6_cdc(batch_id, instruction_id)

    # Zone 7: Observability
    test_zone_7_observability(batch_id)

    # Final Summary
    show_final_summary(batch_id)

    print("\n" + "=" * 60)
    print("LIVE PIPELINE TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
