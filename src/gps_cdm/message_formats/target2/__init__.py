"""Eurozone TARGET2 (Trans-European Automated Real-time Gross Settlement Express Transfer) Extractor - ISO 20022 based."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging
import re
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


class Target2XmlParser:
    """Parser for TARGET2 ISO 20022 pacs.009 XML messages."""

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

    def _find_attr(self, element: ET.Element, path: str, attr: str) -> Optional[str]:
        """Find element attribute."""
        elem = self._find(element, path)
        return elem.get(attr) if elem is not None else None

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse TARGET2 message content."""
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
            logger.error(f"Failed to parse TARGET2 XML: {e}")
            raise ValueError(f"Invalid XML: {e}")

        return self._parse_pacs009(root)

    def _parse_pacs009(self, root: ET.Element) -> Dict[str, Any]:
        """Parse TARGET2 pacs.009 FI Credit Transfer structure."""
        result = {'isTarget2': True}

        # Find FICdtTrf (Financial Institution Credit Transfer)
        fi_transfer = self._find(root, 'FICdtTrf')
        if fi_transfer is None:
            if self._strip_ns(root.tag) == 'FICdtTrf':
                fi_transfer = root

        if fi_transfer is None:
            logger.warning("Cannot find FICdtTrf element in TARGET2 message")
            return result

        # Group Header
        grp_hdr = self._find(fi_transfer, 'GrpHdr')
        if grp_hdr is not None:
            result['msgId'] = self._find_text(grp_hdr, 'MsgId')
            result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')
            result['settlementDate'] = self._find_text(grp_hdr, 'IntrBkSttlmDt')
            result['settlementMethod'] = self._find_text(grp_hdr, 'SttlmInf/SttlmMtd')

            # Amount from header
            amt_elem = self._find(grp_hdr, 'TtlIntrBkSttlmAmt')
            if amt_elem is not None:
                result['amount'] = amt_elem.text
                result['currency'] = amt_elem.get('Ccy', 'EUR')

            # Instructing Agent
            result['instructingAgentBic'] = self._find_text(grp_hdr, 'InstgAgt/FinInstnId/BICFI')
            result['instructingAgentName'] = self._find_text(grp_hdr, 'InstgAgt/FinInstnId/Nm')

            # Instructed Agent
            result['instructedAgentBic'] = self._find_text(grp_hdr, 'InstdAgt/FinInstnId/BICFI')
            result['instructedAgentName'] = self._find_text(grp_hdr, 'InstdAgt/FinInstnId/Nm')

        # Credit Transfer Transaction Info
        cdt_trf = self._find(fi_transfer, 'CdtTrfTxInf')
        if cdt_trf is not None:
            result.update(self._parse_transaction(cdt_trf))

        return result

    def _parse_transaction(self, cdt_trf: ET.Element) -> Dict[str, Any]:
        """Parse CdtTrfTxInf element."""
        result = {}

        # Payment IDs
        pmt_id = self._find(cdt_trf, 'PmtId')
        if pmt_id is not None:
            result['instructionId'] = self._find_text(pmt_id, 'InstrId')
            result['endToEndId'] = self._find_text(pmt_id, 'EndToEndId')
            result['transactionId'] = self._find_text(pmt_id, 'TxId')
            result['uetr'] = self._find_text(pmt_id, 'UETR')

        # Payment Type Info
        pmt_tp = self._find(cdt_trf, 'PmtTpInf')
        if pmt_tp is not None:
            result['paymentType'] = self._find_text(pmt_tp, 'InstrPrty')
            result['serviceLevel'] = self._find_text(pmt_tp, 'SvcLvl/Cd')

        # Amount from transaction
        amt_elem = self._find(cdt_trf, 'IntrBkSttlmAmt')
        if amt_elem is not None:
            result['amount'] = amt_elem.text
            result['currency'] = amt_elem.get('Ccy', 'EUR')

        # Debtor (for pacs.009, Debtor is usually a FinInstnId)
        debtor = self._find(cdt_trf, 'Dbtr')
        if debtor is not None:
            result['debtorName'] = self._find_text(debtor, 'FinInstnId/Nm') or self._find_text(debtor, 'Nm')
            result['debtorBic'] = self._find_text(debtor, 'FinInstnId/BICFI')

        # Debtor Account
        dbtr_acct = self._find(cdt_trf, 'DbtrAcct')
        if dbtr_acct is not None:
            result['debtorAccount'] = (
                self._find_text(dbtr_acct, 'Id/IBAN') or
                self._find_text(dbtr_acct, 'Id/Othr/Id')
            )

        # Debtor Agent
        dbtr_agt = self._find(cdt_trf, 'DbtrAgt')
        if dbtr_agt is not None:
            result['debtorAgentBic'] = self._find_text(dbtr_agt, 'FinInstnId/BICFI')
            result['debtorAgentName'] = self._find_text(dbtr_agt, 'FinInstnId/Nm')

        # Creditor (for pacs.009, Creditor is usually a FinInstnId)
        creditor = self._find(cdt_trf, 'Cdtr')
        if creditor is not None:
            result['creditorName'] = self._find_text(creditor, 'FinInstnId/Nm') or self._find_text(creditor, 'Nm')
            result['creditorBic'] = self._find_text(creditor, 'FinInstnId/BICFI')

        # Creditor Account
        cdtr_acct = self._find(cdt_trf, 'CdtrAcct')
        if cdtr_acct is not None:
            result['creditorAccount'] = (
                self._find_text(cdtr_acct, 'Id/IBAN') or
                self._find_text(cdtr_acct, 'Id/Othr/Id')
            )

        # Creditor Agent
        cdtr_agt = self._find(cdt_trf, 'CdtrAgt')
        if cdtr_agt is not None:
            result['creditorAgentBic'] = self._find_text(cdtr_agt, 'FinInstnId/BICFI')
            result['creditorAgentName'] = self._find_text(cdtr_agt, 'FinInstnId/Nm')

        return result


