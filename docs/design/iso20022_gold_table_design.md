# ISO 20022 Gold Table Design - Semantic Naming

## Design Philosophy

Each ISO 20022 message type maps to a dedicated Gold table with semantic naming that reflects:
1. **Message Category** (pain, pacs, camt, etc.)
2. **Message Purpose** (what the message represents in business terms)

This replaces the generic `cdm_payment_instruction` approach with domain-specific tables.

---

## Complete ISO 20022 Gold Table Mapping

### PAIN Messages (Payment Initiation - Customer to Bank)

| ISO Message | Gold Table Name | Description |
|------------|-----------------|-------------|
| **pain.001** | `cdm_pain_customer_credit_transfer_initiation` | Customer requests bank to send money |
| **pain.002** | `cdm_pain_customer_payment_status_report` | Bank reports payment status to customer |
| **pain.008** | `cdm_pain_customer_direct_debit_initiation` | Customer requests bank to collect money |
| **pain.013** | `cdm_pain_creditor_payment_activation_request` | Creditor requests debtor to pay (RfP) |
| **pain.014** | `cdm_pain_creditor_payment_activation_request_status` | Status of RfP request |

### PACS Messages (Payments Clearing & Settlement - Bank to Bank)

| ISO Message | Gold Table Name | Description |
|------------|-----------------|-------------|
| **pacs.002** | `cdm_pacs_fi_payment_status_report` | Interbank payment status report |
| **pacs.003** | `cdm_pacs_fi_direct_debit` | Interbank direct debit execution |
| **pacs.004** | `cdm_pacs_payment_return` | Payment return/reversal |
| **pacs.008** | `cdm_pacs_fi_customer_credit_transfer` | Interbank customer credit transfer |
| **pacs.009** | `cdm_pacs_fi_credit_transfer` | Financial institution own funds transfer |
| **pacs.010** | `cdm_pacs_fi_direct_debit` | Financial institution direct debit |
| **pacs.028** | `cdm_pacs_fi_payment_status_request` | Request for payment status |

### CAMT Messages (Cash Management)

| ISO Message | Gold Table Name | Description |
|------------|-----------------|-------------|
| **camt.052** | `cdm_camt_bank_to_customer_account_report` | Intraday account report |
| **camt.053** | `cdm_camt_bank_to_customer_statement` | End-of-day account statement |
| **camt.054** | `cdm_camt_bank_to_customer_debit_credit_notification` | Transaction notification |
| **camt.056** | `cdm_camt_fi_payment_cancellation_request` | FI-to-FI cancellation request |
| **camt.029** | `cdm_camt_resolution_of_investigation` | Response to investigation |
| **camt.026** | `cdm_camt_unable_to_apply` | Unable to apply message |
| **camt.027** | `cdm_camt_claim_non_receipt` | Claim non-receipt of payment |
| **camt.087** | `cdm_camt_request_to_modify_payment` | Request to modify payment |

---

## Detailed Table Designs

### 1. cdm_pain_customer_credit_transfer_initiation (pain.001)

**Purpose**: Customer → Bank: "Please send this payment"

```sql
CREATE TABLE gold.cdm_pain_customer_credit_transfer_initiation (
    -- Primary Key
    initiation_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,  -- pain.001, SEPA_pain001, etc.

    -- Message Identification
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,

    -- Initiating Party
    initiating_party_name VARCHAR(140),
    initiating_party_id VARCHAR(35),
    initiating_party_id_type VARCHAR(35),

    -- Payment Information (header level)
    payment_info_id VARCHAR(35),
    payment_method VARCHAR(3),  -- TRF, CHK, TRA
    batch_booking BOOLEAN,
    number_of_transactions INT,
    control_sum DECIMAL(18,4),
    requested_execution_date DATE,

    -- Service Level
    service_level_code VARCHAR(4),
    local_instrument_code VARCHAR(35),
    category_purpose_code VARCHAR(4),

    -- Debtor (Payer)
    debtor_name VARCHAR(140) NOT NULL,
    debtor_address_country VARCHAR(2),
    debtor_id VARCHAR(35),
    debtor_id_type VARCHAR(35),

    -- Debtor Account
    debtor_account_iban VARCHAR(34),
    debtor_account_other VARCHAR(34),
    debtor_account_currency VARCHAR(3),

    -- Debtor Agent (Bank)
    debtor_agent_bic VARCHAR(11),
    debtor_agent_name VARCHAR(140),
    debtor_agent_clearing_system_id VARCHAR(35),

    -- Transaction Details
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35) NOT NULL,
    instructed_amount DECIMAL(18,4) NOT NULL,
    instructed_currency VARCHAR(3) NOT NULL,
    charge_bearer VARCHAR(4),

    -- Creditor Agent (Bank)
    creditor_agent_bic VARCHAR(11),
    creditor_agent_name VARCHAR(140),
    creditor_agent_clearing_system_id VARCHAR(35),

    -- Creditor (Payee)
    creditor_name VARCHAR(140) NOT NULL,
    creditor_address_country VARCHAR(2),
    creditor_id VARCHAR(35),
    creditor_id_type VARCHAR(35),

    -- Creditor Account
    creditor_account_iban VARCHAR(34),
    creditor_account_other VARCHAR(34),
    creditor_account_currency VARCHAR(3),

    -- Ultimate Parties (optional)
    ultimate_debtor_name VARCHAR(140),
    ultimate_creditor_name VARCHAR(140),

    -- Remittance
    remittance_unstructured TEXT[],
    remittance_structured JSONB,
    purpose_code VARCHAR(4),

    -- Regulatory
    regulatory_reporting JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);
```

