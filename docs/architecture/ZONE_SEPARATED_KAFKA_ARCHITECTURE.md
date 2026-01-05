# GPS CDM Zone-Separated Kafka Architecture

## Overview

This document describes the target architecture for the GPS CDM pipeline where each zone (Bronze, Silver, Gold) has dedicated Kafka topics and consumers, ensuring proper separation of concerns and full lineage tracking.

## Current State (Problems)

The current implementation has several issues:

1. **Monolithic Pipeline**: `process_medallion_pipeline()` handles Bronze → Silver → Gold in one task
2. **JSON Wrapping**: Raw content is wrapped in `{"_raw_text": "..."}` instead of stored as-is
3. **Single Kafka Topic Flow**: No separation between zone-specific topics
4. **Parser Confusion**: Wrong parsers used (ChapsXmlParser for SWIFT MT block format)
5. **No Message ID Passing**: Zones don't communicate via Kafka message IDs

## Target Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              NiFi Flow                                       │
│  ┌──────────┐    ┌─────────────────┐    ┌──────────────────────────────┐   │
│  │ GetFile  │───▶│ Detect Message  │───▶│ PublishKafka to Bronze Topic │   │
│  │          │    │ Type & Format   │    │ (raw content as-is)          │   │
│  └──────────┘    └─────────────────┘    └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Kafka Topics (Bronze)                                │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐    │
│  │ bronze.pain.001    │  │ bronze.MT103       │  │ bronze.CHAPS       │    │
│  │ bronze.pacs.008    │  │ bronze.MT202       │  │ bronze.BACS        │    │
│  │ bronze.camt.053    │  │ bronze.MT940       │  │ bronze.FEDWIRE     │    │
│  │ ...                │  │ ...                │  │ ...                │    │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Bronze Consumer Pool (Celery)                             │
│                                                                              │
│  For each message:                                                           │
│  1. Store raw content AS-IS in bronze.raw_payment_messages                  │
│  2. Generate raw_id                                                          │
│  3. Publish raw_id to silver.{message_type} Kafka topic                     │
│  4. Track batch progress in observability.obs_batch_tracking                │
│                                                                              │
│  Task: process_bronze_message(content, message_type, batch_id, metadata)    │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Kafka Topics (Silver)                                │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐    │
│  │ silver.pain.001    │  │ silver.MT103       │  │ silver.CHAPS       │    │
│  │ (raw_id messages)  │  │ (raw_id messages)  │  │ (raw_id messages)  │    │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Silver Consumer Pool (Celery)                             │
│                                                                              │
│  For each raw_id:                                                            │
│  1. Retrieve raw content from bronze.raw_payment_messages by raw_id         │
│  2. Parse using format-appropriate parser (SWIFT MT, XML, JSON, etc.)       │
│  3. Extract fields using database mappings (mapping.silver_field_mappings)  │
│  4. Store in silver.stg_{message_type}                                      │
│  5. Generate stg_id                                                          │
│  6. Publish stg_id to gold.{message_type} Kafka topic                       │
│  7. Update bronze record: processing_status = 'PROMOTED_TO_SILVER'          │
│  8. Track lineage in observability.obs_data_lineage                         │
│                                                                              │
│  Task: process_silver_message(raw_id, message_type, batch_id)               │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Kafka Topics (Gold)                                  │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐    │
│  │ gold.pain.001      │  │ gold.MT103         │  │ gold.CHAPS         │    │
│  │ (stg_id messages)  │  │ (stg_id messages)  │  │ (stg_id messages)  │    │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Gold Consumer Pool (Celery)                               │
│                                                                              │
│  For each stg_id:                                                            │
│  1. Retrieve parsed data from silver.stg_{message_type} by stg_id           │
│  2. Transform to CDM specifications using mapping.gold_field_mappings       │
│  3. Extract entities: Party, Account, FinancialInstitution                  │
│  4. Store in gold tables:                                                    │
│     - gold.cdm_payment_instruction                                           │
│     - gold.cdm_party (DEBTOR, CREDITOR, ULTIMATE_*)                         │
│     - gold.cdm_account (DEBTOR_ACCOUNT, CREDITOR_ACCOUNT)                   │
│     - gold.cdm_financial_institution (DEBTOR_AGENT, CREDITOR_AGENT)         │
│     - gold.cdm_payment_extension_{scheme} (format-specific data)            │
│  5. Update silver record: processing_status = 'PROMOTED_TO_GOLD'            │
│  6. Update Neo4j knowledge graph with full lineage                          │
│  7. Track completion in observability.obs_batch_tracking                    │
│                                                                              │
│  Task: process_gold_message(stg_id, message_type, batch_id)                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Kafka Topic Naming Convention

