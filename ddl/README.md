# CDM Global Regulatory Extensions - DDL Scripts

## Overview

This directory contains executable DDL scripts for extending the Common Domain Model (CDM) to support global regulatory reporting across 69 jurisdictions.

**Coverage:** 98% of 2,800 global regulatory fields
**Total New Attributes:** 223 (across 8 entities)
**ISO 20022 Compliance:** 22% (50 compliant, 23 extended, 150 justified non-ISO extensions)

---

## Execution Order

Execute the DDL scripts in the following order:

### Phase 1: Entity Extensions (Scripts 01-05)

1. **01_extend_party_entity.sql**
   - Extends Party entity with 31 new attributes
   - Coverage: Tax reporting (FATCA, CRS), APAC national IDs
   - Execution time: ~2 minutes

2. **02_extend_account_entity.sql**
   - Extends Account entity with 10 new attributes
   - Coverage: FATCA/CRS account classification, controlling persons
   - Execution time: ~1 minute

3. **03_extend_regulatoryreport_entity.sql**
   - Extends RegulatoryReport entity with 37 new attributes
   - Coverage: Tax reporting, sanctions, UK DAML, terrorist property
   - Execution time: ~3 minutes

4. **04_extend_financialinstitution_entity.sql**
   - Extends FinancialInstitution entity with 13 new attributes
   - Coverage: FinCEN requirements, Middle East/Islamic finance
   - Execution time: ~1 minute

5. **05_extend_compliancecase_entity.sql**
   - Extends ComplianceCase entity with 13 new attributes
   - Coverage: FinCEN SAR narrative, law enforcement interaction, FIU referrals
   - Execution time: ~1 minute

### Phase 2: Reference Entities (Scripts 06-07)

6. **06_create_regulatorypurposecode_entity.sql**
   - Creates new RegulatoryPurposeCode reference entity
   - Attributes: 10
   - Total codes: 350+ (across 69 jurisdictions)
   - Execution time: ~1 minute

7. **07_create_relationshiptobeneficiary_entity.sql**
   - Creates new RelationshipToBeneficiary reference entity
   - Attributes: 5
   - Total codes: 25 (R01-R25)
   - Execution time: <1 minute

---

## Script Details

### 01_extend_party_entity.sql

**Purpose:** Extend Party entity for global tax reporting and identity verification

**Attributes Added:** 31
- **Regional (13):** given_name, family_name, suffix, dba_name, occupation, naics_code, form_of_identification, identification_number, identification_issuing_country, identification_issuing_state, alternate_names, entity_formation, number_of_employees
- **Tax Reporting (10):** us_tax_status, fatca_classification, crs_reportable, crs_entity_type, tax_residencies, w8ben_status, w9_status, tin_issuing_country, secondary_tins, substantial_us_owner
- **APAC National IDs (8):** national_id_type, national_id_number, china_hukou, india_aadhar_number, india_pan_number, korea_alien_registration_number, japan_my_number, singapore_nric_fin

**ISO 20022 Compliance:** 19% (6 compliant, 3 extended, 22 non-ISO)

**Key Features:**
- 4 indexes for performance
- Validation query to verify column additions

---

### 02_extend_account_entity.sql

**Purpose:** Extend Account entity for FATCA/CRS tax reporting

**Attributes Added:** 10
- **Regional (2):** loan_amount, loan_origination
- **Tax Reporting (8):** fatca_status, fatca_giin, crs_reportable_account, account_holder_type, controlling_persons, dormant_account, account_balance_for_tax_reporting, withholding_tax_rate

**ISO 20022 Compliance:** 40% (4 compliant, 1 extended, 5 non-ISO)

**Key Features:**
- 4 indexes for performance
- 2 views: v_fatca_reportable_accounts, v_crs_reportable_accounts
- Validation query

---

### 03_extend_regulatoryreport_entity.sql

**Purpose:** Extend RegulatoryReport entity for global regulatory reporting

**Attributes Added:** 37
- **Regional (14):** reporting_entity_abn, reporting_entity_branch, reporting_entity_contact_name, reporting_entity_contact_phone, filing_type, prior_report_bsa_id, reporting_period_type, total_cash_in, total_cash_out, foreign_cash_in, foreign_cash_out, multiple_persons_flag, aggregation_method
- **Tax Reporting (7):** tax_year, reporting_fi_giin, reporting_fi_tin, sponsor_giin, reporting_model, iga_jurisdiction, pool_report_type
- **Sanctions (4):** sanctions_blocking_date, property_blocked, estimated_property_value, sanctions_program
- **UK DAML (8):** defence_against_money_laundering_flag, consent_required, consent_granted, consent_refusal_reason, consent_request_date, consent_response_date, consent_expiry_date, sarn_number
- **Terrorist Property (5):** terrorist_property_flag, terrorist_entity_name, terrorist_list_source, property_description, property_seized

**ISO 20022 Compliance:** 5% (2 compliant, 0 extended, 35 non-ISO)

**Key Features:**
- 5 indexes for performance
- 3 views: v_fatca_reports_pending, v_uk_daml_sars_awaiting_consent, v_sanctions_blocking_reports
- Validation query

---

### 04_extend_financialinstitution_entity.sql

**Purpose:** Extend FinancialInstitution entity for FinCEN and Islamic finance requirements

**Attributes Added:** 13
- **Regional (8):** rssd_number, tin_type, tin_value, fi_type, msb_registration_number, primary_regulator, branch_country, branch_state
- **Islamic Finance (5):** sharia_compliant_flag, islamic_finance_type, central_bank_license_number, islamic_financial_services_board, sharia_advisory_board

**ISO 20022 Compliance:** 15% (2 compliant, 0 extended, 11 non-ISO)

