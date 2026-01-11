#!/usr/bin/env python3
"""
Prime CDM Catalog with Business Descriptions

This script populates the mapping.cdm_catalog table with:
1. Schema-derived columns from gold.cdm_* tables
2. Business names and descriptions for each data element
3. ISO 20022 cross-references where applicable

Usage:
    python scripts/catalog/prime_cdm_catalog.py

Environment variables:
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
"""

import os
import sys
import json
import psycopg2
from psycopg2.extras import execute_values
from typing import Dict, List, Optional, Any

# Add parent directory to path for importing definitions module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import table definitions from separate files
try:
    from definitions import CDM_EXTENSION_TABLES, CDM_ISO_TABLES, CDM_SUPPORTING_TABLES
except ImportError:
    CDM_EXTENSION_TABLES = {}
    CDM_ISO_TABLES = {}
    CDM_SUPPORTING_TABLES = {}
    print("Warning: Could not import table definitions")

# Database connection
DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'port': int(os.environ.get('POSTGRES_PORT', 5433)),
    'database': os.environ.get('POSTGRES_DB', 'gps_cdm'),
    'user': os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password'),
}

# ============================================================================
# Business Descriptions for CDM Data Elements
# Cross-checked against ISO 20022 definitions where applicable
# ============================================================================

CDM_BUSINESS_DESCRIPTIONS: Dict[str, Dict[str, Dict[str, Any]]] = {
    # ========================================================================
    # NOTE: cdm_payment_instruction has been deprecated and renamed to
    # cdm_payment_instruction_drop. It was replaced by ISO semantic tables:
    # - cdm_pacs_fi_customer_credit_transfer (pacs.008)
    # - cdm_pain_customer_credit_transfer_initiation (pain.001)
    # - etc.
    # ========================================================================

    # ========================================================================
    # cdm_party - Party information (Debtor, Creditor, etc.)
    # Per ISO 20022: PartyIdentification
    # ========================================================================
    # ========================================================================
    # cdm_party - Party information (Debtor, Creditor, etc.)
    # ========================================================================
    'cdm_party': {
        'party_id': {
            'business_name': 'Party ID',
            'business_description': 'Unique identifier for this party record in the Common Domain Model. Auto-generated UUID serving as primary key.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_message_type': {
            'business_name': 'Source Message Type',
            'business_description': 'Original message format from which this party information was extracted.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'role': {
            'business_name': 'Party Role',
            'business_description': 'The role this party plays in the payment transaction. Identifies the relationship of this party to the payment.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'DEBTOR', 'description': 'Party that owes money (payer/originator)'},
                {'value': 'CREDITOR', 'description': 'Party that receives money (payee/beneficiary)'},
                {'value': 'INITIATING_PARTY', 'description': 'Party that initiates the payment on behalf of debtor'},
                {'value': 'ULTIMATE_DEBTOR', 'description': 'Ultimate party that owes the money (when different from debtor)'},
                {'value': 'ULTIMATE_CREDITOR', 'description': 'Ultimate party to receive the money (when different from creditor)'},
            ],
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'name': {
            'business_name': 'Party Name',
            'business_description': 'Full legal name of the party. For organizations, this is the registered company name. For individuals, this is the full name.',
            'data_format': 'Text, max 140 characters',
            'iso_element_name': 'Name',
            'iso_element_path': 'Dbtr/Nm or Cdtr/Nm',
            'iso_data_type': 'Max140Text',
        },
        'party_type': {
            'business_name': 'Party Type',
            'business_description': 'Classification of whether the party is an individual person or an organization/legal entity.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'INDIVIDUAL', 'description': 'Natural person'},
                {'value': 'ORGANIZATION', 'description': 'Legal entity, company, or organization'},
                {'value': 'UNKNOWN', 'description': 'Party type not specified in source'},
            ],
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'address_line': {
            'business_name': 'Address Lines',
            'business_description': 'Street address of the party. May contain multiple lines for complex addresses.',
            'data_format': 'Text array',
            'iso_element_name': 'AddressLine',
            'iso_element_path': 'Dbtr/PstlAdr/AdrLine or Cdtr/PstlAdr/AdrLine',
            'iso_data_type': 'Max70Text',
        },
        'street_name': {
            'business_name': 'Street Name',
            'business_description': 'Name of the street in the party address.',
            'iso_element_name': 'StreetName',
            'iso_element_path': 'PstlAdr/StrtNm',
            'iso_data_type': 'Max70Text',
        },
        'building_number': {
            'business_name': 'Building Number',
            'business_description': 'Number of the building on the street.',
            'iso_element_name': 'BuildingNumber',
            'iso_element_path': 'PstlAdr/BldgNb',
            'iso_data_type': 'Max16Text',
        },
        'city': {
            'business_name': 'City',
            'business_description': 'City or town name in the party postal address.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'TownName',
            'iso_element_path': 'PstlAdr/TwnNm',
            'iso_data_type': 'Max35Text',
        },
        'postal_code': {
            'business_name': 'Postal Code',
            'business_description': 'Postal code or ZIP code in the party address.',
            'data_format': 'Text, max 16 characters',
            'iso_element_name': 'PostCode',
            'iso_element_path': 'PstlAdr/PstCd',
            'iso_data_type': 'Max16Text',
        },
        'country': {
            'business_name': 'Country',
            'business_description': 'ISO 3166-1 alpha-2 country code for the party address.',
            'data_format': 'ISO 3166-1 alpha-2 (2 letters)',
            'iso_element_name': 'Country',
            'iso_element_path': 'PstlAdr/Ctry',
            'iso_data_type': 'CountryCode',
        },
        'country_subdivision': {
            'business_name': 'Country Subdivision',
            'business_description': 'State, province, or region within the country.',
            'iso_element_name': 'CountrySubDivision',
            'iso_element_path': 'PstlAdr/CtrySubDvsn',
            'iso_data_type': 'Max35Text',
        },
        'contact_name': {
            'business_name': 'Contact Name',
            'business_description': 'Name of the contact person for this party.',
            'iso_element_name': 'Name',
            'iso_element_path': 'CtctDtls/Nm',
            'iso_data_type': 'Max140Text',
        },
        'contact_phone': {
            'business_name': 'Contact Phone',
            'business_description': 'Phone number for the party contact.',
            'iso_element_name': 'PhoneNumber',
            'iso_element_path': 'CtctDtls/PhneNb',
            'iso_data_type': 'PhoneNumber',
        },
        'contact_email': {
            'business_name': 'Contact Email',
            'business_description': 'Email address for the party contact.',
            'iso_element_name': 'EmailAddress',
            'iso_element_path': 'CtctDtls/EmailAdr',
            'iso_data_type': 'Max2048Text',
        },
        'identification_code': {
            'business_name': 'Identification Code',
            'business_description': 'Primary identification code for the party. Could be organization ID, private ID, or other identifier.',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Id/OrgId/Othr/Id or Id/PrvtId/Othr/Id',
            'iso_data_type': 'Max35Text',
        },
        'identification_scheme': {
            'business_name': 'Identification Scheme',
            'business_description': 'Scheme or type of the identification code (e.g., DUNS, LEI, Tax ID).',
            'iso_element_name': 'SchemeName',
            'iso_element_path': 'Id/OrgId/Othr/SchmeNm/Cd',
            'iso_data_type': 'ExternalOrganisationIdentification1Code',
        },
        # Additional party address fields
        'address_line1': {
            'business_name': 'Address Line 1',
            'business_description': 'First line of the party postal address.',
            'iso_element_name': 'AddressLine',
            'iso_element_path': 'PstlAdr/AdrLine[1]',
            'iso_data_type': 'Max70Text',
        },
        'address_line2': {
            'business_name': 'Address Line 2',
            'business_description': 'Second line of the party postal address.',
            'iso_element_name': 'AddressLine',
            'iso_element_path': 'PstlAdr/AdrLine[2]',
            'iso_data_type': 'Max70Text',
        },
        'address_line3': {
            'business_name': 'Address Line 3',
            'business_description': 'Third line of the party postal address.',
            'iso_element_name': 'AddressLine',
            'iso_element_path': 'PstlAdr/AdrLine[3]',
            'iso_data_type': 'Max70Text',
        },
        'address_line4': {
            'business_name': 'Address Line 4',
            'business_description': 'Fourth line of the party postal address.',
            'iso_element_name': 'AddressLine',
            'iso_element_path': 'PstlAdr/AdrLine[4]',
            'iso_data_type': 'Max70Text',
        },
        'address_line5': {
            'business_name': 'Address Line 5',
            'business_description': 'Fifth line of the party postal address.',
            'iso_element_name': 'AddressLine',
            'iso_element_path': 'PstlAdr/AdrLine[5]',
            'iso_data_type': 'Max70Text',
        },
        'address_line6': {
            'business_name': 'Address Line 6',
            'business_description': 'Sixth line of the party postal address.',
            'iso_element_name': 'AddressLine',
            'iso_element_path': 'PstlAdr/AdrLine[6]',
            'iso_data_type': 'Max70Text',
        },
        'address_line7': {
            'business_name': 'Address Line 7',
            'business_description': 'Seventh line of the party postal address.',
            'iso_element_name': 'AddressLine',
            'iso_element_path': 'PstlAdr/AdrLine[7]',
            'iso_data_type': 'Max70Text',
        },
        'address_type': {
            'business_name': 'Address Type',
            'business_description': 'Type of address (e.g., residential, business, mailing).',
            'iso_element_name': 'AddressType',
            'iso_element_path': 'PstlAdr/AdrTp',
            'iso_data_type': 'AddressType2Code',
        },
        'post_box': {
            'business_name': 'Post Box',
            'business_description': 'Post office box number.',
            'iso_element_name': 'PostBox',
            'iso_element_path': 'PstlAdr/PstBx',
            'iso_data_type': 'Max16Text',
        },
        'room': {
            'business_name': 'Room',
            'business_description': 'Room or suite number within a building.',
            'iso_element_name': 'Room',
            'iso_element_path': 'PstlAdr/Room',
            'iso_data_type': 'Max70Text',
        },
        'floor': {
            'business_name': 'Floor',
            'business_description': 'Floor or level within a building.',
            'iso_element_name': 'Floor',
            'iso_element_path': 'PstlAdr/Flr',
            'iso_data_type': 'Max70Text',
        },
        'department': {
            'business_name': 'Department',
            'business_description': 'Department or division within an organization.',
            'iso_element_name': 'Department',
            'iso_element_path': 'PstlAdr/Dept',
            'iso_data_type': 'Max70Text',
        },
        'sub_department': {
            'business_name': 'Sub-Department',
            'business_description': 'Sub-division within a department.',
            'iso_element_name': 'SubDepartment',
            'iso_element_path': 'PstlAdr/SubDept',
            'iso_data_type': 'Max70Text',
        },
        'district_name': {
            'business_name': 'District Name',
            'business_description': 'Name of the district or neighbourhood.',
            'iso_element_name': 'DistrictName',
            'iso_element_path': 'PstlAdr/DstrctNm',
            'iso_data_type': 'Max35Text',
        },
        'town_name': {
            'business_name': 'Town Name',
            'business_description': 'Name of the town or city.',
            'iso_element_name': 'TownName',
            'iso_element_path': 'PstlAdr/TwnNm',
            'iso_data_type': 'Max35Text',
        },
        'post_code': {
            'business_name': 'Post Code',
            'business_description': 'Postal or ZIP code.',
            'iso_element_name': 'PostCode',
            'iso_element_path': 'PstlAdr/PstCd',
            'iso_data_type': 'Max16Text',
        },
        'country_sub_division': {
            'business_name': 'Country Sub-Division',
            'business_description': 'State, province, or region within the country.',
            'iso_element_name': 'CountrySubDivision',
            'iso_element_path': 'PstlAdr/CtrySubDvsn',
            'iso_data_type': 'Max35Text',
        },
        'region': {
            'business_name': 'Region',
            'business_description': 'Geographic region of the party address.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'street_building_id': {
            'business_name': 'Street/Building ID',
            'business_description': 'Building identifier or number on the street.',
            'iso_element_name': 'BuildingNumber',
            'iso_element_path': 'PstlAdr/BldgNb',
            'iso_data_type': 'Max16Text',
        },
        # Individual/Private party fields
        'given_name': {
            'business_name': 'Given Name',
            'business_description': 'First name or given name of an individual.',
            'iso_element_name': 'GivenName',
            'iso_element_path': 'Nm/GvnNm',
            'iso_data_type': 'Max35Text',
        },
        'family_name': {
            'business_name': 'Family Name',
            'business_description': 'Surname or family name of an individual.',
            'iso_element_name': 'FamilyName',
            'iso_element_path': 'Nm/FmlyNm',
            'iso_data_type': 'Max35Text',
        },
        'name_suffix': {
            'business_name': 'Name Suffix',
            'business_description': 'Name suffix (e.g., Jr., Sr., III).',
            'iso_element_name': 'NameSuffix',
            'iso_element_path': 'Nm/NmSfx',
            'iso_data_type': 'Max35Text',
        },
        'date_of_birth': {
            'business_name': 'Date of Birth',
            'business_description': 'Birth date of an individual party.',
            'data_format': 'ISO 8601 Date',
            'iso_element_name': 'DateOfBirth',
            'iso_element_path': 'Id/PrvtId/DtAndPlcOfBirth/BirthDt',
            'iso_data_type': 'ISODate',
        },
        'city_of_birth': {
            'business_name': 'City of Birth',
            'business_description': 'City where the individual was born.',
            'iso_element_name': 'CityOfBirth',
            'iso_element_path': 'Id/PrvtId/DtAndPlcOfBirth/CityOfBirth',
            'iso_data_type': 'Max35Text',
        },
        'country_of_birth': {
            'business_name': 'Country of Birth',
            'business_description': 'Country where the individual was born (ISO 3166-1 alpha-2).',
            'data_format': 'ISO 3166-1 alpha-2',
            'iso_element_name': 'CountryOfBirth',
            'iso_element_path': 'Id/PrvtId/DtAndPlcOfBirth/CtryOfBirth',
            'iso_data_type': 'CountryCode',
        },
        'place_of_birth': {
            'business_name': 'Place of Birth',
            'business_description': 'Full place of birth description.',
            'iso_element_name': 'ProvinceOfBirth',
            'iso_element_path': 'Id/PrvtId/DtAndPlcOfBirth/PrvcOfBirth',
            'iso_data_type': 'Max35Text',
        },
        'country_of_residence': {
            'business_name': 'Country of Residence',
            'business_description': 'Country where the individual resides (ISO 3166-1 alpha-2).',
            'data_format': 'ISO 3166-1 alpha-2',
            'iso_element_name': 'CountryOfResidence',
            'iso_element_path': 'CtryOfRes',
            'iso_data_type': 'CountryCode',
        },
        'nationality': {
            'business_name': 'Nationality',
            'business_description': 'Country of citizenship (ISO 3166-1 alpha-2).',
            'data_format': 'ISO 3166-1 alpha-2',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        # Organization identification
        'dba_name': {
            'business_name': 'DBA Name',
            'business_description': 'Doing Business As name - trade name used by the organization.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'legal_entity_type': {
            'business_name': 'Legal Entity Type',
            'business_description': 'Type of legal entity (e.g., Corporation, LLC, Partnership).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'lei': {
            'business_name': 'LEI',
            'business_description': 'Legal Entity Identifier (ISO 17442) - 20-character code uniquely identifying the party.',
            'data_format': 'ISO 17442 (20 characters)',
            'iso_element_name': 'LEI',
            'iso_element_path': 'Id/OrgId/LEI',
            'iso_data_type': 'LEIIdentifier',
        },
        'bic': {
            'business_name': 'BIC',
            'business_description': 'Bank Identifier Code (SWIFT code) if the party is a financial institution.',
            'data_format': 'ISO 9362 (8 or 11 characters)',
            'iso_element_name': 'AnyBIC',
            'iso_element_path': 'Id/OrgId/AnyBIC',
            'iso_data_type': 'AnyBICIdentifier',
        },
        'org_id_lei': {
            'business_name': 'Organization LEI',
            'business_description': 'Legal Entity Identifier for organizational identification.',
            'data_format': 'ISO 17442 (20 characters)',
            'iso_element_name': 'LEI',
            'iso_element_path': 'Id/OrgId/LEI',
            'iso_data_type': 'LEIIdentifier',
        },
        'org_id_any_bic': {
            'business_name': 'Organization BIC',
            'business_description': 'BIC code for organizational identification.',
            'data_format': 'ISO 9362',
            'iso_element_name': 'AnyBIC',
            'iso_element_path': 'Id/OrgId/AnyBIC',
            'iso_data_type': 'AnyBICIdentifier',
        },
        'org_id_other_id': {
            'business_name': 'Organization Other ID',
            'business_description': 'Other organization identifier value.',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Id/OrgId/Othr/Id',
            'iso_data_type': 'Max35Text',
        },
        'org_id_other_scheme_name': {
            'business_name': 'Organization ID Scheme',
            'business_description': 'Scheme name for the other organization identifier.',
            'iso_element_name': 'SchemeName',
            'iso_element_path': 'Id/OrgId/Othr/SchmeNm/Cd',
            'iso_data_type': 'ExternalOrganisationIdentification1Code',
        },
        'org_id_other_issuer': {
            'business_name': 'Organization ID Issuer',
            'business_description': 'Entity that issued the organization identifier.',
            'iso_element_name': 'Issuer',
            'iso_element_path': 'Id/OrgId/Othr/Issr',
            'iso_data_type': 'Max35Text',
        },
        # Private identification
        'prvt_id_birth_date': {
            'business_name': 'Private ID Birth Date',
            'business_description': 'Date of birth for private individual identification.',
            'data_format': 'ISO 8601 Date',
            'iso_element_name': 'BirthDate',
            'iso_element_path': 'Id/PrvtId/DtAndPlcOfBirth/BirthDt',
            'iso_data_type': 'ISODate',
        },
        'prvt_id_birth_city': {
            'business_name': 'Private ID Birth City',
            'business_description': 'City of birth for identification purposes.',
            'iso_element_name': 'CityOfBirth',
            'iso_element_path': 'Id/PrvtId/DtAndPlcOfBirth/CityOfBirth',
            'iso_data_type': 'Max35Text',
        },
        'prvt_id_birth_country': {
            'business_name': 'Private ID Birth Country',
            'business_description': 'Country of birth for identification purposes.',
            'data_format': 'ISO 3166-1 alpha-2',
            'iso_element_name': 'CountryOfBirth',
            'iso_element_path': 'Id/PrvtId/DtAndPlcOfBirth/CtryOfBirth',
            'iso_data_type': 'CountryCode',
        },
        'prvt_id_birth_province': {
            'business_name': 'Private ID Birth Province',
            'business_description': 'Province or state of birth.',
            'iso_element_name': 'ProvinceOfBirth',
            'iso_element_path': 'Id/PrvtId/DtAndPlcOfBirth/PrvcOfBirth',
            'iso_data_type': 'Max35Text',
        },
        'prvt_id_other_id': {
            'business_name': 'Private Other ID',
            'business_description': 'Other private identifier value (e.g., passport, driver license).',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Id/PrvtId/Othr/Id',
            'iso_data_type': 'Max35Text',
        },
        'prvt_id_scheme_name': {
            'business_name': 'Private ID Scheme',
            'business_description': 'Scheme name for the private identifier.',
            'iso_element_name': 'SchemeName',
            'iso_element_path': 'Id/PrvtId/Othr/SchmeNm/Cd',
            'iso_data_type': 'ExternalPersonIdentification1Code',
        },
        'prvt_id_issuer': {
            'business_name': 'Private ID Issuer',
            'business_description': 'Entity that issued the private identifier.',
            'iso_element_name': 'Issuer',
            'iso_element_path': 'Id/PrvtId/Othr/Issr',
            'iso_data_type': 'Max35Text',
        },
        # Government/Tax identification
        'tax_id': {
            'business_name': 'Tax ID',
            'business_description': 'Tax identification number (e.g., TIN, SSN, EIN).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'tax_id_type': {
            'business_name': 'Tax ID Type',
            'business_description': 'Type of tax identifier (e.g., TIN, SSN, EIN, VAT).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'tax_id_country': {
            'business_name': 'Tax ID Country',
            'business_description': 'Country that issued the tax ID.',
            'data_format': 'ISO 3166-1 alpha-2',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'tax_residencies': {
            'business_name': 'Tax Residencies',
            'business_description': 'Countries where the party is tax resident.',
            'data_format': 'JSON Array of country codes',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'national_id_number': {
            'business_name': 'National ID Number',
            'business_description': 'National identification number (e.g., SSN, National Insurance Number).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'national_id_type': {
            'business_name': 'National ID Type',
            'business_description': 'Type of national identification document.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identification_number': {
            'business_name': 'Identification Number',
            'business_description': 'Primary identification document number.',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Id/Othr/Id',
            'iso_data_type': 'Max35Text',
        },
        'identification_type': {
            'business_name': 'Identification Type',
            'business_description': 'Type of identification document (e.g., Passport, National ID, Driver License).',
            'iso_element_name': 'SchemeName',
            'iso_element_path': 'Id/Othr/SchmeNm/Cd',
            'iso_data_type': None,
        },
        'identification_country': {
            'business_name': 'Identification Country',
            'business_description': 'Country that issued the identification document.',
            'data_format': 'ISO 3166-1 alpha-2',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identification_expiry': {
            'business_name': 'Identification Expiry',
            'business_description': 'Expiry date of the identification document.',
            'data_format': 'ISO 8601 Date',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'registration_number': {
            'business_name': 'Registration Number',
            'business_description': 'Company registration number.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'registration_country': {
            'business_name': 'Registration Country',
            'business_description': 'Country of company registration.',
            'data_format': 'ISO 3166-1 alpha-2',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'industry_code': {
            'business_name': 'Industry Code',
            'business_description': 'Industry classification code (e.g., NAICS, SIC, ISIC).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        # Contact information
        'phone_number': {
            'business_name': 'Phone Number',
            'business_description': 'Primary phone number of the party.',
            'iso_element_name': 'PhoneNumber',
            'iso_element_path': 'CtctDtls/PhneNb',
            'iso_data_type': 'PhoneNumber',
        },
        'email_address': {
            'business_name': 'Email Address',
            'business_description': 'Primary email address of the party.',
            'iso_element_name': 'EmailAddress',
            'iso_element_path': 'CtctDtls/EmailAdr',
            'iso_data_type': 'Max2048Text',
        },
        'contact_email_address': {
            'business_name': 'Contact Email Address',
            'business_description': 'Email address of the contact person.',
            'iso_element_name': 'EmailAddress',
            'iso_element_path': 'CtctDtls/EmailAdr',
            'iso_data_type': 'Max2048Text',
        },
        'contact_fax': {
            'business_name': 'Contact Fax',
            'business_description': 'Fax number of the contact person.',
            'iso_element_name': 'FaxNumber',
            'iso_element_path': 'CtctDtls/FaxNb',
            'iso_data_type': 'PhoneNumber',
        },
        'contact_mobile': {
            'business_name': 'Contact Mobile',
            'business_description': 'Mobile phone number of the contact person.',
            'iso_element_name': 'MobileNumber',
            'iso_element_path': 'CtctDtls/MobNb',
            'iso_data_type': 'PhoneNumber',
        },
        'contact_other': {
            'business_name': 'Contact Other',
            'business_description': 'Other contact details.',
            'iso_element_name': 'Other',
            'iso_element_path': 'CtctDtls/Othr',
            'iso_data_type': 'Max35Text',
        },
        # Ultimate party references
        'ultimate_debtor_bic': {
            'business_name': 'Ultimate Debtor BIC',
            'business_description': 'BIC code of the ultimate debtor if different from debtor.',
            'data_format': 'ISO 9362',
            'iso_element_name': 'AnyBIC',
            'iso_element_path': 'UltmtDbtr/Id/OrgId/AnyBIC',
            'iso_data_type': 'AnyBICIdentifier',
        },
        'ultimate_creditor_bic': {
            'business_name': 'Ultimate Creditor BIC',
            'business_description': 'BIC code of the ultimate creditor if different from creditor.',
            'data_format': 'ISO 9362',
            'iso_element_name': 'AnyBIC',
            'iso_element_path': 'UltmtCdtr/Id/OrgId/AnyBIC',
            'iso_data_type': 'AnyBICIdentifier',
        },
        # Risk and compliance fields
        'pep_flag': {
            'business_name': 'PEP Flag',
            'business_description': 'Indicates if the party is a Politically Exposed Person.',
            'data_format': 'Boolean',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'pep_category': {
            'business_name': 'PEP Category',
            'business_description': 'Category of Politically Exposed Person (e.g., Head of State, Senior Official).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'risk_rating': {
            'business_name': 'Risk Rating',
            'business_description': 'Overall risk rating assigned to the party.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'LOW', 'description': 'Low risk party'},
                {'value': 'MEDIUM', 'description': 'Medium risk party'},
                {'value': 'HIGH', 'description': 'High risk party'},
            ],
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'sanctions_screening_status': {
            'business_name': 'Sanctions Screening Status',
            'business_description': 'Result of sanctions list screening.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'CLEAR', 'description': 'No sanctions matches'},
                {'value': 'HIT', 'description': 'Potential sanctions match'},
                {'value': 'PENDING', 'description': 'Screening not completed'},
            ],
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'sanctions_list_match': {
            'business_name': 'Sanctions List Match',
            'business_description': 'Details of any sanctions list matches.',
            'data_format': 'JSON',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        # FATCA/CRS compliance
        'fatca_classification': {
            'business_name': 'FATCA Classification',
            'business_description': 'Foreign Account Tax Compliance Act classification.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'fatca_giin': {
            'business_name': 'FATCA GIIN',
            'business_description': 'Global Intermediary Identification Number for FATCA reporting.',
            'data_format': '19 characters',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'us_tax_status': {
            'business_name': 'US Tax Status',
            'business_description': 'US tax status for FATCA purposes.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'crs_reportable': {
            'business_name': 'CRS Reportable',
            'business_description': 'Indicates if the party is reportable under Common Reporting Standard.',
            'data_format': 'Boolean',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'crs_entity_type': {
            'business_name': 'CRS Entity Type',
            'business_description': 'Entity type for CRS classification purposes.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        # Lineage reference
        'source_instruction_id': {
            'business_name': 'Source Instruction ID',
            'business_description': 'Reference to the source payment instruction that contains this party.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        # SCD and audit fields
        'is_current': {
            'business_name': 'Is Current',
            'business_description': 'SCD2 flag indicating if this is the current version.',
            'data_format': 'Boolean',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'is_deleted': {
            'business_name': 'Is Deleted',
            'business_description': 'Soft delete flag.',
            'data_format': 'Boolean',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'valid_from': {
            'business_name': 'Valid From',
            'business_description': 'Start of validity period for this version.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'valid_to': {
            'business_name': 'Valid To',
            'business_description': 'End of validity period for this version.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'record_version': {
            'business_name': 'Record Version',
            'business_description': 'Version number for optimistic locking.',
            'data_format': 'Integer',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },

    # ========================================================================
    # cdm_financial_institution - Financial institution information
    # ========================================================================
    'cdm_financial_institution': {
        'institution_id': {
            'business_name': 'Institution ID',
            'business_description': 'Unique identifier for this financial institution record in the Common Domain Model.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_message_type': {
            'business_name': 'Source Message Type',
            'business_description': 'Original message format from which this institution information was extracted.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'role': {
            'business_name': 'Institution Role',
            'business_description': 'The role this financial institution plays in the payment chain.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'DEBTOR_AGENT', 'description': 'Bank of the debtor (payer\'s bank)'},
                {'value': 'CREDITOR_AGENT', 'description': 'Bank of the creditor (beneficiary\'s bank)'},
                {'value': 'INSTRUCTING_AGENT', 'description': 'Agent instructing the next party in the chain'},
                {'value': 'INSTRUCTED_AGENT', 'description': 'Agent receiving instruction from previous party'},
                {'value': 'INTERMEDIARY_AGENT1', 'description': 'First intermediary bank in the chain'},
                {'value': 'INTERMEDIARY_AGENT2', 'description': 'Second intermediary bank in the chain'},
                {'value': 'INTERMEDIARY_AGENT3', 'description': 'Third intermediary bank in the chain'},
                {'value': 'PREVIOUS_INSTRUCTING_AGENT1', 'description': 'Previous instructing agent in return chain'},
            ],
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'name': {
            'business_name': 'Institution Name',
            'business_description': 'Full legal name of the financial institution.',
            'data_format': 'Text, max 140 characters',
            'iso_element_name': 'Name',
            'iso_element_path': 'DbtrAgt/FinInstnId/Nm or CdtrAgt/FinInstnId/Nm',
            'iso_data_type': 'Max140Text',
        },
        'bic': {
            'business_name': 'BIC/SWIFT Code',
            'business_description': 'Bank Identifier Code (ISO 9362) - an 8 or 11 character code uniquely identifying the financial institution globally.',
            'data_format': 'ISO 9362 (8 or 11 characters)',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'FinInstnId/BICFI',
            'iso_data_type': 'BICFIIdentifier',
        },
        'clearing_system_id': {
            'business_name': 'Clearing System ID',
            'business_description': 'Identifier of the clearing system (e.g., FEDWIRE, CHIPS, TARGET2) where this institution is a member.',
            'iso_element_name': 'ClearingSystemIdentification',
            'iso_element_path': 'FinInstnId/ClrSysMmbId/ClrSysId/Cd',
            'iso_data_type': 'ExternalClearingSystemIdentification1Code',
        },
        'member_id': {
            'business_name': 'Member ID',
            'business_description': 'Membership identifier within the relevant clearing system. Format varies by clearing system (e.g., ABA routing number for Fedwire).',
            'iso_element_name': 'MemberIdentification',
            'iso_element_path': 'FinInstnId/ClrSysMmbId/MmbId',
            'iso_data_type': 'Max35Text',
        },
        'country': {
            'business_name': 'Country',
            'business_description': 'ISO 3166-1 alpha-2 country code of the institution headquarters. Often derived from positions 5-6 of the BIC code.',
            'data_format': 'ISO 3166-1 alpha-2 (2 letters)',
            'iso_element_name': 'Country',
            'iso_element_path': 'FinInstnId/PstlAdr/Ctry',
            'iso_data_type': 'CountryCode',
        },
        'branch_id': {
            'business_name': 'Branch ID',
            'business_description': 'Identifier for a specific branch of the financial institution. Last 3 characters of an 11-character BIC, or a separate branch code.',
            'iso_element_name': 'BranchIdentification',
            'iso_element_path': 'BrnchId/Id',
            'iso_data_type': 'Max35Text',
        },
        'lei': {
            'business_name': 'LEI',
            'business_description': 'Legal Entity Identifier (ISO 17442) - a 20-character alphanumeric code uniquely identifying legal entities participating in financial transactions.',
            'data_format': 'ISO 17442 (20 characters)',
            'iso_element_name': 'LEI',
            'iso_element_path': 'FinInstnId/LEI',
            'iso_data_type': 'LEIIdentifier',
        },
        'address_line': {
            'business_name': 'Address Lines',
            'business_description': 'Street address of the financial institution.',
            'iso_element_name': 'AddressLine',
            'iso_element_path': 'FinInstnId/PstlAdr/AdrLine',
            'iso_data_type': 'Max70Text',
        },
        'city': {
            'business_name': 'City',
            'business_description': 'City where the institution is located.',
            'iso_element_name': 'TownName',
            'iso_element_path': 'FinInstnId/PstlAdr/TwnNm',
            'iso_data_type': 'Max35Text',
        },
        'postal_code': {
            'business_name': 'Postal Code',
            'business_description': 'Postal code of the institution address.',
            'iso_element_name': 'PostCode',
            'iso_element_path': 'FinInstnId/PstlAdr/PstCd',
            'iso_data_type': 'Max16Text',
        },
        # Additional financial institution fields
        'fi_id': {
            'business_name': 'FI ID',
            'business_description': 'System-generated unique identifier for the financial institution record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'fi_type': {
            'business_name': 'FI Type',
            'business_description': 'Type of financial institution (e.g., Bank, Credit Union, Broker).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'institution_name': {
            'business_name': 'Institution Name',
            'business_description': 'Full legal name of the financial institution.',
            'iso_element_name': 'Name',
            'iso_element_path': 'FinInstnId/Nm',
            'iso_data_type': 'Max140Text',
        },
        'short_name': {
            'business_name': 'Short Name',
            'business_description': 'Abbreviated name or trading name of the institution.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'address_line1': {
            'business_name': 'Address Line 1',
            'business_description': 'First line of the institution address.',
            'iso_element_name': 'AddressLine',
            'iso_element_path': 'FinInstnId/PstlAdr/AdrLine[1]',
            'iso_data_type': 'Max70Text',
        },
        'address_line2': {
            'business_name': 'Address Line 2',
            'business_description': 'Second line of the institution address.',
            'iso_element_name': 'AddressLine',
            'iso_element_path': 'FinInstnId/PstlAdr/AdrLine[2]',
            'iso_data_type': 'Max70Text',
        },
        'town_name': {
            'business_name': 'Town Name',
            'business_description': 'Town or city of the institution.',
            'iso_element_name': 'TownName',
            'iso_element_path': 'FinInstnId/PstlAdr/TwnNm',
            'iso_data_type': 'Max35Text',
        },
        'post_code': {
            'business_name': 'Post Code',
            'business_description': 'Postal or ZIP code of the institution.',
            'iso_element_name': 'PostCode',
            'iso_element_path': 'FinInstnId/PstlAdr/PstCd',
            'iso_data_type': 'Max16Text',
        },
        'country_sub_division': {
            'business_name': 'Country Sub-Division',
            'business_description': 'State, province, or region of the institution.',
            'iso_element_name': 'CountrySubDivision',
            'iso_element_path': 'FinInstnId/PstlAdr/CtrySubDvsn',
            'iso_data_type': 'Max35Text',
        },
        'is_branch': {
            'business_name': 'Is Branch',
            'business_description': 'Indicates if this represents a branch rather than headquarters.',
            'data_format': 'Boolean',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'branch_name': {
            'business_name': 'Branch Name',
            'business_description': 'Name of the branch.',
            'iso_element_name': 'Name',
            'iso_element_path': 'BrnchId/Nm',
            'iso_data_type': 'Max140Text',
        },
        'branch_identification': {
            'business_name': 'Branch Identification',
            'business_description': 'Unique identifier for the branch.',
            'iso_element_name': 'Identification',
            'iso_element_path': 'BrnchId/Id',
            'iso_data_type': 'Max35Text',
        },
        'branch_identification_code': {
            'business_name': 'Branch ID Code',
            'business_description': 'Code identifying the branch within the institution.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'branch_lei': {
            'business_name': 'Branch LEI',
            'business_description': 'Legal Entity Identifier for the branch if different from parent.',
            'data_format': 'ISO 17442 (20 characters)',
            'iso_element_name': 'LEI',
            'iso_element_path': 'BrnchId/LEI',
            'iso_data_type': 'LEIIdentifier',
        },
        'parent_fi_id': {
            'business_name': 'Parent FI ID',
            'business_description': 'Foreign key to the parent financial institution record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'clearing_system_member_id': {
            'business_name': 'Clearing System Member ID',
            'business_description': 'Member identifier in the clearing system.',
            'iso_element_name': 'MemberIdentification',
            'iso_element_path': 'FinInstnId/ClrSysMmbId/MmbId',
            'iso_data_type': 'Max35Text',
        },
        'clearing_system_proprietary': {
            'business_name': 'Clearing System Proprietary',
            'business_description': 'Proprietary clearing system identifier.',
            'iso_element_name': 'Proprietary',
            'iso_element_path': 'FinInstnId/ClrSysMmbId/ClrSysId/Prtry',
            'iso_data_type': 'Max35Text',
        },
        'national_clearing_code': {
            'business_name': 'National Clearing Code',
            'business_description': 'National bank code (e.g., ABA for US, Sort Code for UK).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'national_clearing_system': {
            'business_name': 'National Clearing System',
            'business_description': 'National clearing system identifier.',
            'iso_element_name': 'Code',
            'iso_element_path': 'FinInstnId/ClrSysMmbId/ClrSysId/Cd',
            'iso_data_type': 'ExternalClearingSystemIdentification1Code',
        },
        'rssd_number': {
            'business_name': 'RSSD Number',
            'business_description': 'Research, Statistics, Supervision, and Discount ID assigned by the Federal Reserve.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'other_id': {
            'business_name': 'Other ID',
            'business_description': 'Other identifier for the financial institution.',
            'iso_element_name': 'Identification',
            'iso_element_path': 'FinInstnId/Othr/Id',
            'iso_data_type': 'Max35Text',
        },
        'other_scheme_name': {
            'business_name': 'Other Scheme Name',
            'business_description': 'Scheme name for the other identifier.',
            'iso_element_name': 'SchemeName',
            'iso_element_path': 'FinInstnId/Othr/SchmeNm/Cd',
            'iso_data_type': 'ExternalFinancialInstitutionIdentification1Code',
        },
        'other_issuer': {
            'business_name': 'Other Issuer',
            'business_description': 'Entity that issued the other identifier.',
            'iso_element_name': 'Issuer',
            'iso_element_path': 'FinInstnId/Othr/Issr',
            'iso_data_type': 'Max35Text',
        },
        'fatca_giin': {
            'business_name': 'FATCA GIIN',
            'business_description': 'Global Intermediary Identification Number for FATCA compliance.',
            'data_format': '19 characters',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'fatca_status': {
            'business_name': 'FATCA Status',
            'business_description': 'FATCA classification status of the institution.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_instruction_id': {
            'business_name': 'Source Instruction ID',
            'business_description': 'Reference to the payment instruction from which this FI was derived.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'is_current': {
            'business_name': 'Is Current',
            'business_description': 'SCD2 flag indicating if this is the current version.',
            'data_format': 'Boolean',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'is_deleted': {
            'business_name': 'Is Deleted',
            'business_description': 'Soft delete flag.',
            'data_format': 'Boolean',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'valid_from': {
            'business_name': 'Valid From',
            'business_description': 'Start of validity period for this version.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'valid_to': {
            'business_name': 'Valid To',
            'business_description': 'End of validity period for this version.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'record_version': {
            'business_name': 'Record Version',
            'business_description': 'Version number for optimistic locking.',
            'data_format': 'Integer',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },

    # ========================================================================
    # cdm_account - Account information
    # ========================================================================
    'cdm_account': {
        'account_id': {
            'business_name': 'Account ID',
            'business_description': 'Unique identifier for this account record in the Common Domain Model.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_message_type': {
            'business_name': 'Source Message Type',
            'business_description': 'Original message format from which this account information was extracted.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'role': {
            'business_name': 'Account Role',
            'business_description': 'The role of this account in the payment transaction.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'DEBTOR', 'description': 'Account being debited (source account)'},
                {'value': 'CREDITOR', 'description': 'Account being credited (destination account)'},
            ],
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'account_number': {
            'business_name': 'Account Number',
            'business_description': 'Primary account number or identifier. Format varies by country and institution.',
            'iso_element_name': 'Identification',
            'iso_element_path': 'DbtrAcct/Id/Othr/Id or CdtrAcct/Id/Othr/Id',
            'iso_data_type': 'Max34Text',
        },
        'account_type': {
            'business_name': 'Account Type',
            'business_description': 'Type of account. Uses ISO 20022 ExternalCashAccountType1Code or derived categories.',
            'data_format': 'ISO 20022 ExternalCashAccountType1Code',
            'allowed_values': [
                {'value': 'CACC', 'description': 'Current/checking account'},
                {'value': 'SVGS', 'description': 'Savings account'},
                {'value': 'LOAN', 'description': 'Loan account'},
                {'value': 'CASH', 'description': 'Cash account'},
                {'value': 'CARD', 'description': 'Card account'},
                {'value': 'OTHR', 'description': 'Other account type'},
            ],
            'iso_element_name': 'Type',
            'iso_element_path': 'DbtrAcct/Tp/Cd or CdtrAcct/Tp/Cd',
            'iso_data_type': 'ExternalCashAccountType1Code',
        },
        'currency': {
            'business_name': 'Account Currency',
            'business_description': 'ISO 4217 currency code for the account. Indicates the currency in which the account is denominated.',
            'data_format': 'ISO 4217 (3-letter code)',
            'iso_element_name': 'Currency',
            'iso_element_path': 'DbtrAcct/Ccy or CdtrAcct/Ccy',
            'iso_data_type': 'ActiveOrHistoricCurrencyCode',
        },
        'name': {
            'business_name': 'Account Name',
            'business_description': 'Name on the account, typically the account holder name.',
            'iso_element_name': 'Name',
            'iso_element_path': 'DbtrAcct/Nm or CdtrAcct/Nm',
            'iso_data_type': 'Max70Text',
        },
        'iban': {
            'business_name': 'IBAN',
            'business_description': 'International Bank Account Number (ISO 13616). A standardized international account number format for cross-border payments.',
            'data_format': 'ISO 13616 (up to 34 characters)',
            'iso_element_name': 'IBAN',
            'iso_element_path': 'DbtrAcct/Id/IBAN or CdtrAcct/Id/IBAN',
            'iso_data_type': 'IBAN2007Identifier',
        },
        'scheme_name': {
            'business_name': 'Scheme Name',
            'business_description': 'Name of the scheme or standard used for the account identification.',
            'iso_element_name': 'SchemeName',
            'iso_element_path': 'Acct/Id/Othr/SchmeNm',
            'iso_data_type': 'Max35Text',
        },
        'issuer': {
            'business_name': 'Issuer',
            'business_description': 'Entity that issued or manages the account identifier.',
            'iso_element_name': 'Issuer',
            'iso_element_path': 'Acct/Id/Othr/Issr',
            'iso_data_type': 'Max35Text',
        },
        # Additional account fields
        'account_id_other': {
            'business_name': 'Other Account ID',
            'business_description': 'Alternative account identifier when IBAN is not available.',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Acct/Id/Othr/Id',
            'iso_data_type': 'Max34Text',
        },
        'account_name': {
            'business_name': 'Account Name',
            'business_description': 'Name associated with the account, typically the account holder name.',
            'iso_element_name': 'Name',
            'iso_element_path': 'Acct/Nm',
            'iso_data_type': 'Max70Text',
        },
        'account_scheme_name': {
            'business_name': 'Account Scheme Name',
            'business_description': 'Name of the identification scheme used for the account number.',
            'iso_element_name': 'SchemeName',
            'iso_element_path': 'Acct/Id/Othr/SchmeNm/Cd',
            'iso_data_type': 'ExternalAccountIdentification1Code',
        },
        'account_scheme_issuer': {
            'business_name': 'Account Scheme Issuer',
            'business_description': 'Entity that issued the account identification scheme.',
            'iso_element_name': 'Issuer',
            'iso_element_path': 'Acct/Id/Othr/Issr',
            'iso_data_type': 'Max35Text',
        },
        'account_type_code': {
            'business_name': 'Account Type Code',
            'business_description': 'Standard code for the type of account.',
            'data_format': 'ISO 20022 ExternalCashAccountType1Code',
            'allowed_values': [
                {'value': 'CACC', 'description': 'Current/Checking Account'},
                {'value': 'SVGS', 'description': 'Savings Account'},
                {'value': 'LOAN', 'description': 'Loan Account'},
                {'value': 'CASH', 'description': 'Cash Account'},
                {'value': 'CARD', 'description': 'Card Account'},
            ],
            'iso_element_name': 'Type',
            'iso_element_path': 'Acct/Tp/Cd',
            'iso_data_type': 'ExternalCashAccountType1Code',
        },
        'account_type_proprietary': {
            'business_name': 'Account Type Proprietary',
            'business_description': 'Proprietary account type when standard codes are not applicable.',
            'iso_element_name': 'Proprietary',
            'iso_element_path': 'Acct/Tp/Prtry',
            'iso_data_type': 'Max35Text',
        },
        'account_status': {
            'business_name': 'Account Status',
            'business_description': 'Current status of the account.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'ACTIVE', 'description': 'Account is active'},
                {'value': 'CLOSED', 'description': 'Account has been closed'},
                {'value': 'DORMANT', 'description': 'Account is dormant'},
                {'value': 'FROZEN', 'description': 'Account is frozen'},
            ],
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'branch_id': {
            'business_name': 'Branch ID',
            'business_description': 'Branch identifier where the account is held.',
            'iso_element_name': 'BranchIdentification',
            'iso_element_path': 'Acct/BrnchId/Id',
            'iso_data_type': 'Max35Text',
        },
        'open_date': {
            'business_name': 'Open Date',
            'business_description': 'Date when the account was opened.',
            'data_format': 'ISO 8601 Date',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'close_date': {
            'business_name': 'Close Date',
            'business_description': 'Date when the account was closed.',
            'data_format': 'ISO 8601 Date',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'owner_id': {
            'business_name': 'Owner ID',
            'business_description': 'Foreign key to cdm_party for the account owner.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'financial_institution_id': {
            'business_name': 'Financial Institution ID',
            'business_description': 'Foreign key to cdm_financial_institution where the account is held.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'servicing_institution_bic': {
            'business_name': 'Servicing Institution BIC',
            'business_description': 'BIC of the financial institution servicing the account.',
            'data_format': 'ISO 9362',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'Acct/Svcr/FinInstnId/BICFI',
            'iso_data_type': 'BICFIIdentifier',
        },
        'proxy_type': {
            'business_name': 'Proxy Type',
            'business_description': 'Type of proxy identifier used for the account (e.g., email, phone, alias).',
            'iso_element_name': 'Type',
            'iso_element_path': 'Acct/Prxy/Tp/Cd',
            'iso_data_type': 'ExternalProxyAccountType1Code',
        },
        'proxy_id': {
            'business_name': 'Proxy ID',
            'business_description': 'Proxy identifier value (e.g., email address, phone number).',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Acct/Prxy/Id',
            'iso_data_type': 'Max2048Text',
        },
        'controlling_persons': {
            'business_name': 'Controlling Persons',
            'business_description': 'JSON array of controlling persons for the account (for CRS/FATCA reporting).',
            'data_format': 'JSON Array',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'crs_reportable_account': {
            'business_name': 'CRS Reportable Account',
            'business_description': 'Indicates if the account is reportable under Common Reporting Standard.',
            'data_format': 'Boolean',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'fatca_status': {
            'business_name': 'FATCA Status',
            'business_description': 'FATCA status of the account for US tax reporting.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'risk_rating': {
            'business_name': 'Risk Rating',
            'business_description': 'Risk rating assigned to the account.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'LOW', 'description': 'Low risk account'},
                {'value': 'MEDIUM', 'description': 'Medium risk account'},
                {'value': 'HIGH', 'description': 'High risk account'},
            ],
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'sanctions_screening_status': {
            'business_name': 'Sanctions Screening Status',
            'business_description': 'Result of sanctions screening on the account.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'CLEAR', 'description': 'No sanctions issues'},
                {'value': 'HIT', 'description': 'Potential sanctions match'},
                {'value': 'PENDING', 'description': 'Screening pending'},
            ],
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_instruction_id': {
            'business_name': 'Source Instruction ID',
            'business_description': 'Reference to the payment instruction from which this account was derived.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'is_current': {
            'business_name': 'Is Current',
            'business_description': 'SCD2 flag indicating if this is the current version.',
            'data_format': 'Boolean',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'is_deleted': {
            'business_name': 'Is Deleted',
            'business_description': 'Soft delete flag.',
            'data_format': 'Boolean',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'valid_from': {
            'business_name': 'Valid From',
            'business_description': 'Start of validity period for this version.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'valid_to': {
            'business_name': 'Valid To',
            'business_description': 'End of validity period for this version.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'record_version': {
            'business_name': 'Record Version',
            'business_description': 'Version number for optimistic locking.',
            'data_format': 'Integer',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },

    # ========================================================================
    # cdm_party_identifier - Party identification details
    # ========================================================================
    'cdm_party_identifier': {
        'identifier_id': {
            'business_name': 'Identifier Record ID',
            'business_description': 'Unique identifier for this party identifier record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'party_id': {
            'business_name': 'Parent Party ID',
            'business_description': 'Foreign key linking to the parent party record in cdm_party.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_type': {
            'business_name': 'Identifier Type',
            'business_description': 'Type of party identifier. Distinguishes between organization and private identification schemes.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'ORG_ID', 'description': 'Organisation identification'},
                {'value': 'PRVT_ID', 'description': 'Private (individual) identification'},
                {'value': 'OTHER', 'description': 'Other identification type'},
            ],
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'scheme_code': {
            'business_name': 'Scheme Code',
            'business_description': 'Code identifying the scheme used for the identification. Examples: DUNS, BIC, LEI, TXID.',
            'iso_element_name': 'Code',
            'iso_element_path': 'Id/OrgId/Othr/SchmeNm/Cd',
            'iso_data_type': 'ExternalOrganisationIdentification1Code',
        },
        'scheme_proprietary': {
            'business_name': 'Proprietary Scheme',
            'business_description': 'Proprietary scheme name when using a non-standard identification scheme.',
            'iso_element_name': 'Proprietary',
            'iso_element_path': 'Id/OrgId/Othr/SchmeNm/Prtry',
            'iso_data_type': 'Max35Text',
        },
        'identification': {
            'business_name': 'Identification Value',
            'business_description': 'The actual identification value within the scheme (e.g., the LEI number, tax ID, etc.).',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Id/OrgId/Othr/Id',
            'iso_data_type': 'Max35Text',
        },
        'issuer': {
            'business_name': 'Issuer',
            'business_description': 'Entity that issued the identification.',
            'iso_element_name': 'Issuer',
            'iso_element_path': 'Id/OrgId/Othr/Issr',
            'iso_data_type': 'Max35Text',
        },
        'lei': {
            'business_name': 'LEI',
            'business_description': 'Legal Entity Identifier (ISO 17442) for the party.',
            'data_format': 'ISO 17442 (20 characters)',
            'iso_element_name': 'LEI',
            'iso_element_path': 'Id/OrgId/LEI',
            'iso_data_type': 'LEIIdentifier',
        },
        'bic': {
            'business_name': 'BIC',
            'business_description': 'Bank Identifier Code for the party, if the party is a financial institution.',
            'data_format': 'ISO 9362 (8 or 11 characters)',
            'iso_element_name': 'AnyBIC',
            'iso_element_path': 'Id/OrgId/AnyBIC',
            'iso_data_type': 'AnyBICIdentifier',
        },
    },

    # ========================================================================
    # cdm_institution_identifier - Institution identification details
    # ========================================================================
    'cdm_institution_identifier': {
        'identifier_id': {
            'business_name': 'Identifier Record ID',
            'business_description': 'Unique identifier for this institution identifier record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'institution_id': {
            'business_name': 'Parent Institution ID',
            'business_description': 'Foreign key linking to the parent institution record in cdm_financial_institution.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_type': {
            'business_name': 'Identifier Type',
            'business_description': 'Type of institution identifier.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'BIC', 'description': 'Bank Identifier Code (SWIFT)'},
                {'value': 'CLEARING_MEMBER', 'description': 'Clearing system member ID'},
                {'value': 'LEI', 'description': 'Legal Entity Identifier'},
                {'value': 'OTHER', 'description': 'Other identifier type'},
            ],
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'clearing_system_code': {
            'business_name': 'Clearing System Code',
            'business_description': 'Code identifying the clearing system (e.g., USABA for Fedwire, USPID for CHIPS).',
            'iso_element_name': 'Code',
            'iso_element_path': 'FinInstnId/ClrSysMmbId/ClrSysId/Cd',
            'iso_data_type': 'ExternalClearingSystemIdentification1Code',
        },
        'clearing_system_proprietary': {
            'business_name': 'Proprietary Clearing System',
            'business_description': 'Proprietary clearing system identifier when not using a standard code.',
            'iso_element_name': 'Proprietary',
            'iso_element_path': 'FinInstnId/ClrSysMmbId/ClrSysId/Prtry',
            'iso_data_type': 'Max35Text',
        },
        'member_identification': {
            'business_name': 'Member Identification',
            'business_description': 'The institution member identifier within the clearing system.',
            'iso_element_name': 'MemberIdentification',
            'iso_element_path': 'FinInstnId/ClrSysMmbId/MmbId',
            'iso_data_type': 'Max35Text',
        },
        'bic': {
            'business_name': 'BIC',
            'business_description': 'Bank Identifier Code for the institution.',
            'data_format': 'ISO 9362 (8 or 11 characters)',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'FinInstnId/BICFI',
            'iso_data_type': 'BICFIIdentifier',
        },
        'lei': {
            'business_name': 'LEI',
            'business_description': 'Legal Entity Identifier for the institution.',
            'data_format': 'ISO 17442 (20 characters)',
            'iso_element_name': 'LEI',
            'iso_element_path': 'FinInstnId/LEI',
            'iso_data_type': 'LEIIdentifier',
        },
    },

    # ========================================================================
    # cdm_account_identifier - Account identification details
    # ========================================================================
    'cdm_account_identifier': {
        'identifier_id': {
            'business_name': 'Identifier Record ID',
            'business_description': 'Unique identifier for this account identifier record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'account_id': {
            'business_name': 'Parent Account ID',
            'business_description': 'Foreign key linking to the parent account record in cdm_account.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_type': {
            'business_name': 'Identifier Type',
            'business_description': 'Type of account identifier.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'IBAN', 'description': 'International Bank Account Number'},
                {'value': 'BBAN', 'description': 'Basic Bank Account Number'},
                {'value': 'OTHER', 'description': 'Other account identifier'},
            ],
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'scheme_code': {
            'business_name': 'Scheme Code',
            'business_description': 'Code identifying the account identification scheme.',
            'iso_element_name': 'Code',
            'iso_element_path': 'Acct/Id/Othr/SchmeNm/Cd',
            'iso_data_type': 'ExternalAccountIdentification1Code',
        },
        'scheme_proprietary': {
            'business_name': 'Proprietary Scheme',
            'business_description': 'Proprietary account scheme name.',
            'iso_element_name': 'Proprietary',
            'iso_element_path': 'Acct/Id/Othr/SchmeNm/Prtry',
            'iso_data_type': 'Max35Text',
        },
        'identification': {
            'business_name': 'Identification Value',
            'business_description': 'The account identifier value within the scheme.',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Acct/Id/Othr/Id',
            'iso_data_type': 'Max34Text',
        },
        'issuer': {
            'business_name': 'Issuer',
            'business_description': 'Entity that issued the account identifier.',
            'iso_element_name': 'Issuer',
            'iso_element_path': 'Acct/Id/Othr/Issr',
            'iso_data_type': 'Max35Text',
        },
        'iban': {
            'business_name': 'IBAN',
            'business_description': 'International Bank Account Number.',
            'data_format': 'ISO 13616 (up to 34 characters)',
            'iso_element_name': 'IBAN',
            'iso_element_path': 'Acct/Id/IBAN',
            'iso_data_type': 'IBAN2007Identifier',
        },
    },

    # ========================================================================
    # cdm_party_identifiers - Party identification records (plural)
    # ========================================================================
    'cdm_party_identifiers': {
        'id': {
            'business_name': 'Identifier Record ID',
            'business_description': 'Unique identifier for this party identifier record. Auto-generated primary key.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'party_id': {
            'business_name': 'Party ID',
            'business_description': 'Foreign key linking to the parent party record in cdm_party.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_type': {
            'business_name': 'Identifier Type',
            'business_description': 'Type of identification. Per ISO 20022: Distinguishes between organizational identification (OrgId) and private/individual identification (PrvtId).',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'LEI', 'description': 'Legal Entity Identifier (ISO 17442)'},
                {'value': 'BIC', 'description': 'Bank Identifier Code (ISO 9362)'},
                {'value': 'TAX_ID', 'description': 'Tax Identification Number'},
                {'value': 'NATIONAL_ID', 'description': 'National Identification Number'},
                {'value': 'PASSPORT', 'description': 'Passport Number'},
                {'value': 'DUNS', 'description': 'D-U-N-S Number'},
                {'value': 'OTHER', 'description': 'Other identification scheme'},
            ],
            'iso_element_name': 'SchemeName',
            'iso_element_path': 'Id/OrgId/Othr/SchmeNm/Cd',
            'iso_data_type': 'ExternalOrganisationIdentification1Code',
        },
        'identifier_value': {
            'business_name': 'Identifier Value',
            'business_description': 'The actual identification value within the scheme (e.g., the LEI code, tax ID number, passport number).',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Id/OrgId/Othr/Id',
            'iso_data_type': 'Max35Text',
        },
        'is_primary': {
            'business_name': 'Is Primary',
            'business_description': 'Indicates if this is the primary identifier for the party.',
            'data_format': 'Boolean',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_instruction_id': {
            'business_name': 'Source Instruction ID',
            'business_description': 'Reference to the payment instruction from which this identifier was derived.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },

    # ========================================================================
    # cdm_institution_identifiers - Financial institution identification records
    # ========================================================================
    'cdm_institution_identifiers': {
        'id': {
            'business_name': 'Identifier Record ID',
            'business_description': 'Unique identifier for this institution identifier record. Auto-generated primary key.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'financial_institution_id': {
            'business_name': 'Financial Institution ID',
            'business_description': 'Foreign key linking to the parent financial institution record in cdm_financial_institution.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_type': {
            'business_name': 'Identifier Type',
            'business_description': 'Type of financial institution identification. Per ISO 20022: BICFI (BIC for financial institutions) is the primary identifier.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'BIC', 'description': 'Bank Identifier Code (ISO 9362 BICFI)'},
                {'value': 'LEI', 'description': 'Legal Entity Identifier (ISO 17442)'},
                {'value': 'CLEARING_MEMBER_ID', 'description': 'Clearing system member identification'},
                {'value': 'ABA', 'description': 'American Bankers Association routing number'},
                {'value': 'SORT_CODE', 'description': 'UK Sort Code'},
                {'value': 'OTHER', 'description': 'Other identification scheme'},
            ],
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_value': {
            'business_name': 'Identifier Value',
            'business_description': 'The actual identification value (e.g., BIC code, ABA routing number, clearing member ID).',
            'iso_element_name': 'MemberIdentification',
            'iso_element_path': 'FinInstnId/ClrSysMmbId/MmbId',
            'iso_data_type': 'Max35Text',
        },
        'is_primary': {
            'business_name': 'Is Primary',
            'business_description': 'Indicates if this is the primary identifier for the institution.',
            'data_format': 'Boolean',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_instruction_id': {
            'business_name': 'Source Instruction ID',
            'business_description': 'Reference to the payment instruction from which this identifier was derived.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },

    # ========================================================================
    # cdm_account_identifiers - Account identification records
    # ========================================================================
    'cdm_account_identifiers': {
        'id': {
            'business_name': 'Identifier Record ID',
            'business_description': 'Unique identifier for this account identifier record. Auto-generated primary key.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'account_id': {
            'business_name': 'Account ID',
            'business_description': 'Foreign key linking to the parent account record in cdm_account.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_type': {
            'business_name': 'Identifier Type',
            'business_description': 'Type of account identification. Per ISO 20022: IBAN is preferred for international payments, with BBAN or Other as alternatives.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'IBAN', 'description': 'International Bank Account Number (ISO 13616)'},
                {'value': 'BBAN', 'description': 'Basic Bank Account Number'},
                {'value': 'UPIC', 'description': 'Universal Payment Identification Code'},
                {'value': 'OTHER', 'description': 'Other account identifier scheme'},
            ],
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_value': {
            'business_name': 'Identifier Value',
            'business_description': 'The actual account identifier value (e.g., IBAN, account number).',
            'iso_element_name': 'IBAN',
            'iso_element_path': 'Acct/Id/IBAN',
            'iso_data_type': 'IBAN2007Identifier',
        },
        'is_primary': {
            'business_name': 'Is Primary',
            'business_description': 'Indicates if this is the primary identifier for the account.',
            'data_format': 'Boolean',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_instruction_id': {
            'business_name': 'Source Instruction ID',
            'business_description': 'Reference to the payment instruction from which this identifier was derived.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },

    # ========================================================================
    # cdm_charge - Charges/fees information
    # Per ISO 20022: ChargesInformation provides details on charges related to a payment
    # ========================================================================
    'cdm_charge': {
        'charge_id': {
            'business_name': 'Charge ID',
            'business_description': 'Unique identifier for this charge record in the CDM. Auto-generated UUID.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'payment_id': {
            'business_name': 'Payment ID',
            'business_description': 'Foreign key to the payment instruction this charge applies to. Links charge to its parent payment.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'charge_type': {
            'business_name': 'Charge Type',
            'business_description': 'Per ISO 20022: Type of charge levied on the transaction. Categorizes charges (e.g., transfer fee, correspondent fee, cable charge).',
            'data_format': 'Code',
            'iso_element_name': 'Type',
            'iso_element_path': 'ChrgsInf/Tp/Cd',
            'iso_data_type': 'ExternalChargeType1Code',
        },
        'charge_bearer': {
            'business_name': 'Charge Bearer',
            'business_description': 'Per ISO 20022: Specifies which party/parties will bear the charges associated with processing of the payment transaction. Values: DEBT (debtor), CRED (creditor), SHAR (shared), SLEV (service level).',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'DEBT', 'description': 'All charges borne by debtor (OUR)'},
                {'value': 'CRED', 'description': 'All charges borne by creditor (BEN)'},
                {'value': 'SHAR', 'description': 'Charges shared between debtor and creditor (SHA)'},
                {'value': 'SLEV', 'description': 'Following service level defined between agents'},
            ],
            'iso_element_name': 'ChargeBearer',
            'iso_element_path': 'ChrgBr',
            'iso_data_type': 'ChargeBearerType1Code',
        },
        'amount': {
            'business_name': 'Charge Amount',
            'business_description': 'Per ISO 20022: Transaction charges to be paid by the charge bearer. The monetary value of this specific charge.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'Amount',
            'iso_element_path': 'ChrgsInf/Amt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'currency': {
            'business_name': 'Charge Currency',
            'business_description': 'ISO 4217 currency code of the charge amount. May differ from payment currency.',
            'data_format': 'ISO 4217 (3-letter code)',
            'iso_element_name': 'Currency',
            'iso_element_path': 'ChrgsInf/Amt/@Ccy',
            'iso_data_type': 'ActiveOrHistoricCurrencyCode',
        },
        'agent_id': {
            'business_name': 'Charging Agent ID',
            'business_description': 'Foreign key to the financial institution that levied this charge. Links to cdm_financial_institution.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'charge_reason': {
            'business_name': 'Charge Reason',
            'business_description': 'Per ISO 20022: Additional information about the nature of the charge or its purpose.',
            'data_format': 'Text, max 140 characters',
            'iso_element_name': 'Reason',
            'iso_element_path': 'ChrgsInf/Rsn',
            'iso_data_type': 'Max140Text',
        },
        'charge_date': {
            'business_name': 'Charge Date',
            'business_description': 'Date on which the charge was applied or is effective.',
            'data_format': 'ISO 8601 Date (YYYY-MM-DD)',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_system': {
            'business_name': 'Source System',
            'business_description': 'System from which this charge record originated. Used for audit and traceability.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'created_at': {
            'business_name': 'Created At',
            'business_description': 'Timestamp when this charge record was created in the CDM.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'record_version': {
            'business_name': 'Record Version',
            'business_description': 'Version number for optimistic concurrency control. Incremented on each update.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },

    # ========================================================================
    # cdm_settlement - Settlement information
    # Per ISO 20022: SettlementInformation provides details on how payment will be settled
    # ========================================================================
    'cdm_settlement': {
        'settlement_id': {
            'business_name': 'Settlement ID',
            'business_description': 'Unique identifier for this settlement record in the CDM. Auto-generated UUID.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'payment_id': {
            'business_name': 'Payment ID',
            'business_description': 'Foreign key to the payment instruction being settled. Links settlement record to its parent payment.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'settlement_date': {
            'business_name': 'Settlement Date',
            'business_description': 'Per ISO 20022: Date on which the amount of money ceases to be available to the agent that owes it and when the amount of money becomes available to the agent to which it is due.',
            'data_format': 'ISO 8601 Date (YYYY-MM-DD)',
            'iso_element_name': 'InterbankSettlementDate',
            'iso_element_path': 'IntrBkSttlmDt',
            'iso_data_type': 'ISODate',
        },
        'settlement_amount': {
            'business_name': 'Settlement Amount',
            'business_description': 'Per ISO 20022: Amount of money to be moved between the instructing agent and the instructed agent. This is the interbank settlement amount.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'InterbankSettlementAmount',
            'iso_element_path': 'IntrBkSttlmAmt',
            'iso_data_type': 'ActiveCurrencyAndAmount',
        },
        'settlement_currency': {
            'business_name': 'Settlement Currency',
            'business_description': 'ISO 4217 currency code in which the settlement amount is expressed.',
            'data_format': 'ISO 4217 (3-letter code)',
            'iso_element_name': 'Currency',
            'iso_element_path': 'IntrBkSttlmAmt/@Ccy',
            'iso_data_type': 'ActiveCurrencyCode',
        },
        'settlement_method': {
            'business_name': 'Settlement Method',
            'business_description': 'Per ISO 20022: Method used to settle the credit transfer instruction. Specifies how the interbank settlement will be effected.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'INDA', 'description': 'InstructedAgent - settle through instructed agent (debtor agent)'},
                {'value': 'INGA', 'description': 'InstructingAgent - settle through instructing agent'},
                {'value': 'COVE', 'description': 'CoverMethod - settlement via cover payment (MT202COV)'},
                {'value': 'CLRG', 'description': 'ClearingSystem - settlement through clearing system'},
            ],
            'iso_element_name': 'SettlementMethod',
            'iso_element_path': 'SttlmInf/SttlmMtd',
            'iso_data_type': 'SettlementMethod1Code',
        },
        'settlement_status': {
            'business_name': 'Settlement Status',
            'business_description': 'Current status of the settlement. Indicates whether settlement has been completed, is pending, or has failed.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'PEND', 'description': 'Pending - settlement not yet completed'},
                {'value': 'COMP', 'description': 'Completed - settlement finalized'},
                {'value': 'FAIL', 'description': 'Failed - settlement could not be completed'},
            ],
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'clearing_system_code': {
            'business_name': 'Clearing System Code',
            'business_description': 'Per ISO 20022: Identification of the clearing system (e.g., CHAPS, TARGET2, FEDWIRE, CHIPS) used for settlement.',
            'data_format': 'ISO 20022 External Code',
            'iso_element_name': 'Code',
            'iso_element_path': 'SttlmInf/ClrSys/Cd',
            'iso_data_type': 'ExternalClearingSystemIdentification1Code',
        },
        'settlement_cycle': {
            'business_name': 'Settlement Cycle',
            'business_description': 'Settlement cycle in which this transaction was processed (e.g., T+0, T+1, T+2).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'interbank_settlement_date': {
            'business_name': 'Interbank Settlement Date',
            'business_description': 'Per ISO 20022: Date on which the amount of money ceases to be available to the agent that owes it. Same as settlement_date in most cases.',
            'data_format': 'ISO 8601 Date (YYYY-MM-DD)',
            'iso_element_name': 'InterbankSettlementDate',
            'iso_element_path': 'IntrBkSttlmDt',
            'iso_data_type': 'ISODate',
        },
        'interbank_settlement_amount': {
            'business_name': 'Interbank Settlement Amount',
            'business_description': 'Per ISO 20022: Amount of money to be moved between the instructing agent and instructed agent. This may differ from instructed amount due to currency conversion or fee deduction.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'InterbankSettlementAmount',
            'iso_element_path': 'IntrBkSttlmAmt',
            'iso_data_type': 'ActiveCurrencyAndAmount',
        },
        'interbank_settlement_currency': {
            'business_name': 'Interbank Settlement Currency',
            'business_description': 'ISO 4217 currency code for the interbank settlement amount.',
            'data_format': 'ISO 4217 (3-letter code)',
            'iso_element_name': 'Currency',
            'iso_element_path': 'IntrBkSttlmAmt/@Ccy',
            'iso_data_type': 'ActiveCurrencyCode',
        },
        'settlement_account_id': {
            'business_name': 'Settlement Account ID',
            'business_description': 'Identifier of the account used for settlement. May reference a nostro/vostro account.',
            'iso_element_name': 'IBAN',
            'iso_element_path': 'SttlmInf/SttlmAcct/Id/IBAN',
            'iso_data_type': 'IBAN2007Identifier',
        },
        'settlement_reference': {
            'business_name': 'Settlement Reference',
            'business_description': 'Reference assigned by the settlement system to this settlement transaction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'batch_id': {
            'business_name': 'Batch ID',
            'business_description': 'Identifier of the batch in which this settlement was processed, if applicable.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'netting_indicator': {
            'business_name': 'Netting Indicator',
            'business_description': 'Indicates whether this settlement was part of a netted batch. TRUE if amounts were netted with other transactions.',
            'data_format': 'Boolean',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_system': {
            'business_name': 'Source System',
            'business_description': 'System from which this settlement record originated.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'partition_year': {
            'business_name': 'Partition Year',
            'business_description': 'Year component for table partitioning. Derived from settlement date.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'partition_month': {
            'business_name': 'Partition Month',
            'business_description': 'Month component for table partitioning. Derived from settlement date.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'created_at': {
            'business_name': 'Created At',
            'business_description': 'Timestamp when this settlement record was created in the CDM.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'updated_at': {
            'business_name': 'Updated At',
            'business_description': 'Timestamp of the last update to this settlement record.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'record_version': {
            'business_name': 'Record Version',
            'business_description': 'Version number for optimistic concurrency control. Incremented on each update.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },

    # ========================================================================
    # cdm_remittance_information - Remittance details
    # Per ISO 20022: RemittanceInformation enables matching/reconciliation with items the payment settles
    # ========================================================================
    'cdm_remittance_information': {
        'remittance_id': {
            'business_name': 'Remittance ID',
            'business_description': 'Unique identifier for this remittance information record in the CDM. Auto-generated UUID.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'payment_id': {
            'business_name': 'Payment ID',
            'business_description': 'Foreign key to the payment instruction this remittance information relates to.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'unstructured': {
            'business_name': 'Unstructured Remittance',
            'business_description': 'Per ISO 20022: Information supplied to enable the matching/reconciliation of an entry with the items that the payment is intended to settle, such as commercial invoices in an Accounts Receivable system, in an unstructured form. Array of free-form text lines.',
            'data_format': 'Array of text, max 140 characters per line',
            'iso_element_name': 'Unstructured',
            'iso_element_path': 'RmtInf/Ustrd',
            'iso_data_type': 'Max140Text',
        },
        'document_type_code': {
            'business_name': 'Document Type Code',
            'business_description': 'Per ISO 20022: Code specifying the type of referred document (e.g., CINV=Commercial Invoice, CREN=Credit Note, DEBN=Debit Note).',
            'data_format': 'Code',
            'iso_element_name': 'Code',
            'iso_element_path': 'RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd',
            'iso_data_type': 'DocumentType6Code',
        },
        'document_type_proprietary': {
            'business_name': 'Document Type Proprietary',
            'business_description': 'Per ISO 20022: Proprietary identification of the document type when a standard code is not available.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'Proprietary',
            'iso_element_path': 'RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Prtry',
            'iso_data_type': 'Max35Text',
        },
        'document_number': {
            'business_name': 'Document Number',
            'business_description': 'Per ISO 20022: Unique identification number of the referred document (e.g., invoice number INV-2025-001).',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'Number',
            'iso_element_path': 'RmtInf/Strd/RfrdDocInf/Nb',
            'iso_data_type': 'Max35Text',
        },
        'document_related_date': {
            'business_name': 'Document Related Date',
            'business_description': 'Per ISO 20022: Date associated with the document, such as the date the document was issued.',
            'data_format': 'ISO 8601 Date (YYYY-MM-DD)',
            'iso_element_name': 'RelatedDate',
            'iso_element_path': 'RmtInf/Strd/RfrdDocInf/RltdDt',
            'iso_data_type': 'ISODate',
        },
        'document_line_details': {
            'business_name': 'Document Line Details',
            'business_description': 'Per ISO 20022: Set of elements used to provide details on the amounts of the referred document, including line item details for partial payments.',
            'data_format': 'JSON object',
            'iso_element_name': 'ReferredDocumentAmount',
            'iso_element_path': 'RmtInf/Strd/RfrdDocAmt',
            'iso_data_type': 'RemittanceAmount3',
        },
        'due_payable_amount': {
            'business_name': 'Due Payable Amount',
            'business_description': 'Per ISO 20022: Amount specified is the exact amount due and payable to the creditor.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'DuePayableAmount',
            'iso_element_path': 'RmtInf/Strd/RfrdDocAmt/DuePyblAmt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'due_payable_currency': {
            'business_name': 'Due Payable Currency',
            'business_description': 'ISO 4217 currency code for the due payable amount.',
            'data_format': 'ISO 4217 (3-letter code)',
            'iso_element_name': 'Currency',
            'iso_element_path': 'RmtInf/Strd/RfrdDocAmt/DuePyblAmt/@Ccy',
            'iso_data_type': 'ActiveOrHistoricCurrencyCode',
        },
        'discount_applied_amount': {
            'business_name': 'Discount Applied Amount',
            'business_description': 'Per ISO 20022: Amount of discount applied to the original due amount.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'DiscountAppliedAmount',
            'iso_element_path': 'RmtInf/Strd/RfrdDocAmt/DscntApldAmt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'credit_note_amount': {
            'business_name': 'Credit Note Amount',
            'business_description': 'Per ISO 20022: Amount specified on a credit note relating to the referred document.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'CreditNoteAmount',
            'iso_element_path': 'RmtInf/Strd/RfrdDocAmt/CdtNoteAmt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'tax_amount': {
            'business_name': 'Tax Amount',
            'business_description': 'Per ISO 20022: Amount of money due to government or tax authority according to a specific tax regime.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'TaxAmount',
            'iso_element_path': 'RmtInf/Strd/RfrdDocAmt/TaxAmt',
            'iso_data_type': 'TaxAmountAndType1',
        },
        'remitted_amount': {
            'business_name': 'Remitted Amount',
            'business_description': 'Per ISO 20022: Amount of money remitted for the document. This is the amount actually being paid by this transaction.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'RemittedAmount',
            'iso_element_path': 'RmtInf/Strd/RfrdDocAmt/RmtdAmt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'remitted_currency': {
            'business_name': 'Remitted Currency',
            'business_description': 'ISO 4217 currency code for the remitted amount.',
            'data_format': 'ISO 4217 (3-letter code)',
            'iso_element_name': 'Currency',
            'iso_element_path': 'RmtInf/Strd/RfrdDocAmt/RmtdAmt/@Ccy',
            'iso_data_type': 'ActiveOrHistoricCurrencyCode',
        },
        'creditor_reference_type': {
            'business_name': 'Creditor Reference Type',
            'business_description': 'Per ISO 20022: Specifies the type of creditor reference (e.g., structured creditor reference as per ISO 11649).',
            'data_format': 'Code',
            'iso_element_name': 'Type',
            'iso_element_path': 'RmtInf/Strd/CdtrRefInf/Tp/CdOrPrtry/Cd',
            'iso_data_type': 'DocumentType3Code',
        },
        'creditor_reference': {
            'business_name': 'Creditor Reference',
            'business_description': 'Per ISO 20022: Unique reference, assigned by the creditor, to unambiguously refer to the payment transaction. Also known as Structured Creditor Reference (RF reference per ISO 11649).',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'Reference',
            'iso_element_path': 'RmtInf/Strd/CdtrRefInf/Ref',
            'iso_data_type': 'Max35Text',
        },
        'invoicer_name': {
            'business_name': 'Invoicer Name',
            'business_description': 'Per ISO 20022: Name of the party issuing the referred document (e.g., the vendor who issued the invoice).',
            'data_format': 'Text, max 140 characters',
            'iso_element_name': 'Name',
            'iso_element_path': 'RmtInf/Strd/Invcr/Nm',
            'iso_data_type': 'Max140Text',
        },
        'invoicee_name': {
            'business_name': 'Invoicee Name',
            'business_description': 'Per ISO 20022: Name of the party receiving the referred document (e.g., the customer who received the invoice).',
            'data_format': 'Text, max 140 characters',
            'iso_element_name': 'Name',
            'iso_element_path': 'RmtInf/Strd/Invcee/Nm',
            'iso_data_type': 'Max140Text',
        },
        'additional_info': {
            'business_name': 'Additional Remittance Information',
            'business_description': 'Per ISO 20022: Additional information, in free text form, to complement the structured remittance information.',
            'data_format': 'Text, max 140 characters',
            'iso_element_name': 'AdditionalRemittanceInformation',
            'iso_element_path': 'RmtInf/Strd/AddtlRmtInf',
            'iso_data_type': 'Max140Text',
        },
        'source_system': {
            'business_name': 'Source System',
            'business_description': 'System from which this remittance information originated.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_message_type': {
            'business_name': 'Source Message Type',
            'business_description': 'Original message format from which this remittance information was extracted.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_stg_id': {
            'business_name': 'Source Staging ID',
            'business_description': 'Reference to the Silver layer staging record from which this was derived.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'created_at': {
            'business_name': 'Created At',
            'business_description': 'Timestamp when this remittance information record was created in the CDM.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'record_version': {
            'business_name': 'Record Version',
            'business_description': 'Version number for optimistic concurrency control. Incremented on each update.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },

    # ========================================================================
    # cdm_regulatory_reporting - Regulatory reporting information
    # Per ISO 20022: RegulatoryReporting provides information for regulatory authorities
    # ========================================================================
    'cdm_regulatory_reporting': {
        'reporting_id': {
            'business_name': 'Reporting ID',
            'business_description': 'Unique identifier for this regulatory reporting record in the CDM. Auto-generated UUID.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'payment_id': {
            'business_name': 'Payment ID',
            'business_description': 'Foreign key to the payment instruction this regulatory report relates to.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'authority_name': {
            'business_name': 'Authority Name',
            'business_description': 'Per ISO 20022: Name of the financial or regulatory authority to which information must be reported.',
            'data_format': 'Text, max 140 characters',
            'iso_element_name': 'Name',
            'iso_element_path': 'RgltryRptg/Authrty/Nm',
            'iso_data_type': 'Max140Text',
        },
        'authority_country': {
            'business_name': 'Authority Country',
            'business_description': 'Per ISO 20022: Country of the regulatory authority requiring this report. ISO 3166-1 alpha-2 country code.',
            'data_format': 'ISO 3166-1 alpha-2 (2-letter code)',
            'iso_element_name': 'Country',
            'iso_element_path': 'RgltryRptg/Authrty/Ctry',
            'iso_data_type': 'CountryCode',
        },
        'reporting_type': {
            'business_name': 'Reporting Type',
            'business_description': 'Per ISO 20022: Identifies whether the regulatory reporting information applies to the debit side, credit side, or both sides of the transaction.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'CRDT', 'description': 'Credit - reporting for credit/receiving side'},
                {'value': 'DEBT', 'description': 'Debit - reporting for debit/sending side'},
                {'value': 'BOTH', 'description': 'Both - reporting for both sides'},
            ],
            'iso_element_name': 'DebitCreditReportingIndicator',
            'iso_element_path': 'RgltryRptg/DbtCdtRptgInd',
            'iso_data_type': 'RegulatoryReportingType1Code',
        },
        'reporting_date': {
            'business_name': 'Reporting Date',
            'business_description': 'Date to which the regulatory information applies.',
            'data_format': 'ISO 8601 Date (YYYY-MM-DD)',
            'iso_element_name': 'Date',
            'iso_element_path': 'RgltryRptg/Dtls/Dt',
            'iso_data_type': 'ISODate',
        },
        'reporting_country': {
            'business_name': 'Reporting Country',
            'business_description': 'Per ISO 20022: Country related to the regulatory requirement. May indicate country of origin or destination.',
            'data_format': 'ISO 3166-1 alpha-2 (2-letter code)',
            'iso_element_name': 'Country',
            'iso_element_path': 'RgltryRptg/Dtls/Ctry',
            'iso_data_type': 'CountryCode',
        },
        'reporting_code': {
            'business_name': 'Reporting Code',
            'business_description': 'Per ISO 20022: Code specifying the nature of the regulatory reporting details (e.g., balance of payments code, tax reporting code).',
            'data_format': 'Text, max 10 characters',
            'iso_element_name': 'Code',
            'iso_element_path': 'RgltryRptg/Dtls/Cd',
            'iso_data_type': 'Max10Text',
        },
        'reporting_amount': {
            'business_name': 'Reporting Amount',
            'business_description': 'Per ISO 20022: Amount of money to be reported to the regulatory authority.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'Amount',
            'iso_element_path': 'RgltryRptg/Dtls/Amt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'reporting_currency': {
            'business_name': 'Reporting Currency',
            'business_description': 'ISO 4217 currency code for the reported amount.',
            'data_format': 'ISO 4217 (3-letter code)',
            'iso_element_name': 'Currency',
            'iso_element_path': 'RgltryRptg/Dtls/Amt/@Ccy',
            'iso_data_type': 'ActiveOrHistoricCurrencyCode',
        },
        'reporting_information': {
            'business_name': 'Reporting Information',
            'business_description': 'Per ISO 20022: Additional details of the regulatory reporting, in free text form.',
            'data_format': 'Text, max 35 characters per occurrence',
            'iso_element_name': 'Information',
            'iso_element_path': 'RgltryRptg/Dtls/Inf',
            'iso_data_type': 'Max35Text',
        },
        'source_system': {
            'business_name': 'Source System',
            'business_description': 'System from which this regulatory reporting record originated.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_message_type': {
            'business_name': 'Source Message Type',
            'business_description': 'Original message format from which this regulatory information was extracted.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_stg_id': {
            'business_name': 'Source Staging ID',
            'business_description': 'Reference to the Silver layer staging record from which this was derived.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'created_at': {
            'business_name': 'Created At',
            'business_description': 'Timestamp when this regulatory reporting record was created in the CDM.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'record_version': {
            'business_name': 'Record Version',
            'business_description': 'Version number for optimistic concurrency control. Incremented on each update.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },

    # ========================================================================
    # cdm_payment_status - Payment status tracking
    # Per ISO 20022: pacs.002 PaymentStatusReport provides status information on payments
    # ========================================================================
    'cdm_payment_status': {
        'status_id': {
            'business_name': 'Status Record ID',
            'business_description': 'Unique identifier for this payment status record in the CDM. Auto-generated UUID.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'payment_id': {
            'business_name': 'Payment ID',
            'business_description': 'Foreign key to the payment instruction this status relates to.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'original_message_id': {
            'business_name': 'Original Message ID',
            'business_description': 'Per ISO 20022: Point to point reference, as assigned by the original instructing party, to unambiguously identify the original message.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'OriginalMessageIdentification',
            'iso_element_path': 'OrgnlGrpInfAndSts/OrgnlMsgId',
            'iso_data_type': 'Max35Text',
        },
        'original_message_name_id': {
            'business_name': 'Original Message Name ID',
            'business_description': 'Per ISO 20022: Specifies the original message name identifier to which the message refers (e.g., pain.001.001.03, pacs.008.001.02).',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'OriginalMessageNameIdentification',
            'iso_element_path': 'OrgnlGrpInfAndSts/OrgnlMsgNmId',
            'iso_data_type': 'Max35Text',
        },
        'original_end_to_end_id': {
            'business_name': 'Original End-to-End ID',
            'business_description': 'Per ISO 20022: Unique end-to-end reference assigned by the instructing party in the original transaction.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'OriginalEndToEndIdentification',
            'iso_element_path': 'TxInfAndSts/OrgnlEndToEndId',
            'iso_data_type': 'Max35Text',
        },
        'original_transaction_id': {
            'business_name': 'Original Transaction ID',
            'business_description': 'Per ISO 20022: Unique identification, as assigned by the original first instructing agent, to unambiguously identify the transaction.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'OriginalTransactionIdentification',
            'iso_element_path': 'TxInfAndSts/OrgnlTxId',
            'iso_data_type': 'Max35Text',
        },
        'original_uetr': {
            'business_name': 'Original UETR',
            'business_description': 'Per ISO 20022: Universally unique identifier to provide an end-to-end reference of a payment transaction. Original UETR from the instruction being reported on.',
            'data_format': 'UUID format (36 characters)',
            'iso_element_name': 'UETR',
            'iso_element_path': 'TxInfAndSts/OrgnlUETR',
            'iso_data_type': 'UUIDv4Identifier',
        },
        'group_status': {
            'business_name': 'Group Status',
            'business_description': 'Per ISO 20022: Specifies the status of the payment information group as a whole.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'ACTC', 'description': 'AcceptedTechnicalValidation - Authentication and syntactical validation passed'},
                {'value': 'ACCP', 'description': 'AcceptedCustomerProfile - Preceding check passed'},
                {'value': 'ACSP', 'description': 'AcceptedSettlementInProcess - All preceding checks passed, settlement in process'},
                {'value': 'ACSC', 'description': 'AcceptedSettlementCompleted - Settlement completed'},
                {'value': 'RJCT', 'description': 'Rejected - Payment initiation rejected'},
                {'value': 'PART', 'description': 'PartiallyAccepted - Some transactions accepted, others rejected'},
            ],
            'iso_element_name': 'GroupStatus',
            'iso_element_path': 'OrgnlGrpInfAndSts/GrpSts',
            'iso_data_type': 'ExternalPaymentGroupStatus1Code',
        },
        'transaction_status': {
            'business_name': 'Transaction Status',
            'business_description': 'Per ISO 20022: Specifies the status of the transaction within a group or as individual payment.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'ACCP', 'description': 'AcceptedCustomerProfile - Payment accepted'},
                {'value': 'ACSC', 'description': 'AcceptedSettlementCompleted - Settlement completed'},
                {'value': 'ACSP', 'description': 'AcceptedSettlementInProcess - Settlement in process'},
                {'value': 'ACTC', 'description': 'AcceptedTechnicalValidation - Technical validation passed'},
                {'value': 'ACWC', 'description': 'AcceptedWithChange - Accepted with modification'},
                {'value': 'PDNG', 'description': 'Pending - Payment is pending'},
                {'value': 'RJCT', 'description': 'Rejected - Payment rejected'},
            ],
            'iso_element_name': 'TransactionStatus',
            'iso_element_path': 'TxInfAndSts/TxSts',
            'iso_data_type': 'ExternalPaymentTransactionStatus1Code',
        },
        'status_reason_code': {
            'business_name': 'Status Reason Code',
            'business_description': 'Per ISO 20022: Reason code for the status. Standard ISO 20022 external reason codes (e.g., AC01=Incorrect Account Number, AM04=Insufficient Funds).',
            'data_format': 'ISO 20022 External Code',
            'iso_element_name': 'Code',
            'iso_element_path': 'TxInfAndSts/StsRsnInf/Rsn/Cd',
            'iso_data_type': 'ExternalStatusReason1Code',
        },
        'status_reason_proprietary': {
            'business_name': 'Status Reason Proprietary',
            'business_description': 'Per ISO 20022: Proprietary reason code for the status when a standard code is not available.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'Proprietary',
            'iso_element_path': 'TxInfAndSts/StsRsnInf/Rsn/Prtry',
            'iso_data_type': 'Max35Text',
        },
        'additional_status_info': {
            'business_name': 'Additional Status Information',
            'business_description': 'Per ISO 20022: Further details on the status reason. Free-text explanation of why the payment was rejected or is pending.',
            'data_format': 'Text, max 105 characters',
            'iso_element_name': 'AdditionalInformation',
            'iso_element_path': 'TxInfAndSts/StsRsnInf/AddtlInf',
            'iso_data_type': 'Max105Text',
        },
        'acceptance_datetime': {
            'business_name': 'Acceptance DateTime',
            'business_description': 'Per ISO 20022: Date and time at which the status was assigned to the payment. Timestamp when the status was recorded.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': 'AcceptanceDateTime',
            'iso_element_path': 'TxInfAndSts/AccptncDtTm',
            'iso_data_type': 'ISODateTime',
        },
        'tracker_reason_code': {
            'business_name': 'Tracker Reason Code',
            'business_description': 'SWIFT gpi tracker-specific reason code providing additional status information for cross-border payments tracked via gpi.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_system': {
            'business_name': 'Source System',
            'business_description': 'System from which this payment status record originated.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_message_type': {
            'business_name': 'Source Message Type',
            'business_description': 'Original message format from which this status was extracted (e.g., pacs.002, MT199).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_stg_id': {
            'business_name': 'Source Staging ID',
            'business_description': 'Reference to the Silver layer staging record from which this status was derived.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'created_at': {
            'business_name': 'Created At',
            'business_description': 'Timestamp when this payment status record was created in the CDM.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'record_version': {
            'business_name': 'Record Version',
            'business_description': 'Version number for optimistic concurrency control. Incremented on each update.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },

    # ========================================================================
    # cdm_pain_customer_credit_transfer_initiation - ISO 20022 pain.001
    # CustomerCreditTransferInitiation - Payment initiation from customer to bank
    # ========================================================================
    'cdm_pain_customer_credit_transfer_initiation': {
        'initiation_id': {
            'business_name': 'Initiation ID',
            'business_description': 'Unique identifier for this credit transfer initiation record in the CDM.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_stg_id': {
            'business_name': 'Source Staging ID',
            'business_description': 'Reference to the Silver layer staging record from which this was derived.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_stg_table': {
            'business_name': 'Source Staging Table',
            'business_description': 'Name of the Silver staging table from which this record was derived.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_format': {
            'business_name': 'Source Format',
            'business_description': 'Original message format identifier (e.g., pain.001.001.03).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'message_id': {
            'business_name': 'Message Identification',
            'business_description': 'Per ISO 20022 pain.001: Point to point reference, as assigned by the instructing party, and sent to the next party in the chain to unambiguously identify the message.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'MessageIdentification',
            'iso_element_path': 'GrpHdr/MsgId',
            'iso_data_type': 'Max35Text',
        },
        'creation_datetime': {
            'business_name': 'Creation Date Time',
            'business_description': 'Per ISO 20022: Date and time at which the message was created.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': 'CreationDateTime',
            'iso_element_path': 'GrpHdr/CreDtTm',
            'iso_data_type': 'ISODateTime',
        },
        'initiating_party_name': {
            'business_name': 'Initiating Party Name',
            'business_description': 'Per ISO 20022: Name of the party initiating the payment. This is the entity (organization or individual) that sends the payment instruction to the bank.',
            'data_format': 'Text, max 140 characters',
            'iso_element_name': 'Name',
            'iso_element_path': 'GrpHdr/InitgPty/Nm',
            'iso_data_type': 'Max140Text',
        },
        'payment_info_id': {
            'business_name': 'Payment Information Identification',
            'business_description': 'Per ISO 20022: Unique identification, as assigned by a sending party, to unambiguously identify the payment information group.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'PaymentInformationIdentification',
            'iso_element_path': 'PmtInf/PmtInfId',
            'iso_data_type': 'Max35Text',
        },
        'payment_method': {
            'business_name': 'Payment Method',
            'business_description': 'Per ISO 20022: Specifies the means of payment that will be used to move the amount of money.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'CHK', 'description': 'Cheque'},
                {'value': 'TRF', 'description': 'Credit Transfer'},
                {'value': 'TRA', 'description': 'Transfer Advice'},
            ],
            'iso_element_name': 'PaymentMethod',
            'iso_element_path': 'PmtInf/PmtMtd',
            'iso_data_type': 'PaymentMethod3Code',
        },
        'batch_booking': {
            'business_name': 'Batch Booking',
            'business_description': 'Per ISO 20022: Identifies whether a single entry per individual transaction or a batch entry for the sum of amounts is requested.',
            'data_format': 'Boolean',
            'iso_element_name': 'BatchBooking',
            'iso_element_path': 'PmtInf/BtchBookg',
            'iso_data_type': 'BatchBookingIndicator',
        },
        'number_of_transactions': {
            'business_name': 'Number of Transactions',
            'business_description': 'Per ISO 20022: Number of individual transactions contained in the payment information group.',
            'data_format': 'Integer, max 15 digits',
            'iso_element_name': 'NumberOfTransactions',
            'iso_element_path': 'PmtInf/NbOfTxs',
            'iso_data_type': 'Max15NumericText',
        },
        'control_sum': {
            'business_name': 'Control Sum',
            'business_description': 'Per ISO 20022: Total of all individual amounts included in the message, irrespective of currencies. Used for validation.',
            'data_format': 'Decimal with up to 17 digits',
            'iso_element_name': 'ControlSum',
            'iso_element_path': 'PmtInf/CtrlSum',
            'iso_data_type': 'DecimalNumber',
        },
        'requested_execution_date': {
            'business_name': 'Requested Execution Date',
            'business_description': 'Per ISO 20022: Date at which the initiating party requests the clearing agent to process the payment.',
            'data_format': 'ISO 8601 Date (YYYY-MM-DD)',
            'iso_element_name': 'RequestedExecutionDate',
            'iso_element_path': 'PmtInf/ReqdExctnDt',
            'iso_data_type': 'ISODate',
        },
        'service_level_code': {
            'business_name': 'Service Level Code',
            'business_description': 'Per ISO 20022: Agreement under which the transaction should be processed (e.g., SEPA, URGP=Urgent Payment).',
            'data_format': 'Code',
            'iso_element_name': 'Code',
            'iso_element_path': 'PmtInf/PmtTpInf/SvcLvl/Cd',
            'iso_data_type': 'ExternalServiceLevel1Code',
        },
        'local_instrument_code': {
            'business_name': 'Local Instrument Code',
            'business_description': 'Per ISO 20022: Specifies the local instrument, as published in an external local instrument code list.',
            'data_format': 'Code',
            'iso_element_name': 'Code',
            'iso_element_path': 'PmtInf/PmtTpInf/LclInstrm/Cd',
            'iso_data_type': 'ExternalLocalInstrument1Code',
        },
        'category_purpose_code': {
            'business_name': 'Category Purpose Code',
            'business_description': 'Per ISO 20022: Specifies the high level purpose of the instruction (e.g., CASH=Cash Management Transfer, SALA=Salary Payment).',
            'data_format': 'Code',
            'iso_element_name': 'Code',
            'iso_element_path': 'PmtInf/PmtTpInf/CtgyPurp/Cd',
            'iso_data_type': 'ExternalCategoryPurpose1Code',
        },
        'debtor_name': {
            'business_name': 'Debtor Name',
            'business_description': 'Per ISO 20022: Party that owes an amount of money to the (ultimate) creditor. Name of the paying party.',
            'data_format': 'Text, max 140 characters',
            'iso_element_name': 'Name',
            'iso_element_path': 'PmtInf/Dbtr/Nm',
            'iso_data_type': 'Max140Text',
        },
        'debtor_address_country': {
            'business_name': 'Debtor Country',
            'business_description': 'Per ISO 20022: Country of residence or incorporation of the debtor.',
            'data_format': 'ISO 3166-1 alpha-2 (2-letter code)',
            'iso_element_name': 'Country',
            'iso_element_path': 'PmtInf/Dbtr/PstlAdr/Ctry',
            'iso_data_type': 'CountryCode',
        },
        'debtor_account_iban': {
            'business_name': 'Debtor Account IBAN',
            'business_description': 'Per ISO 20022: International Bank Account Number (IBAN) of the debtor account to be debited.',
            'data_format': 'ISO 13616 IBAN format',
            'iso_element_name': 'IBAN',
            'iso_element_path': 'PmtInf/DbtrAcct/Id/IBAN',
            'iso_data_type': 'IBAN2007Identifier',
        },
        'debtor_agent_bic': {
            'business_name': 'Debtor Agent BIC',
            'business_description': 'Per ISO 20022: Bank Identifier Code (BIC/SWIFT code) of the debtor financial institution.',
            'data_format': 'ISO 9362 BIC (8 or 11 characters)',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'PmtInf/DbtrAgt/FinInstnId/BICFI',
            'iso_data_type': 'BICFIIdentifier',
        },
        'instruction_id': {
            'business_name': 'Instruction Identification',
            'business_description': 'Per ISO 20022: Unique identification as assigned by an instructing party for an instructed party to unambiguously identify the instruction.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'InstructionIdentification',
            'iso_element_path': 'PmtInf/CdtTrfTxInf/PmtId/InstrId',
            'iso_data_type': 'Max35Text',
        },
        'end_to_end_id': {
            'business_name': 'End to End Identification',
            'business_description': 'Per ISO 20022: Unique identification assigned by the initiating party to unambiguously identify the transaction. This identification is passed on, unchanged, throughout the entire end-to-end chain.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'EndToEndIdentification',
            'iso_element_path': 'PmtInf/CdtTrfTxInf/PmtId/EndToEndId',
            'iso_data_type': 'Max35Text',
        },
        'instructed_amount': {
            'business_name': 'Instructed Amount',
            'business_description': 'Per ISO 20022: Amount of money to be moved between the debtor and creditor, before deduction of charges, expressed in the currency as ordered by the initiating party.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'InstructedAmount',
            'iso_element_path': 'PmtInf/CdtTrfTxInf/Amt/InstdAmt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'instructed_currency': {
            'business_name': 'Instructed Currency',
            'business_description': 'ISO 4217 currency code of the instructed amount.',
            'data_format': 'ISO 4217 (3-letter code)',
            'iso_element_name': 'Currency',
            'iso_element_path': 'PmtInf/CdtTrfTxInf/Amt/InstdAmt/@Ccy',
            'iso_data_type': 'ActiveOrHistoricCurrencyCode',
        },
        'charge_bearer': {
            'business_name': 'Charge Bearer',
            'business_description': 'Per ISO 20022: Specifies which party/parties will bear the charges associated with processing of the payment transaction.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'DEBT', 'description': 'All charges borne by debtor (OUR)'},
                {'value': 'CRED', 'description': 'All charges borne by creditor (BEN)'},
                {'value': 'SHAR', 'description': 'Charges shared (SHA)'},
                {'value': 'SLEV', 'description': 'Following service level'},
            ],
            'iso_element_name': 'ChargeBearer',
            'iso_element_path': 'PmtInf/ChrgBr',
            'iso_data_type': 'ChargeBearerType1Code',
        },
        'creditor_agent_bic': {
            'business_name': 'Creditor Agent BIC',
            'business_description': 'Per ISO 20022: Bank Identifier Code (BIC/SWIFT code) of the creditor financial institution.',
            'data_format': 'ISO 9362 BIC (8 or 11 characters)',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI',
            'iso_data_type': 'BICFIIdentifier',
        },
        'creditor_name': {
            'business_name': 'Creditor Name',
            'business_description': 'Per ISO 20022: Party to which an amount of money is due. Name of the beneficiary/payee.',
            'data_format': 'Text, max 140 characters',
            'iso_element_name': 'Name',
            'iso_element_path': 'PmtInf/CdtTrfTxInf/Cdtr/Nm',
            'iso_data_type': 'Max140Text',
        },
        'creditor_address_country': {
            'business_name': 'Creditor Country',
            'business_description': 'Per ISO 20022: Country of residence or incorporation of the creditor.',
            'data_format': 'ISO 3166-1 alpha-2 (2-letter code)',
            'iso_element_name': 'Country',
            'iso_element_path': 'PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/Ctry',
            'iso_data_type': 'CountryCode',
        },
        'creditor_account_iban': {
            'business_name': 'Creditor Account IBAN',
            'business_description': 'Per ISO 20022: International Bank Account Number (IBAN) of the creditor account to be credited.',
            'data_format': 'ISO 13616 IBAN format',
            'iso_element_name': 'IBAN',
            'iso_element_path': 'PmtInf/CdtTrfTxInf/CdtrAcct/Id/IBAN',
            'iso_data_type': 'IBAN2007Identifier',
        },
        'remittance_unstructured': {
            'business_name': 'Remittance Information Unstructured',
            'business_description': 'Per ISO 20022: Information supplied to enable the matching/reconciliation of an entry with the items that the payment is intended to settle in an unstructured form.',
            'data_format': 'Text, max 140 characters',
            'iso_element_name': 'Unstructured',
            'iso_element_path': 'PmtInf/CdtTrfTxInf/RmtInf/Ustrd',
            'iso_data_type': 'Max140Text',
        },
        'purpose_code': {
            'business_name': 'Purpose Code',
            'business_description': 'Per ISO 20022: Underlying reason for the payment transaction (e.g., SALA for salary, SUPP for supplier payment).',
            'data_format': 'Code',
            'iso_element_name': 'Code',
            'iso_element_path': 'PmtInf/CdtTrfTxInf/Purp/Cd',
            'iso_data_type': 'ExternalPurpose1Code',
        },
        'created_at': {
            'business_name': 'Created At',
            'business_description': 'Timestamp when this record was created in the CDM.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },

    # ========================================================================
    # cdm_pacs_fi_customer_credit_transfer - ISO 20022 pacs.008
    # FIToFICustomerCreditTransfer - Interbank credit transfer
    # ========================================================================
    'cdm_pacs_fi_customer_credit_transfer': {
        'transfer_id': {
            'business_name': 'Transfer ID',
            'business_description': 'Unique identifier for this FI-to-FI credit transfer record in the CDM.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_stg_id': {
            'business_name': 'Source Staging ID',
            'business_description': 'Reference to the Silver layer staging record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'message_id': {
            'business_name': 'Message Identification',
            'business_description': 'Per ISO 20022 pacs.008: Point to point reference assigned by the instructing party to identify the message.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'MessageIdentification',
            'iso_element_path': 'GrpHdr/MsgId',
            'iso_data_type': 'Max35Text',
        },
        'creation_datetime': {
            'business_name': 'Creation Date Time',
            'business_description': 'Per ISO 20022: Date and time at which the message was created by the instructing party.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': 'CreationDateTime',
            'iso_element_path': 'GrpHdr/CreDtTm',
            'iso_data_type': 'ISODateTime',
        },
        'number_of_transactions': {
            'business_name': 'Number of Transactions',
            'business_description': 'Per ISO 20022: Number of individual transactions contained in the message.',
            'data_format': 'Integer, max 15 digits',
            'iso_element_name': 'NumberOfTransactions',
            'iso_element_path': 'GrpHdr/NbOfTxs',
            'iso_data_type': 'Max15NumericText',
        },
        'settlement_method': {
            'business_name': 'Settlement Method',
            'business_description': 'Per ISO 20022: Method used to settle the credit transfer instruction.',
            'data_format': 'Enumeration',
            'allowed_values': [
                {'value': 'INDA', 'description': 'InstructedAgent'},
                {'value': 'INGA', 'description': 'InstructingAgent'},
                {'value': 'COVE', 'description': 'CoverMethod'},
                {'value': 'CLRG', 'description': 'ClearingSystem'},
            ],
            'iso_element_name': 'SettlementMethod',
            'iso_element_path': 'GrpHdr/SttlmInf/SttlmMtd',
            'iso_data_type': 'SettlementMethod1Code',
        },
        'instruction_id': {
            'business_name': 'Instruction Identification',
            'business_description': 'Per ISO 20022: Unique identification assigned by an instructing party for an instructed party.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'InstructionIdentification',
            'iso_element_path': 'CdtTrfTxInf/PmtId/InstrId',
            'iso_data_type': 'Max35Text',
        },
        'end_to_end_id': {
            'business_name': 'End to End Identification',
            'business_description': 'Per ISO 20022: Unique identification assigned by the initiating party. Passed unchanged through the entire chain.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'EndToEndIdentification',
            'iso_element_path': 'CdtTrfTxInf/PmtId/EndToEndId',
            'iso_data_type': 'Max35Text',
        },
        'transaction_id': {
            'business_name': 'Transaction Identification',
            'business_description': 'Per ISO 20022: Unique identification assigned by the first instructing agent to identify the transaction.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'TransactionIdentification',
            'iso_element_path': 'CdtTrfTxInf/PmtId/TxId',
            'iso_data_type': 'Max35Text',
        },
        'uetr': {
            'business_name': 'UETR',
            'business_description': 'Per ISO 20022: Universally unique identifier providing an end-to-end reference for the payment transaction. Required for SWIFT gpi payments.',
            'data_format': 'UUID format (36 characters)',
            'iso_element_name': 'UETR',
            'iso_element_path': 'CdtTrfTxInf/PmtId/UETR',
            'iso_data_type': 'UUIDv4Identifier',
        },
        'interbank_settlement_amount': {
            'business_name': 'Interbank Settlement Amount',
            'business_description': 'Per ISO 20022: Amount of money to be moved between the instructing agent and the instructed agent. May differ from InstructedAmount due to FX conversion.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'InterbankSettlementAmount',
            'iso_element_path': 'CdtTrfTxInf/IntrBkSttlmAmt',
            'iso_data_type': 'ActiveCurrencyAndAmount',
        },
        'interbank_settlement_currency': {
            'business_name': 'Interbank Settlement Currency',
            'business_description': 'ISO 4217 currency code of the interbank settlement amount.',
            'data_format': 'ISO 4217 (3-letter code)',
            'iso_element_name': 'Currency',
            'iso_element_path': 'CdtTrfTxInf/IntrBkSttlmAmt/@Ccy',
            'iso_data_type': 'ActiveCurrencyCode',
        },
        'interbank_settlement_date': {
            'business_name': 'Interbank Settlement Date',
            'business_description': 'Per ISO 20022: Date on which the amount of money ceases to be available to the agent that owes it and becomes available to the agent to which it is due.',
            'data_format': 'ISO 8601 Date (YYYY-MM-DD)',
            'iso_element_name': 'InterbankSettlementDate',
            'iso_element_path': 'CdtTrfTxInf/IntrBkSttlmDt',
            'iso_data_type': 'ISODate',
        },
        'instructed_amount': {
            'business_name': 'Instructed Amount',
            'business_description': 'Per ISO 20022: Amount of money to be moved between the debtor and creditor, as instructed by the debtor.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'InstructedAmount',
            'iso_element_path': 'CdtTrfTxInf/InstdAmt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'instructed_currency': {
            'business_name': 'Instructed Currency',
            'business_description': 'ISO 4217 currency code of the instructed amount.',
            'data_format': 'ISO 4217 (3-letter code)',
            'iso_element_name': 'Currency',
            'iso_element_path': 'CdtTrfTxInf/InstdAmt/@Ccy',
            'iso_data_type': 'ActiveOrHistoricCurrencyCode',
        },
        'exchange_rate': {
            'business_name': 'Exchange Rate',
            'business_description': 'Per ISO 20022: Factor used to convert an amount from one currency into another. Rate applied when instructed amount differs from settlement amount.',
            'data_format': 'Decimal (rate)',
            'iso_element_name': 'ExchangeRate',
            'iso_element_path': 'CdtTrfTxInf/XchgRate',
            'iso_data_type': 'BaseOneRate',
        },
        'charge_bearer': {
            'business_name': 'Charge Bearer',
            'business_description': 'Per ISO 20022: Specifies which party/parties will bear the charges.',
            'data_format': 'Enumeration',
            'iso_element_name': 'ChargeBearer',
            'iso_element_path': 'CdtTrfTxInf/ChrgBr',
            'iso_data_type': 'ChargeBearerType1Code',
        },
        'instructing_agent_bic': {
            'business_name': 'Instructing Agent BIC',
            'business_description': 'Per ISO 20022: Agent that instructs the next party in the chain to carry out the (set of) instruction(s).',
            'data_format': 'ISO 9362 BIC (8 or 11 characters)',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'CdtTrfTxInf/InstgAgt/FinInstnId/BICFI',
            'iso_data_type': 'BICFIIdentifier',
        },
        'instructed_agent_bic': {
            'business_name': 'Instructed Agent BIC',
            'business_description': 'Per ISO 20022: Agent that is instructed by the previous party in the chain.',
            'data_format': 'ISO 9362 BIC (8 or 11 characters)',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'CdtTrfTxInf/InstdAgt/FinInstnId/BICFI',
            'iso_data_type': 'BICFIIdentifier',
        },
        'debtor_name': {
            'business_name': 'Debtor Name',
            'business_description': 'Per ISO 20022: Party that owes an amount of money to the (ultimate) creditor.',
            'data_format': 'Text, max 140 characters',
            'iso_element_name': 'Name',
            'iso_element_path': 'CdtTrfTxInf/Dbtr/Nm',
            'iso_data_type': 'Max140Text',
        },
        'debtor_account_iban': {
            'business_name': 'Debtor Account IBAN',
            'business_description': 'Per ISO 20022: IBAN of the debtor account.',
            'data_format': 'ISO 13616 IBAN format',
            'iso_element_name': 'IBAN',
            'iso_element_path': 'CdtTrfTxInf/DbtrAcct/Id/IBAN',
            'iso_data_type': 'IBAN2007Identifier',
        },
        'debtor_agent_bic': {
            'business_name': 'Debtor Agent BIC',
            'business_description': 'Per ISO 20022: Financial institution servicing an account for the debtor.',
            'data_format': 'ISO 9362 BIC (8 or 11 characters)',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI',
            'iso_data_type': 'BICFIIdentifier',
        },
        'creditor_agent_bic': {
            'business_name': 'Creditor Agent BIC',
            'business_description': 'Per ISO 20022: Financial institution servicing an account for the creditor.',
            'data_format': 'ISO 9362 BIC (8 or 11 characters)',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI',
            'iso_data_type': 'BICFIIdentifier',
        },
        'creditor_name': {
            'business_name': 'Creditor Name',
            'business_description': 'Per ISO 20022: Party to which an amount of money is due.',
            'data_format': 'Text, max 140 characters',
            'iso_element_name': 'Name',
            'iso_element_path': 'CdtTrfTxInf/Cdtr/Nm',
            'iso_data_type': 'Max140Text',
        },
        'creditor_account_iban': {
            'business_name': 'Creditor Account IBAN',
            'business_description': 'Per ISO 20022: IBAN of the creditor account.',
            'data_format': 'ISO 13616 IBAN format',
            'iso_element_name': 'IBAN',
            'iso_element_path': 'CdtTrfTxInf/CdtrAcct/Id/IBAN',
            'iso_data_type': 'IBAN2007Identifier',
        },
        'remittance_unstructured': {
            'business_name': 'Remittance Information Unstructured',
            'business_description': 'Per ISO 20022: Information supplied to enable matching/reconciliation in an unstructured form.',
            'data_format': 'Text, max 140 characters',
            'iso_element_name': 'Unstructured',
            'iso_element_path': 'CdtTrfTxInf/RmtInf/Ustrd',
            'iso_data_type': 'Max140Text',
        },
        'created_at': {
            'business_name': 'Created At',
            'business_description': 'Timestamp when this record was created in the CDM.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },

    # ========================================================================
    # cdm_camt_bank_to_customer_statement - ISO 20022 camt.053
    # BankToCustomerStatement - Account statement message
    # ========================================================================
    'cdm_camt_bank_to_customer_statement': {
        'statement_id': {
            'business_name': 'Statement ID',
            'business_description': 'Unique identifier for this bank statement record in the CDM.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'message_id': {
            'business_name': 'Message Identification',
            'business_description': 'Per ISO 20022 camt.053: Point to point reference assigned by the account servicer to identify the message.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'MessageIdentification',
            'iso_element_path': 'GrpHdr/MsgId',
            'iso_data_type': 'Max35Text',
        },
        'creation_datetime': {
            'business_name': 'Creation Date Time',
            'business_description': 'Per ISO 20022: Date and time at which the message was created.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': 'CreationDateTime',
            'iso_element_path': 'GrpHdr/CreDtTm',
            'iso_data_type': 'ISODateTime',
        },
        'statement_identification': {
            'business_name': 'Statement Identification',
            'business_description': 'Per ISO 20022: Unique identification, as assigned by the account servicer, to unambiguously identify the statement.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Stmt/Id',
            'iso_data_type': 'Max35Text',
        },
        'statement_sequence_number': {
            'business_name': 'Statement Sequence Number',
            'business_description': 'Per ISO 20022: Sequential number of the statement for a specific period.',
            'data_format': 'Text, max 35 characters',
            'iso_element_name': 'ElectronicSequenceNumber',
            'iso_element_path': 'Stmt/ElctrncSeqNb',
            'iso_data_type': 'Number',
        },
        'from_datetime': {
            'business_name': 'From Date Time',
            'business_description': 'Per ISO 20022: Start date and time of the period covered by the statement.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': 'FromDateTime',
            'iso_element_path': 'Stmt/FrToDt/FrDtTm',
            'iso_data_type': 'ISODateTime',
        },
        'to_datetime': {
            'business_name': 'To Date Time',
            'business_description': 'Per ISO 20022: End date and time of the period covered by the statement.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': 'ToDateTime',
            'iso_element_path': 'Stmt/FrToDt/ToDtTm',
            'iso_data_type': 'ISODateTime',
        },
        'account_iban': {
            'business_name': 'Account IBAN',
            'business_description': 'Per ISO 20022: IBAN of the account for which the statement is generated.',
            'data_format': 'ISO 13616 IBAN format',
            'iso_element_name': 'IBAN',
            'iso_element_path': 'Stmt/Acct/Id/IBAN',
            'iso_data_type': 'IBAN2007Identifier',
        },
        'account_currency': {
            'business_name': 'Account Currency',
            'business_description': 'Per ISO 20022: Currency of the account.',
            'data_format': 'ISO 4217 (3-letter code)',
            'iso_element_name': 'Currency',
            'iso_element_path': 'Stmt/Acct/Ccy',
            'iso_data_type': 'ActiveOrHistoricCurrencyCode',
        },
        'account_owner_name': {
            'business_name': 'Account Owner Name',
            'business_description': 'Per ISO 20022: Name of the party that legally owns the account.',
            'data_format': 'Text, max 140 characters',
            'iso_element_name': 'Name',
            'iso_element_path': 'Stmt/Acct/Ownr/Nm',
            'iso_data_type': 'Max140Text',
        },
        'account_servicer_bic': {
            'business_name': 'Account Servicer BIC',
            'business_description': 'Per ISO 20022: BIC of the financial institution servicing the account.',
            'data_format': 'ISO 9362 BIC (8 or 11 characters)',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'Stmt/Acct/Svcr/FinInstnId/BICFI',
            'iso_data_type': 'BICFIIdentifier',
        },
        'opening_balance_amount': {
            'business_name': 'Opening Balance Amount',
            'business_description': 'Per ISO 20022: Balance of the account at the beginning of the statement period.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'Amount',
            'iso_element_path': 'Stmt/Bal[Tp/CdOrPrtry/Cd=OPBD]/Amt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'closing_balance_amount': {
            'business_name': 'Closing Balance Amount',
            'business_description': 'Per ISO 20022: Balance of the account at the end of the statement period.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'Amount',
            'iso_element_path': 'Stmt/Bal[Tp/CdOrPrtry/Cd=CLBD]/Amt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'closing_available_balance': {
            'business_name': 'Closing Available Balance',
            'business_description': 'Per ISO 20022: Available balance at the end of the statement period. This reflects amounts after holds and pending transactions.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'Amount',
            'iso_element_path': 'Stmt/Bal[Tp/CdOrPrtry/Cd=CLAV]/Amt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'total_debit_entries_count': {
            'business_name': 'Total Debit Entries Count',
            'business_description': 'Per ISO 20022: Number of debit entries in the statement.',
            'data_format': 'Integer',
            'iso_element_name': 'NumberOfEntries',
            'iso_element_path': 'Stmt/TxsSummry/TtlDbtNtries/NbOfNtries',
            'iso_data_type': 'Max15NumericText',
        },
        'total_debit_entries_sum': {
            'business_name': 'Total Debit Entries Sum',
            'business_description': 'Per ISO 20022: Sum of all debit entries in the statement.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'Sum',
            'iso_element_path': 'Stmt/TxsSummry/TtlDbtNtries/Sum',
            'iso_data_type': 'DecimalNumber',
        },
        'total_credit_entries_count': {
            'business_name': 'Total Credit Entries Count',
            'business_description': 'Per ISO 20022: Number of credit entries in the statement.',
            'data_format': 'Integer',
            'iso_element_name': 'NumberOfEntries',
            'iso_element_path': 'Stmt/TxsSummry/TtlCdtNtries/NbOfNtries',
            'iso_data_type': 'Max15NumericText',
        },
        'total_credit_entries_sum': {
            'business_name': 'Total Credit Entries Sum',
            'business_description': 'Per ISO 20022: Sum of all credit entries in the statement.',
            'data_format': 'Decimal with up to 4 decimal places',
            'iso_element_name': 'Sum',
            'iso_element_path': 'Stmt/TxsSummry/TtlCdtNtries/Sum',
            'iso_data_type': 'DecimalNumber',
        },
        'created_at': {
            'business_name': 'Created At',
            'business_description': 'Timestamp when this record was created in the CDM.',
            'data_format': 'ISO 8601 DateTime',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },
}


def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(**DB_CONFIG)


def refresh_catalog_from_schema(conn) -> tuple:
    """Run the schema refresh function to discover new columns."""
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM mapping.refresh_cdm_catalog_from_schema()")
        result = cur.fetchone()
        conn.commit()
        return result if result else (0, 0)


def update_business_descriptions(conn) -> int:
    """Update catalog with business descriptions from the definitions above."""
    updated = 0

    # Combine main definitions with extension, ISO, and supporting table definitions
    all_definitions = dict(CDM_BUSINESS_DESCRIPTIONS)
    all_definitions.update(CDM_EXTENSION_TABLES)
    all_definitions.update(CDM_ISO_TABLES)
    all_definitions.update(CDM_SUPPORTING_TABLES)

    with conn.cursor() as cur:
        for table_name, columns in all_definitions.items():
            for column_name, metadata in columns.items():
                # Build update statement
                update_fields = []
                values = []

                if 'business_name' in metadata and metadata['business_name']:
                    update_fields.append("business_name = %s")
                    values.append(metadata['business_name'])

                if 'business_description' in metadata and metadata['business_description']:
                    update_fields.append("business_description = %s")
                    values.append(metadata['business_description'])

                if 'data_format' in metadata and metadata['data_format']:
                    update_fields.append("data_format = %s")
                    values.append(metadata['data_format'])

                if 'allowed_values' in metadata and metadata['allowed_values']:
                    update_fields.append("allowed_values = %s")
                    values.append(json.dumps(metadata['allowed_values']))

                if 'iso_element_name' in metadata:
                    update_fields.append("iso_element_name = %s")
                    values.append(metadata['iso_element_name'])

                if 'iso_element_path' in metadata:
                    update_fields.append("iso_element_path = %s")
                    values.append(metadata['iso_element_path'])

                if 'iso_data_type' in metadata:
                    update_fields.append("iso_data_type = %s")
                    values.append(metadata['iso_data_type'])

                if update_fields:
                    update_fields.append("updated_at = CURRENT_TIMESTAMP")
                    update_fields.append("updated_by = %s")
                    values.append('prime_cdm_catalog.py')

                    sql = f"""
                        UPDATE mapping.cdm_catalog
                        SET {', '.join(update_fields)}
                        WHERE pde_table_name = %s AND pde_column_name = %s
                    """
                    values.extend([table_name, column_name])

                    cur.execute(sql, values)
                    if cur.rowcount > 0:
                        updated += cur.rowcount

        conn.commit()

    return updated


def get_catalog_stats(conn) -> dict:
    """Get catalog statistics. Excludes tables marked for drop (_drop suffix)."""
    stats = {}

    with conn.cursor() as cur:
        # Total elements (excluding _drop tables)
        cur.execute("""
            SELECT COUNT(*) FROM mapping.cdm_catalog
            WHERE is_active = true AND pde_table_name NOT LIKE '%_drop'
        """)
        stats['total_elements'] = cur.fetchone()[0]

        # Documented elements (with business description)
        cur.execute("""
            SELECT COUNT(*) FROM mapping.cdm_catalog
            WHERE is_active = true
              AND pde_table_name NOT LIKE '%_drop'
              AND business_description IS NOT NULL AND business_description <> ''
        """)
        stats['documented_elements'] = cur.fetchone()[0]

        # ISO mapped elements
        cur.execute("""
            SELECT COUNT(*) FROM mapping.cdm_catalog
            WHERE is_active = true
              AND pde_table_name NOT LIKE '%_drop'
              AND iso_element_name IS NOT NULL AND iso_element_name <> ''
        """)
        stats['iso_mapped_elements'] = cur.fetchone()[0]

        # By table (excluding _drop tables)
        cur.execute("""
            SELECT pde_table_name, COUNT(*) as total,
                   COUNT(*) FILTER (WHERE business_description IS NOT NULL AND business_description <> '') as documented
            FROM mapping.cdm_catalog
            WHERE is_active = true AND pde_table_name NOT LIKE '%_drop'
            GROUP BY pde_table_name
            ORDER BY pde_table_name
        """)
        stats['by_table'] = [
            {'table': row[0], 'total': row[1], 'documented': row[2]}
            for row in cur.fetchall()
        ]

    return stats


def main():
    print("=" * 60)
    print("CDM Catalog Priming Script")
    print("=" * 60)

    try:
        conn = get_db_connection()
        print(f"\nConnected to database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")

        # Step 1: Refresh catalog from schema
        print("\n[Step 1] Refreshing catalog from Gold schema...")
        inserted, updated = refresh_catalog_from_schema(conn)
        print(f"  - Inserted: {inserted} new columns")
        print(f"  - Updated: {updated} existing columns")

        # Step 2: Update business descriptions
        print("\n[Step 2] Updating business descriptions...")
        descriptions_updated = update_business_descriptions(conn)
        print(f"  - Updated: {descriptions_updated} records")

        # Step 3: Display statistics
        print("\n[Step 3] Catalog Statistics:")
        stats = get_catalog_stats(conn)
        print(f"  - Total elements: {stats['total_elements']}")
        print(f"  - Documented: {stats['documented_elements']} ({100*stats['documented_elements']//max(stats['total_elements'],1)}%)")
        print(f"  - ISO mapped: {stats['iso_mapped_elements']} ({100*stats['iso_mapped_elements']//max(stats['total_elements'],1)}%)")

        print("\n  By Table:")
        for table_stat in stats['by_table']:
            pct = 100 * table_stat['documented'] // max(table_stat['total'], 1)
            print(f"    {table_stat['table']}: {table_stat['documented']}/{table_stat['total']} ({pct}%)")

        conn.close()
        print("\n" + "=" * 60)
        print("Catalog priming complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == '__main__':
    main()
