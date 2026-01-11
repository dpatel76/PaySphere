"""Saudi Arabia SARIE (Saudi Arabian Riyal Interbank Express) Extractor.

ISO 20022 INHERITANCE HIERARCHY:
    SARIE uses Saudi Central Bank (SAMA) ISO 20022 usage guidelines.
    Supports multiple ISO 20022 message types:

    BaseISO20022Parser
        ├── Pacs008Parser (FI to FI Customer Credit Transfer)
        │   └── SariePacs008Parser
        ├── Pacs002Parser (Payment Status Report)
        │   └── SariePacs002Parser
        ├── Pacs004Parser (Payment Return)
        │   └── SariePacs004Parser
        └── Pain001Parser (Customer Credit Transfer Initiation)
            └── SariePain001Parser

SUPPORTED MESSAGE TYPES:
    - pacs.008: Customer Credit Transfer (primary RTGS payment)
    - pacs.002: Payment Status Report
    - pacs.004: Payment Return
    - pain.001: Customer Credit Transfer Initiation (bank-customer interface)

SARIE-SPECIFIC ELEMENTS:
    - Saudi IBAN format (SA + 2 check digits + 2 bank code + 18 account number)
    - SAR currency (Saudi Riyal)
    - BIC/SWIFT codes for Saudi financial institutions
    - Real-time gross settlement via SAMA

CLEARING SYSTEM:
    - SASARIE (Saudi Arabian Riyal Interbank Express)
    - Operated by Saudi Central Bank (SAMA)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re
import logging
import xml.etree.ElementTree as ET

from ..base import (
    BaseExtractor,
    ExtractorRegistry,
    GoldEntities,
    PartyData,
    AccountData,
    FinancialInstitutionData,
)

logger = logging.getLogger(__name__)

# Import ISO 20022 base classes for inheritance
try:
    from ..iso20022 import (
        Pacs008Parser, Pacs008Extractor,
        Pacs002Parser, Pacs002Extractor,
        Pacs004Parser, Pacs004Extractor,
        Pain001Parser, Pain001Extractor,
    )
    ISO20022_BASE_AVAILABLE = True
except ImportError:
    ISO20022_BASE_AVAILABLE = False
    logger.warning("ISO 20022 base classes not available - SARIE will use standalone implementation")


# =============================================================================
# SARIE CONSTANTS
# =============================================================================

CLEARING_SYSTEM = "SASARIE"
DEFAULT_CURRENCY = "SAR"
DEFAULT_COUNTRY = "SA"


# =============================================================================
# SARIE ISO 20022 PARSERS (inherit from base ISO 20022 parsers)
# =============================================================================

# Conditional inheritance for backward compatibility
_Pacs008Base = Pacs008Parser if ISO20022_BASE_AVAILABLE else object
_Pacs002Base = Pacs002Parser if ISO20022_BASE_AVAILABLE else object
_Pacs004Base = Pacs004Parser if ISO20022_BASE_AVAILABLE else object
_Pain001Base = Pain001Parser if ISO20022_BASE_AVAILABLE else object


class SariePacs008Parser(_Pacs008Base):
    """SARIE pacs.008 parser - FI to FI Customer Credit Transfer.

    Primary message type for SARIE RTGS payments.
    Inherits all pacs.008 parsing from base and adds SARIE-specific fields.
    """

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "SARIE_pacs008"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse SARIE pacs.008 message using inherited base parsing."""
        if isinstance(raw_content, dict):
            return raw_content

        if isinstance(raw_content, str) and raw_content.strip().startswith('{'):
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError:
                pass

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'SARIE_pacs008'}

        # Add SARIE-specific fields
        result['isSarie'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        result['defaultCurrency'] = self.DEFAULT_CURRENCY

        return result


class SariePacs002Parser(_Pacs002Base):
    """SARIE pacs.002 parser - Payment Status Report.

    Used for payment acknowledgments and status updates.
    """

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "SARIE_pacs002"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return raw_content

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'SARIE_pacs002'}

        result['isSarie'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        return result


class SariePacs004Parser(_Pacs004Base):
    """SARIE pacs.004 parser - Payment Return.

    Used for payment returns and rejections.
    """

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "SARIE_pacs004"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return raw_content

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'SARIE_pacs004'}

        result['isSarie'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        return result


class SariePain001Parser(_Pain001Base):
    """SARIE pain.001 parser - Customer Credit Transfer Initiation.

    Used for bank-customer interface (initiation of payments).
    """

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "SARIE_pain001"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return raw_content

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'SARIE_pain001'}

        result['isSarie'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        return result


# =============================================================================
# UNIFIED SARIE PARSER (auto-detects message type)
# =============================================================================

class SarieISO20022Parser:
    """Unified SARIE ISO 20022 parser that auto-detects message type.

    Automatically routes to the appropriate parser based on XML root element:
    - FIToFICstmrCdtTrf -> SariePacs008Parser
    - FIToFIPmtStsRpt -> SariePacs002Parser
    - PmtRtr -> SariePacs004Parser
    - CstmrCdtTrfInitn -> SariePain001Parser
    """

    ROOT_TO_PARSER = {
        'FIToFICstmrCdtTrf': 'pacs008',
        'FIToFIPmtStsRpt': 'pacs002',
        'PmtRtr': 'pacs004',
        'CstmrCdtTrfInitn': 'pain001',
    }

    def __init__(self):
        self.pacs008_parser = SariePacs008Parser()
        self.pacs002_parser = SariePacs002Parser()
        self.pacs004_parser = SariePacs004Parser()
        self.pain001_parser = SariePain001Parser()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse SARIE ISO 20022 message, auto-detecting type."""
        if isinstance(raw_content, dict):
            return raw_content

        if isinstance(raw_content, str) and raw_content.strip().startswith('{'):
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError:
                pass

        # Detect message type from XML
        msg_type = self._detect_message_type(raw_content)

        if msg_type == 'pacs008':
            return self.pacs008_parser.parse(raw_content)
        elif msg_type == 'pacs002':
            return self.pacs002_parser.parse(raw_content)
        elif msg_type == 'pacs004':
            return self.pacs004_parser.parse(raw_content)
        elif msg_type == 'pain001':
            return self.pain001_parser.parse(raw_content)
        else:
            # Default to pacs.008 (most common)
            return self.pacs008_parser.parse(raw_content)

    def _detect_message_type(self, xml_content: str) -> str:
        """Detect ISO 20022 message type from XML content."""
        for root_elem, msg_type in self.ROOT_TO_PARSER.items():
            if root_elem in xml_content:
                return msg_type
        return 'pacs008'  # Default


# =============================================================================
# SARIE EXTRACTOR (handles all message types)
# =============================================================================

class SarieExtractor(BaseExtractor):
    """Extractor for Saudi Arabia SARIE payment messages.

    ISO 20022 INHERITANCE:
        SARIE uses SAMA (Saudi Central Bank) ISO 20022 usage guidelines.
        Supports pacs.008, pacs.002, pacs.004, and pain.001 message types.

    Message Type Support:
        - SARIE / SARIE_pacs008: Customer Credit Transfer (primary)
        - SARIE_pacs002: Payment Status Report
        - SARIE_pacs004: Payment Return
        - SARIE_pain001: Customer Credit Transfer Initiation

    Database Tables:
        - Bronze: bronze.raw_payment_messages
        - Silver: silver.stg_sarie (legacy) or silver.stg_iso20022_pacs008 (ISO)
        - Gold: Semantic tables via DynamicGoldMapper
    """

    MESSAGE_TYPE = "SARIE"
    SILVER_TABLE = "stg_sarie"
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    CLEARING_SYSTEM = CLEARING_SYSTEM

    def __init__(self):
        """Initialize extractor with ISO 20022 parser."""
        super().__init__()
        self.iso20022_parser = SarieISO20022Parser()
        self.parser = self.iso20022_parser

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw SARIE content."""
        msg_id = (
            raw_content.get('messageId') or
            raw_content.get('instructionId') or
            raw_content.get('endToEndId') or
            ''
        )
        return {
            'raw_id': self.generate_raw_id(msg_id),
            'message_type': self.MESSAGE_TYPE,
            'raw_content': json.dumps(raw_content) if isinstance(raw_content, dict) else raw_content,
            'batch_id': batch_id,
        }

    # =========================================================================
    # SILVER EXTRACTION
    # =========================================================================

    def extract_silver(
        self,
        msg_content: Dict[str, Any],
        raw_id: str,
        stg_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        """Extract Silver layer fields from SARIE message.

        Handles ISO 20022 parser output with camelCase field names.
        """
        trunc = self.trunc

        # Parse if needed
        if isinstance(msg_content, str):
            msg_content = self.parser.parse(msg_content)
        elif not msg_content.get('isISO20022') and not msg_content.get('isSarie'):
            # Parse raw content
            msg_content = self.parser.parse(json.dumps(msg_content) if isinstance(msg_content, dict) else msg_content)

        # Map ISO 20022 camelCase to Silver snake_case
        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,
            'message_type': 'SARIE',

            # Message identification
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': msg_content.get('settlementDate') or msg_content.get('interbankSettlementDate'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or DEFAULT_CURRENCY,

            # Payment identification
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'transaction_id': trunc(msg_content.get('transactionId'), 35),
            'uetr': trunc(msg_content.get('uetr'), 36),

            # Agents
            'sending_bank_code': trunc(
                msg_content.get('debtorAgentBic') or
                msg_content.get('instructingAgentBic'),
                11
            ),
            'receiving_bank_code': trunc(
                msg_content.get('creditorAgentBic') or
                msg_content.get('instructedAgentBic'),
                11
            ),

            # Debtor (Originator)
            'originator_name': trunc(msg_content.get('debtorName'), 140),
            'originator_account': trunc(
                msg_content.get('debtorAccountIban') or
                msg_content.get('debtorAccountOther'),
                34
            ),
            'originator_id': trunc(msg_content.get('debtorLei') or msg_content.get('debtorOtherId'), 35),

            # Creditor (Beneficiary)
            'beneficiary_name': trunc(msg_content.get('creditorName'), 140),
            'beneficiary_account': trunc(
                msg_content.get('creditorAccountIban') or
                msg_content.get('creditorAccountOther'),
                34
            ),
            'beneficiary_id': trunc(msg_content.get('creditorLei') or msg_content.get('creditorOtherId'), 35),

            # Purpose/Remittance
            'purpose': msg_content.get('remittanceUnstructured') or msg_content.get('purposeCode'),

            # Charge bearer
            'charge_bearer': trunc(msg_content.get('chargeBearer'), 10),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'message_id', 'creation_date_time',
            'settlement_date', 'amount', 'currency',
            'instruction_id', 'end_to_end_id', 'transaction_id', 'uetr',
            'sending_bank_code', 'receiving_bank_code',
            'originator_name', 'originator_account', 'originator_id',
            'beneficiary_name', 'beneficiary_account', 'beneficiary_id',
            'purpose', 'charge_bearer',
        ]

    def get_silver_values(self, silver_record: Dict[str, Any]) -> tuple:
        """Return ordered tuple of values for Silver table INSERT."""
        columns = self.get_silver_columns()
        return tuple(silver_record.get(col) for col in columns)

    # =========================================================================
    # GOLD ENTITY EXTRACTION
    # =========================================================================

    def extract_gold_entities(
        self,
        silver_data: Dict[str, Any],
        stg_id: str,
        batch_id: str
    ) -> GoldEntities:
        """Extract Gold layer entities from SARIE Silver record."""
        entities = GoldEntities()

        # Originator Party (Debtor)
        if silver_data.get('originator_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('originator_name'),
                role="DEBTOR",
                party_type='ORGANIZATION',
                identification_number=silver_data.get('originator_id'),
                country=DEFAULT_COUNTRY,
            ))

        # Beneficiary Party (Creditor)
        if silver_data.get('beneficiary_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('beneficiary_name'),
                role="CREDITOR",
                party_type='ORGANIZATION',
                identification_number=silver_data.get('beneficiary_id'),
                country=DEFAULT_COUNTRY,
            ))

        # Originator Account
        if silver_data.get('originator_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('originator_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or DEFAULT_CURRENCY,
            ))

        # Beneficiary Account
        if silver_data.get('beneficiary_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('beneficiary_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or DEFAULT_CURRENCY,
            ))

        # Sending Bank (Debtor Agent)
        sending_bank = silver_data.get('sending_bank_code')
        if sending_bank:
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                bic=sending_bank if len(sending_bank) in (8, 11) else None,
                clearing_code=sending_bank if len(sending_bank) not in (8, 11) else None,
                clearing_system=CLEARING_SYSTEM,
                country=DEFAULT_COUNTRY,
            ))

        # Receiving Bank (Creditor Agent)
        receiving_bank = silver_data.get('receiving_bank_code')
        if receiving_bank:
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                bic=receiving_bank if len(receiving_bank) in (8, 11) else None,
                clearing_code=receiving_bank if len(receiving_bank) not in (8, 11) else None,
                clearing_system=CLEARING_SYSTEM,
                country=DEFAULT_COUNTRY,
            ))

        return entities


# =============================================================================
# REGISTER EXTRACTORS
# =============================================================================

# Main SARIE extractor (handles all message types via auto-detection)
ExtractorRegistry.register('SARIE', SarieExtractor())
ExtractorRegistry.register('sarie', SarieExtractor())

# Message type specific aliases
ExtractorRegistry.register('SARIE_pacs008', SarieExtractor())
ExtractorRegistry.register('SARIE_pacs002', SarieExtractor())
ExtractorRegistry.register('SARIE_pacs004', SarieExtractor())
ExtractorRegistry.register('SARIE_pain001', SarieExtractor())
