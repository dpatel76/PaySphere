"""
GPS CDM API - Schema Routes

Provides endpoints for schema information:
1. List supported message types
2. Get message type schema from YAML mappings
3. Get display configuration for tables
"""

from typing import List, Dict, Any, Optional
from functools import lru_cache
from pathlib import Path
import yaml

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel


router = APIRouter()

# Base path for mapping files
MAPPINGS_BASE_PATH = Path(__file__).parent.parent.parent.parent.parent.parent / "mappings" / "message_types"


# Response Models
class FieldSchema(BaseModel):
    field_name: str
    source_path: Optional[str] = None
    data_type: str
    required: bool = False
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    description: Optional[str] = None
    transform: Optional[Dict[str, Any]] = None


class TableSchema(BaseModel):
    table_name: str
    layer: str
    primary_key: str
    fields: List[FieldSchema]


class MessageTypeSchema(BaseModel):
    message_type: str
    name: str
    version: Optional[str] = None
    description: Optional[str] = None
    bronze_table: str
    silver_tables: List[str]
    gold_tables: List[str]
    field_count: int
    bronze_to_silver_fields: List[FieldSchema]
    silver_to_gold_fields: List[FieldSchema]
    validations: List[Dict[str, Any]]


class MessageTypeSummary(BaseModel):
    message_type: str
    name: str
    version: Optional[str] = None
    field_count: int
    has_mappings: bool


class FieldDisplayConfig(BaseModel):
    field_name: str
    display_name: str
    data_type: str
    width: int = 150
    sortable: bool = True
    filterable: bool = True
    render_type: str = "text"
    format: Optional[str] = None


class TableDisplayConfig(BaseModel):
    table_name: str
    layer: str
    primary_key: str
    display_columns: List[FieldDisplayConfig]
    editable_fields: List[str] = []


@lru_cache(maxsize=32)
def load_mapping_file(message_type: str) -> Optional[Dict]:
    """Load and cache a mapping file."""
    # Normalize message type name for file lookup
    file_name = message_type.lower().replace(".", "").replace("-", "") + ".yaml"
    file_path = MAPPINGS_BASE_PATH / file_name

    if not file_path.exists():
        # Try alternate naming conventions
        alternatives = [
            message_type.lower().replace(".", "_") + ".yaml",
            message_type.lower() + ".yaml",
        ]
        for alt in alternatives:
            alt_path = MAPPINGS_BASE_PATH / alt
            if alt_path.exists():
                file_path = alt_path
                break
        else:
            return None

    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def get_available_message_types() -> List[str]:
    """Get list of available message types from mapping files."""
    if not MAPPINGS_BASE_PATH.exists():
        return []

    message_types = []
    for yaml_file in MAPPINGS_BASE_PATH.glob("*.yaml"):
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                if data and 'mapping' in data:
                    mt = data['mapping'].get('message_type')
                    if mt:
                        message_types.append(mt)
        except Exception:
            continue

    return sorted(set(message_types))


def parse_field_to_schema(field: Dict) -> FieldSchema:
    """Convert a field mapping to FieldSchema."""
    return FieldSchema(
        field_name=field.get('target', field.get('source', '')),
        source_path=field.get('source'),
        data_type=field.get('type', 'string'),
        required=field.get('required', False),
        max_length=field.get('max_length'),
        precision=field.get('precision'),
        scale=field.get('scale'),
        transform=field.get('transform'),
    )


def infer_render_type(field: FieldSchema) -> str:
    """Infer the render type for a field based on its data type."""
    type_map = {
        'decimal': 'currency',
        'timestamp': 'datetime',
        'date': 'date',
        'boolean': 'chip',
        'json': 'json',
        'integer': 'text',
    }
    return type_map.get(field.data_type, 'text')


def field_name_to_display_name(field_name: str) -> str:
    """Convert a field name to a display name."""
    # Convert snake_case to Title Case
    return ' '.join(word.capitalize() for word in field_name.split('_'))


