# GPS CDM - Comprehensive Standards and Reports Inventory
## Complete Scope for 100% Coverage

**Purpose:** Document ALL payment standards and regulatory reports requiring mapping to GPS CDM
**Date:** 2024-12-20
**Status:** 🔄 IN PROGRESS - Comprehensive scope being implemented

---

## Executive Summary

This document provides the **complete, comprehensive inventory** of all payment standards and regulatory reports that must be mapped to the GPS Common Domain Model for a global financial institution.

**Expanded Scope:**
- **ISO 20022 Messages:** 45+ messages across PACS, PAIN, CAMT categories
- **SWIFT MT Messages:** 15+ message types
- **Regional Payment Systems:** 10+ systems (US, EU, APAC, LatAm)
- **Regulatory Reports:** 40+ reports across 15+ jurisdictions
- **Estimated Total Fields:** 8,000+ fields

---

## ISO 20022 Payment Messages (Complete)

### PACS - Payments Clearing and Settlement (14 messages)

| # | Message | Description | Fields (Est.) | Priority | Status |
|---|---------|-------------|---------------|----------|--------|
| 1 | **pacs.002** | FI to FI Payment Status Report | 95 | HIGH | ⏸️ Pending |
| 2 | **pacs.003** | FI to FI Customer Direct Debit | 135 | HIGH | ⏸️ Pending |
| 3 | **pacs.004** | Payment Return | 110 | HIGH | ⏸️ Pending |
| 4 | **pacs.007** | FI to FI Payment Reversal | 95 | HIGH | ⏸️ Pending |
| 5 | **pacs.008** | FI to FI Customer Credit Transfer | 142 | HIGH | ✅ Complete |
| 6 | **pacs.009** | Financial Institution Credit Transfer | 125 | MEDIUM | ⏸️ Pending |
| 7 | **pacs.010** | Financial Institution Direct Debit | 120 | MEDIUM | ⏸️ Pending |
| 8 | **pacs.028** | FI to FI Payment Status Request | 65 | MEDIUM | ⏸️ Pending |
| 9 | **pacs.029** | Resolution of Investigation | 85 | LOW | ⏸️ Pending |
| 10 | **pacs.030** | Unable to Apply | 75 | LOW | ⏸️ Pending |

**Subtotal:** 10 messages, ~1,247 fields

### PAIN - Payment Initiation (14 messages)

| # | Message | Description | Fields (Est.) | Priority | Status |
|---|---------|-------------|---------------|----------|--------|
| 1 | **pain.001** | Customer Credit Transfer Initiation | 156 | HIGH | ✅ Complete |
| 2 | **pain.002** | Customer Payment Status Report | 82 | HIGH | ⏸️ Pending |
| 3 | **pain.007** | Customer Payment Reversal | 88 | HIGH | ⏸️ Pending |
| 4 | **pain.008** | Customer Direct Debit Initiation | 145 | HIGH | ⏸️ Pending |
| 5 | **pain.009** | Mandate Initiation Request | 92 | MEDIUM | ⏸️ Pending |
| 6 | **pain.010** | Mandate Amendment Request | 87 | MEDIUM | ⏸️ Pending |
| 7 | **pain.011** | Mandate Cancellation Request | 65 | MEDIUM | ⏸️ Pending |
| 8 | **pain.012** | Mandate Acceptance Report | 78 | MEDIUM | ⏸️ Pending |
| 9 | **pain.013** | Creditor Payment Activation Request | 95 | MEDIUM | ⏸️ Pending |
| 10 | **pain.014** | Creditor Payment Activation Request Status | 72 | MEDIUM | ⏸️ Pending |
| 11 | **pain.017** | Mandate Initiation Request Status Report | 68 | LOW | ⏸️ Pending |
| 12 | **pain.018** | Mandate Amendment Request Status Report | 64 | LOW | ⏸️ Pending |

**Subtotal:** 12 messages, ~1,192 fields

### CAMT - Cash Management (12 messages)

