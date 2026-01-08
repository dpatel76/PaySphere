"""Hong Kong RTGS (CHATS) Extractor - ISO 20022 based.

ISO 20022 INHERITANCE HIERARCHY:
    RTGS_HK (Hong Kong CHATS) uses ISO 20022 pacs.008 message format.
    The RtgsHkISO20022Parser inherits from Pacs008Parser.

    BaseISO20022Parser
        └── Pacs008Parser (FI to FI Customer Credit Transfer - pacs.008.001.08)
            └── RtgsHkISO20022Parser (Hong Kong RTGS/CHATS guidelines)

RTGS_HK-SPECIFIC ELEMENTS:
    - Hong Kong Bank Clearing Codes (HKCLC clearing system)
    - HKD currency (Hong Kong Dollars)
    - Real-time gross settlement
    - Operated by Hong Kong Interbank Clearing Limited (HKICL)

CLEARING SYSTEM:
    - HKCLC (Hong Kong Clearing Code)
    - HKHKCLR (HKICL clearing identifier)

DATABASE TABLES:
    - Bronze: bronze.raw_payment_messages
    - Silver: silver.stg_rtgs_hk
    - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_rtgs_hk

MAPPING INHERITANCE:
    RTGS_HK -> pacs.008.base (COMPLETE)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import xml.etree.ElementTree as ET
import re
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
    logger.warning("ISO 20022 base classes not available - RTGS_HK will use standalone implementation")


# =============================================================================
# RTGS_HK ISO 20022 PARSER (inherits from Pacs008Parser)
# =============================================================================

# Use conditional inheritance pattern for backward compatibility
_RtgsHkParserBase = Pacs008Parser if ISO20022_BASE_AVAILABLE else object


class RtgsHkISO20022Parser(_RtgsHkParserBase):
    """RTGS_HK ISO 20022 pacs.008 parser with Hong Kong CHATS usage guidelines.

    Inherits from Pacs008Parser and adds RTGS_HK-specific processing:
    - Hong Kong Bank Clearing Code extraction (HKCLC scheme)
    - RTGS_HK-specific clearing system identification
    - HK address format handling

    ISO 20022 Version: pacs.008.001.08
    Usage Guidelines: Hong Kong RTGS/CHATS Service

    Inheritance Hierarchy:
        BaseISO20022Parser -> Pacs008Parser -> RtgsHkISO20022Parser
    """

    # RTGS_HK-specific constants
    CLEARING_SYSTEM = "HKCLC"  # Hong Kong Clearing Code
    DEFAULT_CURRENCY = "HKD"
    MESSAGE_TYPE = "RTGS_HK"

    def __init__(self):
        """Initialize RTGS_HK parser."""
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse RTGS_HK ISO 20022 pacs.008 message.

        Uses inherited pacs.008 parsing from Pacs008Parser and adds
        RTGS_HK-specific fields.
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

        # Add RTGS_HK-specific fields
        result['isRtgsHk'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM

        return result

    def _parse_standalone(self, raw_content: str) -> Dict[str, Any]:
        """Standalone parsing when base class not available."""
        legacy_parser = RtgsHkXmlParser()
        return legacy_parser.parse(raw_content)


# =============================================================================
# LEGACY XML PARSER (kept for backward compatibility)
# =============================================================================


class RtgsHkXmlParser:
    """Parser for RTGS_HK ISO 20022 XML messages (pacs.008 variant)."""

    NS_PATTERN = re.compile(r'\{[^}]+\}')

    def __init__(self):
        self.ns = {}

    def _strip_ns(self, tag: str) -> str:
        """Remove namespace from XML tag."""
        return self.NS_PATTERN.sub('', tag)

    def _find(self, element: ET.Element, path: str) -> Optional[ET.Element]:
        """Find element using local names (ignoring namespaces)."""
        if element is None:
            return None
        parts = path.split('/')
        current = element
        for part in parts:
            found = None
            for child in current:
                if self._strip_ns(child.tag) == part:
                    found = child
                    break
            if found is None:
                return None
            current = found
        return current

    def _find_text(self, element: ET.Element, path: str) -> Optional[str]:
        """Find element text using local names."""
        elem = self._find(element, path)
        return elem.text if elem is not None else None

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse RTGS_HK message content."""
        # Handle JSON input
        if isinstance(raw_content, dict):
            return raw_content

        if isinstance(raw_content, str) and raw_content.strip().startswith('{'):
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError:
                pass

        # Parse XML
        try:
            if raw_content.startswith('\ufeff'):
                raw_content = raw_content[1:]
            root = ET.fromstring(raw_content)
        except ET.ParseError as e:
            logger.error(f"Failed to parse RTGS_HK XML: {e}")
            raise ValueError(f"Invalid XML: {e}")

        return self._parse_pacs008(root)

    def _parse_pacs008(self, root: ET.Element) -> Dict[str, Any]:
        """Parse RTGS_HK pacs.008 structure."""
        result = {'isRtgsHk': True, 'messageType': 'RTGS_HK'}

        # Find FIToFICstmrCdtTrf
        fi_transfer = self._find(root, 'FIToFICstmrCdtTrf')
        if fi_transfer is None:
            if self._strip_ns(root.tag) == 'FIToFICstmrCdtTrf':
                fi_transfer = root
            else:
                for child in root:
                    if self._strip_ns(child.tag) == 'FIToFICstmrCdtTrf':
                        fi_transfer = child
                        break

        if fi_transfer is None:
            return result

        # Group Header
        grp_hdr = self._find(fi_transfer, 'GrpHdr')
        if grp_hdr is not None:
            result['messageId'] = self._find_text(grp_hdr, 'MsgId')
            result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')

            sttlm_inf = self._find(grp_hdr, 'SttlmInf')
            if sttlm_inf is not None:
                result['settlementMethod'] = self._find_text(sttlm_inf, 'SttlmMtd')
                result['settlementCurrency'] = self._find_text(sttlm_inf, 'SttlmAcct/Ccy') or 'HKD'

            # Instructing/Instructed Agents
            result['sendingBankCode'] = self._find_text(grp_hdr, 'InstgAgt/FinInstnId/ClrSysMmbId/MmbId')
            result['receivingBankCode'] = self._find_text(grp_hdr, 'InstdAgt/FinInstnId/ClrSysMmbId/MmbId')

        # Credit Transfer Transaction Info
        cdt_trf = self._find(fi_transfer, 'CdtTrfTxInf')
        if cdt_trf is not None:
            result.update(self._parse_transaction(cdt_trf))

        return result

    def _parse_transaction(self, tx: ET.Element) -> Dict[str, Any]:
        """Parse credit transfer transaction."""
        result = {}

        # Payment ID
        pmt_id = self._find(tx, 'PmtId')
        if pmt_id is not None:
            result['transactionReference'] = self._find_text(pmt_id, 'InstrId') or self._find_text(pmt_id, 'EndToEndId')
            result['endToEndId'] = self._find_text(pmt_id, 'EndToEndId')
            result['transactionId'] = self._find_text(pmt_id, 'TxId')

        # Settlement Amount
        result['amount'] = self._safe_decimal(self._find_text(tx, 'IntrBkSttlmAmt'))
        result['currency'] = self._find_attr(tx, 'IntrBkSttlmAmt', 'Ccy') or 'HKD'
        result['settlementDate'] = self._find_text(tx, 'IntrBkSttlmDt')

        # Debtor (Payer)
        dbtr = self._find(tx, 'Dbtr')
        if dbtr is not None:
            result['payerName'] = self._find_text(dbtr, 'Nm')

        dbtr_acct = self._find(tx, 'DbtrAcct')
        if dbtr_acct is not None:
            result['payerAccount'] = self._find_text(dbtr_acct, 'Id/Othr/Id') or self._find_text(dbtr_acct, 'Id/IBAN')

        dbtr_agt = self._find(tx, 'DbtrAgt')
        if dbtr_agt is not None:
            result['sendingBankCode'] = result.get('sendingBankCode') or self._find_text(dbtr_agt, 'FinInstnId/ClrSysMmbId/MmbId')

        # Creditor (Payee)
        cdtr = self._find(tx, 'Cdtr')
        if cdtr is not None:
            result['payeeName'] = self._find_text(cdtr, 'Nm')

        cdtr_acct = self._find(tx, 'CdtrAcct')
        if cdtr_acct is not None:
            result['payeeAccount'] = self._find_text(cdtr_acct, 'Id/Othr/Id') or self._find_text(cdtr_acct, 'Id/IBAN')

        cdtr_agt = self._find(tx, 'CdtrAgt')
        if cdtr_agt is not None:
            result['receivingBankCode'] = result.get('receivingBankCode') or self._find_text(cdtr_agt, 'FinInstnId/ClrSysMmbId/MmbId')

        # Purpose & Remittance
        result['purpose'] = self._find_text(tx, 'Purp/Cd') or self._find_text(tx, 'RmtInf/Ustrd')

        return result

    def _find_attr(self, element: ET.Element, path: str, attr: str) -> Optional[str]:
        """Find element attribute."""
        elem = self._find(element, path)
        return elem.get(attr) if elem is not None else None

    def _safe_decimal(self, value: Optional[str]) -> Optional[float]:
        """Safely convert string to decimal."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


# =============================================================================
# LEGACY JSON PARSER (kept for backward compatibility)
# =============================================================================


class RtgsHkParser:
    """Parser for Hong Kong RTGS (CHATS) JSON messages.

    Legacy parser for JSON input format. For ISO 20022 XML, use RtgsHkISO20022Parser.
    """

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse RTGS_HK message content.

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
                    logger.warning(f"Failed to parse RTGS_HK JSON: {e}")

        # Return minimal dict on failure
        return {'messageType': 'RTGS_HK'}


class RtgsHkExtractor(BaseExtractor):
    """Extractor for Hong Kong RTGS (CHATS) payment messages.

    ISO 20022 INHERITANCE:
        RTGS_HK inherits from pacs.008 (FI to FI Customer Credit Transfer).
        The RtgsHkISO20022Parser inherits from Pacs008Parser.
        Uses Hong Kong RTGS/CHATS service guidelines.

    Format Support:
        1. ISO 20022 XML (pacs.008.001.08) - Current standard
        2. JSON format - Legacy support

    RTGS_HK-Specific Elements:
        - Hong Kong Bank Clearing Codes (HKCLC clearing system)
        - HKD currency (Hong Kong Dollars)
        - Real-time gross settlement
        - Operated by HKICL

    Database Tables:
        - Bronze: bronze.raw_payment_messages
        - Silver: silver.stg_rtgs_hk
        - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_rtgs_hk

    Inheritance Hierarchy:
        BaseExtractor -> RtgsHkExtractor
        (Parser: Pacs008Parser -> RtgsHkISO20022Parser)
    """

    MESSAGE_TYPE = "RTGS_HK"
    SILVER_TABLE = "stg_iso20022_pacs008"  # Shared ISO 20022 pacs.008 table
    DEFAULT_CURRENCY = "HKD"
    CLEARING_SYSTEM = "HKCLC"

    def __init__(self):
        """Initialize RTGS_HK extractor with ISO 20022 parser."""
        self.iso20022_parser = RtgsHkISO20022Parser()
        self.legacy_parser = RtgsHkParser()
        self.parser = self.iso20022_parser

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw RTGS_HK content."""
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
        """Extract all Silver layer fields from RTGS_HK message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'RTGS_HK',
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': msg_content.get('settlementDate'),
            'settlement_currency': msg_content.get('settlementCurrency') or 'HKD',

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'HKD',

            # Bank Codes
            'sending_bank_code': trunc(msg_content.get('sendingBankCode'), 11),
            'receiving_bank_code': trunc(msg_content.get('receivingBankCode'), 11),

            # Transaction Details
            'transaction_reference': trunc(msg_content.get('transactionReference'), 35),

            # Payer (Debtor)
            'payer_name': trunc(msg_content.get('payerName'), 140),
            'payer_account': trunc(msg_content.get('payerAccount'), 34),

            # Payee (Creditor)
            'payee_name': trunc(msg_content.get('payeeName'), 140),
            'payee_account': trunc(msg_content.get('payeeAccount'), 34),

            # Purpose
            'purpose': msg_content.get('purpose'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'message_id', 'creation_date_time',
            'settlement_date', 'settlement_currency', 'amount', 'currency',
            'sending_bank_code', 'receiving_bank_code', 'transaction_reference',
            'payer_name', 'payer_account',
            'payee_name', 'payee_account',
            'purpose',
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
        """Extract Gold layer entities from RTGS_HK Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Payer Party (Debtor) - uses Silver column names
        if silver_data.get('payer_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payer_name'),
                role="DEBTOR",
                party_type='UNKNOWN',
                country='HK',
            ))

        # Payee Party (Creditor)
        if silver_data.get('payee_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='HK',
            ))

        # Payer Account
        if silver_data.get('payer_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payer_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'HKD',
            ))

        # Payee Account
        if silver_data.get('payee_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payee_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'HKD',
            ))

        # Sending Bank
        if silver_data.get('sending_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=silver_data.get('sending_bank_code'),
                clearing_system='HKHKCLR',  # HKICL clearing
                country='HK',
            ))

        # Receiving Bank
        if silver_data.get('receiving_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=silver_data.get('receiving_bank_code'),
                clearing_system='HKHKCLR',
                country='HK',
            ))

        return entities


# Register the extractor with all aliases
ExtractorRegistry.register('RTGS_HK', RtgsHkExtractor())
ExtractorRegistry.register('rtgs_hk', RtgsHkExtractor())
ExtractorRegistry.register('CHATS', RtgsHkExtractor())
ExtractorRegistry.register('RTGS', RtgsHkExtractor())  # Alias for NiFi filename pattern
