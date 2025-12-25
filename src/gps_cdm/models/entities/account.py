"""
GPS Payments CDM - Account Domain Entities
==========================================

Account entities including Account, CashAccount, and AccountOwner.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from gps_cdm.models.entities.base import (
    BiTemporalMixin,
    ControllingPerson,
    PartitionMixin,
    SourceTrackingMixin,
    generate_uuid,
)
from gps_cdm.models.enums import (
    AccountStatus,
    AccountType,
    OwnershipType,
    RiskRating,
    SanctionsStatus,
)


@dataclass
class Account(BiTemporalMixin, SourceTrackingMixin, PartitionMixin):
    """
    Core account entity.

    Represents bank accounts, investment accounts, and other
    financial accounts involved in payments.
    """
    # Primary Key
    account_id: UUID = field(default_factory=generate_uuid)

    # Core Identification
    account_number: str = ""
    iban: Optional[str] = None
    account_type: AccountType = AccountType.CHECKING
    currency: str = "USD"

    # Relationships
    financial_institution_id: UUID = field(default_factory=generate_uuid)
    branch_id: Optional[str] = None

    # Status
    account_status: AccountStatus = AccountStatus.ACTIVE
    open_date: date = field(default_factory=date.today)
    close_date: Optional[date] = None

    # Balances
    current_balance: Optional[Decimal] = None
    available_balance: Optional[Decimal] = None
    ledger_balance: Optional[Decimal] = None
    last_transaction_date: Optional[datetime] = None

    # FATCA Extensions
    fatca_status: Optional[str] = None
    fatca_giin: Optional[str] = None
    account_holder_type: Optional[str] = None

    # CRS Extensions
    crs_reportable_account: Optional[bool] = None
    controlling_persons: Optional[List[ControllingPerson]] = None
    dormant_account: Optional[bool] = None
    account_balance_for_tax_reporting: Optional[Decimal] = None
    withholding_tax_rate: Optional[Decimal] = None

    # FinCEN Extensions (for loans)
    loan_amount: Optional[Decimal] = None
    loan_origination: Optional[date] = None

    # Risk
    sanctions_screening_status: SanctionsStatus = SanctionsStatus.NOT_SCREENED
    risk_rating: Optional[RiskRating] = None

    def is_dormant(self, days_threshold: int = 365) -> bool:
        """Check if account is dormant based on last activity."""
        if not self.last_transaction_date:
            return True
        days_since_activity = (datetime.utcnow() - self.last_transaction_date).days
        return days_since_activity > days_threshold

    def validate_iban(self) -> bool:
        """Validate IBAN format."""
        if not self.iban:
            return True
        import re
        pattern = r"^[A-Z]{2}[0-9]{2}[A-Z0-9]+$"
        return bool(re.match(pattern, self.iban)) and len(self.iban) <= 34


@dataclass
class CashAccount:
    """
    Cash account specific attributes.

    ISO 20022 cash account type details.
    """
    cash_account_id: UUID = field(default_factory=generate_uuid)
    account_id: UUID = field(default_factory=generate_uuid)

    # Type
    cash_account_type: str = "CACC"  # CACC, SVGS, CASH, LOAN, CARD, OTHR
    proprietary_type: Optional[str] = None
    secondary_id: Optional[str] = None

    # Limits
    overdraft_limit: Optional[Decimal] = None
    credit_limit: Optional[Decimal] = None

    # Interest
    interest_rate: Optional[Decimal] = None
    interest_type: Optional[str] = None  # FIXED, VARIABLE, TIERED

    # Fees
    minimum_balance: Optional[Decimal] = None
    monthly_fee: Optional[Decimal] = None

    # Audit
    created_timestamp: datetime = field(default_factory=datetime.utcnow)
    last_updated_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AccountOwner(BiTemporalMixin):
    """
    Account ownership relationship.

    Links parties to accounts with ownership details.
    """
    account_owner_id: UUID = field(default_factory=generate_uuid)
    account_id: UUID = field(default_factory=generate_uuid)
    party_id: UUID = field(default_factory=generate_uuid)

    # Ownership
    ownership_type: OwnershipType = OwnershipType.PRIMARY
    ownership_percentage: Optional[Decimal] = None
    role: Optional[str] = None  # OWNER, SIGNATORY, TRUSTEE, etc.

    # Signing Authority
    signing_authority: Optional[str] = None  # SOLE, JOINT_ANY, JOINT_ALL
    signing_limit: Optional[Decimal] = None

    # CRS/FATCA
    is_controlling_person: bool = False
    control_type: Optional[str] = None
    tax_residence: Optional[List[str]] = None

    # Effective Dates
    effective_from: date = field(default_factory=date.today)
    effective_to: Optional[date] = None
