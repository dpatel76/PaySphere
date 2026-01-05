# Message Format Implementation Blueprint

## Overview

This document describes the proven methodology for implementing complete Bronze → Silver → Gold coverage for payment message formats in the GPS CDM pipeline. This blueprint was validated with pain.001 and MT103 implementations.

## Architecture

```
NiFi (File Ingestion)
    → Kafka (bronze.{MSG_TYPE})
    → Bronze Consumer → Celery process_bronze_records
    → Kafka (silver.{MSG_TYPE})
    → Silver Consumer → Celery process_silver_records
    → Kafka (gold.{MSG_TYPE})
    → Gold Consumer → Celery process_gold_records
    → PostgreSQL (Bronze/Silver/Gold tables)
```

## Implementation Phases

### Phase 1: Schema & Mapping Setup

#### 1.1 Verify/Create Silver Table
```sql
-- Check if Silver table exists
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'silver' AND table_name = 'stg_{format_id}'
ORDER BY ordinal_position;
```

#### 1.2 Verify Standard Fields
```sql
-- Check standard fields defined for format
SELECT field_name, field_tag, is_mandatory, field_category
FROM mapping.standard_fields
WHERE format_id = '{FORMAT_ID}' AND is_active = true
ORDER BY field_tag;
```

#### 1.3 Verify Silver Field Mappings
```sql
-- Check Silver mappings
SELECT target_column, source_path, is_required
FROM mapping.silver_field_mappings
WHERE format_id = '{FORMAT_ID}' AND is_active = true
ORDER BY ordinal_position;
```

#### 1.4 Verify Gold Field Mappings
```sql
-- Check Gold mappings by table
SELECT gold_table, gold_column, source_expression, transform_expression, entity_role
FROM mapping.gold_field_mappings
WHERE format_id = '{FORMAT_ID}' AND is_active = true
ORDER BY gold_table, entity_role, ordinal_position;
```

### Phase 2: Extractor Implementation

#### 2.1 File Location
```
src/gps_cdm/message_formats/{format_name}/__init__.py
```

#### 2.2 Required Components

1. **Parser Class** - Format-specific parser (XML, SWIFT MT, Fixed-width, JSON)
2. **Extractor Class** - Implements BaseExtractor interface
3. **Registration** - Register with ExtractorRegistry

#### 2.3 Extractor Interface
```python
class {Format}Extractor(BaseExtractor):
    MESSAGE_TYPE = '{FORMAT_ID}'

    def __init__(self):
        self.parser = {Format}Parser()  # Format-specific parser

    def extract_bronze(self, raw_content, batch_id) -> Dict[str, Any]:
        """Extract Bronze layer record."""
        pass

    def extract_silver(self, msg_content, raw_id, stg_id, batch_id) -> Dict[str, Any]:
        """Extract Silver layer fields - MUST match DB columns exactly."""
        pass

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver columns for INSERT."""
        pass

    def get_silver_values(self, silver_record) -> tuple:
        """Return ordered tuple of values for INSERT."""
        pass

    def extract_gold_entities(self, silver_data, stg_id, batch_id) -> GoldEntities:
        """Extract Gold entities (parties, accounts, FIs)."""
        pass

# Register extractor
ExtractorRegistry.register('{FORMAT_ID}', {Format}Extractor())
ExtractorRegistry.register('{format_id}', {Format}Extractor())  # lowercase alias
```

### Phase 3: Parser Implementation by Format Type

#### 3.1 ISO 20022 XML (pain.001, pacs.008, camt.053, etc.)
```python
class ISO20022Parser:
    def parse(self, xml_content: str) -> Dict[str, Any]:
        # Strip namespaces
        xml_content = re.sub(r'\sxmlns[^"]*"[^"]*"', '', xml_content)
        root = ET.fromstring(xml_content)
        # Extract fields using XPath
        return result
```

