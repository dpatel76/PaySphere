"""
CDM Catalog Definitions - ISO 20022 camt (Cash Management) Tables
Includes camt.053 (Bank to Customer Statement), camt.052 (Bank to Customer Account Report),
camt.054 (Bank to Customer Debit Credit Notification), camt.056 (FI Payment Cancellation Request)
"""

# Common camt fields for statements and reports
_COMMON_CAMT_FIELDS = {
    'statement_id': {
        'business_name': 'Statement ID',
        'business_description': 'Unique identifier for this statement in the CDM.',
        'iso_element_name': None,
        'iso_element_path': None,
        'iso_data_type': None,
    },
    'message_id': {
        'business_name': 'Message Identification',
        'business_description': 'Per ISO 20022: Point-to-point reference assigned by the account servicer to identify the message.',
        'iso_element_name': 'MessageIdentification',
        'iso_element_path': 'GrpHdr/MsgId',
        'iso_data_type': 'Max35Text',
    },
    'creation_datetime': {
        'business_name': 'Creation Date Time',
        'business_description': 'Per ISO 20022: Date and time at which the message was created.',
        'iso_element_name': 'CreationDateTime',
        'iso_element_path': 'GrpHdr/CreDtTm',
        'iso_data_type': 'ISODateTime',
    },
    'message_pagination_page_number': {
        'business_name': 'Page Number',
        'business_description': 'Per ISO 20022: Page number of the message within a sequence.',
        'iso_element_name': 'PageNumber',
        'iso_element_path': 'GrpHdr/MsgPgntn/PgNb',
        'iso_data_type': 'Max5NumericText',
    },
    'message_pagination_last_page': {
        'business_name': 'Last Page Indicator',
        'business_description': 'Per ISO 20022: Indicates if this is the last page.',
        'iso_element_name': 'LastPageIndicator',
        'iso_element_path': 'GrpHdr/MsgPgntn/LastPgInd',
        'iso_data_type': 'YesNoIndicator',
    },
    # Statement Identification
    'statement_identification': {
        'business_name': 'Statement Identification',
        'business_description': 'Per ISO 20022: Unique identification assigned by the account servicer to identify the statement.',
        'iso_element_name': 'Identification',
        'iso_element_path': 'Stmt/Id',
        'iso_data_type': 'Max35Text',
    },
    'electronic_sequence_number': {
        'business_name': 'Electronic Sequence Number',
        'business_description': 'Per ISO 20022: Sequential number assigned by the account servicer.',
        'iso_element_name': 'ElectronicSequenceNumber',
        'iso_element_path': 'Stmt/ElctrncSeqNb',
        'iso_data_type': 'Number',
    },
    'legal_sequence_number': {
        'business_name': 'Legal Sequence Number',
        'business_description': 'Per ISO 20022: Legal sequential number assigned by the account servicer.',
        'iso_element_name': 'LegalSequenceNumber',
        'iso_element_path': 'Stmt/LglSeqNb',
        'iso_data_type': 'Number',
    },
    'creation_date': {
        'business_name': 'Statement Creation Date',
        'business_description': 'Per ISO 20022: Date the statement was created.',
        'iso_element_name': 'CreationDateTime',
        'iso_element_path': 'Stmt/CreDtTm',
        'iso_data_type': 'ISODateTime',
    },
    'from_datetime': {
        'business_name': 'From Date Time',
        'business_description': 'Per ISO 20022: Start date and time of the reporting period.',
        'iso_element_name': 'FromDateTime',
        'iso_element_path': 'Stmt/FrToDt/FrDtTm',
        'iso_data_type': 'ISODateTime',
    },
    'to_datetime': {
        'business_name': 'To Date Time',
        'business_description': 'Per ISO 20022: End date and time of the reporting period.',
        'iso_element_name': 'ToDateTime',
        'iso_element_path': 'Stmt/FrToDt/ToDtTm',
        'iso_data_type': 'ISODateTime',
    },
    # Account Information
    'account_iban': {
        'business_name': 'Account IBAN',
        'business_description': 'Per ISO 20022: IBAN of the account being reported.',
        'iso_element_name': 'IBAN',
        'iso_element_path': 'Stmt/Acct/Id/IBAN',
        'iso_data_type': 'IBAN2007Identifier',
    },
    'account_other_id': {
        'business_name': 'Account Other ID',
        'business_description': 'Per ISO 20022: Other identification of the account.',
        'iso_element_name': 'Identification',
        'iso_element_path': 'Stmt/Acct/Id/Othr/Id',
        'iso_data_type': 'Max34Text',
    },
    'account_type': {
        'business_name': 'Account Type',
        'business_description': 'Per ISO 20022: Type of the account. CACC, SVGS, LOAN.',
        'iso_element_name': 'Code',
        'iso_element_path': 'Stmt/Acct/Tp/Cd',
        'iso_data_type': 'ExternalCashAccountType1Code',
    },
    'account_currency': {
        'business_name': 'Account Currency',
        'business_description': 'Per ISO 20022: Currency of the account.',
        'iso_element_name': 'Currency',
        'iso_element_path': 'Stmt/Acct/Ccy',
        'iso_data_type': 'ActiveOrHistoricCurrencyCode',
    },
    'account_name': {
        'business_name': 'Account Name',
        'business_description': 'Per ISO 20022: Name of the account.',
        'iso_element_name': 'Name',
        'iso_element_path': 'Stmt/Acct/Nm',
        'iso_data_type': 'Max70Text',
    },
    # Account Owner
    'account_owner_name': {
        'business_name': 'Account Owner Name',
        'business_description': 'Per ISO 20022: Name of the account owner.',
        'iso_element_name': 'Name',
        'iso_element_path': 'Stmt/Acct/Ownr/Nm',
        'iso_data_type': 'Max140Text',
    },
    'account_owner_id': {
        'business_name': 'Account Owner ID',
        'business_description': 'Per ISO 20022: Identification of the account owner.',
        'iso_element_name': 'Identification',
        'iso_element_path': 'Stmt/Acct/Ownr/Id',
        'iso_data_type': 'Party38Choice',
    },
    'account_owner_country': {
        'business_name': 'Account Owner Country',
        'business_description': 'Per ISO 20022: Country of the account owner.',
        'iso_element_name': 'Country',
        'iso_element_path': 'Stmt/Acct/Ownr/PstlAdr/Ctry',
        'iso_data_type': 'CountryCode',
    },
    # Account Servicer
    'account_servicer_bic': {
        'business_name': 'Account Servicer BIC',
        'business_description': 'Per ISO 20022: BIC of the account servicing institution.',
        'iso_element_name': 'BICFI',
        'iso_element_path': 'Stmt/Acct/Svcr/FinInstnId/BICFI',
        'iso_data_type': 'BICFIDec2014Identifier',
    },
    'account_servicer_name': {
        'business_name': 'Account Servicer Name',
        'business_description': 'Per ISO 20022: Name of the account servicing institution.',
        'iso_element_name': 'Name',
        'iso_element_path': 'Stmt/Acct/Svcr/FinInstnId/Nm',
        'iso_data_type': 'Max140Text',
    },
    'account_servicer_clearing_id': {
        'business_name': 'Account Servicer Clearing ID',
        'business_description': 'Per ISO 20022: Clearing system member ID of the account servicer.',
        'iso_element_name': 'MemberId',
        'iso_element_path': 'Stmt/Acct/Svcr/FinInstnId/ClrSysMmbId/MmbId',
        'iso_data_type': 'Max35Text',
    },
    'account_servicer_lei': {
        'business_name': 'Account Servicer LEI',
        'business_description': 'Per ISO 20022: LEI of the account servicer.',
        'iso_element_name': 'LEI',
        'iso_element_path': 'Stmt/Acct/Svcr/FinInstnId/LEI',
        'iso_data_type': 'LEIIdentifier',
    },
    'account_servicer_country': {
        'business_name': 'Account Servicer Country',
        'business_description': 'Per ISO 20022: Country of the account servicer.',
        'iso_element_name': 'Country',
        'iso_element_path': 'Stmt/Acct/Svcr/FinInstnId/PstlAdr/Ctry',
        'iso_data_type': 'CountryCode',
    },
    # Balances
    'opening_booked_balance_amount': {
        'business_name': 'Opening Booked Balance Amount',
        'business_description': 'Per ISO 20022: Opening balance that is posted to the account at the start of the period.',
        'iso_element_name': 'Amount',
        'iso_element_path': 'Stmt/Bal[Tp/CdOrPrtry/Cd=OPBD]/Amt',
        'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
    },
    'opening_booked_balance_currency': {
        'business_name': 'Opening Booked Balance Currency',
        'business_description': 'Per ISO 20022: Currency of the opening booked balance.',
        'iso_element_name': 'Currency',
        'iso_element_path': 'Stmt/Bal[Tp/CdOrPrtry/Cd=OPBD]/Amt/@Ccy',
        'iso_data_type': 'ActiveOrHistoricCurrencyCode',
    },
    'opening_booked_balance_indicator': {
        'business_name': 'Opening Booked Balance Credit/Debit',
        'business_description': 'Per ISO 20022: Indicates if opening balance is credit (CRDT) or debit (DBIT).',
        'iso_element_name': 'CreditDebitIndicator',
        'iso_element_path': 'Stmt/Bal[Tp/CdOrPrtry/Cd=OPBD]/CdtDbtInd',
        'iso_data_type': 'CreditDebitCode',
    },
    'opening_booked_balance_date': {
        'business_name': 'Opening Booked Balance Date',
        'business_description': 'Per ISO 20022: Date of the opening booked balance.',
        'iso_element_name': 'Date',
        'iso_element_path': 'Stmt/Bal[Tp/CdOrPrtry/Cd=OPBD]/Dt/Dt',
        'iso_data_type': 'ISODate',
    },
    'closing_booked_balance_amount': {
        'business_name': 'Closing Booked Balance Amount',
        'business_description': 'Per ISO 20022: Closing balance posted to account at end of period.',
        'iso_element_name': 'Amount',
        'iso_element_path': 'Stmt/Bal[Tp/CdOrPrtry/Cd=CLBD]/Amt',
        'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
    },
    'closing_booked_balance_currency': {
        'business_name': 'Closing Booked Balance Currency',
        'business_description': 'Per ISO 20022: Currency of the closing booked balance.',
        'iso_element_name': 'Currency',
        'iso_element_path': 'Stmt/Bal[Tp/CdOrPrtry/Cd=CLBD]/Amt/@Ccy',
        'iso_data_type': 'ActiveOrHistoricCurrencyCode',
    },
    'closing_booked_balance_indicator': {
        'business_name': 'Closing Booked Balance Credit/Debit',
        'business_description': 'Per ISO 20022: Indicates if closing balance is credit or debit.',
        'iso_element_name': 'CreditDebitIndicator',
        'iso_element_path': 'Stmt/Bal[Tp/CdOrPrtry/Cd=CLBD]/CdtDbtInd',
        'iso_data_type': 'CreditDebitCode',
    },
    'closing_booked_balance_date': {
        'business_name': 'Closing Booked Balance Date',
        'business_description': 'Per ISO 20022: Date of the closing booked balance.',
        'iso_element_name': 'Date',
        'iso_element_path': 'Stmt/Bal[Tp/CdOrPrtry/Cd=CLBD]/Dt/Dt',
        'iso_data_type': 'ISODate',
    },
    'closing_available_balance_amount': {
        'business_name': 'Closing Available Balance Amount',
        'business_description': 'Per ISO 20022: Available balance at end of period.',
        'iso_element_name': 'Amount',
        'iso_element_path': 'Stmt/Bal[Tp/CdOrPrtry/Cd=CLAV]/Amt',
        'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
    },
    'closing_available_balance_currency': {
        'business_name': 'Closing Available Balance Currency',
        'business_description': 'Per ISO 20022: Currency of the closing available balance.',
        'iso_element_name': 'Currency',
        'iso_element_path': 'Stmt/Bal[Tp/CdOrPrtry/Cd=CLAV]/Amt/@Ccy',
        'iso_data_type': 'ActiveOrHistoricCurrencyCode',
    },
    'forward_available_balance_amount': {
        'business_name': 'Forward Available Balance Amount',
        'business_description': 'Per ISO 20022: Balance that will be available at a future date.',
        'iso_element_name': 'Amount',
        'iso_element_path': 'Stmt/Bal[Tp/CdOrPrtry/Cd=FWAV]/Amt',
        'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
    },
    # Transaction Summary
    'number_of_entries': {
        'business_name': 'Number of Entries',
        'business_description': 'Per ISO 20022: Total number of entries in the statement.',
        'iso_element_name': 'NumberOfEntries',
        'iso_element_path': 'Stmt/TxsSummry/TtlNtries/NbOfNtries',
        'iso_data_type': 'Max15NumericText',
    },
    'sum_of_entries': {
        'business_name': 'Sum of Entries',
        'business_description': 'Per ISO 20022: Total sum of all entries.',
        'iso_element_name': 'Sum',
        'iso_element_path': 'Stmt/TxsSummry/TtlNtries/Sum',
        'iso_data_type': 'DecimalNumber',
    },
    'total_credit_entries_number': {
        'business_name': 'Total Credit Entries Number',
        'business_description': 'Per ISO 20022: Number of credit entries.',
        'iso_element_name': 'NumberOfEntries',
        'iso_element_path': 'Stmt/TxsSummry/TtlCdtNtries/NbOfNtries',
        'iso_data_type': 'Max15NumericText',
    },
    'total_credit_entries_sum': {
        'business_name': 'Total Credit Entries Sum',
        'business_description': 'Per ISO 20022: Sum of credit entries.',
        'iso_element_name': 'Sum',
        'iso_element_path': 'Stmt/TxsSummry/TtlCdtNtries/Sum',
        'iso_data_type': 'DecimalNumber',
    },
    'total_debit_entries_number': {
        'business_name': 'Total Debit Entries Number',
        'business_description': 'Per ISO 20022: Number of debit entries.',
        'iso_element_name': 'NumberOfEntries',
        'iso_element_path': 'Stmt/TxsSummry/TtlDbtNtries/NbOfNtries',
        'iso_data_type': 'Max15NumericText',
    },
    'total_debit_entries_sum': {
        'business_name': 'Total Debit Entries Sum',
        'business_description': 'Per ISO 20022: Sum of debit entries.',
        'iso_element_name': 'Sum',
        'iso_element_path': 'Stmt/TxsSummry/TtlDbtNtries/Sum',
        'iso_data_type': 'DecimalNumber',
    },
    # Entry Details (for individual transactions)
    'entry_reference': {
        'business_name': 'Entry Reference',
        'business_description': 'Per ISO 20022: Unique reference for the entry as assigned by the servicer.',
        'iso_element_name': 'EntryReference',
        'iso_element_path': 'Stmt/Ntry/NtryRef',
        'iso_data_type': 'Max35Text',
    },
    'entry_amount': {
        'business_name': 'Entry Amount',
        'business_description': 'Per ISO 20022: Amount of money in the entry.',
        'iso_element_name': 'Amount',
        'iso_element_path': 'Stmt/Ntry/Amt',
        'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
    },
    'entry_currency': {
        'business_name': 'Entry Currency',
        'business_description': 'Per ISO 20022: Currency of the entry amount.',
        'iso_element_name': 'Currency',
        'iso_element_path': 'Stmt/Ntry/Amt/@Ccy',
        'iso_data_type': 'ActiveOrHistoricCurrencyCode',
    },
    'entry_credit_debit_indicator': {
        'business_name': 'Entry Credit/Debit Indicator',
        'business_description': 'Per ISO 20022: Indicates if entry is credit or debit.',
        'iso_element_name': 'CreditDebitIndicator',
        'iso_element_path': 'Stmt/Ntry/CdtDbtInd',
        'iso_data_type': 'CreditDebitCode',
    },
    'entry_reversal_indicator': {
        'business_name': 'Entry Reversal Indicator',
        'business_description': 'Per ISO 20022: Indicates if entry is a reversal of a previous entry.',
        'iso_element_name': 'ReversalIndicator',
        'iso_element_path': 'Stmt/Ntry/RvslInd',
        'iso_data_type': 'TrueFalseIndicator',
    },
    'entry_status': {
        'business_name': 'Entry Status',
        'business_description': 'Per ISO 20022: Status of the entry. BOOK, PDNG, INFO.',
        'iso_element_name': 'Status',
        'iso_element_path': 'Stmt/Ntry/Sts/Cd',
        'iso_data_type': 'EntryStatus1Code',
    },
    'entry_booking_date': {
        'business_name': 'Entry Booking Date',
        'business_description': 'Per ISO 20022: Date entry was posted to account.',
        'iso_element_name': 'Date',
        'iso_element_path': 'Stmt/Ntry/BookgDt/Dt',
        'iso_data_type': 'ISODate',
    },
    'entry_value_date': {
        'business_name': 'Entry Value Date',
        'business_description': 'Per ISO 20022: Date entry became effective for interest calculation.',
        'iso_element_name': 'Date',
        'iso_element_path': 'Stmt/Ntry/ValDt/Dt',
        'iso_data_type': 'ISODate',
    },
    'entry_account_servicer_reference': {
        'business_name': 'Entry Account Servicer Reference',
        'business_description': 'Per ISO 20022: Reference assigned by the account servicer.',
        'iso_element_name': 'AccountServicerReference',
        'iso_element_path': 'Stmt/Ntry/AcctSvcrRef',
        'iso_data_type': 'Max35Text',
    },
    # Bank Transaction Code
    'bank_transaction_code_domain': {
        'business_name': 'Bank Transaction Code Domain',
        'business_description': 'Per ISO 20022: Domain of the bank transaction code (e.g., PMNT for payments).',
        'iso_element_name': 'Code',
        'iso_element_path': 'Stmt/Ntry/BkTxCd/Domn/Cd',
        'iso_data_type': 'ExternalBankTransactionDomain1Code',
    },
    'bank_transaction_code_family': {
        'business_name': 'Bank Transaction Code Family',
        'business_description': 'Per ISO 20022: Family within the domain.',
        'iso_element_name': 'Code',
        'iso_element_path': 'Stmt/Ntry/BkTxCd/Domn/Fmly/Cd',
        'iso_data_type': 'ExternalBankTransactionFamily1Code',
    },
    'bank_transaction_code_subfamily': {
        'business_name': 'Bank Transaction Code SubFamily',
        'business_description': 'Per ISO 20022: SubFamily within the family.',
        'iso_element_name': 'Code',
        'iso_element_path': 'Stmt/Ntry/BkTxCd/Domn/Fmly/SubFmlyCd',
        'iso_data_type': 'ExternalBankTransactionSubFamily1Code',
    },
    'bank_transaction_code_proprietary': {
        'business_name': 'Bank Transaction Code Proprietary',
        'business_description': 'Per ISO 20022: Proprietary bank transaction code.',
        'iso_element_name': 'Code',
        'iso_element_path': 'Stmt/Ntry/BkTxCd/Prtry/Cd',
        'iso_data_type': 'Max35Text',
    },
    # Transaction Details
    'transaction_end_to_end_id': {
        'business_name': 'Transaction End to End ID',
        'business_description': 'Per ISO 20022: End to end identification of the original payment.',
        'iso_element_name': 'EndToEndIdentification',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/Refs/EndToEndId',
        'iso_data_type': 'Max35Text',
    },
    'transaction_message_id': {
        'business_name': 'Transaction Message ID',
        'business_description': 'Per ISO 20022: Message identification of the original payment.',
        'iso_element_name': 'MessageIdentification',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/Refs/MsgId',
        'iso_data_type': 'Max35Text',
    },
    'transaction_account_servicer_ref': {
        'business_name': 'Transaction Account Servicer Reference',
        'business_description': 'Per ISO 20022: Reference assigned by the account servicer.',
        'iso_element_name': 'AccountServicerReference',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/Refs/AcctSvcrRef',
        'iso_data_type': 'Max35Text',
    },
    'transaction_payment_info_id': {
        'business_name': 'Transaction Payment Info ID',
        'business_description': 'Per ISO 20022: Payment information identification.',
        'iso_element_name': 'PaymentInformationIdentification',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/Refs/PmtInfId',
        'iso_data_type': 'Max35Text',
    },
    'transaction_instruction_id': {
        'business_name': 'Transaction Instruction ID',
        'business_description': 'Per ISO 20022: Instruction identification.',
        'iso_element_name': 'InstructionIdentification',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/Refs/InstrId',
        'iso_data_type': 'Max35Text',
    },
    'transaction_mandate_id': {
        'business_name': 'Transaction Mandate ID',
        'business_description': 'Per ISO 20022: Mandate identification for direct debit.',
        'iso_element_name': 'MandateIdentification',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/Refs/MndtId',
        'iso_data_type': 'Max35Text',
    },
    'transaction_uetr': {
        'business_name': 'Transaction UETR',
        'business_description': 'Per ISO 20022: Unique End-to-end Transaction Reference.',
        'iso_element_name': 'UETR',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/Refs/UETR',
        'iso_data_type': 'UUIDv4Identifier',
    },
    # Related Parties
    'transaction_debtor_name': {
        'business_name': 'Transaction Debtor Name',
        'business_description': 'Per ISO 20022: Name of the debtor.',
        'iso_element_name': 'Name',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Dbtr/Nm',
        'iso_data_type': 'Max140Text',
    },
    'transaction_debtor_account': {
        'business_name': 'Transaction Debtor Account',
        'business_description': 'Per ISO 20022: Account of the debtor.',
        'iso_element_name': 'IBAN',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/RltdPties/DbtrAcct/Id/IBAN',
        'iso_data_type': 'IBAN2007Identifier',
    },
    'transaction_creditor_name': {
        'business_name': 'Transaction Creditor Name',
        'business_description': 'Per ISO 20022: Name of the creditor.',
        'iso_element_name': 'Name',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/RltdPties/Cdtr/Nm',
        'iso_data_type': 'Max140Text',
    },
    'transaction_creditor_account': {
        'business_name': 'Transaction Creditor Account',
        'business_description': 'Per ISO 20022: Account of the creditor.',
        'iso_element_name': 'IBAN',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/RltdPties/CdtrAcct/Id/IBAN',
        'iso_data_type': 'IBAN2007Identifier',
    },
    'transaction_ultimate_debtor_name': {
        'business_name': 'Transaction Ultimate Debtor Name',
        'business_description': 'Per ISO 20022: Name of the ultimate debtor.',
        'iso_element_name': 'Name',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/RltdPties/UltmtDbtr/Nm',
        'iso_data_type': 'Max140Text',
    },
    'transaction_ultimate_creditor_name': {
        'business_name': 'Transaction Ultimate Creditor Name',
        'business_description': 'Per ISO 20022: Name of the ultimate creditor.',
        'iso_element_name': 'Name',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/RltdPties/UltmtCdtr/Nm',
        'iso_data_type': 'Max140Text',
    },
    # Related Agents
    'transaction_debtor_agent_bic': {
        'business_name': 'Transaction Debtor Agent BIC',
        'business_description': 'Per ISO 20022: BIC of the debtor agent.',
        'iso_element_name': 'BICFI',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/BICFI',
        'iso_data_type': 'BICFIDec2014Identifier',
    },
    'transaction_creditor_agent_bic': {
        'business_name': 'Transaction Creditor Agent BIC',
        'business_description': 'Per ISO 20022: BIC of the creditor agent.',
        'iso_element_name': 'BICFI',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/BICFI',
        'iso_data_type': 'BICFIDec2014Identifier',
    },
    # Remittance Information
    'remittance_unstructured': {
        'business_name': 'Remittance Information Unstructured',
        'business_description': 'Per ISO 20022: Unstructured remittance information.',
        'iso_element_name': 'Unstructured',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Ustrd',
        'iso_data_type': 'Max140Text',
    },
    'remittance_structured': {
        'business_name': 'Remittance Information Structured',
        'business_description': 'Per ISO 20022: Structured remittance information.',
        'iso_element_name': 'Structured',
        'iso_element_path': 'Stmt/Ntry/NtryDtls/TxDtls/RmtInf/Strd',
        'iso_data_type': 'StructuredRemittanceInformation16',
    },
    # Additional Entry Info
    'additional_entry_info': {
        'business_name': 'Additional Entry Information',
        'business_description': 'Per ISO 20022: Additional information about the entry.',
        'iso_element_name': 'AdditionalEntryInformation',
        'iso_element_path': 'Stmt/Ntry/AddtlNtryInf',
        'iso_data_type': 'Max500Text',
    },
    # Source/Lineage fields
    'source_format': {
        'business_name': 'Source Format',
        'business_description': 'Original message format from which this record was derived.',
        'iso_element_name': None,
        'iso_element_path': None,
        'iso_data_type': None,
    },
    'source_stg_table': {
        'business_name': 'Source Staging Table',
        'business_description': 'Silver layer staging table from which this record was derived.',
        'iso_element_name': None,
        'iso_element_path': None,
        'iso_data_type': None,
    },
    'stg_id': {
        'business_name': 'Staging ID',
        'business_description': 'Reference to the Silver layer staging record.',
        'iso_element_name': None,
        'iso_element_path': None,
        'iso_data_type': None,
    },
    'raw_id': {
        'business_name': 'Raw ID',
        'business_description': 'Reference to the Bronze layer raw record.',
        'iso_element_name': None,
        'iso_element_path': None,
        'iso_data_type': None,
    },
    'batch_id': {
        'business_name': 'Batch ID',
        'business_description': 'Identifier of the processing batch.',
        'iso_element_name': None,
        'iso_element_path': None,
        'iso_data_type': None,
    },
    'processing_status': {
        'business_name': 'Processing Status',
        'business_description': 'Current processing status in the CDM pipeline.',
        'iso_element_name': None,
        'iso_element_path': None,
        'iso_data_type': None,
    },
}