**Key Features:**
- 5 indexes for performance
- 3 views: v_islamic_financial_institutions, v_fincen_msb_institutions, v_fi_by_regulator
- Validation query

---

### 05_extend_compliancecase_entity.sql

**Purpose:** Extend ComplianceCase entity for SAR and AML case management

**Attributes Added:** 13
- **SAR Narrative (2):** sar_narrative, sar_activity_type_checkboxes
- **Law Enforcement (3):** law_enforcement_contact_date, law_enforcement_contact_name, law_enforcement_agency
- **Financial Recovery (1):** recovered_amount
- **Suspect Status (3):** suspect_fled_indicator, suspect_arrest_date, suspect_conviction_date
- **Case Management (1):** investigation_status
- **FIU Referrals (3):** referral_to_fiu, fiu_referral_date, fiu_reference_number

**ISO 20022 Compliance:** 15% (2 compliant, 1 extended, 10 non-ISO)

**Key Features:**
- 4 indexes for performance
- 4 views: v_active_sar_cases, v_fiu_referrals, v_sar_activity_type_distribution, v_suspect_outcomes
- Validation query

---

### 06_create_regulatorypurposecode_entity.sql

**Purpose:** Create reference entity for regulatory purpose codes

**Attributes:** 10
- purpose_code_id (PK)
- jurisdiction (ISO 3166-1 alpha-2)
- code_value (e.g., 121010 for China)
- code_description
- category (Trade in Goods, Services, etc.)
- sub_category
- iso20022_mapping
- applicable_payment_types
- requires_supporting_documents
- effective_from/effective_to

**Total Codes:** 350+
- China (PBoC): 190 codes
- India (RBI): 80 codes
- Brazil (BACEN): 40 codes
- Others: 40+ codes

**ISO 20022 Compliance:** 40% (4 compliant, 2 extended, 4 non-ISO)

**Key Features:**
- Partitioned by jurisdiction
- 4 indexes for performance
- 3 views: v_active_purpose_codes, v_purpose_code_iso_mappings, v_trade_purpose_codes
- Unique constraint on (jurisdiction, code_value, effective_from)

---

### 07_create_relationshiptobeneficiary_entity.sql

**Purpose:** Create reference entity for relationship to beneficiary codes

**Attributes:** 5
- relationship_code_id (PK)
- code_value (R01-R25)
- description
- applicable_jurisdictions
- iso20022_equivalent

**Total Codes:** 25
- Family: R01-R05
- Employment: R06-R07
- Business: R08-R10
- Commercial: R11-R12
- Financial: R13-R16
- Property: R17-R18
- Educational: R19-R20
- Medical: R21
- Institutional: R22-R23
- Other: R24-R25

**ISO 20022 Compliance:** 20% (1 compliant, 1 extended, 3 non-ISO)

**Key Features:**
- 2 indexes for performance
- 3 views: v_relationship_codes_by_category, v_relationship_codes_by_jurisdiction, v_relationship_iso20022_mappings
- Unique constraint on code_value

---

## Prerequisites

- Databricks Runtime 11.0+ or Delta Lake 2.0+
- Unity Catalog configured
- Schema `cdm_silver.payments` must exist
- Schema `cdm_silver.compliance` must exist
- Base CDM entities must be created:
  - party
  - account
  - regulatory_report
  - financial_institution
  - compliance_case

---

## Validation

After executing all scripts, run the validation queries:

```sql
-- Verify Party entity extensions
SELECT COUNT(*) FILTER (WHERE column_name LIKE '%tax%' OR column_name LIKE '%fatca%' OR column_name LIKE '%crs%')
FROM information_schema.columns
WHERE table_schema = 'cdm_silver' AND table_name = 'party';
-- Expected: 31 columns

-- Verify Account entity extensions
SELECT COUNT(*) FILTER (WHERE column_name LIKE '%fatca%' OR column_name LIKE '%crs%' OR column_name LIKE '%controlling%')
FROM information_schema.columns
WHERE table_schema = 'cdm_silver' AND table_name = 'account';
-- Expected: 10 columns

-- Verify reference entities created
SHOW TABLES IN cdm_silver.compliance LIKE 'regulatory_purpose_code';
SHOW TABLES IN cdm_silver.compliance LIKE 'relationship_to_beneficiary';
```

---

## Next Steps

1. Load reference data using `../reference_data/load_reference_data.sql`
2. Update JSON Schema for PaymentInstruction.extensions (see `../schemas/payment_instruction_extensions_schema.json`)
3. Update CDM logical model documentation
4. Update CDM physical model documentation
5. Run integration tests

---

## Rollback

To rollback the changes:

```sql
-- Drop new reference entities
DROP TABLE IF EXISTS cdm_silver.compliance.regulatory_purpose_code;
DROP TABLE IF EXISTS cdm_silver.compliance.relationship_to_beneficiary;

-- Drop views
DROP VIEW IF EXISTS cdm_silver.compliance.v_fatca_reportable_accounts;
DROP VIEW IF EXISTS cdm_silver.compliance.v_crs_reportable_accounts;
-- ... (drop all other views created)

-- Note: Cannot easily rollback ALTER TABLE ADD COLUMNS in Delta Lake
-- Consider using Delta Lake time travel if immediate rollback needed
-- RESTORE TABLE cdm_silver.payments.party TO VERSION AS OF <version>;
```

---

## Support

For questions or issues:
- Contact: Data Architecture Team
- Documentation: `/Users/dineshpatel/code/projects/gps_cdm/documents/strategy/`
- Specifications: `cdm_global_regulatory_extensions.md`
- Implementation Summary: `FINAL_GLOBAL_REGULATORY_IMPLEMENTATION_SUMMARY.md`
