# WORKSTREAM 2: PAYMENTS COMMON DOMAIN MODEL (CDM)
## Bank of America Global Payments Data Strategy

**Document Version:** 1.0
**Date:** December 18, 2025
**Classification:** Internal Strategy Document
**Workstream Lead:** UK Resource
**Support:** India Resource 2
**Duration:** Months 1-4

---

## EXECUTIVE SUMMARY

The Payments Common Domain Model (CDM) establishes a unified, standardized data model for all payment types across Bank of America's Global Payments Organization. The CDM serves as the canonical representation of payment data, enabling:

- **Cross-product consistency**: Unified view across ACH, wires, SWIFT, SEPA, RTP, and all payment types
- **Regulatory compliance**: Single source of truth for regulatory reporting across all jurisdictions
- **Analytics enablement**: Consistent data foundation for AI/ML and advanced analytics
- **Operational efficiency**: Reduced data transformation complexity and improved data quality

**Key Principles**:
1. ISO 20022 as canonical foundation
2. Backward compatibility with legacy formats (MT, NACHA, etc.)
3. Regulatory reporting as first-class design driver
4. Extensibility for product-specific requirements
5. Temporal modeling for complete payment lifecycle tracking

**CDM Scope**: 350+ payment types across 38 markets, covering all message formats and regulatory requirements

---

## TABLE OF CONTENTS

