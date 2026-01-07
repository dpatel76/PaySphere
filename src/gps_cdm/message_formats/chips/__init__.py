"""CHIPS (Clearing House Interbank Payments System) Extractor.

IMPORTANT: As of November 2023, CHIPS migrated to ISO 20022 messaging.
The legacy CHIPS proprietary format is deprecated.

Current CHIPS ISO 20022 messages:
- pacs.008.001.08: FI to FI Customer Credit Transfer
- pacs.009.001.08: FI Credit Transfer (interbank)
- pacs.004.001.09: Payment Return
- pacs.002.001.10: Payment Status Report

This extractor supports BOTH formats for backward compatibility:
1. ISO 20022 XML (pacs.008/pacs.009) - Current standard as of November 2023
2. Legacy CHIPS proprietary XML format - For historical data processing

Reference: https://www.theclearinghouse.org/payment-systems/chips
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


class ChipsISO20022Parser:
    """Parser for CHIPS ISO 20022 pacs.008/pacs.009 messages (current standard as of November 2023).

    CHIPS uses standard ISO 20022 messages aligned with CBPR+ (Cross-Border Payments and Reporting Plus).
    Key message types:
    - pacs.008: FI to FI Customer Credit Transfer
    - pacs.009: FI Credit Transfer (interbank)
    """

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

    def parse(self, xml_content: str) -> Dict[str, Any]:
        """Parse CHIPS ISO 20022 pacs.008 or pacs.009 message."""
        try:
            if xml_content.startswith('\ufeff'):
                xml_content = xml_content[1:]
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.error(f"Failed to parse CHIPS ISO 20022 XML: {e}")
            raise ValueError(f"Invalid XML: {e}")

        # Determine message type (pacs.008 or pacs.009)
        fi_transfer = self._find(root, 'FIToFICstmrCdtTrf')  # pacs.008
        if fi_transfer is None:
            fi_transfer = self._find(root, 'FICdtTrf')  # pacs.009
            if fi_transfer is None:
                root_tag = self._strip_ns(root.tag)
                if root_tag == 'FIToFICstmrCdtTrf':
                    fi_transfer = root
                elif root_tag == 'FICdtTrf':
                    fi_transfer = root

        if fi_transfer is None:
            raise ValueError("Cannot find FIToFICstmrCdtTrf or FICdtTrf element")

        return self._parse_transfer(fi_transfer)

    def _parse_transfer(self, fi_transfer: ET.Element) -> Dict[str, Any]:
        """Parse credit transfer element."""
        result = {
            'messageType': 'CHIPS',
            'currency': 'USD',  # CHIPS is primarily USD
            'isISO20022': True,
        }

        # Group Header
        grp_hdr = self._find(fi_transfer, 'GrpHdr')
        if grp_hdr is not None:
            result['messageId'] = self._find_text(grp_hdr, 'MsgId')
            result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')
            result['numberOfTransactions'] = self._find_text(grp_hdr, 'NbOfTxs')
            result['settlementMethod'] = self._find_text(grp_hdr, 'SttlmInf/SttlmMtd')

            # Value/Settlement Date
            value_date = self._find_text(grp_hdr, 'IntrBkSttlmDt')
            result['valueDate'] = value_date

            # Instructing Agent (Sending Bank)
            instg_agt = self._find(grp_hdr, 'InstgAgt/FinInstnId')
            if instg_agt is not None:
                result['sendingParticipant'] = self._find_text(instg_agt, 'ClrSysMmbId/MmbId')
                result['sendingBankBic'] = self._find_text(instg_agt, 'BICFI')
                result['sendingBankName'] = self._find_text(instg_agt, 'Nm')
                result['sendingBankLei'] = self._find_text(instg_agt, 'LEI')
                result['sendingBankAba'] = self._find_text(instg_agt, 'ClrSysMmbId/MmbId')

            # Instructed Agent (Receiving Bank)
            instd_agt = self._find(grp_hdr, 'InstdAgt/FinInstnId')
            if instd_agt is not None:
                result['receivingParticipant'] = self._find_text(instd_agt, 'ClrSysMmbId/MmbId')
                result['receivingBankBic'] = self._find_text(instd_agt, 'BICFI')
                result['receivingBankName'] = self._find_text(instd_agt, 'Nm')
                result['receivingBankLei'] = self._find_text(instd_agt, 'LEI')
                result['receivingBankAba'] = self._find_text(instd_agt, 'ClrSysMmbId/MmbId')

        # Credit Transfer Transaction Information
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
            result['sequenceNumber'] = self._find_text(pmt_id, 'InstrId')
            result['senderReference'] = self._find_text(pmt_id, 'EndToEndId')
            result['relatedReference'] = self._find_text(pmt_id, 'TxId')
            result['uetr'] = self._find_text(pmt_id, 'UETR')

        # Amount
        amt_elem = self._find(cdt_trf, 'IntrBkSttlmAmt')
        if amt_elem is not None:
            try:
                result['amount'] = float(amt_elem.text) if amt_elem.text else None
            except ValueError:
                result['amount'] = None
            result['currency'] = amt_elem.get('Ccy', 'USD')

        # Charge Bearer
        result['chargeBearer'] = self._find_text(cdt_trf, 'ChrgBr')

        # Debtor Agent (Originator's Bank)
        dbtr_agt = self._find(cdt_trf, 'DbtrAgt/FinInstnId')
        if dbtr_agt is not None:
            result['originatorBank'] = self._find_text(dbtr_agt, 'ClrSysMmbId/MmbId')
            result['originatorBankBic'] = self._find_text(dbtr_agt, 'BICFI')
            result['originatorBankName'] = self._find_text(dbtr_agt, 'Nm')

        # Debtor (Originator)
        dbtr = self._find(cdt_trf, 'Dbtr')
        if dbtr is not None:
            result['originatorName'] = self._find_text(dbtr, 'Nm')
            result['originatorAddress'] = self._build_address(dbtr)
            result['originatorLei'] = self._find_text(dbtr, 'Id/OrgId/LEI')
            result['originatorTaxId'] = self._find_text(dbtr, 'Id/OrgId/Othr/Id')

        # Debtor Account
        dbtr_acct = self._find(cdt_trf, 'DbtrAcct/Id')
        if dbtr_acct is not None:
            result['originatorAccount'] = (
                self._find_text(dbtr_acct, 'Othr/Id') or
                self._find_text(dbtr_acct, 'IBAN')
            )

        # Creditor Agent (Beneficiary's Bank)
        cdtr_agt = self._find(cdt_trf, 'CdtrAgt/FinInstnId')
        if cdtr_agt is not None:
            result['beneficiaryBank'] = self._find_text(cdtr_agt, 'ClrSysMmbId/MmbId')
            result['beneficiaryBankBic'] = self._find_text(cdtr_agt, 'BICFI')
            result['beneficiaryBankName'] = self._find_text(cdtr_agt, 'Nm')

        # Creditor (Beneficiary)
        cdtr = self._find(cdt_trf, 'Cdtr')
        if cdtr is not None:
            result['beneficiaryName'] = self._find_text(cdtr, 'Nm')
            result['beneficiaryAddress'] = self._build_address(cdtr)
            result['beneficiaryLei'] = self._find_text(cdtr, 'Id/OrgId/LEI')
            result['beneficiaryTaxId'] = self._find_text(cdtr, 'Id/OrgId/Othr/Id')

        # Creditor Account
        cdtr_acct = self._find(cdt_trf, 'CdtrAcct/Id')
        if cdtr_acct is not None:
            result['beneficiaryAccount'] = (
                self._find_text(cdtr_acct, 'Othr/Id') or
                self._find_text(cdtr_acct, 'IBAN')
            )

        # Intermediary Bank
        intrmy = self._find(cdt_trf, 'IntrmyAgt1/FinInstnId')
        if intrmy is not None:
            result['intermediaryBank'] = self._find_text(intrmy, 'ClrSysMmbId/MmbId')
            result['intermediaryBankBic'] = self._find_text(intrmy, 'BICFI')
            result['intermediaryBankName'] = self._find_text(intrmy, 'Nm')

        # Remittance Information
        rmt_inf = self._find(cdt_trf, 'RmtInf')
        if rmt_inf is not None:
            result['paymentDetails'] = self._find_text(rmt_inf, 'Ustrd')
            # Structured
            strd = self._find(rmt_inf, 'Strd')
            if strd is not None:
                result['paymentInvoice'] = self._find_text(strd, 'RfrdDocInf/Nb')
                result['paymentPurposeCode'] = self._find_text(strd, 'RfrdDocInf/Tp/CdOrPrtry/Cd')

        # Purpose
        purp = self._find(cdt_trf, 'Purp')
        if purp is not None:
            result['paymentPurposeCode'] = self._find_text(purp, 'Cd')

        # Regulatory Reporting
        rgltry = self._find(cdt_trf, 'RgltryRptg')
        if rgltry is not None:
            result['regulatoryReportingCode'] = self._find_text(rgltry, 'Dtls/Cd')
            result['regulatoryCountry'] = self._find_text(rgltry, 'Authrty/Ctry')

        return result

    def _build_address(self, element: ET.Element) -> Optional[str]:
        """Build address string from postal address element."""
        pstl_adr = self._find(element, 'PstlAdr')
        if pstl_adr is None:
            return None

        parts = []
        for tag in ['StrtNm', 'BldgNb', 'TwnNm', 'CtrySubDvsn', 'PstCd', 'Ctry']:
            val = self._find_text(pstl_adr, tag)
            if val:
                parts.append(val)
        return ' '.join(parts) if parts else None


class ChipsXmlParser:
    """Parser for CHIPS XML format messages."""

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse CHIPS message into structured dict."""
        result = {
            'messageType': 'CHIPS',
        }

        # Handle JSON input (pre-parsed)
        if isinstance(raw_content, dict):
            return raw_content

        if raw_content.strip().startswith('{'):
            try:
                parsed = json.loads(raw_content)
                if isinstance(parsed, dict) and 'messageType' not in parsed:
                    parsed['messageType'] = 'CHIPS'
                return parsed
            except json.JSONDecodeError:
                pass

        # Parse CHIPS XML format using regex
        content = raw_content

        # Extract HEADER section first
        header_section = self._extract_section(content, 'HEADER')
        if header_section:
            # Message ID from UID in HEADER
            result['messageId'] = self._extract_tag(header_section, 'UID')
            result['sequenceNumber'] = self._extract_tag(header_section, 'SEQUENCE_NUMBER')
            result['messageTypeCode'] = self._extract_tag(header_section, 'MSG_TYPE')
            result['messagePriority'] = self._extract_tag(header_section, 'MSG_PRIORITY')
            result['creationDateTime'] = self._extract_tag(header_section, 'CREATION_DATETIME')

            # Value date from HEADER
            value_date = self._extract_tag(header_section, 'VALUE_DATE')
            if value_date and len(value_date) >= 8:
                result['valueDate'] = f"{value_date[:4]}-{value_date[4:6]}-{value_date[6:8]}"
            else:
                result['valueDate'] = value_date
        else:
            # Fallback to flat structure (legacy format)
            result['messageId'] = self._extract_tag(content, 'UID')
            result['sequenceNumber'] = self._extract_tag(content, 'SEQUENCE_NUMBER') or self._extract_tag(content, 'UID')
            result['messageTypeCode'] = self._extract_tag(content, 'MSG_TYPE')

            value_date = self._extract_tag(content, 'VALUE_DATE')
            if value_date and len(value_date) >= 8:
                result['valueDate'] = f"{value_date[:4]}-{value_date[4:6]}-{value_date[6:8]}"
            else:
                result['valueDate'] = value_date

        # Sender Info section
        sender_info = self._extract_section(content, 'SENDER_INFO')
        if sender_info:
            result['sendingParticipant'] = self._extract_tag(sender_info, 'SENDER_UID')
            result['sendingBankAba'] = self._extract_tag(sender_info, 'ABA')
            result['sendingBankName'] = self._extract_tag(sender_info, 'NAME')
            result['sendingBankBic'] = self._extract_tag(sender_info, 'BIC')
            result['sendingBankLei'] = self._extract_tag(sender_info, 'LEI')
            result['sendingBankAddress'] = self._extract_address(sender_info)
        else:
            # Fallback for flat structure
            result['sendingParticipant'] = self._extract_tag(content, 'SENDER_UID')

        # Receiver Info section
        receiver_info = self._extract_section(content, 'RECEIVER_INFO')
        if receiver_info:
            result['receivingParticipant'] = self._extract_tag(receiver_info, 'RECEIVER_UID')
            result['receivingBankAba'] = self._extract_tag(receiver_info, 'ABA')
            result['receivingBankName'] = self._extract_tag(receiver_info, 'NAME')
            result['receivingBankBic'] = self._extract_tag(receiver_info, 'BIC')
            result['receivingBankLei'] = self._extract_tag(receiver_info, 'LEI')
            result['receivingBankAddress'] = self._extract_address(receiver_info)
        else:
            # Fallback for flat structure
            result['receivingParticipant'] = self._extract_tag(content, 'RECEIVER_UID')

        # Payment Info section
        payment_info = self._extract_section(content, 'PAYMENT_INFO')
        if payment_info:
            result['senderReference'] = self._extract_tag(payment_info, 'SENDER_REF')
            result['relatedReference'] = self._extract_tag(payment_info, 'RELATED_REF')
            result['uetr'] = self._extract_tag(payment_info, 'UETR')
            result['chargeBearer'] = self._extract_tag(payment_info, 'CHARGE_BEARER')

            amount_str = self._extract_tag(payment_info, 'AMOUNT')
            if amount_str:
                try:
                    result['amount'] = float(amount_str.replace(',', ''))
                except ValueError:
                    result['amount'] = None
            result['currency'] = self._extract_tag(payment_info, 'CURRENCY') or 'USD'
        else:
            # Fallback for flat structure
            result['senderReference'] = self._extract_tag(content, 'SENDER_REF')
            amount_str = self._extract_tag(content, 'AMOUNT')
            if amount_str:
                try:
                    result['amount'] = float(amount_str.replace(',', ''))
                except ValueError:
                    result['amount'] = None
            result['currency'] = self._extract_tag(content, 'CURRENCY') or 'USD'

        # Originator Info section
        orig_info = self._extract_section(content, 'ORIG_INFO')
        if orig_info:
            result['originatorName'] = self._extract_tag(orig_info, 'NAME')
            result['originatorAccount'] = self._extract_tag(orig_info, 'ACCOUNT')
            result['originatorAddress'] = self._extract_address(orig_info)
            result['originatorTaxId'] = self._extract_tag(orig_info, 'TAX_ID')
            result['originatorLei'] = self._extract_tag(orig_info, 'LEI')

            # Extract contact info
            contact_section = self._extract_section(orig_info, 'CONTACT')
            if contact_section:
                result['originatorContactName'] = self._extract_tag(contact_section, 'NAME')
                result['originatorContactPhone'] = self._extract_tag(contact_section, 'PHONE')
                result['originatorContactEmail'] = self._extract_tag(contact_section, 'EMAIL')

        # Originator Bank Info section
        orig_bank_info = self._extract_section(content, 'ORIG_BANK_INFO')
        if orig_bank_info:
            result['originatorBank'] = self._extract_tag(orig_bank_info, 'ABA')
            result['originatorBankBic'] = self._extract_tag(orig_bank_info, 'BIC')
            result['originatorBankName'] = self._extract_tag(orig_bank_info, 'NAME')
            result['originatorBankAddress'] = self._extract_address(orig_bank_info)

        # Beneficiary Info section
        benef_info = self._extract_section(content, 'BENEF_INFO')
        if benef_info:
            result['beneficiaryName'] = self._extract_tag(benef_info, 'NAME')
            result['beneficiaryAccount'] = self._extract_tag(benef_info, 'ACCOUNT')
            result['beneficiaryAddress'] = self._extract_address(benef_info)
            result['beneficiaryTaxId'] = self._extract_tag(benef_info, 'TAX_ID')
            result['beneficiaryLei'] = self._extract_tag(benef_info, 'LEI')

            # Extract contact info
            contact_section = self._extract_section(benef_info, 'CONTACT')
            if contact_section:
                result['beneficiaryContactName'] = self._extract_tag(contact_section, 'NAME')
                result['beneficiaryContactPhone'] = self._extract_tag(contact_section, 'PHONE')
                result['beneficiaryContactEmail'] = self._extract_tag(contact_section, 'EMAIL')

        # Beneficiary Bank Info section
        benef_bank_info = self._extract_section(content, 'BENEF_BANK_INFO')
        if benef_bank_info:
            result['beneficiaryBank'] = self._extract_tag(benef_bank_info, 'ABA')
            result['beneficiaryBankBic'] = self._extract_tag(benef_bank_info, 'BIC')
            result['beneficiaryBankName'] = self._extract_tag(benef_bank_info, 'NAME')
            result['beneficiaryBankAddress'] = self._extract_address(benef_bank_info)

        # Intermediary Bank section
        intermediary_info = self._extract_section(content, 'INTERMEDIARY_BANK')
        if intermediary_info:
            result['intermediaryBank'] = self._extract_tag(intermediary_info, 'ABA')
            result['intermediaryBankBic'] = self._extract_tag(intermediary_info, 'BIC')
            result['intermediaryBankName'] = self._extract_tag(intermediary_info, 'NAME')
            result['intermediaryBankAddress'] = self._extract_address(intermediary_info)

        # Payment Details section
        pmt_details = self._extract_section(content, 'PAYMENT_DETAILS')
        if pmt_details:
            purpose = self._extract_tag(pmt_details, 'PURPOSE') or ''
            purpose_code = self._extract_tag(pmt_details, 'PURPOSE_CODE') or ''
            ref_info = self._extract_tag(pmt_details, 'REF_INFO') or ''
            invoice = self._extract_tag(pmt_details, 'INVOICE_NUMBER') or ''
            narrative = self._extract_tag(pmt_details, 'NARRATIVE') or ''

            result['paymentPurpose'] = purpose
            result['paymentPurposeCode'] = purpose_code
            result['paymentRefInfo'] = ref_info
            result['paymentInvoice'] = invoice
            result['paymentNarrative'] = narrative
            result['paymentDetails'] = f"{purpose} {ref_info} {narrative}".strip()

        # Regulatory Info section
        reg_info = self._extract_section(content, 'REGULATORY_INFO')
        if reg_info:
            result['regulatoryReportingCode'] = self._extract_tag(reg_info, 'REPORTING_CODE')
            result['regulatoryCountry'] = self._extract_tag(reg_info, 'COUNTRY')

        return result

    def _extract_tag(self, content: str, tag_name: str) -> Optional[str]:
        """Extract value from XML-like tag."""
        pattern = rf'<{tag_name}>\s*([^<]+?)\s*</{tag_name}>'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _extract_section(self, content: str, section_name: str) -> Optional[str]:
        """Extract entire section content."""
        pattern = rf'<{section_name}>(.*?)</{section_name}>'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
        return None

    def _extract_address(self, content: str) -> Optional[str]:
        """Extract address from ADDRESS section or ADDR1/ADDR2 tags."""
        # Try ADDRESS section first (nested LINE1/LINE2/LINE3)
        address_section = self._extract_section(content, 'ADDRESS')
        if address_section:
            lines = []
            for tag in ['LINE1', 'LINE2', 'LINE3']:
                line = self._extract_tag(address_section, tag)
                if line:
                    lines.append(line)
            if lines:
                return ' '.join(lines)

        # Fallback to ADDR1/ADDR2 (legacy format)
        addr1 = self._extract_tag(content, 'ADDR1') or ''
        addr2 = self._extract_tag(content, 'ADDR2') or ''
        combined = f"{addr1} {addr2}".strip()
        return combined if combined else None


