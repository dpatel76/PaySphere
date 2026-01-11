"""
GPS CDM - Message Splitter
==========================

Splits multi-record files/messages into individual payment records.
This module is responsible for SPLITTING ONLY - NO EXTRACTION.

Extraction is handled by format-specific parsers in the message_formats package.

Each split record contains:
- content: Raw record content (XML string, text, or dict for JSON)
- index: Position in original file (0-based)
- parent_context: Minimal shared context (IDs only, not extracted data)

Supported formats:
- ISO 20022 XML (pain.001, pacs.008, SEPA, RTP, FedNow, CHAPS, FPS, NPP, MEPS+,
  TARGET2, RTGS_HK, UAEFTS, PromptPay, PayNow, InstaPay, camt.053):
  Multiple CdtTrfTxInf/Ntry elements - returns RAW XML
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

    IMPORTANT: This class handles SPLITTING only - NO extraction logic.
    Parsers in message_formats package handle all field extraction.

    Each split record contains:
    - content: Raw record content (XML string, text, or dict for JSON)
    - index: Position in original file (0-based)
    - parent_context: Minimal shared context (message IDs only, NOT extracted party/account data)
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

        IMPORTANT: Returns RAW XML content - NO extraction.
        Parsers in message_formats package handle all field extraction.

        Each record's 'content' field contains:
        - The complete XML for a single transaction (with parent context embedded)
        - Parent context contains only minimal IDs (messageId, paymentInfoId) for tracing

        ISO 20022 payment initiation messages can contain multiple:
        - PmtInf (Payment Information blocks)
        - CdtTrfTxInf (Credit Transfer Transaction Info) within each PmtInf
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

            # Extract minimal Group Header context (IDs only - NO extracted party/account data)
            grp_hdr = root.find('.//GrpHdr')
            if grp_hdr is None:
                grp_hdr = root.find('GrpHdr')

            # Minimal parent context - IDs only for tracing
            parent_context = {}
            grp_hdr_xml = None
            if grp_hdr is not None:
                parent_context['GrpHdr.MsgId'] = cls._find_text_simple(grp_hdr, 'MsgId')
                parent_context['GrpHdr.CreDtTm'] = cls._find_text_simple(grp_hdr, 'CreDtTm')
                grp_hdr_xml = ET.tostring(grp_hdr, encoding='unicode')

            # Find all Payment Information blocks
            pmt_infs = root.findall('.//PmtInf')

            # Also check for FIToFICstmrCdtTrf structure (pacs.008)
            if not pmt_infs:
                cdtr_trfs = root.findall('.//CdtTrfTxInf')
                if cdtr_trfs:
                    for idx, txn in enumerate(cdtr_trfs):
                        # Return complete ISO 20022 document for this transaction
                        txn_xml = ET.tostring(txn, encoding='unicode')
                        record_xml = cls._build_transaction_xml(grp_hdr_xml, None, txn_xml, message_type)
                        records.append({
                            'content': record_xml,
                            'index': idx,
                            'parent_context': parent_context,
                        })
                    return records if records else [{'content': content, 'index': 0, 'parent_context': {}}]

            # Process each PmtInf block
            for pmt_idx, pmt_inf in enumerate(pmt_infs):
                # Minimal PmtInf context - IDs only
                pmt_context = dict(parent_context)
                pmt_context['PmtInf.PmtInfId'] = cls._find_text_simple(pmt_inf, 'PmtInfId')

                # Serialize PmtInf without its CdtTrfTxInf children (for embedding)
                pmt_inf_copy = cls._copy_element_without_children(pmt_inf, 'CdtTrfTxInf')
                pmt_inf_xml = ET.tostring(pmt_inf_copy, encoding='unicode') if pmt_inf_copy is not None else None

                # Find all transactions within this PmtInf
                transactions = pmt_inf.findall('.//CdtTrfTxInf')

                for txn_idx, txn in enumerate(transactions):
                    # Return complete ISO 20022 document for this transaction
                    txn_xml = ET.tostring(txn, encoding='unicode')
                    record_xml = cls._build_transaction_xml(grp_hdr_xml, pmt_inf_xml, txn_xml, message_type)
                    global_idx = len(records)
                    records.append({
                        'content': record_xml,
                        'index': global_idx,
                        'parent_context': pmt_context,
                    })

            if not records:
                # Fallback to single record (full XML)
                return [{'content': content, 'index': 0, 'parent_context': parent_context}]

            logger.info(f"Split ISO 20022 {message_type} into {len(records)} transactions (raw XML)")
            return records

        except ET.ParseError as e:
            logger.warning(f"XML parse error for {message_type}: {e}")
            return [{'content': content, 'index': 0, 'parent_context': {}}]
        except Exception as e:
            logger.warning(f"Failed to split ISO 20022 {message_type}: {e}")
            return [{'content': content, 'index': 0, 'parent_context': {}}]

    @classmethod
    def _build_transaction_xml(cls, grp_hdr_xml: Optional[str], pmt_inf_xml: Optional[str],
                                txn_xml: str, message_type: str = '') -> str:
        """
        Build a complete, valid ISO 20022 document for a single transaction.

        Instead of using a proprietary wrapper format, we rebuild a valid
        pain.001/pacs.008 document that contains just the single transaction.
        This allows parsers to process split transactions the same way they
        process regular full documents.

        For pain.001: <Document><CstmrCdtTrfInitn><GrpHdr>...</GrpHdr><PmtInf>...<CdtTrfTxInf>...</CdtTrfTxInf></PmtInf></CstmrCdtTrfInitn></Document>
        For pacs.008: <Document><FIToFICstmrCdtTrf><GrpHdr>...</GrpHdr><CdtTrfTxInf>...</CdtTrfTxInf></FIToFICstmrCdtTrf></Document>
        """
        msg_type_lower = message_type.lower().replace('.', '_').replace('-', '_')

        # Determine document structure based on message type
        if msg_type_lower in ('pain_001', 'pain001'):
            # pain.001 structure: Document > CstmrCdtTrfInitn > GrpHdr + PmtInf > CdtTrfTxInf
            if pmt_inf_xml and txn_xml:
                # Insert transaction into PmtInf (before closing tag)
                pmt_inf_with_txn = pmt_inf_xml.rstrip()
                if pmt_inf_with_txn.endswith('</PmtInf>'):
                    pmt_inf_with_txn = pmt_inf_with_txn[:-9] + txn_xml + '</PmtInf>'
                else:
                    pmt_inf_with_txn = pmt_inf_xml + txn_xml

                parts = ['<?xml version="1.0" encoding="UTF-8"?>']
                parts.append('<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">')
                parts.append('<CstmrCdtTrfInitn>')
                if grp_hdr_xml:
                    parts.append(grp_hdr_xml)
                parts.append(pmt_inf_with_txn)
                parts.append('</CstmrCdtTrfInitn>')
                parts.append('</Document>')
                return ''.join(parts)
            else:
                # No PmtInf context - wrap transaction directly
                parts = ['<?xml version="1.0" encoding="UTF-8"?>']
                parts.append('<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">')
                parts.append('<CstmrCdtTrfInitn>')
                if grp_hdr_xml:
                    parts.append(grp_hdr_xml)
                parts.append('<PmtInf>')
                parts.append(txn_xml)
                parts.append('</PmtInf>')
                parts.append('</CstmrCdtTrfInitn>')
                parts.append('</Document>')
                return ''.join(parts)

        elif msg_type_lower in ('pacs_008', 'pacs008'):
            # pacs.008 structure: Document > FIToFICstmrCdtTrf > GrpHdr + CdtTrfTxInf
            parts = ['<?xml version="1.0" encoding="UTF-8"?>']
            parts.append('<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">')
            parts.append('<FIToFICstmrCdtTrf>')
            if grp_hdr_xml:
                parts.append(grp_hdr_xml)
            parts.append(txn_xml)
            parts.append('</FIToFICstmrCdtTrf>')
            parts.append('</Document>')
            return ''.join(parts)

        else:
            # Default: Return a generic wrapper that maintains valid XML structure
            # This is a fallback for other ISO 20022 types
            parts = ['<?xml version="1.0" encoding="UTF-8"?>']
            parts.append('<Document>')
            if grp_hdr_xml:
                parts.append(grp_hdr_xml)
            if pmt_inf_xml:
                # Insert transaction into PmtInf
                pmt_inf_with_txn = pmt_inf_xml.rstrip()
                if pmt_inf_with_txn.endswith('</PmtInf>'):
                    pmt_inf_with_txn = pmt_inf_with_txn[:-9] + txn_xml + '</PmtInf>'
                else:
                    pmt_inf_with_txn = pmt_inf_xml + txn_xml
                parts.append(pmt_inf_with_txn)
            else:
                parts.append(txn_xml)
            parts.append('</Document>')
            return ''.join(parts)

    @classmethod
    def _copy_element_without_children(cls, elem: ET.Element, exclude_tag: str) -> Optional[ET.Element]:
        """
        Create a shallow copy of an element excluding specific child elements.
        Used to copy PmtInf without CdtTrfTxInf children.
        """
        if elem is None:
            return None

        # Create new element with same tag and attributes
        new_elem = ET.Element(elem.tag, elem.attrib)
        new_elem.text = elem.text
        new_elem.tail = elem.tail

        # Copy children except excluded tag
        for child in elem:
            if child.tag != exclude_tag:
                new_elem.append(child)

        return new_elem

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
        including the file/batch headers AND control records for complete parsing.
        """
        records = []
        lines = content.strip().split('\n')

        file_header = None
        batch_header = None
        batch_control = None
        file_control = None
        current_entry = None
        current_addenda = []
        entries_with_addenda = []  # Store all entries before we have control records

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
                    entries_with_addenda.append((current_entry, list(current_addenda)))
                current_entry = line
                current_addenda = []
            elif record_type == '7':
                current_addenda.append(line)
            elif record_type == '8':
                # Batch control - save the last entry first
                if current_entry:
                    entries_with_addenda.append((current_entry, list(current_addenda)))
                    current_entry = None
                    current_addenda = []
                batch_control = line
            elif record_type == '9':
                file_control = line

        # Handle case where file doesn't have batch control (save any remaining entry)
        if current_entry:
            entries_with_addenda.append((current_entry, list(current_addenda)))

        # Now build records with complete content including control records
        for entry, addenda in entries_with_addenda:
            records.append({
                'content': cls._build_ach_record(file_header, batch_header, entry, addenda,
                                                  batch_control, file_control),
                'index': len(records),
                'parent_context': {
                    'file_header': file_header,
                    'batch_header': batch_header,
                    'batch_control': batch_control,
                    'file_control': file_control,
                },
            })

        if not records:
            return [{'content': content, 'index': 0, 'parent_context': {}}]

        logger.info(f"Split ACH/NACHA into {len(records)} entry detail records")
        return records

    @classmethod
    def _build_ach_record(cls, file_header: str, batch_header: str, entry: str, addenda: List[str],
                          batch_control: str = None, file_control: str = None) -> str:
        """Build a complete ACH record from components including control records."""
        lines = []
        if file_header:
            lines.append(file_header)
        if batch_header:
            lines.append(batch_header)
        lines.append(entry)
        lines.extend(addenda)
        if batch_control:
            lines.append(batch_control)
        if file_control:
            lines.append(file_control)
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