| # | Message | Description | Fields (Est.) | Priority | Status |
|---|---------|-------------|---------------|----------|--------|
| 1 | **camt.026** | Unable to Apply | 85 | MEDIUM | ⏸️ Pending |
| 2 | **camt.029** | Resolution of Investigation | 95 | MEDIUM | ⏸️ Pending |
| 3 | **camt.052** | Bank to Customer Account Report | 165 | HIGH | ⏸️ Pending |
| 4 | **camt.053** | Bank to Customer Statement | 178 | HIGH | ⏸️ Pending |
| 5 | **camt.054** | Bank to Customer Debit Credit Notification | 152 | HIGH | ⏸️ Pending |
| 6 | **camt.055** | Customer Payment Cancellation Request | 98 | HIGH | ⏸️ Pending |
| 7 | **camt.056** | FI to FI Payment Cancellation Request | 98 | HIGH | ⏸️ Pending |
| 8 | **camt.057** | Notification to Receive | 88 | MEDIUM | ⏸️ Pending |
| 9 | **camt.058** | Notification to Receive Cancellation Advice | 72 | LOW | ⏸️ Pending |
| 10 | **camt.060** | Account Reporting Request | 95 | MEDIUM | ⏸️ Pending |
| 11 | **camt.086** | Bank Service Billing | 125 | LOW | ⏸️ Pending |
| 12 | **camt.087** | Request to Modify Payment | 85 | LOW | ⏸️ Pending |

**Subtotal:** 12 messages, ~1,336 fields

**ISO 20022 Total:** 34 messages, ~3,775 fields

---

## SWIFT MT Messages (Complete)

| # | Message | Description | Fields (Est.) | Priority | Status |
|---|---------|-------------|---------------|----------|--------|
| 1 | **MT101** | Request for Transfer | 65 | MEDIUM | ⏸️ Pending |
| 2 | **MT103** | Single Customer Credit Transfer | 58 | HIGH | ✅ Complete |
| 3 | **MT103+** | Single Customer Credit Transfer (STP) | 62 | HIGH | ⏸️ Pending |
| 4 | **MT103 REMIT** | Single Customer Credit with Remittance | 68 | MEDIUM | ⏸️ Pending |
| 5 | **MT192** | Request for Cancellation | 45 | MEDIUM | ⏸️ Pending |
| 6 | **MT195** | Queries | 42 | LOW | ⏸️ Pending |
| 7 | **MT196** | Answers | 40 | LOW | ⏸️ Pending |
| 8 | **MT199** | Free Format Message | 25 | LOW | ⏸️ Pending |
| 9 | **MT200** | FI Transfer for Own Account | 38 | MEDIUM | ⏸️ Pending |
| 10 | **MT201** | Multiple FI Transfer for Own Account | 42 | MEDIUM | ⏸️ Pending |
| 11 | **MT202** | General FI Transfer | 47 | HIGH | ⏸️ Pending |
| 12 | **MT202COV** | General FI Transfer (Cover) | 52 | HIGH | ⏸️ Pending |
| 13 | **MT203** | Multiple General FI Transfer | 50 | MEDIUM | ⏸️ Pending |
| 14 | **MT204** | Direct Debit Message | 48 | MEDIUM | ⏸️ Pending |
| 15 | **MT205** | FI Market Transfer | 45 | LOW | ⏸️ Pending |
| 16 | **MT210** | Notice to Receive | 38 | LOW | ⏸️ Pending |
| 17 | **MT292** | Request for Cancellation | 42 | MEDIUM | ⏸️ Pending |
| 18 | **MT900** | Confirmation of Debit | 35 | LOW | ⏸️ Pending |
| 19 | **MT910** | Confirmation of Credit | 35 | LOW | ⏸️ Pending |
| 20 | **MT950** | Statement Message | 55 | MEDIUM | ⏸️ Pending |

**SWIFT Total:** 20 messages, ~932 fields

---

## Regional Payment Systems