### 2. cdm_pacs_fi_customer_credit_transfer (pacs.008)

**Purpose**: Bank → Bank: Actual interbank payment execution

```sql
CREATE TABLE gold.cdm_pacs_fi_customer_credit_transfer (
    -- Primary Key
    transfer_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,  -- pacs.008, FEDWIRE, CHIPS, CHAPS, etc.

    -- Group Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,
    number_of_transactions INT,
    total_interbank_settlement_amount DECIMAL(18,4),
    settlement_method VARCHAR(4),  -- INDA, INGA, COVE, CLRG
    clearing_system VARCHAR(35),

    -- Instructing/Instructed Agents
    instructing_agent_bic VARCHAR(11),
    instructing_agent_clearing_id VARCHAR(35),
    instructed_agent_bic VARCHAR(11),
    instructed_agent_clearing_id VARCHAR(35),

    -- Payment Identification
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35) NOT NULL,
    uetr VARCHAR(36),  -- Unique End-to-end Transaction Reference
    transaction_id VARCHAR(35),
    clearing_system_reference VARCHAR(35),

    -- Payment Type
    instruction_priority VARCHAR(4),
    service_level_code VARCHAR(4),
    local_instrument_code VARCHAR(35),
    category_purpose_code VARCHAR(4),

    -- Settlement
    interbank_settlement_amount DECIMAL(18,4) NOT NULL,
    interbank_settlement_currency VARCHAR(3) NOT NULL,
    interbank_settlement_date DATE NOT NULL,
    instructed_amount DECIMAL(18,4),
    instructed_currency VARCHAR(3),
    exchange_rate DECIMAL(18,10),

    -- Charges
    charge_bearer VARCHAR(4),
    charges_amount DECIMAL(18,4),
    charges_currency VARCHAR(3),

    -- Debtor
    debtor_name VARCHAR(140) NOT NULL,
    debtor_address_country VARCHAR(2),
    debtor_id VARCHAR(35),

    -- Debtor Account
    debtor_account_iban VARCHAR(34),
    debtor_account_other VARCHAR(34),

    -- Debtor Agent
    debtor_agent_bic VARCHAR(11),
    debtor_agent_clearing_id VARCHAR(35),
    debtor_agent_name VARCHAR(140),
    debtor_agent_country VARCHAR(2),

    -- Creditor Agent
    creditor_agent_bic VARCHAR(11),
    creditor_agent_clearing_id VARCHAR(35),
    creditor_agent_name VARCHAR(140),
    creditor_agent_country VARCHAR(2),

    -- Creditor
    creditor_name VARCHAR(140) NOT NULL,
    creditor_address_country VARCHAR(2),
    creditor_id VARCHAR(35),

    -- Creditor Account
    creditor_account_iban VARCHAR(34),
    creditor_account_other VARCHAR(34),

    -- Intermediary Agents
    intermediary_agent1_bic VARCHAR(11),
    intermediary_agent1_country VARCHAR(2),
    intermediary_agent2_bic VARCHAR(11),
    intermediary_agent2_country VARCHAR(2),

    -- Ultimate Parties
    ultimate_debtor_name VARCHAR(140),
    ultimate_creditor_name VARCHAR(140),

    -- Remittance
    remittance_unstructured TEXT[],
    remittance_structured JSONB,
    purpose_code VARCHAR(4),

    -- Regulatory & Supplementary
    regulatory_reporting JSONB,
    supplementary_data JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);
```

