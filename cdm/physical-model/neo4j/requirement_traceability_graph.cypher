// GPS Payments CDM - Regulatory Requirement Traceability Graph Schema
// Version: 1.1.0
// Date: 2024-12-21
// Purpose: Link regulatory requirements to CDM fields for impact analysis

// =============================================================================
// REGULATORY TRACEABILITY GRAPH MODEL
// Links: Regulator -> Report -> Requirement -> CDM Field -> Source Field
// Enables: Impact analysis, coverage tracking, compliance traceability
// =============================================================================

// =============================================================================
// 1. REGULATORY NODE LABELS
// =============================================================================

// -----------------------------------------------------------------------------
// Regulator Node - Regulatory authority
// -----------------------------------------------------------------------------
CREATE CONSTRAINT regulator_id_unique IF NOT EXISTS
FOR (r:Regulator) REQUIRE r.regulator_id IS UNIQUE;

CREATE INDEX regulator_code_idx IF NOT EXISTS
FOR (r:Regulator) ON (r.regulator_code);

// Regulator node properties:
// - regulator_id: STRING
// - regulator_code: STRING (FINCEN, AUSTRAC, FINTRAC, etc.)
// - regulator_name: STRING
// - jurisdiction: STRING (US, AU, CA, UK, EU, HK, SG, JP)
// - website: STRING
// - is_active: BOOLEAN

// -----------------------------------------------------------------------------
// RegulatoryReport Node - Report types
// -----------------------------------------------------------------------------
CREATE CONSTRAINT report_id_unique IF NOT EXISTS
FOR (rpt:RegulatoryReport) REQUIRE rpt.report_id IS UNIQUE;

CREATE INDEX report_code_idx IF NOT EXISTS
FOR (rpt:RegulatoryReport) ON (rpt.report_code);

CREATE INDEX report_category_idx IF NOT EXISTS
FOR (rpt:RegulatoryReport) ON (rpt.category);

// RegulatoryReport node properties:
// - report_id: STRING
// - report_code: STRING (CTR, SAR, IFTI, etc.)
// - report_name: STRING
// - category: STRING (TRANSACTION_THRESHOLD, SUSPICIOUS_ACTIVITY, CROSS_BORDER, TAX, SANCTIONS)
// - filing_frequency: STRING (DAILY, EVENT_DRIVEN, ANNUAL)
// - filing_deadline: STRING
// - threshold_amount: FLOAT
// - threshold_currency: STRING
// - total_requirements: INTEGER

// -----------------------------------------------------------------------------
// Requirement Node - Individual regulatory requirements
// -----------------------------------------------------------------------------
CREATE CONSTRAINT requirement_id_unique IF NOT EXISTS
FOR (req:Requirement) REQUIRE req.requirement_id IS UNIQUE;

CREATE INDEX requirement_code_idx IF NOT EXISTS
FOR (req:Requirement) ON (req.requirement_code);

CREATE INDEX requirement_category_idx IF NOT EXISTS
FOR (req:Requirement) ON (req.category);

CREATE INDEX requirement_criticality_idx IF NOT EXISTS
FOR (req:Requirement) ON (req.criticality);

// Requirement node properties:
// - requirement_id: STRING
// - requirement_code: STRING (REQ-CTR-001)
// - requirement_title: STRING
// - requirement_description: STRING
// - category: STRING (ELIGIBILITY, FIELD, VALIDATION, FORMAT, TIMING)
// - criticality: STRING (MANDATORY, RECOMMENDED, OPTIONAL, CONDITIONAL)
// - is_active: BOOLEAN

// -----------------------------------------------------------------------------
// CDMEntity Node - CDM entities
// -----------------------------------------------------------------------------
CREATE CONSTRAINT cdm_entity_unique IF NOT EXISTS
FOR (e:CDMEntity) REQUIRE e.entity_name IS UNIQUE;

// CDMEntity node properties:
// - entity_name: STRING (Payment, Party, Account, etc.)
// - entity_domain: STRING (payment_core, party, account, etc.)
// - field_count: INTEGER
// - description: STRING

// -----------------------------------------------------------------------------
// CDMField Node - CDM entity fields
// -----------------------------------------------------------------------------
CREATE CONSTRAINT cdm_field_unique IF NOT EXISTS
FOR (f:CDMField) REQUIRE f.field_id IS UNIQUE;

CREATE INDEX cdm_field_name_idx IF NOT EXISTS
FOR (f:CDMField) ON (f.field_name);

CREATE INDEX cdm_field_entity_idx IF NOT EXISTS
FOR (f:CDMField) ON (f.entity_name);