| # | System | Country/Region | Fields (Est.) | Priority | Status |
|---|--------|----------------|---------------|----------|--------|
| 1 | **Fedwire** | USA | 85 | HIGH | ✅ Complete |
| 2 | **NACHA ACH** | USA | 52 | HIGH | ✅ Complete |
| 3 | **CHIPS** | USA | 42 | MEDIUM | ⏸️ Pending |
| 4 | **RTP (Real-Time Payments)** | USA | 78 | HIGH | ⏸️ Pending |
| 5 | **SEPA SCT** | Europe | 118 | HIGH | ✅ Complete |
| 6 | **SEPA SCT Inst** | Europe | 122 | HIGH | ⏸️ Pending |
| 7 | **SEPA SDD Core** | Europe | 135 | HIGH | ⏸️ Pending |
| 8 | **SEPA SDD B2B** | Europe | 128 | MEDIUM | ⏸️ Pending |
| 9 | **TARGET2** | Europe | 95 | MEDIUM | ⏸️ Pending |
| 10 | **UK Faster Payments** | UK | 56 | MEDIUM | ⏸️ Pending |
| 11 | **BACS** | UK | 68 | MEDIUM | ⏸️ Pending |
| 12 | **CHAPS** | UK | 72 | MEDIUM | ⏸️ Pending |
| 13 | **PIX** | Brazil | 72 | HIGH | ✅ Complete |
| 14 | **UPI** | India | 67 | HIGH | ✅ Complete |
| 15 | **PayNow** | Singapore | 51 | MEDIUM | ⏸️ Pending |
| 16 | **PromptPay** | Thailand | 48 | MEDIUM | ⏸️ Pending |
| 17 | **InstaPay** | Philippines | 55 | LOW | ⏸️ Pending |
| 18 | **NPP** | Australia | 64 | MEDIUM | ⏸️ Pending |
| 19 | **CNAPS** | China | 88 | MEDIUM | ⏸️ Pending |
| 20 | **RTGS** | Hong Kong | 62 | MEDIUM | ⏸️ Pending |

**Regional Systems Total:** 20 systems, ~1,558 fields

---

## Regulatory Reports - United States

### FinCEN (Financial Crimes Enforcement Network)

| # | Report | Form # | Fields (Est.) | Priority | Status |
|---|--------|--------|---------------|----------|--------|
| 1 | **CTR** | Form 112 | 117 | HIGH | ✅ Complete |
| 2 | **SAR** | Form 111 | 184 | HIGH | ✅ Complete |
| 3 | **FBAR** | Form 114 | 92 | HIGH | ⏸️ Pending |
| 4 | **Form 8300** | Cash Payments Over $10,000 | 78 | HIGH | ⏸️ Pending |
| 5 | **314(a) Request** | Information Request | 45 | MEDIUM | ⏸️ Pending |
| 6 | **314(b) Notice** | Information Sharing | 38 | MEDIUM | ⏸️ Pending |
| 7 | **CTR-Aggregation** | Aggregated Currency Transaction | 95 | MEDIUM | ⏸️ Pending |

**FinCEN Subtotal:** 7 reports, ~649 fields

### IRS (Internal Revenue Service)

| # | Report | Form # | Fields (Est.) | Priority | Status |
|---|--------|--------|---------------|----------|--------|
| 1 | **FATCA Form 8966** | FATCA Report | 97 | HIGH | ✅ Complete |
| 2 | **FATCA Pool Reporting** | Pooled Reporting | 67 | MEDIUM | ⏸️ Pending |
| 3 | **Form 1099-INT** | Interest Income | 52 | MEDIUM | ⏸️ Pending |
| 4 | **Form 1099-B** | Proceeds from Broker Transactions | 68 | MEDIUM | ⏸️ Pending |
| 5 | **Form 1042-S** | Foreign Person's US Source Income | 75 | MEDIUM | ⏸️ Pending |

**IRS Subtotal:** 5 reports, ~359 fields

### OFAC (Office of Foreign Assets Control)

| # | Report | Description | Fields (Est.) | Priority | Status |
|---|--------|-------------|---------------|----------|--------|
| 1 | **Sanctions Blocking Report** | Blocked Property Report | 72 | HIGH | ⏸️ Pending |
| 2 | **Rejected Transaction Report** | Rejected OFAC Transactions | 58 | MEDIUM | ⏸️ Pending |
| 3 | **Voluntary Self-Disclosure** | Sanctions Violations | 85 | MEDIUM | ⏸️ Pending |

**OFAC Subtotal:** 3 reports, ~215 fields

**US Total:** 15 reports, ~1,223 fields

---

## Regulatory Reports - Australia

### AUSTRAC

