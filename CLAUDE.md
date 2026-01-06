# GPS CDM Project - Claude Context

## Project Overview

GPS Common Domain Model (CDM) - A payment message processing pipeline supporting 63+ payment standards across ISO 20022, SWIFT MT, and regional payment schemes. Uses medallion architecture (Bronze → Silver → Gold) with Celery for distributed task processing and NiFi for flow orchestration.

## Architecture (v3.0 - Zone-Separated Kafka)

The architecture uses zone-separated Kafka topics with dedicated consumers for each zone.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INGESTION TIER                                 │
│  Files (SFTP/S3) → NiFi (Detect Type) → Kafka bronze.{message_type}        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ZONE-SEPARATED PROCESSING                             │
│                                                                             │
│  bronze.{type} → BronzeConsumer → Celery (process_bronze_message)          │
│       │              └─→ bronze.raw_payment_messages (store AS-IS)         │
│       └──────────────→ silver.{type} (publishes raw_ids)                   │
│                                                                             │
│  silver.{type} → SilverConsumer → Celery (process_silver_message)          │
│       │              └─→ silver.stg_{type} (parsed/transformed)            │
│       └──────────────→ gold.{type} (publishes stg_ids)                     │
│                                                                             │
│  gold.{type} → GoldConsumer → Celery (process_gold_message)                │
│                      └─→ gold.cdm_* (CDM entities + Neo4j)                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PERSISTENCE TIER                                   │
│  Bronze (raw_*) → Silver (stg_*) → Gold (cdm_*) [PostgreSQL/Databricks]    │
│  Neo4j Graph: Parties, Accounts, Financial Institutions                    │
│  Observability: batch_tracking, obs_data_lineage                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `BronzeConsumer` | Consumes from bronze.{type}, stores raw, publishes to silver.{type} | `streaming/zone_consumers.py` |
| `SilverConsumer` | Consumes from silver.{type}, parses/transforms, publishes to gold.{type} | `streaming/zone_consumers.py` |
| `GoldConsumer` | Consumes from gold.{type}, creates CDM entities + Neo4j graph | `streaming/zone_consumers.py` |
| `zone_tasks` | Celery tasks for each zone (process_bronze/silver/gold_message) | `orchestration/zone_tasks.py` |
| NiFi Flow | GetFile → Detect Type → PublishKafka (bronze.${message.type}) | NiFi UI |

### Kafka Topic Naming

- Bronze topics: `bronze.pain.001`, `bronze.MT103`, `bronze.FEDWIRE`, etc.
- Silver topics: `silver.pain.001`, `silver.MT103`, `silver.FEDWIRE`, etc.
- Gold topics: `gold.pain.001`, `gold.MT103`, `gold.FEDWIRE`, etc.
- DLQ topics: `dlq.bronze`, `dlq.silver`, `dlq.gold`

### Starting Zone Consumers

```bash
# Start all three zone consumers (each in separate terminal)
source .venv/bin/activate

# Bronze consumer
PYTHONPATH=src:$PYTHONPATH python -m gps_cdm.streaming.zone_consumers \
    --zone bronze --types pain.001,MT103,pacs.008,FEDWIRE,ACH,SEPA,RTP

# Silver consumer
PYTHONPATH=src:$PYTHONPATH python -m gps_cdm.streaming.zone_consumers \
    --zone silver --types pain.001,MT103,pacs.008,FEDWIRE,ACH,SEPA,RTP

# Gold consumer
PYTHONPATH=src:$PYTHONPATH python -m gps_cdm.streaming.zone_consumers \
    --zone gold --types pain.001,MT103,pacs.008,FEDWIRE,ACH,SEPA,RTP
```

### Performance Targets

- **PostgreSQL COPY**: ~135,000 rows/second
- **Micro-batch size**: 100 records per Celery task
- **Target throughput**: 50M+ messages/day

### Restartability

Each zone consumer maintains Kafka consumer offsets. On restart:
1. Consumer resumes from last committed offset
2. Messages redelivered and reprocessed if not committed
3. DLQ topics (`dlq.bronze`, `dlq.silver`, `dlq.gold`) capture failed messages

---

## Key Learnings

### 1. Data Source Configuration

**Issue**: Celery tasks were always trying Databricks first, causing unnecessary warnings when running locally with PostgreSQL.

**Solution**: Use `GPS_CDM_DATA_SOURCE` environment variable to control which data store to use:
- `GPS_CDM_DATA_SOURCE=postgresql` (default) - Use PostgreSQL directly, skip Databricks
- `GPS_CDM_DATA_SOURCE=databricks` - Try Databricks, fallback to PostgreSQL

**Code Location**: `src/gps_cdm/orchestration/celery_tasks.py` (lines 688-709)

### 2. NiFi Input Directory & File Permissions

**Correct Path**: `/opt/nifi/nifi-current/input/`
- GetFile processor polls every 30 seconds
- Files are deleted after reading (Keep Source File = false)

**Wrong Path**: `/opt/nifi/nifi-current/data/nifi_input/` - This was an old test directory with permission issues.

**⚠️ CRITICAL: File Permission Issue (DO NOT WASTE TIME DEBUGGING THIS AGAIN)**

When copying files to NiFi input via `docker cp`, files get permissions `-rw-------` (600) owned by host user (uid 501). NiFi runs as user `nifi` (uid 1000) and **CANNOT READ THESE FILES**.

**ALWAYS use this command pattern when copying files to NiFi:**
```bash
# Best approach: Use tar to copy with correct permissions
# 1. Create temp dir and copy files with world-readable permissions
mkdir -p /tmp/nifi_input_test
cp myfile.xml /tmp/nifi_input_test/
chmod 644 /tmp/nifi_input_test/*

# 2. Use tar to copy - this preserves permissions AND sets nifi as owner
cd /tmp/nifi_input_test && tar cf - . | docker exec -i gps-cdm-nifi tar xf - -C /opt/nifi/nifi-current/input/

# Note: Ignore tar warnings about "Cannot utime" or "Cannot change mode" - files still copy correctly
# Clean up macOS metadata files if present
docker exec gps-cdm-nifi bash -c 'rm -f /opt/nifi/nifi-current/input/._*' 2>/dev/null || true
```

**Why `docker cp` + `chmod` doesn't work:**
- Files copied via `docker cp` are owned by host uid (501), not nifi (1000)
- NiFi container runs as non-root and cannot chmod files it doesn't own
- Only tar method works because it creates files as the nifi user

**Symptoms of this issue:**
- Files remain in input directory (not picked up by GetFile)
- NiFi GetFile processor shows RUNNING but no files processed
- `ls -la` shows files with `-rw-------` permissions

**DO NOT:**
- Spend time checking processor states
- Investigate NiFi flow configuration
- Check polling intervals
- Debug Kafka/Celery connectivity

**INSTEAD:** First check file permissions with `ls -la` and fix with `chmod 644`.

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

## NiFi Flow Structure (Zone-Separated)

```
GPS CDM Payment Pipeline/
├── Message Type Detection/
│   ├── Read Test Messages (GetFile) - /opt/nifi/nifi-current/input/
│   ├── Detect Message Type from Filename (UpdateAttribute)
│   │       Sets ${message.type} from filename pattern: {type}_{id}.{ext}
│   └── Output Ports: To Kafka Publishing
├── Kafka Publishing/
│   ├── Publish to Per-Type Kafka Topics (PublishKafka)
│   │       Topic: bronze.${message.type}
│   │       Bootstrap: kafka:29092
│   └── Log Kafka Failures (LogAttribute)
└── Error Handling/
    ├── Log Error (LogAttribute)
    └── Write to DLQ (PutFile)
```

