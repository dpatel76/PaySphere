"""
GPS Payments CDM - Transform Library
=====================================

Comprehensive library of reusable transform functions for
configuration-driven field mappings.

Categories:
- String transforms: formatting, parsing, cleaning
- Numeric transforms: currency, rounding, conversion
- Date/Time transforms: parsing, formatting, timezone
- Identifier transforms: BIC, IBAN, LEI validation
- Code transforms: ISO code lookups, mappings
- Conditional transforms: if/then logic
- Aggregation transforms: merge, split, collect
"""

from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass
from functools import wraps
import re
from datetime import datetime, date

from pyspark.sql import Column
from pyspark.sql.functions import (
    col, lit, when, coalesce, concat, concat_ws,
    upper, lower, trim, ltrim, rtrim, lpad, rpad,
    substring, length, regexp_extract, regexp_replace,
    split, element_at, array_join, transform as spark_transform,
    to_date, to_timestamp, date_format, current_date, current_timestamp,
    year, month, dayofmonth, hour, minute, second,
    datediff, months_between, add_months, date_add, date_sub,
    round as spark_round, floor, ceil, abs as spark_abs,
    cast, format_number, format_string,
    sha2, md5, base64, unbase64,
    from_json, to_json, get_json_object,
    xpath_string, xpath_int, xpath_float,
    struct, array, create_map, map_keys, map_values,
    size, explode, posexplode,
    udf, pandas_udf,
    expr,
)
from pyspark.sql.types import StringType, DecimalType, DateType, TimestampType


@dataclass
class TransformFunction:
    """Registered transform function."""
    name: str
    func: Callable
    category: str
    description: str
    spark_expr: Optional[str] = None  # Native Spark SQL if available


class TransformLibrary:
    """
    Library of reusable transform functions.

    All transforms can be invoked by name from YAML mappings.
    Most transforms have both Python and Spark SQL implementations
    for optimal performance.
    """

    _transforms: Dict[str, TransformFunction] = {}

    @classmethod
    def register(
        cls,
        name: str,
        category: str,
        description: str,
        spark_expr: Optional[str] = None
    ):
        """Decorator to register a transform function."""
        def decorator(func: Callable):
            cls._transforms[name] = TransformFunction(
                name=name,
                func=func,
                category=category,
                description=description,
                spark_expr=spark_expr,
            )
            return func
        return decorator

    @classmethod
    def get(cls, name: str) -> Optional[TransformFunction]:
        """Get transform function by name."""
        return cls._transforms.get(name)

    @classmethod
    def list_by_category(cls, category: str) -> List[TransformFunction]:
        """List all transforms in a category."""
        return [t for t in cls._transforms.values() if t.category == category]

    @classmethod
    def list_all(cls) -> List[str]:
        """List all registered transform names."""
        return list(cls._transforms.keys())

    @classmethod
    def get_spark_expr(cls, name: str, input_col: str, **params) -> Optional[str]:
        """Get Spark SQL expression for transform if available."""
        transform = cls._transforms.get(name)
        if transform and transform.spark_expr:
            return transform.spark_expr.format(input=input_col, **params)
        return None

    @classmethod
    def apply(cls, name: str, value: Any, **params) -> Any:
        """Apply transform function to a value."""
        transform = cls._transforms.get(name)
        if transform:
            return transform.func(value, **params)
        raise ValueError(f"Unknown transform: {name}")


# ==============================================================================
# STRING TRANSFORMS
# ==============================================================================

@TransformLibrary.register(
    "trim", "string", "Remove leading/trailing whitespace",
    spark_expr="TRIM({input})"
)
def transform_trim(value: Any) -> str:
    """Remove leading and trailing whitespace."""
    return str(value).strip() if value else ""


@TransformLibrary.register(
    "upper", "string", "Convert to uppercase",
    spark_expr="UPPER({input})"
)
def transform_upper(value: Any) -> str:
    """Convert to uppercase."""
    return str(value).upper() if value else ""


@TransformLibrary.register(
    "lower", "string", "Convert to lowercase",
    spark_expr="LOWER({input})"
)
def transform_lower(value: Any) -> str:
    """Convert to lowercase."""
    return str(value).lower() if value else ""


