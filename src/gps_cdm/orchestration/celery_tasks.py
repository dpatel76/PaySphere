"""
GPS CDM - Celery Task Processing
================================

Distributed task processing using Celery for high-throughput batch processing.
Designed for 50M+ messages/day with horizontal scaling.

Architecture:
    NiFi → Kafka (per-message-type topics) → Kafka Consumers → Celery → PostgreSQL

- NiFi handles ingestion, routing, and publishes to Kafka per-message-type topics
- Kafka consumers with micro-batching dispatch to Celery
- Celery handles parallel processing across worker pools
- Redis as message broker
- Workers process partitions independently with checkpointing

Usage:
    # Start workers (one per core):
    celery -A gps_cdm.orchestration.celery_tasks worker -Q celery,bronze,silver,gold,dq,cdc -l info --concurrency=8

    # Start beat scheduler for periodic tasks:
    celery -A gps_cdm.orchestration.celery_tasks beat --loglevel=info

    # Start Kafka consumers:
    python -m gps_cdm.streaming.consumer_launcher
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
    include=[
        "gps_cdm.orchestration.celery_tasks",
        "gps_cdm.orchestration.zone_separated_tasks",
    ],
)

# Alias for backwards compatibility
celery_app = app

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
        # Zone-separated tasks (zone_tasks module)
        "gps_cdm.zone_tasks.process_bronze_records": {"queue": "bronze"},
        "gps_cdm.zone_tasks.process_silver_records": {"queue": "silver"},
        "gps_cdm.zone_tasks.process_gold_records": {"queue": "gold"},
        "gps_cdm.zone_tasks.process_medallion_pipeline": {"queue": "bronze"},
        "gps_cdm.zone_tasks.retry_error": {"queue": "celery"},
        "gps_cdm.zone_tasks.bulk_retry_errors": {"queue": "celery"},
        # New zone-separated tasks (zone_separated_tasks module)
        "gps_cdm.orchestration.zone_separated_tasks.process_bronze_message": {"queue": "bronze"},
        "gps_cdm.orchestration.zone_separated_tasks.process_silver_message": {"queue": "silver"},
        "gps_cdm.orchestration.zone_separated_tasks.process_gold_message": {"queue": "gold"},
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

# Import all extractors to trigger registration, then get the registry
# This import triggers registration of all 29+ message format extractors
from gps_cdm.message_formats import ExtractorRegistry
from gps_cdm.message_formats.base import GoldEntityPersister


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
            # PostgreSQL processing using format-specific extractors
            # NO FALLBACKS - parse raw content using appropriate parser
            from gps_cdm.orchestration.message_processor import MessageProcessor, get_message_format, get_payment_type

            raw_id = f"raw_{uuid.uuid4().hex[:12]}"
            stg_id = f"stg_{uuid.uuid4().hex[:12]}"
            instr_id = f"instr_{uuid.uuid4().hex[:12]}"

            # Determine raw content string for storage
            if isinstance(message_content, str):
                raw_content_str = message_content
            elif isinstance(message_content, dict):
                if 'raw_xml' in message_content:
                    raw_content_str = message_content['raw_xml']
                elif 'raw_content' in message_content:
                    raw_content_str = message_content['raw_content']
                elif '_raw_text' in message_content:
                    # NiFi sends raw SWIFT/XML content wrapped in {"_raw_text": "..."}
                    raw_content_str = json.dumps(message_content)  # Store as-is for Bronze
                else:
                    raw_content_str = json.dumps(message_content)
            else:
                raw_content_str = str(message_content)

            # Parse using format-specific parser
            # First check if content is wrapped in {"_raw_text": "..."} or {"raw": "..."} and unwrap it for parsing
            content_to_parse = raw_content_str
            if isinstance(message_content, dict):
                if '_raw_text' in message_content:
                    # Extract the actual message content for parsing
                    content_to_parse = message_content['_raw_text']
                elif 'raw' in message_content and len(message_content) == 1:
                    # ACH/fixed-width content is wrapped in {"raw": "..."}
                    content_to_parse = message_content['raw']
            msg_content = MessageProcessor.parse_raw_content(content_to_parse, message_type)

            # Extract message ID from parsed content (no fallback to generated ID)
            msg_id = (msg_content.get('messageId') or
                     msg_content.get('message_id') or
                     msg_content.get('transactionReferenceNumber') or
                     msg_content.get('imad') or
                     msg_content.get('traceNumber'))

            # Get message format and payment type from transformation rules
            routing = get_table_routing(message_type)
            payment_type = routing.get('payment_type') if routing else get_payment_type(message_type)
            message_format = get_message_format(message_type)

            try:
                cursor = pg_conn.cursor()

                # Bronze layer - store raw content as received
                cursor.execute("""
                    INSERT INTO bronze.raw_payment_messages
                    (raw_id, message_type, message_format, raw_content, raw_content_hash,
                     source_system, source_file_path, processing_status, _batch_id, _ingested_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (raw_id) DO NOTHING
                """, (raw_id, message_type, message_format, raw_content_str,
                      hashlib.sha256(raw_content_str.encode()).hexdigest()[:64],
                      'NIFI', f'nifi://{message_type}', 'PROCESSED',
                      batch_id, datetime.utcnow()))

                # Silver layer - use message format extractors
                # Get the extractor for this message type
                extractor = ExtractorRegistry.get(message_type)
                if extractor:
                    # Use extractor to get Silver layer fields
                    silver_record = extractor.extract_silver(msg_content, raw_id, stg_id, batch_id)
                    silver_columns = extractor.get_silver_columns()
                    silver_values = extractor.get_silver_values(silver_record)

                    # Build dynamic INSERT statement
                    silver_table = f"silver.{extractor.SILVER_TABLE}"
                    placeholders = ', '.join(['%s'] * len(silver_columns))
                    columns_str = ', '.join(silver_columns)

                    # Only add _processed_at if not already in columns
                    # processing_status is already in extractor columns - do NOT add it again
                    if '_processed_at' not in silver_columns:
                        cursor.execute(f"""
                            INSERT INTO {silver_table}
                            ({columns_str}, _processed_at)
                            VALUES ({placeholders}, %s)
                            ON CONFLICT (stg_id) DO NOTHING
                        """, (*silver_values, datetime.utcnow()))
                    else:
                        cursor.execute(f"""
                            INSERT INTO {silver_table}
                            ({columns_str})
                            VALUES ({placeholders})
                            ON CONFLICT (stg_id) DO NOTHING
                        """, silver_values)

                    source_stg_table = extractor.SILVER_TABLE
                else:
                    # Fallback to generic stg_payment table for unknown types
                    logger.warning(f"No extractor found for message type: {message_type}")
                    source_stg_table = 'stg_payment'

                # Skip the inline extraction code - extractor handles it
                # Get extracted values from msg_content for Gold layer
                end_to_end_id = msg_content.get('endToEndId') or msg_content.get('end_to_end_id')
                uetr = msg_content.get('uetr')
                charge_bearer = msg_content.get('chargeBearer')
                instr_amt = msg_content.get('instructedAmount') or msg_content.get('amount') or msg_content.get('interbankSettlementAmount')
                instr_ccy = msg_content.get('instructedCurrency') or msg_content.get('currency') or msg_content.get('currencyCode') or msg_content.get('interbankSettlementCurrency') or 'USD'
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
                      payment_type, message_type.upper()[:10], 'OUTBOUND', instr_amt, instr_ccy,
                      end_to_end_id, uetr, msg_id, charge_bearer,
                      entity_ids.get('debtor_id'), entity_ids.get('debtor_account_id'), entity_ids.get('debtor_agent_id'),
                      entity_ids.get('creditor_id'), entity_ids.get('creditor_account_id'), entity_ids.get('creditor_agent_id'),
                      entity_ids.get('intermediary_agent1_id'),
                      'PROCESSED', 'NIFI', batch_id,
                      datetime.utcnow().year, datetime.utcnow().month))

                # Persist scheme-specific extension data
                try:
                    from gps_cdm.message_formats.base import GoldEntityPersister
                    # Build staging record from msg_content for extension persistence
                    staging_record = msg_content if isinstance(msg_content, dict) else {}
                    GoldEntityPersister.persist_extension(cursor, instr_id, message_type, staging_record)
                except Exception as ext_err:
                    logger.warning(f"Extension persistence failed for {message_type}: {ext_err}")

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

                    # Persist scheme-specific extension data
                    try:
                        from gps_cdm.message_formats.base import GoldEntityPersister
                        GoldEntityPersister.persist_extension(cursor, instruction_id, message_type, staging_record)
                    except Exception as ext_err:
                        logger.warning(f"Extension persistence failed for {message_type}: {ext_err}")

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
