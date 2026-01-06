"""
GPS CDM - Zone-Separated Kafka Consumers
=========================================

Implements the target architecture where each zone (Bronze, Silver, Gold) has
dedicated Kafka topics and consumers, with proper separation of concerns.

Architecture:
  NiFi → bronze.{msg_type} → BronzeConsumer → silver.{msg_type} → SilverConsumer → gold.{msg_type} → GoldConsumer

Each zone:
  - Consumes from its input topic
  - Processes messages using Celery tasks
  - Publishes IDs to the next zone's topic (except Gold which is terminal)
"""

import json
import logging
import re
import signal
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class ZoneConsumerConfig:
    """Configuration for zone-specific Kafka consumers."""

    # Kafka settings
    bootstrap_servers: str = "localhost:9092"
    group_id_prefix: str = "gps-cdm"  # Will be suffixed with zone name

    # Consumer settings
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = False  # Manual commit for exactly-once
    max_poll_records: int = 100
    session_timeout_ms: int = 30000
    heartbeat_interval_ms: int = 10000
    max_poll_interval_ms: int = 300000  # 5 minutes

    # Batching settings (for micro-batching within zone)
    batch_size: int = 50
    batch_timeout_seconds: float = 5.0

    # Threading
    num_workers: int = 4

    # Celery settings
    celery_timeout_seconds: int = 60

    # Retry settings
    max_retries: int = 3
    retry_backoff_seconds: float = 1.0


@dataclass
class MessageTypeConfig:
    """Configuration for supported message types."""

    # All supported message types with their priorities (higher = more workers)
    MESSAGE_TYPES: Dict[str, int] = field(default_factory=lambda: {
        # ISO 20022 (high volume)
        'pain.001': 3, 'pain.002': 2, 'pain.008': 2,
        'pacs.002': 2, 'pacs.003': 2, 'pacs.004': 2, 'pacs.008': 3, 'pacs.009': 2,
        'camt.052': 1, 'camt.053': 2, 'camt.054': 1,

        # SWIFT MT (high volume)
        'MT103': 3, 'MT202': 2, 'MT940': 1, 'MT101': 1, 'MT199': 1,

        # US Domestic
        'FEDWIRE': 3, 'ACH': 3, 'CHIPS': 2, 'RTP': 2, 'FEDNOW': 2,

        # UK
        'CHAPS': 2, 'BACS': 2, 'FPS': 2,

        # Europe
        'SEPA': 3, 'TARGET2': 2,

        # APAC
        'NPP': 2, 'UPI': 2, 'PIX': 2, 'INSTAPAY': 1, 'PAYNOW': 1, 'PROMPTPAY': 1,
        'MEPS_PLUS': 1, 'CNAPS': 1, 'BOJNET': 1, 'KFTC': 1, 'RTGS_HK': 1,

        # Middle East
        'SARIE': 1, 'UAEFTS': 1,
    })


# =============================================================================
# FORMAT DETECTION
# =============================================================================

class MessageFormatDetector:
    """Detects message format from content, not filename."""

    @staticmethod
    def detect(content: str) -> str:
        """
        Detect message format from content.

        Returns:
            One of: SWIFT_MT, XML, JSON, FIXED, TAG_VALUE, RAW
        """
        content = content.strip()

        # SWIFT MT block format: {1:...}{2:...}{4:...}
        if content.startswith('{1:') or content.startswith('{2:'):
            return 'SWIFT_MT'

        # XML format
        if content.startswith('<?xml') or content.startswith('<Document') or content.startswith('<'):
            return 'XML'

        # JSON format (but not SWIFT which also starts with {)
        if (content.startswith('{') or content.startswith('[')) and not re.match(r'\{\d:', content):
            try:
                json.loads(content)
                return 'JSON'
            except json.JSONDecodeError:
                pass

        # NACHA/ACH fixed-width (lines of 94 characters)
        lines = content.split('\n')
        if lines and all(len(line.rstrip()) == 94 or len(line.rstrip()) == 0 for line in lines[:5] if line.strip()):
            return 'FIXED'

        # FEDWIRE tag-value format: {NNNN}value
        if re.search(r'\{\d{4}\}', content):
            return 'TAG_VALUE'

        return 'RAW'


# =============================================================================
# BASE ZONE CONSUMER
# =============================================================================

