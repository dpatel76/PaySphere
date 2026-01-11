"""Base ISO 20022 XML Parser with common utilities.

This module provides the foundational XML parsing capabilities shared across
all ISO 20022 message types (pacs.008, pacs.009, pain.001, camt.053, etc.).

All ISO 20022-based payment systems (FEDWIRE, CHIPS, CHAPS, TARGET2, SEPA, etc.)
inherit from parsers that extend this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime
import xml.etree.ElementTree as ET
import re
import json
import logging

logger = logging.getLogger(__name__)


class BaseISO20022Parser(ABC):
    """Base parser for all ISO 20022 XML messages.

    Provides common XML navigation, namespace handling, and element extraction
    methods used across all ISO 20022 message types.

    Subclasses implement format-specific parsing logic while leveraging these
    shared utilities.
    """

    # Regex to strip XML namespaces from tags
    NS_PATTERN = re.compile(r'\{[^}]+\}')

    # Common ISO 20022 namespaces (subclasses may add more)
    NAMESPACES = {
        'pacs008': 'urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08',
        'pacs009': 'urn:iso:std:iso:20022:tech:xsd:pacs.009.001.08',
        'pain001': 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.09',
        'camt053': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.08',
    }

    # ==========================================================================
    # XML PARSING ENTRY POINT
    # ==========================================================================

    def _parse_xml(self, xml_content: str) -> ET.Element:
        """Parse XML content and return root element.

        Handles both regular ISO 20022 XML and split transaction XML
        (wrapped in <SplitTransaction> by MessageSplitter).

        Args:
            xml_content: Raw XML string

        Returns:
            Root Element of parsed XML

        Raises:
            ValueError: If XML parsing fails
        """
        if isinstance(xml_content, dict):
            raise ValueError("Expected XML string, got dict")

        content = xml_content.strip()

        # Remove BOM if present
        if content.startswith('\ufeff'):
            content = content[1:]

        try:
            root = ET.fromstring(content)

            # Check if this is a split transaction wrapper from MessageSplitter
            if self._strip_ns(root.tag) == 'SplitTransaction':
                # Store parent context for later access
                self._split_grp_hdr = self._find(root, 'ParentGrpHdr/GrpHdr')
                self._split_pmt_inf = self._find(root, 'ParentPmtInf/PmtInf')
                # Return the actual transaction element for processing
                txn = self._find(root, 'Transaction')
                if txn is not None and len(txn) > 0:
                    return txn[0]  # Return first child (CdtTrfTxInf)
                return root
            else:
                # Regular ISO 20022 document
                self._split_grp_hdr = None
                self._split_pmt_inf = None
                return root

        except ET.ParseError as e:
            logger.error(f"Failed to parse ISO 20022 XML: {e}")
            raise ValueError(f"Invalid ISO 20022 XML: {e}")

    def _get_split_grp_hdr(self) -> Optional[ET.Element]:
        """Get GrpHdr element from split transaction context.

        When MessageSplitter splits a multi-transaction file, the GrpHdr
        is preserved in the wrapper. This method retrieves it for extraction.

        Returns:
            GrpHdr element if available, None otherwise
        """
        return getattr(self, '_split_grp_hdr', None)

    def _get_split_pmt_inf(self) -> Optional[ET.Element]:
        """Get PmtInf element from split transaction context.

        When MessageSplitter splits a multi-transaction file, the PmtInf
        (without CdtTrfTxInf children) is preserved in the wrapper.

        Returns:
            PmtInf element if available, None otherwise
        """
        return getattr(self, '_split_pmt_inf', None)

    # ==========================================================================
    # NAMESPACE HANDLING
    # ==========================================================================

    def _strip_ns(self, tag: str) -> str:
        """Remove namespace prefix from XML tag.

        Args:
            tag: XML tag potentially with namespace like '{http://...}Element'

        Returns:
            Tag without namespace prefix, e.g., 'Element'
        """
        return self.NS_PATTERN.sub('', tag)

    # ==========================================================================
    # ELEMENT NAVIGATION
    # ==========================================================================

    def _find(self, element: Optional[ET.Element], path: str) -> Optional[ET.Element]:
        """Find element by path using local names (ignoring namespaces).

        This method navigates through nested elements using a forward-slash
        separated path, matching element names without namespace prefixes.

        Args:
            element: Parent element to search from
            path: Forward-slash separated path like 'GrpHdr/MsgId'

        Returns:
            Found element or None if not found
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

    def _find_text(self, element: Optional[ET.Element], path: str) -> Optional[str]:
        """Find element text by path.

        Args:
            element: Parent element to search from
            path: Forward-slash separated path

        Returns:
            Element text content or None
        """
        elem = self._find(element, path)
        return elem.text.strip() if elem is not None and elem.text else None

    def _find_attr(self, element: Optional[ET.Element], path: str, attr: str) -> Optional[str]:
        """Find element attribute by path.

        Args:
            element: Parent element to search from
            path: Forward-slash separated path
            attr: Attribute name to retrieve

        Returns:
            Attribute value or None
        """
        elem = self._find(element, path)
        return elem.get(attr) if elem is not None else None

    def _find_all(self, element: Optional[ET.Element], path: str) -> List[ET.Element]:
        """Find all elements matching path's final component.

        Navigates to parent via path (excluding last component), then returns
        all children matching the last component.

        Args:
            element: Parent element to search from
            path: Forward-slash separated path

        Returns:
            List of matching elements (empty if none found)
        """
        if element is None:
            return []

        parts = path.split('/')
        if len(parts) == 1:
            # Single path component - search direct children
            return [child for child in element if self._strip_ns(child.tag) == parts[0]]

        # Navigate to parent, then find all children with target name
        parent_path = '/'.join(parts[:-1])
        target_name = parts[-1]
        parent = self._find(element, parent_path)

        if parent is None:
            return []

        return [child for child in parent if self._strip_ns(child.tag) == target_name]

    # ==========================================================================
    # SAFE TYPE CONVERSIONS
    # ==========================================================================

    def _safe_int(self, value: Optional[str]) -> Optional[int]:
        """Safely convert string to integer.

        Args:
            value: String value to convert

        Returns:
            Integer value or None if conversion fails
        """
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _safe_decimal(self, value: Optional[str]) -> Optional[Decimal]:
        """Safely convert string to Decimal.

        Args:
            value: String value to convert

        Returns:
            Decimal value or None if conversion fails
        """
        if value is None:
            return None
        try:
            return Decimal(value)
        except (ValueError, TypeError, ArithmeticError):
            return None

    def _safe_float(self, value: Optional[str]) -> Optional[float]:
        """Safely convert string to float.

        Args:
            value: String value to convert

        Returns:
            Float value or None if conversion fails
        """
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _safe_date(self, value: Optional[str]) -> Optional[str]:
        """Safely parse and validate ISO date string.

        Args:
            value: Date string in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)

        Returns:
            Original string if valid, None otherwise
        """
        if value is None:
            return None
        try:
            # Try parsing as date or datetime to validate
            if 'T' in value:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
            else:
                datetime.strptime(value[:10], '%Y-%m-%d')
            return value
        except (ValueError, TypeError):
            return None

    # ==========================================================================
    # COMMON ISO 20022 ELEMENT EXTRACTION
    # ==========================================================================

    def _extract_group_header(self, parent: ET.Element) -> Dict[str, Any]:
        """Extract GrpHdr (Group Header) element - common across all ISO 20022 messages.

        GrpHdr contains:
        - MsgId: Message identification
        - CreDtTm: Creation date/time
        - NbOfTxs: Number of transactions
        - TtlIntrBkSttlmAmt: Total interbank settlement amount
        - IntrBkSttlmDt: Interbank settlement date
        - SttlmInf: Settlement information
        - InstgAgt/InstdAgt: Instructing/Instructed agents

        Args:
            parent: Parent element containing GrpHdr

        Returns:
            Dict with extracted header fields
        """
        result = {}
        grp_hdr = self._find(parent, 'GrpHdr')

        if grp_hdr is None:
            return result

        # Core identification
        result['messageId'] = self._find_text(grp_hdr, 'MsgId')
        result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')
        result['numberOfTransactions'] = self._safe_int(self._find_text(grp_hdr, 'NbOfTxs'))

        # Settlement information
        result['totalInterbankSettlementAmount'] = self._safe_float(
            self._find_text(grp_hdr, 'TtlIntrBkSttlmAmt')
        )
        result['totalInterbankSettlementCurrency'] = self._find_attr(
            grp_hdr, 'TtlIntrBkSttlmAmt', 'Ccy'
        )
        result['interbankSettlementDate'] = self._find_text(grp_hdr, 'IntrBkSttlmDt')

        # Settlement method
        result['settlementMethod'] = self._find_text(grp_hdr, 'SttlmInf/SttlmMtd')
        result['clearingSystemCode'] = self._find_text(grp_hdr, 'SttlmInf/ClrSys/Cd')

        # Instructing Agent
        instg_agt = self._find(grp_hdr, 'InstgAgt')
        if instg_agt:
            result.update(self._extract_financial_institution(instg_agt, 'instructingAgent'))

        # Instructed Agent
        instd_agt = self._find(grp_hdr, 'InstdAgt')
        if instd_agt:
            result.update(self._extract_financial_institution(instd_agt, 'instructedAgent'))

        return result

    def _extract_payment_id(self, pmt_id: ET.Element) -> Dict[str, Any]:
        """Extract PmtId (Payment Identification) element.

        PmtId contains:
        - InstrId: Instruction identification
        - EndToEndId: End-to-end identification
        - TxId: Transaction identification
        - UETR: Unique End-to-End Transaction Reference

        Args:
            pmt_id: PmtId element

        Returns:
            Dict with extracted payment ID fields
        """
        if pmt_id is None:
            return {}

        return {
            'instructionId': self._find_text(pmt_id, 'InstrId'),
            'endToEndId': self._find_text(pmt_id, 'EndToEndId'),
            'transactionId': self._find_text(pmt_id, 'TxId'),
            'uetr': self._find_text(pmt_id, 'UETR'),
        }

    def _extract_payment_type_info(self, pmt_tp_inf: ET.Element) -> Dict[str, Any]:
        """Extract PmtTpInf (Payment Type Information) element.

        PmtTpInf contains:
        - InstrPrty: Instruction priority (HIGH, NORM)
        - SvcLvl/Cd: Service level code
        - LclInstrm/Cd or LclInstrm/Prtry: Local instrument
        - CtgyPurp/Cd: Category purpose

        Args:
            pmt_tp_inf: PmtTpInf element

        Returns:
            Dict with extracted payment type fields
        """
        if pmt_tp_inf is None:
            return {}

        return {
            'instructionPriority': self._find_text(pmt_tp_inf, 'InstrPrty'),
            'serviceLevelCode': self._find_text(pmt_tp_inf, 'SvcLvl/Cd'),
            'localInstrumentCode': (
                self._find_text(pmt_tp_inf, 'LclInstrm/Cd') or
                self._find_text(pmt_tp_inf, 'LclInstrm/Prtry')
            ),
            'categoryPurposeCode': self._find_text(pmt_tp_inf, 'CtgyPurp/Cd'),
        }

    def _extract_amount(self, parent: ET.Element, amount_path: str = 'IntrBkSttlmAmt') -> Dict[str, Any]:
        """Extract amount element with currency.

        Args:
            parent: Parent element containing amount
            amount_path: Path to amount element (default: IntrBkSttlmAmt)

        Returns:
            Dict with 'amount' and 'currency' keys
        """
        amt_elem = self._find(parent, amount_path)
        if amt_elem is None:
            return {'amount': None, 'currency': None}

        return {
            'amount': self._safe_float(amt_elem.text),
            'currency': amt_elem.get('Ccy'),
        }

    def _extract_party(self, party_element: ET.Element, prefix: str) -> Dict[str, Any]:
        """Extract party information (Dbtr, Cdtr, UltmtDbtr, UltmtCdtr).

        Extracts:
        - Name
        - Postal address (full structure)
        - Identification (OrgId or PrvtId)
        - Contact details

        Args:
            party_element: Party element (e.g., Dbtr, Cdtr)
            prefix: Key prefix for result dict (e.g., 'debtor', 'creditor')

        Returns:
            Dict with prefixed party fields
        """
        if party_element is None:
            return {}

        result = {}

        # Name
        result[f'{prefix}Name'] = self._find_text(party_element, 'Nm')

        # Postal Address
        pstl_adr = self._find(party_element, 'PstlAdr')
        if pstl_adr:
            result.update(self._extract_postal_address(pstl_adr, prefix))

        # Organization ID
        org_id = self._find(party_element, 'Id/OrgId')
        if org_id:
            result[f'{prefix}Lei'] = self._find_text(org_id, 'LEI')
            result[f'{prefix}OtherId'] = self._find_text(org_id, 'Othr/Id')
            result[f'{prefix}OtherIdScheme'] = self._find_text(org_id, 'Othr/SchmeNm/Cd')
            result[f'{prefix}OtherIdIssuer'] = self._find_text(org_id, 'Othr/Issr')

        # Private ID (for individuals)
        prvt_id = self._find(party_element, 'Id/PrvtId')
        if prvt_id:
            result[f'{prefix}PrivateId'] = (
                self._find_text(prvt_id, 'Othr/Id') or
                self._find_text(prvt_id, 'DtAndPlcOfBirth/BirthDt')
            )

        # Contact Details
        ctct_dtls = self._find(party_element, 'CtctDtls')
        if ctct_dtls:
            result[f'{prefix}ContactName'] = self._find_text(ctct_dtls, 'Nm')
            result[f'{prefix}ContactPhone'] = self._find_text(ctct_dtls, 'PhneNb')
            result[f'{prefix}ContactEmail'] = self._find_text(ctct_dtls, 'EmailAdr')

        return result

    def _extract_postal_address(self, pstl_adr: ET.Element, prefix: str) -> Dict[str, Any]:
        """Extract postal address element.

        Args:
            pstl_adr: PstlAdr element
            prefix: Key prefix for result dict

        Returns:
            Dict with prefixed address fields
        """
        if pstl_adr is None:
            return {}

        result = {
            f'{prefix}StreetName': self._find_text(pstl_adr, 'StrtNm'),
            f'{prefix}BuildingNumber': self._find_text(pstl_adr, 'BldgNb'),
            f'{prefix}BuildingName': self._find_text(pstl_adr, 'BldgNm'),
            f'{prefix}PostCode': self._find_text(pstl_adr, 'PstCd'),
            f'{prefix}TownName': self._find_text(pstl_adr, 'TwnNm'),
            f'{prefix}CountrySubDivision': self._find_text(pstl_adr, 'CtrySubDvsn'),
            f'{prefix}Country': self._find_text(pstl_adr, 'Ctry'),
        }

        # Address lines (multiple possible)
        adr_lines = self._find_all(pstl_adr, 'AdrLine')
        if adr_lines:
            result[f'{prefix}AddressLine1'] = adr_lines[0].text if len(adr_lines) > 0 else None
            result[f'{prefix}AddressLine2'] = adr_lines[1].text if len(adr_lines) > 1 else None

        return result

    def _extract_account(self, acct_element: ET.Element, prefix: str) -> Dict[str, Any]:
        """Extract account information (DbtrAcct, CdtrAcct).

        Extracts:
        - IBAN
        - Other account ID
        - Account type
        - Currency
        - Account name

        Args:
            acct_element: Account element (e.g., DbtrAcct, CdtrAcct)
            prefix: Key prefix for result dict (e.g., 'debtorAccount', 'creditorAccount')

        Returns:
            Dict with prefixed account fields
        """
        if acct_element is None:
            return {}

        result = {
            f'{prefix}Iban': self._find_text(acct_element, 'Id/IBAN'),
            f'{prefix}Other': self._find_text(acct_element, 'Id/Othr/Id'),
            f'{prefix}OtherScheme': self._find_text(acct_element, 'Id/Othr/SchmeNm/Cd'),
            f'{prefix}Type': self._find_text(acct_element, 'Tp/Cd'),
            f'{prefix}Currency': self._find_text(acct_element, 'Ccy'),
            f'{prefix}Name': self._find_text(acct_element, 'Nm'),
        }

        return result

    def _extract_financial_institution(self, fi_element: ET.Element, prefix: str) -> Dict[str, Any]:
        """Extract financial institution information (DbtrAgt, CdtrAgt, InstgAgt, etc.).

        Extracts:
        - BIC (BICFI)
        - LEI
        - Clearing system member ID
        - Name
        - Postal address

        Args:
            fi_element: Agent element (contains FinInstnId)
            prefix: Key prefix for result dict (e.g., 'debtorAgent', 'creditorAgent')

        Returns:
            Dict with prefixed FI fields
        """
        if fi_element is None:
            return {}

        fin_instn_id = self._find(fi_element, 'FinInstnId')
        if fin_instn_id is None:
            return {}

        result = {
            f'{prefix}Bic': self._find_text(fin_instn_id, 'BICFI'),
            f'{prefix}Lei': self._find_text(fin_instn_id, 'LEI'),
            f'{prefix}Name': self._find_text(fin_instn_id, 'Nm'),
            f'{prefix}ClearingSystemId': self._find_text(fin_instn_id, 'ClrSysMmbId/ClrSysId/Cd'),
            f'{prefix}MemberId': self._find_text(fin_instn_id, 'ClrSysMmbId/MmbId'),
        }

        # Postal address
        pstl_adr = self._find(fin_instn_id, 'PstlAdr')
        if pstl_adr:
            result.update(self._extract_postal_address(pstl_adr, prefix))

        return result

    def _extract_remittance_info(self, rmt_inf: ET.Element) -> Dict[str, Any]:
        """Extract remittance information.

        Args:
            rmt_inf: RmtInf element

        Returns:
            Dict with remittance fields
        """
        if rmt_inf is None:
            return {}

        result = {
            'remittanceUnstructured': self._find_text(rmt_inf, 'Ustrd'),
        }

        # Structured remittance
        strd = self._find(rmt_inf, 'Strd')
        if strd:
            # Referenced document
            result['referredDocumentType'] = self._find_text(strd, 'RfrdDocInf/Tp/CdOrPrtry/Cd')
            result['referredDocumentNumber'] = self._find_text(strd, 'RfrdDocInf/Nb')
            result['referredDocumentDate'] = self._find_text(strd, 'RfrdDocInf/RltdDt')

            # Referenced document amount
            result['referredDocumentAmount'] = self._safe_float(
                self._find_text(strd, 'RfrdDocAmt/DuePyblAmt')
            )
            result['referredDocumentCurrency'] = self._find_attr(
                strd, 'RfrdDocAmt/DuePyblAmt', 'Ccy'
            )

            # Creditor reference
            result['creditorReferenceType'] = self._find_text(strd, 'CdtrRefInf/Tp/CdOrPrtry/Cd')
            result['creditorReference'] = self._find_text(strd, 'CdtrRefInf/Ref')

        return result

    def _extract_regulatory_reporting(self, rgltry_rptg: ET.Element) -> Dict[str, Any]:
        """Extract regulatory reporting information.

        Args:
            rgltry_rptg: RgltryRptg element

        Returns:
            Dict with regulatory reporting fields
        """
        if rgltry_rptg is None:
            return {}

        return {
            'regulatoryReportingIndicator': self._find_text(rgltry_rptg, 'DbtCdtRptgInd'),
            'regulatoryAuthorityName': self._find_text(rgltry_rptg, 'Authrty/Nm'),
            'regulatoryAuthorityCountry': self._find_text(rgltry_rptg, 'Authrty/Ctry'),
            'regulatoryCode': self._find_text(rgltry_rptg, 'Dtls/Cd'),
            'regulatoryInfo': self._find_text(rgltry_rptg, 'Dtls/Inf'),
        }

    # ==========================================================================
    # FULL ISO PATH EXTRACTION METHODS (DOT-NOTATION)
    # ==========================================================================
    # These methods produce keys using full ISO 20022 paths with dot notation
    # e.g., 'GrpHdr.MsgId', 'PmtInf.Dbtr.Nm', 'CdtTrfTxInf.Amt.InstdAmt@Ccy'
    #
    # Key rules:
    # - Path separator: '.' (dot)
    # - Attributes: '@' suffix (e.g., 'Amt@Ccy')
    # - Arrays: '[n]' index (e.g., 'AdrLine[0]')
    # - Use ISO element names: Nm, Ctry, BICFI (not name, country, bic)
    # ==========================================================================

    def _make_key(self, *path_parts: str) -> str:
        """Build full ISO path key from parts.

        Examples:
            _make_key('GrpHdr', 'MsgId') -> 'GrpHdr.MsgId'
            _make_key('PmtInf', 'Dbtr', 'Nm') -> 'PmtInf.Dbtr.Nm'

        Args:
            *path_parts: Variable path segments

        Returns:
            Dot-separated ISO path key
        """
        return '.'.join(p for p in path_parts if p)

    def _extract_party_iso_path(self, party_element: ET.Element, path_prefix: str) -> Dict[str, Any]:
        """Extract party information using full ISO path keys.

        Args:
            party_element: Party element (e.g., Dbtr, Cdtr)
            path_prefix: ISO path prefix (e.g., 'PmtInf.Dbtr', 'CdtTrfTxInf.Cdtr')

        Returns:
            Dict with full ISO path keys like 'PmtInf.Dbtr.Nm', 'PmtInf.Dbtr.PstlAdr.Ctry'
        """
        if party_element is None:
            return {}

        result = {}

        # Name
        result[self._make_key(path_prefix, 'Nm')] = self._find_text(party_element, 'Nm')

        # Postal Address
        pstl_adr = self._find(party_element, 'PstlAdr')
        if pstl_adr:
            addr_prefix = self._make_key(path_prefix, 'PstlAdr')
            result[self._make_key(addr_prefix, 'StrtNm')] = self._find_text(pstl_adr, 'StrtNm')
            result[self._make_key(addr_prefix, 'BldgNb')] = self._find_text(pstl_adr, 'BldgNb')
            result[self._make_key(addr_prefix, 'BldgNm')] = self._find_text(pstl_adr, 'BldgNm')
            result[self._make_key(addr_prefix, 'PstCd')] = self._find_text(pstl_adr, 'PstCd')
            result[self._make_key(addr_prefix, 'TwnNm')] = self._find_text(pstl_adr, 'TwnNm')
            result[self._make_key(addr_prefix, 'CtrySubDvsn')] = self._find_text(pstl_adr, 'CtrySubDvsn')
            result[self._make_key(addr_prefix, 'Ctry')] = self._find_text(pstl_adr, 'Ctry')

            # Address lines (with array index)
            adr_lines = self._find_all(pstl_adr, 'AdrLine')
            for i, line in enumerate(adr_lines):
                result[f'{addr_prefix}.AdrLine[{i}]'] = line.text if line.text else None

        # Organization ID
        org_id = self._find(party_element, 'Id/OrgId')
        if org_id:
            id_prefix = self._make_key(path_prefix, 'Id', 'OrgId')
            result[self._make_key(id_prefix, 'LEI')] = self._find_text(org_id, 'LEI')
            result[self._make_key(id_prefix, 'AnyBIC')] = self._find_text(org_id, 'AnyBIC')
            result[self._make_key(id_prefix, 'Othr', 'Id')] = self._find_text(org_id, 'Othr/Id')
            result[self._make_key(id_prefix, 'Othr', 'SchmeNm', 'Cd')] = self._find_text(org_id, 'Othr/SchmeNm/Cd')
            result[self._make_key(id_prefix, 'Othr', 'Issr')] = self._find_text(org_id, 'Othr/Issr')

        # Private ID (for individuals)
        prvt_id = self._find(party_element, 'Id/PrvtId')
        if prvt_id:
            id_prefix = self._make_key(path_prefix, 'Id', 'PrvtId')
            result[self._make_key(id_prefix, 'Othr', 'Id')] = self._find_text(prvt_id, 'Othr/Id')
            result[self._make_key(id_prefix, 'DtAndPlcOfBirth', 'BirthDt')] = self._find_text(
                prvt_id, 'DtAndPlcOfBirth/BirthDt'
            )
            result[self._make_key(id_prefix, 'DtAndPlcOfBirth', 'CityOfBirth')] = self._find_text(
                prvt_id, 'DtAndPlcOfBirth/CityOfBirth'
            )
            result[self._make_key(id_prefix, 'DtAndPlcOfBirth', 'CtryOfBirth')] = self._find_text(
                prvt_id, 'DtAndPlcOfBirth/CtryOfBirth'
            )

        # Contact Details
        ctct_dtls = self._find(party_element, 'CtctDtls')
        if ctct_dtls:
            ctct_prefix = self._make_key(path_prefix, 'CtctDtls')
            result[self._make_key(ctct_prefix, 'Nm')] = self._find_text(ctct_dtls, 'Nm')
            result[self._make_key(ctct_prefix, 'PhneNb')] = self._find_text(ctct_dtls, 'PhneNb')
            result[self._make_key(ctct_prefix, 'EmailAdr')] = self._find_text(ctct_dtls, 'EmailAdr')

        return result

    def _extract_account_iso_path(self, acct_element: ET.Element, path_prefix: str) -> Dict[str, Any]:
        """Extract account information using full ISO path keys.

        Args:
            acct_element: Account element (e.g., DbtrAcct, CdtrAcct)
            path_prefix: ISO path prefix (e.g., 'PmtInf.DbtrAcct', 'CdtTrfTxInf.CdtrAcct')

        Returns:
            Dict with full ISO path keys like 'PmtInf.DbtrAcct.Id.IBAN'
        """
        if acct_element is None:
            return {}

        result = {
            self._make_key(path_prefix, 'Id', 'IBAN'): self._find_text(acct_element, 'Id/IBAN'),
            self._make_key(path_prefix, 'Id', 'Othr', 'Id'): self._find_text(acct_element, 'Id/Othr/Id'),
            self._make_key(path_prefix, 'Id', 'Othr', 'SchmeNm', 'Cd'): self._find_text(
                acct_element, 'Id/Othr/SchmeNm/Cd'
            ),
            self._make_key(path_prefix, 'Tp', 'Cd'): self._find_text(acct_element, 'Tp/Cd'),
            self._make_key(path_prefix, 'Ccy'): self._find_text(acct_element, 'Ccy'),
            self._make_key(path_prefix, 'Nm'): self._find_text(acct_element, 'Nm'),
        }

        return result

    def _extract_financial_institution_iso_path(
        self, fi_element: ET.Element, path_prefix: str
    ) -> Dict[str, Any]:
        """Extract financial institution information using full ISO path keys.

        Args:
            fi_element: Agent element (contains FinInstnId)
            path_prefix: ISO path prefix (e.g., 'PmtInf.DbtrAgt', 'CdtTrfTxInf.CdtrAgt')

        Returns:
            Dict with full ISO path keys like 'PmtInf.DbtrAgt.FinInstnId.BICFI'
        """
        if fi_element is None:
            return {}

        fin_instn_id = self._find(fi_element, 'FinInstnId')
        if fin_instn_id is None:
            return {}

        fi_prefix = self._make_key(path_prefix, 'FinInstnId')

        result = {
            self._make_key(fi_prefix, 'BICFI'): self._find_text(fin_instn_id, 'BICFI'),
            self._make_key(fi_prefix, 'LEI'): self._find_text(fin_instn_id, 'LEI'),
            self._make_key(fi_prefix, 'Nm'): self._find_text(fin_instn_id, 'Nm'),
            self._make_key(fi_prefix, 'ClrSysMmbId', 'ClrSysId', 'Cd'): self._find_text(
                fin_instn_id, 'ClrSysMmbId/ClrSysId/Cd'
            ),
            self._make_key(fi_prefix, 'ClrSysMmbId', 'MmbId'): self._find_text(
                fin_instn_id, 'ClrSysMmbId/MmbId'
            ),
        }

        # Postal address
        pstl_adr = self._find(fin_instn_id, 'PstlAdr')
        if pstl_adr:
            addr_prefix = self._make_key(fi_prefix, 'PstlAdr')
            result[self._make_key(addr_prefix, 'StrtNm')] = self._find_text(pstl_adr, 'StrtNm')
            result[self._make_key(addr_prefix, 'PstCd')] = self._find_text(pstl_adr, 'PstCd')
            result[self._make_key(addr_prefix, 'TwnNm')] = self._find_text(pstl_adr, 'TwnNm')
            result[self._make_key(addr_prefix, 'Ctry')] = self._find_text(pstl_adr, 'Ctry')

            # Address lines
            adr_lines = self._find_all(pstl_adr, 'AdrLine')
            for i, line in enumerate(adr_lines):
                result[f'{addr_prefix}.AdrLine[{i}]'] = line.text if line.text else None

        return result

    def _extract_amount_iso_path(
        self, parent: ET.Element, amount_path: str, path_prefix: str
    ) -> Dict[str, Any]:
        """Extract amount element with currency using full ISO path keys.

        Args:
            parent: Parent element containing amount
            amount_path: Path to amount element (e.g., 'IntrBkSttlmAmt', 'InstdAmt')
            path_prefix: ISO path prefix (e.g., 'CdtTrfTxInf')

        Returns:
            Dict with keys like 'CdtTrfTxInf.IntrBkSttlmAmt', 'CdtTrfTxInf.IntrBkSttlmAmt@Ccy'
        """
        amt_elem = self._find(parent, amount_path)
        if amt_elem is None:
            return {}

        key_base = self._make_key(path_prefix, amount_path)
        return {
            key_base: self._safe_float(amt_elem.text),
            f'{key_base}@Ccy': amt_elem.get('Ccy'),
        }

    def _extract_group_header_iso_path(self, parent: ET.Element) -> Dict[str, Any]:
        """Extract GrpHdr using full ISO path keys.

        Args:
            parent: Parent element containing GrpHdr

        Returns:
            Dict with keys like 'GrpHdr.MsgId', 'GrpHdr.CreDtTm'
        """
        result = {}
        grp_hdr = self._find(parent, 'GrpHdr')

        if grp_hdr is None:
            return result

        # Core identification
        result['GrpHdr.MsgId'] = self._find_text(grp_hdr, 'MsgId')
        result['GrpHdr.CreDtTm'] = self._find_text(grp_hdr, 'CreDtTm')
        result['GrpHdr.NbOfTxs'] = self._safe_int(self._find_text(grp_hdr, 'NbOfTxs'))
        result['GrpHdr.CtrlSum'] = self._safe_float(self._find_text(grp_hdr, 'CtrlSum'))

        # Batch booking
        result['GrpHdr.BtchBookg'] = self._find_text(grp_hdr, 'BtchBookg')

        # Total interbank settlement amount
        ttl_amt = self._find(grp_hdr, 'TtlIntrBkSttlmAmt')
        if ttl_amt is not None:
            result['GrpHdr.TtlIntrBkSttlmAmt'] = self._safe_float(ttl_amt.text)
            result['GrpHdr.TtlIntrBkSttlmAmt@Ccy'] = ttl_amt.get('Ccy')

        result['GrpHdr.IntrBkSttlmDt'] = self._find_text(grp_hdr, 'IntrBkSttlmDt')

        # Settlement info
        result['GrpHdr.SttlmInf.SttlmMtd'] = self._find_text(grp_hdr, 'SttlmInf/SttlmMtd')
        result['GrpHdr.SttlmInf.ClrSys.Cd'] = self._find_text(grp_hdr, 'SttlmInf/ClrSys/Cd')

        # Initiating Party (pain.001)
        initg_pty = self._find(grp_hdr, 'InitgPty')
        if initg_pty:
            result.update(self._extract_party_iso_path(initg_pty, 'GrpHdr.InitgPty'))

        # Instructing Agent (pacs.008)
        instg_agt = self._find(grp_hdr, 'InstgAgt')
        if instg_agt:
            result.update(self._extract_financial_institution_iso_path(instg_agt, 'GrpHdr.InstgAgt'))

        # Instructed Agent (pacs.008)
        instd_agt = self._find(grp_hdr, 'InstdAgt')
        if instd_agt:
            result.update(self._extract_financial_institution_iso_path(instd_agt, 'GrpHdr.InstdAgt'))

        return result

    def _extract_payment_id_iso_path(self, pmt_id: ET.Element, path_prefix: str) -> Dict[str, Any]:
        """Extract PmtId using full ISO path keys.

        Args:
            pmt_id: PmtId element
            path_prefix: ISO path prefix (e.g., 'CdtTrfTxInf.PmtId')

        Returns:
            Dict with keys like 'CdtTrfTxInf.PmtId.InstrId', 'CdtTrfTxInf.PmtId.EndToEndId'
        """
        if pmt_id is None:
            return {}

        return {
            self._make_key(path_prefix, 'InstrId'): self._find_text(pmt_id, 'InstrId'),
            self._make_key(path_prefix, 'EndToEndId'): self._find_text(pmt_id, 'EndToEndId'),
            self._make_key(path_prefix, 'TxId'): self._find_text(pmt_id, 'TxId'),
            self._make_key(path_prefix, 'UETR'): self._find_text(pmt_id, 'UETR'),
            self._make_key(path_prefix, 'ClrSysRef'): self._find_text(pmt_id, 'ClrSysRef'),
        }

    def _extract_payment_type_info_iso_path(
        self, pmt_tp_inf: ET.Element, path_prefix: str
    ) -> Dict[str, Any]:
        """Extract PmtTpInf using full ISO path keys.

        Args:
            pmt_tp_inf: PmtTpInf element
            path_prefix: ISO path prefix (e.g., 'PmtInf.PmtTpInf', 'CdtTrfTxInf.PmtTpInf')

        Returns:
            Dict with keys like 'PmtInf.PmtTpInf.InstrPrty', 'PmtInf.PmtTpInf.SvcLvl.Cd'
        """
        if pmt_tp_inf is None:
            return {}

        return {
            self._make_key(path_prefix, 'InstrPrty'): self._find_text(pmt_tp_inf, 'InstrPrty'),
            self._make_key(path_prefix, 'SvcLvl', 'Cd'): self._find_text(pmt_tp_inf, 'SvcLvl/Cd'),
            self._make_key(path_prefix, 'SvcLvl', 'Prtry'): self._find_text(pmt_tp_inf, 'SvcLvl/Prtry'),
            self._make_key(path_prefix, 'LclInstrm', 'Cd'): self._find_text(pmt_tp_inf, 'LclInstrm/Cd'),
            self._make_key(path_prefix, 'LclInstrm', 'Prtry'): self._find_text(pmt_tp_inf, 'LclInstrm/Prtry'),
            self._make_key(path_prefix, 'SeqTp'): self._find_text(pmt_tp_inf, 'SeqTp'),
            self._make_key(path_prefix, 'CtgyPurp', 'Cd'): self._find_text(pmt_tp_inf, 'CtgyPurp/Cd'),
        }

    def _extract_remittance_info_iso_path(
        self, rmt_inf: ET.Element, path_prefix: str
    ) -> Dict[str, Any]:
        """Extract RmtInf using full ISO path keys.

        Args:
            rmt_inf: RmtInf element
            path_prefix: ISO path prefix (e.g., 'CdtTrfTxInf.RmtInf')

        Returns:
            Dict with keys like 'CdtTrfTxInf.RmtInf.Ustrd', 'CdtTrfTxInf.RmtInf.Strd.CdtrRefInf.Ref'
        """
        if rmt_inf is None:
            return {}

        result = {
            self._make_key(path_prefix, 'Ustrd'): self._find_text(rmt_inf, 'Ustrd'),
        }

        # Structured remittance
        strd = self._find(rmt_inf, 'Strd')
        if strd:
            strd_prefix = self._make_key(path_prefix, 'Strd')

            # Referenced document
            result[self._make_key(strd_prefix, 'RfrdDocInf', 'Tp', 'CdOrPrtry', 'Cd')] = self._find_text(
                strd, 'RfrdDocInf/Tp/CdOrPrtry/Cd'
            )
            result[self._make_key(strd_prefix, 'RfrdDocInf', 'Nb')] = self._find_text(
                strd, 'RfrdDocInf/Nb'
            )
            result[self._make_key(strd_prefix, 'RfrdDocInf', 'RltdDt')] = self._find_text(
                strd, 'RfrdDocInf/RltdDt'
            )

            # Creditor reference
            result[self._make_key(strd_prefix, 'CdtrRefInf', 'Tp', 'CdOrPrtry', 'Cd')] = self._find_text(
                strd, 'CdtrRefInf/Tp/CdOrPrtry/Cd'
            )
            result[self._make_key(strd_prefix, 'CdtrRefInf', 'Ref')] = self._find_text(
                strd, 'CdtrRefInf/Ref'
            )

        return result

    def _extract_regulatory_reporting_iso_path(
        self, rgltry_rptg: ET.Element, path_prefix: str
    ) -> Dict[str, Any]:
        """Extract RgltryRptg using full ISO path keys.

        Args:
            rgltry_rptg: RgltryRptg element
            path_prefix: ISO path prefix (e.g., 'CdtTrfTxInf.RgltryRptg')

        Returns:
            Dict with keys like 'CdtTrfTxInf.RgltryRptg.DbtCdtRptgInd'
        """
        if rgltry_rptg is None:
            return {}

        return {
            self._make_key(path_prefix, 'DbtCdtRptgInd'): self._find_text(rgltry_rptg, 'DbtCdtRptgInd'),
            self._make_key(path_prefix, 'Authrty', 'Nm'): self._find_text(rgltry_rptg, 'Authrty/Nm'),
            self._make_key(path_prefix, 'Authrty', 'Ctry'): self._find_text(rgltry_rptg, 'Authrty/Ctry'),
            self._make_key(path_prefix, 'Dtls', 'Cd'): self._find_text(rgltry_rptg, 'Dtls/Cd'),
            self._make_key(path_prefix, 'Dtls', 'Inf'): self._find_text(rgltry_rptg, 'Dtls/Inf'),
        }

    # ==========================================================================
    # ABSTRACT METHOD - SUBCLASSES MUST IMPLEMENT
    # ==========================================================================

    @abstractmethod
    def parse(self, content: str) -> Dict[str, Any]:
        """Parse message content into standardized dictionary.

        Args:
            content: Raw message content (XML string)

        Returns:
            Dict with all extracted fields using standardized key names
        """
        pass

    def parse_iso_paths(self, content: str) -> Dict[str, Any]:
        """Parse message content using full ISO path key naming.

        This method should be overridden by subclasses to provide
        full ISO path dot-notation keys in the result.

        Args:
            content: Raw message content (XML string)

        Returns:
            Dict with all extracted fields using full ISO path keys
            (e.g., 'GrpHdr.MsgId', 'PmtInf.Dbtr.Nm')
        """
        # Default implementation - subclasses should override
        return self.parse(content)
