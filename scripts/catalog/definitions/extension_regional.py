"""
CDM Catalog Definitions - Regional Payment Extension Tables
Includes BACS, PIX, UPI, CNAPS, KFTC, PAYNOW, PROMPTPAY, SARIE, SWIFT
"""

# BACS - UK Bankers' Automated Clearing Services
CDM_EXTENSION_BACS = {
    'cdm_payment_extension_bacs': {
        'extension_id': {
            'business_name': 'Extension ID',
            'business_description': 'Unique identifier for this BACS extension record.',
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the parent CDM payment instruction.',
        },
        'raw_id': {
            'business_name': 'Raw ID',
            'business_description': 'Reference to the Bronze layer raw message.',
        },
        'format_id': {
            'business_name': 'Format ID',
            'business_description': 'Message format identifier (BACS).',
        },
        'message_type': {
            'business_name': 'Message Type',
            'business_description': 'BACS message type.',
        },
        'silver_message_type': {
            'business_name': 'Silver Message Type',
            'business_description': 'Message type in Silver layer.',
        },
        'processing_status': {
            'business_name': 'Processing Status',
            'business_description': 'Current processing status.',
        },
        'silver_processed_at': {
            'business_name': 'Silver Processed At',
            'business_description': 'Timestamp of Silver processing.',
        },
        'silver_processed_to_gold_at': {
            'business_name': 'Silver Processed to Gold At',
            'business_description': 'Timestamp of Gold processing.',
        },
        # File Header Fields (VOL1, HDR1, HDR2, UHL1)
        'vol1': {
            'business_name': 'VOL1 Record',
            'business_description': 'Volume header record.',
        },
        'hdr1': {
            'business_name': 'HDR1 Record',
            'business_description': 'First header record.',
        },
        'hdr2': {
            'business_name': 'HDR2 Record',
            'business_description': 'Second header record.',
        },
        'uhl1': {
            'business_name': 'UHL1 Record',
            'business_description': 'User header label record.',
        },
        # File Trailer Fields
        'utl1': {
            'business_name': 'UTL1 Record',
            'business_description': 'User trailer label record.',
        },
        'eof1': {
            'business_name': 'EOF1 Record',
            'business_description': 'First end-of-file record.',
        },
        'eof2': {
            'business_name': 'EOF2 Record',
            'business_description': 'Second end-of-file record.',
        },
        # Service User Fields
        'submitter_sun': {
            'business_name': 'Submitter SUN',
            'business_description': 'Service User Number of submitter.',
        },
        'originator_sun': {
            'business_name': 'Originator SUN',
            'business_description': 'Service User Number of originator.',
        },
        'service_user_name': {
            'business_name': 'Service User Name',
            'business_description': 'Name of the service user.',
        },
        # Transaction Details
        'transaction_type': {
            'business_name': 'Transaction Type',
            'business_description': 'Type of BACS transaction.',
        },
        'work_code': {
            'business_name': 'Work Code',
            'business_description': 'BACS work code.',
        },
        'reference': {
            'business_name': 'Reference',
            'business_description': 'Transaction reference.',
        },
        'message_id_ext': {
            'business_name': 'Message ID Extension',
            'business_description': 'Extended message identifier.',
        },
        'free_format_indicator': {
            'business_name': 'Free Format Indicator',
            'business_description': 'Indicates free format text.',
        },
        # Account Fields
        'destination_account_number': {
            'business_name': 'Destination Account Number',
            'business_description': 'Destination account number (8 digits).',
        },
        'originating_account_name': {
            'business_name': 'Originating Account Name',
            'business_description': 'Name on the originating account.',
        },
        # Contra Details
        'contra_sort_code': {
            'business_name': 'Contra Sort Code',
            'business_description': 'Sort code for contra entry.',
        },
        'contra_account_number': {
            'business_name': 'Contra Account Number',
            'business_description': 'Account number for contra entry.',
        },
        'contra_amount': {
            'business_name': 'Contra Amount',
            'business_description': 'Amount for contra entry.',
        },
        'contra_transaction_type': {
            'business_name': 'Contra Transaction Type',
            'business_description': 'Transaction type for contra entry.',
        },
        # Totals
        'credit_count': {
            'business_name': 'Credit Count',
            'business_description': 'Number of credit transactions.',
        },
        'credit_value_total': {
            'business_name': 'Credit Value Total',
            'business_description': 'Total value of credits.',
        },
        'debit_count': {
            'business_name': 'Debit Count',
            'business_description': 'Number of debit transactions.',
        },
        'debit_value_total': {
            'business_name': 'Debit Value Total',
            'business_description': 'Total value of debits.',
        },
        'ddi_count': {
            'business_name': 'DDI Count',
            'business_description': 'Number of Direct Debit Instructions.',
        },
        # File Fields
        'file_sequence_number': {
            'business_name': 'File Sequence Number',
            'business_description': 'Sequence number of the file.',
        },
        'creation_date': {
            'business_name': 'Creation Date',
            'business_description': 'Date the file was created.',
        },
        'currency_code': {
            'business_name': 'Currency Code',
            'business_description': 'Currency code (GBP).',
        },
    },
}

# PIX - Brazil Instant Payments
CDM_EXTENSION_PIX = {
    'cdm_payment_extension_pix': {
        'extension_id': {
            'business_name': 'Extension ID',
            'business_description': 'Unique identifier for this PIX extension record.',
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the parent CDM payment instruction.',
        },
        'stg_id': {
            'business_name': 'Silver Stage ID',
            'business_description': 'Reference to the Silver layer staging record.',
        },
        'raw_id': {
            'business_name': 'Raw ID',
            'business_description': 'Reference to the Bronze layer raw message.',
        },
        'batch_id': {
            'business_name': 'Batch ID',
            'business_description': 'Processing batch identifier.',
        },
        'format_id': {
            'business_name': 'Format ID',
            'business_description': 'Message format identifier (PIX).',
        },
        'message_type': {
            'business_name': 'Message Type',
            'business_description': 'PIX message type code.',
        },
        'processing_status': {
            'business_name': 'Processing Status',
            'business_description': 'Current processing status of the PIX message.',
        },
        'transaction_id': {
            'business_name': 'Transaction ID',
            'business_description': 'Unique PIX transaction identifier.',
        },
        # PIX Key Fields
        'dict_key': {
            'business_name': 'DICT Key',
            'business_description': 'PIX key from the DICT (Diretorio de Identificadores de Contas).',
        },
        'dict_key_type': {
            'business_name': 'DICT Key Type',
            'business_description': 'Type of DICT key: CPF, CNPJ, EMAIL, PHONE, EVP.',
        },
        'dict_owner_type': {
            'business_name': 'DICT Owner Type',
            'business_description': 'Type of key owner: NATURAL_PERSON, LEGAL_PERSON.',
        },
        'dict_creation_date': {
            'business_name': 'DICT Creation Date',
            'business_description': 'Date the DICT key was created.',
        },
        # Payer Fields
        'payer_ispb': {
            'business_name': 'Payer ISPB',
            'business_description': 'ISPB code of the payer institution (8 digits).',
        },
        'payer_account': {
            'business_name': 'Payer Account',
            'business_description': 'Payer account number.',
        },
        'payer_account_type': {
            'business_name': 'Payer Account Type',
            'business_description': 'Type of payer account (CACC, SVGS, etc.).',
        },
        'payer_account_branch': {
            'business_name': 'Payer Account Branch',
            'business_description': 'Payer account branch code.',
        },
        'payer_account_bank_code': {
            'business_name': 'Payer Bank Code',
            'business_description': 'Bank code of the payer.',
        },
        'payer_country': {
            'business_name': 'Payer Country',
            'business_description': 'Country of the payer.',
        },
        # Payee Fields
        'payee_ispb': {
            'business_name': 'Payee ISPB',
            'business_description': 'ISPB code of the payee institution.',
        },
        'payee_account': {
            'business_name': 'Payee Account',
            'business_description': 'Payee account number.',
        },
        'payee_account_type': {
            'business_name': 'Payee Account Type',
            'business_description': 'Type of payee account.',
        },
        'payee_account_branch': {
            'business_name': 'Payee Account Branch',
            'business_description': 'Payee account branch code.',
        },
        'payee_account_bank_code': {
            'business_name': 'Payee Bank Code',
            'business_description': 'Bank code of the payee.',
        },
        # Amount Fields
        'original_amount': {
            'business_name': 'Original Amount',
            'business_description': 'Original transaction amount before adjustments.',
        },
        'final_amount': {
            'business_name': 'Final Amount',
            'business_description': 'Final amount after all adjustments.',
        },
        'change_amount': {
            'business_name': 'Change Amount',
            'business_description': 'Change amount (for PIX Troco).',
        },
        'currency': {
            'business_name': 'Currency',
            'business_description': 'Transaction currency (BRL).',
        },
        # Interest and Fees
        'interest_amount': {
            'business_name': 'Interest Amount',
            'business_description': 'Interest amount applied.',
        },
        'interest_percentage': {
            'business_name': 'Interest Percentage',
            'business_description': 'Interest rate percentage.',
        },
        'fine_amount': {
            'business_name': 'Fine Amount',
            'business_description': 'Fine amount for late payment.',
        },
        'fine_percentage': {
            'business_name': 'Fine Percentage',
            'business_description': 'Fine percentage for late payment.',
        },
        'discount_amount': {
            'business_name': 'Discount Amount',
            'business_description': 'Discount amount applied.',
        },
        'discount_percentage': {
            'business_name': 'Discount Percentage',
            'business_description': 'Discount percentage applied.',
        },
        # Payment Type
        'payment_type': {
            'business_name': 'Payment Type',
            'business_description': 'Type of PIX payment: INSTANT, SCHEDULED, TROCO, SAQUE.',
        },
        'initiation_type': {
            'business_name': 'Initiation Type',
            'business_description': 'How payment was initiated: KEY, MANUAL, QR_CODE, API.',
        },
        'local_instrument': {
            'business_name': 'Local Instrument',
            'business_description': 'PIX local instrument code.',
        },
        # QR Code Fields
        'qr_code_type': {
            'business_name': 'QR Code Type',
            'business_description': 'Type of QR code: STATIC, DYNAMIC.',
        },
        'qr_code_payload': {
            'business_name': 'QR Code Payload',
            'business_description': 'Full QR code payload string.',
        },
        'qr_code_url': {
            'business_name': 'QR Code URL',
            'business_description': 'URL for dynamic QR code.',
        },
        'qr_code_due_date': {
            'business_name': 'QR Code Due Date',
            'business_description': 'Due date from the QR code.',
        },
        'qr_code_expiration_date': {
            'business_name': 'QR Code Expiration Date',
            'business_description': 'Expiration date of the QR code.',
        },
        # SPI Fields (Sistema de Pagamentos Instantâneos)
        'spi_msg_id': {
            'business_name': 'SPI Message ID',
            'business_description': 'SPI message identifier.',
        },
        'spi_creation_date_time': {
            'business_name': 'SPI Creation DateTime',
            'business_description': 'SPI message creation timestamp.',
        },
        'spi_settlement_date_time': {
            'business_name': 'SPI Settlement DateTime',
            'business_description': 'SPI settlement timestamp.',
        },
        'spi_settlement_method': {
            'business_name': 'SPI Settlement Method',
            'business_description': 'SPI settlement method.',
        },
        'scheduled_date': {
            'business_name': 'Scheduled Date',
            'business_description': 'Scheduled date for future-dated PIX.',
        },
        # Return Fields
        'return_id': {
            'business_name': 'Return ID',
            'business_description': 'Identifier for PIX return transaction.',
        },
        'return_reason': {
            'business_name': 'Return Reason',
            'business_description': 'Reason code for return.',
        },
        'return_description': {
            'business_name': 'Return Description',
            'business_description': 'Description of return reason.',
        },
        'original_end_to_end_id': {
            'business_name': 'Original End-to-End ID',
            'business_description': 'Original transaction E2EID for returns.',
        },
        # Remittance
        'remittance_info': {
            'business_name': 'Remittance Info',
            'business_description': 'Remittance information text.',
        },
        # Fraud Detection
        'fraud_marker': {
            'business_name': 'Fraud Marker',
            'business_description': 'Fraud indicator flag.',
        },
        'fraud_score': {
            'business_name': 'Fraud Score',
            'business_description': 'Fraud detection score.',
        },
        'infracao_id': {
            'business_name': 'Infraction ID',
            'business_description': 'Infraction report identifier.',
        },
        'infracao_type': {
            'business_name': 'Infraction Type',
            'business_description': 'Type of infraction reported.',
        },
        # Withdrawal (Saque/Troco)
        'withdrawal_agent_modality': {
            'business_name': 'Withdrawal Agent Modality',
            'business_description': 'Modality for PIX Saque agent.',
        },
        'withdrawal_amount': {
            'business_name': 'Withdrawal Amount',
            'business_description': 'Withdrawal amount for PIX Saque.',
        },
    },
}

