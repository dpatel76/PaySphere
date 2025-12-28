"""
GPS CDM - Kafka Batch Consumer with Restartability
===================================================

High-throughput Kafka consumer that integrates with MicroBatchAccumulator
for efficient bulk database writes with exactly-once semantics.

Key Features:
- Micro-batch accumulation (10K-50K records)
- PostgreSQL checkpointing for crash recovery
- Automatic recovery of in-flight batches
- Dead letter queue for failed batches
- Real-time metrics via Redis

Usage:
    # Start consumer for payment messages
    python -m gps_cdm.streaming.kafka_batch_consumer \
        --topics payment.bronze.iso20022,payment.bronze.swift \
        --group gps-cdm-bronze \
        --batch-size 10000 \
        --flush-interval 10

    # Environment variables:
    KAFKA_BOOTSTRAP_SERVERS=localhost:9092
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5433
    REDIS_URL=redis://localhost:6379
"""

import asyncio
import json
import logging
import os
import signal
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# Kafka imports
try:
    from confluent_kafka import Consumer, KafkaError, KafkaException, TopicPartition
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    Consumer = None

from gps_cdm.streaming.micro_batch_accumulator import (
    BatchState,
    CheckpointStore,
    KafkaMessage,
    MicroBatchAccumulator,
    MicroBatchTracker,
)
from gps_cdm.streaming.bulk_writer import BulkWriter


@dataclass
class ConsumerConfig:
    """Configuration for Kafka batch consumer."""
    # Kafka settings
    bootstrap_servers: str = "localhost:9092"
    group_id: str = "gps-cdm-bronze"
    auto_offset_reset: str = "earliest"
    session_timeout_ms: int = 30000
    max_poll_interval_ms: int = 300000

    # Batch settings
    max_batch_size: int = 10000
    max_wait_seconds: float = 10.0
    checkpoint_interval_seconds: float = 5.0

    # Database settings
    postgres_host: str = "localhost"
    postgres_port: int = 5433
    postgres_database: str = "gps_cdm"
    postgres_user: str = "gps_cdm_svc"
    postgres_password: str = "gps_cdm_password"

    # Recovery settings
    stale_checkpoint_threshold_seconds: int = 60
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> "ConsumerConfig":
        """Create config from environment variables."""
        return cls(
            bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            group_id=os.environ.get("KAFKA_GROUP_ID", "gps-cdm-bronze"),
            max_batch_size=int(os.environ.get("KAFKA_BATCH_SIZE", "10000")),
            max_wait_seconds=float(os.environ.get("KAFKA_FLUSH_INTERVAL", "10.0")),
            postgres_host=os.environ.get("POSTGRES_HOST", "localhost"),
            postgres_port=int(os.environ.get("POSTGRES_PORT", "5433")),
            postgres_database=os.environ.get("POSTGRES_DB", "gps_cdm"),
            postgres_user=os.environ.get("POSTGRES_USER", "gps_cdm_svc"),
            postgres_password=os.environ.get("POSTGRES_PASSWORD", "gps_cdm_password"),
        )


