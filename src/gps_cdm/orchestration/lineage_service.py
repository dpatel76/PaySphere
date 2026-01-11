"""
GPS CDM - Data Lineage Service
===============================

Provides comprehensive data lineage visualization:
1. Lineage mappings across Bronze → Silver → Gold by message type
2. Field-level lineage with filtering
3. Backward lineage from CDM entity to source
4. Backward lineage from reporting views
5. Support for multiple message types

Usage:
    service = LineageService(db_connection)

    # Get lineage for a message type
    lineage = service.get_message_type_lineage("pain.001")

    # Get field-level lineage
    field_lineage = service.get_field_lineage("pain.001", field_name="debtor_name")

    # Get backward lineage from CDM entity
    backward = service.get_backward_lineage_from_cdm("cdm_party", "name")
"""

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class LineageDirection(str, Enum):
    """Lineage direction."""
    FORWARD = "forward"   # Source → Target
    BACKWARD = "backward"  # Target → Source


@dataclass
class FieldLineage:
    """Lineage for a single field."""
    source_layer: str
    source_table: str
    source_field: str
    source_path: Optional[str]  # XPath or JSON path
    target_layer: str
    target_table: str
    target_field: str
    transformation_type: Optional[str]
    transformation_logic: Optional[str]
    data_type: str
    message_type: str
    entity_role: Optional[str] = None  # Role for entity-based mappings (DEBTOR, CREDITOR, etc.)


@dataclass
class EntityLineage:
    """Lineage for a CDM entity."""
    entity_table: str
    entity_field: str
    source_mappings: List[FieldLineage]  # Multiple sources per entity field
    message_types: List[str]


@dataclass
class LayerLineage:
    """Lineage between two layers."""
    source_layer: str
    source_table: str
    target_layer: str
    target_table: str
    field_mappings: List[FieldLineage]
    message_type: str


@dataclass
class FullLineage:
    """Complete lineage from source to gold."""
    message_type: str
    bronze_to_silver: LayerLineage
    silver_to_gold: LayerLineage
    entity_mappings: Dict[str, List[FieldLineage]]  # party, account, fi mappings


