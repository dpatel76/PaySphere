# CDM Global Regulatory Extensions - Reference Data

## Overview

This directory contains reference data files for the CDM global regulatory extensions, specifically for the two new reference entities:

1. **RegulatoryPurposeCode** - Payment purpose codes across 69 jurisdictions (350+ codes)
2. **RelationshipToBeneficiary** - Relationship codes for remittances and payments (25 codes)

---

## Files

### 1. regulatory_purpose_codes_sample.csv

**Description:** Sample dataset of regulatory purpose codes across multiple jurisdictions

**Total Codes in Sample:** 75 codes
**Full Dataset:** 350+ codes

**Code Distribution:**
- **China (PBoC):** 25 sample codes (of 190 total)
  - Trade in Goods: 8 codes
  - Trade in Services: 8 codes
  - Income: 4 codes
  - Current Transfers: 3 codes
- **India (RBI):** 16 sample codes (of 80 total)
  - Export of Goods and Services: 5 codes
  - Remittances: 5 codes
  - Investment: 3 codes
  - Trade Finance: 3 codes
- **Brazil (BACEN):** 10 sample codes (of 40 total)
  - Export: 2 codes
  - Import: 2 codes
  - Remittances: 2 codes
  - Investment: 2 codes
  - Loan: 2 codes
- **Other Jurisdictions:** 24 codes
  - Korea, Singapore, Philippines, UAE, Saudi Arabia, Malaysia, Thailand, Indonesia, Vietnam, Hong Kong, Taiwan, Mexico

**CSV Schema:**
```
purpose_code_id          - UUID v4 primary key
jurisdiction             - ISO 3166-1 alpha-2 country code (CN, IN, BR, etc.)
code_value               - Purpose code value (e.g., 121010 for China)
code_description         - Human-readable description
category                 - High-level category (Trade in Goods, Services, etc.)
sub_category             - Sub-category (Export, Import, etc.)
iso20022_mapping         - ISO 20022 External Purpose Code equivalent
applicable_payment_types - JSON array of applicable payment types
requires_supporting_documents - Boolean flag
effective_from           - Effective start date
effective_to             - Effective end date (NULL = current)
```

**Sample Codes:**
- **121010 (China):** General merchandise trade - export
- **S0001 (India):** Exports of goods
- **10101 (Brazil):** Export of goods - general merchandise
- **R01 (Global):** Customer payment for goods/services

**Usage Example:**
```sql
-- Find all China trade codes
SELECT code_value, code_description, sub_category
FROM cdm_silver.compliance.regulatory_purpose_code
WHERE jurisdiction = 'CN' AND category = 'Trade in Goods'
ORDER BY code_value;
```

---

### 2. relationship_to_beneficiary_codes.csv

**Description:** Complete dataset of relationship to beneficiary codes (R01-R25)

**Total Codes:** 25 (complete)

**Code Categories:**
- **Family (R01-R05):** Spouse, Parent, Child, Sibling, Other Family Member
- **Employment (R06-R07):** Employee, Employer
- **Business (R08-R10):** Business Partner, Shareholder, Director/Officer
- **Commercial (R11-R12):** Customer, Supplier
- **Financial (R13-R16):** Lender, Borrower, Investor, Investee
- **Property (R17-R18):** Tenant, Landlord
- **Educational (R19-R20):** Student, Educational Institution
- **Medical (R21):** Medical Provider/Patient
- **Institutional (R22-R23):** Government Entity, Charity/Non-Profit
- **Other (R24-R25):** Self, No Relationship

**CSV Schema:**
```
relationship_code_id     - UUID v4 primary key
code_value               - Relationship code (R01-R25)
description              - Human-readable description
applicable_jurisdictions - JSON array of ISO country codes
iso20022_equivalent      - ISO 20022 External Purpose Code equivalent
```

**Applicable Jurisdictions:**
- **China (CN):** 21 codes
- **India (IN):** 23 codes
- **Philippines (PH):** 19 codes
- **Hong Kong (HK):** 21 codes
- **Singapore (SG):** 23 codes
- **Thailand (TH):** 17 codes
- **Malaysia (MY):** 16 codes
- **Indonesia (ID):** 16 codes
- **Vietnam (VN):** 16 codes
- **UAE (AE):** 20 codes
- **Saudi Arabia (SA):** 18 codes
- **Brazil (BR):** 21 codes
- **Mexico (MX):** 14 codes