#### 3.2 SWIFT MT (MT103, MT202, MT940, etc.)
```python
class SwiftMTParser:
    def parse(self, content: str) -> Dict[str, Any]:
        # Parse blocks {1:...}{2:...}{3:...}{4:...}{5:...}
        blocks = self._parse_blocks(content)
        # Block 4 contains :XX: tagged fields
        result = self._parse_block4(blocks.get('4', ''))
        return result

    def _parse_blocks(self, content):
        pattern = r'\{(\d):([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        # ...
```

#### 3.3 Fixed-Width (ACH/NACHA, BACS, etc.)
```python
class FixedWidthParser:
    def parse(self, content: str) -> Dict[str, Any]:
        lines = content.strip().split('\n')
        for line in lines:
            line = line.ljust(94)  # Pad to record length
            record_type = line[0]
            # Parse by position based on record type
```

#### 3.4 JSON (PIX, UPI, etc.)
```python
class JSONParser:
    def parse(self, content: str) -> Dict[str, Any]:
        if isinstance(content, str):
            return json.loads(content)
        return content
```

### Phase 4: Key Lessons Learned

#### 4.1 Python `.get()` Behavior
```python
# WRONG - returns None if key exists with None value
account_type = data.get('accountType', 'CACC')

# CORRECT - falls back even if key exists with None
account_type = data.get('accountType') or 'CACC'
```

#### 4.2 Column Names Must Match DB Schema
- Always verify column names against `information_schema.columns`
- Silver extractor's `get_silver_columns()` must return EXACT column names
- Common mismatches: `currency_code` vs `currency`, `sender_reference` vs `senders_reference`

#### 4.3 No Fallbacks in Mappings
- If source data doesn't have a value, store NULL
- Don't create synthetic fallbacks (e.g., don't use `currency` when `instructed_currency` is missing)
- Alter Gold schema to allow NULL for optional fields

#### 4.4 Gold Entity Transforms
Available transforms in DynamicGoldMapper:
- `COALESCE:literal` - Use literal if value is NULL
- `COALESCE_FIELD:field` - Use another Silver field if value is NULL
- `COALESCE_BIC` - Derive institution name from BIC
- `COUNTRY_FROM_BIC` - Extract country code (chars 5-6) from BIC
- `TO_ARRAY` - Wrap value in PostgreSQL array
- `TO_DECIMAL` - Convert to numeric
- `TO_DATE` - Parse ISO date string
- `UPPER`, `LOWER`, `TRIM` - String transforms

#### 4.5 Format-Specific Parsers in zone_tasks.py
The zone_tasks.py must use format-specific parsers:
```python
if hasattr(extractor, 'parser') and hasattr(extractor.parser, 'parse'):
    msg_content = extractor.parser.parse(raw_text)
```

### Phase 5: Testing Procedure

#### 5.1 Create Test File
```bash
# For SWIFT MT
docker exec gps-cdm-nifi bash -c 'cat > /opt/nifi/nifi-current/input/{FORMAT}_test.txt << EOF
{message content}
EOF'

# For XML
docker exec gps-cdm-nifi bash -c 'cat > /opt/nifi/nifi-current/input/{FORMAT}_test.xml << EOF
<?xml version="1.0"?>
{xml content}
EOF'
```

#### 5.2 Start Zone Consumers
```bash
# Start consumers for the format
for zone in bronze silver gold; do
  PYTHONPATH=src:$PYTHONPATH \
  python -m gps_cdm.streaming.zone_consumers --zone $zone --types {FORMAT_ID} &
done
```

#### 5.3 Verify Processing
```bash
# Check Celery logs
tail -f /tmp/celery_gps_cdm.log | grep -E "{FORMAT_ID}|error|ERROR"

# Check Bronze
SELECT raw_id, message_type, processing_status
FROM bronze.raw_payment_messages
WHERE message_type = '{FORMAT_ID}'
ORDER BY _ingested_at DESC LIMIT 5;

# Check Silver
SELECT stg_id, {key_fields}, processing_status
FROM silver.stg_{format_id}
ORDER BY stg_id DESC LIMIT 5;

# Check Gold
SELECT instruction_id, debtor_id, creditor_id
FROM gold.cdm_payment_instruction
WHERE source_message_type = '{FORMAT_ID}'
ORDER BY created_at DESC LIMIT 5;
```