// CDMField node properties:
// - field_id: STRING (entity.field_name)
// - field_name: STRING
// - field_path: STRING (for nested fields)
// - entity_name: STRING
// - data_type: STRING
// - is_pii: BOOLEAN
// - is_regulatory: BOOLEAN

// =============================================================================
// 2. REGULATORY TRACEABILITY RELATIONSHIPS
// =============================================================================

// -----------------------------------------------------------------------------
// Regulator -> RegulatoryReport: MANDATES
// -----------------------------------------------------------------------------
// (Regulator)-[:MANDATES]->(RegulatoryReport)

// -----------------------------------------------------------------------------
// RegulatoryReport -> Requirement: CONTAINS
// -----------------------------------------------------------------------------
// (RegulatoryReport)-[:CONTAINS {section}]->(Requirement)

// -----------------------------------------------------------------------------
// Requirement -> CDMField: MAPS_TO (core traceability)
// -----------------------------------------------------------------------------
// (Requirement)-[:MAPS_TO {
//     mapping_type: STRING,      // DIRECT, DERIVED, LOOKUP
//     transformation_logic: STRING,
//     validation_rule: STRING,
//     coverage_percentage: FLOAT
// }]->(CDMField)

// -----------------------------------------------------------------------------
// CDMEntity -> CDMField: HAS_FIELD
// -----------------------------------------------------------------------------
// (CDMEntity)-[:HAS_FIELD]->(CDMField)

// -----------------------------------------------------------------------------
// CDMField -> CDMField: DERIVES_FROM (inter-field dependencies)
// -----------------------------------------------------------------------------
// (TargetField:CDMField)-[:DERIVES_FROM {logic}]->(SourceField:CDMField)

// =============================================================================
// 3. SAMPLE DATA - REGULATORS
// =============================================================================

// Create Regulators
MERGE (fincen:Regulator {
    regulator_id: 'REG-001',
    regulator_code: 'FINCEN',
    regulator_name: 'Financial Crimes Enforcement Network',
    jurisdiction: 'US',
    is_active: true
});

MERGE (austrac:Regulator {
    regulator_id: 'REG-002',
    regulator_code: 'AUSTRAC',
    regulator_name: 'Australian Transaction Reports and Analysis Centre',
    jurisdiction: 'AU',
    is_active: true
});

MERGE (fintrac:Regulator {
    regulator_id: 'REG-003',
    regulator_code: 'FINTRAC',
    regulator_name: 'Financial Transactions and Reports Analysis Centre of Canada',
    jurisdiction: 'CA',
    is_active: true
});

MERGE (irs:Regulator {
    regulator_id: 'REG-004',
    regulator_code: 'IRS',
    regulator_name: 'Internal Revenue Service',
    jurisdiction: 'US',
    is_active: true
});

MERGE (uknca:Regulator {
    regulator_id: 'REG-005',
    regulator_code: 'UK_NCA',
    regulator_name: 'UK National Crime Agency',
    jurisdiction: 'UK',
    is_active: true
});

MERGE (eba:Regulator {
    regulator_id: 'REG-006',
    regulator_code: 'EBA',
    regulator_name: 'European Banking Authority',
    jurisdiction: 'EU',
    is_active: true
});

MERGE (ofac:Regulator {
    regulator_id: 'REG-007',
    regulator_code: 'OFAC',
    regulator_name: 'Office of Foreign Assets Control',
    jurisdiction: 'US',
    is_active: true
});

MERGE (oecd:Regulator {
    regulator_id: 'REG-008',
    regulator_code: 'OECD',
    regulator_name: 'Organisation for Economic Co-operation and Development',
    jurisdiction: 'INTERNATIONAL',
    is_active: true
});

MERGE (jfiu:Regulator {
    regulator_id: 'REG-009',
    regulator_code: 'JFIU',
    regulator_name: 'Joint Financial Intelligence Unit (Hong Kong)',
    jurisdiction: 'HK',
    is_active: true
});

MERGE (stro:Regulator {
    regulator_id: 'REG-010',
    regulator_code: 'STRO',
    regulator_name: 'Suspicious Transaction Reporting Office (Singapore)',
    jurisdiction: 'SG',
    is_active: true
});

MERGE (jafic:Regulator {
    regulator_id: 'REG-011',
    regulator_code: 'JAFIC',
    regulator_name: 'Japan Financial Intelligence Center',
    jurisdiction: 'JP',
    is_active: true
});