# UPI - India Unified Payments Interface
CDM_EXTENSION_UPI = {
    'cdm_payment_extension_upi': {
        'extension_id': {
            'business_name': 'Extension ID',
            'business_description': 'Unique identifier for this UPI extension record.',
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the parent CDM payment instruction.',
        },
        'raw_id': {
            'business_name': 'Raw ID',
            'business_description': 'Reference to the Bronze layer raw message.',
        },
        'format_id': {
            'business_name': 'Format ID',
            'business_description': 'Message format identifier (UPI).',
        },
        'message_type': {
            'business_name': 'Message Type',
            'business_description': 'UPI message type code.',
        },
        'processing_status': {
            'business_name': 'Processing Status',
            'business_description': 'Current processing status of the UPI message.',
        },
        'transaction_id': {
            'business_name': 'Transaction ID',
            'business_description': 'Unique UPI transaction identifier.',
        },
        # Header Fields
        'head_ver': {
            'business_name': 'Header Version',
            'business_description': 'UPI API header version.',
        },
        'head_ts': {
            'business_name': 'Header Timestamp',
            'business_description': 'Header timestamp.',
        },
        'head_msg_id': {
            'business_name': 'Header Message ID',
            'business_description': 'Unique message ID from header.',
        },
        'head_org_id': {
            'business_name': 'Header Org ID',
            'business_description': 'Originating organization ID.',
        },
        # Transaction Fields
        'txn_id': {
            'business_name': 'Transaction ID',
            'business_description': 'UPI transaction ID.',
        },
        'txn_type': {
            'business_name': 'Transaction Type',
            'business_description': 'Type: PAY, COLLECT, MANDATE, REFUND.',
        },
        'txn_ts': {
            'business_name': 'Transaction Timestamp',
            'business_description': 'Transaction timestamp.',
        },
        'txn_ref_id': {
            'business_name': 'Transaction Reference ID',
            'business_description': 'Reference ID for the transaction.',
        },
        'txn_ref_url': {
            'business_name': 'Transaction Reference URL',
            'business_description': 'Reference URL for additional details.',
        },
        'txn_note': {
            'business_name': 'Transaction Note',
            'business_description': 'User note for the transaction.',
        },
        'txn_cust_ref': {
            'business_name': 'Transaction Customer Reference',
            'business_description': 'Customer reference number.',
        },
        'txn_org_txn_id': {
            'business_name': 'Original Transaction ID',
            'business_description': 'Original transaction ID for refunds.',
        },
        'txn_org_resp_code': {
            'business_name': 'Original Response Code',
            'business_description': 'Response code from original transaction.',
        },
        'transaction_ref_id': {
            'business_name': 'Transaction Reference ID',
            'business_description': 'Reference ID for tracking.',
        },
        'transaction_type': {
            'business_name': 'Transaction Type',
            'business_description': 'Type of UPI transaction.',
        },
        'transaction_status': {
            'business_name': 'Transaction Status',
            'business_description': 'Current transaction status.',
        },
        'sub_type': {
            'business_name': 'Sub Type',
            'business_description': 'Transaction sub-type.',
        },
        # Payer Fields
        'payer_vpa': {
            'business_name': 'Payer VPA',
            'business_description': 'Virtual Payment Address of the payer.',
        },
        'payer_addr': {
            'business_name': 'Payer Address',
            'business_description': 'Payer UPI address.',
        },
        'payer_code': {
            'business_name': 'Payer Code',
            'business_description': 'Payer PSP code.',
        },
        'payer_type': {
            'business_name': 'Payer Type',
            'business_description': 'Type of payer: PERSON, ENTITY, MERCHANT.',
        },
        'payer_seq_num': {
            'business_name': 'Payer Sequence Number',
            'business_description': 'Sequence number for payer.',
        },
        'payer_ac_acnum': {
            'business_name': 'Payer Account Number',
            'business_description': 'Payer bank account number.',
        },
        'payer_ac_ifsc': {
            'business_name': 'Payer IFSC',
            'business_description': 'IFSC code of payer bank.',
        },
        'payer_ac_actype': {
            'business_name': 'Payer Account Type',
            'business_description': 'Type of payer account.',
        },
        'payer_ac_addr_type': {
            'business_name': 'Payer Account Address Type',
            'business_description': 'Address type for payer account.',
        },
        'payer_amount_value': {
            'business_name': 'Payer Amount Value',
            'business_description': 'Amount from payer.',
        },
        'payer_amount_curr': {
            'business_name': 'Payer Amount Currency',
            'business_description': 'Currency of payer amount (INR).',
        },
        'payer_amount_split_name': {
            'business_name': 'Payer Split Name',
            'business_description': 'Name for split payment.',
        },
        'payer_amount_split_value': {
            'business_name': 'Payer Split Value',
            'business_description': 'Split amount value.',
        },
        'payer_identity_type': {
            'business_name': 'Payer Identity Type',
            'business_description': 'Type of payer identity verification.',
        },
        'payer_identity_verified_name': {
            'business_name': 'Payer Verified Name',
            'business_description': 'Verified name of payer.',
        },
        'payer_rating_verified_address': {
            'business_name': 'Payer Verified Address Rating',
            'business_description': 'Rating for verified address.',
        },
        'payer_rating_whitelisted': {
            'business_name': 'Payer Whitelisted',
            'business_description': 'Payer whitelisted status.',
        },
        'payer_cred_type': {
            'business_name': 'Payer Credential Type',
            'business_description': 'Type of credential used: PIN, OTP, BIOMETRIC.',
        },
        'payer_cred_sub_type': {
            'business_name': 'Payer Credential Sub Type',
            'business_description': 'Sub-type of credential.',
        },
        'payer_device_id': {
            'business_name': 'Payer Device ID',
            'business_description': 'Unique device identifier.',
        },
        'payer_device_type': {
            'business_name': 'Payer Device Type',
            'business_description': 'Type of device: MOBILE, POS, WEB.',
        },
        'payer_device_os': {
            'business_name': 'Payer Device OS',
            'business_description': 'Operating system of device.',
        },
        'payer_device_mobile': {
            'business_name': 'Payer Mobile Number',
            'business_description': 'Payer mobile number.',
        },
        'payer_device_location': {
            'business_name': 'Payer Device Location',
            'business_description': 'Location of payer device.',
        },
        'payer_device_ip': {
            'business_name': 'Payer Device IP',
            'business_description': 'IP address of payer device.',
        },
        'payer_device_geocode': {
            'business_name': 'Payer Device Geocode',
            'business_description': 'Geocode of payer device.',
        },
        # Payee Fields
        'payee_vpa': {
            'business_name': 'Payee VPA',
            'business_description': 'Virtual Payment Address of the payee.',
        },
        'payee_addr': {
            'business_name': 'Payee Address',
            'business_description': 'Payee UPI address.',
        },
        'payee_code': {
            'business_name': 'Payee Code',
            'business_description': 'Payee PSP code.',
        },
        'payee_type': {
            'business_name': 'Payee Type',
            'business_description': 'Type of payee.',
        },
        'payee_seq_num': {
            'business_name': 'Payee Sequence Number',
            'business_description': 'Sequence number for payee.',
        },
        'payee_ac_acnum': {
            'business_name': 'Payee Account Number',
            'business_description': 'Payee bank account number.',
        },
        'payee_ac_ifsc': {
            'business_name': 'Payee IFSC',
            'business_description': 'IFSC code of payee bank.',
        },
        'payee_ac_actype': {
            'business_name': 'Payee Account Type',
            'business_description': 'Type of payee account.',
        },
        'payee_ac_addr_type': {
            'business_name': 'Payee Account Address Type',
            'business_description': 'Address type for payee account.',
        },
        'payee_identity_type': {
            'business_name': 'Payee Identity Type',
            'business_description': 'Type of payee identity.',
        },
        'payee_identity_verified_name': {
            'business_name': 'Payee Verified Name',
            'business_description': 'Verified name of payee.',
        },
        'payee_rating_verified_address': {
            'business_name': 'Payee Verified Address Rating',
            'business_description': 'Rating for verified address.',
        },
        'payee_rating_whitelisted': {
            'business_name': 'Payee Whitelisted',
            'business_description': 'Payee whitelisted status.',
        },
        'payee_device_id': {
            'business_name': 'Payee Device ID',
            'business_description': 'Unique device identifier.',
        },
        'payee_device_type': {
            'business_name': 'Payee Device Type',
            'business_description': 'Type of device.',
        },
        'payee_device_os': {
            'business_name': 'Payee Device OS',
            'business_description': 'Operating system of device.',
        },
        'payee_device_mobile': {
            'business_name': 'Payee Mobile Number',
            'business_description': 'Payee mobile number.',
        },
        'payee_device_location': {
            'business_name': 'Payee Device Location',
            'business_description': 'Location of payee device.',
        },
        'payee_device_ip': {
            'business_name': 'Payee Device IP',
            'business_description': 'IP address of payee device.',
        },
        'payee_device_geocode': {
            'business_name': 'Payee Device Geocode',
            'business_description': 'Geocode of payee device.',
        },
        # Merchant Fields
        'merchant_id': {
            'business_name': 'Merchant ID',
            'business_description': 'Unique merchant identifier.',
        },
        'merchant_sub_id': {
            'business_name': 'Merchant Sub ID',
            'business_description': 'Merchant sub-identifier.',
        },
        'merchant_term_id': {
            'business_name': 'Merchant Terminal ID',
            'business_description': 'POS terminal identifier.',
        },
        # Reference Fields
        'ref_type': {
            'business_name': 'Reference Type',
            'business_description': 'Type of reference.',
        },
        'ref_value': {
            'business_name': 'Reference Value',
            'business_description': 'Reference value.',
        },
        'ref_addr': {
            'business_name': 'Reference Address',
            'business_description': 'Reference address.',
        },
        'ref_seq_num': {
            'business_name': 'Reference Sequence Number',
            'business_description': 'Reference sequence number.',
        },
        'remarks': {
            'business_name': 'Remarks',
            'business_description': 'Additional transaction remarks.',
        },
        # PSP Fields
        'psp_name': {
            'business_name': 'PSP Name',
            'business_description': 'Payment Service Provider name.',
        },
        # Response Fields
        'resp_msg_id': {
            'business_name': 'Response Message ID',
            'business_description': 'Response message identifier.',
        },
        'resp_req_msg_id': {
            'business_name': 'Response Request Message ID',
            'business_description': 'Original request message ID.',
        },
        'resp_result': {
            'business_name': 'Response Result',
            'business_description': 'Result of the transaction.',
        },
        'resp_err_code': {
            'business_name': 'Response Error Code',
            'business_description': 'Error code if failed.',
        },
        'response_code': {
            'business_name': 'Response Code',
            'business_description': 'Standard response code.',
        },
        # Acknowledgement Fields
        'ack_ts': {
            'business_name': 'Acknowledgement Timestamp',
            'business_description': 'Acknowledgement timestamp.',
        },
        'ack_api': {
            'business_name': 'Acknowledgement API',
            'business_description': 'API for acknowledgement.',
        },
        'ack_req_msg_id': {
            'business_name': 'Acknowledgement Request Message ID',
            'business_description': 'Request message ID for ack.',
        },
        'ack_err': {
            'business_name': 'Acknowledgement Error',
            'business_description': 'Error in acknowledgement.',
        },
        # Request Auth Fields
        'req_auth_api': {
            'business_name': 'Request Auth API',
            'business_description': 'API used for authorization request.',
        },
        'req_auth_version': {
            'business_name': 'Request Auth Version',
            'business_description': 'Version of auth request.',
        },
        # Risk Fields
        'risk_score_type': {
            'business_name': 'Risk Score Type',
            'business_description': 'Type of risk scoring.',
        },
        'risk_score_value': {
            'business_name': 'Risk Score Value',
            'business_description': 'Calculated risk score.',
        },
        'risk_score_provider': {
            'business_name': 'Risk Score Provider',
            'business_description': 'Provider of risk score.',
        },
        # Rule Fields
        'rule_name': {
            'business_name': 'Rule Name',
            'business_description': 'Name of applied rule.',
        },
        'rule_value': {
            'business_name': 'Rule Value',
            'business_description': 'Value from rule evaluation.',
        },
        # Metadata
        'meta_name': {
            'business_name': 'Metadata Name',
            'business_description': 'Metadata field name.',
        },
        'meta_value': {
            'business_name': 'Metadata Value',
            'business_description': 'Metadata field value.',
        },
    },
}