| # | Report | Description | Fields (Est.) | Priority | Status |
|---|--------|-------------|---------------|----------|--------|
| 1 | **IFTI** | International Funds Transfer Instruction | 87 | HIGH | ✅ Complete |
| 2 | **TTR** | Threshold Transaction Report | 76 | HIGH | ⏸️ Pending |
| 3 | **SMR** | Suspicious Matter Report | 92 | HIGH | ⏸️ Pending |
| 4 | **IFT-I** | International Funds Transfer Instruction (Inbound) | 82 | HIGH | ⏸️ Pending |
| 5 | **IFT-O** | International Funds Transfer Instruction (Outbound) | 84 | HIGH | ⏸️ Pending |
| 6 | **AML/CTF Compliance Report** | Annual Compliance | 125 | MEDIUM | ⏸️ Pending |

**AUSTRAC Total:** 6 reports, ~546 fields

---

## Regulatory Reports - Europe

### EBA (European Banking Authority)

| # | Report | Description | Fields (Est.) | Priority | Status |
|---|--------|-------------|---------------|----------|--------|
| 1 | **PSD2 Fraud Report** | Payment Services Directive 2 Fraud | 87 | HIGH | ⏸️ Pending |
| 2 | **PSD2 Operational/Security Incidents** | Incident Reporting | 65 | MEDIUM | ⏸️ Pending |

**EBA Subtotal:** 2 reports, ~152 fields

### ESMA (European Securities and Markets Authority)

| # | Report | Description | Fields (Est.) | Priority | Status |
|---|--------|-------------|---------------|----------|--------|
| 1 | **MiFID II Transaction Reporting** | Investment Services | 142 | HIGH | ⏸️ Pending |
| 2 | **EMIR Trade Reporting** | Derivatives Reporting | 156 | HIGH | ⏸️ Pending |
| 3 | **MAR STOR** | Suspicious Transactions and Orders | 98 | HIGH | ⏸️ Pending |

**ESMA Subtotal:** 3 reports, ~396 fields

**Europe Total:** 5 reports, ~548 fields

---

## Regulatory Reports - United Kingdom

### UK NCA (National Crime Agency)

| # | Report | Description | Fields (Est.) | Priority | Status |
|---|--------|-------------|---------------|----------|--------|
| 1 | **UK SAR** | Suspicious Activity Report | 122 | HIGH | ⏸️ Pending |
| 2 | **UK DAML SAR** | Defence Against Money Laundering SAR | 132 | HIGH | ⏸️ Pending |

### UK FCA (Financial Conduct Authority)

| # | Report | Description | Fields (Est.) | Priority | Status |
|---|--------|-------------|---------------|----------|--------|
| 1 | **SUP 16 Returns** | Regulatory Returns | 185 | MEDIUM | ⏸️ Pending |
| 2 | **REP-CRIM** | Financial Crime Returns | 95 | HIGH | ⏸️ Pending |

**UK Total:** 4 reports, ~534 fields

---

## Regulatory Reports - OECD

| # | Report | Description | Fields (Est.) | Priority | Status |
|---|--------|-------------|---------------|----------|--------|
| 1 | **CRS Reporting** | Common Reporting Standard | 108 | HIGH | ⏸️ Pending |
| 2 | **CRS Controlling Person** | Controlling Person Report | 85 | HIGH | ⏸️ Pending |

**OECD Total:** 2 reports, ~193 fields

---

## Regulatory Reports - Other Major Jurisdictions

### Canada (FINTRAC)

| # | Report | Description | Fields (Est.) | Priority | Status |
|---|--------|-------------|---------------|----------|--------|
| 1 | **LCTR** | Large Cash Transaction Report | 95 | HIGH | ⏸️ Pending |
| 2 | **STR** | Suspicious Transaction Report | 125 | HIGH | ⏸️ Pending |
| 3 | **EFTR** | Electronic Funds Transfer Report | 88 | HIGH | ⏸️ Pending |
| 4 | **TPR** | Terrorist Property Report | 62 | HIGH | ⏸️ Pending |

**Canada Total:** 4 reports, ~370 fields

### Singapore (MAS)