// =============================================================================
// 4. SAMPLE DATA - CORE PAYMENT REPORTS
// =============================================================================

// FinCEN Reports
MERGE (ctr:RegulatoryReport {
    report_id: 'RPT-CTR',
    report_code: 'CTR',
    report_name: 'Currency Transaction Report',
    category: 'TRANSACTION_THRESHOLD',
    filing_frequency: 'DAILY',
    filing_deadline: '15 days',
    threshold_amount: 10000,
    threshold_currency: 'USD',
    total_requirements: 117
});

MERGE (sar:RegulatoryReport {
    report_id: 'RPT-SAR',
    report_code: 'SAR',
    report_name: 'Suspicious Activity Report',
    category: 'SUSPICIOUS_ACTIVITY',
    filing_frequency: 'EVENT_DRIVEN',
    filing_deadline: '30 days',
    total_requirements: 184
});

// AUSTRAC Reports
MERGE (ifti:RegulatoryReport {
    report_id: 'RPT-IFTI',
    report_code: 'IFTI',
    report_name: 'International Funds Transfer Instruction',
    category: 'CROSS_BORDER',
    filing_frequency: 'REAL_TIME',
    filing_deadline: '10 business days',
    total_requirements: 87
});

MERGE (ttr:RegulatoryReport {
    report_id: 'RPT-TTR',
    report_code: 'TTR',
    report_name: 'Threshold Transaction Report',
    category: 'TRANSACTION_THRESHOLD',
    filing_frequency: 'EVENT_DRIVEN',
    threshold_amount: 10000,
    threshold_currency: 'AUD',
    total_requirements: 76
});

MERGE (smr:RegulatoryReport {
    report_id: 'RPT-SMR',
    report_code: 'SMR',
    report_name: 'Suspicious Matter Report',
    category: 'SUSPICIOUS_ACTIVITY',
    filing_frequency: 'EVENT_DRIVEN',
    total_requirements: 92
});

// FINTRAC Reports
MERGE (lctr:RegulatoryReport {
    report_id: 'RPT-LCTR',
    report_code: 'LCTR',
    report_name: 'Large Cash Transaction Report',
    category: 'TRANSACTION_THRESHOLD',
    filing_frequency: 'EVENT_DRIVEN',
    filing_deadline: '15 calendar days',
    threshold_amount: 10000,
    threshold_currency: 'CAD',
    total_requirements: 95
});

MERGE (str_ca:RegulatoryReport {
    report_id: 'RPT-STR-CA',
    report_code: 'STR',
    report_name: 'Suspicious Transaction Report (Canada)',
    category: 'SUSPICIOUS_ACTIVITY',
    filing_frequency: 'EVENT_DRIVEN',
    filing_deadline: '30 calendar days',
    total_requirements: 125
});

MERGE (eftr:RegulatoryReport {
    report_id: 'RPT-EFTR',
    report_code: 'EFTR',
    report_name: 'Electronic Funds Transfer Report',
    category: 'CROSS_BORDER',
    filing_frequency: 'EVENT_DRIVEN',
    filing_deadline: '5 business days',
    threshold_amount: 10000,
    threshold_currency: 'CAD',
    total_requirements: 88
});

// Create relationships: Regulator -> Report
MATCH (fincen:Regulator {regulator_code: 'FINCEN'})
MATCH (ctr:RegulatoryReport {report_code: 'CTR'})
MERGE (fincen)-[:MANDATES]->(ctr);

MATCH (fincen:Regulator {regulator_code: 'FINCEN'})
MATCH (sar:RegulatoryReport {report_code: 'SAR'})
MERGE (fincen)-[:MANDATES]->(sar);

MATCH (austrac:Regulator {regulator_code: 'AUSTRAC'})
MATCH (ifti:RegulatoryReport {report_code: 'IFTI'})
MERGE (austrac)-[:MANDATES]->(ifti);

MATCH (austrac:Regulator {regulator_code: 'AUSTRAC'})
MATCH (ttr:RegulatoryReport {report_code: 'TTR'})
MERGE (austrac)-[:MANDATES]->(ttr);

MATCH (austrac:Regulator {regulator_code: 'AUSTRAC'})
MATCH (smr:RegulatoryReport {report_code: 'SMR'})
MERGE (austrac)-[:MANDATES]->(smr);

MATCH (fintrac:Regulator {regulator_code: 'FINTRAC'})
MATCH (lctr:RegulatoryReport {report_code: 'LCTR'})
MERGE (fintrac)-[:MANDATES]->(lctr);