# CNAPS - China National Advanced Payment System
CDM_EXTENSION_CNAPS = {
    'cdm_payment_extension_cnaps': {
        'extension_id': {
            'business_name': 'Extension ID',
            'business_description': 'Unique identifier for this CNAPS extension record.',
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the parent CDM payment instruction.',
        },
        'raw_id': {
            'business_name': 'Raw ID',
            'business_description': 'Reference to the Bronze layer raw message.',
        },
        'format_id': {
            'business_name': 'Format ID',
            'business_description': 'Message format identifier (CNAPS).',
        },
        'message_type': {
            'business_name': 'Message Type',
            'business_description': 'CNAPS message type code.',
        },
        'transaction_id': {
            'business_name': 'Transaction ID',
            'business_description': 'Unique CNAPS transaction identifier.',
        },
        'transaction_reference': {
            'business_name': 'Transaction Reference',
            'business_description': 'Transaction reference number.',
        },
        # Bank Codes
        'sender_bank_code': {
            'business_name': 'Sender Bank Code',
            'business_description': 'CNAPS code of sending bank (12 digits).',
        },
        'receiver_bank_code': {
            'business_name': 'Receiver Bank Code',
            'business_description': 'CNAPS code of receiving bank.',
        },
        'correspondent_bank_code': {
            'business_name': 'Correspondent Bank Code',
            'business_description': 'Correspondent bank CNAPS code.',
        },
        'direct_participant_code': {
            'business_name': 'Direct Participant Code',
            'business_description': 'Direct participant CNAPS code.',
        },
        # Account Fields
        'sender_account': {
            'business_name': 'Sender Account',
            'business_description': 'Sender account number.',
        },
        'sender_name': {
            'business_name': 'Sender Name',
            'business_description': 'Name of the sender.',
        },
        'receiver_account': {
            'business_name': 'Receiver Account',
            'business_description': 'Receiver account number.',
        },
        'receiver_name': {
            'business_name': 'Receiver Name',
            'business_description': 'Name of the receiver.',
        },
        'payer_id': {
            'business_name': 'Payer ID',
            'business_description': 'Payer identification number.',
        },
        'payer_address': {
            'business_name': 'Payer Address',
            'business_description': 'Address of the payer.',
        },
        'payee_id': {
            'business_name': 'Payee ID',
            'business_description': 'Payee identification number.',
        },
        'payee_address': {
            'business_name': 'Payee Address',
            'business_description': 'Address of the payee.',
        },
        # System Fields
        'clearing_system': {
            'business_name': 'Clearing System',
            'business_description': 'CNAPS clearing system: HVPS, BEPS, IBPS.',
        },
        'network_code': {
            'business_name': 'Network Code',
            'business_description': 'Network identification code.',
        },
        'transfer_type': {
            'business_name': 'Transfer Type',
            'business_description': 'Type of transfer.',
        },
        'payment_method': {
            'business_name': 'Payment Method',
            'business_description': 'Method of payment.',
        },
        'purpose_code': {
            'business_name': 'Purpose Code',
            'business_description': 'Payment purpose code.',
        },
        # Batch Fields
        'source_batch_id': {
            'business_name': 'Source Batch ID',
            'business_description': 'Source batch identifier.',
        },
        'batch_id_ref': {
            'business_name': 'Batch ID Reference',
            'business_description': 'Reference batch identifier.',
        },
        'batch_count': {
            'business_name': 'Batch Count',
            'business_description': 'Number of items in batch.',
        },
        'batch_amount': {
            'business_name': 'Batch Amount',
            'business_description': 'Total batch amount.',
        },
        'item_sequence': {
            'business_name': 'Item Sequence',
            'business_description': 'Sequence number within batch.',
        },
        # Settlement
        'settlement_date': {
            'business_name': 'Settlement Date',
            'business_description': 'Date of settlement.',
        },
        'settlement_method': {
            'business_name': 'Settlement Method',
            'business_description': 'Method of settlement.',
        },
        # Cross-border
        'cross_border_indicator': {
            'business_name': 'Cross Border Indicator',
            'business_description': 'Indicates if cross-border payment.',
        },
        'cips_reference': {
            'business_name': 'CIPS Reference',
            'business_description': 'CIPS (Cross-Border) reference.',
        },
        # Regulatory
        'regulatory_reporting': {
            'business_name': 'Regulatory Reporting',
            'business_description': 'Regulatory reporting information.',
        },
        'authority_code': {
            'business_name': 'Authority Code',
            'business_description': 'Regulatory authority code.',
        },
        # Additional
        'remarks': {
            'business_name': 'Remarks',
            'business_description': 'Additional remarks.',
        },
        'return_code': {
            'business_name': 'Return Code',
            'business_description': 'Return code if returned.',
        },
        'return_reason': {
            'business_name': 'Return Reason',
            'business_description': 'Reason for return.',
        },
    },
}

