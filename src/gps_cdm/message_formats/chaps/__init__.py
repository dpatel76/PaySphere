"""CHAPS (Clearing House Automated Payment System) Extractor - UK Real-Time Gross Settlement."""

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


class ChapsXmlParser:
    """Parser for CHAPS ISO 20022 XML messages."""

    NS_PATTERN = re.compile(r'\{[^}]+\}')

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
        """Parse CHAPS message content."""
        # Handle JSON input
        if isinstance(raw_content, dict):
            return raw_content

        if raw_content.strip().startswith('{'):
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
            logger.error(f"Failed to parse CHAPS XML: {e}")
            raise ValueError(f"Invalid XML: {e}")

        return self._parse_iso20022(root)

    def _parse_iso20022(self, root: ET.Element) -> Dict[str, Any]:
        """Parse CHAPS ISO 20022 structure."""
        result = {'isChaps': True}

        fi_transfer = self._find(root, 'FIToFICstmrCdtTrf')
        if fi_transfer is None:
            if self._strip_ns(root.tag) == 'FIToFICstmrCdtTrf':
                fi_transfer = root

        if fi_transfer is None:
            return result

        # Group Header
        grp_hdr = self._find(fi_transfer, 'GrpHdr')
        if grp_hdr is not None:
            result['messageId'] = self._find_text(grp_hdr, 'MsgId')
            result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')
            result['settlementMethod'] = self._find_text(grp_hdr, 'SttlmInf/SttlmMtd')
            result['settlementDate'] = self._find_text(grp_hdr, 'IntrBkSttlmDt')

        # Credit Transfer Transaction
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
            result['instructionId'] = self._find_text(pmt_id, 'InstrId')
            result['endToEndId'] = self._find_text(pmt_id, 'EndToEndId')
            result['uetr'] = self._find_text(pmt_id, 'UETR')

        # Amount
        result['amount'] = self._safe_decimal(self._find_text(tx, 'IntrBkSttlmAmt'))
        result['currency'] = self._find_attr(tx, 'IntrBkSttlmAmt', 'Ccy') or 'GBP'

        # Debtor
        dbtr = self._find(tx, 'Dbtr')
        if dbtr is not None:
            result['debtorName'] = self._find_text(dbtr, 'Nm')
            result['debtorAddress'] = self._find_text(dbtr, 'PstlAdr/AdrLine')

        dbtr_acct = self._find(tx, 'DbtrAcct')
        if dbtr_acct is not None:
            result['debtorAccount'] = self._find_text(dbtr_acct, 'Id/Othr/Id')
            result['debtorSortCode'] = self._find_text(dbtr_acct, 'Id/Othr/SchmeNm/Cd')

        dbtr_agt = self._find(tx, 'DbtrAgt')
        if dbtr_agt is not None:
            result['debtorAgentBic'] = self._find_text(dbtr_agt, 'FinInstnId/BICFI')
            result['debtorSortCode'] = result.get('debtorSortCode') or self._find_text(dbtr_agt, 'FinInstnId/ClrSysMmbId/MmbId')

        # Creditor
        cdtr = self._find(tx, 'Cdtr')
        if cdtr is not None:
            result['creditorName'] = self._find_text(cdtr, 'Nm')
            result['creditorAddress'] = self._find_text(cdtr, 'PstlAdr/AdrLine')

        cdtr_acct = self._find(tx, 'CdtrAcct')
        if cdtr_acct is not None:
            result['creditorAccount'] = self._find_text(cdtr_acct, 'Id/Othr/Id')
            result['creditorSortCode'] = self._find_text(cdtr_acct, 'Id/Othr/SchmeNm/Cd')

        cdtr_agt = self._find(tx, 'CdtrAgt')
        if cdtr_agt is not None:
            result['creditorAgentBic'] = self._find_text(cdtr_agt, 'FinInstnId/BICFI')
            result['creditorSortCode'] = result.get('creditorSortCode') or self._find_text(cdtr_agt, 'FinInstnId/ClrSysMmbId/MmbId')

        # Remittance Info
        result['remittanceInfo'] = self._find_text(tx, 'RmtInf/Ustrd')

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


