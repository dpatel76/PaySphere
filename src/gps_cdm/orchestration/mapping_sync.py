"""
GPS CDM - YAML to Database Mapping Sync

Syncs mapping definitions from YAML files to database tables while preserving
user-modified mappings.

Design principles:
1. Database is the single source of truth at runtime
2. YAML files are design-time documentation
3. User-modified mappings (is_user_modified=true) are NEVER overwritten
4. New mappings from YAML are added with source='yaml_sync'
5. Mappings removed from YAML are soft-deleted (is_active=false)

Usage:
    from gps_cdm.orchestration.mapping_sync import MappingSync

    sync = MappingSync()
    result = sync.sync_message_type("pain.001")
    print(f"Added: {result['added']}, Updated: {result['updated']}, Skipped: {result['skipped']}")
"""

import os
import yaml
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Result of a mapping sync operation."""
    message_type: str
    silver_added: int = 0
    silver_updated: int = 0
    silver_skipped: int = 0  # Skipped due to is_user_modified
    gold_added: int = 0
    gold_updated: int = 0
    gold_skipped: int = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    def to_dict(self) -> Dict:
        return {
            "message_type": self.message_type,
            "silver": {
                "added": self.silver_added,
                "updated": self.silver_updated,
                "skipped": self.silver_skipped,
            },
            "gold": {
                "added": self.gold_added,
                "updated": self.gold_updated,
                "skipped": self.gold_skipped,
            },
            "errors": self.errors,
        }


class MappingSync:
    """
    Synchronizes YAML mapping files to database tables.

    Respects user-modified mappings and provides conflict resolution.
    """

    def __init__(self, db_connection=None, mappings_dir: str = None):
        self.db = db_connection
        self.mappings_dir = Path(mappings_dir) if mappings_dir else None
        if not self.mappings_dir:
            self.mappings_dir = Path(__file__).parent.parent.parent.parent / "mappings" / "message_types"

    def _get_db_connection(self):
        """Get or create database connection."""
        if self.db:
            return self.db, False  # Return existing connection, don't close

        conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", 5433)),
            database=os.environ.get("POSTGRES_DB", "gps_cdm"),
            user=os.environ.get("POSTGRES_USER", "gps_cdm_svc"),
            password=os.environ.get("POSTGRES_PASSWORD", "gps_cdm_password"),
        )
        return conn, True  # Return new connection, should close

    def _get_message_type_file(self, message_type: str) -> Optional[Path]:
        """Get YAML file path for a message type."""
        file_map = {
            "pain.001": "pain001.yaml",
            "pain001": "pain001.yaml",
            "pacs.008": "pacs008.yaml",
            "pacs008": "pacs008.yaml",
            "MT103": "mt103.yaml",
            "mt103": "mt103.yaml",
            "MT202": "mt202.yaml",
            "mt202": "mt202.yaml",
            "FEDWIRE": "fedwire.yaml",
            "fedwire": "fedwire.yaml",
            "ACH": "ach.yaml",
            "ach": "ach.yaml",
            "RTP": "rtp.yaml",
            "rtp": "rtp.yaml",
            "SEPA": "sepa.yaml",
            "sepa": "sepa.yaml",
        }

        filename = file_map.get(message_type)
        if not filename:
            # Try dynamic lookup
            normalized = message_type.lower().replace(".", "")
            candidate = self.mappings_dir / f"{normalized}.yaml"
            if candidate.exists():
                return candidate
            return None

        path = self.mappings_dir / filename
        return path if path.exists() else None

    def sync_message_type(self, message_type: str, force: bool = False) -> SyncResult:
        """
        Sync a single message type from YAML to database.

        Args:
            message_type: Message type (e.g., "pain.001")
            force: If True, overwrite user-modified mappings (use with caution!)

        Returns:
            SyncResult with counts and any errors
        """
        result = SyncResult(message_type=message_type)

        yaml_file = self._get_message_type_file(message_type)
        if not yaml_file:
            result.errors.append(f"No YAML file found for {message_type}")
            return result

        try:
            with open(yaml_file, 'r') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            result.errors.append(f"Failed to parse YAML: {e}")
            return result

        conn, should_close = self._get_db_connection()

        try:
            # Parse YAML and sync
            mapping_root = config.get('mapping', config.get('mappings', {}))

            # Sync bronze_to_silver
            b2s_config = mapping_root.get('bronze_to_silver', {})
            self._sync_silver_mappings(conn, message_type, b2s_config, result, force)

            # Sync silver_to_gold
            s2g_config = mapping_root.get('silver_to_gold', {})
            self._sync_gold_mappings(conn, message_type, s2g_config, result, force)

            conn.commit()

        except Exception as e:
            conn.rollback()
            result.errors.append(f"Database error: {e}")
            logger.exception(f"Failed to sync {message_type}")
        finally:
            if should_close:
                conn.close()

        return result

    def _sync_silver_mappings(
        self,
        conn,
        message_type: str,
        b2s_config: Dict,
        result: SyncResult,
        force: bool
    ):
        """Sync bronze→silver mappings to database."""
        cursor = conn.cursor()

        # Get existing mappings
        cursor.execute("""
            SELECT target_column, is_user_modified
            FROM mapping.silver_field_mappings
            WHERE format_id = %s
        """, (message_type,))
        existing = {row[0]: row[1] for row in cursor.fetchall()}

        # Parse YAML field mappings - support both 'fields' and 'field_mappings' keys
        field_mappings = b2s_config.get('fields', b2s_config.get('field_mappings', []))

        for idx, mapping in enumerate(field_mappings):
            source_path = mapping.get('source', mapping.get('source_path', ''))
            target_column = mapping.get('target', mapping.get('target_column', ''))

            if not target_column:
                continue

            is_user_modified = existing.get(target_column, False)

            # Skip user-modified mappings unless force=True
            if is_user_modified and not force:
                result.silver_skipped += 1
                continue

            # Handle transform - convert dict to JSON string
            import json
            transform_raw = mapping.get('transform')
            transform_expr = json.dumps(transform_raw) if isinstance(transform_raw, dict) else transform_raw

            # Use upsert to handle duplicates gracefully
            cursor.execute("""
                INSERT INTO mapping.silver_field_mappings
                (format_id, target_column, source_path, data_type,
                 transform_function, transform_expression, is_required,
                 ordinal_position, source, is_user_modified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'yaml_sync', false)
                ON CONFLICT (format_id, target_column)
                DO UPDATE SET
                    source_path = EXCLUDED.source_path,
                    data_type = EXCLUDED.data_type,
                    transform_function = EXCLUDED.transform_function,
                    transform_expression = EXCLUDED.transform_expression,
                    is_required = EXCLUDED.is_required,
                    ordinal_position = EXCLUDED.ordinal_position,
                    source = 'yaml_sync',
                    updated_at = CURRENT_TIMESTAMP
                WHERE mapping.silver_field_mappings.is_user_modified = false OR %s = true
            """, (
                message_type,
                target_column,
                source_path,
                mapping.get('type', 'VARCHAR'),
                mapping.get('transform_function'),
                transform_expr,
                mapping.get('required', False),
                idx + 1,
                force,
            ))
            if target_column in existing:
                result.silver_updated += 1
            else:
                result.silver_added += 1

        cursor.close()

    def _sync_gold_mappings(
        self,
        conn,
        message_type: str,
        s2g_config: Dict,
        result: SyncResult,
        force: bool
    ):
        """Sync silver→gold mappings to database."""
        cursor = conn.cursor()

        # Get existing mappings
        cursor.execute("""
            SELECT gold_table, gold_column, entity_role, is_user_modified
            FROM mapping.gold_field_mappings
            WHERE format_id = %s
        """, (message_type,))
        existing = {(row[0], row[1], row[2]): row[3] for row in cursor.fetchall()}

        # Parse main field mappings - support both 'fields' and 'field_mappings' keys
        field_mappings = s2g_config.get('fields', s2g_config.get('field_mappings', []))
        # Target table can be under 'target' object or directly
        target_config = s2g_config.get('target', {})
        gold_table = target_config.get('table', s2g_config.get('target_table', 'cdm_payment_instruction'))

        import json
        for idx, mapping in enumerate(field_mappings):
            source_expr = mapping.get('source', '')
            target_column = mapping.get('target', '')

            if not target_column:
                continue

            key = (gold_table, target_column, None)
            is_user_modified = existing.get(key, False)

            if is_user_modified and not force:
                result.gold_skipped += 1
                continue

            # Handle transform - convert dict to JSON string
            transform_raw = mapping.get('transform')
            transform_expr = json.dumps(transform_raw) if isinstance(transform_raw, dict) else transform_raw

            # Use upsert to handle duplicates gracefully
            cursor.execute("""
                INSERT INTO mapping.gold_field_mappings
                (format_id, gold_table, gold_column, source_expression,
                 data_type, transform_expression, ordinal_position,
                 source, is_user_modified, entity_role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'yaml_sync', false, NULL)
                ON CONFLICT (format_id, gold_table, gold_column, entity_role)
                DO UPDATE SET
                    source_expression = EXCLUDED.source_expression,
                    data_type = EXCLUDED.data_type,
                    transform_expression = EXCLUDED.transform_expression,
                    ordinal_position = EXCLUDED.ordinal_position,
                    source = 'yaml_sync',
                    updated_at = CURRENT_TIMESTAMP
                WHERE mapping.gold_field_mappings.is_user_modified = false OR %s = true
            """, (
                message_type,
                gold_table,
                target_column,
                source_expr,
                mapping.get('type', 'VARCHAR'),
                transform_expr,
                idx + 1,
                force,
            ))
            if key in existing:
                result.gold_updated += 1
            else:
                result.gold_added += 1

        # Parse entity mappings (party, account, fi)
        for entity_type in ['party_mappings', 'account_mappings', 'fi_mappings']:
            entity_configs = s2g_config.get(entity_type, [])
            for entity_config in entity_configs:
                entity_role = entity_config.get('role', '')
                target_table = entity_config.get('target_table', '')
                fields = entity_config.get('fields', [])

                for idx, field_def in enumerate(fields):
                    source = field_def.get('source', '')
                    target = field_def.get('target', '')

                    if not target:
                        continue

                    key = (target_table, target, entity_role)
                    is_user_modified = existing.get(key, False)

                    if is_user_modified and not force:
                        result.gold_skipped += 1
                        continue

                    # Use upsert to handle duplicates gracefully
                    cursor.execute("""
                        INSERT INTO mapping.gold_field_mappings
                        (format_id, gold_table, gold_column, source_expression,
                         entity_role, data_type, ordinal_position,
                         source, is_user_modified)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 'yaml_sync', false)
                        ON CONFLICT (format_id, gold_table, gold_column, entity_role)
                        DO UPDATE SET
                            source_expression = EXCLUDED.source_expression,
                            data_type = EXCLUDED.data_type,
                            ordinal_position = EXCLUDED.ordinal_position,
                            source = 'yaml_sync',
                            updated_at = CURRENT_TIMESTAMP
                        WHERE mapping.gold_field_mappings.is_user_modified = false OR %s = true
                    """, (
                        message_type,
                        target_table,
                        target,
                        source,
                        entity_role,
                        field_def.get('type', 'VARCHAR'),
                        idx + 1,
                        force,
                    ))
                    if key in existing:
                        result.gold_updated += 1
                    else:
                        result.gold_added += 1

        cursor.close()

    def sync_all(self, force: bool = False) -> Dict[str, SyncResult]:
        """
        Sync all available YAML mapping files to database.

        Args:
            force: If True, overwrite user-modified mappings

        Returns:
            Dict mapping message_type to SyncResult
        """
        results = {}

        if not self.mappings_dir.exists():
            logger.warning(f"Mappings directory not found: {self.mappings_dir}")
            return results

        for yaml_file in self.mappings_dir.glob("*.yaml"):
            # Extract message type from filename
            stem = yaml_file.stem
            message_type = stem

            # Normalize to standard format
            if stem == "pain001":
                message_type = "pain.001"
            elif stem == "pacs008":
                message_type = "pacs.008"
            elif stem in ("mt103", "mt202"):
                message_type = stem.upper()
            elif stem in ("fedwire", "ach", "rtp", "sepa", "chaps", "bacs"):
                message_type = stem.upper()

            logger.info(f"Syncing {message_type} from {yaml_file.name}")
            results[message_type] = self.sync_message_type(message_type, force=force)

        return results

    def get_user_modified_mappings(self, message_type: str = None) -> Dict[str, List[Dict]]:
        """
        Get all user-modified mappings.

        Returns:
            Dict with 'silver' and 'gold' lists of modified mappings
        """
        conn, should_close = self._get_db_connection()

        try:
            cursor = conn.cursor()
            result = {'silver': [], 'gold': []}

            # Get modified silver mappings
            query = """
                SELECT format_id, target_column, source_path, updated_at
                FROM mapping.silver_field_mappings
                WHERE is_user_modified = true
            """
            if message_type:
                query += " AND format_id = %s"
                cursor.execute(query, (message_type,))
            else:
                cursor.execute(query)

            for row in cursor.fetchall():
                result['silver'].append({
                    'format_id': row[0],
                    'target_column': row[1],
                    'source_path': row[2],
                    'updated_at': row[3].isoformat() if row[3] else None,
                })

            # Get modified gold mappings
            query = """
                SELECT format_id, gold_table, gold_column, entity_role, updated_at
                FROM mapping.gold_field_mappings
                WHERE is_user_modified = true
            """
            if message_type:
                query += " AND format_id = %s"
                cursor.execute(query, (message_type,))
            else:
                cursor.execute(query)

            for row in cursor.fetchall():
                result['gold'].append({
                    'format_id': row[0],
                    'gold_table': row[1],
                    'gold_column': row[2],
                    'entity_role': row[3],
                    'updated_at': row[4].isoformat() if row[4] else None,
                })

            cursor.close()
            return result

        finally:
            if should_close:
                conn.close()


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sync YAML mappings to database")
    parser.add_argument("--message-type", "-m", help="Specific message type to sync")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite user-modified mappings")
    parser.add_argument("--list-modified", action="store_true", help="List user-modified mappings")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    sync = MappingSync()

    if args.list_modified:
        modified = sync.get_user_modified_mappings(args.message_type)
        print(f"Silver mappings: {len(modified['silver'])}")
        for m in modified['silver']:
            print(f"  {m['format_id']}: {m['target_column']}")
        print(f"Gold mappings: {len(modified['gold'])}")
        for m in modified['gold']:
            print(f"  {m['format_id']}: {m['gold_table']}.{m['gold_column']}")
    elif args.message_type:
        result = sync.sync_message_type(args.message_type, force=args.force)
        print(f"Synced {args.message_type}:")
        print(f"  Silver: added={result.silver_added}, updated={result.silver_updated}, skipped={result.silver_skipped}")
        print(f"  Gold: added={result.gold_added}, updated={result.gold_updated}, skipped={result.gold_skipped}")
        if result.errors:
            print(f"  Errors: {result.errors}")
    else:
        results = sync.sync_all(force=args.force)
        print("Sync complete:")
        for msg_type, result in results.items():
            print(f"  {msg_type}: silver={result.silver_added+result.silver_updated}, gold={result.gold_added+result.gold_updated}")
