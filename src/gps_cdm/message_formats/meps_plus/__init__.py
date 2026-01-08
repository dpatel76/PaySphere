"""Singapore MEPS+ (MAS Electronic Payment System Plus) Extractor - ISO 20022 based.

ISO 20022 INHERITANCE HIERARCHY:
    MEPS+ uses MAS (Monetary Authority of Singapore) ISO 20022 usage guidelines based on pacs.008.
    The MepsPlusISO20022Parser inherits from Pacs008Parser.

    BaseISO20022Parser
        └── Pacs008Parser (FI to FI Customer Credit Transfer - pacs.008.001.08)
            └── MepsPlusISO20022Parser (MAS MEPS+ usage guidelines)

MEPS+-SPECIFIC ELEMENTS:
    - SGMEP clearing system (Singapore MEPS+)
    - SGD currency (Singapore Dollars)
    - Real-time gross settlement (RTGS)
    - Operated by MAS (Monetary Authority of Singapore)

CLEARING SYSTEM:
    - SGMEP (Singapore MEPS+)
    - Operated by Monetary Authority of Singapore

DATABASE TABLES:
    - Bronze: bronze.raw_payment_messages
    - Silver: silver.stg_meps_plus
    - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_meps_plus

MAPPING INHERITANCE:
    MEPS_PLUS -> pacs.008.base (COMPLETE)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

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
    from ..iso20022 import Pacs008Parser, Pacs008Extractor
    ISO20022_BASE_AVAILABLE = True
except ImportError:
    ISO20022_BASE_AVAILABLE = False
    logger.warning("ISO 20022 base classes not available - MEPS+ will use standalone implementation")


# =============================================================================
# MEPS+ ISO 20022 PARSER (inherits from Pacs008Parser)
# =============================================================================

# Use conditional inheritance pattern for backward compatibility
_MepsPlusParserBase = Pacs008Parser if ISO20022_BASE_AVAILABLE else object


class MepsPlusISO20022Parser(_MepsPlusParserBase):
    """MEPS+ ISO 20022 pacs.008 parser with MAS usage guidelines.

    Inherits from Pacs008Parser and adds MEPS+-specific processing:
    - SGMEP clearing system identification
    - Singapore-specific address format handling
    - MAS regulatory requirements

    ISO 20022 Version: pacs.008.001.08
    Usage Guidelines: MAS MEPS+ Service

    Inheritance Hierarchy:
        BaseISO20022Parser -> Pacs008Parser -> MepsPlusISO20022Parser
    """

    # MEPS+-specific constants
    CLEARING_SYSTEM = "SGMEP"  # Singapore MEPS+
    DEFAULT_CURRENCY = "SGD"
    MESSAGE_TYPE = "MEPS_PLUS"

    def __init__(self):
        """Initialize MEPS+ parser."""
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse MEPS+ ISO 20022 pacs.008 message.

        Uses inherited pacs.008 parsing from Pacs008Parser and adds
        MEPS+-specific fields.
        """
        # Handle JSON/dict input
        if isinstance(raw_content, dict):
            return raw_content

        if isinstance(raw_content, str) and raw_content.strip().startswith('{'):
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError:
                pass

        # Use parent pacs.008 parsing if available
        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = self._parse_standalone(raw_content)

        # Add MEPS+-specific fields
        result['isMepsPlus'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM

        return result

    def _parse_standalone(self, raw_content: str) -> Dict[str, Any]:
        """Standalone parsing when base class not available."""
        legacy_parser = MepsPlusParser()
        return legacy_parser.parse(raw_content)


# =============================================================================
# LEGACY JSON PARSER (kept for backward compatibility)
# =============================================================================


class MepsPlusParser:
    """Parser for Singapore MEPS+ JSON messages (legacy)."""

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse MEPS+ message content.

        Handles:
        1. Dict input (already parsed)
        2. JSON string input
        3. Returns empty dict with message type on parse failure
        """
        # Handle dict input (already parsed)
        if isinstance(raw_content, dict):
            return raw_content

        # Handle string input
        if isinstance(raw_content, str):
            content = raw_content.strip()

            # Try JSON parsing
            if content.startswith('{'):
                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse MEPS+ JSON: {e}")

        # Return minimal dict on failure
        return {'messageType': 'MEPS_PLUS'}


class MepsPlusExtractor(BaseExtractor):
    """Extractor for Singapore MEPS+ (MAS Electronic Payment System Plus) messages.

    ISO 20022 INHERITANCE:
        MEPS+ inherits from pacs.008 (FI to FI Customer Credit Transfer).
        The MepsPlusISO20022Parser inherits from Pacs008Parser.
        Uses MAS (Monetary Authority of Singapore) usage guidelines.

    Format Support:
        1. ISO 20022 XML (pacs.008.001.08) - Current standard
        2. JSON (legacy format)

    MEPS+-Specific Elements:
        - SGMEP clearing system (Singapore MEPS+)
        - SGD currency (Singapore Dollars)
        - Real-time gross settlement (RTGS)

    Database Tables:
        - Bronze: bronze.raw_payment_messages
        - Silver: silver.stg_meps_plus
        - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_meps_plus

    Inheritance Hierarchy:
        BaseExtractor -> MepsPlusExtractor
        (Parser: Pacs008Parser -> MepsPlusISO20022Parser)
    """

    MESSAGE_TYPE = "MEPS_PLUS"
    SILVER_TABLE = "stg_iso20022_pacs008"  # Shared ISO 20022 pacs.008 table
    DEFAULT_CURRENCY = "SGD"
    CLEARING_SYSTEM = "SGMEP"

    def __init__(self):
        """Initialize MEPS+ extractor with ISO 20022 parser."""
        self.iso20022_parser = MepsPlusISO20022Parser()
        self.legacy_parser = MepsPlusParser()
        self.parser = self.iso20022_parser

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw MEPS+ content."""
        msg_id = raw_content.get('messageId', '') or raw_content.get('transactionReference', '')
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
        """Extract all Silver layer fields from MEPS+ message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'MEPS_PLUS',
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': msg_content.get('settlementDate'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'SGD',

            # Bank BICs
            'sending_bank_bic': trunc(msg_content.get('sendingBankBic'), 11),
            'receiving_bank_bic': trunc(msg_content.get('receivingBankBic'), 11),

            # Transaction Details
            'transaction_reference': trunc(msg_content.get('transactionReference'), 35),

            # Debtor
            'debtor_name': trunc(msg_content.get('debtorName'), 140),
            'debtor_account': trunc(msg_content.get('debtorAccount'), 34),

            # Creditor
            'creditor_name': trunc(msg_content.get('creditorName'), 140),
            'creditor_account': trunc(msg_content.get('creditorAccount'), 34),

            # Purpose
            'purpose_code': trunc(msg_content.get('purposeCode'), 10),
            'remittance_info': msg_content.get('remittanceInfo'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'message_id', 'creation_date_time',
            'settlement_date', 'amount', 'currency',
            'sending_bank_bic', 'receiving_bank_bic', 'transaction_reference',
            'debtor_name', 'debtor_account',
            'creditor_name', 'creditor_account',
            'purpose_code', 'remittance_info',
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
        """Extract Gold layer entities from MEPS+ Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Debtor Party - uses Silver column names
        if silver_data.get('debtor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('debtor_name'),
                role="DEBTOR",
                party_type='UNKNOWN',
                country='SG',
            ))

        # Creditor Party
        if silver_data.get('creditor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('creditor_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='SG',
            ))

        # Debtor Account
        if silver_data.get('debtor_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('debtor_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'SGD',
            ))

        # Creditor Account
        if silver_data.get('creditor_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('creditor_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'SGD',
            ))

        # Sending Bank
        if silver_data.get('sending_bank_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                bic=silver_data.get('sending_bank_bic'),
                country='SG',
            ))

        # Receiving Bank
        if silver_data.get('receiving_bank_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                bic=silver_data.get('receiving_bank_bic'),
                country='SG',
            ))

        return entities


# Register the extractor with all aliases
ExtractorRegistry.register('MEPS_PLUS', MepsPlusExtractor())
ExtractorRegistry.register('meps_plus', MepsPlusExtractor())
ExtractorRegistry.register('MEPS+', MepsPlusExtractor())
ExtractorRegistry.register('MEPS', MepsPlusExtractor())  # Alias for NiFi filename pattern
