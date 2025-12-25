"""
GPS Payments CDM - Ingestion Framework Data Models
===================================================

Dataclass models representing mapping configurations.
These are the internal representation of YAML mapping files.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


class SourceFormat(str, Enum):
    """Supported source message formats."""
    XML = "XML"
    SWIFT_MT = "SWIFT_MT"
    JSON = "JSON"
    CSV = "CSV"
    FIXED_WIDTH = "FIXED_WIDTH"
    EDIFACT = "EDIFACT"


class DataType(str, Enum):
    """Supported data types."""
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    UUID = "uuid"
    ENUM = "enum"
    ARRAY = "array"
    OBJECT = "object"


class TransformType(str, Enum):
    """Types of field transformations."""
    DIRECT = "direct"
    LOOKUP = "lookup"
    EXPRESSION = "expression"
    CONDITIONAL = "conditional"
    SPLIT = "split"
    MERGE = "merge"
    REGEX = "regex"
    TEMPLATE = "template"
    CUSTOM = "custom"
    # Extended types for complex transformations
    XML_TO_JSON = "xml_to_json"
    CONSTANT = "constant"
    CONCAT = "concat"
    COALESCE = "coalesce"
    FLATTEN = "flatten"
    EXTRACT = "extract"


class Severity(str, Enum):
    """Validation severity levels."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ExtractHint(str, Enum):
    """Hints for value extraction."""
    TEXT_CONTENT = "text_content"
    ATTRIBUTE = "attribute"
    FULL_ELEMENT = "full_element"
    CHILD_ELEMENTS = "child_elements"


@dataclass
class SourceConfig:
    """Configuration for source message parsing."""
    format: SourceFormat
    parser: str

    # XML-specific
    namespace: Optional[str] = None
    root_element: Optional[str] = None

    # MT-specific
    message_type: Optional[str] = None

    # CSV-specific
    delimiter: str = ","
    header: bool = True
    encoding: str = "utf-8"

    # Fixed-width specific
    record_length: Optional[int] = None

    def get_parser_config(self) -> Dict[str, Any]:
        """Get parser-specific configuration."""
        config = {"format": self.format.value, "parser": self.parser}

        if self.format == SourceFormat.XML:
            config.update({
                "namespace": self.namespace,
                "root_element": self.root_element,
            })
        elif self.format == SourceFormat.SWIFT_MT:
            config["message_type"] = self.message_type
        elif self.format == SourceFormat.CSV:
            config.update({
                "delimiter": self.delimiter,
                "header": self.header,
                "encoding": self.encoding,
            })
        elif self.format == SourceFormat.FIXED_WIDTH:
            config["record_length"] = self.record_length

        return config


@dataclass
class TransformConfig:
    """Configuration for field transformation."""
    type: TransformType = TransformType.DIRECT

    # Lookup options
    table: Optional[str] = None
    mapping: Optional[Dict[str, Any]] = None
    default: Optional[Any] = None

    # Expression options
    expr: Optional[str] = None
    depends_on: Optional[List[str]] = None

    # Regex options
    pattern: Optional[str] = None
    group: int = 0

    # Template options
    template: Optional[str] = None

    # Custom function
    function: Optional[str] = None
    params: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Union[str, Dict]) -> "TransformConfig":
        """Create from dictionary or string."""
        if isinstance(data, str):
            # Simple transform name - try to match, fall back to CUSTOM
            try:
                transform_type = TransformType(data)
            except ValueError:
                transform_type = TransformType.CUSTOM
            return cls(type=transform_type, function=data if transform_type == TransformType.CUSTOM else None)

        # Get transform type, falling back to CUSTOM for unknown types
        type_str = data.get("type", "direct")
        try:
            transform_type = TransformType(type_str)
        except ValueError:
            transform_type = TransformType.CUSTOM

        return cls(
            type=transform_type,
            table=data.get("table"),
            mapping=data.get("mapping"),
            default=data.get("default"),
            expr=data.get("expr"),
            depends_on=data.get("depends_on"),
            pattern=data.get("pattern"),
            group=data.get("group", 0),
            template=data.get("template"),
            function=data.get("function", type_str if transform_type == TransformType.CUSTOM else None),
            params=data.get("params"),
        )


@dataclass
class TargetConfig:
    """Configuration for target CDM entity/attribute."""
    entity: str
    attribute: str


