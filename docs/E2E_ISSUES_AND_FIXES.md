# E2E Testing Issues and Fixes

This document captures common issues encountered during E2E testing of the GPS CDM pipeline and their resolutions.

## Issue Categories

### 1. Parser Method Issues

**Problem**: Parser class missing required methods that are called by `parse_iso_paths()`.

**Symptoms**:
- Bronze `extractor_output` has snake_case keys instead of ISO dot-notation keys
- Falls back to `extract_silver()` which outputs old format

**Example**: `Pain001XmlParser` was missing `_parse_xml()`, `_get_split_grp_hdr()`, `_get_split_pmt_inf()` methods.

**Fix**: Add missing methods to the parser class:
```python
def _parse_xml(self, xml_content: str) -> ET.Element:
    """Parse XML content and return root element."""
    content = xml_content.strip()
    if content.startswith('\ufeff'):
        content = content[1:]
    return ET.fromstring(content)
```

---

### 2. Silver Mapping Data Type Mismatches

**Problem**: Silver mapping `data_type` doesn't match actual PostgreSQL column type.

**Symptoms**:
- `malformed array literal` error for array columns
- Type conversion errors during INSERT

**Example**: `rmt_inf_ustrd` column is `_text` (PostgreSQL array) but mapping had `data_type = 'VARCHAR'`.

**Fix**: Update mapping to correct data type:
```sql
UPDATE mapping.silver_field_mappings
SET data_type = 'ARRAY'
WHERE format_id = 'pain.001' AND target_column = 'rmt_inf_ustrd';
```

**How to detect**: Compare mapping data_type with actual column type:
```sql
SELECT c.column_name, c.udt_name, m.data_type as mapping_type
FROM information_schema.columns c
LEFT JOIN mapping.silver_field_mappings m
  ON c.column_name = m.target_column AND m.format_id = '{FORMAT}'
WHERE c.table_schema = 'silver' AND c.table_name = 'stg_{format}'
  AND c.udt_name LIKE '_%';  -- Array types start with underscore
```

---

### 3. Special Path Handler Mismatches

**Problem**: Silver mapping uses a special path (like `_FORMAT_ID`) that isn't handled by `extract_silver_record()`.

**Symptoms**:
- `null value in column "source_format" violates not-null constraint`
- Required columns remain NULL despite having mappings

**Example**: Mapping used `_FORMAT_ID` but code handles `_SOURCE_FORMAT`.

**Supported special paths**:
- `_GENERATED_UUID` - Auto-generate UUID
- `_RAW_ID` - Use raw_id from Bronze
- `_BATCH_ID` - Use batch_id
- `_TIMESTAMP` - Current UTC timestamp
- `_SOURCE_FORMAT` or `_sourceFormat` - Use format_id

**Fix**: Update mapping to use supported path:
```sql
UPDATE mapping.silver_field_mappings
SET parser_path = '_SOURCE_FORMAT'
WHERE format_id = 'pain.001' AND target_column = 'source_format';
```

---

### 4. Database Column Name Mismatches

**Problem**: Code uses column name that doesn't exist in actual table schema.

**Symptoms**:
- `column "xxx" does not exist` error
- Transaction aborts silently, subsequent operations fail

**Example**: Identifier insert used `party_identifier_id` but actual column is `id`.

**Fix**: Update code to use correct column names:
```python
# Before (wrong):
INSERT INTO gold.cdm_party_identifiers (party_identifier_id, ...)

# After (correct):
INSERT INTO gold.cdm_party_identifiers (id, ...)
```

**How to detect**:
```sql
SELECT column_name FROM information_schema.columns
WHERE table_schema = 'gold' AND table_name = 'cdm_party_identifiers';
```

---

### 5. NOT NULL Constraint Violations

**Problem**: Required column has no mapping or mapping returns NULL.

**Symptoms**:
- `null value in column "xxx" violates not-null constraint`
- Record insertion fails

