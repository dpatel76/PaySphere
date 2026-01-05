"""ISO 20022 camt.053 (Bank to Customer Statement) Extractor.

camt.053 is a statement message (not payment initiation) with this structure:
- BkToCstmrStmt (root)
  - GrpHdr (Group Header - message metadata)
  - Stmt (Statement - can repeat)
    - Acct (Account information)
    - Bal (Balance - opening OPBD, closing CLBD, etc.)
    - TxsSummry (Transaction Summary)
    - Ntry (Entry - individual statement entries, can repeat)
      - NtryDtls (Entry Details)
        - TxDtls (Transaction Details)
          - RltdPties (Related Parties - Debtor, Creditor)
          - RltdAgts (Related Agents - banks)
          - RmtInf (Remittance Information)
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


class Camt053Parser:
    """Parser for camt.053 XML messages."""

    # ISO 20022 namespaces for camt.053
    NAMESPACES = {
        'camt': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.08',
        'camt_02': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.02',
        'camt_06': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.06',
    }

    @classmethod
    def strip_namespace(cls, xml_string: str) -> str:
        """Remove namespace declarations from XML for easier parsing."""
        # Remove namespace prefixes and declarations
        xml_string = re.sub(r'\sxmlns[^"]*"[^"]*"', '', xml_string)
        xml_string = re.sub(r'<(\/?)\w+:', r'<\1', xml_string)
        return xml_string

    @classmethod
    def parse(cls, raw_content: Any) -> Dict[str, Any]:
        """Parse camt.053 XML into structured dict.

        Args:
            raw_content: XML string or pre-parsed dict

        Returns:
            Dict with standardized field names matching Silver table columns
        """
        # If already parsed dict, return as-is
        if isinstance(raw_content, dict):
            return raw_content

        # Parse XML
        xml_str = raw_content if isinstance(raw_content, str) else str(raw_content)
        xml_str = cls.strip_namespace(xml_str)

        try:
            root = ET.fromstring(xml_str)
        except ET.ParseError as e:
            logger.warning(f"Failed to parse camt.053 XML: {e}")
            return {'parseError': str(e)}

        result = {}

        # =====================================================================
        # GROUP HEADER (GrpHdr)
        # =====================================================================
        grp_hdr = root.find('.//GrpHdr')
        if grp_hdr is not None:
            result['msgId'] = cls._get_text(grp_hdr, 'MsgId')
            result['creationDateTime'] = cls._get_text(grp_hdr, 'CreDtTm')

        # =====================================================================
        # STATEMENT (Stmt) - Take first statement
        # =====================================================================
        stmt = root.find('.//Stmt')
        if stmt is not None:
            result['statementId'] = cls._get_text(stmt, 'Id')
            result['sequenceNumber'] = cls._get_text(stmt, 'ElctrncSeqNb')

            # From/To Date Range
            fr_to_dt = stmt.find('FrToDt')
            if fr_to_dt is not None:
                result['fromDate'] = cls._get_text(fr_to_dt, 'FrDtTm') or cls._get_text(fr_to_dt, 'FrDt')
                result['toDate'] = cls._get_text(fr_to_dt, 'ToDtTm') or cls._get_text(fr_to_dt, 'ToDt')

            # Account Information
            acct = stmt.find('Acct')
            if acct is not None:
                # Account ID - IBAN or Other
                acct_id = acct.find('Id')
                if acct_id is not None:
                    result['accountIban'] = cls._get_text(acct_id, 'IBAN')
                    othr = acct_id.find('Othr')
                    if othr is not None:
                        result['accountNumber'] = cls._get_text(othr, 'Id')
                        scheme = othr.find('SchmeNm')
                        if scheme is not None:
                            result['accountScheme'] = cls._get_text(scheme, 'Cd') or cls._get_text(scheme, 'Prtry')

                result['accountCurrency'] = cls._get_text(acct, 'Ccy')
                result['accountName'] = cls._get_text(acct, 'Nm')

                # Account Type
                acct_tp = acct.find('Tp')
                if acct_tp is not None:
                    result['accountType'] = cls._get_text(acct_tp, 'Cd') or cls._get_text(acct_tp, 'Prtry')

                # Account Owner
                ownr = acct.find('Ownr')
                if ownr is not None:
                    result['accountOwnerName'] = cls._get_text(ownr, 'Nm')
                    # Owner Address
                    pstl_adr = ownr.find('PstlAdr')
                    if pstl_adr is not None:
                        result['accountOwnerStreet'] = cls._get_text(pstl_adr, 'StrtNm')
                        result['accountOwnerBuildingNumber'] = cls._get_text(pstl_adr, 'BldgNb')
                        result['accountOwnerPostCode'] = cls._get_text(pstl_adr, 'PstCd')
                        result['accountOwnerTown'] = cls._get_text(pstl_adr, 'TwnNm')
                        result['accountOwnerCountry'] = cls._get_text(pstl_adr, 'Ctry')
                    # Owner ID
                    ownr_id = ownr.find('Id')
                    if ownr_id is not None:
                        org_id = ownr_id.find('OrgId')
                        if org_id is not None:
                            result['accountOwnerBic'] = cls._get_text(org_id, 'AnyBIC')
                            result['accountOwnerLei'] = cls._get_text(org_id, 'LEI')
                            othr = org_id.find('Othr')
                            if othr is not None:
                                result['accountOwnerId'] = cls._get_text(othr, 'Id')

                # Account Servicer (Bank)
                svcr = acct.find('Svcr')
                if svcr is not None:
                    fin_instn = svcr.find('FinInstnId')
                    if fin_instn is not None:
                        result['accountServicerBic'] = cls._get_text(fin_instn, 'BICFI')
                        result['accountServicerLei'] = cls._get_text(fin_instn, 'LEI')
                        result['accountServicerName'] = cls._get_text(fin_instn, 'Nm')
                        clr = fin_instn.find('ClrSysMmbId')
                        if clr is not None:
                            result['accountServicerMemberId'] = cls._get_text(clr, 'MmbId')

            # =====================================================================
            # BALANCES (Bal) - Extract opening (OPBD) and closing (CLBD)
            # =====================================================================
            for bal in stmt.findall('Bal'):
                bal_tp = bal.find('Tp/CdOrPrtry/Cd')
                if bal_tp is not None:
                    bal_type = bal_tp.text
                    if bal_type == 'OPBD':  # Opening Booked
                        result['openingBalance'] = cls._extract_balance(bal)
                    elif bal_type == 'CLBD':  # Closing Booked
                        result['closingBalance'] = cls._extract_balance(bal)
                    elif bal_type == 'OPAV':  # Opening Available
                        result['openingAvailableBalance'] = cls._extract_balance(bal)
                    elif bal_type == 'CLAV':  # Closing Available
                        result['closingAvailableBalance'] = cls._extract_balance(bal)

            # Capture first balance type found for reference
            first_bal = stmt.find('Bal')
            if first_bal is not None:
                result['balanceType'] = cls._get_text(first_bal, 'Tp/CdOrPrtry/Cd')
                result['balanceAmount'] = cls._get_text(first_bal, 'Amt')
                amt_elem = first_bal.find('Amt')
                if amt_elem is not None:
                    result['balanceCurrency'] = amt_elem.get('Ccy')

            # =====================================================================
            # TRANSACTION SUMMARY (TxsSummry)
            # =====================================================================
            txs_summry = stmt.find('TxsSummry')
            if txs_summry is not None:
                ttl_ntries = txs_summry.find('TtlNtries')
                if ttl_ntries is not None:
                    result['numberOfEntries'] = cls._get_int(ttl_ntries, 'NbOfNtries')
                    result['sumOfEntries'] = cls._get_decimal(ttl_ntries, 'Sum')

                # Credit entries
                cdt_ntries = txs_summry.find('TtlCdtNtries')
                if cdt_ntries is not None:
                    result['numberOfCreditEntries'] = cls._get_int(cdt_ntries, 'NbOfNtries')
                    result['sumOfCreditEntries'] = cls._get_decimal(cdt_ntries, 'Sum')

                # Debit entries
                dbt_ntries = txs_summry.find('TtlDbtNtries')
                if dbt_ntries is not None:
                    result['numberOfDebitEntries'] = cls._get_int(dbt_ntries, 'NbOfNtries')
                    result['sumOfDebitEntries'] = cls._get_decimal(dbt_ntries, 'Sum')

            # =====================================================================
            # ENTRIES (Ntry) - Extract first entry details
            # =====================================================================
            entries = stmt.findall('Ntry')
            result['totalEntries'] = len(entries)

            if entries:
                first_entry = entries[0]
                result['entriesReference'] = cls._get_text(first_entry, 'NtryRef')
                result['entriesAmount'] = cls._get_text(first_entry, 'Amt')
                amt_elem = first_entry.find('Amt')
                if amt_elem is not None:
                    result['entriesCurrency'] = amt_elem.get('Ccy')
                result['entriesCreditDebitIndicator'] = cls._get_text(first_entry, 'CdtDbtInd')
                result['entriesStatus'] = cls._get_text(first_entry, 'Sts/Cd') or cls._get_text(first_entry, 'Sts')
                result['entriesBookingDate'] = cls._get_text(first_entry, 'BookgDt/Dt') or cls._get_text(first_entry, 'BookgDt/DtTm')
                result['entriesValueDate'] = cls._get_text(first_entry, 'ValDt/Dt') or cls._get_text(first_entry, 'ValDt/DtTm')
                result['entriesAccountServicerRef'] = cls._get_text(first_entry, 'AcctSvcrRef')

                # Bank Transaction Code
                bk_tx_cd = first_entry.find('BkTxCd')
                if bk_tx_cd is not None:
                    domn = bk_tx_cd.find('Domn')
                    if domn is not None:
                        result['entriesDomainCode'] = cls._get_text(domn, 'Cd')
                        fmly = domn.find('Fmly')
                        if fmly is not None:
                            result['entriesFamilyCode'] = cls._get_text(fmly, 'Cd')
                            result['entriesSubFamilyCode'] = cls._get_text(fmly, 'SubFmlyCd')
                    prtry = bk_tx_cd.find('Prtry')
                    if prtry is not None:
                        result['entriesProprietaryCode'] = cls._get_text(prtry, 'Cd')
                        result['entriesProprietaryIssuer'] = cls._get_text(prtry, 'Issr')

                # Entry Details - Transaction Details from first entry
                ntry_dtls = first_entry.find('NtryDtls')
                if ntry_dtls is not None:
                    tx_dtls = ntry_dtls.find('TxDtls')
                    if tx_dtls is not None:
                        result['transactionDetails'] = cls._extract_transaction_details(tx_dtls)

            # Store all entries as JSON for later processing
            result['entriesList'] = [cls._extract_entry(e) for e in entries[:10]]  # First 10 entries

        return result

    @classmethod
    def _extract_balance(cls, bal: ET.Element) -> Dict[str, Any]:
        """Extract balance information."""
        result = {}
        amt_elem = bal.find('Amt')
        if amt_elem is not None:
            result['amount'] = amt_elem.text
            result['currency'] = amt_elem.get('Ccy')
        result['creditDebitIndicator'] = cls._get_text(bal, 'CdtDbtInd')
        result['date'] = cls._get_text(bal, 'Dt/Dt') or cls._get_text(bal, 'Dt/DtTm')
        return result

    @classmethod
    def _extract_entry(cls, entry: ET.Element) -> Dict[str, Any]:
        """Extract single entry information."""
        result = {
            'reference': cls._get_text(entry, 'NtryRef'),
            'amount': cls._get_text(entry, 'Amt'),
            'creditDebit': cls._get_text(entry, 'CdtDbtInd'),
            'status': cls._get_text(entry, 'Sts/Cd'),
            'bookingDate': cls._get_text(entry, 'BookgDt/Dt'),
            'valueDate': cls._get_text(entry, 'ValDt/Dt'),
        }
        amt_elem = entry.find('Amt')
        if amt_elem is not None:
            result['currency'] = amt_elem.get('Ccy')
        return result

    @classmethod
    def _extract_transaction_details(cls, tx_dtls: ET.Element) -> Dict[str, Any]:
        """Extract transaction details from entry."""
        result = {}

        # References
        refs = tx_dtls.find('Refs')
        if refs is not None:
            result['endToEndId'] = cls._get_text(refs, 'EndToEndId')
            result['uetr'] = cls._get_text(refs, 'UETR')
            result['transactionId'] = cls._get_text(refs, 'TxId')
            result['instructionId'] = cls._get_text(refs, 'InstrId')
            result['paymentInfoId'] = cls._get_text(refs, 'PmtInfId')
            result['clearingSystemRef'] = cls._get_text(refs, 'ClrSysRef')

        # Related Parties
        rltd_pties = tx_dtls.find('RltdPties')
        if rltd_pties is not None:
            # Debtor
            dbtr = rltd_pties.find('Dbtr')
            if dbtr is not None:
                result['debtorName'] = cls._get_text(dbtr, 'Nm')
            dbtr_acct = rltd_pties.find('DbtrAcct/Id')
            if dbtr_acct is not None:
                result['debtorIban'] = cls._get_text(dbtr_acct, 'IBAN')
            # Creditor
            cdtr = rltd_pties.find('Cdtr')
            if cdtr is not None:
                result['creditorName'] = cls._get_text(cdtr, 'Nm')
            cdtr_acct = rltd_pties.find('CdtrAcct/Id')
            if cdtr_acct is not None:
                result['creditorIban'] = cls._get_text(cdtr_acct, 'IBAN')

        # Related Agents
        rltd_agts = tx_dtls.find('RltdAgts')
        if rltd_agts is not None:
            dbtr_agt = rltd_agts.find('DbtrAgt/FinInstnId')
            if dbtr_agt is not None:
                result['debtorAgentBic'] = cls._get_text(dbtr_agt, 'BICFI')
            cdtr_agt = rltd_agts.find('CdtrAgt/FinInstnId')
            if cdtr_agt is not None:
                result['creditorAgentBic'] = cls._get_text(cdtr_agt, 'BICFI')

        # Remittance Information
        rmt_inf = tx_dtls.find('RmtInf')
        if rmt_inf is not None:
            result['remittanceUnstructured'] = cls._get_text(rmt_inf, 'Ustrd')
            strd = rmt_inf.find('Strd')
            if strd is not None:
                result['creditorReference'] = cls._get_text(strd, 'CdtrRefInf/Ref')

        # Purpose
        purp = tx_dtls.find('Purp')
        if purp is not None:
            result['purposeCode'] = cls._get_text(purp, 'Cd')
            result['purposeProprietary'] = cls._get_text(purp, 'Prtry')

        return result

    @classmethod
    def _get_text(cls, elem: Optional[ET.Element], path: str) -> Optional[str]:
        """Safely get text content from XML element."""
        if elem is None:
            return None
        found = elem.find(path)
        return found.text if found is not None else None

    @classmethod
    def _get_int(cls, elem: Optional[ET.Element], path: str) -> Optional[int]:
        """Get integer value from XML element."""
        text = cls._get_text(elem, path)
        if text:
            try:
                return int(text)
            except ValueError:
                return None
        return None

    @classmethod
    def _get_decimal(cls, elem: Optional[ET.Element], path: str) -> Optional[float]:
        """Get decimal value from XML element."""
        text = cls._get_text(elem, path)
        if text:
            try:
                return float(text)
            except ValueError:
                return None
        return None


class Camt053ParserWrapper:
    """Wrapper around Camt053Parser to provide instance-level parse method."""

    def parse(self, content: Any) -> Dict[str, Any]:
        """Parse camt.053 XML content."""
        return Camt053Parser.parse(content)


class Camt053Extractor(BaseExtractor):
    """Extractor for ISO 20022 camt.053 Bank to Customer Statement messages."""

    MESSAGE_TYPE = "camt.053"
    SILVER_TABLE = "stg_camt053"

    def __init__(self):
        """Initialize extractor with parser instance."""
        super().__init__()
        self.parser = Camt053ParserWrapper()

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw camt.053 content."""
        # Parse if XML string
        if isinstance(raw_content, str) and raw_content.strip().startswith('<'):
            parsed = Camt053Parser.parse(raw_content)
            msg_id = parsed.get('msgId', '') or parsed.get('statementId', '')
            return {
                'raw_id': self.generate_raw_id(msg_id),
                'message_type': self.MESSAGE_TYPE,
                'raw_content': raw_content,  # Store original XML
                'batch_id': batch_id,
            }
        else:
            # Pre-parsed dict
            msg_id = raw_content.get('msgId', '') or raw_content.get('statementId', '')
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
        """Extract all Silver layer fields from camt.053 message."""
        trunc = self.trunc

        # Parse XML if needed
        if isinstance(msg_content, str) and msg_content.strip().startswith('<'):
            msg_content = Camt053Parser.parse(msg_content)

        # Extract nested objects with defaults
        opening_balance = msg_content.get('openingBalance') or {}
        closing_balance = msg_content.get('closingBalance') or {}

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'camt.053',
            'msg_id': trunc(msg_content.get('msgId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),

            # Statement Identification
            'statement_id': trunc(msg_content.get('statementId'), 35),
            'sequence_number': msg_content.get('sequenceNumber'),
            'from_date': msg_content.get('fromDate'),
            'to_date': msg_content.get('toDate'),

            # Account Information
            'account_iban': trunc(msg_content.get('accountIban'), 34),
            'account_number': trunc(msg_content.get('accountNumber'), 34),
            'account_currency': msg_content.get('accountCurrency') or 'XXX',
            'account_owner_name': trunc(msg_content.get('accountOwnerName'), 140),
            'account_servicer_bic': trunc(msg_content.get('accountServicerBic'), 11),

            # Opening Balance
            'opening_balance_amount': opening_balance.get('amount'),
            'opening_balance_currency': opening_balance.get('currency'),
            'opening_balance_credit_debit': opening_balance.get('creditDebitIndicator'),
            'opening_balance_date': opening_balance.get('date'),

            # Closing Balance
            'closing_balance_amount': closing_balance.get('amount'),
            'closing_balance_currency': closing_balance.get('currency'),
            'closing_balance_credit_debit': closing_balance.get('creditDebitIndicator'),
            'closing_balance_date': closing_balance.get('date'),

            # Entry Summary
            'number_of_entries': msg_content.get('numberOfEntries'),
            'sum_of_entries': msg_content.get('sumOfEntries'),

            # Additional Silver columns (from DB schema)
            'processing_status': 'PENDING',
            'account_id_iban': trunc(msg_content.get('accountIban'), 34),
            'account_owner': trunc(msg_content.get('accountOwnerName'), 140),
            'servicer_bic': trunc(msg_content.get('accountServicerBic'), 11),

            # Balance type from first balance
            'balance_type': msg_content.get('balanceType'),
            'balance_amount': msg_content.get('balanceAmount'),
            'balance_currency': msg_content.get('balanceCurrency'),

            # First entry details
            'entries_reference': trunc(msg_content.get('entriesReference'), 35),
            'entries_amount': msg_content.get('entriesAmount'),
            'entries_currency': msg_content.get('entriesCurrency'),
            'entries_credit_debit_indicator': msg_content.get('entriesCreditDebitIndicator'),
            'entries_status': msg_content.get('entriesStatus'),
            'entries_booking_date': msg_content.get('entriesBookingDate'),
            'entries_value_date': msg_content.get('entriesValueDate'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT.

        IMPORTANT: Must match actual database column names exactly.
        """
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'msg_id', 'creation_date_time',
            'statement_id', 'sequence_number', 'from_date', 'to_date',
            'account_iban', 'account_number', 'account_currency',
            'account_owner_name', 'account_servicer_bic',
            'opening_balance_amount', 'opening_balance_currency',
            'opening_balance_credit_debit', 'opening_balance_date',
            'closing_balance_amount', 'closing_balance_currency',
            'closing_balance_credit_debit', 'closing_balance_date',
            'number_of_entries', 'sum_of_entries',
            'processing_status',
            'account_id_iban', 'account_owner', 'servicer_bic',
            'balance_type', 'balance_amount', 'balance_currency',
            'entries_reference', 'entries_amount', 'entries_currency',
            'entries_credit_debit_indicator', 'entries_status',
            'entries_booking_date', 'entries_value_date',
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
        """Extract Gold layer entities from camt.053 Silver record.

        camt.053 is a statement format, so Gold mapping is:
        - Account Owner -> cdm_party (ACCOUNT_OWNER)
        - Statement Account -> cdm_account (STATEMENT_ACCOUNT)
        - Account Servicer Bank -> cdm_financial_institution (ACCOUNT_SERVICER)

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Account Owner Party - uses Silver column names
        account_owner_name = silver_data.get('account_owner_name') or silver_data.get('account_owner')
        if account_owner_name:
            entities.parties.append(PartyData(
                name=account_owner_name,
                role="ACCOUNT_OWNER",
                party_type='UNKNOWN',
            ))

        # Statement Account
        account_iban = silver_data.get('account_iban') or silver_data.get('account_id_iban')
        account_number = silver_data.get('account_number')
        if account_iban or account_number:
            entities.accounts.append(AccountData(
                account_number=account_number or account_iban,
                role="STATEMENT_ACCOUNT",
                iban=account_iban,
                account_type='CACC',
                currency=silver_data.get('account_currency') or 'XXX',
            ))

        # Account Servicer (Bank)
        servicer_bic = silver_data.get('account_servicer_bic') or silver_data.get('servicer_bic')
        if servicer_bic:
            # Extract country from BIC (positions 5-6)
            country = servicer_bic[4:6] if len(servicer_bic) >= 6 else 'XX'
            entities.financial_institutions.append(FinancialInstitutionData(
                role="ACCOUNT_SERVICER",
                bic=servicer_bic,
                country=country,
            ))

        return entities

    def get_extension_data(self, silver_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get ISO 20022 extension data for camt.053 statement.

        Returns data to be persisted to cdm_payment_extension_iso20022.
        """
        return {
            'message_type': 'camt.053',
            'message_definition': 'BankToCustomerStatement',
            'message_namespace': 'urn:iso:std:iso:20022:tech:xsd:camt.053',
            'statement_id': silver_data.get('statement_id'),
            'sequence_number': silver_data.get('sequence_number'),
            'from_date': silver_data.get('from_date'),
            'to_date': silver_data.get('to_date'),
            'opening_balance_credit_debit': silver_data.get('opening_balance_credit_debit'),
            'opening_balance_date': silver_data.get('opening_balance_date'),
            'closing_balance_credit_debit': silver_data.get('closing_balance_credit_debit'),
            'closing_balance_date': silver_data.get('closing_balance_date'),
            'number_of_entries': silver_data.get('number_of_entries'),
            'sum_of_entries': silver_data.get('sum_of_entries'),
            'balance_type': silver_data.get('balance_type'),
            'entries_reference': silver_data.get('entries_reference'),
            'entries_booking_date': silver_data.get('entries_booking_date'),
            'entries_value_date': silver_data.get('entries_value_date'),
            'entries_status': silver_data.get('entries_status'),
            'entries_credit_debit_indicator': silver_data.get('entries_credit_debit_indicator'),
        }


# Register the extractor with all aliases
ExtractorRegistry.register('camt.053', Camt053Extractor())
ExtractorRegistry.register('camt_053', Camt053Extractor())
ExtractorRegistry.register('camt053', Camt053Extractor())
ExtractorRegistry.register('CAMT.053', Camt053Extractor())
ExtractorRegistry.register('BkToCstmrStmt', Camt053Extractor())
