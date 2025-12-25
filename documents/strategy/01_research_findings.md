# RESEARCH FINDINGS
## Bank of America Global Payments Data Strategy

**Document Version:** 1.0
**Date:** December 18, 2025
**Classification:** Internal Strategy Document

---

## TABLE OF CONTENTS

1. [Research Block 1: Bank of America Payments Footprint](#research-block-1-bank-of-america-payments-footprint)
2. [Research Block 2: Regulatory Landscape](#research-block-2-regulatory-landscape)
3. [Research Block 3: Message Formats and Data Models](#research-block-3-message-formats-and-data-models)
4. [Peer Analysis](#peer-analysis)

---

## RESEARCH BLOCK 1: BANK OF AMERICA PAYMENTS FOOTPRINT

### 1.1 Geographic Presence

Bank of America operates payment services globally with the following footprint:

#### **Americas**
- **United States**: Full suite of payment products including domestic and international payments
- **Mexico**: On-the-ground presence through local entities
- **Brazil**: On-the-ground presence with support for local payment systems including PIX
- **Canada**: Payment services through correspondent banking

#### **Europe, Middle East, and Africa (EMEA)**
- **Coverage**: 21 countries across EMEA region
- **Key Markets**: United Kingdom, Germany, France, Italy, Spain, Netherlands, Switzerland, Ireland
- **License Type**: Branch operations and subsidiary structures depending on jurisdiction
- **Local Clearing Systems**:
  - TARGET2 (Eurozone)
  - CHAPS (UK)
  - BACS (UK)
  - SEPA (EU/EEA)

#### **Asia-Pacific (APAC)**
- **Coverage**: 12 markets across Asia
- **Key Markets**: Singapore, Hong Kong, Japan, Australia, India, China
- **License Type**: Branch operations, representative offices, and local subsidiaries
- **Local Clearing Systems**:
  - MEPS+ (Singapore)
  - CHATS/HKD RTGS (Hong Kong)
  - BOJ-NET (Japan)
  - RITS (Australia)
  - NEFT/RTGS (India)
  - CIPS (China cross-border)

### 1.2 Data Residency Requirements by Region

#### **United States**
- **Requirements**: Data can be stored domestically; certain data types require US-based processing
- **Regulations**: Bank Secrecy Act, Federal Reserve regulations
- **Cloud Considerations**: Approved for compute-only cloud usage

#### **European Union/EEA**
- **Requirements**: GDPR mandates for personal data; some member states have additional restrictions
- **Regulations**: GDPR, PSD2/PSD3, DORA, national banking regulations
- **Special Considerations**: Schrems II ruling impacts US cloud provider usage

#### **United Kingdom**
- **Requirements**: Post-Brexit UK GDPR; data adequacy agreements with EU
- **Regulations**: UK GDPR, FCA regulations, Payment Services Regulations
- **Cloud Considerations**: More flexible than EU but must align with FCA operational resilience

#### **Singapore**
- **Requirements**: MAS Technology Risk Management guidelines
- **Regulations**: Payment Services Act, MAS outsourcing notices
- **Cloud Considerations**: Must notify MAS of material cloud arrangements

#### **Hong Kong**
- **Requirements**: HKMA data protection and outsourcing requirements
- **Regulations**: PSSVFO, personal data privacy ordinance
- **Cloud Considerations**: HKMA prior notification for material outsourcing

#### **Australia**
- **Requirements**: APRA CPS 231 outsourcing standards
- **Regulations**: Privacy Act, APRA prudential standards
- **Cloud Considerations**: Must maintain ability to access and retrieve data

#### **China**
- **Requirements**: Data localization for personal information and important data
- **Regulations**: Personal Information Protection Law (PIPL), Cybersecurity Law
- **Cloud Considerations**: Restricted to domestic cloud providers or approved foreign providers

### 1.3 Payment Products Inventory

#### **Domestic US Products**

| Product | Type | Volume (Est.) | Systems | Regulatory Framework |
|---------|------|---------------|---------|---------------------|
| ACH (NACHA) | Batch | High | CashPro, core banking | NACHA Operating Rules, Reg E |
| Fedwire | Real-time | Medium | Federal Reserve connection | Reg J |
| CHIPS | Real-time | Medium | CHIPS network | CHIPS Rules |
| Zelle | Real-time P2P | Growing | Zelle network | Reg E |
| RTP (Real-Time Payments) | Real-time | Growing | The Clearing House RTP | RTP Rules |
| FedNow | Real-time | New/Growing | Federal Reserve FedNow | FedNow Rules |
| Check/Image | Batch | Declining | Image exchange | Reg CC, UCC |

#### **International Products**

| Product | Type | Geographic Scope | Systems | Standards |
|---------|------|------------------|---------|-----------|
| SWIFT MT | Batch/Real-time | Global | SWIFT network | MT103, MT202, MT940, etc. |
| SWIFT MX (ISO 20022) | Batch/Real-time | Global | SWIFT network | pacs.008, pacs.009, camt.053, etc. |
| Cross-border Wires | Real-time | Global | SWIFT, correspondent banking | Various by destination |
| Correspondent Banking | Various | Global | Nostro/Vostro accounts | Basel Committee, FATF |

#### **Regional Products**

| Product | Type | Geographic Scope | Systems | Standards |
|---------|------|------------------|---------|-----------|
| SEPA Credit Transfer (SCT) | Batch | EU/EEA | SEPA infrastructure | ISO 20022 pain/pacs messages |
| SEPA Instant Credit Transfer | Real-time | EU/EEA | SEPA Instant infrastructure | ISO 20022 |
| SEPA Direct Debit (SDD) | Batch | EU/EEA | SEPA infrastructure | ISO 20022 |
| BACS | Batch | UK | Bacs Payment Schemes | Bacs Standard 18 |
| Faster Payments | Real-time | UK | Faster Payments Service | ISO 8583 (future ISO 20022) |
| TARGET2 | Real-time | Eurozone | ECB TARGET2 | Proprietary/migrating to ISO 20022 |
| CHAPS | Real-time | UK | Bank of England RTGS | ISO 20022 |
| PIX | Real-time | Brazil | Brazilian Central Bank | ISO 20022 |
| CIPS | Real-time | China cross-border | PBOC CIPS | ISO 20022 |

#### **Commercial Banking Products (CashPro)**

- **Payment Initiation**: Support for 350+ payment types across 38 markets
- **Real-time Payment Schemes**: 7 schemes including Zelle (US) and PIX (Brazil)
- **Virtual Accounts**: Liquidity management and account reconciliation
- **Notional Pooling**: Cross-border cash concentration
- **Payment APIs**: CashPro Payment API for integration
- **Liquidity Management**: Real-time visibility and forecasting
- **Trade Finance**: Letters of credit, guarantees
- **Foreign Exchange**: FX payments and hedging

#### **Emerging Payment Types**

- **Request to Pay**: ISO 20022 pain.013/pain.014 messages (emerging in EU/UK)
- **Open Banking Payments**: PSD2-enabled account-to-account payments
- **Embedded Payments**: API-driven payments within third-party applications
- **Digital Currency**: Exploration phase for wholesale CBDC (e.g., regulated liability network POC)

### 1.4 Transaction Volumes and Performance Metrics

#### **Key Performance Indicators (2024)**
- **CashPro Transaction Volume**: $1+ trillion (25% YoY growth)
- **Daily Transaction Volume**: Tens of millions of records
- **Latency Requirements**:
  - Fraud detection: <100 milliseconds
  - Real-time payment processing: <1 second
  - Batch processing: Within defined windows (typically EOD)
- **Geographic Coverage**: 38 markets via CashPro platform

---

## RESEARCH BLOCK 2: REGULATORY LANDSCAPE

### 2.1 United States Regulations

#### **2.1.1 Bank Secrecy Act (BSA) / Anti-Money Laundering (AML)**

**Regulatory Body**: Financial Crimes Enforcement Network (FinCEN), U.S. Treasury

**Applicable Payment Types**: All payment types

**Reporting Requirements**:

| Report Type | Trigger | Frequency | Submission Method | Data Elements Required |
|-------------|---------|-----------|-------------------|------------------------|
| Currency Transaction Report (CTR) | Cash transactions >$10,000 (daily aggregate) | Per occurrence | BSA E-Filing System | Customer identity, transaction amount, date, account numbers, business conducting transaction |
| Suspicious Activity Report (SAR) | Suspicious transactions ≥$5,000 | Within 30 days of detection | BSA E-Filing System | Narrative description, involved parties, accounts, transaction details, reason for suspicion |
| Currency and Monetary Instrument Report (CMIR) | International transport of currency/monetary instruments >$10,000 | Per occurrence | BSA E-Filing System | Traveler/shipper info, recipient info, amount, currency, origin/destination |

**Data Element Requirements**:
- Customer identification (name, TIN/SSN/EIN, address, date of birth)
- Transaction amount and currency
- Transaction date and time
- Account numbers (origin and destination)
- Conducting person/entity
- Purpose of transaction
- Beneficial ownership information (for legal entities)

**Retention Requirements**: 5 years from filing date

#### **2.1.2 Office of Foreign Assets Control (OFAC) Sanctions Screening**

**Regulatory Body**: U.S. Treasury OFAC

**Applicable Payment Types**: All payment types, particularly international

**Requirements**:
- Real-time screening of all parties against SDN (Specially Designated Nationals) list
- Screening against other OFAC sanctions lists (country-based, sectoral)
- Blocking of transactions involving sanctioned parties
- Reporting of blocked transactions to OFAC within 10 days

**Data Elements Required**:
- Name and aliases of all transaction parties
- Addresses of all transaction parties
- Identification numbers (passport, national ID, tax ID, etc.)
- Date of birth
- Country of citizenship/incorporation
- BIC/SWIFT codes
- Account numbers
- Transaction amount and currency
- Transaction purpose and description

**Integration Points**: Must be applied to ACH, wires, SWIFT, and all cross-border transactions

#### **2.1.3 Federal Reserve Regulation E (Electronic Fund Transfers)**

**Regulatory Body**: Federal Reserve Board / Consumer Financial Protection Bureau (CFPB)

**Applicable Payment Types**: Consumer electronic fund transfers (ATM, POS, ACH, online banking, mobile payments, P2P)

**Requirements**:
- Error resolution procedures (consumer reports error within 60 days)
- Periodic statements (monthly if EFT occurred)
- Initial disclosures of terms and conditions
- Provisional credit within 10 business days of error claim
- Error investigation completion within 45 days (90 days for new accounts/international)

**Data Elements Required for Statements**:
- Transaction amount
- Transaction date
- Transaction type/description
- Payee identification (if available)
- Account balance
- Fee information

#### **2.1.4 Federal Reserve Regulation CC (Funds Availability)**

**Regulatory Body**: Federal Reserve Board

**Applicable Payment Types**: Check deposits, ACH, wire transfers

**Requirements**:
- Next business day availability for electronic payments, wire transfers, and first $225 of daily deposits
- Specific schedules for local/nonlocal check availability
- Exception holds disclosure requirements
- Large deposit holds (>$5,525 per day)

**Data Elements Required**:
- Deposit amount
- Deposit date/time
- Check amount (if applicable)
- Account number
- Hold amount and reason
- Availability date

#### **2.1.5 Federal Reserve Regulation J (Check Collection and Funds Transfers)**

**Regulatory Body**: Federal Reserve Board

**Applicable Payment Types**: Fedwire funds transfers, check collection through Federal Reserve Banks

**Requirements**:
- Proper authorization and authentication
- Security procedures
- Error and adjustment procedures
- Same-day settlement for Fedwire
- Liability allocation rules

**Data Elements Required**:
- Sender identification
- Receiver identification
- Beneficiary information
- Amount and currency
- Purpose/remittance information
- Related reference numbers

#### **2.1.6 NACHA Operating Rules (ACH)**

**Regulatory Body**: NACHA (The Electronic Payments Association)

**Applicable Payment Types**: All ACH transactions (credit, debit, returns, NOCs)

**Requirements**:
- Standard Entry Class (SEC) code usage
- Authorization requirements by entry type
- Return timeframes (2 business days for most, 60 days for unauthorized)
- Settlement schedules
- Data security requirements (PCI-DSS alignment)
- Same Day ACH rules (amount limits, deadlines)

**Data Elements Required** (per NACHA file format):
- File Header: immediate destination, immediate origin, file ID, record size
- Batch Header: company name, company ID, SEC code, entry description, effective date
- Entry Detail: transaction code, receiving DFI, account number, amount, individual ID, individual name, addenda indicator
- Addenda: payment related information (if applicable)
- Batch/File Control: entry count, hash, debit/credit totals

**Retention**: 6 years for ACH entries and authorizations

#### **2.1.7 Dodd-Frank Act Reporting**

**Regulatory Body**: Multiple (CFTC, SEC, Federal Reserve, OCC, FDIC)

**Applicable Payment Types**: Derivatives transactions, swap reporting, systemic risk monitoring

**Requirements**:
- Swap data reporting to registered swap data repositories
- Real-time reporting of swap transactions
- Reporting of positions, trading volumes
- Counterparty information
- Margin and collateral reporting

**Data Elements Required**:
- Counterparty identification (LEI required)
- Transaction identification (UTI - Unique Transaction Identifier)
- Valuation data
- Position data
- Product information

#### **2.1.8 FFIEC (Federal Financial Institutions Examination Council)**

**Regulatory Body**: FFIEC (interagency body of federal financial regulators)

**Applicable Payment Types**: All payment types (focus on IT, cybersecurity, and operational risk)

**Requirements**:
- IT examination handbook compliance
- Cybersecurity Assessment Tool (CAT) implementation
- Business continuity and disaster recovery
- Vendor management
- Authentication standards

#### **2.1.9 Tax Reporting (Forms 1099, 1042)**

**Regulatory Body**: Internal Revenue Service (IRS)

**Applicable Payment Types**: Payment transactions triggering tax reporting (interest, dividends, merchant payments, international payments)

**Requirements**:
- Form 1099-MISC: Payments to non-employees ≥$600
- Form 1099-K: Payment card and third-party network transactions (aggregate >$600)
- Form 1042: Withholding on payments to foreign persons
- Form 1042-S: Foreign person's U.S. source income

**Data Elements Required**:
- Payer TIN (Taxpayer Identification Number)
- Payee TIN (or foreign equivalent)
- Payment amount
- Payment type/category
- Withholding amount (if applicable)
- Country code (for international)

#### **2.1.10 FATCA (Foreign Account Tax Compliance Act)**

**Regulatory Body**: IRS

**Applicable Payment Types**: International payments, accounts held by foreign entities

**Requirements**:
- Identification of foreign financial accounts held by US persons
- Reporting of account balances and income
- Withholding on payments to non-compliant foreign institutions
- Form 8966 filing for FATCA reporting

**Data Elements Required**:
- Account holder name and TIN
- Account number
- Account balance/value
- Income paid (interest, dividends, gross proceeds)
- Withholding amount
- Foreign institution identification

#### **2.1.11 FedNow and RTP Network Requirements**

**Regulatory Body**: Federal Reserve (FedNow), The Clearing House (RTP)

**Applicable Payment Types**: Real-time payments

**Requirements**:
- 24/7/365 availability
- Settlement in seconds
- Irrevocable payments
- ISO 20022 message standards (for FedNow)
- Fraud prevention controls
- Request for Payment support
- Maximum transaction limits ($500,000 for RTP, $500,000 for FedNow as of 2024)

**Data Elements Required**:
- ISO 20022 compliant message structure
- Enhanced remittance information (up to 140 characters for RTP)
- Purpose codes
- Beneficiary information
- End-to-end transaction ID

### 2.2 European Union / EEA Regulations

#### **2.2.1 PSD2 (Payment Services Directive 2) and PSD3 (Upcoming)**

**Regulatory Body**: European Commission, national competent authorities (e.g., BaFin, FCA, ACPR)

**Applicable Payment Types**: All payment services including credit transfers, direct debits, card payments, e-money, payment initiation services, account information services

**Current PSD2 Requirements**:
- Strong Customer Authentication (SCA) for electronic payments
- Open Banking - API access for licensed TPPs (Third Party Providers)
- Standardized API performance requirements
- Reporting to national competent authorities
- Transaction and fraud reporting
- Enhanced consumer protection

**PSD3 Changes (Expected 2026-2027)**:
- Expanded scope: instant payments, BNPL, cryptocurrency platforms
- Confirmation of Payee (CoP) for all SEPA credit transfers
- Stricter ICT/security resilience aligned with DORA
- Enhanced fraud data-sharing requirements
- Wind-down planning for payment service providers
- Open Banking API standardization and performance SLAs

**Data Elements Required**:
- Payment initiation: debtor/creditor identification, IBAN, amount, currency, purpose, timestamp
- Authentication data: device ID, location, behavioral biometrics
- Fraud reporting: transaction details, fraud type, loss amount, detection method
- API access logs: TPP identity, timestamp, data accessed, consent details

**Reporting Frequency**:
- Transaction reporting: Real-time to immediate
- Fraud reporting: Quarterly to national authority
- Incident reporting: Without undue delay (typically within 24-72 hours)

**Retention**: Varies by member state, typically 5-10 years

#### **2.2.2 GDPR (General Data Protection Regulation)**

**Regulatory Body**: European Data Protection Board, national data protection authorities

**Applicable Payment Types**: All payments involving personal data

**Requirements**:
- Lawful basis for processing personal data
- Data minimization and purpose limitation
- Right to access, rectification, erasure, data portability
- Data Protection Impact Assessments for high-risk processing
- Data breach notification (within 72 hours to authority)
- Privacy by design and by default
- Appropriate technical and organizational measures for security

**Data Elements (Payments Context)**:
- Payment data is considered personal data when linked to identifiable person
- Enhanced protection for sensitive payment data
- Consent requirements for non-essential processing
- Cross-border transfer restrictions (adequacy decisions, SCCs, BCRs)

**Retention**: Must not exceed necessary period (payment data typically 5-7 years for regulatory compliance)

**Penalties**: Up to €20 million or 4% of global annual revenue

#### **2.2.3 DORA (Digital Operational Resilience Act)**

**Regulatory Body**: European Supervisory Authorities (EBA, ESMA, EIOPA)

**Applicable Payment Types**: All payment services (applies to all financial entities)

**Effective Date**: January 17, 2025

**Requirements**:
- ICT risk management framework
- Incident reporting (classification, reporting timelines)
- Digital operational resilience testing (including TLPT - Threat-Led Penetration Testing)
- ICT third-party risk management
- Critical ICT third-party provider oversight
- Information sharing on cyber threats

**Data Elements for Incident Reporting**:
- Incident classification (type, severity)
- Timestamp and duration
- Affected systems and services
- Impact on operations
- Root cause analysis
- Recovery actions
- Lessons learned

**Reporting Timeline**:
- Initial notification: As soon as possible, at the latest 4 hours after classification
- Intermediate report: Within 72 hours
- Final report: Within 1 month

**Integration with PSD3**: PSD3 aligns ICT requirements with DORA

#### **2.2.4 AML Directives (AMLD5, AMLD6)**

**Regulatory Body**: European Commission, national FIUs (Financial Intelligence Units)

**Applicable Payment Types**: All payment types, especially cross-border and high-risk

**Requirements (AMLD5)**:
- Enhanced due diligence for high-risk third countries
- Beneficial ownership registers
- Cryptocurrency exchange and wallet provider coverage
- Prepaid card limits (€150 anonymous, €250 with minimal identification)
- Access to beneficial ownership information

**Requirements (AMLD6)** - Strengthens AMLD5:
- Expanded list of predicate offenses (22 categories)
- Liability for legal persons
- Enhanced penalties (minimum 1-5 years imprisonment, fines up to €5 million or 10% of turnover)
- Enhanced cooperation between FIUs and third countries

**Data Elements Required**:
- Customer due diligence (CDD) information
- Beneficial ownership (at least 25% ownership or control)
- Source of funds and wealth
- Purpose and nature of business relationship
- Transaction monitoring data
- Suspicious transaction reports (STRs)

**Reporting**: STRs filed with national FIU without undue delay

#### **2.2.5 SEPA Regulation and Rulebooks**

**Regulatory Body**: European Payments Council (EPC), European Central Bank

**Applicable Payment Types**: SEPA Credit Transfers, SEPA Instant Credit Transfers, SEPA Direct Debits

**Requirements**:
- ISO 20022 XML message standards
- IBAN and BIC usage
- Euro currency
- Reachability across SEPA zone (36 countries)
- Maximum execution time (SCT: D+1, SCT Inst: <10 seconds)
- Maximum amount for SCT Inst (€100,000 as of 2024)
- Refund rights for direct debits (8 weeks authorized, 13 months unauthorized)

**Data Elements Required**:
- Message elements per SEPA scheme rulebooks
- Debtor/Creditor name and IBAN
- Remittance information (140 characters unstructured)
- Purpose code (optional but recommended)
- Creditor identifier (for SDD)
- Mandate reference (for SDD)
- End-to-end identification

**Reporting**: Scheme adherence reporting to EPC

**Future (Post-October 2025)**:
- Mandatory support for SEPA Instant payments
- Verification of Payee (CoP) mandatory

#### **2.2.6 EMIR (European Market Infrastructure Regulation)**

**Regulatory Body**: ESMA (European Securities and Markets Authority)

**Applicable Payment Types**: Derivatives transactions, OTC derivatives clearing and reporting

**Requirements**:
- Reporting of derivative contracts to trade repositories
- Central clearing for standardized OTC derivatives
- Risk mitigation for non-cleared derivatives
- Position limits for commodity derivatives

**Data Elements Required**:
- Counterparty data (LEI mandatory)
- Unique Transaction Identifier (UTI)
- Contract details (notional amount, currency, maturity, underlying)
- Valuation
- Collateral information
- Lifecycle events

#### **2.2.7 SFTR (Securities Financing Transactions Regulation)**

**Regulatory Body**: ESMA

**Applicable Payment Types**: Securities financing transactions (SFTs) - repos, securities lending, margin lending

**Requirements**:
- Reporting of SFTs to trade repositories
- Reporting of collateral reuse
- Transparency requirements

**Data Elements Required**:
- Counterparty identification (LEI)
- Transaction identification (UTI)
- Transaction details
- Collateral information
- Margin data
- Reuse information

### 2.3 United Kingdom Regulations

#### **2.3.1 UK Payment Services Regulations (PSRs)**

**Regulatory Body**: Financial Conduct Authority (FCA)

**Applicable Payment Types**: All payment services (mirrors PSD2 with UK-specific modifications)

**Requirements**:
- Strong Customer Authentication (SCA)
- Open Banking (CMA9 banks)
- Authorization and execution of payment transactions
- Safeguarding of customer funds
- Reporting to FCA

**Data Elements**: Similar to PSD2 (see section 2.2.1)

**Post-Brexit Divergence**:
- UK government developing separate payment services framework
- Greater FCA rulemaking powers
- Potential divergence from EU PSD3

#### **2.3.2 UK FCA Payment Systems and Services Requirements**

**Regulatory Body**: FCA, Payment Systems Regulator (PSR)

**Applicable Payment Types**: All UK payment systems (Faster Payments, BACS, CHAPS, LINK)

**Requirements**:
- Operational resilience (important business services must remain within impact tolerances)
- Incident reporting to FCA
- Authorized Push Payment (APP) fraud reimbursement (50/50 split between sending/receiving banks as of Oct 2024)
- Consumer protection
- Access to payment systems

**Data Elements for Incident Reporting**:
- Incident description and classification
- Affected systems/services
- Number of customers affected
- Duration
- Root cause (when known)
- Remediation actions

**APP Fraud Reimbursement Data**:
- Transaction details
- Fraud evidence
- Customer due diligence
- Warning provided to customer
- Gross negligence assessment

#### **2.3.3 Bank of England RTGS Requirements**

**Regulatory Body**: Bank of England

**Applicable Payment Types**: CHAPS (high-value payments), settlement for Faster Payments and BACS

**Requirements**:
- ISO 20022 messaging (completed migration 2024)
- Liquidity management
- Operating hours (extended to 20 hours per day in CHAPS renewal program)
- Resilience and business continuity
- SWIFT network connectivity

**Data Elements**: ISO 20022 pacs.008, pacs.009, pacs.004, camt.056 messages

#### **2.3.4 UK GDPR**

**Regulatory Body**: Information Commissioner's Office (ICO)

**Applicable Payment Types**: All payments involving personal data

**Requirements**: Largely mirrors EU GDPR with UK-specific guidance and adequacy arrangements post-Brexit

**Data Elements and Requirements**: Same as EU GDPR (see section 2.2.2)

### 2.4 Asia-Pacific Regulations

#### **2.4.1 Singapore - MAS Payment Services Act**

**Regulatory Body**: Monetary Authority of Singapore (MAS)

**Applicable Payment Types**: All payment services (7 categories including account issuance, domestic/cross-border money transfer, e-money, payment initiation, DPT)

**Effective Date**: January 28, 2020 (amended April 4, 2024)

**Requirements**:
- Licensing based on payment service type
- AML/CFT compliance (PSN01)
- Technology Risk Management Guidelines (TRMG)
- Incident reporting (PSN03)
- Cybersecurity requirements
- Outsourcing notification to MAS

**Data Elements for Reporting**:
- Transaction monitoring data
- Suspicious activity reports
- Cybersecurity incident details
- Technology risk assessments
- Outsourcing arrangements

**Retention**: 5 years for transaction records

#### **2.4.2 Hong Kong - HKMA Payment Systems Oversight**

**Regulatory Body**: Hong Kong Monetary Authority (HKMA)

**Applicable Payment Types**: All payment systems under PSSVFO (designated retail payment systems - Visa, Mastercard, UnionPay, Amex, JETCO, EPS)

**Requirements**:
- Designation of systemically important payment systems
- Oversight of operational, legal, and financial risks
- Data protection and privacy (Personal Data Privacy Ordinance)
- Outsourcing guidelines
- Business continuity management

**Data Elements**:
- Transaction data for oversight
- Operational performance metrics (availability, processing times)
- Incident reports
- Risk assessment data

#### **2.4.3 Japan - Payment Services Act and BOJ Oversight**

**Regulatory Body**: Financial Services Agency (FSA), Bank of Japan (BOJ)

**Applicable Payment Types**: Electronic money, fund transfers, prepaid payment instruments, virtual currencies

**Requirements**:
- PSA licensing for payment service providers
- Fund safeguarding (customer funds held in trust or guarantee)
- AML/CTF compliance
- Cybersecurity requirements (strengthened in 2021 amendments)
- Small-amount fund transfer regulations
- BOJ oversight of financial market infrastructure

**Data Elements**:
- Customer identification and verification
- Transaction records
- Fund safeguarding evidence
- AML monitoring data
- Cybersecurity assessments

#### **2.4.4 India - RBI Payment System Guidelines**

**Regulatory Body**: Reserve Bank of India (RBI)

**Applicable Payment Types**: All payment systems including NEFT, RTGS, IMPS, UPI, card payments, cross-border payments

**Requirements**:
- Payment aggregator licensing (including cross-border PA-CB)
- Net worth requirements (₹25 crore by March 2026 for non-bank entities)
- KYC requirements for cross-border merchants
- Liberalized Remittance Scheme (LRS) compliance (USD $250,000 annual limit for individuals)
- Data localization (payment data must be stored in India)
- Reporting to RBI

**Data Elements Required**:
- Full KYC: PAN, identity proof, business registration, bank details
- Transaction data (stored in India)
- Cross-border transaction reporting
- Foreign exchange data
- Suspicious transaction reporting

**Data Localization**: All payment system data must be stored in India; foreign storage allowed only for foreign leg of transaction

#### **2.4.5 China - PBOC Payment Regulations and CIPS**

**Regulatory Body**: People's Bank of China (PBOC)

**Applicable Payment Types**: All non-bank payment services, cross-border RMB payments

**Requirements**:
- Payment Services Permit for all PSPs (domestic and foreign providing cross-border services to Chinese users)
- Regulations on Supervision and Administration of Non-Bank Payment Institutions (effective May 1, 2024)
- Payment purpose code for cross-border RMB payments
- CIPS participation for cross-border RMB clearing
- Data security measures aligned with Cybersecurity Law
- Data localization for payment data

**Data Elements**:
- Customer identity verification
- Transaction purpose code
- Payment data (stored in China)
- Cross-border reporting data
- Risk management data

**CIPS Requirements**:
- ISO 20022 messaging
- Direct and indirect participant structure
- Operating hours: 24/5 (extended hours)
- Connectivity to SWIFT network

#### **2.4.6 Australia - APRA Banking Requirements**

**Regulatory Body**: Australian Prudential Regulation Authority (APRA)

**Applicable Payment Types**: All banking and payment services provided by ADIs (Authorized Deposit-taking Institutions)

**Requirements**:
- Minimum capital (AUD $50 million Tier 1 for banks)
- CPS 231 Outsourcing standard
- CPS 234 Information security
- Risk management framework
- Business continuity management
- Data retention and availability
- Incident reporting to APRA

**Data Elements**:
- Transaction records
- Risk assessment data
- Outsourcing arrangements and vendor assessments
- Information security incidents
- Operational resilience metrics

**Data Retention**: Must maintain ability to access and retrieve data even if outsourced

### 2.5 Global and Cross-Border Regulations

#### **2.5.1 SWIFT Compliance Requirements**

**Regulatory Body**: SWIFT (cooperative society), overseen by G-10 central banks

**Applicable Payment Types**: All SWIFT message types (particularly cross-border payments)

**Requirements**:
- Customer Security Programme (CSP) attestation
- Security controls framework (mandatory and advisory controls)
- KYC Security Attestation (KYC-SA)
- Local Market Practice (LMP) compliance
- Sanctions screening integration
- ISO 20022 migration (Nov 2025 deadline for MT sunset)

**Data Elements**:
- ISO 20022 message structure (pacs, pain, camt, etc.)
- LEI for entities where applicable
- Enhanced data for sanctions screening
- BIC directory data

**ISO 20022 Migration Timeline**:
- March 2023: Coexistence period began
- November 2025: End of coexistence; MT messages sunset for cross-border payments

#### **2.5.2 FATF Recommendations**

**Regulatory Body**: Financial Action Task Force (FATF)

**Applicable Payment Types**: All payment types globally

**Requirements** (40 Recommendations):
- Risk-based approach to AML/CFT
- Customer due diligence (CDD) and enhanced due diligence (EDD)
- Politically exposed persons (PEP) identification
- Correspondent banking due diligence
- Wire transfer information (Recommendation 16 - "Travel Rule")
- Suspicious transaction reporting
- Targeted financial sanctions
- Virtual asset service providers regulation

**Recommendation 16 (Travel Rule)**:
- Originator information: name, account number, address/national identity/customer ID/date and place of birth
- Beneficiary information: name, account number
- Threshold: Applicable to wire transfers ≥USD/EUR 1,000

**Data Elements for Correspondent Banking**:
- Nature of respondent's business
- Management and ownership structure
- AML/CFT controls
- Regulatory oversight
- Purpose of account
- Identity of respondent's customers with direct access

#### **2.5.3 Basel III/IV - Operational Risk**

**Regulatory Body**: Basel Committee on Banking Supervision (BCBS)

**Applicable Payment Types**: All banking operations including payments (for operational risk capital)

**Requirements**:
- Operational risk capital calculation (Standardized Approach)
- Business Indicator Component (BIC) based on size
- Internal Loss Multiplier (ILM) based on historical losses
- Operational risk management framework
- Scenario analysis and stress testing
- Key Risk Indicators (KRIs) monitoring

**Data Elements for Operational Risk**:
- Loss event data (amount, date, event type, business line)
- Near-miss events
- External loss data
- Business environment and internal control factors (BEICFs)
- Scenario analysis outputs
- KRI measurements

**Event Type Classification**:
- Internal fraud
- External fraud
- Employment practices and workplace safety
- Clients, products, and business practices
- Damage to physical assets
- Business disruption and system failures
- Execution, delivery, and process management

#### **2.5.4 Correspondent Banking Due Diligence**

**Regulatory Bodies**: Basel Committee, FATF, national regulators

**Applicable Payment Types**: All correspondent banking relationships

**Requirements**:
- Know Your Customer's Customer (KYCC) not required per FATF/BCBS but enhanced due diligence on respondent bank mandatory
- Assessment of respondent's AML/CFT controls
- Understanding of respondent's business
- Approval by senior management
- Documentation of AML/CFT responsibilities
- Ongoing monitoring

**Data Elements for Due Diligence**:
- Respondent bank information: ownership, management, license, supervision
- Geographic locations served
- Products and services offered
- Customer base characteristics
- AML/CFT program assessment
- Regulatory actions or adverse information
- Payable-through account and nested relationship identification

**Ongoing Monitoring**:
- Transaction pattern analysis
- Periodic reviews (annual or more frequent based on risk)
- Sanctions and adverse media screening
- Regulatory change monitoring

---

## RESEARCH BLOCK 3: MESSAGE FORMATS AND DATA MODELS

### 3.1 ISO 20022 Standard

#### **3.1.1 Overview**

ISO 20022 is an international standard for electronic data interchange between financial institutions. It uses XML-based messaging and provides a common platform for the development of messages using:
- A modeling methodology
- A central dictionary of business items
- A set of XML design rules

#### **3.1.2 Message Categories**

**PACS (Payment Clearing and Settlement)**
Used between financial institutions for clearing and settlement.

| Message | Name | Usage |
|---------|------|-------|
| pacs.002 | Payment Status Report | Status of payment instruction |
| pacs.003 | FI to FI Customer Direct Debit | Direct debit between FIs |
| pacs.004 | Payment Return | Return of funds |
| pacs.007 | FI to FI Payment Reversal | Reversal request |
| pacs.008 | FI to FI Customer Credit Transfer | Customer credit transfer (replaces MT103) |
| pacs.009 | Financial Institution Credit Transfer | FI to FI transfer (replaces MT202) |
| pacs.010 | Financial Institution Direct Debit | FI direct debit |
| pacs.028 | FI to FI Payment Status Request | Request payment status |

**PAIN (Payment Initiation)**
Used by non-financial institutions (customers/corporates) to initiate payments.

| Message | Name | Usage |
|---------|------|-------|
| pain.001 | Customer Credit Transfer Initiation | Initiate credit transfer |
| pain.002 | Customer Payment Status Report | Status report to customer |
| pain.007 | Customer Payment Reversal | Reversal request from customer |
| pain.008 | Customer Direct Debit Initiation | Initiate direct debit |
| pain.009 | Mandate Initiation Request | Set up direct debit mandate |
| pain.010 | Mandate Amendment Request | Amend mandate |
| pain.011 | Mandate Cancellation Request | Cancel mandate |
| pain.012 | Mandate Acceptance Report | Confirm mandate acceptance |
| pain.013 | Creditor Payment Activation Request | Request to Pay initiation |
| pain.014 | Creditor Payment Activation Request Status Report | Request to Pay status |

**CAMT (Cash Management)**
Used for account reporting and cash management services.

| Message | Name | Usage |
|---------|------|-------|
| camt.052 | Bank to Customer Account Report | Intraday account statement (replaces MT942) |
| camt.053 | Bank to Customer Statement | Account statement (replaces MT940) |
| camt.054 | Bank to Customer Debit/Credit Notification | Debit/credit advice |
| camt.055 | Customer Payment Cancellation Request | Cancellation request |
| camt.056 | FI to FI Payment Cancellation Request | Cancellation request between FIs |
| camt.057 | Notification to Receive | Notification of incoming payment |
| camt.058 | Notification to Receive Cancellation Advice | Cancel notification |
| camt.059 | Payment Cancellation Request Response | Response to cancellation |
| camt.060 | Account Reporting Request | Request statement |

**ACMT (Account Management)**
Used for account opening, maintenance, and closure.

| Message | Name | Usage |
|---------|------|-------|
| acmt.001 | Account Opening Instruction | Open new account |
| acmt.002 | Account Details Confirmation | Confirm account details |
| acmt.003 | Account Modification Instruction | Modify account |
| acmt.005 | Request for Account Management Status Report | Status request |
| acmt.006 | Account Management Status Report | Status report |
| acmt.007 | Account Opening Amendment Request | Amend opening request |
| acmt.011 | Account Request Acknowledgement | Acknowledge request |
| acmt.013 | Account Request Rejection | Reject account request |
| acmt.014 | Account Excluded Mandate Maintenance Request | Maintain mandate |
| acmt.022 | Identification Modification Advice | Modify identification |
| acmt.023 | Identification Verification Request | Verify identification |
| acmt.024 | Identification Verification Report | Report verification |
| acmt.027 | Account Switch Information Request | Request switch info |

**REDA (Reference Data)**
Used for reference data exchange (standing data, counterparty info, etc.).

| Message | Name | Usage |
|---------|------|-------|
| reda.001 | Price Report | Price information |
| reda.002 | Price Report Cancellation | Cancel price report |
| reda.004 | Fund Processing Passport Report | Fund processing info |
| reda.005 | Fund Processing Passport Cancellation | Cancel passport |
| reda.006 | Standing Settlement Instruction | SSI information |
| reda.007 | Standing Settlement Instruction Deletion | Delete SSI |
| reda.014 | Party Activity Advice | Party reference data |
| reda.017 | Security Creation/Update Notification | Security reference data |
| reda.041 | Counterparty Master Data | Counterparty information |
| reda.056 | Party Reference Data | Party information |
| reda.057 | Account Identification | Account reference data |

#### **3.1.3 ISO 20022 Data Dictionary Elements (Key Components)**

**Party Identification**:
- Name (structured and unstructured)
- Postal address (structured per ISO 20022 - country, town, street, building number)
- Identification schemes: BIC, LEI, proprietary
- Contact details

**Account Identification**:
- IBAN
- Other account number formats (BBAN, Wallet ID, etc.)
- Account name
- Currency

**Amount and Currency**:
- Instructed amount
- Interbank settlement amount
- Transaction currency code (ISO 4217)
- Exchange rate

**Dates and Times**:
- Interbank settlement date
- Value date
- Acceptance date and time
- ISO 8601 format

**Purpose and Remittance Information**:
- Purpose code (ISO external code list)
- Category purpose
- Remittance information (structured and unstructured)
- Related references

**Charges and Fees**:
- Charge bearer (DEBT, CRED, SHAR, SLEV)
- Charge type
- Charge amount and currency

**Regulatory Reporting**:
- Regulatory reporting codes
- Country of transaction
- Balance of payments code
- Reporting jurisdiction

### 3.2 Legacy SWIFT MT Messages

#### **3.2.1 MT Message Categories**

**Customer Payments (Category 1)**

| MT Type | Name | ISO 20022 Equivalent |
|---------|------|---------------------|
| MT103 | Single Customer Credit Transfer | pacs.008 |
| MT103+ | Single Customer Credit Transfer (STP) | pacs.008 |
| MT103 REMIT | Single Customer Credit Transfer with Remittance Info | pacs.008 |

**Financial Institution Transfers (Category 2)**

| MT Type | Name | ISO 20022 Equivalent |
|---------|------|---------------------|
| MT200 | Financial Institution Transfer for Own Account | pacs.009 |
| MT202 | General Financial Institution Transfer | pacs.009 |
| MT202COV | General FI Transfer (cover for MT103) | pacs.009 with service level COV |
| MT205 | Financial Markets Transfer | pacs.009 |
| MT210 | Notice to Receive | camt.057 |

**Cash Management (Category 9)**

| MT Type | Name | ISO 20022 Equivalent |
|---------|------|---------------------|
| MT900 | Confirmation of Debit | camt.054 |
| MT910 | Confirmation of Credit | camt.054 |
| MT940 | Customer Statement Message | camt.053 |
| MT942 | Interim Transaction Report | camt.052 |
| MT950 | Statement Message | camt.053 |

#### **3.2.2 MT to MX Migration Considerations**

**Data Enrichment Required**:
- MT messages have field length limitations that MX overcomes
- Structured address data in MX vs. unstructured in MT
- Enhanced remittance information (9,000 characters in MX vs. 140 in MT)
- Additional regulatory reporting fields in MX
- LEI adoption for party identification

**Coexistence Period**:
- March 2023 - November 2025: Coexistence of MT and MX
- November 2025: MT sunset for cross-border payments and cash management
- Translation services available during coexistence

**Truncation Risks in MT**:
- Remittance information truncated when converting MX→MT
- Address information loss
- Purpose codes may not map directly
- Market practice variations

### 3.3 Regional and Domestic Standards

#### **3.3.1 NACHA ACH File Format**

**Structure**: Fixed-width ASCII file, 94 characters per line

**Record Types**:

1. **File Header (Type 1)**:
   - Record Type Code: 1
   - Immediate Destination: 10 digits (routing number)
   - Immediate Origin: 10 digits (routing number)
   - File Creation Date: YYMMDD
   - File Creation Time: HHMM
   - File ID Modifier: A-Z, 0-9
   - Record Size: 094 (fixed)
   - Blocking Factor: 10
   - Format Code: 1
   - Immediate Destination Name: 23 characters
   - Immediate Origin Name: 23 characters

2. **Batch Header (Type 5)**:
   - Record Type Code: 5
   - Service Class Code: 200 (mixed), 220 (credits), 225 (debits)
   - Company Name: 16 characters
   - Company Discretionary Data: 20 characters
   - Company Identification: 10 characters
   - Standard Entry Class (SEC) Code: 3 characters (PPD, CCD, WEB, TEL, CTX, etc.)
   - Company Entry Description: 10 characters
   - Company Descriptive Date: 6 characters
   - Effective Entry Date: YYMMDD
   - Originating DFI Identification: 8 digits

3. **Entry Detail (Type 6)**:
   - Record Type Code: 6
   - Transaction Code: 2 digits (22=checking credit, 27=checking debit, 32=savings credit, 37=savings debit)
   - Receiving DFI Identification: 8 digits (routing number)
   - Check Digit: 1 digit
   - DFI Account Number: 17 characters
   - Amount: 10 digits (in cents)
   - Individual Identification Number: 15 characters
   - Individual Name: 22 characters
   - Discretionary Data: 2 characters
   - Addenda Record Indicator: 0 or 1
   - Trace Number: 15 digits

4. **Addenda (Type 7)**:
   - Record Type Code: 7
   - Addenda Type Code: 05 (most common)
   - Payment Related Information: 80 characters
   - Addenda Sequence Number: 4 digits
   - Entry Detail Sequence Number: 7 digits

5. **Batch Control (Type 8)**:
   - Record Type Code: 8
   - Service Class Code: Must match batch header
   - Entry/Addenda Count: 6 digits
   - Entry Hash: 10 digits (sum of receiving DFI identification numbers)
   - Total Debit Entry Dollar Amount: 12 digits
   - Total Credit Entry Dollar Amount: 12 digits
   - Company Identification: Must match batch header
   - Originating DFI Identification: Must match batch header
   - Batch Number: 7 digits

6. **File Control (Type 9)**:
   - Record Type Code: 9
   - Batch Count: 6 digits
   - Block Count: 6 digits
   - Entry/Addenda Count: 8 digits
   - Entry Hash: 10 digits
   - Total Debit Entry Dollar Amount: 12 digits
   - Total Credit Entry Dollar Amount: 12 digits

**Standard Entry Class (SEC) Codes**:
- PPD: Prearranged Payment and Deposit (consumer)
- CCD: Corporate Credit or Debit
- CTX: Corporate Trade Exchange (with addenda)
- WEB: Internet-initiated entry
- TEL: Telephone-initiated entry
- ARC: Accounts Receivable Conversion
- BOC: Back Office Conversion
- POP: Point of Purchase
- RCK: Re-presented Check Entry
- IAT: International ACH Transaction

**Same Day ACH**:
- Amount limit: $1,000,000 per transaction (as of March 2024)
- Multiple submission windows throughout the day
- Settlement on same business day

#### **3.3.2 Fedwire Message Format**

**Structure**: Proprietary tag-based format (being migrated to ISO 20022)

**Key Tags**:
- {1510}: Type/Subtype code
- {1520}: IMAD (Input Message Accountability Data)
- {2000}: Amount (12 digits, no decimal)
- {3100}: Sender identification
- {3400}: Receiver identification
- {3600}: Business function code
- {4200}: Beneficiary (bank)
- {5000}: Originator to Beneficiary Information (4 lines of 35 characters)
- {6000}: Originator (bank)
- {6100}: Originator Identification
- {6400}: Beneficiary Identification
- {7059}: Beneficiary reference
- {8200}: Receiver memo

**Message Types**:
- Type 1000: Customer Transfer
- Type 1500: Customer Transfer Plus (enhanced data)
- Type 2000: Financial Institution Transfer

**Future ISO 20022 Format**:
- Like-for-like implementation of current Fedwire fields
- Based on pacs.008 and pacs.009 messages
- Enhanced remittance information support (up to 9,000 characters)

#### **3.3.3 CHIPS Message Format**

**Structure**: Proprietary format with fields numbered 10-95

**Key Fields**:
- Field 10: Message Type
- Field 20: Transaction Reference Number
- Field 30: Value Date
- Field 32: Amount and Currency
- Field 50: Ordering Institution
- Field 52: Ordering Institution Account
- Field 56: Intermediary Institution
- Field 57: Beneficiary Institution
- Field 58: Beneficiary Institution Account
- Field 59: Beneficiary
- Field 70: Remittance Information
- Field 72: Sender to Receiver Information

**Message Types**:
- 100: Customer transfer
- 200: Financial institution transfer
- 300: Foreign exchange settlement

**Future ISO 20022**:
- CHIPS migrating to ISO 20022 in line with Fedwire
- Like-for-like approach
- Enhanced data capacity

#### **3.3.4 SEPA XML Schemas**

**SCT (SEPA Credit Transfer)**:
- Based on ISO 20022 pain.001 (customer to PSP)
- Based on ISO 20022 pacs.008 (PSP to PSP)
- Execution time: D+1
- Amount: No limit

**SCT Inst (SEPA Instant Credit Transfer)**:
- Based on ISO 20022 pain.001 (customer to PSP)
- Based on ISO 20022 pacs.008 (PSP to PSP) with instant service level
- Execution time: <10 seconds
- Amount: €100,000 maximum (2024)
- 24/7/365 availability

**SDD (SEPA Direct Debit)**:
- Core scheme: For all customers
- B2B scheme: Business-to-business only
- Based on ISO 20022 pain.008 (customer to PSP)
- Based on ISO 20022 pacs.003 (PSP to PSP)
- Mandate required (creditor identifier + mandate reference)
- Refund rights: 8 weeks (authorized), 13 months (unauthorized)

**Common Data Elements**:
- Creditor/Debtor IBAN (mandatory)
- BIC (optional in SEPA, transitioning to IBAN-only)
- Remittance Information: 140 characters unstructured or structured
- End-to-end ID: 35 characters
- Purpose code: ISO external code list
- Category purpose code
- Regulatory reporting (if applicable)

#### **3.3.5 BACS Standard 18**

**Structure**: Fixed-length record format

**Message Types**:
- Standard 18: Core payment instructions
- AUDDIS: Automated Direct Debit Instruction Service (mandate management)
- ADDACS: Automated Direct Debit Amendment and Cancellation Service
- DDICA: Direct Debit Instruction Cancellation Advice

**Record Types**:
- File header
- Submission header
- User header
- Contra record
- Payment record (debit/credit)
- User trailer
- Submission trailer
- File trailer

**Key Fields (Payment Record)**:
- Destination sorting code: 6 digits
- Destination account number: 8 digits
- Transaction code: 2 digits
- Amount: 11 digits (in pence)
- Reference: 18 characters
- Processing day
- User number
- Originator identification

**ISO 20022 Conversion**:
- Translation available from pain.001 → Standard 18
- Translation available from Standard 18 → pacs.008
- Official translation guide published by Bacs

**Future**: New Payments Architecture (NPA) program paused; no timeline for full ISO 20022 migration

#### **3.3.6 Faster Payments (UK)**

**Current Format**: ISO 8583 text-based format

**Key Fields**:
- Sort code (6 digits)
- Account number (8 digits)
- Amount (up to £1,000,000 as of 2024)
- Reference (up to 18 characters)
- Payment type code
- Processing date

**Settlement**: Real-time, 24/7/365

**Future ISO 20022**:
- Planned under New Payments Architecture (NPA)
- Program currently paused
- Future format expected to be pain.001/pacs.008 based

#### **3.3.7 PIX (Brazil)**

**Format**: ISO 20022 XML

**Messages Used**:
- PACS messages for inter-PSP settlement
- PAIN messages for initiation

**Key Features**:
- Instant payments (settlement in <10 seconds)
- 24/7/365 availability
- QR code support
- Alias-based addressing (CPF, CNPJ, phone, email, random key)
- Free for individuals

**Data Elements**:
- PIX key (alias)
- Transaction ID
- Amount
- Remittance information
- End-to-end ID

#### **3.3.8 CIPS (China Cross-Border Interbank Payment System)**

**Format**: ISO 20022 XML

**Operating Hours**: 24/5 (Monday to Friday extended hours)

**Participant Structure**:
- Direct participants: Settlement accounts with PBOC
- Indirect participants: Through direct participants

**Messages**:
- PACS messages for payment clearing and settlement
- CAMT messages for account reporting

**Key Features**:
- Clearing and settlement in RMB
- SWIFT network integration
- Payment purpose codes required
- Supporting documentation for cross-border transactions

### 3.4 Industry Reference Models

#### **3.4.1 ISDA Common Domain Model (CDM)**

**Purpose**: Standardized, machine-readable model for derivatives lifecycle events

**Scope**:
- Product definitions (interest rate derivatives, credit derivatives, equity derivatives, FX)
- Trade events (execution, confirmation, allocation, clearing)
- Lifecycle events (resets, payments, novations, exercises, expirations)
- Legal agreements (ISDA Master Agreement, Credit Support Annex)

**Modeling Approach**:
- Domain-Driven Design (DDD)
- Event sourcing patterns
- Immutable event history
- Rosetta DSL (Domain Specific Language) for model definition

**Governance**:
- Open source under FINOS (Fintech Open Source Foundation)
- Community Specification License
- Multiple code implementations (Java, Python, Haskell, etc.)

**Relevance to Payments CDM**:
- Model structure and patterns applicable
- Event sourcing approach for payment lifecycle
- Governance and versioning lessons learned
- Integration with regulatory reporting (DRR)

**ISDA Digital Regulatory Reporting (DRR)**:
- Machine-executable regulatory rules
- ISO 20022 format output for reports
- Jurisdictions covered: CFTC, ESMA (EMIR), FCA, ASIC, MAS, expanding to HKMA, SEC, MiFIR, FINMA
- Common interpretation of regulations across firms

#### **3.4.2 BIAN (Banking Industry Architecture Network)**

**Purpose**: Service-oriented architecture reference model for banking

**Framework Components**:
- Service Domains: 350+ standardized business capabilities
- Business Scenarios: End-to-end process flows
- Service Operations: APIs for each service domain
- Information Model: Canonical data model
- Landscape Architecture: Integration patterns

**Payments-Related Service Domains**:
- Payment Execution
- Payment Initiation
- Payment Order
- ACH Operations
- SWIFT Operations
- Direct Debit Mandate
- Payment Routing
- Correspondent Bank
- Nostro Management
- Position Management
- Card Authorization
- Card Settlement
- Card Transaction

**ISO 20022 Integration**:
- BIAN aligns service domain data models with ISO 20022
- Mapping between BIAN canonical model and ISO 20022 messages
- Ensures consistency across internal (BIAN) and external (ISO 20022) data

**Relevance to BofA Payments CDM**:
- Service domain decomposition approach
- API-first design patterns
- Separation of business logic from product specifics
- Canonical data model patterns

**BIAN Financial Industry Data Model**:
- Entity relationship model
- Business Objects aligned with service domains
- Reusable data components
- Version management and governance

#### **3.4.3 IFX (Interactive Financial eXchange)**

**Purpose**: XML-based messaging standard for financial services

**Scope**:
- Retail banking
- Consumer finance
- Payments
- Cards
- Wealth management

**Message Structure**:
- Request/Response pairs
- Comprehensive data dictionary
- Modular schema design

**Relevance**: Limited adoption compared to ISO 20022; BofA should prioritize ISO 20022 alignment

#### **3.4.4 TWIST (Transaction Workflow Innovation Standards Team)**

**Purpose**: Standards for treasury and trade workflows

**Coverage**:
- Confirmation matching
- Settlement instruction matching
- Trade enrichment
- Corporate actions

**Relevance**: Complementary to ISO 20022 for specific treasury use cases

---

## PEER ANALYSIS

### 4.1 JPMorgan Chase

#### **Payments Modernization**
- **ISO 20022 Adoption**: Went live March 2023; accounts for ~30% of ISO 20022 cross-border message traffic on SWIFT
- **Approach**: Native processing of MX messages with legacy MT support during coexistence
- **Data Platform Strategy**: Coupled ISO 20022 migration with back-office modernization and consolidation
- **Target State**: Consolidated payment processing applications with structured data capabilities across payment rails

#### **Technology Initiatives**:
- **Onyx**: Blockchain-based platform for wholesale payments, repo transactions
- **Liink**: Blockchain network for information exchange (account validation, sanctions screening)
- **Cloud Strategy**: Multi-cloud approach with AWS and Microsoft Azure
- **Data Architecture**: Focus on data lakehouse patterns for analytics

#### **Investment**:
- Technology budget: ~$15 billion annually (2024)
- Significant portion allocated to payments infrastructure modernization

### 4.2 Citigroup

#### **Payments Modernization**
- **ISO 20022 Adoption**: Bridging solution with ISO transformation layer on payment processors
- **Approach**: Coordinated migration across payment platforms with central transformation hub
- **Treasury and Trade Solutions (TTS)**: Global platform serving clients in 160+ countries

#### **Technology Architecture**:
- **Platform Approach**: Modular architecture for payment product processors
- **Cloud Strategy**: Hybrid cloud with AWS and Azure; private cloud investments
- **Data Strategy**: Focus on data quality and structured data for compliance and analytics

#### **Key Differentiators**:
- Strong cross-border payments network
- 24/7 payment operations across time zones
- Extensive correspondent banking relationships

### 4.3 Wells Fargo

#### **Platform Modernization**:
- **Focus**: Digital transformation and platform modernization
- **Payments**: Real-time payments participation (RTP and FedNow)
- **Cloud**: Progressive cloud adoption for compute workloads

#### **Technology Investments**:
- Building diverse, innovative teams for digital future
- Focus on operational resilience and risk management
- Modernization of legacy platforms

### 4.4 HSBC

#### **Global Payments Platform**:
- Strong presence in Asia and EMEA
- ISO 20022 implementation across regions
- Integration of HSBCnet platform for treasury and payments

#### **Technology Leadership**:
- CIO with background in AI investments and private cloud (from Citigroup experience)
- Expanded remit including data and innovation
- Focus on digital operational resilience (DORA compliance)

#### **Data Strategy**:
- Data moat leveraging global operations
- Integration with Quantexa for data unification and AML
- Breaking down data silos

### 4.5 BNY Mellon

#### **Data Architecture Strategy**:
- **Deeply integrated AI strategy** leveraging proprietary data
- **Pragmatic technology architecture**: Capital-efficient approach
- **Cultural commitment**: Becoming an AI-native enterprise

#### **Data & Analytics Platform**:
- BNY Data & Analytics platform for insights
- Collaboration with Quantexa for breaking down data silos
- Unification of data with enhanced accuracy

#### **Technology Approach**:
- Focus on cloud-native solutions
- Integration of AI/ML across operations
- Strong data governance and quality focus

### 4.6 Deutsche Bank

#### **Payments Modernization**:
- ISO 20022 adoption for cross-border payments
- Focus on European and global corporate banking
- TARGET2 and EURO1 participation

#### **Technology Investments**:
- Cloud migration initiatives
- Platform consolidation
- Data architecture modernization

### 4.7 Standard Chartered

#### **Geographic Focus**:
- Strong Asia, Africa, Middle East presence
- Cross-border payment specialization
- Correspondent banking network

#### **Technology**:
- ISO 20022 implementation
- Real-time payments participation in key markets
- Digital banking platforms

### 4.8 Industry Collaborative Initiatives

#### **Regulated Liability Network POC**:
- **Participants**: Wells Fargo, BNY Mellon, HSBC, Citi, Mastercard, TD Bank, PNC, Truist, U.S. Bank
- **Technology**: Distributed ledger technology (DLT) on AWS
- **Scope**: Domestic and cross-border payments, digital assets
- **Results**: Success in programmability, privacy, interoperability, availability, settlement speed

#### **New York Fed CBDC Research**:
- **Project**: Exploring central bank digital currency for wholesale payments
- **Participants**: Major U.S. banks including Wells Fargo, Citi
- **Technology**: Distributed ledger
- **Status**: Research and proof-of-concept stage

### 4.9 Key Takeaways from Peer Analysis

#### **Common Themes**:
1. **ISO 20022 as foundation**: All peers adopting ISO 20022 with varying implementation approaches
2. **Cloud adoption**: Hybrid and multi-cloud strategies predominant; compute-first approach common
3. **Data platform modernization**: Coupled with ISO 20022 to capitalize on structured data benefits
4. **Platform consolidation**: Reducing number of payment processing platforms
5. **Real-time payments**: Universal participation in real-time payment schemes
6. **AI/ML enablement**: Data architecture designed to support advanced analytics and AI
7. **Regulatory technology**: Significant investments in compliance automation and reporting
8. **Collaborative innovation**: Industry participation in DLT and CBDC proofs of concept

#### **Differentiation Opportunities for BofA**:
1. **CashPro Platform Advantage**: Already serving 350+ payment types; opportunity to leverage as unified platform
2. **Data Quality Focus**: Use CDM implementation to leapfrog competitors on data quality
3. **AI Leadership**: Leverage CDM for superior AI/ML capabilities (e.g., fraud detection, forecasting)
4. **Regulatory Efficiency**: CDM-driven approach to regulatory reporting can reduce time and cost
5. **Graph Analytics**: Neo4j integration for payment network analysis, fraud ring detection beyond peer capabilities

---

## CONCLUSION

The research conducted across Bank of America's payments footprint, regulatory landscape, and message formats/data models provides a comprehensive foundation for the data strategy development. Key findings include:

1. **Global Complexity**: BofA operates across 38+ markets with diverse regulatory requirements, payment schemes, and data residency mandates
2. **Regulatory Burden**: Over 50+ distinct regulatory reporting requirements identified across jurisdictions
3. **Standards Convergence**: Industry converging on ISO 20022, providing opportunity for standardization via CDM
4. **Peer Movement**: Competitors investing heavily in data platform modernization coupled with ISO 20022 adoption
5. **Technology Evolution**: Shift toward cloud, real-time, and AI-enabled payment processing creating urgency for modernization

This research forms the evidence base for the strategic recommendations in subsequent workstreams.

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-18 | GPS Data Strategy Team | Initial comprehensive research findings |

---

*End of Research Findings Document*
