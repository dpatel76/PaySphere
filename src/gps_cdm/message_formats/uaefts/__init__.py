"""UAE UAEFTS (UAE Funds Transfer System) Extractor - ISO 20022 XML based.

ISO 20022 INHERITANCE HIERARCHY:
    UAEFTS uses UAE Central Bank ISO 20022 usage guidelines based on pacs.008.
    The UaeftsISO20022Parser inherits from Pacs008Parser.

    BaseISO20022Parser
        └── Pacs008Parser (FI to FI Customer Credit Transfer - pacs.008.001.08)
            └── UaeftsISO20022Parser (UAE Central Bank payment guidelines)

UAEFTS-SPECIFIC ELEMENTS:
    - UAE IBAN format (AE + 2 check digits + 3 bank code + 16 account number)
    - AED currency (UAE Dirhams)
    - BIC/SWIFT codes for UAE financial institutions
    - Real-time gross settlement

CLEARING SYSTEM:
    - AEUAE (UAE IBAN/BIC System)
    - Operated by UAE Central Bank

DATABASE TABLES:
    - Bronze: bronze.raw_payment_messages
    - Silver: silver.stg_uaefts
    - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_uaefts

MAPPING INHERITANCE:
    UAEFTS -> pacs.008.base (COMPLETE)
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
    logger.warning("ISO 20022 base classes not available - UAEFTS will use standalone implementation")


# =============================================================================
# UAEFTS ISO 20022 PARSER (inherits from Pacs008Parser)
# =============================================================================

# Use conditional inheritance pattern for backward compatibility
_UaeftsParserBase = Pacs008Parser if ISO20022_BASE_AVAILABLE else object


class UaeftsISO20022Parser(_UaeftsParserBase):
    """UAEFTS ISO 20022 pacs.008 parser with UAE Central Bank usage guidelines.

    Inherits from Pacs008Parser and adds UAEFTS-specific processing:
    - UAE IBAN format handling
    - BIC extraction for UAE financial institutions
    - UAEFTS-specific clearing system identification

    ISO 20022 Version: pacs.008.001.08
    Usage Guidelines: UAE Central Bank UAEFTS Service

    Inheritance Hierarchy:
        BaseISO20022Parser -> Pacs008Parser -> UaeftsISO20022Parser
    """

    # UAEFTS-specific constants
    CLEARING_SYSTEM = "AEUAE"  # UAE IBAN/BIC System
    DEFAULT_CURRENCY = "AED"
    MESSAGE_TYPE = "UAEFTS"

    def __init__(self):
        """Initialize UAEFTS parser."""
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse UAEFTS ISO 20022 pacs.008 message.

        Uses inherited pacs.008 parsing from Pacs008Parser and adds
        UAEFTS-specific fields.
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

        # Add UAEFTS-specific fields
        result['isUaefts'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM

        return result

    def _parse_standalone(self, raw_content: str) -> Dict[str, Any]:
        """Standalone parsing when base class not available."""
        legacy_parser = UaeftsXmlParser()
        return legacy_parser.parse(raw_content)


# =============================================================================
# LEGACY XML PARSER (kept for backward compatibility)
# =============================================================================


class UaeftsXmlParser:
    """Parser for UAEFTS ISO 20022 XML messages (pacs.008 based).

    Legacy parser kept for backward compatibility when ISO 20022 base classes
    are not available.
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

    def _safe_decimal(self, value: Optional[str]) -> Optional[float]:
        """Safely convert string to decimal."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse UAEFTS message content.

        Handles:
        1. Dict input (already parsed)
        2. JSON string input
        3. XML ISO 20022 format (pacs.008)
        """
        # Handle dict input (already parsed)
        if isinstance(raw_content, dict):
            return raw_content

        # Handle string input
        if isinstance(raw_content, str):
            content = raw_content.strip()

            # Try JSON first
            if content.startswith('{'):
                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    pass

            # Try XML parsing
            if content.startswith('<') or content.startswith('<?xml'):
                try:
                    # Handle BOM
                    if content.startswith('\ufeff'):
                        content = content[1:]
                    root = ET.fromstring(content)
                    return self._parse_iso20022(root)
                except ET.ParseError as e:
                    logger.error(f"Failed to parse UAEFTS XML: {e}")
                    raise ValueError(f"Invalid XML: {e}")

        # Return minimal dict on failure
        return {'messageType': 'UAEFTS'}

    def _parse_iso20022(self, root: ET.Element) -> Dict[str, Any]:
        """Parse UAEFTS ISO 20022 pacs.008 structure."""
        result = {'messageType': 'UAEFTS'}

        # Find FIToFICstmrCdtTrf element
        fi_transfer = self._find(root, 'FIToFICstmrCdtTrf')
        if fi_transfer is None:
            # Check if root IS the FIToFICstmrCdtTrf
            if self._strip_ns(root.tag) == 'FIToFICstmrCdtTrf':
                fi_transfer = root
            elif self._strip_ns(root.tag) == 'Document':
                # Document wrapper - look inside
                for child in root:
                    if self._strip_ns(child.tag) == 'FIToFICstmrCdtTrf':
                        fi_transfer = child
                        break

        if fi_transfer is None:
            logger.warning("No FIToFICstmrCdtTrf element found in UAEFTS XML")
            return result

        # Parse Group Header
        grp_hdr = self._find(fi_transfer, 'GrpHdr')
        if grp_hdr is not None:
            result['messageId'] = self._find_text(grp_hdr, 'MsgId')
            result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')
            result['numberOfTransactions'] = self._find_text(grp_hdr, 'NbOfTxs')
            result['settlementDate'] = self._find_text(grp_hdr, 'IntrBkSttlmDt')
            result['settlementMethod'] = self._find_text(grp_hdr, 'SttlmInf/SttlmMtd')

            # Instructing Agent
            instg_agt = self._find(grp_hdr, 'InstgAgt')
            if instg_agt is not None:
                result['instructingAgentBic'] = self._find_text(instg_agt, 'FinInstnId/BICFI')
                result['instructingAgentName'] = self._find_text(instg_agt, 'FinInstnId/Nm')

            # Instructed Agent
            instd_agt = self._find(grp_hdr, 'InstdAgt')
            if instd_agt is not None:
                result['instructedAgentBic'] = self._find_text(instd_agt, 'FinInstnId/BICFI')
                result['instructedAgentName'] = self._find_text(instd_agt, 'FinInstnId/Nm')

        # Parse Credit Transfer Transaction Info
        cdt_trf = self._find(fi_transfer, 'CdtTrfTxInf')
        if cdt_trf is not None:
            result.update(self._parse_transaction(cdt_trf))

        return result

    def _parse_transaction(self, tx: ET.Element) -> Dict[str, Any]:
        """Parse credit transfer transaction element."""
        result = {}

        # Payment ID
        pmt_id = self._find(tx, 'PmtId')
        if pmt_id is not None:
            result['instructionId'] = self._find_text(pmt_id, 'InstrId')
            result['endToEndId'] = self._find_text(pmt_id, 'EndToEndId')
            result['transactionId'] = self._find_text(pmt_id, 'TxId')
            result['uetr'] = self._find_text(pmt_id, 'UETR')

        # Payment Type Info
        pmt_tp = self._find(tx, 'PmtTpInf')
        if pmt_tp is not None:
            result['instructionPriority'] = self._find_text(pmt_tp, 'InstrPrty')
            result['serviceLevel'] = self._find_text(pmt_tp, 'SvcLvl/Prtry')
            result['localInstrument'] = self._find_text(pmt_tp, 'LclInstrm/Prtry')
            result['categoryPurpose'] = self._find_text(pmt_tp, 'CtgyPurp/Cd')

        # Amount
        result['amount'] = self._safe_decimal(self._find_text(tx, 'IntrBkSttlmAmt'))
        result['currency'] = self._find_attr(tx, 'IntrBkSttlmAmt', 'Ccy') or 'AED'
        result['interbankSettlementDate'] = self._find_text(tx, 'IntrBkSttlmDt')

        # Charge Bearer
        result['chargeBearer'] = self._find_text(tx, 'ChrgBr')

        # Debtor
        dbtr = self._find(tx, 'Dbtr')
        if dbtr is not None:
            result['debtorName'] = self._find_text(dbtr, 'Nm')
            result['debtorStreetName'] = self._find_text(dbtr, 'PstlAdr/StrtNm')
            result['debtorBuildingNumber'] = self._find_text(dbtr, 'PstlAdr/BldgNb')
            result['debtorPostCode'] = self._find_text(dbtr, 'PstlAdr/PstCd')
            result['debtorTownName'] = self._find_text(dbtr, 'PstlAdr/TwnNm')
            result['debtorCountry'] = self._find_text(dbtr, 'PstlAdr/Ctry')
            result['debtorLei'] = self._find_text(dbtr, 'Id/OrgId/LEI')
            result['debtorOtherId'] = self._find_text(dbtr, 'Id/OrgId/Othr/Id')

        # Debtor Account
        dbtr_acct = self._find(tx, 'DbtrAcct')
        if dbtr_acct is not None:
            result['debtorIban'] = self._find_text(dbtr_acct, 'Id/IBAN')
            result['debtorAccountType'] = self._find_text(dbtr_acct, 'Tp/Cd')
            result['debtorAccountCurrency'] = self._find_text(dbtr_acct, 'Ccy')
            result['debtorAccountName'] = self._find_text(dbtr_acct, 'Nm')

        # Debtor Agent
        dbtr_agt = self._find(tx, 'DbtrAgt')
        if dbtr_agt is not None:
            result['debtorAgentBic'] = self._find_text(dbtr_agt, 'FinInstnId/BICFI')
            result['debtorAgentName'] = self._find_text(dbtr_agt, 'FinInstnId/Nm')
            result['debtorAgentMemberId'] = self._find_text(dbtr_agt, 'FinInstnId/ClrSysMmbId/MmbId')
            result['debtorAgentCountry'] = self._find_text(dbtr_agt, 'FinInstnId/PstlAdr/Ctry')

        # Creditor Agent
        cdtr_agt = self._find(tx, 'CdtrAgt')
        if cdtr_agt is not None:
            result['creditorAgentBic'] = self._find_text(cdtr_agt, 'FinInstnId/BICFI')
            result['creditorAgentName'] = self._find_text(cdtr_agt, 'FinInstnId/Nm')
            result['creditorAgentMemberId'] = self._find_text(cdtr_agt, 'FinInstnId/ClrSysMmbId/MmbId')
            result['creditorAgentCountry'] = self._find_text(cdtr_agt, 'FinInstnId/PstlAdr/Ctry')

        # Creditor
        cdtr = self._find(tx, 'Cdtr')
        if cdtr is not None:
            result['creditorName'] = self._find_text(cdtr, 'Nm')
            result['creditorStreetName'] = self._find_text(cdtr, 'PstlAdr/StrtNm')
            result['creditorBuildingNumber'] = self._find_text(cdtr, 'PstlAdr/BldgNb')
            result['creditorPostCode'] = self._find_text(cdtr, 'PstlAdr/PstCd')
            result['creditorTownName'] = self._find_text(cdtr, 'PstlAdr/TwnNm')
            result['creditorCountry'] = self._find_text(cdtr, 'PstlAdr/Ctry')
            result['creditorLei'] = self._find_text(cdtr, 'Id/OrgId/LEI')
            result['creditorOtherId'] = self._find_text(cdtr, 'Id/OrgId/Othr/Id')

        # Creditor Account
        cdtr_acct = self._find(tx, 'CdtrAcct')
        if cdtr_acct is not None:
            result['creditorIban'] = self._find_text(cdtr_acct, 'Id/IBAN')
            result['creditorAccountType'] = self._find_text(cdtr_acct, 'Tp/Cd')
            result['creditorAccountCurrency'] = self._find_text(cdtr_acct, 'Ccy')
            result['creditorAccountName'] = self._find_text(cdtr_acct, 'Nm')

        # Purpose
        result['purposeCode'] = self._find_text(tx, 'Purp/Cd')

        # Remittance Information
        rmt_inf = self._find(tx, 'RmtInf')
        if rmt_inf is not None:
            result['remittanceUnstructured'] = self._find_text(rmt_inf, 'Ustrd')
            # Structured remittance
            strd = self._find(rmt_inf, 'Strd')
            if strd is not None:
                result['invoiceNumber'] = self._find_text(strd, 'RfrdDocInf/Nb')
                result['invoiceDate'] = self._find_text(strd, 'RfrdDocInf/RltdDt')

        return result


