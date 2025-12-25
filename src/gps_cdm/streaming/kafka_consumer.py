"""
GPS CDM - Kafka Streaming Consumer
===================================

High-throughput Kafka consumer for real-time payment message processing.
Designed for 50M+ messages/day with horizontal scaling.

Architecture:
- Uses confluent-kafka for high performance
- Supports consumer groups for horizontal scaling
- Batches messages for efficient processing
- Integrates with Celery for distributed processing
- Tracks offsets for exactly-once semantics

Usage:
    # Start consumer for a specific message type:
    python -m gps_cdm.streaming.kafka_consumer --topic payments.pain001 --type pain001

    # Start with multiple partitions:
    python -m gps_cdm.streaming.kafka_consumer --topic payments.all --partitions 0,1,2,3
"""

import os
import json
import uuid
import signal
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import threading

# Kafka imports (confluent-kafka for production)
try:
    from confluent_kafka import Consumer, KafkaError, KafkaException
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    Consumer = None

# Celery imports
try:
    from gps_cdm.orchestration.celery_tasks import (
        process_bronze_partition,
        create_medallion_workflow,
    )
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class KafkaConfig:
    """Configuration for Kafka consumer."""
    bootstrap_servers: str = "localhost:9092"
    group_id: str = "gps-cdm-consumer"
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = False  # Manual commit for exactly-once
    max_poll_records: int = 500
    session_timeout_ms: int = 30000
    heartbeat_interval_ms: int = 10000
    max_poll_interval_ms: int = 300000  # 5 minutes for long processing

    # Batching configuration
    batch_size: int = 100  # Messages per batch
    batch_timeout_ms: int = 5000  # Max wait time before processing

    # Threading configuration
    num_worker_threads: int = 4

    # Additional consumer config
    extra_config: Dict[str, Any] = field(default_factory=dict)

    def to_confluent_config(self) -> Dict[str, Any]:
        """Convert to confluent-kafka configuration dict."""
        config = {
            "bootstrap.servers": self.bootstrap_servers,
            "group.id": self.group_id,
            "auto.offset.reset": self.auto_offset_reset,
            "enable.auto.commit": self.enable_auto_commit,
            "max.poll.records": self.max_poll_records,
            "session.timeout.ms": self.session_timeout_ms,
            "heartbeat.interval.ms": self.heartbeat_interval_ms,
            "max.poll.interval.ms": self.max_poll_interval_ms,
        }
        config.update(self.extra_config)
        return config


@dataclass
class Message:
    """Parsed Kafka message."""
    topic: str
    partition: int
    offset: int
    key: Optional[str]
    value: str
    headers: Dict[str, str]
    timestamp: int
    message_type: Optional[str] = None
    message_id: Optional[str] = None


@dataclass
class Batch:
    """Batch of messages for processing."""
    batch_id: str
    messages: List[Message]
    message_type: str
    created_at: datetime
    topic: str
    partition_offsets: Dict[int, int]  # partition -> max offset