class ChapsExtractor(BaseExtractor):
    """Extractor for CHAPS payment messages."""

    MESSAGE_TYPE = "CHAPS"
    SILVER_TABLE = "stg_chaps"

    def __init__(self):
        self.parser = ChapsXmlParser()

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw CHAPS content."""
        msg_id = raw_content.get('messageId', '') or raw_content.get('instructionId', '')
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
        """Extract all Silver layer fields from CHAPS message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Header
            'message_type': 'CHAPS',
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': msg_content.get('settlementDate'),
            'settlement_method': trunc(msg_content.get('settlementMethod'), 10),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'GBP',

            # Debtor
            'debtor_name': trunc(msg_content.get('debtorName'), 140),
            'debtor_address': msg_content.get('debtorAddress'),
            'debtor_sort_code': trunc(msg_content.get('debtorSortCode'), 6),
            'debtor_account': trunc(msg_content.get('debtorAccount'), 34),
            'debtor_agent_bic': trunc(msg_content.get('debtorAgentBic'), 11),

            # Creditor
            'creditor_name': trunc(msg_content.get('creditorName'), 140),
            'creditor_address': msg_content.get('creditorAddress'),
            'creditor_sort_code': trunc(msg_content.get('creditorSortCode'), 6),
            'creditor_account': trunc(msg_content.get('creditorAccount'), 34),
            'creditor_agent_bic': trunc(msg_content.get('creditorAgentBic'), 11),

            # Payment IDs
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'uetr': msg_content.get('uetr'),

            # Remittance
            'remittance_info': msg_content.get('remittanceInfo'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'message_id', 'creation_date_time',
            'settlement_date', 'settlement_method',
            'amount', 'currency',
            'debtor_name', 'debtor_address', 'debtor_sort_code',
            'debtor_account', 'debtor_agent_bic',
            'creditor_name', 'creditor_address', 'creditor_sort_code',
            'creditor_account', 'creditor_agent_bic',
            'instruction_id', 'end_to_end_id', 'uetr',
            'remittance_info',
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
        msg_content: Dict[str, Any],
        stg_id: str,
        batch_id: str
    ) -> GoldEntities:
        """Extract Gold layer entities from CHAPS message."""
        entities = GoldEntities()

        # Debtor Party
        if msg_content.get('debtorName'):
            entities.parties.append(PartyData(
                name=msg_content.get('debtorName'),
                role="DEBTOR",
                party_type='UNKNOWN',
                country='GB',
            ))

        # Creditor Party
        if msg_content.get('creditorName'):
            entities.parties.append(PartyData(
                name=msg_content.get('creditorName'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='GB',
            ))

        # Debtor Account
        if msg_content.get('debtorAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('debtorAccount'),
                role="DEBTOR",
                account_type='CACC',
                currency='GBP',
            ))

        # Creditor Account
        if msg_content.get('creditorAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('creditorAccount'),
                role="CREDITOR",
                account_type='CACC',
                currency='GBP',
            ))

        # Debtor Agent
        if msg_content.get('debtorAgentBic') or msg_content.get('debtorSortCode'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                bic=msg_content.get('debtorAgentBic'),
                clearing_code=msg_content.get('debtorSortCode'),
                clearing_system='GBDSC',  # UK Domestic Sort Code
                country='GB',
            ))

        # Creditor Agent
        if msg_content.get('creditorAgentBic') or msg_content.get('creditorSortCode'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                bic=msg_content.get('creditorAgentBic'),
                clearing_code=msg_content.get('creditorSortCode'),
                clearing_system='GBDSC',
                country='GB',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('CHAPS', ChapsExtractor())
ExtractorRegistry.register('chaps', ChapsExtractor())
