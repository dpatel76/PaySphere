# Missing Mappings Analysis - GPS CDM Project

**Created:** 2024-12-20
**Purpose:** Identify remaining payment standards and regulatory reports to reach 100+ mapping documents

---

## Current Status

- **Created:** 78 documents (54 standards + 24 reports)
- **Target:** 100+ documents
- **Remaining:** ~25-30 documents minimum

---

## Missing Payment Standards

### ISO 20022 Messages (~15-20 additional messages)

#### ACMT - Account Management Messages (6 messages)
1. **acmt.001** - Account Opening Instruction
2. **acmt.002** - Account Details Confirmation
3. **acmt.003** - Account Modification Instruction
4. **acmt.005** - Account Identification Verification Request
6. **acmt.006** - Account Identification Verification Report
7. **acmt.007** - Account Opening Request

#### REDA - Reference Data Messages (3 messages)
1. **reda.001** - Price Report
2. **reda.002** - Price Report Cancellation
3. **reda.004** - Fund Reference Data Report

#### AUTH - Authorities Messages (4 messages)
1. **auth.026** - Derivatives Contract Report (MiFIR)
2. **auth.027** - Financial Instrument Reporting Reference Data
3. **auth.030** - Payment Regulatory Report (ISO 20022 Payments Statistics)
4. **auth.036** - Market Data Report

#### ADMI - Administration Messages (3 messages)
1. **admi.002** - Message Reject
2. **admi.004** - System Event Notification
3. **admi.007** - Receipt Acknowledgement

#### Additional CAMT Messages (5 messages)
1. **camt.026** - Unable to Apply
2. **camt.027** - Claim Non Receipt
3. **camt.028** - Additional Payment Information
4. **camt.029** - Resolution of Investigation
5. **camt.050** - Liquidity Credit Transfer

### SWIFT MT Messages (~8 additional messages)

#### Category 2 - Financial Institution Transfers
1. **MT210** - Notice to Receive
2. **MT292** - Request for Cancellation (Category 2)
3. **MT295** - Queries (Category 2)
4. **MT296** - Answers (Category 2)
5. **MT299** - Free Format Message (Category 2)

#### Category 9 - Cash Management & Customer Status
1. **MT900** - Confirmation of Debit
2. **MT910** - Confirmation of Credit
3. **MT940** - Customer Statement Message
4. **MT941** - Balance Report
5. **MT942** - Interim Transaction Report
6. **MT950** - Statement Message (already created)

### Additional Regional/National Payment Systems (~5 systems)

#### United States
1. **FedNow** - Federal Reserve Instant Payment Service
2. **EPN (Electronic Payments Network)** - Debit network

#### Middle East
1. **UAEFTS** - UAE Funds Transfer System
2. **SARIE** - Saudi Arabia RTGS

#### Other APAC
1. **MEPS+** - Singapore RTGS (different from PayNow)
2. **BOJ-NET** - Bank of Japan Network

---

## Missing Regulatory Reports

### United States (5 reports)
1. **OFAC SDN Report** - Specially Designated Nationals blocking report
2. **Form 104** - Currency and Monetary Instrument Report (CMIR)
3. **Form 105** - Report of International Transportation of Currency
4. **FinCEN 110** - Designation of Exempt Person
5. **FinCEN 312** - Special Due Diligence for Correspondent Accounts

### European Union (4 reports)
1. **AML Directive Reports** - EU AML/CFT reporting
2. **AMLD5 Reporting** - 5th Anti-Money Laundering Directive
3. **Transfer of Funds Regulation** - EU TFR Article 15
4. **EBA Fraud Data Report** - Detailed fraud statistics

### United Kingdom (2 reports)
1. **Regulation of Investigatory Powers Act (RIPA)** - Disclosure order
2. **Proceeds of Crime Act (POCA)** - Confiscation order

### Asia-Pacific (3 reports)
1. **JAFIC STR** - Japan Suspicious Transaction Report
2. **MAS STR** - Singapore Suspicious Transaction Report
3. **HKMA STR** - Hong Kong Suspicious Transaction Report

### International/Multi-Jurisdictional (3 reports)
1. **SWIFT KYC Registry** - Data submission
2. **LEI Registration** - Legal Entity Identifier application
3. **Wolfsberg Questionnaire** - AML/CFT due diligence

---

## Recommended Priority List (Next 25 Documents)

### High Priority - Core Payment Messages (12 documents)

**ISO 20022 ACMT** (Account Management - critical for onboarding)
1. acmt.001 - Account Opening Instruction
2. acmt.002 - Account Details Confirmation
3. acmt.003 - Account Modification Instruction
4. acmt.007 - Account Opening Request

**SWIFT MT Category 9** (Cash Management - high volume)
5. MT900 - Confirmation of Debit
6. MT910 - Confirmation of Credit
7. MT940 - Customer Statement
8. MT942 - Interim Transaction Report

**ISO 20022 CAMT Investigation** (Operational - high value)
9. camt.026 - Unable to Apply
10. camt.027 - Claim Non Receipt
11. camt.029 - Resolution of Investigation
12. camt.050 - Liquidity Credit Transfer

### Medium Priority - Regulatory & Compliance (8 documents)

**US Regulatory** (FinCEN/OFAC compliance)
13. OFAC SDN Blocking Report
14. FinCEN Form 104 (CMIR)
15. FinCEN 312 (Correspondent Account Due Diligence)

**EU Regulatory** (AML/CFT)
16. EU Transfer of Funds Regulation Article 15
17. AMLD5 Reporting

**APAC Regulatory** (Regional compliance)
18. MAS STR (Singapore)
19. HKMA STR (Hong Kong)
20. JAFIC STR (Japan)

### Lower Priority - Additional Coverage (5 documents)

**Regional Systems** (Geographic expansion)
21. FedNow (US instant payment)
22. UAEFTS (UAE)
23. MEPS+ (Singapore RTGS)

**ISO 20022 REDA** (Reference data)
24. reda.001 - Price Report
25. reda.004 - Fund Reference Data Report

---

## Total Target Breakdown

| Category | Current | Target | Gap |
|----------|---------|--------|-----|
| **ISO 20022** | 24 | 45 | 21 |
| **SWIFT MT** | 10 | 18 | 8 |
| **Regional Systems** | 18 | 23 | 5 |
| **US Regulatory** | 6 | 11 | 5 |
| **EU Regulatory** | 6 | 10 | 4 |
| **APAC Regulatory** | 0 | 3 | 3 |
| **Other Reports** | 5 | 8 | 3 |
| **TOTAL** | **78** | **118** | **40** |

---

## Execution Plan

### Phase 1: High Priority (12 documents)
- Launch 3 parallel agents
- Agent 1: ISO 20022 ACMT (4 messages)
- Agent 2: SWIFT MT Category 9 (4 messages)
- Agent 3: ISO 20022 CAMT Investigation (4 messages)

### Phase 2: Medium Priority (8 documents)
- Launch 2 parallel agents
- Agent 1: US Regulatory (3 reports)
- Agent 2: EU & APAC Regulatory (5 reports)

### Phase 3: Lower Priority (5 documents)
- Launch 1 agent for remaining coverage

**Total Additional Documents:** 25 minimum to reach 103 total

---

**Recommendation:** Proceed with Phase 1 immediately to add critical account management, cash management, and investigation messages.
