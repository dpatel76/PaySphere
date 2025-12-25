"""
GPS CDM - Persistence Factory
=============================

Factory for creating persistence backends based on configuration.
Supports PostgreSQL (testing), Delta Lake (Databricks), and Starburst (federation).

Usage:
    # From environment or config file
    persistence = PersistenceFactory.from_config("config/persistence.yaml")

    # Or programmatically
    persistence = PersistenceFactory.create(
        backend="postgresql",
        spark=spark,
        host="localhost",
        database="cdm_test"
    )
"""

from typing import Dict, Any, Optional
import os
import yaml

from pyspark.sql import SparkSession

from gps_cdm.ingestion.persistence.base import (
    PersistenceBackend,
    PersistenceConfig,
)


class PersistenceFactory:
    """
    Factory for creating persistence backends.

    Supports configuration via:
    - Direct parameters
    - Configuration dictionary
    - YAML configuration file
    - Environment variables
    """

    # Registry of available backends
    _backends: Dict[str, type] = {}

    @classmethod
    def register_backend(cls, name: str, backend_class: type):
        """Register a new backend type."""
        cls._backends[name.lower()] = backend_class

    @classmethod
    def create(
        cls,
        backend: str,
        spark: SparkSession,
        **kwargs
    ) -> PersistenceBackend:
        """
        Create a persistence backend instance.

        Args:
            backend: Backend type (postgresql, delta, starburst)
            spark: SparkSession
            **kwargs: Backend-specific configuration

        Returns:
            Configured PersistenceBackend instance
        """
        # Lazy import backends to avoid circular imports
        cls._ensure_backends_registered()

        backend_lower = backend.lower()
        if backend_lower not in cls._backends:
            available = ", ".join(cls._backends.keys())
            raise ValueError(
                f"Unknown backend: {backend}. Available: {available}"
            )

        # Build config from kwargs
        config = PersistenceConfig(backend=backend_lower, **kwargs)

        # Create backend instance
        backend_class = cls._backends[backend_lower]
        instance = backend_class(spark, config)

        # Initialize if auto_init enabled (default True)
        if kwargs.get("auto_init", True):
            instance.initialize()

        return instance

    @classmethod
    def from_dict(cls, spark: SparkSession, config_dict: Dict[str, Any]) -> PersistenceBackend:
        """
        Create backend from configuration dictionary.

        Args:
            spark: SparkSession
            config_dict: Configuration dictionary

        Returns:
            Configured PersistenceBackend instance
        """
        backend = config_dict.pop("backend", "postgresql")
        return cls.create(backend, spark, **config_dict)

    @classmethod
    def from_config_file(
        cls,
        spark: SparkSession,
        config_path: str,
        environment: str = "development"
    ) -> PersistenceBackend:
        """
        Create backend from YAML configuration file.

        Args:
            spark: SparkSession
            config_path: Path to YAML config file
            environment: Environment to use (development, staging, production)

        Returns:
            Configured PersistenceBackend instance

        Example config file:
            development:
              backend: postgresql
              host: localhost
              port: 5432
              database: cdm_dev

            production:
              backend: delta
              catalog: cdm_prod
              unity_catalog: true
              storage_path: abfss://...
        """
        with open(config_path, "r") as f:
            all_config = yaml.safe_load(f)

        if environment not in all_config:
            raise ValueError(
                f"Environment '{environment}' not found in config. "
                f"Available: {list(all_config.keys())}"
            )

        config_dict = all_config[environment]
        return cls.from_dict(spark, config_dict)

    @classmethod
    def from_environment(cls, spark: SparkSession) -> PersistenceBackend:
        """
        Create backend from environment variables.

        Environment variables:
            CDM_PERSISTENCE_BACKEND: postgresql, delta, starburst
            CDM_PERSISTENCE_HOST: Database host
            CDM_PERSISTENCE_PORT: Database port
            CDM_PERSISTENCE_DATABASE: Database name
            CDM_PERSISTENCE_USER: Username
            CDM_PERSISTENCE_PASSWORD: Password
            CDM_PERSISTENCE_CATALOG: Delta/Starburst catalog
            CDM_PERSISTENCE_STORAGE_PATH: Delta storage path

        Returns:
            Configured PersistenceBackend instance
        """
        backend = os.environ.get("CDM_PERSISTENCE_BACKEND", "postgresql")

        config = {
            "host": os.environ.get("CDM_PERSISTENCE_HOST"),
            "port": int(os.environ.get("CDM_PERSISTENCE_PORT", 0)) or None,
            "database": os.environ.get("CDM_PERSISTENCE_DATABASE"),
            "user": os.environ.get("CDM_PERSISTENCE_USER"),
            "password": os.environ.get("CDM_PERSISTENCE_PASSWORD"),
            "catalog": os.environ.get("CDM_PERSISTENCE_CATALOG", "cdm"),
            "storage_path": os.environ.get("CDM_PERSISTENCE_STORAGE_PATH"),
            "unity_catalog": os.environ.get("CDM_PERSISTENCE_UNITY_CATALOG", "").lower() == "true",
        }

        # Remove None values
        config = {k: v for k, v in config.items() if v is not None}

        return cls.create(backend, spark, **config)

    @classmethod
    def _ensure_backends_registered(cls):
        """Register all available backends."""
        if cls._backends:
            return

        # Import and register backends
        from gps_cdm.ingestion.persistence.postgresql import PostgreSQLBackend
        from gps_cdm.ingestion.persistence.delta import DeltaLakeBackend
        from gps_cdm.ingestion.persistence.databricks_ce import DatabricksCEBackend
        from gps_cdm.ingestion.persistence.databricks_free import DatabricksFreeBackend

        cls.register_backend("postgresql", PostgreSQLBackend)
        cls.register_backend("postgres", PostgreSQLBackend)
        cls.register_backend("pg", PostgreSQLBackend)

        cls.register_backend("delta", DeltaLakeBackend)
        cls.register_backend("deltalake", DeltaLakeBackend)
        cls.register_backend("databricks", DeltaLakeBackend)

        # Databricks Community Edition (being retired Jan 2026)
        cls.register_backend("databricks_ce", DatabricksCEBackend)
        cls.register_backend("databricks-ce", DatabricksCEBackend)
        cls.register_backend("ce", DatabricksCEBackend)

        # Databricks Free Edition (recommended - serverless, Unity Catalog)
        cls.register_backend("databricks_free", DatabricksFreeBackend)
        cls.register_backend("databricks-free", DatabricksFreeBackend)
        cls.register_backend("free", DatabricksFreeBackend)

        # Starburst can be added later
        # cls.register_backend("starburst", StarburstBackend)


# Convenience function for quick setup
def get_persistence(
    spark: SparkSession,
    backend: Optional[str] = None,
    **kwargs
) -> PersistenceBackend:
    """
    Get a persistence backend with minimal configuration.

    Uses environment variables if backend not specified.

    Args:
        spark: SparkSession
        backend: Optional backend override
        **kwargs: Backend configuration

    Returns:
        Configured PersistenceBackend
    """
    if backend:
        return PersistenceFactory.create(backend, spark, **kwargs)
    else:
        return PersistenceFactory.from_environment(spark)
