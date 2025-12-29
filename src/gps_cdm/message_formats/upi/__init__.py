"""UPI (India Unified Payments Interface) Extractor - XML and JSON based."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
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


class UpiXmlParser:
    """Parser for UPI XML format messages (NPCI specification)."""

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse UPI XML message into structured dict."""
        result = {
            'messageType': 'UPI',
        }

        # Handle JSON input (pre-parsed)
        if isinstance(raw_content, dict):
            return raw_content

        if raw_content.strip().startswith('{'):
            try:
                parsed = json.loads(raw_content)
                if isinstance(parsed, dict) and 'messageType' not in parsed:
                    parsed['messageType'] = 'UPI'
                return parsed
            except json.JSONDecodeError:
                pass

        # Parse UPI XML format using regex
        content = raw_content

        # Remove namespaces for easier parsing
        content = re.sub(r'xmlns[^"]*"[^"]*"', '', content)
        content = re.sub(r'<([a-zA-Z]+):', r'<', content)
        content = re.sub(r'</([a-zA-Z]+):', r'</', content)

        # Head attributes
        head_match = re.search(r'<Head[^>]*msgId="([^"]*)"', content)
        if head_match:
            result['transactionId'] = head_match.group(1)

        head_ts_match = re.search(r'<Head[^>]*ts="([^"]*)"', content)
        if head_ts_match:
            result['creationDateTime'] = head_ts_match.group(1)

        # Transaction info
        txn_match = re.search(r'<Txn[^>]*id="([^"]*)"', content)
        if txn_match:
            result['transactionRefId'] = txn_match.group(1)

        txn_note_match = re.search(r'<Txn[^>]*note="([^"]*)"', content)
        if txn_note_match:
            result['remittanceInfo'] = txn_note_match.group(1)

        txn_type_match = re.search(r'<Txn[^>]*type="([^"]*)"', content)
        if txn_type_match:
            result['transactionType'] = txn_type_match.group(1)

        # Payer info
        payer_match = re.search(r'<Payer[^>]*>', content)
        if payer_match:
            payer_block = payer_match.group(0)
            addr_match = re.search(r'addr="([^"]*)"', payer_block)
            if addr_match:
                result['payerVpa'] = addr_match.group(1)
            name_match = re.search(r'name="([^"]*)"', payer_block)
            if name_match:
                result['payerName'] = name_match.group(1)

        # Payer Account details
        payer_acct_match = re.search(r'<Payer[^>]*>.*?<Ac[^>]*>(.*?)</Ac>', content, re.DOTALL)
        if payer_acct_match:
            acct_block = payer_acct_match.group(1)
            ifsc_match = re.search(r'name="IFSC"[^>]*value="([^"]*)"', acct_block)
            if ifsc_match:
                result['payerIfsc'] = ifsc_match.group(1)
            acnum_match = re.search(r'name="ACNUM"[^>]*value="([^"]*)"', acct_block)
            if acnum_match:
                result['payerAccount'] = acnum_match.group(1)

        # Payer Amount (within Payer block)
        payer_amount_match = re.search(r'<Payer[^>]*>.*?<Amount[^>]*curr="([^"]*)"[^>]*value="([^"]*)"', content, re.DOTALL)
        if payer_amount_match:
            result['currency'] = payer_amount_match.group(1)
            try:
                result['amount'] = float(payer_amount_match.group(2))
            except ValueError:
                result['amount'] = None

        # Payee info
        payee_match = re.search(r'<Payee[^>]*>', content)
        if payee_match:
            payee_block = payee_match.group(0)
            addr_match = re.search(r'addr="([^"]*)"', payee_block)
            if addr_match:
                result['payeeVpa'] = addr_match.group(1)
            name_match = re.search(r'name="([^"]*)"', payee_block)
            if name_match:
                result['payeeName'] = name_match.group(1)

        # Payee Account details
        payee_acct_match = re.search(r'<Payee[^>]*>.*?<Ac[^>]*>(.*?)</Ac>', content, re.DOTALL)
        if payee_acct_match:
            acct_block = payee_acct_match.group(1)
            ifsc_match = re.search(r'name="IFSC"[^>]*value="([^"]*)"', acct_block)
            if ifsc_match:
                result['payeeIfsc'] = ifsc_match.group(1)
            acnum_match = re.search(r'name="ACNUM"[^>]*value="([^"]*)"', acct_block)
            if acnum_match:
                result['payeeAccount'] = acnum_match.group(1)

        # Mobile from Device tags
        mobile_match = re.search(r'name="MOBILE"[^>]*value="([^"]*)"', content)
        if mobile_match:
            result['payerMobile'] = mobile_match.group(1)

        return result


