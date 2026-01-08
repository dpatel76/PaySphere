"""Fedwire (US RTGS) Extractor.

IMPORTANT: As of March 2025, Fedwire Funds Service migrated to ISO 20022 messaging.
The legacy FAIM (Fedwire Application Interface for Messages) format is deprecated.

Current Fedwire ISO 20022 messages:
- pacs.008.001.08: FI to FI Customer Credit Transfer (replaces FAIM customer payments)
- pacs.009.001.08: FI Credit Transfer (replaces FAIM bank-to-bank transfers)
- pacs.004.001.09: Payment Return
- pacs.002.001.10: Payment Status Report

This extractor supports BOTH formats for backward compatibility:
1. ISO 20022 XML (pacs.008/pacs.009) - Current standard as of March 2025
2. Legacy FAIM tag-value format - For historical data processing

ISO 20022 INHERITANCE:
    Fedwire inherits from pacs.008 (FI to FI Customer Credit Transfer) base message.
    The FedwireISO20022Parser class inherits from Pacs008Parser for ISO 20022 parsing.
    This ensures compliance with the Federal Reserve's ISO 20022 usage guidelines.

Usage Guidelines Reference:
    - https://www.frbservices.org/resources/financial-services/wires/iso-20022-implementation-center
    - ISO 20022 version: pacs.008.001.08

Fedwire-Specific Elements (beyond standard pacs.008):
    - IMAD (Input Message Accountability Data) - Unique identifier format YYYYMMDDSSSSSSSSNNNNNN
    - ABA Routing Numbers - US clearing system identifier (9 digits)
    - FAIM business function codes - CTR, BTR, DRC, etc.
    - US-specific address format (State codes, ZIP codes)
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

# Import ISO 20022 base classes for inheritance
try:
    from ..iso20022 import Pacs008Parser, Pacs008Extractor
    ISO20022_BASE_AVAILABLE = True
except ImportError:
    ISO20022_BASE_AVAILABLE = False

logger = logging.getLogger(__name__)


# Base class for Fedwire ISO 20022 parser
_FedwireParserBase = Pacs008Parser if ISO20022_BASE_AVAILABLE else object


class FedwireISO20022Parser(_FedwireParserBase):
    """Parser for Fedwire ISO 20022 pacs.008/pacs.009 messages (current standard as of March 2025).

    Fedwire uses standard ISO 20022 messages with Federal Reserve-specific usage guidelines.
    Inherits from Pacs008Parser to reuse common pacs.008 parsing logic.

    Key message types:
    - pacs.008: FI to FI Customer Credit Transfer
    - pacs.009: FI Credit Transfer (interbank)

    Fedwire-Specific Additions (beyond base pacs.008):
    - Maps MsgId to IMAD (Fedwire unique identifier)
    - Default currency is always USD
    - Sender/Receiver FI from InstgAgt/InstdAgt
    - ABA routing numbers via ClrSysMmbId/MmbId

    Inheritance: Pacs008Parser -> FedwireISO20022Parser
    """

    # Clearing system identifier for Fedwire
    CLEARING_SYSTEM = "USABA"
    DEFAULT_CURRENCY = "USD"

    # Fedwire-specific namespace pattern (for standalone use if base not available)
    NS_PATTERN = re.compile(r'\{[^}]+\}')

    def _strip_ns(self, tag: str) -> str:
        """Remove namespace from XML tag."""
        if ISO20022_BASE_AVAILABLE:
            return super()._strip_ns(tag)
        return self.NS_PATTERN.sub('', tag)

    def _find(self, element: ET.Element, path: str) -> Optional[ET.Element]:
        """Find element using local names (ignoring namespaces)."""
        if ISO20022_BASE_AVAILABLE:
            return super()._find(element, path)
        # Fallback implementation for standalone use
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
        if ISO20022_BASE_AVAILABLE:
            return super()._find_text(element, path)
        elem = self._find(element, path)
        return elem.text if elem is not None else None

    def _find_attr(self, element: ET.Element, path: str, attr: str) -> Optional[str]:
        """Find element attribute."""
        if ISO20022_BASE_AVAILABLE:
            return super()._find_attr(element, path, attr)
        elem = self._find(element, path)
        return elem.get(attr) if elem is not None else None

    def parse(self, xml_content: str) -> Dict[str, Any]:
        """Parse Fedwire ISO 20022 pacs.008 or pacs.009 message.

        Uses base Pacs008Parser.parse() for standard pacs.008 extraction,
        then adds Fedwire-specific post-processing.
        """
        try:
            if xml_content.startswith('\ufeff'):
                xml_content = xml_content[1:]
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.error(f"Failed to parse Fedwire ISO 20022 XML: {e}")
            raise ValueError(f"Invalid XML: {e}")

        # Determine message type (pacs.008 or pacs.009)
        fi_transfer = self._find(root, 'FIToFICstmrCdtTrf')  # pacs.008
        if fi_transfer is None:
            fi_transfer = self._find(root, 'FICdtTrf')  # pacs.009
            if fi_transfer is None:
                # Check if root is the message element itself
                root_tag = self._strip_ns(root.tag)
                if root_tag == 'FIToFICstmrCdtTrf':
                    fi_transfer = root
                elif root_tag == 'FICdtTrf':
                    fi_transfer = root

        if fi_transfer is None:
            raise ValueError("Cannot find FIToFICstmrCdtTrf or FICdtTrf element")

        return self._parse_transfer(fi_transfer)

    def _parse_transfer(self, fi_transfer: ET.Element) -> Dict[str, Any]:
        """Parse credit transfer element with Fedwire-specific mappings.

        Extends standard pacs.008 parsing with Fedwire-specific fields:
        - IMAD mapping from MsgId
        - Sender/Receiver FI from InstgAgt/InstdAgt
        - US-specific address handling
        """
        result = {
            'currency': 'USD',  # Fedwire is always USD
            'isISO20022': True,
            'clearingSystem': 'FEDWIRE',
        }

        # Group Header with Fedwire-specific field mapping
        grp_hdr = self._find(fi_transfer, 'GrpHdr')
        if grp_hdr is not None:
            # Map MsgId to IMAD (Fedwire-specific identifier)
            result['imad'] = self._find_text(grp_hdr, 'MsgId')
            result['messageId'] = result['imad']  # Also set standard field
            result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')
            result['settlementDate'] = self._find_text(grp_hdr, 'IntrBkSttlmDt')
            result['settlementMethod'] = self._find_text(grp_hdr, 'SttlmInf/SttlmMtd')

            # Instructing Agent (Sender FI) - Fedwire uses this for the sending bank
            instg_agt = self._find(grp_hdr, 'InstgAgt/FinInstnId')
            if instg_agt is not None:
                result['sender'] = {
                    'bic': self._find_text(instg_agt, 'BICFI'),
                    'routingNumber': self._find_text(instg_agt, 'ClrSysMmbId/MmbId'),
                    'name': self._find_text(instg_agt, 'Nm'),
                    'lei': self._find_text(instg_agt, 'LEI'),
                    'address': self._parse_address(instg_agt),
                }

            # Instructed Agent (Receiver FI) - Fedwire uses this for the receiving bank
            instd_agt = self._find(grp_hdr, 'InstdAgt/FinInstnId')
            if instd_agt is not None:
                result['receiver'] = {
                    'bic': self._find_text(instd_agt, 'BICFI'),
                    'routingNumber': self._find_text(instd_agt, 'ClrSysMmbId/MmbId'),
                    'name': self._find_text(instd_agt, 'Nm'),
                    'lei': self._find_text(instd_agt, 'LEI'),
                    'address': self._parse_address(instd_agt),
                }

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
            result['instructionId'] = self._find_text(pmt_id, 'InstrId')
            result['endToEndId'] = self._find_text(pmt_id, 'EndToEndId')
            result['transactionId'] = self._find_text(pmt_id, 'TxId')
            result['uetr'] = self._find_text(pmt_id, 'UETR')
            result['senderReference'] = self._find_text(pmt_id, 'EndToEndId')  # Map to sender reference

        # Payment Type Info
        pmt_tp = self._find(cdt_trf, 'PmtTpInf')
        if pmt_tp is not None:
            result['businessFunctionCode'] = self._find_text(pmt_tp, 'LclInstrm/Prtry')
            result['typeCode'] = self._find_text(pmt_tp, 'SvcLvl/Cd')

        # Amount (always USD for Fedwire)
        amt_elem = self._find(cdt_trf, 'IntrBkSttlmAmt')
        if amt_elem is not None:
            try:
                result['amount'] = float(amt_elem.text) if amt_elem.text else None
            except ValueError:
                result['amount'] = None
            result['currency'] = amt_elem.get('Ccy', 'USD')

        # Instructed Amount
        instd_amt = self._find(cdt_trf, 'InstdAmt')
        if instd_amt is not None:
            try:
                result['instructedAmount'] = float(instd_amt.text) if instd_amt.text else None
            except ValueError:
                result['instructedAmount'] = None
            result['instructedCurrency'] = instd_amt.get('Ccy', 'USD')

        # Debtor Agent (Originator's Bank)
        dbtr_agt = self._find(cdt_trf, 'DbtrAgt/FinInstnId')
        if dbtr_agt is not None:
            dbtr_agt_bic = self._find_text(dbtr_agt, 'BICFI')
            dbtr_agt_routing = self._find_text(dbtr_agt, 'ClrSysMmbId/MmbId')
            dbtr_agt_name = self._find_text(dbtr_agt, 'Nm')
            dbtr_agt_clr_sys = self._find_text(dbtr_agt, 'ClrSysMmbId/ClrSysId/Cd')
            # Fedwire-specific naming
            result['originatorFi'] = {
                'bic': dbtr_agt_bic,
                'routingNumber': dbtr_agt_routing,
                'name': dbtr_agt_name,
            }
            # Standard ISO 20022 flat keys for DynamicMapper inheritance
            result['debtorAgentBic'] = dbtr_agt_bic
            result['debtorAgentName'] = dbtr_agt_name
            result['debtorAgentMemberId'] = dbtr_agt_routing
            result['debtorAgentClearingSystemId'] = dbtr_agt_clr_sys

        # Debtor (Originator)
        dbtr = self._find(cdt_trf, 'Dbtr')
        if dbtr is not None:
            dbtr_name = self._find_text(dbtr, 'Nm')
            dbtr_addr = self._parse_address(dbtr)
            result['originator'] = {
                'name': dbtr_name,
                'address': dbtr_addr,
            }
            # Standard ISO 20022 flat keys for DynamicMapper inheritance
            result['debtorName'] = dbtr_name
            result['debtorStreetName'] = dbtr_addr.get('line1')
            result['debtorBuildingNumber'] = dbtr_addr.get('line2')
            result['debtorTownName'] = dbtr_addr.get('city')
            result['debtorCountrySubDivision'] = dbtr_addr.get('state')
            result['debtorPostCode'] = dbtr_addr.get('zipCode')
            result['debtorCountry'] = dbtr_addr.get('country')
            # Organization ID
            org_id = self._find(dbtr, 'Id/OrgId')
            if org_id is not None:
                lei = self._find_text(org_id, 'LEI')
                other_id = self._find_text(org_id, 'Othr/Id')
                result['originator']['lei'] = lei
                result['originator']['identifier'] = other_id
                result['debtorLei'] = lei
                result['debtorOtherId'] = other_id

        # Debtor Account
        dbtr_acct = self._find(cdt_trf, 'DbtrAcct/Id')
        if dbtr_acct is not None:
            acct = self._find_text(dbtr_acct, 'Othr/Id') or self._find_text(dbtr_acct, 'IBAN')
            iban = self._find_text(dbtr_acct, 'IBAN')
            if result.get('originator'):
                result['originator']['accountNumber'] = acct
            else:
                result['originator'] = {'accountNumber': acct, 'address': {}}
            # Standard ISO 20022 flat keys
            result['debtorAccountOther'] = acct
            result['debtorAccountIban'] = iban

        # Creditor Agent (Beneficiary's Bank)
        cdtr_agt = self._find(cdt_trf, 'CdtrAgt/FinInstnId')
        if cdtr_agt is not None:
            cdtr_agt_bic = self._find_text(cdtr_agt, 'BICFI')
            cdtr_agt_routing = self._find_text(cdtr_agt, 'ClrSysMmbId/MmbId')
            cdtr_agt_name = self._find_text(cdtr_agt, 'Nm')
            cdtr_agt_clr_sys = self._find_text(cdtr_agt, 'ClrSysMmbId/ClrSysId/Cd')
            # Fedwire-specific naming
            result['beneficiaryBank'] = {
                'bic': cdtr_agt_bic,
                'routingNumber': cdtr_agt_routing,
                'name': cdtr_agt_name,
            }
            # Standard ISO 20022 flat keys for DynamicMapper inheritance
            result['creditorAgentBic'] = cdtr_agt_bic
            result['creditorAgentName'] = cdtr_agt_name
            result['creditorAgentMemberId'] = cdtr_agt_routing
            result['creditorAgentClearingSystemId'] = cdtr_agt_clr_sys

        # Creditor (Beneficiary)
        cdtr = self._find(cdt_trf, 'Cdtr')
        if cdtr is not None:
            cdtr_name = self._find_text(cdtr, 'Nm')
            cdtr_addr = self._parse_address(cdtr)
            result['beneficiary'] = {
                'name': cdtr_name,
                'address': cdtr_addr,
            }
            # Standard ISO 20022 flat keys for DynamicMapper inheritance
            result['creditorName'] = cdtr_name
            result['creditorStreetName'] = cdtr_addr.get('line1')
            result['creditorBuildingNumber'] = cdtr_addr.get('line2')
            result['creditorTownName'] = cdtr_addr.get('city')
            result['creditorCountrySubDivision'] = cdtr_addr.get('state')
            result['creditorPostCode'] = cdtr_addr.get('zipCode')
            result['creditorCountry'] = cdtr_addr.get('country')
            # Organization ID
            org_id = self._find(cdtr, 'Id/OrgId')
            if org_id is not None:
                lei = self._find_text(org_id, 'LEI')
                other_id = self._find_text(org_id, 'Othr/Id')
                result['beneficiary']['lei'] = lei
                result['beneficiary']['identifier'] = other_id
                result['creditorLei'] = lei
                result['creditorOtherId'] = other_id

        # Creditor Account
        cdtr_acct = self._find(cdt_trf, 'CdtrAcct/Id')
        if cdtr_acct is not None:
            acct = self._find_text(cdtr_acct, 'Othr/Id') or self._find_text(cdtr_acct, 'IBAN')
            iban = self._find_text(cdtr_acct, 'IBAN')
            if result.get('beneficiary'):
                result['beneficiary']['accountNumber'] = acct
            else:
                result['beneficiary'] = {'accountNumber': acct, 'address': {}}
            # Standard ISO 20022 flat keys
            result['creditorAccountOther'] = acct
            result['creditorAccountIban'] = iban

        # Remittance Information
        rmt_inf = self._find(cdt_trf, 'RmtInf')
        if rmt_inf is not None:
            result['originatorToBeneficiaryInfo'] = self._find_text(rmt_inf, 'Ustrd')
            # Structured remittance
            strd = self._find(rmt_inf, 'Strd/RfrdDocInf')
            if strd is not None:
                result['fiToFiInfo'] = self._find_text(strd, 'Nb')

        return result

    def _parse_address(self, element: ET.Element) -> Dict[str, Any]:
        """Parse postal address from element."""
        addr = {}
        pstl_adr = self._find(element, 'PstlAdr')
        if pstl_adr is not None:
            addr['line1'] = self._find_text(pstl_adr, 'StrtNm')
            addr['line2'] = self._find_text(pstl_adr, 'BldgNb')
            addr['city'] = self._find_text(pstl_adr, 'TwnNm')
            addr['state'] = self._find_text(pstl_adr, 'CtrySubDvsn')
            addr['zipCode'] = self._find_text(pstl_adr, 'PstCd')
            addr['country'] = self._find_text(pstl_adr, 'Ctry')
        return addr


class FedwireTagValueParser:
    """Parser for Fedwire tag-value format messages.

    Fedwire uses 4-digit numeric tags in the format {NNNN}value.
    Tags are organized by category:
    - 1xxx: Message Disposition
    - 2xxx: Amount
    - 3xxx: Sender/Receiver FI
    - 4xxx: Originator
    - 5xxx: Originator FI (Ordering Customer)
    - 6xxx: Beneficiary
    - 7xxx: FI-to-FI Information
    - 8xxx: Remittance Information
    - 9xxx: Message Trailer
    """

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse Fedwire tag-value message into structured dict."""
        result = {
            'currency': 'USD',  # Fedwire is always USD
        }
        lines = raw_content.strip().split('\n')
        current_tag = None
        current_value = []

        # Multi-line tag accumulators for address lines
        originator_address_lines = []
        beneficiary_address_lines = []

        for line in lines:
            line = line.rstrip()

            # Check for tag at start of line: {NNNN}
            tag_match = re.match(r'^\{(\d{4})\}(.*)$', line)
            if tag_match:
                # Save previous tag value
                if current_tag:
                    self._set_field(result, current_tag, '\n'.join(current_value),
                                   originator_address_lines, beneficiary_address_lines)
                # Start new tag
                current_tag = tag_match.group(1)
                current_value = [tag_match.group(2)] if tag_match.group(2) else []
            elif current_tag:
                # Continuation line
                current_value.append(line)

        # Save last tag
        if current_tag:
            self._set_field(result, current_tag, '\n'.join(current_value),
                           originator_address_lines, beneficiary_address_lines)

        # Process accumulated address lines
        if originator_address_lines:
            self._parse_address_lines(result, 'originator', originator_address_lines)
        if beneficiary_address_lines:
            self._parse_address_lines(result, 'beneficiary', beneficiary_address_lines)

        return result

    def _set_field(self, result: Dict[str, Any], tag: str, value: str,
                   orig_addr_lines: List[str], benef_addr_lines: List[str]) -> None:
        """Set field value based on Fedwire tag."""
        value = value.strip()

        # =========================================================================
        # 1xxx: MESSAGE DISPOSITION
        # =========================================================================
        if tag == '1500':
            # Type/Subtype Code (2 chars)
            result['typeCode'] = value[:2] if value else None
        elif tag == '1510':
            # Subtype Code (2 chars)
            result['subtypeCode'] = value[:2] if value else None
        elif tag == '1520':
            # Input Message Accountability Data (IMAD)
            # Format: YYYYMMDDSSSSSSSSNNNNNN (22 chars)
            result['imad'] = value
            if len(value) >= 8 and value[:8].isdigit():
                try:
                    year = value[:4]
                    month = value[4:6]
                    day = value[6:8]
                    if 1900 <= int(year) <= 2100 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
                        result['inputCycleDate'] = f"{year}-{month}-{day}"
                except (ValueError, IndexError):
                    pass
            if len(value) >= 16:
                result['inputSource'] = value[8:16]
            if len(value) >= 22:
                result['inputSequenceNumber'] = value[16:22]

        # =========================================================================
        # 2xxx: AMOUNT
        # =========================================================================
        elif tag == '2000':
            # Amount: 12-15 digits with implied 2 decimals
            # Value like "000000025000000" = $250,000.00
            clean = value.replace(',', '').replace('.', '').lstrip('0')
            if clean and clean.isdigit():
                result['amount'] = float(clean) / 100
            else:
                result['amount'] = 0.0
                logger.warning(f"FEDWIRE tag 2000 has non-numeric value: {value[:50]}")
            result['currency'] = 'USD'  # Fedwire is always USD

        # =========================================================================
        # 3xxx: SENDER/RECEIVER FI
        # =========================================================================
        elif tag == '3100':
            # Sender FI: 9-digit ABA + Name
            self._parse_fi(result, 'sender', value)
        elif tag == '3320':
            # Sender Reference
            result['senderReference'] = value
        elif tag == '3400':
            # Receiver FI: 9-digit ABA + Name
            self._parse_fi(result, 'receiver', value)
        elif tag == '3500':
            # Receiver FI (alternate location) - just routing number
            if 'receiver' not in result:
                result['receiver'] = {}
            if len(value) >= 9:
                result['receiver']['routingNumber'] = value[:9]
        elif tag == '3600':
            # Business Function Code (CTR, BTR, DRC, etc.)
            result['businessFunctionCode'] = value

        # =========================================================================
        # 4xxx: ORIGINATOR (Debtor/Payer)
        # =========================================================================
        elif tag == '4000':
            # Originator Identifier Code (1 char: B, D, F, etc.)
            # This is NOT the name, just an identifier type
            if 'originator' not in result:
                result['originator'] = {'address': {}}
            result['originator']['identifierCode'] = value
        elif tag == '4100':
            # Originator FI Identifier (D/ABA/Name format)
            if 'originator' not in result:
                result['originator'] = {'address': {}}
            if value.startswith('D/') or value.startswith('F/'):
                parts = value.split('/')
                if len(parts) >= 2:
                    result['originator']['identifierType'] = parts[0]
                    result['originator']['fiRoutingNumber'] = parts[1][:9] if len(parts[1]) >= 9 else parts[1]
                if len(parts) >= 3:
                    result['originator']['fiName'] = parts[2]
            else:
                result['originator']['fiIdentifier'] = value
        elif tag == '4200':
            # Originator Account Number (may have D/ prefix)
            if 'originator' not in result:
                result['originator'] = {'address': {}}
            if value.startswith('D') and len(value) > 1:
                result['originator']['accountNumber'] = value[1:]
                result['originator']['identifier'] = value
            else:
                result['originator']['accountNumber'] = value
                result['originator']['identifier'] = value
        elif tag == '4320':
            # Originator Name (THIS IS THE PRIMARY NAME FIELD)
            if 'originator' not in result:
                result['originator'] = {'address': {}}
            result['originator']['name'] = value

        # =========================================================================
        # 5xxx: ORIGINATOR FI / ORDERING CUSTOMER
        # In some message variants, 5xxx is used for originator details
        # =========================================================================
        elif tag == '5000':
            # This can be Beneficiary OR Originator Name depending on context
            # If we already have originator name from 4320, treat as beneficiary
            # Otherwise, use as originator name (legacy format)
            if 'originator' not in result:
                result['originator'] = {'address': {}}
            # If no name yet from 4320, use this
            if not result['originator'].get('name'):
                result['originator']['name'] = value
            else:
                # If we already have originator, this might be beneficiary in alt format
                # Store for later resolution
                result['_5000_value'] = value
        elif tag == '5010':
            # Originator Address Lines (accumulate)
            orig_addr_lines.append(value)
        elif tag == '5100':
            # Originator FI BIC/Identifier
            if 'originatorFi' not in result:
                result['originatorFi'] = {}
            result['originatorFi']['bic'] = value
        elif tag == '5200':
            # Originator FI Name/Account
            if 'originatorFi' not in result:
                result['originatorFi'] = {}
            result['originatorFi']['name'] = value

        # =========================================================================
        # 6xxx: BENEFICIARY (Creditor/Payee)
        # =========================================================================
        elif tag == '6000':
            # Beneficiary Name (PRIMARY NAME FIELD)
            if 'beneficiary' not in result:
                result['beneficiary'] = {'address': {}}
            result['beneficiary']['name'] = value
        elif tag == '6010':
            # Beneficiary Address Lines (accumulate)
            benef_addr_lines.append(value)
        elif tag == '6100':
            # Beneficiary FI Identifier (BIC or ABA)
            if 'beneficiaryBank' not in result:
                result['beneficiaryBank'] = {}
            # Check if it looks like a BIC (8 or 11 chars, alphanumeric)
            if re.match(r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$', value):
                result['beneficiaryBank']['bic'] = value
            else:
                result['beneficiaryBank']['routingNumber'] = value[:9] if len(value) >= 9 else value
        elif tag == '6110':
            # Beneficiary FI City/Location
            if 'beneficiaryBank' not in result:
                result['beneficiaryBank'] = {}
            result['beneficiaryBank']['city'] = value
        elif tag == '6200':
            # Beneficiary Country
            if 'beneficiary' not in result:
                result['beneficiary'] = {'address': {}}
            result['beneficiary']['address']['country'] = value[:2] if len(value) >= 2 else value
        elif tag == '6210':
            # Beneficiary Reference or Postal Code
            # This can be beneficiary reference OR postal code depending on format
            if 'beneficiary' not in result:
                result['beneficiary'] = {'address': {}}
            # If it looks like a postal code (digits or common postal format)
            if re.match(r'^\d{5}(-\d{4})?$', value) or re.match(r'^[A-Z0-9]{3,10}$', value):
                result['beneficiary']['address']['zipCode'] = value
            result['beneficiaryReference'] = value
        elif tag == '6300':
            # Beneficiary Account Number
            if 'beneficiary' not in result:
                result['beneficiary'] = {'address': {}}
            result['beneficiary']['accountNumber'] = value
        elif tag == '6400':
            # Beneficiary FI BIC (alternate location)
            if 'beneficiaryBank' not in result:
                result['beneficiaryBank'] = {}
            if re.match(r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$', value):
                result['beneficiaryBank']['bic'] = value
            else:
                result['beneficiaryBank']['identifier'] = value
        elif tag == '6500':
            # Beneficiary FI Name
            if 'beneficiaryBank' not in result:
                result['beneficiaryBank'] = {}
            result['beneficiaryBank']['name'] = value

        # =========================================================================
        # 7xxx: FI-TO-FI INFORMATION
        # =========================================================================
        elif tag == '7033':
            # FI-to-FI Information (invoice, PO, etc.)
            result['fiToFiInfo'] = value.replace('\n', ' ')
        elif tag == '7050':
            # Service Message Code
            result['serviceMessageCode'] = value
        elif tag == '7052':
            # Service Message Amount
            clean = value.replace(',', '').replace('.', '').lstrip('0')
            if clean and clean.isdigit():
                result['serviceMessageAmount'] = float(clean) / 100

        # =========================================================================
        # 8xxx: REMITTANCE INFORMATION
        # =========================================================================
        elif tag == '8200':
            # Originator-to-Beneficiary Information
            result['originatorToBeneficiaryInfo'] = value.replace('\n', ' ')
        elif tag == '8250':
            # Additional Remittance Info
            if result.get('originatorToBeneficiaryInfo'):
                result['originatorToBeneficiaryInfo'] += ' ' + value
            else:
                result['originatorToBeneficiaryInfo'] = value

        # =========================================================================
        # 9xxx: MESSAGE TRAILER
        # =========================================================================
        elif tag == '9000':
            # End of message marker
            pass

    def _parse_fi(self, result: Dict[str, Any], prefix: str, value: str) -> None:
        """Parse financial institution field (3100, 3400)."""
        if prefix not in result:
            result[prefix] = {}

        lines = value.split('\n')
        first_line = lines[0] if lines else ''

        # First 9 chars are routing number (ABA)
        if len(first_line) >= 9:
            result[prefix]['routingNumber'] = first_line[:9]
            result[prefix]['name'] = first_line[9:].strip()
        else:
            result[prefix]['name'] = first_line

    def _parse_address_lines(self, result: Dict[str, Any], prefix: str, lines: List[str]) -> None:
        """Parse accumulated address lines for a party."""
        if prefix not in result:
            result[prefix] = {'address': {}}
        if 'address' not in result[prefix]:
            result[prefix]['address'] = {}

        addr = result[prefix]['address']

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Check for country code (2 uppercase letters alone on a line)
            if re.match(r'^[A-Z]{2}$', line):
                addr['country'] = line
            # Check for "CITY STATE ZIP" format
            elif re.match(r'.+\s+[A-Z]{2}\s+\d{5}(-\d{4})?$', line):
                # Parse "MOUNTAIN VIEW CA 94043" format
                match = re.match(r'^(.+?)\s+([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$', line)
                if match:
                    addr['city'] = match.group(1).strip()
                    addr['state'] = match.group(2)
                    addr['zipCode'] = match.group(3)
            elif 'line1' not in addr:
                addr['line1'] = line
            elif 'city' not in addr and 'line2' not in addr:
                # Could be city or line2 - check format
                if re.search(r'[A-Z]{2}\s+\d{5}', line):
                    # This line has state/zip, parse it
                    parts = line.rsplit(' ', 2)
                    if len(parts) >= 3:
                        addr['city'] = parts[0]
                        addr['state'] = parts[1]
                        addr['zipCode'] = parts[2]
                else:
                    addr['line2'] = line


class FedwireExtractor(BaseExtractor):
    """Extractor for Fedwire Funds Service messages.

    ISO 20022 INHERITANCE:
        FEDWIRE inherits from pacs.008 (FI to FI Customer Credit Transfer).
        The FedwireISO20022Parser inherits from Pacs008Parser.
        Uses Federal Reserve ISO 20022 usage guidelines.

    Format Support:
        1. ISO 20022 XML (pacs.008/pacs.009) - Current standard (March 2025+)
        2. Legacy FAIM tag-value format - For historical data processing

    Fedwire-Specific Elements:
        - IMAD (Input Message Accountability Data) - Unique identifier
        - ABA Routing Numbers - US clearing system (USABA)
        - Currency always USD
        - US-specific address format (State codes, ZIP codes)

    Database Tables:
        - Bronze: bronze.raw_payment_messages
        - Silver: silver.stg_fedwire
        - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_fedwire

    Inheritance Hierarchy:
        BaseExtractor -> FedwireExtractor
        (Parser: Pacs008Parser -> FedwireISO20022Parser)
    """

    MESSAGE_TYPE = "FEDWIRE"
    SILVER_TABLE = "stg_iso20022_pacs008"  # Shared ISO 20022 pacs.008 table
    DEFAULT_CURRENCY = "USD"
    CLEARING_SYSTEM = "USABA"  # US ABA routing number system

    def __init__(self):
        self.iso20022_parser = FedwireISO20022Parser()
        self.legacy_parser = FedwireTagValueParser()
        # Default to ISO 20022 parser (current standard)
        self.parser = self.iso20022_parser

    def _detect_and_parse(self, raw_content: str) -> Dict[str, Any]:
        """Auto-detect format and parse accordingly.

        Returns parsed dict regardless of input format.
        """
        content = raw_content.strip()

        # Check if it's XML (ISO 20022)
        if content.startswith('<?xml') or content.startswith('<Document') or content.startswith('<FIToFICstmrCdtTrf'):
            logger.debug("Detected Fedwire ISO 20022 XML format")
            return self.iso20022_parser.parse(content)

        # Check if it's legacy FAIM tag-value format {NNNN}
        if '{1500}' in content or '{2000}' in content or '{3100}' in content:
            logger.debug("Detected Fedwire legacy FAIM tag-value format")
            return self.legacy_parser.parse(content)

        # Try JSON (pre-parsed content)
        if content.startswith('{') and not content.startswith('{1'):
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
        """Extract Bronze layer record from raw Fedwire content."""
        msg_id = raw_content.get('messageId', '') or raw_content.get('imad', '')
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
        """Extract all Silver layer fields from Fedwire message."""
        trunc = self.trunc

        # Handle raw text content - parse it first using auto-detection
        if isinstance(msg_content, dict) and '_raw_text' in msg_content:
            raw_text = msg_content['_raw_text']
            msg_content = self._detect_and_parse(raw_text)

        # Extract nested objects with safe defaults
        sender = msg_content.get('sender') or {}
        sender_addr = sender.get('address') or {} if sender else {}
        receiver = msg_content.get('receiver') or {}
        receiver_addr = receiver.get('address') or {} if receiver else {}
        originator = msg_content.get('originator') or {}
        originator_addr = originator.get('address') or {} if originator else {}
        beneficiary = msg_content.get('beneficiary') or {}
        beneficiary_addr = beneficiary.get('address') or {} if beneficiary else {}
        beneficiary_bank = msg_content.get('beneficiaryBank') or {}
        originator_fi = msg_content.get('originatorFi') or {}
        instructing_bank = msg_content.get('instructingBank') or {}
        intermediary_bank = msg_content.get('intermediaryBank') or {}

        # Currency is always USD for Fedwire
        currency = msg_content.get('currency') or 'USD'

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Header (matching actual DB schema)
            'type_code': trunc(msg_content.get('typeCode'), 2),
            'subtype_code': trunc(msg_content.get('subtypeCode'), 2),
            'imad': trunc(msg_content.get('imad'), 22),
            'omad': trunc(msg_content.get('omad'), 22),
            'input_cycle_date': msg_content.get('inputCycleDate'),
            'input_source': trunc(msg_content.get('inputSource'), 8),
            'input_sequence_number': trunc(msg_content.get('inputSequenceNumber'), 6),

            # Amount & Currency - ALWAYS set currency for Fedwire
            'amount': msg_content.get('amount'),
            'currency': currency,
            'instructed_amount': msg_content.get('instructedAmount'),
            'instructed_currency': msg_content.get('instructedCurrency') or currency,

            # References
            'sender_reference': trunc(msg_content.get('senderReference'), 16),
            'previous_imad': trunc(msg_content.get('previousMessageId'), 22),
            'business_function_code': trunc(msg_content.get('businessFunctionCode'), 3),
            'beneficiary_reference': trunc(msg_content.get('beneficiaryReference'), 16),

            # Sender FI (using DB column names)
            'sender_aba': trunc(sender.get('routingNumber'), 9),
            'sender_name': trunc(sender.get('name'), 140),
            'sender_short_name': trunc(sender.get('shortName'), 35),
            'sender_bic': sender.get('bic'),
            'sender_lei': trunc(sender.get('lei'), 20),
            'sender_address_line1': trunc(sender_addr.get('line1'), 140),
            'sender_address_line2': trunc(sender_addr.get('line2'), 140),
            'sender_city': trunc(sender_addr.get('city'), 35),
            'sender_state': trunc(sender_addr.get('state'), 2),
            'sender_zip_code': trunc(sender_addr.get('zipCode'), 10),
            'sender_country': sender_addr.get('country') or 'US',

            # Receiver FI
            'receiver_aba': trunc(receiver.get('routingNumber'), 9),
            'receiver_name': trunc(receiver.get('name'), 140),
            'receiver_short_name': trunc(receiver.get('shortName'), 35),
            'receiver_bic': receiver.get('bic'),
            'receiver_lei': trunc(receiver.get('lei'), 20),
            'receiver_address_line1': trunc(receiver_addr.get('line1'), 140),
            'receiver_address_line2': trunc(receiver_addr.get('line2'), 140),
            'receiver_city': trunc(receiver_addr.get('city'), 35),
            'receiver_state': trunc(receiver_addr.get('state'), 2),
            'receiver_zip_code': trunc(receiver_addr.get('zipCode'), 10),
            'receiver_country': receiver_addr.get('country') or 'US',

            # Originator (using DB column names)
            'originator_name': trunc(originator.get('name'), 140),
            'originator_account_number': trunc(originator.get('accountNumber'), 35),
            'originator_address_line1': trunc(originator_addr.get('line1'), 140),
            'originator_address_line2': trunc(originator_addr.get('line2'), 140),
            'originator_city': trunc(originator_addr.get('city'), 35),
            'originator_state': trunc(originator_addr.get('state'), 2),
            'originator_zip_code': trunc(originator_addr.get('zipCode'), 10),
            'originator_country': originator_addr.get('country') or 'US',
            'originator_id': trunc(originator.get('identifier'), 35),
            'originator_id_type': trunc(originator.get('identifierType'), 10),

            # Originator Option F (additional party info)
            'originator_option_f': trunc(msg_content.get('originatorOptionF'), 140),

            # Beneficiary (using DB column names)
            'beneficiary_name': trunc(beneficiary.get('name'), 140),
            'beneficiary_account_number': trunc(beneficiary.get('accountNumber'), 35),
            'beneficiary_address_line1': trunc(beneficiary_addr.get('line1'), 140),
            'beneficiary_address_line2': trunc(beneficiary_addr.get('line2'), 140),
            'beneficiary_city': trunc(beneficiary_addr.get('city'), 35),
            'beneficiary_state': trunc(beneficiary_addr.get('state'), 2),
            'beneficiary_zip_code': trunc(beneficiary_addr.get('zipCode'), 10),
            'beneficiary_country': beneficiary_addr.get('country') or 'US',
            'beneficiary_id': trunc(beneficiary.get('identifier'), 35),
            'beneficiary_id_type': trunc(beneficiary.get('identifierType'), 10),

            # Beneficiary Bank (using DB column names)
            'beneficiary_fi_id': trunc(beneficiary_bank.get('routingNumber'), 9),
            'beneficiary_fi_name': trunc(beneficiary_bank.get('name'), 140),
            'beneficiary_fi_bic': beneficiary_bank.get('bic'),

            # Instructing Bank
            'instructing_fi_id': trunc(instructing_bank.get('routingNumber'), 9),
            'instructing_fi_name': trunc(instructing_bank.get('name'), 140),

            # Intermediary Bank
            'intermediary_fi_id': trunc(intermediary_bank.get('routingNumber'), 9) if intermediary_bank else None,
            'intermediary_fi_name': trunc(intermediary_bank.get('name'), 140) if intermediary_bank else None,

            # Info Fields
            'originator_to_beneficiary_info': trunc(msg_content.get('originatorToBeneficiaryInfo'), 140),
            'fi_to_fi_info': trunc(msg_content.get('fiToFiInfo'), 210),
            'charges': trunc(msg_content.get('chargeDetails'), 3),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'type_code', 'subtype_code', 'imad', 'omad',
            'input_cycle_date', 'input_source', 'input_sequence_number',
            'amount', 'currency', 'instructed_amount', 'instructed_currency',
            'sender_reference', 'previous_imad', 'business_function_code', 'beneficiary_reference',
            'sender_aba', 'sender_name', 'sender_short_name', 'sender_bic', 'sender_lei',
            'sender_address_line1', 'sender_address_line2', 'sender_city', 'sender_state',
            'sender_zip_code', 'sender_country',
            'receiver_aba', 'receiver_name', 'receiver_short_name', 'receiver_bic', 'receiver_lei',
            'receiver_address_line1', 'receiver_address_line2', 'receiver_city', 'receiver_state',
            'receiver_zip_code', 'receiver_country',
            'originator_name', 'originator_account_number',
            'originator_address_line1', 'originator_address_line2',
            'originator_city', 'originator_state', 'originator_zip_code', 'originator_country',
            'originator_id', 'originator_id_type', 'originator_option_f',
            'beneficiary_name', 'beneficiary_account_number',
            'beneficiary_address_line1', 'beneficiary_address_line2',
            'beneficiary_city', 'beneficiary_state', 'beneficiary_zip_code', 'beneficiary_country',
            'beneficiary_id', 'beneficiary_id_type',
            'beneficiary_fi_id', 'beneficiary_fi_name', 'beneficiary_fi_bic',
            'instructing_fi_id', 'instructing_fi_name',
            'intermediary_fi_id', 'intermediary_fi_name',
            'originator_to_beneficiary_info', 'fi_to_fi_info', 'charges',
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
        """Extract Gold layer entities from Fedwire Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Originator (Debtor Party) - uses Silver column names
        if silver_data.get('originator_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('originator_name'),
                role="DEBTOR",
                party_type='UNKNOWN',
                street_name=silver_data.get('originator_address_line1'),
                town_name=silver_data.get('originator_city'),
                post_code=silver_data.get('originator_zip_code'),
                country_sub_division=silver_data.get('originator_state'),
                country=silver_data.get('originator_country') or 'US',
                identification_type=silver_data.get('originator_id_type'),
                identification_number=silver_data.get('originator_id'),
            ))

        # Beneficiary (Creditor Party)
        if silver_data.get('beneficiary_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('beneficiary_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                street_name=silver_data.get('beneficiary_address_line1'),
                town_name=silver_data.get('beneficiary_city'),
                post_code=silver_data.get('beneficiary_zip_code'),
                country_sub_division=silver_data.get('beneficiary_state'),
                country=silver_data.get('beneficiary_country') or 'US',
                identification_type=silver_data.get('beneficiary_id_type'),
                identification_number=silver_data.get('beneficiary_id'),
            ))

        # Originator Account (Debtor Account)
        if silver_data.get('originator_account_number'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('originator_account_number'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'USD',
            ))

        # Beneficiary Account (Creditor Account)
        if silver_data.get('beneficiary_account_number'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('beneficiary_account_number'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'USD',
            ))

        # Sender FI (Debtor Agent)
        if silver_data.get('sender_aba'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=silver_data.get('sender_name'),
                short_name=silver_data.get('sender_short_name'),
                bic=silver_data.get('sender_bic'),
                lei=silver_data.get('sender_lei'),
                clearing_code=silver_data.get('sender_aba'),
                clearing_system='USABA',
                address_line1=silver_data.get('sender_address_line1'),
                town_name=silver_data.get('sender_city'),
                country=silver_data.get('sender_country') or 'US',
            ))

        # Receiver FI / Beneficiary Bank (Creditor Agent)
        if silver_data.get('receiver_aba') or silver_data.get('beneficiary_fi_id'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=silver_data.get('receiver_name') or silver_data.get('beneficiary_fi_name'),
                short_name=silver_data.get('receiver_short_name'),
                bic=silver_data.get('receiver_bic') or silver_data.get('beneficiary_fi_bic'),
                lei=silver_data.get('receiver_lei'),
                clearing_code=silver_data.get('receiver_aba') or silver_data.get('beneficiary_fi_id'),
                clearing_system='USABA',
                address_line1=silver_data.get('receiver_address_line1'),
                town_name=silver_data.get('receiver_city'),
                country=silver_data.get('receiver_country') or 'US',
            ))

        # Intermediary Bank
        if silver_data.get('intermediary_fi_id'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INTERMEDIARY",
                name=silver_data.get('intermediary_fi_name'),
                clearing_code=silver_data.get('intermediary_fi_id'),
                clearing_system='USABA',
                country='US',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('FEDWIRE', FedwireExtractor())
ExtractorRegistry.register('fedwire', FedwireExtractor())
