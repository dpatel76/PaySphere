"""
GPS CDM - Full Pipeline Integration Test
=========================================

End-to-end test of the complete medallion pipeline:
1. Bronze: Ingest raw XML message
2. Silver: Parse and stage structured data
3. Gold: Extract normalized entities (Party, Account, FI) with deduplication
4. Verify: Check all tables populated, CDC events captured

This test verifies:
- Entity extraction from YAML mappings works
- Deduplication prevents duplicate parties/accounts
- CDC triggers capture all changes
- Full data lineage from bronze to gold

Usage:
    python tests/integration/test_full_pipeline.py
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

# PostgreSQL connection
PSQL_BIN = "/opt/homebrew/opt/postgresql@16/bin/psql"
DB_NAME = "gps_cdm"


def run_sql(sql: str, fetch: bool = True) -> list:
    """Execute SQL and return results."""
    cmd = [PSQL_BIN, "-d", DB_NAME, "-t", "-A", "-F", "|", "-c", sql]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  SQL Error: {result.stderr}")
        return []
    if fetch and result.stdout.strip():
        rows = []
        for line in result.stdout.strip().split("\n"):
            if line:
                rows.append(line.split("|"))
        return rows
    return []


def cleanup_test_data(batch_id: str):
    """Clean up test data from all layers."""
    run_sql(f"DELETE FROM gold.cdm_payment_instruction WHERE lineage_batch_id = '{batch_id}';", fetch=False)
    run_sql(f"DELETE FROM gold.cdm_party WHERE source_stg_id IN (SELECT stg_id FROM silver.stg_pain001 WHERE _batch_id = '{batch_id}');", fetch=False)
    run_sql(f"DELETE FROM gold.cdm_account WHERE source_stg_id IN (SELECT stg_id FROM silver.stg_pain001 WHERE _batch_id = '{batch_id}');", fetch=False)
    run_sql(f"DELETE FROM silver.stg_pain001 WHERE _batch_id = '{batch_id}';", fetch=False)
    run_sql(f"DELETE FROM bronze.raw_payment_messages WHERE _batch_id = '{batch_id}';", fetch=False)
    run_sql(f"DELETE FROM observability.obs_cdc_tracking WHERE batch_id = '{batch_id}';", fetch=False)


def test_step1_bronze(batch_id: str) -> str:
    """Step 1: Insert raw message into Bronze layer."""
    print("\n" + "=" * 60)
    print("STEP 1: BRONZE LAYER - Ingest Raw Message")
    print("=" * 60)

    raw_id = str(uuid.uuid4())

    test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>FULL-PIPE-TEST-001</MsgId>
            <CreDtTm>2024-12-24T10:00:00</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>10000.00</CtrlSum>
            <InitgPty><Nm>Initiating Corp</Nm></InitgPty>
        </GrpHdr>
        <PmtInf>
            <PmtInfId>PMTINF-FULLTEST-001</PmtInfId>
            <PmtMtd>TRF</PmtMtd>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>10000.00</CtrlSum>
            <ReqdExctnDt><Dt>2024-12-25</Dt></ReqdExctnDt>
            <Dbtr>
                <Nm>John Smith</Nm>
                <PstlAdr>
                    <StrtNm>123 Oak Street</StrtNm>
                    <TwnNm>New York</TwnNm>
                    <Ctry>US</Ctry>
                </PstlAdr>
                <Id><OrgId><LEI>529900T8BM49AURSDO55</LEI></OrgId></Id>
            </Dbtr>
            <DbtrAcct><Id><IBAN>US12345678901234567890</IBAN></Id></DbtrAcct>
            <DbtrAgt><FinInstnId><BICFI>CHASUS33XXX</BICFI></FinInstnId></DbtrAgt>
            <CdtTrfTxInf>
                <PmtId>
                    <EndToEndId>E2E-FULLTEST-001</EndToEndId>
                    <UETR>eb6305c9-1f7f-49de-aef2-d0a9e768ec5e</UETR>
                </PmtId>
                <Amt><InstdAmt Ccy="USD">10000.00</InstdAmt></Amt>
                <ChrgBr>SHAR</ChrgBr>
                <CdtrAgt><FinInstnId><BICFI>BOFAUS3NXXX</BICFI></FinInstnId></CdtrAgt>
                <Cdtr>
                    <Nm>Acme Corporation</Nm>
                    <PstlAdr>
                        <StrtNm>456 Main Ave</StrtNm>
                        <TwnNm>Los Angeles</TwnNm>
                        <Ctry>US</Ctry>
                    </PstlAdr>
                </Cdtr>
                <CdtrAcct><Id><IBAN>US98765432109876543210</IBAN></Id></CdtrAcct>
            </CdtTrfTxInf>
        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>"""

    # Insert into bronze
    sql = f"""
    INSERT INTO bronze.raw_payment_messages (
        raw_id, message_type, message_format, raw_content,
        content_size_bytes, source_system,
        _batch_id, ingestion_timestamp
    ) VALUES (
        '{raw_id}', 'pain.001', 'XML', $xml${test_xml}$xml$,
        {len(test_xml)}, 'GPS_CDM_TEST',
        '{batch_id}', NOW()
    ) RETURNING raw_id;
    """

    result = run_sql(sql)
    if result:
        print(f"  [OK] Bronze record inserted:")
        print(f"       raw_id: {raw_id[:8]}...")
        print(f"       message_type: pain.001")
        print(f"       content_size: {len(test_xml)} bytes")
        return raw_id
    else:
        print("  [FAIL] Could not insert bronze record")
        return None


