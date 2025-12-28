"""
GPS CDM - Micro-Batch Accumulator with Restartability
======================================================

High-throughput message accumulator that batches Kafka messages for bulk database writes.
Provides exactly-once semantics and crash recovery through PostgreSQL checkpointing.

Key Features:
- Time-based and size-based batch flushing
- PostgreSQL checkpoint storage for crash recovery
- Exactly-once semantics via Kafka offset management
- Automatic recovery of in-flight batches on restart
- Dead letter queue for failed batches

Recovery Flow:
1. On startup, check for incomplete batches in micro_batch_tracking
2. Claim stale consumer checkpoints (from crashed consumers)
3. Resume processing from last committed offset
4. Retry or DLQ any failed batches

Usage:
    accumulator = MicroBatchAccumulator(
        consumer_group="gps-cdm-bronze",
        bulk_writer=bulk_writer,
        checkpoint_store=checkpoint_store,
        max_batch_size=10000,
        max_wait_seconds=10.0
    )

    # On each Kafka message
    result = await accumulator.accumulate(message)
    if result:
        # Batch was flushed
        print(f"Wrote {result.records_written} records")

    # On shutdown
    await accumulator.flush_all()
"""

import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class BatchState(Enum):
    """State of a micro-batch."""
    NONE = "NONE"
    ACCUMULATING = "ACCUMULATING"
    FLUSHING = "FLUSHING"
    COMMITTED = "COMMITTED"
    FAILED = "FAILED"


class MicroBatchState(Enum):
    """Processing state for micro-batch tracking."""
    PENDING = "PENDING"
    WRITING_BRONZE = "WRITING_BRONZE"
    BRONZE_COMPLETE = "BRONZE_COMPLETE"
    WRITING_SILVER = "WRITING_SILVER"
    SILVER_COMPLETE = "SILVER_COMPLETE"
    WRITING_GOLD = "WRITING_GOLD"
    GOLD_COMPLETE = "GOLD_COMPLETE"
    COMMITTING = "COMMITTING"
    COMMITTED = "COMMITTED"
    FAILED = "FAILED"


@dataclass
class KafkaOffset:
    """Represents a Kafka topic-partition-offset tuple."""
    topic: str
    partition: int
    offset: int