@dataclass
class FieldMapping:
    """Complete field mapping specification."""
    # Source
    source: Optional[str] = None
    sources: Optional[List[str]] = None  # For merge operations

    # Target
    target: TargetConfig = None

    # Type
    data_type: DataType = DataType.STRING
    precision: Optional[int] = None
    scale: Optional[int] = None
    date_format: Optional[str] = None
    max_length: Optional[int] = None
    array_type: Optional[DataType] = None

    # Required/nullable
    required: bool = False
    nullable: bool = True

    # Transform
    transform: Optional[TransformConfig] = None

    # Extraction hint
    extract: Optional[ExtractHint] = None

    # Condition
    condition: Optional[str] = None

    # Documentation
    notes: Optional[str] = None

    # Computed at compile time
    _order: int = 0  # Execution order
    _target_column: str = ""  # Spark column name

    def __post_init__(self):
        if self.target:
            self._target_column = f"{self.target.entity}__{self.target.attribute}"

    # Type aliases for common naming variations
    TYPE_ALIASES = {
        "timestamp": "datetime",
        "int": "integer",
        "float": "decimal",
        "double": "decimal",
        "number": "decimal",
        "text": "string",
        "varchar": "string",
        "char": "string",
        "bool": "boolean",
        "json": "object",
        "datetime64": "datetime",
        "date64": "date",
    }

    @classmethod
    def from_dict(cls, data: Dict) -> "FieldMapping":
        """Create from dictionary.

        Supports both formats:
        - Old format: target: {entity: "X", attribute: "Y"}
        - Medallion format: target: "column_name" (string)
        """
        target_data = data.get("target", {})

        # Handle medallion format where target is a simple string
        if isinstance(target_data, str):
            # For medallion format, use "Staging" as entity and the string as attribute
            target = TargetConfig(
                entity="Staging",
                attribute=target_data
            )
        else:
            target = TargetConfig(
                entity=target_data.get("entity", ""),
                attribute=target_data.get("attribute", "")
            )

        transform = None
        if "transform" in data:
            transform = TransformConfig.from_dict(data["transform"])

        extract = None
        if "extract" in data:
            extract = ExtractHint(data["extract"])

        # Normalize type name using aliases
        type_name = data.get("type", "string").lower()
        type_name = cls.TYPE_ALIASES.get(type_name, type_name)

        # Handle array_type if present
        array_type = None
        if "array_type" in data:
            arr_type = data["array_type"].lower()
            arr_type = cls.TYPE_ALIASES.get(arr_type, arr_type)
            array_type = DataType(arr_type)

        return cls(
            source=data.get("source"),
            sources=data.get("sources"),
            target=target,
            data_type=DataType(type_name),
            precision=data.get("precision"),
            scale=data.get("scale"),
            date_format=data.get("date_format"),
            max_length=data.get("max_length"),
            array_type=array_type,
            required=data.get("required", False),
            nullable=data.get("nullable", True),
            transform=transform,
            extract=extract,
            condition=data.get("condition"),
            notes=data.get("notes"),
        )


@dataclass
class EntityExtraction:
    """Configuration for extracting entities from repeating elements."""
    path: str
    entity: str
    key_field: Optional[str] = None
    children: Optional[List["EntityExtraction"]] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "EntityExtraction":
        """Create from dictionary."""
        children = None
        if "children" in data:
            children = [cls.from_dict(c) for c in data["children"]]

        return cls(
            path=data["path"],
            entity=data["entity"],
            key_field=data.get("key_field"),
            children=children,
        )


@dataclass
class EntityFieldMapping:
    """Single field mapping within an entity mapping."""
    source: str
    target: str

    @classmethod
    def from_dict(cls, data: Dict) -> "EntityFieldMapping":
        return cls(source=data["source"], target=data["target"])


@dataclass
class EntityMapping:
    """Configuration for extracting related entities (party, account, FI)."""
    role: str  # debtor, creditor, debtor_agent, etc.
    target_table: str
    fields: List[EntityFieldMapping]
    source_prefix: Optional[str] = None
    dedup_key: Optional[List[str]] = None  # Fields to use for deduplication

    @classmethod
    def from_dict(cls, data: Dict) -> "EntityMapping":
        """Create from dictionary."""
        fields = [EntityFieldMapping.from_dict(f) for f in data.get("fields", [])]
        return cls(
            role=data["role"],
            target_table=data["target_table"],
            fields=fields,
            source_prefix=data.get("source_prefix"),
            dedup_key=data.get("dedup_key"),
        )


@dataclass
class ValidationRule:
    """Validation rule specification."""
    rule: str
    severity: Severity
    message: str
    id: Optional[str] = None
    error_code: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "ValidationRule":
        """Create from dictionary."""
        return cls(
            rule=data["rule"],
            severity=Severity(data["severity"]),
            message=data["message"],
            id=data.get("id"),
            error_code=data.get("error_code"),
        )


