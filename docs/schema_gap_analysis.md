# GPS CDM Schema Gap Analysis

## Overview
Analysis of 102 columns referenced in Silver→Gold mappings that don't exist in Gold CDM tables.

## Categorization by Normalized Design

### 1. PARTY-RELATED (should be in cdm_party or party_mappings)
These are denormalized party fields - should use FK relationships instead:
- `debtor_name` → Use `debtor_id` FK to `cdm_party.name`
- `debtor_address` → Use `debtor_id` FK to `cdm_party.address_line1`
- `debtor_iban` → Use `debtor_account_id` FK to `cdm_account.iban`
- `debtor_bic` → Use `debtor_agent_id` FK to `cdm_financial_institution.bic`
- `creditor_name` → Use `creditor_id` FK to `cdm_party.name`
- `creditor_address` → Use `creditor_id` FK to `cdm_party.address_line1`
- `creditor_iban` → Use `creditor_account_id` FK to `cdm_account.iban`
- `creditor_bic` → Use `creditor_agent_id` FK to `cdm_financial_institution.bic`
- `beneficiary_name` → Use `creditor_id` FK
- `beneficiary_address` → Use `creditor_id` FK
- `beneficiary_account_number` → Use `creditor_account_id` FK
- `originator_name` → Use `debtor_id` FK
- `originator_id` → Use `debtor_id` FK to `cdm_party.identification_number`
- `ordering_customer_address` → Use `debtor_id` FK

**Action**: These should NOT be added to cdm_payment_instruction. The YAML mappings should use party_mappings/account_mappings/fi_mappings sections.

### 2. ACCOUNT-RELATED (should be in cdm_account)
- `debtor_account_number` → `cdm_account.account_number` via FK
- `creditor_account_number` → `cdm_account.account_number` via FK
- `creditor_currency` → `cdm_account.currency` via FK

**Action**: Use account_mappings in YAML.

### 3. FI-RELATED (should be in cdm_financial_institution)
- `debtor_agent_bic` → `cdm_financial_institution.bic` via `debtor_agent_id` FK
- `creditor_agent_bic` → `cdm_financial_institution.bic` via `creditor_agent_id` FK
- `debtor_agent_clearing_code` → `cdm_financial_institution.national_clearing_code`
- `creditor_agent_clearing_code` → `cdm_financial_institution.national_clearing_code`
- `sender_bic` → New FK `sender_fi_id` to `cdm_financial_institution`
- `receiver_bic` → New FK `receiver_fi_id` to `cdm_financial_institution`
- `intermediary_bic` → Use `intermediary_agent1_id` FK
- `intermediary_name` → Use `intermediary_agent1_id` FK
- `intermediary_account` → Need new entity or cdm_account link
- `third_reimbursement_bic` → New FK to `cdm_financial_institution`

**Action**: Use fi_mappings in YAML. May need additional FI role FKs in cdm_payment_instruction.

### 4. CHARGES-RELATED (should be in cdm_charge)
- `sender_charges` → `cdm_charge` with charge_type='SENDER'
- `receiver_charges_amount` → `cdm_charge` with charge_type='RECEIVER'
- `receiver_charges_currency` → `cdm_charge.currency`
- `charges_info` → `cdm_charge.charge_reason` or new field

**Action**: Use charge extraction logic to populate cdm_charge table.

### 5. MESSAGE HEADER/ENVELOPE (Legitimate additions to cdm_payment_instruction)
These are payment instruction metadata that belong in the main table:
- `swift_message_type` - SWIFT MT type (103, 202, etc.)
- `number_of_transactions` - Batch count
- `control_sum` - Batch total amount
- `batch_booking` - Batch indicator
- `payment_method` - Payment method code
- `message_creation_datetime` - When message was created
- `original_message_id` - For related/return messages
- `sender_to_receiver_info` - Bank-to-bank info
- `envelope_contents` - Raw envelope data

### 6. WIRE/ACH/RTP SPECIFIC (Need scheme-specific extension table)
These are scheme-specific fields that don't belong in the generic payment instruction:

#### FEDWIRE-specific:
- `wire_type_code`
- `wire_subtype_code`
- `omad`
- `previous_imad`
- `fi_to_fi_info`
- `input_cycle_date`
- `input_sequence_number`
- `input_source`
- `originator_id_type`
- `originator_option_f`
- `beneficiary_id_type`
- `beneficiary_reference`

#### ACH-specific:
- `immediate_destination`
- `immediate_origin`
- `file_creation_date`
- `file_creation_time`
- `file_id_modifier`
- `standard_entry_class`
- `ach_transaction_code`
- `originating_dfi_id`
- `receiving_dfi_id`
- `batch_number`
- `originator_status_code`
- `individual_id`
- `discretionary_data`
- `addenda_indicator`
- `addenda_type`
- `addenda_info`
- `return_reason_code`
- `original_entry_trace`
- `date_of_death`
- `original_receiving_dfi`
- `payment_description`

