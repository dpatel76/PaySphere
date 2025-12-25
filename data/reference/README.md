# Reference Data Loading - GPS CDM

## Overview

This directory contains SQL scripts to populate reference data for the GPS (Global Payments Services) Common Domain Model, specifically:
- **Relationship to Beneficiary Codes**: 25 standardized codes (R01-R25)
- **Regulatory Purpose Codes**: 360+ jurisdiction-specific payment purpose codes

## Directory Structure

```
data/reference/
├── README.md (this file)
├── 00_master_load_reference_data.sql          # Master orchestration script
├── 01_load_relationship_to_beneficiary_codes.sql  # 25 codes (R01-R25)
├── 02_load_regulatory_purpose_codes_china.sql     # 100+ codes (Part 1 of 190)
├── 03_load_regulatory_purpose_codes_india.sql     # 80 codes (S0001-S1099)
├── 04_load_regulatory_purpose_codes_brazil.sql    # 40 codes (10101-90002)
└── 05_load_regulatory_purpose_codes_other_jurisdictions.sql  # 60+ codes
```

## Reference Data Summary

### 1. Relationship to Beneficiary Codes (25 codes)

Standardized relationship codes for remittances and cross-border payments, required by 13 APAC/Middle East/LatAm jurisdictions.

**Categories:**
- Family (R01-R09): Spouse, Parent, Child, Sibling, etc.
- Employment (R10): Employee salary payment
- Commercial (R11-R15): Customer, Supplier, Business partner, etc.
- Property (R16-R17): Landlord, Tenant
- Institutional (R18-R22): Education, Medical, Government, Charity
- Other (R23-R25): Friend, Self, Other

**Applicable Jurisdictions:** CN, IN, PH, HK, SG, TH, MY, ID, VN, AE, SA, BR, MX

**ISO 20022 Mapping:** 72% of codes (18 of 25) map to ISO 20022 External Purpose Codes (FAMI, SALA, GDDS, DIVI, LOAN, RENT, EDUC, MDCS, TAXS, CHAR)

### 2. Regulatory Purpose Codes (360+ codes across 15+ jurisdictions)

Jurisdiction-specific payment purpose codes for regulatory reporting.

| Jurisdiction | Authority | Code Count | Code Range | Key Features |
|--------------|-----------|------------|------------|--------------|
| **China (CN)** | PBoC | 190 | 121000-622999 | Trade in Goods, Services, Income, Transfers, Capital Account |
| **India (IN)** | RBI | 80 | S0001-S1099 | LRS, FEMA categories, UPI support |
| **Brazil (BR)** | BACEN | 40 | 10101-90002 | PIX nature codes, BOP categories |
| **USA (US)** | FinCEN | 8 | US001-US008 | Trade, remittances, investment |
| **UK (GB)** | FCA/BoE | 7 | UK001-UK007 | Trade, financial services, remittances |
| **Singapore (SG)** | MAS | 6 | SG001-SG006 | Trade, professional services, PayNow |
| **Hong Kong (HK)** | HKMA | 5 | HK001-HK005 | Merchandise, services, FPS |
| **Thailand (TH)** | BoT | 6 | TH001-TH006 | Trade, tourism, PromptPay |
| **Malaysia (MY)** | BNM | 5 | MY001-MY005 | Trade, Islamic finance |
| **Philippines (PH)** | BSP | 5 | PH001-PH005 | OFW remittances, BPO |
| **Indonesia (ID)** | BI | 4 | ID001-ID004 | Trade, worker remittances |
| **Vietnam (VN)** | SBV | 4 | VN001-VN004 | Trade, services, remittances |
| **UAE (AE)** | CBUAE | 6 | AE001-AE006 | Trade, Islamic finance (Murabaha, Ijara) |
| **Saudi Arabia (SA)** | SAMA | 6 | SA001-SA006 | Trade, Hajj/Umrah, Sharia compliance |
| **Mexico (MX)** | CNBV/Banxico | 5 | MX001-MX005 | Trade, family remittances, SPEI |
| **Australia (AU)** | AUSTRAC | 4 | AU001-AU004 | IFTI reporting |
| **EU** | ECB | 5 | EU001-EU005 | SEPA, SEPA Instant |

**Total:** 360+ purpose codes across 69 jurisdictions

## Execution Instructions

### Option 1: Execute Master Script (Recommended)

```sql
-- Execute from Databricks SQL Editor or notebook
!source /Users/dineshpatel/code/projects/gps_cdm/data/reference/00_master_load_reference_data.sql
```

This will:
1. Create backups of existing data (if any)
2. Truncate tables for clean load
3. Load all reference data in sequence
4. Run validation queries
5. Optimize tables with ZORDER
6. Generate summary report

### Option 2: Execute Individual Scripts

If you need to load data incrementally or troubleshoot specific jurisdictions:

```sql
-- 1. Load Relationship codes
!source 01_load_relationship_to_beneficiary_codes.sql

-- 2. Load China codes
!source 02_load_regulatory_purpose_codes_china.sql

-- 3. Load India codes
!source 03_load_regulatory_purpose_codes_india.sql

-- 4. Load Brazil codes
!source 04_load_regulatory_purpose_codes_brazil.sql

-- 5. Load other jurisdictions
!source 05_load_regulatory_purpose_codes_other_jurisdictions.sql
```

## Validation Queries

### Check Total Counts

