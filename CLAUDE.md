# GPS CDM Project - Claude Context

## Project Overview

GPS Common Domain Model (CDM) - A payment message processing pipeline supporting 63+ payment standards across ISO 20022, SWIFT MT, and regional payment schemes. Uses medallion architecture (Bronze → Silver → Gold) with Celery for distributed task processing and NiFi for flow orchestration.

## Architecture (v2.0 - Kafka-Based)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INGESTION TIER                                 │
│  Files (SFTP/S3) → NiFi (Parse + Route) → Kafka (payment.bronze.{type})    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROCESSING TIER                                   │
│  Kafka Consumer → MicroBatchAccumulator (10K records) → BulkWriter (COPY)  │
│                          │                                                  │
│                          ▼                                                  │
│  Celery Beat (poll pending) → Bronze→Silver→Gold promotion tasks           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PERSISTENCE TIER                                   │
│  Bronze (raw_*) → Silver (stg_*) → Gold (cdm_*) [PostgreSQL/Databricks]    │
│                          │                                                  │
│  Observability: batch_tracking, kafka_checkpoints, micro_batch_tracking     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `MicroBatchAccumulator` | Accumulates Kafka messages, flushes on size/time | `streaming/micro_batch_accumulator.py` |
| `BulkWriter` | PostgreSQL COPY / Databricks COPY INTO | `streaming/bulk_writer.py` |
| `KafkaBatchConsumer` | Kafka consumer with checkpointing | `streaming/kafka_batch_consumer.py` |
| `batch_promotion_tasks` | Bronze→Silver→Gold Celery tasks | `orchestration/batch_promotion_tasks.py` |
| `batch_stats` API | Real-time processing stats | `api/routes/batch_stats.py` |

### Performance Targets

- **PostgreSQL COPY**: ~135,000 rows/second
- **Micro-batch size**: 10,000-50,000 records
- **Flush interval**: 10 seconds max
- **Target throughput**: 50M+ messages/day

### Restartability

Crash recovery is handled via:
1. **Kafka checkpoints** (`kafka_consumer_checkpoints`) - consumer offsets + pending records
2. **Micro-batch tracking** (`micro_batch_tracking`) - batch state through pipeline
3. **Dead letter queue** (`kafka_dead_letter_queue`) - failed batches for replay

On restart:
1. Consumer claims stale checkpoints (>60s heartbeat)
2. Pending records recovered from checkpoint
3. Incomplete batches resumed or sent to DLQ

---

## Legacy Architecture (v1.0 - Flower API)

```
NiFi (Flow Orchestration)
    → Flower API (Celery Task Submission) [DEPRECATED - unstable]
    → Redis (Message Broker)
    → Celery Workers (Task Processing)
    → PostgreSQL / Databricks (Persistence)
    → Neo4j (Knowledge Graph)
```

**Note**: Flower API had reliability issues (HTTP 400 errors, JSON escaping).
Use Kafka-based architecture (v2.0) for production.

## Key Learnings

### 1. Data Source Configuration

**Issue**: Celery tasks were always trying Databricks first, causing unnecessary warnings when running locally with PostgreSQL.

**Solution**: Use `GPS_CDM_DATA_SOURCE` environment variable to control which data store to use:
- `GPS_CDM_DATA_SOURCE=postgresql` (default) - Use PostgreSQL directly, skip Databricks
- `GPS_CDM_DATA_SOURCE=databricks` - Try Databricks, fallback to PostgreSQL

**Code Location**: `src/gps_cdm/orchestration/celery_tasks.py` (lines 688-709)

### 2. NiFi InvokeHTTP Startup Timing

**Issue**: First few files processed by NiFi failed at InvokeHTTP processor after container startup.

**Root Cause**: HTTP connection pool not fully established when first files arrive. The Failure/No Retry/Retry relationships are auto-terminated, hiding errors.

**Solution**:
- Wait ~30 seconds after NiFi starts before sending files
- Or restart the InvokeHTTP processor if seeing failures
- Files processed after warmup period succeed at 100% rate

**Debugging Tip**: To see InvokeHTTP errors, temporarily set `autoTerminate=false` for the Failure relationship and connect it to a LogAttribute processor.

### 3. NiFi Input Directory

**Correct Path**: `/opt/nifi/nifi-current/input/`
- GetFile processor polls every 30 seconds
- Files are deleted after reading (Keep Source File = false)

