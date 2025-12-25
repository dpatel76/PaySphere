"""
GPS CDM - Databricks Pipeline Celery Tasks
==========================================

Celery tasks for processing data through the Databricks medallion architecture
and syncing lineage to Neo4j knowledge graph.

This enhanced version uses the TransformationEngine and MappingRegistry
to fully populate all CDM entity fields from source messages.

Usage:
    # Start worker with Databricks queues:
    celery -A gps_cdm.orchestration.databricks_pipeline_tasks worker -Q databricks,sync -l info

    # Submit a batch for processing:
    from gps_cdm.orchestration.databricks_pipeline_tasks import process_batch_to_databricks
    result = process_batch_to_databricks.delay(batch_id, xml_content, message_type)
"""

from celery import Celery, chain
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from decimal import Decimal
import uuid
import logging
import os
import json

logger = logging.getLogger(__name__)

# Celery configuration
# Use port 6379 (default Redis) for local development, 6380 requires auth
BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

app = Celery(
    "gps_cdm_databricks",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    result_expires=3600,
    task_soft_time_limit=300,
    task_time_limit=600,
    task_routes={
        "gps_cdm.orchestration.databricks_pipeline_tasks.process_batch_to_databricks": {"queue": "databricks"},
        "gps_cdm.orchestration.databricks_pipeline_tasks.sync_batch_to_neo4j": {"queue": "sync"},
    },
)


def get_databricks_connector():
    """Get Databricks connector with environment configuration."""
    from gps_cdm.ingestion.persistence.databricks_connector import DatabricksConnector
    return DatabricksConnector()


def get_neo4j_service():
    """Get Neo4j service."""
    from gps_cdm.orchestration.neo4j_service import get_neo4j_service as get_neo4j
    return get_neo4j()


def get_transformation_engine():
    """Get transformation engine with mapping registry."""
    from gps_cdm.transformations.engine import TransformationEngine
    from gps_cdm.transformations.registry import MappingRegistry
    return TransformationEngine(MappingRegistry())


def parse_message_comprehensive(content: str, message_type: str) -> Dict[str, Any]:
    """
    Parse any supported payment message type comprehensively.

    This function uses the multi-message-type parser module to support:
    - ISO 20022: pain.001, pain.008, pacs.004, pacs.008, camt.053
    - SWIFT MT: MT103, MT202

    Args:
        content: Raw message content (XML or SWIFT MT)
        message_type: Message type identifier

    Returns:
        Dictionary with all CDM entities:
        - payment: Core payment attributes
        - instruction: Payment instruction details
        - debtor: Debtor party information
        - creditor: Creditor party information
        - debtor_account: Debtor account details
        - creditor_account: Creditor account details
        - debtor_agent: Debtor's financial institution
        - creditor_agent: Creditor's financial institution
        - intermediary_agents: List of intermediary banks
        - remittance: Remittance information
        - regulatory: Regulatory reporting data
        - tax: Tax information if present
        - return_info: Return details for pacs.004
        - entries: Statement entries for camt.053
    """
    try:
        from gps_cdm.orchestration.message_parsers import parse_message
        return parse_message(content, message_type)
    except ImportError:
        logger.warning("message_parsers module not available, using inline parser")
        return _parse_xml_fallback(content, message_type)
    except Exception as e:
        logger.error(f"Error in parse_message: {e}")
        return _parse_xml_fallback(content, message_type)


