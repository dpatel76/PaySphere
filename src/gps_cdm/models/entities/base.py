"""
GPS Payments CDM - Base Entity Models and Mixins
================================================

Common patterns and base classes for CDM entities.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


@dataclass
class BiTemporalMixin:
    """
    Mixin for bi-temporal data management.
    Tracks both business validity (valid_from/valid_to) and
    system time (created_timestamp/last_updated_timestamp).
    """
    valid_from: date = field(default_factory=date.today)
    valid_to: Optional[date] = None
    is_current: bool = True
    created_timestamp: datetime = field(default_factory=datetime.utcnow)
    last_updated_timestamp: datetime = field(default_factory=datetime.utcnow)
    last_updated_by: str = "SYSTEM"
    record_version: int = 1
    is_deleted: bool = False
    deleted_timestamp: Optional[datetime] = None


@dataclass
class SourceTrackingMixin:
    """
    Mixin for tracking source system information.
    """
    source_system: str = ""
    source_system_record_id: Optional[str] = None
    source_message_type: Optional[str] = None
    ingestion_timestamp: Optional[datetime] = None
    bronze_to_silver_timestamp: Optional[datetime] = None


@dataclass
class DataQualityMixin:
    """
    Mixin for data quality metrics.
    """
    data_quality_score: Optional[Decimal] = None
    data_quality_dimensions: Optional[Dict[str, Decimal]] = None
    data_quality_issues: Optional[List[str]] = None


@dataclass
class LineageMixin:
    """
    Mixin for embedded lineage tracking.
    """
    lineage_source_table: Optional[str] = None
    lineage_source_columns: Optional[List[str]] = None
    lineage_batch_id: Optional[str] = None
    lineage_pipeline_run_id: Optional[str] = None


@dataclass
class PartitionMixin:
    """
    Mixin for partitioning columns.
    """
    partition_year: int = field(default_factory=lambda: datetime.utcnow().year)
    partition_month: int = field(default_factory=lambda: datetime.utcnow().month)
    region: str = "US"
    product_type: Optional[str] = None


@dataclass
class Address:
    """Structured address."""
    street_name: Optional[str] = None
    building_number: Optional[str] = None
    building_name: Optional[str] = None
    floor: Optional[str] = None
    room: Optional[str] = None
    post_box: Optional[str] = None
    post_code: Optional[str] = None
    town_name: Optional[str] = None
    district_name: Optional[str] = None
    country_sub_division: Optional[str] = None
    country: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None


@dataclass
class ContactDetails:
    """Contact information."""
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    mobile_number: Optional[str] = None


@dataclass
class TaxResidency:
    """Tax residency information for CRS/FATCA."""
    country: str
    tin_type: str
    tin: str
    tax_residency_basis: str  # CITIZENSHIP, RESIDENCE, DOMICILE, INCORPORATION
    effective_from: date
    effective_to: Optional[date] = None


@dataclass
class SanctionsMatch:
    """Sanctions list match details."""
    list_name: str
    match_type: str
    match_score: Decimal


@dataclass
class ControllingPerson:
    """Controlling person for entity accounts (FATCA/CRS)."""
    party_id: UUID
    control_type: str  # OWNERSHIP, SENIOR_MANAGING_OFFICIAL, CONTROLLING_PERSON
    ownership_percentage: Optional[Decimal] = None
    tax_residence: Optional[List[str]] = None
    tin: Optional[str] = None
    tin_type: Optional[str] = None
    is_pep: bool = False


@dataclass
class RegulatoryReportingInfo:
    """Regulatory reporting information attached to payment."""
    reporting_type: str
    reporting_code: Optional[str] = None
    jurisdiction: Optional[str] = None
    reporting_details: Optional[str] = None


def generate_uuid() -> UUID:
    """Generate a new UUID v4."""
    return uuid4()
