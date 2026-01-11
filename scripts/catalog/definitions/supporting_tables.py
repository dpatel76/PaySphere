"""
CDM Catalog Definitions - Supporting Tables
Includes identifiers, events, statements, charges, remittance, settlement, regulatory, status
"""

# CDM Party Identifiers
CDM_PARTY_IDENTIFIERS = {
    'cdm_party_identifiers': {
        'party_identifier_id': {
            'business_name': 'Party Identifier ID',
            'business_description': 'Unique identifier for this party identifier record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'party_id': {
            'business_name': 'Party ID',
            'business_description': 'Reference to the parent party record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_type': {
            'business_name': 'Identifier Type',
            'business_description': 'Type of identifier: BIC, LEI, NATIONAL_ID, TAX_ID, DUNS, etc.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_value': {
            'business_name': 'Identifier Value',
            'business_description': 'The actual identifier value.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_scheme': {
            'business_name': 'Identifier Scheme',
            'business_description': 'Scheme or authority that issued the identifier.',
            'iso_element_name': 'SchemeName',
            'iso_element_path': 'Document/*/Id/OrgId/Othr/SchmeNm | Document/*/Id/PrvtId/Othr/SchmeNm',
            'iso_data_type': 'Max35Text',
        },
        'issuer': {
            'business_name': 'Issuer',
            'business_description': 'Entity that issued the identifier.',
            'iso_element_name': 'Issuer',
            'iso_element_path': 'Document/*/Id/OrgId/Othr/Issr | Document/*/Id/PrvtId/Othr/Issr',
            'iso_data_type': 'Max35Text',
        },
        'is_primary': {
            'business_name': 'Is Primary',
            'business_description': 'Indicates if this is the primary identifier for the party.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },
}

# CDM Account Identifiers
CDM_ACCOUNT_IDENTIFIERS = {
    'cdm_account_identifiers': {
        'account_identifier_id': {
            'business_name': 'Account Identifier ID',
            'business_description': 'Unique identifier for this account identifier record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'account_id': {
            'business_name': 'Account ID',
            'business_description': 'Reference to the parent account record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_type': {
            'business_name': 'Identifier Type',
            'business_description': 'Type of identifier: IBAN, BBAN, UPIC, PROXY, etc.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_value': {
            'business_name': 'Identifier Value',
            'business_description': 'The actual identifier value.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_scheme': {
            'business_name': 'Identifier Scheme',
            'business_description': 'Scheme for non-standard identifiers.',
            'iso_element_name': 'SchemeName',
            'iso_element_path': 'Document/*/Acct/Id/Othr/SchmeNm',
            'iso_data_type': 'AccountSchemeName1Choice',
        },
        'is_primary': {
            'business_name': 'Is Primary',
            'business_description': 'Indicates if this is the primary identifier.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },
}

# CDM Institution Identifiers
CDM_INSTITUTION_IDENTIFIERS = {
    'cdm_institution_identifiers': {
        'institution_identifier_id': {
            'business_name': 'Institution Identifier ID',
            'business_description': 'Unique identifier for this institution identifier record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'institution_id': {
            'business_name': 'Institution ID',
            'business_description': 'Reference to the parent financial institution record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_type': {
            'business_name': 'Identifier Type',
            'business_description': 'Type of identifier: BIC, LEI, CLEARING_MEMBER_ID, etc.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_value': {
            'business_name': 'Identifier Value',
            'business_description': 'The actual identifier value.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'clearing_system': {
            'business_name': 'Clearing System',
            'business_description': 'Clearing system for clearing member IDs.',
            'iso_element_name': 'Code',
            'iso_element_path': 'Document/*/FinInstnId/ClrSysMmbId/ClrSysId/Cd',
            'iso_data_type': 'ExternalClearingSystemIdentification1Code',
        },
        'is_primary': {
            'business_name': 'Is Primary',
            'business_description': 'Indicates if this is the primary identifier.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },
}

# CDM Identifier Type (Reference Data)
CDM_IDENTIFIER_TYPE = {
    'cdm_identifier_type': {
        'identifier_type_id': {
            'business_name': 'Identifier Type ID',
            'business_description': 'Unique identifier for this identifier type.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'type_code': {
            'business_name': 'Type Code',
            'business_description': 'Short code for the identifier type.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'type_name': {
            'business_name': 'Type Name',
            'business_description': 'Full name of the identifier type.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'description': {
            'business_name': 'Description',
            'business_description': 'Description of the identifier type.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'category': {
            'business_name': 'Category',
            'business_description': 'Category: PARTY, ACCOUNT, INSTITUTION, TRANSACTION.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'validation_pattern': {
            'business_name': 'Validation Pattern',
            'business_description': 'Regex pattern for validating this identifier type.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_type_code': {
            'business_name': 'Identifier Type Code',
            'business_description': 'Standardized code for the identifier type (e.g., BIC, LEI, IBAN, UPIC).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'display_name': {
            'business_name': 'Display Name',
            'business_description': 'Human-readable display name for the identifier type.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'entity_type': {
            'business_name': 'Entity Type',
            'business_description': 'Type of entity this identifier applies to: PARTY, ACCOUNT, INSTITUTION, PAYMENT.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_category': {
            'business_name': 'Identifier Category',
            'business_description': 'Category classification: GLOBAL (BIC, LEI), NATIONAL (tax IDs), PROPRIETARY.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'is_globally_unique': {
            'business_name': 'Is Globally Unique',
            'business_description': 'Indicates if this identifier type is globally unique (e.g., LEI, IBAN) vs requiring context.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'iso20022_element': {
            'business_name': 'ISO 20022 Element',
            'business_description': 'Corresponding ISO 20022 element name for this identifier type.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'max_length': {
            'business_name': 'Maximum Length',
            'business_description': 'Maximum character length allowed for this identifier type.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'requires_issuer': {
            'business_name': 'Requires Issuer',
            'business_description': 'Indicates if this identifier type requires an issuer to be specified.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'requires_scheme': {
            'business_name': 'Requires Scheme',
            'business_description': 'Indicates if this identifier type requires a scheme name to be specified.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'validation_regex': {
            'business_name': 'Validation Regex',
            'business_description': 'Regular expression pattern for validating identifier values of this type.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },
}

# CDM Payment Event
CDM_PAYMENT_EVENT = {
    'cdm_payment_event': {
        'event_id': {
            'business_name': 'Event ID',
            'business_description': 'Unique identifier for this payment event.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the payment instruction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'event_type': {
            'business_name': 'Event Type',
            'business_description': 'Type of event: CREATED, VALIDATED, SENT, RECEIVED, SETTLED, RETURNED, CANCELLED.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'event_datetime': {
            'business_name': 'Event Date Time',
            'business_description': 'Date and time when the event occurred.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': 'ISODateTime',
        },
        'event_source': {
            'business_name': 'Event Source',
            'business_description': 'System or party that generated the event.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'event_status': {
            'business_name': 'Event Status',
            'business_description': 'Status of the event: SUCCESS, FAILURE, PENDING.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'reason_code': {
            'business_name': 'Reason Code',
            'business_description': 'Reason code if applicable (e.g., rejection reason).',
            'iso_element_name': 'Code',
            'iso_element_path': 'Document/FIToFIPmtStsRpt/TxInfAndSts/StsRsnInf/Rsn/Cd | Document/PmtRtr/TxInf/RtrRsnInf/Rsn/Cd',
            'iso_data_type': 'ExternalStatusReason1Code',
        },
        'reason_description': {
            'business_name': 'Reason Description',
            'business_description': 'Human-readable description of the reason.',
            'iso_element_name': 'AdditionalInformation',
            'iso_element_path': 'Document/FIToFIPmtStsRpt/TxInfAndSts/StsRsnInf/AddtlInf | Document/PmtRtr/TxInf/RtrRsnInf/AddtlInf',
            'iso_data_type': 'Max105Text',
        },
        'additional_info': {
            'business_name': 'Additional Information',
            'business_description': 'Additional details about the event.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'payment_id': {
            'business_name': 'Payment ID',
            'business_description': 'Reference to the associated payment instruction or transaction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'event_timestamp': {
            'business_name': 'Event Timestamp',
            'business_description': 'Precise timestamp when the event was recorded in the system.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': 'ISODateTime',
        },
        'actor': {
            'business_name': 'Actor',
            'business_description': 'Identifier of the party or system that performed the action triggering the event.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'actor_type': {
            'business_name': 'Actor Type',
            'business_description': 'Type of actor: SYSTEM, USER, BANK, CLEARING_HOUSE, REGULATOR.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'previous_status': {
            'business_name': 'Previous Status',
            'business_description': 'Payment status before this event occurred.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'new_status': {
            'business_name': 'New Status',
            'business_description': 'Payment status after this event occurred.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_system': {
            'business_name': 'Source System',
            'business_description': 'Name or identifier of the system that originated the event.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'details': {
            'business_name': 'Details',
            'business_description': 'JSON or structured data containing additional event-specific details.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },
}

# CDM Payment Status
CDM_PAYMENT_STATUS = {
    'cdm_payment_status': {
        'status_id': {
            'business_name': 'Status ID',
            'business_description': 'Unique identifier for this status record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the payment instruction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'status_code': {
            'business_name': 'Status Code',
            'business_description': 'Per ISO 20022: Current status of the payment. '
                                   'ACTC=Accepted Technical, ACCP=Accepted Customer Profile, '
                                   'ACSP=Accepted Settlement in Progress, ACSC=Accepted Settlement Completed, '
                                   'RJCT=Rejected, PDNG=Pending.',
            'iso_element_name': 'TransactionStatus',
            'iso_element_path': 'Document/FIToFIPmtStsRpt/TxInfAndSts/TxSts | Document/CstmrPmtStsRpt/OrgnlPmtInfAndSts/TxInfAndSts/TxSts',
            'iso_data_type': 'ExternalPaymentTransactionStatus1Code',
        },
        'status_datetime': {
            'business_name': 'Status Date Time',
            'business_description': 'Date and time when the status was recorded.',
            'iso_element_name': 'AcceptanceDateTime',
            'iso_element_path': 'Document/FIToFIPmtStsRpt/TxInfAndSts/AccptncDtTm',
            'iso_data_type': 'ISODateTime',
        },
        'reason_code': {
            'business_name': 'Reason Code',
            'business_description': 'Per ISO 20022: Reason code for the status.',
            'iso_element_name': 'Code',
            'iso_element_path': 'Document/FIToFIPmtStsRpt/TxInfAndSts/StsRsnInf/Rsn/Cd',
            'iso_data_type': 'ExternalStatusReason1Code',
        },
        'reason_description': {
            'business_name': 'Reason Description',
            'business_description': 'Per ISO 20022: Additional information about the status reason.',
            'iso_element_name': 'AdditionalInformation',
            'iso_element_path': 'Document/FIToFIPmtStsRpt/TxInfAndSts/StsRsnInf/AddtlInf',
            'iso_data_type': 'Max105Text',
        },
        'originator_bic': {
            'business_name': 'Originator BIC',
            'business_description': 'BIC of the party that originated the status.',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'Document/FIToFIPmtStsRpt/TxInfAndSts/StsRsnInf/Orgtr/Id/OrgId/AnyBIC',
            'iso_data_type': 'AnyBICDec2014Identifier',
        },
    },
}

# CDM Payment Identifiers
CDM_PAYMENT_IDENTIFIERS = {
    'cdm_payment_identifiers': {
        'payment_identifier_id': {
            'business_name': 'Payment Identifier ID',
            'business_description': 'Unique identifier for this payment identifier record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the payment instruction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_type': {
            'business_name': 'Identifier Type',
            'business_description': 'Type of identifier: END_TO_END_ID, TRANSACTION_ID, UETR, etc.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_value': {
            'business_name': 'Identifier Value',
            'business_description': 'The actual identifier value.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'assigner': {
            'business_name': 'Assigner',
            'business_description': 'Party that assigned this identifier.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'id': {
            'business_name': 'ID',
            'business_description': 'Primary key identifier for this payment identifier record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_scope': {
            'business_name': 'Identifier Scope',
            'business_description': 'Scope of the identifier: GLOBAL, NETWORK, INSTITUTION, LOCAL.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'is_original': {
            'business_name': 'Is Original',
            'business_description': 'Indicates if this identifier is from the original message or derived/assigned later.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'related_identifier_type': {
            'business_name': 'Related Identifier Type',
            'business_description': 'Type of a related identifier if this identifier references another.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'related_identifier_value': {
            'business_name': 'Related Identifier Value',
            'business_description': 'Value of a related identifier if this identifier references another.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'scheme_name': {
            'business_name': 'Scheme Name',
            'business_description': 'Name of the scheme or authority that defines this identifier format.',
            'iso_element_name': 'SchemeName',
            'iso_element_path': 'Document/*/PmtId/UETR | Document/*/PmtId/EndToEndId',
            'iso_data_type': 'Max35Text',
        },
        'source_message_type': {
            'business_name': 'Source Message Type',
            'business_description': 'Type of the source message from which this identifier was extracted.',
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
    },
}

# CDM Document Identifier
CDM_DOCUMENT_IDENTIFIER = {
    'cdm_document_identifier': {
        'document_identifier_id': {
            'business_name': 'Document Identifier ID',
            'business_description': 'Unique identifier for this document identifier record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the payment instruction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'document_type': {
            'business_name': 'Document Type',
            'business_description': 'Type of document: INVOICE, CONTRACT, PURCHASE_ORDER.',
            'iso_element_name': 'Type',
            'iso_element_path': 'Document/*/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd',
            'iso_data_type': 'ExternalDocumentType1Code',
        },
        'document_number': {
            'business_name': 'Document Number',
            'business_description': 'Document reference number.',
            'iso_element_name': 'Number',
            'iso_element_path': 'Document/*/RmtInf/Strd/RfrdDocInf/Nb',
            'iso_data_type': 'Max35Text',
        },
        'issue_date': {
            'business_name': 'Issue Date',
            'business_description': 'Date the document was issued.',
            'iso_element_name': 'RelatedDate',
            'iso_element_path': 'Document/*/RmtInf/Strd/RfrdDocInf/RltdDt',
            'iso_data_type': 'ISODate',
        },
        'amount': {
            'business_name': 'Amount',
            'business_description': 'Amount referenced in the document.',
            'iso_element_name': 'Amount',
            'iso_element_path': 'Document/*/RmtInf/Strd/RfrdDocAmt/DuePyblAmt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'payment_instruction_id': {
            'business_name': 'Payment Instruction ID',
            'business_description': 'Foreign key reference to the associated payment instruction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_type': {
            'business_name': 'Identifier Type',
            'business_description': 'Type of document identifier: INVOICE_NUMBER, PO_NUMBER, CONTRACT_ID, etc.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_value': {
            'business_name': 'Identifier Value',
            'business_description': 'The actual value of the document identifier.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'document_type_code': {
            'business_name': 'Document Type Code',
            'business_description': 'Per ISO 20022: Coded document type from ExternalDocumentType1Code (e.g., CINV, CNTR, SOAC).',
            'iso_element_name': 'Code',
            'iso_element_path': 'Document/*/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd',
            'iso_data_type': 'ExternalDocumentType1Code',
        },
        'document_date': {
            'business_name': 'Document Date',
            'business_description': 'Date associated with the document (issue date, due date, etc.).',
            'iso_element_name': 'RelatedDate',
            'iso_element_path': 'Document/*/RmtInf/Strd/RfrdDocInf/RltdDt',
            'iso_data_type': 'ISODate',
        },
        'document_amount': {
            'business_name': 'Document Amount',
            'business_description': 'Monetary amount associated with the referenced document.',
            'iso_element_name': 'Amount',
            'iso_element_path': 'Document/*/RmtInf/Strd/RfrdDocAmt/DuePyblAmt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'document_currency': {
            'business_name': 'Document Currency',
            'business_description': 'Currency of the document amount.',
            'iso_element_name': 'Currency',
            'iso_element_path': 'Document/*/RmtInf/Strd/RfrdDocAmt/DuePyblAmt/@Ccy',
            'iso_data_type': 'ActiveOrHistoricCurrencyCode',
        },
        'source_field_name': {
            'business_name': 'Source Field Name',
            'business_description': 'Name of the field in the source message from which this identifier was extracted.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_message_format': {
            'business_name': 'Source Message Format',
            'business_description': 'Format of the source message (e.g., pain.001, pacs.008, MT103).',
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
    },
}

# CDM Transaction Identifier
CDM_TRANSACTION_IDENTIFIER = {
    'cdm_transaction_identifier': {
        'transaction_identifier_id': {
            'business_name': 'Transaction Identifier ID',
            'business_description': 'Unique identifier for this transaction identifier record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the payment instruction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_type': {
            'business_name': 'Identifier Type',
            'business_description': 'Type: MESSAGE_ID, END_TO_END_ID, TRANSACTION_ID, UETR, CLEARING_SYSTEM_REF.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_value': {
            'business_name': 'Identifier Value',
            'business_description': 'The actual identifier value.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_system': {
            'business_name': 'Source System',
            'business_description': 'System that generated the identifier.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'txn_identifier_id': {
            'business_name': 'Transaction Identifier ID (Alt)',
            'business_description': 'Alternative primary key identifier for this transaction identifier record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'payment_instruction_id': {
            'business_name': 'Payment Instruction ID',
            'business_description': 'Foreign key reference to the associated payment instruction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'identifier_scope': {
            'business_name': 'Identifier Scope',
            'business_description': 'Scope of the identifier: GLOBAL (UETR), NETWORK (clearing ref), INSTITUTION (internal ref).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'is_globally_unique': {
            'business_name': 'Is Globally Unique',
            'business_description': 'Indicates if this identifier is globally unique (e.g., UETR) vs locally scoped.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'is_original': {
            'business_name': 'Is Original',
            'business_description': 'Indicates if this identifier is from the original message or assigned during processing.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'is_primary': {
            'business_name': 'Is Primary',
            'business_description': 'Indicates if this is the primary identifier for tracking this transaction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'related_identifier_type': {
            'business_name': 'Related Identifier Type',
            'business_description': 'Type of a related identifier if this references another transaction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'related_identifier_value': {
            'business_name': 'Related Identifier Value',
            'business_description': 'Value of a related identifier if this references another transaction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'scheme_name': {
            'business_name': 'Scheme Name',
            'business_description': 'Name of the scheme or authority that defines this identifier format.',
            'iso_element_name': 'SchemeName',
            'iso_element_path': 'Document/*/PmtId/InstrId | Document/*/PmtId/EndToEndId | Document/*/PmtId/UETR',
            'iso_data_type': 'Max35Text',
        },
        'source_field_name': {
            'business_name': 'Source Field Name',
            'business_description': 'Name of the field in the source message from which this identifier was extracted.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_message_format': {
            'business_name': 'Source Message Format',
            'business_description': 'Format of the source message (e.g., pain.001, pacs.008, MT103).',
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
    },
}

# CDM Charge
CDM_CHARGE = {
    'cdm_charge': {
        'charge_id': {
            'business_name': 'Charge ID',
            'business_description': 'Unique identifier for this charge record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the payment instruction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'charge_type': {
            'business_name': 'Charge Type',
            'business_description': 'Type of charge: SENDER, RECEIVER, AGENT.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'charge_amount': {
            'business_name': 'Charge Amount',
            'business_description': 'Per ISO 20022: Amount of the charge.',
            'iso_element_name': 'Amount',
            'iso_element_path': 'Document/FIToFICstmrCdtTrf/CdtTrfTxInf/ChrgsInf/Amt | Document/FICdtTrf/CdtTrfTxInf/ChrgsInf/Amt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'charge_currency': {
            'business_name': 'Charge Currency',
            'business_description': 'Currency of the charge.',
            'iso_element_name': 'Currency',
            'iso_element_path': 'Document/FIToFICstmrCdtTrf/CdtTrfTxInf/ChrgsInf/Amt/@Ccy | Document/FICdtTrf/CdtTrfTxInf/ChrgsInf/Amt/@Ccy',
            'iso_data_type': 'ActiveOrHistoricCurrencyCode',
        },
        'charge_agent_bic': {
            'business_name': 'Charge Agent BIC',
            'business_description': 'Per ISO 20022: BIC of the agent charging the fee.',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'Document/FIToFICstmrCdtTrf/CdtTrfTxInf/ChrgsInf/Agt/FinInstnId/BICFI',
            'iso_data_type': 'BICFIDec2014Identifier',
        },
        'charge_bearer': {
            'business_name': 'Charge Bearer',
            'business_description': 'Per ISO 20022: Party bearing the charge. DEBT, CRED, SHAR, SLEV.',
            'iso_element_name': 'ChargeBearer',
            'iso_element_path': 'Document/FIToFICstmrCdtTrf/CdtTrfTxInf/ChrgBr | Document/FICdtTrf/CdtTrfTxInf/ChrgBr',
            'iso_data_type': 'ChargeBearerType1Code',
        },
    },
}

# CDM Remittance Information
CDM_REMITTANCE_INFORMATION = {
    'cdm_remittance_information': {
        'remittance_id': {
            'business_name': 'Remittance ID',
            'business_description': 'Unique identifier for this remittance record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the payment instruction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'unstructured': {
            'business_name': 'Unstructured',
            'business_description': 'Per ISO 20022: Free-form remittance information.',
            'iso_element_name': 'Unstructured',
            'iso_element_path': 'Document/FIToFICstmrCdtTrf/CdtTrfTxInf/RmtInf/Ustrd | Document/CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Ustrd',
            'iso_data_type': 'Max140Text',
        },
        'creditor_reference_type': {
            'business_name': 'Creditor Reference Type',
            'business_description': 'Per ISO 20022: Type of creditor reference.',
            'iso_element_name': 'Code',
            'iso_element_path': 'Document/*/RmtInf/Strd/CdtrRefInf/Tp/CdOrPrtry/Cd',
            'iso_data_type': 'ExternalDocumentType1Code',
        },
        'creditor_reference': {
            'business_name': 'Creditor Reference',
            'business_description': 'Per ISO 20022: Reference assigned by the creditor.',
            'iso_element_name': 'Reference',
            'iso_element_path': 'Document/*/RmtInf/Strd/CdtrRefInf/Ref',
            'iso_data_type': 'Max35Text',
        },
        'referred_document_type': {
            'business_name': 'Referred Document Type',
            'business_description': 'Per ISO 20022: Type of referred document.',
            'iso_element_name': 'Code',
            'iso_element_path': 'Document/*/RmtInf/Strd/RfrdDocInf/Tp/CdOrPrtry/Cd',
            'iso_data_type': 'ExternalDocumentType1Code',
        },
        'referred_document_number': {
            'business_name': 'Referred Document Number',
            'business_description': 'Per ISO 20022: Number of the referred document.',
            'iso_element_name': 'Number',
            'iso_element_path': 'Document/*/RmtInf/Strd/RfrdDocInf/Nb',
            'iso_data_type': 'Max35Text',
        },
    },
}

# CDM Settlement
CDM_SETTLEMENT = {
    'cdm_settlement': {
        'settlement_id': {
            'business_name': 'Settlement ID',
            'business_description': 'Unique identifier for this settlement record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the payment instruction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'settlement_method': {
            'business_name': 'Settlement Method',
            'business_description': 'Per ISO 20022: Method used to settle. '
                                   'INDA=Instructed Agent, INGA=Instructing Agent, COVE=Cover, CLRG=Clearing System.',
            'iso_element_name': 'SettlementMethod',
            'iso_element_path': 'Document/FIToFICstmrCdtTrf/GrpHdr/SttlmInf/SttlmMtd | Document/FICdtTrf/GrpHdr/SttlmInf/SttlmMtd',
            'iso_data_type': 'SettlementMethod1Code',
        },
        'settlement_account_iban': {
            'business_name': 'Settlement Account IBAN',
            'business_description': 'Per ISO 20022: IBAN of the settlement account.',
            'iso_element_name': 'IBAN',
            'iso_element_path': 'Document/*/GrpHdr/SttlmInf/SttlmAcct/Id/IBAN',
            'iso_data_type': 'IBAN2007Identifier',
        },
        'clearing_system': {
            'business_name': 'Clearing System',
            'business_description': 'Per ISO 20022: Clearing system used for settlement.',
            'iso_element_name': 'Code',
            'iso_element_path': 'Document/*/GrpHdr/SttlmInf/ClrSys/Cd',
            'iso_data_type': 'ExternalClearingSystemIdentification1Code',
        },
        'settlement_date': {
            'business_name': 'Settlement Date',
            'business_description': 'Per ISO 20022: Date of interbank settlement.',
            'iso_element_name': 'InterbankSettlementDate',
            'iso_element_path': 'Document/FIToFICstmrCdtTrf/CdtTrfTxInf/IntrBkSttlmDt | Document/FICdtTrf/CdtTrfTxInf/IntrBkSttlmDt',
            'iso_data_type': 'ISODate',
        },
        'settlement_amount': {
            'business_name': 'Settlement Amount',
            'business_description': 'Per ISO 20022: Amount settled.',
            'iso_element_name': 'InterbankSettlementAmount',
            'iso_element_path': 'Document/FIToFICstmrCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt | Document/FICdtTrf/CdtTrfTxInf/IntrBkSttlmAmt',
            'iso_data_type': 'ActiveCurrencyAndAmount',
        },
        'settlement_currency': {
            'business_name': 'Settlement Currency',
            'business_description': 'Currency of settlement.',
            'iso_element_name': 'Currency',
            'iso_element_path': 'Document/FIToFICstmrCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt/@Ccy | Document/FICdtTrf/CdtTrfTxInf/IntrBkSttlmAmt/@Ccy',
            'iso_data_type': 'ActiveCurrencyCode',
        },
    },
}

# CDM Regulatory Reporting
CDM_REGULATORY_REPORTING = {
    'cdm_regulatory_reporting': {
        'regulatory_id': {
            'business_name': 'Regulatory ID',
            'business_description': 'Unique identifier for this regulatory reporting record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the payment instruction.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'debit_credit_indicator': {
            'business_name': 'Debit Credit Indicator',
            'business_description': 'Per ISO 20022: Indicates if regulatory reporting is for debit or credit.',
            'iso_element_name': 'DebitCreditReportingIndicator',
            'iso_element_path': 'Document/*/RgltryRptg/DbtCdtRptgInd',
            'iso_data_type': 'RegulatoryReportingType1Code',
        },
        'authority_name': {
            'business_name': 'Authority Name',
            'business_description': 'Per ISO 20022: Name of the regulatory authority.',
            'iso_element_name': 'Name',
            'iso_element_path': 'Document/*/RgltryRptg/Authrty/Nm',
            'iso_data_type': 'Max140Text',
        },
        'authority_country': {
            'business_name': 'Authority Country',
            'business_description': 'Per ISO 20022: Country of the regulatory authority.',
            'iso_element_name': 'Country',
            'iso_element_path': 'Document/*/RgltryRptg/Authrty/Ctry',
            'iso_data_type': 'CountryCode',
        },
        'details_type': {
            'business_name': 'Details Type',
            'business_description': 'Per ISO 20022: Type of regulatory detail.',
            'iso_element_name': 'Code',
            'iso_element_path': 'Document/*/RgltryRptg/Dtls/Tp',
            'iso_data_type': 'Max35Text',
        },
        'details_date': {
            'business_name': 'Details Date',
            'business_description': 'Per ISO 20022: Date related to the regulatory detail.',
            'iso_element_name': 'Date',
            'iso_element_path': 'Document/*/RgltryRptg/Dtls/Dt',
            'iso_data_type': 'ISODate',
        },
        'details_country': {
            'business_name': 'Details Country',
            'business_description': 'Per ISO 20022: Country related to the regulatory detail.',
            'iso_element_name': 'Country',
            'iso_element_path': 'Document/*/RgltryRptg/Dtls/Ctry',
            'iso_data_type': 'CountryCode',
        },
        'details_code': {
            'business_name': 'Details Code',
            'business_description': 'Per ISO 20022: Regulatory reporting code.',
            'iso_element_name': 'Code',
            'iso_element_path': 'Document/*/RgltryRptg/Dtls/Cd',
            'iso_data_type': 'Max10Text',
        },
        'details_amount': {
            'business_name': 'Details Amount',
            'business_description': 'Per ISO 20022: Amount for regulatory reporting.',
            'iso_element_name': 'Amount',
            'iso_element_path': 'Document/*/RgltryRptg/Dtls/Amt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'details_information': {
            'business_name': 'Details Information',
            'business_description': 'Per ISO 20022: Additional regulatory information.',
            'iso_element_name': 'Information',
            'iso_element_path': 'Document/*/RgltryRptg/Dtls/Inf',
            'iso_data_type': 'Max35Text',
        },
    },
}

# CDM Account Statement
CDM_ACCOUNT_STATEMENT = {
    'cdm_account_statement': {
        'statement_id': {
            'business_name': 'Statement ID',
            'business_description': 'Unique identifier for this statement record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'account_id': {
            'business_name': 'Account ID',
            'business_description': 'Reference to the account.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'statement_identification': {
            'business_name': 'Statement Identification',
            'business_description': 'Per ISO 20022: Unique identification of the statement.',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Id',
            'iso_data_type': 'Max35Text',
        },
        'creation_datetime': {
            'business_name': 'Creation Date Time',
            'business_description': 'Per ISO 20022: Date and time the statement was created.',
            'iso_element_name': 'CreationDateTime',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/CreDtTm',
            'iso_data_type': 'ISODateTime',
        },
        'from_datetime': {
            'business_name': 'From Date Time',
            'business_description': 'Per ISO 20022: Start of the statement period.',
            'iso_element_name': 'FromDateTime',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/FrToDt/FrDtTm',
            'iso_data_type': 'ISODateTime',
        },
        'to_datetime': {
            'business_name': 'To Date Time',
            'business_description': 'Per ISO 20022: End of the statement period.',
            'iso_element_name': 'ToDateTime',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/FrToDt/ToDtTm',
            'iso_data_type': 'ISODateTime',
        },
        'opening_balance': {
            'business_name': 'Opening Balance',
            'business_description': 'Opening balance at start of period.',
            'iso_element_name': 'Amount',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Bal[Tp/CdOrPrtry/Cd=OPBD]/Amt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'closing_balance': {
            'business_name': 'Closing Balance',
            'business_description': 'Closing balance at end of period.',
            'iso_element_name': 'Amount',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Bal[Tp/CdOrPrtry/Cd=CLBD]/Amt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'total_credit_entries': {
            'business_name': 'Total Credit Entries',
            'business_description': 'Sum of all credit entries in the period.',
            'iso_element_name': 'Sum',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/TxsSummry/TtlCdtNtries/Sum',
            'iso_data_type': 'DecimalNumber',
        },
        'total_debit_entries': {
            'business_name': 'Total Debit Entries',
            'business_description': 'Sum of all debit entries in the period.',
            'iso_element_name': 'Sum',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/TxsSummry/TtlDbtNtries/Sum',
            'iso_data_type': 'DecimalNumber',
        },
        # Additional account statement fields
        'message_id': {
            'business_name': 'Message ID',
            'business_description': 'Per ISO 20022: Unique message identification assigned by the sender.',
            'iso_element_name': 'MessageIdentification',
            'iso_element_path': 'Document/BkToCstmrStmt/GrpHdr/MsgId',
            'iso_data_type': 'Max35Text',
        },
        'account_number': {
            'business_name': 'Account Number',
            'business_description': 'Account number for which the statement is generated.',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Acct/Id/Othr/Id',
            'iso_data_type': 'Max34Text',
        },
        'account_iban': {
            'business_name': 'Account IBAN',
            'business_description': 'Per ISO 20022: IBAN of the account.',
            'iso_element_name': 'IBAN',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Acct/Id/IBAN',
            'iso_data_type': 'IBAN2007Identifier',
        },
        'account_currency': {
            'business_name': 'Account Currency',
            'business_description': 'Currency of the account.',
            'iso_element_name': 'Currency',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Acct/Ccy',
            'iso_data_type': 'ActiveOrHistoricCurrencyCode',
        },
        'account_owner_name': {
            'business_name': 'Account Owner Name',
            'business_description': 'Name of the account owner.',
            'iso_element_name': 'Name',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Acct/Ownr/Nm',
            'iso_data_type': 'Max140Text',
        },
        'account_servicer_bic': {
            'business_name': 'Account Servicer BIC',
            'business_description': 'Per ISO 20022: BIC of the financial institution servicing the account.',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Acct/Svcr/FinInstnId/BICFI',
            'iso_data_type': 'BICFIDec2014Identifier',
        },
        'account_servicer_id': {
            'business_name': 'Account Servicer ID',
            'business_description': 'Identifier of the financial institution servicing the account.',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Acct/Svcr/FinInstnId/ClrSysMmbId/MmbId',
            'iso_data_type': 'Max35Text',
        },
        'statement_date': {
            'business_name': 'Statement Date',
            'business_description': 'Date of the statement.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': 'ISODate',
        },
        'statement_reference': {
            'business_name': 'Statement Reference',
            'business_description': 'Reference number for the statement.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'sequence_number': {
            'business_name': 'Sequence Number',
            'business_description': 'Per ISO 20022: Sequential number of the statement within a reporting period.',
            'iso_element_name': 'ElectronicSequenceNumber',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/ElctrncSeqNb',
            'iso_data_type': 'Number',
        },
        'from_date': {
            'business_name': 'From Date',
            'business_description': 'Start date of the statement period.',
            'iso_element_name': 'FromDate',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/FrToDt/FrDt',
            'iso_data_type': 'ISODate',
        },
        'to_date': {
            'business_name': 'To Date',
            'business_description': 'End date of the statement period.',
            'iso_element_name': 'ToDate',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/FrToDt/ToDt',
            'iso_data_type': 'ISODate',
        },
        'opening_balance_amount': {
            'business_name': 'Opening Balance Amount',
            'business_description': 'Per ISO 20022: Opening balance amount at start of period.',
            'iso_element_name': 'Amount',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Bal[Tp/CdOrPrtry/Cd=OPBD]/Amt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'opening_balance_currency': {
            'business_name': 'Opening Balance Currency',
            'business_description': 'Currency of the opening balance.',
            'iso_element_name': 'Currency',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Bal[Tp/CdOrPrtry/Cd=OPBD]/Amt/@Ccy',
            'iso_data_type': 'ActiveOrHistoricCurrencyCode',
        },
        'opening_balance_date': {
            'business_name': 'Opening Balance Date',
            'business_description': 'Date of the opening balance.',
            'iso_element_name': 'Date',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Bal[Tp/CdOrPrtry/Cd=OPBD]/Dt/Dt',
            'iso_data_type': 'ISODate',
        },
        'opening_balance_credit_debit': {
            'business_name': 'Opening Balance Credit/Debit',
            'business_description': 'Per ISO 20022: Indicates if opening balance is credit (CRDT) or debit (DBIT).',
            'iso_element_name': 'CreditDebitIndicator',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Bal[Tp/CdOrPrtry/Cd=OPBD]/CdtDbtInd',
            'iso_data_type': 'CreditDebitCode',
        },
        'closing_balance_amount': {
            'business_name': 'Closing Balance Amount',
            'business_description': 'Per ISO 20022: Closing balance amount at end of period.',
            'iso_element_name': 'Amount',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Bal[Tp/CdOrPrtry/Cd=CLBD]/Amt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'closing_balance_currency': {
            'business_name': 'Closing Balance Currency',
            'business_description': 'Currency of the closing balance.',
            'iso_element_name': 'Currency',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Bal[Tp/CdOrPrtry/Cd=CLBD]/Amt/@Ccy',
            'iso_data_type': 'ActiveOrHistoricCurrencyCode',
        },
        'closing_balance_date': {
            'business_name': 'Closing Balance Date',
            'business_description': 'Date of the closing balance.',
            'iso_element_name': 'Date',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Bal[Tp/CdOrPrtry/Cd=CLBD]/Dt/Dt',
            'iso_data_type': 'ISODate',
        },
        'closing_balance_credit_debit': {
            'business_name': 'Closing Balance Credit/Debit',
            'business_description': 'Per ISO 20022: Indicates if closing balance is credit (CRDT) or debit (DBIT).',
            'iso_element_name': 'CreditDebitIndicator',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Bal[Tp/CdOrPrtry/Cd=CLBD]/CdtDbtInd',
            'iso_data_type': 'CreditDebitCode',
        },
        'available_balance_amount': {
            'business_name': 'Available Balance Amount',
            'business_description': 'Per ISO 20022: Available balance amount.',
            'iso_element_name': 'Amount',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Bal[Tp/CdOrPrtry/Cd=AVBL]/Amt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'available_balance_currency': {
            'business_name': 'Available Balance Currency',
            'business_description': 'Currency of the available balance.',
            'iso_element_name': 'Currency',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Bal[Tp/CdOrPrtry/Cd=AVBL]/Amt/@Ccy',
            'iso_data_type': 'ActiveOrHistoricCurrencyCode',
        },
        'available_balance_date': {
            'business_name': 'Available Balance Date',
            'business_description': 'Date of the available balance.',
            'iso_element_name': 'Date',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Bal[Tp/CdOrPrtry/Cd=AVBL]/Dt/Dt',
            'iso_data_type': 'ISODate',
        },
        'number_of_entries': {
            'business_name': 'Number of Entries',
            'business_description': 'Total number of entries in the statement.',
            'iso_element_name': 'NumberOfEntries',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/TxsSummry/TtlNtries/NbOfNtries',
            'iso_data_type': 'Max15NumericText',
        },
        'sum_of_credit_entries': {
            'business_name': 'Sum of Credit Entries',
            'business_description': 'Per ISO 20022: Total sum of credit entries.',
            'iso_element_name': 'Sum',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/TxsSummry/TtlCdtNtries/Sum',
            'iso_data_type': 'DecimalNumber',
        },
        'sum_of_debit_entries': {
            'business_name': 'Sum of Debit Entries',
            'business_description': 'Per ISO 20022: Total sum of debit entries.',
            'iso_element_name': 'Sum',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/TxsSummry/TtlDbtNtries/Sum',
            'iso_data_type': 'DecimalNumber',
        },
        # Metadata/system fields
        'source_message_type': {
            'business_name': 'Source Message Type',
            'business_description': 'Type of the source message (e.g., camt.053, MT940).',
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
        'source_stg_table': {
            'business_name': 'Source Staging Table',
            'business_description': 'Name of the Silver layer staging table.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'scheme_code': {
            'business_name': 'Scheme Code',
            'business_description': 'Payment scheme or clearing system code.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'region': {
            'business_name': 'Region',
            'business_description': 'Geographic region for the statement.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'lineage_batch_id': {
            'business_name': 'Lineage Batch ID',
            'business_description': 'Batch identifier for data lineage tracking.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        # SCD Type 2 fields
        'is_current': {
            'business_name': 'Is Current',
            'business_description': 'Indicates if this is the current/active version of the record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'is_deleted': {
            'business_name': 'Is Deleted',
            'business_description': 'Soft delete flag indicating if the record has been logically deleted.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'valid_from': {
            'business_name': 'Valid From',
            'business_description': 'Start timestamp for record validity (SCD Type 2).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': 'ISODateTime',
        },
        'valid_to': {
            'business_name': 'Valid To',
            'business_description': 'End timestamp for record validity (SCD Type 2).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': 'ISODateTime',
        },
        'record_version': {
            'business_name': 'Record Version',
            'business_description': 'Version number for this record (SCD Type 2).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'updated_by': {
            'business_name': 'Updated By',
            'business_description': 'User or system that last updated this record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'current_status': {
            'business_name': 'Current Status',
            'business_description': 'Current processing status of the statement record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'data_quality_score': {
            'business_name': 'Data Quality Score',
            'business_description': 'Computed data quality score for the record (0-100).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'data_quality_issues': {
            'business_name': 'Data Quality Issues',
            'business_description': 'JSON array of identified data quality issues.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'partition_year': {
            'business_name': 'Partition Year',
            'business_description': 'Year used for table partitioning.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'partition_month': {
            'business_name': 'Partition Month',
            'business_description': 'Month used for table partitioning.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },
}

# CDM Statement Extension
CDM_STATEMENT_EXTENSION = {
    'cdm_statement_extension': {
        'extension_id': {
            'business_name': 'Extension ID',
            'business_description': 'Unique identifier for this statement extension record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'statement_id': {
            'business_name': 'Statement ID',
            'business_description': 'Reference to the parent statement.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'extension_type': {
            'business_name': 'Extension Type',
            'business_description': 'Type of statement extension.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'extension_data': {
            'business_name': 'Extension Data',
            'business_description': 'JSON or XML blob containing format-specific extension data.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_message_type': {
            'business_name': 'Source Message Type',
            'business_description': 'Type of the source message (e.g., MT940, camt.053).',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'sequence_number_mt': {
            'business_name': 'Sequence Number (MT)',
            'business_description': 'For SWIFT MT messages: Statement sequence number from field :28C:.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'statement_number': {
            'business_name': 'Statement Number',
            'business_description': 'Statement number or page number within a multi-page statement.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'additional_statement_info': {
            'business_name': 'Additional Statement Information',
            'business_description': 'Additional free-text information about the statement.',
            'iso_element_name': 'AdditionalStatementInformation',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/AddtlStmtInf',
            'iso_data_type': 'Max500Text',
        },
        'available_balance_type': {
            'business_name': 'Available Balance Type',
            'business_description': 'Type of available balance: AVBL (Available), FWAV (Forward Available), etc.',
            'iso_element_name': 'Code',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Bal/Tp/CdOrPrtry/Cd',
            'iso_data_type': 'ExternalBalanceType1Code',
        },
        'forward_available_balance': {
            'business_name': 'Forward Available Balance',
            'business_description': 'Per ISO 20022: Forward available balance amount.',
            'iso_element_name': 'Amount',
            'iso_element_path': 'Document/BkToCstmrStmt/Stmt/Bal[Tp/CdOrPrtry/Cd=FWAV]/Amt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'entries': {
            'business_name': 'Entries',
            'business_description': 'JSON array containing statement entry/transaction details.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },
}

# Combine all supporting table definitions
CDM_SUPPORTING_TABLES = {}
CDM_SUPPORTING_TABLES.update(CDM_PARTY_IDENTIFIERS)
CDM_SUPPORTING_TABLES.update(CDM_ACCOUNT_IDENTIFIERS)
CDM_SUPPORTING_TABLES.update(CDM_INSTITUTION_IDENTIFIERS)
CDM_SUPPORTING_TABLES.update(CDM_IDENTIFIER_TYPE)
CDM_SUPPORTING_TABLES.update(CDM_PAYMENT_EVENT)
CDM_SUPPORTING_TABLES.update(CDM_PAYMENT_STATUS)
CDM_SUPPORTING_TABLES.update(CDM_PAYMENT_IDENTIFIERS)
CDM_SUPPORTING_TABLES.update(CDM_DOCUMENT_IDENTIFIER)
CDM_SUPPORTING_TABLES.update(CDM_TRANSACTION_IDENTIFIER)
CDM_SUPPORTING_TABLES.update(CDM_CHARGE)
CDM_SUPPORTING_TABLES.update(CDM_REMITTANCE_INFORMATION)
CDM_SUPPORTING_TABLES.update(CDM_SETTLEMENT)
CDM_SUPPORTING_TABLES.update(CDM_REGULATORY_REPORTING)
CDM_SUPPORTING_TABLES.update(CDM_ACCOUNT_STATEMENT)
CDM_SUPPORTING_TABLES.update(CDM_STATEMENT_EXTENSION)
