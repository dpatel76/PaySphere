#!/usr/bin/env python3
"""
GPS CDM - Databricks Connection Setup Script
=============================================

This script helps you configure and test your Databricks Free Edition connection.

Prerequisites:
1. Databricks Free Edition account
2. Personal Access Token (PAT) - generate at: Settings > Developer > Access Tokens
3. SQL Warehouse HTTP Path - find at: SQL Warehouses > Your Warehouse > Connection details

Usage:
    python scripts/setup_databricks_connection.py

The script will:
1. Guide you through entering credentials
2. Test the Databricks connection
3. Test the Neo4j integration
4. Save configuration to .env file
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def get_credentials():
    """Get Databricks credentials from user or environment."""
    print("\n" + "=" * 60)
    print("GPS CDM - Databricks Free Edition Setup")
    print("=" * 60)

    # Server hostname
    server_hostname = os.environ.get("DATABRICKS_SERVER_HOSTNAME")
    if not server_hostname:
        print("\nYour Databricks workspace URL is:")
        print("https://dbc-96614790-02e2.cloud.databricks.com")
        server_hostname = "dbc-96614790-02e2.cloud.databricks.com"
        print(f"\nUsing server hostname: {server_hostname}")

    # HTTP Path
    http_path = os.environ.get("DATABRICKS_HTTP_PATH")
    if not http_path:
        print("\n" + "-" * 60)
        print("To find your SQL Warehouse HTTP Path:")
        print("1. Go to: SQL Warehouses in left sidebar")
        print("2. Click on your warehouse (e.g., 'Starter Warehouse')")
        print("3. Click 'Connection details' tab")
        print("4. Copy the 'HTTP Path' value")
        print("-" * 60)
        http_path = input("\nEnter HTTP Path (e.g., /sql/1.0/warehouses/abc123): ").strip()

    # Access Token
    access_token = os.environ.get("DATABRICKS_TOKEN")
    if not access_token:
        print("\n" + "-" * 60)
        print("To generate a Personal Access Token:")
        print("1. Click your profile icon (top right)")
        print("2. Go to: Settings > Developer > Access Tokens")
        print("3. Click 'Generate new token'")
        print("4. Give it a name like 'GPS CDM Local'")
        print("5. Copy the token (you won't see it again!)")
        print("-" * 60)
        access_token = input("\nEnter Personal Access Token: ").strip()

    return {
        "server_hostname": server_hostname,
        "http_path": http_path,
        "access_token": access_token,
        "catalog": os.environ.get("DATABRICKS_CATALOG", "workspace"),
        "schema": os.environ.get("DATABRICKS_SCHEMA", "cdm_dev"),
    }


def test_databricks_connection(config):
    """Test connection to Databricks."""
    print("\n" + "=" * 60)
    print("Testing Databricks Connection...")
    print("=" * 60)

    try:
        from databricks import sql

        print(f"Connecting to: {config['server_hostname']}")
        print(f"HTTP Path: {config['http_path']}")
        print(f"Catalog: {config['catalog']}")
        print(f"Schema: {config['schema']}")

        connection = sql.connect(
            server_hostname=config["server_hostname"],
            http_path=config["http_path"],
            access_token=config["access_token"],
        )

        with connection.cursor() as cursor:
            # Test basic connectivity
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"\n✓ Basic connectivity: OK")

            # Check catalog
            cursor.execute("SELECT current_catalog()")
            catalog = cursor.fetchone()[0]
            print(f"✓ Current catalog: {catalog}")

            # List tables
            full_schema = f"{config['catalog']}.{config['schema']}"
            cursor.execute(f"SHOW TABLES IN {full_schema}")
            tables = cursor.fetchall()
            print(f"✓ Tables in {full_schema}: {len(tables)}")
            for t in tables:
                print(f"    - {t[1]}")

            # Check for data
            cursor.execute(
                f"SELECT COUNT(*) FROM {full_schema}.obs_batch_tracking"
            )
            batch_count = cursor.fetchone()[0]
            print(f"✓ Batches in tracking table: {batch_count}")

        connection.close()
        print("\n✓ Databricks connection successful!")
        return True

    except ImportError:
        print("\n✗ databricks-sql-connector not installed")
        print("  Run: pip install databricks-sql-connector")
        return False
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        return False


def test_neo4j_integration(config):
    """Test Neo4j integration with Databricks data."""
    print("\n" + "=" * 60)
    print("Testing Neo4j Integration...")
    print("=" * 60)

    try:
        from gps_cdm.orchestration.neo4j_service import get_neo4j_service
        from gps_cdm.ingestion.persistence.databricks_connector import DatabricksConnector

        # Check Neo4j
        neo4j = get_neo4j_service()
        if not neo4j.is_available():
            print("✗ Neo4j not available")
            print("  Run: docker-compose -f docker-compose.nifi.yaml up neo4j -d")
            return False
        print("✓ Neo4j connection: OK")

        # Get Databricks connector
        connector = DatabricksConnector(
            server_hostname=config["server_hostname"],
            http_path=config["http_path"],
            access_token=config["access_token"],
            catalog=config["catalog"],
            schema=config["schema"],
        )

        if not connector.is_available():
            print("✗ Databricks connector not available")
            return False
        print("✓ Databricks connector: OK")

        # Get a batch to sync
        batches = connector.get_batches(limit=1, status="COMPLETED")
        if not batches:
            batches = connector.get_batches(limit=1)

        if not batches:
            print("✗ No batches found in Databricks")
            return False

        batch_id = batches[0]["batch_id"]
        print(f"✓ Found batch: {batch_id}")

        # Sync to Neo4j
        print(f"  Syncing batch to Neo4j...")
        result = connector.sync_batch_to_neo4j(batch_id)
        if result:
            print(f"✓ Batch synced to Neo4j: {batch_id}")

            # Verify in Neo4j
            lineage = neo4j.get_batch_lineage(batch_id)
            if lineage and lineage.get("batch"):
                print(f"✓ Lineage verified in Neo4j")
                print(f"    Batch ID: {lineage['batch']['batch_id']}")
                print(f"    Status: {lineage['batch'].get('status', 'N/A')}")
            else:
                print("✗ Could not verify lineage in Neo4j")
                return False
        else:
            print("✗ Failed to sync batch to Neo4j")
            return False

        connector.close()
        print("\n✓ Neo4j integration successful!")
        return True

    except Exception as e:
        print(f"\n✗ Neo4j integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def save_env_file(config):
    """Save configuration to .env file."""
    env_path = project_root / ".env.databricks"

    content = f"""# Databricks Free Edition Configuration
