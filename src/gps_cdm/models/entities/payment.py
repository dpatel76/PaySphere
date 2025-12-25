"""
GPS Payments CDM - Payment Core Domain Entities
===============================================

Core payment entities including Payment, PaymentInstruction,
CreditTransfer, DirectDebit, PaymentReturn, PaymentReversal.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from gps_cdm.models.entities.base import (
    BiTemporalMixin,
    DataQualityMixin,
    LineageMixin,
    PartitionMixin,
    RegulatoryReportingInfo,
    SourceTrackingMixin,
    generate_uuid,
)
from gps_cdm.models.enums import (
    ChargeBearer,
    PaymentDirection,
    PaymentStatus,
    PaymentType,
    Priority,
    SchemeCode,
)


@dataclass
class Payment(BiTemporalMixin, SourceTrackingMixin, DataQualityMixin, LineageMixin, PartitionMixin):
    """
    Root entity representing a payment transaction.

    This is the central entity in the payment domain, linking to
    PaymentInstruction, Settlement, and PaymentEvents.
    """
    # Primary Key
    payment_id: UUID = field(default_factory=generate_uuid)

    # Core Attributes
    payment_type: PaymentType = PaymentType.CREDIT_TRANSFER
    scheme_code: SchemeCode = SchemeCode.SWIFT
    status: PaymentStatus = PaymentStatus.INITIATED
    direction: PaymentDirection = PaymentDirection.OUTBOUND
    cross_border_flag: bool = False
    priority: Priority = Priority.NORM

    # Foreign Keys
    instruction_id: Optional[UUID] = None
    settlement_id: Optional[UUID] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "payment_id": str(self.payment_id),
            "payment_type": self.payment_type.value,
            "scheme_code": self.scheme_code.value,
            "status": self.status.value,
            "direction": self.direction.value,
            "cross_border_flag": self.cross_border_flag,
            "priority": self.priority.value,
            "instruction_id": str(self.instruction_id) if self.instruction_id else None,
            "settlement_id": str(self.settlement_id) if self.settlement_id else None,
            "created_at": self.created_at.isoformat(),
            "valid_from": self.valid_from.isoformat(),
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
            "is_current": self.is_current,
            "source_system": self.source_system,
            "partition_year": self.partition_year,
            "partition_month": self.partition_month,
            "region": self.region,
        }


@dataclass
class PaymentInstruction(BiTemporalMixin, SourceTrackingMixin, DataQualityMixin, PartitionMixin):
    """
    Detailed instruction for payment execution.

    Contains the full details of a payment including parties,
    amounts, dates, and compliance information.
    """
    # Primary Key
    instruction_id: UUID = field(default_factory=generate_uuid)

    # Foreign Key to Payment
    payment_id: UUID = field(default_factory=generate_uuid)

    # Identifiers
    end_to_end_id: Optional[str] = None  # ISO 20022 E2E ID (max 35)
    uetr: Optional[UUID] = None  # SWIFT UETR
    transaction_id: Optional[str] = None
    instruction_id_ext: Optional[str] = None

    # Parties (FKs to Party)
    debtor_id: UUID = field(default_factory=generate_uuid)
    debtor_account_id: Optional[UUID] = None
    debtor_agent_id: Optional[UUID] = None
    creditor_id: UUID = field(default_factory=generate_uuid)
    creditor_account_id: Optional[UUID] = None
    creditor_agent_id: Optional[UUID] = None

    # Amount
    instructed_amount: Decimal = Decimal("0")
    instructed_currency: str = "USD"
    interbank_settlement_amount: Optional[Decimal] = None
    interbank_settlement_currency: Optional[str] = None
    exchange_rate: Optional[Decimal] = None

    # Dates
    requested_execution_date: date = field(default_factory=date.today)
    requested_execution_time: Optional[time] = None
    value_date: Optional[date] = None
    settlement_date: Optional[date] = None

    # Purpose
    purpose: Optional[str] = None  # ISO 20022 purpose code (max 4)
    purpose_description: Optional[str] = None
    charge_bearer: ChargeBearer = ChargeBearer.SHAR

    # Compliance
    sanctions_screening_status: str = "not_screened"
    sanctions_screening_timestamp: Optional[datetime] = None
    fraud_score: Optional[Decimal] = None
    fraud_flags: Optional[List[str]] = None
    aml_risk_rating: Optional[str] = None
    pep_flag: bool = False
    structuring_indicator: bool = False

    # Regulatory Reporting
    regulatory_reporting: Optional[List[RegulatoryReportingInfo]] = None

    # Remittance
    remittance_unstructured: Optional[List[str]] = None
    remittance_reference: Optional[str] = None

    # Original message for audit
    source_message_content: Optional[str] = None


@dataclass
class CreditTransfer:
    """
    Credit transfer specific details.

    Contains intermediary agent information and routing instructions.
    """
    credit_transfer_id: UUID = field(default_factory=generate_uuid)
    payment_id: UUID = field(default_factory=generate_uuid)

    # Intermediary Agents
    intermediary_agent_1_id: Optional[UUID] = None
    intermediary_agent_2_id: Optional[UUID] = None
    intermediary_agent_3_id: Optional[UUID] = None

    # Instructions
    instruction_for_creditor_agent: Optional[str] = None
    instruction_for_next_agent: Optional[str] = None
    previous_instructing_agent_id: Optional[UUID] = None

    # Audit
    created_timestamp: datetime = field(default_factory=datetime.utcnow)
    last_updated_timestamp: datetime = field(default_factory=datetime.utcnow)
    record_version: int = 1


@dataclass
class DirectDebit:
    """
    Direct debit specific details.

    Contains mandate information and sequence type.
    """
    direct_debit_id: UUID = field(default_factory=generate_uuid)
    payment_id: UUID = field(default_factory=generate_uuid)

    # Mandate
    mandate_id: str = ""
    mandate_date: date = field(default_factory=date.today)
    sequence_type: str = "FRST"  # FRST, RCUR, FNAL, OOFF
    creditor_scheme_id: Optional[str] = None
    direct_debit_type: Optional[str] = None  # B2B, CORE
    amendment_indicator: bool = False

    # Audit
    created_timestamp: datetime = field(default_factory=datetime.utcnow)
    last_updated_timestamp: datetime = field(default_factory=datetime.utcnow)
    record_version: int = 1


@dataclass
class PaymentReturn:
    """
    Payment return details.

    Records information about returned payments.
    """
    return_id: UUID = field(default_factory=generate_uuid)
    original_payment_id: UUID = field(default_factory=generate_uuid)
    return_payment_id: UUID = field(default_factory=generate_uuid)

    # Return Details
    return_reason_code: str = ""  # ISO 20022 return reason
    return_reason_description: Optional[str] = None
    original_end_to_end_id: Optional[str] = None
    original_transaction_id: Optional[str] = None
    return_amount: Decimal = Decimal("0")
    return_currency: str = "USD"
    return_date: date = field(default_factory=date.today)
    charges_information: Optional[str] = None

    # Audit
    created_timestamp: datetime = field(default_factory=datetime.utcnow)
    record_version: int = 1


@dataclass
class PaymentReversal:
    """
    Payment reversal details.

    Records information about reversed payments.
    """
    reversal_id: UUID = field(default_factory=generate_uuid)
    original_payment_id: UUID = field(default_factory=generate_uuid)
    reversal_payment_id: UUID = field(default_factory=generate_uuid)

    # Reversal Details
    reversal_reason_code: str = ""
    reversal_reason_description: Optional[str] = None
    original_interbank_settlement_amount: Optional[Decimal] = None
    original_interbank_settlement_currency: Optional[str] = None
    reversal_date: date = field(default_factory=date.today)

    # Audit
    created_timestamp: datetime = field(default_factory=datetime.utcnow)
    record_version: int = 1


@dataclass
class PaymentStatusReport(PartitionMixin):
    """
    Payment status report for tracking.

    ISO 20022 pacs.002 style status reporting.
    """
    status_report_id: UUID = field(default_factory=generate_uuid)
    payment_id: UUID = field(default_factory=generate_uuid)

    # Status Details
    message_id: str = ""
    creation_date_time: datetime = field(default_factory=datetime.utcnow)
    status_code: str = ""  # ISO 20022 status code
    status_reason_code: Optional[str] = None
    status_reason_description: Optional[str] = None
    acceptance_date_time: Optional[datetime] = None
    effective_interbank_settlement_date: Optional[date] = None
    original_message_id: Optional[str] = None

    # Audit
    created_timestamp: datetime = field(default_factory=datetime.utcnow)
    record_version: int = 1