@dataclass
class CompletenessRule:
    """Data quality completeness rule."""
    field: str
    weight: float = 1.0


@dataclass
class AccuracyRule:
    """Data quality accuracy rule."""
    field: str
    validation: str


@dataclass
class QualityConfig:
    """Data quality configuration."""
    completeness: List[CompletenessRule] = field(default_factory=list)
    accuracy: List[AccuracyRule] = field(default_factory=list)
    timeliness_field: Optional[str] = None
    max_age_hours: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "QualityConfig":
        """Create from dictionary."""
        completeness = [
            CompletenessRule(field=c["field"], weight=c.get("weight", 1.0))
            for c in data.get("completeness", [])
        ]
        accuracy = [
            AccuracyRule(field=a["field"], validation=a["validation"])
            for a in data.get("accuracy", [])
        ]
        timeliness = data.get("timeliness", {})

        return cls(
            completeness=completeness,
            accuracy=accuracy,
            timeliness_field=timeliness.get("timestamp_field"),
            max_age_hours=timeliness.get("max_age_hours"),
        )


@dataclass
class OptimizationConfig:
    """Performance optimization configuration."""
    partition_filter: Optional[str] = None
    cluster_by: Optional[List[str]] = None
    broadcast_lookups: bool = True
    cache_parsed: bool = False

    @classmethod
    def from_dict(cls, data: Dict) -> "OptimizationConfig":
        """Create from dictionary."""
        return cls(
            partition_filter=data.get("partition_filter"),
            cluster_by=data.get("cluster_by"),
            broadcast_lookups=data.get("broadcast_lookups", True),
            cache_parsed=data.get("cache_parsed", False),
        )


