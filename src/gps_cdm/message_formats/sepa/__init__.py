"""SEPA Credit Transfer (pain.001 with SEPA rules) Extractor.

ISO 20022 INHERITANCE HIERARCHY:
    SEPA uses European Payments Council (EPC) ISO 20022 usage guidelines based on pain.001.
    The SepaISO20022Parser inherits from Pain001Parser.

    BaseISO20022Parser
        └── Pain001Parser (Customer Credit Transfer Initiation - pain.001.001.09)
            └── SepaISO20022Parser (EPC SEPA Credit Transfer guidelines)

SEPA-SPECIFIC ELEMENTS:
    - IBAN account numbers (mandatory)
    - BIC codes for financial institutions
    - EUR currency (Euro zone)
    - SEPA AT/RT elements (Additional Transaction/Remittance information)
    - EPC Scheme Rules compliance

CLEARING SYSTEM:
    - STEP2 (Pan-European clearing)
    - TARGET2 (High-value payments)
    - National clearing systems (with SEPA compliance)

DATABASE TABLES:
    - Bronze: bronze.raw_payment_messages
    - Silver: silver.stg_sepa
    - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_sepa

MAPPING INHERITANCE:
    SEPA -> pain.001.base (PARTIAL - SEPA adds EPC-specific fields)
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
    from ..iso20022 import Pain001Parser, Pain001Extractor
    ISO20022_BASE_AVAILABLE = True
except ImportError:
    ISO20022_BASE_AVAILABLE = False
    logger.warning("ISO 20022 base classes not available - SEPA will use standalone implementation")


# =============================================================================
# SEPA ISO 20022 PARSER (inherits from Pain001Parser)
# =============================================================================

# Use conditional inheritance pattern for backward compatibility
_SepaParserBase = Pain001Parser if ISO20022_BASE_AVAILABLE else object


class SepaISO20022Parser(_SepaParserBase):
    """SEPA ISO 20022 pain.001 parser with EPC (European Payments Council) usage guidelines.

    Inherits from Pain001Parser and adds SEPA-specific processing:
    - IBAN validation and extraction
    - BIC code handling for Eurozone FIs
    - SEPA-specific clearing system identification
    - EPC scheme compliance checks

    ISO 20022 Version: pain.001.001.09
    Usage Guidelines: EPC SEPA Credit Transfer Rulebook

    Inheritance Hierarchy:
        BaseISO20022Parser -> Pain001Parser -> SepaISO20022Parser
    """

    # SEPA-specific constants
    CLEARING_SYSTEM = "SEPA"  # SEPA Credit Transfer Scheme
    DEFAULT_CURRENCY = "EUR"
    MESSAGE_TYPE = "SEPA"

    def __init__(self):
        """Initialize SEPA parser."""
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse SEPA ISO 20022 pain.001 message.

        Uses inherited pain.001 parsing from Pain001Parser and adds
        SEPA-specific fields.
        """
        # Handle JSON/dict input
        if isinstance(raw_content, dict):
            return raw_content

        if isinstance(raw_content, str) and raw_content.strip().startswith('{'):
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError:
                pass

        # Use parent pain.001 parsing if available
        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = self._parse_standalone(raw_content)

        # Add SEPA-specific fields
        result['isSepa'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM

        # Ensure IBAN fields are populated
        self._ensure_iban_fields(result)

        return result

    def _parse_standalone(self, raw_content: str) -> Dict[str, Any]:
        """Standalone parsing when base class not available."""
        legacy_parser = SepaXmlParser()
        return legacy_parser.parse(raw_content)

    def _ensure_iban_fields(self, result: Dict[str, Any]) -> None:
        """Ensure SEPA-specific IBAN fields are populated from generic fields."""
        # SEPA mandates IBAN for account identification
        if 'debtorIBAN' not in result and 'debtorAccount' in result:
            debtor_acct = result.get('debtorAccount', {})
            if isinstance(debtor_acct, dict):
                result['debtorIBAN'] = debtor_acct.get('iban')

        if 'creditorIBAN' not in result and 'creditorAccount' in result:
            creditor_acct = result.get('creditorAccount', {})
            if isinstance(creditor_acct, dict):
                result['creditorIBAN'] = creditor_acct.get('iban')


# =============================================================================
# LEGACY XML PARSER (kept for backward compatibility)
# =============================================================================


class SepaXmlParser:
    """Parser for SEPA Credit Transfer XML messages (pain.001 variant).

    Legacy parser kept for backward compatibility when ISO 20022 base classes
    are not available.
    """

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

    def _find_attr(self, element: ET.Element, path: str, attr: str) -> Optional[str]:
        """Find element attribute."""
        elem = self._find(element, path)
        return elem.get(attr) if elem is not None else None

    def parse(self, xml_content: str) -> Dict[str, Any]:
        """Parse SEPA XML content into structured dict."""
        try:
            if xml_content.startswith('\ufeff'):
                xml_content = xml_content[1:]

            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.error(f"Failed to parse SEPA XML: {e}")
            raise ValueError(f"Invalid XML: {e}")

        # Find the main content element (CstmrCdtTrfInitn)
        initn = self._find(root, 'CstmrCdtTrfInitn')
        if initn is None:
            if self._strip_ns(root.tag) == 'CstmrCdtTrfInitn':
                initn = root
            else:
                raise ValueError("Cannot find CstmrCdtTrfInitn element in SEPA message")

        return self._parse_initiation(initn)

    def _parse_initiation(self, initn: ET.Element) -> Dict[str, Any]:
        """Parse CstmrCdtTrfInitn element."""
        result = {'isSepa': True}

        # Group Header
        grp_hdr = self._find(initn, 'GrpHdr')
        if grp_hdr is not None:
            result['messageId'] = self._find_text(grp_hdr, 'MsgId')
            result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')
            result['numberOfTransactions'] = self._safe_int(self._find_text(grp_hdr, 'NbOfTxs'))
            result['controlSum'] = self._safe_decimal(self._find_text(grp_hdr, 'CtrlSum'))

            # Initiating Party
            initg_pty = self._find(grp_hdr, 'InitgPty')
            if initg_pty is not None:
                result['initiatingParty'] = self._parse_party(initg_pty)

        # Payment Information
        pmt_inf = self._find(initn, 'PmtInf')
        if pmt_inf is not None:
            result.update(self._parse_payment_info(pmt_inf))

        return result

    def _parse_payment_info(self, pmt_inf: ET.Element) -> Dict[str, Any]:
        """Parse PmtInf element with SEPA-specific fields."""
        result = {
            'paymentInformation': {}
        }
        pmt_info = result['paymentInformation']

        pmt_info['paymentInfoId'] = self._find_text(pmt_inf, 'PmtInfId')
        pmt_info['paymentMethod'] = self._find_text(pmt_inf, 'PmtMtd')
        pmt_info['batchBooking'] = self._find_text(pmt_inf, 'BtchBookg') == 'true'

        # Requested Execution Date
        req_exctn_dt = self._find(pmt_inf, 'ReqdExctnDt')
        if req_exctn_dt is not None:
            pmt_info['requestedExecutionDate'] = self._find_text(req_exctn_dt, 'Dt')

        # Payment Type Information - SEPA Specific
        pmt_tp_inf = self._find(pmt_inf, 'PmtTpInf')
        if pmt_tp_inf is not None:
            pmt_info['instructionPriority'] = self._find_text(pmt_tp_inf, 'InstrPrty')
            pmt_info['serviceLevel'] = self._find_text(pmt_tp_inf, 'SvcLvl/Cd')
            pmt_info['localInstrument'] = self._find_text(pmt_tp_inf, 'LclInstrm/Cd')
            pmt_info['categoryPurpose'] = self._find_text(pmt_tp_inf, 'CtgyPurp/Cd')

        # Debtor
        dbtr = self._find(pmt_inf, 'Dbtr')
        if dbtr is not None:
            result['debtor'] = self._parse_party(dbtr)

        # Debtor Account - IBAN Required for SEPA
        dbtr_acct = self._find(pmt_inf, 'DbtrAcct')
        if dbtr_acct is not None:
            result['debtorAccount'] = self._parse_account(dbtr_acct)

        # Debtor Agent - BIC
        dbtr_agt = self._find(pmt_inf, 'DbtrAgt')
        if dbtr_agt is not None:
            result['debtorAgent'] = self._parse_agent(dbtr_agt)

        # Charge Bearer - Must be SLEV for SEPA
        result['chargeBearer'] = self._find_text(pmt_inf, 'ChrgBr')

        # Credit Transfer Transaction Information
        cdt_trf_tx_inf = self._find(pmt_inf, 'CdtTrfTxInf')
        if cdt_trf_tx_inf is not None:
            result.update(self._parse_transaction(cdt_trf_tx_inf))

        return result

    def _parse_transaction(self, tx_inf: ET.Element) -> Dict[str, Any]:
        """Parse CdtTrfTxInf element."""
        result = {}

        # Payment ID
        pmt_id = self._find(tx_inf, 'PmtId')
        if pmt_id is not None:
            result['instructionId'] = self._find_text(pmt_id, 'InstrId')
            result['endToEndId'] = self._find_text(pmt_id, 'EndToEndId')

        # Amount - EUR only for SEPA
        amt = self._find(tx_inf, 'Amt')
        if amt is not None:
            instd_amt = self._find(amt, 'InstdAmt')
            if instd_amt is not None:
                result['instructedAmount'] = self._safe_decimal(instd_amt.text)
                result['instructedCurrency'] = instd_amt.get('Ccy')

        # Creditor Agent
        cdtr_agt = self._find(tx_inf, 'CdtrAgt')
        if cdtr_agt is not None:
            result['creditorAgent'] = self._parse_agent(cdtr_agt)

        # Creditor
        cdtr = self._find(tx_inf, 'Cdtr')
        if cdtr is not None:
            result['creditor'] = self._parse_party(cdtr)

        # Creditor Account - IBAN Required for SEPA
        cdtr_acct = self._find(tx_inf, 'CdtrAcct')
        if cdtr_acct is not None:
            result['creditorAccount'] = self._parse_account(cdtr_acct)

        # Purpose
        purp = self._find(tx_inf, 'Purp')
        if purp is not None:
            result['purposeCode'] = self._find_text(purp, 'Cd')

        # Remittance Information
        rmt_inf = self._find(tx_inf, 'RmtInf')
        if rmt_inf is not None:
            result['remittanceInformation'] = {
                'unstructured': self._find_text(rmt_inf, 'Ustrd')
            }

        return result

    def _parse_party(self, party_elem: ET.Element) -> Dict[str, Any]:
        """Parse party element."""
        result = {
            'name': self._find_text(party_elem, 'Nm')
        }

        # Postal Address
        pstl_adr = self._find(party_elem, 'PstlAdr')
        if pstl_adr is not None:
            result['streetName'] = self._find_text(pstl_adr, 'StrtNm')
            result['postalCode'] = self._find_text(pstl_adr, 'PstCd')
            result['townName'] = self._find_text(pstl_adr, 'TwnNm')
            result['country'] = self._find_text(pstl_adr, 'Ctry')

        # Organization ID
        org_id = self._find(party_elem, 'Id/OrgId')
        if org_id is not None:
            result['id'] = self._find_text(org_id, 'Othr/Id')
            result['idScheme'] = self._find_text(org_id, 'Othr/SchmeNm/Cd')
            result['idType'] = 'ORG'

        return result

    def _parse_account(self, acct_elem: ET.Element) -> Dict[str, Any]:
        """Parse account element - IBAN required for SEPA."""
        result = {}

        acct_id = self._find(acct_elem, 'Id')
        if acct_id is not None:
            result['iban'] = self._find_text(acct_id, 'IBAN')
            result['accountNumber'] = result['iban']

        result['currency'] = self._find_text(acct_elem, 'Ccy')

        return result

    def _parse_agent(self, agt_elem: ET.Element) -> Dict[str, Any]:
        """Parse agent element - BIC for SEPA."""
        result = {}

        fin_instn_id = self._find(agt_elem, 'FinInstnId')
        if fin_instn_id is not None:
            result['bic'] = self._find_text(fin_instn_id, 'BICFI')
            result['name'] = self._find_text(fin_instn_id, 'Nm')

        return result

    def _safe_int(self, value: Optional[str]) -> Optional[int]:
        """Safely convert string to int."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _safe_decimal(self, value: Optional[str]) -> Optional[float]:
        """Safely convert string to decimal."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


class SepaExtractor(BaseExtractor):
    """Extractor for SEPA Credit Transfer messages.

    ISO 20022 INHERITANCE:
        SEPA inherits from pain.001 (Customer Credit Transfer Initiation).
        The SepaISO20022Parser inherits from Pain001Parser.
        Uses European Payments Council (EPC) SEPA Credit Transfer Rulebook.

    Format Support:
        1. ISO 20022 XML (pain.001.001.09) - Current standard
        2. Legacy pain.001 versions (003 through 008) - Backward compatibility

    SEPA-Specific Elements:
        - IBAN account numbers (mandatory for SEPA)
        - BIC codes for Eurozone financial institutions
        - EUR currency (Euro zone only)
        - EPC scheme rules compliance

    Database Tables:
        - Bronze: bronze.raw_payment_messages
        - Silver: silver.stg_sepa
        - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_sepa

    Inheritance Hierarchy:
        BaseExtractor -> SepaExtractor
        (Parser: Pain001Parser -> SepaISO20022Parser)
    """

    MESSAGE_TYPE = "SEPA"
    SILVER_TABLE = "stg_sepa"
    DEFAULT_CURRENCY = "EUR"
    CLEARING_SYSTEM = "SEPA"

    def __init__(self):
        """Initialize SEPA extractor with ISO 20022 parser."""
        self.iso20022_parser = SepaISO20022Parser()
        self.legacy_parser = SepaXmlParser()
        self.parser = self.iso20022_parser

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw SEPA content."""
        msg_id = raw_content.get('messageId', '')
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
        """Extract all Silver layer fields from SEPA message."""
        trunc = self.trunc

        # Handle raw text content - parse it first
        if isinstance(msg_content, dict) and '_raw_text' in msg_content:
            raw_text = msg_content['_raw_text']
            # SEPA is XML-based (pain.001 variant for credit transfers)
            if raw_text.strip().startswith('<?xml') or raw_text.strip().startswith('<'):
                parser = SepaXmlParser()
                msg_content = parser.parse(raw_text)

        # Extract nested objects
        initiating_party = msg_content.get('initiatingParty', {})
        pmt_info = msg_content.get('paymentInformation', {})
        debtor = msg_content.get('debtor', {})
        debtor_account = msg_content.get('debtorAccount', {})
        debtor_agent = msg_content.get('debtorAgent', {})
        creditor = msg_content.get('creditor', {})
        creditor_account = msg_content.get('creditorAccount', {})
        creditor_agent = msg_content.get('creditorAgent', {})
        remittance_info = msg_content.get('remittanceInformation', {})

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Header (matching DB schema)
            'msg_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'number_of_transactions': msg_content.get('numberOfTransactions'),

            # Instruction
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),

            # Amounts - EUR Only for SEPA
            'instructed_amount': msg_content.get('instructedAmount'),
            'instructed_currency': msg_content.get('instructedCurrency'),

            # Debtor (matching DB columns)
            'debtor_name': trunc(debtor.get('name'), 140),
            'debtor_iban': trunc(debtor_account.get('iban'), 34),
            'debtor_bic': debtor.get('bic'),
            'debtor_agent_bic': debtor_agent.get('bic'),

            # Creditor (matching DB columns)
            'creditor_name': trunc(creditor.get('name'), 140),
            'creditor_iban': trunc(creditor_account.get('iban'), 34),
            'creditor_bic': creditor.get('bic'),
            'creditor_agent_bic': creditor_agent.get('bic'),

            # Purpose & Charges
            'purpose_code': msg_content.get('purposeCode'),
            'category_purpose': trunc(pmt_info.get('categoryPurpose'), 35),
            'charge_bearer': msg_content.get('chargeBearer'),

            # Remittance Information
            'remittance_info': trunc(remittance_info.get('unstructured'), 140) if remittance_info else None,
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'msg_id', 'creation_date_time', 'number_of_transactions',
            'instruction_id', 'end_to_end_id',
            'instructed_amount', 'instructed_currency',
            'debtor_name', 'debtor_iban', 'debtor_bic', 'debtor_agent_bic',
            'creditor_name', 'creditor_iban', 'creditor_bic', 'creditor_agent_bic',
            'purpose_code', 'category_purpose', 'charge_bearer',
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
        silver_data: Dict[str, Any],
        stg_id: str,
        batch_id: str
    ) -> GoldEntities:
        """Extract Gold layer entities from SEPA Silver record.

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
                party_type='ORGANIZATION' if silver_data.get('creditor_id') else 'UNKNOWN',
                country='XX',
            ))

        # Creditor Party
        if silver_data.get('creditor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('creditor_name'),
                role="CREDITOR",
                party_type='ORGANIZATION' if silver_data.get('creditor_id') else 'UNKNOWN',
                country='XX',
            ))

        # Debtor Account
        if silver_data.get('debtor_iban'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('debtor_iban'),
                role="DEBTOR",
                iban=silver_data.get('debtor_iban'),
                account_type='CACC',
                currency=silver_data.get('instructed_currency') or 'EUR',
            ))

        # Creditor Account
        if silver_data.get('creditor_iban'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('creditor_iban'),
                role="CREDITOR",
                iban=silver_data.get('creditor_iban'),
                account_type='CACC',
                currency='EUR',
            ))

        # Debtor Agent
        if silver_data.get('debtor_agent_bic') or silver_data.get('debtor_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                bic=silver_data.get('debtor_agent_bic') or silver_data.get('debtor_bic'),
                country='XX',
            ))

        # Creditor Agent
        if silver_data.get('creditor_agent_bic') or silver_data.get('creditor_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                bic=silver_data.get('creditor_agent_bic') or silver_data.get('creditor_bic'),
                country='XX',
            ))

        # SEPA-specific fields
        entities.category_purpose = silver_data.get('category_purpose')

        return entities


# Register the extractor
ExtractorRegistry.register('SEPA', SepaExtractor())
ExtractorRegistry.register('sepa', SepaExtractor())
ExtractorRegistry.register('SEPA_CT', SepaExtractor())