### 3. cdm_pacs_fi_payment_status_report (pacs.002)

**Purpose**: Bank → Bank: Status report on a previous payment

```sql
CREATE TABLE gold.cdm_pacs_fi_payment_status_report (
    -- Primary Key
    status_report_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,

    -- Message Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,

    -- Original Message Reference
    original_message_id VARCHAR(35) NOT NULL,
    original_message_name_id VARCHAR(35),
    original_creation_datetime TIMESTAMP,
    original_number_of_transactions INT,

    -- Group Status (if applicable)
    group_status VARCHAR(4),  -- ACCP, ACTC, ACSP, ACWC, PART, PDNG, RCVD, RJCT
    group_status_reason_code VARCHAR(4),
    group_status_reason_info TEXT,

    -- Transaction Status
    status_id VARCHAR(35),
    original_instruction_id VARCHAR(35),
    original_end_to_end_id VARCHAR(35),
    original_uetr VARCHAR(36),
    transaction_status VARCHAR(4) NOT NULL,  -- ACCP, ACTC, ACSP, ACWC, PART, PDNG, RCVD, RJCT
    status_reason_code VARCHAR(4),
    status_reason_additional_info TEXT,
    acceptance_datetime TIMESTAMP,
    effective_settlement_date DATE,
    clearing_system_reference VARCHAR(35),

    -- Original Transaction Reference (partial copy)
    original_settlement_amount DECIMAL(18,4),
    original_settlement_currency VARCHAR(3),
    original_settlement_date DATE,
    original_debtor_name VARCHAR(140),
    original_debtor_account VARCHAR(34),
    original_debtor_agent_bic VARCHAR(11),
    original_creditor_name VARCHAR(140),
    original_creditor_account VARCHAR(34),
    original_creditor_agent_bic VARCHAR(11),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);
```

### 4. cdm_pacs_payment_return (pacs.004)

**Purpose**: Bank → Bank: Return/reversal of a previous payment

```sql
CREATE TABLE gold.cdm_pacs_payment_return (
    -- Primary Key
    return_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,

    -- Message Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,
    number_of_transactions INT,
    settlement_method VARCHAR(4),
    clearing_system VARCHAR(5),

    -- Original Message Reference
    original_message_id VARCHAR(35) NOT NULL,
    original_message_name_id VARCHAR(35),
    original_creation_datetime TIMESTAMP,

    -- Return Transaction
    return_id_ref VARCHAR(35),
    original_instruction_id VARCHAR(35),
    original_end_to_end_id VARCHAR(35),
    original_transaction_id VARCHAR(35),
    original_uetr VARCHAR(36),
    original_clearing_system_reference VARCHAR(35),

    -- Return Reason
    return_reason_code VARCHAR(4) NOT NULL,  -- AC01, AC04, AM04, etc.
    return_reason_proprietary VARCHAR(35),
    return_reason_additional_info TEXT,
    return_originator_name VARCHAR(140),
    return_originator_bic VARCHAR(11),

    -- Returned Amount
    returned_settlement_amount DECIMAL(18,4) NOT NULL,
    returned_settlement_currency VARCHAR(3) NOT NULL,
    return_settlement_date DATE NOT NULL,

    -- Original Transaction Reference
    original_settlement_amount DECIMAL(18,4),
    original_settlement_currency VARCHAR(3),
    original_settlement_date DATE,

    -- Original Debtor (now receives funds back)
    original_debtor_name VARCHAR(140),
    original_debtor_country VARCHAR(2),
    original_debtor_account_iban VARCHAR(34),
    original_debtor_account_other VARCHAR(35),
    original_debtor_agent_bic VARCHAR(11),

    -- Original Creditor (returning funds)
    original_creditor_name VARCHAR(140),
    original_creditor_country VARCHAR(2),
    original_creditor_account_iban VARCHAR(34),
    original_creditor_account_other VARCHAR(35),
    original_creditor_agent_bic VARCHAR(11),

    -- Instructing/Instructed Agents (for return)
    instructing_agent_bic VARCHAR(11),
    instructed_agent_bic VARCHAR(11),

    -- Remittance
    remittance_unstructured TEXT[],

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);
```

