"""
GPS CDM - Neo4j Service
=======================

Service for managing Neo4j knowledge graph operations:
- Batch metadata and layer-level statistics
- Aggregated DQ metrics and trends
- Schema/mapping lineage for visualization

Note: Neo4j is used for knowledge graph and batch metadata,
NOT for individual record storage.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import contextmanager

try:
    from neo4j import GraphDatabase, Driver
    HAS_NEO4J = True
except ImportError:
    HAS_NEO4J = False
    Driver = None

logger = logging.getLogger(__name__)


class Neo4jService:
    """Service for Neo4j knowledge graph operations."""

    def __init__(
        self,
        uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """
        Initialize Neo4j service.

        Args:
            uri: Neo4j bolt URI (default: from NEO4J_URI env var)
            username: Neo4j username (default: from NEO4J_USER env var)
            password: Neo4j password (default: from NEO4J_PASSWORD env var)
        """
        if not HAS_NEO4J:
            logger.warning("neo4j driver not installed. Neo4j operations will be disabled.")
            self._driver = None
            return

        self._uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self._username = username or os.getenv("NEO4J_USER", "neo4j")
        self._password = password or os.getenv("NEO4J_PASSWORD", "neo4jpassword123")

        try:
            self._driver = GraphDatabase.driver(
                self._uri,
                auth=(self._username, self._password),
            )
            # Verify connectivity
            self._driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self._uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self._driver = None

    def close(self):
        """Close the Neo4j driver connection."""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed")

    @contextmanager
    def session(self):
        """Context manager for Neo4j session."""
        if not self._driver:
            raise RuntimeError("Neo4j driver not available")
        session = self._driver.session()
        try:
            yield session
        finally:
            session.close()

    def is_available(self) -> bool:
        """Check if Neo4j is available."""
        return self._driver is not None

    def run_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a raw Cypher query and return results as list of dicts.

        Args:
            query: Cypher query string
            parameters: Optional query parameters

        Returns:
            List of result records as dictionaries
        """
        if not self._driver:
            return []

        try:
            with self.session() as session:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Neo4j query error: {e}")
            return []

    # =========================================================================
    # Batch Metadata Operations
    # =========================================================================

    def upsert_batch(self, batch: Dict[str, Any]) -> bool:
        """
        Create or update a batch node.

        Args:
            batch: Batch metadata dict with batch_id, message_type, etc.

        Returns:
            True if successful
        """
        if not self._driver:
            return False

        query = """
        MERGE (b:Batch {batch_id: $batch_id})
        ON CREATE SET
            b.message_type = $message_type,
            b.source_system = $source_system,
            b.source_file = $source_file,
            b.status = $status,
            b.created_at = datetime($created_at),
            b.updated_at = datetime(),
            b.record_count = COALESCE($total_records, 1)
        ON MATCH SET
            b.status = $status,
            b.updated_at = datetime(),
            b.completed_at = CASE WHEN $completed_at IS NOT NULL
                             THEN datetime($completed_at) ELSE b.completed_at END,
            b.record_count = COALESCE(b.record_count, 0) + COALESCE($total_records, 1),
            b.duration_ms = $duration_ms
        RETURN b.batch_id
        """

        try:
            with self.session() as session:
                result = session.run(
                    query,
                    batch_id=batch.get("batch_id"),
                    message_type=batch.get("message_type"),
                    source_system=batch.get("source_system"),
                    source_file=batch.get("source_file"),
                    status=batch.get("status", "PENDING"),
                    created_at=batch.get("created_at", datetime.utcnow().isoformat()),
                    completed_at=batch.get("completed_at"),
                    total_records=batch.get("total_records", 0),
                    duration_ms=batch.get("duration_ms"),
                )
                result.consume()
                return True
        except Exception as e:
            logger.error(f"Failed to upsert batch: {e}")
            return False

    def upsert_batch_layer(
        self,
        batch_id: str,
        layer: str,
        stats: Dict[str, Any],
    ) -> bool:
        """
        Create or update a BatchLayer node with aggregated stats.

        Args:
            batch_id: Parent batch ID
            layer: Layer name (bronze, silver, gold, analytics)
            stats: Layer statistics

        Returns:
            True if successful
        """
        if not self._driver:
            return False

        batch_layer_id = f"{batch_id}_{layer}"
        sequence_map = {"bronze": 1, "silver": 2, "gold": 3, "analytics": 4}

        query = """
        MATCH (b:Batch {batch_id: $batch_id})
        MERGE (bl:BatchLayer {batch_layer_id: $batch_layer_id})
        ON CREATE SET
            bl.batch_id = $batch_id,
            bl.layer = $layer,
            bl.input_count = $input_count,
            bl.processed_count = $processed_count,
            bl.failed_count = $failed_count,
            bl.pending_count = $pending_count,
            bl.dq_passed_count = COALESCE($dq_passed_count, 0),
            bl.dq_failed_count = COALESCE($dq_failed_count, 0),
            bl.avg_dq_score = $avg_dq_score,
            bl.started_at = CASE WHEN $started_at IS NOT NULL
                            THEN datetime($started_at) ELSE NULL END,
            bl.completed_at = CASE WHEN $completed_at IS NOT NULL
                              THEN datetime($completed_at) ELSE NULL END,
            bl.duration_ms = $duration_ms
        ON MATCH SET
            bl.input_count = COALESCE(bl.input_count, 0) + $input_count,
            bl.processed_count = COALESCE(bl.processed_count, 0) + $processed_count,
            bl.failed_count = COALESCE(bl.failed_count, 0) + $failed_count,
            bl.pending_count = COALESCE(bl.pending_count, 0) + $pending_count,
            bl.dq_passed_count = COALESCE(bl.dq_passed_count, 0) + COALESCE($dq_passed_count, 0),
            bl.dq_failed_count = COALESCE(bl.dq_failed_count, 0) + COALESCE($dq_failed_count, 0),
            bl.completed_at = CASE WHEN $completed_at IS NOT NULL
                              THEN datetime($completed_at) ELSE bl.completed_at END
        MERGE (b)-[:AT_LAYER {sequence: $sequence}]->(bl)
        RETURN bl.batch_layer_id
        """

        try:
            with self.session() as session:
                result = session.run(
                    query,
                    batch_id=batch_id,
                    batch_layer_id=batch_layer_id,
                    layer=layer,
                    sequence=sequence_map.get(layer, 0),
                    input_count=stats.get("input_count", 0),
                    processed_count=stats.get("processed_count", 0),
                    failed_count=stats.get("failed_count", 0),
                    pending_count=stats.get("pending_count", 0),
                    dq_passed_count=stats.get("dq_passed_count"),
                    dq_failed_count=stats.get("dq_failed_count"),
                    avg_dq_score=stats.get("avg_dq_score"),
                    started_at=stats.get("started_at"),
                    completed_at=stats.get("completed_at"),
                    duration_ms=stats.get("duration_ms"),
                )
                result.consume()
                return True
        except Exception as e:
            logger.error(f"Failed to upsert batch layer: {e}")
            return False

    def create_layer_promotion(
        self,
        batch_id: str,
        source_layer: str,
        target_layer: str,
        record_count: int,
        success_rate: float,
    ) -> bool:
        """
        Create a PROMOTED_TO relationship between batch layers.

        Args:
            batch_id: Batch ID
            source_layer: Source layer name
            target_layer: Target layer name
            record_count: Number of records promoted
            success_rate: Promotion success rate (0-1)

        Returns:
            True if successful
        """
        if not self._driver:
            return False

        query = """
        MATCH (source:BatchLayer {batch_layer_id: $source_id})
        MATCH (target:BatchLayer {batch_layer_id: $target_id})
        MERGE (source)-[r:PROMOTED_TO]->(target)
        SET r.record_count = $record_count,
            r.success_rate = $success_rate,
            r.promoted_at = datetime()
        RETURN type(r)
        """

        try:
            with self.session() as session:
                result = session.run(
                    query,
                    source_id=f"{batch_id}_{source_layer}",
                    target_id=f"{batch_id}_{target_layer}",
                    record_count=record_count,
                    success_rate=success_rate,
                )
                result.consume()
                return True
        except Exception as e:
            logger.error(f"Failed to create layer promotion: {e}")
            return False

    # =========================================================================
    # DQ Metrics Operations
    # =========================================================================

    def upsert_dq_metrics(
        self,
        batch_id: str,
        layer: str,
        metrics: Dict[str, Any],
    ) -> bool:
        """
        Create or update aggregated DQ metrics for a batch/layer.

        Args:
            batch_id: Batch ID
            layer: Layer name
            metrics: DQ metrics dict

        Returns:
            True if successful
        """
        if not self._driver:
            return False

        metric_id = f"{batch_id}_{layer}_dq"

        query = """
        MATCH (b:Batch {batch_id: $batch_id})
        MERGE (dq:DQMetrics {metric_id: $metric_id})
        SET dq.batch_id = $batch_id,
            dq.layer = $layer,
            dq.entity_type = $entity_type,
            dq.overall_avg_score = $overall_avg_score,
            dq.completeness_avg = $completeness_avg,
            dq.accuracy_avg = $accuracy_avg,
            dq.validity_avg = $validity_avg,
            dq.records_above_threshold = $records_above_threshold,
            dq.records_below_threshold = $records_below_threshold,
            dq.top_failing_rules = $top_failing_rules,
            dq.evaluated_at = datetime()
        MERGE (b)-[:HAS_DQ_METRICS]->(dq)
        RETURN dq.metric_id
        """

        try:
            with self.session() as session:
                result = session.run(
                    query,
                    batch_id=batch_id,
                    metric_id=metric_id,
                    layer=layer,
                    entity_type=metrics.get("entity_type", "payment"),
                    overall_avg_score=metrics.get("overall_avg_score", 0),
                    completeness_avg=metrics.get("completeness_avg", 0),
                    accuracy_avg=metrics.get("accuracy_avg", 0),
                    validity_avg=metrics.get("validity_avg", 0),
                    records_above_threshold=metrics.get("records_above_threshold", 0),
                    records_below_threshold=metrics.get("records_below_threshold", 0),
                    top_failing_rules=metrics.get("top_failing_rules", []),
                )
                result.consume()
                return True
        except Exception as e:
            logger.error(f"Failed to upsert DQ metrics: {e}")
            return False

    def upsert_exception_summary(
        self,
        batch_id: str,
        layer: str,
        summary: Dict[str, Any],
    ) -> bool:
        """
        Create or update aggregated exception summary for a batch/layer.

        Args:
            batch_id: Batch ID
            layer: Layer name
            summary: Exception summary dict

        Returns:
            True if successful
        """
        if not self._driver:
            return False

        exception_type = summary.get("exception_type", "UNKNOWN")
        summary_id = f"{batch_id}_{layer}_{exception_type}"

        query = """
        MATCH (b:Batch {batch_id: $batch_id})
        MERGE (ex:ExceptionSummary {summary_id: $summary_id})
        SET ex.batch_id = $batch_id,
            ex.layer = $layer,
            ex.exception_type = $exception_type,
            ex.severity = $severity,
            ex.count = $count,
            ex.sample_message = $sample_message,
            ex.first_seen = CASE WHEN ex.first_seen IS NULL
                            THEN datetime() ELSE ex.first_seen END,
            ex.last_seen = datetime()
        MERGE (b)-[:HAS_EXCEPTION_SUMMARY]->(ex)
        RETURN ex.summary_id
        """

        try:
            with self.session() as session:
                result = session.run(
                    query,
                    batch_id=batch_id,
                    summary_id=summary_id,
                    layer=layer,
                    exception_type=exception_type,
                    severity=summary.get("severity", "ERROR"),
                    count=summary.get("count", 0),
                    sample_message=summary.get("sample_message"),
                )
                result.consume()
                return True
        except Exception as e:
            logger.error(f"Failed to upsert exception summary: {e}")
            return False

    # =========================================================================
    # Schema/Lineage Operations
    # =========================================================================

    def upsert_message_type(self, message_type: Dict[str, Any]) -> bool:
        """
        Create or update a MessageType node.

        Args:
            message_type: Message type metadata

        Returns:
            True if successful
        """
        if not self._driver:
            return False

        query = """
        MERGE (mt:MessageType {type: $type})
        SET mt.version = $version,
            mt.name = $name,
            mt.description = $description,
            mt.format = $format
        RETURN mt.type
        """

        try:
            with self.session() as session:
                result = session.run(
                    query,
                    type=message_type.get("type"),
                    version=message_type.get("version"),
                    name=message_type.get("name"),
                    description=message_type.get("description"),
                    format=message_type.get("format", "XML"),
                )
                result.consume()
                return True
        except Exception as e:
            logger.error(f"Failed to upsert message type: {e}")
            return False

    def upsert_cdm_entity(self, entity: Dict[str, Any]) -> bool:
        """
        Create or update a CDMEntity node.

        Args:
            entity: Entity metadata

        Returns:
            True if successful
        """
        if not self._driver:
            return False

        entity_id = f"{entity.get('layer')}.{entity.get('table_name')}"

        query = """
        MERGE (e:CDMEntity {entity_id: $entity_id})
        SET e.entity_type = $entity_type,
            e.layer = $layer,
            e.description = $description
        RETURN e.entity_id
        """

        try:
            with self.session() as session:
                result = session.run(
                    query,
                    entity_id=entity_id,
                    entity_type=entity.get("table_name"),
                    layer=entity.get("layer"),
                    description=entity.get("description"),
                )
                result.consume()
                return True
        except Exception as e:
            logger.error(f"Failed to upsert CDM entity: {e}")
            return False

    def upsert_field_lineage(
        self,
        source_field: Dict[str, Any],
        target_field: Dict[str, Any],
        transform: Dict[str, Any],
    ) -> bool:
        """
        Create or update field lineage relationship.

        Args:
            source_field: Source field metadata
            target_field: Target field metadata
            transform: Transformation metadata

        Returns:
            True if successful
        """
        if not self._driver:
            return False

        source_id = f"{source_field.get('entity_id')}.{source_field.get('field_name')}"
        target_id = f"{target_field.get('entity_id')}.{target_field.get('field_name')}"

        query = """
        MERGE (source:CDMField {field_id: $source_id})
        SET source.field_path = $source_path,
            source.field_name = $source_field_name,
            source.display_name = $source_display_name,
            source.data_type = $source_data_type

        MERGE (target:CDMField {field_id: $target_id})
        SET target.field_path = $target_path,
            target.field_name = $target_field_name,
            target.display_name = $target_display_name,
            target.data_type = $target_data_type

        MERGE (target)-[r:DERIVED_FROM]->(source)
        SET r.transform_type = $transform_type,
            r.logic = $logic,
            r.xpath = $xpath

        RETURN r
        """

        try:
            with self.session() as session:
                result = session.run(
                    query,
                    source_id=source_id,
                    source_path=source_field.get("field_path"),
                    source_field_name=source_field.get("field_name"),
                    source_display_name=source_field.get("display_name"),
                    source_data_type=source_field.get("data_type"),
                    target_id=target_id,
                    target_path=target_field.get("field_path"),
                    target_field_name=target_field.get("field_name"),
                    target_display_name=target_field.get("display_name"),
                    target_data_type=target_field.get("data_type"),
                    transform_type=transform.get("type", "direct"),
                    logic=transform.get("logic"),
                    xpath=transform.get("xpath"),
                )
                result.consume()
                return True
        except Exception as e:
            logger.error(f"Failed to upsert field lineage: {e}")
            return False

    # =========================================================================
    # Query Operations
    # =========================================================================

    def get_batch_lineage(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """
        Get batch lineage with all layer stats.

        Args:
            batch_id: Batch ID

        Returns:
            Batch lineage data or None
        """
        if not self._driver:
            return None

        query = """
        MATCH (b:Batch {batch_id: $batch_id})
        OPTIONAL MATCH (b)-[:AT_LAYER]->(bl:BatchLayer)
        OPTIONAL MATCH (b)-[:HAS_DQ_METRICS]->(dq:DQMetrics)
        OPTIONAL MATCH (b)-[:HAS_EXCEPTION_SUMMARY]->(ex:ExceptionSummary)
        RETURN b,
               collect(DISTINCT bl) as layers,
               collect(DISTINCT dq) as dq_metrics,
               collect(DISTINCT ex) as exceptions
        """

        try:
            with self.session() as session:
                result = session.run(query, batch_id=batch_id)
                record = result.single()
                if not record:
                    return None

                batch_node = dict(record["b"])
                return {
                    "batch": batch_node,
                    "layers": [dict(bl) for bl in record["layers"]],
                    "dq_metrics": [dict(dq) for dq in record["dq_metrics"]],
                    "exceptions": [dict(ex) for ex in record["exceptions"]],
                }
        except Exception as e:
            logger.error(f"Failed to get batch lineage: {e}")
            return None

    def get_schema_lineage(self, message_type: str) -> Optional[Dict[str, Any]]:
        """
        Get schema lineage for a message type.

        Args:
            message_type: Message type (e.g., "pain.001")

        Returns:
            Schema lineage data or None
        """
        if not self._driver:
            return None

        # Query entities produced by this message type and transforms between them
        # Only include transforms where BOTH source and target are produced by this message type
        query = """
        MATCH (mt:MessageType {type: $message_type})
        OPTIONAL MATCH (mt)-[:PRODUCES]->(e:CDMEntity)
        WITH mt, collect(DISTINCT e) as producedEntities
        UNWIND producedEntities as e1
        OPTIONAL MATCH (e1)-[t:TRANSFORMS_TO]->(e2:CDMEntity)
        WHERE e2 IN producedEntities
        WITH mt, producedEntities,
             collect(DISTINCT CASE WHEN t IS NOT NULL THEN {source: e1, target: e2, transform: properties(t)} END) as transforms
        RETURN mt, producedEntities as entities, [t IN transforms WHERE t IS NOT NULL] as transforms
        """

        try:
            with self.session() as session:
                result = session.run(query, message_type=message_type)
                record = result.single()
                if not record:
                    return None

                # Format entities with their fields
                entities = []
                for entity in record["entities"]:
                    if entity:
                        entity_data = {"entity": dict(entity)}
                        entities.append(entity_data)

                # Filter out null transforms
                transforms = [t for t in record["transforms"] if t and t.get("source") and t.get("target")]

                return {
                    "message_type": dict(record["mt"]),
                    "entities": entities,
                    "transforms": transforms,
                }
        except Exception as e:
            logger.error(f"Failed to get schema lineage: {e}")
            return None

    def get_field_lineage_graph(
        self,
        message_type: str,
        field_name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get field lineage graph for visualization.

        Args:
            message_type: Message type
            field_name: Field name to trace

        Returns:
            Graph data with nodes and edges
        """
        if not self._driver:
            return None

        query = """
        MATCH path = (target:CDMField)-[:DERIVED_FROM*1..5]->(source:CDMField)
        WHERE target.field_name = $field_name OR source.field_name = $field_name
        WITH nodes(path) as ns, relationships(path) as rs
        UNWIND ns as n
        WITH collect(DISTINCT n) as nodes, rs
        UNWIND rs as r
        WITH nodes, collect(DISTINCT r) as edges
        RETURN nodes, edges
        """

        try:
            with self.session() as session:
                result = session.run(query, field_name=field_name)
                record = result.single()
                if not record:
                    return None

                nodes = [
                    {
                        "id": node["field_id"],
                        "label": node["display_name"],
                        "field_name": node["field_name"],
                        "data_type": node["data_type"],
                    }
                    for node in record["nodes"]
                ]

                edges = [
                    {
                        "source": edge.start_node["field_id"],
                        "target": edge.end_node["field_id"],
                        "transform_type": edge.get("transform_type"),
                        "logic": edge.get("logic"),
                    }
                    for edge in record["edges"]
                ]

                return {"nodes": nodes, "edges": edges}
        except Exception as e:
            logger.error(f"Failed to get field lineage graph: {e}")
            return None

    def get_processing_bottlenecks(
        self,
        hours_back: int = 24,
    ) -> List[Dict[str, Any]]:
        """
        Get processing bottlenecks by layer.

        Args:
            hours_back: Hours to look back

        Returns:
            List of bottleneck stats by layer
        """
        if not self._driver:
            return []

        query = """
        MATCH (bl:BatchLayer)
        WHERE bl.completed_at IS NOT NULL
          AND bl.completed_at > datetime() - duration({hours: $hours_back})
        RETURN bl.layer as layer,
               avg(bl.duration_ms) as avg_duration_ms,
               sum(bl.failed_count) as total_failures,
               sum(bl.processed_count) as total_processed,
               count(bl) as batch_count
        ORDER BY avg_duration_ms DESC
        """

        try:
            with self.session() as session:
                result = session.run(query, hours_back=hours_back)
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Failed to get processing bottlenecks: {e}")
            return []

    def get_dq_trends(
        self,
        message_type: str,
        days_back: int = 7,
    ) -> List[Dict[str, Any]]:
        """
        Get DQ score trends over time.

        Args:
            message_type: Message type filter
            days_back: Days to look back

        Returns:
            List of DQ trend data points
        """
        if not self._driver:
            return []

        query = """
        MATCH (b:Batch)-[:HAS_DQ_METRICS]->(dq:DQMetrics)
        WHERE b.message_type = $message_type
          AND b.created_at > datetime() - duration({days: $days_back})
        RETURN date(b.created_at) as date,
               avg(dq.overall_avg_score) as avg_score,
               sum(dq.records_above_threshold) as passed,
               sum(dq.records_below_threshold) as failed
        ORDER BY date
        """

        try:
            with self.session() as session:
                result = session.run(
                    query,
                    message_type=message_type,
                    days_back=days_back,
                )
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Failed to get DQ trends: {e}")
            return []

    # =========================================================================
    # Dynamic Mapping Sync Operations
    # =========================================================================

    def sync_message_format_from_db(self, format_data: Dict[str, Any]) -> bool:
        """
        Sync a message format from PostgreSQL mapping.message_formats to Neo4j.

        Args:
            format_data: Message format record from database

        Returns:
            True if successful
        """
        if not self._driver:
            return False

        query = """
        MERGE (mt:MessageType {type: $format_id})
        SET mt.format_name = $format_name,
            mt.format_family = $format_family,
            mt.version = $version,
            mt.description = $description,
            mt.bronze_table = $bronze_table,
            mt.silver_table = $silver_table,
            mt.is_active = $is_active,
            mt.synced_at = datetime()
        RETURN mt.type
        """

        try:
            with self.session() as session:
                result = session.run(
                    query,
                    format_id=format_data.get("format_id"),
                    format_name=format_data.get("format_name"),
                    format_family=format_data.get("format_family"),
                    version=format_data.get("version"),
                    description=format_data.get("description"),
                    bronze_table=format_data.get("bronze_table"),
                    silver_table=format_data.get("silver_table"),
                    is_active=format_data.get("is_active", True),
                )
                result.consume()
                return True
        except Exception as e:
            logger.error(f"Failed to sync message format: {e}")
            return False

    def sync_silver_field_mapping(
        self,
        format_id: str,
        mapping: Dict[str, Any],
    ) -> bool:
        """
        Sync a silver field mapping from PostgreSQL to Neo4j.

        Creates a lineage relationship: Bronze -> Silver field mapping.

        Args:
            format_id: Message format ID
            mapping: Field mapping record

        Returns:
            True if successful
        """
        if not self._driver:
            return False

        source_id = f"bronze.raw_content.{mapping.get('source_json_path', '').replace('.', '_')}"
        target_id = f"silver.{mapping.get('format_id', format_id)}.{mapping.get('target_column')}"

        query = """
        // Ensure message type exists
        MERGE (mt:MessageType {type: $format_id})

        // Create source field (bronze raw content)
        MERGE (source:CDMField {field_id: $source_id})
        SET source.zone = 'bronze',
            source.table_name = 'raw_payment_messages',
            source.field_name = $source_json_path,
            source.json_path = $source_json_path,
            source.data_type = 'json'

        // Create target field (silver column)
        MERGE (target:CDMField {field_id: $target_id})
        SET target.zone = 'silver',
            target.table_name = $silver_table,
            target.field_name = $target_column,
            target.display_name = $display_name,
            target.data_type = $target_data_type,
            target.is_required = $is_required,
            target.is_primary_key = $is_primary_key

        // Create derived from relationship with transform info
        MERGE (target)-[r:DERIVED_FROM]->(source)
        SET r.format_id = $format_id,
            r.transform_type = $transform_type,
            r.transform_function = $transform_function,
            r.default_value = $default_value,
            r.max_length = $max_length,
            r.validation_regex = $validation_regex,
            r.synced_at = datetime()

        // Link target to message type
        MERGE (mt)-[:PRODUCES]->(target)

        RETURN r
        """

        try:
            with self.session() as session:
                result = session.run(
                    query,
                    format_id=format_id,
                    source_id=source_id,
                    target_id=target_id,
                    source_json_path=mapping.get("source_json_path", ""),
                    silver_table=mapping.get("silver_table", f"stg_{format_id.replace('.', '_')}"),
                    target_column=mapping.get("target_column"),
                    display_name=mapping.get("display_name", mapping.get("target_column")),
                    target_data_type=mapping.get("target_data_type", "VARCHAR"),
                    is_required=mapping.get("is_required", False),
                    is_primary_key=mapping.get("is_primary_key", False),
                    transform_type=mapping.get("transform_type", "direct"),
                    transform_function=mapping.get("transform_function"),
                    default_value=mapping.get("default_value"),
                    max_length=mapping.get("max_length"),
                    validation_regex=mapping.get("validation_regex"),
                )
                result.consume()
                return True
        except Exception as e:
            logger.error(f"Failed to sync silver field mapping: {e}")
            return False

    def sync_gold_field_mapping(
        self,
        format_id: str,
        mapping: Dict[str, Any],
    ) -> bool:
        """
        Sync a gold field mapping from PostgreSQL to Neo4j.

        Creates a lineage relationship: Silver -> Gold field mapping.

        Args:
            format_id: Message format ID
            mapping: Field mapping record

        Returns:
            True if successful
        """
        if not self._driver:
            return False

        source_id = f"silver.{format_id}.{mapping.get('source_silver_column')}"
        target_id = f"gold.{mapping.get('target_gold_table')}.{mapping.get('target_gold_column')}"

        query = """
        // Ensure message type exists
        MERGE (mt:MessageType {type: $format_id})

        // Create source field (silver column)
        MERGE (source:CDMField {field_id: $source_id})
        SET source.zone = 'silver',
            source.field_name = $source_silver_column

        // Create target field (gold column)
        MERGE (target:CDMField {field_id: $target_id})
        SET target.zone = 'gold',
            target.table_name = $target_gold_table,
            target.entity_type = $entity_type,
            target.field_name = $target_gold_column,
            target.display_name = $display_name,
            target.data_type = $target_data_type,
            target.is_required = $is_required

        // Create derived from relationship
        MERGE (target)-[r:DERIVED_FROM]->(source)
        SET r.format_id = $format_id,
            r.transform_type = $transform_type,
            r.transform_function = $transform_function,
            r.synced_at = datetime()

        // Link gold entity to message type
        MERGE (e:CDMEntity {entity_id: $entity_id})
        SET e.entity_type = $entity_type,
            e.table_name = $target_gold_table,
            e.layer = 'gold'
        MERGE (mt)-[:PRODUCES]->(e)
        MERGE (e)-[:HAS_FIELD]->(target)

        RETURN r
        """

        entity_id = f"gold.{mapping.get('target_gold_table')}"

        try:
            with self.session() as session:
                result = session.run(
                    query,
                    format_id=format_id,
                    source_id=source_id,
                    target_id=target_id,
                    entity_id=entity_id,
                    source_silver_column=mapping.get("source_silver_column"),
                    target_gold_table=mapping.get("target_gold_table"),
                    target_gold_column=mapping.get("target_gold_column"),
                    entity_type=mapping.get("entity_type"),
                    display_name=mapping.get("display_name", mapping.get("target_gold_column")),
                    target_data_type=mapping.get("target_data_type", "VARCHAR"),
                    is_required=mapping.get("is_required", False),
                    transform_type=mapping.get("transform_type", "direct"),
                    transform_function=mapping.get("transform_function"),
                )
                result.consume()
                return True
        except Exception as e:
            logger.error(f"Failed to sync gold field mapping: {e}")
            return False

    def sync_all_mappings_from_postgres(self) -> Dict[str, int]:
        """
        Sync all dynamic field mappings from PostgreSQL to Neo4j.

        Reads from mapping.message_formats, mapping.silver_field_mappings,
        and mapping.gold_field_mappings tables.

        Returns:
            Dict with counts of synced records
        """
        import psycopg2

        stats = {
            "message_formats": 0,
            "silver_mappings": 0,
            "gold_mappings": 0,
            "errors": 0,
        }

        try:
            # Connect to PostgreSQL
            conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", 5433)),
                database=os.getenv("POSTGRES_DB", "gps_cdm"),
                user=os.getenv("POSTGRES_USER", "gps_cdm_svc"),
                password=os.getenv("POSTGRES_PASSWORD", "gps_cdm_password"),
            )
            cursor = conn.cursor()

            # Sync message formats
            cursor.execute("SELECT * FROM mapping.message_formats WHERE is_active = true")
            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                format_data = dict(zip(columns, row))
                if self.sync_message_format_from_db(format_data):
                    stats["message_formats"] += 1
                else:
                    stats["errors"] += 1

            # Sync silver field mappings
            cursor.execute("SELECT * FROM mapping.silver_field_mappings WHERE is_active = true")
            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                mapping = dict(zip(columns, row))
                if self.sync_silver_field_mapping(mapping.get("format_id"), mapping):
                    stats["silver_mappings"] += 1
                else:
                    stats["errors"] += 1

            # Sync gold field mappings
            cursor.execute("SELECT * FROM mapping.gold_field_mappings WHERE is_active = true")
            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                mapping = dict(zip(columns, row))
                if self.sync_gold_field_mapping(mapping.get("format_id"), mapping):
                    stats["gold_mappings"] += 1
                else:
                    stats["errors"] += 1

            conn.close()
            logger.info(f"Synced mappings to Neo4j: {stats}")

        except Exception as e:
            logger.error(f"Failed to sync mappings from PostgreSQL: {e}")
            stats["errors"] += 1

        return stats

    def get_dynamic_field_lineage(
        self,
        format_id: str,
        target_zone: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get field lineage for a message format from dynamic mappings.

        Args:
            format_id: Message format ID (e.g., 'pain.001')
            target_zone: Optional filter for 'silver' or 'gold'

        Returns:
            List of field lineage records
        """
        if not self._driver:
            return []

        zone_filter = ""
        if target_zone:
            zone_filter = f"AND target.zone = '{target_zone}'"

        query = f"""
        MATCH (mt:MessageType {{type: $format_id}})
        MATCH (target:CDMField)-[r:DERIVED_FROM]->(source:CDMField)
        WHERE r.format_id = $format_id {zone_filter}
        RETURN source.field_id as source_field,
               source.json_path as source_path,
               source.zone as source_zone,
               target.field_id as target_field,
               target.field_name as target_column,
               target.zone as target_zone,
               target.table_name as target_table,
               target.data_type as data_type,
               r.transform_type as transform_type,
               r.transform_function as transform_function
        ORDER BY target.zone, target.table_name, target.field_name
        """

        try:
            with self.session() as session:
                result = session.run(query, format_id=format_id)
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Failed to get dynamic field lineage: {e}")
            return []


# Singleton instance
_neo4j_service: Optional[Neo4jService] = None


def get_neo4j_service() -> Neo4jService:
    """Get or create the Neo4j service singleton."""
    global _neo4j_service
    if _neo4j_service is None:
        _neo4j_service = Neo4jService()
    return _neo4j_service