# KFTC - Korea Financial Telecommunications & Clearings
CDM_EXTENSION_KFTC = {
    'cdm_payment_extension_kftc': {
        'extension_id': {
            'business_name': 'Extension ID',
            'business_description': 'Unique identifier for this KFTC extension record.',
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the parent CDM payment instruction.',
        },
        'raw_id': {
            'business_name': 'Raw ID',
            'business_description': 'Reference to the Bronze layer raw message.',
        },
        'format_id': {
            'business_name': 'Format ID',
            'business_description': 'Message format identifier (KFTC).',
        },
        'message_type': {
            'business_name': 'Message Type',
            'business_description': 'KFTC message type code.',
        },
        'processing_status': {
            'business_name': 'Processing Status',
            'business_description': 'Current processing status.',
        },
        'transaction_id': {
            'business_name': 'Transaction ID',
            'business_description': 'Unique KFTC transaction identifier.',
        },
        'transaction_reference': {
            'business_name': 'Transaction Reference',
            'business_description': 'Transaction reference number.',
        },
        'end_to_end_id': {
            'business_name': 'End-to-End ID',
            'business_description': 'End-to-end transaction reference.',
        },
        'related_reference': {
            'business_name': 'Related Reference',
            'business_description': 'Reference to related transaction.',
        },
        'batch_number': {
            'business_name': 'Batch Number',
            'business_description': 'Processing batch number.',
        },
        # Sender Fields
        'sender_bank_code': {
            'business_name': 'Sender Bank Code',
            'business_description': 'Korean bank code of sender (3 digits).',
        },
        'sender_branch_code': {
            'business_name': 'Sender Branch Code',
            'business_description': 'Branch code of sender bank.',
        },
        'sender_account': {
            'business_name': 'Sender Account',
            'business_description': 'Sender account number.',
        },
        'sender_account_type': {
            'business_name': 'Sender Account Type',
            'business_description': 'Type of sender account.',
        },
        'sender_name': {
            'business_name': 'Sender Name',
            'business_description': 'Name of the sender.',
        },
        'sender_name_korean': {
            'business_name': 'Sender Name (Korean)',
            'business_description': 'Sender name in Korean characters.',
        },
        'sender_cust_id': {
            'business_name': 'Sender Customer ID',
            'business_description': 'Sender customer identifier.',
        },
        'sender_cust_type': {
            'business_name': 'Sender Customer Type',
            'business_description': 'Type of sender customer.',
        },
        'sender_resident_id': {
            'business_name': 'Sender Resident ID',
            'business_description': 'Sender resident registration number.',
        },
        'sender_business_number': {
            'business_name': 'Sender Business Number',
            'business_description': 'Sender business registration number.',
        },
        'sender_address': {
            'business_name': 'Sender Address',
            'business_description': 'Address of the sender.',
        },
        'sender_phone_number': {
            'business_name': 'Sender Phone Number',
            'business_description': 'Contact phone of sender.',
        },
        # Receiver Fields
        'receiver_bank_code': {
            'business_name': 'Receiver Bank Code',
            'business_description': 'Korean bank code of receiver.',
        },
        'receiver_branch_code': {
            'business_name': 'Receiver Branch Code',
            'business_description': 'Branch code of receiver bank.',
        },
        'receiver_account': {
            'business_name': 'Receiver Account',
            'business_description': 'Receiver account number.',
        },
        'receiver_account_type': {
            'business_name': 'Receiver Account Type',
            'business_description': 'Type of receiver account.',
        },
        'receiver_name': {
            'business_name': 'Receiver Name',
            'business_description': 'Name of the receiver.',
        },
        'receiver_name_korean': {
            'business_name': 'Receiver Name (Korean)',
            'business_description': 'Receiver name in Korean characters.',
        },
        'receiver_cust_id': {
            'business_name': 'Receiver Customer ID',
            'business_description': 'Receiver customer identifier.',
        },
        'receiver_cust_type': {
            'business_name': 'Receiver Customer Type',
            'business_description': 'Type of receiver customer.',
        },
        'receiver_resident_id': {
            'business_name': 'Receiver Resident ID',
            'business_description': 'Receiver resident registration number.',
        },
        'receiver_business_number': {
            'business_name': 'Receiver Business Number',
            'business_description': 'Receiver business registration number.',
        },
        'receiver_address': {
            'business_name': 'Receiver Address',
            'business_description': 'Address of the receiver.',
        },
        'receiver_phone_number': {
            'business_name': 'Receiver Phone Number',
            'business_description': 'Contact phone of receiver.',
        },
        # Amount Fields
        'original_amount': {
            'business_name': 'Original Amount',
            'business_description': 'Original transaction amount.',
        },
        'original_currency': {
            'business_name': 'Original Currency',
            'business_description': 'Original amount currency.',
        },
        'total_amount': {
            'business_name': 'Total Amount',
            'business_description': 'Total amount including fees.',
        },
        'fee_amount': {
            'business_name': 'Fee Amount',
            'business_description': 'Transaction fee amount.',
        },
        'tax_amount': {
            'business_name': 'Tax Amount',
            'business_description': 'Tax amount applied.',
        },
        'exchange_rate': {
            'business_name': 'Exchange Rate',
            'business_description': 'Foreign exchange rate.',
        },
        # Processing Fields
        'processing_code': {
            'business_name': 'Processing Code',
            'business_description': 'KFTC processing code.',
        },
        'processing_date': {
            'business_name': 'Processing Date',
            'business_description': 'Date of processing.',
        },
        'value_date': {
            'business_name': 'Value Date',
            'business_description': 'Value date for settlement.',
        },
        'settlement_date': {
            'business_name': 'Settlement Date',
            'business_description': 'Date of settlement.',
        },
        'settlement_method': {
            'business_name': 'Settlement Method',
            'business_description': 'Method of settlement.',
        },
        'settlement_status': {
            'business_name': 'Settlement Status',
            'business_description': 'Current settlement status.',
        },
        'settlement_time': {
            'business_name': 'Settlement Time',
            'business_description': 'Time of settlement.',
        },
        'settlement_cycle_number': {
            'business_name': 'Settlement Cycle Number',
            'business_description': 'Settlement cycle number.',
        },
        'transmission_date_time': {
            'business_name': 'Transmission DateTime',
            'business_description': 'Timestamp of transmission.',
        },
        # Purpose and Category
        'purpose_code': {
            'business_name': 'Purpose Code',
            'business_description': 'Payment purpose code.',
        },
        'purpose_description': {
            'business_name': 'Purpose Description',
            'business_description': 'Description of payment purpose.',
        },
        'category_code': {
            'business_name': 'Category Code',
            'business_description': 'Transaction category code.',
        },
        'channel_code': {
            'business_name': 'Channel Code',
            'business_description': 'Payment channel code.',
        },
        'system_code': {
            'business_name': 'System Code',
            'business_description': 'Processing system code.',
        },
        # GIRO Fields
        'giro_type': {
            'business_name': 'GIRO Type',
            'business_description': 'Type of GIRO transaction.',
        },
        'giro_service_code': {
            'business_name': 'GIRO Service Code',
            'business_description': 'GIRO service code.',
        },
        'giro_biller_code': {
            'business_name': 'GIRO Biller Code',
            'business_description': 'Biller code for GIRO.',
        },
        'giro_bill_number': {
            'business_name': 'GIRO Bill Number',
            'business_description': 'Bill number for GIRO payment.',
        },
        'giro_account_number': {
            'business_name': 'GIRO Account Number',
            'business_description': 'GIRO account number.',
        },
        'giro_payer_number': {
            'business_name': 'GIRO Payer Number',
            'business_description': 'Payer number for GIRO.',
        },
        'giro_contract_number': {
            'business_name': 'GIRO Contract Number',
            'business_description': 'Contract number for recurring GIRO.',
        },
        'giro_due_date': {
            'business_name': 'GIRO Due Date',
            'business_description': 'Due date for GIRO payment.',
        },
        # CMS Fields
        'cms_code': {
            'business_name': 'CMS Code',
            'business_description': 'Cash Management System code.',
        },
        'cms_company_code': {
            'business_name': 'CMS Company Code',
            'business_description': 'Company code for CMS.',
        },
        'cms_department_code': {
            'business_name': 'CMS Department Code',
            'business_description': 'Department code for CMS.',
        },
        'cms_employee_id': {
            'business_name': 'CMS Employee ID',
            'business_description': 'Employee ID for CMS.',
        },
        'cms_contract_id': {
            'business_name': 'CMS Contract ID',
            'business_description': 'Contract ID for CMS.',
        },
        'cms_payment_type': {
            'business_name': 'CMS Payment Type',
            'business_description': 'Payment type for CMS.',
        },
        # Remittance and Narrative
        'remittance_info': {
            'business_name': 'Remittance Info',
            'business_description': 'Remittance information.',
        },
        'invoice_number': {
            'business_name': 'Invoice Number',
            'business_description': 'Associated invoice number.',
        },
        'narrative_memo': {
            'business_name': 'Narrative Memo',
            'business_description': 'Narrative memo text.',
        },
        # Return and Rejection
        'return_code': {
            'business_name': 'Return Code',
            'business_description': 'Return code if returned.',
        },
        'return_reason': {
            'business_name': 'Return Reason',
            'business_description': 'Reason for return.',
        },
        'reject_code': {
            'business_name': 'Reject Code',
            'business_description': 'Rejection code.',
        },
        'reject_reason': {
            'business_name': 'Reject Reason',
            'business_description': 'Reason for rejection.',
        },
        'response_code': {
            'business_name': 'Response Code',
            'business_description': 'Response code from KFTC.',
        },
        # Reconciliation
        'reconciliation_reference': {
            'business_name': 'Reconciliation Reference',
            'business_description': 'Reference for reconciliation.',
        },
        'clearing_reference': {
            'business_name': 'Clearing Reference',
            'business_description': 'Clearing system reference.',
        },
        'confirmation_status': {
            'business_name': 'Confirmation Status',
            'business_description': 'Confirmation status.',
        },
        'original_transaction_id': {
            'business_name': 'Original Transaction ID',
            'business_description': 'Original transaction ID for reversals.',
        },
    },
}

# PAYNOW - Singapore PayNow
CDM_EXTENSION_PAYNOW = {
    'cdm_payment_extension_paynow': {
        'extension_id': {
            'business_name': 'Extension ID',
            'business_description': 'Unique identifier for this PayNow extension record.',
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the parent CDM payment instruction.',
        },
        'raw_id': {
            'business_name': 'Raw ID',
            'business_description': 'Reference to the Bronze layer raw message.',
        },
        'format_id': {
            'business_name': 'Format ID',
            'business_description': 'Message format identifier (PAYNOW).',
        },
        'message_type': {
            'business_name': 'Message Type',
            'business_description': 'PayNow message type.',
        },
        'processing_status': {
            'business_name': 'Processing Status',
            'business_description': 'Current processing status.',
        },
        'silver_processed_at': {
            'business_name': 'Silver Processed At',
            'business_description': 'Timestamp of Silver processing.',
        },
        'silver_processed_to_gold_at': {
            'business_name': 'Silver Processed to Gold At',
            'business_description': 'Timestamp of Gold processing.',
        },
        'transaction_id': {
            'business_name': 'Transaction ID',
            'business_description': 'Unique PayNow transaction identifier.',
        },
        'source_batch_id': {
            'business_name': 'Source Batch ID',
            'business_description': 'Source batch identifier.',
        },
        # Proxy Fields
        'proxy_type': {
            'business_name': 'Proxy Type',
            'business_description': 'Type of proxy: MOBILE, NRIC, UEN, VPA.',
        },
        'proxy_value': {
            'business_name': 'Proxy Value',
            'business_description': 'Proxy value (phone, ID, etc.).',
        },
        # Sender Fields
        'sender_name': {
            'business_name': 'Sender Name',
            'business_description': 'Name of the sender.',
        },
        'sender_proxy': {
            'business_name': 'Sender Proxy',
            'business_description': 'Sender PayNow proxy.',
        },
        'payer_account': {
            'business_name': 'Payer Account',
            'business_description': 'Payer account number.',
        },
        'payer_bank_code': {
            'business_name': 'Payer Bank Code',
            'business_description': 'Bank code of the payer.',
        },
        'payer_proxy_type': {
            'business_name': 'Payer Proxy Type',
            'business_description': 'Type of payer proxy.',
        },
        'payer_proxy_value': {
            'business_name': 'Payer Proxy Value',
            'business_description': 'Payer proxy value.',
        },
        # Receiver Fields
        'receiver_name': {
            'business_name': 'Receiver Name',
            'business_description': 'Name of the receiver.',
        },
        'receiver_proxy': {
            'business_name': 'Receiver Proxy',
            'business_description': 'Receiver PayNow proxy.',
        },
        'payee_account': {
            'business_name': 'Payee Account',
            'business_description': 'Payee account number.',
        },
        'payee_bank_code': {
            'business_name': 'Payee Bank Code',
            'business_description': 'Bank code of the payee.',
        },
        'payee_proxy_type': {
            'business_name': 'Payee Proxy Type',
            'business_description': 'Type of payee proxy.',
        },
        'payee_proxy_value': {
            'business_name': 'Payee Proxy Value',
            'business_description': 'Payee proxy value.',
        },
        # Amount Fields
        'instructed_amount': {
            'business_name': 'Instructed Amount',
            'business_description': 'Instructed payment amount.',
        },
        'instructed_currency': {
            'business_name': 'Instructed Currency',
            'business_description': 'Currency of the amount (SGD).',
        },
        'instruction_priority': {
            'business_name': 'Instruction Priority',
            'business_description': 'Payment priority level.',
        },
        # Remittance
        'remittance_info': {
            'business_name': 'Remittance Info',
            'business_description': 'Remittance information.',
        },
        'referred_document_number': {
            'business_name': 'Referred Document Number',
            'business_description': 'Referenced document number.',
        },
    },
}

