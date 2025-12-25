# GPS CDM Regulatory Requirement Registry

## Overview

This registry contains structured definitions of all regulatory requirements for payment reporting. Each requirement is catalogued with full metadata, source citations, and implementation guidance for DSL traceability.

## Registry Statistics

| Metric | Count |
|--------|-------|
| **Total Requirements** | 487 |
| **Regulators** | 8 |
| **Report Types** | 13 |
| **Jurisdictions** | 6 (US, AU, UK, EU, International, Multiple) |

## Reports Covered

| Report | Regulator | Jurisdiction | Requirements | Status |
|--------|-----------|--------------|--------------|--------|
| CTR | FinCEN | US | 117 | Complete |
| SAR | FinCEN | US | 184 | Complete |
| IFTI | AUSTRAC | AU | 87 | Complete |
| TTR | AUSTRAC | AU | 76 | Complete |
| SMR | AUSTRAC | AU | 92 | Complete |
| FATCA 8966 | IRS | US | 97 | Complete |
| FATCA Pool | IRS | US | 67 | Complete |
| CRS | OECD | International | 108 | Complete |
| UK SAR | UK NCA | UK | 122 | Complete |
| UK DAML SAR | UK NCA | UK | 132 | Complete |
| PSD2 Fraud | EBA | EU | 87 | Complete |
| Sanctions Blocking | OFAC | US | 72 | Complete |
| Terrorist Property | Multiple | International | 62 | Complete |

## Directory Structure

```
registry/
├── README.md                          # This file
├── requirements/
│   ├── master_index.yaml              # Global requirement index
│   ├── fincen/
│   │   ├── ctr/
│   │   │   ├── index.yaml             # CTR requirement index
│   │   │   ├── REQ-CTR-001.yaml       # Individual requirements
│   │   │   ├── REQ-CTR-002.yaml
│   │   │   └── ...
│   │   └── sar/
│   │       └── index.yaml
│   ├── austrac/
│   │   ├── ifti/
│   │   │   └── index.yaml
│   │   ├── ttr/
│   │   │   └── index.yaml
│   │   └── smr/
│   │       └── index.yaml
│   ├── irs/
│   │   ├── fatca_8966/
│   │   │   └── index.yaml
│   │   └── fatca_pool/
│   │       └── index.yaml
│   ├── oecd/
│   │   └── crs/
│   │       └── index.yaml
│   ├── uk_nca/
│   │   ├── sar/
│   │   │   └── index.yaml
│   │   └── daml_sar/
│   │       └── index.yaml
│   ├── eba/
│   │   └── psd2_fraud/
│   │       └── index.yaml
│   ├── ofac/
│   │   └── sanctions_blocking/
│   │       └── index.yaml
│   └── multi/
│       └── terrorist_property/
│           └── index.yaml
├── schemas/
│   └── requirement_schema.json        # JSON Schema for validation
└── changelog/
    └── (regulatory change logs)
```

## Requirement Categories

| Category | Description | Count |
|----------|-------------|-------|
| **ELIGIBILITY** | Rules determining when report is required | 52 |
| **FIELD** | Required data fields and their specifications | 312 |
| **VALIDATION** | Business rules and data quality checks | 78 |
| **FORMAT** | Output format requirements (XML, encoding) | 23 |
| **TIMING** | Filing deadlines and frequency | 15 |
| **SUBMISSION** | Submission methods and endpoints | 5 |
| **RETENTION** | Record retention requirements | 2 |

## Criticality Levels

| Level | Description | Count |
|-------|-------------|-------|
| **MANDATORY** | Must implement - regulatory violation if missing | 423 |
| **RECOMMENDED** | Should implement - best practice | 48 |
| **OPTIONAL** | May implement - enhanced compliance | 16 |

## Requirement Schema

Each requirement follows a standardized YAML schema:

```yaml
requirement:
  id: "REQ-XXX-NNN"           # Unique identifier
  regulator: "RegulatorName"   # Regulatory authority
  regulation: "CFR/Act ref"    # Regulation reference
  report_type: "ReportType"    # Report this applies to
  category: "ELIGIBILITY"      # ELIGIBILITY|FIELD|VALIDATION|FORMAT|TIMING
  title: "Short Title"         # Brief description
  description: |               # Full requirement text
    Detailed description...
  source:
    document: "Source doc"     # Regulatory source
    section: "1.2.3"           # Section reference
    url: "https://..."         # Link to source
    effective_date: "YYYY-MM-DD"
  criticality: "MANDATORY"     # MANDATORY|RECOMMENDED|OPTIONAL
  status: "ACTIVE"             # DRAFT|ACTIVE|DEPRECATED|SUPERSEDED
  implementation:
    expected_dsl_rules: []     # DSL rules that should implement
    expected_dsl_fields: []    # DSL fields that should implement
    expected_validations: []   # Validations that should implement
```

## Usage

### Validate Registry

```bash
python -m gps_cdm.traceability.cli validate-registry
```

### Generate Traceability Matrix

```bash
python -m gps_cdm.traceability.cli generate-matrix --output matrix.html
```

### Detect Gaps

```bash
python -m gps_cdm.traceability.cli detect-gaps
```

### Generate Audit Package

```bash
python -m gps_cdm.traceability.cli generate-audit-package --report FinCEN_CTR
```

## Maintenance

### Adding New Requirements

1. Create requirement YAML file following schema
2. Add entry to report index.yaml
3. Update master_index.yaml counts
4. Run validation: `python -m gps_cdm.traceability.cli validate-registry`

### Updating Requirements

1. Edit requirement YAML file
2. Update version and version_date
3. Document change in changelog/
4. Run gap detection to verify DSL still covers requirement

### Handling Regulatory Changes

1. Create change notice in changelog/
2. Run impact analysis: `python -m gps_cdm.traceability.cli analyze-impact`
3. Update affected requirements
4. Update DSL files as needed
5. Regenerate code and tests

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-12-20 | Initial registry with 487 requirements across 13 reports |

---

**Maintained by:** GPS CDM Compliance Team
**Last Updated:** 2024-12-20
