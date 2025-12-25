"""
GPS CDM - Pytest Configuration and Fixtures
============================================

Shared fixtures for unit and integration tests.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from uuid import uuid4

from gps_cdm.models import (
    Payment,
    Party,
    Account,
    CashAccount,
    Settlement,
    PaymentEvent,
    LineageMetadata,
    AuditTrail,
)
from gps_cdm.models.enums import (
    PaymentType,
    PaymentStatus,
    SchemeCode,
    PaymentDirection,
    PartyType,
    AccountType,
    AccountStatus,
)


# ============================================================================
# Payment Fixtures
# ============================================================================

@pytest.fixture
def sample_payment():
    """Create a sample payment for testing."""
    return Payment(
        payment_type=PaymentType.CREDIT_TRANSFER,
        scheme_code=SchemeCode.SWIFT,
        status=PaymentStatus.INITIATED,
        direction=PaymentDirection.OUTBOUND,
        cross_border_flag=True,
    )


@pytest.fixture
def sample_domestic_payment():
    """Create a sample domestic payment for testing."""
    return Payment(
        payment_type=PaymentType.CREDIT_TRANSFER,
        scheme_code=SchemeCode.ACH,
        status=PaymentStatus.INITIATED,
        direction=PaymentDirection.OUTBOUND,
        cross_border_flag=False,
    )


# ============================================================================
# Party Fixtures
# ============================================================================

@pytest.fixture
def sample_individual_party():
    """Create a sample individual party for testing."""
    return Party(
        party_type=PartyType.INDIVIDUAL,
        name="John Doe",
        country="US",
    )


@pytest.fixture
def sample_corporate_party():
    """Create a sample corporate party for testing."""
    return Party(
        party_type=PartyType.CORPORATE,
        name="Acme Corporation",
        country="US",
        lei="529900T8BM49AURSDO55",
    )


@pytest.fixture
def sample_financial_institution():
    """Create a sample financial institution party for testing."""
    return Party(
        party_type=PartyType.FINANCIAL_INSTITUTION,
        name="First National Bank",
        country="US",
    )


# ============================================================================
# Account Fixtures
# ============================================================================

@pytest.fixture
def sample_account():
    """Create a sample account for testing."""
    return Account(
        account_type=AccountType.CHECKING,
        account_status=AccountStatus.ACTIVE,
        currency="USD",
        country="US",
    )


@pytest.fixture
def sample_cash_account():
    """Create a sample cash account for testing."""
    return CashAccount(
        account_type=AccountType.CHECKING,
        account_status=AccountStatus.ACTIVE,
        currency="USD",
        iban="US12345678901234567890",
    )


# ============================================================================
# Settlement Fixtures
# ============================================================================

@pytest.fixture
def sample_settlement():
    """Create a sample settlement for testing."""
    return Settlement(
        settlement_date=date.today(),
        settlement_amount=Decimal("10000.00"),
        settlement_currency="USD",
    )


# ============================================================================
# Event Fixtures
# ============================================================================

@pytest.fixture
def sample_payment_event(sample_payment):
    """Create a sample payment event for testing."""
    return PaymentEvent(
        payment_id=sample_payment.payment_id,
        new_state="INITIATED",
    )


# ============================================================================
# Lineage Fixtures
# ============================================================================

@pytest.fixture
def sample_lineage_metadata():
    """Create a sample lineage metadata for testing."""
    return LineageMetadata(
        entity_type="Payment",
        field_name="amount",
        source_system="core_banking",
        source_field="txn_amount",
    )


@pytest.fixture
def sample_audit_trail():
    """Create a sample audit trail for testing."""
    return AuditTrail(
        entity_type="Payment",
        actor="system",
    )


# ============================================================================
# Test Data Generators
# ============================================================================

@pytest.fixture
def payment_factory():
    """Factory fixture for creating payments with custom attributes."""
    def _create_payment(**kwargs):
        defaults = {
            "payment_type": PaymentType.CREDIT_TRANSFER,
            "scheme_code": SchemeCode.SWIFT,
            "status": PaymentStatus.INITIATED,
            "direction": PaymentDirection.OUTBOUND,
        }
        defaults.update(kwargs)
        return Payment(**defaults)
    return _create_payment


@pytest.fixture
def party_factory():
    """Factory fixture for creating parties with custom attributes."""
    def _create_party(**kwargs):
        defaults = {
            "party_type": PartyType.INDIVIDUAL,
            "name": "Test Party",
            "country": "US",
        }
        defaults.update(kwargs)
        return Party(**defaults)
    return _create_party
