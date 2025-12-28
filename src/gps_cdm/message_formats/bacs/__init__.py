"""BACS (UK Bankers' Automated Clearing Services) Extractor."""

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


class BacsFixedWidthParser:
    """Parser for BACS Standard 18 fixed-width format messages.

    BACS file format structure:
    - VOL1: Volume header label
    - HDR1/HDR2: File header labels
    - UHL1: User header label (contains service user number, processing date)
    - Data records: Transaction records (fixed 100 chars each)
    - EOF1/EOF2: End of file labels
    - UTL1: User trailer label (contains totals)
    """

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse BACS message into structured dict."""
        result = {
            'messageType': 'BACS',
            'transactions': [],
        }

        # Handle JSON input (pre-parsed)
        if isinstance(raw_content, dict):
            return raw_content

        if raw_content.strip().startswith('{'):
            try:
                parsed = json.loads(raw_content)
                if isinstance(parsed, dict) and 'messageType' not in parsed:
                    parsed['messageType'] = 'BACS'
                return parsed
            except json.JSONDecodeError:
                pass

        lines = raw_content.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # User Header Label (UHL1)
            if line.startswith('UHL1'):
                self._parse_uhl1(line, result)

            # Data record (starts with numeric transaction type code, min 78 chars per Standard 18)
            elif line[0:2].isdigit() and len(line) >= 78:
                tx = self._parse_data_record(line)
                if tx:
                    result['transactions'].append(tx)
                    # Use first transaction for main record fields
                    if len(result['transactions']) == 1:
                        result.update(tx)

            # User Trailer Label (UTL1) - contains totals
            elif line.startswith('UTL1'):
                self._parse_utl1(line, result)

        return result

    def _parse_uhl1(self, line: str, result: Dict):
        """Parse User Header Label (UHL1).

        Format: UHL1 DDDDDD SUNNNNN SSSSS....
        Positions:
        - 1-4: Record type (UHL1)
        - 6-11: Processing date (YYMMDD)
        - 12-17: Service user number (6 digits)
        - 18+: Service user name
        """
        if len(line) >= 11:
            result['processingDate'] = self._parse_date(line[5:11].strip())

        if len(line) >= 17:
            result['serviceUserNumber'] = line[11:17].strip()

        if len(line) >= 40:
            result['serviceUserName'] = line[17:].strip()[:18]

    def _parse_data_record(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse BACS data (transaction) record.

        Standard 18 format (positions are 1-indexed as per spec):
        - Positions 1-2: Transaction type code (2 chars)
        - Positions 3-8: Destination sort code (6 chars)
        - Positions 9-16: Destination account number (8 chars)
        - Position 17: Free format indicator (1 char)
        - Positions 18-28: Amount in pence (11 digits)
        - Positions 29-46: Beneficiary name (18 chars)
        - Positions 47-64: Reference (18 chars)
        - Positions 65-70: Originating sort code (6 chars)
        - Positions 71-78: Originating account number (8 chars)
        - Positions 79-96: Free format or user name (18 chars)
        """
        try:
            tx = {}

            # Transaction type (positions 1-2, 0-indexed: 0-1)
            tx['transactionType'] = line[0:2].strip()

            # Destination sort code (positions 3-8, 0-indexed: 2-7)
            tx['destinationSortCode'] = line[2:8].strip()

            # Destination account (positions 9-16, 0-indexed: 8-15)
            tx['destinationAccount'] = line[8:16].strip()

            # Free format indicator at position 17 (0-indexed: 16)
            # Amount in pence (positions 18-28, 0-indexed: 17-27)
            if len(line) >= 28:
                amount_str = line[17:28].strip()
                if amount_str:
                    try:
                        # Convert from pence to pounds
                        tx['amount'] = float(amount_str) / 100.0
                    except ValueError:
                        tx['amount'] = None

            # Beneficiary name (positions 29-46, 0-indexed: 28-45)
            if len(line) >= 46:
                tx['beneficiaryName'] = line[28:46].strip()

            # Reference (positions 47-64, 0-indexed: 46-63)
            if len(line) >= 64:
                tx['reference'] = line[46:64].strip()

            # Originating sort code (positions 65-70, 0-indexed: 64-69)
            if len(line) >= 70:
                tx['originatingSortCode'] = line[64:70].strip()

            # Originating account (positions 71-78, 0-indexed: 70-77)
            if len(line) >= 78:
                tx['originatingAccount'] = line[70:78].strip()

            return tx

        except Exception as e:
            logger.warning(f"Failed to parse BACS data record: {e}")
            return None

    def _parse_utl1(self, line: str, result: Dict):
        """Parse User Trailer Label (UTL1) - contains totals."""
        # UTL1 contains control totals - useful for validation
        # Format varies but typically has record counts and amount totals
        result['trailerInfo'] = line[4:].strip()

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse BACS date format (YYMMDD or DDDDDD sequence number)."""
        if not date_str or len(date_str) < 6:
            return None
        try:
            year = int(date_str[:2])
            month = int(date_str[2:4])
            day = int(date_str[4:6])
            # Validate it's a date (not a sequence number)
            if 1 <= month <= 12 and 1 <= day <= 31:
                full_year = 2000 + year if year < 50 else 1900 + year
                return f"{full_year}-{month:02d}-{day:02d}"
        except ValueError:
            pass
        return None


class BacsExtractor(BaseExtractor):
    """Extractor for UK BACS payment messages."""

    MESSAGE_TYPE = "BACS"
    SILVER_TABLE = "stg_bacs"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw BACS content."""
        msg_id = raw_content.get('reference', '') or raw_content.get('serviceUserNumber', '')
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
        """Extract all Silver layer fields from BACS message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'BACS',

            # Service User
            'service_user_number': trunc(msg_content.get('serviceUserNumber'), 6),
            'service_user_name': trunc(msg_content.get('serviceUserName'), 18),

            # Processing Date
            'processing_date': msg_content.get('processingDate'),
            'transaction_type': trunc(msg_content.get('transactionType'), 2),

            # Originator
            'originating_sort_code': trunc(msg_content.get('originatingSortCode'), 6),
            'originating_account': trunc(msg_content.get('originatingAccount'), 8),

            # Destination
            'destination_sort_code': trunc(msg_content.get('destinationSortCode'), 6),
            'destination_account': trunc(msg_content.get('destinationAccount'), 8),

            # Amount & Reference
            'amount': msg_content.get('amount'),
            'reference': trunc(msg_content.get('reference'), 18),
            'beneficiary_name': trunc(msg_content.get('beneficiaryName'), 18),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type',
            'service_user_number', 'service_user_name',
            'processing_date', 'transaction_type',
            'originating_sort_code', 'originating_account',
            'destination_sort_code', 'destination_account',
            'amount', 'reference', 'beneficiary_name',
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
        msg_content: Dict[str, Any],
        stg_id: str,
        batch_id: str
    ) -> GoldEntities:
        """Extract Gold layer entities from BACS message."""
        entities = GoldEntities()

        # Service User Party (Originator/Debtor)
        if msg_content.get('serviceUserName'):
            entities.parties.append(PartyData(
                name=msg_content.get('serviceUserName'),
                role="DEBTOR",
                party_type='ORGANIZATION',
                identification_number=msg_content.get('serviceUserNumber'),
                country='GB',
            ))

        # Beneficiary Party (Creditor)
        if msg_content.get('beneficiaryName'):
            entities.parties.append(PartyData(
                name=msg_content.get('beneficiaryName'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='GB',
            ))

        # Originating Account
        if msg_content.get('originatingAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('originatingAccount'),
                role="DEBTOR",
                account_type='CACC',
                currency='GBP',
            ))

        # Destination Account
        if msg_content.get('destinationAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('destinationAccount'),
                role="CREDITOR",
                account_type='CACC',
                currency='GBP',
            ))

        # Originating Bank (by Sort Code)
        if msg_content.get('originatingSortCode'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=msg_content.get('originatingSortCode'),
                clearing_system='GBDSC',
                country='GB',
            ))

        # Destination Bank (by Sort Code)
        if msg_content.get('destinationSortCode'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=msg_content.get('destinationSortCode'),
                clearing_system='GBDSC',
                country='GB',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('BACS', BacsExtractor())
ExtractorRegistry.register('bacs', BacsExtractor())