class KafkaBatchConsumer:
    """
    High-throughput Kafka consumer with micro-batch accumulation.

    Architecture:
    1. Kafka Consumer polls messages
    2. Messages accumulated in MicroBatchAccumulator
    3. On flush trigger (size/time), bulk write to Bronze
    4. Kafka offsets committed after successful write
    5. Checkpoints saved to PostgreSQL for recovery

    Recovery on Restart:
    1. Claim stale checkpoints from crashed consumers
    2. Resume from last committed offset
    3. Retry or DLQ incomplete batches
    """

    def __init__(
        self,
        topics: List[str],
        config: ConsumerConfig,
    ):
        self.topics = topics
        self.config = config
        self.consumer_id = f"{config.group_id}-{uuid.uuid4().hex[:8]}"

        # Kafka consumer
        self.consumer: Optional[Consumer] = None

        # Database connection
        self._db_connection = None

        # Components
        self.checkpoint_store: Optional[CheckpointStore] = None
        self.batch_tracker: Optional[MicroBatchTracker] = None
        self.bulk_writer: Optional[BulkWriter] = None
        self.accumulator: Optional[MicroBatchAccumulator] = None

        # Pending offset commits (topic-partition -> offset)
        self._pending_commits: Dict[tuple, int] = {}
        self._commit_lock = threading.Lock()

        # State
        self._running = False
        self._shutdown_event = asyncio.Event()

        # Metrics
        self.messages_consumed = 0
        self.batches_flushed = 0
        self.errors = 0

    def _get_db_connection(self):
        """Get or create database connection."""
        import psycopg2

        if self._db_connection is None or self._db_connection.closed:
            self._db_connection = psycopg2.connect(
                host=self.config.postgres_host,
                port=self.config.postgres_port,
                database=self.config.postgres_database,
                user=self.config.postgres_user,
                password=self.config.postgres_password,
            )
        return self._db_connection

    def _kafka_commit_callback(self, partition_offsets: Dict[tuple, int]) -> None:
        """
        Callback to commit Kafka offsets after successful batch write.

        Called by MicroBatchAccumulator after bulk write completes.
        """
        with self._commit_lock:
            # Merge with pending commits (keep highest offset per partition)
            for key, offset in partition_offsets.items():
                current = self._pending_commits.get(key, -1)
                self._pending_commits[key] = max(current, offset)

        # Trigger async commit
        self._do_kafka_commit()

    def _do_kafka_commit(self) -> None:
        """Commit pending Kafka offsets."""
        if not self.consumer:
            return

        with self._commit_lock:
            if not self._pending_commits:
                return

            # Build TopicPartition list
            offsets = [
                TopicPartition(topic, partition, offset + 1)  # +1 for next offset
                for (topic, partition), offset in self._pending_commits.items()
            ]
            self._pending_commits.clear()

        try:
            self.consumer.commit(offsets=offsets, asynchronous=False)
            logger.debug(f"Committed {len(offsets)} Kafka offsets")
        except KafkaException as e:
            logger.error(f"Failed to commit Kafka offsets: {e}")
            self.errors += 1

    async def start(self) -> None:
        """Start the consumer."""
        if not KAFKA_AVAILABLE:
            raise RuntimeError("confluent-kafka not installed. Run: pip install confluent-kafka")

        logger.info(f"Starting KafkaBatchConsumer {self.consumer_id}")
        logger.info(f"Topics: {self.topics}")
        logger.info(f"Group: {self.config.group_id}")
        logger.info(f"Batch size: {self.config.max_batch_size}")

        # Initialize components
        self.checkpoint_store = CheckpointStore(self._get_db_connection)
        self.batch_tracker = MicroBatchTracker(self._get_db_connection)
        self.bulk_writer = BulkWriter.create('postgresql', {
            'host': self.config.postgres_host,
            'port': self.config.postgres_port,
            'database': self.config.postgres_database,
            'user': self.config.postgres_user,
            'password': self.config.postgres_password,
        })

        self.accumulator = MicroBatchAccumulator(
            consumer_group=self.config.group_id,
            consumer_id=self.consumer_id,
            bulk_writer=self.bulk_writer,
            checkpoint_store=self.checkpoint_store,
            batch_tracker=self.batch_tracker,
            kafka_commit_callback=self._kafka_commit_callback,
            max_batch_size=self.config.max_batch_size,
            max_wait_seconds=self.config.max_wait_seconds,
            checkpoint_interval_seconds=self.config.checkpoint_interval_seconds,
            max_retries=self.config.max_retries,
        )

        # Perform recovery and start accumulator
        recovery_info = await self.accumulator.start()
        logger.info(f"Recovery complete: {recovery_info}")

        # Create Kafka consumer
        kafka_config = {
            "bootstrap.servers": self.config.bootstrap_servers,
            "group.id": self.config.group_id,
            "auto.offset.reset": self.config.auto_offset_reset,
            "enable.auto.commit": False,  # Manual commit
            "session.timeout.ms": self.config.session_timeout_ms,
            "max.poll.interval.ms": self.config.max_poll_interval_ms,
        }

        self.consumer = Consumer(kafka_config)
        self.consumer.subscribe(self.topics)

        self._running = True

        # Setup signal handlers
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self._signal_handler)

        # Start consume loop
        try:
            await self._consume_loop()
        finally:
            await self._shutdown()

    def _signal_handler(self) -> None:
        """Handle shutdown signals."""
        logger.info("Received shutdown signal")
        self._running = False
        self._shutdown_event.set()

    async def _consume_loop(self) -> None:
        """Main consumption loop."""
        while self._running:
            try:
                # Poll for messages (non-blocking with timeout)
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    # No message, just continue
                    await asyncio.sleep(0.01)
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition
                        continue
                    else:
                        logger.error(f"Kafka error: {msg.error()}")
                        self.errors += 1
                        continue

                # Parse and accumulate message
                kafka_msg = self._parse_message(msg)
                self.messages_consumed += 1

                # Add to accumulator (may trigger flush)
                result = await self.accumulator.accumulate(kafka_msg)

                if result:
                    self.batches_flushed += 1
                    if result.status == "SUCCESS":
                        logger.info(
                            f"Batch {result.batch_id} flushed: "
                            f"{result.records_written} records in {result.duration_ms:.1f}ms"
                        )
                    else:
                        logger.warning(f"Batch {result.batch_id} failed: {result.error}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in consume loop: {e}")
                self.errors += 1
                await asyncio.sleep(1.0)  # Back off on error

    def _parse_message(self, msg) -> KafkaMessage:
        """Parse Kafka message."""
        # Parse headers
        headers = {}
        if msg.headers():
            for key, value in msg.headers():
                headers[key] = value.decode("utf-8") if value else None

        # Parse value
        value = msg.value().decode("utf-8") if msg.value() else ""

        # Detect message type from headers or content
        message_type = headers.get("message_type")
        if not message_type:
            message_type = self._detect_message_type(msg.topic(), value)

        # Extract message ID
        message_id = headers.get("message_id")
        if not message_id:
            message_id = self._extract_message_id(value)

        return KafkaMessage(
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

    def _detect_message_type(self, topic: str, content: str) -> str:
        """Detect message type from topic or content."""
        # Try topic-based detection
        topic_lower = topic.lower()
        if "pain.001" in topic_lower or "pain001" in topic_lower:
            return "pain.001"
        if "pacs.008" in topic_lower or "pacs008" in topic_lower:
            return "pacs.008"
        if "mt103" in topic_lower:
            return "MT103"
        if "fedwire" in topic_lower:
            return "FEDWIRE"
        if "ach" in topic_lower:
            return "ACH"
        if "sepa" in topic_lower:
            return "SEPA"
        if "rtp" in topic_lower:
            return "RTP"

        # Try content-based detection
        content = content.strip()
        if "pain.001" in content:
            return "pain.001"
        if "pacs.008" in content:
            return "pacs.008"
        if content.startswith("{1:"):
            # SWIFT MT format
            if ":20:" in content:
                return "MT103"
            return "MT202"
        if "FEDWIRE" in content.upper():
            return "FEDWIRE"

        return "unknown"

    def _extract_message_id(self, content: str) -> str:
        """Extract message ID from content or generate one."""
        try:
            # Try JSON
            if content.strip().startswith("{"):
                data = json.loads(content)
                return (
                    data.get("messageId") or
                    data.get("message_id") or
                    data.get("MsgId") or
                    str(uuid.uuid4())
                )
        except:
            pass

        return str(uuid.uuid4())

    async def _shutdown(self) -> None:
        """Clean shutdown."""
        logger.info("Shutting down KafkaBatchConsumer...")

        # Stop accumulator (flushes remaining batches)
        if self.accumulator:
            await self.accumulator.stop()

        # Final offset commit
        self._do_kafka_commit()

        # Close Kafka consumer
        if self.consumer:
            self.consumer.close()

        # Close database connection
        if self._db_connection and not self._db_connection.closed:
            self._db_connection.close()

        # Close bulk writer
        if self.bulk_writer:
            self.bulk_writer.close()

        # Log final metrics
        logger.info(f"Consumer shutdown complete")
        logger.info(f"  Messages consumed: {self.messages_consumed}")
        logger.info(f"  Batches flushed: {self.batches_flushed}")
        logger.info(f"  Errors: {self.errors}")


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="GPS CDM Kafka Batch Consumer")
    parser.add_argument("--topics", required=True, help="Comma-separated Kafka topics")
    parser.add_argument("--group", default="gps-cdm-bronze", help="Consumer group ID")
    parser.add_argument("--batch-size", type=int, default=10000, help="Batch size")
    parser.add_argument("--flush-interval", type=float, default=10.0, help="Flush interval (seconds)")
    parser.add_argument("--bootstrap-servers", default="localhost:9092", help="Kafka bootstrap servers")
    args = parser.parse_args()

    config = ConsumerConfig.from_env()
    config.group_id = args.group
    config.max_batch_size = args.batch_size
    config.max_wait_seconds = args.flush_interval
    config.bootstrap_servers = args.bootstrap_servers

    topics = [t.strip() for t in args.topics.split(",")]

    consumer = KafkaBatchConsumer(topics=topics, config=config)
    await consumer.start()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    asyncio.run(main())