### 5. cdm_pacs_fi_credit_transfer (pacs.009)

**Purpose**: Bank → Bank: Bank's own funds transfer (not customer funds)

```sql
CREATE TABLE gold.cdm_pacs_fi_credit_transfer (
    -- Primary Key
    transfer_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,  -- pacs.009, TARGET2

    -- Group Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,
    number_of_transactions INT,
    total_settlement_amount DECIMAL(18,4),
    settlement_method VARCHAR(4),
    clearing_system VARCHAR(35),

    -- Instructing/Instructed Agents
    instructing_agent_bic VARCHAR(11),
    instructing_agent_lei VARCHAR(20),
    instructed_agent_bic VARCHAR(11),
    instructed_agent_lei VARCHAR(20),

    -- Payment Identification
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35) NOT NULL,
    uetr VARCHAR(36),
    transaction_id VARCHAR(35),
    clearing_system_reference VARCHAR(35),

    -- Payment Type
    instruction_priority VARCHAR(4),
    service_level_code VARCHAR(4),

    -- Settlement
    interbank_settlement_amount DECIMAL(18,4) NOT NULL,
    interbank_settlement_currency VARCHAR(3) NOT NULL,
    interbank_settlement_date DATE NOT NULL,

    -- Debtor Agent (Sending FI)
    debtor_agent_bic VARCHAR(11) NOT NULL,
    debtor_agent_lei VARCHAR(20),
    debtor_agent_name VARCHAR(140),
    debtor_agent_clearing_id VARCHAR(35),
    debtor_agent_country VARCHAR(2),
    debtor_agent_account_id VARCHAR(34),

    -- Creditor Agent (Receiving FI)
    creditor_agent_bic VARCHAR(11) NOT NULL,
    creditor_agent_lei VARCHAR(20),
    creditor_agent_name VARCHAR(140),
    creditor_agent_clearing_id VARCHAR(35),
    creditor_agent_country VARCHAR(2),
    creditor_agent_account_id VARCHAR(34),

    -- Intermediary Agents
    intermediary_agent1_bic VARCHAR(11),
    intermediary_agent1_country VARCHAR(2),
    intermediary_agent2_bic VARCHAR(11),
    intermediary_agent2_country VARCHAR(2),

    -- Underlying Customer Transfer (for cover payments)
    underlying_customer_transfer JSONB,

    -- Remittance & Purpose
    remittance_unstructured TEXT[],
    purpose_code VARCHAR(4),

    -- Supplementary
    supplementary_data JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);
```

### 6. cdm_pain_customer_direct_debit_initiation (pain.008)

**Purpose**: Customer → Bank: "Please collect money from this debtor"

```sql
CREATE TABLE gold.cdm_pain_customer_direct_debit_initiation (
    -- Primary Key
    initiation_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,  -- pain.008, SEPA_pain008

    -- Message Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,
    number_of_transactions INT,
    control_sum DECIMAL(18,4),

    -- Initiating Party
    initiating_party_name VARCHAR(140),
    initiating_party_id VARCHAR(35),

    -- Payment Information
    payment_info_id VARCHAR(35),
    payment_method VARCHAR(3),  -- DD
    service_level_code VARCHAR(4),
    local_instrument_code VARCHAR(35),  -- CORE, B2B, COR1
    sequence_type VARCHAR(4),  -- FRST, RCUR, FNAL, OOFF
    category_purpose_code VARCHAR(4),
    requested_collection_date DATE NOT NULL,

    -- Creditor (Collecting Party)
    creditor_name VARCHAR(140) NOT NULL,
    creditor_address_country VARCHAR(2),
    creditor_id VARCHAR(35),  -- Creditor Scheme ID
    creditor_id_type VARCHAR(35),

    -- Creditor Account
    creditor_account_iban VARCHAR(34),
    creditor_account_other VARCHAR(35),
    creditor_account_currency VARCHAR(3),

    -- Creditor Agent
    creditor_agent_bic VARCHAR(11),
    creditor_agent_clearing_id VARCHAR(35),

    -- Direct Debit Transaction
    instruction_id VARCHAR(35),
    end_to_end_id VARCHAR(35) NOT NULL,
    instructed_amount DECIMAL(18,4) NOT NULL,
    instructed_currency VARCHAR(3) NOT NULL,
    charge_bearer VARCHAR(4),

    -- Mandate Information
    mandate_id VARCHAR(35) NOT NULL,
    mandate_date_of_signature DATE,
    amendment_indicator BOOLEAN,

    -- Debtor Agent (Bank being debited)
    debtor_agent_bic VARCHAR(11),
    debtor_agent_clearing_id VARCHAR(35),

    -- Debtor (Party being debited)
    debtor_name VARCHAR(140) NOT NULL,
    debtor_address_country VARCHAR(2),

    -- Debtor Account
    debtor_account_iban VARCHAR(34),
    debtor_account_other VARCHAR(35),

    -- Ultimate Parties
    ultimate_debtor_name VARCHAR(140),
    ultimate_creditor_name VARCHAR(140),

    -- Remittance
    remittance_unstructured TEXT[],
    remittance_structured_reference VARCHAR(35),
    purpose_code VARCHAR(4),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);
```

