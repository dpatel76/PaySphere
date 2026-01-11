"""
GPS CDM API - Lineage Routes

Provides endpoints for data lineage visualization:
1. Lineage mappings across zones by message type
2. Field-level lineage with filtering
3. Backward lineage from CDM entity to source
4. Backward lineage from reporting views
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


# Response Models
class FieldLineageResponse(BaseModel):
    source_layer: str
    source_table: str
    source_field: str
    source_path: Optional[str]
    target_layer: str
    target_table: str
    target_field: str
    transformation_type: Optional[str]
    transformation_logic: Optional[str]
    data_type: str
    message_type: str
    entity_role: Optional[str] = None  # Role for entity-based mappings (DEBTOR, CREDITOR, etc.)


class LayerLineageResponse(BaseModel):
    source_layer: str
    source_table: str
    target_layer: str
    target_table: str
    field_count: int
    message_type: str


class EntityLineageResponse(BaseModel):
    entity_table: str
    entity_field: str
    message_types: List[str]
    source_count: int


# Initialize service
def get_lineage_service():
    """Get lineage service instance."""
    from gps_cdm.orchestration.lineage_service import LineageService
    return LineageService()


@router.get("/message-type/{message_type}")
async def get_message_type_lineage(message_type: str):
    """
    Get complete lineage for a message type.

    Returns bronze→silver→gold mappings with all field transformations.
    """
    service = get_lineage_service()
    lineage = service.get_message_type_lineage(message_type)

    if not lineage:
        raise HTTPException(status_code=404, detail=f"No lineage found for message type: {message_type}")

    return {
        "message_type": lineage.message_type,
        "bronze_to_silver": {
            "source_layer": lineage.bronze_to_silver.source_layer if lineage.bronze_to_silver else None,
            "source_table": lineage.bronze_to_silver.source_table if lineage.bronze_to_silver else None,
            "target_layer": lineage.bronze_to_silver.target_layer if lineage.bronze_to_silver else None,
            "target_table": lineage.bronze_to_silver.target_table if lineage.bronze_to_silver else None,
            "field_count": len(lineage.bronze_to_silver.field_mappings) if lineage.bronze_to_silver else 0,
        },
        "silver_to_gold": {
            "source_layer": lineage.silver_to_gold.source_layer if lineage.silver_to_gold else None,
            "source_table": lineage.silver_to_gold.source_table if lineage.silver_to_gold else None,
            "target_layer": lineage.silver_to_gold.target_layer if lineage.silver_to_gold else None,
            "target_table": lineage.silver_to_gold.target_table if lineage.silver_to_gold else None,
            "field_count": len(lineage.silver_to_gold.field_mappings) if lineage.silver_to_gold else 0,
        },
        "entity_mappings": {
            entity: len(fields)
            for entity, fields in lineage.entity_mappings.items()
        },
    }


@router.get("/message-type/{message_type}/fields")
async def get_field_lineage(
    message_type: str,
    field_name: Optional[str] = Query(None, description="Filter by field name (partial match)"),
    layer: Optional[str] = Query(None, description="Filter by layer (bronze, silver, gold)"),
    data_type: Optional[str] = Query(None, description="Filter by data type"),
):
    """
    Get field-level lineage for a message type.

    Supports filtering by field name, layer, and data type.
    """
    service = get_lineage_service()
    fields = service.get_field_lineage(
        message_type=message_type,
        field_name=field_name,
        layer=layer,
        data_type=data_type,
    )

    return [
        FieldLineageResponse(
            source_layer=f.source_layer,
            source_table=f.source_table,
            source_field=f.source_field,
            source_path=f.source_path,
            target_layer=f.target_layer,
            target_table=f.target_table,
            target_field=f.target_field,
            transformation_type=f.transformation_type,
            transformation_logic=f.transformation_logic,
            data_type=f.data_type,
            message_type=f.message_type,
            entity_role=f.entity_role,
        )
        for f in fields
    ]


@router.get("/backward/entity/{entity_table}")
async def get_backward_lineage_from_entity(
    entity_table: str,
    field_name: Optional[str] = Query(None, description="Filter by field name"),
):
    """
    Get backward lineage from a CDM entity to source message types.

    Shows which message types and fields contribute to a CDM entity.
    """
    service = get_lineage_service()
    lineage = service.get_backward_lineage_from_cdm(entity_table, field_name)

    return {
        "entity_table": lineage.entity_table,
        "entity_field": lineage.entity_field,
        "message_types": lineage.message_types,
        "source_mappings": [
            {
                "message_type": m.message_type,
                "source_layer": m.source_layer,
                "source_table": m.source_table,
                "source_field": m.source_field,
                "source_path": m.source_path,
                "target_field": m.target_field,
            }
            for m in lineage.source_mappings
        ],
    }


@router.get("/backward/report/{report_type}")
async def get_backward_lineage_from_report(
    report_type: str,
    field_name: Optional[str] = Query(None, description="Filter by report field name"),
):
    """
    Get backward lineage from a regulatory report to source.

    Shows the complete lineage from report field → CDM → Silver → Bronze.

    Supported report types:
    - FATCA_8966: FATCA Form 8966
    - FINCEN_CTR: FinCEN Currency Transaction Report
    """
    service = get_lineage_service()
    result = service.get_backward_lineage_from_report(report_type, field_name)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/graph/{message_type}")
async def get_lineage_graph(message_type: str):
    """
    Get lineage as a graph structure for visualization.

    Returns nodes and edges suitable for rendering in a visualization library.
    """
    service = get_lineage_service()
    return service.get_lineage_graph(message_type)


@router.post("/persist/{message_type}")
async def persist_lineage(message_type: str):
    """
    Persist lineage to database for querying.

    This populates the obs_field_lineage table from YAML mappings.
    """
    import os
    import psycopg2
    db = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5433)),
        database=os.environ.get("POSTGRES_DB", "gps_cdm"),
        user=os.environ.get("POSTGRES_USER", "gps_cdm_svc"),
        password=os.environ.get("POSTGRES_PASSWORD", "gps_cdm_password"),
    )

    try:
        from gps_cdm.orchestration.lineage_service import LineageService
        service = LineageService(db)
        count = service.persist_lineage(message_type)
        return {"status": "success", "records_persisted": count}
    finally:
        db.close()


@router.get("/query")
async def query_lineage(
    source_field: Optional[str] = Query(None, description="Filter by source field name"),
    target_field: Optional[str] = Query(None, description="Filter by target field name"),
    layer: Optional[str] = Query(None, description="Filter by layer"),
    limit: int = Query(100, le=1000),
):
    """
    Query lineage from database.

    Searches persisted lineage records with filters.
    """
    import os
    import psycopg2
    db = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5433)),
        database=os.environ.get("POSTGRES_DB", "gps_cdm"),
        user=os.environ.get("POSTGRES_USER", "gps_cdm_svc"),
        password=os.environ.get("POSTGRES_PASSWORD", "gps_cdm_password"),
    )

    try:
        from gps_cdm.orchestration.lineage_service import LineageService
        service = LineageService(db)
        return service.query_lineage_from_db(
            source_field=source_field,
            target_field=target_field,
            layer=layer,
            limit=limit,
        )
    finally:
        db.close()


@router.get("/supported-message-types")
async def list_supported_message_types():
    """List all supported message types from database mapping tables or Neo4j."""
    import os
    import psycopg2

    # First try to get from PostgreSQL mapping.message_formats table (primary source)
    try:
        conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", 5433)),
            database=os.environ.get("POSTGRES_DB", "gps_cdm"),
            user=os.environ.get("POSTGRES_USER", "gps_cdm_svc"),
            password=os.environ.get("POSTGRES_PASSWORD", "gps_cdm_password"),
        )
        cursor = conn.cursor()

        # Query message formats from mapping table
        cursor.execute("""
            SELECT format_id, format_name, format_family, version, description
            FROM mapping.message_formats
            WHERE is_active = true
            ORDER BY format_family, format_id
        """)

        message_types = []
        for row in cursor.fetchall():
            format_id, format_name, format_family, version, description = row
            message_types.append({
                "id": format_id,
                "display_name": f"{format_id} - {format_name}",
                "format_family": format_family,
                "format": "XML" if format_id.startswith(("pain", "pacs", "camt", "acmt")) else "FIN",
                "version": version or "1.0",
                "description": description or "",
            })

        conn.close()

        if message_types:
            return {
                "supported_types": message_types,
                "count": len(message_types),
            }
    except Exception as e:
        import logging
        logging.warning(f"Failed to query mapping.message_formats: {e}")

    # Fallback to Neo4j if PostgreSQL mapping table not available
    from gps_cdm.orchestration.neo4j_service import get_neo4j_service

    neo4j = get_neo4j_service()
    if neo4j.is_available():
        query = """
            MATCH (mt:MessageType)
            WHERE mt.type IS NOT NULL
            RETURN DISTINCT mt.type as id, mt.description as description,
                   mt.format as format, mt.version as version
            ORDER BY mt.type
        """
        results = neo4j.run_query(query)

        message_types = [
            {
                "id": r.get("id"),
                "display_name": r.get("id", "").upper().replace(".", " ").replace("_", " "),
                "format": r.get("format", "XML"),
                "version": r.get("version", "1.0"),
                "description": r.get("description", ""),
            }
            for r in results if r.get("id")
        ]

        if message_types:
            return {
                "supported_types": message_types,
                "count": len(message_types),
            }

    # Final fallback - return default list of all 29 known message types
    default_types = [
        # ISO 20022 Core
        {"id": "pain.001", "display_name": "pain.001 - Customer Credit Transfer Initiation", "format": "XML", "version": "1.0", "format_family": "ISO 20022"},
        {"id": "pain.002", "display_name": "pain.002 - Customer Payment Status Report", "format": "XML", "version": "1.0", "format_family": "ISO 20022"},
        {"id": "pacs.008", "display_name": "pacs.008 - FI Credit Transfer", "format": "XML", "version": "1.0", "format_family": "ISO 20022"},
        {"id": "pacs.009", "display_name": "pacs.009 - FI Credit Transfer (Cover)", "format": "XML", "version": "1.0", "format_family": "ISO 20022"},
        {"id": "pacs.002", "display_name": "pacs.002 - FI Payment Status Report", "format": "XML", "version": "1.0", "format_family": "ISO 20022"},
        {"id": "camt.053", "display_name": "camt.053 - Bank Statement", "format": "XML", "version": "1.0", "format_family": "ISO 20022"},
        # NOTE: All SWIFT MT messages decommissioned Nov 2025 - use ISO 20022 equivalents (camt.053 for statements)
        # US Regional
        {"id": "FEDWIRE", "display_name": "FEDWIRE - Federal Reserve Wire Transfer", "format": "ISO20022", "version": "2023", "format_family": "US Regional"},
        {"id": "ACH", "display_name": "ACH - Automated Clearing House", "format": "NACHA", "version": "2023", "format_family": "US Regional"},
        {"id": "CHIPS", "display_name": "CHIPS - Clearing House Interbank Payment System", "format": "ISO20022", "version": "2023", "format_family": "US Regional"},
        {"id": "RTP", "display_name": "RTP - Real-Time Payments", "format": "ISO20022", "version": "2023", "format_family": "US Regional"},
        {"id": "FEDNOW", "display_name": "FEDNOW - Federal Reserve Instant Payments", "format": "ISO20022", "version": "2023", "format_family": "US Regional"},
        # EU Regional
        {"id": "SEPA", "display_name": "SEPA - Single Euro Payments Area", "format": "ISO20022", "version": "2019", "format_family": "EU Regional"},
        {"id": "TARGET2", "display_name": "TARGET2 - Trans-European RTGS", "format": "ISO20022", "version": "2023", "format_family": "EU Regional"},
        # UK Regional
        {"id": "CHAPS", "display_name": "CHAPS - Clearing House Automated Payment System", "format": "ISO20022", "version": "2023", "format_family": "UK Regional"},
        {"id": "FPS", "display_name": "FPS - Faster Payments Service", "format": "ISO20022", "version": "2023", "format_family": "UK Regional"},
        {"id": "BACS", "display_name": "BACS - Bankers Automated Clearing System", "format": "Fixed", "version": "2023", "format_family": "UK Regional"},
        # Asia-Pacific
        {"id": "NPP", "display_name": "NPP - New Payments Platform (Australia)", "format": "ISO20022", "version": "2023", "format_family": "APAC Regional"},
        {"id": "MEPS_PLUS", "display_name": "MEPS+ - MAS Electronic Payment System (Singapore)", "format": "ISO20022", "version": "2023", "format_family": "APAC Regional"},
        {"id": "RTGS_HK", "display_name": "RTGS HK - Real-Time Gross Settlement (Hong Kong)", "format": "ISO20022", "version": "2023", "format_family": "APAC Regional"},
        {"id": "CNAPS", "display_name": "CNAPS - China National Advanced Payment System", "format": "Proprietary", "version": "2023", "format_family": "APAC Regional"},
        {"id": "BOJNET", "display_name": "BOJ-NET - Bank of Japan Network", "format": "Proprietary", "version": "2023", "format_family": "APAC Regional"},
        {"id": "KFTC", "display_name": "KFTC - Korea Financial Telecommunications", "format": "Fixed", "version": "2023", "format_family": "APAC Regional"},
        {"id": "INSTAPAY", "display_name": "InstaPay - Philippines Instant Payment", "format": "ISO20022", "version": "2023", "format_family": "APAC Regional"},
        # Middle East
        {"id": "UAEFTS", "display_name": "UAEFTS - UAE Funds Transfer System", "format": "ISO20022", "version": "2023", "format_family": "ME Regional"},
        {"id": "SARIE", "display_name": "SARIE - Saudi Arabian Riyal Interbank Express", "format": "SWIFT", "version": "2023", "format_family": "ME Regional"},
        # Latin America & Other
        {"id": "PIX", "display_name": "PIX - Brazil Instant Payment", "format": "JSON", "version": "2023", "format_family": "LATAM Regional"},
        {"id": "UPI", "display_name": "UPI - Unified Payments Interface (India)", "format": "JSON", "version": "2023", "format_family": "APAC Regional"},
        {"id": "PROMPTPAY", "display_name": "PromptPay - Thailand Instant Payment", "format": "ISO20022", "version": "2023", "format_family": "APAC Regional"},
        {"id": "PAYNOW", "display_name": "PayNow - Singapore Instant Payment", "format": "ISO20022", "version": "2023", "format_family": "APAC Regional"},
    ]
    return {
        "supported_types": default_types,
        "count": len(default_types),
    }


@router.get("/supported-reports")
async def list_supported_reports():
    """List all supported regulatory reports for lineage."""
    return {
        "reports": [
            {
                "id": "FATCA_8966",
                "name": "FATCA Form 8966",
                "jurisdiction": "US",
                "description": "Account holder reporting for US tax purposes",
            },
            {
                "id": "FINCEN_CTR",
                "name": "FinCEN Currency Transaction Report",
                "jurisdiction": "US",
                "description": "Cash transactions over $10,000",
            },
            {
                "id": "FINCEN_SAR",
                "name": "FinCEN Suspicious Activity Report",
                "jurisdiction": "US",
                "description": "Suspicious transaction reporting",
            },
            {
                "id": "AUSTRAC_IFTI",
                "name": "AUSTRAC International Funds Transfer Instruction",
                "jurisdiction": "AU",
                "description": "International transfers reporting",
            },
            {
                "id": "OECD_CRS",
                "name": "OECD Common Reporting Standard",
                "jurisdiction": "GLOBAL",
                "description": "Cross-border tax information exchange",
            },
        ]
    }


@router.get("/cdm-entities")
async def list_cdm_entities():
    """List all CDM entities available for backward lineage."""
    return {
        "entities": [
            # Core CDM entities
            {
                "table": "cdm_payment_instruction",
                "display_name": "Payment Instruction",
                "description": "Core payment transaction record",
                "key_fields": ["instruction_id", "end_to_end_id", "uetr"],
                "category": "Core",
            },
            {
                "table": "cdm_party",
                "display_name": "Party",
                "description": "Customer, counterparty, or related party",
                "key_fields": ["party_id", "name", "tax_id"],
                "category": "Core",
            },
            {
                "table": "cdm_account",
                "display_name": "Account",
                "description": "Bank account or financial account",
                "key_fields": ["account_id", "iban", "account_number"],
                "category": "Core",
            },
            {
                "table": "cdm_financial_institution",
                "display_name": "Financial Institution",
                "description": "Bank or financial service provider",
                "key_fields": ["fi_id", "bic", "lei"],
                "category": "Core",
            },
            {
                "table": "cdm_payment_status",
                "display_name": "Payment Status",
                "description": "Status and reason for payment state changes",
                "key_fields": ["status_id", "instruction_id", "status_code"],
                "category": "Core",
            },
            {
                "table": "cdm_fx_rate",
                "display_name": "FX Rate",
                "description": "Currency exchange rate for cross-currency payments",
                "key_fields": ["fx_rate_id", "source_currency", "target_currency"],
                "category": "Core",
            },
            {
                "table": "cdm_account_statement",
                "display_name": "Account Statement",
                "description": "Statement of account activity",
                "key_fields": ["statement_id", "account_id", "statement_date"],
                "category": "Core",
            },
            {
                "table": "cdm_transaction",
                "display_name": "Transaction",
                "description": "Individual transaction within a statement",
                "key_fields": ["transaction_id", "statement_id", "amount"],
                "category": "Core",
            },
            # Normalized identifier tables (ISO 20022 CDM enhancements)
            {
                "table": "cdm_party_identifier",
                "display_name": "Party Identifier",
                "description": "Normalized party identifiers (LEI, BIC, Tax ID, etc.)",
                "key_fields": ["identifier_id", "party_id", "identifier_type", "identifier_value"],
                "category": "Identifier",
            },
            {
                "table": "cdm_account_identifier",
                "display_name": "Account Identifier",
                "description": "Normalized account identifiers (IBAN, BBAN, Proxy, etc.)",
                "key_fields": ["identifier_id", "account_id", "identifier_type", "identifier_value"],
                "category": "Identifier",
            },
            {
                "table": "cdm_fi_identifier",
                "display_name": "FI Identifier",
                "description": "Normalized financial institution identifiers (BIC, ABA, Sort Code, etc.)",
                "key_fields": ["identifier_id", "fi_id", "identifier_type", "identifier_value"],
                "category": "Identifier",
            },
            {
                "table": "cdm_payment_identifier",
                "display_name": "Payment Identifier",
                "description": "Normalized payment identifiers (E2E ID, UETR, TX ID, etc.)",
                "key_fields": ["identifier_id", "instruction_id", "identifier_type", "identifier_value"],
                "category": "Identifier",
            },
        ]
    }


@router.post("/sync/{message_type}")
async def sync_mappings(
    message_type: str,
    force: bool = Query(False, description="Overwrite user-modified mappings"),
):
    """
    Sync YAML mapping file to database for a message type.

    By default, user-modified mappings (is_user_modified=true) are preserved.
    Use force=true to overwrite them (use with caution).
    """
    from gps_cdm.orchestration.mapping_sync import MappingSync

    sync = MappingSync()
    result = sync.sync_message_type(message_type, force=force)

    return {
        "status": "success" if not result.errors else "partial",
        "message_type": message_type,
        "silver": {
            "added": result.silver_added,
            "updated": result.silver_updated,
            "skipped": result.silver_skipped,
        },
        "gold": {
            "added": result.gold_added,
            "updated": result.gold_updated,
            "skipped": result.gold_skipped,
        },
        "errors": result.errors,
    }


@router.post("/sync-all")
async def sync_all_mappings(
    force: bool = Query(False, description="Overwrite user-modified mappings"),
):
    """
    Sync all YAML mapping files to database.

    By default, user-modified mappings are preserved.
    """
    from gps_cdm.orchestration.mapping_sync import MappingSync

    sync = MappingSync()
    results = sync.sync_all(force=force)

    summary = {
        "status": "success",
        "synced_types": len(results),
        "results": {msg_type: r.to_dict() for msg_type, r in results.items()},
    }

    # Check for errors
    all_errors = []
    for r in results.values():
        all_errors.extend(r.errors)
    if all_errors:
        summary["status"] = "partial"

    return summary


@router.get("/user-modified")
async def list_user_modified_mappings(
    message_type: Optional[str] = Query(None, description="Filter by message type"),
):
    """
    List all user-modified mappings.

    These mappings are preserved during YAML sync (unless force=true).
    """
    from gps_cdm.orchestration.mapping_sync import MappingSync

    sync = MappingSync()
    modified = sync.get_user_modified_mappings(message_type)

    return {
        "silver_count": len(modified['silver']),
        "gold_count": len(modified['gold']),
        "silver_mappings": modified['silver'],
        "gold_mappings": modified['gold'],
    }
