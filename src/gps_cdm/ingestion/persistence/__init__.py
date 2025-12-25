"""
GPS CDM - Database-Agnostic Persistence Layer
==============================================

Provides a unified interface for persisting CDM data across different
storage backends:

- PostgreSQL: Local development and testing
- Delta Lake: Databricks production
- Starburst: Query federation
- Neo4j: Graph relationships (optional)

The persistence layer abstracts storage operations so the same ingestion
code works against any configured backend.

Usage:
    # Configuration-driven backend selection
    from gps_cdm.ingestion.persistence import PersistenceFactory

    # For local testing with PostgreSQL
    persistence = PersistenceFactory.create(
        backend="postgresql",
        config={"host": "localhost", "database": "cdm_test"}
    )

    # For production with Databricks
    persistence = PersistenceFactory.create(
        backend="delta",
        config={"catalog": "cdm_prod", "schema": "payments"}
    )

    # Write to bronze/silver/gold
    persistence.write_bronze(df, table="raw_pain001", batch_id="...")
    persistence.write_silver(df, table="payment_instruction", batch_id="...")
    persistence.write_gold(df, table="payment_metrics", batch_id="...")
"""

from gps_cdm.ingestion.persistence.base import (
    PersistenceBackend,
    PersistenceConfig,
    WriteMode,
    Layer,
)
from gps_cdm.ingestion.persistence.factory import PersistenceFactory

__all__ = [
    "PersistenceBackend",
    "PersistenceConfig",
    "PersistenceFactory",
    "WriteMode",
    "Layer",
]