### 7. cdm_camt_bank_to_customer_statement (camt.053)

**Purpose**: Bank → Customer: End-of-day account statement

```sql
CREATE TABLE gold.cdm_camt_bank_to_customer_statement (
    -- Primary Key
    statement_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,

    -- Message Header
    message_id VARCHAR(35) NOT NULL,
    creation_datetime TIMESTAMP NOT NULL,
    message_recipient_name VARCHAR(140),

    -- Statement Identification
    statement_reference VARCHAR(35) NOT NULL,
    electronic_sequence_number BIGINT,
    statement_creation_datetime TIMESTAMP,
    from_datetime TIMESTAMP,
    to_datetime TIMESTAMP,

    -- Account
    account_iban VARCHAR(34),
    account_other_id VARCHAR(34),
    account_currency VARCHAR(3),
    account_owner_name VARCHAR(140),
    account_servicer_bic VARCHAR(11),
    account_servicer_name VARCHAR(140),

    -- Opening Balance
    opening_balance_type VARCHAR(4),  -- OPBD, PRCD
    opening_balance_amount DECIMAL(18,4),
    opening_balance_currency VARCHAR(3),
    opening_balance_credit_debit VARCHAR(4),  -- CRDT, DBIT
    opening_balance_date DATE,

    -- Closing Balance
    closing_balance_type VARCHAR(4),  -- CLBD
    closing_balance_amount DECIMAL(18,4),
    closing_balance_currency VARCHAR(3),
    closing_balance_credit_debit VARCHAR(4),
    closing_balance_date DATE,

    -- Available Balance
    available_balance_amount DECIMAL(18,4),
    available_balance_currency VARCHAR(3),
    available_balance_date DATE,

    -- Transaction Summary
    total_number_of_entries INT,
    total_sum DECIMAL(18,4),
    total_credit_entries INT,
    total_credit_sum DECIMAL(18,4),
    total_debit_entries INT,
    total_debit_sum DECIMAL(18,4),

    -- Entries (stored separately for detail, summary here)
    entries_count INT,
    entries JSONB,  -- Array of entry summaries

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);
```

### 8. cdm_camt_fi_payment_cancellation_request (camt.056)

**Purpose**: Bank → Bank: Request to cancel a previous payment

```sql
CREATE TABLE gold.cdm_camt_fi_payment_cancellation_request (
    -- Primary Key
    cancellation_request_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,

    -- Source Lineage
    source_stg_id VARCHAR(36) NOT NULL,
    source_stg_table VARCHAR(100) NOT NULL,
    source_format VARCHAR(30) NOT NULL,

    -- Assignment
    assignment_id VARCHAR(35) NOT NULL,
    assignment_creation_datetime TIMESTAMP NOT NULL,
    assigner_agent_bic VARCHAR(11),
    assignee_agent_bic VARCHAR(11),

    -- Case
    case_id VARCHAR(35),
    case_creator_name VARCHAR(140),

    -- Original Message Reference
    original_message_id VARCHAR(35) NOT NULL,
    original_message_name_id VARCHAR(35),
    original_creation_datetime TIMESTAMP,

    -- Transaction to Cancel
    cancellation_id VARCHAR(35),
    original_instruction_id VARCHAR(35),
    original_end_to_end_id VARCHAR(35),
    original_transaction_id VARCHAR(35),
    original_uetr VARCHAR(36),
    original_clearing_system_reference VARCHAR(35),

    -- Cancellation Reason
    cancellation_reason_code VARCHAR(4) NOT NULL,  -- CUST, DUPL, TECH, FRAD, etc.
    cancellation_reason_proprietary VARCHAR(35),
    cancellation_reason_additional_info TEXT,

    -- Original Transaction Reference
    original_settlement_amount DECIMAL(18,4),
    original_settlement_currency VARCHAR(3),
    original_settlement_date DATE,

    -- Original Parties
    original_debtor_name VARCHAR(140),
    original_debtor_account_iban VARCHAR(34),
    original_debtor_agent_bic VARCHAR(11),
    original_creditor_name VARCHAR(140),
    original_creditor_account_iban VARCHAR(34),
    original_creditor_agent_bic VARCHAR(11),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _batch_id VARCHAR(36)
);
```

