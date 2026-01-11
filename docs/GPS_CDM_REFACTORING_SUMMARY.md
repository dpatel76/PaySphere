# GPS CDM Major Refactoring Summary

**Date**: 2026-01-10
**Version**: 0.60

## Overview

This document summarizes the major refactoring changes made to the GPS CDM system to improve:
1. Entity traceability (payment-level history preservation)
2. Schema normalization (reduce denormalization)
3. Parser key naming consistency (full ISO paths)
4. Message splitter simplification (split only, no extraction)

## Changes by Phase

### Phase 1: Add source_instruction_id to Entity Tables

**Migration**: `ddl/postgresql/migrations/001_add_source_instruction_id.sql`

Added `source_instruction_id` column to entity tables for payment-level traceability:
- `gold.cdm_party`
- `gold.cdm_account`
- `gold.cdm_financial_institution`
- `gold.cdm_party_identifiers`
- `gold.cdm_account_identifiers`
- `gold.cdm_institution_identifiers`

Each entity record now links back to the payment instruction that created it.

### Phase 2: Enhance Base Parser with Full ISO Path Methods

**Files Modified**:
- `src/gps_cdm/message_formats/iso20022/base_parser.py`
- `src/gps_cdm/message_formats/pain001/__init__.py`

Added support for `<SplitTransaction>` wrapper handling:
- `_parse_xml()` - Detects and unwraps split transactions
- `_get_split_grp_hdr()` - Returns parent GrpHdr from split context
- `_get_split_pmt_inf()` - Returns parent PmtInf from split context

Updated pain.001 parser to:
- Work with both full documents and split transactions
- Use full ISO path dot-notation keys (e.g., `PmtInf.DbtrAgt.FinInstnId.BICFI`)

### Phase 3: Remove Extraction Logic from Message Splitter

**File Modified**: `src/gps_cdm/orchestration/message_splitter.py`

**Lines Removed**: ~200 lines of extraction logic

**Key Changes**:
- `_split_iso20022_xml()` now returns raw XML content wrapped in `<SplitTransaction>`
- Added `_build_transaction_xml()` to construct wrapper with parent context
- Added `_copy_element_without_children()` helper
- Removed `_extract_transaction_content()` and related extraction methods

**Splitter Output Format**:
```python
{
    'content': '<SplitTransaction><ParentGrpHdr>...</ParentGrpHdr><ParentPmtInf>...</ParentPmtInf><Transaction>...</Transaction></SplitTransaction>',
    'index': 0,
    'parent_context': {'GrpHdr.MsgId': 'MSG001'}  # Minimal IDs only
}
```

### Phase 4: Change Entity Persistence to Always INSERT

**File Modified**: `src/gps_cdm/orchestration/dynamic_gold_mapper.py`

**Key Changes**:
- Added `ENTITY_TABLES` constant: `{'cdm_party', 'cdm_account', 'cdm_financial_institution'}`
- `_persist_single_record()` uses simple INSERT (no ON CONFLICT) for entity tables
- Pre-generates `instruction_id` before entity persistence for `source_instruction_id` linkage
- Renamed identifier functions:
  - `_upsert_party_id` -> `_insert_party_id`
  - `_upsert_account_id` -> `_insert_account_id`
  - `_upsert_fi_id` -> `_insert_fi_id`
- All identifier inserts include `source_instruction_id` and `created_at`

**Pattern Change**:
```python
# Before (UPSERT - loses history):
INSERT INTO gold.cdm_party (...) VALUES (...) ON CONFLICT (party_id) DO NOTHING

# After (Always INSERT - preserves history):
INSERT INTO gold.cdm_party (..., source_instruction_id, created_at) VALUES (...)
```

### Phase 5: Normalize Party Identifier Columns

**Migration**: `ddl/postgresql/migrations/002_normalize_party_identifiers.sql`
**DDL Modified**: `ddl/postgresql/03_gold_cdm_tables.sql`

**Columns REMOVED from `cdm_party`**:
- `tax_id`
- `tax_id_type`
- `identification_type`
- `identification_number`
- `national_id_type`
- `national_id_number`

**Columns KEPT in `cdm_party`**:
- `bic` (dual access - also in identifier table)
- `lei` (dual access - also in identifier table)
- `tax_id_country` (context field)
- `identification_country` (context field)
- `identification_expiry` (context field)
- `ultimate_debtor_bic`, `ultimate_creditor_bic`
- All address fields

