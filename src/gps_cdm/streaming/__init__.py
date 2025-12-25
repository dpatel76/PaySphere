"""
GPS CDM - Streaming Module
==========================

High-throughput streaming ingestion for real-time payment processing.

Components:
- kafka_consumer: Kafka consumer with batching and Celery integration
- spark_streaming: Spark Structured Streaming for complex transformations

Architecture:
- NiFi handles data routing and file-based ingestion
- Kafka consumers handle streaming message ingestion
- Celery workers perform distributed processing
- PostgreSQL/Delta Lake for persistence
"""

from gps_cdm.streaming.kafka_consumer import (
    KafkaConfig,
    StreamingConsumer,
    MultiTopicConsumer,
    create_consumer_from_env,
)

__all__ = [
    "KafkaConfig",
    "StreamingConsumer",
    "MultiTopicConsumer",
    "create_consumer_from_env",
]