1. [Deliverable 2.1: CDM Design Principles and Methodology](#deliverable-21-cdm-design-principles-and-methodology)
2. [Deliverable 2.2: Logical Common Domain Model](#deliverable-22-logical-common-domain-model)
3. [Deliverable 2.3: Physical Common Domain Model](#deliverable-23-physical-common-domain-model)
4. [Deliverable 2.4: CDM Governance Framework](#deliverable-24-cdm-governance-framework)

---

## DELIVERABLE 2.1: CDM DESIGN PRINCIPLES AND METHODOLOGY

### Guiding Principles

#### Principle 1: ISO 20022 as Canonical Foundation

**Rationale**:
- Industry standard converging globally (SWIFT MT sunset Nov 2025)
- Rich data model with comprehensive coverage of payment scenarios
- Structured data enabling analytics and AI/ML
- Regulatory alignment (many regulators mandating ISO 20022)

**Implementation Approach**:
- CDM core schema based on ISO 20022 data dictionary
- All payments mapped to ISO 20022 message equivalents
- Extensions where ISO 20022 gaps exist (documented and governed)

**ISO 20022 Message Categories Covered**:
- **pacs** (Payment Clearing and Settlement): pacs.002, pacs.004, pacs.008, pacs.009, pacs.028
- **pain** (Payment Initiation): pain.001, pain.002, pain.007, pain.008, pain.013, pain.014
- **camt** (Cash Management): camt.052, camt.053, camt.054, camt.055, camt.056, camt.057
- **acmt** (Account Management): acmt.001, acmt.002, acmt.003, acmt.022, acmt.023, acmt.024
- **reda** (Reference Data): reda.006, reda.007, reda.014, reda.041, reda.056, reda.057

#### Principle 2: Extensibility for Proprietary Requirements

**Rationale**:
- Product-specific fields not covered by ISO 20022
- BofA internal operational requirements
- Customer-specific customizations (CashPro features)

**Implementation Approach**:
- Core CDM based on ISO 20022 (80-90% coverage)
- Extension mechanism via additional properties (JSON, XML)
- Versioned extensions with governance approval required
- Clear separation of core vs. extension fields

**Extension Categories**:
1. **Product Extensions**: Product-specific features (e.g., CashPro workflow states)
2. **Operational Extensions**: Internal processing fields (e.g., queue assignments, repair flags)
3. **Customer Extensions**: Customer-specific fields (e.g., custom reference numbers, tags)
4. **Regional Extensions**: Jurisdiction-specific requirements not in ISO 20022

#### Principle 3: Backward Compatibility with MT Formats During Transition

**Rationale**:
- SWIFT MT messages coexist until Nov 2025
- Legacy systems still generating MT format
- Gradual migration approach required

**Implementation Approach**:
- CDM supports both MX (ISO 20022) and MT message mappings
- Translation layer: MT → CDM and CDM → MT
- Documented truncation risks (e.g., remittance info 140 chars in MT vs. 9000 in MX)
- Dual representation during coexistence period

**Backward Compatibility Matrix**:

| Legacy Format | CDM Coverage | Mapping Complexity | Notes |
|---------------|--------------|-------------------|-------|
| SWIFT MT103, MT202 | 100% | Medium | Truncation risk for long remittance info |
| NACHA ACH | 100% | Low | Standard Entry Class (SEC) codes mapped to purpose codes |
| Fedwire | 100% | Low | Tag-based format maps directly to CDM |
| CHIPS | 100% | Low | Field numbers map to CDM elements |
| BACS Standard 18 | 100% | Medium | Fixed-length format requires parsing logic |
| Check/Image | 90% | High | Image metadata only; MICR line parsed |

#### Principle 4: Regulatory Reporting as First-Class Design Driver

**Rationale**:
- Regulatory reporting is primary use case driving data strategy
- 50+ distinct regulatory reports across jurisdictions
- CDM must natively support all required data elements

**Implementation Approach**:
- All regulatory data elements included in CDM core schema
- Regulatory reporting crosswalk: CDM → each regulatory report format
- No additional transformations required for regulatory reporting
- Audit trail and lineage built into CDM

**Regulatory Data Elements in CDM**:
- **US**: BSA/AML fields (CTR, SAR), OFAC screening results, tax reporting (1099, 1042)
- **EU/UK**: PSD2 reporting fields, DORA incident data, AML/CTF fields
- **APAC**: MAS reporting, HKMA fields, RBI purpose codes, PBOC cross-border fields
- **Global**: FATF travel rule, Basel operational risk, correspondent banking due diligence

#### Principle 5: Analytics and AI-Readiness

**Rationale**:
- Data should support advanced analytics without additional transformation
- ML models require consistent, high-quality feature engineering
- Graph analytics require relationship modeling

**Implementation Approach**:
- Denormalized structures for analytics performance (avoid excessive joins)
- Pre-computed aggregates and features in Gold layer
- Graph-friendly identifiers (nodes and edges for Neo4j)
- Temporal consistency for time-series analysis

**Analytics-Optimized Design**:
- Consistent party identification across all payments (enables customer 360°)
- Transaction chains and relationships modeled explicitly
- Event sourcing pattern for complete lifecycle tracking
- Feature store integration (features derived from CDM)

#### Principle 6: Multi-Product Harmonization

**Rationale**:
- 350+ payment types must be represented in single unified model
- Cross-product analytics require consistent data model
- Operational efficiencies from shared processing logic

**Implementation Approach**:
- Core CDM applies to all payment types
- Product-specific extensions minimal and governed
- Common processing logic (validation, screening, routing) applied uniformly
- Cross-product views (e.g., "all_payments") for analytics

**Product Coverage**:
- Domestic US: ACH, Fedwire, CHIPS, RTP, FedNow, Zelle, Checks
- International: SWIFT (MT and MX), cross-border wires
- Regional: SEPA (SCT, SCT Inst, SDD), BACS, Faster Payments, PIX, CIPS
- Commercial: CashPro products, virtual accounts, liquidity management

#### Principle 7: Temporal Modeling for Historical Analysis

**Rationale**:
- Payment lifecycle spans multiple states and events
- Audit and compliance require complete history
- Analytics require point-in-time accuracy

**Implementation Approach**:
- Event sourcing: All state changes captured as events
- Delta Lake time travel: Access historical versions of records
- Slowly Changing Dimensions (SCD Type 2) for reference data
- Effective dates and valid time periods for all records

**Temporal Patterns**:
- **Payment Events**: Initiated → Validated → Screened → Cleared → Settled → Confirmed
- **Status History**: Full status change log with timestamps and reasons
- **Reference Data Versioning**: Currency rates, purpose codes, party info with effective dates
- **Audit Trail**: Complete who/what/when/why for all changes

---

### Methodology

#### Domain-Driven Design (DDD) Approach

**Core Domain Entities (Aggregates)**:

1. **Payment Instruction**: Root aggregate containing all payment details
2. **Party**: Debtor, Creditor, and Intermediary party information
3. **Account**: Account identification and attributes
4. **Status**: Payment status and lifecycle events
5. **Regulatory Data**: Compliance and reporting information

**Bounded Contexts**:
- Payment Processing Context: Initiation, validation, routing, clearing, settlement
- Compliance Context: Screening, monitoring, reporting
- Analytics Context: Aggregations, features, insights
- Reference Data Context: Currencies, countries, BICs, purpose codes

**Ubiquitous Language**:
Establishing common terminology across business and technical teams:
- "Payment Instruction" (not "transaction" or "transfer" alone - too ambiguous)
- "Debtor" and "Creditor" (aligned with ISO 20022, not "sender/receiver" or "payer/payee")
- "Interbank Settlement Amount" (not just "amount" - distinguishes from instructed amount)
- "End-to-End ID" (ISO 20022 term, universally understood)

#### Event Sourcing Patterns

**Event-Driven Architecture**:
- All state changes represented as immutable events
- Payment state reconstructed from event log
- Audit trail inherent in design

**Event Types**:
```
PaymentInitiatedEvent
PaymentValidatedEvent
PaymentScreenedEvent (fraud and AML)
PaymentRoutedEvent
PaymentClearedEvent
PaymentSettledEvent
PaymentConfirmedEvent
PaymentReturnedEvent
PaymentFailedEvent
StatusChangedEvent
```

**Benefits**:
- Complete audit trail for regulatory compliance
- Time travel: Reconstruct payment state at any point in time
- Event replay for testing and debugging
- Integration via event streams (Kafka)

#### ISDA CDM Lessons Learned and Patterns

**Applicable Patterns from ISDA CDM**:

1. **Rosetta DSL Approach**: Domain-specific language for model definition
   - BofA Adaptation: JSON Schema as DSL with comprehensive documentation
   - Benefit: Machine-readable, version-controlled, code-generation enabled

2. **Product Definition as Code**: Products defined in machine-executable format
   - BofA Adaptation: Payment product types defined in schema with validation rules
   - Benefit: Consistent product definition across systems

3. **Lifecycle Events Modeling**: Complete trade lifecycle captured
   - BofA Adaptation: Complete payment lifecycle from initiation to settlement
   - Benefit: Full traceability and audit trail

4. **Legal Agreement Integration**: ISDA Master Agreement modeled in CDM
   - BofA Adaptation: Customer agreements, service terms integrated in CDM
   - Benefit: Links contracts to payment transactions

5. **Regulatory Reporting Module**: DRR (Digital Regulatory Reporting)
   - BofA Adaptation: Regulatory reporting as first-class CDM citizen
   - Benefit: Automated, accurate regulatory reporting

**ISDA CDM vs. BofA Payments CDM Comparison**:

| Aspect | ISDA CDM | BofA Payments CDM |
|--------|----------|-------------------|
| Domain | Derivatives | Payments |
| Standard Basis | FpML, ISO 20022 (limited) | ISO 20022 (primary) |
| Scope | Product definition, lifecycle, legal | Payment instruction, lifecycle, regulatory |
| Governance | FINOS open source | Internal (with potential industry collaboration) |
| Technology | Rosetta DSL | JSON Schema, Delta Lake |
| Primary Use Case | Trade lifecycle, regulatory reporting | Payment processing, regulatory reporting, analytics |

#### Digital Regulatory Reporting Alignment

**DRR Principles Applied**:

1. **Machine-Readable Regulations**: Regulatory rules as code
   - BofA Approach: Data quality rules and reporting logic as code (DLT expectations, SQL)
   - Example: CTR $10,000 threshold as validation rule, not manual check

2. **Common Interpretation**: Shared understanding of regulations across firms
   - BofA Approach: Participate in industry forums (SWIFT, EPC, NACHA) for aligned interpretation
   - Benefit: Consistent compliance across industry

3. **Automated Reporting**: Generate reports directly from operational data
   - BofA Approach: Regulatory reports generated from CDM without manual intervention
   - Benefit: Accuracy, timeliness, cost reduction

4. **Audit Trail**: Complete lineage from source data to report
   - BofA Approach: Unity Catalog lineage + Delta Lake audit trail
   - Benefit: Regulatory audit readiness

---

## DELIVERABLE 2.2: LOGICAL COMMON DOMAIN MODEL

### Core Domain Entities

#### Entity 1: Payment Instruction (Root Aggregate)

**Purpose**: Represents a single payment instruction from initiation to settlement

**Attributes**:

```
PaymentInstruction {
  // Identification
  paymentId: UUID (primary key)
  endToEndId: String (ISO 20022 end-to-end identification)
  uetr: UUID (SWIFT gpi unique end-to-end transaction reference)
  instructionId: String (instruction identification)
  transactionId: String (transaction identification)

  // Classification
  paymentType: PaymentType (enum: ACH, Wire, SWIFT, RTP, SEPA, etc.)
  productCode: String (BofA product classification)
  schemeCode: SchemeCode (enum: NACHA, Fedwire, SWIFT, SEPA, RTP, etc.)
  serviceLevel: ServiceLevel (e.g., URGP for urgent, SEPA for SEPA, etc.)

  // Amount and Currency
  instructedAmount: Money {
    amount: Decimal(18,2)
    currency: CurrencyCode (ISO 4217)
  }
  interbankSettlementAmount: Money (if different from instructed)
  exchangeRate: Decimal(15,10) (if currency conversion)
  chargeBearer: ChargeBearer (enum: DEBT, CRED, SHAR, SLEV)

  // Dates and Times
  creationDateTime: DateTime (timestamp of instruction creation)
  requestedExecutionDate: Date
  valueDate: Date
  settlementDate: Date (actual settlement)
  acceptanceDateTime: DateTime

  // Parties
  debtor: Party (reference to Party entity)
  debtorAccount: Account (reference to Account entity)
  debtorAgent: FinancialInstitution (reference to FI entity)

  creditor: Party
  creditorAccount: Account
  creditorAgent: FinancialInstitution

  intermediaryAgents: List<FinancialInstitution> (correspondent banks, clearing agents)

  // Purpose and Remittance
  purpose: PurposeCode (ISO 20022 external code list)
  categoryPurpose: CategoryPurpose
  remittanceInformation: RemittanceInformation {
    unstructured: String (max 9000 chars per ISO 20022 MX)
    structured: StructuredRemittanceInformation (invoices, documents, etc.)
  }

  // Status and Lifecycle
  currentStatus: PaymentStatus (enum: initiated, pending, validated, cleared, settled, completed, failed, returned)
  statusReason: StatusReasonCode
  statusHistory: List<StatusEvent> (all status changes with timestamps)

  // Charges and Fees
  charges: List<Charge> {
    chargeType: ChargeType
    chargeAmount: Money
    chargeTaxAmount: Money
  }

  // Regulatory and Compliance
  regulatoryReporting: List<RegulatoryReportingCode>
  crossBorderFlag: Boolean
  balanceOfPaymentsCode: String
  sanctionsScreeningResult: ScreeningResult {
    status: Enum (clear, hit, pending, false_positive)
    matchedLists: List<String> (e.g., OFAC SDN, EU sanctions)
    reviewStatus: Enum (auto_cleared, manual_review, blocked)
    reviewedBy: String
    reviewedDateTime: DateTime
  }
  fraudScore: Decimal(5,2) (0-100 risk score)
  amlRiskRating: Enum (low, medium, high, very_high)

  // Source and Lineage
  sourceSystem: String (originating system)
  sourceRecordId: String (ID in source system)
  relatedPayments: List<PaymentReference> (original payment for returns, cover payments, etc.)

  // Audit and Data Quality
  createdTimestamp: DateTime
  lastUpdatedTimestamp: DateTime
  dataQualityScore: Decimal(5,2) (0-100)
  dataQualityIssues: List<DataQualityIssue>

  // Product-Specific Extensions
  extensions: Map<String, Any> (product-specific additional fields, e.g., CashPro workflow state)
}
```

#### Entity 2: Party

**Purpose**: Represents a party in a payment (debtor, creditor, or intermediary)

**Attributes**:

```
Party {
  // Identification
  partyId: UUID (primary key)
  name: String (required, standardized format)
  legalName: String (official legal name if different)

  // Identification Schemes
  identifications: List<PartyIdentification> {
    scheme: Enum (BIC, LEI, DUNS, Proprietary, TaxID, PassportNumber, NationalID)
    identification: String
    issuingCountry: CountryCode
  }

  // Party Type
  partyType: Enum (individual, organization, government, financial_institution)
  organizationType: Enum (corporation, partnership, trust, etc.) (if organization)

  // Contact Information
  postalAddress: PostalAddress {
    addressType: Enum (residential, business, correspondence)
    streetName: String
    buildingNumber: String
    postCode: String
    townName: String
    countrySubDivision: String (state/province)
    country: CountryCode (ISO 3166-1 alpha-2)
  }
  phoneNumber: String
  emailAddress: String

  // Regulatory Classification
  isPEP: Boolean (Politically Exposed Person)
  pepType: Enum (domestic, foreign, international_organization) (if isPEP)
  isSanctioned: Boolean
  sanctionedBy: List<String> (e.g., OFAC, EU, UN)
  highRiskJurisdiction: Boolean

  // Relationship Data
  customerSince: Date (if BofA customer)
  riskRating: Enum (low, medium, high, very_high)
  kycStatus: Enum (pending, approved, expired, rejected)
  kycExpiryDate: Date
  lastReviewDate: Date

  // Data Quality
  dataQualityScore: Decimal(5,2)
  standardizationStatus: Enum (raw, standardized, verified)

  // Effective Dates (SCD Type 2)
  effectiveFrom: DateTime
  effectiveTo: DateTime (null if current version)
}
```

#### Entity 3: Account

**Purpose**: Represents a bank account (debtor account, creditor account, nostro/vostro)

**Attributes**:

```
Account {
  // Identification
  accountId: UUID (primary key)
  iban: String (if applicable, ISO 13616 format)
  accountNumber: String (if IBAN not applicable)
  accountName: String

  // Account Type and Currency
  accountType: Enum (current, savings, nostro, vostro, virtual, loan)
  currency: CurrencyCode (ISO 4217)

  // Servicer (Financial Institution holding the account)
  servicer: FinancialInstitution (reference to FI entity)

  // Account Relationship
  accountRelationship: Enum (customer_account, nostro, vostro, internal)
  accountOwner: Party (reference to Party entity)

  // Status
  accountStatus: Enum (active, dormant, closed, blocked)
  statusReason: String

  // Balance Information (optional, may not be available for all accounts)
  availableBalance: Money
  ledgerBalance: Money
  lastUpdatedDateTime: DateTime

  // Restrictions and Limits
  restrictions: List<String> (e.g., debit_only, credit_only, frozen)
  dailyLimits: Map<TransactionType, Money>

  // Effective Dates
  effectiveFrom: DateTime
  effectiveTo: DateTime
}
```

#### Entity 4: Financial Institution

**Purpose**: Represents a financial institution (agent banks, intermediaries, correspondents)

**Attributes**:

```
FinancialInstitution {
  // Identification
  financialInstitutionId: UUID (primary key)
  bic: String (ISO 9362, 8 or 11 characters)
  lei: String (Legal Entity Identifier, ISO 17442)
  name: String
  legalName: String

  // Address
  postalAddress: PostalAddress

  // Branch Information
  branchIdentification: String (if applicable)
  branchName: String

  // Clearing System Membership
  clearingSystemMemberships: List<ClearingSystemMembership> {
    clearingSystem: Enum (Fedwire, CHIPS, TARGET2, CHAPS, etc.)
    memberId: String
    membershipType: Enum (direct, indirect)
  }

  // Correspondent Banking
  correspondentRelationships: List<CorrespondentRelationship> {
    counterpartyFI: FinancialInstitution
    relationshipType: Enum (nostro, vostro, bilateral)
    accountNumber: String
    currency: CurrencyCode
    status: Enum (active, suspended, terminated)
  }

  // Regulatory Information
  primaryRegulator: String
  jurisdiction: CountryCode
  regulatoryLicenses: List<String>

  // Due Diligence
  dueDiligenceStatus: Enum (approved, pending, rejected)
  lastDueDiligenceDate: Date
  nextReviewDate: Date
  riskRating: Enum (low, medium, high)

  // Effective Dates
  effectiveFrom: DateTime
  effectiveTo: DateTime
}
```

#### Entity 5: Payment Status (Lifecycle Event)

**Purpose**: Represents a status change event in the payment lifecycle

**Attributes**:

```
PaymentStatusEvent {
  // Identification
  statusEventId: UUID (primary key)
  paymentId: UUID (foreign key to PaymentInstruction)

  // Status Information
  status: PaymentStatus (enum: initiated, pending, validated, screened, cleared, settled, completed, failed, returned, cancelled)
  statusReason: StatusReasonCode (ISO 20022 status reason codes)
  statusReasonNarrative: String (additional explanation)

  // Timestamp and Actor
  statusTimestamp: DateTime
  updatedBy: String (user ID or system name)
  updateSource: String (system or process that updated status)

  // Additional Context
  processingNode: String (for distributed systems, which node processed)
  retryAttempt: Integer (if applicable)
  errorDetails: String (if status = failed)

  // Upstream/Downstream References
  externalReference: String (reference from external system, e.g., SWIFT ACK)
  relatedEvents: List<UUID> (related status events, e.g., screening event, clearing event)
}
```

#### Entity 6: Settlement

**Purpose**: Represents settlement information for a payment

**Attributes**:

```
Settlement {
  // Identification
  settlementId: UUID (primary key)
  paymentId: UUID (foreign key to PaymentInstruction)

  // Settlement Method
  settlementMethod: Enum (CLRG - clearing system, INDA - instructed agent, INGA - instructing agent)
  clearingSystem: ClearingSystemCode (Fedwire, CHIPS, TARGET2, etc.)

  // Settlement Account
  settlementAccount: Account (reference to Account entity, e.g., nostro account)

  // Settlement Date and Time
  interbankSettlementDate: Date
  settlementTimestamp: DateTime

  // Settlement Amount
  settlementAmount: Money

  // Related Settlement Instructions
  instructingAgent: FinancialInstitution
  instructedAgent: FinancialInstitution

  // Settlement Status
  settlementStatus: Enum (pending, settled, failed, returned)
  settlementReference: String (external settlement system reference)
}
```

#### Entity 7: Charges and Fees

**Purpose**: Represents charges and fees associated with a payment

**Attributes**:

```
Charge {
  // Identification
  chargeId: UUID (primary key)
  paymentId: UUID (foreign key to PaymentInstruction)

  // Charge Type
  chargeType: ChargeType (enum: wire_fee, fx_margin, correspondent_fee, amendment_fee, etc.)
  chargeCategory: Enum (transaction_based, account_based, service_based)

  // Amount
  chargeAmount: Money
  chargeTaxAmount: Money (VAT or other applicable taxes)
  totalChargeAmount: Money (charge + tax)

  // Charge Bearer
  chargeBearer: ChargeBearer (who pays: DEBT = debtor, CRED = creditor)

  // Charge Calculation
  calculationBasis: Enum (flat_fee, percentage, tiered)
  calculationDetails: String (formula or reference to pricing table)

  // Charge Booking
  chargeAccountDebit: Account (account debited for charge)
  chargeAccountCredit: Account (account credited, i.e., revenue account)

  // Timestamp
  chargeAppliedDateTime: DateTime
}
```

#### Entity 8: Regulatory Information

**Purpose**: Represents regulatory and compliance data for a payment

**Attributes**:

```
RegulatoryInformation {
  // Identification
  regulatoryInfoId: UUID (primary key)
  paymentId: UUID (foreign key to PaymentInstruction)

  // Regulatory Reporting Codes
  regulatoryReportingCodes: List<RegulatoryReportingCode> {
    codeType: Enum (purpose_code, balance_of_payments, transaction_type)
    code: String
    jurisdiction: CountryCode
    description: String
  }

  // Transaction Reporting
  transactionReportingType: Enum (CTR, SAR, STR, FBAR, etc.)
  reportingJurisdiction: CountryCode
  reportingObligation: Boolean (does this transaction trigger a report?)
  reportReference: String (reference to generated report)

  // Cross-Border Information
  crossBorderFlag: Boolean
  originatingCountry: CountryCode
  destinationCountry: CountryCode
  transactionCorridor: String (e.g., US-MX, UK-EU)

  // Tax Reporting
  taxReportingType: Enum (Form 1099, Form 1042, FATCA 8966, etc.)
  taxWithholding: Money
  taxJurisdiction: CountryCode

  // FATF Travel Rule
  travelRuleCompliant: Boolean
  originatorInformation: Party (full originator details per travel rule)
  beneficiaryInformation: Party (full beneficiary details)

  // Sanctions and Screening
  sanctionsScreeningRequired: Boolean
  sanctionsScreeningResults: List<ScreeningResult>

  // AML Risk Indicators
  structuringIndicator: Boolean (potential structuring to avoid reporting)
  unusualActivityFlag: Boolean
  highRiskIndicators: List<String>

  // Documentation
  supportingDocuments: List<DocumentReference> {
    documentType: Enum (invoice, contract, shipping_doc, etc.)
    documentId: String
    documentLocation: String (URI or file path)
  }
}
```

#### Entity 9: Remittance Information

**Purpose**: Represents structured and unstructured remittance information

**Attributes**:

```
RemittanceInformation {
  // Identification
  remittanceInfoId: UUID (primary key)
  paymentId: UUID (foreign key to PaymentInstruction)

  // Unstructured Remittance
  unstructured: List<String> (multiple lines, each up to 140 chars for MT compatibility, or single string up to 9000 chars for MX)

  // Structured Remittance
  structured: StructuredRemittanceInformation {
    // Invoice Information
    invoices: List<Invoice> {
      invoiceNumber: String
      invoiceDate: Date
      invoiceAmount: Money
      paymentAmount: Money (partial payment amount if < invoice amount)
      discountAmount: Money
      taxAmount: Money
    }

    // Document References
    documents: List<DocumentReference> {
      documentType: Enum (invoice, credit_note, debit_note, purchase_order, etc.)
      documentNumber: String
      documentDate: Date
      documentAmount: Money
    }

    // Creditor Reference
    creditorReferenceInformation: CreditorReference {
      type: Enum (ISO11649_creditor_reference, SCOR, proprietary)
      reference: String
    }

    // Additional Information
    additionalRemittanceInformation: String
  }
}
```

#### Entity 10: Payment Chain (Relationships)

**Purpose**: Represents relationships between payments (returns, reversals, cover payments, etc.)

**Attributes**:

```
PaymentRelationship {
  // Identification
  relationshipId: UUID (primary key)
  parentPaymentId: UUID (foreign key to PaymentInstruction)
  relatedPaymentId: UUID (foreign key to PaymentInstruction)

  // Relationship Type
  relationshipType: Enum (return, reversal, cover, amendment, cancellation, recall, refund)
  relationshipReason: String (reason for relationship, e.g., return reason code)

  // Timestamp
  relationshipEstablishedDateTime: DateTime

  // Additional Context
  originalInstructedAmount: Money (if relationship involves amount change)
  amountReturned: Money (for returns)
  returnReasonCode: ReturnReasonCode
}
```

---

### Supporting Domain Entities

#### Entity 11: Reference Data

**Purpose**: Centralized reference data used across all payments

**Reference Data Types**:

1. **Currency Reference**:
```
Currency {
  currencyCode: CurrencyCode (ISO 4217, e.g., USD, EUR, GBP)
  currencyName: String
  numericCode: String (ISO 4217 numeric code)
  minorUnit: Integer (decimal places, e.g., 2 for USD)
  effectiveFrom: Date
  effectiveTo: Date
}
```

2. **Country Reference**:
```
Country {
  countryCode: CountryCode (ISO 3166-1 alpha-2, e.g., US, GB, DE)
  countryName: String
  alpha3Code: String (ISO 3166-1 alpha-3)
  numericCode: String
  region: Enum (Americas, EMEA, APAC)
  subregion: String
  highRiskJurisdiction: Boolean
  dataResidencyRequirements: String
  effectiveFrom: Date
  effectiveTo: Date
}
```

3. **Clearing System Reference**:
```
ClearingSystem {
  clearingSystemCode: String (e.g., FDW = Fedwire, CHP = CHIPS, TGT = TARGET2)
  clearingSystemName: String
  operatingCountry: CountryCode
  currency: CurrencyCode
  systemType: Enum (RTGS, ACH, card_network, etc.)
  operatingHours: String
  cutoffTimes: Map<DayOfWeek, Time>
  settlementCycle: Enum (real_time, same_day, next_day, T+2, etc.)
}
```

4. **Purpose Code Reference**:
```
PurposeCode {
  code: String (ISO 20022 external code list, e.g., SALA = salary, SUPP = supplier payment)
  description: String
  category: Enum (trade, treasury, personal, government, etc.)
  applicableProducts: List<PaymentType>
  jurisdictions: List<CountryCode> (some purpose codes are jurisdiction-specific)
}
```

5. **Regulatory Product Mapping**:
```
RegulatoryProductType {
  productCode: String (internal BofA product code)
  regulatoryClassification: Map<Jurisdiction, String> {
    US: "ACH Credit"
    EU: "SEPA Credit Transfer"
    UK: "Faster Payment"
  }
  reportingRequirements: List<RegulationReference>
}
```

#### Entity 12: Compliance and Screening

**Purpose**: Represents compliance screening results and case management

**Attributes**:

```
ScreeningResult {
  // Identification
  screeningId: UUID (primary key)
  paymentId: UUID (foreign key to PaymentInstruction)

  // Screening Type
  screeningType: Enum (sanctions, fraud, AML, PEP, adverse_media)
  screeningList: String (e.g., OFAC SDN, EU Sanctions, HMT Sanctions)

  // Screening Outcome
  screeningStatus: Enum (clear, hit, potential_hit, false_positive, pending_review)
  matchScore: Decimal(5,2) (0-100 confidence score)

  // Match Details
  matchedEntity: String (name of matched entity on screening list)
  matchedFields: List<String> (fields that matched: name, address, DOB, etc.)
  matchReason: String

  // Review and Resolution
  reviewStatus: Enum (auto_cleared, manual_review, escalated, blocked)
  reviewedBy: String (user ID)
  reviewedDateTime: DateTime
  reviewComments: String
  actionTaken: Enum (release, block, request_additional_info)

  // SLA Tracking
  screeningInitiatedDateTime: DateTime
  screeningCompletedDateTime: DateTime
  slaBreachFlag: Boolean

  // Audit
  screeningSystem: String (vendor or system name)
  screeningVersion: String (algorithm or list version)
}
```

```
ComplianceCase {
  // Identification
  caseId: UUID (primary key)
  paymentId: UUID (foreign key to PaymentInstruction)

  // Case Type
  caseType: Enum (sanctions_hit, fraud_alert, SAR_investigation, customer_due_diligence)
  casePriority: Enum (low, medium, high, critical)

  // Case Status
  caseStatus: Enum (open, in_progress, pending_info, escalated, closed)
  caseOutcome: Enum (cleared, blocked, filed_SAR, escalated_to_legal)

  // Assignment
  assignedTo: String (user ID or team)
  assignedDateTime: DateTime

  // Investigation
  investigationNotes: List<InvestigationNote> {
    noteTimestamp: DateTime
    noteAuthor: String
    noteText: String
  }

  // Resolution
  resolutionDateTime: DateTime
  resolutionNarrative: String

  // SLA
  slaDeadline: DateTime
  slaBreachFlag: Boolean
}
```

#### Entity 13: Operational (Exceptions, Repairs, Audit)

**Purpose**: Operational data for payment processing

**Attributes**:

```
PaymentException {
  // Identification
  exceptionId: UUID (primary key)
  paymentId: UUID (foreign key to PaymentInstruction)

  // Exception Type
  exceptionType: Enum (validation_error, insufficient_funds, account_closed, format_error, etc.)
  exceptionCategory: Enum (technical, business, compliance)
  exceptionSeverity: Enum (low, medium, high, critical)

  // Exception Details
  exceptionDescription: String
  exceptionCode: String (error code)
  exceptionField: String (field that caused exception, if applicable)

  // Resolution
  resolutionStatus: Enum (pending, in_progress, resolved, cannot_resolve)
  resolutionAction: Enum (auto_repair, manual_repair, return, reject)
  resolutionNotes: String
  resolvedBy: String
  resolvedDateTime: DateTime

  // SLA
  exceptionRaisedDateTime: DateTime
  slaDeadline: DateTime
  slaBreachFlag: Boolean

  // Root Cause
  rootCause: String
  preventionActions: String
}
```

```
ManualIntervention {
  // Identification
  interventionId: UUID (primary key)
  paymentId: UUID (foreign key to PaymentInstruction)

  // Intervention Type
  interventionType: Enum (repair, override, approval, cancellation)
  interventionReason: String

  // User and Approval
  requestedBy: String
  approvedBy: String (if approval required)
  approvalDateTime: DateTime

  // Changes Made
  originalValue: Map<String, Any> (fields before intervention)
  updatedValue: Map<String, Any> (fields after intervention)

  // Audit
  interventionTimestamp: DateTime
  interventionJustification: String
}
```

```
AuditTrail {
  // Identification
  auditId: UUID (primary key)
  paymentId: UUID (foreign key to PaymentInstruction)

  // Event Information
  eventType: Enum (created, updated, deleted, viewed, exported)
  eventTimestamp: DateTime

  // Actor
  userId: String
  userRole: String
  ipAddress: String
  sessionId: String

  // Changes (for update events)
  changedFields: List<FieldChange> {
    fieldName: String
    oldValue: String
    newValue: String
  }

  // Context
  systemName: String
  processName: String
  transactionId: String
}
```

---

### Cross-Product Mapping

Comprehensive mapping of each payment product to the Common Domain Model:

#### ACH → CDM Mapping

**Source Format**: NACHA file format (fixed-width, 94 characters/record)

**Key Mappings**:

| NACHA Field | NACHA Position | CDM Element | Transformation |
|-------------|----------------|-------------|----------------|
| Transaction Code | Position 2-3 (Entry Detail) | paymentType | Map to "ACH_CREDIT" or "ACH_DEBIT" |
| Receiving DFI ID | Position 4-11 | creditorAgent.clearingSystemMemberships[FedACH].memberId | Direct mapping (routing number) |
| DFI Account Number | Position 13-29 | creditorAccount.accountNumber | Trim leading zeros |
| Amount | Position 30-39 | instructedAmount.amount | Convert cents to decimal (divide by 100) |
| Individual Name | Position 55-76 | creditor.name | Standardize (trim, title case) |
| Standard Entry Class (SEC) Code | Batch Header Position 51-53 | extensions.achSECCode | Store as extension; map to purpose codes where applicable (PPD→personal, CCD→corporate) |
| Company ID | Batch Header Position 41-50 | debtor.identifications[TaxID] | EIN or TIN |
| Effective Entry Date | Batch Header Position 70-75 | requestedExecutionDate | Convert YYMMDD to ISO 8601 date |
| Addenda Record Indicator | Entry Detail Position 79 | (determines if remittance info present) | If "1", parse addenda for remittanceInformation.unstructured |
| Payment Related Info (Addenda) | Addenda Position 4-83 | remittanceInformation.unstructured | Direct mapping |

**Data Quality Considerations**:
- **Debtor/Creditor Name**: Often abbreviated (22 char limit); requires standardization
- **Account Numbers**: May have leading zeros; normalize
- **Remittance Information**: Limited to 80 characters in standard addenda; longer remittance requires CCD/CTX formats

**Sample ACH Entry → CDM**:

```
NACHA Entry Detail Record:
6220731000012345678900000010000JOHN DOE              0123456789      012345678

Mapped to CDM:
{
  "paymentType": "ACH_CREDIT",
  "schemeCode": "NACHA",
  "instructedAmount": {
    "amount": 100.00,
    "currency": "USD"
  },
  "creditorAgent": {
    "clearingSystemMemberships": [{
      "clearingSystem": "FedACH",
      "memberId": "073100001"
    }]
  },
  "creditorAccount": {
    "accountNumber": "2345678900"
  },
  "creditor": {
    "name": "John Doe"
  },
  "requestedExecutionDate": "2025-01-15",
  "extensions": {
    "achTransactionCode": "22",
    "achSECCode": "PPD",
    "achTraceNumber": "012345678"
  }
}
```

#### Wire (Fedwire/CHIPS) → CDM Mapping

**Source Format**: Fedwire proprietary tag-based format

**Key Mappings**:

| Fedwire Tag | Description | CDM Element | Transformation |
|-------------|-------------|-------------|----------------|
| {1510} | Type/Subtype | paymentType | Map to "WIRE_DOMESTIC" |
| {1520} | IMAD | instructionId | Direct mapping |
| {2000} | Amount | instructedAmount | Convert to decimal, divide by 100, currency = USD |
| {3100} | Sender ABA | debtorAgent.clearingSystemMemberships[Fedwire].memberId | Direct |
| {3400} | Receiver ABA | creditorAgent.clearingSystemMemberships[Fedwire].memberId | Direct |
| {4200} | Beneficiary Bank | creditorAgent.name | Parse name and BIC |
| {5000} | Originator to Beneficiary Info | remittanceInformation.unstructured | Concatenate 4 lines (each 35 chars) |
| {6000} | Originator | debtor.name | Parse |
| {6100} | Originator ID | debtor.identifications | Parse |
| {6400} | Beneficiary | creditor.name | Parse |
| {6410} | Beneficiary Account | creditorAccount.accountNumber | Parse |

**Future ISO 20022 Format (Fedwire)**:
- Fedwire migrating to ISO 20022 (based on pacs.008)
- Like-for-like implementation initially
- Enhanced remittance information support (up to 9,000 characters)

#### SWIFT MT → CDM Mapping

**Source Format**: SWIFT MT messages (particularly MT103, MT202)

**MT103 (Single Customer Credit Transfer) → CDM**:

| MT103 Field | Description | CDM Element | Transformation |
|-------------|-------------|-------------|----------------|
| :20: | Transaction Reference | instructionId | Direct |
| :23B: | Bank Operation Code | extensions.swiftBankOperationCode | Store as extension |
| :32A: | Value Date, Currency, Amount | valueDate, instructedAmount | Parse YYMMDD, currency (3 chars), amount (decimal with comma) |
| :50K: or :50A: | Ordering Customer | debtor | Parse name and address (multi-line) |
| :52A: or :52D: | Ordering Institution | debtorAgent | Parse BIC or name/address |
| :57A: or :57D: | Account With Institution | creditorAgent | Parse BIC |
| :59: or :59A: | Beneficiary | creditor, creditorAccount | Parse account number and name/address (multi-line) |
| :70: | Remittance Information | remittanceInformation.unstructured | Max 4 lines x 35 chars = 140 chars |
| :71A: | Details of Charges | chargeBearer | OUR, BEN, SHA |
| :72: | Sender to Receiver Info | extensions.swiftSenderToReceiverInfo | Regulatory reporting, intermediary instructions |

**Challenges**:
- **Truncation**: MT103 :70: field limited to 140 chars; longer remittance info truncated
- **Unstructured Data**: Names and addresses not in structured format; requires parsing
- **Code Interpretation**: MT uses proprietary codes that need mapping to ISO 20022/CDM equivalents

**MT202 (General FI Transfer) → CDM**:
Similar structure to MT103 but for financial institution transfers (no ultimate debtor/creditor, only ordering/beneficiary institutions)

#### SWIFT MX (ISO 20022) → CDM Mapping

**Source Format**: pacs.008 (FI to FI Customer Credit Transfer)

**Mapping**:
Since CDM is based on ISO 20022, mapping is largely **direct** with minimal transformation:

| pacs.008 Element | CDM Element | Transformation |
|------------------|-------------|----------------|
| GrpHdr/MsgId | instructionId | Direct |
| CdtTrfTxInf/PmtId/InstrId | instructionId | Direct |
| CdtTrfTxInf/PmtId/EndToEndId | endToEndId | Direct |
| CdtTrfTxInf/PmtId/UETR | uetr | Direct (SWIFT gpi) |
| CdtTrfTxInf/IntrBkSttlmAmt | interbankSettlementAmount | Direct (includes currency attribute) |
| CdtTrfTxInf/IntrBkSttlmDt | settlementDate | Direct |
| CdtTrfTxInf/ChrgBr | chargeBearer | Direct (DEBT, CRED, SHAR, SLEV) |
| CdtTrfTxInf/Dbtr | debtor | Map to Party entity |
| CdtTrfTxInf/DbtrAcct | debtorAccount | Map to Account entity |
| CdtTrfTxInf/DbtrAgt | debtorAgent | Map to FinancialInstitution entity |
| CdtTrfTxInf/Cdtr | creditor | Map to Party entity |
| CdtTrfTxInf/CdtrAcct | creditorAccount | Map to Account entity |
| CdtTrfTxInf/CdtrAgt | creditorAgent | Map to FinancialInstitution entity |
| CdtTrfTxInf/IntrmyAgt1, IntrmyAgt2, IntrmyAgt3 | intermediaryAgents | Array of FinancialInstitution |
| CdtTrfTxInf/Purp | purpose | Direct (ISO external purpose codes) |
| CdtTrfTxInf/RmtInf | remittanceInformation | Map to RemittanceInformation entity (unstructured and structured) |
| CdtTrfTxInf/RgltryRptg | regulatoryInformation.regulatoryReportingCodes | Direct |

**Advantage**: ISO 20022 native; no data loss, full structured data

#### Real-Time Payments (RTP/FedNow) → CDM Mapping

**Source Format**: ISO 20022 pain.001 (customer to bank) and pacs.008 (interbank)

**Mapping**: Similar to SWIFT MX (ISO 20022 native)

**Additional Considerations**:
- **Irrevocability**: RTP and FedNow payments are irrevocable once sent; status tracking critical
- **Request for Payment**: pain.013 and pain.014 messages for RfP; map to extensions or separate entity
- **Real-time Confirmation**: camt.056 (cancellation request if needed) and pacs.002 (status report)

#### SEPA (SCT, SCT Inst, SDD) → CDM Mapping

**Source Format**: ISO 20022 pain.001 (credit transfer), pain.008 (direct debit), pacs.008 (interbank)

**Mapping**: Direct (ISO 20022 based)

**Specific SEPA Requirements**:
- **IBAN Mandatory**: creditorAccount.iban and debtorAccount.iban required
- **BIC Optional**: Transitioning to IBAN-only (BIC can be derived from IBAN)
- **SEPA Instant**: Max €100,000, <10 seconds execution time
- **Direct Debit Mandate**: For SDD, mandate reference and creditor identifier required

**SEPA-Specific CDM Extensions**:
```
extensions: {
  sepaScheme: "SCT" | "SCT_INST" | "SDD_CORE" | "SDD_B2B"
  sepaCreditorIdentifier: "string" (for direct debits)
  sepaMandateReference: "string" (for direct debits)
  sepaMandateSignatureDate: "date"
  sepaSequenceType: "FRST" | "RCUR" | "FNAL" | "OOFF" (for direct debits)
}
```

#### BACS → CDM Mapping

**Source Format**: BACS Standard 18 (fixed-length records)

**Mapping**:

| BACS Field | CDM Element | Transformation |
|------------|-------------|----------------|
| Destination Sort Code | creditorAgent.clearingSystemMemberships[BACS].memberId | 6-digit sort code |
| Destination Account Number | creditorAccount.accountNumber | 8 digits |
| Transaction Code | paymentType | Map to "BACS_CREDIT" or "BACS_DEBIT" |
| Amount | instructedAmount.amount | Convert pence to decimal |
| Reference | remittanceInformation.unstructured | 18 characters |
| Processing Day | requestedExecutionDate | 2 digits (day offset) |

**BACS to ISO 20022 Conversion**: Official translation guide available from Bacs; use for pain.001 → BACS and BACS → pacs.008 mapping

#### Faster Payments (UK) → CDM Mapping

**Source Format**: Currently ISO 8583; future ISO 20022 (when NPA implemented)

**Current Mapping**:

| FPS Field | CDM Element | Transformation |
|-----------|-------------|----------------|
| Sort Code | creditorAgent.clearingSystemMemberships[FPS].memberId | 6 digits |
| Account Number | creditorAccount.accountNumber | 8 digits |
| Amount | instructedAmount.amount | Direct (up to £1,000,000) |
| Reference | remittanceInformation.unstructured | Up to 18 characters |

**Future**: When NPA delivers ISO 20022, mapping will align with pain.001/pacs.008 (similar to SEPA)

---

### Regulatory Data Element Cross-Reference

Comprehensive cross-reference of CDM data elements to regulatory reports:

#### US CTR (Currency Transaction Report) Mapping

| CTR Field | CDM Element | Notes |
|-----------|-------------|-------|
| Part I - Person(s) Involved in Transaction ||
| Name | debtor.name or creditor.name | Depending on cash in/out |
| TIN (SSN/EIN) | debtor.identifications[TaxID] | Required |
| Address | debtor.postalAddress | Full structured address |
| Date of Birth | debtor.identifications[DateOfBirth] | If individual |
| Occupation/Business | debtor.organizationType | If organization |
| Part II - Amount and Type of Transaction ||
| Date of Transaction | paymentDate | Direct |
| Total Cash In | instructedAmount (if deposit) | Aggregate daily total |
| Total Cash Out | instructedAmount (if withdrawal) | Aggregate daily total |
| Type of Transaction | paymentType | Deposit, withdrawal, exchange, etc. |
| Part III - Financial Institution ||
| Name and Address | debtorAgent or creditorAgent | Bank of America entity |
| EIN | N/A | Bank's EIN (constant) |
| Account Number | debtorAccount or creditorAccount | |

#### US SAR (Suspicious Activity Report) Mapping

| SAR Part | CDM Element | Notes |
|----------|-------------|-------|
| Part I - Subject Information ||
| Name | debtor or creditor (flagged party) | |
| TIN | identifications[TaxID] | If known |
| Address | postalAddress | |
| Part II - Suspicious Activity ||
| Date of Suspicious Activity | paymentDate | Can be date range |
| Total Dollar Amount | instructedAmount | Aggregate if multiple txns |
| Category of Suspicious Activity | regulatoryInformation.highRiskIndicators | Select from SAR categories |
| Part III - Narrative ||
| Explanation of Suspicious Activity | ComplianceCase.investigationNotes | Narrative compiled from case notes |
| Part IV - Financial Institution ||
| Name, Address, EIN | creditorAgent or debtorAgent | Bank of America |
| Account Number | account.accountNumber | Affected account(s) |

#### EU PSD2 Transaction Reporting

| PSD2 Requirement | CDM Element | Notes |
|------------------|-------------|-------|
| Number of Transactions | COUNT(*) from payments_silver WHERE region = 'EMEA' | Aggregated |
| Value of Transactions | SUM(instructedAmount) | By currency and payment type |
| Fraud Incidents | COUNT(*) WHERE fraudScore > threshold OR ComplianceCase.caseType = 'fraud' | |
| Fraud Losses | SUM(instructedAmount) WHERE payment marked as fraud | |
| Average Transaction Value | AVG(instructedAmount) | By payment type |

#### DORA Incident Reporting

| DORA Field | CDM Element | Notes |
|------------|-------------|-------|
| Incident Classification | OperationalIncident.incidentType | Major, critical, etc. |
| Timestamp | OperationalIncident.incidentTimestamp | |
| Affected Services | Payment types or systems affected | E.g., "SEPA Instant Payments" |
| Number of Transactions Affected | COUNT(*) WHERE payment affected by incident | |
| Impact Duration | Incident start to resolution timestamp | |
| Root Cause | OperationalIncident.rootCause | After investigation |

---

### Reconciliation of CDM to Standards and Regulations

**Reconciliation Goal**: Achieve **100% coverage** of all data elements from:
1. ISO 20022 message catalog (payment-related messages)
2. All regulatory reports across jurisdictions
3. All payment product formats (NACHA, Fedwire, SWIFT MT, etc.)

**Reconciliation Approach**:
1. Extract all data elements from each standard/format
2. Map each element to CDM
3. Identify gaps (elements not covered by CDM)
4. Enhance CDM to cover gaps
5. Re-reconcile to ensure 100% coverage

**Reconciliation Matrix** (Illustrative Sample):

| Data Element | ISO 20022 | NACHA | SWIFT MT103 | US CTR | EU PSD2 | CDM Element | Coverage |
|--------------|-----------|-------|-------------|--------|---------|-------------|----------|
| Debtor Name | Dbtr/Nm | Individual Name | :50K: | Part I Name | Originator Name | debtor.name | ✅ 100% |
| Debtor Account | DbtrAcct/Id/IBAN | DFI Account Number | :50K: (embedded) | Part III Acct | Debtor Account | debtorAccount.accountNumber | ✅ 100% |
| Debtor TIN | Dbtr/Id (Tax ID) | Company ID (EIN) | Not standard | Part I TIN | Tax ID | debtor.identifications[TaxID] | ✅ 100% |
| Amount | IntrBkSttlmAmt | Amount (field 30-39) | :32A: | Part II Amount | Transaction Value | instructedAmount | ✅ 100% |
| Remittance Info | RmtInf/Ustrd | Addenda Payment Related Info | :70: | N/A | N/A | remittanceInformation.unstructured | ✅ 100% |
| Purpose Code | Purp/Cd | (mapped from SEC code) | Not standard (in :70:) | N/A | Purpose | purpose | ✅ 100% |
| Cross-Border Flag | N/A (derived) | N/A | N/A | N/A | Cross-Border Indicator | crossBorderFlag | ✅ 100% |
| Fraud Score | N/A | N/A | N/A | N/A | N/A | fraudScore | ✅ 100% |

**Gaps Identified** (Examples):
- **Gap**: ISO 20022 has "Structured Creditor Reference (SCOR)" for invoices; not present in NACHA or MT formats
  - **Resolution**: Include in CDM remittanceInformation.structured; map from ISO 20022, leave null for non-ISO sources
- **Gap**: NACHA has "Same Day ACH Indicator"; not in ISO 20022 standard fields
  - **Resolution**: Include in CDM extensions.achSameDayFlag; specific to ACH product
- **Gap**: DORA requires "Incident Classification" taxonomy; not in payment message standards
  - **Resolution**: Add OperationalIncident entity to CDM (not part of core payment but related)

**Reconciliation Documentation**: Full reconciliation matrix will be maintained as a separate spreadsheet/database with 1000+ data elements across all standards and regulations, mapped to CDM (see Deliverable 5.2 for complete mappings).

---

*(Continued in next section...)*

## DELIVERABLE 2.3: PHYSICAL COMMON DOMAIN MODEL

### Physical Schema Implementation

The physical CDM is implemented using **JSON Schema Draft 2020-12** for schema definitions and **Delta Lake** for storage. JSON Schema provides machine-readable, validate definitions that can be used for:
- Data validation at ingestion
- Code generation (Python, Java, Scala classes)
- API contract definitions
- Documentation generation

### JSON Schema Module Organization

```
/schemas/cdm/
├── core/
│   ├── payment-instruction.schema.json
│   ├── party.schema.json
│   ├── account.schema.json
│   ├── financial-institution.schema.json
│   ├── amount.schema.json
│   ├── date-time.schema.json
│   └── common-types.schema.json
├── status/
│   ├── payment-status.schema.json
│   ├── status-event.schema.json
│   └── status-reason.schema.json
├── settlement/
│   ├── settlement.schema.json
│   ├── clearing-system.schema.json
│   └── charge.schema.json
├── regulatory/
│   ├── regulatory-reporting.schema.json
│   ├── compliance-data.schema.json
│   ├── screening-result.schema.json
│   └── compliance-case.schema.json
├── remittance/
│   ├── remittance-information.schema.json
│   ├── structured-remittance.schema.json
│   └── document-reference.schema.json
├── reference/
│   ├── currency.schema.json
│   ├── country.schema.json
│   ├── purpose-codes.schema.json
│   ├── clearing-system.schema.json
│   └── scheme-codes.schema.json
├── products/
│   ├── ach-payment.schema.json
│   ├── wire-payment.schema.json
│   ├── swift-payment.schema.json
│   ├── realtime-payment.schema.json
│   ├── sepa-payment.schema.json
│   ├── bacs-payment.schema.json
│   └── faster-payment.schema.json
└── analytics/
    ├── payment-event.schema.json
    ├── payment-metrics.schema.json
    └── payment-feature.schema.json
```

### Sample JSON Schema (Core Payment Instruction)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://bofa.com/schemas/cdm/core/payment-instruction.schema.json",
  "title": "Payment Instruction",
  "description": "Core payment instruction entity representing a single payment from initiation to settlement",
  "type": "object",
  "required": [
    "paymentId",
    "paymentType",
    "schemeCode",
    "instructedAmount",
    "paymentDate",
    "currentStatus"
  ],
  "properties": {
    "paymentId": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for the payment (UUID v4)"
    },
    "endToEndId": {
      "type": "string",
      "maxLength": 35,
      "description": "End-to-end identification per ISO 20022"
    },
    "uetr": {
      "type": "string",
      "format": "uuid",
      "description": "Unique End-to-end Transaction Reference (SWIFT gpi)"
    },
    "instructionId": {
      "type": "string",
      "maxLength": 35,
      "description": "Instruction identification"
    },
    "transactionId": {
      "type": "string",
      "maxLength": 35,
      "description": "Transaction identification"
    },
    "paymentType": {
      "type": "string",
      "enum": [
        "ACH_CREDIT",
        "ACH_DEBIT",
        "WIRE_DOMESTIC",
        "WIRE_INTERNATIONAL",
        "SWIFT_MT",
        "SWIFT_MX",
        "RTP",
        "FEDNOW",
        "ZELLE",
        "SEPA_SCT",
        "SEPA_INST",
        "SEPA_SDD",
        "BACS_CREDIT",
        "BACS_DEBIT",
        "FASTER_PAYMENT",
        "PIX",
        "CIPS",
        "CHECK",
        "CARD",
        "OTHER"
      ],
      "description": "Payment type classification"
    },
    "productCode": {
      "type": "string",
      "description": "BofA internal product code"
    },
    "schemeCode": {
      "type": "string",
      "enum": [
        "NACHA",
        "FEDWIRE",
        "CHIPS",
        "SWIFT",
        "RTP",
        "FEDNOW",
        "SEPA",
        "TARGET2",
        "CHAPS",
        "BACS",
        "FPS",
        "PIX",
        "CIPS",
        "OTHER"
      ],
      "description": "Payment scheme code"
    },
    "serviceLevel": {
      "type": "string",
      "description": "Service level code (e.g., URGP for urgent, SEPA for SEPA)"
    },
    "instructedAmount": {
      "$ref": "#/$defs/Money",
      "description": "Instructed amount and currency"
    },
    "interbankSettlementAmount": {
      "$ref": "#/$defs/Money",
      "description": "Interbank settlement amount (if different from instructed)"
    },
    "exchangeRate": {
      "type": "number",
      "minimum": 0,
      "description": "Exchange rate if currency conversion involved"
    },
    "chargeBearer": {
      "type": "string",
      "enum": ["DEBT", "CRED", "SHAR", "SLEV"],
      "description": "Charge bearer per ISO 20022"
    },
    "creationDateTime": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp when payment instruction was created (ISO 8601)"
    },
    "requestedExecutionDate": {
      "type": "string",
      "format": "date",
      "description": "Requested execution date (ISO 8601 date)"
    },
    "valueDate": {
      "type": "string",
      "format": "date",
      "description": "Value date"
    },
    "settlementDate": {
      "type": "string",
      "format": "date",
      "description": "Actual settlement date"
    },
    "acceptanceDateTime": {
      "type": "string",
      "format": "date-time",
      "description": "Acceptance date and time"
    },
    "debtor": {
      "$ref": "party.schema.json",
      "description": "Debtor party information"
    },
    "debtorAccount": {
      "$ref": "account.schema.json",
      "description": "Debtor account information"
    },
    "debtorAgent": {
      "$ref": "financial-institution.schema.json",
      "description": "Debtor agent (financial institution)"
    },
    "creditor": {
      "$ref": "party.schema.json",
      "description": "Creditor party information"
    },
    "creditorAccount": {
      "$ref": "account.schema.json",
      "description": "Creditor account information"
    },
    "creditorAgent": {
      "$ref": "financial-institution.schema.json",
      "description": "Creditor agent (financial institution)"
    },
    "intermediaryAgents": {
      "type": "array",
      "items": {
        "$ref": "financial-institution.schema.json"
      },
      "description": "Intermediary agents (correspondent banks, clearing agents)"
    },
    "purpose": {
      "type": "string",
      "maxLength": 4,
      "description": "Purpose code per ISO 20022 external code list"
    },
    "categoryPurpose": {
      "type": "string",
      "maxLength": 4,
      "description": "Category purpose code"
    },
    "remittanceInformation": {
      "$ref": "remittance/remittance-information.schema.json",
      "description": "Remittance information (structured and unstructured)"
    },
    "currentStatus": {
      "type": "string",
      "enum": [
        "initiated",
        "pending",
        "validated",
        "screened",
        "cleared",
        "settled",
        "completed",
        "failed",
        "returned",
        "cancelled"
      ],
      "description": "Current payment status"
    },
    "statusReason": {
      "type": "string",
      "description": "Status reason code per ISO 20022"
    },
    "statusHistory": {
      "type": "array",
      "items": {
        "$ref": "status/status-event.schema.json"
      },
      "description": "Complete status history"
    },
    "charges": {
      "type": "array",
      "items": {
        "$ref": "settlement/charge.schema.json"
      },
      "description": "Charges and fees associated with payment"
    },
    "regulatoryReportingCodes": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Regulatory reporting codes"
    },
    "crossBorderFlag": {
      "type": "boolean",
      "description": "Cross-border payment indicator"
    },
    "sanctionsScreeningResult": {
      "$ref": "regulatory/screening-result.schema.json",
      "description": "Sanctions screening result"
    },
    "fraudScore": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "description": "Fraud risk score (0-100)"
    },
    "amlRiskRating": {
      "type": "string",
      "enum": ["low", "medium", "high", "very_high"],
      "description": "AML risk rating"
    },
    "sourceSystem": {
      "type": "string",
      "description": "Source system identifier"
    },
    "sourceRecordId": {
      "type": "string",
      "description": "Source system record ID"
    },
    "ingestionTimestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Bronze layer ingestion timestamp"
    },
    "dataQualityScore": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "description": "Overall data quality score (0-100)"
    },
    "dataQualityIssues": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of data quality issues identified"
    },
    "extensions": {
      "type": "object",
      "description": "Product-specific or proprietary extensions",
      "additionalProperties": true
    }
  },
  "$defs": {
    "Money": {
      "type": "object",
      "required": ["amount", "currency"],
      "properties": {
        "amount": {
          "type": "number",
          "description": "Amount as decimal"
        },
        "currency": {
          "type": "string",
          "pattern": "^[A-Z]{3}$",
          "description": "ISO 4217 currency code (3 letters)"
        }
      }
    }
  }
}
```

### Delta Lake Table Specifications

**(See Workstream 1, Deliverable 1.3, Row 4 for detailed Delta Lake table DDL)**

**Key Table Specifications**:

1. **payments_silver** (core CDM table):
   - Partitioned by: payment_year, payment_month, region, product_type
   - Z-Ordered by: payment_id, debtor_account_number, creditor_account_number, payment_date
   - Change Data Feed: Enabled (for downstream consumers)
   - Schema Evolution: Enabled (for CDM versioning)
   - Retention: 7 years (configurable by jurisdiction)

2. **payment_events_bronze** (event sourcing):
   - Partitioned by: event_date
   - Append-only table for all payment lifecycle events
   - Retention: 7 years

3. **payments_gold_regulatory_ctr** (regulatory reporting example):
   - Aggregated table for CTR reporting
   - Partitioned by: report_date
   - Optimized for report generation queries

### Partitioning Strategies

**Time-Based Partitioning**:
- **Year and Month**: Efficient for time-range queries and data retention management
- Enables partition pruning for queries like "payments in Q1 2025"
- Simplifies archival (older partitions moved to cheaper storage)

**Geographic Partitioning**:
- **Region**: US, EMEA, APAC (aligns with data residency requirements)
- Enables region-specific queries without scanning other regions
- Supports multi-region deployments (US data in S3 us-east-1, EMEA data in S3 eu-west-1, etc.)

**Product Partitioning**:
- **Product Type**: ACH, Wire, SWIFT, SEPA, etc.
- Supports domain-oriented data products (ACH team owns ACH partition)
- Optimizes queries for product-specific analytics

**Example Partition Structure**:
```
s3://bofa-payments-silver/payments/
  payment_year=2025/
    payment_month=01/
      region=US/
        product_type=ACH/
          part-00000.parquet
          part-00001.parquet
        product_type=WIRE/
          part-00000.parquet
      region=EMEA/
        product_type=SEPA/
          part-00000.parquet