**Critical NiFi Configuration:**
- PublishKafka topic pattern: `bronze.${message.type}` (NOT `gps-cdm-${message.type}`)
- Bootstrap servers: `kafka:29092` (container internal DNS)
- Message type extracted from filename: `pain.001_test.xml` → `message.type=pain.001`

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

### Kafka/Zone Consumer Issues
1. Check Kafka topics have messages: `docker exec gps-cdm-kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic bronze.pain.001 --from-beginning --timeout-ms 3000`
2. Check zone consumer logs: `tail -f /tmp/zone_consumer_bronze.log`
3. Check NiFi logs: `docker logs gps-cdm-nifi --tail 50`
4. Verify NiFi PublishKafka topic: Should be `bronze.${message.type}`

### Celery Tasks Not Received
1. Verify worker is listening on correct queues: `-Q celery,bronze,silver,gold,dq,cdc`
2. Check Redis connection: `redis-cli ping`
3. Check queue depths: `redis-cli LLEN celery`

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

NiFi extracts message type from filename using **hyphen (`-`) as delimiter**:
- `pain.001-test.json` → message_type = `pain.001`
- `pacs.008-12345.json` → message_type = `pacs.008`
- `MT103-abc.txt` → message_type = `MT103`
- `FEDWIRE-001.txt` → message_type = `FEDWIRE`
- `MEPS_PLUS-test.json` → message_type = `MEPS_PLUS` (underscores in type name preserved)
- `RTGS_HK-test.json` → message_type = `RTGS_HK`

Pattern: `{message_type}-{identifier}.{extension}`

**NiFi Expression**: `${filename:substringBefore('-')}`

**E2E Test Files**: Located in `test_data/e2e/` with naming pattern `{MESSAGE_TYPE}-e2e-test.{ext}`

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

---

## Database-Driven Gold Processing

### Overview

Gold processing uses `DynamicGoldMapper` which reads from `mapping.gold_field_mappings` to determine how to map Silver columns to ALL Gold tables. This is NOT hardcoded in extractors.

**Key Files:**
- `src/gps_cdm/orchestration/dynamic_gold_mapper.py` - Reads mappings from DB and builds Gold records
- `src/gps_cdm/orchestration/zone_tasks.py` - `process_gold_records` task uses DynamicGoldMapper

### Gold Tables and Entity Roles

| Gold Table | Entity Roles | Description |
|------------|-------------|-------------|
| `cdm_payment_instruction` | NULL | Main payment record (1 per message) |
| `cdm_party` | DEBTOR, CREDITOR, INITIATING_PARTY, ULTIMATE_DEBTOR, ULTIMATE_CREDITOR | Party records (multiple per message) |
| `cdm_account` | DEBTOR, CREDITOR | Account records (multiple per message) |
| `cdm_financial_institution` | DEBTOR_AGENT, CREDITOR_AGENT, INTERMEDIARY_AGENT1, INTERMEDIARY_AGENT2 | Bank/FI records |
| `cdm_payment_extension_*` | NULL | Format-specific extension data |

### Gold Mapping Source Expressions

| Expression Type | Example | Description |
|----------------|---------|-------------|
| Silver column | `debtor_name` | Direct Silver column reference |
| Literal string | `'pain.001'` | Quoted literal value |
| Generated UUID | `_GENERATED_UUID` | Auto-generate UUID |
| Context variable | `_CONTEXT.stg_id` | Use context (stg_id, batch_id, now) |
| NULL | `NULL` or empty | Explicit NULL value |

### Gold Mapping Transforms

| Transform | Description | Example Use Case |
|-----------|-------------|-----------------|
| `UPPER` | Convert to uppercase | BIC codes |
| `LOWER` | Convert to lowercase | Email addresses |
| `TRIM` | Strip whitespace | Names |
| `COALESCE:default` | Use default if NULL | `COALESCE:USD` |
| `COALESCE_IBAN` | Fall back to IBAN if account_number NULL | Account identifiers |
| `COALESCE_BIC` | Derive institution name from BIC | FI names |
| `TO_ARRAY` | Wrap single value in array | PostgreSQL array columns |
| `TO_DECIMAL` | Convert to decimal | Amount fields |
| `TO_DATE` | Parse ISO date string | Date fields |

### Common Gold Mapping Issues

1. **Empty string vs NULL entity_role**: Mappings without entity_role MUST have `entity_role = NULL`, not empty string `''`. The grouping logic uses `(table, role)` as key.

2. **NOT NULL columns need mappings**: Check `information_schema.columns` for NOT NULL columns and ensure mappings exist with defaults.

3. **Array columns**: Columns like `remittance_unstructured` need `TO_ARRAY` transform.

4. **Derived fields**: Use `COALESCE_*` transforms to derive values from related fields when primary source is NULL.

---

## Field Coverage Reconciliation Script

### Running the Recon Script

The recon script validates field coverage from Standard → Silver → Gold:

```bash
# Full reconciliation for pain.001
GPS_CDM_DATA_SOURCE=postgresql \
POSTGRES_HOST=localhost \
POSTGRES_PORT=5433 \
POSTGRES_DB=gps_cdm \
POSTGRES_USER=gps_cdm_svc \
POSTGRES_PASSWORD=gps_cdm_password \
PYTHONPATH=src:$PYTHONPATH \
.venv/bin/python scripts/reporting/recon_message_format.py pain.001

# Output options:
#   --output-format psv  (pipe-separated values)
#   --output-format json
#   --output-format text (default)
```

### What the Script Checks

1. **Standard → Silver Coverage**: How many standard fields (leaf nodes only) have Silver mappings
2. **Silver → Gold Coverage**: How many Silver columns have Gold mappings
3. **Mandatory Field Coverage**: Verifies all required fields are mapped
4. **Unmapped Fields**: Lists fields that exist in standard but aren't mapped

### Expected Output

```
=== MESSAGE FORMAT RECONCILIATION: pain.001 ===

STANDARD TO SILVER COVERAGE
Total standard fields: 118 (leaf nodes only)
Fields mapped to Silver: 88
Coverage: 74.6%
Mandatory fields covered: 100.0%

SILVER TO GOLD COVERAGE
Total Silver columns: 118
Columns mapped to Gold: 132 mappings
All critical fields mapped: YES

UNMAPPED STANDARD FIELDS (30)
- CtgyPurp/Cd (OPTIONAL)
- ChqInstr/ChqTp (OPTIONAL)
...
```

### Adding New Format to Recon

1. Add format's standard fields to `mapping.standard_fields` table
2. Add Silver field mappings to `mapping.silver_field_mappings`
3. Add Gold field mappings to `mapping.gold_field_mappings`
4. Run recon script to validate coverage

---

## Field Coverage Analysis & Resolution

This section documents the methodology for achieving 100% field coverage across Standard → Silver → Gold layers.

### Coverage Analysis Queries

#### Standard → Silver Coverage

This query measures how many standard data fields (excluding complex/element types) are mapped to Silver columns:

```sql
WITH standard_data_elements AS (
    SELECT format_id, COUNT(*) as std_elements
    FROM mapping.standard_fields
    WHERE is_active = true AND LOWER(data_type) NOT IN ('complex', 'element')
    GROUP BY format_id
),
silver_mapped AS (
    SELECT sde.format_id, COUNT(DISTINCT sde.standard_field_id) as mapped
    FROM (
        SELECT format_id, standard_field_id, field_path
        FROM mapping.standard_fields
        WHERE is_active = true AND LOWER(data_type) NOT IN ('complex', 'element')
    ) sde
    INNER JOIN mapping.silver_field_mappings sm
        ON sde.format_id = sm.format_id
        AND sde.field_path = sm.source_path
    WHERE sm.is_active = true
    GROUP BY sde.format_id
)
SELECT
    sde.format_id,
    sde.std_elements as total,
    COALESCE(sm.mapped, 0) as mapped,
    ROUND(100.0 * COALESCE(sm.mapped, 0) / sde.std_elements, 1) as pct
FROM standard_data_elements sde
LEFT JOIN silver_mapped sm ON sde.format_id = sm.format_id
ORDER BY pct DESC, format_id;
```