@TransformLibrary.register(
    "capitalize", "string", "Capitalize first letter",
    spark_expr="INITCAP({input})"
)
def transform_capitalize(value: Any) -> str:
    """Capitalize first letter of each word."""
    return str(value).title() if value else ""


@TransformLibrary.register(
    "left_pad", "string", "Left-pad string to length",
    spark_expr="LPAD({input}, {length}, '{pad_char}')"
)
def transform_left_pad(value: Any, length: int = 10, pad_char: str = "0") -> str:
    """Left-pad string to specified length."""
    return str(value).rjust(length, pad_char) if value else ""


@TransformLibrary.register(
    "right_pad", "string", "Right-pad string to length",
    spark_expr="RPAD({input}, {length}, '{pad_char}')"
)
def transform_right_pad(value: Any, length: int = 10, pad_char: str = " ") -> str:
    """Right-pad string to specified length."""
    return str(value).ljust(length, pad_char) if value else ""


@TransformLibrary.register(
    "truncate", "string", "Truncate string to max length",
    spark_expr="SUBSTRING({input}, 1, {max_length})"
)
def transform_truncate(value: Any, max_length: int = 100) -> str:
    """Truncate string to maximum length."""
    return str(value)[:max_length] if value else ""


@TransformLibrary.register(
    "remove_special_chars", "string", "Remove special characters",
    spark_expr="REGEXP_REPLACE({input}, '[^a-zA-Z0-9 ]', '')"
)
def transform_remove_special_chars(value: Any) -> str:
    """Remove special characters, keeping alphanumeric and spaces."""
    return re.sub(r'[^a-zA-Z0-9 ]', '', str(value)) if value else ""


@TransformLibrary.register(
    "normalize_whitespace", "string", "Normalize whitespace to single spaces",
    spark_expr="TRIM(REGEXP_REPLACE({input}, '\\\\s+', ' '))"
)
def transform_normalize_whitespace(value: Any) -> str:
    """Normalize multiple whitespace to single spaces."""
    return " ".join(str(value).split()) if value else ""


@TransformLibrary.register(
    "extract_regex", "string", "Extract using regex pattern",
    spark_expr="REGEXP_EXTRACT({input}, '{pattern}', {group})"
)
def transform_extract_regex(value: Any, pattern: str, group: int = 0) -> str:
    """Extract value using regex pattern."""
    if not value:
        return ""
    match = re.search(pattern, str(value))
    if match:
        return match.group(group) if group <= len(match.groups()) else match.group(0)
    return ""


@TransformLibrary.register(
    "replace", "string", "Replace substring",
    spark_expr="REPLACE({input}, '{old}', '{new}')"
)
def transform_replace(value: Any, old: str, new: str) -> str:
    """Replace substring."""
    return str(value).replace(old, new) if value else ""


@TransformLibrary.register(
    "split_get", "string", "Split string and get element",
    spark_expr="ELEMENT_AT(SPLIT({input}, '{delimiter}'), {index})"
)
def transform_split_get(value: Any, delimiter: str = ",", index: int = 1) -> str:
    """Split string by delimiter and get element at index (1-based)."""
    if not value:
        return ""
    parts = str(value).split(delimiter)
    # Convert to 0-based index
    idx = index - 1 if index > 0 else index
    return parts[idx] if abs(idx) < len(parts) else ""


# ==============================================================================
# NUMERIC TRANSFORMS
# ==============================================================================

@TransformLibrary.register(
    "to_decimal", "numeric", "Convert to decimal",
    spark_expr="CAST({input} AS DECIMAL({precision}, {scale}))"
)
def transform_to_decimal(
    value: Any,
    precision: int = 18,
    scale: int = 2
) -> Optional[float]:
    """Convert to decimal with specified precision and scale."""
    if value is None:
        return None
    try:
        num = float(str(value).replace(",", ""))
        return round(num, scale)
    except (ValueError, TypeError):
        return None


@TransformLibrary.register(
    "round", "numeric", "Round to specified decimal places",
    spark_expr="ROUND({input}, {decimals})"
)
def transform_round(value: Any, decimals: int = 2) -> Optional[float]:
    """Round to specified decimal places."""
    if value is None:
        return None
    try:
        return round(float(value), decimals)
    except (ValueError, TypeError):
        return None


