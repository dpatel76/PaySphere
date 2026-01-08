"""Base ISO 20022 Extractor with DynamicMapper-based Silver extraction.

This module provides the foundational extractor class for all ISO 20022-based
payment formats. It uses DynamicMapper to extract Silver data based on
database-driven mappings, enabling:

1. Shared Silver tables (stg_iso20022_pacs008, stg_iso20022_pacs009, etc.)
2. Mapping inheritance from base formats (pacs.008.base, pacs.009.base, etc.)
3. Canonical ISO 20022 column naming convention
4. Consistent field extraction across all ISO 20022 formats

System-specific extractors (FEDWIRE, CHIPS, CHAPS, etc.) inherit from
message-type-specific extractors (Pacs008Extractor, Pacs009Extractor)
which in turn inherit from this base class.

Architecture:
    BaseISO20022Extractor
    ├── extract_bronze()     - Common Bronze extraction
    ├── extract_silver()     - Uses DynamicMapper with inherited mappings
    ├── get_silver_columns() - Loads columns from DynamicMapper
    ├── get_silver_values()  - Returns values in mapping order
    └── extract_gold_entities() - Common Gold extraction pattern
"""

from abc import abstractmethod
from typing import Dict, Any, List, Optional, Type, Tuple
import json
import logging
import os

from ..base import (
    BaseExtractor,
    GoldEntities,
    PartyData,
    AccountData,
    FinancialInstitutionData,
)
from .base_parser import BaseISO20022Parser

logger = logging.getLogger(__name__)


# Lazy import to avoid circular dependency
_dynamic_mapper_class = None


def _get_dynamic_mapper():
    """Get DynamicMapper class with lazy import."""
    global _dynamic_mapper_class
    if _dynamic_mapper_class is None:
        from ...orchestration.dynamic_mapper import DynamicMapper
        _dynamic_mapper_class = DynamicMapper
    return _dynamic_mapper_class


def _get_db_connection():
    """Get database connection for DynamicMapper."""
    import psycopg2
    return psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=int(os.environ.get('POSTGRES_PORT', 5433)),
        database=os.environ.get('POSTGRES_DB', 'gps_cdm'),
        user=os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
        password=os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password')
    )


