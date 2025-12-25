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
        SET b.message_type = $message_type,
            b.source_system = $source_system,
            b.source_file = $source_file,
            b.status = $status,
            b.created_at = datetime($created_at),
            b.updated_at = datetime(),
            b.completed_at = CASE WHEN $completed_at IS NOT NULL
                             THEN datetime($completed_at) ELSE NULL END,
            b.total_records = $total_records,
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
        SET bl.batch_id = $batch_id,
            bl.layer = $layer,
            bl.input_count = $input_count,
            bl.processed_count = $processed_count,
            bl.failed_count = $failed_count,
            bl.pending_count = $pending_count,
            bl.dq_passed_count = $dq_passed_count,
            bl.dq_failed_count = $dq_failed_count,
            bl.avg_dq_score = $avg_dq_score,
            bl.started_at = CASE WHEN $started_at IS NOT NULL
                            THEN datetime($started_at) ELSE NULL END,
            bl.completed_at = CASE WHEN $completed_at IS NOT NULL
                              THEN datetime($completed_at) ELSE NULL END,
            bl.duration_ms = $duration_ms
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

        # Query entities and transforms separately to avoid nested aggregates
        query = """
        MATCH (mt:MessageType {type: $message_type})
        OPTIONAL MATCH (mt)-[:PRODUCES]->(e:CDMEntity)
        OPTIONAL MATCH (e)-[t:TRANSFORMS_TO]->(e2:CDMEntity)
        WITH mt, collect(DISTINCT e) as entities,
             collect(DISTINCT {source: e, target: e2, transform: properties(t)}) as transforms
        RETURN mt, entities, transforms
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
                transforms = [t for t in record["transforms"] if t.get("source") and t.get("target")]

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


# Singleton instance
_neo4j_service: Optional[Neo4jService] = None


def get_neo4j_service() -> Neo4jService:
    """Get or create the Neo4j service singleton."""
    global _neo4j_service
    if _neo4j_service is None:
        _neo4j_service = Neo4jService()
    return _neo4j_service
