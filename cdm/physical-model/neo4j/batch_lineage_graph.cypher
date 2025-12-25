// GPS CDM - Neo4j Batch Lineage Graph Schema
// ============================================
//
// This schema defines the knowledge graph for:
// - Batch metadata and layer-level statistics (NOT individual records)
// - Aggregated DQ metrics and trends
// - Schema/mapping lineage for visualization
//
// PostgreSQL remains the source of truth for individual records.
//
// Usage:
//   1. Start Neo4j: docker-compose -f docker-compose.nifi.yaml up -d neo4j
//   2. Access browser: http://localhost:7474
//   3. Run this script to create constraints and initial schema

// ============================================================================
// CONSTRAINTS & INDEXES
// ============================================================================

// Batch constraints
CREATE CONSTRAINT batch_id IF NOT EXISTS FOR (b:Batch) REQUIRE b.batch_id IS UNIQUE;
CREATE INDEX batch_status IF NOT EXISTS FOR (b:Batch) ON (b.status);
CREATE INDEX batch_message_type IF NOT EXISTS FOR (b:Batch) ON (b.message_type);
CREATE INDEX batch_created_at IF NOT EXISTS FOR (b:Batch) ON (b.created_at);

// BatchLayer constraints
CREATE CONSTRAINT batch_layer_id IF NOT EXISTS FOR (bl:BatchLayer) REQUIRE bl.batch_layer_id IS UNIQUE;
CREATE INDEX batch_layer_batch_id IF NOT EXISTS FOR (bl:BatchLayer) ON (bl.batch_id);
CREATE INDEX batch_layer_layer IF NOT EXISTS FOR (bl:BatchLayer) ON (bl.layer);

// MessageType constraints
CREATE CONSTRAINT message_type_id IF NOT EXISTS FOR (mt:MessageType) REQUIRE mt.type IS UNIQUE;

// CDMEntity constraints
CREATE CONSTRAINT cdm_entity_id IF NOT EXISTS FOR (e:CDMEntity) REQUIRE e.entity_id IS UNIQUE;
CREATE INDEX cdm_entity_type IF NOT EXISTS FOR (e:CDMEntity) ON (e.entity_type);

// CDMField constraints
CREATE CONSTRAINT cdm_field_id IF NOT EXISTS FOR (f:CDMField) REQUIRE f.field_id IS UNIQUE;
CREATE INDEX cdm_field_path IF NOT EXISTS FOR (f:CDMField) ON (f.field_path);

// DQMetrics constraints
CREATE CONSTRAINT dq_metrics_id IF NOT EXISTS FOR (dq:DQMetrics) REQUIRE dq.metric_id IS UNIQUE;
CREATE INDEX dq_metrics_batch IF NOT EXISTS FOR (dq:DQMetrics) ON (dq.batch_id);

// ExceptionSummary constraints
CREATE CONSTRAINT exception_summary_id IF NOT EXISTS FOR (ex:ExceptionSummary) REQUIRE ex.summary_id IS UNIQUE;
CREATE INDEX exception_summary_batch IF NOT EXISTS FOR (ex:ExceptionSummary) ON (ex.batch_id);

// ============================================================================
// NODE DEFINITIONS
// ============================================================================

// Batch Node - Processing batch metadata
// Properties:
//   - batch_id: string (unique)
//   - message_type: string
//   - source_system: string
//   - source_file: string (optional)
//   - status: PENDING | PROCESSING | COMPLETED | FAILED | PARTIAL
//   - created_at: datetime
//   - updated_at: datetime
//   - completed_at: datetime (optional)
//   - total_records: integer
//   - duration_ms: integer (optional)

// BatchLayer Node - Aggregated stats per layer (NOT individual records)
// Properties:
//   - batch_layer_id: string (batch_id + "_" + layer)
//   - batch_id: string
//   - layer: bronze | silver | gold | analytics
//   - input_count: integer
//   - processed_count: integer
//   - failed_count: integer
//   - pending_count: integer
//   - dq_passed_count: integer (silver only)
//   - dq_failed_count: integer (silver only)
//   - avg_dq_score: float (silver only)
//   - started_at: datetime
//   - completed_at: datetime (optional)
//   - duration_ms: integer

// MessageType Node - Schema/mapping lineage node
// Properties:
//   - type: string (e.g., "pain.001")
//   - version: string (e.g., "001.001.09")
//   - name: string
//   - description: string
//   - format: XML | JSON | CSV