**Key Points:**
- Excludes `complex` and `element` data types (non-data-holding nodes)
- Join condition: `field_path = source_path` (exact match required for traceability)

#### Silver → Gold Coverage

This query measures how many Silver columns are mapped to Gold tables:

```sql
WITH silver_cols AS (
    SELECT DISTINCT format_id, target_column
    FROM mapping.silver_field_mappings
    WHERE is_active = true
),
gold_sources AS (
    SELECT DISTINCT format_id, source_expression as silver_col
    FROM mapping.gold_field_mappings
    WHERE is_active = true
      AND source_expression IS NOT NULL
      AND source_expression <> ''
      AND source_expression NOT LIKE '%GENERATED%'
      AND source_expression NOT LIKE '%CONTEXT%'
      AND source_expression NOT LIKE '''%'
),
silver_to_gold AS (
    SELECT
        sc.format_id,
        COUNT(DISTINCT sc.target_column) as silver_cols,
        COUNT(DISTINCT gs.silver_col) as gold_mapped
    FROM silver_cols sc
    LEFT JOIN gold_sources gs ON sc.format_id = gs.format_id AND sc.target_column = gs.silver_col
    GROUP BY sc.format_id
)
SELECT
    format_id,
    silver_cols as total,
    gold_mapped as mapped,
    ROUND(100.0 * gold_mapped / silver_cols, 1) as pct
FROM silver_to_gold
ORDER BY pct DESC, format_id;
```

**Key Points:**
- Excludes generated UUIDs, context variables, and literal values
- Join condition: `target_column = source_expression`

#### Comprehensive Coverage Report (Both Layers)

```sql
WITH standard_data_elements AS (
    SELECT format_id, COUNT(*) as std_elements
    FROM mapping.standard_fields
    WHERE is_active = true AND LOWER(data_type) NOT IN ('complex', 'element')
    GROUP BY format_id
),
silver_mapped AS (
    SELECT sde.format_id, COUNT(DISTINCT sde.standard_field_id) as mapped
    FROM (
        SELECT format_id, standard_field_id, field_path
        FROM mapping.standard_fields
        WHERE is_active = true AND LOWER(data_type) NOT IN ('complex', 'element')
    ) sde
    INNER JOIN mapping.silver_field_mappings sm
        ON sde.format_id = sm.format_id AND sde.field_path = sm.source_path
    WHERE sm.is_active = true
    GROUP BY sde.format_id
),
silver_cols AS (
    SELECT DISTINCT format_id, target_column FROM mapping.silver_field_mappings WHERE is_active = true
),
gold_sources AS (
    SELECT DISTINCT format_id, source_expression as silver_col
    FROM mapping.gold_field_mappings
    WHERE is_active = true AND source_expression IS NOT NULL AND source_expression <> ''
      AND source_expression NOT LIKE '%GENERATED%' AND source_expression NOT LIKE '%CONTEXT%'
      AND source_expression NOT LIKE '''%'
),
silver_to_gold AS (
    SELECT sc.format_id, COUNT(DISTINCT sc.target_column) as silver_cols,
           COUNT(DISTINCT gs.silver_col) as gold_mapped
    FROM silver_cols sc
    LEFT JOIN gold_sources gs ON sc.format_id = gs.format_id AND sc.target_column = gs.silver_col
    GROUP BY sc.format_id
)
SELECT
    sde.format_id AS format,
    sde.std_elements AS std_fields,
    COALESCE(sm.mapped, 0) AS silver_mapped,
    ROUND(100.0 * COALESCE(sm.mapped, 0) / sde.std_elements, 0) AS std_silver_pct,
    COALESCE(sg.silver_cols, 0) AS silver_cols,
    COALESCE(sg.gold_mapped, 0) AS gold_mapped,
    ROUND(100.0 * COALESCE(sg.gold_mapped, 0) / NULLIF(sg.silver_cols, 0), 0) AS silver_gold_pct
FROM standard_data_elements sde
LEFT JOIN silver_mapped sm ON sde.format_id = sm.format_id
LEFT JOIN silver_to_gold sg ON sde.format_id = sg.format_id
ORDER BY sde.format_id;
```

### Resolving Standard → Silver Coverage Gaps

#### Step 1: Find Unmapped Standard Fields

```sql
SELECT sf.field_path, sf.field_name, sf.is_mandatory
FROM mapping.standard_fields sf
LEFT JOIN mapping.silver_field_mappings sm
    ON sf.format_id = sm.format_id AND sf.field_path = sm.source_path AND sm.is_active = true
WHERE sf.format_id = '{FORMAT_ID}'
  AND sf.is_active = true
  AND LOWER(sf.data_type) NOT IN ('complex', 'element')
  AND sm.source_path IS NULL
ORDER BY sf.field_path;
```

#### Step 2: Add Missing Silver Mappings

**Critical Rule**: `source_path` MUST match `field_path` from `standard_fields` exactly for traceability.

```sql
INSERT INTO mapping.silver_field_mappings
    (format_id, standard_field_id, target_column, source_path, parser_path, is_required, is_active)
SELECT
    sf.format_id,
    sf.standard_field_id,
    '{silver_column_name}' as target_column,
    sf.field_path as source_path,  -- MUST match field_path exactly!
    '{parser_output_key}' as parser_path,
    sf.is_mandatory as is_required,
    true as is_active
FROM mapping.standard_fields sf
WHERE sf.format_id = '{FORMAT_ID}'
  AND sf.field_path = '{field_path}'
ON CONFLICT (format_id, target_column)
DO UPDATE SET source_path = EXCLUDED.source_path, is_active = true;
```

#### Step 3: Add Missing Silver Table Columns (if needed)

```sql
ALTER TABLE silver.stg_{format_id} ADD COLUMN IF NOT EXISTS {column_name} {data_type};
```

### Resolving Silver → Gold Coverage Gaps

#### Step 1: Find Unmapped Silver Columns

```sql
WITH silver_cols AS (
    SELECT DISTINCT target_column FROM mapping.silver_field_mappings
    WHERE format_id = '{FORMAT_ID}' AND is_active = true
),
gold_sources AS (
    SELECT DISTINCT source_expression FROM mapping.gold_field_mappings
    WHERE format_id = '{FORMAT_ID}' AND is_active = true
      AND source_expression IS NOT NULL AND source_expression <> ''
      AND source_expression NOT LIKE '%GENERATED%' AND source_expression NOT LIKE '%CONTEXT%'
      AND source_expression NOT LIKE '''%'
)
SELECT sc.target_column
FROM silver_cols sc
LEFT JOIN gold_sources gs ON sc.target_column = gs.source_expression
WHERE gs.source_expression IS NULL
ORDER BY sc.target_column;
```

#### Step 2: Add Missing Gold Mappings

Gold mappings go to either core CDM tables or format-specific extension tables:

**For Core CDM Tables** (cdm_payment_instruction, cdm_party, cdm_account, cdm_financial_institution):
```sql
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, is_active)
VALUES
    ('{FORMAT_ID}', 'cdm_payment_instruction', '{gold_column}', '{silver_column}', NULL, true);
```

**For Extension Tables** (format-specific fields):
```sql
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, is_active)
VALUES
    ('{FORMAT_ID}', 'cdm_payment_extension_{format}', '{column_name}', '{silver_column}', NULL, true);
```

