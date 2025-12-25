# GPS CDM Project - Claude Context

## Project Overview

GPS Common Domain Model (CDM) - A payment message processing pipeline supporting 63+ payment standards across ISO 20022, SWIFT MT, and regional payment schemes. Uses medallion architecture (Bronze → Silver → Gold) with Celery for distributed task processing and NiFi for flow orchestration.

## Architecture

```
NiFi (Flow Orchestration)
    → Flower API (Celery Task Submission)
    → Redis (Message Broker)
    → Celery Workers (Task Processing)
    → PostgreSQL / Databricks (Persistence)
    → Neo4j (Knowledge Graph)
```

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
