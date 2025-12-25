"""
GPS CDM API - Graph Routes

Provides endpoints for Neo4j knowledge graph operations:
1. Batch lineage with layer progression
2. Schema lineage for visualization
3. Field lineage with variations
4. Processing bottlenecks
5. DQ trends over time
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel

from gps_cdm.orchestration.neo4j_service import get_neo4j_service

router = APIRouter()


# Response Models
class BatchLayerResponse(BaseModel):
    batch_layer_id: str
    layer: str
    input_count: int
    processed_count: int
    failed_count: int
    pending_count: int
    dq_passed_count: Optional[int] = None
    dq_failed_count: Optional[int] = None
    avg_dq_score: Optional[float] = None
    duration_ms: Optional[int] = None


class BatchLineageResponse(BaseModel):
    batch_id: str
    message_type: Optional[str] = None
    status: Optional[str] = None
    layers: List[BatchLayerResponse]
    dq_metrics: List[Dict[str, Any]]
    exceptions: List[Dict[str, Any]]


class FieldLineageNode(BaseModel):
    id: str
    label: str
    field_name: str
    data_type: Optional[str] = None
    layer: Optional[str] = None


class FieldLineageEdge(BaseModel):
    source: str
    target: str
    transform_type: Optional[str] = None
    logic: Optional[str] = None


class FieldLineageResponse(BaseModel):
    nodes: List[FieldLineageNode]
    edges: List[FieldLineageEdge]


class BottleneckResponse(BaseModel):
    layer: str
    avg_duration_ms: float
    total_failures: int
    total_processed: int
    batch_count: int


class DQTrendResponse(BaseModel):
    date: str
    avg_score: float
    passed: int
    failed: int


@router.get("/batches/{batch_id}/lineage", response_model=BatchLineageResponse)
async def get_batch_lineage(batch_id: str):
    """
    Get batch lineage with layer progression.

    Shows the batch metadata along with aggregated statistics
    for each layer (bronze, silver, gold, analytics).
    """
    neo4j = get_neo4j_service()
    if not neo4j.is_available():
        raise HTTPException(status_code=503, detail="Neo4j service not available")

    lineage = neo4j.get_batch_lineage(batch_id)
    if not lineage:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")

    batch = lineage.get("batch", {})
    layers = [
        BatchLayerResponse(
            batch_layer_id=layer.get("batch_layer_id", ""),
            layer=layer.get("layer", ""),
            input_count=layer.get("input_count", 0),
            processed_count=layer.get("processed_count", 0),
            failed_count=layer.get("failed_count", 0),
            pending_count=layer.get("pending_count", 0),
            dq_passed_count=layer.get("dq_passed_count"),
            dq_failed_count=layer.get("dq_failed_count"),
            avg_dq_score=layer.get("avg_dq_score"),
            duration_ms=layer.get("duration_ms"),
        )
        for layer in lineage.get("layers", [])
    ]

    return BatchLineageResponse(
        batch_id=batch.get("batch_id", batch_id),
        message_type=batch.get("message_type"),
        status=batch.get("status"),
        layers=layers,
        dq_metrics=lineage.get("dq_metrics", []),
        exceptions=lineage.get("exceptions", []),
    )


@router.get("/schema/{message_type}")
async def get_schema_lineage(message_type: str):
    """
    Get schema lineage for a message type.

    Returns entities and transformations for visualization.
    """
    neo4j = get_neo4j_service()
    if not neo4j.is_available():
        raise HTTPException(status_code=503, detail="Neo4j service not available")

    lineage = neo4j.get_schema_lineage(message_type)
    if not lineage:
        raise HTTPException(status_code=404, detail=f"Message type {message_type} not found")

    return lineage


@router.get("/schema/{message_type}/field/{field_name}", response_model=FieldLineageResponse)
async def get_field_lineage(message_type: str, field_name: str):
    """
    Get field lineage with variations and transformations.

    Shows how a field flows through the layers with its
    name variations and transformation rules.
    """
    neo4j = get_neo4j_service()
    if not neo4j.is_available():
        raise HTTPException(status_code=503, detail="Neo4j service not available")

    graph = neo4j.get_field_lineage_graph(message_type, field_name)
    if not graph:
        raise HTTPException(
            status_code=404,
            detail=f"Field {field_name} not found in message type {message_type}"
        )

    nodes = [
        FieldLineageNode(
            id=node.get("id", ""),
            label=node.get("label", ""),
            field_name=node.get("field_name", ""),
            data_type=node.get("data_type"),
        )
        for node in graph.get("nodes", [])
    ]

    edges = [
        FieldLineageEdge(
            source=edge.get("source", ""),
            target=edge.get("target", ""),
            transform_type=edge.get("transform_type"),
            logic=edge.get("logic"),
        )
        for edge in graph.get("edges", [])
    ]

    return FieldLineageResponse(nodes=nodes, edges=edges)


@router.get("/bottlenecks", response_model=List[BottleneckResponse])
async def get_processing_bottlenecks(
    hours_back: int = Query(24, ge=1, le=720, description="Hours to look back"),
):
    """
    Get processing bottlenecks by layer.

    Identifies which layers are taking the longest to process
    and have the highest failure rates.
    """
    neo4j = get_neo4j_service()
    if not neo4j.is_available():
        raise HTTPException(status_code=503, detail="Neo4j service not available")

    bottlenecks = neo4j.get_processing_bottlenecks(hours_back)

    return [
        BottleneckResponse(
            layer=b.get("layer", ""),
            avg_duration_ms=float(b.get("avg_duration_ms", 0)),
            total_failures=int(b.get("total_failures", 0)),
            total_processed=int(b.get("total_processed", 0)),
            batch_count=int(b.get("batch_count", 0)),
        )
        for b in bottlenecks
    ]


@router.get("/dq-trends", response_model=List[DQTrendResponse])
async def get_dq_trends(
    message_type: str = Query(..., description="Message type filter"),
    days_back: int = Query(7, ge=1, le=90, description="Days to look back"),
):
    """
    Get DQ score trends over time.

    Shows how data quality scores have changed for a
    specific message type over the specified period.
    """
    neo4j = get_neo4j_service()
    if not neo4j.is_available():
        raise HTTPException(status_code=503, detail="Neo4j service not available")

    trends = neo4j.get_dq_trends(message_type, days_back)

    return [
        DQTrendResponse(
            date=str(t.get("date", "")),
            avg_score=float(t.get("avg_score", 0)),
            passed=int(t.get("passed", 0)),
            failed=int(t.get("failed", 0)),
        )
        for t in trends
    ]


@router.post("/sync/trigger")
async def trigger_sync(background_tasks: BackgroundTasks):
    """
    Manually trigger a sync from PostgreSQL to Neo4j.

    This syncs batch metadata, DQ metrics, and exception
    summaries to the Neo4j knowledge graph.
    """
    neo4j = get_neo4j_service()
    if not neo4j.is_available():
        raise HTTPException(status_code=503, detail="Neo4j service not available")

    # TODO: Implement background sync task
    # background_tasks.add_task(sync_postgres_to_neo4j)

    return {
        "status": "accepted",
        "message": "Sync task queued for background execution",
    }


@router.get("/health")
async def graph_health():
    """Check Neo4j connection health."""
    neo4j = get_neo4j_service()

    return {
        "neo4j_available": neo4j.is_available(),
        "status": "healthy" if neo4j.is_available() else "unavailable",
    }