class ZoneConsumer:
    """
    Base class for zone-specific Kafka consumers.

    Handles:
    - Consuming from zone-specific topics
    - Batching messages for efficiency
    - Dispatching to Celery tasks
    - Publishing output IDs to next zone's topic
    - Error handling and DLQ
    """

    ZONE: str = None  # Override in subclass: 'bronze', 'silver', 'gold'
    CELERY_TASK: str = None  # Override in subclass
    OUTPUT_ZONE: Optional[str] = None  # None for terminal zone (gold)

    def __init__(
        self,
        message_types: List[str],
        config: Optional[ZoneConsumerConfig] = None,
    ):
        self.message_types = message_types
        self.config = config or ZoneConsumerConfig()
        self.topics = [f"{self.ZONE}.{mt}" for mt in message_types]

        self._consumer: Optional[KafkaConsumer] = None
        self._producer: Optional[KafkaProducer] = None
        self._celery_app = None

        self._running = False
        self._shutdown_event = threading.Event()
        self._executor: Optional[ThreadPoolExecutor] = None

        # Batch accumulation
        self._current_batch: List[Dict[str, Any]] = []
        self._batch_start_time: Optional[float] = None
        self._batch_lock = threading.Lock()

        # Statistics
        self._messages_consumed = 0
        self._messages_processed = 0
        self._messages_failed = 0

    def _get_consumer(self) -> KafkaConsumer:
        """Get or create Kafka consumer."""
        if self._consumer is None:
            self._consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=self.config.bootstrap_servers,
                group_id=f"{self.config.group_id_prefix}-{self.ZONE}",
                auto_offset_reset=self.config.auto_offset_reset,
                enable_auto_commit=self.config.enable_auto_commit,
                max_poll_records=self.config.max_poll_records,
                session_timeout_ms=self.config.session_timeout_ms,
                heartbeat_interval_ms=self.config.heartbeat_interval_ms,
                max_poll_interval_ms=self.config.max_poll_interval_ms,
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                value_deserializer=lambda v: v.decode('utf-8') if v else None,
            )
            logger.info(f"[{self.ZONE}] Consumer created for topics: {self.topics}")
        return self._consumer

    def _get_producer(self) -> Optional[KafkaProducer]:
        """Get or create Kafka producer for next zone."""
        if self.OUTPUT_ZONE is None:
            return None

        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=self.config.bootstrap_servers,
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                value_serializer=lambda v: v.encode('utf-8') if v else None,
                acks='all',
            )
            logger.info(f"[{self.ZONE}] Producer created for {self.OUTPUT_ZONE} zone")
        return self._producer

    def _get_celery_app(self):
        """Get Celery app (lazy initialization)."""
        if self._celery_app is None:
            from gps_cdm.orchestration.celery_tasks import celery_app
            self._celery_app = celery_app
        return self._celery_app

    def _extract_headers(self, msg) -> Dict[str, str]:
        """Extract headers from Kafka message."""
        headers = {}
        if msg.headers:
            for key, value in msg.headers:
                if isinstance(value, bytes):
                    headers[key] = value.decode('utf-8')
                else:
                    headers[key] = str(value)
        return headers

    def _build_task_kwargs(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build kwargs for Celery task. Override in subclass.

        Args:
            messages: List of consumed messages with content and metadata

        Returns:
            Kwargs dict for Celery task
        """
        raise NotImplementedError("Subclass must implement _build_task_kwargs")

    def _publish_to_next_zone(
        self,
        output_ids: List[str],
        message_type: str,
        batch_id: str,
    ) -> None:
        """Publish output IDs to next zone's Kafka topic."""
        if self.OUTPUT_ZONE is None:
            return

        producer = self._get_producer()
        topic = f"{self.OUTPUT_ZONE}.{message_type}"

        for output_id in output_ids:
            headers = [
                ('message_type', message_type.encode('utf-8')),
                ('batch_id', batch_id.encode('utf-8')),
                ('source_zone', self.ZONE.encode('utf-8')),
                ('timestamp', datetime.utcnow().isoformat().encode('utf-8')),
            ]

            producer.send(
                topic=topic,
                key=batch_id,
                value=output_id,
                headers=headers,
            )

        producer.flush()
        logger.info(f"[{self.ZONE}] Published {len(output_ids)} IDs to {topic}")

    def _publish_to_dlq(
        self,
        message: Dict[str, Any],
        error: str,
        error_code: str = 'UNKNOWN_ERROR',
    ) -> None:
        """Publish failed message to Dead Letter Queue topic."""
        # Always create a dedicated DLQ producer with JSON serializer
        # (different from the main producer which uses string serializer)
        if not hasattr(self, '_dlq_producer') or self._dlq_producer is None:
            self._dlq_producer = KafkaProducer(
                bootstrap_servers=self.config.bootstrap_servers,
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                value_serializer=lambda v: json.dumps(v).encode('utf-8') if v else None,
            )
        producer = self._dlq_producer

        dlq_topic = f"dlq.{self.ZONE}"
        dlq_message = {
            'original_message': message,
            'error': error,
            'error_code': error_code,
            'zone': self.ZONE,
            'timestamp': datetime.utcnow().isoformat(),
        }

        producer.send(
            topic=dlq_topic,
            key=message.get('batch_id', 'unknown'),
            value=dlq_message,
        )
        producer.flush()
        logger.warning(f"[{self.ZONE}] Published to DLQ: {error}")

    def _process_batch(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a batch of messages using Celery.

        Args:
            messages: List of messages to process

        Returns:
            Celery task result
        """
        if not messages:
            return {'status': 'EMPTY', 'output_ids': []}

        celery = self._get_celery_app()
        task_kwargs = self._build_task_kwargs(messages)

        try:
            result = celery.send_task(
                self.CELERY_TASK,
                kwargs=task_kwargs,
            )

            # Wait for result
            output = result.get(timeout=self.config.celery_timeout_seconds)
            return output

        except Exception as e:
            logger.error(f"[{self.ZONE}] Celery task failed: {e}")
            raise

    def _should_flush_batch(self) -> bool:
        """Check if current batch should be flushed."""
        with self._batch_lock:
            if not self._current_batch:
                return False

            # Size threshold
            if len(self._current_batch) >= self.config.batch_size:
                return True

            # Time threshold
            if self._batch_start_time:
                elapsed = time.time() - self._batch_start_time
                if elapsed >= self.config.batch_timeout_seconds:
                    return True

            return False

    def _flush_batch(self) -> None:
        """Flush current batch to Celery."""
        with self._batch_lock:
            if not self._current_batch:
                return

            batch = self._current_batch.copy()
            self._current_batch = []
            self._batch_start_time = None

        if not batch:
            return

        # Group by message_type
        by_type: Dict[str, List[Dict]] = {}
        for msg in batch:
            mt = msg.get('message_type', 'UNKNOWN')
            if mt not in by_type:
                by_type[mt] = []
            by_type[mt].append(msg)

        # Process each message type batch
        for message_type, type_messages in by_type.items():
            batch_id = type_messages[0].get('batch_id', str(uuid.uuid4()))

            try:
                result = self._process_batch(type_messages)

                if result.get('status') in ('SUCCESS', 'PARTIAL'):
                    # Get output IDs based on zone
                    if self.ZONE == 'bronze':
                        output_ids = result.get('raw_ids', [])
                    elif self.ZONE == 'silver':
                        output_ids = result.get('stg_ids', [])
                    else:  # gold
                        output_ids = result.get('instruction_ids', [])

                    # Publish to next zone
                    if output_ids and self.OUTPUT_ZONE:
                        self._publish_to_next_zone(output_ids, message_type, batch_id)

                    self._messages_processed += len(output_ids)

                    # Track failures
                    failed = result.get('failed', [])
                    self._messages_failed += len(failed)
                    for fail in failed:
                        self._publish_to_dlq(fail, fail.get('error', 'Unknown error'))

                else:
                    # Entire batch failed
                    self._messages_failed += len(type_messages)
                    for msg in type_messages:
                        self._publish_to_dlq(msg, result.get('error', 'Batch processing failed'))

            except Exception as e:
                logger.error(f"[{self.ZONE}] Batch processing error: {e}")
                self._messages_failed += len(type_messages)
                for msg in type_messages:
                    self._publish_to_dlq(msg, str(e))

    def run(self) -> None:
        """Main consumer loop."""
        self._running = True
        self._executor = ThreadPoolExecutor(max_workers=self.config.num_workers)

        consumer = self._get_consumer()

        logger.info(f"[{self.ZONE}] Consumer started for message types: {self.message_types}")

        try:
            while self._running and not self._shutdown_event.is_set():
                # Poll for messages
                records = consumer.poll(timeout_ms=1000)

                for topic_partition, messages in records.items():
                    for msg in messages:
                        self._messages_consumed += 1

                        # Extract metadata
                        headers = self._extract_headers(msg)
                        message_type = headers.get('message_type')

                        # Derive message_type from topic if not in headers
                        if not message_type:
                            # Topic format: zone.message_type
                            message_type = msg.topic.split('.', 1)[1] if '.' in msg.topic else 'UNKNOWN'

                        batch_id = headers.get('batch_id', str(uuid.uuid4()))

                        # Build message dict
                        message = {
                            'content': msg.value,
                            'message_type': message_type,
                            'batch_id': batch_id,
                            'kafka_topic': msg.topic,
                            'kafka_partition': msg.partition,
                            'kafka_offset': msg.offset,
                            'kafka_timestamp': msg.timestamp,
                            'headers': headers,
                        }

                        # Add to batch
                        with self._batch_lock:
                            if not self._current_batch:
                                self._batch_start_time = time.time()
                            self._current_batch.append(message)

                # Check if batch should be flushed
                if self._should_flush_batch():
                    self._flush_batch()

                    # Commit offsets after successful batch processing
                    try:
                        consumer.commit()
                    except KafkaError as e:
                        logger.error(f"[{self.ZONE}] Offset commit failed: {e}")

        except Exception as e:
            logger.error(f"[{self.ZONE}] Consumer error: {e}")
            raise

        finally:
            # Flush any remaining messages
            self._flush_batch()

            # Cleanup
            if self._consumer:
                self._consumer.close()
            if self._producer:
                self._producer.close()
            if self._executor:
                self._executor.shutdown(wait=True)

            logger.info(
                f"[{self.ZONE}] Consumer stopped. "
                f"Consumed: {self._messages_consumed}, "
                f"Processed: {self._messages_processed}, "
                f"Failed: {self._messages_failed}"
            )

    def stop(self) -> None:
        """Signal consumer to stop."""
        self._running = False
        self._shutdown_event.set()


# =============================================================================
# BRONZE CONSUMER
# =============================================================================

class BronzeConsumer(ZoneConsumer):
    """
    Bronze zone consumer.

    Consumes raw messages from bronze.{msg_type} topics.
    Stores raw content AS-IS in bronze.raw_payment_messages.
    Publishes raw_ids to silver.{msg_type} topics.

    Multi-record files (e.g., pain.001 with multiple CdtTrfTxInf) are split
    into individual records, each becoming a separate Bronze record.
    """

    ZONE = 'bronze'
    CELERY_TASK = 'gps_cdm.zone_tasks.process_bronze_records'
    OUTPUT_ZONE = 'silver'

    def _build_task_kwargs(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build kwargs for Bronze Celery task.

        Multi-record messages are split into individual transactions using MessageSplitter.
        Each transaction becomes a separate Bronze record with parent context preserved.
        """
        from gps_cdm.orchestration.message_splitter import split_message

        # Get batch_id from first message
        batch_id = messages[0].get('batch_id', str(uuid.uuid4()))
        message_type = messages[0].get('message_type', 'UNKNOWN')

        # Build records list - split multi-record files into individual transactions
        records = []
        for msg in messages:
            content = msg['content']
            msg_type = msg.get('message_type', message_type)

            # Detect format from content
            message_format = MessageFormatDetector.detect(content)

            # Split multi-record messages (e.g., pain.001 with multiple CdtTrfTxInf)
            split_records = split_message(content, msg_type)

            logger.debug(
                f"[{self.ZONE}] Split {msg_type} message into {len(split_records)} records"
            )

            for split_rec in split_records:
                split_content = split_rec.get('content', content)
                parent_context = split_rec.get('parent_context', {})
                record_index = split_rec.get('index', 0)

                # Merge parent context into content if both are dicts
                if isinstance(split_content, dict) and parent_context:
                    for key, value in parent_context.items():
                        if key not in split_content or split_content[key] is None:
                            split_content[key] = value

                records.append({
                    'content': split_content,  # Individual transaction
                    'message_type': msg_type,
                    'message_format': message_format,
                    'record_index': record_index,
                    'parent_context': parent_context,
                    'metadata': {
                        'kafka_topic': msg.get('kafka_topic'),
                        'kafka_partition': msg.get('kafka_partition'),
                        'kafka_offset': msg.get('kafka_offset'),
                        'source_timestamp': msg.get('kafka_timestamp'),
                        'original_record_count': len(split_records),
                    }
                })

        logger.info(
            f"[{self.ZONE}] Expanded {len(messages)} Kafka messages "
            f"to {len(records)} individual records"
        )

        return {
            'batch_id': batch_id,
            'records': records,
        }


# =============================================================================
# SILVER CONSUMER
# =============================================================================

class SilverConsumer(ZoneConsumer):
    """
    Silver zone consumer.

    Consumes raw_ids from silver.{msg_type} topics.
    Retrieves raw content from Bronze, parses, extracts to Silver.
    Publishes stg_ids to gold.{msg_type} topics.
    """

    ZONE = 'silver'
    CELERY_TASK = 'gps_cdm.zone_tasks.process_silver_records'
    OUTPUT_ZONE = 'gold'

    def _build_task_kwargs(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build kwargs for Silver Celery task."""
        batch_id = messages[0].get('batch_id', str(uuid.uuid4()))
        message_type = messages[0].get('message_type', 'UNKNOWN')

        # Message content is the raw_id
        raw_ids = [msg['content'] for msg in messages]

        return {
            'batch_id': batch_id,
            'raw_ids': raw_ids,
            'message_type': message_type,
        }


# =============================================================================
# GOLD CONSUMER
# =============================================================================

class GoldConsumer(ZoneConsumer):
    """
    Gold zone consumer (terminal zone).

    Consumes stg_ids from gold.{msg_type} topics.
    Retrieves Silver data, transforms to CDM, stores in Gold tables.
    No output publishing (terminal zone).
    """

    ZONE = 'gold'
    CELERY_TASK = 'gps_cdm.zone_tasks.process_gold_records'
    OUTPUT_ZONE = None  # Terminal zone

    def _build_task_kwargs(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build kwargs for Gold Celery task."""
        batch_id = messages[0].get('batch_id', str(uuid.uuid4()))
        message_type = messages[0].get('message_type', 'UNKNOWN')

        # Message content is the stg_id
        stg_ids = [msg['content'] for msg in messages]

        return {
            'batch_id': batch_id,
            'stg_ids': stg_ids,
            'message_type': message_type,
        }


# =============================================================================
# CONSUMER LAUNCHER
# =============================================================================

class ZoneConsumerLauncher:
    """Launches and manages zone-specific consumers."""

    def __init__(
        self,
        zone: str,
        message_types: Optional[List[str]] = None,
        config: Optional[ZoneConsumerConfig] = None,
    ):
        self.zone = zone
        self.config = config or ZoneConsumerConfig()

        # Default to all message types if not specified
        if message_types is None:
            message_types = list(MessageTypeConfig().MESSAGE_TYPES.keys())
        self.message_types = message_types

        self._consumer: Optional[ZoneConsumer] = None
        self._running = False

    def _get_consumer_class(self) -> type:
        """Get consumer class for zone."""
        return {
            'bronze': BronzeConsumer,
            'silver': SilverConsumer,
            'gold': GoldConsumer,
        }[self.zone]

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.stop()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def start(self) -> None:
        """Start the consumer."""
        self._setup_signal_handlers()
        self._running = True

        consumer_class = self._get_consumer_class()
        self._consumer = consumer_class(
            message_types=self.message_types,
            config=self.config,
        )

        logger.info(f"Starting {self.zone} consumer for {len(self.message_types)} message types")
        self._consumer.run()

    def stop(self) -> None:
        """Stop the consumer."""
        self._running = False
        if self._consumer:
            self._consumer.stop()


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    """CLI entry point for zone consumers."""
    import argparse

    parser = argparse.ArgumentParser(description='GPS CDM Zone Consumer')
    parser.add_argument(
        '--zone',
        required=True,
        choices=['bronze', 'silver', 'gold'],
        help='Zone to consume from',
    )
    parser.add_argument(
        '--types',
        help='Comma-separated list of message types (default: all)',
    )
    parser.add_argument(
        '--bootstrap-servers',
        default='localhost:9092',
        help='Kafka bootstrap servers',
    )
    parser.add_argument(
        '--group-id-prefix',
        default='gps-cdm',
        help='Consumer group ID prefix',
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50,
        help='Batch size for processing',
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Number of worker threads',
    )

    args = parser.parse_args()

    # Parse message types
    message_types = None
    if args.types:
        message_types = [t.strip() for t in args.types.split(',')]

    # Build config
    config = ZoneConsumerConfig(
        bootstrap_servers=args.bootstrap_servers,
        group_id_prefix=args.group_id_prefix,
        batch_size=args.batch_size,
        num_workers=args.workers,
    )

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    # Start launcher
    launcher = ZoneConsumerLauncher(
        zone=args.zone,
        message_types=message_types,
        config=config,
    )
    launcher.start()


if __name__ == '__main__':
    main()