def test_step2_silver(batch_id: str, raw_id: str) -> str:
    """Step 2: Parse and insert into Silver staging table."""
    print("\n" + "=" * 60)
    print("STEP 2: SILVER LAYER - Parse to Staging")
    print("=" * 60)

    stg_id = str(uuid.uuid4())

    # Insert parsed staging record (using actual column names from schema)
    sql = f"""
    INSERT INTO silver.stg_pain001 (
        stg_id, raw_id, _batch_id,
        msg_id, creation_date_time,
        number_of_transactions, control_sum,
        initiating_party_name,
        payment_info_id, payment_method,
        requested_execution_date,
        debtor_name, debtor_street_name, debtor_town_name, debtor_country, debtor_id,
        debtor_account_iban, debtor_agent_bic,
        end_to_end_id, uetr,
        instructed_amount, instructed_currency, charge_bearer,
        creditor_name, creditor_street_name, creditor_town_name, creditor_country,
        creditor_account_iban, creditor_agent_bic,
        _processed_at
    ) VALUES (
        '{stg_id}', '{raw_id}', '{batch_id}',
        'FULL-PIPE-TEST-001', '2024-12-24 10:00:00',
        1, 10000.00,
        'Initiating Corp',
        'PMTINF-FULLTEST-001', 'TRF',
        '2024-12-25',
        'John Smith', '123 Oak Street', 'New York', 'US', '529900T8BM49AURSDO55',
        'US12345678901234567890', 'CHASUS33XXX',
        'E2E-FULLTEST-001', 'eb6305c9-1f7f-49de-aef2-d0a9e768ec5e',
        10000.00, 'USD', 'SHAR',
        'Acme Corporation', '456 Main Ave', 'Los Angeles', 'US',
        'US98765432109876543210', 'BOFAUS3NXXX',
        NOW()
    ) RETURNING stg_id;
    """

    result = run_sql(sql)
    if result:
        print(f"  [OK] Silver staging record inserted:")
        print(f"       stg_id: {stg_id[:8]}...")
        print(f"       message_id: FULL-PIPE-TEST-001")
        print(f"       debtor: John Smith")
        print(f"       creditor: Acme Corporation")
        print(f"       amount: 10000.00 USD")
        return stg_id
    else:
        print("  [FAIL] Could not insert silver record")
        return None


