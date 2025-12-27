"""Fedwire (US RTGS) Extractor."""

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


class FedwireTagValueParser:
    """Parser for Fedwire tag-value format messages."""

    # Fedwire tag definitions
    TAG_DEFS = {
        '1500': 'typeCode',
        '1510': 'subtypeCode',
        '1520': 'imad',
        '2000': 'amount',
        '3100': 'senderFi',
        '3320': 'senderReference',
        '3400': 'businessFunctionCode',
        '3600': 'localInstrumentCode',
        '4000': 'originator',
        '4100': 'receiverFiRoutingNumber',
        '4200': 'receiverFiName',
        '5000': 'beneficiary',
        '5100': 'beneficiaryBankRoutingNumber',
        '5200': 'beneficiaryBankName',
        '6000': 'originatorToBeneficiaryInfo',
        '6100': 'omad',
        '6210': 'beneficiaryReference',
        '6300': 'instructingBankInfo',
        '6400': 'fiToFiInfo',
    }

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse Fedwire tag-value message into structured dict."""
        result = {}
        lines = raw_content.strip().split('\n')
        current_tag = None
        current_value = []

        for line in lines:
            line = line.rstrip()

            # Check for tag at start of line: {NNNN}
            tag_match = re.match(r'^\{(\d{4})\}(.*)$', line)
            if tag_match:
                # Save previous tag value
                if current_tag:
                    self._set_field(result, current_tag, '\n'.join(current_value))
                # Start new tag
                current_tag = tag_match.group(1)
                current_value = [tag_match.group(2)] if tag_match.group(2) else []
            elif current_tag:
                # Continuation line
                current_value.append(line)

        # Save last tag
        if current_tag:
            self._set_field(result, current_tag, '\n'.join(current_value))

        return result

    def _set_field(self, result: Dict[str, Any], tag: str, value: str) -> None:
        """Set field value based on Fedwire tag."""
        value = value.strip()

        if tag == '1500':
            result['typeCode'] = value
        elif tag == '1510':
            result['subtypeCode'] = value
        elif tag == '1520':
            result['imad'] = value
            # Parse IMAD: YYYYMMDDSSSSSSSSNNNNNN
            if len(value) >= 8:
                result['inputCycleDate'] = f"{value[:4]}-{value[4:6]}-{value[6:8]}"
            if len(value) >= 16:
                result['inputSource'] = value[8:16]
            if len(value) >= 22:
                result['inputSequenceNumber'] = value[16:22]
        elif tag == '2000':
            # Amount: 12 digits with implied 2 decimals
            clean = value.replace(',', '').replace('.', '').lstrip('0')
            if clean:
                result['amount'] = float(clean) / 100
            else:
                result['amount'] = 0.0
            result['currency'] = 'USD'  # Fedwire is always USD
        elif tag == '3100':
            # Sender FI: RoutingNumber + Name
            self._parse_fi(result, 'sender', value)
        elif tag == '3320':
            result['senderReference'] = value
        elif tag == '3400':
            result['businessFunctionCode'] = value
        elif tag == '3600':
            result['localInstrumentCode'] = value
        elif tag == '4000':
            # Originator (multi-line)
            self._parse_party(result, 'originator', value)
        elif tag == '4100':
            # Receiver FI Routing Number
            if 'receiver' not in result:
                result['receiver'] = {}
            result['receiver']['routingNumber'] = value[:9] if len(value) >= 9 else value
        elif tag == '4200':
            # Receiver FI Name
            if 'receiver' not in result:
                result['receiver'] = {}
            result['receiver']['name'] = value
        elif tag == '5000':
            # Beneficiary (multi-line)
            self._parse_party(result, 'beneficiary', value)
        elif tag == '5100':
            # Beneficiary Bank Routing Number
            if 'beneficiaryBank' not in result:
                result['beneficiaryBank'] = {}
            result['beneficiaryBank']['routingNumber'] = value[:9] if len(value) >= 9 else value
        elif tag == '5200':
            # Beneficiary Bank Name
            if 'beneficiaryBank' not in result:
                result['beneficiaryBank'] = {}
            result['beneficiaryBank']['name'] = value
        elif tag == '6000':
            result['originatorToBeneficiaryInfo'] = value.replace('\n', ' ')
        elif tag == '6100':
            result['omad'] = value
        elif tag == '6210':
            result['beneficiaryReference'] = value
        elif tag == '6300':
            # Instructing bank charges: CCCAMOUNT format
            if len(value) >= 4:
                result['chargesCurrency'] = value[:3]
                result['chargesAmount'] = self._parse_amount(value[3:])
            result['chargeDetails'] = value
        elif tag == '6400':
            result['fiToFiInfo'] = value.replace('\n', ' ')

    def _parse_fi(self, result: Dict[str, Any], prefix: str, value: str) -> None:
        """Parse financial institution field."""
        if prefix not in result:
            result[prefix] = {}

        lines = value.split('\n')
        first_line = lines[0] if lines else ''

        # First 9 chars are routing number
        if len(first_line) >= 9:
            result[prefix]['routingNumber'] = first_line[:9]
            result[prefix]['name'] = first_line[9:].strip()
        else:
            result[prefix]['name'] = first_line

    def _parse_party(self, result: Dict[str, Any], prefix: str, value: str) -> None:
        """Parse party (originator/beneficiary) field."""
        if prefix not in result:
            result[prefix] = {'address': {}}

        lines = value.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            if i == 0:
                # First line: may have identifier prefix like D/ or I/
                if line.startswith('D/') or line.startswith('I/'):
                    result[prefix]['identifierType'] = line[0]  # D or I
                    result[prefix]['identifier'] = line[2:]  # Rest is account
                else:
                    result[prefix]['name'] = line
            elif i == 1 and result[prefix].get('identifier'):
                result[prefix]['name'] = line
            elif 'name' not in result[prefix]:
                result[prefix]['name'] = line
            else:
                # Address lines
                addr = result[prefix]['address']
                if 'line1' not in addr:
                    addr['line1'] = line
                elif 'city' not in addr:
                    # Parse "CITY STATE ZIP" format
                    parts = line.rsplit(' ', 2)
                    if len(parts) >= 2:
                        addr['city'] = parts[0]
                        addr['state'] = parts[1] if len(parts) > 1 else None
                        addr['zipCode'] = parts[2] if len(parts) > 2 else None
                    else:
                        addr['city'] = line
                elif 'country' not in addr:
                    addr['country'] = line[:2] if len(line) >= 2 else line

    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount with comma as decimal separator."""
        if not amount_str:
            return 0.0
        clean = amount_str.replace(',', '.').replace(' ', '')
        try:
            return float(clean)
        except ValueError:
            return 0.0