```
Zone      : bronze | silver | gold
Separator : .
Message   : pain.001 | pacs.008 | MT103 | CHAPS | FEDWIRE | etc.

Examples:
  bronze.pain.001    - Raw pain.001 XML content
  bronze.MT103       - Raw SWIFT MT103 block format
  bronze.CHAPS       - Raw CHAPS SWIFT MT block format

  silver.pain.001    - raw_id for pain.001 messages
  silver.MT103       - raw_id for MT103 messages
  silver.CHAPS       - raw_id for CHAPS messages

  gold.pain.001      - stg_id for pain.001 messages
  gold.MT103         - stg_id for MT103 messages
  gold.CHAPS         - stg_id for CHAPS messages
```

## Message Format Detection

Raw content format is detected by content inspection, NOT by filename:

| Format | Detection Pattern | Parser |
|--------|------------------|--------|
| SWIFT MT Block | Starts with `{1:` or `{2:` | ChapsSwiftParser |
| ISO 20022 XML | Starts with `<?xml` or `<Document` | XML ElementTree |
| JSON | Starts with `{` (not SWIFT) or `[` | json.loads() |
| NACHA/ACH | Lines of exactly 94 characters | Fixed-width parser |
| FEDWIRE | Contains `{NNNN}` tags | Tag-value parser |

## Database Tables

### Bronze Layer (Unchanged)
```sql
bronze.raw_payment_messages
  raw_id            VARCHAR(36) PRIMARY KEY
  message_type      VARCHAR(50)
  message_format    VARCHAR(20)  -- XML, SWIFT_MT, JSON, FIXED, etc.
  raw_content       TEXT         -- STORED AS-IS (no JSON wrapping!)
  raw_content_hash  VARCHAR(64)  -- SHA-256 for deduplication
  source_system     VARCHAR(100)
  source_batch_id   VARCHAR(36)
  processing_status VARCHAR(20)  -- PENDING, PROMOTED_TO_SILVER, FAILED
  _batch_id         VARCHAR(36)
  _ingested_at      TIMESTAMP
```

### Silver Layer (Per Message Type)
```sql
silver.stg_{message_type}
  stg_id            VARCHAR(36) PRIMARY KEY
  raw_id            VARCHAR(36) REFERENCES bronze.raw_payment_messages
  -- Extracted fields based on mapping.silver_field_mappings
  processing_status VARCHAR(20)  -- PENDING, PROMOTED_TO_GOLD, FAILED
  _batch_id         VARCHAR(36)
  _processed_at     TIMESTAMP
```

### Gold Layer (CDM Entities)
```sql
gold.cdm_payment_instruction
  instruction_id      VARCHAR(36) PRIMARY KEY
  source_stg_id       VARCHAR(36)  -- FK to silver table
  source_message_type VARCHAR(50)
  -- CDM unified fields

gold.cdm_party
  party_id            VARCHAR(36) PRIMARY KEY
  instruction_id      VARCHAR(36)
  role                VARCHAR(30)  -- DEBTOR, CREDITOR, ULTIMATE_*
  -- Party fields

gold.cdm_account
  account_id          VARCHAR(36) PRIMARY KEY
  party_id            VARCHAR(36)
  role                VARCHAR(30)  -- DEBTOR_ACCOUNT, CREDITOR_ACCOUNT
  -- Account fields

gold.cdm_financial_institution
  fi_id               VARCHAR(36) PRIMARY KEY
  instruction_id      VARCHAR(36)
  role                VARCHAR(30)  -- DEBTOR_AGENT, CREDITOR_AGENT
  -- FI fields
```

### Observability (Enhanced)
```sql
observability.obs_batch_tracking
  batch_id          VARCHAR(36) PRIMARY KEY
  message_type      VARCHAR(50)
  total_messages    INTEGER
  bronze_received   INTEGER
  bronze_stored     INTEGER
  silver_processed  INTEGER
  gold_completed    INTEGER
  failed_count      INTEGER
  current_zone      VARCHAR(20)  -- BRONZE, SILVER, GOLD, COMPLETE
  started_at        TIMESTAMP
  completed_at      TIMESTAMP

observability.obs_message_tracking
  tracking_id       VARCHAR(36) PRIMARY KEY
  batch_id          VARCHAR(36)
  message_id        VARCHAR(36)  -- raw_id initially, then stg_id, then instruction_id
  message_type      VARCHAR(50)
  current_zone      VARCHAR(20)
  bronze_raw_id     VARCHAR(36)
  silver_stg_id     VARCHAR(36)
  gold_instr_id     VARCHAR(36)
  status            VARCHAR(20)
  error_message     TEXT
  created_at        TIMESTAMP
  updated_at        TIMESTAMP

observability.obs_data_lineage
  lineage_id        VARCHAR(36) PRIMARY KEY
  batch_id          VARCHAR(36)
  source_zone       VARCHAR(20)
  source_table      VARCHAR(100)
  source_id         VARCHAR(36)
  target_zone       VARCHAR(20)
  target_table      VARCHAR(100)
  target_id         VARCHAR(36)
  transformation    VARCHAR(50)
  field_mappings    JSONB        -- Which fields were mapped
  created_at        TIMESTAMP
```

