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


class UpiJsonParser:
    """Parser for UPI JSON format messages (NPCI specification).

    Handles the nested JSON structure:
    {
        "Head": { "msgId": "...", "orgId": "NPCI", "ts": "...", "ver": "2.0", "txnType": "PAY" },
        "Txn": { "id": "...", "type": "PAY", "note": "...", ... },
        "Payer": {
            "addr": "treasuryops@okicici",
            "name": "Mumbai Tech Innovations Pvt Ltd",
            "type": "ENTITY",
            "Ac": { "Detail": [{"name": "ACNUM", "value": "..."}, ...] },
            "Amount": { "curr": "INR", "value": "175000.00" },
            ...
        },
        "Payee": { ... },
        // Also supports flat fields like:
        "headMsgId", "payerAddr", "payerName", "payerAcAcnum", etc.
    }
    """

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse UPI JSON message into structured dict with all standard fields."""
        result = {
            'messageType': 'UPI',
        }

        # Handle dict input (pre-parsed)
        if isinstance(raw_content, dict):
            data = raw_content
        else:
            # Parse JSON string
            if raw_content.strip().startswith('{'):
                try:
                    data = json.loads(raw_content)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse UPI JSON: {e}")
                    return result
            else:
                # Try XML parser for non-JSON
                return self._parse_xml(raw_content)

        # Check for nested structure (Head/Txn/Payer/Payee)
        head = data.get('Head', {})
        txn = data.get('Txn', {})
        payer = data.get('Payer', {})
        payee = data.get('Payee', {})

        # Extract Head fields - prefer nested then flat
        result['headMsgId'] = head.get('msgId') or data.get('headMsgId')
        result['headOrgId'] = head.get('orgId') or data.get('headOrgId')
        result['headTs'] = head.get('ts') or data.get('headTs')
        result['headVer'] = head.get('ver') or data.get('headVer')

        # Extract Txn fields
        result['txnId'] = txn.get('id') or data.get('txnId')
        result['txnType'] = txn.get('type') or head.get('txnType') or data.get('txnType')
        result['txnTs'] = txn.get('ts') or data.get('txnTs')
        result['txnNote'] = txn.get('note') or data.get('txnNote')
        result['txnRefId'] = txn.get('refId') or data.get('txnRefId')
        result['txnRefUrl'] = txn.get('refUrl') or data.get('txnRefUrl')

        # Extract Payer fields
        result['payerAddr'] = payer.get('addr') or data.get('payerAddr')
        result['payerName'] = payer.get('name') or data.get('payerName')
        result['payerType'] = payer.get('type') or data.get('payerType')
        result['payerVpa'] = payer.get('vpa') or data.get('payerVpa') or result.get('payerAddr')

        # Payer Account details from nested Ac/Detail array
        payer_ac = payer.get('Ac', {})
        result['payerAcAddrType'] = payer_ac.get('addrType') or data.get('payerAcAddrType')

        payer_details = payer_ac.get('Detail', [])
        for detail in payer_details:
            name = detail.get('name', '')
            value = detail.get('value')
            if name == 'ACNUM':
                result['payerAcAcnum'] = value
            elif name == 'ACTYPE':
                result['payerAcActype'] = value
            elif name == 'IFSC':
                result['payerAcIfsc'] = value
            elif name == 'NAME':
                result['payerAcName'] = value

        # Fallback to flat fields
        result['payerAcAcnum'] = result.get('payerAcAcnum') or data.get('payerAcAcnum')
        result['payerAcActype'] = result.get('payerAcActype') or data.get('payerAcActype')
        result['payerAcIfsc'] = result.get('payerAcIfsc') or data.get('payerAcIfsc')

        # Payer Amount
        payer_amount = payer.get('Amount', {})
        result['payerAmountCurr'] = payer_amount.get('curr') or data.get('payerAmountCurr')
        amount_value = payer_amount.get('value') or data.get('payerAmountValue')
        if amount_value:
            try:
                result['payerAmountValue'] = float(amount_value)
            except (ValueError, TypeError):
                result['payerAmountValue'] = None

        # Payer Address
        payer_address = payer.get('Address', {})
        result['payerAddressLine1'] = payer_address.get('line1')
        result['payerAddressLine2'] = payer_address.get('line2')
        result['payerCity'] = payer_address.get('city')
        result['payerState'] = payer_address.get('state')
        result['payerCountry'] = payer_address.get('country') or 'IN'
        result['payerPostalCode'] = payer_address.get('postalCode')

        # Payer Contact
        payer_contact = payer.get('Contact', {})
        result['payerContactName'] = payer_contact.get('name')
        result['payerContactPhone'] = payer_contact.get('phone')
        result['payerContactEmail'] = payer_contact.get('email')
        result['payerDeviceMobile'] = payer_contact.get('phone') or data.get('payerDeviceMobile')

        # Payer OrgId
        payer_org = payer.get('OrgId', {})
        result['payerPan'] = payer_org.get('pan')
        result['payerGstin'] = payer_org.get('gstin')

        # Extract Payee fields
        result['payeeAddr'] = payee.get('addr') or data.get('payeeAddr')
        result['payeeName'] = payee.get('name') or data.get('payeeName')
        result['payeeType'] = payee.get('type') or data.get('payeeType')
        result['payeeVpa'] = payee.get('vpa') or data.get('payeeVpa') or result.get('payeeAddr')

        # Payee Account details from nested Ac/Detail array
        payee_ac = payee.get('Ac', {})
        result['payeeAcAddrType'] = payee_ac.get('addrType') or data.get('payeeAcAddrType')

        payee_details = payee_ac.get('Detail', [])
        for detail in payee_details:
            name = detail.get('name', '')
            value = detail.get('value')
            if name == 'ACNUM':
                result['payeeAcAcnum'] = value
            elif name == 'ACTYPE':
                result['payeeAcActype'] = value
            elif name == 'IFSC':
                result['payeeAcIfsc'] = value
            elif name == 'NAME':
                result['payeeAcName'] = value

        # Fallback to flat fields
        result['payeeAcAcnum'] = result.get('payeeAcAcnum') or data.get('payeeAcAcnum')
        result['payeeAcActype'] = result.get('payeeAcActype') or data.get('payeeAcActype')
        result['payeeAcIfsc'] = result.get('payeeAcIfsc') or data.get('payeeAcIfsc')

        # Payee Address
        payee_address = payee.get('Address', {})
        result['payeeAddressLine1'] = payee_address.get('line1')
        result['payeeAddressLine2'] = payee_address.get('line2')
        result['payeeCity'] = payee_address.get('city')
        result['payeeState'] = payee_address.get('state')
        result['payeeCountry'] = payee_address.get('country') or 'IN'
        result['payeePostalCode'] = payee_address.get('postalCode')

        # Payee Contact
        payee_contact = payee.get('Contact', {})
        result['payeeContactName'] = payee_contact.get('name')
        result['payeeContactPhone'] = payee_contact.get('phone')
        result['payeeContactEmail'] = payee_contact.get('email')
        result['payeeDeviceMobile'] = payee_contact.get('phone') or data.get('payeeDeviceMobile')

        # Payee OrgId
        payee_org = payee.get('OrgId', {})
        result['payeePan'] = payee_org.get('pan')
        result['payeeGstin'] = payee_org.get('gstin')

        # Legacy/flat field mappings for backward compatibility
        result['transactionId'] = data.get('transactionId') or result.get('headMsgId')
        result['amount'] = data.get('amount') or result.get('payerAmountValue')
        result['currency'] = data.get('currency') or result.get('payerAmountCurr') or 'INR'
        result['purposeCode'] = data.get('purposeCode')
        result['settlementDate'] = data.get('settlementDate')
        result['creationDateTime'] = result.get('headTs')

        # Additional flat fields that may be present
        result['payerAccount'] = data.get('payerAccount') or result.get('payerAcAcnum')
        result['payeeAccount'] = data.get('payeeAccount') or result.get('payeeAcAcnum')
        result['payerIfsc'] = data.get('payerIfsc') or result.get('payerAcIfsc')
        result['payeeIfsc'] = data.get('payeeIfsc') or result.get('payeeAcIfsc')
        result['remittanceInfo'] = result.get('txnNote')

        return result

    def _parse_xml(self, content: str) -> Dict[str, Any]:
        """Parse UPI XML format (fallback for XML content)."""
        result = {'messageType': 'UPI'}

        # Remove namespaces for easier parsing
        content = re.sub(r'xmlns[^"]*"[^"]*"', '', content)
        content = re.sub(r'<([a-zA-Z]+):', r'<', content)
        content = re.sub(r'</([a-zA-Z]+):', r'</', content)

        # Head fields
        head_match = re.search(r'<Head[^>]*>', content)
        if head_match:
            head_block = head_match.group(0)
            result['headMsgId'] = self._extract_attr(head_block, 'msgId')
            result['headOrgId'] = self._extract_attr(head_block, 'orgId')
            result['headTs'] = self._extract_attr(head_block, 'ts')
            result['headVer'] = self._extract_attr(head_block, 'ver')

        # Txn fields
        txn_match = re.search(r'<Txn[^>]*>', content)
        if txn_match:
            txn_block = txn_match.group(0)
            result['txnId'] = self._extract_attr(txn_block, 'id')
            result['txnType'] = self._extract_attr(txn_block, 'type')
            result['txnTs'] = self._extract_attr(txn_block, 'ts')
            result['txnNote'] = self._extract_attr(txn_block, 'note')

        # Payer fields
        payer_match = re.search(r'<Payer[^>]*>', content)
        if payer_match:
            payer_block = payer_match.group(0)
            result['payerAddr'] = self._extract_attr(payer_block, 'addr')
            result['payerName'] = self._extract_attr(payer_block, 'name')
            result['payerType'] = self._extract_attr(payer_block, 'type')

        # Payee fields
        payee_match = re.search(r'<Payee[^>]*>', content)
        if payee_match:
            payee_block = payee_match.group(0)
            result['payeeAddr'] = self._extract_attr(payee_block, 'addr')
            result['payeeName'] = self._extract_attr(payee_block, 'name')
            result['payeeType'] = self._extract_attr(payee_block, 'type')

        return result

    def _extract_attr(self, tag: str, attr_name: str) -> Optional[str]:
        """Extract attribute value from XML tag."""
        match = re.search(rf'{attr_name}="([^"]*)"', tag)
        return match.group(1) if match else None


class UpiXmlParser:
    """Parser for UPI XML format messages (NPCI specification).

    Extracts all 84 standard data elements from UPI messages.
    Parser output keys are in camelCase format matching the silver_field_mappings.parser_path.
    """

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse UPI XML message into structured dict with all standard fields."""
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

        # =========================================================================
        # ACK FIELDS (4)
        # =========================================================================
        ack_match = re.search(r'<Ack[^>]*>', content)
        if ack_match:
            ack_block = ack_match.group(0)
            result['ackApi'] = self._extract_attr(ack_block, 'api')
            result['ackErr'] = self._extract_attr(ack_block, 'err')
            result['ackReqMsgId'] = self._extract_attr(ack_block, 'reqMsgId')
            result['ackTs'] = self._extract_attr(ack_block, 'ts')

        # =========================================================================
        # HEAD FIELDS (4)
        # =========================================================================
        head_match = re.search(r'<Head[^>]*>', content)
        if head_match:
            head_block = head_match.group(0)
            result['headMsgId'] = self._extract_attr(head_block, 'msgId')
            result['headOrgId'] = self._extract_attr(head_block, 'orgId')
            result['headTs'] = self._extract_attr(head_block, 'ts')
            result['headVer'] = self._extract_attr(head_block, 'ver')

        # =========================================================================
        # META FIELDS (2)
        # =========================================================================
        meta_match = re.search(r'<Meta[^>]*>', content)
        if meta_match:
            meta_block = meta_match.group(0)
            result['metaName'] = self._extract_attr(meta_block, 'name')
            result['metaValue'] = self._extract_attr(meta_block, 'value')

        # =========================================================================
        # PAYEE FIELDS (5 basic + 4 Ac + 7 Device + 4 Info + 3 Merchant = 23)
        # =========================================================================
        # Get full Payee block for nested elements
        payee_block_match = re.search(r'<Payee[^>]*>(.*?)</Payee>', content, re.DOTALL)
        payee_tag_match = re.search(r'<Payee[^>]*>', content)

        if payee_tag_match:
            payee_tag = payee_tag_match.group(0)
            # Payee basic fields
            result['payeeAddr'] = self._extract_attr(payee_tag, 'addr')
            result['payeeCode'] = self._extract_attr(payee_tag, 'code')
            result['payeeName'] = self._extract_attr(payee_tag, 'name')
            result['payeeSeqNum'] = self._extract_attr(payee_tag, 'seqNum')
            result['payeeType'] = self._extract_attr(payee_tag, 'type')

        if payee_block_match:
            payee_content = payee_block_match.group(1)

            # Payee/Ac fields
            ac_match = re.search(r'<Ac[^>]*>', payee_content)
            if ac_match:
                result['payeeAcAddrType'] = self._extract_attr(ac_match.group(0), 'addrType')

            # Payee/Ac/Detail fields
            result['payeeAcAcnum'] = self._extract_detail_value(payee_content, 'ACNUM')
            result['payeeAcActype'] = self._extract_detail_value(payee_content, 'ACTYPE')
            result['payeeAcIfsc'] = self._extract_detail_value(payee_content, 'IFSC')

            # Payee/Device/Tag fields
            device_match = re.search(r'<Device[^>]*>(.*?)</Device>', payee_content, re.DOTALL)
            if device_match:
                device_content = device_match.group(1)
                result['payeeDeviceGeocode'] = self._extract_tag_value(device_content, 'GEOCODE')
                result['payeeDeviceId'] = self._extract_tag_value(device_content, 'ID')
                result['payeeDeviceIp'] = self._extract_tag_value(device_content, 'IP')
                result['payeeDeviceLocation'] = self._extract_tag_value(device_content, 'LOCATION')
                result['payeeDeviceMobile'] = self._extract_tag_value(device_content, 'MOBILE')
                result['payeeDeviceOs'] = self._extract_tag_value(device_content, 'OS')
                result['payeeDeviceType'] = self._extract_tag_value(device_content, 'TYPE')

            # Payee/Info/Identity fields
            identity_match = re.search(r'<Identity[^>]*>', payee_content)
            if identity_match:
                identity_tag = identity_match.group(0)
                result['payeeIdentityType'] = self._extract_attr(identity_tag, 'type')
                result['payeeIdentityVerifiedName'] = self._extract_attr(identity_tag, 'verifiedName')

            # Payee/Info/Rating fields
            rating_match = re.search(r'<Rating[^>]*>', payee_content)
            if rating_match:
                rating_tag = rating_match.group(0)
                result['payeeRatingVerifiedAddress'] = self._extract_attr(rating_tag, 'VerifiedAddress')
                result['payeeRatingWhitelisted'] = self._extract_attr(rating_tag, 'whiteListed')

            # Payee/Merchant fields
            merchant_match = re.search(r'<Merchant[^>]*>', payee_content)
            if merchant_match:
                merchant_tag = merchant_match.group(0)
                result['merchantId'] = self._extract_attr(merchant_tag, 'id')
                result['merchantSubId'] = self._extract_attr(merchant_tag, 'subId')
                result['merchantTermId'] = self._extract_attr(merchant_tag, 'termId')

        # =========================================================================
        # PAYER FIELDS (5 basic + 4 Ac + 4 Amount + 2 Creds + 7 Device + 4 Info = 26)
        # =========================================================================
        # Get full Payer block for nested elements
        payer_block_match = re.search(r'<Payer[^>]*>(.*?)</Payer>', content, re.DOTALL)
        payer_tag_match = re.search(r'<Payer[^>]*>', content)

        if payer_tag_match:
            payer_tag = payer_tag_match.group(0)
            # Payer basic fields
            result['payerAddr'] = self._extract_attr(payer_tag, 'addr')
            result['payerCode'] = self._extract_attr(payer_tag, 'code')
            result['payerName'] = self._extract_attr(payer_tag, 'name')
            result['payerSeqNum'] = self._extract_attr(payer_tag, 'seqNum')
            result['payerType'] = self._extract_attr(payer_tag, 'type')

        if payer_block_match:
            payer_content = payer_block_match.group(1)

            # Payer/Ac fields
            ac_match = re.search(r'<Ac[^>]*>', payer_content)
            if ac_match:
                result['payerAcAddrType'] = self._extract_attr(ac_match.group(0), 'addrType')

            # Payer/Ac/Detail fields
            result['payerAcAcnum'] = self._extract_detail_value(payer_content, 'ACNUM')
            result['payerAcActype'] = self._extract_detail_value(payer_content, 'ACTYPE')
            result['payerAcIfsc'] = self._extract_detail_value(payer_content, 'IFSC')

            # Payer/Amount fields
            amount_match = re.search(r'<Amount[^>]*>', payer_content)
            if amount_match:
                amount_tag = amount_match.group(0)
                result['payerAmountCurr'] = self._extract_attr(amount_tag, 'curr')
                value_str = self._extract_attr(amount_tag, 'value')
                if value_str:
                    try:
                        result['payerAmountValue'] = float(value_str)
                    except ValueError:
                        result['payerAmountValue'] = None

            # Payer/Amount/Split fields
            split_match = re.search(r'<Split[^>]*>', payer_content)
            if split_match:
                split_tag = split_match.group(0)
                result['payerAmountSplitName'] = self._extract_attr(split_tag, 'name')
                split_value_str = self._extract_attr(split_tag, 'value')
                if split_value_str:
                    try:
                        result['payerAmountSplitValue'] = float(split_value_str)
                    except ValueError:
                        result['payerAmountSplitValue'] = None

            # Payer/Creds/Cred fields
            cred_match = re.search(r'<Cred[^>]*>', payer_content)
            if cred_match:
                cred_tag = cred_match.group(0)
                result['payerCredSubType'] = self._extract_attr(cred_tag, 'subType')
                result['payerCredType'] = self._extract_attr(cred_tag, 'type')

            # Payer/Device/Tag fields
            device_match = re.search(r'<Device[^>]*>(.*?)</Device>', payer_content, re.DOTALL)
            if device_match:
                device_content = device_match.group(1)
                result['payerDeviceGeocode'] = self._extract_tag_value(device_content, 'GEOCODE')
                result['payerDeviceId'] = self._extract_tag_value(device_content, 'ID')
                result['payerDeviceIp'] = self._extract_tag_value(device_content, 'IP')
                result['payerDeviceLocation'] = self._extract_tag_value(device_content, 'LOCATION')
                result['payerDeviceMobile'] = self._extract_tag_value(device_content, 'MOBILE')
                result['payerDeviceOs'] = self._extract_tag_value(device_content, 'OS')
                result['payerDeviceType'] = self._extract_tag_value(device_content, 'TYPE')

            # Payer/Info/Identity fields
            identity_match = re.search(r'<Identity[^>]*>', payer_content)
            if identity_match:
                identity_tag = identity_match.group(0)
                result['payerIdentityType'] = self._extract_attr(identity_tag, 'type')
                result['payerIdentityVerifiedName'] = self._extract_attr(identity_tag, 'verifiedName')

            # Payer/Info/Rating fields
            rating_match = re.search(r'<Rating[^>]*>', payer_content)
            if rating_match:
                rating_tag = rating_match.group(0)
                result['payerRatingVerifiedAddress'] = self._extract_attr(rating_tag, 'VerifiedAddress')
                result['payerRatingWhitelisted'] = self._extract_attr(rating_tag, 'whiteListed')

        # =========================================================================
        # PSP FIELDS (1)
        # =========================================================================
        psp_match = re.search(r'<Psp[^>]*>', content)
        if psp_match:
            result['pspName'] = self._extract_attr(psp_match.group(0), 'name')
        # Also check Head/@orgId as PSP orgId is often in Head
        if not result.get('pspName') and result.get('headOrgId'):
            # headOrgId is already captured above
            pass

        # =========================================================================
        # REF FIELDS (4)
        # =========================================================================
        ref_match = re.search(r'<Ref[^>]*>', content)
        if ref_match:
            ref_tag = ref_match.group(0)
            result['refAddr'] = self._extract_attr(ref_tag, 'addr')
            result['refSeqNum'] = self._extract_attr(ref_tag, 'seqNum')
            result['refType'] = self._extract_attr(ref_tag, 'type')
            result['refValue'] = self._extract_attr(ref_tag, 'value')

        # =========================================================================
        # REQAUTHDETAILS FIELDS (2)
        # =========================================================================
        req_auth_match = re.search(r'<ReqAuthDetails[^>]*>', content)
        if req_auth_match:
            req_auth_tag = req_auth_match.group(0)
            result['reqAuthApi'] = self._extract_attr(req_auth_tag, 'api')
            result['reqAuthVersion'] = self._extract_attr(req_auth_tag, 'version')

        # =========================================================================
        # RESP FIELDS (4)
        # =========================================================================
        resp_match = re.search(r'<Resp[^>]*>', content)
        if resp_match:
            resp_tag = resp_match.group(0)
            result['respErrCode'] = self._extract_attr(resp_tag, 'errCode')
            result['respMsgId'] = self._extract_attr(resp_tag, 'msgId')
            result['respReqMsgId'] = self._extract_attr(resp_tag, 'reqMsgId')
            result['respResult'] = self._extract_attr(resp_tag, 'result')

        # =========================================================================
        # TXN FIELDS (9 basic + 3 RiskScores + 2 Rules = 14)
        # =========================================================================
        txn_tag_match = re.search(r'<Txn[^>]*>', content)
        txn_block_match = re.search(r'<Txn[^>]*>(.*?)</Txn>', content, re.DOTALL)

        if txn_tag_match:
            txn_tag = txn_tag_match.group(0)
            result['txnCustRef'] = self._extract_attr(txn_tag, 'custRef')
            result['txnId'] = self._extract_attr(txn_tag, 'id')
            result['txnNote'] = self._extract_attr(txn_tag, 'note')
            result['txnOrgRespCode'] = self._extract_attr(txn_tag, 'orgRespCode')
            result['txnOrgTxnId'] = self._extract_attr(txn_tag, 'orgTxnId')
            result['txnRefId'] = self._extract_attr(txn_tag, 'refId')
            result['txnRefUrl'] = self._extract_attr(txn_tag, 'refUrl')
            result['txnTs'] = self._extract_attr(txn_tag, 'ts')
            result['txnType'] = self._extract_attr(txn_tag, 'type')

        if txn_block_match:
            txn_content = txn_block_match.group(1)

            # Txn/RiskScores/Score fields
            score_match = re.search(r'<Score[^>]*>', txn_content)
            if score_match:
                score_tag = score_match.group(0)
                result['riskScoreProvider'] = self._extract_attr(score_tag, 'provider')
                result['riskScoreType'] = self._extract_attr(score_tag, 'type')
                result['riskScoreValue'] = self._extract_attr(score_tag, 'value')

            # Txn/Rules/Rule fields
            rule_match = re.search(r'<Rule[^>]*>', txn_content)
            if rule_match:
                rule_tag = rule_match.group(0)
                result['ruleName'] = self._extract_attr(rule_tag, 'name')
                result['ruleValue'] = self._extract_attr(rule_tag, 'value')

        # =========================================================================
        # LEGACY FIELD MAPPING (for backward compatibility)
        # =========================================================================
        # Map new fields to old field names for existing code
        if result.get('headMsgId'):
            result['transactionId'] = result['headMsgId']
        if result.get('headTs'):
            result['creationDateTime'] = result['headTs']
        if result.get('txnId'):
            result['transactionRefId'] = result['txnId']
        if result.get('txnNote'):
            result['remittanceInfo'] = result['txnNote']
        if result.get('txnType'):
            result['transactionType'] = result['txnType']
        if result.get('payerAddr'):
            result['payerVpa'] = result['payerAddr']
        if result.get('payeeAddr'):
            result['payeeVpa'] = result['payeeAddr']
        if result.get('payerAcIfsc'):
            result['payerIfsc'] = result['payerAcIfsc']
        if result.get('payeeAcIfsc'):
            result['payeeIfsc'] = result['payeeAcIfsc']
        if result.get('payerAcAcnum'):
            result['payerAccount'] = result['payerAcAcnum']
        if result.get('payeeAcAcnum'):
            result['payeeAccount'] = result['payeeAcAcnum']
        if result.get('payerDeviceMobile'):
            result['payerMobile'] = result['payerDeviceMobile']
        if result.get('payeeDeviceMobile'):
            result['payeeMobile'] = result['payeeDeviceMobile']
        if result.get('payerAmountCurr'):
            result['currency'] = result['payerAmountCurr']
        if result.get('payerAmountValue'):
            result['amount'] = result['payerAmountValue']

        return result

    def _extract_attr(self, tag: str, attr_name: str) -> Optional[str]:
        """Extract attribute value from XML tag."""
        match = re.search(rf'{attr_name}="([^"]*)"', tag)
        return match.group(1) if match else None

    def _extract_detail_value(self, content: str, name: str) -> Optional[str]:
        """Extract value from Detail element with given name attribute."""
        match = re.search(rf'<Detail[^>]*name="{name}"[^>]*value="([^"]*)"', content)
        if not match:
            # Try alternate order: value before name
            match = re.search(rf'<Detail[^>]*value="([^"]*)"[^>]*name="{name}"', content)
        return match.group(1) if match else None

    def _extract_tag_value(self, content: str, name: str) -> Optional[str]:
        """Extract value from Tag element with given name attribute."""
        match = re.search(rf'<Tag[^>]*name="{name}"[^>]*value="([^"]*)"', content)
        if not match:
            # Try alternate order: value before name
            match = re.search(rf'<Tag[^>]*value="([^"]*)"[^>]*name="{name}"', content)
        return match.group(1) if match else None


