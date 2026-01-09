"""
GPS CDM API - Mappings Documentation Routes

Provides endpoints for viewing and managing field mappings documentation:
1. List all message formats with coverage stats
2. Get unified mappings documentation for a format
3. CRUD operations for standard fields, silver mappings, gold mappings
4. Coverage and gap analysis
"""

import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

router = APIRouter()


# =============================================================================
# Response Models
# =============================================================================

class MessageFormatSummary(BaseModel):
    format_id: str
    format_name: str
    format_category: str
    standard_name: Optional[str]
    country: Optional[str]
    governing_body: Optional[str]
    bronze_table: Optional[str]  # May be NULL for base/abstract formats
    silver_table: Optional[str]  # May be NULL for base/abstract formats
    gold_table: Optional[str]  # Primary gold table for format
    total_standard_fields: int
    mapped_to_silver: int
    mapped_to_gold: int
    silver_coverage_pct: Optional[float]
    gold_coverage_pct: Optional[float]
    unmapped_fields: int
    is_active: bool


class StandardFieldResponse(BaseModel):
    standard_field_id: int
    format_id: str
    field_name: str
    field_path: str
    field_tag: Optional[str]
    field_description: Optional[str]
    data_type: str
    min_length: Optional[int]
    max_length: Optional[int]
    allowed_values: Optional[str]
    is_mandatory: bool
    field_category: Optional[str]
    is_active: bool


class MappingDocumentationRow(BaseModel):
    """Unified row for mappings documentation table"""
    # Standard/Format Info
    standard_name: Optional[str]
    country: Optional[str]
    message_format: str
    message_format_description: str
    format_category: str
    governing_body: Optional[str]

    # Standard Field Info
    standard_field_id: Optional[int]
    standard_field_name: Optional[str]
    standard_field_description: Optional[str]
    standard_field_data_type: Optional[str]
    standard_field_allowed_values: Optional[str]
    standard_field_path: Optional[str]
    standard_field_tag: Optional[str]
    standard_field_mandatory: Optional[bool]
    field_category: Optional[str]

    # Bronze Info
    bronze_table: Optional[str]
    bronze_source_path: Optional[str]

    # Silver Mapping Info
    silver_mapping_id: Optional[int]
    silver_table: Optional[str]
    silver_column: Optional[str]
    silver_data_type: Optional[str]
    silver_max_length: Optional[int]
    silver_source_path: Optional[str]
    silver_transform: Optional[str]
    silver_is_required: Optional[bool]
    is_mapped_to_silver: bool

    # Gold Mapping Info
    gold_mapping_id: Optional[int]
    gold_table: Optional[str]
    gold_column: Optional[str]
    gold_data_type: Optional[str]
    gold_entity_role: Optional[str]
    gold_purpose_code: Optional[str]
    gold_source_expression: Optional[str]
    gold_transform: Optional[str]
    is_mapped_to_gold: bool

    # Metadata
    is_active: Optional[bool]
    last_updated: Optional[datetime]


class CoverageStats(BaseModel):
    format_id: str
    format_name: str
    total_standard_fields: int
    mandatory_fields: int
    mapped_to_silver: int
    mapped_to_gold: int
    silver_coverage_pct: Optional[float]
    gold_coverage_pct: Optional[float]
    unmapped_fields: int


class UnmappedField(BaseModel):
    format_id: str
    format_name: str
    field_name: str
    field_path: str
    field_description: Optional[str]
    data_type: Optional[str]
    is_mandatory: Optional[bool]
    field_category: Optional[str]
    gap_type: str


# =============================================================================
# Request Models for Updates
# =============================================================================

class StandardFieldUpdate(BaseModel):
    field_name: Optional[str] = None
    field_description: Optional[str] = None
    data_type: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: Optional[str] = None
    is_mandatory: Optional[bool] = None
    field_category: Optional[str] = None
    is_active: Optional[bool] = None


class StandardFieldCreate(BaseModel):
    format_id: str
    field_name: str
    field_path: str
    field_tag: Optional[str] = None
    field_description: Optional[str] = None
    data_type: str = "VARCHAR"
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: Optional[str] = None
    is_mandatory: bool = False
    field_category: Optional[str] = None


class SilverMappingUpdate(BaseModel):
    target_column: Optional[str] = None
    source_path: Optional[str] = None
    data_type: Optional[str] = None
    max_length: Optional[int] = None
    is_required: Optional[bool] = None
    default_value: Optional[str] = None
    transform_function: Optional[str] = None
    transform_expression: Optional[str] = None
    field_description: Optional[str] = None
    is_active: Optional[bool] = None