class ChipsExtractor(BaseExtractor):
    """Extractor for CHIPS payment messages.

    Supports both current ISO 20022 format (pacs.008/pacs.009) and legacy proprietary format.
    Auto-detects format based on content structure.
    """

    MESSAGE_TYPE = "CHIPS"
    SILVER_TABLE = "stg_chips"

    def __init__(self):
        self.iso20022_parser = ChipsISO20022Parser()
        self.legacy_parser = ChipsXmlParser()
        # Default to ISO 20022 parser (current standard)
        self.parser = self.iso20022_parser

    def _detect_and_parse(self, raw_content: str) -> Dict[str, Any]:
        """Auto-detect format and parse accordingly."""
        content = raw_content.strip()

        # Check if it's ISO 20022 XML (pacs.008/pacs.009)
        if 'FIToFICstmrCdtTrf' in content or 'FICdtTrf' in content or 'pacs.008' in content or 'pacs.009' in content:
            logger.debug("Detected CHIPS ISO 20022 XML format")
            return self.iso20022_parser.parse(content)

        # Check if it's legacy proprietary XML
        if '<HEADER>' in content or '<SENDER_INFO>' in content or '<PAYMENT_INFO>' in content:
            logger.debug("Detected CHIPS legacy proprietary XML format")
            return self.legacy_parser.parse(content)

        # Try JSON (pre-parsed content)
        if content.startswith('{'):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass

        # Default: try ISO 20022 first, fall back to legacy
        try:
            return self.iso20022_parser.parse(content)
        except (ValueError, ET.ParseError):
            return self.legacy_parser.parse(content)

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw CHIPS content."""
        msg_id = (
            raw_content.get('messageId') or
            raw_content.get('sequenceNumber') or
            raw_content.get('senderReference') or
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
        """Extract all Silver layer fields from CHIPS message."""
        trunc = self.trunc

        # Generate message_id - prioritize messageId, fallback to sequenceNumber or senderReference
        message_id = (
            msg_content.get('messageId') or
            msg_content.get('sequenceNumber') or
            msg_content.get('senderReference') or
            f"CHIPS-{stg_id}"
        )

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'CHIPS',
            'sequence_number': trunc(msg_content.get('sequenceNumber'), 20),
            'message_type_code': trunc(msg_content.get('messageTypeCode'), 4),

            # Participants
            'sending_participant': trunc(msg_content.get('sendingParticipant'), 6),
            'receiving_participant': trunc(msg_content.get('receivingParticipant'), 6),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'USD',
            'value_date': msg_content.get('valueDate'),

            # References
            'sender_reference': trunc(msg_content.get('senderReference'), 35),
            'related_reference': trunc(msg_content.get('relatedReference'), 35),

            # Originator
            'originator_name': trunc(msg_content.get('originatorName'), 140),
            'originator_address': msg_content.get('originatorAddress'),
            'originator_account': trunc(msg_content.get('originatorAccount'), 34),

            # Beneficiary
            'beneficiary_name': trunc(msg_content.get('beneficiaryName'), 140),
            'beneficiary_address': msg_content.get('beneficiaryAddress'),
            'beneficiary_account': trunc(msg_content.get('beneficiaryAccount'), 34),

            # Banks - use ABA from ORIG_BANK_INFO/BENEF_BANK_INFO sections
            'originator_bank': trunc(msg_content.get('originatorBank'), 11),
            'beneficiary_bank': trunc(msg_content.get('beneficiaryBank'), 11),
            'intermediary_bank': trunc(msg_content.get('intermediaryBank'), 11),

            # Additional Info
            'payment_details': msg_content.get('paymentDetails'),

            # Additional mandatory fields
            'message_id': trunc(message_id, 35),
            'sender_participant_id': trunc(msg_content.get('sendingParticipant'), 6),
            'receiver_participant_id': trunc(msg_content.get('receivingParticipant'), 6),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'sequence_number', 'message_type_code',
            'sending_participant', 'receiving_participant',
            'amount', 'currency', 'value_date',
            'sender_reference', 'related_reference',
            'originator_name', 'originator_address', 'originator_account',
            'beneficiary_name', 'beneficiary_address', 'beneficiary_account',
            'originator_bank', 'beneficiary_bank', 'intermediary_bank',
            'payment_details',
            'message_id', 'sender_participant_id', 'receiver_participant_id',
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
        """Extract Gold layer entities from CHIPS Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Originator Party (Debtor) - uses Silver column names
        if silver_data.get('originator_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('originator_name'),
                role="DEBTOR",
                party_type='UNKNOWN',
                country='US',
            ))

        # Beneficiary Party (Creditor)
        if silver_data.get('beneficiary_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('beneficiary_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='US',
            ))

        # Originator Account
        if silver_data.get('originator_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('originator_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'USD',
            ))

        # Beneficiary Account
        if silver_data.get('beneficiary_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('beneficiary_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'USD',
            ))

        # Originator Bank (Debtor Agent)
        if silver_data.get('originator_bank') or silver_data.get('sending_participant'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=silver_data.get('sending_participant'),
                bic=silver_data.get('originator_bank'),
                clearing_system='CHIPS',
                country='US',
            ))

        # Beneficiary Bank (Creditor Agent)
        if silver_data.get('beneficiary_bank') or silver_data.get('receiving_participant'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=silver_data.get('receiving_participant'),
                bic=silver_data.get('beneficiary_bank'),
                clearing_system='CHIPS',
                country='US',
            ))

        # Intermediary Bank
        if silver_data.get('intermediary_bank'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INTERMEDIARY",
                bic=silver_data.get('intermediary_bank'),
                clearing_system='CHIPS',
                country='US',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('CHIPS', ChipsExtractor())
ExtractorRegistry.register('chips', ChipsExtractor())
