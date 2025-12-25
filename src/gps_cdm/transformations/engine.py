"""
GPS Payments CDM - Transformation Engine
=========================================

Core transformation engine for converting source messages to CDM
and generating regulatory reports from CDM.

References:
- /documents/mappings/standards/ for payment standard transformations
- /documents/mappings/reports/ for regulatory report generation
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Type, Union
from uuid import UUID, uuid4
import re

from gps_cdm.models.entities.payment import (
    Payment,
    PaymentInstruction,
    CreditTransfer,
    PaymentReturn,
    PaymentReversal,
)
from gps_cdm.models.entities.party import (
    Party,
    PartyIdentification,
    FinancialInstitution,
)
from gps_cdm.models.entities.account import Account
from gps_cdm.models.enums import (
    ChargeBearer,
    PaymentDirection,
    PaymentStatus,
    PaymentType,
    Priority,
    SchemeCode,
)
from gps_cdm.transformations.registry import (
    FieldMapping,
    MappingRegistry,
    MappingType,
    SourceFormat,
    TargetFormat,
)


@dataclass
class TransformationResult:
    """Result of a transformation operation."""
    success: bool
    entities: Dict[str, List[Any]]  # CDM entity name -> list of instances
    errors: List[str]
    warnings: List[str]
    source_format: str
    fields_mapped: int
    fields_failed: int


@dataclass
class ValidationResult:
    """Result of field validation."""
    valid: bool
    errors: List[str]
    warnings: List[str]


class TransformationContext:
    """Context for transformation operations."""

    def __init__(self):
        self.parties: Dict[str, Party] = {}
        self.accounts: Dict[str, Account] = {}
        self.institutions: Dict[str, FinancialInstitution] = {}
        self.payments: List[Payment] = []
        self.instructions: List[PaymentInstruction] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def get_or_create_party(self, key: str, **kwargs) -> Party:
        """Get existing party or create new one."""
        if key not in self.parties:
            self.parties[key] = Party(**kwargs)
        return self.parties[key]

    def get_or_create_institution(self, bic: str, **kwargs) -> FinancialInstitution:
        """Get existing institution or create new one."""
        if bic not in self.institutions:
            self.institutions[bic] = FinancialInstitution(bic=bic, **kwargs)
        return self.institutions[bic]


class BaseParser(ABC):
    """Abstract base class for source format parsers."""

    @abstractmethod
    def parse(self, content: Union[str, bytes, Dict]) -> Dict[str, Any]:
        """Parse source content into intermediate dictionary."""
        pass

    @abstractmethod
    def get_field_value(self, parsed: Dict, path: str) -> Optional[Any]:
        """Extract field value by path from parsed content."""
        pass


class ISO20022Parser(BaseParser):
    """Parser for ISO 20022 XML messages."""

    def __init__(self):
        self._namespaces = {}

    def parse(self, content: Union[str, bytes, Dict]) -> Dict[str, Any]:
        """Parse ISO 20022 XML into dictionary."""
        if isinstance(content, dict):
            return content

        try:
            import xml.etree.ElementTree as ET
            if isinstance(content, bytes):
                content = content.decode('utf-8')

            root = ET.fromstring(content)
            return self._element_to_dict(root)
        except Exception as e:
            raise ValueError(f"Failed to parse ISO 20022 XML: {e}")

    def _element_to_dict(self, element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {}

        # Handle attributes
        if element.attrib:
            for key, value in element.attrib.items():
                result[f"@{key}"] = value

        # Handle children
        children = list(element)
        if children:
            child_dict = {}
            for child in children:
                child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                child_value = self._element_to_dict(child)

                if child_tag in child_dict:
                    # Convert to list for multiple elements
                    if not isinstance(child_dict[child_tag], list):
                        child_dict[child_tag] = [child_dict[child_tag]]
                    child_dict[child_tag].append(child_value)
                else:
                    child_dict[child_tag] = child_value

            result.update(child_dict)
        elif element.text and element.text.strip():
            result["_text"] = element.text.strip()

        return result if len(result) > 1 or "_text" not in result else result.get("_text", result)

    def get_field_value(self, parsed: Dict, path: str) -> Optional[Any]:
        """Extract field value by XPath-like path."""
        parts = path.split('/')
        current = parsed

        for part in parts:
            if current is None:
                return None

            # Handle attribute access
            if part.startswith('@'):
                return current.get(part) if isinstance(current, dict) else None

            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and len(current) > 0:
                current = current[0].get(part) if isinstance(current[0], dict) else None
            else:
                return None

        # Return text value if it's a simple element
        if isinstance(current, dict) and "_text" in current:
            return current["_text"]
        return current


class SWIFTMTParser(BaseParser):
    """Parser for SWIFT MT messages."""

    # MT103 field patterns
    MT_PATTERNS = {
        "20": r":20:(.+)",
        "21": r":21:(.+)",
        "32A": r":32A:(\d{6})([A-Z]{3})(\d+[,.]?\d*)",
        "50K": r":50K:(.+?)(?=:\d{2}[A-Z]?:|$)",
        "52A": r":52A:(.+)",
        "57A": r":57A:(.+)",
        "59": r":59:(.+?)(?=:\d{2}[A-Z]?:|$)",
        "71A": r":71A:(.+)",
        "121": r"\{121:([A-Fa-f0-9\-]+)\}",
    }

    def parse(self, content: Union[str, bytes, Dict]) -> Dict[str, Any]:
        """Parse SWIFT MT message into dictionary."""
        if isinstance(content, dict):
            return content

        if isinstance(content, bytes):
            content = content.decode('utf-8')

        result = {}
        for field_tag, pattern in self.MT_PATTERNS.items():
            match = re.search(pattern, content, re.DOTALL)
            if match:
                if field_tag == "32A":
                    result[field_tag] = {
                        "date": match.group(1),
                        "currency": match.group(2),
                        "amount": match.group(3).replace(',', '.')
                    }
                else:
                    result[field_tag] = match.group(1).strip()

        return result

    def get_field_value(self, parsed: Dict, path: str) -> Optional[Any]:
        """Extract field value by field tag."""
        return parsed.get(path)


class TransformationEngine:
    """
    Core transformation engine.

    Transforms source payment messages to CDM entities and
    generates regulatory reports from CDM data.

    Usage:
        engine = TransformationEngine()

        # Transform ISO 20022 pain.001 to CDM
        result = engine.transform_to_cdm(
            content=xml_content,
            source_format=SourceFormat.ISO20022_PAIN_001
        )

        # Generate FinCEN CTR from CDM
        ctr_xml = engine.generate_report(
            cdm_entities=result.entities,
            target_format=TargetFormat.FINCEN_CTR
        )
    """

    def __init__(self, registry: Optional[MappingRegistry] = None):
        self.registry = registry or MappingRegistry()
        self._parsers: Dict[str, BaseParser] = {
            "iso20022": ISO20022Parser(),
            "swift_mt": SWIFTMTParser(),
        }
        self._transformers: Dict[str, Callable] = self._register_transformers()

    def _register_transformers(self) -> Dict[str, Callable]:
        """Register field transformation functions."""
        return {
            "map_priority_code": self._map_priority,
            "map_charge_bearer": self._map_charge_bearer,
            "map_mt103_charges": self._map_mt103_charges,
            "parse_mt103_32a": self._parse_mt103_32a,
            "parse_mt103_party": self._parse_mt103_party,
            "map_fincen_regulator_code": self._map_fincen_regulator,
            "map_fincen_id_type": self._map_fincen_id_type,
            "format_address_line": self._format_address,
            "if_cash_in": self._if_cash_in,
        }

    def transform_to_cdm(
        self,
        content: Union[str, bytes, Dict],
        source_format: SourceFormat,
        validate: bool = True
    ) -> TransformationResult:
        """
        Transform source message to CDM entities.

        Args:
            content: Source message content (XML, MT text, or pre-parsed dict)
            source_format: Source format identifier
            validate: Whether to validate output

        Returns:
            TransformationResult with CDM entities
        """
        context = TransformationContext()
        fields_mapped = 0
        fields_failed = 0

        # Get mapping specification
        mapping_spec = self.registry.get_mapping(source_format)
        if not mapping_spec:
            return TransformationResult(
                success=False,
                entities={},
                errors=[f"No mapping found for source format: {source_format}"],
                warnings=[],
                source_format=source_format.value,
                fields_mapped=0,
                fields_failed=0
            )

        # Select parser
        parser = self._get_parser(source_format)
        if not parser:
            return TransformationResult(
                success=False,
                entities={},
                errors=[f"No parser available for source format: {source_format}"],
                warnings=[],
                source_format=source_format.value,
                fields_mapped=0,
                fields_failed=0
            )

        # Parse content
        try:
            parsed = parser.parse(content)
        except Exception as e:
            return TransformationResult(
                success=False,
                entities={},
                errors=[f"Failed to parse content: {e}"],
                warnings=[],
                source_format=source_format.value,
                fields_mapped=0,
                fields_failed=0
            )

        # Create core entities
        payment = Payment(
            payment_type=self._determine_payment_type(source_format),
            scheme_code=self._determine_scheme(source_format),
            status=PaymentStatus.INITIATED,
        )
        instruction = PaymentInstruction(payment_id=payment.payment_id)

        # Apply field mappings
        for field_mapping in mapping_spec.field_mappings:
            try:
                value = parser.get_field_value(parsed, field_mapping.source_path)
                if value is not None:
                    self._apply_mapping(
                        context, payment, instruction,
                        field_mapping, value
                    )
                    fields_mapped += 1
                elif not field_mapping.nullable:
                    context.errors.append(
                        f"Required field missing: {field_mapping.source_path}"
                    )
                    fields_failed += 1
            except Exception as e:
                context.errors.append(
                    f"Error mapping {field_mapping.source_path}: {e}"
                )
                fields_failed += 1

        context.payments.append(payment)
        context.instructions.append(instruction)

        # Validate if requested
        if validate:
            validation = self._validate_output(context)
            context.warnings.extend(validation.warnings)
            if not validation.valid:
                context.errors.extend(validation.errors)

        return TransformationResult(
            success=len(context.errors) == 0,
            entities={
                "Payment": context.payments,
                "PaymentInstruction": context.instructions,
                "Party": list(context.parties.values()),
                "FinancialInstitution": list(context.institutions.values()),
                "Account": list(context.accounts.values()),
            },
            errors=context.errors,
            warnings=context.warnings,
            source_format=source_format.value,
            fields_mapped=fields_mapped,
            fields_failed=fields_failed
        )

    def generate_report(
        self,
        cdm_entities: Dict[str, List[Any]],
        target_format: TargetFormat,
        report_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Generate regulatory report from CDM entities.

        Args:
            cdm_entities: Dictionary of CDM entity lists
            target_format: Target report format
            report_date: Report filing date

        Returns:
            Report data structure ready for serialization
        """
        mapping_spec = self.registry.get_report_mapping(target_format)
        if not mapping_spec:
            raise ValueError(f"No mapping found for report format: {target_format}")

        report_data = {
            "report_type": target_format.value,
            "report_date": (report_date or date.today()).isoformat(),
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Apply report field mappings
        for field_mapping in mapping_spec.field_mappings:
            entity_name = field_mapping.cdm_entity
            entities = cdm_entities.get(entity_name, [])

            if entities:
                value = self._extract_cdm_value(
                    entities[0],
                    field_mapping.cdm_attribute
                )
                if value is not None:
                    report_data[field_mapping.source_field_name] = value

        return report_data

    def _get_parser(self, source_format: SourceFormat) -> Optional[BaseParser]:
        """Get appropriate parser for source format."""
        if source_format.value.startswith(("pain.", "pacs.", "camt.")):
            return self._parsers["iso20022"]
        elif source_format.value.startswith("MT"):
            return self._parsers["swift_mt"]
        else:
            return self._parsers.get("iso20022")  # Default

    def _determine_payment_type(self, source_format: SourceFormat) -> PaymentType:
        """Determine payment type from source format."""
        format_map = {
            SourceFormat.ISO20022_PAIN_001: PaymentType.CREDIT_TRANSFER,
            SourceFormat.ISO20022_PAIN_008: PaymentType.DIRECT_DEBIT,
            SourceFormat.ISO20022_PACS_008: PaymentType.CREDIT_TRANSFER,
            SourceFormat.ISO20022_PACS_003: PaymentType.DIRECT_DEBIT,
            SourceFormat.ISO20022_PACS_004: PaymentType.RETURN,
            SourceFormat.ISO20022_PACS_007: PaymentType.REVERSAL,
            SourceFormat.SWIFT_MT103: PaymentType.CREDIT_TRANSFER,
            SourceFormat.SWIFT_MT202: PaymentType.CREDIT_TRANSFER,
        }
        return format_map.get(source_format, PaymentType.CREDIT_TRANSFER)

    def _determine_scheme(self, source_format: SourceFormat) -> SchemeCode:
        """Determine payment scheme from source format."""
        if source_format.value.startswith("MT"):
            return SchemeCode.SWIFT
        elif source_format == SourceFormat.FEDWIRE:
            return SchemeCode.FEDWIRE
        elif source_format == SourceFormat.NACHA_ACH:
            return SchemeCode.ACH
        elif source_format.value.startswith("SEPA"):
            return SchemeCode.SEPA
        elif source_format == SourceFormat.PIX:
            return SchemeCode.PIX
        elif source_format == SourceFormat.UPI:
            return SchemeCode.UPI
        else:
            return SchemeCode.ISO20022

    def _apply_mapping(
        self,
        context: TransformationContext,
        payment: Payment,
        instruction: PaymentInstruction,
        field_mapping: FieldMapping,
        value: Any
    ) -> None:
        """Apply a single field mapping."""
        # Transform value if needed
        if field_mapping.mapping_type == MappingType.LOOKUP:
            transformer = self._transformers.get(field_mapping.transformation_logic)
            if transformer:
                value = transformer(value)
        elif field_mapping.mapping_type == MappingType.DERIVED:
            transformer = self._transformers.get(field_mapping.transformation_logic)
            if transformer:
                value = transformer(value)

        # Apply to target entity
        entity = field_mapping.cdm_entity
        attribute = field_mapping.cdm_attribute

        if entity == "Payment":
            if hasattr(payment, attribute):
                setattr(payment, attribute, value)
        elif entity == "PaymentInstruction":
            if hasattr(instruction, attribute):
                setattr(instruction, attribute, value)
        elif entity == "Party":
            # Create/update party based on context (debtor/creditor)
            party_key = f"party_{len(context.parties)}"
            party = context.get_or_create_party(party_key)
            if hasattr(party, attribute):
                setattr(party, attribute, value)
        elif entity == "FinancialInstitution":
            if attribute == "bic" and value:
                context.get_or_create_institution(value)
        elif entity == "Account":
            account_key = f"account_{len(context.accounts)}"
            if account_key not in context.accounts:
                context.accounts[account_key] = Account()
            if hasattr(context.accounts[account_key], attribute):
                setattr(context.accounts[account_key], attribute, value)

    def _extract_cdm_value(self, entity: Any, attribute: str) -> Optional[Any]:
        """Extract value from CDM entity."""
        if hasattr(entity, attribute):
            value = getattr(entity, attribute)
            # Convert special types
            if isinstance(value, (UUID, Decimal)):
                return str(value)
            elif isinstance(value, (date, datetime)):
                return value.isoformat()
            elif hasattr(value, 'value'):  # Enum
                return value.value
            return value
        return None

    def _validate_output(self, context: TransformationContext) -> ValidationResult:
        """Validate transformed output."""
        errors = []
        warnings = []

        for payment in context.payments:
            if not payment.payment_id:
                errors.append("Payment missing payment_id")

        for instruction in context.instructions:
            if instruction.instructed_amount <= 0:
                warnings.append("Instructed amount is zero or negative")
            if not instruction.instructed_currency:
                warnings.append("Missing instructed currency")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    # Transformer functions
    def _map_priority(self, value: str) -> Priority:
        """Map priority code to CDM enum."""
        mapping = {
            "HIGH": Priority.HIGH,
            "NORM": Priority.NORM,
            "URGN": Priority.URGP,
        }
        return mapping.get(value, Priority.NORM)

    def _map_charge_bearer(self, value: str) -> ChargeBearer:
        """Map charge bearer code to CDM enum."""
        mapping = {
            "DEBT": ChargeBearer.DEBT,
            "CRED": ChargeBearer.CRED,
            "SHAR": ChargeBearer.SHAR,
            "SLEV": ChargeBearer.SLEV,
        }
        return mapping.get(value, ChargeBearer.SHAR)

    def _map_mt103_charges(self, value: str) -> ChargeBearer:
        """Map MT103 charges code to CDM enum."""
        mapping = {
            "BEN": ChargeBearer.CRED,
            "OUR": ChargeBearer.DEBT,
            "SHA": ChargeBearer.SHAR,
        }
        return mapping.get(value, ChargeBearer.SHAR)

    def _parse_mt103_32a(self, value: Dict) -> Decimal:
        """Parse MT103 field 32A composite value."""
        if isinstance(value, dict):
            return Decimal(value.get("amount", "0"))
        return Decimal("0")

    def _parse_mt103_party(self, value: str) -> str:
        """Parse MT103 party field to extract name."""
        if isinstance(value, str):
            lines = value.strip().split('\n')
            # First line after account is usually name
            for line in lines:
                if line and not line.startswith('/'):
                    return line.strip()
        return value

    def _map_fincen_regulator(self, value: str) -> str:
        """Map regulator to FinCEN code."""
        mapping = {
            "OCC": "1",
            "FDIC": "2",
            "FRB": "3",
            "NCUA": "4",
            "IRS": "6",
            "SEC": "7",
        }
        return mapping.get(value, "5")  # 5 = None

    def _map_fincen_id_type(self, value: str) -> str:
        """Map ID type to FinCEN code."""
        mapping = {
            "DRIVERS_LICENSE": "1",
            "PASSPORT": "2",
            "ALIEN_REGISTRATION": "3",
            "STATE_ID": "5",
            "MILITARY_ID": "6",
        }
        return mapping.get(value, "99")  # 99 = Other

    def _format_address(self, value: Any) -> str:
        """Format address object to string."""
        if isinstance(value, dict):
            parts = [
                value.get("address_line_1", ""),
                value.get("city", ""),
                value.get("state", ""),
                value.get("postal_code", ""),
            ]
            return ", ".join(p for p in parts if p)
        return str(value) if value else ""

    def _if_cash_in(self, value: Any) -> Optional[Decimal]:
        """Return value only if cash-in transaction."""
        # Logic would check transaction type
        return value if isinstance(value, Decimal) else None