```

### Indexing Strategies (Z-Ordering)

Z-Ordering co-locates related data in the same files for faster query performance:

**Primary Z-Order Columns**:
1. **payment_id**: Primary key lookups
2. **debtor_account_number**: Debtor account queries (e.g., "all payments from account X")
3. **creditor_account_number**: Creditor account queries
4. **payment_date**: Time-range queries combined with account queries

**Command**:
```sql
OPTIMIZE payments_silver ZORDER BY (payment_id, debtor_account_number, creditor_account_number, payment_date);
```

**Performance Impact**: 10-100x faster queries for common access patterns (based on Databricks benchmarks)

### CDC/Streaming Event Schemas

**(See Workstream 1, Deliverable 1.3, Row 4 for streaming event schemas)**

**Key Characteristics**:
- **Event Sourcing Pattern**: All state changes captured as events
- **Kafka Integration**: Payment events published to Kafka topics
- **Exactly-Once Semantics**: Idempotent processing with Kafka offsets + Delta Lake ACID
- **Schema Registry**: Avro or Protobuf schemas registered for compatibility checks

---

## DELIVERABLE 2.4: CDM GOVERNANCE FRAMEWORK

### Model Governance

#### Change Control Process

**CDM Versioning**:
- **Semantic Versioning**: MAJOR.MINOR.PATCH (e.g., 1.0.0, 1.1.0, 2.0.0)
  - **MAJOR**: Breaking changes (field removal, incompatible type changes)
  - **MINOR**: Backward-compatible additions (new optional fields, new enum values)
  - **PATCH**: Bug fixes, documentation updates

**Change Request Process**:

1. **Request Submission**:
   - Submitter: Domain team, compliance, product owner
   - Form: Change Request Form (Jira/Confluence template)
   - Content: Rationale, proposed change, impact analysis

2. **Initial Review**:
   - Reviewer: CDM Data Architect
   - Timeline: 3 business days
   - Decision: Approve for full review, reject, or request more info

3. **Impact Assessment**:
   - Assess impact on:
     - Downstream consumers (pipelines, reports, dashboards)
     - Data quality rules
     - Regulatory mappings
     - Integration points
   - Categorize: Low, Medium, High impact

4. **CDM Governance Board Review**:
   - **Members**: CDM Architect, Domain Data Product Owners (ACH, Wires, SWIFT, etc.), Compliance Rep, Platform Lead
   - **Frequency**: Bi-weekly
   - **Quorum**: 50% + 1
   - **Decision**: Approve, Reject, or Defer
   - **Approval Threshold**: Majority vote for MINOR changes, unanimous for MAJOR changes

5. **Implementation**:
   - CDM Architect updates JSON Schema
   - Schema versioned in Git repository
   - Automated validation in CI/CD pipeline
   - Backward compatibility tests run

6. **Communication and Rollout**:
   - **Announcement**: Email to all stakeholders + Slack/Teams channel
   - **Documentation Update**: Confluence CDM documentation updated
   - **Training** (if needed): Sessions for impacted teams
   - **Migration Period**: 90 days for MAJOR changes, 30 days for MINOR

**Change Control Tools**:
- **Version Control**: Git (GitHub or GitLab) for JSON Schema files
- **Change Tracking**: Jira for change requests
- **Documentation**: Confluence for CDM documentation
- **Communication**: Email + Slack/Teams

#### Backward Compatibility Rules

**Backward-Compatible Changes** (Allowed in MINOR versions):
- Adding optional fields
- Adding new enum values (if default handling exists)
- Expanding field length (e.g., VARCHAR(100) → VARCHAR(200))
- Adding new tables/entities

**Breaking Changes** (Require MAJOR version):
- Removing fields
- Renaming fields
- Changing field data types (e.g., STRING → INTEGER)
- Making optional fields required
- Removing enum values
- Changing field semantics (same name, different meaning)

**Deprecation Policy**:
- Deprecated fields marked in schema with "deprecated": true
- Deprecation notice period: 6 months minimum
- Deprecated fields removed only in MAJOR version increments

**Migration Support**:
- For MAJOR versions, provide migration scripts
- Dual-schema support during migration period (old and new versions coexist)
- Backward compatibility layer (optional) for critical consumers

#### Extension Guidelines

**When to Use Extensions**:
- Product-specific fields not applicable to other products
- Experimental features (not yet standardized)
- Customer-specific customizations
- Temporary workarounds (with plan to promote to core)

**Extension Naming Convention**:
- Prefix with product/domain: `ach_`, `wire_`, `sepa_`, `cashpro_`
- Descriptive name: `ach_same_day_flag`, `cashpro_workflow_state`
- Avoid generic names: ❌ `flag1`, `temp_field`

**Extension Approval**:
- **MINOR extensions** (product-specific): Domain Data Product Owner approval
- **MAJOR extensions** (cross-product or impacting core): CDM Governance Board approval

**Extension Promotion**:
- If extension used by 3+ products, consider promoting to core CDM
- Promotion requires CDM Governance Board approval
- Extension deprecated after promotion (with migration period)

**Extension Documentation**:
- All extensions documented in CDM documentation
- Include: Purpose, data type, valid values, usage examples
- Ownership: Domain team responsible for extension

#### Collibra Integration for CDM Documentation

**Metadata Synchronization**:
- **Unity Catalog → Collibra**: Automated sync of table/column metadata
- **Sync Frequency**: Daily for catalog changes, real-time for critical updates
- **Metadata Synced**:
  - Table names, descriptions, owners
  - Column names, data types, descriptions
  - Data lineage (source → CDM → consumption)
  - Data quality scores
  - Usage statistics (query frequency, users)

**Business Glossary**:
- CDM entities and attributes linked to business terms in Collibra
- Example: "Debtor" (CDM) → "Customer Making Payment" (business term)
- Stewards: Assigned for each business term (Compliance, Product, Operations)

**Data Quality Integration**:
- Quality rules defined in Collibra, enforced in Delta Live Tables
- Quality scores published to Collibra for visibility
- Quality issues tracked and remediated in Collibra workflows

**Lineage Tracking**:
- End-to-end lineage: Source System → Bronze → Silver (CDM) → Gold → Report/Dashboard
- Column-level lineage: Source field → CDM element → Report field
- Automated lineage capture via Unity Catalog + Collibra integration

---

### Data Quality Rules

#### Field-Level Validation Rules

**Rule Categories**:
1. **Completeness**: Required fields must be populated
2. **Validity**: Values must conform to format, range, or enumeration
3. **Accuracy**: Values must be correct (verified against reference data)
4. **Consistency**: Values must be consistent with related fields
5. **Timeliness**: Data must be current (not stale)

**Example Field-Level Rules**:

| Field | Rule Type | Rule | Error Handling |
|-------|-----------|------|----------------|
| paymentId | Completeness | NOT NULL | Reject record |
| instructedAmount.amount | Validity | > 0 AND < 999999999.99 | Reject record |
| instructedAmount.currency | Validity | RLIKE '^[A-Z]{3}$' | Reject record |
| debtor.name | Completeness | NOT NULL | Flag for review |
| debtorAccount.iban | Validity | IBAN checksum validation | Reject if IBAN provided |
| debtorAgent.bic | Validity | BIC format validation (8 or 11 chars, pattern match) | Reject if BIC provided |
| paymentDate | Validity | BETWEEN '1970-01-01' AND CURRENT_DATE + 30 days | Reject |
| currentStatus | Validity | IN ('initiated', 'pending', ..., 'completed') | Reject |
| endToEndId | Uniqueness | Unique within payment_type + payment_date | Flag duplicate |

**Implementation in Delta Live Tables**:

```python
@dlt.table
@dlt.expect_or_drop("valid_payment_id", "paymentId IS NOT NULL")
@dlt.expect_or_drop("positive_amount", "instructedAmount.amount > 0")
@dlt.expect_or_drop("valid_currency", "LENGTH(instructedAmount.currency) = 3")
@dlt.expect_or_fail("valid_status", "currentStatus IN ('initiated', 'pending', 'validated', 'cleared', 'settled', 'completed', 'failed', 'returned')")
@dlt.expect("complete_debtor_name", "debtor.name IS NOT NULL AND LENGTH(debtor.name) > 0")  # Warning, not drop
def payments_silver():
    return # transformation logic