**Wrong Path**: `/opt/nifi/nifi-current/data/nifi_input/` - This was an old test directory with permission issues.

### 4. Celery Queue Routing

Celery tasks are routed to specific queues. Workers must listen to all queues:

```bash
celery -A gps_cdm.orchestration.celery_tasks worker \
    -Q celery,bronze,silver,gold,dq,cdc \
    --loglevel=info --concurrency=4
```

## Running the E2E Pipeline

### Prerequisites

Start all Docker containers:
```bash
docker-compose -f docker-compose.nifi.yaml up -d
```

Containers needed:
- `gps-cdm-postgres` - PostgreSQL database (port 5433)
- `gps-cdm-redis` - Redis broker (port 6379)
- `gps-cdm-nifi` - Apache NiFi (port 8080)
- `gps-cdm-flower` - Celery Flower API (port 5555)
- `gps-cdm-neo4j` - Neo4j graph database (ports 7474, 7687)

### Start Celery Worker

```bash
source .venv/bin/activate

GPS_CDM_DATA_SOURCE=postgresql \
POSTGRES_HOST=localhost \
POSTGRES_PORT=5433 \
POSTGRES_DB=gps_cdm \
POSTGRES_USER=gps_cdm_svc \
POSTGRES_PASSWORD=gps_cdm_password \
NEO4J_URI=bolt://localhost:7687 \
NEO4J_USER=neo4j \
NEO4J_PASSWORD=neo4jpassword123 \
PYTHONPATH=src:$PYTHONPATH \
celery -A gps_cdm.orchestration.celery_tasks worker \
    -Q celery,bronze,silver,gold,dq,cdc \
    --loglevel=info --concurrency=4
```

### Send Test Files via NiFi

```bash
# Create test file
echo '{"messageId": "TEST-001", "amount": 1000}' > /tmp/pain.001_test.json

# Copy to NiFi input directory
docker cp /tmp/pain.001_test.json gps-cdm-nifi:/opt/nifi/nifi-current/input/

# Wait for processing (GetFile polls every 30 sec)
sleep 35

# Check Celery log for task completion
tail -20 /tmp/celery_gps_cdm.log
```

### Direct Celery Task Submission (Bypass NiFi)

```python
from gps_cdm.orchestration.celery_tasks import process_bronze_partition

result = process_bronze_partition.delay(
    partition_id="test_001",
    file_paths=[],
    message_type="pain.001",
    batch_id="test_batch_001",
    config={
        "message_content": {
            "messageId": "TEST-001",
            "debtor": {"name": "Test Payer"},
            "creditor": {"name": "Test Payee"},
            "amount": 1000.00,
            "currency": "USD"
        }
    }
)

# Wait for result
output = result.get(timeout=30)
print(f"Status: {output['status']}, Persisted to: {output['persisted_to']}")
```

### Manual Flower API Call (Test from NiFi container)

```bash
docker exec gps-cdm-nifi curl -s -u admin:flowerpassword \
    -X POST "http://flower:5555/api/task/send-task/gps_cdm.orchestration.celery_tasks.process_bronze_partition" \
    -H "Content-Type: application/json" \
    -d '{"args": ["partition_001", [], "pain.001", "batch_001", {"message_content": {"test": true}}]}'
```

## NiFi Flow Structure

```
GPS CDM Payment Pipeline/
├── Message Type Detection/
│   ├── Read Test Messages (GetFile) - /opt/nifi/nifi-current/input/
│   ├── Detect Message Type from Filename (UpdateAttribute)
│   ├── Route by Message Type (RouteOnAttribute)
│   └── Output Ports: To Celery, To Celery Dispatch
├── Celery Task Dispatch/
│   ├── Prepare Celery Payload (UpdateAttribute) - Sets batch.id, celery.task
│   ├── Format Task Body (ReplaceText) - Creates JSON args
│   ├── Submit to Celery (InvokeHTTP) - POST to Flower API
│   └── Log Success (LogAttribute)
└── Error Handling/
    ├── Log Error (LogAttribute)
    └── Write to DLQ (PutFile)
```

## NiFi API Access

NiFi API requires the container hostname:
```bash
NIFI_HOST=$(docker exec gps-cdm-nifi hostname)
docker exec gps-cdm-nifi curl -s "http://${NIFI_HOST}:8080/nifi-api/flow/process-groups/root/status"
```

## Troubleshooting

### No Databricks Warnings
Set `GPS_CDM_DATA_SOURCE=postgresql` when starting Celery worker.

