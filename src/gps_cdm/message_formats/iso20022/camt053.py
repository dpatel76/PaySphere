"""ISO 20022 camt.053 Parser and Extractor base classes.

camt.053 (Bank to Customer Account Statement) is a statement message type used
for reporting account activity. Key characteristics:
- Bank → Customer communication (statement reporting, not payment initiation)
- Contains account information, balances, and transaction entries
- Used for cash management and reconciliation
- Different from payment messages (pacs/pain) which initiate transfers

Systems using camt.053 or its variants:
- Banks providing account statements (all ISO 20022 adopters)
- Cash management systems
- ERP integrations

Reference: ISO 20022 Message Definition Report - camt.053.001.08
"""

from typing import Dict, Any, List, Optional
import json
import logging

from .base_parser import BaseISO20022Parser
from .base_extractor import BaseISO20022Extractor

logger = logging.getLogger(__name__)


class Camt053Parser(BaseISO20022Parser):
    """Base parser for camt.053 Bank to Customer Account Statement messages.

    camt.053 structure:
    - Document
      - BkToCstmrStmt
        - GrpHdr (Group Header - message metadata)
        - Stmt (Statement - can repeat)
          - Acct (Account information)
          - Bal (Balance - opening, closing, etc.)
          - TxsSummry (Transaction Summary)
          - Ntry (Entry - individual transactions)
            - NtryDtls (Entry Details)
              - TxDtls (Transaction Details)

    Note: camt.053 is a statement/reporting message, not a payment initiation.
    The structure differs significantly from pacs.008/pain.001.
    """

    ROOT_ELEMENT = "BkToCstmrStmt"
    MESSAGE_TYPE = "camt.053"

    def parse(self, xml_content: str) -> Dict[str, Any]:
        """Parse camt.053 Bank to Customer Statement message.

        Args:
            xml_content: Raw XML string

        Returns:
            Dict with all extracted camt.053 fields
        """
        root = self._parse_xml(xml_content)

        # Find the BkToCstmrStmt element
        stmt_root = self._find(root, self.ROOT_ELEMENT)
        if stmt_root is None:
            root_tag = self._strip_ns(root.tag)
            if root_tag == self.ROOT_ELEMENT:
                stmt_root = root
            else:
                raise ValueError(f"Cannot find {self.ROOT_ELEMENT} element in camt.053 message")

        return self._parse_bank_to_customer_statement(stmt_root)

    def _parse_bank_to_customer_statement(self, stmt_root) -> Dict[str, Any]:
        """Parse BkToCstmrStmt element.

        Args:
            stmt_root: BkToCstmrStmt element

        Returns:
            Dict with extracted fields
        """
        result = {
            'isISO20022': True,
            'messageTypeCode': 'camt.053',
            'messageDefinition': 'BankToCustomerStatement',
        }

        # Extract Group Header
        result.update(self._extract_camt053_group_header(stmt_root))

        # Extract first Statement
        stmt = self._find(stmt_root, 'Stmt')
        if stmt is not None:
            result.update(self._parse_statement(stmt))

        return result

    def _extract_camt053_group_header(self, stmt_root) -> Dict[str, Any]:
        """Extract Group Header from camt.053.

        camt.053 GrpHdr contains:
        - MsgId: Message identification
        - CreDtTm: Creation date/time
        - MsgRcpt: Message recipient (optional)
        - MsgPgntn: Pagination info (for large statements)

        Args:
            stmt_root: BkToCstmrStmt element

        Returns:
            Dict with extracted header fields
        """
        result = {}
        grp_hdr = self._find(stmt_root, 'GrpHdr')

        if grp_hdr is None:
            return result

        # Core identification
        result['messageId'] = self._find_text(grp_hdr, 'MsgId')
        result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')

        # Message Recipient
        msg_rcpt = self._find(grp_hdr, 'MsgRcpt')
        if msg_rcpt:
            result.update(self._extract_party(msg_rcpt, 'messageRecipient'))

        # Pagination
        msg_pgntn = self._find(grp_hdr, 'MsgPgntn')
        if msg_pgntn:
            result['pageNumber'] = self._safe_int(self._find_text(msg_pgntn, 'PgNb'))
            result['lastPageIndicator'] = self._find_text(msg_pgntn, 'LastPgInd') == 'true'

        # Additional Header Info (for certain implementations)
        addtl_inf = self._find(grp_hdr, 'AddtlInf')
        if addtl_inf is not None:
            result['additionalInfo'] = addtl_inf.text

        return result

    def _parse_statement(self, stmt) -> Dict[str, Any]:
        """Parse Stmt (Statement) element.

        Statement contains:
        - Id: Statement identification
        - ElctrncSeqNb: Electronic sequence number
        - LglSeqNb: Legal sequence number
        - CreDtTm: Statement creation date
        - FrToDt: Period covered (from/to dates)
        - Acct: Account information
        - Bal: Balances (opening, closing, available, etc.)
        - TxsSummry: Transaction summary
        - Ntry: Individual entries

        Args:
            stmt: Stmt element

        Returns:
            Dict with statement fields
        """
        result = {}

        # Statement Identification
        result['statementId'] = self._find_text(stmt, 'Id')
        result['electronicSequenceNumber'] = self._safe_int(self._find_text(stmt, 'ElctrncSeqNb'))
        result['legalSequenceNumber'] = self._safe_int(self._find_text(stmt, 'LglSeqNb'))
        result['statementCreationDateTime'] = self._find_text(stmt, 'CreDtTm')

        # Copy Statement Flag
        result['copyDuplicateIndicator'] = self._find_text(stmt, 'CpyDplctInd')

        # Reporting Source
        rptg_src = self._find(stmt, 'RptgSrc')
        if rptg_src:
            result['reportingSourceCode'] = self._find_text(rptg_src, 'Cd')
            result['reportingSourceProprietary'] = self._find_text(rptg_src, 'Prtry')

        # Period (From/To Date)
        fr_to_dt = self._find(stmt, 'FrToDt')
        if fr_to_dt is not None:
            result['fromDateTime'] = (
                self._find_text(fr_to_dt, 'FrDtTm') or
                self._find_text(fr_to_dt, 'FrDt')
            )
            result['toDateTime'] = (
                self._find_text(fr_to_dt, 'ToDtTm') or
                self._find_text(fr_to_dt, 'ToDt')
            )

        # Account Information
        acct = self._find(stmt, 'Acct')
        if acct is not None:
            result.update(self._parse_statement_account(acct))

        # Balances
        result.update(self._parse_balances(stmt))

        # Transaction Summary
        txs_summry = self._find(stmt, 'TxsSummry')
        if txs_summry is not None:
            result.update(self._parse_transaction_summary(txs_summry))

        # Interest (for interest-bearing accounts)
        intrst = self._find(stmt, 'Intrst')
        if intrst is not None:
            result.update(self._parse_interest(intrst))

        # Entries (parse first entry for Silver, collect all for reference)
        entries = self._find_all(stmt, 'Ntry')
        result['totalEntries'] = len(entries)

        if entries:
            first_entry = entries[0]
            result.update(self._parse_entry(first_entry, 'firstEntry'))

            # Collect entries list (first 10 for reference)
            result['entriesList'] = [
                self._extract_entry_summary(e) for e in entries[:10]
            ]

        return result

    def _parse_statement_account(self, acct) -> Dict[str, Any]:
        """Parse Account element in statement.

        Account contains:
        - Id: Account identifier (IBAN or Other)
        - Tp: Account type
        - Ccy: Currency
        - Nm: Account name
        - Ownr: Account owner
        - Svcr: Account servicer (bank)

        Args:
            acct: Acct element

        Returns:
            Dict with account fields
        """
        result = {}

        # Account Identifier
        acct_id = self._find(acct, 'Id')
        if acct_id is not None:
            result['accountIban'] = self._find_text(acct_id, 'IBAN')

            othr = self._find(acct_id, 'Othr')
            if othr is not None:
                result['accountNumber'] = self._find_text(othr, 'Id')
                scheme = self._find(othr, 'SchmeNm')
                if scheme is not None:
                    result['accountScheme'] = (
                        self._find_text(scheme, 'Cd') or
                        self._find_text(scheme, 'Prtry')
                    )
                result['accountIssuer'] = self._find_text(othr, 'Issr')

        # Account Type
        acct_tp = self._find(acct, 'Tp')
        if acct_tp is not None:
            result['accountTypeCode'] = self._find_text(acct_tp, 'Cd')
            result['accountTypeProprietary'] = self._find_text(acct_tp, 'Prtry')

        # Currency and Name
        result['accountCurrency'] = self._find_text(acct, 'Ccy')
        result['accountName'] = self._find_text(acct, 'Nm')

        # Account Owner
        ownr = self._find(acct, 'Ownr')
        if ownr is not None:
            result.update(self._extract_party(ownr, 'accountOwner'))

        # Account Servicer (Bank)
        svcr = self._find(acct, 'Svcr')
        if svcr is not None:
            result.update(self._extract_financial_institution(svcr, 'accountServicer'))

        return result

    def _parse_balances(self, stmt) -> Dict[str, Any]:
        """Parse all Balance elements in statement.

        ISO 20022 defines several balance types:
        - OPBD: Opening Booked Balance
        - CLBD: Closing Booked Balance
        - OPAV: Opening Available Balance
        - CLAV: Closing Available Balance
        - INFO: Information Balance
        - PRCD: Previously Closed Booked
        - ITBD: Interim Booked

        Args:
            stmt: Stmt element

        Returns:
            Dict with balance fields
        """
        result = {}

        for bal in self._find_all(stmt, 'Bal'):
            # Get balance type
            bal_type = self._find_text(bal, 'Tp/CdOrPrtry/Cd')
            if not bal_type:
                bal_type = self._find_text(bal, 'Tp/CdOrPrtry/Prtry')

            # Extract balance data
            bal_data = self._extract_balance(bal)

            # Map to standard field names based on type
            if bal_type == 'OPBD':  # Opening Booked
                result['openingBookedAmount'] = bal_data.get('amount')
                result['openingBookedCurrency'] = bal_data.get('currency')
                result['openingBookedCreditDebit'] = bal_data.get('creditDebitIndicator')
                result['openingBookedDate'] = bal_data.get('date')
            elif bal_type == 'CLBD':  # Closing Booked
                result['closingBookedAmount'] = bal_data.get('amount')
                result['closingBookedCurrency'] = bal_data.get('currency')
                result['closingBookedCreditDebit'] = bal_data.get('creditDebitIndicator')
                result['closingBookedDate'] = bal_data.get('date')
            elif bal_type == 'OPAV':  # Opening Available
                result['openingAvailableAmount'] = bal_data.get('amount')
                result['openingAvailableCurrency'] = bal_data.get('currency')
                result['openingAvailableCreditDebit'] = bal_data.get('creditDebitIndicator')
                result['openingAvailableDate'] = bal_data.get('date')
            elif bal_type == 'CLAV':  # Closing Available
                result['closingAvailableAmount'] = bal_data.get('amount')
                result['closingAvailableCurrency'] = bal_data.get('currency')
                result['closingAvailableCreditDebit'] = bal_data.get('creditDebitIndicator')
                result['closingAvailableDate'] = bal_data.get('date')
            elif bal_type == 'ITBD':  # Interim Booked
                result['interimBookedAmount'] = bal_data.get('amount')
                result['interimBookedCurrency'] = bal_data.get('currency')
            elif bal_type == 'PRCD':  # Previously Closed Booked
                result['previouslyClosedAmount'] = bal_data.get('amount')
                result['previouslyClosedCurrency'] = bal_data.get('currency')

        # Also capture first balance for generic reference
        first_bal = self._find(stmt, 'Bal')
        if first_bal is not None:
            result['balanceType'] = self._find_text(first_bal, 'Tp/CdOrPrtry/Cd')
            amt_elem = self._find(first_bal, 'Amt')
            if amt_elem is not None:
                result['balanceAmount'] = self._safe_float(amt_elem.text)
                result['balanceCurrency'] = amt_elem.get('Ccy')

        return result

    def _extract_balance(self, bal) -> Dict[str, Any]:
        """Extract balance information from a Bal element.

        Args:
            bal: Bal element

        Returns:
            Dict with balance data
        """
        result = {}

        # Amount and Currency
        amt_elem = self._find(bal, 'Amt')
        if amt_elem is not None:
            result['amount'] = self._safe_float(amt_elem.text)
            result['currency'] = amt_elem.get('Ccy')

        # Credit/Debit Indicator
        result['creditDebitIndicator'] = self._find_text(bal, 'CdtDbtInd')

        # Date
        result['date'] = (
            self._find_text(bal, 'Dt/Dt') or
            self._find_text(bal, 'Dt/DtTm')
        )

        return result

    def _parse_transaction_summary(self, txs_summry) -> Dict[str, Any]:
        """Parse TxsSummry (Transaction Summary) element.

        Args:
            txs_summry: TxsSummry element

        Returns:
            Dict with summary fields
        """
        result = {}

        # Total Entries
        ttl_ntries = self._find(txs_summry, 'TtlNtries')
        if ttl_ntries is not None:
            result['summaryNumberOfEntries'] = self._safe_int(self._find_text(ttl_ntries, 'NbOfNtries'))
            result['summarySum'] = self._safe_float(self._find_text(ttl_ntries, 'Sum'))
            result['summaryTotalNetEntry'] = self._safe_float(self._find_text(ttl_ntries, 'TtlNetNtryAmt'))
            result['summaryNetCreditDebit'] = self._find_text(ttl_ntries, 'CdtDbtInd')

        # Credit Entries
        ttl_cdt = self._find(txs_summry, 'TtlCdtNtries')
        if ttl_cdt is not None:
            result['summaryCreditEntries'] = self._safe_int(self._find_text(ttl_cdt, 'NbOfNtries'))
            result['summaryCreditSum'] = self._safe_float(self._find_text(ttl_cdt, 'Sum'))

        # Debit Entries
        ttl_dbt = self._find(txs_summry, 'TtlDbtNtries')
        if ttl_dbt is not None:
            result['summaryDebitEntries'] = self._safe_int(self._find_text(ttl_dbt, 'NbOfNtries'))
            result['summaryDebitSum'] = self._safe_float(self._find_text(ttl_dbt, 'Sum'))

        return result

    def _parse_interest(self, intrst) -> Dict[str, Any]:
        """Parse Interest element.

        Args:
            intrst: Intrst element

        Returns:
            Dict with interest fields
        """
        result = {}

        # Interest Type
        result['interestType'] = self._find_text(intrst, 'Tp/Cd')

        # Interest Rate
        rate = self._find(intrst, 'Rate')
        if rate is not None:
            result['interestRate'] = self._safe_float(self._find_text(rate, 'Pctg'))
            result['interestRateType'] = self._find_text(rate, 'Tp')

        # Interest Amount
        amt = self._find(intrst, 'Amt')
        if amt is not None:
            result['interestAmount'] = self._safe_float(amt.text)
            result['interestCurrency'] = amt.get('Ccy')

        # Period
        fr_to_dt = self._find(intrst, 'FrToDt')
        if fr_to_dt is not None:
            result['interestFromDate'] = self._find_text(fr_to_dt, 'FrDt')
            result['interestToDate'] = self._find_text(fr_to_dt, 'ToDt')

        return result

    def _parse_entry(self, ntry, prefix: str = '') -> Dict[str, Any]:
        """Parse Ntry (Entry) element.

        Entry contains:
        - NtryRef: Entry reference
        - Amt: Entry amount
        - CdtDbtInd: Credit/Debit indicator
        - Sts: Status
        - BookgDt: Booking date
        - ValDt: Value date
        - AcctSvcrRef: Account servicer reference
        - BkTxCd: Bank transaction code
        - NtryDtls: Entry details with transaction info

        Args:
            ntry: Ntry element
            prefix: Prefix for field names (e.g., 'firstEntry')

        Returns:
            Dict with entry fields
        """
        result = {}
        p = f"{prefix}_" if prefix else ''

        # Basic Entry Fields
        result[f'{p}entryReference'] = self._find_text(ntry, 'NtryRef')

        # Amount
        amt_elem = self._find(ntry, 'Amt')
        if amt_elem is not None:
            result[f'{p}entryAmount'] = self._safe_float(amt_elem.text)
            result[f'{p}entryCurrency'] = amt_elem.get('Ccy')

        result[f'{p}creditDebitIndicator'] = self._find_text(ntry, 'CdtDbtInd')

        # Reversal Indicator
        result[f'{p}reversalIndicator'] = self._find_text(ntry, 'RvslInd') == 'true'

        # Status
        result[f'{p}entryStatus'] = (
            self._find_text(ntry, 'Sts/Cd') or
            self._find_text(ntry, 'Sts')
        )

        # Dates
        result[f'{p}bookingDate'] = (
            self._find_text(ntry, 'BookgDt/Dt') or
            self._find_text(ntry, 'BookgDt/DtTm')
        )
        result[f'{p}valueDate'] = (
            self._find_text(ntry, 'ValDt/Dt') or
            self._find_text(ntry, 'ValDt/DtTm')
        )

        # Account Servicer Reference
        result[f'{p}accountServicerReference'] = self._find_text(ntry, 'AcctSvcrRef')

        # Bank Transaction Code
        bk_tx_cd = self._find(ntry, 'BkTxCd')
        if bk_tx_cd is not None:
            result.update(self._parse_bank_transaction_code(bk_tx_cd, prefix))

        # Entry Details (may contain multiple transactions)
        ntry_dtls = self._find(ntry, 'NtryDtls')
        if ntry_dtls is not None:
            # Batch info
            btch = self._find(ntry_dtls, 'Btch')
            if btch is not None:
                result[f'{p}batchNumberOfTransactions'] = self._safe_int(
                    self._find_text(btch, 'NbOfTxs')
                )
                result[f'{p}batchTotalAmount'] = self._safe_float(
                    self._find_text(btch, 'TtlAmt')
                )
                result[f'{p}batchCreditDebit'] = self._find_text(btch, 'CdtDbtInd')

            # First Transaction Details
            tx_dtls = self._find(ntry_dtls, 'TxDtls')
            if tx_dtls is not None:
                result.update(self._parse_transaction_details(tx_dtls, prefix))

        return result

    def _parse_bank_transaction_code(self, bk_tx_cd, prefix: str = '') -> Dict[str, Any]:
        """Parse BkTxCd (Bank Transaction Code) element.

        Args:
            bk_tx_cd: BkTxCd element
            prefix: Prefix for field names

        Returns:
            Dict with transaction code fields
        """
        result = {}
        p = f"{prefix}_" if prefix else ''

        # Domain
        domn = self._find(bk_tx_cd, 'Domn')
        if domn is not None:
            result[f'{p}domainCode'] = self._find_text(domn, 'Cd')

            fmly = self._find(domn, 'Fmly')
            if fmly is not None:
                result[f'{p}familyCode'] = self._find_text(fmly, 'Cd')
                result[f'{p}subFamilyCode'] = self._find_text(fmly, 'SubFmlyCd')

        # Proprietary
        prtry = self._find(bk_tx_cd, 'Prtry')
        if prtry is not None:
            result[f'{p}proprietaryCode'] = self._find_text(prtry, 'Cd')
            result[f'{p}proprietaryIssuer'] = self._find_text(prtry, 'Issr')

        return result

    def _parse_transaction_details(self, tx_dtls, prefix: str = '') -> Dict[str, Any]:
        """Parse TxDtls (Transaction Details) element.

        Args:
            tx_dtls: TxDtls element
            prefix: Prefix for field names

        Returns:
            Dict with transaction detail fields
        """
        result = {}
        p = f"{prefix}_" if prefix else ''

        # References
        refs = self._find(tx_dtls, 'Refs')
        if refs is not None:
            result[f'{p}messageId'] = self._find_text(refs, 'MsgId')
            result[f'{p}accountServicerReference'] = self._find_text(refs, 'AcctSvcrRef')
            result[f'{p}paymentInfoId'] = self._find_text(refs, 'PmtInfId')
            result[f'{p}instructionId'] = self._find_text(refs, 'InstrId')
            result[f'{p}endToEndId'] = self._find_text(refs, 'EndToEndId')
            result[f'{p}transactionId'] = self._find_text(refs, 'TxId')
            result[f'{p}mandateId'] = self._find_text(refs, 'MndtId')
            result[f'{p}chequeNumber'] = self._find_text(refs, 'ChqNb')
            result[f'{p}clearingSystemReference'] = self._find_text(refs, 'ClrSysRef')
            result[f'{p}uetr'] = self._find_text(refs, 'UETR')

        # Amount Details (if different from entry level)
        amt_dtls = self._find(tx_dtls, 'AmtDtls')
        if amt_dtls is not None:
            instd_amt = self._find(amt_dtls, 'InstdAmt')
            if instd_amt is not None:
                amt = self._find(instd_amt, 'Amt')
                if amt is not None:
                    result[f'{p}instructedAmount'] = self._safe_float(amt.text)
                    result[f'{p}instructedCurrency'] = amt.get('Ccy')

        # Related Parties
        rltd_pties = self._find(tx_dtls, 'RltdPties')
        if rltd_pties is not None:
            # Debtor
            dbtr = self._find(rltd_pties, 'Dbtr/Pty') or self._find(rltd_pties, 'Dbtr')
            if dbtr is not None:
                result.update(self._extract_party(dbtr, f'{p}debtor'))

            dbtr_acct = self._find(rltd_pties, 'DbtrAcct')
            if dbtr_acct is not None:
                result.update(self._extract_account(dbtr_acct, f'{p}debtorAccount'))

            # Creditor
            cdtr = self._find(rltd_pties, 'Cdtr/Pty') or self._find(rltd_pties, 'Cdtr')
            if cdtr is not None:
                result.update(self._extract_party(cdtr, f'{p}creditor'))

            cdtr_acct = self._find(rltd_pties, 'CdtrAcct')
            if cdtr_acct is not None:
                result.update(self._extract_account(cdtr_acct, f'{p}creditorAccount'))

            # Ultimate Debtor
            ultmt_dbtr = self._find(rltd_pties, 'UltmtDbtr')
            if ultmt_dbtr is not None:
                result.update(self._extract_party(ultmt_dbtr, f'{p}ultimateDebtor'))

            # Ultimate Creditor
            ultmt_cdtr = self._find(rltd_pties, 'UltmtCdtr')
            if ultmt_cdtr is not None:
                result.update(self._extract_party(ultmt_cdtr, f'{p}ultimateCreditor'))

        # Related Agents
        rltd_agts = self._find(tx_dtls, 'RltdAgts')
        if rltd_agts is not None:
            dbtr_agt = self._find(rltd_agts, 'DbtrAgt')
            if dbtr_agt is not None:
                result.update(self._extract_financial_institution(dbtr_agt, f'{p}debtorAgent'))

            cdtr_agt = self._find(rltd_agts, 'CdtrAgt')
            if cdtr_agt is not None:
                result.update(self._extract_financial_institution(cdtr_agt, f'{p}creditorAgent'))

        # Local Instrument
        lcl_instrm = self._find(tx_dtls, 'LclInstrm')
        if lcl_instrm is not None:
            result[f'{p}localInstrumentCode'] = self._find_text(lcl_instrm, 'Cd')
            result[f'{p}localInstrumentProprietary'] = self._find_text(lcl_instrm, 'Prtry')

        # Purpose
        purp = self._find(tx_dtls, 'Purp')
        if purp is not None:
            result[f'{p}purposeCode'] = self._find_text(purp, 'Cd')
            result[f'{p}purposeProprietary'] = self._find_text(purp, 'Prtry')

        # Remittance Information
        rmt_inf = self._find(tx_dtls, 'RmtInf')
        if rmt_inf is not None:
            result.update(self._extract_remittance_info(rmt_inf, p))

        # Related Dates
        rltd_dts = self._find(tx_dtls, 'RltdDts')
        if rltd_dts is not None:
            result[f'{p}acceptanceDateTime'] = self._find_text(rltd_dts, 'AccptncDtTm')
            result[f'{p}tradeActivityDate'] = self._find_text(rltd_dts, 'TradActvtyDt')
            result[f'{p}tradeDate'] = self._find_text(rltd_dts, 'TradDt')

        # Additional Transaction Info
        result[f'{p}additionalTransactionInfo'] = self._find_text(tx_dtls, 'AddtlTxInf')

        return result

    def _extract_remittance_info(self, rmt_inf, prefix: str = '') -> Dict[str, Any]:
        """Extract remittance information with prefix support.

        Overrides base class to support statement-specific prefixing.

        Args:
            rmt_inf: RmtInf element
            prefix: Field name prefix

        Returns:
            Dict with remittance fields
        """
        result = {}
        p = prefix if prefix.endswith('_') else f'{prefix}_' if prefix else ''

        # Unstructured
        ustrd_list = []
        for ustrd in self._find_all(rmt_inf, 'Ustrd'):
            if ustrd.text:
                ustrd_list.append(ustrd.text)
        if ustrd_list:
            result[f'{p}remittanceUnstructured'] = ustrd_list if len(ustrd_list) > 1 else ustrd_list[0]

        # Structured
        strd = self._find(rmt_inf, 'Strd')
        if strd is not None:
            # Referred Document Information
            rfrd_doc_inf = self._find(strd, 'RfrdDocInf')
            if rfrd_doc_inf is not None:
                result[f'{p}referredDocType'] = (
                    self._find_text(rfrd_doc_inf, 'Tp/CdOrPrtry/Cd') or
                    self._find_text(rfrd_doc_inf, 'Tp/CdOrPrtry/Prtry')
                )
                result[f'{p}referredDocNumber'] = self._find_text(rfrd_doc_inf, 'Nb')
                result[f'{p}referredDocDate'] = (
                    self._find_text(rfrd_doc_inf, 'RltdDt') or
                    self._find_text(rfrd_doc_inf, 'RltdDt/Dt')
                )

            # Creditor Reference
            cdtr_ref_inf = self._find(strd, 'CdtrRefInf')
            if cdtr_ref_inf is not None:
                result[f'{p}creditorReference'] = self._find_text(cdtr_ref_inf, 'Ref')
                result[f'{p}creditorReferenceType'] = (
                    self._find_text(cdtr_ref_inf, 'Tp/CdOrPrtry/Cd') or
                    self._find_text(cdtr_ref_inf, 'Tp/CdOrPrtry/Prtry')
                )

        return result

    def _extract_entry_summary(self, ntry) -> Dict[str, Any]:
        """Extract minimal summary of an entry for the entries list.

        Args:
            ntry: Ntry element

        Returns:
            Dict with entry summary
        """
        result = {
            'reference': self._find_text(ntry, 'NtryRef'),
            'creditDebit': self._find_text(ntry, 'CdtDbtInd'),
            'status': self._find_text(ntry, 'Sts/Cd') or self._find_text(ntry, 'Sts'),
            'bookingDate': (
                self._find_text(ntry, 'BookgDt/Dt') or
                self._find_text(ntry, 'BookgDt/DtTm')
            ),
            'valueDate': (
                self._find_text(ntry, 'ValDt/Dt') or
                self._find_text(ntry, 'ValDt/DtTm')
            ),
        }

        amt_elem = self._find(ntry, 'Amt')
        if amt_elem is not None:
            result['amount'] = self._safe_float(amt_elem.text)
            result['currency'] = amt_elem.get('Ccy')

        return result