```

#### Cross-Field Validation Rules

**Example Rules**:

| Rule Name | Rule Logic | Error Handling |
|-----------|------------|----------------|
| Settlement Amount Consistency | IF interbankSettlementAmount IS NOT NULL THEN interbankSettlementAmount = instructedAmount OR exchangeRate IS NOT NULL | Flag inconsistency |
| Cross-Border Flag Consistency | IF debtor country != creditor country THEN crossBorderFlag = TRUE | Flag |
| Charge Bearer Consistency | IF chargeBearer = 'DEBT' THEN charges[*].chargeBearer = 'DEBT' | Flag |
| Intermediary Agents for Cross-Border | IF crossBorderFlag = TRUE AND debtorAgent.country != creditorAgent.country THEN intermediaryAgents.length >= 0 (may be zero for direct) | Warning |
| Completion Status Requires Settlement | IF currentStatus = 'completed' THEN settlementDate IS NOT NULL | Reject status change |

#### Business Rule Validation

**Example Business Rules**:

1. **Same-Day ACH Amount Limit**:
   - Rule: IF paymentType = 'ACH' AND extensions.achSameDayFlag = TRUE THEN instructedAmount <= 1000000.00
   - Enforcement: Reject at initiation

2. **SEPA Instant Amount Limit**:
   - Rule: IF paymentType = 'SEPA_INST' THEN instructedAmount <= 100000.00 AND instructedCurrency = 'EUR'
   - Enforcement: Reject

3. **Sanctions Screening Required for All Cross-Border**:
   - Rule: IF crossBorderFlag = TRUE THEN sanctionsScreeningResult IS NOT NULL AND sanctionsScreeningResult.screeningStatus != 'pending'
   - Enforcement: Block settlement until screening complete

4. **High-Value Payment Approval**:
   - Rule: IF instructedAmount > 10000000.00 THEN approvals.contains('senior_operations_manager')
   - Enforcement: Manual approval workflow

#### Referential Integrity Rules

**Entity Relationships**:

1. **Currency Codes Must Exist in Reference Data**:
   - Rule: instructedAmount.currency IN (SELECT currencyCode FROM currency_reference WHERE effectiveTo IS NULL)
   - Enforcement: Reject if currency not found

2. **Country Codes Must Exist**:
   - Rule: debtor.postalAddress.country IN (SELECT countryCode FROM country_reference)
   - Enforcement: Reject

3. **BIC Must Be Valid and Active**:
   - Rule: debtorAgent.bic IN (SELECT bic FROM financial_institution_reference WHERE status = 'active')
   - Enforcement: Warning (may be valid BIC not in our reference data)

4. **Purpose Codes Must Be Valid**:
   - Rule: purpose IN (SELECT code FROM purpose_code_reference WHERE applicableProducts CONTAINS paymentType)
   - Enforcement: Warning

#### Quality Scoring Methodology

**Data Quality Score Calculation** (0-100):

Components:
1. **Completeness Score** (30% weight):
   - Critical fields populated: 100%
   - Important fields populated: Percentage of important fields populated
   - Optional fields populated: Bonus (up to 10%)

2. **Validity Score** (30% weight):
   - All validation rules passed: 100%
   - Each failed validation: -5 points

3. **Consistency Score** (20% weight):
   - Cross-field rules passed: 100%
   - Each inconsistency: -10 points

4. **Accuracy Score** (10% weight):
   - Reference data matches: 100%
   - Each mismatch or suspected inaccuracy: -10 points

5. **Timeliness Score** (10% weight):
   - Data current (ingested within SLA): 100%
   - Data stale: Linear degradation based on staleness

**Example Calculation**:

```
Payment with:
- All critical fields populated (paymentId, amount, debtor, creditor, date)
- Missing optional field (purpose code)
- Failed validity rule (BIC format invalid)
- No cross-field inconsistencies
- Reference data matches (currency, country valid)
- Ingested within SLA

Completeness: 100% (critical) + 80% (important 4/5) + 0% (optional) = 90% * 0.3 = 27
Validity: 100% - 5% (1 failed rule) = 95% * 0.3 = 28.5
Consistency: 100% * 0.2 = 20
Accuracy: 100% * 0.1 = 10
Timeliness: 100% * 0.1 = 10

Total Quality Score: 27 + 28.5 + 20 + 10 + 10 = 95.5 (out of 100)
```

**Quality Score Thresholds**:
- **>=95**: Excellent
- **90-94**: Good
- **80-89**: Fair (requires attention)
- **<80**: Poor (requires immediate remediation)

**Quality Dashboards**:
- Real-time quality score monitoring in Databricks SQL dashboards
- Quality trends over time (improving/degrading)
- Quality by product, region, source system
- Alert if quality score falls below threshold

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-18 | GPS Data Strategy Team | Initial Workstream 2 deliverables |

---

*End of Workstream 2: Payments Common Domain Model*
