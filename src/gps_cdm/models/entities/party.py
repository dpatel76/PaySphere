"""
GPS Payments CDM - Party Domain Entities
========================================

Party entities including Party, PartyIdentification,
Person, Organisation, and FinancialInstitution.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from gps_cdm.models.entities.base import (
    Address,
    BiTemporalMixin,
    ContactDetails,
    PartitionMixin,
    SanctionsMatch,
    SourceTrackingMixin,
    TaxResidency,
    generate_uuid,
)
from gps_cdm.models.enums import (
    CRSEntityType,
    FATCAClassification,
    PartyType,
    RiskRating,
    SanctionsStatus,
    TaxIdType,
    USTaxStatus,
)


@dataclass
class Party(BiTemporalMixin, SourceTrackingMixin, PartitionMixin):
    """
    Core party entity (counterparty in payment).

    Represents individuals, organizations, governments, and
    financial institutions involved in payments.
    """
    # Primary Key
    party_id: UUID = field(default_factory=generate_uuid)

    # Core Identification
    party_type: PartyType = PartyType.INDIVIDUAL
    name: str = ""
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    suffix: Optional[str] = None  # Jr, Sr, III
    dba_name: Optional[str] = None  # Doing Business As

    # Personal Details (for individuals)
    date_of_birth: Optional[date] = None
    place_of_birth: Optional[str] = None
    nationality: Optional[List[str]] = None  # ISO country codes

    # Tax Information
    tax_id: Optional[str] = None
    tax_id_type: Optional[TaxIdType] = None

    # FATCA Extensions
    us_tax_status: Optional[USTaxStatus] = None
    fatca_classification: Optional[FATCAClassification] = None
    w8ben_status: Optional[str] = None
    w9_status: Optional[str] = None
    substantial_us_owner: Optional[bool] = None

    # CRS Extensions
    crs_reportable: Optional[bool] = None
    crs_entity_type: Optional[CRSEntityType] = None
    tax_residencies: Optional[List[TaxResidency]] = None

    # FinCEN Extensions
    occupation: Optional[str] = None  # CTR Item 12
    naics_code: Optional[str] = None  # 6-digit NAICS
    form_of_identification: Optional[str] = None
    identification_number: Optional[str] = None
    identification_issuing_country: Optional[str] = None
    identification_issuing_state: Optional[str] = None
    alternate_names: Optional[List[str]] = None  # SAR aliases

    # APAC National IDs
    national_id_type: Optional[str] = None
    national_id_number: Optional[str] = None
    china_hukou: Optional[str] = None
    india_aadhar_number: Optional[str] = None
    india_pan_number: Optional[str] = None
    japan_my_number: Optional[str] = None
    singapore_nric_fin: Optional[str] = None

    # Address
    address: Optional[Address] = None

    # Contact
    contact_details: Optional[ContactDetails] = None

    # Risk/Compliance
    pep_flag: bool = False
    pep_category: Optional[str] = None
    risk_rating: Optional[RiskRating] = None
    sanctions_screening_status: SanctionsStatus = SanctionsStatus.NOT_SCREENED
    sanctions_list_match: Optional[List[SanctionsMatch]] = None

    def is_us_person(self) -> bool:
        """Check if party is a US person for FATCA purposes."""
        if self.us_tax_status in [USTaxStatus.US_CITIZEN, USTaxStatus.US_RESIDENT_ALIEN]:
            return True
        if self.nationality and "US" in self.nationality:
            return True
        return False


@dataclass
class PartyIdentification(BiTemporalMixin):
    """
    Additional party identification documents.

    Tracks various forms of identification for KYC purposes.
    """
    identification_id: UUID = field(default_factory=generate_uuid)
    party_id: UUID = field(default_factory=generate_uuid)

    # Identification Details
    identification_type: str = ""  # PASSPORT, NATIONAL_ID, DRIVERS_LICENSE, etc.
    identification_number: str = ""
    issuing_country: str = ""  # ISO 3166-1 alpha-2
    issuing_authority: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    is_primary: bool = False

    # Verification
    verification_status: str = "UNVERIFIED"  # VERIFIED, UNVERIFIED, EXPIRED, INVALID
    verification_date: Optional[date] = None


@dataclass
class Person:
    """
    Individual-specific attributes (extends Party).

    Additional details specific to natural persons.
    """
    person_id: UUID = field(default_factory=generate_uuid)
    party_id: UUID = field(default_factory=generate_uuid)

    # Personal Details
    title: Optional[str] = None  # Mr, Ms, Dr
    suffix: Optional[str] = None
    place_of_birth: Optional[str] = None
    country_of_birth: Optional[str] = None
    gender: Optional[str] = None  # M, F, O
    marital_status: Optional[str] = None

    # Employment
    employer_name: Optional[str] = None
    employment_status: Optional[str] = None
    job_title: Optional[str] = None
    years_employed: Optional[int] = None

    # Audit
    created_timestamp: datetime = field(default_factory=datetime.utcnow)
    last_updated_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Organisation:
    """
    Organisation-specific attributes (extends Party).

    Additional details specific to legal entities.
    """
    organisation_id: UUID = field(default_factory=generate_uuid)
    party_id: UUID = field(default_factory=generate_uuid)

    # Registration
    registration_number: Optional[str] = None
    registration_country: Optional[str] = None
    legal_form: Optional[str] = None  # LLC, Corp, Ltd

    # Industry
    industry_code: Optional[str] = None  # NAICS/SIC
    industry_description: Optional[str] = None

    # Corporate Details
    incorporation_date: Optional[date] = None
    number_of_employees: Optional[int] = None
    annual_revenue: Optional[Decimal] = None

    # Public Company
    public_company: bool = False
    stock_exchange: Optional[str] = None
    ticker_symbol: Optional[str] = None

    # Parent
    parent_organisation_id: Optional[UUID] = None

    # Audit
    created_timestamp: datetime = field(default_factory=datetime.utcnow)
    last_updated_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FinancialInstitution(BiTemporalMixin, SourceTrackingMixin):
    """
    Financial institution entity.

    Banks, broker-dealers, MSBs, and other financial institutions.
    """
    fi_id: UUID = field(default_factory=generate_uuid)
    institution_name: str = ""

    # Identifiers
    bic: Optional[str] = None  # SWIFT BIC (8 or 11)
    lei: Optional[str] = None  # Legal Entity Identifier (20)
    national_clearing_code: Optional[str] = None  # Routing/Sort/BSB
    national_clearing_system: Optional[str] = None

    # FinCEN Fields
    rssd_number: Optional[str] = None  # Federal Reserve RSSD
    tin_type: Optional[str] = None
    tin_value: Optional[str] = None
    fi_type: Optional[str] = None  # DEPOSITORY, BROKER_DEALER, MSB
    msb_registration_number: Optional[str] = None
    primary_regulator: Optional[str] = None  # OCC, FDIC, FRB

    # FATCA
    fatca_giin: Optional[str] = None

    # Islamic Finance
    sharia_compliant: bool = False
    islamic_finance_type: Optional[str] = None

    # Location
    address: Optional[Address] = None
    country: str = ""
    branch_identification: Optional[str] = None
    branch_name: Optional[str] = None

    def validate_bic(self) -> bool:
        """Validate BIC format."""
        if not self.bic:
            return True
        import re
        pattern = r"^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$"
        return bool(re.match(pattern, self.bic))