### NiFi Files Not Processing
1. Check input directory: `docker exec gps-cdm-nifi ls -la /opt/nifi/nifi-current/input/`
2. Check GetFile processor state: Should be RUNNING
3. Wait for poll interval (30 seconds)

### InvokeHTTP Failures (0 bytes sent)
1. Verify Flower is reachable: `docker exec gps-cdm-nifi curl -s http://flower:5555/api/tasks`
2. Check processor was recently restarted - first few requests may fail
3. Check NiFi logs: `docker logs gps-cdm-nifi --tail 50`

### Celery Tasks Not Received
1. Verify worker is listening on correct queues: `-Q celery,bronze,silver,gold,dq,cdc`
2. Check Redis connection: `redis-cli ping`
3. Check Flower dashboard: http://localhost:5555

## Database Verification

```sql
-- Check Bronze records
SELECT COUNT(*) FROM bronze.raw_payment_messages;

-- Check NiFi-originated records (UUID batch_ids)
SELECT COUNT(*) FROM bronze.raw_payment_messages
WHERE _batch_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$';

-- Recent records
SELECT raw_id, message_type, _batch_id, _ingested_at::timestamp(0)
FROM bronze.raw_payment_messages
ORDER BY _ingested_at DESC
LIMIT 10;
```

## File Naming Convention for NiFi

NiFi extracts message type from filename:
- `pain.001_test.json` → message_type = `pain.001`
- `pacs.008_12345.json` → message_type = `pacs.008`
- `mt103_abc.json` → message_type = `MT103`
- `fedwire_001.json` → message_type = `FEDWIRE`

Pattern: `{message_type}_{identifier}.{extension}`

---

## Known Issues & TODO

### Admin Reprocessing Functions (NEEDS FIX)

**Location**: `src/gps_cdm/api/routes/reprocess.py` and `src/gps_cdm/orchestration/reprocessor.py`

**Current State**:
- `PipelineReprocessor` runs **synchronously** in API request thread
- Does NOT use Celery tasks for distributed processing
- Does NOT go through NiFi flow
- `_promote_bronze_to_silver()` and `_promote_silver_to_gold()` are **stub implementations** that just return existing IDs
- Database connection uses wrong port (5432 instead of 5433)

**Required Fix**:
Reprocessing should dispatch to Celery via the same path as NiFi:

```python
# Current (WRONG - synchronous, stub implementation):
def reprocess_bronze_record(self, raw_id: str):
    stg_id = self._promote_bronze_to_silver(bronze_record)  # Stub!
    ...

# Should be (dispatch to Celery):
from gps_cdm.orchestration.celery_tasks import process_bronze_partition

def reprocess_bronze_record(self, raw_id: str):
    bronze_record = self._get_bronze_record(raw_id)
    result = process_bronze_partition.delay(
        partition_id=f"reprocess_{raw_id}",
        file_paths=[],
        message_type=bronze_record['message_type'],
        batch_id=f"reprocess_{datetime.now().isoformat()}",
        config={"message_content": json.loads(bronze_record['raw_content'])}
    )
    return result.get(timeout=60)  # Or return task_id for async
```

**Also Fix** in `reprocess.py`:
```python
# Wrong:
port=5432

# Correct:
port=int(os.environ.get("POSTGRES_PORT", 5433))
```

### Validation Checklist for E2E Flow

Before marking reprocessing as complete, verify:
- [ ] Reprocessing dispatches to Celery via `process_bronze_partition.delay()`
- [ ] Uses same transformation logic as NiFi flow
- [ ] Records appear in Bronze → Silver → Gold with proper lineage
- [ ] Neo4j graph is updated
- [ ] No Databricks warnings when `GPS_CDM_DATA_SOURCE=postgresql`

---

## Message Format Extractor Blueprint

### Learnings from First 6 Message Types (pain.001, MT103, FEDWIRE, ACH, SEPA, RTP)

The following patterns and fixes were applied to achieve 100% Bronze→Silver→Gold coverage:

#### 1. Python `.get()` Behavior with None Values

**Problem**: `.get('key', 'default')` returns `None` when the key exists with a `None` value, causing NOT NULL constraint violations.

**Solution**: Always use `or` pattern for defaults:
```python
# WRONG - returns None if key exists with None value
account_type = data.get('accountType', 'CACC')

# CORRECT - falls back to default even if key exists with None
account_type = data.get('accountType') or 'CACC'
```