# camt.053 - Bank to Customer Statement
CDM_CAMT_BANK_TO_CUSTOMER_STATEMENT = {
    'cdm_camt_bank_to_customer_statement': _COMMON_CAMT_FIELDS,
}

# camt.052 - Bank to Customer Account Report (intraday report, same structure as statement)
CDM_CAMT_BANK_TO_CUSTOMER_ACCOUNT_REPORT = {
    'cdm_camt_bank_to_customer_account_report': {
        **_COMMON_CAMT_FIELDS,
        'report_identification': {
            'business_name': 'Report Identification',
            'business_description': 'Per ISO 20022: Unique identification of the account report.',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Rpt/Id',
            'iso_data_type': 'Max35Text',
        },
    },
}

# camt.054 - Bank to Customer Debit Credit Notification
CDM_CAMT_BANK_TO_CUSTOMER_DEBIT_CREDIT_NOTIFICATION = {
    'cdm_camt_bank_to_customer_debit_credit_notification': {
        **{k: v for k, v in _COMMON_CAMT_FIELDS.items() if k not in [
            # Exclude balance fields not relevant for notifications
            'opening_booked_balance_amount', 'opening_booked_balance_currency',
            'opening_booked_balance_indicator', 'opening_booked_balance_date',
            'closing_booked_balance_amount', 'closing_booked_balance_currency',
            'closing_booked_balance_indicator', 'closing_booked_balance_date',
            'closing_available_balance_amount', 'closing_available_balance_currency',
            'forward_available_balance_amount'
        ]},
        'notification_identification': {
            'business_name': 'Notification Identification',
            'business_description': 'Per ISO 20022: Unique identification of the notification.',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Ntfctn/Id',
            'iso_data_type': 'Max35Text',
        },
    },
}

