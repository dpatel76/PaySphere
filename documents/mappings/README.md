# GPS CDM - Standards and Reports Mappings

## Overview

This directory contains comprehensive field-level mappings between payment industry standards, regulatory reports, and the GPS (Global Payments Services) Common Domain Model (CDM).

**Goal:** 100% field coverage for all payment standards and regulatory reports

---

## Directory Structure

```
documents/mappings/
├── README.md (this file)
├── MAPPING_COVERAGE_SUMMARY.md           # Overall progress tracking
├── standards/                            # Payment message standards
│   ├── ISO20022_pain001_CustomerCreditTransfer_Mapping.md
│   ├── ISO20022_pacs008_FICreditTransfer_Mapping.md
│   ├── SWIFT_MT103_SingleCustomerCreditTransfer_Mapping.md
│   ├── Fedwire_FundsTransfer_Mapping.md
│   ├── NACHA_ACH_CreditDebit_Mapping.md
│   ├── SEPA_SCT_CreditTransfer_Mapping.md
│   ├── PIX_InstantPayment_Mapping.md
│   ├── UPI_Payment_Mapping.md
│   └── ... (additional standards)
└── reports/                              # Regulatory reporting
    ├── FinCEN_CTR_CurrencyTransactionReport_Mapping.md
    ├── FinCEN_SAR_SuspiciousActivityReport_Mapping.md
    ├── AUSTRAC_IFTI_InternationalFundsTransfer_Mapping.md
    ├── FATCA_Form8966_Mapping.md
    ├── CRS_Reporting_Mapping.md
    ├── UK_SAR_SuspiciousActivityReport_Mapping.md
    └── ... (additional reports)
```

---

## Naming Convention

### Payment Standards
**Format:** `{Standard}_{MessageType}_{Description}_Mapping.md`

**Examples:**
- `ISO20022_pain001_CustomerCreditTransfer_Mapping.md`
- `SWIFT_MT103_SingleCustomerCreditTransfer_Mapping.md`
- `Fedwire_FundsTransfer_Mapping.md`

### Regulatory Reports
**Format:** `{Authority}_{ReportCode}_{ReportName}_Mapping.md`

**Examples:**
- `FinCEN_CTR_CurrencyTransactionReport_Mapping.md`
- `AUSTRAC_IFTI_InternationalFundsTransfer_Mapping.md`
- `FATCA_Form8966_Mapping.md`

---

## Mapping Document Template

Each mapping document includes:

### 1. Header
- Standard/Report name
- Version
- Regulatory authority (for reports)
- Total field count
- Mapping coverage percentage
- Last updated date

### 2. Overview
- Purpose and usage
- When to send/file
- Regulatory requirements (for reports)

### 3. Mapping Statistics
```markdown
| Metric | Count | Percentage |
|--------|-------|------------|
| Total Fields | X | 100% |
| Mapped to CDM | X | 100% |
| Direct Mapping | X | XX% |
| Derived/Calculated | X | XX% |
| Reference Data Lookup | X | XX% |
| CDM Gaps Identified | 0 | 0% |
```

### 4. Field-by-Field Mapping
Complete table with all fields:
- Field number/XPath/Tag
- Field name
- Data type
- Length/format
- Cardinality/Required
- Valid values
- CDM Entity
- CDM Attribute
- Mapping notes

### 5. CDM Gaps (if any)
- Fields that don't map to existing CDM
- Proposed CDM enhancements
- Justification for gaps

### 6. Code Lists and Valid Values
- All enumerations
- External code list references
- Examples

### 7. Message/Report Example
- Sample XML/text showing structure
- Real-world example

### 8. References
- Official specifications
- Related messages/reports
- CDM schemas

---

## How to Use This Directory

### For Data Architects
1. Review mapping documents to understand CDM coverage
2. Identify gaps requiring CDM schema enhancements
3. Validate mappings against specifications
4. Update mappings when standards/reports change

### For Developers
1. Use mappings to implement transformations
2. Reference field mappings for data ingestion
3. Validate message parsing logic
4. Implement regulatory report generation

### For Compliance Officers
1. Verify regulatory requirements are captured
2. Validate report field mappings
3. Ensure all jurisdictions are covered
4. Review audit trail for regulatory changes

### For Product Managers
1. Understand payment standard support
2. Validate business requirements are met
3. Plan for new standards/reports
4. Communicate coverage to stakeholders

---

## Coverage Status

See [MAPPING_COVERAGE_SUMMARY.md](MAPPING_COVERAGE_SUMMARY.md) for:
- Overall progress (X% complete)
- Standards completed vs pending
- Reports completed vs pending
- Field counts by entity
- Timeline and targets

**Current Status:**
- ✅ **2 mappings completed** (273 fields, 100% coverage)
- 🔄 **0 mappings in progress**
- ⏸️ **25 mappings pending** (~2,285 fields)

---

## Mapping Principles

### 1. Completeness
- **100% field coverage** - every field must be mapped
- Include optional fields, not just required fields
- Document all code lists and valid values

### 2. Accuracy
- Use official specifications as source of truth
- Validate field names, types, and cardinality
- Cross-reference with regulatory guidance

### 3. Traceability
- Maintain clear linkage from standard/report to CDM
- Document mapping type (direct, derived, lookup)
- Explain complex transformations

### 4. Maintainability
- Keep mappings up-to-date with version changes
- Document version history
- Link to CDM schema files

---

## CDM Entity Reference

### Core Entities

