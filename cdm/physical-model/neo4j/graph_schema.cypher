// GPS Payments CDM - Neo4J Graph Schema
// Version: 1.0.0
// Date: 2024-12-20
// Purpose: Fraud Detection + Data Lineage Graph

// =============================================================================
// NEO4J GRAPH MODEL FOR GPS CDM
// Two primary use cases:
// 1. Payment Network Graph (Fraud Detection)
// 2. Data Lineage Graph (Impact Analysis)
// =============================================================================

// =============================================================================
// 1. PAYMENT NETWORK GRAPH - Node Labels
// =============================================================================

// -----------------------------------------------------------------------------
// Party Node - Central entity in payment network
// -----------------------------------------------------------------------------
CREATE CONSTRAINT party_id_unique IF NOT EXISTS
FOR (p:Party) REQUIRE p.party_id IS UNIQUE;

CREATE INDEX party_name_idx IF NOT EXISTS
FOR (p:Party) ON (p.name);

CREATE INDEX party_type_idx IF NOT EXISTS
FOR (p:Party) ON (p.party_type);

CREATE INDEX party_risk_idx IF NOT EXISTS
FOR (p:Party) ON (p.risk_rating);

// Party node properties:
// - party_id: STRING (UUID)
// - party_type: STRING (INDIVIDUAL, ORGANIZATION, etc.)
// - name: STRING
// - country: STRING
// - risk_rating: STRING (low, medium, high, very_high)
// - pep_flag: BOOLEAN
// - sanctions_status: STRING
// - created_at: DATETIME
// - last_updated: DATETIME

// -----------------------------------------------------------------------------
// Account Node
// -----------------------------------------------------------------------------
CREATE CONSTRAINT account_id_unique IF NOT EXISTS
FOR (a:Account) REQUIRE a.account_id IS UNIQUE;

CREATE INDEX account_number_idx IF NOT EXISTS
FOR (a:Account) ON (a.account_number);

// Account node properties:
// - account_id: STRING (UUID)
// - account_number: STRING
// - account_type: STRING
// - currency: STRING
// - status: STRING
// - risk_rating: STRING
// - current_balance: FLOAT

// -----------------------------------------------------------------------------
// Financial Institution Node
// -----------------------------------------------------------------------------
CREATE CONSTRAINT fi_id_unique IF NOT EXISTS
FOR (fi:FinancialInstitution) REQUIRE fi.fi_id IS UNIQUE;

CREATE INDEX fi_bic_idx IF NOT EXISTS
FOR (fi:FinancialInstitution) ON (fi.bic);

// FinancialInstitution node properties:
// - fi_id: STRING (UUID)
// - name: STRING
// - bic: STRING
// - country: STRING
// - fi_type: STRING

// -----------------------------------------------------------------------------
// Payment Node
// -----------------------------------------------------------------------------
CREATE CONSTRAINT payment_id_unique IF NOT EXISTS
FOR (pmt:Payment) REQUIRE pmt.payment_id IS UNIQUE;

CREATE INDEX payment_status_idx IF NOT EXISTS
FOR (pmt:Payment) ON (pmt.status);

CREATE INDEX payment_date_idx IF NOT EXISTS
FOR (pmt:Payment) ON (pmt.created_at);

CREATE INDEX payment_type_idx IF NOT EXISTS
FOR (pmt:Payment) ON (pmt.payment_type);

// Payment node properties:
// - payment_id: STRING (UUID)
// - payment_type: STRING
// - scheme_code: STRING
// - status: STRING
// - amount: FLOAT
// - currency: STRING
// - cross_border: BOOLEAN
// - created_at: DATETIME
// - fraud_score: FLOAT
// - sanctions_status: STRING

// =============================================================================
// 2. PAYMENT NETWORK GRAPH - Relationships
// =============================================================================

// -----------------------------------------------------------------------------
// Party -> Account: OWNS relationship
// -----------------------------------------------------------------------------
// (Party)-[:OWNS {ownership_type, ownership_percentage, since}]->(Account)

// -----------------------------------------------------------------------------
// Party -> Payment: SENDS / RECEIVES relationships
// -----------------------------------------------------------------------------
// (Party)-[:SENDS {role: 'DEBTOR'}]->(Payment)
// (Party)-[:RECEIVES {role: 'CREDITOR'}]->(Payment)

// -----------------------------------------------------------------------------
// Account -> Payment: DEBITED_BY / CREDITED_BY relationships
// -----------------------------------------------------------------------------
// (Account)-[:DEBITED_BY]->(Payment)
// (Account)-[:CREDITED_BY]->(Payment)

// -----------------------------------------------------------------------------
// FinancialInstitution -> Payment: PROCESSES relationships
// -----------------------------------------------------------------------------
// (FinancialInstitution)-[:PROCESSES {role: 'DEBTOR_AGENT|CREDITOR_AGENT|INTERMEDIARY'}]->(Payment)

// -----------------------------------------------------------------------------
// Account -> FinancialInstitution: HELD_AT relationship
// -----------------------------------------------------------------------------
// (Account)-[:HELD_AT]->(FinancialInstitution)

