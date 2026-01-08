"""UK Faster Payments Service (FPS) Extractor - ISO 20022 pacs.008 based.

ISO 20022 INHERITANCE HIERARCHY:
    FPS uses UK Faster Payments ISO 20022 usage guidelines based on pacs.008.
    The FpsISO20022Parser inherits from Pacs008Parser.

    BaseISO20022Parser
        └── Pacs008Parser (FI to FI Customer Credit Transfer - pacs.008.001.08)
            └── FpsISO20022Parser (UK Faster Payments usage guidelines)

FPS-SPECIFIC ELEMENTS:
    - UK Sort Codes - 6-digit clearing codes (GBDSC scheme, e.g., 20-00-00)
    - Account Number - 8 digits (e.g., 12345678)
    - GBP currency (British Pounds Sterling)
    - Real-time retail payments up to £250,000

CLEARING SYSTEM:
    - GBDSC (Great Britain Domestic Sort Code)

DATABASE TABLES:
    - Bronze: bronze.raw_payment_messages
    - Silver: silver.stg_fps
    - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_fps

MAPPING INHERITANCE:
    FPS -> pacs.008.base (PARTIAL - UK-specific fields override base)
"""

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

# Import ISO 20022 base classes for inheritance
try:
    from ..iso20022 import Pacs008Parser, Pacs008Extractor
    ISO20022_BASE_AVAILABLE = True
except ImportError:
    ISO20022_BASE_AVAILABLE = False
    logger.warning("ISO 20022 base classes not available - FPS will use standalone implementation")


# =============================================================================
# FPS ISO 20022 PARSER (inherits from Pacs008Parser)
# =============================================================================

# Use conditional inheritance pattern for backward compatibility
_FpsParserBase = Pacs008Parser if ISO20022_BASE_AVAILABLE else object