#### Step 3: Add Missing Extension Table Columns (if needed)

```sql
ALTER TABLE gold.cdm_payment_extension_{format} ADD COLUMN IF NOT EXISTS {column_name} {data_type};
```

### Key Rules for Field Mappings

1. **No Fallback Values**: If source data doesn't have a value, allow NULL. Don't create synthetic defaults.

2. **Traceability Chain**:
   - `standard_fields.field_path` → `silver_field_mappings.source_path` (exact match)
   - `silver_field_mappings.target_column` → `gold_field_mappings.source_expression` (exact match)

3. **Exclude Non-Data Types**: Always filter `WHERE LOWER(data_type) NOT IN ('complex', 'element')` when counting standard fields.

4. **source_path vs parser_path**:
   - `source_path`: Standard field path for lineage tracking (must match `field_path`)
   - `parser_path`: Actual key in parser output (may differ from standard path)

5. **Gold source_expression Exclusions**: When counting coverage, exclude:
   - `_GENERATED_UUID` (auto-generated)
   - `_CONTEXT.*` (context variables)
   - Literal values (quoted strings like `'pain.001'`)

### Common Issues & Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| 0% Standard→Silver coverage | Join finds no matches | Ensure `source_path = field_path` exactly |
| Missing columns in Silver | INSERT fails | Add column with ALTER TABLE |
| 0% Silver→Gold coverage | Join finds no matches | Ensure `source_expression` has no prefix (not `silver.column`) |
| Extension table missing | INSERT fails | Create extension table DDL |
| Duplicate mappings | Inflated counts | Use DISTINCT in queries, upsert with ON CONFLICT |

### Coverage Summary (29 Formats - All at 100%)

| Format | Std Fields | Std→Silver | Silver Cols | Silver→Gold |
|--------|------------|------------|-------------|-------------|
| pain.001 | 118 | 100% | 126 | 100% |
| pacs.008 | 150 | 100% | 158 | 100% |
| MT103 | 28 | 100% | 74 | 100% |
| MT202 | 44 | 100% | 55 | 100% |
| MT940 | 50 | 100% | 54 | 100% |
| camt.053 | 211 | 100% | 218 | 100% |
| ACH | 84 | 100% | 84 | 100% |
| FEDWIRE | 139 | 100% | 139 | 100% |
| CHIPS | 75 | 100% | 75 | 100% |
| SEPA | 99 | 100% | 102 | 100% |
| CHAPS | 135 | 100% | 144 | 100% |
| FPS | 100 | 100% | 112 | 100% |
| BACS | 35 | 100% | 35 | 100% |
| RTP | 66 | 100% | 66 | 100% |
| FEDNOW | 112 | 100% | 112 | 100% |
| TARGET2 | 124 | 100% | 124 | 100% |
| NPP | 99 | 100% | 119 | 100% |
| PIX | 84 | 100% | 88 | 100% |
| UPI | 84 | 100% | 88 | 100% |
| CNAPS | 42 | 100% | 51 | 100% |
| BOJNET | 52 | 100% | 57 | 100% |
| KFTC | 82 | 100% | 85 | 100% |
| MEPS_PLUS | 128 | 100% | 132 | 100% |
| RTGS_HK | 105 | 100% | 108 | 100% |
| SARIE | 120 | 100% | 124 | 100% |
| UAEFTS | 105 | 100% | 108 | 100% |
| PROMPTPAY | 63 | 100% | 63 | 100% |
| PAYNOW | 61 | 100% | 75 | 100% |
| INSTAPAY | 88 | 100% | 92 | 100% |

**Total**: 2,674 standard fields across 29 formats with complete traceability.

---

## E2E Testing Guide for All 29 Message Formats

This section documents the complete E2E testing procedure for validating the NiFi → Kafka → Zone Consumer → Celery → PostgreSQL pipeline across all 29 supported message formats.

### Overview

E2E testing validates:
1. **Bronze Layer**: Raw message storage (AS-IS)
2. **Silver Layer**: Parsed/transformed structured data
3. **Gold Layer**: CDM entities (payment instructions, parties, accounts, FIs)

### Supported Message Formats by Category

| Category | Formats | Parser Type |
|----------|---------|-------------|
| **ISO 20022 XML** | pain.001, pacs.008, camt.053, SEPA, CHAPS, FPS, FEDNOW, TARGET2, NPP, MEPS_PLUS, RTGS_HK, UAEFTS, INSTAPAY | XML namespace-aware |
| **SWIFT MT** | MT103, MT202, MT940 | Block format `{1:...}{4:...}` |
| **Fixed-Width** | ACH (94 chars), BACS, KFTC, BOJNET, CNAPS, CHIPS | Positional parsing |
| **Tag-Value** | FEDWIRE `{NNNN}value`, SARIE | Tag extraction |
| **JSON** | PIX, UPI, PROMPTPAY, PAYNOW | JSON parsing |

### Prerequisites

#### 1. Start Docker Containers

```bash
docker-compose -f docker-compose.nifi.yaml up -d
```

Verify all containers are running:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Expected containers:
- `gps-cdm-nifi` - Apache NiFi (port 8080)
- `gps-cdm-kafka` - Kafka broker (port 9092)
- `gps-cdm-postgres` - PostgreSQL (port 5433)
- `gps-cdm-redis` - Redis (port 6379)
- `gps-cdm-neo4j` - Neo4j (ports 7474, 7687)

#### 2. Start Celery Worker

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

#### 3. Start Zone Consumers

In separate terminals, start consumers for each zone:

```bash
# Terminal 1 - Bronze Consumer (all 29 formats)
source .venv/bin/activate
PYTHONPATH=src:$PYTHONPATH python -m gps_cdm.streaming.zone_consumers \
    --zone bronze \
    --types pain.001,pacs.008,MT103,MT202,MT940,camt.053,ACH,FEDWIRE,SEPA,RTP,CHAPS,FPS,BACS,CHIPS,FEDNOW,TARGET2,NPP,PIX,UPI,CNAPS,BOJNET,KFTC,MEPS_PLUS,RTGS_HK,SARIE,UAEFTS,PROMPTPAY,PAYNOW,INSTAPAY

# Terminal 2 - Silver Consumer
PYTHONPATH=src:$PYTHONPATH python -m gps_cdm.streaming.zone_consumers \
    --zone silver \
    --types pain.001,pacs.008,MT103,MT202,MT940,camt.053,ACH,FEDWIRE,SEPA,RTP,CHAPS,FPS,BACS,CHIPS,FEDNOW,TARGET2,NPP,PIX,UPI,CNAPS,BOJNET,KFTC,MEPS_PLUS,RTGS_HK,SARIE,UAEFTS,PROMPTPAY,PAYNOW,INSTAPAY

# Terminal 3 - Gold Consumer
PYTHONPATH=src:$PYTHONPATH python -m gps_cdm.streaming.zone_consumers \
    --zone gold \
    --types pain.001,pacs.008,MT103,MT202,MT940,camt.053,ACH,FEDWIRE,SEPA,RTP,CHAPS,FPS,BACS,CHIPS,FEDNOW,TARGET2,NPP,PIX,UPI,CNAPS,BOJNET,KFTC,MEPS_PLUS,RTGS_HK,SARIE,UAEFTS,PROMPTPAY,PAYNOW,INSTAPAY
```

---

### Test File Templates by Format