// -----------------------------------------------------------------------------
// Party -> Party: TRANSACTS_WITH relationship (derived)
// -----------------------------------------------------------------------------
// (Party)-[:TRANSACTS_WITH {count, total_amount, first_txn, last_txn, avg_amount}]->(Party)

// =============================================================================
// 3. FRAUD DETECTION SPECIFIC NODES/RELATIONSHIPS
// =============================================================================

// -----------------------------------------------------------------------------
// SuspiciousCluster Node - Identified fraud rings
// -----------------------------------------------------------------------------
CREATE CONSTRAINT cluster_id_unique IF NOT EXISTS
FOR (c:SuspiciousCluster) REQUIRE c.cluster_id IS UNIQUE;

// SuspiciousCluster node properties:
// - cluster_id: STRING
// - cluster_type: STRING (ROUND_TRIPPING, LAYERING, STRUCTURING, RAPID_MOVEMENT)
// - risk_score: FLOAT
// - member_count: INTEGER
// - total_amount: FLOAT
// - detected_at: DATETIME
// - status: STRING (ACTIVE, UNDER_INVESTIGATION, CLOSED)

// (Party)-[:MEMBER_OF {role, join_date}]->(SuspiciousCluster)

// -----------------------------------------------------------------------------
// Alert Node - Fraud/AML alerts
// -----------------------------------------------------------------------------
CREATE CONSTRAINT alert_id_unique IF NOT EXISTS
FOR (alert:Alert) REQUIRE alert.alert_id IS UNIQUE;

// Alert node properties:
// - alert_id: STRING
// - alert_type: STRING (FRAUD, AML, SANCTIONS)
// - severity: STRING (LOW, MEDIUM, HIGH, CRITICAL)
// - status: STRING (OPEN, INVESTIGATING, CLOSED)
// - created_at: DATETIME
// - description: STRING

// (Payment)-[:TRIGGERED]->(Alert)
// (Party)-[:ASSOCIATED_WITH]->(Alert)

// =============================================================================
// 4. DATA LINEAGE GRAPH - Node Labels
// =============================================================================

// -----------------------------------------------------------------------------
// DataSource Node - Source systems
// -----------------------------------------------------------------------------
CREATE CONSTRAINT datasource_id_unique IF NOT EXISTS
FOR (ds:DataSource) REQUIRE ds.source_id IS UNIQUE;

// DataSource node properties:
// - source_id: STRING
// - source_name: STRING
// - source_type: STRING (DATABASE, FILE, API, QUEUE)
// - connection_string: STRING (masked)

// -----------------------------------------------------------------------------
// DataTable Node - Source/target tables
// -----------------------------------------------------------------------------
CREATE CONSTRAINT table_id_unique IF NOT EXISTS
FOR (t:DataTable) REQUIRE t.table_id IS UNIQUE;

// DataTable node properties:
// - table_id: STRING
// - database: STRING
// - schema: STRING
// - table_name: STRING
// - layer: STRING (BRONZE, SILVER, GOLD)
// - record_count: INTEGER
// - last_refreshed: DATETIME

// -----------------------------------------------------------------------------
// DataField Node - Individual fields
// -----------------------------------------------------------------------------
CREATE CONSTRAINT field_id_unique IF NOT EXISTS
FOR (f:DataField) REQUIRE f.field_id IS UNIQUE;

CREATE INDEX field_name_idx IF NOT EXISTS
FOR (f:DataField) ON (f.field_name);

// DataField node properties:
// - field_id: STRING
// - field_name: STRING
// - field_path: STRING (for nested fields)
// - data_type: STRING
// - is_pii: BOOLEAN
// - classification: STRING

// -----------------------------------------------------------------------------
// Transformation Node - Transformation logic
// -----------------------------------------------------------------------------
CREATE CONSTRAINT transform_id_unique IF NOT EXISTS
FOR (t:Transformation) REQUIRE t.transform_id IS UNIQUE;

// Transformation node properties:
// - transform_id: STRING
// - transform_type: STRING (DIRECT, DERIVED, LOOKUP, etc.)
// - logic: STRING (expression)
// - version: STRING

// -----------------------------------------------------------------------------
// Pipeline Node - Data pipelines
// -----------------------------------------------------------------------------
CREATE CONSTRAINT pipeline_id_unique IF NOT EXISTS
FOR (p:Pipeline) REQUIRE p.pipeline_id IS UNIQUE;

// Pipeline node properties:
// - pipeline_id: STRING
// - pipeline_name: STRING
// - schedule: STRING
// - last_run: DATETIME
// - status: STRING

// =============================================================================
// 5. DATA LINEAGE GRAPH - Relationships
// =============================================================================

// -----------------------------------------------------------------------------
// DataSource -> DataTable: CONTAINS
// -----------------------------------------------------------------------------
// (DataSource)-[:CONTAINS]->(DataTable)

// -----------------------------------------------------------------------------
// DataTable -> DataField: HAS_FIELD
// -----------------------------------------------------------------------------
// (DataTable)-[:HAS_FIELD]->(DataField)