MATCH (fintrac:Regulator {regulator_code: 'FINTRAC'})
MATCH (str:RegulatoryReport {report_code: 'STR'})
MERGE (fintrac)-[:MANDATES]->(str);

MATCH (fintrac:Regulator {regulator_code: 'FINTRAC'})
MATCH (eftr:RegulatoryReport {report_code: 'EFTR'})
MERGE (fintrac)-[:MANDATES]->(eftr);

// =============================================================================
// 5. SAMPLE DATA - CDM ENTITIES AND FIELDS
// =============================================================================

// Create CDM Entities
MERGE (payment:CDMEntity {entity_name: 'Payment', entity_domain: 'payment_core'});
MERGE (paymentInst:CDMEntity {entity_name: 'PaymentInstruction', entity_domain: 'payment_core'});
MERGE (party:CDMEntity {entity_name: 'Party', entity_domain: 'party'});
MERGE (person:CDMEntity {entity_name: 'Person', entity_domain: 'party'});
MERGE (partyId:CDMEntity {entity_name: 'PartyIdentification', entity_domain: 'party'});
MERGE (account:CDMEntity {entity_name: 'Account', entity_domain: 'account'});
MERGE (fi:CDMEntity {entity_name: 'FinancialInstitution', entity_domain: 'party'});

// Create CDM Fields for Payment
MERGE (paymentAmount:CDMField {field_id: 'Payment.amount', field_name: 'amount', entity_name: 'Payment', data_type: 'DECIMAL', is_regulatory: true});
MERGE (paymentCurrency:CDMField {field_id: 'Payment.currency', field_name: 'currency', entity_name: 'Payment', data_type: 'STRING', is_regulatory: true});
MERGE (paymentDate:CDMField {field_id: 'Payment.created_at', field_name: 'created_at', entity_name: 'Payment', data_type: 'TIMESTAMP', is_regulatory: true});
MERGE (paymentType:CDMField {field_id: 'Payment.payment_type', field_name: 'payment_type', entity_name: 'Payment', data_type: 'STRING', is_regulatory: true});
MERGE (paymentCrossBorder:CDMField {field_id: 'Payment.cross_border_flag', field_name: 'cross_border_flag', entity_name: 'Payment', data_type: 'BOOLEAN', is_regulatory: true});

// Create CDM Fields for Party
MERGE (partyName:CDMField {field_id: 'Party.name', field_name: 'name', entity_name: 'Party', data_type: 'STRING', is_pii: true, is_regulatory: true});
MERGE (partyAddress:CDMField {field_id: 'Party.address', field_name: 'address', entity_name: 'Party', data_type: 'STRUCT', is_pii: true, is_regulatory: true});
MERGE (partyCountry:CDMField {field_id: 'Party.country', field_name: 'country', entity_name: 'Party', data_type: 'STRING', is_regulatory: true});

// Create CDM Fields for Person
MERGE (personDob:CDMField {field_id: 'Person.date_of_birth', field_name: 'date_of_birth', entity_name: 'Person', data_type: 'DATE', is_pii: true, is_regulatory: true});
MERGE (personOccupation:CDMField {field_id: 'Person.occupation', field_name: 'occupation', entity_name: 'Person', data_type: 'STRING', is_regulatory: true});

// Create CDM Fields for PartyIdentification
MERGE (idType:CDMField {field_id: 'PartyIdentification.id_type', field_name: 'id_type', entity_name: 'PartyIdentification', data_type: 'STRING', is_regulatory: true});
MERGE (idNumber:CDMField {field_id: 'PartyIdentification.id_number', field_name: 'id_number', entity_name: 'PartyIdentification', data_type: 'STRING', is_pii: true, is_regulatory: true});

// Link Entities to Fields
MATCH (payment:CDMEntity {entity_name: 'Payment'})
MATCH (paymentAmount:CDMField {field_id: 'Payment.amount'})
MERGE (payment)-[:HAS_FIELD]->(paymentAmount);

MATCH (payment:CDMEntity {entity_name: 'Payment'})
MATCH (paymentCurrency:CDMField {field_id: 'Payment.currency'})
MERGE (payment)-[:HAS_FIELD]->(paymentCurrency);

MATCH (payment:CDMEntity {entity_name: 'Payment'})
MATCH (paymentDate:CDMField {field_id: 'Payment.created_at'})
MERGE (payment)-[:HAS_FIELD]->(paymentDate);

MATCH (party:CDMEntity {entity_name: 'Party'})
MATCH (partyName:CDMField {field_id: 'Party.name'})
MERGE (party)-[:HAS_FIELD]->(partyName);

