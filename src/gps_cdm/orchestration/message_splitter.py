"""
GPS CDM - Message Splitter
==========================

Splits multi-record files/messages into individual payment records.
This is critical for files that contain multiple transactions (e.g., batch files).

Supported formats:
- ISO 20022 XML (pain.001, pacs.008, SEPA, RTP, FedNow, CHAPS, FPS, NPP, MEPS+,
  TARGET2, RTGS_HK, UAEFTS, PromptPay, PayNow, InstaPay, camt.053):
  Multiple CdtTrfTxInf/Ntry elements
- SWIFT MT (MT103, MT202, MT940): Multiple messages separated by {1:...} blocks
- ACH/NACHA: Fixed-width with multiple entry detail records (type 6)
- BACS: UK fixed-width batch payments
- FEDWIRE: Multiple messages separated by ### delimiter
- CHIPS: US large-value tag-delimited format
- SARIE: Saudi Arabia tag-value format
- JSON (PIX, UPI): JSON arrays of transactions
- KFTC/BOJNET/CNAPS: Asian fixed-width formats
"""

import json
import re
import logging
from typing import List, Dict, Any, Iterator, Optional
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


class MessageSplitter:
    """
    Splits multi-record content into individual payment records.

    Each split record contains:
    - content: The individual record content (dict or string)
    - index: Position in original file (0-based)
    - parent_context: Shared context from parent (e.g., GrpHdr for ISO 20022)
    """

    # ISO 20022 message types that use CdtTrfTxInf splitting
    ISO20022_PAYMENT_TYPES = {
        'pain_001', 'pain001', 'pacs_008', 'pacs008',
        'sepa', 'sepa_sct', 'sepa_sdd', 'sepa_inst',
        'rtp', 'fednow',
        'chaps', 'fps', 'npp',
        'meps_plus', 'meps', 'mepsplus',
        'target2', 'rtgs_hk', 'rtgs',
        'uaefts',
        'promptpay', 'paynow', 'instapay',
    }

    # ISO 20022 statement types that use Ntry splitting
    ISO20022_STATEMENT_TYPES = {
        'camt_053', 'camt053', 'camt_052', 'camt052', 'camt_054', 'camt054',
    }

    # SWIFT MT message types
    SWIFT_MT_TYPES = {'mt103', 'mt202', 'mt202cov', 'mt940', 'mt950', 'mt101', 'mt199', 'mt900', 'mt910'}

    # Fixed-width batch formats
    FIXED_WIDTH_TYPES = {
        'ach': '_split_ach_nacha',
        'nacha': '_split_ach_nacha',
        'bacs': '_split_bacs',
        'chips': '_split_chips',
        'kftc': '_split_kftc',
        'bojnet': '_split_bojnet',
        'cnaps': '_split_cnaps',
    }

    # Tag-value formats
    TAG_VALUE_TYPES = {
        'fedwire': '_split_fedwire',
        'sarie': '_split_sarie',
    }

    # JSON array formats
    JSON_ARRAY_TYPES = {'pix', 'upi'}

    @classmethod
    def split(cls, content: str, message_type: str) -> List[Dict[str, Any]]:
        """
        Split content into individual records based on message type.

        Args:
            content: Raw file/message content (string)
            message_type: Message type identifier

        Returns:
            List of {content, index, parent_context} dicts
        """
        msg_type_lower = message_type.lower().replace('.', '_').replace('-', '_')

        # ISO 20022 payment XML formats (CdtTrfTxInf splitting)
        if msg_type_lower in cls.ISO20022_PAYMENT_TYPES:
            return cls._split_iso20022_xml(content, message_type)

        # ISO 20022 statement XML formats (Ntry splitting)
        if msg_type_lower in cls.ISO20022_STATEMENT_TYPES:
            return cls._split_iso20022_statement(content, message_type)

        # SWIFT MT formats
        if msg_type_lower in cls.SWIFT_MT_TYPES:
            return cls._split_swift_mt(content, message_type)

        # Also handle MT types by prefix pattern for flexibility
        if msg_type_lower.startswith('mt') and len(msg_type_lower) >= 5:
            suffix = msg_type_lower[2:].replace('cov', '').replace('stp', '')
            if suffix.isdigit():
                return cls._split_swift_mt(content, message_type)

        # Fixed-width batch formats
        if msg_type_lower in cls.FIXED_WIDTH_TYPES:
            method_name = cls.FIXED_WIDTH_TYPES[msg_type_lower]
            return getattr(cls, method_name)(content, message_type)

        # Tag-value formats
        if msg_type_lower in cls.TAG_VALUE_TYPES:
            method_name = cls.TAG_VALUE_TYPES[msg_type_lower]
            return getattr(cls, method_name)(content, message_type)

        # JSON array formats
        if msg_type_lower in cls.JSON_ARRAY_TYPES:
            return cls._split_json_array(content, message_type)

        # Default: treat as single record
        logger.debug(f"No splitter for {message_type}, treating as single record")
        return [{'content': content, 'index': 0, 'parent_context': {}}]

    @classmethod
    def _split_iso20022_xml(cls, content: str, message_type: str) -> List[Dict[str, Any]]:
        """
        Split ISO 20022 XML into individual transactions.

        ISO 20022 payment initiation messages can contain multiple:
        - PmtInf (Payment Information blocks)
        - CdtTrfTxInf (Credit Transfer Transaction Info) within each PmtInf

        Each CdtTrfTxInf becomes a separate record for processing.
        """
        records = []

        try:
            # Remove BOM and clean
            if content.startswith('\ufeff'):
                content = content[1:]

            # Parse XML
            root = ET.fromstring(content)

            # Remove namespace prefixes for easier querying
            for elem in root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}')[1]
                # Also clean attributes
                elem.attrib = {k.split('}')[1] if '}' in k else k: v for k, v in elem.attrib.items()}

            # Extract Group Header (shared context)
            grp_hdr = root.find('.//GrpHdr')
            if grp_hdr is None:
                grp_hdr = root.find('GrpHdr')
            parent_context = {}

            if grp_hdr is not None:
                parent_context = {
                    'messageId': cls._find_text_simple(grp_hdr, 'MsgId'),
                    'creationDateTime': cls._find_text_simple(grp_hdr, 'CreDtTm'),
                    'numberOfTransactions': cls._find_text_simple(grp_hdr, 'NbOfTxs'),
                    'controlSum': cls._find_text_simple(grp_hdr, 'CtrlSum'),
                }
                # Initiating Party
                initg_pty = grp_hdr.find('InitgPty')
                if initg_pty is not None:
                    parent_context['initiatingParty'] = {
                        'name': cls._find_text_simple(initg_pty, 'Nm'),
                    }

            # Find all Payment Information blocks
            pmt_infs = root.findall('.//PmtInf')

            # Also check for FIToFICstmrCdtTrf structure (pacs.008)
            if not pmt_infs:
                cdtr_trfs = root.findall('.//CdtTrfTxInf')
                if cdtr_trfs:
                    for idx, txn in enumerate(cdtr_trfs):
                        record_content = cls._extract_transaction_content(txn, parent_context, message_type)
                        records.append({
                            'content': record_content,
                            'index': idx,
                            'parent_context': parent_context,
                        })
                    return records if records else [{'content': content, 'index': 0, 'parent_context': {}}]

            # Process each PmtInf block
            for pmt_idx, pmt_inf in enumerate(pmt_infs):
                # Extract PmtInf-level context
                pmt_context = dict(parent_context)
                pmt_context['paymentInfoId'] = cls._find_text_simple(pmt_inf, 'PmtInfId')
                pmt_context['paymentMethod'] = cls._find_text_simple(pmt_inf, 'PmtMtd')
                pmt_context['requestedExecutionDate'] = cls._find_text_simple(pmt_inf, 'Dt') or cls._find_text_simple(pmt_inf, 'ReqdExctnDt')

                # Debtor info (shared across transactions in this PmtInf)
                dbtr = pmt_inf.find('.//Dbtr')
                if dbtr is not None:
                    pmt_context['debtor'] = {
                        'name': cls._find_text_simple(dbtr, 'Nm'),
                        'country': cls._find_text_simple(dbtr, 'Ctry'),
                    }

                dbtr_acct = pmt_inf.find('.//DbtrAcct')
                if dbtr_acct is not None:
                    pmt_context['debtorAccount'] = {
                        'iban': cls._find_text_simple(dbtr_acct, 'IBAN'),
                    }

                dbtr_agt = pmt_inf.find('.//DbtrAgt')
                if dbtr_agt is not None:
                    pmt_context['debtorAgent'] = {
                        'bic': cls._find_text_simple(dbtr_agt, 'BICFI'),
                    }

                # Find all transactions within this PmtInf
                transactions = pmt_inf.findall('.//CdtTrfTxInf')

                for txn_idx, txn in enumerate(transactions):
                    record_content = cls._extract_transaction_content(txn, pmt_context, message_type)
                    global_idx = len(records)
                    records.append({
                        'content': record_content,
                        'index': global_idx,
                        'parent_context': pmt_context,
                    })

            if not records:
                # Fallback to single record
                return [{'content': content, 'index': 0, 'parent_context': parent_context}]

            logger.info(f"Split ISO 20022 {message_type} into {len(records)} transactions")
            return records

        except ET.ParseError as e:
            logger.warning(f"XML parse error for {message_type}: {e}")
            return [{'content': content, 'index': 0, 'parent_context': {}}]
        except Exception as e:
            logger.warning(f"Failed to split ISO 20022 {message_type}: {e}")
            return [{'content': content, 'index': 0, 'parent_context': {}}]

    @classmethod
    def _extract_transaction_content(cls, txn_elem, parent_context: dict, message_type: str) -> dict:
        """Extract transaction content from XML element and merge with parent context."""
        content = dict(parent_context)

        # Payment ID
        pmt_id = txn_elem.find('.//PmtId')
        if pmt_id is not None:
            content['instructionId'] = cls._find_text_simple(pmt_id, 'InstrId')
            content['endToEndId'] = cls._find_text_simple(pmt_id, 'EndToEndId')
            content['uetr'] = cls._find_text_simple(pmt_id, 'UETR')
            content['paymentId'] = cls._find_text_simple(pmt_id, 'TxId')

        # Amount
        amt = txn_elem.find('.//Amt')
        if amt is not None:
            instd_amt = amt.find('.//InstdAmt')
            if instd_amt is not None:
                content['instructedAmount'] = instd_amt.text
                content['instructedCurrency'] = instd_amt.get('Ccy')

        # Interbank settlement amount (for pacs.008)
        intrbnk_amt = txn_elem.find('.//IntrBkSttlmAmt')
        if intrbnk_amt is not None:
            content['interbankSettlementAmount'] = intrbnk_amt.text
            content['interbankSettlementCurrency'] = intrbnk_amt.get('Ccy')
            if 'instructedAmount' not in content:
                content['instructedAmount'] = intrbnk_amt.text
                content['instructedCurrency'] = intrbnk_amt.get('Ccy')

        # Charge Bearer
        content['chargeBearer'] = cls._find_text_simple(txn_elem, 'ChrgBr')

        # Debtor (Payer) - IMPORTANT for FPS, CHAPS, and UK payments
        dbtr = txn_elem.find('.//Dbtr')
        if dbtr is not None:
            debtor_data = {
                'name': cls._find_text_simple(dbtr, 'Nm'),
                'country': cls._find_text_simple(dbtr, 'Ctry'),
            }
            # Organization ID - extract LEI, AnyBIC, and Other ID
            org_id = dbtr.find('.//Id/OrgId')
            if org_id is not None:
                debtor_data['idType'] = 'ORG'
                debtor_data['lei'] = cls._find_text_simple(org_id, 'LEI')
                debtor_data['anyBic'] = cls._find_text_simple(org_id, 'AnyBIC')
                debtor_data['otherId'] = cls._find_text_simple(org_id, 'Othr/Id')
                debtor_data['otherIdScheme'] = cls._find_text_simple(org_id, 'Othr/SchmeNm/Cd')
                debtor_data['id'] = debtor_data['lei'] or debtor_data['anyBic'] or debtor_data['otherId']
            # Private ID - for individuals
            prvt_id = dbtr.find('.//Id/PrvtId')
            if prvt_id is not None:
                debtor_data['idType'] = 'PRVT'
                debtor_data['otherId'] = cls._find_text_simple(prvt_id, 'Othr/Id')
                debtor_data['otherIdScheme'] = cls._find_text_simple(prvt_id, 'Othr/SchmeNm/Cd')
                debtor_data['id'] = debtor_data['otherId']
            # Address fields
            pstl_adr = dbtr.find('.//PstlAdr')
            if pstl_adr is not None:
                debtor_data['streetName'] = cls._find_text_simple(pstl_adr, 'StrtNm')
                debtor_data['buildingNumber'] = cls._find_text_simple(pstl_adr, 'BldgNb')
                debtor_data['postalCode'] = cls._find_text_simple(pstl_adr, 'PstCd')
                debtor_data['townName'] = cls._find_text_simple(pstl_adr, 'TwnNm')
                debtor_data['countrySubDivision'] = cls._find_text_simple(pstl_adr, 'CtrySubDvsn')
                debtor_data['country'] = cls._find_text_simple(pstl_adr, 'Ctry') or debtor_data.get('country')
                content['payerAddress'] = cls._find_text_simple(pstl_adr, 'AdrLine')
            content['debtor'] = debtor_data
            # Also set flat fields for compatibility
            content['payerName'] = debtor_data.get('name')
            content['debtorName'] = debtor_data.get('name')

        # Debtor Account
        dbtr_acct = txn_elem.find('.//DbtrAcct')
        if dbtr_acct is not None:
            iban = cls._find_text_simple(dbtr_acct, 'IBAN')
            # UK Sort Code + Account Number format (Othr/Id) - also used by RTP
            othr_id = dbtr_acct.find('.//Othr/Id')
            account_number = othr_id.text if othr_id is not None else None
            content['debtorAccount'] = {
                'iban': iban,
                'accountNumber': account_number or iban,  # RTP uses accountNumber
            }
            if account_number:
                content['payerAccount'] = account_number
                content['debtorAccountNumber'] = account_number

        # Debtor Agent (Payer's Bank)
        dbtr_agt = txn_elem.find('.//DbtrAgt')
        if dbtr_agt is not None:
            fin_instn_id = dbtr_agt.find('.//FinInstnId')
            bic = cls._find_text_simple(dbtr_agt, 'BICFI') or (cls._find_text_simple(fin_instn_id, 'BICFI') if fin_instn_id is not None else None)
            lei = cls._find_text_simple(fin_instn_id, 'LEI') if fin_instn_id is not None else None
            name = cls._find_text_simple(fin_instn_id, 'Nm') if fin_instn_id is not None else None
            # UK Sort Code / RTP Member ID (ClrSysMmbId/MmbId)
            member_id_elem = dbtr_agt.find('.//ClrSysMmbId/MmbId')
            member_id = member_id_elem.text if member_id_elem is not None else None
            # Clearing system code
            clr_sys_code = cls._find_text_simple(dbtr_agt, 'ClrSysMmbId/ClrSysId/Cd')
            content['debtorAgent'] = {
                'bic': bic,
                'lei': lei,
                'name': name,
                'memberId': member_id,  # RTP uses memberId
                'clearingSystemCode': clr_sys_code,
                'clearingSystemMemberId': member_id,
            }
            if member_id:
                content['payerSortCode'] = member_id
                content['debtorSortCode'] = member_id

        # Creditor (Payee)
        cdtr = txn_elem.find('.//Cdtr')
        if cdtr is not None:
            creditor_data = {
                'name': cls._find_text_simple(cdtr, 'Nm'),
                'country': cls._find_text_simple(cdtr, 'Ctry'),
            }
            # Organization ID - extract LEI, AnyBIC, and Other ID
            org_id = cdtr.find('.//Id/OrgId')
            if org_id is not None:
                creditor_data['idType'] = 'ORG'
                creditor_data['lei'] = cls._find_text_simple(org_id, 'LEI')
                creditor_data['anyBic'] = cls._find_text_simple(org_id, 'AnyBIC')
                creditor_data['otherId'] = cls._find_text_simple(org_id, 'Othr/Id')
                creditor_data['otherIdScheme'] = cls._find_text_simple(org_id, 'Othr/SchmeNm/Cd')
                creditor_data['id'] = creditor_data['lei'] or creditor_data['anyBic'] or creditor_data['otherId']
            # Private ID - for individuals
            prvt_id = cdtr.find('.//Id/PrvtId')
            if prvt_id is not None:
                creditor_data['idType'] = 'PRVT'
                creditor_data['otherId'] = cls._find_text_simple(prvt_id, 'Othr/Id')
                creditor_data['otherIdScheme'] = cls._find_text_simple(prvt_id, 'Othr/SchmeNm/Cd')
                creditor_data['id'] = creditor_data['otherId']
            # Address fields
            pstl_adr = cdtr.find('.//PstlAdr')
            if pstl_adr is not None:
                creditor_data['streetName'] = cls._find_text_simple(pstl_adr, 'StrtNm')
                creditor_data['buildingNumber'] = cls._find_text_simple(pstl_adr, 'BldgNb')
                creditor_data['postalCode'] = cls._find_text_simple(pstl_adr, 'PstCd')
                creditor_data['townName'] = cls._find_text_simple(pstl_adr, 'TwnNm')
                creditor_data['countrySubDivision'] = cls._find_text_simple(pstl_adr, 'CtrySubDvsn')
                creditor_data['country'] = cls._find_text_simple(pstl_adr, 'Ctry') or creditor_data.get('country')
                content['payeeAddress'] = cls._find_text_simple(pstl_adr, 'AdrLine')
            content['creditor'] = creditor_data
            # Also set flat fields for compatibility
            content['payeeName'] = creditor_data.get('name')
            content['creditorName'] = creditor_data.get('name')

        # Creditor Account
        cdtr_acct = txn_elem.find('.//CdtrAcct')
        if cdtr_acct is not None:
            iban = cls._find_text_simple(cdtr_acct, 'IBAN')
            # UK Sort Code + Account Number format (Othr/Id) - also used by RTP
            othr_id = cdtr_acct.find('.//Othr/Id')
            account_number = othr_id.text if othr_id is not None else None
            content['creditorAccount'] = {
                'iban': iban,
                'accountNumber': account_number or iban,  # RTP uses accountNumber
            }
            if account_number:
                content['payeeAccount'] = account_number
                content['creditorAccountNumber'] = account_number

        # Creditor Agent (Payee's Bank)
        cdtr_agt = txn_elem.find('.//CdtrAgt')
        if cdtr_agt is not None:
            fin_instn_id = cdtr_agt.find('.//FinInstnId')
            bic = cls._find_text_simple(cdtr_agt, 'BICFI') or (cls._find_text_simple(fin_instn_id, 'BICFI') if fin_instn_id is not None else None)
            lei = cls._find_text_simple(fin_instn_id, 'LEI') if fin_instn_id is not None else None
            name = cls._find_text_simple(fin_instn_id, 'Nm') if fin_instn_id is not None else None
            # UK Sort Code / RTP Member ID (ClrSysMmbId/MmbId)
            member_id_elem = cdtr_agt.find('.//ClrSysMmbId/MmbId')
            member_id = member_id_elem.text if member_id_elem is not None else None
            # Clearing system code
            clr_sys_code = cls._find_text_simple(cdtr_agt, 'ClrSysMmbId/ClrSysId/Cd')
            content['creditorAgent'] = {
                'bic': bic,
                'lei': lei,
                'name': name,
                'memberId': member_id,  # RTP uses memberId
                'clearingSystemCode': clr_sys_code,
                'clearingSystemMemberId': member_id,
            }
            if member_id:
                content['payeeSortCode'] = member_id
                content['creditorSortCode'] = member_id

        # Purpose Code
        purp = txn_elem.find('.//Purp')
        if purp is not None:
            content['purposeCode'] = cls._find_text_simple(purp, 'Cd')

        # Remittance Info
        rmt_inf = txn_elem.find('.//RmtInf')
        if rmt_inf is not None:
            unstructured = cls._find_text_simple(rmt_inf, 'Ustrd')
            content['remittanceInfo'] = unstructured  # Flat field for compatibility
            content['remittanceInformation'] = {'unstructured': unstructured}  # RTP uses nested structure
            # Structured reference
            strd = rmt_inf.find('.//Strd/CdtrRefInf/Ref')
            if strd is not None and strd.text:
                content['paymentReference'] = strd.text

        return content

    @classmethod
    def _split_swift_mt(cls, content: str, message_type: str) -> List[Dict[str, Any]]:
        """
        Split SWIFT MT messages by {1:...} block headers.

        SWIFT MT messages start with {1:F01...} and can be concatenated
        in a single file.
        """
        records = []

        # Split by SWIFT block 1 pattern
        pattern = r'(\{1:[^\}]+\})'
        parts = re.split(pattern, content)

        current_msg = ""
        idx = 0

        for part in parts:
            if part.startswith('{1:'):
                # If we have a previous message, save it
                if current_msg.strip():
                    records.append({
                        'content': current_msg.strip(),
                        'index': idx,
                        'parent_context': {},
                    })
                    idx += 1
                current_msg = part
            else:
                current_msg += part

        # Don't forget the last message
        if current_msg.strip():
            records.append({
                'content': current_msg.strip(),
                'index': idx,
                'parent_context': {},
            })

        if not records:
            return [{'content': content, 'index': 0, 'parent_context': {}}]

        logger.info(f"Split SWIFT MT {message_type} into {len(records)} messages")
        return records

    @classmethod
    def _split_ach_nacha(cls, content: str, message_type: str) -> List[Dict[str, Any]]:
        """
        Split ACH/NACHA files into individual entry detail records (type 6).

        NACHA format:
        - Record type 1: File Header
        - Record type 5: Batch Header
        - Record type 6: Entry Detail (one per transaction)
        - Record type 7: Addenda (optional, linked to entry detail)
        - Record type 8: Batch Control
        - Record type 9: File Control

        Each entry detail (type 6) with its addenda becomes a separate record,
        but we include the file/batch headers as context.
        """
        records = []
        lines = content.strip().split('\n')

        file_header = None
        batch_header = None
        current_entry = None
        current_addenda = []

        for line in lines:
            # Pad to 94 chars
            line = line.ljust(94)
            record_type = line[0] if line else ''

            if record_type == '1':
                file_header = line
            elif record_type == '5':
                batch_header = line
            elif record_type == '6':
                # Save previous entry if exists
                if current_entry:
                    records.append({
                        'content': cls._build_ach_record(file_header, batch_header, current_entry, current_addenda),
                        'index': len(records),
                        'parent_context': {
                            'file_header': file_header,
                            'batch_header': batch_header,
                        },
                    })
                current_entry = line
                current_addenda = []
            elif record_type == '7':
                current_addenda.append(line)
            elif record_type == '8':
                # Save the last entry
                if current_entry:
                    records.append({
                        'content': cls._build_ach_record(file_header, batch_header, current_entry, current_addenda),
                        'index': len(records),
                        'parent_context': {
                            'file_header': file_header,
                            'batch_header': batch_header,
                        },
                    })
                    current_entry = None
                    current_addenda = []

        # Handle case where file doesn't have batch control
        if current_entry:
            records.append({
                'content': cls._build_ach_record(file_header, batch_header, current_entry, current_addenda),
                'index': len(records),
                'parent_context': {
                    'file_header': file_header,
                    'batch_header': batch_header,
                },
            })

        if not records:
            return [{'content': content, 'index': 0, 'parent_context': {}}]

        logger.info(f"Split ACH/NACHA into {len(records)} entry detail records")
        return records

    @classmethod
    def _build_ach_record(cls, file_header: str, batch_header: str, entry: str, addenda: List[str]) -> str:
        """Build a complete ACH record from components."""
        lines = []
        if file_header:
            lines.append(file_header)
        if batch_header:
            lines.append(batch_header)
        lines.append(entry)
        lines.extend(addenda)
        return '\n'.join(lines)

    @classmethod
    def _split_fedwire(cls, content: str, message_type: str) -> List[Dict[str, Any]]:
        """
        Split FEDWIRE messages by ### delimiter or multiple {1500} blocks.
        """
        records = []

        # Try splitting by ### delimiter first
        if '###' in content:
            parts = content.split('###')
            for idx, part in enumerate(parts):
                part = part.strip()
                if part:
                    records.append({
                        'content': part,
                        'index': idx,
                        'parent_context': {},
                    })
        else:
            # Try splitting by {1500} tag (start of FEDWIRE message)
            pattern = r'(\{1500\})'
            parts = re.split(pattern, content)

            current_msg = ""
            idx = 0

            for part in parts:
                if part == '{1500}':
                    if current_msg.strip():
                        records.append({
                            'content': current_msg.strip(),
                            'index': idx,
                            'parent_context': {},
                        })
                        idx += 1
                    current_msg = part
                else:
                    current_msg += part

            if current_msg.strip():
                records.append({
                    'content': current_msg.strip(),
                    'index': idx,
                    'parent_context': {},
                })

        if not records:
            return [{'content': content, 'index': 0, 'parent_context': {}}]

        logger.info(f"Split FEDWIRE into {len(records)} messages")
        return records

    @classmethod
    def _split_iso20022_statement(cls, content: str, message_type: str) -> List[Dict[str, Any]]:
        """
        Split ISO 20022 statement messages (camt.053, camt.054) by Ntry elements.

        Unlike payment messages, statement messages are typically processed as a
        whole statement, not individual entries. The extractor expects the full
        XML content to properly extract statement-level fields (balances, account info).

        For camt.053/camt.054, we return the full XML content and let the extractor
        parse it properly.
        """
        # Statement messages should be processed as a complete unit
        # The Camt053Extractor will parse the full XML to extract:
        # - Statement header (Id, MsgId, CreDtTm)
        # - Account information (IBAN, Owner, Servicer)
        # - Balance information (Opening/Closing balances)
        # - Entry summary
        logger.debug(f"Processing {message_type} statement as complete unit")
        return [{'content': content, 'index': 0, 'parent_context': {}}]

    @classmethod
    def _split_bacs(cls, content: str, message_type: str) -> List[Dict[str, Any]]:
        """
        Split UK BACS files into individual payment records.
        BACS uses fixed-width 100-character records.

        Record types:
        - VOL1: Volume header
        - HDR1/HDR2: File headers
        - UHL1: User header
        - Record type 1-3: Payment records
        - UTL1: User trailer
        - EOF1/EOF2: File trailers
        """
        records = []
        lines = content.strip().split('\n')

        header_context = {}

        for line in lines:
            line = line.ljust(100)

            # Extract header info from UHL1 record
            # UHL1 format: UHL1 DDDDDD SUNNNNN SSSSS....
            # Positions: 1-4: UHL1, 5-10: Processing date (space + YYMMDD), 11-16: SU Number, 17+: SU Name
            if line.startswith('UHL1'):
                # Parse processing date (YYMMDD format)
                raw_date = line[5:11].strip()
                if len(raw_date) == 6:
                    try:
                        year = int(raw_date[:2])
                        month = int(raw_date[2:4])
                        day = int(raw_date[4:6])
                        if 1 <= month <= 12 and 1 <= day <= 31:
                            full_year = 2000 + year if year < 50 else 1900 + year
                            header_context['processingDate'] = f"{full_year}-{month:02d}-{day:02d}"
                    except ValueError:
                        pass
                # Service user number and name - use camelCase to match parser output
                header_context['serviceUserNumber'] = line[11:17].strip()
                header_context['serviceUserName'] = line[17:].strip()[:18]

            # Payment records (typically start with a numeric record type indicator)
            # Standard BACS payment record format
            if len(line) >= 80 and line[0:2].isdigit():
                record_type = line[0:2]
                if record_type in ('01', '17', '18', '19', '99'):  # Standard BACS record types
                    records.append({
                        'content': line.strip(),
                        'index': len(records),
                        'parent_context': header_context,
                    })

        if not records:
            return [{'content': content, 'index': 0, 'parent_context': {}}]

        logger.info(f"Split BACS into {len(records)} payment records")
        return records

    @classmethod
    def _split_chips(cls, content: str, message_type: str) -> List[Dict[str, Any]]:
        """
        Split CHIPS (Clearing House Interbank Payments System) messages.
        CHIPS uses a tag-delimited format with messages separated by end-of-message markers.
        """
        records = []

        # CHIPS messages are typically separated by specific delimiters
        # Common patterns: {MSG} blocks or newline-separated with specific headers
        if '{MSG}' in content or '{1:' in content:
            # Similar to SWIFT structure
            pattern = r'(\{MSG\}|\{1:[^\}]+\})'
            parts = re.split(pattern, content)

            current_msg = ""
            idx = 0

            for part in parts:
                if part.startswith('{MSG}') or part.startswith('{1:'):
                    if current_msg.strip():
                        records.append({
                            'content': current_msg.strip(),
                            'index': idx,
                            'parent_context': {},
                        })
                        idx += 1
                    current_msg = part
                else:
                    current_msg += part

            if current_msg.strip():
                records.append({
                    'content': current_msg.strip(),
                    'index': idx,
                    'parent_context': {},
                })
        else:
            # Fallback: split by double newlines or specific CHIPS markers
            parts = re.split(r'\n{2,}|\r\n{2,}', content)
            for idx, part in enumerate(parts):
                part = part.strip()
                if part:
                    records.append({
                        'content': part,
                        'index': idx,
                        'parent_context': {},
                    })

        if not records:
            return [{'content': content, 'index': 0, 'parent_context': {}}]

        logger.info(f"Split CHIPS into {len(records)} messages")
        return records

    @classmethod
    def _split_sarie(cls, content: str, message_type: str) -> List[Dict[str, Any]]:
        """
        Split SARIE (Saudi Arabia RTGS) messages.
        Similar to FEDWIRE with tag-value format.
        """
        records = []

        # SARIE uses similar delimiters to FEDWIRE
        if '###' in content:
            parts = content.split('###')
            for idx, part in enumerate(parts):
                part = part.strip()
                if part:
                    records.append({
                        'content': part,
                        'index': idx,
                        'parent_context': {},
                    })
        elif '{1500}' in content or '{1100}' in content:
            # Tag-based splitting
            pattern = r'(\{1[0-5]00\})'
            parts = re.split(pattern, content)

            current_msg = ""
            idx = 0

            for part in parts:
                if re.match(r'\{1[0-5]00\}', part):
                    if current_msg.strip():
                        records.append({
                            'content': current_msg.strip(),
                            'index': idx,
                            'parent_context': {},
                        })
                        idx += 1
                    current_msg = part
                else:
                    current_msg += part

            if current_msg.strip():
                records.append({
                    'content': current_msg.strip(),
                    'index': idx,
                    'parent_context': {},
                })
        else:
            return [{'content': content, 'index': 0, 'parent_context': {}}]

        if not records:
            return [{'content': content, 'index': 0, 'parent_context': {}}]

        logger.info(f"Split SARIE into {len(records)} messages")
        return records

    @classmethod
    def _split_kftc(cls, content: str, message_type: str) -> List[Dict[str, Any]]:
        """
        Split KFTC (Korea Financial Telecommunications & Clearings) messages.
        Korean fixed-width format with specific record structures.
        """
        records = []
        lines = content.strip().split('\n')

        header = None
        for line in lines:
            # KFTC records are typically 200+ characters
            if len(line) < 50:
                continue

            # First record is usually header
            if header is None and line[0:2] == '01':
                header = line
                continue

            # Transaction records typically start with '02' or '03'
            if line[0:2] in ('02', '03', '10', '20'):
                records.append({
                    'content': line.strip(),
                    'index': len(records),
                    'parent_context': {'header': header} if header else {},
                })

        if not records:
            return [{'content': content, 'index': 0, 'parent_context': {}}]

        logger.info(f"Split KFTC into {len(records)} transaction records")
        return records

    @classmethod
    def _split_bojnet(cls, content: str, message_type: str) -> List[Dict[str, Any]]:
        """
        Split BOJ-NET (Bank of Japan Financial Network) messages.
        Japanese fixed-width format.
        """
        records = []
        lines = content.strip().split('\n')

        header = None
        for line in lines:
            if len(line) < 50:
                continue

            # Header record
            if header is None and line[0:2] in ('00', '01', 'HD'):
                header = line
                continue

            # Transaction records
            if line[0:2] in ('10', '20', '30', 'TX', 'TR'):
                records.append({
                    'content': line.strip(),
                    'index': len(records),
                    'parent_context': {'header': header} if header else {},
                })

        if not records:
            return [{'content': content, 'index': 0, 'parent_context': {}}]

        logger.info(f"Split BOJ-NET into {len(records)} transaction records")
        return records

    @classmethod
    def _split_cnaps(cls, content: str, message_type: str) -> List[Dict[str, Any]]:
        """
        Split CNAPS (China National Advanced Payment System) messages.
        Chinese fixed-width format.
        """
        records = []
        lines = content.strip().split('\n')

        header = None
        for line in lines:
            if len(line) < 50:
                continue

            # Header typically starts with specific markers
            if header is None and (line[0:3] in ('HDR', '000', '001') or line[0:2] == '00'):
                header = line
                continue

            # Transaction records
            if line[0:3] in ('TXN', '100', '200') or line[0:2] in ('10', '20', '30'):
                records.append({
                    'content': line.strip(),
                    'index': len(records),
                    'parent_context': {'header': header} if header else {},
                })

        if not records:
            return [{'content': content, 'index': 0, 'parent_context': {}}]

        logger.info(f"Split CNAPS into {len(records)} transaction records")
        return records

    @classmethod
    def _split_json_array(cls, content: str, message_type: str) -> List[Dict[str, Any]]:
        """
        Split JSON array formats (PIX, UPI).
        Handles both JSON arrays and newline-delimited JSON.
        """
        records = []

        try:
            # Try parsing as JSON
            data = json.loads(content)

            if isinstance(data, list):
                # JSON array of transactions
                for idx, item in enumerate(data):
                    records.append({
                        'content': item if isinstance(item, dict) else {'data': item},
                        'index': idx,
                        'parent_context': {},
                    })
            elif isinstance(data, dict):
                # Single transaction or wrapper with transactions array
                if 'transactions' in data:
                    parent_context = {k: v for k, v in data.items() if k != 'transactions'}
                    for idx, txn in enumerate(data['transactions']):
                        records.append({
                            'content': txn,
                            'index': idx,
                            'parent_context': parent_context,
                        })
                elif 'payments' in data:
                    parent_context = {k: v for k, v in data.items() if k != 'payments'}
                    for idx, txn in enumerate(data['payments']):
                        records.append({
                            'content': txn,
                            'index': idx,
                            'parent_context': parent_context,
                        })
                else:
                    # Single transaction
                    return [{'content': data, 'index': 0, 'parent_context': {}}]

        except json.JSONDecodeError:
            # Try newline-delimited JSON (NDJSON)
            lines = content.strip().split('\n')
            for idx, line in enumerate(lines):
                line = line.strip()
                if line:
                    try:
                        item = json.loads(line)
                        records.append({
                            'content': item,
                            'index': idx,
                            'parent_context': {},
                        })
                    except json.JSONDecodeError:
                        continue

        if not records:
            return [{'content': content, 'index': 0, 'parent_context': {}}]

        logger.info(f"Split {message_type} JSON into {len(records)} transactions")
        return records

    @staticmethod
    def _find_text(elem, path: str) -> Optional[str]:
        """Find text in element using XPath with descendant search."""
        found = elem.find(f'.//{path}')
        return found.text if found is not None else None

    @staticmethod
    def _find_text_simple(elem, tag: str) -> Optional[str]:
        """Find text in element using simple tag name search (no XPath)."""
        # First try direct child
        found = elem.find(tag)
        if found is not None:
            return found.text
        # Then try recursive search through children
        for child in elem.iter():
            if child.tag == tag:
                return child.text
        return None


def split_message(content: str, message_type: str) -> List[Dict[str, Any]]:
    """
    Convenience function to split a message into individual records.

    Args:
        content: Raw file/message content
        message_type: Message type identifier

    Returns:
        List of individual records with content, index, and parent_context
    """
    return MessageSplitter.split(content, message_type)