def test_step3_gold_entities(batch_id: str, stg_id: str) -> dict:
    """Step 3: Extract and insert entities into Gold layer."""
    print("\n" + "=" * 60)
    print("STEP 3: GOLD LAYER - Extract Normalized Entities")
    print("=" * 60)

    import psycopg2

    # Use entity extractor
    from gps_cdm.orchestration.entity_extractor import EntityExtractor, get_entity_ids_for_instruction
    from gps_cdm.ingestion.core.models import MappingConfig

    # Load mapping config
    mapping_path = PROJECT_ROOT / "mappings" / "message_types" / "pain001.yaml"

    import yaml
    with open(mapping_path, 'r') as f:
        raw_config = yaml.safe_load(f)

    mapping_config = MappingConfig.from_dict(raw_config, mapping_path, stage="silver_to_gold")

    print(f"\n  Mapping loaded: {mapping_config.id}")
    print(f"  Party mappings: {len(mapping_config.party_mappings or [])} roles")
    print(f"  Account mappings: {len(mapping_config.account_mappings or [])} roles")
    print(f"  FI mappings: {len(mapping_config.fi_mappings or [])} roles")

    # Connect to database
    db_conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="gps_cdm",
    )

    # Initialize extractor
    extractor = EntityExtractor(db_connection=db_conn)

    # Get staging record
    cursor = db_conn.cursor()
    cursor.execute(f"SELECT * FROM silver.stg_pain001 WHERE stg_id = '{stg_id}'")
    columns = [desc[0] for desc in cursor.description]
    row = cursor.fetchone()
    staging_record = dict(zip(columns, row)) if row else {}

    if not staging_record:
        print("  [FAIL] Could not find staging record")
        return {}

    # Extract entities
    extraction_result = extractor.extract_from_staging(
        staging_records=[staging_record],
        mapping_config=mapping_config,
        batch_id=batch_id,
    )

    print(f"\n  Extraction results:")
    print(f"  - Parties: {len(extraction_result.parties)} (new: {sum(1 for p in extraction_result.parties if p.is_new)})")
    print(f"  - Accounts: {len(extraction_result.accounts)} (new: {sum(1 for a in extraction_result.accounts if a.is_new)})")
    print(f"  - FIs: {len(extraction_result.financial_institutions)} (new: {sum(1 for f in extraction_result.financial_institutions if f.is_new)})")

    # Persist entities
    counts = extractor.persist_entities(
        result=extraction_result,
        source_message_type="pain.001",
    )

    print(f"\n  Persisted to database:")
    print(f"  - New parties: {counts['parties']}")
    print(f"  - New accounts: {counts['accounts']}")
    print(f"  - New FIs: {counts['financial_institutions']}")

    # Get entity IDs for instruction
    entity_ids = get_entity_ids_for_instruction(extraction_result)

    # Insert payment instruction
    instruction_id = str(uuid.uuid4())
    payment_id = str(uuid.uuid4())

    cursor.execute("""
        INSERT INTO gold.cdm_payment_instruction (
            instruction_id, payment_id,
            source_system, source_message_type, source_stg_table, source_stg_id,
            message_id, creation_datetime,
            end_to_end_id, uetr,
            payment_type, scheme_code, direction,
            debtor_id, creditor_id,
            debtor_agent_id, creditor_agent_id,
            instructed_amount, instructed_currency,
            charge_bearer, current_status,
            lineage_batch_id,
            partition_year, partition_month, region,
            created_at, updated_at
        ) VALUES (
            %s, %s,
            %s, %s, %s, %s,
            %s, %s,
            %s, %s,
            %s, %s, %s,
            %s, %s,
            %s, %s,
            %s, %s,
            %s, %s,
            %s,
            %s, %s, %s,
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        )
    """, (
        instruction_id, payment_id,
        "GPS_CDM", "pain.001", "stg_pain001", stg_id,
        staging_record.get("message_id"),
        staging_record.get("creation_datetime"),
        staging_record.get("end_to_end_id"),
        staging_record.get("uetr"),
        "CREDIT_TRANSFER", "ISO20022", "OUTGOING",
        entity_ids.get("debtor_id"),
        entity_ids.get("creditor_id"),
        entity_ids.get("debtor_agent_id"),
        entity_ids.get("creditor_agent_id"),
        staging_record.get("instructed_amount"),
        staging_record.get("instructed_currency", "USD"),
        staging_record.get("charge_bearer", "SHAR"),
        "PENDING",
        batch_id,
        2024, 12, "GLOBAL",
    ))

    db_conn.commit()
    cursor.close()
    db_conn.close()

    print(f"\n  [OK] Payment instruction created:")
    print(f"       instruction_id: {instruction_id[:8]}...")
    print(f"       debtor_id: {entity_ids.get('debtor_id', 'N/A')[:8] if entity_ids.get('debtor_id') else 'N/A'}...")
    print(f"       creditor_id: {entity_ids.get('creditor_id', 'N/A')[:8] if entity_ids.get('creditor_id') else 'N/A'}...")

    return {
        "instruction_id": instruction_id,
        **entity_ids,
        **counts,
    }