# PROMPTPAY - Thailand PromptPay
CDM_EXTENSION_PROMPTPAY = {
    'cdm_payment_extension_promptpay': {
        'extension_id': {
            'business_name': 'Extension ID',
            'business_description': 'Unique identifier for this PromptPay extension record.',
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the parent CDM payment instruction.',
        },
        'raw_id': {
            'business_name': 'Raw ID',
            'business_description': 'Reference to the Bronze layer raw message.',
        },
        'format_id': {
            'business_name': 'Format ID',
            'business_description': 'Message format identifier (PROMPTPAY).',
        },
        'message_type': {
            'business_name': 'Message Type',
            'business_description': 'PromptPay message type.',
        },
        'processing_status': {
            'business_name': 'Processing Status',
            'business_description': 'Current processing status.',
        },
        'processing_timestamp': {
            'business_name': 'Processing Timestamp',
            'business_description': 'Timestamp of processing.',
        },
        'silver_processed_at': {
            'business_name': 'Silver Processed At',
            'business_description': 'Timestamp of Silver processing.',
        },
        'silver_processed_to_gold_at': {
            'business_name': 'Silver Processed to Gold At',
            'business_description': 'Timestamp of Gold processing.',
        },
        'transaction_id': {
            'business_name': 'Transaction ID',
            'business_description': 'Unique PromptPay transaction identifier.',
        },
        # Group Header
        'group_header_msg_id': {
            'business_name': 'Group Header Message ID',
            'business_description': 'Message ID from group header.',
        },
        'group_header_nb_of_txs': {
            'business_name': 'Number of Transactions',
            'business_description': 'Number of transactions in message.',
        },
        # Proxy Fields
        'proxy_msisdn': {
            'business_name': 'Proxy MSISDN',
            'business_description': 'Mobile number proxy.',
        },
        'proxy_nrid': {
            'business_name': 'Proxy NRID',
            'business_description': 'National registration ID proxy.',
        },
        'proxy_txid': {
            'business_name': 'Proxy Tax ID',
            'business_description': 'Tax ID proxy.',
        },
        'proxy_ewal': {
            'business_name': 'Proxy E-Wallet',
            'business_description': 'E-wallet proxy identifier.',
        },
        # Sender Fields
        'sender_name': {
            'business_name': 'Sender Name',
            'business_description': 'Name of the sender.',
        },
        'sender_proxy': {
            'business_name': 'Sender Proxy',
            'business_description': 'Sender PromptPay proxy.',
        },
        'sender_fi_member_id': {
            'business_name': 'Sender FI Member ID',
            'business_description': 'Financial institution member ID of sender.',
        },
        'sender_fi_name': {
            'business_name': 'Sender FI Name',
            'business_description': 'Name of sender financial institution.',
        },
        'payer_account': {
            'business_name': 'Payer Account',
            'business_description': 'Payer account number.',
        },
        'payer_account_type': {
            'business_name': 'Payer Account Type',
            'business_description': 'Type of payer account.',
        },
        'payer_proxy_type': {
            'business_name': 'Payer Proxy Type',
            'business_description': 'Type of payer proxy.',
        },
        'payer_proxy_value': {
            'business_name': 'Payer Proxy Value',
            'business_description': 'Payer proxy value.',
        },
        # Receiver Fields
        'receiver_name': {
            'business_name': 'Receiver Name',
            'business_description': 'Name of the receiver.',
        },
        'receiver_proxy': {
            'business_name': 'Receiver Proxy',
            'business_description': 'Receiver PromptPay proxy.',
        },
        'receiver_fi_member_id': {
            'business_name': 'Receiver FI Member ID',
            'business_description': 'Financial institution member ID of receiver.',
        },
        'receiver_fi_name': {
            'business_name': 'Receiver FI Name',
            'business_description': 'Name of receiver financial institution.',
        },
        'payee_account': {
            'business_name': 'Payee Account',
            'business_description': 'Payee account number.',
        },
        'payee_account_type': {
            'business_name': 'Payee Account Type',
            'business_description': 'Type of payee account.',
        },
        'payee_proxy_type': {
            'business_name': 'Payee Proxy Type',
            'business_description': 'Type of payee proxy.',
        },
        'payee_proxy_value': {
            'business_name': 'Payee Proxy Value',
            'business_description': 'Payee proxy value.',
        },
        # Agent Fields
        'creditor_agent_name': {
            'business_name': 'Creditor Agent Name',
            'business_description': 'Name of the creditor agent.',
        },
        'debtor_agent_name': {
            'business_name': 'Debtor Agent Name',
            'business_description': 'Name of the debtor agent.',
        },
        # Transaction Details
        'transaction_type': {
            'business_name': 'Transaction Type',
            'business_description': 'Type of PromptPay transaction.',
        },
        'transaction_channel': {
            'business_name': 'Transaction Channel',
            'business_description': 'Channel used for transaction.',
        },
        'service_code': {
            'business_name': 'Service Code',
            'business_description': 'PromptPay service code.',
        },
        'original_tx_id': {
            'business_name': 'Original Transaction ID',
            'business_description': 'Original transaction ID for reversals.',
        },
        # Fees
        'fee_amount': {
            'business_name': 'Fee Amount',
            'business_description': 'Transaction fee amount.',
        },
        'fee_bearer_type': {
            'business_name': 'Fee Bearer Type',
            'business_description': 'Who bears the fee.',
        },
        'fee_debtor_account': {
            'business_name': 'Fee Debtor Account',
            'business_description': 'Account charged for fees.',
        },
        # Bill Payment
        'bill_pmt_ref': {
            'business_name': 'Bill Payment Reference',
            'business_description': 'Bill payment reference.',
        },
        'bill_pmt_suffix': {
            'business_name': 'Bill Payment Suffix',
            'business_description': 'Bill payment suffix.',
        },
        # Remittance
        'remittance_structured': {
            'business_name': 'Remittance Structured',
            'business_description': 'Structured remittance information.',
        },
        # NITMX Fields
        'nitmx_msg_id': {
            'business_name': 'NITMX Message ID',
            'business_description': 'NITMX message identifier.',
        },
        'nitmx_batch_id': {
            'business_name': 'NITMX Batch ID',
            'business_description': 'NITMX batch identifier.',
        },
        'nitmx_clearing_code': {
            'business_name': 'NITMX Clearing Code',
            'business_description': 'NITMX clearing code.',
        },
        'nitmx_settlement_cycle': {
            'business_name': 'NITMX Settlement Cycle',
            'business_description': 'NITMX settlement cycle.',
        },
        # Settlement
        'settlement_datetime': {
            'business_name': 'Settlement DateTime',
            'business_description': 'Settlement date and time.',
        },
        'confirmation_datetime': {
            'business_name': 'Confirmation DateTime',
            'business_description': 'Confirmation timestamp.',
        },
        'confirmation_number': {
            'business_name': 'Confirmation Number',
            'business_description': 'Confirmation number.',
        },
        # QR Code
        'qr_code_id': {
            'business_name': 'QR Code ID',
            'business_description': 'QR code identifier.',
        },
        'qr_code_type': {
            'business_name': 'QR Code Type',
            'business_description': 'Type of QR code.',
        },
        'qr_code_data': {
            'business_name': 'QR Code Data',
            'business_description': 'QR code payload data.',
        },
        # Security
        'auth_code': {
            'business_name': 'Auth Code',
            'business_description': 'Authorization code.',
        },
        'otp_verified': {
            'business_name': 'OTP Verified',
            'business_description': 'OTP verification status.',
        },
        'digital_signature': {
            'business_name': 'Digital Signature',
            'business_description': 'Digital signature.',
        },
        # Rejection
        'reject_reason_code': {
            'business_name': 'Reject Reason Code',
            'business_description': 'Rejection reason code.',
        },
        'reject_reason_desc': {
            'business_name': 'Reject Reason Description',
            'business_description': 'Rejection reason description.',
        },
        'reversal_indicator': {
            'business_name': 'Reversal Indicator',
            'business_description': 'Indicates if this is a reversal.',
        },
    },
}

