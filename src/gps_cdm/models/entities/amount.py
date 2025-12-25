"""
GPS Payments CDM - Amount Domain Entities
=========================================

Amount entities including Amount, CurrencyExchange, and Charges.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from gps_cdm.models.entities.base import generate_uuid
from gps_cdm.models.enums import ChargeBearer


@dataclass
class Amount:
    """
    Monetary amount entity.

    Represents a monetary value with currency.
    """
    amount_id: UUID = field(default_factory=generate_uuid)
    value: Decimal = Decimal("0")
    currency: str = "USD"  # ISO 4217
    amount_type: str = "INSTRUCTED"  # INSTRUCTED, SETTLEMENT, EQUIVALENT, etc.
    precision: Optional[int] = None
    minor_units: Optional[int] = None  # e.g., 2 for USD, 0 for JPY
    amount_qualifier: str = "EXACT"  # EXACT, APPROXIMATE, MINIMUM, MAXIMUM
    control_sum: Optional[Decimal] = None
    created_timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_minor_units(self) -> int:
        """Convert amount to minor units (e.g., cents)."""
        units = self.minor_units or 2
        return int(self.value * (10 ** units))

    def format_display(self) -> str:
        """Format amount for display."""
        return f"{self.currency} {self.value:,.2f}"


@dataclass
class CurrencyExchange:
    """
    Currency exchange details.

    Records FX information for cross-currency payments.
    """
    exchange_id: UUID = field(default_factory=generate_uuid)
    payment_id: UUID = field(default_factory=generate_uuid)

    # Currencies
    source_currency: str = "USD"
    target_currency: str = "EUR"
    exchange_rate: Decimal = Decimal("1.0")
    unit_currency: Optional[str] = None

    # Contract
    contract_id: Optional[str] = None
    quotation_date: Optional[date] = None
    rate_type: Optional[str] = None  # SPOT, FORWARD, AGREED, INDICATIVE

    # Amounts
    source_amount_id: Optional[UUID] = None
    target_amount_id: Optional[UUID] = None

    # Rate Source
    rate_source: Optional[str] = None  # Reuters, Bloomberg
    rate_reference_number: Optional[str] = None

    # Audit
    created_timestamp: datetime = field(default_factory=datetime.utcnow)

    def calculate_target_amount(self, source_amount: Decimal) -> Decimal:
        """Calculate target amount based on exchange rate."""
        return source_amount * self.exchange_rate


@dataclass
class Charges:
    """
    Payment charges and fees.

    Records fees associated with payment processing.
    """
    charge_id: UUID = field(default_factory=generate_uuid)
    payment_id: UUID = field(default_factory=generate_uuid)

    # Charge Details
    charge_type: str = "TRANSFER"  # AGENT, CLEARING, TRANSFER, etc.
    charge_bearer: ChargeBearer = ChargeBearer.SHAR
    amount: Decimal = Decimal("0")
    currency: str = "USD"

    # Agent
    agent_id: Optional[UUID] = None

    # Tax
    tax_amount: Optional[Decimal] = None
    tax_currency: Optional[str] = None

    # Description
    charge_reason: Optional[str] = None
    charge_included: bool = False
    charge_date: Optional[date] = None
    charge_reference: Optional[str] = None

    # Audit
    created_timestamp: datetime = field(default_factory=datetime.utcnow)