---

## Summary: Gold Table Mapping

| ISO Message | Gold Table | Business Domain |
|------------|------------|-----------------|
| pain.001 | `cdm_pain_customer_credit_transfer_initiation` | Payment Initiation |
| pain.002 | `cdm_pain_customer_payment_status_report` | Payment Initiation |
| pain.008 | `cdm_pain_customer_direct_debit_initiation` | Payment Initiation |
| pacs.002 | `cdm_pacs_fi_payment_status_report` | Clearing & Settlement |
| pacs.003 | `cdm_pacs_fi_direct_debit` | Clearing & Settlement |
| pacs.004 | `cdm_pacs_payment_return` | Clearing & Settlement |
| pacs.008 | `cdm_pacs_fi_customer_credit_transfer` | Clearing & Settlement |
| pacs.009 | `cdm_pacs_fi_credit_transfer` | Clearing & Settlement |
| camt.052 | `cdm_camt_bank_to_customer_account_report` | Cash Management |
| camt.053 | `cdm_camt_bank_to_customer_statement` | Cash Management |
| camt.054 | `cdm_camt_bank_to_customer_debit_credit_notification` | Cash Management |
| camt.056 | `cdm_camt_fi_payment_cancellation_request` | Cash Management |

---

## Entity Tables (Shared Across All Messages)

These remain shared across all Gold tables via FK relationships:

| Table | Purpose |
|-------|---------|
| `cdm_party` | All party references (debtors, creditors, etc.) |
| `cdm_account` | All account references |
| `cdm_financial_institution` | All FI/agent references |

Each message-specific Gold table has columns for inline party/account data, but can also FK to these shared tables for normalized storage.

---

## Proprietary Format Mapping to ISO 20022 Gold Tables

Proprietary formats map into the appropriate ISO 20022 Gold table based on their functional equivalent:

### Credit Transfer Formats → `cdm_pacs_fi_customer_credit_transfer`

| Proprietary Format | Region | ISO Equivalent | Notes |
|-------------------|--------|----------------|-------|
| **MT103** | Global | pacs.008 | SWIFT customer credit transfer |
| **MT103STP** | Global | pacs.008 | SWIFT STP variant |
| **FEDWIRE** | US | pacs.008 | Federal Reserve wire |
| **CHIPS** | US | pacs.008 | CHIPS large value |
| **ACH** | US | pacs.008 | ACH batch credits |
| **CHAPS** | UK | pacs.008 | UK RTGS |
| **FPS** | UK | pacs.008 | UK Faster Payments |
| **BACS** | UK | pacs.008 | UK batch payments |
| **FEDNOW** | US | pacs.008 | US instant payments |
| **RTP** | US | pacs.008 | US real-time payments |
| **NPP** | AU | pacs.008 | Australia New Payments Platform |
| **SEPA SCT** | EU | pacs.008 | SEPA Credit Transfer |
| **MEPS_PLUS** | SG | pacs.008 | Singapore RTGS |
| **RTGS_HK** | HK | pacs.008 | Hong Kong RTGS |
| **UAEFTS** | UAE | pacs.008 | UAE funds transfer |
| **INSTAPAY** | PH | pacs.008 | Philippines instant |
| **PIX** | BR | pacs.008 | Brazil instant payments |
| **UPI** | IN | pacs.008 | India unified payments |
| **PROMPTPAY** | TH | pacs.008 | Thailand instant |
| **PAYNOW** | SG | pacs.008 | Singapore P2P |

### Bank-to-Bank Transfer Formats → `cdm_pacs_fi_credit_transfer`

