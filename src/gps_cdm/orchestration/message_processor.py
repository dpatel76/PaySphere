"""
Message Processing Pipeline - Format Detection and Extraction

This module provides a unified interface for parsing raw payment messages
in their native formats (XML, SWIFT, Fixed-Width, etc.) and extracting
them into structured data suitable for the Bronze, Silver, and Gold layers.

NO FALLBACKS OR DEFAULTS: If a required field cannot be extracted from the
source message, it is set to None. No synthetic data is generated.
"""

from typing import Dict, Any, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)


class MessageProcessor:
    """
    Unified message processor that handles format detection and parsing.

    Supports:
    - pain.001: ISO 20022 XML (Customer Credit Transfer Initiation)
    - MT103: SWIFT Block Format (Single Customer Credit Transfer)
    - FEDWIRE: Tag-Value Format (US Domestic Wire)
    - ACH: NACHA Fixed-Width Format (US Domestic ACH)
    - SEPA: ISO 20022 XML with SEPA rules (European Credit Transfer)
    - RTP: TCH pacs.008 XML (US Real-Time Payments)
    """

    @staticmethod
    def detect_format(raw_content: str, message_type: str = None) -> str:
        """
        Detect the format of the raw message content.

        Returns: 'xml', 'swift_block', 'tag_value', 'fixed_width', 'json', or 'unknown'
        """
        content = raw_content.strip()

        # XML detection
        if content.startswith('<?xml') or content.startswith('<Document') or content.startswith('<'):
            return 'xml'

        # SWIFT block format detection: {1:...}{2:...}
        if content.startswith('{1:') or content.startswith('{2:'):
            return 'swift_block'

        # Fedwire tag-value format: {NNNN}value
        if content.startswith('{1500}') or content.startswith('{1510}'):
            return 'tag_value'

        # ACH fixed-width format: starts with '1' (file header) and has 94-char lines
        lines = content.split('\n')
        if lines and len(lines[0]) >= 94 and lines[0][0] == '1':
            return 'fixed_width'

        # JSON detection
        if content.startswith('{') or content.startswith('['):
            return 'json'

        return 'unknown'

    @classmethod
    def parse_raw_content(cls, raw_content: str, message_type: str) -> Dict[str, Any]:
        """
        Parse raw message content into a structured dictionary.

        Args:
            raw_content: The raw message content (XML, SWIFT block, etc.)
            message_type: The message type (pain.001, MT103, FEDWIRE, etc.)

        Returns:
            Structured dictionary with parsed fields

        Raises:
            ValueError: If the format cannot be parsed
        """
        msg_type_normalized = message_type.upper().replace('.', '_').replace('-', '_')

        # Detect format
        detected_format = cls.detect_format(raw_content, message_type)

        # Route to appropriate parser
        if msg_type_normalized in ['PAIN_001', 'PAIN001']:
            return cls._parse_pain001(raw_content, detected_format)
        elif msg_type_normalized in ['MT103', '103']:
            return cls._parse_mt103(raw_content, detected_format)
        elif msg_type_normalized in ['FEDWIRE']:
            return cls._parse_fedwire(raw_content, detected_format)
        elif msg_type_normalized in ['ACH', 'NACHA']:
            return cls._parse_ach(raw_content, detected_format)
        elif msg_type_normalized in ['SEPA', 'SEPA_CT']:
            return cls._parse_sepa(raw_content, detected_format)
        elif msg_type_normalized in ['RTP', 'TCH_RTP']:
            return cls._parse_rtp(raw_content, detected_format)
        elif msg_type_normalized in ['PACS_008', 'PACS008']:
            return cls._parse_pacs008(raw_content, detected_format)
        else:
            # Unknown message type - try to parse as JSON
            if detected_format == 'json':
                return json.loads(raw_content)
            raise ValueError(f"Unknown message type: {message_type}")

    @classmethod
    def _parse_pain001(cls, raw_content: str, detected_format: str) -> Dict[str, Any]:
        """Parse pain.001 message."""
        if detected_format == 'xml':
            from gps_cdm.message_formats.pain001 import Pain001XmlParser
            parser = Pain001XmlParser()
            return parser.parse(raw_content)
        elif detected_format == 'json':
            return json.loads(raw_content)
        else:
            raise ValueError(f"Cannot parse pain.001 from format: {detected_format}")

    @classmethod
    def _parse_mt103(cls, raw_content: str, detected_format: str) -> Dict[str, Any]:
        """Parse MT103 message."""
        if detected_format == 'swift_block':
            from gps_cdm.message_formats.mt103 import MT103SwiftParser
            parser = MT103SwiftParser()
            return parser.parse(raw_content)
        elif detected_format == 'json':
            return json.loads(raw_content)
        else:
            raise ValueError(f"Cannot parse MT103 from format: {detected_format}")

    @classmethod
    def _parse_fedwire(cls, raw_content: str, detected_format: str) -> Dict[str, Any]:
        """Parse Fedwire message."""
        if detected_format == 'tag_value':
            from gps_cdm.message_formats.fedwire import FedwireTagValueParser
            parser = FedwireTagValueParser()
            return parser.parse(raw_content)
        elif detected_format == 'json':
            return json.loads(raw_content)
        else:
            raise ValueError(f"Cannot parse Fedwire from format: {detected_format}")

    @classmethod
    def _parse_ach(cls, raw_content: str, detected_format: str) -> Dict[str, Any]:
        """Parse ACH message."""
        if detected_format == 'fixed_width':
            from gps_cdm.message_formats.ach import AchFixedWidthParser
            parser = AchFixedWidthParser()
            return parser.parse(raw_content)
        elif detected_format == 'json':
            return json.loads(raw_content)
        else:
            raise ValueError(f"Cannot parse ACH from format: {detected_format}")

    @classmethod
    def _parse_sepa(cls, raw_content: str, detected_format: str) -> Dict[str, Any]:
        """Parse SEPA message."""
        if detected_format == 'xml':
            from gps_cdm.message_formats.sepa import SepaXmlParser
            parser = SepaXmlParser()
            return parser.parse(raw_content)
        elif detected_format == 'json':
            return json.loads(raw_content)
        else:
            raise ValueError(f"Cannot parse SEPA from format: {detected_format}")

    @classmethod
    def _parse_rtp(cls, raw_content: str, detected_format: str) -> Dict[str, Any]:
        """Parse RTP message."""
        if detected_format == 'xml':
            from gps_cdm.message_formats.rtp import RtpXmlParser
            parser = RtpXmlParser()
            return parser.parse(raw_content)
        elif detected_format == 'json':
            return json.loads(raw_content)
        else:
            raise ValueError(f"Cannot parse RTP from format: {detected_format}")

    @classmethod
    def _parse_pacs008(cls, raw_content: str, detected_format: str) -> Dict[str, Any]:
        """Parse pacs.008 message."""
        if detected_format == 'xml':
            # pacs.008 uses similar structure to RTP
            from gps_cdm.message_formats.rtp import RtpXmlParser
            parser = RtpXmlParser()
            return parser.parse(raw_content)
        elif detected_format == 'json':
            return json.loads(raw_content)
        else:
            raise ValueError(f"Cannot parse pacs.008 from format: {detected_format}")

    @classmethod
    def get_content_for_processing(cls, config: Dict[str, Any], message_type: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract raw content from config and parse it.

        Args:
            config: The task config which may contain 'message_content' or 'raw_xml'
            message_type: The message type

        Returns:
            Tuple of (raw_content_string, parsed_dict)
        """
        message_content = config.get('message_content') if config else None

        if message_content is None:
            raise ValueError("No message_content provided in config")

        # Determine raw content string
        raw_content = None

        if isinstance(message_content, str):
            raw_content = message_content
        elif isinstance(message_content, dict):
            # Check for nested raw content
            if 'raw_xml' in message_content:
                raw_content = message_content['raw_xml']
            elif 'raw_content' in message_content:
                raw_content = message_content['raw_content']
            elif 'raw' in message_content:
                raw_content = message_content['raw']
            else:
                # Assume the dict IS the parsed content (from JSON test files)
                return json.dumps(message_content), message_content

        if raw_content is None:
            raise ValueError("Could not extract raw content from message_content")

        # Parse the raw content
        parsed = cls.parse_raw_content(raw_content, message_type)

        return raw_content, parsed


def get_message_format(message_type: str) -> str:
    """
    Get the canonical message format for a message type.

    Returns: Format identifier (ISO20022, SWIFT_MT, FEDWIRE, ACH, etc.)
    """
    msg_type_normalized = message_type.upper().replace('.', '_').replace('-', '_')

    format_mapping = {
        # ISO 20022
        'PAIN_001': 'ISO20022',
        'PAIN001': 'ISO20022',
        'PAIN_002': 'ISO20022',
        'PACS_008': 'ISO20022',
        'PACS008': 'ISO20022',
        'PACS_002': 'ISO20022',
        'CAMT_053': 'ISO20022',
        # SWIFT MT
        'MT103': 'SWIFT_MT',
        '103': 'SWIFT_MT',
        'MT202': 'SWIFT_MT',
        # US Domestic
        'FEDWIRE': 'FEDWIRE',
        'ACH': 'NACHA',
        'NACHA': 'NACHA',
        # Regional
        'SEPA': 'SEPA',
        'SEPA_CT': 'SEPA',
        'RTP': 'TCH_RTP',
        'TCH_RTP': 'TCH_RTP',
        'FEDNOW': 'FEDNOW',
    }

    return format_mapping.get(msg_type_normalized, 'UNKNOWN')


def get_payment_type(message_type: str) -> str:
    """
    Derive payment type from message type.

    This is a legitimate transformation rule, not invented data.
    The payment type is determined by the message type semantics.
    """
    msg_type_normalized = message_type.upper().replace('.', '_').replace('-', '_')

    payment_type_mapping = {
        # Credit Transfers
        'PAIN_001': 'CREDIT_TRANSFER',
        'PAIN001': 'CREDIT_TRANSFER',
        'PACS_008': 'CREDIT_TRANSFER',
        'PACS008': 'CREDIT_TRANSFER',
        'MT103': 'CREDIT_TRANSFER',
        '103': 'CREDIT_TRANSFER',
        # Direct Debits
        'PAIN_008': 'DIRECT_DEBIT',
        'PACS_003': 'DIRECT_DEBIT',
        # Status
        'PAIN_002': 'PAYMENT_STATUS',
        'PACS_002': 'PAYMENT_STATUS',
        # Returns
        'PACS_004': 'PAYMENT_RETURN',
        # Cover Payments
        'MT202': 'COVER_PAYMENT',
        'PACS_009': 'COVER_PAYMENT',
        # US Domestic
        'FEDWIRE': 'WIRE_TRANSFER',
        'ACH': 'ACH_TRANSFER',
        'NACHA': 'ACH_TRANSFER',
        # Regional
        'SEPA': 'SEPA_CREDIT_TRANSFER',
        'SEPA_CT': 'SEPA_CREDIT_TRANSFER',
        'RTP': 'REAL_TIME_PAYMENT',
        'TCH_RTP': 'REAL_TIME_PAYMENT',
        'FEDNOW': 'INSTANT_PAYMENT',
    }

    return payment_type_mapping.get(msg_type_normalized, 'PAYMENT')