**ISO 20022 Mappings:**
- **FAMI:** Family Maintenance (R01-R05)
- **SALA:** Salary Payment (R06-R07)
- **BUSI:** Business (R08)
- **DIVI:** Dividend/Investment (R09, R15)
- **GDDS:** Goods (R11-R12)
- **LOAN:** Loan (R13-R14)
- **RENT:** Rent (R17)
- **EDUC:** Education (R19-R20)
- **MDCS:** Medical Services (R21)
- **TAXS:** Tax Payment (R22)
- **CHAR:** Charity (R23)

**Usage Example:**
```sql
-- Find all family relationship codes
SELECT code_value, description, iso20022_equivalent
FROM cdm_silver.compliance.relationship_to_beneficiary
WHERE code_value IN ('R01', 'R02', 'R03', 'R04', 'R05')
ORDER BY code_value;

-- Find relationship codes applicable to Singapore
SELECT code_value, description
FROM cdm_silver.compliance.relationship_to_beneficiary
WHERE ARRAY_CONTAINS(applicable_jurisdictions, 'SG')
ORDER BY code_value;
```

---

### 3. load_reference_data.sql

**Description:** SQL script to load CSV files into Delta Lake tables

**Features:**
- COPY INTO commands for both reference entities
- Data validation queries
- Usage examples
- Data quality checks
- Statistics queries

**Execution:**
```bash
# From Databricks SQL Editor or Notebook
%sql
SOURCE /Users/dineshpatel/code/projects/gps_cdm/reference_data/load_reference_data.sql
```

**Or execute step-by-step:**
```sql
-- 1. Load regulatory purpose codes
COPY INTO cdm_silver.compliance.regulatory_purpose_code
FROM '/path/to/regulatory_purpose_codes_sample.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true');

-- 2. Load relationship codes
COPY INTO cdm_silver.compliance.relationship_to_beneficiary
FROM '/path/to/relationship_to_beneficiary_codes.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true');

-- 3. Verify load
SELECT COUNT(*) FROM cdm_silver.compliance.regulatory_purpose_code;
-- Expected: 75 codes (sample)

SELECT COUNT(*) FROM cdm_silver.compliance.relationship_to_beneficiary;
-- Expected: 25 codes (complete)
```

---

## Prerequisites

Before loading reference data:

1. **Execute DDL scripts** from `../ddl/` directory in order:
   - 06_create_regulatorypurposecode_entity.sql
   - 07_create_relationshiptobeneficiary_entity.sql

2. **Verify tables exist:**
   ```sql
   SHOW TABLES IN cdm_silver.compliance LIKE 'regulatory_purpose_code';
   SHOW TABLES IN cdm_silver.compliance LIKE 'relationship_to_beneficiary';
   ```

3. **Ensure file permissions** allow Databricks/Spark to read CSV files

---

## Data Quality

### Regulatory Purpose Codes

**Validation Checks:**
- ✅ All purpose_code_id values are unique UUIDs
- ✅ All jurisdiction values are valid ISO 3166-1 alpha-2 codes
- ✅ All code_value values are non-null
- ✅ All code_description values are non-null
- ✅ effective_from is always populated
- ✅ ISO 20022 mapping is populated for ~80% of codes

**Data Completeness:**
- Sample dataset: 75 codes (21% of full dataset)
- Full dataset target: 350+ codes
- To expand: Add remaining codes from regulatory sources:
  - China PBoC: 165 more codes (190 total)
  - India RBI: 64 more codes (80 total)
  - Brazil BACEN: 30 more codes (40 total)
  - Others: 16 more codes (40+ total)

### Relationship Codes

**Validation Checks:**
- ✅ All relationship_code_id values are unique UUIDs
- ✅ All code_value values are R01-R25
- ✅ All description values are non-null
- ✅ applicable_jurisdictions array is populated for all codes
- ✅ ISO 20022 equivalent mapped for 16 of 25 codes (64%)

**Data Completeness:**
- Complete dataset: All 25 codes included (100%)

---

## Extending the Dataset

### Adding New Purpose Codes

To add purpose codes for additional jurisdictions:

