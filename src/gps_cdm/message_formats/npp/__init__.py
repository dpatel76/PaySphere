"""NPP (Australia New Payments Platform) Extractor - ISO 20022 pacs.008 based.

ISO 20022 INHERITANCE HIERARCHY:
    NPP uses ISO 20022 pacs.008 FIToFICstmrCdtTrf message format with Australian-specific
    BSB (Bank-State-Branch) + Account Number identification. The NppISO20022Parser
    inherits from Pacs008Parser.

    BaseISO20022Parser
        └── Pacs008Parser (FI to FI Customer Credit Transfer - pacs.008.001.08)
            └── NppISO20022Parser (Australian NPP usage guidelines)

NPP-SPECIFIC ELEMENTS:
    - BSB: 6 digits identifying the bank branch (e.g., 064-000)
    - Account Number: 9 digits (e.g., 123456789)
    - PayID: Alternative addressing (email, phone, ABN, etc.)

CLEARING SYSTEM:
    - AUBSB (Australian BSB) / NPPA (NPP Australia)
    - Currency: AUD (Australian Dollar)
    - Real-time instant payments including Osko

DATABASE TABLES:
    - Bronze: bronze.raw_payment_messages
    - Silver: silver.stg_npp
    - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_npp

MAPPING INHERITANCE:
    NPP -> pacs.008.base (COMPLETE)
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
    logger.warning("ISO 20022 base classes not available - NPP will use standalone implementation")


class NppXmlParser:
    """Parser for NPP ISO 20022 pacs.008 XML messages.

    Handles namespace stripping and extracts fields from the FIToFICstmrCdtTrf
    structure used by Australia's New Payments Platform.
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
        """Parse NPP XML message to dictionary.

        Args:
            raw_content: Raw XML string or JSON string

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
            logger.error(f"Failed to parse NPP XML: {e}")
            return {}

        return self._parse_iso20022(root)

    def _parse_iso20022(self, root: ET.Element) -> Dict[str, Any]:
        """Parse NPP pacs.008 XML structure to normalized dict."""
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
            logger.warning("FIToFICstmrCdtTrf element not found in NPP XML")
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
            result['clearingSystem'] = self._find_text(grp_hdr, 'SttlmInf/ClrSys/Prtry')

            # Total Interbank Settlement Amount
            ttl_amt = self._find(grp_hdr, 'TtlIntrBkSttlmAmt')
            if ttl_amt is not None:
                result['totalAmount'] = ttl_amt.text
                result['totalCurrency'] = ttl_amt.get('Ccy') or 'AUD'

            # Instructing Agent (sender bank)
            instg_agt = self._find(grp_hdr, 'InstgAgt/FinInstnId')
            if instg_agt is not None:
                result['instructingAgentBic'] = self._find_text(instg_agt, 'BICFI')
                result['instructingAgentName'] = self._find_text(instg_agt, 'Nm')
                result['instructingAgentBsb'] = self._find_text(instg_agt, 'ClrSysMmbId/MmbId')

            # Instructed Agent (receiver bank)
            instd_agt = self._find(grp_hdr, 'InstdAgt/FinInstnId')
            if instd_agt is not None:
                result['instructedAgentBic'] = self._find_text(instd_agt, 'BICFI')
                result['instructedAgentName'] = self._find_text(instd_agt, 'Nm')
                result['instructedAgentBsb'] = self._find_text(instd_agt, 'ClrSysMmbId/MmbId')

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

            # Payment Type Information
            pmt_tp = self._find(cdt_trf, 'PmtTpInf')
            if pmt_tp is not None:
                result['instructionPriority'] = self._find_text(pmt_tp, 'InstrPrty')
                result['serviceLevel'] = self._find_text(pmt_tp, 'SvcLvl/Prtry')
                result['localInstrument'] = self._find_text(pmt_tp, 'LclInstrm/Prtry')
                result['categoryPurpose'] = self._find_text(pmt_tp, 'CtgyPurp/Cd')

            # Interbank Settlement Amount (with Ccy attribute)
            amt_elem = self._find(cdt_trf, 'IntrBkSttlmAmt')
            if amt_elem is not None:
                result['amount'] = amt_elem.text
                result['currency'] = amt_elem.get('Ccy') or 'AUD'

            # Charge Bearer
            result['chargeBearer'] = self._find_text(cdt_trf, 'ChrgBr')

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
                    result['debtorStreetName'] = self._find_text(pstl_adr, 'StrtNm')
                    result['debtorBuildingNumber'] = self._find_text(pstl_adr, 'BldgNb')
                    result['debtorPostCode'] = self._find_text(pstl_adr, 'PstCd')
                    result['debtorTownName'] = self._find_text(pstl_adr, 'TwnNm')
                    result['debtorCountrySubDivision'] = self._find_text(pstl_adr, 'CtrySubDvsn')
                    result['debtorCountry'] = self._find_text(pstl_adr, 'Ctry')
                    result['payerAddress'] = result['debtorStreetName']

                # Organisation ID (ABN/ACN)
                org_id = self._find(dbtr, 'Id/OrgId/Othr')
                if org_id is not None:
                    result['debtorOrgId'] = self._find_text(org_id, 'Id')
                    result['debtorOrgIdScheme'] = self._find_text(org_id, 'SchmeNm/Cd')
                    result['debtorOrgIdIssuer'] = self._find_text(org_id, 'Issr')

                # Contact Details
                ctct = self._find(dbtr, 'CtctDtls')
                if ctct is not None:
                    result['debtorContactName'] = self._find_text(ctct, 'Nm')
                    result['debtorContactPhone'] = self._find_text(ctct, 'PhneNb')
                    result['debtorContactEmail'] = self._find_text(ctct, 'EmailAdr')

            # Debtor Account (DbtrAcct)
            dbtr_acct = self._find(cdt_trf, 'DbtrAcct')
            if dbtr_acct is not None:
                # Try Othr/Id first (BSB + Account Number format)
                acct_id = self._find_text(dbtr_acct, 'Id/Othr/Id')
                if acct_id:
                    result['debtorAccountNumber'] = acct_id
                    result['payerAccount'] = acct_id
                    # Extract BSB from combined format (BBBBBBNNNNNNNNN)
                    if len(acct_id) >= 6:
                        result['payerBsb'] = acct_id[:6]
                # Try IBAN (rare for NPP but possible)
                iban = self._find_text(dbtr_acct, 'Id/IBAN')
                if iban:
                    result['debtorIban'] = iban

                # Account type and currency
                result['debtorAccountType'] = self._find_text(dbtr_acct, 'Tp/Cd')
                result['debtorAccountCurrency'] = self._find_text(dbtr_acct, 'Ccy')
                result['debtorAccountName'] = self._find_text(dbtr_acct, 'Nm')

                # PayID (Proxy)
                prxy = self._find(dbtr_acct, 'Prxy')
                if prxy is not None:
                    result['payerPayidType'] = self._find_text(prxy, 'Tp/Cd')
                    result['payerPayid'] = self._find_text(prxy, 'Id')

            # Debtor Agent (DbtrAgt) - Payer's Bank
            dbtr_agt = self._find(cdt_trf, 'DbtrAgt')
            if dbtr_agt is not None:
                fi_id = self._find(dbtr_agt, 'FinInstnId')
                if fi_id is not None:
                    result['debtorAgentBic'] = self._find_text(fi_id, 'BICFI')
                    result['debtorAgentName'] = self._find_text(fi_id, 'Nm')

                    # BSB (ClrSysMmbId/MmbId)
                    bsb = self._find_text(fi_id, 'ClrSysMmbId/MmbId')
                    if bsb:
                        result['debtorAgentBsb'] = bsb
                        result['payerBsb'] = result.get('payerBsb') or bsb

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
                    result['creditorStreetName'] = self._find_text(pstl_adr, 'StrtNm')
                    result['creditorBuildingNumber'] = self._find_text(pstl_adr, 'BldgNb')
                    result['creditorPostCode'] = self._find_text(pstl_adr, 'PstCd')
                    result['creditorTownName'] = self._find_text(pstl_adr, 'TwnNm')
                    result['creditorCountrySubDivision'] = self._find_text(pstl_adr, 'CtrySubDvsn')
                    result['creditorCountry'] = self._find_text(pstl_adr, 'Ctry')
                    result['payeeAddress'] = result['creditorStreetName']

                # Organisation ID (ABN/ACN)
                org_id = self._find(cdtr, 'Id/OrgId/Othr')
                if org_id is not None:
                    result['creditorOrgId'] = self._find_text(org_id, 'Id')
                    result['creditorOrgIdScheme'] = self._find_text(org_id, 'SchmeNm/Cd')
                    result['creditorOrgIdIssuer'] = self._find_text(org_id, 'Issr')

                # Contact Details
                ctct = self._find(cdtr, 'CtctDtls')
                if ctct is not None:
                    result['creditorContactName'] = self._find_text(ctct, 'Nm')
                    result['creditorContactPhone'] = self._find_text(ctct, 'PhneNb')
                    result['creditorContactEmail'] = self._find_text(ctct, 'EmailAdr')

            # Creditor Account (CdtrAcct)
            cdtr_acct = self._find(cdt_trf, 'CdtrAcct')
            if cdtr_acct is not None:
                # Try Othr/Id first (BSB + Account Number format)
                acct_id = self._find_text(cdtr_acct, 'Id/Othr/Id')
                if acct_id:
                    result['creditorAccountNumber'] = acct_id
                    result['payeeAccount'] = acct_id
                    # Extract BSB from combined format
                    if len(acct_id) >= 6:
                        result['payeeBsb'] = acct_id[:6]
                # Try IBAN
                iban = self._find_text(cdtr_acct, 'Id/IBAN')
                if iban:
                    result['creditorIban'] = iban

                # Account type and currency
                result['creditorAccountType'] = self._find_text(cdtr_acct, 'Tp/Cd')
                result['creditorAccountCurrency'] = self._find_text(cdtr_acct, 'Ccy')
                result['creditorAccountName'] = self._find_text(cdtr_acct, 'Nm')

                # PayID (Proxy)
                prxy = self._find(cdtr_acct, 'Prxy')
                if prxy is not None:
                    result['payeePayidType'] = self._find_text(prxy, 'Tp/Cd')
                    result['payeePayid'] = self._find_text(prxy, 'Id')

            # Creditor Agent (CdtrAgt) - Payee's Bank
            cdtr_agt = self._find(cdt_trf, 'CdtrAgt')
            if cdtr_agt is not None:
                fi_id = self._find(cdtr_agt, 'FinInstnId')
                if fi_id is not None:
                    result['creditorAgentBic'] = self._find_text(fi_id, 'BICFI')
                    result['creditorAgentName'] = self._find_text(fi_id, 'Nm')

                    # BSB (ClrSysMmbId/MmbId)
                    bsb = self._find_text(fi_id, 'ClrSysMmbId/MmbId')
                    if bsb:
                        result['creditorAgentBsb'] = bsb
                        result['payeeBsb'] = result.get('payeeBsb') or bsb

            # ---------------------------------------------------------------
            # PURPOSE (Purp)
            # ---------------------------------------------------------------
            result['purposeCode'] = self._find_text(cdt_trf, 'Purp/Cd')

            # ---------------------------------------------------------------
            # REMITTANCE INFORMATION (RmtInf)
            # ---------------------------------------------------------------
            rmt_inf = self._find(cdt_trf, 'RmtInf')
            if rmt_inf is not None:
                result['remittanceInfo'] = self._find_text(rmt_inf, 'Ustrd')

                # Structured reference
                strd = self._find(rmt_inf, 'Strd')
                if strd is not None:
                    # Invoice reference
                    ref_doc = self._find(strd, 'RfrdDocInf')
                    if ref_doc is not None:
                        result['referenceDocumentType'] = self._find_text(ref_doc, 'Tp/CdOrPrtry/Cd')
                        result['paymentReference'] = self._find_text(ref_doc, 'Nb')
                        result['referenceDocumentDate'] = self._find_text(ref_doc, 'RltdDt')

                    # Amount due
                    ref_amt = self._find(strd, 'RfrdDocAmt')
                    if ref_amt is not None:
                        due_amt = self._find(ref_amt, 'DuePyblAmt')
                        if due_amt is not None:
                            result['amountDue'] = due_amt.text
                            result['amountDueCurrency'] = due_amt.get('Ccy')

        return result


# =============================================================================
# NPP ISO 20022 PARSER (inherits from Pacs008Parser)
# =============================================================================

# Use conditional inheritance pattern for backward compatibility
_NppParserBase = Pacs008Parser if ISO20022_BASE_AVAILABLE else object


class NppISO20022Parser(_NppParserBase):
    """NPP ISO 20022 pacs.008 parser with Australian usage guidelines.

    Inherits from Pacs008Parser and adds NPP-specific processing:
    - BSB (Bank-State-Branch) extraction (AUBSB scheme)
    - PayID alternative addressing support
    - Australian-specific clearing system identification

    ISO 20022 Version: pacs.008.001.08
    Usage Guidelines: Australian NPP (New Payments Platform)

    Inheritance Hierarchy:
        BaseISO20022Parser -> Pacs008Parser -> NppISO20022Parser
    """

    # NPP-specific constants
    CLEARING_SYSTEM = "AUBSB"  # Australian BSB system
    DEFAULT_CURRENCY = "AUD"
    MESSAGE_TYPE = "NPP"

    def __init__(self):
        """Initialize NPP parser."""
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse NPP ISO 20022 pacs.008 message.

        Uses inherited pacs.008 parsing from Pacs008Parser and adds
        NPP-specific fields.
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

        # Add NPP-specific fields
        result['isNpp'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM

        return result

    def _parse_standalone(self, raw_content: str) -> Dict[str, Any]:
        """Standalone parsing when base class not available."""
        legacy_parser = NppXmlParser()
        return legacy_parser.parse(raw_content)


class NppExtractor(BaseExtractor):
    """Extractor for Australia NPP instant payment messages.

    ISO 20022 INHERITANCE:
        NPP inherits from pacs.008 (FI to FI Customer Credit Transfer).
        The NppISO20022Parser inherits from Pacs008Parser.
        Uses Australian NPP (New Payments Platform) usage guidelines.

    Format Support:
        1. ISO 20022 XML (pacs.008.001.08) - Current standard

    NPP-Specific Elements:
        - BSB (6 digits) identifies the bank/branch
        - Account Number (9 digits)
        - PayID for alias-based addressing (email, phone, ABN)
        - Clearing system: AUBSB (Australian BSB) / NPPA

    Database Tables:
        - Bronze: bronze.raw_payment_messages
        - Silver: silver.stg_npp
        - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_npp

    Inheritance Hierarchy:
        BaseExtractor -> NppExtractor
        (Parser: Pacs008Parser -> NppISO20022Parser)
    """

    MESSAGE_TYPE = "NPP"
    SILVER_TABLE = "stg_iso20022_pacs008"  # Shared ISO 20022 pacs.008 table
    DEFAULT_CURRENCY = "AUD"
    CLEARING_SYSTEM = "AUBSB"

    def __init__(self):
        """Initialize NPP extractor with ISO 20022 parser."""
        self.iso20022_parser = NppISO20022Parser()
        self.legacy_parser = NppXmlParser()
        self.parser = self.iso20022_parser

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw NPP content.

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
        """Extract all Silver layer fields from NPP message.

        This method maps to ALL columns in silver.stg_npp table.
        """
        trunc = self.trunc

        # Parse content if needed
        if isinstance(msg_content, str):
            msg_content = self.parser.parse(msg_content)

        # Extract values with proper fallbacks for None
        payer_name = msg_content.get('payerName') or msg_content.get('debtorName')
        payer_account = msg_content.get('payerAccount') or msg_content.get('debtorAccountNumber')
        payer_bsb = msg_content.get('payerBsb') or msg_content.get('debtorAgentBsb')

        payee_name = msg_content.get('payeeName') or msg_content.get('creditorName')
        payee_account = msg_content.get('payeeAccount') or msg_content.get('creditorAccountNumber')
        payee_bsb = msg_content.get('payeeBsb') or msg_content.get('creditorAgentBsb')

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'NPP',
            'payment_id': trunc(msg_content.get('paymentId') or msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'AUD',

            # Payer (Debtor)
            'payer_bsb': trunc(payer_bsb, 6),
            'payer_account': trunc(payer_account, 34),
            'payer_name': trunc(payer_name, 140),
            'payer_payid': trunc(msg_content.get('payerPayid'), 256),
            'payer_payid_type': trunc(msg_content.get('payerPayidType'), 10),

            # Payee (Creditor)
            'payee_bsb': trunc(payee_bsb, 6),
            'payee_account': trunc(payee_account, 34),
            'payee_name': trunc(payee_name, 140),
            'payee_payid': trunc(msg_content.get('payeePayid'), 256),
            'payee_payid_type': trunc(msg_content.get('payeePayidType'), 10),

            # Payment Details
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'payment_reference': trunc(msg_content.get('paymentReference'), 35),
            'remittance_info': msg_content.get('remittanceInfo'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'payment_id', 'creation_date_time',
            'amount', 'currency',
            'payer_bsb', 'payer_account', 'payer_name',
            'payer_payid', 'payer_payid_type',
            'payee_bsb', 'payee_account', 'payee_name',
            'payee_payid', 'payee_payid_type',
            'end_to_end_id', 'payment_reference', 'remittance_info',
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
        """Extract Gold layer entities from NPP Silver record.

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
                country='AU',
            ))

        # Payee Party (Creditor)
        if silver_data.get('payee_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='AU',
            ))

        # Payer Account
        if silver_data.get('payer_account') or silver_data.get('payer_payid'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payer_account') or silver_data.get('payer_payid'),
                role="DEBTOR",
                account_type='CACC',
                currency='AUD',
            ))

        # Payee Account
        if silver_data.get('payee_account') or silver_data.get('payee_payid'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payee_account') or silver_data.get('payee_payid'),
                role="CREDITOR",
                account_type='CACC',
                currency='AUD',
            ))

        # Payer Bank (by BSB)
        if silver_data.get('payer_bsb'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=silver_data.get('payer_bsb'),
                clearing_system='AUBSB',  # Australian BSB
                country='AU',
            ))

        # Payee Bank (by BSB)
        if silver_data.get('payee_bsb'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=silver_data.get('payee_bsb'),
                clearing_system='AUBSB',
                country='AU',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('NPP', NppExtractor())
ExtractorRegistry.register('npp', NppExtractor())
ExtractorRegistry.register('OSKO', NppExtractor())
ExtractorRegistry.register('osko', NppExtractor())
ExtractorRegistry.register('AU_NPP', NppExtractor())