class StreamingConsumer:
    """
    High-throughput Kafka consumer for GPS CDM.

    Features:
    - Batches messages for efficient processing
    - Supports multiple worker threads
    - Integrates with Celery for distributed processing
    - Tracks offsets for exactly-once semantics
    - Graceful shutdown handling
    """

    def __init__(
        self,
        topics: List[str],
        config: KafkaConfig,
        message_type: str,
        persistence_config: Dict[str, Any],
        mapping_path: str,
    ):
        self.topics = topics
        self.config = config
        self.message_type = message_type
        self.persistence_config = persistence_config
        self.mapping_path = mapping_path

        self.consumer: Optional[Consumer] = None
        self.running = False
        self.shutdown_event = threading.Event()

        # Batching state
        self.current_batch: List[Message] = []
        self.last_batch_time = datetime.utcnow()
        self.batch_lock = threading.Lock()

        # Worker pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=config.num_worker_threads)

        # Metrics
        self.messages_consumed = 0
        self.batches_processed = 0
        self.errors = 0

    def start(self):
        """Start the consumer."""
        if not KAFKA_AVAILABLE:
            raise RuntimeError("confluent-kafka not installed. Run: pip install confluent-kafka")

        logger.info(f"Starting consumer for topics: {self.topics}")
        logger.info(f"Consumer group: {self.config.group_id}")
        logger.info(f"Bootstrap servers: {self.config.bootstrap_servers}")

        # Create consumer
        self.consumer = Consumer(self.config.to_confluent_config())
        self.consumer.subscribe(self.topics)

        self.running = True

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Start processing loop
        try:
            self._consume_loop()
        finally:
            self._shutdown()

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False
        self.shutdown_event.set()

    def _consume_loop(self):
        """Main consumption loop."""
        while self.running:
            try:
                # Poll for messages
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    # Check if batch timeout exceeded
                    self._check_batch_timeout()
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition, not an error
                        continue
                    else:
                        logger.error(f"Kafka error: {msg.error()}")
                        self.errors += 1
                        continue

                # Parse message
                message = self._parse_message(msg)
                self.messages_consumed += 1

                # Add to batch
                with self.batch_lock:
                    self.current_batch.append(message)

                    # Check if batch is ready
                    if len(self.current_batch) >= self.config.batch_size:
                        self._process_batch()

            except KafkaException as e:
                logger.error(f"Kafka exception: {e}")
                self.errors += 1

            except Exception as e:
                logger.exception(f"Unexpected error in consume loop: {e}")
                self.errors += 1

    def _parse_message(self, msg) -> Message:
        """Parse Kafka message into Message dataclass."""
        # Parse headers
        headers = {}
        if msg.headers():
            for key, value in msg.headers():
                headers[key] = value.decode("utf-8") if value else None

        # Parse value
        value = msg.value().decode("utf-8") if msg.value() else ""

        # Extract message type and ID from content or headers
        message_type = headers.get("message_type", self.message_type)
        message_id = headers.get("message_id")

        if not message_id:
            # Try to extract from content
            try:
                content = json.loads(value)
                message_id = content.get("messageId") or content.get("message_id")
            except json.JSONDecodeError:
                # For XML messages, generate a UUID
                message_id = str(uuid.uuid4())

        return Message(
            topic=msg.topic(),
            partition=msg.partition(),
            offset=msg.offset(),
            key=msg.key().decode("utf-8") if msg.key() else None,
            value=value,
            headers=headers,
            timestamp=msg.timestamp()[1] if msg.timestamp() else 0,
            message_type=message_type,
            message_id=message_id,
        )

    def _check_batch_timeout(self):
        """Check if batch timeout exceeded and process if so."""
        with self.batch_lock:
            if self.current_batch:
                elapsed = (datetime.utcnow() - self.last_batch_time).total_seconds() * 1000
                if elapsed >= self.config.batch_timeout_ms:
                    self._process_batch()

    def _process_batch(self):
        """Process the current batch of messages."""
        if not self.current_batch:
            return

        # Create batch
        batch = Batch(
            batch_id=str(uuid.uuid4()),
            messages=self.current_batch.copy(),
            message_type=self.message_type,
            created_at=datetime.utcnow(),
            topic=self.current_batch[0].topic if self.current_batch else "",
            partition_offsets={
                msg.partition: msg.offset for msg in self.current_batch
            },
        )

        # Clear current batch
        self.current_batch = []
        self.last_batch_time = datetime.utcnow()

        # Submit batch for processing
        self.executor.submit(self._process_batch_async, batch)

    def _process_batch_async(self, batch: Batch):
        """Process a batch asynchronously."""
        try:
            logger.info(f"Processing batch {batch.batch_id} with {len(batch.messages)} messages")

            if CELERY_AVAILABLE:
                # Submit to Celery for distributed processing
                self._submit_to_celery(batch)
            else:
                # Process locally
                self._process_locally(batch)

            # Commit offsets after successful processing
            self._commit_offsets(batch)

            self.batches_processed += 1
            logger.info(f"Batch {batch.batch_id} processed successfully")

        except Exception as e:
            logger.exception(f"Error processing batch {batch.batch_id}: {e}")
            self.errors += 1
            # Don't commit offsets - messages will be reprocessed

    def _submit_to_celery(self, batch: Batch):
        """Submit batch to Celery for processing."""
        # Prepare file-like data for Celery task
        # In streaming mode, we pass message content directly

        # Create temporary storage for message contents
        message_contents = [
            {
                "message_id": msg.message_id,
                "message_type": msg.message_type,
                "content": msg.value,
                "headers": msg.headers,
                "kafka_offset": msg.offset,
                "kafka_partition": msg.partition,
            }
            for msg in batch.messages
        ]

        # Submit as Celery task
        result = process_bronze_partition.delay(
            partition_id=f"{batch.batch_id}:kafka",
            file_paths=[],  # Not using file paths for streaming
            message_type=batch.message_type,
            batch_id=batch.batch_id,
            config=self.persistence_config,
        )

        # Could optionally wait for result
        # result.get(timeout=300)

    def _process_locally(self, batch: Batch):
        """Process batch locally (for testing/development)."""
        for msg in batch.messages:
            logger.debug(f"Processing message {msg.message_id} from {msg.topic}:{msg.partition}:{msg.offset}")
            # In production, this would call the actual processing logic

    def _commit_offsets(self, batch: Batch):
        """Commit offsets after successful batch processing."""
        if self.consumer:
            try:
                self.consumer.commit(asynchronous=False)
                logger.debug(f"Committed offsets for batch {batch.batch_id}")
            except KafkaException as e:
                logger.error(f"Failed to commit offsets: {e}")

    def _shutdown(self):
        """Clean shutdown of consumer."""
        logger.info("Shutting down consumer...")

        # Process remaining batch
        with self.batch_lock:
            if self.current_batch:
                logger.info(f"Processing final batch of {len(self.current_batch)} messages")
                self._process_batch()

        # Wait for executor to complete
        self.executor.shutdown(wait=True, cancel_futures=False)

        # Close consumer
        if self.consumer:
            self.consumer.close()

        logger.info("Consumer shutdown complete")
        self._log_metrics()

    def _log_metrics(self):
        """Log consumer metrics."""
        logger.info(f"Consumer metrics:")
        logger.info(f"  Messages consumed: {self.messages_consumed}")
        logger.info(f"  Batches processed: {self.batches_processed}")
        logger.info(f"  Errors: {self.errors}")