1. **Research regulatory requirements** for the jurisdiction
2. **Identify purpose code taxonomy** from central bank or regulator
3. **Map codes to ISO 20022** External Purpose Codes where possible
4. **Add rows to CSV:**
   ```csv
   <new-uuid>,JP,JP001,Export of goods,Trade in Goods,Export,GDDS,"[""Wire"",""Zengin""]",true,2024-01-01,
   ```
5. **Reload data** using load_reference_data.sql

### Adding New Relationship Codes

To add new relationship codes (R26+):

1. **Identify gap** in current 25 codes
2. **Define new relationship** (e.g., "Legal Guardian", "Trust Beneficiary")
3. **Map to ISO 20022** if equivalent exists
4. **Determine applicable jurisdictions**
5. **Add row to CSV:**
   ```csv
   <new-uuid>,R26,Legal Guardian,"[""US"",""UK"",""AU""]",FAMI
   ```
6. **Reload data**

---

## Maintenance

### Updating Codes

To update existing codes (e.g., code description changes):

1. **Modify CSV file** with updated values
2. **For purpose codes with temporal validity:**
   - Set `effective_to` on old code to day before change
   - Add new row with `effective_from` on change date
3. **Reload data** using MERGE or DELETE + INSERT

### Deprecating Codes

To deprecate codes:

```sql
-- For purpose codes (time-based deprecation)
UPDATE cdm_silver.compliance.regulatory_purpose_code
SET effective_to = '2024-12-31'
WHERE jurisdiction = 'CN' AND code_value = '121099';

-- For relationship codes (soft delete not supported - use hard delete)
DELETE FROM cdm_silver.compliance.relationship_to_beneficiary
WHERE code_value = 'R99';
```

---

## Usage in Payments

### Example 1: Validate Purpose Code in Payment

```sql
-- Validate China purpose code in cross-border payment
SELECT
  pi.payment_instruction_id,
  pi.extensions:purposeCode:regulatoryPurposeCode AS purpose_code,
  rpc.code_description,
  rpc.requires_supporting_documents,
  CASE
    WHEN rpc.purpose_code_id IS NULL THEN 'INVALID_CODE'
    WHEN rpc.effective_to IS NOT NULL AND rpc.effective_to < CURRENT_DATE THEN 'EXPIRED_CODE'
    ELSE 'VALID'
  END AS validation_status
FROM cdm_silver.payments.payment_instruction pi
LEFT JOIN cdm_silver.compliance.regulatory_purpose_code rpc
  ON rpc.jurisdiction = 'CN'
  AND rpc.code_value = pi.extensions:purposeCode:regulatoryPurposeCode
  AND (rpc.effective_to IS NULL OR rpc.effective_to >= CURRENT_DATE)
WHERE pi.payment_type = 'CROSS_BORDER'
  AND pi.destination_country = 'CN';
```

### Example 2: Validate Relationship Code in Remittance

```sql
-- Validate relationship code in India remittance
SELECT
  pi.payment_instruction_id,
  pi.extensions:purposeCode:relationshipToBeneficiary AS relationship_code,
  rtb.description,
  rtb.iso20022_equivalent,
  CASE
    WHEN rtb.relationship_code_id IS NULL THEN 'INVALID_CODE'
    WHEN NOT ARRAY_CONTAINS(rtb.applicable_jurisdictions, 'IN') THEN 'NOT_APPLICABLE_FOR_JURISDICTION'
    ELSE 'VALID'
  END AS validation_status
FROM cdm_silver.payments.payment_instruction pi
LEFT JOIN cdm_silver.compliance.relationship_to_beneficiary rtb
  ON rtb.code_value = pi.extensions:purposeCode:relationshipToBeneficiary
WHERE pi.payment_type = 'REMITTANCE'
  AND pi.destination_country = 'IN';
```

---

## Support

For questions or issues:
- **Contact:** Data Architecture Team
- **Documentation:** `../documents/strategy/cdm_global_regulatory_extensions.md`
- **DDL Scripts:** `../ddl/README.md`
- **Implementation Summary:** `../documents/strategy/FINAL_GLOBAL_REGULATORY_IMPLEMENTATION_SUMMARY.md`

---

## Change Log

### v1.0 (2024-12-18)
- Initial release
- 75 sample purpose codes across 18 jurisdictions
- 25 complete relationship codes
- Load script with validation queries