class SilverMappingCreate(BaseModel):
    format_id: str
    target_column: str
    source_path: str
    data_type: str = "VARCHAR"
    max_length: Optional[int] = None
    is_required: bool = False
    default_value: Optional[str] = None
    transform_function: Optional[str] = None
    transform_expression: Optional[str] = None
    ordinal_position: int
    standard_field_id: Optional[int] = None
    field_description: Optional[str] = None


class GoldMappingUpdate(BaseModel):
    gold_table: Optional[str] = None
    gold_column: Optional[str] = None
    source_expression: Optional[str] = None
    entity_role: Optional[str] = None
    data_type: Optional[str] = None
    is_required: Optional[bool] = None
    default_value: Optional[str] = None
    transform_expression: Optional[str] = None
    purpose_code: Optional[str] = None
    field_description: Optional[str] = None
    is_active: Optional[bool] = None


class GoldMappingCreate(BaseModel):
    format_id: str
    gold_table: str
    gold_column: str
    source_expression: str
    entity_role: Optional[str] = None
    data_type: str = "VARCHAR"
    is_required: bool = False
    default_value: Optional[str] = None
    transform_expression: Optional[str] = None
    ordinal_position: int
    purpose_code: Optional[str] = None
    field_description: Optional[str] = None


# =============================================================================
# Database Connection Helper
# =============================================================================

def get_db_connection():
    """Get PostgreSQL database connection."""
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5433)),
        database=os.environ.get("POSTGRES_DB", "gps_cdm"),
        user=os.environ.get("POSTGRES_USER", "gps_cdm_svc"),
        password=os.environ.get("POSTGRES_PASSWORD", "gps_cdm_password"),
    )


# =============================================================================
# Message Format Endpoints
# =============================================================================

@router.get("/formats", response_model=List[MessageFormatSummary])
async def list_message_formats(
    category: Optional[str] = Query(None, description="Filter by format category (ISO20022, SWIFT_MT, REGIONAL)"),
    country: Optional[str] = Query(None, description="Filter by country"),
    active_only: bool = Query(True, description="Only return active formats"),
):
    """
    List all message formats with coverage statistics.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                mf.format_id,
                mf.format_name,
                mf.format_category,
                mf.standard_name,
                mf.country,
                mf.governing_body,
                mf.bronze_table,
                mf.silver_table,
                mf.gold_table,
                mf.is_active,
                COALESCE(cov.total_standard_fields, 0) AS total_standard_fields,
                COALESCE(cov.mapped_to_silver, 0) AS mapped_to_silver,
                COALESCE(cov.mapped_to_gold, 0) AS mapped_to_gold,
                cov.silver_coverage_pct,
                cov.gold_coverage_pct,
                COALESCE(cov.unmapped_fields, 0) AS unmapped_fields
            FROM mapping.message_formats mf
            LEFT JOIN mapping.v_mapping_coverage cov ON mf.format_id = cov.format_id
            WHERE 1=1
        """
        params = []

        if active_only:
            query += " AND mf.is_active = TRUE"

        if category:
            query += " AND mf.format_category = %s"
            params.append(category)

        if country:
            query += " AND mf.country = %s"
            params.append(country)

        query += " ORDER BY mf.format_category, mf.format_id"

        cursor.execute(query, params)
        results = cursor.fetchall()

        return [MessageFormatSummary(**row) for row in results]
    finally:
        conn.close()


@router.get("/formats/{format_id}")
async def get_message_format(format_id: str):
    """
    Get details for a specific message format.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT
                mf.*,
                COALESCE(cov.total_standard_fields, 0) AS total_standard_fields,
                COALESCE(cov.mapped_to_silver, 0) AS mapped_to_silver,
                COALESCE(cov.mapped_to_gold, 0) AS mapped_to_gold,
                cov.silver_coverage_pct,
                cov.gold_coverage_pct
            FROM mapping.message_formats mf
            LEFT JOIN mapping.v_mapping_coverage cov ON mf.format_id = cov.format_id
            WHERE mf.format_id = %s
        """, (format_id,))

        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail=f"Message format not found: {format_id}")

        return dict(result)
    finally:
        conn.close()


# =============================================================================
# Mappings Documentation Endpoints
# =============================================================================