class BaseISO20022Extractor(BaseExtractor):
    """Base extractor for all ISO 20022-based payment formats.

    Uses DynamicMapper for Silver extraction, which:
    - Loads field mappings from mapping.silver_field_mappings
    - Resolves inherited mappings from parent formats (e.g., pacs.008.base)
    - Writes to shared Silver tables with canonical column names
    - Uses source_format discriminator to identify original message type

    Subclasses should define:
    - MESSAGE_TYPE: Format identifier (e.g., 'FEDWIRE', 'CHIPS')
    - PARSER_CLASS: Parser class to use (e.g., FedwirePacs008Parser)
    - DEFAULT_CURRENCY: Default currency if not in message
    - CLEARING_SYSTEM: Clearing system identifier (e.g., 'USABA', 'CHIPS')

    Note: SILVER_TABLE is now dynamically loaded from mapping.message_formats
    """

    # Subclasses define these
    MESSAGE_TYPE: str = "ISO20022"
    PARSER_CLASS: Optional[Type[BaseISO20022Parser]] = None
    DEFAULT_CURRENCY: str = "XXX"
    CLEARING_SYSTEM: Optional[str] = None

    # Cached DynamicMapper instance (per-class to support inheritance)
    _mapper_instance: Optional[Any] = None
    _mapper_conn: Optional[Any] = None

    def __init__(self):
        """Initialize extractor with parser instance."""
        super().__init__()
        self.parser = self.PARSER_CLASS() if self.PARSER_CLASS else None

    @classmethod
    def _get_mapper(cls) -> Any:
        """Get or create DynamicMapper instance for this extractor.

        Returns:
            DynamicMapper instance with database connection
        """
        if cls._mapper_instance is None:
            DynamicMapper = _get_dynamic_mapper()
            cls._mapper_conn = _get_db_connection()
            cls._mapper_instance = DynamicMapper(cls._mapper_conn)
        return cls._mapper_instance

    @classmethod
    def _get_silver_table(cls) -> str:
        """Get Silver table name from database configuration.

        Returns:
            Silver table name (e.g., 'stg_iso20022_pacs008')
        """
        mapper = cls._get_mapper()
        try:
            format_info = mapper._get_format_info(cls.MESSAGE_TYPE)
            return format_info.get('silver_table', f'stg_{cls.MESSAGE_TYPE.lower().replace(".", "_")}')
        except ValueError:
            # Format not in database, use default naming
            return f'stg_{cls.MESSAGE_TYPE.lower().replace(".", "_")}'

    @property
    def SILVER_TABLE(self) -> str:
        """Get Silver table name (dynamically loaded from database)."""
        return self._get_silver_table()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse raw content using the configured parser.

        Args:
            raw_content: Raw message content (XML string or dict)

        Returns:
            Parsed message as dict
        """
        if isinstance(raw_content, dict):
            return raw_content

        if self.parser is None:
            raise ValueError(f"No parser configured for {self.MESSAGE_TYPE}")

        return self.parser.parse(raw_content)

    # ==========================================================================
    # BRONZE EXTRACTION (Common across all ISO 20022)
    # ==========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw ISO 20022 content.

        This implementation is identical across all ISO 20022 formats.

        Args:
            raw_content: Parsed message content as dict
            batch_id: Processing batch identifier

        Returns:
            Dict with raw_id, message_type, raw_content, batch_id
        """
        # Extract message ID from common ISO 20022 locations
        msg_id = (
            raw_content.get('messageId') or
            raw_content.get('msgId') or
            raw_content.get('endToEndId') or
            raw_content.get('instructionId') or
            ''
        )

        return {
            'raw_id': self.generate_raw_id(msg_id),
            'message_type': self.MESSAGE_TYPE,
            'raw_content': json.dumps(raw_content) if isinstance(raw_content, dict) else raw_content,
            'batch_id': batch_id,
        }

    # ==========================================================================
    # SILVER EXTRACTION (Using DynamicMapper)
    # ==========================================================================

    def extract_silver(
        self,
        msg_content: Dict[str, Any],
        raw_id: str,
        stg_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        """Extract Silver layer record using DynamicMapper.

        Uses database-driven mappings to extract fields from parsed message
        content into the canonical Silver table structure. Supports mapping
        inheritance from base ISO 20022 formats.

        Args:
            msg_content: Parsed message content
            raw_id: Reference to Bronze record
            stg_id: Silver staging record ID
            batch_id: Processing batch identifier

        Returns:
            Dict with all fields for Silver staging table
        """
        mapper = self._get_mapper()

        # Use DynamicMapper to extract record based on inherited mappings
        silver_record = mapper.extract_silver_record(
            self.MESSAGE_TYPE,
            msg_content,
            raw_id,
            batch_id
        )

        # Override stg_id with provided value
        silver_record['stg_id'] = stg_id

        # Add source_format discriminator for shared tables
        silver_record['source_format'] = self.MESSAGE_TYPE

        # Add format-specific defaults
        self._apply_format_defaults(silver_record, msg_content)

        return silver_record

    def _apply_format_defaults(self, silver_record: Dict[str, Any], msg_content: Dict[str, Any]) -> None:
        """Apply format-specific defaults to Silver record.

        Override in subclasses to add format-specific fields or defaults.

        Args:
            silver_record: Silver record dict to modify in place
            msg_content: Original parsed message content
        """
        # Default currency if not set
        if not silver_record.get('currency') and not silver_record.get('intr_bk_sttlm_ccy'):
            # Try canonical column name first, then legacy
            if 'intr_bk_sttlm_ccy' in silver_record:
                silver_record['intr_bk_sttlm_ccy'] = self.DEFAULT_CURRENCY
            elif 'currency' in silver_record:
                silver_record['currency'] = self.DEFAULT_CURRENCY

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns from DynamicMapper.

        Loads column list from database mappings, supporting inherited
        mappings from parent formats.

        Returns:
            List of column names in INSERT order
        """
        mapper = self._get_mapper()
        return mapper.get_silver_columns(self.MESSAGE_TYPE)

    def get_silver_values(self, silver_record: Dict[str, Any]) -> Tuple:
        """Return ordered tuple of values for Silver table INSERT.

        Uses DynamicMapper to ensure values are in correct column order.

        Args:
            silver_record: Dict from extract_silver()

        Returns:
            Tuple of values in column order
        """
        mapper = self._get_mapper()
        return mapper.get_silver_values(self.MESSAGE_TYPE, silver_record)

    # ==========================================================================
    # LEGACY SILVER EXTRACTION (For backward compatibility)
    # ==========================================================================

    def _extract_common_silver_fields(
        self,
        msg_content: Dict[str, Any],
        raw_id: str,
        stg_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        """Extract common ISO 20022 fields (LEGACY - use extract_silver instead).

        This method is kept for backward compatibility with subclasses that
        override extract_silver() and call super()._extract_common_silver_fields().

        For new implementations, use extract_silver() which delegates to
        DynamicMapper for database-driven extraction.

        Args:
            msg_content: Parsed message content
            raw_id: Reference to Bronze record
            stg_id: Silver staging record ID
            batch_id: Processing batch identifier

        Returns:
            Dict with common Silver fields
        """
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Source format discriminator for shared Silver tables
            'source_format': self.MESSAGE_TYPE,

            # Message identification
            'message_type': self.MESSAGE_TYPE,
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),

            # Payment identification
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'transaction_id': trunc(msg_content.get('transactionId'), 35),
            'uetr': msg_content.get('uetr'),

            # Settlement
            'settlement_date': msg_content.get('interbankSettlementDate'),
            'settlement_method': trunc(msg_content.get('settlementMethod'), 10),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or self.DEFAULT_CURRENCY,

            # Payment type
            'instruction_priority': trunc(msg_content.get('instructionPriority'), 10),
            'service_level': trunc(msg_content.get('serviceLevelCode'), 35),
            'local_instrument': trunc(msg_content.get('localInstrumentCode'), 35),
            'category_purpose': trunc(msg_content.get('categoryPurposeCode'), 35),

            # Debtor
            'debtor_name': trunc(msg_content.get('debtorName'), 140),
            'debtor_street_name': trunc(msg_content.get('debtorStreetName'), 70),
            'debtor_building_number': trunc(msg_content.get('debtorBuildingNumber'), 16),
            'debtor_post_code': trunc(msg_content.get('debtorPostCode'), 16),
            'debtor_town_name': trunc(msg_content.get('debtorTownName'), 35),
            'debtor_country_sub_division': trunc(msg_content.get('debtorCountrySubDivision'), 35),
            'debtor_country': trunc(msg_content.get('debtorCountry'), 2),
            'debtor_lei': trunc(msg_content.get('debtorLei'), 20),

            # Debtor Account
            'debtor_account_iban': trunc(msg_content.get('debtorAccountIban'), 34),
            'debtor_account_other': trunc(msg_content.get('debtorAccountOther'), 34),
            'debtor_account_type': trunc(msg_content.get('debtorAccountType'), 10),
            'debtor_account_currency': msg_content.get('debtorAccountCurrency'),

            # Debtor Agent
            'debtor_agent_bic': trunc(msg_content.get('debtorAgentBic'), 11),
            'debtor_agent_name': trunc(msg_content.get('debtorAgentName'), 140),
            'debtor_agent_clearing_system_id': trunc(msg_content.get('debtorAgentClearingSystemId'), 10),
            'debtor_agent_member_id': trunc(msg_content.get('debtorAgentMemberId'), 35),

            # Creditor
            'creditor_name': trunc(msg_content.get('creditorName'), 140),
            'creditor_street_name': trunc(msg_content.get('creditorStreetName'), 70),
            'creditor_building_number': trunc(msg_content.get('creditorBuildingNumber'), 16),
            'creditor_post_code': trunc(msg_content.get('creditorPostCode'), 16),
            'creditor_town_name': trunc(msg_content.get('creditorTownName'), 35),
            'creditor_country_sub_division': trunc(msg_content.get('creditorCountrySubDivision'), 35),
            'creditor_country': trunc(msg_content.get('creditorCountry'), 2),
            'creditor_lei': trunc(msg_content.get('creditorLei'), 20),

            # Creditor Account
            'creditor_account_iban': trunc(msg_content.get('creditorAccountIban'), 34),
            'creditor_account_other': trunc(msg_content.get('creditorAccountOther'), 34),
            'creditor_account_type': trunc(msg_content.get('creditorAccountType'), 10),
            'creditor_account_currency': msg_content.get('creditorAccountCurrency'),

            # Creditor Agent
            'creditor_agent_bic': trunc(msg_content.get('creditorAgentBic'), 11),
            'creditor_agent_name': trunc(msg_content.get('creditorAgentName'), 140),
            'creditor_agent_clearing_system_id': trunc(msg_content.get('creditorAgentClearingSystemId'), 10),
            'creditor_agent_member_id': trunc(msg_content.get('creditorAgentMemberId'), 35),

            # Remittance
            'remittance_unstructured': msg_content.get('remittanceUnstructured'),
            'creditor_reference': trunc(msg_content.get('creditorReference'), 35),

            # Processing status
            'processing_status': 'PENDING',
        }

    # ==========================================================================
    # GOLD ENTITY EXTRACTION (Common pattern with overridable helpers)
    # ==========================================================================

    def extract_gold_entities(
        self,
        silver_data: Dict[str, Any],
        stg_id: str,
        batch_id: str
    ) -> GoldEntities:
        """Extract Gold layer entities from Silver record.

        Implements the common extraction pattern for ISO 20022 messages.
        Subclasses can override helper methods to customize field names
        or add format-specific entities.

        Note: Field names may be in canonical ISO 20022 format (e.g., dbtr_nm)
        or legacy format (e.g., debtor_name) depending on Silver table used.

        Args:
            silver_data: Dict with Silver table columns
            stg_id: Silver staging ID
            batch_id: Batch identifier

        Returns:
            GoldEntities container with parties, accounts, and FIs
        """
        entities = GoldEntities()

        # Extract parties
        self._extract_parties(silver_data, entities)

        # Extract accounts
        self._extract_accounts(silver_data, entities)

        # Extract financial institutions
        self._extract_financial_institutions(silver_data, entities)

        return entities

    def _get_field(self, silver_data: Dict[str, Any], *field_names: str) -> Optional[Any]:
        """Get field value trying multiple possible column names.

        Supports both canonical ISO 20022 names and legacy names.

        Args:
            silver_data: Silver record dict
            *field_names: Possible field names in order of preference

        Returns:
            First non-None value found, or None
        """
        for name in field_names:
            value = silver_data.get(name)
            if value is not None:
                return value
        return None

    def _extract_parties(self, silver_data: Dict[str, Any], entities: GoldEntities) -> None:
        """Extract party entities from Silver record.

        Supports both canonical and legacy column naming.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        # Debtor Party - try canonical then legacy column names
        debtor_name = self._get_field(silver_data, 'dbtr_nm', 'debtor_name')
        if debtor_name:
            entities.parties.append(self._create_debtor_party(silver_data))

        # Creditor Party
        creditor_name = self._get_field(silver_data, 'cdtr_nm', 'creditor_name')
        if creditor_name:
            entities.parties.append(self._create_creditor_party(silver_data))

        # Ultimate Debtor (if present)
        ultimate_debtor_name = self._get_field(silver_data, 'ultmt_dbtr_nm', 'ultimate_debtor_name')
        if ultimate_debtor_name:
            entities.parties.append(self._create_ultimate_debtor_party(silver_data))

        # Ultimate Creditor (if present)
        ultimate_creditor_name = self._get_field(silver_data, 'ultmt_cdtr_nm', 'ultimate_creditor_name')
        if ultimate_creditor_name:
            entities.parties.append(self._create_ultimate_creditor_party(silver_data))

    def _create_debtor_party(self, silver_data: Dict[str, Any]) -> PartyData:
        """Create debtor party from Silver data.

        Args:
            silver_data: Silver record dict

        Returns:
            PartyData for debtor
        """
        return PartyData(
            name=self._get_field(silver_data, 'dbtr_nm', 'debtor_name'),
            role="DEBTOR",
            party_type='ORGANIZATION' if self._get_field(silver_data, 'dbtr_org_id_lei', 'debtor_lei') else 'UNKNOWN',
            street_name=self._get_field(silver_data, 'dbtr_pstl_adr_strt_nm', 'debtor_street_name'),
            building_number=self._get_field(silver_data, 'dbtr_pstl_adr_bldg_nb', 'debtor_building_number'),
            post_code=self._get_field(silver_data, 'dbtr_pstl_adr_pst_cd', 'debtor_post_code'),
            town_name=self._get_field(silver_data, 'dbtr_pstl_adr_twn_nm', 'debtor_town_name'),
            country_sub_division=self._get_field(silver_data, 'dbtr_pstl_adr_ctry_sub_dvsn', 'debtor_country_sub_division'),
            country=self._get_field(silver_data, 'dbtr_pstl_adr_ctry', 'debtor_country'),
            identification_type='LEI' if self._get_field(silver_data, 'dbtr_org_id_lei', 'debtor_lei') else None,
            identification_number=self._get_field(silver_data, 'dbtr_org_id_lei', 'debtor_lei'),
        )

    def _create_creditor_party(self, silver_data: Dict[str, Any]) -> PartyData:
        """Create creditor party from Silver data.

        Args:
            silver_data: Silver record dict

        Returns:
            PartyData for creditor
        """
        return PartyData(
            name=self._get_field(silver_data, 'cdtr_nm', 'creditor_name'),
            role="CREDITOR",
            party_type='ORGANIZATION' if self._get_field(silver_data, 'cdtr_org_id_lei', 'creditor_lei') else 'UNKNOWN',
            street_name=self._get_field(silver_data, 'cdtr_pstl_adr_strt_nm', 'creditor_street_name'),
            building_number=self._get_field(silver_data, 'cdtr_pstl_adr_bldg_nb', 'creditor_building_number'),
            post_code=self._get_field(silver_data, 'cdtr_pstl_adr_pst_cd', 'creditor_post_code'),
            town_name=self._get_field(silver_data, 'cdtr_pstl_adr_twn_nm', 'creditor_town_name'),
            country_sub_division=self._get_field(silver_data, 'cdtr_pstl_adr_ctry_sub_dvsn', 'creditor_country_sub_division'),
            country=self._get_field(silver_data, 'cdtr_pstl_adr_ctry', 'creditor_country'),
            identification_type='LEI' if self._get_field(silver_data, 'cdtr_org_id_lei', 'creditor_lei') else None,
            identification_number=self._get_field(silver_data, 'cdtr_org_id_lei', 'creditor_lei'),
        )

    def _create_ultimate_debtor_party(self, silver_data: Dict[str, Any]) -> PartyData:
        """Create ultimate debtor party from Silver data.

        Args:
            silver_data: Silver record dict

        Returns:
            PartyData for ultimate debtor
        """
        return PartyData(
            name=self._get_field(silver_data, 'ultmt_dbtr_nm', 'ultimate_debtor_name'),
            role="ULTIMATE_DEBTOR",
            party_type='UNKNOWN',
            street_name=self._get_field(silver_data, 'ultmt_dbtr_pstl_adr_strt_nm', 'ultimate_debtor_street_name'),
            post_code=self._get_field(silver_data, 'ultmt_dbtr_pstl_adr_pst_cd', 'ultimate_debtor_post_code'),
            town_name=self._get_field(silver_data, 'ultmt_dbtr_pstl_adr_twn_nm', 'ultimate_debtor_town_name'),
            country=self._get_field(silver_data, 'ultmt_dbtr_pstl_adr_ctry', 'ultimate_debtor_country'),
        )

    def _create_ultimate_creditor_party(self, silver_data: Dict[str, Any]) -> PartyData:
        """Create ultimate creditor party from Silver data.

        Args:
            silver_data: Silver record dict

        Returns:
            PartyData for ultimate creditor
        """
        return PartyData(
            name=self._get_field(silver_data, 'ultmt_cdtr_nm', 'ultimate_creditor_name'),
            role="ULTIMATE_CREDITOR",
            party_type='UNKNOWN',
            street_name=self._get_field(silver_data, 'ultmt_cdtr_pstl_adr_strt_nm', 'ultimate_creditor_street_name'),
            post_code=self._get_field(silver_data, 'ultmt_cdtr_pstl_adr_pst_cd', 'ultimate_creditor_post_code'),
            town_name=self._get_field(silver_data, 'ultmt_cdtr_pstl_adr_twn_nm', 'ultimate_creditor_town_name'),
            country=self._get_field(silver_data, 'ultmt_cdtr_pstl_adr_ctry', 'ultimate_creditor_country'),
        )

    def _extract_accounts(self, silver_data: Dict[str, Any], entities: GoldEntities) -> None:
        """Extract account entities from Silver record.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        # Debtor Account
        debtor_acct = (
            self._get_field(silver_data, 'dbtr_acct_id_iban', 'debtor_account_iban') or
            self._get_field(silver_data, 'dbtr_acct_id_othr', 'debtor_account_other', 'debtor_account')
        )
        if debtor_acct:
            entities.accounts.append(self._create_debtor_account(silver_data, debtor_acct))

        # Creditor Account
        creditor_acct = (
            self._get_field(silver_data, 'cdtr_acct_id_iban', 'creditor_account_iban') or
            self._get_field(silver_data, 'cdtr_acct_id_othr', 'creditor_account_other', 'creditor_account')
        )
        if creditor_acct:
            entities.accounts.append(self._create_creditor_account(silver_data, creditor_acct))

    def _create_debtor_account(self, silver_data: Dict[str, Any], account_number: str) -> AccountData:
        """Create debtor account from Silver data.

        Args:
            silver_data: Silver record dict
            account_number: Extracted account number

        Returns:
            AccountData for debtor account
        """
        return AccountData(
            account_number=account_number,
            role="DEBTOR",
            iban=self._get_field(silver_data, 'dbtr_acct_id_iban', 'debtor_account_iban'),
            account_type=self._get_field(silver_data, 'dbtr_acct_tp_cd', 'debtor_account_type') or 'CACC',
            currency=self._get_field(silver_data, 'dbtr_acct_ccy', 'debtor_account_currency', 'currency') or self.DEFAULT_CURRENCY,
        )

    def _create_creditor_account(self, silver_data: Dict[str, Any], account_number: str) -> AccountData:
        """Create creditor account from Silver data.

        Args:
            silver_data: Silver record dict
            account_number: Extracted account number

        Returns:
            AccountData for creditor account
        """
        return AccountData(
            account_number=account_number,
            role="CREDITOR",
            iban=self._get_field(silver_data, 'cdtr_acct_id_iban', 'creditor_account_iban'),
            account_type=self._get_field(silver_data, 'cdtr_acct_tp_cd', 'creditor_account_type') or 'CACC',
            currency=self._get_field(silver_data, 'cdtr_acct_ccy', 'creditor_account_currency', 'currency') or self.DEFAULT_CURRENCY,
        )

    def _extract_financial_institutions(self, silver_data: Dict[str, Any], entities: GoldEntities) -> None:
        """Extract financial institution entities from Silver record.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        # Debtor Agent
        dbtr_agt_bic = self._get_field(silver_data, 'dbtr_agt_bic', 'debtor_agent_bic')
        dbtr_agt_id = self._get_field(silver_data, 'dbtr_agt_clr_sys_mmb_id', 'debtor_agent_member_id')
        if dbtr_agt_bic or dbtr_agt_id:
            entities.financial_institutions.append(self._create_debtor_agent(silver_data))

        # Creditor Agent
        cdtr_agt_bic = self._get_field(silver_data, 'cdtr_agt_bic', 'creditor_agent_bic')
        cdtr_agt_id = self._get_field(silver_data, 'cdtr_agt_clr_sys_mmb_id', 'creditor_agent_member_id')
        if cdtr_agt_bic or cdtr_agt_id:
            entities.financial_institutions.append(self._create_creditor_agent(silver_data))

        # Intermediary Agent 1 (if present)
        intrmdy_agt1_bic = self._get_field(silver_data, 'intrmdy_agt1_bic', 'intermediary_agent1_bic', 'intermediary_agent_bic')
        intrmdy_agt1_id = self._get_field(silver_data, 'intrmdy_agt1_clr_sys_mmb_id', 'intermediary_agent1_member_id', 'intermediary_agent_member_id')
        if intrmdy_agt1_bic or intrmdy_agt1_id:
            entities.financial_institutions.append(self._create_intermediary_agent(silver_data, 1))

        # Intermediary Agent 2 (if present)
        intrmdy_agt2_bic = self._get_field(silver_data, 'intrmdy_agt2_bic', 'intermediary_agent2_bic')
        intrmdy_agt2_id = self._get_field(silver_data, 'intrmdy_agt2_clr_sys_mmb_id', 'intermediary_agent2_member_id')
        if intrmdy_agt2_bic or intrmdy_agt2_id:
            entities.financial_institutions.append(self._create_intermediary_agent(silver_data, 2))

    def _create_debtor_agent(self, silver_data: Dict[str, Any]) -> FinancialInstitutionData:
        """Create debtor agent from Silver data.

        Args:
            silver_data: Silver record dict

        Returns:
            FinancialInstitutionData for debtor agent
        """
        bic = self._get_field(silver_data, 'dbtr_agt_bic', 'debtor_agent_bic')
        return FinancialInstitutionData(
            role="DEBTOR_AGENT",
            name=self._get_field(silver_data, 'dbtr_agt_nm', 'debtor_agent_name') or (f"FI_{bic}" if bic else None),
            bic=bic,
            lei=self._get_field(silver_data, 'dbtr_agt_lei', 'debtor_agent_lei'),
            clearing_code=self._get_field(silver_data, 'dbtr_agt_clr_sys_mmb_id', 'debtor_agent_member_id'),
            clearing_system=self._get_field(silver_data, 'dbtr_agt_clr_sys_cd', 'debtor_agent_clearing_system_id') or self.CLEARING_SYSTEM,
            country=self._derive_country(bic, self._get_field(silver_data, 'dbtr_pstl_adr_ctry', 'debtor_country')),
        )

    def _create_creditor_agent(self, silver_data: Dict[str, Any]) -> FinancialInstitutionData:
        """Create creditor agent from Silver data.

        Args:
            silver_data: Silver record dict

        Returns:
            FinancialInstitutionData for creditor agent
        """
        bic = self._get_field(silver_data, 'cdtr_agt_bic', 'creditor_agent_bic')
        return FinancialInstitutionData(
            role="CREDITOR_AGENT",
            name=self._get_field(silver_data, 'cdtr_agt_nm', 'creditor_agent_name') or (f"FI_{bic}" if bic else None),
            bic=bic,
            lei=self._get_field(silver_data, 'cdtr_agt_lei', 'creditor_agent_lei'),
            clearing_code=self._get_field(silver_data, 'cdtr_agt_clr_sys_mmb_id', 'creditor_agent_member_id'),
            clearing_system=self._get_field(silver_data, 'cdtr_agt_clr_sys_cd', 'creditor_agent_clearing_system_id') or self.CLEARING_SYSTEM,
            country=self._derive_country(bic, self._get_field(silver_data, 'cdtr_pstl_adr_ctry', 'creditor_country')),
        )

    def _create_intermediary_agent(self, silver_data: Dict[str, Any], agent_num: int = 1) -> FinancialInstitutionData:
        """Create intermediary agent from Silver data.

        Args:
            silver_data: Silver record dict
            agent_num: Agent number (1 or 2)

        Returns:
            FinancialInstitutionData for intermediary agent
        """
        if agent_num == 1:
            bic = self._get_field(silver_data, 'intrmdy_agt1_bic', 'intermediary_agent1_bic', 'intermediary_agent_bic')
            name = self._get_field(silver_data, 'intrmdy_agt1_nm', 'intermediary_agent1_name', 'intermediary_agent_name')
            member_id = self._get_field(silver_data, 'intrmdy_agt1_clr_sys_mmb_id', 'intermediary_agent1_member_id', 'intermediary_agent_member_id')
            clr_sys = self._get_field(silver_data, 'intrmdy_agt1_clr_sys_cd', 'intermediary_agent1_clearing_system_id', 'intermediary_agent_clearing_system_id')
        else:
            bic = self._get_field(silver_data, 'intrmdy_agt2_bic', 'intermediary_agent2_bic')
            name = self._get_field(silver_data, 'intrmdy_agt2_nm', 'intermediary_agent2_name')
            member_id = self._get_field(silver_data, 'intrmdy_agt2_clr_sys_mmb_id', 'intermediary_agent2_member_id')
            clr_sys = self._get_field(silver_data, 'intrmdy_agt2_clr_sys_cd', 'intermediary_agent2_clearing_system_id')

        return FinancialInstitutionData(
            role=f"INTERMEDIARY_AGENT{agent_num}",
            name=name or (f"FI_{bic}" if bic else None),
            bic=bic,
            clearing_code=member_id,
            clearing_system=clr_sys or self.CLEARING_SYSTEM,
            country=self._derive_country(bic, None),
        )

    def _derive_country(self, bic: Optional[str], fallback: Optional[str]) -> str:
        """Derive country code from BIC or use fallback.

        BIC format: BANKCCLL where CC is the country code at positions 5-6.

        Args:
            bic: BIC code (may be 8 or 11 characters)
            fallback: Fallback country code

        Returns:
            2-letter country code or 'XX' if cannot determine
        """
        if bic and len(bic) >= 6:
            country = bic[4:6].upper()
            if country.isalpha():
                return country
        return fallback or 'XX'

    @classmethod
    def clear_mapper_cache(cls) -> None:
        """Clear the cached DynamicMapper instance.

        Call this when database mappings have changed and need to be reloaded.
        """
        if cls._mapper_conn:
            try:
                cls._mapper_conn.close()
            except Exception:
                pass
        cls._mapper_instance = None
        cls._mapper_conn = None