| Entity | Purpose | Primary Use Cases |
|--------|---------|-------------------|
| **PaymentInstruction** | Payment message data | pain.001, MT103, Fedwire, ACH, etc. |
| **Party** | Customer/counterparty information | Debtor, Creditor, Ultimate parties |
| **Account** | Bank account details | Debtor/creditor accounts |
| **FinancialInstitution** | Bank/FI information | Agents, intermediaries |
| **RegulatoryReport** | Regulatory filing data | CTR, SAR, IFTI, FATCA, etc. |
| **ComplianceCase** | Investigation/case data | SAR cases, AML alerts |

### Extensions

| Extension | Purpose | Fields |
|-----------|---------|--------|
| **PaymentInstruction.extensions** | Regulatory-specific fields | 104 fields |
| **Party.extensions** | Tax/KYC fields | 31 fields |
| **Account.extensions** | FATCA/CRS fields | 10 fields |

See `/schemas/` for complete entity definitions.

---

## Gap Analysis Process

When a field doesn't map to CDM:

1. **Document the Gap**
   - Record in mapping document
   - Add to CDM Gaps section
   - Note field name, type, and purpose

2. **Analyze Requirement**
   - Is field mandatory or optional?
   - How many standards/reports need it?
   - Business criticality?

3. **Propose Solution**
   - Add to existing entity?
   - Create new extension field?
   - Use supplementaryData?

4. **Update CDM**
   - Modify JSON schema
   - Update DDL script
   - Update documentation
   - Re-validate mapping

5. **Track in Summary**
   - Update MAPPING_COVERAGE_SUMMARY.md
   - Record enhancement in change log
   - Communicate to stakeholders

---

## Quality Assurance

### Validation Checklist

Before marking a mapping as complete:

- ☐ All fields from specification are included
- ☐ Field names match official specification
- ☐ Data types are correct
- ☐ Cardinality/required status is correct
- ☐ All code lists are documented
- ☐ Valid values are enumerated
- ☐ CDM entity and attribute are specified
- ☐ Example message/report is provided
- ☐ References to specs are included
- ☐ Mapping coverage is 100%
- ☐ No undocumented gaps
- ☐ Reviewed by SME

### Review Process

1. **Self-Review** (Data Architect)
   - Validate against specification
   - Check completeness and accuracy

2. **Peer Review** (Another Data Architect)
   - Cross-check field mappings
   - Validate CDM attribute choices

3. **SME Review** (Product/Compliance)
   - Validate business requirements
   - Confirm regulatory interpretation

4. **Final Approval** (Lead Architect)
   - Sign off on mapping
   - Publish to repository
   - Update summary document

---

## Maintenance Schedule

### Quarterly Review
- Check for standard/report version updates
- Review regulatory changes
- Validate CDM schema alignment
- Update mappings as needed

### Annual Audit
- Comprehensive review of all mappings
- Verify all standards are current versions
- Validate regulatory compliance
- Re-test sample transformations

### Ad-Hoc Updates
- When standards release new versions
- When regulators issue new guidance
- When CDM schema changes
- When gaps are discovered

---

## Tools and Automation

### Mapping Validation Script
```bash
# Validate mapping document completeness
./scripts/validate_mapping.sh documents/mappings/standards/ISO20022_pain001_CustomerCreditTransfer_Mapping.md
```

### Coverage Report Generator
```bash
# Generate coverage summary report
./scripts/generate_coverage_report.sh
```

### Gap Analysis Tool
```bash
# Identify fields not mapped to CDM
./scripts/find_mapping_gaps.sh
```

---

## Contribution Guidelines

### Adding a New Mapping

1. **Create Document**
   - Use naming convention
   - Follow template structure
   - Place in correct subdirectory (standards/ or reports/)

2. **Complete All Sections**
   - Header with metadata
   - Overview
   - Statistics table
   - Field-by-field mapping table
   - CDM gaps (if any)
   - Code lists
   - Example
   - References

3. **Validate**
   - Run validation script
   - Ensure 100% field coverage
   - Check for CDM gaps

4. **Update Summary**
   - Add to MAPPING_COVERAGE_SUMMARY.md
   - Update statistics
   - Update completion percentage

5. **Submit for Review**
   - Create pull request
   - Assign reviewers
   - Address feedback

---

## Contact

For questions or issues with mappings:

- **Mapping Questions:** Contact Data Architecture Team
- **Standard Interpretation:** Contact Payments Product Team
- **Regulatory Questions:** Contact Compliance Team
- **CDM Schema Issues:** Contact Data Architecture Team

---

## References

### External Specifications
- ISO 20022: https://www.iso20022.org/
- SWIFT: https://www.swift.com/standards
- Fedwire: https://www.frbservices.org/
- NACHA: https://www.nacha.org/
- FinCEN: https://www.fincen.gov/
- AUSTRAC: https://www.austrac.gov.au/

### Internal Documentation
- [MAPPING_COVERAGE_SUMMARY.md](MAPPING_COVERAGE_SUMMARY.md) - Overall progress tracking
- [Schema Coverage Reconciliation](/SCHEMA_COVERAGE_RECONCILIATION.md) - CDM schema validation
- [Physical Data Model](/documents/physical_model_regulatory_enhanced.md) - Database design
- [CDM Schemas](/schemas/) - JSON schema definitions

---

**Last Updated:** 2024-12-18
**Next Review:** Weekly (until 100% complete)
**Document Owner:** Data Architecture Team