### Phase 6: Reconciliation

#### 6.1 Standard to Silver Coverage
```sql
SELECT
  sf.field_name,
  sf.field_tag,
  sf.is_mandatory,
  COALESCE(string_agg(DISTINCT sm.target_column, ', '), '*** MISSING ***') as silver_columns
FROM mapping.standard_fields sf
LEFT JOIN mapping.silver_field_mappings sm
  ON sf.format_id = sm.format_id AND sf.standard_field_id = sm.standard_field_id
WHERE sf.format_id = '{FORMAT_ID}' AND sf.is_active = true
GROUP BY sf.standard_field_id, sf.field_name, sf.field_tag, sf.is_mandatory
ORDER BY sf.field_tag;
```

#### 6.2 Silver to Gold Coverage
```sql
SELECT gold_table, COUNT(DISTINCT gold_column) as field_count
FROM mapping.gold_field_mappings
WHERE format_id = '{FORMAT_ID}' AND is_active = true
GROUP BY gold_table
ORDER BY gold_table;
```

#### 6.3 Data Population Verification
```sql
-- Verify all mandatory fields populated
SELECT
  sf.field_name,
  sf.is_mandatory,
  CASE WHEN {column} IS NOT NULL THEN 'PASS' ELSE 'FAIL' END as status
FROM mapping.standard_fields sf, silver.stg_{format_id} s
WHERE sf.format_id = '{FORMAT_ID}'
  AND sf.is_mandatory = true
  AND s.stg_id = '{test_stg_id}';
```

### Phase 7: Common Issues & Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| Wrong parser used | Fields NULL or wrong names | Use format-specific parser in zone_tasks.py |
| Column name mismatch | INSERT fails | Match `get_silver_columns()` to DB schema |
| NULL in NOT NULL column | Constraint violation | Either fix mapping or ALTER TABLE to allow NULL |
| Array literal error | `malformed array literal` | Add `TO_ARRAY` transform |
| Value too long | `value too long for varchar(N)` | ALTER COLUMN to larger size |
| Missing transform | NULL in derived field | Add appropriate transform (COUNTRY_FROM_BIC, etc.) |

### Phase 8: Checklist

- [ ] Standard fields defined in `mapping.standard_fields`
- [ ] Silver table exists with correct columns
- [ ] Silver mappings in `mapping.silver_field_mappings`
- [ ] Gold mappings in `mapping.gold_field_mappings`
- [ ] Extractor class implemented with parser
- [ ] Extractor registered in ExtractorRegistry
- [ ] Zone consumers running for format
- [ ] Test file processed through NiFi → Kafka → Celery
- [ ] Bronze record created with correct message_type
- [ ] Silver record created with all mandatory fields
- [ ] Gold entities created (instruction, parties, accounts, FIs)
- [ ] Reconciliation report shows 100% mandatory coverage
- [ ] No fallback values - NULL when source absent

## Message Format Categories

### ISO 20022
- pain.001, pain.002, pain.008
- pacs.002, pacs.003, pacs.004, pacs.008, pacs.009
- camt.052, camt.053, camt.054
- SEPA, CHAPS, FPS, TARGET2, FEDNOW, NPP, RTP
- MEPS_PLUS, RTGS_HK, UAEFTS, PromptPay, PayNow, InstaPay

### SWIFT MT
- MT103, MT103STP, MT101, MT199
- MT202, MT202COV
- MT900, MT910, MT940, MT950

### US Domestic
- FEDWIRE (tag-value)
- ACH/NACHA (fixed-width 94 chars)
- CHIPS (proprietary)

### UK Domestic
- BACS (fixed-width)
- CHAPS, FPS (ISO 20022)

### Asia-Pacific
- CNAPS (China - proprietary)
- BOJNET (Japan - proprietary)
- KFTC (Korea - proprietary)
- UPI (India - JSON)
- PIX (Brazil - JSON)

### Middle East
- SARIE (Saudi - SWIFT-like)
- UAEFTS (UAE - ISO 20022)
