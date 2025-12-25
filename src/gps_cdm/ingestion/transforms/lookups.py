"""
GPS Payments CDM - Lookup Manager
==================================

Manages lookup tables for code transformations and mappings.
Supports broadcast joins for performance optimization.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, broadcast, when, lit, coalesce
from pyspark.sql.types import StructType, StructField, StringType


@dataclass
class LookupTable:
    """Lookup table configuration."""
    name: str
    key_column: str
    value_column: str
    data: Optional[Dict[str, Any]] = None
    df: Optional[DataFrame] = None
    broadcast_df: Optional[DataFrame] = None


class LookupManager:
    """
    Manages lookup tables for code transformations.

    Supports:
    - In-memory dictionary lookups
    - DataFrame-based lookups (for large tables)
    - Broadcast joins for distributed performance
    - Delta table integration
    """

    # Standard lookup tables
    STANDARD_LOOKUPS = {
        "country_code": {
            "key": "iso2",
            "value": "name",
            "data": {
                "US": "United States", "GB": "United Kingdom", "AU": "Australia",
                "CA": "Canada", "DE": "Germany", "FR": "France", "JP": "Japan",
                "CN": "China", "HK": "Hong Kong", "SG": "Singapore",
                "CH": "Switzerland", "NL": "Netherlands", "BE": "Belgium",
                "AT": "Austria", "IT": "Italy", "ES": "Spain", "PT": "Portugal",
                "IE": "Ireland", "LU": "Luxembourg", "SE": "Sweden",
                "NO": "Norway", "DK": "Denmark", "FI": "Finland", "NZ": "New Zealand",
            }
        },
        "currency_code": {
            "key": "code",
            "value": "name",
            "data": {
                "USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound",
                "JPY": "Japanese Yen", "CHF": "Swiss Franc", "AUD": "Australian Dollar",
                "CAD": "Canadian Dollar", "HKD": "Hong Kong Dollar",
                "SGD": "Singapore Dollar", "CNY": "Chinese Yuan",
                "NZD": "New Zealand Dollar", "INR": "Indian Rupee",
                "BRL": "Brazilian Real", "MXN": "Mexican Peso", "ZAR": "South African Rand",
            }
        },
        "currency_decimals": {
            "key": "code",
            "value": "decimals",
            "data": {
                "USD": "2", "EUR": "2", "GBP": "2", "JPY": "0", "CHF": "2",
                "AUD": "2", "CAD": "2", "HKD": "2", "SGD": "2", "CNY": "2",
                "KWD": "3", "BHD": "3", "OMR": "3",  # 3 decimal currencies
            }
        },
        "charge_bearer": {
            "key": "mt_code",
            "value": "iso_code",
            "data": {
                "OUR": "DEBT", "BEN": "CRED", "SHA": "SHAR",
            }
        },
        "purpose_code": {
            "key": "code",
            "value": "description",
            "data": {
                "SALA": "Salary Payment", "SUPP": "Supplier Payment",
                "TAXS": "Tax Payment", "DIVI": "Dividend",
                "RENT": "Rent", "LOAN": "Loan Payment",
                "PENS": "Pension", "INSU": "Insurance Premium",
                "TRAD": "Trade Settlement", "CASH": "Cash Management",
            }
        },
        "payment_method": {
            "key": "code",
            "value": "description",
            "data": {
                "TRF": "Credit Transfer", "TRA": "Credit Transfer Advice",
                "CHK": "Cheque", "DD": "Direct Debit",
            }
        },
        "priority_code": {
            "key": "code",
            "value": "description",
            "data": {
                "HIGH": "High Priority", "NORM": "Normal",
                "LOW": "Low Priority",
            }
        },
        "party_type": {
            "key": "code",
            "value": "description",
            "data": {
                "ORGN": "Organization", "PRVT": "Private Individual",
            }
        },
        "account_type": {
            "key": "code",
            "value": "description",
            "data": {
                "CACC": "Current Account", "SVGS": "Savings Account",
                "LOAN": "Loan Account", "CARD": "Card Account",
                "CASH": "Cash Account", "CISH": "Cash Income",
            }
        },
        "transaction_status": {
            "key": "code",
            "value": "description",
            "data": {
                "ACTC": "Accepted Technical Validation",
                "ACSC": "Accepted Settlement Complete",
                "ACSP": "Accepted Settlement In Process",
                "ACWC": "Accepted With Change",
                "RJCT": "Rejected", "PDNG": "Pending",
                "CANC": "Cancelled",
            }
        },
        "rejection_reason": {
            "key": "code",
            "value": "description",
            "data": {
                "AC01": "Incorrect Account Number",
                "AC04": "Closed Account Number",
                "AC06": "Blocked Account",
                "AG01": "Transaction Forbidden",
                "AM01": "Zero Amount", "AM02": "Not Allowed Amount",
                "AM04": "Insufficient Funds", "AM09": "Wrong Amount",
                "BE01": "Inconsistent With End Customer",
                "RC01": "Bank Identifier Incorrect",
                "RR01": "Missing Debtor Account",
                "RR02": "Missing Debtor Name",
                "RR03": "Missing Creditor Name",
            }
        },
    }

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self._tables: Dict[str, LookupTable] = {}
        self._initialize_standard_lookups()

    def _initialize_standard_lookups(self) -> None:
        """Initialize standard lookup tables."""
        for name, config in self.STANDARD_LOOKUPS.items():
            self._tables[name] = LookupTable(
                name=name,
                key_column=config["key"],
                value_column=config["value"],
                data=config["data"],
            )

    def register(
        self,
        name: str,
        key_column: str,
        value_column: str,
        data: Optional[Dict[str, Any]] = None,
        source_table: Optional[str] = None
    ) -> None:
        """
        Register a lookup table.

        Args:
            name: Table name
            key_column: Column to use as lookup key
            value_column: Column to return as lookup value
            data: Dictionary of key->value mappings
            source_table: Delta table name to load from
        """
        table = LookupTable(
            name=name,
            key_column=key_column,
            value_column=value_column,
            data=data,
        )

        if source_table:
            table.df = self.spark.table(source_table)
            table.broadcast_df = broadcast(table.df)

        self._tables[name] = table

    def get(self, name: str) -> Optional[LookupTable]:
        """Get lookup table by name."""
        return self._tables.get(name)

    def lookup(
        self,
        table_name: str,
        key: Any,
        default: Any = None
    ) -> Any:
        """
        Perform a lookup.

        Args:
            table_name: Name of lookup table
            key: Key to look up
            default: Default value if not found

        Returns:
            Looked up value or default
        """
        table = self._tables.get(table_name)
        if not table:
            return default

        if table.data:
            return table.data.get(str(key), default)

        return default

    def lookup_column(
        self,
        table_name: str,
        key_col: str,
        default_value: Any = None
    ) -> str:
        """
        Generate Spark SQL CASE expression for lookup.

        Args:
            table_name: Name of lookup table
            key_col: Column name containing keys
            default_value: Default value if not found

        Returns:
            Spark SQL CASE expression
        """
        table = self._tables.get(table_name)
        if not table or not table.data:
            return f"COALESCE({key_col}, '{default_value}')"

        cases = []
        for key, value in table.data.items():
            # Escape single quotes
            escaped_value = str(value).replace("'", "''")
            cases.append(f"WHEN {key_col} = '{key}' THEN '{escaped_value}'")

        default = f"'{default_value}'" if default_value else "NULL"
        return f"CASE {' '.join(cases)} ELSE {default} END"

    def get_broadcast_df(self, table_name: str) -> Optional[DataFrame]:
        """
        Get broadcast DataFrame for lookup table.

        Creates DataFrame from dictionary if not already created.
        """
        table = self._tables.get(table_name)
        if not table:
            return None

        if table.broadcast_df:
            return table.broadcast_df

        if table.data:
            # Create DataFrame from dictionary
            rows = [
                {table.key_column: k, table.value_column: v}
                for k, v in table.data.items()
            ]
            table.df = self.spark.createDataFrame(rows)
            table.broadcast_df = broadcast(table.df)
            return table.broadcast_df

        return None

    def join_lookup(
        self,
        df: DataFrame,
        table_name: str,
        join_col: str,
        output_col: str = None,
        default_value: Any = None
    ) -> DataFrame:
        """
        Join lookup table to DataFrame.

        Uses broadcast join for performance.

        Args:
            df: Source DataFrame
            table_name: Lookup table name
            join_col: Column to join on
            output_col: Name for output column (defaults to lookup value column)
            default_value: Default value if not found
        """
        table = self._tables.get(table_name)
        if not table:
            raise ValueError(f"Unknown lookup table: {table_name}")

        lookup_df = self.get_broadcast_df(table_name)
        if lookup_df is None:
            raise ValueError(f"Cannot create lookup DataFrame for: {table_name}")

        output_col = output_col or table.value_column

        # Perform broadcast join
        result = df.join(
            lookup_df,
            df[join_col] == lookup_df[table.key_column],
            "left"
        ).withColumn(
            output_col,
            coalesce(
                lookup_df[table.value_column],
                lit(default_value)
            )
        ).drop(lookup_df[table.key_column]).drop(lookup_df[table.value_column])

        return result

    def list_tables(self) -> List[str]:
        """List all registered lookup tables."""
        return list(self._tables.keys())

    def get_table_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a lookup table."""
        table = self._tables.get(name)
        if not table:
            return None

        return {
            "name": table.name,
            "key_column": table.key_column,
            "value_column": table.value_column,
            "row_count": len(table.data) if table.data else (
                table.df.count() if table.df else 0
            ),
            "has_broadcast_df": table.broadcast_df is not None,
        }


# Singleton instance for global access
_lookup_manager: Optional[LookupManager] = None


def get_lookup_manager(spark: SparkSession = None) -> LookupManager:
    """Get or create global lookup manager instance."""
    global _lookup_manager
    if _lookup_manager is None:
        if spark is None:
            raise ValueError("SparkSession required for first initialization")
        _lookup_manager = LookupManager(spark)
    return _lookup_manager