class FedwireExtractor(BaseExtractor):
    """Extractor for Fedwire messages."""

    MESSAGE_TYPE = "FEDWIRE"
    SILVER_TABLE = "stg_fedwire"

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

        # Extract nested objects
        sender = msg_content.get('sender', {})
        sender_addr = sender.get('address', {}) if sender else {}
        receiver = msg_content.get('receiver', {})
        receiver_addr = receiver.get('address', {}) if receiver else {}
        originator = msg_content.get('originator', {})
        originator_addr = originator.get('address', {}) if originator else {}
        beneficiary = msg_content.get('beneficiary', {})
        beneficiary_addr = beneficiary.get('address', {}) if beneficiary else {}
        beneficiary_bank = msg_content.get('beneficiaryBank', {})
        instructing_bank = msg_content.get('instructingBank', {})
        intermediary_bank = msg_content.get('intermediaryBank', {})

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Header (matching actual DB schema)
            'type_code': trunc(msg_content.get('typeCode'), 4),
            'subtype_code': trunc(msg_content.get('subtypeCode'), 4),
            'imad': trunc(msg_content.get('imad'), 22),
            'omad': trunc(msg_content.get('omad'), 22),
            'input_cycle_date': msg_content.get('inputCycleDate'),
            'input_source': trunc(msg_content.get('inputSource'), 8),
            'input_sequence_number': trunc(msg_content.get('inputSequenceNumber'), 6),

            # Amount & Currency
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'USD',
            'instructed_amount': msg_content.get('instructedAmount'),
            'instructed_currency': msg_content.get('instructedCurrency') or 'USD',

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
        msg_content: Dict[str, Any],
        stg_id: str,
        batch_id: str
    ) -> GoldEntities:
        """Extract Gold layer entities from Fedwire message."""
        entities = GoldEntities()

        # Extract nested objects
        sender = msg_content.get('sender', {})
        sender_addr = sender.get('address', {}) if sender else {}
        receiver = msg_content.get('receiver', {})
        receiver_addr = receiver.get('address', {}) if receiver else {}
        originator = msg_content.get('originator', {})
        originator_addr = originator.get('address', {}) if originator else {}
        beneficiary = msg_content.get('beneficiary', {})
        beneficiary_addr = beneficiary.get('address', {}) if beneficiary else {}
        beneficiary_bank = msg_content.get('beneficiaryBank', {})
        intermediary_bank = msg_content.get('intermediaryBank', {})

        # Originator (Debtor Party)
        if originator.get('name'):
            entities.parties.append(PartyData(
                name=originator.get('name'),
                role="DEBTOR",
                party_type='UNKNOWN',
                street_name=originator_addr.get('line1'),
                town_name=originator_addr.get('city'),
                post_code=originator_addr.get('zipCode'),
                country_sub_division=originator_addr.get('state'),
                country=originator_addr.get('country') or 'US',
                identification_type=originator.get('identifierType'),
                identification_number=originator.get('identifier'),
            ))

        # Beneficiary (Creditor Party)
        if beneficiary.get('name'):
            entities.parties.append(PartyData(
                name=beneficiary.get('name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                street_name=beneficiary_addr.get('line1'),
                town_name=beneficiary_addr.get('city'),
                post_code=beneficiary_addr.get('zipCode'),
                country_sub_division=beneficiary_addr.get('state'),
                country=beneficiary_addr.get('country') or 'US',
                identification_type=beneficiary.get('identifierType'),
                identification_number=beneficiary.get('identifier'),
            ))

        # Originator Account (Debtor Account)
        if originator.get('accountNumber'):
            entities.accounts.append(AccountData(
                account_number=originator.get('accountNumber'),
                role="DEBTOR",
                account_type='CACC',
                currency=msg_content.get('currency') or 'USD',
            ))

        # Beneficiary Account (Creditor Account)
        if beneficiary.get('accountNumber'):
            entities.accounts.append(AccountData(
                account_number=beneficiary.get('accountNumber'),
                role="CREDITOR",
                account_type='CACC',
                currency=msg_content.get('currency') or 'USD',
            ))

        # Sender FI (Debtor Agent)
        if sender.get('routingNumber'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=sender.get('name'),
                short_name=sender.get('shortName'),
                bic=sender.get('bic'),
                lei=sender.get('lei'),
                clearing_code=sender.get('routingNumber'),
                clearing_system='USABA',
                address_line1=sender_addr.get('line1'),
                town_name=sender_addr.get('city'),
                country=sender_addr.get('country') or 'US',
            ))

        # Receiver FI / Beneficiary Bank (Creditor Agent)
        if receiver.get('routingNumber') or beneficiary_bank.get('routingNumber'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=receiver.get('name') or beneficiary_bank.get('name'),
                short_name=receiver.get('shortName'),
                bic=receiver.get('bic') or beneficiary_bank.get('bic'),
                lei=receiver.get('lei'),
                clearing_code=receiver.get('routingNumber') or beneficiary_bank.get('routingNumber'),
                clearing_system='USABA',
                address_line1=receiver_addr.get('line1'),
                town_name=receiver_addr.get('city'),
                country=receiver_addr.get('country') or 'US',
            ))

        # Intermediary Bank
        if intermediary_bank and intermediary_bank.get('routingNumber'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INTERMEDIARY",
                name=intermediary_bank.get('name'),
                clearing_code=intermediary_bank.get('routingNumber'),
                clearing_system='USABA',
                country='US',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('FEDWIRE', FedwireExtractor())
ExtractorRegistry.register('fedwire', FedwireExtractor())
