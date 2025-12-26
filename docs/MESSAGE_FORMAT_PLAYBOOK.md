# GPS CDM Message Format Extraction Playbook

**Date**: 2025-12-26
**Status**: In Progress

## Overview

This playbook documents the process for adding complete field coverage to GPS CDM message format extractors. It covers 67 payment message formats across ISO 20022, SWIFT MT, and regional payment schemes.

## Architecture

### Folder Structure

```
src/gps_cdm/message_formats/
├── __init__.py              # Module init, get_extractor() function
├── base/
│   └── __init__.py          # BaseExtractor class, ExtractorRegistry
├── pain001/                  # ISO 20022 pain.001
│   ├── __init__.py          # Exports Pain001Extractor
│   ├── extractor.py         # Main extractor class
│   ├── silver_schema.py     # Silver column definitions
│   └── gold_entities.py     # Gold entity extraction logic
├── mt103/                    # SWIFT MT103
│   └── ...
├── pacs008/                  # ISO 20022 pacs.008
│   └── ...
├── fedwire/                  # US Fedwire
│   └── ...
└── ... (60+ additional formats)
```

### Extractor Class Pattern

Each message format extractor inherits from `BaseExtractor` and implements:

```python
class Pain001Extractor(BaseExtractor):
    MESSAGE_TYPE = "pain.001"
    SILVER_TABLE = "stg_pain001"

    def extract_bronze(self, raw_content, batch_id):
        # Extract Bronze layer fields
        pass

    def extract_silver(self, msg_content, raw_id, stg_id, batch_id):
        # Extract ALL Silver layer fields - 100% coverage
        pass

    def get_silver_columns(self):
        # Return ordered list of Silver columns
        pass

    def get_silver_values(self, silver_record):
        # Return ordered tuple for INSERT
        pass

    def extract_gold_entities(self, msg_content, stg_id, batch_id):
        # Extract Party, Account, FI entities for Gold
        pass
```

## Completed Message Formats (4/67)

| Format | Silver Coverage | Gold Coverage | Status |
|--------|----------------|---------------|--------|
| pain.001 | 100% (77/77) | Pending Audit | ✅ Complete |
| MT103 | 100% (54/54) | Pending Audit | ✅ Complete |
| pacs.008 | 100% (85/85) | Pending Audit | ✅ Complete |
| FEDWIRE | 100% (68/68) | Pending Audit | ✅ Complete |

## Pending Message Formats (63/67)

### ISO 20022 PAIN Family (5 remaining)
- [ ] pain.002 - Customer Payment Status Report
- [ ] pain.007 - Customer Payment Reversal
- [ ] pain.008 - Customer Direct Debit Initiation
- [ ] pain.013 - Creditor Payment Activation Request
- [ ] pain.014 - Creditor Payment Activation Request Status Report

### ISO 20022 PACS Family (6 remaining)
- [ ] pacs.002 - FI to FI Payment Status Report
- [ ] pacs.003 - FI to FI Customer Direct Debit
- [ ] pacs.004 - Payment Return
- [ ] pacs.007 - FI to FI Payment Reversal
- [ ] pacs.009 - FI Credit Transfer
- [ ] pacs.028 - FI to FI Payment Status Request

### ISO 20022 CAMT Family (12 formats)
- [ ] camt.026 - Unable to Apply
- [ ] camt.027 - Claim Non Receipt
- [ ] camt.028 - Additional Payment Information
- [ ] camt.029 - Resolution of Investigation
- [ ] camt.052 - Bank to Customer Account Report
- [ ] camt.053 - Bank to Customer Statement
- [ ] camt.054 - Bank to Customer Debit Credit Notification
- [ ] camt.055 - Customer Payment Cancellation Request
- [ ] camt.056 - FI to FI Payment Cancellation Request
- [ ] camt.057 - Notification to Receive
- [ ] camt.086 - Bank Services Billing Statement
- [ ] camt.087 - Request to Modify Payment

### ISO 20022 ACMT Family (6 formats)
- [ ] acmt.001 - Account Opening Request
- [ ] acmt.002 - Account Opening Additional Information Request
- [ ] acmt.003 - Account Opening Amendment Request
- [ ] acmt.005 - Account Switch Information Request
- [ ] acmt.006 - Account Switch Information Response
- [ ] acmt.007 - Account Switch Cancel Request

### SWIFT MT Family (7 remaining)
- [ ] MT200 - Financial Institution Transfer
- [ ] MT202 - General Financial Institution Transfer
- [ ] MT202COV - General Financial Institution Transfer (Cover Payment)
- [ ] MT900 - Confirmation of Debit
- [ ] MT910 - Confirmation of Credit
- [ ] MT940 - Customer Statement
- [ ] MT950 - Statement Message

