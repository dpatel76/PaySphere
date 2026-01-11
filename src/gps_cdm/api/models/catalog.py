"""
Pydantic models for CDM Catalog API.
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class AllowedValue(BaseModel):
    """An allowed value with its description."""
    value: str
    description: Optional[str] = None


class LegacyMapping(BaseModel):
    """A legacy format mapping for a catalog element."""
    format_id: str
    source_expression: Optional[str] = None
    transform_expression: Optional[str] = None
    entity_role: Optional[str] = None


class CatalogElement(BaseModel):
    """A CDM catalog element with full metadata."""
    catalog_id: int
    pde_table_name: str
    pde_column_name: str
    pde_data_type: Optional[str] = None
    pde_is_nullable: bool = True

    # Business metadata
    business_name: Optional[str] = None
    business_description: Optional[str] = None
    data_format: Optional[str] = None
    allowed_values: Optional[List[AllowedValue]] = None

    # ISO 20022 reference
    iso_element_name: Optional[str] = None
    iso_element_description: Optional[str] = None
    iso_element_path: Optional[str] = None
    iso_data_type: Optional[str] = None

    # Legacy format mappings
    legacy_mappings: List[LegacyMapping] = Field(default_factory=list)
    legacy_mapping_count: int = 0

    # Metadata
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class CatalogElementUpdate(BaseModel):
    """Fields that can be updated for a catalog element."""
    business_name: Optional[str] = None
    business_description: Optional[str] = None
    data_format: Optional[str] = None
    allowed_values: Optional[List[AllowedValue]] = None
    iso_element_name: Optional[str] = None
    iso_element_description: Optional[str] = None
    iso_element_path: Optional[str] = None
    iso_data_type: Optional[str] = None


class CatalogTableSummary(BaseModel):
    """Summary statistics for a CDM table in the catalog."""
    table_name: str
    display_name: str
    element_count: int
    documented_count: int
    iso_mapped_count: int
    documentation_pct: float
    sort_order: int


class CatalogStats(BaseModel):
    """Overall catalog statistics."""
    total_elements: int
    documented_elements: int
    iso_mapped_elements: int
    total_tables: int
    documentation_pct: float
    iso_mapping_pct: float


class CatalogSearchRequest(BaseModel):
    """Search request for catalog elements."""
    query: Optional[str] = None
    table_name: Optional[str] = None
    documented_only: bool = False
    limit: int = 500
    offset: int = 0


class CatalogSearchResponse(BaseModel):
    """Response for catalog search."""
    elements: List[CatalogElement]
    total_count: int
    limit: int
    offset: int


class CatalogExportRequest(BaseModel):
    """Request for catalog export."""
    table_names: Optional[List[str]] = None
    include_legacy_mappings: bool = True
    format: str = "xlsx"  # xlsx or csv
