"""SWIFT MT103 (Single Customer Credit Transfer) Extractor."""

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


class MT103SwiftParser:
    """Parser for SWIFT MT103 block-format messages."""

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse MT103 SWIFT message into structured dict."""
        result = {}

        # Parse SWIFT blocks
        blocks = self._parse_blocks(raw_content)

        # Block 1: Basic Header
        if '1' in blocks:
            result.update(self._parse_block1(blocks['1']))

        # Block 2: Application Header
        if '2' in blocks:
            result.update(self._parse_block2(blocks['2']))

        # Block 3: User Header
        if '3' in blocks:
            result.update(self._parse_block3(blocks['3']))

        # Block 4: Text (main content)
        if '4' in blocks:
            result.update(self._parse_block4(blocks['4']))

        # Block 5: Trailer
        if '5' in blocks:
            result.update(self._parse_block5(blocks['5']))

        return result

    def _parse_blocks(self, content: str) -> Dict[str, str]:
        """Split message into numbered blocks."""
        blocks = {}
        # Match {N:...} patterns
        pattern = r'\{(\d):([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        for match in re.finditer(pattern, content, re.DOTALL):
            block_num = match.group(1)
            block_content = match.group(2)
            blocks[block_num] = block_content
        return blocks

    def _parse_block1(self, content: str) -> Dict[str, Any]:
        """Parse Block 1: Basic Header."""
        result = {}
        if len(content) >= 12:
            result['applicationId'] = content[0:1]  # F = FIN
            result['serviceId'] = content[1:3]  # 01 = GPA
            result['senderBic'] = content[3:15].strip('X') if len(content) >= 15 else content[3:]
        return result

    def _parse_block2(self, content: str) -> Dict[str, Any]:
        """Parse Block 2: Application Header."""
        result = {}
        if content.startswith('O'):  # Output message
            result['messageDirection'] = 'OUTPUT'
            if len(content) >= 4:
                result['messageType'] = content[1:4]  # e.g., 103
            if len(content) >= 14:
                # HHMM format for time + YYMMDD date
                time_str = content[4:8]
                date_str = content[8:14]
                result['inputTime'] = f"{time_str[:2]}:{time_str[2:]}"
                result['messageInputDate'] = f"20{date_str[:2]}-{date_str[2:4]}-{date_str[4:6]}"
            if len(content) >= 26:
                result['receiverBic'] = content[14:26].strip('X')
        elif content.startswith('I'):  # Input message
            result['messageDirection'] = 'INPUT'
            if len(content) >= 4:
                result['messageType'] = content[1:4]
            if len(content) >= 16:
                result['receiverBic'] = content[4:16].strip('X')
        return result

    def _parse_block3(self, content: str) -> Dict[str, Any]:
        """Parse Block 3: User Header."""
        result = {}
        # Parse sub-blocks like {108:value}
        pattern = r'\{(\d+):([^}]+)\}'
        for match in re.finditer(pattern, content):
            tag = match.group(1)
            value = match.group(2)
            if tag == '108':
                result['senderReference'] = value
            elif tag == '121':
                result['uetr'] = value
        return result

    def _parse_block4(self, content: str) -> Dict[str, Any]:
        """Parse Block 4: Text (message fields)."""
        result = {}

        # Split into lines and parse :XX: tagged fields
        lines = content.strip().split('\n')
        current_tag = None
        current_value = []

        for line in lines:
            line = line.strip()
            if not line or line == '-':
                continue

            # Check for new tag
            tag_match = re.match(r'^:(\d+[A-Z]?):(.*)$', line)
            if tag_match:
                # Save previous field
                if current_tag:
                    self._set_field(result, current_tag, '\n'.join(current_value))
                # Start new field
                current_tag = tag_match.group(1)
                current_value = [tag_match.group(2)] if tag_match.group(2) else []
            elif current_tag:
                # Continuation line
                current_value.append(line)

        # Save last field
        if current_tag:
            self._set_field(result, current_tag, '\n'.join(current_value))

        return result

    def _set_field(self, result: Dict[str, Any], tag: str, value: str) -> None:
        """Set field value based on MT103 tag."""
        value = value.strip()

        if tag == '20':
            result['transactionReferenceNumber'] = value
        elif tag == '23B':
            result['bankOperationCode'] = value
        elif tag == '23E':
            result['instructionCode'] = result.get('instructionCode', [])
            if isinstance(result['instructionCode'], list):
                result['instructionCode'].append(value)
            else:
                result['instructionCode'] = [result['instructionCode'], value]
        elif tag == '32A':
            # Date + Currency + Amount: YYMMDDCCCAMOUNT
            result['valueDate'] = self._parse_date(value[:6])
            result['currencyCode'] = value[6:9]
            result['amount'] = self._parse_amount(value[9:])
        elif tag == '33B':
            # Currency + Amount: CCCAMOUNT
            result['instructedCurrency'] = value[:3]
            result['instructedAmount'] = self._parse_amount(value[3:])
        elif tag == '50K' or tag == '50A' or tag == '50F':
            result['orderingCustomer'] = self._parse_party_field(value, tag)
        elif tag == '52A' or tag == '52D':
            result['orderingInstitution'] = self._parse_institution_field(value, tag)
        elif tag == '53A' or tag == '53B' or tag == '53D':
            result['sendersCorrespondent'] = self._parse_institution_field(value, tag)
        elif tag == '54A' or tag == '54B' or tag == '54D':
            result['receiversCorrespondent'] = self._parse_institution_field(value, tag)
        elif tag == '56A' or tag == '56D':
            result['intermediaryInstitution'] = self._parse_institution_field(value, tag)
        elif tag == '57A' or tag == '57D':
            result['accountWithInstitution'] = self._parse_institution_field(value, tag)
        elif tag == '59' or tag == '59A' or tag == '59F':
            result['beneficiaryCustomer'] = self._parse_party_field(value, tag)
        elif tag == '70':
            result['remittanceInformation'] = value.replace('\n', ' ')
        elif tag == '71A':
            result['detailsOfCharges'] = {'chargeBearer': value}
        elif tag == '71F':
            # Sender's charges: CCCAMOUNT
            if len(value) >= 4:
                result['sendersChargesCurrency'] = value[:3]
                result['sendersChargesAmount'] = self._parse_amount(value[3:])
        elif tag == '71G':
            # Receiver's charges
            if len(value) >= 4:
                result['receiversChargesCurrency'] = value[:3]
                result['receiversChargesAmount'] = self._parse_amount(value[3:])
        elif tag == '72':
            result['senderToReceiverInformation'] = value.replace('\n', ' ')
        elif tag == '77B':
            result['regulatoryReporting'] = value.replace('\n', ' ')

    def _parse_party_field(self, value: str, tag: str) -> Dict[str, Any]:
        """Parse ordering/beneficiary customer field."""
        result = {}
        lines = value.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # First line may have account
            if i == 0:
                if line.startswith('/'):
                    # Account number
                    result['account'] = line[1:].split('\n')[0]
                    continue
                elif '/' in line and not line.startswith('/'):
                    # Party identifier format: /CODE/value
                    pass

            # Check for name vs address
            if i == 0 or (i == 1 and result.get('account')):
                result['name'] = line
            else:
                # Build address
                if 'address' not in result:
                    result['address'] = {}
                if 'streetName' not in result['address']:
                    result['address']['streetName'] = line
                elif 'townName' not in result['address']:
                    result['address']['townName'] = line
                elif 'country' not in result['address']:
                    result['address']['country'] = line[:2] if len(line) >= 2 else line

        return result

    def _parse_institution_field(self, value: str, tag: str) -> Dict[str, Any]:
        """Parse financial institution field."""
        result = {}
        lines = value.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Check for BIC (11 chars) or clearing code
            if i == 0:
                if len(line) >= 8 and line.isalnum():
                    result['bic'] = line
                elif line.startswith('/'):
                    result['account'] = line[1:]
                else:
                    result['name'] = line
            else:
                if 'name' not in result:
                    result['name'] = line
                elif 'country' not in result:
                    result['country'] = line[:2] if len(line) >= 2 else line

        return result

    def _parse_date(self, date_str: str) -> str:
        """Parse YYMMDD date to ISO format."""
        if len(date_str) >= 6:
            year = int(date_str[:2])
            # Handle Y2K: 00-49 = 2000s, 50-99 = 1900s
            full_year = 2000 + year if year < 50 else 1900 + year
            return f"{full_year}-{date_str[2:4]}-{date_str[4:6]}"
        return date_str

    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount with comma as decimal separator."""
        if not amount_str:
            return 0.0
        # Replace comma with period for decimal
        clean = amount_str.replace(',', '.').replace(' ', '')
        try:
            return float(clean)
        except ValueError:
            return 0.0

    def _parse_block5(self, content: str) -> Dict[str, Any]:
        """Parse Block 5: Trailer."""
        result = {}
        pattern = r'\{([A-Z]+):([^}]+)\}'
        for match in re.finditer(pattern, content):
            tag = match.group(1)
            value = match.group(2)
            if tag == 'MAC':
                result['mac'] = value
            elif tag == 'CHK':
                result['checksum'] = value
        return result