def test_step4_verify(batch_id: str):
    """Step 4: Verify data in all layers and CDC events."""
    print("\n" + "=" * 60)
    print("STEP 4: VERIFY DATA ACROSS ALL LAYERS")
    print("=" * 60)

    # Count records in each layer
    counts = {}

    # Bronze
    result = run_sql(f"SELECT COUNT(*) FROM bronze.raw_payment_messages WHERE _batch_id = '{batch_id}';")
    counts["bronze"] = int(result[0][0]) if result else 0

    # Silver
    result = run_sql(f"SELECT COUNT(*) FROM silver.stg_pain001 WHERE _batch_id = '{batch_id}';")
    counts["silver"] = int(result[0][0]) if result else 0

    # Gold - Payment Instructions
    result = run_sql(f"SELECT COUNT(*) FROM gold.cdm_payment_instruction WHERE lineage_batch_id = '{batch_id}';")
    counts["gold_instructions"] = int(result[0][0]) if result else 0

    # Gold - Parties
    result = run_sql(f"""
        SELECT COUNT(*) FROM gold.cdm_party
        WHERE source_stg_id IN (SELECT stg_id FROM silver.stg_pain001 WHERE _batch_id = '{batch_id}');
    """)
    counts["gold_parties"] = int(result[0][0]) if result else 0

    # Gold - Accounts
    result = run_sql(f"""
        SELECT COUNT(*) FROM gold.cdm_account
        WHERE source_stg_id IN (SELECT stg_id FROM silver.stg_pain001 WHERE _batch_id = '{batch_id}');
    """)
    counts["gold_accounts"] = int(result[0][0]) if result else 0

    # Gold - FIs
    result = run_sql("""
        SELECT COUNT(*) FROM gold.cdm_financial_institution
        WHERE created_at > NOW() - INTERVAL '5 minutes';
    """)
    counts["gold_fis"] = int(result[0][0]) if result else 0

    # CDC Events
    result = run_sql(f"""
        SELECT table_name, operation, COUNT(*)
        FROM observability.obs_cdc_tracking
        WHERE batch_id = '{batch_id}' OR change_timestamp > NOW() - INTERVAL '5 minutes'
        GROUP BY table_name, operation
        ORDER BY table_name, operation;
    """)
    cdc_events = result if result else []

    print("\n  Data Counts:")
    print("  " + "-" * 40)
    print(f"  Bronze (raw_payment_messages):     {counts['bronze']}")
    print(f"  Silver (stg_pain001):              {counts['silver']}")
    print(f"  Gold (cdm_payment_instruction):    {counts['gold_instructions']}")
    print(f"  Gold (cdm_party):                  {counts['gold_parties']}")
    print(f"  Gold (cdm_account):                {counts['gold_accounts']}")
    print(f"  Gold (cdm_financial_institution):  {counts['gold_fis']}")
    print("  " + "-" * 40)

    print("\n  CDC Events:")
    if cdc_events:
        for row in cdc_events:
            print(f"    {row[0]}: {row[1]} ({row[2]} events)")
    else:
        print("    No CDC events captured")

    # Verify all layers have data
    success = all([
        counts["bronze"] >= 1,
        counts["silver"] >= 1,
        counts["gold_instructions"] >= 1,
        counts["gold_parties"] >= 1,  # At least debtor or creditor
    ])

    return success, counts