def _parse_xml_fallback(xml_content: str, message_type: str) -> Dict[str, Any]:
    """Fallback inline XML parser for pain.001 if module not available."""
    import xml.etree.ElementTree as ET

    result = {
        "payment": {},
        "instruction": {},
        "debtor": {},
        "creditor": {},
        "debtor_account": {},
        "creditor_account": {},
        "debtor_agent": {},
        "creditor_agent": {},
        "intermediary_agents": [],
        "remittance": {},
        "regulatory": {},
        "tax": {},
        "ultimate_debtor": {},
        "ultimate_creditor": {},
        "charges": [],
        "return_info": {},
        "entries": [],
    }

    try:
        root = ET.fromstring(xml_content)

        def find_text(parent, tag):
            elem = parent.find('.//{*}' + tag)
            return elem.text.strip() if elem is not None and elem.text else None

        # Basic parsing for pain.001/pacs.008
        grp_hdr = root.find('.//{*}GrpHdr')
        if grp_hdr is not None:
            result["payment"]["message_id"] = find_text(grp_hdr, 'MsgId')
            result["payment"]["creation_datetime"] = find_text(grp_hdr, 'CreDtTm')

        # Try pacs.008 structure first (CdtTrfTxInf under root)
        cdt_trf = root.find('.//{*}CdtTrfTxInf')
        if cdt_trf is not None:
            # Amount
            instd_amt = cdt_trf.find('.//{*}InstdAmt')
            if instd_amt is None:
                instd_amt = cdt_trf.find('.//{*}IntrBkSttlmAmt')
            if instd_amt is not None:
                result["instruction"]["instructed_amount"] = instd_amt.text
                result["instruction"]["instructed_currency"] = instd_amt.get('Ccy')

            # End to End ID
            result["instruction"]["end_to_end_id"] = find_text(cdt_trf, 'EndToEndId')

            # Debtor
            dbtr = cdt_trf.find('.//{*}Dbtr')
            if dbtr is not None:
                result["debtor"]["name"] = find_text(dbtr, 'Nm')

            # Creditor
            cdtr = cdt_trf.find('.//{*}Cdtr')
            if cdtr is not None:
                result["creditor"]["name"] = find_text(cdtr, 'Nm')

            # Accounts
            dbtr_acct = cdt_trf.find('.//{*}DbtrAcct')
            if dbtr_acct is not None:
                result["debtor_account"]["iban"] = find_text(dbtr_acct, 'IBAN')

            cdtr_acct = cdt_trf.find('.//{*}CdtrAcct')
            if cdtr_acct is not None:
                result["creditor_account"]["iban"] = find_text(cdtr_acct, 'IBAN')

            # Agents
            dbtr_agt = cdt_trf.find('.//{*}DbtrAgt')
            if dbtr_agt is not None:
                result["debtor_agent"]["bic"] = find_text(dbtr_agt, 'BICFI') or find_text(dbtr_agt, 'BIC')

            cdtr_agt = cdt_trf.find('.//{*}CdtrAgt')
            if cdtr_agt is not None:
                result["creditor_agent"]["bic"] = find_text(cdtr_agt, 'BICFI') or find_text(cdtr_agt, 'BIC')
        else:
            # pain.001 structure (CdtTrfTxInf under PmtInf)
            pmt_inf = root.find('.//{*}PmtInf')
            if pmt_inf is not None:
                dbtr = pmt_inf.find('.//{*}Dbtr')
                if dbtr is not None:
                    result["debtor"]["name"] = find_text(dbtr, 'Nm')

                dbtr_acct = pmt_inf.find('.//{*}DbtrAcct')
                if dbtr_acct is not None:
                    result["debtor_account"]["iban"] = find_text(dbtr_acct, 'IBAN')

                dbtr_agt = pmt_inf.find('.//{*}DbtrAgt')
                if dbtr_agt is not None:
                    result["debtor_agent"]["bic"] = find_text(dbtr_agt, 'BICFI') or find_text(dbtr_agt, 'BIC')

                cdt_trf = pmt_inf.find('.//{*}CdtTrfTxInf')
                if cdt_trf is not None:
                    instd_amt = cdt_trf.find('.//{*}InstdAmt')
                    if instd_amt is not None:
                        result["instruction"]["instructed_amount"] = instd_amt.text
                        result["instruction"]["instructed_currency"] = instd_amt.get('Ccy')

                    result["instruction"]["end_to_end_id"] = find_text(cdt_trf, 'EndToEndId')

                    cdtr = cdt_trf.find('.//{*}Cdtr')
                    if cdtr is not None:
                        result["creditor"]["name"] = find_text(cdtr, 'Nm')

                    cdtr_acct = cdt_trf.find('.//{*}CdtrAcct')
                    if cdtr_acct is not None:
                        result["creditor_account"]["iban"] = find_text(cdtr_acct, 'IBAN')

                    cdtr_agt = cdt_trf.find('.//{*}CdtrAgt')
                    if cdtr_agt is not None:
                        result["creditor_agent"]["bic"] = find_text(cdtr_agt, 'BICFI') or find_text(cdtr_agt, 'BIC')

        return result

    except Exception as e:
        logger.error(f"Error in fallback XML parser: {e}")
        return result


