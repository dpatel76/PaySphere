# ISO 20022 Standards Adoption Reference

This document provides the authoritative reference for how each payment standard has adopted ISO 20022, including supported message types, implementation constraints, and routing requirements for the GPS CDM pipeline.

---

## Table of Contents
1. [Classification Framework](#classification-framework)
2. [US Payment Systems](#us-payment-systems)
3. [European Payment Systems](#european-payment-systems)
4. [UK Payment Systems](#uk-payment-systems)
5. [Asia-Pacific Payment Systems](#asia-pacific-payment-systems)
6. [Middle East Payment Systems](#middle-east-payment-systems)
7. [Latin America Payment Systems](#latin-america-payment-systems)
8. [Routing Decision Matrix](#routing-decision-matrix)
9. [Implementation Constraints Summary](#implementation-constraints-summary)

---

## Classification Framework

### Adoption Categories

| Category | Description | Routing Approach |
|----------|-------------|------------------|
| **NATIVE_ISO** | Built on ISO 20022 from inception | Direct message type routing |
| **FULLY_MIGRATED** | Completed migration from legacy format | Direct message type routing |
| **INTEGRATION_ONLY** | Uses translation layer, not native | Subtype detection → ISO mapping |
| **LEGACY** | Proprietary format, no ISO migration | Subtype detection → ISO mapping |
| **PLANNED_MIGRATION** | Migration announced but not complete | Hybrid routing |

### Message Type Categories

| ISO Message | Category | Primary Use |
|-------------|----------|-------------|
| **pacs.008** | Credit Transfer | Customer credit transfer |
| **pacs.009** | Credit Transfer | FI-to-FI credit transfer |
| **pacs.002** | Status | Payment status report |
| **pacs.004** | Return | Payment return |
| **pacs.003** | Direct Debit | FI direct debit |
| **pacs.010** | Direct Debit | FI direct debit (RTGS) |
| **pain.001** | Initiation | Customer credit transfer initiation |
| **pain.002** | Status | Payment initiation status |
| **pain.008** | Initiation | Customer direct debit initiation |
| **pain.013** | Request | Request for payment |
| **pain.014** | Response | RFP response |
| **camt.053** | Statement | Account statement |
| **camt.052** | Report | Account report |
| **camt.054** | Notification | Debit/credit notification |
| **camt.056** | Cancellation | Cancellation request |
| **camt.029** | Investigation | Resolution of investigation |

---

## US Payment Systems

### FEDWIRE (Fedwire Funds Service)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | FULLY_MIGRATED |
| **Migration Date** | July 14, 2025 |
| **Operator** | Federal Reserve |
| **Settlement** | RTGS (Real-Time Gross Settlement) |

#### Supported Message Types

| Message | Use Case | Constraints |
|---------|----------|-------------|
| **pacs.008** | Customer credit transfer | End-to-End ID mandatory, UETR required |
| **pacs.009** | FI credit transfer | Creditor Agent mandatory |
| **pacs.004** | Payment return | Original transaction reference required |
| **pacs.028** | Payment status request | - |
| **camt.056** | Return request | - |
| **camt.029** | Resolution of investigation | - |
| **camt.052** | Account report | Balance reporting |
| **camt.060** | Account reporting request | - |
| **pain.013** | Drawdown request | - |

#### Implementation Constraints
- End-to-End Identification: MANDATORY (use "Not Provided" if not supplied)
- UETR: MANDATORY for all value messages
- Postal address: Must follow CBPR+ "hybrid end-state" format
- Structured addresses: Required from November 2025

#### Test Files Required
- `FEDWIRE_pacs008-e2e-test.xml`
- `FEDWIRE_pacs009-e2e-test.xml`
- `FEDWIRE_pacs004-e2e-test.xml`
- `FEDWIRE_pacs002-e2e-test.xml`

---

### CHIPS (Clearing House Interbank Payments System)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | FULLY_MIGRATED |
| **Migration Date** | April 8, 2024 |
| **Operator** | The Clearing House |
| **Settlement** | Continuous net settlement with prefunding |

#### Supported Message Types

| Message | Use Case | Notes |
|---------|----------|-------|
| **pacs.008** | Customer credit transfer | 95% are USD leg of cross-border |
| **pacs.009** | FI credit transfer | Full HVPS+ compliance |
| **pacs.002** | Payment status report | Confirmation/rejection |
| **pacs.004** | Payment return | Return processing |
| **camt.056** | Return request | Recall functionality |

#### Implementation Constraints
- Full alignment with HVPS+ and CBPR+ specifications
- First US high-value system to complete migration

#### Test Files Required
- `CHIPS_pacs008-e2e-test.xml`
- `CHIPS_pacs009-e2e-test.xml`
- `CHIPS_pacs002-e2e-test.xml`

---

### FedNow

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | NATIVE_ISO |
| **Launch Date** | July 2023 |
| **Operator** | Federal Reserve |
| **Settlement** | Real-time instant |

#### Supported Message Types

| Message | Use Case | Notes |
|---------|----------|-------|
| **pacs.008** | Credit transfer | Core payment message |
| **pacs.002** | Payment status report | Confirmation |
| **pacs.004** | Payment return | Returns |
| **pacs.028** | Payment status request | Inquiry |
| **pain.013** | Request for payment | RFP |
| **pain.014** | RFP response | RFP response |
| **camt.026** | Request for information | Investigation |
| **camt.029** | Resolution of investigation | Response |
| **camt.055** | RFP cancellation request | Cancel RFP |
| **camt.056** | Return request | Recall |
| **admi.007** | Administrative messages | System messages |

#### Implementation Constraints
- 24/7/365 availability
- Settlement within seconds
- Institution-defined credit transfer limits

#### Test Files Required
- `FEDNOW_pacs008-e2e-test.xml`
- `FEDNOW_pacs002-e2e-test.xml`
- `FEDNOW_pacs004-e2e-test.xml`
- `FEDNOW_pacs009-e2e-test.xml`

---

### RTP (Real-Time Payments by TCH)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | NATIVE_ISO |
| **Launch Date** | November 2017 |
| **Operator** | The Clearing House |
| **Settlement** | Real-time with prefunded positions |

#### Supported Message Types

| Message | Use Case | Notes |
|---------|----------|-------|
| **pacs.008** | Credit transfer | Only settlement message type |
| **pacs.002** | Payment status report | Immediate confirmation |
| **pain.013** | Request for payment | RFP capability |
| **pain.014** | RFP response | Accept/decline RFP |
| **camt.026** | Request for information | Investigation |
| **camt.028** | Information response | Investigation response |
| **camt.056** | Request for return | Recall |
| **camt.029** | Return response | Recall response |
| **remt.001** | Remittance advice | Enhanced remittance |

#### Implementation Constraints
- Credit transfer limit: $1 million (institutions may set lower)
- Real-time settlement and confirmation
- No debit capability (credit push only)

#### Test Files Required
- `RTP_pacs008-e2e-test.xml`
- `RTP_pacs002-e2e-test.xml`

---

### ACH/NACHA

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | INTEGRATION_ONLY |
| **Migration Status** | No conversion planned |
| **Operator** | Nacha / Federal Reserve ACH |
| **Settlement** | Batch (with Same Day ACH option) |

#### Message Type Mapping (NOT native ISO)

| ACH Transaction | SEC Codes | Maps To ISO | Direction |
|-----------------|-----------|-------------|-----------|
| Credit Transfer | CCD, CTX, PPD, IAT | pain.001 / pacs.008 | Credit |
| Direct Debit | PPD, CCD, WEB, TEL | pain.008 | Debit |
| Return | All (with return codes) | pacs.004 | Return |
| Reject/NOC | - | pain.002 / camt.053 | Status |

#### Subtype Detection Rules

| Condition | Subtype | Target ISO |
|-----------|---------|------------|
| Transaction Code 22, 23, 24, 32, 33, 34 | CREDIT | pacs.008 |
| Transaction Code 27, 28, 29, 37, 38, 39 | DEBIT | pain.008 |
| Transaction Code 21, 26, 31, 36 | RETURN | pacs.004 |
| Addenda Record Type 98 (NOC) | NOTIFICATION | camt.054 |
| Batch with multiple entries | BULK | pain.001 |

#### SEC Code Reference

| SEC Code | Description | Typical Direction | ISO Target |
|----------|-------------|-------------------|------------|
| CCD | Corporate Credit/Debit | Both | pacs.008 / pain.008 |
| CTX | Corporate Trade Exchange | Credit | pacs.008 |
| PPD | Prearranged Payment/Deposit | Both | pacs.008 / pain.008 |
| IAT | International ACH | Credit | pacs.008 |
| WEB | Internet-Initiated | Debit | pain.008 |
| TEL | Telephone-Initiated | Debit | pain.008 |
| ARC | Accounts Receivable Check | Debit | pain.008 |
| BOC | Back Office Conversion | Debit | pain.008 |
| POP | Point of Purchase | Debit | pain.008 |
| RCK | Re-presented Check | Debit | pain.008 |

#### Implementation Constraints
- Lines must be exactly 94 characters
- Position-based parsing required
- Same Day ACH: settlement by end of business day
- Standard ACH: next-day settlement

#### Test Files Required
- `ACH-CCD-CREDIT-e2e-test.ach` → pacs.008
- `ACH-PPD-DEBIT-e2e-test.ach` → pain.008
- `ACH-RETURN-e2e-test.ach` → pacs.004
- `ACH-CTX-CREDIT-e2e-test.ach` → pacs.008
- `ACH-WEB-DEBIT-e2e-test.ach` → pain.008

---

## European Payment Systems

### TARGET2 (T2)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | FULLY_MIGRATED |
| **Migration Date** | March 20, 2023 |
| **Operator** | European Central Bank |
| **Settlement** | RTGS |

#### Supported Message Types

| Message | Variant | Use Case |
|---------|---------|----------|
| **pacs.008** | STP | Customer credit transfer |
| **pacs.009** | CORE | FI credit transfer |
| **pacs.009** | COV | Cover payment |
| **pacs.009** | Simplified | Simplified FI transfer |
| **pacs.010** | - | FI direct debit |
| **pacs.002** | - | Payment status report |
| **pacs.004** | - | Payment return |
| **camt.056** | - | Cancellation request |
| **camt.029** | - | Resolution of investigation |
| **camt.057** | - | Notification to receive |

#### Implementation Constraints
- ISO MR 2025 upgrade planned for autumn 2025
- Seven core payment messages prioritized
- RTGS hours: 02:30 CET to 18:00 CET

#### Test Files Required
- `TARGET2_pacs008-e2e-test.xml`
- `TARGET2_pacs009-e2e-test.xml`
- `TARGET2_pacs002-e2e-test.xml`
- `TARGET2_pacs004-e2e-test.xml`

---

### SEPA (SCT, SDD, SCT Inst)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | NATIVE_ISO |
| **Launch Date** | 2008 (SCT), 2009 (SDD), 2017 (SCT Inst) |
| **Operator** | European Payments Council |
| **Settlement** | Varies by scheme |

#### Scheme-Specific Message Types

**SEPA Credit Transfer (SCT):**
| Message | Direction | Use Case |
|---------|-----------|----------|
| pain.001 | Customer → Bank | Payment initiation |
| pain.002 | Bank → Customer | Status report |
| pacs.008 | Bank → Bank | Interbank transfer |
| pacs.002 | Bank → Bank | Status/rejection |
| pacs.004 | Bank → Bank | Return |
| camt.056 | Bank → Bank | Recall |

**SEPA Direct Debit (SDD):**
| Message | Direction | Use Case |
|---------|-----------|----------|
| pain.008 | Creditor → Bank | DD initiation |
| pain.002 | Bank → Creditor | Status report |
| pacs.003 | Bank → Bank | Interbank DD |
| pacs.002 | Bank → Bank | Status/rejection |

**SEPA Instant (SCT Inst):**
| Message | Use Case | Constraints |
|---------|----------|-------------|
| pacs.008.001.08 | Single instant payment | 10-second max |
| pacs.002 | Confirmation (ACCP) / Rejection (RJCT) | Immediate |
| pacs.028 | Status request | - |

#### Implementation Constraints
- SCT Inst: Transaction must complete within 10 seconds
- Structured addresses: MANDATORY from November 2025
- Amount limits vary by scheme

#### Test Files Required
- `SEPA_pacs008-e2e-test.xml`
- `SEPA_pacs002-e2e-test.xml`
- `SEPA_pain001-e2e-test.xml`
- `SEPA_pain008-e2e-test.xml`
- `SEPA_INST_pacs008-e2e-test.xml`
- `SEPA_INST_pacs002-e2e-test.xml`

---

## UK Payment Systems

### CHAPS

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | FULLY_MIGRATED |
| **Migration Date** | June 19, 2023 |
| **Operator** | Bank of England |
| **Settlement** | RTGS |

#### Supported Message Types

| Message | Variant | Use Case |
|---------|---------|----------|
| **pacs.008** | - | Customer credit transfer |
| **pacs.009** | CORE | FI credit transfer |
| **pacs.009** | COV | Cover payment |
| **pacs.002** | - | Payment status report |
| **pacs.004** | - | Payment return |
| **camt.056** | - | Cancellation request |
| **camt.029** | - | Resolution of investigation |

#### Enhanced Data Requirements Timeline

| Date | Requirement |
|------|-------------|
| **May 2025** | LEIs mandatory for FI-to-FI payments |
| **May 2025** | Purpose Codes mandatory for pacs.009 CORE |
| **November 2025** | Structured remittance mandatory in pacs.008 |
| **November 2025** | Structured addresses mandatory |
| **November 2026** | Fully unstructured addresses rejected |
| **November 2027** | pacs.009 COV must include all LEIs from underlying pacs.008 |

#### Implementation Constraints
- LEI: MANDATORY for payments between FIs (from May 2025)
- Purpose Codes: MANDATORY for specific transaction types
- Property transactions require enhanced data

#### Test Files Required
- `CHAPS_pacs008-e2e-test.xml`
- `CHAPS_pacs009-e2e-test.xml`
- `CHAPS_pacs002-e2e-test.xml`
- `CHAPS_pacs004-e2e-test.xml`

---

### FPS (UK Faster Payments)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | PLANNED_MIGRATION |
| **Current Format** | ISO 8583 |
| **Migration Timeline** | TBD (confirmation by end of July 2025) |
| **Operator** | Pay.UK |

#### Target Message Types (Post-Migration)

| Message | Use Case |
|---------|----------|
| pacs.008 | Credit transfer |
| pacs.002 | Status report |
| pain.013 | Request for payment |
| pain.014 | RFP response |
| camt.* | Exceptions |

#### Current State
- Uses ISO 8583 format
- Pay.UK has published ISO 20022 Standards Library
- Conversion mapping available for transition planning

#### Test Files Required
- `FPS_pacs008-e2e-test.xml`
- `FPS_pacs002-e2e-test.xml`

---

### BACS

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | LEGACY |
| **Current Format** | Standard 18 (proprietary) |
| **Migration Status** | No confirmed timeline |
| **Operator** | Pay.UK |

#### Subtype Detection Rules

| Transaction Type | Description | Maps To ISO |
|------------------|-------------|-------------|
| 99 | BACS Credit | pacs.008 |
| 17 | Faster Payment fallback credit | pacs.008 |
| 01 | Direct Debit | pain.008 |
| 18, 19 | Direct Debit variations | pain.008 |

#### Implementation Constraints
- Standard 18 format required for submission
- Translation from/to ISO 20022 supported
- Batch processing (3-day cycle)

#### Test Files Required
- `BACS-CREDIT-e2e-test.txt` → pacs.008
- `BACS-DEBIT-e2e-test.txt` → pain.008

---

## Asia-Pacific Payment Systems

### NPP (Australia New Payments Platform)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | NATIVE_ISO |
| **Launch Date** | February 2018 |
| **Operator** | Australian Payments Plus |
| **Settlement** | Real-time (15 seconds) |

#### Supported Message Types

| Message | Use Case | Notes |
|---------|----------|-------|
| **pacs.008** | Credit transfer | Core message |
| **pacs.002** | Settlement notification | Confirmation |
| **pacs.004** | Payment return | Returns |
| Additional pacs/camt | Exceptions | Investigation |

#### Implementation Constraints
- Up to 280 characters of remittance data
- Over 1,400 data fields available
- Settlement within 15 seconds
- Some proprietary codes for internal processes

#### Test Files Required
- `NPP_pacs008-e2e-test.xml`
- `NPP_pacs002-e2e-test.xml`
- `NPP_pacs004-e2e-test.xml`

---

### MEPS+ (Singapore MAS Electronic Payment System)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | FULLY_MIGRATED |
| **Migration Date** | August 2022 (Like-for-Like++) |
| **Operator** | Monetary Authority of Singapore |
| **Settlement** | RTGS |

#### Supported Message Types
- Aligned with CBPR+ and HVPS+
- Over 100 messages mapped
- Full pacs.008, pacs.009 support

#### Implementation Constraints
- Like-for-Like++ allows progressive data enrichment
- Message schemas in SWIFT MyStandards
- Common standards for domestic and international payments

#### Test Files Required
- `MEPS_PLUS_pacs008-e2e-test.xml`
- `MEPS_PLUS_pacs009-e2e-test.xml`
- `MEPS_PLUS_pacs002-e2e-test.xml`

---

### PayNow/FAST (Singapore)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | NATIVE_ISO |
| **Format** | ISO 20022 based |
| **Operator** | Association of Banks in Singapore |
| **Settlement** | Real-time |

#### Supported Message Types
- pacs.008 (Credit transfer)
- pacs.002 (Status)

#### Test Files Required
- `PAYNOW_pacs008-e2e-test.xml` (if testing separately from FAST)

---

### CHATS/RTGS_HK (Hong Kong)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | FULLY_MIGRATED |
| **Migration Date** | April 2024 |
| **Operator** | HKMA |
| **Settlement** | RTGS |

#### Supported Message Types

| Message | Use Case |
|---------|----------|
| pacs.008 | Customer credit transfer |
| pacs.009 | FI credit transfer |
| pacs.002 | Payment status report |
| pacs.004 | Payment return |

#### Implementation Constraints
- HKMA-specific adaptations to pacs.008
- Local regulatory requirements applied

#### Test Files Required
- `RTGS_HK_pacs008-e2e-test.xml`
- `RTGS_HK_pacs009-e2e-test.xml`
- `RTGS_HK_pacs002-e2e-test.xml`

---

### CNAPS (China)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | FULLY_MIGRATED |
| **Migration Date** | 2013 (First country globally) |
| **Operator** | People's Bank of China |
| **Systems** | CNAPS2, IBPS, CIPS |

#### System-Specific Message Types

| System | Type | Messages |
|--------|------|----------|
| **CNAPS2 (HVPS)** | RTGS High-Value | pacs.008, pacs.009 |
| **CNAPS2 (BEPS)** | Bulk/Retail | pain.001, pacs.008 |
| **IBPS** | Internet Banking | pacs.008 |
| **CIPS** | Cross-border RMB | Full ISO 20022 suite |

#### Subtype Detection Rules

| System Type | Description | Maps To ISO |
|-------------|-------------|-------------|
| HVPS / HIGH_VALUE | Real-time gross settlement | pacs.008, pacs.009 |
| BEPS / BULK | Batch electronic payment | pain.001 |
| IBPS / INTERNET | Internet banking | pacs.008 |

#### Implementation Constraints
- Supports Mandarin characters
- Proprietary network (not SWIFT)
- International ISO 20022 standard on local infrastructure

#### Test Files Required
- `CNAPS-HVPS-e2e-test.json` → pacs.008
- `CNAPS-BEPS-e2e-test.json` → pain.001

---

### BOJ-NET (Japan)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | FULLY_MIGRATED (upgrading) |
| **Version Upgrade** | November 25, 2025 (Version 3 → Version 8) |
| **Operator** | Bank of Japan |
| **Settlement** | RTGS |

#### Supported Message Types
- Standard ISO 20022 pacs/camt messages
- Currently Version 3, upgrading to Version 8 (2019)

#### Implementation Constraints
- Foreign exchange yen settlements
- Current account transactions for overseas institutions
- Version upgrade aligns with SWIFT MT/MX coexistence end

#### Test Files Required
- `BOJNET_pacs008-e2e-test.xml`

---

### KFTC/BOK-Wire (Korea)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | IN_PROGRESS |
| **Target Completion** | 2026 |
| **Operator** | Bank of Korea / Korea Financial Telecommunications |

#### Notes
- Migration in progress
- Full details require Bank of Korea official documentation

#### Test Files Required
- `KFTC_pacs008-e2e-test.json`

---

### UPI (India)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | NOT_ISO20022 |
| **Current Format** | ISO 8583 |
| **Operator** | NPCI (National Payments Corporation of India) |
| **Settlement** | Real-time |

#### Why NOT ISO 20022
- ISO 8583 optimized for high-volume mobile/digital channels
- Speed requirements (larger ISO 20022 messages less suitable)
- 16.58 billion transactions in October 2024 alone
- 50% of global instant transactions

#### Subtype Detection Rules (ISO 8583 to ISO 20022 Mapping)

| MTI | Processing Code | Description | Maps To ISO |
|-----|-----------------|-------------|-------------|
| 0200, 0210 | 00, 01, 40 | Financial Transaction | pacs.008 |
| 0100, 0110 | - | Authorization | pain.001 |
| 0420, 0430 | 20 | Reversal/Refund | pacs.004 |
| 0400, 0410 | - | Cancellation | camt.056 |

#### Transaction Type Detection

| Condition | Subtype | Target ISO |
|-----------|---------|------------|
| txnType = "PAY" | PAYMENT | pacs.008 |
| txnType = "REFUND" | REFUND | pacs.004 |
| txnType = "COLLECT" | COLLECT | pain.008 |
| mti = "0420" or "0430" | REVERSAL | pacs.004 |

#### Implementation Constraints
- VPA (Virtual Payment Address) format: user@bank
- IFSC code required for account routing
- INR currency only

#### Test Files Required
- `UPI-PAY-e2e-test.json` → pacs.008
- `UPI-REFUND-e2e-test.json` → pacs.004
- `UPI-COLLECT-e2e-test.json` → pain.008

---

### PromptPay/BAHTNET (Thailand)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | NATIVE_ISO (PromptPay), MIGRATED (BAHTNET Aug 2022) |
| **Operator** | Bank of Thailand |

#### Supported Message Types
- pacs.008 (Credit transfer)
- pacs.002 (Status)

#### Test Files Required
- `PROMPTPAY_pacs008-e2e-test.json`

---

## Middle East Payment Systems

### SARIE (Saudi Arabia)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | FULLY_MIGRATED |
| **Migration Date** | 2023 |
| **Operator** | SAMA (Saudi Central Bank) |
| **Systems** | SARIE RTGS, Sarie IPS |

#### Supported Message Types

| Message | System | Use Case |
|---------|--------|----------|
| pacs.008 | Both | Credit transfer |
| pacs.009 | RTGS | FI credit transfer |
| pacs.002 | Both | Status |
| pacs.004 | Both | Return |

#### Implementation Constraints
- Sarie IPS: ~600 million instant payments in 2024
- 24/7 real-time delivery
- P2P, P2B, B2B support

#### Test Files Required
- `SARIE_pacs008-e2e-test.xml`
- `SARIE_pacs009-e2e-test.xml`

---

### UAEFTS (UAE)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | PLANNED_MIGRATION |
| **Current Format** | RTGS with SFTP |
| **Operator** | Central Bank of UAE |

#### Current State
- Operating since 2001
- May align with ISO 20022 for international interoperability
- No specific confirmed migration dates

#### Test Files Required
- `UAEFTS_pacs008-e2e-test.xml`
- `UAEFTS_pacs009-e2e-test.xml`
- `UAEFTS_pacs002-e2e-test.xml`

---

## Latin America Payment Systems

### PIX (Brazil)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | NATIVE_ISO |
| **Launch Date** | November 2020 |
| **Operator** | Central Bank of Brazil (BCB) |
| **Settlement** | Real-time |

#### Supported Message Types

| Message | Use Case |
|---------|----------|
| pacs.008 | Instant credit transfer |
| pacs.002 | Payment status/confirmation |
| pacs.004 | Payment return |

#### Implementation Constraints
- 24/7/365 operation
- Settlement in seconds
- PIX keys for addressing (CPF/CNPJ, email, phone, random)

#### Test Files Required
- `PIX_pacs008-e2e-test.json`
- `PIX_pacs004-e2e-test.json`

---

### InstaPay (Philippines)

| Attribute | Value |
|-----------|-------|
| **Adoption Status** | PARTIAL_MIGRATION |
| **Full Mandate** | 2026-2027 (BSP Circular 1223) |
| **Operator** | BSP |
| **Platform** | Mastercard Vocalink |

#### Current State
- Uses ISO 20022 messaging format (partial implementation)
- BSP mandated full adoption within 2 years from Dec 2024

#### Supported Message Types
- pacs.008 (Credit transfer)
- pacs.002 (Status)

#### Test Files Required
- `INSTAPAY_pacs008-e2e-test.xml`
- `INSTAPAY_pacs009-e2e-test.xml`
- `INSTAPAY_pacs002-e2e-test.xml`

---

## Routing Decision Matrix

### By Adoption Status

| Status | Routing Approach |
|--------|------------------|
| NATIVE_ISO | Direct: format_messageType (e.g., `RTP_pacs008`) |
| FULLY_MIGRATED | Direct: format_messageType (e.g., `FEDWIRE_pacs008`) |
| INTEGRATION_ONLY | Detect subtype → map to ISO (e.g., ACH CCD → pacs.008) |
| LEGACY | Detect subtype → map to ISO (e.g., BACS 99 → pacs.008) |
| NOT_ISO20022 | Detect subtype → map to ISO (e.g., UPI PAY → pacs.008) |

### Subtype Detection Required

| Format | Detection Method | Key Field |
|--------|------------------|-----------|
| ACH | Transaction code + SEC code | Line position 1-2, 51-53 |
| BACS | Transaction type | Position 17-18 |
| UPI | txnType / mti field | JSON field |
| CNAPS | system_type field | JSON field |

---

## Implementation Constraints Summary

### Mandatory Fields by Market

| Market | End-to-End ID | UETR | LEI | Structured Address |
|--------|---------------|------|-----|-------------------|
| FEDWIRE | MANDATORY | MANDATORY | - | Nov 2025 |
| CHIPS | MANDATORY | MANDATORY | - | Nov 2025 |
| CHAPS | MANDATORY | MANDATORY | May 2025 | Nov 2025 |
| TARGET2 | MANDATORY | - | - | - |
| SEPA | MANDATORY | - | - | Nov 2025 |

### Character/Data Limits

| System | Remittance Data | Address Lines | Transaction Limit |
|--------|-----------------|---------------|-------------------|
| NPP | 280 chars | Standard | - |
| RTP | Standard | Standard | $1M |
| FedNow | Standard | Standard | Institution-defined |
| SCT Inst | Standard | Standard | €100,000 default |

### Settlement Times

| System | Settlement Time |
|--------|-----------------|
| SCT Inst | 10 seconds |
| NPP | 15 seconds |
| FedNow | Seconds |
| RTP | Seconds |
| TARGET2/CHAPS | RTGS (minutes) |
| ACH Same Day | End of business day |
| BACS | 3 business days |

---

## Appendix: Complete Format/Message Type Matrix

| Format | pacs.008 | pacs.009 | pacs.002 | pacs.004 | pain.001 | pain.008 | camt.053 |
|--------|----------|----------|----------|----------|----------|----------|----------|
| FEDWIRE | ✅ | ✅ | ✅ | ✅ | - | - | - |
| CHIPS | ✅ | ✅ | ✅ | ✅ | - | - | - |
| FEDNOW | ✅ | ✅ | ✅ | ✅ | - | - | - |
| RTP | ✅ | - | ✅ | - | - | - | - |
| ACH* | ✅ | - | - | ✅ | ✅ | ✅ | ✅ |
| TARGET2 | ✅ | ✅ | ✅ | ✅ | - | - | - |
| SEPA | ✅ | - | ✅ | ✅ | ✅ | ✅ | - |
| CHAPS | ✅ | ✅ | ✅ | ✅ | - | - | - |
| FPS | ✅ | - | ✅ | - | - | - | - |
| BACS* | ✅ | - | - | - | - | ✅ | - |
| NPP | ✅ | - | ✅ | ✅ | - | - | - |
| MEPS_PLUS | ✅ | ✅ | ✅ | - | - | - | - |
| RTGS_HK | ✅ | ✅ | ✅ | ✅ | - | - | - |
| CNAPS | ✅ | ✅ | - | - | ✅ | - | - |
| UPI* | ✅ | - | - | ✅ | - | ✅ | - |
| PIX | ✅ | - | ✅ | ✅ | - | - | - |
| SARIE | ✅ | ✅ | ✅ | ✅ | - | - | - |
| UAEFTS | ✅ | ✅ | ✅ | - | - | - | - |
| INSTAPAY | ✅ | ✅ | ✅ | - | - | - | - |

*Requires subtype detection for routing