**Migration Actions**:
1. Migrate existing identifiers to `cdm_party_identifiers` table
2. Remove columns from `cdm_party`
3. Deactivate Gold field mappings for removed columns

### Phase 6: Normalize ISO Semantic Tables

**Migration**: `ddl/postgresql/migrations/003_normalize_iso_semantic_tables.sql`

**Entity FK Columns Added to**:
- `cdm_pain_customer_credit_transfer_initiation` (pain.001)
- `cdm_pacs_fi_customer_credit_transfer` (pacs.008)
- `cdm_pacs_fi_credit_transfer` (pacs.009)
- `cdm_pacs_payment_return` (pacs.004)
- `cdm_pacs_fi_payment_status_report` (pacs.002)
- `cdm_camt_bank_to_customer_statement` (camt.053)
- `cdm_pain_customer_direct_debit_initiation` (pain.008)

**New FK Columns**:
- `debtor_party_id` -> `cdm_party`
- `debtor_account_id` -> `cdm_account`
- `debtor_agent_id` -> `cdm_financial_institution`
- `creditor_party_id` -> `cdm_party`
- `creditor_account_id` -> `cdm_account`
- `creditor_agent_id` -> `cdm_financial_institution`
- `ultimate_debtor_party_id`, `ultimate_creditor_party_id`
- `intermediary_agent1_id`, `intermediary_agent2_id`, `intermediary_agent3_id`

**Gold Field Mappings Added**:
- `_ENTITY_REF.debtor_id` expressions for FK column population
- Mappings for pain.001, pacs.008, camt.053

## Files Modified

| File | Purpose |
|------|---------|
| `src/gps_cdm/orchestration/message_splitter.py` | Removed extraction logic (-200 lines) |
| `src/gps_cdm/orchestration/dynamic_gold_mapper.py` | Entity INSERT + identifier routing |
| `src/gps_cdm/message_formats/iso20022/base_parser.py` | Split transaction handling |
| `src/gps_cdm/message_formats/pain001/__init__.py` | Full ISO path key support |
| `ddl/postgresql/03_gold_cdm_tables.sql` | Removed denormalized identifier columns |
| `ddl/postgresql/migrations/001_add_source_instruction_id.sql` | New migration |
| `ddl/postgresql/migrations/002_normalize_party_identifiers.sql` | New migration |
| `ddl/postgresql/migrations/003_normalize_iso_semantic_tables.sql` | New migration |

## Migration Order

Run migrations in this order:
```bash
psql -h localhost -p 5433 -U gps_cdm_svc -d gps_cdm -f ddl/postgresql/migrations/001_add_source_instruction_id.sql
psql -h localhost -p 5433 -U gps_cdm_svc -d gps_cdm -f ddl/postgresql/migrations/002_normalize_party_identifiers.sql
psql -h localhost -p 5433 -U gps_cdm_svc -d gps_cdm -f ddl/postgresql/migrations/003_normalize_iso_semantic_tables.sql
```

## Query Pattern Changes

### Before (Denormalized)
```sql
SELECT debtor_name, debtor_address_country, debtor_agent_bic
FROM gold.cdm_pacs_fi_customer_credit_transfer
WHERE transfer_id = 'xxx';
```

### After (Normalized with Joins)
```sql
SELECT
    pacs.transfer_id,
    p.name AS debtor_name,
    p.country AS debtor_country,
    fi.bic AS debtor_agent_bic
FROM gold.cdm_pacs_fi_customer_credit_transfer pacs
JOIN gold.cdm_party p ON pacs.debtor_party_id = p.party_id
JOIN gold.cdm_financial_institution fi ON pacs.debtor_agent_id = fi.fi_id
WHERE pacs.transfer_id = 'xxx';
```

## Backwards Compatibility

- Denormalized columns in ISO semantic tables are **kept temporarily**
- Both denormalized and FK columns available during transition
- Future migration (Phase 6c) will drop denormalized columns after full adoption

## Testing

Run E2E tests after migration:
```bash
python scripts/testing/e2e_format_test.py --all
python scripts/validate_zone_separated_e2e.py
```

Verify:
1. Entity records created with `source_instruction_id`
2. ISO semantic tables populated with entity FK columns
3. Identifier tables populated via `_insert_*_id` functions