class MT103Extractor(BaseExtractor):
    """Extractor for SWIFT MT103 messages."""

    MESSAGE_TYPE = "MT103"
    SILVER_TABLE = "stg_mt103"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw MT103 content."""
        msg_id = raw_content.get('transactionReferenceNumber', '') or raw_content.get('senderReference', '')
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
        """Extract all Silver layer fields from MT103 message."""
        trunc = self.trunc

        # Extract nested objects
        ordering_cust = msg_content.get('orderingCustomer', {})
        ordering_cust_addr = ordering_cust.get('address', {}) if ordering_cust else {}
        ordering_inst = msg_content.get('orderingInstitution', {})
        senders_corr = msg_content.get('sendersCorrespondent', {})
        receivers_corr = msg_content.get('receiversCorrespondent', {})
        intermediary = msg_content.get('intermediaryInstitution', {})
        acct_with_inst = msg_content.get('accountWithInstitution', {})
        beneficiary = msg_content.get('beneficiaryCustomer', {})
        beneficiary_addr = beneficiary.get('address', {}) if beneficiary else {}
        details_of_charges = msg_content.get('detailsOfCharges', {})
        regulatory = msg_content.get('regulatoryReporting', {})

        # Instruction codes can be an array - join them
        instruction_codes = msg_content.get('instructionCode', [])
        if isinstance(instruction_codes, list):
            instruction_code_str = ','.join(str(c) for c in instruction_codes[:4])
        else:
            instruction_code_str = str(instruction_codes) if instruction_codes else None

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message References (matching actual table columns)
            'senders_reference': trunc(msg_content.get('senderReference') or msg_content.get('transactionReferenceNumber'), 16),
            'transaction_reference_number': trunc(msg_content.get('transactionReferenceNumber'), 16),
            'bank_operation_code': trunc(msg_content.get('bankOperationCode'), 4),
            'instruction_codes': trunc(instruction_code_str, 35),

            # Dates & Currency
            'value_date': msg_content.get('valueDate'),
            'currency': msg_content.get('currencyCode'),

            # Amount
            'amount': msg_content.get('amount'),

            # Ordering Customer (Field 50)
            'ordering_customer_name': trunc(ordering_cust.get('name'), 140),
            'ordering_customer_account': trunc(ordering_cust.get('account'), 35),
            'ordering_customer_address': trunc(ordering_cust_addr.get('streetName'), 140),
            'ordering_customer_country': ordering_cust_addr.get('country'),
            'ordering_customer_party_id': trunc(ordering_cust.get('partyIdentifier'), 35),
            'ordering_customer_national_id': trunc(ordering_cust.get('nationalId'), 35),

            # Ordering Institution (Field 52)
            'ordering_institution_bic': ordering_inst.get('bic'),
            'ordering_institution_name': trunc(ordering_inst.get('name'), 140),
            'ordering_institution_clearing_code': trunc(ordering_inst.get('clearingCode'), 35),
            'ordering_institution_country': ordering_inst.get('country'),

            # Sender's Correspondent (Field 53)
            'senders_correspondent_bic': senders_corr.get('bic'),
            'senders_correspondent_account': trunc(senders_corr.get('account'), 35),
            'senders_correspondent_name': trunc(senders_corr.get('name'), 140),

            # Receiver's Correspondent (Field 54)
            'receivers_correspondent_bic': receivers_corr.get('bic'),
            'receivers_correspondent_account': trunc(receivers_corr.get('account'), 35),
            'receivers_correspondent_name': trunc(receivers_corr.get('name'), 140),

            # Intermediary Institution (Field 56) - column names match DB schema
            'intermediary_bic': intermediary.get('bic'),
            'intermediary_account': trunc(intermediary.get('account'), 35),
            'intermediary_name': trunc(intermediary.get('name'), 140),

            # Account With Institution (Field 57) - column names match DB schema
            'account_with_institution_bic': acct_with_inst.get('bic'),
            'account_with_institution_account': trunc(acct_with_inst.get('account'), 35),
            'account_with_institution_name': trunc(acct_with_inst.get('name'), 140),

            # Beneficiary Customer (Field 59)
            'beneficiary_name': trunc(beneficiary.get('name'), 140),
            'beneficiary_account': trunc(beneficiary.get('account'), 35),
            'beneficiary_address': trunc(beneficiary_addr.get('streetName'), 140),
            'beneficiary_country': beneficiary_addr.get('country'),
            'beneficiary_party_id': trunc(beneficiary.get('partyIdentifier'), 35),

            # Remittance Information (Field 70)
            'remittance_information': trunc(msg_content.get('remittanceInformation'), 140),

            # Details of Charges (Field 71)
            'details_of_charges': trunc(details_of_charges.get('chargeBearer') if isinstance(details_of_charges, dict) else details_of_charges, 3),

            # Sender to Receiver Information (Field 72) - matches DB column name
            'sender_to_receiver_info': trunc(msg_content.get('senderToReceiverInformation'), 210),

            # Regulatory Reporting (Field 77B)
            'regulatory_reporting': trunc(regulatory.get('code') if isinstance(regulatory, dict) else regulatory, 140),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT - matches DB schema exactly."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'senders_reference', 'transaction_reference_number', 'bank_operation_code', 'instruction_codes',
            'value_date', 'currency', 'amount',
            'ordering_customer_name', 'ordering_customer_account', 'ordering_customer_address',
            'ordering_customer_country', 'ordering_customer_party_id', 'ordering_customer_national_id',
            'ordering_institution_bic', 'ordering_institution_name', 'ordering_institution_clearing_code',
            'ordering_institution_country',
            'senders_correspondent_bic', 'senders_correspondent_account', 'senders_correspondent_name',
            'receivers_correspondent_bic', 'receivers_correspondent_account', 'receivers_correspondent_name',
            'intermediary_bic', 'intermediary_account', 'intermediary_name',
            'account_with_institution_bic', 'account_with_institution_account', 'account_with_institution_name',
            'beneficiary_name', 'beneficiary_account', 'beneficiary_address', 'beneficiary_country',
            'beneficiary_party_id',
            'remittance_information', 'details_of_charges', 'sender_to_receiver_info',
            'regulatory_reporting',
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
        """Extract Gold layer entities from MT103 message."""
        entities = GoldEntities()

        # Extract nested objects
        ordering_cust = msg_content.get('orderingCustomer', {})
        ordering_cust_addr = ordering_cust.get('address', {}) if ordering_cust else {}
        ordering_inst = msg_content.get('orderingInstitution', {})
        beneficiary = msg_content.get('beneficiaryCustomer', {})
        beneficiary_addr = beneficiary.get('address', {}) if beneficiary else {}
        acct_with_inst = msg_content.get('accountWithInstitution', {})
        intermediary = msg_content.get('intermediaryInstitution', {})

        # Ordering Customer (Debtor)
        if ordering_cust.get('name'):
            entities.parties.append(PartyData(
                name=ordering_cust.get('name'),
                role="DEBTOR",
                party_type='UNKNOWN',
                street_name=ordering_cust_addr.get('streetName'),
                building_number=ordering_cust_addr.get('buildingNumber'),
                post_code=ordering_cust_addr.get('postalCode'),
                town_name=ordering_cust_addr.get('townName'),
                country_sub_division=ordering_cust_addr.get('countrySubDivision'),
                country=ordering_cust_addr.get('country'),
                identification_type='CUST' if ordering_cust.get('partyIdentifier') else ('NATL' if ordering_cust.get('nationalId') else None),
                identification_number=ordering_cust.get('partyIdentifier') or ordering_cust.get('nationalId'),
            ))

        # Beneficiary Customer (Creditor)
        if beneficiary.get('name'):
            entities.parties.append(PartyData(
                name=beneficiary.get('name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                street_name=beneficiary_addr.get('streetName'),
                building_number=beneficiary_addr.get('buildingNumber'),
                post_code=beneficiary_addr.get('postalCode'),
                town_name=beneficiary_addr.get('townName'),
                country_sub_division=beneficiary_addr.get('countrySubDivision'),
                country=beneficiary_addr.get('country'),
                identification_type='CUST' if beneficiary.get('partyIdentifier') else None,
                identification_number=beneficiary.get('partyIdentifier'),
            ))

        # Ordering Customer Account (Debtor Account)
        if ordering_cust.get('account'):
            entities.accounts.append(AccountData(
                account_number=ordering_cust.get('account'),
                role="DEBTOR",
                account_type='UNKNOWN',
                currency=msg_content.get('currencyCode') or 'XXX',
            ))

        # Beneficiary Account (Creditor Account)
        if beneficiary.get('account'):
            entities.accounts.append(AccountData(
                account_number=beneficiary.get('account'),
                role="CREDITOR",
                account_type='UNKNOWN',
                currency=msg_content.get('currencyCode') or 'XXX',
            ))

        # Ordering Institution (Debtor Agent)
        if ordering_inst.get('bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=ordering_inst.get('name'),
                bic=ordering_inst.get('bic'),
                clearing_code=ordering_inst.get('clearingCode'),
                country=ordering_inst.get('country') or 'XX',
            ))

        # Account With Institution (Creditor Agent)
        if acct_with_inst.get('bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=acct_with_inst.get('name'),
                bic=acct_with_inst.get('bic'),
                country=acct_with_inst.get('country') or 'XX',
            ))

        # Intermediary Institution
        if intermediary.get('bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INTERMEDIARY",
                name=intermediary.get('name'),
                bic=intermediary.get('bic'),
                country=intermediary.get('country') or 'XX',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('MT103', MT103Extractor())
ExtractorRegistry.register('mt103', MT103Extractor())
ExtractorRegistry.register('103', MT103Extractor())