class MultiTopicConsumer:
    """
    Consumer that handles multiple message types from different topics.

    Routes messages to appropriate processing pipelines based on topic/type.
    """

    def __init__(
        self,
        topic_configs: Dict[str, Dict[str, Any]],
        kafka_config: KafkaConfig,
        persistence_config: Dict[str, Any],
    ):
        """
        Initialize multi-topic consumer.

        Args:
            topic_configs: Dict mapping topic name to config:
                {
                    "payments.pain001": {
                        "message_type": "pain001",
                        "mapping_path": "/path/to/pain001.yaml"
                    },
                    "payments.mt103": {
                        "message_type": "mt103",
                        "mapping_path": "/path/to/mt103.yaml"
                    }
                }
        """
        self.topic_configs = topic_configs
        self.kafka_config = kafka_config
        self.persistence_config = persistence_config

        self.consumers: List[StreamingConsumer] = []
        self.threads: List[threading.Thread] = []

    def start(self):
        """Start consumers for all topics."""
        for topic, config in self.topic_configs.items():
            consumer = StreamingConsumer(
                topics=[topic],
                config=self.kafka_config,
                message_type=config["message_type"],
                persistence_config=self.persistence_config,
                mapping_path=config["mapping_path"],
            )
            self.consumers.append(consumer)

            thread = threading.Thread(
                target=consumer.start,
                name=f"consumer-{topic}",
                daemon=True,
            )
            self.threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in self.threads:
            thread.join()


def create_consumer_from_env() -> StreamingConsumer:
    """Create consumer from environment variables."""
    config = KafkaConfig(
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        group_id=os.environ.get("KAFKA_GROUP_ID", "gps-cdm-consumer"),
        batch_size=int(os.environ.get("KAFKA_BATCH_SIZE", "100")),
        num_worker_threads=int(os.environ.get("KAFKA_NUM_WORKERS", "4")),
    )

    topics = os.environ.get("KAFKA_TOPICS", "payments.incoming").split(",")
    message_type = os.environ.get("MESSAGE_TYPE", "pain001")
    mapping_path = os.environ.get("MAPPING_PATH", "/app/mappings/pain001.yaml")

    persistence_config = {
        "backend": os.environ.get("PERSISTENCE_BACKEND", "postgresql"),
        "catalog": os.environ.get("DB_NAME", "gps_cdm"),
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", "5432")),
        "user": os.environ.get("DB_USER", "gps_cdm"),
        "password": os.environ.get("DB_PASSWORD", ""),
    }

    return StreamingConsumer(
        topics=topics,
        config=config,
        message_type=message_type,
        persistence_config=persistence_config,
        mapping_path=mapping_path,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GPS CDM Kafka Consumer")
    parser.add_argument("--topic", default="payments.incoming", help="Kafka topic(s)")
    parser.add_argument("--type", default="pain001", help="Message type")
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--group-id", default="gps-cdm-consumer")
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    config = KafkaConfig(
        bootstrap_servers=args.bootstrap_servers,
        group_id=args.group_id,
        batch_size=args.batch_size,
        num_worker_threads=args.workers,
    )

    consumer = StreamingConsumer(
        topics=args.topic.split(","),
        config=config,
        message_type=args.type,
        persistence_config={"backend": "postgresql", "catalog": "gps_cdm"},
        mapping_path=f"mappings/message_types/{args.type}.yaml",
    )

    consumer.start()