class UpiExtractor(BaseExtractor):
    """Extractor for India UPI instant payment messages."""

    MESSAGE_TYPE = "UPI"
    SILVER_TABLE = "stg_upi"

    def __init__(self):
        """Initialize extractor with parsers."""
        super().__init__()
        self.parser = UpiJsonParser()
        self.xml_parser = UpiXmlParser()

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw UPI content."""
        # Parse if string
        if isinstance(raw_content, str):
            parsed = self.parser.parse(raw_content)
        else:
            parsed = raw_content

        msg_id = (parsed.get('transactionId', '') or parsed.get('transactionRefId', '') or
                  parsed.get('headMsgId', '') or parsed.get('txnId', ''))
        return {
            'raw_id': self.generate_raw_id(msg_id),
            'message_type': self.MESSAGE_TYPE,
            'raw_content': json.dumps(raw_content) if isinstance(raw_content, dict) else raw_content,
            'batch_id': batch_id,
        }

    # =========================================================================
    # SILVER EXTRACTION - All 84 standard fields
    # =========================================================================

    def extract_silver(
        self,
        msg_content: Dict[str, Any],
        raw_id: str,
        stg_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        """Extract all Silver layer fields from UPI message.

        Maps all 84 standard data elements to silver columns.
        """
        trunc = self.trunc

        # Parse if needed
        if isinstance(msg_content, str):
            parsed = self.parser.parse(msg_content)
        else:
            parsed = self.parser.parse(msg_content)

        return {
            # System fields
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,
            'message_type': 'UPI',

            # Ack fields (4)
            'ack_api': trunc(parsed.get('ackApi'), 50),
            'ack_err': trunc(parsed.get('ackErr'), 100),
            'ack_req_msg_id': trunc(parsed.get('ackReqMsgId'), 50),
            'ack_ts': parsed.get('ackTs'),

            # Head fields (4)
            'head_msg_id': trunc(parsed.get('headMsgId'), 50),
            'head_org_id': trunc(parsed.get('headOrgId'), 50),
            'head_ts': parsed.get('headTs'),
            'head_ver': trunc(parsed.get('headVer'), 10),

            # Meta fields (2)
            'meta_name': trunc(parsed.get('metaName'), 50),
            'meta_value': trunc(parsed.get('metaValue'), 255),

            # Payee basic fields (5)
            'payee_addr': trunc(parsed.get('payeeAddr'), 100),
            'payee_code': trunc(parsed.get('payeeCode'), 10),
            'payee_name': trunc(parsed.get('payeeName'), 140),
            'payee_seq_num': trunc(parsed.get('payeeSeqNum'), 10),
            'payee_type': trunc(parsed.get('payeeType'), 20),

            # Payee/Ac fields (4)
            'payee_ac_addr_type': trunc(parsed.get('payeeAcAddrType'), 20),
            'payee_ac_acnum': trunc(parsed.get('payeeAcAcnum'), 50),
            'payee_ac_actype': trunc(parsed.get('payeeAcActype'), 20),
            'payee_ac_ifsc': trunc(parsed.get('payeeAcIfsc'), 20),

            # Payee/Device fields (7)
            'payee_device_geocode': trunc(parsed.get('payeeDeviceGeocode'), 50),
            'payee_device_id': trunc(parsed.get('payeeDeviceId'), 100),
            'payee_device_ip': trunc(parsed.get('payeeDeviceIp'), 50),
            'payee_device_location': trunc(parsed.get('payeeDeviceLocation'), 100),
            'payee_device_mobile': trunc(parsed.get('payeeDeviceMobile'), 20),
            'payee_device_os': trunc(parsed.get('payeeDeviceOs'), 50),
            'payee_device_type': trunc(parsed.get('payeeDeviceType'), 20),

            # Payee/Info fields (4)
            'payee_identity_type': trunc(parsed.get('payeeIdentityType'), 20),
            'payee_identity_verified_name': trunc(parsed.get('payeeIdentityVerifiedName'), 100),
            'payee_rating_verified_address': trunc(parsed.get('payeeRatingVerifiedAddress'), 20),
            'payee_rating_whitelisted': trunc(parsed.get('payeeRatingWhitelisted'), 10),

            # Payee/Merchant fields (3)
            'merchant_id': trunc(parsed.get('merchantId'), 50),
            'merchant_sub_id': trunc(parsed.get('merchantSubId'), 50),
            'merchant_term_id': trunc(parsed.get('merchantTermId'), 50),

            # Payer basic fields (5)
            'payer_addr': trunc(parsed.get('payerAddr'), 100),
            'payer_code': trunc(parsed.get('payerCode'), 10),
            'payer_name': trunc(parsed.get('payerName'), 140),
            'payer_seq_num': trunc(parsed.get('payerSeqNum'), 10),
            'payer_type': trunc(parsed.get('payerType'), 20),

            # Payer/Ac fields (4)
            'payer_ac_addr_type': trunc(parsed.get('payerAcAddrType'), 20),
            'payer_ac_acnum': trunc(parsed.get('payerAcAcnum'), 50),
            'payer_ac_actype': trunc(parsed.get('payerAcActype'), 20),
            'payer_ac_ifsc': trunc(parsed.get('payerAcIfsc'), 20),

            # Payer/Amount fields (4)
            'payer_amount_curr': trunc(parsed.get('payerAmountCurr'), 3),
            'payer_amount_value': parsed.get('payerAmountValue'),
            'payer_amount_split_name': trunc(parsed.get('payerAmountSplitName'), 50),
            'payer_amount_split_value': parsed.get('payerAmountSplitValue'),

            # Payer/Creds fields (2)
            'payer_cred_sub_type': trunc(parsed.get('payerCredSubType'), 20),
            'payer_cred_type': trunc(parsed.get('payerCredType'), 20),

            # Payer/Device fields (7)
            'payer_device_geocode': trunc(parsed.get('payerDeviceGeocode'), 50),
            'payer_device_id': trunc(parsed.get('payerDeviceId'), 100),
            'payer_device_ip': trunc(parsed.get('payerDeviceIp'), 50),
            'payer_device_location': trunc(parsed.get('payerDeviceLocation'), 100),
            'payer_device_mobile': trunc(parsed.get('payerDeviceMobile'), 20),
            'payer_device_os': trunc(parsed.get('payerDeviceOs'), 50),
            'payer_device_type': trunc(parsed.get('payerDeviceType'), 20),

            # Payer/Info fields (4)
            'payer_identity_type': trunc(parsed.get('payerIdentityType'), 20),
            'payer_identity_verified_name': trunc(parsed.get('payerIdentityVerifiedName'), 100),
            'payer_rating_verified_address': trunc(parsed.get('payerRatingVerifiedAddress'), 20),
            'payer_rating_whitelisted': trunc(parsed.get('payerRatingWhitelisted'), 10),

            # Psp fields (1)
            'psp_name': trunc(parsed.get('pspName'), 100),

            # Ref fields (4)
            'ref_addr': trunc(parsed.get('refAddr'), 100),
            'ref_seq_num': trunc(parsed.get('refSeqNum'), 10),
            'ref_type': trunc(parsed.get('refType'), 20),
            'ref_value': trunc(parsed.get('refValue'), 255),

            # ReqAuthDetails fields (2)
            'req_auth_api': trunc(parsed.get('reqAuthApi'), 50),
            'req_auth_version': trunc(parsed.get('reqAuthVersion'), 10),

            # Resp fields (4)
            'resp_err_code': trunc(parsed.get('respErrCode'), 10),
            'resp_msg_id': trunc(parsed.get('respMsgId'), 50),
            'resp_req_msg_id': trunc(parsed.get('respReqMsgId'), 50),
            'resp_result': trunc(parsed.get('respResult'), 20),

            # Txn basic fields (9)
            'txn_cust_ref': trunc(parsed.get('txnCustRef'), 50),
            'txn_id': trunc(parsed.get('txnId'), 50),
            'txn_note': trunc(parsed.get('txnNote'), 255),
            'txn_org_resp_code': trunc(parsed.get('txnOrgRespCode'), 10),
            'txn_org_txn_id': trunc(parsed.get('txnOrgTxnId'), 50),
            'txn_ref_id': trunc(parsed.get('txnRefId'), 50),
            'txn_ref_url': trunc(parsed.get('txnRefUrl'), 255),
            'txn_ts': parsed.get('txnTs'),
            'txn_type': trunc(parsed.get('txnType'), 20),

            # Txn/RiskScores fields (3)
            'risk_score_provider': trunc(parsed.get('riskScoreProvider'), 50),
            'risk_score_type': trunc(parsed.get('riskScoreType'), 20),
            'risk_score_value': trunc(parsed.get('riskScoreValue'), 20),

            # Txn/Rules fields (2)
            'rule_name': trunc(parsed.get('ruleName'), 50),
            'rule_value': trunc(parsed.get('ruleValue'), 255),

            # Legacy fields for backward compatibility
            'transaction_id': trunc(parsed.get('transactionId') or parsed.get('headMsgId'), 50),
            'transaction_ref_id': trunc(parsed.get('transactionRefId') or parsed.get('txnId'), 50),
            'creation_date_time': parsed.get('creationDateTime') or parsed.get('headTs'),
            'amount': parsed.get('amount') or parsed.get('payerAmountValue'),
            'currency': parsed.get('currency') or parsed.get('payerAmountCurr') or 'INR',
            'payer_vpa': trunc(parsed.get('payerVpa') or parsed.get('payerAddr'), 100),
            'payee_vpa': trunc(parsed.get('payeeVpa') or parsed.get('payeeAddr'), 100),
            'payer_account': trunc(parsed.get('payerAccount') or parsed.get('payerAcAcnum'), 50),
            'payee_account': trunc(parsed.get('payeeAccount') or parsed.get('payeeAcAcnum'), 50),
            'payer_ifsc': trunc(parsed.get('payerIfsc') or parsed.get('payerAcIfsc'), 20),
            'payee_ifsc': trunc(parsed.get('payeeIfsc') or parsed.get('payeeAcIfsc'), 20),
            'payer_mobile': trunc(parsed.get('payerMobile') or parsed.get('payerDeviceMobile'), 20),
            'payee_mobile': trunc(parsed.get('payeeMobile') or parsed.get('payeeDeviceMobile'), 20),
            'transaction_type': trunc(parsed.get('transactionType') or parsed.get('txnType'), 20),
            'sub_type': trunc(parsed.get('subType'), 20),
            'remittance_info': parsed.get('remittanceInfo') or parsed.get('txnNote'),
            'transaction_status': trunc(parsed.get('transactionStatus'), 20),
            'response_code': trunc(parsed.get('responseCode') or parsed.get('respErrCode'), 10),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT.

        Returns all 84 standard field columns plus system and legacy columns.
        """
        return [
            # System fields
            'stg_id', 'raw_id', '_batch_id', 'message_type',

            # Ack fields (4)
            'ack_api', 'ack_err', 'ack_req_msg_id', 'ack_ts',

            # Head fields (4)
            'head_msg_id', 'head_org_id', 'head_ts', 'head_ver',

            # Meta fields (2)
            'meta_name', 'meta_value',

            # Payee basic fields (5)
            'payee_addr', 'payee_code', 'payee_name', 'payee_seq_num', 'payee_type',

            # Payee/Ac fields (4)
            'payee_ac_addr_type', 'payee_ac_acnum', 'payee_ac_actype', 'payee_ac_ifsc',

            # Payee/Device fields (7)
            'payee_device_geocode', 'payee_device_id', 'payee_device_ip',
            'payee_device_location', 'payee_device_mobile', 'payee_device_os', 'payee_device_type',

            # Payee/Info fields (4)
            'payee_identity_type', 'payee_identity_verified_name',
            'payee_rating_verified_address', 'payee_rating_whitelisted',

            # Payee/Merchant fields (3)
            'merchant_id', 'merchant_sub_id', 'merchant_term_id',

            # Payer basic fields (5)
            'payer_addr', 'payer_code', 'payer_name', 'payer_seq_num', 'payer_type',

            # Payer/Ac fields (4)
            'payer_ac_addr_type', 'payer_ac_acnum', 'payer_ac_actype', 'payer_ac_ifsc',

            # Payer/Amount fields (4)
            'payer_amount_curr', 'payer_amount_value', 'payer_amount_split_name', 'payer_amount_split_value',

            # Payer/Creds fields (2)
            'payer_cred_sub_type', 'payer_cred_type',

            # Payer/Device fields (7)
            'payer_device_geocode', 'payer_device_id', 'payer_device_ip',
            'payer_device_location', 'payer_device_mobile', 'payer_device_os', 'payer_device_type',

            # Payer/Info fields (4)
            'payer_identity_type', 'payer_identity_verified_name',
            'payer_rating_verified_address', 'payer_rating_whitelisted',

            # Psp fields (1)
            'psp_name',

            # Ref fields (4)
            'ref_addr', 'ref_seq_num', 'ref_type', 'ref_value',

            # ReqAuthDetails fields (2)
            'req_auth_api', 'req_auth_version',

            # Resp fields (4)
            'resp_err_code', 'resp_msg_id', 'resp_req_msg_id', 'resp_result',

            # Txn basic fields (9)
            'txn_cust_ref', 'txn_id', 'txn_note', 'txn_org_resp_code', 'txn_org_txn_id',
            'txn_ref_id', 'txn_ref_url', 'txn_ts', 'txn_type',

            # Txn/RiskScores fields (3)
            'risk_score_provider', 'risk_score_type', 'risk_score_value',

            # Txn/Rules fields (2)
            'rule_name', 'rule_value',

            # Legacy fields for backward compatibility
            'transaction_id', 'transaction_ref_id', 'creation_date_time',
            'amount', 'currency',
            'payer_vpa', 'payee_vpa',
            'payer_account', 'payee_account',
            'payer_ifsc', 'payee_ifsc',
            'payer_mobile', 'payee_mobile',
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
        payer_name = silver_data.get('payer_name') or silver_data.get('payerName')
        if payer_name:
            entities.parties.append(PartyData(
                name=payer_name,
                role="DEBTOR",
                party_type='UNKNOWN',
                country='IN',
            ))

        # Payee Party (Creditor)
        payee_name = silver_data.get('payee_name') or silver_data.get('payeeName')
        if payee_name:
            entities.parties.append(PartyData(
                name=payee_name,
                role="CREDITOR",
                party_type='UNKNOWN',
                country='IN',
            ))

        # Payer Account (VPA or Account)
        payer_vpa = silver_data.get('payer_vpa') or silver_data.get('payer_addr') or silver_data.get('payerAddr')
        payer_account = silver_data.get('payer_account') or silver_data.get('payer_ac_acnum') or silver_data.get('payerAcAcnum')
        if payer_vpa or payer_account:
            entities.accounts.append(AccountData(
                account_number=payer_vpa or payer_account,
                role="DEBTOR",
                account_type='CACC',
                currency='INR',
            ))

        # Payee Account (VPA or Account)
        payee_vpa = silver_data.get('payee_vpa') or silver_data.get('payee_addr') or silver_data.get('payeeAddr')
        payee_account = silver_data.get('payee_account') or silver_data.get('payee_ac_acnum') or silver_data.get('payeeAcAcnum')
        if payee_vpa or payee_account:
            entities.accounts.append(AccountData(
                account_number=payee_vpa or payee_account,
                role="CREDITOR",
                account_type='CACC',
                currency='INR',
            ))

        # Payer Bank (by IFSC)
        payer_ifsc = silver_data.get('payer_ifsc') or silver_data.get('payer_ac_ifsc') or silver_data.get('payerAcIfsc')
        if payer_ifsc:
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=payer_ifsc,
                clearing_system='INIFSC',  # India IFSC
                country='IN',
            ))

        # Payee Bank (by IFSC)
        payee_ifsc = silver_data.get('payee_ifsc') or silver_data.get('payee_ac_ifsc') or silver_data.get('payeeAcIfsc')
        if payee_ifsc:
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=payee_ifsc,
                clearing_system='INIFSC',
                country='IN',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('UPI', UpiExtractor())
ExtractorRegistry.register('upi', UpiExtractor())