// CDMEntity Node - Gold layer entity types for knowledge graph
// Properties:
//   - entity_id: string (layer + "." + table_name)
//   - entity_type: string (table name)
//   - layer: bronze | silver | gold | analytics
//   - description: string

// CDMField Node - Field metadata for lineage visualization
// Properties:
//   - field_id: string (entity_id + "." + field_name)
//   - field_path: string (canonical path)
//   - field_name: string
//   - display_name: string
//   - data_type: string
//   - is_required: boolean
//   - is_pii: boolean
//   - is_regulatory: boolean

// DQMetrics Node - Aggregated DQ metrics (batch-level summaries)
// Properties:
//   - metric_id: string
//   - batch_id: string
//   - layer: string
//   - entity_type: string
//   - overall_avg_score: float
//   - completeness_avg: float
//   - accuracy_avg: float
//   - validity_avg: float
//   - records_above_threshold: integer
//   - records_below_threshold: integer
//   - top_failing_rules: array
//   - evaluated_at: datetime

// ExceptionSummary Node - Aggregated exception counts (NOT individual exceptions)
// Properties:
//   - summary_id: string
//   - batch_id: string
//   - layer: string
//   - exception_type: string
//   - severity: WARNING | ERROR | CRITICAL
//   - count: integer
//   - sample_message: string
//   - first_seen: datetime
//   - last_seen: datetime

// ============================================================================
// RELATIONSHIP DEFINITIONS
// ============================================================================

// Batch to BatchLayer: (Batch)-[:AT_LAYER {sequence}]->(BatchLayer)
// BatchLayer to BatchLayer: (BatchLayer)-[:PROMOTED_TO {record_count, success_rate}]->(BatchLayer)
// Batch to MessageType: (Batch)-[:USES_MAPPING]->(MessageType)
// Batch to DQMetrics: (Batch)-[:HAS_DQ_METRICS]->(DQMetrics)
// Batch to ExceptionSummary: (Batch)-[:HAS_EXCEPTION_SUMMARY]->(ExceptionSummary)
// MessageType to CDMEntity: (MessageType)-[:PRODUCES]->(CDMEntity)
// CDMEntity to CDMField: (CDMEntity)-[:HAS_FIELD]->(CDMField)
// CDMField to CDMField: (CDMField)-[:DERIVED_FROM {transform_type, logic}]->(CDMField)

// ============================================================================
// SAMPLE DATA - Message Type Schema Lineage
// ============================================================================

// Create pain.001 message type and its entities
MERGE (mt:MessageType {type: 'pain.001'})
SET mt.version = '001.001.09',
    mt.name = 'ISO 20022 Customer Credit Transfer Initiation',
    mt.description = 'Customer credit transfer initiation message',
    mt.format = 'XML';

// Create entities for pain.001
MERGE (bronze:CDMEntity {entity_id: 'bronze.raw_payment_messages'})
SET bronze.entity_type = 'raw_payment_messages',
    bronze.layer = 'bronze',
    bronze.description = 'Raw payment messages in original format';

MERGE (silver:CDMEntity {entity_id: 'silver.stg_pain001'})
SET silver.entity_type = 'stg_pain001',
    silver.layer = 'silver',
    silver.description = 'Staged pain.001 records with parsed fields';

MERGE (gold:CDMEntity {entity_id: 'gold.cdm_payment_instruction'})
SET gold.entity_type = 'cdm_payment_instruction',
    gold.layer = 'gold',
    gold.description = 'Unified payment instruction in CDM format';

// Create relationships
MERGE (mt)-[:PRODUCES]->(bronze)
MERGE (mt)-[:PRODUCES]->(silver)
MERGE (mt)-[:PRODUCES]->(gold)

// Create bronze to silver transformation
MERGE (bronze)-[:TRANSFORMS_TO {
  transformation_type: 'xml_parse',
  description: 'Parse XML to structured fields'
}]->(silver)

// Create silver to gold transformation
MERGE (silver)-[:TRANSFORMS_TO {
  transformation_type: 'normalize',
  description: 'Normalize to unified CDM schema'
}]->(gold);

// ============================================================================
// SAMPLE FIELD LINEAGE
// ============================================================================

// Debtor name lineage
MERGE (f_bronze_dbtr:CDMField {field_id: 'bronze.raw_payment_messages.DbtrNm'})
SET f_bronze_dbtr.field_path = 'PmtInf/Dbtr/Nm',
    f_bronze_dbtr.field_name = 'DbtrNm',
    f_bronze_dbtr.display_name = 'Debtor Name (XML)',
    f_bronze_dbtr.data_type = 'string';