@router.get("/documentation/{format_id}", response_model=List[MappingDocumentationRow])
async def get_mappings_documentation(
    format_id: str,
    field_category: Optional[str] = Query(None, description="Filter by field category"),
    mapped_only: bool = Query(False, description="Only return mapped fields"),
    unmapped_only: bool = Query(False, description="Only return unmapped fields"),
):
    """
    Get unified mappings documentation for a message format.

    Returns all standard fields with their silver and gold mappings.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT *
            FROM mapping.v_mappings_documentation
            WHERE message_format = %s
        """
        params = [format_id]

        if field_category:
            query += " AND field_category = %s"
            params.append(field_category)

        if mapped_only:
            query += " AND is_mapped_to_silver = TRUE"

        if unmapped_only:
            query += " AND is_mapped_to_silver = FALSE"

        query += " ORDER BY field_category, standard_field_name"

        cursor.execute(query, params)
        results = cursor.fetchall()

        if not results:
            # Check if format exists
            cursor.execute("SELECT 1 FROM mapping.message_formats WHERE format_id = %s", (format_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Message format not found: {format_id}")

        return [MappingDocumentationRow(**row) for row in results]
    finally:
        conn.close()


@router.get("/coverage", response_model=List[CoverageStats])
async def get_coverage_stats(
    format_id: Optional[str] = Query(None, description="Filter by specific format"),
):
    """
    Get mapping coverage statistics for all or specific formats.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = "SELECT * FROM mapping.v_mapping_coverage"
        params = []

        if format_id:
            query += " WHERE format_id = %s"
            params.append(format_id)

        query += " ORDER BY format_id"

        cursor.execute(query, params)
        results = cursor.fetchall()

        return [CoverageStats(**row) for row in results]
    finally:
        conn.close()


@router.get("/unmapped", response_model=List[UnmappedField])
async def get_unmapped_fields(
    format_id: Optional[str] = Query(None, description="Filter by specific format"),
    gap_type: Optional[str] = Query(None, description="Filter by gap type (NOT_MAPPED_TO_SILVER, NOT_MAPPED_TO_GOLD)"),
    mandatory_only: bool = Query(False, description="Only return mandatory fields"),
):
    """
    Get list of unmapped fields for gap analysis.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = "SELECT * FROM mapping.v_unmapped_fields WHERE 1=1"
        params = []

        if format_id:
            query += " AND format_id = %s"
            params.append(format_id)

        if gap_type:
            query += " AND gap_type = %s"
            params.append(gap_type)

        if mandatory_only:
            query += " AND is_mandatory = TRUE"

        query += " ORDER BY format_id, gap_type, field_name"

        cursor.execute(query, params)
        results = cursor.fetchall()

        return [UnmappedField(**row) for row in results]
    finally:
        conn.close()


# =============================================================================
# Standard Fields CRUD
# =============================================================================

@router.get("/standard-fields/{format_id}", response_model=List[StandardFieldResponse])
async def list_standard_fields(
    format_id: str,
    category: Optional[str] = Query(None, description="Filter by field category"),
    active_only: bool = Query(True, description="Only return active fields"),
):
    """
    List all standard fields for a message format.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT * FROM mapping.standard_fields
            WHERE format_id = %s
        """
        params = [format_id]

        if active_only:
            query += " AND is_active = TRUE"

        if category:
            query += " AND field_category = %s"
            params.append(category)

        query += " ORDER BY field_category, field_name"

        cursor.execute(query, params)
        results = cursor.fetchall()

        return [StandardFieldResponse(**row) for row in results]
    finally:
        conn.close()


@router.post("/standard-fields", response_model=StandardFieldResponse)
async def create_standard_field(field: StandardFieldCreate):
    """
    Create a new standard field definition.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            INSERT INTO mapping.standard_fields
            (format_id, field_name, field_path, field_tag, field_description,
             data_type, min_length, max_length, allowed_values, is_mandatory, field_category)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            field.format_id, field.field_name, field.field_path, field.field_tag,
            field.field_description, field.data_type, field.min_length,
            field.max_length, field.allowed_values, field.is_mandatory, field.field_category
        ))

        result = cursor.fetchone()
        conn.commit()

        return StandardFieldResponse(**result)
    except psycopg2.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Field already exists or invalid format_id: {str(e)}")
    finally:
        conn.close()


@router.put("/standard-fields/{field_id}", response_model=StandardFieldResponse)
async def update_standard_field(
    field_id: int,
    updates: StandardFieldUpdate,
    updated_by: str = Query("API_USER", description="User making the update"),
):
    """
    Update a standard field definition.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Build dynamic update query
        update_fields = []
        params = []

        for field_name, value in updates.model_dump(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field_name} = %s")
                params.append(value)

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        update_fields.append("updated_by = %s")
        params.append(updated_by)
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(field_id)

        query = f"""
            UPDATE mapping.standard_fields
            SET {', '.join(update_fields)}
            WHERE standard_field_id = %s
            RETURNING *
        """

        cursor.execute(query, params)
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail=f"Standard field not found: {field_id}")

        conn.commit()
        return StandardFieldResponse(**result)
    finally:
        conn.close()


@router.delete("/standard-fields/{field_id}")
async def delete_standard_field(field_id: int, soft_delete: bool = Query(True)):
    """
    Delete or deactivate a standard field.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        if soft_delete:
            cursor.execute("""
                UPDATE mapping.standard_fields
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE standard_field_id = %s
            """, (field_id,))
        else:
            cursor.execute("""
                DELETE FROM mapping.standard_fields
                WHERE standard_field_id = %s
            """, (field_id,))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Standard field not found: {field_id}")

        conn.commit()
        return {"status": "success", "deleted": field_id, "soft_delete": soft_delete}
    finally:
        conn.close()


# =============================================================================
# Silver Mappings CRUD
# =============================================================================

@router.get("/silver-mappings/{format_id}")
async def list_silver_mappings(
    format_id: str,
    active_only: bool = Query(True),
):
    """
    List all silver field mappings for a message format.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT * FROM mapping.silver_field_mappings
            WHERE format_id = %s
        """
        params = [format_id]

        if active_only:
            query += " AND is_active = TRUE"

        query += " ORDER BY ordinal_position"

        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()


@router.post("/silver-mappings")
async def create_silver_mapping(mapping: SilverMappingCreate):
    """
    Create a new silver field mapping.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            INSERT INTO mapping.silver_field_mappings
            (format_id, target_column, source_path, data_type, max_length,
             is_required, default_value, transform_function, transform_expression,
             ordinal_position, standard_field_id, field_description, is_user_modified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            RETURNING *
        """, (
            mapping.format_id, mapping.target_column, mapping.source_path,
            mapping.data_type, mapping.max_length, mapping.is_required,
            mapping.default_value, mapping.transform_function, mapping.transform_expression,
            mapping.ordinal_position, mapping.standard_field_id, mapping.field_description
        ))

        result = cursor.fetchone()
        conn.commit()

        return dict(result)
    except psycopg2.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Mapping already exists: {str(e)}")
    finally:
        conn.close()


@router.put("/silver-mappings/{mapping_id}")
async def update_silver_mapping(
    mapping_id: int,
    updates: SilverMappingUpdate,
    updated_by: str = Query("API_USER"),
):
    """
    Update a silver field mapping.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        update_fields = []
        params = []

        for field_name, value in updates.model_dump(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field_name} = %s")
                params.append(value)

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        update_fields.append("updated_by = %s")
        params.append(updated_by)
        update_fields.append("is_user_modified = TRUE")
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(mapping_id)

        query = f"""
            UPDATE mapping.silver_field_mappings
            SET {', '.join(update_fields)}
            WHERE mapping_id = %s
            RETURNING *
        """

        cursor.execute(query, params)
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail=f"Silver mapping not found: {mapping_id}")

        conn.commit()
        return dict(result)
    finally:
        conn.close()


@router.delete("/silver-mappings/{mapping_id}")
async def delete_silver_mapping(mapping_id: int, soft_delete: bool = Query(True)):
    """
    Delete or deactivate a silver mapping.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        if soft_delete:
            cursor.execute("""
                UPDATE mapping.silver_field_mappings
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE mapping_id = %s
            """, (mapping_id,))
        else:
            cursor.execute("""
                DELETE FROM mapping.silver_field_mappings
                WHERE mapping_id = %s
            """, (mapping_id,))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Silver mapping not found: {mapping_id}")

        conn.commit()
        return {"status": "success", "deleted": mapping_id, "soft_delete": soft_delete}
    finally:
        conn.close()


# =============================================================================
# Gold Mappings CRUD
# =============================================================================

@router.get("/gold-mappings/{format_id}")
async def list_gold_mappings(
    format_id: str,
    gold_table: Optional[str] = Query(None, description="Filter by gold table"),
    entity_role: Optional[str] = Query(None, description="Filter by entity role"),
    active_only: bool = Query(True),
):
    """
    List all gold field mappings for a message format.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT * FROM mapping.gold_field_mappings
            WHERE format_id = %s
        """
        params = [format_id]

        if active_only:
            query += " AND is_active = TRUE"

        if gold_table:
            query += " AND gold_table = %s"
            params.append(gold_table)

        if entity_role:
            query += " AND entity_role = %s"
            params.append(entity_role)

        query += " ORDER BY gold_table, entity_role, ordinal_position"

        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()


@router.post("/gold-mappings")
async def create_gold_mapping(mapping: GoldMappingCreate):
    """
    Create a new gold field mapping.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            INSERT INTO mapping.gold_field_mappings
            (format_id, gold_table, gold_column, source_expression, entity_role,
             data_type, is_required, default_value, transform_expression,
             ordinal_position, purpose_code, field_description, is_user_modified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            RETURNING *
        """, (
            mapping.format_id, mapping.gold_table, mapping.gold_column,
            mapping.source_expression, mapping.entity_role, mapping.data_type,
            mapping.is_required, mapping.default_value, mapping.transform_expression,
            mapping.ordinal_position, mapping.purpose_code, mapping.field_description
        ))

        result = cursor.fetchone()
        conn.commit()

        return dict(result)
    except psycopg2.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Mapping already exists: {str(e)}")
    finally:
        conn.close()


@router.put("/gold-mappings/{mapping_id}")
async def update_gold_mapping(
    mapping_id: int,
    updates: GoldMappingUpdate,
    updated_by: str = Query("API_USER"),
):
    """
    Update a gold field mapping.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        update_fields = []
        params = []

        for field_name, value in updates.model_dump(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field_name} = %s")
                params.append(value)

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        update_fields.append("updated_by = %s")
        params.append(updated_by)
        update_fields.append("is_user_modified = TRUE")
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(mapping_id)

        query = f"""
            UPDATE mapping.gold_field_mappings
            SET {', '.join(update_fields)}
            WHERE mapping_id = %s
            RETURNING *
        """

        cursor.execute(query, params)
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail=f"Gold mapping not found: {mapping_id}")

        conn.commit()
        return dict(result)
    finally:
        conn.close()


@router.delete("/gold-mappings/{mapping_id}")
async def delete_gold_mapping(mapping_id: int, soft_delete: bool = Query(True)):
    """
    Delete or deactivate a gold mapping.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        if soft_delete:
            cursor.execute("""
                UPDATE mapping.gold_field_mappings
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE mapping_id = %s
            """, (mapping_id,))
        else:
            cursor.execute("""
                DELETE FROM mapping.gold_field_mappings
                WHERE mapping_id = %s
            """, (mapping_id,))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Gold mapping not found: {mapping_id}")

        conn.commit()
        return {"status": "success", "deleted": mapping_id, "soft_delete": soft_delete}
    finally:
        conn.close()


# =============================================================================
# Field Categories
# =============================================================================

@router.get("/field-categories/{format_id}")
async def get_field_categories(format_id: str):
    """
    Get distinct field categories for a message format.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT DISTINCT field_category, COUNT(*) as field_count
            FROM mapping.standard_fields
            WHERE format_id = %s AND is_active = TRUE AND field_category IS NOT NULL
            GROUP BY field_category
            ORDER BY field_category
        """, (format_id,))

        return cursor.fetchall()
    finally:
        conn.close()


# =============================================================================
# Export Endpoints
# =============================================================================

@router.get("/export/{format_id}")
async def export_mappings(
    format_id: str,
    format_type: str = Query("json", description="Export format: json, csv"),
):
    """
    Export mappings documentation for a format.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT * FROM mapping.v_mappings_documentation
            WHERE message_format = %s
            ORDER BY field_category, standard_field_name
        """, (format_id,))

        results = cursor.fetchall()

        if format_type == "csv":
            import csv
            import io

            output = io.StringIO()
            if results:
                writer = csv.DictWriter(output, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)

            return {
                "format": "csv",
                "data": output.getvalue(),
                "row_count": len(results),
            }
        else:
            return {
                "format": "json",
                "data": results,
                "row_count": len(results),
            }
    finally:
        conn.close()