```sql
-- Relationship codes (Expected: 25)
SELECT COUNT(*) FROM cdm_silver.relationship_to_beneficiary;

-- Purpose codes (Expected: 360+)
SELECT COUNT(*) FROM cdm_silver.regulatory_purpose_code;

-- Purpose codes by jurisdiction
SELECT jurisdiction, COUNT(*) as code_count
FROM cdm_silver.regulatory_purpose_code
GROUP BY jurisdiction
ORDER BY code_count DESC;
```

### Verify Data Quality

```sql
-- Check for duplicates (Expected: 0)
SELECT jurisdiction, code_value, COUNT(*) as dup_count
FROM cdm_silver.regulatory_purpose_code
GROUP BY jurisdiction, code_value
HAVING COUNT(*) > 1;

-- Check for NULL required fields (Expected: 0)
SELECT COUNT(*) as null_count
FROM cdm_silver.regulatory_purpose_code
WHERE jurisdiction IS NULL
   OR code_value IS NULL
   OR code_description IS NULL;

-- Check ISO 20022 mapping coverage
SELECT
  ROUND(100.0 * SUM(CASE WHEN iso20022_mapping IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) as mapping_pct
FROM cdm_silver.regulatory_purpose_code;
```

### Check Payment Type Coverage

```sql
-- Purpose codes by payment type
SELECT
  payment_type,
  COUNT(DISTINCT jurisdiction) as jurisdiction_count,
  COUNT(*) as code_count
FROM cdm_silver.regulatory_purpose_code
LATERAL VIEW explode(applicable_payment_types) exploded AS payment_type
GROUP BY payment_type
ORDER BY code_count DESC;

-- Expected payment types:
-- SWIFT, Wire, ACH, PIX, UPI, PromptPay, PayNow, Mobile, RTGS, SEPA, etc.
```

## Data Refresh Schedule

### Quarterly Review Process

Reference data should be reviewed and updated quarterly to capture:
1. New regulatory purpose codes from central banks
2. Changes to existing codes (deprecation, effective dates)
3. New jurisdictions or payment systems
4. ISO 20022 mapping updates

**Recommended Schedule:**
- **Q1 (January):** Review China PBoC, India RBI codes
- **Q2 (April):** Review Brazil BACEN, Mexico CNBV codes
- **Q3 (July):** Review APAC codes (SG, HK, TH, MY, PH, ID, VN)
- **Q4 (October):** Review Middle East (UAE, SA), Australia, EU codes

### Change Management Process

1. **Identify Changes:** Monitor regulatory authority announcements
2. **Update Scripts:** Modify relevant SQL scripts with new/changed codes
3. **Test in Dev:** Execute in development environment
4. **Validate:** Run data quality checks
5. **Deploy to QA:** Test with payment validation pipeline
6. **Deploy to Prod:** Schedule maintenance window for production update
7. **Document:** Update this README with version history

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-12-18 | Data Architecture Team | Initial load: 25 relationship codes + 360+ purpose codes |

## Schema References

- **Relationship to Beneficiary Schema:** `/schemas/08_relationship_to_beneficiary_schema.json`
- **Regulatory Purpose Code Schema:** `/schemas/07_regulatory_purpose_code_schema.json`
- **DDL Scripts:**
  - `/ddl/06_create_regulatorypurposecode_entity.sql`
  - `/ddl/07_create_relationshiptobeneficiary_entity.sql`

## Integration Points

### Payment Validation Pipeline

Reference data is consumed by:
1. **Payment Instruction Validator:** Validates `purposeCode` and `relationshipToBeneficiary` fields
2. **Regulatory Reporting Engine:** Maps payment purpose to regulatory categories
3. **ISO 20022 Translator:** Maps proprietary codes to ISO 20022 External Purpose Codes

### API Endpoints

```
GET /api/v1/reference-data/purpose-codes?jurisdiction=CN
GET /api/v1/reference-data/purpose-codes?jurisdiction=IN&category=LRS
GET /api/v1/reference-data/relationship-codes?jurisdiction=SG
```

## Data Governance

### Data Stewardship

**Data Owner:** Global Payments Compliance Team
**Data Steward:** Regional Compliance Managers (by jurisdiction)
**Technical Owner:** Data Architecture Team

### Data Quality Rules

1. **Uniqueness:** (jurisdiction, code_value) must be unique for purpose codes
2. **Completeness:** Required fields cannot be NULL
3. **Validity:** Effective dates must be logical (effective_from <= effective_to)
4. **Referential Integrity:** ISO 20022 mappings must be valid External Purpose Codes
5. **Consistency:** Jurisdiction codes must match ISO 3166-1 alpha-2

### Audit Trail

All reference data changes are tracked via:
- `created_timestamp`: When code was first loaded
- `last_updated_timestamp`: When code was last modified
- Version control: All SQL scripts are versioned in Git

## Support

For questions or issues with reference data loading:
- **Technical Issues:** Contact Data Architecture Team
- **Regulatory Questions:** Contact Global Payments Compliance
- **Code Changes:** Submit PR to GPS CDM repository

## Related Documentation

- [Schema Coverage Reconciliation](/SCHEMA_COVERAGE_RECONCILIATION.md)
- [Cloud Adoption Strategy](/documents/strategy/approach_03_cloud_adoption.md)
- [Physical Data Model](/documents/physical_model_regulatory_enhanced.md)
- [Regulatory Requirements Landscape](/documents/regulatory_global_comprehensive_landscape.md)

---

**Last Updated:** 2024-12-18
**Next Review Date:** Q1 2025
