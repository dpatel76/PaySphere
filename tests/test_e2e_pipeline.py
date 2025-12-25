#!/usr/bin/env python3
"""
End-to-End Pipeline Test for GPS CDM.

Tests the complete flow:
1. Message parsing
2. Table routing
3. Bronze layer processing
4. Silver layer transformation
5. Gold layer consolidation

Usage:
    python tests/test_e2e_pipeline.py
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gps_cdm.orchestration.message_parsers import MESSAGE_PARSERS
from gps_cdm.orchestration.celery_tasks import get_table_routing, get_all_message_types


def test_table_routing_coverage():
    """Test that all message types have routing configured."""
    print("\n" + "=" * 70)
    print("Testing Table Routing Coverage")
    print("=" * 70)

    all_types = get_all_message_types()
    print(f"\nTotal message types from get_all_message_types(): {len(all_types)}")

    missing_routing = []
    routing_results = {}

    for msg_type in all_types:
        routing = get_table_routing(msg_type)
        if routing:
            routing_results[msg_type] = routing
        else:
            missing_routing.append(msg_type)

    print(f"Message types with routing: {len(routing_results)}")
    print(f"Message types missing routing: {len(missing_routing)}")

    if missing_routing:
        print("\nMissing routing for:")
        for mt in missing_routing[:10]:
            print(f"  - {mt}")
        if len(missing_routing) > 10:
            print(f"  ... and {len(missing_routing) - 10} more")

    return len(missing_routing) == 0


def test_parser_to_routing_mapping():
    """Test that parsers and routing align."""
    print("\n" + "=" * 70)
    print("Testing Parser to Routing Mapping")
    print("=" * 70)

    # Get unique parser message types
    parser_types = set()
    for key in MESSAGE_PARSERS.keys():
        # Normalize the key
        normalized = key.lower().replace(".", "_").replace("-", "_")
        parser_types.add(normalized)

    # Get routing message types
    all_types = get_all_message_types()
    routing_types = set()
    for msg_type in all_types:
        normalized = msg_type.lower().replace(".", "_").replace("-", "_")
        routing_types.add(normalized)

    print(f"\nUnique parser types (normalized): {len(parser_types)}")
    print(f"Unique routing types (normalized): {len(routing_types)}")

    # Find gaps
    parsers_without_routing = parser_types - routing_types
    routing_without_parsers = routing_types - parser_types

    print(f"\nParser types without routing: {len(parsers_without_routing)}")
    if parsers_without_routing:
        for pt in list(parsers_without_routing)[:5]:
            print(f"  - {pt}")

    print(f"Routing types without parsers: {len(routing_without_parsers)}")
    if routing_without_parsers:
        for rt in list(routing_without_parsers)[:5]:
            print(f"  - {rt}")

    return True  # Informational test


def test_table_structure():
    """Test that routing returns proper table structure."""
    print("\n" + "=" * 70)
    print("Testing Table Structure")
    print("=" * 70)

    test_types = [
        "pain.001", "pacs.008", "MT103", "SEPA_SCT",
        "NACHA_ACH", "FEDWIRE", "FEDNOW", "RTP", "PIX", "TARGET2"
    ]

    all_valid = True

    for msg_type in test_types:
        routing = get_table_routing(msg_type)
        if routing:
            # Check required fields
            required = ["bronze_table", "silver_table", "gold_tables", "payment_type", "scheme"]
            missing = [f for f in required if f not in routing]

            if missing:
                print(f"  ✗ {msg_type}: Missing fields: {missing}")
                all_valid = False
            else:
                print(f"  ✓ {msg_type}:")
                print(f"      Bronze: {routing['bronze_table']}")
                print(f"      Silver: {routing['silver_table']}")
                print(f"      Gold: {routing['gold_tables']}")
                print(f"      Type: {routing['payment_type']}, Scheme: {routing['scheme']}")
        else:
            print(f"  ✗ {msg_type}: No routing found")
            all_valid = False

    return all_valid


def test_bronze_silver_gold_mapping():
    """Test the Bronze → Silver → Gold table mapping for key message types."""
    print("\n" + "=" * 70)
    print("Testing Bronze → Silver → Gold Mapping")
    print("=" * 70)

    # Test mapping for different categories
    test_cases = [
        # ISO 20022 PAIN
        ("pain.001", "bronze_pain001", "silver_pain001", ["gold_cdm_payment_instruction"]),
        ("pain.008", "bronze_pain008", "silver_pain008", ["gold_cdm_direct_debit"]),

        # ISO 20022 PACS
        ("pacs.008", "bronze_pacs008", "silver_pacs008", ["gold_cdm_payment_instruction"]),
        ("pacs.004", "bronze_pacs004", "silver_pacs004", ["gold_cdm_payment_return"]),

        # ISO 20022 CAMT
        ("camt.053", "bronze_camt053", "silver_camt053", ["gold_cdm_account_statement"]),

        # SWIFT MT
        ("MT103", "bronze_mt103", "silver_mt103", ["gold_cdm_payment_instruction"]),
        ("MT940", "bronze_mt940", "silver_mt940", ["gold_cdm_account_statement"]),

        # Domestic
        ("SEPA_SCT", "bronze_sepa_sct", "silver_sepa_sct", ["gold_cdm_payment_instruction"]),
        ("NACHA_ACH", "bronze_nacha_ach", "silver_nacha_ach", ["gold_cdm_payment_instruction"]),
        ("FEDWIRE", "bronze_fedwire", "silver_fedwire", ["gold_cdm_payment_instruction"]),

        # Real-Time
        ("FEDNOW", "bronze_fednow", "silver_fednow", ["gold_cdm_payment_instruction"]),
        ("PIX", "bronze_pix", "silver_pix", ["gold_cdm_payment_instruction"]),
        ("RTP", "bronze_rtp", "silver_rtp", ["gold_cdm_payment_instruction"]),

        # RTGS
        ("TARGET2", "bronze_target2", "silver_target2", ["gold_cdm_payment_instruction"]),
    ]

    passed = 0
    failed = 0

    for msg_type, exp_bronze, exp_silver, exp_gold in test_cases:
        routing = get_table_routing(msg_type)
        if routing:
            bronze_ok = routing["bronze_table"] == exp_bronze
            silver_ok = routing["silver_table"] == exp_silver
            # Gold tables should contain at least one expected table
            gold_ok = any(g in routing["gold_tables"] for g in exp_gold)

            if bronze_ok and silver_ok and gold_ok:
                print(f"  ✓ {msg_type}: {exp_bronze} → {exp_silver} → {exp_gold[0]}")
                passed += 1
            else:
                print(f"  ✗ {msg_type}:")
                if not bronze_ok:
                    print(f"      Bronze mismatch: {routing['bronze_table']} != {exp_bronze}")
                if not silver_ok:
                    print(f"      Silver mismatch: {routing['silver_table']} != {exp_silver}")
                if not gold_ok:
                    print(f"      Gold mismatch: {routing['gold_tables']} doesn't contain {exp_gold}")
                failed += 1
        else:
            print(f"  ✗ {msg_type}: No routing")
            failed += 1

    print(f"\nPassed: {passed}, Failed: {failed}")
    return failed == 0


def test_simulated_pipeline_flow():
    """Simulate a complete pipeline flow for a sample message."""
    print("\n" + "=" * 70)
    print("Simulating Complete Pipeline Flow")
    print("=" * 70)

    # Sample pain.001 message
    sample_message = {
        "Document": {
            "CstmrCdtTrfInitn": {
                "GrpHdr": {
                    "MsgId": "E2E-TEST-001",
                    "CreDtTm": "2024-12-24T10:30:00Z",
                    "NbOfTxs": "1",
                    "CtrlSum": "10000.00"
                },
                "PmtInf": [{
                    "PmtInfId": "PMT-001",
                    "DbtrNm": "Test Debtor",
                    "CdtTrfTxInf": [{
                        "PmtId": {"EndToEndId": "E2E-001"},
                        "Amt": {"InstdAmt": {"Ccy": "USD", "#text": "10000.00"}},
                        "CdtrNm": "Test Creditor"
                    }]
                }]
            }
        }
    }

    msg_type = "pain.001"

    # Step 1: Parse message
    print("\n1. PARSING MESSAGE")
    parser_class = MESSAGE_PARSERS.get(msg_type)
    if not parser_class:
        print(f"   ✗ No parser for {msg_type}")
        return False

    parser = parser_class()
    try:
        parsed = parser.parse(json.dumps(sample_message))
        print(f"   ✓ Parsed {msg_type} message")
        print(f"     Message ID: {parsed.get('message_id', 'N/A')}")
        print(f"     Fields extracted: {len(parsed)}")
    except Exception as e:
        print(f"   ✗ Parse error: {e}")
        return False

    # Step 2: Get routing
    print("\n2. GETTING TABLE ROUTING")
    routing = get_table_routing(msg_type)
    if not routing:
        print(f"   ✗ No routing for {msg_type}")
        return False

    print(f"   ✓ Routing found:")
    print(f"     Bronze: {routing['bronze_table']}")
    print(f"     Silver: {routing['silver_table']}")
    print(f"     Gold: {routing['gold_tables']}")

    # Step 3: Simulate Bronze insert
    print("\n3. BRONZE LAYER (Raw Storage)")
    bronze_record = {
        "raw_id": "RAW-001",
        "message_type": msg_type,
        "raw_content": json.dumps(sample_message),
        "file_name": "test_file.xml",
        "source_system": "TEST",
        "_ingested_at": datetime.now().isoformat(),
        "_batch_id": "BATCH-001"
    }
    print(f"   ✓ Bronze record prepared for {routing['bronze_table']}")
    print(f"     Raw ID: {bronze_record['raw_id']}")

    # Step 4: Simulate Silver transform
    print("\n4. SILVER LAYER (Normalized)")
    silver_record = {
        "stg_id": "STG-001",
        "raw_id": bronze_record["raw_id"],
        "message_type": msg_type,
        "message_id": parsed.get("message_id", "UNKNOWN"),
        "creation_datetime": parsed.get("creation_datetime"),
        "number_of_transactions": parsed.get("number_of_transactions", 1),
        "control_sum": parsed.get("control_sum"),
        "debtor_name": parsed.get("debtor_name"),
        "creditor_name": parsed.get("creditor_name"),
        "instructed_amount": parsed.get("instructed_amount"),
        "instructed_currency": parsed.get("instructed_currency"),
        "dq_score": 0.95,
        "_processed_at": datetime.now().isoformat()
    }
    print(f"   ✓ Silver record prepared for {routing['silver_table']}")
    print(f"     Staging ID: {silver_record['stg_id']}")
    print(f"     DQ Score: {silver_record['dq_score']}")

    # Step 5: Simulate Gold CDM
    print("\n5. GOLD LAYER (CDM)")
    gold_record = {
        "instruction_id": "INSTR-001",
        "message_source_type": msg_type,
        "source_stg_id": silver_record["stg_id"],
        "payment_type": routing["payment_type"],
        "scheme": routing["scheme"],
        "payer_name": silver_record.get("debtor_name"),
        "payee_name": silver_record.get("creditor_name"),
        "amount": silver_record.get("instructed_amount"),
        "currency": silver_record.get("instructed_currency"),
        "status": "RECEIVED",
        "_cdm_version": "2.0",
        "_created_at": datetime.now().isoformat()
    }
    print(f"   ✓ Gold CDM record prepared for {routing['gold_tables'][0]}")
    print(f"     Instruction ID: {gold_record['instruction_id']}")
    print(f"     Payment Type: {gold_record['payment_type']}")

    print("\n" + "=" * 70)
    print("Pipeline Flow Simulation COMPLETED SUCCESSFULLY")
    print("=" * 70)

    return True


def run_all_tests():
    """Run all E2E tests."""
    print("=" * 70)
    print("GPS CDM End-to-End Pipeline Tests")
    print("=" * 70)

    results = []

    # Test 1: Table routing coverage
    results.append(("Table Routing Coverage", test_table_routing_coverage()))

    # Test 2: Parser to routing mapping
    results.append(("Parser-Routing Mapping", test_parser_to_routing_mapping()))

    # Test 3: Table structure
    results.append(("Table Structure", test_table_structure()))

    # Test 4: Bronze-Silver-Gold mapping
    results.append(("B-S-G Mapping", test_bronze_silver_gold_mapping()))

    # Test 5: Simulated pipeline flow
    results.append(("Pipeline Flow", test_simulated_pipeline_flow()))

    # Summary
    print("\n" + "=" * 70)
    print("E2E Test Summary")
    print("=" * 70)

    passed = 0
    failed = 0

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {status}: {name}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal: {passed} passed, {failed} failed")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
