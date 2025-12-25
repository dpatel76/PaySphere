"""
GPS CDM - Lineage Manager
=========================

Provides end-to-end data lineage tracking across the medallion architecture.
Persists lineage information to Delta Lake for audit, compliance, and debugging.

Features:
- Source-to-target field-level lineage
- Transformation lineage (what functions applied)
- Cross-layer lineage (Bronze → Silver → Gold)
- Regulatory reporting lineage (CDM → Report)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col, lit, current_timestamp, struct, to_json, from_json,
    explode, array, monotonically_increasing_id
)
from pyspark.sql.types import (
    StructType, StructField, StringType, TimestampType, ArrayType, MapType
)
import uuid


@dataclass
class LineageRecord:
    """A single lineage record capturing data flow."""
    lineage_id: str
    batch_id: str
    source_layer: str  # bronze, silver, gold
    target_layer: str  # silver, gold, report
    source_table: str
    target_table: str
    source_record_id: str
    target_record_id: str
    mapping_id: str
    transformation_type: str
    field_mappings: Dict[str, str]  # target_field -> source_field
    transforms_applied: List[str]
    created_at: datetime


class LineageManager:
    """
    Manages data lineage tracking across the GPS CDM pipeline.

    Captures:
    - Record-level lineage (which source record created which target record)
    - Field-level lineage (which source field mapped to which target field)
    - Transformation lineage (which transforms were applied)
    - Cross-layer lineage (Bronze → Silver → Gold → Report)

    Usage:
        lineage_mgr = LineageManager(spark, "cdm_bronze.observability")

        # Track batch lineage
        lineage_mgr.capture_batch_lineage(
            batch_id="abc-123",
            source_layer="bronze",
            target_layer="silver",
            source_table="raw_pain001",
            target_table="payment_instruction",
            mapping_id="PAIN_001_V09",
            source_df=bronze_df,
            target_df=silver_df
        )

        # Query lineage
        lineage = lineage_mgr.get_record_lineage(
            record_id="payment-uuid-456",
            layer="silver"
        )
    """

    # DDL for lineage tracking table
    LINEAGE_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS {catalog}.data_lineage (
        lineage_id STRING NOT NULL COMMENT 'Unique lineage record ID',
        batch_id STRING NOT NULL COMMENT 'Processing batch ID',
        source_layer STRING NOT NULL COMMENT 'Source layer (bronze/silver/gold)',
        target_layer STRING NOT NULL COMMENT 'Target layer (silver/gold/report)',
        source_table STRING NOT NULL COMMENT 'Source table name',
        target_table STRING NOT NULL COMMENT 'Target table name',
        source_record_id STRING COMMENT 'Source record primary key',
        target_record_id STRING COMMENT 'Target record primary key',
        mapping_id STRING COMMENT 'Mapping configuration used',
        transformation_type STRING COMMENT 'Type of transformation',
        field_mappings STRING COMMENT 'JSON: target_field -> source_field',
        transforms_applied ARRAY<STRING> COMMENT 'List of transform functions applied',
        record_count BIGINT COMMENT 'Number of records processed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
    )
    USING DELTA
    PARTITIONED BY (target_layer, date(created_at))
    TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
    COMMENT 'Data lineage tracking for audit and compliance'
    """

    # DDL for field-level lineage
    FIELD_LINEAGE_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS {catalog}.field_lineage (
        field_lineage_id STRING NOT NULL COMMENT 'Unique field lineage ID',
        mapping_id STRING NOT NULL COMMENT 'Mapping configuration ID',
        mapping_version STRING COMMENT 'Mapping version',
        source_format STRING COMMENT 'Source format (XML, MT, JSON)',
        source_field STRING NOT NULL COMMENT 'Source field/XPath',
        target_entity STRING NOT NULL COMMENT 'Target CDM entity',
        target_attribute STRING NOT NULL COMMENT 'Target CDM attribute',
        transform_type STRING COMMENT 'Transform type applied',
        transform_function STRING COMMENT 'Transform function name',
        transform_params STRING COMMENT 'Transform parameters as JSON',
        validation_rules ARRAY<STRING> COMMENT 'Validation rules applied',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
    )
    USING DELTA
    PARTITIONED BY (mapping_id)
    COMMENT 'Field-level lineage for regulatory traceability'
    """

    def __init__(
        self,
        spark: SparkSession,
        catalog: str = "cdm_bronze.observability",
        auto_create: bool = True
    ):
        """
        Initialize lineage manager.

        Args:
            spark: SparkSession
            catalog: Database/catalog path for lineage tables
            auto_create: Auto-create tables if not exists
        """
        self.spark = spark
        self.catalog = catalog
        self.lineage_table = f"{catalog}.data_lineage"
        self.field_lineage_table = f"{catalog}.field_lineage"

        if auto_create:
            self._ensure_tables_exist()

    def _ensure_tables_exist(self):
        """Create lineage tables if they don't exist."""
        try:
            self.spark.sql(self.LINEAGE_TABLE_DDL.format(catalog=self.catalog))
            self.spark.sql(self.FIELD_LINEAGE_TABLE_DDL.format(catalog=self.catalog))
        except Exception:
            pass

    def capture_batch_lineage(
        self,
        batch_id: str,
        source_layer: str,
        target_layer: str,
        source_table: str,
        target_table: str,
        mapping_id: str,
        record_count: int,
        field_mappings: Optional[Dict[str, str]] = None,
        transforms_applied: Optional[List[str]] = None,
        transformation_type: str = "ETL"
    ):
        """
        Capture batch-level lineage for a processing step.

        Args:
            batch_id: Processing batch ID
            source_layer: Source layer name
            target_layer: Target layer name
            source_table: Source table name
            target_table: Target table name
            mapping_id: Mapping configuration ID
            record_count: Number of records processed
            field_mappings: Map of target field to source field
            transforms_applied: List of transform functions used
            transformation_type: Type of transformation
        """
        lineage_id = str(uuid.uuid4())

        record = {
            "lineage_id": lineage_id,
            "batch_id": batch_id,
            "source_layer": source_layer,
            "target_layer": target_layer,
            "source_table": source_table,
            "target_table": target_table,
            "source_record_id": None,
            "target_record_id": None,
            "mapping_id": mapping_id,
            "transformation_type": transformation_type,
            "field_mappings": str(field_mappings or {}),
            "transforms_applied": transforms_applied or [],
            "record_count": record_count,
            "created_at": datetime.utcnow(),
        }

        try:
            df = self.spark.createDataFrame([record])
            df.write.format("delta").mode("append").saveAsTable(self.lineage_table)
        except Exception:
            pass

    def capture_field_lineage(
        self,
        mapping_id: str,
        mapping_version: str,
        source_format: str,
        field_mappings: List[Dict[str, Any]]
    ):
        """
        Capture field-level lineage from a mapping configuration.

        Args:
            mapping_id: Mapping configuration ID
            mapping_version: Mapping version
            source_format: Source format (XML, MT, JSON, etc.)
            field_mappings: List of field mapping definitions
        """
        records = []
        for mapping in field_mappings:
            records.append({
                "field_lineage_id": str(uuid.uuid4()),
                "mapping_id": mapping_id,
                "mapping_version": mapping_version,
                "source_format": source_format,
                "source_field": mapping.get("source", ""),
                "target_entity": mapping.get("target_entity", ""),
                "target_attribute": mapping.get("target_attribute", ""),
                "transform_type": mapping.get("transform_type", "DIRECT"),
                "transform_function": mapping.get("transform_function"),
                "transform_params": str(mapping.get("transform_params", {})),
                "validation_rules": mapping.get("validation_rules", []),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            })

        try:
            if records:
                df = self.spark.createDataFrame(records)
                df.write.format("delta").mode("append").saveAsTable(self.field_lineage_table)
        except Exception:
            pass

    def get_record_lineage(
        self,
        record_id: str,
        layer: str = "silver"
    ) -> List[Dict[str, Any]]:
        """
        Get complete lineage for a specific record.

        Args:
            record_id: Record primary key
            layer: Layer where record exists

        Returns:
            List of lineage records
        """
        try:
            df = self.spark.sql(f"""
                SELECT * FROM {self.lineage_table}
                WHERE target_record_id = '{record_id}'
                   OR source_record_id = '{record_id}'
                ORDER BY created_at
            """)
            return [row.asDict() for row in df.collect()]
        except Exception:
            return []

    def get_mapping_lineage(self, mapping_id: str) -> Dict[str, Any]:
        """
        Get complete field lineage for a mapping configuration.

        Args:
            mapping_id: Mapping configuration ID

        Returns:
            Dictionary with field lineage details
        """
        try:
            df = self.spark.sql(f"""
                SELECT * FROM {self.field_lineage_table}
                WHERE mapping_id = '{mapping_id}'
                ORDER BY target_entity, target_attribute
            """)

            fields = [row.asDict() for row in df.collect()]

            return {
                "mapping_id": mapping_id,
                "field_count": len(fields),
                "fields": fields,
                "entities": list(set(f["target_entity"] for f in fields)),
            }
        except Exception:
            return {"mapping_id": mapping_id, "field_count": 0, "fields": []}

    def get_regulatory_traceability(
        self,
        report_type: str,
        report_field: str
    ) -> List[Dict[str, Any]]:
        """
        Get end-to-end lineage from source to regulatory report field.

        Args:
            report_type: Regulatory report type (e.g., "FinCEN_CTR")
            report_field: Report field name

        Returns:
            Complete lineage chain from source to report
        """
        try:
            # Get field lineage for the report
            df = self.spark.sql(f"""
                SELECT fl.*
                FROM {self.field_lineage_table} fl
                WHERE fl.mapping_id LIKE '%{report_type}%'
                  AND fl.target_attribute = '{report_field}'
            """)

            return [row.asDict() for row in df.collect()]
        except Exception:
            return []

    def generate_lineage_report(self, batch_id: str) -> Dict[str, Any]:
        """
        Generate a complete lineage report for a batch.

        Args:
            batch_id: Processing batch ID

        Returns:
            Comprehensive lineage report
        """
        try:
            # Get batch lineage
            lineage_df = self.spark.sql(f"""
                SELECT * FROM {self.lineage_table}
                WHERE batch_id = '{batch_id}'
                ORDER BY created_at
            """)

            records = [row.asDict() for row in lineage_df.collect()]

            # Summarize by layer
            layers = {}
            for record in records:
                source = record["source_layer"]
                target = record["target_layer"]
                key = f"{source}_to_{target}"
                if key not in layers:
                    layers[key] = {
                        "source_layer": source,
                        "target_layer": target,
                        "tables": [],
                        "total_records": 0,
                    }
                layers[key]["tables"].append({
                    "source": record["source_table"],
                    "target": record["target_table"],
                    "records": record.get("record_count", 0),
                })
                layers[key]["total_records"] += record.get("record_count", 0)

            return {
                "batch_id": batch_id,
                "lineage_records": len(records),
                "layer_summary": layers,
                "details": records,
            }
        except Exception:
            return {"batch_id": batch_id, "lineage_records": 0, "layer_summary": {}}
