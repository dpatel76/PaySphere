"""
GPS CDM - Error Handler
=======================

Handles errors during pipeline processing with dead-letter routing.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ProcessingError:
    """A single processing error."""
    error_id: str
    batch_id: str
    layer: str
    table: str
    error_type: str
    error_message: str
    severity: ErrorSeverity = ErrorSeverity.ERROR
    record_id: Optional[str] = None
    record_data: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class ErrorHandler:
    """
    Handles error routing and dead-letter management.

    Features:
    - Classifies errors by type and severity
    - Routes failed records to dead-letter tables
    - Supports retry of failed records
    """

    def __init__(self, persistence=None):
        """
        Initialize error handler.

        Args:
            persistence: Optional persistence backend for error storage
        """
        self.persistence = persistence
        self.errors: List[ProcessingError] = []

    def record_error(
        self,
        batch_id: str,
        layer: str,
        table: str,
        error_type: str,
        error_message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        record_id: Optional[str] = None,
        record_data: Optional[str] = None,
    ) -> ProcessingError:
        """
        Record a processing error.

        Args:
            batch_id: Batch identifier
            layer: Layer where error occurred
            table: Table being processed
            error_type: Error classification
            error_message: Error details
            severity: Error severity level
            record_id: Optional record identifier
            record_data: Optional failed record data

        Returns:
            ProcessingError object
        """
        import uuid

        error = ProcessingError(
            error_id=str(uuid.uuid4()),
            batch_id=batch_id,
            layer=layer,
            table=table,
            error_type=error_type,
            error_message=error_message[:4000] if error_message else "",
            severity=severity,
            record_id=record_id,
            record_data=record_data,
        )

        self.errors.append(error)

        # Persist to dead-letter table if persistence available
        if self.persistence:
            from gps_cdm.ingestion.persistence.base import Layer
            layer_enum = Layer(layer) if layer in [l.value for l in Layer] else Layer.SILVER
            self.persistence.write_error(
                batch_id=batch_id,
                layer=layer_enum,
                table=table,
                error_type=error_type,
                error_message=error_message,
                record_data=record_data,
                record_id=record_id,
            )

        return error

    def get_errors(self, batch_id: Optional[str] = None) -> List[ProcessingError]:
        """Get recorded errors, optionally filtered by batch."""
        if batch_id:
            return [e for e in self.errors if e.batch_id == batch_id]
        return self.errors

    def get_error_summary(self, batch_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of errors."""
        errors = self.get_errors(batch_id)

        by_type = {}
        by_severity = {}

        for error in errors:
            by_type[error.error_type] = by_type.get(error.error_type, 0) + 1
            by_severity[error.severity.value] = by_severity.get(error.severity.value, 0) + 1

        return {
            "total_errors": len(errors),
            "by_type": by_type,
            "by_severity": by_severity,
        }

    def clear_errors(self, batch_id: Optional[str] = None):
        """Clear recorded errors."""
        if batch_id:
            self.errors = [e for e in self.errors if e.batch_id != batch_id]
        else:
            self.errors = []
