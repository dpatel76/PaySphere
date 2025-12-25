"""
GPS Payments CDM - Mapping Registry
====================================

Machine-readable registry of field mappings from source formats to CDM.
References comprehensive mapping documents in /documents/mappings/.

The mapping documents contain detailed field-by-field mappings:
- standards/: ISO 20022, SWIFT MT, regional payment systems
- reports/: FinCEN, AUSTRAC, FINTRAC, FATCA, CRS, etc.

Note: CDM attribute names may differ slightly from mapping documents.
This registry provides the canonical CDM attribute references.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
import yaml


class MappingType(str, Enum):
    """Type of field mapping."""
    DIRECT = "DIRECT"           # 1:1 mapping
    DERIVED = "DERIVED"         # Calculated/transformed
    LOOKUP = "LOOKUP"           # Reference data lookup
    AGGREGATED = "AGGREGATED"   # Aggregation of multiple fields
    CONDITIONAL = "CONDITIONAL" # Conditional logic
    CONSTANT = "CONSTANT"       # Fixed value
    SPLIT = "SPLIT"             # One source to multiple targets
    MERGE = "MERGE"             # Multiple sources to one target


class SourceFormat(str, Enum):
    """Supported source message formats."""
    # ISO 20022
    ISO20022_PAIN_001 = "pain.001"
    ISO20022_PAIN_002 = "pain.002"
    ISO20022_PAIN_007 = "pain.007"
    ISO20022_PAIN_008 = "pain.008"
    ISO20022_PACS_002 = "pacs.002"
    ISO20022_PACS_003 = "pacs.003"
    ISO20022_PACS_004 = "pacs.004"
    ISO20022_PACS_007 = "pacs.007"
    ISO20022_PACS_008 = "pacs.008"
    ISO20022_PACS_009 = "pacs.009"
    ISO20022_PACS_028 = "pacs.028"
    ISO20022_CAMT_052 = "camt.052"
    ISO20022_CAMT_053 = "camt.053"
    ISO20022_CAMT_054 = "camt.054"
    ISO20022_CAMT_055 = "camt.055"
    ISO20022_CAMT_056 = "camt.056"

    # SWIFT MT
    SWIFT_MT103 = "MT103"
    SWIFT_MT103_STP = "MT103+"
    SWIFT_MT202 = "MT202"
    SWIFT_MT202COV = "MT202COV"
    SWIFT_MT950 = "MT950"

    # Regional
    FEDWIRE = "FEDWIRE"
    NACHA_ACH = "NACHA_ACH"
    CHIPS = "CHIPS"
    RTP = "RTP"
    SEPA_SCT = "SEPA_SCT"
    SEPA_SDD = "SEPA_SDD"
    PIX = "PIX"
    UPI = "UPI"
    NPP = "NPP"
    FASTER_PAYMENTS = "FASTER_PAYMENTS"


class TargetFormat(str, Enum):
    """Supported target/output formats."""
    CDM = "CDM"
    # Regulatory Reports
    FINCEN_CTR = "FINCEN_CTR"
    FINCEN_SAR = "FINCEN_SAR"
    FINCEN_FBAR = "FINCEN_FBAR"
    AUSTRAC_IFTI = "AUSTRAC_IFTI"
    AUSTRAC_TTR = "AUSTRAC_TTR"
    AUSTRAC_SMR = "AUSTRAC_SMR"
    FINTRAC_LCTR = "FINTRAC_LCTR"
    FINTRAC_STR = "FINTRAC_STR"
    FINTRAC_EFTR = "FINTRAC_EFTR"
    FATCA_8966 = "FATCA_8966"
    OECD_CRS = "OECD_CRS"
    JFIU_STR = "JFIU_STR"
    STRO_STR = "STRO_STR"
    JAFIC_STR = "JAFIC_STR"
    UK_SAR = "UK_SAR"


@dataclass
class FieldMapping:
    """Individual field mapping specification."""
    source_path: str                    # XPath or field path in source
    source_field_name: str              # Human-readable field name
    source_type: str                    # Data type in source
    cdm_entity: str                     # Target CDM entity
    cdm_attribute: str                  # Target CDM attribute
    mapping_type: MappingType = MappingType.DIRECT
    transformation_logic: Optional[str] = None  # Transformation expression
    validation_rule: Optional[str] = None
    default_value: Optional[Any] = None
    nullable: bool = True
    cardinality: str = "1..1"           # 0..1, 1..1, 0..n, 1..n
    notes: Optional[str] = None


@dataclass
class MappingSpec:
    """Complete mapping specification for a source format."""
    source_format: SourceFormat
    source_version: str
    description: str
    document_reference: str             # Path to detailed mapping doc
    total_fields: int
    field_mappings: List[FieldMapping] = field(default_factory=list)

    # Coverage statistics
    direct_mappings: int = 0
    derived_mappings: int = 0
    lookup_mappings: int = 0

    def coverage_percentage(self) -> float:
        """Calculate mapping coverage."""
        if self.total_fields == 0:
            return 0.0
        return len(self.field_mappings) / self.total_fields * 100


class MappingRegistry:
    """
    Central registry for all field mappings.

    References the comprehensive mapping documents in /documents/mappings/
    and provides programmatic access for transformation operations.

    Usage:
        registry = MappingRegistry()
        registry.load_from_yaml("/path/to/mappings.yaml")

        # Get mapping for pain.001 to CDM
        mapping = registry.get_mapping(SourceFormat.ISO20022_PAIN_001)

        # Get field mapping for specific path
        field = registry.get_field_mapping("pain.001", "GrpHdr/MsgId")
    """

    # Reference to mapping documents directory
    MAPPING_DOCS_PATH = Path(__file__).parent.parent.parent.parent.parent / "documents" / "mappings"

    def __init__(self):
        self._mappings: Dict[SourceFormat, MappingSpec] = {}
        self._report_mappings: Dict[TargetFormat, MappingSpec] = {}
        self._initialize_core_mappings()

    def _initialize_core_mappings(self):
        """Initialize core mappings based on /documents/mappings/ reference."""
        # ISO 20022 pain.001 - Customer Credit Transfer
        # Full mapping in: documents/mappings/standards/ISO20022_pain001_CustomerCreditTransfer_Mapping.md
        self._mappings[SourceFormat.ISO20022_PAIN_001] = MappingSpec(
            source_format=SourceFormat.ISO20022_PAIN_001,
            source_version="pain.001.001.11",
            description="Customer Credit Transfer Initiation",
            document_reference="standards/ISO20022_pain001_CustomerCreditTransfer_Mapping.md",
            total_fields=156,
            direct_mappings=142,
            derived_mappings=8,
            lookup_mappings=6,
            field_mappings=self._get_pain001_mappings()
        )

        # ISO 20022 pacs.008 - FI Credit Transfer
        # Full mapping in: documents/mappings/standards/ISO20022_pacs008_FICreditTransfer_Mapping.md
        self._mappings[SourceFormat.ISO20022_PACS_008] = MappingSpec(
            source_format=SourceFormat.ISO20022_PACS_008,
            source_version="pacs.008.001.10",
            description="FI to FI Customer Credit Transfer",
            document_reference="standards/ISO20022_pacs008_FICreditTransfer_Mapping.md",
            total_fields=142,
            direct_mappings=128,
            derived_mappings=8,
            lookup_mappings=6,
            field_mappings=self._get_pacs008_mappings()
        )

        # SWIFT MT103
        # Full mapping in: documents/mappings/standards/SWIFT_MT103_SingleCustomerCreditTransfer_Mapping.md
        self._mappings[SourceFormat.SWIFT_MT103] = MappingSpec(
            source_format=SourceFormat.SWIFT_MT103,
            source_version="2023",
            description="Single Customer Credit Transfer",
            document_reference="standards/SWIFT_MT103_SingleCustomerCreditTransfer_Mapping.md",
            total_fields=58,
            direct_mappings=52,
            derived_mappings=4,
            lookup_mappings=2,
            field_mappings=self._get_mt103_mappings()
        )

        # Initialize report mappings
        self._initialize_report_mappings()

    def _initialize_report_mappings(self):
        """Initialize regulatory report mappings."""
        # FinCEN CTR
        # Full mapping in: documents/mappings/reports/FinCEN_CTR_CurrencyTransactionReport_Mapping.md
        self._report_mappings[TargetFormat.FINCEN_CTR] = MappingSpec(
            source_format=SourceFormat.ISO20022_PAIN_001,  # CDM as source
            source_version="1.0",
            description="Currency Transaction Report (Form 112)",
            document_reference="reports/FinCEN_CTR_CurrencyTransactionReport_Mapping.md",
            total_fields=117,
            direct_mappings=95,
            derived_mappings=12,
            lookup_mappings=10,
            field_mappings=self._get_ctr_mappings()
        )

        # FinCEN SAR
        # Full mapping in: documents/mappings/reports/FinCEN_SAR_SuspiciousActivityReport_Mapping.md
        self._report_mappings[TargetFormat.FINCEN_SAR] = MappingSpec(
            source_format=SourceFormat.ISO20022_PAIN_001,
            source_version="1.0",
            description="Suspicious Activity Report (Form 111)",
            document_reference="reports/FinCEN_SAR_SuspiciousActivityReport_Mapping.md",
            total_fields=184,
            direct_mappings=156,
            derived_mappings=18,
            lookup_mappings=10,
            field_mappings=[]  # Detailed in document
        )

        # AUSTRAC IFTI
        # Full mapping in: documents/mappings/reports/AUSTRAC_IFTI_InternationalFundsTransfer_Mapping.md
        self._report_mappings[TargetFormat.AUSTRAC_IFTI] = MappingSpec(
            source_format=SourceFormat.ISO20022_PAIN_001,
            source_version="1.0",
            description="International Funds Transfer Instruction",
            document_reference="reports/AUSTRAC_IFTI_InternationalFundsTransfer_Mapping.md",
            total_fields=87,
            direct_mappings=74,
            derived_mappings=8,
            lookup_mappings=5,
            field_mappings=[]  # Detailed in document
        )

    def _get_pain001_mappings(self) -> List[FieldMapping]:
        """Core pain.001 field mappings to CDM."""
        return [
            # Group Header
            FieldMapping(
                source_path="GrpHdr/MsgId",
                source_field_name="Message Identification",
                source_type="Text",
                cdm_entity="PaymentInstruction",
                cdm_attribute="end_to_end_id",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="GrpHdr/CreDtTm",
                source_field_name="Creation Date Time",
                source_type="DateTime",
                cdm_entity="Payment",
                cdm_attribute="created_at",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="GrpHdr/InitgPty/Nm",
                source_field_name="Initiating Party Name",
                source_type="Text",
                cdm_entity="Party",
                cdm_attribute="name",
                mapping_type=MappingType.DIRECT
            ),
            # Payment Info
            FieldMapping(
                source_path="PmtInf/PmtInfId",
                source_field_name="Payment Information ID",
                source_type="Text",
                cdm_entity="PaymentInstruction",
                cdm_attribute="instruction_id_ext",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="PmtInf/PmtTpInf/InstrPrty",
                source_field_name="Instruction Priority",
                source_type="Code",
                cdm_entity="Payment",
                cdm_attribute="priority",
                mapping_type=MappingType.LOOKUP,
                transformation_logic="map_priority_code"
            ),
            FieldMapping(
                source_path="PmtInf/ReqdExctnDt/Dt",
                source_field_name="Requested Execution Date",
                source_type="Date",
                cdm_entity="PaymentInstruction",
                cdm_attribute="requested_execution_date",
                mapping_type=MappingType.DIRECT
            ),
            # Debtor
            FieldMapping(
                source_path="PmtInf/Dbtr/Nm",
                source_field_name="Debtor Name",
                source_type="Text",
                cdm_entity="Party",
                cdm_attribute="name",
                mapping_type=MappingType.DIRECT,
                notes="Links to debtor_id in PaymentInstruction"
            ),
            FieldMapping(
                source_path="PmtInf/DbtrAcct/Id/IBAN",
                source_field_name="Debtor Account IBAN",
                source_type="Code",
                cdm_entity="Account",
                cdm_attribute="iban",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="PmtInf/DbtrAgt/FinInstnId/BICFI",
                source_field_name="Debtor Agent BIC",
                source_type="Code",
                cdm_entity="FinancialInstitution",
                cdm_attribute="bic",
                mapping_type=MappingType.DIRECT
            ),
            # Transaction
            FieldMapping(
                source_path="CdtTrfTxInf/PmtId/EndToEndId",
                source_field_name="End to End ID",
                source_type="Text",
                cdm_entity="PaymentInstruction",
                cdm_attribute="end_to_end_id",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="CdtTrfTxInf/PmtId/UETR",
                source_field_name="UETR",
                source_type="UUID",
                cdm_entity="PaymentInstruction",
                cdm_attribute="uetr",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="CdtTrfTxInf/Amt/InstdAmt",
                source_field_name="Instructed Amount",
                source_type="Decimal",
                cdm_entity="PaymentInstruction",
                cdm_attribute="instructed_amount",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="CdtTrfTxInf/Amt/InstdAmt/@Ccy",
                source_field_name="Instructed Currency",
                source_type="Code",
                cdm_entity="PaymentInstruction",
                cdm_attribute="instructed_currency",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="CdtTrfTxInf/ChrgBr",
                source_field_name="Charge Bearer",
                source_type="Code",
                cdm_entity="PaymentInstruction",
                cdm_attribute="charge_bearer",
                mapping_type=MappingType.LOOKUP,
                transformation_logic="map_charge_bearer"
            ),
            # Creditor
            FieldMapping(
                source_path="CdtTrfTxInf/Cdtr/Nm",
                source_field_name="Creditor Name",
                source_type="Text",
                cdm_entity="Party",
                cdm_attribute="name",
                mapping_type=MappingType.DIRECT,
                notes="Links to creditor_id in PaymentInstruction"
            ),
            FieldMapping(
                source_path="CdtTrfTxInf/CdtrAcct/Id/IBAN",
                source_field_name="Creditor Account IBAN",
                source_type="Code",
                cdm_entity="Account",
                cdm_attribute="iban",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI",
                source_field_name="Creditor Agent BIC",
                source_type="Code",
                cdm_entity="FinancialInstitution",
                cdm_attribute="bic",
                mapping_type=MappingType.DIRECT
            ),
        ]

    def _get_pacs008_mappings(self) -> List[FieldMapping]:
        """Core pacs.008 field mappings to CDM."""
        return [
            FieldMapping(
                source_path="GrpHdr/MsgId",
                source_field_name="Message Identification",
                source_type="Text",
                cdm_entity="PaymentInstruction",
                cdm_attribute="transaction_id",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="GrpHdr/CreDtTm",
                source_field_name="Creation Date Time",
                source_type="DateTime",
                cdm_entity="Payment",
                cdm_attribute="created_at",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="CdtTrfTxInf/PmtId/InstrId",
                source_field_name="Instruction ID",
                source_type="Text",
                cdm_entity="PaymentInstruction",
                cdm_attribute="instruction_id_ext",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="CdtTrfTxInf/PmtId/EndToEndId",
                source_field_name="End to End ID",
                source_type="Text",
                cdm_entity="PaymentInstruction",
                cdm_attribute="end_to_end_id",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="CdtTrfTxInf/PmtId/UETR",
                source_field_name="UETR",
                source_type="UUID",
                cdm_entity="PaymentInstruction",
                cdm_attribute="uetr",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="CdtTrfTxInf/IntrBkSttlmAmt",
                source_field_name="Interbank Settlement Amount",
                source_type="Decimal",
                cdm_entity="PaymentInstruction",
                cdm_attribute="interbank_settlement_amount",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="CdtTrfTxInf/IntrBkSttlmDt",
                source_field_name="Interbank Settlement Date",
                source_type="Date",
                cdm_entity="PaymentInstruction",
                cdm_attribute="settlement_date",
                mapping_type=MappingType.DIRECT
            ),
        ]

    def _get_mt103_mappings(self) -> List[FieldMapping]:
        """Core MT103 field mappings to CDM."""
        return [
            FieldMapping(
                source_path="20",
                source_field_name="Transaction Reference Number",
                source_type="Text",
                cdm_entity="PaymentInstruction",
                cdm_attribute="transaction_id",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="21",
                source_field_name="Related Reference",
                source_type="Text",
                cdm_entity="PaymentInstruction",
                cdm_attribute="end_to_end_id",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="32A",
                source_field_name="Value Date/Currency/Amount",
                source_type="Composite",
                cdm_entity="PaymentInstruction",
                cdm_attribute="instructed_amount",
                mapping_type=MappingType.DERIVED,
                transformation_logic="parse_mt103_32a"
            ),
            FieldMapping(
                source_path="50K",
                source_field_name="Ordering Customer",
                source_type="Text",
                cdm_entity="Party",
                cdm_attribute="name",
                mapping_type=MappingType.DERIVED,
                transformation_logic="parse_mt103_party",
                notes="Debtor party"
            ),
            FieldMapping(
                source_path="52A",
                source_field_name="Ordering Institution",
                source_type="Text",
                cdm_entity="FinancialInstitution",
                cdm_attribute="bic",
                mapping_type=MappingType.DIRECT,
                notes="Debtor agent"
            ),
            FieldMapping(
                source_path="59",
                source_field_name="Beneficiary Customer",
                source_type="Text",
                cdm_entity="Party",
                cdm_attribute="name",
                mapping_type=MappingType.DERIVED,
                transformation_logic="parse_mt103_party",
                notes="Creditor party"
            ),
            FieldMapping(
                source_path="57A",
                source_field_name="Account With Institution",
                source_type="Text",
                cdm_entity="FinancialInstitution",
                cdm_attribute="bic",
                mapping_type=MappingType.DIRECT,
                notes="Creditor agent"
            ),
            FieldMapping(
                source_path="71A",
                source_field_name="Details of Charges",
                source_type="Code",
                cdm_entity="PaymentInstruction",
                cdm_attribute="charge_bearer",
                mapping_type=MappingType.LOOKUP,
                transformation_logic="map_mt103_charges"
            ),
            FieldMapping(
                source_path="121",
                source_field_name="UETR",
                source_type="UUID",
                cdm_entity="PaymentInstruction",
                cdm_attribute="uetr",
                mapping_type=MappingType.DIRECT
            ),
        ]

    def _get_ctr_mappings(self) -> List[FieldMapping]:
        """CDM to FinCEN CTR field mappings."""
        return [
            # Filing Institution
            FieldMapping(
                source_path="FinancialInstitution.primary_regulator",
                source_field_name="Federal Regulator",
                source_type="Code",
                cdm_entity="FinancialInstitution",
                cdm_attribute="primary_regulator",
                mapping_type=MappingType.LOOKUP,
                transformation_logic="map_fincen_regulator_code"
            ),
            FieldMapping(
                source_path="FinancialInstitution.institution_name",
                source_field_name="Legal Name",
                source_type="Text",
                cdm_entity="FinancialInstitution",
                cdm_attribute="institution_name",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="FinancialInstitution.tin_value",
                source_field_name="TIN",
                source_type="Text",
                cdm_entity="FinancialInstitution",
                cdm_attribute="tin_value",
                mapping_type=MappingType.DIRECT
            ),
            # Person
            FieldMapping(
                source_path="Party.family_name",
                source_field_name="Last Name / Entity Name",
                source_type="Text",
                cdm_entity="Party",
                cdm_attribute="family_name",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="Party.given_name",
                source_field_name="First Name",
                source_type="Text",
                cdm_entity="Party",
                cdm_attribute="given_name",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="Party.tax_id",
                source_field_name="TIN",
                source_type="Text",
                cdm_entity="Party",
                cdm_attribute="tax_id",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="Party.date_of_birth",
                source_field_name="Date of Birth",
                source_type="Date",
                cdm_entity="Party",
                cdm_attribute="date_of_birth",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="Party.address.address_line_1",
                source_field_name="Address",
                source_type="Text",
                cdm_entity="Party",
                cdm_attribute="address",
                mapping_type=MappingType.DERIVED,
                transformation_logic="format_address_line"
            ),
            FieldMapping(
                source_path="Party.occupation",
                source_field_name="Occupation",
                source_type="Text",
                cdm_entity="Party",
                cdm_attribute="occupation",
                mapping_type=MappingType.DIRECT
            ),
            FieldMapping(
                source_path="Party.form_of_identification",
                source_field_name="Form of ID",
                source_type="Code",
                cdm_entity="Party",
                cdm_attribute="form_of_identification",
                mapping_type=MappingType.LOOKUP,
                transformation_logic="map_fincen_id_type"
            ),
            # Transaction
            FieldMapping(
                source_path="PaymentInstruction.instructed_amount",
                source_field_name="Cash In Amount",
                source_type="Decimal",
                cdm_entity="PaymentInstruction",
                cdm_attribute="instructed_amount",
                mapping_type=MappingType.CONDITIONAL,
                transformation_logic="if_cash_in"
            ),
        ]

    def get_mapping(self, source_format: SourceFormat) -> Optional[MappingSpec]:
        """Get mapping specification for a source format."""
        return self._mappings.get(source_format)

    def get_report_mapping(self, target_format: TargetFormat) -> Optional[MappingSpec]:
        """Get mapping specification for generating a regulatory report."""
        return self._report_mappings.get(target_format)

    def get_field_mapping(
        self,
        source_format: Union[str, SourceFormat],
        source_path: str
    ) -> Optional[FieldMapping]:
        """Get specific field mapping by source path."""
        if isinstance(source_format, str):
            try:
                source_format = SourceFormat(source_format)
            except ValueError:
                return None

        mapping_spec = self._mappings.get(source_format)
        if not mapping_spec:
            return None

        for field_mapping in mapping_spec.field_mappings:
            if field_mapping.source_path == source_path:
                return field_mapping
        return None

    def get_all_mappings_for_entity(self, cdm_entity: str) -> List[FieldMapping]:
        """Get all field mappings that target a specific CDM entity."""
        result = []
        for mapping_spec in self._mappings.values():
            for field_mapping in mapping_spec.field_mappings:
                if field_mapping.cdm_entity == cdm_entity:
                    result.append(field_mapping)
        return result

    def get_mapping_document_path(self, source_format: SourceFormat) -> Optional[Path]:
        """Get path to detailed mapping document."""
        mapping_spec = self._mappings.get(source_format)
        if mapping_spec:
            return self.MAPPING_DOCS_PATH / mapping_spec.document_reference
        return None

    def list_supported_formats(self) -> Dict[str, List[str]]:
        """List all supported source and target formats."""
        return {
            "source_formats": [sf.value for sf in self._mappings.keys()],
            "report_formats": [tf.value for tf in self._report_mappings.keys()],
        }

    def get_coverage_summary(self) -> Dict[str, Any]:
        """Get summary of mapping coverage."""
        total_fields = sum(m.total_fields for m in self._mappings.values())
        mapped_fields = sum(len(m.field_mappings) for m in self._mappings.values())

        return {
            "total_source_formats": len(self._mappings),
            "total_report_formats": len(self._report_mappings),
            "total_fields_in_sources": total_fields,
            "fields_with_mappings": mapped_fields,
            "reference_documents_path": str(self.MAPPING_DOCS_PATH),
            "detailed_mappings_available": True,
            "note": "Full field mappings in /documents/mappings/ directory"
        }