class UaeftsExtractor(BaseExtractor):
    """Extractor for UAE Funds Transfer System (UAEFTS) payment messages.

    ISO 20022 INHERITANCE:
        UAEFTS inherits from pacs.008 (FI to FI Customer Credit Transfer).
        The UaeftsISO20022Parser inherits from Pacs008Parser.
        Uses UAE Central Bank UAEFTS Service usage guidelines.

    Format Support:
        1. ISO 20022 XML (pacs.008.001.08) - Current standard

    UAEFTS-Specific Elements:
        - UAE IBAN format (AE + 2 check digits + 3 bank code + 16 account number)
        - AED currency (UAE Dirhams)
        - BIC/SWIFT codes for UAE financial institutions
        - Real-time gross settlement

    Database Tables:
        - Bronze: bronze.raw_payment_messages
        - Silver: silver.stg_uaefts
        - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_uaefts

    Inheritance Hierarchy:
        BaseExtractor -> UaeftsExtractor
        (Parser: Pacs008Parser -> UaeftsISO20022Parser)
    """

    MESSAGE_TYPE = "UAEFTS"
    SILVER_TABLE = "stg_iso20022_pacs008"  # Shared ISO 20022 pacs.008 table
    DEFAULT_CURRENCY = "AED"
    CLEARING_SYSTEM = "AEUAE"

    def __init__(self):
        """Initialize UAEFTS extractor with ISO 20022 parser."""
        self.iso20022_parser = UaeftsISO20022Parser()
        self.legacy_parser = UaeftsXmlParser()
        self.parser = self.iso20022_parser

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw UAEFTS content."""
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
        """Extract all Silver layer fields from UAEFTS message.

        Handles both legacy JSON format and ISO 20022 parsed format.
        """
        trunc = self.trunc

        # Handle nested objects for debtor/creditor (legacy JSON format)
        debtor = msg_content.get('debtor') or {}
        creditor = msg_content.get('creditor') or {}
        debtor_acct = msg_content.get('debtorAccount') or {}
        creditor_acct = msg_content.get('creditorAccount') or {}
        debtor_agent = msg_content.get('debtorAgent') or {}
        creditor_agent = msg_content.get('creditorAgent') or {}

        # Extract amount - try multiple paths (ISO 20022 and legacy)
        amount = (
            msg_content.get('amount') or
            msg_content.get('interbankSettlementAmount') or
            msg_content.get('instructedAmount')
        )

        # Extract currency - try multiple paths
        currency = (
            msg_content.get('currency') or
            msg_content.get('interbankSettlementCurrency') or
            msg_content.get('instructedCurrency') or
            'AED'
        )

        # Extract originator/debtor info (support both ISO 20022 parser output and legacy JSON)
        originator_name = (
            msg_content.get('debtorName') or
            msg_content.get('originatorName') or
            debtor.get('name')
        )
        originator_account = (
            msg_content.get('debtorIban') or
            msg_content.get('originatorAccount') or
            msg_content.get('debtorAccountNumber') or
            debtor_acct.get('accountNumber') or
            debtor_acct.get('iban')
        )

        # Extract beneficiary/creditor info
        beneficiary_name = (
            msg_content.get('creditorName') or
            msg_content.get('beneficiaryName') or
            creditor.get('name')
        )
        beneficiary_account = (
            msg_content.get('creditorIban') or
            msg_content.get('beneficiaryAccount') or
            msg_content.get('creditorAccountNumber') or
            creditor_acct.get('accountNumber') or
            creditor_acct.get('iban')
        )

        # Extract bank codes/BICs (support both ISO 20022 parser output and legacy)
        sending_bank_code = (
            msg_content.get('debtorAgentBic') or
            msg_content.get('sendingBankCode') or
            debtor_agent.get('bic') or
            debtor_agent.get('memberId')
        )
        receiving_bank_code = (
            msg_content.get('creditorAgentBic') or
            msg_content.get('receivingBankCode') or
            creditor_agent.get('bic') or
            creditor_agent.get('memberId')
        )

        # Extract transaction reference
        transaction_reference = (
            msg_content.get('transactionReference') or
            msg_content.get('endToEndId') or
            msg_content.get('instructionId')
        )

        # Extract settlement date
        settlement_date = (
            msg_content.get('settlementDate') or
            msg_content.get('interbankSettlementDate')
        )

        # Extract purpose
        purpose = (
            msg_content.get('purpose') or
            msg_content.get('purposeCode') or
            msg_content.get('remittanceUnstructured')
        )

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'UAEFTS',
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': settlement_date,

            # Amount
            'amount': amount,
            'currency': currency,

            # Bank Codes
            'sending_bank_code': trunc(sending_bank_code, 11),
            'receiving_bank_code': trunc(receiving_bank_code, 11),

            # Transaction Details
            'transaction_reference': trunc(transaction_reference, 35),

            # Originator (Debtor)
            'originator_name': trunc(originator_name, 140),
            'originator_account': trunc(originator_account, 34),
            'originator_address': msg_content.get('originatorAddress') or msg_content.get('debtorStreetName'),

            # Beneficiary (Creditor)
            'beneficiary_name': trunc(beneficiary_name, 140),
            'beneficiary_account': trunc(beneficiary_account, 34),
            'beneficiary_address': msg_content.get('beneficiaryAddress') or msg_content.get('creditorStreetName'),

            # Purpose
            'purpose': purpose,
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'message_id', 'creation_date_time',
            'settlement_date', 'amount', 'currency',
            'sending_bank_code', 'receiving_bank_code', 'transaction_reference',
            'originator_name', 'originator_account', 'originator_address',
            'beneficiary_name', 'beneficiary_account', 'beneficiary_address',
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
        """Extract Gold layer entities from UAEFTS Silver record.

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
                country='AE',
            ))

        # Beneficiary Party (Creditor)
        if silver_data.get('beneficiary_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('beneficiary_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='AE',
            ))

        # Originator Account
        if silver_data.get('originator_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('originator_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'AED',
            ))

        # Beneficiary Account
        if silver_data.get('beneficiary_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('beneficiary_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'AED',
            ))

        # Sending Bank (Debtor Agent)
        sending_bank = silver_data.get('sending_bank_code')
        if sending_bank:
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                bic=sending_bank if len(sending_bank) in (8, 11) else None,
                clearing_code=sending_bank if len(sending_bank) not in (8, 11) else None,
                clearing_system='AEUAEFTS',
                country='AE',
            ))

        # Receiving Bank (Creditor Agent)
        receiving_bank = silver_data.get('receiving_bank_code')
        if receiving_bank:
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                bic=receiving_bank if len(receiving_bank) in (8, 11) else None,
                clearing_code=receiving_bank if len(receiving_bank) not in (8, 11) else None,
                clearing_system='AEUAEFTS',
                country='AE',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('UAEFTS', UaeftsExtractor())
ExtractorRegistry.register('uaefts', UaeftsExtractor())