def calculate_dq_score(parsed_data: Dict[str, Any]) -> tuple:
    """
    Calculate comprehensive data quality score.

    Returns (score, issues_list)
    """
    score = 1.0
    issues = []

    # Check debtor completeness (20%)
    debtor = parsed_data.get("debtor", {})
    if not debtor.get("name"):
        score -= 0.05
        issues.append("missing_debtor_name")
    if not debtor.get("country") and not parsed_data.get("debtor_agent", {}).get("country"):
        score -= 0.05
        issues.append("missing_debtor_country")
    if not debtor.get("address_line_1") and not debtor.get("street_name"):
        score -= 0.03
        issues.append("missing_debtor_address")

    # Check creditor completeness (20%)
    creditor = parsed_data.get("creditor", {})
    if not creditor.get("name"):
        score -= 0.05
        issues.append("missing_creditor_name")
    if not creditor.get("country") and not parsed_data.get("creditor_agent", {}).get("country"):
        score -= 0.05
        issues.append("missing_creditor_country")

    # Check account info (20%)
    debtor_acct = parsed_data.get("debtor_account", {})
    if not debtor_acct.get("iban") and not debtor_acct.get("account_number"):
        score -= 0.05
        issues.append("missing_debtor_account")

    creditor_acct = parsed_data.get("creditor_account", {})
    if not creditor_acct.get("iban") and not creditor_acct.get("account_number"):
        score -= 0.05
        issues.append("missing_creditor_account")

    # Check financial institutions (20%)
    if not parsed_data.get("debtor_agent", {}).get("bic"):
        score -= 0.03
        issues.append("missing_debtor_agent_bic")
    if not parsed_data.get("creditor_agent", {}).get("bic"):
        score -= 0.03
        issues.append("missing_creditor_agent_bic")

    # Check amount validity (15%)
    instruction = parsed_data.get("instruction", {})
    amount = instruction.get("instructed_amount")
    if not amount:
        score -= 0.15
        issues.append("missing_amount")
    else:
        try:
            amt_val = float(amount)
            if amt_val <= 0:
                score -= 0.10
                issues.append("invalid_amount_zero_or_negative")
        except:
            score -= 0.10
            issues.append("invalid_amount_format")

    if not instruction.get("instructed_currency"):
        score -= 0.05
        issues.append("missing_currency")

    # Check payment references (5%)
    if not instruction.get("end_to_end_id"):
        score -= 0.02
        issues.append("missing_end_to_end_id")

    return max(0.0, score), issues


