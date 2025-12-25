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
    """List all supported message types with their lineage status."""
    from pathlib import Path

    mappings_dir = Path(__file__).parent.parent.parent.parent / "mappings" / "message_types"

    message_types = []
    for file in mappings_dir.glob("*.yaml"):
        name = file.stem
        message_types.append({
            "id": name,
            "display_name": name.upper().replace("_", " "),
            "file": file.name,
        })

    return {
        "supported_types": message_types,
        "count": len(message_types),
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
            {
                "table": "cdm_payment_instruction",
                "display_name": "Payment Instruction",
                "description": "Core payment transaction record",
                "key_fields": ["instruction_id", "end_to_end_id", "uetr"],
            },
            {
                "table": "cdm_party",
                "display_name": "Party",
                "description": "Customer, counterparty, or related party",
                "key_fields": ["party_id", "name", "tax_id"],
            },
            {
                "table": "cdm_account",
                "display_name": "Account",
                "description": "Bank account or financial account",
                "key_fields": ["account_id", "iban", "account_number"],
            },
            {
                "table": "cdm_financial_institution",
                "display_name": "Financial Institution",
                "description": "Bank or financial service provider",
                "key_fields": ["fi_id", "bic", "lei"],
            },
        ]
    }