MATCH (party:CDMEntity {entity_name: 'Party'})
MATCH (partyAddress:CDMField {field_id: 'Party.address'})
MERGE (party)-[:HAS_FIELD]->(partyAddress);

// =============================================================================
// 6. SAMPLE DATA - REQUIREMENTS TO CDM FIELD MAPPINGS
// =============================================================================

// CTR Requirements
MERGE (reqCtr001:Requirement {
    requirement_id: 'REQ-CTR-001',
    requirement_code: 'REQ-CTR-001',
    requirement_title: 'Currency Transaction Reporting Threshold',
    category: 'ELIGIBILITY',
    criticality: 'MANDATORY'
});

MERGE (reqCtr041:Requirement {
    requirement_id: 'REQ-CTR-041',
    requirement_code: 'REQ-CTR-041',
    requirement_title: 'Transaction Amount',
    category: 'FIELD',
    criticality: 'MANDATORY'
});

// Link CTR Report to Requirements
MATCH (ctr:RegulatoryReport {report_code: 'CTR'})
MATCH (reqCtr001:Requirement {requirement_id: 'REQ-CTR-001'})
MERGE (ctr)-[:CONTAINS {section: 'ELIGIBILITY'}]->(reqCtr001);

MATCH (ctr:RegulatoryReport {report_code: 'CTR'})
MATCH (reqCtr041:Requirement {requirement_id: 'REQ-CTR-041'})
MERGE (ctr)-[:CONTAINS {section: 'PART_III'}]->(reqCtr041);

// Link Requirements to CDM Fields
MATCH (reqCtr001:Requirement {requirement_id: 'REQ-CTR-001'})
MATCH (paymentAmount:CDMField {field_id: 'Payment.amount'})
MERGE (reqCtr001)-[:MAPS_TO {
    mapping_type: 'DERIVED',
    transformation_logic: 'amount >= 10000 AND currency = USD AND cash_transaction = TRUE',
    coverage_percentage: 100.0
}]->(paymentAmount);

MATCH (reqCtr041:Requirement {requirement_id: 'REQ-CTR-041'})
MATCH (paymentAmount:CDMField {field_id: 'Payment.amount'})
MERGE (reqCtr041)-[:MAPS_TO {
    mapping_type: 'DIRECT',
    coverage_percentage: 100.0
}]->(paymentAmount);

// =============================================================================
// 7. TRACEABILITY QUERIES
// =============================================================================

// Find all requirements for a given CDM field (impact analysis)
// MATCH (field:CDMField {field_name: $fieldName})<-[:MAPS_TO]-(req:Requirement)<-[:CONTAINS]-(rpt:RegulatoryReport)<-[:MANDATES]-(reg:Regulator)
// RETURN reg.regulator_code, rpt.report_code, req.requirement_code, req.criticality;

// Find all CDM fields required by a specific report
// MATCH (rpt:RegulatoryReport {report_code: $reportCode})-[:CONTAINS]->(req:Requirement)-[:MAPS_TO]->(field:CDMField)
// RETURN field.entity_name, field.field_name, req.requirement_code, req.criticality;

// Find requirements by jurisdiction
// MATCH (reg:Regulator {jurisdiction: $jurisdiction})-[:MANDATES]->(rpt:RegulatoryReport)-[:CONTAINS]->(req:Requirement)
// RETURN rpt.report_code, COUNT(req) AS requirement_count
// ORDER BY requirement_count DESC;

// Calculate regulatory coverage for an entity
// MATCH (entity:CDMEntity {entity_name: $entityName})-[:HAS_FIELD]->(field:CDMField)
// OPTIONAL MATCH (field)<-[:MAPS_TO]-(req:Requirement)
// WITH entity, field, COUNT(req) AS req_count
// RETURN entity.entity_name,
//        COUNT(field) AS total_fields,
//        SUM(CASE WHEN req_count > 0 THEN 1 ELSE 0 END) AS regulatory_fields,
//        100.0 * SUM(CASE WHEN req_count > 0 THEN 1 ELSE 0 END) / COUNT(field) AS regulatory_coverage_pct;

// Find cross-jurisdiction impact of a field change
// MATCH (field:CDMField {field_id: $fieldId})<-[:MAPS_TO]-(req:Requirement)<-[:CONTAINS]-(rpt:RegulatoryReport)<-[:MANDATES]-(reg:Regulator)
// RETURN DISTINCT reg.jurisdiction, reg.regulator_code, rpt.report_code, req.criticality
// ORDER BY reg.jurisdiction;