@app.task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def process_batch_to_databricks(
    self,
    batch_id: str,
    xml_content: str,
    message_type: str = "pain.001",
    source_file: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Process a batch of XML data through the Databricks medallion pipeline.

    Enhanced version that extracts and stores ALL CDM fields:
    - Party (debtor, creditor, ultimate debtor/creditor)
    - Account (debtor, creditor accounts with IBAN/account number)
    - FinancialInstitution (debtor agent, creditor agent, intermediaries)
    - PaymentInstruction (full instruction with remittance, regulatory, tax)

    This task:
    1. Creates a batch tracking record
    2. Writes raw data to bronze layer
    3. Uses comprehensive parser to extract ALL CDM fields
    4. Writes CDM-conformant data to silver layer
    5. Creates gold layer entities (Party, Account, FI, PaymentInstruction)
    6. Syncs lineage to Neo4j

    Args:
        batch_id: Unique batch identifier
        xml_content: Raw XML content to process
        message_type: Message type (pain.001, camt.053, etc.)
        source_file: Optional source file name

    Returns:
        Dict with processing results including entity counts
    """
    start_time = datetime.utcnow()
    result = {
        "batch_id": batch_id,
        "status": "PROCESSING",
        "started_at": start_time.isoformat(),
        "bronze_count": 0,
        "silver_count": 0,
        "gold_count": 0,
        "party_count": 0,
        "account_count": 0,
        "fi_count": 0,
        "errors": [],
        "dq_score": 0.0,
        "dq_issues": [],
    }

    try:
        connector = get_databricks_connector()
        if not connector.is_available():
            raise Exception("Databricks not available")

        logger.info(f"Processing batch {batch_id} to Databricks (Enhanced CDM)")

        # 1. Create batch tracking record
        batch_table = connector.get_table_name("obs_batch_tracking")
        connector.execute(f"""
            INSERT INTO {batch_table}
            (batch_id, source_path, mapping_id, status, total_records,
             processed_records, failed_records, started_at, created_at, updated_at)
            VALUES (
                '{batch_id}',
                '{source_file or "celery_task"}',
                '{message_type}',
                'PROCESSING',
                1, 0, 0,
                '{start_time.isoformat()}',
                '{start_time.isoformat()}',
                '{start_time.isoformat()}'
            )
        """)
        logger.info(f"Created batch tracking record: {batch_id}")

        # 2. Parse message comprehensively to extract ALL CDM fields
        # Supports ISO 20022 (pain.001, pacs.008, camt.053, etc.) and SWIFT MT (MT103)
        parsed = parse_message_comprehensive(xml_content, message_type)
        dq_score, dq_issues = calculate_dq_score(parsed)
        result["dq_score"] = dq_score
        result["dq_issues"] = dq_issues

        # Extract key values
        payment = parsed.get("payment", {})
        instruction = parsed.get("instruction", {})
        debtor = parsed.get("debtor", {})
        creditor = parsed.get("creditor", {})
        debtor_account = parsed.get("debtor_account", {})
        creditor_account = parsed.get("creditor_account", {})
        debtor_agent = parsed.get("debtor_agent", {})
        creditor_agent = parsed.get("creditor_agent", {})
        remittance = parsed.get("remittance", {})
        regulatory = parsed.get("regulatory", {})

        message_id = payment.get("message_id") or f"MSG_{batch_id[:8]}"
        creation_dt = payment.get("creation_datetime") or start_time.isoformat()
        amount = float(instruction.get("instructed_amount") or 0)
        currency = instruction.get("instructed_currency") or "EUR"
        e2e_id = instruction.get("end_to_end_id") or ""

        # 3. Write to bronze layer
        raw_id = f"raw_{uuid.uuid4().hex[:12]}"
        bronze_table = connector.get_table_name("bronze_raw_payment")
        escaped_xml = xml_content.replace("'", "''")

        connector.execute(f"""
            INSERT INTO {bronze_table}
            (raw_id, message_type, message_id, creation_datetime, raw_xml,
             file_name, file_path, _batch_id, _ingested_at)
            VALUES (
                '{raw_id}',
                '{message_type}',
                '{message_id}',
                TIMESTAMP '{creation_dt}',
                '{escaped_xml}',
                '{source_file or "celery_task.xml"}',
                '/celery/input/',
                '{batch_id}',
                CURRENT_TIMESTAMP()
            )
        """)
        result["bronze_count"] = 1
        logger.info(f"Wrote bronze record: {raw_id}")

        # 4. Write enhanced silver layer with ALL CDM fields
        stg_id = f"stg_{uuid.uuid4().hex[:12]}"
        silver_table = connector.get_table_name("silver_stg_payment_instruction")

        # Helper for safe SQL string
        def sql_str(val, max_len=None):
            if val is None:
                return "NULL"
            s = str(val).replace("'", "''")
            if max_len:
                s = s[:max_len]
            return f"'{s}'"

        # Build comprehensive silver insert
        # Note: This assumes the silver table has these columns per the DDL
        try:
            connector.execute(f"""
                INSERT INTO {silver_table}
                (stg_id, raw_id, message_type, message_id, payment_id, end_to_end_id,
                 uetr, instruction_id_ext, payment_method, batch_booking,
                 amount, currency, equivalent_amount, equivalent_currency,
                 exchange_rate, charge_bearer, priority, service_level,
                 local_instrument, category_purpose, purpose_code, purpose_description,
                 requested_execution_date,
                 debtor_name, debtor_country, debtor_address, debtor_id_type, debtor_id_value,
                 debtor_date_of_birth, debtor_country_of_residence,
                 debtor_account_iban, debtor_account_number, debtor_account_type, debtor_account_currency,
                 debtor_agent_bic, debtor_agent_name, debtor_agent_clearing_code, debtor_agent_country,
                 creditor_name, creditor_country, creditor_address, creditor_id_type, creditor_id_value,
                 creditor_date_of_birth, creditor_country_of_residence,
                 creditor_account_iban, creditor_account_number, creditor_account_type, creditor_account_currency,
                 creditor_agent_bic, creditor_agent_name, creditor_agent_clearing_code, creditor_agent_country,
                 ultimate_debtor_name, ultimate_creditor_name,
                 remittance_unstructured, remittance_creditor_reference,
                 regulatory_reporting_code, regulatory_authority_country,
                 cross_border_flag,
                 dq_score, dq_issues, _batch_id, _ingested_at, created_at)
                VALUES (
                    '{stg_id}',
                    '{raw_id}',
                    '{message_type}',
                    {sql_str(message_id, 35)},
                    '{batch_id[:16]}',
                    {sql_str(e2e_id, 35)},
                    {sql_str(instruction.get('uetr'), 36)},
                    {sql_str(instruction.get('instruction_id'), 35)},
                    {sql_str(instruction.get('payment_method'), 3)},
                    {sql_str(instruction.get('batch_booking'))},
                    {amount},
                    '{currency}',
                    {instruction.get('equivalent_amount') or 'NULL'},
                    {sql_str(instruction.get('equivalent_currency'), 3)},
                    {instruction.get('exchange_rate') or 'NULL'},
                    {sql_str(instruction.get('charge_bearer'), 4)},
                    {sql_str(instruction.get('priority') or instruction.get('txn_priority'), 4)},
                    {sql_str(instruction.get('service_level') or instruction.get('txn_service_level'), 4)},
                    {sql_str(instruction.get('local_instrument'), 35)},
                    {sql_str(instruction.get('category_purpose'), 4)},
                    {sql_str(instruction.get('purpose_code'), 4)},
                    {sql_str(instruction.get('purpose_proprietary'), 140)},
                    {sql_str(instruction.get('requested_execution_date'))},
                    {sql_str(debtor.get('name'), 140)},
                    {sql_str(debtor.get('country'), 2)},
                    {sql_str(debtor.get('address_line_1') or debtor.get('street_name'), 140)},
                    {sql_str(debtor.get('other_id_scheme'), 35)},
                    {sql_str(debtor.get('other_id') or debtor.get('national_id') or debtor.get('lei'), 35)},
                    {sql_str(debtor.get('date_of_birth'))},
                    {sql_str(debtor.get('country_of_residence'), 2)},
                    {sql_str(debtor_account.get('iban'), 34)},
                    {sql_str(debtor_account.get('account_number'), 34)},
                    {sql_str(debtor_account.get('account_type'), 4)},
                    {sql_str(debtor_account.get('currency'), 3)},
                    {sql_str(debtor_agent.get('bic'), 11)},
                    {sql_str(debtor_agent.get('name'), 140)},
                    {sql_str(debtor_agent.get('clearing_system_member_id'), 35)},
                    {sql_str(debtor_agent.get('country'), 2)},
                    {sql_str(creditor.get('name'), 140)},
                    {sql_str(creditor.get('country'), 2)},
                    {sql_str(creditor.get('address_line_1') or creditor.get('street_name'), 140)},
                    {sql_str(creditor.get('other_id_scheme'), 35)},
                    {sql_str(creditor.get('other_id') or creditor.get('national_id') or creditor.get('lei'), 35)},
                    {sql_str(creditor.get('date_of_birth'))},
                    {sql_str(creditor.get('country_of_residence'), 2)},
                    {sql_str(creditor_account.get('iban'), 34)},
                    {sql_str(creditor_account.get('account_number'), 34)},
                    {sql_str(creditor_account.get('account_type'), 4)},
                    {sql_str(creditor_account.get('currency'), 3)},
                    {sql_str(creditor_agent.get('bic'), 11)},
                    {sql_str(creditor_agent.get('name'), 140)},
                    {sql_str(creditor_agent.get('clearing_system_member_id'), 35)},
                    {sql_str(creditor_agent.get('country'), 2)},
                    {sql_str(parsed.get('ultimate_debtor', {}).get('name'), 140)},
                    {sql_str(parsed.get('ultimate_creditor', {}).get('name'), 140)},
                    {sql_str('; '.join(remittance.get('unstructured', [])) if remittance.get('unstructured') else None, 500)},
                    {sql_str(remittance.get('creditor_reference'), 35)},
                    {sql_str(regulatory.get('code'), 10)},
                    {sql_str(regulatory.get('authority_country'), 2)},
                    {payment.get('cross_border', False)},
                    {dq_score},
                    '{",".join(dq_issues)}',
                    '{batch_id}',
                    CURRENT_TIMESTAMP(),
                    CURRENT_TIMESTAMP()
                )
            """)
        except Exception as silver_err:
            # Fallback to simpler insert if table schema doesn't have all columns
            logger.warning(f"Enhanced silver insert failed, using basic: {silver_err}")
            connector.execute(f"""
                INSERT INTO {silver_table}
                (stg_id, raw_id, message_type, message_id, payment_id, end_to_end_id,
                 amount, currency, debtor_name, debtor_account, creditor_name, creditor_account,
                 dq_score, dq_issues, _batch_id, _ingested_at, created_at)
                VALUES (
                    '{stg_id}',
                    '{raw_id}',
                    '{message_type}',
                    {sql_str(message_id, 35)},
                    '{batch_id[:16]}',
                    {sql_str(e2e_id, 35)},
                    {amount},
                    '{currency}',
                    {sql_str(debtor.get('name'), 140)},
                    {sql_str(debtor_account.get('iban') or debtor_account.get('account_number'), 34)},
                    {sql_str(creditor.get('name'), 140)},
                    {sql_str(creditor_account.get('iban') or creditor_account.get('account_number'), 34)},
                    {dq_score},
                    '{",".join(dq_issues)}',
                    '{batch_id}',
                    CURRENT_TIMESTAMP(),
                    CURRENT_TIMESTAMP()
                )
            """)

        result["silver_count"] = 1
        logger.info(f"Wrote silver record: {stg_id}")

        # 5. Create gold layer entities

        # 5a. Create Party entities (debtor and creditor)
        gold_party_count = 0
        party_table = connector.get_table_name("gold_cdm_party")

        # Debtor party
        if debtor.get('name'):
            debtor_party_id = f"party_{uuid.uuid4().hex[:12]}"
            try:
                connector.execute(f"""
                    INSERT INTO {party_table}
                    (party_id, party_type, name, country, address_line_1, address_city,
                     address_postal_code, country_of_residence, date_of_birth, national_id,
                     lei, bic, _batch_id, _ingested_at, created_at, updated_at)
                    VALUES (
                        '{debtor_party_id}',
                        'DEBTOR',
                        {sql_str(debtor.get('name'), 140)},
                        {sql_str(debtor.get('country'), 2)},
                        {sql_str(debtor.get('address_line_1') or debtor.get('street_name'), 140)},
                        {sql_str(debtor.get('town_name'), 70)},
                        {sql_str(debtor.get('postal_code'), 16)},
                        {sql_str(debtor.get('country_of_residence'), 2)},
                        {sql_str(debtor.get('date_of_birth'))},
                        {sql_str(debtor.get('national_id') or debtor.get('other_id'), 35)},
                        {sql_str(debtor.get('lei'), 20)},
                        {sql_str(debtor.get('bic'), 11)},
                        '{batch_id}',
                        CURRENT_TIMESTAMP(),
                        CURRENT_TIMESTAMP(),
                        CURRENT_TIMESTAMP()
                    )
                """)
                gold_party_count += 1
            except Exception as e:
                logger.warning(f"Could not insert debtor party: {e}")

        # Creditor party
        if creditor.get('name'):
            creditor_party_id = f"party_{uuid.uuid4().hex[:12]}"
            try:
                connector.execute(f"""
                    INSERT INTO {party_table}
                    (party_id, party_type, name, country, address_line_1, address_city,
                     address_postal_code, country_of_residence, date_of_birth, national_id,
                     lei, bic, _batch_id, _ingested_at, created_at, updated_at)
                    VALUES (
                        '{creditor_party_id}',
                        'CREDITOR',
                        {sql_str(creditor.get('name'), 140)},
                        {sql_str(creditor.get('country'), 2)},
                        {sql_str(creditor.get('address_line_1') or creditor.get('street_name'), 140)},
                        {sql_str(creditor.get('town_name'), 70)},
                        {sql_str(creditor.get('postal_code'), 16)},
                        {sql_str(creditor.get('country_of_residence'), 2)},
                        {sql_str(creditor.get('date_of_birth'))},
                        {sql_str(creditor.get('national_id') or creditor.get('other_id'), 35)},
                        {sql_str(creditor.get('lei'), 20)},
                        {sql_str(creditor.get('bic'), 11)},
                        '{batch_id}',
                        CURRENT_TIMESTAMP(),
                        CURRENT_TIMESTAMP(),
                        CURRENT_TIMESTAMP()
                    )
                """)
                gold_party_count += 1
            except Exception as e:
                logger.warning(f"Could not insert creditor party: {e}")

        result["party_count"] = gold_party_count

        # 5b. Create Account entities
        gold_account_count = 0
        account_table = connector.get_table_name("gold_cdm_account")

        # Debtor account
        if debtor_account.get('iban') or debtor_account.get('account_number'):
            debtor_acct_id = f"acct_{uuid.uuid4().hex[:12]}"
            try:
                connector.execute(f"""
                    INSERT INTO {account_table}
                    (account_id, account_type, iban, account_number, currency, account_name,
                     owner_party_type, _batch_id, _ingested_at, created_at, updated_at)
                    VALUES (
                        '{debtor_acct_id}',
                        {sql_str(debtor_account.get('account_type') or 'CACC', 4)},
                        {sql_str(debtor_account.get('iban'), 34)},
                        {sql_str(debtor_account.get('account_number'), 34)},
                        {sql_str(debtor_account.get('currency'), 3)},
                        {sql_str(debtor_account.get('name'), 70)},
                        'DEBTOR',
                        '{batch_id}',
                        CURRENT_TIMESTAMP(),
                        CURRENT_TIMESTAMP(),
                        CURRENT_TIMESTAMP()
                    )
                """)
                gold_account_count += 1
            except Exception as e:
                logger.warning(f"Could not insert debtor account: {e}")

        # Creditor account
        if creditor_account.get('iban') or creditor_account.get('account_number'):
            creditor_acct_id = f"acct_{uuid.uuid4().hex[:12]}"
            try:
                connector.execute(f"""
                    INSERT INTO {account_table}
                    (account_id, account_type, iban, account_number, currency, account_name,
                     owner_party_type, _batch_id, _ingested_at, created_at, updated_at)
                    VALUES (
                        '{creditor_acct_id}',
                        {sql_str(creditor_account.get('account_type') or 'CACC', 4)},
                        {sql_str(creditor_account.get('iban'), 34)},
                        {sql_str(creditor_account.get('account_number'), 34)},
                        {sql_str(creditor_account.get('currency'), 3)},
                        {sql_str(creditor_account.get('name'), 70)},
                        'CREDITOR',
                        '{batch_id}',
                        CURRENT_TIMESTAMP(),
                        CURRENT_TIMESTAMP(),
                        CURRENT_TIMESTAMP()
                    )
                """)
                gold_account_count += 1
            except Exception as e:
                logger.warning(f"Could not insert creditor account: {e}")

        result["account_count"] = gold_account_count

        # 5c. Create FinancialInstitution entities
        gold_fi_count = 0
        fi_table = connector.get_table_name("gold_cdm_financial_institution")

        # Debtor agent
        if debtor_agent.get('bic'):
            debtor_fi_id = f"fi_{uuid.uuid4().hex[:12]}"
            try:
                connector.execute(f"""
                    INSERT INTO {fi_table}
                    (fi_id, fi_type, bic, name, clearing_system_code, clearing_member_id,
                     country, lei, branch_id, branch_name,
                     _batch_id, _ingested_at, created_at, updated_at)
                    VALUES (
                        '{debtor_fi_id}',
                        'DEBTOR_AGENT',
                        {sql_str(debtor_agent.get('bic'), 11)},
                        {sql_str(debtor_agent.get('name'), 140)},
                        {sql_str(debtor_agent.get('clearing_system_code'), 5)},
                        {sql_str(debtor_agent.get('clearing_system_member_id'), 35)},
                        {sql_str(debtor_agent.get('country'), 2)},
                        {sql_str(debtor_agent.get('lei'), 20)},
                        {sql_str(debtor_agent.get('branch_id'), 35)},
                        {sql_str(debtor_agent.get('branch_name'), 140)},
                        '{batch_id}',
                        CURRENT_TIMESTAMP(),
                        CURRENT_TIMESTAMP(),
                        CURRENT_TIMESTAMP()
                    )
                """)
                gold_fi_count += 1
            except Exception as e:
                logger.warning(f"Could not insert debtor agent: {e}")

        # Creditor agent
        if creditor_agent.get('bic'):
            creditor_fi_id = f"fi_{uuid.uuid4().hex[:12]}"
            try:
                connector.execute(f"""
                    INSERT INTO {fi_table}
                    (fi_id, fi_type, bic, name, clearing_system_code, clearing_member_id,
                     country, branch_id, branch_name,
                     _batch_id, _ingested_at, created_at, updated_at)
                    VALUES (
                        '{creditor_fi_id}',
                        'CREDITOR_AGENT',
                        {sql_str(creditor_agent.get('bic'), 11)},
                        {sql_str(creditor_agent.get('name'), 140)},
                        {sql_str(creditor_agent.get('clearing_system_code'), 5)},
                        {sql_str(creditor_agent.get('clearing_system_member_id'), 35)},
                        {sql_str(creditor_agent.get('country'), 2)},
                        {sql_str(creditor_agent.get('branch_id'), 35)},
                        {sql_str(creditor_agent.get('branch_name'), 140)},
                        '{batch_id}',
                        CURRENT_TIMESTAMP(),
                        CURRENT_TIMESTAMP(),
                        CURRENT_TIMESTAMP()
                    )
                """)
                gold_fi_count += 1
            except Exception as e:
                logger.warning(f"Could not insert creditor agent: {e}")

        result["fi_count"] = gold_fi_count

        # 5d. Create comprehensive PaymentInstruction entity
        instruction_id = f"instr_{uuid.uuid4().hex[:12]}"
        gold_table = connector.get_table_name("gold_cdm_payment_instruction")

        # Determine payment type
        payment_type = "CREDIT_TRANSFER"
        if message_type.startswith("pain.008") or message_type.startswith("pacs.003"):
            payment_type = "DIRECT_DEBIT"
        elif message_type.startswith("pacs.004"):
            payment_type = "RETURN"

        # Try enhanced insert, fallback to basic if columns don't exist
        try:
            connector.execute(f"""
                INSERT INTO {gold_table}
                (instruction_id, stg_id, message_type, payment_type, amount, currency,
                 end_to_end_id, uetr, charge_bearer, priority, service_level,
                 purpose_code, cross_border_flag, dq_score,
                 debtor_name, creditor_name,
                 debtor_agent_bic, creditor_agent_bic,
                 status, created_at, updated_at, _batch_id, _ingested_at)
                VALUES (
                    '{instruction_id}',
                    '{stg_id}',
                    '{message_type}',
                    '{payment_type}',
                    {amount},
                    '{currency}',
                    {sql_str(e2e_id, 35)},
                    {sql_str(instruction.get('uetr'), 36)},
                    {sql_str(instruction.get('charge_bearer'), 4)},
                    {sql_str(instruction.get('priority') or 'NORM', 4)},
                    {sql_str(instruction.get('service_level'), 4)},
                    {sql_str(instruction.get('purpose_code'), 4)},
                    {payment.get('cross_border', False)},
                    {dq_score},
                    {sql_str(debtor.get('name'), 140)},
                    {sql_str(creditor.get('name'), 140)},
                    {sql_str(debtor_agent.get('bic'), 11)},
                    {sql_str(creditor_agent.get('bic'), 11)},
                    'PROCESSED',
                    CURRENT_TIMESTAMP(),
                    CURRENT_TIMESTAMP(),
                    '{batch_id}',
                    CURRENT_TIMESTAMP()
                )
            """)
        except Exception as gold_err:
            # Fallback to basic insert matching current table schema
            logger.warning(f"Enhanced gold insert failed, using basic: {gold_err}")
            connector.execute(f"""
                INSERT INTO {gold_table}
                (instruction_id, stg_id, message_type, payment_type, amount, currency,
                 status, created_at, updated_at, _batch_id, _ingested_at)
                VALUES (
                    '{instruction_id}',
                    '{stg_id}',
                    '{message_type}',
                    '{payment_type}',
                    {amount},
                    '{currency}',
                    'PROCESSED',
                    CURRENT_TIMESTAMP(),
                    CURRENT_TIMESTAMP(),
                    '{batch_id}',
                    CURRENT_TIMESTAMP()
                )
            """)

        result["gold_count"] = 1 + gold_party_count + gold_account_count + gold_fi_count
        logger.info(f"Wrote gold record: {instruction_id} (+ {gold_party_count} parties, {gold_account_count} accounts, {gold_fi_count} FIs)")

        # 5. Update batch tracking
        end_time = datetime.utcnow()
        connector.execute(f"""
            UPDATE {batch_table}
            SET status = 'COMPLETED',
                processed_records = 1,
                completed_at = '{end_time.isoformat()}',
                updated_at = '{end_time.isoformat()}'
            WHERE batch_id = '{batch_id}'
        """)

        result["status"] = "COMPLETED"
        result["completed_at"] = end_time.isoformat()
        result["duration_ms"] = int((end_time - start_time).total_seconds() * 1000)

        # 6. Sync to Neo4j (chain to next task)
        sync_batch_to_neo4j.delay(batch_id)

        logger.info(f"Batch {batch_id} completed successfully")
        connector.close()
        return result

    except Exception as e:
        logger.error(f"Batch {batch_id} failed: {e}")
        result["status"] = "FAILED"
        result["errors"].append(str(e))
        result["completed_at"] = datetime.utcnow().isoformat()

        # Try to update batch tracking with failure
        try:
            connector = get_databricks_connector()
            batch_table = connector.get_table_name("obs_batch_tracking")
            connector.execute(f"""
                UPDATE {batch_table}
                SET status = 'FAILED',
                    error_message = '{str(e)[:500].replace("'", "''")}',
                    updated_at = CURRENT_TIMESTAMP()
                WHERE batch_id = '{batch_id}'
            """)
            connector.close()
        except:
            pass

        raise


@app.task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def sync_batch_to_neo4j(self, batch_id: str) -> Dict[str, Any]:
    """
    Sync a Databricks batch to Neo4j knowledge graph.

    This task:
    1. Gets batch info from Databricks
    2. Gets layer statistics
    3. Upserts batch node to Neo4j
    4. Creates layer relationships

    Args:
        batch_id: The batch ID to sync

    Returns:
        Dict with sync results
    """
    result = {
        "batch_id": batch_id,
        "status": "SYNCING",
        "started_at": datetime.utcnow().isoformat(),
    }

    try:
        connector = get_databricks_connector()
        neo4j = get_neo4j_service()

        if not connector.is_available():
            raise Exception("Databricks not available")
        if not neo4j.is_available():
            raise Exception("Neo4j not available")

        logger.info(f"Syncing batch {batch_id} to Neo4j")

        # Get batch info from Databricks
        sync_result = connector.sync_batch_to_neo4j(batch_id)

        if sync_result:
            result["status"] = "SYNCED"
            result["completed_at"] = datetime.utcnow().isoformat()
            logger.info(f"Batch {batch_id} synced to Neo4j successfully")
        else:
            result["status"] = "PARTIAL"
            result["message"] = "Sync completed with warnings"

        connector.close()
        return result

    except Exception as e:
        logger.error(f"Neo4j sync failed for {batch_id}: {e}")
        result["status"] = "FAILED"
        result["error"] = str(e)
        raise


@app.task
def process_pipeline_chain(
    xml_content: str,
    message_type: str = "pain.001",
    source_file: Optional[str] = None,
) -> str:
    """
    Process XML through the full pipeline using task chaining.

    This creates a workflow:
    process_batch_to_databricks -> sync_batch_to_neo4j

    Returns:
        The batch_id for tracking
    """
    batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    # Create chain: process -> sync
    workflow = chain(
        process_batch_to_databricks.s(batch_id, xml_content, message_type, source_file),
        sync_batch_to_neo4j.s(batch_id),
    )

    workflow.apply_async()
    return batch_id
