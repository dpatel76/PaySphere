"""
GPS CDM - Model Unit Tests
==========================

Unit tests for CDM dataclass models.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from gps_cdm.models import (
    Payment,
    Party,
    Account,
    Settlement,
    PaymentEvent,
    LineageMetadata,
    AuditTrail,
)
from gps_cdm.models.enums import (
    PaymentType,
    PaymentStatus,
    SchemeCode,
    PartyType,
    RiskRating,
    TransformationType,
    AuditAction,
)


class TestPayment:
    """Tests for Payment entity."""

    def test_payment_creation_defaults(self, sample_payment):
        """Test payment is created with correct defaults."""
        assert sample_payment.payment_id is not None
        assert isinstance(sample_payment.payment_id, UUID)
        assert sample_payment.status == PaymentStatus.INITIATED

    def test_payment_cross_border_flag(self, sample_payment, sample_domestic_payment):
        """Test cross border flag is set correctly."""
        assert sample_payment.cross_border_flag is True
        assert sample_domestic_payment.cross_border_flag is False

    def test_payment_factory(self, payment_factory):
        """Test payment factory creates valid payments."""
        payment = payment_factory(
            scheme_code=SchemeCode.ACH,
            status=PaymentStatus.COMPLETED,
        )
        assert payment.scheme_code == SchemeCode.ACH
        assert payment.status == PaymentStatus.COMPLETED


class TestParty:
    """Tests for Party entity."""

    def test_individual_party(self, sample_individual_party):
        """Test individual party creation."""
        assert sample_individual_party.party_type == PartyType.INDIVIDUAL
        assert sample_individual_party.name == "John Doe"

    def test_corporate_party_with_lei(self, sample_corporate_party):
        """Test corporate party with LEI."""
        assert sample_corporate_party.party_type == PartyType.CORPORATE
        assert sample_corporate_party.lei == "529900T8BM49AURSDO55"

    def test_party_factory(self, party_factory):
        """Test party factory creates valid parties."""
        party = party_factory(
            name="Test Corp",
            party_type=PartyType.CORPORATE,
            risk_rating=RiskRating.HIGH,
        )
        assert party.name == "Test Corp"
        assert party.risk_rating == RiskRating.HIGH


class TestLineageMetadata:
    """Tests for LineageMetadata entity."""

    def test_lineage_creation(self, sample_lineage_metadata):
        """Test lineage metadata creation."""
        assert sample_lineage_metadata.entity_type == "Payment"
        assert sample_lineage_metadata.source_system == "core_banking"

    def test_lineage_is_active(self, sample_lineage_metadata):
        """Test lineage is_active method."""
        assert sample_lineage_metadata.is_active() is True

    def test_lineage_transformation_type_default(self, sample_lineage_metadata):
        """Test default transformation type."""
        assert sample_lineage_metadata.transformation_type == TransformationType.DIRECT


class TestAuditTrail:
    """Tests for AuditTrail entity."""

    def test_audit_trail_creation(self, sample_audit_trail):
        """Test audit trail creation."""
        assert sample_audit_trail.entity_type == "Payment"
        assert sample_audit_trail.action == AuditAction.CREATE

    def test_audit_trail_changed_field_count(self):
        """Test changed field count method."""
        audit = AuditTrail(
            entity_type="Payment",
            actor="user",
            changed_fields=["amount", "currency", "status"],
        )
        assert audit.get_changed_field_count() == 3

    def test_audit_trail_sensitive_data_detection(self):
        """Test sensitive data detection."""
        audit = AuditTrail(
            entity_type="Party",
            actor="user",
            changed_fields=["name", "tax_id"],
        )
        assert audit.contains_sensitive_data() is True

    def test_audit_trail_no_sensitive_data(self):
        """Test non-sensitive data detection."""
        audit = AuditTrail(
            entity_type="Payment",
            actor="user",
            changed_fields=["amount", "currency"],
        )
        assert audit.contains_sensitive_data() is False


class TestSettlement:
    """Tests for Settlement entity."""

    def test_settlement_creation(self, sample_settlement):
        """Test settlement creation with defaults."""
        assert sample_settlement.settlement_amount == Decimal("10000.00")
        assert sample_settlement.settlement_currency == "USD"

    def test_settlement_date_default(self, sample_settlement):
        """Test settlement date defaults to today."""
        assert sample_settlement.settlement_date == date.today()


class TestPaymentEvent:
    """Tests for PaymentEvent entity."""

    def test_payment_event_creation(self, sample_payment_event):
        """Test payment event creation."""
        assert sample_payment_event.new_state == "INITIATED"

    def test_is_error_event_false(self, sample_payment_event):
        """Test is_error_event returns False for normal events."""
        assert sample_payment_event.is_error_event() is False

    def test_is_error_event_with_error_code(self, sample_payment):
        """Test is_error_event returns True when error_code is set."""
        event = PaymentEvent(
            payment_id=sample_payment.payment_id,
            new_state="FAILED",
            error_code="ERR001",
            error_message="Payment failed",
        )
        assert event.is_error_event() is True