**Apply to**: All extractors for `account_type`, `currency`, `country`, `party_type` fields.

#### 2. Silver Column Names Must Match Database Schema Exactly

**Problem**: Extractor column names didn't match actual PostgreSQL table columns.

**Examples of fixes needed**:
| Extractor Field | DB Column | Message Type |
|-----------------|-----------|--------------|
| sender_reference | senders_reference | MT103 |
| currency_code | currency | MT103 |
| instruction_code | instruction_codes | MT103 |
| sender_routing_number | sender_aba | FEDWIRE |
| receiver_routing_number | receiver_aba | FEDWIRE |
| standard_entry_class_code | standard_entry_class | ACH |
| debtor_account_iban | debtor_iban | SEPA |

**How to verify**: Query `information_schema.columns` for actual column names:
```sql
SELECT column_name FROM information_schema.columns
WHERE table_schema = 'silver' AND table_name = 'stg_XXXX'
ORDER BY ordinal_position;
```

#### 3. Remove Non-Existent Columns

**Problem**: Extractors included columns that don't exist in DB tables.

**Common issues**:
- `_ingested_at` - Not in Silver tables (auto-set by DB)
- Extra fields from spec that weren't added to schema

**Solution**: `get_silver_columns()` must return ONLY columns that exist in the DB table.

#### 4. Format-Specific Parsers Required

**DO NOT** rely on pre-parsed JSON. Each format needs its own parser:

| Format | Parser Type | Key Considerations |
|--------|-------------|-------------------|
| ISO 20022 (pain.001, pacs.008, SEPA) | XML with namespaces | Strip namespaces, handle optional elements |
| SWIFT MT (MT103, MT202) | Block format `{1:...}{2:...}{4:...}` | Regex for blocks, tag:value in block 4 |
| FEDWIRE | Tag-value `{NNNN}value` | 4-digit tags, handle multi-line values |
| ACH/NACHA | Fixed-width 94 chars | Pad lines to 94 chars, parse by position |
| RTP | XML (pacs.008 variant) | Similar to ISO 20022 |

#### 5. Test Data Format Compliance

**Problem**: Test data format didn't match actual standard format.

**Solutions by format**:
- **ACH**: Lines MUST be exactly 94 characters (pad with spaces)
- **FEDWIRE**: Subtype code is 2 chars max (e.g., "00" not "CORE")
- **SWIFT MT**: Must have block structure `{1:...}{2:...}{4:\n:20:...\n-}`
- **XML**: Must have proper namespace declarations

#### 6. Gold Entity Extraction Pattern

Each extractor must implement `extract_gold_entities()` returning `GoldEntities` with:
- `parties`: List of `PartyData` (DEBTOR, CREDITOR, ULTIMATE_*)
- `accounts`: List of `AccountData` with role
- `financial_institutions`: List of `FinancialInstitutionData` (DEBTOR_AGENT, CREDITOR_AGENT)

**Key defaults**:
```python
PartyData(name=..., party_type='UNKNOWN', role='DEBTOR')
AccountData(account_number=..., account_type='CACC', currency='USD')
FinancialInstitutionData(role='DEBTOR_AGENT', country='XX')
```

#### 7. Extension Tables for Scheme-Specific Data

Each payment scheme has an extension table in Gold for non-CDM fields:
- `gold.cdm_payment_extension_fedwire`
- `gold.cdm_payment_extension_ach`
- `gold.cdm_payment_extension_sepa`
- `gold.cdm_payment_extension_swift`
- `gold.cdm_payment_extension_rtp`
- `gold.cdm_payment_extension_iso20022`

Extension data classes are in `src/gps_cdm/message_formats/base/__init__.py`.

#### 8. YAML Mapping Sync Issues

**Problem**: `MappingSync` inserts duplicate rows on each sync instead of upserting.

**Impact**: Inflated mapping counts (e.g., 449 instead of 49).

**Workaround**: Use DISTINCT when querying mappings:
```sql
SELECT DISTINCT gold_column, source_expression
FROM mapping.gold_field_mappings
WHERE format_id = 'XXX' AND is_active = true
```

#### 9. Extractor Registration

Register each extractor with multiple aliases:
```python
ExtractorRegistry.register('MT103', Mt103Extractor())
ExtractorRegistry.register('mt103', Mt103Extractor())
ExtractorRegistry.register('MT103STP', Mt103Extractor())  # Variant
```

#### 10. Currency Field Fallbacks

