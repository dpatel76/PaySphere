"""
GPS Payments CDM - Python Models
================================

This package contains Python dataclass implementations of the GPS Payments
Common Domain Model (CDM) entities.

Modules:
    - entities: Core CDM entity models (Payment, Party, Account, etc.)
    - enums: Enumeration types used across entities
    - mixins: Common patterns (BiTemporal, Auditable, SourceTracking)

Usage:
    from gps_cdm.models import Payment, Party, Account
    from gps_cdm.models.enums import PaymentType, PaymentStatus
"""

from gps_cdm.models.entities.payment import (
    Payment,
    PaymentInstruction,
    CreditTransfer,
    DirectDebit,
    PaymentReturn,
    PaymentReversal,
    PaymentStatusReport,
)
from gps_cdm.models.entities.party import (
    Party,
    PartyIdentification,
    Person,
    Organisation,
    FinancialInstitution,
)
from gps_cdm.models.entities.account import (
    Account,
    CashAccount,
    AccountOwner,
)
from gps_cdm.models.entities.amount import (
    Amount,
    CurrencyExchange,
    Charges,
)
from gps_cdm.models.entities.settlement import (
    Settlement,
    SettlementInstruction,
    ClearingSystem,
)
from gps_cdm.models.entities.events import (
    PaymentEvent,
    WorkflowEvent,
)
from gps_cdm.models.entities.lineage import (
    LineageMetadata,
    AuditTrail,
)

__all__ = [
    # Payment Core
    "Payment",
    "PaymentInstruction",
    "CreditTransfer",
    "DirectDebit",
    "PaymentReturn",
    "PaymentReversal",
    "PaymentStatusReport",
    # Party
    "Party",
    "PartyIdentification",
    "Person",
    "Organisation",
    "FinancialInstitution",
    # Account
    "Account",
    "CashAccount",
    "AccountOwner",
    # Amount
    "Amount",
    "CurrencyExchange",
    "Charges",
    # Settlement
    "Settlement",
    "SettlementInstruction",
    "ClearingSystem",
    # Events
    "PaymentEvent",
    "WorkflowEvent",
    # Lineage
    "LineageMetadata",
    "AuditTrail",
]

__version__ = "1.0.0"
