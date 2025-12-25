"""
GPS Payments CDM - Events Domain Entities
=========================================

Event entities including PaymentEvent and WorkflowEvent.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from gps_cdm.models.entities.base import PartitionMixin, generate_uuid
from gps_cdm.models.enums import ActorType, EventType


@dataclass
class PaymentEvent(PartitionMixin):
    """
    Payment lifecycle event record.

    Tracks all state changes and processing events for payments.
    """
    event_id: UUID = field(default_factory=generate_uuid)
    payment_id: UUID = field(default_factory=generate_uuid)

    # Event Details
    event_type: EventType = EventType.STATUS_CHANGE
    event_timestamp: datetime = field(default_factory=datetime.utcnow)
    previous_state: Optional[str] = None
    new_state: str = ""

    # Actor
    actor: Optional[str] = None
    actor_type: Optional[ActorType] = None
    actor_id: Optional[str] = None

    # Details
    details: Optional[Dict[str, Any]] = None
    correlation_id: Optional[UUID] = None
    parent_event_id: Optional[UUID] = None

    # Performance
    duration_ms: Optional[int] = None

    # Error
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    # Source
    source_system: Optional[str] = None
    external_reference: Optional[str] = None

    # Audit
    created_timestamp: datetime = field(default_factory=datetime.utcnow)

    def is_error_event(self) -> bool:
        """Check if this is an error event."""
        return self.error_code is not None or self.event_type == EventType.ERROR_OCCURRED


@dataclass
class WorkflowEvent:
    """
    Workflow/process event for any entity.

    Tracks workflow actions like approvals, reviews, and investigations.
    """
    workflow_event_id: UUID = field(default_factory=generate_uuid)

    # Entity Reference
    entity_type: str = ""  # Payment, Party, Account, ComplianceCase
    entity_id: UUID = field(default_factory=generate_uuid)

    # Workflow
    workflow_type: str = ""  # APPROVAL, REVIEW, INVESTIGATION
    workflow_instance_id: Optional[UUID] = None

    # Event
    event_type: str = ""  # WORKFLOW_STARTED, TASK_ASSIGNED, etc.
    event_timestamp: datetime = field(default_factory=datetime.utcnow)

    # Actor
    actor: str = ""
    actor_role: Optional[str] = None
    actor_department: Optional[str] = None

    # Assignment
    previous_assignee: Optional[str] = None
    current_assignee: Optional[str] = None

    # Task
    task_name: Optional[str] = None
    task_priority: Optional[str] = None  # LOW, MEDIUM, HIGH, CRITICAL
    due_date: Optional[datetime] = None
    sla_deadline: Optional[datetime] = None

    # Comments
    comments: Optional[str] = None
    attachments: Optional[List[UUID]] = None

    # Decision
    decision: Optional[str] = None
    decision_reason: Optional[str] = None

    # Metadata
    metadata: Optional[Dict[str, Any]] = None

    # Audit
    created_timestamp: datetime = field(default_factory=datetime.utcnow)

    def is_sla_breached(self) -> bool:
        """Check if SLA deadline has been breached."""
        if not self.sla_deadline:
            return False
        return datetime.utcnow() > self.sla_deadline