@dataclass
class MappingConfig:
    """Complete mapping configuration."""
    id: str
    name: str
    version: str
    source: SourceConfig
    fields: List[FieldMapping]

    description: Optional[str] = None
    doc_reference: Optional[str] = None
    entity_extraction: Optional[List[EntityExtraction]] = None
    validations: Optional[List[ValidationRule]] = None
    quality: Optional[QualityConfig] = None
    optimization: Optional[OptimizationConfig] = None

    # Entity mappings for normalized CDM tables
    party_mappings: Optional[List[EntityMapping]] = None
    account_mappings: Optional[List[EntityMapping]] = None
    fi_mappings: Optional[List[EntityMapping]] = None

    # Source file path
    _source_path: Optional[Path] = None

    # Medallion metadata
    stage: Optional[str] = None  # "bronze_to_silver" or "silver_to_gold"
    target_table: Optional[str] = None

    def get_entities(self) -> List[str]:
        """Get list of target entities."""
        entities = set()
        for f in self.fields:
            if f.target:
                entities.add(f.target.entity)
        return sorted(entities)

    def get_fields_for_entity(self, entity: str) -> List[FieldMapping]:
        """Get fields for a specific entity."""
        return [f for f in self.fields if f.target and f.target.entity == entity]

    @classmethod
    def from_dict(
        cls,
        data: Dict,
        source_path: Optional[Path] = None,
        stage: str = "bronze_to_silver"
    ) -> "MappingConfig":
        """Create from dictionary (parsed YAML).

        Supports both formats:
        - Old format: mapping.source, mapping.fields at top level
        - Medallion format: mapping.bronze_to_silver or mapping.silver_to_gold sections

        Args:
            data: Parsed YAML dictionary
            source_path: Path to source YAML file
            stage: For medallion format, which stage to use ("bronze_to_silver" or "silver_to_gold")
        """
        mapping = data["mapping"]

        # Detect format: medallion vs old
        is_medallion = "bronze_to_silver" in mapping or "silver_to_gold" in mapping

        if is_medallion:
            return cls._from_medallion_dict(data, source_path, stage)
        else:
            return cls._from_legacy_dict(data, source_path)

    @classmethod
    def _from_medallion_dict(
        cls,
        data: Dict,
        source_path: Optional[Path],
        stage: str
    ) -> "MappingConfig":
        """Parse medallion format YAML."""
        mapping = data["mapping"]

        # Get the stage section
        stage_config = mapping.get(stage)
        if not stage_config:
            raise ValueError(
                f"Stage '{stage}' not found in mapping. "
                f"Available stages: {[k for k in mapping.keys() if k.endswith('_to_silver') or k.endswith('_to_gold')]}"
            )

        source_data = stage_config["source"]

        # Medallion format uses 'format' under source, or derives from parser
        format_value = source_data.get("format", "XML")
        parser = source_data.get("parser", "iso20022")

        source = SourceConfig(
            format=SourceFormat(format_value),
            parser=parser,
            namespace=source_data.get("namespace"),
            root_element=source_data.get("root_element"),
            message_type=source_data.get("message_type"),
            delimiter=source_data.get("delimiter", ","),
            header=source_data.get("header", True),
            record_length=source_data.get("record_length"),
        )

        # Parse fields
        fields = [FieldMapping.from_dict(f) for f in stage_config.get("fields", [])]

        # Parse entity extraction (if present in stage config)
        entity_extraction = None
        if "entity_extraction" in stage_config:
            entity_extraction = [
                EntityExtraction.from_dict(e)
                for e in stage_config["entity_extraction"]
            ]

        # Parse validations (at mapping level for medallion format)
        validations = None
        if "validations" in mapping:
            validations = [
                ValidationRule.from_dict(v)
                for v in mapping["validations"]
            ]

        # Parse quality config
        quality = None
        if "quality" in mapping:
            quality = QualityConfig.from_dict(mapping["quality"])

        # Parse optimization config
        optimization = None
        opt_key = stage.replace("_to_", "_") if stage else None
        if "optimization" in mapping:
            opt_config = mapping["optimization"]
            if opt_key and opt_key in opt_config:
                optimization = OptimizationConfig.from_dict(opt_config[opt_key])

        # Get target table from stage config
        target_data = stage_config.get("target", {})
        target_table = target_data.get("table") if isinstance(target_data, dict) else None

        # Parse entity mappings (party, account, FI) from stage config
        party_mappings = None
        if "party_mappings" in stage_config:
            party_mappings = [
                EntityMapping.from_dict(m) for m in stage_config["party_mappings"]
            ]

        account_mappings = None
        if "account_mappings" in stage_config:
            account_mappings = [
                EntityMapping.from_dict(m) for m in stage_config["account_mappings"]
            ]

        fi_mappings = None
        if "fi_mappings" in stage_config:
            fi_mappings = [
                EntityMapping.from_dict(m) for m in stage_config["fi_mappings"]
            ]

        return cls(
            id=mapping["id"],
            name=mapping["name"],
            version=data.get("version", "1.0"),
            description=mapping.get("description"),
            doc_reference=mapping.get("doc_reference"),
            source=source,
            fields=fields,
            entity_extraction=entity_extraction,
            validations=validations,
            quality=quality,
            optimization=optimization,
            party_mappings=party_mappings,
            account_mappings=account_mappings,
            fi_mappings=fi_mappings,
            _source_path=source_path,
            stage=stage,
            target_table=target_table,
        )

    @classmethod
    def _from_legacy_dict(cls, data: Dict, source_path: Optional[Path]) -> "MappingConfig":
        """Parse legacy format YAML (direct source/fields at mapping level)."""
        mapping = data["mapping"]

        # Parse source config
        source_data = mapping["source"]
        source = SourceConfig(
            format=SourceFormat(source_data["format"]),
            parser=source_data["parser"],
            namespace=source_data.get("namespace"),
            root_element=source_data.get("root_element"),
            message_type=source_data.get("message_type"),
            delimiter=source_data.get("delimiter", ","),
            header=source_data.get("header", True),
            record_length=source_data.get("record_length"),
        )

        # Parse fields
        fields = [FieldMapping.from_dict(f) for f in mapping.get("fields", [])]

        # Parse entity extraction
        entity_extraction = None
        if "entity_extraction" in mapping:
            entity_extraction = [
                EntityExtraction.from_dict(e)
                for e in mapping["entity_extraction"]
            ]

        # Parse validations
        validations = None
        if "validations" in mapping:
            validations = [
                ValidationRule.from_dict(v)
                for v in mapping["validations"]
            ]

        # Parse quality config
        quality = None
        if "quality" in mapping:
            quality = QualityConfig.from_dict(mapping["quality"])

        # Parse optimization config
        optimization = None
        if "optimization" in mapping:
            optimization = OptimizationConfig.from_dict(mapping["optimization"])

        return cls(
            id=mapping["id"],
            name=mapping["name"],
            version=data.get("version", "1.0"),
            description=mapping.get("description"),
            doc_reference=mapping.get("doc_reference"),
            source=source,
            fields=fields,
            entity_extraction=entity_extraction,
            validations=validations,
            quality=quality,
            optimization=optimization,
            _source_path=source_path,
        )
