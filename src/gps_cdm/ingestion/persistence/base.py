"""
GPS CDM - Persistence Backend Interface
=======================================

Defines the abstract interface for all persistence backends.
Each backend (PostgreSQL, Delta Lake, Starburst) implements this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pyspark.sql import DataFrame, SparkSession


class Layer(str, Enum):
    """Data layer in 4-layer medallion architecture."""
    BRONZE = "bronze"          # Raw data as-is
    SILVER = "silver"          # Structured per message type (stg_*)
    GOLD = "gold"              # CDM normalized (cdm_*)
    ANALYTICAL = "analytical"  # Data products (anl_*)
    OBSERVABILITY = "observability"  # Operational metadata (obs_*)


class WriteMode(str, Enum):
    """Write mode for persistence operations."""
    APPEND = "append"
    OVERWRITE = "overwrite"
    MERGE = "merge"  # Upsert based on key
    ERROR_IF_EXISTS = "error"


@dataclass
class PersistenceConfig:
    """Configuration for a persistence backend."""
    backend: str  # postgresql, delta, starburst
    catalog: str = "gps_cdm"  # Database or catalog name
    bronze_schema: str = "bronze"
    silver_schema: str = "silver"
    gold_schema: str = "gold"
    analytical_schema: str = "analytical"
    observability_schema: str = "observability"

    # DDL directory for schema initialization
    ddl_directory: Optional[str] = None

    # Connection settings (vary by backend)
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None

    # Delta/Databricks specific
    storage_path: Optional[str] = None
    unity_catalog: bool = False

    # Starburst specific
    starburst_catalog: Optional[str] = None

    # Additional settings
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WriteResult:
    """Result of a write operation."""
    success: bool
    layer: Layer
    table: str
    records_written: int
    batch_id: str
    timestamp: datetime
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PersistenceBackend(ABC):
    """
    Abstract base class for persistence backends.

    All backends (PostgreSQL, Delta Lake, Starburst) implement this interface
    to provide consistent data persistence operations.
    """

    def __init__(self, spark: SparkSession, config: PersistenceConfig):
        """
        Initialize persistence backend.

        Args:
            spark: SparkSession for data operations
            config: Backend configuration
        """
        self.spark = spark
        self.config = config
        self._initialized = False

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the backend (create schemas, tables if needed).

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    def write(
        self,
        df: DataFrame,
        layer: Layer,
        table: str,
        batch_id: str,
        mode: WriteMode = WriteMode.APPEND,
        partition_cols: Optional[List[str]] = None,
        merge_keys: Optional[List[str]] = None,
    ) -> WriteResult:
        """
        Write DataFrame to storage.

        Args:
            df: DataFrame to write
            layer: Target layer (bronze/silver/gold)
            table: Table name
            batch_id: Batch identifier for tracking
            mode: Write mode (append/overwrite/merge)
            partition_cols: Columns to partition by
            merge_keys: Primary keys for merge/upsert

        Returns:
            WriteResult with operation details
        """
        pass

    @abstractmethod
    def read(
        self,
        layer: Layer,
        table: str,
        columns: Optional[List[str]] = None,
        filter_expr: Optional[str] = None,
    ) -> DataFrame:
        """
        Read data from storage.

        Args:
            layer: Source layer
            table: Table name
            columns: Columns to select (None = all)
            filter_expr: SQL filter expression

        Returns:
            DataFrame with requested data
        """
        pass

    @abstractmethod
    def table_exists(self, layer: Layer, table: str) -> bool:
        """Check if a table exists."""
        pass

    @abstractmethod
    def get_table_path(self, layer: Layer, table: str) -> str:
        """Get the full path/name for a table."""
        pass

    # Convenience methods for medallion layers
    def write_bronze(
        self,
        df: DataFrame,
        table: str,
        batch_id: str,
        mode: WriteMode = WriteMode.APPEND,
        partition_cols: Optional[List[str]] = None,
    ) -> WriteResult:
        """Write to bronze layer."""
        return self.write(df, Layer.BRONZE, table, batch_id, mode, partition_cols)

    def write_silver(
        self,
        df: DataFrame,
        table: str,
        batch_id: str,
        mode: WriteMode = WriteMode.APPEND,
        partition_cols: Optional[List[str]] = None,
        merge_keys: Optional[List[str]] = None,
    ) -> WriteResult:
        """Write to silver layer."""
        return self.write(df, Layer.SILVER, table, batch_id, mode, partition_cols, merge_keys)

    def write_gold(
        self,
        df: DataFrame,
        table: str,
        batch_id: str,
        mode: WriteMode = WriteMode.OVERWRITE,
        partition_cols: Optional[List[str]] = None,
    ) -> WriteResult:
        """Write to gold layer."""
        return self.write(df, Layer.GOLD, table, batch_id, mode, partition_cols)

    def read_bronze(self, table: str, **kwargs) -> DataFrame:
        """Read from bronze layer."""
        return self.read(Layer.BRONZE, table, **kwargs)

    def read_silver(self, table: str, **kwargs) -> DataFrame:
        """Read from silver layer."""
        return self.read(Layer.SILVER, table, **kwargs)

    def read_gold(self, table: str, **kwargs) -> DataFrame:
        """Read from gold layer."""
        return self.read(Layer.GOLD, table, **kwargs)

    def write_analytical(
        self,
        df: DataFrame,
        table: str,
        batch_id: str,
        mode: WriteMode = WriteMode.OVERWRITE,
        partition_cols: Optional[List[str]] = None,
    ) -> WriteResult:
        """Write to analytical layer (data products)."""
        return self.write(df, Layer.ANALYTICAL, table, batch_id, mode, partition_cols)

    def read_analytical(self, table: str, **kwargs) -> DataFrame:
        """Read from analytical layer."""
        return self.read(Layer.ANALYTICAL, table, **kwargs)

    # Lineage and observability methods
    @abstractmethod
    def write_lineage(
        self,
        batch_id: str,
        source_layer: Layer,
        target_layer: Layer,
        source_table: str,
        target_table: str,
        record_count: int,
        mapping_id: str,
        field_mappings: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Write lineage record for a transformation.

        Args:
            batch_id: Batch identifier
            source_layer: Source data layer
            target_layer: Target data layer
            source_table: Source table name
            target_table: Target table name
            record_count: Number of records transformed
            mapping_id: Mapping configuration ID
            field_mappings: Field-level mapping details

        Returns:
            True if lineage written successfully
        """
        pass

    @abstractmethod
    def write_error(
        self,
        batch_id: str,
        layer: Layer,
        table: str,
        error_type: str,
        error_message: str,
        record_data: Optional[str] = None,
        record_id: Optional[str] = None,
    ) -> bool:
        """
        Write error record for failed processing.

        Args:
            batch_id: Batch identifier
            layer: Layer where error occurred
            table: Table being processed
            error_type: Error classification
            error_message: Error details
            record_data: Failed record data (JSON)
            record_id: Record identifier if known

        Returns:
            True if error written successfully
        """
        pass

    @abstractmethod
    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """
        Get processing status for a batch.

        Args:
            batch_id: Batch identifier

        Returns:
            Dictionary with batch status details
        """
        pass

    # Field-level lineage (for complete traceability)
    @abstractmethod
    def write_field_lineage(
        self,
        batch_id: str,
        source_layer: Layer,
        source_table: str,
        source_field: str,
        target_layer: Layer,
        target_table: str,
        target_field: str,
        transformation_type: str,
        transformation_logic: Optional[str] = None,
        mapping_id: Optional[str] = None,
    ) -> bool:
        """
        Write field-level lineage record.

        Args:
            batch_id: Batch identifier
            source_layer: Source data layer
            source_table: Source table name
            source_field: Source field name
            target_layer: Target data layer
            target_table: Target table name
            target_field: Target field name
            transformation_type: Type of transformation (direct, lookup, expression, etc.)
            transformation_logic: Transformation expression or logic
            mapping_id: Mapping configuration ID

        Returns:
            True if lineage written successfully
        """
        pass

    # Data Quality metrics
    @abstractmethod
    def write_dq_result(
        self,
        batch_id: str,
        layer: Layer,
        entity_type: str,
        entity_id: str,
        overall_score: float,
        dimension_scores: Dict[str, float],
        rule_results: Dict[str, Any],
        issues: Optional[List[str]] = None,
    ) -> bool:
        """
        Write per-record data quality result.

        Args:
            batch_id: Batch identifier
            layer: Data layer
            entity_type: Entity type (e.g., payment_instruction, party)
            entity_id: Entity identifier
            overall_score: Overall DQ score (0-100)
            dimension_scores: Scores by dimension (completeness, accuracy, etc.)
            rule_results: Individual rule results
            issues: List of identified issues

        Returns:
            True if DQ result written successfully
        """
        pass

    @abstractmethod
    def write_dq_metrics(
        self,
        batch_id: str,
        layer: Layer,
        entity_type: str,
        total_records: int,
        avg_score: float,
        dimension_averages: Dict[str, float],
        records_above_threshold: int,
        records_below_threshold: int,
        top_failing_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Write aggregated data quality metrics.

        Args:
            batch_id: Batch identifier
            layer: Data layer
            entity_type: Entity type
            total_records: Total records evaluated
            avg_score: Average overall score
            dimension_averages: Average scores by dimension
            records_above_threshold: Records meeting quality threshold
            records_below_threshold: Records below quality threshold
            top_failing_rules: Most frequently failing rules

        Returns:
            True if metrics written successfully
        """
        pass

    # Change Data Capture
    @abstractmethod
    def write_cdc_event(
        self,
        layer: Layer,
        table: str,
        record_id: str,
        operation: str,  # INSERT, UPDATE, DELETE
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        changed_fields: Optional[List[str]] = None,
        batch_id: Optional[str] = None,
    ) -> bool:
        """
        Write CDC event for downstream sync.

        Args:
            layer: Data layer where change occurred
            table: Table name
            record_id: Record identifier
            operation: Type of operation (INSERT, UPDATE, DELETE)
            old_data: Previous record state (for UPDATE/DELETE)
            new_data: New record state (for INSERT/UPDATE)
            changed_fields: List of changed field names
            batch_id: Associated batch ID

        Returns:
            True if CDC event written successfully
        """
        pass

    @abstractmethod
    def get_pending_cdc_events(
        self,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Get pending CDC events for sync.

        Args:
            limit: Maximum events to retrieve

        Returns:
            List of pending CDC events
        """
        pass

    @abstractmethod
    def mark_cdc_synced(
        self,
        cdc_ids: List[str],
        target_system: str,
    ) -> bool:
        """
        Mark CDC events as synced to target system.

        Args:
            cdc_ids: List of CDC event IDs
            target_system: Target system name (e.g., 'neo4j')

        Returns:
            True if marked successfully
        """
        pass

    # Checkpoint management
    @abstractmethod
    def save_checkpoint(
        self,
        batch_id: str,
        layer: Layer,
        offset: int,
        partition: Optional[str] = None,
        key: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Save processing checkpoint for restartability.

        Args:
            batch_id: Batch identifier
            layer: Current processing layer
            offset: Record offset
            partition: Partition identifier
            key: Last processed record key
            data: Additional checkpoint data

        Returns:
            True if checkpoint saved
        """
        pass

    @abstractmethod
    def get_checkpoint(
        self,
        batch_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get latest checkpoint for a batch.

        Args:
            batch_id: Batch identifier

        Returns:
            Checkpoint data or None if not found
        """
        pass

    @abstractmethod
    def clear_checkpoint(
        self,
        batch_id: str,
    ) -> bool:
        """
        Clear checkpoint after successful completion.

        Args:
            batch_id: Batch identifier

        Returns:
            True if cleared successfully
        """
        pass