class UpiExtractor(BaseExtractor):
    """Extractor for India UPI instant payment messages."""

    MESSAGE_TYPE = "UPI"
    SILVER_TABLE = "stg_upi"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw UPI content."""
        msg_id = raw_content.get('transactionId', '') or raw_content.get('transactionRefId', '')
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
        """Extract all Silver layer fields from UPI message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'UPI',
            'transaction_id': trunc(msg_content.get('transactionId'), 35),
            'transaction_ref_id': trunc(msg_content.get('transactionRefId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'INR',

            # Payer (Debtor)
            'payer_vpa': trunc(msg_content.get('payerVpa'), 256),
            'payer_name': trunc(msg_content.get('payerName'), 140),
            'payer_account': trunc(msg_content.get('payerAccount'), 34),
            'payer_ifsc': trunc(msg_content.get('payerIfsc'), 11),
            'payer_mobile': trunc(msg_content.get('payerMobile'), 15),

            # Payee (Creditor)
            'payee_vpa': trunc(msg_content.get('payeeVpa'), 256),
            'payee_name': trunc(msg_content.get('payeeName'), 140),
            'payee_account': trunc(msg_content.get('payeeAccount'), 34),
            'payee_ifsc': trunc(msg_content.get('payeeIfsc'), 11),
            'payee_mobile': trunc(msg_content.get('payeeMobile'), 15),

            # Transaction Details
            'transaction_type': trunc(msg_content.get('transactionType'), 10),
            'sub_type': trunc(msg_content.get('subType'), 10),
            'remittance_info': msg_content.get('remittanceInfo'),
            'transaction_status': trunc(msg_content.get('transactionStatus'), 20),
            'response_code': trunc(msg_content.get('responseCode'), 10),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'transaction_id', 'transaction_ref_id',
            'creation_date_time', 'amount', 'currency',
            'payer_vpa', 'payer_name', 'payer_account',
            'payer_ifsc', 'payer_mobile',
            'payee_vpa', 'payee_name', 'payee_account',
            'payee_ifsc', 'payee_mobile',
            'transaction_type', 'sub_type', 'remittance_info',
            'transaction_status', 'response_code',
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
        """Extract Gold layer entities from UPI Silver record.

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
                country='IN',
            ))

        # Payee Party (Creditor)
        if silver_data.get('payee_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='IN',
            ))

        # Payer Account (VPA or Account)
        if silver_data.get('payer_vpa') or silver_data.get('payer_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payer_vpa') or silver_data.get('payer_account'),
                role="DEBTOR",
                account_type='CACC',
                currency='INR',
            ))

        # Payee Account (VPA or Account)
        if silver_data.get('payee_vpa') or silver_data.get('payee_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payee_vpa') or silver_data.get('payee_account'),
                role="CREDITOR",
                account_type='CACC',
                currency='INR',
            ))

        # Payer Bank (by IFSC)
        if silver_data.get('payer_ifsc'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=silver_data.get('payer_ifsc'),
                clearing_system='INIFSC',  # India IFSC
                country='IN',
            ))

        # Payee Bank (by IFSC)
        if silver_data.get('payee_ifsc'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=silver_data.get('payee_ifsc'),
                clearing_system='INIFSC',
                country='IN',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('UPI', UpiExtractor())
ExtractorRegistry.register('upi', UpiExtractor())
