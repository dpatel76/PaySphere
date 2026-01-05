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