@TransformLibrary.register(
    "floor", "numeric", "Round down to integer",
    spark_expr="FLOOR({input})"
)
def transform_floor(value: Any) -> Optional[int]:
    """Round down to nearest integer."""
    if value is None:
        return None
    try:
        import math
        return math.floor(float(value))
    except (ValueError, TypeError):
        return None


@TransformLibrary.register(
    "ceil", "numeric", "Round up to integer",
    spark_expr="CEIL({input})"
)
def transform_ceil(value: Any) -> Optional[int]:
    """Round up to nearest integer."""
    if value is None:
        return None
    try:
        import math
        return math.ceil(float(value))
    except (ValueError, TypeError):
        return None


@TransformLibrary.register(
    "abs", "numeric", "Absolute value",
    spark_expr="ABS({input})"
)
def transform_abs(value: Any) -> Optional[float]:
    """Get absolute value."""
    if value is None:
        return None
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return None


@TransformLibrary.register(
    "currency_format", "numeric", "Format as currency",
    spark_expr="FORMAT_NUMBER({input}, {decimals})"
)
def transform_currency_format(value: Any, decimals: int = 2) -> str:
    """Format number as currency string."""
    if value is None:
        return ""
    try:
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return ""


@TransformLibrary.register(
    "implied_decimal", "numeric", "Apply implied decimal places",
    spark_expr="CAST({input} AS DECIMAL(18,2)) / POWER(10, {places})"
)
def transform_implied_decimal(value: Any, places: int = 2) -> Optional[float]:
    """Convert integer with implied decimals (e.g., cents to dollars)."""
    if value is None:
        return None
    try:
        return float(value) / (10 ** places)
    except (ValueError, TypeError):
        return None


@TransformLibrary.register(
    "to_integer", "numeric", "Convert to integer",
    spark_expr="CAST({input} AS INT)"
)
def transform_to_integer(value: Any) -> Optional[int]:
    """Convert to integer."""
    if value is None:
        return None
    try:
        return int(float(str(value).replace(",", "")))
    except (ValueError, TypeError):
        return None


# ==============================================================================
# DATE/TIME TRANSFORMS
# ==============================================================================

@TransformLibrary.register(
    "parse_date", "datetime", "Parse date from string",
    spark_expr="TO_DATE({input}, '{format}')"
)
def transform_parse_date(value: Any, format: str = "%Y-%m-%d") -> Optional[date]:
    """Parse date from string."""
    if not value:
        return None
    try:
        return datetime.strptime(str(value), format).date()
    except (ValueError, TypeError):
        return None


@TransformLibrary.register(
    "parse_datetime", "datetime", "Parse datetime from string",
    spark_expr="TO_TIMESTAMP({input}, '{format}')"
)
def transform_parse_datetime(
    value: Any,
    format: str = "%Y-%m-%dT%H:%M:%S"
) -> Optional[datetime]:
    """Parse datetime from string."""
    if not value:
        return None
    try:
        return datetime.strptime(str(value), format)
    except (ValueError, TypeError):
        return None


@TransformLibrary.register(
    "format_date", "datetime", "Format date as string",
    spark_expr="DATE_FORMAT({input}, '{format}')"
)
def transform_format_date(value: Any, format: str = "yyyy-MM-dd") -> str:
    """Format date as string."""
    if not value:
        return ""
    if isinstance(value, (date, datetime)):
        # Convert Spark format to Python strftime
        py_format = format.replace("yyyy", "%Y").replace("MM", "%m").replace("dd", "%d")
        return value.strftime(py_format)
    return str(value)


@TransformLibrary.register(
    "iso_date", "datetime", "Parse ISO 8601 date",
    spark_expr="TO_DATE({input})"
)
def transform_iso_date(value: Any) -> Optional[date]:
    """Parse ISO 8601 date (YYYY-MM-DD)."""
    return transform_parse_date(value, "%Y-%m-%d")