### Regional Payment Schemes (27 formats)
#### US Payments
- [ ] NACHA_ACH - ACH Batch Format
- [ ] CHIPS - Clearing House Interbank Payments

#### UK Payments
- [ ] BACS - Bankers' Automated Clearing Services
- [ ] CHAPS - Clearing House Automated Payment System
- [ ] FPS - Faster Payments Service

#### EU Payments
- [ ] SEPA_SCT - SEPA Credit Transfer
- [ ] SEPA_SDD - SEPA Direct Debit
- [ ] TARGET2 - Trans-European RTGS

#### Real-Time Payment Systems
- [ ] FedNow - Federal Reserve Real-Time
- [ ] RTP - TCH Real-Time Payments
- [ ] PIX - Brazil Instant Payments
- [ ] NPP - Australia New Payments Platform
- [ ] UPI - India Unified Payments Interface
- [ ] PayNow - Singapore Real-Time
- [ ] PromptPay - Thailand Real-Time
- [ ] InstaPay - Philippines Real-Time

#### RTGS Systems
- [ ] BOJNET - Bank of Japan Net
- [ ] CNAPS - China National Advanced Payment System
- [ ] MEPS_PLUS - Singapore RTGS
- [ ] RTGS_HK - Hong Kong RTGS
- [ ] SARIE - Saudi Arabia RTGS
- [ ] UAEFTS - UAE RTGS
- [ ] KFTC - Korea Financial Telecommunications

## Playbook for Adding New Message Format

### Step 1: Create Test Data (Required First)

```bash
# Create test_data/{format}_compliant.json with sample messages
# Include ALL fields that the format can contain
```

### Step 2: Audit Current Coverage

```bash
# Run audit script to compare test data vs Silver columns
python /tmp/audit_field_coverage.py --format {format_name}
```

### Step 3: Add Missing Silver Columns

```sql
-- Create DDL file: /ddl/postgresql/XX_{format}_missing_columns.sql
ALTER TABLE silver.stg_{format} ADD COLUMN IF NOT EXISTS {column} {type};
```

### Step 4: Update Extraction Code

1. Add extraction logic to `celery_tasks.py` (or create separate extractor class)
2. Extract ALL fields from source JSON
3. Map to Silver column names
4. Ensure correct data types and truncation

### Step 5: Test Extraction

```bash
# Run test script
GPS_CDM_DATA_SOURCE=postgresql python3 /tmp/test_{format}_extraction.py
```

### Step 6: Verify Field Capture

```sql
-- Verify all new fields are populated
SELECT {new_columns} FROM silver.stg_{format} WHERE _batch_id = 'test_batch';
```

### Step 7: Audit Gold Coverage

```sql
-- Check Gold entity extraction completeness
SELECT * FROM gold.cdm_party WHERE source_stg_id = '{stg_id}';
SELECT * FROM gold.cdm_account WHERE source_stg_id = '{stg_id}';
SELECT * FROM gold.cdm_financial_institution WHERE source_stg_id = '{stg_id}';
```

### Step 8: Update Documentation

- Update FIELD_COVERAGE_AUDIT_REPORT.md
- Mark format complete in this playbook

## Parallelization Strategy

### Safe to Parallelize
- Silver table DDL changes (different tables)
- Silver extraction code updates (different message types)
- Test data creation

### Must Coordinate
- Gold table schema changes (shared tables)
- Gold entity extraction logic (shared code paths)
- Cross-zone comparison API changes

### Parallel Agent Workflow

```
Agent 1: pain.002, pain.007, pain.008
Agent 2: pacs.002, pacs.003, pacs.004
Agent 3: MT200, MT202, MT202COV
Agent 4: SEPA_SCT, SEPA_SDD, TARGET2
Agent 5: FedNow, RTP, CHIPS
```

Before starting:
1. Claim message format assignments
2. Lock Gold schema changes (one agent at a time)
3. Document progress in shared tracker

## Audit Results Tracking

### Before/After Template

| Format | Before Silver | After Silver | Before Gold | After Gold |
|--------|---------------|--------------|-------------|------------|
| pain.001 | 76.6% | 100% | TBD | TBD |
| MT103 | 64.8% | 100% | TBD | TBD |
| pacs.008 | 54.1% | 100% | TBD | TBD |
| FEDWIRE | 39.7% | 100% | TBD | TBD |

## Next Steps

1. **Immediate**: Audit Silver-to-Gold mapping for completed 4 formats
2. **Short-term**: Refactor extractors into separate classes
3. **Medium-term**: Add remaining 63 message formats using playbook
4. **Long-term**: Implement automated coverage testing in CI/CD