@router.get("/message-types", response_model=List[MessageTypeSummary])
async def list_message_types():
    """List all supported message types with summaries."""
    message_types = get_available_message_types()

    summaries = []
    for mt in message_types:
        data = load_mapping_file(mt)
        if data and 'mapping' in data:
            mapping = data['mapping']
            b2s_fields = mapping.get('bronze_to_silver', {}).get('fields', [])
            s2g_fields = mapping.get('silver_to_gold', {}).get('fields', [])
            summaries.append(MessageTypeSummary(
                message_type=mapping.get('message_type', mt),
                name=mapping.get('name', mt),
                version=mapping.get('message_version'),
                field_count=len(b2s_fields) + len(s2g_fields),
                has_mappings=True,
            ))

    return summaries


@router.get("/message-types/{message_type}", response_model=MessageTypeSchema)
async def get_message_type_schema(message_type: str):
    """Get full schema for a message type."""
    data = load_mapping_file(message_type)
    if not data or 'mapping' not in data:
        raise HTTPException(status_code=404, detail=f"Message type '{message_type}' not found")

    mapping = data['mapping']
    b2s = mapping.get('bronze_to_silver', {})
    s2g = mapping.get('silver_to_gold', {})

    b2s_fields = [parse_field_to_schema(f) for f in b2s.get('fields', [])]
    s2g_fields = [parse_field_to_schema(f) for f in s2g.get('fields', [])]

    # Extract table names
    bronze_table = b2s.get('source', {}).get('table', 'raw_payment_messages')
    silver_table = b2s.get('target', {}).get('table', 'stg_' + message_type.replace('.', ''))
    gold_table = s2g.get('target', {}).get('table', 'cdm_payment_instruction')

    return MessageTypeSchema(
        message_type=mapping.get('message_type', message_type),
        name=mapping.get('name', message_type),
        version=mapping.get('message_version'),
        description=mapping.get('description'),
        bronze_table=bronze_table,
        silver_tables=[silver_table],
        gold_tables=[gold_table],
        field_count=len(b2s_fields) + len(s2g_fields),
        bronze_to_silver_fields=b2s_fields,
        silver_to_gold_fields=s2g_fields,
        validations=mapping.get('validations', []),
    )


@router.get("/tables/{layer}/{table_name}", response_model=TableDisplayConfig)
async def get_table_display_config(
    layer: str,
    table_name: str,
    message_type: Optional[str] = Query(None, description="Filter by message type"),
):
    """Get display configuration for a table."""
    # Try to find the table in mapping files
    message_types = get_available_message_types() if not message_type else [message_type]

    for mt in message_types:
        data = load_mapping_file(mt)
        if not data or 'mapping' not in data:
            continue

        mapping = data['mapping']
        b2s = mapping.get('bronze_to_silver', {})
        s2g = mapping.get('silver_to_gold', {})

        # Check if this mapping matches the requested table
        fields = []
        primary_key = ""

        if layer == "bronze" and b2s.get('source', {}).get('table') == table_name:
            # For bronze, we don't have explicit field definitions
            primary_key = "raw_id"
            fields = [
                FieldDisplayConfig(field_name="raw_id", display_name="Raw ID", data_type="string", width=140),
                FieldDisplayConfig(field_name="message_type", display_name="Message Type", data_type="string", width=120),
                FieldDisplayConfig(field_name="source_system", display_name="Source", data_type="string", width=100),
                FieldDisplayConfig(field_name="processing_status", display_name="Status", data_type="string", width=120, render_type="chip"),
                FieldDisplayConfig(field_name="ingested_at", display_name="Ingested At", data_type="timestamp", width=160, render_type="datetime"),
            ]

        elif layer == "silver" and b2s.get('target', {}).get('table') == table_name:
            primary_key = "stg_id"
            for field_def in b2s.get('fields', []):
                target = field_def.get('target')
                if target:
                    field = FieldSchema(
                        field_name=target,
                        data_type=field_def.get('type', 'string'),
                        required=field_def.get('required', False),
                        max_length=field_def.get('max_length'),
                    )
                    fields.append(FieldDisplayConfig(
                        field_name=target,
                        display_name=field_name_to_display_name(target),
                        data_type=field.data_type,
                        width=min(200, max(100, (field.max_length or 50) * 3)),
                        render_type=infer_render_type(field),
                    ))

        elif layer == "gold" and s2g.get('target', {}).get('table') == table_name:
            primary_key = "instruction_id"
            for field_def in s2g.get('fields', []):
                target = field_def.get('target')
                if target:
                    field = FieldSchema(
                        field_name=target,
                        data_type=field_def.get('type', 'string'),
                        required=field_def.get('required', False),
                    )
                    fields.append(FieldDisplayConfig(
                        field_name=target,
                        display_name=field_name_to_display_name(target),
                        data_type=field.data_type,
                        width=150,
                        render_type=infer_render_type(field),
                    ))

        if fields:
            return TableDisplayConfig(
                table_name=table_name,
                layer=layer,
                primary_key=primary_key,
                display_columns=fields[:20],  # Limit to first 20 columns for display
                editable_fields=[],  # Could be derived from mapping validation rules
            )

    raise HTTPException(status_code=404, detail=f"Table '{layer}.{table_name}' not found")