// -----------------------------------------------------------------------------
// DataField -> DataField: TRANSFORMS_TO (lineage edge)
// -----------------------------------------------------------------------------
// (SourceField:DataField)-[:TRANSFORMS_TO {
//     transformation_type,
//     transformation_logic,
//     confidence_score,
//     effective_from,
//     effective_to
// }]->(TargetField:DataField)

// -----------------------------------------------------------------------------
// Transformation -> DataField: PRODUCES / CONSUMES
// -----------------------------------------------------------------------------
// (Transformation)-[:CONSUMES]->(SourceField:DataField)
// (Transformation)-[:PRODUCES]->(TargetField:DataField)

// -----------------------------------------------------------------------------
// Pipeline -> Transformation: EXECUTES
// -----------------------------------------------------------------------------
// (Pipeline)-[:EXECUTES {sequence}]->(Transformation)

// =============================================================================
// 6. SAMPLE CYPHER QUERIES - Fraud Detection
// =============================================================================

// Find all parties connected to a suspicious party within 3 hops
// MATCH path = (suspect:Party {party_id: $partyId})-[:TRANSACTS_WITH*1..3]-(connected:Party)
// RETURN path;

// Find potential round-tripping patterns
// MATCH (p1:Party)-[:SENDS]->(pmt1:Payment)-[:RECEIVES]->(p2:Party),
//       (p2)-[:SENDS]->(pmt2:Payment)-[:RECEIVES]->(p1)
// WHERE pmt1.created_at < pmt2.created_at
//   AND duration.between(pmt1.created_at, pmt2.created_at).days < 7
// RETURN p1, p2, pmt1, pmt2;

// Calculate network risk score based on connected high-risk parties
// MATCH (p:Party {party_id: $partyId})-[:TRANSACTS_WITH*1..2]-(connected:Party)
// WHERE connected.risk_rating IN ['high', 'very_high']
// RETURN p.party_id, COUNT(DISTINCT connected) AS high_risk_connections,
//        AVG(connected.fraud_score) AS avg_connected_fraud_score;

// Identify structuring patterns
// MATCH (p:Party)-[:SENDS]->(pmt:Payment)
// WHERE pmt.created_at > datetime() - duration('P7D')
//   AND pmt.amount >= 9000 AND pmt.amount < 10000
// WITH p, COUNT(pmt) AS just_under_threshold_count
// WHERE just_under_threshold_count >= 3
// RETURN p.party_id, p.name, just_under_threshold_count;

// =============================================================================
// 7. SAMPLE CYPHER QUERIES - Data Lineage
// =============================================================================

// Find upstream lineage for a field
// MATCH path = (target:DataField {field_name: $fieldName})<-[:TRANSFORMS_TO*]-(source:DataField)
// RETURN path;

// Find downstream impact of a source field change
// MATCH path = (source:DataField {field_id: $fieldId})-[:TRANSFORMS_TO*]->(target:DataField)
// RETURN DISTINCT target.table_id, target.field_name;

// Find all transformations between Bronze and Silver
// MATCH (bronze:DataField)<-[:HAS_FIELD]-(bt:DataTable {layer: 'BRONZE'}),
//       (silver:DataField)<-[:HAS_FIELD]-(st:DataTable {layer: 'SILVER'}),
//       (bronze)-[t:TRANSFORMS_TO]->(silver)
// RETURN bronze.field_name, t.transformation_type, t.transformation_logic, silver.field_name;

// Calculate field lineage depth
// MATCH path = (target:DataField {field_id: $fieldId})<-[:TRANSFORMS_TO*]-(source:DataField)
// WHERE NOT (source)<-[:TRANSFORMS_TO]-()
// RETURN source.field_name AS origin, length(path) AS depth;

// =============================================================================
// 8. GRAPH DATA SCIENCE ALGORITHMS (for Fraud Detection)
// =============================================================================

// Create in-memory graph projection for community detection
// CALL gds.graph.project(
//   'payment-network',
//   ['Party', 'Account'],
//   {
//     TRANSACTS_WITH: {orientation: 'UNDIRECTED'},
//     OWNS: {orientation: 'UNDIRECTED'}
//   }
// );

// Run Louvain community detection
// CALL gds.louvain.stream('payment-network')
// YIELD nodeId, communityId
// RETURN gds.util.asNode(nodeId).party_id AS party_id, communityId
// ORDER BY communityId;

// Run PageRank to find influential nodes
// CALL gds.pageRank.stream('payment-network')
// YIELD nodeId, score
// RETURN gds.util.asNode(nodeId).party_id AS party_id, score
// ORDER BY score DESC
// LIMIT 100;

// Run node similarity for finding similar transaction patterns
// CALL gds.nodeSimilarity.stream('payment-network')
// YIELD node1, node2, similarity
// RETURN gds.util.asNode(node1).party_id AS party1,
//        gds.util.asNode(node2).party_id AS party2,
//        similarity
// ORDER BY similarity DESC
// LIMIT 100;
