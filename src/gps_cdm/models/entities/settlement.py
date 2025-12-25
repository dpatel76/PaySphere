"""
GPS Payments CDM - Settlement Domain Entities
=============================================

Settlement entities including Settlement, SettlementInstruction, and ClearingSystem.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from gps_cdm.models.entities.base import BiTemporalMixin, PartitionMixin, generate_uuid
from gps_cdm.models.enums import ClearingSystemType, SettlementMethod, SettlementStatus


@dataclass
class Settlement(PartitionMixin):
    """
    Settlement record for payment completion.

    Tracks the settlement lifecycle of a payment.
    """
    settlement_id: UUID = field(default_factory=generate_uuid)
    payment_id: UUID = field(default_factory=generate_uuid)

    # Settlement Details
    settlement_date: date = field(default_factory=date.today)
    settlement_amount: Decimal = Decimal("0")
    settlement_currency: str = "USD"
    settlement_method: SettlementMethod = SettlementMethod.CLRG
    settlement_status: SettlementStatus = SettlementStatus.PENDING

    # Clearing
    clearing_system_id: Optional[UUID] = None
    clearing_system_code: Optional[str] = None
    settlement_cycle: Optional[str] = None  # T+0, T+1, T+2

    # Interbank
    interbank_settlement_date: Optional[date] = None
    interbank_settlement_amount: Optional[Decimal] = None
    interbank_settlement_currency: Optional[str] = None

    # Account
    settlement_account_id: Optional[UUID] = None
    settlement_time: Optional[time] = None
    settlement_reference: Optional[str] = None

    # Batch
    batch_id: Optional[str] = None
    netting_indicator: bool = False

    # Instructions
    instructions: Optional[List["SettlementInstruction"]] = None

    # Timestamps
    created_timestamp: datetime = field(default_factory=datetime.utcnow)
    settled_timestamp: Optional[datetime] = None
    last_updated_timestamp: datetime = field(default_factory=datetime.utcnow)
    record_version: int = 1


@dataclass
class SettlementInstruction:
    """
    Settlement instruction details.

    Individual instructions within a settlement.
    """
    instruction_id: UUID = field(default_factory=generate_uuid)
    settlement_id: UUID = field(default_factory=generate_uuid)

    # Account
    account_id: UUID = field(default_factory=generate_uuid)

    # Type
    instruction_type: str = "CREDIT"  # CREDIT, DEBIT
    instruction_priority: str = "NORM"  # HIGH, NORM, URGP

    # Instructions
    instruction_for_creditor_agent: Optional[str] = None
    instruction_for_debtor_agent: Optional[str] = None
    instruction_for_next_agent: Optional[str] = None

    # Purpose
    purpose: Optional[str] = None

    # Execution
    execution_date: Optional[date] = None
    sequence_number: Optional[int] = None

    # Audit
    created_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ClearingSystem(BiTemporalMixin):
    """
    Clearing system reference data.

    Reference data for payment clearing systems.
    """
    clearing_system_id: UUID = field(default_factory=generate_uuid)

    # Identification
    system_code: str = ""  # ACH, FEDWIRE, TARGET2, etc.
    system_name: str = ""
    system_type: ClearingSystemType = ClearingSystemType.ACH

    # Location
    country: str = ""
    currency: str = "USD"

    # Operating Parameters
    operating_hours: Optional[str] = None  # e.g., "24x7", "06:00-18:00"
    cut_off_time: Optional[time] = None
    settlement_cycle: Optional[str] = None

    # Operator
    operator: Optional[str] = None  # Federal Reserve, ECB, etc.

    # Limits
    max_transaction_amount: Optional[Decimal] = None
    min_transaction_amount: Optional[Decimal] = None

    # Membership
    member_id: Optional[str] = None
    is_participant: bool = False

    def is_within_operating_hours(self, check_time: time) -> bool:
        """Check if current time is within operating hours."""
        if not self.operating_hours or self.operating_hours == "24x7":
            return True
        # Parse operating_hours and check (simplified)
        return True