class FpsISO20022Parser(_FpsParserBase):
    """FPS ISO 20022 pacs.008 parser with UK Faster Payments usage guidelines.

    Inherits from Pacs008Parser and adds FPS-specific processing:
    - UK Sort Code extraction (GBDSC scheme)
    - FPS-specific clearing system identification
    - UK address format handling

    ISO 20022 Version: pacs.008.001.08
    Usage Guidelines: UK Faster Payments

    Inheritance Hierarchy:
        BaseISO20022Parser -> Pacs008Parser -> FpsISO20022Parser
    """

    # FPS-specific constants
    CLEARING_SYSTEM = "GBDSC"  # UK Domestic Sort Code
    DEFAULT_CURRENCY = "GBP"
    MESSAGE_TYPE = "FPS"

    def __init__(self):
        """Initialize FPS parser."""
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse FPS ISO 20022 pacs.008 message.

        Uses inherited pacs.008 parsing from Pacs008Parser and adds
        FPS-specific fields.
        """
        # Handle JSON/dict input
        if isinstance(raw_content, dict):
            return raw_content

        if raw_content.strip().startswith('{'):
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError:
                pass

        # Use parent pacs.008 parsing if available
        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = self._parse_standalone(raw_content)

        # Add FPS-specific fields
        result['isFps'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM

        # Map standard fields to FPS terminology
        self._add_fps_field_aliases(result)

        # Extract UK Sort Codes
        self._extract_uk_sort_codes(result)

        return result

    def _parse_standalone(self, raw_content: str) -> Dict[str, Any]:
        """Standalone parsing when base class not available.

        Delegates to the legacy FpsXmlParser for backward compatibility.
        """
        # Will use the FpsXmlParser._parse_iso20022 method
        legacy_parser = FpsXmlParser()
        return legacy_parser.parse(raw_content)

    def _add_fps_field_aliases(self, result: Dict[str, Any]) -> None:
        """Add FPS-specific field aliases (payer/payee terminology)."""
        # Map ISO 20022 debtor -> FPS payer
        if result.get('debtorName') and not result.get('payerName'):
            result['payerName'] = result['debtorName']
        if result.get('debtorAccount') and not result.get('payerAccount'):
            result['payerAccount'] = result['debtorAccount']

        # Map ISO 20022 creditor -> FPS payee
        if result.get('creditorName') and not result.get('payeeName'):
            result['payeeName'] = result['creditorName']
        if result.get('creditorAccount') and not result.get('payeeAccount'):
            result['payeeAccount'] = result['creditorAccount']

    def _extract_uk_sort_codes(self, result: Dict[str, Any]) -> None:
        """Extract UK Sort Codes from various fields.

        FPS uses GBDSC (UK Domestic Sort Code) scheme.
        Sort codes are 6 digits, often formatted as NN-NN-NN.
        """
        # Try to extract from clearing system member ID
        for prefix in ['debtor', 'creditor']:
            agent_key = f'{prefix}AgentClrSysMmbId'
            sort_key = f'{prefix}SortCode'
            fps_sort_key = f'payer_sort_code' if prefix == 'debtor' else f'payee_sort_code'

            if result.get(agent_key) and not result.get(sort_key):
                mbr_id = result.get(agent_key)
                if mbr_id and len(mbr_id) == 6 and mbr_id.isdigit():
                    result[sort_key] = mbr_id
                    result[fps_sort_key] = mbr_id


# =============================================================================
# LEGACY XML PARSER (kept for backward compatibility)
# =============================================================================

class FpsXmlParser:
    """Parser for FPS ISO 20022 pacs.008 XML messages.

    Handles namespace stripping and extracts fields from the FIToFICstmrCdtTrf
    structure used by UK Faster Payments.

    NOTE: New code should use FpsISO20022Parser which inherits from Pacs008Parser.
    """

    NS_PATTERN = re.compile(r'\{[^}]+\}')

    def _strip_ns(self, tag: str) -> str:
        """Remove namespace from XML tag."""
        return self.NS_PATTERN.sub('', tag)

    def _find(self, element: ET.Element, path: str) -> Optional[ET.Element]:
        """Find element using local names (ignoring namespaces).

        Args:
            element: Parent element to search from
            path: Slash-separated path of element names (e.g., 'GrpHdr/MsgId')

        Returns:
            Found element or None
        """
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
        """Parse FPS XML message to dictionary.

        Args:
            content: Raw XML string or JSON string

        Returns:
            Dictionary with normalized field names (camelCase)
        """
        # If already dict, just return
        if isinstance(raw_content, dict):
            return raw_content

        # Try JSON first
        try:
            parsed = json.loads(raw_content)
            return parsed
        except (json.JSONDecodeError, TypeError):
            pass

        # Parse XML
        try:
            # Strip BOM if present
            if raw_content.startswith('\ufeff'):
                raw_content = raw_content[1:]
            root = ET.fromstring(raw_content)
        except ET.ParseError as e:
            logger.error(f"Failed to parse FPS XML: {e}")
            return {}

        return self._parse_iso20022(root)

    def _parse_iso20022(self, root: ET.Element) -> Dict[str, Any]:
        """Parse FPS pacs.008 XML structure to normalized dict."""
        result = {}

        # Find the FIToFICstmrCdtTrf element (may be root, child of Document, or nested)
        fi_transfer = self._find(root, 'FIToFICstmrCdtTrf')
        if fi_transfer is None:
            # Check if root itself is FIToFICstmrCdtTrf
            if self._strip_ns(root.tag) == 'FIToFICstmrCdtTrf':
                fi_transfer = root
            else:
                # Try Document/FIToFICstmrCdtTrf
                for child in root:
                    if self._strip_ns(child.tag) == 'FIToFICstmrCdtTrf':
                        fi_transfer = child
                        break

        if fi_transfer is None:
            logger.warning("FIToFICstmrCdtTrf element not found in FPS XML")
            return result

        # ---------------------------------------------------------------
        # GROUP HEADER (GrpHdr)
        # ---------------------------------------------------------------
        grp_hdr = self._find(fi_transfer, 'GrpHdr')
        if grp_hdr is not None:
            result['messageId'] = self._find_text(grp_hdr, 'MsgId')
            result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')
            result['numberOfTransactions'] = self._find_text(grp_hdr, 'NbOfTxs')
            result['settlementDate'] = self._find_text(grp_hdr, 'IntrBkSttlmDt')
            result['settlementMethod'] = self._find_text(grp_hdr, 'SttlmInf/SttlmMtd')

        # ---------------------------------------------------------------
        # CREDIT TRANSFER TRANSACTION INFO (CdtTrfTxInf)
        # ---------------------------------------------------------------
        cdt_trf = self._find(fi_transfer, 'CdtTrfTxInf')
        if cdt_trf is not None:
            # Payment Identification
            pmt_id = self._find(cdt_trf, 'PmtId')
            if pmt_id is not None:
                result['instructionId'] = self._find_text(pmt_id, 'InstrId')
                result['endToEndId'] = self._find_text(pmt_id, 'EndToEndId')
                result['paymentId'] = self._find_text(pmt_id, 'TxId')
                result['uetr'] = self._find_text(pmt_id, 'UETR')

            # Interbank Settlement Amount (with Ccy attribute)
            amt_elem = self._find(cdt_trf, 'IntrBkSttlmAmt')
            if amt_elem is not None:
                result['amount'] = amt_elem.text
                result['currency'] = amt_elem.get('Ccy') or 'GBP'

            # ---------------------------------------------------------------
            # DEBTOR (Dbtr) - Payer
            # ---------------------------------------------------------------
            dbtr = self._find(cdt_trf, 'Dbtr')
            if dbtr is not None:
                result['debtorName'] = self._find_text(dbtr, 'Nm')
                result['payerName'] = result['debtorName']

                # Postal Address
                pstl_adr = self._find(dbtr, 'PstlAdr')
                if pstl_adr is not None:
                    result['payerAddress'] = self._find_text(pstl_adr, 'StrtNm')
                    result['debtorStreetName'] = result['payerAddress']

            # Debtor Account (DbtrAcct)
            dbtr_acct = self._find(cdt_trf, 'DbtrAcct')
            if dbtr_acct is not None:
                # Try Othr/Id first (UK BBAN format)
                acct_id = self._find_text(dbtr_acct, 'Id/Othr/Id')
                if acct_id:
                    result['debtorAccountNumber'] = acct_id
                    result['payerAccount'] = acct_id
                # Try IBAN
                iban = self._find_text(dbtr_acct, 'Id/IBAN')
                if iban:
                    result['payerIban'] = iban
                    result['debtorIban'] = iban

            # Debtor Agent (DbtrAgt) - Payer's Bank
            dbtr_agt = self._find(cdt_trf, 'DbtrAgt')
            if dbtr_agt is not None:
                fi_id = self._find(dbtr_agt, 'FinInstnId')
                if fi_id is not None:
                    result['payerBic'] = self._find_text(fi_id, 'BICFI')
                    result['debtorAgentBic'] = result['payerBic']
                    result['debtorAgentName'] = self._find_text(fi_id, 'Nm')

                    # Sort Code (ClrSysMmbId/MmbId)
                    sort_code = self._find_text(fi_id, 'ClrSysMmbId/MmbId')
                    if sort_code:
                        result['payerSortCode'] = sort_code
                        result['debtorSortCode'] = sort_code

            # ---------------------------------------------------------------
            # CREDITOR (Cdtr) - Payee
            # ---------------------------------------------------------------
            cdtr = self._find(cdt_trf, 'Cdtr')
            if cdtr is not None:
                result['creditorName'] = self._find_text(cdtr, 'Nm')
                result['payeeName'] = result['creditorName']

                # Postal Address
                pstl_adr = self._find(cdtr, 'PstlAdr')
                if pstl_adr is not None:
                    result['payeeAddress'] = self._find_text(pstl_adr, 'StrtNm')
                    result['creditorStreetName'] = result['payeeAddress']

            # Creditor Account (CdtrAcct)
            cdtr_acct = self._find(cdt_trf, 'CdtrAcct')
            if cdtr_acct is not None:
                # Try Othr/Id first (UK BBAN format)
                acct_id = self._find_text(cdtr_acct, 'Id/Othr/Id')
                if acct_id:
                    result['creditorAccountNumber'] = acct_id
                    result['payeeAccount'] = acct_id
                # Try IBAN
                iban = self._find_text(cdtr_acct, 'Id/IBAN')
                if iban:
                    result['payeeIban'] = iban
                    result['creditorIban'] = iban

            # Creditor Agent (CdtrAgt) - Payee's Bank
            cdtr_agt = self._find(cdt_trf, 'CdtrAgt')
            if cdtr_agt is not None:
                fi_id = self._find(cdtr_agt, 'FinInstnId')
                if fi_id is not None:
                    result['payeeBic'] = self._find_text(fi_id, 'BICFI')
                    result['creditorAgentBic'] = result['payeeBic']
                    result['creditorAgentName'] = self._find_text(fi_id, 'Nm')

                    # Sort Code (ClrSysMmbId/MmbId)
                    sort_code = self._find_text(fi_id, 'ClrSysMmbId/MmbId')
                    if sort_code:
                        result['payeeSortCode'] = sort_code
                        result['creditorSortCode'] = sort_code

            # ---------------------------------------------------------------
            # REMITTANCE INFORMATION (RmtInf)
            # ---------------------------------------------------------------
            rmt_inf = self._find(cdt_trf, 'RmtInf')
            if rmt_inf is not None:
                result['remittanceInfo'] = self._find_text(rmt_inf, 'Ustrd')

                # Structured reference
                strd = self._find(rmt_inf, 'Strd')
                if strd is not None:
                    ref = self._find_text(strd, 'RfrdDocInf/Nb')
                    if ref:
                        result['paymentReference'] = ref

        return result


class FpsParser:
    """Legacy parser for FPS ISO 20022 pacs.008 XML messages.

    Deprecated: Use FpsXmlParser instead. This class is kept for backward compatibility.
    """

    @staticmethod
    def strip_namespaces(xml_string: str) -> str:
        """Remove XML namespaces for easier parsing."""
        # Remove xmlns declarations
        xml_string = re.sub(r'\sxmlns[^"]*"[^"]*"', '', xml_string)
        # Remove namespace prefixes
        xml_string = re.sub(r'<(/?)[\w]+:', r'<\1', xml_string)
        return xml_string

    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """Parse FPS XML message to dictionary.

        Args:
            content: Raw XML string or JSON string

        Returns:
            Dictionary with normalized field names (camelCase)
        """
        # If already JSON/dict, just return normalized
        if isinstance(content, dict):
            return content

        try:
            parsed = json.loads(content)
            return parsed
        except (json.JSONDecodeError, TypeError):
            pass

        # Try XML parsing
        try:
            clean_xml = FpsParser.strip_namespaces(content)
            root = ET.fromstring(clean_xml)
            return FpsParser._parse_xml_to_dict(root)
        except ET.ParseError as e:
            logger.warning(f"Failed to parse FPS XML: {e}")
            return {}

    @staticmethod
    def _parse_xml_to_dict(root: ET.Element) -> Dict[str, Any]:
        """Parse FPS pacs.008 XML structure to normalized dict."""
        result = {}

        # Find the FIToFICstmrCdtTrf element (may be root or nested)
        fi_to_fi = root.find('.//FIToFICstmrCdtTrf') or root

        # Group Header
        grp_hdr = fi_to_fi.find('.//GrpHdr')
        if grp_hdr is not None:
            result['messageId'] = FpsParser._get_text(grp_hdr, 'MsgId')
            result['creationDateTime'] = FpsParser._get_text(grp_hdr, 'CreDtTm')
            result['numberOfTransactions'] = FpsParser._get_text(grp_hdr, 'NbOfTxs')
            result['settlementDate'] = FpsParser._get_text(grp_hdr, 'IntrBkSttlmDt')

        # Credit Transfer Transaction Info
        cdt_trf = fi_to_fi.find('.//CdtTrfTxInf')
        if cdt_trf is not None:
            # Payment Identification
            pmt_id = cdt_trf.find('PmtId')
            if pmt_id is not None:
                result['instructionId'] = FpsParser._get_text(pmt_id, 'InstrId')
                result['endToEndId'] = FpsParser._get_text(pmt_id, 'EndToEndId')
                result['paymentId'] = FpsParser._get_text(pmt_id, 'TxId')
                result['uetr'] = FpsParser._get_text(pmt_id, 'UETR')

            # Amount
            amt = cdt_trf.find('IntrBkSttlmAmt')
            if amt is not None:
                result['amount'] = amt.text
                result['currency'] = amt.get('Ccy', 'GBP')

            # Debtor (Payer)
            dbtr = cdt_trf.find('Dbtr')
            if dbtr is not None:
                result['payerName'] = FpsParser._get_text(dbtr, 'Nm')
                result['debtorName'] = result['payerName']
                pstl_adr = dbtr.find('PstlAdr')
                if pstl_adr is not None:
                    result['payerAddress'] = FpsParser._get_text(pstl_adr, 'AdrLine')

            # Debtor Account
            dbtr_acct = cdt_trf.find('DbtrAcct')
            if dbtr_acct is not None:
                acct_id = dbtr_acct.find('.//Id/Othr/Id')
                if acct_id is not None:
                    result['payerAccount'] = acct_id.text
                    result['debtorAccountNumber'] = acct_id.text
                iban = dbtr_acct.find('.//Id/IBAN')
                if iban is not None:
                    result['payerIban'] = iban.text

            # Debtor Agent (Payer's Bank - Sort Code)
            dbtr_agt = cdt_trf.find('DbtrAgt')
            if dbtr_agt is not None:
                sort_code = dbtr_agt.find('.//ClrSysMmbId/MmbId')
                if sort_code is not None:
                    result['payerSortCode'] = sort_code.text
                    result['debtorSortCode'] = sort_code.text
                bic = dbtr_agt.find('.//BICFI')
                if bic is not None:
                    result['payerBic'] = bic.text

            # Creditor (Payee)
            cdtr = cdt_trf.find('Cdtr')
            if cdtr is not None:
                result['payeeName'] = FpsParser._get_text(cdtr, 'Nm')
                result['creditorName'] = result['payeeName']
                pstl_adr = cdtr.find('PstlAdr')
                if pstl_adr is not None:
                    result['payeeAddress'] = FpsParser._get_text(pstl_adr, 'AdrLine')

            # Creditor Account
            cdtr_acct = cdt_trf.find('CdtrAcct')
            if cdtr_acct is not None:
                acct_id = cdtr_acct.find('.//Id/Othr/Id')
                if acct_id is not None:
                    result['payeeAccount'] = acct_id.text
                    result['creditorAccountNumber'] = acct_id.text
                iban = cdtr_acct.find('.//Id/IBAN')
                if iban is not None:
                    result['payeeIban'] = iban.text

            # Creditor Agent (Payee's Bank - Sort Code)
            cdtr_agt = cdt_trf.find('CdtrAgt')
            if cdtr_agt is not None:
                sort_code = cdtr_agt.find('.//ClrSysMmbId/MmbId')
                if sort_code is not None:
                    result['payeeSortCode'] = sort_code.text
                    result['creditorSortCode'] = sort_code.text
                bic = cdtr_agt.find('.//BICFI')
                if bic is not None:
                    result['payeeBic'] = bic.text

            # Remittance Information
            rmt_inf = cdt_trf.find('RmtInf')
            if rmt_inf is not None:
                result['remittanceInfo'] = FpsParser._get_text(rmt_inf, 'Ustrd')
                strd = rmt_inf.find('Strd')
                if strd is not None:
                    result['paymentReference'] = FpsParser._get_text(strd, './/CdtrRefInf/Ref')

        return result

    @staticmethod
    def _get_text(element: ET.Element, path: str) -> Optional[str]:
        """Get text from an element at the given path."""
        if element is None:
            return None
        found = element.find(path)
        return found.text if found is not None else None


class FpsExtractor(BaseExtractor):
    """Extractor for UK Faster Payments Service (FPS) messages.

    ISO 20022 INHERITANCE:
        FPS inherits from pacs.008 (FI to FI Customer Credit Transfer).
        The FpsISO20022Parser inherits from Pacs008Parser.
        Uses UK Faster Payments usage guidelines.

    Format Support:
        1. ISO 20022 XML (pacs.008.001.08) - Current standard

    FPS-Specific Elements:
        - UK Sort Codes - 6-digit clearing codes (GBDSC scheme)
        - Account Number - 8 digits
        - GBP currency (British Pounds Sterling)
        - Real-time retail payments up to £250,000

    Database Tables:
        - Bronze: bronze.raw_payment_messages
        - Silver: silver.stg_fps
        - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_fps

    Inheritance Hierarchy:
        BaseExtractor -> FpsExtractor
        (Parser: Pacs008Parser -> FpsISO20022Parser)
    """

    MESSAGE_TYPE = "FPS"
    SILVER_TABLE = "stg_iso20022_pacs008"  # Shared ISO 20022 pacs.008 table
    DEFAULT_CURRENCY = "GBP"
    CLEARING_SYSTEM = "GBDSC"

    def __init__(self):
        """Initialize FPS extractor with ISO 20022 parser."""
        # Primary: ISO 20022 parser (current standard)
        self.iso20022_parser = FpsISO20022Parser()
        # Legacy: XML parser (kept for backward compatibility)
        self.legacy_parser = FpsXmlParser()
        # Default to ISO 20022 parser
        self.parser = self.iso20022_parser

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw FPS content.

        Accepts both pre-parsed dict and raw XML/JSON strings.
        """
        # Parse if string content
        if isinstance(raw_content, str):
            parsed = self.parser.parse(raw_content)
        else:
            parsed = raw_content

        msg_id = (
            parsed.get('paymentId') or
            parsed.get('endToEndId') or
            parsed.get('messageId') or
            ''
        )
        return {
            'raw_id': self.generate_raw_id(msg_id),
            'message_type': self.MESSAGE_TYPE,
            'raw_content': json.dumps(parsed) if isinstance(parsed, dict) else raw_content,
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
        """Extract all Silver layer fields from FPS message.

        This method maps to ALL columns in silver.stg_fps table.
        """
        trunc = self.trunc

        # Parse content if needed
        if isinstance(msg_content, str):
            msg_content = self.parser.parse(msg_content)

        # Extract values with proper fallbacks for None
        payer_name = msg_content.get('payerName') or msg_content.get('debtorName')
        payer_account = msg_content.get('payerAccount') or msg_content.get('debtorAccountNumber')
        payer_sort_code = msg_content.get('payerSortCode') or msg_content.get('debtorSortCode')

        payee_name = msg_content.get('payeeName') or msg_content.get('creditorName')
        payee_account = msg_content.get('payeeAccount') or msg_content.get('creditorAccountNumber')
        payee_sort_code = msg_content.get('payeeSortCode') or msg_content.get('creditorSortCode')

        return {
            # System columns (must match DB exactly)
            'stg_id': stg_id,
            '_raw_id': raw_id,
            '_batch_id': batch_id,

            # Message identification
            'message_id': trunc(msg_content.get('messageId'), 35),
            'message_type': 'FPS',
            'creation_date_time': msg_content.get('creationDateTime'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'GBP',

            # Debtor (ISO 20022 terminology) - maps to DB columns
            'debtor_name': trunc(payer_name, 140),
            'debtor_account_account_number': trunc(payer_account, 8),
            'debtor_account_sort_code': trunc(payer_sort_code, 6),

            # Payer (FPS terminology) - also maps to DB columns
            'payer_name': trunc(payer_name, 140),
            'payer_account': trunc(payer_account, 8),
            'payer_address': msg_content.get('payerAddress'),
            'payer_sort_code': trunc(payer_sort_code, 6),

            # Creditor (ISO 20022 terminology)
            'creditor_name': trunc(payee_name, 140),
            'creditor_account_account_number': trunc(payee_account, 8),
            'creditor_account_sort_code': trunc(payee_sort_code, 6),

            # Payee (FPS terminology)
            'payee_name': trunc(payee_name, 140),
            'payee_account': trunc(payee_account, 8),
            'payee_address': msg_content.get('payeeAddress'),
            'payee_sort_code': trunc(payee_sort_code, 6),

            # Payment identification
            'payment_id': trunc(msg_content.get('paymentId'), 35),
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),

            # Remittance
            'payment_reference': trunc(msg_content.get('paymentReference'), 35),
            'remittance_info': msg_content.get('remittanceInfo'),

            # Settlement
            'requested_execution_date': msg_content.get('requestedExecutionDate') or msg_content.get('settlementDate'),
            'settlement_datetime': msg_content.get('settlementDatetime') or msg_content.get('settlementDate'),

            # Lineage
            'raw_id': raw_id,
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT.

        MUST match actual silver.stg_fps table columns exactly.
        System-managed columns (_ingested_at, _processed_at, etc.) are excluded.
        """
        return [
            # System columns
            'stg_id',
            '_raw_id',
            '_batch_id',

            # Message identification
            'message_id',
            'message_type',
            'creation_date_time',

            # Amount
            'amount',
            'currency',

            # Debtor/Payer
            'debtor_name',
            'debtor_account_account_number',
            'debtor_account_sort_code',
            'payer_name',
            'payer_account',
            'payer_address',
            'payer_sort_code',

            # Creditor/Payee
            'creditor_name',
            'creditor_account_account_number',
            'creditor_account_sort_code',
            'payee_name',
            'payee_account',
            'payee_address',
            'payee_sort_code',

            # Payment details
            'payment_id',
            'instruction_id',
            'end_to_end_id',
            'payment_reference',
            'remittance_info',
            'requested_execution_date',
            'settlement_datetime',
            'raw_id',
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
        """Extract Gold layer entities from FPS Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier

        Returns:
            GoldEntities containing parties, accounts, and financial institutions
        """
        entities = GoldEntities()

        # Get payer/debtor fields (may be in either naming convention)
        payer_name = silver_data.get('payer_name') or silver_data.get('debtor_name')
        payer_account = silver_data.get('payer_account') or silver_data.get('debtor_account_account_number')
        payer_sort_code = silver_data.get('payer_sort_code') or silver_data.get('debtor_account_sort_code')
        payer_address = silver_data.get('payer_address')

        # Get payee/creditor fields
        payee_name = silver_data.get('payee_name') or silver_data.get('creditor_name')
        payee_account = silver_data.get('payee_account') or silver_data.get('creditor_account_account_number')
        payee_sort_code = silver_data.get('payee_sort_code') or silver_data.get('creditor_account_sort_code')
        payee_address = silver_data.get('payee_address')

        # ---------------------------------------------------------------
        # PARTIES
        # ---------------------------------------------------------------

        # Payer Party (Debtor)
        if payer_name:
            entities.parties.append(PartyData(
                name=payer_name,
                role="DEBTOR",
                party_type='UNKNOWN',  # FPS doesn't distinguish person/org
                country='GB',
                street_name=payer_address,  # Use street_name for address
            ))

        # Payee Party (Creditor)
        if payee_name:
            entities.parties.append(PartyData(
                name=payee_name,
                role="CREDITOR",
                party_type='UNKNOWN',
                country='GB',
                street_name=payee_address,  # Use street_name for address
            ))

        # ---------------------------------------------------------------
        # ACCOUNTS
        # ---------------------------------------------------------------

        # Payer Account (UK Sort Code + Account Number)
        # Note: Sort code is stored in the account number as prefix (sort_code + account_number)
        if payer_account:
            # UK accounts use sort code + account number format
            full_account = f"{payer_sort_code}-{payer_account}" if payer_sort_code else payer_account
            entities.accounts.append(AccountData(
                account_number=full_account,
                role="DEBTOR",
                account_type='CACC',  # Current Account
                currency='GBP',
            ))

        # Payee Account
        if payee_account:
            full_account = f"{payee_sort_code}-{payee_account}" if payee_sort_code else payee_account
            entities.accounts.append(AccountData(
                account_number=full_account,
                role="CREDITOR",
                account_type='CACC',
                currency='GBP',
            ))

        # ---------------------------------------------------------------
        # FINANCIAL INSTITUTIONS (Banks identified by Sort Code)
        # ---------------------------------------------------------------

        # Payer's Bank (Debtor Agent)
        if payer_sort_code:
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=payer_sort_code,
                clearing_system='GBDSC',  # Great Britain Domestic Sort Code
                country='GB',
            ))

        # Payee's Bank (Creditor Agent)
        if payee_sort_code:
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=payee_sort_code,
                clearing_system='GBDSC',
                country='GB',
            ))

        return entities


# Register the extractor with all aliases
ExtractorRegistry.register('FPS', FpsExtractor())
ExtractorRegistry.register('fps', FpsExtractor())
ExtractorRegistry.register('FASTER_PAYMENTS', FpsExtractor())
ExtractorRegistry.register('faster_payments', FpsExtractor())
ExtractorRegistry.register('UK_FPS', FpsExtractor())