MERGE (f_silver_dbtr:CDMField {field_id: 'silver.stg_pain001.debtor_name'})
SET f_silver_dbtr.field_path = 'debtor_name',
    f_silver_dbtr.field_name = 'debtor_name',
    f_silver_dbtr.display_name = 'Debtor Name',
    f_silver_dbtr.data_type = 'string',
    f_silver_dbtr.is_required = true;

MERGE (f_gold_payer:CDMField {field_id: 'gold.cdm_payment_instruction.payer_name'})
SET f_gold_payer.field_path = 'payer_name',
    f_gold_payer.field_name = 'payer_name',
    f_gold_payer.display_name = 'Payer Name',
    f_gold_payer.data_type = 'string',
    f_gold_payer.is_required = true;

// Create entity-field relationships
MERGE (bronze)-[:HAS_FIELD]->(f_bronze_dbtr)
MERGE (silver)-[:HAS_FIELD]->(f_silver_dbtr)
MERGE (gold)-[:HAS_FIELD]->(f_gold_payer)

// Create field lineage relationships
MERGE (f_silver_dbtr)-[:DERIVED_FROM {
  transform_type: 'direct',
  xpath: 'PmtInf/Dbtr/Nm',
  extract_method: 'text_content'
}]->(f_bronze_dbtr)

MERGE (f_gold_payer)-[:DERIVED_FROM {
  transform_type: 'direct',
  source_field: 'debtor_name'
}]->(f_silver_dbtr);

// Instructed amount lineage
MERGE (f_bronze_amt:CDMField {field_id: 'bronze.raw_payment_messages.InstdAmt'})
SET f_bronze_amt.field_path = 'PmtInf/CdtTrfTxInf/Amt/InstdAmt',
    f_bronze_amt.field_name = 'InstdAmt',
    f_bronze_amt.display_name = 'Instructed Amount (XML)',
    f_bronze_amt.data_type = 'decimal';

MERGE (f_silver_amt:CDMField {field_id: 'silver.stg_pain001.instructed_amount'})
SET f_silver_amt.field_path = 'instructed_amount',
    f_silver_amt.field_name = 'instructed_amount',
    f_silver_amt.display_name = 'Instructed Amount',
    f_silver_amt.data_type = 'decimal',
    f_silver_amt.is_required = true;

MERGE (f_gold_amt:CDMField {field_id: 'gold.cdm_payment_instruction.instructed_amount'})
SET f_gold_amt.field_path = 'instructed_amount',
    f_gold_amt.field_name = 'instructed_amount',
    f_gold_amt.display_name = 'Instructed Amount',
    f_gold_amt.data_type = 'decimal',
    f_gold_amt.is_required = true;

MERGE (silver)-[:HAS_FIELD]->(f_silver_amt)
MERGE (gold)-[:HAS_FIELD]->(f_gold_amt)

MERGE (f_silver_amt)-[:DERIVED_FROM {
  transform_type: 'direct',
  xpath: 'PmtInf/CdtTrfTxInf/Amt/InstdAmt',
  extract_method: 'text_content'
}]->(f_bronze_amt)

MERGE (f_gold_amt)-[:DERIVED_FROM {
  transform_type: 'direct',
  source_field: 'instructed_amount'
}]->(f_silver_amt);

// ============================================================================
// USEFUL QUERIES
// ============================================================================

// Query 1: Get batch lineage with layer stats
// MATCH (b:Batch {batch_id: $batchId})-[:AT_LAYER]->(bl:BatchLayer)
// RETURN b, bl ORDER BY bl.layer;

// Query 2: Get field lineage for a specific field
// MATCH path = (target:CDMField {field_name: $fieldName})-[:DERIVED_FROM*]->(source:CDMField)
// RETURN path;

// Query 3: Get all entities produced by a message type
// MATCH (mt:MessageType {type: $messageType})-[:PRODUCES]->(e:CDMEntity)
// RETURN mt, e;

// Query 4: Get DQ trends over time
// MATCH (b:Batch)-[:HAS_DQ_METRICS]->(dq:DQMetrics)
// WHERE b.message_type = $messageType
// RETURN b.created_at, dq.overall_avg_score
// ORDER BY b.created_at;

// Query 5: Get processing bottlenecks by layer
// MATCH (bl:BatchLayer)
// WHERE bl.completed_at IS NOT NULL
// RETURN bl.layer, avg(bl.duration_ms) as avg_duration,
//        sum(bl.failed_count) as total_failures
// GROUP BY bl.layer;

RETURN "GPS CDM Neo4j Schema initialized successfully" AS status;