# Generated by setup_databricks_connection.py

DATABRICKS_SERVER_HOSTNAME={config['server_hostname']}
DATABRICKS_HTTP_PATH={config['http_path']}
DATABRICKS_TOKEN={config['access_token']}
DATABRICKS_CATALOG={config['catalog']}
DATABRICKS_SCHEMA={config['schema']}
"""

    with open(env_path, "w") as f:
        f.write(content)

    print(f"\n✓ Configuration saved to: {env_path}")
    print("\nTo load these variables, run:")
    print(f"  source {env_path}")
    print("  # or add to your shell profile")


def main():
    """Main setup flow."""
    # Get credentials
    config = get_credentials()

    if not config["http_path"] or not config["access_token"]:
        print("\n✗ Missing required credentials")
        print("  Please provide HTTP Path and Access Token")
        sys.exit(1)

    # Test Databricks
    databricks_ok = test_databricks_connection(config)

    if databricks_ok:
        # Test Neo4j integration
        neo4j_ok = test_neo4j_integration(config)

        # Save config
        save_env_file(config)

        print("\n" + "=" * 60)
        print("SETUP COMPLETE!")
        print("=" * 60)

        if databricks_ok and neo4j_ok:
            print("\n✓ All integrations working!")
            print("\nNext steps:")
            print("  1. Run end-to-end test:")
            print("     pytest tests/integration/test_databricks_neo4j_e2e.py -v")
            print("\n  2. View lineage in Neo4j Browser:")
            print("     http://localhost:7474")
            print("     Query: MATCH (b:Batch) RETURN b LIMIT 10")
        else:
            print("\n⚠ Some integrations need attention")
            sys.exit(1)
    else:
        print("\n✗ Setup failed - fix Databricks connection first")
        sys.exit(1)


if __name__ == "__main__":
    main()
