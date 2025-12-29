"""Eurozone TARGET2 (Trans-European Automated Real-time Gross Settlement Express Transfer) Extractor - ISO 20022 based."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
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


class Target2Extractor(BaseExtractor):
    """Extractor for Eurozone TARGET2 payment messages."""

    MESSAGE_TYPE = "TARGET2"
    SILVER_TABLE = "stg_target2"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw TARGET2 content."""
        msg_id = raw_content.get('msgId', '') or raw_content.get('endToEndId', '')
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
        """Extract all Silver layer fields from TARGET2 message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'TARGET2',
            'msg_id': trunc(msg_content.get('msgId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': msg_content.get('settlementDate'),
            'settlement_method': trunc(msg_content.get('settlementMethod'), 10),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'EUR',

            # Agents (BICs)
            'instructing_agent_bic': trunc(msg_content.get('instructingAgentBic'), 11),
            'instructed_agent_bic': trunc(msg_content.get('instructedAgentBic'), 11),
            'debtor_agent_bic': trunc(msg_content.get('debtorAgentBic'), 11),
            'creditor_agent_bic': trunc(msg_content.get('creditorAgentBic'), 11),

            # Transaction IDs
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'transaction_id': trunc(msg_content.get('transactionId'), 35),
            'uetr': msg_content.get('uetr'),

            # Debtor
            'debtor_name': trunc(msg_content.get('debtorName'), 140),
            'debtor_account': trunc(msg_content.get('debtorAccount'), 34),

            # Creditor
            'creditor_name': trunc(msg_content.get('creditorName'), 140),
            'creditor_account': trunc(msg_content.get('creditorAccount'), 34),

            # Payment Type
            'payment_type': trunc(msg_content.get('paymentType'), 10),
            'service_level': trunc(msg_content.get('serviceLevel'), 35),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'msg_id', 'creation_date_time',
            'settlement_date', 'settlement_method', 'amount', 'currency',
            'instructing_agent_bic', 'instructed_agent_bic',
            'debtor_agent_bic', 'creditor_agent_bic',
            'instruction_id', 'end_to_end_id', 'transaction_id', 'uetr',
            'debtor_name', 'debtor_account',
            'creditor_name', 'creditor_account',
            'payment_type', 'service_level',
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
        """Extract Gold layer entities from TARGET2 Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Debtor Party - uses Silver column names
        if silver_data.get('debtor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('debtor_name'),
                role="DEBTOR",
                party_type='UNKNOWN',
            ))

        # Creditor Party
        if silver_data.get('creditor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('creditor_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
            ))

        # Debtor Account
        if silver_data.get('debtor_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('debtor_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'EUR',
            ))

        # Creditor Account
        if silver_data.get('creditor_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('creditor_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'EUR',
            ))

        # Debtor Agent
        if silver_data.get('debtor_agent_bic') or silver_data.get('instructing_agent_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                bic=silver_data.get('debtor_agent_bic') or silver_data.get('instructing_agent_bic'),
                clearing_system='TARGET2',
            ))

        # Creditor Agent
        if silver_data.get('creditor_agent_bic') or silver_data.get('instructed_agent_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                bic=silver_data.get('creditor_agent_bic') or silver_data.get('instructed_agent_bic'),
                clearing_system='TARGET2',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('TARGET2', Target2Extractor())
ExtractorRegistry.register('target2', Target2Extractor())