# SARIE - Saudi Arabia RTGS
CDM_EXTENSION_SARIE = {
    'cdm_payment_extension_sarie': {
        'extension_id': {
            'business_name': 'Extension ID',
            'business_description': 'Unique identifier for this SARIE extension record.',
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the parent CDM payment instruction.',
        },
        'stg_id': {
            'business_name': 'Silver Stage ID',
            'business_description': 'Reference to the Silver layer staging record.',
        },
        'raw_id': {
            'business_name': 'Raw ID',
            'business_description': 'Reference to the Bronze layer raw message.',
        },
        'format_id': {
            'business_name': 'Format ID',
            'business_description': 'Message format identifier (e.g., SARIE).',
        },
        'message_type': {
            'business_name': 'Message Type',
            'business_description': 'SARIE message type code.',
        },
        'processing_status': {
            'business_name': 'Processing Status',
            'business_description': 'Current processing status of the SARIE message.',
        },
        # Group Header Fields
        'group_header_message_id': {
            'business_name': 'Group Header Message ID',
            'business_description': 'Unique message identifier from the group header.',
        },
        'group_header_creation_datetime': {
            'business_name': 'Group Header Creation DateTime',
            'business_description': 'Timestamp when the message was created.',
        },
        'group_header_number_of_transactions': {
            'business_name': 'Number of Transactions',
            'business_description': 'Total number of transactions in the message.',
        },
        'group_header_control_sum': {
            'business_name': 'Control Sum',
            'business_description': 'Sum of all transaction amounts for validation.',
        },
        'group_header_clearing_system_code': {
            'business_name': 'Clearing System Code',
            'business_description': 'Code identifying the SARIE clearing system.',
        },
        'group_header_settlement_method': {
            'business_name': 'Settlement Method',
            'business_description': 'Method used for settlement (CLRG, INGA, INDA).',
        },
        'group_header_settlement_account_iban': {
            'business_name': 'Settlement Account IBAN',
            'business_description': 'IBAN of the settlement account.',
        },
        # Transaction IDs
        'transaction_id': {
            'business_name': 'Transaction ID',
            'business_description': 'Unique transaction identifier.',
        },
        'payment_instruction_id': {
            'business_name': 'Payment Instruction ID',
            'business_description': 'Payment instruction identifier.',
        },
        'payment_transaction_id': {
            'business_name': 'Payment Transaction ID',
            'business_description': 'Payment transaction identifier.',
        },
        'end_to_end_id': {
            'business_name': 'End-to-End ID',
            'business_description': 'Unique end-to-end transaction reference.',
        },
        'transaction_reference': {
            'business_name': 'Transaction Reference',
            'business_description': 'Transaction reference number.',
        },
        'uetr': {
            'business_name': 'UETR',
            'business_description': 'Unique End-to-End Transaction Reference (UUID format).',
        },
        'clearing_system_reference': {
            'business_name': 'Clearing System Reference',
            'business_description': 'Reference assigned by the SARIE clearing system.',
        },
        # Amount Fields
        'instructed_amount': {
            'business_name': 'Instructed Amount',
            'business_description': 'Original instructed payment amount.',
        },
        'instructed_currency': {
            'business_name': 'Instructed Currency',
            'business_description': 'Currency of the instructed amount (typically SAR).',
        },
        'interbank_settlement_amount': {
            'business_name': 'Interbank Settlement Amount',
            'business_description': 'Amount to be settled between banks.',
        },
        'interbank_settlement_currency': {
            'business_name': 'Interbank Settlement Currency',
            'business_description': 'Currency for interbank settlement.',
        },
        'interbank_settlement_date': {
            'business_name': 'Interbank Settlement Date',
            'business_description': 'Date of interbank settlement.',
        },
        'exchange_rate': {
            'business_name': 'Exchange Rate',
            'business_description': 'Foreign exchange rate if applicable.',
        },
        'settlement_date': {
            'business_name': 'Settlement Date',
            'business_description': 'Date when the payment is settled.',
        },
        # Debtor Fields
        'debtor_name': {
            'business_name': 'Debtor Name',
            'business_description': 'Name of the debtor (payer).',
        },
        'debtor_country': {
            'business_name': 'Debtor Country',
            'business_description': 'Country of the debtor.',
        },
        'debtor_iban': {
            'business_name': 'Debtor IBAN',
            'business_description': 'Saudi IBAN of the debtor account.',
        },
        'debtor_account_type': {
            'business_name': 'Debtor Account Type',
            'business_description': 'Type of debtor account (CACC, SVGS, etc.).',
        },
        'debtor_account_currency': {
            'business_name': 'Debtor Account Currency',
            'business_description': 'Currency of the debtor account.',
        },
        'debtor_account_name': {
            'business_name': 'Debtor Account Name',
            'business_description': 'Name on the debtor account.',
        },
        'debtor_account_other_id': {
            'business_name': 'Debtor Account Other ID',
            'business_description': 'Alternative debtor account identifier.',
        },
        'debtor_private_id': {
            'business_name': 'Debtor Private ID',
            'business_description': 'Private identification of the debtor.',
        },
        'debtor_private_id_scheme': {
            'business_name': 'Debtor Private ID Scheme',
            'business_description': 'Scheme for the debtor private ID.',
        },
        # Debtor Agent Fields
        'debtor_agent_bic': {
            'business_name': 'Debtor Agent BIC',
            'business_description': 'BIC of the debtor agent (sending bank).',
        },
        'debtor_agent_name': {
            'business_name': 'Debtor Agent Name',
            'business_description': 'Name of the debtor agent bank.',
        },
        'debtor_agent_country': {
            'business_name': 'Debtor Agent Country',
            'business_description': 'Country of the debtor agent.',
        },
        'debtor_agent_member_id': {
            'business_name': 'Debtor Agent Member ID',
            'business_description': 'SARIE member ID of the debtor agent.',
        },
        'debtor_agent_branch_id': {
            'business_name': 'Debtor Agent Branch ID',
            'business_description': 'Branch ID of the debtor agent.',
        },
        'debtor_agent_clearing_system': {
            'business_name': 'Debtor Agent Clearing System',
            'business_description': 'Clearing system of the debtor agent.',
        },
        'debtor_agent_account_iban': {
            'business_name': 'Debtor Agent Account IBAN',
            'business_description': 'IBAN of the debtor agent account.',
        },
        # Creditor Fields
        'creditor_name': {
            'business_name': 'Creditor Name',
            'business_description': 'Name of the creditor (payee).',
        },
        'creditor_country': {
            'business_name': 'Creditor Country',
            'business_description': 'Country of the creditor.',
        },
        'creditor_iban': {
            'business_name': 'Creditor IBAN',
            'business_description': 'Saudi IBAN of the creditor account.',
        },
        'creditor_account_type': {
            'business_name': 'Creditor Account Type',
            'business_description': 'Type of creditor account.',
        },
        'creditor_account_currency': {
            'business_name': 'Creditor Account Currency',
            'business_description': 'Currency of the creditor account.',
        },
        'creditor_account_name': {
            'business_name': 'Creditor Account Name',
            'business_description': 'Name on the creditor account.',
        },
        'creditor_account_other_id': {
            'business_name': 'Creditor Account Other ID',
            'business_description': 'Alternative creditor account identifier.',
        },
        'creditor_private_id': {
            'business_name': 'Creditor Private ID',
            'business_description': 'Private identification of the creditor.',
        },
        'creditor_private_id_scheme': {
            'business_name': 'Creditor Private ID Scheme',
            'business_description': 'Scheme for the creditor private ID.',
        },
        # Creditor Agent Fields
        'creditor_agent_bic': {
            'business_name': 'Creditor Agent BIC',
            'business_description': 'BIC of the creditor agent (receiving bank).',
        },
        'creditor_agent_name': {
            'business_name': 'Creditor Agent Name',
            'business_description': 'Name of the creditor agent bank.',
        },
        'creditor_agent_country': {
            'business_name': 'Creditor Agent Country',
            'business_description': 'Country of the creditor agent.',
        },
        'creditor_agent_member_id': {
            'business_name': 'Creditor Agent Member ID',
            'business_description': 'SARIE member ID of the creditor agent.',
        },
        'creditor_agent_branch_id': {
            'business_name': 'Creditor Agent Branch ID',
            'business_description': 'Branch ID of the creditor agent.',
        },
        'creditor_agent_clearing_system': {
            'business_name': 'Creditor Agent Clearing System',
            'business_description': 'Clearing system of the creditor agent.',
        },
        'creditor_agent_account_iban': {
            'business_name': 'Creditor Agent Account IBAN',
            'business_description': 'IBAN of the creditor agent account.',
        },
        # Instructing/Instructed Agent Fields
        'instructing_agent_bic': {
            'business_name': 'Instructing Agent BIC',
            'business_description': 'BIC of the instructing agent.',
        },
        'instructing_agent_bic_from_msg': {
            'business_name': 'Instructing Agent BIC From Message',
            'business_description': 'BIC of the instructing agent as received in message.',
        },
        'instructing_agent_name': {
            'business_name': 'Instructing Agent Name',
            'business_description': 'Name of the instructing agent.',
        },
        'instructing_agent_name_from_msg': {
            'business_name': 'Instructing Agent Name From Message',
            'business_description': 'Instructing agent name as received in message.',
        },
        'instructing_agent_country': {
            'business_name': 'Instructing Agent Country',
            'business_description': 'Country of the instructing agent.',
        },
        'instructing_agent_country_from_msg': {
            'business_name': 'Instructing Agent Country From Message',
            'business_description': 'Instructing agent country as received in message.',
        },
        'instructing_agent_member_id': {
            'business_name': 'Instructing Agent Member ID',
            'business_description': 'Member ID of the instructing agent.',
        },
        'instructing_agent_member_id_from_msg': {
            'business_name': 'Instructing Agent Member ID From Message',
            'business_description': 'Instructing agent member ID as received in message.',
        },
        'instructed_agent_bic': {
            'business_name': 'Instructed Agent BIC',
            'business_description': 'BIC of the instructed agent.',
        },
        'instructed_agent_bic_from_msg': {
            'business_name': 'Instructed Agent BIC From Message',
            'business_description': 'BIC of the instructed agent as received in message.',
        },
        'instructed_agent_name': {
            'business_name': 'Instructed Agent Name',
            'business_description': 'Name of the instructed agent.',
        },
        'instructed_agent_name_from_msg': {
            'business_name': 'Instructed Agent Name From Message',
            'business_description': 'Instructed agent name as received in message.',
        },
        'instructed_agent_country': {
            'business_name': 'Instructed Agent Country',
            'business_description': 'Country of the instructed agent.',
        },
        'instructed_agent_country_from_msg': {
            'business_name': 'Instructed Agent Country From Message',
            'business_description': 'Instructed agent country as received in message.',
        },
        'instructed_agent_member_id': {
            'business_name': 'Instructed Agent Member ID',
            'business_description': 'Member ID of the instructed agent.',
        },
        'instructed_agent_member_id_from_msg': {
            'business_name': 'Instructed Agent Member ID From Message',
            'business_description': 'Instructed agent member ID as received in message.',
        },
        # Sender/Receiver Legacy Fields
        'sender_account': {
            'business_name': 'Sender Account',
            'business_description': 'Legacy sender account number.',
        },
        'sender_bank_code': {
            'business_name': 'Sender Bank Code',
            'business_description': 'SAMA bank code of the sender.',
        },
        'receiver_account': {
            'business_name': 'Receiver Account',
            'business_description': 'Legacy receiver account number.',
        },
        'receiver_bank_code': {
            'business_name': 'Receiver Bank Code',
            'business_description': 'SAMA bank code of the receiver.',
        },
        # Payment Type Fields
        'service_level_code': {
            'business_name': 'Service Level Code',
            'business_description': 'Service level code (SEPA, SDVA, etc.).',
        },
        'local_instrument_code': {
            'business_name': 'Local Instrument Code',
            'business_description': 'Local instrument code for payment type.',
        },
        'local_instrument_proprietary': {
            'business_name': 'Local Instrument Proprietary',
            'business_description': 'Proprietary local instrument code.',
        },
        'category_purpose_code': {
            'business_name': 'Category Purpose Code',
            'business_description': 'Category purpose code (SALA, SUPP, etc.).',
        },
        'category_purpose_proprietary': {
            'business_name': 'Category Purpose Proprietary',
            'business_description': 'Proprietary category purpose code.',
        },
        'purpose_code': {
            'business_name': 'Purpose Code',
            'business_description': 'Payment purpose code.',
        },
        'purpose_proprietary': {
            'business_name': 'Purpose Proprietary',
            'business_description': 'Proprietary payment purpose.',
        },
        'instruction_priority': {
            'business_name': 'Instruction Priority',
            'business_description': 'Priority of the payment instruction (HIGH, NORM).',
        },
        'instruction_for_agent_code': {
            'business_name': 'Instruction For Agent Code',
            'business_description': 'Instruction code for the agent.',
        },
        'instruction_for_agent_info': {
            'business_name': 'Instruction For Agent Info',
            'business_description': 'Additional instruction information for agent.',
        },
        'instruction_for_creditor_agent_code': {
            'business_name': 'Instruction For Creditor Agent Code',
            'business_description': 'Instruction code for the creditor agent.',
        },
        # Charges Fields
        'charge_bearer': {
            'business_name': 'Charge Bearer',
            'business_description': 'Party bearing the charges (DEBT, CRED, SHAR, SLEV).',
        },
        'charges_amount': {
            'business_name': 'Charges Amount',
            'business_description': 'Amount of charges applied.',
        },
        'charges_currency': {
            'business_name': 'Charges Currency',
            'business_description': 'Currency of the charges.',
        },
        'charges_agent_bic': {
            'business_name': 'Charges Agent BIC',
            'business_description': 'BIC of the agent applying charges.',
        },
        # Remittance Information
        'remittance_unstructured': {
            'business_name': 'Remittance Unstructured',
            'business_description': 'Unstructured remittance information text.',
        },
        'remittance_reference': {
            'business_name': 'Remittance Reference',
            'business_description': 'Structured remittance reference.',
        },
        'remittance_reference_type': {
            'business_name': 'Remittance Reference Type',
            'business_description': 'Type of remittance reference.',
        },
        'remittance_additional_info': {
            'business_name': 'Remittance Additional Info',
            'business_description': 'Additional remittance information.',
        },
        'referred_doc_type': {
            'business_name': 'Referred Document Type',
            'business_description': 'Type of referred document.',
        },
        'referred_doc_number': {
            'business_name': 'Referred Document Number',
            'business_description': 'Number of the referred document.',
        },
        'referred_doc_date': {
            'business_name': 'Referred Document Date',
            'business_description': 'Date of the referred document.',
        },
        # Regulatory Reporting
        'regulatory_authority_name': {
            'business_name': 'Regulatory Authority Name',
            'business_description': 'Name of the regulatory authority.',
        },
        'regulatory_authority_country': {
            'business_name': 'Regulatory Authority Country',
            'business_description': 'Country of the regulatory authority.',
        },
        'regulatory_details_type': {
            'business_name': 'Regulatory Details Type',
            'business_description': 'Type of regulatory reporting details.',
        },
        'regulatory_details_code': {
            'business_name': 'Regulatory Details Code',
            'business_description': 'Regulatory reporting code.',
        },
        'regulatory_details_info': {
            'business_name': 'Regulatory Details Info',
            'business_description': 'Additional regulatory information.',
        },
        'regulatory_details_amount': {
            'business_name': 'Regulatory Details Amount',
            'business_description': 'Amount for regulatory reporting.',
        },
        'regulatory_debit_credit_indicator': {
            'business_name': 'Regulatory Debit/Credit Indicator',
            'business_description': 'Indicator for debit or credit in regulatory reporting.',
        },
        # SARIE-Specific Fields
        'sarie_transaction_type': {
            'business_name': 'SARIE Transaction Type',
            'business_description': 'SARIE-specific transaction type code.',
        },
        'sarie_priority': {
            'business_name': 'SARIE Priority',
            'business_description': 'SARIE-specific priority level.',
        },
        'sarie_settlement_cycle': {
            'business_name': 'SARIE Settlement Cycle',
            'business_description': 'SARIE settlement cycle identifier.',
        },
        'sarie_liquidity_source': {
            'business_name': 'SARIE Liquidity Source',
            'business_description': 'Source of liquidity for SARIE settlement.',
        },
        # Supplementary Data
        'supplementary_alias_type': {
            'business_name': 'Supplementary Alias Type',
            'business_description': 'Type of supplementary alias.',
        },
        'supplementary_alias_value': {
            'business_name': 'Supplementary Alias Value',
            'business_description': 'Value of the supplementary alias.',
        },
        'supplementary_qr_code_ref': {
            'business_name': 'Supplementary QR Code Reference',
            'business_description': 'QR code reference in supplementary data.',
        },
        'supplementary_rfp_flag': {
            'business_name': 'Supplementary RFP Flag',
            'business_description': 'Request for Payment flag in supplementary data.',
        },
    },
}