#### ISO 20022 XML Formats (pain.001, pacs.008, SEPA, CHAPS, FPS, etc.)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>MSG-{UNIQUE_ID}</MsgId>
      <CreDtTm>2025-01-05T10:00:00</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>1000.00</CtrlSum>
      <InitgPty><Nm>Test Initiator</Nm></InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>PMT-001</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>1000.00</CtrlSum>
      <ReqdExctnDt>2025-01-06</ReqdExctnDt>
      <Dbtr><Nm>Test Debtor</Nm></Dbtr>
      <DbtrAcct><Id><IBAN>DE89370400440532013000</IBAN></Id></DbtrAcct>
      <DbtrAgt><FinInstnId><BIC>COBADEFFXXX</BIC></FinInstnId></DbtrAgt>
      <CdtTrfTxInf>
        <PmtId><EndToEndId>E2E-{UNIQUE_ID}</EndToEndId></PmtId>
        <Amt><InstdAmt Ccy="EUR">1000.00</InstdAmt></Amt>
        <CdtrAgt><FinInstnId><BIC>DEUTDEFFXXX</BIC></FinInstnId></CdtrAgt>
        <Cdtr><Nm>Test Creditor</Nm></Cdtr>
        <CdtrAcct><Id><IBAN>DE02120300000000202051</IBAN></Id></CdtrAcct>
        <RmtInf><Ustrd>Test Payment</Ustrd></RmtInf>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>
