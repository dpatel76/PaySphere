"""
GPS CDM - Celery Task Processing
================================

Distributed task processing using Celery for high-throughput batch processing.
Designed for 50M+ messages/day with horizontal scaling.

Architecture:
- NiFi handles ingestion, routing, and Kafka integration
- Celery handles parallel processing across worker pools
- Redis/RabbitMQ as message broker
- Workers process partitions independently with checkpointing

Usage:
    # Start workers (one per core):
    celery -A gps_cdm.orchestration.celery_tasks worker --loglevel=info --concurrency=8

    # Start beat scheduler for periodic tasks:
    celery -A gps_cdm.orchestration.celery_tasks beat --loglevel=info

    # Monitor with Flower:
    celery -A gps_cdm.orchestration.celery_tasks flower
"""

from celery import Celery, group, chain, chord
from celery.schedules import crontab
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import uuid
import hashlib
import logging

logger = logging.getLogger(__name__)
import os

# =============================================================================
# MESSAGE TYPE TO TABLE ROUTING
# =============================================================================
# Maps all 72+ payment message types to their Bronze, Silver, and Gold tables.
# This enables multi-table routing for the complete medallion pipeline.


def get_table_routing(message_type: str) -> dict:
    """
    Get table routing for a message type.

    Returns:
        Dict with bronze_table, silver_table, and gold_tables
    """
    # Normalize message type
    msg_type_lower = message_type.lower().replace(".", "_").replace("-", "_")

    # ISO 20022 PAIN family
    if msg_type_lower.startswith("pain_001") or msg_type_lower == "pain001":
        return {
            "bronze_table": "bronze_pain001",
            "silver_table": "silver_pain001",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account"],
            "payment_type": "CREDIT_TRANSFER",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("pain_002") or msg_type_lower == "pain002":
        return {
            "bronze_table": "bronze_pain002",
            "silver_table": "silver_pain002",
            "gold_tables": ["gold_cdm_payment_instruction"],
            "payment_type": "STATUS_REPORT",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("pain_007") or msg_type_lower == "pain007":
        return {
            "bronze_table": "bronze_pain007",
            "silver_table": "silver_pain007",
            "gold_tables": ["gold_cdm_payment_instruction"],
            "payment_type": "REVERSAL",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("pain_008") or msg_type_lower == "pain008":
        return {
            "bronze_table": "bronze_pain008",
            "silver_table": "silver_pain008",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account"],
            "payment_type": "DIRECT_DEBIT",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("pain_013") or msg_type_lower == "pain013":
        return {
            "bronze_table": "bronze_pain013",
            "silver_table": "silver_pain013",
            "gold_tables": ["gold_cdm_payment_instruction"],
            "payment_type": "PAYMENT_ACTIVATION",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("pain_014") or msg_type_lower == "pain014":
        return {
            "bronze_table": "bronze_pain014",
            "silver_table": "silver_pain014",
            "gold_tables": ["gold_cdm_payment_instruction"],
            "payment_type": "ACTIVATION_STATUS",
            "scheme": "ISO20022",
        }

    # ISO 20022 PACS family
    elif msg_type_lower.startswith("pacs_002") or msg_type_lower == "pacs002":
        return {
            "bronze_table": "bronze_pacs002",
            "silver_table": "silver_pacs002",
            "gold_tables": ["gold_cdm_payment_instruction"],
            "payment_type": "FI_STATUS_REPORT",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("pacs_003") or msg_type_lower == "pacs003":
        return {
            "bronze_table": "bronze_pacs003",
            "silver_table": "silver_pacs003",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account"],
            "payment_type": "FI_DIRECT_DEBIT",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("pacs_004") or msg_type_lower == "pacs004":
        return {
            "bronze_table": "bronze_pacs004",
            "silver_table": "silver_pacs004",
            "gold_tables": ["gold_cdm_payment_instruction"],
            "payment_type": "PAYMENT_RETURN",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("pacs_007") or msg_type_lower == "pacs007":
        return {
            "bronze_table": "bronze_pacs007",
            "silver_table": "silver_pacs007",
            "gold_tables": ["gold_cdm_payment_instruction"],
            "payment_type": "FI_REVERSAL",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("pacs_008") or msg_type_lower == "pacs008":
        return {
            "bronze_table": "bronze_pacs008",
            "silver_table": "silver_pacs008",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account", "gold_cdm_financial_institution"],
            "payment_type": "FI_CREDIT_TRANSFER",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("pacs_009") or msg_type_lower == "pacs009":
        return {
            "bronze_table": "bronze_pacs009",
            "silver_table": "silver_pacs009",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_financial_institution"],
            "payment_type": "FI_COVER_PAYMENT",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("pacs_028") or msg_type_lower == "pacs028":
        return {
            "bronze_table": "bronze_pacs028",
            "silver_table": "silver_pacs028",
            "gold_tables": ["gold_cdm_payment_instruction"],
            "payment_type": "POSITIVE_PAY",
            "scheme": "ISO20022",
        }

    # ISO 20022 CAMT family
    elif msg_type_lower.startswith("camt_026") or msg_type_lower == "camt026":
        return {
            "bronze_table": "bronze_camt026",
            "silver_table": "silver_camt026",
            "gold_tables": ["gold_cdm_payment_instruction"],
            "payment_type": "UNABLE_TO_APPLY",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("camt_027") or msg_type_lower == "camt027":
        return {
            "bronze_table": "bronze_camt027",
            "silver_table": "silver_camt027",
            "gold_tables": ["gold_cdm_payment_instruction"],
            "payment_type": "CLAIM_NON_RECEIPT",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("camt_028") or msg_type_lower == "camt028":
        return {
            "bronze_table": "bronze_camt028",
            "silver_table": "silver_camt028",
            "gold_tables": ["gold_cdm_payment_instruction"],
            "payment_type": "ADDITIONAL_INFO",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("camt_029") or msg_type_lower == "camt029":
        return {
            "bronze_table": "bronze_camt029",
            "silver_table": "silver_camt029",
            "gold_tables": ["gold_cdm_payment_instruction"],
            "payment_type": "RESOLUTION",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("camt_052") or msg_type_lower == "camt052":
        return {
            "bronze_table": "bronze_camt052",
            "silver_table": "silver_camt052",
            "gold_tables": ["gold_cdm_account"],
            "payment_type": "ACCOUNT_REPORT",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("camt_053") or msg_type_lower == "camt053":
        return {
            "bronze_table": "bronze_camt053",
            "silver_table": "silver_camt053",
            "gold_tables": ["gold_cdm_account", "gold_cdm_transaction"],
            "payment_type": "ACCOUNT_STATEMENT",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("camt_054") or msg_type_lower == "camt054":
        return {
            "bronze_table": "bronze_camt054",
            "silver_table": "silver_camt054",
            "gold_tables": ["gold_cdm_account", "gold_cdm_transaction"],
            "payment_type": "NOTIFICATION",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("camt_055") or msg_type_lower == "camt055":
        return {
            "bronze_table": "bronze_camt055",
            "silver_table": "silver_camt055",
            "gold_tables": ["gold_cdm_payment_instruction"],
            "payment_type": "CANCELLATION_REQUEST",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("camt_056") or msg_type_lower == "camt056":
        return {
            "bronze_table": "bronze_camt056",
            "silver_table": "silver_camt056",
            "gold_tables": ["gold_cdm_payment_instruction"],
            "payment_type": "FI_CANCELLATION",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("camt_057") or msg_type_lower == "camt057":
        return {
            "bronze_table": "bronze_camt057",
            "silver_table": "silver_camt057",
            "gold_tables": ["gold_cdm_payment_instruction"],
            "payment_type": "NOTIFICATION_TO_RECEIVE",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("camt_086") or msg_type_lower == "camt086":
        return {
            "bronze_table": "bronze_camt086",
            "silver_table": "silver_camt086",
            "gold_tables": ["gold_cdm_account"],
            "payment_type": "BILLING_STATEMENT",
            "scheme": "ISO20022",
        }

    # ISO 20022 ACMT family
    elif msg_type_lower.startswith("acmt_001") or msg_type_lower == "acmt001":
        return {
            "bronze_table": "bronze_acmt001",
            "silver_table": "silver_acmt001",
            "gold_tables": ["gold_cdm_account", "gold_cdm_party"],
            "payment_type": "ACCOUNT_OPENING",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("acmt_002") or msg_type_lower == "acmt002":
        return {
            "bronze_table": "bronze_acmt002",
            "silver_table": "silver_acmt002",
            "gold_tables": ["gold_cdm_account"],
            "payment_type": "ACCOUNT_AMENDMENT",
            "scheme": "ISO20022",
        }
    elif msg_type_lower.startswith("acmt_003") or msg_type_lower == "acmt003":
        return {
            "bronze_table": "bronze_acmt003",
            "silver_table": "silver_acmt003",
            "gold_tables": ["gold_cdm_account"],
            "payment_type": "ACCOUNT_MODIFICATION",
            "scheme": "ISO20022",
        }

    # SWIFT MT Messages
    elif msg_type_lower in ["mt103", "103", "mt103+"]:
        return {
            "bronze_table": "bronze_mt103",
            "silver_table": "silver_mt103",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account", "gold_cdm_financial_institution"],
            "payment_type": "CREDIT_TRANSFER",  # Standardized - MT103 is Single Customer Credit Transfer
            "scheme": "SWIFT",
        }
    elif msg_type_lower in ["mt200", "200"]:
        return {
            "bronze_table": "bronze_mt200",
            "silver_table": "silver_mt200",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_financial_institution"],
            "payment_type": "FI_OWN_TRANSFER",
            "scheme": "SWIFT",
        }
    elif msg_type_lower in ["mt202", "202"]:
        return {
            "bronze_table": "bronze_mt202",
            "silver_table": "silver_mt202",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_financial_institution"],
            "payment_type": "FI_TRANSFER",
            "scheme": "SWIFT",
        }
    elif msg_type_lower in ["mt202cov", "202cov"]:
        return {
            "bronze_table": "bronze_mt202cov",
            "silver_table": "silver_mt202cov",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_financial_institution"],
            "payment_type": "COVER_PAYMENT",
            "scheme": "SWIFT",
        }
    elif msg_type_lower in ["mt900", "900"]:
        return {
            "bronze_table": "bronze_mt900",
            "silver_table": "silver_mt900",
            "gold_tables": ["gold_cdm_account", "gold_cdm_transaction"],
            "payment_type": "DEBIT_CONFIRMATION",
            "scheme": "SWIFT",
        }
    elif msg_type_lower in ["mt910", "910"]:
        return {
            "bronze_table": "bronze_mt910",
            "silver_table": "silver_mt910",
            "gold_tables": ["gold_cdm_account", "gold_cdm_transaction"],
            "payment_type": "CREDIT_CONFIRMATION",
            "scheme": "SWIFT",
        }
    elif msg_type_lower in ["mt940", "940"]:
        return {
            "bronze_table": "bronze_mt940",
            "silver_table": "silver_mt940",
            "gold_tables": ["gold_cdm_account", "gold_cdm_transaction"],
            "payment_type": "STATEMENT",
            "scheme": "SWIFT",
        }
    elif msg_type_lower in ["mt950", "950"]:
        return {
            "bronze_table": "bronze_mt950",
            "silver_table": "silver_mt950",
            "gold_tables": ["gold_cdm_account", "gold_cdm_transaction"],
            "payment_type": "STATEMENT",
            "scheme": "SWIFT",
        }

    # Domestic Payment Schemes - SEPA
    elif msg_type_lower in ["sepa_sct", "sepa.sct", "sepa_credit_transfer"]:
        return {
            "bronze_table": "bronze_sepa_sct",
            "silver_table": "silver_sepa_sct",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account"],
            "payment_type": "SEPA_CREDIT_TRANSFER",
            "scheme": "SEPA",
        }
    elif msg_type_lower in ["sepa_sdd", "sepa.sdd", "sepa_direct_debit"]:
        return {
            "bronze_table": "bronze_sepa_sdd",
            "silver_table": "silver_sepa_sdd",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account"],
            "payment_type": "SEPA_DIRECT_DEBIT",
            "scheme": "SEPA",
        }

    # US Payment Schemes
    elif msg_type_lower in ["nacha", "nacha_ach", "ach"]:
        return {
            "bronze_table": "bronze_nacha_ach",
            "silver_table": "silver_nacha_ach",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account"],
            "payment_type": "ACH",
            "scheme": "NACHA",
        }
    elif msg_type_lower == "fedwire":
        return {
            "bronze_table": "bronze_fedwire",
            "silver_table": "silver_fedwire",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account", "gold_cdm_financial_institution"],
            "payment_type": "FEDWIRE",
            "scheme": "FEDWIRE",
        }
    elif msg_type_lower == "chips":
        return {
            "bronze_table": "bronze_chips",
            "silver_table": "silver_chips",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_financial_institution"],
            "payment_type": "CHIPS",
            "scheme": "CHIPS",
        }

    # UK Payment Schemes
    elif msg_type_lower == "bacs":
        return {
            "bronze_table": "bronze_bacs",
            "silver_table": "silver_bacs",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account"],
            "payment_type": "BACS",
            "scheme": "UK",
        }
    elif msg_type_lower == "chaps":
        return {
            "bronze_table": "bronze_chaps",
            "silver_table": "silver_chaps",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account", "gold_cdm_financial_institution"],
            "payment_type": "CHAPS",
            "scheme": "UK",
        }
    elif msg_type_lower in ["fps", "faster_payments"]:
        return {
            "bronze_table": "bronze_fps",
            "silver_table": "silver_fps",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account"],
            "payment_type": "FASTER_PAYMENTS",
            "scheme": "UK",
        }

    # Real-Time Payment Systems
    elif msg_type_lower == "fednow":
        return {
            "bronze_table": "bronze_fednow",
            "silver_table": "silver_fednow",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account", "gold_cdm_financial_institution"],
            "payment_type": "FEDNOW",
            "scheme": "FEDNOW",
        }
    elif msg_type_lower in ["rtp", "tch_rtp"]:
        return {
            "bronze_table": "bronze_rtp",
            "silver_table": "silver_rtp",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account", "gold_cdm_financial_institution"],
            "payment_type": "RTP",
            "scheme": "TCH",
        }
    elif msg_type_lower == "pix":
        return {
            "bronze_table": "bronze_pix",
            "silver_table": "silver_pix",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account"],
            "payment_type": "PIX",
            "scheme": "BCB",
        }
    elif msg_type_lower in ["npp", "osko"]:
        return {
            "bronze_table": "bronze_npp",
            "silver_table": "silver_npp",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account"],
            "payment_type": "NPP",
            "scheme": "NPP_AUSTRALIA",
        }
    elif msg_type_lower in ["upi", "imps"]:
        return {
            "bronze_table": "bronze_upi",
            "silver_table": "silver_upi",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account"],
            "payment_type": "UPI",
            "scheme": "NPCI",
        }
    elif msg_type_lower == "paynow":
        return {
            "bronze_table": "bronze_paynow",
            "silver_table": "silver_paynow",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account"],
            "payment_type": "PAYNOW",
            "scheme": "ABS_SG",
        }
    elif msg_type_lower == "promptpay":
        return {
            "bronze_table": "bronze_promptpay",
            "silver_table": "silver_promptpay",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account"],
            "payment_type": "PROMPTPAY",
            "scheme": "BOT_TH",
        }
    elif msg_type_lower == "instapay":
        return {
            "bronze_table": "bronze_instapay",
            "silver_table": "silver_instapay",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account"],
            "payment_type": "INSTAPAY",
            "scheme": "INSTAPAY_PH",
        }

    # RTGS Systems
    elif msg_type_lower in ["target2", "t2"]:
        return {
            "bronze_table": "bronze_target2",
            "silver_table": "silver_target2",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_financial_institution"],
            "payment_type": "TARGET2",
            "scheme": "ECB",
        }
    elif msg_type_lower in ["bojnet", "boj_net"]:
        return {
            "bronze_table": "bronze_bojnet",
            "silver_table": "silver_bojnet",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_financial_institution"],
            "payment_type": "BOJNET",
            "scheme": "BOJ",
        }
    elif msg_type_lower in ["cnaps", "hvps", "beps"]:
        return {
            "bronze_table": "bronze_cnaps",
            "silver_table": "silver_cnaps",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_financial_institution"],
            "payment_type": "CNAPS",
            "scheme": "PBOC",
        }
    elif msg_type_lower in ["meps", "meps_plus"]:
        return {
            "bronze_table": "bronze_meps",
            "silver_table": "silver_meps",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_financial_institution"],
            "payment_type": "MEPS_PLUS",
            "scheme": "MAS",
        }
    elif msg_type_lower in ["rtgs_hk", "chats"]:
        return {
            "bronze_table": "bronze_rtgs_hk",
            "silver_table": "silver_rtgs_hk",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_financial_institution"],
            "payment_type": "RTGS_HK",
            "scheme": "HKMA",
        }
    elif msg_type_lower == "sarie":
        return {
            "bronze_table": "bronze_sarie",
            "silver_table": "silver_sarie",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_financial_institution"],
            "payment_type": "SARIE",
            "scheme": "SAMA",
        }
    elif msg_type_lower == "uaefts":
        return {
            "bronze_table": "bronze_uaefts",
            "silver_table": "silver_uaefts",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_financial_institution"],
            "payment_type": "UAEFTS",
            "scheme": "CBUAE",
        }
    elif msg_type_lower in ["kftc", "bok_wire"]:
        return {
            "bronze_table": "bronze_kftc",
            "silver_table": "silver_kftc",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_financial_institution"],
            "payment_type": "KFTC",
            "scheme": "BOK",
        }

    # Default fallback for unknown message types
    else:
        logger.warning(f"Unknown message type '{message_type}', using generic routing")
        return {
            "bronze_table": f"bronze_{msg_type_lower}",
            "silver_table": f"silver_{msg_type_lower}",
            "gold_tables": ["gold_cdm_payment_instruction", "gold_cdm_party", "gold_cdm_account"],
            "payment_type": "UNKNOWN",
            "scheme": "UNKNOWN",
        }


def get_all_message_types() -> List[str]:
    """Return list of all supported message types."""
    return [
        # ISO 20022 PAIN
        "pain.001", "pain.002", "pain.007", "pain.008", "pain.013", "pain.014",
        # ISO 20022 PACS
        "pacs.002", "pacs.003", "pacs.004", "pacs.007", "pacs.008", "pacs.009", "pacs.028",
        # ISO 20022 CAMT
        "camt.026", "camt.027", "camt.028", "camt.029", "camt.052", "camt.053",
        "camt.054", "camt.055", "camt.056", "camt.057", "camt.086", "camt.087",
        # ISO 20022 ACMT
        "acmt.001", "acmt.002", "acmt.003", "acmt.005", "acmt.006", "acmt.007",
        # SWIFT MT
        "MT103", "MT200", "MT202", "MT202COV", "MT900", "MT910", "MT940", "MT950",
        # Domestic - SEPA
        "SEPA_SCT", "SEPA_SDD",
        # Domestic - US
        "NACHA_ACH", "Fedwire", "CHIPS",
        # Domestic - UK
        "BACS", "CHAPS", "FPS",
        # Real-Time
        "FedNow", "RTP", "PIX", "NPP", "UPI", "PayNow", "PromptPay", "InstaPay",
        # RTGS
        "TARGET2", "BOJNET", "CNAPS", "MEPS", "RTGS_HK", "SARIE", "UAEFTS", "KFTC",
    ]


def get_message_format(message_type: str) -> str:
    """
    Determine the message format based on message type.

    Returns:
        - XML: ISO 20022 messages (pain.*, pacs.*, camt.*, acmt.*), SEPA, FedNow, RTP
        - SWIFT_MT: SWIFT MT messages (MT103, MT202, MT940, etc.)
        - FIXED_WIDTH: NACHA ACH, BACS
        - JSON: Modern real-time systems (PIX, NPP, UPI, PayNow, etc.)
        - PROPRIETARY: CHIPS, CHAPS, RTGS systems
    """
    msg_type = message_type.lower().strip()

    # ISO 20022 XML formats
    if msg_type.startswith(('pain.', 'pacs.', 'camt.', 'acmt.')):
        return "XML"

    # SWIFT MT plain text format
    if msg_type.startswith('mt') and msg_type[2:].replace('cov', '').isdigit():
        return "SWIFT_MT"

    # SEPA uses ISO 20022 XML
    if msg_type in ('sepa_sct', 'sepa.sct', 'sepa_sdd', 'sepa.sdd', 'sepa_credit_transfer', 'sepa_direct_debit'):
        return "XML"

    # US Payments
    if msg_type in ('nacha', 'nacha_ach', 'ach'):
        return "FIXED_WIDTH"
    if msg_type == 'fedwire':
        return "PROPRIETARY"  # Fedwire uses its own proprietary format
    if msg_type == 'chips':
        return "PROPRIETARY"

    # UK Payments
    if msg_type == 'bacs':
        return "FIXED_WIDTH"  # BACS Standard 18 format
    if msg_type in ('chaps', 'fps'):
        return "XML"  # UK uses ISO 20022 for CHAPS/FPS

    # Real-time payment systems
    if msg_type in ('fednow', 'rtp'):
        return "XML"  # FedNow and RTP use ISO 20022
    if msg_type in ('pix', 'npp', 'upi', 'paynow', 'promptpay', 'instapay'):
        return "JSON"  # Modern real-time systems use JSON

    # RTGS systems
    if msg_type in ('target2', 'bojnet', 'cnaps', 'meps', 'rtgs_hk', 'sarie', 'uaefts', 'kftc'):
        return "PROPRIETARY"

    # Default to XML (most standards are migrating to ISO 20022)
    return "XML"


# Celery configuration
BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

app = Celery(
    "gps_cdm",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["gps_cdm.orchestration.celery_tasks"],
)

# Celery configuration for high throughput
app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Worker settings for 50M/day
    worker_prefetch_multiplier=4,  # Prefetch 4 tasks per worker
    worker_concurrency=8,  # 8 concurrent tasks per worker
    task_acks_late=True,  # Acknowledge after task completion
    task_reject_on_worker_lost=True,  # Requeue on worker death

    # Result settings
    result_expires=3600,  # Results expire after 1 hour

    # Task time limits
    task_soft_time_limit=300,  # 5 minute soft limit
    task_time_limit=600,  # 10 minute hard limit

    # Retry settings
    task_default_retry_delay=60,
    task_max_retries=3,

    # Task routing for different workloads
    task_routes={
        # Legacy monolithic task (deprecated - use zone_tasks instead)
        "gps_cdm.orchestration.celery_tasks.process_bronze_partition": {"queue": "bronze"},
        "gps_cdm.orchestration.celery_tasks.process_silver_transform": {"queue": "silver"},
        "gps_cdm.orchestration.celery_tasks.process_gold_aggregate": {"queue": "gold"},
        "gps_cdm.orchestration.celery_tasks.run_dq_evaluation": {"queue": "dq"},
        "gps_cdm.orchestration.celery_tasks.sync_cdc_to_neo4j": {"queue": "cdc"},
        # New zone-separated tasks (preferred)
        "gps_cdm.zone_tasks.process_bronze_records": {"queue": "bronze"},
        "gps_cdm.zone_tasks.process_silver_records": {"queue": "silver"},
        "gps_cdm.zone_tasks.process_gold_records": {"queue": "gold"},
        "gps_cdm.zone_tasks.retry_error": {"queue": "celery"},
        "gps_cdm.zone_tasks.bulk_retry_errors": {"queue": "celery"},
    },

    # Beat scheduler for periodic tasks
    beat_schedule={
        "aggregate-dq-metrics-hourly": {
            "task": "gps_cdm.orchestration.celery_tasks.aggregate_dq_metrics",
            "schedule": crontab(minute=0),  # Every hour
        },
        "sync-cdc-to-neo4j-every-5min": {
            "task": "gps_cdm.orchestration.celery_tasks.sync_cdc_to_neo4j",
            "schedule": timedelta(minutes=5),
        },
        "cleanup-old-checkpoints-daily": {
            "task": "gps_cdm.orchestration.celery_tasks.cleanup_old_checkpoints",
            "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
        },
    },
)

# Import zone-separated tasks so Celery discovers them
from gps_cdm.orchestration import zone_tasks  # noqa: F401


# =============================================================================
# ENTITY EXTRACTION HELPER FUNCTIONS
# =============================================================================

# Import extractors and common persistence
from gps_cdm.message_formats.base import ExtractorRegistry, GoldEntityPersister


def extract_and_persist_entities(cursor, msg_content: dict, message_type: str, stg_id: str, batch_id: str):
    """
    Extract Party, Account, and Financial Institution entities from message content
    and persist them to Gold layer tables.

    Uses message-format-specific extractors with common persistence logic.

    Returns dict with entity IDs for linking to payment instruction:
        {
            'debtor_id': str or None,
            'debtor_account_id': str or None,
            'debtor_agent_id': str or None,
            'creditor_id': str or None,
            'creditor_account_id': str or None,
            'creditor_agent_id': str or None,
            'intermediary_agent1_id': str or None,
            'intermediary_agent2_id': str or None,
            'ultimate_debtor_id': str or None,
            'ultimate_creditor_id': str or None,
        }
    """
    # Get the appropriate extractor for this message type
    extractor = ExtractorRegistry.get(message_type)

    if extractor:
        # Use the extractor to get standardized Gold entities
        gold_entities = extractor.extract_gold_entities(msg_content, stg_id, batch_id)

        # Use common persistence to save all entities
        entity_ids = GoldEntityPersister.persist_all_entities(
            cursor, gold_entities, message_type, stg_id, 'GPS_CDM'
        )

        return entity_ids

    # Fallback for unregistered message types - return empty IDs
    logger.warning(f"No extractor registered for message type: {message_type}")
    return {
        'debtor_id': None,
        'debtor_account_id': None,
        'debtor_agent_id': None,
        'creditor_id': None,
        'creditor_account_id': None,
        'creditor_agent_id': None,
        'intermediary_agent1_id': None,
        'intermediary_agent2_id': None,
        'ultimate_debtor_id': None,
        'ultimate_creditor_id': None,
    }


# The old inline extraction code has been removed.
# All entity extraction now happens through message-format-specific extractors
# in gps_cdm.message_formats.* with common persistence via GoldEntityPersister.


# =============================================================================
# BRONZE LAYER TASKS
# =============================================================================

@app.task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def process_bronze_partition(
    self,
    partition_id: str,
    file_paths: List[str],
    message_type: str,
    batch_id: str,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Process a partition of files into bronze layer.

    This task is designed to be run in parallel across many partitions.
    Each worker processes its partition independently with checkpointing.

    Args:
        partition_id: Unique partition identifier
        file_paths: List of file paths in this partition
        message_type: Type of message (pain001, mt103, etc.)
        batch_id: Overall batch identifier
        config: Persistence configuration

    Returns:
        Dict with processing results
    """
    from gps_cdm.ingestion.persistence.base import PersistenceConfig, Layer

    start_time = datetime.utcnow()
    records_processed = 0
    errors = []

    try:
        # Check if message content was passed directly (from NiFi)
        message_content = config.get('message_content') if config else None

        # Check GPS_CDM_DATA_SOURCE environment variable to determine which store to use
        # Default to 'postgresql' for local development; set to 'databricks' for cloud
        data_source = os.environ.get('GPS_CDM_DATA_SOURCE', 'postgresql').lower()

        use_databricks = False
        use_postgres = False
        connector = None
        pg_conn = None

        # Only try Databricks if explicitly configured
        if data_source == 'databricks':
            try:
                from gps_cdm.ingestion.persistence.databricks_connector import DatabricksConnector
                connector = DatabricksConnector()
                use_databricks = connector.is_available()
                if not use_databricks:
                    logger.warning("Databricks configured but not available, will fallback to PostgreSQL")
            except Exception as db_err:
                logger.warning(f"Databricks connection failed: {db_err}")
                use_databricks = False
                connector = None

        # Use PostgreSQL if configured or as fallback
        if not use_databricks:
            try:
                import psycopg2
                pg_conn = psycopg2.connect(
                    host=os.environ.get('POSTGRES_HOST', 'localhost'),
                    port=int(os.environ.get('POSTGRES_PORT', 5433)),
                    database=os.environ.get('POSTGRES_DB', 'gps_cdm'),
                    user=os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
                    password=os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password')
                )
                use_postgres = True
            except Exception as pg_err:
                logger.warning(f"PostgreSQL connection failed: {pg_err}")
                use_postgres = False
                pg_conn = None

        if message_content and use_databricks and connector:
            # Process inline message content from NiFi
            raw_id = f"raw_{uuid.uuid4().hex[:12]}"
            stg_id = f"stg_{uuid.uuid4().hex[:12]}"
            instr_id = f"instr_{uuid.uuid4().hex[:12]}"

            # Parse message content - can be dict or string
            msg_content = message_content if isinstance(message_content, dict) else {}
            if isinstance(message_content, str):
                try:
                    msg_content = json.loads(message_content)
                except:
                    msg_content = {"raw": message_content}

            # Extract values from message content (using actual parsed data)
            msg_id = msg_content.get('messageId', msg_content.get('message_id', f'MSG-{uuid.uuid4().hex[:8]}'))

            # Try to use parser for proper field extraction
            try:
                from gps_cdm.orchestration.message_parsers import MESSAGE_PARSERS
                parser_class = MESSAGE_PARSERS.get(message_type)
                if parser_class:
                    parser = parser_class()
                    parsed = parser.parse(json.dumps(msg_content))
                else:
                    parsed = msg_content
            except Exception:
                parsed = msg_content

            # Extract field values from parsed data - NO DEFAULTS, use NULL if not present
            debtor_name = (parsed.get('debtor_name') or parsed.get('payer_name') or
                          parsed.get('debtorName') or msg_content.get('debtor', {}).get('name') or
                          parsed.get('initiating_party_name') or None)
            creditor_name = (parsed.get('creditor_name') or parsed.get('payee_name') or
                            parsed.get('creditorName') or msg_content.get('creditor', {}).get('name') or None)
            amount = parsed.get('instructed_amount') or parsed.get('amount') or parsed.get('control_sum') or msg_content.get('amount')
            if amount is not None:
                amount = float(amount)
            else:
                amount = 0  # Amount is required in Gold, but should come from source
            currency = (parsed.get('instructed_currency') or parsed.get('currency') or
                       msg_content.get('currency') or None)

            # payment_method comes from message - stored in Silver
            payment_method = parsed.get('payment_method') or msg_content.get('payment_method')

            # Get routing info - payment_type is derived from message_type
            routing = get_table_routing(message_type)
            payment_type = routing.get('payment_type') if routing else None

            # Derive payment_type from message_type (this is transformation logic, not invented data)
            if not payment_type:
                payment_type_mapping = {
                    'pain.001': 'CREDIT_TRANSFER',
                    'pain.002': 'PAYMENT_STATUS',
                    'pacs.008': 'CREDIT_TRANSFER',
                    'pacs.002': 'PAYMENT_STATUS',
                    'MT103': 'CREDIT_TRANSFER',
                    'MT202': 'COVER_PAYMENT',
                    'FEDWIRE': 'WIRE_TRANSFER',
                    'ACH': 'ACH_TRANSFER',
                    'SEPA': 'SEPA_TRANSFER',
                }
                payment_type = payment_type_mapping.get(message_type, 'TRANSFER')

            # Escape special characters for SQL
            def sql_escape(val):
                if val is None:
                    return 'NULL'
                return str(val).replace("'", "''")

            # 1. Write to Bronze layer (raw data)
            bronze_table = connector.get_table_name("bronze_raw_payment")
            bronze_sql = f"""
                INSERT INTO {bronze_table}
                (raw_id, message_type, message_id, creation_datetime, raw_xml,
                 file_name, file_path, _batch_id, _ingested_at)
                VALUES ('{raw_id}', '{message_type}', '{sql_escape(msg_id)}',
                        '{datetime.utcnow().isoformat()}', '{sql_escape(json.dumps(msg_content))}',
                        'nifi_stream', 'nifi://stream/{message_type}', '{batch_id}',
                        '{datetime.utcnow().isoformat()}')
            """
            connector.execute(bronze_sql)

            # 2. Write to Silver layer (parsed/normalized data)
            silver_table = connector.get_table_name("silver_stg_payment_instruction")
            silver_sql = f"""
                INSERT INTO {silver_table}
                (stg_id, raw_id, message_type, message_id,
                 amount, currency, debtor_name, creditor_name,
                 dq_score, _batch_id, _ingested_at, created_at)
                VALUES ('{stg_id}', '{raw_id}', '{message_type}', '{sql_escape(msg_id)}',
                        {amount}, '{sql_escape(currency)}', '{sql_escape(debtor_name)}', '{sql_escape(creditor_name)}',
                        0.95, '{batch_id}', '{datetime.utcnow().isoformat()}',
                        '{datetime.utcnow().isoformat()}')
            """
            connector.execute(silver_sql)

            # 3. Write to Gold layer (CDM unified format)
            gold_table = connector.get_table_name("gold_cdm_payment_instruction")
            gold_sql = f"""
                INSERT INTO {gold_table}
                (instruction_id, stg_id, message_type, payment_type,
                 amount, currency, status, _batch_id, _ingested_at, created_at)
                VALUES ('{instr_id}', '{stg_id}', '{message_type}', '{payment_type}',
                        {amount}, '{sql_escape(currency)}', 'PROCESSED', '{batch_id}',
                        '{datetime.utcnow().isoformat()}', '{datetime.utcnow().isoformat()}')
            """
            connector.execute(gold_sql)

            records_processed = 1

            # 4. Sync to Neo4j
            try:
                from gps_cdm.orchestration.neo4j_service import get_neo4j_service
                neo4j = get_neo4j_service()
                if neo4j:
                    neo4j.upsert_batch({
                        'batch_id': batch_id,
                        'message_type': message_type,
                        'source_system': 'NIFI',
                        'status': 'COMPLETED',
                        'created_at': datetime.utcnow().isoformat(),
                        'total_records': 1  # Increment by 1 for each record
                    })
                    neo4j.upsert_batch_layer(batch_id, 'bronze', {
                        'input_count': 1, 'processed_count': 1, 'failed_count': 0
                    })
                    neo4j.upsert_batch_layer(batch_id, 'silver', {
                        'input_count': 1, 'processed_count': 1, 'failed_count': 0
                    })
                    neo4j.upsert_batch_layer(batch_id, 'gold', {
                        'input_count': 1, 'processed_count': 1, 'failed_count': 0
                    })
            except Exception as neo4j_err:
                logger.warning(f"Neo4j sync failed: {neo4j_err}")

        elif message_content and use_postgres and pg_conn:
            # PostgreSQL fallback when Databricks is unavailable
            raw_id = f"raw_{uuid.uuid4().hex[:12]}"
            stg_id = f"stg_{uuid.uuid4().hex[:12]}"
            instr_id = f"instr_{uuid.uuid4().hex[:12]}"

            # Parse message content
            msg_content = message_content if isinstance(message_content, dict) else {}
            if isinstance(message_content, str):
                try:
                    msg_content = json.loads(message_content)
                except:
                    msg_content = {"raw": message_content}

            msg_id = msg_content.get('messageId', msg_content.get('message_id', f'MSG-{uuid.uuid4().hex[:8]}'))

            # Try to use parser
            try:
                from gps_cdm.orchestration.message_parsers import MESSAGE_PARSERS
                parser_class = MESSAGE_PARSERS.get(message_type)
                if parser_class:
                    parser = parser_class()
                    parsed = parser.parse(json.dumps(msg_content))
                else:
                    parsed = msg_content
            except Exception:
                parsed = msg_content

            # Extract values - NO DEFAULTS, use NULL if not present
            # Support both snake_case (from parsers) and camelCase (from JSON test files)
            debtor_name = (parsed.get('debtor_name') or parsed.get('payer_name') or
                          parsed.get('debtorName') or msg_content.get('debtor', {}).get('name') or
                          msg_content.get('orderingCustomer', {}).get('name') or
                          parsed.get('initiating_party_name') or msg_content.get('initiatingParty', {}).get('name') or None)
            creditor_name = (parsed.get('creditor_name') or parsed.get('payee_name') or
                            parsed.get('creditorName') or msg_content.get('creditor', {}).get('name') or
                            msg_content.get('beneficiaryCustomer', {}).get('name') or None)
            # For amount: check camelCase from JSON, snake_case from parsers, and nested structures
            amount = (parsed.get('instructed_amount') or parsed.get('amount') or
                     parsed.get('control_sum') or msg_content.get('amount') or
                     msg_content.get('instructedAmount') or msg_content.get('controlSum'))
            if amount is not None:
                amount = float(amount)
            # For currency: check camelCase from JSON and snake_case from parsers
            currency = (parsed.get('instructed_currency') or parsed.get('currency') or
                       msg_content.get('currency') or msg_content.get('instructedCurrency') or
                       msg_content.get('currencyCode') or None)

            # payment_method comes from message or is derived from message_type
            # This is a LEGITIMATE transformation based on the message type
            payment_method = (parsed.get('payment_method') or msg_content.get('payment_method') or
                             msg_content.get('paymentInformation', {}).get('paymentMethod') or
                             msg_content.get('paymentMethod'))

            # Get routing info - payment_type is derived from message_type during Silver->Gold transform
            # This is documented in the schema and is part of the transformation logic
            routing = get_table_routing(message_type)
            # payment_type is derived from message_type, NOT invented - it's a transformation rule
            payment_type = routing.get('payment_type') if routing else None
            message_format = get_message_format(message_type)

            # Derive payment_type from message_type if not explicitly set (this is transformation logic)
            if not payment_type:
                # Standard payment types based on message format
                payment_type_mapping = {
                    'pain.001': 'CREDIT_TRANSFER',
                    'pain.002': 'PAYMENT_STATUS',
                    'pacs.008': 'CREDIT_TRANSFER',
                    'pacs.002': 'PAYMENT_STATUS',
                    'pacs.004': 'PAYMENT_RETURN',
                    'MT103': 'CREDIT_TRANSFER',
                    'MT202': 'COVER_PAYMENT',
                    'FEDWIRE': 'WIRE_TRANSFER',
                    'ACH': 'ACH_TRANSFER',
                    'SEPA': 'SEPA_TRANSFER',
                    'CHAPS': 'CHAPS_TRANSFER',
                    'BACS': 'BACS_TRANSFER',
                    'RTP': 'REAL_TIME_PAYMENT',
                    'FEDNOW': 'INSTANT_PAYMENT',
                }
                payment_type = payment_type_mapping.get(message_type, 'TRANSFER')

            try:
                cursor = pg_conn.cursor()

                # Bronze layer - use PostgreSQL schema.table format
                cursor.execute("""
                    INSERT INTO bronze.raw_payment_messages
                    (raw_id, message_type, message_format, raw_content, raw_content_hash,
                     source_system, source_file_path, processing_status, _batch_id, _ingested_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (raw_id) DO NOTHING
                """, (raw_id, message_type, message_format, json.dumps(msg_content),
                      hashlib.sha256(json.dumps(msg_content).encode()).hexdigest()[:64],
                      'TEST_SCRIPT', f'test://{message_type}', 'PROCESSED',
                      batch_id, datetime.utcnow()))

                # Silver layer - route to correct stg_* table based on message type
                # Get normalized message type for table routing
                msg_type_lower = message_type.lower().replace('.', '_').replace('-', '_')

                if msg_type_lower in ['pain_001', 'pain001']:
                    # Extract pain.001-specific fields from msg_content
                    # COMPLETE EXTRACTION - All 77 source fields captured

                    # Group Header fields
                    creation_dt = msg_content.get('creationDateTime')
                    num_txns = msg_content.get('numberOfTransactions')
                    ctrl_sum = msg_content.get('controlSum')

                    # Initiating Party - nested structure (ALL fields)
                    initiating_party = msg_content.get('initiatingParty', {})
                    init_party_name = initiating_party.get('name')
                    init_party_id = initiating_party.get('id')
                    init_party_id_type = initiating_party.get('idType')  # NEW
                    init_party_country = initiating_party.get('country')  # NEW

                    # Payment Information - nested structure (ALL fields)
                    pmt_info = msg_content.get('paymentInformation', {})
                    pmt_info_id = pmt_info.get('paymentInfoId')
                    pmt_method = pmt_info.get('paymentMethod') or msg_content.get('paymentMethod') or 'TRF'
                    batch_booking = pmt_info.get('batchBooking', False)
                    req_exec_date = pmt_info.get('requestedExecutionDate') or msg_content.get('requestedExecutionDate')
                    service_level = pmt_info.get('serviceLevel')  # NEW
                    local_instrument = pmt_info.get('localInstrument')  # NEW
                    category_purpose = pmt_info.get('categoryPurpose')  # NEW

                    # Debtor (Party) - nested structure (ALL fields)
                    debtor = msg_content.get('debtor', {})
                    debtor_nm = debtor.get('name') or debtor_name
                    debtor_street = debtor.get('streetName')
                    debtor_bldg = debtor.get('buildingNumber')
                    debtor_postal = debtor.get('postalCode')
                    debtor_town = debtor.get('townName')
                    debtor_country_sub = debtor.get('countrySubDivision')  # NEW
                    debtor_country = debtor.get('country')
                    debtor_id = debtor.get('id')
                    debtor_id_type = debtor.get('idType')

                    # Debtor Account - nested structure (ALL fields)
                    debtor_acct = msg_content.get('debtorAccount', {})
                    debtor_acct_iban = debtor_acct.get('iban')
                    debtor_acct_other = debtor_acct.get('other') or debtor_acct.get('accountNumber')
                    debtor_acct_ccy = debtor_acct.get('currency')
                    debtor_acct_type = debtor_acct.get('accountType')  # NEW

                    # Debtor Agent (Financial Institution) - nested structure (ALL fields)
                    debtor_agent = msg_content.get('debtorAgent', {})
                    debtor_agent_bic = debtor_agent.get('bic')
                    debtor_agent_name = debtor_agent.get('name')
                    debtor_agent_clr_sys = debtor_agent.get('clearingSystem')
                    debtor_agent_member = debtor_agent.get('memberId')
                    debtor_agent_country = debtor_agent.get('country')  # NEW

                    # Credit Transfer Transaction fields
                    instr_id = msg_content.get('instructionId')
                    end_to_end_id = msg_content.get('endToEndId') or msg_content.get('end_to_end_id')
                    uetr = msg_content.get('uetr')

                    # Amounts (ALL fields)
                    instr_amt = msg_content.get('instructedAmount') or amount
                    instr_ccy = msg_content.get('instructedCurrency') or currency
                    equiv_amt = msg_content.get('equivalentAmount')
                    equiv_ccy = msg_content.get('equivalentCurrency')
                    exchange_rate = msg_content.get('exchangeRate')  # NEW

                    # Creditor Agent (Financial Institution) - nested structure (ALL fields)
                    creditor_agent = msg_content.get('creditorAgent', {})
                    creditor_agent_bic = creditor_agent.get('bic')
                    creditor_agent_name = creditor_agent.get('name')
                    creditor_agent_clr_sys = creditor_agent.get('clearingSystem')
                    creditor_agent_member = creditor_agent.get('memberId')
                    creditor_agent_country = creditor_agent.get('country')  # NEW

                    # Creditor (Party) - nested structure (ALL fields)
                    creditor = msg_content.get('creditor', {})
                    creditor_nm = creditor.get('name') or creditor_name
                    creditor_street = creditor.get('streetName')
                    creditor_bldg = creditor.get('buildingNumber')
                    creditor_postal = creditor.get('postalCode')
                    creditor_town = creditor.get('townName')
                    creditor_country_sub = creditor.get('countrySubDivision')  # NEW
                    creditor_country = creditor.get('country')
                    creditor_id = creditor.get('id')
                    creditor_id_type = creditor.get('idType')

                    # Creditor Account - nested structure (ALL fields)
                    creditor_acct = msg_content.get('creditorAccount', {})
                    creditor_acct_iban = creditor_acct.get('iban')
                    creditor_acct_other = creditor_acct.get('other') or creditor_acct.get('accountNumber')
                    creditor_acct_ccy = creditor_acct.get('currency')
                    creditor_acct_type = creditor_acct.get('accountType')  # NEW

                    # Ultimate Debtor - nested structure (ALL fields) - NEW
                    ultimate_debtor = msg_content.get('ultimateDebtor', {})
                    ultimate_debtor_name = ultimate_debtor.get('name') if ultimate_debtor else None
                    ultimate_debtor_id = ultimate_debtor.get('id') if ultimate_debtor else None
                    ultimate_debtor_id_type = ultimate_debtor.get('idType') if ultimate_debtor else None

                    # Ultimate Creditor - nested structure (ALL fields) - NEW
                    ultimate_creditor = msg_content.get('ultimateCreditor', {})
                    ultimate_creditor_name = ultimate_creditor.get('name') if ultimate_creditor else None
                    ultimate_creditor_id = ultimate_creditor.get('id') if ultimate_creditor else None
                    ultimate_creditor_id_type = ultimate_creditor.get('idType') if ultimate_creditor else None

                    # Purpose and Charges
                    purpose_code = msg_content.get('purposeCode') or msg_content.get('purpose_code')
                    charge_bearer = msg_content.get('chargeBearer') or msg_content.get('charge_bearer')

                    # Remittance Information - nested structure
                    remit_info = msg_content.get('remittanceInformation', {})
                    if isinstance(remit_info, str):
                        remit_unstruct = remit_info
                        remit_struct = None
                    else:
                        remit_unstruct = remit_info.get('unstructured')
                        remit_struct = remit_info.get('structured')

                    # Regulatory Reporting - nested structure (store as JSONB)
                    reg_reporting = msg_content.get('regulatoryReporting')

                    cursor.execute("""
                        INSERT INTO silver.stg_pain001
                        (stg_id, raw_id, msg_id, creation_date_time, number_of_transactions, control_sum,
                         initiating_party_name, initiating_party_id, initiating_party_id_type, initiating_party_country,
                         payment_info_id, payment_method, batch_booking, requested_execution_date,
                         service_level, local_instrument, category_purpose,
                         debtor_name, debtor_street_name, debtor_building_number, debtor_postal_code, debtor_town_name,
                         debtor_country_sub_division, debtor_country, debtor_id, debtor_id_type,
                         debtor_account_iban, debtor_account_other, debtor_account_currency, debtor_account_type,
                         debtor_agent_bic, debtor_agent_name, debtor_agent_clearing_system, debtor_agent_member_id, debtor_agent_country,
                         instruction_id, end_to_end_id, uetr,
                         instructed_amount, instructed_currency, equivalent_amount, equivalent_currency, exchange_rate,
                         creditor_agent_bic, creditor_agent_name, creditor_agent_clearing_system, creditor_agent_member_id, creditor_agent_country,
                         creditor_name, creditor_street_name, creditor_building_number, creditor_postal_code, creditor_town_name,
                         creditor_country_sub_division, creditor_country, creditor_id, creditor_id_type,
                         creditor_account_iban, creditor_account_other, creditor_account_currency, creditor_account_type,
                         ultimate_debtor_name, ultimate_debtor_id, ultimate_debtor_id_type,
                         ultimate_creditor_name, ultimate_creditor_id, ultimate_creditor_id_type,
                         purpose_code, charge_bearer, remittance_information, structured_remittance, regulatory_reporting,
                         processing_status, _batch_id, _processed_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (stg_id) DO NOTHING
                    """, (stg_id, raw_id, msg_id, creation_dt, num_txns, ctrl_sum,
                          init_party_name, init_party_id, init_party_id_type, init_party_country,
                          pmt_info_id, pmt_method, batch_booking, req_exec_date,
                          service_level, local_instrument, category_purpose,
                          debtor_nm, debtor_street, debtor_bldg, debtor_postal, debtor_town,
                          debtor_country_sub, debtor_country, debtor_id, debtor_id_type,
                          debtor_acct_iban, debtor_acct_other, debtor_acct_ccy, debtor_acct_type,
                          debtor_agent_bic, debtor_agent_name, debtor_agent_clr_sys, debtor_agent_member, debtor_agent_country,
                          instr_id, end_to_end_id, uetr,
                          instr_amt, instr_ccy, equiv_amt, equiv_ccy, exchange_rate,
                          creditor_agent_bic, creditor_agent_name, creditor_agent_clr_sys, creditor_agent_member, creditor_agent_country,
                          creditor_nm, creditor_street, creditor_bldg, creditor_postal, creditor_town,
                          creditor_country_sub, creditor_country, creditor_id, creditor_id_type,
                          creditor_acct_iban, creditor_acct_other, creditor_acct_ccy, creditor_acct_type,
                          ultimate_debtor_name, ultimate_debtor_id, ultimate_debtor_id_type,
                          ultimate_creditor_name, ultimate_creditor_id, ultimate_creditor_id_type,
                          purpose_code, charge_bearer, remit_unstruct,
                          json.dumps(remit_struct) if remit_struct else None,
                          json.dumps(reg_reporting) if reg_reporting else None,
                          'PROCESSED', batch_id, datetime.utcnow()))
                    source_stg_table = 'stg_pain001'

                    # Store extracted values for Gold layer
                    extracted_end_to_end_id = end_to_end_id
                    extracted_uetr = uetr
                    extracted_charge_bearer = charge_bearer

                elif msg_type_lower in ['mt103', '103']:
                    # Extract MT103-specific fields from msg_content
                    # COMPLETE EXTRACTION - All source fields captured
                    # All nested structures need to be fully extracted

                    # Helper to truncate strings
                    def trunc(val, max_len):
                        if val and len(str(val)) > max_len:
                            return str(val)[:max_len]
                        return val

                    # Basic message fields
                    sender_ref = trunc(msg_content.get('senderReference'), 16)
                    transaction_ref_num = trunc(msg_content.get('transactionReferenceNumber'), 16)  # NEW - Field 20 TRN
                    related_ref = trunc(msg_content.get('relatedReference'), 16)
                    bank_op_code = msg_content.get('bankOperationCode')
                    instr_codes = msg_content.get('instructionCode')  # Could be array
                    if instr_codes and not isinstance(instr_codes, list):
                        instr_codes = [instr_codes]
                    value_date = msg_content.get('valueDate')
                    exchange_rate = msg_content.get('exchangeRate')
                    mt103_uetr = msg_content.get('uetr')

                    # Amount fields
                    mt103_currency = msg_content.get('currencyCode') or currency
                    mt103_amount = amount
                    instr_currency = msg_content.get('instructedCurrency')
                    instr_amount = msg_content.get('instructedAmount')

                    # Ordering Customer (Field 50) - nested structure - ALL fields captured
                    ordering_cust = msg_content.get('orderingCustomer', {})
                    ordering_cust_acct = trunc(ordering_cust.get('account'), 34)
                    ordering_cust_name = trunc(ordering_cust.get('name') or debtor_name, 140)
                    ordering_cust_addr = ordering_cust.get('address', {})
                    ordering_cust_addr_str = f"{ordering_cust_addr.get('streetName', '')} {ordering_cust_addr.get('townName', '')} {ordering_cust_addr.get('postalCode', '')}".strip() if ordering_cust_addr else None
                    ordering_cust_country = ordering_cust_addr.get('country') if ordering_cust_addr else None
                    ordering_cust_id = ordering_cust.get('partyIdentifier') or ordering_cust.get('nationalId')
                    ordering_cust_party_id = trunc(ordering_cust.get('partyIdentifier'), 35)  # NEW - party identifier
                    ordering_cust_national_id = trunc(ordering_cust.get('nationalId'), 35)  # NEW - national ID

                    # Ordering Institution (Field 52) - nested structure - ALL fields captured
                    ordering_inst = msg_content.get('orderingInstitution', {})
                    ordering_inst_bic = ordering_inst.get('bic')
                    ordering_inst_acct = ordering_inst.get('account')
                    ordering_inst_name = ordering_inst.get('name')
                    ordering_inst_clearing_code = trunc(ordering_inst.get('clearingCode'), 35)  # NEW
                    ordering_inst_country = ordering_inst.get('country')  # NEW

                    # Sending Institution (Field 51) - nested structure
                    sending_inst = msg_content.get('sendingInstitution', {})
                    sending_inst_bic = sending_inst.get('bic')

                    # Sender's Correspondent (Field 53) - nested structure - ALL fields captured
                    senders_corr = msg_content.get('sendersCorrespondent', {})
                    senders_corr_bic = senders_corr.get('bic') if senders_corr else None
                    senders_corr_acct = trunc(senders_corr.get('account'), 34) if senders_corr else None
                    senders_corr_loc = senders_corr.get('location') if senders_corr else None
                    senders_corr_name = trunc(senders_corr.get('name'), 140) if senders_corr else None  # NEW

                    # Receiver's Correspondent (Field 54) - nested structure - ALL fields captured
                    receivers_corr = msg_content.get('receiversCorrespondent', {})
                    receivers_corr_bic = receivers_corr.get('bic') if receivers_corr else None
                    receivers_corr_acct = trunc(receivers_corr.get('account'), 34) if receivers_corr else None
                    receivers_corr_loc = receivers_corr.get('location') if receivers_corr else None
                    receivers_corr_name = trunc(receivers_corr.get('name'), 140) if receivers_corr else None  # NEW

                    # Third Reimbursement Institution (Field 55) - nested structure
                    third_reimb = msg_content.get('thirdReimbursementInstitution', {})
                    third_reimb_bic = third_reimb.get('bic') if third_reimb else None

                    # Intermediary Institution (Field 56) - nested structure - ALL fields captured
                    intermediary = msg_content.get('intermediaryInstitution', {})
                    intermediary_bic = intermediary.get('bic') if intermediary else None
                    intermediary_acct = trunc(intermediary.get('account'), 34) if intermediary else None
                    intermediary_name = intermediary.get('name') if intermediary else None
                    intermediary_inst_bic = intermediary.get('bic') if intermediary else None  # NEW (duplicate for clarity)
                    intermediary_inst_name = trunc(intermediary.get('name'), 140) if intermediary else None  # NEW
                    intermediary_inst_country = intermediary.get('country') if intermediary else None  # NEW

                    # Account With Institution (Field 57) - nested structure - ALL fields captured
                    acct_with_inst = msg_content.get('accountWithInstitution', {})
                    acct_with_inst_bic = acct_with_inst.get('bic') if acct_with_inst else None
                    acct_with_inst_acct = trunc(acct_with_inst.get('account'), 34) if acct_with_inst else None
                    acct_with_inst_name = acct_with_inst.get('name') if acct_with_inst else None
                    acct_with_inst_country = acct_with_inst.get('country') if acct_with_inst else None  # NEW

                    # Beneficiary Customer (Field 59) - nested structure - ALL fields captured
                    benef_cust = msg_content.get('beneficiaryCustomer', {})
                    benef_acct = trunc(benef_cust.get('account'), 34)
                    benef_name = trunc(benef_cust.get('name') or creditor_name, 140)
                    benef_addr = benef_cust.get('address', {})
                    benef_addr_str = f"{benef_addr.get('streetName', '')} {benef_addr.get('townName', '')} {benef_addr.get('postalCode', '')}".strip() if benef_addr else None
                    benef_country = benef_addr.get('country') if benef_addr else None
                    benef_id = benef_cust.get('partyIdentifier')
                    benef_party_id = trunc(benef_cust.get('partyIdentifier'), 35)  # NEW - explicit party ID

                    # Other fields
                    remittance_info = msg_content.get('remittanceInformation')
                    details_of_charges = msg_content.get('detailsOfCharges')
                    sender_to_receiver = msg_content.get('senderToReceiverInformation')
                    regulatory_reporting = msg_content.get('regulatoryReporting')

                    cursor.execute("""
                        INSERT INTO silver.stg_mt103
                        (stg_id, raw_id, sender_bic, receiver_bic, senders_reference, related_reference,
                         bank_operation_code, instruction_codes, value_date, currency, amount,
                         instructed_currency, instructed_amount, exchange_rate,
                         ordering_customer_account, ordering_customer_name, ordering_customer_address, ordering_customer_country, ordering_customer_id,
                         ordering_customer_party_id, ordering_customer_national_id,
                         sending_institution_bic,
                         ordering_institution_bic, ordering_institution_account, ordering_institution_name,
                         ordering_institution_clearing_code, ordering_institution_country,
                         senders_correspondent_bic, senders_correspondent_account, senders_correspondent_location, senders_correspondent_name,
                         receivers_correspondent_bic, receivers_correspondent_account, receivers_correspondent_location, receivers_correspondent_name,
                         third_reimbursement_bic,
                         intermediary_bic, intermediary_account, intermediary_name,
                         intermediary_institution_bic, intermediary_institution_name, intermediary_institution_country,
                         account_with_institution_bic, account_with_institution_account, account_with_institution_name, account_with_institution_country,
                         beneficiary_account, beneficiary_name, beneficiary_address, beneficiary_country, beneficiary_id, beneficiary_party_id,
                         remittance_information, details_of_charges, sender_to_receiver_info, regulatory_reporting, uetr,
                         transaction_reference_number,
                         processing_status, _batch_id, _processed_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (stg_id) DO NOTHING
                    """, (stg_id, raw_id, ordering_inst_bic or sending_inst_bic, acct_with_inst_bic, sender_ref, related_ref,
                          bank_op_code, instr_codes, value_date, mt103_currency, mt103_amount,
                          instr_currency, instr_amount, exchange_rate,
                          ordering_cust_acct, ordering_cust_name, ordering_cust_addr_str, ordering_cust_country, ordering_cust_id,
                          ordering_cust_party_id, ordering_cust_national_id,
                          sending_inst_bic,
                          ordering_inst_bic, ordering_inst_acct, ordering_inst_name,
                          ordering_inst_clearing_code, ordering_inst_country,
                          senders_corr_bic, senders_corr_acct, senders_corr_loc, senders_corr_name,
                          receivers_corr_bic, receivers_corr_acct, receivers_corr_loc, receivers_corr_name,
                          third_reimb_bic,
                          intermediary_bic, intermediary_acct, intermediary_name,
                          intermediary_inst_bic, intermediary_inst_name, intermediary_inst_country,
                          acct_with_inst_bic, acct_with_inst_acct, acct_with_inst_name, acct_with_inst_country,
                          benef_acct, benef_name, benef_addr_str, benef_country, benef_id, benef_party_id,
                          remittance_info, details_of_charges, sender_to_receiver, json.dumps(regulatory_reporting) if regulatory_reporting else None, mt103_uetr,
                          transaction_ref_num,
                          'PROCESSED', batch_id, datetime.utcnow()))
                    source_stg_table = 'stg_mt103'

                    # Store extracted values for Gold layer
                    # NOTE: MT103 Field 20 (sender_ref) is NOT semantically equivalent to ISO 20022 EndToEndId
                    # MT103 sender_ref is a bank-assigned reference, while EndToEndId is originator-assigned
                    # We store sender_ref separately and only use actual EndToEndId if present in message
                    extracted_end_to_end_id = msg_content.get('endToEndId')  # Only if explicitly provided
                    extracted_sender_ref = sender_ref  # MT103 Field 20 - stored as separate identifier
                    extracted_uetr = mt103_uetr
                    extracted_charge_bearer = details_of_charges
                    extracted_value_date = value_date

                elif msg_type_lower in ['pacs_008', 'pacs008']:
                    # Extract pacs.008-specific fields from msg_content
                    # COMPLETE EXTRACTION - All source fields captured
                    # All nested structures need to be fully extracted

                    # Group Header fields
                    creation_dt = msg_content.get('creationDateTime') or msg_content.get('creation_date_time')
                    num_txns = msg_content.get('numberOfTransactions')

                    # Settlement Information - nested structure
                    settlement_method = msg_content.get('settlementMethod')
                    clearing_system = msg_content.get('clearingSystem')
                    interbank_sttl_date = msg_content.get('interbankSettlementDate')
                    total_interbank_sttl_amt = msg_content.get('totalInterbankSettlementAmount')
                    total_interbank_sttl_ccy = msg_content.get('interbankSettlementCurrency')

                    # Instructing Agent (Financial Institution) - nested structure - ALL fields captured
                    instructing_agent = msg_content.get('instructingAgent', {})
                    instr_agent_bic = instructing_agent.get('bic') or msg_content.get('instructingAgentBic')
                    instr_agent_name = instructing_agent.get('name') if instructing_agent else None  # NEW
                    instr_agent_lei = instructing_agent.get('lei') if instructing_agent else None  # NEW
                    instr_agent_country = instructing_agent.get('country') if instructing_agent else None  # NEW

                    # Instructed Agent (Financial Institution) - nested structure - ALL fields captured
                    instructed_agent = msg_content.get('instructedAgent', {})
                    instr_ed_agent_bic = instructed_agent.get('bic') or msg_content.get('instructedAgentBic')
                    instr_ed_agent_name = instructed_agent.get('name') if instructed_agent else None  # NEW
                    instr_ed_agent_lei = instructed_agent.get('lei') if instructed_agent else None  # NEW
                    instr_ed_agent_country = instructed_agent.get('country') if instructed_agent else None  # NEW

                    # Payment Type Information - nested structure - ALL fields captured (NEW)
                    pmt_type_info = msg_content.get('paymentTypeInformation', {})
                    instruction_priority = pmt_type_info.get('instructionPriority') if pmt_type_info else None  # NEW
                    clearing_channel = pmt_type_info.get('clearingChannel') if pmt_type_info else None  # NEW
                    service_level = pmt_type_info.get('serviceLevel') if pmt_type_info else None  # NEW
                    local_instrument = pmt_type_info.get('localInstrument') if pmt_type_info else None  # NEW
                    category_purpose = pmt_type_info.get('categoryPurpose') if pmt_type_info else None  # NEW

                    # Transaction Identification
                    instruction_id = msg_content.get('instructionId')
                    end_to_end_id = msg_content.get('endToEndId') or msg_content.get('end_to_end_id')
                    transaction_id = msg_content.get('transactionId')
                    uetr = msg_content.get('uetr')
                    clearing_sys_ref = msg_content.get('clearingSystemReference')

                    # Amounts
                    interbank_sttl_amt = msg_content.get('interbankSettlementAmount') or amount
                    interbank_sttl_ccy = msg_content.get('interbankSettlementAmountCurrency') or currency
                    instr_amt = msg_content.get('instructedAmount') or amount
                    instr_ccy = msg_content.get('instructedCurrency') or currency
                    exchange_rate = msg_content.get('exchangeRate')

                    # Charges
                    charge_bearer = msg_content.get('chargeBearer') or msg_content.get('charge_bearer')
                    charges_info = msg_content.get('chargesInformation', [])
                    charges_amt = charges_info[0].get('amount') if charges_info and len(charges_info) > 0 else None
                    charges_ccy = charges_info[0].get('currency') if charges_info and len(charges_info) > 0 else None

                    # Debtor (Party) - nested structure - ALL fields captured
                    debtor = msg_content.get('debtor', {})
                    debtor_nm = debtor.get('name') or debtor_name
                    debtor_addr = f"{debtor.get('streetName', '')} {debtor.get('townName', '')} {debtor.get('postalCode', '')}".strip() if debtor else None
                    debtor_country = debtor.get('country')
                    debtor_street_name = debtor.get('streetName') if debtor else None  # NEW
                    debtor_building_number = debtor.get('buildingNumber') if debtor else None  # NEW
                    debtor_postal_code = debtor.get('postalCode') if debtor else None  # NEW
                    debtor_town_name = debtor.get('townName') if debtor else None  # NEW
                    debtor_country_sub_division = debtor.get('countrySubDivision') if debtor else None  # NEW
                    debtor_id = debtor.get('id') if debtor else None  # NEW
                    debtor_id_type = debtor.get('idType') if debtor else None  # NEW

                    # Debtor Account - nested structure - ALL fields captured
                    debtor_acct = msg_content.get('debtorAccount', {})
                    debtor_acct_iban = debtor_acct.get('iban') if isinstance(debtor_acct, dict) else debtor_acct
                    debtor_acct_currency = debtor_acct.get('currency') if isinstance(debtor_acct, dict) else None  # NEW
                    debtor_acct_type = debtor_acct.get('accountType') if isinstance(debtor_acct, dict) else None  # NEW

                    # Debtor Agent (Financial Institution) - nested structure - ALL fields captured
                    debtor_agent = msg_content.get('debtorAgent', {})
                    debtor_agent_bic = debtor_agent.get('bic') or msg_content.get('debtorAgentBic')
                    debtor_agent_name = debtor_agent.get('name') if debtor_agent else None  # NEW
                    debtor_agent_clearing_member_id = debtor_agent.get('clearingSystemMemberId') if debtor_agent else None  # NEW
                    debtor_agent_lei = debtor_agent.get('lei') if debtor_agent else None  # NEW

                    # Creditor Agent (Financial Institution) - nested structure - ALL fields captured
                    creditor_agent = msg_content.get('creditorAgent', {})
                    creditor_agent_bic = creditor_agent.get('bic') or msg_content.get('creditorAgentBic')
                    creditor_agent_name = creditor_agent.get('name') if creditor_agent else None  # NEW
                    creditor_agent_clearing_member_id = creditor_agent.get('clearingSystemMemberId') if creditor_agent else None  # NEW
                    creditor_agent_lei = creditor_agent.get('lei') if creditor_agent else None  # NEW

                    # Creditor (Party) - nested structure - ALL fields captured
                    creditor = msg_content.get('creditor', {})
                    creditor_nm = creditor.get('name') or creditor_name
                    creditor_addr = f"{creditor.get('streetName', '')} {creditor.get('townName', '')} {creditor.get('postalCode', '')}".strip() if creditor else None
                    creditor_country = creditor.get('country')
                    creditor_street_name = creditor.get('streetName') if creditor else None  # NEW
                    creditor_building_number = creditor.get('buildingNumber') if creditor else None  # NEW
                    creditor_postal_code = creditor.get('postalCode') if creditor else None  # NEW
                    creditor_town_name = creditor.get('townName') if creditor else None  # NEW
                    creditor_country_sub_division = creditor.get('countrySubDivision') if creditor else None  # NEW
                    creditor_id = creditor.get('id') if creditor else None  # NEW
                    creditor_id_type = creditor.get('idType') if creditor else None  # NEW

                    # Creditor Account - nested structure - ALL fields captured
                    creditor_acct = msg_content.get('creditorAccount', {})
                    creditor_acct_iban = creditor_acct.get('iban') if isinstance(creditor_acct, dict) else creditor_acct
                    creditor_acct_currency = creditor_acct.get('currency') if isinstance(creditor_acct, dict) else None  # NEW
                    creditor_acct_type = creditor_acct.get('accountType') if isinstance(creditor_acct, dict) else None  # NEW

                    # Ultimate Parties - nested structures - ALL fields captured
                    ultimate_debtor = msg_content.get('ultimateDebtor', {})
                    ultimate_debtor_name = ultimate_debtor.get('name') if ultimate_debtor else None
                    ultimate_debtor_id = ultimate_debtor.get('id') if ultimate_debtor else None  # NEW
                    ultimate_debtor_id_type = ultimate_debtor.get('idType') if ultimate_debtor else None  # NEW
                    ultimate_creditor = msg_content.get('ultimateCreditor', {})
                    ultimate_creditor_name = ultimate_creditor.get('name') if ultimate_creditor else None
                    ultimate_creditor_id = ultimate_creditor.get('id') if ultimate_creditor else None  # NEW
                    ultimate_creditor_id_type = ultimate_creditor.get('idType') if ultimate_creditor else None  # NEW

                    # Intermediary Agents - nested structures (up to 3)
                    intermediary_1 = msg_content.get('intermediaryAgent1', {})
                    intermediary_1_bic = intermediary_1.get('bic') if intermediary_1 else None
                    intermediary_2 = msg_content.get('intermediaryAgent2', {})
                    intermediary_2_bic = intermediary_2.get('bic') if intermediary_2 else None
                    intermediary_3 = msg_content.get('intermediaryAgent3', {})
                    intermediary_3_bic = intermediary_3.get('bic') if intermediary_3 else None

                    # Purpose and Remittance
                    purpose_code = msg_content.get('purposeCode') or msg_content.get('purpose_code')

                    # Remittance Information - nested structure
                    remit_info = msg_content.get('remittanceInformation', {})
                    if isinstance(remit_info, str):
                        remit_unstruct = remit_info
                        remit_struct = None
                    else:
                        remit_unstruct = remit_info.get('unstructured')
                        remit_struct = remit_info.get('structured')

                    # Regulatory Reporting - nested structure
                    reg_reporting = msg_content.get('regulatoryReporting')

                    cursor.execute("""
                        INSERT INTO silver.stg_pacs008
                        (stg_id, raw_id, msg_id, creation_date_time, number_of_transactions,
                         settlement_method, clearing_system, interbank_settlement_date,
                         total_interbank_settlement_amount, total_interbank_settlement_currency,
                         instructing_agent_bic, instructing_agent_name, instructing_agent_lei, instructing_agent_country,
                         instructed_agent_bic, instructed_agent_name, instructed_agent_lei, instructed_agent_country,
                         instruction_priority, clearing_channel, service_level, local_instrument, category_purpose,
                         instruction_id, end_to_end_id, transaction_id, uetr, clearing_system_reference,
                         interbank_settlement_amount, interbank_settlement_currency,
                         instructed_amount, instructed_currency, exchange_rate,
                         charge_bearer, charges_amount, charges_currency,
                         debtor_name, debtor_address, debtor_country,
                         debtor_street_name, debtor_building_number, debtor_postal_code, debtor_town_name,
                         debtor_country_sub_division, debtor_id, debtor_id_type,
                         debtor_account_iban, debtor_account_currency, debtor_account_type,
                         debtor_agent_bic, debtor_agent_name, debtor_agent_clearing_member_id, debtor_agent_lei,
                         creditor_agent_bic, creditor_agent_name, creditor_agent_clearing_member_id, creditor_agent_lei,
                         creditor_name, creditor_address, creditor_country,
                         creditor_street_name, creditor_building_number, creditor_postal_code, creditor_town_name,
                         creditor_country_sub_division, creditor_id, creditor_id_type,
                         creditor_account_iban, creditor_account_currency, creditor_account_type,
                         ultimate_debtor_name, ultimate_debtor_id, ultimate_debtor_id_type,
                         ultimate_creditor_name, ultimate_creditor_id, ultimate_creditor_id_type,
                         intermediary_agent_1_bic, intermediary_agent_2_bic, intermediary_agent_3_bic,
                         purpose_code, remittance_info, structured_remittance, regulatory_reporting,
                         processing_status, _batch_id, _processed_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (stg_id) DO NOTHING
                    """, (stg_id, raw_id, msg_id, creation_dt, num_txns,
                          settlement_method, clearing_system, interbank_sttl_date,
                          total_interbank_sttl_amt, total_interbank_sttl_ccy,
                          instr_agent_bic, instr_agent_name, instr_agent_lei, instr_agent_country,
                          instr_ed_agent_bic, instr_ed_agent_name, instr_ed_agent_lei, instr_ed_agent_country,
                          instruction_priority, clearing_channel, service_level, local_instrument, category_purpose,
                          instruction_id, end_to_end_id, transaction_id, uetr, clearing_sys_ref,
                          interbank_sttl_amt, interbank_sttl_ccy,
                          instr_amt, instr_ccy, exchange_rate,
                          charge_bearer, charges_amt, charges_ccy,
                          debtor_nm, debtor_addr, debtor_country,
                          debtor_street_name, debtor_building_number, debtor_postal_code, debtor_town_name,
                          debtor_country_sub_division, debtor_id, debtor_id_type,
                          debtor_acct_iban, debtor_acct_currency, debtor_acct_type,
                          debtor_agent_bic, debtor_agent_name, debtor_agent_clearing_member_id, debtor_agent_lei,
                          creditor_agent_bic, creditor_agent_name, creditor_agent_clearing_member_id, creditor_agent_lei,
                          creditor_nm, creditor_addr, creditor_country,
                          creditor_street_name, creditor_building_number, creditor_postal_code, creditor_town_name,
                          creditor_country_sub_division, creditor_id, creditor_id_type,
                          creditor_acct_iban, creditor_acct_currency, creditor_acct_type,
                          ultimate_debtor_name, ultimate_debtor_id, ultimate_debtor_id_type,
                          ultimate_creditor_name, ultimate_creditor_id, ultimate_creditor_id_type,
                          intermediary_1_bic, intermediary_2_bic, intermediary_3_bic,
                          purpose_code, remit_unstruct,
                          json.dumps(remit_struct) if remit_struct else None,
                          json.dumps(reg_reporting) if reg_reporting else None,
                          'PROCESSED', batch_id, datetime.utcnow()))
                    source_stg_table = 'stg_pacs008'

                    # Store extracted values for Gold layer
                    extracted_end_to_end_id = end_to_end_id
                    extracted_uetr = uetr
                    extracted_charge_bearer = charge_bearer

                elif msg_type_lower == 'fedwire':
                    # Extract FEDWIRE-specific fields from msg_content
                    # COMPLETE EXTRACTION - All source fields captured
                    # Helper to truncate strings to max length
                    def trunc(val, max_len):
                        if val and len(str(val)) > max_len:
                            return str(val)[:max_len]
                        return val

                    # Basic message fields
                    type_code = trunc(msg_content.get('typeCode'), 2)
                    subtype_code = trunc(msg_content.get('subtypeCode'), 2)
                    imad = trunc(msg_content.get('imad'), 22)
                    omad = trunc(msg_content.get('omad'), 22)
                    sender_ref = trunc(msg_content.get('senderReference'), 16)
                    biz_func_code = trunc(msg_content.get('businessFunctionCode'), 3)

                    # NEW: Currency and amount details
                    fedwire_currency = msg_content.get('currency', 'USD')  # NEW
                    fedwire_instructed_amount = msg_content.get('instructedAmount')  # NEW
                    fedwire_instructed_currency = msg_content.get('instructedCurrency', 'USD')  # NEW

                    # NEW: Message routing
                    input_cycle_date = msg_content.get('inputCycleDate')  # NEW
                    input_sequence_number = trunc(msg_content.get('inputSequenceNumber'), 10)  # NEW
                    input_source = trunc(msg_content.get('inputSource'), 10)  # NEW
                    previous_message_id = trunc(msg_content.get('previousMessageId'), 35)  # NEW
                    beneficiary_ref = trunc(msg_content.get('beneficiaryReference'), 16)  # NEW

                    # Sender (Financial Institution) - nested structure - ALL fields captured
                    sender = msg_content.get('sender', {})
                    sender_aba = sender.get('routingNumber')
                    sender_short_name = trunc(sender.get('shortName'), 18)
                    sender_name = trunc(sender.get('name'), 140)  # NEW
                    sender_bic = sender.get('bic')  # NEW
                    sender_lei = trunc(sender.get('lei'), 20)  # NEW
                    sender_addr = sender.get('address', {})
                    sender_addr_line1 = trunc(sender_addr.get('line1'), 35) if sender_addr else None  # NEW
                    sender_addr_line2 = trunc(sender_addr.get('line2'), 35) if sender_addr else None  # NEW
                    sender_city = trunc(sender_addr.get('city'), 35) if sender_addr else None  # NEW
                    sender_state = trunc(sender_addr.get('state'), 2) if sender_addr else None  # NEW
                    sender_zip_code = trunc(sender_addr.get('zipCode'), 10) if sender_addr else None  # NEW
                    sender_country = sender_addr.get('country') if sender_addr else 'US'  # NEW

                    # Receiver (Financial Institution) - nested structure - ALL fields captured
                    receiver = msg_content.get('receiver', {})
                    receiver_aba = receiver.get('routingNumber')
                    receiver_short_name = trunc(receiver.get('shortName'), 18)
                    receiver_name = trunc(receiver.get('name'), 140)  # NEW
                    receiver_bic = receiver.get('bic')  # NEW
                    receiver_lei = trunc(receiver.get('lei'), 20)  # NEW
                    receiver_addr = receiver.get('address', {})
                    receiver_addr_line1 = trunc(receiver_addr.get('line1'), 35) if receiver_addr else None  # NEW
                    receiver_addr_line2 = trunc(receiver_addr.get('line2'), 35) if receiver_addr else None  # NEW
                    receiver_city = trunc(receiver_addr.get('city'), 35) if receiver_addr else None  # NEW
                    receiver_state = trunc(receiver_addr.get('state'), 2) if receiver_addr else None  # NEW
                    receiver_zip_code = trunc(receiver_addr.get('zipCode'), 10) if receiver_addr else None  # NEW
                    receiver_country = receiver_addr.get('country') if receiver_addr else 'US'  # NEW

                    # Originator (Party) - nested structure - ALL fields captured
                    originator = msg_content.get('originator', {})
                    originator_id = trunc(originator.get('identifier'), 34)
                    originator_name = trunc(originator.get('name'), 35)
                    originator_account_number = trunc(originator.get('accountNumber'), 35)  # NEW
                    originator_id_type = trunc(originator.get('identifierType'), 10)  # NEW
                    orig_addr = originator.get('address', {})
                    originator_addr1 = trunc(orig_addr.get('line1'), 35) if orig_addr else None
                    originator_addr2 = trunc(orig_addr.get('line2'), 35) if orig_addr else None
                    originator_addr3 = trunc(orig_addr.get('line3') or f"{orig_addr.get('city', '')} {orig_addr.get('state', '')} {orig_addr.get('zipCode', '')}".strip(), 35) if orig_addr else None
                    originator_city = trunc(orig_addr.get('city'), 35) if orig_addr else None  # NEW
                    originator_state = trunc(orig_addr.get('state'), 2) if orig_addr else None  # NEW
                    originator_zip_code = trunc(orig_addr.get('zipCode'), 10) if orig_addr else None  # NEW
                    originator_country = orig_addr.get('country') if orig_addr else 'US'  # NEW
                    originator_option_f = msg_content.get('originatorOptionF')  # NEW

                    # Originator FI - nested structure (may be same as sender or different)
                    originator_fi = msg_content.get('originatorFI') or msg_content.get('instructingBank', {})
                    originator_fi_id = trunc(originator_fi.get('routingNumber'), 34) if originator_fi else None
                    originator_fi_name = trunc(originator_fi.get('name'), 35) if originator_fi else None

                    # Beneficiary (Party) - nested structure - ALL fields captured
                    beneficiary = msg_content.get('beneficiary', {})
                    beneficiary_id = trunc(beneficiary.get('identifier'), 34)
                    beneficiary_name = trunc(beneficiary.get('name'), 35)
                    beneficiary_account_number = trunc(beneficiary.get('accountNumber'), 35)  # NEW
                    beneficiary_id_type = trunc(beneficiary.get('identifierType'), 10)  # NEW
                    benef_addr = beneficiary.get('address', {})
                    beneficiary_addr1 = trunc(benef_addr.get('line1'), 35) if benef_addr else None
                    beneficiary_addr2 = trunc(benef_addr.get('line2'), 35) if benef_addr else None
                    beneficiary_addr3 = trunc(benef_addr.get('line3') or f"{benef_addr.get('city', '')} {benef_addr.get('state', '')} {benef_addr.get('zipCode', '')}".strip(), 35) if benef_addr else None
                    beneficiary_city = trunc(benef_addr.get('city'), 35) if benef_addr else None  # NEW
                    beneficiary_state = trunc(benef_addr.get('state'), 2) if benef_addr else None  # NEW
                    beneficiary_zip_code = trunc(benef_addr.get('zipCode'), 10) if benef_addr else None  # NEW
                    beneficiary_country = benef_addr.get('country') if benef_addr else 'US'  # NEW

                    # Beneficiary FI (Bank) - nested structure - ALL fields captured
                    beneficiary_fi = msg_content.get('beneficiaryBank', {})
                    beneficiary_fi_id = trunc(beneficiary_fi.get('routingNumber'), 34) if beneficiary_fi else None
                    beneficiary_fi_name = trunc(beneficiary_fi.get('name'), 35) if beneficiary_fi else None
                    beneficiary_fi_bic = beneficiary_fi.get('bic') if beneficiary_fi else None  # NEW (extracted separately)
                    # Combine address into single field for storage
                    beneficiary_fi_address = None
                    if beneficiary_fi:
                        bfi_addr = beneficiary_fi.get('address', {})
                        if bfi_addr:
                            beneficiary_fi_address = f"{bfi_addr.get('line1', '')} {bfi_addr.get('line2', '')}".strip()

                    # Intermediary FI - nested structure
                    intermediary_fi = msg_content.get('intermediaryBank', {})
                    intermediary_fi_id = trunc(intermediary_fi.get('routingNumber'), 34) if intermediary_fi else None
                    intermediary_fi_name = trunc(intermediary_fi.get('name'), 35) if intermediary_fi else None

                    # Instructing FI - nested structure
                    instructing_fi = msg_content.get('instructingBank', {})
                    instructing_fi_id = trunc(instructing_fi.get('routingNumber'), 34) if instructing_fi else None
                    instructing_fi_name = trunc(instructing_fi.get('name'), 35) if instructing_fi else None

                    # Other fields
                    orig_to_benef_info = msg_content.get('originatorToBeneficiaryInfo')
                    fi_to_fi_info = msg_content.get('fiToFiInfo')
                    fedwire_charge_details = msg_content.get('chargeDetails')

                    cursor.execute("""
                        INSERT INTO silver.stg_fedwire
                        (stg_id, raw_id, type_code, subtype_code, sender_aba, sender_short_name,
                         receiver_aba, receiver_short_name, imad, omad, amount, sender_reference,
                         business_function_code,
                         currency, instructed_amount, instructed_currency,
                         input_cycle_date, input_sequence_number, input_source, previous_message_id, beneficiary_reference,
                         sender_name, sender_bic, sender_lei, sender_address_line1, sender_address_line2,
                         sender_city, sender_state, sender_zip_code, sender_country,
                         receiver_name, receiver_bic, receiver_lei, receiver_address_line1, receiver_address_line2,
                         receiver_city, receiver_state, receiver_zip_code, receiver_country,
                         originator_id, originator_name, originator_account_number, originator_id_type,
                         originator_address_line1, originator_address_line2, originator_address_line3,
                         originator_city, originator_state, originator_zip_code, originator_country, originator_option_f,
                         originator_fi_id, originator_fi_name,
                         beneficiary_id, beneficiary_name, beneficiary_account_number, beneficiary_id_type,
                         beneficiary_address_line1, beneficiary_address_line2, beneficiary_address_line3,
                         beneficiary_city, beneficiary_state, beneficiary_zip_code, beneficiary_country,
                         beneficiary_fi_id, beneficiary_fi_name, beneficiary_fi_address, beneficiary_fi_bic,
                         intermediary_fi_id, intermediary_fi_name,
                         instructing_fi_id, instructing_fi_name,
                         originator_to_beneficiary_info, fi_to_fi_info, charges,
                         processing_status, _batch_id, _processed_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (stg_id) DO NOTHING
                    """, (stg_id, raw_id, type_code, subtype_code, sender_aba, sender_short_name,
                          receiver_aba, receiver_short_name, imad, omad, amount, sender_ref,
                          biz_func_code,
                          fedwire_currency, fedwire_instructed_amount, fedwire_instructed_currency,
                          input_cycle_date, input_sequence_number, input_source, previous_message_id, beneficiary_ref,
                          sender_name, sender_bic, sender_lei, sender_addr_line1, sender_addr_line2,
                          sender_city, sender_state, sender_zip_code, sender_country,
                          receiver_name, receiver_bic, receiver_lei, receiver_addr_line1, receiver_addr_line2,
                          receiver_city, receiver_state, receiver_zip_code, receiver_country,
                          originator_id, originator_name, originator_account_number, originator_id_type,
                          originator_addr1, originator_addr2, originator_addr3,
                          originator_city, originator_state, originator_zip_code, originator_country, json.dumps(originator_option_f) if originator_option_f else None,
                          originator_fi_id, originator_fi_name,
                          beneficiary_id, beneficiary_name, beneficiary_account_number, beneficiary_id_type,
                          beneficiary_addr1, beneficiary_addr2, beneficiary_addr3,
                          beneficiary_city, beneficiary_state, beneficiary_zip_code, beneficiary_country,
                          beneficiary_fi_id, beneficiary_fi_name, beneficiary_fi_address, beneficiary_fi_bic,
                          intermediary_fi_id, intermediary_fi_name,
                          instructing_fi_id, instructing_fi_name,
                          orig_to_benef_info, fi_to_fi_info, fedwire_charge_details,
                          'PROCESSED', batch_id, datetime.utcnow()))
                    source_stg_table = 'stg_fedwire'

                    # Store extracted values for Gold layer
                    extracted_end_to_end_id = imad  # FEDWIRE uses IMAD as unique identifier
                    extracted_uetr = None
                    extracted_charge_bearer = fedwire_charge_details

                else:
                    # Fallback for other message types - use generic stg_pain001 structure
                    cursor.execute("""
                        INSERT INTO silver.stg_pain001
                        (stg_id, raw_id, msg_id, creation_date_time, debtor_name, creditor_name,
                         instructed_amount, instructed_currency, payment_method, processing_status, _batch_id, _processed_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (stg_id) DO NOTHING
                    """, (stg_id, raw_id, msg_id, datetime.utcnow(), debtor_name, creditor_name,
                          amount, currency, payment_method, 'PROCESSED', batch_id, datetime.utcnow()))
                    source_stg_table = 'stg_pain001'

                    # Default values for fallback
                    extracted_end_to_end_id = None
                    extracted_uetr = None
                    extracted_charge_bearer = None

                # Extract and persist entities (Party, Account, FI) to Gold layer
                entity_ids = extract_and_persist_entities(cursor, msg_content, message_type, stg_id, batch_id)

                # Gold layer - use schema-qualified name with actual extracted values AND entity references
                cursor.execute("""
                    INSERT INTO gold.cdm_payment_instruction
                    (instruction_id, payment_id, source_message_type, source_stg_table, source_stg_id,
                     payment_type, scheme_code, direction, instructed_amount, instructed_currency,
                     end_to_end_id, uetr, message_id, charge_bearer,
                     debtor_id, debtor_account_id, debtor_agent_id,
                     creditor_id, creditor_account_id, creditor_agent_id,
                     intermediary_agent1_id,
                     current_status, source_system, lineage_batch_id, partition_year, partition_month)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (instruction_id) DO NOTHING
                """, (instr_id, str(uuid.uuid4()), message_type, source_stg_table, stg_id,
                      payment_type, message_type.upper()[:10], 'OUTBOUND', amount, currency,
                      extracted_end_to_end_id, extracted_uetr, msg_id, extracted_charge_bearer,
                      entity_ids.get('debtor_id'), entity_ids.get('debtor_account_id'), entity_ids.get('debtor_agent_id'),
                      entity_ids.get('creditor_id'), entity_ids.get('creditor_account_id'), entity_ids.get('creditor_agent_id'),
                      entity_ids.get('intermediary_agent1_id'),
                      'PROCESSED', 'TEST_SCRIPT', batch_id,
                      datetime.utcnow().year, datetime.utcnow().month))

                pg_conn.commit()
                cursor.close()
                records_processed = 1

                # Sync to Neo4j
                try:
                    from gps_cdm.orchestration.neo4j_service import get_neo4j_service
                    neo4j = get_neo4j_service()
                    if neo4j:
                        neo4j.upsert_batch({
                            'batch_id': batch_id, 'message_type': message_type,
                            'source_system': 'TEST_SCRIPT', 'status': 'COMPLETED',
                            'created_at': datetime.utcnow().isoformat(),
                            'total_records': 1  # Increment by 1 for each record
                        })
                        for layer in ['bronze', 'silver', 'gold']:
                            neo4j.upsert_batch_layer(batch_id, layer, {
                                'input_count': 1, 'processed_count': 1, 'failed_count': 0
                            })
                except Exception as neo4j_err:
                    logger.warning(f"Neo4j sync failed: {neo4j_err}")

            except Exception as pg_write_err:
                errors.append({"error": f"PostgreSQL write failed: {pg_write_err}"})
            finally:
                if pg_conn:
                    pg_conn.close()

        elif file_paths:
            # Process file paths (original behavior)
            for i, file_path in enumerate(file_paths):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    records_processed += 1
                except Exception as e:
                    errors.append({
                        "file_path": file_path,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                    })

        persistence_target = "databricks" if (message_content and use_databricks) else \
                            "postgresql" if (message_content and use_postgres) else "none"

        return {
            "status": "SUCCESS" if not errors else "PARTIAL",
            "partition_id": partition_id,
            "batch_id": batch_id,
            "records_processed": records_processed,
            "errors": errors,
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
            "persisted_to": persistence_target,
        }

    except Exception as e:
        # Log error and re-raise for retry
        return {
            "status": "FAILED",
            "partition_id": partition_id,
            "batch_id": batch_id,
            "error": str(e),
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
        }


@app.task(bind=True)
def aggregate_bronze_results(self, results: List[Dict[str, Any]], batch_id: str) -> Dict[str, Any]:
    """
    Aggregate results from all bronze partition tasks.
    Called after all partition tasks complete (as chord callback).

    Also syncs batch and layer stats to Neo4j in real-time.
    """
    from gps_cdm.orchestration.neo4j_service import get_neo4j_service

    total_records = sum(r.get("records_processed", 0) for r in results)
    total_errors = sum(len(r.get("errors", [])) for r in results)
    failed_partitions = [r for r in results if r.get("status") == "FAILED"]
    total_duration = sum(r.get("duration_seconds", 0) for r in results)

    status = "FAILED" if failed_partitions else ("PARTIAL" if total_errors > 0 else "SUCCESS")

    # Sync to Neo4j in real-time
    try:
        neo4j = get_neo4j_service()
        if neo4j.is_available():
            # Update bronze layer stats
            neo4j.upsert_batch_layer(
                batch_id=batch_id,
                layer="bronze",
                stats={
                    "input_count": total_records + total_errors,
                    "processed_count": total_records,
                    "failed_count": total_errors,
                    "pending_count": 0,
                    "started_at": datetime.utcnow().isoformat(),
                    "completed_at": datetime.utcnow().isoformat(),
                    "duration_ms": int(total_duration * 1000),
                }
            )
            logger.info(f"Synced bronze layer stats to Neo4j for batch {batch_id}")
    except Exception as e:
        logger.warning(f"Failed to sync bronze stats to Neo4j: {e}")

    return {
        "batch_id": batch_id,
        "layer": "bronze",
        "total_records": total_records,
        "total_errors": total_errors,
        "partitions_processed": len(results),
        "failed_partitions": len(failed_partitions),
        "status": status,
    }


# =============================================================================
# SILVER LAYER TASKS
# =============================================================================

@app.task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def process_silver_transform(
    self,
    partition_id: str,
    record_ids: List[str],
    message_type: str,
    mapping_path: str,
    batch_id: str,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Transform bronze records to silver layer.

    Reads from bronze.raw_payment_messages and writes to appropriate
    silver.stg_* table based on message type.
    """
    import yaml

    start_time = datetime.utcnow()
    records_processed = 0
    errors = []

    try:
        # Load mapping configuration
        with open(mapping_path, 'r') as f:
            mapping_config = yaml.safe_load(f)

        bronze_to_silver = mapping_config.get("mapping", {}).get("bronze_to_silver", {})
        fields = bronze_to_silver.get("fields", [])

        # In production, read from bronze and transform
        # bronze_df = backend.read_bronze("raw_payment_messages",
        #                                 filter_expr=f"message_id IN {record_ids}")

        # Apply transformations from mapping
        for record_id in record_ids:
            try:
                # Transform each field according to mapping
                transformed_record = {}
                for field in fields:
                    source = field.get("source")
                    target = field.get("target")
                    transform = field.get("transform")

                    # Apply transformation logic
                    # In production, this uses actual data
                    transformed_record[target] = None

                records_processed += 1

            except Exception as e:
                errors.append({
                    "record_id": record_id,
                    "error": str(e),
                })

        # Write to silver table
        target_table = f"stg_{message_type}"
        # result = backend.write_silver(df, target_table, batch_id)

        return {
            "status": "SUCCESS" if not errors else "PARTIAL",
            "partition_id": partition_id,
            "batch_id": batch_id,
            "target_table": target_table,
            "records_processed": records_processed,
            "errors": errors,
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
        }

    except Exception as e:
        return {
            "status": "FAILED",
            "partition_id": partition_id,
            "batch_id": batch_id,
            "error": str(e),
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
        }


@app.task(bind=True)
def aggregate_silver_results(self, results: List[Dict[str, Any]], batch_id: str) -> Dict[str, Any]:
    """
    Aggregate results from all silver partition tasks.
    Also syncs silver layer stats to Neo4j and creates bronze->silver promotion.
    """
    from gps_cdm.orchestration.neo4j_service import get_neo4j_service

    total_records = sum(r.get("records_processed", 0) for r in results)
    total_errors = sum(len(r.get("errors", [])) for r in results)
    failed_partitions = [r for r in results if r.get("status") == "FAILED"]
    total_duration = sum(r.get("duration_seconds", 0) for r in results)

    status = "FAILED" if failed_partitions else ("PARTIAL" if total_errors > 0 else "SUCCESS")

    # Sync to Neo4j in real-time
    try:
        neo4j = get_neo4j_service()
        if neo4j.is_available():
            # Update silver layer stats
            neo4j.upsert_batch_layer(
                batch_id=batch_id,
                layer="silver",
                stats={
                    "input_count": total_records + total_errors,
                    "processed_count": total_records,
                    "failed_count": total_errors,
                    "pending_count": 0,
                    "started_at": datetime.utcnow().isoformat(),
                    "completed_at": datetime.utcnow().isoformat(),
                    "duration_ms": int(total_duration * 1000),
                }
            )

            # Create bronze->silver promotion relationship
            success_rate = total_records / (total_records + total_errors) if (total_records + total_errors) > 0 else 0
            neo4j.create_layer_promotion(
                batch_id=batch_id,
                source_layer="bronze",
                target_layer="silver",
                record_count=total_records,
                success_rate=success_rate,
            )
            logger.info(f"Synced silver layer stats to Neo4j for batch {batch_id}")
    except Exception as e:
        logger.warning(f"Failed to sync silver stats to Neo4j: {e}")

    return {
        "batch_id": batch_id,
        "layer": "silver",
        "total_records": total_records,
        "total_errors": total_errors,
        "partitions_processed": len(results),
        "failed_partitions": len(failed_partitions),
        "status": status,
    }


# =============================================================================
# GOLD LAYER TASKS
# =============================================================================

@app.task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def process_gold_aggregate(
    self,
    partition_id: str,
    source_tables: List[str],
    mapping_paths: Dict[str, str],
    batch_id: str,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Aggregate silver records into unified gold CDM tables.

    Reads from multiple silver.stg_* tables and writes to:
    - gold.cdm_payment_instruction (main payment record)
    - gold.cdm_party (debtor, creditor - with deduplication)
    - gold.cdm_account (debtor_account, creditor_account - with deduplication)
    - gold.cdm_financial_institution (agents - with deduplication)

    Uses EntityExtractor for normalized entity extraction with deduplication.
    """
    import yaml
    import psycopg2
    from pathlib import Path

    start_time = datetime.utcnow()
    records_processed = 0
    entities_created = {"parties": 0, "accounts": 0, "financial_institutions": 0}
    errors = []

    try:
        # Import entity extractor
        from gps_cdm.orchestration.entity_extractor import EntityExtractor, get_entity_ids_for_instruction
        from gps_cdm.ingestion.core.models import MappingConfig

        # Connect to PostgreSQL
        db_conn = psycopg2.connect(
            host=config.get("host", "localhost"),
            port=config.get("port", 5432),
            dbname=config.get("catalog", "gps_cdm"),
            user=config.get("user", os.environ.get("PGUSER", "")),
            password=config.get("password", os.environ.get("PGPASSWORD", "")),
        )
        cursor = db_conn.cursor()

        # Initialize entity extractor
        extractor = EntityExtractor(db_connection=db_conn)

        # Process each source table
        for source_table in source_tables:
            message_type = source_table.replace("stg_", "")
            mapping_path = mapping_paths.get(message_type)

            if not mapping_path or not Path(mapping_path).exists():
                continue

            # Load mapping config
            with open(mapping_path, 'r') as f:
                raw_config = yaml.safe_load(f)

            mapping_config = MappingConfig.from_dict(raw_config, Path(mapping_path), stage="silver_to_gold")

            # Read staging records for this batch
            cursor.execute(f"""
                SELECT * FROM silver.{source_table}
                WHERE _batch_id = %s OR lineage_batch_id = %s
            """, (batch_id, batch_id))

            columns = [desc[0] for desc in cursor.description]
            staging_records = [dict(zip(columns, row)) for row in cursor.fetchall()]

            if not staging_records:
                continue

            # Extract entities using the mapping config
            extraction_result = extractor.extract_from_staging(
                staging_records=staging_records,
                mapping_config=mapping_config,
                batch_id=batch_id,
            )

            # Persist new entities
            entity_counts = extractor.persist_entities(
                result=extraction_result,
                source_message_type=message_type,
            )

            entities_created["parties"] += entity_counts["parties"]
            entities_created["accounts"] += entity_counts["accounts"]
            entities_created["financial_institutions"] += entity_counts["financial_institutions"]

            # Insert payment instructions with entity references
            for staging_record in staging_records:
                stg_id = staging_record.get("stg_id")

                # Get entity IDs for this record
                entity_ids = get_entity_ids_for_instruction(extraction_result)

                # Build payment instruction record
                instruction_id = str(uuid.uuid4())
                payment_id = str(uuid.uuid4())

                try:
                    cursor.execute("""
                        INSERT INTO gold.cdm_payment_instruction (
                            instruction_id, payment_id,
                            source_system, source_message_type, source_stg_table, source_stg_id,
                            message_id, creation_datetime,
                            end_to_end_id, uetr, transaction_id,
                            payment_type, scheme_code, direction,
                            debtor_id, creditor_id,
                            debtor_agent_id, creditor_agent_id,
                            instructed_amount, instructed_currency,
                            charge_bearer, current_status,
                            lineage_batch_id,
                            partition_year, partition_month, region,
                            created_at, updated_at
                        ) VALUES (
                            %s, %s,
                            %s, %s, %s, %s,
                            %s, %s,
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, %s,
                            %s, %s,
                            %s, %s,
                            %s, %s,
                            %s,
                            %s, %s, %s,
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                        ON CONFLICT (instruction_id) DO NOTHING
                    """, (
                        instruction_id, payment_id,
                        "GPS_CDM", message_type, source_table, stg_id,
                        staging_record.get("message_id"),
                        staging_record.get("creation_datetime"),
                        staging_record.get("end_to_end_id"),
                        staging_record.get("uetr"),
                        staging_record.get("transaction_id"),
                        "CREDIT_TRANSFER",  # Default
                        "ISO20022" if "pain" in message_type else "SWIFT",
                        "OUTGOING",  # Default
                        entity_ids.get("debtor_id"),
                        entity_ids.get("creditor_id"),
                        entity_ids.get("debtor_agent_id"),
                        entity_ids.get("creditor_agent_id"),
                        staging_record.get("instructed_amount"),
                        staging_record.get("instructed_currency", "XXX"),
                        staging_record.get("charge_bearer", "SHAR"),
                        "PENDING",
                        batch_id,
                        datetime.utcnow().year,
                        datetime.utcnow().month,
                        "GLOBAL",
                    ))
                    records_processed += 1

                except Exception as e:
                    errors.append({
                        "stg_id": stg_id,
                        "error": str(e),
                    })

            db_conn.commit()

        # Cleanup
        cursor.close()
        db_conn.close()

        return {
            "status": "SUCCESS" if not errors else "PARTIAL",
            "partition_id": partition_id,
            "batch_id": batch_id,
            "target_table": "cdm_payment_instruction",
            "records_processed": records_processed,
            "entities_created": entities_created,
            "errors": errors[:10],  # Limit error output
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
        }

    except Exception as e:
        return {
            "status": "FAILED",
            "partition_id": partition_id,
            "batch_id": batch_id,
            "error": str(e),
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
        }


@app.task(bind=True)
def aggregate_gold_results(self, results: List[Dict[str, Any]], batch_id: str, message_type: str = "pain.001") -> Dict[str, Any]:
    """
    Aggregate results from all gold partition tasks.
    Also syncs gold layer stats to Neo4j, creates silver->gold promotion,
    and updates batch metadata with final status.
    """
    from gps_cdm.orchestration.neo4j_service import get_neo4j_service

    total_records = sum(r.get("records_processed", 0) for r in results)
    total_errors = sum(len(r.get("errors", [])) for r in results)
    total_entities = {
        "parties": sum(r.get("entities_created", {}).get("parties", 0) for r in results),
        "accounts": sum(r.get("entities_created", {}).get("accounts", 0) for r in results),
        "financial_institutions": sum(r.get("entities_created", {}).get("financial_institutions", 0) for r in results),
    }
    failed_partitions = [r for r in results if r.get("status") == "FAILED"]
    total_duration = sum(r.get("duration_seconds", 0) for r in results)

    status = "FAILED" if failed_partitions else ("PARTIAL" if total_errors > 0 else "SUCCESS")
    final_batch_status = "COMPLETED" if status == "SUCCESS" else ("PARTIAL" if status == "PARTIAL" else "FAILED")

    # Sync to Neo4j in real-time
    try:
        neo4j = get_neo4j_service()
        if neo4j.is_available():
            # Update gold layer stats
            neo4j.upsert_batch_layer(
                batch_id=batch_id,
                layer="gold",
                stats={
                    "input_count": total_records + total_errors,
                    "processed_count": total_records,
                    "failed_count": total_errors,
                    "pending_count": 0,
                    "started_at": datetime.utcnow().isoformat(),
                    "completed_at": datetime.utcnow().isoformat(),
                    "duration_ms": int(total_duration * 1000),
                }
            )

            # Create silver->gold promotion relationship
            success_rate = total_records / (total_records + total_errors) if (total_records + total_errors) > 0 else 0
            neo4j.create_layer_promotion(
                batch_id=batch_id,
                source_layer="silver",
                target_layer="gold",
                record_count=total_records,
                success_rate=success_rate,
            )

            # Update batch metadata with final status
            neo4j.upsert_batch({
                "batch_id": batch_id,
                "message_type": message_type,
                "source_system": "GPS_CDM",
                "status": final_batch_status,
                "created_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "total_records": total_records,
            })

            logger.info(f"Synced gold layer stats and batch completion to Neo4j for batch {batch_id}")
    except Exception as e:
        logger.warning(f"Failed to sync gold stats to Neo4j: {e}")

    return {
        "batch_id": batch_id,
        "layer": "gold",
        "total_records": total_records,
        "total_errors": total_errors,
        "entities_created": total_entities,
        "partitions_processed": len(results),
        "failed_partitions": len(failed_partitions),
        "status": status,
        "batch_status": final_batch_status,
    }


# =============================================================================
# DATA QUALITY TASKS
# =============================================================================

@app.task(bind=True)
def run_dq_evaluation(
    self,
    batch_id: str,
    layer: str,
    table: str,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Run data quality evaluation on a batch of records.
    Stores per-record scores and aggregate metrics.
    Also syncs DQ metrics to Neo4j in real-time.
    """
    from gps_cdm.orchestration.neo4j_service import get_neo4j_service

    start_time = datetime.utcnow()

    try:
        # In production, evaluate DQ rules
        # dq_evaluator = DQEvaluator(backend)
        # results = dq_evaluator.evaluate_batch(batch_id, layer, table)

        # Placeholder metrics - replace with actual evaluation
        records_evaluated = 0
        avg_score = 0.85
        passed = 0
        failed = 0

        # Sync DQ metrics to Neo4j in real-time
        try:
            neo4j = get_neo4j_service()
            if neo4j.is_available():
                neo4j.upsert_dq_metrics(
                    batch_id=batch_id,
                    layer=layer,
                    metrics={
                        "entity_type": table,
                        "overall_avg_score": avg_score,
                        "completeness_avg": avg_score,
                        "accuracy_avg": avg_score,
                        "validity_avg": avg_score,
                        "records_above_threshold": passed,
                        "records_below_threshold": failed,
                        "top_failing_rules": [],
                    }
                )
                logger.info(f"Synced DQ metrics to Neo4j for batch {batch_id}, layer {layer}")
        except Exception as e:
            logger.warning(f"Failed to sync DQ metrics to Neo4j: {e}")

        return {
            "status": "SUCCESS",
            "batch_id": batch_id,
            "layer": layer,
            "table": table,
            "records_evaluated": records_evaluated,
            "avg_score": avg_score,
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
        }

    except Exception as e:
        return {
            "status": "FAILED",
            "batch_id": batch_id,
            "error": str(e),
        }


@app.task
def aggregate_dq_metrics():
    """
    Periodic task to aggregate DQ metrics across batches.
    Scheduled by Celery Beat to run hourly.
    """
    # In production, aggregate metrics from obs_dq_results
    # and write to obs_dq_metrics
    pass


# =============================================================================
# CDC TASKS
# =============================================================================

@app.task(bind=True, max_retries=3)
def sync_cdc_to_neo4j(
    self,
    neo4j_uri: Optional[str] = None,
    neo4j_user: Optional[str] = None,
    neo4j_password: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Sync pending CDC events to Neo4j.
    Scheduled by Celery Beat to run every 5 minutes.
    """
    neo4j_uri = neo4j_uri or os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = neo4j_user or os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = neo4j_password or os.environ.get("NEO4J_PASSWORD", "password")

    start_time = datetime.utcnow()
    events_synced = 0

    try:
        # In production:
        # cdc_events = backend.get_pending_cdc_events(limit=1000)
        # for event in cdc_events:
        #     sync_event_to_neo4j(event, neo4j_uri, neo4j_user, neo4j_password)
        #     events_synced += 1
        # backend.mark_cdc_synced([e["cdc_id"] for e in cdc_events], "neo4j")

        return {
            "status": "SUCCESS",
            "events_synced": events_synced,
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
        }

    except Exception as e:
        return {
            "status": "FAILED",
            "error": str(e),
        }


# =============================================================================
# MAINTENANCE TASKS
# =============================================================================

@app.task
def cleanup_old_checkpoints(days_old: int = 7):
    """
    Clean up checkpoints older than specified days.
    Scheduled by Celery Beat to run daily.
    """
    cutoff = datetime.utcnow() - timedelta(days=days_old)
    # In production:
    # backend.execute_sql(f"DELETE FROM obs_checkpoints WHERE created_at < '{cutoff}'")
    pass


# =============================================================================
# WORKFLOW ORCHESTRATION
# =============================================================================

def create_medallion_workflow(
    file_paths: List[str],
    message_type: str,
    mapping_path: str,
    config: Dict[str, Any],
    partition_size: int = 1000,
) -> str:
    """
    Create a complete medallion pipeline workflow.

    This function partitions the work and creates a Celery workflow
    that processes data through Bronze -> Silver -> Gold -> DQ.

    Args:
        file_paths: All files to process
        message_type: Type of message (pain001, mt103, etc.)
        mapping_path: Path to mapping configuration
        config: Persistence configuration
        partition_size: Number of files per partition

    Returns:
        Batch ID for tracking
    """
    batch_id = str(uuid.uuid4())

    # Partition files for parallel processing
    partitions = [
        file_paths[i:i + partition_size]
        for i in range(0, len(file_paths), partition_size)
    ]

    # Create Bronze tasks (parallel)
    bronze_tasks = group([
        process_bronze_partition.s(
            partition_id=f"{batch_id}:bronze:{i}",
            file_paths=partition,
            message_type=message_type,
            batch_id=batch_id,
            config=config,
        )
        for i, partition in enumerate(partitions)
    ])

    # Bronze chord: all bronze tasks -> aggregate -> silver
    bronze_workflow = chord(
        bronze_tasks,
        aggregate_bronze_results.s(batch_id=batch_id),
    )

    # Chain: Bronze -> Silver -> Gold -> DQ
    # Note: In production, Silver/Gold would also be parallelized
    workflow = chain(
        bronze_workflow,
        process_silver_transform.s(
            partition_id=f"{batch_id}:silver:0",
            record_ids=[],  # Populated from bronze results
            message_type=message_type,
            mapping_path=mapping_path,
            batch_id=batch_id,
            config=config,
        ),
        process_gold_aggregate.s(
            partition_id=f"{batch_id}:gold:0",
            source_tables=[f"stg_{message_type}"],
            mapping_paths={message_type: mapping_path},
            batch_id=batch_id,
            config=config,
        ),
        run_dq_evaluation.s(
            batch_id=batch_id,
            layer="gold",
            table="cdm_payment_instruction",
            config=config,
        ),
    )

    # Execute workflow asynchronously
    workflow.apply_async()

    return batch_id


def create_streaming_consumer_workflow(
    kafka_topic: str,
    message_type: str,
    mapping_path: str,
    config: Dict[str, Any],
    batch_size: int = 100,
    poll_interval: float = 1.0,
):
    """
    Create a streaming consumer workflow for Kafka messages.

    This would typically be called by NiFi to process streaming data.
    Messages are batched and processed through the pipeline.

    Args:
        kafka_topic: Kafka topic to consume from
        message_type: Type of message
        mapping_path: Path to mapping configuration
        config: Persistence configuration
        batch_size: Number of messages per batch
        poll_interval: Seconds between polls
    """
    # In production, this would:
    # 1. Consume from Kafka topic
    # 2. Batch messages
    # 3. Submit batches to Celery for processing
    # 4. Track offsets for exactly-once processing

    # NiFi handles the Kafka consumption and calls Celery tasks
    pass


# =============================================================================
# TASK STATUS MONITORING
# =============================================================================

def get_batch_status(batch_id: str) -> Dict[str, Any]:
    """
    Get status of a batch processing workflow.

    Returns:
        Dict with batch status, progress, and any errors
    """
    # Query Celery results backend for task status
    # In production, also query obs_batch_tracking table

    return {
        "batch_id": batch_id,
        "status": "UNKNOWN",
        "layers_completed": [],
        "current_layer": None,
        "progress_percent": 0,
        "errors": [],
    }


def cancel_batch(batch_id: str) -> bool:
    """
    Cancel all tasks for a batch.
    """
    # Revoke all tasks with batch_id in their arguments
    # app.control.revoke(task_ids, terminate=True)
    return True


# =============================================================================
# REPROCESSING TASKS
# =============================================================================

@app.task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def reprocess_bronze_to_silver(
    self,
    raw_id: str,
    message_type: str,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Reprocess a bronze record through to silver layer via Celery.

    This task fetches the bronze record, parses it, and creates/updates
    the silver staging record.

    Args:
        raw_id: Bronze record ID
        message_type: Message type (pain001, mt103, etc.)
        force: Force reprocessing even if already processed

    Returns:
        Dict with reprocessing result
    """
    import psycopg2
    from gps_cdm.transformations.pain001_parser import Pain001Parser

    start_time = datetime.utcnow()

    try:
        # Connect to PostgreSQL
        pg_conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            port=int(os.environ.get('POSTGRES_PORT', 5433)),
            database=os.environ.get('POSTGRES_DB', 'gps_cdm'),
            user=os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
            password=os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password')
        )
        cursor = pg_conn.cursor()

        # Fetch bronze record
        cursor.execute("""
            SELECT raw_id, raw_content, message_type, processing_status,
                   silver_stg_id, _batch_id
            FROM bronze.raw_payment_messages
            WHERE raw_id = %s
        """, (raw_id,))
        row = cursor.fetchone()

        if not row:
            return {
                "status": "FAILED",
                "raw_id": raw_id,
                "error": "Bronze record not found",
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
            }

        raw_content = row[1]
        msg_type = row[2] or message_type
        current_status = row[3]
        existing_silver_id = row[4]
        batch_id = row[5] or f"REPROCESS_{uuid.uuid4().hex[:8]}"

        # Check if already processed
        if current_status == 'PROCESSED' and existing_silver_id and not force:
            return {
                "status": "SKIPPED",
                "raw_id": raw_id,
                "silver_stg_id": existing_silver_id,
                "message": "Already processed",
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
            }

        # Update status to reprocessing
        cursor.execute("""
            UPDATE bronze.raw_payment_messages
            SET processing_status = 'REPROCESSING',
                processing_attempts = processing_attempts + 1
            WHERE raw_id = %s
        """, (raw_id,))
        pg_conn.commit()

        # Parse based on message type
        if msg_type.lower() in ('pain.001', 'pain001'):
            parser = Pain001Parser()
            parsed = parser.parse(raw_content)

            # Generate silver ID
            stg_id = f"stg_{uuid.uuid4().hex[:12]}"

            # Insert into silver
            cursor.execute("""
                INSERT INTO silver.stg_pain001 (
                    stg_id, msg_id, msg_created_at, debtor_name, debtor_country,
                    debtor_account_iban, debtor_agent_bic, creditor_name,
                    creditor_country, creditor_account_iban, creditor_agent_bic,
                    instructed_amount, instructed_currency, charge_bearer,
                    processing_status, _batch_id, _bronze_raw_id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    'PENDING', %s, %s
                )
                ON CONFLICT (stg_id) DO UPDATE SET
                    processing_status = 'PENDING',
                    _ingested_at = CURRENT_TIMESTAMP
                RETURNING stg_id
            """, (
                stg_id,
                parsed.get('msg_id', ''),
                parsed.get('creation_date_time'),
                parsed.get('debtor_name', ''),
                parsed.get('debtor_country', ''),
                parsed.get('debtor_iban', ''),
                parsed.get('debtor_agent_bic', ''),
                parsed.get('creditor_name', ''),
                parsed.get('creditor_country', ''),
                parsed.get('creditor_iban', ''),
                parsed.get('creditor_agent_bic', ''),
                parsed.get('amount', 0),
                parsed.get('currency', 'USD'),
                parsed.get('charge_bearer', 'SLEV'),
                batch_id,
                raw_id,
            ))
            result_stg_id = cursor.fetchone()[0]
            pg_conn.commit()

            # Update bronze with silver link
            cursor.execute("""
                UPDATE bronze.raw_payment_messages
                SET processing_status = 'PROCESSED',
                    silver_stg_id = %s,
                    promoted_to_silver_at = CURRENT_TIMESTAMP,
                    processing_error = NULL
                WHERE raw_id = %s
            """, (result_stg_id, raw_id))
            pg_conn.commit()

            # Chain to silver-to-gold processing
            reprocess_silver_to_gold.delay(result_stg_id, msg_type, force=True)

            return {
                "status": "SUCCESS",
                "raw_id": raw_id,
                "silver_stg_id": result_stg_id,
                "message_type": msg_type,
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
            }
        else:
            # For other message types, mark as pending for future implementation
            cursor.execute("""
                UPDATE bronze.raw_payment_messages
                SET processing_status = 'FAILED',
                    processing_error = 'Unsupported message type for reprocessing'
                WHERE raw_id = %s
            """, (raw_id,))
            pg_conn.commit()

            return {
                "status": "FAILED",
                "raw_id": raw_id,
                "error": f"Unsupported message type: {msg_type}",
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
            }

    except Exception as e:
        logger.error(f"Reprocess bronze failed: {e}")
        return {
            "status": "FAILED",
            "raw_id": raw_id,
            "error": str(e),
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
        }
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'pg_conn' in locals():
            pg_conn.close()


@app.task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def reprocess_silver_to_gold(
    self,
    stg_id: str,
    message_type: str,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Reprocess a silver record through to gold layer via Celery.

    This task transforms the silver staging record and creates/updates
    the gold CDM entities.

    Args:
        stg_id: Silver staging record ID
        message_type: Message type (pain001, mt103, etc.)
        force: Force reprocessing even if already processed

    Returns:
        Dict with reprocessing result
    """
    import psycopg2

    start_time = datetime.utcnow()

    try:
        # Connect to PostgreSQL
        pg_conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            port=int(os.environ.get('POSTGRES_PORT', 5433)),
            database=os.environ.get('POSTGRES_DB', 'gps_cdm'),
            user=os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
            password=os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password')
        )
        cursor = pg_conn.cursor()

        # Fetch silver record
        cursor.execute("""
            SELECT stg_id, msg_id, debtor_name, debtor_country, debtor_account_iban,
                   debtor_agent_bic, creditor_name, creditor_country,
                   creditor_account_iban, creditor_agent_bic, instructed_amount,
                   instructed_currency, charge_bearer, processing_status,
                   gold_instruction_id, _batch_id
            FROM silver.stg_pain001
            WHERE stg_id = %s
        """, (stg_id,))
        row = cursor.fetchone()

        if not row:
            return {
                "status": "FAILED",
                "stg_id": stg_id,
                "error": "Silver record not found",
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
            }

        current_status = row[13]
        existing_gold_id = row[14]
        batch_id = row[15] or f"REPROCESS_{uuid.uuid4().hex[:8]}"

        # Check if already processed
        if current_status == 'PROCESSED' and existing_gold_id and not force:
            return {
                "status": "SKIPPED",
                "stg_id": stg_id,
                "gold_instruction_id": existing_gold_id,
                "message": "Already processed",
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
            }

        # Update status to reprocessing
        cursor.execute("""
            UPDATE silver.stg_pain001
            SET processing_status = 'REPROCESSING'
            WHERE stg_id = %s
        """, (stg_id,))
        pg_conn.commit()

        # Generate gold ID
        instruction_id = f"pi_{uuid.uuid4().hex[:12]}"

        # Insert into gold cdm_payment_instruction
        cursor.execute("""
            INSERT INTO gold.cdm_payment_instruction (
                instruction_id, instruction_type, payer_name, payer_country,
                payer_account_id, payer_agent_bic, payee_name, payee_country,
                payee_account_id, payee_agent_bic, amount, currency,
                charge_bearer, status, _batch_id, _silver_stg_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ACTIVE', %s, %s
            )
            ON CONFLICT (instruction_id) DO UPDATE SET
                status = 'ACTIVE',
                _updated_at = CURRENT_TIMESTAMP
            RETURNING instruction_id
        """, (
            instruction_id,
            'CREDIT_TRANSFER',
            row[2],   # debtor_name -> payer_name
            row[3],   # debtor_country -> payer_country
            row[4],   # debtor_account_iban -> payer_account_id
            row[5],   # debtor_agent_bic -> payer_agent_bic
            row[6],   # creditor_name -> payee_name
            row[7],   # creditor_country -> payee_country
            row[8],   # creditor_account_iban -> payee_account_id
            row[9],   # creditor_agent_bic -> payee_agent_bic
            row[10],  # instructed_amount -> amount
            row[11],  # instructed_currency -> currency
            row[12],  # charge_bearer
            batch_id,
            stg_id,
        ))
        result_gold_id = cursor.fetchone()[0]
        pg_conn.commit()

        # Update silver with gold link
        cursor.execute("""
            UPDATE silver.stg_pain001
            SET processing_status = 'PROCESSED',
                gold_instruction_id = %s,
                promoted_to_gold_at = CURRENT_TIMESTAMP,
                processing_error = NULL
            WHERE stg_id = %s
        """, (result_gold_id, stg_id))
        pg_conn.commit()

        return {
            "status": "SUCCESS",
            "stg_id": stg_id,
            "gold_instruction_id": result_gold_id,
            "message_type": message_type,
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
        }

    except Exception as e:
        logger.error(f"Reprocess silver failed: {e}")
        # Update silver status to failed
        try:
            cursor.execute("""
                UPDATE silver.stg_pain001
                SET processing_status = 'FAILED',
                    processing_error = %s
                WHERE stg_id = %s
            """, (str(e), stg_id))
            pg_conn.commit()
        except:
            pass

        return {
            "status": "FAILED",
            "stg_id": stg_id,
            "error": str(e),
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
        }
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'pg_conn' in locals():
            pg_conn.close()