# SWIFT - SWIFT MT Messages
CDM_EXTENSION_SWIFT = {
    'cdm_payment_extension_swift': {
        'extension_id': {
            'business_name': 'Extension ID',
            'business_description': 'Unique identifier for this SWIFT extension record.',
        },
        'instruction_id': {
            'business_name': 'Instruction ID',
            'business_description': 'Reference to the parent CDM payment instruction.',
        },
        'stg_id': {
            'business_name': 'Silver Stage ID',
            'business_description': 'Reference to the Silver layer staging record.',
        },
        'raw_id': {
            'business_name': 'Raw ID',
            'business_description': 'Reference to the Bronze layer raw message.',
        },
        'batch_id': {
            'business_name': 'Batch ID',
            'business_description': 'Processing batch identifier.',
        },
        'processing_status': {
            'business_name': 'Processing Status',
            'business_description': 'Current processing status of the SWIFT message.',
        },
        # Block 1 - Basic Header
        'swift_message_type': {
            'business_name': 'SWIFT Message Type',
            'business_description': 'SWIFT message type (MT103, MT202, MT940, etc.).',
        },
        'application_identifier': {
            'business_name': 'Application Identifier',
            'business_description': 'Block 1 - Application identifier (F=FIN).',
        },
        'service_identifier': {
            'business_name': 'Service Identifier',
            'business_description': 'Block 1 - Service identifier (01=FIN/GPA, 21=ACK/NAK).',
        },
        'session_number': {
            'business_name': 'Session Number',
            'business_description': 'Block 1 - Session number.',
        },
        'sequence_number': {
            'business_name': 'Sequence Number',
            'business_description': 'Block 1 - Sequence number.',
        },
        'sending_institution_bic': {
            'business_name': 'Sending Institution BIC',
            'business_description': 'BIC of the sending institution from Block 1.',
        },
        # Block 2 - Application Header
        'input_output_identifier': {
            'business_name': 'Input/Output Identifier',
            'business_description': 'Block 2 - I=Input, O=Output.',
        },
        'message_priority': {
            'business_name': 'Message Priority',
            'business_description': 'Block 2 - Message priority (S=System, U=Urgent, N=Normal).',
        },
        'delivery_monitoring': {
            'business_name': 'Delivery Monitoring',
            'business_description': 'Block 2 - Delivery monitoring flag.',
        },
        'obsolescence_period': {
            'business_name': 'Obsolescence Period',
            'business_description': 'Block 2 - Obsolescence period.',
        },
        'banking_priority': {
            'business_name': 'Banking Priority',
            'business_description': 'Block 2 - Banking priority level.',
        },
        'message_id': {
            'business_name': 'Message ID',
            'business_description': 'Unique message identifier.',
        },
        'message_user_reference': {
            'business_name': 'Message User Reference',
            'business_description': 'Block 3 - User reference (Tag 108).',
        },
        'service_type_identifier': {
            'business_name': 'Service Type Identifier',
            'business_description': 'Block 3 - Service type identifier.',
        },
        'uetr': {
            'business_name': 'UETR',
            'business_description': 'Block 3 - Unique End-to-End Transaction Reference.',
        },
        # Block 4 - Text Block - References
        'transaction_reference': {
            'business_name': 'Transaction Reference',
            'business_description': 'Field 20 - Senders transaction reference.',
        },
        'transaction_reference_number': {
            'business_name': 'Transaction Reference Number',
            'business_description': 'Field 20 - Transaction reference number.',
        },
        'transaction_type_code': {
            'business_name': 'Transaction Type Code',
            'business_description': 'Field 26T - Transaction type code.',
        },
        'instruction_codes': {
            'business_name': 'Instruction Codes',
            'business_description': 'Field 23E - Instruction codes.',
        },
        'time_indication': {
            'business_name': 'Time Indication',
            'business_description': 'Field 13C - Time indication.',
        },
        # Amount and Currency
        'value_date_currency_amount': {
            'business_name': 'Value Date Currency Amount',
            'business_description': 'Field 32A - Complete value date, currency, and amount.',
        },
        'exchange_rate': {
            'business_name': 'Exchange Rate',
            'business_description': 'Field 36 - Exchange rate.',
        },
        # Ordering Customer Fields
        'ordering_customer_id': {
            'business_name': 'Ordering Customer ID',
            'business_description': 'Field 50 - Ordering customer account identifier.',
        },
        'ordering_customer_name': {
            'business_name': 'Ordering Customer Name',
            'business_description': 'Field 50 - Ordering customer name.',
        },
        'ordering_customer_address': {
            'business_name': 'Ordering Customer Address',
            'business_description': 'Field 50 - Ordering customer address.',
        },
        'ordering_customer_country': {
            'business_name': 'Ordering Customer Country',
            'business_description': 'Field 50 - Ordering customer country code.',
        },
        'ordering_customer_town_name': {
            'business_name': 'Ordering Customer Town Name',
            'business_description': 'Field 50 - Ordering customer city/town.',
        },
        'ordering_customer_street_name': {
            'business_name': 'Ordering Customer Street Name',
            'business_description': 'Field 50 - Ordering customer street address.',
        },
        'ordering_customer_post_code': {
            'business_name': 'Ordering Customer Post Code',
            'business_description': 'Field 50 - Ordering customer postal code.',
        },
        'ordering_customer_party_id': {
            'business_name': 'Ordering Customer Party ID',
            'business_description': 'Field 50 - Ordering customer party identifier.',
        },
        'ordering_customer_national_id': {
            'business_name': 'Ordering Customer National ID',
            'business_description': 'Field 50 - Ordering customer national ID.',
        },
        # Ordering Institution Fields
        'ordering_institution_bic': {
            'business_name': 'Ordering Institution BIC',
            'business_description': 'Field 52A - Ordering institution BIC.',
        },
        'ordering_institution_account': {
            'business_name': 'Ordering Institution Account',
            'business_description': 'Field 52A - Ordering institution account.',
        },
        'ordering_institution_name': {
            'business_name': 'Ordering Institution Name',
            'business_description': 'Field 52D - Ordering institution name.',
        },
        'ordering_institution_country': {
            'business_name': 'Ordering Institution Country',
            'business_description': 'Field 52D - Ordering institution country.',
        },
        'ordering_institution_clearing_code': {
            'business_name': 'Ordering Institution Clearing Code',
            'business_description': 'Field 52D - Ordering institution clearing code.',
        },
        'ordering_institution_option_d': {
            'business_name': 'Ordering Institution Option D',
            'business_description': 'Field 52D - Ordering institution name and address.',
        },
        # Sender/Receiver Correspondent Fields
        'senders_correspondent_bic': {
            'business_name': 'Senders Correspondent BIC',
            'business_description': 'Field 53A - Senders correspondent BIC.',
        },
        'senders_correspondent_account': {
            'business_name': 'Senders Correspondent Account',
            'business_description': 'Field 53A - Senders correspondent account.',
        },
        'senders_correspondent_location': {
            'business_name': 'Senders Correspondent Location',
            'business_description': 'Field 53B - Senders correspondent location.',
        },
        'senders_correspondent_option_b': {
            'business_name': 'Senders Correspondent Option B',
            'business_description': 'Field 53B - Senders correspondent party identifier.',
        },
        'senders_correspondent_option_d': {
            'business_name': 'Senders Correspondent Option D',
            'business_description': 'Field 53D - Senders correspondent name and address.',
        },
        'sender_correspondent_bic': {
            'business_name': 'Sender Correspondent BIC',
            'business_description': 'Field 53 - Sender correspondent BIC.',
        },
        'senders_charges': {
            'business_name': 'Senders Charges',
            'business_description': 'Field 71F - Senders charges.',
        },
        'receivers_correspondent_bic': {
            'business_name': 'Receivers Correspondent BIC',
            'business_description': 'Field 54A - Receivers correspondent BIC.',
        },
        'receivers_correspondent_account': {
            'business_name': 'Receivers Correspondent Account',
            'business_description': 'Field 54A - Receivers correspondent account.',
        },
        'receivers_correspondent_location': {
            'business_name': 'Receivers Correspondent Location',
            'business_description': 'Field 54B - Receivers correspondent location.',
        },
        'receivers_correspondent_option_b': {
            'business_name': 'Receivers Correspondent Option B',
            'business_description': 'Field 54B - Receivers correspondent party identifier.',
        },
        'receivers_correspondent_option_d': {
            'business_name': 'Receivers Correspondent Option D',
            'business_description': 'Field 54D - Receivers correspondent name and address.',
        },
        'receiver_correspondent_bic': {
            'business_name': 'Receiver Correspondent BIC',
            'business_description': 'Field 54 - Receiver correspondent BIC.',
        },
        # Third Reimbursement Institution
        'third_reimbursement_bic': {
            'business_name': 'Third Reimbursement BIC',
            'business_description': 'Field 55 - Third reimbursement institution BIC.',
        },
        # Intermediary Institution
        'intermediary_bic': {
            'business_name': 'Intermediary BIC',
            'business_description': 'Field 56A - Intermediary institution BIC.',
        },
        'intermediary_account': {
            'business_name': 'Intermediary Account',
            'business_description': 'Field 56A - Intermediary account.',
        },
        'intermediary_name': {
            'business_name': 'Intermediary Name',
            'business_description': 'Field 56D - Intermediary institution name.',
        },
        'intermediary_option_d': {
            'business_name': 'Intermediary Option D',
            'business_description': 'Field 56D - Intermediary name and address.',
        },
        'intermediary_institution_bic': {
            'business_name': 'Intermediary Institution BIC',
            'business_description': 'Field 56 - Intermediary institution BIC.',
        },
        'intermediary_institution_name': {
            'business_name': 'Intermediary Institution Name',
            'business_description': 'Field 56 - Intermediary institution name.',
        },
        'intermediary_institution_country': {
            'business_name': 'Intermediary Institution Country',
            'business_description': 'Field 56 - Intermediary institution country.',
        },
        # Account With Institution
        'account_with_institution_bic': {
            'business_name': 'Account With Institution BIC',
            'business_description': 'Field 57A - Account with institution BIC.',
        },
        'account_with_institution_account': {
            'business_name': 'Account With Institution Account',
            'business_description': 'Field 57A - Account with institution account.',
        },
        'account_with_institution_option_b': {
            'business_name': 'Account With Institution Option B',
            'business_description': 'Field 57B - Account with institution party ID.',
        },
        'account_with_institution_option_d': {
            'business_name': 'Account With Institution Option D',
            'business_description': 'Field 57D - Account with institution name and address.',
        },
        # Beneficiary Fields
        'beneficiary_id': {
            'business_name': 'Beneficiary ID',
            'business_description': 'Field 59 - Beneficiary account identifier.',
        },
        'beneficiary_institution_bic': {
            'business_name': 'Beneficiary Institution BIC',
            'business_description': 'Field 58A - Beneficiary institution BIC.',
        },
        'beneficiary_institution_name': {
            'business_name': 'Beneficiary Institution Name',
            'business_description': 'Field 58D - Beneficiary institution name.',
        },
        'beneficiary_institution_option_a': {
            'business_name': 'Beneficiary Institution Option A',
            'business_description': 'Field 58A - Beneficiary institution BIC option.',
        },
        'beneficiary_institution_option_d': {
            'business_name': 'Beneficiary Institution Option D',
            'business_description': 'Field 58D - Beneficiary institution name/address.',
        },
        # Account Owner
        'account_id': {
            'business_name': 'Account ID',
            'business_description': 'Field 25 - Account identification.',
        },
        'account_owner_bic': {
            'business_name': 'Account Owner BIC',
            'business_description': 'BIC of the account owner.',
        },
        # Statement Fields (MT940/MT950)
        'statement_number': {
            'business_name': 'Statement Number',
            'business_description': 'Field 28C - Statement number/sequence number.',
        },
        'opening_balance_type': {
            'business_name': 'Opening Balance Type',
            'business_description': 'Field 60a - Opening balance type (F=First, M=Intermediate).',
        },
        'opening_balance_indicator': {
            'business_name': 'Opening Balance Indicator',
            'business_description': 'Field 60a - Credit/Debit indicator.',
        },
        'opening_balance_date': {
            'business_name': 'Opening Balance Date',
            'business_description': 'Field 60a - Opening balance date.',
        },
        'opening_balance_currency': {
            'business_name': 'Opening Balance Currency',
            'business_description': 'Field 60a - Opening balance currency.',
        },
        'opening_balance_amount': {
            'business_name': 'Opening Balance Amount',
            'business_description': 'Field 60a - Opening balance amount.',
        },
        'closing_balance_type': {
            'business_name': 'Closing Balance Type',
            'business_description': 'Field 62a - Closing balance type.',
        },
        'closing_balance_indicator': {
            'business_name': 'Closing Balance Indicator',
            'business_description': 'Field 62a - Credit/Debit indicator.',
        },
        'closing_balance_date': {
            'business_name': 'Closing Balance Date',
            'business_description': 'Field 62a - Closing balance date.',
        },
        'closing_balance_currency': {
            'business_name': 'Closing Balance Currency',
            'business_description': 'Field 62a - Closing balance currency.',
        },
        'closing_balance_amount': {
            'business_name': 'Closing Balance Amount',
            'business_description': 'Field 62a - Closing balance amount.',
        },
        'available_balance_indicator': {
            'business_name': 'Available Balance Indicator',
            'business_description': 'Field 64 - Credit/Debit indicator.',
        },
        'available_balance_date': {
            'business_name': 'Available Balance Date',
            'business_description': 'Field 64 - Available balance date.',
        },
        'available_balance_currency': {
            'business_name': 'Available Balance Currency',
            'business_description': 'Field 64 - Available balance currency.',
        },
        'available_balance_amount': {
            'business_name': 'Available Balance Amount',
            'business_description': 'Field 64 - Available balance amount.',
        },
        'forward_balance_indicator': {
            'business_name': 'Forward Balance Indicator',
            'business_description': 'Field 65 - Credit/Debit indicator.',
        },
        'forward_balance_date': {
            'business_name': 'Forward Balance Date',
            'business_description': 'Field 65 - Forward available date.',
        },
        'forward_balance_currency': {
            'business_name': 'Forward Balance Currency',
            'business_description': 'Field 65 - Forward balance currency.',
        },
        'forward_balance_amount': {
            'business_name': 'Forward Balance Amount',
            'business_description': 'Field 65 - Forward balance amount.',
        },
        # Statement Lines (Field 61)
        'statement_lines_value_date': {
            'business_name': 'Statement Line Value Date',
            'business_description': 'Field 61 - Value date for the transaction.',
        },
        'statement_lines_entry_date': {
            'business_name': 'Statement Line Entry Date',
            'business_description': 'Field 61 - Entry date (MMDD).',
        },
        'statement_lines_indicator': {
            'business_name': 'Statement Line Indicator',
            'business_description': 'Field 61 - Debit/Credit indicator.',
        },
        'statement_lines_funds_code': {
            'business_name': 'Statement Line Funds Code',
            'business_description': 'Field 61 - Funds code (3rd character of D/C mark).',
        },
        'statement_lines_amount': {
            'business_name': 'Statement Line Amount',
            'business_description': 'Field 61 - Transaction amount.',
        },
        'statement_lines_transaction_type': {
            'business_name': 'Statement Line Transaction Type',
            'business_description': 'Field 61 - Transaction type identification code.',
        },
        'statement_lines_identification_code': {
            'business_name': 'Statement Line ID Code',
            'business_description': 'Field 61 - Identification code.',
        },
        'statement_lines_reference': {
            'business_name': 'Statement Line Reference',
            'business_description': 'Field 61 - Account owners reference.',
        },
        'statement_lines_reference_account_servicer': {
            'business_name': 'Statement Line Servicer Reference',
            'business_description': 'Field 61 - Account servicers reference.',
        },
        'statement_lines_supplementary_details': {
            'business_name': 'Statement Line Supplementary Details',
            'business_description': 'Field 61 - Supplementary transaction details.',
        },
        # Totals
        'total_debit_count': {
            'business_name': 'Total Debit Count',
            'business_description': 'Total number of debit entries.',
        },
        'total_debit_amount': {
            'business_name': 'Total Debit Amount',
            'business_description': 'Total debit amount.',
        },
        'total_credit_count': {
            'business_name': 'Total Credit Count',
            'business_description': 'Total number of credit entries.',
        },
        'total_credit_amount': {
            'business_name': 'Total Credit Amount',
            'business_description': 'Total credit amount.',
        },
        # Statement Period
        'period_start_date': {
            'business_name': 'Period Start Date',
            'business_description': 'Start date of the statement period.',
        },
        'period_end_date': {
            'business_name': 'Period End Date',
            'business_description': 'End date of the statement period.',
        },
        'number_of_lines': {
            'business_name': 'Number of Lines',
            'business_description': 'Number of statement lines.',
        },
        # Information to Account Owner (Field 86)
        'info_to_account_owner': {
            'business_name': 'Info to Account Owner',
            'business_description': 'Field 86 - Information to account owner.',
        },
        'info_account_owner_code': {
            'business_name': 'Info Account Owner Code',
            'business_description': 'Field 86 - Transaction code.',
        },
        'info_account_owner_reference': {
            'business_name': 'Info Account Owner Reference',
            'business_description': 'Field 86 - Reference.',
        },
        'info_account_owner_name': {
            'business_name': 'Info Account Owner Name',
            'business_description': 'Field 86 - Counterparty name.',
        },
        # Sender to Receiver Info
        'sender_to_receiver_information': {
            'business_name': 'Sender to Receiver Info',
            'business_description': 'Field 72 - Sender to receiver information.',
        },
        # Charges
        'sender_charges_amount': {
            'business_name': 'Sender Charges Amount',
            'business_description': 'Field 71F - Sender charges amount.',
        },
        'sender_charges_currency': {
            'business_name': 'Sender Charges Currency',
            'business_description': 'Field 71F - Sender charges currency.',
        },
        'receiver_charges_amount': {
            'business_name': 'Receiver Charges Amount',
            'business_description': 'Field 71G - Receiver charges amount.',
        },
        'receiver_charges_currency': {
            'business_name': 'Receiver Charges Currency',
            'business_description': 'Field 71G - Receiver charges currency.',
        },
        # Block 5 - Trailer
        'checksum': {
            'business_name': 'Checksum',
            'business_description': 'Block 5 - CHK checksum.',
        },
        'message_authentication_code': {
            'business_name': 'Message Authentication Code',
            'business_description': 'Block 5 - MAC authentication code.',
        },
        'possible_duplicate_emission': {
            'business_name': 'Possible Duplicate Emission',
            'business_description': 'Block 5 - PDE possible duplicate flag.',
        },
        'delayed_message': {
            'business_name': 'Delayed Message',
            'business_description': 'Block 5 - DLM delayed message indicator.',
        },
        'test_training_message': {
            'business_name': 'Test/Training Message',
            'business_description': 'Block 5 - TNG test/training indicator.',
        },
        'validation_flag': {
            'business_name': 'Validation Flag',
            'business_description': 'Message validation status flag.',
        },
        'envelope_contents': {
            'business_name': 'Envelope Contents',
            'business_description': 'Original message envelope contents.',
        },
    },
}

# Combine all regional extension definitions
CDM_EXTENSION_REGIONAL = {}
CDM_EXTENSION_REGIONAL.update(CDM_EXTENSION_BACS)
CDM_EXTENSION_REGIONAL.update(CDM_EXTENSION_PIX)
CDM_EXTENSION_REGIONAL.update(CDM_EXTENSION_UPI)
CDM_EXTENSION_REGIONAL.update(CDM_EXTENSION_CNAPS)
CDM_EXTENSION_REGIONAL.update(CDM_EXTENSION_KFTC)
CDM_EXTENSION_REGIONAL.update(CDM_EXTENSION_PAYNOW)
CDM_EXTENSION_REGIONAL.update(CDM_EXTENSION_PROMPTPAY)
CDM_EXTENSION_REGIONAL.update(CDM_EXTENSION_SARIE)
CDM_EXTENSION_REGIONAL.update(CDM_EXTENSION_SWIFT)