class Camt053Extractor(BaseISO20022Extractor):
    """Base extractor for camt.053 Bank to Customer Account Statement.

    Note: camt.053 is a statement format, not a payment instruction.
    The Gold entity mapping is different:
    - Account Owner -> cdm_party (ACCOUNT_OWNER)
    - Statement Account -> cdm_account (STATEMENT_ACCOUNT)
    - Account Servicer -> cdm_financial_institution (ACCOUNT_SERVICER)
    - Statement entries -> cdm_account_statement (statement record)
    """

    MESSAGE_TYPE: str = "camt.053"
    SILVER_TABLE: str = "stg_camt053"
    PARSER_CLASS = Camt053Parser
    DEFAULT_CURRENCY: str = "XXX"
    CLEARING_SYSTEM: str = None

    def extract_silver(
        self,
        msg_content: Dict[str, Any],
        raw_id: str,
        stg_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        """Extract Silver layer record from parsed camt.053 message.

        Args:
            msg_content: Parsed message content
            raw_id: Reference to Bronze record
            stg_id: Silver staging record ID
            batch_id: Processing batch identifier

        Returns:
            Dict with all fields for Silver staging table
        """
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type and Header
            'message_type': 'camt.053',
            'msg_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),

            # Statement Identification
            'statement_id': trunc(msg_content.get('statementId'), 35),
            'sequence_number': msg_content.get('electronicSequenceNumber'),
            'legal_sequence_number': msg_content.get('legalSequenceNumber'),
            'statement_creation_date_time': msg_content.get('statementCreationDateTime'),
            'copy_duplicate_indicator': msg_content.get('copyDuplicateIndicator'),

            # Period
            'from_date': msg_content.get('fromDateTime'),
            'to_date': msg_content.get('toDateTime'),

            # Account Information
            'account_iban': trunc(msg_content.get('accountIban'), 34),
            'account_number': trunc(msg_content.get('accountNumber'), 34),
            'account_scheme': trunc(msg_content.get('accountScheme'), 35),
            'account_currency': msg_content.get('accountCurrency') or self.DEFAULT_CURRENCY,
            'account_name': trunc(msg_content.get('accountName'), 140),
            'account_type': trunc(msg_content.get('accountTypeCode'), 10),

            # Account Owner
            'account_owner_name': trunc(msg_content.get('accountOwnerName'), 140),
            'account_owner_street': trunc(msg_content.get('accountOwnerStreetName'), 70),
            'account_owner_building_number': trunc(msg_content.get('accountOwnerBuildingNumber'), 16),
            'account_owner_post_code': trunc(msg_content.get('accountOwnerPostCode'), 16),
            'account_owner_town': trunc(msg_content.get('accountOwnerTownName'), 35),
            'account_owner_country': trunc(msg_content.get('accountOwnerCountry'), 2),
            'account_owner_id': trunc(
                msg_content.get('accountOwnerOtherId') or msg_content.get('accountOwnerLei'),
                35
            ),

            # Account Servicer
            'account_servicer_bic': trunc(msg_content.get('accountServicerBic'), 11),
            'account_servicer_lei': trunc(msg_content.get('accountServicerLei'), 20),
            'account_servicer_name': trunc(msg_content.get('accountServicerName'), 140),
            'account_servicer_member_id': trunc(msg_content.get('accountServicerMemberId'), 35),
            'account_servicer_country': trunc(msg_content.get('accountServicerCountry'), 2),

            # Opening Balance (Booked)
            'opening_balance_amount': msg_content.get('openingBookedAmount'),
            'opening_balance_currency': msg_content.get('openingBookedCurrency'),
            'opening_balance_credit_debit': msg_content.get('openingBookedCreditDebit'),
            'opening_balance_date': msg_content.get('openingBookedDate'),

            # Closing Balance (Booked)
            'closing_balance_amount': msg_content.get('closingBookedAmount'),
            'closing_balance_currency': msg_content.get('closingBookedCurrency'),
            'closing_balance_credit_debit': msg_content.get('closingBookedCreditDebit'),
            'closing_balance_date': msg_content.get('closingBookedDate'),

            # Available Balances
            'opening_available_amount': msg_content.get('openingAvailableAmount'),
            'opening_available_currency': msg_content.get('openingAvailableCurrency'),
            'closing_available_amount': msg_content.get('closingAvailableAmount'),
            'closing_available_currency': msg_content.get('closingAvailableCurrency'),

            # Generic balance reference (first balance)
            'balance_type': trunc(msg_content.get('balanceType'), 10),
            'balance_amount': msg_content.get('balanceAmount'),
            'balance_currency': msg_content.get('balanceCurrency'),

            # Transaction Summary
            'number_of_entries': msg_content.get('summaryNumberOfEntries') or msg_content.get('totalEntries'),
            'sum_of_entries': msg_content.get('summarySum'),
            'number_of_credit_entries': msg_content.get('summaryCreditEntries'),
            'sum_of_credit_entries': msg_content.get('summaryCreditSum'),
            'number_of_debit_entries': msg_content.get('summaryDebitEntries'),
            'sum_of_debit_entries': msg_content.get('summaryDebitSum'),

            # First Entry Fields (for reference/indexing)
            'entries_reference': trunc(msg_content.get('firstEntry_entryReference'), 35),
            'entries_amount': msg_content.get('firstEntry_entryAmount'),
            'entries_currency': msg_content.get('firstEntry_entryCurrency'),
            'entries_credit_debit_indicator': msg_content.get('firstEntry_creditDebitIndicator'),
            'entries_status': trunc(msg_content.get('firstEntry_entryStatus'), 10),
            'entries_booking_date': msg_content.get('firstEntry_bookingDate'),
            'entries_value_date': msg_content.get('firstEntry_valueDate'),
            'entries_account_servicer_ref': trunc(msg_content.get('firstEntry_accountServicerReference'), 35),

            # First Entry Bank Transaction Code
            'entries_domain_code': trunc(msg_content.get('firstEntry_domainCode'), 10),
            'entries_family_code': trunc(msg_content.get('firstEntry_familyCode'), 10),
            'entries_sub_family_code': trunc(msg_content.get('firstEntry_subFamilyCode'), 10),
            'entries_proprietary_code': trunc(msg_content.get('firstEntry_proprietaryCode'), 35),

            # First Entry Transaction Details (if available)
            'entries_end_to_end_id': trunc(msg_content.get('firstEntry_endToEndId'), 35),
            'entries_transaction_id': trunc(msg_content.get('firstEntry_transactionId'), 35),
            'entries_uetr': msg_content.get('firstEntry_uetr'),
            'entries_debtor_name': trunc(msg_content.get('firstEntry_debtorName'), 140),
            'entries_creditor_name': trunc(msg_content.get('firstEntry_creditorName'), 140),
            'entries_remittance_unstructured': msg_content.get('firstEntry_remittanceUnstructured'),

            # Processing status
            'processing_status': 'PENDING',

            # Backward compatibility columns
            'account_id_iban': trunc(msg_content.get('accountIban'), 34),
            'account_owner': trunc(msg_content.get('accountOwnerName'), 140),
            'servicer_bic': trunc(msg_content.get('accountServicerBic'), 11),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT.

        Returns:
            List of column names in INSERT order
        """
        return [
            # Core identifiers
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'msg_id', 'creation_date_time',

            # Statement identification
            'statement_id', 'sequence_number', 'legal_sequence_number',
            'statement_creation_date_time', 'copy_duplicate_indicator',

            # Period
            'from_date', 'to_date',

            # Account
            'account_iban', 'account_number', 'account_scheme',
            'account_currency', 'account_name', 'account_type',

            # Account Owner
            'account_owner_name', 'account_owner_street',
            'account_owner_building_number', 'account_owner_post_code',
            'account_owner_town', 'account_owner_country', 'account_owner_id',

            # Account Servicer
            'account_servicer_bic', 'account_servicer_lei', 'account_servicer_name',
            'account_servicer_member_id', 'account_servicer_country',

            # Opening Balance
            'opening_balance_amount', 'opening_balance_currency',
            'opening_balance_credit_debit', 'opening_balance_date',

            # Closing Balance
            'closing_balance_amount', 'closing_balance_currency',
            'closing_balance_credit_debit', 'closing_balance_date',

            # Available Balances
            'opening_available_amount', 'opening_available_currency',
            'closing_available_amount', 'closing_available_currency',

            # Generic balance reference
            'balance_type', 'balance_amount', 'balance_currency',

            # Transaction Summary
            'number_of_entries', 'sum_of_entries',
            'number_of_credit_entries', 'sum_of_credit_entries',
            'number_of_debit_entries', 'sum_of_debit_entries',

            # First Entry
            'entries_reference', 'entries_amount', 'entries_currency',
            'entries_credit_debit_indicator', 'entries_status',
            'entries_booking_date', 'entries_value_date',
            'entries_account_servicer_ref',

            # First Entry Bank Transaction Code
            'entries_domain_code', 'entries_family_code',
            'entries_sub_family_code', 'entries_proprietary_code',

            # First Entry Transaction Details
            'entries_end_to_end_id', 'entries_transaction_id', 'entries_uetr',
            'entries_debtor_name', 'entries_creditor_name',
            'entries_remittance_unstructured',

            # Processing
            'processing_status',

            # Backward compatibility
            'account_id_iban', 'account_owner', 'servicer_bic',
        ]

    def _extract_parties(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract party entities from camt.053 Silver record.

        camt.053 has different party roles than payment messages:
        - Account Owner (party who owns the statement account)
        - Debtor/Creditor (from transaction entries)

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import PartyData

        # Account Owner (primary party in camt.053)
        account_owner_name = (
            silver_data.get('account_owner_name') or
            silver_data.get('account_owner')
        )
        if account_owner_name:
            entities.parties.append(PartyData(
                name=account_owner_name,
                role="ACCOUNT_OWNER",
                party_type='UNKNOWN',
                country=silver_data.get('account_owner_country'),
                identification_number=silver_data.get('account_owner_id'),
                street_name=silver_data.get('account_owner_street'),
                building_number=silver_data.get('account_owner_building_number'),
                post_code=silver_data.get('account_owner_post_code'),
                town_name=silver_data.get('account_owner_town'),
            ))

        # Debtor from first entry (if present)
        if silver_data.get('entries_debtor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('entries_debtor_name'),
                role="DEBTOR",
                party_type='UNKNOWN',
            ))

        # Creditor from first entry (if present)
        if silver_data.get('entries_creditor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('entries_creditor_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
            ))

    def _extract_accounts(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract account entities from camt.053 Silver record.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import AccountData

        # Statement Account (the account the statement is for)
        account_iban = (
            silver_data.get('account_iban') or
            silver_data.get('account_id_iban')
        )
        account_number = silver_data.get('account_number')

        if account_iban or account_number:
            entities.accounts.append(AccountData(
                account_number=account_number or account_iban,
                role="STATEMENT_ACCOUNT",
                iban=account_iban,
                account_type=silver_data.get('account_type') or 'CACC',
                currency=silver_data.get('account_currency') or self.DEFAULT_CURRENCY,
                name=silver_data.get('account_name'),
            ))

    def _extract_financial_institutions(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract financial institution entities from camt.053 Silver record.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import FinancialInstitutionData

        # Account Servicer (the bank providing the statement)
        servicer_bic = (
            silver_data.get('account_servicer_bic') or
            silver_data.get('servicer_bic')
        )
        if servicer_bic:
            # Extract country from BIC positions 5-6
            country = servicer_bic[4:6] if len(servicer_bic) >= 6 else 'XX'

            entities.financial_institutions.append(FinancialInstitutionData(
                role="ACCOUNT_SERVICER",
                bic=servicer_bic,
                lei=silver_data.get('account_servicer_lei'),
                name=silver_data.get('account_servicer_name'),
                member_id=silver_data.get('account_servicer_member_id'),
                country=silver_data.get('account_servicer_country') or country,
            ))