## Celery Task Definitions

### Bronze Task
```python
@shared_task(queue='bronze')
def process_bronze_message(
    content: str,           # Raw content AS-IS
    message_type: str,      # pain.001, MT103, CHAPS, etc.
    message_format: str,    # XML, SWIFT_MT, JSON, FIXED
    batch_id: str,
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Store raw message in Bronze layer and publish raw_id to Silver topic.

    Returns:
        {
            'raw_id': str,
            'batch_id': str,
            'message_type': str,
            'status': 'SUCCESS' | 'FAILED',
            'error': str | None
        }
    """
```

### Silver Task
```python
@shared_task(queue='silver')
def process_silver_message(
    raw_id: str,
    message_type: str,
    batch_id: str
) -> Dict[str, Any]:
    """
    Retrieve Bronze record, parse content, extract to Silver, publish stg_id to Gold topic.

    Returns:
        {
            'stg_id': str,
            'raw_id': str,
            'batch_id': str,
            'message_type': str,
            'status': 'SUCCESS' | 'FAILED',
            'error': str | None,
            'field_count': int
        }
    """
```

### Gold Task
```python
@shared_task(queue='gold')
def process_gold_message(
    stg_id: str,
    message_type: str,
    batch_id: str
) -> Dict[str, Any]:
    """
    Retrieve Silver record, transform to CDM, store Gold entities.

    Returns:
        {
            'instruction_id': str,
            'stg_id': str,
            'batch_id': str,
            'message_type': str,
            'status': 'SUCCESS' | 'FAILED',
            'error': str | None,
            'entities': {
                'parties': List[str],
                'accounts': List[str],
                'financial_institutions': List[str]
            }
        }
    """
```

## Kafka Consumer Implementation

### Zone-Specific Consumer Base
```python
class ZoneConsumer:
    """Base consumer for zone-specific Kafka topics."""

    def __init__(
        self,
        zone: str,              # 'bronze', 'silver', 'gold'
        message_types: List[str],
        celery_task: str,       # Task name to invoke
        output_zone: str | None # Next zone to publish to (None for gold)
    ):
        self.zone = zone
        self.topics = [f"{zone}.{mt}" for mt in message_types]
        self.celery_task = celery_task
        self.output_zone = output_zone
        self.producer = None if output_zone is None else KafkaProducer()

    def process_message(self, msg) -> str:
        """Process message and return output ID for next zone."""
        result = celery_app.send_task(
            self.celery_task,
            kwargs=self._build_task_kwargs(msg)
        ).get(timeout=30)

        if result['status'] == 'SUCCESS':
            if self.output_zone:
                self._publish_to_next_zone(result)
            return result.get('raw_id') or result.get('stg_id') or result.get('instruction_id')
        else:
            self._handle_failure(msg, result)
            raise ProcessingError(result['error'])
```

### Bronze Consumer
```python
class BronzeConsumer(ZoneConsumer):
    def __init__(self, message_types: List[str]):
        super().__init__(
            zone='bronze',
            message_types=message_types,
            celery_task='gps_cdm.zone_tasks.process_bronze_message',
            output_zone='silver'
        )

    def _build_task_kwargs(self, msg) -> Dict:
        content = msg.value.decode('utf-8')
        message_type = msg.headers.get('message_type')
        message_format = self._detect_format(content)

        return {
            'content': content,  # AS-IS, no wrapping
            'message_type': message_type,
            'message_format': message_format,
            'batch_id': msg.headers.get('batch_id'),
            'metadata': {
                'kafka_topic': msg.topic,
                'kafka_partition': msg.partition,
                'kafka_offset': msg.offset,
                'source_timestamp': msg.timestamp
            }
        }

    def _detect_format(self, content: str) -> str:
        content = content.strip()
        if content.startswith('{1:') or content.startswith('{2:'):
            return 'SWIFT_MT'
        elif content.startswith('<?xml') or content.startswith('<Document'):
            return 'XML'
        elif content.startswith('{') or content.startswith('['):
            return 'JSON'
        elif len(content.split('\n')[0]) == 94:
            return 'FIXED'  # NACHA
        elif '{' in content and '}' in content and re.search(r'\{\d{4}\}', content):
            return 'TAG_VALUE'  # FEDWIRE
        else:
            return 'RAW'
```