@router.get("/field-lineage/{message_type}/{field_name}")
async def get_field_lineage(message_type: str, field_name: str):
    """Get field lineage across layers for a specific field."""
    data = load_mapping_file(message_type)
    if not data or 'mapping' not in data:
        raise HTTPException(status_code=404, detail=f"Message type '{message_type}' not found")

    mapping = data['mapping']
    b2s = mapping.get('bronze_to_silver', {})
    s2g = mapping.get('silver_to_gold', {})

    lineage = {
        "message_type": message_type,
        "field_name": field_name,
        "variations": {},
        "transformations": {},
    }

    # Find in bronze_to_silver mappings
    for field in b2s.get('fields', []):
        if field.get('target') == field_name or field.get('source', '').endswith(field_name):
            lineage["variations"]["bronze"] = {
                "table": b2s.get('source', {}).get('table', 'raw_payment_messages'),
                "field": field.get('source', field_name),
                "path": field.get('source'),
            }
            lineage["variations"]["silver"] = {
                "table": b2s.get('target', {}).get('table'),
                "field": field.get('target'),
            }
            if field.get('transform'):
                lineage["transformations"]["bronze_to_silver"] = field.get('transform')
            break

    # Find in silver_to_gold mappings
    for field in s2g.get('fields', []):
        if field.get('source') == field_name or field.get('target') == field_name:
            if "silver" not in lineage["variations"]:
                lineage["variations"]["silver"] = {
                    "table": s2g.get('source', {}).get('table'),
                    "field": field.get('source'),
                }
            lineage["variations"]["gold"] = {
                "table": s2g.get('target', {}).get('table'),
                "field": field.get('target'),
            }
            if field.get('transform'):
                lineage["transformations"]["silver_to_gold"] = field.get('transform')
            break

    if not lineage["variations"]:
        raise HTTPException(status_code=404, detail=f"Field '{field_name}' not found in message type '{message_type}'")

    return lineage


@router.get("/validations/{message_type}")
async def get_message_type_validations(message_type: str):
    """Get validation rules for a message type."""
    data = load_mapping_file(message_type)
    if not data or 'mapping' not in data:
        raise HTTPException(status_code=404, detail=f"Message type '{message_type}' not found")

    mapping = data['mapping']
    validations = mapping.get('validations', [])

    return {
        "message_type": message_type,
        "validations": validations,
        "quality": mapping.get('quality', {}),
    }