| Proprietary Format | Region | ISO Equivalent | Notes |
|-------------------|--------|----------------|-------|
| **MT202** | Global | pacs.009 | SWIFT bank transfer |
| **MT202COV** | Global | pacs.009 | SWIFT cover payment |
| **TARGET2** | EU | pacs.009 | Eurosystem RTGS |

### Direct Debit Formats → `cdm_pain_customer_direct_debit_initiation`

| Proprietary Format | Region | ISO Equivalent | Notes |
|-------------------|--------|----------------|-------|
| **SEPA SDD** | EU | pain.008 | SEPA Direct Debit |
| **ACH Debit** | US | pain.008 | ACH debit entries |
| **BACS DD** | UK | pain.008 | UK Direct Debit |

### Payment Status Formats → `cdm_pacs_fi_payment_status_report`

| Proprietary Format | Region | ISO Equivalent | Notes |
|-------------------|--------|----------------|-------|
| **MT199** | Global | pacs.002 | SWIFT free format (status) |
| **ACH Return** | US | pacs.002 | ACH return notification |

### Account Statement Formats → `cdm_camt_bank_to_customer_statement`

| Proprietary Format | Region | ISO Equivalent | Notes |
|-------------------|--------|----------------|-------|
| **MT940** | Global | camt.053 | SWIFT EOD statement |
| **MT942** | Global | camt.052 | SWIFT interim statement |
| **BAI2** | US | camt.053 | US bank statement format |

### Return/Reversal Formats → `cdm_pacs_payment_return`

| Proprietary Format | Region | ISO Equivalent | Notes |
|-------------------|--------|----------------|-------|
| **MT900/910** | Global | pacs.004 | SWIFT debit/credit advice |
| **ACH Return** | US | pacs.004 | ACH return entries |

---

## Complete Format-to-Gold-Table Mapping

### Summary Table

| Gold Table | ISO Messages | Proprietary Formats |
|-----------|--------------|---------------------|
| `cdm_pain_customer_credit_transfer_initiation` | pain.001 | (customer-initiated, pre-bank) |
| `cdm_pain_customer_direct_debit_initiation` | pain.008 | SEPA SDD, ACH Debit, BACS DD |
| `cdm_pain_customer_payment_status_report` | pain.002 | (customer status reports) |
| `cdm_pacs_fi_customer_credit_transfer` | pacs.008 | MT103, FEDWIRE, CHIPS, ACH, CHAPS, FPS, BACS, FEDNOW, RTP, NPP, MEPS_PLUS, RTGS_HK, UAEFTS, INSTAPAY, PIX, UPI, PROMPTPAY, PAYNOW |
| `cdm_pacs_fi_credit_transfer` | pacs.009 | MT202, MT202COV, TARGET2 |
| `cdm_pacs_fi_payment_status_report` | pacs.002 | MT199 (status), ACH acknowledgments |
| `cdm_pacs_payment_return` | pacs.004 | MT900/910, ACH Returns |
| `cdm_pacs_fi_direct_debit` | pacs.003 | (interbank direct debit) |
| `cdm_camt_bank_to_customer_statement` | camt.053 | MT940, BAI2 |
| `cdm_camt_bank_to_customer_account_report` | camt.052 | MT942 |
| `cdm_camt_bank_to_customer_debit_credit_notification` | camt.054 | MT900, MT910 |
| `cdm_camt_fi_payment_cancellation_request` | camt.056 | (cancellation requests) |

---

## Key Design Principle

**Proprietary formats do NOT get their own Gold tables.** Instead:

1. Each proprietary format is mapped to its ISO 20022 functional equivalent
2. The `source_format` column in each Gold table identifies the originating format
3. Format-specific fields that don't fit the ISO structure go in `supplementary_data` JSONB column
4. This enables unified querying across all payment types

### Example: Querying All Credit Transfers

```sql
-- Find all credit transfers over $10,000 regardless of source format
SELECT
    transfer_id,
    source_format,  -- pacs.008, MT103, FEDWIRE, ACH, etc.
    debtor_name,
    creditor_name,
    interbank_settlement_amount,
    interbank_settlement_currency
FROM gold.cdm_pacs_fi_customer_credit_transfer
WHERE interbank_settlement_amount > 10000
ORDER BY creation_datetime DESC;
```

---

## Migration Path

1. Create new Gold tables with semantic names
2. Update `mapping.message_formats` to reference new `gold_table`
3. Update `mapping.gold_field_mappings` for each format
4. Create views for backward compatibility if needed
5. Run E2E tests for all formats
