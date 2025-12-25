"""
GPS Payments CDM - Lineage Domain Entities
==========================================

Lineage entities including LineageMetadata and AuditTrail.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from gps_cdm.models.entities.base import PartitionMixin, generate_uuid
from gps_cdm.models.enums import ActorType, AuditAction, TransformationType


@dataclass
class LineageMetadata:
    """
    Field-level lineage metadata.

    Tracks transformations from source to target fields.
    """
    lineage_id: UUID = field(default_factory=generate_uuid)

    # Target Entity
    entity_type: str = ""  # Payment, Party, Account, etc.
    entity_id: UUID = field(default_factory=generate_uuid)
    field_name: str = ""
    field_path: Optional[str] = None

    # Source
    source_system: str = ""
    source_database: Optional[str] = None
    source_schema: Optional[str] = None
    source_table: Optional[str] = None
    source_field: str = ""
    source_field_path: Optional[str] = None

    # Transformation
    transformation_type: TransformationType = TransformationType.DIRECT
    transformation_logic: Optional[str] = None
    transformation_version: Optional[str] = None

    # Lookup (for LOOKUP type)
    lookup_table: Optional[str] = None
    lookup_key: Optional[str] = None

    # Quality
    confidence_score: Optional[Decimal] = None  # 0-1
    data_quality_impact: Optional[str] = None  # NONE, LOW, MEDIUM, HIGH

    # Validity
    effective_from: datetime = field(default_factory=datetime.utcnow)
    effective_to: Optional[datetime] = None

    # Pipeline
    created_by: Optional[str] = None
    created_timestamp: datetime = field(default_factory=datetime.utcnow)
    batch_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    pipeline_run_id: Optional[str] = None

    def is_active(self) -> bool:
        """Check if this lineage mapping is currently active."""
        return self.effective_to is None or self.effective_to > datetime.utcnow()


@dataclass
class AuditTrail(PartitionMixin):
    """
    Audit trail for all entity changes.

    Records all CRUD operations on CDM entities.
    """
    audit_id: UUID = field(default_factory=generate_uuid)

    # Entity
    entity_type: str = ""
    entity_id: UUID = field(default_factory=generate_uuid)

    # Action
    action: AuditAction = AuditAction.CREATE
    action_timestamp: datetime = field(default_factory=datetime.utcnow)

    # Actor
    actor: str = ""
    actor_type: ActorType = ActorType.SYSTEM
    actor_ip: Optional[str] = None
    actor_location: Optional[str] = None

    # Session
    session_id: Optional[str] = None
    request_id: Optional[UUID] = None
    correlation_id: Optional[UUID] = None

    # Changes
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changed_fields: Optional[List[str]] = None

    # Reason
    change_reason: Optional[str] = None
    change_ticket: Optional[str] = None

    # Approval
    approval_id: Optional[UUID] = None
    approved_by: Optional[str] = None
    approval_timestamp: Optional[datetime] = None

    # Classification
    data_classification: Optional[str] = None  # PUBLIC, INTERNAL, CONFIDENTIAL, etc.
    retention_period_days: Optional[int] = None
    is_sensitive: bool = False

    # Metadata
    metadata: Optional[Dict[str, Any]] = None

    def get_changed_field_count(self) -> int:
        """Get the number of changed fields."""
        return len(self.changed_fields) if self.changed_fields else 0

    def contains_sensitive_data(self) -> bool:
        """Check if this audit record contains sensitive data changes."""
        if self.is_sensitive:
            return True
        sensitive_fields = ["tax_id", "date_of_birth", "identification_number", "aadhar"]
        if self.changed_fields:
            return any(f.lower() in sensitive_fields for f in self.changed_fields)
        return False
