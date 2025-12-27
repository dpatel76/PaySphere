"""FedNow (Federal Reserve Instant Payments) Extractor - ISO 20022 based."""

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


class FedNowXmlParser:
    """Parser for FedNow ISO 20022 XML messages (pacs.008 variant)."""

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
        """Parse FedNow message content."""
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
            logger.error(f"Failed to parse FedNow XML: {e}")
            raise ValueError(f"Invalid XML: {e}")

        return self._parse_pacs008(root)

    def _parse_pacs008(self, root: ET.Element) -> Dict[str, Any]:
        """Parse FedNow pacs.008 structure."""
        result = {'isFedNow': True}

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

            # Instructing/Instructed Agents
            result['instructingAgentRouting'] = self._find_text(grp_hdr, 'InstgAgt/FinInstnId/ClrSysMmbId/MmbId')
            result['instructedAgentRouting'] = self._find_text(grp_hdr, 'InstdAgt/FinInstnId/ClrSysMmbId/MmbId')

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
            result['instructionId'] = self._find_text(pmt_id, 'InstrId')
            result['endToEndId'] = self._find_text(pmt_id, 'EndToEndId')
            result['transactionId'] = self._find_text(pmt_id, 'TxId')
            result['uetr'] = self._find_text(pmt_id, 'UETR')

        # Settlement Amount
        result['interbankSettlementAmount'] = self._safe_decimal(self._find_text(tx, 'IntrBkSttlmAmt'))
        result['interbankSettlementCurrency'] = self._find_attr(tx, 'IntrBkSttlmAmt', 'Ccy') or 'USD'
        result['interbankSettlementDate'] = self._find_text(tx, 'IntrBkSttlmDt')

        # Debtor
        dbtr = self._find(tx, 'Dbtr')
        if dbtr is not None:
            result['debtorName'] = self._find_text(dbtr, 'Nm')

        dbtr_acct = self._find(tx, 'DbtrAcct')
        if dbtr_acct is not None:
            result['debtorAccount'] = self._find_text(dbtr_acct, 'Id/Othr/Id')

        dbtr_agt = self._find(tx, 'DbtrAgt')
        if dbtr_agt is not None:
            result['debtorAgentRouting'] = self._find_text(dbtr_agt, 'FinInstnId/ClrSysMmbId/MmbId')

        # Creditor
        cdtr = self._find(tx, 'Cdtr')
        if cdtr is not None:
            result['creditorName'] = self._find_text(cdtr, 'Nm')

        cdtr_acct = self._find(tx, 'CdtrAcct')
        if cdtr_acct is not None:
            result['creditorAccount'] = self._find_text(cdtr_acct, 'Id/Othr/Id')

        cdtr_agt = self._find(tx, 'CdtrAgt')
        if cdtr_agt is not None:
            result['creditorAgentRouting'] = self._find_text(cdtr_agt, 'FinInstnId/ClrSysMmbId/MmbId')

        # Purpose & Remittance
        result['purposeCode'] = self._find_text(tx, 'Purp/Cd')
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


class FedNowExtractor(BaseExtractor):
    """Extractor for FedNow instant payment messages."""

    MESSAGE_TYPE = "FEDNOW"
    SILVER_TABLE = "stg_fednow"

    def __init__(self):
        self.parser = FedNowXmlParser()

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw FedNow content."""
        msg_id = raw_content.get('messageId', '') or raw_content.get('transactionId', '')
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
        """Extract all Silver layer fields from FedNow message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Header
            'message_type': 'FEDNOW',
            'msg_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_method': trunc(msg_content.get('settlementMethod'), 10),
            'interbank_settlement_date': msg_content.get('interbankSettlementDate'),
            'interbank_settlement_amount': msg_content.get('interbankSettlementAmount'),
            'interbank_settlement_currency': msg_content.get('interbankSettlementCurrency') or 'USD',

            # Agents
            'instructing_agent_routing': trunc(msg_content.get('instructingAgentRouting'), 9),
            'instructed_agent_routing': trunc(msg_content.get('instructedAgentRouting'), 9),

            # Payment IDs
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'transaction_id': trunc(msg_content.get('transactionId'), 35),
            'uetr': msg_content.get('uetr'),

            # Debtor
            'debtor_name': trunc(msg_content.get('debtorName'), 140),
            'debtor_account': trunc(msg_content.get('debtorAccount'), 34),
            'debtor_agent_routing': trunc(msg_content.get('debtorAgentRouting'), 9),

            # Creditor
            'creditor_name': trunc(msg_content.get('creditorName'), 140),
            'creditor_account': trunc(msg_content.get('creditorAccount'), 34),
            'creditor_agent_routing': trunc(msg_content.get('creditorAgentRouting'), 9),

            # Purpose & Remittance
            'purpose_code': trunc(msg_content.get('purposeCode'), 4),
            'remittance_info': msg_content.get('remittanceInfo'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'msg_id', 'creation_date_time',
            'settlement_method', 'interbank_settlement_date',
            'interbank_settlement_amount', 'interbank_settlement_currency',
            'instructing_agent_routing', 'instructed_agent_routing',
            'instruction_id', 'end_to_end_id', 'transaction_id', 'uetr',
            'debtor_name', 'debtor_account', 'debtor_agent_routing',
            'creditor_name', 'creditor_account', 'creditor_agent_routing',
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
        msg_content: Dict[str, Any],
        stg_id: str,
        batch_id: str
    ) -> GoldEntities:
        """Extract Gold layer entities from FedNow message."""
        entities = GoldEntities()

        # Debtor Party
        if msg_content.get('debtorName'):
            entities.parties.append(PartyData(
                name=msg_content.get('debtorName'),
                role="DEBTOR",
                party_type='UNKNOWN',
            ))

        # Creditor Party
        if msg_content.get('creditorName'):
            entities.parties.append(PartyData(
                name=msg_content.get('creditorName'),
                role="CREDITOR",
                party_type='UNKNOWN',
            ))

        # Debtor Account
        if msg_content.get('debtorAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('debtorAccount'),
                role="DEBTOR",
                account_type='CACC',
                currency='USD',
            ))

        # Creditor Account
        if msg_content.get('creditorAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('creditorAccount'),
                role="CREDITOR",
                account_type='CACC',
                currency='USD',
            ))

        # Debtor Agent
        if msg_content.get('debtorAgentRouting'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=msg_content.get('debtorAgentRouting'),
                clearing_system='FEDNOW',
                country='US',
            ))

        # Creditor Agent
        if msg_content.get('creditorAgentRouting'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=msg_content.get('creditorAgentRouting'),
                clearing_system='FEDNOW',
                country='US',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('FEDNOW', FedNowExtractor())
ExtractorRegistry.register('fednow', FedNowExtractor())
ExtractorRegistry.register('FedNow', FedNowExtractor())