@dataclass
class KafkaMessage:
    """A Kafka message with metadata."""
    topic: str
    partition: int
    offset: int
    key: Optional[str]
    value: str
    headers: Dict[str, str]
    timestamp: int
    message_type: str
    message_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for checkpoint storage."""
        return {
            "topic": self.topic,
            "partition": self.partition,
            "offset": self.offset,
            "key": self.key,
            "value": self.value,
            "headers": self.headers,
            "timestamp": self.timestamp,
            "message_type": self.message_type,
            "message_id": self.message_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KafkaMessage":
        """Deserialize from checkpoint storage."""
        return cls(
            topic=data["topic"],
            partition=data["partition"],
            offset=data["offset"],
            key=data.get("key"),
            value=data["value"],
            headers=data.get("headers", {}),
            timestamp=data.get("timestamp", 0),
            message_type=data["message_type"],
            message_id=data.get("message_id"),
        )


@dataclass
class FlushResult:
    """Result of a batch flush operation."""
    batch_id: str
    table: str
    records_written: int
    duration_ms: float
    status: str
    error: Optional[str] = None
    offsets_committed: bool = False


@dataclass
class RecoveryInfo:
    """Information about recovered batches on startup."""
    stale_checkpoints_claimed: int
    incomplete_batches_found: int
    batches_recovered: List[str]
    batches_sent_to_dlq: List[str]


@dataclass
class BufferState:
    """State of a single message type buffer."""
    messages: List[KafkaMessage] = field(default_factory=list)
    first_message_time: Optional[float] = None
    partition_offsets: Dict[Tuple[str, int], int] = field(default_factory=dict)

    def add(self, message: KafkaMessage) -> None:
        """Add a message to the buffer."""
        if self.first_message_time is None:
            self.first_message_time = time.time()
        self.messages.append(message)
        # Track max offset per topic-partition
        key = (message.topic, message.partition)
        current_max = self.partition_offsets.get(key, -1)
        self.partition_offsets[key] = max(current_max, message.offset)

    def clear(self) -> None:
        """Clear the buffer."""
        self.messages = []
        self.first_message_time = None
        self.partition_offsets = {}

    @property
    def size(self) -> int:
        return len(self.messages)

    @property
    def age_seconds(self) -> float:
        if self.first_message_time is None:
            return 0.0
        return time.time() - self.first_message_time


class CheckpointStore:
    """
    PostgreSQL-backed checkpoint storage for consumer state.

    Provides durability for:
    - Kafka consumer offsets
    - In-flight batch records
    - Processing state
    """

    def __init__(self, connection_factory: Callable):
        """
        Initialize checkpoint store.

        Args:
            connection_factory: Callable that returns a database connection
        """
        self._get_connection = connection_factory

    async def save_checkpoint(
        self,
        consumer_group: str,
        consumer_id: str,
        topic: str,
        partition: int,
        committed_offset: int,
        pending_offset: Optional[int] = None,
        batch_id: Optional[str] = None,
        batch_state: BatchState = BatchState.NONE,
        pending_records: Optional[List[Dict]] = None
    ) -> bool:
        """
        Save consumer checkpoint to PostgreSQL.

        This is called:
        1. After successfully committing a batch (committed_offset updated)
        2. Periodically during accumulation (pending_records saved for recovery)
        """
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO observability.kafka_consumer_checkpoints (
                        checkpoint_id, consumer_group, consumer_id, topic, partition_id,
                        committed_offset, pending_offset, current_batch_id, batch_state,
                        pending_records, processing_status, last_heartbeat_at
                    ) VALUES (
                        uuid_generate_v4()::text, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, 'ACTIVE', CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (consumer_group, topic, partition_id)
                    DO UPDATE SET
                        consumer_id = EXCLUDED.consumer_id,
                        committed_offset = GREATEST(kafka_consumer_checkpoints.committed_offset, EXCLUDED.committed_offset),
                        pending_offset = EXCLUDED.pending_offset,
                        current_batch_id = EXCLUDED.current_batch_id,
                        batch_state = EXCLUDED.batch_state,
                        pending_records = EXCLUDED.pending_records,
                        processing_status = 'ACTIVE',
                        last_heartbeat_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    consumer_group, consumer_id, topic, partition,
                    committed_offset, pending_offset, batch_id, batch_state.value,
                    json.dumps(pending_records) if pending_records else None
                ))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            return False

    async def get_checkpoint(
        self,
        consumer_group: str,
        topic: str,
        partition: int
    ) -> Optional[Dict[str, Any]]:
        """Get checkpoint for a specific topic-partition."""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT committed_offset, pending_offset, current_batch_id,
                           batch_state, pending_records, consumer_id, processing_status
                    FROM observability.kafka_consumer_checkpoints
                    WHERE consumer_group = %s AND topic = %s AND partition_id = %s
                """, (consumer_group, topic, partition))
                row = cur.fetchone()
                if row:
                    return {
                        "committed_offset": row[0],
                        "pending_offset": row[1],
                        "batch_id": row[2],
                        "batch_state": row[3],
                        "pending_records": json.loads(row[4]) if row[4] else None,
                        "consumer_id": row[5],
                        "processing_status": row[6],
                    }
            return None
        except Exception as e:
            logger.error(f"Failed to get checkpoint: {e}")
            return None

    async def claim_stale_checkpoints(
        self,
        consumer_group: str,
        new_consumer_id: str,
        stale_threshold_seconds: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Claim checkpoints from crashed consumers.

        When a consumer crashes, its checkpoints become "stale" (no heartbeat).
        This allows another consumer to take over processing.
        """
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM observability.claim_stale_checkpoint(%s, %s, %s)
                """, (consumer_group, new_consumer_id, stale_threshold_seconds))
                rows = cur.fetchall()
            conn.commit()

            return [
                {
                    "topic": row[0],
                    "partition": row[1],
                    "committed_offset": row[2],
                    "pending_offset": row[3],
                    "batch_id": row[4],
                    "pending_records": row[5],
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Failed to claim stale checkpoints: {e}")
            return []

    async def update_heartbeat(
        self,
        consumer_group: str,
        consumer_id: str
    ) -> bool:
        """Update heartbeat timestamp for all partitions owned by this consumer."""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE observability.kafka_consumer_checkpoints
                    SET last_heartbeat_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE consumer_group = %s AND consumer_id = %s
                """, (consumer_group, consumer_id))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update heartbeat: {e}")
            return False


class MicroBatchTracker:
    """
    Tracks micro-batches through the processing pipeline.

    Provides visibility and recovery for batch processing state.
    """

    def __init__(self, connection_factory: Callable):
        self._get_connection = connection_factory

    async def create_batch(
        self,
        batch_id: str,
        consumer_group: str,
        topic: str,
        message_type: str,
        min_offset: int,
        max_offset: int,
        record_count: int,
        partitions: List[int]
    ) -> bool:
        """Create a new micro-batch tracking record."""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO observability.micro_batch_tracking (
                        batch_id, consumer_group, topic, partitions,
                        min_offset, max_offset, record_count, message_type,
                        state, started_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (
                    batch_id, consumer_group, topic, partitions,
                    min_offset, max_offset, record_count, message_type,
                    MicroBatchState.PENDING.value
                ))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to create batch tracking: {e}")
            return False

    async def update_state(
        self,
        batch_id: str,
        state: MicroBatchState,
        layer_record_count: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update batch processing state."""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                updates = ["state = %s"]
                params = [state.value]

                if state == MicroBatchState.BRONZE_COMPLETE and layer_record_count:
                    updates.append("bronze_written_at = CURRENT_TIMESTAMP")
                    updates.append("bronze_record_count = %s")
                    params.append(layer_record_count)
                elif state == MicroBatchState.SILVER_COMPLETE and layer_record_count:
                    updates.append("silver_written_at = CURRENT_TIMESTAMP")
                    updates.append("silver_record_count = %s")
                    params.append(layer_record_count)
                elif state == MicroBatchState.GOLD_COMPLETE and layer_record_count:
                    updates.append("gold_written_at = CURRENT_TIMESTAMP")
                    updates.append("gold_record_count = %s")
                    params.append(layer_record_count)
                elif state == MicroBatchState.COMMITTED:
                    updates.append("offsets_committed = TRUE")
                    updates.append("offsets_committed_at = CURRENT_TIMESTAMP")
                    updates.append("completed_at = CURRENT_TIMESTAMP")
                    updates.append("duration_ms = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - started_at)) * 1000")
                elif state == MicroBatchState.FAILED:
                    updates.append("error_message = %s")
                    params.append(error_message)
                    updates.append("retry_count = retry_count + 1")

                params.append(batch_id)

                cur.execute(f"""
                    UPDATE observability.micro_batch_tracking
                    SET {", ".join(updates)}
                    WHERE batch_id = %s
                """, params)
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update batch state: {e}")
            return False

    async def get_incomplete_batches(
        self,
        consumer_group: str,
        max_age_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """Get incomplete batches for recovery."""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM observability.get_incomplete_batches(%s, %s)
                """, (consumer_group, max_age_minutes))
                rows = cur.fetchall()

            return [
                {
                    "batch_id": row[0],
                    "topic": row[1],
                    "message_type": row[2],
                    "state": row[3],
                    "min_offset": row[4],
                    "max_offset": row[5],
                    "record_count": row[6],
                    "error_message": row[7],
                    "retry_count": row[8],
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Failed to get incomplete batches: {e}")
            return []

    async def send_to_dlq(
        self,
        batch_id: str,
        consumer_group: str,
        topic: str,
        message_type: str,
        records: List[Dict],
        min_offset: int,
        max_offset: int,
        partitions: List[int],
        error_type: str,
        error_message: str,
        failed_at_layer: Optional[str] = None
    ) -> bool:
        """Send a failed batch to dead letter queue."""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO observability.kafka_dead_letter_queue (
                        batch_id, consumer_group, topic, message_type,
                        partitions, min_offset, max_offset, record_count, records,
                        error_type, error_message, failed_at_layer
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    batch_id, consumer_group, topic, message_type,
                    partitions, min_offset, max_offset, len(records),
                    json.dumps(records), error_type, error_message, failed_at_layer
                ))
            conn.commit()
            logger.warning(f"Batch {batch_id} sent to DLQ: {error_message}")
            return True
        except Exception as e:
            logger.error(f"Failed to send to DLQ: {e}")
            return False


class MicroBatchAccumulator:
    """
    Accumulates Kafka messages into micro-batches for efficient bulk writes.

    Features:
    - Size-based flushing (e.g., every 10,000 records)
    - Time-based flushing (e.g., every 10 seconds)
    - PostgreSQL checkpointing for crash recovery
    - Exactly-once semantics via offset management
    - Automatic retry with dead letter queue

    Recovery Flow on Startup:
    1. Claim any stale checkpoints from crashed consumers
    2. Recover pending_records from checkpoints
    3. Resume processing from last committed offset
    """

    def __init__(
        self,
        consumer_group: str,
        consumer_id: str,
        bulk_writer: "BulkWriter",
        checkpoint_store: CheckpointStore,
        batch_tracker: MicroBatchTracker,
        kafka_commit_callback: Callable[[Dict[Tuple[str, int], int]], None],
        max_batch_size: int = 10_000,
        max_wait_seconds: float = 10.0,
        checkpoint_interval_seconds: float = 5.0,
        max_retries: int = 3,
    ):
        """
        Initialize the accumulator.

        Args:
            consumer_group: Kafka consumer group ID
            consumer_id: Unique ID for this consumer instance
            bulk_writer: BulkWriter instance for database operations
            checkpoint_store: CheckpointStore for persistence
            batch_tracker: MicroBatchTracker for batch state
            kafka_commit_callback: Function to commit Kafka offsets
            max_batch_size: Maximum records before auto-flush
            max_wait_seconds: Maximum time before auto-flush
            checkpoint_interval_seconds: How often to save pending records
            max_retries: Maximum retry attempts before DLQ
        """
        self.consumer_group = consumer_group
        self.consumer_id = consumer_id
        self.bulk_writer = bulk_writer
        self.checkpoint_store = checkpoint_store
        self.batch_tracker = batch_tracker
        self.kafka_commit_callback = kafka_commit_callback

        self.max_batch_size = max_batch_size
        self.max_wait_seconds = max_wait_seconds
        self.checkpoint_interval_seconds = checkpoint_interval_seconds
        self.max_retries = max_retries

        # Per-table buffers (message_type -> BufferState)
        self.buffers: Dict[str, BufferState] = defaultdict(BufferState)

        # Lock for thread-safe buffer access
        self._lock = asyncio.Lock()

        # Background tasks
        self._flush_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._checkpoint_task: Optional[asyncio.Task] = None

        # Metrics
        self.messages_accumulated = 0
        self.batches_flushed = 0
        self.bytes_written = 0
        self.errors = 0

        # Running state
        self._running = False

    async def start(self) -> RecoveryInfo:
        """
        Start the accumulator and perform recovery if needed.

        Returns:
            RecoveryInfo with details about recovered batches
        """
        logger.info(f"Starting MicroBatchAccumulator for {self.consumer_group}/{self.consumer_id}")

        # Perform recovery
        recovery_info = await self._perform_recovery()

        # Start background tasks
        self._running = True
        self._flush_task = asyncio.create_task(self._flush_loop())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._checkpoint_task = asyncio.create_task(self._checkpoint_loop())

        logger.info(f"MicroBatchAccumulator started. Recovery: {recovery_info}")
        return recovery_info

    async def stop(self) -> None:
        """Stop the accumulator gracefully."""
        logger.info("Stopping MicroBatchAccumulator...")
        self._running = False

        # Cancel background tasks
        for task in [self._flush_task, self._heartbeat_task, self._checkpoint_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Flush remaining buffers
        await self.flush_all()

        logger.info("MicroBatchAccumulator stopped")

    async def _perform_recovery(self) -> RecoveryInfo:
        """
        Perform recovery on startup.

        1. Claim stale checkpoints from crashed consumers
        2. Recover pending records from checkpoints
        3. Resume incomplete batches
        """
        recovery_info = RecoveryInfo(
            stale_checkpoints_claimed=0,
            incomplete_batches_found=0,
            batches_recovered=[],
            batches_sent_to_dlq=[],
        )

        # 1. Claim stale checkpoints
        stale = await self.checkpoint_store.claim_stale_checkpoints(
            self.consumer_group,
            self.consumer_id,
            stale_threshold_seconds=60
        )
        recovery_info.stale_checkpoints_claimed = len(stale)

        # 2. Recover pending records from stale checkpoints
        for checkpoint in stale:
            if checkpoint.get("pending_records"):
                pending = checkpoint["pending_records"]
                message_type = pending[0].get("message_type") if pending else "unknown"

                # Re-add to buffer
                for record_dict in pending:
                    message = KafkaMessage.from_dict(record_dict)
                    self.buffers[message_type].add(message)

                logger.info(
                    f"Recovered {len(pending)} pending records for "
                    f"{checkpoint['topic']}:{checkpoint['partition']}"
                )

        # 3. Check for incomplete batches
        incomplete = await self.batch_tracker.get_incomplete_batches(
            self.consumer_group,
            max_age_minutes=60
        )
        recovery_info.incomplete_batches_found = len(incomplete)

        for batch in incomplete:
            if batch["retry_count"] >= self.max_retries:
                # Too many retries, send to DLQ
                recovery_info.batches_sent_to_dlq.append(batch["batch_id"])
                logger.warning(f"Batch {batch['batch_id']} exceeded max retries, sent to DLQ")
            else:
                # Will be retried automatically
                recovery_info.batches_recovered.append(batch["batch_id"])
                logger.info(f"Batch {batch['batch_id']} will be retried (attempt {batch['retry_count'] + 1})")

        return recovery_info

    async def accumulate(self, message: KafkaMessage) -> Optional[FlushResult]:
        """
        Add a message to the buffer.

        Returns FlushResult if the batch was flushed, None otherwise.
        """
        async with self._lock:
            buffer = self.buffers[message.message_type]
            buffer.add(message)
            self.messages_accumulated += 1

            # Check if flush is needed
            if buffer.size >= self.max_batch_size:
                return await self._flush_buffer(message.message_type)

        return None

    async def flush_all(self) -> List[FlushResult]:
        """Flush all buffers."""
        results = []
        async with self._lock:
            for message_type in list(self.buffers.keys()):
                if self.buffers[message_type].size > 0:
                    result = await self._flush_buffer(message_type)
                    if result:
                        results.append(result)
        return results

    async def _flush_buffer(self, message_type: str) -> Optional[FlushResult]:
        """
        Flush a specific buffer to the database.

        This is the core operation that:
        1. Creates batch tracking record
        2. Performs bulk write to Bronze
        3. Updates batch state
        4. Commits Kafka offsets
        5. Updates checkpoint
        """
        buffer = self.buffers[message_type]
        if buffer.size == 0:
            return None

        batch_id = str(uuid.uuid4())
        messages = buffer.messages.copy()
        partition_offsets = buffer.partition_offsets.copy()

        # Get offset range
        all_offsets = [m.offset for m in messages]
        min_offset = min(all_offsets)
        max_offset = max(all_offsets)
        partitions = list(set(m.partition for m in messages))
        topic = messages[0].topic

        # Clear buffer before processing (in case of crash, we have checkpoint)
        buffer.clear()

        start_time = time.time()

        try:
            # 1. Create batch tracking record
            await self.batch_tracker.create_batch(
                batch_id=batch_id,
                consumer_group=self.consumer_group,
                topic=topic,
                message_type=message_type,
                min_offset=min_offset,
                max_offset=max_offset,
                record_count=len(messages),
                partitions=partitions,
            )

            # 2. Update state to WRITING_BRONZE
            await self.batch_tracker.update_state(
                batch_id, MicroBatchState.WRITING_BRONZE
            )

            # 3. Perform bulk write to Bronze
            records = [
                {
                    "raw_id": m.message_id or str(uuid.uuid4()),
                    "message_type": m.message_type,
                    "message_format": self._detect_format(m.value),
                    "raw_content": m.value,
                    "source_system": "KAFKA",
                    "source_channel": "STREAMING",
                    "_batch_id": batch_id,
                    "processing_status": "PENDING",
                    "partition_date": datetime.utcnow().date().isoformat(),
                }
                for m in messages
            ]

            write_result = await self.bulk_writer.bulk_insert_bronze(
                batch_id=batch_id,
                message_type=message_type,
                records=records,
            )

            if not write_result.success:
                raise Exception(f"Bronze write failed: {write_result.error}")

            # 4. Update state to BRONZE_COMPLETE
            await self.batch_tracker.update_state(
                batch_id,
                MicroBatchState.BRONZE_COMPLETE,
                layer_record_count=len(records)
            )

            # 5. Commit Kafka offsets
            self.kafka_commit_callback(partition_offsets)

            # 6. Update state to COMMITTED
            await self.batch_tracker.update_state(batch_id, MicroBatchState.COMMITTED)

            # 7. Update checkpoint with new committed offsets
            for (t, p), offset in partition_offsets.items():
                await self.checkpoint_store.save_checkpoint(
                    consumer_group=self.consumer_group,
                    consumer_id=self.consumer_id,
                    topic=t,
                    partition=p,
                    committed_offset=offset + 1,  # Next offset to read
                    batch_state=BatchState.NONE,
                )

            duration_ms = (time.time() - start_time) * 1000
            self.batches_flushed += 1

            logger.info(
                f"Flushed batch {batch_id}: {len(records)} records "
                f"in {duration_ms:.1f}ms ({len(records) / (duration_ms / 1000):.0f} records/sec)"
            )

            return FlushResult(
                batch_id=batch_id,
                table=f"bronze.raw_payment_messages",
                records_written=len(records),
                duration_ms=duration_ms,
                status="SUCCESS",
                offsets_committed=True,
            )

        except Exception as e:
            self.errors += 1
            logger.exception(f"Failed to flush batch {batch_id}: {e}")

            # Update batch state to FAILED
            await self.batch_tracker.update_state(
                batch_id,
                MicroBatchState.FAILED,
                error_message=str(e)
            )

            # Check retry count and potentially send to DLQ
            # (This would need to fetch the batch record first)

            return FlushResult(
                batch_id=batch_id,
                table=f"bronze.raw_payment_messages",
                records_written=0,
                duration_ms=(time.time() - start_time) * 1000,
                status="FAILED",
                error=str(e),
                offsets_committed=False,
            )

    def _detect_format(self, content: str) -> str:
        """Detect message format from content."""
        content = content.strip()
        if content.startswith("<?xml") or content.startswith("<"):
            return "XML"
        if content.startswith("{"):
            return "JSON"
        if content.startswith("{1:"):
            return "SWIFT_MT"
        return "FIXED"

    async def _flush_loop(self) -> None:
        """Background task to flush buffers based on time."""
        while self._running:
            try:
                await asyncio.sleep(1.0)  # Check every second

                async with self._lock:
                    for message_type, buffer in list(self.buffers.items()):
                        if buffer.size > 0 and buffer.age_seconds >= self.max_wait_seconds:
                            logger.debug(f"Time-based flush for {message_type}")
                            await self._flush_buffer(message_type)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in flush loop: {e}")

    async def _heartbeat_loop(self) -> None:
        """Background task to update heartbeat."""
        while self._running:
            try:
                await asyncio.sleep(10.0)  # Every 10 seconds
                await self.checkpoint_store.update_heartbeat(
                    self.consumer_group,
                    self.consumer_id
                )
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in heartbeat loop: {e}")

    async def _checkpoint_loop(self) -> None:
        """Background task to save pending records for recovery."""
        while self._running:
            try:
                await asyncio.sleep(self.checkpoint_interval_seconds)

                async with self._lock:
                    for message_type, buffer in self.buffers.items():
                        if buffer.size > 0:
                            # Save pending records to checkpoint
                            pending_records = [m.to_dict() for m in buffer.messages]

                            for (topic, partition), offset in buffer.partition_offsets.items():
                                await self.checkpoint_store.save_checkpoint(
                                    consumer_group=self.consumer_group,
                                    consumer_id=self.consumer_id,
                                    topic=topic,
                                    partition=partition,
                                    committed_offset=offset,  # Will be updated on commit
                                    pending_offset=offset,
                                    batch_state=BatchState.ACCUMULATING,
                                    pending_records=pending_records,
                                )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in checkpoint loop: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get accumulator metrics."""
        buffer_stats = {}
        for message_type, buffer in self.buffers.items():
            buffer_stats[message_type] = {
                "size": buffer.size,
                "age_seconds": buffer.age_seconds,
            }

        return {
            "consumer_group": self.consumer_group,
            "consumer_id": self.consumer_id,
            "messages_accumulated": self.messages_accumulated,
            "batches_flushed": self.batches_flushed,
            "bytes_written": self.bytes_written,
            "errors": self.errors,
            "buffers": buffer_stats,
        }