**Fix Options**:
1. Add mapping with default value
2. Add special path handler (e.g., `_SOURCE_FORMAT`)
3. Update mapping to use COALESCE transform

```sql
-- Option 1: Add default value
UPDATE mapping.silver_field_mappings
SET default_value = 'UNKNOWN'
WHERE format_id = 'pain.001' AND target_column = 'xxx';

-- Option 2: Add COALESCE transform
UPDATE mapping.silver_field_mappings
SET transform_function = 'COALESCE', default_value = 'UNKNOWN'
WHERE format_id = 'pain.001' AND target_column = 'xxx';
```

---

### 6. Transaction Abort Propagation

**Problem**: An error in one SQL statement aborts the transaction, but subsequent statements fail with misleading "transaction is aborted" error.

**Symptoms**:
- Log shows SUCCESS then immediately FAILED
- Error message: `current transaction is aborted, commands ignored until end of transaction block`

**Root Cause**: Often a silent error in identifier insertion or entity creation.

**How to debug**:
1. Check for earlier errors in log
2. Look for try/except blocks that catch and log at DEBUG level
3. Test SQL statements individually

---

### 7. Gold Table Lookup Issues

**Problem**: E2E test queries wrong Gold table for format.

**Symptoms**:
- Gold processing succeeds in Celery log
- E2E test reports "Gold instruction NOT FOUND"

**Fix**: Ensure GOLD_TABLE_MAP in e2e_format_test.py has correct mapping:
```python
GOLD_TABLE_MAP = {
    'pain.001': 'cdm_pain_customer_credit_transfer_initiation',
    'pacs.008': 'cdm_pacs_fi_customer_credit_transfer',
    # etc.
}
```

Also verify database has correct mapping:
```sql
SELECT format_id, gold_table FROM mapping.message_formats WHERE format_id = 'pain.001';
```

---

## Debugging Workflow

1. **Check Celery logs** for actual error:
   ```bash
   tail -100 /tmp/celery_gps_cdm.log | grep -E "ERROR|FAIL|constraint"
   ```

2. **Verify Bronze extractor_output keys**:
   ```sql
   SELECT raw_id, jsonb_object_keys(extractor_output::jsonb)
   FROM bronze.raw_payment_messages
   WHERE message_type = 'pain.001'
   LIMIT 1;
   ```

3. **Check Silver mappings**:
   ```sql
   SELECT target_column, parser_path, data_type, default_value
   FROM mapping.silver_field_mappings
   WHERE format_id = 'pain.001' AND is_active = true
   ORDER BY target_column;
   ```

4. **Verify Silver columns match mappings**:
   ```sql
   SELECT c.column_name, c.data_type, c.is_nullable
   FROM information_schema.columns c
   WHERE c.table_schema = 'silver' AND c.table_name = 'stg_iso20022_pain001'
   ORDER BY c.ordinal_position;
   ```

5. **Test parser directly**:
   ```python
   from gps_cdm.message_formats.pain001 import Pain001XmlParser
   parser = Pain001XmlParser()
   result = parser.parse_iso_paths(xml_content)
   print(sorted(result.keys()))
   ```

---

## Quick Reference: Column Type Mappings

| PostgreSQL Type | Mapping data_type | Notes |
|-----------------|-------------------|-------|
| varchar, text | VARCHAR | Default |
| integer, int4 | INTEGER | |
| numeric, decimal | DECIMAL | |
| boolean, bool | BOOLEAN | |
| timestamp | TIMESTAMP | |
| date | DATE | |
| _text, text[] | ARRAY | Array types |
| jsonb | JSONB | |

---

## Checklist for New Format

- [ ] Parser has `parse_iso_paths()` method returning ISO dot-notation keys
- [ ] Silver mappings exist with correct `parser_path` values
- [ ] Silver mappings have correct `data_type` matching actual columns
- [ ] NOT NULL columns have mappings with defaults or special paths
- [ ] Gold table mapping exists in `GOLD_TABLE_MAP`
- [ ] Identifier insert statements use correct column names