ISO 20022 messages may have currency in different locations:
```python
currency = (
    msg_content.get('instructedCurrency') or
    msg_content.get('interbankSettlementCurrency') or
    msg_content.get('currency') or
    'USD'
)
```

---

## Extractor Implementation Checklist

For each new message type, complete these steps:

### Phase 1: Schema & Mapping
- [ ] Create Silver table DDL (`ddl/postgresql/silver/stg_XXX.sql`)
- [ ] Create YAML mapping file (`mappings/message_types/XXX.yaml`)
- [ ] Sync mappings to database (`POST /api/lineage/sync/XXX`)
- [ ] Create extension table if needed (`ddl/postgresql/gold/extension_XXX.sql`)

### Phase 2: Extractor Implementation
- [ ] Create extractor module (`src/gps_cdm/message_formats/XXX/__init__.py`)
- [ ] Implement format-specific parser class
- [ ] Implement `extract_bronze()` method
- [ ] Implement `extract_silver()` method
- [ ] Implement `get_silver_columns()` - MUST match DB exactly
- [ ] Implement `get_silver_values()` method
- [ ] Implement `extract_gold_entities()` method
- [ ] Register extractor with all aliases

### Phase 3: Testing
- [ ] Create compliant test data file
- [ ] Run E2E test via Celery
- [ ] Verify Bronze record created
- [ ] Verify Silver record created (check all columns)
- [ ] Verify Gold entities created (party, account, FI)
- [ ] Verify extension data if applicable
- [ ] Run field coverage verification script

### Phase 4: Reconciliation
- [ ] Verify Bronze→Silver coverage = 100%
- [ ] Verify Silver→Gold coverage = 100%
- [ ] Update mapping sync to fix any gaps

---

## Remaining Message Types to Implement

### ISO 20022 Family
| Type | Description | Base Pattern |
|------|-------------|--------------|
| pacs.002 | Payment Status Report | Similar to pacs.008 |
| pacs.003 | FI Direct Debit | Similar to pain.008 |
| pacs.004 | Payment Return | Similar to pacs.008 |
| pacs.009 | FI Credit Transfer | Similar to pacs.008 |
| pain.002 | Payment Status Report | Similar to pain.001 |
| pain.008 | Direct Debit Initiation | Similar to pain.001 |
| camt.052 | Account Report | Statement format |
| camt.053 | Account Statement | Statement format |
| camt.054 | Credit/Debit Notification | Statement format |

### SWIFT MT Family
| Type | Description | Base Pattern |
|------|-------------|--------------|
| MT101 | Request for Transfer | Similar to MT103 |
| MT199 | Free Format | Text-based |
| MT202 | General FI Transfer | Similar to MT103 |
| MT202COV | Cover Payment | MT202 + cover |
| MT900 | Confirmation of Debit | Notification |
| MT910 | Confirmation of Credit | Notification |
| MT940 | Customer Statement | Statement format |
| MT950 | Statement Message | Statement format |

### Regional Payment Schemes
| Type | Description | Format |
|------|-------------|--------|
| BACS | UK Batch Payments | Fixed-width |
| CHAPS | UK Real-Time | ISO 20022 |
| FPS | UK Faster Payments | ISO 20022 |
| CHIPS | US Large Value | Proprietary |
| FEDNOW | US Instant | ISO 20022 |
| NPP | Australia Instant | ISO 20022 |
| SEPA_INST | SEPA Instant | ISO 20022 |
| SEPA_SCT | SEPA Credit Transfer | ISO 20022 |
| SEPA_SDD | SEPA Direct Debit | ISO 20022 |
| RTGS | Real-Time Gross | Varies |

### Asia-Pacific & Middle East
| Type | Description | Format |
|------|-------------|--------|
| CNAPS | China Payments | Proprietary |
| BOJNET | Japan BOJ Net | Proprietary |
| KFTC | Korea Payments | Proprietary |
| MEPS+ | Singapore | ISO 20022 |
| UPI | India Unified Payments | JSON |
| RTGS_HK | Hong Kong RTGS | ISO 20022 |
| SARIE | Saudi Arabia | SWIFT-like |
| UAEFTS | UAE Payments | ISO 20022 |

### Latin America & Others
| Type | Description | Format |
|------|-------------|--------|
| PIX | Brazil Instant | JSON |
| PromptPay | Thailand | ISO 20022 |
| PayNow | Singapore | ISO 20022 |
| InstaPay | Philippines | ISO 20022 |