### Silver Consumer
```python
class SilverConsumer(ZoneConsumer):
    def __init__(self, message_types: List[str]):
        super().__init__(
            zone='silver',
            message_types=message_types,
            celery_task='gps_cdm.zone_tasks.process_silver_message',
            output_zone='gold'
        )

    def _build_task_kwargs(self, msg) -> Dict:
        # Message value is just the raw_id
        raw_id = msg.value.decode('utf-8')
        return {
            'raw_id': raw_id,
            'message_type': msg.headers.get('message_type'),
            'batch_id': msg.headers.get('batch_id')
        }
```

### Gold Consumer
```python
class GoldConsumer(ZoneConsumer):
    def __init__(self, message_types: List[str]):
        super().__init__(
            zone='gold',
            message_types=message_types,
            celery_task='gps_cdm.zone_tasks.process_gold_message',
            output_zone=None  # Terminal zone
        )

    def _build_task_kwargs(self, msg) -> Dict:
        # Message value is just the stg_id
        stg_id = msg.value.decode('utf-8')
        return {
            'stg_id': stg_id,
            'message_type': msg.headers.get('message_type'),
            'batch_id': msg.headers.get('batch_id')
        }
```

## NiFi Configuration Changes

### Current NiFi Flow (To Change)
```
GetFile → UpdateAttribute → ReplaceText → InvokeHTTP (Flower API)
```

### New NiFi Flow
```
GetFile
    → UpdateAttribute (set message_type, batch_id, detect format)
    → PublishKafka (to bronze.{message_type} topic)
        - topic: ${message_type:prepend('bronze.')}
        - key: ${batch_id}
        - headers: message_type, batch_id, source_file
```

### NiFi Processor Configuration

**UpdateAttribute Processor:**
```
message_type = ${filename:substringBefore('_')}
batch_id = ${UUID()}
message_format = ${content:startsWith('{1:'):ifElse('SWIFT_MT',
                   ${content:startsWith('<?xml'):ifElse('XML',
                   ${content:startsWith('{'):ifElse('JSON', 'RAW')})})}
```

**PublishKafka Processor:**
```
Kafka Brokers: gps-cdm-kafka:9092
Topic Name: bronze.${message_type}
Message Key: ${batch_id}
Message Headers:
  message_type → ${message_type}
  batch_id → ${batch_id}
  message_format → ${message_format}
  source_file → ${filename}
Delivery Guarantee: GUARANTEE_REPLICATED_DELIVERY
```

## Implementation Plan

### Phase 1: Create Zone-Specific Kafka Topics
1. Create topic naming convention script
2. Create all bronze.*, silver.*, gold.* topics
3. Configure topic retention and partitions

### Phase 2: Implement Zone-Specific Celery Tasks
1. `process_bronze_message()` - Store raw, no JSON wrapping
2. `process_silver_message()` - Retrieve by raw_id, parse, extract
3. `process_gold_message()` - Retrieve by stg_id, transform to CDM

### Phase 3: Implement Zone-Specific Consumers
1. BronzeConsumer class with format detection
2. SilverConsumer class with raw_id handling
3. GoldConsumer class with stg_id handling

### Phase 4: Update NiFi Flow
1. Remove Flower API integration
2. Add PublishKafka processor
3. Configure topic routing by message type

### Phase 5: Enhanced Observability
1. Add message-level tracking table
2. Update batch tracking with zone progress
3. Implement full lineage in obs_data_lineage

### Phase 6: E2E Validation
1. Test all 29 message types through new flow
2. Validate data integrity across zones
3. Verify lineage completeness

## Benefits of This Architecture

1. **Separation of Concerns**: Each zone has dedicated processing logic
2. **Scalability**: Independent scaling per zone and message type
3. **Fault Isolation**: Failures in one zone don't affect others
4. **Full Lineage**: Complete tracking from raw to CDM
5. **Format Preservation**: Raw content stored exactly as received
6. **Dynamic Processing**: Mappings drive extraction, not hard-coded logic
7. **Transparency**: Message-level visibility into processing status
8. **Recovery**: Each zone can be replayed independently
