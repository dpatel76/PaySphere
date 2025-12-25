"""
GPS CDM - Orchestration Module
==============================

Orchestration for the 4-layer medallion pipeline.

Production Stack (50M+ messages/day):
- NiFi: Data flow automation, routing, Kafka integration
- Celery: Distributed task processing with worker pools
- Kafka: High-throughput streaming ingestion
- Redis: Celery broker and result backend

Components:
- medallion_pipeline: Main pipeline API
- celery_tasks: Distributed tasks (bronze, silver, gold, dq, cdc queues)
- kafka_consumer: Streaming ingestion

Architecture:
    Bronze (raw) -> Silver (structured) -> Gold (CDM) -> Analytical (products)
"""

# Main pipeline API
from gps_cdm.orchestration.medallion_pipeline import (
    MedallionPipeline,
    run_pipeline,
    get_batch_status,
)

# Import Celery tasks if available
try:
    from gps_cdm.orchestration.celery_tasks import (
        process_bronze_partition,
        process_silver_transform,
        process_gold_aggregate,
        run_dq_evaluation,
        sync_cdc_to_neo4j,
        create_medallion_workflow,
        app as celery_app,
    )
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    process_bronze_partition = None
    process_silver_transform = None
    process_gold_aggregate = None
    run_dq_evaluation = None
    sync_cdc_to_neo4j = None
    create_medallion_workflow = None
    celery_app = None

__all__ = [
    # Main pipeline API
    "MedallionPipeline",
    "run_pipeline",
    "get_batch_status",
    # Celery tasks
    "process_bronze_partition",
    "process_silver_transform",
    "process_gold_aggregate",
    "run_dq_evaluation",
    "sync_cdc_to_neo4j",
    "create_medallion_workflow",
    "celery_app",
    "CELERY_AVAILABLE",
]