```

**File naming**: `pain.001-test-{ID}.xml`, `pacs.008-test-{ID}.xml`, `SEPA-test-{ID}.xml`

#### SWIFT MT Formats (MT103, MT202, MT940)

```
{1:F01BANKBEBBAXXX0000000000}{2:O1031200210102BANKDEFFAXXX00000000002101021200N}{4:
:20:REF-{UNIQUE_ID}
:23B:CRED
:32A:250105EUR1000,00
:50K:/DE89370400440532013000
TEST DEBTOR
:52A:COBADEFFXXX
:53A:DEUTDEFFXXX
:57A:CHASGB2LXXX
:59:/GB82WEST12345698765432
TEST CREDITOR
:70:TEST PAYMENT
:71A:SHA
-}
```

**File naming**: `MT103-test-{ID}.txt`, `MT202-test-{ID}.txt`, `MT940-test-{ID}.txt`

#### ACH/NACHA Format (Fixed-Width 94 Characters)

Each line MUST be exactly 94 characters (pad with spaces):

```
101 091000019 1234567892501051234A094101FIRST NATIONAL BANK    ACME CORPORATION       REF{ID}
5200ACME CORP       PAYROLL VALIDATION  1234567890PPDPAYROLL   250105250105   1091000010000001
62209100001923456789012345   0000100000EMPID001       JOHN DOE EMPLOYEE       0091000010000001
820000000100091000010000000000000000001000001234567890                         091000010000001
9000001000001000000010009100001000000000000000000100000
```

**File naming**: `ACH-test-{ID}.ach`

#### FEDWIRE Format (Tag-Value)

```
{1500}30
{1510}1000
{1520}00
{2000}250105MMQFMP9T00000001
{3100}021000089CITIBANK NA
{3320}REF-{UNIQUE_ID}
{3400}021000021JPMORGAN CHASE
{3600}BNF ACCT 123456789
{4200}D12345678901
{5000}ORIGINATOR NAME
{6000}BENEFICIARY NAME
{6100}123 BENEFICIARY STREET
```

**File naming**: `FEDWIRE-test-{ID}.txt`

#### JSON Formats (PIX, UPI, PROMPTPAY, PAYNOW)

```json
{
  "transactionId": "TX-{UNIQUE_ID}",
  "creationDate": "2025-01-05T10:00:00Z",
  "amount": 1000.00,
  "currency": "BRL",
  "debtor": {
    "name": "Test Debtor",
    "taxId": "12345678901",
    "account": {
      "number": "123456789",
      "branch": "0001",
      "bankCode": "001"
    }
  },
  "creditor": {
    "name": "Test Creditor",
    "pixKey": "creditor@email.com",
    "account": {
      "number": "987654321",
      "branch": "0002",
      "bankCode": "341"
    }
  },
  "description": "Test PIX Payment"
}
```

**File naming**: `PIX-test-{ID}.json`, `UPI-test-{ID}.json`

#### Fixed-Width Regional Formats (BACS, KFTC, BOJNET, CNAPS, CHIPS)

**BACS** (UK, variable record types):
```
VOL1BACS
HDR1ABACS      TEST01
UHL1 12345600250105000000
1234560012345678TEST DEBTOR               00001000REF001
EOF1
```

**KFTC** (Korea, 300 chars):
```
H{DATE}001KFTCTEST         {300 chars total padded}
D001...{transaction details}
T001...{trailer}
```

**File naming**: `BACS-test-{ID}.txt`, `KFTC-test-{ID}.txt`, etc.

---

### E2E Test Execution Steps

#### Step 1: Create Test Files

Create a local staging directory:
```bash
mkdir -p /tmp/nifi_input_test
```

Create test files for each format (examples above).

#### Step 2: Copy Files to NiFi

**⚠️ CRITICAL: Use tar method for correct permissions**

```bash
# Set permissions locally
chmod 644 /tmp/nifi_input_test/*

# Copy using tar (preserves permissions, sets nifi ownership)
cd /tmp/nifi_input_test && tar cf - . | docker exec -i gps-cdm-nifi tar xf - -C /opt/nifi/nifi-current/input/

# Clean up macOS metadata files
docker exec gps-cdm-nifi bash -c 'rm -f /opt/nifi/nifi-current/input/._*' 2>/dev/null || true

# Verify files are readable
docker exec gps-cdm-nifi ls -la /opt/nifi/nifi-current/input/
```

#### Step 3: Wait for Processing

NiFi GetFile polls every 30 seconds. Wait for files to be picked up:

```bash
# Watch for files to disappear (indicates NiFi processed them)
watch -n 5 "docker exec gps-cdm-nifi ls -la /opt/nifi/nifi-current/input/ 2>/dev/null | grep -v '^total'"

# Monitor Celery for task execution
tail -f /tmp/celery_gps_cdm.log | grep -E "process_bronze|process_silver|process_gold|ERROR"
```

#### Step 4: Verify Database Records

**Bronze Layer Verification:**
```sql
-- Check Bronze records by format
SELECT message_type, COUNT(*) as cnt, MAX(_ingested_at) as latest
FROM bronze.raw_payment_messages
GROUP BY message_type
ORDER BY message_type;

-- View recent Bronze records
SELECT raw_id, message_type, processing_status, _ingested_at::timestamp(0)
FROM bronze.raw_payment_messages
ORDER BY _ingested_at DESC LIMIT 20;
```

**Silver Layer Verification:**
```sql
-- Check Silver records by format
SELECT 'pain.001' as fmt, COUNT(*) FROM silver.stg_pain001
UNION ALL SELECT 'pacs.008', COUNT(*) FROM silver.stg_pacs008
UNION ALL SELECT 'MT103', COUNT(*) FROM silver.stg_mt103
UNION ALL SELECT 'MT202', COUNT(*) FROM silver.stg_mt202
UNION ALL SELECT 'MT940', COUNT(*) FROM silver.stg_mt940
UNION ALL SELECT 'camt.053', COUNT(*) FROM silver.stg_camt053
UNION ALL SELECT 'ACH', COUNT(*) FROM silver.stg_ach
UNION ALL SELECT 'FEDWIRE', COUNT(*) FROM silver.stg_fedwire
UNION ALL SELECT 'SEPA', COUNT(*) FROM silver.stg_sepa
UNION ALL SELECT 'RTP', COUNT(*) FROM silver.stg_rtp
UNION ALL SELECT 'CHAPS', COUNT(*) FROM silver.stg_chaps
UNION ALL SELECT 'FPS', COUNT(*) FROM silver.stg_fps
UNION ALL SELECT 'BACS', COUNT(*) FROM silver.stg_bacs
UNION ALL SELECT 'CHIPS', COUNT(*) FROM silver.stg_chips
UNION ALL SELECT 'FEDNOW', COUNT(*) FROM silver.stg_fednow
UNION ALL SELECT 'TARGET2', COUNT(*) FROM silver.stg_target2
UNION ALL SELECT 'NPP', COUNT(*) FROM silver.stg_npp
UNION ALL SELECT 'PIX', COUNT(*) FROM silver.stg_pix
UNION ALL SELECT 'UPI', COUNT(*) FROM silver.stg_upi
UNION ALL SELECT 'CNAPS', COUNT(*) FROM silver.stg_cnaps
UNION ALL SELECT 'BOJNET', COUNT(*) FROM silver.stg_bojnet
UNION ALL SELECT 'KFTC', COUNT(*) FROM silver.stg_kftc
UNION ALL SELECT 'MEPS_PLUS', COUNT(*) FROM silver.stg_meps_plus
UNION ALL SELECT 'RTGS_HK', COUNT(*) FROM silver.stg_rtgs_hk
UNION ALL SELECT 'SARIE', COUNT(*) FROM silver.stg_sarie
UNION ALL SELECT 'UAEFTS', COUNT(*) FROM silver.stg_uaefts
UNION ALL SELECT 'PROMPTPAY', COUNT(*) FROM silver.stg_promptpay
UNION ALL SELECT 'PAYNOW', COUNT(*) FROM silver.stg_paynow
UNION ALL SELECT 'INSTAPAY', COUNT(*) FROM silver.stg_instapay
ORDER BY fmt;
```

**Gold Layer Verification:**
```sql
-- CDM Payment Instructions by format
SELECT source_message_type, COUNT(*) as cnt
FROM gold.cdm_payment_instruction
GROUP BY source_message_type
ORDER BY source_message_type;

-- CDM Parties
SELECT p.source_message_type, p.role, COUNT(*)
FROM gold.cdm_party p
GROUP BY p.source_message_type, p.role
ORDER BY source_message_type, role;

-- CDM Accounts
SELECT source_message_type, role, COUNT(*)
FROM gold.cdm_account
GROUP BY source_message_type, role
ORDER BY source_message_type, role;

-- CDM Financial Institutions
SELECT source_message_type, role, COUNT(*)
FROM gold.cdm_financial_institution
GROUP BY source_message_type, role
ORDER BY source_message_type, role;
```

---

### Single-Command E2E Test Script

```bash
#!/bin/bash
# run_e2e_test.sh - E2E test for a single message format

FORMAT=$1
FILE=$2

if [ -z "$FORMAT" ] || [ -z "$FILE" ]; then
    echo "Usage: $0 <FORMAT> <FILE_PATH>"
    echo "Example: $0 pain.001 /tmp/nifi_input_test/pain.001_test.xml"
    exit 1
fi

echo "=== E2E Test: $FORMAT ==="

# Step 1: Copy file to NiFi
echo "1. Copying file to NiFi..."
cp "$FILE" /tmp/nifi_input_test/
chmod 644 /tmp/nifi_input_test/*
cd /tmp/nifi_input_test && tar cf - "$(basename $FILE)" | docker exec -i gps-cdm-nifi tar xf - -C /opt/nifi/nifi-current/input/
docker exec gps-cdm-nifi bash -c 'rm -f /opt/nifi/nifi-current/input/._*' 2>/dev/null

# Step 2: Wait for processing
echo "2. Waiting for NiFi to pick up file (35 seconds)..."
sleep 35

# Step 3: Verify Bronze
echo "3. Checking Bronze layer..."
docker exec gps-cdm-postgres psql -U gps_cdm_svc -d gps_cdm -c \
    "SELECT raw_id, message_type, processing_status FROM bronze.raw_payment_messages WHERE message_type = '$FORMAT' ORDER BY _ingested_at DESC LIMIT 3;"

# Step 4: Verify Silver
echo "4. Checking Silver layer..."
SILVER_TABLE=$(echo "$FORMAT" | tr '.' '_' | tr '[:upper:]' '[:lower:]')
docker exec gps-cdm-postgres psql -U gps_cdm_svc -d gps_cdm -c \
    "SELECT stg_id, processing_status FROM silver.stg_${SILVER_TABLE} ORDER BY stg_id DESC LIMIT 3;" 2>/dev/null || echo "Silver table check skipped"

# Step 5: Verify Gold
echo "5. Checking Gold layer..."
docker exec gps-cdm-postgres psql -U gps_cdm_svc -d gps_cdm -c \
    "SELECT instruction_id, source_message_type FROM gold.cdm_payment_instruction WHERE source_message_type = '$FORMAT' ORDER BY created_at DESC LIMIT 3;"

echo "=== E2E Test Complete ==="
```

---

### Batch E2E Test for All 29 Formats

```bash
#!/bin/bash
# run_all_formats_e2e.sh - Test all 29 message formats

FORMATS=(
    "pain.001" "pacs.008" "MT103" "MT202" "MT940" "camt.053"
    "ACH" "FEDWIRE" "SEPA" "RTP" "CHAPS" "FPS" "BACS" "CHIPS"
    "FEDNOW" "TARGET2" "NPP" "PIX" "UPI" "CNAPS" "BOJNET" "KFTC"
    "MEPS_PLUS" "RTGS_HK" "SARIE" "UAEFTS" "PROMPTPAY" "PAYNOW" "INSTAPAY"
)

echo "=== E2E Testing All 29 Formats ==="
echo ""

# Prepare test files (assumes test files exist in /tmp/nifi_input_test/)
chmod 644 /tmp/nifi_input_test/*
cd /tmp/nifi_input_test && tar cf - . | docker exec -i gps-cdm-nifi tar xf - -C /opt/nifi/nifi-current/input/
docker exec gps-cdm-nifi bash -c 'rm -f /opt/nifi/nifi-current/input/._*'

echo "Files copied to NiFi. Waiting 60 seconds for processing..."
sleep 60

# Check results
echo ""
echo "=== RESULTS ==="
for fmt in "${FORMATS[@]}"; do
    BRONZE=$(docker exec gps-cdm-postgres psql -U gps_cdm_svc -d gps_cdm -t -c \
        "SELECT COUNT(*) FROM bronze.raw_payment_messages WHERE message_type = '$fmt';" 2>/dev/null | tr -d ' ')
    GOLD=$(docker exec gps-cdm-postgres psql -U gps_cdm_svc -d gps_cdm -t -c \
        "SELECT COUNT(*) FROM gold.cdm_payment_instruction WHERE source_message_type = '$fmt';" 2>/dev/null | tr -d ' ')

    if [ "$BRONZE" -gt 0 ] && [ "$GOLD" -gt 0 ]; then
        STATUS="✅ PASS"
    elif [ "$BRONZE" -gt 0 ]; then
        STATUS="⚠️  PARTIAL (Bronze OK, Gold missing)"
    else
        STATUS="❌ FAIL"
    fi

    printf "%-12s Bronze: %3s  Gold: %3s  %s\n" "$fmt" "$BRONZE" "$GOLD" "$STATUS"
done
```

---

### Troubleshooting E2E Test Failures

#### Files Not Picked Up by NiFi

**Symptom**: Files remain in `/opt/nifi/nifi-current/input/`

**Check**:
```bash
docker exec gps-cdm-nifi ls -la /opt/nifi/nifi-current/input/
```

**Fix**: Ensure files have correct permissions (644) and owner (nifi:nifi)
```bash
# Re-copy using tar method
cd /tmp/nifi_input_test && tar cf - . | docker exec -i gps-cdm-nifi tar xf - -C /opt/nifi/nifi-current/input/
```

#### Bronze Records Created but Silver Empty

**Symptom**: Records in `bronze.raw_payment_messages` but none in `silver.stg_*`

**Check**:
```bash
# Check Silver consumer logs
tail -50 /tmp/zone_consumer_silver.log | grep -E "ERROR|Exception"

# Check Celery logs
tail -50 /tmp/celery_gps_cdm.log | grep -E "process_silver|ERROR"
```

**Common causes**:
- Parser error (format mismatch)
- Column name mismatch between extractor and DB schema
- Missing extractor registration

#### Silver Records Created but Gold Empty

**Symptom**: Records in Silver but none in Gold tables

**Check**:
```bash
# Check Gold consumer logs
tail -50 /tmp/zone_consumer_gold.log | grep -E "ERROR|Exception"

# Check for constraint violations
docker exec gps-cdm-postgres psql -U gps_cdm_svc -d gps_cdm -c \
    "SELECT * FROM dlq.failed_messages ORDER BY created_at DESC LIMIT 5;"
```

**Common causes**:
- NOT NULL constraint violation (often `country` field)
- Missing Gold field mappings in `mapping.gold_field_mappings`
- Transform errors (e.g., invalid date format)

#### Gold Constraint Violations

**Symptom**: `null value in column "country" violates not-null constraint`

**Fix**: Add default value in Gold mapping:
```sql
UPDATE mapping.gold_field_mappings
SET transform_expression = 'COALESCE:XX'
WHERE format_id = '{FORMAT}'
  AND gold_table = 'cdm_financial_institution'
  AND gold_column = 'country';
```

---

### E2E Test Results Summary (29 Formats)

| Format | Bronze | Silver | Gold | Status |
|--------|--------|--------|------|--------|
| pain.001 | ✅ | ✅ | ✅ | **PASS** |
| pacs.008 | ✅ | ✅ | ✅ | **PASS** |
| MT103 | ✅ | ✅ | ✅ | **PASS** |
| MT202 | ✅ | ✅ | ✅ | **PASS** |
| MT940 | ✅ | ✅ | ✅ | **PASS** |
| camt.053 | ✅ | ✅ | ✅ | **PASS** |
| ACH | ✅ | ✅ | ✅ | **PASS** |
| FEDWIRE | ✅ | ✅ | ✅ | **PASS** |
| SEPA | ✅ | ✅ | ✅ | **PASS** |
| RTP | ✅ | ✅ | ✅ | **PASS** |
| CHAPS | ✅ | ✅ | ✅ | **PASS** |
| FPS | ✅ | ✅ | ✅ | **PASS** |
| BACS | ✅ | ✅ | ✅ | **PASS** |
| CHIPS | ✅ | ✅ | ✅ | **PASS** |
| FEDNOW | ✅ | ✅ | ✅ | **PASS** |
| TARGET2 | ✅ | ✅ | ✅ | **PASS** |
| NPP | ✅ | ✅ | ✅ | **PASS** |
| PIX | ✅ | ✅ | ✅ | **PASS** |
| UPI | ✅ | ✅ | ✅ | **PASS** |
| CNAPS | ✅ | ✅ | ✅ | **PASS** |
| BOJNET | ✅ | ✅ | ✅ | **PASS** |
| KFTC | ✅ | ✅ | ✅ | **PASS** |
| MEPS_PLUS | ✅ | ✅ | ✅ | **PASS** |
| RTGS_HK | ✅ | ✅ | ✅ | **PASS** |
| SARIE | ✅ | ✅ | ✅ | **PASS** |
| UAEFTS | ✅ | ✅ | ✅ | **PASS** |
| PROMPTPAY | ✅ | ✅ | ✅ | **PASS** |
| PAYNOW | ✅ | ✅ | ✅ | **PASS** |
| INSTAPAY | ✅ | ✅ | ✅ | **PASS** |

**Total**: 29/29 formats passing E2E validation (100%)

---

## Known Issues Identified During E2E Testing

This section documents issues discovered during comprehensive E2E testing of all 29 message formats. Each issue includes root cause, affected components, and resolution.

### Issue #1: Gold Layer NULL Constraint Violations on `country` Field

**Severity**: HIGH
**Affected Formats**: ACH, SEPA, FEDWIRE, PIX, UPI, and most ISO 20022 formats
**Error Message**: `null value in column "country" of relation "cdm_financial_institution" violates not-null constraint`

**Root Cause**:
The `cdm_financial_institution` table has a NOT NULL constraint on the `country` column. When source data doesn't include country information, the DynamicGoldMapper fails to derive a value.

**Affected Code**:
- `src/gps_cdm/orchestration/dynamic_gold_mapper.py` - `_apply_transform()` method
- `mapping.gold_field_mappings` table - Missing COALESCE defaults

**Resolution**:
1. Add `COUNTRY_FROM_BIC` transform to derive country from BIC (positions 5-6)
2. Add `COALESCE:XX` default for country field in Gold mappings
3. Update database mappings for all formats:

```sql
-- Fix country field for all formats with DEBTOR_AGENT and CREDITOR_AGENT roles
UPDATE mapping.gold_field_mappings
SET transform_expression = 'COUNTRY_FROM_BIC',
    default_value = 'XX'
WHERE gold_table = 'cdm_financial_institution'
  AND gold_column = 'country'
  AND is_active = true;

-- Verify fix
SELECT format_id, entity_role, transform_expression, default_value
FROM mapping.gold_field_mappings
WHERE gold_table = 'cdm_financial_institution' AND gold_column = 'country';
```

---

### Issue #2: DLQ Serialization Bug in Zone Consumers

**Severity**: MEDIUM
**Affected Component**: `src/gps_cdm/streaming/zone_consumers.py`
**Error Message**: `'dict' object has no attribute 'encode'`
**Line**: ~314 (in `_publish_to_dlq` method)

**Root Cause**:
The DLQ producer attempts to serialize a dict value directly, but the `value_serializer` expects a string. The regular producer uses string serialization, but DLQ messages are dicts.

**Affected Code**:
```python
# zone_consumers.py line ~314
producer.send(
    topic=dlq_topic,
    key=message.get('batch_id', 'unknown'),
    value=dlq_message,  # This is a dict, not a string
)
```

**Resolution**:
The DLQ producer now correctly uses JSON serialization (already fixed at lines 298-304):
```python
self._dlq_producer = KafkaProducer(
    bootstrap_servers=self.config.bootstrap_servers,
    key_serializer=lambda k: k.encode('utf-8') if k else None,
    value_serializer=lambda v: json.dumps(v).encode('utf-8') if v else None,
)
```

**Verification**:
```python
# Test DLQ publishing
consumer._publish_to_dlq({'batch_id': 'test', 'content': 'test'}, 'Test error')
# Should not raise 'dict' object has no attribute 'encode'
```

---

### Issue #3: Multi-Transaction Files Only Extract First Transaction

**Severity**: MEDIUM
**Affected Formats**: pain.001, pacs.008, TARGET2, SEPA (any format with multiple transactions per file)
**Symptom**: Files with 3 transactions only produce 1 Silver/Gold record

**Root Cause**:
The message splitter (`src/gps_cdm/orchestration/message_splitter.py`) and parsers extract only the first transaction from multi-transaction XML files. The `CdtTrfTxInf` (pain.001) or `FIToFICstmrCdtTrf` (pacs.008) elements are not iterated.

**Affected Code**:
- `src/gps_cdm/orchestration/message_splitter.py` - `split_message()` function
- `src/gps_cdm/message_formats/pain001/__init__.py` - Parser extracts first `CdtTrfTxInf` only
- `src/gps_cdm/message_formats/pacs008/__init__.py` - Parser extracts first transaction only

**Expected Behavior**:
- Input: pain.001 file with 3 `CdtTrfTxInf` elements
- Output: 3 Bronze records, 3 Silver records, 3 Gold payment instructions

**Resolution**:
Update `split_message()` in `message_splitter.py` to:
1. For pain.001: Extract all `CdtTrfTxInf` elements, preserving parent `PmtInf` context
2. For pacs.008: Extract all `CdtTrfTxInf` elements within `FIToFICstmrCdtTrf`
3. For SWIFT MT: Split by `{1:` block boundaries for multi-message files
4. For ACH: Split by `6` record types (entry detail records)

```python
# Example: Split pain.001 into individual transactions
def split_pain001(content: str) -> List[Dict[str, Any]]:
    root = ET.fromstring(content)
    transactions = []

    for pmt_inf in root.findall('.//PmtInf'):
        # Extract shared context (debtor, debtor account, etc.)
        shared_context = extract_pmt_inf_context(pmt_inf)

        for tx in pmt_inf.findall('.//CdtTrfTxInf'):
            tx_content = ET.tostring(tx, encoding='unicode')
            transactions.append({
                'content': tx_content,
                'parent_context': shared_context,
                'index': len(transactions)
            })

    return transactions
```

---

### Issue #4: DynamicMapper Path Mismatches for JSON Formats (PIX, UPI)

**Severity**: LOW
**Affected Formats**: PIX, UPI, PROMPTPAY, PAYNOW
**Symptom**: Many Silver columns NULL despite data in source JSON

**Root Cause**:
The `mapping.silver_field_mappings` table has `parser_path` values that assume nested JSON structure (e.g., `debtor.name`), but test data uses flat keys (e.g., `debtorName`).

**Example Mismatch**:
| Database `parser_path` | Test Data Key | Result |
|------------------------|---------------|--------|
| `debtor.name` | `debtorName` | NULL (no match) |
| `amount.value` | `amount` | NULL (no match) |
| `creditor.account.number` | `creditorAccountNumber` | NULL (no match) |

**Resolution Options**:

**Option A: Update test data to match mapping paths** (Recommended)
```json
{
  "transactionId": "TX001",
  "debtor": {
    "name": "Test Debtor",
    "account": { "number": "123456" }
  },
  "creditor": {
    "name": "Test Creditor",
    "account": { "number": "789012" }
  },
  "amount": { "value": 1000.00, "currency": "BRL" }
}
```

**Option B: Update Silver mappings to match flat test data**
```sql
UPDATE mapping.silver_field_mappings
SET parser_path = 'debtorName'
WHERE format_id = 'PIX' AND target_column = 'debtor_name';
```

**Option C: Update DynamicMapper to try multiple path formats**
```python
def _resolve_path(self, data: dict, path: str) -> Any:
    # Try original nested path
    value = self._get_nested(data, path)
    if value is not None:
        return value

    # Try flattened camelCase version
    flat_key = path.replace('.', '')
    flat_key = flat_key[0].lower() + flat_key[1:]  # debtorName
    return data.get(flat_key)
```

---

### Issue #5: Extension Table Column Mismatches

**Severity**: LOW
**Affected Formats**: Various (format-specific extension tables)
**Error Message**: `column "xxx" of relation "cdm_payment_extension_yyy" does not exist`

**Root Cause**:
Gold field mappings reference columns that don't exist in extension tables, either because:
1. Column was added to mapping but not to table DDL
2. Column name mismatch (typo or naming convention)

**Resolution**:
1. Compare mapping columns against actual table schema
2. Add missing columns or fix mapping column names

```sql
-- Find mismatches: columns in mappings but not in table
SELECT DISTINCT gfm.gold_column
FROM mapping.gold_field_mappings gfm
WHERE gfm.gold_table = 'cdm_payment_extension_fedwire'
  AND gfm.gold_column NOT IN (
    SELECT column_name FROM information_schema.columns
    WHERE table_schema = 'gold' AND table_name = 'cdm_payment_extension_fedwire'
  );

-- Add missing columns
ALTER TABLE gold.cdm_payment_extension_fedwire
ADD COLUMN IF NOT EXISTS missing_column_name VARCHAR(255);
```

---

### Issue #6: Silver Column Name Mismatches

**Severity**: MEDIUM
**Affected Code**: Extractor `get_silver_columns()` methods
**Error Message**: `column "xxx" does not exist` on INSERT

**Root Cause**:
Extractor classes return column names that don't match the actual database schema. Common mismatches:

| Extractor Column | Actual DB Column | Format |
|------------------|------------------|--------|
| `sender_reference` | `senders_reference` | MT103 |
| `currency_code` | `currency` | MT103 |
| `sender_routing_number` | `sender_aba` | FEDWIRE |
| `standard_entry_class_code` | `standard_entry_class` | ACH |

**Resolution**:
Compare extractor columns with database schema and update extractor code:

```sql
-- Get actual columns for a Silver table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'silver' AND table_name = 'stg_mt103'
ORDER BY ordinal_position;
```

```python
# Fix extractor to match DB schema
def get_silver_columns(self) -> List[str]:
    return [
        'stg_id', 'raw_id', 'batch_id',
        'senders_reference',  # NOT sender_reference
        'currency',  # NOT currency_code
        # ...
    ]
```

---

### Issue #7: Python `.get()` Returns None for Existing Keys with None Values

**Severity**: MEDIUM
**Affected Code**: All extractors using `.get('key', 'default')` pattern

**Root Cause**:
Python's `dict.get('key', 'default')` returns `None` (not the default) when the key exists but has a `None` value. This causes NOT NULL constraint violations.

**Bad Pattern**:
```python
account_type = data.get('accountType', 'CACC')  # Returns None if key exists with None value
```

**Good Pattern**:
```python
account_type = data.get('accountType') or 'CACC'  # Returns 'CACC' even if key exists with None
```

**Resolution**:
Search and replace across all extractor modules:

```bash
# Find instances of this pattern
grep -r "\.get('.*', '" src/gps_cdm/message_formats/

# Replace with 'or' pattern for nullable fields
# Manual review required to determine which fields need defaults
```

---

### Summary Table: All E2E Issues

| # | Issue | Severity | Status | Fix Location |
|---|-------|----------|--------|--------------|
| 1 | Gold country NULL constraint | HIGH | ✅ Fixed | `mapping.gold_field_mappings` - 84 rows updated with `COUNTRY_FROM_BIC` transform |
| 2 | DLQ serialization bug | MEDIUM | ✅ Fixed | `zone_consumers.py:298-304` - JSON serialization for DLQ producer |
| 3 | Multi-TX files single record | MEDIUM | ✅ Fixed | `zone_consumers.py:538-600` - BronzeConsumer now splits messages |
| 4 | JSON path mismatches | LOW | ✅ Fixed | `dynamic_mapper.py:91-156` - Multi-format path resolution |
| 5 | Extension column mismatches | LOW | Deferred | DDL or mappings - minor impact |
| 6 | Silver column mismatches | MEDIUM | ✅ Fixed | Extractor classes |
| 7 | Python .get() None handling | MEDIUM | ✅ Fixed | All extractors |

---

### Verification After Fixes

After applying fixes, run the full E2E test suite:

```bash
# Run batch E2E test
./scripts/run_all_formats_e2e.sh

# Or individual format
./scripts/run_e2e_test.sh pain.001 /tmp/nifi_input_test/pain.001_test.xml

# Expected: All 29 formats show Bronze/Silver/Gold records created
```

**Success Criteria**:
- No NULL constraint violations in Celery logs
- Multi-TX files produce multiple records
- All 29 formats: Bronze ✅ Silver ✅ Gold ✅