#### SEPA-specific:
- `sepa_message_type`
- `sepa_scheme`
- `mandate_id`
- `mandate_date`
- `sequence_type`
- `creditor_scheme_id`
- `settlement_method`
- `clearing_system`

#### RTP-specific:
- `clearing_system_reference`

### 7. REMITTANCE (Need cdm_remittance table or JSON field)
- `remittance_information` - Already have `remittance_unstructured`
- `structured_remittance_data` - Need JSON or separate table
- `regulatory_reporting` - Already have `regulatory_extensions` JSON

### 8. CORRESPONDENT BANKS (Need cdm_correspondent table or additional FKs)
- `sender_correspondent_account`
- `sender_correspondent_location`
- `receiver_correspondent_account`
- `receiver_correspondent_location`

---

## Recommended Schema Changes

### Option A: Extension Tables (Recommended for normalized design)

```sql
-- Scheme-specific extensions
CREATE TABLE gold.cdm_payment_extension_fedwire (
    extension_id UUID PRIMARY KEY,
    instruction_id UUID REFERENCES gold.cdm_payment_instruction(instruction_id),
    wire_type_code VARCHAR(10),
    wire_subtype_code VARCHAR(10),
    omad VARCHAR(50),
    previous_imad VARCHAR(50),
    fi_to_fi_info TEXT,
    input_cycle_date DATE,
    input_sequence_number VARCHAR(20),
    input_source VARCHAR(20),
    originator_id_type VARCHAR(10),
    originator_option_f TEXT,
    beneficiary_id_type VARCHAR(10),
    beneficiary_reference VARCHAR(35),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE gold.cdm_payment_extension_ach (
    extension_id UUID PRIMARY KEY,
    instruction_id UUID REFERENCES gold.cdm_payment_instruction(instruction_id),
    immediate_destination VARCHAR(10),
    immediate_origin VARCHAR(10),
    file_creation_date DATE,
    file_creation_time VARCHAR(4),
    file_id_modifier VARCHAR(1),
    standard_entry_class VARCHAR(3),
    transaction_code VARCHAR(2),
    originating_dfi_id VARCHAR(8),
    receiving_dfi_id VARCHAR(8),
    batch_number INTEGER,
    originator_status_code VARCHAR(1),
    individual_id VARCHAR(15),
    discretionary_data VARCHAR(2),
    addenda_indicator VARCHAR(1),
    addenda_type VARCHAR(2),
    addenda_info TEXT,
    return_reason_code VARCHAR(3),
    original_entry_trace VARCHAR(15),
    date_of_death DATE,
    original_receiving_dfi VARCHAR(8),
    payment_description VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE gold.cdm_payment_extension_sepa (
    extension_id UUID PRIMARY KEY,
    instruction_id UUID REFERENCES gold.cdm_payment_instruction(instruction_id),
    sepa_message_type VARCHAR(35),
    sepa_scheme VARCHAR(4),
    mandate_id VARCHAR(35),
    mandate_date DATE,
    sequence_type VARCHAR(4),
    creditor_scheme_id VARCHAR(35),
    settlement_method VARCHAR(4),
    clearing_system VARCHAR(5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE gold.cdm_payment_extension_swift (
    extension_id UUID PRIMARY KEY,
    instruction_id UUID REFERENCES gold.cdm_payment_instruction(instruction_id),
    swift_message_type VARCHAR(10),
    sender_bic VARCHAR(11),
    receiver_bic VARCHAR(11),
    sender_to_receiver_info TEXT,
    envelope_contents TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Option B: Add common fields to cdm_payment_instruction

For truly common fields across all payment types:

```sql
ALTER TABLE gold.cdm_payment_instruction ADD COLUMN IF NOT EXISTS
    number_of_transactions INTEGER,
    control_sum DECIMAL(18,2),
    batch_booking BOOLEAN,
    payment_method VARCHAR(10),
    message_creation_datetime TIMESTAMP,
    original_message_id VARCHAR(50),
    clearing_system VARCHAR(10),
    clearing_system_reference VARCHAR(50);
```

### Option C: JSON extension field (Simplest but less queryable)

```sql
ALTER TABLE gold.cdm_payment_instruction ADD COLUMN IF NOT EXISTS
    scheme_extensions JSONB;
```

---

## Recommendation

Use **Option A (Extension Tables)** for scheme-specific data + **Option B** for common fields.

This provides:
1. Clean normalized design
2. Efficient queries within each scheme
3. No NULL bloat in main table
4. Easy to add new schemes without altering core table