class Target2Extractor(BaseExtractor):
    """Extractor for Eurozone TARGET2 payment messages."""

    MESSAGE_TYPE = "TARGET2"
    SILVER_TABLE = "stg_target2"

    def __init__(self):
        super().__init__()
        self.parser = Target2XmlParser()

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw TARGET2 content."""
        msg_id = raw_content.get('msgId', '') or raw_content.get('endToEndId', '')
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
        """Extract all Silver layer fields from TARGET2 message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'TARGET2',
            'msg_id': trunc(msg_content.get('msgId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': msg_content.get('settlementDate'),
            'settlement_method': trunc(msg_content.get('settlementMethod'), 10),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'EUR',

            # Agents (BICs)
            'instructing_agent_bic': trunc(msg_content.get('instructingAgentBic'), 11),
            'instructed_agent_bic': trunc(msg_content.get('instructedAgentBic'), 11),
            'debtor_agent_bic': trunc(msg_content.get('debtorAgentBic'), 11),
            'creditor_agent_bic': trunc(msg_content.get('creditorAgentBic'), 11),

            # Transaction IDs
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'transaction_id': trunc(msg_content.get('transactionId'), 35),
            'uetr': msg_content.get('uetr'),

            # Debtor
            'debtor_name': trunc(msg_content.get('debtorName'), 140),
            'debtor_account': trunc(msg_content.get('debtorAccount'), 34),

            # Creditor
            'creditor_name': trunc(msg_content.get('creditorName'), 140),
            'creditor_account': trunc(msg_content.get('creditorAccount'), 34),

            # Payment Type
            'payment_type': trunc(msg_content.get('paymentType'), 10),
            'service_level': trunc(msg_content.get('serviceLevel'), 35),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'msg_id', 'creation_date_time',
            'settlement_date', 'settlement_method', 'amount', 'currency',
            'instructing_agent_bic', 'instructed_agent_bic',
            'debtor_agent_bic', 'creditor_agent_bic',
            'instruction_id', 'end_to_end_id', 'transaction_id', 'uetr',
            'debtor_name', 'debtor_account',
            'creditor_name', 'creditor_account',
            'payment_type', 'service_level',
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
        """Extract Gold layer entities from TARGET2 Silver record.

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
            ))

        # Creditor Party
        if silver_data.get('creditor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('creditor_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
            ))

        # Debtor Account
        if silver_data.get('debtor_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('debtor_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'EUR',
            ))

        # Creditor Account
        if silver_data.get('creditor_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('creditor_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'EUR',
            ))

        # Debtor Agent
        if silver_data.get('debtor_agent_bic') or silver_data.get('instructing_agent_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                bic=silver_data.get('debtor_agent_bic') or silver_data.get('instructing_agent_bic'),
                clearing_system='TARGET2',
            ))

        # Creditor Agent
        if silver_data.get('creditor_agent_bic') or silver_data.get('instructed_agent_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                bic=silver_data.get('creditor_agent_bic') or silver_data.get('instructed_agent_bic'),
                clearing_system='TARGET2',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('TARGET2', Target2Extractor())
ExtractorRegistry.register('target2', Target2Extractor())
