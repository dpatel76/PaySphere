"""
GPS Payments Common Domain Model (CDM)
======================================

A comprehensive data model for payment processing, regulatory reporting,
and analytics supporting:

- 16 payment standards (ISO 20022, SWIFT MT, ACH, SEPA, PIX, UPI, etc.)
- 13 regulatory reports (FinCEN CTR/SAR, AUSTRAC IFTI/TTR, FATCA, CRS, etc.)
- End-to-end data lineage from source to report
- Fraud detection via graph analytics
- 50M+ messages/day throughput

Modules:
    - models: CDM entity dataclasses (29 entities across 8 domains)
    - parsers: Message parsers for various payment formats
    - transformers: Bronze -> Silver -> Gold transformations
    - lineage: Data lineage tracking and management
    - dsl: Domain Specific Language for regulatory reports
    - traceability: Regulatory requirement traceability

Example:
    from gps_cdm.models import Payment, Party, Account
    from gps_cdm.models.enums import PaymentType, PaymentStatus

    payment = Payment(
        payment_type=PaymentType.CREDIT_TRANSFER,
        scheme_code=SchemeCode.SWIFT,
        status=PaymentStatus.INITIATED
    )
"""

__version__ = "1.0.0"
__author__ = "GPS CDM Team"

from gps_cdm.models import (
    Account,
    AuditTrail,
    CashAccount,
    Charges,
    ClearingSystem,
    CreditTransfer,
    CurrencyExchange,
    DirectDebit,
    FinancialInstitution,
    LineageMetadata,
    Organisation,
    Party,
    PartyIdentification,
    Payment,
    PaymentEvent,
    PaymentInstruction,
    PaymentReturn,
    PaymentReversal,
    PaymentStatusReport,
    Person,
    Settlement,
    SettlementInstruction,
    WorkflowEvent,
)

__all__ = [
    # Version
    "__version__",
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