| # | Report | Description | Fields (Est.) | Priority | Status |
|---|--------|-------------|---------------|----------|--------|
| 1 | **STR** | Suspicious Transaction Report | 112 | HIGH | ⏸️ Pending |
| 2 | **CTR** | Cash Transaction Report | 78 | HIGH | ⏸️ Pending |

**Singapore Total:** 2 reports, ~190 fields

### Hong Kong (HKMA)

| # | Report | Description | Fields (Est.) | Priority | Status |
|---|--------|-------------|---------------|----------|--------|
| 1 | **STR** | Suspicious Transaction Report | 105 | HIGH | ⏸️ Pending |
| 2 | **Large Cash Transaction** | Cash Transaction Report | 72 | MEDIUM | ⏸️ Pending |

**Hong Kong Total:** 2 reports, ~177 fields

### Japan (JFSA)

| # | Report | Description | Fields (Est.) | Priority | Status |
|---|--------|-------------|---------------|----------|--------|
| 1 | **STR** | Suspicious Transaction Report | 98 | HIGH | ⏸️ Pending |
| 2 | **Large Cash Transaction** | Cash Transaction Report | 68 | MEDIUM | ⏸️ Pending |

**Japan Total:** 2 reports, ~166 fields

**Other Jurisdictions Total:** 10 reports, ~903 fields

---

## Complete Summary

### Overall Totals

| Category | Messages/Reports | Estimated Fields | Completed | Remaining |
|----------|-----------------|------------------|-----------|-----------|
| **ISO 20022 (PACS)** | 10 | 1,247 | 1 (10%) | 9 (90%) |
| **ISO 20022 (PAIN)** | 12 | 1,192 | 1 (8%) | 11 (92%) |
| **ISO 20022 (CAMT)** | 12 | 1,336 | 0 (0%) | 12 (100%) |
| **SWIFT MT** | 20 | 932 | 1 (5%) | 19 (95%) |
| **Regional Systems** | 20 | 1,558 | 5 (25%) | 15 (75%) |
| **US Reports** | 15 | 1,223 | 2 (13%) | 13 (87%) |
| **Australia Reports** | 6 | 546 | 1 (17%) | 5 (83%) |
| **Europe Reports** | 5 | 548 | 0 (0%) | 5 (100%) |
| **UK Reports** | 4 | 534 | 0 (0%) | 4 (100%) |
| **OECD Reports** | 2 | 193 | 0 (0%) | 2 (100%) |
| **Other Jurisdictions** | 10 | 903 | 0 (0%) | 10 (100%) |
| **TOTAL** | **116** | **~10,212** | **12 (10%)** | **104 (90%)** |

### Current vs. Required Coverage

**Current Status (Before This Session):**
- Documents: 12 detailed mappings
- Fields: ~1,403 fields
- Coverage: **13.7%** of total scope

**Target Status (After Complete Implementation):**
- Documents: 116 detailed mappings
- Fields: ~10,212 fields
- Coverage: **100%** of comprehensive scope

---

## Implementation Plan

### Phase 1: High Priority (Complete First)
1. All remaining PACS messages (9 messages, ~1,105 fields)
2. All remaining PAIN messages (11 messages, ~1,036 fields)
3. Core CAMT messages (camt.052, .053, .054, .055, .056) (5 messages, ~671 fields)
4. Key SWIFT MT messages (MT202, MT103+, MT192) (3 messages, ~161 fields)
5. Core regulatory reports (FinCEN, AUSTRAC, FATCA/CRS) (15 reports, ~1,500 fields)

**Phase 1 Total:** 43 documents, ~4,473 fields

### Phase 2: Medium Priority
1. Regional payment systems (15 systems, ~1,216 fields)
2. Additional SWIFT MT messages (10 messages, ~450 fields)
3. European regulatory reports (5 reports, ~548 fields)
4. UK regulatory reports (4 reports, ~534 fields)

**Phase 2 Total:** 34 documents, ~2,748 fields

### Phase 3: Complete Coverage
1. Remaining CAMT messages (7 messages, ~665 fields)
2. Remaining SWIFT MT messages (6 messages, ~263 fields)
3. Other jurisdiction reports (10 reports, ~903 fields)
4. Low-priority regional systems (5 systems, ~342 fields)

**Phase 3 Total:** 28 documents, ~2,173 fields

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Weekly