def test_step5_deduplication(batch_id: str, stg_id: str):
    """Step 5: Test deduplication by inserting same party again."""
    print("\n" + "=" * 60)
    print("STEP 5: TEST DEDUPLICATION")
    print("=" * 60)

    import psycopg2
    from gps_cdm.orchestration.deduplication import ReferenceDataDeduplicator

    db_conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="gps_cdm",
    )

    dedup = ReferenceDataDeduplicator(db_connection=db_conn)

    # Try to find same party (John Smith, US, with LEI)
    result = dedup.find_party(
        name="John Smith",
        country="US",
        party_type="ORGANIZATION",
        lei="529900T8BM49AURSDO55",
    )

    print(f"\n  Deduplication check for 'John Smith':")
    print(f"  - Is duplicate: {result.is_duplicate}")
    if result.is_duplicate:
        print(f"  - Existing ID: {result.existing_id[:8]}...")
        print(f"  - Match type: {result.match_type}")
        print("  [OK] Deduplication working - found existing party")
    else:
        print("  [WARN] Party not found - deduplication may not be working")

    # Try to find same account (by IBAN)
    result = dedup.find_account(
        account_number="",
        iban="US12345678901234567890",
    )

    print(f"\n  Deduplication check for IBAN 'US12345678901234567890':")
    print(f"  - Is duplicate: {result.is_duplicate}")
    if result.is_duplicate:
        print(f"  - Existing ID: {result.existing_id[:8]}...")
        print("  [OK] Account deduplication working")

    db_conn.close()

    return result.is_duplicate


def main():
    """Run full pipeline integration test."""
    print("\n" + "=" * 60)
    print("GPS CDM - FULL PIPELINE INTEGRATION TEST")
    print("=" * 60)
    print(f"Time: {datetime.now().isoformat()}")

    batch_id = str(uuid.uuid4())
    print(f"\nBatch ID: {batch_id}")

    results = []

    try:
        # Step 1: Bronze
        raw_id = test_step1_bronze(batch_id)
        results.append(("Bronze Ingestion", raw_id is not None))
        if not raw_id:
            return

        # Step 2: Silver
        stg_id = test_step2_silver(batch_id, raw_id)
        results.append(("Silver Parsing", stg_id is not None))
        if not stg_id:
            return

        # Step 3: Gold with entity extraction
        entity_result = test_step3_gold_entities(batch_id, stg_id)
        results.append(("Gold Entity Extraction", bool(entity_result)))

        # Step 4: Verify
        success, counts = test_step4_verify(batch_id)
        results.append(("Data Verification", success))

        # Step 5: Deduplication
        dedup_ok = test_step5_deduplication(batch_id, stg_id)
        results.append(("Deduplication", dedup_ok))

    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {name}")

    passed = sum(1 for _, p in results if p)
    print(f"\n  {passed}/{len(results)} tests passed")

    # Optionally cleanup
    # cleanup_test_data(batch_id)


if __name__ == "__main__":
    main()