@TransformLibrary.register(
    "iso_datetime", "datetime", "Parse ISO 8601 datetime",
    spark_expr="TO_TIMESTAMP({input})"
)
def transform_iso_datetime(value: Any) -> Optional[datetime]:
    """Parse ISO 8601 datetime."""
    if not value:
        return None
    try:
        # Handle various ISO formats
        val = str(value)
        if "T" in val:
            if val.endswith("Z"):
                val = val[:-1] + "+00:00"
            return datetime.fromisoformat(val)
        return datetime.strptime(val, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


@TransformLibrary.register(
    "mt_date", "datetime", "Parse SWIFT MT date (YYMMDD)",
    spark_expr="TO_DATE(CONCAT('20', {input}), 'yyyyMMdd')"
)
def transform_mt_date(value: Any) -> Optional[date]:
    """Parse SWIFT MT date format (YYMMDD)."""
    if not value or len(str(value)) != 6:
        return None
    try:
        return datetime.strptime(str(value), "%y%m%d").date()
    except (ValueError, TypeError):
        return None


@TransformLibrary.register(
    "add_days", "datetime", "Add days to date",
    spark_expr="DATE_ADD({input}, {days})"
)
def transform_add_days(value: Any, days: int) -> Optional[date]:
    """Add days to date."""
    if not value:
        return None
    from datetime import timedelta
    if isinstance(value, date):
        return value + timedelta(days=days)
    return None


@TransformLibrary.register(
    "extract_year", "datetime", "Extract year from date",
    spark_expr="YEAR({input})"
)
def transform_extract_year(value: Any) -> Optional[int]:
    """Extract year from date."""
    if not value:
        return None
    if isinstance(value, (date, datetime)):
        return value.year
    return None


@TransformLibrary.register(
    "extract_month", "datetime", "Extract month from date",
    spark_expr="MONTH({input})"
)
def transform_extract_month(value: Any) -> Optional[int]:
    """Extract month from date."""
    if not value:
        return None
    if isinstance(value, (date, datetime)):
        return value.month
    return None


# ==============================================================================
# IDENTIFIER TRANSFORMS
# ==============================================================================

@TransformLibrary.register(
    "validate_bic", "identifier", "Validate and format BIC",
    spark_expr="CASE WHEN {input} RLIKE '^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$' THEN {input} ELSE NULL END"
)
def transform_validate_bic(value: Any) -> Optional[str]:
    """Validate and return BIC if valid."""
    if not value:
        return None
    bic = str(value).upper().strip()
    # BIC format: 4 letters (bank) + 2 letters (country) + 2 alphanum (location) + optional 3 alphanum (branch)
    pattern = r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$'
    if re.match(pattern, bic):
        return bic
    return None


@TransformLibrary.register(
    "normalize_bic", "identifier", "Normalize BIC to 11 characters",
    spark_expr="CASE WHEN LENGTH({input}) = 8 THEN CONCAT({input}, 'XXX') ELSE {input} END"
)
def transform_normalize_bic(value: Any) -> Optional[str]:
    """Normalize BIC to 11 characters (add XXX if 8 chars)."""
    bic = transform_validate_bic(value)
    if bic and len(bic) == 8:
        return bic + "XXX"
    return bic


@TransformLibrary.register(
    "extract_bic_country", "identifier", "Extract country from BIC",
    spark_expr="SUBSTRING({input}, 5, 2)"
)
def transform_extract_bic_country(value: Any) -> Optional[str]:
    """Extract country code from BIC."""
    bic = transform_validate_bic(value)
    if bic and len(bic) >= 6:
        return bic[4:6]
    return None


@TransformLibrary.register(
    "validate_iban", "identifier", "Validate IBAN format",
    spark_expr="CASE WHEN {input} RLIKE '^[A-Z]{2}[0-9]{2}[A-Z0-9]{4,30}$' THEN {input} ELSE NULL END"
)
def transform_validate_iban(value: Any) -> Optional[str]:
    """Validate and return IBAN if valid format."""
    if not value:
        return None
    iban = str(value).upper().replace(" ", "")
    # Basic format check (full validation requires modulo-97)
    pattern = r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{4,30}$'
    if re.match(pattern, iban):
        return iban
    return None


@TransformLibrary.register(
    "extract_iban_country", "identifier", "Extract country from IBAN",
    spark_expr="SUBSTRING({input}, 1, 2)"
)
def transform_extract_iban_country(value: Any) -> Optional[str]:
    """Extract country code from IBAN."""
    iban = transform_validate_iban(value)
    if iban:
        return iban[:2]
    return None


@TransformLibrary.register(
    "validate_lei", "identifier", "Validate LEI format",
    spark_expr="CASE WHEN {input} RLIKE '^[A-Z0-9]{18}[0-9]{2}$' THEN {input} ELSE NULL END"
)
def transform_validate_lei(value: Any) -> Optional[str]:
    """Validate Legal Entity Identifier."""
    if not value:
        return None
    lei = str(value).upper().strip()
    # LEI format: 18 alphanumeric + 2 numeric
    pattern = r'^[A-Z0-9]{18}[0-9]{2}$'
    if re.match(pattern, lei) and len(lei) == 20:
        return lei
    return None


@TransformLibrary.register(
    "format_account", "identifier", "Format account number",
    spark_expr="TRIM(REGEXP_REPLACE({input}, '[^0-9A-Za-z]', ''))"
)
def transform_format_account(value: Any) -> str:
    """Clean and format account number."""
    if not value:
        return ""
    # Remove non-alphanumeric characters
    return re.sub(r'[^0-9A-Za-z]', '', str(value))


@TransformLibrary.register(
    "mask_account", "identifier", "Mask account number (show last 4)",
    spark_expr="CONCAT(REPEAT('*', LENGTH({input}) - 4), SUBSTRING({input}, -4, 4))"
)
def transform_mask_account(value: Any) -> str:
    """Mask account number, showing only last 4 digits."""
    if not value:
        return ""
    acct = str(value)
    if len(acct) <= 4:
        return acct
    return "*" * (len(acct) - 4) + acct[-4:]


# ==============================================================================
# CODE/LOOKUP TRANSFORMS
# ==============================================================================

@TransformLibrary.register(
    "country_iso2_to_iso3", "code", "Convert ISO 2-letter country to 3-letter",
    spark_expr="CASE {input} WHEN 'US' THEN 'USA' WHEN 'GB' THEN 'GBR' WHEN 'AU' THEN 'AUS' ELSE {input} END"
)
def transform_country_iso2_to_iso3(value: Any) -> Optional[str]:
    """Convert ISO 3166-1 alpha-2 to alpha-3 country code."""
    ISO2_TO_ISO3 = {
        "US": "USA", "GB": "GBR", "AU": "AUS", "CA": "CAN", "DE": "DEU",
        "FR": "FRA", "JP": "JPN", "CN": "CHN", "HK": "HKG", "SG": "SGP",
        "CH": "CHE", "NL": "NLD", "BE": "BEL", "AT": "AUT", "IT": "ITA",
        "ES": "ESP", "PT": "PRT", "IE": "IRL", "LU": "LUX", "SE": "SWE",
        "NO": "NOR", "DK": "DNK", "FI": "FIN", "NZ": "NZL", "IN": "IND",
        "BR": "BRA", "MX": "MEX", "ZA": "ZAF", "AE": "ARE", "SA": "SAU",
    }
    if not value:
        return None
    return ISO2_TO_ISO3.get(str(value).upper(), str(value).upper())


@TransformLibrary.register(
    "currency_to_country", "code", "Get primary country for currency",
    spark_expr="CASE {input} WHEN 'USD' THEN 'US' WHEN 'EUR' THEN 'DE' WHEN 'GBP' THEN 'GB' ELSE NULL END"
)
def transform_currency_to_country(value: Any) -> Optional[str]:
    """Get primary country for currency code."""
    CURRENCY_COUNTRY = {
        "USD": "US", "EUR": "DE", "GBP": "GB", "JPY": "JP", "CHF": "CH",
        "AUD": "AU", "CAD": "CA", "HKD": "HK", "SGD": "SG", "CNY": "CN",
        "NZD": "NZ", "INR": "IN", "BRL": "BR", "MXN": "MX", "ZAR": "ZA",
        "AED": "AE", "SAR": "SA", "SEK": "SE", "NOK": "NO", "DKK": "DK",
    }
    if not value:
        return None
    return CURRENCY_COUNTRY.get(str(value).upper())


@TransformLibrary.register(
    "charge_bearer_code", "code", "Map charge bearer to ISO code",
    spark_expr="CASE UPPER({input}) WHEN 'OUR' THEN 'DEBT' WHEN 'BEN' THEN 'CRED' WHEN 'SHA' THEN 'SHAR' ELSE 'SHAR' END"
)
def transform_charge_bearer_code(value: Any) -> str:
    """Map charge bearer code to ISO 20022 code."""
    BEARER_MAP = {
        "OUR": "DEBT",  # Debtor pays all charges
        "BEN": "CRED",  # Creditor pays all charges
        "SHA": "SHAR",  # Shared
        "SLEV": "SLEV", # Service Level
    }
    if not value:
        return "SHAR"
    return BEARER_MAP.get(str(value).upper(), "SHAR")


@TransformLibrary.register(
    "payment_type_code", "code", "Map payment type to standard code"
)
def transform_payment_type_code(value: Any) -> Optional[str]:
    """Map payment type description to standard code."""
    TYPE_MAP = {
        "CREDIT TRANSFER": "TRF",
        "DIRECT DEBIT": "DD",
        "CHEQUE": "CHK",
        "CARD PAYMENT": "CARD",
        "WIRE": "TRF",
        "ACH": "ACH",
        "SEPA": "TRF",
    }
    if not value:
        return None
    key = str(value).upper()
    for pattern, code in TYPE_MAP.items():
        if pattern in key:
            return code
    return None


# ==============================================================================
# CONDITIONAL TRANSFORMS
# ==============================================================================

@TransformLibrary.register(
    "coalesce", "conditional", "Return first non-null value",
    spark_expr="COALESCE({inputs})"
)
def transform_coalesce(*values) -> Any:
    """Return first non-null value."""
    for v in values:
        if v is not None:
            return v
    return None


@TransformLibrary.register(
    "default_if_null", "conditional", "Return default if value is null",
    spark_expr="COALESCE({input}, '{default}')"
)
def transform_default_if_null(value: Any, default: Any) -> Any:
    """Return default if value is null."""
    return value if value is not None else default


@TransformLibrary.register(
    "null_if_empty", "conditional", "Return null if empty string",
    spark_expr="CASE WHEN TRIM({input}) = '' THEN NULL ELSE {input} END"
)
def transform_null_if_empty(value: Any) -> Any:
    """Return null if value is empty string."""
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


@TransformLibrary.register(
    "if_equals", "conditional", "Return value if equals condition",
    spark_expr="CASE WHEN {input} = '{condition}' THEN '{then_value}' ELSE '{else_value}' END"
)
def transform_if_equals(
    value: Any,
    condition: Any,
    then_value: Any,
    else_value: Any = None
) -> Any:
    """Return then_value if value equals condition, else else_value."""
    if value == condition:
        return then_value
    return else_value


@TransformLibrary.register(
    "if_contains", "conditional", "Return value if contains substring",
    spark_expr="CASE WHEN {input} LIKE '%{substring}%' THEN '{then_value}' ELSE '{else_value}' END"
)
def transform_if_contains(
    value: Any,
    substring: str,
    then_value: Any,
    else_value: Any = None
) -> Any:
    """Return then_value if value contains substring."""
    if value and substring in str(value):
        return then_value
    return else_value


# ==============================================================================
# AGGREGATION/MERGE TRANSFORMS
# ==============================================================================

@TransformLibrary.register(
    "concat", "aggregation", "Concatenate values",
    spark_expr="CONCAT({inputs})"
)
def transform_concat(*values) -> str:
    """Concatenate values into single string."""
    return "".join(str(v) for v in values if v is not None)


@TransformLibrary.register(
    "concat_ws", "aggregation", "Concatenate with separator",
    spark_expr="CONCAT_WS('{separator}', {inputs})"
)
def transform_concat_ws(separator: str, *values) -> str:
    """Concatenate values with separator."""
    return separator.join(str(v) for v in values if v is not None)


@TransformLibrary.register(
    "build_address", "aggregation", "Build formatted address"
)
def transform_build_address(
    street: str = None,
    building: str = None,
    city: str = None,
    postal_code: str = None,
    country: str = None
) -> str:
    """Build formatted address from components."""
    parts = []
    if building:
        parts.append(str(building))
    if street:
        parts.append(str(street))
    if city:
        parts.append(str(city))
    if postal_code:
        parts.append(str(postal_code))
    if country:
        parts.append(str(country))
    return ", ".join(parts)


@TransformLibrary.register(
    "build_name", "aggregation", "Build full name from parts"
)
def transform_build_name(
    family_name: str = None,
    given_name: str = None,
    middle_name: str = None,
    title: str = None
) -> str:
    """Build full name from components."""
    parts = []
    if title:
        parts.append(str(title))
    if given_name:
        parts.append(str(given_name))
    if middle_name:
        parts.append(str(middle_name))
    if family_name:
        parts.append(str(family_name))
    return " ".join(parts)


# ==============================================================================
# HASH/SECURITY TRANSFORMS
# ==============================================================================

@TransformLibrary.register(
    "sha256", "hash", "Generate SHA-256 hash",
    spark_expr="SHA2({input}, 256)"
)
def transform_sha256(value: Any) -> str:
    """Generate SHA-256 hash of value."""
    if not value:
        return ""
    import hashlib
    return hashlib.sha256(str(value).encode()).hexdigest()


@TransformLibrary.register(
    "md5", "hash", "Generate MD5 hash",
    spark_expr="MD5({input})"
)
def transform_md5(value: Any) -> str:
    """Generate MD5 hash of value."""
    if not value:
        return ""
    import hashlib
    return hashlib.md5(str(value).encode()).hexdigest()


@TransformLibrary.register(
    "generate_uuid", "hash", "Generate UUID",
    spark_expr="UUID()"
)
def transform_generate_uuid() -> str:
    """Generate UUID."""
    import uuid
    return str(uuid.uuid4())


# ==============================================================================
# PAYMENT-SPECIFIC TRANSFORMS
# ==============================================================================

@TransformLibrary.register(
    "parse_mt_amount", "payment", "Parse SWIFT MT amount field"
)
def transform_parse_mt_amount(value: Any) -> Optional[float]:
    """Parse amount from MT 32A/33B format (currency + amount)."""
    if not value:
        return None
    # Format: CCYAmount (e.g., "USD1000,50" or "1000,50")
    val = str(value).strip()
    # Remove currency if present
    val = re.sub(r'^[A-Z]{3}', '', val)
    # Replace comma decimal separator
    val = val.replace(",", ".")
    try:
        return float(val)
    except ValueError:
        return None


@TransformLibrary.register(
    "parse_mt_currency", "payment", "Extract currency from MT amount field"
)
def transform_parse_mt_currency(value: Any) -> Optional[str]:
    """Extract currency code from MT 32A/33B format."""
    if not value:
        return None
    val = str(value).strip()
    match = re.match(r'^([A-Z]{3})', val)
    if match:
        return match.group(1)
    return None


@TransformLibrary.register(
    "format_remittance", "payment", "Format remittance information"
)
def transform_format_remittance(value: Any, max_length: int = 140) -> str:
    """Format remittance information to standard length."""
    if not value:
        return ""
    # Clean and normalize
    text = transform_normalize_whitespace(value)
    # Truncate
    return text[:max_length]


@TransformLibrary.register(
    "detect_payment_purpose", "payment", "Detect payment purpose from remittance"
)
def transform_detect_payment_purpose(value: Any) -> Optional[str]:
    """Detect payment purpose code from remittance information."""
    PURPOSE_PATTERNS = {
        r'\b(SALARY|WAGES|PAY)\b': "SALA",
        r'\b(INVOICE|INV|PAYMENT FOR)\b': "SUPP",
        r'\b(TAX|TAXES)\b': "TAXS",
        r'\b(DIVIDEND|DIV)\b': "DIVI",
        r'\b(RENT|LEASE)\b': "RENT",
        r'\b(LOAN|MORTGAGE)\b': "LOAN",
        r'\b(PENSION)\b': "PENS",
        r'\b(INSURANCE|PREMIUM)\b': "INSU",
    }
    if not value:
        return None
    text = str(value).upper()
    for pattern, code in PURPOSE_PATTERNS.items():
        if re.search(pattern, text):
            return code
    return None


# Register summary
def get_transform_summary() -> Dict[str, int]:
    """Get count of transforms by category."""
    summary = {}
    for transform in TransformLibrary._transforms.values():
        category = transform.category
        summary[category] = summary.get(category, 0) + 1
    return summary