class LineageService:
    """
    Provides data lineage visualization and querying.

    Data source priority:
    1. Database mapping tables (mapping.silver_field_mappings, mapping.gold_field_mappings)
       - Single source of truth for runtime
       - Populated from YAML during deployment via sync script
    2. YAML mapping files (fallback if database unavailable)
       - Design-time documentation
       - Should be synced to database before production use

    Uses both forward (source→target) and backward (target→source) queries.
    """

    def __init__(self, db_connection=None, mappings_dir: str = None):
        """
        Initialize lineage service.

        Args:
            db_connection: Database connection for persisted lineage
            mappings_dir: Directory containing YAML mapping files
        """
        self.db = db_connection
        self.mappings_dir = Path(mappings_dir) if mappings_dir else None
        self._lineage_cache: Dict[str, FullLineage] = {}
        self._use_database = True  # Prefer database over YAML

    def _get_db_connection(self):
        """Get or create database connection."""
        if self.db:
            return self.db
        # Create connection from environment
        import os
        import psycopg2
        try:
            return psycopg2.connect(
                host=os.environ.get("POSTGRES_HOST", "localhost"),
                port=int(os.environ.get("POSTGRES_PORT", 5433)),
                database=os.environ.get("POSTGRES_DB", "gps_cdm"),
                user=os.environ.get("POSTGRES_USER", "gps_cdm_svc"),
                password=os.environ.get("POSTGRES_PASSWORD", "gps_cdm_password"),
            )
        except Exception:
            return None

    def _load_lineage_from_database(self, message_type: str) -> Optional[FullLineage]:
        """Load lineage from database mapping tables using effective mappings (includes inheritance)."""
        conn = self._get_db_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()

            # First, get the actual Silver and Gold table names from message_formats table
            cursor.execute("""
                SELECT silver_table, gold_table
                FROM mapping.message_formats
                WHERE format_id = %s AND is_active = true
            """, (message_type,))
            row = cursor.fetchone()
            silver_table = row[0] if row and row[0] else f"stg_{message_type.replace('.', '').lower()}"
            gold_table = row[1] if row and row[1] else "cdm_payment_instruction"

            # Get bronze→silver mappings from effective mappings view (includes inherited mappings)
            # This view resolves the inheritance hierarchy to provide all applicable mappings
            cursor.execute("""
                SELECT source_path, target_column, transform_expression,
                       is_inherited, effective_from_format
                FROM mapping.v_effective_silver_mappings
                WHERE format_id = %s
                ORDER BY target_column
            """, (message_type,))

            b2s_fields = []
            for row in cursor.fetchall():
                source_path = row[0] or ""
                target_column = row[1]
                transform_expr = row[2]
                is_inherited = row[3]
                effective_from = row[4]
                # Extract field name from path (e.g., "GrpHdr/MsgId" -> "MsgId")
                source_field = source_path.split('/')[-1] if source_path and '/' in source_path else source_path
                b2s_fields.append(FieldLineage(
                    source_layer="bronze",
                    source_table="raw_payment_messages",
                    source_field=source_field,
                    source_path=source_path,
                    target_layer="silver",
                    target_table=silver_table,
                    target_field=target_column,
                    transformation_type="inherited" if is_inherited else None,
                    transformation_logic=transform_expr,
                    data_type="string",
                    message_type=message_type,
                ))

            # Get silver→gold mappings from effective mappings view (includes inherited mappings)
            # This view resolves the inheritance hierarchy to provide all applicable mappings
            # Note: %% is needed to escape % for psycopg2 when using LIKE patterns
            cursor.execute("""
                SELECT source_expression, gold_table, gold_column, entity_role,
                       transform_expression, is_inherited, effective_from_format
                FROM mapping.v_effective_gold_mappings
                WHERE format_id = %s
                ORDER BY
                    CASE
                        WHEN gold_table LIKE 'cdm_pacs%%' OR gold_table LIKE 'cdm_pain%%'
                             OR gold_table LIKE 'cdm_camt%%' THEN 1
                        WHEN gold_table = 'cdm_party' THEN 2
                        WHEN gold_table = 'cdm_financial_institution' THEN 3
                        WHEN gold_table = 'cdm_account' THEN 4
                        ELSE 5
                    END,
                    gold_table, gold_column
            """, (message_type,))

            s2g_fields = []
            entity_mappings: Dict[str, List[FieldLineage]] = {}
            for row in cursor.fetchall():
                source_expression = row[0]
                target_gold_table = row[1]
                gold_column = row[2]
                entity_role = row[3]
                transform_expr = row[4]
                is_inherited = row[5]
                effective_from = row[6]

                field = FieldLineage(
                    source_layer="silver",
                    source_table=silver_table,
                    source_field=source_expression,
                    source_path=None,
                    target_layer="gold",
                    target_table=target_gold_table,
                    target_field=gold_column,
                    transformation_type="inherited" if is_inherited else None,
                    transformation_logic=transform_expr,
                    data_type="string",
                    message_type=message_type,
                    entity_role=entity_role,  # Include entity role for role-based mappings
                )
                # Group by entity role if specified (e.g., 'DEBTOR', 'CREDITOR')
                if entity_role:
                    if entity_role not in entity_mappings:
                        entity_mappings[entity_role] = []
                    entity_mappings[entity_role].append(field)
                else:
                    s2g_fields.append(field)

            cursor.close()
            if not self.db:
                conn.close()

            # Only return if we found data
            if not b2s_fields and not s2g_fields and not entity_mappings:
                return None

            b2s = LayerLineage(
                source_layer="bronze",
                source_table="raw_payment_messages",
                target_layer="silver",
                target_table=silver_table,
                field_mappings=b2s_fields,
                message_type=message_type,
            ) if b2s_fields else None

            s2g = LayerLineage(
                source_layer="silver",
                source_table=silver_table,
                target_layer="gold",
                target_table=gold_table,  # Use the actual gold table from message_formats
                field_mappings=s2g_fields,
                message_type=message_type,
            ) if s2g_fields else None

            return FullLineage(
                message_type=message_type,
                bronze_to_silver=b2s,
                silver_to_gold=s2g,
                entity_mappings=entity_mappings,
            )

        except Exception as e:
            import logging
            logging.warning(f"Failed to load lineage from database for {message_type}: {e}")
            return None

    def get_message_type_lineage(self, message_type: str) -> Optional[FullLineage]:
        """
        Get complete lineage for a message type.

        Data source priority:
        1. Database mapping tables (single source of truth)
        2. YAML files (fallback for development/testing)

        Args:
            message_type: Message type (e.g., "pain.001", "MT103")

        Returns:
            FullLineage with all mappings from bronze to gold
        """
        # Check cache
        if message_type in self._lineage_cache:
            return self._lineage_cache[message_type]

        lineage = None

        # Try database first (single source of truth)
        if self._use_database:
            lineage = self._load_lineage_from_database(message_type)

        # Fallback to YAML files if database unavailable or empty
        if not lineage:
            lineage = self._load_lineage_from_mapping(message_type)

        if lineage:
            self._lineage_cache[message_type] = lineage

        return lineage

    def _load_lineage_from_mapping(self, message_type: str) -> Optional[FullLineage]:
        """Load lineage from YAML mapping file."""
        if not self.mappings_dir:
            # Default path
            self.mappings_dir = Path(__file__).parent.parent.parent.parent / "mappings" / "message_types"

        # Map message type to file - includes all 29 available YAML mapping files
        file_map = {
            # ISO 20022 Core
            "pain.001": "pain001.yaml",
            "pain001": "pain001.yaml",
            "pain.002": "pain002.yaml",
            "pain002": "pain002.yaml",
            "pacs.008": "pacs008.yaml",
            "pacs008": "pacs008.yaml",
            "pacs.009": "pacs009.yaml",
            "pacs009": "pacs009.yaml",
            "pacs.002": "pacs002.yaml",
            "pacs002": "pacs002.yaml",
            "camt.053": "camt053.yaml",
            "camt053": "camt053.yaml",
            # NOTE: All SWIFT MT messages decommissioned Nov 2025 - use ISO 20022 equivalents
            # US Regional
            "FEDWIRE": "fedwire.yaml",
            "fedwire": "fedwire.yaml",
            "ACH": "ach.yaml",
            "ach": "ach.yaml",
            "CHIPS": "chips.yaml",
            "chips": "chips.yaml",
            "RTP": "rtp.yaml",
            "rtp": "rtp.yaml",
            "FEDNOW": "fednow.yaml",
            "fednow": "fednow.yaml",
            # EU Regional
            "SEPA": "sepa.yaml",
            "sepa": "sepa.yaml",
            "TARGET2": "target2.yaml",
            "target2": "target2.yaml",
            # UK Regional
            "CHAPS": "chaps.yaml",
            "chaps": "chaps.yaml",
            "FPS": "fps.yaml",
            "fps": "fps.yaml",
            "BACS": "bacs.yaml",
            "bacs": "bacs.yaml",
            # Asia-Pacific
            "NPP": "npp.yaml",
            "npp": "npp.yaml",
            "MEPS_PLUS": "meps_plus.yaml",
            "meps_plus": "meps_plus.yaml",
            "RTGS_HK": "rtgs_hk.yaml",
            "rtgs_hk": "rtgs_hk.yaml",
            "CNAPS": "cnaps.yaml",
            "cnaps": "cnaps.yaml",
            "BOJNET": "bojnet.yaml",
            "bojnet": "bojnet.yaml",
            "KFTC": "kftc.yaml",
            "kftc": "kftc.yaml",
            "INSTAPAY": "instapay.yaml",
            "instapay": "instapay.yaml",
            # Middle East
            "UAEFTS": "uaefts.yaml",
            "uaefts": "uaefts.yaml",
            "SARIE": "sarie.yaml",
            "sarie": "sarie.yaml",
            # Latin America & Other
            "PIX": "pix.yaml",
            "pix": "pix.yaml",
            "UPI": "upi.yaml",
            "upi": "upi.yaml",
            "PROMPTPAY": "promptpay.yaml",
            "promptpay": "promptpay.yaml",
            "PAYNOW": "paynow.yaml",
            "paynow": "paynow.yaml",
        }

        filename = file_map.get(message_type)
        if not filename:
            # Try to find a matching file dynamically
            normalized = message_type.lower().replace(".", "")
            candidate = f"{normalized}.yaml"
            if (self.mappings_dir / candidate).exists():
                filename = candidate
            else:
                return None

        mapping_file = self.mappings_dir / filename
        if not mapping_file.exists():
            return None

        with open(mapping_file, 'r') as f:
            config = yaml.safe_load(f)

        # Support both 'mapping' (singular) and 'mappings' (plural) root keys
        mapping_root = config.get('mapping', config.get('mappings', {}))

        # Parse bronze_to_silver
        b2s_config = mapping_root.get('bronze_to_silver', {})
        b2s = self._parse_layer_mapping(
            b2s_config,
            source_layer="bronze",
            target_layer="silver",
            message_type=message_type
        )

        # Parse silver_to_gold
        s2g_config = mapping_root.get('silver_to_gold', {})
        s2g = self._parse_layer_mapping(
            s2g_config,
            source_layer="silver",
            target_layer="gold",
            message_type=message_type
        )

        # Parse entity mappings
        entity_mappings = {}
        for entity_type in ['party_mappings', 'account_mappings', 'fi_mappings']:
            entity_config = s2g_config.get(entity_type, [])
            entity_fields = []
            for mapping in entity_config:
                role = mapping.get('role', '')
                fields = mapping.get('fields', [])
                for f in fields:
                    entity_fields.append(FieldLineage(
                        source_layer="silver",
                        source_table=s2g.source_table if s2g else "stg_pain001",
                        source_field=f.get('source', ''),
                        source_path=None,
                        target_layer="gold",
                        target_table=mapping.get('target_table', ''),
                        target_field=f.get('target', ''),
                        transformation_type=None,
                        transformation_logic=None,
                        data_type=f.get('type', 'string'),
                        message_type=message_type,
                    ))
            if entity_fields:
                entity_mappings[entity_type.replace('_mappings', '')] = entity_fields

        return FullLineage(
            message_type=message_type,
            bronze_to_silver=b2s,
            silver_to_gold=s2g,
            entity_mappings=entity_mappings,
        )

    def _parse_layer_mapping(
        self,
        config: Dict,
        source_layer: str,
        target_layer: str,
        message_type: str,
    ) -> Optional[LayerLineage]:
        """Parse a layer mapping configuration."""
        source_config = config.get('source', {})
        target_config = config.get('target', {})
        fields_config = config.get('fields', [])

        source_table = source_config.get('table', '')
        target_table = target_config.get('table', '')

        field_mappings = []
        for f in fields_config:
            transform = f.get('transform', {})
            field_mappings.append(FieldLineage(
                source_layer=source_layer,
                source_table=source_table,
                source_field=f.get('source', ''),
                source_path=f.get('source', ''),  # XPath for bronze
                target_layer=target_layer,
                target_table=target_table,
                target_field=f.get('target', ''),
                transformation_type=transform.get('type') if transform else None,
                transformation_logic=str(transform) if transform else None,
                data_type=f.get('type', 'string'),
                message_type=message_type,
            ))

        return LayerLineage(
            source_layer=source_layer,
            source_table=source_table,
            target_layer=target_layer,
            target_table=target_table,
            field_mappings=field_mappings,
            message_type=message_type,
        )

    def get_field_lineage(
        self,
        message_type: str,
        field_name: Optional[str] = None,
        layer: Optional[str] = None,
        data_type: Optional[str] = None,
    ) -> List[FieldLineage]:
        """
        Get field-level lineage with optional filtering.

        Args:
            message_type: Message type
            field_name: Filter by field name (partial match)
            layer: Filter by layer (bronze, silver, gold)
            data_type: Filter by data type

        Returns:
            List of FieldLineage entries
        """
        full_lineage = self.get_message_type_lineage(message_type)
        if not full_lineage:
            return []

        # Collect all field mappings
        all_fields = []

        if full_lineage.bronze_to_silver:
            all_fields.extend(full_lineage.bronze_to_silver.field_mappings)

        if full_lineage.silver_to_gold:
            all_fields.extend(full_lineage.silver_to_gold.field_mappings)

        for entity_fields in full_lineage.entity_mappings.values():
            all_fields.extend(entity_fields)

        # Apply filters
        if field_name:
            field_lower = field_name.lower()
            all_fields = [
                f for f in all_fields
                if field_lower in f.source_field.lower() or field_lower in f.target_field.lower()
            ]

        if layer:
            all_fields = [
                f for f in all_fields
                if f.source_layer == layer or f.target_layer == layer
            ]

        if data_type:
            all_fields = [
                f for f in all_fields
                if f.data_type == data_type
            ]

        return all_fields

    def get_backward_lineage_from_cdm(
        self,
        entity_table: str,
        field_name: Optional[str] = None,
    ) -> EntityLineage:
        """
        Get backward lineage from a CDM entity to source message types.

        Args:
            entity_table: CDM table (cdm_party, cdm_account, etc.)
            field_name: Specific field (None for all fields)

        Returns:
            EntityLineage with all source mappings
        """
        source_mappings = []
        message_types = set()

        # Search all supported message types (NOTE: All SWIFT MT decommissioned Nov 2025)
        all_msg_types = [
            'pain.001', 'pain.002', 'pacs.008', 'pacs.009', 'pacs.002', 'camt.053',
            'FEDWIRE', 'ACH', 'CHIPS', 'RTP', 'FEDNOW',
            'SEPA', 'TARGET2',
            'CHAPS', 'FPS', 'BACS',
            'NPP', 'MEPS_PLUS', 'RTGS_HK', 'CNAPS', 'BOJNET', 'KFTC', 'INSTAPAY',
            'UAEFTS', 'SARIE',
            'PIX', 'UPI', 'PROMPTPAY', 'PAYNOW',
        ]
        for msg_type in all_msg_types:
            lineage = self.get_message_type_lineage(msg_type)
            if not lineage:
                continue

            # Check entity mappings
            for entity_type, fields in lineage.entity_mappings.items():
                for f in fields:
                    if f.target_table == entity_table:
                        if field_name is None or f.target_field == field_name:
                            source_mappings.append(f)
                            message_types.add(msg_type)

            # Check main gold mapping
            if lineage.silver_to_gold:
                for f in lineage.silver_to_gold.field_mappings:
                    if f.target_table == entity_table or 'payment_instruction' in entity_table:
                        if field_name is None or f.target_field == field_name:
                            source_mappings.append(f)
                            message_types.add(msg_type)

        return EntityLineage(
            entity_table=entity_table,
            entity_field=field_name or "*",
            source_mappings=source_mappings,
            message_types=list(message_types),
        )

    def get_backward_lineage_from_report(
        self,
        report_type: str,
        field_name: Optional[str] = None,
    ) -> Dict:
        """
        Get backward lineage from a regulatory report to source.

        Args:
            report_type: Report type (e.g., "FATCA_8966", "FINCEN_CTR")
            field_name: Specific field (None for all fields)

        Returns:
            Dictionary with report field lineage
        """
        # Report field to CDM entity mappings
        report_mappings = {
            "FATCA_8966": {
                "AccountNumber": ("cdm_account", "account_number"),
                "AccountBalance": ("cdm_account", "balance"),
                "AccountHolderName": ("cdm_party", "name"),
                "TIN": ("cdm_party", "tax_id"),
                "ReportingFI_GIIN": ("cdm_financial_institution", "fatca_giin"),
            },
            "FINCEN_CTR": {
                "TransactionAmount": ("cdm_payment_instruction", "instructed_amount"),
                "TransactionDate": ("cdm_payment_instruction", "execution_date"),
                "SenderName": ("cdm_party", "name"),
                "ReceiverName": ("cdm_party", "name"),
                "BankRoutingNumber": ("cdm_financial_institution", "national_clearing_code"),
            },
        }

        if report_type not in report_mappings:
            return {"error": f"Unknown report type: {report_type}"}

        mappings = report_mappings[report_type]
        result = {
            "report_type": report_type,
            "field_lineage": [],
        }

        for report_field, (cdm_table, cdm_field) in mappings.items():
            if field_name and report_field != field_name:
                continue

            # Get lineage from CDM to source
            entity_lineage = self.get_backward_lineage_from_cdm(cdm_table, cdm_field)

            result["field_lineage"].append({
                "report_field": report_field,
                "cdm_table": cdm_table,
                "cdm_field": cdm_field,
                "source_mappings": [
                    {
                        "message_type": m.message_type,
                        "source_layer": m.source_layer,
                        "source_field": m.source_field,
                        "source_path": m.source_path,
                    }
                    for m in entity_lineage.source_mappings
                ],
                "message_types": entity_lineage.message_types,
            })

        return result

    def get_lineage_graph(self, message_type: str) -> Dict:
        """
        Get lineage as a graph structure for visualization.

        Returns nodes and edges for rendering in a UI.
        Fetches entity structure from Neo4j for complete multi-entity gold layer.
        """
        # Try to get entity structure from Neo4j first
        try:
            from gps_cdm.orchestration.neo4j_service import get_neo4j_service
            neo4j = get_neo4j_service()
            if neo4j.is_available():
                schema_lineage = neo4j.get_schema_lineage(message_type)
                if schema_lineage:
                    return self._build_graph_from_neo4j(schema_lineage, message_type)
        except Exception as e:
            logger.warning(f"Failed to get schema from Neo4j: {e}")

        # Fallback to YAML-based lineage
        lineage = self.get_message_type_lineage(message_type)
        if not lineage:
            return {"nodes": [], "edges": []}

        nodes = []
        edges = []
        node_id = 0

        # Add layer nodes
        layers = ["bronze", "silver", "gold"]
        layer_nodes = {}
        for layer in layers:
            layer_nodes[layer] = node_id
            nodes.append({
                "id": node_id,
                "type": "layer",
                "name": layer.upper(),
                "layer": layer,
            })
            node_id += 1

        # Add table nodes
        tables = set()
        if lineage.bronze_to_silver:
            tables.add(("bronze", lineage.bronze_to_silver.source_table))
            tables.add(("silver", lineage.bronze_to_silver.target_table))
        if lineage.silver_to_gold:
            tables.add(("silver", lineage.silver_to_gold.source_table))
            tables.add(("gold", lineage.silver_to_gold.target_table))

        table_nodes = {}
        for layer, table in tables:
            key = f"{layer}.{table}"
            table_nodes[key] = node_id
            nodes.append({
                "id": node_id,
                "type": "table",
                "name": table,
                "layer": layer,
            })
            node_id += 1

        # Add field edges
        for f in self.get_field_lineage(message_type):
            source_key = f"{f.source_layer}.{f.source_table}"
            target_key = f"{f.target_layer}.{f.target_table}"

            if source_key in table_nodes and target_key in table_nodes:
                edges.append({
                    "source": table_nodes[source_key],
                    "target": table_nodes[target_key],
                    "source_field": f.source_field,
                    "target_field": f.target_field,
                    "transformation": f.transformation_type,
                })

        return {"nodes": nodes, "edges": edges}

    def _build_graph_from_neo4j(self, schema_lineage: Dict, message_type: str) -> Dict:
        """Build graph structure from Neo4j schema lineage."""
        nodes = []
        edges = []
        node_id = 0

        # Add layer nodes
        layers = ["bronze", "silver", "gold"]
        layer_nodes = {}
        for layer in layers:
            layer_nodes[layer] = node_id
            nodes.append({
                "id": node_id,
                "type": "layer",
                "name": layer.upper(),
                "layer": layer,
            })
            node_id += 1

        # Add entity/table nodes from Neo4j
        table_nodes = {}
        for entity_data in schema_lineage.get("entities", []):
            entity = entity_data.get("entity", {})
            entity_id = entity.get("entity_id", "")
            layer = entity.get("layer", "")
            entity_type = entity.get("entity_type", "")

            if entity_id and layer:
                # Use entity_id as key (e.g., "bronze.raw_payment_messages")
                table_name = entity_type or entity_id.split(".")[-1]
                table_nodes[entity_id] = node_id
                nodes.append({
                    "id": node_id,
                    "type": "table",
                    "name": table_name,
                    "layer": layer,
                })
                node_id += 1

        # Add transformation edges from Neo4j
        for transform in schema_lineage.get("transforms", []):
            source = transform.get("source", {})
            target = transform.get("target", {})
            transform_info = transform.get("transform", {})

            source_id = source.get("entity_id", "")
            target_id = target.get("entity_id", "")

            if source_id in table_nodes and target_id in table_nodes:
                edges.append({
                    "source": table_nodes[source_id],
                    "target": table_nodes[target_id],
                    "source_field": "",
                    "target_field": "",
                    "transformation": transform_info.get("transformation_type", ""),
                })

        # Add field-level edges from YAML mappings
        for f in self.get_field_lineage(message_type):
            source_key = f"{f.source_layer}.{f.source_table}"
            target_key = f"{f.target_layer}.{f.target_table}"

            if source_key in table_nodes and target_key in table_nodes:
                edges.append({
                    "source": table_nodes[source_key],
                    "target": table_nodes[target_key],
                    "source_field": f.source_field,
                    "target_field": f.target_field,
                    "transformation": f.transformation_type,
                })

        return {"nodes": nodes, "edges": edges}

    def persist_lineage(self, message_type: str) -> int:
        """
        Persist lineage to database for querying.

        Returns number of records inserted.
        """
        if not self.db:
            return 0

        lineage = self.get_message_type_lineage(message_type)
        if not lineage:
            return 0

        cursor = self.db.cursor()
        count = 0

        try:
            # Clear existing lineage for this message type
            cursor.execute("""
                DELETE FROM observability.obs_field_lineage
                WHERE mapping_id LIKE %s
            """, (f"%{message_type}%",))

            # Insert new lineage
            for f in self.get_field_lineage(message_type):
                cursor.execute("""
                    INSERT INTO observability.obs_field_lineage (
                        lineage_id, mapping_id,
                        source_layer, source_table, source_field, source_field_path,
                        target_layer, target_table, target_field,
                        transformation_type, transformation_logic,
                        effective_from, is_current, created_at
                    ) VALUES (
                        uuid_generate_v4()::text, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s,
                        CURRENT_DATE, true, CURRENT_TIMESTAMP
                    )
                """, (
                    f"{message_type}:{f.source_field}:{f.target_field}",
                    f.source_layer, f.source_table, f.source_field, f.source_path,
                    f.target_layer, f.target_table, f.target_field,
                    f.transformation_type, f.transformation_logic,
                ))
                count += 1

            self.db.commit()
            return count
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def query_lineage_from_db(
        self,
        source_field: Optional[str] = None,
        target_field: Optional[str] = None,
        layer: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Query lineage from database."""
        if not self.db:
            return []

        conditions = ["is_current = true"]
        params = []

        if source_field:
            conditions.append("source_field ILIKE %s")
            params.append(f"%{source_field}%")
        if target_field:
            conditions.append("target_field ILIKE %s")
            params.append(f"%{target_field}%")
        if layer:
            conditions.append("(source_layer = %s OR target_layer = %s)")
            params.extend([layer, layer])

        sql = f"""
            SELECT source_layer, source_table, source_field, source_field_path,
                   target_layer, target_table, target_field,
                   transformation_type, transformation_logic, mapping_id
            FROM observability.obs_field_lineage
            WHERE {' AND '.join(conditions)}
            ORDER BY source_layer, source_table, source_field
            LIMIT %s
        """
        params.append(limit)

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()