# camt.056 - FI to FI Payment Cancellation Request
CDM_CAMT_FI_PAYMENT_CANCELLATION_REQUEST = {
    'cdm_camt_fi_payment_cancellation_request': {
        'cancellation_id': {
            'business_name': 'Cancellation ID',
            'business_description': 'Unique identifier for this cancellation request in the CDM.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'message_id': {
            'business_name': 'Message Identification',
            'business_description': 'Per ISO 20022: Reference assigned by the assigner to identify the request.',
            'iso_element_name': 'MessageIdentification',
            'iso_element_path': 'GrpHdr/MsgId',
            'iso_data_type': 'Max35Text',
        },
        'creation_datetime': {
            'business_name': 'Creation Date Time',
            'business_description': 'Per ISO 20022: Date and time at which the message was created.',
            'iso_element_name': 'CreationDateTime',
            'iso_element_path': 'GrpHdr/CreDtTm',
            'iso_data_type': 'ISODateTime',
        },
        'number_of_transactions': {
            'business_name': 'Number of Transactions',
            'business_description': 'Per ISO 20022: Number of transactions to be cancelled.',
            'iso_element_name': 'NumberOfTransactions',
            'iso_element_path': 'GrpHdr/NbOfTxs',
            'iso_data_type': 'Max15NumericText',
        },
        'control_sum': {
            'business_name': 'Control Sum',
            'business_description': 'Per ISO 20022: Total amount to be cancelled.',
            'iso_element_name': 'ControlSum',
            'iso_element_path': 'GrpHdr/CtrlSum',
            'iso_data_type': 'DecimalNumber',
        },
        # Assigning Party
        'assigning_party_name': {
            'business_name': 'Assigning Party Name',
            'business_description': 'Per ISO 20022: Name of the party that assigns the case.',
            'iso_element_name': 'Name',
            'iso_element_path': 'Assgnmt/Assgnr/Nm',
            'iso_data_type': 'Max140Text',
        },
        'assigning_party_bic': {
            'business_name': 'Assigning Party BIC',
            'business_description': 'Per ISO 20022: BIC of the assigning party.',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'Assgnmt/Assgnr/Agt/FinInstnId/BICFI',
            'iso_data_type': 'BICFIDec2014Identifier',
        },
        # Assigned Party
        'assigned_party_name': {
            'business_name': 'Assigned Party Name',
            'business_description': 'Per ISO 20022: Name of the party to which the case is assigned.',
            'iso_element_name': 'Name',
            'iso_element_path': 'Assgnmt/Assgne/Nm',
            'iso_data_type': 'Max140Text',
        },
        'assigned_party_bic': {
            'business_name': 'Assigned Party BIC',
            'business_description': 'Per ISO 20022: BIC of the assigned party.',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'Assgnmt/Assgne/Agt/FinInstnId/BICFI',
            'iso_data_type': 'BICFIDec2014Identifier',
        },
        # Case Identification
        'case_id': {
            'business_name': 'Case Identification',
            'business_description': 'Per ISO 20022: Unique identification of the case.',
            'iso_element_name': 'Identification',
            'iso_element_path': 'Case/Id',
            'iso_data_type': 'Max35Text',
        },
        'case_creator_bic': {
            'business_name': 'Case Creator BIC',
            'business_description': 'Per ISO 20022: BIC of the party that created the case.',
            'iso_element_name': 'BICFI',
            'iso_element_path': 'Case/Cretr/Agt/FinInstnId/BICFI',
            'iso_data_type': 'BICFIDec2014Identifier',
        },
        # Original Payment Information
        'original_message_id': {
            'business_name': 'Original Message Identification',
            'business_description': 'Per ISO 20022: Message identification of the original payment.',
            'iso_element_name': 'OrgnlMsgId',
            'iso_element_path': 'Undrlyg/OrgnlGrpInfAndCxl/OrgnlMsgId',
            'iso_data_type': 'Max35Text',
        },
        'original_message_name_id': {
            'business_name': 'Original Message Name',
            'business_description': 'Per ISO 20022: Name of the original message type.',
            'iso_element_name': 'OrgnlMsgNmId',
            'iso_element_path': 'Undrlyg/OrgnlGrpInfAndCxl/OrgnlMsgNmId',
            'iso_data_type': 'Max35Text',
        },
        'original_creation_datetime': {
            'business_name': 'Original Creation Date Time',
            'business_description': 'Per ISO 20022: Creation date of the original message.',
            'iso_element_name': 'OrgnlCreDtTm',
            'iso_element_path': 'Undrlyg/OrgnlGrpInfAndCxl/OrgnlCreDtTm',
            'iso_data_type': 'ISODateTime',
        },
        'original_end_to_end_id': {
            'business_name': 'Original End to End ID',
            'business_description': 'Per ISO 20022: End to end ID of the original payment.',
            'iso_element_name': 'EndToEndIdentification',
            'iso_element_path': 'Undrlyg/TxInf/OrgnlEndToEndId',
            'iso_data_type': 'Max35Text',
        },
        'original_transaction_id': {
            'business_name': 'Original Transaction ID',
            'business_description': 'Per ISO 20022: Transaction ID of the original payment.',
            'iso_element_name': 'TransactionIdentification',
            'iso_element_path': 'Undrlyg/TxInf/OrgnlTxId',
            'iso_data_type': 'Max35Text',
        },
        'original_uetr': {
            'business_name': 'Original UETR',
            'business_description': 'Per ISO 20022: UETR of the original payment.',
            'iso_element_name': 'UETR',
            'iso_element_path': 'Undrlyg/TxInf/OrgnlUETR',
            'iso_data_type': 'UUIDv4Identifier',
        },
        'original_interbank_settlement_amount': {
            'business_name': 'Original Interbank Settlement Amount',
            'business_description': 'Per ISO 20022: Amount of the original payment.',
            'iso_element_name': 'Amount',
            'iso_element_path': 'Undrlyg/TxInf/OrgnlIntrBkSttlmAmt',
            'iso_data_type': 'ActiveOrHistoricCurrencyAndAmount',
        },
        'original_interbank_settlement_date': {
            'business_name': 'Original Interbank Settlement Date',
            'business_description': 'Per ISO 20022: Settlement date of the original payment.',
            'iso_element_name': 'Date',
            'iso_element_path': 'Undrlyg/TxInf/OrgnlIntrBkSttlmDt',
            'iso_data_type': 'ISODate',
        },
        # Cancellation Details
        'cancellation_reason_code': {
            'business_name': 'Cancellation Reason Code',
            'business_description': 'Per ISO 20022: Reason for the cancellation request.',
            'iso_element_name': 'Code',
            'iso_element_path': 'Undrlyg/TxInf/CxlRsnInf/Rsn/Cd',
            'iso_data_type': 'ExternalCancellationReason1Code',
        },
        'cancellation_reason_proprietary': {
            'business_name': 'Cancellation Reason Proprietary',
            'business_description': 'Per ISO 20022: Proprietary cancellation reason.',
            'iso_element_name': 'Proprietary',
            'iso_element_path': 'Undrlyg/TxInf/CxlRsnInf/Rsn/Prtry',
            'iso_data_type': 'Max35Text',
        },
        'cancellation_additional_info': {
            'business_name': 'Cancellation Additional Information',
            'business_description': 'Per ISO 20022: Additional info about the cancellation.',
            'iso_element_name': 'AdditionalInformation',
            'iso_element_path': 'Undrlyg/TxInf/CxlRsnInf/AddtlInf',
            'iso_data_type': 'Max105Text',
        },
        # Source/Lineage
        'source_format': {
            'business_name': 'Source Format',
            'business_description': 'Original message format.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'source_stg_table': {
            'business_name': 'Source Staging Table',
            'business_description': 'Silver layer staging table.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'stg_id': {
            'business_name': 'Staging ID',
            'business_description': 'Reference to Silver layer record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'raw_id': {
            'business_name': 'Raw ID',
            'business_description': 'Reference to Bronze layer record.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'batch_id': {
            'business_name': 'Batch ID',
            'business_description': 'Processing batch identifier.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
        'processing_status': {
            'business_name': 'Processing Status',
            'business_description': 'Current processing status.',
            'iso_element_name': None,
            'iso_element_path': None,
            'iso_data_type': None,
        },
    },
}

# Combine all camt definitions
CDM_ISO_CAMT = {}
CDM_ISO_CAMT.update(CDM_CAMT_BANK_TO_CUSTOMER_STATEMENT)
CDM_ISO_CAMT.update(CDM_CAMT_BANK_TO_CUSTOMER_ACCOUNT_REPORT)
CDM_ISO_CAMT.update(CDM_CAMT_BANK_TO_CUSTOMER_DEBIT_CREDIT_NOTIFICATION)
CDM_ISO_CAMT.update(CDM_CAMT_FI_PAYMENT_CANCELLATION_REQUEST)
